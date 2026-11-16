"""Figures for the notes "Площадь и объём" and "Мега-, макро- и микромир" (course Физика 7-9, lessons 5, 6, 9, 10).

Run: python3 area_volume_scale.py
PNG files go to content/01. Введение и измерения/00. Вложения/
File prefixes: area-, volume-, scale-of-world-
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle, Wedge
from matplotlib.path import Path as MPath

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "01. Введение и измерения"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, COPPER, GREEN, INK, MUTED, PAPER, RED, SKY, WARM, num, saver, tint

GRID = ASH
C_BLUE = tint(BLUE, 0.7)  # a pale fill of a body
C_BLUE_D = BLUE  # the same colour as a line, a point or a label
C_ORANGE = tint(WARM, 0.4)  # a second pale fill beside C_BLUE
C_RED = RED
C_GREEN = GREEN
C_GREY = MUTED
C_WATER = tint(SKY, 0.6)
C_GLASS = tint(SKY, 0.85)


save = saver(OUT)


def off(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def dim_arrow(ax, p, q, text, off_xy=(0, 0), both=True, color=INK, fs=11, ha="center", va="center"):
    style = "<->" if both else "->"
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, lw=1.2, color=color))
    ax.text((p[0] + q[0]) / 2 + off_xy[0], (p[1] + q[1]) / 2 + off_xy[1], text, color=color, fontsize=fs, ha=ha, va=va,
            bbox=dict(fc=PAPER, ec="none", pad=1.5), zorder=8)


def shade(color, k):
    c = np.array(matplotlib.colors.to_rgb(color))
    return tuple(np.clip(c * k, 0, 1))


def right_angle(ax, corner, sx, sy, size=0.18):
    x, y = corner
    ax.plot([x + sx * size, x + sx * size, x], [y, y + sy * size, y + sy * size], color=INK, lw=1)


def box3d(ax, x0, y0, w, d, h, dx, dy, face, edge=INK, grid=(0, 0, 0), lw=1.3):
    """Oblique box: front face w x h, depth d shifted by (dx, dy) per unit d. grid = cells along w, d, h"""
    ox, oy = dx * d, dy * d
    front = Polygon([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], fc=face, ec=edge, lw=lw)
    top = Polygon([(x0, y0 + h), (x0 + w, y0 + h), (x0 + w + ox, y0 + h + oy), (x0 + ox, y0 + h + oy)],
                  fc=shade(face, 1.1), ec=edge, lw=lw)
    side = Polygon([(x0 + w, y0), (x0 + w + ox, y0 + oy), (x0 + w + ox, y0 + h + oy), (x0 + w, y0 + h)],
                   fc=shade(face, 0.85), ec=edge, lw=lw)
    for p in (front, top, side):
        ax.add_patch(p)
    gw, gd, gh = grid
    thin = dict(color=edge, lw=0.7, alpha=0.75)
    for i in range(1, gw):
        x = x0 + w * i / gw
        ax.plot([x, x], [y0, y0 + h], **thin)
        ax.plot([x, x + ox], [y0 + h, y0 + h + oy], **thin)
    for k in range(1, gh):
        y = y0 + h * k / gh
        ax.plot([x0, x0 + w], [y, y], **thin)
        ax.plot([x0 + w, x0 + w + ox], [y, y + oy], **thin)
    for j in range(1, gd):
        t = j / gd
        ax.plot([x0 + w + ox * t, x0 + w + ox * t], [y0 + oy * t, y0 + h + oy * t], **thin)
        ax.plot([x0 + ox * t, x0 + w + ox * t], [y0 + h + oy * t, y0 + h + oy * t], **thin)


# 1. formulas of areas -------------------------------------------------
def fig_area_formulas():
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 3, 3, fc=C_BLUE, ec=INK, lw=1.4))
    dim_arrow(ax, (0, -0.35), (3, -0.35), "$a$")
    dim_arrow(ax, (3.35, 0), (3.35, 3), "$a$")
    ax.text(1.5, 1.5, "$S$", ha="center", va="center", fontsize=16)
    ax.text(1.5, -1.2, "$S = a \\cdot a = a^2$", ha="center", fontsize=13)
    ax.set_xlim(-0.6, 4.2)
    ax.set_ylim(-1.7, 3.5)
    ax.set_title("Квадрат")
    off(ax)

    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 4.5, 2.6, fc=C_BLUE, ec=INK, lw=1.4))
    dim_arrow(ax, (0, -0.35), (4.5, -0.35), "$a$")
    dim_arrow(ax, (4.85, 0), (4.85, 2.6), "$b$")
    ax.text(2.25, 1.3, "$S$", ha="center", va="center", fontsize=16)
    ax.text(2.25, -1.2, "$S = a \\cdot b$", ha="center", fontsize=13)
    ax.set_xlim(-0.6, 5.5)
    ax.set_ylim(-1.7, 3.5)
    ax.set_title("Прямоугольник")
    off(ax)

    ax = axes[2]
    a, h, p = 4.5, 2.8, 1.4
    ax.add_patch(Polygon([(0, 0), (a, 0), (p, h)], fc=C_BLUE, ec=INK, lw=1.4))
    ax.plot([p, p], [0, h], color=C_RED, lw=1.3, ls="--")
    right_angle(ax, (p, 0), 1, 1)
    dim_arrow(ax, (0, -0.35), (a, -0.35), "$a$ (основание)")
    ax.text(p - 0.2, h / 2, "$h$", color=C_RED, ha="right", va="center", fontsize=13)
    ax.text(2.4, 0.9, "$S$", ha="center", va="center", fontsize=16)
    ax.text(2.25, -1.2, "$S = \\frac{1}{2}\\,a\\,h$", ha="center", fontsize=13)
    ax.set_xlim(-0.6, 5.2)
    ax.set_ylim(-1.7, 3.5)
    ax.set_title("Треугольник")
    off(ax)

    ax = axes[3]
    ax.add_patch(Circle((0, 0), 1.6, fc=C_BLUE, ec=INK, lw=1.4))
    ax.plot([0, 1.6], [0, 0], color=C_RED, lw=1.6)
    ax.plot([0, 0], [0, 0], "o", color=INK, ms=3)
    ax.text(0.8, 0.18, "$r$", color=C_RED, ha="center", fontsize=13)
    dim_arrow(ax, (-1.6, -1.95), (1.6, -1.95), "$d = 2r$", off_xy=(0, -0.3))
    ax.text(-0.4, 0.75, "$S$", ha="center", va="center", fontsize=16)
    ax.text(0, -3.05, "$S = \\pi r^2 = \\dfrac{\\pi d^2}{4}$", ha="center", fontsize=13)
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-3.6, 2.0)
    ax.set_title("Круг")
    off(ax)
    fig.tight_layout()
    save(fig, "area-basic-figures.png")


# 2. triangle = half of rectangle --------------------------------------
def fig_triangle_half():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.15, 1]})
    a, h, p = 5.0, 3.0, 1.8
    ax = axes[0]
    ax.add_patch(Polygon([(0, 0), (p, 0), (p, h)], fc=C_BLUE, ec=INK, lw=1.2))
    ax.add_patch(Polygon([(0, 0), (p, h), (0, h)], fc=C_ORANGE, ec=INK, lw=1.2))
    ax.add_patch(Polygon([(p, 0), (a, 0), (p, h)], fc=C_BLUE, ec=INK, lw=1.2))
    ax.add_patch(Polygon([(p, h), (a, 0), (a, h)], fc=C_ORANGE, ec=INK, lw=1.2))
    ax.plot([p, p], [0, h], color=C_RED, lw=1.5, ls="--")
    ax.text(p - 0.12, h / 2, "$h$", color=C_RED, ha="right", va="center", fontsize=13)
    dim_arrow(ax, (0, -0.4), (a, -0.4), "$a$")
    for lab, (px, py) in zip("1234", [(1.2, 0.9), (0.6, 2.1), (2.87, 0.9), (3.93, 2.1)]):
        ax.text(px, py, lab, ha="center", va="center", fontsize=12)
    ax.text(a / 2, -1.25, "Прямоугольник $a \\times h$: части 1 = 2 и 3 = 4", ha="center", fontsize=11)
    ax.set_xlim(-0.5, 5.6)
    ax.set_ylim(-1.7, 3.5)
    ax.set_title("Синий треугольник и достройка до прямоугольника")
    off(ax)

    ax = axes[1]
    ax.add_patch(Polygon([(0, 0), (a, 0), (p, h)], fc=C_BLUE, ec=INK, lw=1.4))
    ax.plot([p, p], [0, h], color=C_RED, lw=1.4, ls="--")
    right_angle(ax, (p, 0), 1, 1)
    ax.text(p - 0.12, h / 2, "$h$", color=C_RED, ha="right", va="center", fontsize=13)
    dim_arrow(ax, (0, -0.4), (a, -0.4), "$a$")
    ax.text(a / 2, -1.25, "$S = \\dfrac{1}{2}\\,a\\,h$: синие части = половина прямоугольника", ha="center", fontsize=11)
    ax.set_xlim(-0.5, 5.6)
    ax.set_ylim(-1.7, 3.5)
    ax.set_title("Площадь треугольника")
    off(ax)
    fig.tight_layout()
    save(fig, "area-triangle-half-rectangle.png")


# 3. pi as L/d ---------------------------------------------------------
def fig_pi_ratio():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.4), gridspec_kw={"width_ratios": [1, 2.2]})
    ax1.add_patch(Circle((0, 0), 1.5, fc=C_GLASS, ec=INK, lw=1.6))
    ax1.plot([-1.5, 1.5], [0, 0], color=C_RED, lw=1.6)
    ax1.text(0, 0.15, "$d$", color=C_RED, ha="center", fontsize=13)
    ax1.text(0, 1.85, "длина окружности $L$", ha="center", fontsize=11)
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-1.8, 2.3)
    off(ax1)

    d, L = 66.5, 209.0
    ax2.add_patch(Rectangle((0, 2.0), L, 0.7, fc=C_BLUE, ec=INK, lw=1.2))
    ax2.text(L / 2, 2.35, "$L = 209$ мм", ha="center", va="center", fontsize=12)
    for i in range(3):
        ax2.add_patch(Rectangle((i * d, 0.9), d, 0.7, fc=C_ORANGE, ec=INK, lw=1.2))
        ax2.text(i * d + d / 2, 1.25, "$d = 66{,}5$ мм", ha="center", va="center", fontsize=10)
    rem = L - 3 * d
    ax2.add_patch(Rectangle((3 * d, 0.9), rem, 0.7, fc=tint(C_GREEN, 0.6), ec=INK, lw=1.2))
    ax2.annotate("остаток $9{,}5$ мм\n$\\approx 0{,}14\\,d$", (3 * d + rem / 2, 0.9), (3 * d + rem / 2 + 5, -0.45),
                 ha="center", fontsize=10, arrowprops=dict(arrowstyle="-", color=INK, lw=0.9))
    ax2.text(L / 2, -1.5, "$\\dfrac{L}{d} = \\dfrac{209}{66{,}5} \\approx 3{,}14 = \\pi$", ha="center", fontsize=14)
    ax2.set_xlim(-5, L + 8)
    ax2.set_ylim(-2.4, 3.2)
    ax2.axis("off")
    fig.tight_layout()
    save(fig, "area-pi-ratio.png")


# palette helpers -------------------------------------------------------
def cell_counts(poly, nx, ny, ox=0.0, oy=0.0, ns=40):
    p = MPath(poly)
    xs = (np.arange(ns) + 0.5) / ns
    kinds = {}
    for i in range(nx):
        for j in range(ny):
            X, Y = np.meshgrid(ox + i + xs, oy + j + xs)
            frac = p.contains_points(np.c_[X.ravel(), Y.ravel()]).mean()
            kinds[(i, j)] = "full" if frac > 0.9999 else ("part" if frac > 0 else "none")
    n = sum(v == "full" for v in kinds.values())
    k = sum(v == "part" for v in kinds.values())
    return kinds, n, k


def draw_palette(ax, poly, kinds, nx, ny, fc):
    for i in range(nx + 1):
        ax.plot([i, i], [0, ny], color=GRID, lw=1, zorder=0)
    for j in range(ny + 1):
        ax.plot([0, nx], [j, j], color=GRID, lw=1, zorder=0)
    ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=INK, lw=1.8, alpha=0.55, zorder=1))
    for (i, j), kind in kinds.items():
        if kind == "full":
            ax.plot([i + 0.2, i + 0.8], [j + 0.2, j + 0.8], color=C_RED, lw=1.5, zorder=3)
            ax.plot([i + 0.2, i + 0.8], [j + 0.8, j + 0.2], color=C_RED, lw=1.5, zorder=3)
        elif kind == "part":
            ax.plot([i + 0.5], [j + 0.5], "o", color=C_BLUE_D, ms=5, zorder=3)


# 4. palette on a blob (board figure: n = 6, k = 13) -------------------
def fig_palette_blob():
    t = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    r = 1 + 0.08 * np.cos(3 * t + 0.5) + 0.05 * np.sin(2 * t)
    cx, cy, a, b = 3.25, 3.0, 2.3, 1.7
    poly = np.c_[cx + a * r * np.cos(t), cy + b * r * np.sin(t)]
    nx, ny = 7, 6
    kinds, n, k = cell_counts(poly, nx, ny, ns=30)
    assert (n, k) == (6, 13), (n, k)
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    draw_palette(ax, poly, kinds, nx, ny, C_BLUE)
    ax.add_patch(Rectangle((6, 4), 1, 1, fc="none", ec=INK, hatch="////", lw=1.2, zorder=2))
    ax.annotate("$S_1$", (7, 4.5), (7.45, 4.5), fontsize=14, va="center")
    ax.text(0, -0.5, "$\\times$ полностью закрытые: $n = %d$      $\\bullet$ частично закрытые: $k = %d$" % (n, k), fontsize=11)
    ax.text(0, -1.05, "$S = S_1\\,(n + \\frac{1}{2}k) = S_1\\,(6 + 6{,}5) = 12{,}5\\,S_1$", fontsize=13, color=C_RED)
    ax.set_xlim(-0.2, 8.2)
    ax.set_ylim(-1.4, 6.3)
    off(ax)
    save(fig, "area-palette-blob.png")


# 5. palette on the triangle (lab of the lesson: n = 21, k = 12) -------
def fig_palette_triangle():
    poly = [(0, 0), (9, 0), (3, 6)]
    nx, ny = 10, 7
    kinds, n, k = cell_counts(poly, nx, ny)
    assert (n, k) == (21, 12), (n, k)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    draw_palette(ax, poly, kinds, nx, ny, C_BLUE)
    dim_arrow(ax, (0, -0.5), (9, -0.5), "$a = 4{,}5$ см (9 клеток)", off_xy=(0, -0.4), fs=11)
    dim_arrow(ax, (-0.55, 0), (-0.55, 6), "$h = 3$ см", off_xy=(-0.95, 0), fs=11)
    ax.plot([3, 3], [0, 6], color=C_RED, lw=1.2, ls="--", zorder=4)
    ax.text(0.2, 7.35, "клетка $0{,}5 \\times 0{,}5$ см: $S_1 = 0{,}25$ см$^2$; $n = %d$, $k = %d$" % (n, k), fontsize=11)
    ax.text(0.2, -1.9, "$S = 0{,}25\\,(21 + 6) = 6{,}75$ см$^2$  и  $S = \\frac{1}{2} \\cdot 4{,}5 \\cdot 3 = 6{,}75$ см$^2$",
            fontsize=12, color=C_RED)
    ax.set_xlim(-2.2, 10.4)
    ax.set_ylim(-2.4, 7.9)
    off(ax)
    save(fig, "area-palette-triangle.png")


# 6. palette refinement: inner and outer counts squeeze pi -------------
def fig_palette_refinement():
    R = 1.0
    c = np.array([0.3, 0.2])
    sides = [1.0 / 2 ** m for m in range(0, 9)]
    inner, outer, est = [], [], []
    for s in sides:
        m = int(np.ceil((R + 1) / s)) + 1
        idx = np.arange(-m, m)
        X0, Y0 = np.meshgrid(idx * s, idx * s)
        dxn = np.maximum(np.maximum(X0 - c[0], c[0] - (X0 + s)), 0)
        dyn = np.maximum(np.maximum(Y0 - c[1], c[1] - (Y0 + s)), 0)
        near = np.hypot(dxn, dyn)
        dxf = np.maximum(abs(X0 - c[0]), abs(X0 + s - c[0]))
        dyf = np.maximum(abs(Y0 - c[1]), abs(Y0 + s - c[1]))
        far = np.hypot(dxf, dyf)
        full = far <= R
        touch = near < R
        n = full.sum()
        k = (touch & ~full).sum()
        inner.append(n * s * s)
        outer.append((n + k) * s * s)
        est.append(s * s * (n + k / 2))
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.axhline(np.pi, color=INK, lw=1.2, ls="--")
    ax.text(2 ** -8, 2.6, "точная площадь $\\pi$", ha="right", fontsize=10)
    ax.plot(sides, outer, "o-", color=COPPER, lw=2, label="$S_1\\,(n + k)$: не меньше площади")
    ax.plot(sides, inner, "o-", color=C_BLUE_D, lw=2, label="$S_1\\,n$: не больше площади")
    ax.plot(sides, est, "s-", color=C_RED, lw=2, label="палетка $S_1\\,(n + \\frac{1}{2}k)$")
    ax.set_xscale("log", base=2)
    ax.invert_xaxis()
    ax.set_xlabel("Сторона клетки, доли радиуса круга")
    ax.set_ylabel("Оценка площади круга радиуса 1")
    ax.set_title("Мельчение сетки сжимает оценку")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", fontsize=9.5, frameon=False)
    save(fig, "area-palette-refinement.png")


# 7. CD ring -----------------------------------------------------------
def fig_cd_ring():
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.add_patch(Circle((0, 0), 2.0, fc=C_BLUE, ec=INK, lw=1.4, alpha=0.6))
    ax.add_patch(Circle((0, 0), 0.5, fc=PAPER, ec=INK, lw=1.4))
    ax.plot([0, 2.0 * np.cos(0.6)], [0, 2.0 * np.sin(0.6)], color=C_RED, lw=1.6)
    ax.text(1.05, 1.0, "$R$", color=C_RED, fontsize=13)
    ax.plot([0, 0.5 * np.cos(-1.0)], [0, 0.5 * np.sin(-1.0)], color=C_GREEN, lw=1.8)
    ax.text(0.42, -0.62, "$r$", color=C_GREEN, fontsize=13)
    ax.text(0, -2.75, "$S = \\pi R^2 - \\pi r^2$", ha="center", fontsize=13)
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-3.2, 2.4)
    off(ax)
    save(fig, "area-cd-ring.png")


# 8. cube and cuboid with unit cubes ----------------------------------
def fig_volume_cubes():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    dx, dy = 0.55, 0.38
    ax = axes[0]
    box3d(ax, 0, 0, 3, 3, 3, dx, dy, C_BLUE, grid=(3, 3, 3))
    dim_arrow(ax, (0, -0.4), (3, -0.4), "$a$")
    dim_arrow(ax, (3 + 3 * dx + 0.4, 3 * dy), (3 + 3 * dx + 0.4, 3 * dy + 3), "$a$")
    ax.text(3 + 1.5 * dx + 0.3, 1.5 * dy - 0.4, "$a$", fontsize=11, color=INK)
    ax.text(2.4, -1.4, "Куб: $V = a \\cdot a \\cdot a = a^3 = 27$ кубиков при $a = 3$", ha="center", fontsize=12)
    ax.set_xlim(-0.8, 6.6)
    ax.set_ylim(-2.0, 5.6)
    off(ax)

    ax = axes[1]
    box3d(ax, 0, 0, 4, 2, 3, dx, dy, C_ORANGE, grid=(4, 2, 3))
    dim_arrow(ax, (0, -0.4), (4, -0.4), "$a = 4$")
    dim_arrow(ax, (4 + 2 * dx + 0.4, 2 * dy), (4 + 2 * dx + 0.4, 2 * dy + 3), "$c = 3$")
    ax.text(4 + dx + 0.3, dy - 0.4, "$b = 2$", fontsize=11, color=INK)
    ax.text(2.6, -1.4, "Параллелепипед: $V = abc = 4 \\cdot 2 \\cdot 3 = 24$ кубика", ha="center", fontsize=12)
    ax.set_xlim(-0.8, 7.4)
    ax.set_ylim(-2.0, 5.2)
    off(ax)
    fig.tight_layout()
    save(fig, "volume-cube-cuboid.png")


# 9. cuboid and cylinder as stacks of base layers ----------------------
def fig_volume_layers():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    dx, dy = 0.55, 0.38
    ax = axes[0]
    nl = 5
    for i in range(nl):
        box3d(ax, 0, i * 0.5, 3.4, 2.0, 0.5, dx, dy, C_ORANGE if i % 2 == 0 else shade(C_ORANGE, 1.06))
    ax.text(2.8, 2.88, "$S_{\\rm осн}$", ha="center", fontsize=13, color=C_RED, va="center", zorder=9)
    ax.set_xlim(-0.8, 6.3)
    ax.set_ylim(-1.7, 4.6)
    dim_arrow(ax, (3.4 + 2 * dx + 0.45, 2 * dy), (3.4 + 2 * dx + 0.45, 2 * dy + 2.5), "$c$", off_xy=(0.35, 0))
    ax.text(2.6, -1.1, "Слои основания: $V = S_{\\rm осн} \\cdot c$", ha="center", fontsize=12)
    ax.set_title("Прямоугольный параллелепипед")
    off(ax)

    ax = axes[1]
    R, ry, H, nl = 1.5, 0.5, 2.5, 5
    for i in range(nl):
        y = i * H / nl
        ax.add_patch(Rectangle((-R, y), 2 * R, H / nl, fc=C_BLUE, ec="none"))
        ax.add_patch(Ellipse((0, y), 2 * R, 2 * ry, fc=C_BLUE if i % 2 else shade(C_BLUE, 0.93), ec=INK, lw=0.9))
    ax.plot([-R, -R], [0, H], color=INK, lw=1.4)
    ax.plot([R, R], [0, H], color=INK, lw=1.4)
    ax.add_patch(Ellipse((0, H), 2 * R, 2 * ry, fc=shade(C_BLUE, 1.12), ec=INK, lw=1.4))
    ax.plot([0, R], [H, H], color=C_RED, lw=1.6)
    ax.text(R / 2, H + 0.13, "$r$", color=C_RED, ha="center", fontsize=13)
    ax.plot([0, 0], [-0.7, H + 0.7], color=INK, lw=0.8, ls="-.")
    dim_arrow(ax, (R + 0.5, 0), (R + 0.5, H), "$h$", off_xy=(0.3, 0))
    dim_arrow(ax, (-R, -1.0), (R, -1.0), "$d = 2r$", off_xy=(0, -0.3))
    ax.text(0, -1.9, "$V = S_{\\rm осн}\\,h = \\pi r^2 h = \\dfrac{\\pi d^2}{4}\\,h$", ha="center", fontsize=12)
    ax.set_xlim(-2.4, 3.0)
    ax.set_ylim(-2.5, 3.6)
    ax.set_title("Цилиндр")
    off(ax)
    fig.tight_layout()
    save(fig, "volume-cuboid-cylinder-layers.png")


# 10. sphere and V(d) --------------------------------------------------
def fig_volume_sphere():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
    R = 1.6
    ax.add_patch(Circle((0, 0), R, fc=C_BLUE, ec=INK, lw=1.5, alpha=0.6))
    ax.add_patch(Ellipse((0, 0), 2 * R, 0.7, fc="none", ec=INK, lw=0.9, ls="--"))
    ax.add_patch(Wedge((0, 0), R, 180, 360, width=0.0, fc="none"))
    t = np.linspace(np.pi, 2 * np.pi, 60)
    ax.plot(R * np.cos(t), 0.35 * np.sin(t) * 1.0, color=INK, lw=1.6)
    ax.plot([0, R], [0, 0], color=C_RED, lw=1.6)
    ax.plot([0], [0], "o", color=INK, ms=3)
    ax.text(R / 2, 0.5, "$r$", color=C_RED, ha="center", fontsize=13)
    dim_arrow(ax, (-R, -R - 0.45), (R, -R - 0.45), "$d = 2r$", off_xy=(0, -0.3))
    ax.text(0, -R - 1.35, "$V = \\dfrac{4}{3}\\,\\pi r^3 = \\dfrac{\\pi}{6}\\,d^3$", ha="center", fontsize=13)
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-3.6, 2.2)
    ax.set_title("Шар")
    off(ax)

    d = np.linspace(0, 10, 100)
    ax2.plot(d, d ** 3, color=C_RED, lw=2.4, label="куб с ребром $d$: $V = d^3$")
    ax2.plot(d, np.pi / 6 * d ** 3, color=C_BLUE_D, lw=2.4, label="шар диаметра $d$: $V = \\frac{\\pi}{6}\\,d^3$")
    ax2.plot([10, 10], [np.pi / 6 * 1000, 1000], color=C_RED, lw=1.3, ls="--")
    ax2.text(9.8, 750, "шар занимает\n$\\pi/6 \\approx 52\\,\\%$ куба", color=C_RED, ha="right", fontsize=10)
    ax2.set_xlim(0, 10.6)
    ax2.set_ylim(0, 1080)
    ax2.set_xlabel("$d$, см")
    ax2.set_ylabel("$V$, см$^3$")
    ax2.set_title("Объём растёт как куб размера")
    ax2.grid(color=GRID, lw=0.8)
    ax2.set_axisbelow(True)
    ax2.legend(loc="upper left", fontsize=10, frameon=False)
    fig.tight_layout()
    save(fig, "volume-sphere-vs-cube.png")


# graduated cylinder helper ---------------------------------------------
def draw_cylinder(ax, x0, w, vmax, water, ymax_pad=0.0, label_every=100, tick_every=10, bottom=0.0):
    """Cylinder in scale units: y is millilitres."""
    ax.add_patch(Rectangle((x0, bottom), w, water - bottom, fc=C_WATER, ec="none", alpha=0.85, zorder=1))
    ax.plot([x0, x0, x0 + w, x0 + w], [vmax + 15, bottom, bottom, vmax + 15], color=INK, lw=2, zorder=3)
    for v in range(int(bottom), vmax + 1, tick_every):
        big = v % label_every == 0
        ax.plot([x0 + w, x0 + w - (w * (0.35 if big else 0.2))], [v, v], color=INK, lw=1.1 if big else 0.7, zorder=3)
        if big:
            ax.text(x0 + w + 6, v, str(v), va="center", fontsize=9)
    ax.plot([x0 - 8, x0 + w + 8], [bottom, bottom], color=INK, lw=3)


# 11. immersion in graduated cylinder ------------------------------------
def fig_displacement():
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    vmax = 500
    w = 55
    x1, x2 = 40, 200
    draw_cylinder(ax, x1, w, vmax, 335)
    draw_cylinder(ax, x2, w, vmax, 410)
    # thread and bottle on the left
    ax.plot([x1 + w / 2, x1 + w / 2], [455, 520], color=INK, lw=1.2, zorder=4)
    ax.add_patch(Rectangle((x1 + w / 2 - 12, 400), 24, 55, fc=C_ORANGE, ec=INK, lw=1.3, zorder=4))
    ax.add_patch(Rectangle((x1 + w / 2 - 5, 455), 10, 10, fc=C_ORANGE, ec=INK, lw=1.3, zorder=4))
    ax.annotate("тело $V = ?$", (x1 + w / 2 + 12, 430), (x1 + w + 45, 470), fontsize=11, arrowprops=dict(arrowstyle="->", lw=1))
    # body in the right cylinder
    ax.plot([x2 + w / 2, x2 + w / 2], [370, 520], color=INK, lw=1.2, zorder=4)
    ax.add_patch(Rectangle((x2 + w / 2 - 12, 315), 24, 55, fc=C_ORANGE, ec=INK, lw=1.3, zorder=4))
    ax.add_patch(Rectangle((x2 + w / 2 - 5, 370), 10, 10, fc=C_ORANGE, ec=INK, lw=1.3, zorder=4))
    # levels
    ax.plot([x1 - 12, x2 + w + 30], [335, 335], color=C_BLUE_D, lw=1.1, ls="--", zorder=2)
    ax.plot([x2 - 12, x2 + w + 30], [410, 410], color=C_BLUE_D, lw=1.1, ls="--", zorder=2)
    ax.annotate("", (x2 + w + 42, 410), (x2 + w + 42, 335), arrowprops=dict(arrowstyle="<->", color=C_RED, lw=1.4))
    ax.text(x2 + w + 52, 372, "$V = V_2 - V_1$\n$= 410 - 335$\n$= 75$ мл\n$= 75$ см$^3$", color=C_RED, va="center", fontsize=12)
    ax.text(x1 + w / 2, -18, "$V_1 = 335$ мл", ha="center", va="top", fontsize=11, color=C_BLUE_D)
    ax.text(x2 + w / 2, -18, "$V_2 = 410$ мл $= V + V_1$", ha="center", va="top", fontsize=11, color=C_BLUE_D)
    ax.set_xlim(0, 480)
    ax.set_ylim(-70, 545)
    ax.axis("off")
    save(fig, "volume-displacement-cylinder.png")


# 12. meniscus -----------------------------------------------------------
def fig_meniscus():
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    W = 10
    x = np.linspace(0, W, 200)
    level = 77.0
    edge = 1.0
    y = level + edge * (1 - np.sin(np.pi * x / W) ** 0.6)
    ax.fill_between(x, 68, y, color=C_WATER, alpha=0.85)
    ax.plot(x, y, color=C_BLUE_D, lw=2)
    ax.plot([0, 0], [68, 84], color=INK, lw=2.2)
    ax.plot([W, W], [68, 84], color=INK, lw=2.2)
    for v in np.arange(69, 84):
        big = v % 5 == 0
        ax.plot([W, W - (1.8 if big else 1.0)], [v, v], color=INK, lw=1.3 if big else 0.8)
    for v in (70, 75, 80):
        ax.text(W + 0.3, v, str(v), va="center", fontsize=11)
    ax.plot([0, W + 0.3], [level, level], color=C_GREEN, lw=1.4, ls="--")
    ax.annotate("нижний край мениска:\nчитаем $77$ мл", (W / 2, level), (W / 2 + 0.6, 71.4),
                fontsize=11, color=C_GREEN, ha="center", arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.3))
    ax.plot([0, W + 0.3], [level + edge * 0.98, level + edge * 0.98], color=C_RED, lw=1.2, ls=":")
    ax.text(0.4, 82.7, "по краям: ошибка вверх", color=C_RED, fontsize=10)
    ax.text(-0.5, level, "глаз на\nуровне", ha="right", va="center", fontsize=10, color=C_GREEN)
    ax.set_xlim(-3.4, W + 2)
    ax.set_ylim(67, 85.5)
    ax.set_title("Мениск воды: цена деления 1 мл")
    ax.axis("off")
    save(fig, "volume-meniscus-reading.png")


# 13. overflow vessel ----------------------------------------------------
def draw_overflow(ax, x0, water_y, body=None, drops=False, spill=0.0):
    W, H, spout_y = 3.0, 4.0, 3.0
    ax.add_patch(Rectangle((x0, 0), W, water_y, fc=C_WATER, ec="none", alpha=0.85))
    ax.plot([x0, x0, x0 + W], [H, 0, 0], color=INK, lw=2)
    ax.plot([x0 + W, x0 + W], [0, spout_y], color=INK, lw=2)
    ax.plot([x0 + W, x0 + W + 1.0], [spout_y, spout_y - 0.35], color=INK, lw=2)
    ax.plot([x0 + W, x0 + W], [spout_y, H], color=INK, lw=2, alpha=0.0)
    ax.plot([x0 + W, x0 + W + 0.05], [H, H], color=INK, lw=2, alpha=0.0)
    if body is not None:
        bx, by, bw, bh = body
        ax.plot([bx + bw / 2, bx + bw / 2], [by + bh, H + 0.9], color=INK, lw=1.2)
        ax.add_patch(Rectangle((bx, by), bw, bh, fc=C_ORANGE, ec=INK, lw=1.3, zorder=4))
    return x0 + W + 1.0, spout_y - 0.35


def fig_overflow():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
    spout = 3.0
    titles = ["1. Воду наливают до носика", "2. Тело вытесняет воду", "3. Вылившуюся воду измерили"]
    for ax, ttl in zip(axes, titles):
        ax.set_xlim(-1, 9)
        ax.set_ylim(-1.2, 5.4)
        ax.set_title(ttl, fontsize=11.5)
        off(ax)

    def graduated(ax, x0, level, w=0.9, hmax=3.4):
        ax.add_patch(Rectangle((x0, 0), w, level, fc=C_WATER, ec="none", alpha=0.85))
        ax.plot([x0, x0, x0 + w, x0 + w], [hmax, 0, 0, hmax], color=INK, lw=2)
        for k in range(0, 8):
            ax.plot([x0 + w, x0 + w - 0.25], [k * 0.45, k * 0.45], color=INK, lw=0.8)

    # stage 1
    ax = axes[0]
    xv = 0.5
    draw_overflow(ax, xv, spout)
    graduated(ax, 6.4, 0.0)
    ax.text(xv + 1.5, spout + 0.3, "уровень\nу носика", ha="center", fontsize=9.5, color=C_BLUE_D)
    ax.text(6.85, -0.25, "мерный\nцилиндр", ha="center", va="top", fontsize=9.5)
    # stage 2
    ax = axes[1]
    draw_overflow(ax, xv, spout, body=(xv + 0.9, 1.0, 1.2, 1.5))
    ax.annotate("", (6.9, 2.5), (xv + 4.0, 2.65), arrowprops=dict(arrowstyle="->", lw=1.6, color=C_BLUE_D, connectionstyle="arc3,rad=-0.25"))
    ax.text(xv + 2.8, 3.55, "вода\nвытекает", ha="center", fontsize=9.5, color=C_BLUE_D)
    graduated(ax, 6.4, 1.0)
    # stage 3
    # the body stays in the vessel: taken out, it would leave the level V below the spout
    ax = axes[2]
    draw_overflow(ax, xv, spout, body=(xv + 0.9, 1.0, 1.2, 1.5))
    graduated(ax, 6.4, 1.6)
    ax.plot([5.8, 7.6], [1.6, 1.6], color=C_BLUE_D, lw=1.1, ls="--")
    ax.text(8.0, 1.6, "$V$", color=C_RED, fontsize=14, va="center")
    ax.text(4.5, -0.75, "объём вылившейся воды = объём тела", ha="center", fontsize=10.5, color=C_RED)
    save(fig, "volume-overflow-vessel.png")


# 14. chalk --------------------------------------------------------------
def fig_chalk():
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    dx, dy = 0.35, 0.26
    box3d(ax, 0, 0, 1.1, 1.1, 9.6, dx, dy, tint(WARM, 0.85))
    dim_arrow(ax, (-0.35, 0), (-0.35, 9.6), "$9{,}6$ см", off_xy=(-0.95, 0))
    dim_arrow(ax, (0, -0.45), (1.1, -0.45), "$1{,}1$ см", off_xy=(0, -0.55))
    ax.text(1.1 + 0.4, 0.05, "$1{,}1$ см", fontsize=10, ha="left")
    ax.text(3.6, 7.5, "$V = 1{,}1 \\cdot 1{,}1 \\cdot 9{,}6$ см$^3$", fontsize=12, ha="left")
    ax.text(3.6, 6.4, "$= 11{,}616$ см$^3$", fontsize=12, ha="left")
    ax.text(3.6, 5.3, "две значащие цифры", fontsize=11, ha="left", color=C_RED)
    ax.text(3.6, 4.2, "$V \\approx 12$ см$^3$", fontsize=14, ha="left", color=C_RED)
    ax.set_xlim(-2.4, 8.6)
    ax.set_ylim(-1.6, 10.6)
    off(ax)
    save(fig, "volume-chalk-piece.png")


# 15. lab: cup with marks -----------------------------------------------
R_B, R_T, H_CUP = 2.5, 3.5, 9.5  # model of a disposable cup, cm
KCONE = (R_T - R_B) / H_CUP


def cup_level(v):
    r3 = 3 * KCONE * v / np.pi + R_B ** 3
    return (r3 ** (1 / 3) - R_B) / KCONE


def cup_radius(h):
    return R_B + KCONE * h


def draw_cup(ax, x0, water_v=None, ymax=None):
    hh = np.linspace(0, H_CUP, 50)
    left = x0 - cup_radius(hh)
    right = x0 + cup_radius(hh)
    if water_v:
        hw = cup_level(water_v)
        hs = np.linspace(0, hw, 30)
        ax.fill_betweenx(hs, x0 - cup_radius(hs), x0 + cup_radius(hs), color=C_WATER, alpha=0.85)
    ax.plot(left, hh, color=INK, lw=2)
    ax.plot(right, hh, color=INK, lw=2)
    ax.plot([left[0], right[0]], [0, 0], color=INK, lw=2)
    ax.plot([left[-1], right[-1]], [H_CUP, H_CUP], color=INK, lw=1)


def fig_lab_cup_marks():
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.0))
    stages = [([20], "1. Налили 20 мл,\nотметили $20$"), ([20, 40], "2. Долили 20 мл,\nотметили $40$"),
              ([20, 40, 60, 80, 100, 120, 140], "3. Так до $140$ мл")]
    for ax, (marks, ttl) in zip(axes, stages):
        top = marks[-1]
        draw_cup(ax, 0, water_v=top)
        sx = 4.5
        ax.add_patch(Rectangle((sx, 0), 1.3, H_CUP, fc=tint(WARM, 0.85), ec=INK, lw=1.2))
        for v in marks:
            h = cup_level(v)
            ax.plot([sx, sx + 0.8], [h, h], color=INK, lw=1.6)
            ax.plot([-cup_radius(h), sx], [h, h], color=C_BLUE_D, lw=0.7, ls=":")
            ax.text(sx + 0.95, h, str(v), va="center", fontsize=9.5)
        ax.set_xlim(-4.2, 7.4)
        ax.set_ylim(-1.0, 10.6)
        ax.set_title(ttl, fontsize=11.5)
        off(ax)
    save(fig, "volume-lab-cup-marks.png")


def fig_lab_calibration():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.9), gridspec_kw={"width_ratios": [1, 1.4]})
    draw_cup(ax, 0, water_v=140)
    for v in range(20, 141, 20):
        h = cup_level(v)
        ax.plot([-cup_radius(h), cup_radius(h)], [h, h], color=C_BLUE_D, lw=1)
        ax.text(cup_radius(h) + 0.2, h, "%d мл" % v, va="center", fontsize=9.5)
    ax.set_xlim(-4.2, 7.2)
    ax.set_ylim(-0.6, 10.4)
    ax.set_title("Метки на стенке стакана")
    off(ax)

    edges = [0] + list(range(20, 141, 20))
    gaps = [cup_level(b) - cup_level(a) for a, b in zip(edges[:-1], edges[1:])]
    labels = ["%d–%d" % (a, b) for a, b in zip(edges[:-1], edges[1:])]
    ax2.bar(range(len(gaps)), gaps, color=C_BLUE_D, width=0.6, label="стакан, расширяющийся кверху")
    even = cup_level(140) / len(gaps)
    ax2.axhline(even, color=C_GREY, lw=1.8, ls="--", label="цилиндрический сосуд: все промежутки равны")
    for i, g in enumerate(gaps):
        ax2.text(i, g + 0.02, num(g, 2), ha="center", fontsize=9.5)
    ax2.set_xticks(range(len(gaps)))
    ax2.set_xticklabels(labels)
    ax2.set_xlabel("Между метками, мл")
    ax2.set_ylabel("Расстояние между метками, см")
    ax2.set_ylim(0, 1.25)
    ax2.set_title("Промежутки между метками сужаются")
    ax2.grid(color=GRID, lw=0.8, axis="y")
    ax2.set_axisbelow(True)
    ax2.legend(loc="upper right", frameon=False, fontsize=10)
    fig.tight_layout()
    save(fig, "volume-lab-cup-calibration.png")


# 16. logarithmic axis of sizes ------------------------------------------
def fig_scale_axis():
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.set_xlim(-18, 28.5)
    ax.set_ylim(-4.2, 6.6)
    ax.axis("off")
    ax.plot([-17, 28], [0, 0], color=INK, lw=2.2)
    ax.annotate("", (28.4, 0), (27, 0), arrowprops=dict(arrowstyle="->", lw=2.2, color=INK))
    for e in range(-15, 27, 5):
        ax.plot([e, e], [-0.12, 0.12], color=INK, lw=1.3)
        ax.text(e, -0.35, "$10^{%d}$" % e if e != 0 else "$1$", ha="center", va="top", fontsize=9.5)
    ax.text(28.3, -0.35, "$L$, м", ha="right", va="top", fontsize=10)

    # regions
    regions = [(-17, -9, tint(BLUE, 0.8), "Микромир", "квантовая физика"),
               (-9, 15, tint(GREEN, 0.8), "Макромир", "классическая физика"),
               (15, 28, tint(WARM, 0.7), "Мегамир", "космология")]
    for a, b, col, name, sub in regions:
        ax.add_patch(Rectangle((a, -2.55), b - a, 1.35, fc=col, ec=INK, lw=1))
        ax.text((a + b) / 2, -1.55, name, ha="center", va="center", fontsize=12.5, weight="bold")
        ax.text((a + b) / 2, -2.05, sub, ha="center", va="center", fontsize=10.5)
    ax.plot([-9, -9], [-2.55, 5.0], color=GRID, lw=1, ls="--", zorder=0)
    ax.plot([15, 15], [-2.55, 5.0], color=GRID, lw=1, ls="--", zorder=0)

    # 41 orders bracket
    ax.annotate("", (26, -3.35), (-15, -3.35), arrowprops=dict(arrowstyle="<->", lw=1.4, color=C_RED))
    ax.text(5.5, -3.95, "от $10^{-15}$ до $10^{26}$ м: $26 + 15 = 41$ порядок", ha="center", fontsize=11.5, color=C_RED)

    objs = [
        (-15, "ядро,\nнуклон", 1.5), (-10, "атом\nводорода", 3.3), (-7, "вирус", 1.5), (-5, "клетка", 3.3),
        (0.23, "человек", 1.5), (3.94, "Эверест", 3.3), (7.1, "Земля", 1.5), (9.14, "Солнце", 3.3),
        (15, "Солнечная система\nи окрестности\n(оценка Виктора)", 4.4), (16.6, "ближайшая\nзвезда", 4.0),
        (21, "Млечный Путь", 1.5), (26.1, "Вселенная\n(верхняя оценка)", 3.3),
    ]
    for e, name, hgt in objs:
        ax.plot([e, e], [0, hgt - 0.1], color=C_GREY, lw=1)
        ax.plot([e], [0], "o", color=C_BLUE_D, ms=6, zorder=5)
        # The Solar system and the nearest star stand 1.6 orders apart: their labels part to
        # either side, or the Solar system's stem runs through the star's label
        left, right = name.startswith("Солнечная"), name.startswith("ближайшая")
        x, ha = (e - 1.2, "right") if left else (e + 0.3, "left") if right else (e, "center")
        ax.text(x, hgt, name, ha=ha, va="bottom", fontsize=9.8)
    save(fig, "scale-of-world-log-axis.png")


# 17. size of the universe from c*t -------------------------------------
def fig_universe_size():
    c = 3e8
    year = 365 * 86400
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    t = np.linspace(0, 16, 100)
    R = c * t * 1e9 * year / 1e26
    ax.plot(t, R, color=C_BLUE_D, lw=2.4)
    t0 = 14.0
    R0 = c * t0 * 1e9 * year / 1e26
    ax.plot([t0, t0], [0, R0], color=C_RED, lw=1.2, ls="--")
    ax.plot([0, t0], [R0, R0], color=C_RED, lw=1.2, ls="--")
    ax.plot([t0], [R0], "o", color=C_RED, ms=7)
    ax.text(0.3, R0 + 0.06, "$R \\approx 1{,}3 \\cdot 10^{26}$ м", color=C_RED, fontsize=12)
    ax.text(t0, 0.06, "$t = 14$ млрд лет", color=C_RED, fontsize=10.5, ha="center")
    ax.text(5.3, 0.33, "$R = c\\,t$", color=C_BLUE_D, fontsize=13, rotation=27)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 1.7)
    ax.set_xlabel("Время после взрыва $t$, млрд лет")
    ax.set_ylabel("Путь света $R$, $10^{26}$ м")
    ax.set_title("Оценка размера Вселенной по $R = ct$")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "scale-of-world-universe-size-estimate.png")


# 18. look-back time ------------------------------------------------------
def fig_lookback():
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    d = np.logspace(-6, 10.3, 100)
    ax.loglog(d, d, color=C_BLUE_D, lw=2.4)
    arrow = dict(arrowstyle="-", lw=0.8, color=INK)
    pts = [
        (1.58e-5, "Солнце: 8 минут назад", (2e-4, 3e-6), "left", "center"),
        (4.24, "ближайшая звезда: 4 года назад", (2e1, 1e-3), "left", "center"),
        (2.6e4, "центр Галактики", (1e6, 1e0), "left", "center"),
        (2.5e6, "галактика Андромеды", (1e11, 1e3), "right", "center"),
        (1e9, "$10^9$ световых лет:\nвидим то, что было\n$10^9$ лет назад", (1e11, 1e-1), "right", "top"),
    ]
    for x, name, xy_text, ha, va in pts:
        ax.plot([x], [x], "o", color=C_RED, ms=7, zorder=5)
        ax.annotate(name, (x, x), xy_text, fontsize=9.5, ha=ha, va=va, arrowprops=arrow)
    ax.plot([1.4e10], [1.4e10], "o", color=C_RED, ms=7, zorder=5)
    ax.set_xlabel("Расстояние до объекта, световые годы")
    ax.set_ylabel("Насколько давнее прошлое мы видим, лет")
    ax.set_title("Телескоп показывает прошлое")
    ax.grid(color=GRID, lw=0.8, which="major")
    ax.set_axisbelow(True)
    ax.set_xlim(1e-6, 1e11)
    ax.set_ylim(1e-6, 1e11)
    save(fig, "scale-of-world-look-back.png")


if __name__ == "__main__":
    fig_area_formulas()
    fig_triangle_half()
    fig_pi_ratio()
    fig_palette_blob()
    fig_palette_triangle()
    fig_palette_refinement()
    fig_cd_ring()
    fig_volume_cubes()
    fig_volume_layers()
    fig_volume_sphere()
    fig_displacement()
    fig_meniscus()
    fig_overflow()
    fig_chalk()
    fig_lab_cup_marks()
    fig_lab_calibration()
    fig_scale_axis()
    fig_universe_size()
    fig_lookback()
