import networkx as nx
import random

def get_cycle_bases(solution):
    VG = solution["vertices"]
    edges = solution["selected_edges"]

    # Build graph from solution
    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(edges)

    # Compute cycle basis
    cycle_basis = nx.cycle_basis(G)

    return cycle_basis


def break_cycles_intelligently(G):
    cycles = nx.cycle_basis(G)
    removed_edges = []

    for cycle in cycles:
        cycle_edges = [
            (cycle[i], cycle[(i+1) % len(cycle)])
            for i in range(len(cycle))
        ]

        # heuristique : enlever l’arête la plus "branchante"
        edge_to_remove = max(
            cycle_edges,
            key=lambda e: G.degree(e[0]) + G.degree(e[1])
        )

        if G.has_edge(*edge_to_remove):
            G.remove_edge(*edge_to_remove)
            removed_edges.append(edge_to_remove)

    return removed_edges
