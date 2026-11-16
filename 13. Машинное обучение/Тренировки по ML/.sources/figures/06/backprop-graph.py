"""Computational graph of slide 29 with forward values (green) and gradients (red), plus a GIF of both passes.

Values come from backprop_common, which backprop-check.py verifies against
finite differences; nothing here is typed in by hand except the layout.
"""
import sys
from pathlib import Path

from matplotlib.patches import Circle, FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import backprop_common as bc  # noqa: E402

FWD, BWD = fk.P["ribbon"], fk.P["bow"]
NODE_FILL = fk.tint(fk.P["sayori"], 0.45)

v = dict(bc.SLIDE29)
n = bc.graph_forward(v)
g = bc.graph_backward(v, n)
val = {**v, **n}

LEAVES = {"x0": (0, 4.2), "w0": (0, 3.2), "x1": (0, 2.0), "w1": (0, 1.0), "w2": (0, -0.1)}
NODES = {"m0": (1.7, 3.7, "×"), "m1": (1.7, 1.5, "×"), "s0": (3.2, 2.6, "+"), "s": (4.6, 1.5, "+"),
         "neg": (6.0, 1.5, "·(−1)"), "e": (7.4, 1.5, "exp"), "q": (8.8, 1.5, "+1"), "out": (10.2, 1.5, "1/x")}
END = (11.5, 1.5)
# (source, target, forward step, backward step); the value on an edge is the source's.
EDGES = [("x0", "m0", 1, 8), ("w0", "m0", 1, 8), ("x1", "m1", 1, 8), ("w1", "m1", 1, 8),
         ("m0", "s0", 2, 7), ("m1", "s0", 2, 7), ("s0", "s", 3, 6), ("w2", "s", 1, 6),
         ("s", "neg", 4, 5), ("neg", "e", 5, 4), ("e", "q", 6, 3), ("q", "out", 7, 2), ("out", None, 8, 1)]
LEAF_TEX = {"x0": "$x_0$", "w0": "$w_0$", "x1": "$x_1$", "w1": "$w_1$", "w2": "$w_2$"}
N_FWD = 8


def pos(k):
    if k is None:
        return END
    if k in LEAVES:
        return LEAVES[k]
    return NODES[k][:2]


def draw(ax, stage):
    """stage 0..N_FWD shows forward steps, N_FWD+1..2*N_FWD shows backward steps on top."""
    for k, (x, y, op) in NODES.items():
        ax.add_patch(Circle((x, y), 0.36, facecolor=NODE_FILL, edgecolor=fk.TEXT, lw=1, zorder=3))
        ax.text(x, y, op, ha="center", va="center", fontsize=13 if len(op) < 3 else 9, zorder=4)
    for k, (x, y) in LEAVES.items():
        ax.text(x - 1.0, y, LEAF_TEX[k], ha="right", va="center", fontsize=13)
    for src, dst, f_step, b_step in EDGES:
        (x0, y0), (x1, y1) = pos(src), pos(dst)
        r0 = 0.0 if src in LEAVES else 0.38
        r1 = 0.0 if dst is None else 0.40
        if dst is None:
            x0 += r0
        else:
            dx, dy = x1 - x0, y1 - y0
            d = (dx * dx + dy * dy) ** 0.5
            x0, y0 = x0 + dx / d * r0, y0 + dy / d * r0
            x1, y1 = x1 - dx / d * r1, y1 - dy / d * r1
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10,
                                     color=fk.TEXT_2, lw=1, zorder=2))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if src in LEAVES:
            # Leaf values sit beside the leaf: on the edge, neighbours' labels would collide.
            mx, my = x0 - 0.5, y0
        if stage >= f_step:
            ax.text(mx, my + 0.13, f"{fk.num(val[src], 2)}", color=FWD, ha="center", va="bottom", fontsize=9)
        if stage > N_FWD and stage - N_FWD >= b_step:
            ax.text(mx, my - 0.13, f"{fk.num(g[src], 2)}", color=BWD, ha="center", va="top", fontsize=9)
    ax.set_xlim(-1.7, 12.0)
    ax.set_ylim(-0.6, 4.7)
    ax.set_aspect("equal")
    ax.axis("off")
    # fk.gif saves the whole canvas, not a tight box: let the axes fill it.
    ax.figure.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.92)
    if stage <= N_FWD:
        ax.set_title("прямой проход" if stage else "граф вычислений", color=FWD if stage else fk.TEXT)
    else:
        ax.set_title("обратный проход", color=BWD)


OUT = fk.attachments(6)
fig, ax = fk.subplots(1, 1, size=(11.5, 4.6))
draw(ax, 2 * N_FWD)
ax.set_title("$\\sigma(x_0w_0+x_1w_1+w_2)$: значения и градиенты")
fk.save(fig, OUT / "backprop-graph.png")
fk.gif(draw, 2 * N_FWD + 1, OUT / "backprop-graph.gif", size=(9.6, 4.6), fps=1.5, dpi=110, hold_last=3)
