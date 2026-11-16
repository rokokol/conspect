"""Entropy of distributions on four outcomes, from uniform to degenerate."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

DISTRIBUTIONS = [
    (0.25, 0.25, 0.25, 0.25),
    (0.4, 0.3, 0.2, 0.1),
    (0.7, 0.1, 0.1, 0.1),
    (0.94, 0.02, 0.02, 0.02),
    (1.0, 0.0, 0.0, 0.0),
]


def entropy_bits(p):
    p = np.asarray(p, dtype=float)
    nz = p[p > 0]
    return float(max(0.0, -(nz * np.log2(nz)).sum()))


fig, axes = fk.subplots(1, len(DISTRIBUTIONS), size=(12.6, 3.0), sharey=True)
for ax, p in zip(axes, DISTRIBUTIONS):
    ax.bar(np.arange(1, 5), p, color=fk.MODEL_C, width=0.7)
    ax.set_xticks(range(1, 5))
    ax.set_ylim(0, 1.05)
    ax.set_title(f"H = {fk.num(entropy_bits(p), 2)} бит")
    ax.set_xlabel("исход")
    ax.grid(True, axis="y")
axes[0].set_ylabel("вероятность")

fig.tight_layout()
fk.save(fig, fk.attachments(4) / "entropy-four-outcomes.png")
