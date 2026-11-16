"""Figures for the notes "Электрический ток в металлах" and "Электрический ток в жидкостях. Электролиз" (section f13, lessons 183-188 and 191).

Run: nix shell nixpkgs#python3Packages.matplotlib nixpkgs#poppler-utils -c python3 current_media_1.py [name ...]
The system pdflatex needs the tikz package for the circuit schemes.
PNG files go to content/13. Электрический ток в средах/00. Вложения/ (prefixes metal-, electrolysis-)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Arc, Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "13. Электрический ток в средах"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from circuit_diagrams import COLOUR_DEFS  # the TikZ colour names, one source for every circuit script
from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, PAPER, PINK, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
C1, C2, C3, C4 = RED, BLUE, GREEN, VIOLET  # the first curves of theme.SERIES
C5 = WARM  # a gold, glowing or yellow mark
GREY = tint(INK, 0.4)  # guides and small notes
ALUM = tint(INK, 0.8)
WATER = tint(SKY, 0.8)
SOLUTION = tint(SKY, 0.75)
SOFT = tint(INK, 0.94)  # the pale body fill of a part
PLATE = tint(INK, 0.87)  # a grey plate or a block
DARK = tint(INK, 0.2)  # a dark part: a rod, a carbon electrode
POS_FILL = tint(RED, 0.85)  # the pale fill of a positive ion or charge
NEG_FILL = tint(BLUE, 0.85)  # the pale fill of a negative ion or charge

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def canvas(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", ms=12, ls="-", z=5):
    ax.annotate(
        "",
        xy=q,
        xytext=p,
        arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms, linestyle=ls),
        zorder=z,
    )


def line(ax, pts, color=INK, lw=1.6, ls="-", z=3):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)


def txt(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=10, **kw)


def dim_h(ax, x0, x1, y, label, size=11):
    arrow(ax, (x0, y), (x1, y), GREY, 1.1, "<|-|>", 9)
    txt(ax, (x0 + x1) / 2, y - 0.28, label, size, GREY)


def electron(ax, x, y, r=0.09, z=6):
    ax.add_patch(Circle((x, y), r, fc=C2, ec="none", zorder=z))


def ion(ax, x, y, sign="+", r=0.27, color=C1, size=12):
    ax.add_patch(Circle((x, y), r, fc=POS_FILL if color == C1 else NEG_FILL, ec=color, lw=1.3, zorder=4))
    txt(ax, x, y - 0.02, sign, size, color)


def bubble(ax, x, y, r=0.09):
    ax.add_patch(Circle((x, y), r, fc=PAPER, ec=GREY, lw=1.0, zorder=6))


# ---------------------------------------------------------------- metal: carriers


@fig("metal-lattice-electrons")
def _():
    f, ax = canvas(6.8, 4.6, (-0.7, 8.7), (-0.9, 5.0))
    ax.add_patch(FancyBboxPatch((-0.5, -0.5), 8.4, 5.0, boxstyle="round,pad=0.02,rounding_size=0.15", fc=SOFT, ec=GREY, lw=1.2))
    pts = [(i, j) for i in range(8) for j in range(5)]
    for x, y in pts:
        ion(ax, x - 0.0 + 0.0, y, "+")
    rng = np.random.default_rng(5)
    placed = []
    while len(placed) < 22:
        x, y = rng.uniform(-0.3, 7.7), rng.uniform(-0.3, 4.3)
        if min(np.hypot(x - a, y - b) for a, b in pts) < 0.5:
            continue
        if any(np.hypot(x - a, y - b) < 0.45 for a, b in placed):
            continue
        placed.append((x, y))
    for x, y in placed:
        electron(ax, x, y, 0.1)
        a = rng.uniform(0, 2 * np.pi)
        arrow(ax, (x, y), (x + 0.32 * np.cos(a), y + 0.32 * np.sin(a)), C2, 1.0, ms=7)
    ax.add_patch(Circle((0.6, -0.72), 0.16, fc=POS_FILL, ec=C1, lw=1.2))
    txt(ax, 0.9, -0.72, "ион в узле решётки", 10, INK, "left")
    electron(ax, 3.9, -0.72, 0.1)
    txt(ax, 4.15, -0.72, "свободный электрон", 10, INK, "left")
    save(f, "metal-lattice-electrons")


def walk(n, drift, seed=11):
    rng = np.random.default_rng(seed)
    p = [np.zeros(2)]
    for _ in range(n):
        a = rng.uniform(0, 2 * np.pi)
        r = rng.uniform(0.9, 1.7)
        p.append(p[-1] + r * np.array([np.cos(a), np.sin(a)]) + np.array([drift, 0.0]))
    return np.array(p)


@fig("metal-random-vs-drift")
def _():
    f, axs = plt.subplots(1, 2, figsize=(9.8, 3.4))
    for ax, drift, title in zip(axs, (0.0, 1.0), ("Электрического поля нет", "Поле включено: тепловое движение плюс дрейф")):
        p = walk(15, drift)
        ax.plot(p[:, 0], p[:, 1], color=C2, lw=1.4, zorder=3)
        ax.scatter(p[1:-1, 0], p[1:-1, 1], s=26, color=C1, zorder=4, label="столкновение с ионом")
        ax.scatter(*p[0], s=70, color=C3, zorder=5)
        ax.scatter(*p[-1], s=70, color=C4, zorder=5)
        ax.set_aspect("equal")
        cx, cy = p.mean(axis=0)
        ax.set_xlim(cx - 10.0, cx + 10.0)
        ax.set_ylim(cy - 4.6, cy + 4.4)
        ax.axis("off")
        ax.set_title(title, fontsize=11.5)
        ax.annotate("начало", p[0], xytext=(p[0][0] - 1.6, p[0][1] + 1.6), fontsize=10, color=C3, arrowprops=dict(arrowstyle="-", color=C3, lw=0.8))
        ax.annotate("конец", p[-1], xytext=(p[-1][0] + 0.4, p[-1][1] + 1.6), fontsize=10, color=C4, arrowprops=dict(arrowstyle="-", color=C4, lw=0.8))
        if drift:
            arrow(ax, p[0], p[-1], C3, 2.2, ms=16, z=6)
            ax.text((p[0][0] + p[-1][0]) / 2, (p[0][1] + p[-1][1]) / 2 - 1.2, "$l$", fontsize=13, color=C3, ha="center")
            arrow(ax, (cx - 9.6, cy - 4.0), (cx - 7.4, cy - 4.0), C1, 2.0, ms=15)
            ax.text(cx - 8.5, cy - 3.5, r"$\vec F_{\mathrm{эл}}$", fontsize=12, color=C1, ha="center")
    axs[0].legend(loc="lower left", fontsize=9, frameon=False)
    f.tight_layout()
    save(f, "metal-random-vs-drift")


@fig("metal-drift-conductor")
def _():
    f, ax = canvas(8.2, 3.9, (-1.2, 9.6), (-1.7, 3.3))
    # the body has no outline of its own: two lines for the sides, and the far end drawn as an arc (the visible half solid, the hidden half dashed)
    ax.add_patch(Rectangle((0, 0), 8, 2.4, fc=SOFT, ec="none", lw=0, zorder=1))
    line(ax, [(0, 2.4), (8, 2.4)], INK, 1.4)
    line(ax, [(0, 0), (8, 0)], INK, 1.4)
    ax.add_patch(Ellipse((0, 1.2), 0.8, 2.4, fc=ALUM, ec=INK, lw=1.4, zorder=2))
    ax.add_patch(Arc((8, 1.2), 0.8, 2.4, theta1=-90, theta2=90, ec=INK, lw=1.4, zorder=2))
    ax.add_patch(Arc((8, 1.2), 0.8, 2.4, theta1=90, theta2=270, ec=INK, lw=1.4, zorder=2, ls=(0, (4, 3))))
    txt(ax, -0.85, 2.15, "$S$", 14)
    rng = np.random.default_rng(2)
    xs = [1.3, 2.6, 4.0, 5.3, 6.6, 3.9, 5.8, 1.6]
    ys = [1.7, 0.6, 1.5, 0.7, 1.4, 1.0, 1.9, 0.9]  # the last carrier is clear of the arrow of its neighbour
    for x, y in zip(xs, ys):
        ax.add_patch(Circle((x, y), 0.11, fc=C2, ec="none", zorder=5))
        arrow(ax, (x + 0.15, y), (x + 0.75, y), C2, 1.3, ms=9)
    txt(ax, 4.0, 2.75, "$N$ носителей заряда в объёме $V$, заряд каждого $q$", 11.5)
    dim_h(ax, 0, 8, -0.55, "$L$", 13)
    arrow(ax, (8.5, 1.2), (9.5, 1.2), C3, 2.2, ms=15)
    txt(ax, 9.0, 0.75, r"$\vec v$", 13, C3)
    txt(ax, 9.0, 1.65, "дрейф", 10, C3)
    save(f, "metal-drift-conductor")


@fig("metal-riecke-experiment")
def _():
    f, ax = canvas(10.0, 4.2, (-1.0, 12.0), (-2.7, 2.7))
    for x0, c, name in ((1.5, ALUM, "Al"), (3.5, COPPER, "Cu"), (5.5, ALUM, "Al")):
        ax.add_patch(Rectangle((x0, 0.2), 2.0, 1.6, fc=c, ec=INK, lw=1.4, zorder=3))
        txt(ax, x0 + 1.0, 1.0, name, 15)
    ax.add_patch(Rectangle((0.9, 0.0), 0.6, 2.0, fc=LIGHT, ec=INK, lw=1.2, zorder=3))
    ax.add_patch(Rectangle((7.5, 0.0), 0.6, 2.0, fc=LIGHT, ec=INK, lw=1.2, zorder=3))
    txt(ax, 4.5, -0.45, "зажим сжимает цилиндры", 10, GREY)
    # One loop: battery, rheostat in series with it, the clamp with the cylinders (the rheostat limits the current through them)
    line(ax, [(1.2, 0.0), (1.2, -1.4), (2.5, -1.4)])
    line(ax, [(2.8, -1.4), (4.7, -1.4)])
    line(ax, [(6.5, -1.4), (7.8, -1.4), (7.8, 0.0)])
    line(ax, [(2.5, -1.75), (2.5, -1.05)], lw=1.6)
    line(ax, [(2.8, -1.6), (2.8, -1.2)], lw=4.0)
    txt(ax, 2.15, -1.05, "$+$", 12, C1)
    txt(ax, 3.15, -1.05, "$-$", 12, C2)
    txt(ax, 2.65, -2.05, "батарея", 10, GREY)
    # rheostat
    ax.add_patch(Rectangle((4.7, -1.65), 1.8, 0.5, fc=PAPER, ec=INK, lw=1.4, zorder=4))
    arrow(ax, (5.0, -2.0), (6.1, -0.8), INK, 1.2, ms=9)
    txt(ax, 5.6, -2.3, "реостат", 10, GREY)
    # the current leaves the + of the battery, goes through the cylinders left to right and returns through the right wire
    arrow(ax, (7.8, -0.3), (7.8, -1.1), C1, 1.6, ms=12)
    txt(ax, 8.3, -0.7, "$I$", 12, C1)
    txt(ax, 9.9, 0.5, "$Q\\approx3{,}5\\cdot10^{6}$ Кл\nза один год", 10.5, INK, "left")
    save(f, "metal-riecke-experiment")


@fig("metal-inertia-ring")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.0, 4.6))
    # left: tube with balls
    ax = axs[0]
    ax.set_aspect("equal")
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-3.6, 3.4)
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 2.5, fc="none", ec=INK, lw=1.4))
    ax.add_patch(Circle((0, 0), 2.0, fc="none", ec=INK, lw=1.4))
    for a in np.deg2rad([20, 70, 130, 190, 250, 310]):
        r = 2.25
        ax.add_patch(Circle((r * np.cos(a), r * np.sin(a)), 0.16, fc=C5, ec=INK, lw=0.9, zorder=5))
        # velocity direction: counterclockwise
        d = np.array([-np.sin(a), np.cos(a)])
        p = np.array([r * np.cos(a), r * np.sin(a)])
        arrow(ax, p + 0.2 * d, p + 0.75 * d, C3, 1.5, ms=10)
    ax.add_patch(Rectangle((-0.35, 2.55), 0.7, 0.3, fc=LIGHT, ec=INK, lw=1.2, zorder=5))
    ax.add_patch(Rectangle((-0.35, -2.85), 0.7, 0.3, fc=LIGHT, ec=INK, lw=1.2, zorder=5))
    txt(ax, 0, 3.1, "тормоз", 10.5)
    txt(ax, 0, -3.15, "тормоз", 10.5)
    txt(ax, 0, 0, "трубка\nостановлена,\nшарики\nдвижутся\nпо инерции", 10.5, INK)
    ax.set_title("Трубка с шариками", fontsize=12)
    # right: ring with electrons and galvanometer
    ax = axs[1]
    ax.set_aspect("equal")
    ax.set_xlim(-3.4, 5.4)
    ax.set_ylim(-3.6, 3.4)
    ax.axis("off")
    th = np.linspace(np.deg2rad(20), np.deg2rad(340), 200)
    ax.plot(2.3 * np.cos(th), 2.3 * np.sin(th), color=INK, lw=2.0)
    for a in np.deg2rad([40, 90, 140, 190, 250, 300]):
        p = np.array([2.3 * np.cos(a), 2.3 * np.sin(a)])
        electron(ax, *p, 0.13)
        d = np.array([-np.sin(a), np.cos(a)])
        arrow(ax, p + 0.2 * d, p + 0.7 * d, C2, 1.5, ms=10)
    top = 2.3 * np.array([np.cos(np.deg2rad(20)), np.sin(np.deg2rad(20))])
    bot = 2.3 * np.array([np.cos(np.deg2rad(340)), np.sin(np.deg2rad(340))])
    line(ax, [tuple(top), (3.6, top[1]), (3.6, 0.6)])
    line(ax, [tuple(bot), (3.6, bot[1]), (3.6, -0.6)])
    ax.add_patch(Circle((3.6, 0), 0.6, fc=PAPER, ec=INK, lw=1.6, zorder=6))
    txt(ax, 3.6, 0, "Г", 14)
    txt(ax, 4.6, 0.0, "гальвано-\nметр", 10, GREY, "left")
    txt(ax, 0, 0, "кольцо\nостановлено,\nэлектроны\nдвижутся\nпо инерции", 10.5, INK)
    ax.set_title("Металлическое кольцо", fontsize=12)
    f.tight_layout()
    save(f, "metal-inertia-ring")


@fig("metal-tolman-stewart-setup")
def _():
    f, ax = canvas(8.6, 5.2, (-2.2, 8.2), (-1.0, 5.2))
    ax.add_patch(Rectangle((1.0, 1.2), 2.6, 2.2, fc=SOFT, ec=INK, lw=1.4, zorder=3))
    for y in np.linspace(1.5, 3.1, 6):
        line(ax, [(1.1, y), (3.5, y)], GREY, 0.9, z=4)
    ax.add_patch(Ellipse((2.3, 3.4), 2.6, 0.6, fc=PLATE, ec=INK, lw=1.4, zorder=4))
    ax.add_patch(Rectangle((0.7, 0.5), 3.2, 0.7, fc=LIGHT, ec=INK, lw=1.4, zorder=3))
    txt(ax, 2.3, 2.3, "катушка\nс проводом", 10.5, INK)
    ax.add_patch(Rectangle((-0.35, 0.4), 0.45, 0.9, fc=LIGHT, ec=INK, lw=1.3, zorder=3))
    ax.add_patch(Rectangle((4.5, 0.4), 0.45, 0.9, fc=LIGHT, ec=INK, lw=1.3, zorder=3))
    arrow(ax, (-0.1, 0.9), (0.7, 0.9), INK, 1.2, ms=9)
    arrow(ax, (4.5, 0.9), (3.9, 0.9), INK, 1.2, ms=9)
    txt(ax, -0.9, 0.35, "тормоз", 10.5)
    txt(ax, 5.55, 0.35, "тормоз", 10.5)
    # axle and sliding contacts
    line(ax, [(2.3, 3.4), (2.3, 4.5)])
    line(ax, [(2.3, 0.5), (2.3, -0.4)])
    line(ax, [(1.85, 4.5), (2.75, 4.5)], lw=3.0)
    line(ax, [(1.85, -0.4), (2.75, -0.4)], lw=3.0)
    txt(ax, 0.2, 4.7, "скользящий контакт", 10.5, INK, "left")
    line(ax, [(2.75, 4.5), (6.3, 4.5), (6.3, 3.2)])
    line(ax, [(2.75, -0.4), (6.3, -0.4), (6.3, 1.6)])
    ax.add_patch(Circle((6.3, 2.4), 0.8, fc=PAPER, ec=INK, lw=1.6, zorder=6))
    txt(ax, 6.3, 2.4, "Г", 15)
    arrow(ax, (5.3, 2.4), (5.3, 3.3), C1, 1.5, ms=10)
    txt(ax, 5.0, 3.35, "$I(t)$", 12, C1)
    ax.annotate("", xy=(0.8, 4.05), xytext=(3.8, 4.05), arrowprops=dict(arrowstyle="-|>", color=C3, lw=1.5, connectionstyle="arc3,rad=-0.25"))
    txt(ax, 3.9, 3.85, "вращение", 10, C3, "left")
    save(f, "metal-tolman-stewart-setup")


@fig("metal-tolman-stewart-current")
def _():
    f, ax = plt.subplots(figsize=(5.8, 3.6))
    t = np.linspace(0, 1, 300)
    y = t**0.3 * (1 - t) ** 1.3
    y = y / y.max()
    ax.plot(t, y, color=C1, lw=2.2)
    ax.set_xlim(-0.05, 1.12)
    ax.set_ylim(-0.12, 1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.annotate("", xy=(1.12, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.annotate("", xy=(0, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.text(1.1, -0.1, "$t$", fontsize=13, ha="center")
    ax.text(-0.04, 1.14, "$I$", fontsize=13, ha="center")
    ax.text(0.0, -0.1, "начало\nторможения", fontsize=10, ha="center", va="top", color=GREY)
    ax.text(1.0, -0.1, "остановка\nкатушки", fontsize=10, ha="center", va="top", color=GREY)
    ax.set_ylim(-0.4, 1.2)
    save(f, "metal-tolman-stewart-current")


# ---------------------------------------------------------------- metal: resistance and temperature

LAMP_U = np.array([2, 4, 6, 8, 10, 12])
LAMP_I = np.array([0.18, 0.24, 0.28, 0.33, 0.36, 0.40])
LAMP_R = np.array([11, 17, 21, 24, 28, 30])


def bare_axes(ax, xlabel, ylabel):
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.annotate("", xy=(1.03, 0), xycoords=("axes fraction", "data"), xytext=(0.0, 0), textcoords=("axes fraction", "data"), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.annotate("", xy=(0, 1.03), xycoords=("data", "axes fraction"), xytext=(0, 0.0), textcoords=("data", "axes fraction"), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(1.04, -0.06, xlabel, transform=ax.transAxes, fontsize=12, ha="left", va="center")
    ax.text(-0.02, 1.06, ylabel, transform=ax.transAxes, fontsize=12, ha="right", va="center")


@fig("metal-lamp-iv-curve")
def _():
    f, ax = plt.subplots(figsize=(6.4, 4.4))
    u = np.linspace(0, 12.6, 200)
    ax.plot(u, 0.18 * np.maximum(u / 2, 1e-9) ** 0.446, color=C2, lw=2.2, label="лампа накаливания")
    ax.plot([0, 12], [0, 0.40], color=GREY, lw=1.5, ls="--", label="прямая пропорциональность")
    ax.scatter(np.r_[0, LAMP_U], np.r_[0, LAMP_I], s=42, color=C1, zorder=5, label="измерения")
    for x, y in zip(LAMP_U, LAMP_I):
        ax.plot([x, x], [0, y], color=GRID, lw=0.9, zorder=1)
        ax.plot([0, x], [y, y], color=GRID, lw=0.9, zorder=1)
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 0.47)
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
    ax.set_yticks([0.1, 0.2, 0.3, 0.4])
    ax.grid(False)
    ax.set_xlabel("$U$, В")
    ax.set_ylabel("$I$, А")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_title("Вольт-амперная характеристика лампы")
    save(f, "metal-lamp-iv-curve")


@fig("metal-lamp-resistance")
def _():
    f, ax = plt.subplots(figsize=(6.4, 4.2))
    u = np.linspace(2, 12, 100)
    # the points are not joined by segments: a smooth curve is drawn near them (a cubic fit stands for the flexible ruler)
    ax.plot(u, np.polyval(np.polyfit(LAMP_U, LAMP_R, 3), u), color=C2, lw=1.6, zorder=2)
    ax.scatter(LAMP_U, LAMP_R, s=48, color=C1, zorder=5)
    for x, y in zip(LAMP_U, LAMP_R):
        ax.text(x, y + 1.3, f"{y}", ha="center", fontsize=10, color=INK)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 36)
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
    ax.set_xlabel("$U$, В")
    ax.set_ylabel("$R$, Ом")
    ax.set_title("Сопротивление нити растёт с напряжением")
    save(f, "metal-lamp-resistance")


@fig("metal-r-vs-kelvin")
def _():
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    t0, t1 = 273.0, 520.0
    r0 = 1.0
    k = r0 / t0
    tc = 30.0
    tt = np.linspace(tc, t1, 100)
    ax.plot(tt, k * tt, color=C1, lw=2.4)
    ax.plot([0, tc], [0, 0], color=C1, lw=2.4)
    ax.plot([tc, tc], [0, k * tc], color=C1, lw=2.4)
    ax.plot([0, tc], [0, k * tc], color=GREY, lw=1.4, ls="--")
    ax.plot([t0, t0], [0, r0], color=GREY, lw=1.0, ls="--")
    ax.plot([0, t0], [r0, r0], color=GREY, lw=1.0, ls="--")
    ax.set_xlim(0, t1 + 40)
    ax.set_ylim(0, 2.0)
    ax.set_xticks([0, 273])
    ax.set_xticklabels(["0", "273"])
    ax.set_yticks([r0])
    ax.set_yticklabels(["$R_0$"])
    ax.annotate("сверхпроводимость:\n$R=0$", xy=(tc / 2, 0.0), xytext=(105, 0.05), fontsize=10, color=C1, va="bottom", ha="left", arrowprops=dict(arrowstyle="-", color=C1, lw=0.9))
    ax.text(410, 1.78, "$R=R_0(1+\\alpha t)$", fontsize=12, color=C1, ha="center")
    ax.text(t0 + 8, 0.06, "$0\\,^\\circ$C", fontsize=10, color=GREY)
    ax.set_xlabel("$T$, К")
    ax.set_ylabel("$R$")
    ax.set_title("Сопротивление металла и температура")
    save(f, "metal-r-vs-kelvin")


@fig("metal-tks-comparison")
def _():
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    t = np.linspace(0, 200, 100)
    data = [
        ("железо", 6.2e-3, C4),
        ("вольфрам", 4.8e-3, C1),
        ("медь", 4.3e-3, COPPER),
        ("нихром", 0.4e-3, C2),
        ("константан", 0.02e-3, C3),
    ]
    for (name, a, c), dy in zip(data, (0.0, 0.0, -0.07, 0.0, 0.0)):
        ax.plot(t, 1 + a * t, color=c, lw=2.0)
        ax.text(203, 1 + a * 200 + dy, name, color=c, fontsize=10.5, va="center")
    ax.set_xlim(0, 260)
    ax.set_ylim(0.9, 2.4)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("$R/R_0$")
    ax.set_title("Относительное сопротивление разных материалов")
    save(f, "metal-tks-comparison")


@fig("metal-filament-thin-spot")
def _():
    f, ax = canvas(9.0, 3.2, (-0.4, 10.4), (-1.6, 1.9))
    x = np.linspace(0, 10, 300)
    half = 0.55 - 0.32 * np.exp(-((x - 5.0) / 0.9) ** 2)
    ax.fill_between(x, -half, half, color=tint(COPPER, 0.5), ec=INK, lw=1.4, zorder=3)
    hot = np.exp(-((x - 5.0) / 0.9) ** 2)
    for i in range(len(x) - 1):
        ax.fill_between(x[i : i + 2], -half[i : i + 2], half[i : i + 2], color=tuple(np.array(to_rgb(tint(WARM, 0.6))) * (1 - hot[i]) + np.array(to_rgb(RED)) * hot[i]), lw=0, zorder=4)
    line(ax, [(x[0], half[0]), *zip(x, half), (x[-1], half[-1])], INK, 1.4, z=5)
    line(ax, [(x[0], -half[0]), *zip(x, -half), (x[-1], -half[-1])], INK, 1.4, z=5)
    arrow(ax, (1.0, 1.3), (2.6, 1.3), C1, 1.6, ms=11)
    txt(ax, 1.8, 1.65, "$I$ один и тот же", 10.5, C1)
    arrow(ax, (5.0, -0.95), (5.0, -0.45), INK, 1.2, ms=9)
    txt(ax, 5.0, -1.25, "испарилось больше вольфрама: нить тоньше, $R$ больше", 10.5)
    txt(ax, 8.6, 0.95, "толстая часть:\n$R$ мало, нить холоднее", 10, GREY)
    save(f, "metal-filament-thin-spot")


@fig("metal-levitation")
def _():
    f, ax = canvas(6.2, 4.4, (-3.2, 3.2), (-1.5, 3.4))
    # the vessel with liquid nitrogen: the level is above the lower face of the ceramic, the ceramic lies under the surface
    ax.add_patch(Polygon([(-2.6, 0.3), (2.6, 0.3), (2.2, -1.3), (-2.2, -1.3)], fc=SOFT, ec=INK, lw=1.4, zorder=2))
    ax.add_patch(Polygon([(-2.525, 0.0), (2.525, 0.0), (2.2, -1.3), (-2.2, -1.3)], fc=tint(SKY, 0.7), ec="none", zorder=3))
    line(ax, [(-2.525, 0.0), (2.525, 0.0)], C2, 1.2)
    ax.add_patch(Rectangle((-1.5, -0.6), 3.0, 0.5, fc=tint(INK, 0.3), ec=INK, lw=1.4, zorder=4))
    txt(ax, 0, -0.35, "сверхпроводящая керамика", 9.5, PAPER)
    txt(ax, 0, -1.0, "жидкий азот, 77 К", 10.5, C2)
    # the magnet: the north half blue, the south half red (course convention)
    ax.add_patch(Rectangle((-0.7, 0.9), 1.4, 0.55, fc=tint(RED, 0.65), ec=INK, lw=1.4, zorder=4))
    ax.add_patch(Rectangle((-0.7, 0.9), 0.7, 0.55, fc=tint(BLUE, 0.6), ec=INK, lw=1.4, zorder=5))
    txt(ax, -0.35, 1.18, "N", 11, INK)
    txt(ax, 0.35, 1.18, "S", 11, INK)
    arrow(ax, (0, 0.8), (0, 0.1), C1, 1.6, "<|-|>", 11)
    txt(ax, 0.55, 0.5, "воздух", 10.5, GREY, "left")
    txt(ax, -2.2, 2.4, "неодимовый магнит парит:\nсверхпроводящие токи в керамике\nвыталкивают поле магнита", 10.5, INK, "left")
    save(f, "metal-levitation")


# ---------------------------------------------------------------- metal: laboratory work


@fig("metal-tks-lab-setup")
def _():
    f, ax = canvas(10.4, 5.2, (-2.6, 10.4), (-1.0, 5.6))
    ax.add_patch(FancyBboxPatch((0.4, 0.0), 3.6, 3.4, boxstyle="round,pad=0.02,rounding_size=0.25", fc=WATER, ec=INK, lw=1.5, zorder=2))
    txt(ax, 2.2, -0.45, "кипяток, 100 °C", 10.5, C2)
    for bx, by in ((0.9, 0.9), (1.2, 1.7), (3.6, 1.1), (3.0, 0.5), (0.8, 2.6)):
        bubble(ax, bx, by)
    ax.add_patch(FancyBboxPatch((1.7, 0.7), 0.9, 3.7, boxstyle="round,pad=0.0,rounding_size=0.4", fc=SOFT, ec=INK, lw=1.3, zorder=4))
    for y in np.linspace(0.95, 2.2, 6):
        line(ax, [(1.8, y), (2.5, y + 0.05)], COPPER, 2.0, z=5)
    txt(ax, 1.4, 4.1, "пробирка с катушкой\nиз медного провода", 10, INK, "right")
    # thermometer
    ax.add_patch(Rectangle((3.3, 1.0), 0.14, 3.6, fc=PAPER, ec=INK, lw=1.2, zorder=5))
    ax.add_patch(Rectangle((3.3, 1.0), 0.14, 2.6, fc=C1, ec="none", zorder=6))
    txt(ax, 3.7, 4.1, "термометр", 10, INK, "left")
    # multimeter
    ax.add_patch(FancyBboxPatch((6.3, 0.9), 3.0, 2.6, boxstyle="round,pad=0.02,rounding_size=0.2", fc=PINK, ec=INK, lw=1.5, zorder=3))
    ax.add_patch(Rectangle((6.6, 2.4), 2.4, 0.8, fc=tint(GREEN, 0.85), ec=INK, lw=1.2, zorder=4))
    txt(ax, 7.7, 2.8, "105,1", 14, INK)  # the coil is in boiling water, 100 degrees: the hot value, not the room one
    txt(ax, 8.75, 2.6, "Ω", 10, INK)
    ax.add_patch(Circle((7.8, 1.55), 0.5, fc=DARK, ec=INK, lw=1.2, zorder=4))
    txt(ax, 7.8, 0.5, "цифровой омметр", 10.5, INK)
    line(ax, [(1.95, 4.4), (1.95, 5.2), (6.9, 5.2), (6.9, 3.5)], C1, 1.4)
    line(ax, [(2.4, 4.3), (2.4, 4.85), (7.5, 4.85), (7.5, 3.5)], INK, 1.4)
    save(f, "metal-tks-lab-setup")


@fig("metal-tks-lab-points")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.4, 4.2))
    for ax, name, (t1, r1), (t2, r2), c, ylim in (
        (axs[0], "Медь", (21, 81.6), (100, 105.0), COPPER, (0, 125)),
        (axs[1], "Вольфрам", (21, 24.6), (90, 30.5), C1, (0, 40)),
    ):
        k = (r2 - r1) / (t2 - t1)
        r0 = r1 - k * t1
        tt = np.linspace(0, 115, 50)
        ax.plot(tt, r0 + k * tt, color=c, lw=1.8)
        ax.scatter([t1, t2], [r1, r2], s=55, color=INK, zorder=5)
        ax.scatter([0], [r0], s=45, facecolors=PAPER, edgecolors=c, lw=1.6, zorder=5)
        ax.annotate(f"$({num(t1, '', math=True)},\\ {num(r1, '', math=True)})$", (t1, r1), xytext=(t1 + 4, r1 - ylim[1] * 0.14), fontsize=10)
        ax.annotate(f"$({num(t2, '', math=True)},\\ {num(r2, None, math=True)})$", (t2, r2), xytext=(t2 - 42, r2 + ylim[1] * 0.06), fontsize=10)
        ax.text(3, r0 + ylim[1] * 0.16, f"$R_0\\approx{num(r0, 1, math=True)}$ Ом", fontsize=10, color=c)
        ax.set_xlim(0, 120)
        ax.set_ylim(*ylim)
        ax.set_xlabel("$t$, °C")
        ax.set_ylabel("$R$, Ом")
        ax.set_title(f"{name}: две измеренные точки")
    f.tight_layout()
    save(f, "metal-tks-lab-points")


# ---------------------------------------------------------------- tikz circuits

PREAMBLE = (
    r"""
\documentclass[border=6pt]{standalone}
\usepackage[T2A]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[russian]{babel}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc}
"""
    + COLOUR_DEFS
    + r"""\tikzset{every picture/.style={line width=0.9pt,line cap=round,line join=round,color=ink}}
\tikzset{cp/.style={font=\small,align=center}}
% lamp: x y
\newcommand{\lampc}[2]{\begin{scope}[shift={(#1,#2)}]
\draw(-.7,0)--(-.35,0)(.35,0)--(.7,0)(0,0)circle(.35)(-.25,-.25)--(.25,.25)(-.25,.25)--(.25,-.25);
\end{scope}}
% meter: x y label
\newcommand{\meterc}[3]{\begin{scope}[shift={(#1,#2)}]
\draw(-.7,0)--(-.4,0)(.4,0)--(.7,0)(0,0)circle(.4);\node[font=\small] at(0,0){#3};
\end{scope}}
% rheostat: x y
\newcommand{\rheoc}[2]{\begin{scope}[shift={(#1,#2)}]
\draw(-.9,0)--(-.55,0)(.55,0)--(.9,0)(-.55,-.16)rectangle(.55,.16);
\draw[-{Stealth[length=2mm]}](-.25,.62)--(-.05,.2);\draw(-.25,.62)--(.25,.62)--(.25,.2);
\end{scope}}
% current source box
\newcommand{\itbox}[2]{\begin{scope}[shift={(#1,#2)}]
\draw(-.5,-.55)rectangle(.5,.55);\node[font=\small]at(0,0){ИТ};
\end{scope}}
% junction dot
\newcommand{\dotc}[2]{\fill(#1,#2)circle(.06);}
\newcommand{\ca}[4]{\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](#1,#2)--(#3,#4);}
\newcommand{\sgn}[3]{\node[font=\small]at(#1,#2){#3};}
% electrolytic bath: x y  (electrodes at x-.8 and x+.8)
\newcommand{\bath}[2]{\begin{scope}[shift={(#1,#2)}]
\fill[soln](-1.5,-1.4)rectangle(1.5,.9);
\draw(-1.5,.9)--(-1.5,-1.4)--(1.5,-1.4)--(1.5,.9);
\draw[line width=2.2pt](-.8,1.4)--(-.8,-.9);\draw[line width=2.2pt](.8,1.4)--(.8,-.9);
\draw[dashed,grey](-1.6,.9)--(1.6,.9);
\end{scope}}
"""
)

TIKZ = {}


def tikz(name):
    def deco(fn):
        TIKZ[name] = fn
        FIGS[name] = lambda n=name, fn=fn: build_tikz(n, fn())
        return fn

    return deco


def build_tikz(name, body):
    tex = PREAMBLE + "\\begin{document}\n\\begin{tikzpicture}\n" + body + "\\end{tikzpicture}\n\\end{document}\n"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "f.tex").write_text(tex, encoding="utf-8")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "f.tex"], cwd=tmp, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            print(r.stdout[-2500:])
            raise SystemExit(f"pdflatex failed for {name}")
        subprocess.run(["pdftoppm", "-png", "-r", "200", "-singlefile", "f.pdf", "f"], cwd=tmp, check=True)
        (OUT / f"{name}.png").write_bytes((tmp / "f.png").read_bytes())
    print("wrote", name)


@tikz("metal-lamp-circuit")
def _():
    return r"""
\itbox{0}{1.6}
\draw(0,2.15)--(0,3.2)--(1.4,3.2)(3.2,3.2)--(4.4,3.2)(5.8,3.2)--(8,3.2)--(8,0)--(7.1,0)(5.7,0)--(0,0)--(0,1.05);
\rheoc{2.3}{3.2}\meterc{5.1}{3.2}{mA}\lampc{6.4}{0}\meterc{6.4}{1.5}{V}
\draw(5.5,0)--(5.5,1.5)--(5.7,1.5)(7.1,1.5)--(7.3,1.5)--(7.3,0);
\dotc{5.5}{0}\dotc{7.3}{0}
\node[cp]at(2.3,4.35){реостат};\node[cp]at(5.1,4.0){миллиамперметр};
\node[cp]at(6.4,-.7){лампа накаливания};\node[cp]at(6.4,2.25){вольтметр};
\node[cp]at(-1.55,1.6){источник\\тока};
"""


# ---------------------------------------------------------------- electrolysis: helpers

NA_C = BLUE
CL_C = GREEN
CU_C = COPPER


def vessel(ax, x0, y0, x1, y1, level, fill=SOLUTION, lw=2.0):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, level - y0, fc=fill, ec="none", zorder=1))
    line(ax, [(x0, y1), (x0, y0), (x1, y0), (x1, y1)], INK, lw, z=6)
    line(ax, [(x0, level), (x1, level)], BLUE, 1.0, ls="--", z=2)


def rod(ax, x, y0, y1, w=0.32, fc=DARK):
    ax.add_patch(Rectangle((x - w / 2, y0), w, y1 - y0, fc=fc, ec=INK, lw=1.2, zorder=4))


def labeled_ion(ax, x, y, kind, r=None):
    table = {
        "Na": ("Na$^+$", NA_C, NEG_FILL, 0.30),
        "Cl": ("Cl$^-$", CL_C, tint(GREEN, 0.85), 0.34),
        "Cu": ("Cu$^{2+}$", CU_C, tint(COPPER, 0.7), 0.36),
        "Ni": ("Ni$^{2+}$", GREY, tint(INK, 0.9), 0.36),
        "H": ("H$^+$", C1, POS_FILL, 0.28),
    }
    s, c, fc, rr = table[kind]
    rr = r or rr
    ax.add_patch(Circle((x, y), rr, fc=fc, ec=c, lw=1.3, zorder=5))
    txt(ax, x, y, s, 8.5, c)


def water(ax, x, y, o_dir):
    d = np.array([np.cos(o_dir), np.sin(o_dir)])
    n = np.array([-d[1], d[0]])
    c = np.array([x, y])
    o = c + 0.09 * d
    for s in (-1, 1):
        h = c - 0.11 * d + s * 0.13 * n
        line(ax, [tuple(o), tuple(h)], GREY, 0.9, z=4)
        ax.add_patch(Circle(tuple(h), 0.05, fc=PAPER, ec=GREY, lw=0.8, zorder=5))
    ax.add_patch(Circle(tuple(o), 0.09, fc=tint(RED, 0.65), ec=C1, lw=0.8, zorder=5))


def plus_minus(ax, x, y, sign, size=15):
    txt(ax, x, y, sign, size, C1 if "+" in sign else C2, weight="bold")


# ---------------------------------------------------------------- electrolysis: conduction and dissociation


@fig("electrolysis-conductivity-experiment")
def _():
    f, ax = canvas(11.0, 5.4, (-1.7, 12.7), (-1.5, 5.6))
    cases = [
        (0.0, "кристаллы NaCl", False, "crystal"),
        (5.4, "чистая вода", False, "water"),
        (10.8, "раствор NaCl в воде", True, "solution"),
    ]
    for cx, title, on, kind in cases:
        x0, x1 = cx - 1.4, cx + 1.4
        if kind != "crystal":
            vessel(ax, x0, 0.0, x1, 2.6, 1.9)
        else:
            vessel(ax, x0, 0.0, x1, 2.6, 0.0)
            rng = np.random.default_rng(4)
            for _ in range(26):
                ax.add_patch(Rectangle((rng.uniform(x0 + 0.1, x1 - 0.35), rng.uniform(0.05, 0.65)), 0.22, 0.22, fc=PAPER, ec=GREY, lw=0.9, zorder=3))
        rod(ax, cx - 0.65, 0.35, 2.9)
        rod(ax, cx + 0.65, 0.35, 2.9)
        line(ax, [(cx - 0.65, 2.9), (cx - 0.65, 3.55)], INK, 1.6)
        line(ax, [(cx + 0.65, 2.9), (cx + 0.65, 4.7)], INK, 1.6)
        line(ax, [(cx - 0.65, 4.15), (cx - 0.65, 4.7)], INK, 1.6)
        ax.add_patch(Circle((cx - 0.65, 3.85), 0.3, fc=tint(WARM, 0.3) if on else PAPER, ec=INK, lw=1.5, zorder=6))
        line(ax, [(cx - 0.65 - 0.2, 3.65), (cx - 0.65 + 0.2, 4.05)], INK, 1.2, z=7)
        line(ax, [(cx - 0.65 - 0.2, 4.05), (cx - 0.65 + 0.2, 3.65)], INK, 1.2, z=7)
        if on:
            for a in np.deg2rad(np.arange(0, 360, 45)):
                line(ax, [(cx - 0.65 + 0.42 * np.cos(a), 3.85 + 0.42 * np.sin(a)), (cx - 0.65 + 0.62 * np.cos(a), 3.85 + 0.62 * np.sin(a))], C5, 1.5, z=7)
        plus_minus(ax, cx - 0.65, 5.05, "$+$", 13)
        plus_minus(ax, cx + 0.65, 5.05, "$-$", 13)
        txt(ax, cx, -0.5, title, 11.5, INK)
        txt(ax, cx, -1.05, "ток течёт" if on else "тока нет", 10.5, C3 if on else C1)
    save(f, "electrolysis-conductivity-experiment")


@fig("electrolysis-dissociation")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.6, 4.6))
    ax = axs[0]
    ax.set_aspect("equal")
    ax.set_xlim(-0.6, 5.4)
    ax.set_ylim(-0.8, 5.2)
    ax.axis("off")
    for i in range(5):
        for j in range(5):
            if (i + j) % 2 == 0:
                labeled_ion(ax, i, j, "Na", 0.33)
            else:
                labeled_ion(ax, i, j, "Cl", 0.37)
    ax.set_title("Кристалл: ионы вморожены в решётку", fontsize=11.5)
    ax = axs[1]
    ax.set_aspect("equal")
    ax.set_xlim(-0.6, 8.4)
    ax.set_ylim(-0.8, 5.6)
    ax.axis("off")
    ax.add_patch(Rectangle((-0.5, -0.6), 8.8, 6.0, fc=SOLUTION, ec="none", zorder=0))
    rng = np.random.default_rng(7)
    ions = [("Na", 1.6, 4.0), ("Cl", 4.2, 4.3), ("Na", 6.6, 3.4), ("Cl", 2.0, 1.4), ("Na", 4.6, 1.5), ("Cl", 6.9, 0.8)]
    for kind, x, y in ions:
        labeled_ion(ax, x, y, kind, 0.33 if kind == "Na" else 0.37)
        rr = 0.85 if kind == "Na" else 0.95
        for a in np.deg2rad([20, 110, 200, 290]):
            px, py = x + rr * np.cos(a), y + rr * np.sin(a)
            toward = a + np.pi
            water(ax, px, py, toward if kind == "Na" else a)
    ax.set_title("Раствор: вода разделяет ионы", fontsize=11.5)
    f.tight_layout()
    save(f, "electrolysis-dissociation")


@fig("electrolysis-cell-ions")
def _():
    f, ax = canvas(9.4, 6.4, (-1.4, 10.2), (-1.2, 6.8))
    vessel(ax, 0.0, 0.0, 9.0, 5.0, 4.2)
    rod(ax, 1.2, 0.4, 5.6)
    rod(ax, 7.8, 0.4, 5.6)
    txt(ax, 1.2, -0.5, "анод", 11.5, C1)
    txt(ax, 7.8, -0.5, "катод", 11.5, C2)
    for i in range(6):
        y = 0.9 + i * 0.55
        txt(ax, 1.42, y, "+", 9, C1)
        txt(ax, 7.58, y, "-", 10, C2)
    for x, y in ((3.0, 3.4), (4.0, 1.4), (5.0, 2.4), (2.4, 1.0)):  # no ion overlaps the Cl- at (5.6; 3.0)
        labeled_ion(ax, x, y, "Na")
        arrow(ax, (x + 0.4, y), (x + 1.3, y), NA_C, 1.6, ms=11)
    for x, y in ((3.4, 2.1), (5.6, 3.0), (6.2, 1.0), (4.6, 0.5)):
        labeled_ion(ax, x, y, "Cl")
        arrow(ax, (x - 0.45, y), (x - 1.35, y), CL_C, 1.6, ms=11)
    for x, y in ((0.75, 4.5), (0.95, 5.0), (0.55, 4.9)):
        bubble(ax, x, y, 0.09)
    for x, y in ((8.25, 4.5), (8.45, 5.0), (8.05, 4.9)):
        bubble(ax, x, y, 0.09)
    txt(ax, 0.1, 5.75, r"$\mathrm{Cl_2}$", 11, CL_C)
    txt(ax, 8.9, 5.75, r"$\mathrm{H_2}$", 11, C2)
    # circuit
    line(ax, [(1.2, 5.6), (1.2, 6.3), (3.8, 6.3)], INK, 1.8)
    line(ax, [(5.2, 6.3), (7.8, 6.3), (7.8, 5.6)], INK, 1.8)
    line(ax, [(3.8, 5.9), (3.8, 6.7)], INK, 1.6)
    line(ax, [(4.2, 6.05), (4.2, 6.55)], INK, 4.0)
    line(ax, [(4.2, 6.3), (5.2, 6.3)], INK, 1.8)
    plus_minus(ax, 0.75, 6.1, "$+$", 13)
    plus_minus(ax, 8.25, 6.1, "$-$", 13)
    txt(ax, 4.5, -0.5, "раствор NaCl", 11, INK)
    arrow(ax, (2.2, 3.95), (6.8, 3.95), GREY, 1.6, ms=13)
    txt(ax, 4.5, 3.7, r"$\vec E$", 13, GREY)
    save(f, "electrolysis-cell-ions")


@tikz("electrolysis-bath-circuit")
def _():
    return r"""
\bath{3}{0}
\draw(2.2,1.4)--(2.2,2.2)--(0.2,2.2)--(0.2,3.4)--(1.3,3.4);
\draw(1.3,3.05)--(1.3,3.75);\draw[line width=2.4pt](1.7,3.2)--(1.7,3.6);
\draw(1.7,3.4)--(2.9,3.4)--(3.5,3.4)(4.9,3.4)--(5.8,3.4)--(5.8,2.2)--(3.8,2.2)--(3.8,1.4);
\lampc{4.2}{3.4}
\sgn{1.05}{3.85}{$+$}\sgn{1.95}{3.85}{$-$}
\sgn{1.9}{1.7}{$+$}\sgn{4.1}{1.7}{$-$}
\node[cp]at(1.5,4.5){источник тока};\node[cp]at(4.2,4.3){лампа};
\node[cp,anchor=east]at(1.4,0.2){анод};\node[cp,anchor=west]at(4.6,0.2){катод};
\node[cp]at(3,-2.0){электролитическая ванна};
\ca{-0.35}{3.0}{-0.35}{2.4}
"""


# ---------------------------------------------------------------- electrolysis: Faraday law


@fig("electrolysis-faraday-graph")
def _():
    f, ax = plt.subplots(figsize=(6.8, 4.6))
    q = np.linspace(0, 1000, 50)
    data = [("серебро", 1.12, C1), ("медь", 0.33, COPPER), ("никель", 0.30, C4), ("натрий", 0.24, C2), ("алюминий", 0.09, C3)]
    ends = {}
    for name, k, c in data:
        ax.plot(q, k * q, color=c, lw=2.0)
        ends[name] = (k * 1000, c)
    ys = {"серебро": 1120, "медь": 355, "никель": 285, "натрий": 215, "алюминий": 90}
    for name, k, c in data:
        ax.text(1015, ys[name], f"{name}, ${num(k, '', math=True)}$ мг/Кл", color=c, fontsize=10, va="center")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1250)
    ax.set_xlabel("$q$, Кл")
    ax.set_ylabel("$m$, мг")
    ax.set_title("Масса на электроде пропорциональна заряду")
    f.subplots_adjust(right=0.68)
    save(f, "electrolysis-faraday-graph")


@fig("electrolysis-k-table")
def _():
    f, ax = plt.subplots(figsize=(7.2, 4.2))
    names = ["Ag$^+$", "Cl$^-$", "Zn$^{2+}$", "Cu$^{2+}$", "Ni$^{2+}$", "Na$^+$", "Cr$^{3+}$", "Al$^{3+}$", "O$^{2-}$", "H$^+$"]
    vals = [1.12, 0.37, 0.34, 0.33, 0.30, 0.24, 0.18, 0.09, 0.08, 0.01]
    cols = [C1 if n.startswith("Ag") else C2 if n.startswith("Na") else METAL for n in names]
    ax.bar(range(len(vals)), vals, color=cols, ec=INK, lw=0.8)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, num(v, 2), ha="center", fontsize=9.5)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(names)
    ax.set_ylabel("$k$, мг/Кл")
    ax.set_ylim(0, 1.3)
    ax.set_title("Электрохимические эквиваленты")
    save(f, "electrolysis-k-table")


# ---------------------------------------------------------------- electrolysis: applications


@fig("electrolysis-aluminium-cell")
def _():
    f, ax = canvas(8.0, 5.6, (-0.8, 9.6), (-1.2, 6.3))
    ax.add_patch(Rectangle((0, 0), 8, 3.4, fc=tint(COPPER, 0.75), ec="none", zorder=1))
    line(ax, [(0, 4.4), (0, 0), (8, 0), (8, 4.4)], INK, 2.4, z=6)
    ax.add_patch(Rectangle((0.15, 0.15), 7.7, 0.55, fc=PLATE, ec=INK, lw=1.0, zorder=3))
    txt(ax, 4.0, 0.42, "жидкий алюминий на катоде", 10.5, INK)
    rod(ax, 1.4, 1.1, 4.8, 0.7, DARK)
    rod(ax, 6.6, 1.1, 4.8, 0.7, DARK)
    txt(ax, 1.4, 5.0, "анод", 11.5, C1)
    txt(ax, 6.6, 5.0, "анод", 11.5, C1)
    line(ax, [(1.4, 4.8), (1.4, 5.5), (6.6, 5.5), (6.6, 4.8)], INK, 1.6)
    plus_minus(ax, 4.0, 5.8, "$+$", 14)
    txt(ax, 4.0, 2.4, "расплав криолита Na$_3$AlF$_6$\nс растворённым Al$_2$O$_3$", 11, INK)
    line(ax, [(8.0, 0.4), (8.9, 0.4), (8.9, 3.0)], INK, 1.8)
    plus_minus(ax, 8.9, 3.4, "$-$", 14)
    txt(ax, 8.9, 3.95, "катод", 11.5, C2)
    txt(ax, 4.0, -0.6, "$\\mathrm{Al}^{3+}$ идут к катоду и осаждаются алюминием", 10.5, GREY)
    save(f, "electrolysis-aluminium-cell")


def utube_outline(ax, cx, r_out, r_in, y_arm, color=INK, lw=2.0):
    th = np.linspace(np.pi, 2 * np.pi, 60)
    xo, yo = cx + r_out * np.cos(th), 1.8 + r_out * np.sin(th)
    xi, yi = cx + r_in * np.cos(th), 1.8 + r_in * np.sin(th)
    ax.plot(np.r_[cx - r_out, xo, cx + r_out], np.r_[y_arm, yo, y_arm], color=color, lw=lw, zorder=6)
    ax.plot(np.r_[cx - r_in, xi, cx + r_in], np.r_[y_arm, yi, y_arm], color=color, lw=lw, zorder=6)


@fig("electrolysis-gas-cell")
def _():
    f, ax = canvas(6.4, 6.6, (-1.0, 6.6), (-1.4, 7.6))
    cx, ro, ri = 2.5, 1.7, 0.7
    ya, yt = 1.8, 6.0
    # liquid
    th = np.linspace(np.pi, 2 * np.pi, 60)
    outer = list(zip(cx + ro * np.cos(th), ya + ro * np.sin(th)))
    inner = list(zip(cx + ri * np.cos(th[::-1]), ya + ri * np.sin(th[::-1])))
    left_top, right_top = 4.8, 3.6
    poly = [(cx - ro, left_top)] + outer + [(cx + ro, right_top), (cx + ri, right_top), (cx + ri, ya)] + inner + [(cx - ri, ya), (cx - ri, left_top)]
    ax.add_patch(Polygon(poly, fc=SOLUTION, ec="none", zorder=1))
    utube_outline(ax, cx, ro, ri, yt)
    # gases
    ax.add_patch(Rectangle((cx - ro, left_top), ro - ri, yt - left_top, fc=tint(WARM, 0.8), ec="none", zorder=1))
    ax.add_patch(Rectangle((cx + ri, right_top), ro - ri, yt - right_top, fc=tint(GREEN, 0.85), ec="none", zorder=1))
    # electrodes and stoppers
    rod(ax, cx - 1.2, 1.3, 7.0, 0.12)
    rod(ax, cx + 1.2, 1.3, 7.0, 0.12)
    for xx in (cx - 1.2, cx + 1.2):
        ax.add_patch(Rectangle((xx - 0.42, yt), 0.84, 0.35, fc=LIGHT, ec=INK, lw=1.2, zorder=7))
    for xx, sg in ((cx - 1.2 - 0.55, -1), (cx + 1.2 + 0.55, 1)):
        ax.add_patch(Rectangle((xx - 0.13 if sg < 0 else xx - 0.05, 5.55), 0.18, 0.28, fc=LIGHT, ec=INK, lw=1.0, zorder=7))
    plus_minus(ax, cx - 1.2, 7.4, "$+$", 14)
    plus_minus(ax, cx + 1.2, 7.4, "$-$", 14)
    txt(ax, cx - 1.2 - 0.9, 5.4, "$\\mathrm{O_2}$", 12, INK, "right")
    txt(ax, cx + 1.2 + 0.9, 4.8, "$\\mathrm{2H_2}$", 12, INK, "left")
    txt(ax, cx, -0.55, "раствор $\\mathrm{H_2SO_4}$", 11, INK)
    txt(ax, cx, -1.1, "электролизёр", 11, GREY)
    save(f, "electrolysis-gas-cell")


@fig("electrolysis-copper-refining")
def _():
    f, ax = canvas(9.4, 5.6, (-1.0, 10.6), (-1.2, 6.2))
    vessel(ax, 0.0, 0.0, 9.0, 5.0, 4.2)
    # impure copper blank with jagged edge
    blank = [(1.2, 0.5), (1.9, 0.4), (2.5, 0.7), (2.4, 1.6), (2.7, 2.3), (2.3, 3.2), (2.6, 3.8), (1.5, 4.0), (1.2, 3.2), (1.5, 2.4), (1.1, 1.5)]
    ax.add_patch(Polygon(blank, fc=CU_C, ec=INK, lw=1.4, zorder=4))
    line(ax, [(1.9, 4.0), (1.9, 5.7)], INK, 1.8)
    # thin plate of pure copper (pale) and the new layer on its side that faces the anode
    ax.add_patch(Rectangle((7.5, 0.5), 0.14, 3.7, fc=tint(COPPER, 0.5), ec=INK, lw=1.0, zorder=4))
    ax.add_patch(Rectangle((7.2, 0.5), 0.3, 3.7, fc=CU_C, ec=INK, lw=1.0, zorder=4))
    line(ax, [(7.57, 4.2), (7.57, 5.7)], INK, 1.8)
    for x, y in ((3.9, 3.2), (4.6, 1.6), (5.4, 2.8), (6.2, 1.2)):
        labeled_ion(ax, x, y, "Cu")
        arrow(ax, (x + 0.45, y), (x + 1.05, y), CU_C, 1.6, ms=11)
    plus_minus(ax, 1.5, 5.9, "$+$", 14)
    plus_minus(ax, 7.9, 5.9, "$-$", 14)
    txt(ax, 1.9, -0.55, "медь, выплавленная из руды", 10.5, INK)
    txt(ax, 7.6, -0.55, "пластинка чистой меди", 10.5, INK)
    txt(ax, 4.5, -1.05, "раствор $\\mathrm{CuSO_4}$", 10.5, GREY)
    txt(ax, 2.5, 4.65, "переходит в раствор", 9.5, CU_C, "left")
    txt(ax, 7.2, 5.25, "оседает чистая медь", 9.5, CU_C, "right")
    save(f, "electrolysis-copper-refining")


@fig("electrolysis-electroplating")
def _():
    f, ax = canvas(9.6, 6.3, (-1.0, 10.6), (-1.6, 7.2))
    vessel(ax, 0.0, 0.0, 9.6, 5.0, 4.2)
    for x in (1.1, 8.5):
        ax.add_patch(Rectangle((x - 0.17, 0.5), 0.34, 4.5, fc=tint(INK, 0.7), ec=INK, lw=1.2, zorder=4))
    txt(ax, 1.1, -0.5, "Ni", 11.5, INK)
    txt(ax, 8.5, -0.5, "Ni", 11.5, INK)
    # the bus of the anodes goes over the lead of the spoon, so that the two do not cross
    line(ax, [(1.1, 5.0), (1.1, 6.6), (8.5, 6.6), (8.5, 5.0)], INK, 1.8)
    plus_minus(ax, 2.6, 6.95, "$+$", 14)
    # spoon
    ax.add_patch(Ellipse((4.8, 1.3), 0.95, 1.5, fc=PLATE, ec=INK, lw=2.4, zorder=4))
    ax.add_patch(Rectangle((4.72, 1.9), 0.16, 2.9, fc=PLATE, ec=INK, lw=1.4, zorder=4))
    line(ax, [(4.8, 4.8), (4.8, 5.8), (6.0, 5.8)], INK, 1.8)
    plus_minus(ax, 6.3, 5.8, "$-$", 14)
    for x, y in ((2.2, 3.2), (2.4, 1.4), (7.4, 3.0), (7.2, 1.5)):
        labeled_ion(ax, x, y, "Ni")
        d = 1 if x < 4.8 else -1
        arrow(ax, (x + d * 0.45, y), (x + d * 1.15, y), GREY, 1.6, ms=11)
    txt(ax, 4.8, -0.55, "ложка (катод)", 10.5, INK)
    txt(ax, 4.8, -1.15, "раствор $\\mathrm{NiSO_4}$", 10.5, GREY)
    save(f, "electrolysis-electroplating")


def relief(x0, x1, base, h, n_bumps=2):
    """A stair-step relief profile as polyline points between x0 and x1"""
    w = (x1 - x0) / (2 * n_bumps + 1)
    pts = [(x0, base)]
    for i in range(n_bumps):
        a = x0 + (2 * i + 1) * w
        pts += [(a, base), (a + 0.08, base + h), (a + w - 0.08, base + h), (a + w, base)]
    pts.append((x1, base))
    return pts


@fig("electrolysis-galvanoplastics")
def _():
    f, axs = plt.subplots(1, 4, figsize=(13.4, 3.6))
    titles = ["1. Оттиск оригинала", "2. Слой графита", "3. Рост металла в ванне", "4. Копия"]
    for ax, t in zip(axs, titles):
        ax.set_aspect("equal")
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-1.7, 3.0)
        ax.axis("off")
        ax.set_title(t, fontsize=11)
    # 1: original above, plasticine below
    ax = axs[0]
    orig = relief(0, 4, 1.4, -0.5)
    ax.add_patch(Polygon(orig + [(4, 2.2), (0, 2.2)], fc=WARM, ec=INK, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((0, -1.0), 4, 1.4, fc=tint(GREEN, 0.6), ec=INK, lw=1.4, zorder=2))
    txt(ax, 2, 1.85, "оригинал", 10.5)
    txt(ax, 2, -0.3, "пластилин, воск", 10.5)
    arrow(ax, (4.3, 2.2), (4.3, 0.9), C1, 1.6, ms=11)
    # 2: plasticine with imprint and graphite
    ax = axs[1]
    surf = relief(0, 4, 0.4, -0.5)
    ax.add_patch(Polygon([(0, -1.0), (4, -1.0)] + surf[::-1], fc=tint(GREEN, 0.6), ec=INK, lw=1.4, zorder=2))
    line(ax, [p for p in surf], tint(INK, 0.15), 3.0, z=5)
    txt(ax, 2, 1.0, "графит: проводящий слой", 10.5, tint(INK, 0.15))
    txt(ax, 2, -0.5, "пластилин", 10.5)
    # 3: bath with growing layer
    ax = axs[2]
    ax.add_patch(Rectangle((-0.3, -1.4), 4.6, 2.9, fc=SOLUTION, ec="none", zorder=0))
    line(ax, [(-0.3, 2.3), (-0.3, -1.4), (4.3, -1.4), (4.3, 2.3)], INK, 1.8)
    surf = relief(0, 4, 0.2, -0.5)
    ax.add_patch(Polygon([(0, -0.8), (4, -0.8)] + surf[::-1], fc=tint(GREEN, 0.6), ec=INK, lw=1.2, zorder=2))
    top = [(x, y + 0.7) for x, y in surf]
    ax.add_patch(Polygon(surf + top[::-1], fc=CU_C, ec=INK, lw=1.2, zorder=3))
    line(ax, [(2, 0.9), (2, 2.7)], INK, 1.6)
    plus_minus(ax, 2.35, 2.75, "$-$", 13)
    txt(ax, 2, -1.15, "слой металла растёт", 10, INK)
    # 4: copy
    ax = axs[3]
    surf = relief(0, 4, 0.2, -0.5)
    top = [(x, 0.9) for x, _ in surf]
    ax.add_patch(Polygon(surf + [(4, 0.9), (0, 0.9)], fc=CU_C, ec=INK, lw=1.4, zorder=3))
    txt(ax, 2, 0.35, "копия", 10.5)
    txt(ax, 2, -0.6, "рельеф повторён", 10.5, GREY)
    f.tight_layout()
    save(f, "electrolysis-galvanoplastics")


@fig("electrolysis-polishing")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.8, 3.8))
    ax = axs[0]
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-1.4, 3.6)
    ax.axis("off")
    ax.set_title("Полировка: выступы растворяются быстрее", fontsize=11)
    xs = np.linspace(0, 9, 200)
    rng = np.random.default_rng(3)
    rough = 1.0 + 0.55 * np.sin(xs * 2.7) * np.cos(xs * 1.3) + 0.25 * np.sin(xs * 6.1 + 1)
    smooth = rough.min() - 0.1 + 0.05 * np.sin(xs * 1.0)  # the anode only dissolves: the new surface lies under the deepest hollow
    ax.fill_between(xs, -0.6, rough, color=ALUM, ec=INK, lw=1.4, zorder=3)
    ax.plot(xs, smooth, color=C1, lw=1.6, ls="--", zorder=5)
    ax.text(4.5, -0.15, "металлическая пластина, анод $+$", ha="center", fontsize=10.5, zorder=6)
    ax.text(4.5, 3.1, "электролит", ha="center", fontsize=10.5, color=C2)
    ax.text(9.3, smooth[-1], "после", ha="left", fontsize=10, color=C1)
    ax = axs[1]
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-1.4, 3.6)
    ax.axis("off")
    ax.set_title("Заточка: заусенец растворяется", fontsize=11)
    blade = [(0, 0.6), (6.0, 1.45), (6.0, 1.55), (0, 2.4)]
    ax.add_patch(Polygon(blade, fc=ALUM, ec=INK, lw=1.4, zorder=3))
    burr = [(6.0, 1.45), (7.6, 1.15), (7.7, 1.25), (6.0, 1.55)]
    ax.add_patch(Polygon(burr, fc=tint(RED, 0.65), ec=C1, lw=1.2, zorder=4))
    arrow(ax, (8.3, 2.3), (7.2, 1.35), C1, 1.4, ms=11)
    ax.text(8.2, 2.5, "заусенец", fontsize=10.5, color=C1, ha="center")
    ax.text(2.4, 1.5, "лезвие, анод $+$", fontsize=10.5, ha="center", rotation=0)
    f.tight_layout()
    save(f, "electrolysis-polishing")


@fig("electrolysis-layer-thickness")
def _():
    f, ax = canvas(7.4, 4.2, (-1.0, 10.0), (-1.0, 4.4))
    top = [(0.0, 2.2), (5.0, 2.2), (6.6, 3.4), (1.6, 3.4)]
    ax.add_patch(Polygon(top, fc=tint(COPPER, 0.6), ec=INK, lw=1.5, zorder=3))
    front = [(0.0, 2.2), (5.0, 2.2), (5.0, 1.85), (0.0, 1.85)]
    ax.add_patch(Polygon(front, fc=tint(COPPER, 0.35), ec=INK, lw=1.5, zorder=3))
    side = [(5.0, 2.2), (6.6, 3.4), (6.6, 3.05), (5.0, 1.85)]
    ax.add_patch(Polygon(side, fc=tint(COPPER, 0.15), ec=INK, lw=1.5, zorder=3))
    ax.add_patch(Polygon([(0.0, 1.85), (5.0, 1.85), (5.0, 0.0), (0.0, 0.0)], fc=ALUM, ec=INK, lw=1.5, zorder=2))
    ax.add_patch(Polygon([(5.0, 1.85), (6.6, 3.05), (6.6, 1.2), (5.0, 0.0)], fc=tint(INK, 0.65), ec=INK, lw=1.5, zorder=2))
    txt(ax, 3.3, 2.8, "$S$", 14)
    arrow(ax, (5.5, 2.225), (5.5, 2.575), C1, 1.0, "<|-|>", 8)  # on the side strip of the layer at x = 5.5
    txt(ax, 7.0, 2.0, "толщина слоя $h$", 10.5, C1, "left")
    txt(ax, 2.5, 0.9, "деталь", 11, INK)
    txt(ax, 3.3, 3.85, "площадь покрытия", 10.5, GREY)
    save(f, "electrolysis-layer-thickness")


# ---------------------------------------------------------------- problems of the preparation lessons


@fig("metal-iron-wire-thermometer")
def _():
    f, ax = plt.subplots(figsize=(6.4, 4.2))
    alpha = 6e-3
    r0 = 15 / (1 + alpha * 10)
    tt = np.linspace(-20, 70, 50)
    ax.plot(tt, r0 * (1 + alpha * tt), color=C1, lw=2.0)
    t2 = (18.25 / 15) * (1 / alpha + 10) - 1 / alpha
    for t, r, name in ((10, 15.0, "$t_1=10\\,^\\circ$C, $R_1=15$ Ом"), (t2, 18.25, "$t_2\\approx48\\,^\\circ$C, $R_2=18{,}25$ Ом")):
        ax.scatter([t], [r], s=50, color=INK, zorder=5)
        ax.plot([t, t], [0, r], color=GRID, lw=1.0, zorder=1)
        ax.plot([-20, t], [r, r], color=GRID, lw=1.0, zorder=1)
    ax.text(12, 13.2, "$t_1=10\\,^\\circ$C\n$R_1=15$ Ом", fontsize=10)
    ax.text(t2 + 2, 16.0, "$t_2\\approx48\\,^\\circ$C\n$R_2=18{,}25$ Ом", fontsize=10)
    ax.set_xlim(-20, 70)
    ax.set_ylim(12, 20)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("$R$, Ом")
    ax.set_title("Железная проволока как термометр")
    save(f, "metal-iron-wire-thermometer")


@fig("electrolysis-aerostat-forces")
def _():
    f, ax = canvas(5.6, 5.6, (-3.2, 3.6), (-3.6, 3.4))
    ax.add_patch(Circle((0, 0.6), 2.3, fc=SOFT, ec=INK, lw=1.8, zorder=2))
    # The cone starts on the balloon outline (half-width 0.9 at y = 0.6 - sqrt(2.3^2 - 0.9^2)); its top edge is not drawn
    ytop = 0.6 - np.sqrt(2.3**2 - 0.9**2)
    cone = [(-0.9, ytop), (-0.5, -2.4), (0.5, -2.4), (0.9, ytop)]
    ax.add_patch(Polygon(cone, closed=True, fc=PAPER, ec="none", zorder=1))
    ax.add_patch(Polygon(cone, closed=False, fill=False, ec=INK, lw=1.4, zorder=2))
    ax.add_patch(Rectangle((-0.5, -3.1), 1.0, 0.7, fc=LIGHT, ec=INK, lw=1.4, zorder=2))
    txt(ax, -1.0, 1.3, r"$\rho_{\mathrm{H_2}}$, $V$", 13, INK)  # beside the arrow of the buoyant force
    arrow(ax, (0, 0.6), (0, 3.2), C3, 2.2, ms=15)
    txt(ax, 0.6, 3.05, r"$F_{\mathrm{А}}$", 13, C3)
    arrow(ax, (0, 0.6), (0, -1.9), C1, 2.2, ms=15)
    txt(ax, 1.5, -1.0, r"$(m_{\mathrm{H_2}}+m_{\mathrm{об}})\,g$", 11.5, C1)
    txt(ax, -2.9, 2.4, r"$\rho_{\mathrm{в}}$", 13, GREY)
    save(f, "electrolysis-aerostat-forces")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
