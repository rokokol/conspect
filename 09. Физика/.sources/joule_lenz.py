"""Graphs and schemes for the note "Работа и мощность тока. Закон Джоуля–Ленца" (section f11, lessons 163-166).

Graphs come from matplotlib, circuit schemes from TikZ (macros of circuit_diagrams.py and ohm_circuits.py).
Run: nix shell nixpkgs#poppler-utils nixpkgs#python3Packages.matplotlib -c python3 joule_lenz.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefix joule-)
Numbers that are not from the lectures carry the mark "не из лекции" on the picture itself.
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle

import circuit_diagrams as cd
import ohm_circuits  # noqa: F401  (adds the resistor and rheostat macros to the TikZ preamble)

cd.PREAMBLE += r"""
\usetikzlibrary{decorations.pathmorphing}
\newcommand{\coilc}[4]{\draw[decorate,decoration={coil,aspect=0.6,segment length=2.2mm,amplitude=1.6mm}](#1,#2)--(#3,#4);}
"""

OUT = cd.OUT

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ACCENT, ASH, BLUE, GREEN, INK, LIGHT, PAPER, RED, keep_dots, num, saver, tint

GRID = ASH
GREY = tint(INK, 0.45)  # outlines of neutral bodies, guides and small notes
ORANGE = ACCENT  # a highlighted quantity beside RED, BLUE and GREEN: the name is kept, the role is ACCENT
SOFT = tint(INK, 0.94)  # the pale body fill of a part

FIGS = {}  # matplotlib figures
TIKZ = {}  # tikz figures


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


def tikz(name):
    def deco(fn):
        TIKZ[name] = fn
        return fn

    return deco


save = saver(OUT)


def grid(ax):
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def blank(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def txt(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", scale=13, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


# ------------------------------------------------------------ power graphs


@fig("joule-p-vs-i")
def _():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    i = np.linspace(0, 6, 200)
    for r, col in ((10, BLUE), (20, RED)):
        ax.plot(i, i**2 * r, color=col, lw=2.4, label=rf"$R={r}\ \mathrm{{Ом}}$")
    for x in (2, 4):
        y = x**2 * 10
        ax.plot([x, x], [0, y], color=GREY, ls="--", lw=1)
        ax.plot([0, x], [y, y], color=GREY, ls="--", lw=1)
        ax.plot(x, y, "o", color=BLUE)
    ax.annotate("", xy=(4, 160), xytext=(2, 40), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6, connectionstyle="arc3,rad=-0.3"))
    ax.text(0.3, 400, r"$I\times2\ \Rightarrow\ P\times4$", color=ORANGE, fontsize=12, ha="left")
    ax.set_xlabel("$I$, А")
    ax.set_ylabel("$P$, Вт")
    ax.set_title("Мощность и сила тока")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 720)
    ax.legend(frameon=False, loc="upper left")
    grid(ax)
    save(f, "joule-p-vs-i")


@fig("joule-p-vs-r")
def _():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    r = np.linspace(0.5, 30, 600)
    p_u = 144 / r
    ax.plot(r[p_u <= 40], p_u[p_u <= 40], color=BLUE, lw=2.4, label=r"$U=12$ В: $P=U^2/R$")
    ax.plot(r, r * 1.0, color=RED, lw=2.4, label=r"$I=1$ А: $P=I^2R$")
    ax.plot(12, 12, "o", color=INK, zorder=5)
    ax.annotate("$R=12$ Ом\n$P=12$ Вт", xy=(12, 12), xytext=(15.5, 4), fontsize=11, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.text(5.2, 33, "при том же $U$\nбольше $R$ — меньше $P$", color=BLUE, fontsize=10, ha="left")
    ax.text(21.5, 30, "при том же $I$\nбольше $R$ — больше $P$", color=RED, fontsize=10, ha="center")
    ax.set_xlabel("$R$, Ом")
    ax.set_ylabel("$P$, Вт")
    ax.set_title("Мощность и сопротивление")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 40)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    grid(ax)
    save(f, "joule-p-vs-r")


@fig("joule-q-dependences")
def _():
    f, axs = plt.subplots(1, 3, figsize=(11.4, 3.8))
    t = np.linspace(0, 60, 100)
    axs[0].plot(t, 4 * 10 * t, color=BLUE, lw=2.4)
    axs[0].set_xlabel("$t$, с")
    axs[0].set_title("$Q\\propto t$", fontsize=13)
    axs[0].text(0.5, -0.36, "$I=2$ А, $R=10$ Ом", transform=axs[0].transAxes, ha="center", fontsize=10, color=GREY)
    r = np.linspace(0, 30, 100)
    axs[1].plot(r, 4 * r * 10, color=GREEN, lw=2.4)
    axs[1].set_xlabel("$R$, Ом")
    axs[1].set_title("$Q\\propto R$", fontsize=13)
    axs[1].text(0.5, -0.36, "$I=2$ А, $t=10$ с", transform=axs[1].transAxes, ha="center", fontsize=10, color=GREY)
    i = np.linspace(0, 4, 100)
    axs[2].plot(i, i**2 * 10 * 10, color=RED, lw=2.4)
    axs[2].set_xlabel("$I$, А")
    axs[2].set_title("$Q\\propto I^2$", fontsize=13)
    axs[2].text(0.5, -0.36, "$R=10$ Ом, $t=10$ с", transform=axs[2].transAxes, ha="center", fontsize=10, color=GREY)
    for ax in axs:
        ax.set_ylabel("$Q$, Дж")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        grid(ax)
    f.tight_layout()
    save(f, "joule-q-dependences")


@fig("joule-collisions")
def _():
    f = plt.figure(figsize=(11, 4.4))
    ax = f.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.2, 0.9), 5.6, 2.4, fc=SOFT, ec=INK, lw=1.6))
    ions = [(1.0 + 1.1 * k, y) for k in range(5) for y in (1.4, 2.8)]
    for x, y in ions:
        ax.add_patch(Circle((x, y), 0.2, fc=tint(RED, 0.85), ec=RED, lw=1.2))
        txt(ax, x, y, "+", size=10, color=RED)
    pts = [(0.4, 2.1), (1.0, 1.65), (2.1, 2.55), (3.2, 1.65), (4.3, 2.55), (5.4, 2.1)]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=BLUE, lw=1.6)
    arrow(ax, pts[-2], pts[-1], color=BLUE)
    ax.plot([pts[0][0]], [pts[0][1]], "o", color=BLUE, ms=7)
    for x, y in pts[1:-1]:
        ax.plot(x, y, "*", color=ORANGE, ms=13, zorder=5)
    txt(ax, 3.0, 3.85, "электрон разгоняется полем и отдаёт энергию ионам", size=10.5, color=BLUE)
    txt(ax, 3.0, 0.45, "колебания ионов = внутренняя энергия проводника", size=10.5, color=RED)
    ax2 = f.add_axes([0.58, 0.16, 0.4, 0.68])
    labels = ["ударов\nв секунду", "энергия\nодного удара", "теплота\nв секунду"]
    a1 = [1, 1, 1]
    a2 = [2, 2, 4]
    x = np.arange(3)
    ax2.bar(x - 0.19, a1, 0.36, color=BLUE, label="ток $I$")
    ax2.bar(x + 0.19, a2, 0.36, color=RED, label="ток $2I$")
    for xi, v in zip(x + 0.19, a2):
        ax2.text(xi, v + 0.08, f"×{v}", ha="center", fontsize=11, color=RED)
    ax2.set_xticks(x, labels)
    ax2.set_ylim(0, 4.7)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.legend(frameon=False, loc="upper left")
    ax2.set_title("Ток вырос вдвое", fontsize=12)
    save(f, "joule-collisions")


# ----------------------------------------------------------- appliances


@fig("joule-appliance-power")
def _():
    items = [
        ("лампа карманного фонаря $3{,}5$ В, $0{,}26$ А", 3.5 * 0.26, True),
        ("лампа $4$ В, $1$ Вт (задача 12.16)", 1.0, True),
        ("коммутаторная лампа $12$ В, $105$ мА", 12 * 0.105, True),
        ("светодиодная лампа", 5, True),
        ("лампа $18$ В, $1{,}1$ А", 18 * 1.1, True),
        ("лампа накаливания $25$ Вт", 25, True),
        ("лампа накаливания $40$ Вт", 40, True),
        ("ноутбук", 60, False),
        ("телевизор", 100, False),
        ("проекционная лампа", 500, True),
        ("микроволновая печь", 1000, False),
        ("электрочайник $220$ В, $40$ Ом", 220**2 / 40, True),
        ("утюг", 2000, False),
    ]
    items.sort(key=lambda t: t[1])
    f, ax = plt.subplots(figsize=(8.4, 5.4))
    for k, (name, p, lecture) in enumerate(items):
        ax.barh(k, p, color=BLUE if lecture else PAPER, ec=BLUE if lecture else GREY, hatch=None if lecture else "///", lw=1.2, height=0.7)
        label = f"{p:.0f}" if p >= 100 else num(p, ".3g")
        ax.text(p * 1.12, k, label + " Вт", va="center", fontsize=9.5, color=INK)
    ax.set_yticks(range(len(items)), [i[0] for i in items], fontsize=9.5)
    for lbl in ax.get_yticklabels():
        keep_dots(lbl)
    ax.set_xscale("log")
    ax.set_xlim(0.5, 9000)
    ax.set_xlabel("$P$, Вт (логарифмическая шкала)")
    ax.set_title("Мощность приборов")
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.barh([], [])
    from matplotlib.patches import Patch

    ax.legend(
        handles=[Patch(fc=BLUE, label="из лекции: $P=UI$ по надписи на приборе"), Patch(fc=PAPER, ec=GREY, hatch="///", label="ориентир, не из лекции")],
        frameon=False,
        loc="lower right",
        fontsize=9.5,
    )
    save(f, "joule-appliance-power")


@fig("joule-monthly-energy")
def _():
    f, ax = plt.subplots(figsize=(6.8, 4.6))
    d = np.linspace(0, 30, 31)
    for p, col, name in ((40, RED, "лампа накаливания $40$ Вт"), (25, ORANGE, "лампа накаливания $25$ Вт"), (5, GREEN, "светодиодная лампа $5$ Вт")):
        e = p * 10 * d / 1000
        ax.plot(d, e, color=col, lw=2.4, label=name)
        ax.text(30.4, e[-1], num(e[-1], ".3g") + " кВт·ч", color=col, va="center", fontsize=10)
    ax.set_xlabel("дни, по $10$ ч горения в день")
    ax.set_ylabel("расход энергии, кВт·ч")
    ax.set_title("Расход энергии за месяц")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 13)
    sec = ax.secondary_yaxis("right", functions=(lambda x: x * 3.6, lambda x: x / 3.6))
    sec.set_ylabel("МДж")
    sec.spines["right"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    grid(ax)
    f.subplots_adjust(right=0.78)
    save(f, "joule-monthly-energy")


@fig("joule-task-12-16-lamps")
def _():
    f, axs = plt.subplots(1, 2, figsize=(9, 4))
    names = ["карманный\nфонарь\n$4$ В, $1$ Вт", "лампа в прихожей\n$220$ В, $40$ Вт"]
    cur = [1 / 4, 40 / 220]
    res = [16, 1210]
    cols = [BLUE, ORANGE]
    axs[0].bar(names, cur, color=cols, width=0.55)
    for k, v in enumerate(cur):
        axs[0].text(k, v + 0.006, num(v, 3) + " А", ha="center", fontsize=11)
    axs[0].set_ylabel("$I=P/U$, А")
    axs[0].set_ylim(0, 0.3)
    axs[0].set_title("Сила тока")
    axs[1].bar(names, res, color=cols, width=0.55)
    axs[1].set_yscale("log")
    for k, v in enumerate(res):
        axs[1].text(k, v * 1.15, f"{v} Ом", ha="center", fontsize=11)
    axs[1].set_ylabel("$R=U^2/P$, Ом")
    axs[1].set_ylim(5, 5000)
    axs[1].set_title("Сопротивление нити")
    for ax in axs:
        ax.grid(True, axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    f.tight_layout()
    save(f, "joule-task-12-16-lamps")


@fig("joule-series-parallel-power")
def _():
    f, axs = plt.subplots(1, 2, figsize=(9.6, 4.2))
    cols = [BLUE, GREEN, ORANGE]
    ser_r = [10, 20, 30]
    ser_p = [3.6, 7.2, 10.8]
    par_r = [12, 20, 30]
    par_p = [300, 180, 120]
    for ax, r, p, title, tot in ((axs[0], ser_r, ser_p, "Последовательно, $I=0{,}6$ А", "21{,}6"), (axs[1], par_r, par_p, "Параллельно, $U=60$ В", "600")):
        lab = [f"$R_{k + 1}={v}$ Ом" for k, v in enumerate(r)]
        ax.bar(lab, p, color=cols, width=0.55)
        for k, v in enumerate(p):
            ax.text(k, v * 1.02, num(v, "") + " Вт", ha="center", va="bottom", fontsize=11)
        ax.set_title(title, fontsize=12)
        ax.set_ylim(0, max(p) * 1.25)
        ax.text(0.97, 0.95, f"$P=P_1+P_2+P_3={tot}$ Вт", transform=ax.transAxes, ha="right", va="top", fontsize=10.5, color=INK)
        ax.grid(True, axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.set_ylabel("$P$, Вт")
    fig_note = "наибольшая мощность — на наибольшем $R$"
    axs[0].text(0.5, -0.22, fig_note, transform=axs[0].transAxes, ha="center", fontsize=10.5, color=GREEN)
    axs[1].text(0.5, -0.22, "наибольшая мощность — на наименьшем $R$", transform=axs[1].transAxes, ha="center", fontsize=10.5, color=RED)
    f.tight_layout()
    save(f, "joule-series-parallel-power")


# ------------------------------------------------------------------ lamp


@fig("joule-lamp-structure")
def _():
    f, ax = blank(8.2, 7.4, (-5.2, 5.2), (-2.9, 6.1))
    ax.add_patch(Polygon([(-0.95, 1.21), (0.95, 1.21), (1.0, 0.0), (-1.0, 0.0)], fc=SOFT, ec="none"))
    ax.add_patch(Circle((0, 3.3), 2.3, fc=SOFT, ec="none"))
    ax.plot([-0.95, -1.0], [1.21, 0.0], color=INK, lw=2)
    ax.plot([0.95, 1.0], [1.21, 0.0], color=INK, lw=2)
    ax.add_patch(matplotlib.patches.Arc((0, 3.3), 4.6, 4.6, theta1=-65.6, theta2=245.6, color=INK, lw=2))
    ax.add_patch(Rectangle((-1.05, -1.6), 2.1, 1.6, fc=tint(INK, 0.8), ec=INK, lw=1.8))
    for y in (-1.3, -1.0, -0.7, -0.4, -0.1):
        ax.plot([-1.05, 1.05], [y, y + 0.08], color=INK, lw=0.9)
    ax.add_patch(Rectangle((-0.42, -1.75), 0.84, 0.17, fc=GREY, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((-0.38, 0.1), 0.76, 2.9, fc=tint(INK, 0.87), ec=INK, lw=1.4))
    ax.add_patch(Rectangle((-0.06, 0.2), 0.12, 2.0, fc=PAPER, ec=GREY, lw=1))
    ax.plot([-0.22, -0.22], [0.1, 3.1], color=RED, lw=1.6)
    ax.plot([0.22, 0.22], [0.1, 3.1], color=RED, lw=1.6)
    ax.plot([-0.22, -0.95, -0.9], [3.1, 3.8, 4.35], color=INK, lw=1.4)
    ax.plot([0.22, 0.95, 0.9], [3.1, 3.8, 4.35], color=INK, lw=1.4)
    ax.plot([0, 0], [3.0, 4.3], color=INK, lw=0.9)
    ax.plot([-0.9, -0.5], [4.25, 4.25], color=INK, lw=0.9)
    ax.plot([0.9, 0.5], [4.25, 4.25], color=INK, lw=0.9)
    xs = np.linspace(-0.9, 0.9, 400)
    ys = 4.35 + 0.16 * np.sin(xs * 44)
    ax.plot(xs, ys, color=ORANGE, lw=2)
    ax.plot([-0.22, -1.03], [0.1, -0.55], color=RED, lw=1.4)
    ax.plot([0.22, 0.05, 0.0], [0.1, -0.9, -1.75], color=RED, lw=1.4)

    def label(text, xy, xt, ha):
        ax.annotate(text, xy=xy, xytext=xt, ha=ha, va="center", fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY, lw=1))

    label("вольфрамовая нить", (-0.4, 4.4), (-3.5, 5.6), "center")
    label("стеклянная колба", (1.7, 4.9), (3.4, 5.6), "center")
    label("стойки нити", (-0.7, 3.95), (-4.3, 3.2), "center")
    label("вакуум или\nинертный газ", (1.3, 3.2), (3.9, 3.6), "center")
    label("стеклянная стойка", (0.4, 1.7), (3.9, 1.7), "center")
    label("трубка для откачки\nвоздуха", (0.0, 1.2), (-3.6, 1.3), "center")
    label("металлический цоколь", (1.0, -0.8), (3.9, -0.5), "center")
    label("центральный контакт", (0.3, -1.68), (3.7, -2.0), "center")
    save(f, "joule-lamp-structure")


@fig("joule-lamp-iv")
def _():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    u = np.linspace(0, 230, 300)
    rc, rh = 121.0, 1210.0
    r = rc + (rh - rc) * (u / 220) ** 0.8
    ax.plot(u, u / r, color=RED, lw=2.4, label="нить лампы (схематично)")
    ax.plot(u, u / rh, color=BLUE, lw=1.8, ls="--", label="модель курса: $R=1210$ Ом")
    ax.plot(u, u / rc, color=GREY, lw=1.4, ls=":", label="холодная нить: $R\\approx121$ Ом")
    ax.plot(220, 40 / 220, "o", color=INK, zorder=5)
    ax.annotate("рабочий режим\n$220$ В, $40$ Вт", xy=(220, 0.182), xytext=(120, 0.62), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlim(0, 235)
    ax.set_ylim(0, 1.3)
    ax.set_xlabel("$U$, В")
    ax.set_ylabel("$I$, А")
    ax.set_title("Лампа: сопротивление растёт с нагревом")
    ax.text(0.98, 0.03, "форма кривой — не из лекции", transform=ax.transAxes, ha="right", fontsize=9, color=GREY)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    grid(ax)
    save(f, "joule-lamp-iv")


@fig("joule-lamp-lifetime")
def _():
    f, ax = plt.subplots(figsize=(7.6, 3.4))
    rows = [("люминесцентная лампа", 10000, 15000, GREEN), ("лампа накаливания", 1000, 2000, ORANGE), ("перекальная фотолампа", 2, 3, RED)]
    for k, (n, a, b, col) in enumerate(rows):
        ax.barh(k, b - a, left=a, color=col, height=0.5)
        ax.text(b * 1.15, k, f"{a}–{b} ч", va="center", fontsize=11)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_xscale("log")
    ax.set_xlim(1, 100000)
    ax.set_xlabel("срок службы, ч (логарифмическая шкала)")
    ax.set_title("Срок службы ламп")
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(f, "joule-lamp-lifetime")


@fig("joule-energy-conversion")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.4, 3.8), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axs[0]
    ax.barh([0], [5], color=ORANGE, height=0.5)
    ax.barh([0], [95], left=[5], color=RED, height=0.5, alpha=0.75)
    ax.text(2.5, 0.42, "свет\n3–5 %", ha="center", va="bottom", fontsize=10.5, color=ORANGE)
    ax.text(52, 0, "теплота: почти вся потреблённая энергия", ha="center", va="center", fontsize=10.5, color=PAPER)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 1.3)
    ax.set_yticks([])
    ax.set_xlabel("доля потреблённой энергии, %")
    ax.set_title("Лампа накаливания", fontsize=12)
    ax.spines["left"].set_visible(False)
    ax = axs[1]
    lab = ["нагреватель", "тепловой насос\n(кондиционер)"]
    used = [700, 700]
    heat = [700, 3000]
    x = np.arange(2)
    ax.bar(x - 0.19, used, 0.36, color=BLUE, label="потреблено из сети")
    ax.bar(x + 0.19, heat, 0.36, color=RED, label="теплоты в комнате")
    for xi, v in zip(x - 0.19, used):
        ax.text(xi, v + 50, f"{v} Дж", ha="center", fontsize=10.5)
    for xi, v in zip(x + 0.19, heat):
        ax.text(xi, v + 50, f"{v} Дж", ha="center", fontsize=10.5)
    ax.set_xticks(x, lab)
    ax.set_ylim(0, 3700)
    ax.set_ylabel("энергия, Дж")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.set_title("Обогрев комнаты", fontsize=12)
    f.tight_layout()
    save(f, "joule-energy-conversion")


# -------------------------------------------------- short circuit, fuse


@fig("joule-short-circuit-current")
def _():
    u, rw = 220.0, 0.5
    f, axs = plt.subplots(1, 2, figsize=(10.6, 4.2))
    r = np.linspace(0, 60, 601)
    i = u / (r + rw)
    axs[0].plot(r, i, color=RED, lw=2.4)
    axs[0].plot(0, u / rw, "o", color=RED)
    axs[0].annotate("замыкание: $R\\to0$,\n$I\\approx440$ А", xy=(0.4, 430), xytext=(12, 380), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY))
    axs[0].plot(40, u / (40 + rw), "o", color=BLUE)
    axs[0].annotate("нагрузка $40$ Ом:\n$5{,}4$ А", xy=(40, 5.4), xytext=(30, 120), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY))
    axs[0].set_xlabel("сопротивление нагрузки $R$, Ом")
    axs[0].set_ylabel("$I=U/(R+R_\\mathrm{пр})$, А")
    axs[0].set_title("Сила тока в цепи")
    axs[0].set_xlim(0, 60)
    axs[0].set_ylim(0, 460)
    grid(axs[0])
    p = i**2 * rw
    axs[1].semilogy(r, p, color=RED, lw=2.4)
    axs[1].plot(0, u**2 / rw, "o", color=RED)
    axs[1].plot(40, (u / (40.5)) ** 2 * rw, "o", color=BLUE)
    axs[1].text(1.5, 5.5e4, "$\\approx97$ кВт", color=RED, fontsize=10.5)
    axs[1].text(41.5, 40, "$\\approx15$ Вт", color=BLUE, fontsize=10.5)
    axs[1].set_xlabel("сопротивление нагрузки $R$, Ом")
    axs[1].set_ylabel("$P_\\mathrm{пр}=I^2R_\\mathrm{пр}$, Вт")
    axs[1].set_title("Мощность в проводах")
    axs[1].set_xlim(0, 60)
    axs[1].set_ylim(5, 3e5)
    axs[1].grid(True, color=GRID, lw=0.8)
    f.text(0.5, -0.02, "$U=220$ В, сопротивление проводов $R_\\mathrm{пр}=0{,}5$ Ом — не из лекции", ha="center", fontsize=9.5, color=GREY)
    f.tight_layout()
    save(f, "joule-short-circuit-current")


@fig("joule-fuse-device")
def _():
    f, ax = blank(8.4, 5.2, (0, 8.4), (0, 5.2))

    def fuse(y, wire_lw, label, broken=False):
        ax.add_patch(Rectangle((1.2, y - 0.4), 4.2, 0.8, fc=SOFT, ec=INK, lw=1.6))
        for x0 in (0.7, 5.4):
            ax.add_patch(Rectangle((x0, y - 0.46), 0.5, 0.92, fc=tint(INK, 0.7), ec=INK, lw=1.4))
        if broken:
            ax.plot([1.2, 2.9], [y, y], color=ORANGE, lw=wire_lw)
            ax.plot([3.7, 5.4], [y, y], color=ORANGE, lw=wire_lw)
            ax.plot([3.3], [y + 0.08], "o", color=GREY, ms=5)
        else:
            ax.plot([1.2, 5.4], [y, y], color=ORANGE, lw=wire_lw)
        txt(ax, 6.2, y, label, size=10.5, ha="left")

    fuse(4.2, 5.5, "$3$ А: толстая проволока,\nмалое $R$")
    fuse(2.6, 1.4, "$0{,}5$ А: тонкая проволока,\nбольшее $R$, плавится раньше")
    fuse(1.0, 1.4, "сработал: проволока расплавилась,\nцепь разомкнута", broken=True)
    txt(ax, 3.0, 4.95, "стеклянная трубка со свинцовой проволокой", size=10.5)
    save(f, "joule-fuse-device")


@fig("joule-fuse-time-current")
def _():
    f, axs = plt.subplots(1, 2, figsize=(10.4, 4.2))
    k = np.linspace(1.05, 12, 400)
    t = 1 / (k**2 - 1)
    axs[0].semilogy(k, t, color=RED, lw=2.4)
    axs[0].axvline(1, color=GREY, ls="--", lw=1)
    axs[0].text(1.5, 8, "ток ниже номинала:\nне плавится", fontsize=10, color=GREY, va="top")
    axs[0].annotate("несколько\nноминалов:\nдоли секунды", xy=(8, 1 / 63), xytext=(6.3, 0.35), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    axs[0].set_xlabel("$I/I_\\mathrm{ном}$")
    axs[0].set_ylabel("время до плавления, отн. ед.")
    axs[0].set_title("Быстрее при большем токе")
    axs[0].set_xlim(0.8, 12)
    axs[0].set_ylim(5e-3, 10)
    axs[0].grid(True, color=GRID, lw=0.8)
    axs[0].text(0.98, 0.02, "схематично, не из лекции", transform=axs[0].transAxes, ha="right", fontsize=9, color=GREY)
    s = [1, 1 / 4]
    p = [1 * 1.0, 4 * 1.0]
    axs[1].bar(["толстая\nпроволока", "тонкая\nпроволока (в 4 раза\nменьше сечение)"], p, color=[BLUE, RED], width=0.5)
    for x, v in enumerate(p):
        axs[1].text(x, v + 0.08, f"$P\\times{int(v)}$", ha="center", fontsize=12)
    axs[1].set_ylim(0, 5)
    axs[1].set_yticks([])
    axs[1].spines["left"].set_visible(False)
    axs[1].set_title("Один и тот же ток: $P=I^2R$, $R\\propto1/S$", fontsize=11.5)
    axs[1].text(0.02, 0.95, "пример, не из лекции", transform=axs[1].transAxes, ha="left", va="top", fontsize=9, color=GREY)
    f.tight_layout()
    save(f, "joule-fuse-time-current")


# ---------------------------------------------------------- tikz schemes


@tikz("joule-calorimeter-setup")
def _():
    return r"""
% calorimeter
\draw[fill=water!60](.45,.55)rectangle(3.55,2.5);
\draw(0,0)--(0,3.4)(4,0)--(4,3.4)(0,0)--(4,0);
\draw(.45,.55)--(.45,3.2)(3.55,.55)--(3.55,3.2)(.45,.55)--(3.55,.55);
\draw(1.2,0)--(1.4,.55)(2.8,0)--(2.6,.55);
\draw[fill=soft](2.1,3.5)rectangle(3.3,3.68);
\draw[fill=paper](1.32,.75)rectangle(1.48,3.9);\fill[bad](1.32,.75)rectangle(1.48,1.8);
\draw(2.4,3.5)--(2.4,2.4)(2.4,1.0)--(3.0,1.0)--(3.0,3.5);
\coilc{2.4}{2.4}{2.4}{1.0}
\fill(2.4,3.6)circle(.07)(3.0,3.6)circle(.07);
% circuit
\draw(2.4,3.6)--(2.4,6.3)--(5.2,6.3)(6.6,6.3)--(7.0,6.3)(8.2,6.3)--(9.0,6.3)(9.8,6.3)--(10.9,6.3)--(10.9,6.15);
\draw(3.0,3.6)--(3.0,4.2)--(10.9,4.2)--(10.9,4.35);
\draw(3.7,6.3)--(3.7,5.95)(3.7,4.55)--(3.7,4.2);\dotc{3.7}{6.3}\dotc{3.7}{4.2}
\meterc{3.7}{5.25}{90}{V}
\meterc{5.9}{6.3}{0}{A}
\cellc{7.6}{6.3}{0}{2}\sgn{6.85}{6.65}{$+$}\sgn{8.35}{6.65}{$-$}
\keyold{9.4}{6.3}{0}
\rheoc{10.9}{5.25}{-90}
\node[cp]at(5.9,5.7){амперметр};\node[cp]at(7.6,7.0){источник тока};\node[cp]at(9.4,7.0){ключ};
\node[cp,anchor=west]at(11.3,5.25){реостат};
\node[cp,anchor=west]at(4.15,5.0){вольтметр};
\node[cp,anchor=east]at(-.15,2.0){калориметр};
\node[cp]at(.75,4.35){термометр};
\node[cp,anchor=west]at(4.25,1.6){спираль,\\ вода};
\draw[->,thin](.75,4.0)--(1.3,3.7);
"""


@tikz("joule-task-12-20")
def _():
    return r"""
\draw(0,0)--(1.3,0)(2.7,0)--(4.3,0)(5.7,0)--(7.3,0)(8.7,0)--(10,0);
\resc{2}{0}{0}\resc{5}{0}{0}\resc{8}{0}{0}
\draw[fill=paper](0,0)circle(.07)(10,0)circle(.07);
\node[cp]at(2,.6){$R_1=10$ Ом};\node[cp]at(5,.6){$R_2=20$ Ом};\node[cp]at(8,.6){$R_3=30$ Ом};
\node[cp]at(2,-.6){$P_1-?$};\node[cp]at(5,-.6){$P_2-?$};\node[cp]at(8,-.6){$P_3-?$};
\ca{.3}{-1.3}{1.2}{-1.3}\node[cur,font=\small]at(.75,-1.6){$I$};
\ca{3.3}{-1.3}{4.2}{-1.3}\node[cur,font=\small]at(3.75,-1.6){$I$};
\ca{6.3}{-1.3}{7.2}{-1.3}\node[cur,font=\small]at(6.75,-1.6){$I$};
\vdim{0}{1.7}{10}{$U=36$ В}\draw[dashed,grey](0,.1)--(0,1.7)(10,.1)--(10,1.7);
"""


@tikz("joule-task-12-21")
def _():
    return r"""
\draw(0,0)--(1.5,0)(1.5,2)--(1.5,-2)(7,2)--(7,-2)(7,0)--(8.5,0);
\foreach\y in{2,0,-2}{\draw(1.5,\y)--(3.3,\y)(4.7,\y)--(7,\y);\resc{4}{\y}{0}}
\dotc{1.5}{0}\dotc{7}{0}
\draw[fill=paper](0,0)circle(.07)(8.5,0)circle(.07);
\node[cp]at(4,2.5){$R_1=12$ Ом};\node[cp]at(4,.5){$R_2=20$ Ом};\node[cp]at(4,-1.5){$R_3=30$ Ом};
\node[cp,anchor=west]at(7.3,2){$P_1-?$};\node[cp,anchor=west]at(7.3,.5){$P_2-?$};\node[cp,anchor=west]at(7.3,-2){$P_3-?$};
\vdim{0}{-3.0}{8.5}{$U=60$ В}\draw[dashed,grey](0,-.1)--(0,-3.0)(8.5,-.1)--(8.5,-3.0);
"""


@tikz("joule-wire-vs-lamp")
def _():
    return r"""
% the wires stop at the leads of the resistor (3.8 and 5.2 at y = 0) and of the lamp (4.8 and 6.2 at y = 3.2)
\draw(0,1.3)--(0,0)--(3.8,0)(5.2,0)--(8,0)--(8,3.2)--(6.2,3.2)(4.8,3.2)--(3.7,3.2)(2.3,3.2)--(0,3.2)--(0,1.9);
\cellc{0}{1.6}{-90}{3}\sgn{-.4}{2.3}{$+$}\sgn{-.4}{.9}{$-$}
\resc{3}{3.2}{0}\lampc{5.5}{3.2}{0}\resc{4.5}{0}{0}
\fill[glow,opacity=.45](5.5,3.2)circle(.75);\lampc{5.5}{3.2}{0}
\node[cp]at(3,3.9){шнур: $R_\text{шн}$ мало};\node[cp]at(5.5,4.2){нить: $R_\text{л}$ велико};\node[cp]at(4.5,-.6){обратный шнур: $R_\text{шн}$ мало};
\ca{.9}{3.65}{1.7}{3.65}\node[cur,font=\small]at(1.3,3.95){$I$};
\node[cp,anchor=west]at(8.3,1.6){$P=I^2R$\\при одном $I$\\больше там,\\где больше $R$};
"""


@tikz("joule-short-circuit-scheme")
def _():
    return r"""
% the wires stop at the leads of the two wire resistors (1.3 and 2.7) and of the heater (0.9 and 2.3)
\draw(0,1.3)--(0,0)--(1.3,0)(2.7,0)--(8.6,0)--(8.6,.9)(8.6,2.3)--(8.6,3.2)--(2.7,3.2)(1.3,3.2)--(0,3.2)--(0,1.9);
\cellc{0}{1.6}{-90}{3}\sgn{-.4}{2.3}{$+$}\sgn{-.4}{.9}{$-$}
\resc{2}{3.2}{0}\resc{2}{0}{0}
\node[cp]at(2,3.85){провод $R_\text{пр}$};\node[cp]at(2,.6){провод $R_\text{пр}$};
\resc{8.6}{1.6}{-90}\node[cp,anchor=west]at(9.0,1.6){нагреватель\\$R\gg R_\text{пр}$};
\draw[bad,line width=1.8pt](8.6,3.2)--(6.2,3.2)--(6.2,0)--(8.6,0);
\dotc{8.6}{3.2}\dotc{8.6}{0}\dotc{6.2}{3.2}\dotc{6.2}{0}
\node[bad,cp]at(5.2,1.6){замыкание:\\$R\approx0$};
\ca{3.6}{3.55}{4.7}{3.55}\node[cur,font=\small]at(4.15,3.85){$I\to$ велико};
"""


def build_tikz(name):
    cd.build(name, TIKZ[name]())


if __name__ == "__main__":
    wanted = sys.argv[1:] or (list(FIGS) + list(TIKZ))
    for n in wanted:
        if n in FIGS:
            FIGS[n]()
        else:
            build_tikz(n)
