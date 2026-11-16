"""Numbers for the note on gradient boosting: boosting over linear regressions stays one linear regression.

Boosting with the MSE loss on reg1d, base model LinearRegression, exact step rho. After the first step the residuals are orthogonal to the
features and to the constant, so the second model is the zero function. Prints the weights step by step and the distance to one least-squares fit.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LinearRegression  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("reg1d")
f = np.full(len(y), y.mean())
w, b = 0.0, float(y.mean())
for t in range(1, 4):
    r = y - f
    h = LinearRegression().fit(X, r)
    hx = h.predict(X)
    rho = float(hx @ r / (hx @ hx)) if hx @ hx > 1e-24 else 0.0
    w, b = w + rho * float(h.coef_[0]), b + rho * float(h.intercept_)
    f = f + rho * hx
    print(f"step {t}: slope of h = {float(h.coef_[0]):+.3e}, intercept of h = {float(h.intercept_):+.3e}, rho = {rho:.3f}; ensemble: slope {w:.4f}, intercept {b:.4f}")
ols = LinearRegression().fit(X, y)
print(f"one least-squares fit: slope {float(ols.coef_[0]):.4f}, intercept {float(ols.intercept_):.4f}")
print("max |ensemble - OLS| on the sample:", float(np.abs(f - ols.predict(X)).max()))
