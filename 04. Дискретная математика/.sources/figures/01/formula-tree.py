"""Tree of the formula (x | y) -> (not z + x): leaves are variables, inner nodes are functions of A."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(5.4, 3.6))

# node: (x, y, label, is_leaf)
nodes = {
    "root": (2.0, 3.0, r"$\to$", False),
    "sheffer": (0.9, 2.0, r"$\mid$", False),
    "xor": (3.1, 2.0, r"$\oplus$", False),
    "x1": (0.3, 1.0, r"$x$", True),
    "y": (1.5, 1.0, r"$y$", True),
    "not": (2.6, 1.0, r"$\neg$", False),
    "x2": (3.7, 1.0, r"$x$", True),
    "z": (2.6, 0.0, r"$z$", True),
}
edges = [("root", "sheffer"), ("root", "xor"), ("sheffer", "x1"), ("sheffer", "y"),
         ("xor", "not"), ("xor", "x2"), ("not", "z")]

for u, v in edges:
    ax.plot([nodes[u][0], nodes[v][0]], [nodes[u][1], nodes[v][1]],
            color=dmfig.EDGE, linewidth=2, zorder=1)
for x, y, label, leaf in nodes.values():
    if leaf:
        ax.add_patch(plt.Rectangle((x - 0.2, y - 0.2), 0.4, 0.4, facecolor=dmfig.tint(dmfig.P["natsuki"], 0.6),
                                   edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
    else:
        ax.add_patch(plt.Circle((x, y), 0.25, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE,
                                linewidth=1.6, zorder=2))
    ax.text(x, y, label, ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=3)

# key: leaf versus inner node, drawn with the same markers as the tree
ax.add_patch(plt.Rectangle((4.45, 2.55), 0.3, 0.3, facecolor=dmfig.tint(dmfig.P["natsuki"], 0.6),
                           edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(4.9, 2.7, "переменная", va="center", fontsize=10, color=dmfig.INK)
ax.add_patch(plt.Circle((4.6, 2.15), 0.17, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(4.9, 2.15, "функция из $A$", va="center", fontsize=10, color=dmfig.INK)

ax.set_xlim(-0.1, 6.6)
ax.set_ylim(-0.5, 3.5)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 1, "formula-tree")
