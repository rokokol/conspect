"""Radial profile |u(r, 0)| of a guided family (V = 8) next to a leaky one (V = 0.5), m = 1..4."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import круглый_расчёт as cc  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def leaky_root(V, m):
    """First complex root of the family m at V, followed from the cutoff point by continuation."""
    lam = cc.cutoff(m) + 0j
    for v in np.linspace(cc.cutoff(m), V, 300)[1:]:
        lam = cc.complex_root(v, m, lam)
    return lam


r = np.linspace(0, 3, 1500)
fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2), sharey=True, constrained_layout=True)
for ax, V, title in zip(axes, (8.0, 0.5), (f"$V={mffig.num(8, 0)}$: поверхностные", f"$V={mffig.num(0.5, 1, math=True)}$: вытекающие")):
    for m in range(1, 5):
        lam = cc.guided_root(V, m) if V > cc.cutoff(m) else leaky_root(V, m)
        u = np.abs(cc.field(r, 0.0, m, V, lam))
        u /= u[np.argmin(np.abs(r - 1))]
        ax.semilogy(r, u, color=mffig.CYCLE[m], linewidth=2, label=f"$m={m}$")
    ax.axvline(1, color=mffig.INK, linestyle="--", linewidth=1.2)
    ax.set_title(title)
    ax.set_xlabel("$r$")
    ax.set_xlim(0, 3)
    ax.grid(True, color=mffig.AUX, linewidth=0.6)
axes[0].set_ylabel(r"$|u(r,0)|\,/\,|u(1,0)|$")
axes[0].set_ylim(1e-7, 1e4)
axes[0].legend(frameon=False, loc="lower left")
axes[1].text(1.04, 3e3, "$r=1$", color=mffig.INK, va="top")
mffig.save(fig, 6, "круглый-радиальные-профили")
