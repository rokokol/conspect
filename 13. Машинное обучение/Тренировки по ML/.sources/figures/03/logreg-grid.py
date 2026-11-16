"""Logistic regression on polynomial features: zones over degree x C on moons and circles, plus train/validation/test curves."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(3)
DEGREES = [1, 2, 3, 6]
CS = [0.01, 0.1, 1, 100]
CURVE_DEGREES = [1, 2, 3, 4, 5, 6, 7, 8]
CURVE_CS = np.logspace(-3, 3, 13)
FIXED_C = 1.0
FIXED_DEGREE = 6


def make(degree, c):
    return make_pipeline(PolynomialFeatures(degree, include_bias=False), StandardScaler(),
                         LogisticRegression(C=c, max_iter=200000, tol=1e-8))


for name in ("moons", "circles"):
    fig, axes = fk.model_grid(make, DEGREES, CS, name,
                              row_label=lambda d: f"степень {d}", col_label=lambda c: f"$C={fk.num(c, None, math=True)}$",
                              size=(12.4, 12.0))
    fk.save(fig, OUT / f"logreg-grid-{name}.png")

    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    fig, axes = fk.subplots(1, 2, size=(9.6, 3.6))
    for ax, values, build, xlabel, log in (
        (axes[0], CURVE_DEGREES, lambda d: make(d, FIXED_C), f"степень признаков ($C={fk.num(FIXED_C, None, math=True)}$)", False),
        (axes[1], CURVE_CS, lambda c: make(FIXED_DEGREE, c), f"$C$ (степень {FIXED_DEGREE})", True),
    ):
        tr, te, va = [], [], []
        for v in values:
            m = build(v).fit(Xtr, ytr)
            tr.append(m.score(Xtr, ytr))
            te.append(m.score(Xte, yte))
            va.append(cross_val_score(build(v), Xtr, ytr, cv=5).mean())
        b = fk.complexity_curve(ax, values, tr, te, xlabel=xlabel, val=va, log=log)
        print(name, xlabel, "chosen by validation:", values[b], "val", round(va[b], 3),
              "test", round(te[b], 3))
    axes[0].set_title("по степени")
    axes[1].set_title("по $C$")
    fig.tight_layout()
    fk.save(fig, OUT / f"logreg-curves-{name}.png")
