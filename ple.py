import pulp as pl
from itertools import combinations
from helper import *

import pulp as pl

def mbvst_original_PLE_lazy(VG, EG):

    # Compute degrees
    dG = {v: 0 for v in VG}
    for u, v in EG:
        dG[u] += 1
        dG[v] += 1

    # Create model
    model = pl.LpProblem("MBVST_Original_Lazy", pl.LpMinimize)

    # Variables
    x = pl.LpVariable.dicts("x", EG, 0, 1, pl.LpBinary)  # edges
    y = pl.LpVariable.dicts("y", VG, 0, 1, pl.LpBinary)  # branching vertices

    # Objective: minimize branching vertices
    model += pl.lpSum([y[v] for v in VG]), "MinBranchVertices"

    # Tree edge count
    model += pl.lpSum([x[e] for e in EG]) == len(VG) - 1, "TreeEdgeCount"

    # Branching constraints
    for v in VG:
        incident_edges = [e for e in EG if v in e]
        if incident_edges:
            model += pl.lpSum([x[e] for e in incident_edges]) - 2 <= dG[v] * y[v], f"BranchDef_{v}"

    return model, x, y





