"""Confinement factor of the first five modes of the strongly asymmetric waveguide against h."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from несимм_рисунок import POL_STYLE, mode_handles  # noqa: E402
from несимм_расчёт import STRONG, confinement, cutoff  # noqa: E402

g, h_max = STRONG, 2.5

fig, ax = plt.subplots(figsize=(7.2, 4.2))
for pol in ("TE", "TM"):
    for j in range(5):
        hc = cutoff(j, g, pol)
        hs = hc + 1e-6 + (h_max - hc) * np.linspace(0, 1, 400) ** 1.5
        ax.plot(hs, [confinement(j, hv, g, pol) for hv in hs],
                color=mffig.CYCLE[j], ls=POL_STYLE[pol], lw=2)
ax.set_xlim(0, h_max)
ax.set_ylim(0, 1.04)
ax.set_xlabel(r"$h$, мкм")
ax.set_ylabel(r"$\Gamma$")
# TM is weighed by |H_y|^2, which is not the power share of a TM mode: the key says so
pol_keys = [Line2D([], [], color=mffig.INK, ls=POL_STYLE["TE"], lw=1.6, label=r"TE, по $|E_y|^2$"),
            Line2D([], [], color=mffig.INK, ls=POL_STYLE["TM"], lw=1.6, label=r"TM, по $|H_y|^2$")]
ax.legend(handles=mode_handles(range(5)) + pol_keys, loc="upper center",
          bbox_to_anchor=(0.5, -0.17), ncol=7, frameon=False)
fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
