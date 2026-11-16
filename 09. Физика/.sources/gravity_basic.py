"""Figures for the note "Сила тяжести" (course Физика 7-9, lesson 33).

Run: python3 gravity_basic.py
PNG files go to content/05. Силы/00. Вложения/, prefix gravity-*
"""
from forces_common import *
from theme import num

G = 9.8


def attraction():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-6.4, 6.4)
    ax.set_ylim(-2.2, 6.4)
    ax.add_patch(Circle((0, 0), 1.7, fc=tint(SKY, 0.6), ec=INK, lw=1.6))
    ax.text(0, 0, "Земля", ha="center", va="center", fontsize=12)
    th = np.linspace(0, np.pi, 200)
    ax.plot(5.2 * np.cos(th), 5.2 * np.sin(th), ls="--", color=GREY, lw=1.2)
    ax.add_patch(Circle((3.7, 3.65), 0.5, fc=LIGHT, ec=INK, lw=1.4))
    ax.text(4.4, 4.3, "Луна", fontsize=11.5)
    arrow(ax, (3.35, 3.3), (1.4, 1.4), color=FORCE, lw=2.6)
    ax.add_patch(Circle((0, 2.95), 0.27, fc=tint(RED, 0.3), ec=INK, lw=1.2))
    ax.text(0.55, 3.15, "яблоко", fontsize=11.5)
    arrow(ax, (0, 2.6), (0, 1.8), color=FORCE, lw=2.6)
    ax.set_title("Яблоко и Луна притягиваются к Земле", fontsize=12.5)
    ax = axes[1]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.3, 8.3)
    ax.set_ylim(-1.6, 5.4)
    ax.add_patch(Circle((1.0, 3.0), 0.5, fc=tint(RED, 0.3), ec=INK, lw=1.2))
    ax.text(1.0, 3.9, "яблоко", ha="center", fontsize=11)
    ax.add_patch(Rectangle((3.3, 2.7), 1.5, 0.6, fc=BLUE, ec=INK, lw=1.2))
    ax.text(4.05, 3.9, "человек", ha="center", fontsize=11)
    ax.add_patch(Rectangle((6.3, 2.85), 1.2, 0.3, fc=GOLD, ec=INK, lw=1.2))
    ax.text(6.9, 3.9, "ручка", ha="center", fontsize=11)
    arrow(ax, (1.6, 3.0), (3.2, 3.0), color=FORCE, lw=2.4, style="<|-|>")
    arrow(ax, (4.9, 3.0), (6.2, 3.0), color=FORCE, lw=2.4, style="<|-|>")
    ax.annotate("", (6.9, 2.6), (1.0, 2.5), arrowprops=dict(arrowstyle="<|-|>", color=FORCE, lw=2.4, connectionstyle="arc3,rad=0.35"))
    ax.text(4.0, 0.4, "Любые два тела притягиваются\nдруг к другу: действие всегда взаимно", ha="center", fontsize=11.5)
    ax.set_title("Всемирное тяготение", fontsize=12.5)
    fig.tight_layout()
    save(fig, "gravity-attraction.png")


def air_drag():
    fig, axes = blank_row(4, 14, 4.8, (-2.2, 2.2), (-3.0, 4.4))
    titles = ["Лист плашмя\nи блокнот", "Лист ребром\nи блокнот", "Лист ребром и блокнот:\nкадры через равные\nпромежутки времени", "Шар и перо в камере\nбез воздуха"]
    for ax, t in zip(axes, titles):
        ax.set_title(t, fontsize=11.5)
        ax.plot([-2.0, 2.0], [-2.7, -2.7], color=GREY, lw=2)
    ax = axes[0]
    ax.add_patch(Rectangle((-1.8, 1.9), 1.5, 0.05, fc=GOLD, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.3, 1.5), 1.2, 0.5, fc=BLUE, ec=INK, lw=1.4))
    arrow(ax, (-1.05, 1.9), (-1.05, 0.7), color=FORCE, lw=2.4)
    arrow(ax, (-0.55, 1.6), (-0.55, 2.7), color=GREY, lw=2.4)
    ax.text(-1.05, 3.05, "сопротивление\nвоздуха", ha="center", fontsize=9.5, color=NOTE)
    arrow(ax, (0.9, 1.5), (0.9, -0.5), color=FORCE, lw=2.4)
    ax.text(-1.05, -0.3, "лист отстаёт", ha="center", fontsize=10.5)
    ax = axes[1]
    ax.add_patch(Rectangle((-1.2, 1.5), 0.05, 0.9, fc=GOLD, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.3, 1.5), 1.2, 0.5, fc=BLUE, ec=INK, lw=1.4))
    arrow(ax, (-1.17, 1.5), (-1.17, 0.7), color=FORCE, lw=2.4)
    arrow(ax, (0.9, 1.5), (0.9, -0.5), color=FORCE, lw=2.4)
    ax.text(0, -0.9, "падают одинаково", ha="center", fontsize=10.5)
    ax = axes[2]
    for xx, yy in ((-1.2, 1.5), (0.3, 1.5)):
        pass
    ax.add_patch(Rectangle((-1.2, 0.0), 0.05, 0.9, fc=GOLD, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((0.3, 0.0), 1.2, 0.5, fc=BLUE, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((-1.2, 1.7), 0.05, 0.9, fc=GOLD, ec=INK, lw=1.4, alpha=0.35))
    ax.add_patch(Rectangle((0.3, 1.7), 1.2, 0.5, fc=BLUE, ec=INK, lw=1.4, alpha=0.35))
    arrow(ax, (0, 3.3), (0, 2.8), color=GREY, lw=1.5)
    ax.text(0, -1.5, "в каждый момент на одной\nвысоте", ha="center", fontsize=10.5)
    ax = axes[3]
    ax.add_patch(Rectangle((-1.9, -2.7), 3.8, 6.5, fc="none", ec=INK, lw=1.6, ls="--"))
    ax.add_patch(Circle((-0.9, 2.9), 0.32, fc=STONE, ec=INK, lw=1.4))
    ax.add_patch(Ellipse((0.9, 2.9), 0.9, 0.22, fc=tint(WARM, 0.4), ec=INK, lw=1.2))
    arrow(ax, (-0.9, 2.5), (-0.9, 0.0), color=FORCE, lw=3.0)
    arrow(ax, (0.9, 2.55), (0.9, 1.3), color=FORCE, lw=1.4)
    ax.text(0, -1.2, "одна и та же высота\nв любой момент", ha="center", fontsize=10.5)
    fig.text(0.5, 0.0, "Разная сила тяжести, но одинаковое падение, когда воздух не мешает", ha="center", fontsize=12.5)
    save(fig, "gravity-air-drag.png")


def velocity_time():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    t = np.linspace(0, 4, 50)
    ax.plot(t, G * t, color=BLUE, lw=6, alpha=0.4, label="гиря 1 кг")
    ax.plot(t, G * t, color=FORCE, lw=2, ls="--", label="гирька 20 г")
    for k in range(5):
        ax.plot([k], [G * k], "o", color=INK, ms=6, zorder=5)
    for k in range(1, 5):
        ax.annotate("", (k, G * k), (k - 1, G * (k - 1)), arrowprops=dict(arrowstyle="-", color="none"))
        ax.text(k + 0.05, G * k - 3.2, rf"$+{num(G, None, math=True)}$", fontsize=9.5, color=INK)
    ax.set(xlabel=r"$t$, с", ylabel=r"$v$, м/с", xlim=(0, 4.2), ylim=(0, 43))
    ax.set_title("Скорость свободно падающих тел")
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "gravity-velocity-time.png")


def force_mass():
    fig, ax = plt.subplots(figsize=(7.4, 5))
    m = np.linspace(0, 32, 50)
    ax.plot(m, 9.8 * m, color=BLUE, lw=2.4, label=r"$g=9{,}8\ \mathrm{Н/кг}$")
    ax.plot(m, 10 * m, color=FORCE, lw=1.8, ls="--", label=r"$g=10\ \mathrm{Н/кг}$ (в задачах)")
    pts = ((1, 9.8, "гиря 1 кг", (2.6, 4)), (12, 120, "ведро воды 12 кг", (13.2, 92)), (30, 300, "болванка 30 кг", (24.0, 262)))
    for mm, F, txt, pos in pts:
        ax.plot([mm], [F], "o", color=INK, ms=7, zorder=5)
        ax.text(pos[0], pos[1], txt, fontsize=10.5)
    ax.plot([20, 25, 25], [196, 196, 245], color=GREY, lw=1.2)
    ax.text(22.5, 172, r"$\Delta m=5\ \mathrm{кг}$", fontsize=10, color=INK, ha="center")
    ax.text(25.4, 218, r"$\Delta F=49\ \mathrm{Н}$", fontsize=10, color=INK)
    ax.set(xlabel=r"$m$, кг", ylabel=r"$F_\mathrm{тяж}$, Н", xlim=(0, 32), ylim=(0, 330))
    ax.set_title("Сила тяжести пропорциональна массе")
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "gravity-force-mass.png")


def planets():
    data = [("Луна", 1.62), ("Меркурий", 3.70), ("Марс", 3.71), ("Венера", 8.87), ("Земля", 9.81), ("Сатурн", 10.4), ("Юпитер", 24.8)]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    xs = range(len(data))
    cols = [BLUE if n == "Земля" else NOTE for n, _ in data]
    ax.bar(xs, [v for _, v in data], color=cols, width=0.62)
    for i, (n, v) in enumerate(data):
        ax.text(i, v + 0.5, num(v, None), ha="center", fontsize=10.5)
    ax.set_xticks(list(xs), [n for n, _ in data])
    ax.set(ylabel=r"$g$, Н/кг", ylim=(0, 28))
    ax.set_title("Ускорение свободного падения у поверхности")
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    save(fig, "gravity-g-planets.png")


def inertia_compensation():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    m = np.linspace(0, 4, 20)
    ax = axes[0]
    ax.plot(m, G * m, color=FORCE, lw=2.4, label=r"сила тяжести $F=mg$")
    ax.plot(m, 2.5 * m, color=BLUE, lw=2.4, label="инертность (растёт вместе с массой)")
    ax.set(xlabel=r"$m$, кг", xlim=(0, 4), ylim=(0, 42))
    ax.set_yticks([])
    ax.set_title("Обе величины растут вместе с массой", fontsize=11.5)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    ax.grid(color=GRID)
    ax = axes[1]
    ms = np.array([0.5, 1, 2, 4])
    ax.plot(ms, np.full_like(ms, G), "o-", color=GREEN, lw=2.4, ms=8)
    ax.set(xlabel=r"$m$, кг", ylabel=r"$F/m=g$, Н/кг", xlim=(0, 4.4), ylim=(0, 14))
    ax.set_title("Отношение остаётся одним и тем же", fontsize=11.5)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "gravity-inertia-compensation.png")


def plumb():
    fig, ax = blank(6.2, 5.6, (-3.0, 3.4), (-4.4, 3.6))
    ax.plot([-3.0, 3.4], [-3.9, -3.9], color=GREY, lw=2)
    ax.add_patch(Rectangle((1.4, -3.9), 0.7, 7.1, fc=WOOD, ec=INK, lw=1.4, alpha=0.6))
    ax.text(1.75, 3.35, "стена", ha="center", fontsize=10.5)
    ax.plot([-0.8, 0.4], [3.2, 3.2], color=INK, lw=4)
    ax.plot([-0.2, -0.2], [3.2, -0.6], color=INK, lw=1.4)
    ax.add_patch(Polygon([(-0.2, -0.2), (-0.55, -1.1), (0.15, -1.1)], fc=STONE, ec=INK, lw=1.4))
    ax.text(-0.9, -0.7, "отвес", ha="right", fontsize=11)
    arrow(ax, (-0.2, -0.9), (-0.2, -3.4), color=FORCE, lw=3.0, scale=16)
    ax.text(0.15, -2.3, r"$\vec F_\mathrm{тяж}$", color=FORCE, fontsize=14)
    ax.text(-1.0, 1.4, "нить вертикальна:\nсила тяжести\nнаправлена вниз", ha="right", fontsize=10.5)
    save(fig, "gravity-plumb.png")


def earth_oblate():
    fig, ax = blank(8.4, 5.6, (-4.6, 5.2), (-3.4, 3.7))
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(2.3 * np.cos(th), 2.3 * np.sin(th), ls="--", color=GREY, lw=1.3)
    a, b = 2.6, 2.3
    ax.add_patch(Ellipse((0, 0), 2 * a, 2 * b, fc=tint(SKY, 0.8), ec=INK, lw=2))
    ax.plot([0, 0], [-3.2, 3.2], ls="-.", color=GREY, lw=1.2)
    ax.text(0.1, 3.3, "ось вращения", fontsize=10.5)
    arrow(ax, (0, 0), (a, 0), color=INK, lw=1.8)
    arrow(ax, (0, 0), (0, b), color=INK, lw=1.8)
    ax.text(1.3, -0.3, r"$R_\mathrm{э}$", fontsize=14, ha="center")
    ax.text(0.3, 1.1, r"$R_\mathrm{п}$", fontsize=14)
    ax.text(3.0, 0.7, r"$R_\mathrm{э}-R_\mathrm{п}\approx 21\ \mathrm{км}$", fontsize=12)
    ax.text(-4.4, -3.1, "Форма преувеличена: как мандарин, а не как лимон", fontsize=11)
    arrow(ax, (-0.6, 2.95), (-0.6, 2.2), color=FORCE, lw=2.4)
    arrow(ax, (3.3, -0.9), (2.45, -0.9), color=FORCE, lw=2.4)
    ax.text(-0.85, 2.8, "полюс", ha="right", fontsize=11)
    ax.text(3.4, -1.0, "экватор", fontsize=11)
    save(fig, "gravity-earth-oblate.png")


def centers():
    fig, axes = blank_row(4, 13, 3.9, (-2.0, 2.0), (-3.3, 2.3))
    dot = dict(color=INK, ms=7, zorder=6)
    ax = axes[0]
    ax.add_patch(Circle((0, 0), 1.5, fc=LIGHT, ec=INK, lw=1.6))
    ax.plot([0], [0], "o", **dot)
    arrow(ax, (0, 0), (0, -2.6), color=FORCE, lw=2.8)
    ax.set_title("Шар", fontsize=11.5)
    ax = axes[1]
    ax.add_patch(Rectangle((-1.3, -1.0), 2.6, 2.0, fc=LIGHT, ec=INK, lw=1.6))
    ax.plot([-1.3, 1.3], [-1.0, 1.0], color=GREY, lw=1)
    ax.plot([-1.3, 1.3], [1.0, -1.0], color=GREY, lw=1)
    ax.plot([0], [0], "o", **dot)
    arrow(ax, (0, 0), (0, -2.6), color=FORCE, lw=2.8)
    ax.set_title("Параллелепипед", fontsize=11.5)
    ax = axes[2]
    ax.add_patch(Rectangle((-1.9, -0.12), 3.8, 0.24, fc=LIGHT, ec=INK, lw=1.6))
    ax.plot([0], [0], "o", **dot)
    arrow(ax, (0, 0), (0, -2.6), color=FORCE, lw=2.8)
    ax.set_title("Стержень", fontsize=11.5)
    ax = axes[3]
    P = np.array([[-1.7, -1.0], [1.7, -1.0], [0.4, 1.6]])
    ax.add_patch(Polygon(P, fc=LIGHT, ec=INK, lw=1.6))
    for i in range(3):
        mid = (P[(i + 1) % 3] + P[(i + 2) % 3]) / 2
        ax.plot([P[i][0], mid[0]], [P[i][1], mid[1]], color=GREY, lw=1.2)
    c = P.mean(axis=0)
    ax.plot([c[0]], [c[1]], "o", **dot)
    arrow(ax, (c[0], c[1]), (c[0], -2.6), color=FORCE, lw=2.8)
    ax.set_title("Пластина-треугольник", fontsize=11.5)
    fig.text(0.5, 0.02, r"Сила тяжести $\vec F_\mathrm{тяж}$ приложена к центру тяжести (ц. т.)", ha="center", fontsize=12.5)
    save(fig, "gravity-centers.png")


def steel_chain():
    fig, ax = blank(11.5, 2.9, (0, 14.6), (0, 3.6))
    boxes = [(0.2, "Дано:", r"$V=20\ \mathrm{дм^3}=0{,}02\ \mathrm{м^3}$" "\n" r"$\rho=7800\ \mathrm{кг/м^3}$"),
             (4.8, "Масса", r"$m=\rho V=156\ \mathrm{кг}$"),
             (9.5, "Сила тяжести", r"$F=mg=156\cdot 10=1560\ \mathrm{Н}$")]
    for x, head, body in boxes:
        ax.add_patch(Rectangle((x, 0.6), 4.0 if x < 9 else 4.9, 2.3, fc=LIGHT, ec=INK, lw=1.4))
        ax.text(x + 0.2, 2.6, head, fontsize=11, weight="bold", va="top")
        ax.text(x + 0.2, 1.4, body, fontsize=11.5, va="center")
    arrow(ax, (4.3, 1.75), (4.75, 1.75), lw=2)
    arrow(ax, (8.9, 1.75), (9.45, 1.75), lw=2)
    save(fig, "gravity-steel-chain.png")


def direction_earth():
    fig, ax = blank(6, 6, (-4.0, 4.0), (-4.0, 4.0))
    ax.add_patch(Circle((0, 0), 1.8, fc=tint(SKY, 0.6), ec=INK, lw=1.6))
    ax.text(0, 0, "Земля", ha="center", va="center", fontsize=12)
    for ang in range(0, 360, 45):
        r = np.radians(ang)
        p = np.array([np.cos(r), np.sin(r)])
        ax.add_patch(Circle(p * 2.5, 0.16, fc=tint(RED, 0.3), ec=INK, lw=1.0))
        arrow(ax, tuple(p * 2.3), tuple(p * 1.85), color=FORCE, lw=2.2, scale=12)
    ax.text(0, -3.7, "Сила тяжести всюду направлена вертикально вниз", ha="center", fontsize=11.5)
    save(fig, "gravity-direction-earth.png")


if __name__ == "__main__":
    attraction()
    air_drag()
    velocity_time()
    force_mass()
    planets()
    inertia_compensation()
    plumb()
    earth_oblate()
    centers()
    steel_chain()
    direction_earth()
