"""One forest, one table, three importances: impurity (train part), permutation and drop column (held-out part).

The leaf size of the forest is chosen by 5-fold CV on the train part. Permutation: 30 shuffles of each column of the
held-out part. Drop column: retrain without the column on the train part and score on the held-out part; one refit per column.
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imp_common as ic  # noqa: E402

import figkit as fk  # noqa: E402

names, X, y = ic.table()
Xtr, Xva, ytr, yva = ic.held_out(X, y)
m, leaf = ic.forest(Xtr, ytr)
base = m.score(Xva, yva)
perm = permutation_importance(m, Xva, yva, n_repeats=30, random_state=fk.SEED)


def make():
    return RandomForestClassifier(n_estimators=ic.N_FOREST, min_samples_leaf=leaf, random_state=fk.SEED, n_jobs=-1)


drop = ic.drop_column(make, Xtr, ytr, Xva, yva, base)

LABELS = ["x1", "x2", "flag", "noise_num", "noise_cat"]
COLORS = [fk.CATEGORICAL[0]] * 3 + [fk.CATEGORICAL[1]] * 2
fig, axes = fk.subplots(1, 3, size=(11.6, 3.7))
panels = [(m.feature_importances_, None, "impurity: обучающая часть", "доля суммарного прироста"),
          (perm.importances_mean, perm.importances_std, "permutation: отложенная часть", "падение accuracy"),
          (drop, None, "drop column: отложенная часть", "падение accuracy")]
for ax, (vals, err, title, ylabel) in zip(axes, panels):
    ax.bar(range(5), vals, yerr=err, color=COLORS, error_kw=dict(ecolor=fk.TEXT, lw=1, capsize=3))
    ax.axhline(0, color=fk.TEXT_2, lw=0.8)
    ax.set_xticks(range(5), LABELS, fontsize=7, rotation=30)
    ax.set_title(title, fontsize=9, pad=10)
    ax.margins(y=0.16)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y")
    for i, v in enumerate(vals):
        label = fk.num(0.0, 2) if abs(v) < 0.005 else fk.num(v, 2)
        ax.text(i, max(v, 0) + (0 if err is None else err[i]) + 0.008, label, ha="center", fontsize=7)
axes[0].legend(handles=[Patch(color=fk.CATEGORICAL[0], label="сигнал"), Patch(color=fk.CATEGORICAL[1], label="шум")],
               loc="upper right", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "perm-three-methods.png")

print("leaf", leaf, "held-out accuracy", round(base, 3), "train", round(m.score(Xtr, ytr), 3))
print("mdi ", np.round(m.feature_importances_, 3))
print("perm", np.round(perm.importances_mean, 3), "+-", np.round(perm.importances_std, 3))
print("drop", np.round(drop, 3))
