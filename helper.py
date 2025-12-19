from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

def read_graph(filename):
    with open(filename, "r") as f:
        first_line = f.readline().strip().split()
        n = int(first_line[0])
        m = int(first_line[1])

        VG = [str(i) for i in range(1, n + 1)]
        EG = []

        for _ in range(m):
            line = f.readline().strip().split()
            u, v, _ = line[0], line[1], line[2]
            EG.append((u, v))

    return VG, EG


def is_connected(VG, selected_edges):
    if not VG:
        return True

    adj = {v: [] for v in VG}
    for (u, v) in selected_edges:
        adj[u].append(v)
        adj[v].append(u)

    visited = set()
    start = VG[0]
    queue = deque([start])
    visited.add(start)

    while queue:
        node = queue.popleft()
        for neigh in adj[node]:
            if neigh not in visited:
                visited.add(neigh)
                queue.append(neigh)

    return len(visited) == len(VG)


def count_branch_vertices(VG, T):
    degree = {v: 0 for v in VG}
    for (u, v) in T:
        degree[u] += 1
        degree[v] += 1

    branch_vertices = sum(1 for v in VG if degree[v] >= 3)
    return branch_vertices


def visualize_edges(VG, edges):

    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(edges)

    pos = nx.spring_layout(G, seed=42)  # layout for visualization
    plt.figure(figsize=(8,6))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=600)
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=2, edge_color='orange')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    plt.title("MBVST Solution Graph")
    plt.axis('off')
    plt.show()


def draw_graph_ax(ax, VG, edges, cycles=None, iteration=0, pos=None):

    G = nx.Graph()
    G.add_nodes_from(VG)
    G.add_edges_from(edges)

    if pos is None:
        pos = nx.spring_layout(G, seed=42)  # consistent layout

    ax.set_title(f"Iter {iteration + 1}")
    ax.axis('off')

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.5)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue', node_size=200)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)

    if cycles:
        for cycle in cycles:
            cycle_edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
            nx.draw_networkx_edges(G, pos, edgelist=cycle_edges, edge_color='red', width=2, ax=ax)

    return pos
