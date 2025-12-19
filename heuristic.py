import random
from ple import *
from solver import *
from reconnect import *

import matplotlib.pyplot as plt
import networkx as nx
import random

def iterative_mbvst_with_lp_file(VG, EG, max_iter=30, randomize=True):

    # Degree dictionary
    dG = {v: 0 for v in VG}
    for u, v in EG:
        dG[u] += 1
        dG[v] += 1

    candidate_edges = EG.copy()
    graphs_per_iteration = []  # store edges + cycles for plotting
    pos = None  # to keep consistent layout

    for iteration in range(max_iter):
        print(f"Iteration {iteration + 1}")

        model, x_vars, y_vars = mbvst_original_PLE_lazy(VG, candidate_edges)
        model.writeLP("MBVST_Original.lp")
        solution = solve_mbvst_lp("MBVST_Original.lp")
        selected_edges = solution["selected_edges"]

        G_sol = nx.Graph()
        G_sol.add_nodes_from(VG)
        G_sol.add_edges_from(selected_edges)

        if nx.is_connected(G_sol):
            print("Graph is connected! Done.")
            graphs_per_iteration.append((selected_edges.copy(), []))
            solution["iterations"] = iteration + 1
            break

        try:
            connected_edges = reconnect_component(selected_edges, VG, EG, dG)
        except ValueError:
            print("Reconnection impossible — stopping heuristic.")
            graphs_per_iteration.append((selected_edges.copy(), []))
            solution["iterations"] = iteration + 1
            break

        G_conn = nx.Graph()
        G_conn.add_nodes_from(VG)
        G_conn.add_edges_from(connected_edges)

        cycles = nx.cycle_basis(G_conn)
        forest_edges = connected_edges.copy()
        graphs_per_iteration.append((connected_edges.copy(), cycles))

        for cycle in cycles:
            cycle_edges = [
                (cycle[i], cycle[(i + 1) % len(cycle)])
                for i in range(len(cycle))
                if (cycle[i], cycle[(i + 1) % len(cycle)]) in forest_edges
                or (cycle[(i + 1) % len(cycle)], cycle[i]) in forest_edges
            ]

            if not cycle_edges:
                continue

            edge_to_remove = random.choice(cycle_edges) if randomize else cycle_edges[0]
            if edge_to_remove in forest_edges:
                forest_edges.remove(edge_to_remove)
            else:
                forest_edges.remove((edge_to_remove[1], edge_to_remove[0]))

        candidate_edges = forest_edges

    num_iters = len(graphs_per_iteration)
    cols = 3
    rows = (num_iters + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
    axes = axes.flatten()

    for i, (edges, cycles) in enumerate(graphs_per_iteration):
        pos = draw_graph_ax(axes[i], VG, edges, cycles, iteration=i+1, pos=pos)

    # Hide unused subplots
    for j in range(i+1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()

    solution["selected_edges"] = candidate_edges
    if "iterations" not in solution:
        solution["iterations"] = max_iter

    return candidate_edges, solution
