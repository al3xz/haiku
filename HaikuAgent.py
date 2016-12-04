from creamas import CreativeAgent, Artifact
from Model_Classes import Haiku
import random


class HaikuAgent(CreativeAgent):
    def __init__(self, env, nouns, fillers):
        super().__init__(env)
        self.nouns = nouns
        self.fillers = fillers

    async def act(self):
        haiku = self.generate()
        if haiku is not None:
            self.env.add_candidate(haiku)

    def generate(self):
        topic = random.choice(self.nouns)
        nouns, adjectives = self.get_applicable(topic)
        if len(nouns) == 0:
            return None
        line_1 = self.write_line(5, nouns, adjectives)
        line_2 = self.write_line(7, nouns, adjectives)
        line_3 = self.write_line(5, nouns, adjectives)
        return Artifact(self, Haiku(topic, line_1, line_2, line_3), domain=Haiku)

    def write_line(self, length, nouns, adjectives):
        line = []
        sylla_count = 0
        while sylla_count < length:
            choice = random.randint(0, 2)
            if choice == 0:
                line += [random.choice(nouns)]
            elif choice == 1:
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
        applicable_nouns = []
        applicable_adjectives = []
        if len(self.env.artifacts) == 0:
            return [], []
        for metaphor in [art.obj for art in self.env.artifacts]:
            if metaphor.noun_1.word == topic.word:
                applicable_nouns += [metaphor.noun_2]
                applicable_adjectives += [metaphor.adjective]
            if metaphor.noun_2.word == topic.word:
                applicable_nouns += [metaphor.noun_1]
                applicable_adjectives += [metaphor.adjective]
        return applicable_nouns, applicable_adjectives

    def evaluate(self, artifact):
        return random.uniform(0, 1), None