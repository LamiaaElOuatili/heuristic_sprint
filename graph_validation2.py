import networkx as nx
import matplotlib.pyplot as plt
import os

def load_instance(path):
    """
    Load a graph instance.
    File format:
    n m [ignored]
    u v [ignored]
    """
    G = nx.Graph()

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r") as f:
        header = f.readline().split()
        n = int(header[0])
        m = int(header[1])

        # Nodes: 0-based indexing
        G.add_nodes_from(range(n))

        for line in f:
            if not line.strip():
                continue

            parts = list(map(int, line.split()))
            u, v = parts[0], parts[1]

            # Convert to 0-based indexing
            G.add_edge(u - 1, v - 1)

    # Safety checks
    assert G.number_of_nodes() == n, "Node count mismatch"
    assert G.number_of_edges() == m, "Edge count mismatch"

    return G


def graph_info(G):
    degrees = dict(G.degree())

    return {
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "min_degree": min(degrees.values()),
        "max_degree": max(degrees.values())
    }


def count_branch_vertices(T):
    """
    Count branch vertices in a TREE.
    A branch vertex has degree > 2.
    """
    if not nx.is_tree(T):
        raise ValueError("count_branch_vertices expects a TREE")

    return sum(1 for v in T.nodes() if T.degree(v) > 2)


def draw_graph(G, title="Graph"):
    """
    Draw small graphs with FILE labels (1-based).
    """
    if G.number_of_nodes() > 100:
        print("Graph too large to draw.")
        return

    pos = nx.spring_layout(G, seed=42)

    # Display labels as in the file (1-based indexing)
    labels = {v: v + 1 for v in G.nodes()}

    nx.draw(
        G,
        pos,
        labels=labels,
        with_labels=True,
        node_size=500,
        font_size=10
    )
    plt.title(title)
    plt.show()

# Use raw string for Windows paths
#graph_path = r"Instances\Instances\Spd_Inst_Rid_Final2\Spd_RF2_20_27_211.txt"
#G = load_instance(graph_path)

#print("Number of nodes:", G.number_of_nodes())
#print("Number of edges:", G.number_of_edges())
#print("Connected:", nx.is_connected(G))

#info = graph_info(G)
#print("Graph info:", info)

#draw_graph(G, title="Original Graph")


