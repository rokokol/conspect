"""K4 as a plane graph with four distinct colours (lecture 12)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

C = dmfig.COLOURS

# the plane realisation: vertex 4 inside the triangle 1-2-3; every pair of vertices is adjacent
k4 = {1: (0, 0), 2: (3.0, 0), 3: (1.5, 2.6), 4: (1.5, 0.95)}
k4_edges = [(1, 2), (2, 3), (3, 1), (1, 4), (2, 4), (3, 4)]
assert len(set(k4_edges)) == 6

fig, ax = plt.subplots(figsize=(4.8, 4.2))
dmfig.draw_graph(ax, k4, k4_edges, labels={v: f"$c_{v}$" for v in k4}, fills={v: C[v - 1] for v in k4},
                 node_size=0.2, label_size=13)
ax.set_title("$K_4$: четыре вершины — четыре разных цвета", color=dmfig.INK, fontsize=11)
dmfig.save(fig, 4, "k4-colours")
