"""Confinement factor of the first four TE modes of the weakly guiding waveguide against h.

The TM curves differ from these by less than 2.1e-3 and are left out."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from несимм_рисунок import mode_handles  # noqa: E402
from несимм_расчёт import WEAK, confinement, cutoff  # noqa: E402

g, h_max = WEAK, 20.0

fig, ax = plt.subplots(figsize=(7.2, 4.2))
for j in range(4):
    hc = cutoff(j, g, "TE")
    hs = hc + 1e-4 + (h_max - hc) * np.linspace(0, 1, 400) ** 1.5
    ax.plot(hs, [confinement(j, hv, g, "TE") for hv in hs], color=mffig.CYCLE[j], lw=2)
ax.set_xlim(0, h_max)
ax.set_ylim(0, 1.04)
ax.set_xlabel(r"$h$, мкм")
ax.set_ylabel(r"$\Gamma$")
ax.legend(handles=mode_handles(range(4)), loc="upper center", bbox_to_anchor=(0.5, -0.17),
          ncol=4, frameon=False)
fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
