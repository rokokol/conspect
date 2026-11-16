"""Circuit that computes f(x1,...,xn) from the two subfunctions f(0,x2,...,xn) and f(1,x2,...,xn)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon  # noqa: E402

INK, EDGE = dmfig.INK, dmfig.EDGE
BOX = dmfig.tint(dmfig.P["natsuki"], 0.6)
GATE = dmfig.tint(dmfig.P["sayori-eye"], 0.5)

fig, ax = plt.subplots(figsize=(6.2, 5.2))


def wire(*pts):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=EDGE, linewidth=2, zorder=1, solid_joinstyle="round")


def gate(x, y, label):
    ax.add_patch(Polygon([(x - 0.4, y + 0.3), (x + 0.4, y + 0.3), (x, y - 0.3)], closed=True,
                         facecolor=GATE, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
    ax.text(x, y + 0.08, label, ha="center", va="center", fontsize=24 if "cdot" in label else 14,
            color=INK, zorder=3)


def box(x, y, label):
    ax.add_patch(FancyBboxPatch((x - 1.1, y - 0.4), 2.2, 0.8, boxstyle="round,pad=0.02",
                                facecolor=BOX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
    ax.text(x, y, label, ha="center", va="center", fontsize=11, color=INK, zorder=3)


# inputs
for x, label in [(0.0, "$x_1$"), (2.6, "$x_2$"), (4.0, r"$\dots$"), (5.4, "$x_n$")]:
    ax.text(x, 6.0, label, ha="center", va="center", fontsize=14, color=INK)

# negation of x1
ax.add_patch(Polygon([(-0.3, 4.9), (0.3, 4.9), (0.0, 4.4)], closed=True, facecolor=GATE,
                     edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
ax.text(0.0, 4.72, r"$\neg$", ha="center", va="center", fontsize=12, color=INK, zorder=3)
wire((0.0, 5.8), (0.0, 4.9))

# subfunction blocks
box(2.0, 3.6, r"$f(0,x_2,\dots,x_n)$")
box(5.0, 3.6, r"$f(1,x_2,\dots,x_n)$")
for bx in (2.0, 5.0):
    wire((2.6, 5.8), (2.6, 5.3), (bx, 4.0))
    wire((5.4, 5.8), (5.4, 5.3), (bx, 4.0))

# conjunctions and disjunction
gate(1.4, 2.0, r"$\cdot$")
gate(4.6, 2.0, r"$\cdot$")
gate(3.0, 0.5, r"$\vee$")
wire((0.0, 4.4), (0.0, 3.0), (1.1, 2.3))
wire((2.0, 3.2), (2.0, 2.8), (1.7, 2.3))
wire((5.0, 3.2), (5.0, 2.8), (4.6, 2.3))
# x1 reaches the right conjunction around the top and right side, crossing no wire
wire((0.0, 5.6), (-0.9, 5.6), (-0.9, 6.5), (6.2, 6.5), (6.2, 2.7), (5.0, 2.3))
wire((1.4, 1.7), (1.4, 1.2), (2.7, 0.8))
wire((4.6, 1.7), (4.6, 1.2), (3.3, 0.8))
wire((3.0, 0.2), (3.0, -0.4))
ax.text(3.0, -0.75, r"$f(x_1,\dots,x_n)$", ha="center", va="center", fontsize=13, color=INK)

ax.set_xlim(-1.5, 6.7)
ax.set_ylim(-1.1, 6.8)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 1, "shannon-circuit")
