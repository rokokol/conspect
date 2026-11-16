"""Binary cross-entropy H(p, q) as a function of q for fixed p: the minimum sits at q = p and equals H(p)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

fig, ax = fk.subplots(1, 1, size=(6.4, 4.2))

q = np.linspace(0.004, 0.996, 800)
for p, color in zip((0.1, 0.3, 0.5), fk.CATEGORICAL):
    ce = -p * np.log2(q) - (1 - p) * np.log2(1 - q)
    h = -p * np.log2(p) - (1 - p) * np.log2(1 - p)
    ax.plot(q, ce, color=color, lw=2.2, label=f"$p={fk.num(p, None, math=True)}$, $H(p)={fk.num(h, 2, math=True)}$")
    ax.plot([p], [h], "o", color=color, ms=7, zorder=4, mec=fk.ACCENT)
    ax.plot([p, p], [0, h], color=color, lw=1, ls=":")
ax.set_ylim(0, 4.5)
ax.set_xlim(0, 1)
ax.set_xlabel("предсказание $q$")
ax.set_ylabel("$H(p,q)$, бит")
ax.set_title("кросс-энтропия при фиксированном $p$")
ax.legend(loc="upper center")
ax.grid(True)

fig.tight_layout()
fk.save(fig, fk.attachments(4) / "entropy-cross-curve.png")
