"""Propagation constant β against the wave number k for the families m = 0..4, ε_i = 2.3839, ε_e = 2.2124."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import круглый_расчёт as cc  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

s = np.sqrt(cc.DELTA)
k_light = np.linspace(0, 10 / s, 100)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)

for m in range(5):
    V, lam = cc.branch(m, n_left=400, n_right=400)
    k, b = V / s, cc.beta(V, lam)
    color = mffig.CYCLE[m]
    ax1.plot(k, b.real, "-", color=color, linewidth=2)
    ax1.plot(k, np.abs(b.imag), "--", color=color, linewidth=1.6)
    kc = cc.cutoff(m) / s
    ax1.plot([kc], [kc * np.sqrt(cc.EPS_E)], "o", color=mffig.HIGHLIGHT, markeredgecolor=mffig.INK, markersize=6, zorder=5)
    guided = k >= kc
    ax2.plot(k[guided], (b.real / k)[guided], "-", color=color, linewidth=2, label=f"$m={m}$")
    ax2.plot([kc], [np.sqrt(cc.EPS_E)], "o", color=mffig.HIGHLIGHT, markeredgecolor=mffig.INK, markersize=6, zorder=5)

ax1.plot(k_light, k_light * np.sqrt(cc.EPS_I), "-.", color=mffig.INK, linewidth=1.2)
ax1.plot(k_light, k_light * np.sqrt(cc.EPS_E), ":", color=mffig.INK, linewidth=1.4)
for y, name in ((np.sqrt(cc.EPS_I), r"$\sqrt{\varepsilon_i}$"), (np.sqrt(cc.EPS_E), r"$\sqrt{\varepsilon_e}$")):
    ax2.axhline(y, color=mffig.INK, linestyle="-." if y > 1.5 else ":", linewidth=1.2)
    ax2.text(24, y, name, ha="right", va="bottom" if y > 1.5 else "top", color=mffig.INK)

ax1.set_xlabel("$k$")
ax1.set_ylabel(r"$\beta$", rotation=0, labelpad=10)
ax1.set_title("Весь диапазон")
ax1.set_xlim(0, 10 / s)
ax1.set_ylim(0, 40)
ax1.grid(True, color=mffig.AUX, linewidth=0.6)
handles = [
    Line2D([], [], color=mffig.INK, linewidth=2, label=r"$\mathrm{Re}\,\beta$"),
    Line2D([], [], color=mffig.INK, linewidth=1.6, linestyle="--", label=r"$|\mathrm{Im}\,\beta|$"),
    Line2D([], [], color=mffig.INK, linewidth=1.2, linestyle="-.", label=r"$\beta=k\sqrt{\varepsilon_i}$"),
    Line2D([], [], color=mffig.INK, linewidth=1.4, linestyle=":", label=r"$\beta=k\sqrt{\varepsilon_e}$"),
    Line2D([], [], color="none", marker="o", markerfacecolor=mffig.HIGHLIGHT, markeredgecolor=mffig.INK, markersize=6, label="точка отсечки"),
]
ax1.legend(handles=handles, loc="upper left", frameon=False)

ax2.set_xlabel("$k$")
ax2.set_ylabel(r"$\beta/k$", rotation=0, labelpad=14)
ax2.set_title("Направляемые моды")
ax2.set_xlim(0, 10 / s)
ax2.set_ylim(1.48, 1.55)
ax2.grid(True, color=mffig.AUX, linewidth=0.6)
ax2.legend(loc="upper left", bbox_to_anchor=(0.02, 0.9), frameon=False, ncol=2)
mffig.save(fig, 6, "круглый-постоянная-распространения")
