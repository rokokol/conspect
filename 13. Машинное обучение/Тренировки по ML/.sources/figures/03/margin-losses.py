"""Surrogate losses of the margin against the step loss; the natural-log logistic loss and the true Savage loss do not dominate the step at M = 0."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# The grid holds M = 0 exactly, the point where the step and the surrogates touch.
m = np.union1d(np.linspace(-3, 3, 1200), [0.0])
step = (m <= 0).astype(float)
losses = {
    "квадратичная $(1-M)^2$": ((1 - m) ** 2, fk.P["rule"]),
    "hinge $\\max(0,1-M)$": (np.maximum(0, 1 - m), fk.P["monika-eye"]),
    "логистическая $\\log_2(1+e^{-M})$": (np.log2(1 + np.exp(-m)), fk.RED),
    "экспоненциальная $e^{-M}$": (np.exp(-m), fk.P["sayori"]),
    "сигмоидная $2/(1+e^{M})$ (на слайде savage)": (2 / (1 + np.exp(m)), fk.P["sayori-eye"]),
}

fig, (ax, zx) = fk.plt.subplots(1, 2, figsize=(10.6, 4.0), gridspec_kw=dict(width_ratios=[1.45, 1]))
ax.plot(m, step, color=fk.TEXT, lw=2.4, label="ступенька $[M\\leqslant0]$")
for name, (v, c) in losses.items():
    ax.plot(m, v, color=c, lw=1.8, label=name)
    assert (v >= step - 1e-12).all(), name
ax.axvline(0, color=fk.TEXT_2, lw=0.8, ls="--")
ax.set_ylim(-0.1, 4.6)
ax.set_xlim(-3, 3)
ax.set_xlabel("отступ $M$")
ax.set_ylabel("потеря на объекте")
ax.set_title("Верхние оценки ступеньки")
ax.grid(True, axis="y")
ax.legend(loc="upper right", fontsize=7, frameon=True, framealpha=0.95)

# Zoom at M = 0: log2 passes through (0, 1); ln and the true Savage loss stay below the step there.
z = np.union1d(np.linspace(-0.8, 0.6, 400), [0.0])
zx.plot(z, (z <= 0).astype(float), color=fk.TEXT, lw=2.4, label="ступенька")
zx.plot(z, np.log2(1 + np.exp(-z)), color=fk.RED, lw=1.8, label="$\\log_2(1+e^{-M})$")
zx.plot(z, np.log(1 + np.exp(-z)), color=fk.RED, lw=1.8, ls="--", label="$\\ln(1+e^{-M})$")
zx.plot(z, 1 / (1 + np.exp(z)) ** 2, color=fk.P["yuri"], lw=1.8, ls=":", label="Savage $1/(1+e^{M})^2$")
zx.scatter([0, 0, 0], [1, np.log(2), 0.25], color=fk.TEXT, s=18, zorder=4)
zx.annotate(f"$\\ln2\\approx{fk.num(np.log(2), 2, math=True)}$", xy=(0, np.log(2)), xytext=(-0.78, 0.66), fontsize=8, color=fk.TEXT,
            arrowprops=dict(arrowstyle="->", color=fk.TEXT_2, lw=1))
zx.annotate("$1/4$", xy=(0, 0.25), xytext=(0.12, 0.12), fontsize=8, color=fk.TEXT,
            arrowprops=dict(arrowstyle="->", color=fk.TEXT_2, lw=1))
zx.axvline(0, color=fk.TEXT_2, lw=0.8, ls="--")
zx.set_ylim(0, 1.6)
zx.set_xlabel("отступ $M$")
zx.set_title("Окрестность $M=0$")
zx.grid(True, axis="y")
zx.legend(loc="upper right", fontsize=7, frameon=True, framealpha=0.95)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "margin-losses.png")
at0 = {k: float(v[0][np.searchsorted(m, 0.0)]) for k, v in losses.items()}
print("at M=0:", {k: round(x, 4) for k, x in at0.items()})
print("ln(1+e^0) =", round(float(np.log(2)), 4), " Savage 1/(1+e^0)^2 =", 0.25,
      " ln-loss below 1 on M >", round(float(-np.log(np.e - 1)), 4))
