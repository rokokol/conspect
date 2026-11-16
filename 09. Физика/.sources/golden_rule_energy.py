"""Figures of section f08 "Золотое правило механики. КПД" and "Механическая энергия" (lessons 84-86).

Run: python3 golden_rule_energy.py
PNG files with prefixes golden-, efficiency- and energy- go to
content/08. Работа, мощность, простые механизмы/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "08. Работа, мощность, простые механизмы"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED
FORCE = RED
GOLD = WARM
WOOD = tint(COPPER, 0.55)
STONE = METAL
WATER = tint(SKY, 0.7)

G = 10.0


save = saver(OUT)


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=FORCE, lw=2.2, style="-|>", ms=14, ls="-", z=5):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, ls=ls, zorder=z
        )
    )


def dim(ax, p, q, text, off=(0, 0), color=INK, ha="center", va="center", fs=11):
    arrow(ax, p, q, color=color, lw=1.2, style="<|-|>", ms=9)
    ax.text(
        (p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text,
        color=color, ha=ha, va=va, fontsize=fs,
    )


def ground(ax, x0, x1, y, depth=0.15):
    ax.plot([x0, x1], [y, y], color=INK, lw=2, zorder=3)
    for x in np.arange(x0, x1, 0.25):
        ax.plot([x, x - depth], [y, y - depth], color=GREY, lw=1, zorder=2)


def style_axes(ax):
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- golden-


def golden_hydraulic():
    fig, ax = canvas(7.2, 4.4, (0, 12), (-0.5, 7.2))
    # vessel walls
    # Liquid reaches each piston: small piston at 1.7, big piston at 3.6
    ax.add_patch(Rectangle((1.0, 0.3), 1.6, 1.4, fc=WATER, ec="none"))
    ax.add_patch(Rectangle((4.0, 0.3), 5.0, 3.3, fc=WATER, ec="none"))
    ax.add_patch(Rectangle((2.6, 0.3), 1.4, 2.2, fc=WATER, ec="none"))
    ax.plot([1.0, 1.0, 2.6, 2.6, 4.0, 4.0, 9.0, 9.0], [4.6, 0.3, 0.3, 2.5, 2.5, 5.2, 5.2, 0.3], color=INK, lw=0)
    for xs, ys in [([1.0, 1.0, 4.0, 4.0], [4.6, 0.3, 0.3, 4.6]), ([2.6, 2.6, 4.0], [4.6, 2.5, 2.5])]:
        pass
    ax.plot([1.0, 1.0, 9.0, 9.0], [4.6, 0.3, 0.3, 4.6], color=INK, lw=2.5)
    ax.plot([2.6, 2.6, 4.0, 4.0], [4.6, 2.5, 2.5, 4.6], color=INK, lw=2.5)
    # small piston pushed down by h1 = 1.8, big piston up by h2 = 0.6 (area ratio 3)
    ax.add_patch(Rectangle((1.0, 3.5), 1.6, 0.25, fc=STONE, ec=INK, ls="--", alpha=0.35))
    ax.add_patch(Rectangle((1.0, 1.7), 1.6, 0.25, fc=STONE, ec=INK))
    ax.plot([1.8, 1.8], [1.95, 5.3], color=INK, lw=3)
    ax.add_patch(Rectangle((4.0, 3.0), 5.0, 0.25, fc=STONE, ec=INK, ls="--", alpha=0.35))
    ax.add_patch(Rectangle((4.0, 3.6), 5.0, 0.25, fc=STONE, ec=INK))
    ax.plot([6.5, 6.5], [3.85, 5.6], color=INK, lw=3)
    ax.add_patch(Rectangle((5.3, 5.6), 2.4, 0.9, fc=WOOD, ec=INK, zorder=4))
    arrow(ax, (1.8, 6.4), (1.8, 5.5), color=FORCE)
    ax.text(1.4, 6.1, r"$F_1$", color=FORCE, fontsize=13, ha="right")
    # F_1 / F_2 = h_2 / h_1 = 1/3, so F_2 is three times longer than F_1 (0.9)
    arrow(ax, (8.4, 4.0), (8.4, 6.7), color=FORCE)
    ax.text(8.6, 6.4, r"$F_2$", color=FORCE, fontsize=13, ha="left")
    dim(ax, (0.4, 3.62), (0.4, 1.82), r"$h_1$", off=(-0.4, 0))
    dim(ax, (9.6, 3.12), (9.6, 3.72), r"$h_2$", off=(0.45, 0))
    ax.text(6.0, 0.9, "жидкость", ha="center", color=INK, fontsize=10)
    ax.text(
        6.0, -0.35, r"$F_1/F_2 = h_2/h_1$: выигрыш в силе — проигрыш в расстоянии",
        ha="center", fontsize=11,
    )
    save(fig, "golden-hydraulic-trade.png")


def golden_lever_arcs():
    fig, ax = canvas(7.4, 4.6, (-5.2, 4.2), (-3.3, 2.4))
    l1, l2 = 4.0, 2.0
    phi = np.radians(28)
    # initial lever (dashed) and turned lever
    ax.plot([-l1, l2], [0, 0], color=GREY, lw=4, ls="--", zorder=2)
    a = (-l1 * np.cos(phi), -l1 * np.sin(phi))
    b = (l2 * np.cos(phi), l2 * np.sin(phi))
    ax.plot([a[0], b[0]], [a[1], b[1]], color=WOOD, lw=6, solid_capstyle="round", zorder=3)
    ax.add_patch(Polygon([(0, 0), (-0.4, -0.9), (0.4, -0.9)], fc=LIGHT, ec=INK, zorder=4))
    ax.add_patch(Arc((0, 0), 2 * l1, 2 * l1, theta1=180, theta2=180 + 28, color=BLUE, lw=2.2, zorder=4))
    ax.add_patch(Arc((0, 0), 2 * l2, 2 * l2, theta1=0, theta2=28, color=GREEN, lw=2.2, zorder=4))
    ax.text(-l1 * np.cos(np.radians(14)) - 0.35, -l1 * np.sin(np.radians(14)) - 0.1, r"$s_1$", color=BLUE, fontsize=14, ha="right")
    ax.text(l2 * np.cos(np.radians(14)) + 0.3, l2 * np.sin(np.radians(14)) - 0.05, r"$s_2$", color=GREEN, fontsize=14)
    # tangent forces
    t1 = np.array([np.sin(phi), -np.cos(phi)])
    arrow(ax, a, (a[0] + 1.6 * t1[0], a[1] + 1.6 * t1[1]), color=BLUE)
    ax.text(a[0] + 1.6 * t1[0] + 0.15, a[1] + 1.6 * t1[1] - 0.15, r"$F_1$", color=BLUE, fontsize=13)
    t2 = np.array([-np.sin(phi), np.cos(phi)])
    arrow(ax, b, (b[0], b[1] + 1.4), color=GREEN)
    ax.text(b[0] - 0.5, b[1] + 1.3, r"$F^*$", color=GREEN, fontsize=13)
    dim(ax, (-l1, 0.55), (0, 0.55), r"$l_1$", off=(0, 0.25))
    dim(ax, (0, 0.55), (l2, 0.55), r"$l_2$", off=(0, 0.25))
    ax.text(0.0, -2.35, r"$\dfrac{s_2}{s_1}=\dfrac{l_2}{l_1}$: сектора подобны", ha="center", fontsize=12)
    save(fig, "golden-lever-arcs.png")


def golden_hyperbola():
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    style_axes(ax)
    A = 360.0
    s = np.linspace(0.12, 1.05, 300)
    ax.plot(s, A / s, color=INK, lw=2)
    pts = [(0.24, 1500, "прямой подъём", BLUE), (0.80, 450, "через рычаг", GREEN)]
    for x, y, lab, col in pts:
        ax.add_patch(Rectangle((0, 0), x, y, fc=col, alpha=0.13, ec=col, lw=1.2))
        ax.plot([x], [y], "o", color=col, ms=8, zorder=5)
    ax.annotate("сила $1500$ Н,\nпуть $0{,}24$ м", (0.24, 1500), (0.33, 1610), fontsize=10, color=BLUE)
    ax.annotate("сила $450$ Н,\nпуть $0{,}80$ м", (0.80, 450), (0.66, 900), fontsize=10, color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN))
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 2000)
    ax.set_xlabel("путь точки приложения силы $s$, м")
    ax.set_ylabel("сила $F$, Н")
    ax.set_title("Площадь прямоугольника $F\\,s = 360$ Дж одна и та же", fontsize=11)
    save(fig, "golden-tradeoff-hyperbola.png")


def golden_incline_force_work():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    mg, h = 1200.0, 1.5
    ell = np.linspace(1.5, 8, 200)
    style_axes(a1)
    a1.plot(ell, mg * h / ell, color=BLUE, lw=2.2, label="без трения $F = mgh/l$")
    a1.plot([4.8], [375], "o", color=BLUE, ms=8)
    a1.plot([4.8], [500], "o", color=FORCE, ms=8)
    keep_dots(a1.annotate("задача 25.12:\n$F = 500$ Н (с трением)", (4.8, 500), (5.3, 700), color=FORCE, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=FORCE)))
    a1.annotate("$375$ Н без трения", (4.8, 375), (6.0, 560), color=BLUE, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=BLUE))
    a1.set_xlabel("длина плоскости $l$, м (высота $h = 1{,}5$ м)")
    a1.set_ylabel("сила $F$, Н")
    a1.set_title("Длиннее плоскость — меньше сила", fontsize=11)
    a1.set_ylim(0, 1300)
    a1.legend(loc="upper right", frameon=False)
    style_axes(a2)
    a2.axhline(mg * h, color=BLUE, lw=2.2, label="без трения: $A = mgh$")
    # Friction F_тр = mu*mg*cos(alpha) changes with the slope: mu comes from the task (125 N at l = 4.8 m, cos = 0.950)
    mu = 125.0 / (mg * np.sqrt(1 - (h / 4.8) ** 2))
    a2.plot(ell, mg * h + mu * mg * np.sqrt(ell**2 - h**2), color=FORCE, lw=2.2, label="с трением, $\\mu \\approx 0{,}11$: $A = mgh + F_{тр}\\,l$")
    a2.plot([4.8], [2400], "o", color=FORCE, ms=8)
    a2.annotate("$A_з = 500\\cdot 4{,}8 = 2400$ Дж", (4.8, 2400), (1.9, 2900), fontsize=10, color=FORCE,
                arrowprops=dict(arrowstyle="-", color=FORCE))
    a2.set_ylim(0, 3400)
    a2.set_xlabel("длина плоскости $l$, м")
    a2.set_ylabel("работа $A$, Дж")
    a2.set_title("Работа не зависит от длины только без трения", fontsize=11)
    a2.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    save(fig, "golden-incline-force-work.png")


def golden_task_lever():
    fig, ax = canvas(7.2, 3.6, (-5.6, 3.4), (-2.4, 3.0))
    # lever in two positions; long arm on the left is pushed down by 0.8 m
    l1, l2 = 4.0, 1.2
    phi = np.radians(9)
    ax.plot([-l1, l2], [0, 0], color=GREY, lw=4, ls="--", zorder=2)
    a = (-l1 * np.cos(phi), -l1 * np.sin(phi))
    b = (l2 * np.cos(phi), l2 * np.sin(phi))
    ax.plot([a[0], b[0]], [a[1], b[1]], color=WOOD, lw=6, solid_capstyle="round", zorder=3)
    ax.add_patch(Polygon([(0, 0), (-0.35, -0.8), (0.35, -0.8)], fc=LIGHT, ec=INK, zorder=4))
    arrow(ax, (-l1, 1.3), (-l1, 0.15), color=BLUE)
    ax.text(-l1 - 0.3, 1.0, r"$F_1 = 450$ Н", color=BLUE, fontsize=11, ha="right")
    dim(ax, (-l1 - 0.7, 0), (-l1 - 0.7, a[1]), r"$h_1 = 80$ см", off=(-0.15, 0), ha="right")
    ax.add_patch(Rectangle((l2 - 0.45, b[1] + 0.05), 0.9, 0.7, fc=STONE, ec=INK, zorder=4))
    ax.text(l2, b[1] + 0.4, r"$m$", color=PAPER, ha="center", va="center", fontsize=11, zorder=5)
    arrow(ax, (l2, b[1] + 0.05), (l2, -1.3), color=FORCE)
    ax.text(l2 + 0.25, -1.1, r"$P = mg$", color=FORCE, fontsize=11)
    dim(ax, (l2 + 1.2, 0), (l2 + 1.2, b[1]), r"$h_2 = ?$", off=(0.85, 0.0))
    ax.text(-1.6, -2.0, "Ответ: $h_2 = h_1 F_1/(mg) = 24$ см", fontsize=11, ha="center")
    save(fig, "golden-task-lever.png")


def golden_task_blocks():
    fig = plt.figure(figsize=(9.6, 4.2))
    ax = fig.add_axes([0.0, 0.0, 0.44, 1.0])
    ax.set_xlim(0, 8)
    ax.set_ylim(-0.6, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((1.0, 4.2), 4.0, 3.0, fc="none", ec=INK, ls="--", lw=2))
    ax.text(3.0, 5.7, "система\nблоков", ha="center", va="center", fontsize=12)
    ax.plot([2.0, 2.0], [4.2, 1.4], color=INK, lw=2)
    ax.add_patch(Rectangle((1.5, 0.6), 1.0, 0.8, fc=STONE, ec=INK))
    ax.text(2.0, 1.0, "$m$", color=PAPER, ha="center", va="center", fontsize=11)
    arrow(ax, (5.0, 5.2), (6.8, 2.2), color=BLUE)
    ax.text(6.0, 4.0, "$F$", color=BLUE, fontsize=13)
    dim(ax, (0.7, 1.4), (0.7, 3.4), "$h$", off=(-0.35, 0))
    ax.text(5.9, 4.6, "$s = ?$", fontsize=12, color=BLUE)
    ax.text(3.6, -0.3, "чёрный ящик", ha="center", fontsize=11, color=GREY)
    ax2 = fig.add_axes([0.53, 0.14, 0.2, 0.74])
    ax3 = fig.add_axes([0.80, 0.14, 0.2, 0.74])
    for a in (ax2, ax3):
        a.grid(True, axis="y", color=GRID)
        a.set_axisbelow(True)
    ax2.bar(["$F$", "$mg$"], [200, 800], color=[BLUE, FORCE], width=0.55)
    ax2.set_ylabel("Н")
    ax2.set_title("сила: в $4$ раза меньше", fontsize=10)
    ax3.bar(["$h$", "$s$"], [2, 8], color=[FORCE, BLUE], width=0.55)
    ax3.set_ylabel("м")
    ax3.set_title("путь: в $4$ раза больше", fontsize=10)
    save(fig, "golden-task-blocks.png")


def golden_black_box_open():
    fig, ax = canvas(5.6, 4.8, (0, 7), (-0.2, 6.2))
    ax.plot([0.5, 6.5], [5.8, 5.8], color=INK, lw=3)
    for x in np.arange(0.6, 6.5, 0.3):
        ax.plot([x, x + 0.2], [5.8, 6.0], color=GREY, lw=1)
    r = 0.45
    # movable pulley 2 (carries the load) and movable pulley 1 (hangs on the end of rope 2)
    p2, p1, pf = (2.25, 1.9), (2.7, 3.7), (3.6, 4.9)
    for c in (p2, p1, pf):
        ax.add_patch(Circle(c, r, fc=LIGHT, ec=INK, lw=2, zorder=3))
    # rope 2: ceiling -> down the left of pulley 2 -> under it -> up to the frame of pulley 1
    ax.plot([p2[0] - r, p2[0] - r], [5.8, p2[1]], color=INK, lw=2)
    ax.add_patch(Arc(p2, 2 * r, 2 * r, theta1=180, theta2=360, color=INK, lw=2, zorder=4))
    ax.plot([p2[0] + r, p2[0] + r], [p2[1], p1[1] - 0.9], color=INK, lw=2)
    ax.plot([p1[0], p1[0]], [p1[1], p1[1] - 0.9], color=INK, lw=3)
    # rope 1: ceiling -> down the left of pulley 1 -> under it -> up over the fixed pulley -> F
    ax.plot([p1[0] - r, p1[0] - r], [5.8, p1[1]], color=INK, lw=2)
    ax.add_patch(Arc(p1, 2 * r, 2 * r, theta1=180, theta2=360, color=INK, lw=2, zorder=4))
    ax.plot([p1[0] + r, p1[0] + r], [p1[1], pf[1]], color=INK, lw=2)
    ax.add_patch(Arc(pf, 2 * r, 2 * r, theta1=0, theta2=180, color=INK, lw=2, zorder=4))
    ax.plot([pf[0] + r, pf[0] + r], [pf[1], 2.9], color=INK, lw=2)
    ax.plot([pf[0], pf[0]], [pf[1], 5.8], color=INK, lw=2)
    # load on pulley 2
    ax.plot([p2[0], p2[0]], [p2[1], 1.0], color=INK, lw=3)
    ax.add_patch(Rectangle((p2[0] - 0.5, 0.2), 1.0, 0.8, fc=STONE, ec=INK))
    ax.text(p2[0], 0.6, "$m$", color=PAPER, ha="center", va="center", fontsize=11)
    arrow(ax, (pf[0] + r, 3.4), (pf[0] + r, 2.5), color=BLUE)
    ax.text(pf[0] + r + 0.2, 3.0, "$F$", color=BLUE, fontsize=13)
    ax.text(3.3, -0.2, "2 подвижных + 1 неподвижный: выигрыш в $4$ раза", ha="center", fontsize=10)
    save(fig, "golden-task-blocks-inside.png")


# ------------------------------------------------------------ efficiency-


def efficiency_ideal_real():
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    style_axes(ax)
    x = np.linspace(0, 10, 50)
    ax.fill_between(x, x, 10, color=FORCE, alpha=0.08)
    ax.plot(x, x, color=INK, lw=2.2, label="идеальный: $A_п = A_з$, $\\eta = 1$")
    ax.plot(x, 0.75 * x, color=GREEN, lw=2.2, label="реальный: $\\eta = 0{,}75$")
    ax.plot(x, 0.4 * x, color=BLUE, lw=2.2, label="реальный: $\\eta = 0{,}4$")
    ax.text(1.2, 8.6, "$\\eta > 1$ — вечный двигатель,\nтакого механизма нет", color=FORCE, fontsize=10)
    ax.plot([4, 8], [3, 6], "o", color=GREEN)
    ax.annotate("$A_з$ вдвое больше —\nи $A_п$ вдвое больше", (8, 6), (8.2, 4.6), fontsize=10, color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("затраченная работа $A_з$")
    ax.set_ylabel("полезная работа $A_п$")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_title("$\\eta = A_п/A_з$ — наклон прямой", fontsize=11)
    save(fig, "efficiency-ideal-vs-real.png")


def efficiency_stack():
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    names = ["Подвижный блок (25.16)", "Наклонная плоскость (25.12)", "Рычаг (25.10)"]
    eta = [0.9, 0.75, 0.9]
    y = np.arange(3)
    ax.barh(y, [100 * e for e in eta], color=GREEN, height=0.55, label="полезная работа $A_п$")
    ax.barh(y, [100 * (1 - e) for e in eta], left=[100 * e for e in eta], color=FORCE, alpha=0.75, height=0.55,
            label="потери на трение и вес деталей")
    for i, e in enumerate(eta):
        ax.text(100 * e / 2, i, f"$\\eta = {num(e, '', math=True)}$", ha="center", va="center", color=PAPER, fontsize=11)
    ax.set_yticks(y, names)
    for lbl in ax.get_yticklabels():
        keep_dots(lbl)
    ax.set_xlim(0, 100)
    ax.set_xlabel("доля затраченной работы $A_з$, %")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.28), ncol=2, frameon=False, fontsize=10)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "efficiency-stack.png")


def efficiency_lever_scheme():
    fig, ax = canvas(7.2, 3.6, (-5.6, 3.2), (-2.3, 2.6))
    a_ = 1.0
    l1, l2 = 4 * a_, a_
    phi = np.radians(10)
    ax.plot([-l1, l2], [0, 0], color=GREY, lw=4, ls="--", zorder=2)
    a = (-l1 * np.cos(phi), -l1 * np.sin(phi))
    b = (l2 * np.cos(phi), l2 * np.sin(phi))
    ax.plot([a[0], b[0]], [a[1], b[1]], color=WOOD, lw=6, solid_capstyle="round", zorder=3)
    ax.add_patch(Polygon([(0, 0), (-0.35, -0.8), (0.35, -0.8)], fc=LIGHT, ec=INK, zorder=4))
    dim(ax, (-l1, 1.6), (0, 1.6), r"$l_1 = 4a$", off=(0, 0.3))
    dim(ax, (0, 1.6), (l2, 1.6), r"$l_2 = a$", off=(0, 0.3))
    arrow(ax, (-l1, 0.6), (-l1, 0.15), color=BLUE)
    ax.text(-l1 - 0.25, 0.45, r"$F_1 = 250$ Н", color=BLUE, fontsize=11, ha="right")
    dim(ax, (-l1 - 0.6, 0), (-l1 - 0.6, a[1]), r"$h_1$", off=(-0.3, 0))
    ax.add_patch(Rectangle((l2 - 0.4, b[1] + 0.05), 0.8, 0.65, fc=STONE, ec=INK, zorder=4))
    ax.text(l2, b[1] + 0.38, r"$90$ кг", color=PAPER, ha="center", va="center", fontsize=9, zorder=5)
    arrow(ax, (l2, b[1] + 0.05), (l2, -1.1), color=FORCE)
    ax.text(l2 + 0.25, -0.95, r"$P = mg = 900$ Н", color=FORCE, fontsize=11)
    dim(ax, (l2 + 1.6, 0), (l2 + 1.6, b[1]), r"$h_2$", off=(0.35, 0))
    ax.text(-1.4, -1.9, r"$\dfrac{h_2}{h_1} = \dfrac{l_2}{l_1} = \dfrac{1}{4}$", fontsize=12, ha="center")
    save(fig, "efficiency-lever-scheme.png")


def efficiency_incline_scheme():
    fig, ax = canvas(7.2, 3.6, (-0.6, 8.4), (-1.2, 3.0))
    L, h = 4.8, 1.5
    x1 = np.sqrt(L**2 - h**2)
    sc = 1.35
    ax.add_patch(Polygon([(0, 0), (x1 * sc, 0), (x1 * sc, h * sc)], fc=LIGHT, ec=INK, lw=2))
    ax.plot([0, x1 * sc], [0, h * sc], color=INK, lw=3)
    # cart in the middle
    t = 0.45
    cx, cy = t * x1 * sc, t * h * sc
    ang = np.arctan2(h, x1)
    ax.add_patch(Rectangle((cx - 0.45, cy + 0.05), 0.9, 0.55, fc=STONE, ec=INK, angle=np.degrees(ang), zorder=4,
                           rotation_point=(cx, cy)))
    arrow(ax, (cx, cy + 0.4), (cx + 1.4 * np.cos(ang), cy + 0.4 + 1.4 * np.sin(ang)), color=BLUE)
    ax.text(cx + 1.6, cy + 1.25, r"$F = 500$ Н", color=BLUE, fontsize=11)
    dim(ax, (x1 * sc + 0.4, 0), (x1 * sc + 0.4, h * sc), r"$h = 1{,}5$ м", off=(0.75, 0), ha="center")
    ax.text(3.0, 0.45, r"$l = 4{,}8$ м", fontsize=11, rotation=np.degrees(ang), color=INK)
    ax.text(3.2, -0.75, r"$m = 120$ кг:  $A_п = mgh = 1800$ Дж,  $A_з = Fl = 2400$ Дж", ha="center", fontsize=11)
    save(fig, "efficiency-incline-scheme.png")


def efficiency_block_scheme():
    fig, ax = canvas(5.0, 4.8, (0, 6), (-0.3, 6.2))
    ax.plot([0.8, 4.4], [5.8, 5.8], color=INK, lw=3)
    for x in np.arange(0.9, 4.4, 0.3):
        ax.plot([x, x + 0.2], [5.8, 6.0], color=GREY, lw=1)
    ax.add_patch(Circle((2.5, 3.9), 0.75, fc=LIGHT, ec=INK, lw=2, zorder=3))
    ax.plot([1.75, 1.75], [5.8, 3.9], color=INK, lw=2)
    ax.plot([3.25, 3.25], [3.9, 4.8], color=INK, lw=2)
    ax.plot([2.5, 2.5], [3.15, 2.6], color=INK, lw=2)
    ax.add_patch(Polygon([(1.6, 2.6), (3.4, 2.6), (2.5, 1.9)], fc=LIGHT, ec=INK))
    ax.add_patch(Rectangle((1.6, 1.1), 1.8, 0.8, fc=STONE, ec=INK))
    ax.text(2.5, 1.5, "сейф $450$ кг", color=PAPER, ha="center", va="center", fontsize=9)
    arrow(ax, (3.25, 4.8), (3.25, 5.5), color=BLUE)
    ax.text(3.5, 5.3, "$F$", color=BLUE, fontsize=13)
    dim(ax, (4.0, 3.9), (4.0, 4.8), r"$h_1$", off=(0.3, 0))
    dim(ax, (0.7, 1.5), (0.7, 2.1), r"$h_2$", off=(-0.3, 0))
    arrow(ax, (2.5, 1.1), (2.5, 0.3), color=FORCE)
    ax.text(2.75, 0.5, r"$P$", color=FORCE, fontsize=13)
    ax.text(4.9, 3.0, r"$\dfrac{h_2}{h_1}=\dfrac{1}{2}$", fontsize=12)
    save(fig, "efficiency-block-scheme.png")


def efficiency_block_force():
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    style_axes(ax)
    eta = np.linspace(0.5, 1.0, 200)
    m = 450.0
    ax.plot(eta, m * G / (2 * eta), color=BLUE, lw=2.2)
    ax.plot([0.9], [2500], "o", color=FORCE, ms=8)
    ax.plot([1.0], [2250], "o", color=GREEN, ms=8)
    ax.annotate("$\\eta = 0{,}9$: $F = 2500$ Н", (0.9, 2500), (0.62, 2650), color=FORCE, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=FORCE))
    ax.annotate("идеальный блок, $\\eta = 1$: $F = 2250$ Н", (1.0, 2250), (0.6, 2350), color=GREEN, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=GREEN))
    ax.axhline(2250, color=GREEN, lw=1, ls=":")
    ax.set_xlabel("КПД блока $\\eta$")
    ax.set_ylabel("сила на свободном конце $F$, Н")
    ax.set_title("$F = mg/(2\\eta)$: чем хуже блок, тем сильнее тянуть", fontsize=11)
    ax.set_ylim(2000, 4700)
    save(fig, "efficiency-block-force.png")


def efficiency_friction():
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    style_axes(ax)
    mgh = 1800.0
    ftr = np.linspace(0, 400, 300)
    for L, col in [(3.0, BLUE), (4.8, GREEN), (8.0, FORCE)]:
        ax.plot(ftr, mgh / (mgh + ftr * L), color=col, lw=2.2, label=f"$l = {num(L, '', math=True)}$ м")
    ax.plot([125], [0.75], "o", color=GREEN, ms=9, zorder=5)
    keep_dots(ax.annotate("задача 25.12: $\\eta = 0{,}75$,\n$F_{тр} = 125$ Н", (125, 0.75), (190, 0.9), fontsize=10, color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN)))
    ax.set_xlabel("сила трения $F_{тр}$, Н")
    ax.set_ylabel("КПД $\\eta$")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, 400)
    ax.set_title("$\\eta = \\dfrac{mgh}{mgh + F_{тр}\\,l}$: $m = 120$ кг, $h = 1{,}5$ м", fontsize=11)
    ax.legend(frameon=False, title="длина плоскости")
    save(fig, "efficiency-friction.png")


# ------------------------------------------------------------- energy-


def energy_potential_reference():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.2, 4.1))
    style_axes(a1)
    h = np.linspace(0, 1.2, 50)
    a1.plot(h, 10 * h, color=BLUE, lw=2.2)
    a1.plot([1.0], [10], "o", color=BLUE, ms=8)
    a1.annotate("$1$ кг на $1$ м:\n$E_п = 10$ Дж", (1.0, 10), (0.45, 10.2), fontsize=10, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE))
    a1.set_xlabel("высота $h$ над столом, м")
    a1.set_ylabel("$E_п = mgh$, Дж")
    a1.set_title("Работа подъёма — энергия гири ($m = 1$ кг)", fontsize=11)
    style_axes(a2)
    a2.plot(h, 10 * h, color=BLUE, lw=2.2, label="от уровня стола")
    a2.plot(h, 10 * (h + 0.75), color=FORCE, lw=2.2, label="от уровня пола (стол условно $0{,}75$ м)")
    for lo, hi, col in [(0.3, 0.9, GREY)]:
        a2.plot([lo, lo], [10 * lo, 10 * (lo + 0.75)], color=GREY, lw=1, ls=":")
        a2.plot([hi, hi], [10 * hi, 10 * (hi + 0.75)], color=GREY, lw=1, ls=":")
    a2.annotate("", (0.9, 1.0), (0.3, 1.0), arrowprops=dict(arrowstyle="<->", color=INK))
    a2.text(0.6, 1.5, "$\\Delta E_п = 6$ Дж\nв обоих случаях", ha="center", fontsize=10)
    a2.set_xlabel("высота $h$ над столом, м")
    a2.set_ylabel("$E_п$, Дж")
    a2.set_title("Уровень отсчёта сдвигает график, а не изменение", fontsize=11)
    a2.legend(frameon=False, fontsize=9.5, loc="upper left")
    fig.tight_layout()
    save(fig, "energy-potential-reference.png")


def energy_kinetic():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.2, 4.1))
    style_axes(a1)
    m = np.linspace(0, 1.0, 50)
    a1.plot(m, 0.5 * m * 1.0**2, color=FORCE, lw=2.2)
    a1.plot([0.2, 1.0], [0.1, 0.5], "o", color=FORCE)
    a1.text(0.24, 0.06, "$200$ г: $0{,}1$ Дж", fontsize=10)
    a1.text(0.98, 0.3, "$1$ кг: $0{,}5$ Дж", fontsize=10, ha="right")  # below the line, which is at 0.4-0.5 here
    a1.set_xlabel("масса $m$, кг ($v = 1$ м/с)")
    a1.set_ylabel("$E_к = mv^2/2$, Дж")
    a1.set_title("Пропорционально массе", fontsize=11)
    style_axes(a2)
    v = np.linspace(0, 100, 200)
    a2.plot(v, (v / 40) ** 2, color=FORCE, lw=2.2)
    a2.plot([40, 80], [1, 4], "o", color=FORCE, ms=8)
    a2.annotate("$40$ км/ч: $E_к = 1$", (40, 1), (10, 2.5), fontsize=10,
                arrowprops=dict(arrowstyle="-", color=GREY))
    a2.annotate("$80$ км/ч: $E_к = 4$", (80, 4), (48, 5.5), fontsize=10,
                arrowprops=dict(arrowstyle="-", color=GREY))
    a2.set_xlabel("скорость $v$, км/ч")
    a2.set_ylabel("$E_к$ в долях от значения при $40$ км/ч")
    a2.set_title("Пропорционально квадрату скорости", fontsize=11)
    a2.set_ylim(0, 7)
    fig.tight_layout()
    save(fig, "energy-kinetic.png")


def energy_fall_height():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.2))
    h0 = 1.0
    h = np.linspace(0, h0, 100)
    style_axes(a1)
    a1.plot(h, 10 * h, color=BLUE, lw=2.4, label="$E_п = mgh$")
    a1.plot(h, 10 * (h0 - h), color=FORCE, lw=2.4, label="$E_к = mg(h_0 - h)$")
    a1.plot(h, 10 * h + 10 * (h0 - h), color=INK, lw=2, ls="--", label="$E_п + E_к$")
    a1.invert_xaxis()
    a1.set_xlabel("высота $h$ над столом, м (падение слева направо)")
    a1.set_ylabel("энергия, Дж")
    a1.set_ylim(0, 12.5)
    a1.set_title("Падение гири $1$ кг без трения", fontsize=11)
    a1.legend(frameon=False, loc="center right")
    style_axes(a2)
    a2.plot(h, 10 * h, color=BLUE, lw=2.4, label="$E_п$")
    # Uniform sliding: the speed is constant and not zero, so E_к is a positive constant
    a2.plot(h, np.full_like(h, 1.0), color=FORCE, lw=2.4, label="$E_к = $ const: скорость не растёт")
    a2.plot(h, 10 * h + 1.0, color=INK, lw=2, ls="--", label="$E_п + E_к$ убывает")
    a2.invert_xaxis()
    a2.set_xlabel("высота $h$ над столом, м")
    a2.set_ylabel("энергия, Дж")
    a2.set_ylim(0, 12.5)
    a2.set_title("Равномерное сползание по шероховатой плоскости", fontsize=11)
    a2.legend(frameon=False, loc="upper right", fontsize=9.5)  # the upper right corner is free of curves
    fig.tight_layout()
    save(fig, "energy-fall-height.png")


def energy_fall_time():
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    style_axes(ax)
    T = np.sqrt(2 * 1.0 / G)
    t = np.linspace(0, T, 200)
    ep = 10 * (1.0 - G * t**2 / 2)
    ek = 10 * G * t**2 / 2
    ax.plot(t, ep, color=BLUE, lw=2.4, label="$E_п$")
    ax.plot(t, ek, color=FORCE, lw=2.4, label="$E_к$")
    ax.plot(t, ep + ek, color=INK, lw=2, ls="--", label="$E_п + E_к$")
    ax.set_xlabel("время падения $t$, с ($g = 10$ м/с$^2$)")
    ax.set_ylabel("энергия, Дж")
    ax.set_ylim(0, 12.5)
    ax.set_title("Свободное падение гири $1$ кг с $1$ м", fontsize=11)
    ax.legend(frameon=False, loc="center right")
    save(fig, "energy-fall-time.png")


def energy_pendulum_scheme():
    fig, ax = canvas(9.0, 5.6, (-5.2, 5.2), (-6.6, 1.2))
    L = 3.6
    th = np.radians(35)
    ax.plot([-1.0, 1.0], [0, 0], color=INK, lw=3)
    for x in np.arange(-1.0, 1.0, 0.25):
        ax.plot([x, x + 0.15], [0, 0.18], color=GREY, lw=1)
    for ang, col, lab in [(-th, BLUE, "1"), (0.0, FORCE, "2"), (th, BLUE, "3")]:
        x, y = L * np.sin(ang), -L * np.cos(ang)
        ax.plot([0, x], [0, y], color=GREY if ang else INK, lw=1.6 if ang else 2, ls="--" if ang else "-")
        ax.add_patch(Circle((x, y), 0.3, fc=col, ec=INK, zorder=4, alpha=0.9))
        ax.text(x, y - 0.6, lab, ha="center", fontsize=12)
    ax.add_patch(Arc((0, 0), 2.6 * 2, 2.6 * 2, theta1=-90 - 35, theta2=-90 + 35, color=GREY, lw=1))
    # The zero level passes through the lowest point (centre of ball 2), where E_п = 0
    ax.plot([-5, 5], [-L, -L], color=GRID, lw=1.5)
    ax.text(5.1, -L, "уровень\n$E_п = 0$", fontsize=9, color=GREY, va="center")
    h = L * (1 - np.cos(th))
    dim(ax, (-4.7, -L), (-4.7, -L + h), r"$h$", off=(-0.35, 0))
    # small energy bars at each position
    base = -5.6

    def bars(cx, ep, ek):
        ax.add_patch(Rectangle((cx - 0.45, base), 0.35, 1.2 * ep, fc=BLUE))
        ax.add_patch(Rectangle((cx + 0.1, base), 0.35, 1.2 * ek, fc=FORCE))
        ax.plot([cx - 0.6, cx + 0.6], [base, base], color=INK, lw=1)
    bars(-L * np.sin(th), 1.0, 0.0)
    bars(0.0, 0.0, 1.0)
    bars(L * np.sin(th), 1.0, 0.0)
    ax.text(0, base - 0.6, "синий — $E_п$, красный — $E_к$; сумма постоянна", ha="center", fontsize=10)
    save(fig, "energy-pendulum-scheme.png")


def energy_pendulum_time():
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    style_axes(ax)
    L = 1.0
    th0 = np.arccos(1 - 0.05 / L)
    w = np.sqrt(G / L)
    T = 2 * np.pi / w
    t = np.linspace(0, T, 400)
    th = th0 * np.cos(w * t)
    ep = 0.5 * (1 - np.cos(th)) / (1 - np.cos(th0))
    ek = 0.5 - ep
    ax.plot(t, ep, color=BLUE, lw=2.4, label="$E_п$")
    ax.plot(t, ek, color=FORCE, lw=2.4, label="$E_к$")
    ax.plot(t, ep + ek, color=INK, lw=2, ls="--", label="$E_п + E_к$")
    ax.set_xlabel("время $t$, с (нить $1$ м — не из лекции; малые углы)")
    ax.set_ylabel("энергия, Дж ($m = 1$ кг)")
    ax.set_title("Колебание маятника: потенциальная, кинетическая, потенциальная…", fontsize=11)
    ax.legend(frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    ax.set_ylim(0, 0.62)
    save(fig, "energy-pendulum-time.png")


def energy_task_pendulum():
    fig = plt.figure(figsize=(10.0, 4.0))
    ax = fig.add_axes([0.0, 0.0, 0.42, 1.0])
    ax.set_xlim(-2.5, 3.5)
    ax.set_ylim(-4.2, 0.9)
    ax.set_aspect("equal")
    ax.axis("off")
    L = 3.6
    ax.plot([-1.0, 1.0], [0, 0], color=INK, lw=3)
    ax.plot([0, 0], [0, -L], color=INK, lw=2)
    ax.add_patch(Circle((0, -L), 0.28, fc=FORCE, ec=INK, zorder=4))
    arrow(ax, (0.35, -L), (1.6, -L), color=BLUE)
    ax.text(1.7, -L + 0.15, r"$v = 1$ м/с", color=BLUE, fontsize=11)
    th = np.radians(40)
    x, y = L * np.sin(th), -L * np.cos(th)
    ax.plot([0, x], [0, y], color=GREY, ls="--", lw=1.6)
    ax.add_patch(Circle((x, y), 0.28, fc=PAPER, ec=INK, ls="--", zorder=4))
    ax.plot([-0.5, x + 0.8], [-L, -L], color=GRID, lw=1.5)
    dim(ax, (x + 0.8, -L), (x + 0.8, y), r"$h$", off=(0.3, 0))
    ax.text(-0.75, -L - 0.5, "1", fontsize=12)
    ax.text(x + 0.35, y + 0.35, "2", fontsize=12)
    ax2 = fig.add_axes([0.52, 0.15, 0.45, 0.72])
    style_axes(ax2)
    v = np.linspace(0, 2.5, 200)
    ax2.plot(v, 100 * v**2 / (2 * G), color=BLUE, lw=2.4)
    ax2.plot([1], [5], "o", color=FORCE, ms=9)
    ax2.annotate("$v = 1$ м/с: $h = 5$ см", (1, 5), (0.15, 20), fontsize=10, color=FORCE,
                 arrowprops=dict(arrowstyle="-", color=FORCE))
    ax2.set_xlabel("скорость толчка $v$, м/с")
    ax2.set_ylabel("высота подъёма $h = v^2/2g$, см")
    ax2.set_title("Масса маятника в ответ не входит", fontsize=11)
    save(fig, "energy-task-pendulum.png")


if __name__ == "__main__":
    golden_hydraulic()
    golden_lever_arcs()
    golden_hyperbola()
    golden_incline_force_work()
    golden_task_lever()
    golden_task_blocks()
    golden_black_box_open()
    efficiency_ideal_real()
    efficiency_stack()
    efficiency_lever_scheme()
    efficiency_incline_scheme()
    efficiency_block_scheme()
    efficiency_block_force()
    efficiency_friction()
    energy_potential_reference()
    energy_kinetic()
    energy_fall_height()
    energy_fall_time()
    energy_pendulum_scheme()
    energy_pendulum_time()
    energy_task_pendulum()
