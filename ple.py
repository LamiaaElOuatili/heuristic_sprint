def mbvst_relaxed_PLNE(VG, EG):
    """
    Relaxed MILP formulation for the Minimum Branch Vertices
    Spanning Tree (MBVST).

    This model is intentionally RELAXED:
    - Connectivity is not enforced
    - Cycles are discouraged but not forced uniquely
    - Feasibility is guaranteed on connected graphs

    Final tree structure is enforced heuristically.
    """

    import gurobipy as gp
    from gurobipy import GRB
    import networkx as nx

    model = gp.Model("MBVST_relaxed")

    # --------------------------------------------------
    # Variables
    # --------------------------------------------------
    # x[e] = 1 if edge e is selected
    x = model.addVars(EG, vtype=GRB.BINARY, name="x")

    # y[v] = 1 if vertex v is a branch vertex
    y = model.addVars(VG, vtype=GRB.BINARY, name="y")

    # --------------------------------------------------
    # Objective: minimize branch vertices
    # --------------------------------------------------
    model.setObjective(
        gp.quicksum(y[v] for v in VG),
        GRB.MINIMIZE
    )

    # --------------------------------------------------
    # (1) Cardinality: spanning-tree size
    # --------------------------------------------------
    model.addConstr(
        gp.quicksum(x[e] for e in EG) == len(VG) - 1,
        name="cardinality"
    )

    # --------------------------------------------------
    # Build original graph
    # --------------------------------------------------
    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(EG)

    # --------------------------------------------------
    # (2) Mandatory bridges
    # --------------------------------------------------
    for (u, v) in nx.bridges(G):
        if (u, v) in EG:
            model.addConstr(x[(u, v)] == 1, name=f"bridge_{u}_{v}")
        elif (v, u) in EG:
            model.addConstr(x[(v, u)] == 1, name=f"bridge_{v}_{u}")

    # --------------------------------------------------
    # (3) RELAXED cycle constraints (FIX)
    #     At most |C| - 1 edges per cycle
    # --------------------------------------------------
    cycle_basis = nx.cycle_basis(G)

    for idx, cycle in enumerate(cycle_basis):
        cycle_edges = []
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]

            if (u, v) in EG:
                cycle_edges.append((u, v))
            elif (v, u) in EG:
                cycle_edges.append((v, u))

        if cycle_edges:
            model.addConstr(
                gp.quicksum(x[e] for e in cycle_edges)
                <= len(cycle_edges) - 1,
                name=f"cycle_{idx}"
            )

    # --------------------------------------------------
    # (4) Degree / branch linkage
    # --------------------------------------------------
    dG = {v: 0 for v in VG}
    for u, v in EG:
        dG[u] += 1
        dG[v] += 1

    for v in VG:
        incident_edges = [e for e in EG if v in e]
        model.addConstr(
            gp.quicksum(x[e] for e in incident_edges)
            <= 2 + dG[v] * y[v],
            name=f"branch_{v}"
        )

    return model, x, y
