"""K4 drawn with a crossing and as a plane realisation with its four faces (lecture 11)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2))

# the square drawing: the diagonals cross, so it is not a realisation
sq = {1: (0, 0), 2: (2.4, 0), 3: (2.4, 2.4), 4: (0, 2.4)}
sq_edges = [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3), (2, 4)]
dmfig.draw_graph(ax1, sq, sq_edges, node_size=0.2, label_size=14,
                 edge_colors={(1, 3): dmfig.HIGHLIGHT, (2, 4): dmfig.HIGHLIGHT})
ax1.plot([1.2], [1.2], "o", color=dmfig.HIGHLIGHT, ms=7, zorder=4, markerfacecolor="none")
ax1.set_title("рёбра $(1,3)$ и $(2,4)$ пересекаются", color=dmfig.INK, fontsize=11)
ax1.set_xlim(-0.6, 3.0)
ax1.set_ylim(-0.6, 3.0)

# the plane realisation: vertex 4 inside the triangle 1-2-3
pl = {1: (0, 0), 2: (3.0, 0), 3: (1.5, 2.6), 4: (1.5, 0.95)}
pl_edges = [(1, 2), (2, 3), (3, 1), (1, 4), (2, 4), (3, 4)]
faces = [([1, 2, 4], (1.5, 0.32), dmfig.COLOURS[0], "I"),
         ([2, 3, 4], (2.15, 1.35), dmfig.COLOURS[1], "II"),
         ([3, 1, 4], (0.85, 1.35), dmfig.COLOURS[2], "III")]
for vs, (cx, cy), col, name in faces:
    ax2.add_patch(Polygon([pl[v] for v in vs], closed=True, facecolor=col, alpha=0.35, edgecolor="none", zorder=0))
    ax2.text(cx, cy, name, ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=5)
dmfig.draw_graph(ax2, pl, pl_edges, node_size=0.17, label_size=13)
ax2.text(-0.55, 2.55, "IV: внешняя грань\n(вся плоскость\nвне треугольника)", ha="center", va="center", fontsize=11, color=dmfig.INK)
ax2.set_title("плоская реализация: $p=4$, $q=6$, $r=4$", color=dmfig.INK, fontsize=11)
ax2.set_xlim(-1.3, 3.6)
ax2.set_ylim(-0.6, 3.0)
fig.text(0.5, 0.0, "арабские цифры в кружках — вершины; римские — грани реализации", ha="center", fontsize=9.5,
         color=dmfig.INK)
dmfig.save(fig, 4, "planar-k4")
