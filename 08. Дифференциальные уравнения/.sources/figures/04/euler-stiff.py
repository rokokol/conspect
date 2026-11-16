"""Euler polyline for y' = -10 y, y(0) = 1 on [0, 1] with h = 0.2 and h = 0.1.

The step multiplies the value by 1 - 10h: -1 for h = 0.2 (the polyline oscillates
between 1 and -1), 0 for h = 0.1 (the polyline drops to zero in one step).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

LAM = -10.0
POLY = dufig.P["plum"]


def rhs(x, y):
    return LAM * y


def euler(h):
    n = round(1 / h)
    xs = np.linspace(0, 1, n + 1)
    ys = [1.0]
    for x in xs[:-1]:
        ys.append(ys[-1] + h * rhs(x, ys[-1]))
    return xs, np.array(ys)


sol = solve_ivp(rhs, (0, 1), [1.0], dense_output=True, rtol=1e-12, atol=1e-14)
grid = np.linspace(0, 1, 400)
exact = sol.sol(grid)[0]

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True)
for ax, h in zip(axes, (0.2, 0.1)):
    xs, ys = euler(h)
    ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
    ax.plot(grid, exact, color=dufig.SOLUTION, linewidth=2.2, zorder=2)
    ax.plot(xs, ys, color=POLY, linewidth=1.8, zorder=3)
    ax.plot(xs, ys, linestyle="none", marker="o", markersize=5, color=dufig.HIGHLIGHT,
            markeredgecolor=dufig.INK, zorder=4)
    ax.set_title(rf"$h={str(h).replace('.', '{,}')}$, $\tilde y_{{j+1}}=(1-10h)\,\tilde y_j$")
    ax.set_xlabel(r"$x$")
    ax.set_ylim(-1.25, 1.25)

axes[0].set_ylabel(r"$y$")
handles = [
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, label=r"точное решение $e^{-10x}$"),
    Line2D([], [], color=POLY, linewidth=1.8, marker="o", markersize=5,
           markerfacecolor=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
           label="ломаная Эйлера, узлы"),
]
axes[1].legend(handles=handles, loc="upper right", fontsize=8)

dufig.save(fig, 4, "euler-stiff")
