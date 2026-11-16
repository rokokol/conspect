"""Shared setup for the overfit-* figures: reg1d split into 28 train and 12 test points, polynomial least squares of any degree.

The split matches the polyfit sandbox of the note (28 train points, 12 test points). Polynomial.fit rescales x to [-1, 1]
before it solves the least-squares problem, so degree 15 stays numerically sound.
"""
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial
from sklearn.model_selection import KFold, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, Y = fk.dataset("reg1d")
x_tr, x_te, y_tr, y_te = train_test_split(X[:, 0], Y, test_size=12, random_state=fk.SEED)
MAX_DEGREE = 15


def fit(degree, x=None, y=None):
    """Least-squares polynomial of the given degree on (x, y), default the train part."""
    return Polynomial.fit(x_tr if x is None else x, y_tr if y is None else y, degree)


def mse(model, x, y):
    return float(((model(x) - y) ** 2).mean())


def cv_mse(degree, folds=None):
    """Mean validation MSE over k folds of the train part (default: leave-one-out); the test part never enters."""
    errs = []
    for tr, va in KFold(folds or len(x_tr), shuffle=True, random_state=fk.SEED).split(x_tr):
        errs.append(mse(fit(degree, x_tr[tr], y_tr[tr]), x_tr[va], y_tr[va]))
    return float(np.mean(errs))
