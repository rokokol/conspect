"""Figures for the notes "Электрический ток в газах" and "Электрический ток в полупроводниках" (section f13, lessons 192-194).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 current_media_2.py [name ...]
PNG files go to content/13. Электрический ток в средах/00. Вложения/ (prefixes gas-, semi-)
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "13. Электрический ток в средах"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ASH, BLUE, GREEN, INK, PAPER, PINK, RED, VIOLET, WARM, saver, tint

GRID = ASH
C1, C2, C3, C4 = RED, BLUE, GREEN, VIOLET  # the first curves of theme.SERIES
C5 = WARM  # a gold, glowing or yellow mark
GREY = tint(INK, 0.4)  # guides and small notes
POS_FILL = tint(RED, 0.85)
NEG_FILL = tint(BLUE, 0.85)
ION_FILL = tint(INK, 0.9)
SOFT = tint(INK, 0.94)  # the pale body fill of a part
PLATE = tint(INK, 0.87)  # a grey plate or a block

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


# ---------- primitives ----------


def canvas(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def neutral(ax, x, y, r=0.5):
    ax.add_patch(Circle((x, y), r, fc=PAPER, ec=INK, lw=1.8, zorder=3))


def posion(ax, x, y, r=0.5):
    ax.add_patch(Circle((x, y), r, fc=POS_FILL, ec=C1, lw=1.8, zorder=3))
    ax.text(x, y, "+", ha="center", va="center", color=C1, fontsize=max(int(28 * r), 10), fontweight="bold", zorder=4)


def negion(ax, x, y, r=0.5):
    ax.add_patch(Circle((x, y), r, fc=NEG_FILL, ec=C2, lw=1.8, zorder=3))
    ax.text(x, y, "−", ha="center", va="center", color=C2, fontsize=max(int(28 * r), 10), fontweight="bold", zorder=4)
    ax.add_patch(Circle((x - r * 0.95, y + r * 0.35), r * 0.28, fc=C2, ec=C2, zorder=5))


def electron(ax, x, y, r=0.14):
    ax.add_patch(Circle((x, y), r, fc=C2, ec=C2, zorder=5))


def arrow(ax, p, q, color=INK, lw=1.8, ms=14, ls="-", rad=0.0, z=6):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, ls=ls,
            connectionstyle=f"arc3,rad={rad}", zorder=z, shrinkA=0, shrinkB=0,
        )
    )


def text(ax, x, y, s, size=11, ha="center", va="center", color=INK, **kw):
    ax.text(x, y, s, fontsize=size, ha=ha, va=va, color=color, **kw)


def particle_legend(f, ncol=4, y=0.0):
    handles = [
        Line2D([], [], marker="o", ls="", mfc=PAPER, mec=INK, mew=1.6, ms=13, label="нейтральная молекула"),
        Line2D([], [], marker="o", ls="", mfc=POS_FILL, mec=C1, mew=1.6, ms=13, label="положительный ион"),
        Line2D([], [], marker="o", ls="", mfc=NEG_FILL, mec=C2, mew=1.6, ms=13, label="отрицательный ион"),
        Line2D([], [], marker="o", ls="", mfc=C2, mec=C2, ms=6, label="электрон"),
    ]
    f.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False, bbox_to_anchor=(0.5, y), fontsize=10)


def axes_arrows(ax, xl, yl, xmax, ymax):
    """Coordinate axes with arrowheads and no ticks."""
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    arrow(ax, (0, 0), (xmax, 0), color=INK, lw=1.6, ms=13, z=2)
    arrow(ax, (0, 0), (0, ymax), color=INK, lw=1.6, ms=13, z=2)
    ax.text(xmax, -0.03 * ymax, xl, ha="right", va="top", fontsize=13)
    ax.text(-0.02 * xmax, ymax, yl, ha="right", va="top", fontsize=13)


# ---------- gas: ionization ----------


@fig("gas-ionization-scheme")
def _():
    f, axs = plt.subplots(2, 2, figsize=(12, 6.2))
    panels = [
        "Образование положительного иона",
        "Образование отрицательного иона",
        "Рекомбинация: ион захватывает электрон",
        "Рекомбинация: два иона обмениваются электроном",
    ]
    for ax, title in zip(axs.flat, panels):
        ax.set_xlim(0, 12)
        ax.set_ylim(0.3, 3.9)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=12, fontweight="bold", pad=2)
        arrow(ax, (5.2, 2.0), (6.6, 2.0), color=GREY, lw=3, ms=22)
    y = 2.0
    # a: collision of two fast neutral molecules
    ax = axs[0, 0]
    neutral(ax, 1.0, y)
    arrow(ax, (1.7, y), (2.9, y), color=INK)
    neutral(ax, 4.0, y)
    neutral(ax, 7.7, y)
    posion(ax, 9.3, y)
    electron(ax, 10.9, 3.4)
    arrow(ax, (10.1, 2.7), (10.8, 3.3), color=C2, lw=1.4, ms=11)
    text(ax, 2.5, 0.7, "быстрые молекулы\n(высокая температура)", size=9.5, color=GREY)
    # b: electron sticks to a neutral molecule
    ax = axs[0, 1]
    electron(ax, 1.0, y)
    arrow(ax, (1.4, y), (2.9, y), color=C2)
    neutral(ax, 4.0, y)
    negion(ax, 8.8, y)
    text(ax, 2.5, 0.7, "электрон не отталкивается\nнейтральной молекулой", size=9.5, color=GREY)
    # c: ion + electron
    ax = axs[1, 0]
    electron(ax, 1.0, y)
    arrow(ax, (1.4, y), (2.9, y), color=C2)
    posion(ax, 4.0, y)
    neutral(ax, 8.8, y)
    # d: ion + ion
    ax = axs[1, 1]
    posion(ax, 1.4, y)
    negion(ax, 4.2, y)
    arrow(ax, (2.1, y), (2.9, y), color=INK, ms=11)
    neutral(ax, 7.7, y)
    neutral(ax, 9.3, y)
    particle_legend(f, y=-0.02)
    f.tight_layout(rect=(0, 0.05, 1, 1))
    save(f, "gas-ionization-scheme")


# ---------- gas: tube ----------


@fig("gas-tube-setup")
def _():
    f, ax = canvas(9.5, 5.6, (0, 12), (0, 7.2))
    ax.add_patch(FancyBboxPatch((2.2, 3.6), 7.6, 2.6, boxstyle="round,pad=0.25,rounding_size=1.1",
                                fc=SOFT, ec=INK, lw=2.2, zorder=1))
    # electrodes and wires
    ax.plot([3.2, 3.2], [3.9, 5.9], color=INK, lw=5, solid_capstyle="butt", zorder=3)
    ax.plot([8.8, 8.8], [3.9, 5.9], color=INK, lw=5, solid_capstyle="butt", zorder=3)
    ax.plot([2.0, 3.2], [4.9, 4.9], color=INK, lw=1.8, zorder=2)
    ax.plot([8.8, 10.0], [4.9, 4.9], color=INK, lw=1.8, zorder=2)
    ax.plot([1.0, 2.0], [4.9, 4.9], color=INK, lw=1.8)
    ax.plot([10.0, 11.0], [4.9, 4.9], color=INK, lw=1.8)
    ax.plot([1.0, 1.0, 3.0], [4.9, 1.2, 1.2], color=INK, lw=1.8)
    ax.plot([11.0, 11.0, 8.6], [4.9, 1.2, 1.2], color=INK, lw=1.8)
    # battery
    ax.plot([3.0, 3.6], [1.2, 1.2], color=INK, lw=1.8)
    ax.plot([3.6, 3.6], [0.7, 1.7], color=INK, lw=3)
    ax.plot([4.1, 4.1], [0.95, 1.45], color=INK, lw=3)
    ax.plot([4.1, 5.4], [1.2, 1.2], color=INK, lw=1.8)
    text(ax, 3.35, 1.9, "+", size=14, color=C1)
    text(ax, 4.45, 1.9, "−", size=14, color=C2)
    text(ax, 4.0, 0.25, "источник напряжения, $U$", size=10.5)
    # milliammeter
    ax.plot([5.4, 7.2], [1.2, 1.2], color=INK, lw=1.8)
    ax.add_patch(Circle((7.9, 1.2), 0.7, fc=PAPER, ec=INK, lw=1.8, zorder=3))
    text(ax, 7.9, 1.2, "мА", size=12)
    ax.plot([7.2, 7.2], [1.2, 1.2], color=INK)
    ax.plot([8.6, 8.6], [1.2, 1.2], color=INK)
    text(ax, 7.9, 0.25, "миллиамперметр", size=10.5)
    # ionizer under the tube
    ax.add_patch(Rectangle((5.3, 2.05), 1.4, 0.75, fc=tint(VIOLET, 0.85), ec=C4, lw=1.8, zorder=3))
    text(ax, 6.0, 2.42, "ионизатор", size=9.5, color=C4)
    for dx in (-0.45, 0.0, 0.45):
        arrow(ax, (6.0 + dx * 0.4, 2.9), (6.0 + dx * 1.6, 3.85), color=C4, lw=1.4, ms=11, ls="--")
    # pump stub and tap
    ax.plot([3.9, 3.9], [3.35, 2.7], color=INK, lw=2.2)
    ax.plot([3.9, 3.9], [2.7, 2.2], color=INK, lw=2.2)
    ax.add_patch(Polygon([[3.65, 2.65], [4.15, 2.65], [3.65, 2.25], [4.15, 2.25]], closed=True, fc=PAPER, ec=INK, lw=1.4, zorder=4))
    text(ax, 2.9, 2.45, "кран, насос", size=9.5, color=GREY, ha="right")
    # electrode labels
    text(ax, 3.2, 6.65, "анод, +", size=11.5, color=C1)
    text(ax, 8.8, 6.65, "катод, −", size=11.5, color=C2)
    # charged particles in the tube
    for (x, y) in [(4.6, 5.3), (4.9, 4.3)]:
        electron(ax, x, y)
        arrow(ax, (x - 0.2, y), (x - 0.75, y), color=C2, lw=1.3, ms=10)
    negion(ax, 5.3, 4.75, r=0.2)
    arrow(ax, (5.05, 4.75), (4.5, 4.75), color=C2, lw=1.3, ms=10)
    for (x, y) in [(7.1, 5.3), (7.5, 4.3), (7.0, 4.75)]:
        posion(ax, x, y, r=0.2)
        arrow(ax, (x + 0.25, y), (x + 0.8, y), color=C1, lw=1.3, ms=10)
    text(ax, 6.0, 5.75, "ток течёт от анода к катоду", size=9.5, color=GREY)
    f.tight_layout()
    save(f, "gas-tube-setup")


# ---------- gas: I(U) ----------


def _iv(U, In, tau, Uz):
    base = In * (1 - np.exp(-U / tau))
    extra = np.where(U > Uz, 0.04 * (np.exp(np.clip(U - Uz, 0, None) / 0.55) - 1), 0.0)
    return base + extra


@fig("gas-iv-curve")
def _():
    f, ax = plt.subplots(figsize=(8.6, 5.3))
    Uz, ymax = 6.2, 3.5
    axes_arrows(ax, "$U$", "$I$", 10.4, ymax + 0.8)
    U = np.linspace(0, 10, 900)
    I1 = _iv(U, 1.0, 1.3, Uz)
    I2 = _iv(U, 1.7, 1.9, Uz)
    m1, m2 = I1 <= ymax, I2 <= ymax
    ax.axvspan(0, Uz, color=C2, alpha=0.07, lw=0)
    ax.axvspan(Uz, 10.4, color=C1, alpha=0.07, lw=0)
    ax.plot(U[m1], I1[m1], color=INK, lw=2.8, label="ионизатор слабее")
    ax.plot(U[m2], I2[m2], color=C4, lw=2.4, ls="--", label="ионизатор мощнее")
    ax.axvline(Uz, color=GREY, lw=1.3, ls=":")
    ax.axhline(1.0, xmax=Uz / 10.4, color=GREY, lw=1.0, ls=":")
    ax.axhline(1.7, xmax=Uz / 10.4, color=C4, lw=1.0, ls=":")
    ax.text(-0.15, 1.0, "$I_н$", ha="right", va="center", fontsize=13)
    ax.text(-0.15, 1.7, "$I_н'$", ha="right", va="center", fontsize=13, color=C4)
    ax.text(Uz, -0.14, "$U_з$", ha="center", va="top", fontsize=13)
    ax.text(3.1, 4.05, "несамостоятельный разряд", ha="center", va="center", fontsize=12, color=C2, fontweight="bold")
    ax.text(3.1, 3.72, "нужен внешний ионизатор", ha="center", va="center", fontsize=10, color=C2)
    ax.text(8.3, 4.05, "самостоятельный разряд", ha="center", va="center", fontsize=12, color=C1, fontweight="bold")
    ax.text(8.3, 3.72, "ионизатор не нужен", ha="center", va="center", fontsize=10, color=C1)
    ax.annotate("растёт число ионов,\nдостигающих электродов", xy=(1.0, 0.55), xytext=(0.9, 1.9),
                fontsize=9.5, color=GREY, ha="left", arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    ax.annotate("ток насыщения:\nдошли все ионы", xy=(4.3, 1.0), xytext=(3.8, 0.28),
                fontsize=9.5, color=GREY, ha="left", arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    ax.annotate("электронно-ионная\nлавина", xy=(7.8, 1.7), xytext=(6.4, 0.75),
                fontsize=9.5, color=GREY, ha="left", arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    ax.legend(loc="lower right", frameon=False, fontsize=10, bbox_to_anchor=(1.0, 0.0))
    ax.set_title("Вольт-амперная характеристика газового разряда")
    f.tight_layout()
    save(f, "gas-iv-curve")


# ---------- gas: impact ionization avalanche ----------


@fig("gas-avalanche")
def _():
    f, ax = canvas(10.5, 5.6, (0, 12.4), (0.2, 7.6))
    ax.plot([0.6, 0.6], [0.8, 7.0], color=INK, lw=5, solid_capstyle="butt")
    ax.plot([11.8, 11.8], [0.8, 7.0], color=INK, lw=5, solid_capstyle="butt")
    text(ax, 0.6, 7.4, "катод, −", size=11.5, color=C2)
    text(ax, 11.8, 7.4, "анод, +", size=11.5, color=C1)
    r = 0.3
    ys = [4.0]
    cols = [2.5, 5.0, 7.5]
    nmol = [1, 2, 4]
    ymol = {1: [4.0], 2: [3.0, 5.0], 4: [1.9, 3.3, 4.7, 6.1]}
    e_prev = [(1.4, 4.0)]
    arrow(ax, (0.9, 4.0), (1.35, 4.0), color=C2, lw=1.4, ms=10)
    electron(ax, 1.5, 4.0, r=0.13)
    targets_prev = [(1.5, 4.0)]
    for k, xc in enumerate(cols):
        for ym in ymol[nmol[k]]:
            posion(ax, xc, ym, r=r)
    # electrons flying between columns
    def flights(src, dst):
        for (x0, y0), (x1, y1) in zip(src, dst):
            arrow(ax, (x0 + 0.15, y0), (x1 - 0.45, y1), color=C2, lw=1.2, ms=9)
    gen0 = [(1.5, 4.0)]
    gen1 = [(3.4, 3.7), (3.4, 4.3)]
    gen2 = [(5.9, 2.8), (5.9, 3.3), (5.9, 4.7), (5.9, 5.2)]
    gen3 = [(8.4, y) for y in (1.7, 2.15, 3.1, 3.55, 4.5, 4.95, 5.9, 6.35)]
    for g in (gen1, gen2, gen3):
        for (x, y) in g:
            electron(ax, x, y, r=0.13)
    flights(gen0, [(2.5, 4.0)])
    for (x, y), m in zip(gen1, [(5.0, 3.0), (5.0, 5.0)]):
        arrow(ax, (x + 0.15, y), (m[0] - 0.4, m[1]), color=C2, lw=1.2, ms=9)
    for (x, y), m in zip(gen2, [(7.5, 1.9), (7.5, 3.3), (7.5, 4.7), (7.5, 6.1)]):
        arrow(ax, (x + 0.15, y), (m[0] - 0.4, m[1]), color=C2, lw=1.2, ms=9)
    for (x, y) in gen3:
        arrow(ax, (x + 0.15, y), (x + 1.0, y), color=C2, lw=1.2, ms=9)
    # generation counters
    for x, s in [(1.5, "1"), (3.4, "2"), (5.9, "4"), (8.4, "8")]:
        text(ax, x, 0.75, s, size=15, color=C2, fontweight="bold")
    text(ax, 5.0, 0.2, "число электронов удваивается после каждого столкновения", size=10, color=GREY)
    f.tight_layout()
    save(f, "gas-avalanche")


# ---------- gas: Paschen-like ----------


@fig("gas-ignition-pressure")
def _():
    f, ax = plt.subplots(figsize=(8.4, 4.9))
    s = np.linspace(-3.2, 3.6, 600)
    y = 2.3 + 0.55 * (np.cosh(0.95 * (s + 0.4)) - 1) ** 0.85 * 0.5
    axes_arrows(ax, "$p$", "$U_з$", 7.4, 7.2)
    X = s + 3.4
    ax.plot(X, y, color=INK, lw=2.8)
    ax.axvspan(1.4, 2.4, color=C3, alpha=0.12, lw=0)
    ax.text(1.9, 6.3, "тлеющий\nразряд", ha="center", va="center", fontsize=11, color=C3, fontweight="bold")
    ax.text(1.9, 5.5, "$10^{-2}\\dots10^{-1}$ мм рт. ст.", ha="center", va="center", fontsize=9.5, color=C3)
    xa = 6.3
    ax.axvline(xa, color=C1, lw=1.4, ls=":")
    ax.text(xa - 0.1, 6.4, "$p_{атм}$: искровой,\nдуговой, коронный", ha="right", va="center", fontsize=10.5, color=C1)
    ax.annotate("слишком мало молекул:\nэлектрон долетает до электрода\nбез столкновений", xy=(0.4, 3.35), xytext=(0.3, 1.0),
                fontsize=9.5, color=GREY, ha="left", arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    ax.annotate("молекулы близко:\nэлектрон не набирает\nэнергию до столкновения", xy=(5.5, 3.5), xytext=(3.9, 1.0),
                fontsize=9.5, color=GREY, ha="left", arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    ax.set_title("Напряжение зажигания зависит от давления (качественно)")
    f.tight_layout()
    save(f, "gas-ignition-pressure")


# ---------- gas: spark ----------


@fig("gas-spark")
def _():
    f, ax = canvas(9.4, 4.4, (0, 12), (0.5, 6.0))
    for x, sgn in ((2.6, -1), (9.4, 1)):
        ax.add_patch(Circle((x, 3.7), 0.95, fc=PLATE, ec=INK, lw=2.2, zorder=3))
        ax.plot([x + sgn * 0.6, x + sgn * 1.6], [3.0, 1.4], color=INK, lw=4, solid_capstyle="round", zorder=2)
    text(ax, 2.6, 5.4, "кондуктор", size=11)
    text(ax, 9.4, 5.4, "кондуктор", size=11)
    xs = [3.5, 4.3, 5.1, 5.7, 6.5, 7.1, 8.5]
    ys = [3.8, 4.3, 3.4, 4.5, 3.2, 4.1, 3.7]
    ax.plot(xs, ys, color=WARM, lw=9, alpha=0.3, solid_joinstyle="round")
    ax.plot(xs, ys, color=WARM, lw=3.2, solid_joinstyle="miter", zorder=4)
    arrow(ax, (3.55, 2.35), (8.45, 2.35), color=GREY, lw=1.4, ms=11)
    arrow(ax, (8.45, 2.35), (3.55, 2.35), color=GREY, lw=1.4, ms=11)
    text(ax, 6.0, 1.9, "около $5$ см", size=11.5)
    text(ax, 6.0, 0.95, "$30$ кВ на $1$ см  $\\Rightarrow$  около $150$ кВ на промежутке", size=11.5, color=C1)
    f.tight_layout()
    save(f, "gas-spark")


# ---------- gas: arc ----------


@fig("gas-arc")
def _():
    f, ax = canvas(10.5, 5.4, (0, 12.4), (0.6, 7.6))
    ax.add_patch(Polygon([[0.6, 2.7], [4.0, 2.7], [4.75, 3.2], [4.0, 3.7], [0.6, 3.7]], closed=True, fc=tint(INK, 0.3), ec=INK, lw=1.8, zorder=3))
    ax.add_patch(Polygon([[11.8, 2.7], [8.2, 2.7], [7.9, 3.0], [8.75, 3.2], [7.9, 3.4], [8.2, 3.7], [11.8, 3.7]], closed=True, fc=tint(INK, 0.3), ec=INK, lw=1.8, zorder=3))
    verts = [(4.75, 3.2), (5.8, 5.9), (7.3, 5.9), (8.75, 3.25)]
    codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4]
    for lw, al, col in ((16, 0.18, WARM), (8, 0.45, WARM), (2.6, 1.0, tint(WARM, 0.85))):
        ax.add_patch(PathPatch(MPath(verts, codes), fc="none", ec=col, lw=lw, alpha=al, zorder=4, capstyle="round"))
    # heated tip glow
    ax.add_patch(Circle((4.75, 3.2), 0.45, fc=WARM, ec="none", alpha=0.6, zorder=4))
    text(ax, 2.5, 4.4, "катод, −", size=11.5, color=C2)
    text(ax, 10.0, 4.4, "анод, +", size=11.5, color=C1)
    text(ax, 2.5, 5.3, "раскалённый катод\nиспускает электроны", size=10, color=GREY)
    text(ax, 10.0, 5.3, "электроны раскаляют анод,\nуглерод испаряется", size=10, color=GREY)
    ax.annotate("кратер", xy=(8.5, 3.0), xytext=(9.4, 1.5), fontsize=11, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    electron(ax, 5.6, 4.35)
    arrow(ax, (5.75, 4.55), (6.6, 5.0), color=C2, lw=1.3, ms=10)
    posion(ax, 7.6, 4.85, r=0.22)
    arrow(ax, (7.35, 4.7), (6.6, 4.3), color=C1, lw=1.3, ms=10, rad=0.2)
    ax.annotate("горячий воздух поднимается,\nдуга изгибается вверх", xy=(6.5, 5.95), xytext=(6.5, 7.15),
                fontsize=10, ha="center", color=GREY, arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
    text(ax, 6.2, 0.95, "$U=40\\dots60$ В,  $I$ — десятки ампер", size=11.5)
    f.tight_layout()
    save(f, "gas-arc")


# ---------- gas: glow ----------


@fig("gas-glow")
def _():
    f, ax = canvas(10.8, 5.0, (-0.2, 12.8), (0.4, 6.8))
    ax.add_patch(FancyBboxPatch((1.9, 2.4), 8.6, 2.4, boxstyle="round,pad=0.2,rounding_size=1.0",
                                fc=SOFT, ec=INK, lw=2.2, zorder=1))
    ax.add_patch(Rectangle((2.5, 2.5), 0.55, 2.2, fc=PINK, ec="none", alpha=0.95, zorder=2))
    ax.add_patch(Rectangle((3.05, 2.5), 1.9, 2.2, fc=INK, ec="none", alpha=0.85, zorder=2))
    ax.add_patch(Rectangle((4.95, 2.5), 4.7, 2.2, fc=VIOLET, ec="none", alpha=0.6, zorder=2))
    ax.plot([2.4, 2.4], [2.6, 4.6], color=INK, lw=5, solid_capstyle="butt", zorder=3)
    ax.plot([9.9, 9.9], [2.6, 4.6], color=INK, lw=5, solid_capstyle="butt", zorder=3)
    ax.plot([0.4, 2.4], [3.6, 3.6], color=INK, lw=1.8)
    ax.plot([9.9, 11.9], [3.6, 3.6], color=INK, lw=1.8)
    text(ax, 0.75, 4.15, "катод, −", size=11.5, color=C2)
    text(ax, 11.6, 4.15, "анод, +", size=11.5, color=C1)
    text(ax, 3.95, 4.2, "ионы", size=9.5, color=PAPER)
    text(ax, 3.95, 3.0, "электроны", size=9.5, color=PAPER)
    ax.annotate("прикатодное\nсвечение", xy=(2.8, 2.5), xytext=(2.0, 1.1), fontsize=10.5, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.annotate("тёмное катодное\nпространство", xy=(4.0, 5.05), xytext=(4.0, 6.2), fontsize=10.5, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.annotate("анодный (положительный) столб", xy=(7.3, 2.4), xytext=(7.3, 1.1), fontsize=10.5, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    arrow(ax, (4.6, 3.85), (3.3, 3.85), color=RED, lw=1.3, ms=10)
    arrow(ax, (3.3, 3.35), (4.6, 3.35), color=BLUE, lw=1.3, ms=10)
    f.tight_layout()
    save(f, "gas-glow")


# ---------- gas: corona ----------


@fig("gas-corona")
def _():
    f, ax = canvas(10.4, 5.4, (-1.0, 12), (0.4, 7.0))
    ax.add_patch(Polygon([[1.6, 2.9], [1.6, 4.5], [7.2, 3.7]], closed=True, fc=PLATE, ec=INK, lw=2.2, zorder=3))
    ax.plot([-0.8, 1.6], [3.7, 3.7], color=INK, lw=2)
    text(ax, -0.7, 4.2, "к $+$ источника", size=10, color=GREY, ha="left")
    for x in (5.4, 5.8, 6.2):  # the signs stay on the body of the point, clear of its outline
        text(ax, x, 3.7, "+", size=13, color=C1, fontweight="bold", zorder=5)
    tip = np.array([7.2, 3.7])
    for r, al in ((0.9, 0.5), (1.45, 0.28), (2.0, 0.14)):
        th = np.linspace(-1.05, 1.05, 60)
        ax.plot(tip[0] + r * np.cos(th), tip[1] + r * np.sin(th), color=VIOLET, lw=7, alpha=al, solid_capstyle="round", zorder=2)
    for ang in np.linspace(-0.8, 0.8, 5):
        p0 = tip + 0.15 * np.array([np.cos(ang), np.sin(ang)])
        p1 = tip + 2.4 * np.array([np.cos(ang), np.sin(ang)])  # the rays end before the two notes on the right
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=GREY, lw=1.0, ls=":", zorder=1)
    text(ax, 9.6, 6.2, "сильное поле только\nвблизи острия", size=10.5, color=GREY)
    posion(ax, 9.1, 4.9, r=0.25)
    arrow(ax, (9.4, 5.0), (10.9, 5.5), color=C1, lw=1.4, ms=11)
    text(ax, 10.6, 4.55, "ионы уходят\n(ионный ветер)", size=9.5, color=C1)
    electron(ax, 9.3, 2.5)
    arrow(ax, (9.1, 2.6), (7.9, 3.35), color=C2, lw=1.4, ms=11)
    text(ax, 10.0, 1.5, "электроны летят\nк острию", size=9.5, color=C2)
    text(ax, 4.6, 1.6, "$p\\approx p_{атм}$", size=12)
    f.tight_layout()
    save(f, "gas-corona")


# ---------- semiconductors ----------


@fig("semi-resistivity-scale")
def _():
    f, ax = plt.subplots(figsize=(10.5, 3.9))
    ax.set_xlim(-13, 18)
    ax.set_ylim(-0.4, 3.9)
    for s in ("left", "top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ticks = list(range(-8, 17, 4))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"$10^{{{t}}}$" for t in ticks])
    ax.set_xlabel("удельное сопротивление $\\rho$, Ом$\\cdot$м")
    bands = [
        (-8, -6, 2.9, C2, "металлы"),
        (3, 7, 1.8, C3, "полупроводники"),
        (10, 16, 0.7, C5, "диэлектрики"),
    ]
    for a, b, y, c, name in bands:
        ax.add_patch(Rectangle((a, y), b - a, 0.5, fc=c, alpha=0.85, ec="none"))
        ax.text((a + b) / 2, y + 0.75, name, ha="center", va="center", color=c, fontsize=12.5, fontweight="bold")
    ax.text(-7.0, 2.5, "серебро, медь, алюминий $10^{-8}$;  нихром $10^{-6}$", ha="center", va="top", fontsize=9.5, color=GREY)
    ax.text(13.0, 0.4, "резина, бумага, дерево $10^{10}$;  янтарь $10^{16}$", ha="center", va="top", fontsize=9.5, color=GREY)
    ax.text(5.0, 1.45, "от $10^{3}$ до $10^{7}$", ha="center", va="top", fontsize=9.5, color=GREY)
    f.tight_layout()
    save(f, "semi-resistivity-scale")


@fig("semi-rho-t")
def _():
    f, ax = plt.subplots(figsize=(7.6, 4.9))
    axes_arrows(ax, "$t$", "$\\rho$", 10.0, 6.4)
    t = np.linspace(0.6, 8.6, 200)
    ax.plot(t, 1.0 + 0.32 * t, color=C2, lw=3)
    tt = np.linspace(0.8, 8.4, 200)
    ax.plot(tt, 0.4 + 5.2 * np.exp(-0.42 * (tt - 0.8)), color=C3, lw=3)
    ax.text(8.7, 3.95, "металлы", color=C2, fontsize=12.5, fontweight="bold", va="center")
    ax.text(3.0, 4.45, "полупроводники", color=C3, fontsize=12.5, fontweight="bold", ha="left", va="center")
    f.tight_layout()
    save(f, "semi-rho-t")


ION_R = 0.52


def si_ion(ax, x, y, label="Si", fc=ION_FILL, ec=INK, r=ION_R, size=11):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=1.8, zorder=3))
    ax.text(x, y, label, ha="center", va="center", fontsize=size, zorder=4)


def bond_pos(a, b, k):
    """Positions of the two electrons of a bond between ions a and b (k = 0 or 1)."""
    ax_, ay = a
    bx, by = b
    mx, my = (ax_ + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax_, by - ay
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    s = (-0.17, 0.17)[k]
    return mx + ux * s, my + uy * s


def draw_bond(ax, a, b, present=(True, True), color=INK, lw=1.0):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=GRID, lw=lw + 1.5, zorder=1)
    for k in (0, 1):
        if present[k]:
            x, y = bond_pos(a, b, k)
            ax.add_patch(Circle((x, y), 0.11, fc=C2, ec=PAPER, lw=0.8, zorder=5))


def hole_mark(ax, pos, r=0.24):
    ax.add_patch(Circle(pos, r, fc=PAPER, ec=C1, lw=1.6, ls="--", zorder=6))
    ax.text(pos[0], pos[1], "+", ha="center", va="center", color=C1, fontsize=12, fontweight="bold", zorder=7)


def grid_points(step, n=3):
    return {(i, j): (i * step, j * step) for i in range(n) for j in range(n)}


def grid_bonds(n=3):
    out = []
    for i in range(n):
        for j in range(n):
            if i + 1 < n:
                out.append(((i, j), (i + 1, j)))
            if j + 1 < n:
                out.append(((i, j), (i, j + 1)))
    return out


def plate(ax, x, y0, y1, sign, side):
    """Contact plate: side = -1 means the hatch goes to the left."""
    ax.plot([x, x], [y0, y1], color=INK, lw=3, zorder=2)
    for y in np.linspace(y0, y1, 9)[:-1]:
        ax.plot([x, x + side * 0.35], [y, y + 0.35], color=INK, lw=1.2, zorder=2)
    col = C1 if sign == "+" else C2
    ax.text(x + side * 0.9, (y0 + y1) / 2, sign if sign == "+" else "−", fontsize=17, color=col,
            ha="center", va="center", fontweight="bold")


@fig("semi-lattice-zero")
def _():
    step = 2.6
    P = grid_points(step)
    f, ax = canvas(8.2, 5.4, (-2.6, 7.8), (-1.2, 6.5))
    for a, b in grid_bonds():
        draw_bond(ax, P[a], P[b])
    for p in P.values():
        si_ion(ax, *p)
    plate(ax, -1.7, -0.6, 5.8, "+", -1)
    plate(ax, 6.9, -0.6, 5.8, "−", 1)
    text(ax, 2.6, -1.0, "$T=0$ К: все электроны связаны с ионами, тока нет", size=11, color=GREY)
    f.tight_layout()
    save(f, "semi-lattice-zero")


@fig("semi-lattice-holes")
def _():
    step = 2.6
    P = grid_points(step)
    f, ax = canvas(9.4, 5.9, (-2.6, 8.6), (-1.5, 6.9))
    broken = {((0, 2), (1, 2)): 0, ((2, 1), (2, 2)): 1, ((0, 0), (1, 0)): 1}
    for a, b in grid_bonds():
        if (a, b) in broken:
            k = broken[(a, b)]
            pres = [True, True]
            pres[k] = False
            draw_bond(ax, P[a], P[b], present=pres)
            hole_mark(ax, bond_pos(P[a], P[b], k))
        else:
            draw_bond(ax, P[a], P[b])
    for p in P.values():
        si_ion(ax, *p)
    for (x, y) in [(1.3, 3.9), (3.9, 3.9), (3.9, 1.3)]:
        ax.add_patch(Circle((x, y), 0.13, fc=C2, ec=PAPER, lw=0.8, zorder=6))
        arrow(ax, (x - 0.2, y), (x - 1.0, y), color=C2, lw=1.5, ms=11)
    for (x, y) in [(1.3, 5.2 + 0.0), (5.2, 3.9), (1.3, 0.0)]:
        pass
    plate(ax, -1.7, -0.6, 5.8, "+", -1)
    plate(ax, 6.9, -0.6, 5.8, "−", 1)
    ax.annotate("свободный электрон", xy=(3.95, 4.05), xytext=(4.9, 6.25), fontsize=10.5, ha="center", color=C2,
                arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.2, shrinkB=4))
    ax.annotate("дырка", xy=bond_pos(P[(2, 1)], P[(2, 2)], 1), xytext=(6.2, 3.4), fontsize=10.5, ha="center", color=C1,  # between the lattice and the plate, clear of the other note and of the hatching
                arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2, shrinkB=8))
    text(ax, 2.6, -1.1, "$T>0$: тепловое движение рвёт часть связей", size=11, color=GREY)
    f.tight_layout()
    save(f, "semi-lattice-holes")


@fig("semi-hole-motion")
def _():
    f, ax = canvas(9.6, 6.6, (-2.4, 12.2), (-0.6, 8.8))
    step = 2.4
    xs = [i * step for i in range(5)]
    rows = [(6.6, 1), (3.6, 2), (0.6, 3)]
    for y, hb in rows:
        for b in range(1, 5):
            a, c = (xs[b - 1], y), (xs[b], y)
            k = 0
            if b == hb:
                draw_bond(ax, a, c, present=(True, True))
            else:
                draw_bond(ax, a, c)
        for x in xs:
            si_ion(ax, x, y, r=0.44, size=10)
        # rebuild the bond with a hole: remove one electron by drawing it white over
        xm = (hb - 0.5) * step
        ax.add_patch(Circle((xm + 0.17, y), 0.13, fc=PAPER, ec="none", zorder=6))
        hole_mark(ax, (xm + 0.17, y), r=0.24)
    for (y, hb) in rows[:2]:
        xa = (hb + 0.5) * step - 0.17
        xb = (hb - 0.5) * step + 0.17
        arrow(ax, (xa, y + 0.25), (xb + 0.15, y + 0.35), color=C2, lw=1.6, ms=11, rad=0.55)
    for (y, hb) in rows[:2]:
        arrow(ax, ((hb - 0.5) * step + 0.35, y - 0.55), ((hb + 0.5) * step - 0.35, y - 0.55), color=C1, lw=1.6, ms=11, ls="--")
    for y in (6.6, 3.6, 0.6):
        plate(ax, -1.6, y - 0.9, y + 0.9, "+", -1)
        plate(ax, 10.9, y - 0.9, y + 0.9, "−", 1)
    text(ax, 4.8, 8.4, "электрон соседней связи перескакивает влево, дырка сдвигается вправо", size=10.5, color=GREY)
    f.tight_layout()
    save(f, "semi-hole-motion")


@fig("semi-donor-phosphorus")
def _():
    step = 2.6
    P = grid_points(step)
    f, ax = canvas(8.4, 6.0, (-1.2, 6.6), (-1.6, 6.9))
    for a, b in grid_bonds():
        draw_bond(ax, P[a], P[b])
    for k, p in P.items():
        if k == (1, 1):
            continue
        si_ion(ax, *p)
    si_ion(ax, *P[(1, 1)], label="P", fc=tint(WARM, 0.7), ec=C5, r=0.7, size=13)
    # fifth electron
    x, y = 3.55, 3.7
    ax.add_patch(Circle((x, y), 0.14, fc=C2, ec=PAPER, lw=0.8, zorder=6))
    arrow(ax, (x + 0.15, y + 0.15), (x + 0.9, y + 0.9), color=C2, lw=1.6, ms=11)
    ax.annotate("пятый электрон\nстановится свободным", xy=(x + 0.9, y + 0.9), xytext=(5.2, 5.9), fontsize=10.5,
                ha="center", color=C2)
    text(ax, 2.6, 6.55, "$V_{Si}=4$,  $V_{P}=5$", size=12.5)
    text(ax, 2.6, -0.95, "донорная примесь: $n>p$, электронный полупроводник ($n$-типа)", size=11, color=GREY)
    f.tight_layout()
    save(f, "semi-donor-phosphorus")


@fig("semi-acceptor-aluminium")
def _():
    step = 2.6
    P = grid_points(step)
    f, ax = canvas(8.4, 6.5, (-1.2, 6.6), (-2.4, 6.9))
    for a, b in grid_bonds():
        if (a, b) == ((2, 1), (2, 2)):
            draw_bond(ax, P[a], P[b], present=(True, False))
            hole_mark(ax, bond_pos(P[a], P[b], 1))
        else:
            draw_bond(ax, P[a], P[b])
    for k, p in P.items():
        if k == (1, 1):
            continue
        si_ion(ax, *p)
    si_ion(ax, *P[(1, 1)], label="Al", fc=tint(WARM, 0.7), ec=C5, r=0.7, size=13)
    ax.add_patch(Circle((4.07, 2.6), 0.2, fc="none", ec=C5, lw=2, zorder=6))
    arrow(ax, (4.95, 3.75), (4.3, 2.85), color=C2, lw=1.6, ms=11, rad=0.25)
    # the note stands under the lattice: a label with a white box over the bonds hid their electrons
    ax.text(2.6, -1.2, "электрон из соседней связи\nдостраивает связь алюминия", fontsize=10, ha="center", va="center", color=C2)
    ax.annotate("дырка", xy=bond_pos(P[(2, 1)], P[(2, 2)], 1), xytext=(6.2, 3.55), fontsize=10.5, ha="center", color=C1,
                arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2, shrinkB=8))
    text(ax, 2.6, 6.55, "$V_{Si}=4$,  $V_{Al}=3$", size=12.5)
    text(ax, 2.6, -1.95, "акцепторная примесь: $p>n$, дырочный полупроводник ($p$-типа)", size=11, color=GREY)
    f.tight_layout()
    save(f, "semi-acceptor-aluminium")


@fig("semi-carrier-types")
def _():
    f, ax = plt.subplots(figsize=(8.6, 4.6))
    groups = ["собственный", "с донорной примесью\n($n$-тип)", "с акцепторной примесью\n($p$-тип)"]
    ne = [1.0, 3.0, 0.4]
    ph = [1.0, 0.4, 3.0]
    x = np.arange(3)
    w = 0.32
    ax.bar(x - w / 2 - 0.02, ne, w, color=C2, label="свободные электроны, $n$")
    ax.bar(x + w / 2 + 0.02, ph, w, color=C1, label="свободные дырки, $p$")
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_ylim(0, 4.2)
    ax.text(0, 1.35, "$n_0=p_0$", ha="center", fontsize=12)
    ax.text(1, 3.4, "$n>p$", ha="center", fontsize=12)
    ax.text(2, 3.4, "$p>n$", ha="center", fontsize=12)
    ax.text(1, 3.85, "ток электронный", ha="center", fontsize=10, color=C2)
    ax.text(2, 3.85, "ток дырочный", ha="center", fontsize=10, color=C1)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.set_title("Концентрации носителей (схематично)")
    f.tight_layout()
    save(f, "semi-carrier-types")


@fig("semi-pn-junction")
def _():
    f, ax = canvas(9.6, 4.4, (0, 12), (0, 5.6))
    ax.add_patch(Rectangle((0.8, 1.4), 5.2, 2.4, fc=POS_FILL, ec=INK, lw=2))
    ax.add_patch(Rectangle((6.0, 1.4), 5.2, 2.4, fc=NEG_FILL, ec=INK, lw=2))
    ax.plot([6.0, 6.0], [1.2, 4.0], color=INK, lw=2.4, ls="--", zorder=5)
    for (x, y) in [(1.5, 3.2), (2.6, 2.1), (3.1, 3.3), (4.2, 2.4), (5.1, 3.1), (1.7, 1.9), (4.6, 1.8), (3.6, 2.8)]:
        hole_mark(ax, (x, y), r=0.2)
    for (x, y) in [(6.7, 3.2), (7.6, 2.0), (8.3, 3.1), (9.3, 2.3), (10.3, 3.2), (10.5, 1.9), (7.2, 2.7), (9.0, 1.8)]:
        ax.add_patch(Circle((x, y), 0.13, fc=C2, ec=PAPER, lw=0.8, zorder=6))
    text(ax, 3.4, 4.55, "$p$-область: акцепторная примесь,\nосновные носители дырки", size=10.5, color=C1)
    text(ax, 8.6, 4.55, "$n$-область: донорная примесь,\nосновные носители электроны", size=10.5, color=C2)
    text(ax, 6.0, 0.7, "$p$-$n$-переход", size=12)
    f.tight_layout()
    save(f, "semi-pn-junction")


@fig("semi-diode-iv")
def _():
    f, ax = plt.subplots(figsize=(8.2, 5.0))
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-4, 10)
    ax.set_ylim(-1.0, 6.4)
    for a, b in (((-4, 0), (10, 0)), ((0, -1.0), (0, 6.4))):
        arrow(ax, a, b, color=INK, lw=1.6, ms=13, z=2)
    ax.text(10, -0.25, "$U$", ha="right", va="top", fontsize=13)
    ax.text(-0.15, 6.4, "$I$", ha="right", va="top", fontsize=13)
    U = np.linspace(-4, 8.2, 500)
    I = np.where(U < 0, -0.12 * (1 - np.exp(U / 1.2)), 0.12 * (np.exp(np.clip(U - 2.0, -6, None) * 0.9) - 0.0))
    I = np.where(U >= 0, np.minimum(0.06 * (np.exp(1.05 * U) - 1), 9), I)
    m = I <= 6.0
    ax.plot(U[m], I[m], color=INK, lw=3)
    ax.text(6.2, 2.0, "прямое включение:\nток течёт хорошо", ha="left", va="center", fontsize=11, color=C3)
    ax.text(-3.7, 1.0, "обратное включение:\nтока почти нет", ha="left", va="center", fontsize=11, color=C1)
    # diode symbol
    x0, y0 = 1.0, 4.9
    ax.add_patch(Polygon([[x0, y0 - 0.5], [x0, y0 + 0.5], [x0 + 0.85, y0]], closed=True, fc=PAPER, ec=INK, lw=2))
    ax.plot([x0 + 0.85, x0 + 0.85], [y0 - 0.5, y0 + 0.5], color=INK, lw=2.4)
    ax.plot([x0 - 0.5, x0], [y0, y0], color=INK, lw=2)
    ax.plot([x0 + 0.85, x0 + 1.35], [y0, y0], color=INK, lw=2)
    arrow(ax, (x0 - 0.5, y0 + 0.85), (x0 + 1.35, y0 + 0.85), color=C3, lw=1.6, ms=11)
    ax.text(x0 - 0.5, y0 - 0.6, "анод", ha="center", va="top", fontsize=9.5, color=GREY)
    ax.text(x0 + 1.35, y0 - 0.6, "катод", ha="center", va="top", fontsize=9.5, color=GREY)
    f.tight_layout()
    save(f, "semi-diode-iv")


@fig("semi-rectifier")
def _():
    f, (a1, a2) = plt.subplots(2, 1, figsize=(8.0, 4.8), sharex=True, sharey=True)  # one scale: the current does not grow
    t = np.linspace(0, 3, 600)
    s = np.sin(2 * np.pi * t)
    a1.plot(t, s, color=C2, lw=2.4)
    a2.plot(t, np.clip(s, 0, None), color=C3, lw=2.4)
    for a, ttl in ((a1, "переменный ток на входе"), (a2, "ток за диодом идёт в одну сторону")):
        a.axhline(0, color=INK, lw=1.2)
        a.set_yticks([])
        a.set_xticks([])
        a.spines["left"].set_visible(False)
        a.spines["bottom"].set_visible(False)
        a.set_title(ttl, fontsize=11.5)
        a.set_ylabel("$I$", rotation=0, labelpad=10)
    a2.set_xlabel("$t$")
    f.tight_layout()
    save(f, "semi-rectifier")


if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
        print("ok", n)
