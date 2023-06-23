"""
Finite Metric spaces
"""
from typing import Iterable, Any, List, Tuple, Dict
from itertools import product, combinations
from more_itertools import bucket

class MetricSpace:
    pass

class MetricElement:
    pass

def _validate(space: MetricSpace, elt: MetricElement) -> bool:
    """
    validate compatiblity for metric space.
    """
    return (isinstance(elt, MetricElement)
            and isinstance(space, MetricSpace)
            and elt._parent is space)

class MetricElement:

    def __init__(self, parent: MetricSpace, ident: Any):

        self._parent = parent
        self._ident = ident

    def __eq__(self, other: MetricElement):

        if not _validate(self._parent, other):
            raise ValueError("Different parents")
        return self._ident == other._ident
    
    def __le__(self, other: MetricElement):

        if not _validate(self._parent, other):
            raise ValueError("Different parents")
        return self._ident <= other._ident

    def __lt__(self, other: MetricElement):

        if not (isinstance(other, MetricElement)
                and self._parent is other._parent):
            raise ValueError("Different parents")
        return self._ident < other._ident

    @property
    def id(self):
        return self._ident

    def __str__(self):
        return str(self._ident)

    def __repr__(self):
        return f'{self._parent.name}({self._ident})'

    def __hash__(self):
        """ The hash function for lookups """
        return hash((self._parent._name, self._ident))
    
class MetricSpace:

    def __init__(self, name: str):

        self._name = name

    @property
    def name(self):
        return self._name

    def _valid(self, elt1: MetricElement, elt2: MetricElement):
        if not (isinstance(elt1, MetricElement)
                and isinstance(elt2, MetricElement)
                and elt1._parent is self
                and elt2._parent is self):
            raise ValueError("Incompatible elements")

    def dist(self, elt1: MetricElement, elt2: MetricElement) -> int:
        """
        The distance function.
        """
        raise NotImplemented

    def elements(self) -> Iterable[MetricElement]:
        """
        All the elements in some arbitrary order.
        """
        raise NotImplemented

class Grid(MetricSpace):

    def __init__(self, mdim: int, ndim: int):

        self._mdim = mdim
        self._ndim = ndim

        super().__init__(f'grid[{mdim},{ndim}]')

    def elements(self) -> Iterable[MetricElement]:
        """
        All the elements in the grid.
        """

        yield from (MetricElement(self, _)
                    for _ in product(range(self._mdim),
                                     range(self._ndim)))

    def dist(self, elt1: MetricElement, elt2: MetricElement):
        """ Euclidean distance^2 """
        self._valid(elt1, elt2)
        return ((elt1._ident[0] - elt2._ident[0])**2
                + (elt1._ident[1] - elt2._ident[1])**2)

class TaxiCab(MetricSpace):

    def __init__(self, mdim: int, ndim: int):

        self._mdim = mdim
        self._ndim = ndim

        super().__init__(f'taxicab[{mdim},{ndim}]')

    def elements(self) -> Iterable[MetricElement]:
        """
        All the elements in the grid.
        """

        yield from (MetricElement(self, _)
                    for _ in product(range(self._mdim),
                                     range(self._ndim)))

    def dist(self, elt1: MetricElement, elt2: MetricElement):
        """ Euclidean distance^2 """
        self._valid(elt1, elt2)
        return (abs(elt1._ident[0] - elt2._ident[0])
                + abs(elt1._ident[1] - elt2._ident[1]))

class Cube(MetricSpace):

    def __init__(self, dim: int, size: int):

        self._size = size
        self._dim = dim

        super().__init__(f'cube[{dim},{size}]')

    def elements(self) -> Iterable[MetricElement]:
        """
        All the elements in the grid.
        """

        yield from (MetricElement(self, _)
                    for _ in product(range(self._size),
                                     repeat=self._dim))

    def dist(self, elt1: MetricElement, elt2: MetricElement):
        """ Euclidean distance^2 """
        self._valid(elt1, elt2)
        pairs = zip(elt1._ident, elt2._ident)
        return sum(((_[0] - _[1]) ** 2 for _ in pairs))

MPAIR = Tuple[MetricElement, MetricElement]    
    
def pair_dist(space: MetricSpace) -> Dict[int, List[MPAIR]]:
    """
    pair distance distribution.
    """
    distribute = bucket(combinations(space.elements(), 2),
                        key=lambda _: space.dist(*_))
    return {_: list(distribute[_]) for _ in list(distribute)}
