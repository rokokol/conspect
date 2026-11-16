"""SFE of the adder cell Sigma_1: two half adders Sigma' and one disjunction, 9 elements; outputs z and q'."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
INPUT_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)

fig, ax = plt.subplots(figsize=(7.4, 8.4))

R = 0.36
# node: (x, y, label, kind); kind is "in" (source), "elem" or "out" (an element that is an output)
nodes = {
    "x": (0.0, 7.4, r"$x$", "in"),
    "y": (2.6, 7.4, r"$y$", "in"),
    "q": (4.6, 3.1, r"$q$", "in"),
    "A1": (0.0, 5.9, r"$\wedge$", "elem"),
    "B1": (2.6, 5.9, r"$\vee$", "elem"),
    "N1": (0.0, 4.5, r"$\neg$", "elem"),
    "D1": (1.3, 3.1, r"$\wedge$", "elem"),
    "A2": (0.0, 1.5, r"$\wedge$", "elem"),
    "B2": (2.6, 1.5, r"$\vee$", "elem"),
    "N2": (0.0, 0.1, r"$\neg$", "elem"),
    "D2": (1.3, -1.3, r"$\wedge$", "out"),
    "V": (-2.8, 3.7, r"$\vee$", "out"),
}
arcs = [
    ("x", "A1"), ("y", "A1"), ("x", "B1"), ("y", "B1"), ("A1", "N1"), ("N1", "D1"), ("B1", "D1"),
    ("D1", "A2"), ("q", "A2"), ("D1", "B2"), ("q", "B2"), ("A2", "N2"), ("N2", "D2"), ("B2", "D2"),
    ("A1", "V"), ("A2", "V"),
]

# the two half adders, drawn behind the elements
for y0, y1 in ((2.55, 6.45), (-1.85, 2.05)):
    ax.add_patch(FancyBboxPatch((-0.75, y0), 4.3, y1 - y0, boxstyle="round,pad=0.0,rounding_size=0.25",
                                facecolor="none", edgecolor=dmfig.MUTED, linewidth=1.6,
                                linestyle=(0, (5, 4)), zorder=0))
MUTED_TEXT = dmfig.tint(dmfig.INK, 0.45)
ax.text(3.8, 5.0, r"$\Sigma'$", ha="left", va="center", fontsize=16, color=MUTED_TEXT)
ax.text(3.8, 0.2, r"$\Sigma'$", ha="left", va="center", fontsize=16, color=MUTED_TEXT)

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
ax.add_patch(FancyArrowPatch((-2.8 - R, 3.7), (-4.2, 3.7), arrowstyle="-|>", mutation_scale=16,
                             color=HIGHLIGHT, linewidth=2, zorder=1))
ax.text(-4.35, 3.7, r"$q'=m(x,y,q)$", ha="right", va="center", fontsize=14, color=INK)
ax.add_patch(FancyArrowPatch((1.3, -1.3 - R), (1.3, -2.5), arrowstyle="-|>", mutation_scale=16,
                             color=HIGHLIGHT, linewidth=2, zorder=1))
ax.text(1.3, -2.85, r"$z=x\oplus y\oplus q$", ha="center", va="center", fontsize=14, color=INK)

# key, drawn with the same markers as the circuit
kx, ky = 5.0, 6.6
ax.add_patch(Rectangle((kx - 0.15, ky - 0.15), 0.3, 0.3, facecolor=INPUT_FILL,
                       edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.35, ky, "вход (исток)", va="center", fontsize=11, color=INK)
ax.add_patch(Circle((kx, ky - 0.6), 0.17, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
ax.text(kx + 0.35, ky - 0.6, "функциональный элемент", va="center", fontsize=11, color=INK)
ax.add_patch(Circle((kx, ky - 1.2), 0.17, facecolor=dmfig.VERTEX, edgecolor=HIGHLIGHT, linewidth=3.2))
ax.text(kx + 0.35, ky - 1.2, "выход схемы", va="center", fontsize=11, color=INK)
ax.add_patch(FancyBboxPatch((kx - 0.2, ky - 2.0), 0.4, 0.3, boxstyle="round,pad=0.0,rounding_size=0.08",
                            facecolor="none", edgecolor=dmfig.MUTED, linewidth=1.6, linestyle=(0, (3, 2))))
ax.text(kx + 0.35, ky - 1.85, "полусумматор (4 элемента)", va="center", fontsize=11, color=INK)

ax.set_xlim(-8.0, 9.6)
ax.set_ylim(-3.3, 8.0)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "adder-cell")
