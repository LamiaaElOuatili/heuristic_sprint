import time
import networkx as nx

from ple import mbvst_relaxed_PLNE
from reconnect import reconnect_component
from cycle import break_cycles_intelligently
from helper import visualize_edges


# ============================================================
# Fallback solution
# ============================================================

def fallback_spanning_tree(VG, EG):
    """
    Always returns a valid spanning tree using BFS.
    Used only if the heuristic fails completely.
    """
    print("[FALLBACK] Building BFS spanning tree (no optimization).")

    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(EG)

    if not nx.is_connected(G):
        raise ValueError("[FALLBACK ERROR] Original graph is not connected.")

    T = nx.bfs_tree(G, source=VG[0])
    edges = list(T.edges())

    branch_vertices = sum(1 for v in VG if T.degree(v) >= 3)
    print(f"[FALLBACK] Branch vertices: {branch_vertices}")

    return edges, branch_vertices


# ============================================================
# Main heuristic
# ============================================================

def heuristic_cycle_basis(VG, EG, max_iter=50, max_components=5):
    """
    Heuristic solver for the Minimum Branch Vertices Spanning Tree (MBVST).

    Steps per iteration:
      1) Solve relaxed MILP (acyclicity relaxed)
      2) Discard overly fragmented solutions
      3) Reconnect components
      4) Break remaining cycles heuristically
      5) Evaluate number of branch vertices
      6) Keep the best solution found
    """

    print("[INFO] Starting MBVST heuristic")
    start_time = time.time()

    # --------------------------------------------------
    # Precompute original degrees
    # --------------------------------------------------
    dG = {v: 0 for v in VG}
    for u, v in EG:
        dG[u] += 1
        dG[v] += 1

    best_solution = None
    best_obj = float("inf")
    first_solution_edges = None

    # ==================================================
    # Main loop
    # ==================================================
    for it in range(max_iter):
        print(f"\n[ITERATION {it + 1}]")

        # --------------------------------------------------
        # 1) Solve relaxed MILP
        # --------------------------------------------------
        try:
            model, x_vars, y_vars = mbvst_relaxed_PLNE(VG, EG)
            model.optimize()
        except Exception as e:
            print(f"[ERROR] MILP solver crashed: {e}")
            continue

        if model.SolCount == 0:
            print("[WARNING] MILP returned no feasible solution.")
            continue

        selected_edges = [e for e in EG if x_vars[e].X > 0.5]
        print(f"[INFO] MILP selected {len(selected_edges)} edges")

        # --------------------------------------------------
        # 2) Build solution graph
        # --------------------------------------------------
        G = nx.Graph()
        G.add_nodes_from(VG)
        G.add_edges_from(selected_edges)

        # --------------------------------------------------
        # 3) Fragmentation check
        # --------------------------------------------------
        nb_components = nx.number_connected_components(G)
        if nb_components > max_components:
            print(
                f"[WARNING] Too many connected components "
                f"({nb_components} > {max_components}). Iteration skipped."
            )
            continue

        # --------------------------------------------------
        # 4) Reconnect components
        # --------------------------------------------------
        try:
            selected_edges = reconnect_component(
                selected_edges, VG, EG, dG
            )
        except ValueError as e:
            print(f"[ERROR] Reconnection failed: {e}")
            continue

        G = nx.Graph()
        G.add_nodes_from(VG)
        G.add_edges_from(selected_edges)

        if not nx.is_connected(G):
            print("[ERROR] Graph still disconnected after reconnection.")
            continue

        # --------------------------------------------------
        # 5) Break cycles
        # --------------------------------------------------
        try:
            removed_edges = break_cycles_intelligently(G)
            print(f"[INFO] Removed {len(removed_edges)} cycle edges")
        except Exception as e:
            print(f"[ERROR] Cycle breaking failed: {e}")
            continue

        final_edges = list(G.edges())

        # Save first valid solution for visualization
        if first_solution_edges is None:
            first_solution_edges = final_edges

        # --------------------------------------------------
        # 6) Evaluate solution
        # --------------------------------------------------
        branch_vertices = sum(1 for v in VG if G.degree(v) >= 3)
        print(f"[INFO] Branch vertices: {branch_vertices}")

        # --------------------------------------------------
        # 7) Update best solution
        # --------------------------------------------------
        if branch_vertices < best_obj:
            best_obj = branch_vertices
            best_solution = final_edges
            print("[SUCCESS] New best solution found")

    # ==================================================
    # Final safety check
    # ==================================================
    if best_solution is None:
        print("[WARNING] No valid solution found in all iterations.")
        best_solution, best_obj = fallback_spanning_tree(VG, EG)

    elapsed = time.time() - start_time
    print("\n[INFO] Heuristic finished")
    print(f"[INFO] Total runtime: {elapsed:.3f} seconds")
    print(f"[RESULT] Best number of branch vertices: {best_obj}")

    # ==================================================
    # Visualizations
    # ==================================================
    if first_solution_edges is not None:
        print("[VISUAL] First valid solution")
        visualize_edges(VG, first_solution_edges)

    print("[VISUAL] Best final solution")
    visualize_edges(VG, best_solution)

    return best_solution, best_obj


