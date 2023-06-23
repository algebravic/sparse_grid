"""
General SAT utilities
"""
from typing import List, Tuple, Iterable
from pysat.formula import WCNF, CNF, IDPool
from pysat.examples.rc2 import RC2, RC2Stratified

PAIR = Tuple[int, int]

def distance(pnt1: PAIR, pnt2: PAIR) -> int:
    return (pnt1[0] - pnt2[0]) ** 2 + (pnt1[1] - pnt2[1]) ** 2


def solve_maxsat(cnf: WCNF,
                 stratified: bool = False, **kwds) -> List[int] | None:
    """
    Solve with a maxsat solver
    """
    maxsat_solver = RC2Stratified if stratified else RC2
    max_solver = maxsat_solver(cnf, **kwds)
    soln = max_solver.compute()
    print("Time = {}".format(max_solver.oracle_time()))
    return soln

def enumerate_maxsat(cnf: WCNF,
                     chatter: bool = False,
                     stratified: bool = False,
                     **kwds) -> Iterable[List[int]]:
    """
    Solve with a maxsat solver
    """
    maxsat_solver = RC2Stratified if stratified else RC2
    max_solver = maxsat_solver(cnf, **kwds)
    old_cost  = None
    for soln in max_solver.enumerate():
        cost = max_solver.cost
        if old_cost is not None and cost != old_cost:
            break
        old_cost = cost
        yield soln
        if chatter:
            print(f"Cost = {cost},"
                  + f"time={max_solver.oracle_time()}")
    print(f"Total Time = {max_solver.oracle_time()}")

def get_answer(soln: List[int] | None,
               pool: IDPool,
               stem: str = 'x') -> List[PAIR] | None:
    """
    Get the answer.
    """
    if soln is None:
        return None

    pos = [pool.obj(_) for _ in soln if _ > 0]
    xvals = [_[1:] for _ in pos if _ is not None and _[0] == stem]
    pvals = [(_[1:3], _[3:5]) for _ in pos if _ is not None
             and _[0] == 'p']
    pdict = {distance(*_): _ for _ in pvals}
    return xvals, pdict
