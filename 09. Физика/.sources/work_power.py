"""Figures for the notes "Механическая работа" and "Мощность" (course Физика 7-9, lessons 71-77).

Run: python3 work_power.py
PNG files go to content/08. Работа, мощность, простые механизмы/00. Вложения/, prefixes work-*, power-*
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "08. Работа, мощность, простые механизмы"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, saver, tint

GRID = ASH
GREY = MUTED
FORCE = RED
GOLD = WARM
WOOD = tint(COPPER, 0.55)
WATER = tint(SKY, 0.7)
ORANGE = COPPER  # a warm accent that stays readable as a thin line or text on white
PURPLE = VIOLET

F_TR = r"F_\mathrm{тр}"
F_TYAZH = r"F_\mathrm{тяж}"


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def blank_row(n, w, h, xlim, ylim):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    for ax in np.atleast_1d(axes):
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def lab(ax, x, y, text, color=INK, fs=12, ha="center", va="center", **kw):
    ax.text(x, y, text, color=color, fontsize=fs, ha=ha, va=va, **kw)


def dot(ax, x, y, color=INK, r=0.06):
    ax.add_patch(Circle((x, y), r, fc=color, ec=color, zorder=6))


def ground(ax, x0, x1, y, h=0.16):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.6, zorder=2)
    for x in np.linspace(x0 + 0.1, x1, int((x1 - x0) / 0.35)):
        ax.plot([x, x - 0.16], [y, y - h], color=GREY, lw=1)


def block(ax, x, y, w=1.8, h=0.9, face=WOOD, z=3):
    ax.add_patch(Rectangle((x, y), w, h, fc=face, ec=INK, lw=1.5, zorder=z))


def dim_bar(ax, p, q, text, off=(0, 0.25), fs=10.5, color=INK):
    arrow(ax, p, q, color=color, lw=1.2, style="<|-|>", scale=9)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="center", fontsize=fs, color=color)


def ball(ax, x, y, r=0.35, face=GOLD):
    ax.add_patch(Circle((x, y), r, fc=face, ec=INK, lw=1.5, zorder=4))


def scale_labels(ax, pts):
    """Points on a log axis with labels above (y > 0) or below (y < 0) the axis, each with an own alignment."""
    for x, txt, y, col, ha in pts:
        ax.plot([x, x], [0, y - 0.1 if y > 0 else y + 0.1], color=col, lw=1, ls=":")
        ax.plot([x], [0], "o", color=col, ms=7, zorder=5)
        ax.text(x, y, txt, ha=ha, va="bottom" if y > 0 else "top", fontsize=9.6, color=col)


# ------------------------------------------------------------------ work

def work_three_situations():
    fig, axes = blank_row(3, 12.5, 3.9, (-2.3, 2.3), (-0.6, 3.6))
    ax = axes[0]
    ax.plot([-0.9, 0.9], [3.2, 3.2], color=INK, lw=3)
    ax.plot([0, 0], [3.2, 1.55], color=INK, lw=1.2)
    ball(ax, 0, 1.2)
    arrow(ax, (0.55, 1.2), (0.55, 2.3), color=FORCE, lw=2.4)
    lab(ax, 0.9, 1.75, r"$\vec F$", FORCE, 14)
    lab(ax, 0, 0.2, "Сила есть, перемещения нет", INK, 11)
    lab(ax, 0, -0.35, r"$A = 0$", INK, 14, weight="bold")
    ax = axes[1]
    ball(ax, -1.5, 1.6, face=tint(WARM, 0.7))
    ball(ax, 1.5, 1.6)
    ax.plot([-1.5], [1.6], "o", color=GREY, ms=0)
    arrow(ax, (-1.05, 1.6), (1.05, 1.6), color=BLUE, lw=2.2, ls="--")
    lab(ax, 0, 2.05, r"$s$", BLUE, 14)
    lab(ax, 0, 0.9, "сил нет: $\\vec F = 0$", INK, 11)
    lab(ax, 0, 0.2, "Перемещение есть, силы нет", INK, 11)
    lab(ax, 0, -0.35, r"$A = 0$", INK, 14, weight="bold")
    ax = axes[2]
    ax.plot([-0.9, 0.9], [3.4, 3.4], color=INK, lw=3)
    ball(ax, -0.5, 0.7, face=tint(WARM, 0.7))
    ball(ax, -0.5, 2.2)
    ax.plot([-0.5, -0.5], [1.05, 3.4], color=INK, lw=1.2, zorder=1)
    arrow(ax, (0.0, 2.2), (0.0, 2.95), color=FORCE, lw=2.4)
    lab(ax, 0.32, 2.6, r"$\vec F$", FORCE, 14)
    dim_bar(ax, (-1.35, 0.7), (-1.35, 2.2), r"$s$", off=(-0.3, 0), color=BLUE)
    lab(ax, 0, 0.0, "Сила и перемещение вдоль неё", INK, 11)
    lab(ax, 0, -0.5, r"$A = F\,s$", FORCE, 14, weight="bold")
    save(fig, "work-three-situations.png")


def work_area_rectangle():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.add_patch(Rectangle((0, 0), 0.5, 2, fc=BLUE, alpha=0.35, ec=BLUE, lw=1.8))
    ax.add_patch(Rectangle((0, 0), 0.5, 4, fc="none", ec=FORCE, lw=1.6, ls="--"))
    ax.add_patch(Rectangle((0, 0), 1.0, 2, fc="none", ec=GREEN, lw=1.6, ls="--"))
    ax.text(0.25, 1.0, "$A = 2\\cdot 0{,}5$\n$= 1$ Дж", ha="center", va="center", fontsize=11.5, color=INK)
    ax.text(0.25, 3.0, "сила вдвое:\n$2$ Дж", ha="center", va="center", fontsize=10.5, color=FORCE)
    ax.text(0.75, 1.0, "путь вдвое:\n$2$ Дж", ha="center", va="center", fontsize=10.5, color=GREEN)
    ax.set(xlim=(0, 1.2), ylim=(0, 4.6), xlabel="перемещение $s$, м", ylabel="сила $F$, Н")
    ax.set_title("Работа постоянной силы — площадь прямоугольника под графиком $F(s)$", fontsize=11.5)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "work-area-rectangle.png")


def _mover(ax, x, y, w=1.8, h=0.9):
    ground(ax, x - 1.0, x + w + 1.4, y)
    block(ax, x, y, w, h)


def work_sign_cases():
    fig, axes = blank_row(3, 13, 3.6, (-0.5, 5.2), (-1.3, 2.9))
    specs = [
        ("Сила вдоль перемещения", r"$A = +F\,s > 0$", "тело разгоняется", GREEN),
        ("Сила против перемещения", r"$A = -F\,s < 0$", "тело тормозит", FORCE),
        ("Сила $\\perp$ перемещению", r"$A = 0$", "скорость по модулю не меняется", GREY),
    ]
    for ax, (t, a, c, col) in zip(axes, specs):
        _mover(ax, 1.4, 0.0)
        lab(ax, 2.6, 2.6, t, INK, 11.5, weight="bold")
        arrow(ax, (1.3, -0.55), (3.7, -0.55), color=BLUE, lw=2.0, ls="--")
        lab(ax, 2.5, -0.95, r"$\vec s$", BLUE, 13)
        lab(ax, 2.6, 2.0, a, col, 14, weight="bold")
        lab(ax, 2.6, 1.6, c, GREY, 9.5)
    arrow(axes[0], (3.2, 0.45), (4.7, 0.45), color=FORCE, lw=2.6)
    lab(axes[0], 4.2, 0.85, r"$\vec F$", FORCE, 14)
    arrow(axes[1], (1.4, 0.45), (0.0, 0.45), color=FORCE, lw=2.6)
    lab(axes[1], 0.5, 0.85, r"$\vec F_\mathrm{тр}$", FORCE, 13)
    arrow(axes[2], (2.3, 0.45), (2.3, -0.4), color=FORCE, lw=2.6, zorder=6)  # above the block, so its whole length shows
    lab(axes[2], 2.7, -0.3, r"$\vec F_\mathrm{тяж}$", FORCE, 12, ha="left")
    save(fig, "work-sign-cases.png")


def work_block_four_forces():
    fig, ax = blank(9.2, 4.6, (-1.2, 8.4), (-1.5, 3.7))
    ground(ax, -0.6, 4.8, 0.0)
    block(ax, 1.0, 0.0, 2.2, 1.0)
    dot(ax, 2.1, 0.5)
    arrow(ax, (3.2, 0.5), (4.6, 0.5), color=FORCE, lw=2.8)
    lab(ax, 4.55, 0.95, r"$\vec F_\mathrm{пр}$", FORCE, 13)
    arrow(ax, (1.0, 0.25), (-0.3, 0.25), color=BLUE, lw=2.8)
    lab(ax, -0.05, 0.75, r"$\vec F_\mathrm{тр}$", BLUE, 13)
    arrow(ax, (2.1, 0.5), (2.1, -0.85), color=PURPLE, lw=2.6, zorder=6)  # above the block, so its whole length shows
    lab(ax, 2.55, -0.65, r"$\vec F_\mathrm{тяж}$", PURPLE, 12, ha="left")
    arrow(ax, (2.1, 1.0), (2.1, 2.4), color=GREEN, lw=2.6)
    lab(ax, 2.5, 2.2, r"$\vec N$", GREEN, 13, ha="left")
    arrow(ax, (0.8, -1.25), (3.4, -1.25), color=GREY, lw=1.6, ls="--")
    lab(ax, 2.1, -1.5, r"$\vec s$", GREY, 12)
    rows = [
        (r"$A_\mathrm{пр} = +F\,s > 0$", FORCE),
        (r"$A_\mathrm{тр} = -F_\mathrm{тр}\,s < 0$", BLUE),
        (r"$A_\mathrm{тяж} = 0$", PURPLE),
        (r"$A_N = 0$", GREEN),
        (r"$\sum A = 0$ при $F_\mathrm{тр} = F_\mathrm{пр}$", INK),
    ]
    for i, (txt, col) in enumerate(rows):
        lab(ax, 5.3, 3.2 - 0.62 * i, txt, col, 12.5, ha="left", weight="bold" if i == 4 else None)
    save(fig, "work-block-four-forces.png")


def work_zero_examples():
    fig, axes = blank_row(3, 13.2, 3.9, (-2.6, 2.6), (-1.5, 3.4))
    ax = axes[0]
    ground(ax, -2.2, 2.2, 0.0)
    ball(ax, -1.0, 0.35)
    ball(ax, 1.1, 0.35, face=tint(WARM, 0.7))
    arrow(ax, (-0.5, 0.35), (0.65, 0.35), color=BLUE, lw=2, ls="--")
    lab(ax, 0.1, 0.72, r"$\vec s$", BLUE, 13)
    arrow(ax, (-1.0, 0.7), (-1.0, 1.9), color=GREEN, lw=2.4)
    lab(ax, -0.62, 1.55, r"$\vec N$", GREEN, 12)
    arrow(ax, (-1.0, 0.0), (-1.0, -1.1), color=FORCE, lw=2.4)
    lab(ax, -0.55, -0.8, r"$\vec F_\mathrm{тяж}$", FORCE, 12)
    lab(ax, 0, 3.3, "Гладкий горизонтальный пол", INK, 11.5, weight="bold")
    lab(ax, 0, 2.85, r"угол $90^\circ$: $A = 0$", GREY, 11)
    ax = axes[1]
    cy = 0.5
    ax.add_patch(Circle((0, cy), 0.5, fc=GREEN, ec=INK, lw=1.4, alpha=0.55))
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(1.7 * np.cos(th), cy + 1.7 * np.sin(th), color=GREY, lw=1, ls=":")
    mx, my = 1.2, cy + 1.2
    ball(ax, mx, my, r=0.2, face=tint(WARM, 0.7))
    arrow(ax, (mx, my), (mx - 0.7, my - 0.7), color=FORCE, lw=2.4)
    lab(ax, mx - 1.15, my - 0.2, r"$\vec F_\mathrm{тяж}$", FORCE, 12)
    arrow(ax, (mx, my), (mx + 0.8, my - 0.8), color=BLUE, lw=2.4)
    lab(ax, mx + 0.85, my - 0.3, r"$\vec v$", BLUE, 13)
    lab(ax, 0, cy, "Земля", INK, 10)
    lab(ax, 0, 3.3, "Луна на круговой орбите", INK, 11.5, weight="bold")
    lab(ax, 0, 2.85, r"$\vec F_\mathrm{тяж} \perp \vec v$: $A = 0$", GREY, 11)
    ax = axes[2]
    ax.add_patch(Polygon([(-2.3, -0.2), (2.3, -0.2), (2.3, 2.2)], fc=LIGHT, ec=INK, lw=1.5))
    ang = np.arctan2(2.4, 4.6)
    t = np.array([np.cos(ang), np.sin(ang)])
    n = np.array([-np.sin(ang), np.cos(ang)])
    c = np.array([0.0, -0.2 + 2.4 * 2.3 / 4.6]) + 0.32 * n
    ball(ax, c[0], c[1], r=0.28)
    arrow(ax, tuple(c), tuple(c - 1.0 * t), color=BLUE, lw=2.2, ls="--")
    lab(ax, -1.75, 1.45, "вниз: $A > 0$\nразгон", GREEN, 10.5)
    arrow(ax, tuple(c), tuple(c + 1.0 * t), color=BLUE, lw=2.2, ls="--")
    lab(ax, 0.75, 2.25, "вверх: $A < 0$\nторможение", FORCE, 10.5)
    arrow(ax, tuple(c), (c[0], c[1] - 1.1), color=FORCE, lw=2.4)
    lab(ax, c[0] + 0.5, c[1] - 0.9, r"$\vec F_\mathrm{тяж}$", FORCE, 12)
    lab(ax, 0, 3.3, "Наклонная плоскость", INK, 11.5, weight="bold")
    lab(ax, 0, 2.85, "перемещение частично вдоль силы", GREY, 10)
    save(fig, "work-zero-examples.png")


def work_joule_scale():
    fig, ax = plt.subplots(figsize=(12.5, 4.6))
    ax.set_xscale("log")
    ax.set_xlim(3e-4, 4e7)
    ax.set_ylim(-3.2, 3.6)
    ax.axis("off")
    bands = [
        (1e-6, 1e-3, "мДж", PAPER),
        (1e-3, 1, "", LIGHT),
        (1, 1e3, "Дж", PAPER),
        (1e3, 1e6, "кДж", LIGHT),
        (1e6, 1e9, "МДж", PAPER),
    ]
    for lo, hi, name, col in bands:
        ax.add_patch(Rectangle((lo, -0.35), hi - lo, 0.7, fc=col, ec="none"))
    ax.plot([3e-4, 4e7], [0, 0], color=INK, lw=1.6)
    for e, name in ((-3, "1 мДж"), (0, "1 Дж"), (3, "1 кДж"), (6, "1 МДж")):
        ax.plot([10.0**e] * 2, [-0.35, 0.35], color=INK, lw=1.6)
        ax.text(10.0**e, -0.62, name, ha="center", va="top", fontsize=11, color=INK, weight="bold")
    pts = [
        (0.2, "пружина динамометра\n$0{,}2$ Дж", -1.5, BLUE, "right"),
        (0.5, "линейка встала\n$0{,}5$ Дж", 1.0, BLUE, "right"),
        (5, "гвоздь из доски\n$5$ Дж", -1.5, BLUE, "left"),
        (11, "книги на стул\n$11$ Дж", 1.0, BLUE, "left"),
        (8.4e4, "человек катит\nвагонетку $84$ кДж", -1.5, GREEN, "center"),
        (4.5e4, "камень со дна\n$45$ кДж", 1.0, GREEN, "right"),
        (9.52e4, "колонна со дна озера\n$95{,}2$ кДж", 1.0, GREEN, "left"),
        (9e6, "клеть из шахты\n$9$ МДж", -1.5, FORCE, "center"),
        (0.011, "часовой механизм:\nмДж", 2.4, GREY, "center"),
    ]
    scale_labels(ax, pts)
    ax.text(3e-4, -3.0, "гиря $1$ кг: на $10$ см — $1$ Дж, на $1$ м — $10$ Дж", ha="left", va="center", fontsize=10, color=INK)
    ax.set_title("Шкала работы: каждое деление в $10$ раз больше", fontsize=12, y=1.0)
    save(fig, "work-joule-scale.png")


def work_spring_triangle():
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    l = np.array([0, 10.0])
    ax.add_patch(Rectangle((0, 0), 10, 4, fc="none", ec=GREY, lw=1.4, ls="--"))
    ax.add_patch(Polygon([(0, 0), (10, 0), (10, 4)], fc=BLUE, alpha=0.35, ec="none"))
    ax.plot(l, 4 * l / 10, color=BLUE, lw=2.6)
    ax.plot([0, 10], [2, 2], color=ORANGE, lw=1.6, ls="-.")
    ax.plot([10], [4], "o", color=BLUE)
    ax.text(6.8, 1.0, "$A = \\dfrac{1}{2}Fl = 0{,}2$ Дж", ha="center", va="center", fontsize=12, color=INK)
    ax.text(3.0, 3.35, "$Fl = 0{,}4$ Дж, если бы\nсила была постоянной $4$ Н", ha="center", va="center", fontsize=10.5, color=GREY)
    ax.text(0.2, 2.15, "средняя сила $F/2 = 2$ Н", ha="left", va="bottom", fontsize=10.5, color=ORANGE)
    ax.text(9.7, 4.15, "$F = kl$", ha="right", va="bottom", fontsize=12, color=BLUE)
    ax.set(xlim=(0, 10.8), ylim=(0, 4.8), xlabel="удлинение пружины $l$, см", ylabel="сила упругости $F$, Н")
    ax.set_title("Работа переменной силы — площадь под графиком; $k = 40$ Н/м", fontsize=11.5)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "work-spring-triangle.png")


def work_nail():
    fig = plt.figure(figsize=(12.6, 4.6))
    ax = fig.add_axes([0.0, 0.05, 0.46, 0.9])
    ax.set_xlim(-20, 18)
    ax.set_ylim(-0.6, 8.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, -0.3), 5, 8.6, fc=WOOD, ec=INK, lw=1.5, hatch="///", zorder=1))
    lab(ax, 2.5, 8.55, "доска, $d = 5$ см", INK, 10.5, va="bottom")
    heads = [0.0, -10.0, -15.0]
    ys = [6.7, 3.9, 1.1]
    for h, y in zip(heads, ys):
        ax.add_patch(Rectangle((h - 0.6, y - 0.55), 0.6, 1.1, fc=INK, ec=INK, zorder=4))
        ax.add_patch(Rectangle((h, y - 0.13), 15, 0.26, fc=GREY, ec=INK, lw=1, zorder=4))
        arrow(ax, (h - 1.0, y), (h - 3.4, y), color=FORCE, lw=2.4)
    lab(ax, -4.6, ys[0] + 0.5, r"$\vec F$", FORCE, 13)
    lab(ax, 16.4, ys[0], "$l = 15$ см", INK, 10.5, ha="left")
    dim_bar(ax, (0.0, 5.35), (-10.0, 5.35), r"$l-d$: работа $A_1$", off=(0, 0.4), color=BLUE)
    dim_bar(ax, (-10.0, 2.5), (-15.0, 2.5), r"$d$: работа $A_2$", off=(0, 0.4), color=GREEN)
    ax2 = fig.add_axes([0.55, 0.14, 0.43, 0.74])
    s = np.array([0, 10, 15.0])
    f = np.array([40, 40, 0.0])
    ax2.fill_between([0, 10], 0, 40, color=BLUE, alpha=0.3)
    ax2.fill_between([10, 15], [40, 0], 0, color=GREEN, alpha=0.3)
    ax2.plot(s, f, color=INK, lw=2.4)
    ax2.text(5, 20, "$A_1 = F(l-d) = 4$ Дж", ha="center", fontsize=11, color=INK)
    ax2.text(12.3, 8, "$A_2 = \\dfrac{1}{2}Fd$\n$= 1$ Дж", ha="center", fontsize=10.5, color=INK)
    ax2.axvline(10, color=GREY, lw=1, ls=":")
    ax2.set(xlim=(0, 15.6), ylim=(0, 46), xlabel="сдвиг гвоздя $s$, см", ylabel="сила $F$, Н")
    ax2.set_title("$A = A_1 + A_2 = 5$ Дж", fontsize=12)
    ax2.grid(color=GRID)
    save(fig, "work-nail.png")


def work_ruler():
    fig, ax = blank(12.0, 4.4, (-0.6, 12.6), (-1.6, 4.6))
    ground(ax, -0.4, 11.4, 0.0)
    L = 3.0
    # state 1: lying
    ax.add_patch(Rectangle((0.2, 0.0), L, 0.14, fc=WOOD, ec=INK, lw=1.4, zorder=3))
    dot(ax, 0.2 + L / 2, 0.07, FORCE, 0.07)
    lab(ax, 0.2 + L / 2, -0.55, "лежит", INK, 11)
    # state 2: raised by L/2, horizontal
    ax.add_patch(Rectangle((4.0, L / 2), L, 0.14, fc="none", ec=GREY, lw=1.4, ls="--", zorder=3))
    dot(ax, 4.0 + L / 2, L / 2 + 0.07, FORCE, 0.07)
    arrow(ax, (4.0 + L / 2, 0.15), (4.0 + L / 2, L / 2 - 0.05), color=BLUE, lw=2.2)
    lab(ax, 4.0 + L / 2 + 0.25, L / 4 + 0.1, r"$L/2$", BLUE, 13, ha="left")
    lab(ax, 4.0 + L / 2, -0.55, "поднять центр тяжести:\n$A = mg\\cdot L/2$", INK, 11)
    # state 3: vertical
    ax.add_patch(Rectangle((9.9, 0.0), 0.14, L, fc=WOOD, ec=INK, lw=1.4, zorder=3))
    dot(ax, 9.97, L / 2, FORCE, 0.07)
    ax.add_patch(Rectangle((8.7, L / 2), L * 0.4, 0.14, fc="none", ec=GREY, lw=1.0, ls=":"))
    lab(ax, 9.97, -0.55, "повернуть, высота та же:\n$A = 0$", INK, 11)
    arrow(ax, (7.3, 1.9), (9.4, 1.9), color=GREY, lw=1.6, style="-|>")
    arrow(ax, (3.4, 0.9), (3.9, 0.9), color=GREY, lw=1.6, style="-|>")
    lab(ax, 5.5, 4.2, "Линейка $1$ м, $100$ г: $A = mgL/2 = 0{,}5$ Дж", INK, 12.5, weight="bold")
    lab(ax, 5.5, 3.65, "красная точка — центр тяжести", GREY, 10)
    save(fig, "work-ruler.png")


def work_lake_column():
    fig, ax = blank(7.6, 6.0, (-0.6, 7.6), (-0.6, 6.4))
    ax.add_patch(Rectangle((0, 0), 7.0, 5.0, fc=WATER, ec="none", zorder=0))
    ax.plot([0, 7.0], [5.0, 5.0], color=BLUE, lw=2)
    ax.plot([0, 7.0], [0, 0], color=INK, lw=2.4)
    ax.plot([-0.4, 7.4], [5.9, 5.9], color=INK, lw=3)
    ax.plot([2.6, 2.6], [1.6, 5.9], color=INK, lw=1.3)
    ax.add_patch(Rectangle((2.3, 1.0), 0.6, 1.6, fc=tint(METAL, 0.45), ec=INK, lw=1.5, zorder=3))
    ax.add_patch(Rectangle((2.3, 0.0), 0.6, 1.6, fc="none", ec=GREY, lw=1.3, ls="--", zorder=3))
    ax.add_patch(Rectangle((2.3, 3.4), 0.6, 1.6, fc="none", ec=GREY, lw=1.3, ls="--", zorder=3))
    ax.plot([2.6, 2.6], [1.6, 5.9], color=INK, lw=1.3, zorder=2)
    # Marble 2700 kg/m3 in water 1000: F_А / F_тяж = 0.37, F = 0.63 F_тяж; F_тяж length 1.1
    arrow(ax, (3.4, 1.8), (3.4, 2.49), color=FORCE, lw=2.6)
    lab(ax, 3.75, 2.2, r"$\vec F$", FORCE, 13, ha="left")
    arrow(ax, (2.0, 1.8), (2.0, 0.7), color=INK, lw=2.6)
    lab(ax, 1.15, 1.2, r"$\vec F_\mathrm{тяж}$", INK, 12)
    arrow(ax, (2.0, 1.8), (2.0, 2.21), color=BLUE, lw=2.6)
    lab(ax, 1.15, 2.1, r"$\vec F_\mathrm{А}$", BLUE, 12)
    dim_bar(ax, (6.6, 0.0), (6.6, 5.0), r"$h$", off=(0.35, 0), color=INK)
    lab(ax, 0.2, 5.5, "поверхность озера", INK, 10, ha="left")
    lab(ax, 0.2, 0.3, "дно", INK, 10, ha="left")
    lab(ax, 4.0, 0.9, "$F + F_\\mathrm{А} = F_\\mathrm{тяж}$", INK, 11.5, ha="left")
    lab(ax, 4.0, 0.4, "подъём равномерный", GREY, 9, ha="left")
    save(fig, "work-lake-column.png")


def work_stone_vs_density():
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    rho = np.linspace(500, 8000, 300)
    a = (rho - 1000) * 10 * 0.6 * 5 / 1000
    ax.plot(rho[rho >= 1000], a[rho >= 1000], color=BLUE, lw=2.6)
    ax.plot(rho[rho <= 1000], a[rho <= 1000], color=GREY, lw=1.8, ls="--")
    ax.axhline(0, color=INK, lw=1)
    for x, name, dy in ((1000, "$\\rho_\\mathrm{в}$: $A = 0$", 30), (2500, "камень $2500$: $45$ кДж", 12), (7800, "сталь $7800$: $204$ кДж", -22)):
        y = (x - 1000) * 30 / 1000
        ax.plot([x], [y], "o", color=FORCE, zorder=5)
        ax.annotate(name, (x, y), (x + (300 if x < 7000 else -3200), y + dy), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(560, -44, "формула даёт $A < 0$:\nтело всплыло бы само", ha="left", fontsize=9.5, color=GREY)
    ax.set(xlim=(500, 8300), ylim=(-50, 230), xlabel=r"плотность тела $\rho$, кг/м$^3$", ylabel="работа $A$, кДж")
    ax.set_title("Подъём тела объёмом $0{,}6$ м$^3$ с глубины $5$ м: $A = (\\rho-\\rho_\\mathrm{в})gVh$", fontsize=11)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "work-stone-vs-density.png")


def _piston(ax, x0, title, sub, big=False):
    w = 2.6 if big else 1.6
    ax.add_patch(Rectangle((x0, 0.3), 3.6, w, fc=WATER if big else LIGHT, ec=INK, lw=1.6, zorder=1))
    ax.add_patch(Rectangle((x0 + 1.5, 0.3), 0.25, w, fc=GREY, ec=INK, lw=1.4, zorder=3))
    arrow(ax, (x0 + 0.1, 0.3 + w / 2), (x0 + 1.45, 0.3 + w / 2), color=FORCE, lw=2.8)
    lab(ax, x0 + 0.8, 0.3 + w / 2 + 0.35, r"$\vec F$", FORCE, 13)
    ax.add_patch(Rectangle((x0 + 1.75, 0.3), 1.7, w, fc="none", ec="none"))
    dim_bar(ax, (x0 + 1.05, -0.2), (x0 + 1.75 + 0.02, -0.2), "", color=BLUE)
    lab(ax, x0 + 1.4, -0.65, r"ход $h$", BLUE, 11.5)
    lab(ax, x0 + 2.65, 0.3 + w / 2, r"$p$", BLUE, 15)
    lab(ax, x0 + 1.9, 0.3 + w + 0.4, r"площадь $S$", INK, 11)
    lab(ax, x0 + 1.8, 3.65, title, INK, 11.5, weight="bold")
    lab(ax, x0 + 1.8, -1.35, sub, INK, 11)


def work_piston_pressure():
    fig, axes = blank_row(2, 12.4, 4.5, (-0.4, 4.4), (-1.9, 4.0))
    _piston(axes[0], 0.0, "Насос: $A = 80$ Дж, $h = 40$ см", r"$p = \dfrac{A}{hS} = 0{,}1$ МПа при $S = 20$ см$^2$")
    _piston(axes[1], 0.0, "Пресс: $A = 80$ кДж, $h = 2$ см", r"$p = \dfrac{A}{hS} = 10$ МПа при $S = 4000$ см$^2$", big=True)
    save(fig, "work-piston-pressure.png")


# ------------------------------------------------------------------ power

def power_work_time_lines():
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    t = np.linspace(0, 6.2, 50)
    ax.plot(t, 2.0 * t, color=BLUE, lw=2.6, label="Тая: $N = \\dfrac{11}{5{,}51} \\approx 2$ Вт")
    ax.plot(t, 27.5 * t, color=FORCE, lw=2.6, label="Саша: $N = \\dfrac{11}{0{,}40} = 27{,}5$ Вт")
    ax.axhline(11, color=GREY, ls="--", lw=1.2)
    ax.plot([5.51], [11], "o", color=BLUE, zorder=5)
    ax.plot([0.40], [11], "o", color=FORCE, zorder=5)
    ax.text(0.9, 11.4, "одна и та же работа $11$ Дж", ha="left", fontsize=10.5, color=GREY)
    ax.text(0.9, 7.0, "наклон прямой — мощность", ha="left", fontsize=10.5, color=INK, rotation=0)
    ax.set(xlim=(0, 6.3), ylim=(0, 14), xlabel="время $t$, с", ylabel="совершённая работа $A$, Дж")
    ax.set_title("Одна работа за разное время: у кого круче, тот мощнее", fontsize=11.5)
    ax.legend(frameon=False, loc="upper right", fontsize=10.5, bbox_to_anchor=(1.0, 0.55))
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "power-work-time-lines.png")


def power_scale():
    fig, ax = plt.subplots(figsize=(13.4, 5.6))
    ax.set_xscale("log")
    ax.set_xlim(3e-4, 5e10)
    ax.set_ylim(-3.6, 4.2)
    ax.axis("off")
    bands = [(1e-6, 1e-3, PAPER), (1e-3, 1, LIGHT), (1, 1e3, PAPER), (1e3, 1e6, LIGHT), (1e6, 1e9, PAPER), (1e9, 1e12, LIGHT)]
    for lo, hi, col in bands:
        ax.add_patch(Rectangle((lo, -0.35), hi - lo, 0.7, fc=col, ec="none"))
    ax.plot([3e-4, 5e10], [0, 0], color=INK, lw=1.6)
    for e, name in ((-3, "1 мВт"), (0, "1 Вт"), (3, "1 кВт"), (6, "1 МВт"), (9, "1 ГВт")):
        ax.plot([10.0**e] * 2, [-0.35, 0.35], color=INK, lw=1.6)
        ax.text(10.0**e, -0.62, name, ha="center", va="top", fontsize=11, color=INK, weight="bold")
    pts = [
        (2.0, "Тая, книги на стул\n$2$ Вт", 1.0, BLUE, "right"),
        (5.0, "сердце при нагрузке\n$5$ Вт", -1.5, BLUE, "right"),
        (27.5, "Саша, те же книги\n$27{,}5$ Вт", 2.4, BLUE, "right"),
        (32, "строитель, кирпичи\n$32$ Вт", -1.5, BLUE, "left"),
        (60, "насос из колодца\n$\\geq 60$ Вт", 1.0, BLUE, "left"),
        (736, "$1$ л.с. $= 736$ Вт", -2.9, ORANGE, "center"),
        (800, "спортсмен на канате\n$800$ Вт", 2.4, BLUE, "left"),
        (1.5e6, "локомотив\n$1{,}5$ МВт", 2.4, GREEN, "center"),
        (1.84e7, "скоростной поезд\n$18{,}4$ МВт", 1.0, GREEN, "center"),
        (3.24e7, "атомный ледокол\n$32{,}4$ МВт", -1.5, GREEN, "center"),
        (1e9, "энергоблок АЭС $\\approx 1$ ГВт\n(не из лекции)", 2.4, GREY, "center"),
        (0.011, "часовой механизм:\nмилливатты", 2.4, GREY, "center"),
    ]
    scale_labels(ax, pts)
    ax.plot([1e9], [0], "o", mfc=PAPER, mec=GREY, ms=9, zorder=6)
    ax.set_ylim(-4.3, 3.9)
    ax.set_title("Шкала мощности: от часов до ледокола, каждое деление в $10$ раз больше", fontsize=12, y=1.0)
    save(fig, "power-scale.png")


def power_horsepower():
    fig, ax = blank(7.6, 5.2, (-1.0, 8.6), (-1.6, 5.6))
    ax.plot([2.4, 5.6], [5.1, 5.1], color=INK, lw=3)
    ax.plot([4.0, 4.0], [5.1, 4.8], color=INK, lw=2)
    ax.add_patch(Circle((4.0, 4.4), 0.42, fc=PAPER, ec=INK, lw=2, zorder=3))
    dot(ax, 4.0, 4.4)
    ax.plot([3.58, 3.58], [4.4, 1.9], color=INK, lw=1.6, zorder=2)
    ax.plot([4.42, 4.42], [4.4, 2.2], color=INK, lw=1.6, zorder=2)
    ax.add_patch(Rectangle((3.05, 0.9), 1.05, 1.0, fc=tint(METAL, 0.45), ec=INK, lw=1.6, zorder=3))
    lab(ax, 3.575, 1.4, "$75$ кг", INK, 10.5)
    ax.add_patch(Rectangle((3.05, -0.1), 1.05, 1.0, fc="none", ec=GREY, lw=1.3, ls="--", zorder=3))
    dim_bar(ax, (2.55, -0.1), (2.55, 0.9), r"$h = 1$ м", off=(-0.75, 0), color=BLUE)
    arrow(ax, (4.42, 2.4), (4.42, 1.2), color=FORCE, lw=2.6)
    lab(ax, 4.85, 1.8, r"$\vec F$", FORCE, 13, ha="left")
    lab(ax, 6.4, 3.2, "равномерно,\nза $t = 1$ с", INK, 12)
    lab(ax, 6.6, 1.0, r"$N = \dfrac{mgh}{t} \approx 736$ Вт", INK, 12.5, weight="bold")
    lab(ax, 6.6, 0.15, "$= 1$ л.с.", ORANGE, 13, weight="bold")
    lab(ax, 3.6, -1.15, "$g = 9{,}81$ Н/кг", GREY, 10.5)
    save(fig, "power-horsepower.png")


def power_force_speed():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6))
    ax = axes[0]
    v = np.linspace(3.5, 40, 300)
    ax.plot(v, 1500 / v, color=GREEN, lw=2.6)
    ax.add_patch(Rectangle((0, 0), 15, 100, fc=GREEN, alpha=0.3, ec=GREEN, lw=1.4))
    ax.plot([15], [100], "o", color=GREEN, zorder=5)
    ax.text(7.5, 50, "$Fv = 1{,}5$ МВт", ha="center", va="center", fontsize=10.5, color=INK)
    ax.text(21, 320, "$N = 1{,}5$ МВт постоянна:\nбольше скорость — меньше сила", fontsize=10.5, color=INK)
    ax.annotate("локомотив: $F = 100$ кН,\n$v = 15$ м/с", (15, 100), (22, 230), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set(xlim=(0, 40), ylim=(0, 400), xlabel="скорость $v$, м/с", ylabel="сила тяги $F$, кН")
    ax.set_title("$N = Fv$: площадь прямоугольника — мощность", fontsize=11.5)
    ax.grid(color=GRID)
    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 159.7, 115.2, fc=BLUE, alpha=0.3, ec=BLUE, lw=1.4))
    ax.plot([159.7], [115.2], "o", color=BLUE, zorder=5)
    ax.text(80, 58, "$115{,}2 \\cdot 159{,}7 \\approx 18{,}4$ МВт", ha="center", va="center", fontsize=11, color=INK)
    ax.annotate("скоростной поезд: $F_\\mathrm{сопр} = 115{,}2$ кН,\n$v = 575$ км/ч $= 159{,}7$ м/с", (159.7, 115.2), (20, 135), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set(xlim=(0, 200), ylim=(0, 170), xlabel="скорость $v$, м/с", ylabel="сила тяги $F$, кН")
    ax.set_title("Скорость: $575 / 3{,}6 \\approx 159{,}7$ м/с", fontsize=11.5)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "power-force-speed.png")


def power_heart_steps():
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    beats = np.arange(0, 6)
    step = 60 / 150
    t = beats * step
    a = beats * 2
    ax.step(t, a, where="post", color=FORCE, lw=2.4, label="$2$ Дж за каждое сокращение")
    tt = np.linspace(0, 5 * step + 0.4, 10)
    ax.plot(tt, 5 * tt, color=BLUE, lw=2, ls="--", label="средняя мощность $N = 5$ Вт")
    ax.set(xlim=(0, 2.4), ylim=(0, 13), xlabel="время $t$, с", ylabel="работа сердца $A$, Дж")
    ax.set_title("Сердце: $150$ сокращений в минуту, $N = A_1 n / t = 5$ Вт", fontsize=11.5)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "power-heart-steps.png")


def power_center_of_gravity():
    fig, axes = blank_row(2, 12.4, 5.6, (-0.6, 6.2), (-1.5, 5.9))
    ax = axes[0]
    a, h = 4.0, 3.0
    x0 = 1.0
    ax.add_patch(Rectangle((x0, 0), a, h, fc=WATER, ec="none"))
    ax.add_patch(Rectangle((x0, 0), a, a, fc="none", ec=INK, lw=2.4))
    dot(ax, x0 + a / 2, h / 2, FORCE, 0.09)
    lab(ax, x0 + a / 2 + 0.2, h / 2, "центр тяжести\nводы", FORCE, 9.5, ha="left")
    arrow(ax, (x0 + a / 2, h / 2), (x0 + a / 2, a), color=BLUE, lw=2.4)
    lab(ax, x0 + a / 2 - 0.25, (h / 2 + a) / 2, r"$a-\dfrac{h}{2}$", BLUE, 12, ha="right")
    dim_bar(ax, (x0 - 0.35, 0), (x0 - 0.35, h), r"$h$", off=(-0.3, 0), color=INK)
    dim_bar(ax, (x0 + a + 0.4, 0), (x0 + a + 0.4, a), r"$a$", off=(0.3, 0), color=INK)
    ax.add_patch(Rectangle((x0 + a - 0.7, a + 0.05), 0.7, 0.45, fc=GREY, ec=INK, lw=1.4))
    lab(ax, x0 + a - 0.35, a + 0.7, "насос", INK, 10.5)
    lab(ax, 2.6, 5.5, "Подвал-куб: $A = \\rho a^2 h\\,g\\left(a-\\dfrac{h}{2}\\right)$", INK, 11, weight="bold")
    lab(ax, 2.6, -0.7,"$t = A/N = 1200$ с $= 20$ мин", INK, 11.5)
    ax = axes[1]
    L = 4.4
    ax.add_patch(Circle((3.0, 4.45), 0.4, fc=PAPER, ec=INK, lw=2, zorder=3))
    lab(ax, 3.0, 4.45, "ворот", INK, 8)
    ax.plot([3.0, 3.0], [4.05, 4.05 - L], color=INK, lw=3.4)
    dot(ax, 3.0, 4.05 - L / 2, FORCE, 0.1)
    lab(ax, 3.3, 4.05 - L / 2, "центр тяжести цепи", FORCE, 9.5, ha="left")
    dim_bar(ax, (2.4, 4.05), (2.4, 4.05 - L), r"$L = 20$ м", off=(-0.75, 0), color=INK)
    arrow(ax, (3.9, 4.05 - L / 2), (3.9, 4.05), color=BLUE, lw=2.4)  # the centre of gravity rises by L/2
    lab(ax, 4.15, 4.05 - L / 4, r"$\dfrac{L}{2}$", BLUE, 12, ha="left")
    lab(ax, 3.0, 5.5, "Цепь на вороте: $A = \\dfrac{mgL}{2}$", INK, 11, weight="bold")
    lab(ax, 3.0, -1.0,"$t = \\dfrac{mgL}{2N} = 50$ с", INK, 11.5)
    save(fig, "power-center-of-gravity.png")


def power_traction_scheme():
    fig, ax = blank(9.2, 4.0, (-1.0, 8.6), (-1.3, 3.2))
    ground(ax, -0.6, 8.2, 0.0)
    ax.add_patch(Rectangle((1.2, 0.25), 5.4, 1.1, fc=LIGHT, ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Polygon([(6.6, 0.25), (7.5, 0.25), (7.5, 1.0), (7.1, 1.35), (6.6, 1.35)], fc=tint(SKY, 0.8), ec=INK, lw=1.6, zorder=3))
    for cx in (1.7, 2.6, 3.9, 5.2, 6.3, 7.1):
        ax.add_patch(Circle((cx, 0.2), 0.2, fc=PAPER, ec=INK, lw=1.3, zorder=4))
    dot(ax, 4.0, 0.8)
    arrow(ax, (4.0, 0.8), (6.2, 0.8), color=FORCE, lw=2.8, zorder=6)
    lab(ax, 5.4, 1.15, r"$\vec F_\mathrm{тяги}$", FORCE, 12.5)
    arrow(ax, (4.0, 0.8), (1.8, 0.8), color=BLUE, lw=2.8, zorder=6)
    lab(ax, 2.6, 1.15, r"$\vec F_\mathrm{сопр}$", BLUE, 12.5)
    arrow(ax, (4.0, 1.35), (4.0, 2.5), color=GREEN, lw=2.4)
    lab(ax, 4.4, 2.3, r"$\vec F_\mathrm{упр}$", GREEN, 12, ha="left")  # not N: that letter is the power here
    arrow(ax, (4.0, 0.8), (4.0, -0.35), color=PURPLE, lw=2.4, zorder=6)  # same length as the reaction force
    lab(ax, 4.4, -0.42, r"$\vec F_\mathrm{тяж}$", PURPLE, 12, ha="left")
    arrow(ax, (7.7, 0.7), (8.4, 0.7), color=INK, lw=2.0)
    lab(ax, 8.0, 1.05, r"$\vec v$", INK, 13)
    lab(ax, 4.0, -0.75, r"$v = \mathrm{const}$: $F_\mathrm{тяги} = F_\mathrm{сопр}$, $N = F\,v$", INK, 12.5, weight="bold")
    save(fig, "power-traction-scheme.png")


def power_pump_well():
    fig, ax = blank(7.4, 6.2, (-0.6, 7.4), (-4.9, 4.9))
    ground(ax, -0.4, 7.2, 0.0)
    ax.add_patch(Rectangle((0.6, -3.5), 2.0, 3.5, fc=tint(WARM, 0.9), ec=INK, lw=1.6, zorder=1))
    ax.add_patch(Rectangle((0.6, -4.6), 2.0, 1.1, fc=WATER, ec=INK, lw=1.6, zorder=2))
    ax.plot([0.6, 2.6], [-3.5, -3.5], color=BLUE, lw=2, zorder=3)
    ax.add_patch(Circle((1.6, -3.5), 0.22, fc=GREY, ec=INK, lw=1.4, zorder=5))
    lab(ax, 1.9, -3.1, "насос", INK, 9, ha="left")
    ax.plot([1.6, 1.6, 5.0], [-3.3, 2.8, 2.8], color=INK, lw=2.2, zorder=4)
    ax.add_patch(Rectangle((4.4, 2.5), 2.2, 1.6, fc=LIGHT, ec=INK, lw=1.6, zorder=2))
    ax.add_patch(Rectangle((4.4, 2.5), 2.2, 0.9, fc=WATER, ec="none", zorder=3))
    lab(ax, 5.5, 3.7, "бак", INK, 10)
    dim_bar(ax, (3.15, -3.5), (3.15, 0.0), r"$H = 3{,}5$ м", off=(0.05, 0), color=BLUE)
    dim_bar(ax, (3.9, 0.0), (3.9, 2.5), r"$h = 2{,}5$ м", off=(0.05, 0), color=GREEN)
    lab(ax, 3.2, 4.65, r"$p = \rho g (H+h) = 60$ кПа", INK, 11, weight="bold")
    lab(ax, 3.2, -4.4, r"$N = \dfrac{\rho V g (H+h)}{t} = 60$ Вт", INK, 11, weight="bold", ha="left")
    lab(ax, 3.4, -5.05, "$V = 60$ л за $t = 1$ мин", GREY, 10, ha="left")
    save(fig, "power-pump-well.png")


def main():
    for f in (
        work_three_situations,
        work_area_rectangle,
        work_sign_cases,
        work_block_four_forces,
        work_zero_examples,
        work_joule_scale,
        work_spring_triangle,
        work_nail,
        work_ruler,
        work_lake_column,
        work_stone_vs_density,
        work_piston_pressure,
        power_work_time_lines,
        power_scale,
        power_horsepower,
        power_force_speed,
        power_heart_steps,
        power_center_of_gravity,
        power_traction_scheme,
        power_pump_well,
    ):
        f()


if __name__ == "__main__":
    main()
