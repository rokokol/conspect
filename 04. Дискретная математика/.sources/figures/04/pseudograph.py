"""The lecturer's pseudograph on 7 vertices (board drawing, L08 1:16): a loop at 1, a double edge 3-4, an isolated vertex 7."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

pos = {1: (0, 2), 3: (2, 2), 2: (0, 0), 4: (2, 0), 5: (3.6, 2), 6: (3.6, 0), 7: (5, 1)}
# edge 3-4 is listed twice and drawn as two arcs
edges = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 4), (5, 6)]
curved = {(3, 4): 0.25}

fig, ax = plt.subplots(figsize=(6.2, 3.6))
simple = [e for e in edges if e != (3, 4)]
# the loop at vertex 1 goes under the vertex disc
ax.add_patch(Circle((-0.3, 2.3), 0.42, fill=False, edgecolor=dmfig.EDGE, linewidth=2, zorder=1))
# the two parallel edges: (3, 4) and (4, 3) with the same rad bend to opposite sides
dmfig.draw_graph(ax, pos, simple + [(3, 4), (4, 3)], curved={(3, 4): 0.25, (4, 3): 0.25},
                 node_size=0.2, label_size=14)

degrees = {1: 4, 2: 3, 3: 4, 4: 3, 5: 1, 6: 1, 7: 0}
offsets = {1: (0.38, 0.38), 2: (-0.38, -0.38), 3: (0.38, 0.38), 4: (0.38, -0.38),
           5: (0.38, 0.38), 6: (0.38, -0.38), 7: (0.0, 0.42)}
for v, d in degrees.items():
    x, y = pos[v]
    dx, dy = offsets[v]
    ax.text(x + dx, y + dy, f"{d}", ha="center", va="center", fontsize=11, color=dmfig.HIGHLIGHT)

ax.text(2.5, -0.95, r"красные числа у вершин — степени $\deg v$", ha="center",
        fontsize=10, color=dmfig.INK)
ax.set_xlim(-1.2, 5.6)
ax.set_ylim(-1.2, 3.0)
dmfig.save(fig, 4, "pseudograph")
