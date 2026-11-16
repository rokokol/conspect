"""One query point: k = 1, k = 4 with a tie, k = 4 with weights 1/j (hand-placed points)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

import figkit as fk  # noqa: E402

GREEN, BLUE = fk.CATEGORICAL[2], fk.CATEGORICAL[0]

# (angle in degrees, distance, colour); sorted by distance below
POINTS = [(150, 0.8, GREEN), (20, 1.2, GREEN), (-60, 1.55, BLUE), (95, 1.9, BLUE),
          (200, 2.6, BLUE), (-120, 2.4, GREEN), (60, 2.7, GREEN), (-10, 2.9, BLUE)]
POINTS.sort(key=lambda p: p[1])
xy = np.array([[d * np.cos(np.radians(a)), d * np.sin(np.radians(a))] for a, d, _ in POINTS])
col = [c for *_, c in POINTS]
dist = np.array([p[1] for p in POINTS])

w = 1 / np.arange(1, 5)
w = w / w.sum()
p_green = w[[i for i in range(4) if col[i] == GREEN]].sum()


def base(ax, title):
    for (x, y_), c in zip(xy, col):
        ax.scatter([x], [y_], s=60, color=c, edgecolors="white", zorder=3)
    ax.scatter([0], [0], s=110, color=fk.GREY, edgecolors=fk.TEXT, zorder=4)
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)


fig, axes = fk.subplots(1, 3, size=(11.5, 3.9))

ax = axes[0]
base(ax, "k = 1: зелёный")
ax.add_patch(Circle((0, 0), dist[0] + 0.12, fill=False, ec=fk.TEXT, lw=1.2, ls="--"))
ax.plot(*zip([0, 0], xy[0]), color=fk.TEXT, lw=1.5, zorder=2)

ax = axes[1]
base(ax, "k = 4: два зелёных, два синих")
ax.add_patch(Circle((0, 0), dist[3] + 0.12, fill=False, ec=fk.TEXT, lw=1.2, ls="--"))
for i in range(4):
    ax.plot([0, xy[i, 0]], [0, xy[i, 1]], color=col[i], lw=1.8, zorder=2)
ax.text(0, -3.05, "ничья 2 : 2", ha="center", fontsize=9, color=fk.TEXT)

ax = axes[2]
base(ax, "k = 4 с весами 1/j")
ax.add_patch(Circle((0, 0), dist[3] + 0.12, fill=False, ec=fk.TEXT, lw=1.2, ls="--"))
for i in range(4):
    ax.plot([0, xy[i, 0]], [0, xy[i, 1]], color=col[i], lw=1 + 9 * w[i], zorder=2,
            solid_capstyle="round")
    u = xy[i] / dist[i]
    ax.text(*(xy[i] + 0.5 * u), f"$w_{i + 1}={fk.num(w[i], 2, math=True)}$", fontsize=8, color=fk.TEXT, zorder=6,
            ha="left" if u[0] > 0.2 else "right" if u[0] < -0.2 else "center",
            va="bottom" if u[1] > 0.2 else "top" if u[1] < -0.2 else "center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
ax.text(0, -3.05, f"P(зелёный) = {fk.num(p_green, 2)}", ha="center", fontsize=9, color=fk.TEXT)

fig.tight_layout()
fk.save(fig, fk.attachments(1) / "knn-neighbors-weights.png")
print(w, p_green)
