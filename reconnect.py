import networkx as nx

def reconnect_component(forest_edges, VG, EG, dG):

    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(forest_edges)

    # Get connected components
    components = list(nx.connected_components(G))
    if len(components) <= 1:
        return forest_edges  # already connected

    # Pick the largest component as the main component
    main_comp = max(components, key=len)
    other_comps = [c for c in components if c != main_comp]

    new_edges = set(forest_edges)

    for comp in other_comps:
        # Find candidate edges connecting comp to main_comp
        candidates = [(u, v) for u in comp for v in main_comp if (u, v) in EG or (v, u) in EG]
        if not candidates:
            raise ValueError("No edge to reconnect component exists in EG")

        # Select the edge that minimizes branching vertices
        best_edge = None
        min_new_branches = float('inf')
        for u, v in candidates:
            # Compute degrees if this edge is added
            deg_u = sum(1 for e in new_edges if u in e) + 1
            deg_v = sum(1 for e in new_edges if v in e) + 1

            # Count new branching vertices (degree > 2)
            new_branches = (deg_u > 2) + (deg_v > 2)

            if new_branches < min_new_branches:
                min_new_branches = new_branches
                best_edge = (u, v)

        new_edges.add(best_edge)
        # Update the graph
        G.add_edge(*best_edge)

    return list(new_edges)

