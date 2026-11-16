"""Figures of section f09 "Колебания. Маятники" and "Механические волны. Звук" (lessons 92-97).

Run: python3 oscillations_waves.py
PNG files with prefixes osc-, wave- and sound- go to
content/09. Вращение, колебания, волны/00. Вложения/
Curves marked "качественно" are sketches, not measurements.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle
from scipy.special import ellipk

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
from theme import ASH, BLUE, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, WARM, num, saver, tint

GRID = ASH
GREY = MUTED
GOLD = WARM
STONE = METAL


save = saver(OUT)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", scale=13, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def dim_h(ax, x0, x1, y, text, color=INK, dy=0.08, fs=11):
    """Horizontal dimension line with a label above."""
    arrow(ax, (x0, y), (x1, y), color=color, style="<|-|>", scale=10, lw=1.3)
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom", color=color, fontsize=fs)


def dim_v(ax, x, y0, y1, text, color=INK, dx=0.08, fs=11, ha="left"):
    arrow(ax, (x, y0), (x, y1), color=color, style="<|-|>", scale=10, lw=1.3)
    ax.text(x + dx, (y0 + y1) / 2, text, ha=ha, va="center", color=color, fontsize=fs)


def blank(w, h, xlim, ylim, n=1):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    axes = np.atleast_1d(axes)
    for ax in axes:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def spring_path(p, q, n=8, w=0.09):
    """Zig-zag polyline from p to q with n coils and half-width w."""
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    L = np.linalg.norm(d)
    u = d / L
    nrm = np.array([-u[1], u[0]])
    lead = 0.12 * L
    pts = [p, p + u * lead]
    body = L - 2 * lead
    for i in range(2 * n):
        t = lead + body * (i + 0.5) / (2 * n)
        pts.append(p + u * t + nrm * w * (1 if i % 2 == 0 else -1))
    pts += [q - u * lead, q]
    return np.array(pts)


def hatch_ceiling(ax, x0, x1, y, h=0.12, n=12):
    ax.plot([x0, x1], [y, y], color=INK, lw=2)
    for xx in np.linspace(x0, x1, n):
        ax.plot([xx, xx - h], [y, y + h], color=INK, lw=1)


def hatch_wall(ax, x, y0, y1, h=0.12, n=8):
    ax.plot([x, x], [y0, y1], color=INK, lw=2)
    for yy in np.linspace(y0, y1, n):
        ax.plot([x, x - h], [yy, yy - h], color=INK, lw=1)


# ---------------------------------------------------------------- oscillations


def osc_xt_sinusoid():
    T, A = 2.0, 5.0
    t = np.linspace(0, 2.5 * T, 800)
    x = A * np.cos(2 * np.pi * t / T)
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ax.plot(t, x, color=BLUE, lw=2.2)
    ax.axhline(0, color=INK, lw=1)
    for lvl in (A, -A):
        ax.axhline(lvl, color=GREY, lw=1, ls="--")
    ax.text(2.5 * T + 0.05, 0, "положение\nравновесия", va="center", fontsize=9.5, color=INK)
    dim_v(ax, 0.18, 0, A, "$A$", color=RED, dx=0.06)
    dim_v(ax, 0.18 + T + 0.55, -A, A, "$2A$", color=GREEN, dx=0.06)
    ax.annotate("", xy=(T, A + 1.3), xytext=(0, A + 1.3), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.4))
    ax.text(T / 2, A + 1.5, "$T$", ha="center", color=RED, fontsize=12)
    for xx in (0, T):
        ax.plot([xx, xx], [A, A + 1.3], color=RED, lw=0.9, ls=":")
    ax.set_ylim(-A - 1.5, A + 3)
    ax.set_xlim(0, 2.5 * T)
    ax.set_xlabel("$t$, с")
    ax.set_ylabel("$x$, см")
    ax.set_title("Колебание: отклонение от положения равновесия")
    ax.grid(color=GRID, lw=0.6)
    save(fig, "osc-xt-sinusoid.png")


def osc_amplitude_schemes():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.6))
    # pendulum
    ax = a1
    ax.set_xlim(-1.9, 1.9)
    ax.set_ylim(-2.25, 0.35)
    ax.set_aspect("equal")
    ax.axis("off")
    hatch_ceiling(ax, -0.4, 0.4, 0.0)
    L, th = 1.3, np.radians(28)
    for s, ls in ((0, "-"), (1, "--"), (-1, "--")):
        px, py = L * np.sin(s * th), -L * np.cos(s * th)
        ax.plot([0, px], [0, py], color=INK if s == 0 else GREY, lw=1.5, ls=ls)
        ax.add_patch(Circle((px, py), 0.09, color=BLUE if s == 0 else PAPER, ec=INK, lw=1.4, zorder=3))
    px = L * np.sin(th)
    yb = -L * np.cos(th)
    ax.plot([0, 0], [-L - 0.1, -L * 0.15], color=GREY, lw=0.8, ls=":")
    dim_h(ax, 0, px, -1.5, "$A$", color=RED, dy=0.03)
    dim_h(ax, -px, 0, -1.5, "$A$", color=RED, dy=0.03)
    dim_h(ax, -px, px, -1.72, "$2A$", color=GREEN, dy=-0.02)
    ax.get_children()
    ax.text(0.06, -0.35, r"$\alpha$", color=INK, fontsize=11)
    ax.text(0.0, -1.93, "положение равновесия — нижняя точка", ha="center", va="top", fontsize=9, color=INK)
    ax.set_title("Математический маятник")
    # spring pendulum
    ax = a2
    ax.set_xlim(-1.6, 2.5)
    ax.set_ylim(-2.6, 0.35)
    ax.set_aspect("equal")
    ax.axis("off")
    hatch_ceiling(ax, -0.5, 0.5, 0.0)
    ys = {"up": -1.05, "eq": -1.6, "down": -2.15}
    # Ghost weights have no fill and the spring is on top, so it stays visible down to the real weight
    ax.plot(*spring_path((0, 0), (0, ys["eq"] + 0.22), n=9, w=0.13).T, color=INK, lw=1.6, zorder=4)
    for k, y in ys.items():
        ax.add_patch(
            Rectangle((-0.22, y - 0.22), 0.44, 0.44, fc=BLUE if k == "eq" else "none", ec=INK, lw=1.4, ls="-" if k == "eq" else "--", zorder=3)
        )
    dim_v(ax, 0.6, ys["eq"], ys["up"], "$A$", color=RED, dx=0.07)
    dim_v(ax, 0.6, ys["down"], ys["eq"], "$A$", color=RED, dx=0.07)
    dim_v(ax, -0.75, ys["down"], ys["up"], "$2A$", color=GREEN, dx=-0.07, ha="right")
    ax.text(1.1, ys["eq"], "положение\nравновесия", ha="left", va="center", fontsize=9, color=INK)
    ax.set_title("Пружинный маятник")
    save(fig, "osc-amplitude-schemes.png")


def osc_pendulum_types():
    fig, axes = blank(11, 4.3, (-1.5, 1.5), (-2.8, 0.4), n=3)
    a1, a2, a3 = axes
    # math
    hatch_ceiling(a1, -0.4, 0.4, 0.0)
    th = np.radians(25)
    L = 1.9
    a1.plot([0, 0], [0, -L], color=INK, lw=1.5)
    a1.add_patch(Circle((0, -L), 0.08, color=BLUE, ec=INK, zorder=3))
    for s in (1, -1):
        px, py = L * np.sin(s * th), -L * np.cos(s * th)
        a1.plot([0, px], [0, py], color=GREY, lw=1, ls="--")
        a1.add_patch(Circle((px, py), 0.08, fc=PAPER, ec=GREY, ls="--", zorder=3))
    a1.text(0.08, -1.0, "нить", fontsize=9, color=INK)
    a1.text(0, -2.7, "математический\n(материальная точка на нити)", ha="center", va="top", fontsize=9.5)
    # spring
    hatch_ceiling(a2, -0.4, 0.4, 0.0)
    a2.plot(*spring_path((0, 0), (0, -1.6), n=8, w=0.12).T, color=INK, lw=1.5)
    a2.add_patch(Rectangle((-0.2, -1.6 - 0.4), 0.4, 0.4, fc=BLUE, ec=INK, lw=1.3, zorder=3))
    for y in (-1.2, -2.0):
        a2.add_patch(Rectangle((-0.2, y - 0.4), 0.4, 0.4, fc="none", ec=GREY, ls="--", lw=1))
    a2.text(0, -2.7, "пружинный\n(груз на пружине)", ha="center", va="top", fontsize=9.5)
    # physical: plate rotating about an axis through a hole
    a3.plot([-0.4, 0.4], [0, 0], color=INK, lw=2)
    a3.add_patch(Circle((0, -0.15), 0.05, color=INK, zorder=4))

    def plate(angle, **kw):
        c, s = np.cos(angle), np.sin(angle)
        pts = np.array([[-0.28, -0.1], [0.28, -0.1], [0.42, -1.45], [-0.42, -1.45]])
        pts = pts - np.array([0, -0.15]) * 0
        rot = np.array([[c, -s], [s, c]])
        pts = (pts - np.array([0, -0.15])) @ rot.T + np.array([0, -0.15])
        a3.add_patch(Polygon(pts, closed=True, **kw))

    plate(np.radians(-25), fc="none", ec=GREY, ls="--", lw=1)
    plate(np.radians(25), fc="none", ec=GREY, ls="--", lw=1)
    plate(0, fc=BLUE, ec=INK, lw=1.3, alpha=0.9)
    a3.add_patch(Circle((0, -0.15), 0.05, color=PAPER, ec=INK, zorder=5))
    a3.text(0, -2.7, "физический\n(тело на неподвижной оси)", ha="center", va="top", fontsize=9.5)
    save(fig, "osc-pendulum-types.png")


def osc_path_period():
    T, A = 1.0, 1.0
    t = np.linspace(0, T, 400)
    x = A * np.cos(2 * np.pi * t / T)
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    ax.plot(t, x, color=BLUE, lw=2.2)
    ax.axhline(0, color=INK, lw=1)
    for k in range(5):
        ax.axvline(k * T / 4, color=GREY, lw=0.8, ls=":")
    ys = [A, 0, -A, 0, A]
    for k in range(5):
        ax.plot(k * T / 4, ys[k], "o", color=RED, zorder=4)
    labels = ["от $A$ до $0$: путь $A$", "от $0$ до $-A$: путь $A$", "от $-A$ до $0$: путь $A$", "от $0$ до $A$: путь $A$"]
    for k, lab in enumerate(labels):
        ax.text((k + 0.5) * T / 4, -1.55, lab, ha="center", fontsize=8.6, color=INK)
    ax.text(T / 2, 1.5, "путь за период: $4A$", ha="center", fontsize=12, color=RED)
    ax.set_xticks([k * T / 4 for k in range(5)])
    ax.set_xticklabels(["0", "$T/4$", "$T/2$", "$3T/4$", "$T$"])
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["$-A$", "0", "$A$"])
    ax.set_ylim(-1.8, 1.9)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$x$")
    ax.grid(axis="y", color=GRID, lw=0.6)
    save(fig, "osc-path-period.png")


def osc_damped_undamped():
    T = 1.0
    t = np.linspace(0, 8, 1600)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.4, 5.4), sharex=True)
    a1.plot(t, np.cos(2 * np.pi * t / T), color=BLUE, lw=1.8)
    a1.axhline(0, color=INK, lw=0.8)
    a1.set_title("Незатухающие: амплитуда постоянна")
    tau = 3.0
    env = np.exp(-t / tau)
    a2.plot(t, env * np.cos(2 * np.pi * t / T), color=RED, lw=1.8)
    a2.plot(t, env, color=GREY, ls="--", lw=1.1)
    a2.plot(t, -env, color=GREY, ls="--", lw=1.1)
    a2.axhline(0, color=INK, lw=0.8)
    a2.set_title("Затухающие: амплитуда убывает")
    for ax in (a1, a2):
        ax.set_ylabel("$x$")
        ax.set_yticks([])
        ax.grid(axis="x", color=GRID, lw=0.6)
    a2.set_xlabel("$t$")
    fig.tight_layout()
    save(fig, "osc-damped-undamped.png")


def osc_friction_damping():
    w0 = 2 * np.pi
    t = np.linspace(0, 4, 1600)

    def under(g):
        w = np.sqrt(w0**2 - g**2)
        return np.exp(-g * t) * (np.cos(w * t) + g / w * np.sin(w * t))

    def over(g):
        d = np.sqrt(g**2 - w0**2)
        r1, r2 = -g + d, -g - d
        return (r2 * np.exp(r1 * t) - r1 * np.exp(r2 * t)) / (r2 - r1)

    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.plot(t, under(0.6), color=BLUE, lw=2, label="малое трение: много колебаний")
    ax.plot(t, under(3.0), color=GREEN, lw=2, label="большое трение: гаснет почти сразу")
    ax.plot(t, over(1.8 * w0), color=RED, lw=2, label="очень большое трение: ни одного колебания")
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$x$")
    ax.set_yticks([])
    ax.set_title("Чем больше трение, тем быстрее затухание (качественно)")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    ax.grid(axis="x", color=GRID, lw=0.6)
    save(fig, "osc-friction-damping.png")


def osc_forced():
    w0 = 2 * np.pi
    g = 0.12 * w0
    t = np.linspace(0, 14, 5000)

    def rhs(y, tt):
        return np.array([y[1], -2 * g * y[1] - w0**2 * y[0] + 12 * np.cos(w0 * tt)])

    y = np.zeros((len(t), 2))
    dt = t[1] - t[0]
    for i in range(len(t) - 1):
        k1 = rhs(y[i], t[i])
        k2 = rhs(y[i] + dt / 2 * k1, t[i] + dt / 2)
        k3 = rhs(y[i] + dt / 2 * k2, t[i] + dt / 2)
        k4 = rhs(y[i] + dt * k3, t[i] + dt)
        y[i + 1] = y[i] + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    x = y[:, 0]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.4, 5), sharex=True, gridspec_kw={"height_ratios": [1, 2.2]})
    a1.plot(t, np.cos(w0 * t), color=GOLD, lw=1.4)
    a1.set_ylabel("$F$")
    a1.set_title("Периодическая внешняя сила")
    a2.plot(t, x / np.max(np.abs(x)), color=BLUE, lw=1.6)
    a2.set_ylabel("$x$")
    a2.set_title("Колебания раскачиваются (качественно)")
    a2.set_xlabel("$t$")
    for ax in (a1, a2):
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_yticks([])
        ax.grid(axis="x", color=GRID, lw=0.6)
    fig.tight_layout()
    save(fig, "osc-forced.png")


def osc_pendulum_T_l():
    g = 9.8
    l = np.linspace(0, 4.4, 300)
    T = 2 * np.pi * np.sqrt(l / g)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(l, T, color=BLUE, lw=2.2)
    for lv in (0.25, 1.0, 4.0):
        Tv = 2 * np.pi * np.sqrt(lv / g)
        ax.plot([lv, lv], [0, Tv], color=GREY, ls=":", lw=1)
        ax.plot([0, lv], [Tv, Tv], color=GREY, ls=":", lw=1)
        ax.plot(lv, Tv, "o", color=RED, zorder=4)
        ax.text(lv + 0.07, Tv - 0.22, num(Tv, 1) + " с", fontsize=9.5, color=RED)
    ax.set_xlim(0, 4.6)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel("длина нити $l$, м")
    ax.set_ylabel("период $T$, с")
    ax.set_title("Нитяной маятник: длиннее нить, больше период")
    ax.text(2.4, 1.6, r"$T = 2\pi\sqrt{l/g}$" + "\n(справка, не из лекции)", fontsize=10, color=INK, va="top")
    ax.grid(color=GRID, lw=0.6)
    save(fig, "osc-pendulum-T-l.png")


def osc_pendulum_T_independence():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    m = np.linspace(0, 500, 50)
    a1.plot(m, np.full_like(m, 2.0), color=BLUE, lw=2.2)
    a1.set_ylim(0, 3)
    a1.set_xlabel("масса груза $m$, г")
    a1.set_ylabel("период $T$, с")
    a1.set_title("Нитяной маятник: $T$ не зависит от $m$")
    a1.grid(color=GRID, lw=0.6)
    A = np.linspace(0.5, 90, 300)
    T0 = 2.0
    T = T0 * (2 / np.pi) * ellipk(np.sin(np.radians(A) / 2) ** 2)
    a2.plot(A, T, color=BLUE, lw=2.2)
    a2.axvspan(0, 15, color=GREEN, alpha=0.15)
    a2.text(7.5, 1.1, "малые\nамплитуды", ha="center", fontsize=9.5, color=GREEN)
    a2.set_ylim(0, 3)
    a2.set_xlabel("амплитуда (угол) $\\alpha$, градусы")
    a2.set_ylabel("период $T$, с")
    a2.set_title("$T$ почти не зависит от $A$, пока $A$ мала")
    a2.grid(color=GRID, lw=0.6)
    a2.text(88, 0.3, "расчёт по точной формуле,\nне из лекции", ha="right", fontsize=8.5, color=INK)
    fig.tight_layout()
    save(fig, "osc-pendulum-T-independence.png")


def osc_springs_combination():
    fig, axes = blank(11.5, 4.6, (-0.4, 4.2), (-1.9, 1.7), n=3)
    titles = ["Одна пружина", "Параллельно", "Последовательно"]
    subs = [r"$k=\dfrac{F}{\Delta l}=k_0$", r"$k=\dfrac{2F}{\Delta l}=2k_0$", r"$k=\dfrac{F}{2\Delta l}=\dfrac{k_0}{2}$"]
    for ax, ti, su in zip(axes, titles, subs):
        ax.set_title(ti, fontsize=12)
        ax.text(2.0, -1.75, su, ha="center", fontsize=12, color=INK)
        hatch_wall(ax, 0, -0.9, 0.9, h=0.1, n=8)
    a1, a2, a3 = axes
    # one spring, length 2.6 -> stretched by dl
    a1.plot(*spring_path((0, 0), (2.4, 0), n=8, w=0.16).T, color=INK, lw=1.5)
    a1.plot([2.4, 2.4], [-0.5, 0.5], color=INK, lw=3)
    arrow(a1, (2.4, 0), (3.6, 0), color=RED, lw=2)
    a1.text(3.0, 0.15, "$F$", color=RED, fontsize=12)
    dim_h(a1, 1.6, 2.4, 0.75, r"$\Delta l$", color=GREEN, dy=0.05)
    # parallel
    for y in (0.35, -0.35):
        a2.plot(*spring_path((0, y), (2.4, y), n=8, w=0.12).T, color=INK, lw=1.4)
    a2.plot([2.4, 2.4], [-0.75, 0.75], color=INK, lw=3)
    # Same scale on all panels: F is 1.2 long, 2F is 2.4 long
    arrow(a2, (2.4, 0), (4.8, 0), color=RED, lw=2)
    a2.text(3.5, 0.15, "$2F$", color=RED, fontsize=12)
    dim_h(a2, 1.6, 2.4, 1.0, r"$\Delta l$", color=GREEN, dy=0.05)
    # series
    a3.plot(*spring_path((0, 0), (2.0, 0), n=6, w=0.16).T, color=INK, lw=1.5)
    a3.plot(*spring_path((2.0, 0), (4.0, 0), n=6, w=0.16).T, color=INK, lw=1.5)
    a3.plot([4.0, 4.0], [-0.5, 0.5], color=INK, lw=3)
    arrow(a3, (4.0, 0), (5.2, 0), color=RED, lw=2)
    a3.text(4.5, 0.15, "$F$", color=RED, fontsize=12)
    dim_h(a3, 1.0, 2.0, 0.55, r"$\Delta l$", color=GREEN, dy=0.05)
    dim_h(a3, 3.0, 4.0, 0.55, r"$\Delta l$", color=GREEN, dy=0.05)
    for ax in axes:
        ax.set_xlim(-0.4, 5.3)
    fig = a1.figure
    save(fig, "osc-springs-combination.png")


T_DATA = {  # period of a spring pendulum, s: {k/k0: (T at m0, T at 2 m0)}
    0.5: (0.68, 0.93),
    1.0: (0.46, 0.64),
    2.0: (0.34, 0.47),
}
T_REF = 0.46


def osc_spring_T_mass():
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    m = np.linspace(0, 2.6, 200)
    cols = {0.5: RED, 1.0: BLUE, 2.0: GREEN}
    labs = {0.5: r"$k_0/2$", 1.0: r"$k_0$", 2.0: r"$2k_0$"}
    for k, (t1, t2) in T_DATA.items():
        ax.plot(m * 100, T_REF * np.sqrt(m / k), color=cols[k], lw=1.4, alpha=0.7)
        ax.plot([100, 200], [t1, t2], "o", color=cols[k], ms=8, label=f"жёсткость {labs[k]}")
    ax.set_xlabel("масса груза $m$, г")
    ax.set_ylabel("период $T$, с")
    ax.set_xlim(0, 260)
    ax.set_ylim(0, 1.15)
    ax.set_title("Пружинный маятник: больше масса, больше период")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.text(258, 0.05, "точки — опыт, линии — $T \\propto \\sqrt{m}$", ha="right", fontsize=9)
    ax.grid(color=GRID, lw=0.6)
    save(fig, "osc-spring-T-mass.png")


def osc_spring_T_stiffness():
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    kk = np.linspace(0.3, 2.3, 200)
    for idx, (col, lab) in enumerate(((BLUE, "масса $m_0$"), (RED, "масса $2m_0$"))):
        mm = 1.0 if idx == 0 else 2.0
        ax.plot(kk, T_REF * np.sqrt(mm / kk), color=col, lw=1.4, alpha=0.7)
        ax.plot(list(T_DATA), [T_DATA[k][idx] for k in T_DATA], "o", color=col, ms=8, label=lab)
    ax.set_xticks([0.5, 1, 2])
    ax.set_xticklabels(["$k_0/2$", "$k_0$", "$2k_0$"])
    ax.set_xlabel("жёсткость пружины $k$")
    ax.set_ylabel("период $T$, с")
    ax.set_ylim(0, 1.15)
    ax.set_title("Пружинный маятник: жёстче пружина, меньше период")
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.text(2.28, 0.05, "точки — опыт, линии — $T \\propto 1/\\sqrt{k}$", ha="right", fontsize=9)
    ax.grid(color=GRID, lw=0.6)
    save(fig, "osc-spring-T-stiffness.png")


def osc_spring_T_vs_sqrt():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    xs, ys = [], []
    for k, (t1, t2) in T_DATA.items():
        for mm, tt in ((1.0, t1), (2.0, t2)):
            xs.append(np.sqrt(mm / k))
            ys.append(tt)
    xline = np.linspace(0, 2.2, 10)
    ax.plot(xline, T_REF * xline, color=GREY, lw=1.6, ls="--", label="прямая через начало")
    ax.plot(xs, ys, "o", color=BLUE, ms=9, label="шесть опытов")
    ax.set_xlabel(r"$\sqrt{\dfrac{m/m_0}{k/k_0}}$")
    ax.set_ylabel("период $T$, с")
    ax.set_title(r"$T$ пропорционален $\sqrt{m/k}$")
    ax.set_xlim(0, 2.2)
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(color=GRID, lw=0.6)
    save(fig, "osc-spring-T-vs-sqrt.png")


# ---------------------------------------------------------------------- waves


def wave_snapshot():
    lam, A = 2.0, 1.0
    x = np.linspace(0, 3.2 * lam, 800)
    y = A * np.sin(2 * np.pi * x / lam)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(x, y, color=BLUE, lw=2.2)
    ax.axhline(0, color=INK, lw=1)
    xc = lam / 4
    ax.plot([xc, xc + lam], [A + 0.18, A + 0.18], color=RED, lw=0)  # spacer
    dim_h(ax, xc, xc + lam, A + 0.25, r"$\lambda$", color=RED, dy=0.05, fs=13)
    for xx in (xc, xc + lam):
        ax.plot([xx, xx], [A, A + 0.25], color=RED, lw=0.9, ls=":")
    dim_v(ax, 3 * lam / 4 + 2 * lam - 0.55, 0, -A, "$A$", color=GREEN, dx=0.06)
    ax.text(xc, A + 0.75, "гребень", ha="center", color=INK, fontsize=9.5)
    ax.text(3 * lam / 4, -A - 0.35, "впадина", ha="center", color=INK, fontsize=9.5)
    arrow(ax, (5.2, 1.25), (6.2, 1.25), color=INK, lw=2)
    ax.text(5.7, 1.4, "скорость волны $c$", ha="center", fontsize=10)
    ax.set_ylim(-1.7, 2.1)
    ax.set_xlabel("расстояние вдоль луча $x$")
    ax.set_ylabel("смещение частиц")
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("Мгновенный снимок волны")
    save(fig, "wave-snapshot.png")


def wave_space_time():
    lam, T, A = 2.0, 1.0, 1.0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9))
    x = np.linspace(0, 2.5 * lam, 600)
    a1.plot(x, A * np.cos(2 * np.pi * x / lam), color=BLUE, lw=2.2)
    a1.axhline(0, color=INK, lw=0.8)
    dim_h(a1, 0, lam, A + 0.3, r"$\lambda$", color=RED, dy=0.05, fs=13)
    for xx in (0, lam):
        a1.plot([xx, xx], [A, A + 0.3], color=RED, lw=0.9, ls=":")
    a1.set_ylim(-1.5, 1.9)
    a1.set_yticks([])
    a1.set_xticks([])
    a1.set_xlabel("$x$")
    a1.set_title("Снимок: все точки в один момент")
    t = np.linspace(0, 2.5 * T, 600)
    a2.plot(t, A * np.cos(2 * np.pi * t / T), color=GREEN, lw=2.2)
    a2.axhline(0, color=INK, lw=0.8)
    dim_h(a2, 0, T, A + 0.3, "$T$", color=RED, dy=0.05, fs=13)
    for xx in (0, T):
        a2.plot([xx, xx], [A, A + 0.3], color=RED, lw=0.9, ls=":")
    a2.set_ylim(-1.5, 1.9)
    a2.set_yticks([])
    a2.set_xticks([])
    a2.set_xlabel("$t$")
    a2.set_title("Одна точка (поплавок) во времени")
    fig.tight_layout()
    save(fig, "wave-space-time.png")


def wave_shift_period():
    lam, A = 2.0, 0.42
    x = np.linspace(0, 3 * lam, 600)
    rows = [(0.0, "$t=0$"), (0.25, "$t=T/4$"), (0.5, "$t=T/2$"), (0.75, "$t=3T/4$"), (1.0, "$t=T$")]
    fig, ax = plt.subplots(figsize=(9, 6.6))
    xf = 1.5 * lam + 0.0  # fixed float position
    ax.axis("off")
    for i, (frac, lab) in enumerate(rows):
        y0 = -i * 1.15
        # wave moving right: crest at x = 0.25 lam + lam * frac + n lam
        y = A * np.cos(2 * np.pi * (x - lam * frac) / lam - np.pi / 2 * 0)
        ax.plot(x, y0 + y, color=BLUE, lw=1.8)
        ax.plot([0, 3 * lam], [y0, y0], color=LIGHT, lw=0.8)
        ax.text(-0.25, y0, lab, ha="right", va="center", fontsize=10)
        cx = lam * frac
        ax.plot(cx, y0 + A, "o", color=RED, zorder=4)
        ax.plot(cx + lam, y0 + A, "o", color=RED, zorder=4)
        yf = A * np.cos(2 * np.pi * (xf - lam * frac) / lam)
        ax.plot(xf, y0 + yf, "s", color=GREEN, ms=8, zorder=5)
    ax.plot([xf, xf], [A + 0.2, -4 * 1.15 - A - 0.2], color=GREEN, lw=0.9, ls=":")
    yb = -4 * 1.15 - A - 0.55
    dim_h(ax, 0, lam, yb, r"гребень за время $T$ смещается на $\lambda$", color=RED, dy=-0.5, fs=10)
    ax.text(xf + 0.1, A + 0.3, "поплавок", color=GREEN, fontsize=9.5)
    arrow(ax, (4.2, 0.9), (5.4, 0.9), color=INK, lw=2)
    ax.text(4.8, 1.05, "$c$", ha="center", fontsize=12)
    ax.set_xlim(-1.6, 6.3)
    ax.set_ylim(yb - 0.9, 1.6)
    save(fig, "wave-shift-period.png")


def wave_transverse_longitudinal():
    lam = 2.0
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.4, 6.6))
    x0 = np.arange(0, 3 * lam + 1e-9, 0.2)
    # transverse
    ax = a1
    ax.set_xlim(-0.5, 7.4)
    ax.set_ylim(-1.7, 1.9)
    ax.axis("off")
    ax.plot(x0, 0.55 * np.sin(2 * np.pi * x0 / lam), color=BLUE, lw=1.6)
    ax.plot(x0, 0.55 * np.sin(2 * np.pi * x0 / lam), "o", color=BLUE, ms=5)
    ax.plot([0, 3 * lam], [0, 0], color=GREY, lw=0.8, ls="--")
    # The particle sits on the axis (x = 1.5 lambda); its swing is the amplitude 0.55 up and down
    xp = 1.5 * lam
    arrow(ax, (xp, -0.55), (xp, 0.55), color=RED, style="<|-|>", lw=1.6)
    ax.text(xp + 0.12, 0.62, "колебания\nчастицы", color=RED, fontsize=9.5, va="bottom")
    arrow(ax, (0.2, -1.35), (2.2, -1.35), color=INK, lw=2)
    ax.text(2.35, -1.35, "распространение волны", fontsize=9.5, va="center")
    ax.set_title("Поперечная волна: колебания перпендикулярны распространению")
    # longitudinal
    ax = a2
    ax.set_xlim(-0.5, 8.4)
    ax.set_ylim(-1.7, 1.9)
    ax.axis("off")
    s = 0.32
    for row, yy in enumerate((0.55, 0.2, -0.15, -0.5)):
        xs = x0 + s * np.sin(2 * np.pi * x0 / lam) * -1
        ax.plot(xs, np.full_like(xs, yy), "o", color=BLUE, ms=5)
    # region labels
    for cx, lab in ((lam * 0.5 + 0.0, "сжатие"), (lam * 1.0 + 0.0, "разрежение"), (lam * 1.5, "сжатие"), (lam * 2.0, "разрежение")):
        pass
    comp = [x for x in np.arange(0, 3 * lam + 1e-9, lam) if x >= 0]
    for c in comp:
        ax.text(c + 0.0 * lam, 1.0, "сжатие", ha="center", fontsize=9.5, color=RED)
        if c + lam / 2 < 3 * lam:  # no particles to the right of x = 3 lambda
            ax.text(c + lam / 2, 1.0, "разрежение", ha="center", fontsize=9.5, color=INK)
    xp = 3.6
    # The arrow spans the swing of the particles, 2 * s
    arrow(ax, (xp - s, -0.9), (xp + s, -0.9), color=RED, style="<|-|>", lw=1.6)
    ax.text(xp, -1.1, "колебания частицы", ha="center", color=RED, fontsize=9.5, va="top")
    arrow(ax, (0.2, -1.5), (2.2, -1.5), color=INK, lw=2)
    ax.text(2.35, -1.5, "распространение волны", fontsize=9.5, va="center")
    ax.set_title("Продольная волна: колебания вдоль распространения")
    fig.tight_layout()
    save(fig, "wave-transverse-longitudinal.png")


def wave_float_lambda():
    lam = 1.2
    x = np.linspace(0, 4.2 * lam, 600)
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.fill_between(x, 0.15 * np.cos(2 * np.pi * x / lam), -0.6, color=tint(SKY, 0.7), alpha=0.8)
    ax.plot(x, 0.15 * np.cos(2 * np.pi * x / lam), color=BLUE, lw=2)
    xf = 2.5 * lam
    yf = 0.15 * np.cos(2 * np.pi * xf / lam)
    ax.plot([xf, xf], [yf + 0.35, yf], color=INK, lw=1.4)
    ax.add_patch(Rectangle((xf - 0.05, yf - 0.03), 0.1, 0.16, fc=RED, ec=INK, zorder=4))
    arrow(ax, (xf + 0.02, yf + 0.5), (xf + 0.02, yf + 0.25), color=RED, style="<|-|>", lw=1.3)
    dim_h(ax, lam, 2 * lam, 0.15 + 0.22, r"$\lambda=1{,}2$ м", color=GREEN, dy=0.04)
    for xx in (lam, 2 * lam):
        ax.plot([xx, xx], [0.15, 0.37], color=GREEN, lw=0.9, ls=":")
    arrow(ax, (4.2 * lam - 0.1, 0.55), (4.2 * lam - 1.0, 0.55), color=INK, lw=2)
    ax.text(4.2 * lam - 0.55, 0.6, "$c$", ha="center", fontsize=12)
    ax.text(xf + 0.1, yf + 0.5, "поплавок", fontsize=9.5)
    ax.set_ylim(-0.6, 0.95)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "wave-float-lambda.png")


# --------------------------------------------------------------------- sound


def sound_wavelength_frequency():
    c = 340.0
    nu = np.logspace(1, np.log10(30000), 400)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.loglog(nu, c / nu, color=BLUE, lw=2.2)
    ax.axvspan(20, 20000, color=GREEN, alpha=0.12)
    for f, lab, dy in ((20, "17 м", 1.4), (20000, "17 мм", 1.4), (440, "0,77 м", 1.4)):
        ax.plot(f, c / f, "o", color=RED, zorder=4)
        off = (-46, 8) if f == 20000 else (8, 8)
        ax.annotate(lab, (f, c / f), textcoords="offset points", xytext=off, fontsize=10, color=RED)
    ax.set_xlim(10, 30000)
    ax.set_ylim(0.008, 40)
    ax.set_xlabel(r"частота $\nu$, Гц")
    ax.set_ylabel(r"длина волны $\lambda$, м")
    ax.set_title("Звук в воздухе: чем выше частота, тем короче волна")
    ax.text(1500, 20, "слышимый диапазон", color=GREEN, ha="center", fontsize=10)
    ax.text(3000, 0.012, r"$c = 340$ м/с", fontsize=10)
    ax.grid(which="both", color=GRID, lw=0.5)
    save(fig, "sound-wavelength-frequency.png")


def sound_frequency_ranges():
    fig, ax = plt.subplots(figsize=(9.4, 3.7))
    ax.set_xscale("log")
    ax.set_xlim(1, 1e5)
    ax.set_ylim(0, 4.1)
    ax.barh(0.6, 20 - 1, left=1, height=0.8, color=BLUE, alpha=0.55)
    ax.barh(0.6, 20000 - 20, left=20, height=0.8, color=GREEN, alpha=0.55)
    ax.barh(0.6, 1e5 - 20000, left=20000, height=0.8, color=RED, alpha=0.45)
    ax.text(4.5, 0.6, "инфразвук\n$\\nu<20$ Гц", ha="center", va="center", fontsize=9.5)
    ax.text(630, 0.6, "звук, который слышит человек\n20 Гц ... 20 кГц", ha="center", va="center", fontsize=10)
    ax.text(45000, 0.6, "ультра-\nзвук", ha="center", va="center", fontsize=9)
    marks = [
        (256, "камертон\n256 Гц", 1.55, "right"),
        (440, "камертон\n440 Гц", 2.35, "center"),
        (1000, "сигнал точного\nвремени 1000 Гц", 3.15, "center"),
        (18000, "18 кГц: Виктор\nуже не слышит", 1.55, "right"),
        (21500, "дети слышат\n21–22 кГц", 2.35, "left"),
    ]
    for f, lab, y, ha in marks:
        ax.plot([f, f], [1.0, y - 0.05], color=INK, lw=0.9)
        ax.plot(f, 1.0, "v", color=INK, ms=5)
        ax.text(f, y, lab, ha=ha, va="bottom", fontsize=8.6)
    ax.set_yticks([])
    ax.set_xlabel(r"частота $\nu$, Гц")
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", which="both", color=GRID, lw=0.5)
    save(fig, "sound-frequency-ranges.png")


def sound_speed_media():
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    names = ["воздух (комнатная температура)", "вода", "сталь"]
    vals = [340, 1500, 5000]
    cols = [BLUE, GREEN, STONE]
    ax.barh(names[::-1], vals[::-1], color=cols[::-1])
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 80, i, f"{v} м/с", va="center", fontsize=10.5)
    ax.set_xlim(0, 6000)
    ax.set_xlabel("скорость звука $c$, м/с")
    ax.set_title("Скорость звука зависит от среды")
    ax.grid(axis="x", color=GRID, lw=0.6)
    save(fig, "sound-speed-media.png")


def sound_pitch():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.6, 4.8), sharex=True)
    t = np.linspace(0, 0.02, 2000)
    for ax, nu, col in ((a1, 256, BLUE), (a2, 440, RED)):
        ax.plot(t * 1000, np.sin(2 * np.pi * nu * t), color=col, lw=1.8)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_yticks([])
        ax.set_ylabel(f"{nu} Гц", rotation=0, labelpad=30, va="center")
        ax.set_ylim(-1.3, 1.3)
    a1.set_title("Одинаковая амплитуда: выше частота, выше звук")
    a2.set_xlabel("$t$, мс")
    fig.tight_layout()
    save(fig, "sound-pitch.png")


def sound_loudness():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.6, 4.8), sharex=True)
    t = np.linspace(0, 0.012, 2000)
    for ax, amp, col, lab in ((a1, 1.0, BLUE, "громкий\nзвук"), (a2, 0.35, RED, "тихий\nзвук")):
        ax.plot(t * 1000, amp * np.sin(2 * np.pi * 440 * t), color=col, lw=1.8)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_ylim(-1.3, 1.3)
        ax.set_yticks([])
        ax.set_ylabel(lab, rotation=0, labelpad=32, va="center")
        ax.axhline(amp, color=GREY, lw=0.8, ls="--")
        ax.text(11.9, amp + 0.08, "$A$", ha="right", fontsize=10, color=INK)
    a1.set_title("Одна частота (440 Гц): больше амплитуда, громче звук")
    a2.set_xlabel("$t$, мс")
    fig.tight_layout()
    save(fig, "sound-loudness.png")


def sound_ear_sensitivity():
    # Terhardt approximation of the threshold of hearing in quiet, f in kHz, level in dB.
    # It is valid inside the audible range, so the curve is drawn only from 20 Hz to 20 kHz.
    f = np.logspace(np.log10(20), np.log10(20000), 500)
    fk = f / 1000
    thr = 3.64 * fk**-0.8 - 6.5 * np.exp(-0.6 * (fk - 3.3) ** 2) + 1e-3 * fk**4
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axvspan(10, 20, color=LIGHT)
    ax.axvspan(20000, 40000, color=LIGHT)
    ax.semilogx(f, thr, color=BLUE, lw=2.2)
    ax.axvspan(3000, 4000, color=GOLD, alpha=0.3)
    ax.text(3460, -13, "≈ 3–4 кГц", ha="center", va="center", fontsize=10)
    ax.axvline(20, color=GREY, ls="--", lw=1)
    ax.axvline(20000, color=GREY, ls="--", lw=1)
    ax.text(14, 50, "инфразвук", ha="center", va="center", fontsize=9, color=INK, rotation=90)
    ax.text(28000, 50, "ультразвук", ha="center", va="center", fontsize=9, color=INK, rotation=90)
    ax.set_xlim(10, 40000)
    # The axis is inverted: the lower the threshold, the better the ear hears
    ax.set_ylim(100, -20)
    ax.set_xlabel(r"частота $\nu$, Гц")
    ax.set_ylabel("порог слышимости, дБ\n(выше на рисунке — слышно лучше)")
    ax.set_title("Ухо лучше всего слышит около 3–4 кГц (порог слышимости)")
    ax.grid(which="both", axis="x", color=GRID, lw=0.5)
    ax.grid(axis="y", color=GRID, lw=0.5)
    save(fig, "sound-ear-sensitivity.png")


HARMONICS = {
    "камертон: только основной тон": (1.0, 0.0, 0.0, 0.0),
    "440 + 880 + 1320 + 1760 Гц": (1.0, 0.5, 0.33, 0.25),
    "тот же основной тон, другие обертоны": (1.0, 0.15, 0.6, 0.1),
}


def _wave(t, amps, base=440.0):
    return sum(a * np.sin(2 * np.pi * base * (i + 1) * t) for i, a in enumerate(amps))


def sound_timbre_waveforms():
    t = np.linspace(0, 3 / 440, 1500)
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 6.6), sharex=True)
    cols = (BLUE, RED, GREEN)
    for ax, (lab, amps), col in zip(axes, HARMONICS.items(), cols):
        ax.plot(t * 1000, _wave(t, amps), color=col, lw=1.8)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_ylim(-2.2, 2.2)
        ax.set_yticks([])
        ax.set_title(lab, fontsize=10.5, loc="left")
        for k in range(4):
            ax.axvline(k * 1000 / 440, color=GRID, lw=0.8, ls=":")
    axes[-1].set_xlabel("$t$, мс (три периода основного тона, $T\\approx 2{,}27$ мс)")
    fig.suptitle("Одна высота, разная форма колебаний, разный тембр", y=1.0)
    fig.tight_layout()
    save(fig, "sound-timbre-waveforms.png")


def sound_timbre_spectrum():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    freqs = [440, 880, 1320, 1760]
    for ax, (lab, amps), col in zip(axes, HARMONICS.items(), (BLUE, RED, GREEN)):
        ax.bar(range(4), amps, color=col, width=0.55)
        ax.set_xticks(range(4))
        ax.set_xticklabels([f"{f}" for f in freqs], fontsize=9)
        ax.set_title(lab, fontsize=9.5)
        ax.set_xlabel("частота, Гц")
        ax.set_ylim(0, 1.2)
    axes[0].set_ylabel("амплитуда")
    axes[1].annotate("основной тон", (0, 1.0), (0.4, 1.12), fontsize=8.5, arrowprops=dict(arrowstyle="-", color=GREY))
    axes[1].annotate("обертоны", (2, 0.33), (1.7, 0.75), fontsize=8.5, arrowprops=dict(arrowstyle="-", color=GREY))
    fig.text(0.5, -0.04, "амплитуды обертонов выбраны для иллюстрации", ha="center", fontsize=8.5)
    fig.tight_layout()
    save(fig, "sound-timbre-spectrum.png")


def sound_envelope():
    t = np.linspace(0, 2.0, 40000)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.8, 5), sharex=True)
    car = np.sin(2 * np.pi * 220 * t)
    g = np.where(t < 0.03, t / 0.03, np.exp(-(t - 0.03) / 0.6))
    f = np.clip(t / 0.5, 0, 1) ** 2 * np.exp(-np.clip(t - 1.4, 0, None) / 0.2)
    for ax, env, col, ti in ((a1, g, BLUE, "гитара: резкая атака, затем затухание"), (a2, f, GREEN, "флейта: сначала шипение, звук разгорается медленно")):
        ax.plot(t, env * car, color=col, lw=0.35)
        ax.plot(t, env, color=INK, lw=1.4)
        ax.plot(t, -env, color=INK, lw=1.4)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_yticks([])
        ax.set_title(ti, loc="left", fontsize=10.5)
        ax.set_ylim(-1.2, 1.2)
    a2.set_xlabel("$t$ (качественно; частота колебаний занижена для наглядности)")
    fig.tight_layout()
    save(fig, "sound-envelope.png")


def sound_beats():
    t = np.linspace(0, 0.6, 30000)
    f1, f2 = 440.0, 444.0
    s = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
    env = 2 * np.abs(np.cos(np.pi * (f2 - f1) * t))
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(t, s, color=BLUE, lw=0.35)
    ax.plot(t, env, color=RED, lw=1.5)
    ax.plot(t, -env, color=RED, lw=1.5)
    ax.set_yticks([])
    ax.set_ylim(-2.6, 2.6)
    ax.set_xlabel("$t$, с")
    ax.set_title("440 Гц + 444 Гц: громкость то растёт, то падает")
    ax.annotate("", xy=(0.5, 2.3), xytext=(0.25, 2.3), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.2))
    ax.text(0.375, 2.35, "$1/(\\nu_2-\\nu_1)=0{,}25$ с", ha="center", fontsize=9.5, color=RED)
    save(fig, "sound-beats.png")


def _person(ax, x, y, s=0.5, color=INK):
    ax.add_patch(Circle((x, y + 1.55 * s), 0.22 * s, fc=PAPER, ec=color, lw=1.4))
    ax.plot([x, x], [y + 1.33 * s, y + 0.7 * s], color=color, lw=1.6)
    ax.plot([x - 0.3 * s, x + 0.3 * s], [y + 1.15 * s, y + 1.15 * s], color=color, lw=1.6)
    ax.plot([x, x - 0.25 * s], [y + 0.7 * s, y], color=color, lw=1.6)
    ax.plot([x, x + 0.25 * s], [y + 0.7 * s, y], color=color, lw=1.6)


def sound_echo():
    fig, ax = plt.subplots(figsize=(8.6, 3.1))
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-1.5, 2.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-0.5, 9.5], [0, 0], color=INK, lw=1)
    _person(ax, 0.5, 0, s=1.0)
    ax.add_patch(Rectangle((8.4, 0), 0.6, 2.2, fc=STONE, ec=INK, lw=1.4))
    ax.text(8.7, 2.35, "стена замка", ha="center", fontsize=9.5)
    arrow(ax, (1.0, 1.9), (8.3, 1.9), color=BLUE, lw=2)
    ax.text(4.6, 2.0, "звук идёт к стене", ha="center", color=BLUE, fontsize=9.5)
    arrow(ax, (8.3, 1.1), (1.1, 1.1), color=RED, lw=2)
    ax.text(4.6, 0.72, "отражённый звук (эхо)", ha="center", color=RED, fontsize=9.5)
    dim_h(ax, 0.5, 8.7, -0.55, "$l$", color=GREEN, dy=-0.5, fs=12)
    ax.text(4.6, -1.35, "путь звука за время $t$: $s=2l$", ha="center", fontsize=10.5)
    save(fig, "sound-echo.png")


def sound_thunder():
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1.6, 3.8)
    ax.set_aspect("equal")
    ax.axis("off")
    for cx in (1.7, 8.6):
        for dx, dy, r in ((0, 0, 0.7), (0.7, 0.1, 0.6), (-0.7, -0.05, 0.55)):
            ax.add_patch(Circle((cx + dx, 3.1 + dy), r, fc=LIGHT, ec=GREY))
    zig = [(2.4, 3.0), (3.2, 2.5), (3.6, 2.9), (4.6, 2.4), (5.3, 2.8), (6.4, 2.35), (7.2, 2.7), (8.0, 3.0)]
    ax.plot(*zip(*zig), color=GOLD, lw=3)
    _person(ax, 1.5, -1.3, s=0.8)
    ear = (1.5, -0.2)
    for tx, ty, col in ((zig[0][0], zig[0][1], BLUE), (zig[-1][0], zig[-1][1], RED)):
        arrow(ax, (tx, ty - 0.1), ear, color=col, lw=1.3, linestyle="--")
    ax.text(3.6, 0.0, "ближний конец: звук приходит раньше", color=BLUE, fontsize=9.3)
    ax.text(3.6, -0.5, "дальний конец: звук приходит позже", color=RED, fontsize=9.3)
    ax.text(3.6, -1.1, "звуки от разных участков молнии\nсливаются в один долгий раскат", fontsize=9.3, va="top")
    save(fig, "sound-thunder.png")


if __name__ == "__main__":
    osc_xt_sinusoid()
    osc_amplitude_schemes()
    osc_pendulum_types()
    osc_path_period()
    osc_damped_undamped()
    osc_friction_damping()
    osc_forced()
    osc_pendulum_T_l()
    osc_pendulum_T_independence()
    osc_springs_combination()
    osc_spring_T_mass()
    osc_spring_T_stiffness()
    osc_spring_T_vs_sqrt()
    wave_snapshot()
    wave_space_time()
    wave_shift_period()
    wave_transverse_longitudinal()
    wave_float_lambda()
    sound_wavelength_frequency()
    sound_frequency_ranges()
    sound_speed_media()
    sound_pitch()
    sound_loudness()
    sound_ear_sensitivity()
    sound_timbre_waveforms()
    sound_timbre_spectrum()
    sound_envelope()
    sound_beats()
    sound_echo()
    sound_thunder()
