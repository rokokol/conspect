"""Picard iterates for y' = y, y(0) = 1: phi_n is the Taylor polynomial of e^x of degree n."""
import sys
from math import factorial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import cumulative_trapezoid  # noqa: E402

xs = np.linspace(0, 2, 801)

def iterate_colour(n):
    """Later iterates are darker tints of one hue, apart from the solution colour."""
    return dufig.tint(dufig.P["plum"], 0.72 - 0.18 * n)


fig, ax = plt.subplots(figsize=(6.4, 4.4))

# Each iterate is computed by the Picard step itself, phi_n = 1 + int_0^x phi_{n-1}.
phi = np.ones_like(xs)
for n in range(5):
    taylor = sum(xs**k / factorial(k) for k in range(n + 1))
    assert np.allclose(phi, taylor, atol=1e-4)
    ax.plot(xs, phi, color=iterate_colour(n), linewidth=1.4)
    ax.annotate(rf"$\varphi_{n}$", (xs[-1], phi[-1]), xytext=(4, 0),
                textcoords="offset points", va="center", color=iterate_colour(n))
    phi = 1 + cumulative_trapezoid(phi, xs, initial=0)

ax.plot(xs, np.exp(xs), color=dufig.SOLUTION, linewidth=2.4, label=r"решение $e^x$")
ax.set_xlim(0, 2)
ax.set_ylim(0, 7.6)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title(r"Приближения Пикара для $y'=y$")
ax.legend(loc="upper left", fontsize=8)

dufig.save(fig, 3, "picard-iterates")
