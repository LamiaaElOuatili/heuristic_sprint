import os
import csv
import time
import re
import networkx as nx

from graph_validation2 import load_instance
from heuristic import heuristic_cycle_basis
from plne_cp2 import solve_mbvst_flow


# ============================================================
# Configuration
# ============================================================

INSTANCE_FOLDER = "Spd_Inst_Rid_Final2"
OUTPUT_CSV = "results.csv"

TIME_LIMIT_EXACT = 60       # seconds for CPLEX
MAX_INSTANCES_PER_SIZE = 5
MIN_N = 20
MAX_N = 500


# ============================================================
# Utility
# ============================================================

def count_branch_vertices_tree(T):
    return sum(1 for v in T.nodes() if T.degree(v) > 2)


def extract_n_from_filename(filename):
    """
    Extract number of nodes from filename:
    Example: Spd_RF2_200_222_3811.txt → 200
    """
    match = re.search(r"_([0-9]+)_", filename)
    if match:
        return int(match.group(1))
    return None


# ============================================================
# Main batch runner
# ============================================================

def main():

    # --------------------------------------------------
    # Collect instances grouped by size
    # --------------------------------------------------
    files_by_size = {}

    for fname in sorted(os.listdir(INSTANCE_FOLDER)):
        if not fname.endswith(".txt"):
            continue

        n = extract_n_from_filename(fname)
        if n is None or not (MIN_N <= n <= MAX_N):
            continue

        files_by_size.setdefault(n, []).append(fname)

    if not files_by_size:
        raise RuntimeError("[ERROR] No valid instances found.")

    # --------------------------------------------------
    # Prepare CSV (incremental write)
    # --------------------------------------------------
    fieldnames = [
        "instance", "n", "m",
        "exact_status", "exact_time", "exact_branch_vertices",
        "heuristic_time", "heuristic_branch_vertices"
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        f.flush()

        # --------------------------------------------------
        # Process instances
        # --------------------------------------------------
        for n in sorted(files_by_size.keys()):
            selected_files = files_by_size[n][:MAX_INSTANCES_PER_SIZE]

            print("\n=================================================")
            print(f"[SIZE n={n}] Processing {len(selected_files)} instances")

            for fname in selected_files:
                path = os.path.join(INSTANCE_FOLDER, fname)
                print(f"\n[INSTANCE] {fname}")

                # ------------------------------------------
                # Load instance
                # ------------------------------------------
                try:
                    G = load_instance(path)
                except Exception as e:
                    print(f"[ERROR] Load failed: {e}")
                    continue

                m = G.number_of_edges()
                print(f"[INFO] n={n}, m={m}")

                # ------------------------------------------
                # Exact PLNE
                # ------------------------------------------
                try:
                    T_opt, status, exact_time = solve_mbvst_flow(
                        G, time_limit=TIME_LIMIT_EXACT
                    )

                    if status == "Optimal" and nx.is_tree(T_opt):
                        exact_obj = count_branch_vertices_tree(T_opt)
                    else:
                        exact_obj = None

                except Exception as e:
                    print(f"[ERROR] Exact solver failed: {e}")
                    status = "ERROR"
                    exact_time = None
                    exact_obj = None

                # ------------------------------------------
                # Heuristic
                # ------------------------------------------
                try:
                    VG = list(G.nodes())
                    EG = list(G.edges())

                    start = time.time()
                    _, heur_obj = heuristic_cycle_basis(VG, EG)
                    heuristic_time = time.time() - start

                except Exception as e:
                    print(f"[ERROR] Heuristic failed: {e}")
                    heuristic_time = None
                    heur_obj = None

                # ------------------------------------------
                # Write CSV row immediately
                # ------------------------------------------
                writer.writerow({
                    "instance": fname,
                    "n": n,
                    "m": m,
                    "exact_status": status,
                    "exact_time": exact_time,
                    "exact_branch_vertices": exact_obj,
                    "heuristic_time": heuristic_time,
                    "heuristic_branch_vertices": heur_obj
                })
                f.flush()   # 🔥 CRITICAL: save immediately

                print("[SAVED] Result written to CSV")

    print("\n=================================================")
    print(f"[DONE] Incremental results saved in {OUTPUT_CSV}")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()
