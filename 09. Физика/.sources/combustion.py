"""Figures for the note "Теплота сгорания. КПД нагревателя" (section f10, lessons 114-116, problems of 117, 118).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 combustion.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefix combustion-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, WARM, keep_dots, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
WATER = BLUE
WATER_FILL = tint(SKY, 0.7)
GOLD = WARM
SOLID = COPPER  # solid fuel: wood, coal
LIQUID = WARM  # liquid fuel: oil, petrol, spirit
GAS = BLUE  # gaseous fuel
LOSS = tint(INK, 0.8)  # heat lost to the surroundings
ALUMINIUM = METAL
COPPER_CUP = COPPER

# Table of specific heats of combustion, MJ/kg (school textbook table shown in lesson 114)
FUELS = [
    ("Порох", 4, "s"),
    ("Дрова сухие", 10, "s"),
    ("Бурый уголь", 12, "s"),
    ("Солома", 14, "s"),
    ("Торф", 15, "s"),
    ("Тротил", 15, "s"),
    ("Каменный уголь", 27, "s"),
    ("Спирт", 27, "l"),
    ("Антрацит", 30, "s"),
    ("Древесный уголь", 34, "s"),
    ("Дизельное топливо", 42, "l"),
    ("Природный газ", 44, "g"),
    ("Нефть", 44, "l"),
    ("Бензин", 46, "l"),
    ("Керосин", 46, "l"),
    ("Пропан", 46, "g"),
    ("Ацетилен", 50, "g"),
    ("Водород", 120, "g"),
]
PHASE_COLOR = {"s": SOLID, "l": LIQUID, "g": GAS}
PHASE_NAME = {"s": "твёрдое", "l": "жидкое", "g": "газообразное"}


save = saver(OUT)


def axes_grid(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def phase_legend(ax, loc="lower right"):
    handles = [Rectangle((0, 0), 1, 1, color=PHASE_COLOR[k]) for k in "slg"]
    ax.legend(handles, [PHASE_NAME[k] for k in "slg"], loc=loc, frameon=False)


# 1. bar chart of q for all fuels
def fuel_bars():
    data = sorted(FUELS, key=lambda f: f[1])
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    names = [f[0] for f in data]
    vals = [f[1] for f in data]
    ax.barh(names, vals, color=[PHASE_COLOR[f[2]] for f in data], height=0.72)
    for i, v in enumerate(vals):
        ax.text(v + 1.2, i, str(v), va="center", fontsize=10, color=INK)
    ax.set_xlim(0, 132)
    ax.set_xlabel(r"$q$, МДж/кг")
    ax.set_title("Удельная теплота сгорания топлива")
    phase_legend(ax)
    save(fig, "combustion-fuel-q-bars.png")


# 2. Q(m) lines: slope is q
def q_of_m():
    fig, ax = axes_grid(7.4, 4.8)
    m = np.linspace(0, 5, 50)
    picks = [
        ("Водород", 120, GAS),
        ("Бензин", 46, LIQUID),
        ("Каменный уголь", 27, INK),
        ("Дрова сухие", 10, SOLID),
        ("Порох", 4, HOT),
    ]
    for name, q, color in picks:
        ax.plot(m, q * m, color=color, lw=2.2)
        ax.text(
            5.05,
            q * 5,
            f"{name}, {q}",
            va="center",
            fontsize=10,
            color=color,
        )
    ax.set_xlim(0, 6.6)
    ax.set_ylim(0, 640)
    ax.set_xlabel(r"масса сгоревшего топлива $m$, кг")
    ax.set_ylabel(r"выделившаяся теплота $Q_{\mathrm{сг}}$, МДж")
    ax.set_title(r"$Q_{\mathrm{сг}} = qm$: наклон прямой равен $q$")
    ax.axvline(1, color=GREY, ls="--", lw=1)
    ax.text(1.05, 590, "при $m = 1$ кг ордината\nчисленно равна $q$", fontsize=9.5, color=NOTE)
    save(fig, "combustion-q-vs-mass.png")


# 3. equal-energy masses (derived, not from the lecture)
def equal_energy():
    picks = [
        ("Водород", 120),
        ("Бензин", 46),
        ("Дизельное топливо", 42),
        ("Древесный уголь", 34),
        ("Каменный уголь", 27),
        ("Торф", 15),
        ("Дрова сухие", 10),
        ("Порох", 4),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    names = [p[0] for p in picks][::-1]
    masses = [46 / p[1] for p in picks][::-1]
    cols = [PHASE_COLOR[dict((f[0], f[2]) for f in FUELS)[n]] for n in names]
    ax.barh(names, masses, color=cols, height=0.7)
    for i, v in enumerate(masses):
        ax.text(v + 0.2, i, num(v, 2), va="center", fontsize=10)
    ax.axvline(1, color=GREY, ls="--", lw=1)
    ax.set_xlim(0, 14)
    ax.set_xlabel("масса топлива, кг")
    ax.set_title("Сколько килограммов топлива дают $46$ МДж, как $1$ кг бензина")
    phase_legend(ax, "center right")
    save(fig, "combustion-equal-energy-mass.png")


# helper for Sankey-like flow: one source bar splits into stacked parts
def flow(ax, x0, x1, width, total, parts, colors, labels, unit, gap_frac=0.06):
    """Left bar of height total at x0; right stacked bars at x1 separated by gaps."""
    scale = 1.0
    gap = total * gap_frac
    ax.add_patch(Rectangle((x0 - width, 0), width, total, color=INK))
    y_left = 0.0
    y_right = 0.0
    n = len(parts)
    total_right = sum(parts) + gap * (n - 1)
    shift = (total - total_right) / 2
    y_right = shift
    for p, c, lab in zip(parts, colors, labels):
        xs = np.linspace(x0, x1, 40)
        t = (1 - np.cos(np.pi * (xs - x0) / (x1 - x0))) / 2
        lo = y_left + (y_right - y_left) * t
        hi = y_left + p + (y_right + p - y_left - p) * t
        ax.fill_between(xs, lo, hi, color=c, alpha=0.55, lw=0)
        ax.add_patch(Rectangle((x1, y_right), width, p, color=c))
        ax.text(
            x1 + width + 0.03 * (x1 - x0),
            y_right + p / 2,
            f"{lab}\n{num(p, 1)}" + f" {unit}",
            va="center",
            fontsize=10.5,
            color=INK,
        )
        y_left += p
        y_right += p + gap


# 4. lab: energy flow of the gas burner
def lab_flow():
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    total = 644.0
    useful = 265.4
    lost = total - useful
    flow(
        ax,
        0.0,
        1.0,
        0.06,
        total,
        [useful, lost],
        [WATER, LOSS],
        ["нагрев воды $Q_{\\mathrm{пол}}$", "потери: воздух, кастрюля"],
        "кДж",
    )
    ax.text(-0.08, total / 2, "выделилось при\nсгорании\n$Q_{\\mathrm{сг}} = 644$ кДж", ha="right", va="center", fontsize=10.5)
    ax.text(0.5, total * 1.09, r"$\eta = \dfrac{265}{644} \approx 0{,}41$", ha="center", fontsize=13, color=INK)
    ax.set_xlim(-0.5, 1.75)
    ax.set_ylim(-20, total * 1.22)
    ax.axis("off")
    ax.set_title("Куда ушла теплота газовой горелки в лабораторной работе")
    save(fig, "combustion-lab-energy-flow.png")


# 5. kettle problem 30.19: useful part splits into kettle and water; fuel needed
def kettle_flow():
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    dt = 85.0
    q_kettle = 0.92 * 0.4 * dt
    q_water = 4.2 * 3 * dt
    useful = q_kettle + q_water
    total = useful / 0.4
    lost = total - useful
    flow(
        ax,
        0.0,
        1.0,
        0.06,
        total,
        [q_water, q_kettle, lost],
        [WATER, ALUMINIUM, LOSS],
        [
            "вода в чайнике",
            "алюминиевый чайник",
            "потери, $60\\ \\%$",
        ],
        "кДж",
        gap_frac=0.05,
    )
    ax.text(
        -0.08,
        total / 2,
        f"$Q_{{\\mathrm{{сг}}}} = Q_{{\\mathrm{{пол}}}} / \\eta$\n$\\approx {total:.0f}$ кДж",
        ha="right",
        va="center",
        fontsize=10.5,
    )
    ax.set_xlim(-0.6, 1.9)
    ax.set_ylim(-60, total * 1.08)
    ax.axis("off")
    ax.set_title("Задача о чайнике: $\\eta = 0{,}4$, полезная теплота идёт на воду и на чайник")
    save(fig, "combustion-kettle-flow.png")


# 6. spirit lamp problem 30.21
def lamp_flow():
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    dt = 80.0
    q_water = 4.2 * 0.4 * dt
    q_cup = 0.4 * 0.1 * dt
    total = 27 * 13.2
    lost = total - q_water - q_cup
    flow(
        ax,
        0.0,
        1.0,
        0.06,
        total,
        [q_water, q_cup, lost],
        [WATER, COPPER_CUP, LOSS],
        ["вода", "медная чашка", "потери, $61\\ \\%$"],
        "кДж",
        gap_frac=0.05,
    )
    ax.text(
        -0.08,
        total / 2,
        "$Q_{\\mathrm{сг}} = qm_{\\mathrm{с}}$\n$= 27 \\cdot 13{,}2$ г\n$\\approx 356$ кДж",
        ha="right",
        va="center",
        fontsize=10.5,
    )
    ax.set_xlim(-0.6, 1.9)
    ax.set_ylim(-20, total * 1.08)
    ax.axis("off")
    ax.set_title(r"Спиртовка: $\eta = \dfrac{137{,}6}{356{,}4} \approx 0{,}39$")
    save(fig, "combustion-lamp-flow.png")


# 7. eta of heaters and engines from the lessons
def eta_bars():
    data = [
        ("Газовая горелка (лаб. работа)", 41, GAS),
        ("Спиртовка (30.21)", 39, LIQUID),
        ("Горелка под чайником (30.19, дано)", 40, GAS),
        ("Проточный нагреватель (4.59)", 53, GREEN),
        ("Двигатель автомобиля (5.40)", 35, HOT),
        ("Двигатель трактора (5.39)", 29, HOT),
    ]
    data.sort(key=lambda d: d[1])
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.barh([d[0] for d in data], [d[1] for d in data], color=[d[2] for d in data], height=0.66)
    for lbl in ax.get_yticklabels():
        keep_dots(lbl)
    for i, d in enumerate(data):
        ax.text(d[1] + 1, i, f"{d[1]} %", va="center", fontsize=10.5)
    ax.set_xlim(0, 100)
    ax.axvline(100, color=GREY, lw=1)
    ax.set_xlabel(r"$\eta$, %")
    ax.set_title("КПД нагревателей и двигателей из задач темы")
    ax.legend(
        [Rectangle((0, 0), 1, 1, color=c) for c in (GAS, LIQUID, GREEN, HOT)],
        ["газовый", "спиртовой", "проточный", "тепловой двигатель"],
        loc="lower right",
        frameon=False,
        fontsize=9,
    )
    save(fig, "combustion-eta-bars.png")


# 8. engines: tractor and car, work vs heat
def engines_flow():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))
    cases = [
        ("Трактор (5.39)", 756.0, 216.0, "МДж"),
        ("Автомобиль (5.40)", 457.2, 158.4, "МДж"),
    ]
    for ax, (title, q, a, unit) in zip(axes, cases):
        ax.bar([0], [a], color=GREEN, width=0.5, label="полезная работа $A$")
        ax.bar([0], [q - a], bottom=[a], color=LOSS, width=0.5, label="потери")
        ax.text(0, a / 2, f"$A$ = {num(a, None)}", ha="center", va="center", color=PAPER, fontsize=11)
        ax.text(0, a + (q - a) / 2, f"{q - a:.0f}", ha="center", va="center", fontsize=11)
        ax.text(0, q * 1.02, f"$Q_{{\\mathrm{{сг}}}}$ = {num(q, None)} {unit}", ha="center", fontsize=11)
        ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(0, 860)
        ax.set_xticks([])
        eta_txt = num(a / q, 2, math=True)
        keep_dots(ax.set_title(f"{title}\n$\\eta = {eta_txt}$"))
    axes[0].set_ylabel("энергия, МДж")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.5, -0.05))
    save(fig, "combustion-engines-flow.png")


# 9. mixture of alcohol and gasoline, task 5.38
def mixture():
    fig, ax = axes_grid(7.2, 4.4)
    w = np.linspace(0, 1, 50)
    q = 46 * (1 - w) + 27 * w
    ax.plot(w * 100, q, color=INK, lw=2.4)
    w0 = 6 / 19
    ax.plot([0, w0 * 100], [40, 40], color=HOT, ls="--", lw=1.4)
    ax.plot([w0 * 100, w0 * 100], [26, 40], color=HOT, ls="--", lw=1.4)
    ax.plot([w0 * 100], [40], "o", color=HOT, ms=8)
    ax.text(w0 * 100 + 2, 41.2, r"$q = 40$ МДж/кг: спирта $\approx 32\ \%$ по массе", color=HOT, fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_ylim(25, 47.5)
    ax.yaxis.set_major_formatter(lambda v, _: num(v, None))
    ax.set_xlabel("доля спирта в смеси по массе, %")
    ax.set_ylabel(r"$q$ смеси, МДж/кг")
    ax.set_title("Удельная теплота сгорания смеси бензина и спирта")
    ax.text(1, 46.4, "чистый бензин, 46", fontsize=9.5, color=NOTE)
    ax.text(99, 25.5, "чистый спирт, 27", fontsize=9.5, color=NOTE, ha="right")
    save(fig, "combustion-mixture-q.png")


# 10. sugar problem: height compared with Hoverla
def sugar():
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.grid(True, axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    names = ["100 г сахара,\nвся энергия в\nподъём", "гора Говерла"]
    vals = [2150, 2061]
    ax.bar(names, vals, color=[GOLD, METAL], width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 30, f"{v} м", ha="center", fontsize=11)
    ax.set_ylim(0, 2500)
    ax.set_ylabel("высота, м")
    ax.set_title("Подъём человека $80$ кг\nза счёт энергии $100$ г сахара")
    save(fig, "combustion-sugar-height.png")


# 11. scheme of the lab
def lab_scheme():
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    # scales
    ax.add_patch(Rectangle((0.6, 0.4), 2.6, 0.5, color=METAL))
    ax.add_patch(Rectangle((1.5, 0.55), 1.0, 0.22, color=INK))
    ax.text(2.0, 0.66, "762,9", color=PAPER, fontsize=7.5, ha="center", va="center")
    # gas cylinder
    ax.add_patch(Rectangle((1.2, 0.9), 1.6, 2.2, color=LIGHT, ec=INK, lw=1.5))
    ax.text(2.0, 1.9, "газовый\nбаллон", ha="center", va="center", fontsize=9.5)
    ax.text(2.0, -0.15, "весы: $m_1$ до опыта,\n$m_2$ после опыта", ha="center", va="top", fontsize=9.5)
    # burner
    ax.add_patch(Rectangle((1.85, 3.1), 0.3, 0.7, color=INK))
    ax.add_patch(Rectangle((1.4, 3.8), 1.2, 0.18, color=INK))
    # flame
    for dx, h in [(-0.35, 0.55), (0, 0.8), (0.35, 0.55)]:
        ax.add_patch(Polygon([[2.0 + dx - 0.16, 3.98], [2.0 + dx + 0.16, 3.98], [2.0 + dx, 3.98 + h]], color=WARM, alpha=0.85))
    # pot with water
    ax.add_patch(Rectangle((1.1, 4.85), 1.8, 1.05, fc=WATER_FILL, ec=INK, lw=2))
    ax.add_patch(Rectangle((1.1, 4.85), 1.8, 0.85, color=WATER, alpha=0.5))
    ax.text(2.0, 5.28, "вода\n$800$ г", ha="center", va="center", fontsize=9.5)
    # thermometer
    ax.plot([2.55, 2.55], [4.9, 6.2], color=HOT, lw=3)
    ax.text(2.75, 6.1, "$t$", fontsize=11)
    # formula block
    ax.text(
        4.0,
        4.9,
        "1. $t_1 = 21\\ ^\\circ$C до нагрева\n"
        "2. нагрели до кипения, $t_2 = 100\\ ^\\circ$C\n"
        "3. выключили горелку сразу после закипания",
        fontsize=10.5,
        va="top",
    )
    ax.text(
        4.0,
        3.0,
        r"$Q_{\mathrm{пол}} = c_{\mathrm{в}} m_{\mathrm{в}}(t_2 - t_1)$",
        fontsize=12,
        va="center",
    )
    ax.text(
        4.0,
        2.3,
        r"$Q_{\mathrm{сг}} = q\,(m_1 - m_2)$",
        fontsize=12,
        va="center",
    )
    ax.text(
        4.0,
        1.3,
        r"$\eta = \dfrac{c_{\mathrm{в}} m_{\mathrm{в}}(t_2 - t_1)}{q\,(m_1 - m_2)}$",
        fontsize=14,
        va="center",
        bbox=dict(boxstyle="square,pad=0.4", fc=PAPER, ec=INK, lw=1.3),
    )
    save(fig, "combustion-lab-scheme.png")


# 12. dependence of the fuel mass on eta and dt (kettle problem, working formula)
def fuel_vs_eta():
    fig, ax = axes_grid(7.2, 4.5)
    eta = np.linspace(0.1, 1.0, 100)
    c_sum = 0.92 * 0.4 + 4.2 * 3  # kJ/degC
    q = 44.0  # kJ/g
    for dt, color in [(85, INK), (60, WATER), (40, GREEN)]:
        m = c_sum * dt / (eta * q)
        ax.plot(eta, m, color=color, lw=2.2, label=rf"$\Delta t = {dt}\ ^\circ$C")
    ax.plot([0.4], [c_sum * 85 / (0.4 * q)], "o", color=HOT, ms=8)
    ax.annotate("$\\eta = 0{,}4$: $63$ г", (0.4, c_sum * 85 / (0.4 * q)), (0.5, 95), fontsize=10.5, color=HOT, arrowprops=dict(arrowstyle="->", color=HOT))
    ax.set_xlabel(r"КПД нагревателя $\eta$")
    ax.set_ylabel("масса газа $m_{\\mathrm{г}}$, г")
    ax.set_title("Чем выше КПД, тем меньше топлива", pad=10)
    ax.xaxis.set_major_formatter(lambda v, _: num(v, None))
    ax.set_ylim(0, 160)
    ax.legend(frameon=False)
    save(fig, "combustion-fuel-vs-eta.png")


if __name__ == "__main__":
    fuel_bars()
    q_of_m()
    equal_energy()
    lab_flow()
    kettle_flow()
    lamp_flow()
    eta_bars()
    engines_flow()
    mixture()
    sugar()
    lab_scheme()
    fuel_vs_eta()
