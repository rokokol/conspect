"""Neumann functions Y_0, Y_1, Y_2 from scipy.special.yv.

Each Y_m is checked to have the structure (2/pi) J_m(x) ln x + x^(-m) * (even power series),
which is the form of the second solution for integer m.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.special import jv, yv  # noqa: E402

for m in range(3):
    t = np.linspace(0.05, 0.6, 12)
    regular = t**m * (yv(m, t) - 2 / np.pi * jv(m, t) * np.log(t))
    fit = np.polynomial.polynomial.polyfit(t**2, regular, 5)
    t_test = np.array([0.07, 0.33, 0.58])
    predicted = np.polynomial.polynomial.polyval(t_test**2,
                                                 fit)
    exact = t_test**m * (yv(m, t_test) - 2 / np.pi * jv(m, t_test) * np.log(t_test))
    assert np.allclose(predicted, exact, atol=1e-7), m

xs = np.linspace(0.04, 20, 2000)

fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.axhline(0, color=dufig.MUTED, linewidth=0.8, zorder=0)
for m, colour in zip(range(3), (dufig.SOLUTION, dufig.P["plum"], dufig.P["rule"])):
    ax.plot(xs, yv(m, xs), color=colour, linewidth=2.0, label=rf"$Y_{m}(x)$")
ax.set_xlim(0, 20)
ax.set_ylim(-1.6, 0.7)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title(r"Функции Неймана $Y_0,\ Y_1,\ Y_2$")
ax.legend(loc="lower right", fontsize=8)

dufig.save(fig, 9, "bessel-y")
