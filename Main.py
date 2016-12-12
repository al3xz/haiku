from creamas import Simulation
from Model_Classes import Word, Noun
from MetaphorAgent import MetaphorAgent
from HaikuAgent import HaikuAgent
from gensim.models import word2vec
from MetaHaikuEnvironment import MetaHaikuEnvironment
import os

NUMBER_METAPHOR_AGENTS = 20
NUMBER_HAIKU_AGENTS = 5
FILE_NAME = '/nouns_brown.txt'


def filter_nouns(nouns):
    """
    Filter out nouns which has no other noun with a common adjective

    :param nouns: the list of nouns
    :return: the filtered list of nouns
    """

    matched = []
    for noun in nouns:
        matched_this = False
        for other_noun in nouns:
            if matched_this:
                break
            for adj in other_noun.adjectives:
                if adj in noun.adjectives:
                    matched += [noun]
                    matched_this = True
                    break
    return matched

if __name__ == "__main__":
    fillers = [
        Word('is', 1),
        Word('and', 1),
        Word('ere', 1),
        Word('such', 1),
        Word('how', 1),
        Word('grows', 1),
        Word('finds', 1),
        Word('flees', 1),
        Word('looms', 1),
        Word('rises', 1),
        Word('yo', 1),
        Word('this', 1),
        Word('there', 1),
        Word('of', 1),
        Word('like', 1),
    ]

    with open(os.getcwd() + FILE_NAME, 'r') as f:
        lines = f.readlines()
    nouns = [Noun.parse(line) for line in lines]

    word2vec_model = word2vec.Word2Vec.load(os.getcwd() + FILE_NAME + ".word2vec")
    #state bear
    #print(model)
    #print(model.similarity('manager', 'allocation'))

    nouns = filter_nouns(nouns)
    for noun in nouns[0:200]:
        print(noun.full_string())

    env = MetaHaikuEnvironment.create(('localhost', 5555))
    env.num_metaphors_accepted_per_round = 5

    for i in range(0, 20):
        MetaphorAgent(env, nouns, word2vec_model)
    for i in range(0, 5):
        HaikuAgent(env, fillers)

    sim = Simulation(env, log_folder='logs', callback=env.vote)
    sim.async_steps(500)
    sim.end()


