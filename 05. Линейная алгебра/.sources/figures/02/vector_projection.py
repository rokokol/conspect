"""Projection of a vector on a direction e, (x, e) = |x| cos(alpha), and additivity of the projection."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Rectangle  # noqa: E402

e = np.array([1.0, 0.0])
x = np.array([3.6, 1.8])
y = np.array([1.5, 1.2])
dot = lambda a, b: float(a @ b)  # noqa: E731
alpha = np.degrees(np.arccos(dot(x, e) / np.linalg.norm(x)))
assert np.isclose(dot(x + y, e), dot(x, e) + dot(y, e))


def arrow(ax, start, vec, color, lw=2.2, ls="-", style="-|>"):
    ax.annotate("", xy=np.add(start, vec), xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def square(ax, corner, size=0.16):
    ax.add_patch(Rectangle(corner, -size, size, fill=False, edgecolor=lafig.MUTED, lw=1.0))


def dimension(ax, x0, x1, level, text):
    """Horizontal dimension line from x0 to x1 at height `level`, with a label."""
    arrow(ax, (x0, level), (x1 - x0, 0), lafig.INK, lw=1.1, style="<|-|>")
    ax.text((x0 + x1) / 2, level - 0.12, text, color=lafig.INK, ha="center", va="top")


fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw=dict(width_ratios=[1, 1.15]))

# (a) projection of x on the line along e
a.set_xlim(-0.3, 4.2)
a.set_ylim(-1.1, 2.3)
a.set_aspect("equal")
a.axis("off")
a.set_title("Проекция вектора", color=lafig.INK, fontsize=11)
a.plot([-0.2, 4.1], [0, 0], color=lafig.MUTED, lw=1.2)
a.plot([x[0], x[0]], [0, x[1]], ls=":", color=lafig.AUX, lw=1.4)
square(a, (x[0], 0))
arrow(a, (0, 0), x, lafig.VECTOR)
arrow(a, (0, 0), e * 1.2, lafig.IMAGE, lw=2.6)
a.add_patch(Arc((0, 0), 1.3, 1.3, theta1=0, theta2=alpha, color=lafig.HIGHLIGHT, lw=1.6))
a.text(0.85, 0.2, r"$\alpha$", color=lafig.HIGHLIGHT, ha="center", va="center")
a.text(x[0] / 2 - 0.15, x[1] / 2 + 0.22, r"$x$", color=lafig.INK, ha="center", va="center")
a.text(0.6, -0.17, r"$e$", color=lafig.INK, ha="center", va="top")
arrow(a, (0, 0), (x[0], 0), lafig.HIGHLIGHT, lw=2.0)
a.text(x[0] * 0.62, 0.12, r"$\hat x$ — проекция $x$", color=lafig.HIGHLIGHT, ha="center", va="bottom")
dimension(a, 0, x[0], -0.55, r"$(x,e)=|x|\cos\alpha=|\hat x|$")

# (b) additivity: (x + y, e) = (x, e) + (y, e)
b.set_xlim(-0.3, 5.4)
b.set_ylim(-1.9, 3.3)
b.set_aspect("equal")
b.axis("off")
b.set_title("Проекция суммы", color=lafig.INK, fontsize=11)
b.plot([-0.2, 5.3], [0, 0], color=lafig.MUTED, lw=1.2)
s = x + y
for p, c in ((y, lafig.AUX), (x, lafig.AUX), (s, lafig.AUX)):
    b.plot([p[0], p[0]], [0, p[1]], ls=":", color=c, lw=1.4)
b.plot([y[0] + 0, s[0]], [y[1], s[1]], ls="--", color=lafig.AUX, lw=1.2)
b.plot([x[0], s[0]], [x[1], s[1]], ls="--", color=lafig.AUX, lw=1.2)
arrow(b, (0, 0), x, lafig.VECTOR)
arrow(b, (0, 0), y, lafig.VECTOR)
arrow(b, (0, 0), s, lafig.IMAGE, lw=2.6)
b.text(x[0] * 0.65 + 0.1, x[1] * 0.65 - 0.3, r"$x$", color=lafig.INK, ha="center", va="center")
b.text(y[0] / 2 - 0.15, y[1] / 2 + 0.2, r"$y$", color=lafig.INK, ha="center", va="center")
b.text(s[0] * 0.62 - 0.45, s[1] * 0.62 + 0.45, r"$x+y$", color=lafig.INK, ha="center", va="center")
dimension(b, 0, y[0], -0.45, r"$(y,e)$")
dimension(b, y[0], s[0], -0.45, r"$(x,e)$")
dimension(b, 0, s[0], -1.15, r"$(x+y,e)$")

lafig.save(fig, 2, "vector_projection")
