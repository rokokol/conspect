"""Phase plane (y1, y2) of the system y1' = y2, y2' = -y1, equivalent to y'' + y = 0.

An isocline dy2/dy1 = -y1/y2 = tan(alpha) = k is the line y2 = -y1/k through
the origin. The tangent to a trajectory is perpendicular to the radius vector,
so the trajectories are circles; the flow runs clockwise because y1' = y2.
Circles come from the numerical solution, not from the closed form.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

LIM = 3.0
TICK = 0.17

# slope k of the tangent and the unit direction of the isocline y2 = -y1 / k
ISOCLINES = [
    (0.0, (0.0, 1.0), r"$k=0$"),
    (1.0, (1.0, -1.0), r"$k=1$"),
    (-1.0, (1.0, 1.0), r"$k=-1$"),
    (2.0, (2.0, -1.0), r"$k=2$"),
    (-2.0, (2.0, 1.0), r"$k=-2$"),
    (0.5, (1.0, -2.0), r"$k=\frac{1}{2}$"),
    (-0.5, (1.0, 2.0), r"$k=-\frac{1}{2}$"),
    (np.inf, (1.0, 0.0), r"$k=\infty$"),
]

fig, ax = plt.subplots(figsize=(6.4, 6.4))


def rhs(t, y):
    return [y[1], -y[0]]


for radius in (1.0, 2.0):
    sol = solve_ivp(rhs, (0, 2 * np.pi), [0.0, radius], rtol=1e-10, atol=1e-12, dense_output=True)
    ts = np.linspace(0, 2 * np.pi, 600)
    y1, y2 = sol.sol(ts)
    assert np.allclose(np.hypot(y1, y2), radius, atol=1e-7)
    ax.plot(y1, y2, color=dufig.SOLUTION, lw=2.2, zorder=3)
    i = 90
    ax.annotate("", (y1[i + 6], y2[i + 6]), (y1[i], y2[i]),
                arrowprops=dict(arrowstyle="-|>", color=dufig.SOLUTION, lw=2.2, mutation_scale=14), zorder=4)

for k, (dx, dy), label in ISOCLINES:
    d = np.array([dx, dy]) / np.hypot(dx, dy)
    ax.plot([-LIM * 1.4 * d[0], LIM * 1.4 * d[0]], [-LIM * 1.4 * d[1], LIM * 1.4 * d[1]],
            color=dufig.FIELD, lw=1.2, zorder=1)
    t = np.array([0.0, 1.0]) if np.isinf(k) else np.array([1.0, k]) / np.hypot(1.0, k)
    assert abs(d @ t) < 1e-12
    for s in (-2.4, -1.5, 1.5, 2.4):
        c = s * d
        ax.plot([c[0] - TICK * t[0], c[0] + TICK * t[0]], [c[1] - TICK * t[1], c[1] + TICK * t[1]],
                color=dufig.HIGHLIGHT, lw=3.0, solid_capstyle="round", zorder=2)
    ax.annotate(label, 2.8 * d, xytext=(0, 0), textcoords="offset points", color=dufig.INK,
                fontsize=9, ha="center", va="center")

ax.axhline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.set_xlim(-LIM, LIM)
ax.set_ylim(-LIM, LIM)
ax.set_aspect("equal")
ax.set_xlabel(r"$y_1$")
ax.set_ylabel(r"$y_2$")
ax.set_title("Фазовая плоскость системы $y_1'=y_2$, $y_2'=-y_1$")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.FIELD, lw=1.2, label=r"изоклина $\tan\alpha=k$"),
        Line2D([], [], color=dufig.HIGHLIGHT, lw=2.2, label="касательная к траектории"),
        Line2D([], [], color=dufig.SOLUTION, lw=2.2, label="траектория, стрелка по ходу $x$"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=8,
)

dufig.save(fig, 1, "phase-plane-oscillator")
