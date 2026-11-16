"""Figures for the notes of section f01 (course Физика 7-9, lessons 1-4, 7, 8).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 intro_measurements.py [name ...]
PNG files go to content/01. Введение и измерения/00. Вложения/
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle, Ellipse, Circle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "01. Введение и измерения"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH  # grid and dashed guides
NOTE = tint(INK, 0.4)  # small notes and secondary text
GREY = NOTE  # small notes; guides and outlines name MUTED
SCALE = tint(WARM, 0.85)  # the body of a ruler, thermometer or other scale
GLASS = tint(SKY, 0.8)
SHOT = tint(INK, 0.3)  # a lead shot, a dark metal part
FEATHER = tint(WARM, 0.4)
RIGHT_FILL = tint(GREEN, 0.8)  # a correct digit
DOUBT_FILL = tint(RED, 0.8)  # a doubtful digit


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, style="->", color=INK, lw=1.4, ms=12, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, lw=lw, color=color, **kw))


# ---------------------------------------------------------------- lesson 2


def muller_lyer():
    fig, ax = blank(6.4, 3.2, (-1, 11), (-1.6, 3.4))
    L = 10
    fin = 0.9
    for y, out in ((2.4, True), (0.4, False)):
        ax.plot([0, L], [y, y], color=INK, lw=2.4)
        for x, sgn in ((0, 1), (L, -1)):
            dx = sgn * fin if out else -sgn * fin
            for s in (1, -1):
                ax.plot([x, x + dx], [y, y + s * 0.6], color=INK, lw=2.4)
    ax.text(L / 2, 3.15, "отрезок A", ha="center", fontsize=11, color=GREY)
    ax.text(L / 2, 1.1, "отрезок B", ha="center", fontsize=11, color=GREY)
    for x in (0, L):
        ax.plot([x, x], [-0.8, 3.0], color=GRID, lw=1, ls="--", zorder=0)
    arrow(ax, (0, -1.1), (L, -1.1), "<->", color=RED)
    ax.text(L / 2, -1.5, "оба отрезка по 40 см", ha="center", color=RED, fontsize=11)
    save(fig, "muller-lyer-illusion.png")


def knowledge_helix():
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    t = np.linspace(0.3, 4.05 * np.pi, 900)
    x = 2.2 * np.cos(t)
    y = 0.85 * t + 0.5 * np.sin(t)
    front = np.sin(t) < 0
    for seg, ls, a in ((True, "-", 1.0), (False, "--", 0.4)):
        ax.plot(np.where(front == seg, x, np.nan), np.where(front == seg, y, np.nan), ls=ls, color=BLUE, lw=2.2,
                alpha=a)
    stops = [(0.3, "незнание"), (1.5 * np.pi, "наблюдение"), (2.0 * np.pi, "гипотеза"), (2.5 * np.pi, "эксперимент"),
             (3.0 * np.pi, "гипотеза"), (3.5 * np.pi, "эксперимент"), (4.0 * np.pi, "закон")]
    for i, (tt, lab) in enumerate(stops, 1):
        px, py = 2.2 * np.cos(tt), 0.85 * tt + 0.5 * np.sin(tt)
        col = RED if i == len(stops) else INK
        ax.plot(px, py, "o", color=PAPER, ms=17, mec=col, mew=1.8, zorder=5)
        ax.text(px, py, str(i), ha="center", va="center", fontsize=10.5, color=col, weight="bold", zorder=6)
        ax.text(3.7, 12.4 - i * 1.05, "%d  %s" % (i, lab), fontsize=12.5, color=col, va="center",
                weight="bold" if i == len(stops) else None)
    # the next turn above the law is the theory: the arrow goes up from point 7
    ax.annotate("", (2.2, 12.85), (2.2, 11.15), arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.8))
    ax.text(2.2, 13.2, "теория", fontsize=13, color=GREEN, weight="bold", ha="center", va="bottom")
    ax.annotate("", (-3.3, 13.8), (-3.3, -0.2), arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))
    ax.text(-3.55, 6.8, "знание", rotation=90, va="center", ha="right", fontsize=12.5)
    ax.set_xlim(-4.2, 7.6)
    ax.set_ylim(-1.2, 14.2)
    ax.axis("off")
    save(fig, "knowledge-helix.png")


def newton_tube():
    fig, ax = blank(7.4, 4.6, (-0.5, 9.1), (-0.8, 6.4))
    tubes = [(1.4, "воздух есть"), (6.4, "воздух откачан")]
    for cx, lab in tubes:
        ax.add_patch(Rectangle((cx - 0.65, 0), 1.3, 5.4, fc=tint(SKY, 0.9), ec=INK, lw=2))
        ax.text(cx, 5.75, lab, ha="center", fontsize=12)
    # air: shot at bottom, feather midway
    cx = 1.4
    ax.plot(cx + 0.28, 0.32, "o", color=SHOT, ms=9, zorder=4)
    ax.add_patch(Ellipse((cx - 0.28, 2.6), 0.22, 0.75, angle=25, fc=FEATHER, ec=INK, zorder=4))
    for xx, yy, m in ((cx + 0.28, 5.0, "o"), (cx - 0.28, 5.0, "e")):
        if m == "o":
            ax.plot(xx, yy, "o", color=SHOT, ms=9, alpha=0.3)
        else:
            ax.add_patch(Ellipse((xx, yy), 0.22, 0.75, angle=25, fc=FEATHER, ec=INK, alpha=0.3))
    arrow(ax, (cx + 0.28, 4.6), (cx + 0.28, 0.9), color=MUTED, style="->")
    arrow(ax, (cx - 0.28, 4.6), (cx - 0.28, 3.15), color=MUTED, style="->")
    ax.text(cx + 1.05, 2.4, "дробинка\nупала на дно,\nперо ещё\nв полёте", fontsize=9.5, va="center")
    # vacuum
    cx = 6.4
    ax.plot(cx + 0.28, 0.32, "o", color=SHOT, ms=9, zorder=4)
    ax.add_patch(Ellipse((cx - 0.28, 0.4), 0.75, 0.22, angle=15, fc=FEATHER, ec=INK, zorder=4))
    ax.plot(cx + 0.28, 5.0, "o", color=SHOT, ms=9, alpha=0.3)
    ax.add_patch(Ellipse((cx - 0.28, 5.0), 0.22, 0.75, angle=25, fc=FEATHER, ec=INK, alpha=0.3))
    arrow(ax, (cx + 0.28, 4.6), (cx + 0.28, 0.9), color=MUTED)
    arrow(ax, (cx - 0.28, 4.6), (cx - 0.28, 0.9), color=MUTED)
    ax.text(cx + 1.05, 2.4, "оба тела\nдостигли дна\nодновременно", fontsize=9.5, va="center")
    ax.text(4.0, -0.55, "серые фигуры — начальное положение, цветные — момент, когда дробинка у дна", ha="center",
            fontsize=8.5, color=GREY)
    save(fig, "free-fall-newton-tube.png")


def fall_speed_graph():
    g = 9.81
    t = np.linspace(0, 1.5, 300)
    fig, ax = plt.subplots(figsize=(6.6, 4))
    ax.plot(t, g * t, color=GREEN, lw=3.5, alpha=0.5, label="вакуум: перо и дробинка")
    for vt, col, lab, ls in ((60, INK, "воздух: дробинка", "-"), (1.4, RED, "воздух: перо", "-")):
        v = vt * np.tanh(g * t / vt)
        ax.plot(t, v, color=col, lw=2, ls=ls, label=lab)
    ax.set_xlabel("время падения, с")
    ax.set_ylabel("скорость, м/с")
    ax.set_ylim(0, 15)
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Скорость падения (качественно)")
    save(fig, "free-fall-speed-graph.png")


def mica_boat():
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.9))
    x = np.linspace(-4, 4, 300)
    stages = [
        (0.0, 0.35, "1. бугорок под лодочкой:\nона скатывается вправо"),
        (2.0, 2.0, "2. справа вырос новый бугорок:\nлодочка скатывается влево"),
        (-1.7, -1.7, "3. по инерции проскочила середину,\nслева новый бугорок"),
    ]
    for ax, (xb, xboat, title) in zip(axs, stages):
        ax.set_xlim(-4, 4)
        ax.set_ylim(-1.2, 1.9)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((-4, -1.0), 8, 0.55, fc=tint(INK, 0.75), ec=INK))
        ax.text(3.9, -0.72, "алюминий", ha="right", va="center", fontsize=8.5)
        y = 0.55 * np.exp(-((x - xb) ** 2) / 1.2)
        ax.fill_between(x, -0.45 + y, -0.45 + y + 0.18, color=tint(WARM, 0.75), ec=INK)
        ax.plot(x, -0.27 + y, color=INK, lw=1)
        yb = -0.27 + 0.55 * np.exp(-((xboat - xb) ** 2) / 1.2)
        # rocker: a half-cylinder with a round bottom that touches the mica at one point
        th = np.linspace(np.pi, 2 * np.pi, 40)
        r = 0.55
        ax.add_patch(Polygon(np.column_stack([xboat + r * np.cos(th), yb + 0.05 + r + r * np.sin(th)]),
                             fc=SHOT, ec=INK, zorder=5))
        yb += 0.15
        ax.add_patch(Polygon([(xboat - 0.12, yb + 0.45), (xboat + 0.12, yb + 0.45), (xboat, yb + 0.85)],
                             fc=WARM, ec=RED, zorder=4))
        ax.set_title(title, fontsize=9.5)
    arrow(axs[0], (0.35, 1.45), (1.3, 1.35), color=RED)
    arrow(axs[1], (2.0, 1.45), (1.0, 1.35), color=RED)
    arrow(axs[2], (-1.7, 1.45), (-0.7, 1.35), color=RED)
    save(fig, "mica-boat-oscillation.png")


def theory_applicability():
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-15, 1e10)
    ax.set_ylim(1e-9, 1)
    ax.add_patch(Rectangle((1e-9, 1e-9), 1e10, 0.1 - 1e-9, fc=tint(SKY, 0.8), ec="none"))
    ax.add_patch(Rectangle((1e-9, 0.1), 1e10, 0.9, fc=tint(WARM, 0.7), ec="none"))
    ax.add_patch(Rectangle((1e-15, 1e-9), 1e-9 - 1e-15, 0.1, fc=tint(GREEN, 0.8), ec="none"))
    ax.add_patch(Rectangle((1e-15, 0.1), 1e-9 - 1e-15, 0.9, fc=tint(VIOLET, 0.8), ec="none"))
    ax.text(1e-1, 1e-4, "классическая\nмеханика", ha="center", va="center", fontsize=13, weight="bold")
    ax.text(1e0, 0.3, "теория относительности\n(классика — при $v \\ll c$)", ha="center", va="center", fontsize=10.5)
    ax.text(1e-12, 1e-5, "квантовая\nмеханика", ha="center", va="center", fontsize=10)
    ax.text(1e-12, 0.3, "релятив.\nквантовая\nтеория", ha="center", va="center", fontsize=9)
    ax.text(1e-12, 1e-8 * 3, "классика — при\nбольших размерах", ha="center", va="bottom", fontsize=8, color=GREY)
    ax.axvline(1e-9, color=INK, ls="--", lw=1)
    ax.axhline(0.1, color=INK, ls="--", lw=1)
    ax.set_xlabel("размер системы, м")
    ax.set_ylabel("скорость, доля скорости света $v/c$")
    ax.set_title("Границы применимости теорий (схема)")
    ax.set_xticks([1e-15, 1e-9, 1e-3, 1e3, 1e9])
    save(fig, "theory-applicability.png")


# ---------------------------------------------------------------- lesson 3


def prefix_ladder():
    rows = [
        ("гига", "Г", 9, "Земля — Солнце ≈ 150 Гм"),
        ("мега", "М", 6, "Земля — Луна ≈ 384 Мм"),
        ("кило", "к", 3, "расстояние между городами"),
        ("гекто", "г", 2, ""),
        ("дека", "да", 1, ""),
        ("", "", 0, "метр — основная единица"),
        ("деци", "д", -1, ""),
        ("санти", "с", -2, "лист бумаги"),
        ("милли", "м", -3, "толщина монеты"),
        ("микро", "мк", -6, ""),
        ("нано", "н", -9, "атом ≈ 0,1 нм"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    n = len(rows)
    for i, (name, sym, p, ex) in enumerate(rows):
        y = n - 1 - i
        base = p == 0
        col = tint(WARM, 0.7) if base else (LIGHT if p > 0 else tint(GREEN, 0.85))
        ax.add_patch(Rectangle((0, y - 0.42), 5.6, 0.84, fc=col, ec=MUTED))
        if base:
            ax.text(0.2, y, "м", va="center", fontsize=13, weight="bold")
            ax.text(1.9, y, "$10^{0}=1$", va="center", fontsize=12.5)
        else:
            ax.text(0.2, y, name, va="center", fontsize=12.5)
            ax.text(1.5, y, sym + "м", va="center", fontsize=12.5, weight="bold", color=BLUE)
            ax.text(3.1, y, "$10^{%d}$" % p, va="center", fontsize=12.5)
        ax.text(5.9, y, ex, va="center", fontsize=10, color=INK)
    kilo_y, m_y, milli_y = n - 1 - 2, n - 1 - 5, n - 1 - 8
    for a, b, lab in ((kilo_y, m_y, "×1000"), (m_y, milli_y, "×1000")):
        arrow(ax, (-0.55, a), (-0.55, b), color=RED, lw=1.6)
        ax.text(-0.75, (a + b) / 2, lab, rotation=90, ha="right", va="center", color=RED, fontsize=10.5)
    ax.set_xlim(-1.6, 10.5)
    ax.set_ylim(-0.7, n - 0.4)
    ax.axis("off")
    ax.set_title("Десятичные приставки: от гига- до нано-")
    save(fig, "prefix-ladder.png")


def meridian_metre():
    fig, ax = blank(6.2, 4.4, (-2.1, 3.9), (-2.0, 2.2))
    ax.add_patch(Circle((0, 0), 1.6, fc=GLASS, ec=INK, lw=2))
    ax.add_patch(Ellipse((0, 0), 1.6, 3.2, fc="none", ec=BLUE, lw=2.2))
    ax.plot([0, 0], [-1.85, 1.85], color=MUTED, ls="--", lw=1)
    ax.text(0, 1.98, "С", ha="center", fontsize=11)
    ax.text(0, -2.25, "Ю", ha="center", fontsize=11)
    ax.plot(0, 0.0, "o", color=INK, ms=1)
    # Paris lies on the meridian ellipse: (x/0.8)^2 + (y/1.6)^2 = 1 at y = 1.0 gives x = 0.62
    ax.text(0.75, 1.0, "Париж", fontsize=10.5, color=INK, va="center")
    ax.plot(0.62, 1.0, "o", color=RED, ms=6, zorder=5)
    ax.text(-0.15, -0.1, "Парижский\nмеридиан", ha="right", fontsize=10.5, color=BLUE)
    ax.text(2.0, 1.3, "длина меридиана\n$4\\cdot10^{7}$ м = 40 000 км", fontsize=12)
    ax.text(2.0, 0.2, "1 м $=\\dfrac{1}{40\\,000\\,000}$ меридиана", fontsize=12, color=RED)
    ax.text(2.0, -0.7, "эталон — рейка\nс двумя штрихами", fontsize=10.5, color=GREY)
    save(fig, "meridian-metre.png")


# ---------------------------------------------------------------- lesson 4


def hscale(ax, x0, x1, n, y=0.0, h=0.5, major=None, label_fmt=None, ticks_from=0):
    """Draw a horizontal scale from x0 to x1 with n divisions. Returns tick xs."""
    ax.add_patch(Rectangle((x0 - 0.05 * (x1 - x0), y - h * 1.1), 1.1 * (x1 - x0), h * 1.1, fc=SCALE, ec=INK, lw=1.2))
    xs = np.linspace(x0, x1, n + 1)
    for i, xx in enumerate(xs):
        big = major is None or (i % major == 0)
        ax.plot([xx, xx], [y, y - (h * 0.95 if big else h * 0.55)], color=INK, lw=1.6 if big else 1.1)
    return xs


def scale_anatomy():
    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    ax.set_xlim(-2.6, 6.8)
    ax.set_ylim(-14, 55)
    ax.axis("off")
    ax.add_patch(Rectangle((-0.35, -12), 0.7, 64, fc=SCALE, ec=INK))
    for v in range(-10, 51, 5):
        big = v % 10 == 0
        ax.plot([0.35 - (0.5 if big else 0.3), 0.35], [v, v], color=INK, lw=1.6 if big else 1.1)
        if big:
            ax.text(0.6, v, str(v), va="center", fontsize=11)
    ax.text(0, 54, "°C", ha="center", fontsize=13)
    # limits
    ax.annotate("верхний предел\nизмерения: 50 °C", (1.6, 50), (3.2, 50), va="center", fontsize=11,
                arrowprops=dict(arrowstyle="<-", color=RED, lw=1.4))
    ax.annotate("нижний предел\nизмерения: −10 °C", (1.6, -10), (3.2, -10), va="center", fontsize=11,
                arrowprops=dict(arrowstyle="<-", color=RED, lw=1.4))
    # stroke, division
    ax.annotate("штрих", (-0.0, 25), (-2.4, 30), fontsize=11.5, va="center",
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.3))
    ax.annotate("деление —\nпромежуток\nмежду штрихами", (-0.15, 17.5), (-2.5, 8), fontsize=11.5, va="center",
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.3))
    ax.plot([-0.5, -0.5], [15, 20], color=GREEN, lw=3)
    # two chosen strokes
    for v in (20, 30):
        ax.plot([0.35, 1.5], [v, v], color=ACCENT, lw=1.2, ls=":")
    ax.plot([1.5, 1.5], [20, 30], color=ACCENT, lw=2)
    ax.text(3.0, 25, "$c=\\dfrac{30-20}{2}=5\\ ^\\circ$C\n(между штрихами 20 и 30\nдва деления)", fontsize=11.5,
            va="center", color=ACCENT)
    save(fig, "scale-thermometer-anatomy.png")


def scale_gallery():
    panels = [
        ("линейка: штрихи 10 и 11 см", 10, 11, 2, "см", "$c=\\dfrac{11-10}{2}=0{,}5$ см", 1),
        ("линейка: между 1 и 2 см", 1, 2, 10, "см", "$c=\\dfrac{2-1}{10}=0{,}1$ см $=1$ мм", 1),
        ("дюймовая линейка: 0 и 1 дюйм", 0, 1, 16, "дюйм", "$c=\\dfrac{1-0}{16}=\\dfrac{1}{16}$ дюйма", 4),
        ("мерный цилиндр: штрихи 20 и 30 мл", 20, 30, 10, "мл", "$c=\\dfrac{30-20}{10}=1$ мл", 5),
        ("шприц: штрихи 4 и 5 мл", 4, 5, 5, "мл", "$c=\\dfrac{5-4}{5}=0{,}2$ мл", 1),
        ("малый шприц: штрихи 2 и 2,5 мл", 2, 2.5, 5, "мл", "$c=\\dfrac{2{,}5-2}{5}=0{,}1$ мл", 1),
        ("термометр: штрихи 40 и 60 °C", 40, 60, 10, "°C", "$c=\\dfrac{60-40}{10}=2\\ ^\\circ$C", 1),
        ("медицинский: штрихи 38 и 39 °C", 38, 39, 10, "°C", "$c=\\dfrac{39-38}{10}=0{,}1\\ ^\\circ$C", 1),
        ("термометр: штрихи 40 и 50 °C", 40, 50, 20, "°C", "$c=\\dfrac{50-40}{20}=0{,}5\\ ^\\circ$C", 2),
        ("нижняя шкала линейки: 0 и 1 мм", 0, 1, 2, "мм", "$c=\\dfrac{1-0}{2}=0{,}5$ мм", 1),
    ]
    fig, axs = plt.subplots(5, 2, figsize=(9, 8.2))
    for ax, (title, a, b, n, unit, formula, major) in zip(axs.flat, panels):
        ax.set_xlim(-0.12, 1.55)
        ax.set_ylim(-1.05, 0.7)
        ax.axis("off")
        xs = np.linspace(0, 1, n + 1)
        ax.add_patch(Rectangle((-0.06, -0.62), 1.12, 0.62, fc=SCALE, ec=INK, lw=1.1))
        for i, xx in enumerate(xs):
            big = (i % major == 0) or i == n
            ax.plot([xx, xx], [0, -0.5 if big else -0.28], color=INK, lw=1.5 if big else 1.0)
        fmt = lambda v: num(v, None)
        ax.text(0, -0.85, fmt(a), ha="center", fontsize=10)
        ax.text(1, -0.85, fmt(b), ha="center", fontsize=10)
        ax.text(0, 0.15, title, fontsize=9.5, va="bottom")
        ax.text(1.13, -0.3, formula, fontsize=10, va="center", color=BLUE)
        ax.annotate("", (xs[0], 0.05), (xs[1], 0.05), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.1))
    fig.suptitle("Цена деления $c=(b-a)/n$ у разных шкал", fontsize=13, y=0.995)
    fig.tight_layout()
    save(fig, "scale-division-gallery.png")


def thermometer_reading():
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.set_xlim(19, 41.5)
    ax.set_ylim(-1.8, 1.6)
    ax.axis("off")
    ax.add_patch(Rectangle((19.4, -0.5), 21.2, 1.0, fc=SCALE, ec=INK))
    ax.add_patch(Rectangle((19.4, -0.12), 27 - 19.4, 0.24, fc=RED, ec="none"))
    for v in range(20, 41, 2):
        ax.plot([v, v], [-0.5, -0.5 + (0.45 if v % 20 == 0 else 0.25)], color=INK, lw=1.4)
        ax.plot([v, v], [0.5, 0.5 - (0.45 if v % 20 == 0 else 0.25)], color=INK, lw=1.4)
    ax.text(20, -0.85, "20", ha="center", fontsize=11)
    ax.text(40, -0.85, "40", ha="center", fontsize=11)
    ax.axvspan(26, 28, ymin=0.05, ymax=0.95, color=WARM, alpha=0.4)
    ax.annotate("столбик: 20 + 3,5 деления\nпо 2 °C = 27 °C", (27, 0.5), (30.6, 1.05), fontsize=11, va="center",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))
    ax.text(27, -1.35, "точность — половина цены деления: $27\\pm1\\ ^\\circ$C", ha="center", color=ACCENT, fontsize=11)
    ax.text(41.4, 0, "°C", fontsize=11, va="center")
    save(fig, "thermometer-reading.png")


def vernier_reading():
    fig, axs = plt.subplots(2, 1, figsize=(9, 5.6))
    cases = [(1.7, 0, 12, "модель нониуса: 1 деление основной шкалы + 0,7 → 1,7"),
             (11.5, 8, 22, "штангенциркуль, диаметр ручки: 11 мм + 0,5 мм → 11,5 мм")]
    for ax, (val, lo, hi, title) in zip(axs, cases):
        ax.set_xlim(lo - 0.5, hi + 0.5)
        ax.set_ylim(-2.7, 1.9)
        ax.axis("off")
        ax.set_title(title, fontsize=11.5, loc="left")
        ax.add_patch(Rectangle((lo - 0.5, 0.0), hi - lo + 1, 0.85, fc=SCALE, ec=INK))
        for m in range(lo, hi + 1):
            ax.plot([m, m], [0, 0.55], color=INK, lw=1.4)
            if (m % 5 == 0) or hi - lo < 8:
                ax.text(m, 1.05, str(m), ha="center", fontsize=9.5)
        ax.text(lo - 0.3, 1.5, "основная шкала, мм", fontsize=9.5, color=GREY, va="center")
        ax.add_patch(Rectangle((val - 0.1, -1.15), 9 + 0.1 + 0.4, 1.15, fc=GLASS, ec=INK))
        k_match = None
        for k in range(11):
            xv = val + 0.9 * k
            ax.plot([xv, xv], [0, -0.55 if k % 5 else -0.75], color=INK, lw=1.4)
            ax.text(xv, -0.98, str(k), ha="center", va="center", fontsize=7.5, color=GREY)
            frac = (xv - lo) % 1
            near = min(frac, 1 - frac) < 1e-6
            if k > 0 and near and k_match is None:
                k_match = k
                ax.plot([xv, xv], [-0.75, 0.55], color=RED, lw=2.4)
        ax.text(val, -1.5, "нуль нониуса", ha="center", fontsize=9.5, color=BLUE)
        ax.plot([val, val], [-0.75, 0.6], color=BLUE, lw=2.2)
        ax.text(val + 0.9 * (k_match or 0), -2.15, "совпал %d-й штрих нониуса → десятые: 0,%d" % (k_match, k_match),
                ha="center", fontsize=10.5, color=RED)
        ax.text(hi + 0.4, 1.5, "10 делений нониуса = 9 делений основной шкалы", fontsize=9, color=GREY, ha="right",
                va="center")
    fig.tight_layout()
    save(fig, "vernier-reading.png")


def micrometer_reading():
    fig, ax = plt.subplots(figsize=(9, 4.3))
    ax.set_xlim(14.3, 25.2)
    ax.set_ylim(-4.2, 4.2)
    ax.axis("off")
    # sleeve (stationary)
    ax.add_patch(Rectangle((14.5, -0.9), 20.59 - 14.5, 1.8, fc=LIGHT, ec=INK))
    ax.plot([14.5, 20.59], [0, 0], color=INK, lw=1.4)
    for mm in range(15, 21):
        ax.plot([mm, mm], [0, 0.75], color=INK, lw=1.3)
        ax.text(mm, 1.1, str(mm) if mm % 5 == 0 else "", ha="center", fontsize=11)
    for mm in range(15, 21):
        ax.plot([mm + 0.5, mm + 0.5], [0, -0.6], color=INK, lw=1.3)
    ax.text(14.5, 1.85, "неподвижная шкала: основная, цена деления 1 мм,\nи дополнительная (со смещением 0,5 мм)",
            fontsize=9.5, color=GREY, va="bottom")
    # drum
    ax.add_patch(Rectangle((20.59, -2.9), 4.0, 5.8, fc=tint(INK, 0.8), ec=INK, lw=1.6))
    ax.plot([20.59, 24.59], [0, 0], color=RED, lw=1.8)
    for nmark in range(0, 17):
        yy = (9 - nmark) * 0.35
        if abs(yy) > 2.8:
            continue
        ax.plot([20.59, 20.59 + (0.7 if nmark % 5 == 0 else 0.4)], [yy, yy], color=INK, lw=1.3)
        if nmark % 5 == 0 or nmark == 9:
            ax.text(21.5, yy + (0.22 if nmark == 9 else 0), str(nmark), va="center", fontsize=10,
                    color=BLUE if nmark == 9 else INK, weight="bold" if nmark == 9 else None)
    ax.text(22.75, -3.4, "барабан: 50 делений по 0,01 мм", ha="center", fontsize=9.5, color=GREY)
    ax.annotate("край барабана: за штрихом 20, за\nполумиллиметровым штрихом", (20.59, -0.75), (16.2, -2.5),
                fontsize=10.5, arrowprops=dict(arrowstyle="->", color=INK, lw=1.2), va="center")
    ax.text(14.5, -3.7, "20 мм + 0,5 мм + 0,09 мм = 20,59 мм", fontsize=12.5, color=RED, weight="bold")
    save(fig, "micrometer-reading.png")


# ---------------------------------------------------------------- lesson 7


def coin_measurements():
    data = [("мерная лента", 20.0, 2.5, "20 ± 2,5"), ("линейка", 21.0, 0.5, "21,0 ± 0,5"),
            ("штангенциркуль", 20.7, 0.1, "20,7 ± 0,1"), ("микрометр", 20.59, 0.01, "20,59 ± 0,01")]
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw=dict(width_ratios=[1.15, 1]))
    for ax, (lo, hi) in zip(axs, ((16.5, 24), (20.45, 20.95))):
        for i, (name, v, e, txt) in enumerate(data):
            if v - e > hi or v + e < lo:
                continue
            ax.errorbar(v, i, xerr=e, fmt="o", color=[METAL, COPPER, BLUE, GREEN][i], capsize=5, lw=2.4, ms=6)
        ax.axvspan(20.58, 20.60, color=GREEN, alpha=0.25, lw=0)
        ax.set_yticks(range(4))
        ax.set_yticklabels([d[0] for d in data] if ax is axs[0] else [""] * 4)
        ax.set_ylim(-0.6, 3.6)
        ax.set_xlim(lo, hi)
        ax.grid(axis="x", color=GRID)
        ax.set_xlabel("диаметр монеты, мм")
    axs[0].set_title("Все приборы")
    axs[1].set_title("Приближение к 20,6 мм")
    axs[1].invert_yaxis()
    axs[0].invert_yaxis()
    save(fig, "coin-measurements.png")


def significant_digits():
    rows = [("20,59 мм", "20,59", 2), ("2,059 см", "2,059", 3), ("0,2059 дм", "0,2059", 4), ("0,02059 м", "0,02059", 5)]
    fig, ax = blank(10.6, 4.6, (-0.3, 14.2), (-2.3, 5.4))
    for r, (label, s, after) in enumerate(rows):
        y = 4.2 - r * 1.15
        ax.text(-0.1, y, label, va="center", fontsize=12)
        digs = [c for c in s if c != ","]
        lead = len(digs) - len("".join(digs).lstrip("0"))
        x = 3.4
        k = 0
        for c in s:
            if c == ",":
                ax.text(x - 0.3, y - 0.1, ",", ha="center", va="center", fontsize=18)
                x += 0.4
                continue
            if k < lead:
                fc, tc = LIGHT, GREY
            elif k == len(digs) - 1:
                fc, tc = DOUBT_FILL, RED
            else:
                fc, tc = RIGHT_FILL, GREEN
            ax.add_patch(Rectangle((x - 0.42, y - 0.42), 0.84, 0.84, fc=fc, ec=MUTED))
            ax.text(x, y, c, ha="center", va="center", fontsize=16, color=tc, weight="bold")
            x += 0.95
            k += 1
        ax.text(9.9, y, "знаков после запятой: %d" % after, va="center", fontsize=10, color=GREY)
    ax.add_patch(Rectangle((3.0, -0.6), 0.4, 0.4, fc=LIGHT, ec=MUTED))
    ax.text(3.6, -0.4, "левые нули: масштаб, не точность", va="center", fontsize=10, color=GREY)
    ax.add_patch(Rectangle((3.0, -1.15), 0.4, 0.4, fc=RIGHT_FILL, ec=MUTED))
    ax.text(3.6, -0.95, "верные цифры", va="center", fontsize=10, color=GREEN)
    ax.add_patch(Rectangle((3.0, -1.7), 0.4, 0.4, fc=DOUBT_FILL, ec=MUTED))
    ax.text(3.6, -1.5, "сомнительная цифра", va="center", fontsize=10, color=RED)
    ax.text(9.9, -1.0, "везде 4 значащие цифры:\nточность одна и та же", fontsize=11, va="center")
    save(fig, "significant-digits.png")


def zero_precision():
    labels = ["2 см", "2,0 см", "2,00 см", "2,000 см"]
    half = [0.5, 0.05, 0.005, 0.0005]
    ranges = ["от 1,5 до 2,5 см", "от 1,95 до 2,05 см", "от 1,995 до 2,005 см", "от 1,9995 до 2,0005 см"]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    y = np.arange(4)
    ax.barh(y, half, color=[METAL, COPPER, BLUE, GREEN], height=0.55)
    ax.set_xscale("log")
    ax.set_xlim(2e-4, 3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=12)
    ax.invert_yaxis()
    for i, (h, r) in enumerate(zip(half, ranges)):
        ax.text(h * 1.25, i, "±%s: %s" % (num(h, None), r), va="center", fontsize=10)
    ax.set_xlabel("допустимое отклонение, см (логарифмическая шкала)")
    ax.set_title("Нули справа — значащие цифры")
    ax.grid(axis="x", color=GRID)
    save(fig, "zero-precision.png")


def rounding_circumference():
    fig, axs = plt.subplots(2, 1, figsize=(8.6, 5.4), gridspec_kw=dict(height_ratios=[1.15, 1]))
    ax = axs[0]
    ax.set_xlim(-0.3, 11.5)
    ax.set_ylim(-1.9, 2.5)
    ax.axis("off")
    ax.text(0, 2.1, "$d=2{,}1$ см (две значащие цифры), $\\pi\\approx3{,}14$; калькулятор: $C=\\pi d$", fontsize=11.5)
    s = "6,594"
    x = 1.0
    keep = 0
    for c in s:
        if c == ",":
            ax.text(x - 0.05, 0.75, ",", ha="center", fontsize=20)
            x += 0.5
            continue
        kept = keep < 2
        ax.add_patch(Rectangle((x - 0.45, 0.35), 0.9, 0.95, fc=RIGHT_FILL if kept else LIGHT, ec=MUTED))
        ax.text(x, 0.82, c, ha="center", va="center", fontsize=18, color=GREEN if kept else GREY, weight="bold")
        x += 1.0
        keep += 1
    ax.annotate("", (3.6, 0.3), (1.0, 0.3), arrowprops=dict(arrowstyle="-", color=GREEN, lw=2))
    ax.text(2.3, -0.05, "две цифры, как у данных; за ними 9 — округляем вверх", ha="center", fontsize=10, color=GREEN)
    ax.text(5.2, 0.8, "→", fontsize=24, va="center")
    ax.text(6.0, 0.8, "6,6 см", fontsize=22, va="center", color=GREEN, weight="bold")
    ax.text(0, -1.3, "лишние цифры не несут информации: длину знаем не лучше, чем две цифры", fontsize=10.5, color=GREY)
    ax = axs[1]
    lo, hi = 2.05 * 3.14, 2.15 * 3.14
    ax.axvspan(lo, hi, color=BLUE, alpha=0.25, lw=0, label="область неопределённости")
    ax.plot([6.594], [0.35], "o", color=GREY, ms=8, label="калькулятор: 6,594")
    ax.plot([6.6], [-0.35], "s", color=GREEN, ms=10, label="ответ: 6,6")
    ax.set_yticks([])
    ax.set_xlim(6.3, 6.9)
    ax.set_ylim(-1, 1)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("длина окружности $C$, см")
    ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    ax.set_title("d известен с точностью ±0,05 см, значит C — в пределах ±0,16 см", fontsize=10.5, loc="left")
    fig.tight_layout()
    save(fig, "rounding-circumference.png")


# ---------------------------------------------------------------- lesson 8


def standard_form_shift():
    fig, ax = blank(10.4, 6.0, (0, 13.4), (-0.3, 8.9))
    # row 1
    def digits(x0, y, s, sz=20, hl=None):
        for i, c in enumerate(s):
            ax.text(x0 + i * 0.62, y, c, ha="center", va="center", fontsize=sz, family="DejaVu Sans Mono")
    digits(0.6, 7.0, "120000,")
    ax.text(5.0, 7.0, "=  $1{,}2\\cdot10^{5}$", fontsize=18, va="center")
    # five places left: from after the last zero to the gap between "1" and "2"
    arrow(ax, (0.6 + 6 * 0.62 - 0.15, 7.55), (0.6 + 0.31, 7.55), color=RED, lw=1.8, connectionstyle="arc3,rad=0.4")
    ax.text(2.4, 8.55, "запятая сдвинута на 5 знаков влево $\\rightarrow$ $10^{5}$", color=RED, fontsize=10, ha="center")
    # row 2
    digits(0.6, 5.2, "0,0001")
    ax.text(5.0, 5.2, "=  $10^{-4}$", fontsize=18, va="center")
    ax.text(0.6, 4.55, "считаем нули вместе с нулём перед запятой: 1, 2, 3, 4", fontsize=10, color=RED)
    # row 3
    digits(0.6, 3.5, "0,007")
    ax.text(5.0, 3.5, "=  $7\\cdot10^{-3}$", fontsize=18, va="center")
    # normalization
    ax.add_patch(Rectangle((0.2, -0.1), 13.0, 2.6, fc=LIGHT, ec=MUTED))
    ax.text(0.6, 2.05, "$1{,}2\\cdot10^{5}$", fontsize=18, va="center")
    ax.annotate("мантисса", (1.5, 1.85), (1.5, 0.85), ha="center", color=BLUE, fontsize=11,
                arrowprops=dict(arrowstyle="->", color=BLUE))
    ax.annotate("множитель $10^{n}$", (3.4, 2.0), (4.0, 0.85), ha="center", color=GREEN, fontsize=11,
                arrowprops=dict(arrowstyle="->", color=GREEN))
    ax.text(6.3, 2.05, "нормализованное: $1\\leqslant$ мантисса $<10$", fontsize=11.5, va="center")
    ax.text(6.3, 1.15, "$12\\cdot10^{4}$ — то же число, ненормализованное", fontsize=10.5, va="center", color=GREY)
    save(fig, "standard-form-shift.png")


def area_unit_conversion():
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.6))
    ax = axs[0]
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 10.6)
    ax.set_ylim(-1.3, 11.4)
    ax.axis("off")
    for i in range(10):
        for j in range(10):
            hl = (i == 0 and j == 9)
            ax.add_patch(Rectangle((i, j), 1, 1, fc=tint(WARM, 0.5) if hl else tint(SKY, 0.85), ec=MUTED, lw=0.8))
    ax.add_patch(Rectangle((0, 0), 10, 10, fc="none", ec=INK, lw=2))
    ax.annotate("", (0, -0.6), (10, -0.6), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(5, -1.15, "1 м = 10 дм", ha="center", fontsize=11)
    ax.text(-0.5, 5, "1 м = 10 дм", rotation=90, ha="right", va="center", fontsize=11)
    ax.text(5, 10.7, "$1\\ \\mathrm{м}^2=10\\cdot10=100\\ \\mathrm{дм}^2$", ha="center", fontsize=12.5)
    ax.text(0.5, 9.5, "1 дм²", ha="center", va="center", fontsize=7.5)
    ax = axs[1]
    ax.axis("off")
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 10)
    rows = [
        ("1 м = 10 дм", "$1\\ \\mathrm{м}^2=10^{2}\\ \\mathrm{дм}^2$"),
        ("1 м = 100 см", "$1\\ \\mathrm{м}^2=10^{4}\\ \\mathrm{см}^2$"),
        ("1 м = 1000 мм", "$1\\ \\mathrm{м}^2=10^{6}\\ \\mathrm{мм}^2$"),
        ("1 км = 1000 м", "$1\\ \\mathrm{км}^2=10^{6}\\ \\mathrm{м}^2$"),
    ]
    ax.text(0, 9.4, "длина  →  площадь: показатель степени удваивается", fontsize=11, color=GREY)
    for k, (a, b) in enumerate(rows):
        y = 7.6 - k * 1.9
        ax.text(0, y, a, fontsize=13, va="center")
        arrow(ax, (5.0, y), (5.9, y), color=RED)
        ax.text(6.2, y, b, fontsize=13, va="center")
    save(fig, "area-unit-conversion.png")


def speed_scale_conversion():
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.set_xlim(-9, 78)
    ax.set_ylim(-3.4, 3.4)
    ax.axis("off")
    ax.plot([0, 72], [1.3, 1.3], color=INK, lw=2)
    ax.plot([0, 72], [-1.3, -1.3], color=INK, lw=2)
    for v in range(0, 73, 9):
        ax.plot([v, v], [1.3, 1.6], color=INK)
        ax.text(v, 1.9, str(v), ha="center", fontsize=10)
    for u in range(0, 21, 5):
        x = u * 3.6
        ax.plot([x, x], [-1.3, -1.6], color=INK)
        ax.text(x, -2.1, str(u), ha="center", fontsize=10)
    ax.text(-8.5, 1.3, "км/ч", fontsize=12, va="center", color=BLUE, weight="bold")
    ax.text(-8.5, -1.3, "м/с",fontsize=12, va="center", color=GREEN, weight="bold")
    for u in (5, 10, 20):
        x = u * 3.6
        ax.plot([x, x], [1.3, -1.3], color=GRID, lw=1.2, ls="--")
    ax.plot([18, 18], [1.3, -1.3], color=RED, lw=2.2)
    ax.text(18.6, 0, "18 км/ч = 5 м/с", color=RED, fontsize=12, va="center", weight="bold")
    ax.text(40, 0, "1 м/с = 3,6 км/ч", fontsize=12.5, va="center")
    ax.text(0, -2.9, "$1\\ \\frac{\\mathrm{м}}{\\mathrm{с}}=\\frac{10^{-3}\\ \\mathrm{км}}{\\frac{1}{3600}\\ \\mathrm{ч}}=3{,}6\\ \\frac{\\mathrm{км}}{\\mathrm{ч}}$",
            fontsize=12, va="center")
    save(fig, "speed-scale-conversion.png")


ALL = [muller_lyer, knowledge_helix, newton_tube, fall_speed_graph, mica_boat, theory_applicability, prefix_ladder,
       meridian_metre, scale_anatomy, scale_gallery, thermometer_reading, vernier_reading, micrometer_reading,
       coin_measurements, significant_digits, zero_precision, rounding_circumference, standard_form_shift,
       area_unit_conversion, speed_scale_conversion]

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for fn in ALL:
        if not want or fn.__name__ in want:
            fn()
