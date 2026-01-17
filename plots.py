import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("results.csv")

# Keep only rows where exact solution exists
df_valid = df.dropna(subset=["exact_branch_vertices"])

# Compute gap (%)
df_valid["gap"] = (
    (df_valid["heuristic_branch_vertices"] - df_valid["exact_branch_vertices"])
    / df_valid["exact_branch_vertices"]
) * 100

# Group by graph size
summary = df_valid.groupby(["n", "m"]).agg(
    instances=("instance", "count"),
    exact_avg=("exact_branch_vertices", "mean"),
    heuristic_avg=("heuristic_branch_vertices", "mean"),
    gap_avg=("gap", "mean"),
    exact_time_avg=("exact_time", "mean"),
    heuristic_time_avg=("heuristic_time", "mean"),
).reset_index()

print(summary)

plt.figure()
plt.plot(summary["n"], summary["exact_time_avg"], marker='o', label="Exact")
plt.plot(summary["n"], summary["heuristic_time_avg"], marker='s', label="Heuristic")

plt.xlabel("Number of vertices |V|")
plt.ylabel("Average runtime (seconds)")
plt.title("Runtime vs graph size")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(summary["n"], summary["exact_avg"], marker='o', label="Exact")
plt.plot(summary["n"], summary["heuristic_avg"], marker='s', label="Heuristic")

plt.xlabel("Number of vertices |V|")
plt.ylabel("Average number of branching vertices")
plt.title("Solution quality vs graph size")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
