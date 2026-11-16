"""Figures for the note "Гидростатическое давление" (course Физика 7-9, lessons 47, 48, 51, 52).

Run: python3 pressure_hydrostatic.py
PNG files go to content/06. Давление/00. Вложения/, prefix hydro-.
Colour code as in pressure_solids.py: force red, area green, pressure blue; water light blue.
Vessel drawings marked "не в масштабе" exaggerate small level differences.
Curves and levels in the problem figures follow the answers of the problems.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle
from matplotlib.ticker import FuncFormatter

from pressure_solids import C_F, C_ORANGE, C_P, C_S, GREY, GRID, INK, METAL, OUT, arrow, blank, save
from theme import BLUE, GREEN, PAPER, PINK, SKY, VIOLET, WARM, num, tint

WATER = tint(SKY, 0.7)
WATER_EDGE = SKY
KERO = tint(WARM, 0.55)
KERO_EDGE = WARM
OIL = tint(WARM, 0.65)
MERC = tint(INK, 0.6)
SKIN = tint(PINK, 0.6)
G = 9.81
COMMA = FuncFormatter(lambda v, _: num(v, None))

PLATE = tint(INK, 0.75)  # a light grey plate or lid
PLATE_PALE = tint(INK, 0.85)
YELLOW_FILL = tint(WARM, 0.6)  # a pale yellow body: a plug, a cube
MOLECULE = VIOLET
GAS_FILL = tint(GREEN, 0.85)

C_WATER = BLUE
C_SEA = GREEN
C_OIL = WARM
C_MERC = tint(INK, 0.3)


def line(ax, xs, ys, color=INK, lw=1.8, z=4, **kw):
    ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle="round", **kw)


def rect(ax, x, y, w, h, fc="none", ec=INK, lw=1.8, z=3, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))


def poly(ax, pts, fc="none", ec=INK, lw=1.8, z=3, **kw):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, **kw))


def label(ax, x, y, text, fs=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, zorder=10, **kw)


def dim(ax, p, q, color=INK, lw=1.3):
    """Double-headed dimension arrow."""
    arrow(ax, p, q, color=color, lw=lw, style="<|-|>", scale=10, zorder=6)


def free_surface(ax, x0, x1, y, color=WATER_EDGE):
    line(ax, [x0, x1], [y, y], color=color, lw=2.0, z=5)


# ---------------------------------------------------------------- vessel with a derivation


def cylinder_derivation():
    fig, ax = blank(8.4, 4.6, (-0.2, 9.4), (-1.3, 6.3))
    rect(ax, 2.0, 1.0, 3.2, 4.8, lw=2.2)
    ax.add_patch(Rectangle((2.04, 1.04), 3.12, 3.7, fc=WATER, ec="none", zorder=1))
    free_surface(ax, 2.0, 5.2, 4.74)
    dim(ax, (1.3, 1.0), (1.3, 4.74), color=INK)
    label(ax, 0.95, 2.9, "$h$", fs=14)
    label(ax, 3.6, 3.2, r"$\rho$", fs=15)
    dim(ax, (2.0, -0.05), (5.2, -0.05), color=C_S)
    label(ax, 3.6, -0.6, "$S$", fs=14, color=C_S)
    for x in (2.6, 3.6, 4.6):
        arrow(ax, (x, 1.0), (x, 0.3), color=C_F, lw=2.4, scale=13)
    label(ax, 5.55, 0.55, r"$\vec{F}$", fs=14, color=C_F, ha="left")
    label(ax, 3.6, 5.4, "свободная поверхность", fs=8, color=WATER_EDGE)
    label(
        ax,
        5.85,
        4.6,
        "\n".join(
            [
                r"$p = \dfrac{F}{S}$",
                r"$F = P = mg$",
                r"$m = \rho V,\ V = Sh$",
            ]
        ),
        fs=12,
        ha="left",
        va="top",
    )
    label(ax, 5.85, 1.5, r"$p = \dfrac{\rho S h g}{S} = \rho g h$", fs=14, color=C_P, ha="left",
          bbox=dict(boxstyle="round,pad=0.4", fc=PAPER, ec=C_P, lw=1.6))
    save(fig, "hydro-cylinder-derivation.png")


# ---------------------------------------------------------------- p(h) lines


def p_of_h_liquids():
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))
    ax = axes[0]
    h = np.linspace(0, 40, 80)
    for rho, name, col in ((1030, "морская вода, 1030", C_SEA), (1000, "вода, 1000", C_WATER), (800, "масло, 800", C_OIL)):
        ax.plot(h, rho * G * h / 1e3, color=col, lw=2.4, label=f"{name} кг/м³")
    ax.plot([40], [1030 * G * 40 / 1e3], "o", color=C_SEA, ms=7, zorder=5)
    ax.annotate("404 кПа", (40, 1030 * G * 40 / 1e3), xytext=(21, 380), fontsize=11, color=C_SEA,
                arrowprops=dict(arrowstyle="-|>", color=C_SEA, lw=1.4))
    ax.set_xlim(0, 42)
    ax.set_ylim(0, 440)
    ax.set_xlabel("глубина $h$, м")
    ax.set_ylabel("давление $p$, кПа")
    ax.set_title("Глубины до 40 м")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(loc="upper left", fontsize=9.5, frameon=False)

    ax = axes[1]
    h = np.linspace(0, 1, 50)
    for rho, name, col in ((13600, "ртуть, 13 600", C_MERC), (1000, "вода, 1000", C_WATER), (800, "масло, 800", C_OIL)):
        ax.plot(h, rho * G * h / 1e3, color=col, lw=2.4, label=f"{name} кг/м³")
    ax.plot([1], [13600 * G / 1e3], "o", color=C_MERC, ms=7, zorder=5)
    ax.annotate("133 кПа", (1, 13600 * G / 1e3), xytext=(0.5, 118), fontsize=11, color=C_MERC,
                arrowprops=dict(arrowstyle="-|>", color=C_MERC, lw=1.4))
    ax.plot([1], [1000 * G / 1e3], "o", color=C_WATER, ms=7, zorder=5)
    ax.annotate("9,8 кПа", (1, 1000 * G / 1e3), xytext=(0.68, 36), fontsize=11, color=C_WATER,
                arrowprops=dict(arrowstyle="-|>", color=C_WATER, lw=1.4))
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 145)
    ax.set_xlabel("глубина $h$, м")
    ax.set_ylabel("давление $p$, кПа")
    ax.set_title("Ртуть и вода до 1 м")
    ax.xaxis.set_major_formatter(COMMA)
    ax.grid(color=GRID, lw=0.8)
    ax.legend(loc="upper left", fontsize=9.5, frameon=False)
    fig.tight_layout()
    save(fig, "hydro-p-of-h-liquids.png")


# ---------------------------------------------------------------- plates at one depth


def plate_orientations():
    fig, ax = blank(11.0, 5.2, (-0.6, 15.0), (-0.2, 7.9))
    xr = 11.0
    poly(ax, [(1, 7.3), (1, 2.0), (4.7, 2.0), (4.7, 0.3), (6.5, 0.3), (6.5, 2.0), (xr, 2.0), (xr, 7.3)], lw=2.2)
    poly(ax, [(1.04, 6.4), (1.04, 2.04), (4.74, 2.04), (4.74, 0.34), (6.46, 0.34), (6.46, 2.04), (xr - 0.04, 2.04), (xr - 0.04, 6.4)],
         fc=WATER, ec="none", z=1)
    free_surface(ax, 1.0, xr, 6.4)
    yd = 4.6
    line(ax, [1.0, xr], [yd, yd], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    dim(ax, (0.35, 6.4), (0.35, yd), color=INK)
    label(ax, 0.0, 5.5, "$h$", fs=14)

    def arrows_at(cx, cy, normals, length=0.7, gap=0.1):
        for nx, ny in normals:
            n = np.hypot(nx, ny)
            ux, uy = nx / n, ny / n
            arrow(ax, (cx + (gap + length) * ux, cy + (gap + length) * uy), (cx + gap * ux, cy + gap * uy),
                  color=C_P, lw=2.2, scale=11)

    plate = dict(fc=YELLOW_FILL, ec=INK, lw=1.4, z=6)
    y_lab = yd - 1.3
    # horizontal plate
    cx = 2.4
    poly(ax, [(cx - 0.5, yd - 0.05), (cx + 0.5, yd - 0.05), (cx + 0.5, yd + 0.05), (cx - 0.5, yd + 0.05)], **plate)
    arrows_at(cx, yd, [(0, 1), (0, -1)])
    label(ax, cx, y_lab, "горизонтально", fs=9.5)
    # vertical plate
    cx = 4.7
    poly(ax, [(cx - 0.05, yd - 0.5), (cx + 0.05, yd - 0.5), (cx + 0.05, yd + 0.5), (cx - 0.05, yd + 0.5)], **plate)
    arrows_at(cx, yd, [(1, 0), (-1, 0)])
    label(ax, cx, y_lab, "вертикально", fs=9.5)
    # tilted plate
    c, s = np.cos(np.radians(45)), np.sin(np.radians(45))
    cx = 6.9
    pts = [(cx - 0.5 * c - 0.05 * s, yd - 0.5 * s + 0.05 * c), (cx + 0.5 * c - 0.05 * s, yd + 0.5 * s + 0.05 * c),
           (cx + 0.5 * c + 0.05 * s, yd + 0.5 * s - 0.05 * c), (cx - 0.5 * c + 0.05 * s, yd - 0.5 * s - 0.05 * c)]
    poly(ax, pts, **plate)
    arrows_at(cx, yd, [(-s, c), (s, -c)], gap=0.12)
    label(ax, cx, y_lab, "наклонно", fs=9.5)
    # fish
    fx = 9.0
    ax.add_patch(Ellipse((fx, yd), 0.9, 0.42, fc=WARM, ec=INK, lw=1.2, zorder=6))
    poly(ax, [(fx + 0.4, yd), (fx + 0.78, yd + 0.22), (fx + 0.78, yd - 0.22)], fc=WARM, ec=INK, lw=1.2, z=6)
    ax.add_patch(Circle((fx - 0.25, yd + 0.06), 0.045, fc=INK, ec="none", zorder=7))
    arrow(ax, (fx, yd + 0.95), (fx, yd + 0.3), color=C_P, lw=2.2, scale=11)
    arrow(ax, (fx, yd - 0.95), (fx, yd - 0.3), color=C_P, lw=2.2, scale=11)
    label(ax, fx, y_lab, "рыбка", fs=9.5)
    # plate at the wall
    poly(ax, [(xr - 0.19, yd - 0.5), (xr - 0.04, yd - 0.5), (xr - 0.04, yd + 0.5), (xr - 0.19, yd + 0.5)], **plate)
    arrow(ax, (xr - 0.95, yd), (xr - 0.24, yd), color=C_P, lw=2.2, scale=11)
    label(ax, xr - 0.9, yd + 0.95, "у стенки", fs=9.5)
    label(ax, 5.6, 1.0, "дно глубже:\nна $p$ не влияет", fs=8, color=GREY)
    label(ax, 11.5, 6.3, r"на глубине $h$" "\n" r"$p = \rho g h$" "\nво всех точках", fs=11.5, color=C_P, ha="left", va="top")
    label(ax, 6.0, 7.0, "свободная поверхность", fs=9.5, color=WATER_EDGE)
    save(fig, "hydro-plate-orientations.png")


# ---------------------------------------------------------------- the tubes thought experiment


def tube_poly(p, q, w=0.28):
    """Rectangle around the segment p-q of half width w."""
    p, q = np.array(p, float), np.array(q, float)
    d = (q - p) / np.hypot(*(q - p))
    n = np.array([-d[1], d[0]])
    return [tuple(p + w * n), tuple(q + w * n), tuple(q - w * n), tuple(p - w * n)]


def perpetuum_tubes():
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.6))
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axes[0]
    ax.set_xlim(-1.2, 7.0)
    ax.set_ylim(-1.1, 5.0)
    bot = np.array([5.0, 0.0])
    top_v = np.array([5.0, 4.0])
    ang = np.radians(40)
    top_i = bot + 4.0 * np.array([-np.cos(ang), np.sin(ang)])
    poly(ax, tube_poly(bot, top_v), fc=WATER, lw=1.8)
    poly(ax, tube_poly(bot, top_i), fc=WATER, lw=1.8)
    line(ax, [top_i[0] - 0.4, 6.0], [top_v[1], top_v[1]], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    line(ax, [top_i[0] - 0.4, 6.0], [top_i[1], top_i[1]], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    line(ax, [top_i[0] - 0.4, 6.0], [0, 0], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    dim(ax, (5.9, 0.0), (5.9, 4.0), color=INK)
    label(ax, 6.45, 2.0, "$h_2$", fs=14)
    dim(ax, (top_i[0] - 0.2, 0.0), (top_i[0] - 0.2, top_i[1]), color=INK)
    label(ax, top_i[0] - 0.65, top_i[1] / 2, "$h_1$", fs=14)
    label(ax, 2.35, 0.85, "1 м", fs=12, rotation=40)
    label(ax, 4.45, 2.0, "1 м", fs=12, rotation=90)
    ax.plot([bot[0] - 0.12], [0.0], "o", color=C_P, ms=6, zorder=7)
    ax.plot([bot[0] + 0.12], [0.0], "o", color=C_P, ms=6, zorder=7)
    label(ax, 4.3, -0.55, "$p_1$", fs=14, color=C_P)
    label(ax, 5.6, -0.55, "$p_2$", fs=14, color=C_P)
    label(ax, 2.9, -1.05, r"$h_1 < h_2 \Rightarrow p_1 < p_2$", fs=12.5, color=C_P)
    ax.set_title("Трубки одной длины, 1 м", fontsize=11)

    ax = axes[1]
    ax.set_xlim(-0.3, 8.3)
    ax.set_ylim(-1.1, 5.0)
    poly(ax, [(0, 4.6), (0, 0), (8, 0), (8, 4.6)], lw=2.2)
    ax.add_patch(Rectangle((0.04, 0.04), 7.92, 3.9, fc=WATER, ec="none", zorder=1))
    free_surface(ax, 0, 8, 3.94)
    yb = 1.3
    line(ax, [0.4, 7.6], [yb, yb], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    # net tubes (dashed outlines)
    for pts in (tube_poly((5.5, yb), (5.5, 3.94), 0.25), tube_poly((4.2, yb), (1.3, 3.94), 0.25)):
        poly(ax, pts, ec=INK, lw=1.4, fc="none", z=5, ls=(0, (3, 2)))
    dim(ax, (7.0, 3.94), (7.0, yb), color=INK)
    label(ax, 7.5, 2.6, "$h$", fs=14)
    ax.plot([5.5], [yb], "o", color=C_P, ms=6, zorder=7)
    ax.plot([4.2], [yb], "o", color=C_P, ms=6, zorder=7)
    label(ax, 5.5, yb - 0.5, "$p$", fs=14, color=C_P)
    label(ax, 4.2, yb - 0.5, "$p$", fs=14, color=C_P)
    label(ax, 4.0, -0.75, "Нижние концы на одной глубине: давления равны", fs=11, color=C_P)
    ax.set_title("Сетчатые трубки в сосуде", fontsize=11)
    save(fig, "hydro-perpetuum-tubes.png")


# ---------------------------------------------------------------- vessels of different shape


def vessels_same_pressure():
    fig, ax = blank(12.0, 4.6, (-0.6, 18.4), (-1.5, 5.2))
    level = 4.0
    shapes = [
        ([(0, 0), (2, 0), (2, 4.6), (0, 4.6)], [(0, 0), (2, 0), (2, level), (0, level)], "цилиндр"),
        ([(0, 0), (2, 0), (3.6, 4.6), (-1.6, 4.6)], None, "расширяется"),
        ([(0, 0), (2, 0), (1.5, 4.6), (0.5, 4.6)], None, "сужается"),
        ([(0, 0), (2, 0), (2, 4.6), (1.5, 4.6), (1.5, 1.2), (0, 1.2)], [(0, 0), (2, 0), (2, level), (1.5, level), (1.5, 1.2), (0, 1.2)], "с узкой трубкой"),
    ]
    dxs = [0.4, 4.6, 9.3, 12.9]
    for (outer, water, name), dx in zip(shapes, dxs):
        outer_s = [(x + dx, y) for x, y in outer]
        if water is None:
            # water = the vessel clipped at the level; the walls are straight lines
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = outer
            t = level / 4.6
            xl = x0 + (x3 - x0) * t
            xr = x1 + (x2 - x1) * t
            water = [(x0, y0), (x1, y1), (xr, level), (xl, level)]
        water_s = [(x + dx, y) for x, y in water]
        poly(ax, water_s, fc=WATER, ec="none", z=1)
        poly(ax, outer_s, lw=2.2, z=3)
        xs = [x for x, _ in water_s if _ == level]
        line(ax, [min(xs), max(xs)], [level, level], color=WATER_EDGE, lw=2.0, z=5)
        for x in (0.4, 1.0, 1.6):
            arrow(ax, (x + dx, 0.0), (x + dx, -0.7), color=C_P, lw=2.2, scale=11)
        label(ax, 1.0 + dx, -1.15, name, fs=10.5)
    line(ax, [-0.4, 15.4], [level, level], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    dim(ax, (-0.3, 0.0), (-0.3, level), color=INK)
    label(ax, -0.62, 2.0, "$h$", fs=14)
    label(ax, 15.5, 1.0, r"$p = \rho g h$" "\nодно и то же", fs=12, color=C_P, ha="left")
    save(fig, "hydro-vessels-same-pressure.png")


# ---------------------------------------------------------------- Bazhinova exercise


def bazhinov_vessel():
    fig, ax = blank(8.6, 5.0, (-1.4, 8.6), (-1.1, 5.4))
    outer = [(0, 0), (7.6, 0), (7.6, 4.4), (4.8, 4.4), (4.8, 1.0), (2.4, 1.0), (2.4, 2.0), (0, 2.0)]
    water = [(0.04, 0.04), (7.56, 0.04), (7.56, 4.0), (4.84, 4.0), (4.84, 0.96), (2.44, 0.96), (2.44, 1.96), (0.04, 1.96)]
    poly(ax, water, fc=WATER, ec="none", z=1)
    poly(ax, outer, lw=2.4, z=3)
    free_surface(ax, 4.8, 7.6, 4.0)
    line(ax, [-0.4, 4.8], [4.0, 4.0], color=WATER_EDGE, lw=1.4, ls=(0, (4, 3)), z=2)
    for x, name in ((1.2, "A"), (3.6, "B"), (6.2, "C")):
        arrow(ax, (x, 0.05), (x, 3.95), color=INK, lw=1.2, style="<|-|>", scale=9, zorder=6)
        ax.plot([x], [0], "o", color=C_P, ms=7, zorder=7)
        label(ax, x, -0.45, name, fs=14)
    label(ax, 0.95, 4.0, "$h$", fs=14, va="bottom", ha="right")
    dim(ax, (-0.35, 0.0), (-0.35, 2.0), color=GREY)
    label(ax, -0.85, 1.0, "$h/2$", fs=12, color=GREY)
    dim(ax, (4.3, 0.0), (4.3, 1.0), color=GREY)
    label(ax, 4.55, 0.5, "$h/4$", fs=12, color=GREY)
    label(ax, 2.4, 2.6, "потолок давит\nна жидкость", fs=9.5, color=GREY)
    label(ax, 3.8, -0.95, r"$p_A = p_B = p_C$", fs=13, color=C_P)
    save(fig, "hydro-bazhinov-vessel.png")


# ---------------------------------------------------------------- Pascal's law and the hydrostatic pressure


def pascal_addition():
    fig = plt.figure(figsize=(10.0, 4.4))
    ax = fig.add_axes([0.0, 0.02, 0.45, 0.96])
    ax.set_xlim(-0.5, 6.3)
    ax.set_ylim(-0.5, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    rect(ax, 0.8, 0.3, 3.6, 4.6, lw=2.2)
    ax.add_patch(Rectangle((0.84, 0.34), 3.52, 3.9, fc=WATER, ec="none", zorder=1))
    rect(ax, 0.84, 4.0, 3.52, 0.3, fc=PLATE, ec=INK, lw=1.6, z=4)
    rect(ax, 1.9, 4.3, 1.4, 0.9, fc=METAL, ec=INK, lw=1.6, z=4)
    label(ax, 2.6, 4.75, "груз", fs=10.5)
    for x in (1.4, 2.6, 3.8):
        arrow(ax, (x, 4.0), (x, 3.3), color=C_P, lw=2.4, scale=12)
    label(ax, 4.7, 3.65, "$p_0$", fs=14, color=C_P, ha="left")
    label(ax, 4.7, 2.2, r"$+\rho g h$", fs=13, color=C_P, ha="left")
    dim(ax, (0.4, 4.0), (0.4, 0.34), color=INK)
    label(ax, 0.08, 2.2, "$h$", fs=14)
    ax2 = fig.add_axes([0.56, 0.16, 0.41, 0.72])
    h = np.linspace(0, 5, 20)
    p0 = 2.5
    ax2.plot(h, 1.4 * h, color=C_WATER, lw=2.6, label="без груза: $p = \\rho g h$")
    ax2.plot(h, p0 + 1.4 * h, color=C_F, lw=2.6, label="с грузом: $p = p_0 + \\rho g h$")
    ax2.annotate("", xy=(2.4, p0 + 1.4 * 2.4), xytext=(2.4, 1.4 * 2.4),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.3))
    ax2.text(2.55, 1.4 * 2.4 + p0 / 2, "$p_0$ в любой точке", fontsize=11, va="center")
    ax2.set_xlim(0, 5.2)
    ax2.set_ylim(0, 11.5)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlabel("глубина $h$", fontsize=12)
    ax2.set_ylabel("давление $p$", fontsize=12)
    ax2.spines["left"].set_visible(True)
    ax2.legend(loc="upper left", fontsize=10.5, frameon=False)
    save(fig, "hydro-pascal-addition.png")


# ---------------------------------------------------------------- finger and balance


def beaker(ax, cx, ybase, level, w0=1.5, w1=1.9, hgt=2.3, finger=False):
    def half(y):
        return (w0 + (w1 - w0) * (y - ybase) / hgt) / 2

    yl = ybase + level
    poly(ax, [(cx - half(ybase), ybase), (cx + half(ybase), ybase), (cx + half(yl), yl), (cx - half(yl), yl)],
         fc=WATER, ec="none", z=2)
    poly(ax, [(cx - half(ybase), ybase), (cx + half(ybase), ybase), (cx + half(ybase + hgt), ybase + hgt),
              (cx - half(ybase + hgt), ybase + hgt)], lw=2.0, z=4)
    line(ax, [cx - half(yl), cx + half(yl)], [yl, yl], color=WATER_EDGE, lw=2.0, z=5)
    if finger:
        rect(ax, cx - 0.22, ybase + 0.7, 0.44, hgt + 0.9 - 0.7, fc=SKIN, ec=INK, lw=1.4, z=6)
    return yl


def balance(ax, tilt, level_l, level_r, finger):
    piv = (6.0, 2.65)
    poly(ax, [(piv[0] - 0.4, 0.6), (piv[0] + 0.4, 0.6), (piv[0], piv[1])], fc=PLATE_PALE, lw=1.8, z=3)
    L = (1.6, 2.7 - tilt)
    R = (10.4, 2.7 + tilt)
    line(ax, [L[0], R[0]], [L[1], R[1]], color=INK, lw=3.2, z=4)
    for e in (L, R):
        line(ax, [e[0] - 1.25, e[0] + 1.25], [e[1], e[1]], color=INK, lw=2.6, z=4)
    yl = beaker(ax, L[0], L[1] + 0.05, level_l, finger=finger)
    yr = beaker(ax, R[0], R[1] + 0.05, level_r)
    return L, R, yl, yr


def finger_balance():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    for ax in axes:
        ax.set_xlim(0, 12)
        ax.set_ylim(0.3, 6.4)
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axes[0]
    L, R, yl, yr = balance(ax, 0.0, 1.5, 1.5, False)
    dim(ax, (0.35, L[1] + 0.05), (0.35, yl), color=INK)
    label(ax, 0.05, (L[1] + yl) / 2, "$h$", fs=13)
    dim(ax, (11.65, R[1] + 0.05), (11.65, yr), color=INK)
    label(ax, 12.0, (R[1] + yr) / 2, "$h$", fs=13)
    ax.set_title("Весы уравновешены", fontsize=11)
    ax = axes[1]
    L, R, yl, yr = balance(ax, 0.45, 1.5 + 0.35, 1.5, True)
    dim(ax, (0.35, L[1] + 0.05), (0.35, yl), color=INK)
    label(ax, 0.0, (L[1] + yl) / 2, "$h'$", fs=13)
    dim(ax, (11.65, R[1] + 0.05), (11.65, yr), color=INK)
    label(ax, 12.0, (R[1] + yr) / 2, "$h$", fs=13)
    label(ax, 6.0, 5.6, r"$h' > h \Rightarrow p' > p \Rightarrow F' > F$", fs=12.5, color=C_P)
    ax.set_title("Палец в воде, не касаясь стакана", fontsize=11)
    save(fig, "hydro-finger-balance.png")


# ---------------------------------------------------------------- pressure on a wall


def wall_triangle():
    fig = plt.figure(figsize=(10.0, 4.4))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(0.0, 8.4)
    ax.set_ylim(-0.3, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ys, yb, xw = 5.4, 0.8, 6.0
    ax.add_patch(Rectangle((1.0, yb), xw - 1.0, ys - yb, fc=WATER, ec="none", zorder=1))
    line(ax, [1.0, 1.0, xw, xw], [ys + 0.8, yb, yb, ys + 0.8], lw=2.4)
    free_surface(ax, 1.0, xw, ys)
    pmax = 2.6
    for y in np.linspace(ys - 0.02, yb, 9):
        L = pmax * (ys - y) / (ys - yb)
        if L > 0.15:
            arrow(ax, (xw - L, y), (xw, y), color=C_P, lw=2.0, scale=10)
    line(ax, [xw, xw - pmax], [ys, yb], color=C_P, lw=1.6, z=6, ls=(0, (4, 2)))
    dim(ax, (0.55, ys), (0.55, yb), color=INK)
    label(ax, 0.2, 3.1, "$h$", fs=14)
    label(ax, xw + 0.15, ys + 0.05, r"$p = 0$", fs=11.5, ha="left", color=C_P)
    label(ax, xw + 0.15, yb - 0.05, r"$p_{\max} = \rho g h$", fs=11.5, ha="left", color=C_P, va="center")
    label(ax, 3.4, 5.9, "вид сбоку, правая стенка", fs=10, color=GREY)

    ax2 = fig.add_axes([0.6, 0.15, 0.37, 0.72])
    ax2.set_xlim(0, 1.25)
    ax2.set_ylim(1.15, -0.05)
    d = np.linspace(0, 1, 30)
    ax2.fill_betweenx(d, 0, d, color=WATER, alpha=0.85, zorder=1)
    ax2.plot(d, d, color=C_P, lw=2.4, zorder=3)
    ax2.add_patch(Rectangle((0, 0), 0.5, 1.0, fc="none", ec=C_F, lw=1.8, ls=(0, (4, 2)), zorder=4))
    ax2.plot([0.5, 0.5], [0, 1], color=C_F, lw=1.8, ls=(0, (4, 2)), zorder=4)
    ax2.set_xticks([0, 0.5, 1.0])
    ax2.set_xticklabels(["0", r"$\rho g h/2$", r"$\rho g h$"])
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["0", "$h$"])
    ax2.set_xlabel("давление $p$", fontsize=12)
    ax2.set_ylabel("глубина", fontsize=12)
    ax2.text(0.66, 0.3, "площади\nравны", fontsize=10.5, color=INK)
    ax2.text(0.14, 0.42, r"$p_{ср}$", fontsize=13, color=C_F)
    ax2.spines["top"].set_visible(True)
    save(fig, "hydro-wall-triangle.png")


def aquarium_cube():
    fig, ax = blank(8.8, 5.0, (-2.4, 9.0), (-1.9, 5.4))
    a = 4.0
    dx, dy = 1.7, 1.15
    # water
    poly(ax, [(0, 0), (a, 0), (a, a / 2), (0, a / 2)], fc=WATER, ec="none", z=1)
    poly(ax, [(0, a / 2), (a, a / 2), (a + dx, a / 2 + dy), (dx, a / 2 + dy)], fc=tint(SKY, 0.55), ec="none", z=1)
    poly(ax, [(a, 0), (a, a / 2), (a + dx, a / 2 + dy), (a + dx, dy)], fc=WATER, ec="none", z=1, hatch="///")
    # cube edges
    rect(ax, 0, 0, a, a, lw=2.2, z=4)
    poly(ax, [(0, a), (a, a), (a + dx, a + dy), (dx, a + dy)], lw=2.0, z=4)
    poly(ax, [(a, 0), (a, a), (a + dx, a + dy), (a + dx, dy)], lw=2.0, z=4)
    line(ax, [dx, dx], [dy, a + dy], lw=1.2, ls=(0, (3, 3)), color=GREY)
    line(ax, [0, dx], [0, dy], lw=1.2, ls=(0, (3, 3)), color=GREY)
    line(ax, [dx, a + dx], [dy, dy], lw=1.2, ls=(0, (3, 3)), color=GREY)
    # forces
    arrow(ax, (a / 2 + dx / 2, dy / 2 + 0.05), (a / 2 + dx / 2, -1.4), color=C_F, lw=2.8, scale=15)
    label(ax, a / 2 + dx / 2 + 0.15, -1.6, r"$\vec F_{д}$", fs=14, color=C_F, ha="left")
    # F_б = F_д / 4: a quarter of the bottom arrow
    fb = (dy / 2 + 0.05 + 1.4) / 4
    arrow(ax, (a + dx / 2, a / 4 + dy / 2), (a + dx / 2 + fb, a / 4 + dy / 2), color=C_F, lw=2.8, scale=12)
    label(ax, a + dx / 2 + fb + 0.1, a / 4 + dy / 2 + 0.35, r"$\vec F_{б}$", fs=14, color=C_F, ha="left")
    dim(ax, (-0.55, 0), (-0.55, a), color=INK)
    label(ax, -0.95, a / 2, "$a$", fs=14)
    dim(ax, (-1.6, 0), (-1.6, a / 2), color=INK)
    label(ax, -2.0, a / 4, "$h$", fs=14)
    label(ax, 7.0, 4.0, r"$h = a/2$", fs=12.5, ha="left")
    label(ax, a + dx + 0.1, a / 2 + dy + 0.35, r"$p_{\min}=0$", fs=10.5, color=C_P, ha="left")
    label(ax, a + dx + 0.35, dy - 0.1, r"$p_{\max}$", fs=10.5, color=C_P, ha="left", va="top")
    save(fig, "hydro-aquarium-cube.png")


# ---------------------------------------------------------------- problems


def floors_pressure():
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    n = np.linspace(1, 9, 50)
    p = 200 - 30 * (n - 1)
    ax.plot(n, p, color=C_P, lw=2.4, zorder=3)
    nn = np.arange(1, 9)
    ax.plot(nn, 200 - 30 * (nn - 1), "o", color=C_P, ms=6, zorder=4)
    ax.plot([5], [80], "o", color=C_F, ms=10, zorder=5)
    ax.annotate("5-й этаж: 80 кПа", (5, 80), xytext=(5.4, 150), fontsize=11, color=C_F,
                arrowprops=dict(arrowstyle="-|>", color=C_F, lw=1.4))
    n0 = 1 + 200 / 30
    ax.axhline(0, color=INK, lw=1.2)
    ax.fill_between(n[n >= n0], p[n >= n0], 0, color=C_F, alpha=0.18, zorder=2)
    ax.text(7.2, -55, "вода не поднимется", fontsize=10.5, color=C_F, ha="center")
    ax.plot([n0], [0], "o", mfc=PAPER, mec=INK, ms=7, zorder=5)
    ax.text(n0 + 0.05, 14, f"$n \\approx {num(n0, 1, math=True)}$", fontsize=10.5)
    ax.set_xlim(0.7, 9.3)
    ax.set_ylim(-70, 225)
    ax.set_xlabel("номер этажа $n$")
    ax.set_ylabel("давление $p_n$, кПа")
    ax.grid(color=GRID, lw=0.8)
    save(fig, "hydro-floors-pressure.png")


def football_chamber():
    fig, ax = blank(8.0, 5.4, (-0.2, 9.0), (-0.4, 7.4))
    line(ax, [1.0, 8.0], [0.0, 0.0], lw=2.2)
    for x in np.arange(1.1, 8.0, 0.35):
        line(ax, [x, x - 0.16], [0, -0.16], color=GREY, lw=1)
    ax.add_patch(Ellipse((5.4, 0.85), 3.6, 1.5, fc=WATER, ec=INK, lw=2.0, zorder=3))
    poly(ax, [(1.0, 0.55), (1.0, 6.9), (1.42, 6.9), (1.42, 0.85), (3.6, 0.9), (3.6, 0.55)], fc=WATER, lw=1.8, z=3)
    ax.add_patch(Rectangle((1.02, 6.3), 0.38, 0.6, fc=PAPER, ec="none", zorder=4))
    line(ax, [1.02, 1.4], [6.3, 6.3], color=WATER_EDGE, lw=2.0, z=5)
    rect(ax, 3.7, 1.62, 3.4, 0.2, fc=PLATE, ec=INK, lw=1.6, z=5)
    ax.add_patch(Ellipse((5.4, 2.75), 0.9, 0.9, fc=METAL, ec=INK, lw=1.6, zorder=5))
    label(ax, 5.4, 2.75, "$m$", fs=13)
    arrow(ax, (6.3, 2.8), (6.3, 1.85), color=C_F, lw=2.6, scale=14, zorder=6)
    label(ax, 6.55, 2.35, r"$\vec P$", fs=13, color=C_F, ha="left")
    dim(ax, (3.7, 1.35), (7.1, 1.35), color=C_S)
    label(ax, 7.6, 1.35, "$S$", fs=13.5, color=C_S)
    dim(ax, (0.45, 0.85), (0.45, 6.3), color=INK)
    label(ax, 0.0, 3.6, "$h$", fs=14)
    line(ax, [3.55, 3.55], [0.42, 1.02], color=INK, lw=1.6, ls=(0, (3, 2)), z=7)
    label(ax, 2.55, 2.2, "мысленная\nперегородка", fs=9.5, color=GREY)
    ax.annotate("", xy=(3.55, 1.0), xytext=(2.9, 1.9), arrowprops=dict(arrowstyle="-", color=GREY, lw=1.0))
    label(ax, 2.6, 4.2, r"$p = \rho g h$", fs=13, color=C_P)
    label(ax, 6.8, 3.6, r"$p = \dfrac{mg}{S}$", fs=13, color=C_P)
    save(fig, "hydro-football-chamber.png")


def valve_flap():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axes[0]
    ax.set_xlim(-0.5, 9.0)
    ax.set_ylim(-0.4, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    line(ax, [0, 8], [0.4, 0.4], lw=2.4)
    line(ax, [0, 8], [3.4, 3.4], lw=2.4)
    rng = np.random.default_rng(4)
    for _ in range(26):
        ax.add_patch(Circle((rng.uniform(0.3, 3.5), rng.uniform(0.7, 3.1)), 0.09, fc=MOLECULE, ec="none", zorder=2))
    rect(ax, 4.2, 0.4, 0.25, 3.0, fc=PLATE, ec=INK, lw=1.8, z=4)
    rect(ax, 4.25, 3.4, 0.15, 0.6, fc=INK, ec=INK, z=4)
    line(ax, [3.95, 4.7], [4.0, 4.0], lw=3, color=INK)
    for y in (1.0, 1.9, 2.8):
        arrow(ax, (3.6, y), (4.15, y), color=C_F, lw=2.4, scale=12)
    label(ax, 1.9, 4.0, "газ под давлением $p$", fs=10.5)
    dim(ax, (5.2, 0.4), (5.2, 3.4), color=INK)
    label(ax, 5.55, 1.9, "$d$", fs=14)
    ax = axes[1]
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-2.0, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 1.5, fc=GAS_FILL, ec=C_S, lw=2.2))
    dim(ax, (-1.5, 0), (1.5, 0), color=INK)
    label(ax, 0, 0.35, "$d$", fs=14)
    label(ax, 0, -0.75, r"$S = \dfrac{\pi d^2}{4}$", fs=13, color=C_S)
    ax.set_title("Заслонка спереди", fontsize=11)
    save(fig, "hydro-valve-flap.png")


def diver_force():
    fig, ax = blank(9.0, 4.4, (-0.3, 10.2), (-1.4, 5.0))
    ax.add_patch(Rectangle((0.2, -0.6), 3.4, 5.2, fc=WATER, ec="none", zorder=1))
    free_surface(ax, 0.2, 3.6, 4.6)
    line(ax, [0.2, 0.2, 3.6, 3.6], [4.9, -0.6, -0.6, 4.9], lw=1.6, color=GREY)
    dim(ax, (-0.1, 4.6), (-0.1, 0.0), color=INK)
    label(ax, -0.28, 2.3, "$h$", fs=13, ha="right")
    ax.add_patch(Rectangle((1.7, 0.0), 0.8, 0.8, fc=YELLOW_FILL, ec=INK, lw=1.6, zorder=5))
    label(ax, 2.1, 0.4, "1 дм²", fs=9.5)
    arrow(ax, (1.0, 0.4), (1.65, 0.4), color=C_F, lw=2.6, scale=13, zorder=6)
    label(ax, 1.2, 1.0, "$F$", fs=13, color=C_F)
    label(ax, 2.0, 3.6, r"$h = 100$ м", fs=11, color=INK)
    label(ax, 4.3, 4.0, r"$F = \rho g h S = 10$ кН", fs=13, color=C_F, ha="left")
    label(ax, 4.3, 3.3, "равна весу груза массой 1 т", fs=11.5, ha="left")
    rect(ax, 5.2, 1.5, 1.8, 1.3, fc=METAL, ec=INK, lw=1.8, z=4)
    label(ax, 6.1, 2.15, "1 т", fs=14)
    arrow(ax, (6.1, 1.5), (6.1, -0.3), color=C_F, lw=2.8, scale=15)
    label(ax, 6.4, 0.6, r"$P = 10$ кН", fs=11.5, color=C_F, ha="left")
    save(fig, "hydro-diver-force.png")


def oil_water_layers():
    fig = plt.figure(figsize=(9.6, 4.4))
    ax = fig.add_axes([0.0, 0.0, 0.42, 1.0])
    ax.set_xlim(-1.4, 5.4)
    ax.set_ylim(-0.6, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    hm, hw = 3.75, 2.25  # 12,5 cm and 7,5 cm in the scale 0,3 per cm
    x0, x1 = 0.8, 3.4
    ax.add_patch(Rectangle((x0, 0.0), x1 - x0, hw, fc=WATER, ec="none", zorder=1))
    ax.add_patch(Rectangle((x0, hw), x1 - x0, hm, fc=OIL, ec="none", zorder=1))
    line(ax, [x0, x0, x1, x1], [hw + hm + 0.4, 0, 0, hw + hm + 0.4], lw=2.4)
    line(ax, [x0, x1], [hw + hm, hw + hm], color=KERO_EDGE, lw=1.8)
    line(ax, [x0, x1], [hw, hw], color=INK, lw=1.0, ls=(0, (4, 3)), z=5)
    label(ax, 2.1, hw + hm / 2, "масло", fs=12)
    label(ax, 2.1, hw / 2, "вода", fs=12)
    dim(ax, (3.8, hw), (3.8, hw + hm), color=INK)
    label(ax, 4.5, hw + hm / 2, "$h_м$", fs=13)
    dim(ax, (3.8, 0), (3.8, hw), color=INK)
    label(ax, 4.5, hw / 2, "$h_в$", fs=13)
    dim(ax, (0.3, 0), (0.3, hw + hm), color=INK)
    label(ax, -0.15, (hw + hm) / 2, "$h$", fs=13)
    ax.plot([2.1], [0], "o", color=C_P, ms=7, zorder=7)
    label(ax, 2.1, -0.4, "$p$ на дне", fs=11, color=C_P)

    ax2 = fig.add_axes([0.55, 0.16, 0.42, 0.72])
    d = np.array([0, 12.5, 20.0])
    p = np.array([0, 1000, 1750])
    ax2.plot(d, p, color=C_P, lw=2.6, zorder=3)
    ax2.plot(d, p, "o", color=C_P, ms=6, zorder=4)
    ax2.axvline(12.5, color=GREY, lw=1.0, ls=(0, (4, 3)))
    ax2.text(4.6, 800, "слой масла:\nнаклон $\\rho_м g$", ha="center", fontsize=10)
    ax2.text(16.3, 600, "слой воды:\nнаклон $\\rho_в g$", ha="center", fontsize=10)
    ax2.annotate("1000 Па", (12.5, 1000), xytext=(3.5, 1300), fontsize=10.5, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax2.annotate("1750 Па", (20, 1750), xytext=(13.5, 1700), fontsize=10.5, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax2.set_xlim(0, 21.5)
    ax2.set_ylim(0, 2000)
    ax2.set_xlabel("глубина, см")
    ax2.set_ylabel("давление $p$, Па")
    ax2.grid(color=GRID, lw=0.8)
    save(fig, "hydro-oil-water-layers.png")


# ---------------------------------------------------------------- U-shaped tubes


def utube(ax, x0, left, right, bottom, w=1.0, g=1.4, t=0.9, H=6.0):
    """U-tube: arms of width w, gap g, bottom bar of height t. Fluids: lists of (y0, y1, colour)."""
    xr = x0 + w + g
    ax.add_patch(Rectangle((x0, 0), 2 * w + g, t, fc=bottom, ec="none", zorder=1))
    for (a, b, c) in left:
        ax.add_patch(Rectangle((x0, a), w, b - a, fc=c, ec="none", zorder=1))
    for (a, b, c) in right:
        ax.add_patch(Rectangle((xr, a), w, b - a, fc=c, ec="none", zorder=1))
    # open ends: polylines, not closed polygons
    line(ax, [x0, x0, xr + w, xr + w], [H, 0, 0, H], lw=2.2, z=3)
    line(ax, [x0 + w, x0 + w, xr, xr], [H, t, t, H], lw=2.2, z=3)


def utube_three_high_problem():
    """Kirik 3 high: kerosene poured into the left knee of a water U-tube."""
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.6))
    scale = 0.125  # 1 cm = 0.125 units: h_k = 20 cm = 2.5, delta h = 8 cm = 1.0
    hk = 20 * scale
    dh = 8 * scale
    lvl = 3.0
    H = 5.8
    for ax in axes:
        ax.set_xlim(-1.5, 6.0)
        ax.set_ylim(-0.7, 6.2)
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axes[0]
    utube(ax, 0.0, [(0.9, lvl, WATER)], [(0.9, lvl, WATER)], WATER, H=H)
    line(ax, [-0.3, 3.3], [lvl, lvl], color=WATER_EDGE, lw=1.6, z=5)
    ax.set_title("До: вода на одном уровне", fontsize=11)
    ax = axes[1]
    ll, rl = lvl - dh, lvl + dh
    utube(ax, 0.0, [(0.9, ll, WATER), (ll, ll + hk, KERO)], [(0.9, rl, WATER)], WATER, H=H)
    line(ax, [-0.6, 3.3], [lvl, lvl], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    line(ax, [-0.6, 3.3], [ll, ll], color=INK, lw=1.2, ls=(0, (4, 3)), z=6)
    dim(ax, (-0.35, ll), (-0.35, ll + hk), color=INK)
    label(ax, -0.95, ll + hk / 2, "$h_к$", fs=13)
    dim(ax, (3.55, lvl), (3.55, rl), color=INK)
    label(ax, 4.05, (lvl + rl) / 2, r"$\Delta h$", fs=13)
    label(ax, 0.5, ll - 0.35, "$p_1$", fs=13, color=C_P)
    label(ax, 2.4, ll - 0.35, "$p_2$", fs=13, color=C_P)
    ax.plot([0.5], [ll], "o", color=C_P, ms=6, zorder=7)
    ax.plot([2.4], [ll], "o", color=C_P, ms=6, zorder=7)
    dim(ax, (4.5, ll), (4.5, rl), color=C_P)
    label(ax, 5.1, (ll + rl) / 2, r"$2\Delta h$", fs=13, color=C_P)
    ax.set_title("После: керосин в левом колене", fontsize=11)
    save(fig, "hydro-utube-kerosene-water.png")


def utube_mercury_problem():
    """Kirik 1 high: mercury at the bottom, water on the left, kerosene on the right."""
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    ax.set_xlim(-1.6, 5.0)
    ax.set_ylim(-0.8, 8.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ym = 1.6
    hw, hk = 4.0, 5.0
    H = 7.6
    utube(ax, 0.0, [(0.9, ym, MERC), (ym, ym + hw, WATER)], [(0.9, ym, MERC), (ym, ym + hk, KERO)], MERC, H=H)
    line(ax, [-0.4, 3.4], [ym, ym], color=INK, lw=1.2, ls=(0, (4, 3)), z=6)
    dim(ax, (3.55, ym), (3.55, ym + hk), color=INK)
    label(ax, 4.1, ym + hk / 2, "$h_к$", fs=13)
    label(ax, 0.5, ym + hw / 2, "$m_в$", fs=13)
    label(ax, 2.9, ym + hk / 2, "керосин", fs=10.5, rotation=90)
    ax.plot([0.5], [ym], "o", color=C_P, ms=6, zorder=7)
    ax.plot([2.4], [ym], "o", color=C_P, ms=6, zorder=7)
    label(ax, 0.5, ym - 0.5, "$p_1$", fs=13, color=C_P)
    label(ax, 2.4, ym - 0.5, "$p_2$", fs=13, color=C_P)
    label(ax, 0.5, H + 0.45, "$S$", fs=13, color=C_S)
    label(ax, 2.4, H + 0.45, "$S$", fs=13, color=C_S)
    label(ax, 1.45, 0.45, "ртуть", fs=10.5)
    label(ax, 1.45, -0.6, "$p_1 = \\dfrac{m_в g}{S},\\ p_2 = \\rho_к g h_к$", fs=11.5, color=C_P)
    save(fig, "hydro-utube-mercury-kerosene.png")


def utube_three_liquids_problem():
    """Lukashik 545: water, mercury and kerosene; the mercury level is lower on the right (not to scale)."""
    fig, ax = plt.subplots(figsize=(6.8, 5.6))
    ax.set_xlim(-1.6, 5.4)
    ax.set_ylim(-1.0, 7.4)
    ax.set_aspect("equal")
    ax.axis("off")
    scale = 0.12
    hw, hk = 20 * scale, 33.5 * scale
    dm = 0.35  # exaggerated: 0,5 cm would be 0,06
    yb = 1.5
    H = 6.9
    utube(ax, 0.0, [(0.9, yb + dm, MERC), (yb + dm, yb + dm + hw, WATER)], [(0.9, yb, MERC), (yb, yb + hk, KERO)], MERC, H=H)
    line(ax, [-0.4, 3.4], [yb, yb], color=INK, lw=1.2, ls=(0, (4, 3)), z=6)
    line(ax, [-0.4, 1.0], [yb + dm, yb + dm], color=INK, lw=1.0, ls=(0, (4, 3)), z=6)
    dim(ax, (-0.25, yb + dm), (-0.25, yb + dm + hw), color=INK)
    label(ax, -0.85, yb + dm + hw / 2, "$h_в$", fs=13)
    dim(ax, (3.55, yb), (3.55, yb + hk), color=INK)
    label(ax, 4.1, yb + hk / 2, "$h_к$", fs=13)
    dim(ax, (-0.25, yb), (-0.25, yb + dm), color=C_F)
    label(ax, -1.0, yb + dm / 2 - 0.05, r"$\Delta h_{рт}$", fs=11.5, color=C_F)
    ax.plot([0.5], [yb], "o", color=C_P, ms=6, zorder=7)
    ax.plot([2.4], [yb], "o", color=C_P, ms=6, zorder=7)
    label(ax, 0.5, yb - 0.5, "$p_1$", fs=13, color=C_P)
    label(ax, 2.4, yb - 0.5, "$p_2$", fs=13, color=C_P)
    label(ax, 0.5, yb + dm + hw / 2, "вода", fs=10.5)
    label(ax, 2.9, yb + hk / 2, "керосин", fs=10.5, rotation=90)
    label(ax, 1.45, 0.45, "ртуть", fs=10.5)
    label(ax, 1.45, -0.55, "уровни ртути не в масштабе", fs=9.5, color=GREY)
    save(fig, "hydro-utube-three-liquids.png")


# ---------------------------------------------------------------- 16.18 and 16.23


def glass_in_glass():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
    for ax in axes:
        ax.set_xlim(-1.0, 5.6)
        ax.set_ylim(-0.9, 6.0)
        ax.set_aspect("equal")
        ax.axis("off")
    y1 = 2.6
    dl = 0.55
    ax = axes[0]
    ax.add_patch(Rectangle((0.04, 0.04), 3.92, y1, fc=WATER, ec="none", zorder=1))
    line(ax, [0, 0, 4, 4], [5.4, 0, 0, 5.4], lw=2.4)
    free_surface(ax, 0, 4, y1 + 0.04)
    dim(ax, (-0.45, 0), (-0.45, y1), color=INK)
    label(ax, -0.85, y1 / 2, "$h_1$", fs=13)
    ax.plot([1.4], [0], "o", color=C_P, ms=7, zorder=7)
    label(ax, 1.4, -0.5, "$p_1$", fs=13, color=C_P)
    ax.set_title("Было", fontsize=11)
    ax = axes[1]
    y2 = y1 + dl
    ax.add_patch(Rectangle((0.04, 0.04), 3.92, y2, fc=WATER, ec="none", zorder=1))
    line(ax, [0, 0, 4, 4], [5.4, 0, 0, 5.4], lw=2.4)
    free_surface(ax, 0, 4, y2 + 0.04)
    line(ax, [-0.2, 4.2], [y1 + 0.04, y1 + 0.04], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    xs0, xs1 = 1.3, 2.7  # small glass, floating, bottom under water
    ytop, ybot = 4.1, 1.5
    poly(ax, [(xs0, ytop), (xs0 + 0.1, ybot), (xs1 - 0.1, ybot), (xs1, ytop)], fc=PAPER, lw=2.2, z=4, alpha=0.85)
    ax.add_patch(Rectangle((xs0 + 0.15, ybot + 0.12), (xs1 - xs0) - 0.3, 0.3, fc=PLATE_PALE, ec="none", zorder=5))
    dim(ax, (-0.45, 0), (-0.45, y2), color=INK)
    label(ax, -0.85, y2 / 2, "$h_2$", fs=13)
    ax.plot([1.4], [0], "o", color=C_P, ms=7, zorder=7)
    label(ax, 1.4, -0.5, "$p_2$", fs=13, color=C_P)
    label(ax, 3.55, y2 + 0.45, r"$h_2 > h_1$", fs=11.5, color=C_P)
    ax.set_title("Стало: стакан плавает", fontsize=11)
    save(fig, "hydro-glass-in-glass.png")


def two_vessels():
    fig = plt.figure(figsize=(10.0, 4.4))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(-0.6, 9.4)
    ax.set_ylim(-1.2, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")
    s1, s2 = 2.4, 3.6
    h1, h2 = 3.6, 2.4
    for x0, w, hh, name, sn in ((0.5, s1, h1, "1", "$S_1$"), (4.6, s2, h2, "2", "$S_2$")):
        ax.add_patch(Rectangle((x0, 0), w, hh, fc=WATER, ec="none", zorder=1))
        line(ax, [x0, x0, x0 + w, x0 + w], [4.6, 0, 0, 4.6], lw=2.4)
        free_surface(ax, x0, x0 + w, hh)
        dim(ax, (x0, -0.45), (x0 + w, -0.45), color=C_S)
        label(ax, x0 + w / 2, -0.9, sn, fs=13, color=C_S)
        label(ax, x0 + w / 2, hh / 2, name, fs=13)
    dim(ax, (3.35, 0), (3.35, h1), color=INK)
    label(ax, 3.7, h1 / 2, "$h_1$", fs=13)
    dim(ax, (8.5, 0), (8.5, h2), color=INK)
    label(ax, 8.95, h2 / 2, "$h_2$", fs=13)
    line(ax, [0.3, 8.8], [h2, h2], color=GREY, lw=1.0, ls=(0, (4, 3)), z=2)
    label(ax, 4.6, 5.2, "поровну воды: $m_1 = m_2$, $S_2 = 1{,}5\\,S_1$", fs=10.5)
    ax2 = fig.add_axes([0.6, 0.14, 0.37, 0.72])
    xs = np.arange(4)
    vals = [1, 1, 1.5, 1]
    cols = [C_F, C_F, C_P, C_P]
    ax2.bar(xs, vals, color=cols, width=0.62, zorder=3)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(["$F_1$", "$F_2$", "$p_1$", "$p_2$"], fontsize=13)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.set_ylim(0, 1.9)
    ax2.text(0.5, 1.12, "$F_1 = F_2$", ha="center", fontsize=12, color=C_F)
    ax2.text(2.5, 1.62, "$p_1 = 1{,}5\\,p_2$", ha="center", fontsize=12, color=C_P)
    save(fig, "hydro-two-vessels.png")


if __name__ == "__main__":
    cylinder_derivation()
    p_of_h_liquids()
    plate_orientations()
    perpetuum_tubes()
    vessels_same_pressure()
    bazhinov_vessel()
    pascal_addition()
    finger_balance()
    wall_triangle()
    aquarium_cube()
    floors_pressure()
    football_chamber()
    valve_flap()
    diver_force()
    oil_water_layers()
    utube_three_high_problem()
    utube_mercury_problem()
    utube_three_liquids_problem()
    glass_in_glass()
    two_vessels()
