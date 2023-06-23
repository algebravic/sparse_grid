"""
Construct a graph whose automorphism group gives
the syntatical automorphisms of a cnf
"""

from typing import List, Tuple, Iterable
from itertools import chain
import networkx as nx

CLAUSE = List[int]
FORMULA = List[CLAUSE]

def lit_id(lit: int) -> str:
    """ literal id """
    return ('p' if lit > 0 else 'n') + str(abs(lit))

def bliss_graph(clauses: FORMULA) -> nx.Graph:
    """
    Produce a colored graph from a cnf formula.

    The vertices are
    1) Clauses of length > 2.
    2) literals.
    
    Each one of the above is colored by the above ordinals.

    Edges: Each clause has an edge connecting its literals.
    Each 2-clause has an edge connecting its two literals.
    For each variable there is an edge connecting its
    two literals.
    """

    gph=nx.Graph()
    support = set(chain(*(map(abs,_) for _ in clauses)))
    for variable in support:
        gph.add_node(lit_id(variable), color=2)
        gph.add_node(lit_id(-variable), color=2)
        gph.add_edge(lit_id(variable), lit_id(-variable))

    for ind, clause in enumerate(clauses, start=1):
        if len(clause) == 2:
            gph.add_edge(lit_id(clause[0]), lit_id(clause[1]))
        else:
            cid = f'c{ind}'
            gph.add_node(cid,color=1)
            for lit in clause: 
                gph.add_edge(cid, lit_id(lit))
    
def dimacs_graph(clauses: FORMULA,
                 comments=List[str]) -> Iterable[str]:
    """
    Yield the lines of an extended DIMACS graph
    associated to a CNF formula.

    The number of edges is 2V + #Cx
    where Cx is the number clauses of length > 2
    """
    def lit_ind(lit: int) -> int:
        """ Index of literal """
        return 2 * abs(lit) - int(lit > 0)
    yield from ('c ' + _ for _ in comments)
    big = [_ for _ in clauses if len(_) > 2]
    small = [_ for _ in clauses if len(_) == 2]
    support = set(chain(*(map(abs,_) for _ in clauses)))
    edge1 = sum(map(len, big))
    edge2 = len(small)
    edge3 = len(support)
    edges = edge1 + edge2 + edge3
    nvars = len(support)
    base = 2 * nvars + 1
    yield f'p edge {2 * len(support) + len(big)} {edges}'
    # default color for a vertex is 0
    # yield from (f'n {2 * _ + 1} 1' for _ in range(nvars))
    # yield from (f'n {2 * _ + 2} 1' for _ in range(nvars))
    yield from (f'n {base + _} 1' for _ in range(len(big)))
    # Now for the edges
    yield from (f'e {2 * _ + 1} {2 * _ + 2}'
                for _ in range(nvars))
    yield from (f'e {lit_ind(_[0])} {lit_ind(_[1])}'
                for _ in small)
    for ind, clause in enumerate(big):
        yield from (f'e {base + ind} {lit_ind(_)}'
                    for _ in clause)
def write_dimacs(clauses: FORMULA,
                 name: str,
                 comments:List[str]=[]):
    """
    Write an extended DIMACS graph for a formula.
    """
    with open(name, 'w', encoding='utf8') as fil:
        fil.write('\n'.join(dimacs_graph(clauses,
                                         comments=comments)))
        fil.write('\n')
