"""Figures of section f08 "Рычаг. Момент силы" and "Блоки" (lessons 78-83).

Run: python3 lever_pulley.py
PNG files with prefixes lever- and pulley- go to
content/08. Работа, мощность, простые механизмы/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

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
from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED
FORCE = RED
GOLD = WARM
WOOD = tint(COPPER, 0.55)
STONE = METAL


save = saver(OUT)


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p0, p1, color=FORCE, lw=2.2, style="-|>", ms=14, z=5, ls="-"):
    ax.annotate(
        "",
        xy=p1,
        xytext=p0,
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0,
            mutation_scale=ms, linestyle=ls,
        ),
        zorder=z,
    )


def text(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=8, **kw)


def dim(ax, x0, x1, y, label, color=BLUE, size=11, dy=0.28):
    arrow(ax, (x0, y), (x1, y), color=color, lw=1.4, style="<|-|>", ms=9)
    for x in (x0, x1):
        ax.plot([x, x], [y - 0.13, y + 0.13], color=color, lw=1.4, zorder=5)
    text(ax, (x0 + x1) / 2, y + dy, label, size=size, color=color)


def bar(ax, x0, x1, y, h=0.28, sections=None, face=WOOD):
    """Lever bar; sections=n draws n alternating black and white parts."""
    if sections:
        w = (x1 - x0) / sections
        for i in range(sections):
            fc = INK if i % 2 == 0 else PAPER
            ax.add_patch(
                Rectangle((x0 + i * w, y - h / 2), w, h, fc=fc, ec=INK, lw=1.3, zorder=3)
            )
    else:
        ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, fc=face, ec=INK, lw=1.3, zorder=3))


def support(ax, x, y, s=0.45):
    ax.add_patch(
        Polygon([(x, y), (x - s, y - 1.35 * s), (x + s, y - 1.35 * s)], fc=GREY, ec=INK, lw=1.3, zorder=4)
    )
    ax.plot([x - 1.5 * s, x + 1.5 * s], [y - 1.35 * s] * 2, color=INK, lw=1.6, zorder=4)


def box(ax, x, y, w, h, label=None, fc=LIGHT, size=11):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=fc, ec=INK, lw=1.3, zorder=4))
    if label:
        text(ax, x, y, label, size=size)


def hatch_ceiling(ax, x0, x1, y, h=0.22):
    ax.plot([x0, x1], [y, y], color=INK, lw=2, zorder=4)
    for x in np.arange(x0, x1, 0.28):
        ax.plot([x, x + 0.2], [y, y + h], color=INK, lw=1, zorder=4)


def rot_arrow(ax, c, r, a0, a1, color, lw=2.4, ms=14):
    t = np.radians(np.linspace(a0, a1, 40))
    xs, ys = c[0] + r * np.cos(t), c[1] + r * np.sin(t)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, zorder=5)
    arrow(ax, (xs[-3], ys[-3]), (xs[-1], ys[-1]), color=color, lw=lw, ms=ms)


def pulley(ax, c, r, axle=True, fc=PAPER):
    ax.add_patch(Circle(c, r, fc=fc, ec=INK, lw=2, zorder=3))
    ax.add_patch(Circle(c, r * 0.72, fc="none", ec=GREY, lw=1, zorder=3))
    if axle:
        ax.add_patch(Circle(c, 0.07, fc=INK, ec=INK, zorder=6))


def rope(ax, pts, color=INK, lw=1.8):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, zorder=2.5, solid_capstyle="round")


def arc_rope(ax, c, r, a0, a1, color=INK, lw=1.8):
    t = np.radians(np.linspace(a0, a1, 60))
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, zorder=2.5)


def weight_label(ax, x, y, label, color=FORCE, size=12):
    text(ax, x, y, label, size=size, color=color)


# ---------------------------------------------------------------- lever


def lever_two_kinds():
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax in axs:
        ax.set_aspect("equal")
        ax.axis("off")
    # first kind
    ax = axs[0]
    ax.set_xlim(-5.6, 5.6)
    ax.set_ylim(-3.2, 3.0)
    bar(ax, -5, 5, 0)
    support(ax, 0, -0.14)
    text(ax, 0, -1.25, "O", size=12)
    arrow(ax, (-4, 2.2), (-4, 0.16))
    arrow(ax, (2.5, 2.2), (2.5, 0.16))
    text(ax, -4.45, 1.5, r"$\vec F_1$", size=13, color=FORCE)
    text(ax, 2.95, 1.5, r"$\vec F_2$", size=13, color=FORCE)
    for x in (-4, 2.5):
        ax.plot([x, x], [-0.14, -2.0], color=GREY, lw=1.2, ls="--", zorder=1)
    dim(ax, -4, 0, -2.2, r"$l_1$")
    dim(ax, 0, 2.5, -2.2, r"$l_2$")
    ax.set_title("Рычаг первого рода")
    # second kind
    ax = axs[1]
    ax.set_xlim(-5.6, 5.6)
    ax.set_ylim(-3.2, 3.0)
    bar(ax, -5, 5, 0)
    support(ax, 5, -0.14)
    text(ax, 5, -1.25, "O", size=12)
    arrow(ax, (-5, -1.7), (-5, -0.16))
    arrow(ax, (-1.5, 2.2), (-1.5, 0.16))
    text(ax, -4.35, -1.15, r"$\vec F_1$", size=13, color=FORCE)
    text(ax, -0.95, 1.5, r"$\vec F_2$", size=13, color=FORCE)
    for x in (-5, -1.5):
        ax.plot([x, x], [-0.14, -2.0], color=GREY, lw=1.2, ls="--", zorder=1)
    dim(ax, -5, 5, -2.4, r"$l_1$", dy=-0.42)
    dim(ax, -1.5, 5, -1.7, r"$l_2$", dy=-0.42)
    ax.set_title("Рычаг второго рода")
    save(fig, "lever-two-kinds.png")


def lever_arm_construction():
    fig, ax = canvas(6.8, 4.6, (-2.5, 7.4), (-3.3, 3.6))
    O = np.array([0.0, 0.0])
    A = np.array([4.4, 0.2])
    d = np.array([np.cos(np.radians(-50)), np.sin(np.radians(-50))])
    # line of action
    ax.plot(*zip(A - 3.4 * d, A + 3.9 * d), color=GREY, lw=1.4, ls="--", zorder=1)
    arrow(ax, A, A + 2.0 * d)
    text(ax, *(A + 2.0 * d + np.array([0.55, 0.0])), r"$\vec F$", size=13, color=FORCE)
    # lever
    ax.plot([O[0], A[0]], [O[1], A[1]], color=INK, lw=7, solid_capstyle="round", zorder=3)
    ax.plot([O[0], A[0]], [O[1], A[1]], color=WOOD, lw=4.5, solid_capstyle="round", zorder=3.1)
    ax.add_patch(Circle(O, 0.16, fc=INK, zorder=6))
    text(ax, -0.4, -0.45, "O", size=12)
    # foot of perpendicular
    H = A + d * np.dot(O - A, d)
    ax.plot(*zip(O, H), color=BLUE, lw=2.2, zorder=4)
    n = (O - H) / np.linalg.norm(O - H)
    t = d
    sq = 0.32
    ax.plot(
        [H[0] + n[0] * sq, H[0] + (n + t)[0] * sq, H[0] + t[0] * sq],
        [H[1] + n[1] * sq, H[1] + (n + t)[1] * sq, H[1] + t[1] * sq],
        color=BLUE, lw=1.4, zorder=4,
    )
    text(ax, *((O + H) / 2 + np.array([-0.2, 0.35])), r"$l$", size=14, color=BLUE)
    text(ax, 2.3, -0.55, r"$OA$ — не плечо", size=10, color=GREY, rotation=2.6)
    text(ax, 5.5, 2.6, "линия действия\nсилы", size=10, color=GREY)
    fig.suptitle("Плечо — перпендикуляр от оси к линии действия силы", fontsize=12, y=0.99)
    save(fig, "lever-arm-construction.png")


def lever_experiments():
    rows = [
        (dict(l1=10, F1=0.5, l2=10, F2=0.5), "1)", r"$F_1/F_2 = 1$,  $l_2/l_1 = 1$"),
        (dict(l1=10, F1=1.0, l2=5, F2=2.0), "2)", r"$F_1/F_2 = 1/2$,  $l_2/l_1 = 1/2$"),
        (dict(l1=20, F1=1.5, l2=15, F2=2.0), "3)", r"$F_1/F_2 = 3/4$,  $l_2/l_1 = 3/4$"),
    ]
    fig, axs = plt.subplots(3, 1, figsize=(8.4, 6.8))
    for ax, (p, mark, ratio) in zip(axs, rows):
        ax.set_xlim(-27, 47)
        ax.set_ylim(-9.5, 6.5)
        ax.set_aspect("equal")
        ax.axis("off")
        bar(ax, -25, 25, 0, h=1.6)
        support(ax, 0, -0.8, s=1.8)
        for x, F, name in ((-p["l1"], p["F1"], "F_1"), (p["l2"], p["F2"], "F_2")):
            ax.plot([x, x], [-0.8, -4.4], color=INK, lw=1.2)
            box(ax, x, -5.7, 3.6, 2.6, fc=WOOD)
            arrow(ax, (x, -7.0), (x, -9.0), lw=2)
            ax.text(x + 2.6, -7.9, rf"${name}=" + num(F, 1, math=True) + r"$ Н",
                    fontsize=10, color=FORCE, va="center")
        dim(ax, -p["l1"], 0, 3.3, rf"$l_1={p['l1']}$ см", dy=1.2, size=10)
        # a short arm gets its label higher, so that the two labels do not touch
        dy2 = 1.2 if p["l2"] >= 10 else 2.6
        dim(ax, 0, p["l2"], 3.3, rf"$l_2={p['l2']}$ см", dy=dy2, size=10)
        text(ax, -26, 6, mark, size=14, ha="left")
        text(ax, 36, 0, ratio, size=11, ha="center")
    fig.suptitle("Опыты с рычагом: рычаг в равновесии", fontsize=12, y=0.93)
    save(fig, "lever-experiments.png")


def lever_hyperbola():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axs[0]
    l = np.linspace(2.5, 40, 400)
    pts = {0.05: (10, 0.5), 0.10: (10, 1.0), 0.30: (20, 1.5)}
    cols = {0.05: BLUE, 0.10: GREEN, 0.30: FORCE}
    for M, (px, py) in pts.items():
        ax.plot(l, M / (l / 100), color=cols[M], lw=2, label=rf"$M={num(M, '', math=True)}$ Н$\cdot$м")
        ax.scatter([px], [py], color=cols[M], s=60, zorder=5, edgecolor=INK)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 3.2)
    ax.set_xlabel(r"плечо $l_1$, см")
    ax.set_ylabel(r"сила $F_1$, Н")
    ax.set_title(r"$F_1=M/l_1$: сила у рычага при неизменном моменте")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")
    ax = axs[1]
    r = np.linspace(0, 4.5, 100)
    ax.fill_between(r, r, 0, where=r >= 1, color=GREEN, alpha=0.12)
    ax.fill_between(r, r, 5, where=r <= 1, color=GOLD, alpha=0.15)
    ax.plot(r, r, color=INK, lw=2)
    for rr, gg in ((1.0, 1.0), (2.0, 2.0), (20 / 15, 20 / 15)):
        ax.scatter([rr], [gg], color=FORCE, s=55, zorder=5, edgecolor=INK)
    ax.axhline(1, color=GREY, lw=1, ls="--")
    text(ax, 3.2, 0.45, "выигрыш в силе", size=10, color=GREEN)
    text(ax, 0.55, 2.7, "проигрыш\nв силе", size=10, color=INK)
    ax.set_xlim(0, 4.5)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel(r"отношение плеч $l_1/l_2$")
    ax.set_ylabel(r"выигрыш в силе $F_2/F_1$")
    ax.set_title("Выигрыш в силе равен отношению плеч")
    ax.grid(color=GRID, lw=0.8)
    save(fig, "lever-hyperbola.png")


def lever_path_force():
    fig, ax = canvas(8.4, 3.9, (-5.6, 3.2), (-2.4, 2.6))
    ang = np.radians(18)
    l1, l2 = 5.0, 1.25
    ax.set_xlim(-6.3, 3.2)
    # horizontal (dashed)
    ax.plot([-l1, l2], [0, 0], color=GREY, lw=1.4, ls="--", zorder=1)
    # tilted lever: left end goes down
    L = np.array([-l1 * np.cos(ang), -l1 * np.sin(ang)])
    R = np.array([l2 * np.cos(ang), l2 * np.sin(ang)])
    ax.plot(*zip(L, R), color=INK, lw=9, solid_capstyle="butt", zorder=3)
    ax.plot(*zip(L, R), color=WOOD, lw=6.5, solid_capstyle="butt", zorder=3.1)
    support(ax, 0, -0.12, s=0.4)
    arrow(ax, (-l1, 0.05), (L[0], L[1] + 0.02), color=BLUE, lw=2, ms=12)
    text(ax, L[0] - 0.35, L[1] / 2 + 0.05, r"$s_1$", size=13, color=BLUE)
    arrow(ax, (l2, 0.05), (R[0], R[1] - 0.02), color=BLUE, lw=2, ms=12)
    text(ax, R[0] + 0.35, R[1] / 2 + 0.05, r"$s_2$", size=13, color=BLUE)
    arrow(ax, (L[0] + 0.6, L[1] + 1.6), (L[0] + 0.6, L[1] + 0.4), lw=2, ms=10)
    text(ax, L[0] + 1.1, L[1] + 1.35, r"$\vec F_1$", size=13, color=FORCE)
    # F_2 acts on the lever itself: its line of action meets the right end
    arrow(ax, (R[0], R[1] + 2.2), (R[0], R[1] + 0.12), lw=4, ms=18)
    text(ax, R[0] + 0.45, R[1] + 1.4,r"$\vec F_2$", size=13, color=FORCE)
    text(ax, -0.5, -1.8, r"малая сила проходит большой путь: $s_1/s_2=l_1/l_2$", size=11)
    save(fig, "lever-path-force.png")


def lever_moment_signs():
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6))
    for ax, sgn in zip(axs, (+1, -1)):
        ax.set_xlim(-4.6, 4.6)
        ax.set_ylim(-2.0, 3.8)
        ax.set_aspect("equal")
        ax.axis("off")
        bar(ax, -4, 4, 0)
        support(ax, 0, -0.14, s=0.4)
        ax.add_patch(Circle((0, 0), 0.09, fc=INK, zorder=7))
        x = -2.5 if sgn > 0 else 2.5
        arrow(ax, (x, 2.2), (x, 0.16))
        text(ax, x + (-0.5 if sgn > 0 else 0.5), 1.7, r"$\vec F$", size=13, color=FORCE)
        if sgn > 0:
            rot_arrow(ax, (0, 0.0), 1.2, 25, 150, GREEN)
            text(ax, 0, 3.3, r"$M>0$: против часовой стрелки", size=11, color=GREEN)
        else:
            rot_arrow(ax, (0, 0.0), 1.2, 155, 30, FORCE)
            text(ax, 0, 3.3, r"$M<0$: по часовой стрелке", size=11, color=FORCE)
        ax.set_title("")
    fig.suptitle("Знак момента силы: против часовой стрелки — плюс", fontsize=12, y=1.0)
    save(fig, "lever-moment-signs.png")


def _moment_bars(ax, ccw, cw, unit, lim=None):
    """Stacked bars: counter-clockwise moments against clockwise ones."""
    bottom = 0
    for lab, v, col in ccw:
        ax.bar(0, v, bottom=bottom, width=0.6, color=col, edgecolor=INK, lw=1.2)
        ax.text(0, bottom + v / 2, lab, ha="center", va="center", fontsize=10, color=PAPER if v > 0 else INK)
        bottom += v
    tot_ccw = bottom
    bottom = 0
    for lab, v, col in cw:
        ax.bar(1, v, bottom=bottom, width=0.6, color=col, edgecolor=INK, lw=1.2)
        ax.text(1, bottom + v / 2, lab, ha="center", va="center", fontsize=10, color=PAPER)
        bottom += v
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["против часовой\n(плюс)", "по часовой\n(минус)"])
    ax.set_ylabel(f"момент, {unit}")
    ax.set_ylim(0, (lim or max(tot_ccw, bottom)) * 1.18)
    ax.spines["bottom"].set_visible(True)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def lever_moment_balance():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1.9, 1]})
    ax = axs[0]
    ax.set_xlim(-25, 21)
    ax.set_ylim(-11, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    bar(ax, -22, 20, 0, h=1.4)
    support(ax, 0, -0.7, s=1.7)
    loads = [(-20, 0.5, r"$F_3=0{,}5$ Н", GREEN), (-10, 2.0, r"$F_1=2$ Н", BLUE), (15, 2.0, r"$F_2=2$ Н", FORCE)]
    for x, F, lab, col in loads:
        ax.plot([x, x], [-0.7, -3.5], color=INK, lw=1.2)
        box(ax, x, -4.8, 3.6, 2.6, fc=WOOD)
        arrow(ax, (x, -6.1), (x, -8.2), color=col, lw=2)
        ax.text(x, -9.7, lab, ha="center", fontsize=10, color=col)
    dim(ax, -20, 0, 6.2, r"$l_3=20$ см", dy=1.1, size=10)
    dim(ax, -10, 0, 2.6, r"$l_1=10$ см", dy=1.1, size=10)
    dim(ax, 0, 15, 2.6, r"$l_2=15$ см", dy=1.1, size=10)
    ax.set_title("Три силы на рычаге в равновесии")
    _moment_bars(
        axs[1],
        [(r"$M_1=0{,}2$", 0.2, BLUE), (r"$M_3=0{,}1$", 0.1, GREEN)],
        [(r"$M_2=0{,}3$", 0.3, FORCE)],
        r"Н$\cdot$м",
    )
    axs[1].set_title("Моменты уравновешены")
    save(fig, "lever-moment-balance.png")


# ---------------------------------------------------------------- lever tasks


def _sections(ax, n, y=0.0, h=0.7):
    bar(ax, 0, n, y, h=h, sections=n)


def lever_task_sections():
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 6.2))
    # 13.5
    ax = axs[0]
    ax.set_xlim(-0.6, 8.6)
    ax.set_ylim(-3.3, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    _sections(ax, 8)
    support(ax, 4, -0.35, s=0.22)
    for x, lab, val in ((2, "1", r"$P_1=?$"), (7, "2", r"$P_2=40$ Н")):
        ax.plot([x, x], [-0.35, -1.0], color=INK, lw=1.2)
        box(ax, x, -1.35, 0.7, 0.7, lab)
        arrow(ax, (x, -1.75), (x, -2.55), lw=2, ms=11)
        text(ax, x + 0.15, -2.95, val, size=10, color=FORCE)
    dim(ax, 2, 4, 0.95, r"$l_1=2a$", size=10, dy=0.35)
    dim(ax, 4, 7, 0.95, r"$l_2=3a$", size=10, dy=0.35)
    keep_dots(ax.set_title("Задача 13.5"))
    # 13.11
    ax = axs[1]
    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(-3.3, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    _sections(ax, 10)
    support(ax, 8, -0.35, s=0.22)
    for x, lab, val in ((0, "1", r"$m_1=?$"), (10, "2", r"$m_2=?$")):
        ax.plot([x, x], [-0.35, -1.0], color=INK, lw=1.2)
        box(ax, x, -1.35, 0.7, 0.7, lab)
        arrow(ax, (x, -1.75), (x, -2.55), lw=2, ms=11)
        text(ax, x + (0.0 if x else 0.3), -2.95, val, size=10, color=FORCE)
    dim(ax, 0, 8, 0.95, r"$l_1=8a$", size=10, dy=0.35)
    dim(ax, 8, 10, 0.95, r"$l_2=2a$", size=10, dy=0.35)
    keep_dots(ax.set_title(r"Задача 13.11: $m_1+m_2=50$ кг"))
    save(fig, "lever-task-sections.png")


def lever_task_support_shift():
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.9), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axs[0]
    ax.set_xlim(-10, 175)
    ax.set_ylim(-42, 40)
    ax.set_aspect("equal")
    ax.axis("off")
    bar(ax, 0, 165, 0, h=5)
    ax.plot([82.5, 82.5], [-4, 14], color=GREY, lw=1.2, ls="--")
    text(ax, 82.5, 18, "середина", size=9, color=GREY)
    x0 = 82.5 - 37.5
    support(ax, x0, -2.5, s=6)
    for x, lab, col in ((0, r"$m_1=24$ кг", BLUE), (165, r"$m_2=9$ кг", FORCE)):
        ax.plot([x, x], [-2.5, -14], color=INK, lw=1.2)
        box(ax, x, -19, 13, 9, fc=WOOD)
        text(ax, x, -30, lab, size=10, color=col)
    dim(ax, x0, 82.5, 13, r"$x$", size=11, dy=6)
    dim(ax, 0, x0, -35, r"$l_1$", size=10, dy=-7)
    dim(ax, x0, 165, -35, r"$l_2$", size=10, dy=-7)
    ax.set_title(r"Опора смещена к большему грузу, $L=165$ см")
    ax = axs[1]
    k = np.linspace(1, 8, 200)
    x = 82.5 * (k - 1) / (k + 1)
    ax.plot(k, x, color=BLUE, lw=2)
    ax.axhline(82.5, color=GREY, ls="--", lw=1)
    text(ax, 6.7, 85.5, r"$L/2$: опора на краю", size=9, color=GREY)
    ax.scatter([24 / 9], [37.5], color=FORCE, s=70, zorder=5, edgecolor=INK)
    ax.plot([24 / 9] * 2, [0, 37.5], color=FORCE, lw=1, ls=":")
    ax.plot([1, 24 / 9], [37.5] * 2, color=FORCE, lw=1, ls=":")
    text(ax, 24 / 9 + 0.3, 30, "37,5 см", size=10, color=FORCE, ha="left")
    ax.set_xlim(1, 8)
    ax.set_ylim(0, 95)
    ax.set_xlabel(r"отношение масс $m_1/m_2$")
    ax.set_ylabel(r"смещение опоры $x$, см")
    ax.set_title(r"$x=\dfrac{L}{2}\cdot\dfrac{m_1-m_2}{m_1+m_2}$")
    ax.grid(color=GRID, lw=0.8)
    save(fig, "lever-task-support-shift.png")


def lever_task_table_edge():
    fig, ax = canvas(8.6, 3.5, (-2.0, 9.6), (-2.6, 3.4))
    bar(ax, 0, 8.0, 0.0, h=0.3)
    # The lever end rests on the table edge, so the edge is exactly at O (x = 0)
    ax.add_patch(Rectangle((-1.8, -1.6), 1.8, 1.45, fc=WOOD, ec=INK, lw=1.3, zorder=2))
    text(ax, -0.9, -0.9, "стол", size=10)
    ax.add_patch(Circle((0, 0), 0.09, fc=INK, zorder=7))
    text(ax, 0, 0.5, "O", size=11)
    ax.plot([2.0, 2.0], [-0.15, -0.8], color=INK, lw=1.2)
    box(ax, 2.0, -1.25, 1.1, 0.8, "50 кг", size=9)
    arrow(ax, (2.0, -1.7), (2.0, -2.4), lw=2)
    text(ax, 2.55, -2.1, r"$F_1=500$ Н", size=10, color=FORCE, ha="left")
    arrow(ax, (8.0, -0.9), (8.0, -0.17), lw=2.6)
    text(ax, 8.0, -1.25, r"$F_2=125$ Н", size=10, color=FORCE)
    dim(ax, 0, 2.0, 1.5, r"$l_1=0{,}5$ м", size=10, dy=0.4)
    dim(ax, 0, 8.0, 2.55, r"$l_2=L=2$ м", size=10, dy=0.4)
    keep_dots(fig.suptitle("Задача 13.16: сила вверх на конце рычага", fontsize=12, y=0.99))
    save(fig, "lever-task-table-edge.png")


def lever_task_three_loads():
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axs[0]
    ax.set_xlim(-0.8, 8.8)
    ax.set_ylim(-3.6, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")
    _sections(ax, 8)
    support(ax, 4, -0.35, s=0.24)
    arrow(ax, (4, -2.6), (4, -0.7), color=GREEN, lw=2.6)
    text(ax, 5.2, -1.9, r"$N=135$ Н", size=10, color=GREEN)
    loads = [(0, "1", r"$m_1=5{,}5$ кг", 55), (3, "2", r"$m_2=2$ кг", 20), (8, "3", r"$m_3=6$ кг", 60)]
    for x, lab, txt, F in loads:
        ax.plot([x, x], [-0.35, -1.0], color=INK, lw=1.2)
        box(ax, x, -1.35, 0.7, 0.7, lab)
        arrow(ax, (x, -1.75), (x, -2.6), lw=2, ms=11)
        text(ax, x, -3.0, txt, size=9, color=FORCE)
    dim(ax, 0, 4, 1.9, r"$l_1=4a$", size=10, dy=0.4)
    dim(ax, 4, 8, 0.95, r"$l_3=4a$", size=10, dy=0.4)
    dim(ax, 3, 4, 0.95, r"$l_2=a$", size=8, dy=0.4)
    keep_dots(ax.set_title("Задача 13.18: масса груза 1 неизвестна"))
    _moment_bars(
        axs[1],
        [(r"$M_1=220$", 220, BLUE), (r"$M_2=20$", 20, GREEN)],
        [(r"$M_3=240$", 240, FORCE)],
        r"Н$\cdot a$",
    )
    axs[1].set_title("Моменты при $m_1=5{,}5$ кг")
    save(fig, "lever-task-three-loads.png")


def lever_task_heavy_lever():
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axs[0]
    ax.set_xlim(-0.8, 10.8)
    ax.set_ylim(-3.8, 3.8)
    ax.set_aspect("equal")
    ax.axis("off")
    _sections(ax, 10)
    support(ax, 3, -0.35, s=0.24)
    for x, lab, txt in ((1, "1", r"$m_1=10$ кг"), (8, "2", r"$m_2=2$ кг")):
        ax.plot([x, x], [-0.35, -1.0], color=INK, lw=1.2)
        box(ax, x, -1.35, 0.7, 0.7, lab)
        arrow(ax, (x, -1.75), (x, -2.55), lw=2, ms=11)
        text(ax, x, -3.0, txt, size=9, color=FORCE)
    arrow(ax, (5, 1.7), (5, 0.4), color=GREEN, lw=2.4)
    text(ax, 5.25, 1.6, r"$m_р g$, ц. т.", size=10, color=GREEN, ha="left")
    ax.add_patch(Circle((5, 0), 0.09, fc=PAPER, ec=GREEN, zorder=7))
    dim(ax, 1, 3, 1.15, r"$l_1=2a$", size=9, dy=0.35)
    dim(ax, 3, 5, 1.15, r"$l_р=2a$", size=9, dy=0.35)
    dim(ax, 3, 8, 2.9, r"$l_2=5a$", size=9, dy=0.35)
    keep_dots(ax.set_title("Задача 13.19: опора в трёх секциях от левого края"))
    _moment_bars(
        axs[1],
        [(r"$M_1=200$", 200, BLUE)],
        [(r"$M_р=100$", 100, GREEN), (r"$M_2=100$", 100, FORCE)],
        r"Н$\cdot a$",
    )
    axs[1].set_title(r"Моменты при $m_р=5$ кг")
    save(fig, "lever-task-heavy-lever.png")


def lever_task_unequal_scales():
    fig, axs = plt.subplots(2, 1, figsize=(8.2, 6.4))
    cfg = [
        ("Ящик слева, гиря 6 кг справа", "M", "6 кг", r"$M\,l_1=m_1\,l_2$"),
        ("Гиря 24 кг слева, ящик справа", "24 кг", "M", r"$m_2\,l_1=M\,l_2$"),
    ]
    for ax, (title, left, right, eq) in zip(axs, cfg):
        ax.set_xlim(-0.6, 3.6)
        ax.set_ylim(-2.4, 1.6)
        ax.set_aspect("equal")
        ax.axis("off")
        bar(ax, 0, 3.0, 0, h=0.14)
        support(ax, 1.0, -0.07, s=0.13)
        for x, lab in ((0.0, left), (3.0, right)):
            ax.plot([x, x], [-0.07, -0.45], color=INK, lw=1.2)
            fc = WOOD if lab == "M" else LIGHT
            box(ax, x, -0.8, 0.75, 0.6, lab, fc=fc, size=9)
        dim(ax, 0, 1.0, 0.55, r"$l_1$", size=10, dy=0.2)
        dim(ax, 1.0, 3.0, 0.55, r"$l_2$", size=10, dy=0.2)
        text(ax, 1.5, -1.7, eq, size=12)
        ax.set_title(title)
    keep_dots(fig.suptitle(r"Задача 13.17: $M=\sqrt{m_1 m_2}$, здесь $l_2=2\,l_1$", fontsize=12, y=0.99))
    save(fig, "lever-task-unequal-scales.png")


# ---------------------------------------------------------------- pulley


def pulley_fixed():
    fig, ax = canvas(5.6, 5.0, (-2.8, 4.0), (-4.3, 3.4))
    hatch_ceiling(ax, -1.6, 1.6, 3.0)
    ax.plot([0, 0], [3.0, 0], color=INK, lw=3, zorder=2)
    pulley(ax, (0, 0), 1.0)
    rope(ax, [(-1.0, 0), (-1.0, -2.4)])
    rope(ax, [(1.0, 0), (1.0, -2.4)])
    arc_rope(ax, (0, 0), 1.0, 0, 180)
    box(ax, -1.0, -3.0, 0.9, 0.9, "")
    arrow(ax, (-1.0, -3.5), (-1.0, -4.15), color=FORCE, lw=2.4, ms=13)
    text(ax, -1.45, -3.85, r"$\vec P$", size=13, color=FORCE)
    # Fixed block: F = P, so both arrows have the same length (0.65)
    arrow(ax, (1.0, -2.4), (1.0, -3.05), color=FORCE, lw=2.4, ms=13)
    text(ax, 1.5, -2.8, r"$\vec F$", size=13, color=FORCE)
    ax.plot([-1.0, -1.0], [0, -0.0], color=BLUE)
    arrow(ax, (0, 0), (-0.98, 0), color=BLUE, lw=1.5, style="-|>", ms=8)
    arrow(ax, (0, 0), (0.98, 0), color=BLUE, lw=1.5, style="-|>", ms=8)
    # Arm labels sit below the rim, between the ropes, each under its own arrow with a thin leader
    for sx, lab in ((-1, r"$l_1=R$"), (1, r"$l_2=R$")):
        ax.plot([sx * 0.5, sx * 0.5], [-0.04, -1.2], color=BLUE, lw=0.9, ls=(0, (2, 2)), zorder=2)
        text(ax, sx * 0.5, -1.45, lab, size=10, color=BLUE)
    text(ax, 1.9, 1.2, r"$PR=FR$" + "\n" + r"$F=P$", size=12, ha="left")
    save(fig, "pulley-fixed.png")


def pulley_movable():
    fig, ax = canvas(6.2, 6.6, (-2.4, 4.4), (-6.1, 3.6))
    hatch_ceiling(ax, -1.7, -0.3, 3.0)
    rope(ax, [(-1.0, 3.0), (-1.0, 0)])
    arc_rope(ax, (0, 0), 1.0, 180, 360)
    rope(ax, [(1.0, 0), (1.0, 3.0)])
    pulley(ax, (0, 0), 1.0)
    # load on the axle
    rope(ax, [(0, 0), (0, -3.6)])
    box(ax, 0, -4.2, 0.9, 0.9, "")
    # Movable block: F = P/2 (P is 1.0 long, F is 0.5)
    arrow(ax, (0, -4.7), (0, -5.7), color=FORCE, lw=2.4, ms=13)
    text(ax, -0.5, -5.3, r"$\vec P$", size=13, color=FORCE)
    arrow(ax, (1.0, 2.5), (1.0, 3.0), color=FORCE, lw=2.4, ms=13)
    text(ax, 1.5, 2.75, r"$\vec F$", size=13, color=FORCE)
    # instantaneous axis
    ax.add_patch(Circle((-1.0, 0), 0.12, fc=GREEN, ec=INK, zorder=7))
    text(ax, -1.55, 0.35, "ось", size=10, color=GREEN)
    ax.plot([1.0, 1.0], [0, -2.9], color=GREY, lw=1.2, ls="--", zorder=1)
    dim(ax, -1.0, 0, -1.5, r"$l_1=R$", size=10, dy=-0.4)
    dim(ax, -1.0, 1.0, -2.7, r"$l_2=2R$", size=10, dy=-0.4)
    text(ax, 2.0, 0.3, r"$F\cdot 2R=P\cdot R$" + "\n" + r"$F=P/2$", size=12, ha="left")
    save(fig, "pulley-movable.png")


def pulley_combined(name="pulley-combined.png", load="", block="", title=None, dashed=False):
    fig, ax = canvas(6.2, 6.4, (-2.6, 4.6), (-4.7, 4.6))
    hatch_ceiling(ax, -1.7, 3.5, 4.0)
    rope(ax, [(-1.0, 4.0), (-1.0, 0)])
    arc_rope(ax, (0, 0), 1.0, 180, 360)
    pulley(ax, (0, 0), 1.0)
    # fixed pulley
    ax.plot([2.0, 2.0], [4.0, 2.4], color=INK, lw=3, zorder=2)
    fc = (2.0, 2.4)
    pulley(ax, fc, 1.0)
    rope(ax, [(1.0, 0), (1.0, 2.4)])
    arc_rope(ax, fc, 1.0, 0, 180)
    rope(ax, [(3.0, 2.4), (3.0, 0.6)])
    # Movable + fixed block: F = P/2 (P is 0.9 long, F is 0.45)
    arrow(ax, (3.0, 0.6), (3.0, 0.15), color=FORCE, lw=2.4, ms=13)
    text(ax, 3.5, 0.4, r"$\vec F$", size=13, color=FORCE)
    rope(ax, [(0, 0), (0, -2.2)])
    box(ax, 0, -2.8, 1.3 if load else 0.9, 0.9, load, size=9)
    arrow(ax, (0, -3.3), (0, -4.2), color=FORCE, lw=2.4, ms=13)
    text(ax, -0.5, -3.9, r"$\vec P$", size=13, color=FORCE)
    if dashed:
        ax.add_patch(
            Rectangle((-1.35, -3.5), 2.7, 4.75, fc="none", ec=BLUE, lw=1.6, ls="--", zorder=1)
        )
        text(ax, -1.9, -1.1, "одно\nтело", size=9, color=BLUE, ha="right")
    if block:
        text(ax, 0.15, -1.45, "блок " + block, size=8, color=GREY, ha="left")
    keep_dots(fig.suptitle(title or "Подвижный и неподвижный блок вместе", fontsize=12, y=0.99))
    save(fig, name)


def pulley_two_movable():
    fig, ax = canvas(6.2, 8.0, (-3.2, 3.2), (-7.5, 5.4))
    hatch_ceiling(ax, -3.0, -0.3, 4.5)
    # block A (upper)
    A = (0.0, 0.0)
    rope(ax, [(-0.8, 4.5), (-0.8, 0)])
    arc_rope(ax, A, 0.8, 180, 360)
    rope(ax, [(0.8, 0), (0.8, 3.6)])
    pulley(ax, A, 0.8)
    # Two movable blocks: P = 4F (P is 1.6 long, F is 0.4)
    arrow(ax, (0.8, 3.2), (0.8, 3.6), color=FORCE, lw=2.4, ms=13)
    text(ax, 1.3, 3.4, r"$\vec F$", size=13, color=FORCE)
    text(ax, 1.3, 1.5, r"$F$", size=10, color=BLUE)
    text(ax, -1.3, 1.5, r"$F$", size=10, color=BLUE)
    # block B (lower)
    B = (-0.9, -2.6)
    rope(ax, [(-1.8, 4.5), (-1.8, -2.6)])
    arc_rope(ax, B, 0.9, 180, 360)
    rope(ax, [(0.0, -2.6), (0.0, 0.0)])
    pulley(ax, B, 0.9)
    text(ax, -2.35, 1.5, r"$2F$", size=10, color=BLUE)
    text(ax, 0.42, -1.3, r"$2F$", size=10, color=BLUE)
    rope(ax, [B, (B[0], -4.3)])
    box(ax, B[0], -4.85, 0.9, 0.9, "")
    arrow(ax, (B[0], -5.35), (B[0], -6.95), color=FORCE, lw=2.4, ms=13)
    text(ax, B[0] - 0.55, -6.3, r"$\vec P$", size=13, color=FORCE)
    text(ax, 2.1, -3.2, r"$P=4F$", size=13, ha="left")
    save(fig, "pulley-two-movable.png")


def pulley_gain_chain():
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    n = np.arange(0, 5)
    g = 2**n
    ax.bar(n, g, color=[LIGHT, BLUE, BLUE, BLUE, GREY], edgecolor=INK, lw=1.2, width=0.6)
    for x, v in zip(n, g):
        ax.text(x, v + 0.4, str(v), ha="center", fontsize=11)
    ax.set_xticks(n)
    ax.set_xlabel("число подвижных блоков подряд $n$")
    ax.set_ylabel(r"выигрыш в силе $P/F$")
    ax.set_title(r"Выигрыш в силе цепочки: $2^n$")
    ax.set_ylim(0, 19)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "pulley-gain-chain.png")


def pulley_task_gate():
    fig, ax = canvas(6.6, 5.2, (-2.4, 6.4), (-5.5, 2.4))
    ax.add_patch(Circle((0, 0), 1.0, fc=WOOD, ec=INK, lw=2, zorder=3))
    ax.add_patch(Circle((0, 0), 0.09, fc=INK, zorder=6))
    ax.plot([0, 4.0], [0, 0], color=INK, lw=6, solid_capstyle="round", zorder=4)
    ax.plot([0, 4.0], [0, 0], color=GOLD, lw=4, solid_capstyle="round", zorder=4.1)
    rope(ax, [(-1.0, 0), (-1.0, -2.4)])
    box(ax, -1.0, -3.0, 0.9, 0.9, "m")
    # Gate with l = 4R: F = P/4 (P is 1.6 long, F is 0.4)
    arrow(ax, (-1.0, -3.5), (-1.0, -5.1), lw=2.4, ms=12)
    text(ax, -1.5, -4.5, r"$\vec P$", size=13, color=FORCE)
    arrow(ax, (4.0, 0.55), (4.0, 0.15), lw=2.4, ms=12)
    text(ax, 4.5, 0.5, r"$\vec F$", size=13, color=FORCE)
    dim(ax, -1.0, 0, -1.4, r"$R$", size=11, dy=-0.4)
    dim(ax, 0, 4.0, -1.4, r"$l=\alpha R,\ \alpha=4$", size=11, dy=-0.5)
    keep_dots(fig.suptitle("Задача 14.17: ворот", fontsize=12, y=0.99))
    save(fig, "pulley-task-gate.png")


def pulley_task_14_18():
    fig, ax = canvas(7.4, 8.2, (-2.6, 5.2), (-4.6, 6.6))
    hatch_ceiling(ax, -0.9, 4.2, 6.0)
    # fixed pulley
    Fx = (0.0, 5.0)
    R0, R1, R2, R3 = 0.55, 0.55, 0.75, 0.95
    ax.plot([0, 0], [6.0, 5.0], color=INK, lw=3, zorder=2)
    pulley(ax, Fx, R0)
    arc_rope(ax, Fx, R0, 0, 180)
    rope(ax, [(-R0, 5.0), (-R0, 2.6)])
    # F = P/8: F is 0.25 long, P is 2.0
    arrow(ax, (-R0, 3.2), (-R0, 2.95), color=FORCE, lw=2.4, ms=13)
    text(ax, -1.25, 2.9, r"$\vec F$", size=13, color=FORCE)
    text(ax, -1.05, 3.9, r"$F_c$", size=10, color=BLUE)
    text(ax, -0.6, 2.3, "A", size=11, ha="right")
    # M1
    M1 = (1.1, 3.7)
    rope(ax, [(R0, 5.0), (R0, 3.7)])
    arc_rope(ax, M1, R1, 180, 360)
    rope(ax, [(M1[0] + R1, 3.7), (M1[0] + R1, 6.0)])
    pulley(ax, M1, R1)
    text(ax, 1.65 + 0.32, 4.9, r"$P/8$", size=9, color=BLUE)
    text(ax, 0.15, 4.35, r"$P/8$", size=9, color=BLUE)
    text(ax, 1.9, 5.65, "c", size=11, color=GREY)
    # M2
    M2 = (1.85, 2.3)
    rope(ax, [(M1[0], 3.7), (M1[0], 2.3)])
    arc_rope(ax, M2, R2, 180, 360)
    rope(ax, [(M2[0] + R2, 2.3), (M2[0] + R2, 6.0)])
    pulley(ax, M2, R2)
    text(ax, 0.6, 3.0, r"$P/4$", size=9, color=BLUE)
    text(ax, 2.98, 4.0, r"$P/4$", size=9, color=BLUE)
    text(ax, 2.8, 5.65, "b", size=11, color=GREY)
    # M3
    M3 = (2.8, 0.7)
    rope(ax, [(M2[0], 2.3), (M2[0], 0.7)])
    arc_rope(ax, M3, R3, 180, 360)
    rope(ax, [(M3[0] + R3, 0.7), (M3[0] + R3, 6.0)])
    pulley(ax, M3, R3)
    text(ax, 1.4, 1.4, r"$P/2$", size=9, color=BLUE)
    text(ax, 4.45, 3.3, r"$P/2$", size=9, color=BLUE)
    text(ax, 3.95, 5.65, "a", size=11, color=GREY)
    # load
    rope(ax, [M3, (M3[0], -1.3)])
    box(ax, M3[0], -1.85, 0.9, 0.9, "")
    arrow(ax, (M3[0], -2.35), (M3[0], -4.35), color=FORCE, lw=2.4, ms=13)
    text(ax, M3[0] - 0.55, -3.4, r"$\vec P$", size=13, color=FORCE)
    keep_dots(fig.suptitle(r"Задача 14.18: $F=P/8$", fontsize=12, y=0.99))
    save(fig, "pulley-task-14-18.png")


def pulley_task_14_20():
    fig, ax = canvas(10.4, 5.8, (-3.4, 10.6), (-5.4, 5.6))
    hatch_ceiling(ax, -2.4, 1.2, 5.0)
    # movable block with the load 1 (left), fixed block (right)
    Mv = (-1.4, 2.2)
    Fx = (0.2, 4.0)
    ax.plot([Fx[0], Fx[0]], [5.0, 4.0], color=INK, lw=3, zorder=2)
    rope(ax, [(Mv[0] - 0.8, 5.0), (Mv[0] - 0.8, Mv[1])])
    arc_rope(ax, Mv, 0.8, 180, 360)
    rope(ax, [(Mv[0] + 0.8, Mv[1]), (Mv[0] + 0.8, Fx[1])])
    pulley(ax, Mv, 0.8)
    pulley(ax, Fx, 0.8)
    arc_rope(ax, Fx, 0.8, 0, 180)
    ax_x = Fx[0] + 0.8
    rope(ax, [(ax_x, Fx[1]), (ax_x, 0.0)])
    rope(ax, [Mv, (Mv[0], 0.4)])
    box(ax, Mv[0], -0.1, 0.8, 0.8, "1")
    arrow(ax, (Mv[0], -0.6), (Mv[0], -1.5), color=FORCE, lw=2.4, ms=12)
    text(ax, Mv[0] - 0.55, -1.2, r"$\vec P_1$", size=13, color=FORCE)
    text(ax, ax_x + 0.45, 1.6, r"$F$", size=12, color=BLUE)
    # lever: A at x=ax_x, O at right end, length L = 9 (90 cm)
    xA, xO, y = ax_x, ax_x + 9.0, 0.0
    bar(ax, xA, xO, y, h=0.24)
    ax.add_patch(Circle((xO, y), 0.11, fc=INK, zorder=7))
    text(ax, xO + 0.3, y + 0.4, "O", size=12)
    text(ax, xA - 0.05, y + 0.5, "A", size=11, ha="right")
    xB = xO - 3.0
    ax.plot([xB, xB], [y, y - 0.7], color=INK, lw=1.2)
    box(ax, xB, y - 1.15, 0.8, 0.8, "2")
    arrow(ax, (xB, y - 1.6), (xB, y - 2.5), color=FORCE, lw=2.4, ms=12)
    text(ax, xB + 0.55, y - 2.15, r"$\vec P_2$", size=13, color=FORCE)
    text(ax, xB, y + 0.5, "B", size=11)
    dim(ax, xB, xO, -3.1, r"$x=?$", size=11, dy=-0.5)
    dim(ax, xA, xO, -4.3, r"$L=90$ см", size=10, dy=-0.5)
    keep_dots(fig.suptitle("Задача 14.20: блоки поднимают конец рычага", fontsize=12, y=0.98))
    save(fig, "pulley-task-14-20.png")


def main():
    lever_two_kinds()
    lever_arm_construction()
    lever_experiments()
    lever_hyperbola()
    lever_path_force()
    lever_moment_signs()
    lever_moment_balance()
    lever_task_sections()
    lever_task_support_shift()
    lever_task_table_edge()
    lever_task_three_loads()
    lever_task_heavy_lever()
    lever_task_unequal_scales()
    pulley_fixed()
    pulley_movable()
    pulley_combined()
    pulley_combined(
        name="pulley-task-14-13.png",
        load="200 кг",
        block="5 кг",
        title="Задача 14.13: груз и подвижный блок как одно тело",
        dashed=True,
    )
    pulley_two_movable()
    pulley_gain_chain()
    pulley_task_gate()
    pulley_task_14_18()
    pulley_task_14_20()


if __name__ == "__main__":
    main()
