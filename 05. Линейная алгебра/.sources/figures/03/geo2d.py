"""Shared drawing of vectors and lines in the plane for the figures of topic 03."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc  # noqa: E402


def new_axes(ax, xlim, ylim, labels=(r"$x_1$", r"$x_2$"), axes=True):
    """A frameless equal-aspect axes; with `axes` the two coordinate axes are drawn as arrows."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    if axes:
        style = dict(arrowstyle="-|>", color=lafig.MUTED, lw=1.1, shrinkA=0, shrinkB=0)
        ax.annotate("", xy=(xlim[1], 0), xytext=(xlim[0], 0), arrowprops=style)
        ax.annotate("", xy=(0, ylim[1]), xytext=(0, ylim[0]), arrowprops=style)
        ax.text(xlim[1], -0.05 * (ylim[1] - ylim[0]), labels[0], ha="right", va="top", color=lafig.INK)
        ax.text(0.03 * (xlim[1] - xlim[0]), ylim[1], labels[1], ha="left", va="top", color=lafig.INK)


def arrow(ax, start, vec, color, lw=2.2, ls="-", style="-|>"):
    """Arrow from `start` along `vec`."""
    ax.annotate("", xy=np.add(start, vec), xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def line(ax, point, direction, half, color, lw=1.8, ls="-"):
    """Segment of a line through `point` along `direction`, `half` long on both sides."""
    d = np.asarray(direction, float)
    d = d / np.linalg.norm(d)
    p = np.asarray(point, float)
    ax.plot(*zip(p - half[0] * d, p + half[1] * d), color=color, lw=lw, ls=ls)


def square(ax, corner, u, w, size=0.14):
    """Right-angle mark at `corner` between the directions u and w."""
    c = np.asarray(corner, float)
    u, w = np.asarray(u, float), np.asarray(w, float)
    u, w = size * u / np.linalg.norm(u), size * w / np.linalg.norm(w)
    ax.plot(*zip(c + u, c + u + w, c + w), color=lafig.MUTED, lw=1.0)


def angle(ax, center, deg_from, deg_to, radius, color, label=None, label_r=None):
    """Counter-clockwise arc about `center`, with an optional label at its middle."""
    ax.add_patch(Arc(center, 2 * radius, 2 * radius, theta1=deg_from, theta2=deg_to, color=color, lw=1.6))
    if label:
        mid = np.deg2rad((deg_from + deg_to) / 2)
        r = label_r if label_r is not None else radius * 1.3
        ax.text(center[0] + r * np.cos(mid), center[1] + r * np.sin(mid), label, color=color, ha="center", va="center")


def dot(ax, p, color, size=26):
    ax.scatter([p[0]], [p[1]], s=size, color=color, zorder=5)
