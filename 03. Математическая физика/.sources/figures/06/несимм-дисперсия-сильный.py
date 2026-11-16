"""Dispersion curves n_eff(h) of the strongly asymmetric waveguide: TE on the left, TM on the right."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from несимм_расчёт import STRONG, cutoff, n_eff  # noqa: E402

g, h_max, n_modes = STRONG, 2.5, 5

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4), sharey=True)
for ax, pol in zip(axes, ("TE", "TM")):
    for j in range(n_modes):
        hc = cutoff(j, g, pol)
        hs = hc + 1e-7 + (h_max - hc) * np.linspace(0, 1, 500) ** 2
        ne = [n_eff(j, hv, g, pol) for hv in hs]
        c = mffig.CYCLE[j % len(mffig.CYCLE)]
        ax.plot(hs, ne, color=c, lw=2)
        ax.text(h_max + 0.04, ne[-1] + (0.004 if j == 0 else 0), rf"${pol}_{j}$", color=c, va="center")
        ax.plot([hc], [g.n_s], "o", color=mffig.HIGHLIGHT, ms=5, zorder=5)
    ax.axhline(g.n_f, color=mffig.AUX, ls="--", lw=1.2)
    ax.axhline(g.n_s, color=mffig.AUX, ls=":", lw=1.2)
    ax.text(0.05, g.n_f, r"$n_f$", va="bottom")
    ax.text(0.05, g.n_s, r"$n_s$", va="top")
    ax.set_xlim(0, h_max + 0.3)
    ax.set_ylim(g.n_s - 0.03, g.n_f + 0.03)
    ax.set_title(pol)
    ax.set_xlabel(r"$h$, мкм")
axes[0].set_ylabel(r"$n_{\mathrm{eff}}$")
axes[1].plot([], [], "o", color=mffig.HIGHLIGHT, ms=5, ls="none", label="отсечка")
fig.legend(*axes[1].get_legend_handles_labels(), loc="lower center", frameon=False)
fig.tight_layout(rect=(0, 0.07, 1, 1))
mffig.save(fig, 6, Path(__file__).stem)
