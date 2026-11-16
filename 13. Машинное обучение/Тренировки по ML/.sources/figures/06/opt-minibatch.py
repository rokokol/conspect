"""Mini-batch noise: SGD paths on the MSE surface of a line fit at four batch sizes, and the size of the gradient error by batch size.

Data: y = 2x + 1 + N(0, 1), 500 points. Parameters (slope w, intercept b). Left: the same start, step size and
number of steps, batch of 1, 8, 64 and all 500 points. Right: the root mean square distance between the
gradient of a random batch and the full gradient at the start, over 4000 batches per size, with the line
proportional to k^(-1/2). The step size is 0.05, a value inside the stability bound 2/lambda_max of the
full-batch loss (printed), not a tuned one: the picture compares batch sizes at one step.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402

OUT = fk.attachments(6)
rng = np.random.default_rng(fk.SEED)
N = 500
x = rng.normal(0, 1, N)
y = 2 * x + 1 + rng.normal(0, 1, N)
D = np.c_[x, np.ones(N)]  # columns: slope, intercept
LR, STEPS = 0.05, 120
START = np.array([-0.6, -1.0])
K = [1, 8, 64, N]
COLORS = {1: fk.P["bow"], 8: fk.P["sayori-eye"], 64: fk.P["monika-eye"], N: fk.P["ink"]}


def grad(p, idx):
    r = D[idx] @ p - y[idx]
    return 2 * D[idx].T @ r / len(idx)


def full_loss(p):
    p = np.asarray(p, float)
    return np.mean((np.tensordot(p, D.T, axes=([-1], [0])) - y) ** 2, axis=-1)


lam_max = np.linalg.eigvalsh(2 * D.T @ D / N).max()
print(f"lambda_max {lam_max:.3f}, stability bound 2/lambda_max = {2 / lam_max:.3f}, step {LR}")
assert LR < 2 / lam_max

paths = {}
for k in K:
    r = np.random.default_rng(fk.SEED + 1)
    p = START.copy()
    pts = [p]
    for _ in range(STEPS):
        idx = r.choice(N, k, replace=False)
        p = p - LR * grad(p, idx)
        pts.append(p)
    paths[k] = np.array(pts)

w_opt = np.linalg.lstsq(D, y, rcond=None)[0]
print("least squares:", np.round(w_opt, 3))

gw, gb = np.meshgrid(np.linspace(-1, 3, 200), np.linspace(-1.5, 2.5, 200))
Z = full_loss(np.stack([gw, gb], axis=-1))

fig, axes = fk.subplots(1, 2, size=(10.6, 4.2), gridspec_kw={"width_ratios": [1.1, 1]})
ax = axes[0]
fk.loss_contourf(ax, gw, gb, Z, n=12)
for k in K:
    p = paths[k]
    ax.plot(p[:, 0], p[:, 1], color=COLORS[k], lw=1.5, label="весь набор, $k=500$" if k == N else f"$k={k}$")
ax.scatter(*START, s=50, color=fk.P["paper"], edgecolor=fk.TEXT, zorder=6)
ax.plot(*w_opt, marker="x", color=fk.TEXT, ms=9, mew=2, zorder=6)
ax.set_xlabel("наклон $w$")
ax.set_ylabel("сдвиг $b$")
ax.set_title(f"SGD, {STEPS} шагов")
ax.legend(loc="lower right", fontsize=8)

ax = axes[1]
ks = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256])
g_full = grad(START, np.arange(N))
err = []
for k in ks:
    r = np.random.default_rng(fk.SEED + 2)
    d = [np.sum((grad(START, r.choice(N, k, replace=False)) - g_full) ** 2) for _ in range(4000)]
    err.append(np.sqrt(np.mean(d)))
err = np.array(err)
ax.plot(ks, err, color=fk.MODEL_C, marker="o", ms=5, lw=2, label="измерено")
ax.plot(ks, err[0] / np.sqrt(ks), color=fk.TEXT_2, ls="--", lw=1.4, label="$\\propto k^{-1/2}$")
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xlabel("размер батча $k$")
ax.set_ylabel("ошибка градиента")
ax.set_title("Шум градиента по размеру батча")
ax.grid(True, axis="y")
ax.legend()
fig.tight_layout()
fk.save(fig, OUT / "opt-minibatch.png")
print("gradient error by k:", dict(zip(ks.tolist(), np.round(err, 3).tolist())))
