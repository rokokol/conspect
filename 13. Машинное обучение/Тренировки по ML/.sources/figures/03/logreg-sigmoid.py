"""Sigmoid with its derivative, and the chain probability -> odds -> logit that the sigmoid inverts."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

fig, axes = fk.subplots(1, 3, size=(11.4, 3.5))

p = np.linspace(0.005, 0.995, 400)
ax = axes[0]
ax.plot(p, p / (1 - p), color=fk.TEXT, lw=2)
ax.set_ylim(0, 10)
ax.axhline(1, color=fk.GRIDC, lw=1, ls="--")
ax.plot([0.5], [1], "o", color=fk.ACCENT, zorder=4)
ax.annotate(f"p = {fk.num(0.5, 1)}: шансы 1", (0.5, 1), (0.08, 4.5), arrowprops=dict(arrowstyle="->", color=fk.TEXT_2),
            color=fk.TEXT, fontsize=8)
ax.set_xlabel("вероятность $p$")
ax.set_ylabel("шансы $p/(1-p)$")
ax.set_title("p → шансы")
ax.grid(True)

ax = axes[1]
ax.plot(p, np.log(p / (1 - p)), color=fk.TEXT, lw=2)
ax.axhline(0, color=fk.GRIDC, lw=1, ls="--")
ax.plot([0.5], [0], "o", color=fk.ACCENT, zorder=4)
ax.set_ylim(-6, 6)
ax.set_xlabel("вероятность $p$")
ax.set_ylabel("логит $\\ln\\frac{p}{1-p}$")
ax.set_title("шансы → логит")
ax.grid(True)

z = np.linspace(-7, 7, 600)
sig = 1 / (1 + np.exp(-z))
ax = axes[2]
ax.plot(z, (z > 0).astype(float), color=fk.GRIDC, lw=1.5, drawstyle="steps-post", label="порог (ступенька)")
ax.plot(z, sig, color=fk.MODEL_C, lw=2.2, label="$\\sigma(z)$")
ax.plot(z, sig * (1 - sig), color=fk.MODEL2_C, lw=2.2, label="$\\sigma'(z)=\\sigma(1-\\sigma)$")
ax.axhline(0.5, color=fk.GRIDC, lw=0.8, ls=":")
ax.plot([0], [0.5], "o", color=fk.ACCENT, zorder=4)
ax.plot([0], [0.25], "o", color=fk.MODEL2_C, zorder=4)
ax.text(0.45, 0.27, f"максимум {fk.num(0.25, 2)}", color=fk.TEXT, fontsize=8)
ax.set_xlabel("$z=w^\\top x$")
ax.set_title("логит → вероятность")
ax.set_ylim(-0.04, 1.06)
ax.legend(loc="upper left")
ax.grid(True)

fig.tight_layout()
fk.save(fig, fk.attachments(3) / "logreg-sigmoid.png")
