"""Post-pruning on moons: the full tree is cut back by sklearn's minimal cost-complexity pruning (ccp_alpha).

Accuracy against the number of leaves that remain; the chosen size comes from 5-fold CV on the train part.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.model_selection import cross_val_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)

full = DecisionTreeClassifier(random_state=fk.SEED).fit(Xtr, ytr)
alphas = full.cost_complexity_pruning_path(Xtr, ytr).ccp_alphas

by_leaves = {}  # number of leaves -> the largest alpha that still gives it
for a in alphas:
    m = DecisionTreeClassifier(random_state=fk.SEED, ccp_alpha=a).fit(Xtr, ytr)
    by_leaves[m.get_n_leaves()] = a
leaves = sorted(by_leaves)

train, test, val = [], [], []
for n in leaves:
    a = by_leaves[n]
    m = DecisionTreeClassifier(random_state=fk.SEED, ccp_alpha=a).fit(Xtr, ytr)
    train.append(m.score(Xtr, ytr))
    test.append(m.score(Xte, yte))
    val.append(cross_val_score(DecisionTreeClassifier(random_state=fk.SEED, ccp_alpha=a), Xtr, ytr, cv=5).mean())

fig, ax = fk.subplots(1, 1, size=(6.6, 3.8))
b = fk.complexity_curve(ax, leaves, train, test, xlabel="число листьев после усечения", ylabel="accuracy", val=val)
ax.invert_xaxis()
ax.set_title("Усечение от полного дерева")
fk.save(fig, fk.attachments(4) / "tree-pruning-path.png")

print("leaves:", leaves)
print("full tree leaves:", full.get_n_leaves())
print("CV choice:", leaves[b], "test at choice:", round(test[b], 3), "train:", round(train[b], 3))
print("train:", [round(v, 3) for v in train])
print("test:", [round(v, 3) for v in test])
print("cv:", [round(v, 3) for v in val])
