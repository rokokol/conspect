"""Shooting method: y1 + eps*y2 meets the left boundary condition for every eps, one eps meets the right one.

The equation is y'' + (1+x) y' + (0.5 cos x - 1) y = sin 3x + x on [0, 2] with
y'(0) + 0.7 y(0) = 0 and y'(2) - 0.4 y(2) = 0.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

p = lambda x: 1 + x
q = lambda x: 0.5 * np.cos(x) - 1
f = lambda x: np.sin(3 * x) + x
x1, x2 = 0.0, 2.0
alpha, beta = 0.7, -0.4
gamma, delta = 0.3, 1.0
opts = dict(rtol=1e-11, atol=1e-12, dense_output=True)

y1 = solve_ivp(lambda x, u: [u[1], f(x) - p(x) * u[1] - q(x) * u[0]],
               (x1, x2), [gamma, -alpha * gamma], **opts)
y2 = solve_ivp(lambda x, u: [u[1], -p(x) * u[1] - q(x) * u[0]],
               (x1, x2), [delta, -alpha * delta], **opts)

v1, d1 = y1.sol(x2)
v2, d2 = y2.sol(x2)
eps = -(d1 + beta * v1) / (d2 + beta * v2)

xs = np.linspace(x1, x2, 400)
Y1 = y1.sol(xs)[0]
Y2 = y2.sol(xs)[0]
answer = Y1 + eps * Y2

# The combination meets the right condition: y'(x2) + beta y(x2) = 0.
resid = y1.sol(x2)[1] + eps * y2.sol(x2)[1] + beta * (y1.sol(x2)[0] + eps * y2.sol(x2)[0])
assert abs(resid) < 1e-9

fig, ax = plt.subplots(figsize=(6.6, 4.6))
for k, e in enumerate(np.linspace(-1.5, 6.5, 9)):
    ax.plot(xs, Y1 + e * Y2, color=dufig.FIELD, linewidth=1.1,
            label=r"$y_1+\varepsilon' y_2$ при разных $\varepsilon'$" if k == 0 else None)
ax.plot(xs, Y1, color=dufig.HIGHLIGHT, linewidth=1.8, linestyle="--",
        label=r"$y_1$, то есть $\varepsilon'=0$")
ax.plot(xs, answer, color=dufig.SOLUTION, linewidth=2.6,
        label=rf"$y_1+\varepsilon y_2$, $\varepsilon={dufig.num(eps, 2, math=True)}$")
for xb in (x1, x2):
    ax.axvline(xb, color=dufig.MUTED, linewidth=0.9)
ax.plot([x1], [answer[0]], "o", color=dufig.SOLUTION)
ax.plot([x2], [answer[-1]], "o", color=dufig.SOLUTION)
note_box = dict(boxstyle="round,pad=0.3", fc="white", ec=dufig.MUTED, lw=0.6)
ax.annotate(r"$y'+\alpha y=0$" "\nпри любом $\\varepsilon'$", (x1, answer[0]),
            xytext=(30, -75), textcoords="offset points", fontsize=8, color=dufig.INK,
            bbox=note_box, arrowprops=dict(arrowstyle="-", color=dufig.MUTED))
ax.annotate(r"$y'+\beta y=0$" "\nтолько при $\\varepsilon$", (x2, answer[-1]),
            xytext=(-95, -75), textcoords="offset points", fontsize=8, color=dufig.INK,
            bbox=note_box, arrowprops=dict(arrowstyle="-", color=dufig.MUTED))
ax.set_ylim(-1.5, 10.5)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
ax.set_title("Метод пристрелки")
ax.legend(loc="upper left", fontsize=8)

dufig.save(fig, 10, "shooting")
