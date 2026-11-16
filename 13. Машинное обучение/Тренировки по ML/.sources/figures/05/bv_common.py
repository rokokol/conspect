"""Shared simulation of the bias-variance figures: the noisy sine, fresh training samples, bias^2 and variance on a grid.

The truth is f(x) = sin 2 pi x, x ~ U(0, 1), y = f(x) + noise with sigma = 0.25, the same law as the reg1d data set.
Every training sample is a fresh draw from this law (the lecturer's "generator of data"), not a bootstrap of one sample.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402,F401

SIGMA = 0.25
GRID = np.linspace(0, 1, 201)
F_GRID = np.sin(2 * np.pi * GRID)


def truth(x):
    return np.sin(2 * np.pi * np.asarray(x))


def draw(rng, n):
    x = np.sort(rng.uniform(0, 1, n))
    return x, truth(x) + rng.normal(0, SIGMA, n)


def poly_fit(degree):
    """Least squares polynomial in the Legendre basis (stable up to degree about n/2)."""
    def fit(x, y):
        p = np.polynomial.Legendre.fit(x, y, degree, domain=[0, 1])
        return p
    return fit


def predictions(fit, n, m, seed=fk.SEED, grid=GRID):
    """Predictions on grid of m models, each fitted on its own fresh sample of n points. Shape (m, len(grid))."""
    rng = np.random.default_rng(seed)
    out = np.empty((m, len(grid)))
    for i in range(m):
        x, y = draw(rng, n)
        out[i] = fit(x, y)(grid)
    return out


def decompose(pred, grid=GRID):
    """bias^2 and variance averaged over the grid (x is uniform, so the grid mean is the expectation over x)."""
    f = truth(grid)
    m = len(pred)
    var = pred.var(axis=0, ddof=1)
    # The mean of m predictions carries its own noise var / m, which would inflate the squared bias.
    bias2 = float(np.mean((pred.mean(axis=0) - f) ** 2 - var / m))
    return bias2, float(np.mean(var))


def test_error(pred, seed=fk.SEED + 7, n_test=200, grid=GRID):
    """Direct estimate of E (y - mu_X(x))^2 with fresh test pairs, to check the sum bias^2 + variance + sigma^2.

    Each model is scored on its own fresh test set; the test x are the grid points nearest to random draws.
    """
    rng = np.random.default_rng(seed)
    errs = []
    for p in pred:
        idx = rng.integers(0, len(grid), n_test)
        y = truth(grid[idx]) + rng.normal(0, SIGMA, n_test)
        errs.append(np.mean((p[idx] - y) ** 2))
    return float(np.mean(errs))
