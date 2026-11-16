"""The first step of the SFED theorem: a delay is cut out, its vertex becomes a source q', the vertex before it becomes an output q."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

INK, EDGE, HIGHLIGHT, MUTED = dmfig.INK, dmfig.EDGE, dmfig.HIGHLIGHT, dmfig.MUTED
INPUT_FILL = dmfig.tint(dmfig.P["natsuki"], 0.6)
DELAY_FILL = dmfig.tint(dmfig.P["sayori"], 0.5)

R = 0.36
fig, (axl, axr) = plt.subplots(1, 2, figsize=(10.4, 4.4))


def source(ax, xy, label, fill=INPUT_FILL):
    p = Rectangle((xy[0] - R, xy[1] - R), 2 * R, 2 * R, facecolor=fill,
                  edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2)
    ax.add_patch(p)
    ax.text(*xy, label, ha="center", va="center", fontsize=15, color=INK, zorder=3)
    return p


def element(ax, xy, label, output=False, fill=dmfig.VERTEX):
    p = Circle(xy, R, facecolor=fill, edgecolor=HIGHLIGHT if output else dmfig.VERTEX_EDGE,
               linewidth=3.2 if output else 1.6, zorder=2)
    ax.add_patch(p)
    ax.text(*xy, label, ha="center", va="center", fontsize=15, color=INK, zorder=3)
    return p


def arc(ax, a, b, pa, pb, rad=0.0, color=EDGE, style="-"):
    ax.add_patch(FancyArrowPatch(a, b, patchA=pa, patchB=pb, arrowstyle="-|>", mutation_scale=16,
                                 shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}",
                                 color=color, linewidth=2, linestyle=style, zorder=1))


# left: the circuit with a delay
X, A, Z = (0.0, 2.6), (0.0, 0.8), (2.6, 0.8)
px = source(axl, X, r"$x$")
pa = element(axl, A, r"$\vee$", output=True)
pz = element(axl, Z, r"$\mathrm{з}$", fill=DELAY_FILL)
arc(axl, X, A, px, pa)
arc(axl, A, Z, pa, pz, rad=0.35)
arc(axl, Z, A, pz, pa, rad=0.35)
axl.add_patch(FancyArrowPatch((0, 0.8 - R), (0, -0.55), arrowstyle="-|>", mutation_scale=16,
                              color=HIGHLIGHT, linewidth=2, zorder=1))
axl.text(0, -0.85, r"$y$", ha="center", va="center", fontsize=15, color=INK)
axl.text(1.3, 2.9, "СФЭЗ", ha="center", fontsize=13, color=INK)

# right: after cutting
X2, A2, Q2 = (0.0, 2.6), (0.0, 0.8), (2.6, 0.8)
px = source(axr, X2, r"$x$")
pa = element(axr, A2, r"$\vee$", output=True)
pq = source(axr, Q2, r"$q'$", fill=dmfig.tint(dmfig.P["sayori"], 0.5))
arc(axr, X2, A2, px, pa)
arc(axr, Q2, A2, pq, pa, rad=0.35)
axr.add_patch(FancyArrowPatch(A2, Q2, patchA=pa, patchB=pq, arrowstyle="-", shrinkA=0, shrinkB=0,
                              connectionstyle="arc3,rad=0.35", color=EDGE, alpha=0.45, linewidth=2,
                              linestyle=(0, (3, 3)), zorder=1))
axr.text(1.7, -0.1, "дуга убрана", ha="center", va="center", fontsize=11, color=INK)
axr.add_patch(FancyArrowPatch((0, 0.8 - R), (0, -0.55), arrowstyle="-|>", mutation_scale=16,
                              color=HIGHLIGHT, linewidth=2, zorder=1))
axr.text(0, -0.85, r"$y,\ q$", ha="center", va="center", fontsize=15, color=INK)
axr.text(1.3, 2.9, "СФЭ", ha="center", fontsize=13, color=INK)

# key
kx, ky = 0.2, -1.9
axr.add_patch(Rectangle((kx - 0.15, ky - 0.15), 0.3, 0.3, facecolor=INPUT_FILL,
                        edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
axr.text(kx + 0.35, ky, "вход (исток)", va="center", fontsize=11, color=INK)
axr.add_patch(Circle((kx, ky - 0.6), 0.17, facecolor=dmfig.VERTEX, edgecolor=HIGHLIGHT, linewidth=3.2))
axr.text(kx + 0.35, ky - 0.6, "выход схемы", va="center", fontsize=11, color=INK)
axr.add_patch(Rectangle((kx - 0.15, ky - 1.35), 0.3, 0.3, facecolor=DELAY_FILL,
                        edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
axr.text(kx + 0.35, ky - 1.2, "новый вход на месте задержки", va="center", fontsize=11, color=INK)

axl.add_patch(Rectangle((kx - 0.15, ky + 0.45), 0.3, 0.3, facecolor=INPUT_FILL,
                        edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
axl.text(kx + 0.35, ky + 0.6, "вход (исток)", va="center", fontsize=11, color=INK)
axl.add_patch(Circle((kx, ky), 0.17, facecolor=DELAY_FILL, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6))
axl.text(kx + 0.35, ky, "задержка", va="center", fontsize=11, color=INK)
axl.add_patch(Circle((kx, ky - 0.6), 0.17, facecolor=dmfig.VERTEX, edgecolor=HIGHLIGHT, linewidth=3.2))
axl.text(kx + 0.35, ky - 0.6, "выход схемы", va="center", fontsize=11, color=INK)

for ax in (axl, axr):
    ax.set_xlim(-1.2, 3.6)
    ax.set_ylim(-4.0, 3.3)
    ax.set_aspect("equal")
    ax.axis("off")
dmfig.save(fig, 7, "sfed-cut-delay")
