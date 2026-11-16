"""Coin, 90 heads and 10 tails: likelihood of the parameter p and its logarithm share one maximum."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import figkit as fk  # noqa: E402

HEADS, TAILS = 90, 10
# Dense near 1, so the log curve visibly falls to minus infinity there.
p = np.concatenate([np.linspace(0.001, 0.999, 999), 1 - np.logspace(-3.05, -12, 80)])
L = p**HEADS * (1 - p) ** TAILS
logL = HEADS * np.log(p) + TAILS * np.log(1 - p)
phat = HEADS / (HEADS + TAILS)

fig, axes = fk.subplots(1, 2, size=(10.4, 3.5))
for ax, f, name in [(axes[0], L, "Правдоподобие"), (axes[1], logL, "Логарифм правдоподобия")]:
    ax.plot(p, f, color=fk.BLUE)
    for q in (0.5, 0.92):
        v = q**HEADS * (1 - q) ** TAILS if f is L else HEADS * np.log(q) + TAILS * np.log(1 - q)
        ax.plot([q], [v], "o", color=fk.TEST_C, zorder=4)
        ax.annotate(f"p = {fk.num(q, None)}", (q, v), textcoords="offset points",
                    xytext=(-20, 14) if q == 0.5 else (10, -16), fontsize=9, color=fk.TEXT)
    ax.axvline(phat, color=fk.TEXT_2, lw=1, ls="--")
    ax.set_title(name)
    ax.set_xlabel("p")
    ax.grid(True, axis="y")
axes[1].set_ylim(-120, -25)
axes[1].set_xlim(-0.05, 1.22)
axes[1].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
axes[0].text(0.45, 6.5e-15, f"максимум в p = {fk.num(phat, None)}", ha="left", fontsize=9, color=fk.TEXT_2)
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "nb-coin-likelihood.png")
print(0.5 ** 100, 0.92**90 * 0.08**10, 0.9**90 * 0.1**10)
