"""The rectangle of the Cauchy problem, the cone |y - y0| <= M|x - x0| and h = min(a, b/M).

The example is y' = 1 + y^2, y(0) = 0 on |x| <= 1, |y| <= 1: M = 2, h = 1/2.
The solution tan x leaves the rectangle through its top side at x = pi/4 < a.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

A, B = 1.0, 1.0
M = 1 + B**2
H = min(A, B / M)


def rhs(x, y):
    return 1 + y**2


def leave_top(x, y):
    return abs(y[0]) - 1.25


leave_top.terminal = True

fig, ax = plt.subplots(figsize=(6.4, 4.6))

SHADE = dufig.tint(dufig.HIGHLIGHT, 0.6)
ax.add_patch(Rectangle((-H, -B), 2 * H, 2 * B, color=SHADE, linewidth=0, zorder=0))
ax.add_patch(Rectangle((-A, -B), 2 * A, 2 * B, fill=False,
                       edgecolor=dufig.INK, linewidth=1.4, zorder=2))

xs = np.linspace(-A, A, 200)
ax.plot(xs, M * xs, color=dufig.FIELD, linestyle="--", linewidth=1.2, zorder=1)
ax.plot(xs, -M * xs, color=dufig.FIELD, linestyle="--", linewidth=1.2, zorder=1)

for span in ((0, A), (0, -A)):
    sol = solve_ivp(rhs, span, [0.0], events=leave_top, max_step=0.005,
                    rtol=1e-10, atol=1e-12)
    ax.plot(sol.t, sol.y[0], color=dufig.SOLUTION, linewidth=2.2, zorder=3)

x_exit = np.pi / 4
EXIT = dict(marker="o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK, markersize=7)
ax.plot([x_exit, -x_exit], [1.0, -1.0], linestyle="none", zorder=4, **EXIT)
ax.plot([0], [0], marker="o", color=dufig.INK, markersize=5, zorder=4)

ax.set_xticks([-A, -H, 0, H, A])
ax.set_xticklabels([r"$x_0-a$", r"$x_0-h$", r"$x_0$", r"$x_0+h$", r"$x_0+a$"])
ax.set_yticks([-B, 0, B])
ax.set_yticklabels([r"$y_0-b$", r"$y_0$", r"$y_0+b$"])
ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.3, 1.3)
ax.set_title(r"Прямоугольник $\Pi$ и отрезок $|x-x_0|\leq h$")

handles = [
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, label="решение"),
    Line2D([], [], color=dufig.FIELD, linestyle="--", label=r"$|y-y_0|=M|x-x_0|$"),
    Patch(color=SHADE, label=r"$|x-x_0|\leq h$"),
    Line2D([], [], linestyle="none", label=r"выход из $\Pi$", **EXIT),
]
ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)

dufig.save(fig, 3, "cauchy-rectangle")
