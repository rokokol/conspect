"""Shared drawing helpers for the notes of section f12 (electromagnets, motors, measuring instruments).

All figures are matplotlib drawings in data coordinates with a fixed aspect.
PNG files go to content/12. Магнитные явления/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = COURSE / "content" / "12. Магнитные явления" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, PAPER, RED, VIOLET, WARM, saver, tint  # noqa: F401  (COPPER, LIGHT, METAL, PAPER, VIOLET, WARM, tint reach the users through *)

GRID = ASH
GREY = tint(INK, 0.4)  # guides, small notes and the lines that stand for them
ORANGE = ACCENT  # a motion, a moving part: the name is kept, the role is ACCENT
IRON = tint(INK, 0.8)  # iron cores
# Course convention (lecture U170): the north pole and the north end of a needle are blue, the south ones are red.
# Field lines and field arrows are green, so that they do not merge with the blue pole.
NORTH = BLUE
SOUTH = RED
FIELD = GREEN


save = saver(OUT)


def grid(ax):
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def blank(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def blank_multi(rows, cols, w, h, xlim, ylim):
    f, axs = plt.subplots(rows, cols, figsize=(w, h))
    axs = np.atleast_1d(axs).ravel()
    for ax in axs:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return f, axs


def txt(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, shrinkA=0, shrinkB=0, **kw))


def line(ax, pts, color=INK, lw=1.8, **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round", **kw)


def rect(ax, x, y, w, h, fc=LIGHT, ec=INK, lw=1.6, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def circ(ax, x, y, r, fc=PAPER, ec=INK, lw=1.6, **kw):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, **kw))


def poly(ax, pts, fc=LIGHT, ec=INK, lw=1.6, **kw):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, **kw))


def cross_in(ax, x, y, r=0.16, color=INK, lw=1.5):
    """Current or field into the page: a circle with a cross."""
    circ(ax, x, y, r, fc=PAPER, ec=color, lw=lw, zorder=6)
    d = r * 0.68
    ax.plot([x - d, x + d], [y - d, y + d], color=color, lw=lw, zorder=7)
    ax.plot([x - d, x + d], [y + d, y - d], color=color, lw=lw, zorder=7)


def dot_out(ax, x, y, r=0.16, color=INK, lw=1.5):
    """Current or field out of the page: a circle with a dot."""
    circ(ax, x, y, r, fc=PAPER, ec=color, lw=lw, zorder=6)
    ax.plot([x], [y], "o", color=color, ms=r * 22, zorder=7)


def battery(ax, x, y, horizontal=True, size=0.5, color=INK, label=True, flip=False):
    """Cell: long plate is plus. Centered at (x, y). Wires attach at +-size from the centre."""
    s = size
    if horizontal:
        sgn = -1 if flip else 1
        ax.plot([x - sgn * s * 0.25, x - sgn * s * 0.25], [y - s * 0.55, y + s * 0.55], color=color, lw=2.4)
        ax.plot([x + sgn * s * 0.25, x + sgn * s * 0.25], [y - s * 0.32, y + s * 0.32], color=color, lw=3.4)
        ax.plot([x - sgn * s, x - sgn * s * 0.25], [y, y], color=color, lw=1.8)
        ax.plot([x + sgn * s * 0.25, x + sgn * s], [y, y], color=color, lw=1.8)
        if label:
            txt(ax, x - sgn * s * 0.25 - sgn * 0.02, y + s * 0.85, "+", 10, ha="center")
            txt(ax, x + sgn * s * 0.25, y + s * 0.85, "−", 10, ha="center")
    else:
        sgn = -1 if flip else 1
        ax.plot([x - s * 0.55, x + s * 0.55], [y + sgn * s * 0.25, y + sgn * s * 0.25], color=color, lw=2.4)
        ax.plot([x - s * 0.32, x + s * 0.32], [y - sgn * s * 0.25, y - sgn * s * 0.25], color=color, lw=3.4)
        ax.plot([x, x], [y - sgn * s, y - sgn * s * 0.25], color=color, lw=1.8)
        ax.plot([x, x], [y + sgn * s * 0.25, y + sgn * s], color=color, lw=1.8)
        if label:
            txt(ax, x + s * 0.85, y + sgn * s * 0.25, "+", 10)
            txt(ax, x + s * 0.85, y - sgn * s * 0.25, "−", 10)


def lamp(ax, x, y, r=0.32, color=INK):
    circ(ax, x, y, r, ec=color)
    d = r * 0.7
    ax.plot([x - d, x + d], [y - d, y + d], color=color, lw=1.6)
    ax.plot([x - d, x + d], [y + d, y - d], color=color, lw=1.6)


def motor(ax, x, y, r=0.38, color=INK, letter="M"):
    circ(ax, x, y, r, ec=color)
    txt(ax, x, y, letter, 12, color=color)


def node(ax, x, y, r=0.06, color=INK):
    ax.plot([x], [y], "o", color=color, ms=r * 60, zorder=8)


def terminal(ax, x, y, r=0.07, color=INK):
    circ(ax, x, y, r, fc=PAPER, ec=color, lw=1.4, zorder=8)


def coil_horizontal(ax, x0, x1, y, h=0.5, n=6, color=INK, core=True, core_fc=IRON, wind=+1, lw=1.8, arrows=False):
    """Solenoid seen from the side. `wind` gives the slant of the visible turns: +1 goes up to the right."""
    if core:
        rect(ax, x0 - 0.35, y - h * 0.5, (x1 - x0) + 0.7, h, fc=core_fc, ec=INK, lw=1.4, zorder=1)
    xs = np.linspace(x0, x1, n)
    step = (x1 - x0) / (n - 1) if n > 1 else 0.3
    for xi in xs:
        ax.plot([xi - wind * step * 0.22, xi + wind * step * 0.22], [y - h * 0.62, y + h * 0.62], color=color, lw=lw, zorder=3)


def coil_vertical(ax, x, y0, y1, w=0.5, n=6, color=INK, core=True, core_fc=IRON, wind=+1, lw=1.8):
    if core:
        rect(ax, x - w * 0.5, y0 - 0.35, w, (y1 - y0) + 0.7, fc=core_fc, ec=INK, lw=1.4, zorder=1)
    ys = np.linspace(y0, y1, n)
    step = (y1 - y0) / (n - 1) if n > 1 else 0.3
    for yi in ys:
        ax.plot([x - w * 0.62, x + w * 0.62], [yi - wind * step * 0.22, yi + wind * step * 0.22], color=color, lw=lw, zorder=3)


def field_loop_v(ax, x, ytop, ybot, spread, color=FIELD, lw=1.4, n=1, side=+1):
    """Closed field line outside a vertical coil: comes out at the top, goes around, enters at the bottom."""
    t = np.linspace(0, np.pi, 80)
    xs = x + side * spread * np.sin(t)
    ys = ytop - (ytop - ybot) * (1 - np.cos(t)) / 2
    ax.plot(xs, ys, color=color, lw=lw)
    k = 34
    arrow(ax, (xs[k], ys[k]), (xs[k + 3], ys[k + 3]), color=color, lw=lw, scale=11)


def pole_label(ax, x, y, s, color=INK, size=13):
    txt(ax, x, y, s, size, color=color, weight="bold")
