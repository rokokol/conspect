"""Shared helpers for the figures of section f05 "Силы" (lessons 32-41).

The scripts forces_basic.py and gravity_basic.py import this module.
Run: python3 forces_basic.py; python3 gravity_basic.py
PNG files go to content/05. Силы/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "05. Силы"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint  # noqa: F401  star-imported by the users

GRID = ASH
GREY = MUTED  # guides, auxiliary lines and arrows, inactive parts
NOTE = tint(INK, 0.4)  # small notes and secondary text
FORCE = RED  # the force the figure is about
GOLD = WARM  # gold, a coin, a thin plate
WOOD = tint(COPPER, 0.35)  # wood as a fill
STONE = tint(INK, 0.35)  # a stone, a heavy grey body
EARTH = COPPER  # the ground


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def blank_row(n, w, h, xlim, ylim):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    for ax in np.atleast_1d(axes):
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def cart(ax, x, y, w=2.0, h=0.8, face=LIGHT, load=0.0):
    """Cart with two wheels; load is the height of a weight on top."""
    ax.add_patch(Rectangle((x, y), w, h, fc=face, ec=INK, lw=1.4, zorder=3))
    if load:
        ax.add_patch(Rectangle((x + w * 0.3, y + h), w * 0.4, load, fc=STONE, ec=INK, lw=1.2, zorder=3))
    for cx in (x + w * 0.22, x + w * 0.78):
        ax.add_patch(Circle((cx, y - 0.02), 0.14, fc=PAPER, ec=INK, lw=1.2, zorder=4))
    ax.plot([x - 0.4, x + w + 0.4], [y - 0.17, y - 0.17], color=GREY, lw=1, zorder=1)


def dim_bar(ax, p, q, text, off=(0, 0.25), fs=10.5, color=INK):
    arrow(ax, p, q, color=color, lw=1.2, style="<|-|>", scale=9)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="center", fontsize=fs, color=color)
