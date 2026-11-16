"""Shared data for the nearly collinear demo of lecture 2 (slides 17-19), used by linreg-* and reg-* figures."""
import numpy as np

W_TRUE = np.array([2.68647887, -0.52184084, -1.12776533])  # the true weights on lecture slide 17
N, SIGMA_Y = 100, 0.3


def sample(seed, gap):
    """x1 free, x2 free, x3 = x2 plus a small gap; y = X w_true plus noise."""
    rng = np.random.default_rng(seed)
    x1, x2, e, eta = rng.normal(size=(4, N))
    X = np.c_[x1, x2, x2 + gap * e]
    return X, X @ W_TRUE + SIGMA_Y * eta


def ols(X, y):
    return np.linalg.solve(X.T @ X, X.T @ y)


def ridge(X, y, lam):
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)
