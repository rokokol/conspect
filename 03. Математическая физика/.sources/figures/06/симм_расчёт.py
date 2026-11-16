"""Roots and profiles of a symmetric planar waveguide, shared by the симм-* figures.

X = kappa*d and Y = gamma*d lie on the circle X^2 + Y^2 = V^2. A TE mode solves
tan X = Y/X (even) or tan X = -X/Y (odd). A TM mode has the same form with
the factor q = (n1/n2)^2: tan X = q*Y/X (even) or tan X = -X/(q*Y) (odd).
"""
import numpy as np
from scipy.optimize import brentq

# The parameters of the worked example of the lecture notebook
N1, N2, LAM, D = 1.45, 1.44, 1.55e-6, 16e-6
K0 = 2 * np.pi / LAM
V_EX = K0 * D * np.sqrt(N1**2 - N2**2)


def modes(V, q=1.0):
    """All guided modes at V as a list of (parity, X), ordered by X.

    Branch m of the roots lies in (m*pi/2, (m+1)*pi/2): even for m even, odd for m odd.
    """
    out = []
    m = 0
    while m * np.pi / 2 < V:
        a = m * np.pi / 2 + 1e-12
        b = min((m + 1) * np.pi / 2 - 1e-12, V - 1e-12)
        if m % 2 == 0:
            par = "even"

            def f(X):
                return X * np.sin(X) - q * np.sqrt(V**2 - X**2) * np.cos(X)
        else:
            par = "odd"

            def f(X):
                return q * np.sqrt(V**2 - X**2) * np.sin(X) + X * np.cos(X)
        if f(a) * f(b) < 0:
            out.append((par, brentq(f, a, b, xtol=1e-14)))
        m += 1
    return out


def pi_half_label(x, pos=None):
    """Tick label of a multiple of pi/2: 0, pi/2, pi, 3pi/2, 2pi, ... without a leading 1."""
    n = int(round(2 * x / np.pi))
    if n == 0:
        return "0"
    if n % 2 == 0:
        k = n // 2
        return r"$\pi$" if k == 1 else rf"${k}\pi$"
    return r"$\pi/2$" if n == 1 else rf"${n}\pi/2$"


def profile(x_over_d, par, X, V):
    """Field of a mode against x/d, unit amplitude of the core cosine or sine."""
    xi = np.asarray(x_over_d, dtype=float)
    Y = np.sqrt(V**2 - X**2)
    f = np.cos if par == "even" else np.sin
    core = f(X * xi)
    edge = f(X)
    sign = 1.0 if par == "even" else np.sign(xi)
    tail = sign * edge * np.exp(-Y * (np.abs(xi) - 1))
    return np.where(np.abs(xi) <= 1, core, tail)
