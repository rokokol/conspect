"""Toy game f = 3 x1 + x2 x3 at x = (1, 1, 1): the lattice of coalitions with the gains of feature 2 marked.

v(S) = E[f | x_S] with the other features Bernoulli(1/2), independent. The edges of feature 2 carry the gain and the weight
|S|!(n-|S|-1)!/n! of the coalition S they start from; their weighted sum is phi_2.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from shapley_lib import coalitions, interventional_values, shapley_from_values, shapley_weights  # noqa: E402

bg = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)
x = np.array([[1.0, 1.0, 1.0]])
v = interventional_values(lambda Z: 3 * Z[:, 0] + Z[:, 1] * Z[:, 2], x, bg)[:, 0]
phi = shapley_from_values(v[:, None], 3)[:, 0]
w = shapley_weights(3)
masks = coalitions(3)
size = masks.sum(1)

# x position by coalition so that the levels do not cross awkwardly
xpos = {0: 0.0, 1: -2.4, 2: 0.0, 4: 2.4, 3: -2.4, 5: 0.0, 6: 2.4, 7: 0.0}
pos = {k: (xpos[k], size[k]) for k in range(8)}


def label(k):
    return "{" + ",".join(str(i + 1) for i in range(3) if k >> i & 1) + "}" if k else "{}"


fig, ax = fk.subplots(1, 1, size=(8.6, 5.2))
FEATURE = 1  # feature 2 (0-based index 1)
for k in range(8):
    for i in range(3):
        if k >> i & 1:
            continue
        a, b = pos[k], pos[k | 1 << i]
        mine = i == FEATURE
        ax.annotate("", xy=b, xytext=a, zorder=1,
                    arrowprops=dict(arrowstyle="-|>", lw=2.2 if mine else 0.8,
                                    color=fk.MODEL_C if mine else fk.GRIDC, shrinkA=19, shrinkB=19))
        if mine:
            gain = v[k | 1 << i] - v[k]
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ax.text(mx + 0.12, my, f"+{fk.num(gain, 2)}\n×{w[size[k]]:.3f}".replace("×0.333", "×1/3").replace("×0.167", "×1/6"),
                    fontsize=7.5, color=fk.MODEL_C, ha="left", va="center", zorder=4,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
for k in range(8):
    ax.text(*pos[k], f"{label(k)}\nv = {fk.num(v[k], 2)}", ha="center", va="center", fontsize=8.5, zorder=3,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=fk.TEXT, lw=0.9))
ax.set_xlim(-3.9, 4.2)
ax.set_ylim(-0.45, 3.45)
ax.axis("off")
ax.set_title(f"Решётка коалиций; синие рёбра — признак 2: $\\varphi_2={fk.num(phi[1], 3, math=True)}$", fontsize=9)
fk.save(fig, fk.attachments(7) / "shapley-toy-lattice.png")
print("v", v, "phi", phi)
