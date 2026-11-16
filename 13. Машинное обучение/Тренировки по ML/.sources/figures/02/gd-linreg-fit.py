"""Gradient descent on the MSE of a line fit: its path in the weight plane and the lines it passes through, against the analytic answer."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# Same cloud as linreg-line-residuals.py
rng = np.random.default_rng(fk.SEED)
x = rng.uniform(0.5, 5.5, 14)
y = 1.2 + 0.7 * x + rng.normal(0, 0.55, x.size)
X = np.c_[np.ones_like(x), x]
n = len(x)

w_star = np.linalg.solve(X.T @ X, X.T @ y)
lam = np.linalg.eigvalsh(2 * X.T @ X / n)
eta = 1 / lam[-1]  # below the stability bound 2/lambda_max
SHOWN = [0, 10, 50, 200, 1000]

w = np.zeros(2)
path = [w.copy()]
for _ in range(max(SHOWN)):
    w = w - eta * 2 * X.T @ (X @ w - y) / n
    path.append(w.copy())
path = np.array(path)
assert np.abs(path[-1] - w_star).max() < 1e-6, "GD did not reach the normal-equation solution"


def mse(w0, w1):
    return ((y[None, None, :] - w0[..., None] - w1[..., None] * x) ** 2).mean(-1)


g0, g1 = np.meshgrid(np.linspace(-0.6, 2.2, 260), np.linspace(-0.2, 1.2, 260))
Z = mse(g0, g1)

fig, axes = fk.subplots(1, 2, size=(10.2, 4.0))

ax = axes[0]
fk.loss_contourf(ax, g0, g1, Z, n=12)
ax.plot(path[:, 0], path[:, 1], color=fk.MODEL_C, lw=1.4, zorder=3)
# Steps 200 and 1000 sit under the cross: the path has reached the solution by then
LABELLED = [10, 50]
ax.scatter(path[LABELLED, 0], path[LABELLED, 1], s=30, color=fk.MODEL_C, edgecolor="white", zorder=4)
for k in LABELLED:
    ax.annotate(f"{k}", path[k], xytext=(5, 5), textcoords="offset points", fontsize=8, color=fk.TEXT)
ax.scatter(*path[0], s=46, color=fk.MODEL2_C, edgecolor="white", zorder=5, label="старт $w=0$")
ax.plot(*w_star, marker="x", color=fk.TEXT, ms=9, mew=2, ls="none", zorder=5, label="нормальное уравнение")
ax.set_xlabel("$w_0$")
ax.set_ylabel("$w_1$")
ax.set_title("Путь по весам")
ax.legend(loc="upper right")

ax = axes[1]
t = np.array([0.0, 6.0])
shades = [fk.tint(fk.MODEL_C, a) for a in np.linspace(0.6, 0.0, len(SHOWN))]
for k, c in zip(SHOWN, shades):
    ax.plot(t, path[k, 0] + path[k, 1] * t, color=c, lw=1.6, label=f"шаг {k}")
ax.plot(t, w_star[0] + w_star[1] * t, color=fk.MODEL2_C, lw=1.4, ls="--", label="МНК")
ax.scatter(x, y, s=26, color=fk.TEXT_2, edgecolor="white", zorder=3)
ax.set_xlim(0, 6)
ax.set_xlabel("признак $x$")
ax.set_ylabel("целевая переменная $y$")
ax.set_title("Прямые по ходу спуска")
ax.grid(True)
ax.legend(loc="lower right", ncol=2)

fig.tight_layout()
fk.save(fig, fk.attachments(2) / "gd-linreg-fit.png")
print(f"eigenvalues {lam}, kappa {lam[-1] / lam[0]:.1f}, eta {eta:.4f}, w* {w_star}")
