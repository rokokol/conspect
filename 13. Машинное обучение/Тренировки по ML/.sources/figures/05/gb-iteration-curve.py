"""MSE of gradient boosting against the number of trees M on cos x + noise: train, 5-fold validation on the train part, test.

One ensemble of 400 trees is grown; the value at M is the staged prediction of its first M trees. M is chosen on the validation curve only,
and the test curve is drawn to show the result of that choice. The noise variance 0.2 is the floor of any MSE.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from boost_common import ods_cos  # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor  # noqa: E402
from sklearn.model_selection import KFold, train_test_split  # noqa: E402

import figkit as fk  # noqa: E402

M_MAX = 400
GRID = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 400]
PARAMS = dict(learning_rate=0.3, max_depth=4, random_state=fk.SEED)


def staged_mse(model, X, y):
    return np.array([np.mean((y - p) ** 2) for p in model.staged_predict(X)])


X, y = ods_cos(n=240)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=fk.SEED)
full = GradientBoostingRegressor(n_estimators=M_MAX, **PARAMS).fit(Xtr, ytr)
train, test = staged_mse(full, Xtr, ytr), staged_mse(full, Xte, yte)
folds = []
for fit_idx, val_idx in KFold(5, shuffle=True, random_state=fk.SEED).split(Xtr):
    m = GradientBoostingRegressor(n_estimators=M_MAX, **PARAMS).fit(Xtr[fit_idx], ytr[fit_idx])
    folds.append(staged_mse(m, Xtr[val_idx], ytr[val_idx]))
val = np.mean(folds, axis=0)

idx = [m - 1 for m in GRID]
fig, ax = fk.subplots(1, 1, size=(6.6, 4.2))
best = fk.complexity_curve(ax, GRID, train[idx], test[idx], xlabel="число деревьев M", ylabel="MSE", val=val[idx],
                           better="min", log=True)
ax.axhline(0.2, color=fk.TEXT_2, lw=1.4, ls="-.")
ax.text(30, 0.212, f"дисперсия шума {fk.num(0.2, None)}", fontsize=8, color=fk.TEXT_2)
ax.set_title("бустинг на cos x + шум")
ax.legend(loc="lower left")
fk.save(fig, fk.attachments(5) / "gb-iteration-curve.png")

print("M", GRID)
print("train", [round(float(v), 3) for v in train[idx]])
print("val  ", [round(float(v), 3) for v in val[idx]])
print("test ", [round(float(v), 3) for v in test[idx]])
print("chosen by validation: M =", GRID[best], "val", round(float(val[idx][best]), 3), "test", round(float(test[idx][best]), 3))
print("test at M = 400:", round(float(test[-1]), 3), "; best test over all M (not used):", int(np.argmin(test)) + 1, round(float(test.min()), 3))

es = GradientBoostingRegressor(n_estimators=M_MAX, n_iter_no_change=10, validation_fraction=0.2, **PARAMS).fit(Xtr, ytr)
print("sklearn early stopping (10 rounds without gain on 20% of train) stopped at", es.n_estimators_, "trees")
