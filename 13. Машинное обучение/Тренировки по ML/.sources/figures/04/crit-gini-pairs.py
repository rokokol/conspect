"""Gini as a probability: all ordered pairs of draws with replacement from the two parts of the first split X <= 12.

The left part holds 5 red (yellow on the slide) and 8 purple balls, the right part 6 red and 1 purple.
Every cell is one ordered pair (first draw, second draw); with replacement all n^2 pairs are equally likely.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

RED, SIR = fk.CLASS_COLORS[1], fk.CLASS_COLORS[0]
parts = [("левая часть, X ≤ 12", np.array([1] * 5 + [0] * 8)), ("правая часть, X > 12", np.array([1] * 6 + [0] * 1))]

fig, axes = fk.subplots(1, 2, size=(10.8, 5.4), gridspec_kw={"width_ratios": [13, 7]})
for ax, (name, balls) in zip(axes, parts):
    n = len(balls)
    for i in range(n):
        for j in range(n):
            same = balls[i] == balls[j]
            col = fk.tint(RED if balls[i] else SIR, 0.45) if same else "white"
            ax.add_patch(fk.plt.Rectangle((j, n - 1 - i), 1, 1, fc=col, ec=fk.GRIDC, lw=0.6,
                                          hatch=None if same else "///"))
    ax.scatter(np.arange(n) + 0.5, np.full(n, n + 0.45), s=90, c=[RED if v else SIR for v in balls],
               edgecolors="white", linewidths=0.8, clip_on=False)
    ax.scatter(np.full(n, -0.45), n - 1 - np.arange(n) + 0.5, s=90, c=[RED if v else SIR for v in balls],
               edgecolors="white", linewidths=0.8, clip_on=False)
    k1 = int(balls.sum())
    k0 = n - k1
    diff = 2 * k0 * k1
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_anchor("N")
    ax.set_title(f"{name}: {k1} + {k0} = {n} шариков", pad=50)
    ax.set_xlabel(f"штрих — шарики разного цвета: {diff} из {n * n} пар = {fk.num(diff / n**2, 3)}", fontsize=8)
    ax.text(n / 2, n + 1.0, "второй шарик", ha="center", va="bottom", fontsize=8, color=fk.TEXT)
    ax.text(-1.0, n / 2, "первый шарик", ha="right", va="center", rotation=90, fontsize=8, color=fk.TEXT)
    p1 = k1 / n
    print(name, "n", n, "different pairs", diff, "of", n * n, "=", round(diff / n**2, 4),
          "| 1-p0^2-p1^2 =", round(1 - p1**2 - (1 - p1) ** 2, 4), "| 2 p0 p1 =", round(2 * p1 * (1 - p1), 4))
left, right = parts[0][1], parts[1][1]
g = (13 * (80 / 169) + 7 * (12 / 49)) / 20
print("weighted Gini of the split X<=12:", round(g, 4))
fk.save(fig, fk.attachments(4) / "crit-gini-pairs.png")
