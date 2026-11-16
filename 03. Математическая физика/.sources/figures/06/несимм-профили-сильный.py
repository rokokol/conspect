"""TE and TM profiles of the first three modes of the strongly asymmetric waveguide, h = 1.1 um."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from несимм_рисунок import POL_STYLE, mode_handles, pol_handles  # noqa: E402
from несимм_расчёт import STRONG, profile  # noqa: E402

g, h = STRONG, 1.1
z = np.linspace(-0.5, h + 0.4, 3000)

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.axvspan(-0.5, 0, color=mffig.CLADDING, lw=0)
ax.axvspan(h, h + 0.4, color=mffig.CLADDING, lw=0)
ax.axvspan(0, h, color=mffig.CORE, lw=0)
for pol in ("TE", "TM"):
    for j in range(3):
        ax.plot(z, profile(z, j, h, g, pol), color=mffig.CYCLE[j], ls=POL_STYLE[pol], lw=2)
ax.axhline(0, color=mffig.MUTED, lw=0.8)
ax.text(-0.25, 1.0, r"подложка $n_s$", ha="center", va="top")
ax.text(h / 2, 1.0, r"волноводный слой $n_f$", ha="center", va="top")
ax.text(h + 0.2, 1.0, r"$n_a$", ha="center", va="top")
ax.set_xlim(-0.5, h + 0.4)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel(r"$z$, мкм")
ax.set_ylabel(r"нормированные $E_y$ и $H_y$")
ax.legend(handles=mode_handles(range(3)) + pol_handles(), loc="upper center",
          bbox_to_anchor=(0.5, -0.17), ncol=5, frameon=False)
fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
