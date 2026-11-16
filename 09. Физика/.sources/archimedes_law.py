"""Figures for the note "Закон Архимеда" (course Физика 7-9, lessons 63-66).

Run: python3 archimedes_law.py
PNG files go to content/07. Закон Архимеда и плавание/00. Вложения/, prefix archimedes-.
Colour code as in pressure_solids.py: force red, area green, pressure blue; water light blue.
The Archimedes force is orange so that it differs from the thread force and gravity.
Numbers marked "условно" in a figure are illustrative and do not come from the lecture.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np
from matplotlib.patches import Polygon, Rectangle
from matplotlib.ticker import FuncFormatter

from pressure_hydrostatic import C_OIL, C_WATER, WATER, WATER_EDGE, dim, free_surface, line, rect
from pressure_solids import BODY, C_F, C_P, C_S, GREY, GRID, INK, METAL, arrow, blank
from theme import ACCENT, COPPER, GREEN, PAPER, VIOLET, WARM, num, saver, tint

from course import COURSE

OUT = COURSE / "content" / "07. Закон Архимеда и плавание" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

C_A = ACCENT  # Archimedes force
C_ACID = VIOLET
GOLD = tint(WARM, 0.4)
ALLOY = tint(COPPER, 0.5)
SILVER = tint(INK, 0.7)
COMMA = FuncFormatter(lambda v, _: num(v, None))


save = saver(OUT)


def label(ax, x, y, text, fs=11, color=INK, ha="center", va="center", zorder=10, **kw):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, zorder=zorder, **kw)


def force(ax, p, q, color, lw=2.6, short=False):
    # A very short arrow (to scale) needs a small head and no end shrink, or it turns into a bare triangle
    if short:
        arrow(ax, p, q, color=PAPER, lw=3.6, scale=10, zorder=7, shrinkA=0, shrinkB=0)  # halo, keeps it visible on a body
        arrow(ax, p, q, color=color, lw=2.4, scale=10, zorder=8, shrinkA=0, shrinkB=0)
    else:
        arrow(ax, p, q, color=color, lw=lw, scale=14, zorder=8)


def spring(ax, x, y0, y1, n=8, w=0.28):
    ys = np.linspace(y0, y1, 2 * n + 1)
    xs = [x + (w if i % 2 else -w) if 0 < i < 2 * n else x for i in range(2 * n + 1)]
    line(ax, xs, ys, color=INK, lw=1.4)


def hatch_support(ax, x, y, w=1.4):
    line(ax, [x - w / 2, x + w / 2], [y, y], lw=2.2)
    for k in np.linspace(x - w / 2, x + w / 2, 7):
        line(ax, [k, k + 0.16], [y, y + 0.2], color=GREY, lw=1.0)


def beaker(ax, x0, x1, y0, y1, level, edge_lw=2.2):
    ax.add_patch(Rectangle((x0 + 0.03, y0 + 0.03), x1 - x0 - 0.06, level - y0 - 0.03, fc=WATER, ec="none", zorder=1))
    line(ax, [x0, x0, x1, x1], [y1, y0, y0, y1], lw=edge_lw)
    free_surface(ax, x0, x1, level)


# ------------------------------------------------------------ dynamometer, air and water
def dynamometer_experiment():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.4))
    for ax in axes:
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 9.2)
        ax.set_aspect("equal")
        ax.axis("off")
    # panel 1: air
    ax = axes[0]
    ax.set_title("В воздухе", fontsize=12)
    hatch_support(ax, 3, 8.8)
    spring(ax, 3, 8.8, 7.6)
    line(ax, [3, 3], [7.6, 4.7], color=GREY, lw=1.6)
    rect(ax, 2.1, 3.3, 1.8, 1.4, fc=BODY, lw=1.8, z=5)
    force(ax, (3, 4.0), (3, 6.0), C_F)
    force(ax, (3, 4.0), (3, 2.0), C_F)
    label(ax, 3.35, 6.0, r"$\vec{F}$", fs=14, color=C_F, ha="left")
    label(ax, 3.35, 2.0, r"$\vec{F}_\text{тяж}$", fs=14, color=C_F, ha="left")
    label(ax, 3.0, 0.9, r"$F = F_\text{тяж} = 1$ Н", fs=12)
    arrow(ax, (3.5, 7.2), (4.5, 7.2), color=INK, lw=1.4, scale=11)
    label(ax, 4.6, 7.2, "1 Н", fs=12, ha="left")
    # panel 2: water
    ax = axes[1]
    ax.set_title("В воде", fontsize=12)
    hatch_support(ax, 3.5, 8.8)
    spring(ax, 3.5, 8.8, 7.6)
    beaker(ax, 0.6, 6.4, 1.6, 6.6, 5.7)
    line(ax, [3.5, 3.5], [7.6, 4.4], color=GREY, lw=1.6, z=2)
    rect(ax, 2.6, 3.0, 1.8, 1.4, fc=BODY, lw=1.8, z=5)
    yc = 3.7
    force(ax, (3.5, 4.4), (3.5, 4.95), C_F)
    force(ax, (3.9, yc), (3.9, yc + 1.6), C_A)
    force(ax, (3.5, yc), (3.5, yc - 2.0), C_F)
    label(ax, 3.35, 4.95, r"$\vec{F}'$", fs=13, color=C_F, ha="right")
    label(ax, 4.05, 5.5, r"$\vec{F}_\text{А}$", fs=14, color=C_A, ha="left")
    label(ax, 3.65, 1.75, r"$\vec{F}_\text{тяж}$", fs=13, color=C_F, ha="left")
    arrow(ax, (4.0, 7.2), (5.0, 7.2), color=INK, lw=1.4, scale=11)
    label(ax, 5.1, 7.2, "0,2 Н", fs=12, ha="left")
    label(ax, 3.5, 0.75, r"$F' + F_\text{А} = F_\text{тяж}$", fs=12)
    label(ax, 3.5, 0.15, r"$F_\text{А} = 1 - 0{,}2 = 0{,}8$ Н", fs=12, color=C_A)
    save(fig, "archimedes-dynamometer-experiment.png")


# ------------------------------------------------------------ reading and F_A vs depth
def force_vs_depth():
    H = 1.0
    h = np.linspace(0, 1.7, 400)
    fa = 0.8 * np.minimum(h / H, 1)
    fd = 1.0 - fa
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 5.6), sharex=True)
    for ax in (a1, a2):
        ax.axvspan(0, H, color=WATER, alpha=0.45, lw=0)
        ax.axvline(H, color=GREY, lw=1.1, ls="--")
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_xlim(0, 1.7)
        ax.set_ylim(0, 1.1)
    a1.plot(h, fa, color=C_A, lw=2.6)
    a1.set_ylabel("$F_\\text{А}$, Н")
    a1.set_title("Сила Архимеда растёт, пока тело входит в воду", fontsize=12)
    a1.annotate("0,8 Н", (1.35, 0.8), (1.35, 0.9), ha="center", color=C_A, fontsize=11)
    a2.plot(h, fd, color=C_F, lw=2.6)
    a2.axhline(1.0, color=GREY, lw=1.1, ls=":")
    a2.text(1.68, 1.02, "$F_\\text{тяж} = 1$ Н", ha="right", va="bottom", fontsize=10, color=GREY)
    a2.set_ylabel("показание $F$, Н")
    a2.set_title("Показание динамометра падает и потом не меняется", fontsize=12)
    a2.annotate("0,2 Н", (1.35, 0.2), (1.35, 0.32), ha="center", color=C_F, fontsize=11)
    a2.set_xticks([0, 0.5, 1.0, 1.5])
    a2.set_xticklabels(["тело коснулось\nводы", "погружено\nнаполовину", "погружено\nполностью", "глубже"])
    a2.text(0.5, 0.06, "погружается", ha="center", fontsize=10, color=C_WATER)
    a2.text(1.35, 0.06, "погружено целиком", ha="center", fontsize=10, color=INK)
    for ax in (a1, a2):
        ax.yaxis.set_major_formatter(COMMA)
    fig.text(0.5, 0.005, "Глубина погружения нижней грани, условно: линейная часть — брусок с вертикальными стенками", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "archimedes-force-vs-depth.png")


# ------------------------------------------------------------ pressure on faces
def pressure_faces():
    fig, ax = blank(8.6, 6.4, (-1.6, 8.6), (-0.4, 8.4))
    rect(ax, 0.0, 0.0, 7.0, 8.0, lw=2.2, z=2)
    ax.add_patch(Rectangle((0.04, 0.04), 6.92, 7.4, fc=WATER, ec="none", zorder=1))
    free_surface(ax, 0.0, 7.0, 7.44)
    bx0, bx1, by0, by1 = 2.3, 4.7, 2.2, 4.4
    rect(ax, bx0, by0, bx1 - bx0, by1 - by0, fc=BODY, lw=2.0, z=5)
    # pressure arrows (blue): on top down, bottom up, sides inward
    # Pressure grows linearly with depth, so arrow length = K * depth for every arrow (also the side ones)
    K = 0.247
    for x in np.linspace(bx0 + 0.4, bx1 - 0.4, 4):
        arrow(ax, (x, by1 + K * (7.44 - by1)), (x, by1 + 0.04), color=C_P, lw=1.8, scale=11, zorder=6)
        arrow(ax, (x, by0 - K * (7.44 - by0)), (x, by0 - 0.04), color=C_P, lw=1.8, scale=11, zorder=6)
    for y in np.linspace(by0 + 0.3, by1 - 0.3, 4):
        ln = K * (7.44 - y)
        arrow(ax, (bx0 - ln, y), (bx0 - 0.04, y), color=C_P, lw=1.8, scale=11, zorder=6)
        arrow(ax, (bx1 + ln, y), (bx1 + 0.04, y), color=C_P, lw=1.8, scale=11, zorder=6)
    # resulting forces
    force(ax, (3.1, by1 - 0.1), (3.1, by1 - 0.75), C_F, lw=3.0)
    force(ax, (3.9, by0 + 0.1), (3.9, by0 + 1.5), C_F, lw=3.0)
    label(ax, 2.95, by1 - 0.55, r"$F_1$", fs=13, color=C_F, ha="right", zorder=12)
    label(ax, 4.05, by0 + 1.1, r"$F_2$", fs=13, color=C_F, ha="left", zorder=12)
    label(ax, 3.5, by1 + 1.05, r"$p_1$", fs=14, color=C_P)
    label(ax, 3.5, by0 - 1.65, r"$p_2 > p_1$", fs=14, color=C_P)
    # depths
    dim(ax, (-0.55, 7.44), (-0.55, by1))
    label(ax, 0.3, 5.9, r"$h_1$", fs=14, ha="left")
    dim(ax, (-1.2, 7.44), (-1.2, by0))
    label(ax, -1.45, 4.8, r"$h_2$", fs=14)
    ax.plot([-1.2, 0.0], [by0, by0], color=GREY, lw=0.8, ls=":")
    ax.plot([-0.55, 0.0], [by1, by1], color=GREY, lw=0.8, ls=":")
    label(ax, 7.35, 4.0, "боковые силы\nравны и\nпротивоположны", fs=10.5, color=C_P, ha="left")
    label(ax, 7.35, 1.2, r"$F_2 > F_1$" + "\n" + r"$F_\text{А} = F_2 - F_1$", fs=12.5, color=C_A, ha="left")
    save(fig, "archimedes-pressure-on-faces.png")


# ------------------------------------------------------------ partial immersion, derivation
def partial_derivation():
    fig, ax = blank(9.0, 6.6, (-1.5, 9.5), (-0.6, 8.6))
    rect(ax, 0.0, 0.0, 6.6, 7.4, lw=2.2, z=2)
    wl = 5.0
    ax.add_patch(Rectangle((0.04, 0.04), 6.52, wl - 0.04, fc=WATER, ec="none", zorder=1))
    free_surface(ax, 0.0, 6.6, wl)
    bx0, bx1, by0, by1 = 2.1, 4.5, 2.0, 6.3
    rect(ax, bx0, by0, bx1 - bx0, by1 - by0, fc=BODY, lw=2.0, z=5)
    ax.plot([bx0, bx1], [wl, wl], color=WATER_EDGE, lw=1.6, ls="--", zorder=6)
    for x in np.linspace(bx0 + 0.4, bx1 - 0.4, 4):
        arrow(ax, (x, by1 + 0.8), (x, by1 + 0.04), color=C_P, lw=1.8, scale=11, zorder=6)
        arrow(ax, (x, by0 - 1.1), (x, by0 - 0.04), color=C_P, lw=1.8, scale=11, zorder=6)
    for x in (0.7, 1.4, 5.2, 5.9):
        arrow(ax, (x, wl + 0.75), (x, wl + 0.06), color=C_P, lw=1.6, scale=10, zorder=6)
    force(ax, (3.3, by1 - 0.25), (3.3, by1 - 1.05), C_F, lw=3.0)
    force(ax, (3.3, by0 + 0.25), (3.3, by0 + 1.7), C_F, lw=3.0)
    label(ax, 3.45, by1 - 0.65, r"$F_1$", fs=13, color=C_F, ha="left", zorder=12)
    label(ax, 3.45, by0 + 1.0, r"$F_2$", fs=13, color=C_F, ha="left", zorder=12)
    label(ax, 3.3, by1 + 1.15, r"$p_1 = p_\text{атм}$", fs=13, color=C_P)
    label(ax, 3.3, by0 - 1.45, r"$p_2 = p_\text{атм} + \rho_\text{ж} g h$", fs=13, color=C_P)
    label(ax, 0.9, wl + 1.2, r"$p_\text{атм}$", fs=12, color=C_P)
    dim(ax, (5.15, wl), (5.15, by0))
    label(ax, 5.45, 3.5, r"$h$", fs=14, ha="left")
    label(ax, 7.0, 1.6, "$S$ — площадь\nоснования", fs=10.5, color=C_S, ha="left")
    label(ax, 7.0, 6.4, "над водой", fs=10, color=GREY, ha="left")
    label(ax, 7.0, 3.5, "погружённая\nчасть (объём\n$V_\\text{погр} = hS$)", fs=10.5, ha="left")
    save(fig, "archimedes-partial-derivation.png")


# ------------------------------------------------------------ pressure profile with two atmospheres
def pressure_profile():
    h = np.linspace(0, 20, 100)
    rho_g = 10.0  # kPa per metre of water
    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    h1, h2 = 5.0, 15.0
    ax.axvspan(h1, h2, color=BODY, alpha=0.4, lw=0)
    ax.text((h1 + h2) / 2, 14, "тело", ha="center", fontsize=11)
    for k, (p0, col, ls, name) in enumerate(((100, C_P, "-", "$p_\\text{атм} = 100$ кПа"), (50, GREEN, "--", "$p_\\text{атм}$ меньше вдвое"))):
        ax.plot(h, p0 + rho_g * h, color=col, lw=2.4, ls=ls, label=name)
        p1, p2 = p0 + rho_g * h1, p0 + rho_g * h2
        ax.plot([h1, h2], [p1, p2], "o", color=col)
        xa = h2 + 1.0 + 1.3 * k
        ax.annotate("", (xa, p2), (xa, p1), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=1.8))
        ax.plot([h2, xa], [p1, p1], color=col, lw=0.8, ls=":")
    ax.text(h2 + 4.0, 105, "$p_2 - p_1 = 100$ кПа\nв обоих случаях", color=C_A, fontsize=10.5, va="bottom", ha="left")
    ax.set_xlim(0, 23.5)
    ax.set_ylim(0, 320)
    ax.set_xlabel("глубина $h$, м")
    ax.set_ylabel("давление $p$, кПа")
    ax.set_title("Разность давлений не зависит от $p_\\text{атм}$", fontsize=12)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(loc="upper left", frameon=False)
    fig.text(0.5, 0.005, "Числа условные; $\\rho_\\text{ж} g = 10$ кПа/м, глубины верхней и нижней граней 5 и 15 м", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "archimedes-pressure-profile.png")


# ------------------------------------------------------------ F_A(V) for several liquids
def force_vs_volume():
    v = np.linspace(0, 500, 100)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    data = ((800, "масло, 800 кг/м³", C_OIL), (1000, "вода, 1000 кг/м³", C_WATER), (1500, "раствор, 1500 кг/м³", C_ACID))
    for rho, name, col in data:
        ax.plot(v, rho * 10 * v * 1e-6, color=col, lw=2.5, label=name)
    ax.plot([200], [2.0], "o", color=C_WATER, ms=8)
    ax.annotate("тело объёмом 200 см³\nв воде: 2 Н", (200, 2.0), (250, 0.7), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY), color=INK)
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 8)
    ax.set_xlabel("объём погружённой части $V_\\text{погр}$, см³")
    ax.set_ylabel("$F_\\text{А}$, Н")
    ax.set_title("Сила Архимеда пропорциональна объёму и плотности", fontsize=12)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(loc="upper left", frameon=False)
    ax.yaxis.set_major_formatter(COMMA)
    fig.text(0.5, 0.005, "$g = 10$ Н/кг; масло 0,8 и раствор 1,5 г/см³ — значения из задач урока 65 и 66", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "archimedes-force-vs-volume.png")


# ------------------------------------------------------------ overflow vessel
def can(ax, x0=0.6, x1=4.0, y0=0.8, y1=4.4, wl=3.7):
    ax.add_patch(Rectangle((x0 + 0.03, y0 + 0.03), x1 - x0 - 0.06, wl - y0 - 0.03, fc=WATER, ec="none", zorder=1))
    line(ax, [x0, x0, x1, x1], [y1, y0, y0, y1 - 0.6], lw=2.2)
    line(ax, [x1, x1 + 0.7, x1 + 0.7], [wl + 0.02, wl + 0.02, wl - 0.45], lw=2.0)
    line(ax, [x1, x1], [y1 - 0.6, wl + 0.35], lw=2.2)
    line(ax, [x1, x1 + 0.7], [wl + 0.35, wl + 0.35], lw=2.0)
    free_surface(ax, x0, x1, wl)


def overflow_vessel():
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.6))
    for ax in axes:
        ax.set_xlim(0, 7.2)
        ax.set_ylim(0, 8.0)
        ax.set_aspect("equal")
        ax.axis("off")
    titles = ("Сосуд налит до носика", "Тело вытесняет воду", "Вытесненную воду взвешивают")
    for ax, t in zip(axes, titles):
        ax.set_title(t, fontsize=11.5)
    # 1
    ax = axes[0]
    can(ax)
    hatch_support(ax, 2.3, 7.7)
    line(ax, [2.3, 2.3], [7.7, 5.6], color=GREY, lw=1.5)
    # brick 1.4 x 0.7 = 0.98 area units; the same area as the water in the small cup (1.14 x 0.86)
    rect(ax, 1.6, 4.9, 1.4, 0.7, fc=BODY, lw=1.8, z=5)
    rect(ax, 4.1, 0.8, 1.2, 1.2, lw=2.0)
    label(ax, 4.7, 0.3, "пустой стаканчик", fs=9.5, color=GREY)
    # 2
    ax = axes[1]
    can(ax)
    hatch_support(ax, 2.3, 7.7)
    line(ax, [2.3, 2.3], [7.7, 3.3], color=GREY, lw=1.5, z=2)
    rect(ax, 1.6, 2.6, 1.4, 0.7, fc=BODY, lw=1.8, z=5)
    ax.add_patch(Rectangle((4.13, 0.83), 1.14, 0.86, fc=WATER, ec="none", zorder=1))
    rect(ax, 4.1, 0.8, 1.2, 1.2, lw=2.0)
    ax.plot([4.7, 4.7], [3.25, 1.69], color=WATER_EDGE, lw=2.4)
    label(ax, 4.7, 0.3, "$V_\\text{выт} = V_\\text{погр}$", fs=11)
    # 3
    ax = axes[2]
    hatch_support(ax, 3.6, 7.7)
    spring(ax, 3.6, 7.7, 6.5)
    line(ax, [3.6, 3.6], [6.5, 3.2], color=GREY, lw=1.5)
    # the same cup as in frames 1-2, with the same water volume
    ax.add_patch(Rectangle((3.03, 2.03), 1.14, 0.86, fc=WATER, ec="none", zorder=1))
    rect(ax, 3.0, 2.0, 1.2, 1.2, lw=2.0)
    force(ax, (3.6, 2.45), (3.6, 1.0), C_F)
    label(ax, 3.85, 1.2, r"$P_\text{выт}$", fs=13, color=C_F, ha="left")
    arrow(ax, (4.2, 6.9), (5.2, 6.9), color=INK, lw=1.4, scale=11)
    label(ax, 5.3, 6.9, "0,8 Н", fs=12, ha="left")
    label(ax, 3.6, 0.3, r"$= F_\text{А} = 0{,}8$ Н", fs=12, color=C_A)
    fig.tight_layout()
    save(fig, "archimedes-overflow-vessel.png")


# ------------------------------------------------------------ crown volumes
def crown_volumes():
    rho_au, rho_ag, m = 19.3, 10.5, 300.0
    v_au, v_ag = m / rho_au, m / rho_ag
    v_mix = 25.0
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    names = ["золотой\nслиток", "корона\nиз сплава", "серебряный\nслиток"]
    vals = [v_au, v_mix, v_ag]
    cols = [GOLD, ALLOY, SILVER]
    bars = ax.bar(names, vals, color=cols, ec=INK, lw=1.4, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.6, num(v, 1) + " см³", ha="center", fontsize=11)
    ax.set_ylim(0, 34)
    ax.set_ylabel("вытесненный объём воды, см³")
    ax.set_title("Одинаковая масса, разный объём", fontsize=12)
    ax.grid(True, axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.005, "Масса $300$ г; плотности золота $19{,}3$ и серебра $10{,}5$ г/см³; объём сплава — из задачи Гиерона", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "archimedes-crown-volumes.png")


# ------------------------------------------------------------ weight redistribution
def weight_redistribution():
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.bar([0], [1.0], color=C_F, ec=INK, width=0.5, lw=1.4, label="на динамометр")
    ax.bar([1], [0.2], color=C_F, ec=INK, width=0.5, lw=1.4)
    ax.bar([1], [0.8], bottom=[0.2], color=C_WATER, ec=INK, width=0.5, lw=1.4, label="на воду")
    ax.text(0, 0.5, "1 Н", ha="center", va="center", color=PAPER, fontsize=12)
    ax.text(1, 0.1, "0,2 Н", ha="center", va="center", color=PAPER, fontsize=11)
    ax.text(1, 0.6, "0,8 Н", ha="center", va="center", color=PAPER, fontsize=12)
    ax.axhline(1.0, color=GREY, ls="--", lw=1.2)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["в воздухе", "в воде"])
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("вес тела, Н")
    ax.yaxis.set_major_formatter(COMMA)
    ax.set_title("Вес не теряется, он делится", fontsize=12)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    save(fig, "archimedes-weight-redistribution.png")


# ------------------------------------------------------------ force diagrams for dynamometer problems
def body_panel(ax, title, x0, x1, y0, y1, wl, forces, thread_top=8.6):
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 9.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11.5)
    xc = (x0 + x1) / 2
    beaker(ax, 0.5, 6.5, 1.0, 7.2, wl)
    line(ax, [xc, xc], [thread_top, y1], color=GREY, lw=1.5, z=2)
    hatch_support(ax, xc, thread_top)


def dynamometer_problems():
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 5.0))
    # 20.16: fully immersed
    ax = axes[0]
    body_panel(ax, "Тело целиком в воде", 2.6, 4.4, 3.0, 4.6, 6.0, None)
    rect(ax, 2.6, 3.0, 1.8, 1.6, fc=BODY, lw=1.8, z=5)
    yc = 3.8
    # F = F_A = 2 N and F_tyazh = 4 N: the two upward arrows are each half of the downward one
    force(ax, (3.0, yc), (3.0, yc + 1.0), C_F)
    force(ax, (4.0, yc), (4.0, yc + 1.0), C_A)
    force(ax, (3.5, yc), (3.5, yc - 2.0), C_F)
    label(ax, 2.85, 5.05, r"$\vec{F}$", fs=13, color=C_F, ha="right")
    label(ax, 4.15, 5.05, r"$\vec{F}_\text{А}$", fs=13, color=C_A, ha="left")
    label(ax, 3.65, 1.75, r"$\vec{F}_\text{тяж}$", fs=13, color=C_F, ha="left")
    # 20.19: half immersed cylinder
    ax = axes[1]
    body_panel(ax, "Цилиндр наполовину в воде", 2.7, 4.3, 3.0, 6.4, 4.7, None)
    rect(ax, 2.7, 3.0, 1.6, 3.4, fc=METAL, lw=1.8, z=5)
    ax.plot([2.7, 4.3], [4.7, 4.7], color=WATER_EDGE, lw=1.6, ls="--", zorder=6)
    ax.plot([3.9], [4.7], "o", color=C_F, ms=6, zorder=9)
    # Scale 0.72 per newton: F_tyazh 3.12 N -> 2.25, F_A 0.2 N -> 0.144, F 2.92 N -> 2.10 (F + F_A = F_tyazh)
    force(ax, (3.1, 3.85), (3.1, 3.99), C_A, short=True)
    force(ax, (3.9, 4.7), (3.9, 2.45), C_F)
    label(ax, 2.6, 3.95,r"$\vec{F}_\text{А}$", fs=13, color=C_A, ha="right", zorder=12)
    label(ax, 4.05, 2.3, r"$\vec{F}_\text{тяж}$", fs=13, color=C_F, ha="left")
    label(ax, 4.15, 7.5, r"$\vec{F}$", fs=13, color=C_F, ha="left")
    force(ax, (3.9, 6.4), (3.9, 8.5), C_F)
    label(ax, 5.55, 3.4, "$F_\\text{А}$ в центре\nпогружённой\nчасти", fs=9, color=C_A)
    # 20.26: cube, x above water
    ax = axes[2]
    # Square cube a = 2.2, x = 0.44 above water (x / a = 0.2); scale 0.0258 per newton: 89 N -> 2.3, 8 N -> 0.21, 81 N -> 2.09
    body_panel(ax, "Куб частью над водой", 2.4, 4.6, 3.0, 5.2, 4.76, None)
    rect(ax, 2.4, 3.0, 2.2, 2.2, fc=tint(COPPER, 0.55), lw=1.8, z=5)
    ax.plot([2.4, 4.6], [4.76, 4.76], color=WATER_EDGE, lw=1.6, ls="--", zorder=6)
    force(ax, (3.1, 3.88), (3.1, 4.09), C_A, short=True)
    force(ax, (3.9, 4.1), (3.9, 1.8), C_F)
    force(ax, (3.5, 5.2), (3.5, 7.29), C_F)
    label(ax, 2.3, 3.95, r"$\vec{F}_\text{А}$", fs=13, color=C_A, ha="right", zorder=12)
    label(ax, 4.05, 1.95, r"$\vec{F}_\text{тяж}$", fs=13, color=C_F, ha="left")
    dim(ax, (5.05, 4.76), (5.05, 5.2), color=INK)
    label(ax, 5.35, 5.0, "$x$", fs=13, ha="left")
    dim(ax, (1.45, 3.0), (1.45, 5.2), color=INK)
    label(ax, 1.2, 4.1, "$a$", fs=13, ha="right")
    label(ax, 3.35, 7.1, r"$\vec{F}$", fs=13, color=C_F, ha="right")
    fig.tight_layout()
    save(fig, "archimedes-dynamometer-problems.png")


# ------------------------------------------------------------ steel part with a cavity
def cavity_part():
    fig, ax = blank(6.0, 5.6, (0, 7.0), (0, 9.0))
    beaker(ax, 0.5, 6.5, 1.0, 7.0, 6.0)
    rect(ax, 2.3, 3.0, 2.4, 2.4, fc=METAL, lw=2.0, z=5)
    rect(ax, 2.5, 3.5, 1.0, 1.0, fc=PAPER, lw=1.6, z=6)
    label(ax, 3.0, 4.0, "$V_\\text{п}$", fs=12, zorder=12)
    label(ax, 2.7, 5.05, "$V_\\text{ст}$", fs=10.5, zorder=12, color=INK)
    line(ax, [3.5, 3.5], [8.4, 5.4], color=GREY, lw=1.5, z=2)
    hatch_support(ax, 3.5, 8.4)
    force(ax, (3.95, 4.2), (3.95, 2.0), C_F)
    # Scale 0.564 per newton: mg 3.9 N -> 2.2, F 3.35 N -> 1.89, F_A 0.55 N -> 0.31
    force(ax, (3.5, 5.4), (3.5, 7.29), C_F)
    force(ax, (4.4, 4.2), (4.4, 4.51), C_A, short=True)
    label(ax, 4.1, 2.2, r"$\vec{F}_\text{тяж}$", fs=13, color=C_F, ha="left")
    label(ax, 3.3, 7.3, r"$\vec{F}$", fs=13, color=C_F, ha="right")
    label(ax, 4.85, 4.4, r"$\vec{F}_\text{А}$", fs=13, color=C_A, ha="left")
    label(ax, 3.5, 0.45, "$V = V_\\text{ст} + V_\\text{п}$", fs=12)
    save(fig, "archimedes-cavity-part.png")


# ------------------------------------------------------------ F versus liquid density (three problems)
def force_vs_density():
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.3))
    specs = [
        ("Пластилин: $F = P(1 - \\rho_\\text{ж}/\\rho)$", (0, 1.0), (1.0, 0.2), 1.5, [(1.0, 0.2)], "$\\rho = 1{,}25$ г/см³", 1.0, "Н"),
        ("Брусок: масло и вода", (0, 24.0), (1.0, 14.0), 3.0, [(0.8, 16.0), (1.0, 14.0)], "$\\rho = 2{,}4$ г/см³", 24.0, "Н"),
        ("Грузик: вода и жидкость", (0, 11.0), (1.0, 10.0), 2.0, [(1.0, 10.0), (1.5, 9.5)], "$\\rho = 11$ г/см³", 11.0, "Н"),
    ]
    for ax, (title, p0, p1, xmax, pts, dens, top, _unit) in zip(axes, specs):
        slope = (p1[1] - p0[1]) / (p1[0] - p0[0])
        xs = np.linspace(0, xmax, 50)
        ys = p0[1] + slope * xs
        zero = -p0[1] / slope
        ax.plot(xs, ys, color=C_F, lw=2.4)
        ax.plot([0], [p0[1]], "o", mfc=PAPER, mec=C_F, ms=8, zorder=6)
        ax.plot([q[0] for q in pts], [q[1] for q in pts], "o", color=C_F, ms=8, zorder=6)
        if zero <= xmax:
            ax.plot([zero], [0], "s", color=C_A, ms=8, zorder=6)
            ax.annotate(dens, (zero, 0), (0.98 * xmax, 0.4 * top), ha="right", fontsize=10.5, color=C_A, arrowprops=dict(arrowstyle="-", color=C_A))
        ax.set_xlim(0, xmax)
        ax.set_ylim(0, top * 1.12)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("плотность жидкости, г/см³")
        ax.set_ylabel("показание $F$, Н")
        ax.grid(True, color=GRID, lw=0.8)
        ax.xaxis.set_major_formatter(COMMA)
        ax.yaxis.set_major_formatter(COMMA)
    axes[0].text(0.03, 1.03, "$P$", fontsize=11, color=C_F)
    axes[1].text(0.06, 24.6, "$mg$", fontsize=11, color=C_F)
    axes[2].text(0.06, 11.25, "$P$", fontsize=11, color=C_F)
    axes[2].text(1.5, 8.6, "$\\rho_\\text{ж} = 1{,}5$ г/см³", ha="center", fontsize=10.5, color=C_A)
    fig.text(0.5, 0.005, "Прямая $F = P - \\rho_\\text{ж} g V$: точка при $\\rho_\\text{ж} = 0$ — вес в воздухе, нуль показания — плотность самого тела", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "archimedes-force-vs-density.png")


# ------------------------------------------------------------ Hiero ingot
def hiero_graph():
    m, rho_au, rho_ag = 300.0, 19.3, 10.5
    v_ing = 25.0
    ms = np.linspace(0, m, 100)
    vs = (m - ms) / rho_au + ms / rho_ag
    m_ag = (v_ing - m / rho_au) / (1 / rho_ag - 1 / rho_au)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.plot(ms, vs, color=INK, lw=2.4)
    ax.axhline(v_ing, color=C_WATER, lw=1.8, ls="--")
    ax.plot([m_ag], [v_ing], "o", color=C_A, ms=9, zorder=6)
    ax.plot([m_ag, m_ag], [0, v_ing], color=C_A, lw=1.2, ls=":")
    ax.text(5, v_ing + 0.5, "объём слитка из взвешивания в воде: 25 см³", color=C_WATER, fontsize=10.5)
    ax.annotate(f"серебра {num(m_ag, 0)} г,\nзолота {num(m - m_ag, 0)} г", (m_ag, v_ing), (m_ag - 118, 18), fontsize=11, color=C_A, arrowprops=dict(arrowstyle="-", color=C_A))
    ax.text(3, 14.5, "чистое золото", fontsize=9.5, color=GREY)
    ax.text(m - 3, 29.2, "чистое серебро", fontsize=9.5, color=GREY, ha="right")
    ax.set_xlim(0, m)
    ax.set_ylim(12, 31)
    ax.set_xlabel("масса серебра в слитке, г")
    ax.set_ylabel("объём слитка, см³")
    ax.set_title("Слиток массой 300 г: объём растёт с долей серебра", fontsize=12)
    ax.grid(True, color=GRID, lw=0.8)
    ax.xaxis.set_major_formatter(COMMA)
    ax.yaxis.set_major_formatter(COMMA)
    fig.text(0.5, 0.005, "Прямая $V = \\dfrac{m - m_\\text{Ag}}{\\rho_\\text{Au}} + \\dfrac{m_\\text{Ag}}{\\rho_\\text{Ag}}$; плотности $19{,}3$ и $10{,}5$ г/см³", ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, "archimedes-hiero-graph.png")


if __name__ == "__main__":
    dynamometer_experiment()
    force_vs_depth()
    pressure_faces()
    partial_derivation()
    pressure_profile()
    force_vs_volume()
    overflow_vessel()
    crown_volumes()
    weight_redistribution()
    dynamometer_problems()
    cavity_part()
    force_vs_density()
    hiero_graph()
