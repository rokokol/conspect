"""Correlation with the target against permutation importance when one feature acts through its square.

y = a^2 + 0.6 b + noise. Correlation is computed on the train part. A forest regressor (leaf size by 5-fold CV on the train
part) is scored with R^2, and permutation importance is the drop of R^2 over 30 shuffles of the held-out part.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
n = 800
a, b, c = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)
y = a**2 + 0.6 * b + rng.normal(0, 0.3, n)
X = np.column_stack([a, b, c])
Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.3, random_state=fk.SEED)

grid = GridSearchCV(RandomForestRegressor(n_estimators=200, random_state=fk.SEED, n_jobs=-1),
                    {"min_samples_leaf": [1, 5, 20]}, cv=5).fit(Xtr, ytr)
m = grid.best_estimator_
perm = permutation_importance(m, Xva, yva, n_repeats=30, random_state=fk.SEED)
corr = np.array([abs(np.corrcoef(Xtr[:, j], ytr)[0, 1]) for j in range(3)])

LABELS = ["a (в квадрате)", "b (линейно)", "c (шум)"]
fig, axes = fk.subplots(1, 3, size=(11.6, 3.6), gridspec_kw={"width_ratios": [1, 1, 1.1]})
for ax, j, title in ((axes[0], 0, "$y$ против $a$"), (axes[1], 1, "$y$ против $b$")):
    ax.scatter(Xtr[:, j], ytr, s=9, color=fk.TRAIN_C, alpha=0.55, edgecolor="none")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("признак")
    ax.grid(True)
axes[0].set_ylabel("$y$")
ax = axes[2]
xs = np.arange(3)
ax.bar(xs - 0.2, corr, 0.4, color=fk.P["ash"], label="|корреляция| с $y$ (обучающая часть)")
ax.bar(xs + 0.2, perm.importances_mean, 0.4, yerr=perm.importances_std, color=fk.CATEGORICAL[0],
       error_kw=dict(ecolor=fk.TEXT, lw=1, capsize=3), label="permutation: падение $R^2$ (отложенная)")
ax.set_xticks(xs, LABELS, fontsize=8)
ax.legend(fontsize=6.5, loc="upper right")
ax.set_ylim(-0.08, 1.9)
ax.grid(True, axis="y")
ax.set_title("Две меры одного признака", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "perm-vs-correlation.png")

print("leaf", grid.best_params_, "held-out R2", round(m.score(Xva, yva), 3))
print("corr", np.round(corr, 3), "perm", np.round(perm.importances_mean, 3), "+-", np.round(perm.importances_std, 3))
z = rng.normal(size=100000)
print("corr(z, z^3) on N(0,1):", round(float(np.corrcoef(z, z**3)[0, 1]), 3),
      " on U(-1,1):", round(float(np.corrcoef(u := rng.uniform(-1, 1, 100000), u**3)[0, 1]), 3))
