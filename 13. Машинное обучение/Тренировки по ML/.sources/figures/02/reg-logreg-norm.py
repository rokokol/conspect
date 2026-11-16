"""Logistic regression on separable data: the weight norm grows without bound as the regularisation weakens."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

rng = np.random.default_rng(fk.SEED)
X = np.r_[rng.normal([-2.2, 0], 0.6, (40, 2)), rng.normal([2.2, 0], 0.6, (40, 2))]
y = np.r_[np.zeros(40), np.ones(40)].astype(int)
assert LogisticRegression(C=1e6, max_iter=10000).fit(X, y).score(X, y) == 1.0

Cs = np.logspace(-3, 6, 28)
norms = [np.linalg.norm(LogisticRegression(C=c, max_iter=100000, tol=1e-10).fit(X, y).coef_) for c in Cs]

fig, axes = fk.subplots(1, 2, size=(9.2, 3.8))
ax = axes[0]
ax.scatter(*X[y == 0].T, color=fk.BLUE, s=18, edgecolor="white")
ax.scatter(*X[y == 1].T, color=fk.RED, s=18, edgecolor="white")
xs = np.linspace(-4, 4, 2)
ax.axvline(0, color=fk.TEXT, lw=1.4)
ax.set_title("Разделимая выборка")
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")

ax = axes[1]
ax.plot(Cs, norms, color=fk.TEXT, marker="o", ms=3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("$C$ (чем больше, тем слабее штраф)")
ax.set_ylabel("$\\|w\\|_2$")
ax.set_title("Норма весов растёт без предела")
ax.grid(True)
fig.tight_layout()
fk.save(fig, OUT / "reg-logreg-norm.png")
print(norms[0], norms[-1])
