"""What max_features does to a forest on Friedman #1 (5 useful and 5 noise features): correlation of trees, their variance, the forest error.

At a fixed point x the randomness is the draw of the training sample plus the forest's own randomness, so sigma^2 and rho
are measured over many independently drawn training samples, as in the formula D = rho sigma^2 + (1 - rho) sigma^2 / N.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.datasets import make_friedman1  # noqa: E402
from sklearn.ensemble import RandomForestRegressor  # noqa: E402

import figkit as fk  # noqa: E402

FEATURES = [1, 2, 3, 5, 7, 10]
N_TREES = 100
N_DATASETS = 60
N_TRAIN = 200
N_X = 50


def friedman_f(X):
    return 10 * np.sin(np.pi * X[:, 0] * X[:, 1]) + 20 * (X[:, 2] - 0.5) ** 2 + 10 * X[:, 3] + 5 * X[:, 4]


# The noise-free function is checked against the generator, so "true" below means the real Friedman #1 signal.
Xchk, ychk = make_friedman1(50, n_features=10, noise=0.0, random_state=fk.SEED)
assert np.allclose(friedman_f(Xchk), ychk)

Xs, _ = make_friedman1(N_X, n_features=10, noise=0.0, random_state=fk.SEED + 999)
fs = friedman_f(Xs)

rho_hat, sigma2, forest_var, bias2, total = [], [], [], [], []
for mf in FEATURES:
    preds = np.empty((N_DATASETS, N_TREES, N_X))
    for m in range(N_DATASETS):
        X, y = make_friedman1(N_TRAIN, n_features=10, noise=1.0, random_state=fk.SEED + 1 + m)
        rf = RandomForestRegressor(n_estimators=N_TREES, max_features=mf, random_state=fk.SEED + m).fit(X, y)
        preds[m] = np.array([t.predict(Xs) for t in rf.estimators_])
    centered = preds - preds.mean(0, keepdims=True)
    cov = np.einsum("mkx,mlx->xkl", centered, centered) / (N_DATASETS - 1)
    diag = np.einsum("xkk->xk", cov)
    s2 = float(diag.mean())
    c = float((cov.sum((1, 2)) - diag.sum(1)).mean() / (N_TREES * (N_TREES - 1)))
    avg = preds.mean(1)  # forest prediction per dataset and point
    fv = float(avg.var(0, ddof=1).mean())
    b2 = float(((avg.mean(0) - fs) ** 2).mean())
    sigma2.append(s2)
    rho_hat.append(c / s2)
    forest_var.append(fv)
    bias2.append(b2)
    total.append(float(((avg - fs) ** 2).mean()))
    print("max_features", mf, "sigma2", round(s2, 3), "rho", round(c / s2, 3),
          "forest var", round(fv, 3), "formula", round(c + (s2 - c) / N_TREES, 3),
          "bias2", round(b2, 3), "mse vs f", round(total[-1], 3))

fig, (ax1, ax2) = fk.subplots(1, 2, size=(11.6, 4.0))
ax1.plot(FEATURES, rho_hat, color=fk.MODEL_C, marker="o", ms=5, lw=1.8)
ax1.set_xlabel("max_features")
ax1.set_ylabel("корреляция деревьев ρ")
ax1.set_title("корреляция деревьев")
ax1.set_xticks(FEATURES)
ax1.set_ylim(0, 0.13)
ax1.grid(True, axis="y")
ax1.text(0.03, 0.95, "max_features = 10 — это бэггинг", transform=ax1.transAxes, ha="left", va="top",
         fontsize=8, color=fk.TEXT)

ax2.plot(FEATURES, sigma2, color=fk.MODEL2_C, marker="s", ms=4, lw=1.6, label="дисперсия одного дерева σ²")
ax2.plot(FEATURES, forest_var, color=fk.MODEL_C, marker="o", ms=4, lw=1.6, label=f"дисперсия леса из {N_TREES}")
ax2.plot(FEATURES, bias2, color=fk.TEXT_2, marker="^", ms=4, lw=1.4, ls=":", label="смещение² леса")
ax2.plot(FEATURES, total, color=fk.ACCENT, marker="D", ms=4, lw=1.8, label="MSE леса = смещение² + дисперсия")
ax2.set_xlabel("max_features")
ax2.set_ylabel("квадрат единиц y")
ax2.set_title("дисперсия и смещение")
ax2.set_xticks(FEATURES)
ax2.grid(True, axis="y")
ax2.set_ylim(0, 31)
ax2.legend(loc="upper right")
fk.save(fig, fk.attachments(5) / "rf-max-features-corr.png")
