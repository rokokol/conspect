"""Small probabilities of a teacher on digits: what a soft label holds beyond the answer.

Teacher: multinomial logistic regression on the 8x8 digits, C chosen by 5-fold CV on the train part. For the first
correctly classified test image of the digits 3, 7 and 9, the probabilities of the ten classes at T = 1 and T = 4
on a logarithmic axis. T = 4 is for illustration, not chosen. Output: distill-dark-knowledge.png
"""
import sys
from pathlib import Path

import numpy as np
from scipy.special import softmax
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

DIGITS = (3, 7, 9)
TEMPS = (1.0, 4.0)

X, y = load_digits(return_X_y=True)
X = X / 16.0
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=fk.SEED, stratify=y)
cv = StratifiedKFold(5, shuffle=True, random_state=fk.SEED)
gs = GridSearchCV(LogisticRegression(max_iter=5000), {"C": [0.01, 0.1, 1, 10]}, cv=cv,
                  error_score="raise").fit(Xtr, ytr)
model = gs.best_estimator_
print(f"C={gs.best_params_['C']:g}\ttrain {model.score(Xtr, ytr):.3f}\ttest {model.score(Xte, yte):.3f}")
logits = model.decision_function(Xte)

fig = fk.plt.figure(figsize=(3.6 * len(DIGITS), 1.1 + 3.0 * len(TEMPS)))
gs = fig.add_gridspec(1 + len(TEMPS), len(DIGITS), height_ratios=[0.9] + [3.0] * len(TEMPS))
for j, d in enumerate(DIGITS):
    idx = next(i for i in range(len(yte)) if yte[i] == d and logits[i].argmax() == d)
    img = fig.add_subplot(gs[0, j])
    img.imshow(Xte[idx].reshape(8, 8), cmap="Greys")
    img.axis("off")
    for i, T in enumerate(TEMPS):
        ax = fig.add_subplot(gs[1 + i, j])
        p = softmax(logits[idx] / T)
        colors = [fk.ACCENT if k == d else fk.TEXT_2 for k in range(10)]
        ax.bar(range(10), p, color=colors)
        ax.set_yscale("log")
        ax.set_ylim(1e-9, 1.5)
        ax.set_xticks(range(10))
        order = [k for k in np.argsort(-p) if k != d][:2]
        ax.set_xlabel(f"класс; после {d}: {order[0]} ({fk.num(p[order[0]], '.1e')}), {order[1]} ({fk.num(p[order[1]], '.1e')})", fontsize=7)
        if j == 0:
            ax.set_ylabel(f"вероятность, T={fk.num(T, None)}")
        print(f"digit {d}\tT={T:g}\tp_true {p[d]:.4f}\tsecond {order[0]} {p[order[0]]:.2e}\tthird {order[1]} {p[order[1]]:.2e}")
fig.tight_layout()
fk.save(fig, fk.attachments(8) / "distill-dark-knowledge.png")
