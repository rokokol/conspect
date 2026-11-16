"""The two particular solutions A_1, A_2 of the Airy equation y'' + x y = 0.

A_1(0) = 1, A_1'(0) = 0 and A_2(0) = 0, A_2'(0) = 1 give W(0) = 1. The curves come
from scipy.special.airy: the standard Airy functions solve w'' = x w, so
y(x) = w(-x) solves y'' + x y = 0, and A_1, A_2 are fixed by their data at 0.
The truncated power series of the lecture is compared with them as a check.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.special import airy  # noqa: E402

AI0, AIP0, _, _ = airy(0.0)
C1, C2 = AI0, -AIP0


def a1(x):
    ai, _, bi, _ = airy(-x)
    return (ai + bi / np.sqrt(3)) / (2 * C1)


def a2(x):
    ai, _, bi, _ = airy(-x)
    return (ai - bi / np.sqrt(3)) / (2 * C2)


def series(x, first_power, terms=140):
    """Series of the lecture: a_n = -a_{n-3} / (n (n - 1)), a_0 = 1 or a_1 = 1 (first_power 0 or 1)."""
    term = x**first_power
    total = term
    for j in range(1, terms):
        n = 3 * j + first_power
        term = -term * x**3 / (n * (n - 1))
        total += term
    return total


grid = np.linspace(-6, 10, 1200)
check = np.linspace(-6, 6, 25)
assert np.allclose(a1(check), series(check, 0), rtol=1e-7, atol=1e-7)
assert np.allclose(a2(check), series(check, 1), rtol=1e-7, atol=1e-7)
assert np.isclose(a1(0.0), 1) and np.isclose(a2(0.0), 0)
step = 1e-6
assert np.isclose((a1(step) - a1(-step)) / (2 * step), 0, atol=1e-6)
assert np.isclose((a2(step) - a2(-step)) / (2 * step), 1, atol=1e-6)

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
ax.axvline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
ax.plot(grid, a1(grid), color=dufig.SOLUTION, linewidth=2.2, label=r"$A_1(x)$: $A_1(0)=1,\ A_1'(0)=0$")
ax.plot(grid, a2(grid), color=dufig.P["plum"], linewidth=2.2, label=r"$A_2(x)$: $A_2(0)=0,\ A_2'(0)=1$")
ax.set_xlim(-6, 10)
ax.set_ylim(-4, 4)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title(r"Решения уравнения Эйри $y''+xy=0$")
ax.legend(loc="lower right", fontsize=8)

dufig.save(fig, 9, "airy-solutions")
