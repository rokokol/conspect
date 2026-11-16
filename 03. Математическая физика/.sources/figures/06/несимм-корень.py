"""The residual F(n_eff) of the TE dispersion equation: monotone, one root per mode number."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from несимм_расчёт import STRONG, n_eff, residual  # noqa: E402

g, h = STRONG, 1.1
x = np.linspace(g.n_s * (1 + 1e-9), g.n_f * (1 - 1e-9), 600)

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.axhline(0, color=mffig.MUTED, lw=1)
for j in range(5):
    c = mffig.CYCLE[j % len(mffig.CYCLE)]
    ax.plot(x, residual(x, j, h, g, "TE"), color=c, lw=2, label=rf"$j={j}$")
    root = n_eff(j, h, g, "TE")
    if root is not None:
        ax.plot([root], [0], "o", color=mffig.HIGHLIGHT, ms=7, zorder=5)
ax.plot([], [], "o", color=mffig.HIGHLIGHT, ms=7, ls="none", label="корень")
ax.set_xlim(g.n_s, g.n_f)
ax.set_ylim(-17, 6)
ax.set_xlabel(r"$n_{\mathrm{eff}}$")
ax.set_ylabel(r"$F(n_{\mathrm{eff}},j)$")
ax.legend(ncol=3, loc="lower left")
fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
