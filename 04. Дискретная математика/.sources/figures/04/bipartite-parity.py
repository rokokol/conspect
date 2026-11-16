"""Two-colouring by the parity of path length from a root, one root per component (lecture 13)."""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

C = dmfig.COLOURS

pos = {"a": (0, 1), "b": (1.2, 1.9), "c": (2.6, 1.9), "d": (3.8, 1), "e": (2.6, 0.1), "f": (1.2, 0.1),
       "g": (3.2, 3.1), "h": (5.2, 1.9), "i": (6.4, 1.9)}
edges = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("f", "a"), ("b", "e"), ("c", "g"),
         ("h", "i")]
roots = ["a", "h"]

adj = {v: [] for v in pos}
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)
length = {}
for r in roots:
    length[r] = 0
    queue = deque([r])
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if w not in length:
                length[w] = length[u] + 1
                queue.append(w)
# every path from the root has the parity of the shortest one: check on the edges
assert all(length[u] % 2 != length[v] % 2 for u, v in edges)
assert set(length) == set(pos)

fills = {v: C[0] if length[v] % 2 == 0 else C[1] for v in pos}
fig, ax = plt.subplots(figsize=(9.6, 3.9))
dmfig.draw_graph(ax, pos, edges, labels={v: str(length[v]) for v in pos}, fills=fills, node_size=0.22,
                 label_size=13)
for r in roots:
    x, y = pos[r]
    ax.text(x - 0.05, y - 0.5, "$v_0$", ha="center", fontsize=12, color=dmfig.INK)
handles = [Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor=C[0],
                  markeredgecolor=dmfig.VERTEX_EDGE, label="чётная длина путей из $v_0$: $c_1$"),
           Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor=C[1],
                  markeredgecolor=dmfig.VERTEX_EDGE, label="нечётная длина: $c_2$")]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False,
          fontsize=11, labelcolor=dmfig.INK)
fig.text(0.5, 0.97, "число в вершине — длина одного пути из $v_0$ своей компоненты", ha="center", fontsize=10,
         color=dmfig.INK)
dmfig.save(fig, 4, "bipartite-parity")
