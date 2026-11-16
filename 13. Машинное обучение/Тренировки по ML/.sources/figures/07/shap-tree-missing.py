"""A feature that is missing in a tree: the walk goes both ways and the answers are averaged by the training counts (slide 27).

Hand-made tree on 10 training objects. Root x1 <= t: left 6 objects, right 4 (leaf C, value 6). The left child splits on x2 <= u:
leaf A (4 objects, value 1) and leaf B (2 objects, value 4). Object x: x1 <= t, x2 > u, so it lands in B and f(x) = 4.
"""
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

POS = {"root": (0.5, 0.92), "L": (0.27, 0.52), "C": (0.73, 0.52), "A": (0.12, 0.12), "B": (0.42, 0.12)}
LABEL = {"root": "$x_1\\leqslant t$\n10", "L": "$x_2\\leqslant u$\n6", "C": "C: 6\n4 объекта",
         "A": "A: 1\n4 объекта", "B": "B: 4\n2 объекта"}
EDGES = [("root", "L", "да"), ("root", "C", "нет"), ("L", "A", "да"), ("L", "B", "нет")]
N = {"L": 6, "C": 4, "A": 4, "B": 2}
VAL = {"A": 1, "B": 4, "C": 6}


def weights(S):
    """Fraction of the walk that goes through each edge when the features in S are known (x: x1 <= t, x2 > u)."""
    w = {}
    # root splits on feature 1
    if 1 in S:
        w[("root", "L")], w[("root", "C")] = F(1), F(0)
    else:
        w[("root", "L")], w[("root", "C")] = F(6, 10), F(4, 10)
    # left child splits on feature 2, x goes to B
    if 2 in S:
        w[("L", "A")], w[("L", "B")] = F(0), F(1)
    else:
        w[("L", "A")], w[("L", "B")] = F(4, 6), F(2, 6)
    return w


def value(S):
    w = weights(S)
    return (w[("root", "L")] * (w[("L", "A")] * VAL["A"] + w[("L", "B")] * VAL["B"])
            + w[("root", "C")] * VAL["C"])


cases = [(set(), "ничего не известно"), ({1}, "известен $x_1$"), ({2}, "известен $x_2$"), ({1, 2}, "известны оба")]
fig, axes = fk.subplots(1, 4, size=(12.4, 3.5))
for ax, (S, title) in zip(axes, cases):
    w = weights(S)
    for a, b, lab in EDGES:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        ax.plot([x0, x1], [y0, y1], color=fk.MODEL_C if w[(a, b)] > 0 else fk.GRIDC, lw=0.8 + 4.5 * float(w[(a, b)]),
                ls="-" if w[(a, b)] > 0 else ":", zorder=1, solid_capstyle="round")
        if w[(a, b)] > 0:
            ax.text((x0 + x1) / 2 + (0.035 if b in ("C", "B") else -0.035), (y0 + y1) / 2, str(w[(a, b)]),
                    fontsize=8, ha="left" if b in ("C", "B") else "right", va="center", color=fk.TEXT,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"), zorder=3)
    for name, (px, py) in POS.items():
        ax.text(px, py, LABEL[name], ha="center", va="center", fontsize=7.5, zorder=4,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=fk.TEXT if name == "B" else fk.TEXT_2,
                          lw=1.6 if name == "B" else 0.8))
    ax.set_title(f"{title}\n$v={fk.num(float(value(S)), None, math=True)}$", fontsize=9)
    ax.set_xlim(0, 0.86)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "shap-tree-missing.png")
for S, _ in cases:
    print(sorted(S), value(S))
