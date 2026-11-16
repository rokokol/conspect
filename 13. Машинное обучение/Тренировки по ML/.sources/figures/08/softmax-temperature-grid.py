"""The same ten logits at six temperatures: the distribution flattens as T grows and collapses to one bar as T falls."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import softmax_common as S  # noqa: E402
from softmax_common import fk  # noqa: E402

TEMPS = [0.1, 0.5, 1, 2, 5, 20]
fig, axes = fk.subplots(2, 3, size=(12.6, 6.6), sharey=True)
x = np.arange(len(S.NAMES))
colors = [fk.MODEL_C] * 5 + [fk.MODEL2_C] * 5
for ax, T in zip(axes.ravel(), TEMPS):
    q = S.softmax(S.Z, T)
    ax.bar(x, q, color=colors)
    ax.set_title(f"$T={fk.num(T, None, math=True)}$, $H={fk.num(S.entropy(q), 2, math=True)}$", fontsize=10)
    ax.set_xticks(x, S.NAMES, rotation=70, ha="right", fontsize=7)
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y")
for ax in axes[:, 0]:
    ax.set_ylabel("вероятность $q_i$")
axes[0, 0].legend(handles=[Patch(color=fk.MODEL_C, label="машины"), Patch(color=fk.MODEL2_C, label="грибы")],
                  fontsize=8, loc="upper left")
fig.tight_layout()
fk.save(fig, fk.attachments(8) / "softmax-temperature-grid.png")

for T in TEMPS:
    q = S.softmax(S.Z, T)
    print(f"T={T:g} H={S.entropy(q):.3f} max={q.max():.3f} mushrooms total={q[5:].sum():.4f}")
print("ln N =", round(float(np.log(10)), 3))
