"""Drawing helpers of topic 05: a code graph with directed arcs and parsings of a word into codewords."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

TOPIC = 5


def draw_digraph(ax, pos, arcs, labels, fills=None, bent=None, arc_colours=None, label_pos=None, radius=0.2):
    """Directed graph: arcs is [(u, v)], bent {(u, v): rad} curves an arc, label_pos {(u, v): (x, y)} fixes a label."""
    fills = fills or {}
    bent = bent or {}
    arc_colours = arc_colours or {}
    for arc in arcs:
        u, v = arc
        ax.add_patch(FancyArrowPatch(
            pos[u], pos[v], arrowstyle="-|>", mutation_scale=18, shrinkA=radius * 72 * 0.62,
            shrinkB=radius * 72 * 0.62, connectionstyle=f"arc3,rad={bent.get(arc, 0)}",
            color=arc_colours.get(arc, dmfig.EDGE), linewidth=2, zorder=1))
    for v, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), radius, facecolor=fills.get(v, dmfig.VERTEX),
                            edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6, zorder=2))
        ax.text(x, y, labels[v], ha="center", va="center", fontsize=14, color=dmfig.INK, zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()


def draw_word(ax, word, y, cell=1.0, x0=0.0):
    """The word as a row of boxes, one per symbol."""
    for i, ch in enumerate(word):
        ax.add_patch(FancyBboxPatch((x0 + i * cell + 0.04, y), cell - 0.08, 0.7, boxstyle="round,pad=0,rounding_size=0.08",
                                    facecolor="#ffffff", edgecolor=dmfig.VERTEX_EDGE, linewidth=1.4, zorder=2))
        ax.text(x0 + (i + 0.5) * cell, y + 0.35, ch, ha="center", va="center", fontsize=16, color=dmfig.INK, zorder=3)


def draw_legend(ax, entries, x, y, step=0.55):
    """A colour key under the parsings: entries is [(fill, text)], one row each."""
    for k, (fill, text) in enumerate(entries):
        yy = y - k * step
        ax.add_patch(FancyBboxPatch((x, yy - 0.15), 0.5, 0.3, boxstyle="round,pad=0,rounding_size=0.05",
                                    facecolor=fill, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.2))
        ax.text(x + 0.65, yy, text, ha="left", va="center", fontsize=11, color=dmfig.INK)


def draw_parsing(ax, parts, y, fills, names=None, cell=1.0, x0=0.0):
    """A parsing: one bracket per codeword, filled in turn from `fills`; `names` go under the brackets."""
    pos = 0
    for k, w in enumerate(parts):
        ax.add_patch(FancyBboxPatch((x0 + pos * cell + 0.04, y), len(w) * cell - 0.08, 0.7,
                                    boxstyle="round,pad=0,rounding_size=0.08",
                                    facecolor=fills[k % len(fills)], edgecolor=dmfig.VERTEX_EDGE, linewidth=1.4, zorder=2))
        ax.text(x0 + (pos + len(w) / 2) * cell, y + 0.35, w, ha="center", va="center", fontsize=15, color=dmfig.INK, zorder=3)
        if names:
            ax.text(x0 + (pos + len(w) / 2) * cell, y - 0.3, names[k], ha="center", va="center", fontsize=12, color=dmfig.INK,
                    bbox=dict(boxstyle="square,pad=0.1", facecolor=ax.figure.get_facecolor(), edgecolor="none"), zorder=4)
        pos += len(w)
