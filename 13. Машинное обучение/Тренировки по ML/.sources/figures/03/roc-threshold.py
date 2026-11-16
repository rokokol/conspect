"""Choosing a threshold on validation scores of the training part, then showing the outcome on the test part: default 0.5 against the lecturer's rule (recall at least 0.6, then the best precision)."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, roc_curve
from sklearn.model_selection import cross_val_predict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
model = LogisticRegression().fit(Xtr, ytr)
score = model.predict_proba(Xte)[:, 1]
# Validation scores: out-of-fold predictions on the training part, the model never scores an object it was fitted on.
val_score = cross_val_predict(LogisticRegression(), Xtr, ytr, cv=5, method="predict_proba")[:, 1]


def rare(y_, s_):
    """Mild imbalance, so the two rules differ: every negative and every third positive."""
    pos = np.flatnonzero(y_ == 1)
    ii = np.r_[np.flatnonzero(y_ == 0), pos[::3]]
    return y_[ii], s_[ii]


yv, sv = rare(ytr, val_score)
yy, ss = rare(yte, score)

# The rule runs on validation only: among thresholds with recall >= 0.6 take the one with the highest precision.
pv, rv, thr_v = precision_recall_curve(yv, sv)
ok = np.flatnonzero(rv[:-1] >= 0.6)
best = ok[np.argmax(pv[:-1][ok])]
t_rule = thr_v[best]
val_point = (rv[best], pv[best])

f, t, _ = roc_curve(yy, ss)
p, r, _ = precision_recall_curve(yy, ss)


def point(th):
    pred = ss >= th
    tp, fp = (pred & (yy == 1)).sum(), (pred & (yy == 0)).sum()
    fn, tn = ((~pred) & (yy == 1)).sum(), ((~pred) & (yy == 0)).sum()
    return dict(th=th, tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn), tpr=tp / (tp + fn), fpr=fp / (fp + tn),
                prec=tp / (tp + fp) if tp + fp else 1.0)


pts = [(point(0.5), fk.TEXT, f"порог {fk.num(0.5, 1)}"), (point(t_rule), fk.MODEL2_C, f"порог {fk.num(t_rule, 2)}, валидация")]
for d, _, name in pts:
    print(name, {k: (round(float(v), 3) if isinstance(v, float) else v) for k, v in d.items()})
print("test objects", len(yy), "positives", int(yy.sum()), "| validation objects", len(yv), "positives", int(yv.sum()))
print("validation at the rule: recall", round(float(val_point[0]), 3), "precision", round(float(val_point[1]), 3))

fig, (ax, bx, cx) = fk.subplots(1, 3, size=(13.6, 4.3))
bins = np.linspace(0, 1, 26)
ax.hist(ss[yy == 0], bins=bins, color=fk.tint(fk.CLASS_COLORS[0], 0.3), label="класс 0, тест")
ax.hist(ss[yy == 1], bins=bins, color=fk.tint(fk.CLASS_COLORS[1], 0.3), alpha=0.8, label="класс 1, тест")
for d, c, name in pts:
    ax.axvline(d["th"], color=c, lw=2.5, label=name)
ax.set_title("оценки теста и два порога")
ax.set_xlabel("оценка P(класс 1)")
ax.set_ylabel("число объектов")
ax.legend(fontsize=6, loc="center left", bbox_to_anchor=(0.1, 0.7), borderaxespad=0.2)

bx.plot(f, t, color=fk.MODEL_C, lw=2)
bx.plot([0, 1], [0, 1], color=fk.TEXT_2, ls="--", lw=1)
cx.plot(r, p, color=fk.MODEL_C, lw=2, label="тест")
cx.plot(rv, pv, color=fk.TEXT_2, lw=1.2, ls=":", label="валидация")
cx.scatter([val_point[0]], [val_point[1]], s=60, facecolors="white", edgecolors=fk.MODEL2_C, linewidths=2, zorder=5,
           label="выбор по валидации")
cx.axvline(0.6, color=fk.GRIDC, lw=1, ls="--")
for d, c, name in pts:
    bx.scatter([d["fpr"]], [d["tpr"]], s=70, color=c, edgecolors="white", zorder=5, label=name)
    cx.scatter([d["tpr"]], [d["prec"]], s=70, color=c, edgecolors="white", zorder=5, label=name)
bx.set_title("ROC теста")
bx.set_xlabel("FPR")
bx.set_ylabel("TPR")
cx.set_title("PR: тест, валидация и выбор")
cx.set_xlabel("recall")
cx.set_ylabel("precision")
for a in (bx, cx):
    a.set_xlim(0, 1)
    a.set_ylim(0, 1.02)
    a.set_aspect("equal")
    a.grid(True)
    a.legend(loc="lower right" if a is bx else "lower left", fontsize=6)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "roc-threshold.png")
