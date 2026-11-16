"""Figures for the note "Кипение. Теплота парообразования" (section f10, lessons 123-126).

Run: nix shell nixpkgs#python3Packages.matplotlib nixpkgs#python3Packages.scipy -c python3 boiling.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefix boiling-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle
from scipy.interpolate import PchipInterpolator

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
WATER = BLUE  # water: a line, a bar, a label
WATER_FILL = tint(SKY, 0.7)  # the body of water in a vessel
VESSEL = tint(ASH, 0.6)  # the glass of a flask or a pot
ICE = SKY
GOLD = WARM
STEAM = VIOLET  # steam, as in melting_evaporation.py
SOLID = METAL  # a substance that is solid at room temperature (here all three are metals)
FLAME = WARM
AIR = METAL

# Reference data: lessons 123-126 (school textbook tables shown in the lessons)
SATURATED = [(20, 17.5), (50, 92.5), (80, 355), (100, 760)]  # t, degC -> p_sat, mm Hg
ALTITUDE = [(0, 100), (1000, 97), (2061, 93), (8848, 72)]  # m -> t_boil, degC
PRESSURE_TABLE = [(1, 100), (2, 120), (5, 151), (20, 211), (100, 310), (226, 374)]  # atm -> degC
LATENT = [  # MJ/kg
    ("Вода", 2.3),
    ("Аммиак", 1.4),
    ("Спирт", 0.9),
    ("Эфир", 0.4),
    ("Ртуть", 0.3),
    ("Жидкий воздух", 0.2),
]
BOILING_POINTS = [  # degC, state at room temperature
    ("Водород", -253, "g"),
    ("Азот", -196, "g"),
    ("Воздух", -192, "g"),
    ("Кислород", -183, "g"),
    ("Эфир", 35, "l"),
    ("Спирт", 78, "l"),
    ("Вода, молоко", 100, "l"),
    ("Глицерин", 290, "l"),
    ("Масло", 310, "l"),
    ("Ртуть", 357, "l"),
    ("Свинец", 1740, "s"),
    ("Медь", 2567, "s"),
    ("Железо", 2750, "s"),
]


save = saver(OUT)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", ms=12, **kw):
    ax.add_patch(
        FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, **kw)
    )


# 1. Kettle heating curve with observations (lesson 123)
def lesson_curve():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    tau = np.array([0, 10, 15])
    t = np.array([21, 100, 100])
    ax.plot(tau, t, color=WATER, lw=3, solid_capstyle="round")
    ax.axhline(100, color=GREY, lw=1, ls="--")
    marks = [(1, 33, 35), (2, 60, 60), (3, 80, 80), (4, 88, 88), (5, 97, 97)]
    for n, temp, _ in marks:
        x = (temp - 21) / 79 * 10
        ax.plot(x, temp, "o", ms=17, color=PAPER, mec=INK, mew=1.4, zorder=4)
        ax.text(x, temp, str(n), ha="center", va="center", fontsize=11, zorder=5, color=INK)
    ax.text(12.5, 103.5, "кипение: $t = 100\\ ^\\circ$C = const", ha="center", color=HOT, fontsize=12)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 112)
    ax.set_xticks([])
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("время $\\tau$, произвольные единицы")
    ax.set_ylabel("температура $t$, $^\\circ$C")
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    items = [
        "1  конвекционные потоки, 30-40 °C",
        "2  пузырьки воздуха у дна, ≈ 60 °C",
        "3  вода мутнеет, ≈ 80 °C",
        "4  шум от схлопывания пузырьков\n    (кавитация), 80-90 °C",
        "5  пузыри пара доходят до поверхности,\n    шум сменяется бурлением",
    ]
    ax.text(6.0, 52, "\n".join(items), va="top", ha="left", fontsize=10.5, color=INK, linespacing=1.55)
    ax.set_title("Нагревание воды в чайнике")
    save(fig, "boiling-lesson-heating-curve.png")


# 2. Bubble at the bottom: pressure balance at three temperatures (lesson 124)
def bubble_stages():
    states = [
        ("$t = 20\\ ^\\circ$C", 0.32, 742.5, 17.5, "почти весь воздух"),
        # r = 0.32 * (V2/V1)^(1/3) with V2/V1 = (742.5/405) * (353/293) = 2.2, so r = 0.42
        ("$t = 80\\ ^\\circ$C", 0.42, 405, 355, "пара уже почти половина"),
        ("$t = 100\\ ^\\circ$C", 0.85, 0, 760, "пар вытеснил воздух"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.6))
    for ax, (title, r, p_air, p_v, note) in zip(axes, states):
        ax.set_xlim(-1.3, 1.9)
        ax.set_ylim(-1.2, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=13)
        ax.add_patch(Rectangle((-1.3, -1.1), 2.0, 0.0, fc="none"))
        ax.plot([-1.25, 0.65], [-1.05, -1.05], color=INK, lw=2)
        ax.add_patch(Circle((-0.3, -1.05 + r), r, fc=WATER_FILL, ec=WATER, lw=2))
        cy = -1.05 + r
        for ang in np.linspace(0, 2 * np.pi, 7)[:-1] + 0.3:
            if ang > np.pi * 1.05 and ang < np.pi * 1.95 and r < 0.4:
                continue
            p1 = (-0.3 + (r + 0.30) * np.cos(ang), cy + (r + 0.30) * np.sin(ang))
            p2 = (-0.3 + (r + 0.04) * np.cos(ang), cy + (r + 0.04) * np.sin(ang))
            if p1[1] < -1.0:
                continue
            arrow(ax, p1, p2, color=INK, lw=1.4, ms=9)
        ax.text(-0.3, 1.3, "$p_{\\mathrm{атм}}$ давит снаружи", ha="center", fontsize=10.5, color=INK)
        # stacked bar of partial pressures inside the bubble
        x0, w = 1.0, 0.45
        h_air = 2.0 * p_air / 760
        h_v = 2.0 * p_v / 760
        ax.add_patch(Rectangle((x0, -1.0), w, h_air, fc=AIR, ec=INK, lw=1))
        ax.add_patch(Rectangle((x0, -1.0 + h_air), w, h_v, fc=WATER, ec=INK, lw=1))
        ax.plot([x0 - 0.1, x0 + w + 0.1], [1.0, 1.0], color=INK, lw=1, ls="--")
        ax.text(x0 + w / 2, 1.08, "760", ha="center", fontsize=10)
        if p_air > 60:
            ax.text(x0 + w / 2, -1.0 + h_air / 2, num(p_air, None), ha="center", va="center", fontsize=9.5, color=PAPER)
        if p_v > 60:
            ax.text(x0 + w / 2, -1.0 + h_air + h_v / 2, num(p_v, None), ha="center", va="center", fontsize=9.5, color=PAPER)
        else:
            ax.text(x0 + w + 0.06, -1.0 + h_air + h_v + 0.05, num(p_v, None), ha="left", va="bottom", fontsize=9.5, color=WATER)
        ax.text(-0.3, -1.2, note, ha="center", va="top", fontsize=10, color=NOTE)
    fig.legend(
        handles=[
            Rectangle((0, 0), 1, 1, fc=AIR, ec=INK, label="$p_{\\mathrm{возд}}$"),
            Rectangle((0, 0), 1, 1, fc=WATER, ec=INK, label="$p_{\\mathrm{н.п.}}$, насыщенный пар"),
        ],
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.08),
    )
    fig.text(0.5, 0.0, "Столбцы: давление внутри пузырька, мм рт. ст.; $p_{\\mathrm{возд}} = p_{\\mathrm{атм}} - p_{\\mathrm{н.п.}}$ (рисунок схематичный)", ha="center", fontsize=10, color=NOTE)
    save(fig, "boiling-bubble-stages.png")


# 3. Saturated vapour pressure of water (lesson 124)
def saturated_pressure():
    fig, ax = plt.subplots(figsize=(8.5, 5))
    T = np.linspace(15, 105, 200)
    P = 10 ** (8.07131 - 1730.63 / (233.426 + T))  # Antoine equation, mm Hg, 1-100 degC
    ax.plot(T, P, color=WATER, lw=2.6, label="давление насыщенного пара воды")
    for t, p in SATURATED:
        ax.plot(t, p, "o", color=INK, ms=8, zorder=5)
        ax.annotate(num(p, None), (t, p), textcoords="offset points", xytext=(-8, 8), ha="right", fontsize=11)
    ax.axhline(760, color=HOT, lw=1.6, ls="--")
    ax.text(16, 780, "нормальное атмосферное давление, 760 мм рт. ст.", color=HOT, fontsize=10.5)
    ax.plot([100, 100], [0, 760], color=HOT, lw=1.2, ls=":")
    ax.annotate(
        "$p_{\\mathrm{н.п.}} = p_{\\mathrm{атм}}$:\nвода кипит",
        (100, 760),
        xytext=(78, 560),
        fontsize=11,
        color=HOT,
        arrowprops=dict(arrowstyle="->", color=HOT),
    )
    ax.set_xlim(15, 108)
    ax.set_ylim(0, 860)
    ax.set_xticks([20, 50, 80, 100])
    ax.set_xlabel("температура $t$, $^\\circ$C")
    ax.set_ylabel("$p_{\\mathrm{н.п.}}$, мм рт. ст.")
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Давление насыщенного пара воды")
    save(fig, "boiling-saturated-pressure.png")


# 4. Boiling point versus pressure (lesson 124)
def boiling_vs_pressure():
    pts = [(17.5 / 760, 20)] + PRESSURE_TABLE
    x = np.log10([p for p, _ in pts])
    y = [t for _, t in pts]
    f = PchipInterpolator(x, y)
    xs = np.linspace(x[0], x[-1], 300)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.axhspan(374, 420, color=LIGHT, zorder=0)
    ax.text(0.03, 397, "выше 374 °C граница между жидкостью и паром исчезает", fontsize=10, color=INK, va="center")
    ax.plot(10**xs, f(xs), color=WATER, lw=2.6)
    for p, t in PRESSURE_TABLE[:-1]:
        ax.plot(p, t, "o", color=INK, ms=8, zorder=5)
        ax.annotate(f"{t}", (p, t), textcoords="offset points", xytext=(8, -14), fontsize=11)
    ax.plot(226, 374, "*", color=HOT, ms=18, zorder=6)
    ax.annotate("критическая точка\n226 атм, 374 °C", (226, 374), xytext=(0.9, 300), fontsize=10.5, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT))
    ax.plot(17.5 / 760, 20, "s", color=GREEN, ms=8, zorder=5)
    ax.annotate("колба с насосом:\n≈ 20 мм рт. ст., 20 °C", (17.5 / 760, 20), xytext=(0.03, 110), fontsize=10.5, color=GREEN, arrowprops=dict(arrowstyle="->", color=GREEN))
    ax.annotate("скороварка\n2 атм, 120 °C", (2, 120), xytext=(0.5, 200), fontsize=10.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xscale("log")
    ax.set_xlim(0.02, 400)
    ax.set_ylim(0, 420)
    ax.set_xticks([1, 2, 5, 20, 100, 226])
    ax.set_xticklabels(["1", "2", "5", "20", "100", "226"])
    ax.minorticks_off()
    ax.set_xlabel("давление $p$, атм (шкала логарифмическая)")
    ax.set_ylabel("температура кипения $t_{\\mathrm{кип}}$, $^\\circ$C")
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Температура кипения воды и давление")
    save(fig, "boiling-vs-pressure.png")


# 5. Boiling point versus altitude (lesson 124)
def boiling_vs_altitude():
    h = np.array([a for a, _ in ALTITUDE]) / 1000
    t = np.array([b for _, b in ALTITUDE])
    f = PchipInterpolator(h, t)
    xs = np.linspace(0, h[-1], 200)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, f(xs), color=WATER, lw=2.6)
    names = ["уровень моря", "", "Говерла", "Эверест"]
    for (a, b), name in zip(ALTITUDE, names):
        ax.plot(a / 1000, b, "o", color=INK, ms=8, zorder=5)
        label = f"{name}\n{a} м, {b} °C" if name else f"{a} м, {b} °C"
        ax.annotate(label, (a / 1000, b), textcoords="offset points", xytext=(10, 6), fontsize=10.5)
    ax.set_xlim(-0.3, 10.5)
    ax.set_ylim(60, 106)
    ax.set_xlabel("высота над уровнем моря, км")
    ax.set_ylabel("температура кипения воды, $^\\circ$C")
    ax.grid(color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Температура кипения воды в горах")
    save(fig, "boiling-vs-altitude.png")


# 6. Specific heat of vaporization of substances (lesson 123)
def latent_bars():
    names = [n for n, _ in LATENT][::-1]
    vals = [v for _, v in LATENT][::-1]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    colors = [WATER if n == "Вода" else METAL for n in names]
    ax.barh(names, vals, color=colors, height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + 0.03, i, num(v, None), va="center", fontsize=11, bbox=dict(fc=PAPER, ec="none", pad=1))
    ax.axvline(0.33, color=HOT, ls="--", lw=1.4)
    ax.text(0.62, 0.5, "удельная теплота плавления\nльда, 0,33 МДж/кг", color=HOT, fontsize=10, va="center")
    ax.set_xlim(0, 2.7)
    ax.set_xlabel("удельная теплота парообразования $L$, МДж/кг")
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Удельная теплота парообразования")
    save(fig, "boiling-latent-heat-bars.png")


# 7. Boiling points of substances (lesson 123)
def boiling_points():
    fig, ax = plt.subplots(figsize=(9, 6))
    names = [n for n, _, _ in BOILING_POINTS][::-1]
    vals = [v for _, v, _ in BOILING_POINTS][::-1]
    state = [s for _, _, s in BOILING_POINTS][::-1]
    col = {"g": WATER, "l": GOLD, "s": SOLID}
    ax.barh(names, vals, color=[col[s] for s in state], height=0.66)
    for i, v in enumerate(vals):
        if v >= 0:
            ax.text(v + 40, i, f"{v}", va="center", fontsize=10.5)
        else:
            ax.text(v - 40, i, f"−{-v}", va="center", ha="right", fontsize=10.5)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlim(-520, 3050)
    ax.set_xlabel("температура кипения при нормальном давлении, $^\\circ$C")
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.legend(
        handles=[
            Rectangle((0, 0), 1, 1, fc=WATER, label="газ при комнатной температуре"),
            Rectangle((0, 0), 1, 1, fc=GOLD, label="жидкость при комнатной температуре"),
            Rectangle((0, 0), 1, 1, fc=SOLID, label="твёрдое при комнатной температуре"),
        ],
        loc="upper right",
        frameon=False,
    )
    ax.set_title("Температуры кипения веществ")
    save(fig, "boiling-points-substances.png")


# 8. Boiling versus evaporation (lesson 123)
def boiling_vs_evaporation():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    rng = np.random.default_rng(3)
    for ax in axes:
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 4.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.plot([0.5, 0.5, 3.5, 3.5], [3.6, 0.5, 0.5, 3.6], color=INK, lw=2.5)
        ax.add_patch(Rectangle((0.5, 0.5), 3.0, 2.4, fc=WATER_FILL, ec="none"))
        ax.plot([0.5, 3.5], [2.9, 2.9], color=WATER, lw=2)
    ax = axes[0]
    ax.set_title("Испарение: с поверхности, при любой температуре", fontsize=11.5)
    for x in [1.0, 1.7, 2.4, 3.0]:
        arrow(ax, (x, 2.95), (x + rng.uniform(-0.15, 0.15), 3.9), color=WATER, lw=1.6)
    ax.text(2.0, 1.6, "жидкость", ha="center", color=WATER, fontsize=11)
    ax = axes[1]
    ax.set_title("Кипение: во всём объёме, при $t_{\\mathrm{кип}}$", fontsize=11.5)
    for x, y, r in [(1.0, 0.75, 0.14), (1.6, 1.2, 0.2), (2.4, 0.8, 0.16), (2.9, 1.5, 0.26), (1.3, 2.0, 0.3), (2.2, 2.2, 0.36)]:
        ax.add_patch(Circle((x, y), r, fc=PAPER, ec=WATER, lw=1.6))
        arrow(ax, (x, y + r + 0.03), (x, y + r + 0.28), color=WATER, lw=1.2, ms=8)
    for x in [1.0, 2.0, 3.0]:
        arrow(ax, (x, 2.95), (x, 3.7), color=WATER, lw=1.6)
    ax.text(3.0, 0.8, "пузыри\nпара", ha="center", color=WATER, fontsize=10)
    save(fig, "boiling-vs-evaporation.png")


# 9. Pressure cooker (lesson 124)
def pressure_cooker():
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((2.5, 1.4), 3.6, 2.4, fc=VESSEL, ec=INK, lw=2.5))
    ax.add_patch(Rectangle((2.5, 1.4), 3.6, 1.35, fc=WATER_FILL, ec="none"))
    ax.plot([2.5, 6.1], [2.75, 2.75], color=WATER, lw=2)
    ax.add_patch(Polygon([[2.3, 3.8], [3.0, 4.35], [5.6, 4.35], [6.3, 3.8]], fc=LIGHT, ec=INK, lw=2.5))
    # safety valve: cone with weight
    ax.add_patch(Polygon([[4.05, 4.35], [4.55, 4.35], [4.45, 4.85], [4.15, 4.85]], fc=METAL, ec=INK, lw=1.5))
    ax.add_patch(Rectangle((4.05, 4.85), 0.5, 0.35, fc=INK, ec=INK))
    for (x, y) in [(3.0, 3.35), (3.6, 3.1), (4.4, 3.5), (5.0, 3.2), (5.5, 3.55), (4.9, 3.6)]:
        ax.plot(x, y, ".", color=WATER, ms=6)
    for (x, y, r) in [(3.2, 1.7, 0.13), (4.1, 2.0, 0.18), (5.0, 1.75, 0.15), (4.6, 2.3, 0.2)]:
        ax.add_patch(Circle((x, y), r, fc=PAPER, ec=WATER, lw=1.5))
    # burner
    ax.add_patch(Polygon([[4.0, 0.55], [4.6, 0.55], [4.3, 1.25]], fc=FLAME, ec=FLAME, alpha=0.85))
    ax.plot([3.7, 4.9], [0.35, 0.35], color=INK, lw=3)
    # valve steam
    for dx in [-0.35, 0, 0.35]:
        arrow(ax, (4.3 + dx * 0.3, 5.25), (4.3 + dx * 1.6, 5.85), color=GREY, lw=1.4, ms=10, ls="--")
    ax.text(4.3, 6.15, "пар выходит, когда давление\nподнимает клапан", ha="center", fontsize=10, color=NOTE, va="center")
    ax.annotate("груз", (4.55, 5.05), xytext=(5.4, 5.4), fontsize=11, arrowprops=dict(arrowstyle="-", color=INK))
    ax.annotate("предохранительный\nклапан", (4.5, 4.6), xytext=(6.4, 4.8), fontsize=11, arrowprops=dict(arrowstyle="-", color=INK))
    ax.annotate("$p = 2$ атм", (5.3, 3.5), xytext=(6.9, 3.7), fontsize=13, arrowprops=dict(arrowstyle="-", color=INK))
    ax.annotate("$t = 120\\ ^\\circ$C", (5.5, 2.0), xytext=(6.9, 2.0), fontsize=13, arrowprops=dict(arrowstyle="-", color=INK))
    ax.text(4.3, 0.05, "скороварка (автоклав)", ha="center", fontsize=12)
    save(fig, "boiling-pressure-cooker.png")


# 10. Boiling at reduced pressure: three experiments (lesson 124)
def low_pressure_experiments():
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.8))
    for ax in axes:
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 5)
        ax.set_aspect("equal")
        ax.axis("off")
    # (a) inverted flask cooled by cold water
    ax = axes[0]
    ax.set_ylim(-0.9, 5)
    ax.set_title("Колба вверх дном, поливаем холодной водой", fontsize=10.5)
    # inverted flask: neck and stopper below, water in the lower part
    ax.add_patch(Rectangle((1.75, 1.15), 0.5, 0.9, fc=WATER_FILL, ec=INK, lw=2))
    water = Circle((2, 3.0), 1.1, fc=WATER_FILL, ec="none")
    ax.add_patch(water)
    water.set_clip_path(Rectangle((0, 0), 4, 2.75, transform=ax.transData))
    ax.add_patch(Circle((2, 3.0), 1.1, fc="none", ec=INK, lw=2))
    ax.add_patch(Polygon([[1.65, 0.75], [2.35, 0.75], [2.25, 1.15], [1.75, 1.15]], fc=METAL, ec=INK, lw=1.5))
    for x, y, r in [(1.5, 2.2, 0.1), (2.2, 2.35, 0.13), (1.95, 1.7, 0.09)]:
        ax.add_patch(Circle((x, y), r, fc=PAPER, ec=WATER, lw=1.3))
    ax.text(2, 3.35, "пар", ha="center", color=WATER, fontsize=10)
    arrow(ax, (3.3, 4.75), (2.75, 3.95), color=WATER, lw=1.6)
    ax.text(3.35, 4.6, "холодная\nвода", fontsize=9.5, color=WATER, va="top")
    ax.text(2, 0.5, "пар конденсируется на холодной стенке,\nдавление над водой падает", ha="center", fontsize=9.5, color=INK, va="top")
    # (b) vacuum pump
    ax = axes[1]
    ax.set_title("Колба, откачиваем воздух насосом", fontsize=10.5)
    ax.add_patch(Rectangle((1.25, 2.85), 0.5, 1.0, fc=VESSEL, ec=INK, lw=2))
    flask = Circle((1.5, 1.9), 1.05, fc=WATER_FILL, ec="none")
    ax.add_patch(flask)
    flask.set_clip_path(Rectangle((0, 0), 4, 1.95, transform=ax.transData))
    ax.add_patch(Circle((1.5, 1.9), 1.05, fc="none", ec=INK, lw=2))
    ax.add_patch(Polygon([[1.15, 3.85], [1.85, 3.85], [1.75, 4.2], [1.25, 4.2]], fc=METAL, ec=INK, lw=1.5))
    ax.plot([1.5, 1.5, 3.1], [4.2, 4.5, 4.5], color=INK, lw=2)
    ax.add_patch(Rectangle((3.1, 4.2), 0.8, 0.6, fc=WATER, ec=INK, lw=1.5))
    ax.text(3.5, 4.5, "насос", color=PAPER, ha="center", va="center", fontsize=9.5)
    # Bubbles form at the surface: the text says the water boils from the top
    for x, y in [(1.0, 1.85), (1.4, 1.88), (1.8, 1.84), (2.15, 1.87)]:
        ax.add_patch(Circle((x, y), 0.07, fc=PAPER, ec=WATER, lw=1.2))
    ax.text(1.5, 0.55, "вода кипит с поверхности\nпри комнатной температуре,\n$p \\approx 20$ мм рт. ст.", ha="center", fontsize=9.5, va="top")
    # (c) syringe
    ax = axes[2]
    ax.set_title("Шприц с водой, оттягиваем поршень", fontsize=10.5)
    ax.add_patch(Rectangle((0.6, 2.0), 2.4, 0.9, fc=VESSEL, ec=INK, lw=2))
    ax.add_patch(Rectangle((0.6, 2.0), 1.1, 0.9, fc=WATER_FILL, ec="none"))
    ax.add_patch(Rectangle((1.9, 2.0), 1.1, 0.9, fc=PAPER, ec="none", hatch="..", alpha=0.6))
    ax.add_patch(Rectangle((3.0, 2.05), 0.15, 0.8, fc=INK))
    ax.plot([3.15, 3.9], [2.45, 2.45], color=INK, lw=3)
    ax.add_patch(Rectangle((0.3, 2.35), 0.3, 0.2, fc=VESSEL, ec=INK, lw=1.5))
    arrow(ax, (3.5, 3.1), (3.95, 3.1), color=HOT, lw=2)
    ax.text(3.0, 3.3, "тянем", color=HOT, fontsize=10, ha="center")
    ax.text(2.4, 1.6, "пар", ha="center", fontsize=10, color=WATER, va="top")
    ax.text(1.15, 1.6, "вода", ha="center", fontsize=10, color=WATER, va="top")
    ax.text(1.8, 0.8, "воздуха в шприце нет:\nвода кипит при комнатной\nтемпературе", ha="center", fontsize=9.5, va="top")
    save(fig, "boiling-low-pressure-experiments.png")


# 11. Problem 6.38: from ice at -20 to steam at 100, energies to scale
def task_ice_to_steam():
    c_ice, c_w, lam, L, m = 2.1, 4.2, 330, 2300, 3
    q1 = c_ice * m * 20
    q2 = lam * m
    q3 = c_w * m * 100
    q4 = L * m
    qs = np.cumsum([0, q1, q2, q3, q4])
    ts = [-20, 0, 0, 100, 100]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10.5, 6.6), sharex=True, gridspec_kw={"height_ratios": [3.2, 1]})
    cols = [ICE, GREEN, WATER, STEAM]
    names = ["нагрев льда", "плавление", "нагрев воды", "парообразование"]
    for i in range(4):
        ax.plot(qs[i : i + 2], ts[i : i + 2], color=cols[i], lw=4, solid_capstyle="butt")
    ax.axhline(100, color=GREY, lw=1, ls="--")
    ax.axhline(0, color=GREY, lw=1, ls="--")
    for q, t in zip(qs[1:4], [0, 0, 100]):
        ax.plot([q, q], [-30, t], color=GREY, lw=0.9, ls=":")
    ax.plot([qs[4], qs[4]], [-30, 100], color=GREY, lw=0.9, ls=":")
    ax.set_ylim(-30, 118)
    ax.set_ylabel("температура $t$, $^\\circ$C")
    ax.set_yticks([-20, 0, 20, 40, 60, 80, 100])
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("Три килограмма льда: от $-20\\ ^\\circ$C до пара при $100\\ ^\\circ$C, масштаб по оси $Q$ сохранён")
    ax.text(qs[1] + 120, 6, "плавление,\n$t = 0\\ ^\\circ$C", color=GREEN, fontsize=10, va="bottom")
    ax.text(qs[4] - 700, 106, "парообразование, $t = 100\\ ^\\circ$C", color=STEAM, fontsize=10.5, ha="center")
    ax.text(qs[2] + 1150, 38, "нагрев воды\n(наклон меньше:\n$c_{\\mathrm{в}} = 2 c_{\\mathrm{л}}$)", color=WATER, fontsize=10)
    ax.text(qs[0] + 60, -13, "нагрев льда", color=INK, fontsize=10)
    ax.text(qs[4], -27, f"{qs[4]:.0f}", ha="center", fontsize=10, color=INK)
    for q in qs[1:4]:
        ax.text(q, -27, f"{q:.0f}", ha="center", fontsize=10, color=INK)
    for i, (a, b) in enumerate(zip(qs[:-1], qs[1:])):
        ax2.barh(0, b - a, left=a, color=cols[i], height=0.6, ec=PAPER)
        val = f"{b - a:.0f}"
        if b - a > 800:
            ax2.text((a + b) / 2, 0, f"{names[i]}\n{val} кДж", ha="center", va="center", fontsize=9.5, color=PAPER)
        else:
            ax2.annotate(f"{names[i]}, {val} кДж", ((a + b) / 2, 0.3), xytext=((a + b) / 2 - 300 + 500 * i, 0.95), fontsize=9.5, ha="center", arrowprops=dict(arrowstyle="-", color=GREY))
    ax2.set_ylim(-0.5, 1.25)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.set_xlabel("полученная теплота $Q$, кДж")
    ax2.set_xlim(-200, qs[4] + 300)
    save(fig, "boiling-task-ice-to-steam.png")


def split_bar(name, title, parts, unit, xlabel, note=None):
    fig, ax = plt.subplots(figsize=(10, 2.7))
    left = 0
    total = sum(v for _, v, _ in parts)
    for label, v, col in parts:
        ax.barh(0, v, left=left, color=col, height=0.55, ec=PAPER)
        share = 100 * v / total
        amount = f"{v:,.0f}".replace(",", " ")
        txt = f"{label}\n{amount} {unit} ({share:.0f} %)"
        if share > 20:
            ax.text(left + v / 2, 0, txt, ha="center", va="center", fontsize=10, color=PAPER)
        else:
            ax.annotate(txt, (left + v / 2, 0.28), xytext=(left + v / 2, 0.75), ha="center", fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
        left += v
    ax.set_xlim(0, total * 1.02)
    ax.set_ylim(-0.5, 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    if note:
        fig.text(0.5, -0.02, note, ha="center", fontsize=10, color=NOTE)
    save(fig, name)


def condensate_panels(name, water_t0, theta, m_w, m_s, title):
    c = 4.2
    L = 2300
    q_w = c * m_w * (theta - water_t0)
    q_cond = L * m_s
    q_cool = c * m_s * (100 - theta)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, gridspec_kw={"width_ratios": [q_w, q_cond + q_cool]})
    a.plot([0, q_w], [water_t0, theta], color=WATER, lw=3.5)
    a.set_title("Вода в калориметре получает теплоту", fontsize=11.5)
    a.text(q_w / 2, (water_t0 + theta) / 2 + 6, f"$Q_{{\\mathrm{{в}}}} = {num(q_w, 0)}$ кДж", ha="center", color=WATER, fontsize=11)
    b.plot([0, q_cond], [100, 100], color=STEAM, lw=3.5)
    b.plot([q_cond, q_cond + q_cool], [100, theta], color=WATER, lw=3.5)
    b.invert_xaxis()
    b.set_title("Пар отдаёт теплоту: конденсация, затем остывание", fontsize=11.5)
    b.text(q_cond / 2, 104, f"конденсация\n$Lm_{{\\mathrm{{п}}}}$ = {num(q_cond, 1)} кДж", ha="center", color=STEAM, fontsize=10.5)
    b.annotate(
        f"остывание воды\n{num(theta, None)}…100 °C: {num(q_cool, 1)} кДж",
        (q_cond + q_cool * 0.35, 100 - 0.35 * (100 - theta)),
        xytext=(q_cond * 0.5, 66),
        ha="center",
        color=WATER,
        fontsize=10.5,
        arrowprops=dict(arrowstyle="->", color=WATER),
    )
    for ax in (a, b):
        ax.axhline(theta, color=GREY, ls="--", lw=1)
        ax.grid(color=GRID)
        ax.set_axisbelow(True)
    a.set_ylabel("температура $t$, $^\\circ$C")
    a.text(q_w * 0.02, theta + 2.5, f"$\\theta = {theta:g}\\ ^\\circ$C", color=INK, fontsize=10.5)
    a.set_xlabel("полученная теплота, кДж")
    b.set_xlabel("отданная теплота, кДж")
    a.set_ylim(water_t0 - 8, 118)
    keep_dots(fig.suptitle(title, fontsize=12.5, y=1.0))
    save(fig, name)


def main():
    lesson_curve()
    bubble_stages()
    saturated_pressure()
    boiling_vs_pressure()
    boiling_vs_altitude()
    latent_bars()
    boiling_points()
    boiling_vs_evaporation()
    pressure_cooker()
    low_pressure_experiments()
    task_ice_to_steam()
    split_bar(
        "boiling-task-kettle-boil-off.png",
        "Чайник: куда пошла теплота, полученная водой",
        [("нагрев воды", 672, WATER), ("парообразование", 230, STEAM)],
        "кДж",
        "полученная теплота $Q$, кДж",
    )
    split_bar(
        "boiling-task-petrol-energy.png",
        "Бензин: куда идёт теплота сгорания $0{,}8$ кг",
        [("нагрев воды", 16800, WATER), ("парообразование", 4320, STEAM), ("потери", 14080, METAL)],
        "кДж",
        "теплота, кДж",
    )
    split_bar(
        "boiling-task-desalination.png",
        "Опреснение $1$ т воды: теплота на нагрев и на выпаривание",
        [("нагрев", 336, WATER), ("выпаривание", 2300, STEAM)],
        "МДж",
        "теплота, МДж",
    )
    condensate_panels("boiling-task-steam-calorimeter.png", 20, 40, 1.0, 0.0329, "Задача 6.43: $33$ г пара нагревают $1$ кг воды с $20$ до $40\\ ^\\circ$C")
    condensate_panels("boiling-task-initial-temperature.png", 36.5, 60, 1.0, 0.040, "Задача II-6: $40$ г пара, вода нагрелась до $60\\ ^\\circ$C")


if __name__ == "__main__":
    main()
