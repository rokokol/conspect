"""An ordered rooted tree, its depth-first walk and the 0/1 code of the walk (lecture 11, the 4^q estimate)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

pos = {"r": (2.0, 2.5), "a": (0.65, 1.25), "b": (3.5, 1.25), "c": (-0.6, 0.0), "d": (1.9, 0.0), "e": (3.5, 0.0)}
# children in the order of the subtrees
children = {"r": ["a", "b"], "a": ["c", "d"], "b": ["e"], "c": [], "d": [], "e": []}

steps = []  # (parent, child, direction)


def walk(v):
    for c in children[v]:
        steps.append((v, c, 0))
        walk(c)
        steps.append((v, c, 1))


walk("r")
code = "".join(str(s[2]) for s in steps)
q = sum(len(c) for c in children.values())
assert len(code) == 2 * q and code == "0010110011"

edges = [(v, c) for v in children for c in children[v]]
fig, ax = plt.subplots(figsize=(6.6, 4.6))
dmfig.draw_graph(ax, pos, edges, node_size=0.2, label_size=14)
for k, (v, c, d) in enumerate(steps, 1):
    (x1, y1), (x2, y2) = pos[v], pos[c]
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    n = (dy ** 2 + dx ** 2) ** 0.5
    nx, ny = -dy / n, dx / n  # the normal; the way down is drawn on its negative side
    side = 1 if d else -1
    off = 0.45 if abs(nx) > 0.95 else 0.3  # a vertical edge: labels need more room beside it
    ax.text(mx + side * off * nx, my + side * off * ny, f"{k}: {d}", ha="center", va="center", fontsize=11,
            color=dmfig.HIGHLIGHT if d == 0 else dmfig.INK)
ax.text(1.45, -0.75, f"код дерева: {code}", ha="center", fontsize=13, color=dmfig.INK)
ax.text(1.45, -1.2, "шаг $k$: $0$ — по ребру от корня (красный), $1$ — к корню; поддеревья идут слева направо",
        ha="center", fontsize=9.5, color=dmfig.INK)
ax.set_xlim(-1.4, 4.3)
ax.set_ylim(-1.5, 3.0)
dmfig.save(fig, 4, "rooted-tree-code")
