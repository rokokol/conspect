"""Gradient boosting of trees of depth 2 on moons: rows are the learning rate, columns the number of trees; data and split are the same as for the tree, the bagging and the forest.

The cell that 5-fold cross-validation on the train part picks is printed; the test part is not used for the choice.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import GradientBoostingClassifier  # noqa: E402
from sklearn.model_selection import cross_val_score, StratifiedKFold  # noqa: E402

import figkit as fk  # noqa: E402

RATES = [1.0, 0.1, 0.01]
COUNTS = [1, 10, 100, 500]


def make(lr, n):
    return GradientBoostingClassifier(learning_rate=lr, n_estimators=n, max_depth=2, random_state=fk.SEED)


fig, axes = fk.model_grid(make, RATES, COUNTS, "moons", col_label=lambda n: f"деревьев: {n}",
                          row_label=lambda lr: f"η = {fk.num(lr, None)}", size=(13.2, 9.6))
fk.save(fig, fk.attachments(5) / "gb-zones-lr-trees.png")

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
cv = StratifiedKFold(5, shuffle=True, random_state=fk.SEED)
table = {}
for lr in RATES:
    for n in COUNTS:
        val = cross_val_score(make(lr, n), Xtr, ytr, cv=cv).mean()
        m = make(lr, n).fit(Xtr, ytr)
        table[(lr, n)] = (val, m.score(Xtr, ytr), m.score(Xte, yte))
        print("lr", lr, "trees", n, "cv", round(val, 3), "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
best = max(table, key=lambda k: table[k][0])
print("chosen by cross-validation:", best, "cv", round(table[best][0], 3), "test", round(table[best][2], 3))
