"""Logistic regression against a one-hidden-layer network of 8 neurons with no, tanh and ReLU activation.

Each network is the best of ten random starts by training loss.

Rows are xor, circles and moons; across a row only the model changes. The
network without activation must draw the same straight boundary as logistic
regression: the script checks that both boundaries are lines.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import nn_common as nc  # noqa: E402

DATA = ["xor", "circles", "moons"]
WIDTH = 8
MODELS = [
    ("логистическая регрессия", lambda X, y: LogisticRegression(max_iter=10000).fit(X, y)),
    ("сеть без активации", lambda X, y: nc.best_of(lambda s: nc.mlp([WIDTH], "identity", seed=s), X, y)),
    ("сеть с tanh", lambda X, y: nc.best_of(lambda s: nc.mlp([WIDTH], "tanh", seed=s), X, y)),
    ("сеть с ReLU", lambda X, y: nc.best_of(lambda s: nc.mlp([WIDTH], "relu", seed=s), X, y)),
]

fig, axes = fk.subplots(len(DATA), len(MODELS), size=(12.4, 9.4))
for i, name in enumerate(DATA):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for j, (title, make) in enumerate(MODELS):
        m = make(Xtr, ytr)
        fk.plot_decision(axes[i, j], m, Xtr, ytr, X_test=Xte, y_test=yte)
        if i == 0:
            axes[i, j].set_title(title)
        if j == 0:
            axes[i, j].set_ylabel(name)
        if j < 2:
            # The decision function of a linear model is affine: its second differences vanish.
            g = np.linspace(-1, 1, 5)
            P = np.array([[a, b] for a in g for b in g])
            d = m.decision_function(P) if hasattr(m, "decision_function") else nc.logit(m, P)
            A = np.c_[P, np.ones(len(P))]
            resid = d - A @ np.linalg.lstsq(A, d, rcond=None)[0]
            assert np.max(np.abs(resid)) < 1e-6, (name, title, np.max(np.abs(resid)))
        print(name, title, "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
fig.tight_layout()
fk.save(fig, fk.attachments(6) / "nn-nonlinearity.png")
