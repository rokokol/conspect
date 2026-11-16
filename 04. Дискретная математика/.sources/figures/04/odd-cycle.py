"""An odd cycle does not fit into two colours (lecture 13)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

C = dmfig.COLOURS

n = 5
pos = {i: (math.cos(math.pi / 2 - 2 * math.pi * i / n), math.sin(math.pi / 2 - 2 * math.pi * i / n))
       for i in range(n)}
edges = [(i, (i + 1) % n) for i in range(n)]
fills = {0: C[0], 1: C[1], 2: C[0], 3: C[1], 4: dmfig.P["paper"]}
labels = {0: "$v_1$", 1: "$v_2$", 2: "$v_3$", 3: "$v_4$", 4: "$v_5$"}

fig, ax = plt.subplots(figsize=(5.0, 4.6))
dmfig.draw_graph(ax, pos, edges, labels=labels, fills=fills, node_size=0.14, label_size=12,
                 edge_colors={(3, 4): dmfig.HIGHLIGHT, (4, 0): dmfig.HIGHLIGHT})
ax.set_title("цикл длины $5=2\\cdot2+1$: пятой вершине\nне хватает цвета", color=dmfig.INK, fontsize=11)
fig.text(0.5, 0.0, "$v_4$ имеет цвет $c_2$, $v_1$ имеет цвет $c_1$: оба цвета заняты",
         ha="center", fontsize=9.5, color=dmfig.INK)
dmfig.save(fig, 4, "odd-cycle")
