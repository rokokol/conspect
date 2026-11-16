"""Figures for the note "Атмосферное давление" (course Физика 7-9, lessons 53, 55, 56, 57).

Run: python3 pressure_atmosphere.py
PNG files go to content/06. Давление/00. Вложения/, prefix atm-.
Colour code as in pressure_solids.py: force red, pressure blue; water light blue, mercury grey, oil amber.
Curves marked "не из лекции" are reference data, not from the lesson.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = COURSE / "content" / "06. Давление" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
NOMEDIA = OUT / ".nomedia"
if not NOMEDIA.exists():
    NOMEDIA.touch()

from theme import ASH, BLUE, COPPER, GREEN, INK, METAL, MUTED, PAPER, PINK, RED, SKY, WARM, num, saver, tint

GREY = MUTED
LIGHT = tint(INK, 0.9)
GRID = ASH
C_F = RED
C_P = BLUE
WATER = tint(SKY, 0.7)
WATER_EDGE = SKY
MERC = tint(INK, 0.6)
MERC_EDGE = tint(INK, 0.3)
OIL = tint(WARM, 0.55)
OIL_EDGE = COPPER  # WARM is too light for a thin outline or a pipe on white
GLASS = tint(SKY, 0.92)
SPRING = COPPER  # a metal spring
WOOD = tint(COPPER, 0.55)
EARTH = tint(COPPER, 0.6)


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


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=13, ls="-", z=5):
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


def ground_hatch(ax, x0, x1, y, h=0.15):
    line(ax, [x0, x1], [y, y], lw=1.8)
    for x in np.arange(x0 + 0.1, x1, 0.3):
        line(ax, [x, x - 0.14], [y, y - h], color=GREY, lw=1)


def dim_v(ax, x, y0, y1, text, color=INK, side="right", fs=11):
    """Vertical dimension arrow with a label."""
    arrow(ax, (x, y0), (x, y1), color=color, lw=1.4, style="<|-|>", scale=10)
    dx = 0.18 if side == "right" else -0.18
    label(ax, x + dx, (y0 + y1) / 2, text, fs=fs, color=color, ha="left" if side == "right" else "right")


def tap(ax, x, y, open_=False, color=INK):
    """A small valve on a vertical tube at (x, y); open_ turns the handle."""
    ax.add_patch(Polygon([(x - 0.16, y - 0.12), (x + 0.16, y + 0.12), (x + 0.16, y - 0.12), (x - 0.16, y + 0.12)],
                         closed=True, fc=PAPER, ec=color, lw=1.5, zorder=6))
    if open_:
        line(ax, [x + 0.16, x + 0.55], [y, y], color=color, lw=1.6)
        line(ax, [x + 0.55, x + 0.55], [y - 0.14, y + 0.14], color=color, lw=2.4)
    else:
        line(ax, [x + 0.16, x + 0.55], [y, y], color=color, lw=1.6)
        line(ax, [x + 0.55, x + 0.55], [y - 0.14, y + 0.14], color=color, lw=2.4)


def flask(ax, cx, cy, r, fill="none", neck_h=0.9, neck_w=0.34, edge=INK):
    ax.add_patch(Circle((cx, cy), r, fc=fill, ec=edge, lw=2, zorder=3))
    ax.add_patch(Rectangle((cx - neck_w / 2, cy + r - 0.05), neck_w, neck_h + 0.05, fc=PAPER, ec=edge, lw=2, zorder=2))
    # erase the circle arc inside the neck so the flask reads as one vessel
    ax.add_patch(Rectangle((cx - neck_w / 2 + 0.03, cy + r - 0.09), neck_w - 0.06, 0.16, fc=fill if fill != "none" else PAPER,
                           ec="none", zorder=4))
    return cy + r + neck_h


def scale_pan(ax, cx, y, text, w=2.4):
    ax.add_patch(Rectangle((cx - w / 2, y - 0.55), w, 0.55, fc=LIGHT, ec=INK, lw=1.8, zorder=3))
    label(ax, cx, y - 0.28, text, fs=11, color=INK)
    ax.add_patch(Rectangle((cx - w / 2 - 0.15, y - 0.65), w + 0.3, 0.1, fc=GREY, ec=INK, lw=1.2, zorder=3))


# ---------------------------------------------------------------- 1. weighing air


def air_weighing():
    fig, axes = blank(11.2, 4.6, (0, 15.5), (0, 6.6), n=1)
    ax = axes[0]
    cxs = [2.2, 7.6, 13.0]
    titles = ["1. Откачиваем воздух", "2. Взвешиваем колбу\nбез воздуха", "3. Открываем кран,\nвзвешиваем с воздухом"]
    for cx, t in zip(cxs, titles):
        label(ax, cx + 0.3, 6.15, t, fs=11)
    # panel 1
    y = 2.8
    top = flask(ax, cxs[0], y, 1.05, fill="none")
    tap(ax, cxs[0], top - 0.2)
    line(ax, [cxs[0] - 0.17, cxs[0] - 0.17], [top - 0.05, top + 0.55])
    line(ax, [cxs[0] + 0.17, cxs[0] + 0.17], [top - 0.05, top + 0.35])
    line(ax, [cxs[0] - 0.17, cxs[0] - 1.0], [top + 0.55, top + 0.55])
    line(ax, [cxs[0] + 0.17, cxs[0] - 1.0], [top + 0.35, top + 0.35])
    arrow(ax, (cxs[0] - 0.9, top + 0.45), (cxs[0] - 1.9, top + 0.45), color=C_P, lw=2)
    label(ax, cxs[0] - 1.45, top - 0.35, "к вакуумному\nнасосу", fs=9.5, color=GREY)
    label(ax, cxs[0], y, "$V=1{,}23$ л", fs=10.5)
    # panel 2: vacuum on the scale, tap closed
    scale_pan(ax, cxs[1], 1.55, "173,82 г")
    top = flask(ax, cxs[1], 2.8, 1.05, fill="none")
    ax.add_patch(Rectangle((cxs[1] - 0.6, 1.62), 1.2, 0.13, fc=tint(COPPER, 0.4), ec=INK, lw=1, zorder=4))
    tap(ax, cxs[1], top - 0.2)
    line(ax, [cxs[1] - 0.17, cxs[1] - 0.17], [top - 0.05, top + 0.55])
    line(ax, [cxs[1] + 0.17, cxs[1] + 0.17], [top - 0.05, top + 0.55])
    label(ax, cxs[1], 2.8, "вакуум", fs=10.5, color=GREY)
    # panel 3: air enters
    scale_pan(ax, cxs[2], 1.55, "175,18 г")
    top = flask(ax, cxs[2], 2.8, 1.05, fill="none")
    ax.add_patch(Rectangle((cxs[2] - 0.6, 1.62), 1.2, 0.13, fc=tint(COPPER, 0.4), ec=INK, lw=1, zorder=4))
    tap(ax, cxs[2], top - 0.2, open_=True)
    line(ax, [cxs[2] - 0.17, cxs[2] - 0.17], [top - 0.05, top + 0.85])
    line(ax, [cxs[2] + 0.17, cxs[2] + 0.17], [top - 0.05, top + 0.85])
    arrow(ax, (cxs[2] - 0.0, top + 1.45), (cxs[2] - 0.0, top + 0.6), color=C_P, lw=2)
    rng = np.random.default_rng(2)
    for _ in range(22):
        r = 0.8 * np.sqrt(rng.uniform())
        a = rng.uniform(0, 2 * np.pi)
        ax.add_patch(Circle((cxs[2] + r * np.cos(a), 2.8 + r * np.sin(a)), 0.055, fc=C_P, ec="none", zorder=5))
    label(ax, cxs[2] + 1.6, 3.9, "воздух", fs=10.5, color=C_P)
    # formula
    label(ax, 7.75, 0.45, r"$m_\mathrm{возд} = 175{,}18\ \mathrm{г} - 173{,}82\ \mathrm{г} = 1{,}36\ \mathrm{г}$", fs=12.5)
    save(fig, "atm-air-weighing.png")


# ---------------------------------------------------------------- 2. syringe in water


def syringe_water():
    fig, axes = blank(6.2, 5.6, (0, 9), (0, 8.2))
    ax = axes[0]
    # pan with water
    ax.add_patch(Polygon([(1.0, 0.4), (8.0, 0.4), (8.4, 3.0), (0.6, 3.0)], closed=True, fc=WATER, ec=INK, lw=2, zorder=2))
    line(ax, [0.6, 8.4], [3.0, 3.0], color=WATER_EDGE, lw=2.2)
    # syringe barrel
    bx, bw = 3.6, 1.7
    rect(ax, bx, 4.6, bw, 3.0, fc=PAPER, ec=INK, lw=2, z=3)
    # water inside barrel (raised)
    ax.add_patch(Rectangle((bx + 0.03, 4.63), bw - 0.06, 1.4, fc=WATER, ec="none", zorder=4))
    line(ax, [bx + 0.03, bx + bw - 0.03], [6.03, 6.03], color=WATER_EDGE, lw=2, z=5)
    # nozzle and water column in tube
    rect(ax, bx + bw / 2 - 0.15, 3.0 - 0.9, 0.3, 1.7 + 0.9, fc=WATER, ec=INK, lw=1.6, z=3)
    ax.add_patch(Rectangle((bx + bw / 2 - 0.12, 2.1), 0.24, 3.5, fc=WATER, ec="none", zorder=4))
    # piston raised
    ax.add_patch(Rectangle((bx + 0.04, 6.35), bw - 0.08, 0.35, fc=METAL, ec=INK, lw=1.5, zorder=5))
    line(ax, [bx + bw / 2, bx + bw / 2], [6.7, 8.1], lw=3.2)
    line(ax, [bx + bw / 2 - 0.5, bx + bw / 2 + 0.5], [8.1, 8.1], lw=3.2)
    arrow(ax, (bx + bw + 0.5, 6.55), (bx + bw + 0.5, 7.6), color=INK, lw=2.2)
    label(ax, bx + bw + 0.75, 7.2, "поршень\nвверх", fs=10, ha="left")
    # vacuum
    label(ax, bx + bw / 2, 6.45 + 0.0, "", fs=9)
    label(ax, 6.6, 5.2, "вакуум,\n$p=0$", fs=11, color=GREY, ha="left")
    arrow(ax, (6.55, 5.45), (5.4, 6.2), color=GREY, lw=1.2, scale=9)
    # atmosphere on the pan water surface
    for x in (1.3, 2.2, 6.0, 6.9, 7.7):
        arrow(ax, (x, 4.0), (x, 3.15), color=C_P, lw=2.2)
    label(ax, 1.0, 4.4, r"$p_\mathrm{атм}$", fs=13, color=C_P)
    # pressure transmitted inside the tube, same level as pan surface
    arrow(ax, (bx + bw / 2, 2.55), (bx + bw / 2, 3.25), color=C_P, lw=2.2)
    label(ax, bx + bw / 2 + 0.3, 2.05, r"$p_\mathrm{атм}$", fs=13, color=C_P, ha="left")
    label(ax, 4.45, 0.0, "вода поднимается вслед за поршнем", fs=11)
    save(fig, "atm-syringe-water.png")


# ---------------------------------------------------------------- 3. bottle and pump


def bottle(ax, cx, y0, w, h, water_h=0.0, neck_w=0.9, neck_h=1.2):
    ax.add_patch(Rectangle((cx - w / 2, y0), w, h, fc=GLASS, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((cx - neck_w / 2, y0 + h - 0.02), neck_w, neck_h, fc=GLASS, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((cx - w / 2 + 0.03, y0 + 0.03), w - 0.06, h - 0.02, fc=GLASS, ec="none", zorder=4))
    if water_h > 0:
        ax.add_patch(Rectangle((cx - w / 2 + 0.03, y0 + 0.03), w - 0.06, water_h, fc=WATER, ec="none", zorder=4))
        line(ax, [cx - w / 2 + 0.03, cx + w / 2 - 0.03], [y0 + 0.03 + water_h] * 2, color=WATER_EDGE, lw=1.8, z=5)
    # stopper
    ax.add_patch(Rectangle((cx - neck_w / 2 - 0.05, y0 + h + neck_h - 0.05), neck_w + 0.1, 0.4, fc=tint(INK, 0.2), ec=INK, lw=1.5, zorder=6))
    return y0 + h + neck_h + 0.35


def bottle_vacuum():
    fig, axes = blank(10.4, 5.4, (0, 15), (0, 7.8))
    ax = axes[0]
    # left: pumping
    label(ax, 3.2, 7.4, "1. Откачиваем воздух\nиз бутылки", fs=11.5)
    top = bottle(ax, 3.0, 0.8, 2.2, 3.4)
    line(ax, [3.0, 3.0], [top - 0.2, top + 1.3], lw=3)
    line(ax, [3.0, 5.2], [top + 1.3, top + 1.3], lw=3)
    ax.add_patch(Rectangle((5.2, top + 0.85), 1.2, 0.9, fc=BLUE, ec=INK, lw=1.6, zorder=5))
    label(ax, 5.8, top + 1.3, "насос", fs=9.5, color=PAPER)
    label(ax, 3.0, 2.4, "вакуум", fs=11, color=GREY, zorder=8)
    # right: the tube end goes into the water
    label(ax, 11.0, 7.4, "2. Конец трубки в воде:\nвода врывается в бутылку", fs=11.5)
    ax.add_patch(Polygon([(10.4, 0.3), (14.4, 0.3), (14.7, 2.4), (10.1, 2.4)], closed=True, fc=WATER, ec=INK, lw=2, zorder=2))
    line(ax, [10.1, 14.7], [2.4, 2.4], color=WATER_EDGE, lw=2.2)
    top = bottle(ax, 8.0, 0.8, 2.2, 3.4, water_h=2.6)
    # bent tube from the stopper down into the pan, filled with water
    xs = [8.0, 8.0, 12.3, 12.3]
    ys = [top - 0.2, top + 1.0, top + 1.0, 1.1]
    line(ax, xs, ys, lw=6.5, color=INK)
    line(ax, xs, ys, lw=3.8, color=WATER, z=5)
    for x in (13.2, 14.0, 10.8):
        arrow(ax, (x, 3.55), (x, 2.55), color=C_P, lw=2.2)
    label(ax, 13.6, 4.15, r"$p_\mathrm{атм}$", fs=13, color=C_P)
    label(ax, 5.0, 3.6, "остался воздух,\nкоторый не откачали", fs=9, color=GREY)
    arrow(ax, (6.3, 3.6), (7.4, 3.8), color=GREY, lw=1.1, scale=8)
    save(fig, "atm-bottle-vacuum.png")


# ---------------------------------------------------------------- 4. Torricelli steps


def torricelli_tube(ax, cx, ytop, ybot, w=0.5, fill=MERC, fill_top=None, edge=INK):
    """Glass tube, closed at the top. Mercury from ybot up to fill_top (None = full)."""
    ft = ytop if fill_top is None else fill_top
    ax.add_patch(Rectangle((cx - w / 2, ybot), w, ytop - ybot, fc=GLASS, ec=edge, lw=2, zorder=3))
    if ft > ybot:
        ax.add_patch(Rectangle((cx - w / 2 + 0.03, ybot), w - 0.06, ft - ybot, fc=fill, ec="none", zorder=4))
    ax.add_patch(Arc((cx, ytop), w, w, theta1=0, theta2=180, ec=edge, lw=2, zorder=3))


def dish(ax, cx, ybase, w=4.2, h=0.9, level=0.55):
    ax.add_patch(Polygon([(cx - w / 2 + 0.3, ybase), (cx + w / 2 - 0.3, ybase), (cx + w / 2, ybase + h),
                          (cx - w / 2, ybase + h)], closed=True, fc=GLASS, ec=INK, lw=2, zorder=2))
    ax.add_patch(Polygon([(cx - w / 2 + 0.34, ybase + 0.05), (cx + w / 2 - 0.34, ybase + 0.05),
                          (cx + w / 2 - 0.05, ybase + level), (cx - w / 2 + 0.05, ybase + level)],
                         closed=True, fc=MERC, ec="none", zorder=3))
    return ybase + level


def torricelli_steps():
    fig, axes = blank(11.6, 5.8, (0, 17), (0, 8.6))
    ax = axes[0]
    # panel 1: full tube, finger, above the dish
    label(ax, 2.6, 8.15, "1. Трубка полна ртути,\nконец зажат пальцем", fs=10.5)
    torricelli_tube(ax, 2.6, 6.8, 2.4)
    ax.add_patch(Ellipse((2.6, 2.3), 0.9, 0.45, fc=tint(PINK, 0.6), ec=INK, lw=1.3, zorder=6))
    dim_v(ax, 1.5, 2.4, 6.8, "около\n1 м", color=GREY, side="left", fs=10)
    dish(ax, 2.6, 0.5, w=4.0, h=0.9)
    # panel 2: inverted into the dish, still full
    label(ax, 8.4, 8.15, "2. Конец в ртути, палец убран:\nртуть начинает выливаться", fs=10.5)
    torricelli_tube(ax, 8.4, 7.0, 0.95)
    lev = dish(ax, 8.4, 0.5, w=4.0, h=0.9)
    arrow(ax, (9.3, 5.2), (9.3, 3.2), color=C_F, lw=2.2)
    # panel 3: settled at 760 mm
    label(ax, 14.2, 8.15, "3. Уровень установился\nна высоте 760 мм", fs=10.5)
    lev = dish(ax, 14.2, 0.5, w=4.0, h=0.9)
    torricelli_tube(ax, 14.2, 7.0, 0.95, fill_top=5.75)
    label(ax, 14.75, 6.55, "торричеллиева\nпустота (вакуум)", fs=9.5, color=GREY, ha="left")
    dim_v(ax, 13.4, lev, 5.75, "760 мм", side="left", fs=11)
    for x in (12.3, 16.1):
        arrow(ax, (x, 2.45), (x, lev + 0.08), color=C_P, lw=2.0)
    label(ax, 16.35, 2.55, r"$p_\mathrm{атм}$", fs=12, color=C_P, ha="left")
    save(fig, "atm-torricelli-steps.png")


def torricelli_balance():
    fig, axes = blank(7.4, 6.6, (0, 11.5), (0, 9.8))
    ax = axes[0]
    lev = dish(ax, 4.0, 0.6, w=5.2, h=1.1, level=0.7)
    y0 = 0.9
    torricelli_tube(ax, 4.0, 8.4, y0, w=0.6, fill_top=7.0)
    ytop_m = 7.0
    # atmospheric pressure on the dish surface
    for x in (1.9, 2.7, 5.9, 6.4):
        arrow(ax, (x, lev + 1.1), (x, lev + 0.06), color=C_P, lw=2.2)
    label(ax, 1.2, lev + 1.5, r"$p_\mathrm{атм}$", fs=13, color=C_P)
    # the pressure passes through the mercury (Pascal): up arrow at the level of the dish surface
    arrow(ax, (4.0, y0 + 0.05), (4.0, lev + 0.8), color=C_P, lw=2.6, z=8)
    label(ax, 4.55, lev + 0.45, r"$p_\mathrm{атм}$", fs=12, color=C_P, ha="left", zorder=12)
    # weight of the column
    arrow(ax, (4.0, ytop_m - 0.15), (4.0, ytop_m - 1.35), color=C_F, lw=2.6, z=8)
    label(ax, 4.55, ytop_m - 0.85, r"$\rho_\mathrm{рт}\, g\, h$", fs=12, color=C_F, ha="left", zorder=12)
    # vacuum
    label(ax, 5.0, 8.05, "вакуум, $p=0$", fs=11, color=GREY, ha="left")
    # height
    line(ax, [4.6, 8.0], [lev, lev], color=GREY, lw=1.2, ls="--")
    line(ax, [4.6, 8.0], [ytop_m, ytop_m], color=GREY, lw=1.2, ls="--")
    dim_v(ax, 7.6, lev, ytop_m, "$h = 760$ мм", side="right", fs=12)
    save(fig, "atm-torricelli-balance.png")


# ---------------------------------------------------------------- 5. column heights


def column_heights():
    rho = {"Ртуть": 13600.0, "Вода": 1000.0, "Минеральное масло": 850.0}
    g = 9.81
    p0 = 101300.0
    hs = {k: p0 / (v * g) for k, v in rho.items()}
    fig, axes = plt.subplots(1, 1, figsize=(7.6, 6.4))
    ax = axes
    cols = {"Ртуть": (MERC, MERC_EDGE), "Вода": (WATER, WATER_EDGE), "Минеральное масло": (OIL, OIL_EDGE)}
    xs = [1, 3, 5]
    for x, (name, h) in zip(xs, hs.items()):
        fc, ec = cols[name]
        ax.add_patch(Rectangle((x - 0.32, 0), 0.64, h, fc=fc, ec=INK, lw=1.8, zorder=3))
        ax.add_patch(Arc((x, h), 0.64, 0.64, theta1=0, theta2=180, ec=INK, lw=1.8, zorder=3))
        ax.text(x, h + 0.55, num(h, 2) + " м" if h < 1 else num(h, 1) + " м",
                ha="center", va="bottom", fontsize=12, color=INK)
        ax.text(x, -0.85, name, ha="center", va="top", fontsize=11)
        ax.text(x, -1.65, f"$\\rho = {int(rho[name]):,}$".replace(",", "\\,") + " кг/м$^3$", ha="center", va="top",
                fontsize=10, color=GREY)
    ax.set_xlim(0, 6)
    ax.set_ylim(-2.4, 14)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.set_ylabel("высота столба, м")
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Столб, который держит нормальное давление")
    ax.set_yticks(range(0, 15, 2))
    save(fig, "atm-column-heights.png")


# ---------------------------------------------------------------- 6. mm Hg layer and units


def mmhg_layer():
    fig, axes = blank(7.4, 3.3, (0, 11), (0, 4.5))
    ax = axes[0]
    ax.add_patch(Rectangle((0.8, 0.5), 7.0, 0.32, fc=MERC, ec=INK, lw=1.8, zorder=3))
    ground_hatch(ax, 0.3, 8.3, 0.5)
    label(ax, 8.55, 0.66, "$h = 1$ мм", fs=11, ha="left")
    label(ax, 4.3, 1.3, "лужица ртути, площадь любая", fs=10.5, color=GREY)
    label(ax, 4.6, 2.85, r"$p = \rho g h = 13\,600\ \frac{\mathrm{кг}}{\mathrm{м}^3}\cdot 9{,}8\ \frac{\mathrm{Н}}{\mathrm{кг}}"
                        r"\cdot 10^{-3}\ \mathrm{м} \approx 133{,}3\ \mathrm{Па}$", fs=13)
    label(ax, 4.6, 4.05, "1 мм рт. ст. — давление слоя ртути толщиной 1 мм", fs=11.5)
    save(fig, "atm-mmhg-layer.png")


def units_scale():
    fig, ax = plt.subplots(figsize=(9.6, 3.3))
    mm = np.linspace(0, 800, 2)
    ax.set_xlim(-10, 830)
    ax.set_ylim(-2.6, 2.4)
    ax.axis("off")
    ax.plot([0, 800], [0, 0], color=INK, lw=2)
    for v in range(0, 801, 100):
        ax.plot([v, v], [-0.13, 0.13], color=INK, lw=1.5)
        ax.text(v, 0.36, f"{v}", ha="center", va="bottom", fontsize=10.5)
    ax.text(-10, 1.35, "мм рт. ст.", ha="left", va="center", fontsize=11, color=INK)
    # lower scale: hPa
    ax.plot([0, 800], [-1.5, -1.5], color=C_P, lw=2)
    for hpa in range(0, 1001, 200):
        x = hpa / 1.3332
        ax.plot([x, x], [-1.63, -1.37], color=C_P, lw=1.5)
        ax.text(x, -1.92, f"{hpa}", ha="center", va="top", fontsize=10.5, color=C_P)
    ax.text(-10, -0.9, "гПа", ha="left", va="center", fontsize=11, color=C_P)
    # normal pressure
    x = 760
    ax.plot([x, x], [-1.5, 0], color=C_F, lw=1.6, ls="--")
    ax.plot([x], [0], "o", color=C_F, ms=7, zorder=5)
    ax.plot([x], [-1.5], "o", color=C_F, ms=7, zorder=5)
    ax.text(x - 12, 1.35, "нормальное давление\n760 мм рт. ст. = 1013 гПа", ha="right", va="center", fontsize=10.5, color=C_F)
    save(fig, "atm-units-scale.png")


# ---------------------------------------------------------------- 7. aneroid


def zigzag(x0, y0, x1, y1, n, amp):
    """Points of a zigzag between two points (spring or bellows edge)."""
    t = np.linspace(0, 1, 2 * n + 1)
    dx, dy = x1 - x0, y1 - y0
    L = np.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    xs, ys = [], []
    for i, ti in enumerate(t):
        off = 0 if i in (0, 2 * n) else amp * (1 if i % 2 else -1)
        xs.append(x0 + dx * ti + nx * off)
        ys.append(y0 + dy * ti + ny * off)
    return xs, ys


def aneroid_state(ax, ox, height, ang, n_arrows, title):
    y0 = 0.6
    yt = y0 + height
    ground_hatch(ax, ox - 1.9, ox + 1.9, y0 - 0.02, h=0.2)
    # bellows: two zigzag edges
    for sx in (-1, 1):
        xs, ys = zigzag(ox + sx * 1.15, y0, ox + sx * 1.15, yt, 6, 0.2)
        line(ax, xs, ys, lw=1.8)
    # spring inside
    xs, ys = zigzag(ox, y0, ox, yt, 7, 0.32)
    line(ax, xs, ys, color=SPRING, lw=1.8)
    # top plate and rod
    ax.add_patch(Rectangle((ox - 1.4, yt), 2.8, 0.14, fc=LIGHT, ec=INK, lw=1.6, zorder=5))
    ry = yt + 1.35
    line(ax, [ox, ox], [yt + 0.14, ry], lw=2.4)
    # wheel with pointer
    W = (ox + 2.5, 4.4)
    ax.add_patch(Circle(W, 0.34, fc=PAPER, ec=INK, lw=1.8, zorder=6))
    ax.add_patch(Circle(W, 0.06, fc=INK, ec=INK, zorder=7))
    line(ax, [ox, W[0] - 0.34], [ry, W[1] - 0.12], color=GREY, lw=1.6, z=5)
    line(ax, [ox - 0.06, ox + 0.06], [ry, ry], lw=3.5, z=6)
    # return spring on the other side of the wheel
    line(ax, [W[0] + 0.34, W[0] + 0.34], [W[1] - 0.1, W[1] + 0.05], color=GREY, lw=1.6, z=5)
    xs, ys = zigzag(W[0] + 0.34, W[1] + 0.05, W[0] + 0.34, W[1] + 1.05, 3, 0.1)
    line(ax, xs, ys, color=SPRING, lw=1.4)
    line(ax, [W[0] + 0.05, W[0] + 0.6], [W[1] + 1.05, W[1] + 1.05], lw=2.4)
    # pointer over a scale
    L = 1.7
    a = np.deg2rad(ang)
    arrow(ax, W, (W[0] + L * np.cos(a), W[1] + L * np.sin(a)), color=INK, lw=2.4, scale=14, z=8)
    t = np.linspace(np.deg2rad(25), np.deg2rad(155), 60)
    line(ax, W[0] + 1.95 * np.cos(t), W[1] + 1.95 * np.sin(t), color=GREY, lw=1.3)
    label(ax, W[0] + 1.75, W[1] + 1.55, "$p\\uparrow$", fs=10, color=GREY)
    label(ax, W[0] - 1.75, W[1] + 1.55, "$p\\downarrow$", fs=10, color=GREY)
    # atmospheric pressure on the plate
    for i in range(n_arrows):
        x = ox - 0.9 + i * (1.8 / max(n_arrows - 1, 1)) if n_arrows > 1 else ox
        arrow(ax, (x, yt + 1.15 + 0.0), (x, yt + 0.22), color=C_P, lw=2.0, scale=11, z=4)
    label(ax, ox, 7.75, title, fs=10.5)


def aneroid_mechanism():
    fig, axes = blank(11.8, 6.4, (0, 16), (0, 8.4))
    ax = axes[0]
    aneroid_state(ax, 2.9, 1.7, 55, 4, "Давление больше:\nатмосфера сжимает коробочку,\nстрелка вправо")
    aneroid_state(ax, 11.4, 2.5, 125, 2, "Давление меньше:\nпружина распрямляет коробочку,\nстрелка влево")
    label(ax, 2.9, 0.15, "гофрированная коробочка, воздух откачан; внутри пружина", fs=9.5, color=GREY, ha="left")
    ax.texts[-1].set_position((0.3, 0.15))
    save(fig, "atm-aneroid-mechanism.png")


def aneroid_dial():
    fig, axes = blank(5.6, 5.4, (-3.6, 3.6), (-3.6, 3.6))
    ax = axes[0]

    def th(v):
        return np.deg2rad(225 - (v - 900) / 300.0 * 270)

    ax.add_patch(Circle((0, 0), 3.35, fc=tint(INK, 0.95), ec=INK, lw=2.4, zorder=1))
    for v in range(900, 1201, 5):
        big = v % 50 == 0
        r0 = 2.75 if big else (2.87 if v % 10 == 0 else 2.95)
        line(ax, [r0 * np.cos(th(v)), 3.05 * np.cos(th(v))], [r0 * np.sin(th(v)), 3.05 * np.sin(th(v))],
             lw=1.8 if big else 0.9, z=3)
        if big:
            label(ax, 2.35 * np.cos(th(v)), 2.35 * np.sin(th(v)), str(v), fs=10)
    label(ax, 0, -0.8, "гПа", fs=11, color=GREY)
    label(ax, 0, -1.3, "БАРОМЕТР-АНЕРОИД", fs=8.5, color=GREY)
    # normal pressure mark and the classroom reading
    v = 1013
    ax.plot([3.18 * np.cos(th(v))], [3.18 * np.sin(th(v))], marker="o", color=C_F, ms=6, zorder=6)
    v = 1006
    arrow(ax, (0, 0), (1.95 * np.cos(th(v)), 1.95 * np.sin(th(v))), color=INK, lw=2.6, scale=16, z=8)
    ax.add_patch(Circle((0, 0), 0.12, fc=INK, ec=INK, zorder=9))
    label(ax, 0, -2.05, "стрелка: 1006 гПа", fs=10.5, color=INK)
    label(ax, 0, -2.65, "красная точка:\nнормальное 1013 гПа", fs=8.5, color=C_F)
    save(fig, "atm-aneroid-dial.png")


# ---------------------------------------------------------------- 8. atmosphere layers


def atmosphere_layers():
    rng = np.random.default_rng(7)
    fig, axes = blank(8.6, 6.2, (-7.2, 7.2), (-0.8, 9.2))
    ax = axes[0]
    R = 14.0
    cy = -R
    xs = np.linspace(-7.2, 7.2, 200)
    ysurf = np.sqrt(R**2 - xs**2) + cy
    ax.fill_between(xs, -0.8, ysurf, color=EARTH, zorder=1)
    ax.plot(xs, ysurf, color=INK, lw=2, zorder=2.5)
    # air molecules: density falls off with height
    n = 900
    xs_p = rng.uniform(-7.1, 7.1, n * 3)
    hs = rng.exponential(2.4, n * 3)
    keep = hs < 8.6
    xs_p, hs = xs_p[keep][:n], hs[keep][:n]
    ys_p = np.sqrt(R**2 - xs_p**2) + cy + 0.08 + hs
    ok = ys_p < 9.0
    ax.scatter(xs_p[ok], ys_p[ok], s=7, color=C_P, alpha=0.55, zorder=2, linewidths=0)
    # two barometers, at the ground and on a mountain
    xa, xb = -3.6, 3.4
    ya = np.sqrt(R**2 - xa**2) + cy
    ax.add_patch(Polygon([(2.0, np.sqrt(R**2 - 2.0**2) + cy), (3.4, 3.1), (4.9, np.sqrt(R**2 - 4.9**2) + cy)],
                         closed=True, fc=tint(COPPER, 0.4), ec=INK, lw=1.6, zorder=3))
    yb = 3.1
    for x, y, txt in ((xa, ya, r"$p_0$"), (xb, yb, r"$p_1$")):
        ax.add_patch(Circle((x, y + 0.42), 0.36, fc=PAPER, ec=INK, lw=1.8, zorder=6))
        label(ax, x, y + 0.42, "", fs=8)
        line(ax, [x, x + 0.16], [y + 0.42, y + 0.55], lw=1.6, z=7)
        label(ax, x + 0.9, y + 0.5, txt, fs=15, color=C_P)
    # the weight of the air column above each barometer
    arrow(ax, (xa, 8.9), (xa, ya + 0.85), color=C_F, lw=3.2, scale=16, z=7)
    arrow(ax, (xb, 8.9), (xb, yb + 0.85), color=C_F, lw=1.8, scale=13, z=7)
    label(ax, xa + 0.15, 5.0, "весь воздух\nнад барометром", fs=10, color=C_F, ha="left")
    label(ax, xb + 0.2, 6.2, "воздуха над\nбарометром меньше", fs=10, color=C_F, ha="left")
    label(ax, 0.0, -0.4, "Земля", fs=11)
    label(ax, 0.0, 8.6, r"$p_0 > p_1$", fs=14, color=C_P, va="center",
          bbox=dict(fc=PAPER, ec="none", pad=1.5, alpha=0.85))
    save(fig, "atm-layers-heights.png")


# ---------------------------------------------------------------- 9. mountain data and graphs

MOUNTAIN_H = np.array([424, 500, 575, 643, 812, 998, 1130, 1164, 1264], dtype=float)
MOUNTAIN_P = np.array([733, 726, 720, 714, 701, 687, 676, 671, 664], dtype=float)


def mountain_graph():
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    slope, icpt = np.polyfit(MOUNTAIN_H, MOUNTAIN_P, 1)
    print("mountain fit: slope", slope, "m per mmHg", -1 / slope)
    hh = np.array([380, 1310])
    ax.plot(hh, slope * hh + icpt, color=C_P, lw=2, zorder=2, label="прямая через точки")
    ax.scatter(MOUNTAIN_H, MOUNTAIN_P, color=INK, s=38, zorder=4, label="измерения")
    ax.scatter([424, 1264], [733, 664], s=140, facecolors="none", edgecolors=C_F, lw=2, zorder=5)
    # delta annotations
    ax.plot([424, 1264], [664, 664], color=GREY, lw=1.2, ls="--", zorder=1)
    ax.plot([424, 424], [664, 733], color=GREY, lw=1.2, ls="--", zorder=1)
    ax.annotate("", xy=(1264, 660), xytext=(424, 660), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    ax.text(844, 655.5, r"$\Delta h = 840$ м", ha="center", va="top", fontsize=11)
    ax.annotate("", xy=(400, 733), xytext=(400, 664), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    ax.text(392, 698.5, r"$\Delta p = 69$" + "\nмм рт. ст.", ha="right", va="center", fontsize=11)
    ax.text(1040, 728, r"$\dfrac{\Delta h}{\Delta p} = \dfrac{840\ \mathrm{м}}{69\ \mathrm{мм\ рт.\ ст.}}"
                       r"\approx 12\ \dfrac{\mathrm{м}}{\mathrm{мм\ рт.\ ст.}}$", ha="center", va="center", fontsize=11.5)
    ax.set_xlim(240, 1340)
    ax.set_ylim(640, 745)
    ax.set_xlabel("высота $h$, м")
    ax.set_ylabel("давление $p$, мм рт. ст.")
    ax.set_title("Подъём на гору Парашка")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", frameon=False, bbox_to_anchor=(0.2, 0.3))
    save(fig, "atm-mountain-graph.png")


def isa_mmhg(h_m):
    """Standard atmosphere, mm Hg. Reference data, not from the lesson."""
    h = np.asarray(h_m, dtype=float)
    p = np.where(h <= 11000, 1013.25 * (1 - 0.0065 * h / 288.15) ** 5.25588, 226.32 * np.exp(-(h - 11000) / 6341.62))
    return p * 0.750062


def pressure_full_profile():
    P0 = 760.0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.9), gridspec_kw=dict(width_ratios=[1.35, 1]))
    h = np.linspace(0, 20, 400)
    halving = P0 * 2 ** (-h / 5.5)
    line_lin = P0 - h * 1000 / 12.0
    a1.plot(h, halving, color=C_P, lw=2.4, label=r"$p_0 \cdot 2^{-h/5{,}5\ \mathrm{км}}$: вдвое на каждые 5,5 км")
    a1.plot(h[line_lin > 0], line_lin[line_lin > 0], color=C_F, lw=2, ls="--", label="прямая: 12 м на 1 мм рт. ст.")
    a1.plot(h, isa_mmhg(h * 1000), color=GREY, lw=1.6, ls=":", label="стандартная атмосфера (не из лекции)")
    hp = np.array([0, 5.5, 11, 16.5])
    a1.scatter(hp, P0 / 2 ** (hp / 5.5), color=INK, zorder=5, s=36)
    for x, txt in ((0, "$p_0$"), (5.5, "$p_0/2$"), (11, "$p_0/4$"), (16.5, "$p_0/8$")):
        yv = P0 / 2 ** (x / 5.5)
        a1.plot([x, x], [0, yv], color=GRID, lw=1, zorder=0)
        a1.annotate(txt, (x, yv), textcoords="offset points", xytext=(9, 7), fontsize=10.5)
    a1.text(9.6, 30, "прямая доходит\nдо нуля на 9 км", color=C_F, ha="left", va="center", fontsize=10)
    a1.set_xlim(0, 20)
    a1.set_ylim(0, 800)
    a1.set_xlabel("высота $h$, км")
    a1.set_ylabel("давление $p$, мм рт. ст.")
    a1.set_title("Давление во всей атмосфере")
    a1.legend(loc="upper right", frameon=False, fontsize=9.5)
    a1.grid(color=GRID, lw=0.8)
    # zoom
    hz = np.linspace(0, 1.5, 100)
    a2.plot(hz, P0 * 2 ** (-hz / 5.5), color=C_P, lw=2.4)
    a2.plot(hz, P0 - hz * 1000 / 12.0, color=C_F, lw=2, ls="--")
    a2.set_xlim(0, 1.5)
    a2.set_ylim(600, 770)
    a2.set_xlabel("высота $h$, км")
    a2.set_ylabel("давление $p$, мм рт. ст.")
    a2.set_title("Первые 1,5 км: кривая почти прямая")
    a2.grid(color=GRID, lw=0.8)
    diff = (P0 - 1500 / 12.0) - P0 * 2 ** (-1.5 / 5.5)
    print("difference line - halving at 1.5 km:", diff, "mm Hg")
    a2.text(0.75, 610, f"на 1,5 км расхождение около {round(diff)} мм рт. ст.", ha="center", fontsize=10)
    fig.tight_layout()
    save(fig, "atm-p-of-h-profile.png")


# ---------------------------------------------------------------- 10. problems


def plane(ax, x, y, s=1.0, color=METAL):
    ax.add_patch(Ellipse((x, y), 2.6 * s, 0.55 * s, fc=color, ec=INK, lw=1.6, zorder=5))
    ax.add_patch(Polygon([(x + 0.1 * s, y - 0.1 * s), (x + 0.5 * s, y - 0.1 * s), (x - 0.7 * s, y - 1.0 * s)], closed=True,
                         fc=color, ec=INK, lw=1.4, zorder=4))
    ax.add_patch(Polygon([(x - 1.0 * s, y + 0.1 * s), (x - 1.3 * s, y + 0.75 * s), (x - 0.8 * s, y + 0.2 * s)], closed=True,
                         fc=color, ec=INK, lw=1.4, zorder=4))
    for k in range(4):
        ax.add_patch(Circle((x + (0.3 + 0.25 * k) * s, y + 0.05 * s), 0.05 * s, fc=PAPER, ec=INK, lw=0.8, zorder=6))


def problem_plane():
    fig, axes = blank(8.6, 5.6, (0, 13), (0, 8.4))
    ax = axes[0]
    ground_hatch(ax, 0.3, 12.7, 0.9, h=0.25)
    plane(ax, 3.6, 6.6, s=1.25)
    dim_v(ax, 6.2, 0.9, 6.55, "$h$", side="right", fs=14)
    line(ax, [3.6, 6.4], [6.55, 6.55], color=GREY, lw=1.1, ls="--")
    label(ax, 3.6, 7.7, r"$p = 674$ мм рт. ст.", fs=12, color=C_P)
    ax.add_patch(Circle((1.6, 1.45), 0.4, fc=PAPER, ec=INK, lw=1.8, zorder=6))
    line(ax, [1.6, 1.78], [1.45, 1.63], lw=1.6, z=7)
    label(ax, 1.6, 2.35, r"$p_0 = 756$ мм рт. ст.", fs=12, color=C_P)
    label(ax, 9.7, 5.4, r"$\Delta p = p_0 - p = 82$ мм рт. ст.", fs=12)
    label(ax, 9.7, 4.0, r"$h = 82 \cdot 12\ \mathrm{м} = 984\ \mathrm{м}$", fs=12.5)
    label(ax, 9.7, 3.0, r"$h \approx 980$ м", fs=13, color=C_F)
    save(fig, "atm-problem-plane.png")


def problem_room():
    fig, axes = blank(9.4, 5.2, (0, 15), (0, 7.4))
    ax = axes[0]
    # sea
    ax.add_patch(Polygon([(0.2, 0.4), (6.5, 0.4), (6.5, 2.0), (0.2, 2.0)], closed=True, fc=WATER, ec="none", zorder=1))
    line(ax, [0.2, 6.6], [2.0, 2.0], color=WATER_EDGE, lw=2.2)
    # land: slope up from the shore to a plateau
    ax.add_patch(Polygon([(6.5, 0.4), (6.5, 2.0), (9.5, 3.4), (14.8, 3.4), (14.8, 0.4)], closed=True, fc=EARTH,
                         ec=INK, lw=1.8, zorder=2))
    line(ax, [6.5, 9.5, 14.8], [2.0, 3.4, 3.4], lw=2.2)
    # building
    ax.add_patch(Rectangle((10.4, 3.4), 3.2, 2.2, fc=tint(WARM, 0.75), ec=INK, lw=1.8, zorder=3))
    ax.add_patch(Polygon([(10.2, 5.6), (13.8, 5.6), (12.0, 6.6)], closed=True, fc=tint(RED, 0.45), ec=INK, lw=1.6, zorder=3))
    for x in (10.8, 12.0, 13.0):
        rect(ax, x, 3.7, 0.5, 0.6, fc=PAPER, z=4, lw=1.2)
        rect(ax, x, 4.6, 0.5, 0.6, fc=PAPER, z=4, lw=1.2)
    ax.add_patch(Circle((11.05, 4.9), 0.27, fc="none", ec=C_P, lw=2.2, zorder=6))
    label(ax, 11.05, 6.9, "", fs=9)
    # levels
    line(ax, [0.2, 10.4], [2.0, 2.0], color=GREY, lw=1.1, ls="--")
    line(ax, [6.5, 10.3], [4.9, 4.9], color=GREY, lw=1.1, ls="--", z=1)
    dim_v(ax, 9.0, 2.0, 4.9, "$h$", side="left", fs=14)
    label(ax, 2.6, 2.75, r"$p_0 = 1009$ гПа", fs=12, color=C_P)
    label(ax, 3.4, 1.15, "уровень моря", fs=10.5, color=GREY)
    label(ax, 6.7, 6.5, r"$p = 1004$ гПа (кабинет)", fs=12, color=C_P)
    arrow(ax, (8.1, 6.4), (10.6, 5.2), color=C_P, lw=1.3, scale=10)
    label(ax, 6.5, 5.4, r"$h = (p_0 - p)\cdot 9\ \frac{\mathrm{м}}{\mathrm{гПа}} = 45\ \mathrm{м}$", fs=11.5, ha="center")
    save(fig, "atm-problem-room.png")


# ---------------------------------------------------------------- 11. Magdeburg hemispheres


def magdeburg_hemispheres():
    fig, axes = blank(8.2, 6.4, (-5.6, 5.6), (-4.4, 5.6))
    ax = axes[0]
    R = 2.2
    ax.add_patch(Wedge((0, 0), R, 90, 270, fc=tint(COPPER, 0.5), ec=INK, lw=2.2, zorder=3, width=0.25))
    ax.add_patch(Wedge((0, 0), R, -90, 90, fc=tint(COPPER, 0.35), ec=INK, lw=2.2, zorder=3, width=0.25))
    # leather gasket and flanges
    ax.add_patch(Rectangle((-0.12, R - 0.3), 0.24, 0.3, fc=COPPER, ec=INK, lw=1.3, zorder=4))
    ax.add_patch(Rectangle((-0.12, -R), 0.24, 0.3, fc=COPPER, ec=INK, lw=1.3, zorder=4))
    for x in (-R - 0.3, R + 0.3):
        ax.add_patch(Circle((x, 0), 0.3, fc="none", ec=INK, lw=2.2, zorder=4))
    # valve and pump hose
    # the tap sits on the right hemisphere at 45 degrees, away from the seam and its gasket
    c45 = np.cos(np.pi / 4)
    bx, by = R * c45, R * c45
    tilt = matplotlib.transforms.Affine2D().rotate_deg_around(bx, by, -45) + ax.transData
    ax.add_patch(Rectangle((bx - 0.22, by), 0.44, 0.6, fc=LIGHT, ec=INK, lw=1.8, zorder=5, transform=tilt))
    tx, ty = bx + 0.6 * c45, by + 0.6 * c45
    line(ax, [tx, tx + 0.5, 2.9], [ty, ty + 0.5, ty + 0.5], lw=3)
    label(ax, 4.1, ty + 0.5, "к вакуумному\nнасосу", fs=10, color=GREY)
    label(ax, 0, 0, "воздух\nоткачан", fs=11, color=GREY)
    label(ax, -3.15, 0.75, "ручка", fs=9.5, color=GREY)
    # atmospheric force on every element of the surface
    for a in np.deg2rad(np.arange(-160, 161, 20)):
        if abs(np.sin(a)) > 0.98 and abs(np.cos(a)) < 0.2:
            continue
        p0 = ((R + 1.15) * np.cos(a), (R + 1.15) * np.sin(a))
        p1 = ((R + 0.32) * np.cos(a), (R + 0.32) * np.sin(a))
        if abs(np.cos(a) + 1) < 0.02 or abs(np.cos(a) - 1) < 0.02:
            continue
        arrow(ax, p0, p1, color=C_P, lw=1.9, scale=11, z=6)
    label(ax, -3.65, -2.6, r"$p_\mathrm{атм}$", fs=13, color=C_P)
    # diameter
    dim_v(ax, 0, -R - 0.6, -R - 0.6, "", side="right")
    arrow(ax, (-R, -R - 0.75), (R, -R - 0.75), color=INK, lw=1.4, style="<|-|>", scale=10)
    label(ax, 0, -R - 1.2, "$d = 35{,}5$ см", fs=12)
    save(fig, "atm-magdeburg-hemispheres.png")


def magdeburg_disc():
    fig, axes = blank(9.6, 5.0, (-3.2, 9.6), (-3.2, 3.2))
    ax = axes[0]
    R = 2.0
    # hemisphere with the curved side to the left, atmosphere on it
    ax.add_patch(Wedge((0, 0), R, 90, 270, fc=tint(COPPER, 0.5), ec=INK, lw=2.2, zorder=3, width=0.22))
    line(ax, [0, 0], [-R, R], lw=2.2)
    for a in np.deg2rad(np.arange(100, 261, 20)):
        p0 = ((R + 1.0) * np.cos(a), (R + 1.0) * np.sin(a))
        p1 = ((R + 0.15) * np.cos(a), (R + 0.15) * np.sin(a))
        arrow(ax, p0, p1, color=C_P, lw=1.7, scale=10, z=6)
    arrow(ax, (0.3, 0), (2.7, 0), color=C_F, lw=3.2, scale=16, z=7)
    label(ax, 1.5, 0.45, r"$\vec F$", fs=14, color=C_F)
    label(ax, -0.5, -3.0, "полусфера: силы под разными углами", fs=10.5)
    # equality
    label(ax, 4.2, 0.0, "=", fs=26)
    # flat disc of the same diameter
    x0 = 6.3
    line(ax, [x0, x0], [-R, R], lw=5, color=INK)
    for y in np.linspace(-R + 0.25, R - 0.25, 7):
        arrow(ax, (x0 - 1.7, y), (x0 - 0.1, y), color=C_P, lw=1.7, scale=10, z=6)
    arrow(ax, (x0 + 0.15, 0), (x0 + 2.4, 0), color=C_F, lw=3.2, scale=16, z=7)
    label(ax, x0 + 1.3, 0.45, r"$\vec F$", fs=14, color=C_F)
    label(ax, x0 - 0.2, -3.0, "плоский диск того же диаметра: все силы параллельны", fs=10.5, ha="center")
    arrow(ax, (x0 + 0.6, -R), (x0 + 0.6, R), color=INK, lw=1.3, style="<|-|>", scale=9)
    label(ax, x0 + 0.85, 1.35, "$d$", fs=13, ha="left")
    label(ax, x0 + 1.1, -1.35, r"$S = \dfrac{\pi d^2}{4}$", fs=13, ha="left")
    save(fig, "atm-magdeburg-disc.png")


# ---------------------------------------------------------------- 12. card, table, weather


def card_glass():
    fig, axes = blank(6.0, 5.6, (0, 9), (0, 8.4))
    ax = axes[0]
    rect(ax, 2.7, 2.6, 3.2, 4.2, fc=WATER, ec=INK, lw=2, z=3)
    ax.add_patch(Rectangle((2.6, 2.45), 3.4, 0.16, fc=tint(WARM, 0.6), ec=INK, lw=1.5, zorder=5))
    label(ax, 4.3, 5.0, "вода", fs=12)
    label(ax, 4.3, 7.3, "банка полна воды, воздуха в ней нет", fs=10.5, color=GREY)
    line(ax, [2.75, 5.85], [6.7, 6.7], color=WATER_EDGE, lw=1.6, z=5)
    for x in (3.0, 4.3, 5.6):
        arrow(ax, (x, 1.2), (x, 2.3), color=C_P, lw=2.4, z=6)
    label(ax, 6.9, 1.55, r"$p_\mathrm{атм}$", fs=13, color=C_P, ha="left")
    arrow(ax, (4.3, 4.3), (4.3, 3.0), color=C_F, lw=2.4, z=6)
    label(ax, 4.8, 3.65, "вес воды", fs=10, color=C_F, ha="left")
    label(ax, 6.5, 2.5, "карточка", fs=10.5, color=GREY, ha="left")
    save(fig, "atm-card-glass.png")


def table_force():
    fig, axes = blank(9.4, 4.9, (0, 14), (0, 6.6))
    ax = axes[0]
    ax.add_patch(Rectangle((1.5, 2.55), 11.0, 0.35, fc=WOOD, ec=INK, lw=1.8, zorder=3))
    for x in (2.0, 11.7):
        rect(ax, x, 0.5, 0.35, 2.05, fc=WOOD, z=3, lw=1.6)
    ground_hatch(ax, 0.8, 13.2, 0.5, h=0.2)
    for x in np.linspace(2.0, 12.0, 8):
        arrow(ax, (x, 4.6), (x, 3.05), color=C_P, lw=2.2, z=5)
    for x in (3.4, 4.8, 9.2, 10.6):
        arrow(ax, (x, 1.05), (x, 2.4), color=C_P, lw=2.2, z=5)
    label(ax, 7.0, 5.6, "сверху на крышку $4\\times 1$ м: $F = pS \\approx 395$ кН, вес груза около 40 т", fs=12, color=C_P)
    label(ax, 7.0, 1.6, "снизу давит\nтот же воздух", fs=11, color=C_P)
    save(fig, "atm-table-force.png")


def spiral_arrow(ax, cx, cy, r0, r1, a0, a1, cw, color):
    n = 40
    t = np.linspace(0, 1, n)
    r = r0 + (r1 - r0) * t
    a = a0 + (a1 - a0) * t
    a = a0 - abs(a1 - a0) * t if cw else a0 + abs(a1 - a0) * t
    xs, ys = cx + r * np.cos(a), cy + r * np.sin(a)
    line(ax, xs[:-1], ys[:-1], color=color, lw=2, z=4)
    arrow(ax, (xs[-3], ys[-3]), (xs[-1], ys[-1]), color=color, lw=2, scale=13, z=5)


def wind_map():
    fig, axes = blank(13.4, 5.0, (0, 22), (0, 7.4), n=1)
    ax = axes[0]
    # left panel: three points and wind from high to low
    label(ax, 4.0, 7.0, "Ветер дует туда, где давление меньше", fs=11.5)
    pts = [(1.2, 4.4), (4.0, 3.1), (7.0, 1.6)]
    for x, y in pts:
        ax.add_patch(Circle((x, y), 0.2, fc=INK, ec=INK, zorder=6))
    label(ax, 1.5, 5.2, "Бендеры — Тирасполь\n1012 гПа", fs=10)
    label(ax, 3.3, 2.15, "Одесса\n1013 гПа", fs=10)
    label(ax, 6.6, 0.7, "Херсонская область\n1014–1015 гПа", fs=10)
    arrow(ax, (6.7, 1.85), (4.4, 2.95), color=C_P, lw=3, scale=16)
    arrow(ax, (3.6, 3.3), (1.6, 4.25), color=C_P, lw=3, scale=16)
    label(ax, 6.9, 4.3, "давление растёт\nв сторону Херсонской\nобласти, ветер идёт\nот большего к меньшему", fs=9.5, color=GREY)
    # right panel: anticyclone and cyclone
    ax.plot([9.6, 9.6], [0.4, 7.0], color=GRID, lw=1.5)
    cx1, cy1 = 13.2, 3.4
    ax.add_patch(Circle((cx1, cy1), 0.1, fc=C_F, ec="none", zorder=6))
    for k in range(3):
        a0 = k * 2 * np.pi / 3
        spiral_arrow(ax, cx1, cy1, 0.6, 2.0, a0, a0 + 2.0, cw=True, color=C_F)
    label(ax, cx1, 6.4, "Антициклон\nвысокое давление, до 1038 гПа\nвоздух по часовой стрелке", fs=9.5)
    cx2, cy2 = 18.6, 3.4
    ax.add_patch(Circle((cx2, cy2), 0.1, fc=C_P, ec="none", zorder=6))
    for k in range(3):
        a0 = k * 2 * np.pi / 3
        spiral_arrow(ax, cx2, cy2, 2.0, 0.6, a0, a0 + 2.0, cw=False, color=C_P)
    label(ax, cx2, 6.4, "Циклон\nнизкое давление, до 965 гПа\nвоздух против часовой стрелки", fs=9.5)
    label(ax, cx1, 0.7, "H", fs=16, color=C_F)
    label(ax, cx2, 0.7, "L", fs=16, color=C_P)
    save(fig, "atm-wind-map.png")


if __name__ == "__main__":
    air_weighing()
    syringe_water()
    bottle_vacuum()
    torricelli_steps()
    torricelli_balance()
    column_heights()
    mmhg_layer()
    units_scale()
    aneroid_mechanism()
    aneroid_dial()
    atmosphere_layers()
    mountain_graph()
    pressure_full_profile()
    problem_plane()
    problem_room()
    magdeburg_hemispheres()
    magdeburg_disc()
    card_glass()
    table_force()
    wind_map()
