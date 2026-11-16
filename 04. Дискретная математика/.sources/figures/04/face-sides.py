"""The graph of lecture 12, fig. 12.3: a 4-cycle, a triangle inside it and a bridge; faces with 3, 4 and 9 sides."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
from matplotlib.patches import PathPatch, Polygon  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

pos = {1: (0, 2.2), 2: (2.2, 4.4), 3: (4.4, 2.2), 4: (2.2, 0),   # outer 4-cycle
       5: (1.7, 3.0), 6: (2.7, 3.0), 7: (2.2, 2.1)}              # triangle with the bridge (7, 4)
edges = [(1, 2), (2, 3), (3, 4), (4, 1), (5, 6), (6, 7), (7, 5), (7, 4)]

# the count of the lecture: walk along each face boundary and count edge passages
g = nx.Graph(edges)
is_planar, emb = nx.check_planarity(g)
assert is_planar
seen, faces = set(), []
for u, v in emb.edges():
    if (u, v) in seen:
        continue
    face = emb.traverse_face(u, v, mark_half_edges=seen)
    faces.append(face)
sides = sorted(len(f) for f in faces)
p, q = g.number_of_nodes(), g.number_of_edges()
print("p", p, "q", q, "sides", sides)
assert sides == [3, 4, 9] and sum(sides) == 2 * q == 16 and p - q + len(faces) == 2

fig, ax = plt.subplots(figsize=(5.4, 4.8))
# the middle face is the square with the triangle cut out: a compound path with a hole
square = [pos[v] for v in (1, 4, 3, 2)]
hole = [pos[v] for v in (5, 6, 7)]
verts = square + [square[0]] + hole + [hole[0]]
codes = [MPath.MOVETO] + [MPath.LINETO] * 3 + [MPath.CLOSEPOLY] + [MPath.MOVETO] + [MPath.LINETO] * 2 + [MPath.CLOSEPOLY]
ax.add_patch(PathPatch(MPath(verts, codes), facecolor=dmfig.COLOURS[1], alpha=0.3, edgecolor="none", zorder=0))
ax.add_patch(Polygon(hole, closed=True, facecolor=dmfig.COLOURS[0], alpha=0.45, edgecolor="none", zorder=0))
dmfig.draw_graph(ax, pos, edges, labels={v: str(v) for v in pos}, node_size=0.17, label_size=12,
                 edge_colors={(7, 4): dmfig.HIGHLIGHT})
ax.text(2.2, 2.62, "3", ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=5)
ax.text(3.5, 2.2, "9", ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=5)
ax.text(4.3, 0.75, "4", ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=5)
ax.text(4.3, 0.3, "внешняя\nгрань", ha="center", va="center", fontsize=10, color=dmfig.INK)
ax.set_xlim(-0.6, 5.2)
ax.set_ylim(-0.6, 4.9)
ax.set_title("числа в гранях — их стороны; ребро $(7,4)$ считается дважды", color=dmfig.INK, fontsize=10.5)
dmfig.save(fig, 4, "face-sides")
