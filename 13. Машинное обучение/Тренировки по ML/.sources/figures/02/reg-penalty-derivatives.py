"""One weight under L2 and L1: the pull of the penalty, and the penalised optimum against the unpenalised one."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

LAM = 1.0
fig, axes = fk.subplots(1, 2, size=(9.4, 4.0))

ax = axes[0]
w = np.linspace(-2, 2, 801)
ax.plot(w, 2 * LAM * w, color=fk.CATEGORICAL[0], label="L2: $2\\lambda w$")
ax.plot(w, LAM * np.sign(w), color=fk.CATEGORICAL[1], label="L1: $\\lambda\\,\\mathrm{sign}(w)$")
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.axvline(0, color=fk.TEXT_2, lw=0.8)
ax.annotate("рядом с нулём тянет\nслабо", (0.12, 0.24), xytext=(0.5, -1.3), color=fk.CATEGORICAL[0],
            arrowprops=dict(arrowstyle="->", color=fk.CATEGORICAL[0]), fontsize=8)
ax.annotate("тянет с силой $\\lambda$\nпри любом $w\\ne0$", (0.15, 1.0), xytext=(0.7, 0.2), color=fk.CATEGORICAL[1],
            arrowprops=dict(arrowstyle="->", color=fk.CATEGORICAL[1]), fontsize=8)
ax.set_xlabel("$w$")
ax.set_ylabel("производная штрафа")
ax.set_title("Куда тянет штраф, $\\lambda=1$")
ax.set_ylim(-2.4, 2.4)
ax.grid(True)
ax.legend(loc="upper left")

ax = axes[1]
a = np.linspace(-3, 3, 801)
ridge = a / (1 + LAM)
lasso = np.sign(a) * np.maximum(abs(a) - LAM / 2, 0)
ax.plot(a, a, color=fk.TEXT_2, lw=1, ls="--", label="без штрафа")
ax.plot(a, ridge, color=fk.CATEGORICAL[0], label="L2")
ax.plot(a, lasso, color=fk.CATEGORICAL[1], label="L1")
ax.axvspan(-LAM / 2, LAM / 2, color=fk.tint(fk.CATEGORICAL[1], 0.8), zorder=0)
ax.text(0, -2.0, "мёртвая зона L1:\nвес ровно 0", ha="center", fontsize=8, color=fk.CATEGORICAL[1])
ax.set_xlabel("оптимальный вес без штрафа")
ax.set_ylabel("оптимальный вес со штрафом")
ax.set_title("Сжатие веса, $\\lambda=1$")
ax.grid(True)
ax.legend(loc="upper left")
ax.set_aspect("equal")

fig.tight_layout()
fk.save(fig, OUT / "reg-penalty-derivatives.png")
