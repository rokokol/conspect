"""Numerics of the round weakly guiding waveguide, shared by the figures of its note.

The problem: -Δu = λ²u in the core r<1, -Δu = (λ²-V²)u outside, u and ∂u/∂r continuous on r=1,
partial radiation condition at infinity. The characteristic equation of the m-th azimuthal family is
det A_m(V, λ) = 0 with A_m built from J_m and the Hankel function H_m^(1).
"""
import numpy as np
from scipy.optimize import brentq, root
from scipy.special import hankel1, jn_zeros, jv, kv

EPS_I, EPS_E = 2.3839, 2.2124
DELTA = EPS_I - EPS_E


def det(V, lam, m):
    """Determinant of the matrix A_m(V, λ) of the characteristic equation."""
    a = np.sqrt(lam * lam - V * V + 0j)
    A = np.array(
        [
            [jv(m, lam), -hankel1(m, a)],
            [m * jv(m, lam) - lam * jv(m + 1, lam), -m * hankel1(m, a) + a * hankel1(m + 1, a)],
        ],
        dtype=complex,
    )
    return np.linalg.det(A)


def cutoff(m):
    """First cutoff point of the family m: the root of λJ_{m+1}(λ) = 2mJ_m(λ), i.e. of J_{m-1}.

    For m = 0 the first root is λ = 0 (the fundamental mode has no cutoff).
    """
    if m == 0:
        return 0.0
    return float(jn_zeros(m - 1, 1)[0])


def _guided_eq(lam, V, m):
    kappa = np.sqrt(V * V - lam * lam)
    return lam * jv(m + 1, lam) * kv(m, kappa) - kappa * kv(m + 1, kappa) * jv(m, lam)


def guided_root(V, m, n=1, scan=4000):
    """n-th real root 0 < λ < V of the guided equation λJ_{m+1}(λ)K_m(κ) = κK_{m+1}(κ)J_m(λ), κ = √(V²-λ²)."""
    grid = np.linspace(1e-6, V * (1 - 1e-12), scan)
    f = _guided_eq(grid, V, m)
    roots = [
        brentq(_guided_eq, grid[i], grid[i + 1], args=(V, m), xtol=1e-14)
        for i in range(scan - 1)
        if f[i] * f[i + 1] < 0
    ]
    return roots[n - 1] if len(roots) >= n else None


def complex_root(V, m, guess):
    """Newton-type refinement of a complex root of det A_m = 0 from the starting value guess."""

    def system(x):
        d = det(V, x[0] + 1j * x[1], m)
        return [d.real, d.imag]

    s = root(system, [guess.real, guess.imag], tol=1e-14)
    return s.x[0] + 1j * s.x[1]


def branch(m, V_min=0.02, V_max=10.0, n_left=500, n_right=500):
    """The first root λ(V) of the family m on [V_min, V_max].

    Right of the cutoff the root is real and found by bracketing. Left of it the root is complex and
    is followed from the cutoff point by continuation in V. Returns the arrays V and λ.
    """
    Vc = cutoff(m)
    if m == 0:
        V = np.linspace(V_min, V_max, n_left + n_right)
        return V, np.array([guided_root(v, 0) for v in V], dtype=complex)
    V_right = np.linspace(Vc, V_max, n_right)[1:]
    lam_right = np.array([guided_root(v, m) for v in V_right], dtype=complex)
    V_left = np.linspace(Vc, V_min, n_left)[1:]
    lam_left, prev = [], Vc + 0j
    for v in V_left:
        prev = complex_root(v, m, prev)
        lam_left.append(prev)
    V = np.concatenate([V_left[::-1], [Vc], V_right])
    lam = np.concatenate([lam_left[::-1], [Vc + 0j], lam_right])
    return V, lam


def beta(V, lam):
    """Propagation constant β = √((V²ε_i - λ²(ε_i-ε_e)) / (ε_i-ε_e))."""
    return np.sqrt((V * V * EPS_I - lam * lam * DELTA) / DELTA + 0j)


def field(r, phi, m, V, lam):
    """Eigenfunction (9), (10) of the family cos(mφ) on the grid of polar coordinates (r, φ)."""
    a = np.sqrt(lam * lam - V * V + 0j)
    r = np.asarray(r, dtype=float)
    inside = hankel1(m, a) / jv(m, lam) * jv(m, lam * np.minimum(r, 1.0))
    outside = hankel1(m, a * np.maximum(r, 1.0))
    return np.where(r < 1, inside, outside) * np.cos(m * phi)
