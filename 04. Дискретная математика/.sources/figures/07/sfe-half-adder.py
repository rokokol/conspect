"""SFE of the half adder: inputs x, y; elements and, or, not, and; outputs z1 = xy, z2 = x xor y."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
INPUT_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)

fig, ax = plt.subplots(figsize=(6.4, 5.4))

R = 0.36
# node: (x, y, label, kind); kind is "in" (source), "elem" or "out" (an element that is an output)
nodes = {
    "x": (0.0, 4.6, r"$x$", "in"),
    "y": (3.2, 4.6, r"$y$", "in"),
    "A": (0.0, 3.0, r"$\wedge$", "out"),
    "B": (3.2, 3.0, r"$\vee$", "elem"),
    "N": (0.0, 1.5, r"$\neg$", "elem"),
    "D": (1.6, 0.0, r"$\wedge$", "out"),
}
arcs = [("x", "A"), ("y", "A"), ("x", "B"), ("y", "B"), ("A", "N"), ("N", "D"), ("B", "D")]

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
    ax.text(x, y, label, ha="center", va="center", fontsize=16, color=INK, zorder=3)

for u, v in arcs:
    ax.add_patch(FancyArrowPatch(nodes[u][:2], nodes[v][:2], patchA=patches[u], patchB=patches[v],
                                 arrowstyle="-|>", mutation_scale=16, shrinkA=0, shrinkB=0,
                                 color=EDGE, linewidth=2, zorder=1))

# output wires
ax.add_patch(FancyArrowPatch((-R, 3.0), (-1.5, 3.0), arrowstyle="-|>", mutation_scale=16,
                             color=HIGHLIGHT, linewidth=2, zorder=1))
ax.text(-1.65, 3.0, r"$z_1=xy$", ha="right", va="center", fontsize=14, color=INK)
ax.add_patch(FancyArrowPatch((1.6, -R), (1.6, -1.2), arrowstyle="-|>", mutation_scale=16,
                             color=HIGHLIGHT, linewidth=2, zorder=1))
ax.text(1.6, -1.5, r"$z_2=(\overline{xy})(x\vee y)$", ha="center", va="center", fontsize=14, color=INK)

# key, drawn with the same markers as the circuit
kx, ky = 4.5, 1.3
ax.add_patch(Rectangle((kx - 0.15, ky - 0.15), 0.3, 0.3, facecolor=INPUT_FILL,
                       edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.35, ky, "вход (исток)", va="center", fontsize=11, color=INK)
ax.add_patch(Circle((kx, ky - 0.6), 0.17, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.35, ky - 0.6, "функциональный элемент", va="center", fontsize=11, color=INK)
ax.add_patch(Circle((kx, ky - 1.2), 0.17, facecolor=dmfig.VERTEX, edgecolor=HIGHLIGHT, linewidth=3.2))
ax.text(kx + 0.35, ky - 1.2, "выход схемы", va="center", fontsize=11, color=INK)

ax.set_xlim(-3.4, 8.2)
ax.set_ylim(-2.0, 5.3)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "sfe-half-adder")
