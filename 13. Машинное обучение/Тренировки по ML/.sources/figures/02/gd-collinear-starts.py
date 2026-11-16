"""Gradient descent on the MSE valley of two identical features: each start ends at its own point of the floor."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# Same data as linreg-mse-landscape.py, right panel: x2 is a copy of x1
rng = np.random.default_rng(fk.SEED)
n = 60
x1 = rng.normal(0, 1, n)
rng.normal(0, 1, n)  # the independent x2 of the left panel, drawn to keep the noise identical
noise = rng.normal(0, 0.3, n)
x2 = x1
y = x1 + x2 + noise
X = np.c_[x1, x2]

lam = np.linalg.eigvalsh(2 * X.T @ X / n)
eta = 0.3 / lam[-1]
c = (x1 @ y) / (x1 @ x1)  # the floor is the line w1 + w2 = c

STARTS = np.array([[0.0, 0.0], [-2.4, -2.0], [-1.0, 4.6], [4.6, 0.4]])
ends = []
paths = []
for w0 in STARTS:
    w = w0.copy()
    p = [w.copy()]
    for _ in range(400):
        w = w - eta * 2 * X.T @ (X @ w - y) / n
        p.append(w.copy())
    paths.append(np.array(p))
    ends.append(w)
ends = np.array(ends)

# GD moves only along (1, 1), so each start lands on the orthogonal projection of itself onto the floor
proj = STARTS + ((c - STARTS.sum(1)) / 2)[:, None] * np.array([1.0, 1.0])
assert np.abs(ends - proj).max() < 1e-6
assert np.abs(ends[0] - c / 2).max() < 1e-6  # from zero: the minimum-norm solution

w1g, w2g = np.meshgrid(np.linspace(-3, 5, 300), np.linspace(-3, 5, 300))
Z = ((y - (w1g[..., None] * x1 + w2g[..., None] * x2)) ** 2).mean(-1)

fig, ax = fk.subplots(1, 1, size=(5.6, 4.6))
fk.loss_contourf(ax, w1g, w2g, Z, n=12)
line = np.array([-3.0, 5.0])
ax.plot(line, c - line, color=fk.MODEL2_C, lw=2.2, zorder=3, label=f"дно: $w_1+w_2={fk.num(c, 2, math=True)}$")
for p, e in zip(paths, ends):
    ax.plot(p[:, 0], p[:, 1], color=fk.TEXT, lw=1.2, zorder=4)
    ax.scatter(*p[0], s=34, color=fk.TEXT, edgecolor="white", zorder=5)
    ax.scatter(*e, s=60, color=fk.MODEL_C, edgecolor="white", zorder=6)
ax.scatter([], [], s=34, color=fk.TEXT, edgecolor="white", label="старты")
ax.scatter([], [], s=60, color=fk.MODEL_C, edgecolor="white", label="где остановился спуск")
ax.set_xlim(-3, 5)
ax.set_ylim(-3, 5)
ax.set_aspect("equal")
ax.set_xlabel("$w_1$")
ax.set_ylabel("$w_2$")
ax.set_title("$x_2$ — копия $x_1$")
ax.legend(loc="upper right")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "gd-collinear-starts.png")
print(f"c={c:.4f}, ends={ends.round(3).tolist()}")
