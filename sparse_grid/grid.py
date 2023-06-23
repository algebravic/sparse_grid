"""
Find a minimal set of points in the n x n grid so that all possible distances are represented.

Symmetries:  The group D_4 of order 8 operates on the square grid.
1) There are only two pairs which give a squared distance of (n-1)^2:
((0,0), (n-1,n-1)) and ((0,n-1), (n-1,0))
Without loss of generality, we can pick the first which breaks one symmetry.

2) For the squared distance of (n-1)^2 + (n-1)^2 we have the following pairs

((0,0), (n-1,n-2)), ((0,0), (n-2,n-1)), ((0,1), (n-1,n-1)), ((1,0), (n-1,n-1))
((0,n-2), (n-1,0)), ((0,n-1), (n-2,0)), ((0,n-1), (n-1,1), ((n-1,0), (1,n-1))
((n-2,0), (0,n-1)), ((n-1,0), (0,n-2)), ((n-1,0), (1,n-1), ((0,n-1), (n-1,1))

For the pair ((0,0), (n-1,n-1)) there are 4 symmetries that fix this:
(x,y) -> (n-1-x,n-1-y); (x,y) -> (y,x); (x,y) -> (n-1-y, n-1-x); identity

Except for the identity, none of these fix those points in class (2)
Therefore there are 3 orbits.  A symmetry break to make sure that only the
lexicographically smallest point in an orbit is chosen.

Orbit of ((0,0), (n-1,n-2)): {((0,1), (n-1,n-1)), ((1,0),(n-1,n-1)), ((0,0),(n-2,n-1))}
Orbit of ((0,n-2),(n-1,0)): {((0,n-1),(n-1,1)), ((1,n-1),(n-1,0)), ((0,n-1),(n-2,0))}

"""
from typing import Tuple, Iterable, List, Callable
from itertools import product, combinations
from functools import partial
import networkx as nx
from pysat.formula import WCNF,IDPool
from .util import solve_maxsat, get_answer, PAIR, distance
from .metric import Grid, MetricSpace, pair_dist

SYMM = Callable[[PAIR], PAIR]

def ident(arg: PAIR) -> PAIR:
    """ identity """
    return arg

def flip(arg: PAIR) -> PAIR:
    """ flip """
    return (arg[1], arg[0])

def reflect(high: int, arg: PAIR) -> PAIR:
    """ reflect """
    return (high-1-arg[0], high-1-arg[1])

def rflip(high: int, arg: PAIR) -> PAIR:
    """ reflect and flip """
    return (high-1-arg[1], high-1-arg[0])

def canonical(value: Tuple[PAIR, PAIR]) -> Tuple[PAIR, PAIR]:
    """ canonical form """
    return tuple(sorted(value))

def reps(values: List[Tuple[PAIR, PAIR]], funs: List[SYMM]) -> List[List[PAIR]]:
    """
    Orbits
    """
    gph = nx.DiGraph()
    for pnts in values:
        pnt = canonical(pnts)
        trans = [canonical(tuple(map(_,pnt))) for _ in funs]
        # add directed edges
        for pntx in trans:
            if pntx != pnt:
                gph.add_edge(*sorted((pnt, pntx)))
    lower = [node for node, in_degree in gph.in_degree()
            if in_degree == 0]
    upper = [node for node, in_degree in gph.in_degree()
            if in_degree != 0]

    return lower, upper

def grid_model(num: int,
               diag: bool=False,
               lex: bool=False,
               backward: bool=False,
               forbid: bool=False) -> Tuple[WCNF, IDPool]:
    """
    Use Max Sat to find the minimal grid.

    Variables: ('x', i, j) means (i,j) is in the set.
    (d,'i') means that distance i is in the set.
    """
    cnf = WCNF()
    pool = IDPool()
    all_dist = {}
    for pnt1, pnt2 in combinations(
            product(range(num), repeat=2), 2):
        dist = distance(pnt1, pnt2)
        if dist not in all_dist:
            all_dist[dist] = []
        pair = pnt1 + pnt2
        pvar = pool.id(('p',) + pair)
        var1 = pool.id(('x',) + pnt1)
        var2 = pool.id(('x',) + pnt2)
        # if the pair is in the covering set
        # then its two consituents must be present
        cnf.extend([[-pvar, var1], [-pvar, var2]])
        if backward:
            cnf.append([-var1, -var2, pvar])
        all_dist[dist].append(pair)
    print(f"# distances = {len(all_dist.keys())}")
    # print([(key, len(val)) for key, val in all_dist.items()])

    # For each distance, at least one pair must be present
    for pvars in all_dist.values():
        cnf.append([pool.id(('p',) + _) for _ in pvars])

    if diag:
        diagonal = [(0,0), (num-1, num-1)]
        cnf.append([pool.id(('p',) + diagonal[0] + diagonal[1])])

    if lex:
        # Get second largest distance
        second = (num - 1) ** 2 + (num - 2) ** 2
        cand = [(_[0:2], _[2:4]) for _ in all_dist[second]]
        funs = [flip, partial(reflect, num),
                partial(rflip, num)]
        leaders, nonleaders = reps(cand, funs)
        # Exactly one of them will hold
        print(leaders)
        cnf.append([pool.id(('p',) + _[0] + _[1])
                    for _ in leaders])
        if forbid:
            cnf.extend([[-pool.id(('p',) + _[0] + _[1])]
                        for _ in nonleaders])

    for pnt in product(range(num), repeat=2):
        cnf.append([-pool.id(('x',) + pnt)], weight=1)

    return cnf, pool

def find_grid(num: int,
              diag: bool = True,
              lex: bool = False,
              forbid: bool = False,
              backward: bool = False,
              stratified: bool = False,
              **kwds) -> Iterable[PAIR]:
    """
    Get the grid graph.
    """
    cnf, pool = grid_model(num,
                           diag=diag,
                           lex=lex,
                           forbid=forbid,
                           backward=backward)
    soln = solve_maxsat(cnf, stratified=stratified, **kwds)
    return get_answer(soln, pool)
