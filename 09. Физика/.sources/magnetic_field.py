"""Figures for the notes "Магнитное поле тока" and "Постоянные магниты. Магнитное поле Земли" (section f12, lessons 170-172, 175).

Run: python3 magnetic_field.py [name ...]
PNG files go to content/12. Магнитные явления/00. Вложения/ (prefixes magnet-, earth-)
Fields are computed numerically: a loop by summing Biot-Savart segments, a solenoid and a bar magnet as a stack of loops, the Earth as an ideal dipole.
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "12. Магнитные явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import BLUE, COPPER, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, saver, tint

plt.rcParams["font.size"] = 12  # у этих рисунков подписи крупнее

# Course convention (lecture U170): the north pole and the north end of a needle are blue, the south ones are red.
# Field lines are green so that they do not merge with the blue pole.
FIELD = GREEN
CUR = RED
NORTH = BLUE
SOUTH = RED
GRAY = tint(INK, 0.4)  # small notes and secondary text


_save = saver(OUT)


def save(fig, name):
    _save(fig, name, facecolor=PAPER)


def arrow(ax, p, q, color=FIELD, lw=1.6, ms=13, z=5, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, zorder=z,
            shrinkA=0, shrinkB=0,
        )
    )


def cross(ax, x, y, r=0.13, color=CUR):
    """Current into the page."""
    ax.add_patch(Circle((x, y), r, fill=False, ec=color, lw=1.6, zorder=6))
    d = r * 0.7
    ax.plot([x - d, x + d], [y - d, y + d], color=color, lw=1.6, zorder=6)
    ax.plot([x - d, x + d], [y + d, y - d], color=color, lw=1.6, zorder=6)


def dot(ax, x, y, r=0.13, color=CUR):
    """Current out of the page."""
    ax.add_patch(Circle((x, y), r, fill=False, ec=color, lw=1.6, zorder=6))
    ax.add_patch(Circle((x, y), r * 0.3, color=color, zorder=6))


def loop_field(X, Z, R, z0=0.0, n=240):
    """Field (Bx, Bz) in the plane y=0 of a loop of radius R, axis z, current counterclockwise seen from +z."""
    phi = (np.arange(n) + 0.5) * 2 * np.pi / n
    dphi = 2 * np.pi / n
    Bx = np.zeros_like(X)
    Bz = np.zeros_like(X)
    for p in phi:
        # element position and direction
        px, py = R * np.cos(p), R * np.sin(p)
        dlx, dly = -R * np.sin(p) * dphi, R * np.cos(p) * dphi
        rx, ry, rz = X - px, -py, Z - z0
        r3 = (rx**2 + ry**2 + rz**2) ** 1.5 + 1e-9
        # dl x r, dl = (dlx, dly, 0)
        Bx += (dly * rz) / r3
        Bz += (dlx * ry - dly * rx) / r3
    return Bx, Bz


def stack_field(X, Z, R, zs, n=240):
    Bx = np.zeros_like(X)
    Bz = np.zeros_like(X)
    for z0 in zs:
        bx, bz = loop_field(X, Z, R, z0, n=n)
        Bx += bx
        Bz += bz
    return Bx, Bz


# ---------------------------------------------------------------- straight wire

def wire_field_lines():
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    for r in (0.6, 1.1, 1.6, 2.1):
        ax.add_patch(Circle((0, 0), r, fill=False, ec=FIELD, lw=1.6, ls="-"))
        # clockwise when current goes into the page: arrows at 4 places
        for a in np.radians([45, 135, 225, 315]):
            x, y = r * np.cos(a), r * np.sin(a)
            tx, ty = np.sin(a), -np.cos(a)  # clockwise tangent
            arrow(ax, (x - 0.02 * tx, y - 0.02 * ty), (x + 0.02 * tx, y + 0.02 * ty), ms=14)
    cross(ax, 0, 0, r=0.2)
    ax.text(0.28, -0.42, "$I$", color=CUR, fontsize=14)
    ax.text(0, -2.55, "Ток направлен от нас (за плоскость рисунка)", ha="center", color=GRAY, fontsize=11)
    ax.text(0, 2.5, "Вид сверху: линии поля — окружности", ha="center", fontsize=12)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "magnet-wire-field-lines.png")


def wire_vectors():
    """Vectors of the field around a wire: the arrow length falls with the distance (length ~ 1/r)."""
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    for r in (0.75, 1.3, 2.1, 3.0):
        # the inner ring has 8 arrows 0.57 apart: keep them shorter than that so that they do not touch
        L = 0.28 / r + 0.14
        for a in np.radians(np.arange(0, 360, 45) + (r > 1) * 22.5):
            x, y = r * np.cos(a), r * np.sin(a)
            tx, ty = np.sin(a), -np.cos(a)  # clockwise tangent
            arrow(ax, (x - tx * L / 2, y - ty * L / 2), (x + tx * L / 2, y + ty * L / 2), lw=1.8, ms=12)
    cross(ax, 0, 0, r=0.2)
    ax.text(0, -3.75, "Чем дальше от провода, тем короче стрелки поля", ha="center", color=GRAY, fontsize=11)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-4.0, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "magnet-wire-vectors.png")


def needle(ax, c, d, L=0.34, w=0.11, z=4):
    """Magnetic needle centred at c, its north (blue) end along the unit vector d."""
    c = np.asarray(c, float)
    d = np.asarray(d, float) / np.hypot(*d)
    n = np.array([-d[1], d[0]])
    ax.add_patch(plt.Polygon([c + d * L, c + n * w, c - n * w], closed=True, fc=NORTH, ec=INK, lw=0.8, zorder=z))
    ax.add_patch(plt.Polygon([c - d * L, c + n * w, c - n * w], closed=True, fc=tint(INK, 0.85), ec=INK, lw=0.8, zorder=z))


def oersted():
    """Oersted's experiment, top view: a wire and a needle beneath it, the needle turns when the current flows."""
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8))
    titles = ("Тока нет", "Ток слева направо", "Ток справа налево")
    # needle in the wire plane, then turned by the current; the north end turns to the top of the drawing for a rightward current
    dirs = ((-1, 0), (0.25, 1), (-0.25, -1))
    for ax, t, d, cur in zip(axes, titles, dirs, (0, 1, -1)):
        ax.add_patch(Rectangle((-2.2, -0.09), 4.4, 0.18, fc=COPPER, ec=INK, lw=0.8, zorder=1))
        ax.text(-2.15, 0.28, "провод", fontsize=10, color=GRAY)
        needle(ax, (0, 0), d, L=0.8, w=0.15, z=3)
        if cur:
            arrow(ax, (-1.9 * cur, 1.15), (1.9 * cur, 1.15), color=CUR, lw=2.4, ms=18)
            ax.text(0, 1.3, "$I$", color=CUR, fontsize=14, ha="center")
        ax.text(0, -1.3, t, ha="center", fontsize=12)
        ax.set_xlim(-2.4, 2.4)
        ax.set_ylim(-1.5, 1.7)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.04, "Вид сверху, стрелка под проводом; синий конец — северный (N). Над проводом стрелка повернулась бы в обратную сторону", ha="center", color=GRAY, fontsize=10.5)
    save(fig, "magnet-oersted-experiment.png")


def task_vertical_wire():
    """Task 13.2: vertical wire, current down, a needle to the right of it; the field on that side points to us."""
    fig, ax = plt.subplots(figsize=(4.4, 4.6))
    ax.plot([0, 0], [-2.0, 2.0], color=INK, lw=5, solid_capstyle="round", zorder=1)
    arrow(ax, (0, 1.9), (0, 0.6), color=CUR, lw=2.6, ms=20, z=6)
    ax.text(-0.35, 1.2, "$I$", color=CUR, fontsize=15)
    t = np.linspace(0, 2 * np.pi, 200)
    # clockwise from above: the front half goes to the left, the right side comes toward us
    for lo, hi, z in ((0, np.pi, 0), (np.pi, 2 * np.pi, 2)):
        tt = np.linspace(lo, hi, 100)
        ax.plot(1.5 * np.cos(tt), -0.6 + 0.45 * np.sin(tt), color=FIELD, lw=1.8, zorder=z)
    # the arrowhead sits away from the wire, at the left of it
    t0 = 1.5 * np.pi - 0.6
    arrow(ax, (1.5 * np.cos(t0 + 0.05), -0.6 + 0.45 * np.sin(t0 + 0.05)), (1.5 * np.cos(t0 - 0.05), -0.6 + 0.45 * np.sin(t0 - 0.05)), ms=16, z=6)
    # needle on the right, seen from the front: its north end (blue) turns toward the viewer
    needle(ax, (1.9, -0.6), (-0.55, -0.85), L=0.55, w=0.14, z=7)
    ax.text(1.9, 0.1, "$B$ к нам", color=FIELD, fontsize=12, ha="center")
    ax.set_xlim(-2.2, 3.0)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "magnet-task-vertical-wire.png")


def cross_dot_legend():
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 2.6))
    for ax, f, t, sub in zip(axes, (cross, dot), ("От нас", "К нам"), ("видно оперение стрелы", "видно остриё стрелы")):
        f(ax, 0, 0, r=0.5)
        ax.text(0, -1.0, t, ha="center", fontsize=13)
        ax.text(0, -1.5, sub, ha="center", fontsize=10, color=GRAY)
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.8, 0.9)
        ax.set_aspect("equal")
        ax.axis("off")
    save(fig, "magnet-cross-dot.png")


def wire_compass():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.9))
    for ax, sign, title in zip(axes, (+1, -1), ("Ток от нас", "Ток к нам")):
        ax.add_patch(Circle((0, 0), 1.7, fill=False, ec=MUTED, lw=1, ls="--"))
        for a in np.radians(np.arange(0, 360, 45)):
            cx, cy = 1.7 * np.cos(a), 1.7 * np.sin(a)
            # direction of B: clockwise for current into page (sign=+1)
            needle(ax, (cx, cy), (sign * np.sin(a), -sign * np.cos(a)))
        (cross if sign > 0 else dot)(ax, 0, 0, r=0.22)
        ax.set_title(title)
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.02, "Синий конец стрелки — северный полюс; стрелки ложатся по касательной к окружности", ha="center", color=GRAY, fontsize=11)
    save(fig, "magnet-wire-compass.png")


def wire_gimlet():
    """Right-hand gimlet rule: current along the wire, field circles around it."""
    fig, ax = plt.subplots(figsize=(4.6, 5.6))
    ax.plot([0, 0], [-2.2, 2.4], color=INK, lw=4, solid_capstyle="round", zorder=1)
    arrow(ax, (0, 0.9), (0, 2.5), color=CUR, lw=2.6, ms=20)
    ax.text(0.15, 2.05, "$I$", color=CUR, fontsize=15)
    for y0 in (-1.0, 0.2):
        # ellipse seen from a slant; counterclockwise seen from above (current up); the far half passes behind the wire
        for lo, hi, z in ((0, np.pi, 0), (np.pi, 2 * np.pi, 2)):
            t = np.linspace(lo, hi, 100)
            ax.plot(1.5 * np.cos(t), y0 + 0.45 * np.sin(t), color=FIELD, lw=1.8, zorder=z)
        # arrow on the front half (y below centre): moving left-to-right there means counterclockwise from above
        t0 = 1.5 * np.pi + 0.6  # off the wire, so that the arrowhead does not cover it
        p =(1.5 * np.cos(t0 - 0.05), y0 + 0.45 * np.sin(t0 - 0.05))
        q = (1.5 * np.cos(t0 + 0.05), y0 + 0.45 * np.sin(t0 + 0.05))
        arrow(ax, p, q, ms=16, z=6)
        ax.text(1.75, y0 + 0.05, "$B$", color=FIELD, fontsize=14)
    ax.text(0, -2.7, "Большой палец — по току,\nчетыре пальца — по линиям поля", ha="center", fontsize=11, color=GRAY)
    ax.set_xlim(-2.3, 2.4)
    ax.set_ylim(-3.3, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "magnet-wire-right-hand.png")


# ---------------------------------------------------------------- loop, solenoid, magnet

def _trace(F, p0, sign, box, ds=0.02, nmax=9000):
    """Follow a field line from p0 with RK4 steps of fixed length; stop at the box edge or when the line closes."""
    pts = [np.array(p0, float)]

    def unit(p):
        v = np.array(F(p))
        n = np.hypot(*v)
        return sign * v / n if n > 0 else v

    closed = False
    for i in range(nmax):
        p = pts[-1]
        k1 = unit(p)
        k2 = unit(p + 0.5 * ds * k1)
        k3 = unit(p + 0.5 * ds * k2)
        k4 = unit(p + ds * k3)
        q = p + ds * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if abs(q[0]) > box[0] or abs(q[1]) > box[1]:
            break
        pts.append(q)
        if i > 60 and np.hypot(*(q - pts[0])) < 1.5 * ds:
            closed = True
            break
    return np.array(pts), closed


def draw_line(ax, F, seed, box, color=FIELD, lw=1.5, arrows=(0.5,), ds=0.02, tf=None):
    fwd, closed = _trace(F, seed, +1, box, ds)
    if closed:
        line = fwd
    else:
        back, _ = _trace(F, seed, -1, box, ds)
        line = np.vstack([back[::-1], fwd[1:]])
    if tf is not None:
        line = tf(line)  # optional map of the computed line to the drawing frame
    ax.plot(line[:, 0], line[:, 1], color=color, lw=lw, zorder=3, solid_capstyle="round")
    seg = np.hypot(*np.diff(line, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    for f in arrows:
        i = int(np.searchsorted(s, f * s[-1]))
        i = min(max(i, 1), len(line) - 2)
        arrow(ax, line[i - 1], line[i + 1], color=color, lw=lw, ms=13, z=4)
    return line


def _streams(ax, X, Z, Bx, Bz, seeds, box, color=FIELD, lw=1.5, arrows=(0.5,), tf=None):
    from scipy.interpolate import RegularGridInterpolator

    ix = RegularGridInterpolator((X[0], Z[:, 0]), Bx.T, bounds_error=False, fill_value=None)
    iz = RegularGridInterpolator((X[0], Z[:, 0]), Bz.T, bounds_error=False, fill_value=None)
    F = lambda p: (ix(p)[0], iz(p)[0])
    for sd in seeds:
        draw_line(ax, F, sd, box, color=color, lw=lw, arrows=arrows, tf=tf)


def loop_field_lines():
    R = 1.0
    x = np.linspace(-3.4, 3.4, 500)
    z = np.linspace(-3.0, 3.0, 440)
    X, Z = np.meshgrid(x, z)
    Bx, Bz = loop_field(X, Z, R)
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    seeds = [(xx, 0.0) for xx in (0.0, 0.3, 0.55, 0.78, -0.3, -0.55, -0.78)]
    _streams(ax, X, Z, Bx, Bz, seeds, box=(3.35, 2.95), arrows=(0.3, 0.7))
    # loop sections: counterclockwise seen from +z; with x to the right and z up, +y points into the page,
    # so at x=+R the current goes into the page and at x=-R out of it
    cross(ax, R, 0, r=0.09)
    dot(ax, -R, 0, r=0.09)
    ax.plot([-R, R], [0, 0], color=CUR, lw=1, ls=":", zorder=1)
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-3.0, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Виток с током: сечение плоскостью, проходящей через ось")
    save(fig, "magnet-loop-field-lines.png")


def solenoid_field_lines():
    R = 0.8
    N = 17
    L = 4.0
    zs = np.linspace(-L / 2, L / 2, N)
    x = np.linspace(-4.2, 4.2, 340)
    z = np.linspace(-4.2, 4.2, 340)
    X, Z = np.meshgrid(x, z)
    Bx, Bz = stack_field(X, Z, R, zs, n=120)
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    # equal-flux seeds inside the coil: the field there is nearly uniform, so flux grows as x^2
    xs_in = R * 0.8 * np.sqrt(np.arange(1, 5) / 4)
    seeds = [(0.0, 0.0)] + [(s * xx, 0.0) for xx in xs_in for s in (1, -1)]
    # The field is computed with the axis along z and drawn turned by 90 degrees counterclockwise, (x, z) -> (-z, x):
    # the axis of the coil is horizontal, the field inside goes from right to left, the north pole N is at the left
    rot = lambda P: np.column_stack([-P[:, 1], P[:, 0]])
    rp = lambda p: (-p[1], p[0])
    _streams(ax, X, Z, Bx, Bz, seeds, box=(4.15, 4.15), arrows=(0.2, 0.7), tf=rot)
    for zz in zs:
        # current into the page at x=+R (top after the turn), out of the page at x=-R (bottom)
        cross(ax, *rp((R, zz)), r=0.07)
        dot(ax, *rp((-R, zz)), r=0.07)
    ax.add_patch(Rectangle((-L / 2, -R), L, 2 * R, fill=False, ec=MUTED, lw=1, ls="--", zorder=1))
    # the pole labels sit above the axis, beside the field lines that leave the ends
    ax.text(-L / 2 - 0.5, 1.3, "$N$", ha="center", va="center", color=NORTH, fontsize=14, fontweight="bold",
            bbox=dict(fc=PAPER, ec="none", pad=1.5), zorder=8)
    ax.text(L / 2 + 0.5, 1.3, "$S$", ha="center", va="center", color=SOUTH, fontsize=14, fontweight="bold",
            bbox=dict(fc=PAPER, ec="none", pad=1.5), zorder=8)
    # needles: on the axis outside the coil and inside it the north end follows the field to the left; beside the coil it points right
    for c, d in (((0.0, L / 2 + 0.85), (0, 1)), ((0.0, -L / 2 - 0.95), (0, 1)), ((0.16, 0.0), (0, 1)), ((2.0, 0.6), (0, -1)), ((-2.0, 0.6), (0, -1))):
        needle(ax, rp(c), rp(d), L=0.3, w=0.1, z=6)
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-4.2, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Катушка с током: сечение вдоль оси")
    save(fig, "magnet-solenoid-field-lines.png")


def bar_magnet_lines():
    R = 0.45
    L = 3.0
    zs = np.linspace(-L / 2, L / 2, 25)
    x = np.linspace(-4.5, 4.5, 300)
    z = np.linspace(-4.5, 4.5, 300)
    X, Z = np.meshgrid(x, z)
    Bx, Bz = stack_field(X, Z, R, zs, n=100)
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    xs_in = R * 0.8 * np.sqrt(np.arange(1, 5) / 4)
    seeds = [(0.0, 0.0)] + [(s * xx, 0.0) for xx in xs_in for s in (1, -1)]
    _streams(ax, X, Z, Bx, Bz, seeds, box=(4.45, 4.45), lw=1.4, arrows=(0.2, 0.7))
    ax.add_patch(Rectangle((-R, 0), 2 * R, L / 2, fc=NORTH, ec=INK, lw=1.2, alpha=0.35, zorder=5))
    ax.add_patch(Rectangle((-R, -L / 2), 2 * R, L / 2, fc=SOUTH, ec=INK, lw=1.2, alpha=0.35, zorder=5))
    ax.text(-R - 0.25, L / 4, "N", color=NORTH, ha="center", va="center", fontsize=16, fontweight="bold", zorder=7)
    ax.text(-R - 0.25, -L / 4, "S", color=SOUTH, ha="center", va="center", fontsize=16, fontweight="bold", zorder=7)
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Полосовой магнит: линии выходят из N и входят в S")
    save(fig, "magnet-bar-field-lines.png")


def two_magnets(attract):
    R = 0.4
    L = 2.0
    zs = np.linspace(-L / 2, L / 2, 15)
    x = np.linspace(-3.0, 3.0, 260)
    z = np.linspace(-4.0, 4.0, 340)
    X, Z = np.meshgrid(x, z)
    gap = 0.8
    c1, c2 = -(L / 2 + gap / 2), (L / 2 + gap / 2)
    # magnet 1 (lower): N up. magnet 2 (upper): N up if attract (S faces N of the first), N down if repel.
    Bx1, Bz1 = stack_field(X, Z - c1, R, zs, n=100)
    Bx2, Bz2 = stack_field(X, Z - c2, R, zs, n=100)
    s = 1 if attract else -1
    Bx, Bz = Bx1 + s * Bx2, Bz1 + s * Bz2
    fig, ax = plt.subplots(figsize=(4.6, 6.6))
    # seeds well inside the winding (x < R): a seed at 0.9 R made the tracer circle a wire and draw the same piece thousands of times
    xs_in = R * 0.8 * np.sqrt(np.arange(1, 4) / 3)
    seeds = [(sg * xx, c1) for xx in xs_in for sg in (1, -1)]
    if attract:
        seeds.append((0.0, c1))
    else:
        seeds += [(sg * xx, c2) for xx in xs_in for sg in (1, -1)]
    # the lines stop inside the window (xlim 2.6)
    _streams(ax, X, Z, Bx, Bz, seeds, box=(2.55, 3.95), lw=1.3, arrows=(0.2, 0.7))
    for c, up_is_north in ((c1, True), (c2, attract)):
        top, bot = (NORTH, SOUTH) if up_is_north else (SOUTH, NORTH)
        tl, bl = ("N", "S") if up_is_north else ("S", "N")
        ax.add_patch(Rectangle((-R, c), 2 * R, L / 2, fc=top, ec=INK, lw=1.2, zorder=6))
        ax.add_patch(Rectangle((-R, c - L / 2), 2 * R, L / 2, fc=bot, ec=INK, lw=1.2, zorder=6))
        ax.text(0, c + L / 4, tl, color=PAPER, ha="center", va="center", fontsize=14, fontweight="bold", zorder=7)
        ax.text(0, c - L / 4, bl, color=PAPER, ha="center", va="center", fontsize=14, fontweight="bold", zorder=7)
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-4.0, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Разноимённые полюса притягиваются" if attract else "Одноимённые полюса отталкиваются", fontsize=11)
    save(fig, "magnet-attract.png" if attract else "magnet-repel.png")


def cut_magnet():
    fig, axs = plt.subplots(3, 1, figsize=(6.4, 4.4))
    def bar(ax, x0, w, first="N"):
        h = 0.8
        half = w / 2
        ax.add_patch(Rectangle((x0, 0), half, h, fc=SOUTH, ec=INK, lw=1.2))
        ax.add_patch(Rectangle((x0 + half, 0), half, h, fc=NORTH, ec=INK, lw=1.2))
        ax.text(x0 + half / 2, h / 2, "S", color=PAPER, ha="center", va="center", fontsize=13, fontweight="bold")
        ax.text(x0 + half * 1.5, h / 2, "N", color=PAPER, ha="center", va="center", fontsize=13, fontweight="bold")
    bar(axs[0], 0, 6)
    bar(axs[1], 0, 2.8)
    bar(axs[1], 3.2, 2.8)
    for x0 in (0, 1.55, 3.1, 4.65):
        bar(axs[2], x0, 1.35)
    for ax in axs:
        ax.set_xlim(-0.2, 6.2)
        ax.set_ylim(-0.2, 1.0)
        ax.set_aspect("equal")
        ax.axis("off")
    axs[0].set_title("Магнит нельзя разделить на отдельные полюса: каждая часть — снова магнит", fontsize=11)
    save(fig, "magnet-cut.png")


def ampere_hypothesis():
    """End face of a magnet: small closed currents (molecular currents) all run the same way."""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.add_patch(Rectangle((0, 0), 6, 3, fc=LIGHT, ec=INK, lw=1.2))
    for i in range(6):
        for j in range(3):
            cx, cy = 0.5 + i, 0.5 + j
            ax.add_patch(Circle((cx, cy), 0.33, fill=False, ec=CUR, lw=1.4))
            arrow(ax, (cx - 0.02, cy - 0.33), (cx + 0.02, cy - 0.33), color=CUR, lw=1.4, ms=9)
    ax.set_xlim(-0.3, 6.3)
    ax.set_ylim(-0.3, 3.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Торец магнита: молекулярные токи (схема)", fontsize=11)
    save(fig, "magnet-ampere-hypothesis.png")


def magnet_shapes():
    from matplotlib.patches import Ellipse, Wedge

    fig, axs = plt.subplots(1, 3, figsize=(10.0, 3.0))
    # bar
    ax = axs[0]
    ax.add_patch(Rectangle((-1.6, -0.35), 1.6, 0.7, fc=SOUTH, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((0, -0.35), 1.6, 0.7, fc=NORTH, ec=INK, lw=1.2))
    ax.text(-0.8, 0, "S", color=PAPER, ha="center", va="center", fontsize=15, fontweight="bold")
    ax.text(0.8, 0, "N", color=PAPER, ha="center", va="center", fontsize=15, fontweight="bold")
    ax.set_title("Полосовой", fontsize=12)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.3, 1.3)
    # horseshoe: two colored halves of a bent bar
    ax = axs[1]
    ax.add_patch(Wedge((0, 0), 1.1, 0, 180, width=0.5, fc=SOUTH, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-1.1, -0.9), 0.5, 0.9, fc=SOUTH, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((0.6, -0.9), 0.5, 0.9, fc=NORTH, ec=INK, lw=1.2))
    ax.add_patch(Wedge((0, 0), 1.1, 0, 90, width=0.5, fc=NORTH, ec=INK, lw=1.2))
    ax.text(-0.85, -0.55, "S", color=PAPER, ha="center", va="center", fontsize=14, fontweight="bold")
    ax.text(0.85, -0.55, "N", color=PAPER, ha="center", va="center", fontsize=14, fontweight="bold")
    ax.set_title("Подковообразный", fontsize=12)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.3, 1.5)
    # ring, magnetised along its axis: the top face is one pole, the bottom face the other
    ax = axs[2]
    ax.add_patch(Ellipse((0, -0.3), 2.4, 1.0, fc=SOUTH, ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-1.2, -0.3), 2.4, 0.6, fc=SOUTH, ec="none"))
    ax.plot([-1.2, -1.2], [-0.3, 0.3], color=INK, lw=1.2)
    ax.plot([1.2, 1.2], [-0.3, 0.3], color=INK, lw=1.2)
    ax.add_patch(Ellipse((0, 0.3), 2.4, 1.0, fc=NORTH, ec=INK, lw=1.2))
    ax.add_patch(Ellipse((0, 0.3), 0.9, 0.36, fc=PAPER, ec=INK, lw=1.2))
    ax.text(0, 0.72, "N", color=NORTH, ha="center", fontsize=13, fontweight="bold")
    ax.text(0, -1.0, "S", color=SOUTH, ha="center", fontsize=13, fontweight="bold")
    ax.set_title("Кольцевой", fontsize=12)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.3, 1.3)
    for ax in axs:
        ax.set_aspect("equal")
        ax.axis("off")
    save(fig, "magnet-shapes.png")


# ---------------------------------------------------------------- Earth

def earth_field():
    tilt = np.radians(10)
    # dipole moment m points to the geographic south (field lines leave the magnet's N pole, which sits in the south)
    m = np.array([np.sin(tilt), -np.cos(tilt)])  # tilted axis, pointing to the south
    fig, ax = plt.subplots(figsize=(7.4, 7.4))
    # dipole field line: r = Lsh * sin^2(theta), theta counted from the magnetic axis; the field runs from theta=0 (m side) to theta=pi
    axis = m
    perp = np.array([-m[1], m[0]])
    for Lsh in (1.5, 2.0, 2.7, 3.6):
        for side in (1, -1):
            th0 = np.arcsin(np.sqrt(1 / Lsh))
            th = np.linspace(th0, np.pi - th0, 300)
            rr = Lsh * np.sin(th) ** 2
            px = rr * (np.cos(th) * axis[0] + side * np.sin(th) * perp[0])
            py = rr * (np.cos(th) * axis[1] + side * np.sin(th) * perp[1])
            ax.plot(px, py, color=FIELD, lw=1.4, zorder=3)
            for f in (0.3, 0.7):
                i = int(f * len(px))
                arrow(ax, (px[i - 1], py[i - 1]), (px[i + 1], py[i + 1]), ms=13)
    ax.add_patch(Circle((0, 0), 1.0, fc=tint(SKY, 0.8), ec=INK, lw=1.5, zorder=4))
    # geographic axis
    ax.plot([0, 0], [-1.5, 1.5], color=INK, lw=1.4, ls="--", zorder=5)
    ax.text(0.06, 1.55, "Северный географический\nполюс", ha="left", va="bottom", fontsize=10)
    ax.text(0.06, -1.55, "Южный географический\nполюс", ha="left", va="top", fontsize=10)
    # magnetic axis
    ax.plot([-1.5 * m[0], 1.5 * m[0]], [-1.5 * m[1], 1.5 * m[1]], color=GRAY, lw=1.6, zorder=5)
    # the magnetic pole in the north is a S pole (field lines enter), in the south it is an N pole
    ax.plot([-m[0]], [-m[1]], "o", color=SOUTH, ms=9, zorder=7)
    ax.plot([m[0]], [m[1]], "o", color=NORTH, ms=9, zorder=7)
    ax.annotate("Южный магнитный полюс\n(у северного географического)", xy=(-m[0], -m[1]), xytext=(-3.9, 2.4),
                arrowprops=dict(arrowstyle="->", color=SOUTH), color=SOUTH, fontsize=10, zorder=8)
    ax.annotate("Северный магнитный полюс\n(у южного географического)", xy=(m[0], m[1]), xytext=(-3.9, -2.9),
                arrowprops=dict(arrowstyle="->", color=NORTH), color=NORTH, fontsize=10, zorder=8)
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-4.2, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Магнитное поле Земли: линии входят на севере, выходят на юге")
    save(fig, "earth-field-lines.png")


def earth_inclination():
    """A needle free to turn in the vertical plane lies along the field line: it dips at middle latitudes."""
    tilt = np.radians(10)
    m = np.array([np.sin(tilt), -np.cos(tilt)])
    axis = m
    perp = np.array([-m[1], m[0]])
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    for Lsh in (1.6, 2.4):
        th0 = np.arcsin(np.sqrt(1 / Lsh))
        th = np.linspace(th0, np.pi - th0, 200)
        rr = Lsh * np.sin(th) ** 2
        for side in (1,):
            ax.plot(rr * (np.cos(th) * axis[0] + side * np.sin(th) * perp[0]), rr * (np.cos(th) * axis[1] + side * np.sin(th) * perp[1]),
                    color=FIELD, lw=1.0, alpha=0.55, zorder=1)
    ax.add_patch(Circle((0, 0), 1.0, fc=tint(SKY, 0.8), ec=INK, lw=1.5, zorder=2))
    ax.plot([0, 0], [-1.35, 1.35], color=INK, lw=1.2, ls="--", zorder=3)
    # the labels stand left of the axis: the needles at 75 degrees occupy the space to its right
    ax.text(-0.06, 1.38, "Северный географический полюс", fontsize=10, ha="right")
    ax.text(-0.06, -1.5, "Южный географический полюс", fontsize=10, ha="right")
    for deg in (75, 45, 0, -45, -75):
        a = np.radians(deg)
        p = np.array([np.cos(a), np.sin(a)])
        B = 3 * np.dot(m, p) * p - m
        B = B / np.linalg.norm(B)
        c = p * 1.32  # far enough from the globe that the tip at 75 degrees stays outside it
        needle(ax, c, B, L=0.26, w=0.08, z=6)
        if deg == 45:
            tang = np.array([-p[1], p[0]])  # local horizontal, pointing north
            ax.plot([c[0] - tang[0] * 0.45, c[0] + tang[0] * 0.45], [c[1] - tang[1] * 0.45, c[1] + tang[1] * 0.45], color=GRAY, lw=1.1, ls=":", zorder=5)
            ax.annotate("горизонталь", xy=c + tang * 0.42, xytext=(1.85, 0.95), fontsize=10, color=GRAY, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(-1.6, 2.6)
    ax.set_ylim(-1.7, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Стрелка ложится вдоль линии поля", fontsize=11)
    save(fig, "earth-inclination.png")


def earth_declination():
    """Top view, east and west declination: the needle turns off the geographic meridian toward the east (alpha > 0) or the west (alpha < 0)."""
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.4))
    d = np.radians(20)
    for ax, sgn, title, sign_txt in zip(axes, (+1, -1), ("Восточное склонение", "Западное склонение"), (r"$\alpha>0$", r"$\alpha<0$")):
        ax.plot([0, 0], [-1.6, 2.7], color=INK, lw=1.6)
        arrow(ax, (0, 2.3), (0, 2.75), color=INK, lw=1.6, ms=13)
        ax.text(0.08, 2.75, "С", fontsize=13, fontweight="bold")
        ax.text(0.08, -1.85, "Ю", fontsize=13, fontweight="bold")
        # the magnetic meridian is the line along the needle
        dx, dy = sgn * np.sin(d), np.cos(d)
        # the meridian runs through the needle axis (0, 0.4)
        ax.plot([-1.6 * dx, 2.5 * dx], [0.4 - 1.6 * dy, 0.4 + 2.5 * dy], color=CUR, lw=1.4, ls="--")
        needle(ax, (0, 0.4), (dx, dy), L=1.0, w=0.2, z=5)
        t = np.linspace(np.pi / 2, np.pi / 2 - sgn * d, 30)
        ax.plot(1.7 * np.cos(t), 0.4 + 1.7 * np.sin(t), color=GRAY, lw=1.3)
        ax.text(sgn * 0.55 - 0.1, 2.35 - 0.1, r"$\alpha$", fontsize=14, color=GRAY)
        ax.text(0, -2.35, title + ", " + sign_txt, ha="center", fontsize=12)
        ax.set_xlim(-2.4, 2.4)
        ax.set_ylim(-2.6, 3.1)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.0, "Сплошная линия — географический меридиан, пунктир — магнитный меридиан", ha="center", color=GRAY, fontsize=10.5)
    save(fig, "earth-declination.png")


def coil_drawing():
    """Two ways to show how a coil is wound: on a core, or by line thickness (thick = near, thin dashed = behind)."""
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.0))
    ax = axes[0]
    ax.add_patch(Rectangle((-2.2, -0.7), 4.4, 1.4, fc=LIGHT, ec=INK, lw=1.2, zorder=1))
    for x in np.linspace(-1.6, 1.6, 6):
        ax.plot([x - 0.12, x + 0.12], [-0.95, 0.95], color=CUR, lw=2.2, zorder=3)
        ax.plot([x + 0.12, x + 0.52], [0.95, -0.95], color=CUR, lw=1.0, ls=":", zorder=0)
    ax.set_title("На каркасе:\nвитки перед ним идут вверх, за ним вниз", fontsize=10)
    ax = axes[1]
    for x in np.linspace(-1.6, 1.6, 6):
        ax.plot([x - 0.12, x + 0.12], [-0.95, 0.95], color=CUR, lw=2.6)
        ax.plot([x + 0.12, x + 0.52], [0.95, -0.95], color=CUR, lw=0.8, ls=(0, (2, 2)))
    ax.set_title("Толщиной линии:\nтолстая ближе к нам, тонкая прерывистая дальше", fontsize=10)
    for ax in axes:
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
    save(fig, "magnet-coil-drawing.png")


ALL = {
    "wire": [wire_field_lines, wire_vectors, wire_compass, wire_gimlet, oersted, cross_dot_legend, task_vertical_wire],
    "loop": [loop_field_lines],
    "solenoid": [solenoid_field_lines, coil_drawing],
    "bar": [bar_magnet_lines, lambda: two_magnets(True), lambda: two_magnets(False), cut_magnet, ampere_hypothesis, magnet_shapes],
    "earth": [earth_field, earth_inclination, earth_declination],
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(ALL)
    for n in names:
        for f in ALL[n]:
            f()
