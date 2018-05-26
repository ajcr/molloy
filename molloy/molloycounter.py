from collections import Counter

from .collectionconstraints import CollectionConstraintHandler


class Molloy(Counter):
    """
    A collection of objects with which to count
    numbers of possible collections, sequences or
    partitions.

    As with the collections.Counter class, the input
    can be any iterable, or a dictionary of existing
    counts. Unlike the parent class, the default when
    nothing is passed in is to create an empty dict-like
    object.

    Note that all counts must be positive integers.
    """
    def __init__(self, collection=''):
        super().__init__(collection)
        if not all(self._is_positive_integer(n) for n in self.values()):
            raise ValueError('Non-integer counts for items')

    @staticmethod
    def _is_positive_integer(n):
        return n > 0 and isinstance(n, int)

    def count_collections(self, size=None, constraints=None):
        """
        Count the number of collections of a particular
        size.

        The collection can optionally meet any number of
        constraints on the items that it contains.
        """
        if size is None:
            size = self.total

        if constraints is not None:
            constraints = constraints.replace('\n', ' ')

        x = CollectionConstraintHandler(constraints or '', self, size)

        return x.solution

    def count_sequences(self, size):
        """
        Count the number of sequences of a particular
        size, optionally meeting any number of constraints
        on the items that make up that sequence.
        """
        raise NotImplementedError

    def count_partitions(self, size):
        """
        Count the number of partitions of a particular
        size, optionally meeting any number of constraints
        on the items that make up the partitions.
        """
        raise NotImplementedError
