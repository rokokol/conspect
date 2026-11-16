"""Figures for the note "Гидравлический пресс" (course Физика 7-9, lessons 60, 61, 62).

Run: python3 pressure_press.py
PNG files go to content/06. Давление/00. Вложения/, prefix press-.
Drawing helpers and the colour code come from pressure_atmosphere.py (force red, pressure blue, oil amber, water light blue).
Task data are taken from the lesson frames; g = 10 N/kg as in the lesson unless a graph says otherwise.
"""
from matplotlib.patches import Circle, Polygon, Rectangle
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np

from pressure_atmosphere import (
    C_F, C_P, GREEN, GREY, GRID, INK, LIGHT, OIL, OIL_EDGE, WATER, WATER_EDGE,
    arrow, blank, dim_v, label, line, rect, save,
)
from theme import COPPER, GREEN, METAL, PAPER, SKY, WARM, RED, keep_dots, num, tint

FLUID = OIL
FLUID_EDGE = OIL_EDGE


def fill(ax, x0, x1, y0, y1, fc=FLUID, z=1, hatch=None):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="none", zorder=z, hatch=hatch))


def vessels(ax, x1, w1, x2, w2, ybot, ytop, py1, py2, ch=0.55, fc=FLUID, dashed=None, th=0.22):
    """Two connected cylinders with pistons at heights py1 (left, narrow) and py2 (right, wide); liquid under the pistons."""
    fill(ax, x1, x1 + w1, ybot, py1, fc)
    fill(ax, x1 + w1, x2, ybot, ybot + ch, fc)
    fill(ax, x2, x2 + w2, ybot, py2, fc)
    line(ax, [x1, x1, x2 + w2, x2 + w2], [ytop, ybot, ybot, ytop], lw=2.4)
    line(ax, [x1 + w1, x1 + w1], [ybot + ch, ytop], lw=2.4)
    line(ax, [x2, x2], [ybot + ch, ytop], lw=2.4)
    line(ax, [x1 + w1, x2], [ybot + ch, ybot + ch], lw=2.4)
    for (xa, w, py) in ((x1, w1, py1), (x2, w2, py2)):
        ax.add_patch(Rectangle((xa + 0.02, py), w - 0.04, th, fc=GREY, ec=INK, lw=1.6, zorder=5))
    if dashed:
        for (xa, w, py) in dashed:
            ax.add_patch(Rectangle((xa + 0.02, py), w - 0.04, th, fc="none", ec=GREY, lw=1.4, ls="--", zorder=4))


def fbox(ax, x, y, text, color=INK, fs=12, **kw):
    label(ax, x, y, text, fs=fs, color=color, **kw)


# ---------------------------------------------------------------- 1. scheme of the law


def scheme():
    fig, axes = blank(11.6, 5.8, (0, 16.5), (0, 8.4))
    ax = axes[0]
    x1, w1, x2, w2 = 1.2, 1.5, 4.6, 4.2
    vessels(ax, x1, w1, x2, w2, 0.8, 5.6, 4.0, 4.0)
    # S1, S2 as double arrows above the cylinders
    for (xa, w, s) in ((x1, w1, "$S_1$"), (x2, w2, "$S_2$")):
        arrow(ax, (xa, 6.15), (xa + w, 6.15), color=GREY, lw=1.4, style="<|-|>", scale=9)
        label(ax, xa + w / 2, 6.55, s, fs=13, color=GREY)
    # forces: the short arrow on the small piston, the long one on the big piston
    arrow(ax, (x1 + w1 / 2, 5.6), (x1 + w1 / 2, 4.35), color=C_F, lw=2.8, scale=15)
    label(ax, x1 - 0.2, 5.1, "$F_1$", fs=14, color=C_F, ha="right")
    arrow(ax, (x2 + w2 / 2, 6.0), (x2 + w2 / 2, 4.35), color=C_F, lw=2.8, scale=15)
    label(ax, x2 + w2 / 2 + 0.5, 5.4, "$F_2$", fs=14, color=C_F, ha="left")
    # pressures below the pistons
    label(ax, x1 + w1 / 2, 2.6, "$p_1 = \\dfrac{F_1}{S_1}$", fs=12, color=C_P)
    label(ax, x2 + w2 / 2, 2.6, "$p_2 = \\dfrac{F_2}{S_2}$", fs=12, color=C_P)
    # equations
    label(ax, 10.6, 6.6, "$p_1 = p_2$", fs=14, ha="left")
    label(ax, 10.6, 5.5, "$\\dfrac{F_1}{S_1} = \\dfrac{F_2}{S_2}$", fs=14, ha="left")
    ax.text(10.6, 3.9, "$\\dfrac{F_2}{F_1} = \\dfrac{S_2}{S_1}$", fontsize=16, ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.4", fc=PAPER, ec=INK, lw=1.8))
    label(ax, 10.6, 2.4, "$S_2 > S_1$ значит $F_2 > F_1$\nво столько же раз", fs=11, ha="left", color=GREY)
    label(ax, 3.2, 0.25, "давление от поршней в тысячи раз больше давления столба жидкости, его не учитываем", fs=9.5,
          color=GREY, ha="center")
    save(fig, "press-scheme.png")


# ---------------------------------------------------------------- 2. force lines


def force_lines():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.6))
    f1 = np.linspace(0, 500, 100)
    cols = {1: GREY, 5: WARM, 10: C_P, 40: C_F}
    for k, c in cols.items():
        a.plot(f1, k * f1 / 1000, color=c, lw=2.3, label="$S_2/S_1 = %d$" % k)
    a.plot([300], [12], "o", color=C_F, ms=8, zorder=5)
    a.annotate("$300$ Н даёт $12$ кН", (300, 12), (330, 7.5), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    a.set_xlabel("сила на малом поршне $F_1$, Н")
    a.set_ylabel("сила на большом поршне $F_2$, кН")
    a.set_title("Чем больше отношение площадей, тем круче прямая", fontsize=11)
    a.set_xlim(0, 500)
    a.set_ylim(0, 21)
    a.grid(color=GRID, lw=0.8)
    a.legend(loc="upper left", frameon=False, fontsize=10)

    s2 = np.linspace(0, 500, 100)
    for f, c in ((100, GREY), (300, C_P), (500, WARM)):
        b.plot(s2, f * s2 / 10 / 1000, color=c, lw=2.3, label="$F_1 = %d$ Н" % f)
    b.plot([400], [12], "o", color=C_F, ms=8, zorder=5)
    b.annotate("$S_2 = 400$ см$^2$", (400, 12), (200, 16.5), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    b.set_xlabel("площадь большого поршня $S_2$, см$^2$")
    b.set_ylabel("$F_2$, кН")
    b.set_title("При $S_1 = 10$ см$^2$ сила растёт с площадью", fontsize=11)
    b.set_xlim(0, 500)
    b.set_ylim(0, 26)
    b.grid(color=GRID, lw=0.8)
    b.legend(loc="upper left", frameon=False, fontsize=10)
    for x in (a, b):
        x.spines["top"].set_visible(False)
        x.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "press-force-lines.png")


# ---------------------------------------------------------------- 3. all lesson problems on one log-log plot


def problems_map():
    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    x = np.array([2.0, 2000.0])
    for k, lab in ((0.004, None), (1, "$F_2 = F_1$"), (10, "$F_2 = 10F_1$"), (100, "$F_2 = 100F_1$")):
        ax.plot(x, k * x, color=GREY, lw=1.2, ls="--", zorder=1)
    ax.text(3.0, 3.4, "$F_2 = F_1$", color=GREY, fontsize=10, rotation=39)
    ax.text(3.0, 33, "$F_2 = 10F_1$", color=GREY, fontsize=10, rotation=39)
    ax.text(3.0, 330, "$F_2 = 100F_1$", color=GREY, fontsize=10, rotation=39)
    pts = [
        ("19.4", 300, 12000, 40, (-10, -12)),
        ("19.6", 300, 15000, 50, (-10, -1)),
        ("19.12", 450, 33750, 75, (10, 4)),
        ("19.14", 500, 3000, 6, (10, -10)),
        ("19.22", 300, 21000, 70, (-10, 10)),
        ("500 а", 20, 500, 25, (10, -12)),
        ("500 б", 50, 2500, 50, (-10, 4)),
        ("Марон 12", 10, 0.04, 0.004, (10, 4)),
    ]
    for name, f1, f2, k, (ox, oy) in pts:
        ax.plot([f1], [f2], "o", color=C_F, ms=7, zorder=5)
        keep_dots(ax.annotate(name + ", $S_2/S_1 = %s$" % num(k, None, math=True), (f1, f2), (ox, oy), textcoords="offset points",
                    fontsize=9.5, color=INK, ha="left" if ox > 0 else "right", va="center"))
    ax.text(3.2, 0.0125 * 0.4 / 0.4 * 1.0, "$F_2 = 0{,}004F_1$", color=GREY, fontsize=10, rotation=39)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(3, 1500)
    ax.set_ylim(0.01, 1e5)
    ax.set_xlabel("$F_1$, Н")
    ax.set_ylabel("$F_2$, Н")
    ax.set_title("Задачи урока на плоскости сил", fontsize=12)
    ax.grid(color=GRID, lw=0.7, which="both")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "press-problems-map.png")


# ---------------------------------------------------------------- 4. travel of the pistons


def travel():
    fig, axes = blank(12.2, 6.0, (0, 17.6), (0, 9.0))
    ax = axes[0]
    # left: initial state, right: the small piston is pushed down by h1, the big one rises by h2
    # both pistons start level; V1 = V2 gives h2 = h1 * w1 / w2
    start, h1 = 3.8, 2.4
    h2 = h1 * 1.2 / 4.0
    for ox, moved in ((0.4, False), (9.4, True)):
        x1, w1, x2, w2 = ox + 0.4, 1.2, ox + 3.2, 4.0
        py1 = start - (h1 if moved else 0)
        py2 = start + (h2 if moved else 0)
        vessels(ax, x1, w1, x2, w2, 0.8, 6.2, py1, py2)
        label(ax, x1 + w1 / 2, 6.8, "$S_1$", fs=13, color=GREY)
        label(ax, x2 + w2 / 2, 6.8, "$S_2$", fs=13, color=GREY)
    ox = 9.4
    x1, w1, x2, w2 = ox + 0.4, 1.2, ox + 3.2, 4.0
    # dashed initial positions and the shifts
    ax.add_patch(Rectangle((x1 + 0.02, start), w1 - 0.04, 0.22, fc="none", ec=GREY, lw=1.4, ls="--", zorder=4))
    ax.add_patch(Rectangle((x2 + 0.02, start), w2 - 0.04, 0.22, fc="none", ec=GREY, lw=1.4, ls="--", zorder=4))
    dim_v(ax, x1 - 0.5, start - h1 + 0.22, start + 0.22, "$h_1$", side="left", fs=13)
    dim_v(ax, x2 + w2 + 0.5, start, start + h2, "$h_2$", side="right", fs=13)
    label(ax, x1 + w1 / 2, 7.55, "$V_1 = S_1 h_1$", fs=10.5, color=C_P, ha="center")
    label(ax, x2 + w2 / 2, 7.55, "$V_2 = S_2 h_2$", fs=10.5, color=C_P, ha="center")
    label(ax, 4.5, 8.6, "начало", fs=12)
    label(ax, 13.6, 8.6, "малый поршень вниз на $h_1$, большой вверх на $h_2$", fs=11.5)
    label(ax, 13.6, 0.35, "жидкость несжимаема: $V_1 = V_2$, то есть $S_1 h_1 = S_2 h_2$", fs=11.5, color=INK)
    save(fig, "press-travel.png")


# ---------------------------------------------------------------- 5. travel and gain graphs


def travel_graph():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.7))
    h1 = np.linspace(0, 120, 100)
    for k, c in ((1, GREY), (5, WARM), (10, C_P), (50, GREEN), (100, C_F)):
        a.plot(h1, h1 / k, color=c, lw=2.2, label="$S_2/S_1 = %d$" % k)
    a.plot([100], [1], "o", color=C_F, ms=8, zorder=5)
    a.annotate("$100$ мм вниз: $1$ мм вверх", (100, 1), (42, 12), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    a.set_xlabel("ход малого поршня $h_1$, мм")
    a.set_ylabel("подъём большого поршня $h_2$, мм")
    a.set_title("Большой поршень идёт в $S_2/S_1$ раз короче", fontsize=11)
    a.set_xlim(0, 120)
    a.set_ylim(0, 30)
    a.grid(color=GRID, lw=0.8)
    a.legend(loc="upper left", frameon=False, fontsize=10, ncol=1)

    k = np.array([1, 2000.0])
    b.plot(k, k, color=INK, lw=1.8)
    pts = [("шприцы", 5, 5), ("19.14", 6, 6), ("500 б", 50, 50), ("19.22", 70, 70), ("Виктор: 100", 100, 100)]
    for name, x, y in pts:
        b.plot([x], [y], "o", color=C_F, ms=7, zorder=5)
    b.annotate("шприцы", (5, 5), (2.0, 12), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY))
    keep_dots(b.annotate("19.14", (6, 6), (7.5, 2.2), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY)))
    b.annotate("500 б", (50, 50), (18, 62), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY))
    keep_dots(b.annotate("19.22", (70, 70), (95, 40), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY)))
    b.annotate("машина Виктора", (100, 100), (120, 55), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY))
    b.set_xscale("log")
    b.set_yscale("log")
    b.set_xlim(1, 300)
    b.set_ylim(1, 300)
    b.set_xlabel("выигрыш в силе $F_2/F_1$")
    b.set_ylabel("проигрыш в расстоянии $h_1/h_2$")
    b.set_title("Выигрыш в силе равен проигрышу в расстоянии", fontsize=11)
    b.grid(color=GRID, lw=0.7, which="both")
    for x in (a, b):
        x.spines["top"].set_visible(False)
        x.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "press-travel-graph.png")


# ---------------------------------------------------------------- 6. two syringes


def syringes():
    fig, axes = blank(12.6, 5.4, (0, 18.6), (0, 8.0))
    ax = axes[0]
    # geometry: the big syringe has 5 times the cross-section; 1 mL = 5 divisions on the small one and 1 on the big one
    def barrel(x, w, ytop, ybot, div_h, ml_fill, name):
        ax.add_patch(Rectangle((x, ybot), w, ytop - ybot, fc=LIGHT, ec=INK, lw=2.2, zorder=2))
        # graduations every division
        n = int((ytop - ybot) / div_h)
        for i in range(n + 1):
            yy = ybot + i * div_h
            line(ax, [x + w, x + w + (0.32 if i % 5 == 0 else 0.18)], [yy, yy], lw=1.2, color=GREY)
        return n

    # small syringe: division height 0.6, 1 mL = 5 divisions = 3.0
    barrel(1.2, 1.0, 7.0, 1.0, 0.6, 1, "малый")
    # big syringe: division height 0.6, 1 mL = 1 division
    barrel(9.0, 2.2, 7.0, 1.0, 0.6, 1, "большой")
    # 1 mL highlighted
    ax.add_patch(Rectangle((1.2, 1.0), 1.0, 3.0, fc=FLUID, ec="none", zorder=3, alpha=0.9))
    ax.add_patch(Rectangle((9.0, 1.0), 2.2, 0.6, fc=FLUID, ec="none", zorder=3, alpha=0.9))
    dim_v(ax, 3.4, 1.0, 4.0, "$1$ мл =\n$5$ делений", fs=11)
    dim_v(ax, 12.4, 1.0, 1.6, "$1$ мл =\n$1$ деление", fs=11)
    label(ax, 1.7, 7.6, "малый шприц, $S_1$", fs=11.5)
    label(ax, 10.1, 7.6, "большой шприц, $S_2 = 5S_1$", fs=11.5)
    arrow(ax, (5.6, 4.0), (5.6, 1.0), color=C_F, lw=2.2, scale=13)
    label(ax, 6.05, 2.5, "поршень\nпрошёл\n$5$ делений", fs=10, color=C_F, ha="left")
    arrow(ax, (15.6, 1.6), (15.6, 1.0), color=C_F, lw=2.2, scale=11)
    label(ax, 16.0, 2.1, "поршень\nпрошёл\n$1$ деление", fs=10, color=C_F, ha="left")
    label(ax, 9.0, 0.3, "один и тот же объём: путь малого поршня в $5$ раз длиннее", fs=11, color=INK)
    save(fig, "press-syringes-demo.png")


# ---------------------------------------------------------------- 7. the full press with a pump


def machine():
    fig, axes = blank(14.4, 8.0, (0, 21.6), (-1.0, 11.4))
    ax = axes[0]
    # oil reservoir on the left; the return pipe enters its right wall at the bottom (y from 0.35 to 0.85)
    fill(ax, 0.6, 7.4, 0.0, 1.5)
    line(ax, [0.6, 0.6, 7.4], [2.6, 0.0, 0.0], lw=2.4)
    line(ax, [7.4, 7.4], [0.0, 0.35], lw=2.4)
    line(ax, [7.4, 7.4], [0.85, 2.6], lw=2.4)
    line(ax, [0.62, 7.38], [1.5, 1.5], color=FLUID_EDGE, lw=2, z=2)
    label(ax, 2.4, 0.7, "масло", fs=11, color=INK)
    # small pump cylinder above the reservoir: piston, valve 1 at the bottom, outlet valve 2 on the right
    cx0, cx1 = 5.0, 6.8
    yb, yt = 3.6, 8.2
    fill(ax, cx0, cx1, yb, 6.0)
    line(ax, [cx0, cx0], [yb, yt], lw=2.4)
    line(ax, [cx1, cx1], [yb, yb + 1.4], lw=2.4)
    line(ax, [cx1, cx1], [yb + 2.0, yt], lw=2.4)
    line(ax, [cx0, 5.6], [yb, yb], lw=2.4)
    line(ax, [6.2, cx1], [yb, yb], lw=2.4)
    # inlet tube from the reservoir up to the cylinder bottom
    line(ax, [5.6, 5.6], [yb, 0.7], lw=2.2)
    line(ax, [6.2, 6.2], [yb, 0.7], lw=2.2)
    fill(ax, 5.6, 6.2, 0.7, yb)
    # valve 1 (cone) at the bottom of the cylinder
    # pushing the lever down: valve 1 is closed (red), valve 2 open (green)
    ax.add_patch(Polygon([(5.5, yb + 0.5), (6.3, yb + 0.5), (5.9, yb)], closed=True, fc=tint(RED, 0.85), ec=C_F, lw=1.8, zorder=7))
    label(ax, 4.6, yb + 0.45, "клапан 1", fs=10.5, color=C_F, ha="right")
    # piston and lever
    ax.add_patch(Rectangle((cx0 + 0.02, 6.0), cx1 - cx0 - 0.04, 0.22, fc=GREY, ec=INK, lw=1.6, zorder=5))
    line(ax, [5.9, 5.9], [6.22, 9.2], lw=3.2, z=6)
    line(ax, [5.9, 3.0], [9.2, 10.0], lw=3.4, z=6)  # handle
    line(ax, [5.9, 8.4], [9.2, 8.6], lw=3.4, z=6)
    ax.plot([8.4], [8.6], "o", color=INK, ms=8, zorder=8)
    arrow(ax, (3.0, 10.7), (3.0, 10.1), color=C_F, lw=2.6, scale=14)
    label(ax, 3.4, 10.75, "$F_1$", fs=13, color=C_F, ha="left")
    label(ax, 9.0, 8.6, "шарнир", fs=10, color=GREY, ha="left")
    # pipe from the pump to the big cylinder, valve 2 in it
    line(ax, [cx1, 10.6], [yb + 1.4, yb + 1.4], lw=2.4)
    line(ax, [cx1, 10.6], [yb + 2.0, yb + 2.0], lw=2.4)
    fill(ax, cx1, 10.6, yb + 1.4, yb + 2.0)
    ax.add_patch(Circle((8.3, yb + 1.7), 0.32, fc=tint(GREEN, 0.85), ec=GREEN, lw=1.8, zorder=7))
    label(ax, 8.3, yb + 0.9, "клапан 2", fs=10.5, color=GREEN)
    # big cylinder on the right: piston with a platform, a workpiece, a fixed plate on top
    bx0, bx1 = 10.6, 15.6
    byb, byt = 1.6, 7.0
    fill(ax, bx0, bx1, byb, 5.0)
    line(ax, [bx0, bx0], [yb + 2.0, byt], lw=2.4)
    line(ax, [bx0, bx0], [byb, yb + 1.4], lw=2.4)
    line(ax, [bx1, bx1], [byb, byt], lw=2.4)
    line(ax, [bx0, bx1], [byb, byb], lw=2.4)
    ax.add_patch(Rectangle((bx0 + 0.02, 5.0), bx1 - bx0 - 0.04, 0.3, fc=GREY, ec=INK, lw=1.6, zorder=5))
    line(ax, [13.1, 13.1], [5.3, 6.2], lw=8, z=5, color=GREY)
    ax.add_patch(Rectangle((11.9, 6.2), 2.4, 0.4, fc=PAPER, ec=INK, lw=2, zorder=5))
    ax.add_patch(Rectangle((12.25, 6.6), 1.7, 0.9, fc=METAL, ec=INK, lw=2, hatch="///", zorder=5))
    ax.add_patch(Rectangle((11.4, 7.5), 3.4, 0.35, fc=GREY, ec=INK, lw=2, zorder=5))
    for xh in np.arange(11.5, 14.9, 0.4):
        line(ax, [xh, xh + 0.25], [7.85, 8.2], color=GREY, lw=1.4)
    label(ax, 16.0, 7.05, "деталь", fs=10.5, color=INK, ha="left")
    label(ax, 16.0, 7.85, "неподвижная опора", fs=10.5, color=INK, ha="left")
    arrow(ax, (13.1, 4.2), (13.1, 4.9), color=C_F, lw=2.6, scale=14, z=8)
    label(ax, 13.45, 4.0, "$F_2$", fs=13, color=C_F, ha="left")
    label(ax, 13.1, 2.6, "$S_2$", fs=13, color=GREY)
    label(ax, 5.9, 4.9, "$S_1$", fs=13, color=GREY)
    # drain tap at the bottom of the big cylinder and the return pipe to the reservoir
    fill(ax, 7.4, bx0 + 1.2, 0.35, 0.85)
    fill(ax, bx0 + 0.6, bx0 + 1.2, 0.35, byb)
    line(ax, [bx0 + 0.6, bx0 + 0.6, 7.4], [byb, 0.85, 0.85], lw=2.4)
    line(ax, [bx0 + 1.2, bx0 + 1.2, 7.4], [byb, 0.35, 0.35], lw=2.4)
    ax.add_patch(Polygon([(bx0 + 0.6, 1.4), (bx0 + 1.2, 1.0), (bx0 + 1.2, 1.4), (bx0 + 0.6, 1.0)], closed=True, fc=PAPER,
                         ec=C_F, lw=1.6, zorder=7))
    label(ax, bx0 + 0.9, -0.5, "кран слива масла", fs=10.5, color=C_F)
    label(ax, 16.4, 4.0, "масло под\nбольшим\nпоршнем", fs=10, color=INK, ha="left")
    label(ax, 10.0, 10.9, "Гидравлический пресс: насос подаёт масло, кран его возвращает", fs=11.5)
    save(fig, "press-machine-scheme.png")


# ---------------------------------------------------------------- 8. brakes


def brakes():
    fig, axes = blank(11.6, 5.6, (-1.2, 16.6), (0, 8.4))
    ax = axes[0]
    # car outline
    ax.add_patch(Rectangle((3.2, 1.6), 10.6, 5.2, fc="none", ec=GREY, lw=1.6, ls="--", zorder=1))
    label(ax, 8.5, 7.15, "вид сверху, четыре колеса", fs=9.5, color=GREY)
    # wheels as small rectangles with a wheel cylinder each
    wheels = [(4.2, 5.9), (12.8, 5.9), (4.2, 2.5), (12.8, 2.5)]
    for wx, wy in wheels:
        ax.add_patch(Rectangle((wx - 0.55, wy - 0.85), 1.1, 1.7, fc=LIGHT, ec=INK, lw=2, zorder=4))
        ax.add_patch(Rectangle((wx - 0.32, wy - 0.3), 0.64, 0.6, fc=FLUID, ec=INK, lw=1.4, zorder=5))
    # master cylinder with a pedal on the left
    ax.add_patch(Rectangle((0.6, 3.75), 1.9, 0.9, fc=FLUID, ec=INK, lw=2.2, zorder=4))
    line(ax, [0.2, 0.6], [4.2, 4.2], lw=3.2, z=5)
    arrow(ax, (0.0, 5.2), (0.0, 4.4), color=C_F, lw=2.4, scale=13)
    label(ax, 0.35, 5.35, "$F$ на педаль", fs=11, color=C_F, ha="left")
    label(ax, 1.55, 3.3, "главный\nцилиндр", fs=10, color=INK)
    # four lines
    junction = (2.9, 4.2)
    line(ax, [2.5, 3.2], [4.2, 4.2], lw=2.6, color=FLUID_EDGE, z=3)
    for wx, wy in wheels:
        line(ax, [3.2, 3.2, wx - 0.55 if wx < 8 else wx + 0.55], [4.2, wy, wy], lw=2.4, color=FLUID_EDGE, z=3) if wx < 8 else None
    # the right wheels are reached through a pipe along the middle of the car
    line(ax, [3.2, 8.5], [4.2, 4.2], lw=2.6, color=FLUID_EDGE, z=3)
    line(ax, [8.5, 8.5, 12.25], [4.2, 5.9, 5.9], lw=2.4, color=FLUID_EDGE, z=3)
    line(ax, [8.5, 8.5, 12.25], [4.2, 2.5, 2.5], lw=2.4, color=FLUID_EDGE, z=3)
    line(ax, [3.2, 3.2, 3.65], [4.2, 5.9, 5.9], lw=2.4, color=FLUID_EDGE, z=3)
    line(ax, [3.2, 3.2, 3.65], [4.2, 2.5, 2.5], lw=2.4, color=FLUID_EDGE, z=3)
    label(ax, 8.5, 0.9, "по закону Паскаля давление одно и то же во всех четырёх гидролиниях:\nкаждое колесо тормозится с одной силой", fs=11, color=C_P)
    label(ax, 4.2, 7.15 - 0.55, "", fs=1)
    for wx, wy in wheels:
        label(ax, wx + (1.1 if wx > 8 else -1.1), wy, "$p$", fs=12, color=C_P)
    save(fig, "press-brakes.png")


# ---------------------------------------------------------------- 9. problems


def problem_19_4():
    fig, axes = blank(9.2, 5.4, (0, 13.2), (0, 7.8))
    ax = axes[0]
    x1, w1, x2, w2 = 1.2, 0.9, 3.6, 3.6
    vessels(ax, x1, w1, x2, w2, 0.8, 5.4, 3.8, 3.8, fc=WATER)
    arrow(ax, (x1 + w1 / 2, 5.4), (x1 + w1 / 2, 4.15), color=C_F, lw=2.6, scale=14)
    label(ax, x1 - 0.2, 5.05, "$F_1 = 300$ Н", fs=11.5, color=C_F, ha="right")
    arrow(ax, (x2 + w2 / 2, 5.9), (x2 + w2 / 2, 4.15), color=C_F, lw=3.2, scale=17)
    label(ax, x2 + w2 / 2 + 0.4, 5.0, "$F_2 = ?$", fs=12, color=C_F, ha="left")
    label(ax, x1 + w1 / 2, 6.2, "$S_1 = 10$ см$^2$", fs=11, color=GREY)
    label(ax, x2 + w2 / 2, 6.6, "$S_2 = 400$ см$^2$", fs=11, color=GREY)
    ax.text(9.0, 4.8, "$\\dfrac{F_2}{F_1} = \\dfrac{S_2}{S_1} = 40$", fontsize=13, ha="left", va="center")
    ax.text(9.0, 3.4, "$F_2 = 12$ кН", fontsize=13, ha="left", va="center", color=C_F,
            bbox=dict(boxstyle="square,pad=0.35", fc=PAPER, ec=C_F, lw=1.6))
    save(fig, "press-problem-19-4.png")


def car(ax, x, y, w, color=METAL):
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + 0.55), (x + 0.82 * w, y + 0.6), (x + 0.68 * w, y + 1.0),
                          (x + 0.3 * w, y + 1.0), (x + 0.18 * w, y + 0.6), (x, y + 0.55)], closed=True, fc=LIGHT, ec=INK, lw=2, zorder=6))
    for cx in (x + 0.22 * w, x + 0.78 * w):
        ax.add_patch(Circle((cx, y), 0.24, fc=INK, ec=INK, zorder=7))


def problem_jack():
    fig, axes = blank(12.4, 6.0, (0, 18.6), (-1.0, 8.2))
    ax = axes[0]
    for ox, name in ((0.2, "19.6"), (9.6, "19.12")):
        x1, w1, x2, w2 = ox + 0.8, 0.9, ox + 3.2, 3.6
        vessels(ax, x1, w1, x2, w2, 0.8, 5.0, 3.6, 3.6)
        car(ax, x2 + 0.35, 3.85, 2.9)
        arrow(ax, (x1 + w1 / 2, 5.0), (x1 + w1 / 2, 3.95), color=C_F, lw=2.6, scale=14)
        label(ax, x1 + w1 / 2 - 0.2, 5.5, "$F_1$", fs=12.5, color=C_F, ha="right")
        label(ax, x2 + w2 / 2, 5.8, "$S_2$", fs=12.5, color=GREY)
        label(ax, x1 + w1 / 2, 6.2, "$S_1$", fs=12.5, color=GREY)
    keep_dots(ax.text(0.4, 7.7, "19.6: $P = 15$ кН, $F_1 = 300$ Н, $S_2 = 200$ см$^2$, $S_1 = ?$", fontsize=10.5, ha="left"))
    ax.text(0.4, -0.3, "$S_1 = S_2 \\dfrac{F_1}{P} = 4$ см$^2$", fontsize=12, ha="left", va="center", color=C_F)
    keep_dots(ax.text(9.8, 7.7, "19.12: $S_1 = 4$ см$^2$, $S_2 = 300$ см$^2$, $F_1 = 450$ Н;\n$m = ?$, $p = ?$", fontsize=10.5, ha="left", va="center"))
    ax.text(9.8, -0.3, "$m \\approx 3{,}4$ т, $p = 1{,}125$ МПа", fontsize=12, ha="left", va="center", color=C_F)
    save(fig, "press-problem-jack.png")


def problem_500():
    fig, axes = blank(12.6, 7.4, (0, 18), (0, 10.2))
    ax = axes[0]
    # (a) two stages: 20 N on 2 cm^2 -> 10 cm^2 (100 N), rod, 2 cm^2 -> 10 cm^2 (500 N)
    label(ax, 0.3, 9.7, "а", fs=14, ha="left")
    label(ax, 0.3, 4.6, "б", fs=14, ha="left")
    y = 8.0
    ax.add_patch(Rectangle((1.6, y - 0.25), 2.4, 0.5, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((1.6, y - 0.25), 0.25, 0.5, fc=GREY, ec=INK, lw=1.4, zorder=5))
    ax.add_patch(Rectangle((4.0, y - 0.8), 2.0, 1.6, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((4.0 + 1.75, y - 0.8), 0.25, 1.6, fc=GREY, ec=INK, lw=1.4, zorder=5))
    # rod from the big piston to the second small piston
    line(ax, [6.0, 8.0], [y, y], lw=3.5, color=GREY, z=4)
    ax.add_patch(Rectangle((8.0, y - 0.25), 2.4, 0.5, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((8.0, y - 0.25), 0.25, 0.5, fc=GREY, ec=INK, lw=1.4, zorder=5))
    ax.add_patch(Rectangle((10.4, y - 0.8), 2.0, 1.6, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((10.4 + 1.75, y - 0.8), 0.25, 1.6, fc=GREY, ec=INK, lw=1.4, zorder=5))
    arrow(ax, (0.7, y), (1.55, y), color=C_F, lw=2.6, scale=14)
    label(ax, 0.75, y + 0.55, "$20$ Н", fs=11.5, color=C_F)
    label(ax, 2.8, y + 0.7, "$2$ см$^2$", fs=10.5, color=GREY)
    label(ax, 5.0, y + 1.25, "$10$ см$^2$", fs=10.5, color=GREY)
    label(ax, 5.05, y - 1.35, "$100$ Н\n(в $5$ раз больше)", fs=10, color=C_F)
    label(ax, 7.0, y + 0.45, "шток\n$100$ Н", fs=10, color=C_F)
    label(ax, 9.2, y + 0.7, "$2$ см$^2$", fs=10.5, color=GREY)
    label(ax, 11.4, y + 1.25, "$10$ см$^2$", fs=10.5, color=GREY)
    arrow(ax, (12.65, y), (13.7, y), color=C_F, lw=3.2, scale=16)
    ax.add_patch(Circle((14.6, y), 0.85, fc=METAL, ec=INK, lw=2, hatch="///", zorder=4))
    label(ax, 14.6, y - 1.35, "$500$ Н", fs=11.5, color=C_F)
    ax.text(15.8, y + 0.4, "$\\dfrac{500}{20} = 25$", fontsize=13, ha="left", va="center", color=INK)
    # panel b: 50 N on 1 cm^2 -> 10 cm^2 (500 N); rod; 2 cm^2 -> 10 cm^2 (2500 N)
    y = 3.4
    ax.add_patch(Rectangle((1.6, y - 0.2), 2.4, 0.4, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((1.6, y - 0.2), 0.25, 0.4, fc=GREY, ec=INK, lw=1.4, zorder=5))
    ax.add_patch(Rectangle((4.0, y - 0.8), 2.0, 1.6, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((4.0 + 1.75, y - 0.8), 0.25, 1.6, fc=GREY, ec=INK, lw=1.4, zorder=5))
    line(ax, [6.0, 8.0], [y, y], lw=3.5, color=GREY, z=4)
    ax.add_patch(Rectangle((8.0, y - 0.25), 2.4, 0.5, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((8.0, y - 0.25), 0.25, 0.5, fc=GREY, ec=INK, lw=1.4, zorder=5))
    ax.add_patch(Rectangle((10.4, y - 0.8), 2.0, 1.6, fc=FLUID, ec=INK, lw=2, zorder=3))
    ax.add_patch(Rectangle((10.4 + 1.75, y - 0.8), 0.25, 1.6, fc=GREY, ec=INK, lw=1.4, zorder=5))
    arrow(ax, (0.7, y), (1.55, y), color=C_F, lw=2.6, scale=14)
    label(ax, 0.75, y + 0.55, "$50$ Н", fs=11.5, color=C_F)
    label(ax, 2.8, y + 0.6, "$1$ см$^2$", fs=10.5, color=GREY)
    label(ax, 5.0, y + 1.25, "$10$ см$^2$", fs=10.5, color=GREY)
    label(ax, 5.05, y - 1.35, "$500$ Н\n(в $10$ раз больше)", fs=10, color=C_F)
    label(ax, 7.0, y + 0.45, "шток\n$500$ Н", fs=10, color=C_F)
    label(ax, 9.2, y + 0.7, "$2$ см$^2$", fs=10.5, color=GREY)
    label(ax, 11.4, y + 1.25, "$10$ см$^2$", fs=10.5, color=GREY)
    label(ax, 11.4, y - 1.35, "$2500$ Н\n(в $5$ раз больше)", fs=10, color=C_F)
    arrow(ax, (12.65, y), (13.7, y), color=C_F, lw=3.2, scale=16)
    ax.add_patch(Circle((14.6, y), 0.85, fc=METAL, ec=INK, lw=2, hatch="///", zorder=4))
    ax.text(15.8, y + 0.4, "$\\dfrac{2500}{50} = 50$", fontsize=13, ha="left", va="center", color=INK)
    save(fig, "press-problem-500.png")


def problem_19_14():
    fig, axes = blank(12.4, 5.8, (0, 17.6), (0, 8.4))
    ax = axes[0]
    x1, w1, x2, w2 = 1.6, 1.0, 4.6, 4.6
    # solid: start, dashed: end; h_1 = 24 cm is 1.8 units, h_2 = 4 cm is 0.3 units
    vessels(ax, x1, w1, x2, w2, 0.8, 6.4, 4.4, 3.3, dashed=[(x1, w1, 2.6), (x2, w2, 3.6)])  # h_2 = 4 cm is 0.3 units
    ax.add_patch(Rectangle((x2 + 1.1, 3.52), 2.4, 0.9, fc=METAL, ec=INK, lw=2, hatch="///", zorder=6))
    ax.add_patch(Rectangle((x2 + 1.1, 3.82), 2.4, 0.9, fc="none", ec=GREY, lw=1.4, ls="--", zorder=6))
    label(ax, x2 + 2.3, 4.0, "$300$ кг", fs=10.5, color=INK, zorder=8, bbox=dict(boxstyle="square,pad=0.15", fc=PAPER, ec="none"))
    dim_v(ax, x1 - 0.5, 2.6, 4.4, "$h_1 = 24$ см", side="left", fs=11)
    dim_v(ax, x2 + w2 + 0.5, 3.3, 3.6, "$h_2 = 4$ см", side="right", fs=11)
    arrow(ax, (x1 + w1 / 2, 6.4), (x1 + w1 / 2, 4.85), color=C_F, lw=2.6, scale=14)
    label(ax, x1 + w1 / 2 + 0.4, 5.9, "$F_1 = ?$", fs=12, color=C_F, ha="left")
    label(ax, x1 + w1 / 2, 7.05, "$S_1$", fs=12, color=GREY)
    label(ax, x2 + w2 / 2, 7.05, "$S_2$", fs=12, color=GREY)
    label(ax, 6.9, 0.25, "сплошная линия: начало, пунктир: конец", fs=10, color=GREY)
    ax.text(12.6, 5.6, "$\\dfrac{P}{F_1} = \\dfrac{h_1}{h_2}$", fontsize=14, ha="left", va="center")
    ax.text(12.6, 3.5, "$F_1 = mg\\,\\dfrac{h_2}{h_1} = 500$ Н", fontsize=13, ha="left", va="center", color=C_F)
    save(fig, "press-problem-19-14.png")


def problem_19_22():
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    n = np.linspace(0, 1300, 100)
    m, g, h1 = 2100.0, 10.0, 0.10
    for f1, c in ((150, GREY), (300, C_F), (600, C_P)):
        ax.plot(n, n * h1 * f1 / (m * g), color=c, lw=2.3, label="$F_1 = %d$ Н" % f1)
    ax.plot([1050], [1.5], "o", color=C_F, ms=8, zorder=5)
    ax.annotate("$1050$ ходов, $1{,}5$ м", (1050, 1.5), (560, 1.98), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    ax.axhline(1.5, color=GREY, lw=1, ls=":")
    ax.set_xlabel("число ходов малого поршня $N$")
    ax.set_ylabel("высота подъёма $H$, м")
    ax.set_title("Подъём растёт с числом ходов (ход $10$ см, $2100$ кг)", fontsize=11.5)
    ax.set_xlim(0, 1300)
    ax.set_ylim(0, 3.2)
    ax.grid(color=GRID, lw=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    save(fig, "press-problem-19-22.png")


def problem_marom():
    fig, axes = blank(10.6, 4.6, (0, 15.0), (0, 6.4))
    ax = axes[0]
    y = 2.9
    x0, x1 = 1.2, 8.0
    fill(ax, 2.6, x1, y - 1.1, y + 1.1, fc=WATER)
    line(ax, [x0, x1], [y + 1.1, y + 1.1], lw=2.4)
    line(ax, [x0, x1], [y - 1.1, y - 1.1], lw=2.4)
    line(ax, [x1, x1], [y + 1.1, y + 0.25], lw=2.4)
    line(ax, [x1, x1], [y - 1.1, y - 0.25], lw=2.4)
    line(ax, [x1, 10.4], [y + 0.25, y + 0.25], lw=2.4)
    line(ax, [x1, 10.4], [y - 0.25, y - 0.25], lw=2.4)
    ax.add_patch(Rectangle((x1, y - 0.25), 1.2, 0.5, fc=tint(SKY, 0.8), ec=WATER_EDGE, lw=1.4, hatch="////", zorder=4))
    ax.add_patch(Rectangle((2.4, y - 1.08), 0.28, 2.16, fc=GREY, ec=INK, lw=1.6, zorder=5))
    line(ax, [x0, 2.4], [y, y], lw=3.2, z=5)
    arrow(ax, (0.2, y), (1.3, y), color=C_F, lw=2.8, scale=15)
    label(ax, 0.7, y + 0.6, "$F_1 = 10$ Н", fs=11, color=C_F)
    label(ax, 5.1, y + 1.55, "$S_1 = 25$ см$^2$", fs=11, color=GREY)
    label(ax, 9.3, y + 0.9, "$S_2 = 10$ мм$^2$", fs=11, color=GREY)
    label(ax, 9.3, y - 0.9, "затвердевший\nкусочек воды", fs=10, color=WATER_EDGE)
    arrow(ax, (9.4, y), (10.9, y), color=C_F, lw=1.8, scale=9)
    label(ax, 11.3, y, "$F_2$", fs=13, color=C_F, ha="left")
    ax.text(11.9, y + 1.3, "$F_2 = F_1\\dfrac{S_2}{S_1}$", fontsize=13, ha="left", va="center")
    ax.text(11.9, y - 0.5, "$= 10\\ \\mathrm{Н} \\cdot \\dfrac{10}{2500} = 0{,}04\\ \\mathrm{Н}$", fontsize=13, ha="left", va="center", color=C_F)
    save(fig, "press-problem-marom-12.png")


def problem_boat():
    fig, axes = blank(12.4, 5.2, (0, 18.4), (0, 7.6))
    ax = axes[0]
    for ox, after in ((0.6, False), (9.6, True)):
        wl = 3.9 if not after else 3.55
        fill(ax, ox, ox + 7.6, 0.6, wl, fc=WATER)
        line(ax, [ox, ox, ox + 7.6, ox + 7.6], [5.6, 0.6, 0.6, 5.6], lw=2.4)
        line(ax, [ox + 0.02, ox + 7.58], [wl, wl], color=WATER_EDGE, lw=2.2, z=2)
        if after:
            line(ax, [ox - 0.6, ox + 8.2], [3.9, 3.9], color=GREY, lw=1.2, ls="--", z=3)
            label(ax, ox + 8.25, 3.9, "было", fs=10, color=GREY, ha="left")
            dim_v(ax, ox + 7.0, 3.55, 3.9, "", side="right")
        # boat
        by = wl - 0.55 if not after else wl - 0.4
        bx = ox + 2.6
        ax.add_patch(Polygon([(bx, by + 0.7), (bx + 3.2, by + 0.7), (bx + 2.7, by), (bx + 0.5, by)], closed=True, fc=LIGHT, ec=INK, lw=2, zorder=6))
        ax.add_patch(Circle((bx + 0.6, by + 1.1), 0.22, fc=LIGHT, ec=INK, lw=1.6, zorder=6))
        line(ax, [bx + 0.6, bx + 0.6], [by + 0.7, by + 0.9], lw=1.6, z=6)
        if not after:
            ax.add_patch(Circle((bx + 2.0, by + 1.0), 0.5, fc=tint(COPPER, 0.55), ec=INK, lw=2, zorder=7))
            label(ax, ox + 3.8, 5.3, "камень в лодке", fs=11, color=INK)
        else:
            ax.add_patch(Circle((ox + 5.9, 1.25), 0.55, fc=tint(COPPER, 0.55), ec=INK, lw=2, zorder=7))
            label(ax, ox + 3.8, 5.3, "камень на дне, уровень воды ниже", fs=11, color=INK)
    label(ax, 4.4, 6.8, "до броска", fs=12.5)
    label(ax, 13.4, 6.8, "после броска", fs=12.5)
    save(fig, "press-problem-boat.png")


if __name__ == "__main__":
    scheme()
    force_lines()
    problems_map()
    travel()
    travel_graph()
    syringes()
    machine()
    brakes()
    problem_19_4()
    problem_jack()
    problem_500()
    problem_19_14()
    problem_19_22()
    problem_marom()
    problem_boat()
