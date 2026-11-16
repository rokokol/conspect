"""Figures of section f09, note "Вращательное движение" (lessons 87-91).

Run: python3 rotation.py
PNG files with the prefix rotation- go to
content/09. Вращение, колебания, волны/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "09. Вращение, колебания, волны"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, WARM, num, saver, tint

GRID = ASH
GREY = MUTED
GOLD = WARM
STEEL = METAL


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def blank_row(n, w, h, xlim, ylim):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    for ax in np.atleast_1d(axes):
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def circ(ax, c, r, **kw):
    kw.setdefault("fill", False)
    kw.setdefault("ec", INK)
    kw.setdefault("lw", 1.6)
    ax.add_patch(Circle(c, r, **kw))


def dot(ax, p, color=INK, s=28, **kw):
    ax.plot(*p, "o", color=color, ms=s ** 0.5, **kw)


def spin(ax, c, r, a0, a1, color=BLUE, lw=1.8, ccw=True):
    """Arc arrow around c from angle a0 to a1 (degrees), tip at the end."""
    ts = np.radians(np.linspace(a0, a1, 60))
    xs, ys = c[0] + r * np.cos(ts), c[1] + r * np.sin(ts)
    ax.plot(xs[:-2], ys[:-2], color=color, lw=lw)
    arrow(ax, (xs[-3], ys[-3]), (xs[-1], ys[-1]), color=color, lw=lw, scale=14)


def gear_poly(cx, cy, r, z, phase=0.0, **kw):
    """Gear outline with z teeth; r is the pitch radius, phase the angle of a tooth centre."""
    m = 2 * r / z
    r_out, r_in = r + 0.8 * m, r - 0.9 * m
    p = 2 * np.pi / z
    pts = []
    for k in range(z):
        a = phase + k * p
        for da, rr in ((-0.32, r_in), (-0.17, r_out), (0.17, r_out), (0.32, r_in), (0.5, r_in)):
            pts.append((cx + rr * np.cos(a + da * p), cy + rr * np.sin(a + da * p)))
    kw.setdefault("fc", LIGHT)
    kw.setdefault("ec", INK)
    kw.setdefault("lw", 1.4)
    return Polygon(pts, closed=True, **kw)


def belt(ax, c1, r1, c2, r2, color=INK, lw=2.2, ls="-", crossed=False):
    """Belt: the two outer tangent lines of two circles."""
    d = np.subtract(c2, c1)
    L = np.hypot(*d)
    phi = np.arctan2(d[1], d[0])
    alpha = np.arccos((r1 - r2) / L)
    for s in (1, -1):
        th = phi + s * alpha
        u = np.array([np.cos(th), np.sin(th)])
        p1, p2 = np.add(c1, r1 * u), np.add(c2, r2 * u)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, ls=ls, solid_capstyle="round")


def clock_dial(ax, c, r, hand_angle, hand_len, color, lw=3.0, ticks=12):
    """Clock dial; hand_angle in degrees measured clockwise from 12 o'clock."""
    circ(ax, c, r, ec=INK, lw=1.8)
    for k in range(ticks):
        a = np.radians(90 - 360 * k / ticks)
        L = 0.13 * r if k % 3 else 0.2 * r
        ax.plot(
            [c[0] + (r - L) * np.cos(a), c[0] + r * np.cos(a)],
            [c[1] + (r - L) * np.sin(a), c[1] + r * np.sin(a)],
            color=INK, lw=1.2,
        )
    a = np.radians(90 - hand_angle)
    ax.plot([c[0], c[0] + hand_len * np.cos(a)], [c[1], c[1] + hand_len * np.sin(a)],
            color=color, lw=lw, solid_capstyle="round")
    dot(ax, c, INK, 30)


# --- 1. Axis of rotation on a cylinder ---------------------------------------
def axis_cylinder():
    fig, ax = blank(4.6, 5.1, (-3.2, 3.8), (-2.2, 4.5))
    R, h = 2.0, 1.0
    top, bot = 1.2, 0.2
    ax.add_patch(Ellipse((0, top), 2 * R, 0.9 * R, fc=LIGHT, ec=INK, lw=1.6, zorder=2))
    ax.plot([-R, -R], [bot, top], color=INK, lw=1.6, zorder=1)
    ax.plot([R, R], [bot, top], color=INK, lw=1.6, zorder=1)
    # The whole bottom ellipse is filled: its front half lies outside the side rectangle.
    ax.add_patch(Ellipse((0, bot), 2 * R, 0.9 * R, fc=LIGHT, ec=INK, lw=1.6, zorder=0))
    ax.add_patch(Rectangle((-R, bot), 2 * R, top - bot, fc=LIGHT, ec="none", zorder=1))
    ax.add_patch(Ellipse((0, top), 2 * R, 0.9 * R, fc=LIGHT, ec=INK, lw=1.6, zorder=2))
    for rr, col in ((1.2, BLUE), (1.75, GREEN)):
        ax.add_patch(Ellipse((0, top), 2 * rr, 0.9 * rr, fill=False, ec=col, lw=1.4, ls="--", zorder=3))
    ax.add_patch(Ellipse((0, bot), 2 * 1.75, 0.9 * 1.75, fill=False, ec=RED, lw=1.4, ls="--", zorder=0))
    # axis
    ax.plot([0, 0], [top, 3.4], color=INK, lw=1.4, ls=(0, (8, 2, 1.5, 2)), zorder=4)
    ax.plot([0, 0], [-1.4, bot], color=INK, lw=1.4, ls=(0, (8, 2, 1.5, 2)), zorder=0)
    ax.plot([0, 0], [bot, top], color=GREY, lw=1.0, ls=":", zorder=1)
    dot(ax, (0, top), INK, 26, zorder=5)
    dot(ax, (0, bot), INK, 26, zorder=1)
    # points
    pa = (1.2 * np.cos(np.radians(-40)), top + 0.45 * 1.2 * np.sin(np.radians(-40)))
    pb = (1.75 * np.cos(np.radians(-125)), top + 0.45 * 1.75 * np.sin(np.radians(-125)))
    pc = (1.75 * np.cos(np.radians(-25)), bot + 0.45 * 1.75 * np.sin(np.radians(-25)))
    for p, col, nm in ((pa, BLUE, "A"), (pb, GREEN, "B"), (pc, RED, "C")):
        ax.plot(*p, "o", color=col, ms=7, zorder=5)
        ax.text(p[0] + 0.12, p[1] - 0.08, nm, color=col, fontsize=12, va="top", zorder=6)
    ax.text(0.14, 3.2, "O$'$", fontsize=12)
    ax.text(-0.42, top + 0.08, "O", fontsize=12, zorder=6)
    ax.text(0.0, -1.85, "ось вращения", ha="center", fontsize=11, color=INK)
    spin(ax, (0, 3.75), 0.5, 200, -20, color=BLUE, ccw=False)
    save(fig, "rotation-axis-cylinder.png")


# --- 2. Translation versus rotation ------------------------------------------
def translation_rotation():
    fig, (a, b) = blank_row(2, 8.6, 3.6, (-3.4, 3.4), (-2.6, 2.6))
    a.set_title("Поступательное: все точки одинаково", color=INK, fontsize=11)
    a.add_patch(Rectangle((-2.2, -0.6), 2.2, 1.2, fc=LIGHT, ec=INK, lw=1.6))
    pts = [(-1.9, 0.35), (-1.1, 0.0), (-0.4, -0.35)]
    for (x, y), col in zip(pts, (BLUE, GREEN, RED)):
        dot(a, (x, y), col, 30)
        arrow(a, (x, y), (x + 2.4, y), color=col, lw=1.8)
    a.text(0, -2.5, "пути и скорости точек равны", ha="center", fontsize=10.5, color=INK)
    b.set_title("Вращательное: точки по окружностям", color=INK, fontsize=11)
    circ(b, (0, 0), 2.1, fc=LIGHT)
    for rr, col in ((0.7, BLUE), (1.5, GREEN)):
        circ(b, (0, 0), rr, ec=col, ls="--", lw=1.3)
    dot(b, (0, 0), INK, 30)
    dot(b, (0.7, 0), BLUE, 30)
    dot(b, (0, 1.5), GREEN, 30)
    arrow(b, (0.7, 0), (0.7, 0.55), color=BLUE)
    arrow(b, (0, 1.5), (-1.1, 1.5), color=GREEN)
    spin(b, (0, 0), 2.45, 25, 75, color=INK)
    b.text(0, -2.5, "пути и скорости точек разные", ha="center", fontsize=10.5, color=INK)
    save(fig, "rotation-translation-rotation.png")


# --- 3. Rolling wheel: translation plus rotation -----------------------------
def rolling_cycloid():
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    R = 1.0
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(R * (t - np.sin(t)), R * (1 - np.cos(t)), color=RED, lw=2.0, label="точка обода")
    ax.plot([0, 2 * np.pi * R], [R, R], color=BLUE, lw=1.6, ls="--", label="ось (центр колеса)")
    for tt, al in ((0, 0.9), (np.pi / 2, 0.55), (np.pi, 0.55), (3 * np.pi / 2, 0.55), (2 * np.pi, 0.9)):
        cx = R * tt
        ax.add_patch(Circle((cx, R), R, fill=False, ec=GREY, lw=1.3, alpha=al))
        ax.plot([cx, R * (tt - np.sin(tt))], [R, R * (1 - np.cos(tt))], color=GREY, lw=1.0, alpha=al)
        dot(ax, (cx, R), BLUE, 16)
        dot(ax, (R * (tt - np.sin(tt)), R * (1 - np.cos(tt))), RED, 22)
    ax.axhline(0, color=INK, lw=1.2)
    ax.set_aspect("equal")
    ax.set_xlim(-1.3, 7.6)
    ax.set_ylim(-0.3, 2.35)
    ax.axis("off")
    ax.legend(loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.02))
    save(fig, "rotation-rolling-cycloid.png")


# --- 4. Clock hands and their periods ----------------------------------------
def clock_periods():
    fig, axes = blank_row(3, 9.0, 3.4, (-1.5, 1.5), (-1.9, 1.5))
    data = [
        ("секундная стрелка", "T = 1 мин", 60, 1.0, RED),
        ("минутная стрелка", "T = 1 ч", 150, 0.95, BLUE),
        ("часовая стрелка", "T = 12 ч", 240, 0.62, GREEN),
    ]
    for ax, (name, per, ang, ln, col) in zip(axes, data):
        clock_dial(ax, (0, 0), 1.2, ang, ln, col)
        spin(ax, (0, 0), 1.38, 90, 20, color=col, ccw=False)
        ax.text(0, -1.55, name, ha="center", fontsize=11, color=INK)
        ax.text(0, -1.95, per, ha="center", fontsize=12, color=col, fontweight="bold")
    for ax in axes:
        ax.set_ylim(-2.2, 1.55)
    save(fig, "rotation-clock-periods.png")


# --- 5. nu(T) hyperbola ------------------------------------------------------
def hyperbola():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    T = np.linspace(0.04, 1.3, 400)
    ax.plot(T, 1 / T, color=BLUE, lw=2.2)
    pts = [
        (0.05, "винт вертолёта", (0.09, 19.0)),
        (0.125, "вал двигателя", (0.17, 10.5)),
        (1 / 3, "колесо велосипеда", (0.42, 7.2)),
        (0.5, "вентилятор", (0.66, 4.8)),
        (0.962, "колесо-игрушка", (0.8, 2.6)),
    ]
    for t, name, xy in pts:
        v = 1 / t
        ax.plot([t, t], [0, v], color=GRID, lw=1.0, zorder=0)
        ax.plot([0, t], [v, v], color=GRID, lw=1.0, zorder=0)
        dot(ax, (t, v), RED, 30, zorder=3)
        ax.annotate(f"{name}\nT = {num(t, '.3g')} с, $\\nu$ = {num(v, '.3g')} об/с", (t, v),
                    xytext=xy, fontsize=8.6, color=INK, ha="left", va="bottom",
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.set_xlim(0, 1.45)
    ax.set_ylim(0, 24)
    ax.set_xlabel("$T$, с")
    ax.set_ylabel("$\\nu$, об/с")
    ax.set_title("Частота обратна периоду: $\\nu = 1/T$")
    ax.grid(color=GRID, lw=0.7)
    save(fig, "rotation-frequency-period-hyperbola.png")


# --- 6. Linear velocity vectors ---------------------------------------------
def linear_velocity_vectors():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 4.4))
    for ax in (a, b):
        ax.set_aspect("equal")
        ax.axis("off")
    a.set_xlim(-3.3, 3.3)
    a.set_ylim(-3.1, 3.4)
    ra, rb = 1.1, 2.4
    for rr in (ra, rb):
        circ(a, (0, 0), rr, ec=GREY, ls="--", lw=1.4)
    dot(a, (0, 0), INK, 30)
    a.text(-0.32, -0.36, "O", fontsize=12)
    tha, thb = np.radians(35), np.radians(115)
    A = (ra * np.cos(tha), ra * np.sin(tha))
    B = (rb * np.cos(thb), rb * np.sin(thb))
    for P, th, rr, col, nm in ((A, tha, ra, BLUE, "A"), (B, thb, rb, GREEN, "B")):
        a.plot([0, P[0]], [0, P[1]], color=col, lw=1.4)
        dot(a, P, col, 34)
        t = np.array([-np.sin(th), np.cos(th)])
        arrow(a, P, np.add(P, 0.62 * rr * t), color=RED, lw=2.2)
        off = np.array([np.cos(th), np.sin(th)]) * 0.28
        a.text(P[0] + off[0] + 0.05, P[1] + off[1] + 0.03, nm, color=col, fontsize=13, fontweight="bold")
    a.text(0.75 * ra * np.cos(tha) - 0.2, 0.25 * ra * np.sin(tha) - 0.5, "$R_A$", color=BLUE, fontsize=12)
    a.text(0.5 * B[0] - 0.55, 0.5 * B[1] + 0.05, "$R_B$", color=GREEN, fontsize=12)
    a.text(A[0] + 0.62 * ra * (-np.sin(tha)) + 0.05, A[1] + 0.62 * ra * np.cos(tha) - 0.05, "$\\vec v_A$",
           color=RED, fontsize=12)
    a.text(B[0] + 0.62 * rb * (-np.sin(thb)) - 0.4, B[1] + 0.62 * rb * np.cos(thb) + 0.12, "$\\vec v_B$",
           color=RED, fontsize=12)
    spin(a, (0, 0), 2.85, -50, 10, color=INK)
    a.set_title("$R_B > R_A$, поэтому $v_B > v_A$", fontsize=11)

    b.set_xlim(-2.0, 2.0)
    b.set_ylim(-2.1, 2.3)
    circ(b, (0, 0), 1.15, ec=GREY, ls="--", lw=1.4)
    dot(b, (0, 0), INK, 30)
    for k, deg in enumerate((0, 90, 180, 270)):
        th = np.radians(deg)
        P = (1.15 * np.cos(th), 1.15 * np.sin(th))
        t = np.array([-np.sin(th), np.cos(th)])
        dot(b, P, BLUE, 30)
        arrow(b, P, np.add(P, 0.85 * t), color=RED, lw=2.2)
    b.set_title("Точка $A$: $\\vec v$ меняет направление", fontsize=11)
    spin(b, (0, 0), 1.55, 20, 70, color=INK)
    save(fig, "rotation-linear-velocity-vectors.png")


# --- 7. v(R) at fixed period -------------------------------------------------
def v_vs_radius():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    R = np.linspace(0, 10, 100)
    for T, col in ((0.5, GREY), (0.96, RED), (2.0, GREEN)):
        lw = 2.4 if T == 0.96 else 1.6
        ax.plot(R, 2 * np.pi * R / T, color=col, lw=lw, label=f"$T$ = {num(T, '')} с")
    for r in (3, 7):
        v = 2 * np.pi * r / 0.96
        ax.plot([r, r], [0, v], color=GRID, lw=1.0, zorder=0)
        ax.plot([0, r], [v, v], color=GRID, lw=1.0, zorder=0)
        dot(ax, (r, v), RED, 34, zorder=3)
        ax.annotate(f"$R$ = {num(r, '')} см, $v$ = {num(v, 1)} см/с", (r, v), xytext=(10, -16),
                    textcoords="offset points", ha="left", va="top", fontsize=9, color=INK,
                    bbox=dict(fc=PAPER, ec="none", pad=1.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 130)
    ax.set_xlabel("$R$, см")
    ax.set_ylabel("$v$, см/с")
    ax.set_title("При постоянном $T$: $v = \\dfrac{2\\pi}{T}R$ — прямая")
    ax.grid(color=GRID, lw=0.7)
    ax.legend(loc="upper left", frameon=False)
    save(fig, "rotation-linear-speed-vs-radius.png")


# --- 8. v(T) at fixed radius -------------------------------------------------
def v_vs_period():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    T = np.linspace(0.3, 3.0, 300)
    for R, col in ((3, BLUE), (7, GREEN)):
        ax.plot(T, 2 * np.pi * R / T, color=col, lw=2.0, label=f"$R$ = {R} см")
        v = 2 * np.pi * R / 0.96
        dot(ax, (0.96, v), RED, 34, zorder=3)
        ax.annotate(num(v, 1) + " см/с", (0.96, v), xytext=(8, 4), textcoords="offset points",
                    fontsize=9.5, color=INK)
    ax.set_xlim(0.3, 3.0)
    ax.set_ylim(0, 160)
    ax.set_xlabel("$T$, с")
    ax.set_ylabel("$v$, см/с")
    ax.set_title("При постоянном $R$: $v \\sim 1/T$ — гипербола")
    ax.grid(color=GRID, lw=0.7)
    ax.legend(frameon=False)
    save(fig, "rotation-linear-speed-vs-period.png")


# --- 9. Stroboscope ----------------------------------------------------------
def stroboscope():
    fig, axes = plt.subplots(3, 5, figsize=(8.6, 5.6))
    rows = [(1.0, "Интервал = $T$:\nметка стоит"), (0.9, "Интервал = $0{,}9\\,T$:\nметка идёт назад"),
            (1.1, "Интервал = $1{,}1\\,T$:\nметка идёт вперёд")]
    for i, (ratio, label) in enumerate(rows):
        for k in range(5):
            ax = axes[i, k]
            ax.set_aspect("equal")
            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)
            ax.axis("off")
            circ(ax, (0, 0), 1.0, fc=LIGHT)
            ang = 2 * np.pi * ratio * k + np.pi / 2
            P = (0.78 * np.cos(ang), 0.78 * np.sin(ang))
            ax.plot([0, P[0]], [0, P[1]], color=RED, lw=2.2)
            dot(ax, P, RED, 40)
            dot(ax, (0, 0), INK, 20)
            if i == 0:
                ax.set_title(f"вспышка {k + 1}", fontsize=10)
        axes[i, 0].text(-1.45, 0, label, va="center", ha="right", fontsize=10.5, color=INK)
    fig.subplots_adjust(left=0.2)
    fig.text(0.5, 0.005, "Колесо вращается против часовой стрелки; на кадрах видно только положение метки во время вспышки",
             ha="center", fontsize=9, color=INK)
    save(fig, "rotation-stroboscope.png")


# --- 10. Transmissions -------------------------------------------------------
def transmissions():
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 7.2))
    for ax in axes.flat:
        ax.set_aspect("equal")
        ax.axis("off")
    # belt
    a = axes[0, 0]
    a.set_xlim(-1.8, 5.6)
    a.set_ylim(-2.2, 2.4)
    c1, r1, c2, r2 = (0.0, 0.0), 0.7, (3.4, 0.0), 1.5
    belt(a, c1, r1, c2, r2)
    circ(a, c1, r1, fc=LIGHT)
    circ(a, c2, r2, fc=LIGHT)
    dot(a, c1, INK, 24)
    dot(a, c2, INK, 24)
    spin(a, c1, 1.0, 130, 40, color=BLUE, ccw=False)
    spin(a, c2, 1.85, 130, 40, color=BLUE, ccw=False)
    a.text(0, -1.0, "$R_1$", ha="center", color=INK, fontsize=12)
    a.text(3.4, -1.9, "$R_2$", ha="center", color=INK, fontsize=12)
    a.set_title("Ременная: оба шкива в одну сторону", fontsize=11)
    # chain
    b = axes[0, 1]
    b.set_xlim(-1.8, 5.6)
    b.set_ylim(-2.2, 2.4)
    c1, r1, c2, r2 = (0.0, 0.0), 0.75, (3.3, 0.0), 1.55
    belt(b, c1, r1 + 0.05, c2, r2 + 0.05, color=STEEL, lw=4.0, ls=(0, (1.2, 0.9)))
    b.add_patch(gear_poly(*c1, r1, 10, phase=0.0))
    b.add_patch(gear_poly(*c2, r2, 20, phase=0.0))
    dot(b, c1, INK, 24)
    dot(b, c2, INK, 24)
    spin(b, c1, 1.15, 130, 40, color=BLUE, ccw=False)
    spin(b, c2, 2.0, 130, 40, color=BLUE, ccw=False)
    b.text(0, -1.3, "$z_1$", ha="center", color=INK, fontsize=12)
    b.text(3.3, -2.15, "$z_2$", ha="center", color=INK, fontsize=12)
    b.set_title("Цепная: звёздочки и цепь", fontsize=11)
    # friction
    f = axes[1, 0]
    f.set_xlim(-2.4, 5.0)
    f.set_ylim(-2.4, 2.4)
    r1, r2 = 1.7, 0.85
    c1, c2 = (0.0, 0.0), (r1 + r2, 0.0)
    circ(f, c1, r1, fc=LIGHT)
    circ(f, c2, r2, fc=tint(COPPER, 0.5))
    dot(f, c1, INK, 24)
    dot(f, c2, INK, 24)
    spin(f, c1, r1 + 0.35, 140, 50, color=BLUE, ccw=False)
    spin(f, c2, r2 + 0.35, 40, 130, color=RED, ccw=True)
    arrow(f, (c2[0] + r2 + 0.1 + 1.0, 0.0), (c2[0] + r2 + 0.1, 0.0), color=GREEN, lw=2.2)
    f.text(c2[0] + r2 + 0.95, 0.25, "прижим", color=GREEN, ha="center", fontsize=10)
    f.plot([r1, r1], [-0.35, 0.35], color=RED, lw=3)
    f.text(r1 - 0.15, -0.85, "трение", color=RED, fontsize=10, ha="right")
    f.text(0, -r1 - 0.5, "$R_1$", ha="center", color=INK, fontsize=12)
    f.text(c2[0], -r2 - 0.55, "$R_2$", ha="center", color=INK, fontsize=12)
    f.set_title("Фрикционная: валики в разные стороны", fontsize=11)
    # gears
    g = axes[1, 1]
    g.set_xlim(-2.4, 6.4)
    g.set_ylim(-3.3, 3.3)
    z1, z2 = 12, 18
    r1 = 1.3
    r2 = r1 * z2 / z1
    p2 = 2 * np.pi / z2
    g.add_patch(gear_poly(0, 0, r1, z1, phase=0.0))
    g.add_patch(gear_poly(r1 + r2, 0, r2, z2, phase=np.pi + p2 / 2))
    dot(g, (0, 0), INK, 24)
    dot(g, (r1 + r2, 0), INK, 24)
    spin(g, (0, 0), r1 + 0.55, 130, 50, color=BLUE, ccw=False)
    spin(g, (r1 + r2, 0), r2 + 0.55, 40, 130, color=RED, ccw=True)
    g.text(0, -0.6, "$z_1$", ha="center", color=INK, fontsize=12)
    g.text(r1 + r2, -0.6, "$z_2$", ha="center", color=INK, fontsize=12)
    g.set_title("Зубчатая: шестерни в разные стороны", fontsize=11)
    fig.tight_layout()
    save(fig, "rotation-transmissions.png")


def transmissions_more():
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6))
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    # conical
    a = axes[0]
    a.set_xlim(-3.6, 2.6)
    a.set_ylim(-1.6, 3.6)
    a.plot([-3.2, -0.8], [0, 0], color=INK, lw=3)
    a.plot([0, 0], [0.8, 3.2], color=INK, lw=3)
    a.add_patch(Polygon([(-0.8, -0.8), (-0.8, 0.8), (-1.6, 1.6), (-1.6, -1.6)], fc=LIGHT, ec=INK, lw=1.6))
    a.add_patch(Polygon([(-0.8, 0.8), (0.8, 0.8), (1.6, 1.6), (-1.6, 1.6)], fc=tint(COPPER, 0.5), ec=INK, lw=1.6))
    a.plot([-1.6, -0.8], [-0.0, 0.0], color=INK, lw=0.0)
    spin(a, (-2.6, 0), 0.55, 60, 300, color=BLUE, ccw=True)
    spin(a, (0, 2.6), 0.55, 330, 570, color=RED, ccw=True)
    a.set_title("Коническая: оси под углом", fontsize=11)
    # worm
    b = axes[1]
    b.set_xlim(-3.9, 3.0)
    b.set_ylim(-3.6, 2.2)
    b.add_patch(Rectangle((-2.6, 0.9), 5.2, 0.8, fc=LIGHT, ec=INK, lw=1.6))
    for x in np.arange(-2.2, 2.5, 0.5):
        b.plot([x, x + 0.3], [0.9, 1.7], color=INK, lw=1.4)
    b.plot([-2.9, 2.9], [1.3, 1.3], color=INK, lw=1.0, ls=(0, (8, 2, 1.5, 2)))
    zw = 20
    b.add_patch(gear_poly(0, -0.95, 1.85, zw, phase=np.pi / 2 + np.pi / zw))
    dot(b, (0, -0.95), INK, 24)
    spin(b, (-3.3, 1.3), 0.4, 60, 300, color=BLUE, ccw=True)
    spin(b, (0, -0.95), 0.85, 30, 150, color=RED, ccw=True)
    b.set_title("Червячная: замедление в $z$ раз", fontsize=11)
    # rack
    c = axes[2]
    c.set_xlim(-3.2, 3.6)
    c.set_ylim(-2.4, 2.6)
    zg = 14
    rg = 1.1
    # A gear tooth points down at x = 0 and the rack gap is placed under it
    c.add_patch(gear_poly(0, rg + 0.05, rg, zg, phase=-np.pi / 2))
    dot(c, (0, rg + 0.05), INK, 24)
    m = 2 * rg / zg
    pitch = np.pi * m
    # Rack gaps sit at x = (k + 0.975 - 0.975) * pitch, so one gap is exactly at x = 0
    xs = np.arange(-6 * pitch + 0.025 * pitch, 3.1, pitch)
    top = 0.05
    c.add_patch(Rectangle((-3.0, top - 0.75), 6.3, 0.75 - 0.9 * m, fc=LIGHT, ec=INK, lw=1.6))
    for x in xs:
        c.add_patch(Polygon([(x + 0.1 * pitch, top - 0.9 * m), (x + 0.3 * pitch, top + 0.8 * m),
                             (x + 0.65 * pitch, top + 0.8 * m), (x + 0.85 * pitch, top - 0.9 * m)],
                            fc=LIGHT, ec=INK, lw=1.2))
    spin(c, (0, rg + 0.05), 0.6, 40, 140, color=BLUE, ccw=True)
    arrow(c, (-0.4, -1.3), (1.6, -1.3), color=RED, lw=2.2)
    c.text(0.6, -1.85, "рейка", ha="center", color=RED, fontsize=10.5)
    c.set_title("Реечная: вращение — в движение", fontsize=11)
    fig.tight_layout()
    save(fig, "rotation-transmissions-more.png")


# --- 11. Belt: nu2 against R2 ------------------------------------------------
def belt_frequency():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    R2 = np.linspace(4, 60, 300)
    ax.plot(R2, 1200 * 8 / R2, color=BLUE, lw=2.2)
    dot(ax, (32, 300), RED, 34, zorder=3)
    ax.plot([32, 32], [0, 300], color=GRID, lw=1.0, zorder=0)
    ax.plot([0, 32], [300, 300], color=GRID, lw=1.0, zorder=0)
    ax.annotate("$R_2$ = 32 см, $\\nu_2$ = 300 об/мин", (32, 300), xytext=(10, 12), textcoords="offset points",
                fontsize=9.5, color=INK)
    dot(ax, (8, 1200), GREEN, 34, zorder=3)
    ax.annotate("шкив 1: $R_1$ = 8 см,\n$\\nu_1$ = 1200 об/мин", (8, 1200), xytext=(10, -8),
                textcoords="offset points", fontsize=9.5, color=INK, va="top")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 1500)
    ax.set_xlabel("радиус ведомого шкива $R_2$, см")
    ax.set_ylabel("$\\nu_2$, об/мин")
    ax.set_title("Больше радиус — меньше частота: $\\nu_2 = \\nu_1 R_1/R_2$")
    ax.grid(color=GRID, lw=0.7)
    save(fig, "rotation-belt-frequency-vs-radius.png")


# --- 12. Grinding wheel ------------------------------------------------------
def grinder():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
    a.set_aspect("equal")
    a.axis("off")
    a.set_xlim(-2.4, 3.6)
    a.set_ylim(-2.3, 2.5)
    # face-on view of the wheel
    circ(a, (0, 0), 1.6, fc=tint(COPPER, 0.5))
    circ(a, (0, 0), 0.45, fc=LIGHT)
    dot(a, (0, 0), INK, 24)
    a.plot([-1.6, 1.6], [0, 0], color=INK, lw=1.2)
    a.annotate("", (-1.6, -0.0), (1.6, 0.0), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    a.text(0, -0.75, "$d$ = 300 мм", ha="center", fontsize=11)
    ang = np.radians(50)
    P = (1.6 * np.cos(ang), 1.6 * np.sin(ang))
    dot(a, P, RED, 34, zorder=5)
    t = np.array([-np.sin(ang), np.cos(ang)])
    arrow(a, P, np.add(P, 1.3 * t), color=RED, lw=2.4)
    a.text(P[0] + 1.3 * t[0] + 0.08, P[1] + 1.3 * t[1] + 0.05, "$\\vec v$", color=RED, fontsize=13)
    spin(a, (0, 0), 1.95, -100, -30, color=BLUE, ccw=True)
    a.text(0, -2.35, "вал двигателя вращает круг с частотой $\\nu$", ha="center", fontsize=10)
    a.set_title("Точка рабочей поверхности", fontsize=11)
    # comparison
    labels = ["1400 об/мин", "2800 об/мин"]
    vals = [np.pi * 0.3 * 1400 / 60, np.pi * 0.3 * 2800 / 60]
    cols = [GREEN, RED]
    b.bar(labels, vals, color=cols, width=0.55)
    b.axhline(35, color=INK, lw=1.6, ls="--")
    b.text(-0.4, 36, "допустимо: 35 м/с", ha="left", fontsize=10)
    for i, v in enumerate(vals):
        b.text(i, v + 1, f"{v:.0f} м/с", ha="center", fontsize=11)
    b.set_ylim(0, 52)
    b.set_ylabel("$v$, м/с")
    b.set_title("Скорость точек круга", fontsize=11)
    b.grid(axis="y", color=GRID, lw=0.7)
    b.set_axisbelow(True)
    save(fig, "rotation-grinder.png")


# --- 13. Earth and latitude --------------------------------------------------
def earth():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 4.4), gridspec_kw={"width_ratios": [1, 1.25]})
    a.set_aspect("equal")
    a.axis("off")
    a.set_xlim(-2.1, 3.1)
    a.set_ylim(-2.0, 2.3)
    circ(a, (0, 0), 1.5, fc=LIGHT)
    # Equator seen at a slant: near half solid, far half dashed
    a.add_patch(Arc((0, 0), 3.0, 0.7, theta1=180, theta2=360, ec=INK, lw=1.4))
    a.add_patch(Arc((0, 0), 3.0, 0.7, theta1=0, theta2=180, ec=INK, lw=1.2, ls=(0, (4, 3))))
    a.plot([0, 0], [-1.95, 1.95], color=INK, lw=1.2, ls=(0, (8, 2, 1.5, 2)))
    # The resident stands on the near side of the equator, as on the board; v is tangent to the equator
    a.plot([0, 0], [0, -0.35], color=BLUE, lw=1.8)
    dot(a, (0, 0), INK, 24)
    dot(a, (0, -0.35), RED, 40, zorder=5)
    arrow(a, (0, -0.35), (1.6, -0.35), color=RED, lw=2.4)
    a.text(-0.1, -0.22, "$R$", color=BLUE, fontsize=12, ha="right")
    a.text(1.0, -0.72, "$\\vec v$", color=RED, fontsize=13)
    spin(a, (0, 0), 0.0 + 1.75, 70, 110, color=BLUE, ccw=True)
    a.text(-2.0, -1.75, "$T$ = 24 ч, $R$ = 6400 км", fontsize=10.5)
    a.set_title("Житель экватора", fontsize=11)
    phi = np.linspace(0, 90, 200)
    v0 = 2 * np.pi * 6400e3 / (24 * 3600)
    b.plot(phi, v0 * np.cos(np.radians(phi)), color=BLUE, lw=2.2)
    b.axhline(340, color=RED, lw=1.5, ls="--")
    b.text(89, 350, "скорость звука 340 м/с", color=RED, ha="right", fontsize=9.5)
    dot(b, (0, v0), INK, 34, zorder=3)
    b.annotate(f"экватор: {v0:.0f} м/с", (0, v0), xytext=(8, 4), textcoords="offset points", fontsize=9.5)
    b.set_xlim(0, 90)
    b.set_ylim(0, 520)
    b.set_xlabel("широта, градусы")
    b.set_ylabel("$v$, м/с")
    b.set_title("Скорость вращения Земли по широте", fontsize=11)
    b.grid(color=GRID, lw=0.7)
    save(fig, "rotation-earth-equator.png")


# --- 14. Clock hands problem -------------------------------------------------
def clock_hands_problem():
    fig, ax = blank(6.2, 4.6, (-2.0, 3.3), (-2.0, 2.3))
    c = (0.0, 0.0)
    clock_dial(ax, c, 1.75, 40, 1.5, BLUE, lw=3.4)
    cs = (0.0, -0.75)
    circ(ax, cs, 0.5, ec=GREY, lw=1.2)
    a_s = np.radians(90 - 240)
    tip_s = (cs[0] + 0.5 * np.cos(a_s), cs[1] + 0.5 * np.sin(a_s))
    ax.plot([cs[0], tip_s[0]], [cs[1], tip_s[1]], color=RED, lw=2.6, solid_capstyle="round")
    dot(ax, cs, RED, 22)
    a_m = np.radians(90 - 40)
    tip_m = (1.5 * np.cos(a_m), 1.5 * np.sin(a_m))
    dot(ax, tip_m, BLUE, 30)
    dot(ax, tip_s, RED, 30)
    tm = np.array([np.sin(a_m), -np.cos(a_m)])
    ts = np.array([np.sin(a_s), -np.cos(a_s)])
    arrow(ax, tip_m, np.add(tip_m, 0.5 * tm), color=BLUE, lw=2.4)
    arrow(ax, tip_s, np.add(tip_s, 1.7 * ts), color=RED, lw=2.4)
    ax.text(-0.05, 1.05, "$l_м = 3\\,l_с$", color=BLUE, fontsize=12, ha="right")
    ax.text(0.15, -0.6, "$l_с$", color=RED, fontsize=12)
    ax.text(tip_m[0] + 0.5 * tm[0] + 0.06, tip_m[1] + 0.5 * tm[1] - 0.05, "$\\vec v_м$", color=BLUE, fontsize=12)
    ax.text(tip_s[0] + 1.7 * ts[0] - 0.55, tip_s[1] + 1.7 * ts[1] - 0.05, "$\\vec v_с$", color=RED, fontsize=12)
    ax.text(0.0, -2.0, "$T_м$ = 60 мин, $T_с$ = 1 мин; стрелки скоростей не в масштабе", ha="center", fontsize=9.5)
    save(fig, "rotation-clock-hands-problem.png")


# --- 15. Four pulleys --------------------------------------------------------
def four_pulleys():
    fig, ax = blank(7.2, 6.9, (-2.2, 5.9), (-6.6, 3.4))
    k = 0.05
    r1, r2, r3, r4 = 8 * k, 32 * k, 11 * k, 55 * k
    c1 = (-0.4, 1.6)
    c23 = (2.6, 1.0)
    # Axle distance 4.5 > r2 + r4 = 4.35: pulleys 2 and 4 must not overlap
    c4 = (2.6, -3.5)
    belt(ax, c1, r1, c23, r2, color=INK, lw=2.4)
    circ(ax, c23, r2, fc=LIGHT, zorder=2)
    circ(ax, c4, r4, fc=LIGHT, zorder=1)
    belt(ax, c23, r3, c4, r4, color=RED, lw=2.4)
    circ(ax, c23, r3, fc=tint(COPPER, 0.5), zorder=3)
    circ(ax, c1, r1, fc=LIGHT, zorder=2)
    for c in (c1, c23, c4):
        dot(ax, c, INK, 22, zorder=4)
    for c, r, nm, ang, off in ((c1, r1, "1", 250, (-0.45, -0.25)), (c23, r2, "2", 25, (0.0, 0.1)),
                               (c23, r3, "3", 215, (-0.25, -0.3)), (c4, r4, "4", 300, (0.1, 0.0))):
        a = np.radians(ang)
        ax.plot([c[0], c[0] + r * np.cos(a)], [c[1], c[1] + r * np.sin(a)], color=BLUE, lw=1.4, zorder=5)
        ax.text(c[0] + 0.62 * r * np.cos(a) + off[0], c[1] + 0.62 * r * np.sin(a) + off[1], f"$R_{nm}$",
                color=BLUE, fontsize=11, zorder=6)
    ax.text(c1[0] - r1 - 0.15, c1[1] + 0.05, "шкив 1", ha="right", va="center", fontsize=10.5)
    ax.text(c23[0] + r2 + 0.2, c23[1] + 0.5, "шкивы 2 и 3\nна одном валу", ha="left", fontsize=10.5)
    ax.text(c4[0] - r4 + 0.45, c4[1] + 0.55, "шкив 4", ha="left", fontsize=10.5)
    spin(ax, c1, r1 + 0.32, 160, 100, color=GREEN, ccw=False)
    ax.text(-2.1, 2.9, "$\\nu_1$ = 1200 об/мин", color=GREEN, fontsize=10.5)
    ax.text(c4[0] - 1.6, c4[1] - 0.3, "$\\nu_4$ = ?", color=GREEN, fontsize=12, ha="center")
    ax.text(0.2, 0.55, "ремень 1", color=INK, fontsize=9.5)
    ax.text(0.5, -1.0, "ремень 2", color=RED, fontsize=9.5)
    save(fig, "rotation-four-pulleys.png")


# --- 16. Saw -----------------------------------------------------------------
def saw():
    fig, ax = blank(7.6, 5.0, (-4.9, 3.3), (-2.6, 2.6))
    # radii in the ratio of the diameters 600 : 300 : 120 mm
    Rs, r2, r1 = 1.6, 0.8, 0.32
    cp = (0.0, 0.0)
    cm = (-3.3, 0.0)
    ax.add_patch(gear_poly(0, 0, Rs, 40, phase=0.0, fc=tint(METAL, 0.8), zorder=0))
    ax.add_patch(Rectangle((cm[0] - 0.9, cm[1] - 0.55), 1.0, 1.1, fc=LIGHT, ec=INK, lw=1.4, zorder=0))
    belt(ax, cm, r1, cp, r2, color=INK, lw=2.2)
    circ(ax, cp, r2, fc=tint(COPPER, 0.5), zorder=3)
    circ(ax, cm, r1, fc=tint(COPPER, 0.5), zorder=3)
    dot(ax, cm, INK, 20, zorder=4)
    dot(ax, cp, INK, 22, zorder=4)
    ang = np.radians(50)
    P = (Rs * np.cos(ang), Rs * np.sin(ang))
    dot(ax, P, RED, 34, zorder=5)
    t = np.array([np.sin(ang), -np.cos(ang)])
    arrow(ax, P, np.add(P, 1.0 * t), color=RED, lw=2.4)
    ax.text(P[0] + t[0] + 0.08, P[1] + t[1] + 0.05, "$\\vec v$", color=RED, fontsize=13)
    a2 = np.radians(-100)
    ax.plot([0, Rs * np.cos(a2)], [0, Rs * np.sin(a2)], color=BLUE, lw=1.4, zorder=5)
    ax.text(0.08, -1.0, "$D/2$", color=BLUE, fontsize=11, zorder=6)
    ax.text(-0.18, 0.95, "$d_2$", color=INK, fontsize=11, zorder=6, ha="right")
    ax.text(cm[0] - 0.4, cm[1] - 0.75, "мотор\n$d_1$ = 120 мм\n$\\nu_1$ = 1200 об/мин", ha="center", va="top",
            fontsize=9.5)
    ax.text(1.6, -2.0, "пила $D$ = 600 мм\nна одной оси с шкивом $d_2$ = 300 мм", ha="center", fontsize=9.5)
    spin(ax, cm, r1 + 0.28, 150, 60, color=GREEN, ccw=False)
    save(fig, "rotation-saw.png")


# --- 17. Bicycle -------------------------------------------------------------
def bicycle():
    fig, ax = blank(8.6, 4.4, (-2.4, 9.6), (-2.6, 2.9))
    Rw = 2.0
    cw = (5.4, 0.0)
    r2 = 0.36
    r1 = r2 * 48 / 18
    cf = (0.6, 0.0)
    circ(ax, cw, Rw, ec=INK, lw=2.6)
    circ(ax, cw, Rw - 0.14, ec=GREY, lw=1.0)
    for a in range(0, 360, 30):
        aa = np.radians(a)
        ax.plot([cw[0], cw[0] + (Rw - 0.14) * np.cos(aa)], [cw[1], cw[1] + (Rw - 0.14) * np.sin(aa)],
                color=LIGHT, lw=0.9, zorder=0)
    belt(ax, cf, r1 + 0.05, cw, r2 + 0.05, color=STEEL, lw=3.6, ls=(0, (1.2, 0.9)))
    ax.add_patch(gear_poly(*cf, r1, 24, phase=0.0, zorder=3))
    ax.add_patch(gear_poly(*cw, r2, 9, phase=0.0, zorder=3))
    dot(ax, cf, INK, 22, zorder=4)
    dot(ax, cw, INK, 22, zorder=4)
    ax.plot([cf[0], cf[0] - 0.55], [cf[1], cf[1] - 0.8], color=INK, lw=3.0, zorder=4)
    ax.plot([cf[0], cf[0] + 0.55], [cf[1], cf[1] + 0.8], color=INK, lw=3.0, zorder=4)
    ax.plot([cf[0] - 0.55 - 0.25, cf[0] - 0.55 + 0.25], [cf[1] - 0.8] * 2, color=INK, lw=4.0, zorder=4)
    ax.plot([cf[0] + 0.55 - 0.25, cf[0] + 0.55 + 0.25], [cf[1] + 0.8] * 2, color=INK, lw=4.0, zorder=4)
    ax.plot([cf[0] + 0.8, cw[0]], [cf[1] + 1.5, cw[1]], color=INK, lw=0)
    spin(ax, cf, r1 + 0.55, 150, 60, color=BLUE, ccw=False)
    spin(ax, cw, Rw + 0.3, 150, 100, color=BLUE, ccw=False)
    bottom = (cw[0], cw[1] - Rw)
    dot(ax, bottom, GREEN, 26, zorder=5)
    arrow(ax, (cw[0] + 0.0, cw[1]), (cw[0] + 2.9, cw[1]), color=RED, lw=2.4)
    ax.text(cw[0] + 2.95, 0.12, "$\\vec v$", color=RED, fontsize=13)
    ax.plot([cw[0] - Rw, cw[0] + Rw], [cw[1]] * 2, color=BLUE, lw=0)
    ax.plot([cw[0], cw[0] + Rw * np.cos(np.radians(-60))], [cw[1], cw[1] + Rw * np.sin(np.radians(-60))],
            color=BLUE, lw=1.4)
    ax.text(cw[0] + 0.55, -0.95, "$d/2$", color=BLUE, fontsize=11)
    ax.text(cf[0], -r1 - 0.95, "$z_1$ = 48", ha="center", fontsize=10.5)
    ax.text(cw[0] - 0.9, -0.85, "$z_2$ = 18", ha="center", fontsize=10.5,
            bbox=dict(fc=PAPER, ec="none", pad=1.5))
    ax.text(cf[0] - 0.35, r1 + 0.95 + 0.25, "$\\nu_1$ = 1 об/с", ha="center", color=BLUE, fontsize=10.5)
    ax.text(cw[0], -Rw - 0.55, "колесо $d$ = 70 см", ha="center", fontsize=10.5)
    ax.plot([-2.2, 9.2], [-Rw, -Rw], color=INK, lw=1.2)
    save(fig, "rotation-bike-chain.png")


# --- 18. Bicycle: 24 gears ---------------------------------------------------
def bike_gears():
    front = [22, 32, 42]
    rear = [32, 28, 24, 21, 18, 15, 13, 11]
    D = 26 * 2.54 / 100
    nu = 75 / 60
    rows = []
    for i, zf in enumerate(front, 1):
        for j, zr in enumerate(rear, 1):
            v = np.pi * D * nu * zf / zr * 3.6
            rows.append((v, f"{i}-{j}", i))
    rows.sort()
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    cols = {1: BLUE, 2: GREEN, 3: RED}
    ax.bar(range(len(rows)), [r[0] for r in rows], color=[cols[r[2]] for r in rows], width=0.75)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r[1] for r in rows], rotation=90, fontsize=8.5)
    ax.set_ylabel("$v$, км/ч")
    ax.set_xlabel("передача (передняя-задняя), по возрастанию скорости")
    ax.set_title("Скорость велосипеда на 24 передачах при 75 об/мин")
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    from matplotlib.patches import Patch

    ax.legend(handles=[Patch(color=cols[i], label=f"передняя {i} ({front[i - 1]} зуб.)") for i in (1, 2, 3)],
              frameon=False, loc="upper left")
    save(fig, "rotation-bike-gears-speed.png")
    return rows


if __name__ == "__main__":
    axis_cylinder()
    translation_rotation()
    rolling_cycloid()
    clock_periods()
    hyperbola()
    linear_velocity_vectors()
    v_vs_radius()
    v_vs_period()
    stroboscope()
    transmissions()
    transmissions_more()
    belt_frequency()
    grinder()
    earth()
    clock_hands_problem()
    four_pulleys()
    saw()
    bicycle()
    rows = bike_gears()
    for r in rows:
        print(f"{r[1]}: {r[0]:.2f}")
