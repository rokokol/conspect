"""Shared drawing of a complex plane for the figures of topic 01."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc  # noqa: E402


def new_plane(xlim, ylim, size=(5.2, 5.2)):
    """Axes with the real and the imaginary axis drawn as arrows through the origin."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    arrow = dict(arrowstyle="-|>", color=lafig.MUTED, lw=1.2, shrinkA=0, shrinkB=0)
    ax.annotate("", xy=(xlim[1], 0), xytext=(xlim[0], 0), arrowprops=arrow)
    ax.annotate("", xy=(0, ylim[1]), xytext=(0, ylim[0]), arrowprops=arrow)
    ax.text(xlim[1], -0.07 * (ylim[1] - ylim[0]), r"$\mathrm{Re}\,z$", ha="right", va="top", color=lafig.INK)
    ax.text(0.03 * (xlim[1] - xlim[0]), ylim[1], r"$\mathrm{Im}\,z$", ha="left", va="top", color=lafig.INK)
    return fig, ax


def vector(ax, w, color, lw=2.2, style="-|>"):
    """Arrow from the origin to the complex number w."""
    ax.annotate(
        "",
        xy=(w.real, w.imag),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0),
    )


def angle(ax, radius, deg_from, deg_to, color, label=None, label_r=None):
    """Counter-clockwise arc about the origin, with an optional label at its middle."""
    ax.add_patch(Arc((0, 0), 2 * radius, 2 * radius, theta1=deg_from, theta2=deg_to, color=color, lw=1.6))
    if label:
        mid = np.deg2rad((deg_from + deg_to) / 2)
        r = label_r if label_r is not None else radius * 1.25
        ax.text(r * np.cos(mid), r * np.sin(mid), label, color=color, ha="center", va="center")
