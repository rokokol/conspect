"""Variance of an average of N models against N: the formula at several rho, a simulation, and real bagged trees."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

N_MAX = 100
GRID_N = [1, 2, 3, 5, 10, 20, 50, 100]
RHOS = [0.0, 0.3, 0.7, 1.0]
N_DATASETS = 400  # independent training samples drawn from the generator
N_X = 60


def theory(rho, n):
    """D of the mean of n models with variance 1 and pairwise correlation rho."""
    return rho + (1 - rho) / n


# Left: n predictions with variance 1 and pairwise correlation rho, built from one common and one own normal part.
rng = np.random.default_rng(fk.SEED)
sim = {}
for rho in RHOS:
    z0 = rng.standard_normal((20000, 1))
    z = rng.standard_normal((20000, N_MAX))
    b = np.sqrt(rho) * z0 + np.sqrt(1 - rho) * z
    sim[rho] = [float(np.var(b[:, :n].mean(1))) for n in GRID_N]

# Right: bagged full trees on the noisy sine. Each of N_DATASETS fresh training samples gets N_MAX bootstrap trees.
# At a fixed x the randomness is the draw of the data and of the bootstrap, so D and rho are over datasets.
xs = np.linspace(0.02, 0.98, N_X)[:, None]
rng_d = np.random.default_rng(fk.SEED + 7)
preds = np.empty((N_DATASETS, N_MAX, N_X))
for m in range(N_DATASETS):
    x = np.sort(rng_d.uniform(0, 1, 40))
    y = np.sin(2 * np.pi * x) + rng_d.normal(0, 0.25, 40)
    for k in range(N_MAX):
        idx = rng_d.integers(0, 40, 40)
        preds[m, k] = DecisionTreeRegressor(random_state=fk.SEED).fit(x[idx, None], y[idx]).predict(xs)

centered = preds - preds.mean(0, keepdims=True)
cov = np.einsum("mkx,mlx->xkl", centered, centered) / (N_DATASETS - 1)  # cov across datasets, per x
diag = np.einsum("xkk->xk", cov)
sigma2_x = diag.mean(1)
cov_off_x = (cov.sum((1, 2)) - diag.sum(1)) / (N_MAX * (N_MAX - 1))
sigma2, c = float(sigma2_x.mean()), float(cov_off_x.mean())
rho_hat = c / sigma2
measured = [float(np.var(preds[:, :n].mean(1), axis=0, ddof=1).mean()) for n in GRID_N]

fig, (ax1, ax2) = fk.subplots(1, 2, size=(11.6, 4.3))
ns = np.arange(1, N_MAX + 1)
cols = [fk.MODEL_C, fk.MODEL2_C, fk.TEXT_2, fk.ACCENT]
for rho, col in zip(RHOS, cols):
    ax1.plot(ns, [theory(rho, n) for n in ns], color=col, lw=1.8, label=f"ρ = {fk.num(rho, None)}")
    ax1.scatter(GRID_N, sim[rho], s=26, facecolors="white", edgecolors=col, linewidths=1.2, zorder=3)
    if rho > 0:
        ax1.axhline(rho, color=col, lw=0.7, ls=":")
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlabel("число моделей N")
ax1.set_ylabel("D(среднее) / σ²")
ax1.set_title("формула и симуляция")
handles, labels = ax1.get_legend_handles_labels()
handles += [Line2D([], [], color=fk.GRIDC, lw=2),
            Line2D([], [], color=fk.GRIDC, marker="o", ls="", mfc="white", mew=1.4, ms=5),
            Line2D([], [], color=fk.GRIDC, lw=1.2, ls=":")]
labels += ["формула", "симуляция", "предел ρσ²"]
ax1.legend(handles, labels, loc="lower left")

ax2.plot(ns, [(rho_hat + (1 - rho_hat) / n) for n in ns], color=fk.MODEL2_C, lw=1.8,
         label=f"формула при ρ = {fk.num(rho_hat, 2)}")
ax2.plot(ns, 1 / ns, color=fk.TEXT_2, lw=1.2, ls="--", label="независимые: 1/N")
ax2.scatter(GRID_N, [v / sigma2 for v in measured], s=30, facecolors="white", edgecolors=fk.MODEL_C,
            linewidths=1.4, zorder=3, label="замер на деревьях")
ax2.axhline(rho_hat, color=fk.MODEL2_C, lw=0.7, ls=":", label="предел ρσ²")
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("число деревьев N")
ax2.set_ylabel("D(среднее) / σ²")
ax2.set_title("бэггинг деревьев на синусе")
ax2.legend(loc="lower left")
fk.save(fig, fk.attachments(5) / "bag-variance-vs-n.png")

print("sigma2", round(sigma2, 4), "cov", round(c, 4), "rho_hat", round(rho_hat, 3))
for n, v in zip(GRID_N, measured):
    print(n, "measured", round(v / sigma2, 3), "formula", round(theory(rho_hat, n), 3), "indep", round(1 / n, 3))
for rho in RHOS:
    print("rho", rho, [round(v, 3) for v in sim[rho]], [round(theory(rho, n), 3) for n in GRID_N])
