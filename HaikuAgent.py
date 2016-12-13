from creamas import CreativeAgent, Artifact
from Model_Classes import Haiku
from MetaphorMemory import MetaphorMemory
import random


class HaikuAgent(CreativeAgent):
    """
    This class is a type of CreativeAgent which generates and evaluates haiku artifacts.

    Attributes:
        GUESS_SCORE_WEIGHT    The weight given to the guess-ability of a haiku when evaluating that haiku

        WORD_VARIETY_WEIGHT   The weight given to the word variety of a haiku when evaluating that haiku
    """

    def __init__(self, env, fillers, mem_cap=500):
        """
        :param env (Environment): the creamas environment the agent will operate in
        :param fillers (list of :class:'Word'): a list of filler words which can appear in any haiku
        :param mem_cap (int): the number of metaphors the agent will keep in its memory before it starts forgetting them at random
        """
        super().__init__(env)
        self.fillers = fillers
        self.memory = MetaphorMemory(mem_cap)

    GUESS_SCORE_WEIGHT = 1
    WORD_VARIETY_WEIGHT = 1

    async def act(self):
        """
        Each simulation round, the HaikuAgent memorizes the metaphor winners from last round, then generates a
        new :class:'Haiku' and enters it as a candidate.
        """
        if len(self.env.artifacts) > 0:
            # memorize the most recent artifact.  Agents will distinguish themselves once they start forgetting
            for winner in self.env.artifacts[(-self.env.num_metaphors_accepted_per_round - 1):-1]:
                self.memory.memorize(winner.obj)

        haiku = self.generate()
        if haiku is not None:
            self.env.add_candidate(haiku)

    def generate(self):
        """
        The HaikuAgent generates a new haiku, drawing on the metaphors in its memory.  This includes three steps.

        * pick a topic noun from a random metaphor in memory
        * compile a list of nouns and adjectives linked to the topic by searching the metaphor memory
        * generate three lines of text with the appropriate syllable counts by picking from the filler words, nouns, and adjectives

        :return: a new :class:'Haiku'
        """
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
        """
        Generates a line of text with the desired syllable count using the given nouns and adjectives.  The process is:

        * randomly select whether the next word will be filler (1/5 chance), noun (2/5), or adjective (2/5)
        * randomly select the specific word from the appropriate list and add it to the line.  Update the syllable count.
        * if the syllable count is greater than the desired amount, delete the last word and add filler words until the count is correct
        * else repeat

        :param length: the desired number of syllables
        :type length: int
        :param nouns: the list of nouns to choose from
        :type nouns: list of :class:'Noun'
        :param adjectives: the list of adjectives to choose from
        :type adjectives: list of :class:'Word'
        :return: a line of text with the appropriate number of syllables
        """
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
        """
        Search for nouns and adjectives linked to the given topic noun by metaphors in the memory.  Nouns are chose if they
        share a metaphor with the topic.  Adjectives are chosen if a metaphor involving the topic uses them.

        :param topic: The topic noun
        :type topic: :class:'Noun'
        :return: a tuple containing the lists of applicable nouns and adjectives
        """
        if len(self.memory.metaphor_lookup) == 0:
            return [], []
        applicable_nouns = list(self.memory.metaphor_lookup[topic].keys())
        applicable_adjectives = []
        for noun in applicable_nouns:
            applicable_adjectives += [meta.adjective for meta in self.memory.metaphor_lookup[topic][noun]]
        return applicable_nouns, applicable_adjectives

    def evaluate(self, artifact):
        """
        Evaluate a :class:'Haiku' by computing guess and word variety scores and returning their weighted sum.

        Word variety is calculated as (unique words / total words)

        Guesses are created by searching the metaphor memory for nouns which share a metaphor with nouns in the :class:'Haiku' and making a list.
        For adjectives, all nouns for which there is a metaphor in memory using that adjective are added to the list.  If a noun is added
        multiple times during the noun and adjective search, it gets a higher score.  The top 3 scores are the guesses.

        Guess score is 1.0 for a first guess,  0.4 for a second guess, and 0.1 for a third guess.

        Weights for the guess score and word variety score are class attributes of HaikuAgent.

        :param artifact: the artifact to be evaluated.  The domain should be :class:'Haiku'.
        :return: A tuple containing the score for the artifact and a boolean indicating whether the first guess was correct for framing.
        """
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
        for cand in candidate_scores.keys():
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