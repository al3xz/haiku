from creamas import CreativeAgent, Artifact
from Model_Classes import Haiku
from MetaphorMemory import MetaphorMemory
import random


class HaikuAgent(CreativeAgent):
    def __init__(self, env, nouns, fillers, mem_cap=500):
        super().__init__(env)
        self.nouns = nouns
        self.fillers = fillers
        self.memory = MetaphorMemory(mem_cap)

    GUESS_SCORE_WEIGHT = 1
    WORD_VARIETY_WEIGHT = 1

    async def act(self):
        if len(self.env.artifacts) > 0:
            # memorize the most recent artifact.  Agents will distinguish themselves once they start forgetting
            for winner in self.env.artifacts[(-self.env.num_metaphors_accepted_per_round - 1):-1]:
                self.memory.memorize(winner.obj)

        haiku = self.generate()
        if haiku is not None:
            self.env.add_candidate(haiku)

    def generate(self):
        known_topics = self.memory.metaphor_lookup.keys()
        if len(known_topics) == 0:
            return None
        topic = random.choice(list(known_topics))
        nouns, adjectives = self.get_applicable(topic)
        line_1 = self.write_line(5, nouns, adjectives)
        line_2 = self.write_line(7, nouns, adjectives)
        line_3 = self.write_line(5, nouns, adjectives)
        return Artifact(self, Haiku(topic, line_1, line_2, line_3, max(len(nouns), len(adjectives))), domain=Haiku)

    def write_line(self, length, nouns, adjectives):
        line = []
        sylla_count = 0
        while sylla_count < length:
            choice = random.randint(0, 5)
            if choice <= 1:
                line += [random.choice(nouns)]
            elif choice <= 3:
                line += [random.choice(adjectives)]
            else:
                line += [random.choice(self.fillers)]
            sylla_count += line[-1].syllables
        if sylla_count > length:
            sylla_count -= line[-1].syllables
            line = line[:-1]
        while sylla_count < length:
            line += [random.choice(self.fillers)]
            sylla_count += 1
        return line

    def get_applicable(self, topic):
        if len(self.memory.metaphor_lookup) == 0:
            return [], []
        applicable_nouns = list(self.memory.metaphor_lookup[topic].keys())
        applicable_adjectives = []
        for noun in applicable_nouns:
            applicable_adjectives += [meta.adjective for meta in self.memory.metaphor_lookup[topic][noun]]
        return applicable_nouns, applicable_adjectives

    def evaluate(self, artifact):
        haiku = artifact.obj
        haiku_content = haiku.line_1 + haiku.line_2 + haiku.line_3

        word_variety_score = len(set(haiku_content)) / float(len(haiku_content))

        candidate_metaphors = []
        for word in haiku_content:
            if word in self.memory.metaphor_lookup.keys():
                for other_noun in self.memory.metaphor_lookup[word]:
                    for metaphor in self.memory.metaphor_lookup[word][other_noun]:
                        candidate_metaphors += [metaphor]

        candidate_scores = dict([(candidate, 1) for candidate in candidate_metaphors])
        for word in haiku_content:
            for metaphor in candidate_metaphors:
                if word == metaphor.adjective:
                    candidate_scores[metaphor] += 1

        topic_scores = dict()
        for cand in candidate_scores:
            if cand.noun_2 not in topic_scores.keys():
                topic_scores[cand.noun_2] = 0
            topic_scores[cand.noun_2] += candidate_scores[cand]

        if len(topic_scores) == 0:
            guess_score = 0
        else:
            guesses = sorted(topic_scores, key=topic_scores.get, reverse=True)[0:3]
            if haiku.topic == guesses[0]:
                guess_score = 10
                artifact.obj.guessed_by += 1
            elif len(guesses) > 1 and haiku.topic == guesses[1]:
                guess_score = 4
            elif len(guesses) > 2 and haiku.topic == guesses[2]:
                guess_score = 1
            else:
                guess_score = 0
        guess_score /= 10

        return guess_score * HaikuAgent.GUESS_SCORE_WEIGHT + word_variety_score * HaikuAgent.WORD_VARIETY_WEIGHT, guess_score > 0.6