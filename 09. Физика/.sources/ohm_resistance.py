"""Graphs for the notes "Закон Ома для участка цепи" and "Сопротивление проводника" (section f11, lessons 151-156).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 ohm_resistance.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes ohm-, resistance-, rheostat-)
The circuit schemes are in ohm_circuits.py
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def axes(w, h, xlabel, ylabel, xlim, ylim, title):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    keep_dots(ax.set_title(title))
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return f, ax


@fig("ohm-iv-experiment")
def _():
    f, ax = axes(6.4, 4.6, "$U$, В", "$I$, А", (0, 5.4), (0, 2.8), "Опыт: три проводника")
    U = np.array([0, 1, 2, 3, 4, 5])
    data = [
        ("№ 1", 2, [0, 0.5, 1, 1.5, 2], C1),
        ("№ 2", 5, [0, 0.2, 0.4, 0.6, 0.8, 1.0], C2),
        ("№ 3", 10, [0, 0.1, 0.2, 0.3, 0.4, 0.5], C3),
    ]
    for name, R, I, c in data:
        x = np.linspace(0, 5, 2)
        ax.plot(x, x / R, color=c, lw=1.6, zorder=2)
        ax.plot(U[: len(I)], I, "o", color=c, ms=7, zorder=3)
        ax.text(5.25, 5 / R, f"{name}: $R={R}$ Ом", color=c, va="center", fontsize=10)
    ax.plot([4, 5], [2, 2.5], ls="--", color=C1, lw=1.2)
    ax.plot([5], [2.5], "o", mfc=PAPER, mec=C1, ms=7, zorder=3)
    ax.set_xlim(0, 7.4)
    ax.set_xticks(range(6))
    save(f, "ohm-iv-experiment")


@fig("ohm-ratio-constant")
def _():
    f, ax = axes(6.4, 4.2, "$I$, А", "$U/I$, В/А", (0, 2.4), (0, 12), "Отношение $U/I$ от тока не зависит")
    data = [(2, [0.5, 1, 1.5, 2], C1), (5, [0.2, 0.4, 0.6, 0.8, 1.0], C2), (10, [0.1, 0.2, 0.3, 0.4, 0.5], C3)]
    for R, I, c in data:
        ax.plot(I, [R] * len(I), "o-", color=c, ms=7, lw=1.4)
        ax.text(2.42, R, f"{R} В/А", color=c, va="center", fontsize=10)
    ax.set_xlim(0, 2.9)
    save(f, "ohm-ratio-constant")


@fig("ohm-current-vs-resistance")
def _():
    f, ax = axes(6.4, 4.4, "$R$, Ом", "$I$, А", (0, 12), (0, 4.4), "Ток при $U=4$ В")
    R = np.linspace(1, 12, 200)
    ax.plot(R, 4 / R, color=INK, lw=1.6)
    for r, c in [(2, C1), (5, C2), (10, C3)]:
        ax.plot([r], [4 / r], "o", color=c, ms=8, zorder=3)
        lab = f"{num(r, '')} Ом: {num(4 / r, None)} А"
        ax.annotate(lab, (r, 4 / r), xytext=(r + 0.5, 4 / r + 0.3), color=c, fontsize=10)
    save(f, "ohm-current-vs-resistance")


@fig("ohm-iv-family")
def _():
    f, ax = axes(6.6, 4.8, "$U$, В", "$I$, А", (0, 10), (0, 10.5), "Наклон прямой равен $1/R$")
    cols = [C1, C5, C3, C2, C4]
    for R, c in zip([1, 2, 5, 10, 20], cols):
        U = np.array([0, 10.0])
        ax.plot(U, U / R, color=c, lw=1.7)
        ax.text(10.2, 10 / R, f"$R={R}$ Ом", color=c, ha="left", va="center", fontsize=10)
    ax.text(0.4, 9.4, "больше $R$ — положе прямая", color=GREY, fontsize=10)
    ax.set_xlim(0, 12.6)
    ax.set_xticks(range(0, 11, 2))
    save(f, "ohm-iv-family")


@fig("ohm-task-10-18")
def _():
    f, ax = axes(6.4, 4.4, "$U$, В", "$I$, А", (0, 36), (0, 1.8), "Задача 10.18")
    for n, Iv, c in [(1, 1.5, C1), (2, 1.0, C2), (3, 0.5, C3)]:
        x = np.array([0, 33])
        ax.plot(x, x * Iv / 30, color=c, lw=1.7)
        ax.text(33.5, 33 * Iv / 30, f"{n}", color=c, va="center", fontsize=11, fontweight="bold")
        ax.plot([0, 30], [Iv, Iv], ls=":", color=c, lw=1)
        ax.plot([30], [Iv], "o", color=c, ms=6)
    ax.axvline(30, ls="--", color=GREY, lw=1)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_yticks([0, 0.5, 1.0, 1.5])
    save(f, "ohm-task-10-18")


@fig("ohm-task-10-32")
def _():
    f, ax = axes(6.4, 4.6, "$U$, В", "$I$, А", (0, 60), (0, 11), "Задача 10.32")
    ax.plot([0, 50], [0, 10], color=C1, lw=1.7)
    ax.plot([0, 50], [0, 50 / 15], color=C2, lw=1.7)
    ax.plot([50], [10], "o", color=C1)
    ax.plot([30], [2], "o", color=C2)
    ax.plot([50, 50], [0, 10], ls="--", color=GREY, lw=1)
    ax.plot([0, 50], [10, 10], ls="--", color=GREY, lw=1)
    ax.plot([30, 30], [0, 2], ls="--", color=GREY, lw=1)
    ax.plot([0, 30], [2, 2], ls="--", color=GREY, lw=1)
    ax.text(31, 8, "$R_1=5$ Ом", color=C1, ha="right", rotation=0, fontsize=11)
    ax.text(52, 3.4, "$R_2=15$ Ом", color=C2, fontsize=11)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    save(f, "ohm-task-10-32")


@fig("resistance-r-vs-l")
def _():
    f, ax = axes(6.6, 4.6, "$l$, м", "$R$, Ом", (0, 100), (0, 7), "Медный провод: $R(l)$")
    l = np.array([0, 100.0])
    for S, c in [(0.5, C1), (1, C5), (2, C2)]:
        ax.plot(l, 0.017 * l / S, color=c, lw=1.7)
        # in mathtext the decimal comma is written as {,}, otherwise a space follows it
        ax.text(101, 0.017 * 100 / S, f"$S={num(S, '', math=True)}$ мм$^2$", color=c, va="center", fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 4)
    ax.text(50, 3.7,"больше $l$ — больше $R$, прямая пропорциональность", color=GREY, ha="center", fontsize=9.5)
    f.subplots_adjust(right=0.78)
    save(f, "resistance-r-vs-l")


@fig("resistance-r-vs-s")
def _():
    f, ax = axes(6.6, 4.6, "$S$, мм$^2$", "$R$, Ом", (0, 4), (0, 6), "Медный провод: $R(S)$")
    S = np.linspace(0.1, 4, 300)
    for l, c, ty in [(10, C2, 0.7), (20, C1, 1.4)]:
        ax.plot(S, 0.017 * l / S, color=c, lw=1.7)
        ax.annotate(f"$l={l}$ м", (1.2, 0.017 * l / 1.2), xytext=(2.0, ty), color=c, fontsize=10, arrowprops=dict(arrowstyle="-", color=c))
    ax.set_ylim(0, 4)
    ax.text(2.2, 3.5, "больше $S$ — меньше $R$, обратная пропорциональность", color=GREY, ha="center", fontsize=9.5)
    save(f, "resistance-r-vs-s")


@fig("resistance-resistivity-bars")
def _():
    items = [
        ("серебро", 0.016, "m"), ("медь", 0.017, "m"), ("золото", 0.024, "m"), ("алюминий", 0.028, "m"),
        ("вольфрам", 0.055, "m"), ("железо", 0.10, "m"), ("свинец", 0.21, "m"), ("ртуть", 0.96, "m"),
        ("никелин", 0.40, "a"), ("манганин", 0.43, "a"), ("константан", 0.50, "a"),
        ("нихром", 1.1, "a"), ("фехраль", 1.3, "a"),
        ("графит", 13, "c"), ("фарфор", 1e19, "d"), ("эбонит", 1e20, "d"),
    ]
    items.sort(key=lambda t: t[1])
    col = {"m": C5, "a": C2, "c": GREY, "d": C1}
    f, ax = plt.subplots(figsize=(7.4, 6.0))
    y = np.arange(len(items))
    base = 1e-2
    ax.barh(y, [v - base for _, v, _ in items], left=base, color=[col[k] for _, _, k in items], height=0.7)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels([n for n, _, _ in items])
    ax.invert_yaxis()
    ax.set_xlim(1e-2, 1e24)
    ax.set_xlabel(r"$\rho$, Ом$\cdot$мм$^2$/м (при 20 °C), логарифмическая шкала")
    ax.set_title("Удельное сопротивление веществ")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for i, (_, v, _) in enumerate(items):
        lab = num(v, None) if v < 1e3 else f"$10^{{{int(round(np.log10(v)))}}}$"
        ax.text(v * 2.2, i, lab, va="center", fontsize=9.5)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[Patch(color=C5, label="чистые металлы"), Patch(color=C2, label="сплавы"), Patch(color=GREY, label="графит"), Patch(color=C1, label="диэлектрики")],
        loc="upper right", frameon=False, fontsize=10,
    )
    save(f, "resistance-resistivity-bars")


@fig("resistance-task-wire-diameter")
def _():
    f, ax = axes(6.6, 4.6, "$d$, мм", "$R$, Ом", (0.2, 1.0), (0, 6), "Медь, 10 м: $R(d)$")
    d = np.linspace(0.2, 1.0, 300)
    R = 4 * 0.017 * 10 / (np.pi * d**2)
    ax.plot(d, R, color=INK, lw=1.7)
    ax.axhline(1, ls="--", color=C1, lw=1.2)
    ax.axvline(0.465, ls="--", color=GREY, lw=1)
    ax.fill_between(d, 0, 1, where=d >= 0.465, color=C3, alpha=0.18)
    ax.plot([0.465], [1], "o", color=C1, zorder=3)
    ax.text(0.5, 1.25, "$R\\leqslant1$ Ом: $d\\geqslant0{,}47$ мм", color=C3, fontsize=10.5)
    ax.text(0.22, 1.12, "предел $R=1$ Ом", color=C1, fontsize=10)
    save(f, "resistance-task-wire-diameter")


@fig("resistance-task-1045-intersection")
def _():
    f, ax = axes(6.6, 4.6, "$l$, м", "$S$, мм$^2$", (0, 200), (0, 4), "Задача 10.45")
    l = np.linspace(28.5, 200, 300)
    ax.plot([0, 200], [0, 0.017 * 200], color=C2, lw=1.7)
    ax.plot(l, 1e6 / (8900 * l), color=C1, lw=1.7)
    L0 = np.sqrt(1 / (0.017e-6 * 8900))
    S0 = 0.017 * L0
    ax.plot([L0], [S0], "o", color=INK, zorder=3)
    ax.plot([L0, L0], [0, S0], ls="--", color=GREY, lw=1)
    ax.plot([0, L0], [S0, S0], ls="--", color=GREY, lw=1)
    # the caption lies below both curves, and the decimal comma is {,} so that mathtext does not add a space
    ax.annotate(f"$l\\approx{num(L0, '.0f', math=True)}$ м,  $S\\approx{num(S0, 1, math=True)}$ мм$^2$", (L0, S0), xytext=(100, 0.25), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.text(125, 1.5, "$R=1$ Ом", color=C2, rotation=0, fontsize=10.5)
    ax.text(36, 3.7, "$m=1$ кг", color=C1, fontsize=10.5)
    save(f, "resistance-task-1045-intersection")


@fig("resistance-task-al-vs-cu")
def _():
    f, ax = plt.subplots(figsize=(5.6, 4.2))
    rho_r = {"медь": 0.017e-6, "алюминий": 0.028e-6}
    rho_m = {"медь": 8900, "алюминий": 2700}
    l, R = 100, 1.0
    m = {k: rho_m[k] * rho_r[k] * l**2 / R for k in rho_r}
    bars = ax.bar(list(m), list(m.values()), color=[C5, GREY], width=0.55)
    for b, k in zip(bars, m):
        S = rho_r[k] * l / R * 1e6
        lab = num(m[k], 2) + " кг" + "\n$S=" + num(S, 1, math=True) + "$ мм$^2$"
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03, lab, ha="center", fontsize=10)
    ax.set_ylim(0, 2.1)
    ax.set_ylabel("масса провода, кг")
    ax.set_title("$l=100$ м, $R=1$ Ом")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.text(0.5, 0.93, f"медный тяжелее в {m['медь'] / m['алюминий']:.0f} раза", ha="center", transform=ax.transAxes, fontsize=10.5, color=GREY)
    save(f, "resistance-task-al-vs-cu")


@fig("rheostat-current-position")
def _():
    f, ax = axes(6.6, 4.6, "положение ползунка $x$", "$I/I_{\\max}$", (0, 1), (0, 1.1), "Ток в цепи с реостатом")
    x = np.linspace(0, 1, 200)
    for k, c in [(3, C2), (10, C1)]:
        ax.plot(x, 1 / (1 + k * x), color=c, lw=1.7)
        ax.text(0.98, 1 / (1 + k) + 0.05, f"$R_{{\\max}}={k}R_\\text{{л}}$", color=c, ha="right", fontsize=10)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["0\nвключено мало провода", "1\nвключён весь провод"])
    save(f, "rheostat-current-position")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
