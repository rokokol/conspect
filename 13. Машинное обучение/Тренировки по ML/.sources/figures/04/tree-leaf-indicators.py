"""A tree is a linear model over leaf indicators: regions with leaf numbers, indicator matrix, leaf constants."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sklearn.tree import DecisionTreeClassifier  # noqa: E402
from tree_common import box_of, draw_splits  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
m = DecisionTreeClassifier(max_depth=3, random_state=fk.SEED).fit(Xtr, ytr)
leaf_ids = np.flatnonzero(m.tree_.children_left < 0)  # node ids of leaves
col = {nid: j for j, nid in enumerate(leaf_ids)}
c = np.array([m.tree_.value[nid][0, 1] / m.tree_.value[nid][0].sum() for nid in leaf_ids])  # P(class 1) per leaf

fig = fk.plt.figure(figsize=(12.6, 4.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 0.28], wspace=0.28)
ax = fig.add_subplot(gs[0])
fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte, proba=False, scores=False,
                 title="Области листьев $Q_j$")
box = box_of(np.vstack([Xtr, Xte]))
draw_splits(ax, m, box, lw=1.6)

# Label every leaf by the position of the first point that falls in it (inside its rectangle).
rng = np.random.default_rng(fk.SEED)
gx, gy = np.meshgrid(np.linspace(box[0], box[1], 400), np.linspace(box[2], box[3], 400))
cells = m.apply(np.c_[gx.ravel(), gy.ravel()])
for nid in leaf_ids:
    mask = cells == nid
    cx, cy = gx.ravel()[mask].mean(), gy.ravel()[mask].mean()
    ax.text(cx, cy, f"L{col[nid] + 1}", ha="center", va="center", fontsize=9, color=fk.TEXT, zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=fk.TEXT_2, lw=0.6, alpha=0.9))

# Indicator matrix for 10 objects of the test part, sorted by leaf.
# One test object from every leaf first, so no column of the matrix is empty, then random ones up to ten.
te_leaf = m.apply(Xte)
first = [int(rng.choice(np.flatnonzero(te_leaf == nid))) for nid in leaf_ids]
rest = rng.choice(np.setdiff1d(np.arange(len(Xte)), first), 10 - len(first), replace=False)
pick = np.r_[first, rest].astype(int)
Xp = Xte[pick]
order = np.argsort(m.apply(Xp))
Xp = Xp[order]
Z = np.zeros((len(Xp), len(leaf_ids)))
for i, nid in enumerate(m.apply(Xp)):
    Z[i, col[nid]] = 1
ax2 = fig.add_subplot(gs[1])
ax2.imshow(Z, cmap="ddlc_seq", vmin=0, vmax=1.4, aspect="auto")
for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
        ax2.text(j, i, f"{int(Z[i, j])}", ha="center", va="center", fontsize=8,
                 color=fk.TEXT if Z[i, j] < 0.5 else "white")
ax2.set_xticks(range(len(leaf_ids)), [f"L{j + 1}\nc={fk.num(c[j], 2)}" for j in range(len(leaf_ids))])
ax2.set_yticks(range(len(Xp)), [f"x{i + 1}" for i in range(len(Xp))])
ax2.set_title(r"Признаки $[\mathbf{x}\in Q_j]$")
ax2.grid(False)
for side in ax2.spines.values():
    side.set_visible(False)

ax3 = fig.add_subplot(gs[2])
pred_vec = Z @ c
ax3.imshow(pred_vec[:, None], cmap=fk.PROBA_CMAP, vmin=0, vmax=1, aspect="auto")
for i, v in enumerate(pred_vec):
    ax3.text(0, i, fk.num(v, 2), ha="center", va="center", fontsize=8, color=fk.TEXT)
ax3.set_xticks([0], ["ŷ"])
ax3.set_yticks([])
ax3.set_title("Z·c")
ax3.grid(False)
for side in ax3.spines.values():
    side.set_visible(False)
fk.save(fig, fk.attachments(4) / "tree-leaf-indicators.png")

print("leaf constants c:", {f"L{col[n] + 1}": round(float(c[col[n]]), 3) for n in leaf_ids})
assert np.allclose(pred_vec, m.predict_proba(Xp)[:, 1]), "Z c must equal predict_proba"
print("Z c equals predict_proba for the 10 objects")
