"""OOB error of a random forest against the number of trees, next to 5-fold validation, train and test (moons).

One forest of T trees is grown once; the curve at n uses its first n trees, so every point is a forest of n trees.
An object enters the OOB error once at least one of the first n trees has not seen it.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402

import figkit as fk  # noqa: E402

T = 500
GRID_N = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500]


def tree_probas(rf, X):
    """Probability of class 1 from every tree: shape (trees, objects)."""
    return np.array([t.predict_proba(X)[:, 1] for t in rf.estimators_])


def err_prefix(P, y, n, mask=None):
    """Error of the mean of the first n trees; mask (trees, objects) keeps only the trees allowed per object."""
    if mask is None:
        mean = P[:n].mean(0)
        return float(np.mean((mean > 0.5) != y)), 1.0
    w = mask[:n]
    cnt = w.sum(0)
    seen = cnt > 0
    mean = (P[:n] * w).sum(0)[seen] / cnt[seen]
    return float(np.mean((mean > 0.5) != y[seen])), float(seen.mean())


X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)

rf = RandomForestClassifier(n_estimators=T, random_state=fk.SEED).fit(Xtr, ytr)
P_tr, P_te = tree_probas(rf, Xtr), tree_probas(rf, Xte)
inbag = np.zeros((T, len(Xtr)), dtype=bool)
for k, idx in enumerate(rf.estimators_samples_):
    inbag[k, idx] = True
oob_mask = ~inbag

train = [err_prefix(P_tr, ytr, n)[0] for n in GRID_N]
test = [err_prefix(P_te, yte, n)[0] for n in GRID_N]
oob = [err_prefix(P_tr, ytr, n, oob_mask) for n in GRID_N]

# Validation: 5-fold on the train part, every fold a forest of T trees on four fifths of it.
fold_P, fold_y = [], []
for fit_idx, val_idx in StratifiedKFold(5, shuffle=True, random_state=fk.SEED).split(Xtr, ytr):
    f = RandomForestClassifier(n_estimators=T, random_state=fk.SEED).fit(Xtr[fit_idx], ytr[fit_idx])
    fold_P.append(tree_probas(f, Xtr[val_idx]))
    fold_y.append(ytr[val_idx])
P_val, y_val = np.hstack(fold_P), np.concatenate(fold_y)
val = [err_prefix(P_val, y_val, n)[0] for n in GRID_N]

fig, (ax1, ax2) = fk.subplots(1, 2, size=(11.6, 4.0), gridspec_kw={"width_ratios": [1.7, 1]})
ax1.plot(GRID_N, train, color=fk.TRAIN_C, marker="o", ms=4, label="train")
ax1.plot(GRID_N, [o[0] for o in oob], color=fk.MODEL_C, marker="o", ms=4, lw=1.8, label="OOB")
ax1.plot(GRID_N, val, color=fk.TEXT_2, marker="s", ms=3, ls=":", label="валидация, 5 блоков")
ax1.plot(GRID_N, test, color=fk.TEST_C, marker="o", ms=4, mfc="white", label="test")
ax1.set_xscale("log")
ax1.set_xlabel("число деревьев n")
ax1.set_ylabel("доля ошибок")
ax1.set_title("ошибка леса от числа деревьев")
ax1.grid(True, axis="y")
ax1.legend(loc="upper right")

ax2.plot(GRID_N, [o[1] for o in oob], color=fk.MODEL_C, marker="o", ms=4)
ax2.axhline(1.0, color=fk.GRIDC, lw=0.8)
ax2.set_xscale("log")
ax2.set_xlabel("число деревьев n")
ax2.set_ylabel("доля объектов с OOB-оценкой")
ax2.set_title("у скольких объектов есть OOB")
ax2.set_ylim(0, 1.05)
ax2.grid(True, axis="y")
fk.save(fig, fk.attachments(5) / "rf-oob-vs-trees.png")

print("n", GRID_N)
print("train", [round(v, 3) for v in train])
print("oob  ", [round(o[0], 3) for o in oob])
print("val  ", [round(v, 3) for v in val])
print("test ", [round(v, 3) for v in test])
print("covered", [round(o[1], 3) for o in oob])
print("sklearn oob_score_ at T:", round(1 - RandomForestClassifier(n_estimators=T, oob_score=True,
                                                                  random_state=fk.SEED).fit(Xtr, ytr).oob_score_, 3))
