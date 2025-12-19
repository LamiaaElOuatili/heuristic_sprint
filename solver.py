import cplex
import time
from helper import *

def solve_mbvst_lp(filename):
    start_time = time.time()

    cpx = cplex.Cplex(filename)
    cpx.solve()

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Status:", cpx.solution.get_status_string())
    print("Objective:", cpx.solution.get_objective_value())

    names = cpx.variables.get_names()
    values = cpx.solution.get_values()

    selected_edges = []
    VG = set()

    for name, val in zip(names, values):
        if name.startswith("x") and abs(val - 1) < 1e-6:
            inside = name[name.index("(")+1 : name.index(")")]
            u, v = inside.replace("'", "").split(",")
            u, v = u.strip(), v.strip()

            # Normalize vertex names: Remove underscores if any
            u = u.lstrip('_')
            v = v.lstrip('_')

            selected_edges.append((u, v))
            VG.add(u)
            VG.add(v)

    print("\nSelected edges from CPLEX:")
    print(selected_edges)

    VG = sorted(list(VG))
    connected = is_connected(VG, selected_edges)

    print("\nIs the graph connected?  ->", connected)
    print("Execution time (seconds):", elapsed_time)

    return {
        "selected_edges": selected_edges,
        "vertices": VG,
        "connected": connected,
        "objective": cpx.solution.get_objective_value(),
        "status": cpx.solution.get_status_string(),
        "execution_time": elapsed_time
    }


