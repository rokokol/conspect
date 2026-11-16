"""The Gram determinant of two vectors of V3 is the squared area of their parallelogram."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Polygon, Rectangle  # noqa: E402

x = np.array([3.0, 0.0])
y = np.array([1.2, 1.8])
gram = np.array([[x @ x, x @ y], [y @ x, y @ y]])
area = abs(x[0] * y[1] - x[1] * y[0])
assert np.isclose(np.linalg.det(gram), area**2)
phi = np.degrees(np.arccos(x @ y / (np.linalg.norm(x) * np.linalg.norm(y))))


def arrow(ax, start, vec, color, lw=2.2, style="-|>"):
    ax.annotate("", xy=np.add(start, vec), xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.set_xlim(-0.3, 4.6)
ax.set_ylim(-0.6, 2.3)
ax.set_aspect("equal")
ax.axis("off")
ax.add_patch(Polygon([(0, 0), x, x + y, y], closed=True, facecolor=lafig.tint(lafig.VECTOR, 0.88),
                     edgecolor=lafig.AUX, lw=1.2))
ax.plot([y[0], y[0]], [0, y[1]], ls=":", color=lafig.HIGHLIGHT, lw=1.6)
ax.add_patch(Rectangle((y[0], 0), -0.15, 0.15, fill=False, edgecolor=lafig.MUTED, lw=1.0))
arrow(ax, (0, 0), x, lafig.VECTOR)
arrow(ax, (0, 0), y, lafig.IMAGE)
ax.text(x[0] / 2, -0.25, r"$x$", color=lafig.INK, ha="center", va="center")
ax.text(y[0] / 2 - 0.2, y[1] / 2 + 0.1, r"$y$", color=lafig.INK, ha="center", va="center")
ax.text(y[0] + 0.12, y[1] / 2, r"$|y|\sin\varphi$", color=lafig.INK, ha="left", va="center")
ax.add_patch(Arc((0, 0), 1.0, 1.0, theta1=0, theta2=phi, color=lafig.HIGHLIGHT, lw=1.6))
ax.text(0.68, 0.2, r"$\varphi$", color=lafig.HIGHLIGHT, ha="center", va="center")
ax.text(x[0] / 2 + y[0] / 2 + 0.3, y[1] / 2, r"$S$", color=lafig.INK, ha="center", va="center")

lafig.save(fig, 7, "gram_area")
