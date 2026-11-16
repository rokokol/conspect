"""The code graph G_phi of the lecturer's code a->0, b->01, c->10 (lecture 13); the cycle through the empty word is red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codefig  # noqa: E402
import codegraph  # noqa: E402
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

code = ["0", "01", "10"]
V, arcs = codegraph.build_graph(code)
cycle = codegraph.cycle_through_lambda(V, arcs)
assert V == ["", "0", "1"] and cycle == ["", "1", ""]

names = {"": r"$\Lambda$", "0": "0", "1": "1"}
pos = {"": (0.0, 0.0), "1": (3.0, 1.9), "0": (6.0, 0.0)}
on_cycle = set(zip(cycle, cycle[1:]))
bent = {("", "1"): -0.22, ("1", ""): -0.22, ("0", "1"): -0.22, ("1", "0"): -0.22}
colours = {a: (dmfig.HIGHLIGHT if a in on_cycle else dmfig.EDGE) for a in arcs}

fig, ax = plt.subplots(figsize=(7.2, 4.2))
codefig.draw_digraph(ax, pos, list(arcs), names, bent=bent, arc_colours=colours, radius=0.3)
# the codeword B_l = beta_i D beta_j that gives each arc, set just outside the bent arc
labels = {("", "1"): r"01 = $\Lambda$·0·1", ("1", ""): r"10 = 1·0·$\Lambda$",
          ("0", "1"): r"01 = 0·$\Lambda$·1", ("1", "0"): r"10 = 1·$\Lambda$·0"}
for arc, label in labels.items():
    (x1, y1), (x2, y2) = pos[arc[0]], pos[arc[1]]
    dx, dy = x2 - x1, y2 - y1
    rad = bent[arc]
    mx, my = (x1 + x2) / 2 + 0.5 * rad * dy, (y1 + y2) / 2 - 0.5 * rad * dx
    norm = (dx * dx + dy * dy) ** 0.5
    ox, oy = rad * dy / abs(rad) / norm, -rad * dx / abs(rad) / norm
    ax.text(mx + 0.5 * ox, my + 0.5 * oy, label, ha="center", va="center", fontsize=12, color=colours[arc])
ax.text(3.0, -0.85, r"подпись у дуги $\beta_i\to\beta_j$ — кодовое слово $B_l=\beta_i D\beta_j$, красные дуги — цикл через $\Lambda$",
        ha="center", fontsize=9.5, color=dmfig.INK)
ax.set_xlim(-0.8, 6.8)
ax.set_ylim(-1.2, 2.6)
dmfig.save(fig, codefig.TOPIC, "code-graph")
