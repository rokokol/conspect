"""Isoclines of y' = (y - x)/(y + x) with one integral curve.

Every isocline is a line through the origin, where the right-hand side is
undefined. The integral curve is the logarithmic spiral r = exp(-theta), the
exact solution in polar coordinates.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

LIM = 2.7
TICK = 0.16

# (direction of the line, slope of the tangents on it, label)
ISOCLINES = [
    ((1.0, 1.0), 0.0, r"$y'=0$"),
    ((0.0, 1.0), 1.0, r"$y'=1$"),
    ((1.0, 0.0), -1.0, r"$y'=-1$"),
    ((1.0, -1.0), np.inf, r"$y'=\infty$"),
]

fig, ax = plt.subplots(figsize=(6.4, 6.4))

for (dx, dy), slope, label in ISOCLINES:
    d = np.array([dx, dy]) / np.hypot(dx, dy)
    ax.plot([-LIM * d[0] * 1.4, LIM * d[0] * 1.4], [-LIM * d[1] * 1.4, LIM * d[1] * 1.4],
            color=dufig.FIELD, lw=1.4, zorder=1)
    t = np.array([0.0, 1.0]) if np.isinf(slope) else np.array([1.0, slope]) / np.hypot(1.0, slope)
    for s in np.arange(-2.4, 2.41, 0.4):
        if abs(s) < 0.3:
            continue
        c = s * d
        if max(abs(c[0]), abs(c[1])) > LIM:
            continue
        ax.plot([c[0] - TICK * t[0], c[0] + TICK * t[0]], [c[1] - TICK * t[1], c[1] + TICK * t[1]],
                color=dufig.HIGHLIGHT, lw=2.2, solid_capstyle="round", zorder=2)
    end = 2.45 * d
    ax.annotate(label, end, xytext=(8, 6), textcoords="offset points", color=dufig.INK, fontsize=10)

theta = np.linspace(-0.9, 6.2, 800)
r = np.exp(-theta)
ax.plot(r * np.cos(theta), r * np.sin(theta), color=dufig.SOLUTION, lw=2.4, zorder=3)

ax.axhline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.set_xlim(-LIM, LIM)
ax.set_ylim(-LIM, LIM)
ax.set_aspect("equal")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_title("Изоклины и интегральная кривая")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.FIELD, lw=1.4, label="изоклина"),
        Line2D([], [], color=dufig.HIGHLIGHT, lw=2.2, label="направление касательной"),
        Line2D([], [], color=dufig.SOLUTION, lw=2.4, label="интегральная кривая"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=8,
)

dufig.save(fig, 1, "изоклины")
