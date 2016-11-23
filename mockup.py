from creamas import CreativeAgent, Environment, Simulation
import random
import logging
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Word:
    def __init__(self, word, syllables):
        self.word = word
        self.syllables = syllables


class Noun(Word):
    def __init__(self, word, syllables, adjectives=None):
        super().__init__(word, syllables)
        self.adjectives = adjectives or []

    def add_adjectives(self, adjective):
        self.adjectives += [adjective]

    def get_adjectives(self):
        random.shuffle(self.adjectives)
        return self.adjectives

    @staticmethod
    def parse(text):
        parts = text.split(' ')
        noun = Noun(parts[0], int(parts[1]))

        parts = parts[2:]
        while len(parts) > 0:
            noun.add_adjectives(Word(parts[0], int(parts[1])))
            parts = parts[2:]
        return noun


class Metaphor:
    def __init__(self, noun_1, noun_2, adjective):
        self.noun_1 = noun_1
        self.noun_2 = noun_2
        self.adjective = adjective


class Haiku:
    def __init__(self, topic, line_1, line_2, line_3):
        self.topic = topic
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_3 = line_3

    def __str__(self):
        line_1_str = " ".join([word.word for word in self.line_1])
        line_2_str = " ".join([word.word for word in self.line_2])
        line_3_str = " ".join([word.word for word in self.line_3])
        return "\n".join([self.topic.word.upper() + ':\n', line_1_str, line_2_str, line_3_str])


class MetaphorAgent(CreativeAgent):
    def __init__(self, env, nouns):
        super().__init__(env)
        self.nouns = nouns

    async def act(self):
        metaphor = None
        while metaphor is None:
            metaphor = self.generate()
        self.env.add_candidate(metaphor)

    def generate(self):
        random.shuffle(self.nouns)
        for noun_1 in self.nouns:
            for noun_2 in self.nouns:
                if noun_1.word != noun_2.word:
                    for adj in noun_1.get_adjectives():
                        if adj.word in [adj2.word for adj2 in noun_2.get_adjectives()]:
                            if random.randint(0, 1) == 1:
                                return Metaphor(noun_1, noun_2, adj)
        return None

    def evaluate(self, artifact):
        return random.uniform(0, 1), None


class HaikuAgent(CreativeAgent):
    def __init__(self, env, nouns, fillers):
        super().__init__(env)
        self.nouns = nouns
        self.fillers = fillers

    async def act(self):
        haiku = self.generate()
        if haiku is not None:
            logger.info(str(haiku))

    def generate(self):
        topic = random.choice(self.nouns)
        nouns, adjectives = self.get_applicable(topic)
        if len(nouns) == 0:
            return None
        line_1 = self.write_line(5, nouns, adjectives)
        line_2 = self.write_line(7, nouns, adjectives)
        line_3 = self.write_line(5, nouns, adjectives)
        return Haiku(topic, line_1, line_2, line_3)

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
        for metaphor in self.env.artifacts:
            if metaphor.noun_1.word == topic.word:
                applicable_nouns += [metaphor.noun_2]
                applicable_adjectives += [metaphor.adjective]
            if metaphor.noun_2.word == topic.word:
                applicable_nouns += [metaphor.noun_1]
                applicable_adjectives += [metaphor.adjective]
        return applicable_nouns, applicable_adjectives

    def evaluate(self, artifact):
        return random.uniform(0, 1), None


class MockEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def vote(self, age):
        for artifact in self.perform_voting(method='mean'):
            self.add_artifact(artifact[0])
            #logger.info('{} and {} share {}'.format(artifact[0].noun_1.word, artifact[0].noun_2.word, artifact[0].adjective.word))
        self.clear_candidates()


if __name__ == "__main__":
    fillers = [
        Word('is', 1),
        Word('and', 1),
        Word('err', 1),
        Word('such', 1),
        Word('how', 1),
        Word('grows', 1),
        Word('finds', 1),
        Word('leaves', 1),
        Word('looms', 1),
        Word('rises', 1),
        Word('yo', 1),
    ]

    with open(os.getcwd() + '/nouns.txt', 'r') as f:
        lines = f.readlines()
    nouns = [Noun.parse(line) for line in lines]

    # codec=aiomas.MsgPack, extra_serializers=[get_listmem_ser]
    env = MockEnvironment.create(('localhost', 5555))

    for i in range(0, 50):
        MetaphorAgent(env, nouns)
    HaikuAgent(env, nouns, fillers)

    sim = Simulation(env, log_folder='logs', callback=env.vote)
    sim.async_steps(100)
    sim.end()


