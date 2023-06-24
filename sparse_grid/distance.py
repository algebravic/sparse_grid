"""
Minimal distance cover for a finite metric space.
"""
from typing import List, Iterable, Tuple, Dict, FrozenSet
from itertools import chain
from pysat.formula import WCNF, IDPool
from pysat.card import EncType, CardEnc
from .util import solve_maxsat, enumerate_maxsat
from .metric import MetricSpace, MetricElement, pair_dist, MPAIR

DIST = Dict[int, List[MetricElement]]
PAIR = FrozenSet[MetricElement]

def get_values(pool: IDPool, soln: List[int],
               stem: str = 'x',
               neg: bool = False) -> List[MetricElement]:
    """
    Get the solution.
    """
    if neg:
        sel = [pool.obj(- _) for _ in soln if _ < 0]
    else:
        sel = [pool.obj(_) for _ in soln if _ > 0]
    return [_[1] for _ in sel if _ is not None and _[0] == stem]

def _normalize(pair: PAIR) -> PAIR:
    """
    Normalize
    """
    return pair if pair[0] < pair[1] else (pair[1], pair[0])

def extended_model(distances: DIST, cnf: WCNF, pool: IDPool):
    """
    Calculate various sets that we need for the extended model.
    """
    support = {}
    #partner[d,x]: set of y such that dist(x,y) = d
    covers = {}
    # support[d] is the set of all elements that can yield d
    for dist, pairs in distances.items():
        support[dist] = set(chain(*pairs))
        covers[dist] = set(map(frozenset, pairs))

    for dist, pairs in distances.items():
        dvar = pool.id(('d', dist))
        for elt in support[dist]:
            # Is elt is involved in some pair
            # if one of the w's is true then x is there
            lits = [pool.id(('w', _, dist))
                    for _ in covers[dist] if elt in _]
            for clause in CardEnc.atmost(
                    lits = lits + [- pool.id(('x', elt))],
                    bound = 1,
                    encoding = EncType.ladder,
                    vpool = pool).clauses:
                cnf.append([-dvar] + clause)
        # w({i,j},d) means {i,j} is the chosen one for d

        for clause in CardEnc.equals(
                lits = [pool.id(('w', _ ,dist))
                        for _ in covers[dist]],
                bound = 1,
                encoding = EncType.ladder,
                vpool = pool).clauses:
            cnf.append([-dvar] + clause)
        # Each distance needs at least 2 candidates
        cnf.extend(CardEnc.atleast(
            lits = [pool.id(('x', elt))
                    for elt in support[dist]],
            bound = 2,
            encoding = EncType.totalizer,
            vpool = pool))
        
def simple_model(distances: DIST, cnf: WCNF, pool: IDPool):
    """
    Simple model.
    """
    for dist, pairs in distances.items():
        dvar = pool.id(('d', dist))
        cnf.append(
            [-dvar] + [pool.id(('p',_)) for _ in pairs])
        for pair in pairs:
            pvar = pool.id(('p', pair))
            var1 = pool.id(('x', pair[0]))
            var2 = pool.id(('x', pair[1]))
            
            cnf.extend([[-pvar, var1], [-pvar, var2],
                        [pvar, -var1, -var2],
                        [-pvar, dvar]])
    return distances, cnf, pool

def distance_cover(space: MetricSpace,
                   simple: bool = True,
                   bound: int = 0) -> Tuple[WCNF, IDPool]:
    """
    Used Max Sat to find a minimal distance cover of a finite metric
    space.

    There should be methods for vector spaces with symmetries.

    If bound > 0, find the maximum number of distances
    which can be covered by <= bound colors
    """
    cnf = WCNF()
    pool = IDPool()
    distances = pair_dist(space)
    model = simple_model if simple else extended_model
    model(distances, cnf, pool)

    lits = [pool.id(('x', elt))
            for elt in space.elements()]
    if bound > 0:
        for dist in distances.keys():
            cnf.append([pool.id(('d', dist))], weight=1)
        cnf.extend(CardEnc.atmost(lits = lits,
                                  bound = bound,
                                  encoding = EncType.totalizer,
                                  vpool = pool))
    else:
        cnf.extend([[pool.id(('d', _))]
                    for _ in distances.keys()])
                    
        for lit in lits:
            cnf.append([-lit], weight=1)

    return cnf, pool

def distance_solve(space: MetricSpace,
                   bound: int = 0,
                   simple: bool = False,
                   **kwds) -> List[MetricElement]:
    """
    Get one solution.
    """

    cnf, pool = distance_cover(space, bound=bound, simple=simple)
    soln = solve_maxsat(cnf, **kwds)
    if bound > 0:
        return get_values(pool, soln, stem='d', neg=True)
    else:
        return get_values(pool, soln, stem='x')

def distance_enumerate(space: MetricSpace,
                       chatter: bool = False,
                       **kwds) -> Iterable[List[MetricElement]]:
    """
    Enumerate all solutions
    """
    cnf, pool = distance_cover(space)
    for soln in enumerate_maxsat(cnf,
                                 chatter = chatter,
                                 **kwds):
        yield get_values(pool, soln)
