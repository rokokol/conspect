"""Figures for the note "Механическое движение и скорость" (lesson 15).

Run (the helpers come from motion_graphs.py in the same folder):
  nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages(ps: [ps.matplotlib ps.numpy]))]' -c python3 motion_speed.py
The PNG files go to content/03. Механическое движение/00. Вложения/, prefix "motion-".
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import num
import numpy as np
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle

from motion_graphs import C1, C2, C3, COPPER, GREEN, GREY, INK, NOTE, arrows, guides, save, tint


def wagon(ax, x0, x1, y, h, color, ec=INK, alpha=1.0, wheels=True):
    ax.add_patch(Rectangle((x0, y), x1 - x0, h, fc=color, ec=ec, lw=1.1, alpha=alpha, zorder=3))
    if wheels:
        for x in (x0 + 0.18 * (x1 - x0), x1 - 0.18 * (x1 - x0)):
            ax.add_patch(Circle((x, y), h * 0.16, fc=INK, alpha=alpha, zorder=4))


def vec(ax, p, q, color=INK, lw=1.8, style="-|>", ms=14, ls="-"):
    ax.add_patch(
        FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, ls=ls, zorder=5)
    )


# 1. position relative to different bodies
def reference_frame():
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
    for ax, title in zip(axs, ["Тело отсчёта — дерево у путей", "Тело отсчёта — сиденье в поезде"]):
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.6, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11)
        ax.plot([0, 10], [0.2, 0.2], color=GREY, lw=2)
    # left: tree fixed, train shifts
    a = axs[0]
    a.plot([1.2, 1.2], [0.2, 1.4], color=COPPER, lw=5)
    a.add_patch(Circle((1.2, 2.0), 0.7, fc=tint(GREEN, 0.6), ec="none"))
    wagon(a, 2.0, 5.0, 0.4, 1.2, tint(C1, 0.85), alpha=0.6)
    a.add_patch(Circle((3.5, 1.0), 0.16, fc=C2, alpha=0.6, zorder=6))
    wagon(a, 5.4, 8.4, 0.4, 1.2, tint(C1, 0.8))
    a.add_patch(Circle((6.9, 1.0), 0.16, fc=C2, zorder=6))
    vec(a, (3.6, 2.4), (6.8, 2.4), color=C2)
    a.text(5.2, 2.65, "положение меняется", ha="center", color=C2, fontsize=10)
    a.text(3.5, -0.35, "$t_1$", ha="center")
    a.text(6.9, -0.35, "$t_2$", ha="center")
    # right: seat, passenger fixed
    b = axs[1]
    wagon(b, 3.0, 8.0, 0.4, 1.8, tint(C1, 0.8))
    b.add_patch(Rectangle((4.2, 0.7), 0.7, 0.5, fc=tint(COPPER, 0.4), ec=INK, lw=1, zorder=4))
    b.add_patch(Circle((4.55, 1.5), 0.18, fc=C2, zorder=6))
    b.text(5.6, 1.35, "пассажир", fontsize=10, color=C2, va="center")
    b.annotate("сиденье", (4.55, 0.7), (4.5, -0.3), ha="center", fontsize=9, color=NOTE,
               arrowprops=dict(arrowstyle="->", color=GREY))
    b.text(5.5, 2.6, "положение не меняется", ha="center", color=C3, fontsize=10)
    save(fig, "motion-reference-frame.png")


# 2. trajectory and path
def trajectory_path():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    t = np.linspace(0, 1, 400)
    x = 0.4 + 6.4 * t
    y = 0.6 + 2.0 * np.sin(2 * np.pi * t * 0.95) * (1 - 0.15 * t) + 0.8 * t
    ax.plot(x, y, color=C1, lw=2.6, zorder=2)
    seg = np.hypot(np.diff(x), np.diff(y))
    cum = np.concatenate([[0], np.cumsum(seg)])
    for L in np.arange(0.75, cum[-1], 0.75):
        i = np.searchsorted(cum, L)
        dx, dy = x[i] - x[i - 1], y[i] - y[i - 1]
        n = np.hypot(dx, dy)
        ax.plot([x[i] - 0.09 * dy / n, x[i] + 0.09 * dy / n], [y[i] + 0.09 * dx / n, y[i] - 0.09 * dx / n],
                color=INK, lw=1.2, zorder=3)
    ax.plot(x[0], y[0], "o", color=INK, ms=7, zorder=4)
    ax.plot(x[-1], y[-1], "o", color=INK, ms=7, zorder=4)
    ax.text(x[0] - 0.1, y[0] - 0.35, "A", ha="center", fontsize=13)
    ax.text(x[-1] + 0.05, y[-1] + 0.3, "B", ha="center", fontsize=13)
    ax.annotate("траектория", (x[100], y[100]), (1.6, 3.3), color=C1, fontsize=12,
                arrowprops=dict(arrowstyle="->", color=C1))
    ax.text(3.6, -1.15, "путь $s$ — длина траектории, измеренная вдоль неё", ha="center", fontsize=11, color=INK)
    ax.set_xlim(-0.3, 7.5)
    ax.set_ylim(-1.5, 3.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Траектория и путь")
    save(fig, "motion-trajectory-path.png")


# 3. straight and curved
def straight_curved():
    fig, axs = plt.subplots(2, 1, figsize=(6.2, 4.4))
    a, b = axs
    a.plot([0.5, 6.5], [0, 0], color=C1, lw=2.6)
    for x, n in [(0.5, "A"), (6.5, "B")]:
        a.plot(x, 0, "o", color=INK)
        a.text(x, 0.35, n, ha="center", fontsize=12)
    a.set_title("Прямолинейное движение: траектория — прямая", fontsize=11)
    t = np.linspace(0, 1, 200)
    b.plot(0.5 + 6 * t, 0.9 * np.sin(np.pi * t * 1.3) - 0.3 * t, color=C2, lw=2.6)
    b.plot(0.5, 0, "o", color=INK)
    b.plot(6.5, 0.9 * np.sin(np.pi * 1.3) - 0.3, "o", color=INK)
    b.text(0.5, -0.5, "A", ha="center", fontsize=12)
    b.text(6.5, 0.9 * np.sin(np.pi * 1.3) - 0.85, "B", ha="center", fontsize=12)
    b.set_title("Криволинейное движение: траектория — кривая", fontsize=11)
    for ax in axs:
        ax.set_xlim(0, 7)
        ax.set_ylim(-1.4, 1.2)
        ax.axis("off")
    save(fig, "motion-straight-curved.png")


# 4. material point: road versus garage
def material_point():
    fig, axs = plt.subplots(2, 1, figsize=(8.6, 5.0), gridspec_kw={"height_ratios": [1, 1.3]})
    a, b = axs
    a.set_xlim(0, 12)
    a.set_ylim(-0.9, 1.0)
    a.axis("off")
    a.plot([0.8, 11.2], [0, 0], color=GREY, lw=3)
    a.plot(4.2, 0.0, "o", color=C2, ms=9, zorder=4)
    vec(a, (4.5, 0.0), (6.4, 0.0), color=C2)
    a.text(0.8, -0.35, "Одесса", ha="center")
    a.text(11.2, -0.35, "Киев", ha="center")
    a.text(6.0, 0.55, "размеры автомобиля не важны: материальная точка", ha="center", fontsize=11, color=C3)
    b.set_xlim(0, 12)
    b.set_ylim(-1.0, 3.3)
    b.axis("off")
    b.add_patch(Rectangle((2.2, 0.0), 0.15, 2.4, fc=INK, ec="none"))
    b.add_patch(Rectangle((9.65, 0.0), 0.15, 2.4, fc=INK, ec="none"))
    b.add_patch(Polygon([[2.0, 2.4], [6.0, 3.1], [10.0, 2.4]], closed=True, fc=tint(COPPER, 0.6), ec=INK))
    b.add_patch(Rectangle((3.9, 0.1), 3.4, 1.0, fc=tint(C1, 0.8), ec=INK, lw=1.2))
    b.add_patch(Rectangle((4.5, 1.1), 1.8, 0.6, fc=tint(C1, 0.85), ec=INK, lw=1.2))
    for x in (4.5, 6.7):
        b.add_patch(Circle((x, 0.1), 0.28, fc=INK, zorder=4))
    vec(b, (7.5, 0.6), (9.2, 0.6), color=C2)
    b.text(6.0, -0.45, "заезд в гараж: размеры автомобиля решают всё", ha="center", va="top", fontsize=11, color=C2)
    save(fig, "motion-material-point.png")


# 5. uniform versus non-uniform for the tram
def tram_uniform():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    # stand 250 s, move 50 s at 10 m/s: +500 m per 5 min
    tt, ss = [0.0], [0.0]
    for k in range(3):
        tt.append(tt[-1] + 250 / 60)
        ss.append(ss[-1])
        tt.append(tt[-1] + 50 / 60)
        ss.append(ss[-1] + 500)
    ax.plot(tt, ss, color=C2, lw=2.4, label="трамвай: стоит на остановке, между остановками $10\\ \\text{м/с}$")
    tl = np.array([0, 15])
    ax.plot(tl, 100 * tl, "--", color=GREY, lw=1.4, label="равномерное движение со скоростью $100\\ \\text{м/мин}$")
    for k in (1, 2, 3):
        ax.plot(5 * k, 500 * k, "o", color=INK, zorder=4)
        guides(ax, 5 * k, 500 * k)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 1700)
    ax.set_xticks([0, 5, 10, 15])
    ax.set_yticks([0, 500, 1000, 1500])
    arrows(ax, "$t$, мин", "$s$, м")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.set_title("Трамвай: по 500 м за 5 минут", pad=24)
    save(fig, "motion-tram-nonuniform.png")


# 6. equal intervals: uniform and non-uniform
def equal_intervals():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    a, b = axs
    t = np.linspace(0, 6, 100)
    a.plot(t, 2 * t, color=C1, lw=2.4)
    for k in range(6):
        a.add_patch(Rectangle((k, 2 * k), 1, 2, fc=C1, alpha=0.12, ec=C1, lw=0.8))
    a.text(3.0, 1.0, "все $\\Delta s$ равны", ha="center", color=C1)
    a.set_title("Равномерное движение", fontsize=11, pad=24)
    b.plot(t, 0.4 * t**2, color=C2, lw=2.4)
    for k in range(6):
        y0, y1 = 0.4 * k * k, 0.4 * (k + 1) ** 2
        b.add_patch(Rectangle((k, y0), 1, y1 - y0, fc=C2, alpha=0.12, ec=C2, lw=0.8))
    b.text(2.0, 11, "$\\Delta s$ разные\nпри равных $\\Delta t$", ha="center", color=C2)
    b.set_title("Неравномерное движение", fontsize=11, pad=24)
    for ax in axs:
        ax.set_xlim(0, 6.8)
        ax.set_ylim(0, 14.5)
        ax.set_xticks(range(0, 7))
        ax.set_yticklabels([])
        ax.set_yticks([])
        arrows(ax, "$t$", "$s$")
    save(fig, "motion-equal-intervals.png")


# 7. velocity vectors
def velocity_vectors():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(-3.6, 5.4)
    ax.set_ylim(-2.5, 2.7)
    ax.set_aspect("equal")
    ax.axis("off")
    d1 = np.array([1.0, 1.0]) * 1.2
    d2 = np.array([1.0, -1.0]) * 1.2
    p1, p2 = np.array([-3.0, -0.6]), np.array([0.2, 1.7])
    for p, d, c, n, txt, lp, ha in [
        (p1, d1, C1, 1, "северо-восток", p1 + np.array([0.0, -0.6]), "center"),
        (p2, d2, C2, 2, "юго-восток", p2 + d2 + np.array([0.2, -0.1]), "left"),
    ]:
        ax.add_patch(Circle(p, 0.13, fc=c, ec=INK, zorder=4))
        vec(ax, p + 0.15 * d / np.linalg.norm(d), p + d, color=c, lw=2.4, ms=18)
        ax.text(p[0] - 0.25, p[1] + 0.12, f"{n}", ha="right", va="center", fontsize=12, color=c)
        ax.text(lp[0], lp[1], f"$\\vec{{v}}_{n}$: $1\\ \\text{{м/с}}$, {txt}", color=c, fontsize=11,
                va="center", ha=ha)
    # compass
    cx, cy = 4.5, -1.6
    vec(ax, (cx, cy), (cx, cy + 0.9), lw=1.4)
    vec(ax, (cx, cy), (cx + 0.9, cy), lw=1.4)
    ax.text(cx, cy + 1.05, "С", ha="center", fontsize=10)
    ax.text(cx + 1.05, cy, "В", va="center", fontsize=10)
    ax.text(-3.4, -2.35, "Одинаковый модуль $v_1=v_2=1\\ \\text{м/с}$, векторы разные", fontsize=11)
    ax.set_title("Скорость — вектор")
    save(fig, "motion-velocity-vectors.png")


# 8. speedometer shows modulus only
def speedometer():
    fig, ax = plt.subplots(figsize=(4.8, 3.6))
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-0.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Arc((0, 0), 2.2, 2.2, theta1=0, theta2=180, lw=2.4, color=INK))
    vmax = 180
    for v in range(0, vmax + 1, 20):
        ang = np.pi * (1 - v / vmax)
        ax.plot([0.93 * np.cos(ang), 1.1 * np.cos(ang)], [0.93 * np.sin(ang), 1.1 * np.sin(ang)], color=INK, lw=1.4)
        ax.text(0.78 * np.cos(ang), 0.78 * np.sin(ang), str(v), ha="center", va="center", fontsize=8)
    ang = np.pi * (1 - 54 / vmax)
    vec(ax, (0, 0), (0.9 * np.cos(ang), 0.9 * np.sin(ang)), color=C2, lw=2.6, ms=16)
    ax.add_patch(Circle((0, 0), 0.05, fc=INK, zorder=6))
    ax.text(0, -0.2, "$v = 54\\ \\text{км/ч}$", ha="center", fontsize=12, color=C2)
    ax.text(0, 0.38, "модуль", ha="center", fontsize=9, color=NOTE)
    ax.set_title("Спидометр показывает только модуль")
    save(fig, "motion-speedometer.png")


# 9. speed scale, log axis
def speed_scale():
    items = [
        ("пешеход", 1.4, "1,4", C3),
        ("велосипедист", 5, "5", C3),
        ("электропоезд из задачи", 20, "20", C1),
        ("Одесса: вращение Земли", 320, "320", C2),
        ("звук в воздухе", 340, "340", C1),
        ("Земля на орбите", 3.0e4, "$3\\cdot10^{4}$", C2),
        ("свет в вакууме", 3.0e8, "$3\\cdot10^{8}$", COPPER),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    ys = np.arange(len(items))
    for y, (name, v, lab, c) in zip(ys, items):
        ax.barh(y, v, color=c, alpha=0.85, height=0.6)
        ax.text(v * 1.25, y, lab, va="center", fontsize=9)
    ax.set_yticks(ys)
    ax.set_yticklabels([it[0] for it in items])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.5, 3e10)
    ax.set_xlabel("$v$, м/с (логарифмическая шкала)")
    ax.spines["left"].set_visible(True)
    ax.set_title("Порядки скоростей")
    save(fig, "motion-speed-scale.png")


# 10. km/h against m/s
def unit_conversion():
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    x = np.array([0, 22])
    ax.plot(x, 3.6 * x, color=C1, lw=2.2)
    for xv in (5, 10, 15, 20):
        ax.plot(xv, 3.6 * xv, "o", color=C2, zorder=4)
        guides(ax, xv, 3.6 * xv)
        ax.text(xv + 0.3, 3.6 * xv - 4.5, num(3.6 * xv, None), color=C2, fontsize=9)
    ax.text(3.0, 66, "$v_{\\text{км/ч}} = 3{,}6\\,v_{\\text{м/с}}$", color=C1, fontsize=12, rotation=0)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 90)
    ax.set_xticks([0, 5, 10, 15, 20])
    arrows(ax, "$v$, м/с", "$v$, км/ч")
    ax.set_title("Перевод м/с в км/ч")
    save(fig, "motion-unit-conversion.png")


# 11. same distance, different times
def same_distance():
    items = [("самолёт", 900, C1), ("автомобиль", 90, C2), ("велосипед", 20, C3)]
    dist = 480.0
    fig, ax = plt.subplots(figsize=(7.6, 3.3))
    for y, (n, v, c) in enumerate(items):
        t = dist / v
        ax.barh(y, t, color=c, alpha=0.85, height=0.55)
        lab = f"{t * 60:.0f} мин" if t < 1 else num(t, 1) + " ч"
        note = " в седле; с ночёвками — несколько дней" if n == "велосипед" else ""
        ax.text(t * 1.15, y, f"{lab} при {v} км/ч{note}", va="center", fontsize=9)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([n for n, _, _ in items])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.3, 300)
    ax.set_xlabel("время в пути, ч (логарифмическая шкала)")
    ax.spines["left"].set_visible(True)
    ax.set_title("Одно расстояние — разное время")
    save(fig, "motion-same-distance.png")


if __name__ == "__main__":
    reference_frame()
    trajectory_path()
    straight_curved()
    material_point()
    tram_uniform()
    equal_intervals()
    velocity_vectors()
    speedometer()
    speed_scale()
    unit_conversion()
    same_distance()
