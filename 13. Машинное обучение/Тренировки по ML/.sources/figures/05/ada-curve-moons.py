"""Accuracy of AdaBoost on stumps against the number of stumps T (moons): train, 5-fold validation on the train part, test.

One ensemble of 500 stumps is grown; the value at T is the staged score of its first T stumps. T is chosen on the validation curve only.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import AdaBoostClassifier  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

T_MAX = 500
GRID = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500]


def make():
    return AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=fk.SEED), n_estimators=T_MAX,
                              random_state=fk.SEED)


def staged(model, X, y):
    return np.array(list(model.staged_score(X, y)))


X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
full = make().fit(Xtr, ytr)
train, test = staged(full, Xtr, ytr), staged(full, Xte, yte)
folds = []
for fit_idx, val_idx in StratifiedKFold(5, shuffle=True, random_state=fk.SEED).split(Xtr, ytr):
    folds.append(staged(make().fit(Xtr[fit_idx], ytr[fit_idx]), Xtr[val_idx], ytr[val_idx]))
val = np.mean(folds, axis=0)

idx = [t - 1 for t in GRID]
fig, ax = fk.subplots(1, 1, size=(6.4, 4.0))
best = fk.complexity_curve(ax, GRID, train[idx], test[idx], xlabel="число пней T", ylabel="accuracy", val=val[idx],
                           better="max", log=True)
ax.set_title("AdaBoost на пнях, moons")
fk.save(fig, fk.attachments(5) / "ada-curve-moons.png")

print("T", GRID)
print("train", [round(float(v), 3) for v in train[idx]])
print("val  ", [round(float(v), 3) for v in val[idx]])
print("test ", [round(float(v), 3) for v in test[idx]])
print("chosen by validation: T =", GRID[best], "val", round(val[idx][best], 3), "test", round(test[idx][best], 3))
