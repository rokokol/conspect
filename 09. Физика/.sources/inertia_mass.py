"""Figures for the notes "Инерция и взаимодействие тел" and "Масса" (course Физика 7-9, lessons 23-26).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 inertia_mass.py
PNG files go to content/04. Инерция, масса, плотность/00. Вложения/
Prefixes: inertia-* for the first note, mass-* for the second.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "04. Инерция, масса, плотность"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
C1 = BLUE  # body 1, light
C2 = RED  # body 2, heavy
C_SPRING = tint(INK, 0.4)
C_LOAD = tint(INK, 0.3)  # a dark metal weight
C_OK = GREEN
C_SAND = tint(WARM, 0.3)
C_WOOD = tint(COPPER, 0.3)
C_WATER = tint(SKY, 0.6)
C_GLASS = tint(SKY, 0.5)
C_METAL = tint(INK, 0.55)  # a steel ball, a metal part
C_PALE_METAL = tint(INK, 0.8)  # a light grey metal part
C_GOLD = WARM  # a coin, the Sun
C_PAPER = tint(WARM, 0.85)


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color,
            shrinkA=0, shrinkB=0, **kw,
        )
    )


def floor(ax, x0, x1, y, color=INK):
    ax.plot([x0, x1], [y, y], color=color, lw=1.6)
    for x in np.arange(x0, x1, 0.35):
        ax.plot([x, x - 0.18], [y, y - 0.18], color=color, lw=0.7)


def cart(ax, x, y, w=1.6, h=0.55, color=C1, load=None, label=None, lab_dy=0.0):
    """Cart with its lower-left corner at (x, y)."""
    r = 0.13
    ax.add_patch(Rectangle((x, y + 2 * r), w, h, fc=tint(color, 0.55), ec=color, lw=1.6))
    for cx in (x + 0.3, x + w - 0.3):
        ax.add_patch(Circle((cx, y + r), r, fc=PAPER, ec=INK, lw=1.2))
    if load:
        lw_ = load
        ax.add_patch(
            Rectangle((x + w / 2 - lw_ / 2, y + 2 * r + h), lw_, lw_ * 0.9,
                      fc=C_LOAD, ec=INK, lw=1.2)
        )
        ax.add_patch(
            Rectangle((x + w / 2 - lw_ / 5, y + 2 * r + h + lw_ * 0.9), lw_ * 0.4, lw_ * 0.3,
                      fc=C_LOAD, ec=INK, lw=1.2)
        )
    if label:
        ax.text(x + w / 2, y + 2 * r + h / 2 + lab_dy, label, ha="center", va="center",
                color=INK, fontsize=12, fontweight="bold")
    return (x + w / 2, y + 2 * r + h)


def spring(ax, x0, x1, y, n=7, amp=0.16, color=C_SPRING):
    xs = np.linspace(x0, x1, 2 * n + 1)
    ys = [y + (amp if i % 2 else -amp) if 0 < i < 2 * n else y for i in range(2 * n + 1)]
    ax.plot(xs, ys, color=color, lw=1.8)


def text_box(ax, x, y, s, color=INK, fs=11, **kw):
    ax.text(x, y, s, ha=kw.pop("ha", "center"), va=kw.pop("va", "center"), color=color,
            fontsize=fs, **kw)


# ---------------------------------------------------------------- inertia-*


def galileo_ramp():
    fig, axes = plt.subplots(3, 1, figsize=(8.4, 7.2))
    cases = [
        ("Песок", C_SAND, 1.0, "≈ 10 см"),
        ("Полотенце", tint(VIOLET, 0.75), 4.0, "≈ 40 см"),
        ("Гладкий стол", LIGHT, 6.6, "движение продолжается"),
    ]
    for ax, (name, col, run, lab) in zip(axes, cases):
        ax.set_xlim(-0.5, 11.5)
        ax.set_ylim(-0.6, 2.9)
        ax.set_aspect("equal")
        ax.axis("off")
        # ramp
        ax.plot([0, 3], [2.2, 0.4], color=INK, lw=2)
        ax.plot([3, 11], [0.4, 0.4], color=INK, lw=2)
        ax.add_patch(Rectangle((3, 0.4 - 0.22), 8, 0.22, fc=col, ec=INK, lw=1, alpha=0.9))
        ax.add_patch(Circle((0.25, 2.2 + 0.2), 0.22, fc=C_METAL, ec=INK, lw=1.2))
        # end of the ramp
        ax.add_patch(Circle((3.0, 0.4 + 0.22), 0.22, fc="none", ec=INK, ls="--", lw=1.2))
        xe = 3.0 + run
        ax.add_patch(Circle((xe, 0.4 + 0.22), 0.22, fc=C_METAL, ec=INK, lw=1.2))
        arrow(ax, (3.35, 1.05), (xe - 0.3, 1.05), color=C2, lw=1.6)
        ax.text(0.1, 0.5, name, fontsize=12, fontweight="bold", va="center")
        ax.text((3.35 + xe) / 2, 1.45, lab, ha="center", fontsize=11, color=C2)
        if run > 5:
            arrow(ax, (xe + 0.35, 1.05), (xe + 1.6, 1.05), color=C2, lw=1.6, ls=":")
            ax.text(xe + 1.9, 1.05, "…", fontsize=16, va="center", color=C2)
    fig.suptitle("Опыты Галилея: одна высота, разные поверхности", y=0.99, fontsize=13)
    fig.tight_layout()
    save(fig, "inertia-galileo-ramp.png")


def velocity_time_no_action():
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    t1, t2, t3 = 2, 5, 8
    ax.plot([0, t1], [0, 0], color=C1, lw=2.6)
    tt = np.linspace(t1, t2, 50)
    ax.plot(tt, 3 * (tt - t1) / (t2 - t1), color=C2, lw=2.6)
    ax.plot([t2, t3], [3, 3], color=C1, lw=2.6)
    tt = np.linspace(t3, 10, 50)
    ax.plot(tt, 3 - 3 * (tt - t3) / (10 - t3), color=C2, lw=2.6)
    ax.axvspan(t1, t2, color=C2, alpha=0.08)
    ax.axvspan(t3, 10, color=C2, alpha=0.08)
    ax.text(1, 0.25, "покой", ha="center", color=C1, fontsize=11)
    ax.text((t1 + t2) / 2, 3.35, "действует\nдругое тело", ha="center", color=C2, fontsize=10)
    ax.text((t2 + t3) / 2, 3.35, "тел нет или\nдействие\nскомпенсировано", ha="center",
            color=C1, fontsize=10)
    ax.text(9, 3.35, "торможение", ha="center", color=C2, fontsize=10)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.3, 4.4)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$v$")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Скорость меняется только под действием тел")
    save(fig, "inertia-velocity-time-action.png")


def compensated_actions():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.9))
    # ball on sand
    ax = axs[0]
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-1.5, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-2.2, -1.0), 4.4, 1.0, fc=C_SAND, ec=INK, lw=1.2))
    ax.add_patch(Circle((0, 0.55), 0.55, fc=C_METAL, ec=INK, lw=1.4))
    arrow(ax, (0, 0.55), (0, -0.55 - 0.55), color=C2, lw=2.2)
    arrow(ax, (0, 0.55), (0, 0.55 + 1.1), color=C1, lw=2.2)
    ax.text(0.25, -0.55, "Земля", color=C2, fontsize=11, va="center")
    ax.text(0.25, 1.65, "песок", color=C1, fontsize=11, va="center")
    ax.text(0, 2.75, "Шар на песке: $v = 0$", ha="center", fontsize=12)
    ax.text(0, -1.35, "два действия компенсируют друг друга", ha="center", fontsize=10, color=INK)
    # ball on thread
    ax = axs[1]
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-1.5, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-1.2, 1.2], [2.4, 2.4], color=INK, lw=3)
    ax.plot([0, 0], [2.4, 1.1], color=INK, lw=1.4)
    ax.add_patch(Circle((0, 0.55), 0.55, fc=C_METAL, ec=INK, lw=1.4))
    arrow(ax, (0, 0.55), (0, -0.55 - 0.55), color=C2, lw=2.2)
    arrow(ax, (0, 0.55), (0, 0.55 + 0.75), color=C1, lw=2.2)
    ax.text(0.25, -0.55, "Земля", color=C2, fontsize=11, va="center")
    ax.text(0.25, 1.35, "нить", color=C1, fontsize=11, va="center")
    ax.text(0, 2.75, "Шар на нити: $v = 0$", ha="center", fontsize=12)
    ax.text(0, -1.35, "перережем нить: остаётся одно действие", ha="center", fontsize=10)
    fig.tight_layout()
    save(fig, "inertia-compensated-actions.png")


def carts_scene(name, title, m2_load, v1, v2, note):
    """Before/after scene of two carts; v1 to the left, v2 to the right (lengths in units)."""
    fig, ax = blank(9.4, 4.6, (-6.4, 6.4), (-0.4, 5.6))
    # before row
    yb = 3.55
    ax.plot([-5.4, 5.4], [yb, yb], color=INK, lw=1.2)
    ax.text(-6.3, yb + 1.05, "до", fontsize=12, style="italic")
    cart(ax, -1.75, yb, color=C1, label="1")
    cart(ax, 0.15, yb, color=C2, label="2", load=m2_load)
    spring(ax, -0.15, 0.15, yb + 0.55, n=3, amp=0.12)
    ax.text(0, yb + 1.55 + (0.5 if m2_load else 0), "сжатая пружина, нить", ha="center",
            fontsize=10, color=C_SPRING)
    # after row
    ya = 0.7
    ax.plot([-5.4, 5.4], [ya, ya], color=INK, lw=1.2)
    ax.text(-6.3, ya + 1.05, "после", fontsize=12, style="italic")
    x1 = -1.75 - 0.6 * v1
    x2 = 0.15 + 0.6 * v2
    c1 = cart(ax, x1, ya, color=C1, label="1")
    c2 = cart(ax, x2, ya, color=C2, label="2", load=m2_load)
    s = 0.45
    arrow(ax, (c1[0] - 0.8, ya + 0.75), (c1[0] - 0.8 - s * v1, ya + 0.75), color=INK, lw=2.4)
    arrow(ax, (c2[0] + 0.8, ya + 0.75), (c2[0] + 0.8 + s * v2, ya + 0.75), color=INK, lw=2.4)
    ax.text(c1[0] - 0.8 - s * v1 / 2, ya + 1.15, "$\\vec v_1$", ha="center", fontsize=13)
    ax.text(c2[0] + 0.8 + s * v2 / 2, ya + 1.15, "$\\vec v_2$", ha="center", fontsize=13)
    ax.text(0, -0.15, note, ha="center", fontsize=12, color=C2)
    ax.set_title(title, fontsize=13, pad=14)
    save(fig, name)


def coin_card():
    fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.4))
    titles = ["Монета на картонке", "Картонку выбивают", "Монета в банке"]
    for i, ax in enumerate(axs):
        ax.set_xlim(-3, 3)
        ax.set_ylim(-0.4, 4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[i], fontsize=11)
        # jar
        ax.add_patch(Rectangle((-1.1, 0), 2.2, 2.2, fc=C_GLASS, ec=INK, lw=1.3, alpha=0.35))
        ax.plot([-1.1, 1.1], [2.2, 2.2], color=INK, lw=1.3)
    # panel 1
    ax = axs[0]
    ax.add_patch(Rectangle((-1.6, 2.2), 3.2, 0.1, fc=LIGHT, ec=INK, lw=1.2))
    ax.add_patch(Circle((0, 2.5), 0.2, fc=C_GOLD, ec=INK, lw=1.2))
    # panel 2
    ax = axs[1]
    ax.add_patch(Rectangle((-0.6, 2.2), 3.2, 0.1, fc=LIGHT, ec=INK, lw=1.2))
    arrow(ax, (1.4, 3.0), (2.6, 3.0), color=C2, lw=2.4)
    ax.text(2.0, 3.35, "быстро", color=C2, ha="center", fontsize=10)
    ax.add_patch(Circle((0, 2.5), 0.2, fc=C_GOLD, ec=INK, lw=1.2))
    ax.text(0, 3.45, "монета почти не успела\nизменить скорость", ha="center", fontsize=9)
    # panel 3
    ax = axs[2]
    ax.add_patch(Circle((0, 0.3), 0.2, fc=C_GOLD, ec=INK, lw=1.2))
    arrow(ax, (0, 2.4), (0, 0.7), color=INK, lw=1.2, ls="--")
    fig.tight_layout()
    save(fig, "inertia-coin-card.png")


def velocity_build_up():
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    t = np.linspace(0, 6, 300)
    tau = 2.0
    v_light = np.where(t < tau, 3.0 * t / tau, 3.0)
    v_heavy = np.where(t < tau, 1.5 * t / tau, 1.5)
    ax.plot(t, v_light, color=C1, lw=2.6, label="лёгкая тележка")
    ax.plot(t, v_heavy, color=C2, lw=2.6, label="нагруженная тележка")
    ax.plot([0, 0, 6], [0, 0, 0], color=INK, lw=0.6)
    ax.axvline(tau, color=GRID, lw=1.5, ls="--")
    ax.text(tau + 0.1, 3.4, "пружина\nраспрямилась", fontsize=9, color=INK, va="top")
    ax.annotate("", xy=(0.0, 3.4), xytext=(tau, 3.4), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(tau / 2, 3.5, "взаимодействие", ha="center", fontsize=9)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$|v|$")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Скорость набирается постепенно")
    ax.legend(loc="center right", frameon=False)
    save(fig, "inertia-velocity-build-up.png")


def students_carts():
    fig, ax = blank(9.0, 3.4, (-5.8, 5.8), (-0.6, 3.2))
    floor(ax, -4.8, 4.8, 0.0)
    # light student goes far, heavy student goes near
    for x, col, lab in [(-3.6, C1, "меньшая инертность"), (1.6, C2, "большая инертность")]:
        pass
    # heavy: near centre
    # light student far left
    x1, x2 = -3.4, 1.4
    for x, col in [(x1, C1), (x2, C2)]:
        ax.add_patch(Rectangle((x, 0.28), 1.5, 0.16, fc=LIGHT, ec=INK, lw=1.2))
        ax.add_patch(Circle((x + 0.35, 0.16), 0.12, fc=PAPER, ec=INK))
        ax.add_patch(Circle((x + 1.15, 0.16), 0.12, fc=PAPER, ec=INK))
        ax.add_patch(Rectangle((x + 0.45, 0.44), 0.6, 1.2, fc=col, ec=INK, lw=1.2, alpha=0.85))
        ax.add_patch(Circle((x + 0.75, 1.9), 0.26, fc=tint(WARM, 0.4), ec=INK, lw=1.2))
    arrow(ax, (x1 + 0.2, 2.35), (x1 - 1.5, 2.35), color=INK, lw=2.6)
    arrow(ax, (x2 + 1.3, 2.35), (x2 + 1.9, 2.35), color=INK, lw=2.6)
    ax.text(x1 - 0.7, 2.75, "скорость изменилась\nсильнее", ha="center", fontsize=9)
    ax.text(x2 + 1.6, 2.75, "изменилась\nменьше", ha="center", fontsize=9)
    ax.text(x1 + 0.75, -0.45, "инертность меньше", ha="center", color=C1, fontsize=10)
    ax.text(x2 + 0.75, -0.45, "инертность больше", ha="center", color=C2, fontsize=10)
    ax.set_title("Два ученика на тележках отталкиваются ладонями")
    save(fig, "inertia-students-carts.png")


def balloon():
    fig, ax = blank(7.8, 3.6, (-4, 4), (-1.8, 1.8))
    # balloon body
    ax.add_patch(Circle((0.6, 0), 0.9, fc=tint(RED, 0.6), ec=INK, lw=1.5))
    ax.add_patch(Polygon([[-0.3, -0.12], [-0.7, -0.3], [-0.7, 0.3], [-0.3, 0.12]], fc=tint(RED, 0.6),
                         ec=INK, lw=1.5))
    # air jet
    for dy in (-0.35, 0, 0.35):
        arrow(ax, (-0.9, dy * 0.8), (-2.7 - abs(dy) * 1.2, dy * 1.1), color=C1, lw=1.6)
    arrow(ax, (1.6, 0), (3.5, 0), color=C2, lw=2.6)
    ax.text(-1.9, 1.05, "воздух уходит назад", ha="center", color=C1, fontsize=11)
    ax.text(2.6, 0.5, "шарик летит вперёд", ha="center", color=C2, fontsize=11)
    ax.set_title("Шарик и воздух взаимодействуют: упругая резина — как пружина")
    save(fig, "inertia-balloon.png")


def problem_wagons_stop():
    fig, ax = blank(10.0, 3.9, (-0.5, 10.5), (0.3, 5.2))
    # before
    yb, ya = 3.2, 0.9
    ax.plot([0, 10], [yb, yb], color=INK, lw=1.2)
    ax.plot([0, 10], [ya, ya], color=INK, lw=1.2)
    ax.text(-0.4, yb + 1.0, "до", fontsize=12, style="italic")
    ax.text(-0.4, ya + 1.0, "после", fontsize=12, style="italic")
    cart(ax, 1.4, yb, w=2.4, h=0.8, color=C1)
    cart(ax, 6.0, yb, w=2.4, h=0.8, color=C2)
    ax.text(2.6, yb + 0.6, "$m_1 = 80$ т", ha="center", va="center", color=INK, fontsize=11)
    ax.text(7.2, yb + 0.6, "$m_2 = ?$", ha="center", va="center", color=INK, fontsize=11)
    arrow(ax, (2.6, yb + 1.55), (4.2, yb + 1.55), color=INK, lw=2.4)
    arrow(ax, (7.2, yb + 1.55), (6.2, yb + 1.55), color=INK, lw=2.4)
    ax.text(3.4, yb + 1.9, "$v_1 = +0{,}2$ м/с", ha="center", fontsize=11)
    ax.text(6.7, yb + 1.9, "$v_2 = -0{,}5$ м/с", ha="center", fontsize=11)
    # both stop at the same moment: the second wagon's path is v2/v1 = 2.5 times the first's,
    # so the 2.2 gap closes as d + 2.5 d with d = 0.63
    cart(ax, 2.03, ya, w=2.4, h=0.8, color=C1)
    cart(ax, 4.43, ya, w=2.4, h=0.8, color=C2)
    ax.text(4.43, ya + 1.6, "после сцепки $v_1' = v_2' = 0$", ha="center", fontsize=11)
    arrow(ax, (0.3, 5.0), (1.5, 5.0), color=INK, lw=1.4)
    ax.text(1.7, 5.0, "$x$", va="center", fontsize=12)
    save(fig, "inertia-problem-wagons-stop.png")


def problem_three_wagons():
    fig, ax = blank(11.8, 4.4, (-0.5, 12.3), (-0.1, 5.9))
    yb, ya = 3.5, 0.8
    ax.plot([0, 12], [yb, yb], color=INK, lw=1.2)
    ax.plot([0, 12], [ya, ya], color=INK, lw=1.2)
    ax.text(-0.4, yb + 1.0, "до", fontsize=12, style="italic")
    ax.text(-0.4, ya + 1.0, "после", fontsize=12, style="italic")
    cart(ax, 0.8, yb, w=2.0, h=0.8, color=C1)
    cart(ax, 5.2, yb, w=2.0, h=0.8, color=C2)
    cart(ax, 7.2, yb, w=2.0, h=0.8, color=C2)
    for x, lab in [(1.8, "$m$"), (6.2, "$m$"), (8.2, "$m$")]:
        ax.text(x, yb + 0.6, lab, ha="center", va="center", color=INK, fontsize=12)
    ax.plot([5.2, 9.2], [yb + 1.5, yb + 1.5], color=INK, lw=1)
    ax.text(7.2, yb + 1.75, "$2m$", ha="center", fontsize=12)
    arrow(ax, (1.8, yb + 1.55), (3.6, yb + 1.55), color=INK, lw=2.4)
    ax.text(2.7, yb + 1.9, "$\\vec v$", ha="center", fontsize=12)
    # after the coupling the three wagons have moved on to the right of the pair's old place
    cart(ax, 5.6, ya, w=2.0, h=0.8, color=C1)
    cart(ax, 7.6, ya, w=2.0, h=0.8, color=C2)
    cart(ax, 9.6, ya, w=2.0, h=0.8, color=C2)
    arrow(ax, (8.1, ya + 1.55), (9.1, ya + 1.55), color=INK, lw=2.4)
    ax.text(8.6, ya + 1.95, "$\\vec v'\\ ?$", ha="center", fontsize=12)
    ax.text(2.6, ya + 0.6, "$v' = \\dfrac{v}{3}$", ha="center", va="center", fontsize=13, color=C2)
    arrow(ax, (10.4, 0.2), (11.6, 0.2), color=INK, lw=1.4)
    ax.text(11.75, 0.2, "$x$", va="center", fontsize=12)
    ax.text(10.2, 0.2, "запад", va="center", ha="right", fontsize=10)
    save(fig, "inertia-problem-three-wagons.png")


def problem_bullet():
    fig, ax = blank(10.0, 4.0, (-0.5, 10.5), (-0.6, 4.6))
    yb, ya = 2.9, 0.6
    for y, cap in [(yb, "до"), (ya, "после")]:
        ax.plot([0, 10], [y, y], color=INK, lw=1.2)
        ax.text(-0.4, y + 0.95, cap, fontsize=12, style="italic")
    ax.add_patch(Rectangle((5.0, yb), 2.0, 0.9, fc=C_WOOD, ec=INK, lw=1.4))
    ax.text(6.0, yb + 0.45, "$m_б$", ha="center", va="center", fontsize=12)
    # bullet: body on the left, point forward (to the right)
    ax.add_patch(Polygon([[1.5, yb + 0.5], [1.0, yb + 0.35], [1.0, yb + 0.65]], fc=C2, ec=INK))
    ax.add_patch(Rectangle((0.6, yb + 0.35), 0.4, 0.3, fc=C2, ec=INK))
    arrow(ax, (1.8, yb + 0.5), (4.2, yb + 0.5), color=INK, lw=2.4)
    ax.text(3.0, yb + 0.85, "$v_п = 300$ м/с", ha="center", fontsize=11)
    ax.text(1.0, yb - 0.3, "$m_п = 50$ г", ha="center", fontsize=10)
    # the block has moved right, along its velocity
    ax.add_patch(Rectangle((5.6, ya), 2.0, 0.9, fc=C_WOOD, ec=INK, lw=1.4))
    ax.plot([5.6, 7.6], [ya + 0.45, ya + 0.45], color=INK, lw=1, ls="--")
    ax.add_patch(Polygon([[9.0, ya + 0.5], [8.5, ya + 0.35], [8.5, ya + 0.65]], fc=C2, ec=INK))
    ax.add_patch(Rectangle((8.1, ya + 0.35), 0.4, 0.3, fc=C2, ec=INK))
    arrow(ax, (6.3, ya + 1.2), (7.5, ya + 1.2), color=INK, lw=2.4)
    ax.text(6.9, ya + 1.55, "$v_б'\\ ?$", ha="center", fontsize=12)
    arrow(ax, (8.6, ya + 1.2), (9.6, ya + 1.2), color=INK, lw=2.4)
    ax.text(9.1, ya + 1.55, "$v_п' = 100$ м/с", ha="center", fontsize=10)
    save(fig, "inertia-problem-bullet-block.png")


# -------------------------------------------------------------------- mass-*


def ratio_rows():
    """Carts of masses 1:1, 1:2, 1:4 after pushing apart: speeds inversely proportional."""
    fig, ax = blank(9.4, 5.2, (-6, 6), (1.2, 8.2))
    rows = [(1, 1, 3.0, 3.0), (1, 2, 3.0, 1.5), (1, 4, 3.0, 0.75)]
    y = 6.4
    for m1, m2, v1, v2 in rows:
        ax.plot([-5.8, 5.8], [y, y], color=INK, lw=1.0)
        c1x = -0.9 - 0.4 * v1 - 0.8
        c2x = 0.9 + 0.4 * v2 - 0.8 + 0.2
        w2 = 1.2 + 0.4 * (m2 - 1) if m2 <= 2 else 2.4
        # cart 2 widens with mass
        cart(ax, c1x, y, w=1.2, h=0.5, color=C1)
        cart(ax, c2x, y, w=w2 + 0.4, h=0.5, color=C2)
        ax.text(c1x + 0.6, y + 0.55, "$m_1$", ha="center", va="center", color=INK, fontsize=11)
        ax.text(c2x + (w2 + 0.4) / 2, y + 0.55, f"${m2}m_1$" if m2 > 1 else "$m_1$",
                ha="center", va="center", color=INK, fontsize=11)
        arrow(ax, (c1x + 0.6, y + 1.35), (c1x + 0.6 - 0.55 * v1, y + 1.35), color=INK, lw=2.4)
        arrow(ax, (c2x + (w2 + 0.4) / 2, y + 1.35), (c2x + (w2 + 0.4) / 2 + 0.55 * v2, y + 1.35),
              color=INK, lw=2.4)
        ax.text(-5.7, y + 1.0, f"$m_2/m_1 = {m2}$", fontsize=12, va="center")
        ax.text(5.7, y + 1.0, f"$v_1/v_2 = {int(v1 / v2) if v1 / v2 == int(v1 / v2) else v1 / v2:g}$",
                fontsize=12, va="center", ha="right", color=C2)
        y -= 2.2
    ax.set_title("Во сколько раз масса больше, во столько раз скорость меньше", fontsize=12)
    save(fig, "mass-carts-ratio.png")


def ratio_line():
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    x = np.linspace(0, 5, 10)
    ax.plot(x, x, color=C2, lw=2.4)
    pts = [(1, 1), (2, 2), (4, 4), (0.5, 0.5)]
    for px, py in pts:
        ax.plot(px, py, "o", color=C1, ms=8, zorder=3)
    ax.plot([0, 2], [2, 2], color=GRID, ls="--", lw=1.2)
    ax.plot([2, 2], [0, 2], color=GRID, ls="--", lw=1.2)
    ax.text(2.1, 1.65, "$m_2 = 2m_1$\n$v_1 = 2v_2$", fontsize=10, color=INK)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_xlabel("$m_2 / m_1$")
    ax.set_ylabel("$|v_1| / |v_2|$")
    ax.set_title("Отношение скоростей — прямая через начало")
    ax.grid(color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    save(fig, "mass-ratio-line.png")


def interaction_strength():
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
    # left: three interactions, same carts (m2 = 2 m1)
    ax = axs[0]
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.3, 6.6)
    ax.set_aspect("equal")
    ax.axis("off")
    rows = [("слабая пружина", 1.0), ("тугая пружина", 2.0), ("пороховой заряд", 3.5)]
    y = 4.6
    for name, v2 in rows:
        v1 = 2 * v2
        ax.plot([-4.9, 4.9], [y, y], color=INK, lw=1.0)
        w1, w2 = 1.0, 1.7
        c1x = -0.3 - 0.22 * v1 - w1
        c2x = 0.3 + 0.22 * v2
        cart(ax, c1x, y, w=w1, h=0.4, color=C1)
        cart(ax, c2x, y, w=w2, h=0.4, color=C2)
        arrow(ax, (c1x + w1 / 2, y + 1.0), (c1x + w1 / 2 - 0.2 * v1, y + 1.0), color=INK, lw=2.2)
        arrow(ax, (c2x + w2 / 2, y + 1.0), (c2x + w2 / 2 + 0.2 * v2, y + 1.0), color=INK, lw=2.2)
        ax.text(-4.8, y + 1.35, name, fontsize=10, color=INK)
        y -= 2.1
    ax.set_title("Одни и те же тележки, разное взаимодействие", fontsize=11)
    # right: v1 vs v2
    ax = axs[1]
    v2s = np.array([0, 5])
    ax.plot(v2s, 2 * v2s, color=C2, lw=2.4)
    for name, v2 in rows:
        ax.plot(v2, 2 * v2, "o", color=C1, ms=9, zorder=3)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 10)
    ax.set_xlabel("$|v_2|$")
    ax.set_ylabel("$|v_1|$")
    ax.text(3.2, 4.0, "$|v_1| = \\dfrac{m_2}{m_1}\\,|v_2|$", fontsize=11, color=C2)
    ax.grid(color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    ax.set_title("Скорости разные, отношение одно и то же", fontsize=11)
    fig.tight_layout()
    save(fig, "mass-interaction-strength.png")


def mass_from_ratio():
    fig, ax = blank(9.2, 3.4, (-5.5, 5.5), (-0.4, 3.4))
    y = 0.6
    ax.plot([-5.4, 5.4], [y, y], color=INK, lw=1.2)
    cart(ax, -3.3, y, w=1.5, h=0.5, color=C1)
    cart(ax, 1.2, y, w=2.2, h=0.5, color=C2)
    ax.text(-2.55, y + 0.51, "$m_{эт}$", ha="center", va="center", color=INK, fontsize=11)
    ax.text(2.3, y + 0.51, "$m_{тела}$", ha="center", va="center", color=INK, fontsize=11)
    ax.text(-2.55, y - 0.55, "эталон", ha="center", fontsize=10)
    ax.text(2.3, y - 0.55, "взвешиваемое тело", ha="center", fontsize=10)
    arrow(ax, (-2.55, y + 1.5), (-4.75, y + 1.5), color=INK, lw=2.4)
    arrow(ax, (2.3, y + 1.5), (3.2, y + 1.5), color=INK, lw=2.4)
    ax.text(-3.65, y + 1.85, "$v_{эт}$", ha="center", fontsize=13)
    ax.text(2.75, y + 1.85, "$v_{тела}$", ha="center", fontsize=13)
    ax.text(0, 2.85, "$m_{тела} = m_{эт}\\cdot\\dfrac{v_{эт}}{v_{тела}}$", ha="center", fontsize=14)
    save(fig, "mass-etalon-measurement.png")


def axis_signs():
    fig, ax = blank(9.0, 3.0, (-5.5, 5.5), (-0.5, 3.0))
    y = 0.6
    arrow(ax, (-5.2, y), (5.2, y), color=INK, lw=1.6)
    ax.text(5.2, y - 0.4, "$x$", fontsize=13)
    cart(ax, -3.2, y, w=1.3, h=0.5, color=C1, label="1")
    cart(ax, 1.8, y, w=1.3, h=0.5, color=C2, label="2")
    arrow(ax, (-2.55, y + 1.5), (-4.4, y + 1.5), color=INK, lw=2.4)
    arrow(ax, (2.45, y + 1.5), (4.3, y + 1.5), color=INK, lw=2.4)
    ax.text(-3.5, y + 1.9, "$v_1 < 0$: против оси", ha="center", fontsize=11, color=C1)
    ax.text(3.4, y + 1.9, "$v_2 > 0$: вдоль оси", ha="center", fontsize=11, color=C2)
    save(fig, "mass-axis-signs.png")


def delta_scale():
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ax.set_xlim(34, 46)
    ax.set_ylim(-1.6, 1.8)
    ax.axis("off")
    ax.plot([35, 45], [0, 0], color=INK, lw=1.4)
    for x in range(35, 46):
        ax.plot([x, x], [-0.08, 0.08], color=INK, lw=1)
        if x % 1 == 0 and x in (36, 38, 40, 42, 44):
            ax.text(x, -0.35, str(x), ha="center", fontsize=10)
    ax.text(45.6, -0.35, "кг", ha="center", fontsize=10)
    ax.annotate("", xy=(38, 0.9), xytext=(40, 0.9),
                arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.2))
    ax.text(39, 1.2, "$\\Delta m = 38 - 40 = -2$ кг", ha="center", color=C1, fontsize=11)
    ax.annotate("", xy=(42, -0.9), xytext=(38, -0.9),
                arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2))
    ax.text(40, -1.35, "$\\Delta m = 42 - 38 = +4$ кг", ha="center", color=C2, fontsize=11)
    ax.set_title("Изменение = конечное значение − начальное")
    save(fig, "mass-delta-scale.png")


def billiard():
    fig, ax = blank(9.2, 3.8, (-5.4, 5.4), (-0.5, 3.6))
    for y, cap in [(2.6, "до"), (0.5, "после")]:
        ax.plot([-5.2, 5.2], [y, y], color=INK, lw=1.0, ls=":")
        ax.text(-5.2, y + 0.45, cap, fontsize=12, style="italic")
    r = 0.4
    ax.add_patch(Circle((-3.4, 2.6 + r), r, fc=tint(C1, 0.55), ec=INK, lw=1.3))
    ax.add_patch(Circle((1.4, 2.6 + r), r, fc=tint(C2, 0.55), ec=INK, lw=1.3))
    arrow(ax, (-2.8, 3.0), (-1.2, 3.0), color=INK, lw=2.4)
    ax.text(-2.0, 3.3, "$\\vec v_1$", ha="center", fontsize=13)
    ax.add_patch(Circle((-1.3, 0.5 + r), r, fc=tint(C1, 0.55), ec=INK, lw=1.3))
    ax.add_patch(Circle((3.0, 0.5 + r), r, fc=tint(C2, 0.55), ec=INK, lw=1.3))
    ax.text(-1.3, 1.4, "$v_1' = 0$", ha="center", fontsize=12, color=C1)
    arrow(ax, (3.6, 0.9), (5.0, 0.9), color=INK, lw=2.4)
    ax.text(4.3, 1.25, "$\\vec v_2' = \\vec v_1$", ha="center", fontsize=12)
    ax.text(0, -0.25, "$m_1 = m_2$", ha="center", fontsize=12)
    save(fig, "mass-billiard.png")


def exoplanet():
    fig, ax = blank(6.2, 5.2, (-3.4, 3.4), (-3.2, 3.2))
    th = np.linspace(0, 2 * np.pi, 200)
    # centre of mass at origin, star radius 0.4, planet radius 2.5 (m_star/m_planet = 6.25)
    ax.plot(2.5 * np.cos(th), 2.5 * np.sin(th), color=C1, lw=1.4)
    ax.plot(0.4 * np.cos(th), 0.4 * np.sin(th), color=C2, lw=1.4)
    ax.add_patch(Circle((-0.4 * np.cos(0.8), -0.4 * np.sin(0.8)), 0.2, fc=C_GOLD, ec=INK, lw=1.3))
    ax.add_patch(Circle((2.5 * np.cos(0.8), 2.5 * np.sin(0.8)), 0.12, fc=C1, ec=INK, lw=1.2))
    ax.plot([0], [0], "+", color=INK, ms=10, mew=1.6)
    ax.text(0.5, -0.1, "центр масс", fontsize=8, va="top")
    ax.text(2.7 * np.cos(0.8), 2.7 * np.sin(0.8) + 0.25, "планета", ha="center", color=C1, fontsize=11)
    ax.text(-1.15, -1.0, "звезда", ha="center", color=C2, fontsize=11)
    ax.text(0, -3.0, "Звезда описывает малый круг, планета — большой: радиусы\nобратно пропорциональны массам",
            ha="center", fontsize=9)
    ax.set_title("Экзопланету находят по движению звезды", fontsize=12)
    save(fig, "mass-exoplanet-wobble.png")


def balance(ax, cx, cy, theta_deg=0.0, left=None, right=None, scale=1.0, label_parts=False):
    """Draw a beam balance. Positive theta: right pan down. left/right: lists of pan contents."""
    L = 2.6 * scale
    th = np.radians(theta_deg)
    # stand
    ax.add_patch(Polygon([[cx - 0.5 * scale, cy - 2.6 * scale], [cx + 0.5 * scale, cy - 2.6 * scale],
                          [cx, cy]], fc=C_PALE_METAL, ec=INK, lw=1.3))
    ax.plot([cx - 1.0 * scale, cx + 1.0 * scale], [cy - 2.6 * scale] * 2, color=INK, lw=2.4)
    # beam
    lx, ly = cx - L * np.cos(th), cy + L * np.sin(th)
    rx, ry = cx + L * np.cos(th), cy - L * np.sin(th)
    ax.plot([lx, rx], [ly, ry], color=INK, lw=3.4, solid_capstyle="round")
    ax.add_patch(Circle((cx, cy), 0.11 * scale, fc=PAPER, ec=INK, lw=1.4, zorder=4))
    # pointer
    px, py = cx + 0.9 * scale * np.sin(th), cy + 0.9 * scale * np.cos(th)
    ax.plot([cx, px], [cy, py], color=C2, lw=2.2)
    # fixed zero mark
    ax.plot([cx, cx], [cy + 1.05 * scale, cy + 1.25 * scale], color=INK, lw=1.4)
    # pans
    h = 1.6 * scale
    pw = 1.0 * scale
    for (x, y, items, side) in [(lx, ly, left, "L"), (rx, ry, right, "R")]:
        ax.plot([x, x - pw * 0.9], [y, y - h], color=INK, lw=1.0)
        ax.plot([x, x + pw * 0.9], [y, y - h], color=INK, lw=1.0)
        ax.plot([x - pw, x + pw], [y - h, y - h], color=INK, lw=2.6, solid_capstyle="round")
        ax.add_patch(Wedge((x, y - h), pw, 180, 360, fc=LIGHT, ec=INK, lw=1.0, alpha=0.55))
        if items:
            draw_items(ax, x, y - h, items, side, scale)
    return (lx, ly), (rx, ry)


def draw_items(ax, x, y, items, side, scale):
    """Items: list of (kind, label). Stacked on the pan."""
    cur_x = x - 0.5 * scale
    for kind, label in items:
        if kind == "body":
            ax.add_patch(Rectangle((x - 0.35 * scale, y), 0.7 * scale, 0.65 * scale,
                                   fc=C_METAL, ec=INK, lw=1.2))
            if label:
                ax.text(x, y + 0.33 * scale, label, ha="center", va="center", fontsize=8 * scale,
                        color=INK)
        elif kind == "weight":
            w = 0.34 * scale
            ax.add_patch(Rectangle((cur_x, y), w, 0.36 * scale, fc=C_LOAD, ec=INK, lw=1.0))
            ax.add_patch(Rectangle((cur_x + w * 0.3, y + 0.36 * scale), w * 0.4, 0.12 * scale,
                                   fc=C_LOAD, ec=INK, lw=1.0))
            if label:
                ax.text(cur_x + w / 2, y + 0.75 * scale, label, ha="center", fontsize=6.5 * scale)
            cur_x += w + 0.06 * scale
        elif kind == "sand":
            ax.add_patch(Polygon([[x - 0.55 * scale, y + 0.16 * scale * (label == "on_paper")],
                                  [x + 0.55 * scale, y + 0.16 * scale * (label == "on_paper")],
                                  [x, y + 0.6 * scale]],
                                 fc=C_SAND, ec=INK, lw=1.0))
        elif kind == "sand_small":
            ax.add_patch(Polygon([[x - 0.3 * scale, y + 0.16 * scale],
                                  [x + 0.3 * scale, y + 0.16 * scale], [x, y + 0.36 * scale]],
                                 fc=C_SAND, ec=INK, lw=1.0))
        elif kind == "sand_side":
            ax.add_patch(Polygon([[x - 0.75 * scale, y], [x - 0.05 * scale, y],
                                  [x - 0.4 * scale, y + 0.45 * scale]], fc=C_SAND, ec=INK, lw=1.0))
            cur_x = x + 0.1 * scale
        elif kind == "paper_bits":
            for dx in (-0.25, 0.05, 0.3):
                ax.add_patch(Rectangle((x + dx * scale, y), 0.18 * scale, 0.05 * scale,
                                       fc=C_PAPER, ec=INK, lw=0.8))
        elif kind == "glass":
            ax.add_patch(Rectangle((x - 0.32 * scale, y), 0.64 * scale, 0.78 * scale,
                                   fc=C_GLASS, ec=INK, lw=1.2, alpha=0.6))
            if label == "water":
                ax.add_patch(Rectangle((x - 0.32 * scale, y), 0.64 * scale, 0.5 * scale,
                                       fc=C_WATER, ec="none"))
        elif kind == "paper":
            ax.add_patch(Polygon([[x - 0.5 * scale, y], [x + 0.5 * scale, y],
                                  [x + 0.35 * scale, y + 0.16 * scale],
                                  [x - 0.35 * scale, y + 0.16 * scale]], fc=C_PAPER, ec=INK, lw=1.0))


def balance_parts():
    fig, ax = blank(8.6, 6.4, (-5.6, 5.6), (-4.0, 3.6))
    balance(ax, 0, 0.6, 0.0, left=[("body", "тело")],
            right=[("weight", ""), ("weight", ""), ("weight", "")], scale=1.25)
    ax.annotate("коромысло", (-1.4, 0.6), (-4.6, 2.2), fontsize=11,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    ax.annotate("указатель", (0.0, 1.75), (2.4, 3.0), fontsize=11,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    ax.annotate("опора", (0.0, -1.0), (2.3, -1.8), fontsize=11,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    ax.text(-3.6, -3.5, "левая чашка:\nвзвешиваемое тело", ha="center", fontsize=10, color=INK)
    ax.text(3.6, -3.5, "правая чашка:\nгири", ha="center", fontsize=10, color=INK)
    save(fig, "mass-balance-parts.png")


def weight_set():
    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.2, 6.6)
    ax.axis("off")
    rows = [
        ["100 г"],
        ["50 г", "20 г", "20 г", "10 г"],
        ["5 г", "2 г", "2 г", "1 г"],
        ["500 мг", "200 мг", "200 мг", "100 мг"],
        ["50 мг", "20 мг", "20 мг", "10 мг"],
    ]
    sizes = {"100 г": 0.62, "50 г": 0.52, "20 г": 0.44, "10 г": 0.38, "5 г": 0.33, "2 г": 0.29,
             "1 г": 0.26, "500 мг": 0.31, "200 мг": 0.27, "100 мг": 0.24, "50 мг": 0.21,
             "20 мг": 0.18, "10 мг": 0.16}
    y = 5.8
    for row in rows:
        n = len(row)
        for i, lab in enumerate(row):
            x = 3.0 + i * 1.8 if n > 1 else 3.0
            r = sizes[lab] * 0.85
            mg = "мг" in lab
            ax.add_patch(Circle((x, y), r, fc=C_PALE_METAL if not mg else tint(WARM, 0.6), ec=INK, lw=1.3))
            ax.text(x, y, lab.split()[0], ha="center", va="center", fontsize=9, fontweight="bold")
            ax.text(x, y - r - 0.1, lab, ha="center", va="top", fontsize=8, color=INK)
        y -= 1.3
    ax.text(0.15, 5.8, "граммовые", fontsize=10, color=INK, va="center")
    ax.text(0.15, 1.9, "миллиграммовые\n(пинцетом)", fontsize=10, color=INK, va="center")
    ax.plot([0.1, 9.9], [3.55, 3.55], color=GRID, lw=1.2)
    ax.set_title("Набор гирь лабораторных весов")
    save(fig, "mass-weight-set.png")


def weighing_sequence():
    """Mini balances for the weighing of the cylinder: 52.55 g."""
    steps = [
        ("100 г", "много", 12),
        ("50 г", "мало", -8),
        ("50 + 20 г", "много", 12),
        ("50 + 10 г", "много", 12),
        ("50 + 5 г", "много", 12),
        ("50 + 2 г", "мало", -5),
        ("50 + 2 + 2 г", "много", 10),
        ("50 + 2 + 1 г", "много", 8),
        ("52 г + 500 мг", "мало", -3),
        ("52,5 г + 200 мг", "много", 5),
        ("52,5 г + 100 мг", "много", 3),
        ("52,5 г + 50 мг", "равновесие", 0),
    ]
    fig, axs = plt.subplots(3, 4, figsize=(11.2, 8.0))
    for i, (ax, (lab, verdict, th)) in enumerate(zip(axs.ravel(), steps)):
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-2.7, 3.2)
        ax.set_aspect("equal")
        ax.axis("off")
        balance(ax, 0, 1.0, th * 0.6, left=[("body", "")], right=[("weight", "")], scale=0.95)
        col = C_OK if verdict == "равновесие" else (C2 if verdict == "много" else C1)
        ax.text(0, 2.9, f"{i + 1}. {lab}", ha="center", fontsize=10.5, fontweight="bold")
        ax.text(0, -2.35, verdict, ha="center", fontsize=11, color=col, fontweight="bold")
    fig.suptitle("Взвешивание цилиндра: гири берут от большей к меньшей", fontsize=13, y=0.995)
    fig.tight_layout()
    save(fig, "mass-weighing-sequence.png")


def weighing_convergence():
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    target = 52.55
    kept = [50, 2, 0.5, 0.05]
    rem = [target]
    for k in kept:
        rem.append(rem[-1] - k)
    rem[-1] = 0.0
    labels = ["старт", "+50 г", "+2 г", "+500 мг", "+50 мг"]
    xs = np.arange(len(rem))
    ax.semilogy(xs[:-1], rem[:-1], "o-", color=C1, lw=2.4, ms=8)
    for x, r in zip(xs[:-1], rem[:-1]):
        ax.annotate(num(r, None) + " г", (x, r), textcoords="offset points", xytext=(6, 8), fontsize=10)
    # zero has no place on a log axis: the last step drops out through the bottom edge
    bottom = 0.007
    ax.plot([xs[-2], xs[-1]], [rem[-2], bottom], color=C1, lw=2.4, ls="--")
    ax.plot(xs[-1], bottom, "v", color=C1, ms=11, clip_on=False, zorder=5)
    ax.text(xs[-1], bottom * 2.6, "равновесие:\n0 г", ha="center", va="bottom", fontsize=10)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylabel("недобранная масса, г")
    ax.set_ylim(bottom, 120)
    ax.grid(color=GRID, lw=0.7, which="both")
    ax.set_axisbelow(True)
    ax.set_title("Оставленные гири сводят недобор к нулю")
    save(fig, "mass-weighing-convergence.png")


def sand_boat():
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.9))
    titles = ["1. Лодочку уравновешивают", "2. Гиря 10 г, досыпают песок", "3. Стрелка на нуле"]
    for ax, t in zip(axs, titles):
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-2.6, 3.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(t, fontsize=10.5)
    balance(axs[0], 0, 1.0, 0, left=[("paper", "")], right=[("paper_bits", "")], scale=0.95)
    balance(axs[1], 0, 1.0, 5, left=[("paper", ""), ("sand_small", "")],
            right=[("weight", "10 г")], scale=0.95)
    balance(axs[2], 0, 1.0, 0, left=[("paper", ""), ("sand", "on_paper")],
            right=[("weight", "10 г")], scale=0.95)
    fig.tight_layout()
    save(fig, "mass-sand-boat.png")


def liquid_counterweight():
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.9))
    titles = ["1. Стакан против песка", "2. Наливают воду", "3. Гири на правой чашке"]
    for ax, t in zip(axs, titles):
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-2.6, 3.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(t, fontsize=10.5)
    balance(axs[0], 0, 1.0, 0, left=[("glass", "")], right=[("sand", "")], scale=0.95)
    balance(axs[1], 0, 1.0, -6, left=[("glass", "water")], right=[("sand", "")], scale=0.95)
    balance(axs[2], 0, 1.0, 0, left=[("glass", "water")],
            right=[("sand_side", ""), ("weight", ""), ("weight", "")], scale=0.95)
    fig.tight_layout()
    save(fig, "mass-liquid-counterweight.png")


def weights_decomposition():
    fig, axs = plt.subplots(2, 1, figsize=(10.0, 4.6))
    data = [
        ("$m = 115{,}86$ г", [("100 г", 1.0), ("10 г", 0.7), ("5 г", 0.6), ("500 мг", 0.5),
                              ("200 мг", 0.45), ("100 мг", 0.4), ("50 мг", 0.35), ("10 мг", 0.3)]),
        ("$m = 99{,}99$ г", [("50 г", 0.9), ("20 г", 0.8), ("20 г", 0.8), ("5 г", 0.6), ("2 г", 0.5),
                             ("2 г", 0.5), ("500 мг", 0.45), ("200 мг", 0.4), ("200 мг", 0.4),
                             ("50 мг", 0.3), ("20 мг", 0.28), ("20 мг", 0.28)]),
    ]
    for ax, (title, ws) in zip(axs, data):
        ax.set_xlim(-0.5, 14)
        ax.set_ylim(-0.9, 1.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.text(-0.4, 0.95, title, fontsize=12, fontweight="bold", va="center")
        x = 0.6
        for lab, r in ws:
            r *= 0.5
            mg = "мг" in lab
            ax.add_patch(Circle((x + r, 0), r, fc=tint(WARM, 0.6) if mg else C_PALE_METAL, ec=INK, lw=1.2))
            ax.text(x + r, -r - 0.25, lab, ha="center", va="top", fontsize=8.5)
            x += 2 * r + 0.45
    fig.suptitle("Разложение массы на гири набора", fontsize=13)
    fig.tight_layout()
    save(fig, "mass-weights-decomposition.png")


def chain_of_etalons():
    fig, ax = blank(9.2, 3.2, (-0.3, 9.5), (-0.3, 3.0))
    boxes = [(0.2, "тело 2\n(неизвестная масса)"), (3.4, "тело 1\n(масса известна)"),
             (6.6, "эталон\n$m_{эт} = 1$ кг")]
    for i, (x, lab) in enumerate(boxes):
        ax.add_patch(Rectangle((x, 0.8), 2.6, 1.3, fc=LIGHT if i < 2 else tint(WARM, 0.6), ec=INK, lw=1.4))
        ax.text(x + 1.3, 1.45, lab, ha="center", va="center", fontsize=10)
    arrow(ax, (3.0, 1.45), (3.4, 1.45), color=C2, lw=2.0, style="<|-|>")
    arrow(ax, (6.2, 1.45), (6.6, 1.45), color=C2, lw=2.0, style="<|-|>")
    ax.text(3.2, 2.55, "?", ha="center", fontsize=16, color=C2)
    ax.text(6.4, 2.55, "?", ha="center", fontsize=16, color=C2)
    ax.text(4.75, 0.2, "чтобы узнать массу тела, нужно тело с известной массой;\nвыход — эталон, масса которого равна единице по договорённости",
            ha="center", va="center", fontsize=9.5)
    save(fig, "mass-etalon-chain.png")


if __name__ == "__main__":
    galileo_ramp()
    velocity_time_no_action()
    compensated_actions()
    carts_scene("inertia-carts-equal.png", "Одинаковые тележки: скорости равны по модулю", None, 3.0, 3.0,
                "$|v_1| = |v_2|$")
    carts_scene("inertia-carts-loaded.png", "Правая тележка с гирей: её скорость меньше", 0.55, 3.0, 1.5,
                "$|v_1| > |v_2|$, инертность второй тележки больше")
    coin_card()
    velocity_build_up()
    students_carts()
    balloon()
    problem_wagons_stop()
    problem_three_wagons()
    problem_bullet()
    ratio_rows()
    ratio_line()
    interaction_strength()
    mass_from_ratio()
    axis_signs()
    delta_scale()
    billiard()
    exoplanet()
    balance_parts()
    weight_set()
    weighing_sequence()
    weighing_convergence()
    sand_boat()
    liquid_counterweight()
    weights_decomposition()
    chain_of_etalons()
