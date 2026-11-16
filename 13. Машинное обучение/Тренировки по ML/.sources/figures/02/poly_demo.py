"""Shared polynomial-regression setup for the reg-poly-* figures: reg1d data, degree-15 features, Ridge and LASSO in lecture terms.

Both fits are exact, so no iterative solver can stop short of the optimum. Ridge is the SVD formula; LASSO
is read off the exact piecewise-linear path from lars_path. The objective is ||y - Zw||^2 + lam * penalty(w)
on standardised features with a free, unpenalised intercept (centred y).
scikit-learn scales its LASSO objective by 1/(2n), so its alpha equals lam / (2n); lars_path reports
alpha in that scaling.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import lars_path
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

DEGREE = 15
X, Y = fk.dataset("reg1d")
Xtr, Xte, ytr, yte = train_test_split(X, Y, train_size=15, random_state=fk.SEED)
N_TR = len(Xtr)


class Fit:
    """A fitted polynomial model; predict(x) takes a column of raw x values."""

    def __init__(self, kind, lam, x, y):
        self.poly = PolynomialFeatures(DEGREE, include_bias=False)
        self.scaler = StandardScaler().fit(self.poly.fit_transform(x))
        Z = self.scaler.transform(self.poly.transform(x))
        self.y_mean = y.mean()
        yc = y - self.y_mean
        if kind == "ridge":
            U, s, Vt = np.linalg.svd(Z, full_matrices=False)
            self.w = Vt.T @ (s / (s**2 + lam) * (U.T @ yc))
        else:
            alphas, _, coefs = lars_path(Z, yc, method="lasso")
            a = lam / (2 * len(y))
            self.w = np.array([np.interp(a, alphas[::-1], row[::-1]) for row in coefs])

    def predict(self, x):
        return self.scaler.transform(self.poly.transform(x)) @ self.w + self.y_mean

    @property
    def n_nonzero(self):
        return int((abs(self.w) > 1e-10).sum())


def fit(kind, lam, x=None, y=None):
    return Fit(kind, lam, Xtr if x is None else x, ytr if y is None else y)


def mse(model, A, b):
    return float(((model.predict(A) - b) ** 2).mean())


def cv_mse(kind, lam, folds=N_TR):
    """Mean validation MSE over folds of the training part only (default: leave-one-out, 15 folds of one point).

    The test part never enters the choice of lam."""
    errs = []
    for tr, va in KFold(folds, shuffle=True, random_state=fk.SEED).split(Xtr):
        errs.append(mse(Fit(kind, lam, Xtr[tr], ytr[tr]), Xtr[va], ytr[va]))
    return float(np.mean(errs))
