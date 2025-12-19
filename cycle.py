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


def break_cycles(solution, cycle_basis, randomize=True):
    """
    Break cycles in the solution while ensuring the graph remains connected.

    Args:
        solution: dict with 'vertices' and 'selected_edges'
        cycle_basis: list of cycles (from nx.cycle_basis)
        randomize: whether to remove edges randomly or deterministically

    Returns:
        List of edges forming a cycle-free forest
    """
    VG = solution["vertices"]
    edges = set(solution["selected_edges"])  # use set for fast removal

    # Build a graph from the edges
    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(edges)

    for cycle in cycle_basis:
        # Convert cycle nodes to edges
        cycle_edges = []
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            if (u, v) in edges:
                cycle_edges.append((u, v))
            elif (v, u) in edges:
                cycle_edges.append((v, u))

        if not cycle_edges:
            continue

        # Try to remove an edge safely
        safe_edges = []
        for e in cycle_edges:
            G.remove_edge(*e)
            if nx.is_connected(G):
                safe_edges.append(e)
            G.add_edge(*e)  # put it back for next check

        if not safe_edges:
            # All edges are bridges; cannot remove any edge from this cycle
            continue

        # Select which safe edge to remove
        edge_to_remove = random.choice(safe_edges) if randomize else safe_edges[0]

        # Remove it from the graph
        if edge_to_remove in edges:
            edges.remove(edge_to_remove)
        elif (edge_to_remove[1], edge_to_remove[0]) in edges:
            edges.remove((edge_to_remove[1], edge_to_remove[0]))

        # Also update the graph for subsequent cycles
        G.remove_edge(*edge_to_remove)

    return list(edges)
