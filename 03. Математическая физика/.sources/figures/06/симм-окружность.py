"""симм-окружность.png: roots as intersections of the circle X^2+Y^2=V^2 with the TE branches."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mffig  # noqa: E402
import симм_расчёт as symm_slab  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

n1, n2, lam = 3.5, 1.45, 1.55e-6
K0NA = 2 * np.pi / lam * np.sqrt(n1**2 - n2**2)  # k0 sqrt(n1^2 - n2^2), 1/m
cases = [0.13e-6, 0.25e-6]

fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.0))
for ax, d in zip(axes, cases):
    V = K0NA * d
    lim = max(V * 1.08, 1.0)
    # branches Y = X tan X (even) and Y = -X cot X (odd) on their intervals of width pi/2
    m = 0
    while m * np.pi / 2 < lim:
        a, b = m * np.pi / 2, (m + 1) * np.pi / 2
        x = np.linspace(a + 1e-6, b - 1e-6, 2000)
        y = x * np.tan(x) if m % 2 == 0 else -x / np.tan(x)
        y[y > 3 * lim] = np.nan
        ax.plot(x, y, color=mffig.MODE if m % 2 == 0 else mffig.ODD,
                lw=2.2, ls="-" if m % 2 == 0 else "--")
        ax.axvline(b, color=mffig.AUX, lw=0.8, zorder=0)
        m += 1
    th = np.linspace(0, np.pi / 2, 400)
    ax.plot(V * np.cos(th), V * np.sin(th), color=mffig.INK, lw=1.5)
    for i, (par, Xr) in enumerate(symm_slab.modes(V)):
        ax.plot(Xr, np.sqrt(V**2 - Xr**2), "o", color=mffig.HIGHLIGHT, mec=mffig.INK, ms=6, zorder=5)
        ax.annotate(rf"$\mathrm{{TE}}_{i}$", (Xr, np.sqrt(V**2 - Xr**2)),
                    textcoords="offset points", xytext=(6, 5), color=mffig.INK)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_aspect("equal")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(np.pi / 2))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(symm_slab.pi_half_label))
    ax.tick_params(axis="x", labelsize=8)
    ax.set_xlabel(r"$X=\varkappa d$")
    ax.set_ylabel(r"$Y=\gamma d$")
    ax.set_title(rf"$d={mffig.num(d * 1e6, 2, math=True)}$ мкм, $V={mffig.num(V, 2, math=True)}$")

fig.legend(
    handles=[
        Line2D([], [], color=mffig.INK, lw=1.5, label=r"$X^2+Y^2=V^2$"),
        Line2D([], [], color=mffig.MODE, lw=2.2, label=r"$Y=X\tan X$, чётные"),
        Line2D([], [], color=mffig.ODD, lw=2.2, ls="--", label=r"$Y=-X\cot X$, нечётные"),
        Line2D([], [], marker="o", ls="", color=mffig.HIGHLIGHT, mec=mffig.INK, label="корень"),
    ],
    loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.subplots_adjust(bottom=0.22, wspace=0.3)

mffig.save(fig, 6, "симм-окружность")
