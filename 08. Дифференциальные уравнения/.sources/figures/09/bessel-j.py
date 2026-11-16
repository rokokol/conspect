"""Bessel functions J_0, J_1, J_2 from scipy.special.jv, checked against the power series of the lecture."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.special import factorial, gamma, jv  # noqa: E402


def series(m, x, terms=60):
    """J_m(x) = sum (-1)^j / (Gamma(m+j+1) j!) (x/2)^(2j+m)."""
    return sum((-1) ** j / (gamma(m + j + 1) * factorial(j)) * (x / 2) ** (2 * j + m)
               for j in range(terms))


xs = np.linspace(0, 20, 1000)
for m in range(3):
    assert np.allclose(series(m, xs[:500]), jv(m, xs[:500]), atol=1e-9)

fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
for m, colour in zip(range(3), (dufig.SOLUTION, dufig.P["plum"], dufig.P["rule"])):
    ax.plot(xs, jv(m, xs), color=colour, linewidth=2.0, label=rf"$J_{m}(x)$")
ax.set_xlim(0, 20)
ax.set_ylim(-0.5, 1.05)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title(r"Функции Бесселя $J_0,\ J_1,\ J_2$")
ax.legend(loc="upper right", fontsize=8)

dufig.save(fig, 9, "bessel-j")
