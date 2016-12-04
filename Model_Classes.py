import random


class Word:
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
    def __init__(self, word, syllables, adjectives=None):
        super().__init__(word, syllables)
        self.adjectives = adjectives or []

    def add_adjectives(self, adjective):
        self.adjectives += [adjective]

    def get_adjectives(self):
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