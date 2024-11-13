Minimal distance cover
======================

Let $S$ be a finite metric space with distance function $d$.  A subset
$C \subseteq S$ is a *distance cover* for $S$ if for all $x \ne y \in
S$ there are $a,b \in C$ such that $d(x,y) = d(a,b)$.  The *minimal
distance cover problem* is to find a distance cover of minimal
cardinality.

Our starting point is with the $n \times n$ integral grid with
the distance the standard Euclidean distance.

The general problem may be modeled via Max Sat.  We have indicator
variables $`x_a`$ for each $a \in S$, and variables $`p_{a,b}`$ for
each subset $\{a,b\} \subset S$ of cardinality 2.  We have clauses
$`p_{a,b} \Rightarrow x_a \wedge x_b`$ and clauses
$`\bigvee_{a,b, d(a,b) = d} p_{a,b}`$ for each realizable $d$
as hard constraints, and $`\overline{x_a}`$ of weight 1 as
soft constraints.

If $S$ has isometries, we can add symmetry breaking clauses.

More specifically, each metric space will be supplied with a list
of generators of a permutation group that leaves the distance
invariant.  We'll use the Schreier-Sims algorithm (courtesy
of sympy), to form a base and strong generating set for the induced
action of the permutation group on unordered pairs of points.

If the base is $`(b_1, \dots, b_m)`$ (where $`b_i`$ is an unordorded
pair) let $`G_i`$ for $i \ge 0$ denote the stabilizer of $`(b_1,
\dots, b_i)`$ (which is the whole group for $i=0$).  We then,
inductively consider the orbits of $`G_i`$.  We will choose one of
these orbits (probably one of maximum cardinality) and require that
the minimum member (under some convenient ordering) of that orbit be
present, and all of the others, not present.  I think that this is
what the Schreier Sims algorithms does.  So, inductively, we require
that $`b_i`$ be present and all of the other members of its orbits
under the action of $`G_i`$ not be present.
