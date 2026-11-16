"""Figures for the note "Внутренняя энергия. Теплопередача" (section f10, lessons 105-107 and 111).

Run: nix shell nixpkgs#python3Packages.matplotlib nixpkgs#python3Packages.scipy -c python3 heat_transfer.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefixes internal- and transfer-).
Palette and drawing helpers come from temperature_expansion.py in the same folder.
Reference numbers that are not from the lectures are marked in the note next to each figure.
"""
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle
import matplotlib.pyplot as plt
from theme import ACCENT, BLUE, COPPER, METAL, PAPER, RED, SKY, VIOLET, WARM, num, tint
from matplotlib.colors import LinearSegmentedColormap
from scipy.special import erfc

from temperature_expansion import (
    COLD,
    GOLD,
    GREEN,
    GREY,
    GRID,
    HOT,
    INK,
    LIGHT,
    WATER,
    arrow,
    blank,
    dim,
    grid,
    save,
)

BRASS = COPPER  # the copper wire and rod
IRON = tint(INK, 0.2)  # dark steel
SILVER = METAL  # a bright metal rail
FLAME = WARM
SOOT = INK  # soot, the black surface
WARM_FILL = tint(RED, 0.8)  # a warm body
COOL_FILL = tint(SKY, 0.75)  # a cold body, and cold water
TABLE = tint(COPPER, 0.5)  # a wooden table
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT_COLD = LinearSegmentedColormap.from_list("hot_cold", [RED, LIGHT, BLUE])  # a temperature gradient from hot to cold
WAX = COPPER  # a drop of wax that holds a coin
COIN = WARM  # a coin, gold in colour
STOPPER = COPPER  # a cork or rubber stopper
WATER_FILL = tint(SKY, 0.85)  # the body of water in a vessel
LEAD = VIOLET  # lead, as in heat_capacity.py

K = "$E_\\mathrm{к}$"
P = "$E_\\mathrm{п}$"


def flame(ax, x, y, s=1.0):
    """Teardrop flame with its base at (x, y)."""
    outer = np.array([[0, 0], [-0.32, 0.25], [-0.2, 0.7], [0, 1.15], [0.2, 0.7], [0.32, 0.25]])
    inner = np.array([[0, 0.02], [-0.16, 0.2], [-0.08, 0.5], [0, 0.72], [0.08, 0.5], [0.16, 0.2]])
    ax.add_patch(Polygon(outer * s + [x, y], closed=True, fc=FLAME, ec="none", zorder=4))
    ax.add_patch(Polygon(inner * s + [x, y], closed=True, fc=tint(WARM, 0.6), ec="none", zorder=5))


def burner(ax, x, y, w=0.9):
    ax.add_patch(Rectangle((x - w / 2, y - 0.45), w, 0.45, fc=LIGHT, ec=INK, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((x - w / 4, y), w / 2, 0.15, fc=METAL, ec=INK, lw=1.2, zorder=3))
    flame(ax, x, y + 0.15)


def wiggle(ax, p, q, n=6, amp=0.13, color=HOT, lw=1.6):
    """Wavy line (radiation) from p to q with an arrow head."""
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    L = np.hypot(*d)
    u = d / L
    nrm = np.array([-u[1], u[0]])
    s = np.linspace(0, 1, 200)
    pts = p[None, :] + np.outer(s, d) + np.outer(amp * np.sin(2 * np.pi * n * s), nrm)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, zorder=3)
    arrow(ax, pts[-6], q, color=color, lw=lw, scale=11)


# ------------------------------------------------------------ internal energy


def internal_parts():
    fig, ax = blank(10.6, 4.9, (-0.6, 13.4), (-2.3, 5.6))
    ax.add_patch(Rectangle((0, 0), 3.7, 0.35, fc=TABLE, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.25, -0.9), 0.3, 0.9, fc=TABLE, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((3.15, -0.9), 0.3, 0.9, fc=TABLE, ec=INK, lw=1.2))
    ax.add_patch(Circle((1.9, 3.6), 0.55, fc=LIGHT, ec=INK, lw=1.8))
    arrow(ax, (2.6, 3.6), (3.6, 3.6), color=COLD, lw=2)
    ax.text(3.7, 3.6, "$v$", color=COLD, va="center", fontsize=13)
    dim(ax, (0.6, 0.35), (0.6, 3.0), "$h$", off=(-0.3, 0))
    ax.text(
        1.85,
        -1.15,
        "Тело как целое: " + P + " (взаимодействие с Землёй)\nи " + K + " упорядоченного движения\nво внутреннюю энергию не входят",
        ha="center",
        va="top",
        color=INK,
    )
    cx, cy, R = 9.2, 2.6, 2.4
    ax.add_patch(Circle((cx, cy), R, fc=PAPER, ec=INK, lw=1.8))
    ax.plot([2.45, cx + R * np.cos(np.radians(125))], [3.95, cy + R * np.sin(np.radians(125))], color=GREY, lw=1.2, ls="--")
    ax.plot([2.45, cx + R * np.cos(np.radians(235))], [3.25, cy + R * np.sin(np.radians(235))], color=GREY, lw=1.2, ls="--")
    rng = np.random.default_rng(11)
    pts = []
    for _ in range(4000):
        p = rng.uniform(-1, 1, 2) * (R - 0.55)
        if np.hypot(*p) < R - 0.55 and all(np.hypot(*(p - q)) > 0.95 for q in pts):
            pts.append(p)
        if len(pts) == 13:
            break
    pts = np.array(pts) + [cx, cy]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if np.hypot(*(pts[i] - pts[j])) < 1.35:
                ax.plot(*zip(pts[i], pts[j]), color=GREEN, lw=1.5, ls=(0, (3, 2)), zorder=2)
    for p in pts:
        ax.add_patch(Circle(p, 0.2, fc=WATER, ec=INK, lw=1.2, zorder=3))
        a = rng.uniform(0, 2 * np.pi)
        arrow(ax, p, p + 0.55 * np.array([np.cos(a), np.sin(a)]), color=HOT, lw=1.5, scale=9)
    ax.text(cx, cy + R + 0.3, "Внутренняя энергия тела", ha="center", va="bottom", fontsize=13, color=INK)
    ax.text(cx, cy - R - 0.25, "красные стрелки: " + K + " хаотического движения молекул", ha="center", va="top", color=HOT)
    ax.text(cx, cy - R - 0.85, "зелёные линии: " + P + " взаимодействия молекул друг с другом", ha="center", va="top", color=GREEN)
    save(fig, "internal-energy-parts.png")


def internal_sand_bars():
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    labels = ["шар поднят", "шар падает,\nперед ударом", "шар лежит в песке"]
    ep = [100, 0, 0]
    ek = [0, 100, 0]
    ui = [0, 0, 100]
    x = np.arange(3)
    ax.bar(x, ep, 0.55, color=GOLD, label="потенциальная " + P)
    ax.bar(x, ek, 0.55, color=COLD, label="кинетическая " + K)
    ax.bar(x, ui, 0.55, color=HOT, label="внутренняя: шар и песок чуть нагрелись")
    for xi, txt in zip(x, ["100 %", "100 %", "100 %"]):
        ax.text(xi, 103, txt, ha="center", color=INK)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 178)
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("доля начальной энергии, %")
    ax.legend(loc="upper center", ncol=1, frameon=False, fontsize=9.5)
    ax.set_title("Куда девается механическая энергия шара")
    save(fig, "internal-sand-energy-bars.png")


def box(ax, x, y, w, h, text, fc, ec=INK, fs=11):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.6, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, zorder=4)


def internal_two_ways():
    fig, ax = blank(9.4, 5.0, (0, 12), (0, 6.4))
    box(ax, 4.3, 2.3, 3.4, 1.8, "Тело\nвнутренняя энергия $U$", LIGHT, fs=12)
    ax.text(2.1, 6.05, "1. Работа", ha="center", fontsize=13, color=INK)
    ax.text(9.9, 6.05, "2. Теплопередача", ha="center", fontsize=13, color=INK)
    ax.plot([6, 6], [0.3, 6.0], color=GRID, lw=1.5)
    arrow(ax, (2.0, 4.6), (4.3, 3.7), color=GREEN, lw=2.6, scale=16)
    ax.text(2.0, 5.1, "работа над телом:\nсгибают проволоку, трут\nладони, накачивают воздух", ha="center", va="center", fontsize=10)
    ax.text(3.15, 4.35, "$U$ растёт", ha="center", color=GREEN, rotation=17, fontsize=10)
    arrow(ax, (4.3, 2.7), (2.0, 1.6), color=HOT, lw=2.6, scale=16)
    ax.text(2.0, 0.85, "тело само совершает работу:\nсжатый воздух выталкивает\nпробку", ha="center", va="center", fontsize=10)
    ax.text(3.15, 2.45, "$U$ убывает", ha="center", color=HOT, rotation=17, fontsize=10)
    arrow(ax, (10.0, 4.6), (7.7, 3.7), color=GREEN, lw=2.6, scale=16)
    ax.text(10.0, 5.1, "тело получает $Q$:\nпроволока в пламени,\nшар в горячей воде", ha="center", va="center", fontsize=10)
    ax.text(8.85, 4.35, "$U$ растёт", ha="center", color=GREEN, rotation=-17, fontsize=10)
    arrow(ax, (7.7, 2.7), (10.0, 1.6), color=HOT, lw=2.6, scale=16)
    ax.text(10.0, 0.85, "тело отдаёт $Q$:\nгорячая вода остывает,\nшар нагревается", ha="center", va="center", fontsize=10)
    ax.text(8.85, 2.45, "$U$ убывает", ha="center", color=HOT, rotation=-17, fontsize=10)
    ax.text(6, 0.1, "Признак не различает способ: нагрелось — значит, $U$ выросла", ha="center", va="center", fontsize=10.5, color=INK)
    save(fig, "internal-two-ways.png")


def bottle(ax, x, y, s=1.0, fog=False, stopper=True):
    body = np.array([[0, 0], [0, 2.4], [0.35, 3.0], [0.35, 3.9], [0.85, 3.9], [0.85, 3.0], [1.2, 2.4], [1.2, 0]])
    ax.add_patch(Polygon(body * s + [x, y], closed=True, fc=WATER_FILL, ec=INK, lw=1.8, zorder=3))
    ax.add_patch(Rectangle((x + 0.02 * s, y + 0.02), 1.16 * s, 0.35 * s, fc=WATER, ec="none", zorder=3))
    if stopper:
        ax.add_patch(Polygon(np.array([[0.3, 3.85], [0.9, 3.85], [0.82, 4.25], [0.38, 4.25]]) * s + [x, y], closed=True, fc=STOPPER, ec=INK, lw=1.4, zorder=4))
    if fog:
        rng = np.random.default_rng(4)
        for _ in range(28):
            px = x + rng.uniform(0.1, 1.1) * s
            py = y + rng.uniform(0.5, 3.5) * s
            ax.add_patch(Circle((px, py), rng.uniform(0.06, 0.12), fc=PAPER, ec=GREY, lw=0.6, alpha=0.9, zorder=4))


def internal_bottle():
    fig, ax = blank(11.4, 5.6, (-0.6, 15.6), (-1.0, 6.7))
    # left: pumping
    bottle(ax, 4.0, 0.4)
    ax.plot([4.6, 4.6, 2.2], [4.65, 5.15, 5.15], color=INK, lw=2.4)
    ax.add_patch(Rectangle((0.5, 4.75), 1.7, 0.8, fc=LIGHT, ec=INK, lw=1.6))
    ax.plot([1.35, 1.35], [5.55, 6.0], color=INK, lw=3)
    ax.plot([0.85, 1.85], [6.0, 6.0], color=INK, lw=3)
    arrow(ax, (1.35, 6.4), (1.35, 5.8), color=INK, lw=1.6)
    ax.text(1.35, 4.5, "насос", ha="center", va="top")
    ax.text(4.6, 0.05, "вода на дне,\nводяной пар", ha="center", va="top", fontsize=10)
    ax.text(4.6, -0.75, "1. Накачивают воздух:\nработа над воздухом, $U$ растёт", ha="center", va="top", fontsize=10.5, color=GREEN)
    # right: stopper flies
    bottle(ax, 11.0, 0.4, fog=True, stopper=False)
    ax.add_patch(Polygon(np.array([[0.3, 3.85], [0.9, 3.85], [0.82, 4.25], [0.38, 4.25]]) + [11.9, 1.4], closed=True, fc=STOPPER, ec=INK, lw=1.4))
    arrow(ax, (11.6, 4.5), (11.9, 5.2), color=INK, lw=2)
    ax.text(12.8, 5.6, "пробка летит", fontsize=10.5, va="center")
    ax.text(11.6, 0.05, "туман: пар сконденсировался", ha="center", va="top", fontsize=10)
    ax.text(11.6, -0.75, "2. Воздух совершает работу над пробкой:\n$U$ убывает, воздух охлаждается", ha="center", va="top", fontsize=10.5, color=HOT)
    arrow(ax, (6.4, 2.2), (9.8, 2.2), color=INK, lw=2, scale=16)
    ax.text(8.1, 2.5, "отпускают пробку", ha="center", fontsize=10.5)
    save(fig, "internal-bottle-experiment.png")


# ------------------------------------------------------------------ transfer


def transfer_overview():
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.2))
    for a in axes:
        a.set_aspect("equal")
        a.axis("off")
    # conduction
    a = axes[0]
    a.set_xlim(0, 8)
    a.set_ylim(-1.2, 5)
    xs = np.linspace(0.6, 7.4, 60)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        f = (x0 - 0.6) / 6.8
        a.add_patch(Rectangle((x0, 2.0), x1 - x0, 0.7, fc=HOT_COLD(f), ec="none"))
    a.add_patch(Rectangle((0.6, 2.0), 6.8, 0.7, fc="none", ec=INK, lw=1.6))
    a.add_patch(Rectangle((0.3, 0.3), 1.2, 0.55, fc=LIGHT, ec=INK, lw=1.4))
    flame(a, 0.9, 0.85, 1.0)
    arrow(a, (2.0, 3.35), (6.6, 3.35), color=HOT, lw=2.6, scale=16)
    a.text(4.0, 4.15, "энергия идёт по телу,", ha="center", fontsize=10.5)
    a.text(4.0, 3.75, "вещество остаётся на месте", ha="center", fontsize=10.5)
    a.text(4.6, 1.3, "молекулы передают энергию\nсоседям при взаимодействии", ha="center", va="top", fontsize=10)
    a.set_title("Теплопроводность", fontsize=13)
    # convection
    a = axes[1]
    a.set_xlim(0, 8)
    a.set_ylim(-1.2, 5)
    a.add_patch(Polygon([[1.0, 1.2], [7.0, 1.2], [6.6, 4.3], [1.4, 4.3]], closed=True, fc=COOL_FILL, ec=INK, lw=1.6))
    for cx, sign in [(2.85, -1), (5.15, 1)]:
        t = np.linspace(0.15 * np.pi, 1.85 * np.pi, 60)
        xx = cx + 0.85 * np.cos(t)
        yy = 2.75 + 1.1 * np.sin(t)
        a.plot(xx, yy, color=GREY, lw=1.2)
    for (p, q, c) in [
        ((4.0, 1.7), (4.0, 3.9), HOT),
        ((4.0, 3.95), (2.25, 3.95), HOT),
        ((2.1, 3.7), (2.1, 1.7), COLD),
        ((2.2, 1.55), (3.7, 1.55), COLD),
        ((4.0, 3.95), (5.75, 3.95), HOT),
        ((5.9, 3.7), (5.9, 1.7), COLD),
        ((5.8, 1.55), (4.3, 1.55), COLD),
    ]:
        arrow(a, p, q, color=c, lw=2.2, scale=13)
    flame(a, 4.0, 0.15, 0.9)
    a.add_patch(Rectangle((3.4, -0.35), 1.2, 0.5, fc=LIGHT, ec=INK, lw=1.4))
    a.text(4.0, -0.7, "вещество движется струями:\nтёплое вверх, холодное вниз", ha="center", va="top", fontsize=10)
    a.set_title("Конвекция", fontsize=13)
    # radiation
    a = axes[2]
    a.set_xlim(0, 8)
    a.set_ylim(-1.2, 5)
    a.add_patch(Circle((1.1, 3.4), 0.85, fc=FLAME, ec=INK, lw=1.6))
    for ang in np.radians([-20, -40, -60]):
        p = (1.1 + 1.0 * np.cos(ang), 3.4 + 1.0 * np.sin(ang))
        q = (p[0] + 3.3 * np.cos(ang), p[1] + 3.3 * np.sin(ang))
        wiggle(a, p, q, n=6, amp=0.09)
    a.add_patch(Circle((6.7, 1.2), 0.7, fc=WATER, ec=INK, lw=1.6))
    a.text(4.0, 4.55, "пустота, среда не нужна", ha="center", fontsize=10.5, color=INK)
    a.text(4.0, -0.5, "энергию переносят\nэлектромагнитные волны", ha="center", va="top", fontsize=10)
    a.set_title("Излучение", fontsize=13)
    fig.tight_layout()
    save(fig, "transfer-overview-three.png")


def transfer_conduction_coins():
    fig, ax = blank(9.4, 4.4, (-0.4, 12.6), (-2.4, 3.2))
    ax.add_patch(Rectangle((0.3, 2.0), 5.6, 0.22, fc=BRASS, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((6.1, 2.0), 5.6, 0.22, fc=IRON, ec=INK, lw=1.4))
    ax.text(0.3, 2.65, "медь", color=BRASS, fontsize=12)
    ax.text(11.7, 2.65, "железо", color=IRON, fontsize=12, ha="right")
    burner(ax, 6.0, 0.55, 1.1)
    for i, x in enumerate([4.7, 3.5, 2.3]):
        ax.add_patch(Circle((x, 1.55), 0.32, fc=COIN, ec=INK, lw=1.2, ls="--", alpha=0.6))
        ax.add_patch(Circle((x, 1.55), 0.32, fc="none", ec=INK, lw=1.2, ls="--"))
        ax.plot([x, x], [2.0, 1.87], color=WAX, lw=3)
        ax.add_patch(Circle((x + 0.15 * (i - 1), -1.3 - 0.05 * i), 0.3, fc=COIN, ec=INK, lw=1.2))
    for i, x in enumerate([7.4, 8.6, 9.8]):
        fell = i == 0
        y = 1.55 if not fell else -1.6
        ax.add_patch(Circle((x, y), 0.32, fc=COIN, ec=INK, lw=1.2, ls="--" if fell else "-"))
        if not fell:
            ax.plot([x, x], [2.0, 1.87], color=WAX, lw=3)
    ax.plot([7.4, 7.4], [2.0, 1.87], color=WAX, lw=3)
    ax.add_patch(Circle((7.4, 1.55), 0.32, fc="none", ec=INK, lw=1.2, ls="--"))
    arrow(ax, (5.7, 3.0), (1.6, 3.0), color=HOT, lw=3.4, scale=20)
    arrow(ax, (6.3, 3.0), (10.6, 3.0), color=HOT, lw=1.6, scale=12)
    ax.text(3.4, 3.3, "энергия", ha="center", color=HOT)
    ax.text(8.5, 3.3, "энергия", ha="center", color=HOT)
    ax.text(3.4, -2.3, "упали все три монеты", ha="center", va="top", fontsize=10.5, color=INK)
    ax.text(8.6, -2.3, "упала одна монета", ha="center", va="top", fontsize=10.5, color=INK)
    ax.text(9.6, 0.2, "монеты на пластилине\nна одинаковых расстояниях\nот горелки", ha="center", va="center", fontsize=9.5, color=INK)
    save(fig, "transfer-conduction-coins.png")


DIFF_CU = 1.1e-4  # m^2/s, room temperature
DIFF_FE = 2.3e-5
T0, T_HOT, T_MELT = 20.0, 400.0, 60.0


def rod_temp(x, t, d):
    return T0 + (T_HOT - T0) * erfc(x / (2 * np.sqrt(d * t)))


def transfer_rod_profiles():
    x = np.linspace(0, 0.10, 300)
    times = [2, 5, 10, 20]
    cols = [tint(RED, 0.7), tint(RED, 0.45), tint(RED, 0.2), RED]  # a longer heating time is a deeper red
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), sharey=True)
    for ax, d, name in [(axes[0], DIFF_CU, "медь"), (axes[1], DIFF_FE, "железо")]:
        for t, c in zip(times, cols):
            ax.plot(x * 100, rod_temp(x, t, d), color=c, lw=2.2, label=f"{t} с")
        ax.axhline(T_MELT, color=GREY, lw=1.2, ls="--")
        ax.set_title(name)
        ax.set_xlabel("расстояние от пламени, см")
        for xc in [3, 6, 9]:
            ax.plot([xc], [T0 - 22], marker="o", color=COIN, mec=INK, clip_on=False, zorder=5)
        grid(ax)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 420)
    axes[0].set_ylabel("температура, °C")
    axes[1].text(9.9, T_MELT + 8, "пластилин плавится", ha="right", color=INK, fontsize=9.5)
    axes[1].legend(title="время нагрева", frameon=False, loc="upper right")
    fig.suptitle("Температура вдоль проволоки: медь прогревается глубже", y=1.02)
    fig.tight_layout()
    save(fig, "transfer-rod-temperature-profiles.png")


def fall_time(x, d):
    z = float(np.interp((T_MELT - T0) / (T_HOT - T0), np.sort(erfc(np.linspace(0, 3, 4000))), np.linspace(0, 3, 4000)[::-1]))
    return x**2 / (4 * d * z**2)


def transfer_coin_fall():
    t = np.linspace(0.05, 60, 800)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for d, c, name, ls in [(DIFF_CU, BRASS, "медь", "-"), (DIFF_FE, IRON, "железо", "-")]:
        for i, xc in enumerate([0.03, 0.06, 0.09]):
            ax.plot(t, rod_temp(xc, t, d), color=c, lw=2.2, alpha=(1.0, 0.7, 0.45)[i], label=f"{name}, {int(xc*100)} см" if i == 0 else None)
            tf = fall_time(xc, d)
            if tf < 60:
                ax.plot([tf], [T_MELT], marker="o", color=c, mec=INK, zorder=5)
                print(f"{name} {xc*100:.0f} cm falls at {tf:.1f} s")
    ax.axhline(T_MELT, color=GREY, lw=1.2, ls="--")
    ax.text(59, T_MELT + 8, "пластилин плавится: монета падает", ha="right", fontsize=9.5)
    ax.text(1.2, 250, "тёмные линии — ближняя монета (3 см),\nсветлее — 6 и 9 см", va="center", fontsize=9.5)
    ax.set_xlabel("время нагрева, с")
    ax.set_ylabel("температура в точке монеты, °C")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 300)
    grid(ax)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Монеты на меди падают раньше")
    save(fig, "transfer-coin-fall-times.png")


def transfer_conductivity_bars():
    classes = {
        0: ("металлы", METAL),
        1: ("жидкий металл", IRON),
        2: ("другие твёрдые тела", TABLE),
        3: ("жидкости", WATER),
        4: ("газ", LIGHT),
    }
    data = [
        ("серебро", 429, 0),
        ("медь", 401, 0),
        ("алюминий", 237, 0),
        ("железо", 80, 0),
        ("ртуть", 8.3, 1),
        ("стекло", 1.0, 2),
        ("кирпич", 0.7, 2),
        ("дерево", 0.15, 2),
        ("пенопласт", 0.04, 2),
        ("вода", 0.6, 3),
        ("машинное масло", 0.15, 3),
        ("воздух", 0.026, 4),
    ]
    data.sort(key=lambda r: -r[1])
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    y = np.arange(len(data))[::-1]
    for yi, (n, v, g) in zip(y, data):
        ax.barh(yi, v, color=classes[g][1], ec=INK, lw=0.8, height=0.7)
        ax.text(v * 1.15, yi, num(v, None), va="center", fontsize=9.5)
    ax.legend(
        handles=[Rectangle((0, 0), 1, 1, fc=c, ec=INK, lw=0.8) for _, c in classes.values()],
        labels=[n for n, _ in classes.values()],
        loc="lower right",
        frameon=False,
        fontsize=9.5,
    )
    ax.set_yticks(y, [r[0] for r in data])
    ax.set_xscale("log")
    ax.set_xlim(0.01, 1500)
    ax.set_ylim(-0.6, len(data) - 0.4)
    ax.set_xlabel("коэффициент теплопроводности, Вт/(м·К), логарифмическая шкала")
    ax.set_title("Проводники тепла от лучших к худшим")
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "transfer-conductivity-bars.png")


def transfer_conduction_mechanism():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8))
    for a in axes:
        a.set_aspect("equal")
        a.axis("off")
        a.set_xlim(0, 10)
        a.set_ylim(-1.2, 4.4)
    a = axes[0]
    a.set_title("Диэлектрик: колебания атомов передаются соседям", fontsize=11.5)
    for i in range(8):
        amp = 0.6 * np.exp(-i / 3.2)
        x = 0.8 + i * 1.15
        a.add_patch(Circle((x, 1.6), 0.3, fc=HOT if i < 3 else (WARM_FILL if i < 6 else COOL_FILL), ec=INK, lw=1.3, zorder=3))
        arrow(a, (x - amp, 2.35), (x + amp, 2.35), color=INK, style="<|-|>", scale=8, lw=1.3)
        if i < 7:
            xs = np.linspace(x + 0.3, x + 0.85, 12)
            a.plot(xs, 1.6 + 0.12 * np.sin(np.linspace(0, 6 * np.pi, 12)) * (1 if i % 2 == 0 else -1), color=GREY, lw=1.3)
    arrow(a, (1.0, 3.4), (8.6, 3.4), color=HOT, lw=2.4, scale=15)
    a.text(4.8, 3.75, "энергия", ha="center", color=HOT)
    a.text(4.8, 0.55, "чем сильнее взаимодействие\nмежду частицами, тем лучше передача", ha="center", va="top", fontsize=9.5)
    a = axes[1]
    a.set_title("Металл: ещё и свободные электроны", fontsize=11.5)
    for row in range(2):
        for i in range(7):
            # Ions are tinted from the hot left edge to the cold right edge, as the atoms in the left panel
            a.add_patch(Circle((1.0 + i * 1.3, 1.1 + row * 1.3), 0.3, fc=HOT if i < 2 else (WARM_FILL if i < 4 else COOL_FILL), ec=INK, lw=1.3, zorder=3))
            a.text(1.0 + i * 1.3, 1.1 + row * 1.3, "+", ha="center", va="center", fontsize=10, zorder=4)
    rng = np.random.default_rng(2)
    for _ in range(26):
        x, y = rng.uniform(0.6, 9.0), rng.uniform(0.6, 3.0)
        a.plot(x, y, "o", color=COLD, ms=4.5, zorder=5)
        # Free electrons move at random in all directions; those near the hot edge are faster (longer arrows)
        ang = rng.uniform(0, 2 * np.pi)
        ln = 0.25 + 0.5 * (9.0 - x) / 8.4
        arrow(a, (x, y), (x + ln * np.cos(ang), y + ln * np.sin(ang)), color=COLD, lw=1.1, scale=7)
    arrow(a, (1.0, 3.75), (8.6, 3.75), color=HOT, lw=2.4, scale=15)
    a.text(4.8, 4.05, "энергия", ha="center", color=HOT)
    a.text(4.8, 0.05, "электроны быстры и общие для всего куска:\nза это же металлы хорошо проводят ток", ha="center", va="top", fontsize=9.5)
    fig.tight_layout()
    save(fig, "transfer-conduction-mechanism.png")


def transfer_convection_flask():
    fig, ax = blank(6.9, 5.4, (-0.5, 8), (-1.6, 6.6))
    flask = [[0.8, 0.6], [7.2, 0.6], [5.5, 4.6], [5.5, 6.0], [2.5, 6.0], [2.5, 4.6]]
    ax.add_patch(Polygon(flask, closed=True, fc=LIGHT, ec="none"))
    # The liquid takes the flask outline up to y = 4.3: the fill edges lie on the slanted walls
    ax.add_patch(Polygon([[0.8, 0.6], [7.2, 0.6], [5.6275, 4.3], [2.3725, 4.3]], closed=True, fc=COOL_FILL, ec="none"))
    ax.add_patch(Polygon(flask, closed=True, fill=False, ec=INK, lw=2, zorder=3))
    ax.add_patch(Circle((4.0, 1.25), 0.6, fc=ACCENT, ec="none", alpha=0.7))
    ax.text(4.0, 1.25, "краситель", ha="center", va="center", fontsize=7, color=PAPER)
    for (p, q, c) in [
        ((4.0, 1.9), (4.0, 3.9), HOT),
        ((3.9, 4.0), (3.1, 4.0), HOT),
        ((3.0, 3.9), (2.75, 1.8), COLD),
        ((2.6, 1.35), (3.35, 1.35), COLD),
        ((4.1, 4.0), (4.9, 4.0), HOT),
        ((5.0, 3.9), (5.25, 1.8), COLD),
        ((5.4, 1.35), (4.65, 1.35), COLD),
    ]:
        arrow(ax, p, q, color=c, lw=2.6, scale=15)
    flame(ax, 4.0, -0.1, 0.65)
    ax.add_patch(Rectangle((3.3, -0.6), 1.4, 0.5, fc=LIGHT, ec=INK, lw=1.4))
    ax.text(-0.45, 5.2, "тёплая жидкость:\nплотность меньше,\nона всплывает", fontsize=9.5, color=HOT, va="center")
    ax.text(7.95, 5.2, "холодная\nопускается", fontsize=9.5, color=COLD, va="center", ha="right")
    ax.text(4.0, 6.4, "конвекционные потоки", ha="center", fontsize=11)
    save(fig, "transfer-convection-flask.png")


def transfer_air_density():
    t = np.linspace(-20, 120, 300)
    rho = 101325 * 0.02897 / (8.314 * (t + 273.15))
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.plot(t, rho, color=INK, lw=2.4)
    for tt, name, col in [(20, "воздух в комнате", COLD), (70, "воздух у лампы", HOT)]:
        r = 101325 * 0.02897 / (8.314 * (tt + 273.15))
        ax.plot([tt], [r], "o", color=col, ms=9, mec=INK, zorder=5)
        ax.plot([tt, tt], [0.85, r], color=col, lw=1.2, ls="--")
        ax.text(tt + 3, r + 0.03, f"{name}\n{num(tt, '')} °C: {num(r, 2)} кг/м³", color=col, fontsize=9.5)
    ax.set_xlabel("температура воздуха, °C")
    ax.set_ylabel("плотность, кг/м³")
    ax.set_ylim(0.85, 1.4)
    ax.set_xlim(-20, 120)
    grid(ax)
    ax.set_title("Плотность воздуха падает с нагреванием")
    save(fig, "transfer-air-density-temperature.png")


def room(ax, x0, window_right=True):
    ax.add_patch(Rectangle((x0, 0), 4.6, 3.2, fc=PAPER, ec=INK, lw=2))
    ax.add_patch(Rectangle((x0 + 4.6 - 0.07, 1.0), 0.14, 1.9, fc=WATER, ec=INK, lw=1.2, zorder=4))
    ax.text(x0 + 4.6 + 0.2, 1.95, "окно", fontsize=10, va="center")


def transfer_room_radiator():
    fig, ax = blank(11.4, 4.6, (-0.5, 12.6), (-1.6, 4.0))
    # a: radiator under window
    room(ax, 0.0)
    ax.add_patch(Rectangle((4.1, 0.05), 0.4, 0.8, fc=HOT, ec=INK, lw=1.2, zorder=4))
    ax.text(2.3, -0.2, "батарея под окном", ha="center", va="top", fontsize=11)
    pts = [(4.0, 0.5), (4.0, 2.9), (0.6, 2.9), (0.6, 0.4), (3.5, 0.4)]
    cols = [HOT, tint(RED, 0.4), tint(BLUE, 0.4), tint(BLUE, 0.65)]  # the air cools along its way
    for (p, q), c in zip(zip(pts[:-1], pts[1:]), cols):
        arrow(ax, p, q, color=c, lw=2.6, scale=15)
    ax.text(2.3, 1.6, "циркуляция:\nхолод от окна не\nдоходит до пола", ha="center", va="center", fontsize=10)
    # b: radiator opposite
    room(ax, 7.4)
    ax.add_patch(Rectangle((7.5, 0.05), 0.4, 0.8, fc=HOT, ec=INK, lw=1.2, zorder=4))
    ax.text(9.7, -0.2, "батарея у противоположной стены", ha="center", va="top", fontsize=11)
    arrow(ax, (8.2, 0.6), (8.2, 2.9), color=HOT, lw=2.6, scale=15)
    arrow(ax, (8.3, 2.9), (10.0, 2.9), color=HOT, lw=2.6, scale=15)
    arrow(ax, (11.6, 2.5), (11.6, 0.5), color=COLD, lw=2.6, scale=15)
    arrow(ax, (11.5, 0.4), (8.6, 0.4), color=COLD, lw=3.6, scale=17)
    ax.text(9.8, 0.95, "холодный воздух\nидёт по полу: сквозняк", ha="center", va="center", fontsize=10, color=COLD)
    save(fig, "transfer-room-radiator.png")


def transfer_breeze():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.2))
    for a, day in zip(axes, (True, False)):
        a.set_aspect("equal")
        a.axis("off")
        a.set_xlim(0, 10)
        a.set_ylim(-1.6, 5.4)
        land_c = WARM if day else tint(BLUE, 0.5)
        sea_c = tint(SKY, 0.6) if day else tint(WARM, 0.6)
        a.add_patch(Polygon([[0, -0.6], [4.6, -0.6], [5.4, -1.2], [5.4, -1.6], [0, -1.6]], closed=True, fc=land_c, ec=INK, lw=1.4))
        a.add_patch(Polygon([[5.4, -0.9], [10, -0.9], [10, -1.6], [5.4, -1.6]], closed=True, fc=sea_c, ec=INK, lw=1.4))
        a.text(2.4, -1.1, "берег " + ("горячий" if day else "прохладный"), ha="center", va="center", fontsize=10.5)
        a.text(7.7, -1.25, "море " + ("прохладное" if day else "тёплое"), ha="center", va="center", fontsize=10.5)
        if day:
            a.add_patch(Circle((1.0, 4.7), 0.45, fc=FLAME, ec=INK, lw=1.4))
            for ang in np.linspace(0, 2 * np.pi, 9)[:-1]:
                a.plot([1.0 + 0.6 * np.cos(ang), 1.0 + 0.85 * np.cos(ang)], [4.7 + 0.6 * np.sin(ang), 4.7 + 0.85 * np.sin(ang)], color=FLAME, lw=1.6)
            arrow(a, (2.3, 0.3), (2.3, 4.6), color=HOT, lw=2.6, scale=15)
            arrow(a, (2.4, 4.6), (6.6, 4.6), color=GREY, lw=2, scale=13)
            arrow(a, (6.6, 4.5), (6.6, 0.5), color=GREY, lw=2, scale=13)
            arrow(a, (6.4, 0.2), (2.5, 0.2), color=COLD, lw=3.4, scale=17)
            a.text(4.4, 1.0, "дневной бриз:\nс моря на сушу", ha="center", fontsize=11, color=COLD)
            a.set_title("День", fontsize=13)
        else:
            arrow(a, (7.6, 0.4), (7.6, 4.6), color=HOT, lw=2.6, scale=15)
            arrow(a, (7.6, 4.6), (3.4, 4.6), color=GREY, lw=2, scale=13)
            arrow(a, (3.4, 4.6), (3.4, 0.6), color=GREY, lw=2, scale=13)
            arrow(a, (3.6, 0.2), (7.4, 0.2), color=COLD, lw=3.4, scale=17)
            a.text(5.5, 1.0, "ночной бриз:\nс суши на море", ha="center", fontsize=11, color=COLD)
            a.set_title("Ночь", fontsize=13)
    fig.tight_layout()
    save(fig, "transfer-breeze.png")


def transfer_kerosene_lamp():
    fig, ax = blank(7.6, 5.6, (-4.2, 6.4), (-1.0, 7.4))
    # tank
    ax.add_patch(Polygon([[-1.6, 0], [1.6, 0], [1.9, 0.9], [1.3, 1.6], [-1.3, 1.6], [-1.9, 0.9]], closed=True, fc=tint(COPPER, 0.4), ec=INK, lw=1.8))
    ax.text(0, 0.55, "керосин", ha="center", va="center", fontsize=10.5)
    # burner with holes
    ax.add_patch(Rectangle((-0.9, 1.6), 1.8, 0.7, fc=LIGHT, ec=INK, lw=1.6))
    for x in (-0.55, 0, 0.55):
        ax.add_patch(Circle((x, 1.95), 0.09, fc=INK, ec="none"))
    ax.add_patch(Rectangle((-0.13, 1.3), 0.26, 1.9, fc=tint(WARM, 0.8), ec=INK, lw=1.2, zorder=3))
    flame(ax, 0, 3.2, 1.4)
    # glass chimney
    ax.add_patch(Polygon([[-0.9, 2.3], [-0.9, 2.8], [-1.35, 3.6], [-0.6, 4.4], [-0.55, 6.6], [0.55, 6.6], [0.6, 4.4], [1.35, 3.6], [0.9, 2.8], [0.9, 2.3]], closed=True, fc="none", ec=INK, lw=1.6, alpha=0.9))
    for (p, q, c) in [
        ((-2.6, 2.05), (-1.0, 2.05), COLD),
        ((2.6, 2.05), (1.0, 2.05), COLD),
    ]:
        arrow(ax, p, q, color=c, lw=2.8, scale=16)
    for x in (-0.3, 0.3):
        arrow(ax, (x, 4.7), (x, 6.9), color=HOT, lw=2.4, scale=14)
    ax.text(-2.7, 2.35, "воздух через\nотверстия", ha="right", va="bottom", fontsize=10, color=COLD)
    ax.text(1.2, 5.9, "тяга: нагретый воздух\nв стекле поднимается,\nснизу подсасывается\nсвежий", ha="left", va="center", fontsize=10, color=HOT)
    ax.annotate("ламповое стекло", xy=(-1.3, 3.7), xytext=(-2.2, 4.6), ha="right", va="center", fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("пламя", xy=(0.25, 3.6), xytext=(2.3, 3.6), ha="left", va="center", fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("фитиль, пропитанный\nкеросином", xy=(0.13, 2.7), xytext=(2.3, 2.75), ha="left", va="center", fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    save(fig, "transfer-kerosene-lamp.png")


def transfer_draught_height():
    h = np.logspace(-1, 3, 200)
    rho_out = 101325 * 0.02897 / (8.314 * 273.15)
    rho_in = 101325 * 0.02897 / (8.314 * (150 + 273.15))
    dp = 9.81 * h * (rho_out - rho_in)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.loglog(h, dp, color=INK, lw=2.4)
    for hh, name, dx, dy in [(0.2, "лампа, стекло 20 см", 1.4, 0.6), (10, "печная труба, 10 м", 1.4, 0.6), (420, "Экибастузская ГРЭС-2, 420 м", 0.12, 1.6)]:  # label above the line, left of the point
        d = 9.81 * hh * (rho_out - rho_in)
        ax.plot([hh], [d], "o", color=HOT, ms=9, mec=INK, zorder=5)
        txt = f"{d:.1f}" if d < 10 else f"{d:.0f}"
        ax.annotate(f"{name}\n{num(txt, '')} Па", xy=(hh, d), xytext=(hh * dx, d * dy), fontsize=9.5, va="center", ha="left" if dx > 1 else "right")
    ax.set_xlabel("высота трубы, м")
    ax.set_ylabel("разность давлений (тяга), Па")
    ax.grid(True, which="both", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Чем выше труба, тем сильнее тяга")
    save(fig, "transfer-draught-height.png")


def u_tube(ax, x, diff, base=0.0):
    """U-tube manometer at x; positive diff raises the right column."""
    ax.plot([x, x, x + 0.9, x + 0.9], [base + 3.0, base, base, base + 3.0], color=INK, lw=2.2)
    lv = base + 1.4
    ax.add_patch(Rectangle((x + 0.03, base + 0.03), 0.84, 0.0, fc=WATER))
    ax.add_patch(Polygon([[x + 0.04, base + 0.03], [x + 0.86, base + 0.03], [x + 0.86, lv + diff / 2], [x + 0.46, lv + diff / 2], [x + 0.46, lv - diff / 2], [x + 0.04, lv - diff / 2]], closed=True, fc=WATER, ec="none"))


def transfer_radiation_receiver():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.2))
    for a, black in zip(axes, (True, False)):
        a.set_aspect("equal")
        a.axis("off")
        a.set_xlim(0, 12)
        a.set_ylim(-1.4, 4.6)
        a.add_patch(Rectangle((0.3, 0.2), 1.3, 1.2, fc=LIGHT, ec=INK, lw=1.6))
        a.add_patch(Rectangle((0.3, 1.4), 1.3, 0.14, fc=RED, ec=INK, lw=1.2))
        a.text(0.95, -0.2, "плитка", ha="center", va="top", fontsize=10.5)
        a.add_patch(Rectangle((4.2, 0.5), 1.3, 1.6, fc=PAPER, ec=INK, lw=1.6))
        a.add_patch(Rectangle((4.2, 0.5), 0.22, 1.6, fc=SOOT if black else LIGHT, ec=INK, lw=1.4))
        a.add_patch(Rectangle((5.28, 0.5), 0.22, 1.6, fc=LIGHT if black else SOOT, ec=INK, lw=1.4))
        a.text(4.85, 0.1, "теплоприёмник", ha="center", va="top", fontsize=10.5)
        for y in (0.8, 1.3, 1.8):
            if black:
                wiggle(a, (1.8, y), (4.1, y), n=4, amp=0.07, color=HOT, lw=1.4)
            else:
                wiggle(a, (1.8, y), (4.1, y), n=4, amp=0.07, color=HOT, lw=1.4)
        if not black:
            for y in (0.8, 1.3, 1.8):
                arrow(a, (4.1, y + 0.08), (2.7, y + 0.35), color=GREY, lw=1.0, scale=7)
        a.plot([5.5, 6.8, 6.8, 8.3], [1.3, 1.3, 3.6, 3.6], color=INK, lw=1.4, ls=(0, (4, 2)))
        d = 0.8 if black else 0.0
        u_tube(a, 8.3, d, base=1.1)
        a.text(8.75, 0.75, "манометр", ha="center", va="top", fontsize=10.5)
        a.set_title("Чёрная сторона к плитке" if black else "Блестящая сторона к плитке", fontsize=12.5)
        a.text(10.4, 2.6, "давление\nвыросло" if black else "давление\nне выросло", ha="left", va="center", fontsize=10, color=HOT if black else COLD)
        a.text(3.0, 2.85, "излучение" if black else "излучение отражается", ha="center", fontsize=10, color=HOT)
    fig.tight_layout()
    save(fig, "transfer-radiation-receiver.png")


def transfer_albedo():
    data = [
        ("свежий снег", 0.85, tint(SKY, 0.85)),
        ("белая краска", 0.80, LIGHT),
        ("морской лёд", 0.55, tint(SKY, 0.6)),
        ("сухой песок", 0.35, WARM),
        ("лес", 0.12, GREEN),
        ("тёмный асфальт", 0.07, IRON),
        ("вода", 0.06, WATER),
        ("сажа", 0.03, INK),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    y = np.arange(len(data))[::-1]
    for yi, (n, v, c) in zip(y, data):
        ax.barh(yi, v, color=c, ec=INK, lw=0.9, height=0.7)
        ax.text(v + 0.015, yi, num(v, 2), va="center", fontsize=9.5)
    ax.set_yticks(y, [r[0] for r in data])
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("доля отражённого солнечного излучения")
    ax.set_title("Светлое отражает, тёмное поглощает")
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "transfer-albedo-bars.png")


def planck(lam_um, T):
    lam = lam_um * 1e-6
    h, c, kB = 6.626e-34, 2.998e8, 1.381e-23
    return 1 / (lam**5 * (np.exp(h * c / (lam * kB * T)) - 1))


def transfer_radiation_spectra():
    lam = np.logspace(-1, 2, 600)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.axvspan(0.38, 0.78, color=tint(WARM, 0.7), alpha=0.7)
    ax.text(0.55, 0.04, "видимый\nсвет", ha="center", va="bottom", fontsize=9.5)
    for T, c, name in [(300, COLD, "300 К (комната, тело)"), (1000, COPPER, "1000 К (раскалённая плитка)"), (5800, HOT, "5800 К (Солнце)")]:
        s = planck(lam, T)
        ax.plot(lam, s / s.max(), color=c, lw=2.4, label=name)
    ax.set_xscale("log")
    # Headroom above the curves keeps the legend off every peak
    ax.set_ylim(0, 1.5)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("длина волны, мкм")
    ax.set_ylabel("мощность излучения (в долях максимума)")
    ax.set_title("Чем горячее тело, тем короче волны его излучения")
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    ax.grid(True, which="major", color=GRID, lw=0.8)
    save(fig, "transfer-radiation-spectra.png")


def transfer_radiation_power():
    t = np.linspace(-20, 300, 300)
    s = 5.670e-8 * (t + 273.15) ** 4
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(t, s, color=INK, lw=2.4)
    for tt, name, pos in [(25, "доска, 25 °C", (-15, 1900)), (38.8, "рот, 38,8 °C", (30, 3300)), (128, "плитка, 128 °C", (140, 3600))]:
        v = 5.670e-8 * (tt + 273.15) ** 4
        ax.plot([tt], [v], "o", color=HOT, ms=9, mec=INK, zorder=5)
        ax.annotate(f"{name}\n{v:.0f} Вт/м²", xy=(tt, v), xytext=pos, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlabel("температура тела, °C")
    ax.set_ylabel("мощность излучения с 1 м², Вт/м²")
    ax.set_title("Чем горячее тело, тем сильнее оно излучает")
    ax.set_ylim(0, 1600 * 5)
    grid(ax)
    save(fig, "transfer-radiation-power.png")


def transfer_thermos():
    fig, ax = blank(8.9, 6.0, (-5.2, 5.6), (-1.6, 6.6))
    ax.add_patch(Polygon([[-1.5, 0], [1.5, 0], [1.5, 4.6], [1.0, 5.0], [-1.0, 5.0], [-1.5, 4.6]], closed=True, fc=LIGHT, ec=INK, lw=1.8))
    # double wall flask
    outer = Polygon([[-1.3, 0.2], [1.3, 0.2], [1.3, 4.4], [0.9, 4.8], [-0.9, 4.8], [-1.3, 4.4]], closed=True, fc=tint(SKY, 0.8), ec=INK, lw=2)
    ax.add_patch(outer)
    inner = Polygon([[-1.0, 0.5], [1.0, 0.5], [1.0, 4.3], [0.7, 4.6], [-0.7, 4.6], [-1.0, 4.3]], closed=True, fc=WARM_FILL, ec=INK, lw=2)
    ax.add_patch(inner)
    ax.add_patch(Polygon([[-0.9, 0.55], [0.9, 0.55], [0.9, 3.4], [-0.9, 3.4]], closed=True, fc=tint(WARM, 0.5), ec="none"))
    ax.plot([1.15, 1.15], [0.35, 4.3], color=SILVER, lw=2.5)
    ax.plot([-1.15, -1.15], [0.35, 4.3], color=SILVER, lw=2.5)
    ax.plot([0.88, 0.88], [0.6, 4.2], color=SILVER, lw=2.5)
    ax.plot([-0.88, -0.88], [0.6, 4.2], color=SILVER, lw=2.5)
    ax.add_patch(Rectangle((-0.65, 4.75), 1.3, 0.75, fc=STOPPER, ec=INK, lw=1.5))
    ax.text(0, 4.1, "горячая\nжидкость", ha="center", va="center", fontsize=10, zorder=6)
    ax.text(3.9, 4.9, "пробка", va="center", fontsize=10.5)
    ax.plot([0.7, 3.8], [5.1, 4.9], color=GREY, lw=1)  # leader starts at the cork edge
    ax.text(3.9, 3.0, "вакуум между стенками:\nнет ни теплопроводности,\nни конвекции", va="center", fontsize=10, color=COLD)
    ax.plot([1.2, 3.8], [2.4, 2.9], color=GREY, lw=1)
    ax.text(-5.0, 1.3, "серебристые\nповерхности отражают\nтепловое излучение", va="center", fontsize=10, color=HOT)
    ax.plot([-1.1, -2.3], [1.5, 1.4], color=GREY, lw=1)
    arrow(ax, (0.3, 2.5), (0.85, 2.1), color=HOT, lw=1.6, scale=9)
    arrow(ax, (0.85, 2.1), (0.2, 1.6), color=HOT, lw=1.6, scale=9)
    ax.text(0, -0.5, "Термос: горячее остаётся горячим, холодное — холодным", ha="center", va="top", fontsize=11)
    save(fig, "transfer-thermos.png")


# --------------------------------------------------------------------- tasks


C_W = 4200.0
G = 10.0


def task_elephant():
    m = np.logspace(0, 4.3, 200)
    q = 3 * C_W * 80
    h = q / (m * G)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.loglog(m, h, color=INK, lw=2.4)
    for mm, hh, name, dx, dy in [(4000, 25.2, "слон 4 т: 25 м", 1.4, 1.5), (1000, 100.8, "1 т: 100 м", 1.4, 1.5), (1, 1.008e5, "1 кг: 100 км", 1.8, 1.0)]:
        ax.plot([mm], [hh], "o", color=HOT, ms=9, mec=INK, zorder=5)
        ax.annotate(name, xy=(mm, hh), xytext=(mm * dx, hh * dy), fontsize=10, va="center")
    ax.set_xlabel("масса поднимаемого тела, кг")
    ax.set_ylabel("высота подъёма, м")
    ax.set_title("Энергия одного чайника: масса и высота")
    ax.grid(True, which="both", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "internal-task-elephant-height.png")


def task_drop():
    h = np.linspace(0, 50, 200)
    dt = G * h * 1000 / C_W
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(h, dt, color=INK, lw=2.4)
    ax.axhline(100, color=GREY, lw=1.2, ls="--")
    ax.plot([42], [100], "o", color=HOT, ms=10, mec=INK, zorder=5)
    ax.annotate("42 км: вода нагрета от 0 °C до 100 °C", xy=(42, 100), xytext=(6, 106), fontsize=10)
    ax.set_xlabel("высота падения, км")
    ax.set_ylabel("нагрев капли, °C")
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 125)
    ax.text(26, 12, "водопад 100 м нагревает\nводу всего на 0,24 °C", fontsize=10, color=COLD)
    grid(ax)
    ax.set_title("Нагрев падающей капли без потерь")
    save(fig, "internal-task-drop-height.png")


def task_steel_lead():
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.9))
    names = ["сталь", "свинец"]
    cols = [IRON, LEAD]
    data = [
        ("удельная теплоёмкость $c$,\nДж/(кг·°C)", [500, 140]),
        ("плотность $\\rho$, кг/м³", [7800, 11300]),
        ("$c\\rho$ (теплоёмкость\nединицы объёма), МДж/(м³·°C)", [500 * 7800 / 1e6, 140 * 11300 / 1e6]),
    ]
    for a, (title, vals) in zip(axes, data):
        a.bar(names, vals, color=cols, ec=INK, width=0.6)
        for i, v in enumerate(vals):
            label = num(v, 0) if v >= 100 else num(v, ".3g")
            a.text(i, v * 1.02, label, ha="center", va="bottom", fontsize=10)
        a.set_title(title, fontsize=10.5)
        a.set_ylim(0, max(vals) * 1.18)
        a.spines["left"].set_visible(False)
        a.set_yticks([])
    axes[2].text(0.5, max(data[2][1]) * 1.1, "в 2,5 раза", ha="center", color=HOT, fontsize=11)
    fig.suptitle("Шары равного объёма: теплоёмкость шара $\\propto c\\rho$", y=1.02)
    fig.tight_layout()
    save(fig, "internal-task-steel-lead.png")


def task_wet_sand():
    x = np.linspace(0, 1, 200)
    r = x * 4200 / 800 + (1 - x)
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.plot(x * 100, r, color=INK, lw=2.4)
    ax.plot([20], [1.85], "o", color=HOT, ms=10, mec=INK, zorder=5)
    ax.annotate("20 % воды: 1,85", xy=(20, 1.85), xytext=(28, 1.3), fontsize=10.5, arrowprops=dict(arrowstyle="-|>", color=INK))
    ax.axhline(1, color=GREY, lw=1.2, ls="--")
    ax.text(99, 1.12, "сухой песок", ha="right", color=NOTE)
    ax.set_xlabel("доля воды в массе, %")
    ax.set_ylabel("$Q_\\mathrm{мокр} / Q_\\mathrm{сух}$")
    ax.set_xlim(0, 100)
    ax.set_ylim(0.8, 5.5)
    grid(ax)
    ax.set_title("Во сколько раз дороже нагреть мокрый песок")
    save(fig, "internal-task-wet-sand.png")


def main():
    internal_parts()
    internal_sand_bars()
    internal_two_ways()
    internal_bottle()
    transfer_overview()
    transfer_conduction_coins()
    transfer_rod_profiles()
    transfer_coin_fall()
    transfer_conductivity_bars()
    transfer_conduction_mechanism()
    transfer_convection_flask()
    transfer_air_density()
    transfer_room_radiator()
    transfer_breeze()
    transfer_kerosene_lamp()
    transfer_draught_height()
    transfer_radiation_receiver()
    transfer_albedo()
    transfer_radiation_spectra()
    transfer_radiation_power()
    transfer_thermos()
    task_elephant()
    task_drop()
    task_steel_lead()
    task_wet_sand()


if __name__ == "__main__":
    main()
