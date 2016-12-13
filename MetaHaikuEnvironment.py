from creamas import Environment
from Model_Classes import Metaphor, Haiku
from MetaphorAgent import MetaphorAgent
from HaikuAgent import HaikuAgent
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class MetaHaikuEnvironment(Environment):
    """
    This class is a type of Environment which can handle both metaphor and haiku agents and objects.  Both types of artifacts
    can be candidates in the same round, and only the corresponding agents should vote on them.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_metaphors_accepted_per_round = kwargs.get('metaphor_winners') or 1
        self.haikus = []

    def vote(self, age):
        """
        This method implements a custom voting process to separate metaphor and haiku candidates and collect votes from
        the appropriate type of agents for each group.  The process is as follows:

        * Separate candidates into metaphors and haiku
        * Separate agents in MetaphorAgents and HaikuAgents
        * Have each agent evaluate each candidate of its type.  Give each candidate a score which is the average of these
        evaluations
        * Apply the 50% score penalty to haiku which are guessed by 90% or more of the HaikuAgents
        * Choose the top *self.num_metaphors_accepted_per_round* scoring metaphors as winners.  Add them to the environment
        artifacts and print them to the log.
        * Choose the top scoring haiku and add it to *self.haikus*.  Print it, along with some meta-information about it
        (the number of metaphor agents which guessed it correctly and the number of metaphors used to create it)

        :param age: Does nothing.  Required due to inheritance.
        """

        metaphor_candidates = [cand for cand in self._candidates if cand.domain() == Metaphor]
        haiku_candidates = [cand for cand in self._candidates if cand.domain() == Haiku]

        metaphor_scores = dict()
        haiku_scores = dict()

        for metaphor in metaphor_candidates:
            metaphor_scores[metaphor] = 0
        for haiku in haiku_candidates:
            haiku_scores[haiku] = 0

        agents = self.get_agents(address=False)
        metaphor_agents = [agent for agent in agents if isinstance(agent, MetaphorAgent)]
        haiku_agents = [agent for agent in agents if isinstance(agent, HaikuAgent)]

        for a in metaphor_agents:
            votes = a.vote(candidates=metaphor_candidates)
            for vote in votes:
                metaphor_scores[vote[0]] += vote[1] / len(metaphor_agents)
        for a in haiku_agents:
            votes = a.vote(candidates=haiku_candidates)
            for vote in votes:
                haiku_scores[vote[0]] += vote[1] / len(haiku_agents)

        # Penalty for being easily guessable by everyone
        for haiku, score in haiku_scores.items():
            if haiku.obj.guessed_by > 0.9 * len(haiku_agents):
                haiku_scores[haiku] /= 2

        if len(metaphor_candidates) >= self.num_metaphors_accepted_per_round:
            winning_metaphors = sorted(metaphor_scores, key=metaphor_scores.get, reverse=True)[0:self.num_metaphors_accepted_per_round]
            for metaphor in winning_metaphors:
                self.add_artifact(metaphor)
                logger.info(str(metaphor.obj))

        if len(haiku_candidates) >= 1:
            winning_haiku = sorted(haiku_scores, key=haiku_scores.get, reverse=True)[0]
            self.haikus.append(winning_haiku)
            logger.info(str(winning_haiku.obj))
            logger.info(winning_haiku.obj.get_str_metadata())

        self.clear_candidates()
