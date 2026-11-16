"""One fitted logistic regression with the weight vector stretched: the boundary stays, the probabilities and the loss change."""
import copy
import sys
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, y = fk.dataset("linear")
Xtr, Xte, ytr, yte = fk.split(X, y)
base = LogisticRegression(C=1.0).fit(Xtr, ytr)

SCALES = [0.25, 1.0, 5.0]
fig, axes = fk.subplots(1, len(SCALES), size=(10.2, 3.5))
for ax, c in zip(axes, SCALES):
    m = copy.deepcopy(base)
    m.coef_ = base.coef_ * c
    m.intercept_ = base.intercept_ * c
    fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte, scores=False)
    ax.set_title(f"веса $\\times {fk.num(c, None, math=True)}$")
    ax.text(0.98, 0.02, f"train log-loss {fk.num(log_loss(ytr, m.predict_proba(Xtr)), 2)}\ntrain accuracy {fk.num(m.score(Xtr, ytr), 2)}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    print(c, round(log_loss(ytr, m.predict_proba(Xtr)), 4), round(m.score(Xtr, ytr), 4))
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "logreg-weight-scale.png")
