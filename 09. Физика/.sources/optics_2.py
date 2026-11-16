"""Figures for the notes "Преломление света" and "Полное внутреннее отражение" (section f14, lessons 202-208).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 optics_2.py [name ...]
PNG files go to content/14. Оптика/00. Вложения/ (prefixes refraction-, tir-)

Every ray is built from the vector form of Snell's law (refract below), and each figure asserts the
numbers it prints against the lesson data or the stated indices.
"""
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = COURSE / "content" / "14. Оптика" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)

from theme import ACCENT, ASH, BLUE, GREEN, INK, MUTED, PAPER, RED, SKY, VIOLET, WARM, num, saver, tint

GRID = ASH
RAY = GREEN  # every ray of light
RAY2 = RED  # the second quantity: an auxiliary angle, a shift, a second case
GOLD = WARM  # a source, a coin, a bright body
SPECIAL = ACCENT  # a highlighted quantity or a critical ray
GREY = tint(INK, 0.4)  # small notes and secondary text
GUIDE = MUTED  # normals and other guides
GLASS = tint(SKY, 0.8)
WATER = tint(SKY, 0.7)
PLASTIC = tint(INK, 0.88)  # a neutral pale body, apart from glass and water

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


save = saver(OUT)


def ru_axis(*axs, y=True):
    """Decimal comma on the tick labels."""
    fmt = FuncFormatter(lambda v, _: num(v, None))
    for a in axs:
        a.xaxis.set_major_formatter(fmt)
        if y:
            a.yaxis.set_major_formatter(fmt)


# ---------- geometry ----------


def rad(d):
    return math.radians(d)


def deg(r):
    return math.degrees(r)


def vec(theta):
    """Unit vector at theta degrees counter-clockwise from +x."""
    return np.array([math.cos(rad(theta)), math.sin(rad(theta))])


def ang(v):
    return deg(math.atan2(v[1], v[0]))


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def refract(d, nrm, n1, n2):
    """Vector Snell's law. nrm is a unit normal pointing against d (toward the side d came from).

    Returns the refracted unit direction, or None at total internal reflection.
    """
    c = -float(np.dot(nrm, d))
    r = n1 / n2
    k = 1 - r * r * (1 - c * c)
    if k < 0:
        return None
    return r * d + (r * c - math.sqrt(k)) * nrm


def reflect(d, nrm):
    return d - 2 * float(np.dot(d, nrm)) * nrm


def inc_angle(d, nrm):
    """Angle in degrees between a ray and the normal line."""
    return deg(math.acos(min(1.0, abs(float(np.dot(d, nrm))))))


def snell_check(n1, a1, n2, a2, tol=1e-6):
    assert abs(n1 * math.sin(rad(a1)) - n2 * math.sin(rad(a2))) < tol, (n1, a1, n2, a2)


def seg_hit(p, d, a, b):
    """Parameter t > 0 where ray p + t d crosses segment ab, or None."""
    e = b - a
    den = cross(d, e)
    if abs(den) < 1e-12:
        return None
    t = cross(a - p, e) / den
    s = cross(a - p, d) / den
    if t > 1e-9 and -1e-9 <= s <= 1 + 1e-9:
        return t
    return None


def poly_hit(p, d, poly, skip=None):
    """Nearest edge crossed by the ray: (t, edge index, outward unit normal)."""
    best = None
    n = len(poly)
    cx = sum(v[0] for v in poly) / n
    cy = sum(v[1] for v in poly) / n
    for i in range(n):
        if i == skip:
            continue
        a, b = np.array(poly[i]), np.array(poly[(i + 1) % n])
        t = seg_hit(p, d, a, b)
        if t is not None and (best is None or t < best[0]):
            e = (b - a) / np.linalg.norm(b - a)
            nrm = np.array([e[1], -e[0]])
            if float(np.dot(nrm, np.array([cx, cy]) - a)) > 0:
                nrm = -nrm
            best = (t, i, nrm)
    return best


# ---------- drawing primitives ----------


def canvas(w, h, xlim, ylim):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return f, ax


def line(ax, p, q, color=INK, lw=2.0, ls="-", z=5, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round", **kw)


def head(ax, p, q, color=INK, lw=2.0, f=0.55, ms=15, z=6):
    """Arrow head on segment pq at fraction f."""
    p, q = np.array(p, float), np.array(q, float)
    a = p + (q - p) * (f - 0.015)
    b = p + (q - p) * (f + 0.015)
    ax.add_patch(
        FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=z)
    )


def ray(ax, p, q, color=RAY, lw=2.2, ls="-", f=0.55, arrow=True, z=5):
    line(ax, p, q, color=color, lw=lw, ls=ls, z=z)
    if arrow:
        head(ax, p, q, color=color, lw=lw, f=f, z=z + 1)


def text(ax, x, y, s, size=11, ha="center", va="center", color=INK, **kw):
    ax.text(x, y, s, fontsize=size, ha=ha, va=va, color=color, zorder=10, **kw)


def arc(ax, o, a1, a2, r, label=None, color=INK, lab_r=None, fs=11, lw=1.6, n=1):
    """Angle mark at o between directions a1 and a2 (degrees from +x); n concentric arcs."""
    diff = (a2 - a1 + 180) % 360 - 180
    t1, t2 = (a1, a1 + diff) if diff > 0 else (a1 + diff, a1)
    for k in range(n):
        ax.add_patch(Arc(o, 2 * (r + 0.07 * r * k), 2 * (r + 0.07 * r * k), theta1=t1, theta2=t2, color=color, lw=lw, zorder=6))
    if label:
        mid = rad(a1 + diff / 2)
        lr = lab_r if lab_r else r * 1.45
        text(ax, o[0] + lr * math.cos(mid), o[1] + lr * math.sin(mid), label, size=fs, color=color)


def right_mark(ax, o, a1, a2, s=0.22, color=INK):
    u, v = vec(a1) * s, vec(a2) * s
    ax.add_patch(Polygon([o + u, o + u + v, o + v], closed=False, fill=False, ec=color, lw=1.4, zorder=6))


def eye(ax, x, y, s=0.28, color=INK):
    ax.add_patch(Ellipse((x, y), 2 * s, s * 1.15, fc=PAPER, ec=color, lw=1.6, zorder=8))
    ax.add_patch(Circle((x, y), s * 0.3, fc=color, ec=color, zorder=9))


def halfplane(ax, xs, y0, y1, color, z=0):
    ax.add_patch(Rectangle((xs[0], y0), xs[1] - xs[0], y1 - y0, fc=color, ec="none", zorder=z))


# ---------- generic interface drawing ----------


def interface(ax, o, n1, n2, alpha, from_top=True, rot=0.0, L=3.0, lab=True, refl=True, names=("1", "2"),
              color=RAY, fs=11, arc_r=0.85, reflect_ls="--"):
    """Boundary through o; medium "names[0]" above (index n1 if light comes from the top), below n2.

    Light travels from the medium it starts in into the other one. alpha is the angle of incidence in degrees.
    rot turns the whole picture counter-clockwise (degrees). Returns (beta, refracted end point).
    """
    R = lambda v: np.array([math.cos(rad(rot)) * v[0] - math.sin(rad(rot)) * v[1], math.sin(rad(rot)) * v[0] + math.cos(rad(rot)) * v[1]])
    up = R(np.array([0.0, 1.0]))
    nrm_src = up if from_top else -up  # points into the source medium
    d_in = -vec(ang(nrm_src) + (alpha if from_top else -alpha))  # incident direction (toward o)
    # incident ray comes from the upper-left (top) / lower-left (bottom)
    src_dir = -d_in
    n_src, n_dst = (n1, n2) if from_top else (n2, n1)
    d_out = refract(d_in, nrm_src, n_src, n_dst)
    beta = inc_angle(d_out, nrm_src) if d_out is not None else None
    if beta is not None:
        snell_check(n_src, alpha, n_dst, beta)
    # boundary and normal
    t = R(np.array([1.0, 0.0]))
    line(ax, o - t * (L * 1.15), o + t * (L * 1.15), color=INK, lw=2.0, z=3)
    line(ax, o - up * L, o + up * L, color=GUIDE, lw=1.3, ls=(0, (5, 4)), z=2)
    p_in = o + src_dir * L
    ray(ax, p_in, o, color=color)
    if beta is not None:
        q = o + d_out * L
        ray(ax, o, q, color=color)
        arc(ax, o, ang(-nrm_src), ang(d_out), arc_r, label=None, color=color)
    if refl:
        d_r = reflect(d_in, nrm_src)
        ray(ax, o, o + d_r * L, color=GREY, ls=reflect_ls, lw=1.6)
    if lab:
        a_dir = ang(nrm_src)
        arc(ax, o, a_dir, ang(src_dir), arc_r, label=None, color=color)
    return beta, (o + d_out * L if d_out is not None else None), nrm_src, src_dir, d_out


# =====================================================================
# Refraction
# =====================================================================


@fig("refraction-boundary-notation")
def _():
    n1, n2, a = 1.0, 1.45, 40.0
    f, ax = canvas(8.2, 5.6, (-4.2, 4.6), (-3.4, 3.4))
    halfplane(ax, (-4.2, 4.6), -3.4, 0, PLASTIC)
    o = np.array([0.0, 0.0])
    beta, q, nrm, src, dout = interface(ax, o, n1, n2, a, L=3.0, arc_r=0.9)
    assert abs(beta - math.degrees(math.asin(math.sin(rad(a)) / n2))) < 1e-9
    text(ax, -3.6, 2.9, "среда 1", size=12, ha="left", color=GREY)
    text(ax, -3.6, -2.9, "среда 2", size=12, ha="left", color=GREY)
    text(ax, -2.2, 2.45, "падающий\nлуч", size=11)
    text(ax, 2.6, 2.55, "отражённый\nлуч", size=11, color=GREY)
    text(ax, 2.05, -2.65, "преломлённый\nлуч", size=11)
    text(ax, 0.15, 3.15, "перпендикуляр", size=10.5, ha="left", color=GREY)
    text(ax, -0.25, -0.3, "точка\nпадения", size=10, ha="right", va="top", color=GREY)
    text(ax, -0.52, 1.25, r"$\alpha$", size=14, color=RAY)
    text(ax, 0.55, 1.25, r"$\gamma$", size=14, color=GREY)
    arc(ax, o, 90, 90 - a, 0.9, label=None, color=GREY, n=2)
    text(ax, 0.3, -1.3, r"$\beta$", size=14, color=RAY)
    f.tight_layout()
    save(f, "refraction-boundary-notation")


@fig("refraction-both-directions")
def _():
    f, axs = plt.subplots(1, 2, figsize=(11.2, 4.6))
    a1 = math.degrees(math.asin(1.5 * math.sin(rad(30))))  # 48.59
    for ax, (nsrc, ndst, a, from_top, ttl, lo, hi) in zip(
        axs,
        [
            (1.0, 1.5, a1, True, "из воздуха в стекло", "воздух", "стекло"),
            (1.5, 1.0, 30.0, False, "из стекла в воздух", "воздух", "стекло"),
        ],
    ):
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.2, 3.2)
        ax.set_aspect("equal")
        ax.axis("off")
        if from_top:
            halfplane(ax, (-3.6, 3.6), -3.2, 0, GLASS)
            n1, n2 = 1.0, 1.5
        else:
            halfplane(ax, (-3.6, 3.6), -3.2, 0, GLASS)
            n1, n2 = 1.0, 1.5
        o = np.array([0.0, 0.0])
        beta, q, nrm, src, dout = interface(ax, o, n1, n2, a, from_top=from_top, L=2.7, refl=False, arc_r=0.8)
        ax.set_title(ttl, fontsize=12.5, pad=4)
        text(ax, -3.4, 2.75, "воздух", size=11, ha="left", color=GREY)
        text(ax, -3.4, -2.75, "стекло, $n = 1{,}5$", size=11, ha="left", color=GREY)
        if from_top:
            text(ax, 0.3, 1.4, r"$\alpha=48{,}6^\circ$", size=12, color=RAY, ha="left")
            text(ax, -0.3, -1.5, r"$\beta=30^\circ$", size=12, color=RAY, ha="right")
            assert abs(beta - 30) < 1e-6
        else:
            text(ax, 0.3, -1.5, r"$\alpha=30^\circ$", size=12, color=RAY, ha="left")
            text(ax, -0.3, 1.4, r"$\beta=48{,}6^\circ$", size=12, color=RAY, ha="right")
            assert abs(beta - a1) < 1e-6
    f.tight_layout()
    save(f, "refraction-both-directions")


@fig("refraction-angle-graph")
def _():
    alpha = np.array([15, 30, 45, 60, 75], float)
    beta = np.array([10, 21, 30, 37, 41], float)
    n = 1.45
    ratios = np.sin(np.radians(alpha)) / np.sin(np.radians(beta))
    assert np.allclose(ratios, [1.49, 1.40, 1.41, 1.44, 1.47], atol=0.012)
    assert np.all(np.abs(ratios / n - 1) < 0.04)
    f, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.9))
    x = np.linspace(0, 90, 400)
    a1.plot(x, np.degrees(np.arcsin(np.sin(np.radians(x)) / n)), color=RAY, lw=2.4, label=r"закон Снеллиуса, $n_{21}=1{,}45$")
    a1.plot(x, x / 1.5, color=RAY2, lw=2.0, ls="--", label=r"гипотеза $\beta=\alpha/1{,}5$")
    a1.scatter(alpha, beta, s=55, color=INK, zorder=5, label="измерения")
    a1.set_xlim(0, 90)
    a1.set_ylim(0, 50)
    a1.set_xlabel(r"угол падения $\alpha$, град")
    a1.set_ylabel(r"угол преломления $\beta$, град")
    a1.set_xticks(range(0, 91, 15))
    a1.grid(color=GRID, lw=0.8)
    a1.legend(loc="upper left", frameon=False, fontsize=10)
    a1.set_title("Углы не пропорциональны", pad=6)
    s = np.linspace(0, 1, 50)
    a2.plot([0, 1.0], [0, 1.0 / n], color=RAY, lw=2.4, label=r"$\sin\alpha=1{,}45\,\sin\beta$")
    a2.scatter(np.sin(np.radians(alpha)), np.sin(np.radians(beta)), s=55, color=INK, zorder=5, label="измерения")
    for al, be in zip(alpha, beta):
        a2.annotate(f"{int(al)}°", (math.sin(rad(al)), math.sin(rad(be))), textcoords="offset points", xytext=(-16, 7), fontsize=9.5, color=GREY)
    a2.set_xlim(0, 1.02)
    a2.set_ylim(0, 0.75)
    a2.set_xlabel(r"$\sin\alpha$")
    a2.set_ylabel(r"$\sin\beta$")
    a2.grid(color=GRID, lw=0.8)
    a2.legend(loc="upper left", frameon=False, fontsize=10)
    a2.set_title("Синусы пропорциональны", pad=6)
    f.tight_layout()
    ru_axis(a1, a2)
    save(f, "refraction-angle-graph")


@fig("refraction-index-bars")
def _():
    names = ["вакуум", "воздух", "вода", "стекло", "алмаз"]
    lo = np.array([1.0, 1.0, 1.33, 1.4, 2.41])
    hi = np.array([1.0, 1.0, 1.33, 1.7, 2.41])
    f, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.0), sharey=True)
    y = np.arange(len(names))[::-1]
    for i, (yy, l, h) in enumerate(zip(y, lo, hi)):
        a1.barh(yy, l, color=BLUE, alpha=0.85, height=0.55)
        if h > l:
            a1.barh(yy, h - l, left=l, color=BLUE, alpha=0.4, height=0.55, hatch="//", ec=PAPER)
        lab = num(l, 2) if h == l else num(l, 1) + "–" + num(h, 1)
        if names[i] == "воздух":
            lab = "1,000…"
        if names[i] == "вакуум":
            lab = "1"
        a1.text(h + 0.04, yy, lab, va="center", fontsize=10.5)
        a2.barh(yy, 1 / h, color=GOLD, alpha=0.9, height=0.55)
        if h > l:
            a2.barh(yy, 1 / l - 1 / h, left=1 / h, color=GOLD, alpha=0.4, height=0.55, hatch="//", ec=PAPER)
        hi_s = num(1 / l, 2)
        lo_s = num(1 / h, 2)
        a2.text(1 / l + 0.02, yy, hi_s if h == l else f"{lo_s}–{hi_s}", va="center", fontsize=10.5)
    a1.set_yticks(y)
    a1.set_yticklabels(names)
    a1.set_xlim(0, 3.0)
    a2.set_xlim(0, 1.3)
    a1.set_title(r"Абсолютный показатель преломления $n=c/v$", fontsize=11.5, pad=6)
    a2.set_title(r"Скорость света в среде $v/c = 1/n$", fontsize=11.5, pad=6)
    for a in (a1, a2):
        a.grid(axis="x", color=GRID, lw=0.8)
        a.set_axisbelow(True)
    f.tight_layout()
    ru_axis(a1, a2, y=False)
    save(f, "refraction-index-bars")


@fig("refraction-cases-17-1")
def _():
    # Five boundary pictures of problem 17.1: which medium is optically denser.
    cases = [
        ("а", dict(n1=1.0, n2=1.5, a=50, top=True, rot=0), "$n_2>n_1$"),
        ("б", dict(n1=1.5, n2=1.0, a=25, top=True, rot=0), "$n_1>n_2$"),
        ("в", dict(n1=1.5, n2=1.0, a=45, top=False, rot=0), "$n_1>n_2$"),
        # г and д repeat the textbook figures on the board (frame U203 board-09-20)
        # г: the boundary is vertical, medium 1 on the left, the ray goes up and to the right, small angle in medium 1
        ("г", dict(n1=1.5, n2=1.0, a=33, top=True, rot=90, lab=((-1.6, 2.0), (1.6, -1.6))), "$n_1>n_2$"),
        # д: the boundary leans 23 degrees from the vertical, medium 1 on the right, the ray arrives from the upper right
        ("д", dict(n1=1.0, n2=1.5, a=60, top=True, rot=-113, lab=((1.5, 2.0), (-1.7, -1.5))), "$n_2>n_1$"),
    ]
    f, axs = plt.subplots(2, 3, figsize=(11.6, 7.4))
    axs = axs.flat
    for ax, (nm, p, res) in zip(axs, cases):
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.6, 2.6)
        ax.set_aspect("equal")
        ax.axis("off")
        o = np.array([0.0, 0.0])
        beta, q, nrm, src, dout = interface(ax, o, p["n1"], p["n2"], p["a"], from_top=p["top"], rot=p["rot"], L=2.0, refl=False, arc_r=0.6)
        up = vec(90 + p["rot"])
        pos1, pos2 = p.get("lab", (up * 1.6 + vec(p["rot"]) * 2.0, -up * 1.6 + vec(p["rot"]) * 2.0))
        text(ax, *pos1, "1", size=15, color=GREY)
        text(ax, *pos2, "2", size=15, color=GREY)
        a_val, b_val = p["a"], beta
        src_ang, out_ang = ang(src), ang(dout)
        # labels
        text(ax, *(o + vec(ang(nrm) + (p["a"] / 2 if p["top"] else -p["a"] / 2)) * 1.05), r"$\alpha$", size=13, color=RAY)
        text(ax, *(o + vec(ang(-nrm) + (-beta / 2 if p["top"] else beta / 2)) * 1.05), r"$\beta$", size=13, color=RAY)
        ax.set_title(f"{nm})  {res}", fontsize=13, pad=2)
    axs2 = f.axes[5]
    axs2.axis("off")
    axs2.set_xlim(0, 1)
    axs2.set_ylim(0, 1)
    axs2.text(0.03, 0.62, "Больше оптическая плотность —\nменьше угол с перпендикуляром", fontsize=12, va="center", ha="left")
    axs2.text(0.03, 0.22, "Рисунки построены для пары\n$n=1{,}0$ и $n=1{,}5$", fontsize=10.5, va="center", ha="left", color=GREY)
    f.tight_layout()
    save(f, "refraction-cases-17-1")


@fig("refraction-problem-17-3")
def _():
    alpha, phi = 40.0, 110.0
    beta = 180 - alpha - phi
    assert beta == 30.0
    n21 = math.sin(rad(alpha)) / math.sin(rad(beta))
    assert abs(n21 - 1.2856) < 1e-3
    f, ax = canvas(7.0, 5.6, (-3.6, 3.8), (-3.2, 3.2))
    halfplane(ax, (-3.6, 3.8), -3.2, 0, GLASS)
    o = np.array([0.0, 0.0])
    line(ax, (-3.4, 0), (3.6, 0), color=INK, lw=2)
    line(ax, (0, -2.9), (0, 2.9), color=GUIDE, lw=1.3, ls=(0, (5, 4)), z=2)
    ray(ax, o + vec(90 + alpha) * 2.8, o, color=RAY)
    ray(ax, o, o + vec(90 - alpha) * 2.8, color=RAY)
    ray(ax, o, o + vec(-90 + beta) * 2.8, color=RAY)
    arc(ax, o, 90, 90 + alpha, 0.85, r"$\alpha$", color=RAY, lab_r=1.15)
    arc(ax, o, 90, 90 - alpha, 0.85, r"$\alpha$", color=RAY, lab_r=1.15)
    arc(ax, o, -90, -90 + beta, 0.85, r"$\beta$", color=RAY, lab_r=1.15)
    arc(ax, o, 90 - alpha, -90 + beta, 1.55, r"$\varphi$", color=RAY2, lab_r=1.9, n=1)
    text(ax, -3.4, 2.75, "среда 1", size=11, ha="left", color=GREY)
    text(ax, -3.4, -2.75, "среда 2", size=11, ha="left", color=GREY)
    text(ax, 2.05, 2.6, "отражённый", size=10, color=GREY)
    text(ax, -2.0, 2.6, "падающий", size=10, color=GREY)
    f.tight_layout()
    save(f, "refraction-problem-17-3")


@fig("refraction-mug-coin")
def _():
    n, gam = 4 / 3, 30.0  # sight line 30 degrees below horizontal
    W, Hh, wl = 10.0, 8.0, 6.0  # mug width, height, water level
    a_air = 90 - gam  # incidence angle in air (from vertical normal)
    b_w = deg(math.asin(math.sin(rad(a_air)) / n))
    snell_check(1.0, a_air, n, b_w)
    # sight line from the rim (0, Hh) going down-right at gam below horizontal: y = Hh - x tan(gam)
    x_surf = (Hh - wl) / math.tan(rad(gam))
    coin_x = x_surf + wl * 0 + (wl - 0.3) * math.tan(rad(b_w))
    eye_p = np.array([-3.0, Hh + 3.0 * math.tan(rad(gam))])
    f, axs = plt.subplots(1, 2, figsize=(11.6, 4.9))
    for k, ax in enumerate(axs):
        ax.set_xlim(-4.6, 11.2)
        ax.set_ylim(-0.8, 10.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if k == 1:
            halfplane(ax, (0, W), 0, wl, WATER, z=1)
            line(ax, (0, wl), (W, wl), color=BLUE, lw=1.6, z=3)
            text(ax, 9.2, 5.2, "вода", size=11, color=BLUE)
        line(ax, (0, Hh), (0, 0), color=INK, lw=3)
        line(ax, (0, 0), (W, 0), color=INK, lw=3)
        line(ax, (W, 0), (W, Hh), color=INK, lw=3)
        ax.add_patch(Ellipse((coin_x, 0.3), 0.9, 0.3, fc=GOLD, ec=INK, lw=1.2, zorder=4))
        eye(ax, eye_p[0] - 0.3, eye_p[1] + 0.15, s=0.42)
        if k == 0:
            y_hit = Hh - W * math.tan(rad(gam))
            assert y_hit > 1.0 and coin_x > 6
            ray(ax, eye_p, np.array([W, y_hit]), color=RAY, f=0.5)
            ax.plot([W], [y_hit], "o", color=RAY, zorder=7)
            text(ax, 5.0, 10.0, "без воды взгляд упирается в стенку", size=11)
            text(ax, coin_x - 0.05, -0.55, "монета", size=10, color=GREY)
        else:
            top = np.array([x_surf, wl])
            q = np.array([coin_x, 0.3])
            ray(ax, q, top, color=RAY, f=0.5)
            ray(ax, top, eye_p, color=RAY, f=0.55)
            line(ax, (x_surf, wl - 2.1), (x_surf, wl + 1.9), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
            arc(ax, top, 90, 90 + a_air, 1.1, r"$\alpha$", color=RAY, lab_r=1.45)
            arc(ax, top, -90, -90 + b_w, 1.1, None, color=RAY)
            text(ax, x_surf + 0.45, wl - 1.4, r"$\beta$", size=12, color=RAY)
            text(ax, 5.0, 10.0, "с водой луч от монеты доходит до глаза", size=11)
            # check geometry of the drawn ray against Snell
            d_w = (top - q) / np.linalg.norm(top - q)
            d_a = (eye_p - top) / np.linalg.norm(eye_p - top)
            assert abs(inc_angle(d_w, np.array([0, 1.0])) - b_w) < 1e-6
            assert abs(inc_angle(d_a, np.array([0, 1.0])) - a_air) < 1e-6
            assert eye_p[1] > Hh and Hh - 0 > 0
    f.tight_layout()
    save(f, "refraction-mug-coin")


@fig("refraction-kirik-5")
def _():
    n = 1.33
    h = 4.0
    f, ax = canvas(10.4, 5.6, (-10.6, 1.4), (-4.4, 4.6))
    halfplane(ax, (-10.6, 1.4), -4.4, 0, WATER)
    line(ax, (-10.4, 0), (1.2, 0), color=INK, lw=2)
    S = np.array([0.0, h])
    text(ax, 0.0, h + 0.3, "источник", size=10.5, color=GREY)
    ax.plot([0], [h], "o", color=GOLD, ms=9, zorder=7)
    text(ax, -10.3, 0.4, "воздух", size=11, ha="left", color=GREY)
    text(ax, -10.3, -0.45, "вода", size=11, ha="left", color=BLUE)
    cols = {60: RAY2, 30: RAY}
    for a, col in cols.items():
        p = np.array([-h * math.tan(rad(a)), 0.0])
        d_in = (p - S) / np.linalg.norm(p - S)
        d_out = refract(d_in, np.array([0, 1.0]), 1.0, n)
        b = inc_angle(d_out, np.array([0, 1.0]))
        snell_check(1.0, a, n, b)
        line(ax, p - np.array([0, 1.0]) * 0 + np.array([0, 1.4]), p - np.array([0, 2.6]), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
        ray(ax, S, p, color=col, f=0.5)
        ray(ax, p, p + d_out * 3.3, color=col, f=0.45)
        arc(ax, p, 90, ang(-d_in), 1.0, rf"$\alpha={a}^\circ$", color=col, lab_r=1.75, fs=10.5)
        # the beta label sits beside the normal, outside the narrow angle, so that the refracted ray does not cross it
        arc(ax, p, -90, ang(d_out), 1.0, None, color=col)
        text(ax, p[0] + 1.25, -1.55, rf"$\beta={num(b, 1, math=True)}^\circ$", size=10.5, color=col)
    f.tight_layout()
    save(f, "refraction-kirik-5")


def _apparent(n, H, alpha_deg, ye):
    a = rad(alpha_deg)
    xs = H * math.tan(a)
    b = math.asin(n * math.sin(a))
    x_eye = xs + ye * math.tan(b)
    h_app = xs / math.tan(b)
    return xs, deg(b), x_eye, h_app


@fig("refraction-apparent-depth-eyes")
def _():
    n, H = 4 / 3, 4.0
    xs, b, xe, h_app = _apparent(n, H, 10.0, 1.6)
    assert abs(h_app - H / n) < 0.05
    f, ax = canvas(7.4, 6.4, (-2.4, 2.4), (-H - 0.8, 2.6))
    halfplane(ax, (-2.4, 2.4), -H - 0.3, 0, WATER)
    line(ax, (-2.3, 0), (2.3, 0), color=BLUE, lw=1.6)
    line(ax, (-2.3, -H - 0.3), (2.3, -H - 0.3), color=INK, lw=2.4)
    ax.plot([0], [-H], "o", color=RAY2, ms=10, zorder=8)
    for sgn in (-1, 1):
        P = np.array([sgn * xs, 0.0])
        E = np.array([sgn * xe, 1.6])
        ray(ax, np.array([0, -H]), P, color=RAY, f=0.5)
        ray(ax, P, E, color=RAY, f=0.55)
        line(ax, P, np.array([0, -h_app]), color=GREY, lw=1.5, ls=(0, (5, 4)), z=3)
        eye(ax, E[0] + sgn * 0.0, E[1] + 0.25, s=0.3)
        d_w = (P - np.array([0, -H])) / np.linalg.norm(P - np.array([0, -H]))
        d_a = (E - P) / np.linalg.norm(E - P)
        snell_check(n, inc_angle(d_w, np.array([0, 1.0])), 1.0, inc_angle(d_a, np.array([0, 1.0])))
    ax.plot([0], [-h_app], "o", mfc=PAPER, mec=GREY, mew=2, ms=10, zorder=8)
    ax.annotate("", (-1.85, -h_app), (-1.85, 0), arrowprops=dict(arrowstyle="<->", color=SPECIAL, lw=1.6))
    ax.annotate("", (-2.15, -H), (-2.15, 0), arrowprops=dict(arrowstyle="<->", color=VIOLET, lw=1.6))
    text(ax, -1.66, -h_app / 2, r"$h$", size=14, color=SPECIAL, ha="left")
    text(ax, -2.3, -H / 2, r"$H$", size=14, color=VIOLET, ha="right")
    text(ax, 0.22, -H - 0.05, "предмет", size=10.5, ha="left", color=RAY2)
    text(ax, 0.22, -h_app + 0.05, "кажется здесь", size=10.5, ha="left", color=GREY)
    text(ax, 1.75, -2.1, "вода", size=11.5, color=BLUE)
    text(ax, 1.9, 0.3, "воздух", size=11, color=GREY)
    f.tight_layout()
    save(f, "refraction-apparent-depth-eyes")


@fig("refraction-apparent-depth-triangles")
def _():
    n, H = 4 / 3, 4.0
    xs, b, xe, h_app = _apparent(n, H, 12.0, 1.7)
    al = 12.0
    assert abs(xs / H - math.tan(rad(al))) < 1e-9
    assert abs(xs / h_app - math.tan(rad(b))) < 1e-9
    f, ax = canvas(7.6, 6.6, (-1.9, 3.4), (-H - 0.8, 2.8))
    halfplane(ax, (-1.9, 3.4), -H - 0.3, 0, WATER)
    line(ax, (-1.8, 0), (3.3, 0), color=BLUE, lw=1.6)
    line(ax, (-1.8, -H - 0.3), (3.3, -H - 0.3), color=INK, lw=2.4)
    O = np.array([0.0, -H])
    P = np.array([xs, 0.0])
    E2 = np.array([xe, 1.7])
    A = np.array([0.0, -h_app])
    ax.plot(*O, "o", color=RAY2, ms=10, zorder=8)
    ray(ax, O, np.array([0, 1.7]), color=GREY, lw=1.6, f=0.6)
    eye(ax, 0, 1.95, s=0.3)
    ray(ax, O, P, color=RAY, f=0.5)
    ray(ax, P, E2, color=RAY, f=0.55)
    eye(ax, E2[0] + 0.05, E2[1] + 0.25, s=0.3)
    line(ax, P, A, color=GREY, lw=1.5, ls=(0, (5, 4)), z=3)
    line(ax, (xs, -2.2), (xs, 1.5), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    line(ax, (0, 0), P, color=SPECIAL, lw=3, z=4)
    text(ax, xs / 2, 0.22, r"$x$", size=13, color=SPECIAL)
    arc(ax, O, 90, ang(P - O), 1.1, r"$\alpha$", color=RAY, lab_r=1.45, fs=12)
    arc(ax, A, 90, ang(P - A), 0.9, r"$\beta$", color=RAY, lab_r=1.2, fs=12)
    arc(ax, P, 90, ang(E2 - P), 0.9, r"$\beta$", color=RAY, lab_r=1.3, fs=12)
    arc(ax, P, -90, ang(O - P), 0.9, r"$\alpha$", color=RAY, lab_r=1.3, fs=12)
    ax.annotate("", (-1.0, -H), (-1.0, 0), arrowprops=dict(arrowstyle="<->", color=VIOLET, lw=1.6))
    ax.annotate("", (-0.5, -h_app), (-0.5, 0), arrowprops=dict(arrowstyle="<->", color=SPECIAL, lw=1.6))
    text(ax, -1.15, -H / 2, r"$H$", size=14, color=VIOLET, ha="right")
    text(ax, -0.65, -h_app / 2, r"$h$", size=14, color=SPECIAL, ha="right")
    text(ax, 2.6, -2.2, "вода", size=11.5, color=BLUE)
    text(ax, 2.6, 0.3, "воздух", size=11, color=GREY)
    f.tight_layout()
    save(f, "refraction-apparent-depth-triangles")


@fig("refraction-small-angles")
def _():
    x = np.linspace(0.01, 20, 400)
    s, t, r = np.sin(np.radians(x)), np.tan(np.radians(x)), np.radians(x)
    f, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.6))
    a1.plot(x, r, color=GREY, lw=1.8, ls=":", label=r"$x$ (в радианах)")
    a1.plot(x, t, color=RAY2, lw=2.2, label=r"$\operatorname{tg}\,x$")
    a1.plot(x, s, color=RAY, lw=2.2, label=r"$\sin x$")
    a1.set_xlabel("угол $x$, град")
    a1.set_xlim(0, 20)
    a1.set_ylim(0, 0.4)
    a1.legend(frameon=False, loc="upper left")
    a1.grid(color=GRID, lw=0.8)
    a1.set_title("Кривые сливаются при малых углах", pad=6)
    err = (t / s - 1) * 100
    a2.plot(x, err, color=INK, lw=2.3)
    e5 = (math.tan(rad(5)) / math.sin(rad(5)) - 1) * 100
    e1 = (math.tan(rad(1)) / math.sin(rad(1)) - 1) * 100
    assert abs(math.sin(rad(1)) - 0.017452406) < 1e-9 and abs(math.tan(rad(1)) - 0.017455065) < 1e-8
    a2.axvline(5, color=RAY2, lw=1.4, ls="--")
    a2.scatter([5], [e5], color=RAY2, zorder=5)
    a2.annotate(rf"$5^\circ$: {num(e5, 2)}" + " %", (5, e5), xytext=(6.2, e5 + 1.3), fontsize=11, color=RAY2)
    a2.set_xlim(0, 20)
    a2.set_ylim(0, 6.2)
    a2.set_xlabel("угол $x$, град")
    a2.set_ylabel(r"$(\operatorname{tg}x/\sin x-1)\cdot 100\,\%$")
    a2.grid(color=GRID, lw=0.8)
    a2.set_title(r"Расхождение $\operatorname{tg}x$ и $\sin x$", pad=6)
    f.tight_layout()
    ru_axis(a1, a2)
    save(f, "refraction-small-angles")


@fig("refraction-glass-air-deviation")
def _():
    n, a = 1.5, 30.0
    b = deg(math.asin(n * math.sin(rad(a))))
    phi = b - a
    assert abs(b - 48.59) < 0.01 and abs(phi - 18.59) < 0.01
    f, ax = canvas(7.6, 5.8, (-3.6, 4.0), (-3.2, 3.3))
    halfplane(ax, (-3.6, 4.0), 0, 3.3, GLASS)
    o = np.array([0.0, 0.0])
    line(ax, (-3.5, 0), (3.9, 0), color=INK, lw=2)
    line(ax, (0, -2.9), (0, 2.9), color=GUIDE, lw=1.3, ls=(0, (5, 4)), z=2)
    # light goes from glass (above) into air (below): incident from upper left
    inc = vec(90 + a)
    ray(ax, o + inc * 3.0, o, color=RAY)
    ray(ax, o, o + vec(-90 + b) * 3.0, color=RAY)
    ray(ax, o, o + vec(-90 + a) * 3.0, color=GREY, ls="--", lw=1.8, arrow=False)
    arc(ax, o, 90, 90 + a, 0.9, r"$\alpha$", color=RAY, lab_r=1.25)
    arc(ax, o, -90, -90 + b, 0.9, r"$\beta$", color=RAY, lab_r=1.25)
    arc(ax, o, -90 + a, -90 + b, 2.0, r"$\varphi$", color=RAY2, lab_r=2.35, fs=13)
    arc(ax, o, -90, -90 + a, 1.45, r"$\alpha$", color=GREY, lab_r=1.75)
    text(ax, -3.4, 2.75, "стекло, $n=1{,}5$", size=11, ha="left", color=GREY)
    text(ax, -3.4, -2.75, "воздух", size=11, ha="left", color=GREY)
    text(ax, 1.2, -2.85, "без преломления", size=9.5, color=GREY, ha="left")
    f.tight_layout()
    save(f, "refraction-glass-air-deviation")


@fig("refraction-shadow-pole")
def _():
    n, al, hp, D = 4 / 3, 60.0, 1.0, 1.7
    b = deg(math.asin(math.sin(rad(al)) / n))
    L = hp * math.tan(rad(b))
    L_formula = hp * math.sin(rad(al)) / math.sqrt(n * n - math.sin(rad(al)) ** 2)
    assert abs(L - L_formula) < 1e-9 and abs(L - 3 * math.sqrt(3) / math.sqrt(37)) < 1e-9 and abs(L - 0.854) < 1e-3
    f, ax = canvas(9.6, 5.4, (-3.4, 3.6), (-0.6, 3.6))
    halfplane(ax, (-3.4, 3.6), 0, D, WATER)
    line(ax, (-3.3, D), (3.5, D), color=BLUE, lw=1.6)
    line(ax, (-3.3, 0), (3.5, 0), color=INK, lw=2.6)
    pole_x = 0.0
    line(ax, (pole_x, 0), (pole_x, hp), color=INK, lw=6, z=4)
    T = np.array([pole_x, hp])
    d_w = vec(-90 + b)
    Q = np.array([T[0] - d_w[0] * (D - hp) / (-d_w[1]), D])
    ground = T + d_w * (hp / (-d_w[1]))
    assert abs(ground[0] - pole_x - L) < 1e-9
    src = Q + vec(90 + al) * 2.6
    ray(ax, src, Q, color=RAY, f=0.5)
    ray(ax, Q, ground, color=RAY, f=0.3)
    line(ax, (Q[0], D - 1.3), (Q[0], D + 1.2), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    ax.add_patch(Polygon([[pole_x, 0], [ground[0], 0], [pole_x, hp]], fc=tint(INK, 0.45), ec="none", alpha=0.35, zorder=3, hatch="///"))
    arc(ax, Q, 90, 90 + al, 0.75, r"$\alpha$", color=RAY, lab_r=1.05)
    arc(ax, Q, -90, ang(d_w), 0.75, r"$\beta$", color=RAY, lab_r=0.98)
    line(ax, (pole_x, hp), (pole_x, hp + 0.55), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    arc(ax, T, 90, ang(-d_w), 0.42, r"$\beta$", color=RAY, lab_r=0.62, fs=11)
    ax.annotate("", (pole_x - 0.22, hp), (pole_x - 0.22, 0), arrowprops=dict(arrowstyle="<->", color=VIOLET, lw=1.5))
    text(ax, pole_x - 0.4, hp / 2, r"$h$", size=13, color=VIOLET, ha="right")
    text(ax, ground[0] + 0.12, 0.2, "тень", size=11, color=GREY, ha="left")
    ax.annotate("", (ground[0], -0.22), (pole_x, -0.22), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
    text(ax, ground[0] / 2, -0.42, r"$l$", size=13)
    text(ax, 2.6, 1.2, "вода", size=11, color=BLUE)
    text(ax, 2.6, 2.3, "воздух", size=11, color=GREY)
    text(ax, -2.4, 3.3, "лучи Солнца", size=10.5, color=RAY)
    f.tight_layout()
    save(f, "refraction-shadow-pole")


@fig("refraction-lamp-shadow")
def _():
    H, h = 4.5, 1.5
    x1, d, l1, l2 = 2.0, 1.0, 1.0, 1.5
    x2 = x1 + d
    assert abs(H / (x1 + l1) - h / l1) < 1e-9 and abs(H / (x2 + l2) - h / l2) < 1e-9
    assert abs(H - h * (1 + d / (l2 - l1))) < 1e-9
    f, (a1, a2) = plt.subplots(1, 2, figsize=(11.8, 4.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
    # left: lamp frame
    ax = a1
    ax.set_xlim(-0.7, 5.6)
    ax.set_ylim(-0.8, 5.3)
    ax.set_aspect("equal")
    ax.axis("off")
    line(ax, (-0.4, 0), (5.3, 0), color=INK, lw=2.4)
    lamp = np.array([0.0, H])
    ax.plot(*lamp, "o", color=GOLD, ms=13, zorder=8)
    for x, l, col, ls in ((x1, l1, BLUE, "--"), (x2, l2, RAY2, "-")):
        line(ax, (x, 0), (x, h), color=col, lw=5, ls="-", z=4)
        tip = np.array([x + l, 0.0])
        line(ax, lamp, tip, color=RAY, lw=1.6, z=3)
        line(ax, (x, 0), tip, color=col, lw=4, z=3, alpha=0.6)
    text(ax, -0.2, H / 2, r"$H$", size=14, color=INK, ha="right")
    ax.annotate("", (0.0, 0.1), (0.0, H - 0.25), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    text(ax, x1 - 0.17, h / 2, r"$h$", size=12, color=BLUE, ha="right")
    text(ax, x2 + 0.15, h / 2 + 0.25, r"$h$", size=12, color=RAY2, ha="left")
    text(ax, x1 + l1 / 2, -0.35, r"$l_1$", size=12, color=BLUE)
    text(ax, x2 + l2 / 2, -0.35, r"$l_2$", size=12, color=RAY2)
    ax.annotate("", (x2, 0.55), (x1, 0.55), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    text(ax, x1 + 0.3, 0.3, r"$d$", size=12)  # below the arrow, clear of the lamp ray to the tip at x1 + l1
    ax.set_title("Фонарь неподвижен, шест переносят", fontsize=11.5, pad=4)
    # right: pole frame
    ax = a2
    ax.set_xlim(-3.6, 2.2)
    ax.set_ylim(-0.8, 5.3)
    ax.set_aspect("equal")
    ax.axis("off")
    line(ax, (-3.4, 0), (2.0, 0), color=INK, lw=2.4)
    line(ax, (0, 0), (0, h), color=INK, lw=5, z=4)
    T = np.array([0.0, h])
    lamps = [np.array([-x1, H]), np.array([-x2, H])]
    for lp, l, col in zip(lamps, (l1, l2), (BLUE, RAY2)):
        ax.plot(*lp, "o", color=GOLD, ms=11, zorder=8, mec=col, mew=2)
        line(ax, lp, np.array([l, 0.0]), color=RAY, lw=1.6, z=3)
        assert abs(cross(np.array([l, 0.0]) - lp, T - lp)) < 1e-9
    line(ax, lamps[1], lamps[0], color=INK, lw=2, z=6)
    text(ax, -(x1 + x2) / 2, H + 0.3, r"$d$", size=12)
    line(ax, (-3.3, h), (0.0, h), color=GREY, lw=1, ls=(0, (3, 3)), z=2)
    ax.annotate("", (-3.2, H), (-3.2, h), arrowprops=dict(arrowstyle="<->", color=VIOLET, lw=1.4))
    text(ax, -3.3, (H + h) / 2, r"$H-h$", size=11, color=VIOLET, ha="right")
    ax.annotate("", (l2, -0.35), (l1, -0.35), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    text(ax, (l1 + l2) / 2, -0.62, r"$l_2-l_1$", size=11)
    text(ax, 0.17, h / 2, r"$h$", size=12, ha="left")
    ax.set_title("В системе шеста фонарь переносят", fontsize=11.5, pad=4)
    f.tight_layout()
    save(f, "refraction-lamp-shadow")


@fig("refraction-plate")
def _():
    n1, n2, a1 = 1.0, 1.5, 50.0
    t = 2.4  # plate thickness in figure units
    f, ax = canvas(9.2, 6.2, (-4.0, 5.4), (-t - 2.2, 2.6))
    halfplane(ax, (-4.0, 5.4), -t, 0, GLASS)
    line(ax, (-4.0, 0), (5.4, 0), color=INK, lw=2)
    line(ax, (-4.0, -t), (5.4, -t), color=INK, lw=2)
    O1 = np.array([0.0, 0.0])
    d0 = vec(-90 + a1)
    p_in = O1 - d0 * 2.8
    d1 = refract(d0, np.array([0, 1.0]), n1, n2)
    b1 = inc_angle(d1, np.array([0, 1.0]))
    O2 = O1 + d1 * (t / -d1[1])
    d2 = refract(d1, np.array([0, 1.0]), n2, n1)
    b2 = inc_angle(d2, np.array([0, 1.0]))
    snell_check(n1, a1, n2, b1)
    snell_check(n2, b1, n1, b2)
    assert abs(b2 - a1) < 1e-9 and abs(ang(d2) - ang(d0)) < 1e-9
    ray(ax, p_in, O1, color=RAY, f=0.5)
    ray(ax, O1, O2, color=RAY, f=0.5)
    end = O2 + d2 * 2.9
    ray(ax, O2, end, color=RAY, f=0.6)
    ray(ax, O1, O1 + d0 * 4.8, color=GREY, ls="--", lw=1.6, arrow=False)
    line(ax, O1 + np.array([0, 1.0]), O1 - np.array([0, t + 0.8]), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    line(ax, O2 + np.array([0, 0.8]), O2 - np.array([0, 1.0]), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    arc(ax, O1, 90, 90 + a1 * 1, 0.9, r"$\alpha_1$", color=RAY, lab_r=1.3)
    arc(ax, O1, -90, ang(d1), 0.9, r"$\beta_1$", color=RAY, lab_r=1.25)
    arc(ax, O2, 90, ang(-d1), 0.9, r"$\alpha_2$", color=RAY, lab_r=1.3)
    arc(ax, O2, -90, ang(d2), 0.9, r"$\beta_2$", color=RAY, lab_r=1.3)
    # shift delta: distance from O2 to the dashed continuation
    cont_pt = O1 + d0 * float(np.dot(O2 - O1, d0))
    delta = abs(cross(d0, O2 - O1))
    ax.annotate("", O2, cont_pt, arrowprops=dict(arrowstyle="<->", color=RAY2, lw=1.6))
    text(ax, (O2[0] + cont_pt[0]) / 2 + 0.3, (O2[1] + cont_pt[1]) / 2 - 0.05, r"$\delta$", size=14, color=RAY2, ha="left")
    text(ax, -3.8, 2.2, r"$n_1$", size=14, color=GREY, ha="left")
    text(ax, -3.8, -t - 1.9, r"$n_1$", size=14, color=GREY, ha="left")
    text(ax, -3.8, -t / 2, r"$n_2>n_1$", size=14, color=GREY, ha="left")
    f.tight_layout()
    save(f, "refraction-plate")


@fig("refraction-plate-problem")
def _():
    n, d, a = 1.5, 2.0, 60.0
    b = deg(math.asin(math.sin(rad(a)) / n))
    L = d / math.cos(rad(b))
    delta = d * math.sin(rad(a - b)) / math.cos(rad(b))
    assert abs(b - 35.26) < 0.01 and abs(delta - 1.0246) < 1e-3 and abs(L * math.sin(rad(a - b)) - delta) < 1e-9
    f, ax = canvas(8.8, 5.4, (-3.3, 4.6), (-d - 1.4, 1.9))
    halfplane(ax, (-3.3, 4.6), -d, 0, GLASS)
    line(ax, (-3.3, 0), (4.6, 0), color=INK, lw=2)
    line(ax, (-3.3, -d), (4.6, -d), color=INK, lw=2)
    O1 = np.array([0.0, 0.0])
    d0 = vec(-90 + a)
    d1 = refract(d0, np.array([0, 1.0]), 1.0, n)
    O2 = O1 + d1 * (d / -d1[1])
    d2 = refract(d1, np.array([0, 1.0]), n, 1.0)
    ray(ax, O1 - d0 * 2.0, O1, color=RAY, f=0.5)
    ray(ax, O1, O2, color=RAY, f=0.5)
    ray(ax, O2, O2 + d2 * 2.3, color=RAY, f=0.6)
    ray(ax, O1, O1 + d0 * 4.2, color=GREY, ls="--", lw=1.6, arrow=False)
    cont_pt = O1 + d0 * float(np.dot(O2 - O1, d0))
    line(ax, O2, cont_pt, color=RAY2, lw=2.2)
    right_mark(ax, cont_pt, ang(O2 - cont_pt), ang(O1 - cont_pt), s=0.22, color=RAY2)
    line(ax, (0, 0.6), (0, -d - 0.5), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    line(ax, (O2[0], -d + 0.6), (O2[0], -d - 0.7), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    line(ax, (0, -d), (O2[0], -d), color=INK, lw=1, z=3)
    line(ax, (0, 0), (0, -d), color=INK, lw=1.4, z=3)
    arc(ax, O1, 90, 90 + a, 0.7, r"$\alpha$", color=RAY, lab_r=1.0)
    arc(ax, O1, -90, ang(d1), 0.7, r"$\beta$", color=RAY, lab_r=1.0)
    arc(ax, O1, ang(d0), ang(d1), 1.25, r"$\alpha-\beta$", color=RAY2, lab_r=1.75, fs=10)
    text(ax, -0.25, -d / 2, r"$d$", size=13, ha="right")
    text(ax, O2[0] / 2 - 0.3, -d / 2 - 0.05, r"$l$", size=13)
    text(ax, (O2[0] + cont_pt[0]) / 2 + 0.25, (O2[1] + cont_pt[1]) / 2 + 0.05, r"$\delta$", size=14, color=RAY2, ha="left")
    text(ax, -3.1, 1.45, "воздух", size=11, ha="left", color=GREY)
    text(ax, -3.1, -d / 2, "стекло, $n=1{,}5$", size=11, ha="left", color=GREY)
    f.tight_layout()
    save(f, "refraction-plate-problem")


@fig("refraction-plate-shift-graph")
def _():
    n, d = 1.5, 2.0
    a = np.linspace(0, 90, 400)
    b = np.degrees(np.arcsin(np.sin(np.radians(a)) / n))
    dl = d * np.sin(np.radians(a - b)) / np.cos(np.radians(b))
    assert abs(dl[-1] - d) < 1e-9 and abs(dl[0]) < 1e-12 and np.all(np.diff(dl) >= 0)
    f, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.plot(a, dl, color=RAY, lw=2.5)
    ax.axhline(d, color=GREY, ls="--", lw=1.4)
    text(ax, 3, d + 0.07, "толщина пластинки $d$", size=10.5, ha="left", va="bottom", color=GREY)
    a60 = 60
    v60 = d * math.sin(rad(60 - math.degrees(math.asin(math.sin(rad(60)) / n)))) / math.cos(math.asin(math.sin(rad(60)) / n))
    ax.scatter([a60], [v60], color=RAY2, zorder=5, s=55)
    ax.annotate(rf"$60^\circ$: {num(v60, 2)} см", (a60, v60), xytext=(26, v60 + 0.45), fontsize=11, color=RAY2,
                arrowprops=dict(arrowstyle="-", color=RAY2))
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 2.4)
    ax.set_xticks(range(0, 91, 15))
    ax.set_xlabel(r"угол падения $\alpha$, град")
    ax.set_ylabel(r"смещение луча $\delta$, см")
    ax.grid(color=GRID, lw=0.8)
    ax.set_title(r"Смещение растёт до $d$ при $\alpha\to 90^\circ$", pad=6)
    f.tight_layout()
    ru_axis(ax)
    save(f, "refraction-plate-shift-graph")


def prism_path(phi, n, a1, s=0.55, H=5.0):
    """Ray through an isosceles prism with apex angle phi, apex up. Returns geometry and angles."""
    hp = rad(phi / 2)
    A = np.array([0.0, H])
    Bl = np.array([-H * math.tan(hp), 0.0])
    Br = np.array([H * math.tan(hp), 0.0])
    # left face: outward normal
    n_out_l = np.array([-math.cos(hp), math.sin(hp)])
    n_out_r = np.array([math.cos(hp), math.sin(hp)])
    n_in_l = -n_out_l
    P1 = A + (Bl - A) * s
    d0 = vec(ang(n_in_l) + a1)
    d1 = refract(d0, n_out_l, 1.0, n)
    b1 = inc_angle(d1, n_out_l)
    # intersection with right face
    t = seg_hit(P1, d1, A, Br)
    P2 = P1 + d1 * t
    a2 = inc_angle(d1, n_out_r)
    d2 = refract(d1, -n_out_r, n, 1.0)
    b2 = inc_angle(d2, n_out_r) if d2 is not None else None
    return dict(A=A, Bl=Bl, Br=Br, P1=P1, P2=P2, d0=d0, d1=d1, d2=d2, b1=b1, a2=a2, b2=b2, nl=n_out_l, nr=n_out_r)


@fig("refraction-prism")
def _():
    phi, n, a1 = 60.0, 1.5, 45.0
    g = prism_path(phi, n, a1)
    b1, a2, b2 = g["b1"], g["a2"], g["b2"]
    delta = abs(ang(g["d2"]) - ang(g["d0"]))
    assert abs(b1 - 28.13) < 0.01 and abs(a2 - (phi - b1)) < 1e-6 and abs(b2 - 52.4) < 0.05
    assert abs(delta - (a1 + b2 - phi)) < 1e-6
    snell_check(1.0, a1, n, b1)
    snell_check(n, a2, 1.0, b2)
    f, ax = canvas(9.6, 6.4, (-5.0, 6.0), (-0.7, 6.0))
    ax.add_patch(Polygon([g["Bl"], g["A"], g["Br"]], closed=True, fc=GLASS, ec=INK, lw=2.2, zorder=2))
    P1, P2 = g["P1"], g["P2"]
    ray(ax, P1 - g["d0"] * 3.0, P1, color=RAY, f=0.5)
    ray(ax, P1, P2, color=RAY, f=0.5)
    end = P2 + g["d2"] * 3.6
    ray(ax, P2, end, color=RAY, f=0.6)
    # the incident direction continued, and the emerging ray traced back, meet at X
    den = cross(g["d0"], g["d2"])
    s_x = cross(P2 - P1, g["d2"]) / den
    X = P1 + g["d0"] * s_x
    ray(ax, P1, X + g["d0"] * 2.2, color=GREY, ls="--", lw=1.7, arrow=False)
    ray(ax, P2, X, color=GREY, ls="--", lw=1.7, arrow=False)
    for P, nrm in ((P1, g["nl"]), (P2, g["nr"])):
        line(ax, P - nrm * 1.3, P + nrm * 1.3, color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=3)
    arc(ax, P1, ang(g["nl"]), ang(-g["d0"]), 0.9, r"$\alpha_1$", color=RAY, lab_r=1.3)
    arc(ax, P1, ang(-g["nl"]), ang(g["d1"]), 0.9, r"$\beta_1$", color=RAY, lab_r=1.3)
    arc(ax, P2, ang(-g["nr"]), ang(-g["d1"]), 0.9, r"$\alpha_2$", color=RAY, lab_r=1.3)
    arc(ax, P2, ang(g["nr"]), ang(g["d2"]), 0.9, r"$\beta_2$", color=RAY, lab_r=1.3)
    arc(ax, X, ang(g["d0"]), ang(g["d2"]), 1.6, r"$\delta$", color=RAY2, lab_r=2.0, fs=14)
    arc(ax, g["A"], -90 - phi / 2, -90 + phi / 2, 0.85, r"$\varphi$", color=INK, lab_r=1.2, fs=13)
    text(ax, -3.8, 5.3, r"$n_1$", size=14, color=GREY)
    text(ax, 0, 1.0, r"$n_2>n_1$", size=13, color=GREY)
    f.tight_layout()
    save(f, "refraction-prism")


@fig("refraction-prism-deviation")
def _():
    def dev(phi, n, a1):
        hp = phi
        b1 = math.asin(math.sin(rad(a1)) / n)
        a2 = rad(phi) - b1
        s = n * math.sin(a2)
        if abs(s) > 1:
            return float("nan")
        return a1 + deg(math.asin(s)) - phi

    a = np.linspace(0.1, 89.9, 1500)
    f, ax = plt.subplots(figsize=(8.2, 4.9))
    sets = [(45, 1.5, RAY, r"$\varphi=45^\circ,\ n=1{,}5$"), (60, 1.5, RAY2, r"$\varphi=60^\circ,\ n=1{,}5$"), (45, 1.6, BLUE, r"$\varphi=45^\circ,\ n=1{,}6$")]
    mins = []
    for phi, n, col, lab in sets:
        d = np.array([dev(phi, n, x) for x in a])
        ok = ~np.isnan(d)
        ax.plot(a[ok], d[ok], color=col, lw=2.4, label=lab)
        i = np.nanargmin(d)
        a_sym = deg(math.asin(n * math.sin(rad(phi / 2))))
        assert abs(a[i] - a_sym) < 0.2, (a[i], a_sym)
        ax.scatter([a[i]], [d[i]], color=col, zorder=5, s=45)
        mins.append((phi, n, d[i]))
    # larger phi and larger n both raise the minimum deviation
    d45, d60, d45b = mins[0][2], mins[1][2], mins[2][2]
    assert d60 > d45 and d45b > d45
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 70)
    ax.set_xlabel(r"угол падения на первую грань $\alpha_1$, град")
    ax.set_ylabel(r"угол отклонения $\delta$, град")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper center", fontsize=10.5)
    ax.set_title("Минимум отклонения — при симметричном ходе луча", pad=6, fontsize=11.5)
    f.tight_layout()
    ru_axis(ax)
    save(f, "refraction-prism-deviation")


@fig("refraction-brewster")
def _():
    n = math.sqrt(2)
    a = deg(math.atan(n))
    b = deg(math.asin(math.sin(rad(a)) / n))
    assert abs(a + b - 90) < 1e-9 and abs(a - 54.7356) < 1e-3
    f, ax = canvas(7.2, 5.4, (-3.5, 3.9), (-3.2, 3.2))
    halfplane(ax, (-3.5, 3.9), -3.2, 0, WATER)
    o = np.array([0.0, 0.0])
    beta, q, nrm, src, dout = interface(ax, o, 1.0, n, a, L=2.8, refl=False, arc_r=0.8)
    ray(ax, o, o + vec(90 - a) * 2.8, color=RAY2, f=0.55)
    right_mark(ax, o, 90 - a, -90 + b, s=0.4, color=RAY2)
    text(ax, -0.5, 1.35, r"$\alpha^{*}$", size=14, color=RAY)
    text(ax, 0.55, 1.45, r"$\alpha^{*}$", size=14, color=RAY2)
    text(ax, 0.3, -1.35, r"$\beta^{*}$", size=14, color=RAY)
    text(ax, 1.35, -0.35, r"$90^\circ$", size=12, color=RAY2)
    text(ax, -3.3, 2.75, r"$n_1=1$", size=12, ha="left", color=GREY)
    text(ax, -3.3, -2.75, r"$n_2=\sqrt{2}$", size=12, ha="left", color=GREY)
    f.tight_layout()
    save(f, "refraction-brewster")


@fig("refraction-lab-setup")
def _():
    # Top view: paper with two parallel lines, the plate on it, the eye looking along the line.
    n = 1.56
    a = 40.0
    t = 3.0
    # work in the plate frame (faces horizontal), then turn everything so that the lines run left to right
    rot = 90 - a
    Rm = lambda v: np.array([math.cos(rad(rot)) * v[0] - math.sin(rad(rot)) * v[1], math.sin(rad(rot)) * v[0] + math.cos(rad(rot)) * v[1]])
    d0 = vec(-90 + a)
    O1 = np.array([0.0, 0.0])
    d1 = refract(d0, np.array([0, 1.0]), 1.0, n)
    O2 = O1 + d1 * (t / -d1[1])
    d2 = refract(d1, np.array([0, 1.0]), n, 1.0)
    assert abs(ang(d2) - ang(d0)) < 1e-9
    h = abs(cross(d0, O2 - O1))
    f, ax = canvas(10.4, 5.6, (-5.6, 8.6), (-4.9, 4.0))
    ax.add_patch(Rectangle((-5.5, -4.8), 14.0, 8.7, fc=tint(INK, 0.96), ec=GUIDE, lw=1.2, zorder=0))
    plate = [Rm(np.array(v, float)) for v in [(-3.0, 0), (3.0, 0), (3.0, -t), (-3.0, -t)]]
    ax.add_patch(Polygon(plate, closed=True, fc=GLASS, ec="none", zorder=1, alpha=0.9))
    line(ax, Rm(np.array([-3.0, 0])), Rm(np.array([3.0, 0])), color=RED, lw=1.8, z=2)
    line(ax, Rm(np.array([-3.0, -t])), Rm(np.array([3.0, -t])), color=RED, lw=1.8, z=2)
    p_a, q_a = Rm(O1 - d0 * 3.4), Rm(O1)
    p_b, q_b = Rm(O2), Rm(O2 + d2 * 3.4)
    ray(ax, p_a, q_a, color=INK, lw=1.8, f=0.5)
    ray(ax, q_a, p_b, color=RAY, lw=1.8, f=0.5)
    ray(ax, p_b, q_b, color=INK, lw=1.8, f=0.5)
    cont = O1 + d0 * float(np.dot(O2 - O1, d0))
    ray(ax, Rm(O1), Rm(cont + d0 * 1.2), color=GREY, ls="--", lw=1.4, arrow=False)
    eye(ax, *Rm(O2 + d2 * 4.3), s=0.36)
    ax.annotate("", Rm(O2), Rm(cont), arrowprops=dict(arrowstyle="<->", color=RAY2, lw=1.6))
    mid = (Rm(O2) + Rm(cont)) / 2
    text(ax, mid[0] + 0.75, mid[1], r"$h$", size=14, color=RAY2)  # behind the second face, which passes right of the arrow
    text(ax, *(Rm(O1 - d0 * 1.7) + np.array([0, 0.45])), "первая линия", size=10.5, color=GREY)
    text(ax, *(Rm(O2 + d2 * 2.2) + np.array([0, 0.45])), "вторая линия", size=10.5, color=GREY)
    text(ax, *Rm(np.array([-1.3, -1.8])), "пластинка,\n$n=?$", size=11.5, color=GREY)  # left of the refracted ray
    text(ax, *(Rm(np.array([-3.0, 0.0])) + np.array([-0.9, 0.35])), "грани\nпластинки", size=10, color=RED)
    f.tight_layout()
    save(f, "refraction-lab-setup")


@fig("refraction-lab-construction")
def _():
    # Construction of d1 and d2 with a compass: a circle around the point of incidence.
    d1v, d2v = 32.0, 20.5
    R = 50.0
    sa, sb = d1v / R, d2v / R
    a, b = deg(math.asin(sa)), deg(math.asin(sb))
    n = d1v / d2v
    assert abs(math.sin(rad(a)) / math.sin(rad(b)) - n) < 1e-9 and abs(n - 1.5610) < 1e-3
    f, ax = canvas(9.4, 7.4, (-62, 62), (-62, 62))
    ax.add_patch(Circle((0, 0), R, fc="none", ec=GREY, lw=1.3, ls=(0, (5, 4)), zorder=2))
    halfplane(ax, (-62, 62), -62, 0, GLASS, z=0)
    line(ax, (-60, 0), (60, 0), color=RED, lw=2.0, z=3)
    line(ax, (0, -58), (0, 58), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
    Pi = vec(90 + a) * R
    Pr = vec(-90 + b) * R
    ray(ax, Pi * 1.18, np.array([0, 0]), color=RAY, f=0.45)
    ray(ax, np.array([0, 0]), Pr * 1.18, color=RAY, f=0.5)
    foot_i = np.array([0.0, Pi[1]])
    foot_r = np.array([0.0, Pr[1]])
    line(ax, Pi, foot_i, color=RAY2, lw=2.4, z=6)
    line(ax, Pr, foot_r, color=BLUE, lw=2.4, z=6)
    right_mark(ax, foot_i, 180, -90, s=3.5, color=INK)
    right_mark(ax, foot_r, 180, 90, s=3.5, color=INK)
    line(ax, np.array([0, 0]), Pi, color=INK, lw=1.0, z=4)
    line(ax, np.array([0, 0]), Pr, color=INK, lw=1.0, z=4)
    text(ax, Pi[0] / 2 - 2.5, Pi[1] + 4.0, r"$d_1$", size=15, color=RAY2)
    text(ax, Pr[0] / 2 + 4.0, Pr[1] - 4.0, r"$d_2$", size=15, color=BLUE)
    text(ax, Pi[0] * 0.45 + 1, Pi[1] * 0.45 + 7.5, r"$R$", size=13, color=INK)
    arc(ax, np.array([0.0, 0.0]), 90, 90 + a, 13, r"$\alpha$", color=RAY, lab_r=19, fs=13)
    arc(ax, np.array([0.0, 0.0]), -90, -90 + b, 13, r"$\beta$", color=RAY, lab_r=19, fs=13)
    text(ax, 58, 4, "граница\nпластинки", size=10, color=RED, ha="right", va="bottom")
    f.tight_layout()
    save(f, "refraction-lab-construction")


# =====================================================================
# Total internal reflection
# =====================================================================


@fig("tir-critical-rays")
def _():
    n = 1.5
    acr = deg(math.asin(1 / n))
    assert abs(acr - 41.81) < 0.01
    cases = [("1", 30.0, RAY), ("2", 40.0, BLUE), ("*", acr, SPECIAL), ("3", 45.0, RAY2)]
    f, ax = canvas(9.4, 6.2, (-4.6, 5.0), (-3.6, 3.9))
    halfplane(ax, (-4.6, 5.0), 0, 3.9, GLASS)
    line(ax, (-4.5, 0), (4.9, 0), color=INK, lw=2)
    line(ax, (0, -3.3), (0, 3.4), color=GUIDE, lw=1.3, ls=(0, (5, 4)), z=2)
    o = np.array([0.0, 0.0])
    text(ax, -4.4, 3.4, "стекло, $n=1{,}5$", size=11.5, ha="left", color=GREY)
    text(ax, -4.4, -3.2, "воздух", size=11.5, ha="left", color=GREY)
    out = {}
    reach = {"1": 3.3, "2": 3.6, "*": 3.9, "3": 4.2}
    for lab, a, col in cases:
        d_in = -vec(90 + a)
        d_out = refract(d_in, np.array([0, 1.0]), n, 1.0)
        ray(ax, o + vec(90 + a) * reach[lab], o, color=col, f=0.5)
        ax.text(*(o + vec(90 + a) * (reach[lab] + 0.3)), lab, fontsize=13, color=col, ha="center", va="center", fontweight="bold")
        if d_out is None:
            assert lab == "3"
            ray(ax, o, o + vec(90 - a) * 3.4, color=col, f=0.55)
            out[lab] = None
        else:
            b = inc_angle(d_out, np.array([0, 1.0]))
            snell_check(n, a, 1.0, b)
            out[lab] = b
            ray(ax, o, o + d_out * (3.3 if lab != "*" else 4.3), color=col, f=0.55)
            if lab != "*":
                ray(ax, o, o + vec(90 - a) * 2.6, color=col, ls="--", lw=1.3, arrow=False)
    assert abs(out["1"] - 48.59) < 0.01 and abs(out["2"] - 74.62) < 0.01 and abs(out["*"] - 90) < 1e-3
    arc(ax, o, 90, 90 + acr, 1.6, r"$\alpha_{\rm пр}$", color=SPECIAL, lab_r=2.1, fs=12)
    text(ax, 4.3, -0.4, "вдоль границы", size=10, color=SPECIAL, ha="right", va="top")
    f.tight_layout()
    save(f, "tir-critical-rays")


@fig("tir-angle-graph")
def _():
    f, ax = plt.subplots(figsize=(8.2, 5.0))
    x = np.linspace(0, 90, 2000)
    for n, col, lab in ((1.5, RAY, "стекло, $n=1{,}5$"), (4 / 3, BLUE, "вода, $n=4/3$")):
        s = n * np.sin(np.radians(x))
        ok = s <= 1
        ax.plot(x[ok], np.degrees(np.arcsin(s[ok])), color=col, lw=2.5, label=lab)
        acr = deg(math.asin(1 / n))
        ax.plot([acr, acr], [0, 90], color=col, lw=1.2, ls="--")
        ax.scatter([acr], [90], color=col, zorder=5, s=45)
        ax.text(acr - 0.6, 3, rf"${num(acr, 1, math=True)}^\circ$", color=col, fontsize=10.5, ha="right")
    ax.plot(x, x, color=GREY, lw=1.3, ls=":", label=r"$\beta=\alpha$")
    ax.axvspan(deg(math.asin(1 / 1.5)), 90, color=RAY2, alpha=0.07)
    ax.text(75, 30, "для стекла здесь\nполное отражение", color=RAY2, ha="center", fontsize=11)
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 95)
    ax.set_xticks(range(0, 91, 15))
    ax.set_yticks(range(0, 91, 15))
    ax.set_xlabel(r"угол падения $\alpha$, град")
    ax.set_ylabel(r"угол преломления $\beta$, град")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left", fontsize=10.5)
    ax.set_title("Преломление в воздух из оптически более плотной среды", pad=6, fontsize=11.5)
    f.tight_layout()
    ru_axis(ax)
    save(f, "tir-angle-graph")


@fig("tir-critical-vs-n")
def _():
    n = np.linspace(1.0, 2.6, 400)
    f, ax = plt.subplots(figsize=(7.8, 4.7))
    ax.plot(n[1:], np.degrees(np.arcsin(1 / n[1:])), color=INK, lw=2.4)
    pts = [("вода", 4 / 3, VIOLET, (10, 8)), ("стекло", 1.5, RAY, (18, 14)), ("пластик диска", 1 / math.sin(rad(42)), BLUE, (-140, -30)), ("алмаз", 2.41, RAY2, (-44, 12))]
    for nm, nn, col, off in pts:
        a = deg(math.asin(1 / nn))
        ax.scatter([nn], [a], color=col, s=60, zorder=5)
        ax.annotate(f"{nm}: {num(a, 1)}°", (nn, a), textcoords="offset points", xytext=off, fontsize=10.5, color=col)
    assert abs(deg(math.asin(1 / 2.41)) - 24.5) < 0.05 and abs(1 / math.sin(rad(42)) - 1.494) < 1e-3
    ax.axhline(45, color=GREY, ls="--", lw=1.3)
    nsq = math.sqrt(2)
    ax.axvline(nsq, color=GREY, ls="--", lw=1.3)
    ax.text(2.55, 46, r"$45^\circ$", color=GREY, ha="right", fontsize=10.5)
    ax.text(nsq + 0.03, 75, r"$n=\sqrt{2}$", color=GREY, fontsize=10.5, ha="left")
    ax.set_xlim(1.0, 2.6)
    ax.set_ylim(0, 92)
    ax.set_xlabel(r"абсолютный показатель преломления среды $n$")
    ax.set_ylabel(r"предельный угол $\alpha_{\rm пр}$, град")
    ax.grid(color=GRID, lw=0.8)
    ax.set_title(r"Чем больше $n$, тем меньше предельный угол", pad=6, fontsize=11.5)
    f.tight_layout()
    ru_axis(ax)
    save(f, "tir-critical-vs-n")


@fig("tir-plastic-measurement")
def _():
    a = 42.0
    n = 1 / math.sin(rad(a))
    assert abs(n - 1.494) < 1e-3
    f, ax = canvas(7.4, 5.4, (-3.6, 3.8), (-2.8, 3.6))
    ax.add_patch(Wedge((0, 0), 3.0, 0, 180, fc=PLASTIC, ec=INK, lw=2.2, zorder=1))
    line(ax, (-3.3, 0), (3.6, 0), color=INK, lw=2.2, z=3)
    line(ax, (0, -2.4), (0, 3.25), color=GUIDE, lw=1.3, ls=(0, (5, 4)), z=2)
    o = np.array([0.0, 0.0])
    ray(ax, o + vec(90 + a) * 3.0, o, color=RAY, f=0.5)
    ray(ax, o, o + vec(0) * 3.2, color=SPECIAL, f=0.6)
    ray(ax, o, o + vec(90 - a) * 3.0, color=GREY, ls="--", lw=1.5, arrow=False)
    arc(ax, o, 90, 90 + a, 1.1, r"$\alpha_{\rm пр}=42^\circ$", color=RAY, lab_r=1.95, fs=11.5)
    right_mark(ax, o, 90, 0, s=0.3, color=SPECIAL)
    text(ax, 2.2, -0.35, r"$\beta=90^\circ$", size=11.5, color=SPECIAL)
    text(ax, -2.6, -1.35, "воздух", size=11, color=GREY)
    text(ax, 0.3, 2.6, "пластик", size=11, color=GREY, ha="left")
    text(ax, 1.3, -1.9, r"$n=\dfrac{1}{\sin\alpha_{\rm пр}}\approx 1{,}49$", size=12)
    f.tight_layout()
    save(f, "tir-plastic-measurement")


def trace_prism(poly, n, p, d, steps=6):
    """Follow a ray inside a prism; at each wall: TIR -> reflect, else refract out (and note the weak reflection)."""
    path = [np.array(p, float)]
    events = []
    skip = None
    for _ in range(steps):
        hit = poly_hit(path[-1], d, poly, skip)
        if hit is None:
            break
        t, i, nrm = hit
        q = path[-1] + d * t
        a = inc_angle(d, nrm)
        path.append(q)
        d_out = refract(d, -nrm, n, 1.0)
        if d_out is None:
            events.append(("tir", q, a, nrm))
            d = reflect(d, nrm)
            skip = i
        else:
            events.append(("out", q, a, nrm, d_out, reflect(d, nrm)))
            break
    return path, events


@fig("tir-prism-retro")
def _():
    n = 1 / math.sin(rad(42))  # the plastic of the lesson: critical angle 42 degrees
    acr = deg(math.asin(1 / n))
    f, axs = plt.subplots(1, 2, figsize=(11.6, 4.8))
    for ax, tilt, ttl in zip(axs, (0.0, 5.0), ("Грани перпендикулярны лучу", "Призма чуть повёрнута")):
        ax.set_xlim(-3.6, 4.4)
        ax.set_ylim(-2.9, 2.9)
        ax.set_aspect("equal")
        ax.axis("off")
        rot = lambda v: np.array([math.cos(rad(tilt)) * v[0] - math.sin(rad(tilt)) * v[1], math.sin(rad(tilt)) * v[0] + math.cos(rad(tilt)) * v[1]])
        poly = [rot(np.array(v, float)) for v in [(0, 2), (0, -2), (2, 0)]]
        ax.add_patch(Polygon(poly, closed=True, fc=PLASTIC, ec=INK, lw=2.2, zorder=1))
        p0 = np.array([-3.4, 0.8])
        d0 = np.array([1.0, 0.0])
        # the entry face is rotated with the prism; find the entry point and refract there
        t, i, nrm = poly_hit(p0, d0, poly)
        q0 = p0 + d0 * t
        d_in = refract(d0, nrm, 1.0, n)
        a0 = inc_angle(d0, nrm)
        snell_check(1.0, a0, n, inc_angle(d_in, nrm))
        ray(ax, p0, q0, color=RAY, f=0.45)
        path2, events = trace_prism(poly, n, q0, d_in)
        for k in range(1, len(path2)):
            ray(ax, path2[k - 1], path2[k], color=RAY, f=0.5)
        for e in events:
            if e[0] == "tir":
                assert e[2] > acr
        last = events[-1]
        assert last[0] == "out"
        q = last[1]
        ray(ax, q, q + last[4] * 2.6, color=RAY2, f=0.55)
        ax.set_title(ttl, fontsize=12, pad=4)
        if tilt == 0.0:
            # two total reflections at 45 degrees, then normal exit through the entry face
            assert [e[0] for e in events] == ["tir", "tir", "out"]
            assert abs(events[0][2] - 45) < 1e-6 and abs(events[1][2] - 45) < 1e-6 and abs(events[2][2]) < 1e-3
            assert abs(abs(ang(last[4])) - 180.0) < 1e-6
            text(ax, 1.55, 1.3, "45°", size=11, color=INK)
            text(ax, 1.55, -1.3, "45°", size=11, color=INK)
            text(ax, 2.75, 0.0, "полное\nотражение", size=10, color=GREY, ha="left")
        else:
            # the second face is hit below the critical angle: part of the light leaves
            assert [e[0] for e in events] == ["tir", "out"]
            assert abs(events[0][2] + events[1][2] - 90) < 1e-6 and events[0][2] > acr > events[1][2]
            ray(ax, q, q + last[5] * 1.6, color=GREY, ls="--", lw=1.4, arrow=False)
            lab2 = num(events[1][2], 1)
            labc = num(acr, 1)
            text(ax, 0.2, -2.45, rf"на второй грани {lab2}° < {labc}°: часть света выходит", size=10.5, color=RAY2)
    f.tight_layout()
    save(f, "tir-prism-retro")


@fig("tir-light-guide")
def _():
    n = 1.5
    acr = deg(math.asin(1 / n))
    f, (a1, a2) = plt.subplots(2, 1, figsize=(10.4, 8.6))
    # straight rod
    ax = a1
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(-2.4, 2.4)
    ax.set_aspect("equal")
    ax.axis("off")
    W = 1.0
    ax.add_patch(Rectangle((0, -W), 12.0, 2 * W, fc=GLASS, ec=INK, lw=2.2, zorder=1))
    th_air = 30.0
    th_in = deg(math.asin(math.sin(rad(th_air)) / n))
    snell_check(1.0, th_air, n, th_in)
    wall_inc = 90 - th_in
    assert wall_inc > acr
    p = np.array([0.0, -0.45])
    d = vec(th_in)
    pts = [p]
    x = 0.0
    while True:
        if d[1] > 0:
            t = (W - pts[-1][1]) / d[1]
        else:
            t = (-W - pts[-1][1]) / d[1]
        q = pts[-1] + d * t
        if q[0] >= 12.0:
            q = pts[-1] + d * ((12.0 - pts[-1][0]) / d[0])
            pts.append(q)
            break
        pts.append(q)
        d = np.array([d[0], -d[1]])
    src = pts[0] - vec(th_air) * 1.3
    ray(ax, src, pts[0], color=RAY, f=0.5)
    for k in range(1, len(pts)):
        ray(ax, pts[k - 1], pts[k], color=RAY, f=0.5)
    ray(ax, pts[-1], pts[-1] + vec(th_air * (1 if d[1] > 0 else -1)) * 1.5, color=RAY, f=0.55)
    text(ax, 6.0, 1.7, f"угол падения на стенку {num(wall_inc, 1)}° больше предельного {num(acr, 1)}°", size=11, color=RAY2)
    ax.set_title("Прямой стержень", fontsize=12.5, pad=4)
    # bent guide
    ax = a2
    Rin, Rout = 6.0, 7.0
    ax.set_xlim(-1.2, 8.0)
    ax.set_ylim(-1.0, 8.0)
    ax.set_aspect("equal")
    ax.axis("off")
    sector = 100.0
    ax.add_patch(Wedge((0, 0), Rout, 0, sector, width=Rout - Rin, fc=GLASS, ec=INK, lw=2.2, zorder=1))
    L = 5.6
    p = vec(0) * 6.5
    # direction at polar angle 0 with impact parameter L: component along the tangent = L / r
    sin_rad = L / 6.5
    d = vec(90) * sin_rad + vec(0) * math.sqrt(1 - sin_rad**2)
    pts = [p]
    incs = []
    for _ in range(80):
        b = float(np.dot(pts[-1], d))
        c = float(np.dot(pts[-1], pts[-1]))
        best = None
        for R in (Rout, Rin):
            disc = b * b - (c - R * R)
            if disc < 0:
                continue
            for t in (-b + math.sqrt(disc), -b - math.sqrt(disc)):
                if t > 1e-7 and (best is None or t < best[0]):
                    best = (t, R)
        t, R = best
        q = pts[-1] + d * t
        if ang(q) % 360 > sector:
            break
        nrm = q / np.linalg.norm(q)
        incs.append(inc_angle(d, nrm))
        pts.append(q)
        d = reflect(d, nrm)
    assert incs and min(incs) > acr, (min(incs), acr)
    for k in range(1, len(pts)):
        ray(ax, pts[k - 1], pts[k], color=RAY, f=0.5, arrow=(k % 2 == 1))
    last = pts[-1]
    # straight continuation to the exit face (polar angle = sector)
    ex = vec(sector)
    ts = seg_hit(last, d, ex * Rin, ex * Rout)
    if ts is not None:
        ray(ax, last, last + d * ts, color=RAY, f=0.5)
    ax.set_title("Изогнутый световод: луч не выходит, пока угол падения больше предельного", fontsize=12, pad=4)
    text(ax, 1.6, 1.6, f"наименьший угол падения на стенки {num(min(incs), 1)}°\nпредельный угол стекла {num(acr, 1)}°", size=11, color=RAY2)
    f.tight_layout()
    save(f, "tir-light-guide")


@fig("tir-fiber-bundle")
def _():
    f, ax = canvas(10.4, 4.8, (-0.5, 13.0), (-0.3, 6.4))
    pat = [1, 1, 0, 1, 0]
    ys = [5.0, 4.0, 3.0, 2.0, 1.0]
    fibers = []
    for k, y in enumerate(ys):
        x = np.linspace(2.0, 10.0, 80)
        yy = y + 0.9 * np.sin((x - 2.0) / 8 * math.pi) * (1 if k % 2 == 0 else -1) * 0.5 * (1 - abs(2 - k) / 3)
        ax.plot(x, yy, color=GREY, lw=7, alpha=0.35, solid_capstyle="round", zorder=1)
        ax.plot(x, yy, color=INK, lw=1.0, zorder=2)
    for x0, title in ((0.6, "изображение на входе"), (10.7, "то же изображение на выходе")):
        for v, y in zip(pat, ys):
            ax.add_patch(Rectangle((x0, y - 0.38), 0.76, 0.76, fc=GOLD if v else PAPER, ec=INK, lw=1.4, zorder=3))
        text(ax, x0 + 0.38, 5.95, title, size=10.5, color=INK)
    # the fibers carry each cell to the same place
    for v, y in zip(pat, ys):
        if v:
            ax.plot([1.36, 2.0], [y, y], color=GOLD, lw=3, zorder=2)
            ax.plot([10.0, 10.7], [y, y], color=GOLD, lw=3, zorder=2)
    text(ax, 6.0, 0.15, "жгут тонких волокон: порядок на обоих концах одинаков", size=11, color=GREY)
    f.tight_layout()
    save(f, "tir-fiber-bundle")


@fig("tir-fiber-link")
def _():
    f, ax = plt.subplots(figsize=(12.4, 3.6))
    ax.set_xlim(0, 15.6)
    ax.set_ylim(-0.3, 3.5)
    ax.axis("off")
    # (x, label, colour); fibres lie between the boxes
    boxes = [(0.2, "лазер", GOLD), (5.6, "фотоприёмник,\nусилитель\nи лазер", BLUE), (11.0, "фотоприёмник,\nусилитель\nи лазер", BLUE)]
    for x, lab, col in boxes:
        ax.add_patch(Rectangle((x, 0.35), 2.4, 1.5, fc=PAPER, ec=col, lw=2.2, zorder=3))
        ax.text(x + 1.2, 1.1, lab, ha="center", va="center", fontsize=10.5, zorder=4)
    for x0, x1 in ((2.6, 5.6), (8.0, 11.0)):
        ax.plot([x0, x1], [1.1, 1.1], color=GREY, lw=9, alpha=0.35, solid_capstyle="butt", zorder=1)
        ax.plot([x0, x1], [1.1, 1.1], color=INK, lw=1.0, zorder=2)
    ax.annotate("", (15.5, 1.1), (13.4, 1.1), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=2))
    ax.text(14.45, 1.45, "и так далее", ha="center", fontsize=10, color=GREY)

    def pulses(x0, amp, col):
        for k, on in enumerate((1, 0, 1, 1)):
            if on:
                ax.add_patch(Rectangle((x0 + 0.3 * k, 2.3), 0.22, 0.85 * amp, fc=col, ec="none", zorder=3))
        ax.plot([x0 - 0.1, x0 + 1.3], [2.3, 2.3], color=INK, lw=0.8, zorder=2)

    for x0 in (2.8, 8.2):
        pulses(x0, 1.0, GOLD)
        pulses(x0 + 1.9, 0.4, BLUE)
    ax.text(3.3, 3.4, "на выходе лазера", fontsize=9.5, ha="center", color=GREY)
    ax.text(5.75, 3.4, "слабее после волокна", fontsize=9.5, ha="center", color=GREY)
    ax.text(8.7, 3.4, "усилен и отправлен снова", fontsize=9.5, ha="center", color=GREY)
    f.tight_layout()
    save(f, "tir-fiber-link")


@fig("tir-problem-1040")
def _():
    n, D = 4 / 3, 3.0
    acr = deg(math.asin(1 / n))
    assert abs(acr - 48.59) < 0.01
    f, ax = canvas(11.6, 6.0, (-2.4, 11.4), (-0.6, D + 2.8))
    halfplane(ax, (-0.6, 10.9), 0, D, WATER)
    line(ax, (-0.6, 0), (10.9, 0), color=INK, lw=3)
    line(ax, (-0.6, 0), (-0.6, D + 0.6), color=INK, lw=3)
    line(ax, (10.9, 0), (10.9, D + 0.6), color=INK, lw=3)
    line(ax, (-0.6, D), (10.9, D), color=BLUE, lw=1.6)
    S = np.array([0.0, 0.0])
    ax.plot(*S, "o", color=GOLD, ms=11, zorder=8)
    text(ax, 0.0, -0.45, "источник", size=10.5, color=GREY)
    for lab, a, col in (("A", 30.0, RAY), ("B", 60.0, RAY2)):
        P = np.array([D * math.tan(rad(a)), D])
        d = (P - S) / np.linalg.norm(P - S)
        d_out = refract(d, np.array([0, -1.0]), n, 1.0)
        ray(ax, S, P, color=col, f=0.5)
        line(ax, P - np.array([0, 1.3]), P + np.array([0, 1.4]), color=GUIDE, lw=1.2, ls=(0, (5, 4)), z=2)
        text(ax, P[0] - 0.3, D + 1.65, lab, size=14, color=col)
        arc(ax, P, -90, ang(-d), 0.9, rf"$\alpha_{lab}={a:.0f}^\circ$", color=col, lab_r=1.75 if lab == "A" else 1.85, fs=10.5)
        d_r = reflect(d, np.array([0, 1.0]))
        if d_out is not None:
            b = inc_angle(d_out, np.array([0, 1.0]))
            snell_check(n, a, 1.0, b)
            assert abs(b - 41.81) < 0.01
            ray(ax, P, P + d_out * 2.6, color=col, f=0.55)
            ray(ax, P, P + d_r * 2.6, color=col, ls="--", lw=1.4, arrow=False)
            arc(ax, P, 90, ang(d_out), 0.9, rf"$\beta_A={num(b, 1, math=True)}^\circ$", color=col, lab_r=1.75, fs=10.5)
        else:
            assert a > acr
            end = P + d_r * (D / -d_r[1])
            ray(ax, P, end, color=col, f=0.5)
            text(ax, P[0] + 0.15, D + 0.9, "полное\nотражение", size=10.5, color=col, ha="left")
    text(ax, 9.2, 1.2, "вода", size=11.5, color=BLUE)
    text(ax, 9.3, D + 1.0, "воздух", size=11, color=GREY)
    f.tight_layout()
    save(f, "tir-problem-1040")


@fig("tir-problem-1045")
def _():
    phi, n = 20.0, 1.5
    acr = deg(math.asin(1 / n))
    hp = rad(phi / 2)
    Lx = 7.0
    h = Lx * math.tan(hp)
    apex = np.array([Lx, 0.0])
    top = np.array([0.0, h])
    bot = np.array([0.0, -h])
    poly = [top, bot, apex]  # base on the left, apex on the right
    f, ax = canvas(10.4, 6.2, (-1.4, 9.6), (-4.6, 2.8))
    ax.add_patch(Polygon(poly, closed=True, fc=GLASS, ec=INK, lw=2.2, zorder=1))
    # the ray runs perpendicular to the upper lateral face, going down
    d0 = np.array([-math.sin(hp), -math.cos(hp)])
    # verify the ray is normal to the upper face
    assert abs(float(np.dot(d0, (apex - top) / np.linalg.norm(apex - top)))) < 1e-9
    res = {}
    for case, frac, col in (("a", 0.45, RAY), ("b", 0.03, RAY2)):
        P = top + (apex - top) * frac
        ray(ax, P - d0 * 1.0, P, color=col, f=0.5)
        t, i, nrm = poly_hit(P, d0, poly, 2)
        q = P + d0 * t
        a = inc_angle(d0, nrm)
        if case == "a":
            assert i == 1
            d_out = refract(d0, -nrm, n, 1.0)
            b = inc_angle(d_out, nrm)
            snell_check(n, a, 1.0, b)
            delta = abs(ang(d_out) - ang(d0))
            assert abs(a - 20) < 1e-9 and abs(b - 30.86) < 0.01 and abs(delta - 10.86) < 0.01
            ray(ax, P, q, color=col, f=0.5)
            ray(ax, q, q + d_out * 2.0, color=col, f=0.55)
            ray(ax, q, q + d0 * 2.0, color=GREY, ls="--", lw=1.4, arrow=False)
            ray(ax, q, q + reflect(d0, nrm) * 1.3, color=col, ls="--", lw=1.2, arrow=False)
            line(ax, q - nrm * 0.9, q + nrm * 0.9, color=GREY, lw=1.1, ls=(0, (5, 4)), z=3)
            arc(ax, q, ang(-nrm), ang(-d0), 0.7, r"$\alpha_A$", color=col, lab_r=1.05, fs=11)
            arc(ax, q, ang(nrm), ang(d_out), 0.7, r"$\beta_A$", color=col, lab_r=1.05, fs=11)
            arc(ax, q, ang(d0), ang(d_out), 1.5, r"$\delta_A$", color=col, lab_r=1.9, fs=11.5)
            res["a"] = delta
        else:
            assert i == 0
            assert abs(a - 80) < 1e-9 and a > acr
            ray(ax, P, q, color=col, f=0.5)
            d_r = reflect(d0, nrm)
            t2, i2, nrm2 = poly_hit(q, d_r, poly, 0)
            q2 = q + d_r * t2
            ray(ax, q, q2, color=col, f=0.5)
            a2 = inc_angle(d_r, nrm2)
            assert abs(a2) < 1e-9
            ray(ax, q2, q2 + d_r * 2.0, color=col, f=0.55)
            line(ax, q - nrm * 0.9, q + nrm * 0.9, color=GREY, lw=1.1, ls=(0, (5, 4)), z=3)
            arc(ax, q, ang(-nrm), ang(-d0), 0.8, r"$\alpha_B$", color=col, lab_r=1.2, fs=11)
            delta = abs(ang(d_r) - ang(d0))
            delta = 180 - delta if delta > 180 else delta
            assert abs(delta - 20.0) < 1e-9 and abs(delta - phi) < 1e-9
            ray(ax, q2, q2 + d0 * 2.0, color=GREY, ls="--", lw=1.4, arrow=False)
            arc(ax, q2, ang(d0), ang(d_r), 1.2, r"$\delta_B=\varphi$", color=col, lab_r=2.05, fs=11)
            res["b"] = delta
    arc(ax, apex, 180 - phi / 2, 180 + phi / 2, 1.5, r"$\varphi$", color=INK, lab_r=2.0, fs=12)
    text(ax, -0.25, h + 0.4, "основание", size=10, color=GREY, ha="right")
    f.tight_layout()
    save(f, "tir-problem-1045")


if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
        print("ok", n)
