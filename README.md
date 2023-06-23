Minimal distance cover
======================

Let $S$ be a finite metric space with distance function $d$.  A subset
$C \subseteq S$ is a *distance cover* for $S$ if for all $x \ne y \in
S$ there are $a,b \in C$ such that $d(x,y) = d(a,b)$.  The *minimal
distance cover problem* is to find a distance cover of minimal
cardinality.

Our starting point is with the $n \times n$ integral grid with
the distance the standard Euclidean distance.

The general problem may be modeled via Max Sat.  We have variables
$`x_a`$ for each $a \in S$, and variables $`p_{a,b}`$ for each subset
$\{a,b\} \subset S$ of cardinality 2.  We have clauses $`p_{a,b}
\Rightarrow a,b`$ and clauses $`\bigvee_{a,b, d(a,b) = d} p_{a,b}`$ as
hard constraints, and $`\overline{x_a}`$ of weight 1 as soft
constraints.

If $S$ has isometries, we can add symmetry breaking clauses.
