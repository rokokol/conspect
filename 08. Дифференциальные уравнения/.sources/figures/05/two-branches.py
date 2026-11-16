"""Solutions of y'^2 - (2x + y) y' + 2xy = 0: the parabolas y = x^2 + C1 and the exponentials y = C2 e^x.

The left-hand side factors as (y' - 2x)(y' - y). Through a point (x0, y0) pass one
parabola and one exponential with slopes 2 x0 and y0. They have the same slope
exactly on the line y = 2x, where dF/dy' = 2y' - 2x - y vanishes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

XLIM = (-2.2, 2.2)
YLIM = (-2.2, 4.0)

x = np.linspace(*XLIM, 400)

fig, ax = plt.subplots(figsize=(6.4, 5.0))

for c1 in np.arange(-2.0, 3.1, 1.0):
    ax.plot(x, x**2 + c1, color=dufig.FIELD, linewidth=1.2, zorder=1)
for c2 in np.arange(-2.0, 2.1, 0.5):
    if c2 != 0:
        ax.plot(x, c2 * np.exp(x), color=dufig.FIELD, linewidth=1.2, zorder=1)
ax.axhline(0, color=dufig.FIELD, linewidth=1.2, zorder=1)

# one point with different slopes, one point where the slopes meet
x0, y0 = -0.5, 1.0
c1, c2 = y0 - x0**2, y0 * np.exp(-x0)
ax.plot(x, x**2 + c1, color=dufig.SOLUTION, linewidth=2.2, zorder=3)
ax.plot(x, c2 * np.exp(x), color=dufig.SOLUTION, linewidth=2.2, linestyle="--", zorder=3)
ax.plot([x0], [y0], marker="o", color=dufig.INK, markersize=5, zorder=5)

xt = 1.2
yt = 2 * xt
ax.plot(x, x**2 + (yt - xt**2), color=dufig.HIGHLIGHT, linewidth=2.2, zorder=2)
ax.plot(x, yt * np.exp(x - xt), color=dufig.HIGHLIGHT, linewidth=2.2, linestyle="--", zorder=2)
ax.plot(x, 2 * x, color=dufig.INK, linewidth=1.6, linestyle=(0, (4, 3)), zorder=3)
ax.plot([xt], [yt], marker="o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
        markersize=7, zorder=5)

ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.axvline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_title("Два семейства решений")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, label=r"$y=x^2+C_1$ через точку"),
        Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, linestyle="--",
               label=r"$y=C_2e^x$ через ту же точку"),
        Line2D([], [], color=dufig.INK, linewidth=1.6, linestyle=(0, (4, 3)),
               label=r"$y=2x$: наклоны совпадают"),
        Line2D([], [], color=dufig.HIGHLIGHT, linewidth=2.2, marker="o",
               markeredgecolor=dufig.INK, markersize=7,
               label="парабола и экспонента, касающиеся в точке на $y=2x$"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=8,
)

dufig.save(fig, 5, "two-branches")
