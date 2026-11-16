"""Moore diagram of the 3-state automaton with pairwise distinguishable states but no single experiment for all three."""
import math
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

INK, EDGE = dmfig.INK, dmfig.EDGE

# (input, state) -> (next state, output); the transition table the note and the proof rely on
TRANS = {
    (1, 1): (1, 0), (0, 1): (2, 0),
    (1, 2): (1, 0), (0, 2): (2, 1),
    (1, 3): (3, 1), (0, 3): (2, 0),
}


def run(state, word):
    out = []
    for a in word:
        state, b = TRANS[(a, state)]
        out.append(b)
    return tuple(out)


# the facts the note states, checked against the table drawn below
assert run(1, [0]) != run(2, [0]) and run(1, [1]) != run(3, [1]) and run(2, [0]) != run(3, [0])
for first, tail in product((0, 1), product((0, 1), repeat=6)):
    w = [first, *tail]
    outs = [run(q, w) for q in (1, 2, 3)]
    assert len(set(outs)) < 3
    assert (outs[0] == outs[2]) if first == 0 else (outs[0] == outs[1])

R = 0.42
POS = {1: (0.0, 0.0), 2: (3.4, 0.0), 3: (6.8, 0.0)}
LOOP_DIR = {1: 180, 2: 90, 3: 0}

fig, ax = plt.subplots(figsize=(8.0, 3.8))
NODES = {}
for q, (x, y) in POS.items():
    NODES[q] = Circle((x, y), R, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE,
                      linewidth=1.8, zorder=2)
    ax.add_patch(NODES[q])
    ax.text(x, y, str(q), ha="center", va="center", fontsize=16, color=INK, zorder=3)


def label(a, b):
    return f"{a} ({b})"


moves = {}
for (a, q), (q2, b) in TRANS.items():
    moves.setdefault((q, q2), []).append(label(a, b))

for (u, v), labels in moves.items():
    (x1, y1), (x2, y2) = POS[u], POS[v]
    if u == v:
        th = math.radians(LOOP_DIR[u])
        cx, cy = x1, y1
        pts = []
        for k, ang in enumerate((th - 0.5, th - 0.45, th + 0.45, th + 0.5)):
            rad = R if k in (0, 3) else 3.0 * R
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        ax.add_patch(FancyArrowPatch(path=MPath(pts, [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4]),
                                     arrowstyle="-|>", mutation_scale=16, color=EDGE, linewidth=2, zorder=1))
        d = 3.0 * R + 0.28
        ax.text(cx + d * math.cos(th), cy + d * math.sin(th), "\n".join(labels), ha="center",
                va="center", fontsize=13, color=INK)
    else:
        rad = 0.35 if (v, u) in moves else 0.0
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                                     patchA=NODES[u], patchB=NODES[v], shrinkA=0, shrinkB=0,
                                     connectionstyle=f"arc3,rad={rad}", color=EDGE, linewidth=2, zorder=1))
        dx, dy = x2 - x1, y2 - y1
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = dy, -dx
        norm = math.hypot(nx, ny)
        if rad == 0:
            lx, ly = mx, my + 0.3
        else:
            lx = mx + 0.5 * rad * nx + (nx / norm) * 0.3
            ly = my + 0.5 * rad * ny + (ny / norm) * 0.3
        ax.text(lx, ly, "\n".join(labels), ha="center", va="center", fontsize=13, color=INK)

ax.text(3.4, -2.1, "пометка на дуге: вход (выход)", ha="center", va="center", fontsize=12, color=INK)
ax.set_xlim(-2.4, 9.2)
ax.set_ylim(-2.6, 2.4)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "moore-3state")
