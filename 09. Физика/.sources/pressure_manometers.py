"""Figures for the note "Манометры и насосы", manometer part (course Физика 7-9, lesson 58).

Run: python3 pressure_manometers.py
PNG files go to content/06. Давление/00. Вложения/, prefix manometer-.
Drawing helpers and the colour code come from pressure_atmosphere.py (force red, pressure blue, water light blue).
Numbers on the graphs are computed from rho, g and 1 at = 98.1 kPa; the mercury and kerosene lines are reference data, not from the lesson.
"""
from matplotlib.patches import Arc, Circle, Rectangle, Wedge
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np

from pressure_atmosphere import (
    C_F, C_P, GREEN, GREY, INK, LIGHT, MERC, MERC_EDGE, WATER, WATER_EDGE, GLASS, GRID,
    arrow, blank, dim_v, label, line, save, zigzag,
)
from theme import COPPER, PAPER, SKY, tint

ORANGE = COPPER  # a warm accent for kerosene and the spring, readable as a thin line on white

TW = 0.5  # tube width


def utube(ax, xl, xr, cy, ytop_l, ytop_r, yl, yr, liq=WATER, liq_edge=WATER_EDGE):
    """U-tube: centres of the arms xl and xr, bottom arc centre height cy, liquid levels yl and yr."""
    cx = (xl + xr) / 2
    R = (xr - xl) / 2
    ro, ri = R + TW / 2, R - TW / 2
    ax.add_patch(Wedge((cx, cy), ro, 180, 360, width=TW, fc=liq, ec="none", zorder=2))
    ax.add_patch(Rectangle((xl - TW / 2, cy), TW, yl - cy, fc=liq, ec="none", zorder=2))
    ax.add_patch(Rectangle((xr - TW / 2, cy), TW, yr - cy, fc=liq, ec="none", zorder=2))
    ax.add_patch(Arc((cx, cy), 2 * ro, 2 * ro, theta1=180, theta2=360, ec=INK, lw=2, zorder=4))
    ax.add_patch(Arc((cx, cy), 2 * ri, 2 * ri, theta1=180, theta2=360, ec=INK, lw=2, zorder=4))
    line(ax, [xl - TW / 2] * 2, [cy, ytop_l], lw=2)
    line(ax, [xl + TW / 2] * 2, [cy, ytop_l], lw=2)
    line(ax, [xr - TW / 2] * 2, [cy, ytop_r], lw=2)
    line(ax, [xr + TW / 2] * 2, [cy, ytop_r], lw=2)
    line(ax, [xl - TW / 2, xl + TW / 2], [yl, yl], color=liq_edge, lw=2, z=5)
    line(ax, [xr - TW / 2, xr + TW / 2], [yr, yr], color=liq_edge, lw=2, z=5)


def manometer(ax, ox, d, vessel_text, cy=1.6, y0=3.6, ytop=6.4, gap=2.0, vessel_fc=tint(SKY, 0.85)):
    """Liquid manometer at horizontal offset ox: the left arm is open, the right arm goes to a vessel.

    d is the level difference left minus right (positive when the vessel pressure is higher)."""
    xl, xr = ox, ox + gap
    yl, yr = y0 + d / 2, y0 - d / 2
    utube(ax, xl, xr, cy, ytop, ytop + 0.0, yl, yr)
    vc = None
    if vessel_text is not None:
        # elbow to the vessel on the right arm
        line(ax, [xr - TW / 2, xr - TW / 2], [ytop, ytop + TW], lw=2)
        line(ax, [xr - TW / 2, xr + 1.5], [ytop + TW, ytop + TW], lw=2)
        line(ax, [xr + TW / 2, xr + 1.5], [ytop, ytop], lw=2)
        vc = (xr + 2.5, ytop + TW / 2)
        ax.add_patch(Circle(vc, 1.0, fc=vessel_fc, ec=INK, lw=2, zorder=3))
        label(ax, vc[0], vc[1], vessel_text, fs=13, color=C_P)
    return dict(xl=xl, xr=xr, yl=yl, yr=yr, y0=y0, ytop=ytop, vc=vc)


def atm_arrow(ax, x, ytop):
    arrow(ax, (x, ytop + 1.05), (x, ytop + 0.25), color=C_P, lw=2.2, scale=13)
    label(ax, x, ytop + 1.3, "$p_\\mathrm{атм}$", fs=12, color=C_P)


# ---------------------------------------------------------------- 1. derivation


def derivation():
    fig, axes = blank(9.6, 6.4, (0, 13.4), (0, 8.6))
    ax = axes[0]
    d = 2.0
    g = manometer(ax, 2.6, d, "$p$")
    xl, xr, yl, yr, y0 = g["xl"], g["xr"], g["yl"], g["yr"], g["y0"]
    atm_arrow(ax, xl, g["ytop"])
    # free-surface level and the equal-level line through the lower surface
    line(ax, [xl - 1.3, xr + 0.6], [y0, y0], color=GREY, lw=1.2, ls="--", z=1)
    label(ax, xr + 0.75, y0, "0", fs=11, color=GREY, ha="left")
    line(ax, [xl - 0.85, xr + 0.6], [yr, yr], color=INK, lw=1.4, ls="--", z=1)
    # the ruler: both arms shifted by dh/2
    dim_v(ax, xl - 1.0, yr, yl, "$\\Delta h$", side="left", fs=13)
    arrow(ax, (xl + 1.0, y0), (xl + 1.0, yl), color=GREEN, lw=1.6, scale=10)
    arrow(ax, (xr - 1.0, y0), (xr - 1.0, yr), color=GREEN, lw=1.6, scale=10)
    label(ax, xl + 1.05, y0 + d / 4 + 0.05, "$\\dfrac{\\Delta h}{2}$", fs=10, color=GREEN, ha="left")
    label(ax, xr - 1.05, y0 - d / 4 - 0.05, "$\\dfrac{\\Delta h}{2}$", fs=10, color=GREEN, ha="right")
    for x, t in ((xl, "$p_1$"), (xr, "$p_2$")):
        ax.plot([x], [yr], "o", color=C_F, ms=7, zorder=7)
    label(ax, xl + 0.4, yr - 0.32, "$p_1$", fs=13, color=C_F)
    label(ax, xr + 0.5, yr - 0.32, "$p_2$", fs=13, color=C_F)
    # equations
    label(ax, 9.2, 4.1, "условие равновесия\n$p_1 = p_2$", fs=11.5, ha="left")
    label(ax, 9.2, 3.0, "$p_1 = p_\\mathrm{атм} + \\rho g\\,\\Delta h$", fs=12, ha="left")
    label(ax, 9.2, 2.2, "$p_2 = p$", fs=12, ha="left")
    ax.text(9.2, 1.0, "$p - p_\\mathrm{атм} = \\rho g\\,\\Delta h$", fontsize=13, color=INK, ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.35", fc=PAPER, ec=INK, lw=1.6))
    label(ax, 6.5, 8.35, "$p > p_\\mathrm{атм}$: жидкость слева поднялась, справа опустилась на столько же", fs=10.5, color=GREY)
    save(fig, "manometer-utube-derivation.png")


# ---------------------------------------------------------------- 2. three states


def states():
    fig, axes = blank(13.4, 5.4, (0, 22.4), (-1.3, 8.5))
    ax = axes[0]
    cases = [
        (1.7, -1.6, "$p < p_\\mathrm{атм}$", "$\\Delta h < 0$", "$p - p_\\mathrm{атм} = \\rho g\\,\\Delta h < 0$"),
        (8.7, 0.0, "$p = p_\\mathrm{атм}$", "$\\Delta h = 0$", "$p - p_\\mathrm{атм} = 0$"),
        (15.7, 1.6, "$p > p_\\mathrm{атм}$", "$\\Delta h > 0$", "$p - p_\\mathrm{атм} = \\rho g\\,\\Delta h > 0$"),
    ]
    for ox, d, ptxt, dtxt, eq in cases:
        g = manometer(ax, ox, d, "$p$", vessel_fc=tint(SKY, 0.85))
        atm_arrow(ax, g["xl"], g["ytop"])
        line(ax, [g["xl"] - 0.7, g["xr"] + 0.7], [g["y0"], g["y0"]], color=GREY, lw=1.1, ls="--", z=1)
        label(ax, ox + 1.0, -0.25, eq, fs=10.5)
        label(ax, ox + 1.0, -0.9, ptxt + ",  " + dtxt, fs=11.5, color=C_P)
    label(ax, 11.2, 8.25, "Разность уровней $\\Delta h$ (слева минус справа) со знаком показывает $p - p_\\mathrm{атм}$", fs=11, color=GREY)
    save(fig, "manometer-utube-states.png")


# ---------------------------------------------------------------- 3. probe in a liquid


def depth_probe():
    fig, axes = blank(11.0, 6.0, (0, 15.5), (-1.3, 8.4))
    ax = axes[0]
    # beaker with water
    bx0, bx1, by0, by1, lvl = 0.6, 5.2, 0.6, 5.2, 4.5
    ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, lvl - by0, fc=WATER, ec="none", zorder=1))
    line(ax, [bx0, bx0, bx1, bx1], [by1, by0, by0, by1], lw=2.2)
    line(ax, [bx0 + 0.02, bx1 - 0.02], [lvl, lvl], color=WATER_EDGE, lw=2.2, z=2)
    # probe tube from above down to depth h
    depth = 1.6
    py = lvl - depth
    px = 2.9
    ax.add_patch(Rectangle((px - 0.11, py), 0.22, by1 + 1.6 - py, fc=PAPER, ec=INK, lw=1.8, zorder=3))
    line(ax, [px - 0.11, px + 0.11], [py, py], color=WATER_EDGE, lw=1.5, z=4)
    ax.plot([px], [py], "o", color=C_F, ms=7, zorder=8)
    dim_v(ax, 1.5, py, lvl, "$h$", side="right", fs=13)
    line(ax, [1.3, px + 0.3], [py, py], color=GREY, lw=1.1, ls="--", z=1)
    label(ax, 4.5, 2.05, "вода", fs=11, color=WATER_EDGE)
    # hose from the probe to the manometer (top of the right arm)
    g = manometer(ax, 8.4, depth, None, ytop=6.4)
    ytop = g["ytop"]
    # hose from the probe top to the top of the right arm
    line(ax, [px, px, g["xr"], g["xr"]], [by1 + 1.6, 7.9, 7.9, ytop], color=GREY, lw=3.2, z=1)
    atm_arrow(ax, g["xl"], ytop)
    line(ax, [g["xl"] - 0.7, g["xr"] + 0.7], [g["y0"], g["y0"]], color=GREY, lw=1.1, ls="--", z=1)
    dim_v(ax, g["xl"] - 0.9, g["yr"], g["yl"], "$\\Delta h$", side="left", fs=13)
    label(ax, 11.6, -0.15, "жидкость в манометре та же: $\\Delta h = h$", fs=11.5, color=C_P)
    label(ax, 11.6, -0.8, "давление растёт с глубиной $p = p_\\mathrm{атм} + \\rho g h$", fs=10.5, color=GREY)
    save(fig, "manometer-depth-probe.png")


# ---------------------------------------------------------------- 4. sensitivity graph


G = 9.81
AT = 98066.5


def sensitivity():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.6))
    liquids = [("вода, $1000$ кг/м$^3$", 1000.0, C_P), ("керосин, $800$ кг/м$^3$", 800.0, ORANGE),
               ("ртуть, $13\\,600$ кг/м$^3$", 13600.0, MERC_EDGE)]
    dp = np.linspace(0, 10, 100)  # kPa
    for name, rho, col in liquids:
        a.plot(dp, dp * 1000 / (rho * G) * 100, color=col, lw=2.2, label=name)
    a.set_xlabel("$p - p_\\mathrm{атм}$, кПа")
    a.set_ylabel("$\\Delta h$, см")
    a.set_title("Чувствительность манометра")
    a.set_xlim(0, 10)
    a.set_ylim(0, 130)
    a.grid(color=GRID, lw=0.8)
    a.legend(loc="upper left", frameon=False, fontsize=10)
    a.annotate("$\\rho$ меньше: тот же перепад\nдаёт большее $\\Delta h$", (6.0, 61), (6.3, 25), fontsize=10, color=GREY,
               arrowprops=dict(arrowstyle="->", color=GREY))

    p_at = np.linspace(0, 6, 100)
    for name, rho, col in [liquids[0], liquids[2]]:
        b.plot(p_at, p_at * AT / (rho * G), color=col, lw=2.2, label=name)
    b.axvline(1.0, color=GREY, lw=1.0, ls=":")
    b.axvline(4.0, color=GREY, lw=1.0, ls=":")
    b.plot([1.0, 4.0, 6.0], [1.0 * AT / (1000 * G), 4 * AT / (1000 * G), 6 * AT / (1000 * G)], "o", color=C_F, ms=6, zorder=5)
    b.annotate("$\\approx 10$ м при 1 ат", (1.0, 10.0), (0.15, 33), fontsize=10, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    b.annotate("$> 40$ м при 4 ат", (4.0, 40.0), (2.2, 52), fontsize=10, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    b.annotate("шкала металлического\nманометра до 6 ат", (6.0, 60.0), (3.4, 20), fontsize=10, color=C_F,
               arrowprops=dict(arrowstyle="->", color=C_F))
    b.set_xlabel("избыточное давление, ат (технические атмосферы)")
    b.set_ylabel("высота столба, м")
    b.set_title("Столб жидкости при больших давлениях")
    b.set_xlim(0, 6.3)
    b.set_ylim(0, 66)
    b.grid(color=GRID, lw=0.8)
    b.legend(loc="upper left", frameon=False, fontsize=10)
    for x in (a, b):
        x.spines["top"].set_visible(False)
        x.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "manometer-sensitivity-graph.png")


# ---------------------------------------------------------------- 5. Bourdon tube


def bourdon_state(ax, ox, R, span_deg, ptr_deg, title, shade):
    """Flat tube bent in less than one turn, fixed at the bottom; the free end moves out when the tube straightens."""
    cy = -2.2 + R
    a = np.deg2rad(-90 - np.linspace(0, span_deg, 120))
    xs, ys = ox + R * np.cos(a), cy + R * np.sin(a)
    line(ax, xs, ys, color=shade, lw=11, z=3)
    line(ax, xs, ys, color=PAPER, lw=6, z=4)
    # inlet fitting
    ax.add_patch(Rectangle((ox - 0.28, -3.2), 0.56, 1.05, fc=LIGHT, ec=INK, lw=1.8, zorder=5))
    arrow(ax, (ox, -3.95), (ox, -3.25), color=C_P, lw=2.4, scale=14)
    label(ax, ox + 0.45, -3.7, "$p$", fs=13, color=C_P, ha="left")
    # closed free end
    ex, ey = xs[-1], ys[-1]
    ax.add_patch(Circle((ex, ey), 0.2, fc=INK, ec=INK, zorder=6))
    # axis with pointer, thread and return spring
    ax.add_patch(Circle((ox, 0), 0.32, fc=PAPER, ec=INK, lw=1.8, zorder=6))
    ax.add_patch(Circle((ox, 0), 0.06, fc=INK, ec=INK, zorder=7))
    line(ax, [ex, ox - 0.32], [ey, 0.0], color=GREY, lw=1.6, z=5)
    xs2, ys2 = zigzag(ox + 0.32, 0, ox + 1.15, 0, 3, 0.11)
    line(ax, xs2, ys2, color=ORANGE, lw=1.5, z=5)
    line(ax, [ox + 1.15, ox + 1.15], [-0.25, 0.25], lw=3)
    th = np.deg2rad(ptr_deg)
    arrow(ax, (ox, 0), (ox + 1.7 * np.cos(th), 1.7 * np.sin(th)), color=INK, lw=2.6, scale=15, z=8)
    # scale arc
    t = np.linspace(np.deg2rad(20), np.deg2rad(160), 60)
    line(ax, ox + 1.95 * np.cos(t), 1.95 * np.sin(t), color=GREY, lw=1.3)
    label(ax, ox + 1.95 * np.cos(np.deg2rad(160)) - 0.35, 1.95 * np.sin(np.deg2rad(160)), "0", fs=10, color=GREY)
    label(ax, ox, 3.55, title, fs=10.5)


def bourdon():
    fig, axes = blank(11.6, 6.0, (-3.6, 13.8), (-4.4, 4.6))
    ax = axes[0]
    bourdon_state(ax, 0, 2.2, 250, 125, "Давление низкое:\nтрубка свёрнута сильнее,\nстрелка у нуля", INK)
    bourdon_state(ax, 8.6, 2.45, 232, 55, "Давление выше:\nтрубка немного распрямилась,\nнить повернула ось", INK)
    label(ax, 4.3, -4.25, "плоская металлическая трубка, запаянная с конца; нить обмотана вокруг оси, другой конец нити на пружине",
          fs=9.5, color=GREY)
    save(fig, "manometer-bourdon-mechanism.png")


# ---------------------------------------------------------------- 6. dials


def dial(ax, ox, vmin, vmax, a0, a1, majors, unit, name, reading, note):
    """Dial with a linear scale between angles a0 and a1 (degrees, clockwise from a0)."""
    def th(v):
        return np.deg2rad(a0 + (v - vmin) / (vmax - vmin) * (a1 - a0))

    ax.add_patch(Circle((ox, 0), 3.35, fc=PAPER, ec=INK, lw=2.4, zorder=1))
    for v in np.linspace(vmin, vmax, int(round((vmax - vmin) / majors[1])) * 5 + 1):
        big = abs((v - vmin) / majors[1] - round((v - vmin) / majors[1])) < 1e-6
        r0 = 2.72 if big else 2.9
        line(ax, [ox + r0 * np.cos(th(v)), ox + 3.05 * np.cos(th(v))], [r0 * np.sin(th(v)), 3.05 * np.sin(th(v))],
             lw=1.8 if big else 0.9, z=3)
        if big:
            label(ax, ox + 2.32 * np.cos(th(v)), 2.32 * np.sin(th(v)), majors[0](v), fs=10.5)
    label(ax, ox, -0.85, unit, fs=11, color=GREY)
    label(ax, ox, -1.35, name, fs=8.5, color=GREY)
    arrow(ax, (ox, 0), (ox + 1.9 * np.cos(th(reading)), 1.9 * np.sin(th(reading))), color=INK, lw=2.6, scale=16, z=8)
    ax.add_patch(Circle((ox, 0), 0.12, fc=INK, ec=INK, zorder=9))
    label(ax, ox, -4.05, note, fs=10.5)


def dials():
    fig, axes = blank(12.4, 5.2, (-3.8, 16.2), (-5.2, 3.7))
    ax = axes[0]
    fmt = lambda v: str(int(round(v)))
    # manometer 0..6 at, 270 degrees sweep from 225 (left-down) clockwise
    dial(ax, 0, 0, 6, 225, -45, (fmt, 1), "кгс/см$^2$", "МАНОМЕТР", 1.0, "избыточное давление,\nшкала от $0$ до $6$ ат")
    # vacuum gauge -1..0
    dial(ax, 8.2, -1, 0, 225, -45, (lambda v: fmt(v) if v else "0", 0.2 * 5), "кгс/см$^2$", "ВАКУУММЕТР", -0.75,
         "разрежение,\n$-1$ ат: почти нулевое давление")
    # scale bar: 1 at compared with 1 atm
    ax.text(12.0, 2.2, "1 ат = 1 кгс/см$^2$", fontsize=11, ha="left", color=INK)
    ax.text(12.0, 1.2, "$\\approx 10\\ \\mathrm{Н/см^2}$", fontsize=11, ha="left", color=INK)
    ax.text(12.0, 0.2, "$\\approx 100$ кПа", fontsize=11, ha="left", color=INK)
    ax.text(12.0, -0.8, "$\\approx p_\\mathrm{атм}$", fontsize=11, ha="left", color=C_F)
    ax.text(12.0, -1.9, "баллоны с газом:\nсотни атмосфер", fontsize=10, ha="left", color=GREY)
    save(fig, "manometer-dials.png")


# ---------------------------------------------------------------- 7. siphon


def siphon():
    fig, axes = blank(9.6, 6.9, (0, 13.6), (-1.5, 9.0))
    ax = axes[0]
    # vessel
    x0, x1, y0, y1, lvl = 1.0, 5.6, 1.4, 5.2, 4.3
    ax.add_patch(Rectangle((x0, y0), x1 - x0, lvl - y0, fc=WATER, ec="none", zorder=1))
    line(ax, [x0, x0, x1, x1], [y1, y0, y0, y1], lw=2.2)
    line(ax, [x0 + 0.02, x1 - 0.02], [lvl, lvl], color=WATER_EDGE, lw=2.2, z=2)
    # tube: short arm inside the vessel, arc on the top, long arm outside
    xa, xb = 3.0, 8.2
    top = 7.6
    yend = -0.2
    for dx, lw, col, z in ((0.0, 9, INK, 3), (0.0, 5.2, PAPER, 4)):
        r = (xb - xa) / 2
        cxm = (xa + xb) / 2
        t = np.linspace(np.pi, 0, 60)
        xs = np.concatenate([[xa, xa], cxm + r * np.cos(t), [xb, xb]])
        ys = np.concatenate([[y0 + 0.5, top - r], top - r + r * np.sin(t), [top - r, yend]])
        line(ax, xs, ys, color=col, lw=lw, z=z)
    # water inside the tube (below the top)
    r = (xb - xa) / 2
    ax.plot([xa, xa], [y0 + 0.5, top - r], color=WATER, lw=5.2, zorder=4.5, solid_capstyle="butt")
    ax.plot([xb, xb], [top - r, yend], color=WATER, lw=5.2, zorder=4.5, solid_capstyle="butt")
    t = np.linspace(np.pi, 0, 60)
    ax.plot((xa + xb) / 2 + r * np.cos(t), top - r + r * np.sin(t), color=WATER, lw=5.2, zorder=4.5, solid_capstyle="butt")
    # atmosphere on the surface
    for x in (1.9, 4.6):
        arrow(ax, (x, lvl + 1.0), (x, lvl + 0.2), color=C_P, lw=2, scale=12)
    label(ax, 1.9, lvl + 1.3, "$p_\\mathrm{атм}$", fs=11, color=C_P)
    # marks
    ys2 = lvl
    line(ax, [xa - 0.5, xb + 1.6], [ys2, ys2], color=GREY, lw=1.2, ls="--", z=1)
    ax.plot([xa], [ys2], "o", color=C_F, ms=7, zorder=8)
    ax.plot([xb], [ys2], "o", color=C_F, ms=7, zorder=8)
    label(ax, xa + 0.45, ys2 - 0.5, "$p_1 = p_\\mathrm{атм}$", fs=11.5, color=C_F, ha="left")
    label(ax, xb + 0.4, ys2 + 0.3, "$p_2$", fs=13, color=C_F, ha="left")
    dim_v(ax, xb + 1.35, yend, ys2, "$\\Delta h$", fs=13)
    arrow(ax, (xb, yend - 0.25), (xb, yend - 0.9), color=C_P, lw=2, scale=12)
    label(ax, xb + 0.35, yend - 0.5, "$p = p_\\mathrm{атм}$", fs=11, color=C_P, ha="left")
    # equations
    label(ax, 10.9, 7.9, "$p_2 = p_\\mathrm{атм} - \\rho g\\,\\Delta h$", fs=12, ha="center")
    label(ax, 10.9, 7.0, "$p_2 < p_1$", fs=13, color=C_F)
    label(ax, 10.9, 6.3, "жидкость течёт от $p_1$ к $p_2$", fs=10.5, color=GREY)
    # flow arrows
    arrow(ax, (xa, 6.0), (xa, 6.6), color=GREEN, lw=2.2, scale=12, z=9)
    arrow(ax, (xb, 5.6), (xb, 4.9), color=GREEN, lw=2.2, scale=12, z=9)
    arrow(ax, (xb, 1.6), (xb, 0.9), color=GREEN, lw=2.2, scale=12, z=9)
    save(fig, "manometer-siphon.png")


if __name__ == "__main__":
    derivation()
    states()
    depth_probe()
    sensitivity()
    bourdon()
    dials()
    siphon()
