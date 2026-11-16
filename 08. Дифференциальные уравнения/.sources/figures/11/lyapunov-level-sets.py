"""Level curves v = c and trajectories for the three examples of the Lyapunov and Chetaev theorems.

lyapunov-stable.png:     x1' = -x1 x2^4, x2' = x1^4 x2, v = x1^4 + x2^4. dv/dt = 0, every trajectory
                         stays on its level curve inside the epsilon-disk.
lyapunov-asymptotic.png: x1' = -x1^3 - x2, x2' = x1 - x2^3, v = x1^2 + x2^2. dv/dt = -2(x1^4 + x2^4),
                         the trajectories cross the circles inward.
chetaev-unstable.png:    x1' = x1^5 + x2^3, x2' = x1^3 + x2^5, v = x1^4 - x2^4. dv/dt = 4(x1^8 - x2^8) > 0
                         in the region G = {v > 0}, trajectories started in G leave the unit disk.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

TOPIC = 11
GRID = np.linspace(-1.25, 1.25, 601)
X1, X2 = np.meshgrid(GRID, GRID)


def stable_rhs(t, x):
    return [-x[0] * x[1] ** 4, x[0] ** 4 * x[1]]


def asymptotic_rhs(t, x):
    return [-x[0] ** 3 - x[1], x[0] - x[1] ** 3]


def chetaev_rhs(t, x):
    return [x[0] ** 5 + x[1] ** 3, x[0] ** 3 + x[1] ** 5]


def exits_unit_disk(t, x):
    return x[0] ** 2 + x[1] ** 2 - 1.0


exits_unit_disk.terminal = True


def setup(ax, title):
    ax.set_aspect("equal")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
    ax.axvline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.set_title(title)


def draw_trajectory(ax, sol):
    ax.plot(sol.y[0], sol.y[1], color=dufig.SOLUTION, linewidth=2.0, zorder=3)
    ax.plot(sol.y[0][0], sol.y[1][0], "o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
            markersize=6, zorder=4)


def epsilon_circle(ax, radius):
    phi = np.linspace(0, 2 * np.pi, 400)
    ax.plot(radius * np.cos(phi), radius * np.sin(phi), color=dufig.INK, linestyle="--",
            linewidth=1.3, zorder=2)


# Stable, not asymptotically: v is constant along solutions.
v1 = X1**4 + X2**4
fig, ax = plt.subplots(figsize=(5.6, 5.4))
setup(ax, r"$v=x_1^4+x_2^4$, $\dfrac{dv}{dt}=0$")
STARTS = ([0.45, 0.25], [0.8, 0.3], [-0.6, 0.6])
# The levels are the values of v at the starting points, so each trajectory lies on a drawn level.
ax.contour(X1, X2, v1, levels=sorted(s[0] ** 4 + s[1] ** 4 for s in STARTS),
           colors=[dufig.FIELD], linewidths=1.2, zorder=1)
epsilon_circle(ax, 1.0)
for start in STARTS:
    sol = solve_ivp(stable_rhs, (0, 400), start, max_step=0.05, rtol=1e-10, atol=1e-12)
    v = sol.y[0] ** 4 + sol.y[1] ** 4
    assert np.ptp(v) < 1e-7 * v[0], np.ptp(v)
    draw_trajectory(ax, sol)
ax.legend(handles=[
    Line2D([], [], color=dufig.FIELD, linewidth=1.2, label=r"поверхности уровня $v=c$"),
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.0, label="траектории, лежат на уровнях"),
    Line2D([], [], color=dufig.INK, linestyle="--", linewidth=1.3, label=r"$\varepsilon$-окрестность нуля"),
    Line2D([], [], marker="o", linestyle="none", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
           label="начальная точка"),
], loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=7)
dufig.save(fig, TOPIC, "lyapunov-stable")

# Asymptotically stable: v decreases strictly, trajectories cross the circles inward.
v2 = X1**2 + X2**2
fig, ax = plt.subplots(figsize=(5.6, 5.4))
setup(ax, r"$v=x_1^2+x_2^2$, $\dfrac{dv}{dt}=-2(x_1^4+x_2^4)$")
ax.contour(X1, X2, v2, levels=[0.1, 0.3, 0.6], colors=[dufig.FIELD], linewidths=1.2, zorder=1)
epsilon_circle(ax, 1.0)
for start in ([0.9, 0.0], [-0.5, 0.75], [0.1, -0.7]):
    sol = solve_ivp(asymptotic_rhs, (0, 12), start, max_step=0.02, rtol=1e-10, atol=1e-12)
    v = sol.y[0] ** 2 + sol.y[1] ** 2
    assert np.all(np.diff(v) < 0) and v[-1] < 0.2 * v[0], v[-1] / v[0]
    draw_trajectory(ax, sol)
ax.plot([0], [0], "o", color=dufig.INK, markersize=5, zorder=5)
ax.annotate(r"$x\to0$", (0, 0), xytext=(0.62, -0.42), fontsize=9, color=dufig.INK, zorder=6,
             arrowprops=dict(arrowstyle="->", color=dufig.INK, linewidth=1.0),
             bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.9))
ax.legend(handles=[
    Line2D([], [], color=dufig.FIELD, linewidth=1.2, label=r"поверхности уровня $v=c$"),
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.0, label="траектории, пересекают уровни внутрь"),
    Line2D([], [], color=dufig.INK, linestyle="--", linewidth=1.3, label=r"$\varepsilon$-окрестность нуля"),
    Line2D([], [], marker="o", linestyle="none", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
           label="начальная точка"),
], loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=7)
dufig.save(fig, TOPIC, "lyapunov-asymptotic")

# Unstable by Chetaev: G = {|x1| > |x2|} is where v > 0, and dv/dt > 0 there.
v3 = X1**4 - X2**4
fig, ax = plt.subplots(figsize=(5.6, 5.4))
setup(ax, r"$v=x_1^4-x_2^4$, $\dfrac{dv}{dt}=4(x_1^8-x_2^8)$")
ax.contourf(X1, X2, v3, levels=[0, 10], colors=[dufig.tint(dufig.HIGHLIGHT, 0.6)], zorder=0)
ax.plot([-1.25, 1.25], [-1.25, 1.25], color=dufig.INK, linewidth=1.2, zorder=2)
ax.plot([-1.25, 1.25], [1.25, -1.25], color=dufig.INK, linewidth=1.2, zorder=2)
epsilon_circle(ax, 1.0)
for start in ([0.30, 0.10], [0.30, -0.15], [-0.30, 0.12], [-0.28, -0.2]):
    sol = solve_ivp(chetaev_rhs, (0, 1e4), start, events=exits_unit_disk, max_step=0.05,
                    rtol=1e-10, atol=1e-12)
    assert sol.status == 1, "trajectory did not reach the unit circle"
    v = sol.y[0] ** 4 - sol.y[1] ** 4
    assert np.all(np.diff(v) > 0) and v[0] > 0
    draw_trajectory(ax, sol)
ax.legend(handles=[
    Patch(color=dufig.tint(dufig.HIGHLIGHT, 0.6), label=r"области $v>0$ (углы, $G$ — один из них)"),
    Line2D([], [], color=dufig.INK, linewidth=1.2, label=r"граница $G$: $v=0$"),
    Line2D([], [], color=dufig.SOLUTION, linewidth=2.0, label="траектории из $G$ уходят"),
    Line2D([], [], color=dufig.INK, linestyle="--", linewidth=1.3, label=r"окрестность $|x|<1$"),
    Line2D([], [], marker="o", linestyle="none", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
           label="начальная точка"),
], loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=7)
dufig.save(fig, TOPIC, "chetaev-unstable")
