"""The mirror that sends the rays of a source at the origin out parallel to the x axis.

The mirror is the parabola y^2 = 2Cx + C^2 with its focus at O. At a point
M(x, y) the tangent meets the x axis at A = (-r, 0), r = |OM|: the triangle
OAM is isosceles, and tan(alpha) = y / (x + r) is the slope of the tangent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Arc, Polygon  # noqa: E402

C = 1.0
XMAX = 3.2
YMAX = np.sqrt(2 * C * XMAX + C**2)


def mirror_x(y):
    return (y**2 - C**2) / (2 * C)


fig, ax = plt.subplots(figsize=(6.8, 4.6))

ys = np.linspace(-YMAX, YMAX, 500)
ax.plot(mirror_x(ys), ys, color=dufig.SOLUTION, lw=2.4, zorder=3)

for yr in (-1.5, -0.9, 0.9, 2.6, -2.6):
    xr = mirror_x(yr)
    ax.plot([0, xr], [0, yr], color=dufig.FIELD, lw=1.2, zorder=1)
    ax.annotate("", (XMAX + 0.45, yr), (xr, yr),
                arrowprops=dict(arrowstyle="->", color=dufig.FIELD, lw=1.2), zorder=1)

ym = 1.9
xm = mirror_x(ym)
r = np.hypot(xm, ym)
alpha = np.arctan2(ym, xm + r)
assert abs(np.tan(alpha) - ym / (xm + r)) < 1e-12
assert abs(np.tan(alpha) - (r - xm) / ym) < 1e-12
assert abs(np.tan(alpha) - C / ym) < 1e-12

ax.add_patch(Polygon([(0, 0), (-r, 0), (xm, ym)], closed=True,
                     color=dufig.tint(dufig.HIGHLIGHT, 0.65), linewidth=0, zorder=0))
ax.plot([-r - 0.3 * np.cos(alpha), xm + 0.55 * np.cos(alpha)],
        [-0.3 * np.sin(alpha), ym + 0.55 * np.sin(alpha)], color=dufig.INK, lw=1.4, zorder=2)
ax.plot([0, xm], [0, ym], color=dufig.HIGHLIGHT, lw=2.0, zorder=2)
ax.annotate("", (XMAX + 0.45, ym), (xm, ym),
            arrowprops=dict(arrowstyle="->", color=dufig.HIGHLIGHT, lw=2.0), zorder=2)
ax.plot([xm], [ym], "o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK, markersize=7, zorder=4)
ax.plot([0], [0], "o", color=dufig.INK, markersize=5, zorder=4)

deg = np.degrees(alpha)
ax.add_patch(Arc((-r, 0), 1.3, 1.3, theta1=0, theta2=deg, color=dufig.INK, lw=1.0, zorder=3))
ax.add_patch(Arc((xm, ym), 1.3, 1.3, theta1=0, theta2=deg, color=dufig.INK, lw=1.0, zorder=3))
ax.add_patch(Arc((xm, ym), 1.3, 1.3, theta1=180 + deg, theta2=180 + 2 * deg, color=dufig.INK,
                 lw=1.0, zorder=3))
ax.annotate(r"$\alpha$", (-r + 0.95, 0.12), color=dufig.INK)
ax.annotate(r"$\alpha$", (xm + 0.72, ym + 0.08), color=dufig.INK)
lab = np.array([xm, ym]) + 0.5 * np.array([np.cos(np.pi + 1.5 * alpha), np.sin(np.pi + 1.5 * alpha)])
ax.annotate(r"$\alpha$", lab, ha="center", va="center", color=dufig.INK)
ax.annotate(r"$M(x,y)$", (xm, ym), xytext=(-6, 10), textcoords="offset points", ha="center", color=dufig.INK)
ax.annotate(r"$A$", (-r, 0), xytext=(0, -16), textcoords="offset points", ha="center", color=dufig.INK)
ax.annotate(r"$O$", (0, 0), xytext=(-2, -16), textcoords="offset points", ha="center", color=dufig.INK)

ax.axhline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.set_xlim(-r - 0.7, XMAX + 0.6)
ax.set_ylim(-YMAX - 0.2, YMAX + 0.2)
ax.set_aspect("equal")
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title("Зеркало с фокусом в начале координат")
ax.legend(
    handles=[
        Line2D([], [], color=dufig.FIELD, lw=1.2, label="луч источника и отражённый луч"),
        Line2D([], [], color=dufig.HIGHLIGHT, lw=2.0, label="выделенный луч в точке $M$"),
        Line2D([], [], color=dufig.INK, lw=1.4, label="касательная в $M$"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=8,
)

dufig.save(fig, 1, "parabolic-mirror")
