"""Shared helpers for the figures of section f02 "Строение вещества" (lessons 11-14).

The scripts matter_atoms.py and matter_states.py import this module.
Run: python3 matter_atoms.py; python3 matter_states.py
PNG files go to content/02. Строение вещества/00. Вложения/
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
    / "02. Строение вещества"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, VIOLET, WARM, saver, tint  # noqa: F401  star-imported by the users

GRID = ASH
GLASS = tint(SKY, 0.8)
WATER = tint(SKY, 0.6)  # water as a fill
WATER_D = BLUE  # water or cold as a line, a text or an arrow
ORANGE = WARM
GOLD = WARM
LEAD = tint(INK, 0.45)
GREY = MUTED  # guides and inactive parts
NOTE = tint(INK, 0.4)  # small notes and secondary text
SOOT = INK


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


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", scale=13, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def dim(ax, p, q, text, off=(0, 0), color=INK, fs=10, ha="center", va="center"):
    arrow(ax, p, q, color=color, lw=1.1, style="<->", scale=10)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, color=color, fontsize=fs, ha=ha, va=va)


def shade(color, k):
    c = np.array(matplotlib.colors.to_rgb(color))
    return tuple(np.clip(c * k, 0, 1))
