"""Euler polyline for y' = y, y(0) = 1 on [0, 1] with N = 5 nodes (h = 0.2), against e^x.

Each segment is the tangent of the line field at the left node of its step, so the
polyline is built by the recurrence y_{j+1} = y_j + h f(x_j, y_j) itself.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

A, N = 1.0, 5
H = A / N


def rhs(x, y):
    return y


nodes = np.linspace(0, A, N + 1)
ys = [1.0]
for x in nodes[:-1]:
    ys.append(ys[-1] + H * rhs(x, ys[-1]))
ys = np.array(ys)

sol = solve_ivp(rhs, (0, A), [1.0], dense_output=True, rtol=1e-12, atol=1e-12)
xs = np.linspace(0, A, 400)
exact = sol.sol(xs)[0]

fig, ax = plt.subplots(figsize=(6.4, 4.6))

for xj, yj in zip(nodes, ys):
    ax.plot([xj, xj], [0, yj], color=dufig.FIELD, linestyle="--", linewidth=1, zorder=1)

ax.plot(xs, exact, color=dufig.SOLUTION, linewidth=2.2, zorder=2)
POLY = dufig.P["plum"]
ax.plot(nodes, ys, color=POLY, linewidth=1.8, zorder=3)
ax.plot(nodes, ys, linestyle="none", marker="o", markersize=6, color=dufig.HIGHLIGHT,
        markeredgecolor=dufig.INK, zorder=4)

end_exact = sol.sol(A)[0]
ax.annotate("", xy=(A, ys[-1]), xytext=(A, end_exact),
            arrowprops=dict(arrowstyle="<->", color=dufig.INK, linewidth=1))
ax.annotate(rf"$e-\tilde y_N\approx{end_exact - ys[-1]:.2f}$".replace(".", "{,}"),
            (A, (end_exact + ys[-1]) / 2), xytext=(-10, -14), textcoords="offset points",
            ha="right", va="center", fontsize=9, color=dufig.INK)

ax.set_xticks(nodes)
ax.set_xticklabels([rf"$x_{j}$" for j in range(N + 1)])
ax.set_yticks(ys)
ax.set_yticklabels([rf"$\tilde y_{j}$" for j in range(N + 1)])
ax.set_xlim(-0.04, 1.06)
ax.set_ylim(0.8, 2.9)
ax.set_title(r"Ломаная Эйлера для $y'=y$, $y(0)=1$, $h=0{,}2$")

handles = [
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, label=r"точное решение $e^x$"),
    Line2D([], [], color=POLY, linewidth=1.8, marker="o", markersize=6,
           markerfacecolor=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
           label="ломаная Эйлера, узлы"),
]
ax.legend(handles=handles, loc="upper left", fontsize=8)

dufig.save(fig, 4, "euler-polyline")
