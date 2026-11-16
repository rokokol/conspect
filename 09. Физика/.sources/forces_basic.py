"""Figures for the note "Сила" (course Физика 7-9, lesson 32).

Run: python3 forces_basic.py
PNG files go to content/05. Силы/00. Вложения/, prefix force-*
"""
from forces_common import *


def same_change():
    fig, axes = blank_row(5, 15, 2.9, (-0.3, 4.6), (-1.6, 2.6))
    names = ["палец", "пружина", "магнит", "нитка", "ветер"]
    for ax, name in zip(axes, names):
        cart(ax, 2.0, 0.6, w=1.9, h=0.7)
        arrow(ax, (2.6, 1.75), (3.9, 1.75), color=BLUE, lw=2.2)
        ax.text(3.25, 2.1, r"$\Delta v$", ha="center", color=BLUE, fontsize=12)
        ax.text(1.0, 2.2, name, ha="center", fontsize=12, weight="bold")
        ax.text(2.95, -0.85, r"$\Delta v = 2\ \mathrm{м/с}$", ha="center", fontsize=11, color=BLUE)
        ax.text(2.95, -1.35, "за 1 с", ha="center", fontsize=10, color=INK)
    ax = axes[0]
    ax.add_patch(Ellipse((0.9, 0.95), 0.7, 0.45, fc=tint(WARM, 0.4), ec=INK, lw=1.2))
    arrow(ax, (1.3, 0.95), (1.95, 0.95), color=FORCE, lw=2.2)
    ax = axes[1]
    xs = np.linspace(0.5, 1.95, 40)
    ys = 0.95 + 0.22 * np.sin(np.linspace(0, 6 * np.pi, 40))
    ax.plot(xs, ys, color=INK, lw=1.6)
    ax.plot([0.5, 0.5], [0.6, 1.3], color=INK, lw=3)
    ax = axes[2]
    ax.add_patch(Rectangle((0.3, 0.7), 0.5, 0.5, fc=tint(BLUE, 0.6), ec=INK, lw=1.2))  # the north pole is blue
    ax.add_patch(Rectangle((0.8, 0.7), 0.5, 0.5, fc=tint(RED, 0.6), ec=INK, lw=1.2))  # the south pole is red
    ax.text(0.55, 0.95, "N", color=INK, ha="center", va="center", fontsize=9)
    ax.text(1.05, 0.95, "S", color=INK, ha="center", va="center", fontsize=9)
    arrow(ax, (1.4, 0.95), (1.95, 0.95), color=FORCE, lw=2.2)
    ax = axes[3]
    ax.plot([0.5, 2.0], [0.95, 0.95], color=INK, lw=1.4)
    ax.add_patch(Circle((0.5, 0.95), 0.1, fc=INK))
    arrow(ax, (0.6, 0.95), (1.2, 0.95), color=FORCE, lw=2.2)
    ax = axes[4]
    for dy in (-0.2, 0, 0.2):
        arrow(ax, (0.2, 0.95 + dy), (1.3, 0.95 + dy), color=GREY, lw=1.8)
    arrow(ax, (1.35, 0.95), (1.95, 0.95), color=FORCE, lw=2.2)
    fig.text(0.5, 0.0, "Скорость тележки меняется одинаково: значит, все эти тела действуют на неё с одной и той же силой",
             ha="center", fontsize=12)
    save(fig, "force-same-change.png")


def proportionality():
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.9), gridspec_kw={"width_ratios": [1, 1, 1.05]})
    t = np.linspace(0, 6, 50)
    ax = axes[0]
    for F, c in ((1, NOTE), (2, BLUE), (3, FORCE)):
        ax.plot(t, F * t, color=c, lw=2.2, label=rf"$F={F}\ \mathrm{{Н}}$")
    ax.set(xlabel=r"$t$, с", ylabel=r"$m\,\Delta v$, кг·м/с", xlim=(0, 6), ylim=(0, 18))
    ax.set_title("Больше сила, круче прямая")
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    ax = axes[1]
    for m, c in ((1, FORCE), (2, BLUE), (4, NOTE)):
        ax.plot(t, 4 * t / m, color=c, lw=2.2, label=rf"$m={m}\ \mathrm{{кг}}$")
    ax.set(xlabel=r"$t$, с", ylabel=r"$\Delta v$, м/с", xlim=(0, 6), ylim=(0, 24))
    ax.set_title(r"Сила $4\ \mathrm{Н}$, разные массы")
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    ax = axes[2]
    labels = [r"$m=1,\ \Delta v=1$", r"$m=1,\ \Delta v=2$", r"$m=2,\ \Delta v=1$"]
    vals = [1, 2, 2]
    ax.bar(range(3), vals, color=[NOTE, FORCE, FORCE], width=0.6)
    ax.set_xticks(range(3), labels, fontsize=9.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.06, rf"$F\sim{v}$", ha="center", fontsize=11)
    ax.set(ylabel=r"$m\,\Delta v$ за одно время", ylim=(0, 2.6))
    ax.set_title("Сила растёт с массой и с изменением скорости", fontsize=11)
    fig.tight_layout()
    save(fig, "force-proportionality.png")


def newton_definition():
    fig, ax = blank(12, 5.4, (-1, 13.2), (-1.0, 7.4))
    rows = [(0, 0.0), (1, 0.5), (2, 2.0), (3, 4.5)]
    for k, (t, x) in enumerate(rows):
        y = 5.6 - 1.75 * k
        xx = x * 1.9
        ax.plot([-0.6, 12.4], [y - 0.18, y - 0.18], color=GREY, lw=1)
        cart(ax, xx, y, w=1.3, h=0.55)
        ax.text(-0.95, y + 0.3, rf"$t={t}\ \mathrm{{с}}$", ha="right", va="center", fontsize=11.5)
        arrow(ax, (xx + 1.3, y + 0.28), (xx + 1.3 + 0.9, y + 0.28), color=FORCE, lw=2.6)
        ax.text(xx + 1.3 + 0.45, y + 0.68, r"$1\ \mathrm{Н}$", color=FORCE, ha="center", fontsize=10.5)
        if t:
            arrow(ax, (xx + 0.65, y + 1.0), (xx + 0.65 + 0.7 * t, y + 1.0), color=BLUE, lw=2.4)
        ax.text(xx + 0.65 + 0.7 * t + 0.15, y + 1.0, rf"$v={t}\ \mathrm{{м/с}}$", color=BLUE, va="center", fontsize=11)
    ax.text(5.8, 6.95, "Тележка массой 1 кг под действием силы 1 Н", ha="center", fontsize=13, weight="bold")
    ax.text(5.8, -0.55, "Каждую секунду скорость растёт на 1 м/с", ha="center", fontsize=12)
    save(fig, "force-newton-definition.png")


def prefixes():
    fig, ax = plt.subplots(figsize=(11.5, 3.6))
    ax.set_xlim(-6.8, 6.8)
    ax.set_ylim(-1.6, 2.6)
    ax.axis("off")
    ax.plot([-6.5, 6.5], [0, 0], color=INK, lw=2)
    names = {-6: "мкН", -3: "мН", 0: "Н", 3: "кН", 6: "МН"}
    for p, n in names.items():
        ax.plot([p, p], [-0.15, 0.15], color=INK, lw=2)
        ax.text(p, -0.5, n, ha="center", fontsize=13, weight="bold")
        ax.text(p, -1.0, rf"$10^{{{p}}}\ \mathrm{{Н}}$", ha="center", fontsize=11, color=INK)
    for p in range(-6, 7):
        if p not in names:
            ax.plot([p, p], [-0.07, 0.07], color=GREY, lw=1)
    ax.plot([np.log10(9.8)], [0], "o", color=BLUE, ms=9)
    ax.annotate("Сила тяжести гири 1 кг:\nоколо 9,8 Н", (np.log10(9.8), 0.05), (0.5, 1.5), ha="center", color=BLUE,
                fontsize=11, arrowprops=dict(arrowstyle="-", color=BLUE))
    ax.plot([6], [0], "o", color=FORCE, ms=9)
    ax.annotate("Снаряд в орудии\n(порядка МН)", (6, 0.05), (5.6, 1.5), ha="center", color=FORCE, fontsize=11,
                arrowprops=dict(arrowstyle="-", color=FORCE))
    ax.plot([-6], [0], "o", color=GREEN, ms=9)
    ax.annotate("Доли микроньютона и\nмикроньютоны: очень слабые силы", (-6, 0.05), (-4.3, 1.5), ha="center", color=GREEN,
                fontsize=11, arrowprops=dict(arrowstyle="-", color=GREEN))
    ax.text(0, 2.4, "Кратные и дольные единицы силы (логарифмическая шкала)", ha="center", fontsize=12.5, weight="bold")
    save(fig, "force-prefixes.png")


def third_law():
    fig, ax = blank(11, 4.4, (-1.2, 10.2), (-0.7, 4.3))
    cart(ax, 3.1, 1.0, w=1.7, h=0.7)
    cart(ax, 5.2, 1.0, w=1.7, h=0.7, load=0.55)
    ax.plot([4.8, 5.2], [1.35, 1.35], color=INK, lw=2.4)
    ax.text(3.95, 2.0, r"$m_1$", ha="center", fontsize=12)
    ax.text(6.05, 2.45, r"$m_2$", ha="center", fontsize=12)
    # forces
    arrow(ax, (4.0, 0.55 - 0.1), (2.2, 0.55 - 0.1), color=FORCE, lw=3.2, scale=16)
    arrow(ax, (6.05, 0.55 - 0.1), (7.85, 0.55 - 0.1), color=FORCE, lw=3.2, scale=16)
    ax.text(3.0, 0.05, r"$\vec F_1$ (на 1-е тело)", ha="center", color=FORCE, fontsize=11.5)
    ax.text(7.0, 0.05, r"$\vec F_2$ (на 2-е тело)", ha="center", color=FORCE, fontsize=11.5)
    ax.text(5.0, -0.5, r"$|\vec F_1|=|\vec F_2|,\quad \vec F_1\uparrow\downarrow\vec F_2$", ha="center", fontsize=12.5)
    # velocities
    arrow(ax, (3.9, 3.3), (2.0, 3.3), color=BLUE, lw=2.2)
    arrow(ax, (6.1, 3.3), (7.1, 3.3), color=BLUE, lw=2.2)
    ax.text(2.9, 3.65, r"$\vec v_1$", color=BLUE, ha="center", fontsize=12)
    ax.text(6.6, 3.65, r"$\vec v_2$", color=BLUE, ha="center", fontsize=12)
    ax.text(5.0, 4.2, r"$m_1\Delta v_1 / t = -\,m_2 \Delta v_2 / t$", ha="center", fontsize=12.5)
    save(fig, "force-third-law.png")


def point_of_application():
    fig, axes = blank_row(2, 11, 4.4, (-2.2, 4.2), (-0.7, 5.6))
    for ax, top in zip(axes, (True, False)):
        ax.plot([-2, 4], [0, 0], color=GREY, lw=2)
        if top:
            ax.add_patch(Rectangle((0, 0), 1.2, 3.2, fc=WOOD, ec=INK, lw=1.4, alpha=0.35, ls="--"))
            # pushed right at the top, the box turns clockwise about its bottom right edge
            tilt = matplotlib.transforms.Affine2D().rotate_deg_around(1.2, 0, -25) + ax.transData
            ax.add_patch(Rectangle((0, 0), 1.2, 3.2, fc=WOOD, ec=INK, lw=1.4, transform=tilt))
            arrow(ax, (-1.6, 3.0), (-0.1, 3.0), color=FORCE, lw=3)
            ax.add_patch(Arc((1.45, 1.6), 1.0, 1.0, theta1=-30, theta2=60, color=BLUE, lw=2))
            ax.set_title("Сила у верхнего края: тело опрокидывается", fontsize=12)
        else:
            ax.add_patch(Rectangle((0.0, 0), 1.2, 3.2, fc=WOOD, ec=INK, lw=1.4, alpha=0.35, ls="--"))
            ax.add_patch(Rectangle((1.4, 0), 1.2, 3.2, fc=WOOD, ec=INK, lw=1.4))
            arrow(ax, (-1.6, 0.5), (-0.1, 0.5), color=FORCE, lw=3)
            arrow(ax, (0.75, 3.5), (2.05, 3.5), color=BLUE, lw=2)
            ax.set_title("Сила у основания: тело скользит по столу", fontsize=12)
        ax.text(-0.85, 3.5 if top else 0.9, r"$\vec F$", color=FORCE, fontsize=13, ha="center")
    fig.text(0.5, 0.03, "Одна и та же сила по модулю и по направлению, разные точки приложения", ha="center", fontsize=12)
    save(fig, "force-point-of-application.png")


def vector_scale():
    fig, ax = blank(7.2, 5.6, (-1.2, 6.0), (-1.4, 8.2))
    ax.add_patch(Rectangle((1.0, 0), 4.0, 7.0, fc=WOOD, ec=INK, lw=1.6, alpha=0.5))
    ax.plot([-0.4, 6.0], [0, 0], color=GREY, lw=2)
    ax.plot([1.0, 1.0], [0, 5.0], ls=":", color=GREY, lw=1)
    dim_bar(ax, (0.55, 0), (0.55, 5.0), "5 см", off=(-0.5, 0), fs=10.5)
    ax.plot([1.0], [5.0], "o", color=INK, ms=6)
    ax.text(0.7, 5.3, "A", fontsize=13, ha="right", weight="bold")
    arrow(ax, (1.0, 5.0), (3.0, 5.0), color=FORCE, lw=3.4, scale=18)
    ax.text(2.0, 5.5, r"$\vec F$", color=FORCE, fontsize=16, ha="center")
    ax.text(4.05, 5.0, r"$F=2\ \mathrm{Н}$", fontsize=12, va="center", ha="left")
    # scale
    ax.plot([0.2, 1.2], [-0.95, -0.95], color=INK, lw=2.6)
    ax.plot([0.2, 0.2], [-0.85, -1.05], color=INK, lw=2)
    ax.plot([1.2, 1.2], [-0.85, -1.05], color=INK, lw=2)
    ax.text(1.5, -0.95, r"масштаб: $1\ \mathrm{Н}\leftrightarrow 1\ \mathrm{см}$", va="center", fontsize=11.5)
    for x in (2.0, 3.0):
        ax.plot([x, x], [4.9, 5.1], color=INK, lw=1.2)
    ax.text(3.0, 4.55, "2 см", ha="center", fontsize=10.5)
    save(fig, "force-vector-scale.png")


def vectors_compare():
    fig, axes = blank_row(2, 11, 4.6, (-0.5, 6.2), (-0.8, 5.4))
    ax = axes[0]
    ax.set_title("Одна величина, разные направления", fontsize=12)
    ang = [0, 45, 90, 180]
    for a, c in zip(ang, (FORCE, BLUE, GREEN, VIOLET)):
        r = 2.0
        ax.arrow(0.5, 2.4, 0, 0, alpha=0)
        arrow(ax, (2.8, 2.4), (2.8 + r * np.cos(np.radians(a)), 2.4 + r * np.sin(np.radians(a))), color=c, lw=3)
    ax.plot([2.8], [2.4], "o", color=INK, ms=7)
    ax.text(2.8, 0.3, r"все $|\vec F|=2\ \mathrm{Н}$", ha="center", fontsize=11.5)
    ax = axes[1]
    ax.set_title("Одно направление, разные модули", fontsize=12)
    for i, (F, c) in enumerate(((1, VIOLET), (2, BLUE), (3, GREEN), (4, FORCE))):
        y = 4.2 - i * 1.05
        ax.plot([0.2], [y], "o", color=INK, ms=7)
        arrow(ax, (0.2, y), (0.2 + F, y), color=c, lw=3)
        ax.text(0.2 + F + 0.15, y, rf"${F}\ \mathrm{{Н}}$", va="center", fontsize=11.5)
    ax.plot([0.2, 1.2], [0.0, 0.0], color=INK, lw=2.6)
    ax.text(1.5, 0.0, r"$1\ \mathrm{Н}\leftrightarrow 1\ \mathrm{см}$", va="center", fontsize=11)
    save(fig, "force-vectors-compare.png")


def stone_on_ground():
    fig, ax = blank(6.2, 6.2, (-2.4, 4.4), (-6.6, 2.4))
    ax.add_patch(Rectangle((-2.3, -6.0), 6.6, 6.0, fc=EARTH, ec="none", alpha=0.25))
    ax.plot([-2.3, 4.3], [0, 0], color=INK, lw=2)
    ax.add_patch(Ellipse((1.0, 0.75), 2.3, 1.5, fc=STONE, ec=INK, lw=1.6))
    ax.text(1.0, 0.75, "камень", ha="center", va="center", fontsize=11, color=PAPER)
    ax.plot([1.0], [0], "o", color=INK, ms=7, zorder=5)
    arrow(ax, (1.0, 0), (1.0, -5.0), color=FORCE, lw=3.4, scale=18)
    for k in range(1, 6):
        ax.plot([0.85, 1.15], [-k, -k], color=INK, lw=1.3)
    ax.text(1.35, -2.5, r"$\vec F$", color=FORCE, fontsize=16, va="center")
    ax.text(-2.1, -5.7, "Земля", fontsize=11, color=EARTH, weight="bold")
    ax.plot([-1.8, -1.8], [-1.0, -2.0], color=INK, lw=2.6)
    ax.plot([-1.9, -1.7], [-1.0, -1.0], color=INK, lw=2)
    ax.plot([-1.9, -1.7], [-2.0, -2.0], color=INK, lw=2)
    ax.text(-1.6, -1.5, r"$10\ \mathrm{Н}$" "\n" r"$=1\ \mathrm{см}$", va="center", fontsize=10.5)
    ax.text(2.0, -5.0, r"$F=50\ \mathrm{Н}$", va="center", fontsize=12)
    save(fig, "force-stone-on-ground.png")


def deformation():
    fig, ax = blank(9.5, 5.2, (-1.0, 9.4), (-5.6, 2.4))
    x = np.linspace(0, 7, 60)
    ax.plot(x, np.zeros_like(x), color=GREY, lw=6, alpha=0.5, solid_capstyle="round")
    y = -0.055 * x**2
    ax.plot(x, y, color=INK, lw=6, solid_capstyle="round")
    ax.plot([-0.4, -0.4], [-1.0, 1.0], color=INK, lw=4)
    for xi in (1.5, 3.0, 4.5, 6.0, 7.0):
        yi = -0.055 * xi**2
        arrow(ax, (xi, yi - 0.15), (xi, yi - 0.15 - 0.22 * xi), color=BLUE, lw=2.2)
    arrow(ax, (7.5, 1.9), (7.5, 0.7), color=FORCE, lw=3.4, scale=16)
    ax.text(7.75, 1.2, r"$\vec F$", color=FORCE, fontsize=15)
    ax.text(3.4, -5.1, "Точки тела меняют скорость по-разному: тело деформируется", ha="center", fontsize=12)
    ax.text(0.3, 1.15, "закреплено", fontsize=10.5, color=INK)
    ax.text(2.2, -3.3, r"синие стрелки — скорости точек", color=BLUE, fontsize=11, ha="center")
    save(fig, "force-deformation-velocities.png")


if __name__ == "__main__":
    same_change()
    proportionality()
    newton_definition()
    prefixes()
    third_law()
    point_of_application()
    vector_scale()
    vectors_compare()
    stone_on_ground()
    deformation()
