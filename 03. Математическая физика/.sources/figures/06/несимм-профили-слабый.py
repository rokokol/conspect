"""TE profiles of the first three modes of the weakly guiding waveguide, h = 32 um."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from несимм_расчёт import WEAK, profile  # noqa: E402

g, h = WEAK, 32.0
z = np.linspace(-12, h + 12, 2000)

fig, ax = plt.subplots(figsize=(7.2, 4))
ax.axvspan(-12, 0, color=mffig.CLADDING, lw=0)
ax.axvspan(h, h + 12, color=mffig.CLADDING, lw=0)
ax.axvspan(0, h, color=mffig.CORE, lw=0)
for j in range(3):
    ax.plot(z, profile(z, j, h, g, "TE"), color=mffig.CYCLE[j], lw=2, label=rf"$j={j}$")
ax.axhline(0, color=mffig.MUTED, lw=0.8)
ax.set_xlim(-12, h + 12)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel(r"$z$, мкм")
ax.set_ylabel("нормированный $E_y$")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False)
fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
