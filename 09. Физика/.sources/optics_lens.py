"""Figures of section f14 "Оптика": notes "Линзы. Построение изображений" (lens-) and "Формула тонкой линзы" (thinlens-), lessons 209-214, 217, 218.

Run: python3 optics_lens.py [name ...]
PNG files go to content/14. Оптика/00. Вложения/
Every ray diagram is computed: the image position comes from the thin lens formula, and each ray passes through the computed point.
Figures marked "схема" are sketches, not measurements.
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "14. Оптика"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import ACCENT, BLUE, COPPER, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, VIOLET, num, saver, tint

GREY = MUTED  # the optical axis, guides and dimension lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
LENS = BLUE  # a lens, its centre: a colour of its own, apart from the object and the rays
LENS2 = tint(BLUE, 0.45)  # the second lens, or the glasses, beside a first one
GLASS = tint(SKY, 0.8)
R1 = RED  # characteristic ray 1: parallel to the axis
R2 = BLUE  # characteristic ray 2: through the optical centre
R3 = GREEN  # characteristic ray 3: through the focus
IMG = VIOLET  # an image
AUX = ACCENT  # an auxiliary ray or a quantity set against a first one
EYE = COPPER  # the eye in the glasses sketch

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


# ---------------------------------------------------------------- primitives


def new(xl, yl, k=1.2, nrows=1, ncols=1):
    """Figure with equal-aspect axes without frame; every panel has the same limits."""
    w = (xl[1] - xl[0]) * k * ncols
    h = (yl[1] - yl[0]) * k * nrows
    figure, axes = plt.subplots(nrows, ncols, figsize=(w, h), squeeze=False)
    for ax in axes.flat:
        ax.set_xlim(xl)
        ax.set_ylim(yl)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.plot(xl, [0, 0], color=GREY, lw=1.2, zorder=1)
    return figure, (axes[0, 0] if nrows * ncols == 1 else axes.flat)


def lens(ax, kind, half, x=0.0, w=0.12, color=LENS, lw=2.2, ls="-"):
    """Schematic lens: double arrow with outward heads (converging) or with inward heads (diverging)."""
    ax.plot([x, x], [-half, half], color=color, lw=lw, ls=ls, zorder=3)
    for s in (1, -1):
        if kind == "conv":
            ax.plot([x - w, x, x + w], [s * (half - 2 * w), s * half, s * (half - 2 * w)], color=color, lw=lw, zorder=3)
        else:
            ax.plot([x - w, x, x + w], [s * (half + 2 * w), s * half, s * (half + 2 * w)], color=color, lw=lw, zorder=3)


def line(ax, p, q, color, ls="-", lw=1.5, arrow=True, z=2, head=0.07):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, ls=ls, lw=lw, zorder=z)
    n = np.hypot(q[0] - p[0], q[1] - p[1])
    if arrow and n > 0.35:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ux, uy = (q[0] - p[0]) / n, (q[1] - p[1]) / n
        ax.annotate(
            "",
            xy=(mx + ux * head, my + uy * head),
            xytext=(mx - ux * head, my - uy * head),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=11, shrinkA=0, shrinkB=0),
            zorder=4,
        )


def arrow(ax, x, y0, y1, color=INK, dashed=False, lw=2.6, scale=14):
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y0),
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=lw, linestyle="--" if dashed else "-",
            mutation_scale=scale, shrinkA=0, shrinkB=0,
        ),
        zorder=5,
    )


def dim(ax, x0, x1, y, text, color=GREY, dy=0.08, va="bottom", fs=11, lw=1.0):
    ax.annotate(
        "", xy=(x1, y), xytext=(x0, y),
        arrowprops=dict(arrowstyle="<|-|>", color=color, lw=lw, mutation_scale=9, shrinkA=0, shrinkB=0),
    )
    ax.text((x0 + x1) / 2, y + (dy if va == "bottom" else -dy), text, ha="center", va=va, fontsize=fs, color=INK)


def vdim(ax, x, y0, y1, text, color=GREY, dx=0.08, ha="left", fs=11):
    ax.annotate(
        "", xy=(x, y1), xytext=(x, y0),
        arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.0, mutation_scale=9, shrinkA=0, shrinkB=0),
    )
    ax.text(x + (dx if ha == "left" else -dx), (y0 + y1) / 2, text, ha=ha, va="center", fontsize=fs, color=INK)


def dot(ax, x, y=0.0, real=True, color=INK, ms=5.5):
    ax.plot([x], [y], "o", ms=ms, mfc=color if real else PAPER, mec=color, mew=1.3, zorder=6)


def label(ax, x, y, text, ha="center", va="center", fs=11, color=INK, **kw):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, zorder=7, **kw)


def foci(ax, F, ox=0.0, names=("$F$", "$F$"), dy=0.07, real=None, avoid=(), ticks=None, above=()):
    """Mark both foci of a thin lens at x = ox +- |F| (hollow dots for a diverging lens).

    The label stands below the axis, left of the dot (right of it for the far focus of a diverging lens,
    where ray 3 runs parallel to the axis just above and ray 2 leaves below the label);
    it drops lower when its x is close to an x in `avoid` (the bases of the object and the image).
    A side s in `above` puts its label above the axis, right of the dot, for a figure with a ray through that focus.
    """
    r = F > 0 if real is None else real
    for s, nm in zip((-1, 1), names):
        x = ox + s * abs(F)
        dot(ax, x, 0, real=r)
        if nm:
            k = 4 if any(abs(x - a) < 0.3 * max(abs(F), 1) for a in avoid) else 1
            if s in above:
                label(ax, x + 0.06, dy, nm, ha="left", va="bottom")
            elif F < 0 and s > 0:
                label(ax, x + 0.05, -dy * k, nm, ha="left", va="top")
            else:
                label(ax, x - 0.05, -dy * k, nm, ha="right", va="top")


# ------------------------------------------------------------ ray diagrams


def image_of(F, d, h):
    f = None if abs(d - F) < 1e-9 else d * F / (d - F)
    return f, (None if f is None else -h * f / d)


def construct(ax, F, d, h, x_end, obj="arrow", rays=(1, 2, 3), ox=0.0, extend=0.45,
              names=True, mark_foci=True, two_f=False, arrow_lw=2.6, lab=("A", "B", "A'", "B'"),
              show_image=True, u=1.0, foci_above=()):
    """Image of the object tip A at distance d and height h in a thin lens of signed focal length F.

    The lens stands at x = ox.  Rays: 1 parallel to the axis, 2 through the optical centre, 3 through the front focus.
    Virtual parts are dashed.  u is the length unit of the picture: label offsets scale with it.
    """
    f, H = image_of(F, d, h)
    if obj == "arrow":
        arrow(ax, ox - d, 0, h, INK, lw=arrow_lw)
    else:
        dot(ax, ox - d, h, color=INK)
    if names:
        label(ax, ox - d - 0.06 * u, h + (0.04 * u if h > 0 else -0.04 * u), f"${lab[0]}$", ha="right", va="bottom" if h > 0 else "top")
        if obj == "arrow":
            label(ax, ox - d - 0.08 * u, -0.08 * u if h > 0 else 0.08 * u, f"${lab[1]}$", ha="right", va="top" if h > 0 else "bottom")
    xe = x_end
    if f is not None and f > 0:
        xe = min(x_end, f + extend)
    # ray 1
    if 1 in rays:
        line(ax, (ox - d, h), (ox, h), R1)
        line(ax, (ox, h), (ox + xe, h * (1 - xe / F)), R1)
        if f is not None and f < 0:
            line(ax, (ox, h), (ox + f, H), R1, ls="--", arrow=False, lw=1.2)
            if F < 0:
                line(ax, (ox + f, H), (ox + F, 0), R1, ls="--", arrow=False, lw=1.2)
    # ray 2
    if 2 in rays:
        line(ax, (ox - d, h), (ox, 0), R2)
        line(ax, (ox, 0), (ox + xe, -h / d * xe), R2)
        if f is not None and f < 0:
            line(ax, (ox, 0), (ox + f, H), R2, ls="--", arrow=False, lw=1.2)
    # ray 3
    if 3 in rays and f is not None:
        y3 = -h * F / (d - F)
        line(ax, (ox - d, h), (ox, y3), R3)
        line(ax, (ox, y3), (ox + xe, y3), R3)
        if F > 0 and d < F:
            line(ax, (ox - d, h), (ox - F, 0), R3, ls="--", arrow=False, lw=1.2)
        if F < 0:
            line(ax, (ox, y3), (ox - F, 0), R3, ls="--", arrow=False, lw=1.2)
        if f < 0:
            line(ax, (ox, y3), (ox + f, y3), R3, ls="--", arrow=False, lw=1.2)
    # image
    if f is not None and show_image:
        real = f > 0
        if obj == "arrow":
            arrow(ax, ox + f, 0, H, IMG, dashed=not real, lw=arrow_lw)
        else:
            dot(ax, ox + f, H, real=real, color=IMG)
        if names and not real and obj == "arrow":
            # virtual image: all rays pass the tip, so the label stands right of the shaft, low, beside the axis
            label(ax, ox + f + 0.08 * u, 0.12 * H, f"${lab[2]}$", ha="left", va="center", color=IMG)
        elif names and not real:
            # virtual point image: between ray 3 above and the ray through the centre, directly above the point
            label(ax, ox + f, H + 0.03 * u, f"${lab[2]}$", ha="center", va="bottom", color=IMG)
        elif names:
            label(ax, ox + f - 0.06 * u, H + (-0.05 * u if H < 0 else 0.05 * u), f"${lab[2]}$", ha="right", va="top" if H < 0 else "bottom", color=IMG)
        if names:
            if obj == "arrow":
                label(ax, ox + f + 0.08 * u, 0.08 * u if H < 0 else -0.08 * u, f"${lab[3]}$", ha="left", va="bottom" if H < 0 else "top", color=IMG)
    if mark_foci:
        avoid = [ox - d] + ([ox + f] if f is not None else [])
        foci(ax, F, ox, dy=0.07 * u, avoid=avoid, above=foci_above)
        if two_f and F > 0:
            for s in (-1, 1):
                x = ox + s * 2 * F
                dot(ax, x, 0, real=True)
                k = 4 if any(abs(x - a) < 0.3 * abs(F) for a in avoid) else 1
                label(ax, x - 0.05 * u, -0.07 * u * k, "$2F$", ha="right", va="top")
    return f, H


# ------------------------------------------------------------ note 1: lenses


def lens_shape(ax, cx, cy, s1, R1_, s2, R2_, a=0.16, half=1.0, fs=10, text=None):
    """Lens profile: s = +1 convex surface, -1 concave, 0 flat; R is the radius of the surface."""
    y = np.linspace(-half, half, 160)
    sag = lambda yy, R: R - np.sqrt(R ** 2 - yy ** 2)
    xl = cx - a + (s1 * sag(y, R1_) if s1 else 0 * y)
    xr = cx + a - (s2 * sag(y, R2_) if s2 else 0 * y)
    poly = np.concatenate([np.column_stack([xl, cy + y]), np.column_stack([xr[::-1], cy + y[::-1]])])
    ax.add_patch(Polygon(poly, closed=True, fc=GLASS, ec=LENS, lw=1.8))
    if text:
        ax.text(cx, cy - half - 0.22, text, ha="center", va="top", fontsize=fs)


@fig("lens-types")
def _():
    figure, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.set_xlim(-0.9, 10.0)
    ax.set_ylim(-3.9, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    xs = [1.0, 4.2, 7.4]
    # convex lenses are thicker in the middle, concave ones at the edge
    lens_shape(ax, xs[0], 1.7, 1, 2.4, 1, 2.4, a=0.42, text="двояковыпуклая")
    lens_shape(ax, xs[1], 1.7, 0, 1, 1, 1.6, a=0.42, text="плоско-выпуклая")
    lens_shape(ax, xs[2], 1.7, 1, 1.5, -1, 3.0, a=0.42, text="вогнуто-выпуклая")
    lens_shape(ax, xs[0], -1.9, -1, 2.4, -1, 2.4, a=0.12, text="двояковогнутая")
    lens_shape(ax, xs[1], -1.9, 0, 1, -1, 1.6, a=0.12, text="плоско-вогнутая")
    lens_shape(ax, xs[2], -1.9, 1, 3.0, -1, 1.5, a=0.12, text="выпукло-вогнутая")
    ax.text(-0.6, 1.7, "выпуклые", rotation=90, ha="center", va="center", fontsize=12, color=INK)
    ax.text(-0.6, -1.9, "вогнутые", rotation=90, ha="center", va="center", fontsize=12, color=INK)
    # symbols
    ax.plot([9.3, 9.3], [0.7, 2.7], color=LENS, lw=2.2)
    for s in (0.7, 2.7):
        d = 1 if s > 1 else -1
        ax.plot([9.3 - 0.15, 9.3, 9.3 + 0.15], [s - d * 0.3, s, s - d * 0.3], color=LENS, lw=2.2)
    ax.text(9.3, 0.3, "собирающая", ha="center", va="top", fontsize=10)
    ax.plot([9.3, 9.3], [-2.9, -0.9], color=LENS, lw=2.2)
    for s, d in ((-0.9, 1), (-2.9, -1)):
        ax.plot([9.3 - 0.15, 9.3, 9.3 + 0.15], [s + d * 0.3, s, s + d * 0.3], color=LENS, lw=2.2)
    ax.text(9.3, -3.3, "рассеивающая", ha="center", va="top", fontsize=10)
    return figure


@fig("lens-spherical-surfaces")
def _():
    figure, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for ax in (a1, a2):
        ax.set_aspect("equal")
        ax.axis("off")
    # a) two surfaces meet at the edge
    R1_, R2_ = 1.5, 1.5
    O1, O2 = 0.5, -0.5
    a1.set_xlim(-2.4, 2.5)
    a1.set_ylim(-1.75, 1.75)
    t = np.linspace(0, 2 * np.pi, 300)
    a1.plot(O1 + R1_ * np.cos(t), R1_ * np.sin(t), color=GREY, lw=1, ls="--")
    a1.plot(O2 + R2_ * np.cos(t), R2_ * np.sin(t), color=GREY, lw=1, ls="--")
    ymax = np.sqrt(R1_ ** 2 - ((O1 - O2) / 2) ** 2)
    y = np.linspace(-ymax, ymax, 200)
    xl = O1 - np.sqrt(R1_ ** 2 - y ** 2)
    xr = O2 + np.sqrt(R2_ ** 2 - y ** 2)
    a1.add_patch(Polygon(np.concatenate([np.column_stack([xl, y]), np.column_stack([xr[::-1], y[::-1]])]), fc=GLASS, ec=LENS, lw=2))
    a1.plot([-2.3, 2.4], [0, 0], color=INK, lw=1.2)
    dot(a1, O1, 0)
    dot(a1, O2, 0)
    label(a1, O1 + 0.05, -0.17, "$O_1$", ha="left", va="top")
    label(a1, O2 - 0.05, -0.17, "$O_2$", ha="right", va="top")
    th = np.radians(150)
    a1.plot([O1, O1 + R1_ * np.cos(th)], [0, R1_ * np.sin(th)], color=R1, lw=1.3)
    label(a1, O1 + 0.72 * R1_ * np.cos(th), 0.72 * R1_ * np.sin(th) + 0.16, "$R_1$", color=R1)
    th = np.radians(30)
    a1.plot([O2, O2 + R2_ * np.cos(th)], [0, R2_ * np.sin(th)], color=R2, lw=1.3)
    label(a1, O2 + 0.72 * R2_ * np.cos(th), 0.72 * R2_ * np.sin(th) + 0.16, "$R_2$", color=R2)
    label(a1, 1.7, 0.14, "главная оптическая ось", ha="left", fs=10, va="bottom")
    a1.text(0, -1.7, "обе поверхности сходятся у края", ha="center", va="top", fontsize=10)
    # b) thick meniscus cut off at the edge
    a2.set_xlim(-1.2, 4.3)
    a2.set_ylim(-1.75, 1.75)
    O1, R1_ = 1.3, 1.5
    O2, R2_ = 2.6, 2.3
    arc = np.radians(np.linspace(105, 255, 200))
    a2.plot(O1 + R1_ * np.cos(arc), R1_ * np.sin(arc), color=GREY, lw=1, ls="--")
    arc = np.radians(np.linspace(130, 230, 200))
    a2.plot(O2 + R2_ * np.cos(arc), R2_ * np.sin(arc), color=GREY, lw=1, ls="--")
    y = np.linspace(-1.0, 1.0, 200)
    xl = O1 - np.sqrt(R1_ ** 2 - y ** 2)
    xr = O2 - np.sqrt(R2_ ** 2 - y ** 2)
    a2.add_patch(Polygon(np.concatenate([np.column_stack([xl, y]), np.column_stack([xr[::-1], y[::-1]])]), fc=GLASS, ec=LENS, lw=2))
    a2.plot([-1.1, 4.2], [0, 0], color=INK, lw=1.2)
    dot(a2, O1, 0)
    dot(a2, O2, 0)
    label(a2, O1 - 0.05, -0.17, "$O_1$", ha="right", va="top")
    label(a2, O2 + 0.05, -0.17, "$O_2$", ha="left", va="top")
    th = np.radians(150)
    a2.plot([O1, O1 + R1_ * np.cos(th)], [0, R1_ * np.sin(th)], color=R1, lw=1.3)
    label(a2, O1 + 0.55 * R1_ * np.cos(th), 0.55 * R1_ * np.sin(th) + 0.16, "$R_1$", color=R1)
    th = np.radians(160)
    a2.plot([O2, O2 + R2_ * np.cos(th)], [0, R2_ * np.sin(th)], color=R2, lw=1.3)
    label(a2, O2 + 0.6 * R2_ * np.cos(th), 0.6 * R2_ * np.sin(th) + 0.16, "$R_2$", color=R2)
    label(a2, 3.0, 0.14, "главная оптическая ось", ha="left", fs=10, va="bottom")
    a2.text(1.6, -1.7, "тело обрезано по краю", ha="center", va="top", fontsize=10)
    return figure


@fig("lens-prism-assembly")
def _():
    """Schematic: plate and prisms with growing refracting angle bend a parallel beam towards one point."""
    figure, ax = plt.subplots(figsize=(10, 4.8))
    ax.set_xlim(-3.2, 4.4)
    ax.set_ylim(-2.25, 2.25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-3.2, 4.4], [0, 0], color=GREY, lw=1.2)
    Fx = 3.0
    w = 0.42
    centres = [0.0, 0.42, 0.84, 1.26, 1.68, -0.42, -0.84, -1.26, -1.68]
    for yc in centres:
        ylo, yhi = yc - w / 2, yc + w / 2
        if abs(yc) < 1e-9:
            poly = [(-0.13, ylo), (-0.13, yhi), (0.13, yhi), (0.13, ylo)]
        else:
            dthick = 0.08 + 0.17 * abs(yc)
            thin = 0.03
            big = thin + dthick
            if yc > 0:
                poly = [(-0.13, ylo), (-0.13, yhi), (-0.13 + thin, yhi), (-0.13 + big, ylo)]
            else:
                poly = [(-0.13, ylo), (-0.13, yhi), (-0.13 + big, yhi), (-0.13 + thin, ylo)]
        ax.add_patch(Polygon(poly, closed=True, fc=GLASS, ec=LENS, lw=1.3, zorder=3))
    for y0 in (1.68, 1.26, 0.84, 0.42, 0.0, -0.42, -0.84, -1.26, -1.68):
        line(ax, (-3.0, y0), (0.0, y0), R1, lw=1.3)
        line(ax, (0.0, y0), (Fx, 0), R1, lw=1.3)
    label(ax, 0.15, 2.05, "плоскопараллельная пластинка\nи призмы с растущим\nпреломляющим углом", ha="left", va="center", fs=10)
    dot(ax, Fx, 0)
    label(ax, Fx + 0.1, -0.08, "лучи идут в одну область", ha="left", va="top", fs=10)
    return figure


@fig("lens-focus-converging")
def _():
    figure, axes = new((-3.2, 3.6), (-1.75, 1.75), nrows=1, ncols=2, k=0.95)
    F = 2.0
    for ax, sgn in zip(axes, (1, -1)):
        Fs = sgn * F
        lens(ax, "conv" if sgn > 0 else "div", 1.4)
        for y0 in (-1.0, -0.5, 0.0, 0.5, 1.0):
            line(ax, (-3.0, y0), (0, y0), R1, lw=1.3, arrow=abs(y0) > 0.1)
            if sgn > 0:
                line(ax, (0, y0), (F + 0.9, y0 * (1 - (F + 0.9) / F)), R1, lw=1.3, arrow=abs(y0) > 0.1)
            else:
                xe = 3.3
                line(ax, (0, y0), (xe, y0 * (1 - xe / Fs)), R1, lw=1.3, arrow=abs(y0) > 0.1)
                line(ax, (0, y0), (Fs, 0), R1, ls="--", lw=1.0, arrow=False)
        foci(ax, Fs, names=("$F$", "$F$"))
        dim(ax, 0, Fs, -1.3, "$F$", va="top", dy=0.06)
    axes[0].set_title("собирающая: фокус действительный", fontsize=11)
    axes[1].set_title("рассеивающая: фокус мнимый", fontsize=11)
    return figure


@fig("lens-secondary-focus")
def _():
    figure, axes = new((-3.2, 4.8), (-2.7, 1.95), nrows=1, ncols=2, k=0.85)
    F = 2.0
    s = 0.25
    for ax, sgn in zip(axes, (1, -1)):
        Fs = sgn * F
        lens(ax, "conv" if sgn > 0 else "div", 1.4)
        for x in (-Fs, Fs):
            ax.plot([x, x], [-2.15, 1.85], color=GREY, lw=1, ls=(0, (6, 3)))
        for y0 in (-0.9, -0.45, 0.0, 0.45, 0.9):
            line(ax, (-3.0, y0 - 3.0 * s), (0, y0), R2, lw=1.3, arrow=abs(y0) > 0.1)
            xe = F + 0.9 if sgn > 0 else 4.7
            line(ax, (0, y0), (xe, y0 + (s * Fs - y0) / Fs * xe), R2, lw=1.3, arrow=abs(y0) > 0.1)
            if sgn < 0:
                line(ax, (0, y0), (Fs, s * Fs), R2, ls="--", lw=1.0, arrow=False)
        dot(ax, Fs, s * Fs, real=sgn > 0, color=IMG)
        if sgn > 0:
            label(ax, F + 1.0, s * F, "побочный\nфокус", ha="left", va="center", color=IMG, fs=10)
        else:
            # below the beam, with a leader to the point: every ray near the point is part of the beam
            ax.annotate("побочный\nфокус", (Fs, s * Fs), (-1.1, -1.85), ha="center", va="center", fontsize=10, color=IMG, zorder=7,
                        arrowprops=dict(arrowstyle="-", color=IMG, lw=0.8, shrinkA=2, shrinkB=4))
        foci(ax, Fs, names=("", "$F$") if sgn > 0 else ("$F$", ""))
        for x in (-Fs, Fs):
            # under the lowest ray, where no ray runs
            label(ax, x + 0.06, -2.2, "фокальная\nплоскость", ha="left", va="top", fs=9, color=NOTE)
    return figure


@fig("lens-characteristic-rays")
def _():
    figure, axes = new((-3.6, 3.6), (-1.8, 1.8), nrows=1, ncols=2, k=0.9)
    for ax, F in zip(axes, (1.0, -1.0)):
        lens(ax, "conv" if F > 0 else "div", 1.4)
        construct(ax, F, 2.6, 1.1, 3.4, two_f=(F > 0), extend=0.5)  # a taller object gives the virtual image room for its labels
    axes[0].set_title("собирающая линза", fontsize=11)
    axes[1].set_title("рассеивающая линза", fontsize=11)
    return figure


def image_fig(F, d, h, xl, yl, half, two_f=True, k=1.2, extend=0.45, rays=(1, 2, 3), note=None):
    figure, ax = new(xl, yl, k=k)
    lens(ax, "conv" if F > 0 else "div", half)
    construct(ax, F, d, h, xl[1] - 0.1, two_f=two_f, extend=extend, rays=rays)
    if note:
        label(ax, xl[1] - 0.1, yl[1] - 0.12, note, ha="right", va="top", fs=11)
    return figure


@fig("lens-image-d-gt-2F")
def _():
    return image_fig(1.0, 3.0, 0.8, (-4.3, 4.3), (-1.45, 1.45), 1.3)


@fig("lens-image-d-eq-2F")
def _():
    return image_fig(1.0, 2.0, 0.8, (-3.4, 3.4), (-1.45, 1.45), 1.3)


@fig("lens-image-F-2F")
def _():
    return image_fig(1.0, 1.5, 0.5, (-3.3, 4.3), (-1.4, 1.4), 1.25)


@fig("lens-image-d-eq-F")
def _():
    figure, ax = new((-3.3, 3.6), (-1.35, 1.35))
    lens(ax, "conv", 1.25)
    F, d, h = 1.0, 1.0, 0.8
    arrow(ax, -d, 0, h, INK)
    label(ax, -d - 0.06, h + 0.04, "$A$", ha="right", va="bottom")
    label(ax, -d - 0.08, -0.08, "$B$", ha="right", va="top")
    line(ax, (-d, h), (0, h), R1)
    line(ax, (0, h), (3.4, h * (1 - 3.4 / F)), R1)
    line(ax, (-d, h), (0, 0), R2)
    line(ax, (0, 0), (3.4, -h / d * 3.4), R2)
    foci(ax, F, avoid=[-d])
    for s in (-1, 1):
        dot(ax, s * 2 * F)
        label(ax, s * 2 * F - 0.05, -0.07, "$2F$", ha="right", va="top")
    label(ax, 3.45, 1.2, "лучи параллельны,\nизображения нет", ha="right", va="top", fs=11)
    return figure


@fig("lens-image-d-lt-F")
def _():
    return image_fig(1.0, 0.6, 0.5, (-3.2, 3.4), (-1.85, 1.85), 1.65, two_f=False)


@fig("lens-image-diverging")
def _():
    return image_fig(-1.0, 3.0, 0.8, (-3.6, 2.8), (-1.35, 1.35), 1.05, two_f=False, k=1.5)


# Kirik problems of lesson 211, coordinates recomputed from the thin lens formula


@fig("lens-problem-103-2")
def _():
    """Kirik 8, p. 103, no. 2: the object is a horizontal arrow above the axis, F = 1."""
    F = 1.0
    figure, ax = new((-3.0, 4.0), (-1.5, 1.3), k=1.25)
    lens(ax, "conv", 1.2)
    foci(ax, F)
    y0, dA, dB = 0.5, 2.4, 1.5
    ax.annotate("", xy=(-dB, y0), xytext=(-dA, y0), arrowprops=dict(arrowstyle="-|>", lw=2.6, color=INK, mutation_scale=14, shrinkA=0, shrinkB=0), zorder=5)
    label(ax, -dA - 0.05, y0 + 0.1, "$A$", ha="right", va="bottom")
    label(ax, -dB, y0 + 0.1, "$B$", va="bottom")
    fA, fB = dA * F / (dA - F), dB * F / (dB - F)
    hA, hB = -y0 * fA / dA, -y0 * fB / dB
    line(ax, (-dA, y0), (0, y0), R1)
    xe = fB + 0.15
    line(ax, (0, y0), (xe, y0 * (1 - xe / F)), R1)
    line(ax, (-dA, y0), (fA + 0.3, hA + (hA / fA) * 0.3), R2)
    line(ax, (-dB, y0), (xe, hB + (hB / fB) * 0.15), R2)
    ax.annotate("", xy=(fB, hB), xytext=(fA, hA), arrowprops=dict(arrowstyle="-|>", lw=2.6, color=IMG, mutation_scale=14, shrinkA=0, shrinkB=0), zorder=5)
    label(ax, fA - 0.08, hA - 0.03, "$A'$", ha="right", va="top", color=IMG)
    label(ax, fB + 0.25, hB - 0.05, "$B'$", ha="left", va="center", color=IMG)
    return figure


@fig("lens-problem-104-9")
def _():
    """Kirik 8, p. 104, no. 9: the lens is found from the object and the image; F = 1."""
    figure, ax = new((-3.7, 3.0), (-3.4, 3.45), k=0.95)
    lens(ax, "conv", 3.2)
    construct(ax, 1.0, 2.85, 2.9, 2.9, extend=0.35, lab=("A", "B", "A_1", "B_1"))
    dot(ax, 0, 0, color=LENS)
    label(ax, 0.08, 0.08, "$O$", ha="left", va="bottom", color=LENS)
    return figure


@fig("lens-problem-104-10")
def _():
    """Kirik 8, p. 104, no. 10: a virtual reduced upright image, diverging lens; unit 100 px of the book figure."""
    figure, ax = new((-6.3, 6.3), (-1.5, 1.5), k=0.85)
    lens(ax, "div", 1.15)
    construct(ax, -5.4, 3.6, 0.95, 6.2, extend=0.4, lab=("A", "B", "A_1", "B_1"))
    dot(ax, 0, 0, color=LENS)
    label(ax, 0.1, 0.1, "$O$", ha="left", va="bottom", color=LENS)
    return figure


def side_focus(ax, point, text_xy):
    """Label "побочный фокус" at text_xy with a thin leader to the secondary focus at point."""
    ax.annotate("побочный фокус", point, text_xy, ha="center", va="center", fontsize=10, color=IMG, zorder=7,
                arrowprops=dict(arrowstyle="-", color=IMG, lw=0.8, shrinkA=2, shrinkB=4))


def given_ray(ax, p, q, **kw):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", lw=2.4, color=INK, mutation_scale=13, shrinkA=0, shrinkB=0), zorder=5)


@fig("lens-problem-105-13")
def _():
    """Kirik 8, p. 105, no. 13: foci of a converging lens from one ray; F = 1."""
    figure, ax = new((-2.6, 2.6), (-1.65, 1.7), k=1.6)
    lens(ax, "conv", 1.45)
    s_in, y0 = 0.21, 1.10
    s_out = -0.89
    given_ray(ax, (-2.3, y0 - s_in * 2.3), (0, y0))
    line(ax, (0, y0), (2.3, y0 + s_out * 2.3), INK, lw=2.4, arrow=False)
    ax.annotate("", xy=(1.3, y0 + s_out * 1.3), xytext=(1.2, y0 + s_out * 1.2), arrowprops=dict(arrowstyle="-|>", lw=2.4, color=INK, mutation_scale=13))
    # focal planes
    for x in (-1, 1):
        ax.plot([x, x], [-1.3, 1.45], color=GREY, lw=1, ls=(0, (6, 3)))
    label(ax, 1.05, 1.45, "фокальная плоскость", ha="left", va="top", fs=9, color=NOTE)
    label(ax, -1.05, -1.3, "фокальная плоскость", ha="right", va="top", fs=9, color=NOTE)  # below both auxiliary lines
    # auxiliary ray through O parallel to the given one
    line(ax, (-2.3, -s_in * 2.3), (2.3, s_in * 2.3), AUX, lw=1.5, ls="--")
    dot(ax, 1.0, s_in * 1.0, color=IMG)
    # the labels of the side foci stand in the gaps between the lines, with a leader to the point
    side_focus(ax, (1.0, s_in * 1.0), (1.55, 0.72))
    dot(ax, 1.0, 0, color=R3)
    label(ax, 1.05, -0.08, "$F$", ha="left", va="top", color=R3)
    # the front focus from reversibility
    line(ax, (-2.3, -s_out * 2.3), (2.3, s_out * 2.3), AUX, lw=1.5, ls="--")
    line(ax, (-2.3, y0 - s_in * 2.3), (0, y0), R3, lw=1.0, arrow=False, ls=":")
    dot(ax, -1.0, -s_out * 1.0, color=IMG)
    side_focus(ax, (-1.0, -s_out * 1.0), (-0.58, 1.32))
    dot(ax, -1.0, 0, color=R3)
    label(ax, -1.05, -0.08, "$F$", ha="right", va="top", color=R3)
    return figure


@fig("lens-problem-105-14")
def _():
    """Kirik 8, p. 105, no. 14: foci of a diverging lens from one ray; |F| = 1."""
    figure, ax = new((-2.6, 2.6), (-1.7, 1.8), k=1.6)
    lens(ax, "div", 1.35)
    s_in, y0, s_out = -0.226, 1.19, 0.97
    given_ray(ax, (-2.3, y0 - s_in * 2.3), (0, y0))
    line(ax, (0, y0), (1.4, y0 + s_out * 1.4), INK, lw=2.4, arrow=False)
    ax.annotate("", xy=(0.95, y0 + s_out * 0.95), xytext=(0.85, y0 + s_out * 0.85), arrowprops=dict(arrowstyle="-|>", lw=2.4, color=INK, mutation_scale=13))
    for x in (-1, 1):
        ax.plot([x, x], [-1.5, 1.65], color=GREY, lw=1, ls=(0, (6, 3)))
    # two lines, right of each plane at the bottom: the auxiliary ray runs left of the left plane there
    label(ax, -0.97, -1.55, "фокальная\nплоскость", ha="left", va="bottom", fs=9, color=NOTE)
    label(ax, 1.05, -1.55, "фокальная\nплоскость", ha="left", va="bottom", fs=9, color=NOTE)
    # left: virtual continuation of the outgoing ray and the auxiliary ray through O
    line(ax, (0, y0), (-1.0, y0 - s_out * 1.0), INK, lw=1.3, ls="--", arrow=False)
    line(ax, (-2.3, -s_in * 2.3), (2.3, s_in * 2.3), AUX, lw=1.5, ls="--")
    dot(ax, -1.0, -s_in, real=False, color=IMG)
    side_focus(ax, (-1.0, -s_in), (-1.65, 1.0))
    dot(ax, -1.0, 0, real=False, color=R3)
    label(ax, -1.05, -0.08, "$F$", ha="right", va="top", color=R3)
    # right: reversed ray
    line(ax, (-2.3, -s_out * 2.3), (2.3, s_out * 2.3), AUX, lw=1.5, ls="--")
    line(ax, (0, y0), (1.0, y0 + s_in * 1.0), INK, lw=1.3, ls=":", arrow=False)
    dot(ax, 1.0, s_out, real=False, color=IMG)
    side_focus(ax, (1.0, s_out), (1.65, 0.38))
    dot(ax, 1.0, 0, real=False, color=R3)
    label(ax, 1.05, -0.08, "$F$", ha="left", va="top", color=R3)
    return figure


@fig("lens-problem-106-2")
def _():
    """Kirik 8, p. 106, no. 2 (level "достаточный"): point A and its virtual image above the axis; unit 100 px."""
    figure, ax = new((-2.3, 2.3), (-1.3, 1.4), k=1.9)
    lens(ax, "div", 1.0)
    construct(ax, -0.662, 1.70, 0.82, 2.2, obj="point", extend=0.4, lab=("A", "B", "A_1", "B_1"))
    dot(ax, 0, 0, color=LENS)
    label(ax, 0.06, -0.06, "$O$", ha="left", va="top", color=LENS)
    return figure


@fig("lens-problem-106-1")
def _():
    """Kirik 8, p. 106, no. 1: point A above the axis, real image below; F = 1."""
    figure, ax = new((-4.9, 2.6), (-3.5, 3.6), k=0.95)
    lens(ax, "conv", 3.3)
    # ray 1 and the grey ray cross the axis near the right focus, so its label goes above the axis, right of the dot
    f, H = construct(ax, 1.0, 4.32, 3.03, 2.5, obj="point", extend=0.5, lab=("A", "B", "A_1", "B_1"), foci_above=(1,))
    # arbitrary extra ray from A through the lens edge also passes the image
    line(ax, (-4.32, 3.03), (0, 1.5), GREY, lw=1.1)
    line(ax, (0, 1.5), (f + 0.3, 1.5 + (H - 1.5) / f * (f + 0.3)), GREY, lw=1.1)
    dot(ax, 0, 0, color=LENS)
    label(ax, 0.06, 0.08, "$O$", ha="left", va="bottom", color=LENS)
    return figure


# ------------------------------------------------------------ note 2


@fig("thinlens-derivation")
def _():
    F, d, h = 1.0, 2.4, 1.0
    f, H = image_of(F, d, h)
    figure, ax = new((-3.0, 2.3), (-1.85, 1.6), k=1.65)
    lens(ax, "conv", 1.45)
    # triangles
    ax.add_patch(Polygon([(-d, h), (-d, 0), (0, 0)], closed=True, fc=tint(R2, 0.7), ec="none", zorder=0))
    ax.add_patch(Polygon([(f, H), (f, 0), (0, 0)], closed=True, fc=tint(R2, 0.7), ec="none", zorder=0))
    ax.add_patch(Polygon([(0, h), (F, 0), (0, 0)], closed=True, fc=tint(AUX, 0.7), ec="none", zorder=0))
    ax.add_patch(Polygon([(f, H), (F, 0), (f, 0)], closed=True, fc=tint(AUX, 0.7), ec="none", zorder=0))
    construct(ax, F, d, h, 2.25, rays=(1, 2), extend=0.3, mark_foci=False, lab=("A", "B", "A'", "B'"))
    dot(ax, F, 0)
    label(ax, F, 0.1, "$F$", va="bottom")
    dot(ax, -F, 0)
    label(ax, -F, 0.1, "$F$", va="bottom")
    dot(ax, 0, 0, color=LENS)
    label(ax, -0.07, -0.12, "$O$", ha="right", va="top")
    label(ax, -0.07, h + 0.02, "$C$", ha="right", va="bottom")
    vdim(ax, -d - 0.3, 0, h, "$h$", ha="right")
    vdim(ax, f + 0.35, 0, H, "$H$")
    dim(ax, -d, 0, -0.97, "$d$", va="bottom", dy=0.06)
    dim(ax, 0, f, -1.3, "$f$", va="bottom", dy=0.06)
    dim(ax, 0, F, -1.65, "$F$", va="bottom", dy=0.06)
    dim(ax, F, f, -1.65, "$f-F$", va="bottom", dy=0.06)
    label(ax, 0.2, 1.55, "$\\triangle ABO\\ \\sim\\ \\triangle A'B'O$", color=R2, fs=12, ha="left", va="top")
    label(ax, 0.2, 1.25, "$\\triangle COF\\ \\sim\\ \\triangle A'B'F$", color=AUX, fs=12, ha="left", va="top")
    return figure


def f_of_d(d, F):
    with np.errstate(divide="ignore", invalid="ignore"):
        return d * F / (d - F)


@fig("thinlens-graph-f-d")
def _():
    figure, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    F = 1.0
    # converging
    d1 = np.linspace(0.02, 1 - 1e-3, 400)
    d2 = np.linspace(1 + 1e-3, 6.2, 800)
    a1.plot(d1, f_of_d(d1, F), color=IMG, lw=2.2)
    a1.plot(d2, f_of_d(d2, F), color=IMG, lw=2.2)
    dv = np.linspace(-3.4, -0.02, 300)
    a1.plot(dv, f_of_d(dv, F), color=GREY, lw=1.4, ls="--")
    a1.axhline(0, color=INK, lw=1)
    a1.axvline(0, color=INK, lw=1)
    a1.axvline(F, color=GREY, lw=1, ls=":")
    a1.axhline(F, color=GREY, lw=1, ls=":")
    for dd, nm, off in ((2.0, "$d=2F,\\ f=2F$", (0.1, 0.25)), (1.5, "$d=1{,}5F,\\ f=3F$", (0.15, 0.2)), (3.0, "$d=3F,\\ f=1{,}5F$", (0.15, 0.3))):
        ff = dd * F / (dd - F)
        a1.plot([dd], [ff], "o", color=R1, ms=6, zorder=5)
        a1.annotate(nm, (dd, ff), xytext=(dd + off[0] + 0.25, ff + off[1] + 0.4), fontsize=10, color=R1, arrowprops=dict(arrowstyle="-", color=R1, lw=0.8))
    a1.set_xlim(-3.4, 6.2)
    a1.set_ylim(-5, 6)
    a1.set_xlabel("$d$ (в единицах $F$)")
    a1.set_ylabel("$f$ (в единицах $F$)")
    a1.set_title("собирающая линза, $F>0$", fontsize=11)
    a1.text(6.1, 5.0, "$f>0$: изображение\nдействительное", ha="right", va="center", fontsize=10, color=INK)
    a1.text(-0.1, -3.2, "$f<0$: изображение\nмнимое", ha="right", va="center", fontsize=10, color=INK)
    a1.text(-3.2, 1.6, "$d<0$: мнимый предмет\n(пунктир)", ha="left", va="center", fontsize=9, color=NOTE)
    a1.grid(color=LIGHT)
    a1.set_xticks([-3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    # diverging
    Fn = -1.0
    d = np.linspace(0, 6.2, 400)
    a2.plot(d, f_of_d(d, Fn), color=IMG, lw=2.2)
    a2.axhline(0, color=INK, lw=1)
    a2.axvline(0, color=INK, lw=1)
    a2.axhline(Fn, color=GREY, lw=1, ls=":")
    a2.set_xlim(-0.4, 6.2)
    a2.set_ylim(-5, 6)
    a2.set_xlabel("$d$ (в единицах $|F|$)")
    a2.set_ylabel("$f$ (в единицах $|F|$)")
    a2.set_title("рассеивающая линза, $F<0$", fontsize=11)
    a2.text(6.1, -1.25, "$f\\to F$ при $d\\to\\infty$", ha="right", va="top", fontsize=10)
    a2.text(0.5, -3.0, "всегда $F<f<0$:\nмнимое изображение\nмежду линзой и фокусом", fontsize=10, ha="left", va="center")
    a2.grid(color=LIGHT)
    for ax in (a1, a2):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    figure.tight_layout()
    return figure


@fig("thinlens-graph-gamma-d")
def _():
    figure, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    F = 1.0
    d1 = np.linspace(0.0, 1 - 1e-3, 400)
    d2 = np.linspace(1 + 1e-3, 6.2, 800)
    g = lambda d, F: F / (d - F)
    a1.plot(d1, g(d1, F), color=IMG, lw=2.2)
    a1.plot(d2, g(d2, F), color=IMG, lw=2.2)
    a1.axhline(0, color=INK, lw=1)
    a1.axvline(0, color=INK, lw=1)
    a1.axvline(F, color=GREY, lw=1, ls=":")
    for v in (1, -1):
        a1.axhline(v, color=R1, lw=1, ls="--")
    a1.plot([2], [1], "o", color=R1, ms=6, zorder=5)
    a1.annotate("$d=2F$, $\\Gamma=1$", (2, 1), xytext=(2.6, 2.3), fontsize=10, color=R1, arrowprops=dict(arrowstyle="-", color=R1, lw=0.8))
    a1.set_xlim(-0.2, 6.2)
    a1.set_ylim(-4, 4)
    a1.set_xlabel("$d$ (в единицах $F$)")
    a1.set_ylabel("$\\Gamma$")
    a1.set_title("собирающая линза", fontsize=11)
    a1.text(6.1, 0.62, "$0<\\Gamma<1$: действительное\nуменьшенное", ha="right", fontsize=10, va="center")
    a1.text(6.1, 2.0, "$\\Gamma>1$: действительное\nувеличенное", ha="right", fontsize=10, va="center")
    a1.text(1.15, -3.0, "$\\Gamma<0$: мнимое,\n$|\\Gamma|>1$", ha="left", fontsize=10, va="center")
    a1.grid(color=LIGHT)
    Fn = -1.0
    d = np.linspace(0, 6.2, 400)
    a2.plot(d, g(d, Fn), color=IMG, lw=2.2)
    a2.axhline(0, color=INK, lw=1)
    a2.axvline(0, color=INK, lw=1)
    a2.axhline(-1, color=R1, lw=1, ls="--")
    a2.set_xlim(-0.2, 6.2)
    a2.set_ylim(-4, 4)
    a2.set_xlabel("$d$ (в единицах $|F|$)")
    a2.set_ylabel("$\\Gamma$")
    a2.set_title("рассеивающая линза", fontsize=11)
    a2.text(6.1, -2.2, "$-1<\\Gamma<0$: мнимое уменьшенное\nизображение при любом $d$", ha="right", va="center", fontsize=10)
    a2.grid(color=LIGHT)
    for ax in (a1, a2):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    figure.tight_layout()
    return figure


@fig("thinlens-coordinates")
def _():
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    cases = [
        (2.4, 1.0, 1.0, "действительное изображение: $f>0$"),
        (0.6, 0.5, 1.0, "мнимое изображение: $f<0$"),
    ]
    for ax, (d, h, F, title) in zip(axes, cases):
        f, H = image_of(F, d, h)
        Gm = f / d
        Hc = Gm * h  # lecturer's coordinate H, counted downwards
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-3.4, 3.7)
        ax.set_ylim(-2.0, 1.9)
        ax.set_title(title, fontsize=11)
        ax.annotate("", xy=(-3.3, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.4, mutation_scale=12))
        ax.annotate("", xy=(3.6, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.4, mutation_scale=12))
        ax.annotate("", xy=(0, 1.8), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.4, mutation_scale=12))
        ax.annotate("", xy=(0, -1.9), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.4, mutation_scale=12))
        label(ax, -3.25, 0.12, "ось $d$", ha="left", va="bottom", color=NOTE)
        label(ax, 3.55, 0.12, "ось $f$", ha="right", va="bottom", color=NOTE)
        label(ax, 0.08, 1.75, "ось $h$", ha="left", va="top", color=NOTE)
        label(ax, 0.08, -1.85, "ось $H$", ha="left", va="bottom", color=NOTE)
        # the object point has the coordinates (d, h): d is counted to the left
        dot(ax, -d, h, color=INK)
        label(ax, -d + (-0.1 if f > 0 else 0.12), h + 0.1, "$(d;\\,h)$", ha="right" if f > 0 else "left", va="bottom")
        # image point: f to the right, H downwards
        dot(ax, f, -Hc, real=f > 0, color=IMG)
        label(ax, f + (0.1 if f > 0 else -0.1), -Hc + (-0.12 if Hc > 0 else 0.12), "$(f;\\,H)$", ha="left" if f > 0 else "right", va="top" if Hc > 0 else "bottom", color=IMG)
        ax.plot([-d, f], [h, -Hc], color=R2, lw=1.3, ls="--")
        ax.plot([-d, -d], [0, h], color=GREY, lw=0.9, ls=":")
        ax.plot([f, f], [0, -Hc], color=GREY, lw=0.9, ls=":")
        dot(ax, 0, 0, color=LENS)
    return figure


@fig("thinlens-virtual-object")
def _():
    figure, ax = new((-2.6, 3.0), (-1.2, 1.3), k=1.6)
    lens(ax, "conv", 1.05)
    F = 1.0
    dS = -2.0  # virtual object: d < 0, the converging beam aims at x = +2
    f = dS * F / (dS - F)
    for y0 in (0.7, -0.7):
        line(ax, (-1.4, y0 * (1 + 1.4 / 2.0)), (0, y0), INK, lw=1.5)
        line(ax, (0, y0), (2.0, 0), INK, lw=1.2, ls="--", arrow=False)
        line(ax, (0, y0), (f + 0.25, y0 * (1 - (f + 0.25) / f)), R1, lw=1.5)
    dot(ax, 2.0, 0, real=False, color=INK)
    label(ax, 2.08, -0.08, "$S$ (мнимый предмет)", ha="left", va="top")
    dot(ax, f, 0, color=IMG)
    label(ax, f, -0.12, "$S'$", va="top", color=IMG)
    foci(ax, F)
    label(ax, -2.5, 0.6, "сходящийся пучок\nот другой системы", ha="left", va="center", fs=10)
    return figure


@fig("thinlens-two-lenses")
def _():
    figure, ax = new((-3.6, 6.8), (-1.25, 1.25), k=1.0)
    D1, D2 = 0.5, 0.25
    d = 3.0
    f1 = 1 / (D1 - 1 / d)
    D = D1 + D2
    f = 1 / (D - 1 / d)
    lens(ax, "conv", 1.05, x=-0.05, color=LENS)
    lens(ax, "conv", 1.05, x=0.05, color=LENS2)
    dot(ax, -d, 0)
    label(ax, -d, -0.1, "$S$", va="top")
    y0 = 0.6
    line(ax, (-d, 0), (0, y0), INK)
    line(ax, (0, y0), (f + 0.4, y0 * (1 - (f + 0.4) / f)), R1)
    line(ax, (0, y0), (f1, 0), AUX, ls="--", arrow=False, lw=1.2)
    dot(ax, f1, 0, real=False, color=AUX)
    label(ax, f1, -0.1, "$S'$", va="top", color=AUX)
    dot(ax, f, 0, color=IMG)
    label(ax, f, -0.1, "$S''$", va="top", color=IMG)
    label(ax, -0.9, 1.15, "$D_1$", ha="right", color=LENS)
    label(ax, 0.75, 1.15, "$D_2$", ha="left", color=LENS2)
    dim(ax, -d, 0, -0.7, "$d$", va="top", dy=0.06)
    dim(ax, 0, f, -0.7, "$f$", va="top", dy=0.06)
    dim(ax, 0, f1, -1.12, "$f_1$", va="top", dy=0.06)
    return figure


@fig("thinlens-eye-glasses")
def _():
    """Schematic (not to scale in the eye): reading distance 20 cm without glasses and 25 cm with them."""
    figure, axes = plt.subplots(2, 1, figsize=(11, 6.6))
    f = 2.0  # the retina stays where it is; one unit of the picture is 4 cm
    Deye = 1 / 5.0 + 1 / f
    titles = ["без очков: книга в $d=20$ см, изображение на сетчатке", "в очках: книга в $d_{опт}=25$ см, изображение там же"]
    for ax, title, d, glasses in zip(axes, titles, (5.0, 6.25), (False, True)):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-0.6, 10.2)
        ax.set_ylim(-1.45, 1.45)
        ax.set_title(title, fontsize=11)
        assert abs(1 / d + 1 / f - Deye - (1 / 6.25 - 1 / 5.0 if glasses else 0)) < 1e-9
        Xl = d
        ax.plot([-0.6, 10.2], [0, 0], color=GREY, lw=1.2)
        a = (f + 0.35) / 2  # the front wall of the eye stands 0.35 before the lens of the eye, so the glasses fit outside
        b = 1.05
        th = np.linspace(0, 2 * np.pi, 300)
        ax.plot(Xl + f - a + a * np.cos(th), b * np.sin(th), color=EYE, lw=1.8)
        label(ax, Xl + f - a + 0.05, -b - 0.12, "глаз", va="top", color=EYE, fs=10)
        h = 0.55
        arrow(ax, 0, 0, h, INK)
        label(ax, 0, h + 0.1, "книга", va="bottom", fs=10)
        lens(ax, "conv", 0.75, x=Xl, w=0.1)
        if glasses:
            lens(ax, "div", 0.75, x=Xl - 0.5, w=0.1, color=LENS2)
            label(ax, Xl - 0.65, 0.85, "очки", ha="right", color=LENS2, fs=10)
        ximg = Xl + f
        himg = -h * f / d
        for y0 in (0.6, -0.6):
            line(ax, (0, h), (Xl, y0), R1, lw=1.3)
            line(ax, (Xl, y0), (ximg, himg), R1, lw=1.3)
        arrow(ax, ximg, 0, himg, IMG, lw=2.0, scale=10)
        dim(ax, 0, Xl, -0.95, "$d=20$ см" if not glasses else "$d_{опт}=25$ см", va="bottom", dy=0.06)
        dim(ax, Xl, ximg, -0.95, "$f$", va="bottom", dy=0.06)
    return figure


def screen_panels(L_, F, h, xl, yl, half, positions, k, w, dy, dtxt, ftxt, ltxt, dims=(-8.0, 11.0, 15.0)):
    """Object at x = 0, screen at x = L_, the lens at each of the given positions; rays 1 and 2 only."""
    figure, axes = new(xl, yl, k=k, nrows=len(positions), ncols=1)
    axes = np.atleast_1d(axes)
    for ax, dd in zip(axes, positions):
        f, H = image_of(F, dd, h)
        ax.plot([L_, L_], [-half, half], color=INK, lw=3)
        label(ax, L_, half + dy, "экран", va="bottom", fs=10)
        lens(ax, "conv", half - 2.5 * w, x=dd, w=w)
        construct(ax, F, dd, h, L_, ox=dd, extend=0.0, names=False, mark_foci=False, rays=(1, 2), arrow_lw=2.4, u=dy)
        label(ax, -0.6 * dy, h + 0.4 * dy, "$A$", ha="right", va="bottom")
        label(ax, -0.6 * dy, -0.4 * dy, "$B$", ha="right", va="top")
        dim(ax, 0, dd, dims[0], dtxt(dd), va="top", dy=0.5 * dy, fs=10)
        dim(ax, dd, L_, dims[1], ftxt(f), va="bottom", dy=0.5 * dy, fs=10)
        dim(ax, 0, L_, dims[2], ltxt, va="bottom", dy=0.5 * dy, fs=10)
        gm = f / dd
        gtxt = num(gm, 2, math=True).rstrip("0").rstrip("{,}")
        label(ax, L_ + 2 * dy, H / 2, f"$\\Gamma={gtxt}$", fs=11, color=IMG, ha="left", va="center")
    return figure


@fig("thinlens-screen-two-positions")
def _():
    """Two lens positions give a sharp image: L = 100 cm, l = 20 cm, F = 24 cm."""
    F, L_, l_, h = 24.0, 100.0, 20.0, 10.0
    d1 = (L_ - l_) / 2
    positions = (d1, d1 + l_)
    return screen_panels(
        L_, F, h, (-8, 122), (-19, 19.5), 17.5, positions, 0.08, 1.0, 1.0,
        lambda d: f"$d={d:.0f}$ см", lambda f: f"$f={f:.0f}$ см", "$L=100$ см", dims=(-8.0, 11.0, 15.5),
    )


@fig("thinlens-lab-bench")
def _():
    """Schematic of the optical bench with the two sharp positions of the lens (lab data of lesson 218)."""
    figure, axes = plt.subplots(2, 1, figsize=(11.5, 5.4))
    data = [(70, 16.6, 62.1, 45.5), (50, 18.3, 40.6, 22.3)]
    x_obj = 5.0
    for ax, (L_, x1, x2, l_) in zip(axes, data):
        ax.set_aspect("equal")
        ax.set_xlim(0, 82)
        ax.set_ylim(-7.5, 9)
        ax.axis("off")
        ax.add_patch(Polygon([(0, -1.2), (80, -1.2), (80, 0), (0, 0)], closed=True, fc=LIGHT, ec=INK, lw=1.2))
        for t in range(0, 81, 10):
            ax.plot([t, t], [-1.2, 0], color=INK, lw=1.1)
            ax.text(t, -1.6, f"{t}", ha="center", va="top", fontsize=9)
        ax.text(81.5, -1.6, "см", ha="left", va="top", fontsize=9)
        x_scr = x_obj + L_
        arrow(ax, x_obj, 0, 3.0, INK, lw=2.4, scale=10)
        label(ax, x_obj, 3.4, "предмет", va="bottom", fs=10)
        ax.plot([x_scr, x_scr], [0, 6.0], color=INK, lw=3.5)
        label(ax, x_scr, 6.4, "экран", va="bottom", fs=10)
        lens(ax, "conv", 4.4, x=x1, w=0.6, color=R1)
        lens(ax, "conv", 4.4, x=x2, w=0.6, color=R2)
        label(ax, x1, 5.2, f"$x_1={num(x1, '', math=True)}$" + "\nувеличенное", va="bottom", color=R1, fs=10)
        label(ax, x2, 5.2, f"$x_2={num(x2, '', math=True)}$" + "\nуменьшенное", va="bottom", color=R2, fs=10)
        dim(ax, x_obj, x_scr, 8.4, f"$L={L_}$ см", va="bottom", dy=0.3, fs=10)
        dim(ax, x1, x2, -4.3, f"$l=|x_1-x_2|={num(l_, '', math=True)}$" + " см", va="top", dy=0.3, fs=10)
    return figure


@fig("thinlens-lab-result")
def _():
    figure, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.axhline(10.0, color=GREY, ls="--", lw=1.4)
    ax.text(0.55, 9.97, "на линзе указано 100 мм", ha="left", va="top", fontsize=10, color=NOTE)
    ax.plot([1, 2], [10.1, 10.0], "o", color=IMG, ms=8)
    ax.set_xlim(0.5, 2.5)
    ax.set_ylim(9.7, 10.4)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["$L=70$ см", "$L=50$ см"])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, 1)))  # decimal comma, as in the other figures
    ax.set_ylabel("$F$, см")
    ax.grid(color=LIGHT)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for x, y in ((1, 10.1), (2, 10.0)):
        ax.text(x, y + 0.06, num(y, 1), ha="center", fontsize=10)
    return figure


@fig("thinlens-problem-screen-90")
def _():
    """Task 1127: L = 90 cm, F = 20 cm; the lens stands 30 cm or 60 cm from the object."""
    L_, F = 90.0, 20.0
    root = np.sqrt(L_ ** 2 - 4 * L_ * F)
    positions = ((L_ - root) / 2, (L_ + root) / 2)
    return screen_panels(
        L_, F, 6.0, (-8, 110), (-17, 18.5), 15.0, positions, 0.085, 1.0, 1.0,
        lambda d: f"$d={d:.0f}$ см", lambda f: f"$f={f:.0f}$ см", "$L=90$ см", dims=(-7.0, 9.5, 13.0),
    )


@fig("thinlens-problem-screen-300")
def _():
    """Task 1128: L = 3 m, image five times larger: d = 50 cm, f = 250 cm, D = 2,4 dptr."""
    L_, G = 300.0, 5.0
    d = L_ / (1 + G)
    F = d * (G * d) / (d + G * d)
    return screen_panels(
        L_, F, 10.0, (-15, 360), (-66, 74), 62.0, (d,), 0.03, 4.0, 5.0,
        lambda x: f"$d={x:.0f}$ см", lambda f: f"$f={f:.0f}$ см", "$L=300$ см", dims=(-38.0, 22.0, 62.0),
    )


def simple_problem(F, d, h, xl, yl, half, k=1.2, two_f=False, extend=0.45):
    figure, ax = new(xl, yl, k=k)
    lens(ax, "conv" if F > 0 else "div", half, w=(xl[1] - xl[0]) * 0.012)
    construct(ax, F, d, h, xl[1] - 0.05 * (xl[1] - xl[0]), two_f=two_f, extend=extend, u=abs(F))
    return figure


@fig("thinlens-problem-diverging-f")
def _():
    """Kirik 8, p. 112, no. 2: d = 15 cm, f = -6 cm, F = -10 cm; h is chosen for the picture."""
    return simple_problem(-10.0, 15.0, 4.0, (-18.5, 15.5), (-6.8, 6.8), 5.6, k=0.3, extend=3)


@fig("thinlens-problem-coin")
def _():
    """Kirik 8, p. 112, no. 3: F = 6 cm, f = -18 cm, d = 4,5 cm."""
    return simple_problem(6.0, 4.5, 2.0, (-22, 22), (-10.5, 10.5), 9.0, k=0.25, extend=3)


@fig("thinlens-problem-1120")
def _():
    """Rymkevich 1120: d = 4 cm, Gamma = -5, F = 5 cm (D = 20 dptr)."""
    return simple_problem(5.0, 4.0, 1.0, (-23, 22), (-7.2, 7.2), 5.8, k=0.25, extend=3)


@fig("thinlens-problem-1122")
def _():
    """Rymkevich 1122: F = 12 cm, Gamma = +3, d = 16 cm, f = 48 cm."""
    return simple_problem(12.0, 16.0, 3.0, (-48, 70), (-13, 13), 11, k=0.11, two_f=True, extend=6)


@fig("thinlens-problem-1124")
def _():
    """Rymkevich 1124: d = 40 cm, Gamma = -1/4, F = -40/3 cm (D = -7,5 dptr)."""
    return simple_problem(-40 / 3, 40.0, 12.0, (-50, 46), (-16, 16), 14, k=0.11, extend=6)


@fig("thinlens-problem-1125")
def _():
    """Rymkevich 1125: d = 4F, the image is three times smaller (F = 1)."""
    return simple_problem(1.0, 4.0, 0.9, (-4.6, 3.2), (-1.4, 1.4), 1.25, k=1.45, two_f=True, extend=0.5)


@fig("thinlens-problem-h-d")
def _():
    """Kirik 8, p. 115, no. 8: d1 = 36 cm, H1 = 10 cm; d2 = 24 cm, H2 = 20 cm; the solution is F = 12 cm and h = 20 cm."""
    F, h = 12.0, 20.0
    figure, axes = new((-52, 36), (-27, 27), k=0.095, nrows=2, ncols=1)
    for ax, dd in zip(axes, (36.0, 24.0)):
        lens(ax, "conv", 23, w=1.6)
        construct(ax, F, dd, h, 33.0, extend=3, names=False, rays=(1, 2), two_f=False, arrow_lw=2.4, u=F)
        f, H = image_of(F, dd, h)
        label(ax, -dd - 1.5, h / 2, "$h=20$ см", ha="right", fs=10)
        label(ax, f + 2.0, H / 2, f"$H={-H:.0f}$ см", ha="left", color=IMG, fs=10)
        label(ax, -51, -22, f"$d={dd:.0f}$ см, $f={f:.0f}$ см", ha="left", va="center", fs=10)
    return figure


def main(names):
    todo = names or list(FIGS)
    for n in todo:
        figure = FIGS[n]()
        if figure is not None:
            save(figure, n)


if __name__ == "__main__":
    main(sys.argv[1:])
