"""Figures for the note "Совместное движение тел" (lesson 21).

Run (the helpers come from motion_graphs.py and motion_speed.py in the same folder):
  nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages(ps: [ps.matplotlib ps.numpy]))]' -c python3 motion_meeting.py
The PNG files go to content/03. Механическое движение/00. Вложения/, prefix "meeting-".
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
import numpy as np
from matplotlib.patches import Circle, Rectangle

from motion_graphs import C1, C2, C3, GREY, INK, NOTE, PAPER, SKY, arrows, save, tint
from motion_speed import vec

LIGHT1 = tint(C1, 0.8)  # body 1, a pale fill
LIGHT2 = tint(C2, 0.8)  # body 2, a pale fill


def train(ax, x0, x1, y, color, alpha=1.0, h=0.5, head="right", label=None):
    """Draw a train as a long rectangle with windows; head marks the front side."""
    ax.add_patch(Rectangle((x0, y), x1 - x0, h, fc=color, ec=INK, lw=1.1, alpha=alpha, zorder=3))
    n = max(int((x1 - x0) / 0.8), 2)
    for k in range(n):
        wx = x0 + (k + 0.3) * (x1 - x0) / n
        ax.add_patch(Rectangle((wx, y + 0.27 * h), 0.4 * (x1 - x0) / n, 0.4 * h, fc=PAPER, ec="none",
                               alpha=alpha, zorder=4))
    fx = x1 if head == "right" else x0
    ax.plot([fx], [y + h / 2], marker=">" if head == "right" else "<", color=INK, ms=7, alpha=alpha, zorder=5)
    if label:
        ax.text((x0 + x1) / 2, y + h + 0.08, label, ha="center", va="bottom", fontsize=10, color=INK)


def dim(ax, x0, x1, y, text, color=INK, dy=-0.2):
    ax.annotate("", (x1, y), (x0, y), arrowprops=dict(arrowstyle="<->", color=color, lw=1.3))
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom" if dy > 0 else "top", color=color, fontsize=10)


def rails(ax, y, x0, x1):
    ax.plot([x0, x1], [y, y], color=GREY, lw=2, zorder=1)


# 1. oncoming trains, two frames of reference
def oncoming_frames():
    fig, axs = plt.subplots(2, 1, figsize=(8.6, 5.6))
    a, b = axs
    for ax in axs:
        ax.set_xlim(-2.2, 13.5)
        ax.set_ylim(-0.6, 3.0)
        ax.axis("off")
    a.set_title("Система отсчёта — Земля: движутся оба поезда", fontsize=11, loc="left")
    rails(a, 0.0, -0.4, 13.4)
    rails(a, 0.9, -0.4, 13.4)
    train(a, 1.0, 4.6, 0.0, LIGHT1, label="поезд 1")
    a.add_patch(Circle((3.6, 0.25), 0.11, fc=C2, ec=INK, zorder=6))
    vec(a, (4.8, 0.25), (6.2, 0.25), color=C1)
    a.text(5.5, 0.4, "$\\vec v_1$", ha="center", color=C1, fontsize=12)
    train(a, 7.4, 12.6, 0.9, LIGHT2, head="left", label="встречный поезд")
    vec(a, (7.2, 1.15), (5.8, 1.15), color=C2)
    a.text(6.5, 1.3, "$\\vec v_2$", ha="center", color=C2, fontsize=12)
    dim(a, 7.4, 12.6, 0.75, "$l_2$", dy=-0.05)
    b.set_title("Система отсчёта — пассажир: поезд 1 стоит", fontsize=11, loc="left")
    rails(b, 0.0, -0.4, 13.4)
    rails(b, 0.9, -0.4, 13.4)
    train(b, 1.0, 4.6, 0.0, LIGHT1, label="поезд 1")
    b.add_patch(Circle((3.6, 0.25), 0.11, fc=C2, ec=INK, zorder=6))
    b.plot([3.6, 3.6], [0.4, 1.7], ls=":", color=GREY, lw=1)
    train(b, 3.6, 8.8, 0.9, LIGHT2, alpha=0.55, head="left")
    train(b, -1.6, 3.6, 0.9, LIGHT2, alpha=0.9, head="left")
    b.text(6.2, 1.5, "начало: голова у пассажира", ha="center", fontsize=9.5, color=NOTE)
    b.text(0.5, 1.5, "конец: хвост у пассажира", ha="center", fontsize=9.5, color=NOTE)
    vec(b, (8.6, 2.3), (0.4, 2.3), color=C2, lw=2.4, ms=18)
    b.text(4.5, 2.5, "$v_{\\text{отн}}=v_1+v_2$, путь поезда 2 мимо пассажира равен $l_2$", ha="center", color=C2,
           fontsize=11)
    save(fig, "meeting-trains-frames.png")


# 2. x(t) for the passenger and the two ends of the oncoming train
def oncoming_xt():
    v1, v2, D, L = 15.0, 20.0, 300.0, 150.0
    t1, t2 = D / (v1 + v2), (D + L) / (v1 + v2)
    t = np.linspace(0, 15, 100)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.plot(t, v1 * t, color=C1, lw=2.4)
    ax.plot(t, D - v2 * t, color=C2, lw=2.4)
    ax.plot(t, D + L - v2 * t, color=C2, lw=2.4, ls="--")
    ax.axvspan(t1, t2, color=C3, alpha=0.18, lw=0)
    for tm, xm in [(t1, v1 * t1), (t2, v1 * t2)]:
        ax.plot(tm, xm, "o", color=INK, zorder=5)
        ax.plot([tm, tm], [0, xm], ls=":", color=GREY, lw=1)
    ax.text(t1 + 0.1, 40, "начало\nвстречи", fontsize=9, color=INK)
    ax.text(t2 - 0.1, 40, "конец\nвстречи", fontsize=9, color=INK, ha="right")
    ax.annotate("", (t2, 25), (t1, 25), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.6))
    ax.text((t1 + t2) / 2, 5, "$t\\approx4{,}3$ с", ha="center", color=C3, fontsize=11)
    ax.text(15.2, v1 * 15, "пассажир", color=C1, va="center")
    ax.text(15.2, D - v2 * 15 + 28, "голова поезда", color=C2, va="center")
    ax.text(15.2, D + L - v2 * 15, "хвост поезда", color=C2, va="center")
    ax.set_xlim(0, 19.5)
    ax.set_ylim(0, 480)
    ax.set_xticks(range(0, 16, 3))
    arrows(ax, "$t$, с", "$x$, м")
    ax.set_title("Встречный поезд: график $x(t)$", pad=22)
    save(fig, "meeting-trains-xt.png")


# 3. distance between two bodies against time
def distance_between():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    a, b = axs
    t = np.linspace(0, 20, 50)
    a.plot(t, 100 - 5 * t, color=C1, lw=2.4)
    a.plot(20, 0, "o", color=INK, zorder=5)
    a.text(8, 66, "наклон $-(v_1+v_2)$", color=C1, rotation=-30, fontsize=10)
    a.set_title("Навстречу: расстояние убывает\nсо скоростью $v_1+v_2$", fontsize=11, pad=22)
    # same example as chase_xt: v1 = 5, v2 = 2 m/s, D = 60 m, caught up at 20 s
    tt = np.linspace(0, 20, 50)
    b.plot(tt, 60 - 3 * tt, color=C2, lw=2.4)
    b.plot(20, 0, "o", color=INK, zorder=5)
    b.text(8, 34, "наклон $-(v_1-v_2)$", color=C2, rotation=-22, fontsize=10)
    b.set_title("Вдогонку: расстояние убывает\nсо скоростью $v_1-v_2$", fontsize=11, pad=22)
    for ax, xm, ym in [(a, 24, 110), (b, 24, 70)]:
        ax.set_xlim(0, xm)
        ax.set_ylim(0, ym)
        arrows(ax, "$t$, с", "расстояние, м")
    save(fig, "meeting-distance-between.png")


# 4. two bodies come together: x(t)
def approach_xt():
    v1, v2, D = 2.0, 3.0, 100.0
    tm = D / (v1 + v2)
    xm = v1 * tm
    t = np.linspace(0, 30, 100)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(t, v1 * t, color=C1, lw=2.4)
    ax.plot(t, D - v2 * t, color=C2, lw=2.4)
    ax.plot(tm, xm, "o", color=INK, ms=9, zorder=5)
    ax.plot([tm, tm], [0, xm], ls="--", color=GREY, lw=1)
    ax.plot([0, tm], [xm, xm], ls="--", color=GREY, lw=1)
    ax.text(9.0, 4, "встреча:\n$t=20$ с, $x=40$ м", fontsize=10)
    ax.text(26, v1 * 26 + 5, "тело 1, $v_1=2$ м/с", color=C1, ha="center", fontsize=10, rotation=15)
    ax.text(7, D - v2 * 7 + 3, "тело 2, $v_2=3$ м/с", color=C2, fontsize=10, rotation=-27)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlim(0, 33)
    ax.set_ylim(0, 112)
    arrows(ax, "$t$, с", "$x$, м")
    ax.set_title("Тела едут навстречу", pad=22)
    save(fig, "meeting-approach-xt.png")


# 5. chase: x(t)
def chase_xt():
    v1, v2, D = 5.0, 2.0, 60.0
    tm = D / (v1 - v2)
    xm = v1 * tm
    t = np.linspace(0, 30, 100)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(t, v1 * t, color=C1, lw=2.4)
    ax.plot(t, D + v2 * t, color=C2, lw=2.4)
    ax.plot(tm, xm, "o", color=INK, ms=9, zorder=5)
    ax.plot([tm, tm], [0, xm], ls="--", color=GREY, lw=1)
    ax.plot([0, tm], [xm, xm], ls="--", color=GREY, lw=1)
    ax.text(tm + 1.0, xm - 30, "догон:\n$t=20$ с, $x=100$ м", fontsize=10)
    ax.text(9.0, 32, "догоняющее, $v_1=5$ м/с", color=C1, fontsize=10, rotation=29)
    ax.text(1.5, D + 10, "убегающее, $v_2=2$ м/с", color=C2, fontsize=10, rotation=9)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_yticks([0, 30, 60, 100, 150])
    ax.set_xlim(0, 33)
    ax.set_ylim(0, 170)
    arrows(ax, "$t$, с", "$x$, м")
    ax.set_title("Одно тело догоняет другое", pad=22)
    save(fig, "meeting-chase-xt.png")


# 6. overtaking, frame of the slow train
def overtake_frames():
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.set_xlim(-4.2, 9.2)
    ax.set_ylim(-1.6, 3.0)
    ax.axis("off")
    L = 3.0
    for y in (0.0, 1.0):
        rails(ax, y - 0.05, -4.0, 9.0)
    ax.text(-4.1, 2.75, "Система отсчёта — медленный поезд", fontsize=11, ha="left")
    train(ax, 0, L, 1.0, LIGHT2)
    ax.text(L + 0.3, 1.25, "поезд 2 стоит", fontsize=10, va="center")
    train(ax, -L, 0, 0.0, LIGHT1, alpha=0.6, head="right", label="начало обгона")
    train(ax, L, 2 * L, 0.0, LIGHT1, head="right")
    ax.text(1.5 * L, 0.62, "конец обгона", ha="center", fontsize=10)
    ax.plot([0, 0], [0.5, 1.0], ls=":", color=INK)
    ax.plot([L, L], [0.5, 1.0], ls=":", color=INK)
    # the head of train 1 moves from x = 0 to x = 2L
    vec(ax, (0.0, -0.3), (2 * L, -0.3), color=C1, lw=2.2)
    ax.text(L, -0.55, "голова поезда 1 проходит $2l$ относительно поезда 2", ha="center", va="top", color=C1,
            fontsize=10.5)
    ax.text(L, -1.05, "$v_{\\text{отн}}=v_1-v_2$", ha="center", va="top", color=C1, fontsize=12)
    dim(ax, 0, L, 1.75, "$l$", dy=0.05)
    dim(ax, -L, 0, 2.3, "$l$", dy=0.05)
    dim(ax, L, 2 * L, 2.3, "$l$", dy=0.05)
    save(fig, "meeting-overtake-frames.png")


# 7. overtaking: x(t)
def overtake_xt():
    v1, v2, L = 15.0, 10.0, 150.0
    t = np.linspace(0, 70, 200)
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    # x is counted from the tail of train 1 at the start of overtaking
    ax.plot(t, L + v1 * t, color=C1, lw=2.4, label="поезд 1, голова")
    ax.plot(t, v1 * t, color=C1, lw=2.4, ls="--", label="поезд 1, хвост")
    ax.plot(t, 2 * L + v2 * t, color=C2, lw=2.4, label="поезд 2, голова")
    ax.plot(t, L + v2 * t, color=C2, lw=2.4, ls="--", label="поезд 2, хвост")
    T = 2 * L / (v1 - v2)
    ax.axvspan(0, T, color=C3, alpha=0.16, lw=0)
    ax.plot([0], [L], "o", color=INK, zorder=5)
    ax.plot([T], [v1 * T], "o", color=INK, zorder=5)
    ax.annotate("начало обгона:\nголова 1 у хвоста 2", (0, L), (3, 420), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("конец обгона:\nхвост 1 у головы 2", (T, v1 * T), (36, 1080), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("", (T, 1180), (0, 1180), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.6))
    ax.text(T / 2, 1200, "$t=60$ с", ha="center", color=C3, fontsize=11)
    ax.set_xlim(0, 72)
    ax.set_ylim(0, 1300)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    arrows(ax, "$t$, с", "$x$, м")
    ax.set_title("Обгон: график $x(t)$", pad=22)
    save(fig, "meeting-overtake-xt.png")


# 8. river scheme
def river_scheme():
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.3, 4.6)
    ax.axis("off")
    ax.add_patch(Rectangle((1.5, 0.0), 9.0, 4.0, fc=tint(SKY, 0.8), ec="none", zorder=0))
    ax.plot([1.5, 10.5], [4.0, 4.0], color=INK, lw=1.5)
    ax.plot([1.5, 10.5], [0.0, 0.0], color=INK, lw=1.5)
    ax.plot([1.5, 1.5], [-0.1, 4.1], color=INK, lw=1.2, ls="--")
    ax.plot([10.5, 10.5], [-0.1, 4.1], color=INK, lw=1.2, ls="--")
    ax.text(1.5, 4.25, "A", ha="center", fontsize=13)
    ax.text(10.5, 4.25, "B", ha="center", fontsize=13)
    vec(ax, (0.2, 4.35), (1.1, 4.35), color=C1)
    ax.text(0.65, 4.55, "течение", ha="center", fontsize=8, color=C1)
    rows = [
        (3.3, "лодка по течению", "$v_{\\text{л}}+v_{\\text{р}}$", 1.0, C1),
        (2.0, "плот", "$v_{\\text{р}}$", 1.0, C3),
        (0.7, "лодка против течения", "$v_{\\text{л}}-v_{\\text{р}}$", -1.0, C2),
    ]
    for y, name, lab, sgn, c in rows:
        x0 = 3.0 if sgn > 0 else 9.2
        ln = {C1: 3.4, C3: 1.4, C2: 2.0}[c]
        ax.add_patch(Rectangle((x0 - (0 if sgn > 0 else 0.6), y - 0.13), 0.6, 0.26, fc=c, ec=INK, alpha=0.8, zorder=3))
        p = (x0 + 0.65, y) if sgn > 0 else (x0 - 0.05, y)
        vec(ax, p, (p[0] + sgn * ln, y), color=c, lw=2.4)
        ax.text(x0 if sgn > 0 else x0, y + 0.22, name, fontsize=9.5, color=c, ha="left" if sgn > 0 else "right")
        ax.text(p[0] + sgn * ln / 2, y - 0.32, lab, ha="center", va="top", fontsize=11, color=c)
    dim(ax, 1.5, 10.5, -0.2, "$L$", dy=-0.05)
    save(fig, "meeting-river-scheme.png")


# 9. river x(t) for the three trips
def river_xt():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)
    data = [
        ("Лодка по течению", C1, lambda t: t / 3, 3, "3 ч"),
        ("Плот", C3, lambda t: t / 12, 12, "12 ч"),
        ("Лодка против течения", C2, lambda t: 1 - t / 6, 6, "6 ч"),
    ]
    for ax, (name, c, f, T, lab) in zip(axs, data):
        t = np.linspace(0, T, 50)
        ax.plot(t, f(t), color=c, lw=2.4)
        ax.plot(T, f(T), "o", color=INK, zorder=5)
        ax.plot([T, T], [0, f(T)], ls=":", color=GREY, lw=1)
        ax.tick_params(labelleft=True)
        ax.set_xlim(0, 13)
        ax.set_ylim(-0.02, 1.15)
        ax.set_xticks([0, 3, 6, 9, 12])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["A", "B"])
        ax.set_title(name, fontsize=11, pad=22)
        arrows(ax, "$t$, ч", "$x$")
    save(fig, "meeting-river-xt.png")


if __name__ == "__main__":
    oncoming_frames()
    oncoming_xt()
    distance_between()
    approach_xt()
    chase_xt()
    overtake_frames()
    overtake_xt()
    river_scheme()
    river_xt()
