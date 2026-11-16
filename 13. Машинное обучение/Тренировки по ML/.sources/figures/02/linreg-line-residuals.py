"""Linear regression as a line through a cloud: vertical OLS residuals against PCA perpendiculars."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
x = rng.uniform(0.5, 5.5, 14)
y = 1.2 + 0.7 * x + rng.normal(0, 0.55, x.size)

# OLS with the dummy unit column: w = (X^T X)^-1 X^T y
X = np.c_[np.ones_like(x), x]
w0, w1 = np.linalg.solve(X.T @ X, X.T @ y)

# First principal component of the centred cloud
c = np.array([x.mean(), y.mean()])
P = np.c_[x, y] - c
_, vecs = np.linalg.eigh(P.T @ P)
d = vecs[:, -1]
if d[0] < 0:
    d = -d

fig, axes = fk.subplots(1, 2, size=(9.2, 3.9))
grid = np.array([-0.3, 6.0])

ax = axes[0]
ax.plot(grid, w0 + w1 * grid, color=fk.RED, lw=2)
for xi, yi in zip(x, y):
    ax.plot([xi, xi], [yi, w0 + w1 * xi], color=fk.TEXT_2, lw=1, ls=":")
ax.scatter(x, y, s=26, color=fk.BLUE, edgecolor="white", zorder=3)
ax.scatter([0], [w0], s=40, color=fk.RED, zorder=4)
ax.annotate("$w_0$", (0, w0), xytext=(0.9, 0.2), color=fk.RED,
            arrowprops=dict(arrowstyle="->", color=fk.RED))
ax.set_title("МНК: вертикальные остатки")

ax = axes[1]
t = np.array([-6.0, 6.0])
ax.plot(grid, w0 + w1 * grid, color=fk.RED, lw=1.2, ls="--", label="прямая МНК")
ax.plot(c[0] + t * d[0], c[1] + t * d[1], color=fk.ACCENT, lw=2, label="главная компонента")
for p in P:
    foot = c + (p @ d) * d
    ax.plot([p[0] + c[0], foot[0]], [p[1] + c[1], foot[1]], color=fk.TEXT_2, lw=1, ls=":")
ax.scatter(x, y, s=26, color=fk.BLUE, edgecolor="white", zorder=3)
ax.set_title("Главная компонента: перпендикуляры")
ax.legend(loc="lower right")

for a in axes:
    a.set_xlim(-0.3, 6)
    a.set_ylim(0, 6)
    a.set_xlabel("признак $x$")
    a.set_aspect("equal")
    a.grid(True)
axes[0].set_ylabel("целевая переменная $y$")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "linreg-line-residuals.png")
