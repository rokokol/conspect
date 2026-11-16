"""Sum and difference of vectors: the parallelogram rule, the triangle rule, x - y."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

x = np.array([3.0, 0.8])
y = np.array([1.0, 2.0])
s = x + y
d = x - y
assert np.allclose(s, y + x) and np.allclose(y + d, x)


def arrow(ax, start, vec, color, lw=2.2, ls="-"):
    ax.annotate("", xy=start + vec, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def label(ax, point, text, color, dx=0.0, dy=0.0):
    ax.text(point[0] + dx, point[1] + dy, text, color=color, ha="center", va="center")


def panel(ax, title):
    ax.set_xlim(-0.5, 4.8)
    ax.set_ylim(-0.7, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, color=lafig.INK, fontsize=11)


o = np.zeros(2)
fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.7))

ax = axes[0]
panel(ax, "Правило параллелограмма")
for a, b in ((x, y), (y, x)):
    ax.plot(*zip(a, a + b), ls="--", color=lafig.AUX, lw=1.3)
arrow(ax, o, x, lafig.VECTOR)
arrow(ax, o, y, lafig.VECTOR)
arrow(ax, o, s, lafig.IMAGE, lw=2.6)
label(ax, x / 2, r"$x$", lafig.INK, 0, -0.25)
label(ax, y / 2, r"$y$", lafig.INK, -0.25, 0)
label(ax, s / 2, r"$x+y$", lafig.INK, -0.1, 0.35)

ax = axes[1]
panel(ax, "Правило треугольника")
arrow(ax, o, x, lafig.VECTOR)
arrow(ax, x, y, lafig.VECTOR)
arrow(ax, o, s, lafig.IMAGE, lw=2.6)
label(ax, x / 2, r"$x$", lafig.INK, 0, -0.25)
label(ax, x + y / 2, r"$y$", lafig.INK, 0.27, 0)
label(ax, s / 2, r"$x+y$", lafig.INK, -0.1, 0.35)

ax = axes[2]
panel(ax, "Разность")
arrow(ax, o, x, lafig.VECTOR)
arrow(ax, o, y, lafig.VECTOR)
arrow(ax, y, d, lafig.IMAGE, lw=2.6)
label(ax, x / 2, r"$x$", lafig.INK, 0, -0.25)
label(ax, y / 2, r"$y$", lafig.INK, -0.25, 0)
label(ax, y + d / 2, r"$x-y$", lafig.INK, 0.05, 0.3)

lafig.save(fig, 2, "vector_sum")
