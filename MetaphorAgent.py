from creamas import CreativeAgent, Artifact
from MetaphorMemory import MetaphorMemory
from Model_Classes import Metaphor
import random


class MetaphorAgent(CreativeAgent):
    def __init__(self, env, nouns, mem_cap=100):
        super().__init__(env)
        self.nouns = nouns
        self.memory = MetaphorMemory(mem_cap)

    SHARED_SCORE_EVAL_WEIGHT = 1
    NOUN_SCORE_EVAL_WEIGHT = 0
    ADJ_SCORE_EVAL_WEIGHT = 0

    INVENT_TRIES = 10

    async def act(self):
        if len(self.env.artifacts) > 0:
            # memorize the most recent artifact.  Agents will distinguish themselves once they start forgetting
            for winner in self.env.artifacts[(-self.env.num_metaphors_accepted_per_round - 1):-1]:
                self.memory.memorize(winner.obj)

        metaphor = self.invent()
        if metaphor is not None:
            self.env.add_candidate(metaphor)
            self.memory.memorize(metaphor.obj)

    def invent(self):
        best_score = -1
        best_metaphor = None
        for i in range(0, MetaphorAgent.INVENT_TRIES):
            candidate = self.generate()
            if candidate is None:
                continue
            score = self.eval_metaphor(candidate.obj)
            if score > best_score:
                best_metaphor = candidate
                best_score = score
        best_metaphor.add_eval(self, best_score)
        return best_metaphor

    def generate(self):
        random.shuffle(self.nouns)
        for noun_1 in self.nouns:
            for noun_2 in self.nouns:
                if noun_1.word != noun_2.word:
                    for adj in noun_1.get_adjectives():
                        if adj.word in [adj2.word for adj2 in noun_2.get_adjectives()]:
                            if random.randint(0, 1) == 1:
                                return Artifact(self, Metaphor(noun_1, noun_2, adj), domain=Metaphor)
        return None

    def evaluate(self, artifact):
        if isinstance(artifact.obj, Metaphor):
            return self.eval_metaphor(artifact.obj), None
        return -1, None

    def count_noun_metaphors(self, noun, shared_noun):
        shared_count = 0
        count = 0
        if noun in self.memory.metaphor_lookup.keys():
            for other_noun, metaphor_list in self.memory.metaphor_lookup[noun].items():
                if other_noun == shared_noun:
                    shared_count += len(metaphor_list)
                count += len(metaphor_list)
        return count, shared_count

    def eval_metaphor(self, metaphor):
        if self.memory.contains(metaphor):
            return 0

        # Hard to evaluate the 'truth' of a metaphor without a model of the world that is well beyond the capability
        # of this algorithm.  Instead, focus on surprise/novelty.

        noun1_count, shared_count = self.count_noun_metaphors(metaphor.noun_1, metaphor.noun_2)
        noun2_count, _ = self.count_noun_metaphors(metaphor.noun_2, metaphor.noun_1)
        adj_count = self.memory.adjective_counts.get(metaphor.adjective) or 0
        total_count = float(self.memory.count)

        if total_count == 0:
            return 1

        noun1_score = 1 - (noun1_count / total_count)
        noun2_score = 1 - (noun2_count / total_count)
        shared_score = 1 - (shared_count / total_count)
        adj_score = 1 - (adj_count / total_count)

        nominator = ((MetaphorAgent.SHARED_SCORE_EVAL_WEIGHT * shared_score)
                     + (MetaphorAgent.NOUN_SCORE_EVAL_WEIGHT * noun1_score)
                     + (MetaphorAgent.NOUN_SCORE_EVAL_WEIGHT * noun2_score)
                     + (MetaphorAgent.ADJ_SCORE_EVAL_WEIGHT * adj_score))
        denominator = (MetaphorAgent.SHARED_SCORE_EVAL_WEIGHT
                       + (2 * MetaphorAgent.NOUN_SCORE_EVAL_WEIGHT)
                       + MetaphorAgent.ADJ_SCORE_EVAL_WEIGHT)
        return nominator / denominator