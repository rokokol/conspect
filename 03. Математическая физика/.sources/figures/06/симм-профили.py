"""симм-профили.png: TE (E_y) and TM (H_y) mode profiles at V of the worked example, shifted by mode number."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mffig  # noqa: E402
import симм_расчёт as symm_slab  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

V = symm_slab.V_EX
q = (symm_slab.N1 / symm_slab.N2) ** 2
OFFSET = 2.6
CORE_PALE = mffig.CORE
xi = np.linspace(-2.5, 2.5, 1500)

fig, axes = plt.subplots(1, 2, figsize=(9.4, 6.4), sharey=True, gridspec_kw={"wspace": 0.28})
for ax, (name, field, qq) in zip(axes, [("TE", r"$E_y$", 1.0), ("TM", r"$H_y$", q)]):
    ms = symm_slab.modes(V, qq)
    ax.axvspan(-1, 1, color=CORE_PALE, lw=0, zorder=0)
    for i, (par, X) in enumerate(ms):
        base = i * OFFSET
        ax.axhline(base, color=mffig.AUX, lw=0.8, zorder=1)
        f = symm_slab.profile(xi, par, X, V)
        ax.plot(xi, base + f, color=mffig.MODE if par == "even" else mffig.ODD,
                ls="-" if par == "even" else "--", lw=2, zorder=3)
        ax.text(2.58, base, rf"$\mathrm{{{name}}}_{i}$", va="center", color=mffig.INK)
    ax.set_xlim(-2.5, 2.5)
    ax.set_xlabel(r"$x/d$")
    ax.set_title(f"{name}: {field}")
    ax.set_yticks([])
axes[0].set_ylabel("поле, сдвинуто по номеру моды")
fig.legend(
    handles=[
        Line2D([], [], color=mffig.MODE, lw=2, label="чётная мода"),
        Line2D([], [], color=mffig.ODD, lw=2, ls="--", label="нечётная мода"),
        plt.Rectangle((0, 0), 1, 1, color=CORE_PALE, label="сердцевина $|x|\\leqslant d$"),
    ],
    loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01))
fig.subplots_adjust(bottom=0.11)

mffig.save(fig, 6, "симм-профили")
