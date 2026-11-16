"""AdaBoost on moons, circles and xor: rows are the data sets, columns are 1, 10 and 100 stumps and 100 trees of depth 2; the split of every set is the same as for the tree and the forest."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import AdaBoostClassifier  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

DATA = ["moons", "circles", "xor"]
COLUMNS = [(1, 1), (1, 10), (1, 100), (2, 100)]  # (depth of the base tree, number of trees)


def make(depth, n):
    return AdaBoostClassifier(DecisionTreeClassifier(max_depth=depth, random_state=fk.SEED), n_estimators=n,
                              random_state=fk.SEED)


fig, axes = fk.subplots(len(DATA), len(COLUMNS), size=(13.2, 9.6))
for i, name in enumerate(DATA):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for j, (depth, n) in enumerate(COLUMNS):
        m = make(depth, n).fit(Xtr, ytr)
        fk.plot_decision(axes[i, j], m, Xtr, ytr, X_test=Xte, y_test=yte)
        if i == 0:
            axes[i, j].set_title(f"{'пни' if depth == 1 else 'деревья глубины 2'}, T = {n}")
        if j == 0:
            axes[i, j].set_ylabel(name)
        print(name, "depth", depth, "T", n, "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
fig.tight_layout()
fk.save(fig, fk.attachments(5) / "ada-zones-datasets.png")

# A sum of stumps is additive in the features: a check of the reasoning in the note on the exponential loss and the xor.
X, y = fk.dataset("xor")
Xtr, Xte, ytr, yte = fk.split(X, y)
m = make(1, 100).fit(Xtr, ytr)
a = np.linspace(-1.5, 1.5, 31)
grid = np.array([[u, v] for u in a for v in a])
F = m.decision_function(grid).reshape(31, 31)
# For an additive F(u, v) = g(u) + h(v) the mixed second difference vanishes.
mixed = F[1:, 1:] - F[1:, :-1] - F[:-1, 1:] + F[:-1, :-1]
print("max |mixed difference| of the 100-stump score on xor:", float(np.abs(mixed).max()))
