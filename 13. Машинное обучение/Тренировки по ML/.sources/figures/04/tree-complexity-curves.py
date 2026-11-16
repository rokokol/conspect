"""Train/test accuracy of a tree on moons against each stopping criterion: max_depth, min_samples_leaf, min_impurity_decrease.

The marked value is chosen by 5-fold cross-validation on the train part, never by test. A second figure shows the regions for min_impurity_decrease.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.model_selection import cross_val_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)


def curves(make, values):
    train, test, val = [], [], []
    for v in values:
        m = make(v).fit(Xtr, ytr)
        train.append(m.score(Xtr, ytr))
        test.append(m.score(Xte, yte))
        val.append(cross_val_score(make(v), Xtr, ytr, cv=5).mean())
    return train, test, val


specs = [
    ("max_depth", list(range(1, 13)), lambda v: DecisionTreeClassifier(max_depth=v, random_state=fk.SEED), False),
    ("min_samples_leaf", [1, 2, 3, 5, 8, 12, 20, 30, 45, 70],
     lambda v: DecisionTreeClassifier(min_samples_leaf=v, random_state=fk.SEED), False),
    ("min_impurity_decrease", [0, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05],
     lambda v: DecisionTreeClassifier(min_impurity_decrease=v, random_state=fk.SEED), False),
]

fig, axes = fk.subplots(1, 3, size=(13.2, 3.7))
for ax, (name, values, make, log) in zip(axes, specs):
    train, test, val = curves(make, values)
    xs = list(range(len(values))) if name == "min_impurity_decrease" else values
    b = fk.complexity_curve(ax, xs, train, test, xlabel=name, ylabel="accuracy", val=val, log=log)
    if name == "min_impurity_decrease":
        ax.set_xticks(xs, [fk.num(v, None) for v in values], rotation=45, fontsize=7)
    ax.set_ylim(0.6, 1.02)
    ax.set_title("глубина" if name == "max_depth" else "размер листа" if name == "min_samples_leaf"
                 else "минимальный прирост")
    print(name, "CV choice:", values[b], "cv:", [round(v, 3) for v in val], "test:", [round(t, 3) for t in test])
axes[1].set_ylabel("")
axes[2].set_ylabel("")
fk.save(fig, fk.attachments(4) / "tree-complexity-moons.png")

IMPS = [0, 0.002, 0.01, 0.05]
fig, _ = fk.model_grid(lambda r, c: DecisionTreeClassifier(min_impurity_decrease=c, random_state=fk.SEED),
                       [0], IMPS, "moons", col_label=lambda c: f"min_impurity_decrease = {fk.num(c, None)}",
                       size=(12.4, 3.3))
fk.save(fig, fk.attachments(4) / "tree-impurity-grid.png")
print("leaves:", [DecisionTreeClassifier(min_impurity_decrease=c, random_state=fk.SEED).fit(Xtr, ytr).get_n_leaves()
                  for c in IMPS])
