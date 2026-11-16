"""Shared helpers for the figures of section f07 (floating bodies, ships, balloons).

Colour code as in pressure_atmosphere.py: force red, water light blue, mercury grey, oil amber.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = COURSE / "content" / "07. Закон Архимеда и плавание" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
NOMEDIA = OUT / ".nomedia"
if not NOMEDIA.exists():
    NOMEDIA.touch()

from theme import ACCENT, ASH, COPPER, GREEN, INK, METAL, MUTED, PAPER, PINK, RED, SKY, VIOLET, WARM, num, saver, tint  # noqa: F401

GREY = MUTED
LIGHT = tint(INK, 0.9)  # a pale grey part: a gondola, a plate
GRID = ASH
C_F = RED  # force, gravity, a pressing or lifting force
C_A = ACCENT  # the Archimedes force, as in archimedes_law.py
HOT = RED  # hot air
WATER = tint(SKY, 0.7)
WATER_EDGE = SKY
MERC = tint(INK, 0.6)
MERC_EDGE = tint(INK, 0.3)
OIL = tint(WARM, 0.55)
OIL_EDGE = WARM
WOOD = tint(COPPER, 0.55)
WOOD_EDGE = COPPER
ICE = tint(SKY, 0.88)
ICE_EDGE = SKY
STEEL = METAL
SINKS = tint(RED, 0.88)  # the range of densities where a body sinks
PLASTICINE = tint(VIOLET, 0.7)
PLASTICINE_EDGE = VIOLET
SALT = tint(GREEN, 0.8)
SALT_EDGE = GREEN


save = saver(OUT)


def blank(w, h, xlim, ylim, n=1):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    axes = np.atleast_1d(axes)
    for ax in axes:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=13, ls="-", z=8):
    ax.add_patch(
        FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, linestyle=ls, zorder=z)
    )


def line(ax, xs, ys, color=INK, lw=2, z=4, **kw):
    ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle="round", **kw)


def rect(ax, x, y, w, h, fc="none", ec=INK, lw=1.8, z=3, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))


def label(ax, x, y, text, fs=11, color=INK, ha="center", va="center", **kw):
    kw.setdefault("zorder", 10)
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, **kw)


def liquid(ax, x0, x1, y0, y1, fc=WATER, ec=WATER_EDGE, z=1):
    """A filled liquid layer with a solid surface line."""
    rect(ax, x0, y0, x1 - x0, y1 - y0, fc=fc, ec="none", z=z)
    line(ax, [x0, x1], [y1, y1], color=ec, lw=2, z=z + 1)


def vessel(ax, x0, x1, y0, y1, lw=2.4):
    """Open vessel outline: bottom and two walls."""
    line(ax, [x0, x0, x1, x1], [y1, y0, y0, y1], color=INK, lw=lw, z=6)


def dim_v(ax, x, y0, y1, text, color=INK, side="right", fs=10.5):
    arrow(ax, (x, y0), (x, y1), color=color, lw=1.3, style="<|-|>", scale=9)
    dx = 0.18 if side == "right" else -0.18
    label(ax, x + dx, (y0 + y1) / 2, text, fs=fs, color=color, ha="left" if side == "right" else "right")


def style_axes(ax, xlabel, ylabel, title=None):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
