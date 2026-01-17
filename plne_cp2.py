import pulp
import networkx as nx
import graph_validation2
import helper
import time

def solve_mbvst_flow(G, time_limit=60):

    n = G.number_of_nodes()
    nodes = list(G.nodes())
    root = nodes[0]

    # Build directed arc set
    arcs = []
    for u, v in G.edges():
        arcs.append((u, v))
        arcs.append((v, u))

    A_plus = {v: [] for v in nodes}
    A_minus = {v: [] for v in nodes}

    for (u, v) in arcs:
        A_plus[u].append((u, v))
        A_minus[v].append((u, v))

    deg_G = dict(G.degree())

    prob = pulp.LpProblem("MBVST_Flow", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", arcs, cat="Binary")
    f = pulp.LpVariable.dicts("f", arcs, lowBound=0)
    y = pulp.LpVariable.dicts("y", nodes, cat="Binary")

    # Objective
    prob += pulp.lpSum(y[v] for v in nodes)

    # Incoming arc constraints
    for v in nodes:
        if v != root:
            prob += pulp.lpSum(x[a] for a in A_minus[v]) == 1

    # Root has no incoming arc
    prob += pulp.lpSum(x[a] for a in A_minus[root]) == 0

    # Anti-parallel constraint
    for u, v in G.edges():
        prob += x[(u, v)] + x[(v, u)] <= 1

    # Flow constraints
    prob += (
        pulp.lpSum(f[a] for a in A_plus[root])
        - pulp.lpSum(f[a] for a in A_minus[root])
        == n - 1
    )

    for v in nodes:
        if v != root:
            prob += (
                pulp.lpSum(f[a] for a in A_plus[v])
                - pulp.lpSum(f[a] for a in A_minus[v])
                == -1
            )

    # Flow-edge coupling
    for (u, v) in arcs:
        prob += f[(u, v)] <= (n - 1) * x[(u, v)]

    # Branch vertex definition
    for v in nodes:
        prob += (
            pulp.lpSum(x[a] for a in A_plus[v])
            + pulp.lpSum(x[a] for a in A_minus[v])
            - 2
            <= deg_G[v] * y[v]
        )

    solver = pulp.CPLEX_CMD(timeLimit=time_limit, msg=True)

    start_time = time.time()
    status = prob.solve(solver)
    end_time = time.time()

    runtime = end_time - start_time

    T = nx.Graph()
    T.add_nodes_from(nodes)

    for (u, v) in arcs:
        if pulp.value(x[(u, v)]) == 1:
            if not T.has_edge(u, v):
                T.add_edge(u, v)

    return T, pulp.LpStatus[status], runtime


#graph_path = r"Instances\Instances\Spd_Inst_Rid_Final2\Spd_RF2_500_672_5203.txt"
#G = graph_validation.load_instance(graph_path)
#T_opt, status, runtime = solve_mbvst_flow(G)

#print("Solver status:", status)
#print("Runtime (s):", round(runtime, 3))
#print("Is tree:", nx.is_tree(T_opt))
#print("Branch vertices:",
#      sum(1 for v in T_opt.nodes() if T_opt.degree(v) > 2))

#helper.draw_solution(G, T_opt, title="Optimal MBVST on Original Graph")

