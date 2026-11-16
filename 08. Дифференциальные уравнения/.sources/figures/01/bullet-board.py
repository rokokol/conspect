"""The bullet in a board: the set-up and the solved motion for m x'' = -k (x')^2.

The bullet enters at x = 0 with 200 m/s and leaves at x = 0.1 m with 80 m/s.
With alpha = m/k the speed is v(t) = 200 alpha / (200 t + alpha); alpha follows
from x(T) = 0.1 and T = 3 alpha / 400. The speed is integrated numerically and
checked against the closed form.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

V0, V1, L = 200.0, 80.0, 0.1
ALPHA = L / np.log(5 / 2)
T = 3 * ALPHA / 400


def rhs(t, s):
    x, v = s
    return [v, -v**2 / ALPHA]


sol = solve_ivp(rhs, (0, T), [0.0, V0], dense_output=True, rtol=1e-11, atol=1e-12)
assert abs(sol.y[0, -1] - L) < 1e-8 and abs(sol.y[1, -1] - V1) < 1e-6

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.0, 3.6), gridspec_kw={"width_ratios": [1.05, 1]})

ax0.add_patch(Rectangle((0, -0.5), L, 1.0, color=dufig.tint(dufig.FIELD, 0.35), zorder=1))
ax0.plot([0, 0], [-0.5, 0.5], color=dufig.INK, lw=1.4)
ax0.plot([L, L], [-0.5, 0.5], color=dufig.INK, lw=1.4)
ax0.add_patch(FancyArrowPatch((-0.16, 0), (-0.01, 0), mutation_scale=18, color=dufig.SOLUTION, lw=2.2))
ax0.add_patch(FancyArrowPatch((L + 0.01, 0), (L + 0.12, 0), mutation_scale=18, color=dufig.SOLUTION, lw=2.2))
ax0.annotate(r"$200$ м/с", (-0.085, 0.07), ha="center", color=dufig.INK)
ax0.annotate(r"$80$ м/с", (L + 0.065, 0.07), ha="center", color=dufig.INK)
ax0.annotate("", (0, -0.62), (L, -0.62), arrowprops=dict(arrowstyle="<->", color=dufig.MUTED))
ax0.annotate(r"$0{,}1$ м", (L / 2, -0.78), ha="center", color=dufig.INK)
ax0.annotate(r"$t=0$", (0, 0.58), ha="center", color=dufig.INK)
ax0.annotate(r"$t=T$", (L, 0.58), ha="center", color=dufig.INK)
ax0.xaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",").replace("-", "−")))
ax0.set_xlim(-0.2, 0.22)
ax0.set_ylim(-0.95, 0.85)
ax0.set_xlabel(r"$x$, м")
ax0.set_yticks([])
ax0.set_title("Пуля и доска")

tt = np.linspace(0, T, 400)
ax1.plot(tt * 1e3, sol.sol(tt)[1], color=dufig.SOLUTION, lw=2.4)
ax1.plot([T * 1e3], [V1], "o", color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK, markersize=7, zorder=4)
ax1.plot([0], [V0], "o", color=dufig.INK, markersize=5, zorder=4)
ax1.axhline(V1, color=dufig.FIELD, lw=1.0, ls="--", zorder=0)
ax1.axvline(T * 1e3, color=dufig.FIELD, lw=1.0, ls="--", zorder=0)
ax1.set_xticks([0, T * 1e3])
ax1.set_xticklabels([r"$0$", r"$T\approx0{,}82$"])
ax1.set_yticks([V1, V0])
ax1.set_xlabel(r"$t$, мс")
ax1.set_ylabel(r"$v=x'$, м/с")
ax1.set_title("Скорость в доске")

fig.tight_layout()
dufig.save(fig, 1, "bullet-board")
