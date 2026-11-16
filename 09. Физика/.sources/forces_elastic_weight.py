"""Figures for the notes "Сила упругости. Закон Гука" and "Вес тела" (course Физика 7-9, lessons 34-37).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 forces_elastic_weight.py
PNG files go to content/05. Силы/00. Вложения/
Prefixes: elastic-* (lessons 34, 35 problems), dynamometer-* (lesson 35), weight-* (lessons 36, 37).
Colour code of the forces, the same in every picture: gravity red, elastic force green, weight blue.
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
    / "05. Силы"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
NOMEDIA = OUT / ".nomedia"
if not NOMEDIA.exists():
    NOMEDIA.touch()

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
GREY = tint(INK, 0.4)  # small notes and the marker of an expected value
C_GRAV = RED  # force of gravity
C_ELAS = GREEN  # elastic force
C_WEIGHT = BLUE  # weight
C_BODY = tint(WARM, 0.3)
C_WOOD = tint(COPPER, 0.3)
C_WATER = tint(SKY, 0.6)
C_STEEL = tint(INK, 0.6)
BODY_PALE = tint(WARM, 0.6)  # a pale body on a scale or a spring
SCALE_PANEL = tint(WARM, 0.85)  # the plate of a dynamometer or a ruler

FT = r"$\vec{F}_{\mathrm{т}}$"
FU = r"$\vec{F}_{\mathrm{упр}}$"
PV = r"$\vec{P}$"


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=2.2, style="-|>", scale=15, **kw):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color,
            shrinkA=0, shrinkB=0, **kw,
        )
    )


def txt(ax, x, y, s, color=INK, fs=11, ha="center", va="center", **kw):
    ax.text(x, y, s, ha=ha, va=va, color=color, fontsize=fs, **kw)


def hatch_floor(ax, x0, x1, y, color=INK, n=None, down=0.18):
    ax.plot([x0, x1], [y, y], color=color, lw=1.6)
    for x in np.arange(x0 + 0.2, x1, 0.3):
        ax.plot([x, x - down], [y, y - down], color=color, lw=0.7)


def hatch_wall(ax, x, y0, y1, color=INK, side=-1):
    ax.plot([x, x], [y0, y1], color=color, lw=1.6)
    for y in np.arange(y0 + 0.15, y1, 0.3):
        ax.plot([x, x + side * 0.18], [y, y + 0.15], color=color, lw=0.7)


def coil(ax, x, y_top, y_bot, n=8, amp=0.32, color=GREY, lw=2.0):
    """Vertical spring between y_top and y_bot centred on x."""
    ys = np.linspace(y_top, y_bot, 4 * n + 1)
    xs = x + amp * np.sin(np.linspace(0, 2 * np.pi * n, 4 * n + 1))
    ax.plot(xs, ys, color=color, lw=lw)


def graph_axes(w, h, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig, ax


# =================================================================== elastic-*


def elastic_ruler_weight():
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.2))
    cases = [
        ("Гиря только опустилась", 0.15, 0.4),
        ("Равновесие", 0.5, 1.4),
        ("Придавили и отпустили", 0.85, 2.2),
    ]
    x = np.linspace(0, 6, 80)
    for ax, (title, d, fu) in zip(axes, cases):
        ax.set_xlim(-0.6, 6.6)
        ax.set_ylim(-2.7, 2.9)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=12)
        for sx in (0, 6):
            ax.add_patch(Polygon([[sx - 0.3, -1.0], [sx + 0.3, -1.0], [sx, 0]], fc=LIGHT, ec=INK, lw=1.3))
        ax.plot([-0.6, 6.6], [-1.0, -1.0], color=INK, lw=1.6)
        ax.plot(x, np.zeros_like(x), color=INK, lw=1.2, ls="--")
        y = -d * (1 - ((x - 3) / 3) ** 2)
        ax.plot(x, y, color=C_WOOD, lw=5, solid_capstyle="round")
        ytop = -d + 0.06
        ax.add_patch(Rectangle((2.6, ytop), 0.8, 0.8, fc=C_STEEL, ec=INK, lw=1.3))
        cy = ytop + 0.4
        ax.plot([3], [cy], "o", color=INK, ms=4)
        arrow(ax, (3, cy), (3, cy - 1.4), color=C_GRAV)
        arrow(ax, (3, ytop), (3, ytop + fu), color=C_ELAS)
        txt(ax, 3.55, cy - 1.3, FT, C_GRAV, 13, ha="left")
        txt(ax, 3.55, ytop + fu, FU, C_ELAS, 13, ha="left")
        txt(ax, 6.55, 0.15, "исходное\nположение", GREY, 9, ha="right", va="bottom")
    axes[0].text(3, -2.5, "сила упругости меньше силы тяжести", ha="center", fontsize=9.5, color=INK)
    axes[1].text(3, -2.5, "силы уравновешивают друг друга", ha="center", fontsize=9.5, color=INK)
    axes[2].text(3, -2.5, "сила упругости больше силы тяжести", ha="center", fontsize=9.5, color=INK)
    save(fig, "elastic-ruler-weight.png")


def elastic_deformation_types():
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 6.6))
    for ax in axes.flat:
        ax.set_xlim(-0.3, 5.3)
        ax.set_ylim(-0.9, 3.2)
        ax.set_aspect("equal")
        ax.axis("off")

    def disp(ax, p, q):
        arrow(ax, p, q, color=GREY, lw=1.8, ls="--")

    # stretch
    ax = axes[0, 0]
    ax.set_title("Растяжение")
    hatch_wall(ax, 0.2, 0.2, 1.6)
    ax.add_patch(Rectangle((0.2, 0.5), 2.6, 0.7, fc="none", ec=GREY, ls="--", lw=1.3))
    ax.add_patch(Rectangle((0.2, 0.5), 3.4, 0.7, fc=BODY_PALE, ec=INK, lw=1.5))
    disp(ax, (3.6, 1.35), (4.4, 1.35))
    arrow(ax, (3.6, 0.85), (2.5, 0.85), color=C_ELAS)
    txt(ax, 3.05, 0.35, FU, C_ELAS, 13)
    txt(ax, 4.0, 1.75, "смещение\nчастиц", GREY, 9.5)
    txt(ax, 1.4, -0.3, r"$\Delta l>0$", INK, 12)
    # compression
    ax = axes[0, 1]
    ax.set_title("Сжатие")
    hatch_wall(ax, 0.2, 0.2, 1.6)
    ax.add_patch(Rectangle((0.2, 0.5), 3.4, 0.7, fc="none", ec=GREY, ls="--", lw=1.3))
    ax.add_patch(Rectangle((0.2, 0.5), 2.4, 0.7, fc=BODY_PALE, ec=INK, lw=1.5))
    disp(ax, (2.6, 1.35), (1.8, 1.35))
    arrow(ax, (2.6, 0.85), (3.7, 0.85), color=C_ELAS)
    txt(ax, 3.4, 0.35, FU, C_ELAS, 13)
    txt(ax, 2.2, 1.85, "смещение\nчастиц", GREY, 9.5)
    txt(ax, 1.4, -0.3, r"$\Delta l<0$", INK, 12)
    # bending
    ax = axes[0, 2]
    ax.set_title("Изгиб")
    x = np.linspace(0.3, 4.7, 60)
    ax.plot(x, np.zeros_like(x) + 0.9, color=GREY, ls="--", lw=1.3)
    y = 0.9 - 0.7 * (1 - ((x - 2.5) / 2.2) ** 2)
    ax.plot(x, y, color=C_WOOD, lw=5, solid_capstyle="round")
    for sx in (0.3, 4.7):
        ax.add_patch(Polygon([[sx - 0.25, 0.0], [sx + 0.25, 0.0], [sx, 0.85]], fc=LIGHT, ec=INK, lw=1.2))
    disp(ax, (2.5, 0.75), (2.5, -0.1))
    arrow(ax, (1.7, 0.4), (1.7, 1.5), color=C_ELAS)
    txt(ax, 1.05, 1.5, FU, C_ELAS, 13)
    txt(ax, 3.4, -0.35, "смещение частиц", GREY, 9.5)
    # shear
    ax = axes[1, 0]
    ax.set_title("Сдвиг")
    ax.plot([0.2, 4.6], [0.2, 0.2], color=INK, lw=2)
    for xx in np.arange(0.3, 4.6, 0.3):
        ax.plot([xx, xx - 0.18], [0.2, 0.02], color=INK, lw=0.7)
    ax.add_patch(Rectangle((1.0, 0.2), 2.2, 1.6, fc="none", ec=GREY, ls="--", lw=1.3))
    ax.add_patch(Polygon([[1.0, 0.2], [3.2, 0.2], [3.9, 1.8], [1.7, 1.8]], fc=BODY_PALE, ec=INK, lw=1.5))
    disp(ax, (2.0, 2.05), (3.0, 2.05))
    arrow(ax, (3.9, 1.5), (2.7, 1.5), color=C_ELAS)
    txt(ax, 2.9, 1.05, FU, C_ELAS, 13)
    txt(ax, 3.9, 2.05, "смещение\nчастиц", GREY, 9.5, ha="left")
    # torsion
    ax = axes[1, 1]
    ax.set_title("Кручение")
    ax.plot([0.9, 3.9], [0.2, 0.2], color=INK, lw=2)
    for xx in np.arange(1.0, 3.9, 0.3):
        ax.plot([xx, xx - 0.18], [0.2, 0.02], color=INK, lw=0.7)
    ax.add_patch(Rectangle((1.4, 0.2), 1.6, 1.8, fc="none", ec=GREY, ls="--", lw=1.3))
    ax.add_patch(Polygon([[1.4, 0.2], [3.0, 0.2], [3.45, 2.0], [1.85, 2.0]], fc=BODY_PALE, ec=INK, lw=1.5))
    for xx in np.linspace(1.6, 2.8, 4):
        ax.plot([xx, xx], [0.2, 2.0], color=GREY, ls="--", lw=1.0)
        ax.plot([xx, xx + 0.45], [0.2, 2.0], color=INK, lw=1.2)
    arrow(ax, (2.9, 2.35), (1.9, 2.35), color=C_ELAS)
    arrow(ax, (1.9, 2.7), (2.9, 2.7), color=C_ELAS)
    txt(ax, 3.15, 2.35, r"$\vec{F}_{1}$", C_ELAS, 12, ha="left")
    txt(ax, 3.15, 2.7, r"$\vec{F}_{2}$", C_ELAS, 12, ha="left")
    txt(ax, 2.2, -0.35, "пара сил упругости", GREY, 10)
    # legend panel
    ax = axes[1, 2]
    ax.set_title("Обозначения")
    disp(ax, (0.5, 1.7), (1.6, 1.7))
    txt(ax, 1.9, 1.7, "смещение частиц тела при деформации", INK, 10, ha="left")
    arrow(ax, (0.5, 0.9), (1.6, 0.9), color=C_ELAS)
    txt(ax, 1.9, 0.9, "сила упругости, направлена\nпротив смещения частиц", INK, 10, ha="left")
    ax.add_patch(Rectangle((0.5, -0.05), 1.1, 0.3, fc="none", ec=GREY, ls="--", lw=1.3))
    txt(ax, 1.9, 0.1, "недеформированное состояние", INK, 10, ha="left")
    ax.set_xlim(-0.3, 7.3)
    save(fig, "elastic-deformation-types.png")


def elastic_plastic():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0), sharey=True)
    # elastic
    ax = axes[0]
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Упругая деформация")
    ax.plot([0, 0.95], [0, 0.95], color=C_ELAS, lw=2.4)
    ax.annotate("", xy=(0.62, 0.62), xytext=(0.45, 0.45), arrowprops=dict(arrowstyle="-|>", color=C_ELAS, lw=2))
    ax.annotate("", xy=(0.4, 0.4), xytext=(0.55, 0.55), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=2, ls="--"))
    txt(ax, 0.72, 0.35, "нагрузка и разгрузка\nидут по одной линии", INK, 9.5, ha="left")
    ax.plot([0], [0], "o", color=INK)
    txt(ax, 0.06, -0.08, "форма восстановлена", INK, 9.5, ha="left")
    # plastic
    ax = axes[1]
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Пластическая деформация")
    ax.plot([0, 0.5, 1.0], [0, 0.5, 0.8], color=C_GRAV, lw=2.4)
    # unloading runs parallel to the elastic part (slope 1): from (1.0, 0.8) down to (0.2, 0)
    ax.plot([1.0, 0.2], [0.8, 0.0], color=GREY, lw=2.2, ls="--")
    ax.plot([0.2], [0.0], "o", color=INK)
    ax.annotate("", xy=(0.58, 0.38), xytext=(0.74, 0.54), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=2))
    ax.plot([0.5], [0.5], "o", mfc=PAPER, mec=C_GRAV, ms=8, mew=2)
    txt(ax, 0.44, 0.58, "предел\nупругости", C_GRAV, 9.5, ha="right")
    txt(ax, 0.22, -0.08, "остаточная деформация", INK, 9.5, ha="left")
    txt(ax, 0.66, 0.22, "разгрузка", GREY, 9.5, ha="left")
    for ax in axes:
        ax.set_xlabel(r"удлинение $\Delta l$")
        ax.set_xlim(-0.05, 1.15)
        ax.set_ylim(-0.15, 1.1)
        ax.set_xticks([])
        ax.set_yticks([])
    axes[0].set_ylabel(r"сила упругости $F_{\mathrm{упр}}$")
    save(fig, "elastic-plastic.png")


def elastic_hooke_data():
    # lesson 34: 5, 10, 15, 20 g -> 2, 4, 6, 8 mm; 100 g -> 60 mm instead of the predicted 40 mm
    dl = np.array([2, 4, 6, 8])
    F = np.array([0.05, 0.10, 0.15, 0.20])
    fig, ax = graph_axes(8.2, 5.0, r"удлинение $\Delta l$, мм", r"сила упругости $F_{\mathrm{упр}}$, Н")
    ax.axvspan(0, 10, color=tint(GREEN, 0.85), alpha=0.8)
    ax.text(5, 1.12, "малые\nдеформации", ha="center", va="center", fontsize=9.5, color=C_ELAS)
    ax.plot([0, 40], [0, 1.0], color=GREY, ls="--", lw=1.6)
    ax.plot(dl, F, "o", color=C_ELAS, ms=8, label="измерения: 5, 10, 15, 20 г")
    ax.plot([0, 8], [0, 0.2], color=C_ELAS, lw=2.6)
    ax.plot([40], [1.0], "o", mfc=PAPER, mec=GREY, ms=9, label="ожидали по закону Гука: 40 мм")
    ax.plot([60], [1.0], "o", color=C_GRAV, ms=9, label="получили для 100 г: 60 мм")
    ax.annotate("", xy=(58, 1.0), xytext=(42, 1.0), arrowprops=dict(arrowstyle="-|>", color=C_GRAV, lw=1.6))
    ax.text(30, 0.5, r"$k = \dfrac{0{,}1}{0{,}004}\ \mathrm{Н/м} = 25\ \mathrm{Н/м}$", fontsize=11, color=INK, rotation=0)
    ax.set_xlim(0, 70)
    ax.set_ylim(0, 1.25)
    ax.legend(loc="lower right", fontsize=9, frameon=True)
    save(fig, "elastic-hooke-data.png")


def elastic_hooke_stiffness():
    fig, ax = graph_axes(8.6, 5.4, r"удлинение $\Delta l$, см", r"сила упругости $F_{\mathrm{упр}}$, Н")
    springs = [(20, 6.0, BLUE), (50, 4.0, VIOLET), (100, 3.0, RED)]
    for k, lim, col in springs:
        d = np.linspace(0, lim, 50)
        F = k * d / 100
        ax.plot(d, F, color=col, lw=2.6)
        d2 = np.linspace(lim, lim * 1.55, 40)
        F2 = k * lim / 100 + 0.35 * k / 100 * (d2 - lim) * (1 - 0.5 * (d2 - lim) / lim)
        ax.plot(d2, F2, color=col, lw=2.0, ls=(0, (3, 2)))
        ax.plot([lim], [k * lim / 100], "o", color=col, ms=9, mfc=PAPER, mew=2)
        ax.text(lim * 1.57, F2[-1], rf"$k={k}\ \mathrm{{Н/м}}$", color=col, fontsize=11, va="center")
    ax.text(7.0, 3.4, "сплошная линия: закон Гука\nпунктир: за пределом упругости\nкружок: предел упругости", fontsize=9.5, va="top")
    # slope triangle for the stiffest spring
    ax.plot([2.0, 4.0, 4.0], [0.4, 0.4, 0.8], color=GREY, lw=1.2)
    ax.text(3.0, 0.32, r"$\Delta l$", ha="center", va="top", fontsize=10, color=GREY)
    ax.text(4.1, 0.6, r"$\Delta F$", ha="left", va="center", fontsize=10, color=GREY)
    ax.text(5.0, 0.35, r"$k=\dfrac{\Delta F}{\Delta l}$ — наклон прямой", ha="left", va="center", fontsize=10, color=GREY)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.5)
    save(fig, "elastic-hooke-stiffness.png")


def elastic_hooke_abs():
    fig, ax = graph_axes(7.4, 4.6, r"удлинение $\Delta l$, мм", r"модуль силы упругости $|\vec{F}_{\mathrm{упр}}|$, Н")
    d = np.linspace(-8, 8, 100)
    ax.plot(d, 0.025 * np.abs(d), color=C_ELAS, lw=2.6)
    ax.axvline(0, color=INK, lw=1)
    ax.text(-4, 0.235, "сжатие\n" + r"$\Delta l<0$", ha="center", fontsize=10.5)
    ax.text(4, 0.235, "растяжение\n" + r"$\Delta l>0$", ha="center", fontsize=10.5)
    ax.text(0.0, 0.11, r"$F_{\mathrm{упр}}=k\,|\Delta l|$", ha="center", fontsize=12, color=C_ELAS)
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(0, 0.28)
    save(fig, "elastic-hooke-abs.png")


def elastic_rubber_setup():
    # true scale in centimetres: the thread is 15 cm long; the ruler zero is at the pointer clip
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 8.4))
    l0 = 15.0
    cases = [("Без груза", 0.0, None, ""), ("Гиря 10 г", 0.4, None, r"$\Delta l=4\ \mathrm{мм}$"),
             ("Гиря 100 г", 6.0, 4.0, r"$\Delta l=60\ \mathrm{мм}$")]
    for ax, (title, dl, pred, lab) in zip(axes, cases):
        ax.set_xlim(-4.6, 4.2)
        ax.set_ylim(-l0 - 9.4, 1.8)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=12)
        ax.plot([-1.0, 1.0], [1.0, 1.0], color=INK, lw=2)
        ax.add_patch(Rectangle((-0.35, 0.1), 0.7, 0.9, fc=tint(COPPER, 0.5), ec=INK, lw=1.3))
        ax.plot([0, 0], [0.1, -l0 - dl], color=COPPER, lw=2.4)
        ax.add_patch(Rectangle((-0.3, -l0 - dl - 0.15), 0.6, 0.3, fc=tint(COPPER, 0.5), ec=INK, lw=1.2, zorder=3))
        yb = -l0 - dl - 1.2
        ax.plot([0, 0], [-l0 - dl, yb + 0.4], color=GREY, lw=1.2)
        ax.add_patch(Polygon([[-0.7, yb + 0.4], [0.7, yb + 0.4], [0.4, yb - 0.2], [-0.4, yb - 0.2]], fc=LIGHT, ec=INK, lw=1.2))
        # ruler with the zero at the initial position of the clip
        ax.add_patch(Rectangle((1.3, -l0 - 7.4), 1.0, 7.8, fc=SCALE_PANEL, ec=INK, lw=1.2))
        for i in range(0, 8):
            ax.plot([1.3, 1.9], [-l0 - i, -l0 - i], color=INK, lw=1)
            ax.text(2.4, -l0 - i, str(i * 10), fontsize=8, va="center")
        txt(ax, 2.6, -l0 + 0.7, "мм", INK, 8)
        ax.plot([0.3, 1.3], [-l0 - dl, -l0 - dl], color=C_GRAV, lw=1.2)
        if lab:
            # the arrow stays left of the "expected" label next to the thread
            ax.annotate("", xy=(-2.2, -l0 - dl), xytext=(-2.2, -l0),
                        arrowprops=dict(arrowstyle="<->", color=C_GRAV, lw=1.5))
            txt(ax, -2.4, -l0 - dl / 2 - 0.9, lab, C_GRAV, 10, ha="right")
        if pred:
            ax.plot([-0.3, 1.3], [-l0 - pred, -l0 - pred], color=GREY, lw=1.0, ls="--")
            txt(ax, -0.5, -l0 - pred - 0.9, "ожидали\n40 мм", GREY, 8.5, ha="right")
    save(fig, "elastic-rubber-setup.png")


def elastic_hanging_spring():
    fig, ax = blank(5.6, 6.2, (-1.2, 4.6), (-6.4, 0.9))
    ax.plot([-0.9, 0.9], [0.5, 0.5], color=INK, lw=2)
    for xx in np.arange(-0.8, 0.9, 0.3):
        ax.plot([xx, xx + 0.15], [0.5, 0.7], color=INK, lw=0.7)
    ax.add_patch(Rectangle((-0.4, -2.7), 0.8, 0.9, fc="none", ec=GREY, ls="--", lw=1.3))
    coil(ax, 0, 0.5, -3.6, n=6)
    ax.add_patch(Rectangle((-0.4, -4.5), 0.8, 0.9, fc=C_STEEL, ec=INK, lw=1.4))
    txt(ax, 0, -4.05, r"$m$", INK, 12)
    ax.plot([0], [-4.05], "o", color=INK, ms=0)
    # forces
    ax.plot([1.0], [-4.05], "o", color=INK, ms=4)
    arrow(ax, (1.0, -4.05), (1.0, -5.55), color=C_GRAV)
    arrow(ax, (1.0, -3.6), (1.0, -2.1), color=C_ELAS)
    txt(ax, 1.25, -5.4, FT, C_GRAV, 13, ha="left")
    txt(ax, 1.25, -2.2, FU, C_ELAS, 13, ha="left")
    ax.annotate("", xy=(-1.0, -3.6), xytext=(-1.0, -1.8), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    txt(ax, -1.1, -2.7, r"$\Delta l$", INK, 13, ha="right")
    txt(ax, 2.2, -1.9, "пунктир: положение\nгруза до растяжения", GREY, 9.5, ha="left")
    save(fig, "elastic-hanging-spring.png")


def elastic_problem_11_15():
    fig, ax = graph_axes(7.4, 5.2, r"растягивающая сила $F$, Н", r"длина пружины $l$, см")
    F = np.array([0, 40])
    ax.plot(F, 16 + F / 2, color=C_ELAS, lw=2.6)
    ax.axhline(36, xmax=1, color=GREY, ls="--", lw=1)
    ax.text(1, 36.6, r"$l=36\ \mathrm{см}$ при $F=40\ \mathrm{Н}$", fontsize=9.5, color=GREY)
    ax.text(1, 14.6, r"$l_0=16\ \mathrm{см}$", fontsize=9.5, color=GREY, va="top")
    for dl, Fv, col in ((12, 24, VIOLET), (17, 34, C_GRAV)):
        l = 16 + dl
        ax.plot([0, Fv, Fv], [l, l, 0], color=col, ls=":", lw=1.4)
        ax.plot([Fv], [l], "o", color=col, ms=8)
        ax.text(Fv + 0.8, l - 2.2, rf"$\Delta l={dl}\ \mathrm{{см}}$" + "\n" + rf"$F={Fv}\ \mathrm{{Н}}$", color=col, fontsize=10.5, va="top")
    ax.set_xlim(0, 46)
    ax.set_ylim(0, 40)
    ax.set_xticks(range(0, 46, 10))
    ax.set_yticks(range(0, 41, 8))
    save(fig, "elastic-problem-11-15.png")


# ============================================================== dynamometer-*


def dyn_body(ax, x, y_top, h, w=1.1, ticks=None, ptr=None, unit="Н", ptr_color=C_GRAV):
    """Vertical dynamometer: spring on top, case with a scale."""
    ax.plot([x - 0.5, x + 0.5], [y_top + 0.35, y_top + 0.35], color=INK, lw=2)
    for xx in np.arange(x - 0.45, x + 0.5, 0.25):
        ax.plot([xx, xx + 0.12], [y_top + 0.35, y_top + 0.5], color=INK, lw=0.7)


def dynamometer_scheme():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 5.6))
    for ax, F in zip(axes, (0, 2)):
        ax.set_xlim(-2.0, 4.6)
        ax.set_ylim(-6.8, 1.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ext = 0.9 * F  # extension per newton is 0.9 length units
        ax.plot([-0.5, 0.5], [0.5, 0.5], color=INK, lw=2)
        for xx in np.arange(-0.4, 0.5, 0.25):
            ax.plot([xx, xx + 0.12], [0.5, 0.68], color=INK, lw=0.7)
        top, bot = 0.5, -1.8 - ext
        coil(ax, 0, top, bot, n=6)
        # pointer and scale
        ptr_y = bot
        ax.plot([0, 1.4], [ptr_y, ptr_y], color=INK, lw=1.4)
        ax.add_patch(Polygon([[1.4, ptr_y], [1.15, ptr_y + 0.1], [1.15, ptr_y - 0.1]], fc=INK))
        ax.add_patch(Rectangle((1.5, -4.9), 0.9, 4.2, fc=PAPER, ec=INK, lw=1.4))
        txt(ax, 1.95, -0.95, "Н", INK, 11)
        for n in range(4):
            yy = -1.8 - 0.9 * n
            ax.plot([1.5, 1.75], [yy, yy], color=INK, lw=1.4)
            ax.text(1.95, yy, str(n), fontsize=11, va="center", ha="left")
        # hook
        ax.plot([0, 0], [bot, bot - 0.35], color=INK, lw=1.4)
        ax.add_patch(Circle((0, bot - 0.5), 0.15, fc="none", ec=INK, lw=1.6))
        if F:
            arrow(ax, (0, bot - 0.7), (0, bot - 1.9), color=C_GRAV)
            txt(ax, 0.35, bot - 1.6, r"$\vec{F}$", C_GRAV, 13, ha="left")
            arrow(ax, (-0.55, bot - 0.2), (-0.55, bot + 1.1), color=C_ELAS)
            txt(ax, -0.7, bot + 0.5, FU, C_ELAS, 12, ha="right")
            ax.set_title("Сила 2 Н приложена к крючку", fontsize=11)
        else:
            ax.set_title("Пружина не деформирована: ноль", fontsize=11)
        ax.text(-1.85, -0.2, "пружина", fontsize=10, color=GREY) if F == 0 else None
    axes[0].annotate("указатель", xy=(0.7, -1.8), xytext=(1.0, 0.1), fontsize=10, color=GREY,
                     arrowprops=dict(arrowstyle="-", color=GREY))
    axes[0].annotate("шкала", xy=(2.4, -1.4), xytext=(2.6, -0.3), fontsize=10, color=GREY,
                     arrowprops=dict(arrowstyle="-", color=GREY))
    save(fig, "dynamometer-scheme.png")


def dynamometer_calibration():
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.set_xlim(-2, 44)
    ax.set_ylim(-3.2, 3.2)
    ax.axis("off")
    ax.plot([0, 40], [1.0, 1.0], color=INK, lw=1.6)
    ax.plot([0, 40], [-1.0, -1.0], color=C_GRAV, lw=1.6)
    for i, d in enumerate(range(0, 41, 4)):
        ax.plot([d, d], [1.0, 1.25], color=INK, lw=1.3)
        ax.text(d, 1.55, str(d), ha="center", fontsize=10)
        ax.plot([d, d], [-1.0, -1.25], color=C_GRAV, lw=1.3)
        ax.text(d, -1.75, num(0.1 * i, 1), ha="center", fontsize=10, color=C_GRAV)
        ax.plot([d, d], [0.7, -0.7], color=GRID, lw=0.9, ls="--")
    ax.text(-1.2, 1.1, r"$\Delta l$, мм", ha="right", va="center", fontsize=11)
    ax.text(-1.2, -1.1, "$F$, Н", ha="right", va="center", fontsize=11, color=C_GRAV)
    ax.text(20, 2.7, "Шкала длины переписывается в шкалу силы", ha="center", fontsize=11.5)
    ax.text(20, -2.7, r"Деления равные, потому что $F=k\,\Delta l$ ($k=25\ \mathrm{Н/м}$: $4\ \mathrm{мм}\leftrightarrow0{,}1\ \mathrm{Н}$)", ha="center", fontsize=10.5, color=INK)
    save(fig, "dynamometer-calibration.png")


def strip_scale(ax, y, limit, major_step, minor_per_major, label, price):
    length = 10.0
    ax.add_patch(Rectangle((0, y - 0.35), length, 0.7, fc=SCALE_PANEL, ec=INK, lw=1.3))
    nmaj = int(round(limit / major_step))
    for i in range(nmaj * minor_per_major + 1):
        xx = length * i / (nmaj * minor_per_major)
        major = i % minor_per_major == 0
        ax.plot([xx, xx], [y + 0.35, y + (0.05 if major else 0.17)], color=INK, lw=1.4 if major else 0.6)
    for i in range(nmaj + 1):
        v = i * major_step
        ax.text(length * i / nmaj, y - 0.12, num(v, None), ha="left" if i == 0 else "right" if i == nmaj else "center", va="center", fontsize=9)
    ax.text(-0.3, y, label, ha="right", va="center", fontsize=10)
    ax.text(length + 0.3, y, price, ha="left", va="center", fontsize=10, color=C_GRAV)


def dynamometer_scale_division():
    fig, ax = plt.subplots(figsize=(11.5, 3.6))
    ax.set_xlim(-3.0, 16.0)
    ax.set_ylim(-0.6, 4.2)
    ax.axis("off")
    strip_scale(ax, 3.3, 1.0, 0.2, 10, "предел 1 Н", r"цена деления $\dfrac{0{,}2}{10}=0{,}02\ \mathrm{Н}$")
    strip_scale(ax, 1.9, 5.0, 1.0, 10, "предел 5 Н", r"цена деления $\dfrac{1}{10}=0{,}1\ \mathrm{Н}$")
    strip_scale(ax, 0.5, 10.0, 1.0, 10, "предел 10 Н", r"цена деления $\dfrac{1}{10}=0{,}1\ \mathrm{Н}$")
    save(fig, "dynamometer-scale-division.png")


def dyn_horizontal(ax, x0, y, reading, F):
    ax.add_patch(Rectangle((x0, y - 0.45), 3.2, 0.9, fc=SCALE_PANEL, ec=INK, lw=1.4))
    for i in range(11):
        xx = x0 + 0.3 + 2.6 * i / 10
        ax.plot([xx, xx], [y + 0.45, y + (0.15 if i % 5 == 0 else 0.28)], color=INK, lw=1)
    ax.text(x0 + 0.3, y - 0.2, "0", ha="center", fontsize=8)
    ax.text(x0 + 2.9, y - 0.2, "1 Н", ha="center", fontsize=8)
    xp = x0 + 0.3 + 2.6 * reading
    ax.add_patch(Polygon([[xp, y + 0.5], [xp - 0.12, y + 0.85], [xp + 0.12, y + 0.85]], fc=C_GRAV))
    ax.plot([x0 - 0.5, x0], [y, y], color=INK, lw=1.6)
    ax.add_patch(Circle((x0 - 0.65, y), 0.15, fc="none", ec=INK, lw=1.6))
    ax.plot([x0 + 3.2, x0 + 3.7], [y, y], color=INK, lw=1.6)
    ax.add_patch(Circle((x0 + 3.85, y), 0.15, fc="none", ec=INK, lw=1.6))


def dynamometer_pair_check():
    fig, ax = blank(11.0, 3.0, (-2.5, 12.5), (-1.6, 1.8))
    dyn_horizontal(ax, 0.0, 0.0, 1.0, 1)
    dyn_horizontal(ax, 4.95, 0.0, 1.0, 1)
    ax.plot([4.0, 4.95 - 0.5], [0, 0], color=INK, lw=1.6)
    arrow(ax, (-0.8, -0.8), (-2.3, -0.8), color=C_GRAV)
    txt(ax, -1.5, -1.25, r"$\vec{F}$", C_GRAV, 13)
    arrow(ax, (9.6, -0.8), (11.1, -0.8), color=C_GRAV)
    txt(ax, 10.3, -1.25, r"$\vec{F}$", C_GRAV, 13)
    txt(ax, 1.6, 1.4, "левый: 1 Н", INK, 11)
    txt(ax, 6.55, 1.4, "правый: 1 Н", INK, 11)
    txt(ax, 4.5, -1.3, "тянут левый с силой 1 Н: правый показывает тоже 1 Н", INK, 10)
    save(fig, "dynamometer-pair-check.png")


def dynamometer_mass_scale():
    fig, ax = blank(5.2, 7.0, (-2.4, 3.6), (-8.4, 1.0))
    ax.plot([-0.5, 0.5], [0.5, 0.5], color=INK, lw=2)
    ax.add_patch(Rectangle((0.6, -6.0), 2.0, 5.6, fc=SCALE_PANEL, ec=INK, lw=1.4))
    txt(ax, 1.05, -0.2, "Н", C_GRAV, 11, fontweight="bold")
    txt(ax, 1.75, -0.2, "кг", C_WEIGHT, 11, fontweight="bold")
    for n, (Fv, m) in enumerate([(0, "0"), (2, "200 г"), (4, "400 г"), (6, "600 г"), (8, "800 г"), (10, "1 кг")]):
        yy = -1.0 - 0.9 * n
        ax.plot([0.6, 0.85], [yy, yy], color=INK, lw=1.3)
        ax.text(1.05, yy, str(Fv), va="center", fontsize=10, color=C_GRAV)
        ax.text(1.55, yy, m, va="center", fontsize=9.5, color=C_WEIGHT)
    pointer_y = -1.0 - 0.9 * 5
    ax.plot([0, 0.6], [pointer_y, pointer_y], color=INK, lw=1.3)
    ax.add_patch(Polygon([[0.6, pointer_y], [0.35, pointer_y + 0.1], [0.35, pointer_y - 0.1]], fc=INK))
    coil(ax, 0, 0.5, pointer_y, n=8)
    ax.plot([0, 0], [pointer_y, pointer_y - 0.4], color=INK, lw=1.3)
    ax.add_patch(Rectangle((-0.45, pointer_y - 1.1), 0.9, 0.7, fc=C_STEEL, ec=INK, lw=1.3))
    txt(ax, 0, pointer_y - 0.75, "1 кг", INK, 10)
    txt(ax, 0.6, -7.9, "динамометр с двойной шкалой — пружинные весы", INK, 9.5)
    save(fig, "dynamometer-mass-scale.png")


def dyn_lever(ax, cx, y, tilt=0.0):
    ax.plot([cx, cx], [y - 1.0, y], color=INK, lw=2.4)
    ax.add_patch(Polygon([[cx - 0.4, y - 1.0], [cx + 0.4, y - 1.0], [cx, y - 0.7]], fc=INK))
    ax.plot([cx - 1.6, cx + 1.6], [y, y], color=INK, lw=2.6)
    for sx in (cx - 1.6, cx + 1.6):
        ax.plot([sx, sx], [y, y - 0.5], color=GREY, lw=1)
        ax.plot([sx - 0.45, sx + 0.45], [y - 0.5, y - 0.5], color=INK, lw=2)
        ax.add_patch(Rectangle((sx - 0.25, y - 0.5), 0.5, 0.5, fc=C_STEEL, ec=INK, lw=1, zorder=0))
    ax.plot([cx, cx], [y, y + 0.35], color=GREY, lw=1.5)


def dynamometer_moon():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.6))
    for ax, (title, g_txt, spring_txt, sc) in zip(
        axes,
        [("Земля", r"$g=10\ \mathrm{Н/кг}$", "1 кг", 1.0), ("Луна", r"$g\approx\dfrac{10}{6}\ \mathrm{Н/кг}$", r"$\approx0{,}17$ кг", 1 / 6)],
    ):
        ax.set_xlim(-1.5, 9.5)
        ax.set_ylim(-3.0, 4.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{title}, {g_txt}", fontsize=12)
        # lever balance
        dyn_lever(ax, 2.0, 2.3)
        ax.text(2.0, -1.0, "рычажные весы:\nравновесие, 1 кг = 1 кг", ha="center", va="top", fontsize=10)
        ax.text(0.4, 3.1, "1 кг", ha="center", fontsize=10)
        ax.text(3.6, 3.1, "гиря\n1 кг", ha="center", fontsize=10)
        # spring balance: zero of the scale at the top, 1 kg at the bottom
        sx = 6.8
        ax.plot([sx - 0.5, sx + 0.5], [3.9, 3.9], color=INK, lw=2)
        ax.add_patch(Rectangle((sx + 0.6, -0.1), 1.0, 3.5, fc=SCALE_PANEL, ec=INK, lw=1.3))
        ax.text(sx + 1.1, 3.05, "0", ha="center", fontsize=8)
        ax.text(sx + 1.1, 0.25, "1 кг", ha="center", fontsize=8)
        py = 3.0 - 2.8 * sc
        ax.plot([sx, sx + 0.6], [py, py], color=INK, lw=1.3)
        ax.add_patch(Polygon([[sx + 0.6, py], [sx + 0.35, py + 0.08], [sx + 0.35, py - 0.08]], fc=INK))
        coil(ax, sx, 3.9, py, n=5, amp=0.25)
        ax.plot([sx, sx], [py, py - 0.25], color=INK, lw=1.2)
        ax.add_patch(Rectangle((sx - 0.35, py - 0.85), 0.7, 0.6, fc=C_STEEL, ec=INK, lw=1.2))
        ax.text(sx, -1.0, f"пружинные весы\nпокажут {spring_txt}", ha="center", va="top", fontsize=10,
                color=C_GRAV if sc < 1 else INK)
    save(fig, "dynamometer-moon.png")


def dynamometer_limits():
    school, pro = BLUE, RED
    items = [
        ("для малых сил, 0,05 Н (цена 2 мН)", 0.05, pro),
        ("учебный на 1 Н", 1, school),
        ("учебный на 5 Н", 5, school),
        ("учебный на 10 Н", 10, school),
        ("демонстрационный на 12 Н", 12, school),
        ("динамометр на 1 кН", 1e3, pro),
        ("пружинные весы 250 кг", 2500, pro),
        ("дистанционный цифровой на 5000 Н", 5000, pro),
        ("динамометр на 400 кН", 4e5, pro),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    names = [n for n, _, _ in items]
    vals = [v for _, v, _ in items]
    cols = [c for _, _, c in items]
    ax.barh(range(len(items)), vals, color=cols, height=0.62)
    ax.set_xscale("log")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("верхний предел измерения, Н (логарифмическая шкала)")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(0.01, 3e6)
    for i, v in enumerate(vals):
        lab = num(v, None) if v < 1e3 else num(v / 1e3, None) + " кН"
        ax.text(v * 1.25, i, lab if v < 1e3 else lab, va="center", fontsize=9.5)
    save(fig, "dynamometer-limits.png")


# ================================================================== weight-*


def weight_contact():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0))
    for ax in axes:
        ax.set_xlim(-2.6, 6.0)
        ax.set_ylim(-3.6, 4.4)
        ax.set_aspect("equal")
        ax.axis("off")
    xs = np.linspace(-2.4, 5.8, 80)
    # before
    ax = axes[0]
    ax.set_title("До соприкосновения с опорой")
    ax.add_patch(Rectangle((0.6, 1.0), 2.0, 2.0, fc=BODY_PALE, ec=INK, lw=1.5))
    for yy in np.linspace(1.15, 2.85, 6):
        ax.plot([0.6, 2.6], [yy, yy], color=GREY, lw=0.9)
    for yy in (0.0, -0.4, -0.8, -1.2, -1.6):
        ax.plot(xs, np.full_like(xs, yy), color=GREY, lw=1.1)
    ax.plot(xs, np.full_like(xs, 0.4), color=INK, lw=1.8)
    ax.plot([1.6], [2.0], "o", color=INK, ms=4)
    arrow(ax, (1.6, 2.0), (1.6, 0.6), color=C_GRAV)
    txt(ax, 1.95, 0.9, FT, C_GRAV, 13, ha="left")
    # after
    ax = axes[1]
    ax.set_title("После соприкосновения с опорой")
    for k, yy in enumerate((0.4, 0.0, -0.4, -0.8, -1.2, -1.6)):
        depth = 0.32 * (1 - k * 0.14)
        ax.plot(xs, yy - depth * np.exp(-((xs - 1.6) / 1.5) ** 2), color=INK if k == 0 else GREY, lw=1.8 if k == 0 else 1.1)
    top = 0.4 - 0.32
    poly = [[0.6, 3.0], [2.6, 3.0], [2.9, top], [0.3, top]]
    ax.add_patch(Polygon(poly, fc=BODY_PALE, ec=INK, lw=1.5))
    for yy in np.linspace(3.0, top + 0.15, 7):
        frac = (3.0 - yy) / (3.0 - top)
        half = 1.0 + 0.15 * frac ** 2
        ax.plot([1.6 - half, 1.6 + half], [yy, yy], color=GREY, lw=0.9)
    ax.plot([1.6], [2.0], "o", color=INK, ms=4)
    arrow(ax, (1.6, 2.0), (1.6, 0.6), color=C_GRAV)
    arrow(ax, (2.05, top + 0.1), (2.05, top + 1.5), color=C_ELAS)
    txt(ax, 1.45, 0.9, FT, C_GRAV, 13, ha="right")
    txt(ax, 2.25, top + 1.55, FU, C_ELAS, 12, ha="left")
    ax.text(3.15, 1.25, "деформация\nтела", fontsize=10, va="center")
    ax.annotate("", xy=(2.9, 0.7), xytext=(3.4, 0.95), arrowprops=dict(arrowstyle="-", color=GREY))
    ax.text(-2.4, -2.3, "деформация опоры", fontsize=10, va="center")
    ax.annotate("", xy=(0.4, -0.55), xytext=(-0.6, -2.0), arrowprops=dict(arrowstyle="-", color=GREY))
    txt(ax, 4.0, 3.3, "слои молекул\nсильно преувеличены", GREY, 9)
    save(fig, "weight-contact.png")


def weight_support_and_hanger():
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.4))
    # on a support
    ax = axes[0]
    ax.set_xlim(-2.4, 4.4)
    ax.set_ylim(-3.3, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Тело на опоре")
    ax.set_xlim(-2.4, 5.2)
    ax.plot([-2.2, 4.2], [0, 0], color=INK, lw=2)
    ax.add_patch(Rectangle((0.0, 0.0), 2.0, 1.7, fc=BODY_PALE, ec=INK, lw=1.5))
    ax.plot([1.0], [0.85], "o", color=INK, ms=5)
    # the three forces are equal in magnitude: one length 2.55
    arrow(ax, (1.0, 0.85), (1.0, -1.7), color=C_GRAV)
    txt(ax, 1.3, -1.6, FT, C_GRAV, 13, ha="left")
    arrow(ax, (0.55, 0.0), (0.55, 2.55), color=C_ELAS)
    txt(ax, 0.35, 2.7, FU, C_ELAS, 13, ha="right")
    ax.plot([0.35], [0.0], "o", color=C_WEIGHT, ms=5)
    arrow(ax, (0.35, 0.0), (0.35, -2.55), color=C_WEIGHT, lw=2.6)
    txt(ax, 0.15, -2.6, PV, C_WEIGHT, 14, ha="right")
    txt(ax, 3.3, 1.2, "точка приложения\n" + r"$\vec{F}_{\mathrm{т}}$ и $\vec{F}_{\mathrm{упр}}$:" + "\nтело", INK, 9.5)
    txt(ax, 3.2, -1.0, "точка приложения\n" + r"$\vec{P}$:" + " опора", C_WEIGHT, 9.5)
    # on a thread
    ax = axes[1]
    ax.set_xlim(-2.4, 4.4)
    ax.set_ylim(-3.3, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Тело на подвесе")
    ax.plot([-0.5, 0.5], [3.7, 3.7], color=INK, lw=2)
    for xx in np.arange(-0.4, 0.5, 0.25):
        ax.plot([xx, xx + 0.12], [3.7, 3.88], color=INK, lw=0.7)
    ax.plot([0, 0], [3.7, 1.4], color=INK, lw=1.4)
    ax.add_patch(Circle((0, 0.4), 1.0, fc=BODY_PALE, ec=INK, lw=1.5))
    ax.plot([0], [0.4], "o", color=INK, ms=5)
    # the three forces are equal in magnitude: one length 2.0
    arrow(ax, (0, 0.4), (0, -1.6), color=C_GRAV)
    txt(ax, 0.3, -1.5, FT, C_GRAV, 13, ha="left")
    arrow(ax, (-0.35, 1.4), (-0.35, 3.4), color=C_ELAS)
    txt(ax, -0.6, 3.2, FU, C_ELAS, 13, ha="right")
    ax.plot([0, 0.35], [2.5, 2.5], color=C_WEIGHT, lw=1, ls=":")
    ax.plot([0], [2.5], "o", color=C_WEIGHT, ms=5)
    arrow(ax, (0.35, 2.5), (0.35, 0.5), color=C_WEIGHT, lw=2.6)
    txt(ax, 0.65, 0.6, PV, C_WEIGHT, 14, ha="left")
    txt(ax, 3.1, 2.8, "точка приложения\n" + r"$\vec{P}$:" + " подвес (нить)", C_WEIGHT, 9.5)
    txt(ax, 3.0, 0.2, "точка приложения\n" + r"$\vec{F}_{\mathrm{т}}$:" + " тело", C_GRAV, 9.5)
    save(fig, "weight-support-and-hanger.png")


def weight_dynamometer_acceleration():
    fig, axes = plt.subplots(1, 4, figsize=(12.6, 5.6))
    cases = [
        ("Гиря покоится", 10, None, "10 Н", INK),
        ("Гирю тянут вверх\nс разгоном", 13.5, "up", "больше 10 Н", C_WEIGHT),
        ("Гирю опускают\nс разгоном вниз", 6.5, "down", "меньше 10 Н", C_WEIGHT),
        ("Свободное\nпадение", 0, "down", "0", C_WEIGHT),
    ]
    for ax, (title, reading, mv, txt_r, colr) in zip(axes, cases):
        ax.set_xlim(-2.4, 3.2)
        ax.set_ylim(-7.4, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11)
        ax.plot([-0.5, 0.5], [0.7, 0.7], color=INK, lw=2)
        ax.add_patch(Rectangle((0.7, -5.2), 1.3, 5.6, fc=SCALE_PANEL, ec=INK, lw=1.3))
        for v in range(0, 16, 5):
            yy = -0.2 - v * 0.3
            ax.plot([0.7, 1.0], [yy, yy], color=INK, lw=1.2)
            ax.text(1.15, yy, str(v), fontsize=9, va="center")
        py = -0.2 - reading * 0.3
        coil(ax, 0, 0.7, py, n=4, amp=0.22)
        ax.plot([0, 0.7], [py, py], color=INK, lw=1.2)
        ax.add_patch(Polygon([[0.7, py], [0.5, py + 0.07], [0.5, py - 0.07]], fc=INK))
        ax.plot([0, 0], [py, py - 0.3], color=INK, lw=1.2)
        ax.add_patch(Rectangle((-0.4, py - 1.15), 0.8, 0.85, fc=C_STEEL, ec=INK, lw=1.3))
        txt(ax, 0, py - 0.72, "1 кг", INK, 9.5)
        arrow(ax, (-1.0, py - 0.7), (-1.0, py - 1.9), color=C_GRAV, lw=2)
        txt(ax, -1.0, py - 2.3, r"$F_{\mathrm{т}}=10$ Н", C_GRAV, 9)
        txt(ax, 0.7, -7.0, "показание " + txt_r, colr, 10, fontweight="bold")
    fig.text(0.5, 0.04, "положения стрелки качественные: важно только больше или меньше 10 Н", ha="center", fontsize=9, color=GREY)
    save(fig, "weight-dynamometer-acceleration.png")


def weight_loop():
    fig, ax = blank(7.4, 7.0, (-4.0, 4.6), (-4.4, 4.6))
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(3 * np.cos(th), 3 * np.sin(th), color=INK, lw=3.0)
    ax.plot(3 * np.cos(th), 3 * np.sin(th), color=GRID, lw=1.2)
    # top: rider inside at (0, 2.5) -> track above at (0, 3)
    ax.add_patch(Circle((0, 2.5), 0.26, fc=C_BODY, ec=INK, lw=1.3, zorder=3))
    ax.plot([0], [2.5], "o", color=INK, ms=3, zorder=4)
    arrow(ax, (0, 2.5), (0, 1.2), color=C_GRAV)
    txt(ax, 0.35, 1.5, FT, C_GRAV, 13, ha="left")
    ax.plot([0.55], [3.0], "o", color=C_WEIGHT, ms=5, zorder=4)
    arrow(ax, (0.55, 3.0), (0.55, 4.3), color=C_WEIGHT, lw=2.6)
    txt(ax, 0.8, 4.05, PV, C_WEIGHT, 14, ha="left")
    txt(ax, -0.4, 3.85, "вес приложен к петле\nи направлен вверх", C_WEIGHT, 9.5, ha="right")
    # bottom
    ax.add_patch(Circle((0, -2.5), 0.26, fc=C_BODY, ec=INK, lw=1.3, zorder=3))
    ax.plot([0], [-2.5], "o", color=INK, ms=3, zorder=4)
    arrow(ax, (0, -2.5), (0, -3.7), color=C_GRAV)
    txt(ax, 0.35, -3.6, FT, C_GRAV, 13, ha="left")
    ax.plot([-0.55], [-3.0], "o", color=C_WEIGHT, ms=5, zorder=4)
    arrow(ax, (-0.55, -3.0), (-0.55, -4.35), color=C_WEIGHT, lw=2.6)
    txt(ax, -0.8, -4.15, PV, C_WEIGHT, 14, ha="right")
    txt(ax, 0, 0.3, "«мёртвая петля»", INK, 11)
    txt(ax, 0, -0.4, "длины стрелок качественные", GREY, 9)
    save(fig, "weight-loop.png")


def weight_gasoline():
    fig, ax = blank(7.6, 5.4, (-2.0, 9.6), (-4.4, 3.4))
    ax.add_patch(Rectangle((0, 0), 3.2, 2.6, fc=tint(WARM, 0.8), ec="none"))
    ax.plot([0, 0, 3.2, 3.2], [2.9, 0, 0, 2.9], color=INK, lw=2.4)
    ax.text(1.6, 1.3, "бензин\n25 л", ha="center", va="center", fontsize=12)
    ax.plot([1.6], [0.0], "o", color=C_WEIGHT, ms=5)
    arrow(ax, (1.6, 0.0), (1.6, -1.8), color=C_WEIGHT, lw=2.8)
    txt(ax, 1.95, -1.0, PV, C_WEIGHT, 14, ha="left")
    txt(ax, 1.6, -2.3, r"$P\approx180\ \mathrm{Н}$, приложен ко дну", C_WEIGHT, 10.5)
    # scale bar
    ax.plot([5.4, 6.4], [1.6, 1.6], color=INK, lw=2)
    for xx in (5.4, 6.4):
        ax.plot([xx, xx], [1.5, 1.7], color=INK, lw=2)
    txt(ax, 5.9, 2.05, "100 Н", INK, 11)
    txt(ax, 5.9, 1.2, "1 см", INK, 10)
    txt(ax, 7.9, 0.4, "масштаб: 1 см — 100 Н,\nстрелка длиной 1,8 см", INK, 9.5)
    save(fig, "weight-gasoline.png")


def weight_palm():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 5.4))
    for ax in axes:
        ax.set_xlim(-2.8, 4.6)
        ax.set_ylim(-4.2, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axes[0]
    ax.set_title("Тело покоится на ладони")
    ax.add_patch(Polygon([[-2.0, -0.35], [1.8, -0.35], [2.4, -0.15], [1.8, 0.0], [-2.0, 0.0]], fc=tint(WARM, 0.5), ec=INK, lw=1.3))
    ax.add_patch(Rectangle((-0.45, 0.0), 1.1, 1.1, fc=BODY_PALE, ec=INK, lw=1.5))
    txt(ax, 0.1, 0.55, r"$m$" + "\n5 кг", INK, 10)
    # P = F_t: one length 2.85
    ax.plot([0.1], [0.55], "o", color=INK, ms=4)
    arrow(ax, (0.1, 0.55), (0.1, -2.3), color=C_GRAV, lw=2.4)
    txt(ax, 0.4, -2.0, FT, C_GRAV, 13, ha="left")
    ax.plot([-0.9], [-0.18], "o", color=C_WEIGHT, ms=5)
    arrow(ax, (-0.9, -0.18), (-0.9, -3.03), color=C_WEIGHT, lw=2.4)
    txt(ax, -1.15, -2.7, PV, C_WEIGHT, 13, ha="right")
    txt(ax, 0.9, -3.8, r"$P=F_{\mathrm{т}}=50\ \mathrm{Н}$", INK, 11)
    ax = axes[1]
    ax.set_title("Ладонь выдернули")
    ax.plot([-2.0, 2.4], [-0.15, -0.15], color=GRID, lw=2, ls="--")
    ax.text(1.6, 0.3, "ладони нет", color=GREY, fontsize=9)
    ax.add_patch(Rectangle((-0.45, 0.0), 1.1, 1.1, fc=BODY_PALE, ec=INK, lw=1.5))
    txt(ax, 0.1, 0.55, r"$m$" + "\n5 кг", INK, 10)
    ax.plot([0.1], [0.55], "o", color=INK, ms=4)
    arrow(ax, (0.1, 0.55), (0.1, -2.3), color=C_GRAV, lw=2.4)
    txt(ax, 0.4, -2.0, FT, C_GRAV, 13, ha="left")
    txt(ax, 0.9, -3.8, r"$P=0$, $F_{\mathrm{т}}=50\ \mathrm{Н}$", INK, 11)
    save(fig, "weight-palm.png")


def weight_jump():
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.8))
    for ax in axes:
        ax.set_xlim(-2.6, 4.2)
        ax.set_ylim(-4.4, 4.4)
        ax.set_aspect("equal")
        ax.axis("off")

    def man(ax, x, y, col=C_BODY):
        ax.add_patch(Rectangle((x - 0.35, y), 0.7, 1.4, fc=col, ec=INK, lw=1.4))
        ax.add_patch(Circle((x, y + 1.75), 0.3, fc=col, ec=INK, lw=1.4))

    ax = axes[0]
    ax.set_title("На пирсе")
    ax.add_patch(Rectangle((-2.6, -0.4), 4.0, 0.4, fc=C_WOOD, ec=INK, lw=1.3))
    man(ax, 0.0, 0.0)
    ax.plot([0.0], [0.7], "o", color=INK, ms=4)
    arrow(ax, (0.3, 0.7), (0.3, -1.2), color=C_GRAV)
    arrow(ax, (-0.3, 0.0), (-0.3, 1.9), color=C_ELAS, lw=2.0) if False else None
    arrow(ax, (-0.55, 0.0), (-0.55, -1.9), color=C_WEIGHT, lw=2.6)
    txt(ax, 0.6, -1.0, FT, C_GRAV, 12, ha="left")
    txt(ax, -0.8, -1.8, PV, C_WEIGHT, 13, ha="right")
    txt(ax, 0.0, 3.6, "вес есть", C_WEIGHT, 11, fontweight="bold")
    ax = axes[1]
    ax.set_title("В полёте")
    ax.add_patch(Rectangle((-2.6, -0.4), 2.2, 0.4, fc=C_WOOD, ec=INK, lw=1.3))
    ax.add_patch(Rectangle((-2.6, -4.4), 6.8, 3.2, fc=C_WATER, ec="none", alpha=0.7))
    man(ax, 1.2, 0.6)
    ax.plot([1.2], [1.3], "o", color=INK, ms=4)
    arrow(ax, (1.2, 1.3), (1.2, -0.5), color=C_GRAV)
    txt(ax, 1.5, 0.2, FT, C_GRAV, 12, ha="left")
    txt(ax, 1.2, 3.6, "опоры нет: вес равен 0\n(невесомость)", C_WEIGHT, 10.5, fontweight="bold")
    ax = axes[2]
    ax.set_title("В воде")
    ax.add_patch(Rectangle((-2.6, -4.4), 6.8, 4.8, fc=C_WATER, ec="none", alpha=0.7))
    ax.plot([-2.6, 4.2], [0.4, 0.4], color=BLUE, lw=1.6)
    man(ax, 0.6, -3.2)
    ax.plot([0.6], [-2.5], "o", color=INK, ms=4)
    # hovering diver: F_A = F_t = P, one length 1.2
    arrow(ax, (0.95, -2.5), (0.95, -3.7), color=C_GRAV)
    txt(ax, 1.25, -3.6, FT, C_GRAV, 12, ha="left")
    arrow(ax, (0.25, -3.1), (0.25, -1.9), color=C_ELAS)
    txt(ax, -0.05, -2.0, r"$\vec{F}_{\mathrm{А}}$", C_ELAS, 12, ha="right")
    arrow(ax, (-0.85, -3.2), (-0.85, -4.4), color=C_WEIGHT, lw=2.6)
    txt(ax, -1.1, -4.2, PV, C_WEIGHT, 13, ha="right")
    txt(ax, 1.0, 3.4, "опора — вода:\nвес есть", C_WEIGHT, 10.5, fontweight="bold")
    save(fig, "weight-jump.png")


def weight_vs_mass():
    fig, ax = graph_axes(7.6, 4.8, r"масса $m$, кг", r"вес $P$ покоящегося тела, Н")
    m = np.linspace(0, 5, 50)
    ax.plot(m, 10 * m, color=C_WEIGHT, lw=2.6, label=r"Земля, $g=10\ \mathrm{Н/кг}$")
    ax.plot(m, 10 / 6 * m, color=C_GRAV, lw=2.6, label=r"Луна, $g\approx\dfrac{10}{6}\ \mathrm{Н/кг}$")
    ax.plot([1], [10], "o", color=C_WEIGHT)
    ax.plot([1], [10 / 6], "o", color=C_GRAV)
    ax.text(0.9, 12.5, "1 кг: 10 Н", fontsize=10, color=C_WEIGHT, va="bottom", ha="right")
    ax.text(1.15, 4.5, r"1 кг: $\approx1{,}7$ Н", fontsize=10, color=C_GRAV, va="bottom")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 52)
    ax.legend(loc="upper left", fontsize=10)
    save(fig, "weight-vs-mass.png")


if __name__ == "__main__":
    elastic_ruler_weight()
    elastic_deformation_types()
    elastic_plastic()
    elastic_hooke_data()
    elastic_hooke_stiffness()
    elastic_hooke_abs()
    elastic_rubber_setup()
    elastic_hanging_spring()
    elastic_problem_11_15()
    dynamometer_scheme()
    dynamometer_calibration()
    dynamometer_scale_division()
    dynamometer_pair_check()
    dynamometer_mass_scale()
    dynamometer_moon()
    dynamometer_limits()
    weight_contact()
    weight_support_and_hanger()
    weight_dynamometer_acceleration()
    weight_loop()
    weight_gasoline()
    weight_palm()
    weight_jump()
    weight_vs_mass()
