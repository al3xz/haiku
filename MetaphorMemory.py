import random


class MetaphorMemory:
    """
    This class represents an agent's memory of metaphors it has encountered.
    """
    def __init__(self, capacity):
        assert type(capacity) is int, "capacity is not an integer"
        self._capacity = capacity
        self._count = 0
        self._metaphors = dict()
        self._adjective_counts = dict()

    @property
    def capacity(self):
        """
        Returns the maximum number of metaphors which can be stored in the memory.  If new metaphors are memorized while
        at capacity, a random old metaphor will be forgotten.
        """
        return self._capacity

    @property
    def count(self):
        """
        The number of metaphors currently memorized.
        """
        return self._count

    @property
    def adjective_counts(self):
        """
        Returns a dict containing all adjectives used in the metaphors in the memory and count of how many times those
         adjectives are used.
        """
        return self._adjective_counts

    @property
    def metaphor_lookup(self):
        """
        Returns the metaphor memory.  The structure allows two nouns to be used in either order as
        keys to return a list of metaphors which link those two nouns.
        """
        return self._metaphors

    def contains(self, metaphor):
        """
        A method to check whether a metaphor is in the memory already.  Note that metaphor equality is determined by
        having the same nouns and adjective, not by object id.  The order of the nouns may also be reversed.

        :param metaphor: The metaphor to check for.
        :return: True if the memory contains that metaphor, false otherwise.
        """
        if metaphor.noun_1 not in self._metaphors.keys():
            return False

        if metaphor.noun_2 not in self._metaphors[metaphor.noun_1].keys():
            return False

        if metaphor not in self._metaphors[metaphor.noun_1][metaphor.noun_2]:
            return False

        return True

    def get_random_metaphor(self):
        """
        Returns a random metaphor from the memory.
        """
        noun_from = random.choice(list(self._metaphors.keys()))
        noun_to = random.choice(list(self._metaphors[noun_from].keys()))
        return random.choice(self._metaphors[noun_from][noun_to])

    def forget(self, metaphor):
        """
        Removes the given metaphor from the memory.  Will throw a KeyNotFoundException if that metaphor does not
        exist in the memory.

        :param metaphor: The metaphor to remove
        """
        self._metaphors[metaphor.noun_1][metaphor.noun_2].remove(metaphor)
        self._metaphors[metaphor.noun_2][metaphor.noun_1].remove(metaphor)
        # if the list is empty remove the key
        if not self._metaphors[metaphor.noun_1][metaphor.noun_2]:
            del self._metaphors[metaphor.noun_1][metaphor.noun_2]
            del self._metaphors[metaphor.noun_2][metaphor.noun_1]
        if len(self._metaphors[metaphor.noun_1]) == 0:
            del self._metaphors[metaphor.noun_1]
        if len(self._metaphors[metaphor.noun_2]) == 0:
            del self._metaphors[metaphor.noun_2]
        self._adjective_counts[metaphor.adjective] -= 1

    def memorize(self, metaphor):
        """
        Adds a metaphor to the memory.  If the memory is at capacity before this is called, a random metaphor will be
        forgotten first.
        """
        if self.contains(metaphor):
            return

        self._count += 1
        if self._count > self._capacity:
            to_remove = self.get_random_metaphor()
            self.forget(to_remove)

        def __insert_metaphor_one_way(noun_from, noun_to, metaphor_obj):
            if noun_from not in self._metaphors.keys():
                self._metaphors[noun_from] = dict()
            if noun_to not in self._metaphors[noun_from].keys():
                self._metaphors[noun_from][noun_to] = []
            self._metaphors[noun_from][noun_to] += [metaphor_obj]

        __insert_metaphor_one_way(metaphor.noun_1, metaphor.noun_2, metaphor)
        __insert_metaphor_one_way(metaphor.noun_2, metaphor.noun_1, metaphor)

        if metaphor.adjective not in self._adjective_counts.keys():
            self._adjective_counts[metaphor.adjective] = 0
        self._adjective_counts[metaphor.adjective] += 1
