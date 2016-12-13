import random


class Word:
    """
    Represents a word (either a noun or adjective).  We defined our own class for this instead of just using strings
    because it needed to include the syllable count.
    """
    def __init__(self, word, syllables):
        self.word = word
        self.syllables = syllables

    def __eq__(self, other):
        return isinstance(other, Word) and other.word == self.word and other.syllables == self.syllables

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.word, self.syllables))

    def __str__(self):
        return self.word


class Noun(Word):
    """
    Derived from word.  Adds a list of describing adjectives.
    """
    def __init__(self, word, syllables, adjectives=None):
        super().__init__(word, syllables)
        self.adjectives = adjectives or []

    def add_adjectives(self, adjective):
        """
        Add to the list of describing adjectives.

        :param adjective: the adjective to add.
        :type adjective: Word
        """
        self.adjectives += [adjective]

    def get_adjectives(self):
        """
        Returns the list of describing adjectives.  The list is shuffled first because generally this is used to get a
        random adjective.

        :return: The shuffled list of adjectives.
        """
        random.shuffle(self.adjectives)
        return self.adjectives

    def __eq__(self, other):
        return isinstance(other, Noun) and other.word == self.word

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.word, self.syllables))

    def __str__(self):
        return str(self.word)

    def full_string(self):
        """
        Returns the noun, including all its describing adjectives, as a string.

        :return: noun: adjective adjective adjective
        """
        return "{}: {}".format(str(self.word), " ".join([str(adj) for adj in self.adjectives]))


    @staticmethod
    def parse(text):
        """
        Parse a noun object from a data file containing nouns and their describing adjectives.

        :param text: a line of text from a data file.  Format should be:

        noun # adjective # adjective #\n

        where # is replaced by the syllable count of the preceeding word
        :return: the parsed noun
        """
        parts = text.split(' ')
        noun = Noun(parts[0], int(parts[1]))

        parts = parts[2:]
        while len(parts) > 0:
            noun.add_adjectives(Word(parts[0], int(parts[1])))
            parts = parts[2:]
        return noun


class Metaphor:
    """
    This class represents a metaphor, as created by a MetaphorAgent.  It relates two nouns by a shared adjective.
    """
    def __init__(self, noun_1, noun_2, adjective):
        self.noun_1 = noun_1
        self.noun_2 = noun_2
        self.adjective = adjective

    def __eq__(self, other):
        if not isinstance(other, Metaphor):
            return False

        if (self.noun_1 == other.noun_1 and self.noun_2 == other.noun_2) \
            or (self.noun_1 == other.noun_2 and self.noun_2 == other.noun_1):
            return self.adjective == other.adjective

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.noun_1, self.noun_2, self.adjective))

    def __str__(self):
        an = 'an' if self.noun_2.word[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
        return "{} is as {} as {} {}".format(self.noun_1, self.adjective, an, self.noun_2)


class Haiku:
    """
    This class represents a haiku, as created by a HaikuAgent.  It has a topic (a noun), three lines (lists of words),
    and records of how many HaikuAgents have guessed it during evaluation and how many metaphors were used to create it.
    The syllable counts of the words in each line should add up to 5 for the first line, 7 for the second, and 5 again
    for the third.
    """
    def __init__(self, topic, line_1, line_2, line_3, metaphors_used):
        self.topic = topic
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_3 = line_3
        self.guessed_by = 0
        self.metaphors_used = metaphors_used

    def __str__(self):
        line_1_str = " ".join([word.word for word in self.line_1])
        line_2_str = " ".join([word.word for word in self.line_2])
        line_3_str = " ".join([word.word for word in self.line_3])
        return "\n".join([self.topic.word.upper() + ':\n', line_1_str, line_2_str, line_3_str])

    def get_str_metadata(self):
        """
        Returns the *self.guessed_by* and *self.metaphors_used* data as a readable string.

        :return: string of the metadata
        """
        return "\n".join(["Guessed by {}".format(self.guessed_by), "{} metaphors used".format(self.metaphors_used)])