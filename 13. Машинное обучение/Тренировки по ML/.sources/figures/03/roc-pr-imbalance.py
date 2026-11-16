"""ROC and PR of one fixed model on a balanced test set and on the same test set with 10 % of the positives kept."""
import sys
from pathlib import Path

import numpy as np
from sklearn import datasets as skd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, precision_recall_curve, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# The course's moons recipe at 4000 points: 10 % of the positives of the 300-point set would be 15 objects, too few for a curve.
X, y = skd.make_moons(4000, noise=0.3, random_state=fk.SEED)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, random_state=fk.SEED, stratify=y)
model = LogisticRegression().fit(Xtr, ytr)
score = model.predict_proba(Xte)[:, 1]

pos = np.flatnonzero(yte == 1)
keep = np.r_[np.flatnonzero(yte == 0), pos[: len(pos) // 10]]
sets = [("баланс 1 : 1", np.arange(len(yte)), fk.MODEL_C), ("дисбаланс 10 : 1", keep, fk.MODEL2_C)]

fig, (ax, bx, cx) = fk.subplots(1, 3, size=(13.6, 4.3))
for name, ii, c in sets:
    yy, ss = yte[ii], score[ii]
    f, t, _ = roc_curve(yy, ss)
    p, r, _ = precision_recall_curve(yy, ss)
    auc, ap, base = roc_auc_score(yy, ss), average_precision_score(yy, ss), yy.mean()
    print(name, "n", len(yy), "positives", int(yy.sum()), "AUC", round(auc, 3), "AP", round(ap, 3), "base", round(base, 3))
    ax.plot(f, t, color=c, lw=2, label=f"{name}, AUC {fk.num(auc, 2)}")
    bx.plot(r, p, color=c, lw=2, label=f"{name}, AP {fk.num(ap, 2)}")
    bx.axhline(base, color=c, ls=":", lw=1)
    # A fixed threshold 0.5: where the same model sits on both curves.
    pred = ss >= 0.5
    tpr, fpr = (pred & (yy == 1)).sum() / (yy == 1).sum(), (pred & (yy == 0)).sum() / (yy == 0).sum()
    prec = (pred & (yy == 1)).sum() / pred.sum()
    ax.scatter([fpr], [tpr], s=60, color=c, edgecolors=fk.TEXT, zorder=5)
    bx.scatter([tpr], [prec], s=60, color=c, edgecolors=fk.TEXT, zorder=5)
    print("   at 0.5: TPR", round(float(tpr), 3), "FPR", round(float(fpr), 3), "precision", round(float(prec), 3))
    if name.startswith("баланс"):
        # The negatives are the same objects in both variants: one line for both.
        cx.hist(ss[yy == 0], bins=25, range=(0, 1), histtype="step", lw=2, color=fk.TEXT_2, label="класс 0, в обоих наборах")
    cx.hist(ss[yy == 1], bins=25, range=(0, 1), histtype="step", lw=2, color=c, label=f"класс 1, {name}")
ax.plot([0, 1], [0, 1], color=fk.TEXT_2, ls="--", lw=1)
ax.set_title("ROC: почти не меняется")
ax.set_xlabel("FPR")
ax.set_ylabel("TPR")
bx.set_title("PR: проседает, пунктир - доля класса 1")
bx.set_xlabel("recall")
bx.set_ylabel("precision")
cx.set_title("оценки по классам")
cx.set_xlabel("оценка P(класс 1)")
cx.set_ylabel("число объектов теста")
for a in (ax, bx):
    a.set_xlim(0, 1)
    a.set_ylim(0, 1.02)
    a.set_aspect("equal")
for a in (ax, bx, cx):
    a.grid(True)
    if a is bx:
        a.legend(loc="lower left", bbox_to_anchor=(0.0, 0.14), fontsize=7)
    else:
        a.legend(loc="lower right" if a is ax else "upper center", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "roc-pr-imbalance.png")
