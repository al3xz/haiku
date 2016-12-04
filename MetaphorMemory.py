import random


class MetaphorMemory:
    def __init__(self, capacity):
        self._capacity = capacity
        self._count = 0
        self._metaphors = dict()
        self._adjective_counts = dict()

    @property
    def capacity(self):
        return self._capacity

    @property
    def count(self):
        return self._count

    @property
    def adjective_counts(self):
        return self._adjective_counts

    @property
    def metaphor_lookup(self):
        return self._metaphors

    def contains(self, metaphor):
        if metaphor.noun_1 not in self._metaphors.keys():
            return False

        if metaphor.noun_2 not in self._metaphors[metaphor.noun_1].keys():
            return False

        if metaphor not in self._metaphors[metaphor.noun_1][metaphor.noun_2]:
            return False

        return True

    def get_random_metaphor(self):
        noun_from = random.choice(list(self._metaphors.keys()))
        noun_to = random.choice(list(self._metaphors[noun_from].keys()))
        return random.choice(self._metaphors[noun_from][noun_to])

    def forget(self, metaphor):
        self._metaphors[metaphor.noun_1][metaphor.noun_2].remove(metaphor)
        self._metaphors[metaphor.noun_2][metaphor.noun_1].remove(metaphor)
        self._adjective_counts[metaphor.adjective] -= 1

    def memorize(self, metaphor):
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
