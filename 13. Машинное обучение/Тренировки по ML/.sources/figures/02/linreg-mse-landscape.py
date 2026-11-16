"""MSE over two weights: a bowl with one minimum against a valley of minima when x2 copies x1."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

rng = np.random.default_rng(fk.SEED)
n = 60
x1 = rng.normal(0, 1, n)
x2_indep = rng.normal(0, 1, n)
noise = rng.normal(0, 0.3, n)

w1g, w2g = np.meshgrid(np.linspace(-3, 5, 300), np.linspace(-3, 5, 300))


def mse(x2):
    y = x1 + x2 + noise
    pred = w1g[..., None] * x1 + w2g[..., None] * x2
    return ((y - pred) ** 2).mean(-1)


fig, axes = fk.subplots(1, 2, size=(9.2, 4.2))
levels = np.array([0.2, 0.5, 1, 2, 4, 8, 16, 32])

ax = axes[0]
z = mse(x2_indep)
ax.contourf(w1g, w2g, z, levels=np.r_[0, levels, 1e9], colors=[fk.tint(fk.BLUE, a) for a in np.linspace(0.1, 0.9, len(levels) + 1)])
ax.contour(w1g, w2g, z, levels=levels, colors="white", linewidths=0.6)
ax.scatter([1], [1], color=fk.RED, s=45, zorder=4, label="единственный минимум")
ax.set_title("Признаки независимы")
ax.legend(loc="upper left")

ax = axes[1]
z = mse(x1)
ax.contourf(w1g, w2g, z, levels=np.r_[0, levels, 1e9], colors=[fk.tint(fk.BLUE, a) for a in np.linspace(0.1, 0.9, len(levels) + 1)])
ax.contour(w1g, w2g, z, levels=levels, colors="white", linewidths=0.6)
line = np.array([-3.0, 5.0])
ax.plot(line, 2 - line, color=fk.RED, lw=2.2, label="дно: $w_1+w_2=2$", zorder=3)
pts = np.array([[1, 1], [-1, 3], [3, -1]])  # pairs on the line; the lecturer's (10, -8) lies off this frame
ax.scatter(pts[:, 0], pts[:, 1], color=fk.RED, s=45, zorder=4, edgecolor="white")
ax.set_title("$x_2$ — копия $x_1$")
ax.legend(loc="upper right")

for a in axes:
    a.set_xlabel("$w_1$")
    a.set_xlim(-3, 5)
    a.set_ylim(-3, 5)
    a.set_aspect("equal")
axes[0].set_ylabel("$w_2$")
fig.tight_layout()
fk.save(fig, OUT / "linreg-mse-landscape.png")
