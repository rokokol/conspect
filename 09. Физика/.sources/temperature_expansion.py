"""Figures for the notes "Температура. Тепловое равновесие" and "Тепловое расширение" (section f10, lessons 98-104).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 temperature_expansion.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefixes temp- and expansion-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ACCENT, ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
COLD = BLUE
GOLD = WARM
WATER = tint(SKY, 0.6)  # water as a body
WATER_PALE = tint(SKY, 0.8)
OIL = WARM
MERCURY = METAL
SPIRIT = tint(VIOLET, 0.35)  # coloured water or spirit in a flask or a thermometer
FLAME = WARM
GLASS = tint(SKY, 0.7)
IRON = tint(INK, 0.2)  # dark steel
LIGHT_METAL = tint(INK, 0.8)  # a pale metal body
WOOD = tint(COPPER, 0.6)  # a wooden or cork support
# the colour of a metal in a line or a fill, and its linear expansion coefficient, 1/degC
METALS = {
    "цинк": (VIOLET, 3.0e-5),
    "латунь": (ACCENT, 1.9e-5),
    "медь": (COPPER, 1.7e-5),
    "железо": (IRON, 1.2e-5),
    "сталь": (GREEN, 1.1e-5),
    "стекло": (SKY, 0.9e-5),
}


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", scale=13, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def dim(ax, p, q, text, off=(0, 0.25), color=INK, fs=11, ha="center"):
    arrow(ax, p, q, color=color, style="<|-|>", scale=9, lw=1.2)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha=ha, va="center", color=color, fontsize=fs)


def grid(ax):
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- temperature


def temp_equilibrium():
    t = np.linspace(0, 10, 200)
    hot = 50 + 40 * np.exp(-t / 2.2)
    cold = 50 - 40 * np.exp(-t / 2.2)
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.plot(t, hot, color=HOT, lw=2.4)
    ax.plot(t, cold, color=COLD, lw=2.4)
    ax.axhline(50, color=GREY, lw=1.2, ls="--")
    ax.text(3.2, 90, "горячее тело\nостывает", color=HOT, va="top")
    ax.text(3.2, 10, "холодное тело\nнагревается", color=COLD, va="bottom")
    ax.annotate(
        "тепловое равновесие:\nтемпературы равны",
        xy=(7, 50),
        xytext=(5.6, 72),
        color=INK,
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3),
    )
    ax.set_xlabel("время")
    ax.set_ylabel("температура")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Выравнивание температур")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    save(fig, "temp-equilibrium-curves.png")


def draw_thermometer(ax, x, top, bulb_y, level, label_marks=(), width=0.22, bulb_r=0.5, fill=HOT):
    """Liquid thermometer: reservoir at (x, bulb_y), capillary up to `top`, liquid up to `level`."""
    ax.add_patch(Rectangle((x - width / 2, bulb_y), width, top - bulb_y, fc=PAPER, ec=INK, lw=1.6, zorder=2))
    ax.add_patch(Circle((x, bulb_y), bulb_r, fc=fill, ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Rectangle((x - width / 2 + 0.03, bulb_y), width - 0.06, level - bulb_y, fc=fill, ec="none", zorder=4))
    for y, txt in label_marks:
        ax.plot([x + width / 2, x + width / 2 + 0.25], [y, y], color=INK, lw=1.4, zorder=5)
        ax.text(x + width / 2 + 0.35, y, txt, va="center", color=INK)


def temp_liquid_thermometer():
    fig, ax = blank(8.2, 5.4, (-2.2, 7.4), (-1.6, 5.4))
    # melting ice
    ax.add_patch(Rectangle((-1.6, -1.4), 3.2, 1.9, fc=WATER_PALE, ec=INK, lw=1.5))
    for (cx, cy) in [(-1.0, -0.6), (0.9, -0.9), (-0.3, 0.1), (1.2, 0.0)]:
        ax.add_patch(Rectangle((cx - 0.22, cy - 0.22), 0.44, 0.44, fc=PAPER, ec=GREY, lw=1, angle=15))
    draw_thermometer(ax, 0, 4.6, 0, 1.4, label_marks=[(1.4, "0 °C")], fill=COLD)
    ax.text(0, -1.9, "тающий лёд", ha="center", va="top")
    # boiling water
    ax.add_patch(Rectangle((3.4, -1.4), 3.2, 1.9, fc=WATER_PALE, ec=INK, lw=1.5))
    for (bx, by) in [(3.9, -0.9), (4.4, -0.3), (5.6, -0.8), (6.0, -0.2), (5.0, -1.1)]:
        ax.add_patch(Circle((bx, by), 0.1, fc=PAPER, ec=GREY, lw=1))
    draw_thermometer(ax, 5.0, 4.6, 0, 3.9, label_marks=[(3.9, "100 °C")], fill=HOT)
    ax.text(5.0, -1.9, "кипящая вода\n$p$ = 760 мм рт. ст.", ha="center", va="top")
    # 100 equal parts
    for i in range(11):
        y = 1.4 + (3.9 - 1.4) * i / 10
    ax.text(5.55, 2.65, "100 равных\nчастей", va="center", color=INK, fontsize=10)
    ax.plot([5.28, 5.5], [1.4, 1.4], color=GREY, lw=1, ls=":")
    dim(ax, (5.4, 1.4), (5.4, 3.9), "", color=GREY)
    ax.text(3.1, 4.9, "капилляр", ha="right", color=INK)
    ax.annotate("", xy=(5.0, 4.4), xytext=(3.2, 4.9), arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.text(3.1, 0.55, "резервуар", ha="right", color=INK)
    ax.annotate("", xy=(4.6, 0.1), xytext=(3.2, 0.55), arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.text(2.55, 2.65, "реперные\nточки", ha="center", va="center", color=ACCENT, fontsize=10.5, fontweight="bold")
    arrow(ax, (1.9, 2.3), (0.95, 1.55), color=ACCENT, lw=1.2)
    arrow(ax, (3.2, 3.0), (4.5, 3.75), color=ACCENT, lw=1.2)
    save(fig, "temp-liquid-thermometer.png")


def temp_scales():
    """Celsius, Kelvin and Fahrenheit side by side; range -30..110 degrees Celsius."""
    def c2k(c):
        return c + 273.15

    def c2f(c):
        return 1.8 * c + 32

    pts = [
        (-17.8, "смесь льда\nи нашатыря"),
        (0.0, "таяние льда"),
        (36.6, "тело здорового\nчеловека"),
        (100.0, "кипение воды"),
    ]
    lo, hi = -30, 110
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    ax.set_xlim(-0.6, 12.4)
    ax.set_ylim(lo - 12, hi + 16)
    ax.axis("off")
    xs = {"C": 1.0, "K": 4.2, "F": 7.4}
    names = {"C": "Цельсий, °C", "K": "Кельвин, К", "F": "Фаренгейт, °F"}
    conv = {"C": lambda c: c, "K": c2k, "F": c2f}
    fmt = {"C": ".1f", "K": ".2f", "F": ".1f"}
    for key, x in xs.items():
        ax.plot([x, x], [lo, hi], color=INK, lw=2.2)
        ax.text(x, hi + 10, names[key], ha="center", fontsize=12, fontweight="bold")
        # ticks every 10 °C
        for c in range(lo, hi + 1, 10):
            ax.plot([x - 0.18, x], [c, c], color=GREY, lw=1)
    for c, label in pts:
        ax.plot([xs["C"], xs["F"]], [c, c], color=GRID, lw=1.2, zorder=0)
        for key, x in xs.items():
            val = conv[key](c)
            ax.plot([x - 0.3, x + 0.1], [c, c], color=HOT if c == 100 else COLD if c <= 0 else GREEN, lw=2.4)
            txt = num(val, fmt[key])
            if abs(val) < 0.05:
                txt = "0"
            ax.text(x + 0.25, c + 0.3, txt.replace("-", "−"), va="bottom", fontsize=11)
        ax.text(9.7, c, label, va="center", ha="left", fontsize=10, color=INK)
    ax.text(0.2, lo - 6, "Диапазон −30…110 °C; абсолютный нуль лежит ниже: 0 К = −273,15 °C = −459,67 °F", fontsize=9, color=NOTE, ha="left")
    save(fig, "temp-scales-side-by-side.png")


def temp_conversion_line():
    c = np.linspace(-40, 110, 100)
    f = 1.8 * c + 32
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(c, f, color=INK, lw=2)
    marks = [
        (-17.8, 0.0, "0 °F — смесь льда\nи нашатыря", (14, -22)),
        (0, 32, "таяние льда", (40, 10)),
        (36.6, 97.9, "тело здорового\nчеловека", (0, 150)),
        (100, 212, "кипение воды", (32, 195)),
    ]
    for cx, fy, txt, off in marks:
        ax.plot(cx, fy, "o", color=HOT, ms=7, zorder=3)
        ax.annotate(txt, (cx, fy), xytext=off, textcoords="data", fontsize=9.5, color=INK, va="center", arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.plot([-40], [-40], "s", color=COLD, ms=7)
    ax.annotate("−40: шкалы совпадают", (-40, -40), xytext=(-38, 40), fontsize=9.5, color=COLD, va="center", arrowprops=dict(arrowstyle="-", color=COLD, lw=1))
    grid(ax)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("$t_F$, °F")
    ax.set_title("Фаренгейт против Цельсия")
    ax.set_xlim(-45, 115)
    ax.set_ylim(-45, 225)
    save(fig, "temp-conversion-line.png")


def temp_ranges():
    data = [
        ("ртуть", -35, 750, HOT),
        ("спирт", -80, 70, GOLD),
        ("пентан", -200, 35, COLD),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, (name, a, b, col) in enumerate(data):
        ax.barh(i, b - a, left=a, height=0.5, color=col, alpha=0.85, ec=INK)
        ax.text(a - 10, i, f"{a}".replace("-", "−"), ha="right", va="center", fontsize=10)
        ax.text(b + 10, i, f"{b}", ha="left", va="center", fontsize=10, bbox=dict(fc=PAPER, ec="none", pad=1.5), zorder=5)
    ax.axvline(0, color=INK, lw=1.2, ls="--")
    ax.axvline(100, color=INK, lw=1.2, ls="--")
    ax.text(-8, 2.55, "0 °C", ha="right", fontsize=9.5)
    ax.text(108, 2.55, "100 °C", ha="left", fontsize=9.5)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([d[0] for d in data], fontsize=12)
    ax.set_xlim(-330, 830)
    ax.set_ylim(-0.6, 2.8)
    ax.set_xlabel("температура, °C")
    ax.set_title("Рабочие диапазоны жидкостей")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    grid(ax)
    save(fig, "temp-thermometer-ranges.png")


# ------------------------------------------------------------------ expansion


def water_density(t):
    """Tanaka et al. 2001 formula for the density of air-free water, kg/m^3."""
    a1, a2, a3, a4, a5 = -3.983035, 301.797, 522528.9, 69.34881, 999.974950
    return a5 * (1 - (t + a1) ** 2 * (t + a2) / (a3 * (t + a4)))


def expansion_water_density():
    t = np.linspace(0, 12, 300)
    rho = water_density(t)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(t, rho, color=COLD, lw=2.4)
    ax.axvspan(0, 4, color=WATER_PALE, zorder=0)
    ax.axvline(4, color=GREY, lw=1.2, ls="--")
    ax.plot([3.98], [water_density(3.98)], "o", color=HOT, ms=7, zorder=3)
    ax.annotate("наибольшая плотность\nпри 4 °C", (3.98, water_density(3.98)), (5.0, 999.985), fontsize=10.5, va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(0.2, 999.75, "нагревание: вода\nсжимается", fontsize=10, color=COLD, va="bottom")
    ax.text(8.6, 999.93, "нагревание: вода\nрасширяется", fontsize=10, color=HOT, ha="center", va="center")
    grid(ax)
    ax.set_xlabel("температура, °C")
    ax.set_ylabel("плотность, кг/м³")
    ax.set_title("Плотность воды около 4 °C")
    ax.set_ylim(999.7, 1000.0)
    ax.set_xlim(0, 10)
    ax.text(0.2, 999.705, "справочные значения, не из лекции", ha="left", fontsize=8.5, color=NOTE)
    save(fig, "expansion-water-density.png")


def expansion_lake():
    fig, ax = blank(5.4, 5.0, (-0.2, 5.4), (-0.4, 5.2))
    ax.add_patch(Rectangle((0.4, 0.3), 3.0, 4.0, fc=PAPER, ec=INK, lw=1.6))
    layers = [(3.6, 4.3, tint(SKY, 0.85), "лёд, 0 °C"), (2.8, 3.6, tint(SKY, 0.7), "0…1 °C"), (2.0, 2.8, tint(SKY, 0.55), "2 °C"), (1.2, 2.0, tint(SKY, 0.4), "3 °C"), (0.3, 1.2, tint(SKY, 0.25), "4 °C")]
    for a, b, col, txt in layers:
        ax.add_patch(Rectangle((0.4, a), 3.0, b - a, fc=col, ec=GREY, lw=0.8))
        ax.text(3.6, (a + b) / 2, txt, va="center", fontsize=10.5)
    ax.text(0.4, 4.75, "Водоём зимой", fontsize=12, fontweight="bold")
    ax.text(0.4, -0.15, "схема, не из лекции", fontsize=8.5, color=NOTE, va="top")
    ax.text(1.9, 0.75, "плотность\nнаибольшая", ha="center", va="center", fontsize=9.5, color=INK)
    save(fig, "expansion-lake-layers.png")


def flask_neck(ax, cx, cy, r, hw, ytop, level, fc, alpha=1.0, lw=1.6):
    """Round flask whose neck opens into the bulb: one fill and one outline, no seam at the join."""
    jy = cy + np.sqrt(r * r - hw * hw)
    a0 = np.arctan2(jy - cy, hw)
    arc = np.linspace(a0, np.pi - a0 - 2 * np.pi, 240)
    pts = list(zip(cx + r * np.cos(arc), cy + r * np.sin(arc)))
    ax.add_patch(Polygon([(cx + hw, level)] + pts + [(cx - hw, level)], closed=True, fc=fc, ec="none", alpha=alpha, zorder=2))
    if level < ytop:
        ax.add_patch(Polygon([(cx + hw, ytop), (cx + hw, level), (cx - hw, level), (cx - hw, ytop)], closed=True, fc=PAPER, ec="none", zorder=2))
    ax.add_patch(Polygon([(cx + hw, ytop), (cx + hw, jy)] + pts + [(cx - hw, jy), (cx - hw, ytop)], closed=False, fill=False, ec=INK, lw=lw, zorder=3))
    ax.plot([cx - hw, cx + hw], [ytop, ytop], color=INK, lw=lw, solid_capstyle="butt", zorder=3)


def clamp(ax, x, y, w=0.7, h=1.2):
    ax.add_patch(Rectangle((x, y), w, h, fc=METAL, ec=INK, lw=1.4))
    ax.plot([x + w / 2] * 2, [y, y + h], color=INK, lw=1)


def expansion_rod_needle():
    fig, ax = blank(9.6, 4.2, (-0.6, 11.8), (-1.4, 4.0))
    # stand base
    ax.add_patch(Rectangle((0.0, -0.3), 1.8, 0.35, fc=LIGHT, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.5, 0.05), 0.8, 1.7, fc=METAL, ec=INK, lw=1.4))  # vise
    ax.text(0.9, -0.7, "тиски", ha="center", fontsize=10)
    # rod
    # Needle top is at y = 0.62 + 0.16 = 0.78, so the rod rests exactly on it.
    ax.add_patch(Rectangle((1.3, 0.78), 5.6, 0.32, fc=tint(COPPER, 0.5), ec=INK, lw=1.4))
    ax.text(3.7, 1.28, "медная трубка", ha="center", fontsize=10.5)
    # glass plate + support
    ax.add_patch(Rectangle((5.2, 0.35), 2.6, 0.12, fc=GLASS, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((5.5, -0.35), 2.0, 0.7, fc=WOOD, ec=INK, lw=1.2))
    ax.text(6.5, -0.75, "подставка со стеклом", ha="center", fontsize=10)
    # needle under the rod end
    ax.add_patch(Circle((6.9, 0.62), 0.16, fc=INK, ec=INK))
    # pointer (paper arrow)
    for ang, col, ls in [(70, GREY, "--"), (48, HOT, "-")]:
        r = 2.4
        x0, y0 = 6.9, 0.62
        ax.plot([x0, x0 + r * np.cos(np.radians(ang))], [y0, y0 + r * np.sin(np.radians(ang))], color=col, lw=3 if col == HOT else 2, ls=ls, solid_capstyle="round")
    ax.text(10.0, 3.3, "деление\nшкалы", ha="left", fontsize=10)
    # Scale tick across the tip of the initial (grey) pointer at (7.72, 2.88), leader starts at the tick.
    ax.plot([7.53, 7.91], [2.95, 2.81], color=INK, lw=2)
    ax.plot([7.95, 9.9], [2.88, 3.3], color=INK, lw=1)
    # heating
    ax.add_patch(Polygon([[3.1, 0.35], [2.9, -0.2], [3.3, -0.2]], closed=True, fc=FLAME, ec=HOT))
    ax.text(3.1, -0.65, "горелка", ha="center", fontsize=10)
    arrow(ax, (7.45, 0.95), (8.2, 0.95), color=HOT)
    ax.text(8.3, 0.95, "удлинение", va="center", color=HOT, fontsize=10.5)
    ax.text(4.4, 3.0, "игла катится, стрелка на ней\nповорачивается", ha="center", fontsize=10.5, color=INK)
    save(fig, "expansion-rod-needle.png")


def expansion_flask_scheme():
    fig, ax = blank(8.0, 4.8, (-0.4, 10.4), (-0.6, 5.2))
    for x0, lvl, title in [(0.4, 3.2, "холодная"), (5.4, 3.7, "нагретая")]:
        flask_neck(ax, x0 + 1.3, 0.9, 1.1, 0.08, 4.8, lvl, SPIRIT, alpha=0.75)
        ax.text(x0 + 1.3, -0.5, title, ha="center", fontsize=10.5)
    ax.plot([1.7 + 0.1, 6.7 - 0.1], [3.2, 3.2], color=GREY, ls="--", lw=1)
    dim(ax, (6.95, 3.2), (6.95, 3.7), "", color=HOT)
    ax.text(7.15, 3.45, "$\\Delta V$", color=HOT, va="center", fontsize=12)
    ax.text(8.85, 0.9, "кастрюля\nс горячей\nводой", fontsize=9.5, ha="center", va="center", color=COLD)
    ax.add_patch(Rectangle((4.2, -0.3), 5.4, 1.9, fc="none", ec=COLD, lw=1.4, ls="--"))
    save(fig, "expansion-liquid-flask.png")


def expansion_flask_level():
    t = np.linspace(0, 10, 300)
    level = -0.35 * (np.exp(-t / 0.5) - np.exp(-t / 0.2)) * 3 + 1 * (1 - np.exp(-t / 3.0))
    level = np.where(t < 0, 0, level)
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(t, level, color=INK, lw=2.4)
    ax.axhline(0, color=GREY, lw=1.2, ls="--")
    ax.annotate("сначала нагрелась колба:\nобъём колбы вырос,\nуровень опустился", (0.75, level[np.argmin(level)]), (2.3, -0.6), fontsize=10, va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.annotate("потом нагрелась вода:\nона расширяется сильнее стекла", (7.0, level[np.argmin(abs(t - 7.0))]), (4.6, 0.4), fontsize=10, va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.set_xlabel("время после погружения в горячую воду")
    ax.set_ylabel("уровень жидкости")
    ax.set_xticks([])
    ax.set_yticks([0])
    ax.set_yticklabels(["начальный"])
    ax.set_ylim(-0.9, 1.3)
    ax.set_title("Уровень жидкости при резком нагреве")
    save(fig, "expansion-flask-level-time.png")


def expansion_gas_flask():
    fig, ax = blank(6.2, 5.0, (-0.6, 5.6), (-0.6, 5.6))
    ax.add_patch(Circle((2.0, 1.9), 1.7, fc=LIGHT, ec=INK, lw=1.6))
    ax.add_patch(Wedge((2.0, 1.9), 1.7, 180, 360, fc=SPIRIT, ec="none", alpha=0.7))
    ax.add_patch(Rectangle((1.9, 0.5), 0.2, 4.6, fc=PAPER, ec=INK, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((1.93, 0.5), 0.14, 2.6, fc=SPIRIT, ec="none", alpha=0.85, zorder=4))
    ax.text(1.05, 2.65, "воздух", ha="center", fontsize=11, zorder=5)
    ax.text(2.0, 0.7, "", ha="center")
    ax.text(3.9, 1.0, "подкрашенная\nвода", va="center", fontsize=10)
    arrow(ax, (3.85, 1.0), (2.8, 1.0), color=GREY, lw=1.1)
    ax.text(3.95, 4.5, "пробка", fontsize=10)
    ax.annotate("", xy=(2.45, 3.6), xytext=(3.9, 4.45), arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.add_patch(Rectangle((1.6, 3.48), 0.8, 0.22, fc=WOOD, ec=INK, lw=1.2, zorder=6))
    ax.text(3.95, 3.9, "вода выдавливается\nрасширяющимся\nвоздухом", fontsize=10, color=HOT, va="center")
    arrow(ax, (2.35, 4.4), (2.35, 5.2), color=HOT)
    ax.text(-1.5, 1.9, "тёплые\nладони", fontsize=10.5, color=HOT, ha="left", va="center")
    for y in (1.3, 1.9, 2.5):
        arrow(ax, (-0.1, y), (0.45, y), color=HOT, lw=1.3)
    save(fig, "expansion-gas-flask.png")


def expansion_bimetal():
    fig = plt.figure(figsize=(9.6, 4.2))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(-0.3, 6.6)
    ax.set_ylim(-3.9, 2.2)
    ax.set_aspect("equal")
    ax.axis("off")
    # flat strip
    ax.add_patch(Rectangle((0.2, 1.3), 4.4, 0.28, fc=VIOLET, ec=INK, lw=1.3))
    ax.add_patch(Rectangle((0.2, 1.02), 4.4, 0.28, fc=IRON, ec=INK, lw=1.3))
    ax.text(4.75, 1.44, "Zn", va="center", fontsize=10.5)
    ax.text(4.75, 1.16, "Fe", va="center", fontsize=10.5)
    ax.text(0.2, 1.9, "комнатная температура", fontsize=10.5)
    # bent strip: arcs about a centre below
    R = 4.6
    cx, cy = 2.4, -6.3
    th = np.linspace(np.radians(60), np.radians(120), 60)
    for r0, r1, col in [(R, R + 0.28, VIOLET), (R - 0.28, R, IRON)]:
        xs = np.concatenate([cx + r1 * np.cos(th), (cx + r0 * np.cos(th))[::-1]])
        ys = np.concatenate([cy + r1 * np.sin(th), (cy + r0 * np.sin(th))[::-1]])
        ax.add_patch(Polygon(np.column_stack([xs, ys]), closed=True, fc=col, ec=INK, lw=1.3))
    ax.text(4.9, -1.75, "Zn снаружи дуги", fontsize=10.5, color=VIOLET, ha="left")
    ax.text(4.9, -2.2, "Fe внутри", fontsize=10.5, color=INK, ha="left")
    ax.text(0.2, -0.75, "после нагрева", fontsize=10.5)
    ax.add_patch(Polygon([[2.4, -2.6], [2.2, -3.3], [2.6, -3.3]], closed=True, fc=FLAME, ec=HOT))
    # graph
    ax2 = fig.add_axes([0.58, 0.16, 0.4, 0.72])
    t = np.linspace(0, 300, 50)
    for name in ("цинк", "железо"):
        col, a = METALS[name]
        ax2.plot(t, a * t * 1000, color=col, lw=2.4, label=f"{name}, $\\alpha$ = {num(a * 1e5, 1)}$\\cdot 10^{{-5}}$ °C$^{{-1}}$")
    ax2.set_xlabel("$t$, °C")
    ax2.set_ylabel("удлинение стержня 1 м, мм")
    ax2.set_title("Цинк удлиняется сильнее")
    ax2.legend(frameon=False, loc="upper left")
    grid(ax2)
    save(fig, "expansion-bimetal-strip.png")


def expansion_linear_scheme():
    fig, ax = blank(8.0, 3.4, (-0.4, 10.4), (-1.6, 2.2))
    ax.add_patch(Rectangle((0.4, 1.0), 6.0, 0.34, fc=LIGHT_METAL, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.4, 0.0), 6.9, 0.34, fc=tint(RED, 0.7), ec=INK, lw=1.4))
    ax.plot([6.4, 6.4], [0.34, 1.0], color=GREY, ls="--", lw=1)
    ax.text(-0.1, 1.17, "$t_0$", ha="right", va="center", fontsize=12)
    ax.text(-0.1, 0.17, "$t$", ha="right", va="center", fontsize=12)
    dim(ax, (0.4, 1.75), (6.4, 1.75), "$l_0$", off=(0, 0.28), fs=12)
    dim(ax, (0.4, -0.55), (7.3, -0.55), "$l$", off=(0, -0.3), fs=12)
    dim(ax, (6.4, 0.68), (7.3, 0.68), "", color=HOT)
    ax.text(7.55, 0.68, "$\\Delta l = l - l_0$\nабсолютное удлинение", va="center", color=HOT, fontsize=10.5)
    for x in (2.2, 3.8, 5.4):
        ax.add_patch(Polygon([[x, -1.1], [x - 0.15, -1.55], [x + 0.15, -1.55]], closed=True, fc=FLAME, ec=HOT))
    save(fig, "expansion-linear-scheme.png")


def expansion_linear_proportional():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
    ax = axes[0]
    dt = np.array([0, 100, 200])
    ax.plot(dt, dt * 0.001, "o-", color=COLD, lw=2.2, label="$l_0$ = 50 см")
    ax.plot(dt, dt * 0.002, "o-", color=HOT, lw=2.2, label="$l_0$ = 100 см")
    ax.set_xlabel("$\\Delta t$, °C")
    ax.set_ylabel("$\\Delta l$, мм")
    ax.set_title("$\\Delta l \\sim \\Delta t$")
    ax.set_xticks(dt)
    ax.legend(frameon=False)
    grid(ax)
    ax = axes[1]
    l0 = np.array([0, 50, 100])
    ax.plot(l0, l0 * 0.002, "o-", color=INK, lw=2.2)
    ax.set_xlabel("$l_0$, см")
    ax.set_ylabel("$\\Delta l$, мм")
    ax.set_title("$\\Delta l \\sim l_0$ при $\\Delta t$ = 100 °C")
    ax.set_xticks(l0)
    grid(ax)
    fig.text(0.5, -0.04, "числа из рассуждения лектора: линейка 50 см при нагреве на 100 °C удлиняется на 0,1 мм", ha="center", fontsize=9, color=NOTE)
    fig.tight_layout()
    save(fig, "expansion-linear-proportional.png")


def expansion_linear_metals():
    t = np.linspace(0, 300, 50)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for name, (col, a) in METALS.items():
        ax.plot(t, a * t * 1000, color=col, lw=2.4)
        shift = {"латунь": 0.14, "медь": -0.14, "железо": 0.12, "сталь": -0.12}.get(name, 0.0)
        ax.text(302, a * 300 * 1000 + shift, name, color=col, va="center", fontsize=10.5)
    ax.set_xlim(0, 350)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("$\\Delta l$ стержня $l_0$ = 1 м, мм")
    ax.set_title("Удлинение стержня 1 м при $t_0$ = 0 °C")
    grid(ax)
    save(fig, "expansion-linear-metals.png")


def expansion_volume_scheme():
    fig, ax = blank(6.6, 4.4, (-0.4, 8.4), (-0.6, 5.2))
    ax.add_patch(Circle((2.0, 1.6), 1.3, fc=WATER, ec=INK, lw=1.6, alpha=0.85))
    ax.add_patch(Rectangle((1.9, 2.7), 0.2, 2.3, fc=PAPER, ec=INK, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((1.93, 2.7), 0.14, 0.8, fc=WATER, ec="none", zorder=4, alpha=0.85))
    ax.add_patch(Rectangle((1.93, 3.5), 0.14, 0.7, fc=BLUE, ec="none", zorder=4))
    ax.plot([1.5, 2.5], [3.5, 3.5], color=GREY, ls="--", lw=1, zorder=5)
    ax.text(2.9, 3.85, "$\\Delta V$", color=HOT, fontsize=12.5, va="center")
    ax.text(2.9, 3.3, "$V_0$, $t_0$", fontsize=11.5, va="center")
    ax.text(2.9, 4.5, "при $t$: объём $V$", fontsize=11, va="center")
    ax.text(4.4, 1.6, "сосуд не расширяется:\nжидкость выходит\nв капилляр, как столбик\nртути в термометре", fontsize=10, va="center")
    save(fig, "expansion-volume-scheme.png")


def expansion_liquids_volume():
    t = np.linspace(0, 100, 50)
    data = [("нефть", 1.0e-3, HOT), ("подсолнечное масло", 7.82e-4, OIL), ("ртуть", 1.8e-4, MERCURY)]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for name, b, col in data:
        ax.plot(t, 1 + b * t, color=col, lw=2.4)
        ax.text(101, 1 + b * 100, name, va="center", color=col, fontsize=10.5)
    ax.set_xlim(0, 135)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("$V / V_0$")
    ax.set_title("Объём жидкостей при нагревании")
    grid(ax)
    save(fig, "expansion-liquids-volume.png")


def expansion_area_square():
    fig, ax = blank(6.4, 4.2, (-0.6, 8.6), (-1.0, 5.2))
    a = 3.0
    e = 0.3
    ax.add_patch(Rectangle((0, 0), a, a, fc=tint(BLUE, 0.8), ec=INK, lw=1.6))
    ax.add_patch(Rectangle((a, 0), e, a, fc=tint(RED, 0.75), ec=INK, lw=1.2))
    ax.add_patch(Rectangle((0, a), a, e, fc=tint(RED, 0.75), ec=INK, lw=1.2))
    ax.add_patch(Rectangle((a, a), e, e, fc=HOT, ec=INK, lw=1.2))
    ax.text(a / 2, a / 2, "$S_0 = a_0 b_0$", ha="center", va="center", fontsize=13)
    dim(ax, (0, -0.35), (a, -0.35), "$a_0$", off=(0, -0.3), fs=12)
    dim(ax, (a, -0.35), (a + e, -0.35), "", color=HOT)
    ax.text(a + e / 2 + 0.05, -0.75, "$a_0\\alpha t$", color=HOT, ha="center", fontsize=11)
    ax.text(4.3, 3.5, "угловой квадрат\n$S_0\\alpha^2 t^2$:\nв $10^3$ раз меньше\nполосок $S_0\\alpha t$", fontsize=10, va="center", color=HOT)
    ax.annotate("", xy=(a + e / 2, a + e / 2), xytext=(4.25, 3.2), arrowprops=dict(arrowstyle="-|>", color=HOT, lw=1.2))
    ax.text(4.3, 1.2, "$S = S_0(1+\\alpha t)^2$\n$\\approx S_0(1+2\\alpha t)$", fontsize=12, va="center")
    ax.text(4.3, -0.4, "размер квадрата $\\alpha t$ преувеличен", fontsize=8.5, color=NOTE)
    save(fig, "expansion-area-square.png")


def expansion_cube_terms():
    a = METALS["железо"][1]
    t = 100
    x = a * t
    terms = [("1", 1.0), ("$3\\alpha t$", 3 * x), ("$3\\alpha^2 t^2$", 3 * x**2), ("$\\alpha^3 t^3$", x**3)]
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    cols = [METAL, COLD, GREEN, HOT]
    ax.bar(range(len(terms)), [v for _, v in terms], color=cols, ec=INK)
    ax.set_yscale("log")
    ax.set_xticks(range(len(terms)))
    ax.set_xticklabels([n for n, _ in terms], fontsize=12)
    for i, (_, v) in enumerate(terms):
        ax.text(i, v * 1.5, num(v, ".1e").replace("e-0", "·10⁻").replace("e+00", ""), ha="center", fontsize=10)
    ax.set_ylim(1e-10, 30)
    ax.set_title("Слагаемые $(1+\\alpha t)^3$, железо, $t$ = 100 °C")
    ax.set_ylabel("значение слагаемого")
    grid(ax)
    save(fig, "expansion-cube-terms.png")


def expansion_3alpha_error():
    # Each curve stops at the limit of its solid state: zinc melts near 420 C, ordinary glass softens near 500 C.
    tmax = {"цинк": 400, "железо": 1000, "стекло": 500}
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    for name in ("цинк", "железо", "стекло"):
        col, a = METALS[name]
        t = np.linspace(0, tmax[name], 200)
        exact = (1 + a * t) ** 3
        approx = 1 + 3 * a * t
        ax.plot(t, (exact - approx) / exact * 100, color=col, lw=2.2, label=name)
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("погрешность формулы $1+3\\alpha t$, %")
    ax.set_title("Пренебрежение $\\alpha^2t^2$ и $\\alpha^3t^3$")
    ax.legend(frameon=False)
    grid(ax)
    save(fig, "expansion-3alpha-error.png")


def expansion_beta_compare():
    items = [
        ("стекло", 3 * METALS["стекло"][1], METALS["стекло"][0]),
        ("сталь", 3 * METALS["сталь"][1], METALS["сталь"][0]),
        ("железо", 3 * METALS["железо"][1], METALS["железо"][0]),
        ("медь", 3 * METALS["медь"][1], METALS["медь"][0]),
        ("латунь", 3 * METALS["латунь"][1], METALS["латунь"][0]),
        ("цинк", 3 * METALS["цинк"][1], METALS["цинк"][0]),
        ("ртуть", 1.8e-4, MERCURY),
        ("масло\nподсолн.", 7.82e-4, OIL),
        ("нефть", 1.0e-3, HOT),
    ]
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    for i, (n, b, col) in enumerate(items):
        ax.bar(i, b * 1e4, color=col, ec=INK)
        ax.text(i, b * 1e4 + 0.15, num(b * 1e4, 2), ha="center", fontsize=9.5)
    ax.axvline(5.5, color=GREY, ls="--", lw=1.2)
    ax.text(2.5, 10.5, "твёрдые: $\\beta = 3\\alpha$", ha="center", fontsize=11)
    ax.text(7.0, 10.5, "жидкости", ha="center", fontsize=11)
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels([n for n, _, _ in items], fontsize=9.5)
    ax.set_ylabel("$\\beta$, $10^{-4}$ °C$^{-1}$")
    ax.set_ylim(0, 11.5)
    ax.set_title("Коэффициент объёмного расширения")
    grid(ax)
    save(fig, "expansion-beta-compare.png")


def expansion_task_rolled_steel():
    t = np.linspace(0, 1000, 100)
    a = 1.1e-5
    l0 = 15.0 / (1 + a * 20)
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    ax.plot(t, l0 * (1 + a * t), color=INK, lw=2.2)
    ax.plot([20, 900], [15.0, l0 * (1 + a * 900)], "o", color=HOT, ms=7, zorder=3)
    ax.annotate("20 °C: 15,0 м", (20, 15.0), (150, 14.998), fontsize=10.5, va="center")
    ax.annotate("900 °C: 15,1 м", (900, l0 * (1 + a * 900)), (560, 15.16), fontsize=10.5, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
    ax.set_ylim(14.985, 15.175)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: num(v, 3)))
    ax.set_xlabel("$t$, °C")
    ax.set_ylabel("длина полосы, м")
    ax.set_title("Стальная полоса при остывании")
    grid(ax)
    save(fig, "expansion-task-rolled-steel.png")


def expansion_task_rulers():
    fig = plt.figure(figsize=(9.6, 4.0))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(-0.6, 5.6)
    ax.set_ylim(-1.4, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.5, 1.3), 3.4, 0.4, fc=METAL, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.5, 0.8), 2.4, 0.4, fc=tint(COPPER, 0.5), ec=INK, lw=1.4))
    ax.text(3.95, 1.5, "железная", va="center", fontsize=10.5)
    ax.text(2.95, 1.0, "медная", va="center", fontsize=10.5)
    ax.plot([0.5, 0.5], [0.4, 2.2], color=INK, lw=2)
    dim(ax, (0.5, 2.15), (3.9, 2.15), "$l_{0\\,\\mathrm{Fe}}$ = 34 см", off=(0, 0.3), fs=10.5)
    dim(ax, (0.5, 0.35), (2.9, 0.35), "$l_{0\\,\\mathrm{Cu}}$ = 24 см", off=(0, -0.3), fs=10.5)
    dim(ax, (2.9, 0.6), (3.9, 0.6), "", color=HOT)
    ax.text(4.05, 0.6, "$\\Delta l$ = 10 см", color=HOT, va="center", fontsize=10.5)
    ax2 = fig.add_axes([0.6, 0.16, 0.38, 0.72])
    t = np.linspace(0, 1000, 50)
    fe = 34 * (1 + 1.2e-5 * t)
    cu = 24 * (1 + 1.7e-5 * t)
    ax2.plot(t, fe, color=IRON, lw=2.4, label="железо")
    ax2.plot(t, cu, color=COPPER, lw=2.4, label="медь")
    ax2.annotate("", xy=(700, fe[35]), xytext=(700, cu[35]), arrowprops=dict(arrowstyle="<|-|>", color=HOT, lw=1.2))
    ax2.text(720, (fe[35] + cu[35]) / 2, "10 см\nпри любой $t$", color=HOT, va="center", fontsize=10)
    ax2.set_xlabel("$t$, °C")
    ax2.set_ylabel("длина, см")
    ax2.set_title("Линии параллельны")
    ax2.legend(frameon=False, loc="center left")
    grid(ax2)
    save(fig, "expansion-task-rulers.png")


def expansion_task_cork():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2))
    for ax, dn, dr, title in [(axes[0], 1.0, 1.0, "при 20 °C: диаметры равны"), (axes[1], 1.02, 1.1, "горлышко 150 °C, пробка 50 °C")]:
        ax.set_xlim(-2.3, 2.3)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axis("off")
        R =1.85 * dr  # every size of the neck grows by the same factor, outer edge included
        Rn = dn * 1.0
        Rgl = dr * 1.0
        ax.add_patch(Circle((0, 0), R, fc=LIGHT_METAL, ec=INK, lw=1.4))
        ax.add_patch(Circle((0, 0), Rgl, fc=PAPER, ec=INK, lw=1.4))
        ax.add_patch(Circle((0, 0), Rn, fc=tint(SKY, 0.5), ec=INK, lw=1.4, hatch="///"))
        ax.set_title(title, fontsize=11)
        ax.text(0, -2.4, "", ha="center")
    ax = axes[1]
    ax.annotate("зазор $\\Delta d$", (0.75, 0.75), (0.0, 1.55), ha="center", fontsize=11, color=HOT, arrowprops=dict(arrowstyle="-|>", color=HOT, lw=1.2))
    axes[0].text(0, -2.3, "горлышко и пробка (схема)", ha="center", fontsize=9, color=NOTE)
    axes[1].text(0, -2.3, "размеры зазора преувеличены", ha="center", fontsize=9, color=NOTE)
    fig.tight_layout()
    save(fig, "expansion-task-cork.png")


def expansion_task_mercury_flask():
    fig, ax = blank(7.6, 4.4, (-0.4, 9.4), (-0.6, 5.0))
    for x0, over, title in [(0.4, False, "$0$ °C, $V_0$"), (5.0, True, "$t$ = 100 °C")]:
        flask_neck(ax, x0 + 1.5, 1.4, 1.3 * (1.04 if over else 1.0), 0.12, 4.5, 4.5, MERCURY, alpha=0.9)
        ax.text(x0 + 1.5, -0.4, title, ha="center", fontsize=11)
    # Spilled mercury runs down the outer wall of the tube, below its cut at y = 4.5.
    for dx, dy in [(0.37, -0.35), (0.42, -0.9)]:
        ax.add_patch(Circle((6.5 + dx, 4.5 + dy), 0.09, fc=MERCURY, ec=INK, lw=0.8))
    arrow(ax, (7.15, 4.3), (7.15, 3.5), color=HOT, lw=1.1)
    ax.text(7.5, 4.3, "$\\Delta V$ — вылившаяся\nртуть", fontsize=10.5, va="center", color=HOT)
    ax.text(3.7, 4.55, "ртуть расширяется\nсильнее стекла", fontsize=10, ha="center", va="center")
    save(fig, "expansion-task-mercury-flask.png")


def expansion_task_hole():
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9))
    for ax, k, title in [(axes[0], 1.0, "холодный лист"), (axes[1], 1.12, "нагретый лист")]:
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.2, 2.2)
        ax.set_aspect("equal")
        ax.axis("off")
        w, h = 4.4 * k, 3.4 * k
        ax.add_patch(Rectangle((-w / 2, -h / 2), w, h, fc=LIGHT_METAL, ec=INK, lw=1.4))
        ax.add_patch(Circle((0, 0), 0.9 * k, fc=PAPER, ec=INK, lw=1.4))
        ax.set_title(title, fontsize=11)
        if k > 1:
            ax.add_patch(Circle((0, 0), 0.9, fc="none", ec=HOT, lw=1.2, ls="--"))
            ax.add_patch(Rectangle((-2.2, -1.7), 4.4, 3.4, fc="none", ec=HOT, lw=1.0, ls="--"))
    axes[1].text(0, -2.15, "штрих — прежние размеры", ha="center", fontsize=9, color=HOT)
    axes[0].text(0, -2.15, "всё подобно увеличивается в $1+\\alpha\\Delta t$ раз", ha="center", fontsize=9, color=NOTE)
    fig.tight_layout()
    save(fig, "expansion-task-hole.png")


def expansion_lab_pycnometer():
    fig, ax = blank(8.2, 5.0, (-0.4, 10.2), (-0.8, 5.6))
    for x0, over, title in [(0.5, False, "$V_1$, $t_1$ = 25 °C"), (5.2, True, "$V_2$, $t_2$ = 64 °C")]:
        flask_neck(ax, x0 + 1.4, 1.2, 1.15, 0.1, 4.8, 2.2 + (1.3 if over else 0.75), OIL, alpha=0.85)
        ax.text(x0 + 1.4, -0.5, title, ha="center", fontsize=11)
    y_mark = 2.95
    y_top = 3.5
    ax.plot([1.6, 1.6 + 0.4], [y_mark, y_mark], color=INK, lw=1.8, zorder=6)
    ax.text(2.2, y_mark, "метка 100 мл", va="center", fontsize=9.5)
    ax.plot([6.3, 8.0], [y_mark, y_mark], color=GREY, ls="--", lw=1, zorder=5)
    ax.add_patch(Rectangle((6.53, y_mark), 0.14, y_top - y_mark, fc=HOT, ec="none", zorder=5, alpha=0.6))
    dim(ax, (7.25, y_mark), (7.25, y_top), "", color=HOT)
    ax.text(7.45, (y_mark + y_top) / 2, "$h$ = 3,1 см", va="center", color=HOT, fontsize=10.5)
    ax.text(8.9, 4.4, "$\\Delta V = \\dfrac{\\pi d^2 h}{4}$", fontsize=11.5, color=HOT, ha="center")
    ax.text(6.6, 5.15, "$d$ = 1,1 см", fontsize=10.5, ha="center")
    save(fig, "expansion-lab-pycnometer.png")


def expansion_lab_result():
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    apparent = 7.55
    glass = 0.27
    ax.bar(0, apparent, color=OIL, ec=INK, width=0.55)
    ax.bar(1, glass, color=METALS["стекло"][0], ec=INK, width=0.55)
    ax.bar(2, apparent, color=OIL, ec=INK, width=0.55)
    ax.bar(2, glass, bottom=apparent, color=METALS["стекло"][0], ec=INK, width=0.55)
    ax.text(0, apparent + 0.2, "7,55", ha="center")
    ax.text(1, glass + 0.2, "0,27", ha="center")
    ax.text(2, apparent + glass + 0.2, "7,82", ha="center", fontweight="bold")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["по видимому\nизменению объёма", "расширение\nколбы $3\\alpha$", "$\\beta$ масла"], fontsize=10)
    ax.set_ylabel("$10^{-4}$ °C$^{-1}$")
    ax.set_ylim(0, 9)
    ax.set_title("Поправка на расширение стекла")
    grid(ax)
    save(fig, "expansion-lab-result.png")


def main():
    temp_equilibrium()
    temp_liquid_thermometer()
    temp_scales()
    temp_conversion_line()
    temp_ranges()
    expansion_water_density()
    expansion_lake()
    expansion_rod_needle()
    expansion_liquid_flask = expansion_flask_scheme
    expansion_liquid_flask()
    expansion_flask_level()
    expansion_gas_flask()
    expansion_bimetal()
    expansion_linear_scheme()
    expansion_linear_proportional()
    expansion_linear_metals()
    expansion_volume_scheme()
    expansion_liquids_volume()
    expansion_area_square()
    expansion_cube_terms()
    expansion_3alpha_error()
    expansion_beta_compare()
    expansion_task_rolled_steel()
    expansion_task_rulers()
    expansion_task_cork()
    expansion_task_mercury_flask()
    expansion_task_hole()
    expansion_lab_pycnometer()
    expansion_lab_result()


if __name__ == "__main__":
    main()
