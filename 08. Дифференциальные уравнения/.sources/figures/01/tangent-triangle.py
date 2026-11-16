"""The tangent to a curve and the triangle it cuts off the coordinate axes.

The curve is the hyperbola y = S / (2x), the solution of the area problem for
S = 2: the tangent at M(x, y) meets the axes at A = (0, y - x y') and
B = (x - y / y', 0), and the triangle OAB has area S for every M.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

S = 2.0


def curve(x):
    return S / (2 * x)


def slope(x):
    return -S / (2 * x**2)


xm = 1.4
ym = curve(xm)
k = slope(xm)
ya = ym - xm * k
xb = xm - ym / k
assert abs(0.5 * ya * xb - S) < 1e-12

fig, ax = plt.subplots(figsize=(6.4, 4.6))

ax.add_patch(Polygon([(0, 0), (0, ya), (xb, 0)], closed=True,
                     color=dufig.tint(dufig.HIGHLIGHT, 0.65), linewidth=0, zorder=0))
xs = np.linspace(0.38, 3.6, 400)
ax.plot(xs, curve(xs), color=dufig.SOLUTION, lw=2.4, zorder=3)
ax.plot([0, xb], [ya, 0], color=dufig.INK, lw=1.4, zorder=2)
ax.plot([xm, xm], [0, ym], color=dufig.MUTED, lw=1.0, ls="--", zorder=1)
ax.plot([0, xm], [ym, ym], color=dufig.MUTED, lw=1.0, ls="--", zorder=1)
ax.plot([xm], [ym], "o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK, markersize=7, zorder=4)

ax.axhline(0, color=dufig.MUTED, lw=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, lw=0.8, zorder=0)
LABELS = [
    (r"$M(x,y)$", (xm, ym), (8, 8)),
    (r"$A$", (0, ya), (-14, 2)),
    (r"$C$", (0, ym), (-14, -3)),
    (r"$O$", (0, 0), (-14, -12)),
    (r"$D$", (xm, 0), (0, -16)),
    (r"$B$", (xb, 0), (2, -16)),
    (r"$S$", (0.55, 0.45), (0, 0)),
]
for text, xy, off in LABELS:
    ax.annotate(text, xy, xytext=off, textcoords="offset points", color=dufig.INK, ha="center")
ax.annotate(r"$l$", (3.2, curve(3.2)), xytext=(4, 8), textcoords="offset points", color=dufig.SOLUTION)

ax.set_xlim(-0.3, 4.0)
ax.set_ylim(-0.3, 2.6)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title("Касательная и треугольник $OAB$")

dufig.save(fig, 1, "tangent-triangle")
