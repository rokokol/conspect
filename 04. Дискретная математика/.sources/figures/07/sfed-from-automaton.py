"""SFED that models an automaton: an SFE for G', F' with every output q_j fed back to the input q'_j through a delay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
BOX_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)
DELAY_FILL = dmfig.tint(dmfig.P["sayori"], 0.5)

fig, ax = plt.subplots(figsize=(7.2, 4.2))


def wire(points, color=EDGE, arrow=True):
    for a, b in zip(points[:-2], points[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, linewidth=2, zorder=1, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>" if arrow else "-",
                                 mutation_scale=16, color=color, linewidth=2, zorder=1,
                                 shrinkA=0, shrinkB=0))


ax.add_patch(Rectangle((0, 1.2), 4.4, 2.2, facecolor=BOX_FILL, edgecolor=dmfig.VERTEX_EDGE,
                       linewidth=1.8, zorder=2))
ax.text(2.2, 2.3, r"СФЭ в $\{\wedge,\vee,\neg\}$" "\n" r"реализует $F',\,G'$",
        ha="center", va="center", fontsize=14, color=INK, zorder=3)

# inputs and outputs of the whole circuit
wire([(-1.4, 2.8), (0, 2.8)], color=EDGE)
ax.text(-1.5, 2.8, r"$x_1,\dots,x_n$", ha="right", va="center", fontsize=13, color=INK)
wire([(4.4, 2.8), (5.8, 2.8)], color=HIGHLIGHT)
ax.text(5.9, 2.8, r"$y_1,\dots,y_m$", ha="left", va="center", fontsize=13, color=INK)

# feedback through delays
D = (2.2, 0.0)
ax.add_patch(Rectangle((D[0] - 0.4, D[1] - 0.4), 0.8, 0.8, facecolor=DELAY_FILL,
                       edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
ax.text(*D, r"$\mathrm{з}$", ha="center", va="center", fontsize=16, color=INK, zorder=3)
wire([(3.7, 1.2), (3.7, 0.0), (D[0] + 0.4, 0.0)], arrow=True)
ax.text(3.85, 0.6, r"$q_1,\dots,q_r$", ha="left", va="center", fontsize=13, color=INK)
wire([(D[0] - 0.4, 0.0), (0.7, 0.0), (0.7, 1.2)], arrow=True)
ax.text(0.55, 0.6, r"$q'_1,\dots,q'_r$", ha="right", va="center", fontsize=13, color=INK)

ax.set_xlim(-3.4, 7.8)
ax.set_ylim(-0.7, 3.7)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "sfed-from-automaton")
