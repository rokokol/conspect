"""Ritz approximations of the characteristic numbers k^2 pi^2 of the kernel x(1-s), x<=s, against the number of basis functions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from scipy.linalg import eigh  # noqa: E402

x, s = sp.symbols("x s")


def apply_kernel(p):
    """(Kp)(x) = (1-x) int_0^x s p ds + x int_x^1 (1-s) p ds, the solution of -u''=p, u(0)=u(1)=0."""
    ps = p.subs(x, s)
    return sp.expand((1 - x) * sp.integrate(s * ps, (s, 0, x)) + x * sp.integrate((1 - s) * ps, (s, x, 1)))


NMAX = 10
basis = [sp.legendre(j, 2 * x - 1) for j in range(NMAX)]
kb = [apply_kernel(b) for b in basis]
G = np.array([[float(sp.integrate(sp.expand(kb[k] * basis[j]), (x, 0, 1))) for k in range(NMAX)] for j in range(NMAX)])
M = np.diag([1 / (2 * j + 1) for j in range(NMAX)])

fig, ax = plt.subplots(figsize=(6.4, 3.8))
for k, color in zip((1, 2, 3), nmfig.CYCLE):
    ns, errs = [], []
    for n in range(k, NMAX + 1):
        sigma = eigh(G[:n, :n], M[:n, :n], eigvals_only=True)[::-1]
        lam = 1 / sigma[k - 1]
        ns.append(n)
        errs.append(lam / (k * np.pi) ** 2 - 1)
    ax.semilogy(ns, errs, marker="o", ms=4, color=color, label=rf"$\lambda_{k}^{{(n)}}$, $\lambda_{k}={k}^2\pi^2$")
ax.set_xlabel("число функций $n$ в $V_n$")
ax.set_ylabel(r"относительная погрешность $\lambda_k^{(n)}/\lambda_k-1$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 4, "ritz_green_kernel")
