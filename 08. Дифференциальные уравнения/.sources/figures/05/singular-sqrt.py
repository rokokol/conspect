"""Equation y' = sqrt(y): the singular solution y = 0 and the parabolas tangent to it.

The general solution is y = ((x + C) / 2)^2 for x + C >= 0. The parabola with
C = -x0 leaves the axis at x0, so every point (x0, 0) of y = 0 lies on a
particular solution with the same tangent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

XLIM = (-3.0, 3.0)
YLIM = (-0.4, 3.0)

fig, ax = plt.subplots(figsize=(6.4, 4.2))

touch = np.arange(-2.5, 2.01, 0.5)
for x0 in touch:
    x = np.linspace(x0, XLIM[1], 300)
    ax.plot(x, ((x - x0) / 2) ** 2, color=dufig.FIELD, linewidth=1.4, zorder=1)
ax.plot(touch, np.zeros_like(touch), linestyle="none", marker="o", color=dufig.HIGHLIGHT,
        markeredgecolor=dufig.INK, markersize=6, zorder=4)

ax.plot(XLIM, (0, 0), color=dufig.SOLUTION, linewidth=2.6, zorder=3)

ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_title(r"Решения уравнения $y'=\sqrt{y}$")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.SOLUTION, linewidth=2.6, label=r"особое решение $y=0$"),
        Line2D([], [], color=dufig.FIELD, linewidth=1.4, label=r"$y=\left(\frac{x+C}{2}\right)^2$"),
        Line2D([], [], linestyle="none", marker="o", color=dufig.HIGHLIGHT,
               markeredgecolor=dufig.INK, label="точки касания"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, frameon=False, fontsize=8,
)

dufig.save(fig, 5, "singular-sqrt")
