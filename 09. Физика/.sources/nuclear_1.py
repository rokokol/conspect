"""Figures for section f15 "Ядерная физика" (lessons 220-224).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 nuclear_1.py [name ...]
PNG files go to content/15. Ядерная физика/00. Вложения/ (prefixes nucleus-, decay-, halflife-)

Every figure that prints a number asserts it against the lesson data or recomputes it from the lesson formulas.
"""
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Ellipse
from matplotlib.ticker import FuncFormatter

from course import COURSE

OUT = COURSE / "content" / "15. Ядерная физика" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, VIOLET, WARM, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
GOLD = WARM  # gold, and what is gold in colour
LEAD = METAL  # a lead container and a lead layer
PROTON = tint(RED, 0.7)  # a proton: positive, so a red tint
NEUTRON = tint(INK, 0.7)  # a neutron: neutral, so a grey, hatched
POSITIVE_FILL = tint(RED, 0.85)  # a positively charged body: a nucleus, a drop
PAPER_FILL = tint(WARM, 0.8)  # a sheet of paper or a plate
PLATE = tint(INK, 0.8)  # a pale grey plate
SHADOW = tint(INK, 0.2)  # a dark shadow or a dark sheet
LIGHT_METAL = tint(INK, 0.7)  # aluminium

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def ru_axis(*axs, y=True):
    fmt = FuncFormatter(lambda v, _: num(v, None))
    for a in axs:
        a.xaxis.set_major_formatter(fmt)
        if y:
            a.yaxis.set_major_formatter(fmt)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", ls="-", ms=12, z=5, rad=0.0, shrink=0):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, ls=ls, zorder=z,
            connectionstyle=f"arc3,rad={rad}", shrinkA=shrink, shrinkB=shrink,
        )
    )


def node(ax, x, y, sym, a, col=INK, fs=9.5):
    ax.text(
        x, y, f"${{}}^{{{a}}}$" + sym, ha="center", va="center", fontsize=fs, color=col, zorder=7,
        bbox=dict(boxstyle="round,pad=0.25", fc=LIGHT, ec=col, lw=1.2),
    )


def txt(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)


def nucleon(ax, x, y, kind, r=0.5):
    if kind == "p":
        ax.add_patch(Circle((x, y), r, fc=PROTON, ec=INK, lw=1.2, zorder=4))
        txt(ax, x, y, "+", size=13, color=INK, fontweight="bold", zorder=5)  # above the disc (zorder 4)
    else:
        ax.add_patch(Circle((x, y), r, fc=NEUTRON, ec=INK, lw=1.2, hatch="////", zorder=4))


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------- nucleus-


@fig("nucleus-thomson-pudding")
def thomson():
    f, ax = plt.subplots(figsize=(4.6, 4.4))
    blank(ax, (-1.35, 1.35), (-1.45, 1.35))
    ax.add_patch(Circle((0, 0), 1.0, fc=POSITIVE_FILL, ec=RED, lw=2))
    pts = [(-0.55, 0.45), (0.1, 0.65), (0.55, 0.2), (-0.15, -0.05), (0.35, -0.5), (-0.5, -0.4), (0.0, -0.75)]
    for x, y in pts:
        ax.add_patch(Circle((x, y), 0.09, fc=BLUE, ec=INK, lw=1, zorder=4))
        txt(ax, x, y, "−", size=10, color=PAPER, fontweight="bold", zorder=5)
    txt(ax, 0, 1.22, "Положительно заряженная капля", size=10.5, color=RED)
    txt(ax, 0, -1.3, "электроны плавают внутри, как изюм в пудинге", size=10, color=BLUE)
    arrow(ax, (-1.3, -0.2), (-1.0, 0.0), color=GREY, lw=1.2, ms=9)
    txt(ax, -1.3, -0.4, "$\\sim10^{-10}$ м", size=10, color=NOTE, ha="center")
    ax.set_title("Модель Томсона")
    save(f, "nucleus-thomson-pudding")


@fig("nucleus-rutherford-setup")
def rutherford():
    f, ax = plt.subplots(figsize=(8.6, 5.4))
    blank(ax, (-6.6, 6.2), (-4.2, 4.4))
    # screen: one arc around the foil; the gap is on the left, where the beam enters
    th = np.linspace(-165, 165, 300)
    R = 3.6
    ax.plot(R * np.cos(np.radians(th)), R * np.sin(np.radians(th)), color=GREEN, lw=4, solid_capstyle="round", zorder=2)
    # foil
    ax.plot([0, 0], [-1.3, 1.3], color=GOLD, lw=5, zorder=3, solid_capstyle="butt")
    # lead container with a channel to the right
    ax.add_patch(Rectangle((-5.3, -0.75), 1.5, 1.5, fc=LEAD, ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Rectangle((-4.45, -0.12), 0.7, 0.24, fc=PAPER, ec="none", zorder=4))
    ax.add_patch(Circle((-4.7, 0), 0.13, fc=RED, ec=INK, lw=0.8, zorder=5))
    # beam
    arrow(ax, (-3.75, 0), (-0.05, 0), color=RED, lw=2, ms=13)
    # passing alphas, small angles
    for ang in (4, 9, -6, -11):
        a = math.radians(ang)
        arrow(ax, (0, 0), (3.45 * math.cos(a), 3.45 * math.sin(a)), color=RED, lw=1.3, ms=9)
    # back scattered alpha
    a = math.radians(141)
    arrow(ax, (0.0, 0.05), (3.4 * math.cos(a), 3.4 * math.sin(a)), color=RED, lw=1.8, ms=12)
    txt(ax, 3.6 * math.cos(a) - 0.75, 3.6 * math.sin(a) + 0.2, "!!!", size=15, color=RED, fontweight="bold")
    ax.plot([3.6 * math.cos(a)], [3.6 * math.sin(a)], marker="*", ms=16, color=GOLD, mec=INK, zorder=6)
    txt(ax, -2.9, 3.95, "почти назад — очень редко", size=10.5, color=RED)
    txt(ax, 4.9, 1.0, "почти все частицы\nлетят прямо или\nотклоняются слабо", size=10.5, color=RED, ha="left")
    txt(ax, -5.4, -1.35, "свинцовый контейнер\nс источником", size=10, color=NOTE)
    txt(ax, 0.0, -1.75, "золотая фольга (мишень)", size=10.5, color=INK)
    txt(ax, 3.6, -3.4, "экран с ZnS:\nвспышка — сцинтилляция", size=10.5, color=GREEN)
    ax.set_title("Опыт Резерфорда и Марсдена, 1911")
    save(f, "nucleus-rutherford-setup")


@fig("nucleus-hydrogen-isotopes")
def hydrogen():
    f, axs = plt.subplots(1, 3, figsize=(10.5, 4.2))
    specs = [
        ("протий", r"${}^{1}_{1}\mathrm{H}$", [("p", 0, 0)], (1, 1, 0)),
        ("дейтерий", r"${}^{2}_{1}\mathrm{H}$" + r", ${}^{2}_{1}\mathrm{D}$", [("p", -0.26, 0.0), ("n", 0.26, 0.0)], (1, 2, 1)),
        ("тритий", r"${}^{3}_{1}\mathrm{H}$" + r", ${}^{3}_{1}\mathrm{T}$", [("p", -0.28, -0.15), ("n", 0.3, -0.12), ("n", 0.0, 0.32)], (1, 3, 2)),
    ]
    for ax, (name, sym, parts, (Z, A, N)) in zip(axs, specs):
        blank(ax, (-2.2, 2.2), (-3.3, 2.5))
        ax.add_patch(Circle((0, 0), 1.9, fc="none", ec=BLUE, lw=1.6, ls=(0, (4, 3))))
        ax.add_patch(Circle((-1.35, 1.35), 0.14, fc=BLUE, ec=INK, lw=1))
        txt(ax, -1.35, 1.35, "−", size=10, color=PAPER, fontweight="bold", zorder=6)
        for kind, x, y in parts:
            nucleon(ax, x, y, kind, r=0.25)
        assert Z + N == A
        txt(ax, 0, -2.35, name, size=13, fontweight="bold")
        txt(ax, 0, -2.85, sym, size=12, color=NOTE)
        txt(ax, 0, 2.2, f"$Z={Z}$   $A={A}$   $N={N}$", size=11.5)
    f.suptitle("Изотопы водорода: протонов поровну, нейтронов разное число", fontsize=12.5, y=1.0)
    f.tight_layout()
    save(f, "nucleus-hydrogen-isotopes")


@fig("nucleus-fission-uranium")
def fission():
    f, axs = plt.subplots(1, 3, figsize=(11.5, 4.6))
    rng = 1.25
    # stage 1
    ax = axs[0]
    blank(ax, (-2.6, 2.6), (-3.0, 2.6))
    ax.add_patch(Circle((0, 0), 1.0, fc=POSITIVE_FILL, ec=RED, lw=2))
    for x, y in [(-0.45, 0.3), (0.3, 0.45), (0.1, -0.2), (-0.35, -0.5), (0.5, -0.4)]:
        txt(ax, x, y, "+", size=12, color=RED, fontweight="bold")
    ax.add_patch(Circle((-2.1, 1.7), 0.17, fc=NEUTRON, ec=INK, lw=1.2, hatch="////"))
    arrow(ax, (-1.9, 1.55), (-0.85, 0.75), color=GREY, lw=1.8)
    txt(ax, -1.6, 2.15, "нейтрон", size=10.5, color=NOTE)
    txt(ax, 0, -2.2, "${}^{235}_{92}\\mathrm{U}$: 92 протона,\nкруглое ядро", size=11)
    ax.set_title("1. Нейтрон попадает в ядро")
    # stage 2
    ax = axs[1]
    blank(ax, (-2.6, 2.6), (-3.0, 2.6))
    ax.add_patch(Ellipse((0, 0), 3.6, 1.5, fc=POSITIVE_FILL, ec=RED, lw=2))
    for x, y in [(-1.3, 0.0), (-0.7, 0.25), (-0.6, -0.3), (0.0, 0.1), (0.7, 0.25), (0.6, -0.3), (1.3, 0.0)]:
        txt(ax, x, y, "+", size=12, color=RED, fontweight="bold")
    ax.add_patch(Circle((0, 0), rng, fc="none", ec=GREEN, lw=1.6, ls=(0, (5, 3))))
    txt(ax, 0, 1.85, "радиус действия\nядерных сил", size=10, color=GREEN)
    arrow(ax, (-1.85, 0.0), (-2.5, 0.0), color=RED, lw=2)
    arrow(ax, (1.85, 0.0), (2.5, 0.0), color=RED, lw=2)
    txt(ax, 0, -2.2, "концы ядра вышли за предел\nядерных сил: протоны\nотталкиваются", size=10.5)
    ax.set_title("2. Ядро вытягивается")
    # stage 3
    ax = axs[2]
    blank(ax, (-2.6, 2.6), (-3.0, 2.6))
    for sx in (-1, 1):
        ax.add_patch(Ellipse((sx * 1.3, 0), 1.3, 1.1, fc=POSITIVE_FILL, ec=RED, lw=2))
        for dx, dy in [(-0.25, 0.1), (0.2, 0.2), (0.0, -0.2)]:
            txt(ax, sx * 1.3 + dx, dy, "+", size=11, color=RED, fontweight="bold")
        arrow(ax, (sx * 2.0, 0.0), (sx * 2.5, 0.0), color=BLUE, lw=2.4)
    txt(ax, 0, -2.2, "два осколка разлетаются;\nэнергию им дало\nэлектрическое отталкивание", size=10.5)
    ax.set_title("3. Два осколка")
    f.tight_layout()
    save(f, "nucleus-fission-uranium")


@fig("nucleus-electron-volt")
def electron_volt():
    f, ax = plt.subplots(figsize=(7.6, 4.6))
    blank(ax, (-2.6, 6.6), (-3.6, 3.3))
    # plates
    ax.plot([0, 0], [-1.9, 1.9], color=INK, lw=3)
    ax.plot([0, 0], [0.25, -0.25], color=PAPER, lw=6, zorder=3)
    ax.plot([2.2, 2.2], [-1.9, 1.9], color=INK, lw=3)
    ax.plot([2.2, 2.2], [0.25, -0.25], color=PAPER, lw=6, zorder=3)
    for y in np.linspace(-1.6, 1.6, 6):
        txt(ax, -0.25, y, "−", size=12, color=BLUE)
        txt(ax, 2.45, y, "+", size=12, color=RED)
    # particle
    ax.add_patch(Circle((-1.8, 0), 0.15, fc=BLUE, ec=INK, lw=1))
    arrow(ax, (-1.6, 0), (-0.2, 0), color=GREY, lw=1.6)
    ax.add_patch(Circle((3.3, 0), 0.15, fc=BLUE, ec=INK, lw=1))
    arrow(ax, (2.4, 0), (5.6, 0), color=RED, lw=2.4)
    txt(ax, 4.3, 0.5, "+1 эВ", size=14, color=RED, fontweight="bold")
    txt(ax, -1.8, 0.6, "электрон\n(заряд $-e$)", size=10.5, color=NOTE)
    # source
    ax.plot([0, 0], [-1.9, -2.5], color=INK, lw=1.5)
    ax.plot([2.2, 2.2], [-1.9, -2.5], color=INK, lw=1.5)
    # battery in the lead: short thick plate (-) to the left plate, long thin plate (+) to the right one; no wire across the gap
    ax.plot([0, 0.95], [-2.5, -2.5], color=INK, lw=1.5)
    ax.plot([1.25, 2.2], [-2.5, -2.5], color=INK, lw=1.5)
    ax.plot([0.95, 0.95], [-2.7, -2.3], color=INK, lw=4, solid_capstyle="butt")
    ax.plot([1.25, 1.25], [-2.9, -2.1], color=INK, lw=1.5, solid_capstyle="butt")
    txt(ax, 1.1, -3.3, "$U = 1$ В", size=12)
    ax.set_title("Ускоряющее напряжение 1 В даёт частице 1 эВ")
    e = 1.6e-19
    assert abs(e * 1 - 1.6e-19) < 1e-30
    save(f, "nucleus-electron-volt")


@fig("nucleus-stone-lift")
def stone():
    m = 1000e3
    g = 10
    n = 2.6e21
    e0 = 200e6 * 1.6e-19
    h = e0 * n / (m * g)
    assert abs(h - 8320) < 1
    f, ax = plt.subplots(figsize=(7.8, 3.6))
    names = ["Джомолунгма (Эверест)", "Глыба 1000 т, поднятая\nэнергией распада 1 г урана"]
    vals = [8848, h]
    ax.barh(names, vals, color=[NOTE, RED], height=0.55)
    for i, v in enumerate(vals):
        ax.text(v - 150, i, num(v, ",.0f").replace(",", " ") + " м", ha="right", va="center", color=PAPER, fontsize=12, fontweight="bold")
    ax.set_xlim(0, 9600)
    ax.set_xlabel("Высота, м")
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Один грамм урана почти достаёт до вершины Эвереста")
    f.tight_layout()
    save(f, "nucleus-stone-lift")


# ---------------------------------------------------------------- decay-


@fig("decay-becquerel-plate")
def becquerel():
    f, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
    blank(a1, (-3.4, 3.6), (-2.2, 2.9))
    a1.add_patch(Rectangle((-3.0, -0.6), 6.0, 0.5, fc=INK, ec=INK, lw=1.4))
    a1.add_patch(Rectangle((-3.0, -1.4), 6.0, 0.8, fc=PAPER_FILL, ec=INK, lw=1.4))
    txt(a1, 0, -1.0, "фотопластинка", size=10.5)
    txt(a1, 1.9, -0.35, "чёрная бумага", size=9.5, color=PAPER)
    # copper cross lying flat on the paper (side view), salt heap on it
    # the heap is wider than the cross (as the dark spot on the right panel), so it covers the cross completely
    a1.add_patch(Rectangle((-0.5, -0.1), 1.0, 0.16, fc=COPPER, ec=INK, lw=1, zorder=3))
    a1.add_patch(Polygon([(-0.8, -0.1), (0.8, -0.1), (0.0, 0.85)], fc=WARM, ec=INK, lw=1, alpha=0.85, zorder=4))
    a1.add_patch(Polygon([(-2.4, -0.1), (-1.5, -0.1), (-1.95, 0.75)], fc=WARM, ec=INK, lw=1, zorder=4))
    txt(a1, -1.95, 1.05, "соль урана", size=10.5)
    txt(a1, 0.0, 1.25, "соль урана\nна медном крестике", size=10.5)
    txt(a1, 1.9, 0.6, "крестик лежит\nна бумаге", size=10, color=INK)
    a1.set_title("Схема опыта Беккереля", pad=10)
    # developed plate
    blank(a2, (-2.0, 2.0), (-2.2, 2.9))
    a2.add_patch(Rectangle((-1.8, -1.6), 3.6, 3.2, fc=PLATE, ec=INK, lw=1.4))
    a2.add_patch(Ellipse((-0.8, -0.1), 1.3, 1.1, fc=SHADOW, ec="none", alpha=0.85))
    cx, cy = 0.75, 0.3
    a2.add_patch(Ellipse((cx, cy), 1.6, 1.6, fc=SHADOW, ec="none", alpha=0.85))
    a2.add_patch(Rectangle((cx - 0.09, cy - 0.65), 0.18, 1.3, fc=PLATE, ec="none"))
    a2.add_patch(Rectangle((cx - 0.45, cy - 0.12), 0.9, 0.18, fc=PLATE, ec="none"))
    txt(a2, -0.8, -1.05, "кучка соли", size=10)
    txt(a2, 0.75, 1.25, "тень креста", size=10, color=INK)
    a2.set_title("Проявленная пластинка", pad=10)
    f.tight_layout()
    save(f, "decay-becquerel-plate")


@fig("decay-magnetic-field-three-rays")
def three_rays():
    H = 3.6
    f, ax = plt.subplots(figsize=(7.4, 6.0))
    blank(ax, (-3.6, 4.6), (-1.6, 5.7))
    # field marks (into the page)
    for x in np.linspace(-3.0, 4.0, 8):
        for y in np.linspace(0.2, 3.0, 5):
            txt(ax, x, y, "×", size=12, color=tint(BLUE, 0.5))
    # source
    ax.add_patch(Rectangle((-0.6, -1.3), 1.2, 1.1, fc=LEAD, ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Rectangle((-0.1, -0.3), 0.2, 0.3, fc=PAPER, ec="none", zorder=4))
    txt(ax, 0, -0.75, "RaCl$_2$", size=11, color=PAPER, fontweight="bold", zorder=5)
    # plate
    ax.add_patch(Rectangle((-3.0, H), 7.0, 0.3, fc=PAPER_FILL, ec=INK, lw=1.4))
    txt(ax, 4.3, H + 0.15, "фото-\nпластинка", size=9.5, ha="left")

    def arc_path(R, sgn):
        # circle centre at (sgn*R, 0) through the origin, beam initially along +y
        y = np.linspace(0, H, 100)
        x = sgn * (R - np.sqrt(R * R - y * y))
        return x, y

    # gamma
    ax.plot([0, 0], [0, H], color=VIOLET, lw=2.2, zorder=5)
    ax.plot([0], [H], "o", color=VIOLET, ms=7, zorder=6)
    txt(ax, 0.0, H + 1.5, "$\\gamma$\nне отклоняется", size=10.5, color=VIOLET, ha="center")
    # alpha: left (positive charge, v up, B into the page: force points left); heavy, so the deflection is much smaller than beta's
    xa, ya = arc_path(30.0, -1)
    ax.plot(xa, ya, color=RED, lw=2.4, zorder=5)
    ax.plot([xa[-1]], [ya[-1]], "o", color=RED, ms=7, zorder=6)
    txt(ax, xa[-1], H + 0.8, "$\\alpha$\nзаряд $+$", size=10.5, color=RED, ha="center")
    # beta: right, a fan; every beta radius is well below the alpha one (R must stay above H)
    xs = []
    for R in (3.8, 4.4, 5.2, 6.4, 8.0):
        xb, yb = arc_path(R, +1)
        ax.plot(xb, yb, color=BLUE, lw=1.6, zorder=5)
        xs.append(xb[-1])
    ax.plot([min(xs), max(xs)], [H, H], color=BLUE, lw=5, solid_capstyle="round", zorder=6)
    txt(ax, (min(xs) + max(xs)) / 2 + 0.9, H + 0.8, "$\\beta$\nзаряд $-$", size=10.5, color=BLUE, ha="center")
    txt(ax, -2.9, 0.0, "$\\vec B$ от нас ($\\times$)", size=11, color=BLUE, ha="left")
    ax.set_title("Резерфорд: магнитное поле делит излучение радия на три части")
    save(f, "decay-magnetic-field-three-rays")


@fig("decay-penetration")
def penetration():
    f, ax = plt.subplots(figsize=(9.0, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    x0, w = 4.6, 1.0
    rows = [
        (5.0, "$\\alpha$", RED, "лист бумаги", PAPER_FILL, 0.12, "задерживает полностью"),
        (3.0, "$\\beta$", BLUE, "алюминий, несколько мм", LIGHT_METAL, 0.8, "ослабляет"),
        (1.0, "$\\gamma$", VIOLET, "толстый слой свинца", LEAD, 1.0, "ослабляет, но проходит"),
    ]
    for y, name, col, barrier, bcol, bw, verdict in rows:
        txt(ax, 0.35, y, name, size=20, color=col)
        ax.add_patch(Rectangle((x0, y - 0.6), bw, 1.2, fc=bcol, ec=INK, lw=1.4, zorder=3))
        txt(ax, x0 + bw / 2, y - 0.95, barrier, size=10, color=NOTE)
        if name == "$\\alpha$":
            arrow(ax, (0.9, y), (x0 - 0.05, y), color=col, lw=2.4)
            txt(ax, x0 + bw + 0.3, y, "$\\times$ " + verdict, size=10.5, color=col, ha="left")
        else:
            arrow(ax, (0.9, y), (x0 - 0.05, y), color=col, lw=2.4)
            arrow(ax, (x0 + bw + 0.05, y), (x0 + bw + 2.6, y), color=col, lw=1.3, ls=(0, (4, 3)))
            txt(ax, x0 + bw + 2.8, y, verdict, size=10.5, color=col, ha="left")
    ax.set_title("Проникающая способность растёт: $\\alpha$, $\\beta$, $\\gamma$")
    save(f, "decay-penetration")


@fig("decay-shift-rules-cells")
def shift_cells():
    f, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.set_xlim(-0.6, 7.6)
    ax.set_ylim(-3.0, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    cells = [(84, "Po"), (85, "At"), (86, "Rn"), (87, "Fr"), (88, "Ra"), (89, "Ac"), (90, "Th")]
    pos = {}
    for i, (z, s) in enumerate(cells):
        ax.add_patch(Rectangle((i, -0.5), 1, 1, fc=LIGHT, ec=INK, lw=1.3))
        txt(ax, i + 0.5, 0.12, s, size=15, fontweight="bold")
        txt(ax, i + 0.5, -0.27, str(z), size=10, color=NOTE)
        pos[z] = i + 0.5
    # alpha: Rn(86) -> Po(84)   (220 -> 216)
    arrow(ax, (pos[86], 0.55), (pos[84], 0.55), color=RED, lw=2.2, rad=0.6)
    txt(ax, pos[85], 1.75, "$\\alpha$: $A\\to A-4$, $Z\\to Z-2$\n${}^{220}_{86}\\mathrm{Rn}\\to{}^{216}_{84}\\mathrm{Po}$", size=10.5, color=RED)
    # beta: Ra(88) -> Ac(89)   (225 -> 225)
    arrow(ax, (pos[88], -0.55), (pos[89], -0.55), color=BLUE, lw=2.2, rad=0.8)
    txt(ax, pos[88] + 0.6, -2.0, "$\\beta$: $A\\to A$, $Z\\to Z+1$\n${}^{225}_{88}\\mathrm{Ra}\\to{}^{225}_{89}\\mathrm{Ac}$", size=10.5, color=BLUE)
    # two betas: Ra(88) -> Th(90)  (228 -> 228)
    arrow(ax, (pos[88], 0.55), (pos[90], 0.55), color=BLUE, lw=1.6, rad=-0.5, ls=(0, (5, 3)))
    txt(ax, pos[89], 1.75, "два $\\beta$: $Z+2$\n${}^{228}_{88}\\mathrm{Ra}\\to{}^{228}_{90}\\mathrm{Th}$", size=10.5, color=BLUE)
    txt(ax, 3.5, 3.3, "Номер клетки — зарядовое число $Z$\n$\\alpha$ сдвигает на две клетки назад, $\\beta$ на одну вперёд", size=11, color=INK)
    save(f, "decay-shift-rules-cells")


URANIUM_CHAIN = [
    ("U", 92, 238), ("Th", 90, 234), ("Pa", 91, 234), ("U", 92, 234), ("Th", 90, 230), ("Ra", 88, 226),
    ("Rn", 86, 222), ("Po", 84, 218), ("Pb", 82, 214), ("Bi", 83, 214), ("Po", 84, 214), ("Pb", 82, 210),
    ("Bi", 83, 210), ("Po", 84, 210), ("Pb", 82, 206),
]


def chain_steps():
    steps = []
    for (s1, z1, a1), (s2, z2, a2) in zip(URANIUM_CHAIN, URANIUM_CHAIN[1:]):
        if (a2 - a1, z2 - z1) == (-4, -2):
            steps.append("a")
        elif (a2 - a1, z2 - z1) == (0, 1):
            steps.append("b")
        else:
            raise AssertionError((s1, s2))
    return steps


@fig("decay-uranium-series-az")
def uranium_az():
    steps = chain_steps()
    assert steps.count("a") == 8 and steps.count("b") == 6
    f, ax = plt.subplots(figsize=(9.0, 8.2))
    ax.set_xlim(80.8, 93.2)
    ax.set_ylim(203, 241)
    ax.set_xlabel("Зарядовое число $Z$")
    ax.set_ylabel("Массовое число $A$")
    ax.set_xticks(range(82, 93, 1))
    ax.set_yticks(range(206, 239, 4))
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    for (s1, z1, a1), (s2, z2, a2), k in zip(URANIUM_CHAIN, URANIUM_CHAIN[1:], steps):
        arrow(ax, (z1, a1), (z2, a2), color=RED if k == "a" else BLUE, lw=1.8, ms=11, shrink=15)
    for s, z, a in URANIUM_CHAIN:
        node(ax, z, a, s, a)
    ax.plot([], [], color=RED, lw=2, label="$\\alpha$-распад: 8 раз")
    ax.plot([], [], color=BLUE, lw=2, label="$\\beta$-распад: 6 раз")
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Семейство урана-238")
    save(f, "decay-uranium-series-az")


@fig("decay-uranium-series-nz")
def uranium_nz():
    steps = chain_steps()
    f, ax = plt.subplots(figsize=(9.0, 7.0))
    ax.set_xlim(121, 149)
    ax.set_ylim(80.8, 93.4)
    ax.set_xlabel("Число нейтронов $N$")
    ax.set_ylabel("Число протонов $Z$")
    ax.set_xticks(range(122, 149, 2))
    ax.set_yticks(range(82, 93, 1))
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    nz = [(a - z, z) for _, z, a in URANIUM_CHAIN]
    for (n1, z1), (n2, z2), k in zip(nz, nz[1:], steps):
        if k == "a":
            assert (n2 - n1, z2 - z1) == (-2, -2)
        else:
            assert (n2 - n1, z2 - z1) == (-1, 1)
        arrow(ax, (n1, z1), (n2, z2), color=RED if k == "a" else BLUE, lw=1.8, ms=11, shrink=9)
    for (s, z, a), (n, _) in zip(URANIUM_CHAIN, nz):
        node(ax, n, z, s, a)
    ax.plot([], [], color=RED, lw=2, label="$\\alpha$: $N-2$, $Z-2$")
    ax.plot([], [], color=BLUE, lw=2, label="$\\beta$: $N-1$, $Z+1$")
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Те же ядра в осях $N$ и $Z$")
    save(f, "decay-uranium-series-nz")


@fig("decay-four-families")
def families():
    fams = [
        ("Семейство урана", 92, 238, 82, 206, "U", "Pb", 2, RED),
        ("Семейство тория", 90, 232, 82, 208, "Th", "Pb", 0, BLUE),
        ("Семейство актиния", 92, 235, 82, 207, "U", "Pb", 3, GREEN),
        ("Семейство нептуния", 93, 237, 83, 209, "Np", "Bi", 1, VIOLET),
    ]
    f, ax = plt.subplots(figsize=(9.0, 6.6))
    ax.set_xlim(79.5, 96)
    ax.set_ylim(202, 242)
    ax.set_xlabel("Зарядовое число $Z$")
    ax.set_ylabel("Массовое число $A$")
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    # label offsets in data units: starts to the right, ends to the left, staggered
    off_start = {2: (1.0, 0.0), 0: (-1.0, 0.0), 3: (1.0, 0.0), 1: (1.0, 0.0)}
    off_end = {2: (-0.4, -1.5), 0: (-0.4, 1.3), 3: (-0.4, -0.1), 1: (0.4, -1.0)}
    for name, z0, a0, z1, a1, s0, s1, k, col in fams:
        assert a0 % 4 == k and a1 % 4 == k
        # the uranium line is bent so that it does not pass through the thorium-232 start point
        arrow(ax, (z0, a0), (z1, a1), color=col, lw=2.2, ms=13, shrink=4, rad=-0.12 if k == 2 else 0.0)
        ax.plot([z0, z1], [a0, a1], "o", ms=7, mfc=col, mec=col, zorder=6)
        dx, dy = off_start[k]
        ax.text(z0 + dx, a0 + dy, f"${{}}^{{{a0}}}$" + s0, ha="left" if dx > 0 else "right", va="center", fontsize=10.5, color=col)
        dx, dy = off_end[k]
        ax.text(z1 + dx, a1 + dy, f"${{}}^{{{a1}}}$" + s1, ha="left" if dx > 0 else "right", va="center", fontsize=10.5, color=col)
        ax.plot([], [], color=col, lw=2.4, label=f"{name}: $A=4n+{k}$")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_title("Четыре радиоактивных семейства")
    f.tight_layout()
    save(f, "decay-four-families")


# ---------------------------------------------------------------- halflife-


@fig("halflife-coin-experiment")
def coins():
    data = [128, 62, 26, 17, 6]
    ideal = [128 / 2**n for n in range(5)]
    assert ideal == [128, 64, 32, 16, 8]
    f, ax = plt.subplots(figsize=(7.2, 4.6))
    t = np.linspace(0, 4.4, 200)
    ax.plot(t, 128 / 2**t, color=GREY, lw=1.6, ls="--", label="$128/2^{n}$")
    ax.plot(range(5), data, "o-", color=RED, lw=2, ms=8, label="бросания монет")
    for n, v in enumerate(data):
        ax.annotate(str(v), (n, v), textcoords="offset points", xytext=(9, 7), fontsize=11, color=RED)
    ax.set_xlabel("Номер опыта")
    ax.set_ylabel("Число нераспавшихся монет $N$")
    ax.set_xticks(range(5))
    ax.set_ylim(0, 140)
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    ax.set_title("Монетная модель распада")
    f.tight_layout()
    save(f, "halflife-coin-experiment")


def decay_axes(ax, ytop=1.0):
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, ytop * 1.08)
    ax.set_xticks(range(6))
    ax.set_xticklabels(["0", "$T$", "$2T$", "$3T$", "$4T$", "$5T$"])
    ax.grid(color=GRID)
    ax.set_axisbelow(True)


@fig("halflife-decay-curve")
def decay_curve():
    f, ax = plt.subplots(figsize=(7.6, 4.8))
    decay_axes(ax)
    t = np.linspace(0, 5.2, 300)
    ax.plot(t, 2.0**-t, color=RED, lw=2.4)
    names = ["$N_0$", "$N_0/2$", "$N_0/4$", "$N_0/8$", "$N_0/16$"]
    ax.set_yticks([2.0**-k for k in range(5)])
    ax.set_yticklabels(names)
    for k in range(5):
        ax.plot([k], [2.0**-k], "o", color=RED, ms=7, zorder=5)
        ax.plot([k, k], [0, 2.0**-k], color=GREY, lw=1, ls=":")
        ax.plot([0, k], [2.0**-k, 2.0**-k], color=GREY, lw=1, ls=":")
    ax.set_xlabel("Время $t$")
    ax.set_ylabel("Число ядер $N$")
    ax.set_title("Кривая радиоактивного распада")
    ax.text(2.7, 0.62, "$N=\\dfrac{N_0}{2^{t/T}}$", fontsize=16, color=RED)
    f.tight_layout()
    save(f, "halflife-decay-curve")


@fig("halflife-activity-curve")
def activity_curve():
    f, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6))
    t = np.linspace(0, 5.2, 300)
    decay_axes(a1)
    a1.plot(t, 2.0**-t, color=RED, lw=2.4, label="образец из $N_0$ ядер")
    a1.plot(t, 0.5 * 2.0**-t, color=BLUE, lw=2.4, label="половина образца, $N_0/2$ ядер")
    assert abs(0.5 * 2.0**-2 - 0.125) < 1e-12
    a1.set_yticks([0, 0.5, 1.0])
    a1.set_yticklabels(["0", "$A_0/2$", "$A_0$"])
    a1.set_xlabel("Время $t$")
    a1.set_ylabel("Активность $A=\\lambda N$")
    a1.set_title("Одно вещество, разное число ядер")
    a1.legend(frameon=False, loc="upper right", fontsize=9.5)
    # different nuclides, same N0
    t2 = np.linspace(0, 10, 300)
    a2.set_xlim(0, 10)
    a2.set_ylim(0, 1.08)
    a2.plot(t2, 2.0 ** (-t2 / 1.0), color=RED, lw=2.4, label="короткий период $T_1$")
    a2.plot(t2, 2.0 ** (-t2 / 5.0), color=BLUE, lw=2.4, label="длинный период $T_2=5T_1$")
    a2.set_xticks([0, 1, 5, 10])
    a2.set_xticklabels(["0", "$T_1$", "$T_2$", "$10T_1$"])
    a2.set_yticks([0, 0.5, 1.0])
    a2.set_yticklabels(["0", "$N_0/2$", "$N_0$"])
    a2.grid(color=GRID)
    a2.set_axisbelow(True)
    a2.set_xlabel("Время $t$")
    a2.set_ylabel("Число ядер $N$")
    a2.set_title("Одинаковое $N_0$, разные периоды")
    a2.legend(frameon=False, loc="upper right", fontsize=9.5)
    f.tight_layout()
    save(f, "halflife-activity-curve")


@fig("halflife-examples-log")
def examples_log():
    year = 365.25 * 24 * 3600
    rows = [
        ("Радон ${}^{220}_{86}\\mathrm{Rn}$", 60.0, "около 1 мин"),
        ("Радий ${}^{226}_{88}\\mathrm{Ra}$", 1600 * year, "1600 лет"),
        ("Углерод ${}^{14}_{6}\\mathrm{C}$", 5570 * year, "5570 лет"),
        ("Уран ${}^{238}_{92}\\mathrm{U}$", 4.5e9 * year, "4,5 млрд лет"),
    ]
    f, ax = plt.subplots(figsize=(8.0, 3.8))
    ax.barh([r[0] for r in rows], [r[1] for r in rows], color=[RED, GOLD, GREEN, BLUE], height=0.6)
    ax.set_xscale("log")
    ax.set_xlim(10, 3e18)
    ax.set_xlabel("Период полураспада $T$, с (логарифмическая шкала)")
    for i, r in enumerate(rows):
        ax.text(r[1] * 1.6, i, r[2], va="center", fontsize=11)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Периоды полураспада: от минут до миллиардов лет")
    ratio = 4.5e9 * year / 60.0
    assert 15 < math.log10(ratio) < 16.5
    f.tight_layout()
    save(f, "halflife-examples-log")


@fig("halflife-lambda-vs-T")
def lam_vs_T():
    year = 365.25 * 24 * 3600
    pts = [
        ("${}^{220}$Rn", 60.0),
        ("${}^{226}$Ra", 1600 * year),
        ("${}^{14}$C", 5570 * year),
        ("${}^{238}$U", 4.5e9 * year),
    ]
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    T = np.logspace(1, 18, 100)
    ax.loglog(T, 0.69 / T, color=GREY, lw=1.8, label="$\\lambda\\approx 0{,}69/T$")
    shifts = {"${}^{226}$Ra": (-46, 10), "${}^{14}$C": (10, -2)}
    for name, t in pts:
        ax.plot([t], [0.69 / t], "o", ms=8, color=RED)
        ax.annotate(name, (t, 0.69 / t), textcoords="offset points", xytext=shifts.get(name, (8, 6)), fontsize=11)
    ax.set_xlabel("Период полураспада $T$, с")
    ax.set_ylabel("Постоянная распада $\\lambda$, с$^{-1}$")
    ax.grid(color=GRID, which="major")
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    ax.set_title("Чем больше период, тем меньше постоянная распада")
    f.tight_layout()
    save(f, "halflife-lambda-vs-T")


@fig("halflife-carbon-dating")
def carbon():
    T = 5570.0
    f, ax = plt.subplots(figsize=(7.8, 4.6))
    age = np.linspace(0, 60000, 400)
    ax.plot(age / 1000, 2.0 ** (-age / T), color=GREEN, lw=2.4)
    ax.axvspan(1, 50, color=GOLD, alpha=0.18, lw=0)
    ax.text(25.5, 0.78, "метод даёт возраст\nот 1000 до 50 000 лет", ha="center", fontsize=11, color=INK)
    for k in range(1, 5):
        ax.plot([k * T / 1000], [2.0**-k], "o", color=GREEN, ms=7)
        ax.annotate(f"$1/{2**k}$", (k * T / 1000, 2.0**-k), textcoords="offset points", xytext=(8, 7), fontsize=10.5)
    frac = 2.0 ** (-50000 / T)
    assert 0.0019 < frac < 0.0021
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Возраст древесины, тыс. лет")
    ax.set_ylabel("Доля радиоуглерода ${}^{14}$C от исходной")
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Радиоуглеродная датировка, $T=5570$ лет")
    ru_axis(ax)
    f.tight_layout()
    save(f, "halflife-carbon-dating")


if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
        print("ok", n)
