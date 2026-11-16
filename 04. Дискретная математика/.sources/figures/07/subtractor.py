"""Subtractor of order n: negations on x, adder S_n with y, negations on the low n outputs; z_0 stays unused."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT
MUTED = dmfig.tint(dmfig.INK, 0.45)  # dmfig.MUTED is too pale for text
R = 0.34

fig, ax = plt.subplots(figsize=(9.0, 6.6))


def arrow(p, q, colour=EDGE, lw=2, style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=16, shrinkA=0, shrinkB=0,
                                 color=colour, linewidth=lw, zorder=1))


def neg(x, y):
    ax.add_patch(Circle((x, y), R, facecolor=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
    ax.text(x, y, r"$\neg$", ha="center", va="center", fontsize=16, color=INK, zorder=3)


# adder S_n with its input and output ports
ax.add_patch(Rectangle((0.0, 2.0), 9.0, 1.5, facecolor=dmfig.tint(dmfig.P["natsuki"], 0.6),
                       edgecolor=dmfig.VERTEX_EDGE, linewidth=1.8, zorder=2))
ax.text(4.5, 2.75, r"$S_n$", ha="center", va="center", fontsize=22, color=INK, zorder=3)

xs = {"1": 1.0, "n": 3.6}      # ports of the first number, negated
ys = {"1": 5.4, "n": 8.0}      # ports of the second number, direct
outs = {"0": 0.8, "1": 3.2, "n": 5.8}

for idx, px in xs.items():
    ax.text(px, 7.4, rf"$x_{{{idx}}}$", ha="center", va="bottom", fontsize=13, color=INK)
    arrow((px, 7.35), (px, 5.9 + R), style="-")
    neg(px, 5.9)
    arrow((px, 5.9 - R), (px, 3.5))
for idx, px in ys.items():
    ax.text(px, 7.4, rf"$y_{{{idx}}}$", ha="center", va="bottom", fontsize=13, color=INK)
    arrow((px, 7.35), (px, 3.5))
ax.text(2.3, 6.55, r"$\cdots$", ha="center", va="center", fontsize=20, color=INK)
ax.text(6.7, 6.55, r"$\cdots$", ha="center", va="center", fontsize=20, color=INK)

# outputs: z_0 is dropped, z_1..z_n pass through negations
arrow((outs["0"], 2.0), (outs["0"], 0.6), MUTED)
ax.text(outs["0"], 0.3, r"$z_0=0$", ha="center", va="top", fontsize=13, color=MUTED)
for idx in ("1", "n"):
    px = outs[idx]
    arrow((px, 2.0), (px, 1.2 + R), style="-")
    neg(px, 1.2)
    arrow((px, 1.2 - R), (px, -0.2), HIGHLIGHT)
    ax.text(px, -0.5, rf"$z_{{{idx}}}$", ha="center", va="top", fontsize=13, color=INK)
ax.text(4.5, 0.5, r"$\cdots$", ha="center", va="center", fontsize=20, color=INK)

ax.text(8.3, 1.0, "$z_0$ не используется:\nпри $X\\geqslant Y$ там всегда $0$", ha="left", va="center",
        fontsize=11, color=MUTED)

ax.set_xlim(-0.8, 11.5)
ax.set_ylim(-1.3, 8.4)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, 7, "subtractor")
