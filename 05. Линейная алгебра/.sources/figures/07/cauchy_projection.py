"""The proof of the Cauchy-Bunyakovsky inequality: x splits into (x, e)e and a vector orthogonal to it."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

y = np.array([3.0, 0.0])
x = np.array([2.4, 1.9])
e = y / np.linalg.norm(y)
b = (x @ e) * e
r = x - b
assert np.isclose(r @ b, 0)
assert np.isclose(x @ x, r @ r + b @ b)
assert (x @ y) ** 2 <= (x @ x) * (y @ y)


def arrow(ax, start, vec, color, lw=2.2):
    ax.annotate("", xy=np.add(start, vec), xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.set_xlim(-0.3, 4.4)
ax.set_ylim(-0.7, 2.4)
ax.set_aspect("equal")
ax.axis("off")
arrow(ax, (0, 0), y, lafig.MUTED, lw=1.6)
ax.text(y[0] + 0.1, -0.05, r"$y,\ e=y/|y|$", color=lafig.INK, ha="left", va="center")
arrow(ax, (0, 0), x, lafig.VECTOR)
ax.text(x[0] / 2 - 0.2, x[1] / 2 + 0.2, r"$x$", color=lafig.INK, ha="center", va="center")
arrow(ax, (0, 0), b, lafig.IMAGE, lw=2.6)
ax.text(b[0] / 2, -0.3, r"$(x,e)e$", color=lafig.INK, ha="center", va="center")
arrow(ax, b, r, lafig.HIGHLIGHT, lw=2.6)
ax.text(b[0] + 0.12, r[1] / 2, r"$x-(x,e)e$", color=lafig.INK, ha="left", va="center")
ax.add_patch(Rectangle(b, -0.16, 0.16, fill=False, edgecolor=lafig.MUTED, lw=1.0))

lafig.save(fig, 7, "cauchy_projection")
