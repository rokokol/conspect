"""One step of Gram-Schmidt in R^2: h2 is a2 minus its projection on h1 = a1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

a1 = np.array([3.4, 0.9])
a2 = np.array([1.1, 2.3])
h1 = a1
x21 = -(a2 @ h1) / (h1 @ h1)
p = -x21 * h1
h2 = x21 * h1 + a2
assert np.isclose(h1 @ h2, 0)
assert np.allclose(h2, a2 - p)


def arrow(ax, start, vec, color, lw=2.2, ls="-"):
    ax.annotate("", xy=np.add(start, vec), xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def right_angle(ax, corner, u, v, size=0.2):
    u = u / np.linalg.norm(u) * size
    v = v / np.linalg.norm(v) * size
    ax.add_patch(Polygon([corner + u, corner + u + v, corner + v], closed=False, fill=False,
                         edgecolor=lafig.INK, lw=1.2))


fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.set_xlim(-1.9, 4.9)
ax.set_ylim(-0.6, 2.7)
ax.set_aspect("equal")
ax.axis("off")

arrow(ax, (0, 0), h2, lafig.HIGHLIGHT, lw=2.4, ls=(0, (4, 3)))
arrow(ax, p, a2 - p, lafig.HIGHLIGHT, lw=2.6)
shift = np.array([h1[1], -h1[0]]) / np.linalg.norm(h1) * 0.14
arrow(ax, shift, p, lafig.AUX, lw=3.0)
arrow(ax, (0, 0), a1, lafig.VECTOR)
arrow(ax, (0, 0), a2, lafig.IMAGE)
right_angle(ax, np.array([0.0, 0.0]), h1, h2)
right_angle(ax, p, -h1, h2)

ax.text(a1[0] + 0.1, a1[1] - 0.05, r"$a^1=h^1$", color=lafig.INK, ha="left", va="top")
ax.text(a2[0] + 0.1, a2[1] + 0.1, r"$a^2$", color=lafig.INK, ha="left", va="bottom")
ax.text(p[0] / 2 + 0.25, p[1] / 2 - 0.45, r"$-x_{2,1}h^1=\dfrac{(a^2,h^1)}{(h^1,h^1)}h^1$",
        color=lafig.INK, ha="center", va="center")
ax.text(h2[0] / 2 - 0.12, h2[1] / 2 + 0.1, r"$h^2=a^2+x_{2,1}h^1$" "\nот начала (пунктир)",
        color=lafig.INK, ha="right", va="center")
mid = p + (a2 - p) / 2
ax.text(mid[0] + 0.12, mid[1] - 0.15, r"то же $h^2$," "\nперенесённый (сплошная)",
        color=lafig.INK, ha="left", va="center")

lafig.save(fig, 7, "gram_schmidt")
