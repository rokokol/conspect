"""K5 and K3,3 with the usual drawings; every crossing of the drawing is marked (lecture 11)."""
import itertools
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402


def crossings(pos, edges):
    """Interior intersection points of pairs of edges that share no end."""
    pts = []
    for (a, b), (c, d) in itertools.combinations(edges, 2):
        if {a, b} & {c, d}:
            continue
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = pos[a], pos[b], pos[c], pos[d]
        den = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
        if abs(den) < 1e-12:
            continue
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / den
        s = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / den
        if 0 < t < 1 and 0 < s < 1:
            pts.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    return pts


pos5 = {i: (math.cos(math.pi / 2 + 2 * math.pi * i / 5), math.sin(math.pi / 2 + 2 * math.pi * i / 5)) for i in range(5)}
edges5 = list(itertools.combinations(range(5), 2))
# the hexagon: the parts are the vertices 0, 2, 4 and 1, 3, 5 (alternating); sides plus three long diagonals
pos33 = {i: (math.cos(math.pi / 2 + math.pi * i / 3), math.sin(math.pi / 2 + math.pi * i / 3)) for i in range(6)}
edges33 = [(u, v) for u in (0, 2, 4) for v in (1, 3, 5)]
assert len(edges5) == 10 and len(edges33) == 9

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 4.4))
neutral = dmfig.tint(dmfig.MUTED, 0.75)  # K5 has no parts, so its vertices carry no part colour
dmfig.draw_graph(ax1, pos5, edges5, labels={i: str(i + 1) for i in pos5}, fills={i: neutral for i in pos5},
                 node_size=0.11, label_size=12)
ax1.set_title("$K_5$: $p=5$, $q=10$", color=dmfig.INK, fontsize=12)

fills = {i: dmfig.COLOURS[i % 2] for i in pos33}
dmfig.draw_graph(ax2, pos33, edges33, labels={i: str(i + 1) for i in pos33}, fills=fills, node_size=0.11,
                 label_size=12)
ax2.set_title("$K_{3,3}$: $p=6$, $q=9$", color=dmfig.INK, fontsize=12)

for ax, pos, edges in ((ax1, pos5, edges5), (ax2, pos33, edges33)):
    cr = sorted({(round(x, 6), round(y, 6)) for x, y in crossings(pos, edges)})  # one mark per point
    ax.plot(*zip(*cr), "o", color=dmfig.HIGHLIGHT, ms=8, markerfacecolor="none", markeredgewidth=2, zorder=4)
    print(len(cr), "crossing points")
cross_key = Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=dmfig.HIGHLIGHT,
                   markeredgewidth=2, ms=9, label="пересечение рёбер")
ax1.legend(handles=[cross_key], loc="lower center", bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=10,
           labelcolor=dmfig.INK)
ax2.legend(handles=[
    Line2D([0], [0], marker="o", color="none", markerfacecolor=dmfig.COLOURS[0], markeredgecolor=dmfig.VERTEX_EDGE,
           ms=10, label="первая доля"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor=dmfig.COLOURS[1], markeredgecolor=dmfig.VERTEX_EDGE,
           ms=10, label="вторая доля"),
    cross_key,
], loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=10, labelcolor=dmfig.INK)
ax1.set_xlim(-1.35, 1.35)
ax1.set_ylim(-1.3, 1.3)
ax2.set_xlim(-1.35, 1.35)
ax2.set_ylim(-1.3, 1.3)
dmfig.save(fig, 4, "k5-k33")
