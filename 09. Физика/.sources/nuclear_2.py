"""Figures for the notes "Доза излучения. Ослабление излучения" and
"Деление ядер. Термоядерный синтез" (section f15, lessons 225-229).

Run: python3 nuclear_2.py
PNG files go to content/15. Ядерная физика/00. Вложения/ (prefixes dose-, fission-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "15. Ядерная физика"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
HOT_L = tint(RED, 0.85)
GREEN_L = tint(GREEN, 0.8)
WATER = BLUE  # water, and the negative charge
WATER_L = tint(SKY, 0.75)
GOLD = WARM  # nuclear fuel and the things made of it
GOLD_L = tint(WARM, 0.6)
STEEL = METAL
WOOD = COPPER
WOOD_L = tint(COPPER, 0.7)
NEUTRON = tint(INK, 0.4)  # a neutron: neutral, so a grey
LEAD = tint(INK, 0.2)  # lead, a dark shield
LIGHT_METAL = tint(INK, 0.8)  # a pale metal part
DETECTOR = INK  # the dark body of a detector


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", ms=12, ls="-", rad=0.0, z=5):
    ax.add_patch(
        FancyArrowPatch(
            p,
            q,
            arrowstyle=style,
            mutation_scale=ms,
            color=color,
            lw=lw,
            ls=ls,
            connectionstyle=f"arc3,rad={rad}",
            zorder=z,
        )
    )


def text(ax, x, y, s, size=10.5, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)


def neutron(ax, x, y, r=0.1, z=6):
    ax.add_patch(Circle((x, y), r, fc=NEUTRON, ec=INK, lw=0.8, zorder=z))


def proton(ax, x, y, r=0.1, z=6):
    ax.add_patch(Circle((x, y), r, fc=HOT, ec=INK, lw=0.8, zorder=z))


# ---------------------------------------------------------------- dose-


def dose_quality_factor():
    names = ["гамма", "бета", "протоны", "нейтроны", "альфа"]
    lo = [1, 1, 5, 5, 20]
    hi = [1, 1, 5, 10, 20]
    cols = [METAL, METAL, GOLD, VIOLET, HOT]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for i, (n, a, b, c) in enumerate(zip(names, lo, hi, cols)):
        if a == b:
            ax.barh(i, a, color=c, height=0.6)
            ax.text(a + 0.4, i, f"{a}", va="center", fontsize=11)
        else:
            ax.barh(i, a, color=c, height=0.6, alpha=0.55)
            ax.barh(i, b - a, left=a, color=c, height=0.6)
            ax.text(b + 0.4, i, f"{a}–{b}", va="center", fontsize=11)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xlim(0, 23)
    ax.set_xlabel("коэффициент качества K")
    ax.set_title("Коэффициент качества излучения")
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "dose-quality-factor.png")


def dose_three_doses():
    fig, ax = blank(11, 3.7, (0, 11), (0, 3.7))
    boxes = [
        (0.2, WATER_L, WATER, "Поглощённая доза", r"$D=\dfrac{W}{m}$", "Гр = Дж/кг", "энергия излучения,\nпоглощённая 1 кг вещества"),
        (3.9, HOT_L, HOT, "Эквивалентная доза", r"$H=K\,D$", "Зв (бэр)", "биологическое действие:\nучёт вида излучения"),
        (7.6, tint(ACCENT, 0.85), ACCENT, "Экспозиционная доза", r"$D_{\mathrm{эксп}}=\dfrac{Q}{m}$", "Кл/кг (Р)", "заряд ионов одного знака\nв 1 кг сухого воздуха"),
    ]
    for x, fc, ec, title, f, unit, desc in boxes:
        ax.add_patch(FancyBboxPatch((x, 0.2), 3.2, 3.3, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=ec, lw=1.8))
        text(ax, x + 1.6, 3.05, title, size=12.5, weight="bold")
        text(ax, x + 1.6, 2.1, f, size=17)
        text(ax, x + 1.6, 1.25, unit, size=12, color=ec, weight="bold")
        text(ax, x + 1.6, 0.6, desc, size=9.5)
    save(fig, "dose-three-doses.png")


def dose_geiger_tube():
    fig = plt.figure(figsize=(12.2, 4.8))
    ax = fig.add_axes([0.0, 0.0, 0.66, 1.0])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    # glass tube with inner metal layer
    ax.add_patch(FancyBboxPatch((1.4, 3.3), 5.0, 1.9, boxstyle="round,pad=0.02,rounding_size=0.45", fc=LIGHT, ec=STEEL, lw=3))
    ax.add_patch(FancyBboxPatch((1.55, 3.45), 4.7, 1.6, boxstyle="round,pad=0.02,rounding_size=0.4", fc=PAPER, ec=GREY, lw=1.2, ls="--"))
    ax.plot([0.9, 6.9], [4.25, 4.25], color=INK, lw=1.6, zorder=3)  # anode wire
    # gas dots
    rng = np.random.default_rng(3)
    for _ in range(30):
        x, y = rng.uniform(1.8, 6.0), rng.uniform(3.6, 4.9)
        if abs(y - 4.25) > 0.18:
            ax.plot(x, y, ".", color=GREY, ms=3)
    # ions and electrons
    for x, y in [(3.0, 3.75), (3.7, 3.7), (4.4, 3.8)]:
        ax.text(x, y, "+", color=HOT, fontsize=13, ha="center", va="center", weight="bold")
        arrow(ax, (x, y - 0.12), (x, 3.52), color=HOT, lw=1, ms=8)
    for x, y in [(3.3, 4.75), (4.1, 4.8)]:
        ax.text(x, y, "−", color=WATER, fontsize=15, ha="center", va="center", weight="bold")
        arrow(ax, (x, y - 0.14), (x, 4.36), color=WATER, lw=1, ms=8)
    # incoming particle
    arrow(ax, (0.3, 5.9), (2.6, 4.95), color=VIOLET, lw=2)
    text(ax, 0.9, 6.2, "бета-частица (электрон)\nили электрон из катода\nпод действием гамма-излучения", size=9, ha="left", color=VIOLET)
    # labels
    text(ax, 3.4, 2.75, "стеклянная трубка,\nпокрытая изнутри металлом (катод)", size=9.5)
    arrow(ax, (3.4, 3.05), (3.4, 3.4), color=GREY, lw=1.2, ms=9)
    text(ax, 6.3, 5.95, "разрежённый\nинертный газ", size=9.5, ha="center")
    arrow(ax, (6.2, 5.5), (5.6, 4.85), color=GREY, lw=1.2, ms=9)
    text(ax, 0.75, 2.85, "тонкая проволока\n(анод)", size=9.5, ha="center")
    arrow(ax, (1.0, 3.2), (1.2, 4.1), color=GREY, lw=1.2, ms=9)
    # circuit: anode -> R -> "+", cathode -> "-", amplifier across R
    ax.plot([6.9, 7.4], [4.25, 4.25], color=INK, lw=1.6)
    ax.plot([7.4, 7.4], [4.25, 3.6], color=INK, lw=1.6)
    ax.add_patch(Rectangle((7.2, 2.4), 0.4, 1.2, fc=PAPER, ec=INK, lw=1.6, zorder=3))
    text(ax, 7.0, 3.0, r"$R\approx10^{7}$ Ом", size=10, ha="right")
    ax.plot([7.4, 7.4], [2.4, 1.0], color=INK, lw=1.6)
    ax.plot([7.4, 9.0], [1.0, 1.0], color=INK, lw=1.6)
    text(ax, 9.25, 1.0, "+", size=14, weight="bold")
    ax.plot([5.4, 5.4], [3.3, 0.55], color=INK, lw=1.6)
    ax.plot([5.4, 9.0], [0.55, 0.55], color=INK, lw=1.6)
    text(ax, 9.25, 0.55, "−", size=16, weight="bold")
    text(ax, 3.3, 0.55, "источник напряжения\n800–1000 В", size=9.5)
    ax.add_patch(Rectangle((8.4, 1.75), 1.2, 2.3, fc=LIGHT, ec=INK, lw=1.6, zorder=3))
    ax.text(9.0, 2.9, "усили-\nтель", fontsize=9.5, ha="center", va="center")
    # upper tap sits on the wire above the resistor body (4.25..3.6), lower tap on the wire below it
    ax.plot([7.4, 8.4], [3.85, 3.85], color=INK, lw=1.4)
    ax.plot([7.4, 8.4], [2.0, 2.0], color=INK, lw=1.4)
    ax.plot([7.4], [3.85], "o", color=INK, ms=4)
    ax.plot([7.4], [2.0], "o", color=INK, ms=4)
    # pulses axes
    ax2 = fig.add_axes([0.72, 0.22, 0.26, 0.6])
    t = np.linspace(0, 10, 2000)
    i = np.zeros_like(t)
    for t0 in (1.5, 3.4, 4.0, 7.2, 8.5):
        m = t >= t0
        i[m] += np.exp(-(t[m] - t0) / 0.12)
    ax2.plot(t, np.minimum(i, 1.0) * 1.0, color=HOT, lw=1.8)
    ax2.set_xlabel("время t")
    ax2.set_ylabel("сила тока I")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_title("Импульсы тока", fontsize=12)
    fig.text(0.85, 0.06, "каждый импульс — одна частица", ha="center", fontsize=9.5, color=INK)
    save(fig, "dose-geiger-tube.png")


def dose_scale():
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    ax.set_xscale("log")
    ax.set_xlim(0.1, 1000)
    ax.set_ylim(0, 3)
    ax.set_yticks([])
    for s in ("left",):
        ax.spines[s].set_visible(False)
    zones = [
        (0.1, 1, GREEN_L, GREEN, "безвредно\nоднократно"),
        (50, 100, GOLD_L, GOLD, "переносимо\nоднократно"),
        (100, 400, HOT_L, HOT, "лучевая\nболезнь"),
        (400, 1000, tint(RED, 0.55), INK, "смертельно"),
    ]
    for a, b, fc, ec, label in zones:
        ax.axvspan(a, b, ymin=0.33, ymax=0.53, fc=fc, ec=ec, lw=1.3)
        ax.text(np.sqrt(a * b), 2.0, label, ha="center", va="center", fontsize=9.5, color=INK)
    ax.plot([0.14, 0.14], [0.85, 1.75], color=INK, lw=1.6)
    ax.text(0.14, 2.45, "рентгеновское\nобследование:\n0,14 бэр", ha="center", va="center", fontsize=9.5, color=INK)
    ax.plot([166], [1.3], "*", color=INK, ms=13, zorder=6)
    keep_dots(ax.annotate("задача 30.2: 166 бэр", xy=(166, 1.3), xytext=(166, 0.45), ha="center", fontsize=9.5, arrowprops=dict(arrowstyle="->", color=INK)))
    ax.set_xticks([0.1, 1, 50, 100, 400, 1000])
    ax.set_xticklabels(["0,1", "1", "50", "100", "400", "1000"])
    ax.minorticks_off()
    ax.set_xlabel("эквивалентная доза, бэр")
    sec = ax.secondary_xaxis("top", functions=(lambda x: x / 100, lambda x: x * 100))
    sec.set_xlabel("эквивалентная доза, Зв")
    sec.spines["top"].set_visible(True)
    ax.set_title("Эквивалентная доза и действие на организм", pad=38)
    save(fig, "dose-scale.png")


def dose_attenuation_curve():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
    x = np.linspace(0, 4.6, 300)
    a1.plot(x, 2.0 ** (-x), color=HOT, lw=2.4)
    for k in range(0, 4):
        a1.plot([k, k], [0, 2.0 ** (-k)], color=GREY, lw=1, ls="--")
        a1.plot([0, k], [2.0 ** (-k)] * 2, color=GREY, lw=1, ls="--")
        a1.plot(k, 2.0 ** (-k), "o", color=HOT, ms=7, zorder=5)
    a1.set_xticks(range(0, 5))
    a1.set_xticklabels(["0", "h", "2h", "3h", "4h"])
    a1.set_yticks([0, 1 / 8, 1 / 4, 1 / 2, 1])
    a1.set_yticklabels(["0", "1/8", "1/4", "1/2", "1"])
    a1.set_xlabel("толщина слоя d")
    a1.set_ylabel(r"$P_{\mathrm{прош}}\,/\,P_{\mathrm{пад}}$")
    a1.set_title("Мощность дозы за слоем")
    a1.set_ylim(0, 1.08)
    a1.grid(True, color=GRID, lw=0.8)
    a1.set_axisbelow(True)
    a1.annotate("слой половинного\nослабления h", xy=(1, 0.5), xytext=(1.9, 0.72), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=INK))
    a2.plot(x, 2.0 ** x, color=WATER, lw=2.4)
    for k in range(0, 4):
        a2.plot(k, 2.0 ** k, "o", color=WATER, ms=7, zorder=5)
        a2.plot([k, k], [0, 2.0 ** k], color=GREY, lw=1, ls="--")
    a2.set_xticks(range(0, 5))
    a2.set_xticklabels(["0", "h", "2h", "3h", "4h"])
    a2.set_yticks([1, 2, 4, 8, 16])
    a2.set_xlabel("толщина слоя d")
    a2.set_ylabel(r"коэффициент ослабления $K_\gamma$")
    a2.set_title("Коэффициент ослабления")
    a2.grid(True, color=GRID, lw=0.8)
    a2.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "dose-attenuation-curve.png")


def dose_lab_setup():
    fig, ax = blank(10.6, 5.0, (0, 10.6), (-0.5, 4.5))
    # table
    ax.add_patch(Rectangle((0.1, 0.35), 10.0, 0.3, fc=WOOD_L, ec=WOOD, lw=1.4))
    # stand with source
    ax.add_patch(Rectangle((0.7, 0.65), 1.2, 0.18, fc=STEEL, ec=INK))
    ax.add_patch(Rectangle((1.22, 0.83), 0.1, 2.6, fc=STEEL, ec=INK))
    ax.add_patch(Rectangle((1.22, 2.5), 0.85, 0.16, fc=STEEL, ec=INK))
    ax.add_patch(Rectangle((1.95, 2.25), 0.75, 0.65, fc=LIGHT_METAL, ec=INK, lw=1.6, zorder=4))
    ax.add_patch(Circle((2.32, 2.575), 0.17, fc=GOLD, ec=INK, zorder=5))
    text(ax, 2.32, 3.35, "источник\nгамма-излучения", size=10)
    # rays
    for dy in (-0.2, 0, 0.2):
        arrow(ax, (2.8, 2.575 + dy), (7.2, 2.575 + dy), color=HOT, lw=1.5, ms=10)
    # barrier
    ax.add_patch(Rectangle((4.0, 0.65), 1.3, 3.0, fc=WOOD_L, ec=WOOD, lw=2, hatch="///", zorder=3))
    text(ax, 4.65, 3.95, "преграда:\nдерево, алюминий,\nсвинцовый аккумулятор", size=10)
    # dosimeter
    ax.add_patch(FancyBboxPatch((7.2, 0.65), 1.7, 2.6, boxstyle="round,pad=0.02,rounding_size=0.12", fc=DETECTOR, ec=INK, lw=1.6))
    ax.add_patch(Rectangle((7.45, 2.35), 1.2, 0.7, fc=GREEN_L, ec=INK))
    for x in (7.65, 8.05, 8.45):
        ax.add_patch(Circle((x, 1.75), 0.14, fc=PAPER, ec=GREY))
    ax.add_patch(Circle((8.05, 1.35), 0.14, fc=PAPER, ec=GREY))
    text(ax, 8.05, 3.6, "дозиметр", size=10)
    ax.add_patch(Circle((7.55, 2.575), 0.07, fc=HOT, ec=INK, zorder=6))
    text(ax, 8.05, 0.95, "", size=9)
    # dimensions
    ax.plot([2.32, 2.32], [0.0, 2.2], color=GREY, lw=0.9, ls=":")
    ax.plot([7.55, 7.55], [0.0, 2.45], color=GREY, lw=0.9, ls=":")
    arrow(ax, (2.32, 0.1), (7.55, 0.1), color=INK, lw=1.2, style="<|-|>", ms=9)
    text(ax, 4.9, -0.2, "10 см между осями источника и счётчика", size=10)
    text(ax, 9.45, 3.85, "ось счётчика Гейгера —\n≈ 1 см от края прибора", size=9, color=INK)
    arrow(ax, (9.2, 3.55), (7.65, 2.65), color=GREY, lw=0.9, ms=7)
    save(fig, "dose-lab-setup.png")


# data of the two recordings
D2019 = {"без преграды": 113, "вода, 9 см": 73, "дерево, 10 см": 84, "алюминий, 8 см": 62, "«свинец», 9 см": 36}
N_F = 17
D2014 = {"без преграды": 0.87, "дерево, 4 см": 0.69, "алюминий, 4 см": 0.65, "свинцовый\nаккумулятор, 6 см": 0.32}
P_F = 0.12


def dose_lab_data():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [5, 4]})
    cols1 = [GOLD, WATER, WOOD, STEEL, LEAD]
    names1 = list(D2019)
    vals1 = [v - N_F for v in D2019.values()]
    a1.bar(range(5), vals1, color=cols1, width=0.65)
    for i, v in enumerate(vals1):
        lab = f"{v}" if i == 0 else f"{num(v, '')}\nK = {num(vals1[0] / v, 2)}"
        a1.text(i, v + 3, lab, ha="center", fontsize=10)
    a1.set_xticks(range(5))
    a1.set_xticklabels(names1, fontsize=9)
    a1.set_ylim(0, 125)
    a1.set_ylabel(r"$N-N_{\mathrm{ф}}$, отсчёты за 100 с")
    a1.set_title("Запись 2019: счётчик Гейгера")
    a1.grid(True, axis="y", color=GRID, lw=0.8)
    a1.set_axisbelow(True)
    cols2 = [GOLD, WOOD, STEEL, LEAD]
    names2 = list(D2014)
    vals2 = [round(v - P_F, 2) for v in D2014.values()]
    a2.bar(range(4), vals2, color=cols2, width=0.65)
    for i, v in enumerate(vals2):
        lab = num(v, 2) if i == 0 else f"{num(v, 2)}\nK = {num(vals2[0] / v, 2)}"
        a2.text(i, v + 0.02, lab, ha="center", fontsize=10)
    a2.set_xticks(range(4))
    a2.set_xticklabels(names2, fontsize=9)
    a2.set_ylim(0, 0.95)
    a2.set_ylabel(r"$P-P_{\mathrm{ф}}$, мкЗв/ч")
    a2.set_title("Запись 2014: дозиметр")
    a2.grid(True, axis="y", color=GRID, lw=0.8)
    a2.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "dose-lab-data.png")


def half_layer(d, k):
    return d * np.log(2) / np.log(k)


def dose_lab_fit():
    base19 = D2019["без преграды"] - N_F
    base14 = D2014["без преграды"] - P_F
    rows = [
        ("вода", 9, (73 - N_F) / base19, 2019, WATER),
        ("дерево", 10, (84 - N_F) / base19, 2019, WOOD),
        ("алюминий", 8, (62 - N_F) / base19, 2019, STEEL),
        ("«свинец»", 9, (36 - N_F) / base19, 2019, LEAD),
        ("дерево", 4, (0.69 - P_F) / base14, 2014, WOOD),
        ("алюминий", 4, (0.65 - P_F) / base14, 2014, STEEL),
        ("свинцовый аккумулятор", 6, (0.32 - P_F) / base14, 2014, LEAD),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    x = np.linspace(0, 12, 300)
    for name, d, f, year, c in rows:
        h = half_layer(d, 1 / f)
        ls = "-" if year == 2019 else "--"
        mk = "o" if year == 2019 else "s"
        ax.plot(x, 2.0 ** (-x / h), color=c, ls=ls, lw=1.6, alpha=0.85)
        ax.plot(d, f, mk, color=c, ms=8, mec=INK, zorder=5)
        hs = num(h, 1)
        ax.text(12.15, 2.0 ** (-12 / h), f"{name}, h ≈ {hs} см", va="center", fontsize=8.5, color=INK)
    ax.axhline(0.5, color=GREY, lw=1, ls=":")
    ax.text(0.15, 0.52, "1/2", fontsize=9, color=NOTE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("толщина слоя d, см")
    ax.set_ylabel(r"$1/K_\gamma$ — доля прошедшего излучения")
    ax.set_title("Опыты: доля прошедшего излучения")
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    from matplotlib.lines import Line2D

    ax.legend(
        handles=[
            Line2D([], [], color=INK, marker="o", ls="-", label="запись 2019"),
            Line2D([], [], color=INK, marker="s", ls="--", label="запись 2014"),
        ],
        loc="upper right",
        fontsize=9,
    )
    fig.subplots_adjust(right=0.68)
    save(fig, "dose-lab-fit.png")


# ---------------------------------------------------------------- fission-


def fission_uranium_nucleus():
    fig, ax = blank(14.2, 3.2, (0, 14.3), (0.1, 3.3))
    cy = 1.9
    # stage 1
    ax.add_patch(Circle((2.6, cy), 0.62, fc=GOLD_L, ec=INK, lw=1.6))
    text(ax, 2.6, cy, r"$^{235}_{92}$U", size=12)
    neutron(ax, 0.55, cy, 0.14)
    arrow(ax, (0.75, cy), (1.85, cy), color=NEUTRON, lw=1.8)
    text(ax, 0.75, cy + 0.45, r"$^{1}_{0}n$", size=11)
    text(ax, 1.6, 0.6, "нейтрон входит в ядро\nбез отталкивания", size=9.5)
    # stage 2
    ax.add_patch(Circle((5.0, cy), 0.66, fc=HOT_L, ec=INK, lw=1.6))
    text(ax, 5.0, cy, r"$^{236}_{92}$U", size=12)
    text(ax, 5.0, 0.6, "неустойчивое ядро\nколеблется", size=9.5)
    arrow(ax, (3.4, cy), (4.2, cy), color=INK)
    # stage 3
    ax.add_patch(Ellipse((7.5, cy), 2.0, 0.95, fc=HOT_L, ec=INK, lw=1.6))
    for x, y in [(6.85, 2.05), (7.1, 1.65), (7.5, 2.15), (7.9, 1.65), (8.15, 2.05), (7.5, 1.75)]:
        text(ax, x, y, "+", size=12, color=HOT, weight="bold")
    ax.plot([7.5, 7.5], [1.05, 2.75], color=GREY, lw=1.2, ls="--")
    text(ax, 7.5, 0.6, "капля вытянулась: края не\nудерживает короткодействующая\nядерная сила, а электрическое\nотталкивание растёт", size=9)
    arrow(ax, (5.85, cy), (6.35, cy), color=INK)
    # stage 4
    ax.add_patch(Circle((11.4, cy + 0.15), 0.42, fc=WATER_L, ec=INK, lw=1.6))
    text(ax, 11.4, cy + 0.15, "Ba", size=11)
    ax.add_patch(Circle((13.0, cy + 0.15), 0.35, fc=GREEN_L, ec=INK, lw=1.6))
    text(ax, 13.0, cy + 0.15, "Kr", size=11)
    arrow(ax, (10.95, cy + 0.15), (10.25, cy + 0.15), color=INK, lw=2.2)
    arrow(ax, (13.45, cy + 0.15), (14.15, cy + 0.15), color=INK, lw=2.2)
    text(ax, 12.2, cy + 0.95, "≈ 200 МэВ на одно деление", size=10.5, color=HOT, weight="bold")
    # fission neutrons leave the fission point (the gap between the fragments) and fly outward to the circles
    for x in (11.7, 12.2, 12.7):
        neutron(ax, x, 0.95, 0.11)
        arrow(ax, (12.2, 1.8), (x, 1.12), color=NEUTRON, lw=1.4, ms=9)
    text(ax, 12.2, 0.45, "2–3 нейтрона", size=9.5)
    arrow(ax, (8.75, cy), (9.55, cy), color=INK)
    save(fig, "fission-uranium-nucleus.png")


def fission_chain_tree():
    fig, ax = blank(9.4, 5.2, (0, 9.4), (0, 5.2))
    levels = [1, 2, 4, 8]
    ys = [4.5, 3.25, 2.0, 0.75]
    xs = []
    for n in levels:
        xs.append([(i + 0.5) * 9.0 / n + 0.2 for i in range(n)])
    for li in range(len(levels) - 1):
        for i, x in enumerate(xs[li]):
            for j in (2 * i, 2 * i + 1):
                arrow(ax, (x, ys[li] - 0.2), (xs[li + 1][j], ys[li + 1] + 0.2), color=NEUTRON, lw=1.4, ms=9)
    for li, n in enumerate(levels):
        for x in xs[li]:
            ax.add_patch(Circle((x, ys[li]), 0.2, fc=GOLD_L, ec=INK, lw=1.4, zorder=6))
    neutron(ax, xs[0][0] - 0.0, 5.05, 0.1)
    arrow(ax, (xs[0][0], 4.95), (xs[0][0], 4.72), color=NEUTRON, lw=1.4, ms=9)
    text(ax, xs[0][0] + 0.45, 5.05, "первый нейтрон", size=9.5, ha="left")
    for li, n in enumerate(levels):
        text(ax, 0.05, ys[li], str(n), size=13, ha="left", weight="bold", color=HOT)
    text(ax, 8.2, 4.5, "Ядро урана-235:\nкаждое деление даёт\n2–3 нейтрона,\nкаждый вызывает\nновое деление", size=9.5, ha="center")
    save(fig, "fission-chain-tree.png")


def fission_critical_mass():
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12, 4.1))
    rng = np.random.default_rng(7)

    def nuclei(ax, cx, cy, r, n, kind):
        pts = []
        while len(pts) < n:
            x, y = rng.uniform(-r, r, 2)
            if kind == "ball" and x * x + y * y > r * r:
                continue
            pts.append((cx + x, cy + y))
        for x, y in pts:
            ax.add_patch(Circle((x, y), 0.045 * (r / 1.3 + 0.5), fc=GOLD, ec="none", zorder=3))
        return pts

    for ax in (a1, a2, a3):
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.6, 2.6)
        ax.set_aspect("equal")
        ax.axis("off")
    # foil
    a1.add_patch(Rectangle((-0.12, -2.0), 0.24, 4.0, fc=GOLD_L, ec=INK, lw=1.4))
    a1.set_title("Тонкая фольга", fontsize=12)
    for ang, l in [(20, 2.2), (150, 2.2), (-40, 2.2), (200, 2.2), (60, 2.2)]:  # 60, not 80: an 80 degree ray runs along the foil
        a = np.deg2rad(ang)
        arrow(a1, (0, 0.0), (l * np.cos(a), l * np.sin(a)), color=NEUTRON, lw=1.4, ms=9)
    a1.text(0, -2.55, "нейтроны вылетают наружу:\nцепной реакции нет", ha="center", va="top", fontsize=10)
    # small ball
    a2.add_patch(Circle((0, 0), 1.0, fc=GOLD_L, ec=INK, lw=1.4))
    a2.set_title("Малый шарик", fontsize=12)
    for ang in (20, 110, 200, 290):
        a = np.deg2rad(ang)
        arrow(a2, (0, 0), (1.9 * np.cos(a), 1.9 * np.sin(a)), color=NEUTRON, lw=1.4, ms=9)
    a2.text(0, -2.55, "большинство нейтронов\nуходит, не встретив ядра", ha="center", va="top", fontsize=10)
    # large ball
    a3.add_patch(Circle((0, 0), 2.0, fc=GOLD_L, ec=INK, lw=1.6))
    a3.set_title("Масса не меньше критической", fontsize=12)
    pts = nuclei(a3, 0, 0, 1.9, 40, "ball")
    # each neutron ends on a drawn nucleus: take the nucleus 1.2..1.7 from the centre nearest to the wanted direction
    cand = [p for p in pts if 1.2 <= np.hypot(*p) <= 1.7]
    for ang in (30, 130, 250):
        tx, ty = min(cand, key=lambda p: abs((np.degrees(np.arctan2(p[1], p[0])) - ang + 180) % 360 - 180))
        cand.remove((tx, ty))
        arrow(a3, (0, 0), (tx, ty), color=NEUTRON, lw=1.4, ms=9)
        a3.plot(tx, ty, "*", color=HOT, ms=11, zorder=7)
    a3.text(0, -2.55, "нейтроны встречают ядра,\nчисло делений растёт", ha="center", va="top", fontsize=10)
    fig.tight_layout()
    save(fig, "fission-critical-mass.png")


def fission_neutron_moderation():
    fig, ax = blank(12.6, 4.2, (0, 12.6), (0, 4.2))
    # panel 1
    text(ax, 2.0, 3.85, "Быстрый нейтрон попал в уран-238", size=11.5, weight="bold")
    neutron(ax, 0.5, 2.3, 0.14)
    arrow(ax, (0.7, 2.3), (2.0, 2.3), color=HOT, lw=3)
    ax.add_patch(Circle((2.6, 2.3), 0.62, fc=LIGHT, ec=INK, lw=1.6))
    text(ax, 2.6, 2.3, r"$^{238}_{92}$U", size=12)
    text(ax, 2.0, 1.05, "поглощён, деления нет:\nнейтрон выбыл из реакции", size=10)
    ax.plot([4.35, 4.35], [0.3, 3.6], color=GREY, lw=1, ls="--")
    # panel 2
    text(ax, 6.55, 3.85, "Замедлитель", size=11.5, weight="bold")
    nuc = [(6.0, 2.9), (6.9, 2.05), (6.0, 1.3), (7.3, 3.0), (7.6, 1.4)]
    for x, y in nuc:
        ax.add_patch(Circle((x, y), 0.28, fc=WATER_L, ec=WATER, lw=1.4))
    pts = [(4.7, 2.5), (5.85, 2.75), (6.55, 2.25), (6.2, 1.55), (7.45, 1.2)]
    for a, b in zip(pts[:-1], pts[1:]):
        arrow(ax, a, b, color=GOLD, lw=1.6, ms=10, rad=0.1)
    neutron(ax, 4.7, 2.5, 0.14)
    text(ax, 6.55, 0.55, "при каждом ударе нейтрон отдаёт энергию\nядрам лёгкого вещества и замедляется", size=9.5)
    ax.plot([8.7, 8.7], [0.3, 3.6], color=GREY, lw=1, ls="--")
    # panel 3
    text(ax, 10.65, 3.85, "Медленный нейтрон попал в уран-235", size=11.5, weight="bold")
    neutron(ax, 9.0, 2.3, 0.14)
    arrow(ax, (9.2, 2.3), (10.0, 2.3), color=WATER, lw=1.2)
    ax.add_patch(Circle((10.7, 2.3), 0.62, fc=GOLD_L, ec=INK, lw=1.6))
    text(ax, 10.7, 2.3, r"$^{235}_{92}$U", size=12)
    text(ax, 10.7, 1.05, "деление: цепная реакция\nпродолжается", size=10)
    save(fig, "fission-neutron-moderation.png")


def fission_reactor_scheme():
    fig, ax = blank(15.0, 8.2, (0, 15.0), (0, 8.2))
    # vessel
    ax.add_patch(FancyBboxPatch((0.4, 1.6), 5.4, 4.4, boxstyle="round,pad=0.02,rounding_size=0.4", fc=WATER_L, ec=INK, lw=2))
    ax.add_patch(Rectangle((0.8, 5.95), 4.6, 0.3, fc=STEEL, ec=INK))
    # fuel rods and control rods
    for i in range(4):
        x = 1.1 + i * 1.15
        ax.add_patch(Rectangle((x, 2.0), 0.4, 3.7, fc=GOLD, ec=INK, lw=1.3, zorder=4))
    for i in range(4):
        x = 1.68 + i * 1.15
        ax.add_patch(Rectangle((x, 3.0), 0.3, 3.0, fc=LIGHT_METAL, ec=INK, lw=1.3, hatch="////", zorder=5))
    text(ax, 0.4, 6.9, "регулирующие стержни\n(бористая сталь)", size=10, ha="left")
    arrow(ax, (1.6, 6.55), (1.85, 5.8), color=GREY, lw=1.2, ms=9)
    # natural uranium needs a heavy-water moderator (U226 15:14)
    text(ax, 0.4, 1.1, "ТВЭЛы (природный уран) в тяжёлой воде", size=10, ha="left")
    text(ax, 0.4, 0.6, "тяжёлая вода: замедлитель и теплоноситель", size=10, color=WATER, ha="left")
    # primary loop
    hot = HOT
    ax.plot([5.8, 8.2], [5.2, 5.2], color=hot, lw=3, zorder=4)
    # steam generator
    ax.add_patch(Rectangle((7.2, 1.7), 2.0, 4.4, fc=PAPER, ec=INK, lw=2))
    ax.add_patch(Rectangle((7.2, 1.7), 2.0, 2.0, fc=WATER_L, ec="none", alpha=0.7, zorder=1))
    t = np.linspace(0, 1, 100)
    yy = 5.2 - t * 2.9
    xx = 8.2 + 0.7 * np.sin(t * 6 * np.pi)
    ax.plot(xx, yy, color=hot, lw=3, zorder=4)
    ax.plot([7.4, 7.6, 8.2 + 0.0], [5.2, 5.2, 5.2], color=hot, lw=3, zorder=4)
    ax.plot([8.2, 8.2], [2.3, 2.3], color=hot)
    # cold leg of the primary loop: lighter shade of the primary colour, not the secondary-loop blue
    ax.plot([8.2, 8.2, 6.6, 6.6, 5.8], [2.3, 1.95, 1.95, 2.6, 2.6], color=tint(RED, 0.4), lw=3)
    # pump
    ax.add_patch(Circle((6.6, 2.3), 0.28, fc=PAPER, ec=INK, lw=1.8, zorder=6))
    arrow(ax, (6.45, 2.2), (6.75, 2.4), color=INK, lw=1.2, ms=8)
    text(ax, 6.6, 1.25, "главный циркуляционный\nнасос", size=9, ha="center")
    # labels stay clear of the steam pipe (x=8.7) and of the generator wall (x=7.2)
    text(ax, 7.75, 6.5, "парогенератор\n(теплообменник)", size=10, ha="right")
    text(ax, 6.5, 5.7, "первый\nконтур", size=10, color=HOT)
    # secondary loop
    ax.plot([8.7, 8.7, 10.6], [6.1, 6.9, 6.9], color=BLUE, lw=3)
    text(ax, 9.5, 7.2, "пар", size=10, color=BLUE)
    # turbine
    ax.add_patch(Polygon([[10.6, 7.3], [10.6, 6.5], [11.9, 6.1], [11.9, 7.7]], fc=LIGHT, ec=INK, lw=2))
    text(ax, 11.25, 6.9, "турбина", size=10)
    ax.plot([11.9, 12.4], [6.9, 6.9], color=INK, lw=3)
    ax.add_patch(Circle((12.85, 6.9), 0.45, fc=GOLD_L, ec=INK, lw=2))
    text(ax, 12.85, 6.9, "G", size=13, weight="bold")
    text(ax, 12.85, 6.2, "генератор", size=10)
    arrow(ax, (12.85, 7.4), (12.85, 7.4), color=INK)
    # condenser and return
    ax.add_patch(Rectangle((10.7, 3.8), 1.6, 1.3, fc=WATER_L, ec=INK, lw=2))
    text(ax, 11.5, 4.45, "конденсатор", size=10)
    arrow(ax, (11.25, 6.05), (11.25, 5.15), color=BLUE, lw=2.2, ms=12)
    ax.plot([10.7, 9.6, 9.6, 8.7, 8.7], [4.0, 4.0, 1.4, 1.4, 1.7], color=BLUE, lw=3)
    arrow(ax, (8.7, 1.4), (8.7, 1.7), color=BLUE, lw=2.2, ms=12)
    text(ax, 10.2, 3.2, "вода возвращается\nв парогенератор", size=9.5, ha="left")
    text(ax, 11.6, 2.5, "второй контур", size=10, color=BLUE)
    # electricity
    arrow(ax, (13.35, 6.9), (14.0, 6.9), color=GOLD, lw=2.4, ms=12)
    text(ax, 14.05, 7.3, "электро-\nэнергия", size=10, ha="left", color=INK)
    save(fig, "fission-reactor-scheme.png")


def fission_fusion_dt():
    fig, ax = blank(12.4, 2.9, (0, 12.4), (0.4, 3.3))
    cy = 1.9

    def cluster(cx, cy_, ps, ns, label, sub):
        pts = {1: [(0, 0)], 2: [(-0.11, 0), (0.11, 0)], 3: [(0, 0.17), (-0.15, -0.08), (0.15, -0.08)], 4: [(-0.11, 0.11), (0.11, 0.11), (-0.11, -0.11), (0.11, -0.11)]}
        n_all = ps + ns
        coords = pts.get(n_all)
        if n_all == 5:
            coords = [(0, 0.3), (-0.26, 0.1), (0.26, 0.1), (-0.15, -0.22), (0.15, -0.22)]
        if n_all == 4:
            coords = [(-0.18, 0.18), (0.18, 0.18), (-0.18, -0.18), (0.18, -0.18)]
        if n_all == 2:
            coords = [(-0.17, 0), (0.17, 0)]
        if n_all == 3:
            coords = [(0, 0.22), (-0.22, -0.14), (0.22, -0.14)]
        order = ["p"] * ps + ["n"] * ns
        for (dx, dy), k in zip(coords, order):
            (proton if k == "p" else neutron)(ax, cx + dx, cy_ + dy, 0.15)
        text(ax, cx, cy_ - 0.75, label, size=12)
        text(ax, cx, cy_ - 1.15, sub, size=9.5)

    cluster(1.5, cy, 1, 1, r"$^{2}_{1}$H", "дейтерий")
    cluster(4.3, cy, 1, 2, r"$^{3}_{1}$H", "тритий")
    arrow(ax, (2.3, cy), (2.9, cy), color=HOT, lw=2.4)
    arrow(ax, (3.5, cy), (2.9, cy), color=HOT, lw=2.4)
    text(ax, 2.9, cy + 0.75, "сближение", size=9.5, color=HOT)
    arrow(ax, (5.2, cy), (6.6, cy), color=INK, lw=2)
    text(ax, 5.9, cy + 0.5, "T > 10 млн °C", size=10, color=HOT)
    cluster(8.0, cy, 2, 2, r"$^{4}_{2}$He", "гелий")
    neutron(ax, 10.2, cy + 0.5, 0.15)
    arrow(ax, (10.4, cy + 0.55), (11.5, cy + 0.85), color=NEUTRON, lw=1.8)
    text(ax, 10.2, cy - 0.05, r"$^{1}_{0}n$", size=12)
    text(ax, 10.2, cy - 0.45, "нейтрон", size=9.5)
    text(ax, 11.3, cy - 1.0, "+ 17,6 МэВ", size=12.5, color=HOT, weight="bold")
    save(fig, "fission-fusion-dt.png")


def fission_energy_per_nucleon():
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    names = ["деление урана-235\n200 МэВ на 235 нуклонов", "синтез D + T\n17,6 МэВ на 5 нуклонов"]
    vals = [200 / 235, 17.6 / 5]
    ax.bar(names, vals, color=[GOLD, HOT], width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.08, num(v, 2) + " МэВ", ha="center", fontsize=11.5)
    ax.text(0, 2.3, "синтез даёт на нуклон\n≈ в 4 раза больше", fontsize=11.5, ha="center")  # above the short bar, clear of the tall one
    ax.set_ylim(0, 4.3)
    ax.set_ylabel("энергия на один нуклон, МэВ")
    ax.set_title("Энергия на один нуклон топлива")
    ax.grid(True, axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "fission-energy-per-nucleon.png")


def fission_breeder():
    fig, ax = blank(10.4, 5.4, (0, 10.4), (0, 5.4))
    ax.add_patch(Circle((4.4, 2.7), 2.5, fc=GREEN_L, ec=INK, lw=2))
    ax.add_patch(Circle((4.4, 2.7), 1.25, fc=GOLD_L, ec=INK, lw=2))
    text(ax, 4.4, 2.7, "активная зона\nурана-235\n(без замедлителя)", size=10)
    text(ax, 4.4, 0.8, "зона воспроизводства: уран-238", size=10)
    for ang in (20, 55, 160, 215, 325):
        a = np.deg2rad(ang)
        arrow(ax, (4.4 + 1.3 * np.cos(a), 2.7 + 1.3 * np.sin(a)), (4.4 + 2.2 * np.cos(a), 2.7 + 2.2 * np.sin(a)), color=HOT, lw=1.8, ms=11)
    text(ax, 8.4, 4.3, "быстрые нейтроны\nуходят из активной\nзоны в зону\nвоспроизводства", size=9.5, color=HOT)
    arrow(ax, (7.5, 4.1), (6.2, 3.7), color=HOT, lw=1.0, ms=8)
    text(ax, 8.4, 2.0, r"$^{238}$U + n $\rightarrow$ плутоний", size=11)
    text(ax, 8.4, 1.3, "плутония накапливается\nв 1,5 раза больше,\nчем выгорело урана-235", size=9.5)
    save(fig, "fission-breeder.png")


if __name__ == "__main__":
    dose_quality_factor()
    dose_three_doses()
    dose_geiger_tube()
    dose_scale()
    dose_attenuation_curve()
    dose_lab_setup()
    dose_lab_data()
    dose_lab_fit()
    fission_uranium_nucleus()
    fission_chain_tree()
    fission_critical_mass()
    fission_neutron_moderation()
    fission_reactor_scheme()
    fission_fusion_dt()
    fission_energy_per_nucleon()
    fission_breeder()
