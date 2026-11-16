"""Figures for the note "Сообщающиеся сосуды" (course Физика 7-9, lessons 49, 50, 54).

Run: python3 pressure_vessels.py
PNG files go to content/06. Давление/00. Вложения/, prefix vessels-*.
Helpers and the colour code come from pressure_gas_pascal.py: force red, pressure blue.
Liquids: water light blue, brine darker blue, kerosene yellow, machine oil orange, mercury grey.
Densities on the graphs come from the lessons (kerosene 800, water 1000, brine 1240 kg/m^3);
the mercury layer in vessels-utube-mercury.png is drawn without a density, as in the lesson.
"""
import numpy as np
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from pressure_gas_pascal import (
    C_F,
    C_P,
    GREY,
    INK,
    LIGHT,
    WATER,
    WATER_EDGE,
    arrow,
    blank,
    ground_hatch,
    label,
    line,
    rect,
    save,
)

from theme import BLUE, COPPER, GREEN, METAL, PAPER, SKY, VIOLET, WARM, keep_dots, tint

BRINE = tint(BLUE, 0.6)
KERO = tint(WARM, 0.6)
OIL = tint(WARM, 0.45)
MERCURY = METAL
GATE = COPPER
G_ACC = 10  # N/kg, as used in the lessons' estimates


def fill_poly(ax, pts, fc, ec="none", z=2, alpha=1.0, lw=0):
    p = Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha)
    ax.add_patch(p)
    return p


def open_vessel(ax, x0, x1, y0, top, lw=2.2):
    """Walls and bottom of an open rectangular vessel."""
    line(ax, [x0, x0, x1, x1], [top, y0, y0, top], lw=lw)


def liquid(ax, x0, x1, y0, y1, fc=WATER, z=1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="none", zorder=z))


def surface(ax, x0, x1, y, color=WATER_EDGE, lw=1.6):
    line(ax, [x0, x1], [y, y], color=color, lw=lw, z=3)


def dim(ax, x, y0, y1, text, side=-1, fs=11, color=INK, off=0.28):
    arrow(ax, (x, y0 + 0.02), (x, y1 - 0.02), color=color, lw=1.3, style="<|-|>", scale=9)
    label(ax, x + side * off, (y0 + y1) / 2, text, fs=fs, color=color, ha="right" if side < 0 else "left")


def hline(ax, x0, x1, y, color=GREY, ls="--", lw=1.3, z=4):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, ls=ls, zorder=z)


def tap(ax, x, y, closed=True, size=0.22):
    """Tap symbol on a horizontal tube."""
    ax.add_patch(Polygon([(x - size, y + 0.02), (x + size, y + 0.02), (x, y - size * 1.1)], fc=PAPER, ec=INK, lw=1.6, zorder=6))
    line(ax, [x, x], [y + 0.02, y + size * 1.4], lw=1.6, z=6)
    line(ax, [x - size * 0.7, x + size * 0.7], [y + size * 1.4, y + size * 1.4], lw=1.6, z=6)


def two_vessels(ax, xl, xr, tube_y, floor, top, tube_h=0.3):
    """Two rectangular vessels joined by a horizontal tube with a tap. xl, xr are (x0, x1) pairs."""
    line(ax, [xl[0], xl[0], xl[1]], [top, floor, floor], lw=2.2)
    line(ax, [xr[0], xr[1], xr[1]], [floor, floor, top], lw=2.2)
    line(ax, [xl[1], xl[1]], [floor, top], lw=2.2)
    line(ax, [xr[0], xr[0]], [floor, top], lw=2.2)


# ------------------------------------------------------------- lesson 49


def two_liquids_equilibrium():
    fig, (ax,) = blank(8.6, 6.2, (-1.6, 7.6), (-1.2, 6.4))
    floor, top = 0.0, 4.6
    xl, xr = (0.0, 2.6), (4.0, 5.2)
    h1, h2 = 3.5, 2.8
    # tube between the vessels (below the walls), tap in the middle
    ax.add_patch(Rectangle((xl[1], 0.0), xr[0] - xl[1], 0.32, fc=WATER, ec="none", zorder=1))
    liquid(ax, xl[0], xl[1], floor, h1, KERO)
    liquid(ax, xr[0], xr[1], floor, h2, BRINE)
    # vessel walls
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, floor, floor, top], lw=2.4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, floor, floor, top], lw=2.4)
    # tube walls: erase the floor segment between the vessels by drawing the tube lines
    ax.add_patch(Rectangle((xl[1] - 0.01, 0.01), xr[0] - xl[1] + 0.02, 0.3, fc=PAPER, ec="none", zorder=2))
    liquid(ax, xl[1], xr[0], 0.02, 0.3, WATER, z=3)
    line(ax, [xl[1], xr[0]], [0.32, 0.32], lw=2.4, z=4)
    line(ax, [xl[1], xr[0]], [0.0, 0.0], lw=2.4, z=4)
    tap(ax, 3.3, 0.32)
    label(ax, 3.3, 1.0, "кран", fs=11, color=GREY)
    surface(ax, xl[0], xl[1], h1, color=COPPER)
    surface(ax, xr[0], xr[1], h2, color=SKY)
    dim(ax, -0.35, floor, h1, "$h_1$", side=-1, fs=14)
    dim(ax, 5.55, floor, h2, "$h_2$", side=1, fs=14)
    label(ax, 1.3, 2.0, r"$\rho_1$", fs=16)
    label(ax, 4.6, 1.5, r"$\rho_2$", fs=16)
    label(ax, 1.3, 4.2, "сосуд 1", fs=11, color=GREY)
    label(ax, 4.6, 4.2, "сосуд 2", fs=11, color=GREY)
    # bottom pressures
    arrow(ax, (1.3, -0.95), (1.3, -0.12), color=C_P, lw=1.8)
    arrow(ax, (4.6, -0.95), (4.6, -0.12), color=C_P, lw=1.8)
    label(ax, 1.3, -1.12, "$p_1$ на дно", fs=12, color=C_P)
    label(ax, 4.6, -1.12, "$p_2$ на дно", fs=12, color=C_P)
    label(ax, 2.9, 5.9, r"$p_1=p_2 \Rightarrow \rho_1 g h_1=\rho_2 g h_2$", fs=13)
    label(ax, 2.9, 5.35, r"$\rho_1<\rho_2 \Rightarrow h_1>h_2$", fs=13, color=C_F)
    save(fig, "vessels-two-liquids-equilibrium.png")


def shapes_one_liquid():
    fig, (ax,) = blank(9.6, 4.4, (-0.4, 9.6), (-0.7, 5.0))
    y0, ytop, level = 0.4, 4.4, 3.2
    yy = np.linspace(y0, ytop, 60)
    centers = (1.6, 4.4, 7.2)

    def w1(y):
        return 0.45 + 0.12 * (y - y0)

    def w2(y):
        return 0.5 + 0.3 * np.sin(np.pi * (y - y0) / (ytop - y0))

    def w3(y):
        return 0.5 + 0.18 * np.sin(2.6 * (y - y0)) + 0.04 * (y - y0)

    widths = (w1, w2, w3)
    for c, w in zip(centers, widths):
        yl = yy[yy <= level]
        left = [(c - w(y), y) for y in yl]
        right = [(c + w(y), y) for y in yl[::-1]]
        fill_poly(ax, left + right, WATER, z=1)
        line(ax, [c - w(y) for y in yy], list(yy), lw=2.2)
        line(ax, [c + w(y) for y in yy], list(yy), lw=2.2)
    # common channel
    x_a, x_b = centers[0] - w1(y0), centers[2] + w3(y0)
    ax.add_patch(Rectangle((x_a, 0.0), x_b - x_a, y0, fc=WATER, ec="none", zorder=1))
    line(ax, [x_a, x_b], [0.0, 0.0], lw=2.2)
    line(ax, [x_a, x_a], [0.0, y0], lw=2.2)
    line(ax, [x_b, x_b], [0.0, y0], lw=2.2)
    # closing segments between vessels at the channel top
    for a, b in ((0, 1), (1, 2)):
        xa = centers[a] + widths[a](y0)
        xb = centers[b] - widths[b](y0)
        line(ax, [xa, xb], [y0, y0], lw=2.2)
    hline(ax, x_a - 0.1, x_b + 0.1, level, color=C_F, lw=1.6)
    label(ax, x_b + 0.6, level, "одна высота\nсвободных поверхностей", fs=9.5, color=C_F, ha="left")
    ax.set_xlim(-0.4, 11.4)
    label(ax, 4.5, -0.45, "Форма и ширина сосудов не важны: жидкость одна, поверхности на одном уровне", fs=10, color=INK)
    save(fig, "vessels-shapes-one-liquid.png")


def syringe_tilted(ax, p0, w, theta, T, level, fill, edge, plunger=False):
    """Tilted tube: P0 bottom-left corner, w width, theta tilt from vertical, T length, level = y of the surface."""
    d = np.array([np.sin(theta), np.cos(theta)])
    n = np.array([np.cos(theta), -np.sin(theta)])
    p0 = np.array(p0, float)
    p1 = p0 + w * n
    t0 = (level - p0[1]) / d[1]
    t1 = (level - p1[1]) / d[1]
    if fill is not None:
        fill_poly(ax, [p0, p1, p1 + t1 * d, p0 + t0 * d], fill, z=1)
        line(ax, [(p0 + t0 * d)[0], (p1 + t1 * d)[0]], [level, level], color=edge, lw=1.6, z=3)
    pts = [p0 + T * d, p0, p1, p1 + T * d]
    line(ax, [q[0] for q in pts], [q[1] for q in pts], lw=2.2)


def syringes_brine():
    fig, axes = blank(12.0, 4.8, (-0.5, 5.6), (-1.2, 5.2), n=3)
    titles = ("Вода в обоих", "Правый наклонён", "Слева вода, справа раствор соли")
    lvl = 3.0
    for k, ax in enumerate(axes):
        # left (wide) tube: vertical
        wl, wr = 1.3, 0.75
        xl0, xr0 = 0.0, 2.9
        theta = 0.0 if k != 1 else np.radians(20)
        left_fill, right_fill = WATER, WATER if k < 2 else BRINE
        level_r = lvl if k < 2 else 2.35
        # joining tube (flexible) along the bottom
        pl = (xl0 + wl / 2, 0.0)
        pr = (xr0 + (wr / 2) * np.cos(theta), -(wr / 2) * np.sin(theta))
        # draw liquids and walls
        syringe_tilted(ax, (xl0, 0.0), wl, 0.0, 4.6, lvl, left_fill, WATER_EDGE)
        syringe_tilted(ax, (xr0, 0.0), wr, theta, 4.6, level_r, right_fill, WATER_EDGE if k < 2 else SKY)
        # connecting tube
        xs = np.array([pl[0], pl[0], (pl[0] + pr[0]) / 2, pr[0], pr[0]])
        ys = np.array([0.0, -0.55, -0.7, -0.55, pr[1]])
        ax.plot(xs, ys, color=INK, lw=7, solid_capstyle="round", zorder=2)
        ax.plot(xs, ys, color=WATER if k < 2 else tint(SKY, 0.6), lw=4.2, solid_capstyle="round", zorder=2.5)
        hline(ax, -0.3, 5.3, lvl, color=C_F, lw=1.4)
        if k == 2:
            hline(ax, -0.3, 5.3, level_r, color=C_F, lw=1.4)
            dim(ax, 4.3, level_r, lvl, r"$h_1 > h_2$", side=1, fs=11)
            label(ax, 0.65, 1.5, r"$\rho_1$", fs=15)
            label(ax, 4.0, 1.2, r"$\rho_2 > \rho_1$", fs=13, ha="left")
        label(ax, 2.6, -1.0, titles[k], fs=11.5)
    save(fig, "vessels-syringes-brine.png")


def carpenter_and_liquid_level():
    fig = plt.figure(figsize=(12.0, 4.6))
    axA = fig.add_axes([0.0, 0.02, 0.36, 0.96])
    axA.set_xlim(0, 4.2)
    axA.set_ylim(0, 4.6)
    axA.set_aspect("equal")
    axA.axis("off")
    # carpenter's level: box with a slightly bent tube
    rect(axA, 0.2, 1.4, 3.8, 1.0, fc=tint(WARM, 0.85), ec=INK, lw=2.0)
    xs = np.linspace(0.55, 3.65, 60)
    ys = 1.9 + 0.3 * (1 - ((xs - 2.1) / 1.55) ** 2)
    axA.plot(xs, ys + 0.13, color=INK, lw=1.6, zorder=6)
    axA.plot(xs, ys - 0.13, color=INK, lw=1.6, zorder=6)
    axA.add_patch(Circle((2.1, 2.2), 0.11, fc=PAPER, ec=INK, lw=1.4, zorder=7))
    label(axA, 2.1, 3.1, "пузырёк", fs=11)
    arrow(axA, (2.1, 2.95), (2.1, 2.42), lw=1.4, scale=10)
    label(axA, 2.1, 0.8, "плотницкий уровень:\nпузырёк в середине —\nповерхность горизонтальна", fs=10.5)
    label(axA, 2.1, 4.25, "Плотницкий уровень", fs=12)
    axB = fig.add_axes([0.38, 0.02, 0.62, 0.96])
    axB.set_xlim(-0.6, 10.6)
    axB.set_ylim(-1.2, 5.2)
    axB.set_aspect("equal")
    axB.axis("off")
    # foundation, right end slightly lower (exaggerated)
    fx = np.array([0.0, 9.6])
    fy = np.array([3.0, 2.5])
    fill_poly(axB, [(0, 3.0), (9.6, 2.5), (9.6, 1.8), (0, 1.8)], tint(WARM, 0.9), z=1)
    line(axB, list(fx), list(fy), lw=2.4)
    for x in np.arange(0.3, 9.6, 0.5):
        line(axB, [x, x - 0.22], [1.8, 1.55], color=GREY, lw=1)
    # tube (thick, flexible) below the foundation
    tx = np.array([0.0, 0.0, 1.0, 4.8, 8.6, 9.6, 9.6])
    ty = np.array([3.05, 0.5, 0.15, 0.05, 0.15, 0.5, 3.05])
    axB.plot(tx, ty, color=INK, lw=8, solid_capstyle="round", zorder=2)
    axB.plot(tx, ty, color=WATER, lw=5, solid_capstyle="round", zorder=2.5)
    # water levels: left at A, right slightly above B
    hline(axB, 0.0, 9.6, 3.0, color=C_F, lw=1.6)
    axB.add_patch(Circle((0.0, 3.0), 0.07, fc=C_F, ec=C_F, zorder=6))
    axB.add_patch(Circle((9.6, 2.5), 0.07, fc=INK, ec=INK, zorder=6))
    label(axB, -0.35, 3.45, "$A$", fs=15)
    label(axB, 9.9, 2.1, "$B$", fs=15)
    dim(axB, 10.15, 2.5, 3.0, r"$\Delta h$", side=1, fs=13, color=C_F)
    label(axB, 4.8, 4.3, "Жидкостный уровень: вода в гибкой трубке", fs=12)
    label(axB, 4.8, 3.55, "уровни воды в концах трубки — на одной высоте", fs=10.5, color=C_F)
    label(axB, 4.8, 2.1, "фундамент дома", fs=11, color=INK)
    save(fig, "vessels-levels-carpenter-liquid.png")


def lock_stages():
    fig = plt.figure(figsize=(13.0, 7.6))
    up, low = 3.0, 1.0
    titles = (
        "1. Судно в верхнем бьефе",
        "2. Открыт верхний канал: шлюз наполняется",
        "3. Уровни равны: ворота открыты, судно входит",
        "4. Верхние закрыты, открыт нижний канал: уровень падает",
        "5. Уровни равны: нижние ворота открыты, судно выходит",
    )
    # (upper gate open, upper channel open, lower gate open, lower channel open, chamber level, ship x, ship level)
    stages = (
        (False, False, False, False, low, 1.0, up),
        (False, True, False, False, up, 1.0, up),
        (True, False, False, False, up, 3.25, up),
        (False, False, False, True, low, 3.25, low),
        (False, False, True, False, low, 5.5, low),
    )
    pos = [(0.005, 0.51), (0.34, 0.51), (0.675, 0.51), (0.005, 0.03), (0.34, 0.03)]
    for (px, py), title, st in zip(pos, titles, stages):
        ax = fig.add_axes([px, py, 0.32, 0.42])
        ax.set_xlim(-0.2, 6.7)
        ax.set_ylim(-0.75, 4.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ug, uc, lg, lc, chl, sx, sl = st
        # ground
        fill_poly(ax, [(-0.2, -0.75), (6.7, -0.75), (6.7, 0.0), (4.5, 0.0), (4.5, 0.0), (2.0, 0.0), (2.0, low), (-0.2, low)], tint(WARM, 0.9), z=0.5)
        line(ax, [-0.2, 2.0, 2.0], [low, low, 0.0], lw=2.0)
        line(ax, [2.0, 4.5], [0.0, 0.0], lw=2.0)
        line(ax, [4.5, 6.7], [0.0, 0.0], lw=2.0)
        # channels: upper (shaft at x=1.3 -> pipe -> shaft at x=3.0), lower (3.8 -> 5.4)
        for (xa, xb, ya, opened, ftop_a, ftop_b) in ((1.3, 3.0, -0.45, uc, low, 0.0), (3.8, 5.4, -0.45, lc, 0.0, 0.0)):
            pipe = [(xa - 0.1, ftop_a), (xa - 0.1, ya - 0.1), (xb + 0.1, ya - 0.1), (xb + 0.1, ftop_b), (xb - 0.1, ftop_b), (xb - 0.1, ya + 0.1), (xa + 0.1, ya + 0.1), (xa + 0.1, ftop_a)]
            fill_poly(ax, pipe, WATER if opened else PAPER, ec=INK, lw=1.4, z=2)
            xm = (xa + xb) / 2
            ax.add_patch(Rectangle((xm - 0.12, ya - 0.14), 0.24, 0.28, fc=GREEN if opened else C_F, ec=INK, lw=1.0, zorder=6))
            if opened:
                arrow(ax, (xm - 0.55, ya), (xm - 0.25, ya), color=C_F, lw=1.6, scale=9, z=7)
        # water
        fill_poly(ax, [(-0.2, low), (2.0, low), (2.0, up), (-0.2, up)], WATER, z=1)
        fill_poly(ax, [(2.15, 0.0), (4.35, 0.0), (4.35, chl), (2.15, chl)], WATER, z=1)
        fill_poly(ax, [(4.5, 0.0), (6.7, 0.0), (6.7, low), (4.5, low)], WATER, z=1)
        for x0, x1, y in ((-0.2, 2.0, up), (2.15, 4.35, chl), (4.5, 6.7, low)):
            line(ax, [x0, x1], [y, y], color=WATER_EDGE, lw=1.4, z=3)
        # gates
        for x0, isopen in ((2.0, ug), (4.35, lg)):
            if isopen:
                ax.add_patch(Rectangle((x0, 0.0), 0.15, 3.5, fc="none", ec=GATE, lw=1.3, ls="--", zorder=5))
            else:
                ax.add_patch(Rectangle((x0, 0.0), 0.15, 3.5, fc=GATE, ec=INK, lw=1.4, zorder=5))
        # ship
        hull = [(sx - 0.55, sl + 0.22), (sx + 0.55, sl + 0.22), (sx + 0.4, sl - 0.16), (sx - 0.4, sl - 0.16)]
        fill_poly(ax, hull, tint(METAL, 0.3), ec=INK, lw=1.2, z=8)
        ax.add_patch(Rectangle((sx - 0.15, sl + 0.22), 0.3, 0.22, fc=tint(METAL, 0.75), ec=INK, lw=1.0, zorder=8))
        # flows
        if st == stages[1]:
            arrow(ax, (1.7, 2.0), (2.75, 1.4), color=C_F, lw=1.4, scale=9, z=9)
        if st == stages[3]:
            arrow(ax, (4.0, 0.7), (5.3, 0.3), color=C_F, lw=1.4, scale=9, z=9)
        label(ax, 3.25, 4.0, title, fs=9.6)
        label(ax, 0.9, 1.9, "верхний\nбьеф", fs=8.5, color=GREY)
        label(ax, 5.6, 2.0, "нижний\nбьеф", fs=8.5, color=GREY)
    # legend panel
    ax = fig.add_axes([0.675, 0.03, 0.32, 0.42])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.add_patch(Rectangle((0.3, 3.4), 0.15, 0.7, fc=GATE, ec=INK, lw=1.4))
    label(ax, 0.75, 3.75, "ворота закрыты", fs=10, ha="left")
    ax.add_patch(Rectangle((0.3, 2.4), 0.15, 0.7, fc="none", ec=GATE, lw=1.3, ls="--"))
    label(ax, 0.75, 2.75, "ворота открыты", fs=10, ha="left")
    ax.add_patch(Rectangle((0.3, 1.55), 0.3, 0.3, fc=C_F, ec=INK, lw=1.0))
    label(ax, 0.9, 1.7, "канал закрыт", fs=10, ha="left")
    ax.add_patch(Rectangle((0.3, 0.75), 0.3, 0.3, fc=GREEN, ec=INK, lw=1.0))
    label(ax, 0.9, 0.9, "канал открыт", fs=10, ha="left")
    save(fig, "vessels-lock-stages.png")


# ------------------------------------------------------------- lesson 50


def problems_1710_1711():
    fig, axes = blank(12.0, 4.9, (-0.4, 6.2), (-1.0, 4.2), n=2)
    ax = axes[0]
    # 17.10: wide right vessel, narrow left, horizontal tube, equal levels
    xl, xr = (0.0, 1.5), (3.0, 5.6)
    lev, top = 2.9, 3.7
    liquid(ax, *xl, 0.0, lev)
    liquid(ax, *xr, 0.0, lev)
    ax.add_patch(Rectangle((xl[1], 0.02), xr[0] - xl[1], 0.3, fc=PAPER, ec="none", zorder=2))
    liquid(ax, xl[1], xr[0], 0.02, 0.3, WATER, z=3)
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    ax.add_patch(Rectangle((xl[1] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    ax.add_patch(Rectangle((xr[0] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    line(ax, [xl[1], xr[0]], [0.32, 0.32], lw=2.4, z=4)
    line(ax, [xl[1], xr[0]], [0.0, 0.0], lw=2.4, z=4)
    tap(ax, 2.25, 0.32)
    hline(ax, xl[0] - 0.2, xr[1] + 0.2, lev, color=C_F)
    dim(ax, -0.35, 0.0, lev, "$h_1$", side=-1, fs=13)
    dim(ax, 5.95, 0.0, lev, "$h_2$", side=1, fs=13)
    label(ax, 0.75, 1.5, "меньше\nводы", fs=10, color=GREY)
    label(ax, 4.3, 1.5, "больше воды", fs=10, color=GREY)
    label(ax, 2.9, -0.55, "17.10: $h_1=h_2 \\Rightarrow$ вода не перетекает", fs=12)
    keep_dots(ax.texts[-1])
    # 17.11: inclined tube
    ax = axes[1]
    xl, xr = (0.0, 1.8), (3.2, 5.0)
    lev, top = 2.9, 3.7
    liquid(ax, *xl, 0.0, lev)
    liquid(ax, *xr, 0.0, lev)
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    a = np.array([1.5, 1.9])
    b = np.array([3.5, 0.6])
    dvec = (b - a) / np.linalg.norm(b - a)
    nvec = np.array([-dvec[1], dvec[0]]) * 0.17
    pipe = [a + nvec, b + nvec, b - nvec, a - nvec]
    fill_poly(ax, pipe, WATER, ec=INK, lw=2.0, z=5)
    tapc = (a + b) / 2
    ax.add_patch(Rectangle((tapc[0] - 0.13, tapc[1] - 0.13), 0.26, 0.26, fc=PAPER, ec=INK, lw=1.6, zorder=7))
    label(ax, tapc[0] + 0.42, tapc[1] + 0.35, "кран", fs=10.5, color=GREY)
    hline(ax, -0.2, 5.2, lev, color=C_F)
    line(ax, [tapc[0], tapc[0]], [tapc[1] - 0.45, tapc[1] + 0.45], color=C_P, lw=1.6, z=8, ls=":")
    dim(ax, tapc[0] - 0.65, tapc[1], lev, "$d$", side=-1, fs=12, color=C_P)
    label(ax, 2.6, -0.55, "17.11: та же глубина по обе стороны крана $\\Rightarrow$ течения нет", fs=12)
    keep_dots(ax.texts[-1])
    save(fig, "vessels-problems-1710-1711.png")


def problems_1716_1717():
    fig = plt.figure(figsize=(13.0, 5.0))
    axs = [fig.add_axes([0.0 + 0.335 * i, 0.02, 0.33, 0.96]) for i in range(3)]
    for ax in axs:
        ax.set_xlim(-0.5, 6.2)
        ax.set_ylim(-1.0, 4.4)
        ax.set_aspect("equal")
        ax.axis("off")
    # 17.16 initial: kerosene left, water right, equal heights
    ax = axs[0]
    xl, xr, lev, top = (0.0, 2.0), (3.4, 5.4), 2.9, 3.8
    liquid(ax, *xl, 0.0, lev, KERO)
    liquid(ax, *xr, 0.0, lev, WATER)
    ax.add_patch(Rectangle((xl[1], 0.02), xr[0] - xl[1], 0.3, fc=PAPER, ec="none", zorder=2))
    liquid(ax, xl[1], xr[0], 0.02, 0.3, WATER, z=3)
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    ax.add_patch(Rectangle((xl[1] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    ax.add_patch(Rectangle((xr[0] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    line(ax, [xl[1], xr[0]], [0.32, 0.32], lw=2.4, z=4)
    line(ax, [xl[1], xr[0]], [0.0, 0.0], lw=2.4, z=4)
    tap(ax, 2.7, 0.32)
    hline(ax, -0.2, 5.6, lev, color=C_F)
    label(ax, 1.0, 1.6, "керосин\n" + r"$\rho_1$", fs=11)
    label(ax, 4.4, 1.6, "вода\n" + r"$\rho_2$", fs=11)
    label(ax, 2.7, 4.2, r"$h_1=h_2$, $\rho_1<\rho_2$", fs=11.5)
    label(ax, 2.7, -0.75, "17.16 до открытия крана", fs=11.5)
    keep_dots(ax.texts[-1])
    # 17.16 after: water under kerosene on the left
    ax = axs[1]
    # kerosene keeps its volume (2.9); water 0.29 + 2.61 = 2.9; bottom pressures 0.8*2.9 + 0.29 = 2.61
    hl_w, hl_k = 0.29, 2.9
    hr = 2.61
    liquid(ax, *xl, 0.0, hl_w, WATER)
    liquid(ax, *xl, hl_w, hl_w + hl_k, KERO)
    liquid(ax, *xr, 0.0, hr, WATER)
    ax.add_patch(Rectangle((xl[1], 0.02), xr[0] - xl[1], 0.3, fc=PAPER, ec="none", zorder=2))
    liquid(ax, xl[1], xr[0], 0.02, 0.3, WATER, z=3)
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    ax.add_patch(Rectangle((xl[1] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    ax.add_patch(Rectangle((xr[0] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
    line(ax, [xl[1], xr[0]], [0.32, 0.32], lw=2.4, z=4)
    line(ax, [xl[1], xr[0]], [0.0, 0.0], lw=2.4, z=4)
    tap(ax, 2.7, 0.32)
    arrow(ax, (3.3, 0.17), (2.05, 0.17), color=C_F, lw=2.0, scale=12, z=9)
    label(ax, 2.7, -0.3, "течёт влево", fs=10.5, color=C_F)
    label(ax, 1.0, 2.6, "керосин\nплавает сверху", fs=10.5)
    label(ax, 4.4, 1.1, "вода", fs=11)
    label(ax, 2.7, 4.2, "схема, масштаб условный", fs=9.5, color=GREY)
    label(ax, 2.7, -0.75, "17.16 после: слой воды под керосином", fs=11.5)
    keep_dots(ax.texts[-1])
    # 17.17
    ax = axs[2]
    xl, xr, lev, top = (0.0, 1.9), (3.6, 5.5), 2.9, 3.8
    liquid(ax, *xl, 0.0, lev, WATER)
    liquid(ax, *xr, 0.0, lev, OIL)
    line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
    a = np.array([1.6, 1.9])
    b = np.array([3.9, 0.55])
    dvec = (b - a) / np.linalg.norm(b - a)
    nvec = np.array([-dvec[1], dvec[0]]) * 0.17
    fill_poly(ax, [a + nvec, b + nvec, b - nvec, a - nvec], WATER, ec=INK, lw=2.0, z=5)
    tapc = (a + b) / 2
    ax.add_patch(Rectangle((tapc[0] - 0.13, tapc[1] - 0.13), 0.26, 0.26, fc=PAPER, ec=INK, lw=1.6, zorder=7))
    hline(ax, -0.2, 5.7, lev, color=C_F)
    arrow(ax, (tapc[0] - 0.3, tapc[1] + 0.55), (tapc[0] + 0.4, tapc[1] + 0.12 - 0.3), color=C_F, lw=2.0, scale=12, z=9)
    label(ax, 0.95, 1.5, "вода\n" + r"$\rho_1$", fs=11)
    label(ax, 4.55, 1.6, "машинное\nмасло\n" + r"$\rho_2$", fs=10.5)
    label(ax, 2.75, 4.2, r"$h_1=h_2$, $\rho_1>\rho_2$", fs=11.5)
    label(ax, 2.75, -0.75, "17.17: жидкость потечёт вправо", fs=11.5)
    keep_dots(ax.texts[-1])
    save(fig, "vessels-problems-1716-1717.png")


def problem_1718_ball():
    fig, axes = blank(11.0, 4.6, (-0.4, 6.4), (-0.9, 4.4), n=2)
    for k, ax in enumerate(axes):
        xl, xr = (0.0, 2.0), (3.6, 5.6)
        lev0, top = 2.4, 3.9
        lev = lev0 if k == 0 else 2.65
        liquid(ax, *xl, 0.0, lev)
        liquid(ax, *xr, 0.0, lev)
        ax.add_patch(Rectangle((xl[1], 0.02), xr[0] - xl[1], 0.3, fc=PAPER, ec="none", zorder=2))
        liquid(ax, xl[1], xr[0], 0.02, 0.3, WATER, z=3)
        line(ax, [xl[0], xl[0], xl[1], xl[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
        line(ax, [xr[0], xr[0], xr[1], xr[1]], [top, 0.0, 0.0, top], lw=2.4, z=4)
        ax.add_patch(Rectangle((xl[1] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
        ax.add_patch(Rectangle((xr[0] - 0.015, 0.02), 0.03, 0.28, fc=WATER, ec="none", zorder=5))
        line(ax, [xl[1], xr[0]], [0.32, 0.32], lw=2.4, z=4)
        line(ax, [xl[1], xr[0]], [0.0, 0.0], lw=2.4, z=4)
        # ball
        if k == 0:
            ax.add_patch(Circle((1.0, lev0 + 0.72), 0.32, fc=OIL, ec=INK, lw=1.6, zorder=6))
            arrow(ax, (1.0, lev0 + 0.4), (1.0, lev0 + 0.05), color=GREY, lw=1.4, scale=9, z=7)
            label(ax, 2.8, -0.55, "до: шарик над водой", fs=11.5)
        else:
            ax.add_patch(Circle((1.0, lev + 0.06), 0.32, fc=OIL, ec=INK, lw=1.6, zorder=6))
            hline(ax, -0.3, 5.9, lev0, color=GREY, lw=1.2)
            hline(ax, -0.3, 5.9, lev, color=C_F, lw=1.5)
            dim(ax, 5.95, lev0, lev, r"$\Delta h$", side=1, fs=12, color=C_F)
            label(ax, 2.8, -0.55, "после: уровень вырос в обоих сосудах", fs=11.5)
        label(ax, 4.6, 1.3, "вода", fs=11, color=GREY)
    save(fig, "vessels-ball-floating.png")


def squeezed_vessel():
    fig, axes = blank(9.6, 5.4, (-0.6, 4.6), (-1.0, 5.2), n=2)
    ax = axes[0]
    liquid(ax, 0.3, 3.3, 0.0, 1.8)
    open_vessel(ax, 0.3, 3.3, 0.0, 4.4)
    dim(ax, 0.0, 0.0, 1.8, "$h$", side=-1, fs=13)
    arrow(ax, (1.8, -0.15), (1.8, -0.85), color=C_F, lw=2.6, scale=16)
    label(ax, 1.8, 3.4, "площадь дна $S$", fs=11)
    label(ax, 1.8, 2.6, "давление $p$", fs=11, color=C_P)
    label(ax, 1.8, -1.05, "$F = pS = mg$", fs=12, color=C_F)
    ax = axes[1]
    liquid(ax, 1.05, 2.55, 0.0, 3.6)
    open_vessel(ax, 1.05, 2.55, 0.0, 4.4)
    dim(ax, 0.8, 0.0, 3.6, "$2h$", side=-1, fs=13)
    arrow(ax, (1.8, -0.15), (1.8, -0.85), color=C_F, lw=2.6, scale=16)
    label(ax, 1.8, 4.75, "площадь дна $S/2$", fs=11)
    label(ax, 3.7, 2.0, "давление\n$2p$", fs=11, color=C_P)
    label(ax, 1.8, -1.05, "$F = 2p \\cdot \\frac{S}{2} = mg$", fs=12, color=C_F)
    save(fig, "vessels-squeezed-vessel.png")


def utube_geometry(w=0.8, g=0.5):
    Ro = g / 2 + w
    Ri = g / 2
    return Ro, Ri


def utube_liquid(ax, yl, yr, fc, yc, w=0.8, g=0.5, clip=None):
    Ro, Ri = utube_geometry(w, g)
    th = np.linspace(np.pi, 2 * np.pi, 40)
    outer = [(Ro * np.cos(t), yc + Ro * np.sin(t)) for t in th]
    inner = [(Ri * np.cos(t), yc + Ri * np.sin(t)) for t in th[::-1]]
    pts = [(-Ro, yl), (-Ro, yc)] + outer + [(Ro, yc), (Ro, yr), (Ri, yr), (Ri, yc)] + inner + [(-Ri, yc), (-Ri, yl)]
    p = fill_poly(ax, pts, fc, z=1)
    if clip is not None:
        c = Rectangle((clip[0], clip[1]), clip[2] - clip[0], clip[3] - clip[1], transform=ax.transData)
        p.set_clip_path(c)


def utube_walls(ax, yc, top, w=0.8, g=0.5, lw=2.4):
    Ro, Ri = utube_geometry(w, g)
    th = np.linspace(np.pi, 2 * np.pi, 60)
    xo = [Ro * np.cos(t) for t in th]
    yo = [yc + Ro * np.sin(t) for t in th]
    line(ax, [-Ro] + xo + [Ro], [top] + yo + [top], lw=lw, z=4)
    xi = [Ri * np.cos(t) for t in th]
    yi = [yc + Ri * np.sin(t) for t in th]
    line(ax, [-Ri] + xi + [Ri], [top] + yi + [top], lw=lw, z=4)


def utube_mercury():
    fig, axes = blank(11.4, 6.2, (-2.5, 2.5), (-0.4, 5.3), n=2)
    Ro, Ri = utube_geometry()
    yc, top = 1.05, 4.2
    ym = 1.5
    for k, ax in enumerate(axes):
        utube_liquid(ax, ym, ym, MERCURY, yc)
        utube_walls(ax, yc, top)
        if k == 1:
            liquid(ax, -Ro, -Ri, ym, ym + 2.0, KERO)
            liquid(ax, Ri, Ro, ym, ym + 1.6, WATER)
            surface(ax, -Ro, -Ri, ym + 2.0, color=COPPER)
            surface(ax, Ri, Ro, ym + 1.6)
            dim(ax, -Ro - 0.3, ym, ym + 2.0, r"$h_\mathrm{к}=20$ см", side=-1, fs=11)
            dim(ax, Ro + 0.3, ym, ym + 1.6, r"$h_\mathrm{в}=?$", side=1, fs=11)
            hline(ax, -Ro - 0.2, Ro + 0.2, ym, color=C_F, lw=1.6)
            label(ax, 0, 4.95, r"$p_\mathrm{к}=p_\mathrm{в}$ на уровне ртути", fs=12, color=C_F)
            label(ax, -Ro + 0.4, 4.45, "керосин", fs=9.5)
            label(ax, Ro - 0.4, 4.45, "вода", fs=9.5)
            label(ax, 0, -0.25, "после: ртуть на тех же уровнях", fs=11.5)
        else:
            hline(ax, -Ro - 0.2, Ro + 0.2, ym, color=C_F, lw=1.4)
            label(ax, 0, 4.95, "до: ртуть на одном уровне", fs=11)
            label(ax, 0, -0.25, "U-образная трубка с ртутью", fs=11.5)
    save(fig, "vessels-utube-mercury.png")


def utube_kerosene_water():
    fig, (ax,) = blank(7.4, 5.6, (-3.4, 3.4), (-0.7, 4.5))
    W = 1.1
    Ro, Ri = utube_geometry(W)
    yc, top = Ro, 3.3
    hw = 2.0
    hk = 2.5
    utube_liquid(ax, hk, hw, KERO, yc, w=W, clip=(-Ro - 0.1, -0.5, 0.0, 4))
    utube_liquid(ax, hw, hw, WATER, yc, w=W, clip=(0.0, -0.5, Ro + 0.1, 4))
    utube_walls(ax, yc, top, w=W)
    surface(ax, -Ro, -Ri, hk, color=COPPER)
    surface(ax, Ri, Ro, hw)
    line(ax, [0, 0], [-0.02, 0.5], color=C_F, lw=1.8, z=8, ls="--")
    label(ax, 0.0, -0.32, "воображаемая перегородка", fs=10, color=C_F)
    dim(ax, -Ro - 0.3, 0.0, hk, r"$h_\mathrm{к}$", side=-1, fs=13)
    dim(ax, Ro + 0.3, 0.0, hw, r"$h_\mathrm{в}$", side=1, fs=13)
    label(ax, -(Ri + W / 2), 1.7, "керосин\n" + r"$\rho_\mathrm{к}$", fs=9.5)
    label(ax, Ri + W / 2, 1.5, "вода\n" + r"$\rho_\mathrm{в}$", fs=9.5)
    label(ax, 0, 4.0, r"$\dfrac{h_\mathrm{к}}{h_\mathrm{в}}=\dfrac{\rho_\mathrm{в}}{\rho_\mathrm{к}}=1{,}25$", fs=14)
    save(fig, "vessels-utube-kerosene-water.png")


# ------------------------------------------------------------- graphs


def h_of_h_lines():
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    x = np.linspace(0, 45, 50)
    pairs = (
        ("керосин, $\\rho=800$", 1000 / 800, COPPER),
        ("вода, $\\rho=1000$", 1.0, C_P),
        ("раствор соли, $\\rho=1240$", 1000 / 1240, VIOLET),
    )
    for name, k, c in pairs:
        ax.plot(x, k * x, color=c, lw=2.4, label=name)
    ax.plot([16], [20], "o", color=COPPER, ms=8, zorder=5)
    keep_dots(ax.annotate("17.23: 16 см воды\nдержат 20 см керосина", xy=(16, 20), xytext=(2, 32), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY, lw=1)))
    ax.plot([38.9], [31.3], "o", color=VIOLET, ms=8, zorder=5)
    ax.annotate("опыт: 38,9 см воды\nдержат 31,3 см раствора", xy=(38.9, 31.3), xytext=(21, 6), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.set_xlim(0, 45)
    ax.set_ylim(0, 56)
    ax.set_xlabel("высота столба воды $h_\\mathrm{в}$, см", fontsize=12)
    ax.set_ylabel("высота столба другой жидкости $h$, см", fontsize=12)
    ax.set_title("Высота столба, уравновешивающая воду")
    ax.grid(color=LIGHT, lw=1)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    save(fig, "vessels-h-of-h-lines.png")


def p_of_h_two_liquids():
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    h = np.linspace(0, 0.4, 50)
    for name, rho, c in (
        ("керосин", 800, COPPER),
        ("вода", 1000, C_P),
        ("раствор соли", 1240, VIOLET),
    ):
        ax.plot(h * 100, rho * G_ACC * h / 1000, color=c, lw=2.4, label=f"{name}, $\\rho={rho}$")
    p0 = 800 * G_ACC * 0.2 / 1000
    ax.axhline(p0, color=C_F, lw=1.4, ls="--")
    ax.text(41.3, p0, "$p_1=p_2$", color=C_F, va="center", ha="right", fontsize=11, backgroundcolor=PAPER)
    ax.plot([20, 16, 12.9], [p0] * 3, "o", color=INK, ms=7, zorder=5)
    for hx, t in ((20, "20"), (16, "16"), (12.9, "12,9")):
        ax.plot([hx, hx], [0, p0], color=GREY, lw=1, ls=":")
        ax.text(hx, -0.25, t, ha="center", va="top", fontsize=10, color=INK)
    ax.set_xlim(0, 42)
    ax.set_ylim(0, 5.6)
    ax.set_xlabel("глубина $h$, см", fontsize=12, labelpad=24)
    ax.set_ylabel("давление $p=\\rho g h$, кПа", fontsize=12)
    ax.set_title("Одно давление, разные глубины")
    ax.grid(color=LIGHT, lw=1)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    label(ax, 30, 0.7, "$g=10\\ \\text{Н/кг}$", fs=10, color=GREY)
    save(fig, "vessels-p-of-h-two-liquids.png")


# ------------------------------------------------------------- lesson 54


def lab_tube_in_cylinder():
    fig, (ax,) = blank(7.6, 6.4, (-2.6, 5.6), (-1.0, 6.2))
    x0, x1 = 0.0, 2.6
    hs = 4.0
    ht = 5.0
    # cylinder with brine
    liquid(ax, x0, x1, 0.0, hs, BRINE)
    line(ax, [x0, x0, x1, x1], [5.7, 0.0, 0.0, 5.7], lw=2.4, z=4)
    # tube: inner column of fresh water, open at both ends, bottom at the cylinder floor
    tx0, tx1 = 0.95, 1.65
    ax.add_patch(Rectangle((tx0, 0.12), tx1 - tx0, ht - 0.12, fc=WATER, ec="none", zorder=2))
    line(ax, [tx0, tx0], [0.12, 5.4], lw=1.8, z=5)
    line(ax, [tx1, tx1], [0.12, 5.4], lw=1.8, z=5)
    surface(ax, x0, x1, hs, color=SKY, lw=1.5)
    line(ax, [tx0, tx1], [ht, ht], color=WATER_EDGE, lw=1.6, z=6)
    hline(ax, -0.2, 3.4, 0.12, color=C_F, lw=1.6)
    hline(ax, tx1, 3.4, ht, color=GREY, lw=1.1)
    hline(ax, x1, 3.4, hs, color=GREY, lw=1.1)
    dim(ax, 3.2, 0.12, hs, r"$h_\mathrm{с}$", side=1, fs=14)
    dim(ax, 4.1, 0.12, ht, r"$h_\mathrm{в}$", side=1, fs=14)
    label(ax, 1.3, 2.0, "", fs=1)
    label(ax, -0.25, 2.0, "раствор\nсоли\n" + r"$\rho_\mathrm{с}$", fs=11, ha="right")
    label(ax, 1.3, 4.55, "вода\n" + r"$\rho_\mathrm{в}$", fs=10.5)
    label(ax, -0.25, 0.12, "нижний срез трубки", fs=10, color=C_F, ha="right")
    label(ax, 1.3, -0.65, r"$p_\mathrm{в}=p_\mathrm{с}\ \Rightarrow\ \rho_\mathrm{в}h_\mathrm{в}=\rho_\mathrm{с}h_\mathrm{с}$", fs=12.5)
    save(fig, "vessels-lab-tube-in-cylinder.png")


if __name__ == "__main__":
    two_liquids_equilibrium()
    shapes_one_liquid()
    syringes_brine()
    carpenter_and_liquid_level()
    lock_stages()
    problems_1710_1711()
    problems_1716_1717()
    problem_1718_ball()
    squeezed_vessel()
    utube_mercury()
    utube_kerosene_water()
    h_of_h_lines()
    p_of_h_two_liquids()
    lab_tube_in_cylinder()
