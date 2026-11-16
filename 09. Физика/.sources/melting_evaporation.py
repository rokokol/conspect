"""Figures for the notes "Плавление и кристаллизация" (lessons 119, 120) and "Испарение и конденсация" (lessons 121, 122).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 melting_evaporation.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefixes melting- and evaporation-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ACCENT, ASH, BLUE, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
COLD = BLUE
GOLD = ACCENT  # the melting and crystallisation plateau, a highlighted value
ICE = SKY
WATER = BLUE
WATER_FILL = tint(SKY, 0.7)
PAPER_FILL = tint(WARM, 0.8)  # filter paper and chalk
STEAM = VIOLET  # steam, as in boiling.py


save = saver(OUT)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", **kw):
    ax.add_patch(
        FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, color=color, lw=lw, **kw)
    )


# ---------------------------------------------------------------- melting

# Melting temperatures of the textbook table shown in lesson 119, degC
MELT = [
    ("Водород", -256),
    ("Спирт", -115),
    ("Ртуть", -39),
    ("Лёд", 0),
    ("Парафин", 55),
    ("Нафталин", 80),
    ("Олово", 232),
    ("Свинец", 327),
    ("Цинк", 420),
    ("Алюминий", 660),
    ("Серебро", 962),
    ("Золото", 1065),
    ("Медь", 1087),
    ("Чугун", 1200),
    ("Сталь", 1400),
    ("Железо", 1535),
    ("Титан", 1660),
    ("Вольфрам", 3387),
]


def melting_ice_heating_cycle():
    """Qualitative t(tau) of the glass with ice, lesson 119."""
    # segments: (duration, t_start, t_end)
    segs = [
        (2.0, -10, 0, ICE, "нагревание\nльда"),
        (3.0, 0, 0, GOLD, "плавление"),
        (2.2, 0, 10, COLD, "нагревание\nводы"),
        (2.6, 10, 0, COLD, "охлаждение\nводы"),
        (3.0, 0, 0, GOLD, "кристаллизация"),
        (1.6, 0, -8, ICE, "охлаждение\nльда"),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = 0.0
    for dur, t0, t1, col, lab in segs:
        ax.plot([x, x + dur], [t0, t1], color=col, lw=3.2, solid_capstyle="round")
        xm = x + dur / 2
        if t0 == t1:
            ax.text(xm, 1.8, lab, ha="center", va="bottom", fontsize=10.5, color=INK)
        elif t1 > t0:
            ax.text(xm - 0.25, (t0 + t1) / 2 + 0.3, lab, ha="right", va="center", fontsize=10.5, color=INK)
        else:
            ax.text(xm + 0.25, (t0 + t1) / 2 + 0.3, lab, ha="left", va="center", fontsize=10.5, color=INK)
        x += dur
    ax.axhline(0, color=GREY, lw=0.9, zorder=0)
    ax.annotate(
        "стакан в морозильник",
        xy=(7.2, 10),
        xytext=(7.2, 13.6),
        ha="center",
        fontsize=10.5,
        arrowprops=dict(arrowstyle="-|>", color=INK),
    )
    ax.set_xlim(-0.4, x + 0.4)
    ax.set_ylim(-14, 16)
    ax.set_xticks([])
    ax.set_yticks([-10, 0, 10])
    ax.set_xlabel(r"время $\tau$ (условные единицы)")
    ax.set_ylabel(r"$t$, $^\circ$C")
    ax.set_title("Стакан со льдом: комната, затем морозильник")
    ax.text(3.6, -12.8, "плато при $0\\ ^\\circ$C: температура плавления равна температуре кристаллизации", fontsize=9.5, color=NOTE, ha="left")
    save(fig, "melting-ice-heating-cycle.png")


def melting_temperatures_chart():
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    names = [n for n, _ in MELT]
    vals = [v for _, v in MELT]
    cols = [ICE if v < 20 else HOT for v in vals]
    y = np.arange(len(MELT))
    ax.barh(y, vals, color=cols, height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.axvline(0, color=INK, lw=0.8)
    ax.axvspan(-300, 20, color=LIGHT, zorder=0, alpha=0.6)
    for yi, v in zip(y, vals):
        ax.text(v + (50 if v >= 0 else -50), yi, f"{v}".replace("-", "−"), va="center", ha="left" if v >= 0 else "right", fontsize=10)
    ax.set_xlim(-700, 3700)
    ax.set_xlabel(r"температура плавления, $^\circ$C")
    ax.set_title("Температуры плавления веществ")
    ax.text(3650, 1.5, "при нормальном\nатмосферном давлении", fontsize=9.5, color=NOTE, ha="right", va="center")
    save(fig, "melting-temperatures-chart.png")


def melting_temperature_zoom():
    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    sel = [("Ртуть", -39), ("Спирт", -115), ("Водород", -256)]
    ax.axhline(0, color=GREY, lw=1)
    ax.set_xlim(-300, 60)
    ax.set_ylim(-0.6, 1.4)
    ax.axvline(20, color=GOLD, lw=1.6)
    ax.text(24, 1.2, "комната\n$20\\ ^\\circ$C", fontsize=9.5, va="top")
    for name, v in sel:
        ax.plot(v, 0, "o", color=ICE, ms=9)
        ax.text(v, 0.28, f"{name}\n{v}".replace("-", "−"), ha="center", fontsize=10)
    ax.text(-39, -0.4, "ртутный термометр\nнельзя ниже этой точки", ha="center", fontsize=9.5, color=HOT)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(r"$t$, $^\circ$C")
    ax.set_title("Привычные жидкости и газы при низкой температуре — твёрдые")
    save(fig, "melting-liquids-freeze.png")


def melting_lattice_wells():
    """Molecule in the potential well of a crystal lattice site, lesson 119 (22:02)."""
    x = np.linspace(0, 6 * np.pi, 600)
    u = -np.cos(x)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    titles = [
        r"$t < t_\mathrm{пл}$: колебания в яме",
        r"$t = t_\mathrm{пл}$: амплитуда доходит до края",
        r"$t > t_\mathrm{пл}$ после плавления",
    ]
    for ax, ttl in zip(axes, titles):
        ax.plot(x, u, color=INK, lw=2)
        ax.set_title(ttl, fontsize=10.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(-1.6, 2.0)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
    # panel 1: small oscillation in the middle well
    a = axes[0]
    # u = -cos(x): the bottom of the middle well is x = 2 pi, the barrier top between wells is x = 3 pi
    xw = 2 * np.pi
    xc = 3 * np.pi
    a.plot(xw, -0.85, "o", color=HOT, ms=13, zorder=3)
    # one two-sided arrow above the ball, inside the well (the well is 2.7 wide at u = -0.2); small heads keep the shaft visible
    arrow(a, (xw - 1.15, -0.2), (xw + 1.15, -0.2), color=HOT, style="<|-|>,head_length=0.3,head_width=0.15")
    # panel 2: molecule at the rim of the well, on the curve (u = cos 0.45 = 0.9)
    a = axes[1]
    a.plot(xc - 0.45, 0.95, "o", color=HOT, ms=13, zorder=3)
    arrow(a, (xc - 0.1, 1.15), (xc + 0.9, 1.5), color=HOT)
    a.text(xc, 1.75, "выскакивает из ямы", ha="center", fontsize=9.5, color=HOT)
    # panel 3: free molecules wander over the wells
    a = axes[2]
    rng = np.random.default_rng(3)
    for k, (px, py) in enumerate([(3.0, 1.5), (7.5, 1.2), (11.5, 1.6), (15.2, 1.1)]):
        a.plot(px, py, "o", color=HOT, ms=13, zorder=3)
        arrow(a, (px, py), (px + 1.2 * (-1) ** k, py + 0.05), color=HOT, lw=1.2)
    a.text(3 * np.pi, -1.45, "решётка разрушена: молекулы свободны", ha="center", fontsize=9.5)
    save(fig, "melting-lattice-wells.png")


def melting_energy_split():
    """Kinetic vs potential energy over the three stages of the ice experiment (schematic)."""
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    stages = ["нагревание льда", "плавление", "нагревание воды"]
    ek = [2.0, 0.0, 2.0]
    ep = [0.0, 3.2, 0.0]
    x = np.arange(3)
    ax.bar(x - 0.18, ek, 0.34, color=HOT, label="кинетическая энергия молекул растёт")
    ax.bar(x + 0.18, ep, 0.34, color=COLD, label="потенциальная энергия взаимодействия растёт")
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_yticks([])
    ax.set_ylabel("прирост внутренней энергии")
    ax.set_ylim(0, 4.6)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    ax.set_title("На что идёт полученная теплота")
    ax.text(1, 3.4, "температура\nне меняется", ha="center", fontsize=9.5, color=INK, va="bottom")
    save(fig, "melting-energy-split.png")


def melting_lambda_bars():
    data = [
        ("Лёд", 332, True),
        ("Серебро", 87, True),
        ("Алюминий", 390, False),
        ("Железо", 270, False),
        ("Медь", 210, False),
        ("Олово", 59, False),
        ("Свинец", 25, False),
        ("Ртуть", 12, False),
    ]
    data.sort(key=lambda r: -r[1])
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    y = np.arange(len(data))
    ax.barh(y, [d[1] for d in data], color=[GREEN if d[2] else GREY for d in data], height=0.68)
    ax.set_yticks(y)
    ax.set_yticklabels([d[0] for d in data])
    ax.invert_yaxis()
    for yi, d in zip(y, data):
        ax.text(d[1] + 6, yi, str(d[1]), va="center", fontsize=10)
    ax.set_xlim(0, 450)
    ax.set_xlabel(r"удельная теплота плавления $\lambda$, кДж/кг")
    ax.set_title("Удельная теплота плавления")
    ax.text(445, len(data) - 0.5, "зелёным — значения из лекции,\nсерым — справочные, не из лекции", ha="right", va="bottom", fontsize=9.5, color=NOTE)
    save(fig, "melting-lambda-bars.png")


def melting_q_vs_mass():
    m = np.linspace(0, 2.0, 50)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for name, lam, col in [("лёд, $\\lambda = 332$", 332, ICE), ("серебро, $\\lambda = 87$", 87, GREY), ("свинец, $\\lambda = 25$", 25, HOT)]:
        ax.plot(m, lam * m, color=col, lw=2.4, label=name)
    ax.plot([1], [332], "o", color=ICE)
    ax.plot([1], [87], "o", color=GREY)
    ax.plot([1], [25], "o", color=HOT)
    ax.axvline(1, color=GRID, lw=1, zorder=0)
    ax.text(1.03, 500, "при $m = 1$ кг\n$Q_\\mathrm{пл} = \\lambda$ численно", fontsize=9.5)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 700)
    ax.set_xlabel("масса $m$, кг")
    ax.set_ylabel(r"$Q_\mathrm{пл}$, кДж")
    ax.set_title("Теплота плавления растёт с массой")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    # Placed between the silver and lead lines, clear of both
    ax.text(1.98, 75, "$\\lambda$ свинца — не из лекции", ha="right", fontsize=8.5, color=NOTE)
    save(fig, "melting-q-vs-mass.png")


def melting_crystallization_equal():
    """Q_melt = -Q_cryst by energy conservation; the gedanken machine of 10 and 11 J."""
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    for (x0, x1, lab, col) in [(0.4, 3.6, "расплавили:\nпоглотили 10 Дж", HOT), (6.4, 9.6, "закристаллизовали:\nвыделилось 11 Дж", COLD)]:
        ax.add_patch(FancyBboxPatch((x0, 1.4), x1 - x0, 1.4, boxstyle="round,pad=0.05", fc=PAPER, ec=col, lw=2))
        ax.text((x0 + x1) / 2, 2.1, lab, ha="center", va="center", fontsize=10.5)
    arrow(ax, (3.7, 2.4), (6.3, 2.4), color=HOT)
    arrow(ax, (6.3, 1.8), (3.7, 1.8), color=COLD)
    ax.text(5, 3.15, "цикл: $+1$ Дж за оборот\n= энергия из ничего", ha="center", fontsize=10.5, color=INK)
    ax.text(5, 0.7, r"закон сохранения энергии запрещает: $Q_\mathrm{кр}^{-} = Q_\mathrm{пл}$", ha="center", fontsize=10.5)
    save(fig, "melting-cycle-forbidden.png")


def melting_ice_to_boiling():
    """t(Q) for 4 kg of snow at -10 degC to boiling water; scaled, in kJ (problem 32.19)."""
    q1 = 2.1 * 4 * 10
    q2 = 332 * 4
    q3 = 4.2 * 4 * 100
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    xs = [0, q1, q1 + q2, q1 + q2 + q3]
    ts = [-10, 0, 0, 100]
    ax.plot(xs[:2], ts[:2], color=ICE, lw=3.2)
    ax.plot(xs[1:3], ts[1:3], color=GOLD, lw=3.2)
    ax.plot(xs[2:], ts[2:], color=COLD, lw=3.2)
    ax.plot(xs, ts, "o", color=INK, ms=5)
    ax.text(q1 + q2 / 2, 8, "$Q_2 = 1328$: плавление", ha="center", fontsize=10.5)
    ax.text(q1 + q2 + q3 / 2 - 100, 66, "$Q_3 = 1680$: нагревание воды", ha="center", fontsize=10.5, rotation=0)
    ax.text(q1 + 20, -22, "$Q_1 = 84$: нагревание льда", ha="left", fontsize=9.5, color=INK)
    ax.set_xlim(-60, 3350)
    ax.set_ylim(-40, 115)
    ax.set_yticks([-10, 0, 100])
    ax.set_xlabel(r"полученная теплота $Q$, кДж (масштаб соблюдён)")
    ax.set_ylabel(r"$t$, $^\circ$C")
    ax.set_title("Снег $-10\\ ^\\circ$C $\\rightarrow$ кипяток: масса 4 кг")
    ax.text(3300, -30, "$Q = 84 + 1328 + 1680 = 3092$ кДж", ha="right", fontsize=10.5)
    save(fig, "melting-task-snow-to-boiling.png")


def melting_ice_terms_bars():
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    parts = [("нагреть лёд на $10\\ ^\\circ$C", 21, ICE), ("расплавить лёд", 332, GOLD), ("нагреть воду на $100\\ ^\\circ$C", 420, COLD)]
    y = np.arange(3)
    ax.barh(y, [p[1] for p in parts], color=[p[2] for p in parts], height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels([p[0] for p in parts])
    ax.invert_yaxis()
    for yi, p in zip(y, parts):
        ax.text(p[1] + 6, yi, str(p[1]), va="center")
    ax.set_xlim(0, 500)
    ax.set_xlabel("кДж на 1 кг льда")
    ax.set_title("Три слагаемых, на килограмм")
    save(fig, "melting-task-snow-terms.png")


def melting_silver_fork():
    m = 0.07
    q_kr = 87 * m
    q_oh = 0.25 * m * 900
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot([0, q_kr], [962, 962], color=GOLD, lw=3.2)
    ax.plot([q_kr, q_kr + q_oh], [962, 62], color=HOT, lw=3.2)
    ax.plot([0, q_kr, q_kr + q_oh], [962, 962, 62], "o", color=INK, ms=5)
    ax.text(q_kr / 2, 1010, "кристаллизация\n$Q_\\mathrm{кр} = 6{,}09$ кДж", ha="center", fontsize=10)
    ax.text(q_kr + 0.35, 430, "остывание вилки\n$Q_\\mathrm{охл} = 15{,}75$ кДж", ha="left", fontsize=10)
    ax.set_xlim(-0.6, 24)
    ax.set_ylim(0, 1200)
    ax.set_yticks([62, 962])
    ax.set_xticks([0, q_kr, q_kr + q_oh])
    ax.set_xticklabels(["0", "6,09", "21,84"])
    ax.set_xlabel(r"отданная теплота $|Q^-|$, кДж")
    ax.set_ylabel(r"$t$, $^\circ$C")
    ax.set_title("Серебряная вилка массой 70 г")
    save(fig, "melting-task-silver-fork.png")


def melting_two_metals():
    """Problem 32.27: read from the board, cells."""
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    # On the board both liquid segments (after the plateau) are steeper than the solid ones before it.
    ax.plot([0, 2, 6, 6.6], [1, 4, 4, 5.3], color=HOT, lw=3, label="металл 1")
    ax.plot([0, 2, 7, 8.4], [1, 2, 2, 4.4], color=COLD, lw=3, label="металл 2")
    ax.annotate("", xy=(6, 4.35), xytext=(2, 4.35), arrowprops=dict(arrowstyle="<->", color=HOT))
    ax.text(4, 4.5, "$Q_{\\mathrm{пл}\\,1}$: 4 клетки", ha="center", color=HOT, fontsize=10.5)
    ax.annotate("", xy=(7, 1.65), xytext=(2, 1.65), arrowprops=dict(arrowstyle="<->", color=COLD))
    ax.text(4.5, 1.2, "$Q_{\\mathrm{пл}\\,2}$: 5 клеток", ha="center", color=COLD, fontsize=10.5)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 5.6)
    ax.set_xticks(range(0, 11))
    ax.set_yticks(range(0, 6))
    ax.grid(color=GRID, lw=0.7)
    ax.tick_params(labelbottom=False, labelleft=False)
    ax.set_xlabel("$Q$ (клетки)")
    ax.set_ylabel("$t$")
    ax.set_title("Две заготовки одной массы в печи")
    ax.legend(frameon=False, loc="lower right")
    save(fig, "melting-task-two-metals.png")


# ------------------------------------------------------------ evaporation


def evaporation_molecule_escape():
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    # liquid
    xs = np.linspace(0, 10, 200)
    surf = 3.2 + 0.08 * np.sin(xs * 3)
    ax.fill_between(xs, 0, surf, color=WATER_FILL)
    ax.plot(xs, surf, color=COLD, lw=2)
    rng = np.random.default_rng(5)
    pts = [(x, y) for x in np.linspace(0.6, 9.4, 12) for y in np.linspace(0.5, 2.9, 5)]
    for (x, y) in pts:
        ax.add_patch(Circle((x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.15, 0.15)), 0.22, color=COLD, alpha=0.85))
    # fast molecule leaves
    ax.add_patch(Circle((3.0, 3.5), 0.24, color=HOT, zorder=4))
    arrow(ax, (3.0, 3.75), (3.6, 5.9), color=HOT, lw=2.2)
    ax.text(3.75, 5.95, "быстрая: $E_k > A$, улетает в пар", fontsize=10.5, color=HOT, va="center")
    # slow molecule returns
    ax.add_patch(Circle((7.0, 3.55), 0.24, color=GREEN, zorder=4))
    arrow(ax, (7.0, 3.85), (7.1, 4.6), color=GREEN, lw=2.2)
    arrow(ax, (7.5, 4.55), (7.55, 3.9), color=GREEN, lw=2.2, connectionstyle="arc3,rad=-0.5")
    ax.text(7.7, 5.0, "медленная: $E_k < A$,\nпритяжение возвращает", fontsize=10.5, color=GREEN, va="center")
    ax.text(5, 0.06, "жидкость", ha="center", fontsize=10.5, color=COLD)
    ax.set_title("Молекулы у поверхности жидкости")
    save(fig, "evaporation-molecule-escape.png")


def evaporation_energy_distribution():
    """Schematic Maxwell-type distribution of molecular kinetic energies (not from the lecture)."""
    e = np.linspace(0.001, 10, 500)

    def f(e, t):
        return 2 * np.sqrt(e / np.pi) * t ** -1.5 * np.exp(-e / t)

    a = 4.6
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    for t, col, lab in [(1.0, COLD, "низкая температура"), (1.6, HOT, "высокая температура")]:
        y = f(e, t)
        ax.plot(e, y, color=col, lw=2.4, label=lab)
        m = e >= a
        ax.fill_between(e[m], 0, y[m], color=col, alpha=0.35)
    ax.axvline(a, color=INK, lw=1.4, ls="--")
    ax.text(a + 0.1, 0.62, "работа выхода $A$", fontsize=10.5, rotation=90, va="top")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 0.68)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("кинетическая энергия молекулы $E_k$")
    ax.set_ylabel("доля молекул")
    ax.set_title("Быстрых молекул больше при высокой температуре")
    ax.legend(frameon=False, fontsize=10)
    ax.text(9.9, 0.34, "закрашено: молекулы\nс $E_k > A$", ha="right", fontsize=9.5, color=INK)
    ax.text(9.9, 0.6, "схема, не из лекции", ha="right", fontsize=8.5, color=NOTE)
    save(fig, "evaporation-energy-distribution.png")


def evaporation_cooling():
    """The class analogy as a plain diagram: the fast leave, the mean drops."""
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6), sharey=True)
    e = np.linspace(0.001, 10, 400)
    y = 2 * np.sqrt(e / np.pi) * np.exp(-e / 1.4) / 1.4 ** 1.5
    a = 5.0
    axes[0].plot(e, y, color=INK, lw=2)
    axes[0].fill_between(e, 0, y, where=e >= a, color=HOT, alpha=0.4)
    mean0 = 1.5 * 1.4
    axes[0].axvline(mean0, color=COLD, lw=1.6, ls="--")
    axes[0].set_title("До: средняя энергия $\\bar E_k$", fontsize=10.5)
    keep = e < a
    axes[1].plot(e[keep], y[keep], color=INK, lw=2)
    mean1 = np.sum(e[keep] * y[keep]) / np.sum(y[keep])
    axes[1].axvline(mean1, color=COLD, lw=1.6, ls="--")
    axes[1].set_title("После: быстрые улетели, $\\bar E_k$ меньше", fontsize=10.5)
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 10)
        ax.axvline(a, color=GREY, lw=1, ls=":")
        ax.set_xlabel("$E_k$")
    axes[0].text(a + 0.2, 0.3, "$E_k > A$\nулетают", color=HOT, fontsize=9.5, transform=axes[0].get_xaxis_transform())
    axes[0].text(mean0 + 0.15, 0.7, "среднее", color=COLD, fontsize=9.5, transform=axes[0].get_xaxis_transform())
    axes[1].text(mean1 + 0.15, 0.7, "среднее", color=COLD, fontsize=9.5, transform=axes[1].get_xaxis_transform())
    fig.text(0.99, 0.01, "схема, не из лекции", fontsize=8, color=NOTE, ha="right")
    fig.suptitle("Испарение охлаждает жидкость", fontsize=12.5, y=1.04)
    save(fig, "evaporation-cooling-mechanism.png")


def evaporation_psychrometer():
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    for x, h, lab, col in [(2.6, 5.4, "сухой\n$20\\ ^\\circ$C", HOT), (6.6, 4.9, "влажный\nменьше $18\\ ^\\circ$C", COLD)]:
        ax.add_patch(Rectangle((x - 0.25, 1.7), 0.5, 4.8, fc=PAPER, ec=INK, lw=1.6))
        ax.add_patch(Rectangle((x - 0.13, 1.7), 0.26, h - 1.7, fc=col, ec="none"))
        ax.add_patch(Circle((x, 1.35), 0.55, fc=col, ec=INK, lw=1.6, zorder=2))
        ax.text(x, 7.2, lab, ha="center", fontsize=11)
    # The cloth is wrapped around the wet bulb: a ring under the bulb, with a wick to the water vessel
    ax.add_patch(Circle((6.6, 1.35), 0.68, fc=PAPER_FILL, ec=INK, lw=1.2, zorder=1))
    ax.plot([7.24, 8.45, 8.45], [1.58, 1.85, 0.5], color=INK, lw=4.6, solid_capstyle="round", solid_joinstyle="round", zorder=0)
    ax.plot([7.24, 8.45, 8.45], [1.58, 1.85, 0.5], color=PAPER_FILL, lw=3, solid_capstyle="round", solid_joinstyle="round", zorder=0.5)
    ax.add_patch(Rectangle((8.2, 0.15), 1.4, 1.2, fc=WATER_FILL, ec=INK, lw=1.2, zorder=0.2))
    ax.text(9.05, 0.45, "вода", ha="center", va="center", fontsize=9.5)
    ax.annotate("ткань", xy=(6.1, 0.9), xytext=(4.1, 0.35), ha="left", va="center", fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_title("Психрометр: два одинаковых термометра", fontsize=12.5)
    save(fig, "evaporation-psychrometer.png")


def evaporation_wind_return():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
    rng = np.random.default_rng(8)
    for ax, wind in zip(axes, (False, True)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.fill_between([0, 10], 0, 1.4, color=WATER_FILL)
        ax.plot([0, 10], [1.4, 1.4], color=COLD, lw=2)
        for (x, y) in [(2.0, 2.8), (4.0, 3.6), (5.6, 2.4)]:
            ax.add_patch(Circle((x, y), 0.2, color=COLD, zorder=3))
        for _ in range(16):
            ax.add_patch(Circle((rng.uniform(0.5, 9.5), rng.uniform(2.0, 5.5)), 0.13, color=GREY, zorder=2))
        if wind:
            ax.set_title("С ветром: пар уносится, назад не возвращается", fontsize=11)
            for yy in (2.5, 3.6, 4.7):
                arrow(ax, (0.3, yy), (9.7, yy), color=GREEN, lw=1.4)
        else:
            ax.set_title("Без ветра: часть молекул возвращается", fontsize=11)
            arrow(ax, (4.0, 3.4), (3.5, 1.7), color=HOT, lw=2, connectionstyle="arc3,rad=0.4")
            arrow(ax, (2.0, 2.6), (2.5, 1.7), color=HOT, lw=2, connectionstyle="arc3,rad=-0.4")
        ax.text(9.9, 0.55, "вода", ha="right", color=COLD, fontsize=10)
    axes[0].text(0.1, 0.3, "синие — молекулы воды, серые — воздуха", fontsize=9, color=NOTE)
    save(fig, "evaporation-wind-return.png")


def evaporation_area():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8))
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.6, 1.0), 1.6, 1.6, fc=WATER_FILL, ec=COLD, lw=2))
    ax.add_patch(Rectangle((3.6, 0.7), 5.8, 2.2, fc=WATER_FILL, ec=COLD, lw=2))
    ax.text(1.4, 3.2, "капля", ha="center", fontsize=10.5)
    ax.text(6.5, 3.2, "размазали", ha="center", fontsize=10.5)
    ax.text(5, -0.6, "вид сверху: воды поровну, площадь разная,\nбыстрее высыхает та, где площадь больше", ha="center", fontsize=9.5, color=NOTE)
    ax.set_title("Одна и та же вода на доске", fontsize=11)
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.6, 1.0), 2.2, 1.6, fc=PAPER_FILL, ec=INK, lw=1.6))
    ax.add_patch(Rectangle((4.0, 1.0), 1.1, 1.6, fc=PAPER_FILL, ec=INK, lw=1.6))
    ax.add_patch(Rectangle((5.6, 1.0), 1.1, 1.6, fc=PAPER_FILL, ec=INK, lw=1.6))
    ax.add_patch(Rectangle((5.1, 1.0), 0.5, 1.6, fc=PAPER, ec="none"))
    for x in (5.1, 5.6):
        ax.plot([x, x], [1.0, 2.6], color=HOT, lw=3)
    arrow(ax, (3.0, 1.8), (3.8, 1.8), color=INK)
    ax.text(5.35, 3.1, "две новые поверхности", ha="center", fontsize=10, color=HOT)
    ax.text(5, 0.3, "кусок мела: разломили — площадь выросла", ha="center", fontsize=9.5, color=NOTE)
    ax.set_title("Распыление увеличивает площадь", fontsize=11)
    save(fig, "evaporation-area-split.png")


def evaporation_factors_scheme():
    """Four qualitative panels; no numbers, only the direction of the dependence."""
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.2))
    x = np.linspace(0, 1, 50)
    panels = [
        ("температура жидкости", "$t$", 0.15 + 1.6 * x ** 2, HOT),
        ("площадь поверхности", "$S$", 1.7 * x, GREEN),
        # The curve starts above zero: evaporation goes on in still air
        ("обдув воздухом", "скорость ветра", 0.5 + 1.2 * (1 - np.exp(-3 * x)) / (1 - np.exp(-3)), COLD),
    ]
    for ax, (ttl, xl, y, col) in zip(axes[:3], panels):
        ax.plot(x, y, color=col, lw=2.6)
        ax.set_title(ttl, fontsize=10.5)
        ax.set_xlabel(xl)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(0, 2)
    axes[0].set_ylabel("скорость испарения")
    ax = axes[3]
    for i, (n, h, c) in enumerate([("вода", 0.9, COLD), ("спирт", 1.7, GOLD)]):
        ax.bar(i, h, color=c, width=0.6)
        ax.text(i, h + 0.05, n, ha="center", fontsize=10)
    ax.set_ylim(0, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("род жидкости", fontsize=10.5)
    ax.set_xlabel("разная работа выхода")
    fig.suptitle("От чего зависит скорость испарения (качественно)", fontsize=12.5, y=1.07)
    save(fig, "evaporation-factors-scheme.png")


def evaporation_paper_experiment():
    """Four filter-paper sheets at three moments; schematic radii, order of drying as in the lesson."""
    labels = ["вода", "вода + лампа", "вода + ветер", "спирт"]
    cols = [COLD, HOT, GREEN, GOLD]
    radii = {
        "вода": [1.0, 0.85, 0.7],
        "вода + лампа": [1.0, 0.45, 0.0],
        "вода + ветер": [1.0, 0.7, 0.4],
        "спирт": [1.0, 0.35, 0.0],
    }
    fig, axes = plt.subplots(4, 3, figsize=(6.6, 6.6))
    for i, lab in enumerate(labels):
        for j in range(3):
            ax = axes[i, j]
            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.add_patch(Rectangle((-1.2, -1.2), 2.4, 2.4, fc=LIGHT, ec=GREY, lw=1))
            r = radii[lab][j]
            if r > 0:
                ax.add_patch(Circle((0, 0), r * 0.9, fc=cols[i], alpha=0.45, ec=cols[i]))
            if j == 0:
                ax.text(-1.35, 0, lab, ha="right", va="center", fontsize=10)
            if i == 0:
                ax.set_title(["сразу", "позже", "ещё позже"][j], fontsize=10)
    fig.suptitle("Опыт с фильтровальной бумагой (схема)", fontsize=12.5)
    fig.subplots_adjust(left=0.24)
    save(fig, "evaporation-paper-experiment.png")


def evaporation_estimate_steps():
    """Step diagram of the estimate of lesson 122."""
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    boxes = [
        (0.2, 3.5, 3.3, 1.5, "измеряем", "$\\Delta m$ (весы), $\\Delta t$ (секундомер),\n$D = 13$ см", GOLD),
        (3.9, 3.5, 3.3, 1.5, "площадь поверхности", "$S = \\dfrac{\\pi D^2}{4} = 133\\ \\mathrm{см}^2$", COLD),
        (7.6, 3.5, 3.2, 1.5, "число молекул", "$N = \\dfrac{\\Delta m}{m_0}$,  $m_0 = 3 \\cdot 10^{-23}$ г", GREEN),
        (0.2, 0.5, 5.0, 1.8, "плотность потока", "$j = \\dfrac{N}{S\\,\\Delta t} = \\dfrac{\\Delta m}{m_0\\,S\\,\\Delta t}$", HOT),
        (5.7, 0.5, 5.1, 1.8, "рабочая формула", "$j = 2{,}5 \\cdot 10^{20}\\,\\dfrac{1}{\\mathrm{г \\cdot см^2}}\\,\\dfrac{\\Delta m}{\\Delta t}$", INK),
    ]
    for (x, y, w, h, ttl, body, col) in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06", fc=PAPER, ec=col, lw=2.2))
        ax.text(x + w / 2, y + h - 0.32, ttl, ha="center", va="center", fontsize=10.5, color=col, weight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.2, body, ha="center", va="center", fontsize=11)
    arrow(ax, (3.55, 4.25), (3.85, 4.25))
    arrow(ax, (7.25, 4.25), (7.55, 4.25))
    arrow(ax, (9.2, 3.4), (3.2, 2.45), connectionstyle="arc3,rad=0.15")
    arrow(ax, (5.25, 1.4), (5.65, 1.4))
    ax.text(5.5, 5.25, "Как оценить число испаряющихся молекул", ha="center", fontsize=12.5)
    save(fig, "evaporation-estimate-steps.png")


DATA = [
    ("обычные\nусловия", 0.41, 840, 63.90, 63.49, 0, COLD),
    ("подогрев\nлампой", 3.98, 830, 72.64, 68.66, 90, HOT),
    ("обдув\nветром", 1.35, 800, 75.73, 74.38, 200, GREEN),
]
K = 2.5e20


def evaporation_measured_loss():
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    for name, dm, dt, m0, m1, t0, col in DATA:
        ax.plot([0, dt], [0, dm], "-o", color=col, lw=2.4, label=name.replace("\n", " "))
        ax.text(dt + 8, dm, num(dm, 2) + " г", va="center", color=col, fontsize=10)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 4.6)
    ax.set_xlabel(r"время испарения $\Delta t$, с")
    ax.set_ylabel(r"испарилась масса $\Delta m$, г")
    ax.set_title("Опыт: сколько воды испарилось с тарелки")
    ax.legend(frameon=False, loc="upper left")
    ax.text(990, 2.4, "прямые проведены между началом\nи концом опыта", ha="right", fontsize=8.5, color=NOTE)
    save(fig, "evaporation-measured-loss.png")


def evaporation_j_bars():
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    vals = [K * dm / dt for (_, dm, dt, *_r) in DATA]
    names = [d[0].replace("\n", " ") for d in DATA]
    cols = [d[-1] for d in DATA]
    ax.bar(names, vals, color=cols, width=0.55)
    ax.set_yscale("log")
    ax.set_ylim(1e16, 1e19)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.18, num(v / 10 ** np.floor(np.log10(v)), 1) + r"$\cdot 10^{" + f"{int(np.floor(np.log10(v)))}" + "}$", ha="center", fontsize=11)
    ax.set_ylabel(r"$j$, молекул / (см$^2\cdot$с)")
    ax.set_title("Плотность потока испаряющихся молекул")
    ax.text(2.45, 6e18, "ось логарифмическая", ha="right", fontsize=8.5, color=NOTE)
    ax.text(1, 3.0e17, "в 10 раз", ha="center", fontsize=9.5, color=INK)
    ax.text(2, 1.1e17, "в 3,5 раза", ha="center", fontsize=9.5, color=INK)
    save(fig, "evaporation-j-bars.png")


def evaporation_counting_scale():
    sec_year = 86400 * 365
    vals = [1.2e17 / sec_year / 1e9, 1.2e18 / sec_year / 1e9, 13.7]
    names = ["счёт молекул\nпри $j = 1{,}2 \\cdot 10^{17}$", "счёт молекул\nпри $j = 1{,}2 \\cdot 10^{18}$", "возраст\nВселенной"]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar(names, vals, color=[COLD, HOT, GREY], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.8, num(v, 1) + " млрд лет", ha="center", fontsize=10.5)
    ax.set_ylabel("млрд лет")
    ax.set_ylim(0, 44)
    ax.set_title("Пересчитать молекулы с 1 см$^2$ за одну секунду")
    ax.text(2.4, 41, "по одной молекуле в секунду", ha="right", fontsize=9.5, color=NOTE)
    save(fig, "evaporation-counting-scale.png")


def evaporation_condensation_examples():
    fig, ax = plt.subplots(figsize=(9.6, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    cards = [
        ("роса", "пар у земли\nохладился\nк утру", COLD),
        ("туман", "капельки\nпорядка\nмикрометра", GREY),
        ("облака", "пар поднялся\nна километры", ICE),
        ("запотевшее\nзеркало", "выдох на\nхолодную\nповерхность", GREEN),
        ("очки\nзимой", "с мороза в\nтёплое\nпомещение", HOT),
    ]
    w = 1.8
    for i, (t, b, c) in enumerate(cards):
        x = 0.1 + i * 1.95
        ax.add_patch(FancyBboxPatch((x, 0.2), w, 3.1, boxstyle="round,pad=0.04", fc=PAPER, ec=c, lw=2))
        ax.text(x + w / 2, 2.6, t, ha="center", va="center", fontsize=11, weight="bold", color=INK if c in (GREY, ICE) else c)  # a pale outline colour is no text colour
        ax.text(x + w / 2, 1.2, b, ha="center", va="center", fontsize=9.5)
    ax.set_title("Конденсация водяного пара: примеры из лекции", fontsize=12)
    save(fig, "evaporation-condensation-examples.png")


if __name__ == "__main__":
    melting_ice_heating_cycle()
    melting_temperatures_chart()
    melting_temperature_zoom()
    melting_lattice_wells()
    melting_energy_split()
    melting_lambda_bars()
    melting_q_vs_mass()
    melting_crystallization_equal()
    melting_ice_to_boiling()
    melting_ice_terms_bars()
    melting_silver_fork()
    melting_two_metals()
    evaporation_molecule_escape()
    evaporation_energy_distribution()
    evaporation_cooling()
    evaporation_psychrometer()
    evaporation_wind_return()
    evaporation_area()
    evaporation_factors_scheme()
    evaporation_paper_experiment()
    evaporation_estimate_steps()
    evaporation_measured_loss()
    evaporation_j_bars()
    evaporation_counting_scale()
    evaporation_condensation_examples()
