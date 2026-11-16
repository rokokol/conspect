"""A connected graph on 6 vertices and one of its spanning trees (lemma 1 and the existence theorem)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

pos = {1: (0, 1.6), 2: (1.6, 2.4), 3: (3.2, 1.6), 4: (3.2, 0), 5: (1.6, -0.8), 6: (0, 0)}
edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (2, 5), (1, 3), (2, 6)]
# the order of throwing away: each removed edge lies on a cycle of the graph that is left at that moment
removed = [(1, 3), (2, 6), (3, 4), (6, 1)]
tree = [e for e in edges if e not in removed]
p, q = len(pos), len(edges)
assert q - len(removed) == p - 1

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.9))
dmfig.draw_graph(ax1, pos, edges, node_size=0.2, label_size=14)
ax1.set_title(f"граф: $p={p}$, $q={q}$", color=dmfig.INK, fontsize=12)

styles = {e: "--" for e in removed}
colours = {e: dmfig.MUTED for e in removed}
colours.update({e: dmfig.HIGHLIGHT for e in tree})
dmfig.draw_graph(ax2, pos, edges, edge_colors=colours, edge_styles=styles, node_size=0.2, label_size=14)
ax2.set_title(f"остовное дерево: $q={len(tree)}=p-1$", color=dmfig.INK, fontsize=12)

ax2.legend(handles=[
    Line2D([0], [0], color=dmfig.HIGHLIGHT, lw=2, label="рёбра остова"),
    Line2D([0], [0], color=dmfig.MUTED, lw=2, ls="--", label="выброшенные рёбра"),
], loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=10,
    labelcolor=dmfig.INK)
for ax in (ax1, ax2):
    ax.set_xlim(-0.6, 3.8)
    ax.set_ylim(-1.2, 2.8)
dmfig.save(fig, 4, "spanning-tree")
