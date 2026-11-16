"""Ridge on the collinear demo of lecture 2: weights as a function of lambda, and the path in the (w2, w3) plane."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from collinear_demo import W_TRUE, ols, ridge, sample  # noqa: E402

X, y = sample(fk.SEED, 4e-5)
w_ols = ols(X, y)
lams = np.logspace(-10, 4, 280)
W = np.array([ridge(X, y, l) for l in lams])

fig, axes = fk.subplots(1, 2, size=(9.8, 3.9))

ax = axes[0]
for k, color in enumerate(fk.CATEGORICAL):
    ax.plot(lams, W[:, k], color=color, label=f"$w_{k + 1}$")
    ax.scatter([lams[0] / 2.5], [w_ols[k]], color=color, s=22, zorder=4)
ax.set_xscale("log")
ax.set_xlabel("$\\lambda$")
ax.set_ylabel("вес")
ax.set_title("Веса гребневой регрессии")
ax.grid(True, axis="y")
ax.legend(loc="center right")
ax.text(lams[0], 55, "точки слева —\nМНК", color=fk.TEXT_2, fontsize=8)

ax = axes[1]
ax.plot(W[:, 1], W[:, 2], color=fk.TEXT_2, lw=1.4)
for d in (-9, -7, -6):
    i = int(np.argmin(abs(np.log10(lams) - d)))
    ax.scatter(W[i, 1], W[i, 2], color=fk.BLUE, s=34, zorder=4, edgecolor="white")
    ax.annotate(f"$10^{{{d}}}$", (W[i, 1], W[i, 2]), xytext=(7, 4), textcoords="offset points",
                fontsize=8, color=fk.TEXT)
i = int(np.argmin(abs(np.log10(lams) + 2)))
ax.axhline(0, color=fk.GRIDC, lw=1)
ax.axvline(0, color=fk.GRIDC, lw=1)

# Zoom on the end of the path: ridge splits the weight evenly, the truth splits it unevenly
ins = ax.inset_axes([0.6, 0.6, 0.37, 0.33])
ins.plot(W[:, 1], W[:, 2], color=fk.TEXT_2, lw=1.4)
ins.plot([-1.4, 0.2], [-1.4, 0.2], color=fk.GRIDC, lw=1, ls="--")
ins.scatter(W[i, 1], W[i, 2], color=fk.ACCENT, s=40, zorder=5, edgecolor="white")
ins.scatter([W_TRUE[1]], [W_TRUE[2]], color=fk.RED, s=40, zorder=5, edgecolor="white")
ins.annotate("истина", (W_TRUE[1], W_TRUE[2]), xytext=(4, -14), textcoords="offset points", color=fk.RED, fontsize=7)
ins.annotate("$\\lambda=10^{-2}$", (W[i, 1], W[i, 2]), xytext=(-52, 6), textcoords="offset points",
             color=fk.ACCENT, fontsize=7)
ins.set_xlim(-1.4, 0.2)
ins.set_ylim(-1.4, 0.2)
ins.set_title("увеличено; пунктир $w_2=w_3$", fontsize=7)
ins.tick_params(labelsize=6)
ins.grid(True)
ax.set_xlabel("$w_2$")
ax.set_ylabel("$w_3$")
ax.set_title("Путь $(w_2, w_3)$ при росте $\\lambda$")
ax.grid(True)

fig.tight_layout()
fk.save(fig, fk.attachments(2) / "reg-ridge-collinear-path.png")
