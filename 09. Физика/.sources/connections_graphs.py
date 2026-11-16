"""Graphs and bar charts for the note "Соединение проводников" (section f11, lessons 157-162).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 connections_graphs.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefix connection-)
The circuit schemes are in connections.py
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.category import StrCategoryLocator

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "11. Электрические явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ASH, BLUE, COPPER, GREEN, INK, PAPER, RED, VIOLET, keep_dots, num, saver, tint

GRID = ASH
C1, C2, C3, C4, C5 = RED, BLUE, GREEN, VIOLET, COPPER  # curves of several cases, in the order of theme.SERIES
GREY = tint(INK, 0.4)  # guides and small notes
PALETTE = [C2, C1, C3, C4, C5, GREY]

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


COMMA = mticker.FuncFormatter(lambda v, _: num(v, None))


_save = saver(OUT)


def save(f, name):
    for ax in f.axes:
        ax.yaxis.set_major_formatter(COMMA)
        if not isinstance(ax.xaxis.get_major_locator(), (mticker.FixedLocator, StrCategoryLocator)):
            ax.xaxis.set_major_formatter(COMMA)
    _save(f, name)


def grid(ax):
    ax.grid(color=GRID, linewidth=0.8, axis="y")
    ax.set_axisbelow(True)


def stacked(name, values, labels, unit, total_label, title, colors=None, fmt="{:g}", w=7.2, part_unit=None):
    """One horizontal stacked bar: the parts of one quantity add up to the whole."""
    f, ax = plt.subplots(figsize=(w, 1.9))
    left = 0.0
    colors = colors or PALETTE
    for i, (v, lab) in enumerate(zip(values, labels)):
        ax.barh(0, v, left=left, height=0.55, color=colors[i % len(colors)], edgecolor=PAPER, linewidth=1.5)
        ax.text(left + v / 2, 0, f"{lab}\n{num(v, fmt[2:-1])} {part_unit or unit}", ha="center", va="center", color=PAPER, fontsize=10, fontweight="bold")
        left += v
    ax.annotate("", xy=(0, 0.52), xytext=(left, 0.52), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    ax.text(left / 2, 0.6, total_label, ha="center", va="bottom", color=INK, fontsize=11)
    ax.set_xlim(0, left * 1.02)
    ax.set_ylim(-0.45, 0.95)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(f"{unit}")
    keep_dots(ax.set_title(title, loc="left"))
    save(f, name)


def bars(name, labels, values, unit, title, color=C2, ylabel=None, fmt="{:g}", w=5.6, h=3.6, refs=()):
    f, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(values))
    ax.bar(x, values, color=color, width=0.6)
    for xi, v in zip(x, values):
        ax.text(xi, v + max(values) * 0.02, num(v, fmt[2:-1]), ha="center", va="bottom", fontsize=10)
    for y, txt, c in refs:
        ax.axhline(y, color=c, linestyle="--", linewidth=1.2)
        ax.text(2.5, y + max(values) * 0.06, txt, ha="center", va="bottom", color=c, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_ylabel(ylabel or unit)
    keep_dots(ax.set_title(title, loc="left"))
    grid(ax)
    save(f, name)


@fig("connection-n-resistors-graph")
def _():
    N = np.arange(1, 11)
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(N, N * 1.0, "o-", color=C1, label=r"последовательно: $R=nR_1$")
    Nn = np.linspace(1, 10, 200)
    ax.plot(N, 1.0 / N, "o-", color=C2, label=r"параллельно: $R=R_1/n$")
    ax.axhline(1.0, color=GREY, linestyle="--", linewidth=1)
    ax.text(10, 1.12, r"$R_1=1$ кОм", ha="right", va="bottom", color=GREY, fontsize=10)
    ax.plot([4], [4], "o", markersize=11, markerfacecolor="none", markeredgecolor=C1)
    ax.annotate("4 резистора: 4 кОм", xy=(4, 4), xytext=(4.7, 2.5), arrowprops=dict(arrowstyle="->", color=C1), color=C1)
    ax.plot([5], [0.2], "o", markersize=11, markerfacecolor="none", markeredgecolor=C2)
    ax.annotate("5 резисторов: 200 Ом", xy=(5, 0.2), xytext=(5.6, 1.7), arrowprops=dict(arrowstyle="->", color=C2), color=C2)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0, 10.8)
    ax.set_xticks(N)
    ax.set_xlabel("число одинаковых резисторов $n$")
    ax.set_ylabel("общее сопротивление, кОм")
    ax.set_title("Сопротивление $n$ одинаковых резисторов по $1$ кОм")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False)
    save(f, "connection-n-resistors-graph")


@fig("connection-parallel-less-than-min")
def _():
    R2 = np.linspace(0.5, 60, 400)
    R1 = 10.0
    Rp = R1 * R2 / (R1 + R2)
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(R2, Rp, color=C2, linewidth=2, label=r"$R_\mathrm{пар}=\dfrac{R_1R_2}{R_1+R_2}$")
    ax.plot(R2, R2, color=GREY, linestyle=":", linewidth=1.2, label=r"$R=R_2$ (для сравнения)")
    ax.axhline(R1, color=C1, linestyle="--", linewidth=1.2)
    ax.text(59, R1 + 0.3, r"$R_1=10$: предел при $R_2\to\infty$", ha="right", va="bottom", color=C1, fontsize=10)
    ax.plot([20], [20 / 3], "o", color=C2, markersize=9)
    ax.annotate(r"$10\parallel20=\dfrac{20}{3}\approx6{,}7$", xy=(20, 20 / 3), xytext=(26, 2.0), arrowprops=dict(arrowstyle="->", color=C2), color=C2)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 16)
    ax.set_xlabel(r"$R_2$, Ом")
    ax.set_ylabel(r"$R_\mathrm{пар}$, Ом")
    ax.set_title(r"Параллельное соединение с $R_1=10$ Ом: результат меньше меньшего")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=False)
    save(f, "connection-parallel-less-than-min")


@fig("connection-series-distribution")
def _():
    """Task 7.15: R = 1, 4, 2 Ом in series, I = 1 А: equal current, voltage proportional to resistance."""
    R = [1, 4, 2]
    I = [1, 1, 1]
    U = [r * i for r, i in zip(R, I)]
    f, axs = plt.subplots(1, 3, figsize=(10.4, 3.5))
    lab = ["$R_1$", "$R_2$", "$R_3$"]
    for ax, vals, ttl, unit, col in zip(axs, [R, I, U], ["Сопротивление", "Сила тока", "Напряжение"], ["Ом", "А", "В"], [C3, C1, C2]):
        ax.bar(lab, vals, color=col, width=0.6)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.06, f"{v:g}", ha="center", va="bottom")
        ax.set_ylim(0, 5)
        ax.set_ylabel(unit)
        ax.set_title(ttl)
        grid(ax)
    axs[1].text(1, 2.0, "одинакова", ha="center", color=C1, fontsize=11)
    axs[2].axhline(7, color=INK, linestyle="--", linewidth=0)
    axs[2].text(1, 4.9, "сумма $U_1+U_2+U_3=7$ В", ha="center", color=INK, fontsize=10)
    f.suptitle("Последовательное соединение: ток один, напряжение делится пропорционально сопротивлению", y=1.03, fontsize=12)
    save(f, "connection-series-distribution")


@fig("connection-parallel-distribution")
def _():
    """Task 8.28: R = 4, 6, 8 Ом in parallel at U = 2,4 В."""
    R = np.array([4.0, 6.0, 8.0])
    U = 2.4
    I = U / R
    G = 1 / R
    f, axs = plt.subplots(2, 2, figsize=(9.6, 6.4))
    lab = ["$R_1$", "$R_2$", "$R_3$"]
    ax = axs[0, 0]
    ax.bar(lab + [r"$R_\mathrm{пар}$"], list(R) + [24 / 13], color=[C3, C3, C3, C1], width=0.6)
    for i, v in enumerate(list(R) + [24 / 13]):
        ax.text(i, v + 0.15, f"{v:.2f}".rstrip("0").rstrip(".") if i < 3 else "1,85", ha="center")
    ax.set_ylim(0, 9.5)
    ax.set_title("Сопротивление, Ом")
    grid(ax)
    ax = axs[0, 1]
    ax.bar(lab, [U] * 3, color=C2, width=0.6)
    for i in range(3):
        ax.text(i, U + 0.06, "2,4", ha="center")
    ax.set_ylim(0, 3.2)
    ax.set_title("Напряжение одинаково, В")
    grid(ax)
    ax = axs[1, 0]
    ax.bar(lab, I, color=C1, width=0.6)
    for i, v in enumerate(I):
        ax.text(i, v + 0.015, num(v, 1), ha="center")
    ax.axhline(I.sum(), color=INK, linestyle="--", linewidth=1)
    ax.text(2.4, I.sum() + 0.02, "$I=I_1+I_2+I_3=1{,}3$ А", ha="right", va="bottom", fontsize=10)
    ax.set_ylim(0, 1.6)
    ax.set_title("Сила тока в ветвях, А")
    grid(ax)
    ax = axs[1, 1]
    bottom = 0.0
    for i, g in enumerate(G):
        ax.bar([0], [g], bottom=bottom, color=[C3, C4, C5][i], width=0.5)
        ax.text(0, bottom + g / 2, f"$G_{i + 1}=1/{int(R[i])}$", ha="center", va="center", color=PAPER, fontsize=10, fontweight="bold")
        bottom += g
    ax.text(0, bottom + 0.012, r"$G=13/24\approx0{,}54$ См", ha="center", va="bottom", fontsize=10)
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(0, 0.68)
    ax.set_xticks([])
    ax.set_title("Проводимости складываются, См")
    grid(ax)
    f.suptitle("Параллельное соединение $4$, $6$ и $8$ Ом на $2{,}4$ В", fontsize=12)
    f.tight_layout()
    save(f, "connection-parallel-distribution")


@fig("connection-six-parallel-count")
def _():
    R = [10, 12, 15, 20, 30, 60]
    n = [60 // r for r in R]
    f, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar([str(r) for r in R], n, color=C2, width=0.6)
    for i, v in enumerate(n):
        ax.text(i, v + 0.1, f"{v}", ha="center", va="bottom")
    ax.set_xlabel("резистор в цепи, Ом")
    ax.set_ylabel("сколько резисторов по $60$ Ом")
    ax.set_ylim(0, 7.5)
    # sum(n) = 21 takes the singular "резистор"
    ax.set_title(f"Всего {sum(n)} резистор по $60$ Ом: $R=60/{sum(n)}=20/7$ Ом")
    grid(ax)
    save(f, "connection-six-parallel-count")


@fig("connection-task-7-2-bars")
def _():
    stacked("connection-task-7-2-bars", [0.5, 2.5], ["$U_1$", "$U_2$"], "В", r"$U_\mathrm{ист}=3$ В", "Задача 7.2: напряжение источника разделилось между резисторами", [C2, C1])


@fig("connection-task-7-12-bars")
def _():
    stacked("connection-task-7-12-bars", [18, 6], ["$U_1$", "$U_2$"], "В", r"$U=24$ В на обоих резисторах", "Задача 7.12: напряжения на резисторах $6$ и $2$ Ом", [C2, C1])


@fig("connection-task-7-15-bars")
def _():
    stacked("connection-task-7-15-bars", [1, 4, 2], ["$U_1$", "$U_2$", "$U_3$"], "В", r"$U_\mathrm{ист}=7$ В", "Задача 7.15: напряжения на резисторах $1$, $4$ и $2$ Ом", [C3, C2, C1])


@fig("connection-task-7-19-bars")
def _():
    stacked("connection-task-7-19-bars", [3.9, 5.1], [r"$U_\mathrm{р}$", r"$U_\mathrm{л}$"], "В", r"$U=9$ В", "Задача 7.19: реостат забирает на себя лишние $3{,}9$ В", [C4, C5], fmt="{:g}")


@fig("connection-task-8-20-bars")
def _():
    stacked("connection-task-8-20-bars", [0.125, 0.375], ["$I_1$", "$I_2$"], "А", "$I=0{,}5$ А через источник", "Задача 8.20: токи в резисторах $180$ и $60$ Ом", [C2, C1], fmt="{:.3g}")


@fig("connection-task-8-24-bars")
def _():
    stacked("connection-task-8-24-bars", [75, 25], ["$I_1$: 500 Ом", "$I_2$: 1,5 кОм"], "%", "весь ток $I$", "Задача 8.24: ток делится обратно пропорционально сопротивлению", [C2, C1], w=7.2)


@fig("connection-task-11-22b-currents")
def _():
    bars("connection-task-11-22b-currents", ["$I_1$", "$I_2$", "$I_3$"], [8, 4, 4], "мА", "Задача 11.22 б: токи в резисторах по $1$ кОм при $12$ В", C1, w=4.6, h=3.4)


@fig("connection-task-11-22v-currents")
def _():
    bars("connection-task-11-22v-currents", ["$I_1$", "$I_2$", "$I_3$", "$I_4$"], [12, 6, 6, 12], "мА", "Задача 11.22 в: токи в резисторах по $1$ кОм при $12$ В", C1, w=5.2, h=3.4)


@fig("connection-task-11-32-currents")
def _():
    bars(
        "connection-task-11-32-currents",
        [f"$I_{i}$" for i in range(1, 7)],
        [200, 50, 150, 50, 200, 50],
        "мА",
        "Задача 11.32: токи в резисторах по $200$ Ом при $110$ В",
        C1,
        w=6.4,
        h=3.6,
        refs=[(200, "весь ток $I=200$ мА", GREY)],
    )


@fig("connection-task-839-ring-graph")
def _():
    R0 = 360.0
    x = np.linspace(0, R0, 400)
    r = x * (R0 - x) / R0
    f, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(x, r, color=C2, linewidth=2)
    ax.axhline(80, color=C1, linestyle="--", linewidth=1.2)
    ax.text(352, 83, r"$r=80$ Ом", ha="right", va="bottom", color=C1)
    for xv in (120, 240):
        ax.plot([xv], [80], "o", color=C1, markersize=9)
        ax.plot([xv, xv], [0, 80], color=C1, linestyle=":", linewidth=1.2)
    # the numbers stand right of the dotted lines so that the lines do not cross them
    ax.text(126, 6, "$120$", ha="left", color=C1)
    ax.text(246, 6, "$240$", ha="left", color=C1)
    ax.plot([180], [90], "o", color=INK, markersize=7)
    ax.annotate("противоположные точки: $90$ Ом, наибольшее возможное", xy=(180, 90), xytext=(30, 100), arrowprops=dict(arrowstyle="->", color=INK), color=INK, fontsize=10)
    ax.set_xlim(0, R0)
    ax.set_ylim(0, 112)
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360])
    ax.set_xlabel(r"сопротивление дуги $R$ между точками подключения, Ом")
    ax.set_ylabel(r"сопротивление кольца $r$ между ними, Ом")
    ax.set_title(r"Кольцо $360$ Ом: $r=\dfrac{R(R_0-R)}{R_0}$")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(f, "connection-task-839-ring-graph")


@fig("connection-task-649-graph")
def _():
    k = np.linspace(1, 6, 200)
    f, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(k, k**2, color=C2, linewidth=2)
    ax.plot([4], [16], "o", color=C1, markersize=9)
    ax.plot([4, 4], [0, 16], color=C1, linestyle=":", linewidth=1.2)
    ax.plot([1, 4], [16, 16], color=C1, linestyle=":", linewidth=1.2)
    ax.annotate("длина в $4$ раза больше: $R'=16R$", xy=(4, 16), xytext=(1.3, 25), arrowprops=dict(arrowstyle="->", color=C1), color=C1)
    ax.set_xlim(1, 6)
    ax.set_ylim(0, 37)
    ax.set_xlabel(r"во сколько раз вытянули провод, $k=l'/l$")
    ax.set_ylabel(r"$R'/R$")
    ax.set_title(r"Волочение при постоянном объёме: $R'/R=k^2$")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(f, "connection-task-649-graph")


@fig("connection-task-8-33-graph")
def _():
    n = np.arange(1, 8)
    f, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(n, 3.0 * n**2, "o-", color=C2)
    ax.plot([3], [27], "o", markersize=12, markerfacecolor="none", markeredgecolor=C1)
    ax.annotate(r"$n=3$: $R_0=27$ Ом", xy=(3, 27), xytext=(3.6, 12), arrowprops=dict(arrowstyle="->", color=C1), color=C1)
    ax.axhline(3, color=GREY, linestyle="--", linewidth=1)
    ax.text(7, 4.5, r"$R=3$ Ом после соединения", ha="right", color=GREY, fontsize=10)
    ax.set_xlabel("число кусков $n$")
    ax.set_ylabel(r"сопротивление целого провода $R_0=n^2R$, Ом")
    ax.set_title("Провод режут на $n$ частей и соединяют параллельно")
    ax.set_xticks(n)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    save(f, "connection-task-8-33-graph")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
