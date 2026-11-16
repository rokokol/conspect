"""Two ROC shapes the lecturer's questions touch: hard labels give a triangle, a poorly fitting linear model gives a non-convex curve."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

fig, axes = fk.subplots(1, 2, size=(9.0, 4.4))

# (a) moons, logistic regression: only the labels at threshold 0.5 versus the scores.
X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
m = LogisticRegression().fit(Xtr, ytr)
score = m.predict_proba(Xte)[:, 1]
label = (score >= 0.5).astype(int)
f, tp, _ = roc_curve(yte, score)
fpr0 = ((label == 1) & (yte == 0)).sum() / (yte == 0).sum()
tpr0 = ((label == 1) & (yte == 1)).sum() / (yte == 1).sum()
ax = axes[0]
ax.plot(f, tp, color=fk.TEXT_2, lw=2, label=f"по оценкам, AUC {fk.num(roc_auc_score(yte, score), 2)}")
ax.plot([0, fpr0, 1], [0, tpr0, 1], color=fk.MODEL_C, lw=2, marker="o", ms=5,
        label=f"только метки, AUC {fk.num((1 + tpr0 - fpr0) / 2, 2)}")
ax.set_title("метки без оценок: треугольник")
print("triangle point", round(float(fpr0), 3), round(float(tpr0), 3), "AUC labels", round(float((1 + tpr0 - fpr0) / 2), 4))

# (b) xor, a linear score: a line cannot separate the classes, and the ROC curve wanders around the diagonal.
Xc, yc = fk.dataset("xor")
Xctr, Xcte, yctr, ycte = fk.split(Xc, yc)
mc = LogisticRegression().fit(Xctr, yctr)
sc = mc.predict_proba(Xcte)[:, 1]
f2, t2, _ = roc_curve(ycte, sc)
a2 = roc_auc_score(ycte, sc)
ax = axes[1]
ax.plot(f2, t2, color=fk.MODEL_C, lw=2, label=f"линейная модель, AUC {fk.num(a2, 2)}")
print("xor AUC", round(float(a2), 3), "min(tpr - fpr)", round(float((t2 - f2).min()), 3), "max(tpr - fpr)", round(float((t2 - f2).max()), 3))
ax.set_title("линейная модель на XOR")
for ax in axes:
    ax.plot([0, 1], [0, 1], color=fk.TEXT_2, ls="--", lw=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.grid(True)
    ax.legend(loc="lower right", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "roc-shapes.png")
