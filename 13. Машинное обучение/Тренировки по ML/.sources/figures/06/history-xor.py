"""AND, OR and XOR on {0,1}^2, and XOR made separable by the extra feature x1*x2 (lecture 6, slide 5)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

PTS = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
TARGETS = {"AND": [0, 0, 0, 1], "OR": [0, 1, 1, 1], "XOR": [0, 1, 1, 0]}
LINES = {"AND": (1, 1, 1.5), "OR": (1, 1, 0.5)}  # a*x1 + b*x2 = c

fig = fk.plt.figure(figsize=(13.2, 3.5))
for i, (name, y) in enumerate(TARGETS.items()):
    ax = fig.add_subplot(1, 4, i + 1)
    for p, c in zip(PTS, y):
        ax.scatter(*p, s=260, color=fk.CLASS_COLORS[c], edgecolors=fk.TEXT, linewidths=1.2, zorder=3)
    if name in LINES:
        a, b, c = LINES[name]
        xs = np.linspace(-0.4, 1.4, 2)
        ax.plot(xs, (c - a * xs) / b, color=fk.ACCENT, lw=1.6)
        verdict = "одна прямая делит"
    else:
        verdict = "ни одна прямая не делит"
    ax.set_xlim(-0.4, 1.4)
    ax.set_ylim(-0.4, 1.4)
    ax.set_aspect("equal")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.set_title(f"{name}: {verdict}", fontsize=10)

ax = fig.add_subplot(1, 4, 4, projection="3d")
y = TARGETS["XOR"]
for p, c in zip(PTS, y):
    ax.scatter(p[0], p[1], p[0] * p[1], s=120, color=fk.CLASS_COLORS[c], edgecolors=fk.TEXT, linewidths=1.0,
               depthshade=False)
gx, gy = np.meshgrid(np.linspace(-0.1, 1.1, 10), np.linspace(-0.1, 1.1, 10))
ax.plot_surface(gx, gy, (gx + gy - 0.5) / 2, color=fk.ACCENT, alpha=0.18, linewidth=0)
ax.set_xlabel("x₁")
ax.set_ylabel("x₂")
ax.set_zlabel("x₁x₂")
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_zticks([0, 1])
ax.set_title("XOR с признаком x₁x₂: плоскость делит", fontsize=10)

fk.save(fig, fk.attachments(6) / "history-xor.png")

# The plane x1 + x2 - 2 x1 x2 = 0.5 must separate the classes of XOR.
side = [(p[0] + p[1] - 2 * p[0] * p[1] - 0.5) > 0 for p in PTS]
assert side == [bool(c) for c in y], side
print("plane separates XOR:", side)
