from creamas import Simulation
from Model_Classes import Word, Noun
from MetaphorAgent import MetaphorAgent
from HaikuAgent import HaikuAgent
from MetaHaikuEnvironment import MetaHaikuEnvironment
import os


if __name__ == "__main__":
    fillers = [
        Word('is', 1),
        Word('and', 1),
        Word('ere', 1),
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

    env = MetaHaikuEnvironment.create(('localhost', 5555))

    for i in range(0, 20):
        MetaphorAgent(env, nouns)
    HaikuAgent(env, nouns, fillers)

    sim = Simulation(env, log_folder='logs', callback=env.vote)
    sim.async_steps(500)
    sim.end()


