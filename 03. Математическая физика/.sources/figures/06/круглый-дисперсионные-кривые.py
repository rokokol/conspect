"""Eigenvalues λ(V) of the first root of the families m = 0..4 with the cutoff points."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import круглый_расчёт as cc  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

fig, ax = plt.subplots(figsize=(7.2, 5.2))
ax.plot([0, 10], [0, 10], "-.", color=mffig.INK, linewidth=1.4, zorder=2)
handles = []
for m in range(5):
    V, lam = cc.branch(m)
    color = mffig.CYCLE[m]
    ax.plot(V, np.abs(lam.real), "-", color=color, linewidth=2, zorder=3)
    ax.plot(V, np.abs(lam.imag), "--", color=color, linewidth=1.6, alpha=0.8, zorder=3)
    Vc = cc.cutoff(m)
    ax.plot([Vc], [Vc], "o", color=mffig.HIGHLIGHT, markeredgecolor=mffig.INK, markersize=7, zorder=5)
    # the point m = 0 sits in the corner of the axes: its label goes above the diagonal, clear of the tick labels
    label, offset = ("0", (3, 14)) if m == 0 else (mffig.num(Vc, 3), (7, -15))
    ax.annotate(label, (Vc, Vc), xytext=offset, textcoords="offset points", color=mffig.INK, fontsize=9, zorder=6)
    handles.append(Line2D([], [], color=color, linewidth=2, label=f"$m={m}$"))

handles += [
    Line2D([], [], color=mffig.INK, linewidth=2, linestyle="-", label=r"$|\mathrm{Re}\,\lambda|$"),
    Line2D([], [], color=mffig.INK, linewidth=1.6, linestyle="--", label=r"$|\mathrm{Im}\,\lambda|$"),
    Line2D([], [], color=mffig.INK, linewidth=1.4, linestyle="-.", label=r"$\lambda=V$"),
    Line2D([], [], color="none", marker="o", markerfacecolor=mffig.HIGHLIGHT, markeredgecolor=mffig.INK, markersize=7, label="точка отсечки"),
]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel(r"$V$")
ax.set_ylabel(r"$\lambda$", rotation=0, labelpad=12)
ax.set_title(r"Первый корень $\lambda_{m1}(V)$")
ax.grid(True, color=mffig.AUX, linewidth=0.6)
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False)
mffig.save(fig, 6, "круглый-дисперсионные-кривые")
