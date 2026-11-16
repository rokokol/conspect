"""The lecturer's isomorphism example (fig. 9.1): the map 1->b, 2->a, 3->d, 4->c is checked edge by edge."""
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

phi = {1: "b", 2: "a", 3: "d", 4: "c"}
e1 = [(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)]
e2 = [("a", "b"), ("b", "d"), ("d", "c"), ("c", "a"), ("a", "d")]
g1, g2 = nx.Graph(e1), nx.Graph(e2)
assert all(g2.has_edge(phi[u], phi[v]) for u, v in e1) and len(e1) == len(e2)
assert nx.is_isomorphic(g1, g2)

pos1 = {1: (0, 2), 2: (2, 2), 3: (0, 0), 4: (2, 0)}
pos2 = {"a": (4.5, 2), "b": (6.5, 2), "c": (4.5, 0), "d": (6.5, 0)}
colour = {1: dmfig.COLOURS[0], 2: dmfig.COLOURS[1], 3: dmfig.COLOURS[2], 4: dmfig.COLOURS[4]}
fills = {**colour, **{phi[v]: c for v, c in colour.items()}}

fig, ax = plt.subplots(figsize=(6.4, 3.4))
dmfig.draw_graph(ax, {**pos1, **pos2}, e1 + e2, fills=fills, node_size=0.2, label_size=14)
ax.text(1, 2.7, r"$G_1$", ha="center", fontsize=13, color=dmfig.INK)
ax.text(5.5, 2.7, r"$G_2$", ha="center", fontsize=13, color=dmfig.INK)
ax.text(3.25, -0.95, r"одинаковый цвет — вершины, которые $\varphi$ переводит друг в друга",
        ha="center", fontsize=10, color=dmfig.INK)
ax.set_xlim(-1.0, 7.5)
ax.set_ylim(-1.3, 3.2)
dmfig.save(fig, 4, "isomorphism")
