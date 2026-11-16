"""Shared drawing of second-order surfaces for the figures of topic 15 (and the ruled surfaces of topic 15)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "03"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "02"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402


def panel(fig, spec, lim, title, elev=20, azim=-58, zoom=1.15):
    """A frameless 3D axes with the three coordinate axes drawn from the origin and a title."""
    ax = v3d.new_axes(fig, spec, lim, elev=elev, azim=azim, zoom=zoom)
    ax.computed_zorder = False
    for k, text in enumerate((r"$x$", r"$y$", r"$z$")):
        vec = np.zeros(3)
        vec[k] = lim[k][1]
        ax.plot(*zip(np.zeros(3), vec), color=lafig.MUTED, lw=0.9, zorder=1)
        ax.text(*(vec * 1.08), text, color=lafig.INK, ha="center", va="center", zorder=6)
    ax.set_title(title, y=0.96, color=lafig.INK)
    return ax


def sheet(ax, X, Y, Z, alpha=0.28):
    """A pale filled sheet of the surface with no mesh lines: the curves drawn over it carry the shape."""
    ax.plot_surface(X, Y, Z, color=lafig.tint(lafig.VECTOR, 0.3), alpha=alpha, linewidth=0,
                    antialiased=True, shade=False, rstride=1, cstride=1, zorder=2)


def curve(ax, X, Y, Z, color, lw=1.3, ls="-", zorder=4):
    """A space curve through the points (X, Y, Z)."""
    ax.plot(X, Y, Z, color=color, lw=lw, ls=ls, zorder=zorder)


def key(fig, entries, ncol=2, y=0.0):
    """The legend of the figure: entries are (colour, width, text) or (colour, width, text, line style)."""
    fig.legend(handles=[Line2D([0], [0], color=e[0], lw=e[1], label=e[2], ls=e[3] if len(e) > 3 else "-")
                        for e in entries],
               loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)
