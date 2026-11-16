"""Graphs and sketches for the notes "Электрический ток. Электрическая цепь" and "Сила тока и напряжение" (section f11, lessons 143-150).

Circuit schemes are drawn by circuit_diagrams.py; this script draws graphs, experiment sketches and instrument dials.
Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 current_voltage.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes current-, voltage-)
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "11. Электрические явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, WARM, num, saver, tint

GRID = ASH
GREY = tint(INK, 0.45)  # outlines of neutral bodies, guides and small notes
ORANGE = ACCENT  # a highlighted value beside RED and BLUE: the name is kept, the role is ACCENT
WATER = tint(SKY, 0.6)
IRON = tint(INK, 0.45)  # grey metal and the lines and labels that stand for it
SOFT = tint(INK, 0.94)  # the pale body fill of a part
PLATE = tint(INK, 0.87)  # a grey plate or a block

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def blank(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def txt(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)


def charge_sign(ax, x, y, sign, r=0.13, color=BLUE):
    ax.add_patch(Circle((x, y), r, fc=PAPER, ec=color, lw=1.2, zorder=5))
    ax.plot([x - r * 0.55, x + r * 0.55], [y, y], color=color, lw=1.2, zorder=6)
    if sign == "+":
        ax.plot([x, x], [y - r * 0.55, y + r * 0.55], color=color, lw=1.2, zorder=6)


# ---------------------------------------------------------------- note 1


def two_balls(ax, cy=1.4, plus_left=True):
    for cx, sign, col in ((1.6, "+", RED), (5.4, "-", BLUE)):
        ax.add_patch(Circle((cx, cy), 1.05, fc=SOFT, ec=INK, lw=1.8))
        rng = np.random.default_rng(3 if sign == "+" else 5)
        for k in range(9):
            a = 2 * np.pi * k / 9 + 0.3
            rr = 0.62 + (k % 2) * 0.12
            x, y = cx + rr * np.cos(a), cy + rr * np.sin(a)
            txt(ax, x, y, "+" if sign == "+" else "−", size=13, color=col)
    return (1.6, cy), (5.4, cy)


@fig("current-electrometer-flow")
def _():
    f, ax = blank(7.4, 4.4, (-0.2, 7.2), (-0.3, 4.4))
    two_balls(ax)
    # conductor
    ax.add_patch(FancyArrowPatch((2.35, 2.05), (4.65, 2.05), connectionstyle="arc3,rad=-0.32", arrowstyle="-", lw=4, color=IRON))
    txt(ax, 3.5, 1.62, "проводник", size=10, color=IRON)
    arrow(ax, (4.5, 3.25), (2.5, 3.25), color=BLUE, lw=2.2)
    txt(ax, 3.5, 3.55, "движение электронов", color=BLUE, size=10.5)
    arrow(ax, (2.5, 3.95), (4.5, 3.95), color=RED, lw=2.2)
    txt(ax, 3.5, 4.22, "направление тока", color=RED, size=10.5)
    txt(ax, 1.6, -0.1, "недостаток\nэлектронов", size=10.5)
    txt(ax, 5.4, -0.1, "избыток\nэлектронов", size=10.5)
    save(f, "current-electrometer-flow")


@fig("current-conditions-source")
def _():
    f, ax = blank(8.4, 5.6, (-0.9, 7.9), (-2.6, 4.5))
    (lx, ly), (rx, ry) = two_balls(ax, cy=1.4)
    ax.add_patch(FancyArrowPatch((2.4, 2.1), (4.6, 2.1), connectionstyle="arc3,rad=-0.3", arrowstyle="-", lw=4, color=IRON))
    arrow(ax, (4.5, 3.05), (2.5, 3.05), color=BLUE, lw=2.0)
    txt(ax, 3.5, 3.35, "электроны в проводнике", color=BLUE, size=10)
    # source contour
    ax.add_patch(Rectangle((-0.7, -2.4), 8.4, 2.4, fc="none", ec=INK, lw=1.6, ls="--", zorder=1))
    txt(ax, 3.5, -2.1, "источник тока", size=11.5, weight="bold")
    txt(ax, 1.0, -0.5, "положительный\nполюс", size=9.5, ha="center")
    txt(ax, 6.0, -0.5, "отрицательный\nполюс", size=9.5, ha="center")
    charge_sign(ax, 3.5, -1.2, "-", r=0.17)
    arrow(ax, (3.28, -1.2), (2.1, -1.2), color=RED, lw=2.4)
    arrow(ax, (3.72, -1.2), (4.9, -1.2), color=GREEN, lw=2.4)
    txt(ax, 2.7, -1.65, r"$F_{\mathrm{эл}}$", size=13, color=RED)
    txt(ax, 4.3, -1.65, r"$F_{\mathrm{ст}}$", size=13, color=GREEN)
    save(f, "current-conditions-source")


@fig("current-electrons-chaos-drift")
def _():
    f, axes = plt.subplots(1, 2, figsize=(9.6, 3.2))
    rng = np.random.default_rng(11)
    # starts lie in the right part of the wire, because the drift carries the electrons to the left (against the current)
    starts = [(2.4, 0.9), (3.3, 2.0), (4.6, 1.1), (5.7, 2.1), (6.6, 0.8), (7.3, 1.6), (1.9, 2.2), (7.0, 2.3)]

    def fold(v, lo, hi):
        """Reflect a coordinate from the walls instead of clipping it, so the points do not stick to a wall."""
        span = hi - lo
        w = np.mod(v - lo, 2 * span)
        return lo + np.where(w <= span, w, 2 * span - w)

    steps = []
    for _s in starts:
        ang = rng.uniform(0, 2 * np.pi, 7)
        steps.append(np.c_[np.cos(ang), np.sin(ang)] * 0.55)
    for ax, drift, title in zip(axes, (0.0, 0.3), ("Тока нет: только тепловое движение", "Ток есть: к тепловому движению добавлен снос")):
        ax.set_xlim(-0.4, 8.4)
        ax.set_ylim(-0.7, 3.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 8, 3, boxstyle="round,pad=0,rounding_size=0.25", fc=SOFT, ec=IRON, lw=2.5))
        for (x0, y0), st in zip(starts, steps):
            st = st.copy()
            st[:, 0] -= drift * 1.0  # drift is against the current, which points to the right
            path = np.vstack([[x0, y0], np.array([x0, y0]) + np.cumsum(st, axis=0)])
            path[:, 1] = fold(path[:, 1], 0.2, 2.8)
            path[:, 0] = fold(path[:, 0], 0.2, 7.8)
            ax.plot(path[:, 0], path[:, 1], color=BLUE, lw=1.1, alpha=0.8)
            ax.plot(*path[0], "o", color=BLUE, ms=4)
            ax.plot(*path[-1], "o", color=BLUE, ms=6, mec=PAPER, mew=0.8)
        ax.set_title(title, fontsize=11)
    arrow(axes[1], (5.2, -0.3), (2.8, -0.3), color=BLUE, lw=2.2)
    txt(axes[1], 4.0, -0.62, "средний снос электронов", size=9.5, color=BLUE)
    arrow(axes[1], (2.8, 3.15), (5.2, 3.15), color=RED, lw=2.2)
    txt(axes[1], 6.6, 3.15, "ток", size=10.5, color=RED)
    txt(axes[0], 4.0, -0.5, r"$v_{\mathrm{тепл}}\approx 100$ км/с, направления случайны", size=9.5)
    f.subplots_adjust(wspace=0.05)
    save(f, "current-electrons-chaos-drift")


@fig("current-effect-heating")
def _():
    f, ax = blank(8.2, 5.0, (0, 10), (0, 6.2))
    # stand
    for x in (1.2, 8.8):
        ax.add_patch(Rectangle((x - 0.25, 4.6), 0.5, 0.8, fc=IRON, ec=INK, lw=1.2))
    xs = np.linspace(1.2, 8.8, 200)
    ax.plot(xs, np.full_like(xs, 4.6), color=GREY, lw=1.6, ls=(0, (4, 3)))
    sag = 4.6 - 0.85 * np.sin(np.pi * (xs - 1.2) / 7.6)
    ax.plot(xs, sag, color=RED, lw=2.4)
    for x in (2.6, 4.0, 5.4, 6.8):
        y = 4.6 - 0.85 * np.sin(np.pi * (x - 1.2) / 7.6)
        ax.add_patch(Polygon([[x - 0.12, y], [x + 0.12, y], [x, y - 0.5]], fc=WARM, ec=INK, lw=0.8))
    txt(ax, 5.0, 5.55, "тока нет", size=10.5, color=GREY)
    txt(ax, 5.0, 3.15, "ток течёт: проволока нагрелась, удлинилась и провисла", size=10, color=RED)
    # circuit
    ax.plot([1.2, 1.2, 3.2], [4.6, 1.3, 1.3], color=INK, lw=1.6)
    ax.plot([8.8, 8.8, 7.0], [4.6, 1.3, 1.3], color=INK, lw=1.6)
    # key
    ax.plot([3.2, 3.6], [1.3, 1.3], color=INK, lw=1.6)
    ax.plot([3.6, 4.5], [1.3, 1.38], color=INK, lw=1.6)  # closed key: the lever rests on the second contact
    ax.plot([4.5, 5.2], [1.3, 1.3], color=INK, lw=1.6)
    ax.plot([3.6, 4.5], [1.3, 1.3], "o", color=INK, ms=4)
    ax.plot([4.5, 5.2], [1.3, 1.3], color=INK, lw=1.6)
    ax.plot([5.2, 5.5], [1.3, 1.3], color=INK, lw=1.6)
    ax.add_patch(Rectangle((5.5, 0.9), 1.5, 0.8, fc=PAPER, ec=INK, lw=1.6))
    txt(ax, 6.25, 1.3, "ИТ", size=12)
    txt(ax, 4.1, 0.7, "ключ замкнут", size=10)
    txt(ax, 6.25, 0.4, "источник тока", size=10)
    save(f, "current-effect-heating")


@fig("current-effect-magnetic")
def _():
    f, ax = blank(7.8, 5.6, (0, 9), (0, 6.5))
    # iron core and coil
    ax.add_patch(Rectangle((2.05, 2.6), 0.5, 2.8, fc=IRON, ec=INK, lw=1.2, zorder=2))
    for k in range(9):
        y = 2.75 + k * 0.3
        ax.plot([1.85, 2.75], [y, y + 0.18], color=COPPER, lw=2.4, zorder=3)
    # nails
    rng = np.random.default_rng(2)
    for x, dy in ((1.95, 0.75), (2.15, 1.0), (2.3, 0.8), (2.45, 1.05), (2.6, 0.7)):
        ax.plot([x, x + (x - 2.3) * 0.6], [2.6, 2.6 - dy], color=tint(INK, 0.3), lw=2.0, solid_capstyle="round", zorder=1)
    ax.plot([1.95, 1.7], [2.0, 1.55], alpha=0)
    # wires: coil top -> key -> IT -> coil bottom
    # the top wire starts at the end of the last coil turn (2.75, 5.33), not at the iron core
    ax.plot([2.75, 2.95, 2.95, 4.2], [5.33, 5.33, 5.9, 5.9], color=INK, lw=1.6)
    ax.plot([4.2, 4.6], [5.9, 5.9], color=INK, lw=1.6)
    ax.plot([4.6, 5.5], [5.9, 5.96], color=INK, lw=1.6)  # closed key
    ax.plot([4.6, 5.5], [5.9, 5.9], "o", color=INK, ms=4)
    ax.plot([5.5, 6.2], [5.9, 5.9], color=INK, lw=1.6)
    ax.add_patch(Rectangle((6.2, 5.5), 1.5, 0.8, fc=PAPER, ec=INK, lw=1.6))
    txt(ax, 6.95, 5.9, "ИТ", size=12)
    ax.plot([7.7, 8.4, 8.4, 1.2, 1.2, 1.85], [5.9, 5.9, 0.9, 0.9, 2.75, 2.75], color=INK, lw=1.6)
    txt(ax, 5.05, 5.45, "ключ замкнут", size=10)
    txt(ax, 0.9, 4.35, "катушка,\nнамотанная\nпроводом", size=9.5, ha="center")
    txt(ax, 3.7, 4.55, "железный\nсердечник", size=9.5, ha="left")
    ax.annotate("", xy=(2.5, 4.4), xytext=(3.65, 4.5), arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    txt(ax, 3.9, 1.5, "железные гвозди\nпритягиваются", size=10, ha="left")
    ax.annotate("", xy=(2.55, 1.9), xytext=(3.85, 1.6), arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    save(f, "current-effect-magnetic")


@fig("current-effect-chemical")
def _():
    f, ax = blank(8.6, 6.0, (0, 10), (0, 8.0))
    # beaker
    ax.add_patch(Rectangle((1.2, 0.6), 4.6, 3.6, fc=WATER, ec="none", alpha=0.75, zorder=0))
    ax.plot([1.2, 1.2, 5.8, 5.8], [4.9, 0.6, 0.6, 4.9], color=INK, lw=2.2)
    txt(ax, 3.5, 0.2, r"водный раствор $\mathrm{CuSO}_4$", size=10.5)
    # electrodes
    for x, name in ((2.0, "анод"), (5.0, "катод")):
        ax.add_patch(Rectangle((x - 0.2, 1.1), 0.4, 4.6, fc=tint(INK, 0.2), ec=INK, lw=1.2, zorder=3))
    ax.add_patch(Rectangle((4.8, 1.1), 0.4, 2.0, fc=COPPER, ec=INK, lw=1.0, zorder=4))
    ax.add_patch(Rectangle((4.62, 1.3), 0.18, 1.6, fc=COPPER, ec="none", zorder=4))
    ax.add_patch(Rectangle((5.2, 1.3), 0.18, 1.6, fc=COPPER, ec="none", zorder=4))
    txt(ax, 1.55, 5.9, "анод", size=11, ha="right")
    txt(ax, 4.45, 5.9, "катод", size=11, ha="right")
    txt(ax, 7.2, 2.2, "красный слой меди\nна катоде", size=9.5, ha="left", color=COPPER)
    ax.annotate("", xy=(5.4, 2.1), xytext=(7.15, 2.2), arrowprops=dict(arrowstyle="-", color=COPPER, lw=1))
    # ions
    for y in (2.3, 3.3, 4.0):
        txt(ax, 3.1, y, r"$\mathrm{Cu}^{2+}$", size=10, color=RED)
        arrow(ax, (3.55, y), (4.35, y), color=RED, lw=1.5, scale=10)
    for y in (1.7, 2.8):
        txt(ax, 4.05, y, r"$\mathrm{SO}_4^{2-}$", size=10, color=BLUE)
        arrow(ax, (3.5, y), (2.55, y), color=BLUE, lw=1.5, scale=10)
    # wires, battery on the top rail (long plate is plus, on the anode side), lamp on the cathode wire
    rail = 7.4
    ax.plot([2.0, 2.0, 3.3], [5.7, rail, rail], color=INK, lw=1.6)
    ax.plot([3.3, 3.3], [rail - 0.25, rail + 0.25], color=INK, lw=1.8)
    ax.plot([3.55, 3.55], [rail - 0.13, rail + 0.13], color=INK, lw=4)
    ax.plot([3.55, 4.1], [rail, rail], color=INK, lw=1.6)
    ax.plot([4.1, 4.1], [rail - 0.25, rail + 0.25], color=INK, lw=1.8)
    ax.plot([4.35, 4.35], [rail - 0.13, rail + 0.13], color=INK, lw=4)
    ax.plot([4.35, 5.0, 5.0], [rail, rail, 6.75], color=INK, lw=1.6)
    txt(ax, 2.75, rail + 0.32, "+", size=12)
    txt(ax, 4.7, rail + 0.32, "−", size=12)
    ax.plot([5.0, 5.0], [5.7, 6.15], color=INK, lw=1.6)
    ax.add_patch(Circle((5.0, 6.45), 0.3, fc=PAPER, ec=INK, lw=1.6, zorder=4))
    ax.plot([4.79, 5.21], [6.24, 6.66], color=INK, lw=1.3, zorder=5)
    ax.plot([4.79, 5.21], [6.66, 6.24], color=INK, lw=1.3, zorder=5)
    txt(ax, 5.5, 6.45, "лампа горит:\nв цепи идёт ток", size=9.5, ha="left")
    save(f, "current-effect-chemical")


@fig("current-galvanic-sources")
def _():
    f, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Лимон с медной и железной проволокой", fontsize=11)
    ax.add_patch(Ellipse((3.2, 1.5), 3.0, 2.2, fc=tint(WARM, 0.4), ec=WARM, lw=2))
    ax.plot([2.4, 2.6], [1.5, 3.4], color=COPPER, lw=3)
    ax.plot([3.8, 3.7], [1.5, 3.4], color=IRON, lw=3)
    txt(ax, 1.95, 3.9, "медь", size=10, color=COPPER)
    txt(ax, 4.35, 3.4, "железо", size=10, color=IRON)
    # galvanometer
    ax.add_patch(FancyBboxPatch((5.4, 1.6), 2.2, 1.6, boxstyle="round,pad=0.05,rounding_size=0.15", fc=PAPER, ec=INK, lw=1.8))
    ax.add_patch(Arc((6.5, 1.85), 1.6, 1.4, theta1=40, theta2=140, color=INK, lw=1.4))
    ax.plot([6.5, 6.9], [1.85, 2.9], color=RED, lw=2)
    txt(ax, 6.5, 1.3, "гальванометр", size=10)
    ax.plot([2.6, 2.6, 5.4, 5.4], [3.4, 4.4, 4.4, 3.2], color=INK, lw=1.2)
    ax.plot([3.7, 3.7, 5.0, 5.0, 5.4], [3.4, 3.9, 3.9, 2.0, 2.0], color=INK, lw=1.2)
    ax = axes[1]
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Вольтов столб", fontsize=11)
    y = 0.4
    for k in range(4):
        ax.add_patch(Rectangle((1.5, y), 2.6, 0.32, fc=tint(INK, 0.7), ec=INK, lw=1))
        ax.add_patch(Rectangle((1.5, y + 0.32), 2.6, 0.32, fc=tint(SKY, 0.7), ec=INK, lw=1, hatch="///"))
        ax.add_patch(Rectangle((1.5, y + 0.64), 2.6, 0.32, fc=SOFT, ec=INK, lw=1))
        y += 1.0
    txt(ax, 4.45, 0.56, "цинк", size=9.5, ha="left")
    txt(ax, 4.45, 0.88, "подушечка с солёной водой", size=9.5, ha="left")
    txt(ax, 4.45, 1.2, "серебряный диск", size=9.5, ha="left")
    txt(ax, 2.8, 4.75, "+", size=16, color=RED)
    txt(ax, 2.8, 0.05, "−", size=16, color=BLUE)
    txt(ax, 2.8, 5.35, "каждая тройка слоёв — один элемент", size=9.5, color=GREY)
    f.subplots_adjust(wspace=0.05)
    save(f, "current-galvanic-sources")


# ---------------------------------------------------------------- note 2


@fig("current-charge-cross-section")
def _():
    f, ax = blank(8.0, 3.8, (0, 10), (0, 4.6))
    ax.add_patch(Rectangle((0.5, 1.2), 8.4, 2.0, fc=SOFT, ec=IRON, lw=2.2))
    ax.add_patch(Ellipse((5.4, 2.2), 0.7, 2.0, fc=PLATE, ec=INK, lw=1.6, ls="-"))
    ax.add_patch(Ellipse((5.4, 2.2), 0.7, 2.0, fc="none", ec=RED, lw=1.6, ls="--"))
    rng = np.random.default_rng(4)
    for x in (1.2, 2.0, 2.9, 3.7, 6.3, 7.1, 8.0):
        y = rng.uniform(1.5, 2.9)
        charge_sign(ax, x, y, "-", r=0.14)
        arrow(ax, (x - 0.15, y), (x - 0.65, y), color=BLUE, lw=1.4, scale=9)
    arrow(ax, (3.0, 3.75), (6.6, 3.75), color=RED, lw=2.2)
    txt(ax, 4.8, 4.1, "ток", size=11, color=RED)
    txt(ax, 5.4, 0.75, "поперечное сечение проводника", size=10)
    txt(ax, 5.4, 0.25, r"за время $t$ через него проходит заряд $q$", size=10)
    txt(ax, 1.4, 0.75, "электроны", size=10, color=BLUE)
    save(f, "current-charge-cross-section")


@fig("current-charge-time-graph")
def _():
    f, ax = plt.subplots(figsize=(6.4, 4.4))
    t = np.linspace(0, 4, 50)
    ax.plot(t, 1.0 * t, color=BLUE, lw=2.4, label=r"$I = 1$ А")
    ax.plot(t, 2.0 * t, color=RED, lw=2.4, label=r"$I = 2$ А")
    ax.plot([1, 1], [0, 2], color=GREY, ls="--", lw=1)
    for y, c in ((1, BLUE), (2, RED)):
        ax.plot([0, 1], [y, y], color=c, ls="--", lw=1)
        ax.plot([1], [y], "o", color=c)
    ax.plot([2.5, 3.5, 3.5], [5.0, 5.0, 7.0], color=RED, lw=1.2)
    txt(ax, 3.0, 4.6, r"$\Delta t$", size=11, color=RED)
    txt(ax, 3.82, 6.0, r"$\Delta q$", size=11, color=RED)
    txt(ax, 2.35, 6.4, r"$I = \dfrac{\Delta q}{\Delta t}$ — наклон прямой", size=10.5, ha="right", color=INK)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 8.4)
    ax.set_xlabel(r"время $t$, с")
    ax.set_ylabel(r"заряд $q$, Кл")
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Заряд через сечение растёт линейно")
    save(f, "current-charge-time-graph")


@fig("current-ampere-definition")
def _():
    f, axes = plt.subplots(1, 2, figsize=(9.2, 4.2))
    for ax, same in zip(axes, (True, False)):
        ax.set_xlim(-1.2, 6.2)
        ax.set_ylim(-0.6, 5.0)
        ax.set_aspect("equal")
        ax.axis("off")
        x1, x2 = 1.0, 4.4
        ax.plot([x1, x1], [0.2, 4.2], color=INK, lw=3)
        ax.plot([x2, x2], [0.2, 4.2], color=INK, lw=3)
        up = 1 if same else 1
        arrow(ax, (x1 - 0.45, 3.2), (x1 - 0.45, 3.9), color=RED, lw=2.4)
        if same:
            arrow(ax, (x2 + 0.45, 3.2), (x2 + 0.45, 3.9), color=RED, lw=2.4)
        else:
            arrow(ax, (x2 + 0.45, 3.9), (x2 + 0.45, 3.2), color=RED, lw=2.4)
        txt(ax, x1 - 0.9, 3.55, r"$I$", size=13, color=RED)
        txt(ax, x2 + 0.9, 3.55, r"$I$", size=13, color=RED)
        ax.plot([x1, x2], [0.0, 0.0], color=GREY, lw=1.2)
        ax.plot([x1, x1], [-0.1, 0.1], color=GREY, lw=1.2)
        ax.plot([x2, x2], [-0.1, 0.1], color=GREY, lw=1.2)
        txt(ax, (x1 + x2) / 2, -0.35, r"$d = 1$ м", size=10.5)
        if same:
            arrow(ax, (x1 + 0.1, 2.1), (x1 + 1.0, 2.1), color=GREEN, lw=2.2)
            arrow(ax, (x2 - 0.1, 2.1), (x2 - 1.0, 2.1), color=GREEN, lw=2.2)
            ax.set_title("Токи в одну сторону: притяжение", fontsize=11.5)
        else:
            arrow(ax, (x1 - 0.1, 2.1), (x1 - 1.0, 2.1), color=GREEN, lw=2.2)
            arrow(ax, (x2 + 0.1, 2.1), (x2 + 1.0, 2.1), color=GREEN, lw=2.2)
            ax.set_title("Токи в разные стороны: отталкивание", fontsize=11.5)
        txt(ax, (x1 + x2) / 2, 2.55, r"$F$ на каждый метр", size=10.5, color=GREEN)
    f.text(0.5, 0.0, r"$F = 2\cdot 10^{-7}$ Н на каждый метр длины при $I = 1$ А; тонкие бесконечно длинные проводники в вакууме", ha="center", fontsize=10, color=INK)
    f.subplots_adjust(wspace=0.1, bottom=0.08)
    save(f, "current-ampere-definition")


@fig("current-typical-values-log")
def _():
    f, ax = plt.subplots(figsize=(10.4, 4.6))
    ax.set_xscale("log")
    ax.set_xlim(1e-9, 3e3)
    ax.set_ylim(-3.2, 3.6)
    ax.yaxis.set_visible(False)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.set_xticks([1e-9, 1e-6, 1e-3, 1, 1e3])
    ax.set_xticklabels(["1 нА", "1 мкА", "1 мА", "1 А", "1 кА"])
    ax.tick_params(axis="x", pad=6)
    pts = [
        (1e-9, "наноампер: токи\nтакого порядка редки", 1.3, BLUE),
        (3e-7, "показание\nмикроамперметра\nв задаче: 0,3 мкА", -1.5, BLUE),
        (8e-5, "луч кинескопа 80 мкА;\nпредел микроамперметра\n100 мкА", 2.1, BLUE),
        (5e-1, "предел миллиамперметра\n500 мА", -1.7, ORANGE),
        (0.27, "лампочка от\nфонарика 0,27 А", 2.7, ORANGE),
        (5.0, "зарядка аккумулятора 5 А,\nэлектроплитка 5–10 А", 1.3, RED),
        (1000.0, "мощные сварочные\nаппараты: до кА", 2.4, RED),
    ]
    for x, label, y, c in pts:
        ax.plot([x, x], [0, y * 0.72], color=GREY, lw=1)
        ax.plot([x], [0], "o", color=c, ms=8, zorder=5)
        ax.text(x, y, label, ha="center", va="center", fontsize=9.5, color=INK)
    ax.plot([5, 10], [0, 0], color=RED, lw=6, alpha=0.5, solid_capstyle="butt")
    ax.set_title("Типичные силы тока на логарифмической шкале", pad=10)
    save(f, "current-typical-values-log")


@fig("current-dial-parallax")
def _():
    f, ax = blank(7.6, 5.1, (-0.5, 8.5), (-3.2, 5.4))
    # scale with mirror
    ax.add_patch(Rectangle((0.5, -0.25), 6.5, 0.25, fc=PLATE, ec=INK, lw=1.2))
    for k, x in enumerate((1.5, 3.75, 6.0)):
        ax.plot([x, x], [0, 0.35], color=INK, lw=1.6)
        txt(ax, x, -0.6, str(k + 1), size=11)
    ax.plot([3.75, 3.75], [0, 2.0], color=RED, lw=2.6)
    ax.plot([3.75, 3.75], [-0.25, -2.25], color=RED, lw=2.6, alpha=0.35)
    txt(ax, 4.05, 1.9, "стрелка", size=10, ha="left", color=RED)
    txt(ax, 4.05, -1.9, "её отражение\nв зеркале", size=9.5, ha="left", color=RED, alpha=0.7)
    tip = np.array([3.75, 2.0])
    for eye, col in (((0.2, 4.8), BLUE), ((7.3, 4.8), BLUE), ((3.75, 5.0), GREEN)):
        ax.add_patch(Circle(eye, 0.22, fc=PAPER, ec=col, lw=1.8))
        d = tip - np.array(eye)
        end = np.array(eye) + d * ((0 - eye[1]) / d[1])
        ax.plot([eye[0], end[0]], [eye[1], end[1]], color=col, lw=1.2, ls="--")
        ax.plot([eye[0], tip[0]], [eye[1], tip[1]], color=col, lw=1.6)
    # the ray of the left eye through the tip reaches the scale at x = 6.3 (mark 3), the right one at x = 1.2 (mark 1)
    txt(ax, 0.2, 5.3, "видно \"3\"", size=9.5, color=BLUE)
    txt(ax, 7.3, 5.3, "видно \"1\"", size=9.5, color=BLUE)
    txt(ax, 3.75, 5.55, "", size=8)
    # two lines below the end of the reflection line (y = -2.25)
    txt(ax, 3.75, -3.0, "взгляд перпендикулярно шкале:\nстрелка закрывает своё отражение, параллакса нет", size=9.5, color=GREEN)
    save(f, "current-dial-parallax")


# dial helper ---------------------------------------------------------------


def dial(ax, vmax, major, minor, value, unit, reading_text, title):
    """Draw a school meter dial; the scale is an arc of 80 degrees, zero at the left."""
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-0.6, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((-2.4, -0.4), 4.8, 3.3, boxstyle="round,pad=0.02,rounding_size=0.25", fc=SOFT, ec=INK, lw=2))
    px, py, R = 0.0, -1.6, 4.1
    a0, a1 = 116.0, 64.0
    ang = lambda v: np.deg2rad(a0 + (a1 - a0) * v / vmax)
    th = np.linspace(a0, a1, 100)
    ax.plot(px + R * np.cos(np.deg2rad(th)), py + R * np.sin(np.deg2rad(th)), color=INK, lw=1.4)
    nmaj = int(round(vmax / major))
    for i in range(nmaj + 1):
        for j in range(minor):
            v = i * major + j * major / minor
            if v > vmax + 1e-9:
                break
            a = ang(v)
            L = 0.24 if j == 0 else (0.16 if minor % 2 == 0 and j == minor // 2 else 0.1)
            ax.plot([px + R * np.cos(a), px + (R - L) * np.cos(a)], [py + R * np.sin(a), py + (R - L) * np.sin(a)], color=INK, lw=1.3 if j == 0 else 0.8)
        v = i * major
        a = ang(v)
        s = num(v, None)
        ax.text(px + (R - 0.55) * np.cos(a), py + (R - 0.55) * np.sin(a), s, ha="center", va="center", fontsize=10.5, color=INK)
    ax.text(0, 0.25, unit, ha="center", va="center", fontsize=13, color=INK, weight="bold")
    if value is not None:
        a = ang(value)
        ax.plot([px + (R - 0.9) * np.cos(a), px + (R + 0.08) * np.cos(a)], [py + (R - 0.9) * np.sin(a), py + (R + 0.08) * np.sin(a)], color=RED, lw=2.0)
        ax.plot([px + (R - 0.9) * np.cos(a), px], [py + (R - 0.9) * np.sin(a), py + 0.0], color=RED, lw=0)
    ax.add_patch(Circle((0, -0.15), 0.1, fc=INK, ec=INK, zorder=4))
    ax.set_title(title, fontsize=10.5, pad=4)
    ax.text(0, -0.8, reading_text, ha="center", va="center", fontsize=11, color=INK)


@fig("current-scale-price-ammeter")
def _():
    f, ax = plt.subplots(figsize=(5.4, 3.9))
    dial(ax, 2.0, 0.5, 10, None, "A", "", "Школьный амперметр, предел 2 А")
    ax.text(0, -1.0, "между подписанными штрихами 0 и 0,5 А — 10 делений:\n" + r"$c = \dfrac{0{,}5\ \mathrm{А}}{10} = 0{,}05\ \mathrm{А} = 50\ \mathrm{мА}$", ha="center", va="center", fontsize=10.5)
    ax.set_ylim(-1.5, 3.2)
    save(f, "current-scale-price-ammeter")


@fig("current-task-5-24-dials")
def _():
    f, axes = plt.subplots(1, 3, figsize=(11.6, 3.9))
    dial(axes[0], 3.0, 1.0, 10, 1.4, "mA", "", "а) миллиамперметр, предел 3 мА")
    dial(axes[1], 1.5, 0.5, 10, 0.3, r"$\mu$A", "", "б) микроамперметр, предел 1,5 мкА")
    dial(axes[2], 6.0, 2.0, 10, 5.0, "A", "", "в) амперметр, предел 6 А")
    notes = [r"$c = 0{,}1$ мА, $I = 1{,}4$ мА", r"$c = 0{,}05$ мкА, $I = 0{,}3$ мкА", r"$c = 0{,}2$ А, $I = 5$ А"]
    for ax, s in zip(axes, notes):
        ax.set_ylim(-1.2, 3.2)
        ax.text(0, -0.85, s, ha="center", va="center", fontsize=11, color=INK)
    f.subplots_adjust(wspace=0.08)
    save(f, "current-task-5-24-dials")


@fig("voltage-task-5-25-dials")
def _():
    f, axes = plt.subplots(1, 3, figsize=(11.6, 3.9))
    dial(axes[0], 15.0, 5.0, 10, 7.5, "V", "", "а) вольтметр, предел 15 В")
    dial(axes[1], 12.0, 4.0, 10, 10.0, "mV", "", "б) милливольтметр, предел 12 мВ")
    dial(axes[2], 6.0, 2.0, 10, 3.6, "kV", "", "в) киловольтметр, предел 6 кВ")
    notes = [r"$c = 0{,}5$ В, $U = 7{,}5$ В", r"$c = 0{,}4$ мВ, $U = 10$ мВ", r"$c = 0{,}2$ кВ, $U = 3{,}6$ кВ"]
    for ax, s in zip(axes, notes):
        ax.set_ylim(-1.2, 3.2)
        ax.text(0, -0.85, s, ha="center", va="center", fontsize=11, color=INK)
    f.subplots_adjust(wspace=0.08)
    save(f, "voltage-task-5-25-dials")


@fig("voltage-water-analogy")
def _():
    f, (ax, bx) = plt.subplots(1, 2, figsize=(11.2, 5.4), gridspec_kw={"width_ratios": [1.15, 1]})
    # hydraulic panel
    ax.set_xlim(0, 10.6)
    ax.set_ylim(-1.0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Вода: падение с высоты", fontsize=11.5)
    tank = Rectangle((2.0, 6.4), 2.2, 0.9, fc=WATER, ec=INK, lw=1.6)
    ax.add_patch(tank)
    ax.plot([3.1, 3.1], [6.4, 4.0], color=BLUE, lw=3)
    turbine1 = Circle((3.1, 3.7), 0.4, fc=PAPER, ec=INK, lw=1.6)
    ax.add_patch(turbine1)
    for k in range(4):
        a = k * np.pi / 2 + 0.4
        ax.plot([3.1, 3.1 + 0.4 * np.cos(a)], [3.7, 3.7 + 0.4 * np.sin(a)], color=INK, lw=1.4)
    ax.add_patch(Rectangle((2.3, 2.5), 1.6, 0.35, fc=WATER, ec=INK, lw=1.4))
    ax.plot([3.1, 3.1], [2.5, 1.7], color=BLUE, lw=3)
    turbine2 = Circle((3.1, 1.4), 0.4, fc=PAPER, ec=INK, lw=1.6)
    ax.add_patch(turbine2)
    for k in range(4):
        a = k * np.pi / 2 + 0.9
        ax.plot([3.1, 3.1 + 0.4 * np.cos(a)], [1.4, 1.4 + 0.4 * np.sin(a)], color=INK, lw=1.4)
    ax.add_patch(Rectangle((2.0, 0.3), 2.2, 0.55, fc=WATER, ec=INK, lw=1.6))
    # heights
    ax.annotate("", xy=(1.3, 3.7), xytext=(1.3, 6.4), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    txt(ax, 0.9, 5.0, r"$H$", size=13)
    ax.annotate("", xy=(4.9, 1.4), xytext=(4.9, 2.5), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    txt(ax, 5.35, 1.95, r"$h$", size=13)
    txt(ax, 5.0, -0.6, r"$H > h$: тот же поток воды, работа разная", size=10)
    # pump loop
    ax.plot([4.2, 6.9, 6.9, 4.2], [0.55, 0.55, 6.85, 6.85], color=BLUE, lw=3)
    ax.add_patch(Rectangle((6.3, 3.0), 1.2, 0.9, fc=PLATE, ec=INK, lw=1.6, zorder=3))
    txt(ax, 6.9, 3.45, "насос", size=10, zorder=4)
    arrow(ax, (7.7, 3.1), (7.7, 4.4), color=GREEN, lw=2.4)
    txt(ax, 7.95, 4.9, "в насосе работает\nсила давления", size=9.5, ha="left", color=GREEN)
    txt(ax, 4.4, 5.0, "у турбинок\nработает\nсила тяжести", size=9.5, ha="left", color=RED)
    # electric panel
    bx.set_xlim(0, 10)
    bx.set_ylim(0, 8)
    bx.set_aspect("equal")
    bx.axis("off")
    bx.set_title("Ток: перенос заряда полем", fontsize=11.5)
    bx.plot([1.5, 1.5, 8.5, 8.5, 1.5], [1.0, 6.6, 6.6, 1.0, 1.0], color=INK, lw=1.8)
    # lamps on top
    for x, name, col in ((3.4, r"$220$ В", RED), (6.6, r"$3{,}5$ В", ORANGE)):
        bx.add_patch(Circle((x, 6.6), 0.55, fc=PAPER, ec=INK, lw=1.8, zorder=3))
        bx.plot([x - 0.39, x + 0.39], [6.21, 6.99], color=INK, lw=1.4, zorder=4)
        bx.plot([x - 0.39, x + 0.39], [6.99, 6.21], color=INK, lw=1.4, zorder=4)
        txt(bx, x, 7.5, name, size=11, color=col)
    txt(bx, 5.0, 5.4, r"$I = 0{,}3$ А в обеих лампах", size=10.5)
    bx.add_patch(Rectangle((0.9, 3.0), 1.2, 1.4, fc=PLATE, ec=INK, lw=1.6, zorder=3))
    txt(bx, 1.5, 3.7, "ИТ", size=11, zorder=4)
    arrow(bx, (2.6, 3.2), (2.6, 4.3), color=GREEN, lw=2.4)
    txt(bx, 3.0, 2.3, "в источнике работает\nсторонняя сила", size=9.5, ha="left", color=GREEN)
    txt(bx, 5.0, 4.05, "на лампах работает\nэлектрическая сила", size=9.5, color=RED)
    txt(bx, 5.0, 0.4, "напряжение $U$ — аналог высоты $H$", size=10.5)
    f.subplots_adjust(wspace=0.05)
    save(f, "voltage-water-analogy")


@fig("voltage-work-charge-graph")
def _():
    f, ax = plt.subplots(figsize=(6.8, 4.8))
    q = np.array([0.1, 20.0])
    for U, c, name in ((220, RED, r"$220$ В (лампа)"), (5, BLUE, r"$5$ В (звонок)"), (3.5, ORANGE, r"$3{,}5$ В (лампа)")):
        ax.plot(q, U * q, color=c, lw=2.4, label=name)
        ax.plot([1], [U], "o", color=c)
    ax.plot([2], [10], "s", color=BLUE)
    ax.axvline(1, color=GREY, lw=1, ls="--")
    ax.annotate(r"$2$ Кл, $10$ Дж", xy=(2, 10), xytext=(3.2, 2.0), fontsize=10, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.1, 20)
    ax.set_ylim(0.3, 4000)
    ax.set_xlabel(r"перенесённый заряд $q$, Кл")
    ax.set_ylabel(r"работа поля $A$, Дж")
    ax.grid(True, which="major", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title(r"$A = qU$ на логарифмических осях")
    ax.text(1.15, 0.42, "при $q = 1$ Кл число\nджоулей равно числу вольт", fontsize=9.5, color=INK)
    save(f, "voltage-work-charge-graph")


@fig("voltage-typical-log")
def _():
    f, ax = plt.subplots(figsize=(10.6, 4.9))
    ax.set_xscale("log")
    ax.set_xlim(3e-7, 3e6)
    ax.set_ylim(-3.4, 3.8)
    ax.yaxis.set_visible(False)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.set_xticks([1e-6, 1e-3, 1, 1e3, 1e6])
    ax.set_xticklabels(["1 мкВ", "1 мВ", "1 В", "1 кВ", "1 МВ"])
    ax.tick_params(axis="x", pad=6)
    pts = [
        (1e-5, "напряжения порядка\nмикровольт измеряют\nмикровольтметром", 1.4, BLUE, "center"),
        (1e-2, "предел милливольтметра\n12 мВ", -1.4, BLUE, "center"),
        (1.25, "никель-кадмиевый\nаккумулятор 1,25 В", 2.0, GREEN, "right"),
        (1.5, "гальванический\nэлемент\n1,35–1,5 В", 1.2, GREEN, "left"),
        (3.3, "литиевый элемент\nчуть больше 3 В", -2.5, GREEN, "right"),
        (5.0, "звонок из\nзадачи 5 В", -1.4, ORANGE, "left"),
        (220.0, "сеть, настольная лампа\n220 В", 2.7, RED, "center"),
        (3600.0, "показание киловольтметра\nв задаче 3,6 кВ", -1.4, ORANGE, "center"),
        (1.1e5, "линия электропередачи\nв Одесской области\n110 кВ", 1.7, RED, "right"),
        (6.5e5, "до 550–750 кВ\nна выходе станций", 2.7, RED, "center"),
    ]
    for x, label, y, c, ha in pts:
        ax.plot([x, x], [0, y * 0.75], color=GREY, lw=1)
        ax.plot([x], [0], "o", color=c, ms=8, zorder=5)
        ax.text(x, y, label, ha=ha, va="center", fontsize=9, color=INK)
    ax.set_title("Типичные напряжения на логарифмической шкале", pad=10)
    save(f, "voltage-typical-log")


@fig("current-kinescope-beam")
def _():
    f, ax = blank(9.2, 4.6, (0, 11), (0, 5.2))
    # tube body
    ax.add_patch(Polygon([[1.6, 2.1], [1.6, 3.1], [7.3, 4.8], [7.3, 0.4]], fc=SOFT, ec=INK, lw=2))
    ax.add_patch(Rectangle((0.2, 2.15), 1.4, 0.9, fc=PLATE, ec=INK, lw=1.6))
    txt(ax, 0.9, 1.6, "электронная\nпушка", size=9.5)
    ax.plot([7.3, 7.3], [0.4, 4.8], color=INK, lw=4)
    txt(ax, 8.4, 4.4, "экран", size=10.5, ha="left")
    ax.annotate("", xy=(7.4, 4.1), xytext=(8.35, 4.35), arrowprops=dict(arrowstyle="-", color=GREY))
    # deflection system
    ax.add_patch(Rectangle((4.0, 1.6), 0.5, 2.0, fc="none", ec=INK, lw=1.4, ls="--"))
    txt(ax, 4.25, 4.0, "ОС", size=10.5)
    txt(ax, 4.25, 0.75, "отклоняющая\nсистема", size=9.5)
    # beam
    ax.plot([1.6, 7.3], [2.6, 2.6], color=BLUE, lw=2.4)
    for x in (2.3, 3.2, 5.0, 5.9, 6.7):
        charge_sign(ax, x, 2.6, "-", r=0.13)
    arrow(ax, (3.3, 2.05), (5.3, 2.05), color=BLUE, lw=2.0)
    txt(ax, 4.3, 1.8, "", size=8)
    arrow(ax, (5.4, 3.35), (3.2, 3.35), color=RED, lw=2.4)
    txt(ax, 6.2, 3.35, "ток", size=11, color=RED)
    txt(ax, 8.4, 2.6, r"$I = 80$ мкА" + "\nэлектронов за 1 с?", size=10.5, ha="left")
    txt(ax, 5.5, 5.0, "электроны летят к экрану, ток идёт от экрана к пушке", size=9.5, color=GREY)
    save(f, "current-kinescope-beam")


@fig("current-drift-cylinder")
def _():
    f, ax = blank(8.4, 4.2, (0, 10.4), (0, 5.4))
    ax.add_patch(Rectangle((0.6, 1.4), 8.6, 2.2, fc=SOFT, ec=IRON, lw=2.2))
    ax.add_patch(Rectangle((4.4, 1.4), 4.8, 2.2, fc=tint(BLUE, 0.85), ec=BLUE, lw=1.6, alpha=0.6))
    ax.add_patch(Ellipse((9.2, 2.5), 0.6, 2.2, fc=PLATE, ec=INK, lw=1.6))
    rng = np.random.default_rng(6)
    for _i in range(22):
        x, y = rng.uniform(0.9, 8.9), rng.uniform(1.6, 3.4)
        ax.plot(x, y, "o", color=BLUE, ms=3.6)
    for x, y in ((1.4, 2.5), (2.4, 2.0), (3.2, 3.0)):
        arrow(ax, (x, y), (x + 0.55, y), color=BLUE, lw=1.4, scale=9)
    ax.annotate("", xy=(4.4, 0.95), xytext=(9.2, 0.95), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    txt(ax, 6.8, 0.55, r"$\ell = vt$", size=12)
    txt(ax, 9.2, 4.05, r"сечение $S$", size=11)
    txt(ax, 6.8, 4.05, r"$V = \ell S = vtS$", size=11, color=BLUE)
    arrow(ax, (3.2, 4.4), (1.2, 4.4), color=RED, lw=2.2)
    txt(ax, 3.4, 4.4, r"ток $I$", size=11, color=RED, ha="left")
    arrow(ax, (1.2, 5.0), (3.2, 5.0), color=BLUE, lw=2.0)
    txt(ax, 3.4, 5.0, r"скорость $v$ электронов", size=10.5, color=BLUE, ha="left")
    txt(ax, 0.7, 0.6, "электроны из цилиндра $V$\nуспеют пройти сечение\nза время $t$", size=9, ha="left")
    save(f, "current-drift-cylinder")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
