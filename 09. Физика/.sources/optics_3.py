"""Figures for the notes "Глаз. Цветовосприятие" and "Дисперсия света" (section f14, lessons 215, 216, 219).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 optics_3.py [name ...]
PNG files go to content/14. Оптика/00. Вложения/ (prefixes eye-, dispersion-)

Every ray path comes from the vector form of Snell's law (refract) or from the thin lens equation,
and each figure asserts the numbers it prints. Values of n that the lecturer does not give are
reference numbers and are marked on the figure as "не из лекции".
"""
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, Polygon, Rectangle

from course import COURSE

OUT = COURSE / "content" / "14. Оптика" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
RAY = GREEN  # every ray of light
RAY2 = RED  # a second ray in a figure that already has a green one
GREY = tint(INK, 0.4)  # small notes and secondary text
GLASS = tint(SKY, 0.8)  # glass, a lens, the water of a drop
LENS = BLUE  # the outline of a lens, as in optics_lens.py
EYEFILL = tint(WARM, 0.85)
CORNEA = BLUE
RETINA = RED
IRIS = COPPER
NERVE = WARM
WHITE_LIGHT = tint(INK, 0.2)  # the ray of white light
# the colour of a light is data here: a spectrum, a mixing disc, a filter. The primaries and the secondaries
# are the pure RGB and CMY triples, and a wavelength gets its colour from wavelength_rgb below
RGB_R, RGB_G, RGB_B = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
CMY_Y, CMY_M, CMY_C = (1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def canvas(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def rad(d):
    return math.radians(d)


def deg(r):
    return math.degrees(r)


def vec(theta):
    return np.array([math.cos(rad(theta)), math.sin(rad(theta))])


def ang(v):
    return deg(math.atan2(v[1], v[0]))


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def refract(d, nrm, n1, n2):
    """Vector Snell's law; nrm is a unit normal pointing against d."""
    c = -float(np.dot(nrm, d))
    r = n1 / n2
    k = 1 - r * r * (1 - c * c)
    if k < 0:
        return None
    return r * d + (r * c - math.sqrt(k)) * nrm


def reflect(d, nrm):
    return d - 2 * float(np.dot(d, nrm)) * nrm


def ray(ax, p, q, color=RAY, lw=1.8, f=0.55, arrow=True, ls="-", z=3, alpha=1.0):
    p, q = np.asarray(p, float), np.asarray(q, float)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round", alpha=alpha)
    if arrow:
        a = p + (q - p) * (f - 0.012)
        b = p + (q - p) * f
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=13, alpha=alpha), zorder=z)


def text(ax, x, y, s, size=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=8, **kw)


def lens_shape(ax, x, h, kind, w=0.11, color=LENS, lw=2.2, fc=GLASS, angle=0.0, cy=0.0):
    """Thin lens outline centred at (x, cy) with half-height h; angle rotates it about that centre."""
    t = np.linspace(-1, 1, 60)
    y = h * t + cy
    if kind == "conv":
        half = w * (1 - t**2)
        left, right = x - half, x + half
    elif kind == "plano_right":  # convex on the left, flat on the right (plano-convex half of a lens)
        left, right = x - 2 * w * (1 - t**2), x + 0 * t
    elif kind == "plano_left":  # flat on the left, convex on the right
        left, right = x + 0 * t, x + 2 * w * (1 - t**2)
    else:
        half = w * (0.25 + 0.75 * t**2)
        left, right = x - half, x + half
    xs = np.concatenate([left, right[::-1]])
    ys = np.concatenate([y, y[::-1]])
    pts = np.stack([xs, ys], axis=1)
    if angle:
        c = np.array([x, cy])
        a = rad(angle)
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        pts = (pts - c) @ R.T + c
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=color, lw=lw, zorder=4))


def wavelength_rgb(wl):
    """Approximate RGB of a spectral colour (Bruton), wl in nm."""
    if 380 <= wl < 440:
        r, g, b = -(wl - 440) / 60, 0.0, 1.0
    elif 440 <= wl < 490:
        r, g, b = 0.0, (wl - 440) / 50, 1.0
    elif 490 <= wl < 510:
        r, g, b = 0.0, 1.0, -(wl - 510) / 20
    elif 510 <= wl < 580:
        r, g, b = (wl - 510) / 70, 1.0, 0.0
    elif 580 <= wl < 645:
        r, g, b = 1.0, -(wl - 645) / 65, 0.0
    elif 645 <= wl <= 780:
        r, g, b = 1.0, 0.0, 0.0
    else:
        r = g = b = 0.0
    if 380 <= wl < 420:
        f = 0.3 + 0.7 * (wl - 380) / 40
    elif 700 < wl <= 780:
        f = 0.3 + 0.7 * (780 - wl) / 80
    else:
        f = 1.0
    return tuple(round(max(0, c * f) ** 0.8, 4) for c in (r, g, b))


# ---------------------------------------------------------------------------------------------
# eye
# ---------------------------------------------------------------------------------------------

EX_C = np.array([1.2, 0.0])  # eyeball centre
ER = 1.2  # eyeball radius, retina at x = 2.4
XL = 0.55  # thin lens of the eye
XR = EX_C[0] + ER  # retina on the axis
LR = XR - XL  # lens-to-retina distance
RY = 0.3  # height of the drawn rays at the eye lens, inside the pupil


def circle_hit(p, d):
    """Forward intersection of the ray p + t d with the eyeball circle (t > 0, the far root)."""
    f = p - EX_C
    b = float(np.dot(f, d))
    c = float(np.dot(f, f)) - ER**2
    disc = b * b - c
    t = -b + math.sqrt(disc)
    return p + d * t


def draw_eye(ax, lens_w=0.12, nerve=True, fill=True):
    # cornea: circle through the ends of the sclera arc with its leftmost point at x = -0.05
    e = EX_C + ER * np.array([math.cos(rad(140)), math.sin(rad(140))])
    left = -0.05
    r_c = ((e[0] - left) ** 2 + e[1] ** 2) / (2 * (e[0] - left))
    c_c = left + r_c
    a0 = deg(math.atan2(e[1], e[0] - c_c))
    if fill:
        # the fill follows the outline: the eyeball circle plus the cornea bulge in front of it
        ax.add_patch(Circle(EX_C, ER, fc=EYEFILL, ec="none", zorder=0))
        ang = np.radians(np.linspace(a0, 360 - a0, 120))
        bulge = list(zip(c_c + r_c * np.cos(ang), r_c * np.sin(ang)))
        ax.add_patch(Polygon(bulge, closed=True, fc=EYEFILL, ec="none", zorder=0))
    ax.add_patch(Arc(EX_C, 2 * ER, 2 * ER, theta1=-140, theta2=140, color=INK, lw=2.4, zorder=2))
    ax.add_patch(Arc((c_c, 0), 2 * r_c, 2 * r_c, theta1=a0, theta2=360 - a0, color=CORNEA, lw=2.4, zorder=2))
    # retina
    ax.add_patch(Arc(EX_C, 2 * ER, 2 * ER, theta1=-62, theta2=62, color=RETINA, lw=5, zorder=3))
    # iris with the pupil
    for s in (1, -1):
        ax.plot([e[0] + 0.02, XL - 0.14], [s * 0.77, s * 0.40], color=IRIS, lw=4, solid_capstyle="round", zorder=3)
    # lens of the eye
    ax.add_patch(Ellipse((XL, 0), 2 * lens_w, 1.0, fc=GLASS, ec=LENS, lw=2.2, zorder=4))
    if nerve:
        ax.plot([XR - 0.05, XR + 0.85], [-0.42, -0.7], color=NERVE, lw=9, solid_capstyle="round", zorder=1)
    return e


@fig("eye-structure")
def _():
    f, ax = canvas(9.4, 5.6, (-2.6, 4.6), (-1.75, 1.85))
    draw_eye(ax)
    lab = dict(size=11.5, color=INK)

    def leader(xy, xt, s, ha="right", dy=0.0):
        ax.annotate("", xy=xy, xytext=(xt, xy[1] + dy), arrowprops=dict(arrowstyle="-", color=GREY, lw=1.1, shrinkA=2, shrinkB=0), zorder=6)
        text(ax, xt + (-0.06 if ha == "right" else 0.06), xy[1] + dy, s, ha=ha, **lab)

    leader((-0.04, 0.22), -0.95, "роговица", dy=0.75)
    leader((0.30, 0.0), -0.95, "передняя камера\nс водянистой влагой", dy=-0.45)
    leader((0.33, 0.52), -0.95, "радужная оболочка", dy=1.0)
    leader((0.40, 0.03), -0.95, "зрачок", dy=0.22)
    leader((XL, 0.44), 0.95, "хрусталик", ha="left", dy=1.22)
    leader((1.55, -0.2), 1.2, "стекловидное тело", ha="left", dy=-1.15)
    leader((2.33, 0.45), 3.1, "сетчатка", ha="left", dy=0.75)
    leader((XR + 0.55, -0.6), 3.35, "зрительный нерв", ha="left", dy=-0.45)
    f.tight_layout()
    save(f, "eye-structure")


@fig("eye-image-inverted")
def _():
    s, h = 3.0, RY
    f, ax = canvas(10.4, 4.4, (-3.4, 3.6), (-1.6, 1.6))
    draw_eye(ax, nerve=False)
    ax.annotate("", xy=(XL - s, h), xytext=(XL - s, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=3, mutation_scale=18), zorder=5)
    text(ax, XL - s, -0.22, "предмет", size=11, color=INK)
    # chief ray through the optical centre and the ray parallel to the axis
    d = np.array([s, -h])
    d = d / np.linalg.norm(d)
    top = np.array([XL - s, h])
    hit = circle_hit(np.array([XL, 0.0]), d)
    img_y = hit[1]
    assert abs(img_y - (-h * (hit[0] - XL) / s)) < 1e-9
    ray(ax, top, np.array([XL, 0.0]), color=RAY, f=0.6)
    ray(ax, np.array([XL, 0.0]), hit, color=RAY, f=0.6)
    # parallel ray: hits the lens at height h and goes to the same image point
    ray(ax, top, np.array([XL, h]), color=RAY2, f=0.6)
    ray(ax, np.array([XL, h]), hit, color=RAY2, f=0.6)
    ax.plot([XL - s - 0.3, 3.3], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    ax.annotate("", xy=(hit[0] + 0.03, img_y), xytext=(hit[0] + 0.03, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=3, mutation_scale=14, shrinkA=0, shrinkB=0), zorder=6)
    text(ax, hit[0] + 0.45, img_y - 0.14, "изображение:\nдействительное,\nперевёрнутое,\nуменьшенное", size=10.5, color=RETINA, ha="left")
    f.tight_layout()
    save(f, "eye-image-inverted")


@fig("eye-accommodation")
def _():
    f, axs = plt.subplots(1, 2, figsize=(11.4, 4.3))
    cases = [
        ("далёкий предмет: хрусталик тоньше", None, 0.085),
        ("близкий предмет: хрусталик толще", 3.0, 0.2),
    ]
    results = []
    for ax, (ttl, s, w) in zip(axs, cases):
        ax.set_xlim(-3.9, 3.0)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(ttl, fontsize=11.5, pad=4)
        draw_eye(ax, lens_w=w, nerve=False)
        ax.plot([-3.7, 2.8], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
        img = np.array([XR, 0.0])
        for y in (RY, -RY):
            P = np.array([XL, y])
            if s is None:
                src = np.array([-3.6, y])
            else:
                # rays from an on-axis point at distance s from the lens
                src = np.array([XL - s, 0.0])
            ray(ax, src, P, color=RAY, f=0.55)
            ray(ax, P, img, color=RAY, f=0.6)
        if s is None:
            f_eye = LR
            text(ax, -3.0, -0.75, "параллельный пучок:\nизображение в фокусе", size=10, color=GREY)
        else:
            f_eye = 1 / (1 / s + 1 / LR)
            ax.plot([XL - s], [0], "o", color=INK, ms=6, zorder=5)
            text(ax, XL - s, -0.3, "предмет", size=10, color=INK)
        text(ax, 1.25, 1.42, f"$F$ глаза = {num(f_eye, 2)} отн. ед.", size=10, color=GREY) if False else None
        results.append(f_eye)
    assert abs(results[0] - LR) < 1e-12 and results[1] < results[0]
    f.tight_layout()
    save(f, "eye-accommodation")


def myopia_params(f_eye, x_c=-0.95):
    """Virtual source distance s and focal length of the correcting lens for a point at infinity."""
    inv = 1 / f_eye - 1 / LR
    s = 1 / inv
    F_corr = -(s - (XL - x_c))
    return s, F_corr


@fig("eye-myopia")
def _():
    f_eye = 1.25
    x_c = -0.95
    s, F_corr = myopia_params(f_eye, x_c)
    assert F_corr < 0 and f_eye < LR
    f, axs = plt.subplots(2, 1, figsize=(8.8, 7.6))
    for ax in axs:
        ax.set_xlim(-2.0, 3.4)
        ax.set_ylim(-1.45, 1.45)
        ax.set_aspect("equal")
        ax.axis("off")
    # (a) uncorrected
    ax = axs[0]
    ax.set_title("близорукий глаз: изображение бесконечно далёкой точки — перед сетчаткой", fontsize=11, pad=4)
    draw_eye(ax, lens_w=0.17, nerve=False)
    F = np.array([XL + f_eye, 0.0])
    ys = []
    for y in (RY, -RY):
        P = np.array([XL, y])
        ray(ax, np.array([-1.8, y]), P, color=RAY, f=0.5)
        d = (F - P) / np.linalg.norm(F - P)
        hit = circle_hit(P, d)
        ray(ax, P, hit, color=RAY, f=0.35)
        ys.append(hit[1])
    ax.plot([-1.9, 3.2], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    ax.plot([F[0]], [0], "o", color=INK, ms=5, zorder=6)
    text(ax, F[0], -0.2, "фокус\nглаза", size=9.5, color=INK, va="top")
    ax.plot([XR - 0.02] * 2, [ys[1], ys[0]], color=INK, lw=3.4, zorder=7, solid_capstyle="butt")
    text(ax, 2.95, 0.95, "кружок\nнерезкости", size=10, color=INK)
    ax.annotate("", xy=(XR + 0.02, ys[0]), xytext=(2.8, 0.7), arrowprops=dict(arrowstyle="-", color=GREY, lw=1), zorder=6)
    # (b) corrected
    ax = axs[1]
    ax.set_title("исправление: рассеивающая линза перед глазом", fontsize=11, pad=4)
    draw_eye(ax, lens_w=0.17, nerve=False)
    lens_shape(ax, x_c, 0.85, "div", w=0.11)
    ax.plot([-1.9, 3.2], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    V = np.array([XL - s, 0.0])
    img = np.array([XR, 0.0])
    # The diverged rays must reach the eye lens at height RY (inside the pupil, behind the iris edge),
    # so the incoming rays start lower: the height scales with the distances from the virtual source
    y_in = RY * (x_c - V[0]) / (XL - V[0])
    for y in (y_in, -y_in):
        Pc = np.array([x_c, y])
        ray(ax, np.array([-1.8, y]), Pc, color=RAY, f=0.5)
        d = (Pc - V) / np.linalg.norm(Pc - V)
        # check: the diverging ray hits the eye lens, which sends it to the retina point
        t = (XL - x_c) / d[0]
        Pe = Pc + d * t
        ray(ax, Pc, Pe, color=RAY, f=0.5)
        ray(ax, Pe, img, color=RAY, f=0.6)
        assert abs(abs(Pe[1]) - RY) < 1e-9
        # thin lens equation of the eye: object at V, image at the retina
        assert abs(1 / (XL - V[0]) + 1 / LR - 1 / f_eye) < 1e-9
    text(ax, x_c, 1.05, "$F<0$", size=11, color=LENS)
    ax.plot([XR], [0], "o", color=INK, ms=5, zorder=6)
    f.tight_layout()
    save(f, "eye-myopia")


@fig("eye-hyperopia")
def _():
    f_eye = 3.0
    x_c = -0.95
    assert f_eye > LR
    u = 1 / (1 / LR - 1 / f_eye)  # distance from the eye lens to the virtual point behind it
    V = np.array([XL + u, 0.0])
    F1 = V[0] - x_c
    f, axs = plt.subplots(2, 1, figsize=(8.8, 7.6))
    for ax in axs:
        ax.set_xlim(-2.0, 3.6)
        ax.set_ylim(-1.45, 1.45)
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axs[0]
    ax.set_title("дальнозоркий глаз: изображение точки — за сетчаткой", fontsize=11, pad=4)
    draw_eye(ax, lens_w=0.09, nerve=False)
    F = np.array([XL + f_eye, 0.0])
    ys = []
    for y in (RY, -RY):
        P = np.array([XL, y])
        ray(ax, np.array([-1.8, y]), P, color=RAY, f=0.5)
        d = (F - P) / np.linalg.norm(F - P)
        hit = circle_hit(P, d)
        ray(ax, P, hit, color=RAY, f=0.4)
        ray(ax, hit, F, color=RAY, ls="--", lw=1.4, arrow=False)
        ys.append(hit[1])
    ax.plot([-1.9, 3.4], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    ax.plot([F[0]], [0], "o", color=INK, ms=5, zorder=6)
    text(ax, F[0] + 0.05, -0.22, "фокус\nглаза", size=9.5, color=INK, va="top")
    ax.plot([XR - 0.02] * 2, [ys[1], ys[0]], color=INK, lw=3.4, zorder=7, solid_capstyle="butt")
    text(ax, 2.95, 0.95, "кружок\nнерезкости", size=10, color=INK)
    ax.annotate("", xy=(XR + 0.02, ys[0]), xytext=(2.8, 0.7), arrowprops=dict(arrowstyle="-", color=GREY, lw=1), zorder=6)
    ax = axs[1]
    ax.set_title("исправление: собирающая линза помогает хрусталику", fontsize=11, pad=4)
    draw_eye(ax, lens_w=0.09, nerve=False)
    lens_shape(ax, x_c, 0.85, "conv", w=0.14)
    ax.plot([-1.9, 3.4], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    img = np.array([XR, 0.0])
    for y in (RY, -RY):
        Pc = np.array([x_c, y])
        ray(ax, np.array([-1.8, y]), Pc, color=RAY, f=0.5)
        d = (V - Pc) / np.linalg.norm(V - Pc)
        t = (XL - x_c) / d[0]
        Pe = Pc + d * t
        ray(ax, Pc, Pe, color=RAY, f=0.5)
        ray(ax, Pe, img, color=RAY, f=0.6)
    assert abs(1 / (-u) + 1 / LR - 1 / f_eye) < 1e-9
    text(ax, x_c, 1.05, "$F>0$", size=11, color=LENS)
    ax.plot([XR], [0], "o", color=INK, ms=5, zorder=6)
    assert F1 > 0
    f.tight_layout()
    save(f, "eye-hyperopia")


# ---------------------------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------------------------


def disc_image(centers, r, colors, mode, n=700, ext=1.75):
    xs = np.linspace(-ext, ext, n)
    X, Y = np.meshgrid(xs, xs)
    if mode == "add":
        img = np.zeros((n, n, 3))
    else:
        img = np.ones((n, n, 3))
    for (cx, cy), col in zip(centers, colors):
        m = (X - cx) ** 2 + (Y - cy) ** 2 <= r * r
        if mode == "add":
            img[m] = np.clip(img[m] + np.array(col), 0, 1)
        else:
            img[m] = img[m] * np.array(col)
    return img


TRI = [(-0.52, 0.30), (0.52, 0.30), (0.0, -0.6)]


@fig("eye-additive")
def _():
    img = disc_image(TRI, 0.95, [(1, 0, 0), (0, 1, 0), (0, 0, 1)], "add")
    # the three overlaps and the centre follow from the sums R+G, R+B, G+B, R+G+B
    f, ax = plt.subplots(figsize=(5.6, 5.4))
    ax.imshow(img, extent=(-1.75, 1.75, -1.75, 1.75), origin="lower")
    ax.axis("off")
    ax.set_title("Аддитивный способ: свет складывается", fontsize=12, pad=6)
    t = dict(ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(-1.0, 0.85, "R", color=PAPER, **t)
    ax.text(1.0, 0.85, "G", color=PAPER, **t)
    ax.text(0.0, -1.35, "B", color=PAPER, **t)
    ax.text(0.0, 0.62, "Y\nжёлтый", color=INK, **{**t, "fontsize": 10})
    ax.text(-0.72, -0.42, "M\nпурпурный", color=INK, **{**t, "fontsize": 9.5})
    ax.text(0.72, -0.42, "C\nголубой", color=INK, **{**t, "fontsize": 10})
    ax.text(0.0, -0.02, "W\nбелый", color=INK, **{**t, "fontsize": 10})
    f.tight_layout()
    save(f, "eye-additive")


@fig("eye-subtractive")
def _():
    img = disc_image(TRI, 0.95, [(1, 1, 0), (1, 0, 1), (0, 1, 1)], "sub")
    f, ax = plt.subplots(figsize=(5.6, 5.4))
    ax.imshow(img, extent=(-1.75, 1.75, -1.75, 1.75), origin="lower")
    ax.axis("off")
    ax.set_title("Субтрактивный способ: свет вычитается", fontsize=12, pad=6)
    t = dict(ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(-1.0, 0.85, "Y\nжёлтый", color=INK, **{**t, "fontsize": 10})
    ax.text(1.0, 0.85, "M\nпурпурный", color=INK, **{**t, "fontsize": 10})
    ax.text(0.0, -1.35, "C\nголубой", color=INK, **{**t, "fontsize": 10})
    ax.text(0.0, 0.62, "R", color=PAPER, **t)
    ax.text(-0.72, -0.42, "G", color=PAPER, **t)
    ax.text(0.72, -0.42, "B", color=PAPER, **t)
    ax.text(0.0, -0.02, "чёрный", color=PAPER, **{**t, "fontsize": 9})
    f.tight_layout()
    save(f, "eye-subtractive")


@fig("eye-filter-chains")
def _():
    RGB = {"R": RGB_R, "G": RGB_G, "B": RGB_B}
    FILT = {"Y": (CMY_Y, "жёлтый", "B"), "M": (CMY_M, "пурпурный", "G"), "C": (CMY_C, "голубой", "R")}
    chains = [("Y", "C", "G"), ("Y", "M", "R"), ("C", "M", "B")]
    f, ax = plt.subplots(figsize=(10.6, 5.9))
    ax.set_xlim(-0.6, 9.4)
    ax.set_ylim(-1.2, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")

    def beam(x, y, present):
        for k, c in enumerate("RGB"):
            yy = y + (1 - k) * 0.27
            if c in present:
                ax.add_patch(Circle((x, yy), 0.11, fc=RGB[c], ec="none", zorder=4))
            else:
                ax.add_patch(Circle((x, yy), 0.11, fc="none", ec=GRID, lw=1.2, ls=(0, (2, 2)), zorder=4))

    def filt(x, y, key):
        col, name, cut = FILT[key]
        ax.add_patch(Rectangle((x - 0.16, y - 0.5), 0.32, 1.0, fc=col, ec=INK, lw=1.6, zorder=3))
        text(ax, x, y + 0.72, key, size=12, color=INK)
        text(ax, x, y - 0.7, f"минус ${cut}$", size=9.5, color=GREY)

    rows = []
    for i, (a, b, res) in enumerate(chains):
        y = 3.4 - i * 1.8
        present = set("RGB")
        text(ax, -0.45, y, "W", size=13, color=INK)
        x = 0.4
        beam(x, y, present)
        ax.plot([0.55, 1.75], [y, y], color=GRID, lw=1, zorder=1)
        filt(2.0, y, a)
        present -= {FILT[a][2]}
        beam(3.4, y, present)
        ax.plot([3.55, 4.75], [y, y], color=GRID, lw=1, zorder=1)
        filt(5.0, y, b)
        present -= {FILT[b][2]}
        beam(6.4, y, present)
        ax.plot([6.55, 7.45], [y, y], color=GRID, lw=1, zorder=1)
        assert present == {res}, (a, b, present)
        ax.add_patch(Circle((7.9, y), 0.3, fc=RGB[res], ec="none", zorder=4))
        text(ax, 8.6, y, res, size=13, color=INK)
        rows.append(present)
    f.tight_layout()
    save(f, "eye-filter-chains")


@fig("eye-anaglyph")
def _():
    f, ax = canvas(9.4, 5.6, (-0.4, 9.2), (-0.4, 5.6))
    # screen
    ax.add_patch(Rectangle((2.6, 4.3), 3.2, 1.0, fc=LIGHT, ec=INK, lw=2, zorder=2))
    text(ax, 4.2, 4.8, "экран", size=12)
    # projectors with filters
    for x0, name, col, lab in ((1.6, "Л", RED, "К"), (5.2, "П", GREEN, "З")):
        ax.add_patch(Rectangle((x0, 0.2), 1.4, 0.9, fc=PAPER, ec=INK, lw=2, zorder=2))
        text(ax, x0 + 0.7, -0.15, name, size=13)
        ax.add_patch(Rectangle((x0 + 0.35, 1.6), 0.7, 0.6, fc=col, ec=INK, lw=1.6, zorder=3))
        text(ax, x0 + 0.7, 1.9, lab, size=12, color=PAPER, fontweight="bold")
        ray(ax, (x0 + 0.7, 1.1), (x0 + 0.7, 1.6), color=INK, lw=1.3, f=0.6)
        ray(ax, (x0 + 0.7, 2.2), (4.2 + (-0.5 if name == "Л" else 0.5), 4.3), color=col, lw=1.8, f=0.55)
    text(ax, 2.3, 0.65, "левый\nкадр", size=10, color=GREY)
    text(ax, 5.9, 0.65, "правый\nкадр", size=10, color=GREY)
    # glasses
    ax.add_patch(Rectangle((6.85, 1.85), 1.05, 0.9, fc=RED, ec=INK, lw=2, zorder=3, alpha=0.9))
    ax.add_patch(Rectangle((7.95, 1.85), 1.05, 0.9, fc=GREEN, ec=INK, lw=2, zorder=3, alpha=0.9))
    text(ax, 7.375, 2.3, "К", size=12, color=PAPER, fontweight="bold")
    text(ax, 8.475, 2.3, "З", size=12, color=PAPER, fontweight="bold")
    text(ax, 7.95, 1.5, "очки: левый глаз — красный,\nправый — зелёный", size=10, color=GREY)
    f.tight_layout()
    save(f, "eye-anaglyph")


# ---------------------------------------------------------------------------------------------
# dispersion
# ---------------------------------------------------------------------------------------------


def ru_axis(*axs, y=True):
    """Decimal comma on the tick labels."""
    from matplotlib.ticker import FuncFormatter

    fmt = FuncFormatter(lambda v, _: num(v, None))
    for a in axs:
        if y:
            a.yaxis.set_major_formatter(fmt)


def cauchy(wl_nm, A, B):
    return A + B / (wl_nm / 1000.0) ** 2


# illustrative glass: the dispersion is stronger than in real crown glass so that the fan is visible
GLASS_A, GLASS_B = 1.40, 0.050

SEVEN = [("красный", 700), ("оранжевый", 610), ("жёлтый", 580), ("зелёный", 540), ("голубой", 490), ("синий", 450), ("фиолетовый", 410)]


def prism_hits(phi, n, d0, y_hit_frac, shift=(0.0, 0.0), h=3.0):
    """Path of a ray through an apex-up prism; returns hit points, inner direction, exit direction."""
    s = 2 * h * math.tan(rad(phi / 2))
    Bl = np.array([-s / 2, 0.0]) + shift
    A = np.array([0.0, h]) + shift
    Br = np.array([s / 2, 0.0]) + shift
    nL = np.array([-math.cos(rad(phi / 2)), math.sin(rad(phi / 2))])
    nR = np.array([math.cos(rad(phi / 2)), math.sin(rad(phi / 2))])
    P1 = Bl + y_hit_frac * (A - Bl)
    d1 = refract(d0, nL, 1.0, n)
    # intersection with the right face A -> Br
    e = Br - A
    t = cross(A - P1, e) / cross(d1, e)
    P2 = P1 + d1 * t
    d2 = refract(d1, -nR, n, 1.0)
    return dict(P1=P1, P2=P2, d1=d1, d2=d2, Bl=Bl, A=A, Br=Br, nL=nL, nR=nR)


@fig("dispersion-newton-prism")
def _():
    phi = 60.0
    a1 = 55.0
    d0 = vec(-phi / 2 + a1)
    res = []
    for name, wl in SEVEN:
        n = cauchy(wl, GLASS_A, GLASS_B)
        g = prism_hits(phi, n, d0, 0.42)
        assert g["d2"] is not None
        res.append((name, wl, n, g))
    exits = [ang(g["d2"]) for *_, g in res]
    # the violet ray is deviated most, the red one least
    devs = [ang(d0) - e for e in exits]
    assert all(devs[i] < devs[i + 1] for i in range(len(devs) - 1)), devs
    ns = [r[2] for r in res]
    assert all(ns[i] < ns[i + 1] for i in range(len(ns) - 1))
    # mirror in y (apex down, as on the board) and turn so that the middle exit ray is horizontal
    e_mid = -ang(res[3][3]["d2"])
    rho = rad(-e_mid)
    Rm = np.array([[math.cos(rho), -math.sin(rho)], [math.sin(rho), math.cos(rho)]])

    def T(p):
        return Rm @ np.array([p[0], -p[1]])

    g0 = res[3][3]
    f, ax = canvas(10.4, 5.4, (-5.6, 6.2), (-3.2, 3.6))
    verts = [T(g0["Bl"]), T(g0["A"]), T(g0["Br"])]
    ax.add_patch(Polygon(verts, closed=True, fc=GLASS, ec=INK, lw=2.2, zorder=2))
    P1 = T(g0["P1"])
    inc_dir = Rm @ np.array([d0[0], -d0[1]])
    ray(ax, P1 - inc_dir * 4.4, P1, color=WHITE_LIGHT, lw=2.6, f=0.55)
    text(ax, (P1 - inc_dir * 4.4)[0] + 0.1, (P1 - inc_dir * 4.4)[1] + 0.35, "белый свет", size=11, ha="left")
    X_s = 4.6
    ends = []
    for name, wl, n, g in res:
        col = wavelength_rgb(wl)
        Pa, Pb = T(g["P1"]), T(g["P2"])
        ray(ax, Pa, Pb, color=col, lw=1.6, arrow=False)
        de = Rm @ np.array([g["d2"][0], -g["d2"][1]])
        t = (X_s - Pb[0]) / de[0]
        end = Pb + de * t
        ends.append(end)
        ray(ax, Pb, end, color=col, lw=2.0, f=0.55, arrow=(name == "зелёный"))
    # screen
    ys = [e[1] for e in ends]
    ax.plot([X_s, X_s], [min(ys) - 0.6, max(ys) + 0.6], color=INK, lw=2.6, zorder=5)
    for end, (name, wl) in zip(ends, SEVEN):
        ax.plot([X_s], [end[1]], "o", color=wavelength_rgb(wl), ms=7, zorder=7, mec=INK, mew=0.5)
    mid_y = (ys[0] + ys[-1]) / 2
    ys_lab = np.linspace(mid_y - 1.6, mid_y + 1.6, len(SEVEN)) if ys[0] < ys[-1] else np.linspace(mid_y + 1.6, mid_y - 1.6, len(SEVEN))
    for end, yl, L in zip(ends, ys_lab, "КОЖЗГСФ"):
        ax.plot([X_s + 0.1, X_s + 0.5], [end[1], yl], color=GREY, lw=0.8)
        text(ax, X_s + 0.65, yl, L, size=11, color=INK, ha="left")
    ax.annotate("", xy=(X_s + 1.25, max(ys) + 0.1), xytext=(X_s + 1.25, min(ys) - 0.1), arrowprops=dict(arrowstyle="-", color=GREY, lw=1.4))
    text(ax, X_s + 1.4, (max(ys) + min(ys)) / 2, "спектр", size=12, ha="left")
    text(ax, -5.4, -2.95, "значения $n$ условные: дисперсия на рисунке усилена", size=9.5, color=GREY, ha="left")
    f.tight_layout()
    save(f, "dispersion-newton-prism")


@fig("dispersion-n-lambda")
def _():
    wl = np.linspace(380, 760, 300)
    f, ax = plt.subplots(figsize=(8.4, 4.8))
    crown = cauchy(wl, 1.5046, 0.00420)
    water = cauchy(wl, 1.3235, 0.003286)
    flint = cauchy(wl, 1.60, 0.0100)
    for arr, lab, col in ((flint, "тяжёлое стекло", VIOLET), (crown, "стекло", BLUE), (water, "вода", SKY)):
        ax.plot(wl, arr, lw=2.6, color=col, label=lab)
    lo, hi = 1.27, 1.72
    ax.set_ylim(lo, hi)
    bar = np.array([[wavelength_rgb(w) for w in wl]])
    ax.imshow(bar, extent=(380, 760, lo, lo + 0.03), aspect="auto", origin="lower", zorder=0)
    ax.set_xlim(380, 760)
    ax.set_xlabel(r"длина волны $\lambda$, нм")
    ax.set_ylabel(r"показатель преломления $n$")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="center right", fontsize=10.5)
    ax.set_title("С ростом длины волны показатель преломления убывает", fontsize=11.5, pad=6)
    ax.annotate("$n$ фиолетового — наибольший", xy=(385, flint[0]), xytext=(420, 1.705), fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ax.annotate("$n$ красного — наименьший", xy=(755, flint[-1]), xytext=(700, 1.66), fontsize=10, color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
    ru_axis(ax)
    ax.text(0.99, 0.09, "значения $n$ — справочные, не из лекции", transform=ax.transAxes, fontsize=8.5, color=GREY, ha="right", va="bottom")
    assert crown[0] > crown[-1] and water[0] > water[-1]
    assert abs(cauchy(486.1, 1.5046, 0.00420) - 1.5224) < 2e-3 and abs(cauchy(656.3, 1.5046, 0.00420) - 1.5143) < 2e-3
    f.tight_layout()
    save(f, "dispersion-n-lambda")


@fig("dispersion-spectrum-scale")
def _():
    f, ax = plt.subplots(figsize=(10.4, 2.9))
    wl = np.linspace(330, 810, 600)
    bar = np.array([[wavelength_rgb(w) for w in wl]])
    ax.imshow(bar, extent=(330, 810, 0, 1), aspect="auto", origin="lower")
    ax.add_patch(Rectangle((330, 0), 50, 1, fc=LIGHT, ec="none"))
    ax.add_patch(Rectangle((760, 0), 50, 1, fc=LIGHT, ec="none"))
    ax.set_xlim(330, 810)
    ax.set_ylim(-0.75, 1.75)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([380, 450, 500, 550, 600, 650, 700, 760])
    ax.tick_params(axis="x", length=5, labelsize=10.5)
    ax.set_xlabel(r"длина волны $\lambda$, нм")
    for x in (380, 760):
        ax.plot([x, x], [0, 1.15], color=INK, lw=1.6)
    ax.plot([555, 555], [0, 1.0], color=INK, lw=1.2, ls=(0, (3, 3)))
    ax.text(555, 1.2, "глаз лучше всего\nвидит свет около $555$ нм", ha="center", fontsize=9.5, va="bottom")
    ax.text(355, 0.5, "ультра-\nфиолет", ha="center", va="center", fontsize=9.5)
    ax.text(785, 0.5, "инфра-\nкрасный", ha="center", va="center", fontsize=9.5)
    names = [("фиолетовый", 410), ("синий", 460), ("голубой", 490), ("зелёный", 540), ("жёлтый", 580), ("оранжевый", 615), ("красный", 700)]
    for nm, x in names:
        ax.text(x, -0.22, nm, ha="center", va="top", fontsize=8.6, rotation=0)
    ax.text(570, -0.62, "границы между цветами условны", fontsize=8.5, color=GREY, ha="center", va="top")
    f.tight_layout()
    save(f, "dispersion-spectrum-scale")


@fig("dispersion-half-lens")
def _():
    F = 1.0
    f, axs = plt.subplots(2, 1, figsize=(10.4, 6.4))
    # (a) the whole lens: slit at 2F, image at 2F
    ax = axs[0]
    ax.set_xlim(-2.6, 2.7)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("целая линза: щель на расстоянии $2F$, изображение щели на расстоянии $2F$", fontsize=11, pad=2)
    h = 0.35
    lens_shape(ax, 0, 1.0, "conv", w=0.09)  # the same half-height as the halves below
    ax.plot([-2.5, 2.6], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    ax.plot([-2 * F, -2 * F], [-h, h], color=INK, lw=3.5, zorder=5, solid_capstyle="butt")
    text(ax, -2 * F, -0.6, "щель", size=10.5)
    img_y = -h
    ray(ax, (-2 * F, h), (0, 0), color=RAY, f=0.55)
    ray(ax, (0, 0), (2 * F, img_y), color=RAY, f=0.6)
    ray(ax, (-2 * F, h), (0, h), color=RAY2, f=0.55)
    ray(ax, (0, h), (2 * F, -h), color=RAY2, f=0.6)
    assert abs(((h - 0) / (0 - h)) - (-1)) < 1e-9 and abs(1 / (2 * F) + 1 / (2 * F) - 1 / F) < 1e-12
    ax.plot([2 * F, 2 * F], [-h, h], color=INK, lw=3.5, zorder=5, solid_capstyle="butt")
    text(ax, 2 * F, -0.6, "изображение\nщели", size=10.5)
    for x in (-F, F):
        ax.plot([x], [0], "o", color=INK, ms=3.5, zorder=6)
    # (b) the lens cut in two: power 10 instead of 20 dioptres for each half
    ax = axs[1]
    ax.set_xlim(-2.6, 5.7)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("линза, распиленная пополам: у каждой половинки $F'=2F$, щель в её фокусе", fontsize=11, pad=2)
    fp = 2 * F
    L2 = 3.0
    # the halves of one cut lens: plano-convex, flat sides turned to each other, same half-height 0.8 as the whole lens
    lens_shape(ax, 0, 1.0, "plano_right", w=0.09)
    lens_shape(ax, L2, 1.0, "plano_left", w=0.09)
    ax.plot([-2.5, 5.6], [0, 0], color=GREY, lw=0.9, ls=(0, (5, 4)), zorder=1)
    ax.plot([-fp, -fp], [-h, h], color=INK, lw=3.5, zorder=5, solid_capstyle="butt")
    text(ax, -fp, -0.75, "щель", size=10.5)
    # the beam between the halves slopes down by h/fp, so the outer ray reaches the second half at |y1| + 0.525 < 1.0
    for y1, col in ((0.4, RAY), (0.0, RAY2), (-0.4, RAY)):
        slope_in = (y1 - h) / fp
        slope_mid = slope_in - y1 / fp  # after the first half
        assert abs(slope_mid - (-h / fp)) < 1e-12  # parallel beam
        y2 = y1 + slope_mid * L2
        slope_out = slope_mid - y2 / fp
        y_end = y2 + slope_out * fp
        assert abs(y_end - (-h)) < 1e-12  # same image of the slit, inverted
        ray(ax, (-fp, h), (0, y1), color=col, f=0.55)
        ray(ax, (0, y1), (L2, y2), color=col, f=0.5)
        ray(ax, (L2, y2), (L2 + fp, y_end), color=col, f=0.6)
    ax.plot([L2 + fp, L2 + fp], [-h, h], color=INK, lw=3.5, zorder=5, solid_capstyle="butt")
    text(ax, L2 + fp, 0.7, "изображение\nщели", size=10.5)
    text(ax, L2 / 2, 1.22, "параллельный пучок", size=10.5, color=GREY)
    f.tight_layout()
    save(f, "dispersion-half-lens")


@fig("dispersion-spectrograph")
def _():
    phi, n_cols = 50.0, [("красный", 700), ("зелёный", 540), ("синий", 450)]
    f1, f2 = 2.0, 4.0
    x_l1 = -2.6
    slit_x = x_l1 - f1
    d_beam = np.array([1.0, 0.0])
    hh = 0.55  # half-height of the parallel beam
    base_y, face_h = -1.5, 3.0  # the prism stands on y = -1.5, so the axis ray y = 0 meets its left face
    f, ax = canvas(11.6, 6.4, (-5.1, 7.6), (-5.3, 3.6))

    def hit_frac(y):
        return (y - base_y) / face_h

    # shift the prism sideways so that the axis ray meets the left face at x = -1.4
    g = prism_hits(phi, cauchy(540, GLASS_A, GLASS_B), d_beam, hit_frac(0.0), shift=np.array([0.0, base_y]))
    shift = np.array([-1.4 - g["P1"][0], base_y])
    g = prism_hits(phi, cauchy(540, GLASS_A, GLASS_B), d_beam, hit_frac(0.0), shift=shift)
    ax.add_patch(Polygon([g["Bl"], g["A"], g["Br"]], closed=True, fc=GLASS, ec=INK, lw=2.0, zorder=2))
    # slit, first lens, parallel beam
    ax.plot([slit_x, slit_x], [-0.35, 0.35], color=INK, lw=4, zorder=5, solid_capstyle="butt")
    text(ax, slit_x, -0.75, "щель", size=10.5)
    lens_shape(ax, x_l1, 1.25, "conv", w=0.1)
    ax.plot([slit_x - 0.3, x_l1 + 0.6], [0, 0], color=GREY, lw=0.8, ls=(0, (5, 4)), zorder=1)
    # upper and lower rays of the parallel beam at y = +hh and y = -hh, for each colour
    mids = {}
    for name, wl in n_cols:
        n = cauchy(wl, GLASS_A, GLASS_B)
        rows = []
        for y in (hh, -hh):
            rows.append(prism_hits(phi, n, d_beam, hit_frac(y), shift=shift))
        mids[name] = rows
    e_dirs = {k: ang(v[0]["d2"]) for k, v in mids.items()}
    assert e_dirs["красный"] > e_dirs["зелёный"] > e_dirs["синий"]
    e_m = e_dirs["зелёный"]
    dm = vec(e_m)
    perp = np.array([-dm[1], dm[0]])
    P_mid = mids["зелёный"][0]["P2"] * 0.5 + mids["зелёный"][1]["P2"] * 0.5
    C2 = P_mid + dm * 2.3
    lens_shape(ax, C2[0], 1.25, "conv", w=0.1, angle=e_m, cy=C2[1])
    # the beam before the prism: from the slit through the first lens, then parallel to the axis
    for y, row in ((hh, 0), (-hh, 1)):
        ray(ax, (slit_x, 0.0), (x_l1, y), color=WHITE_LIGHT, lw=1.2, f=0.55)
        ray(ax, (x_l1, y), (mids["зелёный"][row]["P1"][0], y), color=WHITE_LIGHT, lw=1.2, f=0.5)
    # focal plane of the second lens
    foc = C2 + dm * f2
    ax.plot([foc[0] - perp[0] * 1.3, foc[0] + perp[0] * 1.3], [foc[1] - perp[1] * 1.3, foc[1] + perp[1] * 1.3], color=INK, lw=2.4, zorder=5)
    text(ax, foc[0] + 0.15, foc[1] - 1.55, "экран или\nфотопластинка", size=10.5, ha="left", va="center")
    spots = {}
    colmap = {"красный": wavelength_rgb(700), "зелёный": wavelength_rgb(540), "синий": wavelength_rgb(450)}
    for name, rows in mids.items():
        col = colmap[name]
        for r_ in rows:
            ray(ax, r_["P1"], r_["P2"], color=col, lw=1.3, arrow=False)
            de = r_["d2"]
            # hit point on the plane of the second lens
            t = float(np.dot(C2 - r_["P2"], dm)) / float(np.dot(de, dm))
            H = r_["P2"] + de * t
            ray(ax, r_["P2"], H, color=col, lw=1.6, f=0.55)
            delta = rad(ang(de) - e_m)
            spot = foc + perp * f2 * math.tan(delta)
            ray(ax, H, spot, color=col, lw=1.8, f=0.6)
            spots[name] = spot
    # light after the lens hits the plane perpendicular to dm; check the order on the screen
    order = [float(np.dot(spots[k] - foc, perp)) for k in ("красный", "зелёный", "синий")]
    assert order[0] > order[1] > order[2], order
    for name, sp in spots.items():
        ax.plot([sp[0]], [sp[1]], "o", color=colmap[name], ms=8, zorder=7, mec=INK, mew=0.6)
    text(ax, -4.9, 3.2, "щель стоит в фокусе первой линзы, экран — в фокусе второй", size=10, ha="left", color=GREY)
    text(ax, g["A"][0], g["A"][1] + 0.35, "призма", size=10.5)
    f.tight_layout()
    save(f, "dispersion-spectrograph")


@fig("dispersion-line-spectra")
def _():
    f, ax = plt.subplots(figsize=(10.4, 3.6))
    rows = [
        ("H", [410.2, 434.0, 486.1, 656.3]),
        ("Na", [589.0, 589.6]),
    ]
    xs = np.linspace(380, 760, 800)
    for i, (el, lines) in enumerate(rows):
        y0 = 1.0 - i * 1.25
        ax.add_patch(Rectangle((380, y0 - 0.5), 380, 1.0, fc=INK, ec="none", zorder=1))
        for L in lines:
            ax.plot([L, L], [y0 - 0.5, y0 + 0.5], color=wavelength_rgb(L), lw=2.2, zorder=2)
        ax.text(372, y0, el, ha="right", va="center", fontsize=13, fontweight="bold")
    ax.annotate("жёлтый дублет натрия:\n$589{,}0$ и $589{,}6$ нм", xy=(589.3, -0.76), xytext=(640, -1.3), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY, lw=1), ha="left", va="center")
    ax.set_xlim(360, 765)
    ax.set_ylim(-1.7, 1.9)
    ax.spines[["left"]].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([400, 450, 500, 550, 600, 650, 700, 750])
    ax.set_xlabel(r"длина волны $\lambda$, нм")
    ax.text(385, 1.8, "положения линий — справочные, не из лекции", fontsize=8.5, color=GREY, va="top")
    f.tight_layout()
    save(f, "dispersion-line-spectra")


def drop_path(n, b):
    """One internal reflection in a unit water drop; the white ray comes along +x at height b."""
    P1 = np.array([-math.sqrt(1 - b * b), b])
    d0 = np.array([1.0, 0.0])
    d1 = refract(d0, P1, 1.0, n)
    # far root on the unit circle
    bq = float(np.dot(P1, d1))
    t = -2 * bq
    P2 = P1 + d1 * t
    d2 = reflect(d1, P2)
    bq2 = float(np.dot(P2, d2))
    P3 = P2 + d2 * (-2 * bq2)
    d3 = refract(d2, -P3, n, 1.0)
    return P1, P2, P3, d0, d1, d2, d3


@fig("dispersion-rainbow-drop")
def _():
    b = 0.86
    n_r, n_v = 1.3311, 1.3435  # water, 656 and 405 nm: reference values, not from the lecture
    f, ax = canvas(8.8, 7.4, (-2.4, 3.6), (-3.1, 1.6))
    ax.add_patch(Circle((0, 0), 1.0, fc=GLASS, ec=INK, lw=2.2, zorder=1))
    col_r, col_v = wavelength_rgb(700), wavelength_rgb(450)
    P1, _, _, d0, _, _, _ = drop_path(n_r, b)
    ray(ax, P1 - d0 * 1.6, P1, color=WHITE_LIGHT, lw=2.6, f=0.6)
    text(ax, P1[0] - 1.6, b + 0.2, "белый свет", size=11, ha="left")
    angles = {}
    for n, col, nm in ((n_r, col_r, "красный"), (n_v, col_v, "синий")):
        P1, P2, P3, d0, d1, d2, d3 = drop_path(n, b)
        ray(ax, P1, P2, color=col, lw=2.0, f=0.5)
        ray(ax, P2, P3, color=col, lw=2.0, f=0.5)
        ray(ax, P3, P3 + d3 * 2.6, color=col, lw=2.2, f=0.5)
        dev = 180.0 - (ang(d3) - ang(d0) if ang(d3) - ang(d0) > 0 else ang(d3) - ang(d0) + 360)
        back = deg(math.acos(float(np.dot(-d0, d3))))
        angles[nm] = back
        # sanity: deviation D = 180 + 2i - 4r and Descartes angle 180 - D
        i_ = deg(math.asin(b))
        r_ = deg(math.asin(b / n))
        D = 180 + 2 * i_ - 4 * r_
        assert abs((180 - D) - back) < 1e-6, (180 - D, back)
    assert abs(angles["красный"] - 42.4) < 0.1 and abs(angles["синий"] - 40.6) < 0.1
    # angle marks at the point where the ray is turned back: extend the incident line
    for nm, col, rr in (("красный", col_r, 1.2), ("синий", col_v, 0.9)):
        n = n_r if nm == "красный" else n_v
        P1, P2, P3, d0, d1, d2, d3 = drop_path(n, b)
        ray(ax, P3, P3 - d0 * 1.7, color=GREY, lw=1.0, ls=(0, (4, 3)), arrow=False)
        a0 = ang(-d0)
        a1 = ang(d3)
        lo, hi = sorted([a0, a1])
        ax.add_patch(Arc(P3, 2 * rr, 2 * rr, theta1=lo, theta2=hi, color=col, lw=1.6, zorder=6))
        mid = rad((lo + hi) / 2)
        ax.text(P3[0] + (rr + 0.45) * math.cos(mid), P3[1] + (rr + 0.45) * math.sin(mid), f"${num(angles[nm], 1, math=True)}^\\circ$", fontsize=11, color=col, ha="center", va="center")
    text(ax, 2.0, 1.2, "красный отклонён меньше,\nсиний — больше", size=10.5, color=INK, ha="center")
    text(ax, 0.6, -3.0, "$n$ воды: красный $1{,}331$, синий $1{,}344$ — не из лекции", size=9, color=GREY)
    f.tight_layout()
    save(f, "dispersion-rainbow-drop")


@fig("dispersion-rainbow-geometry")
def _():
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
    # (a) side view: sun behind the observer, drops at 42 and 40.6 degrees from the antisolar direction
    ax1.set_xlim(-8.6, 2.2)
    ax1.set_ylim(-2.6, 5.3)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("вид сбоку: Солнце за спиной", fontsize=11, pad=3)
    sun = 18.0  # sun elevation, degrees
    d_s = vec(180 + sun)  # direction of the sun rays
    E = np.array([0.0, 0.0])
    L = 7.6
    col = {"красный": wavelength_rgb(700), "синий": wavelength_rgb(450)}
    for nm, a in (("красный", 42.4), ("синий", 40.6)):
        direction = vec(180 + sun - a)
        D = E + direction * L
        ax1.plot([E[0], D[0]], [E[1], D[1]], color=col[nm], lw=2.0, zorder=3)
        ax1.add_patch(Circle(D, 0.17, fc=GLASS, ec=col[nm], lw=1.6, zorder=4))
        # incoming sun ray to this drop
        S = D - d_s * 3.2
        ray(ax1, S, D, color=RAY, lw=1.3, f=0.4)
    ax1.plot([E[0], E[0] + d_s[0] * 7.5], [E[1], E[1] + d_s[1] * 7.5], color=GREY, lw=1, ls=(0, (5, 4)), zorder=1)
    ax1.plot([0], [0], "o", color=INK, ms=6, zorder=6)
    text(ax1, 0.25, -0.45, "глаз", size=10.5, ha="left")
    text(ax1, -4.9, -2.3, "направление,\nпротивоположное Солнцу", size=9.5, color=GREY)
    # angle arcs at the eye
    for nm, a, rr in (("красный", 42.4, 2.0), ("синий", 40.6, 1.45)):
        lo = 180 + sun - a
        hi = 180 + sun
        ax1.add_patch(Arc(E, 2 * rr, 2 * rr, theta1=lo, theta2=hi, color=col[nm], lw=1.4, zorder=3))
    ax1.text(-2.6, 0.5, "$42{,}4^\\circ$", color=col["красный"], fontsize=10.5, ha="center")
    ax1.text(-1.0, -0.85, "$40{,}6^\\circ$", color=col["синий"], fontsize=10.5, ha="center")
    ax1.text(-6.0, 4.6, "капля выше — красный свет в глаз,\nниже — синий", fontsize=10, ha="center", va="center")
    # (b) front view: arcs
    ax2.set_xlim(-3.7, 3.7)
    ax2.set_ylim(-0.3, 4.0)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("вид спереди: две радуги", fontsize=11, pad=3)
    th = np.linspace(rad(8), rad(172), 200)
    bands_main = [(wavelength_rgb(wl), r) for (_, wl), r in zip(SEVEN, (2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0))]
    for c, r in bands_main:
        ax2.plot(r * np.cos(th), r * np.sin(th), color=c, lw=3.2, solid_capstyle="butt")
    bands_sec = [(wavelength_rgb(wl), r) for (_, wl), r in zip(SEVEN, (3.05, 3.12, 3.19, 3.26, 3.33, 3.40, 3.47))]
    th2 = np.linspace(rad(10), rad(170), 200)
    for c, r in bands_sec:
        ax2.plot(r * np.cos(th2), r * np.sin(th2), color=c, lw=2.2, alpha=0.5, solid_capstyle="butt")
    ax2.text(0, 0.8, "основная радуга:\nкрасный снаружи,\nсиний внутри", ha="center", fontsize=10.5)
    ax2.text(0, 3.75, "побочная, слабее: красный внутри, синий снаружи", ha="center", fontsize=9.5, color=GREY)
    f.tight_layout()
    save(f, "dispersion-rainbow-geometry")


if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
        print("ok", n)
