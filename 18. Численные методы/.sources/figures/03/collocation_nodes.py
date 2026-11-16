"""Collocation for y = f + int_0^pi (sin s + cos x) y ds, exact y = e^x: equispaced and Chebyshev nodes, Legendre and monomial bases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from numpy.polynomial import legendre as leg  # noqa: E402

a, b = 0.0, np.pi
g_nodes, g_weights = leg.leggauss(120)
s = (b - a) / 2 * g_nodes + (a + b) / 2
w = (b - a) / 2 * g_weights
x_plot = np.linspace(a, b, 401)


def f(x):
    return np.exp(x) - (1 + np.exp(np.pi)) / 2 + (1 - np.exp(np.pi)) * np.cos(x)


def legendre(x, j):
    return leg.legval(2 * (x - a) / (b - a) - 1, [0] * j + [1])


def monomial(x, j):
    return x**j


def run(basis, pts):
    n1 = len(pts)
    m = np.zeros((n1, n1))
    for j in range(n1):
        phi = basis(s, j)
        for i in range(n1):
            m[i, j] = basis(pts[i], j) - np.sum(w * (np.sin(s) + np.cos(pts[i])) * phi)
    c = np.linalg.solve(m, f(pts))
    y = sum(c[j] * basis(x_plot, j) for j in range(n1))
    return np.abs(y - np.exp(x_plot)).max() / np.exp(b), np.linalg.cond(m, np.inf)


def equispaced(n1):
    return np.linspace(a, b, n1)


def chebyshev_points(n1):
    k = np.arange(n1)
    return (a + b) / 2 - (b - a) / 2 * np.cos((2 * k + 1) * np.pi / (2 * n1))


ns = np.arange(2, 31)
cases = [
    ("равномерные узлы, Лежандр", legendre, equispaced, nmfig.CYCLE[0], "o"),
    ("равномерные узлы, $x^j$", monomial, equispaced, nmfig.CYCLE[2], "^"),
    ("узлы Чебышёва, Лежандр", legendre, chebyshev_points, nmfig.CYCLE[1], "s"),
]
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
for label, basis, pts, color, marker in cases:
    res = [run(basis, pts(n)) for n in ns]
    axes[0].semilogy(ns, np.maximum([r[0] for r in res], 1e-16), marker=marker, ms=4, color=color, label=label)
    axes[1].semilogy(ns, [r[1] for r in res], marker=marker, ms=4, color=color, label=label)
axes[0].set_ylabel("относительная погрешность")
axes[1].set_ylabel(r"$\mathrm{cond}\,M$")
for ax in axes:
    ax.set_xlabel("число функций $n$")
    ax.grid(True, which="major")
axes[1].legend()
nmfig.save(fig, 3, "collocation_nodes")
