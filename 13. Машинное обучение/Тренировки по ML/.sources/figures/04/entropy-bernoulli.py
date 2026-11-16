"""Surprise -log p and the Bernoulli entropy H(p) in bits and nats."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

fig, axes = fk.subplots(1, 2, size=(10.4, 3.6))

p = np.linspace(0.002, 0.998, 600)

ax = axes[0]
ax.plot(p, -np.log2(p), color=fk.MODEL_C, lw=2.2)
for q in (0.5, 0.1):
    ax.plot([q], [-np.log2(q)], "o", color=fk.ACCENT, zorder=4)
ax.annotate(f"p = {fk.num(0.5, 1)}: 1 бит", (0.5, 1), (0.6, 2.2), arrowprops=dict(arrowstyle="->", color=fk.TEXT_2),
            color=fk.TEXT, fontsize=8)
ax.annotate(f"p = {fk.num(0.1, 1)}: {fk.num(3.32, 2)} бита", (0.1, -np.log2(0.1)), (0.3, 4.4),
            arrowprops=dict(arrowstyle="->", color=fk.TEXT_2), color=fk.TEXT, fontsize=8)
ax.set_ylim(0, 7)
ax.set_xlabel("вероятность исхода $p$")
ax.set_ylabel("$-\\log_2 p$")
ax.set_title("неожиданность исхода")
ax.grid(True)

pe = np.linspace(1e-9, 1 - 1e-9, 2000)
h2 = -pe * np.log2(pe) - (1 - pe) * np.log2(1 - pe)
ax = axes[1]
ax.plot(pe, h2, color=fk.MODEL_C, lw=2.2, label="в битах, $\\log_2$")
ax.plot(pe, h2 * np.log(2), color=fk.MODEL2_C, lw=2.2, label="в натах, $\\ln$")
ax.plot([0.5], [1], "o", color=fk.ACCENT, zorder=4)
ax.plot([0.5], [np.log(2)], "o", color=fk.ACCENT, zorder=4)
ax.text(0.54, 1.0, "максимум 1 бит", color=fk.TEXT, fontsize=8, va="center")
ax.text(0.54, np.log(2) - 0.06, f"$\\ln 2\\approx{fk.num(0.693, 3, math=True)}$ нат", color=fk.TEXT, fontsize=8, va="top")
ax.set_ylim(0, 1.15)
ax.set_xlabel("параметр Бернулли $p$")
ax.set_ylabel("$H(p)$")
ax.set_title("энтропия монетки")
ax.legend(loc="lower center")
ax.grid(True)

fig.tight_layout()
fk.save(fig, fk.attachments(4) / "entropy-bernoulli.png")
