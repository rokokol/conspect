"""Figures for the note "Количество теплоты. Удельная теплоёмкость" (section f10, lessons 108-110, 117, 118).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 heat_capacity.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefix heat-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

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
WATER = BLUE  # water as a line or a bar
WATER_FILL = tint(SKY, 0.7)  # the body of water in a vessel
WATER_FILL_PALE = tint(SKY, 0.8)
WATER_FILL_DEEP = tint(SKY, 0.6)
HOT_FILL = tint(RED, 0.85)  # a hot body: the heater block
OIL = WARM
SAND = tint(INK, 0.4)  # sand: a grey line, kept apart from the peach oil and the copper
IRON = tint(INK, 0.2)  # dark steel
ALU = METAL
LEAD = VIOLET
COIL = COPPER  # the wire of a heater
TANGENT = ACCENT  # the tangent line, a highlighted construction


save = saver(OUT)


def axes_grid(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    return fig, ax


# 1. glass and pot: Q against dt, the slope is the heat capacity
def glass_pot():
    fig, ax = axes_grid(6.2, 4.2)
    dt = np.array([0, 1, 2, 3])
    for c, col, name in ((4, HOT, "кастрюля, $C=4$ кДж/°C"), (1, COLD, "стакан, $C=1$ кДж/°C")):
        ax.plot(dt, c * dt, "-o", color=col, lw=2, label=name)
    ax.set_xlabel(r"$\Delta t$, °C")
    ax.set_ylabel(r"$Q$, кДж")
    ax.set_xticks(dt)
    ax.set_yticks(range(0, 13, 2))
    ax.set_xlim(0, 3.3)
    ax.set_ylim(0, 13)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Количество теплоты и нагрев тела")
    save(fig, "heat-glass-pot-q-dt.png")


# 2. time and temperature for glass and pot on the same 100 W heater
def glass_pot_time():
    fig, ax = axes_grid(6.2, 4.2)
    tau = np.linspace(0, 120, 50)
    for c, col, name in ((4, HOT, "кастрюля"), (1, COLD, "стакан")):
        ax.plot(tau, 20 + 100 * tau / (c * 1000), color=col, lw=2, label=name)
    ax.set_xlabel(r"$\tau$, с")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, 125)
    ax.set_ylim(20, 33)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Нагреватель 100 Вт: температура от времени")
    save(fig, "heat-glass-pot-t-time.png")


# 3. t(Q) for 1 kg of different substances: the slope is 1/(cm)
def t_of_q(items, name, title, qmax, tmax, m=1.0):
    fig, ax = axes_grid(6.4, 4.4)
    q = np.array([0, qmax])
    for label, c, col in items:
        ax.plot(q, 20 + q * 1000 / (c * m), color=col, lw=2.2, label=f"{label}, $c={c}$")
    ax.set_xlabel(r"$Q$, кДж")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, qmax)
    ax.set_ylim(20, tmax)
    ax.legend(loc="upper left", frameon=False, fontsize=10, title="Дж/(кг·°C)", title_fontsize=9)
    ax.set_title(title)
    save(fig, name)


def water_oil_sand():
    t_of_q(
        [("вода", 4200, WATER), ("масло", 1700, OIL), ("песок", 850, SAND)],
        "heat-water-oil-sand-t-q.png",
        "Нагрев 1 кг: вода, масло, песок",
        50,
        80,
    )


def metals():
    t_of_q(
        [("свинец", 140, LEAD), ("медь", 400, COPPER), ("железо", 460, IRON), ("алюминий", 920, ALU)],
        "heat-metals-t-q.png",
        "Нагрев 1 кг металлов",
        15,
        130,
    )


# 4. the same substance, different masses
def masses():
    fig, ax = axes_grid(6.4, 4.4)
    q = np.array([0, 420])
    for m, col in ((1, HOT), (2, GREEN), (4, COLD)):
        ax.plot(q, 20 + q * 1000 / (4200 * m), color=col, lw=2.2, label=f"вода, $m={m}$ кг")
    ax.set_xlabel(r"$Q$, кДж")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, 420)
    ax.set_ylim(20, 120)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Нагрев воды разной массы")
    save(fig, "heat-water-masses-t-q.png")


# 5. bar chart of specific heat capacity
def bars():
    data = [
        ("золото", 130, "s"),
        ("свинец", 140, "s"),
        ("ртуть", 140, "l"),
        ("олово", 230, "s"),
        ("серебро", 250, "s"),
        ("медь", 400, "s"),
        ("латунь", 400, "s"),
        ("железо", 460, "s"),
        ("сталь", 500, "s"),
        ("алюминий", 920, "s"),
        ("масло подсолн.", 1700, "l"),
        ("лёд", 2100, "s"),
        ("керосин", 2100, "l"),
        ("спирт", 2500, "l"),
        ("вода", 4200, "l"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    names = [d[0] for d in data]
    vals = [d[1] for d in data]
    cols = [WATER if d[2] == "l" else METAL for d in data]
    y = np.arange(len(data))
    ax.barh(y, vals, color=cols)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    for yi, v in zip(y, vals):
        ax.text(v + 50, yi, str(v), va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 4800)
    ax.set_xlabel(r"$c$, Дж/(кг·°C)")
    ax.set_title("Удельная теплоёмкость веществ")
    ax.legend(
        handles=[Rectangle((0, 0), 1, 1, color=METAL), Rectangle((0, 0), 1, 1, color=WATER)],
        labels=["твёрдые", "жидкие"],
        loc="upper right",
        frameon=False,
    )
    save(fig, "heat-specific-capacity-bars.png")


# 6. received and given heat on one line
def sign():
    fig, ax = axes_grid(6.4, 4.2)
    k = 1000 / (4200 * 0.1)
    q = np.array([-10, 10])
    ax.plot(q, 40 + q * k, color=INK, lw=2)
    ax.axvline(0, color=GREY, lw=1)
    ax.annotate("", xy=(9, 40 + 9 * k), xytext=(2, 40 + 2 * k),
                arrowprops=dict(arrowstyle="->", color=HOT, lw=2))
    ax.annotate("", xy=(-9, 40 - 9 * k), xytext=(-2, 40 - 2 * k),
                arrowprops=dict(arrowstyle="->", color=COLD, lw=2))
    ax.text(5.5, 40 - 6, r"$Q>0$: получено, $t$ растёт", color=HOT, ha="center", fontsize=10)
    ax.text(-5.5, 40 + 6, r"$Q<0$: отдано, $t$ падает", color=COLD, ha="center", fontsize=10)
    ax.set_xlabel(r"$Q$, кДж")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(-10, 10)
    ax.set_ylim(10, 70)
    ax.set_title("Знак количества теплоты, вода 0,1 кг")
    save(fig, "heat-received-given-sign.png")


# 7. the two calorimeters
def calorimeter():
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 4.6))
    for ax in axs:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")
        ax.axis("off")
    # simple one
    ax = axs[0]
    ax.set_title("Простейший")
    # Both vessels are open at the top and closed at the bottom
    ax.add_patch(Polygon([(1.5, 6.6), (1.5, 1.2), (8.5, 1.2), (8.5, 6.6)], closed=False, fill=False, ec=INK, lw=2.2))
    ax.add_patch(Polygon([(2.6, 6.0), (2.6, 1.8), (7.4, 1.8), (7.4, 6.0)], closed=False, fill=False, ec=INK, lw=2.2))
    ax.add_patch(Rectangle((2.7, 1.8), 4.6, 2.6, color=WATER_FILL))
    # Stands lie on the bottom of the outer vessel and carry the bottom of the inner one
    ax.add_patch(Polygon([(3.1, 1.2), (3.7, 1.2), (3.55, 1.8), (3.25, 1.8)], color=METAL))
    ax.add_patch(Polygon([(6.3, 1.2), (6.9, 1.2), (6.75, 1.8), (6.45, 1.8)], color=METAL))
    ax.add_patch(Rectangle((4.7, 3.2), 0.5, 5.8, fc=PAPER, ec=HOT, lw=1.6))
    ax.add_patch(Rectangle((4.8, 3.2), 0.3, 1.2, color=HOT))
    ax.text(0.8, 8.4, "термометр", fontsize=10, ha="left")
    ax.annotate("", xy=(4.65, 8.3), xytext=(3.4, 8.4), arrowprops=dict(arrowstyle="->", color=INK))
    # Leaders touch the walls so each name is tied to its own vessel
    ax.text(0.1, 0.3, "внешний сосуд", fontsize=10)
    ax.plot([1.2, 1.9], [0.75, 1.2], color=GREY, lw=1)
    ax.text(0.2, 7.2, "внутренний сосуд", fontsize=10)
    ax.plot([1.6, 2.6], [7.05, 6.0], color=GREY, lw=1)
    ax.text(7.6, 7.1, "воздушная\nпрослойка", fontsize=9, ha="center", color=NOTE)
    # modern one
    ax = axs[1]
    ax.set_title("Современный")
    ax.add_patch(Rectangle((1.2, 1.2), 7.6, 5.4, fc=PAPER, ec=INK, lw=2.2))
    ax.add_patch(Rectangle((1.5, 1.5), 7.0, 4.8, fc=LIGHT, ec="none"))
    ax.add_patch(Rectangle((2.6, 2.0), 4.8, 4.6, fc=PAPER, ec=INK, lw=2.2))
    ax.add_patch(Rectangle((2.7, 2.0), 4.6, 2.6, color=WATER_FILL))
    ax.add_patch(Rectangle((1.0, 6.6), 8.0, 0.35, fc=METAL, ec=INK))
    # thermometer
    ax.add_patch(Rectangle((3.4, 3.0), 0.35, 5.6, fc=PAPER, ec=HOT, lw=1.6))
    ax.add_patch(Rectangle((3.45, 3.0), 0.25, 1.0, color=HOT))
    # heater
    xs = np.linspace(0, 1, 200)
    ax.plot(5.6 + 0.35 * np.sin(xs * 6 * np.pi), 2.4 + xs * 5.8, color=COIL, lw=2)
    ax.plot([5.6, 5.6], [8.2, 9.1], color=INK, lw=1.5)
    ax.plot([6.3, 6.3], [7.0, 9.1], color=INK, lw=1.5)
    ax.plot([5.6, 5.6], [2.4, 3.0], color=COIL, lw=2)
    ax.text(6.55, 8.7, "клеммы\nнагревателя", fontsize=9, va="center")
    # stirrer
    ax.plot([4.5, 4.5], [2.6, 8.8], color=GREEN, lw=2)
    ax.add_patch(Rectangle((4.2, 2.6), 0.6, 0.15, color=GREEN))
    ax.text(4.5, 9.3, "мешалка", fontsize=9, ha="left", color=GREEN)
    ax.text(3.2, 9.3, "термометр", fontsize=9, ha="right", color=HOT)
    ax.text(5.0, 0.55, "пенопластовая прослойка", fontsize=10, ha="center", color=NOTE)
    ax.text(9.0, 7.1, "крышка", fontsize=9, ha="right", va="bottom")
    save(fig, "heat-calorimeters.png")


# 8. task with three heating graphs (lesson 110)
def heating_graphs():
    fig, ax = axes_grid(6.4, 4.6)
    ax.plot([0, 10], [20, 70], color=HOT, lw=2.4)
    ax.plot([0, 10], [20, 40], color=COLD, lw=2.4)
    ax.plot([0, 1], [20, 70], color=GREEN, lw=2.4)
    ax.text(10.15, 70, "1", color=HOT, fontsize=12, va="center", fontweight="bold")
    ax.text(10.15, 40, "2", color=COLD, fontsize=12, va="center", fontweight="bold")
    ax.text(1.1, 68, "3", color=GREEN, fontsize=12, va="center", fontweight="bold")
    for x, y, col in ((10, 70, HOT), (10, 40, COLD), (1, 70, GREEN)):
        ax.plot([x], [y], "o", color=col, ms=6)
    ax.set_xlabel(r"$\tau$, мин")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, 11)
    ax.set_ylim(20, 75)
    ax.set_xticks(range(0, 11, 2))
    ax.set_yticks(range(20, 71, 10))
    ax.set_title("Три опыта с одним нагревателем")
    save(fig, "heat-task-three-liquids.png")


# 9. reading dt and tau off the graph
def heating_graphs_read():
    fig, ax = axes_grid(6.4, 4.6)
    ax.plot([0, 10], [20, 70], color=HOT, lw=2.4)
    ax.plot([0, 10], [20, 40], color=COLD, lw=2.4)
    ax.plot([0, 1], [20, 70], color=GREEN, lw=2.4)
    ax.annotate("", xy=(10.4, 70), xytext=(10.4, 20), arrowprops=dict(arrowstyle="<->", color=HOT))
    ax.text(10.55, 45, r"$\Delta t_1=50$", color=HOT, rotation=90, va="center", fontsize=10)
    ax.annotate("", xy=(9.6, 40), xytext=(9.6, 20), arrowprops=dict(arrowstyle="<->", color=COLD))
    ax.text(9.35, 30, r"$\Delta t_2=20$", color=COLD, rotation=90, va="center", ha="right", fontsize=10)
    ax.annotate("", xy=(1, 21), xytext=(0, 21), arrowprops=dict(arrowstyle="<->", color=GREEN))
    ax.text(1.3, 62, r"$\tau_3=1$ мин", color=GREEN, ha="left", fontsize=10)
    ax.axvline(10, color=GREY, lw=1, ls="--")
    ax.text(6.4, 22.4, r"$\tau_1=\tau_2=10$ мин", color=INK, ha="center", fontsize=10)
    ax.set_xlabel(r"$\tau$, мин")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, 11.6)
    ax.set_ylim(20, 75)
    ax.set_xticks(range(0, 11, 2))
    ax.set_yticks(range(20, 71, 10))
    ax.set_title("Что снимают с графика")
    save(fig, "heat-task-three-liquids-read.png")


# 10. bath: shares of heat
def bath_shares():
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    parts = [("ванна (сталь)", 3000, METAL), ("детали (медь)", 5100, COPPER), ("масло", 40800, OIL)]
    left = 0
    for i, (name, v, col) in enumerate(parts):
        ax.barh([0], [v], left=left, color=col, edgecolor=PAPER, height=0.55)
        label = f"{name}\n{num(v / 1000, 1)} МДж"
        if i == 2:
            ax.text(left + v / 2, 0, label, ha="center", va="center", fontsize=10, color=INK)
        else:
            ytxt = 0.55 if i == 0 else -0.55
            ax.annotate(label, xy=(left + v / 2, 0.27 * (1 if i == 0 else -1)), xytext=(left + v / 2 + (500 if i == 0 else 0), ytxt),
                        ha="left" if i == 0 else "center", va="center", fontsize=9,
                        arrowprops=dict(arrowstyle="-", color=GREY))
        left += v
    ax.set_xlim(0, left)
    ax.set_ylim(-0.9, 0.9)
    ax.set_yticks([])
    ax.set_xlabel(r"$Q$, кДж")
    ax.spines["left"].set_visible(False)
    ax.set_title("Куда пошли 48,9 МДж")
    save(fig, "heat-task-bath-shares.png")


# 11. flowing water through a heater
def pipe():
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.5, 1.5), 11, 1.6, fc=WATER_FILL_PALE, ec=INK, lw=2))
    ax.add_patch(Rectangle((3.3, 1.2), 2.4, 2.2, fc=HOT_FILL, ec=HOT, lw=2))
    ax.text(4.5, 3.75, "нагреватель $P$", ha="center", color=HOT, fontsize=11)
    ax.text(1.4, 0.95, r"$t_1=15$ °C", ha="center", fontsize=10)
    ax.text(10.4, 0.95, r"$t_2=35$ °C", ha="center", fontsize=10)
    ax.add_patch(Rectangle((7.4, 1.5), 3.4, 1.6, fc=WATER_FILL_DEEP, ec=COLD, lw=1.8, alpha=0.9))
    ax.annotate("", xy=(10.8, 4.0), xytext=(7.4, 4.0), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(9.1, 4.25, r"$v\tau$", ha="center", fontsize=12)
    ax.annotate("", xy=(11.6, 3.1), xytext=(11.6, 1.5), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(11.85, 2.3, r"$d$", va="center", fontsize=12)
    ax.add_patch(FancyArrowPatch((0.1, 2.3), (0.9, 2.3), arrowstyle="-|>", mutation_scale=16, color=COLD, lw=2))
    ax.text(6.0, 0.1, r"объём протёкшей воды $V=\frac{\pi d^2}{4}\,v\tau$", ha="center", fontsize=10)
    save(fig, "heat-task-flow-heater.png")


# 12. kettle heater: heating to a stationary temperature, then cooling
def stationary():
    fig, ax = axes_grid(6.6, 4.4)
    t0, tst, tau_c = 20, 78, 12.0
    x1 = np.linspace(0, tau_c, 200)
    y1 = t0 + (tst - t0) * (1 - np.exp(-x1 / 3.2))
    y_off = y1[-1]
    x2 = np.linspace(tau_c, 30, 200)
    y2 = t0 + (y_off - t0) * np.exp(-(x2 - tau_c) / 3.2)
    ax.plot(x1, y1, color=HOT, lw=2.4, label="нагрев")
    ax.plot(x2, y2, color=COLD, lw=2.4, label="после выключения")
    ax.axhline(100, color=GREY, ls="--", lw=1.2)
    ax.text(29.5, 101.5, "100 °C", ha="right", color=NOTE, fontsize=10)
    ax.axhline(tst, color=GRID, ls=":", lw=1)
    ax.axvline(tau_c, color=GREY, ls=":", lw=1)
    slope = -(y_off - t0) / 3.2
    xs = np.array([tau_c, tau_c + 5])
    ax.plot(xs, y_off + slope * (xs - tau_c), color=TANGENT, lw=1.8, ls="--", label="касательная")
    ax.text(0.5, t0 + 2, r"$t_{\mathrm{ком}}$", fontsize=10)
    ax.set_xlabel(r"$\tau$")
    ax.set_ylabel(r"$t$, °C")
    ax.set_xlim(0, 30)
    ax.set_ylim(15, 108)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc="center right", frameon=False)
    ax.set_title("Нагрев с потерями и остывание")
    ax.grid(False)
    save(fig, "heat-task-stationary-cooling.png")


# 13. Joule's experiment with a motor
def joule():
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((2.2, 0.8), 5.6, 4.0, fc=PAPER, ec=INK, lw=2.2))
    ax.add_patch(Rectangle((2.3, 0.8), 5.4, 2.6, color=WATER_FILL))
    ax.add_patch(Rectangle((3.6, 5.3), 2.0, 1.2, fc=LIGHT, ec=INK, lw=2))
    ax.text(4.6, 5.9, "двигатель\n$N=50$ Вт", ha="center", va="center", fontsize=9)
    ax.plot([4.6, 4.6], [1.6, 5.3], color=INK, lw=3)
    ax.add_patch(Rectangle((3.4, 1.5), 2.4, 0.2, color=GREEN))
    ax.add_patch(Rectangle((4.5, 1.1), 0.2, 1.0, color=GREEN))
    ax.add_patch(FancyArrowPatch((3.2, 2.4), (4.0, 2.7), connectionstyle="arc3,rad=-0.4", arrowstyle="->", color=GREEN, lw=1.6))
    ax.text(8.1, 2.1, "вода\n$2$ кг", fontsize=10, va="center")
    ax.text(5.0, 0.3, "калориметр", ha="center", fontsize=10)
    save(fig, "heat-task-joule-paddle.png")


if __name__ == "__main__":
    glass_pot()
    glass_pot_time()
    water_oil_sand()
    metals()
    masses()
    bars()
    sign()
    calorimeter()
    heating_graphs()
    heating_graphs_read()
    bath_shares()
    pipe()
    stationary()
    joule()
