"""Clairaut equation y = x y' + y' - y'^2.

The general solution is the family of lines y = C x + C - C^2. The singular
solution y = (x + 1)^2 / 4 is tangent to every line of the family at x = 2C - 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

XLIM = (-3.0, 3.0)
YLIM = (-1.5, 4.5)

x = np.linspace(*XLIM, 400)

fig, ax = plt.subplots(figsize=(6.4, 5.0))

for c in np.arange(-1.0, 2.01, 0.5):
    ax.plot(x, c * x + c - c**2, color=dufig.FIELD, linewidth=1.3, zorder=1)
    xc = 2 * c - 1
    ax.plot([xc], [(xc + 1) ** 2 / 4], marker="o", color=dufig.HIGHLIGHT,
            markeredgecolor=dufig.INK, markersize=6, zorder=4)

ax.plot(x, (x + 1) ** 2 / 4, color=dufig.SOLUTION, linewidth=2.6, zorder=3)

ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_title("Уравнение Клеро")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.FIELD, linewidth=1.3, label=r"общее решение $y=Cx+C-C^2$"),
        Line2D([], [], color=dufig.SOLUTION, linewidth=2.6, label=r"особое решение $y=\frac{(x+1)^2}{4}$"),
        Line2D([], [], linestyle="none", marker="o", color=dufig.HIGHLIGHT,
               markeredgecolor=dufig.INK, label=r"касание при $x=2C-1$"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=8,
)

dufig.save(fig, 5, "clairaut-envelope")
