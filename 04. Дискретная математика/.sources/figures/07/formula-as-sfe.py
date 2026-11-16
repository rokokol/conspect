"""The formula (not(xy))(x or y) drawn as a rooted tree with arcs pointing from the leaves to the root: a special SFE."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
INPUT_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)

fig, ax = plt.subplots(figsize=(5.4, 4.6))

R = 0.3
nodes = {
    "root": (1.5, 3.0, r"$\wedge$", "out"),
    "not": (0.5, 2.0, r"$\neg$", "elem"),
    "or": (2.5, 2.0, r"$\vee$", "elem"),
    "and": (0.5, 1.0, r"$\wedge$", "elem"),
    "x1": (0.0, 0.0, r"$x$", "in"),
    "y1": (1.0, 0.0, r"$y$", "in"),
    "x2": (2.0, 0.0, r"$x$", "in"),
    "y2": (3.0, 0.0, r"$y$", "in"),
}
arcs = [("x1", "and"), ("y1", "and"), ("and", "not"), ("not", "root"),
        ("x2", "or"), ("y2", "or"), ("or", "root")]

patches = {}
for name, (x, y, label, kind) in nodes.items():
    if kind == "in":
        p = Rectangle((x - R, y - R), 2 * R, 2 * R, facecolor=INPUT_FILL,
                      edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2)
    else:
        p = Circle((x, y), R, facecolor=dmfig.VERTEX,
                   edgecolor=HIGHLIGHT if kind == "out" else dmfig.VERTEX_EDGE,
                   linewidth=3.2 if kind == "out" else 1.6, zorder=2)
    ax.add_patch(p)
    patches[name] = p
    ax.text(x, y, label, ha="center", va="center", fontsize=15, color=INK, zorder=3)

for u, v in arcs:
    ax.add_patch(FancyArrowPatch(nodes[u][:2], nodes[v][:2], patchA=patches[u], patchB=patches[v],
                                 arrowstyle="-|>", mutation_scale=14, shrinkA=0, shrinkB=0,
                                 color=EDGE, linewidth=2, zorder=1))

ax.add_patch(FancyArrowPatch((1.5, 3.0 + R), (1.5, 3.9), arrowstyle="-|>", mutation_scale=14,
                             color=HIGHLIGHT, linewidth=2, zorder=1))
ax.text(1.5, 4.1, r"$z_2$", ha="center", va="center", fontsize=14, color=INK)

kx, ky = 3.9, 2.9
ax.add_patch(Rectangle((kx - 0.13, ky - 0.13), 0.26, 0.26, facecolor=INPUT_FILL,
                       edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.3, ky, "вход (лист)", va="center", fontsize=10, color=INK)
ax.add_patch(Circle((kx, ky - 0.5), 0.15, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.3, ky - 0.5, "элемент", va="center", fontsize=10, color=INK)
ax.add_patch(Circle((kx, ky - 1.0), 0.15, facecolor=dmfig.VERTEX, edgecolor=HIGHLIGHT, linewidth=3.2))
ax.text(kx + 0.3, ky - 1.0, "выход (корень)", va="center", fontsize=10, color=INK)

ax.set_xlim(-0.6, 6.0)
ax.set_ylim(-0.6, 4.5)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "formula-as-sfe")
