from creamas import CreativeAgent, Artifact
from MetaphorMemory import MetaphorMemory
from Model_Classes import Metaphor
import random


class MetaphorAgent(CreativeAgent):
    """
    This class is a type of CreativeAgent which generates and evaluates metaphors.

    Attributes:
        SHARED_SCORE_EVAL_WEIGHT    The weight given to the score for metaphors with both nouns in common used when evaluating a new metaphor

        NOUN_SCORE_EVAL_WEIGHT      The weight given to the score for metaphors with one noun in common used when evaluating a new metaphor

        ADJ_SCORE_EVAL_WEIGHT       The weight given to the score for metaphors with the adjective in common used when evaluating a new metaphor

        INVENT_TRIES                The number of metaphors to generate and evaluate before submitting the best as a candidate
    """
    def __init__(self, env, nouns, mem_cap=100):
        """
        :param env (Environment): the creamas environment the agent will operate in
        :param nouns (list of :class:'Noun'): a list of nouns (describing adjectives included) to draw metaphors from
        :param mem_cap (int): the number of metaphors the agent will keep in its memory before it starts forgetting them at random
        """
        super().__init__(env)
        self.nouns = nouns
        self.memory = MetaphorMemory(mem_cap)

    SHARED_SCORE_EVAL_WEIGHT = 1
    NOUN_SCORE_EVAL_WEIGHT = 0
    ADJ_SCORE_EVAL_WEIGHT = 0

    INVENT_TRIES = 10

    async def act(self):
        """
        Each simulation round, the MetaphorAgent memorizes the metaphor winners from last round, then invents a
        new :class:'Metaphor' and enters it as a candidate.
        """
        if len(self.env.artifacts) > 0:
            # memorize the most recent artifact.  Agents will distinguish themselves once they start forgetting
            for winner in self.env.artifacts[(-self.env.num_metaphors_accepted_per_round - 1):-1]:
                self.memory.memorize(winner.obj)

        metaphor = self.invent()
        if metaphor is not None:
            self.env.add_candidate(metaphor)
            self.memory.memorize(metaphor.obj)

    def invent(self):
        """
        Generates INVENT_TRIES new metaphors and evaluates them, then returns the one with the best
        evaluation.

        :return: the metaphor with the best evaluation
        """
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
        """
        Generate a new metaphor by a very simple method:

        * shuffle the lists of nouns and adjectives
        * repeatedly pick a noun, then pick another noun, then check if they have any adjectives in common
        * if an adjective is found in common, with probability 0.5 create a metaphor using these two nouns and that adjective.  With probability 0.5 continue searching.
        * if no adjective in common is found, pick a new noun (without replacement)

        :return: an Artifact with the Metaphor as its object and :class:'Metaphor' as its domain
        """
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
        """
        Evaluation method inherited from CreativeAgent.  If the object is a Metaphor, evaluate it with eval_metphor().  Otherwise
        give a -1 evaluation.

        :param artifact: the artifact to be evaluated
        :return: The evaluation score for the metaphor (or -1) and None for framing
        """
        if isinstance(artifact.obj, Metaphor):
            return self.eval_metaphor(artifact.obj), None
        return -1, None

    def count_noun_metaphors(self, noun, shared_noun):
        """
        Count the appearances of a noun in the metaphor memory.  Also count the number of metaphors which have the same other noun as the one given.

        :param noun: the noun to count
        :type noun: :class:'Noun'
        :param shared_noun: the other noun in the metaphor
        :type shared_noun: :class:'Noun'
        :return: a tuple including the metaphor counts for the single noun and for both nouns
        """
        shared_count = 0
        count = 0
        if noun in self.memory.metaphor_lookup.keys():
            for other_noun, metaphor_list in self.memory.metaphor_lookup[noun].items():
                if other_noun == shared_noun:
                    shared_count += len(metaphor_list)
                count += len(metaphor_list)
        return count, shared_count

    def eval_metaphor(self, metaphor):
        """
        Evaluate a metaphor by calculating four scores and taking their weighted sum.

        The first two scores are the noun scores.  One for each of the metaphor's nouns.  These are returned by count_noun_metaphors(),
        and indicate the number of metaphors in memory which include the noun.

        The shared_count score is also returned by count_noun_metaphors(), and indicates the number of metaphors in memory which
        include both nouns in the metaphor being evaluated.

        The adjective score is indicates the number of metaphors in memory which use the same adjective as the metaphor being evaluated.

        :param metaphor: The metaphor to be evaluated
        :return: The evaluation score for the metaphor
        """
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
