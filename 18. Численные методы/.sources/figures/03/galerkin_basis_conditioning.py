"""Galerkin and Galerkin-Petrov for y - int_{-1}^1 e^{xs} y ds = f, exact y = e^x: error and conditioning against n."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from numpy.polynomial import legendre as leg  # noqa: E402

nodes, weights = leg.leggauss(80)
x_plot = np.linspace(-1, 1, 401)
kernel = np.exp(nodes[:, None] * nodes[None, :])
z = nodes + 1
f_nodes = np.exp(nodes) - (np.exp(z) - np.exp(-z)) / z


def legendre(t, j):
    return leg.legval(t, [0] * j + [1])


def chebyshev(t, j):
    return np.cos(j * np.arccos(np.clip(t, -1, 1)))


def monomial(t, j):
    return t**j


def run(phi, psi, n):
    """Trial functions phi_j and test functions psi_i, j, i = 0..n-1; returns max error and cond(A)."""
    ph = np.array([phi(nodes, j) for j in range(n)])
    ps = np.array([psi(nodes, i) for i in range(n)])
    a = (ps * weights) @ ph.T - (ps * weights) @ ((kernel * weights[None, :]) @ ph.T)
    c = np.linalg.solve(a, (ps * weights) @ f_nodes)
    y = sum(c[j] * phi(x_plot, j) for j in range(n))
    return np.abs(y - np.exp(x_plot)).max(), np.linalg.cond(a)


ns = np.arange(1, 13)
cases = [
    ("$\\psi_i=\\varphi_i$, Лежандр", legendre, legendre, nmfig.CYCLE[0], "o", "-"),
    ("$\\psi_i=T_i$, $\\varphi_j=P_j$", legendre, chebyshev, nmfig.CYCLE[1], "s", "--"),
    ("$\\psi_i=\\varphi_i=x^i$", monomial, monomial, nmfig.CYCLE[2], "^", "-"),
]
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
for label, phi, psi, color, marker, ls in cases:
    res = [run(phi, psi, n) for n in ns]
    axes[0].semilogy(ns, [r[0] for r in res], marker=marker, ms=4, ls=ls, color=color, label=label)
    axes[1].semilogy(ns, [r[1] for r in res], marker=marker, ms=4, ls=ls, color=color, label=label)
axes[0].set_ylabel(r"$\max|y-\widetilde y|$")
axes[1].set_ylabel(r"$\mathrm{cond}\,A$")
for ax in axes:
    ax.set_xlabel("число функций $n$")
    ax.grid(True, which="major")
axes[0].legend()
nmfig.save(fig, 3, "galerkin_basis_conditioning")
