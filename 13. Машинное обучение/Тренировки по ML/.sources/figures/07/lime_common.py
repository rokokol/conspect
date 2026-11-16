"""LIME written out by hand for two features: one black box on moons, one explained point, nothing else changes between figures.

Black box f(z) = P(class 1) of an RBF SVM (C and gamma by 5-fold CV on the train part). Perturbations z = x + tau * N(0, I),
neighbour weight pi_x(z) = exp(-|z - x|^2 / sigma^2) as in the LIME paper, local model g(z) = a + w . (z - x) by weighted
least squares on f(z). The explanation is the vector w.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

TAU = 0.8
GRID = {"estimator__C": [1, 10, 100], "estimator__gamma": [0.5, 1, 2, 5]}


def black_box():
    """RBF SVM with Platt-calibrated probabilities (SVC(probability=True) is deprecated in scikit-learn 1.9)."""
    X, y = fk.dataset("moons")
    Xtr, Xte, ytr, yte = fk.split(X, y)
    base = CalibratedClassifierCV(SVC(kernel="rbf"), method="sigmoid", cv=5, ensemble=False)
    grid = GridSearchCV(base, GRID, cv=5, n_jobs=1).fit(Xtr, ytr)
    return grid.best_estimator_, grid.best_params_, (Xtr, Xte, ytr, yte)


def proba(model):
    return lambda Z: model.predict_proba(np.atleast_2d(Z))[:, 1]


def explained_point(f, Xte):
    """The held-out object whose probability is closest to 0.5: an object near the boundary has something to explain."""
    return Xte[np.argmin(np.abs(f(Xte) - 0.5))]


def sample(x, n, rng, tau=TAU):
    return x + tau * rng.normal(size=(n, len(x)))


def kernel(Z, x, sigma):
    return np.exp(-((Z - x) ** 2).sum(1) / sigma**2)


def local_fit(f, x, Z, w):
    """Weighted least squares of f(Z) on Z - x: intercept a, coefficients c, weighted R^2."""
    t = f(Z)
    A = np.c_[np.ones(len(Z)), Z - x]
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(A * sw[:, None], t * sw, rcond=None)
    resid = t - A @ beta
    tbar = np.average(t, weights=w)
    r2 = 1 - np.sum(w * resid**2) / max(np.sum(w * (t - tbar) ** 2), 1e-12)
    return beta[0], beta[1:], r2


def gradient(f, x, h=1e-3):
    g = np.zeros(len(x))
    for j in range(len(x)):
        e = np.zeros(len(x))
        e[j] = h
        g[j] = (f(x + e)[0] - f(x - e)[0]) / (2 * h)
    return g


def angle(a, b):
    """Angle in degrees between two coefficient vectors."""
    c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def boundary_segment(a, c, x, box, level=0.5):
    """Points of the line a + c . (z - x) = level inside the box (xmin, xmax, ymin, ymax), or None."""
    xmin, xmax, ymin, ymax = box
    if abs(c[1]) > abs(c[0]):
        xs = np.array([xmin, xmax])
        ys = x[1] + (level - a - c[0] * (xs - x[0])) / c[1]
    else:
        ys = np.array([ymin, ymax])
        xs = x[0] + (level - a - c[1] * (ys - x[1])) / c[0]
    return xs, ys
