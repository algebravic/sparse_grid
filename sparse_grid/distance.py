"""
Minimal distance cover for a finite metric space.
"""
from typing import List, Iterable, Tuple
from pysat.formula import WCNF, IDPool
from pysat.card import EncType, CardEnc
from .util import solve_maxsat, enumerate_maxsat
from .metric import MetricSpace, MetricElement, pair_dist, MPAIR

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
    
def distance_cover(space: MetricSpace,
                   bound: int = 0) -> Tuple[WCNF, IDPool]:
    """
    Used Max Sat to find a minimal distance cover of a finite metric
    space.

    There should be methods for vector spaces with symmetries.

    If bound > 0, find the maximum number of distances
    which can be covered by <= bound colors
    """
    distances = pair_dist(space)
    cnf = WCNF()
    pool = IDPool()

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
                   **kwds) -> List[MetricElement]:
    """
    Get one solution.
    """

    cnf, pool = distance_cover(space, bound=bound)
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
