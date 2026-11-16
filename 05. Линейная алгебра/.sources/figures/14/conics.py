"""Shared drawing helpers of the conic figures: the axes frame, point labels and the figure legend."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402,F401
from matplotlib.lines import Line2D  # noqa: E402


def frame(ax, xlim, ylim, xlabel="$x$", ylabel="$y$"):
    """Equal-scale axes without ticks, the coordinate axes drawn as thin lines with arrows' labels."""
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axhline(0, color=lafig.MUTED, lw=0.9, zorder=0)
    ax.axvline(0, color=lafig.MUTED, lw=0.9, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.text(xlim[1], -0.07 * (ylim[1] - ylim[0]), xlabel, color=lafig.INK, ha="right", va="top")
    ax.text(0.03 * (xlim[1] - xlim[0]), ylim[1], ylabel, color=lafig.INK, ha="left", va="top")


def label(ax, xy, text, offset, color=None, ha="center", halo=False):
    """A text at xy + offset; halo puts a white plate under it where it crosses a curve."""
    plate = dict(fc="white", ec="none", alpha=0.85, pad=1.5) if halo else None
    ax.text(xy[0] + offset[0], xy[1] + offset[1], text, color=color or lafig.INK, ha=ha, va="center", bbox=plate)


def line(color, label_text, lw=2.0, ls="-"):
    return Line2D([0], [0], color=color, lw=lw, ls=ls, label=label_text)


def dot(color, label_text, filled=True):
    return Line2D([0], [0], marker="o", ls="", color=color, markerfacecolor=color if filled else "none",
                  markersize=7, label=label_text)
