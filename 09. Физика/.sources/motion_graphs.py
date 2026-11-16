"""Figures for the note "Графики движения" (lessons 18 and 19).

Run:
  nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages(ps: [ps.matplotlib ps.numpy]))]' -c python3 motion_graphs.py
The PNG files go to content/03. Механическое движение/00. Вложения/.
"""


import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

from course import COURSE
OUT = COURSE / "content" / "03. Механическое движение" / "00. Вложения"

from theme import ASH, BLUE, COPPER, GREEN, INK, MUTED, PAPER, RED, SKY, VIOLET, keep_dots, saver, tint

C1 = BLUE  # body 1, path (the figures were blue here before, so the notes' wording holds)
C2 = RED  # body 2 and the highlighted point
C3 = GREEN  # third series
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text


_save = saver(OUT)


def save(fig, name):
    _save(fig, name, bbox_inches="tight", pad_inches=0.15)


def arrows(ax, xlabel, ylabel):
    ax.plot(1, 0, ">", color=INK, transform=ax.get_yaxis_transform(), clip_on=False, ms=6)
    ax.plot(0, 1, "^", color=INK, transform=ax.get_xaxis_transform(), clip_on=False, ms=6)
    ax.annotate(xlabel, (1, 0), xycoords=("axes fraction", "data"), xytext=(6, -14),
                textcoords="offset points", ha="left")
    ax.annotate(ylabel, (0, 1), xycoords=("data", "axes fraction"), xytext=(8, 4),
                textcoords="offset points", ha="left", va="bottom")


def guides(ax, x, y, color=GREY):
    ax.plot([x, x], [0, y], ls="--", lw=0.8, color=color, zorder=1)
    ax.plot([0, x], [y, y], ls="--", lw=0.8, color=color, zorder=1)


# 1. one, two and three numbers
def coordinates_dimensions():
    fig = plt.figure(figsize=(10, 3.4))
    ax = fig.add_subplot(1, 3, 1)
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-1, 1.5)
    ax.axis("off")
    ax.annotate("", (5.4, 0), (-0.3, 0), arrowprops=dict(arrowstyle="-|>", color=INK))
    for t in range(0, 5):
        ax.plot([t, t], [-0.06, 0.06], color=INK, lw=1)
        ax.text(t, -0.25, str(t), ha="center")
    ax.plot(3, 0, "o", color=C2, ms=9)
    ax.text(3, 0.3, "$x=3$", ha="center", color=C2)
    ax.text(5.4, -0.25, "$x$", ha="center")
    ax.set_title("Одно число: точка на линии")

    ax = fig.add_subplot(1, 3, 2)
    ax.set_xlim(-0.5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis("off")
    ax.annotate("", (4.8, 0), (-0.3, 0), arrowprops=dict(arrowstyle="-|>", color=INK))
    ax.annotate("", (0, 3.8), (0, -0.3), arrowprops=dict(arrowstyle="-|>", color=INK))
    ax.plot([3, 3], [0, 2], "--", color=GREY, lw=0.9)
    ax.plot([0, 3], [2, 2], "--", color=GREY, lw=0.9)
    ax.plot(3, 2, "o", color=C2, ms=9)
    ax.text(3.15, 2.15, "$(x;\\,y)$", color=C2)
    ax.text(3, -0.4, "$x$", ha="center")
    ax.text(-0.35, 2, "$y$", va="center")
    ax.text(4.8, -0.4, "$x$", ha="center")
    ax.text(0.15, 3.8, "$y$", va="center")
    ax.set_title("Два числа: точка на плоскости")

    ax = fig.add_subplot(1, 3, 3, projection="3d")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_zlim(0, 4)
    p = (3, 2.5, 2.5)
    ax.plot([0, p[0]], [p[1], p[1]], [0, 0], "--", color=GREY, lw=0.9)
    ax.plot([p[0], p[0]], [0, p[1]], [0, 0], "--", color=GREY, lw=0.9)
    ax.plot([p[0], p[0]], [p[1], p[1]], [0, p[2]], "--", color=GREY, lw=0.9)
    ax.plot(*p, "o", color=C2, ms=8)
    ax.text(p[0], p[1], p[2] + 0.3, "$(x;\\,y;\\,z)$", color=C2, ha="center")
    ax.set_xlabel("$x$", labelpad=-8)
    ax.set_ylabel("$y$", labelpad=-8)
    ax.set_zlabel("$z$", labelpad=-8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.view_init(22, -60)
    ax.set_title("Три числа: точка в пространстве")
    fig.tight_layout()
    save(fig, "coordinates-dimensions.png")


def draw_house(ax, x, y, w=0.18, h=0.16):
    ax.add_patch(Rectangle((x - w / 2, y), w, h, fc=PAPER, ec=INK, lw=1.2, zorder=3))
    ax.add_patch(Polygon([(x - w / 2 - 0.03, y + h), (x + w / 2 + 0.03, y + h), (x, y + h + 0.13)],
                         fc=PAPER, ec=INK, lw=1.2, zorder=3))


def draw_tree(ax, x, y):
    ax.plot([x, x], [y, y + 0.14], color=COPPER, lw=3, zorder=3)
    ax.add_patch(Circle((x, y + 0.26), 0.13, fc=tint(GREEN, 0.6), ec=INK, lw=1.0, zorder=3))


# 2. coordinate axis with house and tree
def coordinate_axis_house_tree():
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.set_xlim(-0.3, 4.6)
    ax.set_ylim(-0.95, 1.05)
    ax.axis("off")
    ax.annotate("", (4.5, 0), (-0.15, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    for x, lab in [(0, "0"), (1.5, "1,5"), (3, "3")]:
        ax.plot([x, x], [-0.05, 0.05], color=INK, lw=1.3)
        ax.text(x, -0.22, lab, ha="center", va="top")
    ax.text(4.5, -0.22, "$x$, км", ha="center", va="top")
    draw_house(ax, 1.5, 0.05)
    draw_tree(ax, 3, 0.05)
    ax.text(1.5, 0.55, "$x_1$", ha="center", color=C1, fontsize=13)
    ax.text(3, 0.68, "$x_2$", ha="center", color=C2, fontsize=13)
    ax.annotate("начало\nкоординат", (0, 0.02), (0, 0.55), ha="center",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("", (3, -0.5), (1.5, -0.5), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.5))
    ax.text(2.25, -0.68, "$s=|x_2-x_1|=1{,}5$ км", ha="center", va="top", color=C3)
    ax.set_title("Координатная ось: дом и дерево")
    save(fig, "coordinate-axis-house-tree.png")


def draw_train(ax, x, y, color):
    ax.add_patch(Rectangle((x - 0.13, y), 0.26, 0.14, fc=color, ec=INK, lw=1.1, zorder=3))
    ax.add_patch(Rectangle((x + 0.02, y + 0.14), 0.09, 0.09, fc=color, ec=INK, lw=1.1, zorder=3))
    for dx in (-0.07, 0.07):
        ax.add_patch(Circle((x + dx, y - 0.005), 0.03, fc=INK, zorder=4))


# 3. locomotive between km posts
def locomotive_axis():
    fig, ax = plt.subplots(figsize=(8.5, 3.0))
    ax.set_xlim(124.7, 127.6)
    ax.set_ylim(-0.95, 0.75)
    ax.axis("off")
    ax.annotate("", (127.5, 0), (124.8, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    for x in (125, 126, 127):
        ax.plot([x, x], [-0.05, 0.05], color=INK, lw=1.3)
        ax.text(x, -0.2, str(x), ha="center", va="top")
    ax.text(127.5, -0.2, "$x$, км", ha="center", va="top")
    draw_train(ax, 125, 0.05, tint(C1, 0.8))
    draw_train(ax, 127, 0.05, tint(C1, 0.5))
    ax.text(125, 0.42, "$x_1=125$ км", ha="center", color=C1)
    ax.text(127, 0.42, "$x_2=127$ км", ha="center", color=C1)
    ax.annotate("", (127, -0.55), (125, -0.55), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.5))
    ax.text(126, -0.72, "$s=|x_2-x_1|=2$ км за $t=1{,}5$ мин", ha="center", va="top", color=C3)
    keep_dots(ax.set_title("Задача 2.30: локомотив между столбиками"))
    save(fig, "locomotive-axis.png")


T = np.array([0, 1, 2, 3, 4])


# 4. path graph of two bodies
def st_two_bodies():
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    for v, c, n in [(2, C1, 1), (3, C2, 2)]:
        ax.plot(T, v * T, "-", color=c, lw=2, zorder=2)
        ax.plot(T[1:], v * T[1:], "o", color=c, zorder=3)
        ax.plot(0, 0, "o", color=INK, zorder=4, ms=4)
        ax.text(4.08, v * 4, f"тело {n}", color=c, va="center")
        for t in T[1:]:
            guides(ax, t, v * t)
    ax.set_xlim(0, 4.9)
    ax.set_ylim(0, 13.5)
    ax.set_xticks(T)
    ax.set_yticks(range(0, 13))
    arrows(ax, "$t$, с", "$s$, м")
    ax.set_title("График движения тел 1 и 2")
    save(fig, "st-two-bodies.png")


# 5. path and speed graphs one under another, common time axis
def st_vt_two_bodies():
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.2, 7.4), sharex=True,
                               gridspec_kw={"height_ratios": [1.8, 1]})
    for v, c, n in [(2, C1, 1), (3, C2, 2)]:
        a.plot(T, v * T, "-", color=c, lw=2)
        a.text(4.08, v * 4, f"тело {n}", color=c, va="center")
        b.plot([0, 4], [v, v], "-", color=c, lw=2)
        b.text(4.08, v, f"тело {n}", color=c, va="center")
    a.set_ylim(0, 13.5)
    a.set_yticks(range(0, 13, 2))
    a.set_xlim(0, 4.9)
    a.set_title("График движения тел 1 и 2", fontsize=11)
    arrows(a, "", "$s$, м")
    b.set_ylim(0, 3.7)
    b.set_yticks([0, 1, 2, 3])
    b.set_xticks(T)
    b.set_title("График скорости тел 1 и 2", fontsize=11)
    arrows(b, "$t$, с", "$v$, м/с")
    for ax in (a, b):
        for t in T[1:]:
            ax.axvline(t, ls=":", lw=0.7, color=GREY, zorder=0)
    fig.tight_layout()
    save(fig, "st-vt-two-bodies.png")


# 6. area under speed graph
def velocity_area_path():
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    for ax, v, c, n in [(axs[0], 2, C1, 1), (axs[1], 3, C2, 2)]:
        ax.add_patch(Rectangle((0, 0), 4, v, fc=c, alpha=0.22, ec="none"))
        ax.plot([0, 4], [v, v], color=c, lw=2)
        ax.plot([4, 4], [0, v], ls="--", color=GREY, lw=0.9)
        ax.text(2, v / 2, f"$s_{n}=v_{n}t={v}\\cdot 4={v * 4}$ м", ha="center", va="center",
                color=c, fontsize=12)
        ax.set_xlim(0, 4.9)
        ax.set_ylim(0, 3.7)
        ax.set_xticks(T)
        ax.set_yticks([0, 1, 2, 3])
        arrows(ax, "$t$, с", "$v$, м/с")
        ax.set_title(f"Тело {n}: площадь прямоугольника", pad=22)
    fig.tight_layout()
    save(fig, "velocity-area-path.png")


# 7. build the path graph from two points
def path_from_speed():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.9))
    a.add_patch(Rectangle((0, 0), 4, 2, fc=C1, alpha=0.30, ec="none"))
    a.plot([0, 4], [2, 2], color=C1, lw=2)
    a.plot([4, 4], [0, 2], ls="--", color=GREY, lw=0.9)
    a.text(2, 1, "$S=2\\cdot 4=8$", ha="center", va="center", color=C1, fontsize=12)
    a.set_xlim(0, 4.9)
    a.set_ylim(0, 3.2)
    a.set_xticks(T)
    a.set_yticks([0, 1, 2, 3])
    arrows(a, "$t$, с", "$v$, м/с")
    a.set_title("1. Площадь за 4 с даёт путь", pad=22)
    b.plot([0, 4], [0, 8], color=C1, lw=2)
    b.plot([0, 4], [0, 8], "o", color=C1, zorder=3)
    b.annotate("вторая точка\n(4 с; 8 м)", (4, 8), (2.4, 9.3), color=C1,
               arrowprops=dict(arrowstyle="->", color=C1))
    b.annotate("начало\nкоординат", (0, 0), (1.3, 0.6), color=NOTE,
               arrowprops=dict(arrowstyle="->", color=GREY))
    guides(b, 4, 8)
    b.set_xlim(0, 4.9)
    b.set_ylim(0, 12)
    b.set_xticks(T)
    b.set_yticks(range(0, 11, 2))
    arrows(b, "$t$, с", "$s$, м")
    b.set_title("2. Прямая через две точки", pad=22)
    fig.tight_layout()
    save(fig, "path-graph-from-speed-graph.png")


# 8. slope grows with speed
def slope_comparison():
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    t = np.array([0, 4])
    cols = {1: GREEN, 2: C1, 3: C2, 5: VIOLET}
    for v, c in cols.items():
        ax.plot(t, v * t, color=c, lw=2)
        ax.text(4.08, v * 4, f"$v={v}$ м/с", color=c, va="center")
    for v, c in [(2, C1), (5, VIOLET)]:
        ax.plot([3, 4, 4], [3 * v, 3 * v, 4 * v], color=GREY, lw=1.1)
        ax.text(3.5, 3 * v - 0.3, "$\\Delta t=1$ с", ha="center", va="top", fontsize=8, color=NOTE)
        ax.text(4.06, 3.5 * v, f"$\\Delta s={v}$ м", va="center", fontsize=8, color=NOTE)
    ax.set_xlim(0, 5.3)
    ax.set_ylim(0, 21.5)
    ax.set_yticks(range(0, 21, 5))
    ax.set_xticks(range(5))
    arrows(ax, "$t$, с", "$s$, м")
    ax.set_title("Наклон графика растёт со скоростью")
    save(fig, "slope-comparison.png")


# 9. coordinate vs path
def coordinate_vs_path():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8), sharex=True)
    tx = [0, 4, 8]
    a.plot(tx, [0, 40, 0], color=C1, lw=2)
    a.plot(tx, [0, 40, 0], "o", color=C1)
    a.set_ylim(0, 52)
    a.set_title("Координата: растёт, потом убывает", pad=22)
    arrows(a, "$t$, ч", "$x$, км")
    b.plot(tx, [0, 40, 80], color=C2, lw=2)
    b.plot(tx, [0, 40, 80], "o", color=C2)
    b.set_ylim(0, 104)
    b.set_title("Путь: только растёт", pad=22)
    arrows(b, "$t$, ч", "$s$, км")
    for ax in (a, b):
        ax.set_xlim(0, 9.6)
        ax.set_xticks(tx)
    fig.tight_layout()
    save(fig, "coordinate-vs-path.png")


# 10. problem 4.10
def task_4_10():
    tt = [0, 1, 2, 4, 5]
    ss = [0, 100, 100, 200, 250]
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.6, 7.6), sharex=True,
                               gridspec_kw={"height_ratios": [1.5, 1]})
    a.plot(tt, ss, color=C1, lw=2)
    a.plot(tt, ss, "o", color=C1, zorder=3)
    for t, s in zip(tt[1:], ss[1:]):
        guides(a, t, s)
    a.set_xlim(0, 5.9)
    a.set_ylim(0, 290)
    a.set_yticks([0, 100, 200])
    a.set_title("График движения: $s(t)$ дан", fontsize=11)
    arrows(a, "", "$s$, км")
    segs = [(0, 1, 100, "1"), (1, 2, 0, "2"), (2, 5, 50, "3")]
    for x0, x1, v, n in segs:
        b.plot([x0, x1], [v, v], color=C2, lw=2.4)
    b.plot([1, 1], [0, 100], ls=":", color=C2, lw=1)
    b.plot([2, 2], [0, 50], ls=":", color=C2, lw=1)
    b.add_patch(Rectangle((0, 0), 1, 100, fc=C2, alpha=0.18, ec="none"))
    b.add_patch(Rectangle((2, 0), 3, 50, fc=C2, alpha=0.18, ec="none"))
    b.text(0.5, 50, "100 км", ha="center", va="center", fontsize=9)
    b.text(3.5, 25, "150 км", ha="center", va="center", fontsize=9)
    b.text(1.5, 8, "стоит", ha="center", va="bottom", fontsize=9, color=C2)
    b.set_ylim(0, 128)
    b.set_yticks([0, 50, 100])
    b.set_xticks(range(6))
    b.set_title("График скорости: $v(t)$ строим", fontsize=11)
    arrows(b, "$t$, ч", "$v$, км/ч")
    for ax in (a, b):
        for t in range(1, 6):
            ax.axvline(t, ls=":", lw=0.6, color=ASH, zorder=0)
    fig.tight_layout()
    save(fig, "task-4-10-graphs.png")


# 11. route scheme of the traveler
def traveler_route_scheme():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(-3, 56)
    ax.set_ylim(-4.2, 4.6)
    ax.axis("off")
    ax.annotate("", (54, 0), (-1.5, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.text(54.6, -0.5, "$x$, км", va="top")
    for x in (0, 30, 35, 50):
        ax.plot([x, x], [-0.25, 0.25], color=INK, lw=1.3)
        ax.text(x, -0.55, str(x), ha="center", va="top")
    bars = [(0, 30, C1, "1  лодка\n$v_1=15$ км/ч, $t_1=2$ ч\n$s_1=30$ км", 1.0),
            (30, 35, C3, "2  пешком\n$v_2=5$ км/ч\n$t_2=1$ ч, $s_2=5$ км", 2.55),
            (35, 50, C2, "4  пешком\n$v_4=5$ км/ч, $t_4=3$ ч\n$s_4=15$ км", 1.0)]
    for x0, x1, c, lab, yl in bars:
        ax.plot([x0, x1], [0.9, 0.9], color=c, lw=6, solid_capstyle="butt")
        ax.text((x0 + x1) / 2, yl + 0.35, lab, ha="center", va="bottom", fontsize=9.5, color=c)
    ax.plot([30, 32.5], [0.9, 2.55 + 0.3], color=C3, lw=0.8)
    ax.plot(35, 0, "s", color=INK, ms=6)
    ax.text(35, -2.9, "3  отдых, $t_3=1$ ч\n$s_3=0$", ha="center", va="top", fontsize=9.5)
    ax.plot(50, 0, "s", color=INK, ms=6)
    ax.text(50.4, -2.9, "5  ожидание поезда\n$t_5=1$ ч, $s_5=0$", ha="center", va="top", fontsize=9.5)
    ax.annotate("", (0, -1.6), (50, -1.6), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=2))
    ax.text(12, -1.95, "6  поезд назад: $t_6=2$ ч, $s_6=50$ км", ha="left", va="top", fontsize=9.5, color=NOTE)
    keep_dots(ax.set_title("Задача 4.25: маршрут путешественника"))
    save(fig, "traveler-route-scheme.png")


STAGES = [(0, 0), (2, 30), (3, 35), (4, 35), (7, 50), (8, 50), (10, 0)]
STAGES_S = [(0, 0), (2, 30), (3, 35), (4, 35), (7, 50), (8, 50), (10, 100)]


def numbers(ax, ymax):
    spans = [(0, 2), (2, 3), (3, 4), (4, 7), (7, 8), (8, 10)]
    for i, (a0, a1) in enumerate(spans, 1):
        ax.text((a0 + a1) / 2, ymax, str(i), ha="center", va="top", fontsize=9, color=NOTE)
        if i > 1:
            ax.axvline(a0, ls=":", lw=0.6, color=ASH, zorder=0)


# 12. coordinate and path graphs of the traveler
def traveler_x_s_graphs():
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.4, 8.4), sharex=True)
    for ax, pts, c in [(a, STAGES, C1), (b, STAGES_S, C2)]:
        t, y = zip(*pts)
        ax.plot(t, y, color=c, lw=2)
        ax.plot(t[1:], y[1:], "o", color=c, zorder=3)
        ax.plot(0, 0, "o", color=INK, ms=4, zorder=4)
        ax.set_xlim(0, 11.2)
        ax.set_xticks(range(0, 11, 2))
    a.set_ylim(0, 60)
    a.set_yticks(range(0, 51, 10))
    a.set_title("Координата: график $x(t)$", fontsize=11)
    arrows(a, "", "$x$, км")
    numbers(a, 58)
    guides(a, 7, 50)
    b.set_ylim(0, 116)
    b.set_yticks(range(0, 101, 20))
    b.set_title("Путь: график $s(t)$", fontsize=11)
    arrows(b, "$t$, ч", "$s$, км")
    numbers(b, 113)
    b.plot([0, 10], [0, 100], ls="--", color=GREY, lw=1.3)
    b.plot([10, 10], [0, 100], ls=":", color=GREY, lw=0.9)
    b.plot([0, 10], [100, 100], ls=":", color=GREY, lw=0.9)
    b.text(0.4, 84, "$v_{ср}=\\dfrac{s_{общ}}{t_{общ}}=\\dfrac{100}{10}=10$ км/ч", color=NOTE,
           rotation=0, fontsize=10, ha="left")
    b.text(0.15, 102, "$s_{общ}=100$ км", color=NOTE, va="bottom", fontsize=9)
    b.text(10, -14, "$t_{общ}=10$ ч", color=NOTE, ha="center", fontsize=9)
    fig.tight_layout()
    save(fig, "traveler-x-s-graphs.png")


# 13. speed graph of the traveler, area is path
def traveler_speed_graph():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    stages = [(0, 2, 15, "30"), (2, 3, 5, "5"), (3, 4, 0, "0"), (4, 7, 5, "15"),
              (7, 8, 0, "0"), (8, 10, 25, "50")]
    for x0, x1, v, lab in stages:
        ax.plot([x0, x1], [v, v], color=C2, lw=2.4)
        ax.add_patch(Rectangle((x0, 0), x1 - x0, v, fc=C2, alpha=0.18, ec="none"))
        if v > 0:
            ax.text((x0 + x1) / 2, v / 2, f"{lab} км", ha="center", va="center", fontsize=9)
    ax.plot([0, 10], [10, 10], ls="--", color=GREY, lw=1.3)
    ax.text(10.15, 10, "$v_{ср}=10$ км/ч", color=NOTE, va="center", fontsize=9)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 30)
    ax.set_xticks(range(0, 11, 2))
    ax.set_yticks([0, 5, 10, 15, 25])
    arrows(ax, "$t$, ч", "$v$, км/ч")
    ax.set_title("Модуль скорости путешественника")
    save(fig, "traveler-speed-graph.png")


if __name__ == "__main__":
    coordinates_dimensions()
    coordinate_axis_house_tree()
    locomotive_axis()
    st_two_bodies()
    st_vt_two_bodies()
    velocity_area_path()
    path_from_speed()
    slope_comparison()
    coordinate_vs_path()
    task_4_10()
    traveler_route_scheme()
    traveler_x_s_graphs()
    traveler_speed_graph()
