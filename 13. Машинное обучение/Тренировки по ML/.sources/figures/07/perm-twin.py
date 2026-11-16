"""A column and its exact copy: how impurity, permutation and drop-column importance react.

Same table as in perm-three-methods, same split, same forest settings (leaf size 20, the one chosen there by CV); the only change is one extra column,
a copy of x1. Impurity importance is read on the train part, the other two on the held-out part.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imp_common as ic  # noqa: E402

import figkit as fk  # noqa: E402

names, X, y = ic.table()
Xtr, Xva, ytr, yva = ic.held_out(X, y)
_, LEAF = ic.forest(Xtr, ytr)


def make():
    return RandomForestClassifier(n_estimators=ic.N_FOREST, min_samples_leaf=LEAF, random_state=fk.SEED, n_jobs=-1)


def three(Xa, Xb):
    m = make().fit(Xa, ytr)
    base = m.score(Xb, yva)
    perm = permutation_importance(m, Xb, yva, n_repeats=30, random_state=fk.SEED).importances_mean
    return m.feature_importances_, perm, ic.drop_column(make, Xa, ytr, Xb, yva, base), base


alone = three(Xtr, Xva)
Xtr2, Xva2 = np.column_stack([Xtr, Xtr[:, 0]]), np.column_stack([Xva, Xva[:, 0]])
twin = three(Xtr2, Xva2)

LABELS = ["x1", "x2", "flag", "noise_num", "noise_cat", "x1_copy"]
# plotting order: x1, x1_copy, x2, flag, noises
order = [0, 5, 1, 2, 3, 4]
fig, axes = fk.subplots(1, 3, size=(11.8, 3.9))
titles = ["impurity: обучающая часть", "permutation: отложенная часть", "drop column: отложенная часть"]
w = 0.38
for ax, k, title in zip(axes, range(3), titles):
    a = np.full(6, np.nan)
    a[:5] = alone[k]
    b = twin[k]
    xs = np.arange(6)
    ax.bar(xs - w / 2, a[order], w, color=fk.P["ash"], label="без копии")
    ax.bar(xs + w / 2, b[order], w, color=fk.MODEL2_C, label="с копией x1")
    ax.axhline(0, color=fk.TEXT_2, lw=0.8)
    ax.set_xticks(xs, [LABELS[i] for i in order], fontsize=7, rotation=30)
    ax.set_title(title, fontsize=9, pad=8)
    ax.grid(True, axis="y")
    ax.margins(y=0.1)
axes[0].set_ylabel("важность")
axes[0].legend(loc="upper right", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "perm-twin.png")

print("leaf", LEAF, "held-out accuracy alone/twin", round(alone[3], 3), round(twin[3], 3))
for nm, i in (("impurity", 0), ("permutation", 1), ("drop", 2)):
    print(nm, "alone", np.round(alone[i], 3), "twin", np.round(twin[i], 3), "x1+copy", round(twin[i][0] + twin[i][5], 3))
