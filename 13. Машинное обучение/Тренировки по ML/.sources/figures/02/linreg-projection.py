"""OLS as an orthogonal projection of Y onto the column space of X: a schematic side view."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

fig, ax = fk.subplots(1, 1, size=(6.6, 4.4))

# The plane L is a parallelogram seen obliquely; "up" on the page is the normal direction.
plane = np.array([[0.0, 0.0], [6.4, 0.0], [8.2, 1.9], [1.8, 1.9]])
ax.add_patch(Polygon(plane, closed=True, fc=fk.tint(fk.BLUE, 0.78), ec=fk.BLUE, lw=1.2, zorder=1))

O = np.array([2.3, 0.75])
c1 = O + np.array([2.6, 0.0])
c2 = O + np.array([1.3, 0.9])
Yh = O + np.array([3.6, 0.55])
Y = Yh + np.array([0.0, 2.3])


def vec(a, b, color, lw=2.2, ls="-", z=3):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


vec(O, c1, fk.BLUE)
vec(O, c2, fk.BLUE)
vec(O, Y, fk.TEXT, lw=2.4)
vec(O, Yh, fk.RED, lw=2.4)
vec(Yh, Y, fk.CATEGORICAL[1], ls="--")

# Right angle between the residual and the plane
a = 0.28
ax.plot([Yh[0] - a, Yh[0] - a, Yh[0]], [Yh[1], Yh[1] + a, Yh[1] + a], color=fk.TEXT_2, lw=1, zorder=4)

ax.scatter(*O, color=fk.TEXT, s=18, zorder=5)
ax.text(O[0] - 0.15, O[1] - 0.3, "0", ha="right", color=fk.TEXT_2)
ax.text(O[0] + 0.3, O[1] - 0.36, "столбец из единиц", color=fk.BLUE)
ax.text(c2[0] - 0.3, 2.1, "столбец признака", color=fk.BLUE, ha="right", va="bottom")
ax.text(Y[0] + 0.15, Y[1], r"$Y$", color=fk.TEXT, fontsize=13, va="center")
ax.text(Yh[0] + 0.15, Yh[1] - 0.45, r"$X\hat w$", color=fk.RED, fontsize=13)
ax.text(Yh[0] + 0.15, Yh[1] + 1.15, r"остаток $Y-X\hat w$", color=fk.CATEGORICAL[1], va="center")
ax.text(0.7, 0.05,"плоскость $L$ — линейная оболочка столбцов", color=fk.BLUE, fontsize=8)

ax.set_xlim(-0.2, 9.0)
ax.set_ylim(-0.2, 4.0)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("$Y$ проецируется на плоскость столбцов")
fk.save(fig, OUT / "linreg-projection.png")
