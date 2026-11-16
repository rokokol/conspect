"""Figures for the note "Манометры и насосы", pump part (course Физика 7-9, lesson 59).

Run: python3 pressure_pumps.py
PNG files go to content/06. Давление/00. Вложения/, prefix pump-.
Drawing helpers and the colour code come from pressure_atmosphere.py (force red, pressure blue, water light blue).
The flow curves on the graphs are a schematic model (half-sine piston speed, first-order smoothing by the air chamber), not from the lesson.
"""
from matplotlib.patches import Circle, Polygon, Rectangle
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np

from pressure_atmosphere import (
    C_F, C_P, GREEN, GREY, INK, LIGHT, WATER, WATER_EDGE, GRID,
    arrow, blank, dim_v, label, line, rect, save,
)
from theme import COPPER, PAPER, tint

ORANGE = COPPER  # a warm accent for oil curves, readable as a thin line on white

G = 9.81
OPEN_C = GREEN
SHUT_C = C_F


def valve(ax, x, y, is_open, up=True, w=0.62, h=0.5):
    """Conical flap valve on a hole at (x, y): the cone points down into the hole, lifted when open."""
    lift = 0.32 if is_open else 0.0
    col = OPEN_C if is_open else SHUT_C
    ax.add_patch(Polygon([(x - w / 2, y + h + lift), (x + w / 2, y + h + lift), (x, y + lift)], closed=True,
                         fc=tint(C_F, 0.85) if not is_open else tint(GREEN, 0.85), ec=col, lw=1.8, zorder=7))
    if is_open:
        for s in (-1, 1):
            # inside the hole, not through the solid wall beside it
            arrow(ax, (x + s * 0.1, y - 0.35), (x + s * 0.1, y + 0.4), color=WATER_EDGE, lw=1.5, scale=9, z=8)
    return col


def water_rect(ax, x0, x1, y0, y1, z=1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=WATER, ec="none", zorder=z))


def tank(ax, x0, x1, y0, y1, lvl, atm=True):
    water_rect(ax, x0, x1, y0, lvl)
    line(ax, [x0, x0, x1, x1], [y1, y0, y0, y1], lw=2.2)
    line(ax, [x0 + 0.02, x1 - 0.02], [lvl, lvl], color=WATER_EDGE, lw=2, z=2)
    if atm:
        for x in (x0 + 0.5, x1 - 0.5):
            arrow(ax, (x, lvl + 0.85), (x, lvl + 0.15), color=C_P, lw=1.8, scale=11)


# ---------------------------------------------------------------- 1. suction pump strokes


def suction_panel(ax, ox, up):
    cw = 2.8  # cylinder width
    yb, yt = 2.4, 7.0  # cylinder bottom and top
    xm = ox + cw / 2
    piston_y = 5.2 if up else 3.2
    # tank and inlet tube
    tank(ax, ox - 0.9, ox + cw + 0.9, 0.2, 1.7, 1.15, atm=True)
    water_rect(ax, xm - 0.22, xm + 0.22, 0.6, yb + 0.05, z=1)
    line(ax, [xm - 0.22, xm - 0.22], [0.6, yb], lw=2)
    line(ax, [xm + 0.22, xm + 0.22], [0.6, yb], lw=2)
    # cylinder walls with bottom neck
    line(ax, [ox, ox], [yb, yt], lw=2.4)
    line(ax, [ox + cw, ox + cw], [yb, yt], lw=2.4)
    line(ax, [ox, xm - 0.22], [yb, yb], lw=2.4)
    line(ax, [xm + 0.22, ox + cw], [yb, yb], lw=2.4)
    # water below the piston (follows the piston), water above (spout level)
    water_rect(ax, ox, ox + cw, yb, piston_y)
    water_rect(ax, ox, ox + cw, piston_y + 0.22, 6.2)
    line(ax, [ox + 0.02, ox + cw - 0.02], [6.2, 6.2], color=WATER_EDGE, lw=1.8, z=2)
    # piston: plate with a hole (valve 2)
    hx = xm - 0.55
    ax.add_patch(Rectangle((ox, piston_y), hx - 0.31 - ox, 0.22, fc=GREY, ec=INK, lw=1.6, zorder=6))
    ax.add_patch(Rectangle((hx + 0.31, piston_y), ox + cw - hx - 0.31, 0.22, fc=GREY, ec=INK, lw=1.6, zorder=6))
    # rod
    line(ax, [xm + 0.65, xm + 0.65], [piston_y + 0.22, yt + 0.5], lw=3.2, z=6)
    arrow(ax, (xm + 1.05, yt + 0.4), (xm + 1.05, yt + 1.0) if up else (xm + 1.05, yt - 0.3), color=C_F, lw=2.6, scale=14)
    # valves: bottom valve 1 open on up-stroke, piston valve 2 open on down-stroke
    c1 = valve(ax, xm, yb, up)
    c2 = valve(ax, hx, piston_y, not up)
    label(ax, ox - 0.55, yb + 0.35, "клапан 1", fs=10.5, color=c1, ha="right")
    label(ax, ox - 0.55, piston_y + 0.2, "клапан 2", fs=10.5, color=c2, ha="right")
    # spout on the right, near the top
    line(ax, [ox + cw, ox + cw + 1.3], [6.2, 6.2], lw=2.4)
    line(ax, [ox + cw, ox + cw + 1.3], [6.8, 6.8], lw=2.4)
    line(ax, [ox + cw + 1.3, ox + cw + 1.3], [6.8, 6.4], lw=2.4)
    # pressure under the piston on the up-stroke
    if up:
        label(ax, xm - 0.5, (yb + piston_y) / 2 + 0.3, "$p < p_\\mathrm{атм}$", fs=11, color=C_P)
        arrow(ax, (xm, 1.2), (xm, 2.2), color=GREEN, lw=2.2, scale=12, z=8)  # along the inlet pipe
        arrow(ax, (ox + cw + 0.65, 6.55), (ox + cw + 1.05, 6.55), color=GREEN, lw=2.0, scale=11, z=8)
        ax.text(ox - 0.75, yt + 2.0, "Поршень вверх", fontsize=12, color=INK, ha="left")
        ax.text(ox - 0.75, yt + 1.5, "атмосфера загоняет воду в цилиндр", fontsize=10.5, color=GREY, ha="left")
    else:
        arrow(ax, (hx, piston_y - 0.4), (hx, piston_y + 0.9), color=GREEN, lw=2.2, scale=12, z=8)
        ax.text(ox - 0.75, yt + 2.0, "Поршень вниз", fontsize=12, color=INK, ha="left")
        ax.text(ox - 0.75, yt + 1.5, "вода переходит в область над поршнем", fontsize=10.5, color=GREY, ha="left")


def suction_strokes():
    fig, axes = blank(12.8, 6.8, (-2.2, 14.6), (0, 9.4))
    axes[0].set_ylim(0, 9.6)
    ax = axes[0]
    suction_panel(ax, 0.6, True)
    suction_panel(ax, 8.4, False)
    save(fig, "pump-suction-strokes.png")


# ---------------------------------------------------------------- 2. force pump strokes


def force_panel(ax, ox, up):
    cw = 2.8
    yb, yt = 2.4, 6.6
    xm = ox + cw / 2
    piston_y = 5.0 if up else 3.2
    tank(ax, ox - 0.9, ox + cw + 0.9, 0.2, 1.7, 1.15, atm=True)
    water_rect(ax, xm - 0.22, xm + 0.22, 0.6, yb + 0.05)
    line(ax, [xm - 0.22, xm - 0.22], [0.6, yb], lw=2)
    line(ax, [xm + 0.22, xm + 0.22], [0.6, yb], lw=2)
    line(ax, [ox, ox], [yb, yt], lw=2.4)
    line(ax, [ox + cw, ox + cw], [yb, yt], lw=2.4)
    line(ax, [ox, xm - 0.22], [yb, yb], lw=2.4)
    line(ax, [xm + 0.22, ox + cw], [yb, yb], lw=2.4)
    water_rect(ax, ox, ox + cw, yb, piston_y)
    # solid piston and rod
    ax.add_patch(Rectangle((ox, piston_y), cw, 0.22, fc=GREY, ec=INK, lw=1.6, zorder=6))
    line(ax, [xm, xm], [piston_y + 0.22, yt + 0.5], lw=3.2, z=6)
    arrow(ax, (xm + 0.45, yt + 0.4), (xm + 0.45, yt + 1.0) if up else (xm + 0.45, yt - 0.3), color=C_F, lw=2.6, scale=14)
    c1 = valve(ax, xm, yb, up)
    label(ax, ox - 0.5, yb + 0.35, "впускной\nклапан", fs=10, color=c1, ha="right")
    # outlet valve on the right of the cylinder, feeding the air chamber
    oy = 3.0
    line(ax, [ox + cw, ox + cw + 0.9], [oy - 0.3, oy - 0.3], lw=2.4)
    line(ax, [ox + cw, ox + cw + 0.9], [oy + 0.3, oy + 0.3], lw=2.4)
    water_rect(ax, ox + cw, ox + cw + 0.9, oy - 0.3, oy + 0.3, z=1)
    cxv = ox + cw + 1.5
    # small horizontal valve drawn as a rotated cone: use a block with a ball
    col = SHUT_C if up else OPEN_C
    ax.add_patch(Circle((cxv - (0.0 if up else -0.0), oy), 0.28, fc=tint(C_F, 0.85) if up else tint(GREEN, 0.85), ec=col, lw=1.8, zorder=7))
    label(ax, cxv, oy - 0.9, "выпускной\nклапан", fs=10, color=col)
    # air chamber on the right
    ax_x0, ax_x1 = ox + cw + 2.0, ox + cw + 4.8
    ac_y0, ac_y1 = 2.5, 6.0
    line(ax, [ax_x0, ax_x0, ax_x1, ax_x1], [ac_y1, ac_y0, ac_y0, ac_y1], lw=2.4)
    line(ax, [ax_x0, ax_x1], [ac_y1, ac_y1], lw=2.4)
    lvl = 4.2 if up else 4.6  # down-stroke: water enters the chamber and compresses the air
    water_rect(ax, ax_x0, ax_x1, ac_y0, lvl)
    line(ax, [ax_x0 + 0.02, ax_x1 - 0.02], [lvl, lvl], color=WATER_EDGE, lw=1.8, z=2)
    label(ax, ax_x0 + 1.0, (lvl + ac_y1) / 2, "воздушная\nкамера", fs=9, color=GREY)
    # connection from valve to the chamber bottom
    line(ax, [ox + cw + 0.9, ax_x0], [oy - 0.3, oy - 0.3], lw=2.4)
    line(ax, [ox + cw + 0.9, ax_x0], [oy + 0.3, oy + 0.3], lw=2.4)
    water_rect(ax, ox + cw + 0.9, ax_x0, oy - 0.3, oy + 0.3)
    # outlet tube: from below the water level in the chamber up through the top
    tx = ax_x1 - 0.6
    line(ax, [tx - 0.2, tx - 0.2], [3.0, 8.5], lw=2)
    line(ax, [tx + 0.2, tx + 0.2], [3.0, 8.5], lw=2)
    water_rect(ax, tx - 0.2, tx + 0.2, 3.0, 8.0 if not up else 8.5)
    if up:
        arrow(ax, (tx, 6.6), (tx, 7.7), color=GREEN, lw=2.2, scale=12, z=8)
        label(ax, tx + 0.35, 7.15, "воздух\nпродолжает\nвыталкивать", fs=9.5, color=GREEN, ha="left")
        label(ax, xm - 0.5, (yb + piston_y) / 2 + 0.3, "$p < p_\\mathrm{атм}$", fs=11, color=C_P)
        arrow(ax, (xm, 1.2), (xm, 2.2), color=GREEN, lw=2.2, scale=12, z=8)  # along the inlet pipe
        ax.text(ox - 0.75, yt + 1.6, "Поршень вверх", fontsize=12, color=INK, ha="left")
        ax.text(ox - 0.75, yt + 1.05, "впускной клапан открыт, вода входит", fontsize=10.5, color=GREY, ha="left")
    else:
        arrow(ax, (xm + 0.9, oy), (xm + 1.4, oy), color=GREEN, lw=2.2, scale=12, z=9)
        arrow(ax, (tx, 5.6), (tx, 6.8), color=GREEN, lw=2.2, scale=12, z=8)
        label(ax, tx + 0.35, 6.2, "воздух сжат", fs=9.5, color=GREEN, ha="left")
        ax.text(ox - 0.75, yt + 1.6, "Поршень вниз", fontsize=12, color=INK, ha="left")
        ax.text(ox - 0.75, yt + 1.05, "вода открывает выпускной клапан", fontsize=10.5, color=GREY, ha="left")


def force_strokes():
    fig, axes = blank(13.8, 6.4, (-2.2, 21.4), (0, 9.4))
    ax = axes[0]
    force_panel(ax, 0.6, True)
    force_panel(ax, 10.6, False)
    save(fig, "pump-force-strokes.png")


# ---------------------------------------------------------------- 3. cycle graph


def cycle_graph():
    t = np.linspace(0, 2, 2000)
    y = 0.5 - 0.5 * np.cos(2 * np.pi * t)  # 0 bottom, 1 top
    v = np.gradient(y, t)
    up = v > 0
    fig, axs = plt.subplots(4, 1, figsize=(9.6, 8.2), sharex=True, gridspec_kw=dict(height_ratios=[1.6, 0.8, 1, 1]))
    ax = axs[0]
    ax.plot(t, y, color=INK, lw=2.2)
    ax.set_ylabel("положение\nпоршня")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["низ", "верх"])
    for a in axs:
        a.grid(color=GRID, lw=0.7, axis="x")
        a.spines["top"].set_visible(False)
        a.spines["right"].set_visible(False)
    for k in range(2):
        ax.text(k + 0.25, 1.08, "вверх", ha="center", fontsize=10.5, color=GREEN)
        ax.text(k + 0.75, 1.08, "вниз", ha="center", fontsize=10.5, color=C_F)
        for a in axs:
            a.axvspan(k, k + 0.5, color=tint(GREEN, 0.9), lw=0, zorder=0)
            a.axvspan(k + 0.5, k + 1, color=tint(C_F, 0.9), lw=0, zorder=0)
    ax.set_ylim(-0.1, 1.25)
    # valve states
    ax = axs[1]
    ax.fill_between(t, 1.2, 2.0, where=up, color=OPEN_C, alpha=0.75, lw=0, step="mid")
    ax.fill_between(t, 0, 0.8, where=~up, color=OPEN_C, alpha=0.75, lw=0, step="mid")
    ax.set_yticks([0.4, 1.6])
    ax.set_yticklabels(["клапан 2\n(в поршне) или\nвыпускной", "клапан 1\nвпускной"])
    ax.set_ylim(0, 2.0)
    ax.text(2.0, 2.05, "зелёное: клапан открыт", ha="right", fontsize=9.5, color=GREEN)
    # flow: suction pump delivers on the up-stroke, force pump on the down-stroke
    q_up = np.where(up, np.abs(v), 0)
    q_dn = np.where(~up, np.abs(v), 0)
    q_up /= q_up.max()
    q_dn /= q_dn.max()
    ax = axs[2]
    ax.fill_between(t, q_up, color=C_P, alpha=0.75, lw=0)
    ax.set_ylabel("всасывающий\nнасос: подача")
    ax.set_yticks([])
    ax = axs[3]
    ax.fill_between(t, q_dn, color=C_P, alpha=0.75, lw=0)
    ax.set_ylabel("нагнетательный\nбез камеры: подача")
    ax.set_yticks([])
    axs[3].set_xlabel("время, ходов поршня вверх и вниз")
    axs[3].set_xticks([0, 0.5, 1, 1.5, 2])
    axs[3].set_xticklabels(["0", "1/2", "1", "3/2", "2"])
    axs[3].set_xlabel("время, в периодах")
    fig.tight_layout()
    save(fig, "pump-cycle-graph.png")


# ---------------------------------------------------------------- 4. air chamber smoothing


def chamber_graph():
    dt = 0.0005
    t = np.arange(0, 3, dt)
    v = np.sin(2 * np.pi * t)
    q_in = np.where(v < 0, -v, 0.0)  # delivery on the down-stroke
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.plot(t, q_in, color=GREY, lw=1.6, label="без воздушной камеры")
    for tau, col, name in ((0.06, ORANGE, "камера малая"), (0.22, C_P, "камера большая")):
        q = np.zeros_like(t)
        for i in range(1, len(t)):
            q[i] = q[i - 1] + dt * (q_in[i] - q[i - 1]) / tau
        ax.plot(t, q, color=col, lw=2.4, label=name)
    ax.axhline(2 / np.pi / 2 * 1.0, color=INK, lw=1, ls=":")
    ax.text(0.03, 2 / np.pi / 2 + 0.03, "средняя подача", ha="left", fontsize=10)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("время, в периодах")
    ax.set_ylabel("подача воды, отн. ед.")
    ax.set_title("Воздушная камера сглаживает подачу")
    ax.grid(color=GRID, lw=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    save(fig, "pump-air-chamber-graph.png")


# ---------------------------------------------------------------- 5. suction limit


def suction_limit():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.6), gridspec_kw=dict(width_ratios=[1.15, 1]))
    p = np.linspace(40, 105, 100)
    for rho, name, col in ((1000, "вода", C_P), (850, "минеральное масло, $850$ кг/м$^3$", ORANGE)):
        a.plot(p, p * 1000 / (rho * G), color=col, lw=2.3, label=name if rho != 1000 else "вода, $1000$ кг/м$^3$")
    a.axvline(101.3, color=GREY, ls=":", lw=1.2)
    a.plot([101.3], [101300 / (1000 * G)], "o", color=C_F, ms=7, zorder=5)
    a.annotate("$\\approx 10$ м: предел\nвсасывающего насоса", (101.3, 10.33), (55, 10.6), fontsize=10.5, color=C_F,
               arrowprops=dict(arrowstyle="->", color=C_F))
    a.annotate("нормальное\nдавление $101{,}3$ кПа", (101.3, 1.5), (72, 1.3), fontsize=10, color=GREY)
    a.set_xlabel("атмосферное давление, кПа")
    a.set_ylabel("наибольшая высота подъёма, м")
    a.set_title("Насос не поднимает выше столба,\nкоторый держит атмосфера", fontsize=11.5)
    a.set_xlim(40, 105)
    a.set_ylim(0, 15)
    a.grid(color=GRID, lw=0.8)
    a.legend(loc="upper left", frameon=False, fontsize=10)

    # right panel: possible lift of the two designs
    b.set_xlim(0, 3)
    b.set_ylim(0, 30)
    b.bar([0.75], [10.33], width=0.8, color=C_P, alpha=0.85)
    b.bar([2.25], [29], width=0.8, color=GREEN, alpha=0.85)
    b.annotate("", (2.25, 30), (2.25, 29), arrowprops=dict(arrowstyle="->", color=GREEN, lw=2))
    b.text(0.75, 11.2, "$\\approx 10$ м", ha="center", fontsize=11)
    b.text(2.25, 20, "любая\nвысота", ha="center", fontsize=11, color=PAPER)
    b.axhline(20, color=C_F, ls="--", lw=1.3)
    b.text(0.75, 20.7, "требуется $20$ м", ha="center", color=C_F, fontsize=10)
    b.set_xticks([0.75, 2.25])
    b.set_xticklabels(["всасывающий\n(над водой)", "нагнетательный\n(внизу, в воде)"])
    b.set_ylabel("высота подъёма воды, м")
    b.set_title("Что может поднять воду на $20$ м", fontsize=11.5)
    for x in (a, b):
        x.spines["top"].set_visible(False)
        x.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "pump-suction-limit.png")


# ---------------------------------------------------------------- 6. problem 19.16, heights


def heights_problem():
    fig, axes = blank(11.6, 6.6, (0, 17), (-0.5, 10.5))
    ax = axes[0]
    # left: pump high above the water, the atmosphere does the lifting
    tank(ax, 0.6, 4.6, 0.0, 1.5, 1.0, atm=True)
    xm = 2.6
    water_rect(ax, xm - 0.2, xm + 0.2, 0.4, 5.6)
    line(ax, [xm - 0.2, xm - 0.2], [0.4, 6.0], lw=2)
    line(ax, [xm + 0.2, xm + 0.2], [0.4, 6.0], lw=2)
    rect(ax, xm - 0.9, 6.0, 1.8, 2.2, fc=LIGHT)
    label(ax, xm, 7.1, "насос", fs=11)
    dim_v(ax, xm + 1.5, 1.0, 6.0, "$H \\leq 10$ м", fs=12)
    label(ax, xm, 9.1, "выше атмосфера воду\nне поднимет", fs=10.5, color=C_F)
    label(ax, xm, 9.9, "Вариант а: насос над водой", fs=11.5)
    # right: pump on the bottom in the water, delivery pipe goes up
    xt = 11.6
    ax.add_patch(Rectangle((8.6, 0.0), 5.2, 3.2, fc=WATER, ec=INK, lw=2.2, zorder=1))
    rect(ax, xt - 0.9, 0.6, 1.8, 1.6, fc=LIGHT, z=4)
    label(ax, xt, 1.4, "насос", fs=11, zorder=6)
    line(ax, [xt - 0.2, xt - 0.2], [2.2, 10.0], lw=2)
    line(ax, [xt + 0.2, xt + 0.2], [2.2, 10.0], lw=2)
    water_rect(ax, xt - 0.2, xt + 0.2, 2.2, 9.6, z=2)
    dim_v(ax, xt + 1.4, 3.2, 9.8, "$20$ м и больше", fs=12)
    arrow(ax, (xt - 1.4, 1.4), (xt - 0.95, 1.4), color=C_F, lw=2, scale=12)
    label(ax, xt - 2.6, 1.4, "поршень\nдавит воду", fs=10, color=C_F)
    label(ax, xt, 10.4, "Вариант б: насос на дне", fs=11.5)
    save(fig, "pump-problem-heights.png")


# ---------------------------------------------------------------- 7. problem 19.17, piston direction


def check_valve(ax, x, y, is_open, direction=+1):
    """A check valve on a horizontal pipe at (x, y): ball, seat; flow direction is +1 (to the right)."""
    col = OPEN_C if is_open else SHUT_C
    ax.add_patch(Rectangle((x - 0.5, y - 0.45), 1.0, 0.9, fc=PAPER, ec=INK, lw=2, zorder=6))
    shift = 0.18 * direction if is_open else -0.05 * direction
    ax.add_patch(Circle((x + shift, y), 0.24, fc=tint(GREEN, 0.85) if is_open else tint(C_F, 0.85), ec=col, lw=2, zorder=7))
    line(ax, [x - 0.5 * direction * -1, x - 0.5 * direction * -1], [y - 0.28, y + 0.28], color=INK, lw=2.4, z=8)
    return col


def piston_direction():
    fig, axes = blank(12.6, 5.4, (0, 20.8), (0, 7.4))
    ax = axes[0]
    for ox, up in ((0.4, True), (10.8, False)):
        y = 1.6
        # pipe
        for yy in (y - 0.35, y + 0.35):
            line(ax, [ox, ox + 4.0], [yy, yy], lw=2.2)
            line(ax, [ox + 5.6, ox + 9.6], [yy, yy], lw=2.2)
        water_rect(ax, ox, ox + 9.6, y - 0.35, y + 0.35, z=0)
        # cylinder above the pipe
        line(ax, [ox + 4.0, ox + 4.0], [y + 0.35, 5.0], lw=2.2)
        line(ax, [ox + 5.6, ox + 5.6], [y + 0.35, 5.0], lw=2.2)
        line(ax, [ox + 4.0, ox + 5.6], [y - 0.35, y - 0.35], lw=2.2)
        piston_y = 3.9 if up else 2.6
        water_rect(ax, ox + 4.0, ox + 5.6, y - 0.35, piston_y, z=0)
        ax.add_patch(Rectangle((ox + 4.0, piston_y), 1.6, 0.22, fc=GREY, ec=INK, lw=1.6, zorder=6))
        line(ax, [ox + 4.8, ox + 4.8], [piston_y + 0.22, 6.0], lw=3, z=6)
        arrow(ax, (ox + 5.4, 5.6), (ox + 5.4, 6.2) if up else (ox + 5.4, 5.0), color=C_F, lw=2.4, scale=13)
        cl = check_valve(ax, ox + 2.0, y, up)
        cr = check_valve(ax, ox + 7.6, y, not up)
        label(ax, ox + 2.0, y - 1.05, "открыт" if up else "закрыт", fs=10.5, color=cl)
        label(ax, ox + 7.6, y - 1.05, "закрыт" if up else "открыт", fs=10.5, color=cr)
        # flow arrows
        if up:
            arrow(ax, (ox + 0.2, y), (ox + 1.2, y), color=WATER_EDGE, lw=2.4, scale=13, z=9)
            arrow(ax, (ox + 3.0, y), (ox + 3.8, y), color=WATER_EDGE, lw=2.4, scale=13, z=9)
            ax.text(ox, 6.9, "Поршень вверх: жидкость втягивается слева", fontsize=11.5, ha="left")
        else:
            arrow(ax, (ox + 5.8, y), (ox + 6.6, y), color=WATER_EDGE, lw=2.4, scale=13, z=9)
            arrow(ax, (ox + 8.6, y), (ox + 9.6, y), color=WATER_EDGE, lw=2.4, scale=13, z=9)
            ax.text(ox, 6.9, "Поршень вниз: жидкость выталкивается вправо", fontsize=11.5, ha="left")
    save(fig, "pump-problem-piston-direction.png")


# ---------------------------------------------------------------- 8. Eiffel tower problem


def eiffel():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 5.4), gridspec_kw=dict(width_ratios=[1, 1.45]))
    # tower sketch
    a.set_xlim(-3.2, 5.2)
    a.set_ylim(-30, 372)
    a.axis("off")
    hs = np.linspace(0, 325, 60)
    half = 1.4 + 22 * np.exp(-hs / 90.0) * 0.12
    w = 0.5 + 2.6 * (1 - hs / 325) ** 2.2
    a.fill_betweenx(hs, -w, w, color=LIGHT, ec=INK, lw=1.8, zorder=2)
    a.plot([-3.0, 3.0], [0, 0], color=INK, lw=2)
    a.plot([-1.1, 1.1], [149.23, 149.23], color=INK, lw=4, zorder=3)
    for hh, name, c in ((0, "$h_0 = 0$", GREY), (149.23, "$h_1 = 149{,}23$ м", GREY), (325, "$h_2 = 325$ м", GREY)):
        a.plot([0, 3.6], [hh, hh], color=c, lw=1, ls="--", zorder=1)
        a.text(3.7, hh, name, fontsize=10.5, va="center", ha="left", color=INK)
    a.text(-3.1, 60, "$p_0 = ?$", fontsize=11.5, color=C_F, ha="left")
    # right of the tower, under the h1 mark, clear of the contour
    a.text(3.7, 149.23 - 22, "$p_1 = 1003$ гПа", fontsize=11.5, color=C_P, ha="left")
    a.text(-3.1, 340, "$p_2 = ?$", fontsize=11.5, color=C_F, ha="left")
    a.set_title("Эйфелева башня", fontsize=11.5)

    p0 = 1003 + 149.23 / 9
    p2 = 1003 - (325 - 149.23) / 9
    hh = np.linspace(0, 340, 100)
    b.plot(p0 - hh / 9, hh, color=INK, lw=2.2)
    pts = [(1003, 149.23, C_P, "$p_1 = 1003$ гПа\n(дано)"), (p0, 0, C_F, "$p_0 \\approx 1020$ гПа"), (p2, 325, C_F, "$p_2 \\approx 983$ гПа")]
    for pp, h, c, txt in pts:
        b.plot([pp], [h], "o", color=c, ms=8, zorder=5)
        b.plot([pp, pp], [0, h], color=c, lw=0.9, ls=":")
    b.annotate(pts[0][3], (1003, 149.23), (1008.5, 175), fontsize=10.5, color=C_P, arrowprops=dict(arrowstyle="->", color=C_P))
    b.annotate(pts[1][3], (p0, 0), (p0 - 14.5, 24), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    b.annotate(pts[2][3], (p2, 325), (p2 + 5.5, 300), fontsize=10.5, color=C_F, arrowprops=dict(arrowstyle="->", color=C_F))
    b.text(1005.5, 262, "наклон: $9$ м на гПа", fontsize=10.5, color=GREY)
    b.set_xlabel("атмосферное давление, гПа")
    b.set_ylabel("высота, м")
    b.set_xlim(975, 1028)
    b.set_ylim(-5, 350)
    b.grid(color=GRID, lw=0.8)
    b.spines["top"].set_visible(False)
    b.spines["right"].set_visible(False)
    b.set_title("Давление убывает с высотой линейно", fontsize=11.5)
    fig.tight_layout()
    save(fig, "pump-problem-eiffel.png")


# ---------------------------------------------------------------- 9. mug of justice


def mug_panel(ax, ox, overflow):
    # cup body: trapezoid, central column with an inverted U tube inside
    xl, xr, yb, yt = ox, ox + 4.4, 0.6, 5.6
    ax.add_patch(Polygon([(xl + 0.4, yb), (xr - 0.4, yb), (xr, yt), (xl, yt)], closed=True, fc="none", ec=INK, lw=2.4, zorder=3))
    lvl = 4.2 if not overflow else 5.15
    ytop_bend = 4.45
    # water
    wl = xl + 0.4 * (lvl - yb) / (yt - yb) * 0 + (0.4 * (1 - (lvl - yb) / (yt - yb)))
    wr = xr - (0.4 * (1 - (lvl - yb) / (yt - yb)))
    ax.add_patch(Polygon([(xl + 0.4, yb + 0.02), (xr - 0.4, yb + 0.02), (wr, lvl), (wl, lvl)], closed=True, fc=WATER, ec="none", zorder=2))
    line(ax, [wl, wr], [lvl, lvl], color=WATER_EDGE, lw=2, z=4)
    # siphon inside: column with an inverted U; the outlet goes out through the bottom
    xc = ox + 2.2
    line(ax, [xc - 0.55, xc - 0.55], [yb + 0.35, ytop_bend + 0.0], color=INK, lw=6.5, z=5)
    line(ax, [xc + 0.55, xc + 0.55], [yb - 0.6, ytop_bend + 0.0], color=INK, lw=6.5, z=5)
    t = np.linspace(np.pi, 0, 40)
    line(ax, xc + 0.55 * np.cos(t), ytop_bend + 0.55 * np.sin(t) * 0.0 + 0.0 + 0.55 * np.sin(t), color=INK, lw=6.5, z=5)
    line(ax, [xc - 0.55, xc - 0.55], [yb + 0.35, ytop_bend], color=PAPER, lw=3.6, z=6)
    line(ax, [xc + 0.55, xc + 0.55], [yb - 0.6, ytop_bend], color=PAPER, lw=3.6, z=6)
    line(ax, xc + 0.55 * np.cos(t), ytop_bend + 0.55 * np.sin(t), color=PAPER, lw=3.6, z=6)
    if overflow:
        fill = WATER
        line(ax, [xc - 0.55, xc - 0.55], [yb + 0.35, ytop_bend], color=fill, lw=3.6, z=6.5)
        line(ax, [xc + 0.55, xc + 0.55], [yb - 0.6, ytop_bend], color=fill, lw=3.6, z=6.5)
        line(ax, xc + 0.55 * np.cos(t), ytop_bend + 0.55 * np.sin(t), color=fill, lw=3.6, z=6.5)
        arrow(ax, (xc + 0.55, 2.4), (xc + 0.55, 0.3), color=GREEN, lw=2.2, scale=12, z=9)
        arrow(ax, (xc - 0.55, 1.6), (xc - 0.55, 3.2), color=GREEN, lw=2.2, scale=12, z=9)
        arrow(ax, (xc + 0.55, yb - 0.75), (xc + 0.55, yb - 1.4), color=C_P, lw=2.0, scale=11, z=9)
    else:
        line(ax, [xc - 0.55, xc - 0.55], [yb + 0.35, lvl], color=WATER, lw=3.6, z=6.5)
    # reference line on the wall
    line(ax, [xl + 0.05, xr - 0.05], [ytop_bend + 0.55, ytop_bend + 0.55], color=C_F, lw=1.2, ls="--", z=7)
    label(ax, xr + 0.2, ytop_bend + 0.55, "круговая\nлиния", fs=10, color=C_F, ha="left")
    ax.text(ox + 2.2, 6.3, "налито до линии: вода стоит" if not overflow else "налито выше линии: работает сифон",
            fontsize=11, ha="center")


def mug():
    fig, axes = blank(12.6, 5.4, (-0.6, 15.6), (-1.6, 6.9))
    ax = axes[0]
    mug_panel(ax, 0.6, False)
    mug_panel(ax, 8.6, True)
    save(fig, "pump-mug-of-justice.png")


if __name__ == "__main__":
    suction_strokes()
    force_strokes()
    cycle_graph()
    chamber_graph()
    suction_limit()
    heights_problem()
    piston_direction()
    eiffel()
    mug()
