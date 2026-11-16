"""Impurity importance against permutation importance of one forest family, grid by the minimum leaf size.

Same table, same split, same forest settings (200 trees); only min_samples_leaf changes across columns. Top row is
impurity importance (a train-part statistic), bottom row is permutation importance on the held-out part
(accuracy drop, 30 shuffles per column). All three leaf sizes are shown, none is picked.
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
LABELS = ["x1", "x2", "flag\n2 знач.", "noise_num\nвсе разные", "noise_cat\n3 знач."]
COLORS = [fk.CATEGORICAL[0]] * 3 + [fk.CATEGORICAL[1]] * 2

fig, axes = fk.subplots(2, len(ic.LEAF_GRID), size=(11.6, 6.4), sharey="row")
for j, leaf in enumerate(ic.LEAF_GRID):
    m = RandomForestClassifier(n_estimators=ic.N_FOREST, min_samples_leaf=leaf, random_state=fk.SEED,
                               n_jobs=-1).fit(Xtr, ytr)
    perm = permutation_importance(m, Xva, yva, n_repeats=30, random_state=fk.SEED)
    ax = axes[0, j]
    ax.bar(range(5), m.feature_importances_, color=COLORS)
    ax.set_title(f"min_samples_leaf = {leaf}\ntrain {fk.num(m.score(Xtr, ytr), 2)} | held-out {fk.num(m.score(Xva, yva), 2)}",
                 fontsize=10)
    ax.set_ylim(0, 0.52)
    ax.set_xticks(range(5), LABELS, fontsize=6.5)
    ax.grid(True, axis="y")
    for i, v in enumerate(m.feature_importances_):
        ax.text(i, v + 0.01, f"{fk.num(v, 2)}", ha="center", fontsize=8)
    ax = axes[1, j]
    ax.bar(range(5), perm.importances_mean, yerr=perm.importances_std, color=COLORS,
           error_kw=dict(ecolor=fk.TEXT, lw=1, capsize=3))
    ax.axhline(0, color=fk.TEXT_2, lw=0.8)
    ax.set_ylim(-0.04, 0.22)
    ax.set_xticks(range(5), LABELS, fontsize=6.5)
    ax.grid(True, axis="y")
    print(leaf, "mdi", np.round(m.feature_importances_, 3), "perm", np.round(perm.importances_mean, 3),
          "train/held-out", round(m.score(Xtr, ytr), 3), round(m.score(Xva, yva), 3))
axes[0, 0].set_ylabel("impurity, обучающая часть")
axes[1, 0].set_ylabel("permutation, отложенная часть")
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "imp-mdi-bias-leaf.png")
