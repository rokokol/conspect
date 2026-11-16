"""симм-тангенсы.png: graphical solution of the TE eigenvalue equations at V of the worked example."""
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

V = symm_slab.V_EX
YLIM = 9

fig, ax = plt.subplots(figsize=(8.2, 4.6))

# tan X with the branches cut at the asymptotes
X = np.linspace(1e-3, V * 1.12, 20000)
t = np.tan(X)
t[np.abs(t) > 4 * YLIM] = np.nan
ax.plot(X, t, color=mffig.INK, lw=1.3)

Xi = np.linspace(1e-3, V * (1 - 1e-6), 20000)
Yi = np.sqrt(V**2 - Xi**2)
ax.plot(Xi, Yi / Xi, color=mffig.MODE, lw=2.2)
ax.plot(Xi, -Xi / Yi, color=mffig.ODD, lw=2.2, ls="--")
ax.axvline(V, color=mffig.MUTED, lw=1)

# the roots; the last one lies far below the frame
for i, (par, Xr) in enumerate(symm_slab.modes(V)):
    y = np.tan(Xr)
    if abs(y) < YLIM:
        ax.plot(Xr, y, "o", color=mffig.HIGHLIGHT, mec=mffig.INK, ms=6, zorder=5)
    else:
        ax.annotate("", xy=(Xr, -YLIM), xytext=(Xr, -YLIM + 1.2),
                    arrowprops=dict(arrowstyle="-|>", color=mffig.INK, lw=1.2))
        ax.text(Xr - 0.1, -YLIM + 1.5, r"$\mathrm{TE}_{%d}$: $\tan X\approx%.0f$" % (i, y),
                ha="right", color=mffig.INK)

ax.set_xlim(0, V * 1.12)
ax.set_ylim(-YLIM, YLIM)
ax.xaxis.set_major_locator(mticker.MultipleLocator(np.pi / 2))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(symm_slab.pi_half_label))
ax.tick_params(axis="x", labelsize=8)
ax.set_xlabel(r"$X=\varkappa d$")
ax.legend(
    handles=[
        Line2D([], [], color=mffig.INK, lw=1.3, label=r"$\tan X$"),
        Line2D([], [], color=mffig.MODE, lw=2.2, label=r"$Y/X$, чётные"),
        Line2D([], [], color=mffig.ODD, lw=2.2, ls="--", label=r"$-X/Y$, нечётные"),
        Line2D([], [], color=mffig.MUTED, lw=1, label=r"$X=V$"),
        Line2D([], [], marker="o", ls="", color=mffig.HIGHLIGHT, mec=mffig.INK, label="корень"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=5, frameon=False)

mffig.save(fig, 6, "симм-тангенсы")
