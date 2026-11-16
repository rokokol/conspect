"""Adder S_n: n-1 cells Sigma_1 and one half adder Sigma', carries run from the lowest digit x_n to the left."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
CELL_FILL = dmfig.VERTEX
HALF_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)

fig, ax = plt.subplots(figsize=(11.0, 4.6))

W, H = 1.7, 1.3
# column: (centre x, digit index label, kind)
cols = [(0.0, "1", "cell"), (3.4, "2", "cell"), (10.2, "n-1", "cell"), (13.6, "n", "half")]


def arrow(p, q, colour=EDGE, lw=2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, shrinkA=0, shrinkB=0,
                                 color=colour, linewidth=lw, zorder=1))


for cx, idx, kind in cols:
    ax.add_patch(Rectangle((cx - W / 2, -H / 2), W, H, facecolor=CELL_FILL if kind == "cell" else HALF_FILL,
                           edgecolor=dmfig.VERTEX_EDGE, linewidth=1.8, zorder=2))
    ax.text(cx, 0, r"$\Sigma_1$" if kind == "cell" else r"$\Sigma'$", ha="center", va="center",
            fontsize=18, color=INK, zorder=3)
    for dx, name in ((-0.6, "x"), (0.6, "y")):
        arrow((cx + dx, 1.9), (cx + dx, H / 2))
        ax.text(cx + dx, 2.1, rf"${name}_{{{idx}}}$", ha="center", va="bottom", fontsize=13, color=INK)
    arrow((cx, -H / 2), (cx, -1.9), HIGHLIGHT)
    ax.text(cx, -2.1, rf"$z_{{{idx}}}$", ha="center", va="top", fontsize=13, color=INK)

# carries: from the left edge of column i to the right edge of column i-1
carry = [(3.4, 0.0, "1"), (10.2, 3.4 + 0.0, None), (13.6, 10.2, "n-1")]
arrow((3.4 - W / 2, 0), (0.0 + W / 2, 0))
ax.text((3.4 - W / 2 + W / 2) / 2, 0.18, r"$q_1$", ha="center", va="bottom", fontsize=13, color=INK)
arrow((13.6 - W / 2, 0), (10.2 + W / 2, 0))
ax.text((13.6 - W / 2 + 10.2 + W / 2) / 2, 0.18, r"$q_{n-1}$", ha="center", va="bottom", fontsize=13, color=INK)
# the middle part is not drawn
ax.plot([3.4 + W / 2, 3.4 + W / 2 + 0.7], [0, 0], color=EDGE, linewidth=2, linestyle=(0, (1, 2)))
ax.plot([10.2 - W / 2 - 0.7, 10.2 - W / 2], [0, 0], color=EDGE, linewidth=2, linestyle=(0, (1, 2)))
ax.text(6.8, 0, r"$\cdots$", ha="center", va="center", fontsize=24, color=INK)

# the carry out of the leftmost cell is the extra digit z_0
arrow((-W / 2, 0), (-2.6, 0), HIGHLIGHT)
ax.text(-2.75, 0, r"$z_0=q_0$", ha="right", va="center", fontsize=13, color=INK)

ax.text(13.6, -3.1, "полусумматор: 4 элемента", ha="center", va="center", fontsize=11, color=INK)
ax.text(0.0, -3.1, "ячейка: 9 элементов", ha="center", va="center", fontsize=11, color=INK)

ax.set_xlim(-6.2, 15.0)
ax.set_ylim(-3.5, 3.0)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "adder-chain")
