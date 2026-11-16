"""The penalty Omega of LIME as L1: the local model on six features, two of them signal (moons) and four noise.

The black box is a random forest (leaf size by 5-fold CV on the train part). The local model is the weighted LASSO path, exact
through lars_path: the rows are centred with the weights and scaled by sqrt(w), which turns the weighted problem into an
ordinary one. Kernel width 1.5, because six dimensions push the perturbations far from the point.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import lars_path
from sklearn.model_selection import GridSearchCV

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from lime_common import kernel, sample  # noqa: E402

SIGMA, N = 1.5, 1000
X2, y = fk.dataset("moons")
rng = np.random.default_rng(fk.SEED)
X = np.c_[X2, rng.normal(size=(len(X2), 4))]
Xtr, Xte, ytr, yte = fk.split(X, y)
grid = GridSearchCV(RandomForestClassifier(200, random_state=fk.SEED, n_jobs=-1),
                    {"min_samples_leaf": [1, 5, 20]}, cv=5).fit(Xtr, ytr)
model = grid.best_estimator_
f = lambda Z: model.predict_proba(np.atleast_2d(Z))[:, 1]  # noqa: E731
x = Xte[np.argmin(np.abs(f(Xte) - 0.5))]

Z = sample(x, N, np.random.default_rng(fk.SEED))
w = kernel(Z, x, SIGMA)
t = f(Z)
D = Z - x
mu_d = np.average(D, axis=0, weights=w)
mu_t = np.average(t, weights=w)
sw = np.sqrt(w)
alphas, active, coefs = lars_path((D - mu_d) * sw[:, None], (t - mu_t) * sw, method="lasso")

names = ["$x_1$ (сигнал)", "$x_2$ (сигнал)"] + [f"шум {k}" for k in range(1, 5)]
sig = [fk.MODEL2_C, fk.MODEL_C]
fig, ax = fk.subplots(1, 1, size=(7.2, 3.8))
share = np.abs(coefs).sum(0)
share = share / share[-1]
for j in range(6):
    color = sig[j] if j < 2 else fk.TEXT_2
    ax.plot(share, coefs[j], color=color, lw=2.2 if j < 2 else 1.1, zorder=3 if j < 2 else 2,
            label=names[j] if j < 2 else ("шумовые столбцы 1–4" if j == 2 else None))
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.set_xlabel("доля $\\|w\\|_1$ от полной (слабее штраф $\\to$)")
ax.set_ylabel("коэффициент локальной модели")
ax.legend(fontsize=7, loc="upper left")
ax.grid(True)
ax.set_title("Путь локального LASSO для одного объекта", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "lime-lasso-path.png")
print("leaf", grid.best_params_, "entry order", [int(j) for j in active])
print("final coefs", np.round(coefs[:, -1], 3))
