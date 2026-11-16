"""Synthetic centred planar cloud shared by the two PCA figures: elongated, rotated, fixed seed."""
import numpy as np

N = 100
ANGLE = np.deg2rad(32.0)


def cloud():
    """Return X (N x 2, centred), covariance C, eigenvalues lam (descending), eigenvectors W (columns)."""
    rng = np.random.default_rng(7)
    z = rng.standard_normal((N, 2)) * np.array([2.3, 0.8])
    rot = np.array([[np.cos(ANGLE), -np.sin(ANGLE)], [np.sin(ANGLE), np.cos(ANGLE)]])
    x = z @ rot.T
    x = x - x.mean(axis=0)
    c = x.T @ x / (N - 1)
    lam, w = np.linalg.eigh(c)
    lam, w = lam[::-1], w[:, ::-1]
    for j in range(2):                      # fix the sign of each component: positive first coordinate
        if w[0, j] < 0:
            w[:, j] = -w[:, j]
    assert np.allclose(x.mean(axis=0), 0)
    assert np.allclose(c, c.T) and np.all(lam >= 0) and lam[0] > lam[1]
    assert np.allclose(w.T @ w, np.eye(2))
    assert np.allclose(c @ w, w * lam)
    return x, c, lam, w
