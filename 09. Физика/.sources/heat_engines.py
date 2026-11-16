"""Figures for the note "Тепловые двигатели" (section f10, lessons 130-134).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 heat_engines.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefix engine-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (
    Arc,
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ACCENT, ASH, BLUE, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED  # guides, auxiliary lines and quiet arrows
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
HOT_L = tint(RED, 0.85)
GREEN_L = tint(GREEN, 0.8)
WATER = BLUE
WATER_L = tint(SKY, 0.75)
GOLD = WARM  # the working body, a flame, a spark, a mass
GOLD_L = tint(WARM, 0.6)
STEEL = METAL
LOSS = tint(INK, 0.8)  # heat lost to the surroundings
VAPOUR = VIOLET  # evaporation, as steam is VIOLET in boiling.py
STROKE_GAS = {
    "intake": tint(SKY, 0.7),  # fresh mixture
    "compression": tint(WARM, 0.6),  # compressed mixture
    "power": tint(RED, 0.7),  # burning gas
    "exhaust": tint(INK, 0.8),  # exhaust gas
}


save = saver(OUT)


def axes_grid(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=LIGHT, ec=INK, fs=11, lw=1.6, tc=INK):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            fc=fc,
            ec=ec,
            lw=lw,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc)


def arrow(ax, p1, p2, color=INK, lw=2.0, ms=16, style="-|>", ls="-", rad=0.0, z=5):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            arrowstyle=style,
            mutation_scale=ms,
            color=color,
            lw=lw,
            ls=ls,
            connectionstyle=f"arc3,rad={rad}",
            zorder=z,
        )
    )


def flame(ax, x, y, s=1.0):
    ax.add_patch(
        Polygon(
            [(x - 0.28 * s, y), (x, y + 0.95 * s), (x + 0.28 * s, y)],
            closed=True,
            fc=WARM,
            ec=HOT,
            lw=1.2,
            zorder=4,
        )
    )
    ax.add_patch(
        Polygon(
            [(x - 0.12 * s, y), (x, y + 0.5 * s), (x + 0.12 * s, y)],
            closed=True,
            fc=tint(WARM, 0.6),
            ec="none",
            zorder=5,
        )
    )


# 1. energy flow of a heat engine: Q1 -> A + Q2
def energy_flow():
    fig, ax = blank(9.6, 5.0, (0, 12), (0, 6.2))
    box(ax, 0.2, 2.2, 2.9, 1.7, "Нагреватель\n$T_1$", fc=HOT_L, ec=HOT, fs=12)
    box(ax, 4.5, 2.2, 3.0, 1.7, "Рабочее тело", fc=GOLD_L, ec=GOLD, fs=12)
    box(ax, 8.9, 2.2, 2.9, 1.7, "Охладитель\n$T_2 < T_1$", fc=WATER_L, ec=WATER, fs=12)
    arrow(ax, (3.15, 3.05), (4.45, 3.05), color=HOT, lw=3.2, ms=22)
    ax.text(3.8, 3.35, "$Q_1$", ha="center", fontsize=14, color=HOT)
    arrow(ax, (7.55, 3.05), (8.85, 3.05), color=WATER, lw=3.2, ms=22)
    ax.text(8.2, 3.35, "$Q_2$", ha="center", fontsize=14, color=WATER)
    arrow(ax, (6.0, 2.15), (6.0, 0.95), color=GREEN, lw=3.2, ms=22)
    ax.text(6.35, 1.45, "$A$", fontsize=14, color=GREEN, va="center")
    ax.text(6.0, 0.55, "работа, совершённая двигателем", ha="center", fontsize=10.5, color=GREEN)
    ax.text(
        6.0,
        5.85,
        r"$Q_1 = A + Q_2 \;\Rightarrow\; A = Q_1 - Q_2$",
        ha="center",
        fontsize=13,
    )
    ax.text(
        6.0,
        4.85,
        r"$\eta = \dfrac{A}{Q_1} = \dfrac{Q_1 - Q_2}{Q_1}$",
        ha="center",
        fontsize=13,
        color=INK,
    )
    save(fig, "engine-energy-flow.png")


# 2. cork experiment: chain of energy transformations
def cork_chain():
    fig, ax = blank(6.6, 7.4, (0, 10), (0, 11.4))
    labels = [
        ("Внутренняя энергия топлива\n(газ в горелке)", HOT_L, HOT),
        ("Внутренняя энергия воды растёт,\nвода закипает", HOT_L, HOT),
        ("Пар: внутренняя энергия больше,\nчем у воды при той же температуре", HOT_L, HOT),
        ("Работа силы давления пара", GREEN_L, GREEN),
        ("Кинетическая энергия пробки", GREEN_L, GREEN),
    ]
    notes = [
        "горение, теплопередача",
        "парообразование (кипение)",
        "пар давит на пробку",
        "пробка приходит в движение",
    ]
    ys = [9.5, 7.3, 5.1, 2.9, 0.7]
    for (t, fc, ec), y in zip(labels, ys):
        box(ax, 1.0, y, 8.0, 1.5, t, fc=fc, ec=ec, fs=11)
    for i, n in enumerate(notes):
        y0 = ys[i]
        arrow(ax, (3.2, y0 - 0.05), (3.2, ys[i + 1] + 1.55), color=INK, lw=2.2)
        ax.text(3.6, y0 - 0.35, n, fontsize=10, va="center", color=NOTE)
    ax.text(9.6, 6.3, "внутренняя\nэнергия", rotation=90, ha="center", va="center", fontsize=9.5, color=HOT)
    ax.text(9.6, 1.9, "механическая\nэнергия", rotation=90, ha="center", va="center", fontsize=9.5, color=GREEN)
    save(fig, "engine-cork-chain.png")


# 3. cyclic machine: three stages with balls
def cycle_stages():
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.8))
    titles = [
        "1. Шарик на нижней полке",
        "2. Нагрев: газ расширяется",
        "3. Охлаждение: поршень вниз",
    ]
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 6)
        ax.set_ylim(-1.2, 6.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[k], fontsize=11.5)
        piston_y = 1.4 if k != 1 else 2.6
        cx = 3.0
        ax.add_patch(Rectangle((cx - 0.8, 0), 1.6, 3.4, fc="none", ec=INK, lw=2))
        ax.add_patch(Rectangle((cx - 0.8, 0), 1.6, piston_y, fc=WATER_L if k != 1 else HOT_L, ec="none"))
        ax.add_patch(Rectangle((cx - 0.8, piston_y), 1.6, 0.22, fc=STEEL, ec=INK, lw=1))
        rod_top = piston_y + 1.9
        ax.plot([cx, cx], [piston_y + 0.22, rod_top], color=INK, lw=2.5)
        ax.plot([cx - 0.55, cx + 0.55], [rod_top, rod_top], color=INK, lw=3)
        # shelves: low on the left, high on the right
        ax.plot([0.2, 1.7], [3.5, 3.5], color=INK, lw=2.5)
        ax.plot([4.3, 5.8], [4.72, 4.72], color=INK, lw=2.5)
        if k == 0:
            ax.add_patch(Circle((cx, rod_top + 0.22), 0.22, fc=GOLD, ec=INK, lw=1.2))
            ax.add_patch(Circle((1.0, 3.72), 0.22, fc=GOLD, ec=INK, lw=1.2))
            ax.text(cx, -0.8, "рабочее тело (воздух)", ha="center", fontsize=10, color=WATER)
        if k == 1:
            ax.add_patch(Circle((cx + 0.6, rod_top + 0.22), 0.22, fc=GOLD, ec=INK, lw=1.2))
            arrow(ax, (cx + 0.9, rod_top + 0.4), (4.9, 4.72), color=GREEN, lw=1.6, ms=12)
            ax.add_patch(Circle((5.2, 4.72), 0.22, fc=GOLD, ec=INK, lw=1.2))
            # The flame is 0.76 high: it spans y = -0.95 ... -0.19, under the cylinder bottom (y = 0)
            flame(ax, cx, -0.95, 0.8)
            ax.text(cx + 1.05, -0.75, "нагреватель\n$T_1$", fontsize=10, color=HOT, va="center")
            arrow(ax, (cx + 1.2, 1.4), (cx + 1.2, 2.4), color=GREEN, lw=2, ms=12)
        if k == 2:
            ax.add_patch(Circle((5.2, 4.72), 0.22, fc=GOLD, ec=INK, lw=1.2))
            ax.add_patch(Rectangle((0.3, -0.9), 5.4, 1.4, fc=WATER_L, ec=WATER, lw=1.5, zorder=0))
            ax.text(3.0, -1.05, "охладитель $T_2 < T_1$", ha="center", fontsize=10, color=WATER, va="top")
            arrow(ax, (cx + 1.2, 2.6), (cx + 1.2, 1.6), color=WATER, lw=2, ms=12)
    save(fig, "engine-cycle-stages.png")


# 4. efficiency against the share of heat lost to the cooler
def eta_vs_loss():
    fig, ax = axes_grid(7.2, 4.4)
    x = np.linspace(0, 1, 100)
    ax.plot(x, (1 - x) * 100, color=INK, lw=2.4)
    ax.axhspan(20, 40, color=GREEN_L, zorder=0)
    ax.text(0.02, 30, "типичные современные\nдвигатели, $\\eta = 20 \\ldots 40\\ \\%$", ha="left", va="center", fontsize=10, color=GREEN)
    ax.xaxis.set_major_formatter(lambda v, _: num(v, None))
    ax.plot([0], [100], "o", mfc=PAPER, mec=HOT, ms=9, mew=2, zorder=5)
    ax.annotate(
        "$Q_2 = 0$, $\\eta = 1$:\nнедостижимо в цикле",
        (0, 100),
        (0.18, 88),
        fontsize=10,
        color=HOT,
        arrowprops=dict(arrowstyle="->", color=HOT),
    )
    ax.set_xlim(-0.02, 1)
    ax.set_ylim(0, 108)
    ax.set_xlabel(r"доля теплоты, отданной охладителю, $Q_2 / Q_1$")
    ax.set_ylabel(r"$\eta$, %")
    ax.set_title(r"$\eta = 1 - Q_2 / Q_1$")
    save(fig, "engine-eta-vs-loss.png")


# 5. Newcomen atmospheric engine, two phases
def newcomen():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.0))
    titles = [
        "Пар из котла поднимает поршень",
        "Впрыск холодной воды: пар конденсируется",
    ]
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 12.8)
        ax.set_ylim(-0.5, 9.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[k], fontsize=11.5)
        # boiler
        ax.add_patch(Rectangle((0.3, 0.3), 2.8, 2.0, fc=WATER_L, ec=INK, lw=2))
        ax.text(1.7, 1.15, "котёл", ha="center", fontsize=10)
        flame(ax, 1.7, -0.45, 0.6)
        # pipe to cylinder with tap
        ax.plot([2.4, 2.4, 4.6], [2.3, 3.0, 3.0], color=INK, lw=2.5)
        ax.plot([2.4, 2.4], [2.3, 3.0], color=INK, lw=2.5)
        ax.add_patch(Circle((3.3, 3.0), 0.16, fc=GOLD, ec=INK, zorder=6))
        ax.text(3.3, 3.4, "кран", ha="center", fontsize=9)
        # cylinder, open at the top: the atmosphere presses on the piston from above
        ax.plot([4.6, 4.6, 6.6, 6.6], [6.6, 3.0, 3.0, 6.6], color=INK, lw=2)
        piston_y = 5.4 if k == 0 else 3.6
        ax.add_patch(Rectangle((4.6, 3.0), 2.0, piston_y - 3.0, fc=HOT_L if k == 0 else WATER_L, ec="none"))
        ax.add_patch(Rectangle((4.6, piston_y), 2.0, 0.25, fc=STEEL, ec=INK, lw=1))
        # rocker beam: the piston end moves by 1.8 (the piston travel), so the tilt is 0.9 at each end and the piston rod keeps one length
        tilt = 0.9 if k == 0 else -0.9
        slope = -2 * tilt / 6.0

        def beam_y(x):
            return 7.6 + tilt + slope * (x - 5.6)

        ax.plot([5.6, 5.6], [piston_y + 0.25, beam_y(5.6)], color=INK, lw=2)
        ax.plot([5.6, 11.6], [beam_y(5.6), beam_y(11.6)], color=INK, lw=4)
        ax.plot([8.6, 8.6], [7.6, 6.4], color=INK, lw=3)
        ax.add_patch(Polygon([(8.2, 6.4), (9.0, 6.4), (8.6, 7.4)], fc=METAL, ec=INK))
        # pump rod on the right
        # constant rod length 4.4; the box is tall enough to hold the lower end of the rod in both positions (2.4 ... 4.0)
        ax.plot([11.3, 11.3], [beam_y(11.3), beam_y(11.3) - 4.4], color=INK, lw=2)
        ax.add_patch(Rectangle((10.5, 0.4), 1.6, 4.2, fc=WATER_L, ec=INK, lw=2))
        ax.text(11.3, 1.2, "насос\nшахты", ha="center", fontsize=9)
        if k == 0:
            arrow(ax, (5.6, 4.0), (5.6, 5.0), color=HOT, lw=2.5, ms=16)
            ax.text(6.75, 4.2, "пар", color=HOT, fontsize=11)
            ax.text(5.6, 9.15, "поршень вверх, насос опускается", ha="center", fontsize=9.5, color=NOTE)
        else:
            ax.text(6.75, 3.9, "холодная вода", color=WATER, fontsize=10)
            for dx in (-0.5, 0, 0.5):
                ax.add_patch(Circle((5.6 + dx, 3.25), 0.1, fc=WATER, ec="none"))
            # the arrows stand beside the piston rod (x = 5.6) and press on the piston top at y = 3.85
            arrow(ax, (5.0, 7.4), (5.0, 4.2), color=GREEN, lw=2.5, ms=16)
            arrow(ax, (6.2, 6.4), (6.2, 4.2), color=GREEN, lw=2.5, ms=16)
            ax.text(4.1, 7.6, "$p_{\\mathrm{атм}}$", color=GREEN, fontsize=12, ha="center")
            ax.text(5.6, 9.15, "поршень вниз, насос поднимается", ha="center", fontsize=9.5, color=NOTE)
    save(fig, "engine-newcomen.png")


# 6. Watt double-acting steam engine with slide valve
def watt():
    fig, axes = plt.subplots(2, 1, figsize=(11.6, 9.2))
    cases = [
        dict(title="Поршень идёт вправо: пар слева, отработавший пар справа уходит в атмосферу", va=1.0, px=5.0, dirn=1),
        dict(title="Поршень идёт влево: золотники сдвинулись, пар справа", va=3.0, px=5.0, dirn=-1),  # crank at 120 and 240 degrees gives one crosshead position, so one piston position (the rod keeps its length)
    ]
    for ax, c in zip(axes, cases):
        ax.set_xlim(-0.2, 17.4)
        ax.set_ylim(-1.6, 7.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(c["title"], fontsize=11.5)
        # main cylinder
        ax.add_patch(Rectangle((1.2, 0.2), 7.6, 1.8, fc="none", ec=INK, lw=2))
        px = c["px"]
        ax.add_patch(Rectangle((px - 0.3, 0.2), 0.6, 1.8, fc=STEEL, ec=INK, lw=1.2, zorder=4))
        ax.plot([px, 10.6], [1.1, 1.1], color=INK, lw=3)
        ax.text(px, -0.35, "поршень", ha="center", fontsize=9.5)
        ax.text(2.5, -0.35, "цилиндр", ha="center", fontsize=9.5)
        ax.text(9.7, 1.55, "шток", ha="center", fontsize=9.5)
        # valve chest
        ax.add_patch(Rectangle((0.0, 4.0), 10.0, 1.2, fc="none", ec=INK, lw=2))
        # ports from chest down to cylinder ends
        for xp in (2.5, 7.5):
            ax.plot([xp - 0.4, xp - 0.4], [2.0, 4.0], color=INK, lw=2)
            ax.plot([xp + 0.4, xp + 0.4], [2.0, 4.0], color=INK, lw=2)
            ax.add_patch(Rectangle((xp - 0.4, 2.0), 0.8, 2.0, fc=HOT_L if False else PAPER, ec="none", zorder=0))
        # valve pistons
        a = c["va"]
        for xs in (a, a + 5.0):
            ax.add_patch(Rectangle((xs, 4.05), 1.0, 1.1, fc=STEEL, ec=INK, lw=1.2, zorder=4))
        ax.plot([a, a + 6.0], [4.6, 4.6], color=INK, lw=1.2, zorder=3)
        ax.plot([a + 1.0, a + 5.0], [4.6, 4.6], color=INK, lw=3, zorder=3)
        # steam inlet
        ax.plot([4.6, 4.6], [5.2, 6.4], color=INK, lw=2)
        ax.plot([5.4, 5.4], [5.2, 6.4], color=INK, lw=2)
        arrow(ax, (5.0, 6.8), (5.0, 5.35), color=HOT, lw=3, ms=18)
        ax.text(5.5, 6.65, "пар", color=HOT, fontsize=11, va="center")
        # steam region
        ax.add_patch(Rectangle((a + 1.0, 4.05), 4.0, 1.1, fc=HOT_L, ec="none", zorder=2))
        if c["dirn"] == 1:
            ax.add_patch(Rectangle((2.1, 2.0), 0.8, 2.0, fc=HOT_L, ec="none", zorder=1))
            ax.add_patch(Rectangle((1.2, 0.2), px - 0.3 - 1.2, 1.8, fc=HOT_L, ec="none", zorder=1))
            arrow(ax, (2.5, 3.9), (2.5, 2.4), color=HOT, lw=2.5, ms=14)
            arrow(ax, (px - 1.0, 1.1), (px - 0.5, 1.1), color=HOT, lw=2.5, ms=14)
            arrow(ax, (px + 0.7, 1.6), (px + 1.7, 1.6), color=GREEN, lw=2.5, ms=14)
            arrow(ax, (7.5, 2.3), (7.5, 3.9), color=GREY, lw=2.2, ms=14)
            arrow(ax, (7.5, 4.6), (10.9, 4.6), color=GREY, lw=2.2, ms=14, z=6)
            ax.text(10.95, 4.6, "выхлоп в атмосферу", fontsize=9.5, va="center", color=NOTE)
        else:
            ax.add_patch(Rectangle((7.1, 2.0), 0.8, 2.0, fc=HOT_L, ec="none", zorder=1))
            ax.add_patch(Rectangle((px + 0.3, 0.2), 8.8 - px - 0.3, 1.8, fc=HOT_L, ec="none", zorder=1))
            arrow(ax, (7.5, 3.9), (7.5, 2.4), color=HOT, lw=2.5, ms=14)
            arrow(ax, (px + 1.0, 1.1), (px + 0.5, 1.1), color=HOT, lw=2.5, ms=14)
            arrow(ax, (px - 0.7, 1.6), (px - 1.7, 1.6), color=GREEN, lw=2.5, ms=14)
            arrow(ax, (2.5, 2.3), (2.5, 3.9), color=GREY, lw=2.2, ms=14)
            arrow(ax, (2.5, 4.6), (-0.15, 4.6), color=GREY, lw=2.2, ms=14, z=6)
            ax.text(0.05, 5.6, "выхлоп в атмосферу", fontsize=9.5, va="center", color=NOTE)
        ax.text(8.0, 5.7, "золотниковый механизм", ha="left", fontsize=9.5)
        # flywheel with crank
        wx, wy, wr = 14.3, 1.1, 2.6
        ax.add_patch(Circle((wx, wy), wr, fc="none", ec=INK, lw=3))
        ax.add_patch(Circle((wx, wy), 0.15, fc=INK))
        ang = np.deg2rad(120 if c["dirn"] == 1 else 240)
        cxp, cyp = wx + 1.2 * np.cos(ang), wy + 1.2 * np.sin(ang)
        ax.plot([wx, cxp], [wy, cyp], color=INK, lw=4)
        ax.plot([10.6, cxp], [1.1, cyp], color=INK, lw=2.5)
        ax.add_patch(Circle((10.6, 1.1), 0.14, fc=PAPER, ec=INK, zorder=6))
        ax.add_patch(Circle((cxp, cyp), 0.14, fc=PAPER, ec=INK, zorder=6))
        ax.text(wx, wy - wr - 0.45, "маховик", ha="center", fontsize=9.5)
        mx, my = (10.6 + cxp) / 2, (1.1 + cyp) / 2
        # the flywheel rim starts at x = 11.7, so the label stands left of it
        ax.text(11.0, 1.1 + (0.45 if c["dirn"] == 1 else -0.75), "шатун", fontsize=9.5, ha="center")
        ax.text(wx + 0.35, wy - 0.6 if c["dirn"] == 1 else wy + 0.35, "кривошип", fontsize=9, ha="left")
        arrow(ax, (wx - 1.0, wy + 1.95), (wx + 1.0, wy + 1.95), color=GREY, lw=1.8, ms=12, rad=-0.35)
    save(fig, "engine-watt-double-action.png")


# 7. steam turbine: wheel with nozzles, multi-stage scheme
def turbine():
    fig, axes = plt.subplots(1, 3, figsize=(16.0, 4.6), gridspec_kw={"width_ratios": [1, 1, 2.3]})
    # simple and multi-nozzle wheel
    for k, ax in enumerate(axes[:2]):
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.4, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Одно сопло" if k == 0 else "Четыре сопла", fontsize=11.5)
        ax.add_patch(Circle((0, 0), 2.0, fc="none", ec=INK, lw=2.5))
        ax.add_patch(Circle((0, 0), 0.12, fc=INK))
        for a in np.arange(0, 360, 20):
            r = np.deg2rad(a)
            x0, y0 = 2.0 * np.cos(r), 2.0 * np.sin(r)
            r2 = np.deg2rad(a + 35)
            x1, y1 = 2.6 * np.cos(r2), 2.6 * np.sin(r2)
            ax.plot([x0, x1], [y0, y1], color=STEEL, lw=2.2)
        nozzle_angles = [180 - 30] if k == 0 else [150, 60, -30, -120]
        for na in nozzle_angles:
            r = np.deg2rad(na)
            # The jet leaves the nozzle along a tangent-leaning line in the direction of rotation (clockwise, so the polar angle falls)
            bx, by = 2.75 * np.cos(r), 2.75 * np.sin(r)
            ex, ey = 2.25 * np.cos(r - 0.45), 2.25 * np.sin(r - 0.45)
            ux, uy = (ex - bx), (ey - by)
            n = np.hypot(ux, uy)
            ux, uy = ux / n, uy / n
            # the nozzle is a segment on the same line, behind the start of the jet
            ax.plot([bx - 0.8 * ux, bx], [by - 0.8 * uy, by], color=INK, lw=6, solid_capstyle="butt")
            arrow(ax, (bx, by), (ex, ey), color=HOT, lw=2.6, ms=14)
        arrow(ax, (0.9, 0.8), (0.9, -0.8), color=GREEN, lw=2.2, ms=14, rad=-0.6)
        ax.text(0, -3.35, "сопло — трубка, из которой бьёт струя пара" if k == 0 else "мощность растёт с числом сопел", ha="center", fontsize=9.5, color=NOTE)
    # multi-stage side view
    ax = axes[2]
    ax.set_xlim(0, 15)
    ax.set_ylim(-3.6, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Многоступенчатая турбина (вид сбоку)", fontsize=11.5)
    ax.add_patch(Rectangle((1.0, -0.25), 13.0, 0.5, fc=STEEL, ec=INK, lw=1.5))  # shaft
    ax.plot([1.0, 14.0], [2.7, 2.7], color=INK, lw=2.5)
    ax.plot([1.0, 14.0], [-2.7, -2.7], color=INK, lw=2.5)
    ax.text(14.1, 0, "вал", fontsize=9.5, va="center")
    ax.set_ylim(-3.9, 4.1)
    xs_rotor = [3.0, 7.0, 11.0]
    xs_stator = [5.0, 9.0]
    for x in xs_rotor:
        for sgn in (1, -1):
            ax.add_patch(Rectangle((x - 0.15, 0.25 if sgn > 0 else -2.2), 0.3, 1.95, fc=WATER, ec=INK, lw=1))
            ax.add_patch(Rectangle((x - 0.5, 2.1 if sgn > 0 else -2.55), 1.0, 0.4, fc=WATER_L, ec=INK, lw=1))
    for x in xs_stator:
        for sgn in (1, -1):
            ax.add_patch(Rectangle((x - 0.1, 0.9 if sgn > 0 else -2.7), 0.2, 1.8, fc=METAL, ec=INK, lw=1))
    arrow(ax, (0.1, 1.5), (2.3, 1.5), color=HOT, lw=3.2, ms=18)
    arrow(ax, (0.1, -1.5), (2.3, -1.5), color=HOT, lw=3.2, ms=18)
    ax.text(0.1, 1.9, "пар из котла", color=HOT, fontsize=9.5, ha="left", va="bottom")
    arrow(ax, (12.0, 1.5), (14.6, 1.5), color=GREY, lw=2.5, ms=16)
    ax.text(14.6, 0.9, "отработавший пар", color=NOTE, fontsize=9, ha="right", va="top")
    for x, t in zip([3.0, 5.0, 7.0, 9.0, 11.0], ["колесо", "статор", "колесо", "статор", "колесо"]):
        ax.text(x, -3.05, t, ha="center", fontsize=9)
    ax.text(8.0, -3.6, "колёса вращаются, статоры неподвижны и направляют пар на следующее колесо", ha="center", fontsize=9, color=NOTE)
    ax.annotate("", xy=(13.4, 3.05), xytext=(1.6, 3.05), arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(7.5, 3.3, "давление пара падает", ha="center", fontsize=9, color=NOTE)
    save(fig, "engine-turbine-scheme.png")


# 8. efficiency of engines
def efficiency_compare():
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    rows = [
        ("Паровая машина Уатта", 1, 8, "1…8"),
        ("Двигатель Ленуара", 0, 3.3, "3,3"),
        ("Двигатель Отто", 0, 24, "24"),
        ("Дизель грузовика (задача 31.30)", 0, 39, "39"),
        ("Паровая турбина, выхлоп в атмосферу", 0, 40, "до 40"),
        ("Паровая турбина с конденсацией пара", 0, 50, "до 50"),
    ]
    steam = {0, 4, 5}
    for i, (name, lo, hi, lab) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, hi - lo, left=lo, color=WATER if i in steam else GOLD, height=0.55)
        ax.text(hi + 0.8, y, lab, va="center", fontsize=10.5)
    ax.legend(
        [Rectangle((0, 0), 1, 1, color=WATER), Rectangle((0, 0), 1, 1, color=GOLD)],
        ["паровые двигатели", "двигатели внутреннего сгорания"],
        frameon=False,
        loc="center right",  # upper right collides with the band label, lower right with the bottom bar; the middle right is free
    )
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    for lbl in ax.get_yticklabels():
        keep_dots(lbl)
    ax.axvspan(20, 40, color=GREEN_L, zorder=0, alpha=0.7)
    # The band sits left of the upper-right legend; its label says "typical", the best engines are above 40 %
    ax.text(24, len(rows) - 0.35, "типичные современные\nдвигатели", ha="center", fontsize=9, color=GREEN, va="bottom")
    ax.set_xlim(0, 58)
    ax.set_ylim(-0.6, len(rows) + 0.5)
    ax.set_xlabel(r"$\eta$, %")
    ax.set_title("КПД тепловых двигателей")
    save(fig, "engine-efficiency-compare.png")


# 9. carburetor
def carburetor():
    fig = plt.figure(figsize=(9.2, 6.6))
    ax = fig.add_axes([0.02, 0.36, 0.96, 0.62])
    ax.set_xlim(0, 12)
    ax.set_ylim(-1.0, 5.0)
    ax.set_aspect("equal")
    ax.axis("off")
    top = [(0.5, 3.8), (3.5, 3.8), (5.0, 3.0), (7.0, 3.0), (8.5, 3.8), (11.5, 3.8)]
    bot = [(0.5, 1.2), (3.5, 1.2), (5.0, 2.0), (7.0, 2.0), (8.5, 1.2), (11.5, 1.2)]
    ax.plot(*zip(*top), color=INK, lw=2.6)
    ax.plot(*zip(*bot), color=INK, lw=2.6)
    for y in (1.6, 2.5, 3.4):
        arrow(ax, (0.0, y), (1.3, y), color=WATER, lw=2, ms=13)
    ax.text(0.0, 4.2, "воздух из\nатмосферы, $p_{\\mathrm{атм}}$", fontsize=10, color=WATER)
    for y in (1.9, 2.5, 3.1):
        arrow(ax, (10.4, y), (11.9, y), color=GREEN, lw=2, ms=13)
    ax.text(11.9, 4.2, "к ДВС", fontsize=10, color=GREEN, ha="right")
    ax.text(6.0, 3.35, "узкая часть: воздух быстрее", ha="center", fontsize=9.5, color=NOTE)
    # petrol vessel and jet tube
    # open float chamber: the air above the petrol is the atmosphere
    ax.plot([4.5, 4.5, 7.5, 7.5], [0.3, -0.9, -0.9, 0.3], color=INK, lw=2)
    ax.add_patch(Rectangle((4.5, -0.9), 3.0, 0.8, fc=GOLD_L, ec="none"))
    ax.text(6.8, -0.5, "бензин", ha="center", fontsize=10.5)
    ax.plot([5.9, 5.9], [-0.4, 2.0], color=INK, lw=2.4)
    ax.plot([6.1, 6.1], [-0.4, 2.0], color=INK, lw=2.4)
    ax.add_patch(Rectangle((5.9, -0.4), 0.2, 2.4, fc=GOLD_L, ec="none", zorder=0))
    ax.annotate("жиклёр: отверстие\nдиаметром доли мм", (6.05, 2.0), (8.3, 0.1), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=HOT), color=HOT)
    arrow(ax, (6.0, 2.1), (6.0, 2.75), color=GOLD, lw=2.4, ms=12)
    ax.text(4.3, 0.75, "$p_{\\mathrm{атм}}$ на поверхности\nбензина", fontsize=9.5, color=WATER, ha="right", va="center")
    arrow(ax, (5.0, 0.75), (5.0, -0.05), color=WATER, lw=1.5, ms=10)
    arrow(ax, (7.0, 0.75), (7.0, -0.05), color=WATER, lw=1.5, ms=10)
    # pressure profile
    ax2 = fig.add_axes([0.12, 0.08, 0.76, 0.22])
    x = np.linspace(0.5, 11.5, 300)
    p = 1 - 0.35 * np.exp(-((x - 6.0) / 1.5) ** 2)
    ax2.plot(x, p, color=INK, lw=2.4)
    ax2.axhline(1, color=WATER, ls="--", lw=1.4)
    ax2.text(11.5, 1.02, "$p_{\\mathrm{атм}}$", color=WATER, ha="right", va="bottom", fontsize=10.5)
    ax2.set_xlim(0.5, 11.5)
    ax2.set_ylim(0.55, 1.12)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_ylabel("давление\nв потоке")
    ax2.annotate("в сужении $p < p_{\\mathrm{атм}}$:\nбензин поднимается по трубке", (6.0, 0.65), (8.6, 0.72), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=HOT), color=HOT)
    save(fig, "engine-carburetor.png")


# helpers for cylinder drawings
CRANK_R = 1.0
ROD_L = 2.8


def piston_pin_y(theta_deg):
    t = np.deg2rad(theta_deg)
    return CRANK_R * np.cos(t) + np.sqrt(ROD_L**2 - (CRANK_R * np.sin(t)) ** 2)


def valve(ax, x, open_, color_open=GREEN):
    head = 4.6
    if open_:
        ax.plot([x, x], [head + 0.8, head - 0.05], color=INK, lw=2)
        ax.add_patch(Rectangle((x - 0.32, head - 0.22), 0.64, 0.14, fc=color_open, ec=INK, lw=1, zorder=6))
    else:
        ax.plot([x, x], [head + 0.8, head + 0.0], color=INK, lw=2)
        ax.add_patch(Rectangle((x - 0.32, head - 0.1), 0.64, 0.14, fc=METAL, ec=INK, lw=1, zorder=6))


def cylinder(ax, cx, theta, gas, intake, exhaust, spark=False, labels=False):
    pin = piston_pin_y(theta)
    top = pin + 0.45
    # The flywheel circle (radius 1.35) reaches y = 1.35, so the walls start above it at y = 1.5
    ax.add_patch(Rectangle((cx - 1.2, 1.5), 2.4, 3.1, fc=PAPER, ec="none", zorder=0))
    ax.add_patch(Rectangle((cx - 1.15, top), 2.3, 4.6 - top, fc=gas, ec="none", zorder=1))
    ax.plot([cx - 1.2, cx - 1.2], [1.5, 4.6], color=INK, lw=2.6, zorder=3)
    ax.plot([cx + 1.2, cx + 1.2], [1.5, 4.6], color=INK, lw=2.6, zorder=3)
    ax.plot([cx - 1.2, cx + 1.2], [4.6, 4.6], color=INK, lw=2.6, zorder=3)
    # ports
    ax.plot([cx - 0.95, cx - 0.95], [4.6, 5.3], color=INK, lw=2)
    ax.plot([cx - 0.25, cx - 0.25], [4.6, 5.3], color=INK, lw=2)
    ax.plot([cx + 0.25, cx + 0.25], [4.6, 5.3], color=INK, lw=2)
    ax.plot([cx + 0.95, cx + 0.95], [4.6, 5.3], color=INK, lw=2)
    # piston
    ax.add_patch(Rectangle((cx - 1.15, pin - 0.15), 2.3, 0.6, fc=STEEL, ec=INK, lw=1.4, zorder=4))
    for dy in (0.3, 0.38):
        ax.plot([cx - 1.15, cx + 1.15], [pin + dy, pin + dy], color=INK, lw=0.8, zorder=5)
    # crank and rod
    t = np.deg2rad(theta)
    px, py = cx + CRANK_R * np.sin(t), CRANK_R * np.cos(t)
    ax.add_patch(Circle((cx, 0), 1.35, fc="none", ec=GREY, lw=2, zorder=2))
    ax.plot([cx, px], [0, py], color=INK, lw=4, zorder=5)
    ax.plot([cx, px], [pin, py], color=INK, lw=2.8, zorder=5)
    ax.add_patch(Circle((cx, 0), 0.12, fc=INK, zorder=6))
    ax.add_patch(Circle((px, py), 0.1, fc=PAPER, ec=INK, zorder=7))
    valve(ax, cx - 0.6, intake)
    valve(ax, cx + 0.6, exhaust, color_open=HOT)
    # spark plug
    ax.plot([cx, cx], [4.6, 5.5], color=INK, lw=4, zorder=2)
    ax.add_patch(Rectangle((cx - 0.12, 4.75), 0.24, 0.5, fc=GOLD, ec=INK, lw=1, zorder=6))
    if spark:
        ax.plot([cx - 0.28, cx + 0.05, cx - 0.1, cx + 0.3], [4.32, 4.1, 3.85, 3.6], color=ACCENT, lw=2.6, zorder=7)
    return top


# 10. ICE anatomy
def ice_anatomy():
    fig, ax = blank(9.2, 7.0, (-4.5, 6.2), (-1.8, 6.4))
    cx = 0.0
    cylinder(ax, cx, 30, WATER_L, intake=False, exhaust=False)
    top_vmt = piston_pin_y(0) + 0.45
    top_nmt = piston_pin_y(180) + 0.45
    ax.plot([cx - 1.9, cx - 1.3], [top_vmt, top_vmt], color=GREY, ls="--", lw=1)
    ax.text(cx - 2.0, top_vmt, "ВМТ", ha="right", va="center", fontsize=10, color=NOTE)
    ax.plot([cx - 1.9, cx - 1.3], [top_nmt, top_nmt], color=GREY, ls="--", lw=1)
    ax.text(cx - 2.0, top_nmt, "НМТ", ha="right", va="center", fontsize=10, color=NOTE)
    ax.annotate("", xy=(cx - 1.65, top_vmt), xytext=(cx - 1.65, top_nmt), arrowprops=dict(arrowstyle="<->", color=GREY))
    ax.text(cx - 2.0, (top_vmt + top_nmt) / 2, "ход\nпоршня", ha="right", va="center", fontsize=9, color=NOTE)
    ax.annotate("впускной клапан\n(от карбюратора)", (cx - 0.6, 5.15), (-4.3, 5.9), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("выпускной клапан\n(к выхлопной трубе)", (cx + 0.6, 5.15), (2.0, 5.9), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("свеча зажигания\n(к катушке, около 10 000 В)", (cx, 5.5), (-1.0, 6.5), fontsize=10, ha="center", arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("поршень с кольцами", (cx + 1.15, 3.55), (2.4, 3.6), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("шатун", (cx + 0.15, 1.2), (2.4, 1.6), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("кривошип", (cx + 0.5, 0.45), (2.4, 0.3), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("маховик", (cx + 1.0, -0.9), (2.4, -1.2), fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
    save(fig, "engine-ice-anatomy.png")


# 11. four strokes
def four_strokes():
    fig, axes = plt.subplots(1, 4, figsize=(15.0, 6.6))
    specs = [
        dict(name="1. Впуск", theta=60, gas=STROKE_GAS["intake"], intake=True, exhaust=False, spark=False,
             pdir=-1, p="$p \\approx 0{,}9$ атм", t="$t \\approx 50\\ ^\\circ$C", note="поршень вниз,\nсмесь засасывается"),
        dict(name="2. Сжатие", theta=300, gas=STROKE_GAS["compression"], intake=False, exhaust=False, spark=False,
             pdir=1, p="$p$: $0{,}9 \\to 9$ атм", t="$t$: $50 \\to 300\\ ^\\circ$C", note="поршень вверх,\nсмесь сжимается"),
        dict(name="3. Рабочий ход", theta=60, gas=STROKE_GAS["power"], intake=False, exhaust=False, spark=True,
             pdir=-1, p="$p$: $35 \\to 6$ атм", t="$t$: $2500 \\to 1400\\ ^\\circ$C", note="после искры газ\nтолкает поршень вниз"),
        dict(name="4. Выпуск", theta=300, gas=STROKE_GAS["exhaust"], intake=False, exhaust=True, spark=False,
             pdir=1, p="$p \\approx 1{,}1$ атм", t="$t \\approx 1400\\ ^\\circ$C и ниже", note="поршень вверх,\nвыхлоп через клапан"),
    ]
    for ax, s in zip(axes, specs):
        ax.set_xlim(-2.4, 2.4)
        ax.set_ylim(-3.2, 6.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(s["name"], fontsize=12.5, pad=6)
        cylinder(ax, 0, s["theta"], s["gas"], s["intake"], s["exhaust"], s["spark"])
        y0 = 3.0
        if s["pdir"] < 0:
            arrow(ax, (-1.85, y0 + 0.6), (-1.85, y0 - 0.6), color=GREEN, lw=2.8, ms=16)
        else:
            arrow(ax, (-1.85, y0 - 0.6), (-1.85, y0 + 0.6), color=GREEN, lw=2.8, ms=16)
        ax.text(-1.0, 6.05, "впуск", fontsize=9, ha="center", color=GREEN if s["intake"] else NOTE)
        ax.text(1.0, 6.05, "выпуск", fontsize=9, ha="center", color=HOT if s["exhaust"] else NOTE)
        ax.text(-1.0, 5.75, "открыт" if s["intake"] else "закрыт", fontsize=9, ha="center", color=GREEN if s["intake"] else NOTE)
        ax.text(1.0, 5.75, "открыт" if s["exhaust"] else "закрыт", fontsize=9, ha="center", color=HOT if s["exhaust"] else NOTE)
        ax.text(0, -1.95, s["note"], ha="center", va="top", fontsize=9.5)
        ax.text(0, -2.85, s["p"] + "\n" + s["t"], ha="center", va="top", fontsize=10, color=INK)
    fig.subplots_adjust(wspace=0.05)
    save(fig, "engine-four-strokes.png")


# 12. pressure and temperature during the cycle (schematic from the lecture table)
def pt_cycle():
    fig, (axp, axt) = plt.subplots(2, 1, figsize=(8.6, 6.2), sharex=True)
    xs = [0, 180, 180, 360, 360, 540, 540, 720]
    p = [0.9, 0.9, 0.9, 9, 35, 6, 1.1, 1.1]
    t = [50, 50, 50, 300, 2500, 1400, 1400, 1400]
    names = ["впуск", "сжатие", "рабочий ход", "выпуск"]
    colors = [WATER_L, GOLD_L, HOT_L, LIGHT]
    for ax, ys, unit, col in ((axp, p, "$p$, атм", INK), (axt, t, "$t$, $^\\circ$C", HOT)):
        for i in range(4):
            ax.axvspan(180 * i, 180 * (i + 1), color=colors[i], zorder=0)
        ax.plot(xs, ys, color=col, lw=2.6, marker="o", ms=5)
        ax.set_ylabel(unit)
        ax.grid(True, color=PAPER, lw=0.8)
    for i, n in enumerate(names):
        axp.text(180 * i + 90, 37.5, n, ha="center", fontsize=10.5, va="bottom")
    axp.set_ylim(0, 42)
    axt.set_ylim(0, 2900)
    axt.set_xlim(0, 720)
    axt.set_xticks([0, 180, 360, 540, 720])
    axt.set_xlabel("угол поворота маховика, градусы (полный цикл — два оборота)")
    axp.annotate("искра у ВМТ", (360, 33), (215, 30), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=INK))
    axp.annotate("открылся выпускной\nклапан", (540, 3.5), (565, 14), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=INK))
    axp.set_title("Цикл четырёхтактного двигателя: значения таблицы урока", fontsize=12)
    fig.subplots_adjust(hspace=0.08)
    save(fig, "engine-otto-pt-cycle.png")


# 13. four cylinders
def four_cylinders():
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    order = ["Впуск", "Сжатие", "Рабочий ход", "Выпуск"]
    cols = [WATER_L, GOLD_L, HOT_L, LIGHT]
    for j in range(4):
        for s in range(4):
            k = (s + j) % 4
            ax.add_patch(Rectangle((s, 3 - j), 1, 1, fc=cols[k], ec=PAPER, lw=3))
            ax.text(s + 0.5, 3 - j + 0.5, order[k], ha="center", va="center", fontsize=10, fontweight="bold" if k == 2 else "normal")
            if k == 2:
                ax.add_patch(Rectangle((s + 0.04, 3 - j + 0.04), 0.92, 0.92, fc="none", ec=HOT, lw=2.2))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5])
    ax.set_xticklabels(["такт 1", "такт 2", "такт 3", "такт 4"])
    ax.set_yticks([0.5, 1.5, 2.5, 3.5])
    ax.set_yticklabels(["цилиндр 4", "цилиндр 3", "цилиндр 2", "цилиндр 1"])
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("В каждом такте ровно один цилиндр совершает рабочий ход", fontsize=11.5)
    save(fig, "engine-four-cylinders.png")


# 14. rubber engine
def rubber_engine():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.0))
    titles = ["Резина холодная: центр тяжести на оси", "Резина у лампы укоротилась"]
    for k, ax in enumerate(axes):
        ax.set_xlim(-3.6, 4.6)
        ax.set_ylim(-4.0, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[k], fontsize=11, pad=10)
        shift = np.array([0.0, 0.0]) if k == 0 else np.array([-0.55, 0.0])
        ax.add_patch(Circle(shift, 2.6, fc="none", ec=INK, lw=3))
        for a in range(0, 360, 30):
            r = np.deg2rad(a)
            end = shift + 2.6 * np.array([np.cos(r), np.sin(r)])
            hot = k == 1 and (-50 < ((a + 180) % 360) - 180 < 50)
            ax.plot([0, end[0]], [0, end[1]], color=HOT if hot else GOLD, lw=2.2)
        ax.add_patch(Circle((0, 0), 0.14, fc=INK, zorder=6))
        ax.text(0.2, -0.5, "ось", fontsize=9.5, ha="left", zorder=8, bbox=dict(fc=PAPER, ec="none", pad=1))  # right of the axis: the mg arrow runs on its left
        if k == 1:
            ax.add_patch(Circle(shift, 0.1, fc=PAPER, ec=HOT, lw=2, zorder=7))
            ax.annotate("центр тяжести\nсместился от оси", shift + np.array([-0.05, 0.1]), (-3.3, 1.2), fontsize=9, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT), bbox=dict(fc=PAPER, ec="none", pad=1))
            arrow(ax, (shift[0], -0.15), (shift[0], -1.5), color=GREEN, lw=2.4, ms=14)
            ax.text(shift[0] - 0.15, -3.0, "$mg$: момент силы тяжести\nвращает колесо", fontsize=9, ha="center", va="top", color=GREEN)
        ax.add_patch(Circle((4.0, 0.0), 0.55, fc=tint(WARM, 0.8), ec=GOLD, lw=2))
        for a in range(0, 360, 45):
            r = np.deg2rad(a)
            ax.plot([4.0 + 0.7 * np.cos(r), 4.0 + 0.95 * np.cos(r)], [0.7 * np.sin(r), 0.95 * np.sin(r)], color=GOLD, lw=1.6)
        ax.text(4.0, -1.35, "лампа\n(нагреватель)", ha="center", fontsize=9, color=HOT)
    axes[1].text(3.7, 1.9, "воздух вокруг —\nохладитель", fontsize=9, color=WATER, ha="center")
    save(fig, "engine-rubber-engine.png")


# 15. tasks: share of useful work
def tasks_eta():
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    rows = [
        ("Подъёмник, 7.13", 0.227, "$A = 90$ кДж,  $Q_{\\mathrm{сг}} = 396$ кДж"),
        ("Двигатель, 7.14", 0.20, "$A = 12{,}5$ МДж,  $Q_{\\mathrm{сг}} = 62{,}5$ МДж"),
        ("Тепловоз, 31.29", 0.35, "$A = 200$ ГДж,  $Q_{\\mathrm{сг}} = 571$ ГДж"),
        ("Грузовик, 31.30", 0.39, "$A = 7{,}8$ ГДж,  $Q_{\\mathrm{сг}} = 20$ ГДж"),
    ]
    for i, (name, eta, lab) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, eta * 100, color=GREEN, height=0.55)
        ax.barh(y, (1 - eta) * 100, left=eta * 100, color=LOSS, height=0.55)
        ax.text(eta * 50, y, f"$\\eta = {num(eta, None, math=True)}$", ha="center", va="center", color=PAPER, fontsize=10.5, fontweight="bold")
        ax.text(101, y, lab, va="center", fontsize=9.5)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    for lbl in ax.get_yticklabels():
        keep_dots(lbl)
    ax.set_xlim(0, 100)
    ax.set_xlabel("доля от теплоты сгорания $Q_{\\mathrm{сг}}$ (сколько ушло в работу), %")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("Куда уходит теплота сгорания в задачах урока")
    save(fig, "engine-tasks-eta.png")


# 16. truck: fuel left against the distance
def truck_range():
    fig, ax = axes_grid(7.4, 4.4)
    k = 0.05 * 12e3 * 10 / (0.39 * 42e6 * 800) * 1e3 * 1e3  # litres per km
    s = np.linspace(0, 600 / k, 100)  # the line ends at the empty tank, the fuel level never goes below zero
    v = 600 - k * s
    ax.plot(s, v, color=INK, lw=2.4)
    ax.plot([1300], [600 - k * 1300], "o", color=HOT, ms=8, zorder=5)
    ax.annotate("Донецк, 1300 км:\nосталось $4{,}8$ л", (1300, 600 - k * 1300), (880, 430), fontsize=10, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT))
    ax.axhline(0, color=GREY, lw=1)
    ax.set_xlim(0, 1400)
    ax.set_ylim(-30, 640)
    ax.set_xlabel("пройденный путь $s$, км")
    ax.set_ylabel("топлива в баках, л")
    keep_dots(ax.set_title("Грузовик Львов — Донецк (31.30)"))
    ax.text(30, 30, "бак опустеет на $s \\approx 1310$ км", fontsize=9.5, color=NOTE)
    save(fig, "engine-task-truck-range.png")


# 17. locomotive: fuel against the train mass
def locomotive_fuel():
    fig, ax = axes_grid(7.4, 4.4)
    m = np.linspace(0, 8000, 100)  # tonnes
    for eta, col in ((0.35, INK), (0.5, GREEN)):
        fuel = 0.008 * m * 1e3 * 10 * 500e3 / (eta * 42e6) / 1e3  # tonnes
        ax.plot(m, fuel, color=col, lw=2.4, label=f"$\\eta = {num(eta, None, math=True)}$")
    ax.plot([5000], [13.605], "o", color=HOT, ms=8, zorder=5)
    ax.annotate("5000 т: $13{,}6$ т топлива", (5000, 13.605), (1200, 19), fontsize=10, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT))
    ax.set_xlim(0, 8000)
    ax.set_ylim(0, 25)
    ax.set_xlabel("масса состава $M$, т")
    ax.set_ylabel("масса дизельного топлива, т")
    keep_dots(ax.set_title("Тепловоз Киев — Одесса (31.29), 500 км"))
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.62))
    save(fig, "engine-task-locomotive-fuel.png")


# 18. drops collision: speed against efficiency of conversion
def drops_speed():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.3), gridspec_kw={"width_ratios": [1, 1.35]})
    c_dt = 4200 * 80 / 1e3  # kJ/kg
    L = 2300.0
    ax1.bar(["нагреть\nот 20 до 100 °C", "испарить\nпри 100 °C"], [c_dt, L], color=[WATER, VAPOUR], width=0.55)
    for i, v in enumerate([c_dt, L]):
        ax1.text(i, v + 40, num(v, None) + " кДж/кг", ha="center", fontsize=10)
    ax1.set_ylim(0, 2700)
    ax1.set_ylabel("энергия на 1 кг воды, кДж")
    ax1.set_title("Что нужно каждой капле", fontsize=11.5)
    eta = np.linspace(0.2, 1.0, 100)
    v = np.sqrt(2 * (c_dt + L) * 1e3 / eta) / 1e3
    ax2.plot(eta, v, color=INK, lw=2.4)
    ax2.plot([0.5], [3.247], "o", color=HOT, ms=8, zorder=5)
    ax2.annotate("$\\eta = 0{,}5$:\n$v \\approx 3{,}2$ км/с", (0.5, 3.247), (0.62, 4.0), fontsize=10, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT))
    ax2.grid(True, color=GRID, lw=0.8)
    ax2.set_xlabel("доля механической энергии, перешедшая во внутреннюю, $\\eta$")
    ax2.set_ylabel("минимальная скорость капли, км/с")
    ax2.set_xlim(0.2, 1.0)
    ax2.set_ylim(2, 5.2)
    keep_dots(ax2.set_title("Скорость встречи (33.53)", fontsize=11.5))
    ax2.xaxis.set_major_formatter(lambda v, _: num(v, None))
    ax2.yaxis.set_major_formatter(lambda v, _: num(v, None))
    fig.subplots_adjust(wspace=0.3)
    save(fig, "engine-task-drops-speed.png")


# 19. kerosene burner: where the heat goes
def kerosene_energy():
    fig, ax = plt.subplots(figsize=(8.0, 3.4))
    parts = [
        ("нагрев воды\n504 кДж", 504, WATER),
        ("испарение\n186 кДж", 186, VAPOUR),
        ("потери 690 кДж", 690, LOSS),
    ]
    left = 0
    for name, v, col in parts:
        ax.barh(0, v, left=left, color=col, height=0.5)
        ax.text(left + v / 2, 0, name, ha="center", va="center", fontsize=10, color=PAPER if col in (WATER, VAPOUR) else INK)
        left += v
    ax.annotate("", xy=(690, 0.38), xytext=(0, 0.38), arrowprops=dict(arrowstyle="<->", color=GREEN))
    ax.text(345, 0.46, "$Q_{\\mathrm{пол}}$ = 690 кДж = $0{,}5\\,Q_{\\mathrm{сг}}$", ha="center", fontsize=10, color=GREEN)
    ax.set_xlim(0, 1380)
    ax.set_ylim(-0.5, 0.85)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("теплота сгорания 30 г керосина $Q_{\\mathrm{сг}} = 1380$ кДж")
    keep_dots(ax.set_title("Керосиновая горелка (33.50)"))
    save(fig, "engine-task-kerosene-energy.png")


if __name__ == "__main__":
    energy_flow()
    cork_chain()
    cycle_stages()
    eta_vs_loss()
    newcomen()
    watt()
    turbine()
    efficiency_compare()
    carburetor()
    ice_anatomy()
    four_strokes()
    pt_cycle()
    four_cylinders()
    rubber_engine()
    tasks_eta()
    truck_range()
    locomotive_fuel()
    drops_speed()
    kerosene_energy()
