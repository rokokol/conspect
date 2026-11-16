"""Accuracy as a per-object step loss against a smooth surrogate (logistic loss in base 2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)

M = np.linspace(-4, 4, 800)
fig, ax = fk.plt.subplots(figsize=(5.8, 3.6))
ax.plot(M, (M < 0).astype(float), color=fk.TEXT, lw=2, label="ошибка классификации (ступенька)")
ax.plot(M, np.log2(1 + np.exp(-M)), color=fk.RED, lw=2, label="логистическая потеря $\\log_2(1+e^{-M})$")
ax.axvline(0, color=fk.TEXT_2, lw=0.8, ls="--")
ax.annotate("производная нулевая везде,\nкроме скачка при $M=0$", xy=(1.9, 0.0), xytext=(0.6, 1.9),
            fontsize=8, color=fk.TEXT_2, arrowprops=dict(arrowstyle="->", color=fk.TEXT_2, lw=1))
ax.set_ylim(-0.1, 3.6)
ax.set_xlabel("отступ $M$: верность и уверенность ответа")
ax.set_ylabel("потеря на объекте")
ax.set_title("Ступенька и её гладкий суррогат")
ax.set_axisbelow(True)
ax.grid(True, axis="y")
ax.legend(loc="upper right")

fig.tight_layout()
fk.save(fig, OUT / "step-vs-logistic-loss.png")
