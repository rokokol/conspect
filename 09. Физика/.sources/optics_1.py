"""Figures for the notes of section f14 "Оптика" (lessons 195-201): light and shadow, reflection, the plane mirror.

Run: python3 optics_1.py [name ...]   (matplotlib only)
PNG files go to content/14. Оптика/00. Вложения/ (prefixes light- and mirror-)
Every ray is computed from the law it illustrates (straight lines, angle of reflection equal to angle of incidence,
the image as the mirror reflection of the point), and the key facts of each picture are checked by assert statements.
Colours are the roles of theme.py: incident ray green, reflected ray red, image and extensions of rays violet and dashed, normal grey and dashed.
"""
import sys

import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from magnet_common import arrow, blank, blank_multi, poly, rect  # only the colour-free helpers: every colour here is passed in
from matplotlib.patches import Arc, Circle, Ellipse, Polygon, Rectangle, Wedge

from course import COURSE
from theme import ACCENT, BLUE, COPPER, GREEN, INK, LIGHT, MUTED, PAPER, RED, SKY, VIOLET, WARM, saver, tint

OUT14 = COURSE / "content" / "14. Оптика" / "00. Вложения"
OUT14.mkdir(parents=True, exist_ok=True)
(OUT14 / ".nomedia").touch()

FIGS = {}
GREY = MUTED  # guides, normals, dimension lines and small notes
INC = GREEN  # every ray of light; the incident one
REF = RED  # the reflected ray, the second ray of a pair
VIRT = VIOLET  # an image and the extensions of rays behind a mirror
RAY3 = ACCENT  # a fourth ray in a figure that already uses green, blue and red
DASH = (0, (4, 3))
SUN = WARM
UMBRA = tint(INK, 0.3)
PENUMBRA = tint(INK, 0.7)
ZONE = tint(GREEN, 0.85)  # where the light reaches the eye
ZONE_TEXT = INK
SOFT = tint(INK, 0.9)  # the pale body fill of a ground, a wall, a room


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


save14 = saver(OUT14)


# ------------------------------------------------------------------ geometry helpers


def P(x, y):
    return np.array([float(x), float(y)])


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.hypot(*v)


def polar(deg, r=1.0):
    t = np.deg2rad(deg)
    return np.array([r * np.cos(t), r * np.sin(t)])


def reflect_point(p, a, b):
    """Mirror image of p in the straight line through a and b."""
    p, a, b = map(np.asarray, (p, a, b))
    u = unit(b - a)
    w = p - a
    return a + 2 * np.dot(w, u) * u - w


def reflect_dir(d, surface_dir):
    """Direction of a ray after reflection in a line with the given direction."""
    u = unit(surface_dir)
    d = np.asarray(d, dtype=float)
    return 2 * np.dot(d, u) * u - d


def intersect(p, d, q, e):
    """Point where the line p + t d meets the line q + s e."""
    m = np.array([[d[0], -e[0]], [d[1], -e[1]]])
    t, _ = np.linalg.solve(m, np.asarray(q) - np.asarray(p))
    return np.asarray(p) + t * np.asarray(d)


def foot(pt, through, direction):
    """Foot of the perpendicular from pt to the line through `through` with the given direction."""
    through = np.asarray(through, dtype=float)
    u = unit(direction)
    return through + np.dot(np.asarray(pt, dtype=float) - through, u) * u


def sees(e, images, mirror_a, mirror_b):
    """True if an eye at e sees every image through the mirror segment a-b."""
    e = np.asarray(e, dtype=float)
    a, b = np.asarray(mirror_a, dtype=float), np.asarray(mirror_b, dtype=float)
    u = unit(b - a)
    for im in images:
        im = np.asarray(im, dtype=float)
        try:
            h = intersect(e, im - e, a, u)
        except np.linalg.LinAlgError:
            return False
        if not 0 <= np.dot(h - a, u) <= np.hypot(*(b - a)):
            return False
        if np.dot(im - e, h - e) <= 0:
            return False
    return True


def zone_mask(xlim, ylim, images, a, b, inside=None, n=300):
    xs = np.linspace(*xlim, n)
    ys = np.linspace(*ylim, n)
    m = np.zeros((n, n))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if inside is not None and not inside(x, y):
                continue
            if sees(P(x, y), images, a, b):
                m[j, i] = 1
    return xs, ys, m


def draw_zone(ax, xlim, ylim, images, a, b, inside=None, n=300):
    xs, ys, m = zone_mask(xlim, ylim, images, a, b, inside, n)
    ax.contourf(xs, ys, m, levels=[0.5, 1.5], colors=[ZONE], alpha=0.9, zorder=0)


# ------------------------------------------------------------------ drawing helpers


def ray(ax, p, q, color=INC, lw=1.9, marks=(0.5,), dash=False, z=4, size=13, alpha=1.0):
    """Line from p to q with arrowheads at the given fractions of its length."""
    p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=DASH if dash else "-", zorder=z, alpha=alpha, solid_capstyle="round")
    d = unit(q - p)
    for t in marks:
        c = p + (q - p) * t
        arrow(ax, c - d * 0.06, c + d * 0.06, color=color, lw=lw, scale=size, zorder=z + 1, alpha=alpha)


def dashed(ax, p, q, color=GREY, lw=1.2, z=3, alpha=1.0):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=DASH, zorder=z, alpha=alpha)


def mirror_line(ax, p, q, side=-1, lw=3.2, tick=0.22, step=0.3, color=INK):
    """Mirror from p to q; the hatching sits on the back side (side=+1 is the left of the direction p to q)."""
    p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, solid_capstyle="butt", zorder=5)
    length = np.hypot(*(q - p))
    u = (q - p) / length
    n = np.array([-u[1], u[0]]) * side
    s = step / 2
    while s < length:
        b = p + u * s
        t = b + n * tick - u * tick * 0.7
        ax.plot([b[0], t[0]], [b[1], t[1]], color=color, lw=1.0, zorder=5)
        s += step


def wall_line(ax, p, q, side=-1, lw=2.4, tick=0.16, step=0.25):
    mirror_line(ax, p, q, side=side, lw=lw, tick=tick, step=step)


def arc_label(ax, c, r, a1, a2, text=None, color=INK, lw=1.5, lr=1.42, size=11, z=6):
    """Angle arc about c from direction a1 to a2 (degrees) with a label beyond the arc."""
    lo, hi = min(a1, a2), max(a1, a2)
    ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=lo, theta2=hi, color=color, lw=lw, zorder=z))
    if text:
        m = np.deg2rad((lo + hi) / 2)
        ax.text(c[0] + lr * r * np.cos(m), c[1] + lr * r * np.sin(m), text, fontsize=size, color=color, ha="center", va="center", zorder=z + 1)


def compass_arc(ax, c, r, toward, half=13, color=GREY, lw=1.1):
    """Short arc of a compass with centre c and radius r around the direction to the point `toward`."""
    a0 = np.degrees(np.arctan2(toward[1] - c[1], toward[0] - c[0]))
    ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=a0 - half, theta2=a0 + half, color=color, lw=lw, zorder=2))


def right_angle(ax, c, d1, d2, s=0.2, color=INK, lw=1.2):
    c = np.asarray(c, dtype=float)
    a, b = unit(d1) * s, unit(d2) * s
    ax.plot([c[0] + a[0], c[0] + a[0] + b[0], c[0] + b[0]], [c[1] + a[1], c[1] + a[1] + b[1], c[1] + b[1]], color=color, lw=lw, zorder=6)


def tick(ax, p, q, n=1, size=0.11, color=INK, lw=1.3, gap=0.09):
    """Equal-segment marks on the middle of p-q."""
    p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
    u = unit(q - p)
    nrm = np.array([-u[1], u[0]])
    mid = (p + q) / 2
    for i in range(n):
        c = mid + u * gap * (i - (n - 1) / 2)
        a, b = c - nrm * size + u * 0.03, c + nrm * size - u * 0.03
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, zorder=7)


def eye(ax, x, y, ang=0.0, s=0.26, color=INK):
    ax.add_patch(Ellipse((x, y), 2 * s, 1.1 * s, angle=ang, fc=PAPER, ec=color, lw=1.4, zorder=9))
    t = np.deg2rad(ang)
    ax.add_patch(Circle((x - 0.35 * s * np.cos(t), y - 0.35 * s * np.sin(t)), 0.3 * s, fc=color, ec=color, zorder=10))


def star(ax, x, y, size=17):
    ax.plot([x], [y], marker="*", color=SUN, mec=INK, mew=1.0, ms=size, zorder=9, ls="none")


def image_dot(ax, p, size=10):
    ax.plot([p[0]], [p[1]], marker="o", mfc=PAPER, mec=VIRT, ms=size, mew=2.0, zorder=9, ls="none")


def dot(ax, p, color=INK, size=5.5, z=8):
    ax.plot([p[0]], [p[1]], "o", color=color, ms=size, zorder=z)


def label(ax, p, s, size=11, dx=0.0, dy=0.0, color=INK, ha="center", va="center", bg=False, **kw):
    if bg:
        kw["bbox"] = dict(fc=PAPER, ec="none", pad=1.5, alpha=0.85)
    ax.text(p[0] + dx, p[1] + dy, s, fontsize=size, color=color, ha=ha, va=va, zorder=12, **kw)


def dim(ax, p, q, text="", off=(0.0, 0.0), color=GREY, size=10.5, **kw):
    """Dimension line with arrowheads at both ends and an optional label at the middle shifted by off."""
    p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
    arrow(ax, p, q, color=color, lw=1.2, style="<|-|>", scale=9, zorder=7)
    if text:
        m = (p + q) / 2
        ax.text(m[0] + off[0], m[1] + off[1], text, fontsize=size, color=color, ha="center", va="center", zorder=12, **kw)


def mix(c1, c2, t):
    a = np.array(matplotlib.colors.to_rgb(c1))
    b = np.array(matplotlib.colors.to_rgb(c2))
    return tuple(a + (b - a) * t)


def gradient_band(ax, x0, x1, y0, y1, c_bottom, c_top, n=50, z=1):
    for i in range(n):
        ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
        ax.add_patch(Rectangle((x0, ya), x1 - x0, yb - ya + 0.002, fc=mix(c_bottom, c_top, (i + 0.5) / n), ec="none", zorder=z))


def fill(ax, pts, color, alpha=1.0, z=1):
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", alpha=alpha, zorder=z))


def sphere(ax, c, r, fc, z=6, lw=1.6):
    ax.add_patch(Circle(c, r, fc=fc, ec=INK, lw=lw, zorder=z))


# ------------------------------------------------------------------ light: beams and the law of rectilinear propagation


@fig
def light_beams():
    f, axs = blank_multi(1, 3, 12.6, 3.5, (-0.6, 4.8), (-2.6, 2.15))
    ax = axs[0]
    star(ax, 0, 0)
    for a in (-30, -15, 0, 15, 30):
        ray(ax, P(0, 0), polar(a, 4.0), marks=(0.6,))
    label(ax, (2.1, -2.4), "расходящийся пучок", 11.5, weight="bold")
    ax = axs[1]
    focus = P(3.0, 0)
    for y in (-1.5, -0.75, 0, 0.75, 1.5):
        ray(ax, P(0, y), focus, marks=(0.45,))
        end = focus + (focus - P(0, y)) * 0.4
        ax.plot([focus[0], end[0]], [focus[1], end[1]], color=INC, lw=1.2, alpha=0.45)
    dot(ax, focus, INK, 6)
    label(ax, (2.1, -2.4), "сходящийся пучок", 11.5, weight="bold")
    ax = axs[2]
    for y in (-1.2, -0.6, 0, 0.6, 1.2):
        ray(ax, P(0, y), P(4.2, y), marks=(0.55,))
    label(ax, (2.1, -2.4), "параллельный пучок", 11.5, weight="bold")
    save14(f, "light-beams")


@fig
def light_sugar_cell():
    f, ax = blank(10.4, 4.6, (-2.0, 8.6), (-0.6, 3.1))
    sugar, water = tint(WARM, 0.55), tint(SKY, 0.8)
    x0, x1 = 0.0, 4.4
    rect(ax, x0, 0, x1 - x0, 0.9, fc=sugar, ec="none", zorder=1)
    gradient_band(ax, x0, x1, 0.9, 1.9, sugar, water)
    rect(ax, x0, 1.9, x1 - x0, 0.8, fc=water, ec="none", zorder=1)
    rect(ax, x0, 0, x1 - x0, 2.7, fc="none", ec=INK, lw=2.0, zorder=6)
    for y, text in ((0.45, "крепкий раствор сахара"), (1.4, "область переменной концентрации"), (2.3, "чистая вода")):
        label(ax, (x1 + 0.2, y), text, 11, ha="left")
    t = np.linspace(0, 1, 120)
    xs = x0 + (x1 - x0) * t
    ys = 1.7 - 0.72 * (3 * t**2 - 2 * t**3)
    rect(ax, -1.8, 1.52, 0.9, 0.36, fc=LIGHT, ec=INK, lw=1.4, zorder=5)
    label(ax, (-1.35, 1.25), "лазер", 10.5)
    ax.plot([-0.9, x0], [1.7, 1.7], color=INC, lw=2.0, zorder=5)
    ax.plot(xs, ys, color=INC, lw=2.6, zorder=5)
    k = 54
    arrow(ax, (xs[k], ys[k]), (xs[k + 3], ys[k + 3]), color=INC, lw=2.4, scale=16, zorder=6)
    dashed(ax, P(x0, 1.7), P(x1, 1.7), color=GREY, lw=1.3)
    label(ax, (2.3, 2.2), "прямо, если бы среда была однородной", 9.5, color=GREY)
    save14(f, "light-sugar-cell")


# ------------------------------------------------------------------ shadow and penumbra


def sight_line(ax, e, target, barrier_x, half, visible, color=GREY):
    """Sight line from an eye to a source; a cross marks the place where the barrier blocks it."""
    if visible:
        ax.plot([e[0], target[0]], [e[1], target[1]], color=color, lw=1.1, zorder=3)
    else:
        y_at = target[1] + (e[1] - target[1]) * (barrier_x - target[0]) / (e[0] - target[0])
        assert abs(y_at) <= half + 1e-9, "sight line must hit the barrier"
        ax.plot([e[0], barrier_x], [e[1], y_at], color=color, lw=1.1, ls=DASH, zorder=3)
        ax.plot([barrier_x], [y_at], marker="x", color=RED, ms=7, mew=2.0, zorder=9)


@fig
def light_point_shadow():
    f, ax = blank(10.6, 6.0, (-1.0, 9.6), (-3.6, 3.8))
    S = P(0, 0)
    xb, hb, xs = 3.0, 0.7, 7.0
    ys = hb * xs / xb
    fill(ax, [(xb, hb), (xs, ys), (xs, -ys), (xb, -hb)], UMBRA, alpha=0.8, z=1)
    ax.plot([xs, xs], [-3.4, 3.4], color=INK, lw=2.6, zorder=5)
    ax.plot([xb, xb], [-hb, hb], color=INK, lw=6.5, solid_capstyle="butt", zorder=6)
    star(ax, *S)
    for y_end in (2.9, -2.9, 2.0, -2.0):
        ray(ax, S, P(xs, y_end), marks=(0.4,))
    for sgn in (1, -1):
        ray(ax, S, P(xs, sgn * ys), marks=(), z=5)
        ray(ax, S, P(xb, sgn * 0.3), marks=(0.6,))
    in_shadow, in_light = P(6.3, 0.45), P(6.3, 2.35)
    sight_line(ax, in_shadow, S, xb, hb, visible=False)
    sight_line(ax, in_light, S, xb, hb, visible=True)
    for e in (in_shadow, in_light):
        eye(ax, e[0], e[1], s=0.27)
    label(ax, (-0.5, 0.55), "S", 13, weight="bold")
    # label below the fan of rays, with a leader to the barrier
    ax.annotate("преграда", (xb, -hb), (2.0, -2.5), ha="center", va="center", fontsize=11, color=INK, zorder=12,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    label(ax, (xs, 3.7), "экран", 11)
    label(ax, (5.2, 0.0), "тень", 13, color=PAPER, weight="bold")
    label(ax, (4.6, 3.05), "освещённая область", 11)
    label(ax, (4.6, -3.05), "освещённая область", 11)
    label(ax, (8.35, 0.45), "глаз в тени:\nисточник не виден", 10, color=RED)
    label(ax, (8.35, 2.35), "глаз вне тени:\nисточник виден", 10)
    save14(f, "light-point-shadow")


@fig
def light_two_sources():
    f, ax = blank(12.6, 7.0, (-1.2, 12.2), (-4.3, 4.6))
    S1, S2 = P(0, 0.9), P(0, -0.9)
    xb, hb, xs = 4.0, 0.8, 9.0

    def hit(S, edge):
        return S[1] + (edge - S[1]) * xs / xb

    u1, u2 = hit(S1, hb), hit(S2, -hb)  # edges of the umbra on the screen
    assert abs(u1 - 0.675) < 1e-9 and abs(u2 + 0.675) < 1e-9
    top_pen, bot_pen = hit(S2, hb), hit(S1, -hb)
    fill(ax, [(xb, hb), (xs, top_pen), (xs, u1)], PENUMBRA, alpha=0.75, z=1)
    fill(ax, [(xb, -hb), (xs, bot_pen), (xs, u2)], PENUMBRA, alpha=0.75, z=1)
    fill(ax, [(xb, hb), (xs, u1), (xs, u2), (xb, -hb)], UMBRA, alpha=0.85, z=1)
    ax.plot([xs, xs], [-4.0, 4.0], color=INK, lw=2.6, zorder=5)
    ax.plot([xb, xb], [-hb, hb], color=INK, lw=6.5, solid_capstyle="butt", zorder=6)
    for S in (S1, S2):
        star(ax, *S, size=15)
        for edge in (hb, -hb):
            ray(ax, S, P(xs, hit(S, edge)), marks=(0.25,), lw=1.5)
    label(ax, (-0.7, 0.9), "S$_1$", 13, weight="bold")
    label(ax, (-0.7, -0.9), "S$_2$", 13, weight="bold")
    ax.annotate("преграда", (xb, -hb), (2.6, -2.9), ha="center", va="center", fontsize=11, color=INK, zorder=12,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    label(ax, (xs, 4.4), "экран", 11)
    label(ax, (7.3, 0.0), "тень", 13, color=PAPER, weight="bold")
    label(ax, (7.3, -1.9), "полутень", 11.5)
    label(ax, (8.0, 2.15), "полутень", 11.5)  # between the sight line to S1 and the edge of the penumbra
    cases = [
        (0.0, "тень:\nне виден ни один\nисточник"),
        (1.8, "полутень:\nвиден только S$_1$"),
        (3.6, "освещённая область:\nвидны оба источника"),
    ]
    for y, text in cases:
        e = P(xs, y)
        for S in (S1, S2):
            y_at = S[1] + (e[1] - S[1]) * xb / xs
            sight_line(ax, e, S, xb, hb, visible=abs(y_at) > hb)
        eye(ax, e[0], e[1], s=0.27)
        label(ax, (xs + 0.5, y), text, 9.5, ha="left")
    save14(f, "light-two-sources")


def shadow_panel(ax, R, r, xb, xs):
    """Source of half-size R at x=0, barrier of half-size r at x=xb, screen at x=xs; R=0 is a point source."""
    xtip = R * xb / (R - r) if R > r else None
    if xtip is not None:
        assert xs < xtip, "the screen must stand before the tip of the umbra"
    x = np.linspace(xb, xs, 60)
    y_u = R + (r - R) * x / xb  # edge of the umbra: top of the source through the top of the barrier
    y_p = -R + (r + R) * x / xb  # outer edge of the penumbra
    up = np.maximum(y_u, 0)
    fill(ax, list(zip(x, y_p)) + list(zip(x[::-1], up[::-1])), PENUMBRA, alpha=0.75, z=1)
    fill(ax, list(zip(x, -y_p)) + list(zip(x[::-1], -up[::-1])), PENUMBRA, alpha=0.75, z=1)
    fill(ax, list(zip(x, up)) + list(zip(x[::-1], -up[::-1])), UMBRA, alpha=0.85, z=1)
    ax.plot([xs, xs], [-(y_p[-1] + 0.6), y_p[-1] + 0.6], color=INK, lw=2.4, zorder=5)
    ax.plot([xb, xb], [-r, r], color=INK, lw=6.0, solid_capstyle="butt", zorder=6)
    if R > 0:
        ax.plot([0, 0], [-R, R], color=INC, lw=6.0, solid_capstyle="butt", zorder=6)
        for s1 in (1, -1):
            for s2 in (1, -1):
                ray(ax, P(0, s1 * R), P(xs, s1 * R + (s2 * r - s1 * R) * xs / xb), marks=(), lw=1.3)
    else:
        star(ax, 0, 0, 15)
        for s2 in (1, -1):
            ray(ax, P(0, 0), P(xs, s2 * r * xs / xb), marks=(), lw=1.3)
    return R + (r - R) * xs / xb  # half-size of the umbra on the screen, negative if there is none


@fig
def light_extended_source():
    f, ax = blank(11.6, 6.4, (-1.0, 10.4), (-3.2, 3.2))
    R, r, xb, xs = 1.2, 0.6, 4.0, 6.0
    yu_s = shadow_panel(ax, R, r, xb, xs)
    yp_s = -R + (r + R) * xs / xb
    assert abs(yu_s - 0.3) < 1e-9 and abs(yp_s - 1.5) < 1e-9
    n = 160
    for i in range(n):
        y0, y1 = -2.6 + 5.2 * i / n, -2.6 + 5.2 * (i + 1) / n
        lev = min(1.0, max(0.0, (abs((y0 + y1) / 2) - yu_s) / (yp_s - yu_s)))
        ax.add_patch(Rectangle((xs + 0.02, y0), 0.3, y1 - y0 + 0.004, fc=mix(INK, PAPER, lev), ec="none", zorder=4))
    ys_ = np.linspace(-2.6, 2.6, 400)
    lev = np.clip((np.abs(ys_) - yu_s) / (yp_s - yu_s), 0, 1)
    x_base = 7.3
    ax.plot(x_base + 1.9 * lev, ys_, color=INK, lw=2.4, zorder=6)
    ax.plot([x_base, x_base], [-2.6, 2.6], color=GREY, lw=1.2, zorder=3)
    ax.plot([x_base + 1.9] * 2, [-2.6, 2.6], color=GREY, lw=1.0, ls=DASH, zorder=3)
    label(ax, (x_base + 0.95, 3.05), "освещённость", 11)
    label(ax, (x_base, -2.95), "0", 10, color=GREY)
    label(ax, (x_base + 1.9, -2.95), "полная", 10, color=GREY)
    label(ax, (-0.55, 0.0), "протяжённый\nисточник", 10.5, ha="right")
    label(ax, (xb - 0.6, -1.15), "преграда", 10.5, bg=True)
    label(ax, (xs + 0.15, 3.05), "экран", 10.5)
    label(ax, (5.05, 0.0), "тень", 11, color=PAPER, weight="bold")
    label(ax, (5.15, 0.98), "полутень", 10.5)
    label(ax, (5.15, -0.98), "полутень", 10.5)
    save14(f, "light-extended-source")


@fig
def light_shadow_size():
    f, axs = blank_multi(3, 1, 9.6, 9.0, (-1.0, 8.6), (-2.4, 2.4))
    cases = [
        (1.0, 0.5, "источник больше преграды: тень меньше преграды"),
        (0.25, 0.5, "источник меньше преграды: тень больше преграды"),
        (0.0, 0.5, "точечный источник, предельный случай: тень ещё больше"),
    ]
    xb, xs = 3.0, 5.0
    for ax, (R, r, title) in zip(axs, cases):
        half = shadow_panel(ax, R, r, xb, xs)
        label(ax, (3.8, 2.15), title, 11, weight="bold")
        ax.plot([xs + 0.35, xs + 0.35], [-abs(half), abs(half)], color=RED, lw=2.4, zorder=7)
        label(ax, (xs + 1.05, 0), "тень\n%s преграды" % ("<" if abs(half) < r else ">"), 10.5, color=RED, ha="left")
    save14(f, "light-shadow-size")


# ------------------------------------------------------------------ eclipses


def eclipse_panel(ax, Rs, xm, rm, xe, re, xr):
    """Sun at the origin, Moon at xm, Earth at xe; the light cones end at x=xr. Returns the umbra apex and the penumbra crossing."""
    x_u = xm * Rs / (Rs - rm)  # external tangents meet here: apex of the umbra
    x_p = xm * Rs / (Rs + rm)  # internal tangents cross here
    s_u, s_p = np.arcsin(Rs / x_u), np.arcsin(Rs / x_p)
    X, Y = P(x_u, 0), P(x_p, 0)
    up = np.array([np.cos(s_p), np.sin(s_p)])
    dn = np.array([np.cos(s_p), -np.sin(s_p)])
    reach_p = (xr - x_p) / np.cos(s_p)
    fill(ax, [foot((xm, 0), Y, up), Y + up * reach_p, Y + dn * reach_p, foot((xm, 0), Y, dn)], PENUMBRA, alpha=0.75, z=1)
    u_up = np.array([-np.cos(s_u), np.sin(s_u)])
    u_dn = np.array([-np.cos(s_u), -np.sin(s_u)])
    fill(ax, [foot((xm, 0), X, u_up), X, foot((xm, 0), X, u_dn)], UMBRA, alpha=0.85, z=2)
    reach_u = (xr - x_u) / np.cos(s_u)
    fill(ax, [X, X + np.array([np.cos(s_u), np.sin(s_u)]) * reach_u, X + np.array([np.cos(s_u), -np.sin(s_u)]) * reach_u], tint(INK, 0.45), alpha=0.45, z=2)
    for sgn in (1, -1):
        u = np.array([np.cos(s_p), sgn * np.sin(s_p)])  # internal tangent, touches the Sun on the side opposite to its far end
        t0 = foot((0, 0), Y, u)
        assert abs(np.hypot(*t0) - Rs) < 1e-9
        t1 = Y + u * reach_p
        ax.plot([t0[0], t1[0]], [t0[1], t1[1]], color=INC, lw=1.4, zorder=3)
        t_sun = foot((0, 0), X, np.array([-np.cos(s_u), sgn * np.sin(s_u)]))
        ax.plot([t_sun[0], X[0]], [t_sun[1], X[1]], color=INC, lw=1.4, zorder=3)
        ax.plot([X[0], X[0] + (xr - x_u)], [0, sgn * (xr - x_u) * np.tan(s_u)], color=INC, lw=1.2, ls=DASH, zorder=3)
    sphere(ax, (0, 0), Rs, tint(SUN, 0.45))  # a pale body fill: the star marker stays full strength
    sphere(ax, (xm, 0), rm, tint(INK, 0.65))
    sphere(ax, (xe, 0), re, tint(SKY, 0.7))
    label(ax, (0, 0), "Солнце", 12, weight="bold")
    return X, Y


@fig
def light_solar_eclipse():
    f, axs = blank_multi(2, 1, 12.4, 7.6, (-3.6, 17.4), (-3.4, 3.4))
    Rs, xm, rm, re = 3.0, 9.0, 0.9, 1.5
    ax = axs[0]
    xe = 11.6
    X, Y = eclipse_panel(ax, Rs, xm, rm, xe, re, 17.2)
    x_u = X[0]
    hw_umbra = lambda x: rm * (x_u - x) / (x_u - xm)  # noqa: E731
    hw_pen = lambda x: rm * (x - Y[0]) / (xm - Y[0])  # noqa: E731
    p_total = P(xe - re, 0)
    th = np.deg2rad(40)
    p_part = P(xe - re * np.cos(th), re * np.sin(th))
    assert abs(p_total[1]) < hw_umbra(p_total[0])
    assert hw_umbra(p_part[0]) < abs(p_part[1]) < hw_pen(p_part[0])
    label(ax, (9.3, -2.75), "полное затмение\nв области тени", 10.5, color=RED)
    ax.plot([p_total[0], 9.7], [0, -2.2], color=RED, lw=1.2, zorder=9)
    label(ax, (10.2, 2.75), "частичное затмение\nв области полутени", 10.5, color=RED)
    ax.plot([p_part[0], 10.2], [p_part[1], 2.2], color=RED, lw=1.2, zorder=9)
    label(ax, (-3.4, 3.15), "масштаб не соблюдён", 10, color=GREY, ha="left")
    label(ax, (xe + 0.3, -re - 0.45), "Земля", 11.5)
    label(ax, (xm, rm + 0.4), "Луна", 11)
    ax = axs[1]
    xe2 = 15.4
    X, Y = eclipse_panel(ax, Rs, xm, rm, xe2, re, 17.2)
    assert xe2 - re > X[0], "the Earth must lie beyond the apex of the umbra"
    label(ax, (13.0, -2.75), "кольцевое затмение", 10.5, color=RED)
    ax.plot([xe2 - re, 13.6], [0, -2.3], color=RED, lw=1.2, zorder=9)
    label(ax, (xe2, re + 0.45), "Земля", 11.5)
    label(ax, (xm, rm + 0.4), "Луна", 11)
    label(ax, (-3.4, 3.15), "Луна дальше от Земли: конус тени до неё не достаёт", 10, color=GREY, ha="left")
    save14(f, "light-solar-eclipse")


@fig
def light_lunar_eclipse():
    f, ax = blank(12.4, 4.6, (-3.6, 17.4), (-3.5, 3.5))
    Rs, xe, re = 3.0, 9.0, 1.3
    X, Y = eclipse_panel(ax, Rs, xe, re, xe, re, 17.2)
    x_u = X[0]
    xm, rm = 13.3, 0.3
    assert rm < re * (x_u - xm) / (x_u - xe), "the Moon must fit into the umbra"
    ax.add_patch(Circle((xe, 0), re * 1.08, fc="none", ec=INC, lw=2.2, zorder=7))
    sphere(ax, (xm, 0), rm, COPPER, z=7)
    label(ax, (xe, -re - 0.55), "Земля и её атмосфера", 10.5)
    label(ax, (xm + 0.3, -1.25), "Луна в тени Земли", 10.5, color=RED, bg=True)
    label(ax, (12.4, 2.55), "полутень", 10.5)
    label(ax, (-3.4, 3.25), "масштаб не соблюдён", 10, color=GREY, ha="left")
    save14(f, "light-lunar-eclipse")


# ------------------------------------------------------------------ pinhole camera


def tree_polys(cx, base, top):
    """Conifer between y=base and y=top as a list of polygons."""
    k = (top - base) / 3.0
    return [
        [(cx, base + 3.0 * k), (cx - 0.6 * k, base + 1.9 * k), (cx + 0.6 * k, base + 1.9 * k)],
        [(cx, base + 2.4 * k), (cx - 0.8 * k, base + 1.1 * k), (cx + 0.8 * k, base + 1.1 * k)],
        [(cx, base + 1.6 * k), (cx - 1.0 * k, base + 0.4 * k), (cx + 1.0 * k, base + 0.4 * k)],
        [(cx - 0.15 * k, base + 0.4 * k), (cx + 0.15 * k, base + 0.4 * k), (cx + 0.15 * k, base), (cx - 0.15 * k, base)],
    ]


@fig
def light_pinhole():
    f, ax = blank(11.0, 5.4, (-7.4, 4.8), (-2.6, 2.7))
    A, B = P(-5, 2.0), P(-5, -1.0)
    for poly_ in tree_polys(-5, -1.0, 2.0):
        poly(ax, poly_, fc=tint(GREEN, 0.7), ec=INK, lw=1.2, zorder=4)
    wall_h = 1.9
    ax.plot([0, 0], [0.09, wall_h], color=INK, lw=3.0, zorder=6)
    ax.plot([0, 0], [-0.09, -wall_h], color=INK, lw=3.0, zorder=6)
    ax.plot([0, 3, 3, 0], [wall_h, wall_h, -wall_h, -wall_h], color=INK, lw=3.0, zorder=6)
    k = 3.0 / 5.0  # the image is smaller in the ratio of the distances from the hole
    A1, B1 = P(3, -A[1] * k), P(3, -B[1] * k)
    assert abs(A1[1] + 1.2) < 1e-9 and abs(B1[1] - 0.6) < 1e-9
    ray(ax, A, A1, marks=(0.35, 0.8))
    ray(ax, B, B1, marks=(0.35, 0.8))
    ray(ax, P(-5, 0.5), P(3, -0.3), marks=(), lw=1.3, alpha=0.6)
    for poly_ in tree_polys(-5, -1.0, 2.0):  # the image: turned by 180 degrees about the hole and scaled
        poly(ax, [(3.0 - k * (x + 5), -k * y) for x, y in poly_], fc=tint(GREEN, 0.85), ec=INK, lw=1.0, zorder=5)
    label(ax, A, "A", 12, dx=0.3, dy=0.25, weight="bold")
    label(ax, B, "B", 12, dx=0.3, dy=-0.25, weight="bold")
    label(ax, A1, "A$'$", 12, dx=0.35, dy=-0.1, weight="bold")
    label(ax, B1, "B$'$", 12, dx=0.35, dy=0.1, weight="bold")
    label(ax, (-1.4, 1.1), "отверстие", 11)
    ax.plot([-0.95, -0.05], [0.95, 0.12], color=GREY, lw=0.9)
    label(ax, (3.0, 2.3), "экран", 11)
    label(ax, (1.5, -2.35), "перевёрнутое изображение, оно тусклое", 10.5)
    label(ax, (-5, -1.75), "предмет", 11)
    save14(f, "light-pinhole")


@fig
def light_pinhole_size():
    f, axs = blank_multi(1, 2, 12.0, 4.6, (-4.6, 3.8), (-2.5, 2.5))
    P0 = P(-4.0, 1.4)
    for ax, h, title in zip(axs, (0.12, 0.9), ("малое отверстие: чёткое изображение, но тусклое", "большое отверстие: светлее, но размытое")):
        ax.plot([0, 0], [h / 2, 2.2], color=INK, lw=3.0, zorder=6)
        ax.plot([0, 0], [-h / 2, -2.2], color=INK, lw=3.0, zorder=6)
        ax.plot([3, 3], [-2.2, 2.2], color=INK, lw=2.4, zorder=6)
        star(ax, *P0, size=14)
        hits = []
        for edge in (h / 2, -h / 2):
            end = P(3, P0[1] + (edge - P0[1]) * 7.0 / 4.0)
            hits.append(end[1])
            ray(ax, P0, end, marks=(0.45,), lw=1.6)
        ax.plot([3.0, 3.0], hits, color=RED, lw=5.0, zorder=8, solid_capstyle="butt")
        label(ax, (-0.3, 2.45), title, 11, weight="bold")
        label(ax, (3.35, np.mean(hits)), "пятно", 10.5, color=RED, ha="left")
    save14(f, "light-pinhole-size")


# ------------------------------------------------------------------ problems on rectilinear propagation


@fig
def light_tree_shadow():
    f, ax = blank(11.6, 3.9, (-9.0, 41.5), (-2.4, 13.6))
    h, l, H, L = 1.8, 4.5, 12.0, 30.0
    xt = 9.0
    slope = h / l
    assert abs(H / L - slope) < 1e-9
    ax.plot([-9, 41], [0, 0], color=INK, lw=2.0, zorder=3)
    fill(ax, [(0, 0), (0, h), (l, 0)], tint(INK, 0.8), alpha=0.9, z=2)
    fill(ax, [(xt, 0), (xt, H), (xt + L, 0)], tint(INK, 0.8), alpha=0.6, z=2)
    ax.plot([0, 0], [0, h], color=INK, lw=3.0, zorder=6)
    ax.add_patch(Circle((0, h + 0.3), 0.3, fc=PAPER, ec=INK, lw=1.6, zorder=6))
    poly(ax, [(xt, H), (xt - 1.6, 5.0), (xt + 1.6, 5.0)], fc=tint(GREEN, 0.7), ec=INK, lw=1.2, zorder=5)
    poly(ax, [(xt, H - 3.2), (xt - 2.4, 2.6), (xt + 2.4, 2.6)], fc=tint(GREEN, 0.7), ec=INK, lw=1.2, zorder=5)
    ax.plot([xt, xt], [0, H], color=INK, lw=2.6, zorder=6)
    for x0, top in ((0, h), (xt, H)):
        ray(ax, P(x0 - 6.5, top + 6.5 * slope), P(x0 + top / slope, 0), marks=(0.3,), lw=1.6)
    dim(ax, P(-1.0, 0), P(-1.0, h))
    label(ax, (-2.3, h / 2), "$h$ = 1,8 м", 10.5, ha="right")
    dim(ax, P(xt - 3.3, 0), P(xt - 3.3, H))
    label(ax, (xt - 4.0, H / 2), "$H$ = ?", 11, ha="right")
    dim(ax, P(0, -0.9), P(l, -0.9), "$l$ = 4,5 м", off=(0, -0.75))
    dim(ax, P(xt, -0.9), P(xt + L, -0.9), "$L$ = 30 м", off=(0, -0.75))
    right_angle(ax, (0, 0), (1, 0), (0, 1), s=0.5)
    right_angle(ax, (xt, 0), (1, 0), (0, 1), s=0.5)
    save14(f, "light-tree-shadow")


@fig
def light_apple_fence():
    f, ax = plt.subplots(figsize=(11.6, 4.0))
    ax.set_xlim(-16, 112)
    ax.set_ylim(-9.5, 9.5)
    ax.axis("off")
    d, D, L = 1.0, 12.0, 100.0
    lx = L * d / (D - d)
    assert abs(lx - 100 / 11) < 1e-9
    O = P(-lx, 0)
    ax.plot([0, 0], [d / 2, 8.6], color=INK, lw=5.0, solid_capstyle="butt", zorder=6)
    ax.plot([0, 0], [-d / 2, -8.6], color=INK, lw=5.0, solid_capstyle="butt", zorder=6)
    ax.add_patch(Ellipse((L, 0), 5.0, D, fc=tint(RED, 0.7), ec=INK, lw=1.6, zorder=5))
    ax.plot([L, L], [-D / 2, D / 2], color=INK, lw=1.0, ls=DASH, zorder=6)
    for edge, end in ((d / 2, P(L, D / 2)), (-d / 2, P(L, -D / 2))):
        ray(ax, end, O, marks=(0.5,), lw=1.8)
        assert abs(end[1] + (O[1] - end[1]) * L / (L + lx) - edge) < 1e-9  # the ray touches the edge of the hole
    ax.plot([-16, 105], [0, 0], color=GREY, lw=0.9, ls=DASH)
    eye(ax, O[0] - 1.5, 0, s=2.0)
    ax.text(O[0] - 1.5, -2.6, "глаз O", fontsize=11, ha="center")
    ax.text(0, 9.25, "забор", fontsize=11, ha="center")
    ax.text(L, 8.4, "яблоко", fontsize=11, ha="center")
    ax.text(L + 4.0, D / 2, "A$'$", fontsize=12, ha="left", va="center", weight="bold")
    ax.text(L + 4.0, -D / 2, "B$'$", fontsize=12, ha="left", va="center", weight="bold")
    ax.text(-2.4, d / 2 + 0.3, "A", fontsize=12, ha="right", va="bottom", weight="bold")
    ax.text(-2.4, -d / 2 - 0.3, "B", fontsize=12, ha="right", va="top", weight="bold")
    arrow(ax, (L + 10, -D / 2), (L + 10, D / 2), color=GREY, lw=1.2, style="<|-|>", scale=9)
    ax.text(L + 12, 0, "$D$ = 12 см", fontsize=10.5, ha="left", va="center")
    arrow(ax, (0, -7.6), (L, -7.6), color=GREY, lw=1.2, style="<|-|>", scale=9)
    ax.text(L / 2, -8.5, "$L$ = 1 м", fontsize=10.5, ha="center")
    arrow(ax, (O[0], -5.0), (0, -5.0), color=GREY, lw=1.2, style="<|-|>", scale=9)
    ax.text(O[0] / 2, -6.0, "$l$", fontsize=11.5, ha="center")
    ax.text(3.0, 2.2, "$d$ = 1 см", fontsize=10.5, ha="left")
    ax.text(58, 6.6, "масштабы по осям разные", fontsize=9.5, color=GREY)
    save14(f, "light-apple-fence")


@fig
def light_lamp_ball():
    f, ax = blank(8.6, 6.4, (-4.6, 4.6), (-1.0, 5.9))
    R, r, H, h = 2.0, 1.0, 5.0, 1.0  # horizontal in tens of centimetres, vertical in metres
    umbra = (r * H - R * h) / (H - h)
    pen = (R * h + r * H) / (H - h)
    assert abs(umbra - 0.75) < 1e-9 and abs(pen - 1.75) < 1e-9
    fill(ax, [(-r, h), (-pen, 0), (pen, 0), (r, h)], PENUMBRA, alpha=0.8, z=1)
    fill(ax, [(-r, h), (-umbra, 0), (umbra, 0), (r, h)], UMBRA, alpha=0.9, z=2)
    ax.plot([-4.2, 4.2], [0, 0], color=INK, lw=2.4, zorder=5)
    ax.plot([-R, R], [H, H], color=INC, lw=7.0, solid_capstyle="butt", zorder=6)
    ax.plot([-r, r], [h, h], color=INK, lw=7.0, solid_capstyle="butt", zorder=6)
    ax.plot([0, 0], [-0.3, 5.5], color=GREY, lw=1.0, ls=DASH, zorder=1)
    for s in (1, -1):
        ray(ax, P(s * R, H), P(s * umbra, 0), marks=(0.5,), lw=1.6)
        ray(ax, P(s * R, H), P(-s * pen, 0), marks=(0.5,), lw=1.6, alpha=0.75)
    dim(ax, P(-umbra, -0.35), P(umbra, -0.35), color=RED)
    dim(ax, P(-pen, -0.75), P(pen, -0.75), color=RED)
    label(ax, (2.15, -0.35), "$d_{т}$ = 15 см", 10.5, color=RED, ha="left")
    label(ax, (2.15, -0.78), "$d_{п}$ = 35 см", 10.5, color=RED, ha="left")
    label(ax, (R + 0.25, H), "лампа, $R$ = 20 см", 10.5, ha="left")
    label(ax, (r + 0.25, h), "шар, $r$ = 10 см", 10.5, ha="left")
    dim(ax, P(-3.3, 0), P(-3.3, H))
    label(ax, (-3.55, H / 2), "$H$ = 5 м", 10.5, ha="right")
    dim(ax, P(-2.7, 0), P(-2.7, h))
    label(ax, (-3.0, 0.5), "$h$", 10.5, ha="right")
    label(ax, (3.95, 4.3), "по горизонтали\nмасштаб в 10 раз\nкрупнее, чем по\nвертикали", 9.5, color=GREY, ha="right")
    save14(f, "light-lamp-ball")


# ------------------------------------------------------------------ reflection


@fig
def mirror_diffuse_specular():
    f, axs = blank_multi(1, 2, 12.0, 4.4, (-1.0, 7.4), (-1.0, 3.8))
    d = polar(-50, 1.0)
    ax = axs[0]
    angles = [18, -14, 8, -22, 12, -6]  # slopes of the facets of a rough surface, degrees
    pts = [P(0.2, 0.0)]
    for a in angles:
        pts.append(pts[-1] + polar(a, 1.05))
    for p, q in zip(pts[:-1], pts[1:]):
        ax.plot([p[0], q[0]], [p[1], q[1]], color=INK, lw=3.0, zorder=5, solid_capstyle="round")
    fill(ax, pts + [(pts[-1][0], -0.7), (pts[0][0], -0.7)], SOFT, z=1)
    for p, q in zip(pts[:-1], pts[1:]):
        mid = (p + q) / 2
        u = unit(q - p)
        n = np.array([-u[1], u[0]])
        r = d - 2 * np.dot(d, n) * n
        assert np.dot(d, n) < 0 and r[1] > 0 and abs(np.dot(-d, n) - np.dot(r, n)) < 1e-9  # equal angles with the local normal
        ray(ax, mid - d * 2.3, mid, marks=(0.5,), lw=1.7)
        ray(ax, mid, mid + r * 1.9, marks=(0.6,), color=REF, lw=1.7)
    label(ax, (3.6, 3.55), "диффузное отражение", 12, weight="bold")
    label(ax, (3.6, -0.45), "шероховатая поверхность", 10.5, color=GREY)
    ax = axs[1]
    mirror_line(ax, P(0.0, 0.0), P(7.2, 0.0), side=-1, lw=3.2)
    r = np.array([d[0], -d[1]])
    for x in (1.6, 3.4, 5.2):
        ray(ax, P(x, 0) - d * 2.3, P(x, 0), marks=(0.5,), lw=1.7)
        ray(ax, P(x, 0), P(x, 0) + r * 1.9, marks=(0.6,), color=REF, lw=1.7)
    label(ax, (3.6, 3.55), "зеркальное отражение", 12, weight="bold")
    label(ax, (3.6, -0.75), "гладкая поверхность", 10.5, color=GREY)
    save14(f, "mirror-diffuse-specular")


@fig
def mirror_roughness_wavelength():
    f, axs = blank_multi(1, 2, 12.0, 4.4, (-0.5, 7.0), (-0.9, 4.2))
    d = polar(-55, 1.0)

    def lam_bar(ax, x0=4.4, y=3.45, lam=0.2):
        """Wavelength mark: a short bar with end ticks, as arrowheads would cover a segment this short."""
        ax.plot([x0, x0 + lam], [y, y], color=BLUE, lw=1.8, zorder=7)
        for x in (x0, x0 + lam):
            ax.plot([x, x], [y - 0.1, y + 0.1], color=BLUE, lw=1.8, zorder=7)
        ax.text(x0 + lam / 2, y + 0.3, "$\\lambda$", fontsize=10.5, color=BLUE, ha="center", va="center", zorder=12)

    # left: bumps much larger than the wavelength, right: much smaller
    ax = axs[0]
    pitch, amp = 2.0, 0.28  # D = 2.0 against lambda = 0.2 below: D is ten times larger
    xs = np.arange(0.2, 6.8, pitch / 2)
    ys = [amp if i % 2 == 0 else 0.0 for i in range(len(xs))]
    ax.plot(xs, ys, color=INK, lw=2.4, zorder=5)
    fill(ax, list(zip(xs, ys)) + [(xs[-1], -0.6), (xs[0], -0.6)], SOFT, z=1)
    for i in range(len(xs) - 1):
        p, q = P(xs[i], ys[i]), P(xs[i + 1], ys[i + 1])
        mid = (p + q) / 2
        u = unit(q - p)
        n = np.array([-u[1], u[0]])
        n = n if n[1] > 0 else -n
        r = d - 2 * np.dot(d, n) * n
        assert r[1] > 0
        ray(ax, mid - d * 2.0, mid, marks=(0.5,), lw=1.6)
        ray(ax, mid, mid + r * 1.6, marks=(0.6,), color=REF, lw=1.6)
    dim(ax, P(xs[0], -0.35), P(xs[2], -0.35), "$D$", off=(0, -0.3))
    lam_bar(ax)
    label(ax, (3.3, 4.0), "$D\\gg\\lambda$: отражение диффузное", 11.5, weight="bold")
    ax = axs[1]
    ax.plot([0.2, 6.8], [0, 0], color=INK, lw=3.0, zorder=5)
    fill(ax, [(0.2, 0), (6.8, 0), (6.8, -0.6), (0.2, -0.6)], SOFT, z=1)
    for x in (1.6, 3.4, 5.2):
        ray(ax, P(x, 0) - d * 2.0, P(x, 0), marks=(0.5,), lw=1.6)
        ray(ax, P(x, 0), P(x, 0) + np.array([d[0], -d[1]]) * 1.6, marks=(0.6,), color=REF, lw=1.6)
    lam_bar(ax)
    label(ax, (3.3, 4.0), "$D\\ll\\lambda$: отражение зеркальное", 11.5, weight="bold")
    label(ax, (3.3, -0.4), "атомные неровности много меньше $\\lambda$", 10, color=GREY, bg=True)
    save14(f, "mirror-roughness-wavelength")


@fig
def mirror_law_terms():
    f, ax = blank(9.4, 5.6, (-4.3, 5.0), (-2.3, 4.0))
    a = 40.0
    L = 3.3
    O = P(0, 0)
    mirror_line(ax, P(-4.0, 0), P(4.0, 0), side=-1, lw=3.2)
    ax.plot([0, 0], [0.0, 3.6], color=GREY, lw=1.3, ls=DASH, zorder=3)
    inc_from, ref_to = polar(90 + a, L), polar(90 - a, L)
    ray(ax, inc_from, O, marks=(0.55,), lw=2.2)
    ray(ax, O, ref_to, marks=(0.55,), color=REF, lw=2.2)
    arc_label(ax, O, 1.3, 90, 90 + a, "$\\alpha$", color=INC, lr=1.3, size=14)
    arc_label(ax, O, 1.3, 90 - a, 90, "$\\gamma$", color=REF, lr=1.3, size=14)
    arc_label(ax, O, 0.75, 90 + a, 180, "$\\varphi$", color=GREY, lr=1.55, size=12)
    right_angle(ax, O, (1, 0), (0, 1), s=0.28)
    dot(ax, O, INK, 7)
    label(ax, (0.05, -0.55), "точка падения", 10.5)
    label(ax, (0.05, 3.85), "перпендикуляр (нормаль)", 10.5)
    label(ax, inc_from, "падающий луч", 10.5, dy=0.3)
    label(ax, ref_to, "отражённый луч", 10.5, dy=0.3)
    label(ax, (3.9, 0.45), "отражающая\nповерхность", 10.5)
    label(ax, (-3.2, 0.72), "угол\nскольжения", 9.5, color=GREY)
    label(ax, (-4.1, -1.6), "$\\alpha$ — угол падения,  $\\gamma$ — угол отражения,  $\\gamma=\\alpha$", 11, ha="left")
    save14(f, "mirror-law-terms")


@fig
def mirror_task_two_rays():
    f, ax = blank(8.6, 5.0, (-4.4, 4.6), (-0.9, 3.9))
    O = P(0, 0)
    a1, a2 = 25.0, 35.0
    mirror_line(ax, P(-4.0, 0), P(4.0, 0), side=-1, lw=3.2)
    ax.plot([0, 0], [0, 3.6], color=GREY, lw=1.3, ls=DASH, zorder=3)
    L = 3.3
    ray(ax, polar(90 + a1, L), O, marks=(0.55,), lw=2.0)
    ray(ax, polar(90 + a2, L), O, marks=(0.55,), lw=2.0, color=BLUE)
    ray(ax, O, polar(90 - a1, L), marks=(0.55,), color=REF, lw=2.0)
    ray(ax, O, polar(90 - a2, L), marks=(0.55,), color=RAY3, lw=2.0)
    arc_label(ax, O, 1.0, 90 + a1, 90 + a2, "$\\varphi$", lr=1.45, size=13)
    arc_label(ax, O, 1.0, 90 - a2, 90 - a1, "$\\delta$", lr=1.45, size=13)
    arc_label(ax, O, 1.8, 90, 90 + a1, "$\\alpha_1$", lr=1.12, size=11, color=INC)
    arc_label(ax, O, 2.4, 90, 90 + a2, "$\\alpha_2$", lr=1.1, size=11, color=BLUE)
    arc_label(ax, O, 1.8, 90 - a1, 90, "$\\gamma_1$", lr=1.12, size=11, color=REF)
    arc_label(ax, O, 2.4, 90 - a2, 90, "$\\gamma_2$", lr=1.1, size=11, color=RAY3)
    label(ax, (-3.6, 3.5), "$\\varphi=\\alpha_2-\\alpha_1$\n$\\delta=\\gamma_2-\\gamma_1=\\alpha_2-\\alpha_1=\\varphi$", 10.5, ha="left", va="top")
    save14(f, "mirror-task-two-rays")


@fig
def mirror_task_glancing():
    f, ax = blank(9.0, 4.8, (-4.4, 4.8), (-0.9, 3.7))
    O = P(0, 0)
    alpha = 72.0
    assert abs(alpha / (90 - alpha) - 4) < 1e-9  # the angle of incidence is four times the glancing angle
    mirror_line(ax, P(-4.0, 0), P(4.0, 0), side=-1, lw=3.2)
    ax.plot([0, 0], [0, 3.4], color=GREY, lw=1.3, ls=DASH, zorder=3)
    L = 3.6
    ray(ax, polar(90 + alpha, L), O, marks=(0.55,), lw=2.2)
    ray(ax, O, polar(90 - alpha, L), marks=(0.55,), color=REF, lw=2.2)
    arc_label(ax, O, 1.3, 90, 90 + alpha, "$\\alpha$", color=INC, lr=1.25, size=14)
    arc_label(ax, O, 1.3, 90 - alpha, 90, "$\\gamma$", color=REF, lr=1.25, size=14)
    arc_label(ax, O, 0.9, 90 + alpha, 180, "$\\varphi$", color=GREY, lr=1.7, size=13)
    label(ax, (3.6, 2.6), "$\\alpha=4\\varphi$\n$\\varphi+\\alpha=90^\\circ$\n$\\gamma=\\alpha=72^\\circ$", 11)
    save14(f, "mirror-task-glancing")


@fig
def mirror_construct_reflected():
    f, ax = blank(9.0, 5.4, (-4.2, 4.8), (-2.4, 3.6))
    O = P(0, 0)
    mirror_line(ax, P(-4.0, 0), P(4.0, 0), side=-1, lw=3.2)
    inc = P(-3.0, 2.6)
    # the normal with a compass: equal marks a and b on the mirror, then arcs of one larger radius from a and b
    a, b = P(-1.0, 0), P(1.0, 0)
    rho = 1.9
    h = np.sqrt(rho**2 - 1.0)
    for c in (a, b):
        ax.plot([c[0], c[0]], [-0.12, 0.12], color=INK, lw=1.4, zorder=6)
        for sgn in (1, -1):
            compass_arc(ax, c, rho, P(0, sgn * h))
    ax.plot([0, 0], [-h, h + 0.75], color=GREY, lw=1.4, ls=DASH, zorder=3)
    for sgn in (1, -1):
        dot(ax, P(0, sgn * h), GREY, 4)
    ray(ax, inc, O, marks=(0.55,), lw=2.2)
    al = np.degrees(np.arctan2(-inc[0], inc[1]))
    ray(ax, O, polar(90 - al, np.hypot(*inc)), marks=(0.55,), color=REF, lw=2.2)
    arc_label(ax, O, 1.0, 90, 90 + al, "$\\alpha$", color=INC, lr=1.35, size=13)
    arc_label(ax, O, 1.0, 90 - al, 90, "$\\gamma$", color=REF, lr=1.35, size=13)
    right_angle(ax, O, (1, 0), (0, 1), s=0.25)
    label(ax, (-1.0, -0.4), "a", 10.5, color=GREY)
    label(ax, (1.0, -0.4), "b", 10.5, color=GREY)
    label(ax, (-2.3, 2.9), "дуги одного радиуса\nиз точек a и b", 9.5, color=GREY)
    ax.plot([-1.3, -0.1], [2.55, h], color=GREY, lw=0.8)
    save14(f, "mirror-construct-reflected")


@fig
def mirror_construct_mirror():
    f, ax = blank(9.0, 5.6, (-4.0, 4.6), (-1.6, 4.6))
    O = P(0, 0)
    ang_i, ang_r = 140.0, 35.0
    Pi, Pr = polar(ang_i, 1.4), polar(ang_r, 1.4)
    ray(ax, polar(ang_i, 3.9), O, marks=(0.6,), lw=2.2)
    ray(ax, O, polar(ang_r, 3.9), marks=(0.6,), color=REF, lw=2.2)
    # the bisector with a compass: equal marks on both rays, then arcs of one radius from the marks
    rho = 1.25
    mid = (Pi + Pr) / 2
    half = np.hypot(*(Pi - Pr)) / 2
    bis_dir = unit(mid)
    Q = mid + bis_dir * np.sqrt(rho**2 - half**2)
    for c in (Pi, Pr):
        dot(ax, c, GREY, 4)
        compass_arc(ax, c, rho, Q, half=16)
    Bis = bis_dir * 3.5
    dashed(ax, O, Bis, color=GREY, lw=1.4)
    dot(ax, Q, GREY, 4)
    bis_ang = np.degrees(np.arctan2(bis_dir[1], bis_dir[0]))
    assert abs(bis_ang - (ang_i + ang_r) / 2) < 1e-9
    mdir = polar(bis_ang - 90, 1.0)
    mirror_line(ax, -mdir * 3.6, mdir * 3.6, side=-1, lw=3.2)
    arc_label(ax, O, 1.0, bis_ang, ang_i, "$\\alpha$", color=INC, lr=1.3, size=13)
    arc_label(ax, O, 1.0, ang_r, bis_ang, "$\\gamma$", color=REF, lr=1.3, size=13)
    right_angle(ax, O, bis_dir, mdir, s=0.3)
    label(ax, Bis, "биссектриса = нормаль", 10.5, dy=0.3)
    label(ax, mdir * 3.6, "зеркало", 10.5, dy=-0.4)
    label(ax, polar(ang_i, 3.9), "падающий", 10.5, dy=0.3)
    label(ax, polar(ang_r, 3.9), "отражённый", 10.5, dy=0.3, dx=0.3)
    save14(f, "mirror-construct-mirror")


@fig
def mirror_task_well():
    f, ax = blank(8.4, 6.6, (-3.6, 4.0), (-3.2, 3.9))
    phi = 60.0
    d_in = polar(-phi, 1.0)  # the rays go down and to the right
    d_out = P(0, -1)
    n = unit(d_out - d_in)
    surf = np.array([-n[1], n[0]])
    surf = surf if surf[1] < 0 else -surf  # the mirror leans like a backslash
    assert np.allclose(reflect_dir(d_in, surf), d_out)
    eps = np.degrees(np.arctan2(abs(surf[1]), abs(surf[0])))
    assert abs(eps - 75.0) < 1e-9
    O = P(0, 1.1)
    ax.plot([-3.4, -0.9], [0, 0], color=INK, lw=2.6, zorder=5)
    ax.plot([0.9, 3.8], [0, 0], color=INK, lw=2.6, zorder=5)
    # hatching goes into the ground, outside the shaft, as on the board
    wall_line(ax, P(-0.9, 0), P(-0.9, -3.0), side=-1, lw=2.6, tick=0.2, step=0.35)
    wall_line(ax, P(0.9, 0), P(0.9, -3.0), side=+1, lw=2.6, tick=0.2, step=0.35)
    mirror_line(ax, O - surf * 0.9, O + surf * 0.9, side=1, lw=3.4)
    ray(ax, O - d_in * 3.0, O, marks=(0.45,), lw=2.3)
    ray(ax, O, P(0, -3.0), marks=(0.4, 0.75), color=REF, lw=2.3)
    dashed(ax, O + P(-1.6, 0), O + P(1.0, 0), color=GREY)
    arc_label(ax, O, 0.9, 120, 180, "$\\varphi$", color=INC, lr=1.35, size=13)
    arc_label(ax, O, 0.75, np.degrees(np.arctan2(surf[1], surf[0])), 0, "$\\varepsilon$", color=INK, lr=1.5, size=13)
    label(ax, (-0.95, 2.05), "зеркало", 10.5, ha="right")
    label(ax, (-2.6, 2.5), "лучи Солнца", 10.5)
    label(ax, (0.0, -3.4), "$\\varepsilon=\\dfrac{\\varphi+90^\\circ}{2}=75^\\circ$", 12.5, weight="bold")
    save14(f, "mirror-task-well")


@fig
def mirror_task_sunbeam():
    f, ax = blank(9.2, 5.4, (-3.6, 2.6), (-1.2, 2.9))
    A, C, B = P(-2.0, 0), P(0, 0), P(0, 2.0)
    phi, eps = 25.0, 10.0
    d_in = polar(-phi, 1.0)
    surf = polar(eps, 1.0)
    assert np.allclose(reflect_dir(d_in, surf), unit(B - A))  # the mirror at A turns the ray to B
    ax.plot([-3.4, 1.2], [0, 0], color=INK, lw=2.4, zorder=3)
    wall_line(ax, P(0, 0), P(0, 2.6), side=-1, lw=2.4, tick=0.16, step=0.25)
    mirror_line(ax, A - surf * 0.6, A + surf * 0.6, side=-1, lw=3.6, tick=0.14, step=0.2)
    ray(ax, A - d_in * 2.6, A, marks=(0.5,), lw=2.3)
    ray(ax, A, B, marks=(0.55,), color=REF, lw=2.3)
    arc_label(ax, A, 0.9, 180 - phi, 180, "$\\varphi$", color=INC, lr=1.45, size=12)
    arc_label(ax, A, 1.1, 0, eps, "$\\varepsilon$", color=INK, lr=1.25, size=12)  # arc beyond the mirror end (0.6)
    ax.add_patch(Arc(A, 1.7, 1.7, theta1=eps, theta2=45, color=REF, lw=1.4, zorder=6))
    label(ax, A + polar(28, 1.05), "45°", 10.5, color=REF)
    label(ax, A, "A", 13, dx=-0.15, dy=-0.5, weight="bold")
    label(ax, B, "B", 13, dx=0.3, weight="bold")
    label(ax, C, "C", 13, dx=0.3, dy=-0.3, weight="bold")
    dim(ax, P(-2.0, -0.9), P(0.0, -0.9), "$AC$ = 20 м", off=(0, -0.3))
    dim(ax, P(0.75, 0.0), P(0.75, 2.0), "$BC$ = 20 м", off=(0.3, 0), rotation=90)
    label(ax, (-3.0, 1.8), "лучи Солнца", 10.5)
    save14(f, "mirror-task-sunbeam")


@fig
def mirror_task_two_mirrors():
    f, ax = blank(9.0, 6.6, (-1.0, 5.4), (-0.9, 5.6))
    alpha = 60.0  # angle of incidence on the first mirror
    beta = 90 - alpha
    mirror_line(ax, P(0, 0), P(5.0, 0), side=-1, lw=3.4)
    mirror_line(ax, P(0, 0), P(0, 5.2), side=-1, lw=3.4)
    d = P(-np.cos(np.deg2rad(beta)), -np.sin(np.deg2rad(beta)))
    d2 = reflect_dir(d, P(1, 0))
    d3 = reflect_dir(d2, P(0, 1))
    assert np.allclose(d3, -d), "after two reflections the ray goes back"
    H1 = P(2.8, 0)
    H2 = H1 + d2 * (-H1[0] / d2[0])
    ray(ax, H1 - d * 3.0, H1, marks=(0.5,), lw=2.3)
    ray(ax, H1, H2, marks=(0.5,), color=REF, lw=2.3)
    ray(ax, H2, H2 + d3 * 3.4, marks=(0.7,), color=RAY3, lw=2.3)
    dashed(ax, H1, H1 + P(0, 1.6))
    dashed(ax, H2, H2 + P(1.6, 0))
    arc_label(ax, H1, 0.9, 90, 90 + alpha, "$\\alpha$", color=INC, lr=1.3, size=12)
    arc_label(ax, H1, 0.9, 90 - alpha, 90, "$\\alpha$", color=REF, lr=1.3, size=12)
    ax.add_patch(Arc(H2, 1.8, 1.8, theta1=0, theta2=beta, color=RAY3, lw=1.5, zorder=6))
    ax.add_patch(Arc(H2, 2.4, 2.4, theta1=-beta, theta2=0, color=REF, lw=1.5, zorder=6))
    label(ax, H2 + P(1.75, 0.32), "$90^\\circ-\\alpha$", 10.5, color=RAY3)
    label(ax, H2 + P(1.85, -0.42), "$90^\\circ-\\alpha$", 10.5, color=REF)
    right_angle(ax, P(0, 0), (1, 0), (0, 1), s=0.3)
    label(ax, (0.6, 0.6), "$90^\\circ$", 10.5)
    label(ax, (4.5, -0.4), "зеркало 1", 10.5)
    label(ax, (-0.5, 4.5), "зеркало 2", 10.5, rotation=90)
    label(ax, H1 - d * 3.0 + P(0.0, 0.3), "падающий", 10.5)
    label(ax, H2 + d3 * 3.4 + P(-0.6, 0.45), "выходящий: параллелен\nпадающему, направлен обратно", 10.5)
    save14(f, "mirror-task-two-mirrors")


# ------------------------------------------------------------------ plane mirror: images


def group_images(src, mirrors):
    """All images of a point produced by reflections in a set of lines."""
    found = [np.asarray(src, dtype=float)]
    frontier = [found[0]]
    while frontier:
        nxt = []
        for p in frontier:
            for a, b in mirrors:
                q = reflect_point(p, a, b)
                if not any(np.allclose(q, z, atol=1e-7) for z in found):
                    found.append(q)
                    nxt.append(q)
        frontier = nxt
    return found


@fig
def mirror_two_mirrors_images():
    f, axs = blank_multi(1, 2, 13.0, 6.4, (-3.9, 3.9), (-3.6, 3.9))
    for ax, alpha, title in ((axs[0], 90.0, "угол между зеркалами $90^\\circ$: три изображения"), (axs[1], 60.0, "угол между зеркалами $60^\\circ$: пять изображений")):
        O = P(0, 0)
        m1, m2 = polar(0, 1.0), polar(alpha, 1.0)
        S = polar(0.35 * alpha, 1.7)
        imgs = group_images(S, [(O, m1), (O, m2)])
        assert len(imgs) - 1 == int(round(360 / alpha)) - 1
        th = np.linspace(0, 2 * np.pi, 200)
        ax.plot(1.7 * np.cos(th), 1.7 * np.sin(th), color=GREY, lw=0.9, ls=DASH, zorder=1)
        ax.add_patch(Wedge((0, 0), 3.0, 0, alpha, fc=tint(WARM, 0.8), ec="none", alpha=0.7, zorder=0))
        mirror_line(ax, O, m1 * 3.0, side=-1, lw=3.2)
        mirror_line(ax, O, m2 * 3.0, side=+1, lw=3.2)
        star(ax, *S, size=16)
        label(ax, S, "S", 12, dx=0.25, dy=0.25, weight="bold")
        for i, q in enumerate(imgs[1:], 1):
            image_dot(ax, q)
            label(ax, q, f"S$_{i}$", 10.5, dx=0.36, dy=0.3, color=VIRT)
        label(ax, (0, 3.6), title, 11.5, weight="bold")
        label(ax, (0, -3.35), "не из лекции", 9.5, color=GREY)
    save14(f, "mirror-two-mirrors-images")


@fig
def mirror_virtual_box():
    f, ax = blank(9.4, 4.6, (-3.6, 7.2), (-2.4, 2.6))
    wall = dict(color=INK, lw=2.6, zorder=6, solid_capstyle="butt")
    rect(ax, -3.2, -1.8, 4.2, 3.6, fc=SOFT, ec="none", zorder=2)
    ax.plot([1.0, -3.2, -3.2, 1.0], [1.8, 1.8, -1.8, -1.8], **wall)
    ax.plot([1.0, 1.0], [0.6, 1.8], **wall)
    ax.plot([1.0, 1.0], [-0.6, -1.8], **wall)
    label(ax, (-1.1, 0.0), "?", 40, color=GREY)
    label(ax, (-1.1, -1.45), "зеркала, призмы, линзы…", 10, color=GREY)
    Sv = P(-0.2, 0.0)
    for a in (-16, -8, 0, 8, 16):
        t = np.tan(np.deg2rad(a))
        dashed(ax, Sv, P(1.0, Sv[1] + (1.0 - Sv[0]) * t), color=VIRT, lw=1.4)
        ray(ax, P(1.0, Sv[1] + (1.0 - Sv[0]) * t), P(5.4, Sv[1] + (5.4 - Sv[0]) * t), marks=(0.5,), lw=1.9)
    image_dot(ax, Sv, 9)
    label(ax, (Sv[0], -0.45), "S$'$", 12, color=VIRT, weight="bold")
    eye(ax, 6.3, 0.0, s=0.4)
    label(ax, (6.3, -0.6), "глаз", 10.5)
    label(ax, (1.6, 2.3), "видим точку там, где пересекаются продолжения лучей", 10.5)
    save14(f, "mirror-virtual-box")


@fig
def mirror_point_image():
    f, ax = blank(9.4, 6.2, (-4.0, 5.0), (-3.3, 3.7))
    O = P(0, 0)
    S, S1 = P(0, 2.4), P(0, -2.4)
    mirror_line(ax, P(-4.0, 0), P(4.6, 0), side=-1, lw=3.2)
    A, B = P(-1.7, 0), P(2.6, 0)
    assert np.allclose(reflect_point(S, A, B), S1)
    dashed(ax, S, S1, color=GREY, lw=1.3)
    for H in (A, B):
        d_ref = np.array([(H - S)[0], -(H - S)[1]])
        ray(ax, S, H, marks=(0.5,), lw=2.0)
        ray(ax, H, H + d_ref * 0.9, marks=(0.55,), color=REF, lw=2.0)
        dashed(ax, H, S1, color=VIRT, lw=1.6)
        assert np.allclose(unit(H - S1), unit(d_ref))  # the extension of the reflected ray passes through S'
    star(ax, *S, size=16)
    image_dot(ax, S1)
    label(ax, S, "S", 13, dx=0.35, weight="bold")
    label(ax, S1, "S$'$", 13, dx=0.4, weight="bold", color=VIRT)
    label(ax, A, "A", 12, dx=-0.15, dy=0.3, weight="bold")
    label(ax, B, "B", 12, dx=0.15, dy=0.3, weight="bold")
    label(ax, O, "O", 12, dx=-0.3, dy=0.3, weight="bold")
    right_angle(ax, O, (1, 0), (0, 1), s=0.28)
    right_angle(ax, O, (1, 0), (0, -1), s=0.28)
    tick(ax, S, O)
    tick(ax, O, S1)
    label(ax, (2.2, -1.2), "$SO=OS'$", 12, ha="left")
    label(ax, (-3.7, -2.4), "$\\triangle SAO=\\triangle S'AO$:\nпрямые углы при O,\nобщая сторона $AO$,\nравные острые углы", 10.5, ha="left")
    save14(f, "mirror-point-image")


@fig
def mirror_object_image():
    f, ax = blank(9.6, 4.6, (-4.4, 4.6), (-0.8, 3.4))
    wall_line(ax, P(0, -0.8), P(0, 3.3), side=-1, lw=3.2, tick=0.2, step=0.3)
    A, B = P(-3.0, 2.5), P(-3.0, 0.7)
    A1, B1 = P(3.0, 2.5), P(3.0, 0.7)
    arrow(ax, B, A, color=INK, lw=3.0, scale=20, zorder=6)
    arrow(ax, B1, A1, color=VIRT, lw=3.0, scale=20, zorder=6, linestyle=(0, (3, 2)))
    for p, q, n in ((A, A1, 1), (B, B1, 2)):
        dashed(ax, p, q, color=GREY)
        tick(ax, p, P(0, p[1]), n=n)
        tick(ax, P(0, p[1]), q, n=n)
    label(ax, A, "A", 13, dx=-0.3, dy=0.1, weight="bold")
    label(ax, B, "B", 13, dx=-0.3, weight="bold")
    label(ax, A1, "A$'$", 13, dx=0.4, dy=0.1, weight="bold", color=VIRT)
    label(ax, B1, "B$'$", 13, dx=0.4, weight="bold", color=VIRT)
    label(ax, (-3.0, -0.35), "предмет", 11)
    label(ax, (3.0, -0.35), "изображение: мнимое, прямое,\nв натуральную величину", 10.5, color=VIRT)
    save14(f, "mirror-object-image")


@fig
def mirror_left_right():
    f, axs = blank_multi(1, 2, 13.0, 5.2, (-4.6, 4.6), (-3.3, 2.8))

    def person(ax, cx, facing, left_col, right_col, left_txt, right_txt):
        ax.add_patch(Ellipse((cx, 0), 0.8, 1.7, fc=LIGHT, ec=INK, lw=1.6, zorder=6))
        poly(ax, [(cx + facing * 0.4, 0.22), (cx + facing * 0.7, 0), (cx + facing * 0.4, -0.22)], fc=INK, ec=INK, zorder=7)
        left_y = 1.0 if facing > 0 else -1.0  # seen from above, a person facing +x has the left hand at +y
        for yy, col, tx in ((left_y, left_col, left_txt), (-left_y, right_col, right_txt)):
            ax.add_patch(Circle((cx, yy * 1.38), 0.26, fc=col, ec=INK, lw=1.4, zorder=7))
            ax.text(cx, yy * 1.38, tx, fontsize=10.5, color=PAPER, ha="center", va="center", weight="bold", zorder=8)

    ax = axs[0]
    wall_line(ax, P(0, -2.6), P(0, 2.6), side=-1, lw=3.2, tick=0.2, step=0.3)
    person(ax, -2.4, +1, BLUE, RED, "Л", "П")
    # the image of the left hand (blue) keeps its place across the mirror, but the image faces the object, so it is the image's right hand
    person(ax, 2.4, -1, RED, BLUE, "Л", "П")
    ax.plot([-2.1, 2.1], [1.38, 1.38], color=BLUE, lw=0.9, ls=DASH, zorder=2)
    ax.plot([-2.1, 2.1], [-1.38, -1.38], color=RED, lw=0.9, ls=DASH, zorder=2)
    label(ax, (0, 2.85), "вид сверху: право и лево меняются местами", 11, weight="bold")
    label(ax, (-2.4, -2.45), "предмет", 10.5)
    label(ax, (2.4, -2.45), "изображение", 10.5, color=VIRT)
    label(ax, (0, -3.1), "цвет — чья это рука у предмета, буква — как её называет сам человек", 9.5, color=GREY)
    ax = axs[1]
    wall_line(ax, P(0, -2.6), P(0, 2.6), side=-1, lw=3.2, tick=0.2, step=0.3)
    for cx, col in ((-2.4, INK), (2.4, VIRT)):
        ax.plot([cx, cx], [-2.0, 1.2], color=col, lw=3.0, zorder=6)
        ax.add_patch(Circle((cx, 1.6), 0.4, fc=PAPER, ec=col, lw=1.8, zorder=6))
        label(ax, (cx, 2.3), "голова", 9.5, color=col)
        label(ax, (cx, -2.3), "ноги", 9.5, color=col)
    label(ax, (0, 2.85), "вид сбоку: верх и низ остаются на местах", 11, weight="bold")
    save14(f, "mirror-left-right")


# ------------------------------------------------------------------ plane mirror: visibility zones


@fig
def mirror_visibility_point():
    f, ax = blank(10.6, 6.6, (-5.0, 7.0), (-2.6, 4.4))
    a, b = P(-1.5, 0), P(1.5, 0)
    S = P(-0.4, 1.5)
    S1 = reflect_point(S, a, b)
    draw_zone(ax, (-5, 7), (0.02, 4.4), [S1], a, b)
    mirror_line(ax, a, b, side=-1, lw=3.6)
    for edge in (a, b):
        dashed(ax, S1, S1 + (edge - S1) * 4.3, color=GREY, lw=1.3)
        dashed(ax, S1, edge, color=VIRT, lw=1.2)
    star(ax, *S, size=16)
    image_dot(ax, S1)
    label(ax, S, "S", 13, dx=-0.3, dy=0.25, weight="bold")
    label(ax, S1, "S$'$", 13, dx=0.4, dy=-0.1, weight="bold", color=VIRT)
    E1, E2 = P(0.4, 3.2), P(4.3, 1.6)
    assert sees(E1, [S1], a, b) and not sees(E2, [S1], a, b)
    H1 = intersect(E1, S1 - E1, a, b - a)
    ray(ax, S, H1, marks=(0.5,), lw=1.9)
    ray(ax, H1, E1, marks=(0.5,), color=REF, lw=1.9)
    dashed(ax, H1, S1, color=VIRT, lw=1.3)
    eye(ax, E1[0], E1[1], ang=-10, s=0.3)
    label(ax, E1 + P(0.0, 0.45), "видит изображение", 10.5)
    H2 = intersect(E2, S1 - E2, a, b - a)
    dashed(ax, E2, H2, color=GREY, lw=1.3)
    dashed(ax, H2, S1, color=GREY, lw=1.0, alpha=0.6)
    ax.plot([H2[0]], [H2[1]], marker="x", color=RED, ms=8, mew=2.0, zorder=9)
    eye(ax, E2[0], E2[1], ang=-20, s=0.3)
    label(ax, E2 + P(0.9, -0.6), "не видит: в точке отражения\nзеркала нет", 10.5, color=RED)
    label(ax, (-1.8, 2.9), "область видимости", 11.5, weight="bold", color=ZONE_TEXT)
    save14(f, "mirror-visibility-point")


@fig
def mirror_visibility_extended():
    f, ax = blank(10.8, 6.8, (-5.0, 5.6), (-3.2, 4.6))
    a, b = P(-1.2, 0), P(1.2, 0)
    A, B = P(-1.6, 1.4), P(1.6, 1.4)
    A1, B1 = reflect_point(A, a, b), reflect_point(B, a, b)
    # the zone is a triangle on the mirror: its sides are the lines A'a and B'b, and they meet at the apex
    apex = intersect(A1, a - A1, B1, b - B1)
    assert abs(apex[0]) < 1e-9 and apex[1] > 0
    fill(ax, [a, apex, b], ZONE, alpha=0.9, z=0)
    mirror_line(ax, a, b, side=-1, lw=3.6)
    for im in (A1, B1):
        for edge in (a, b):
            dashed(ax, im, im + (edge - im) * 4.0, color=GREY, lw=1.2)
    arrow(ax, A, B, color=INK, lw=3.0, scale=18, zorder=6)
    arrow(ax, A1, B1, color=VIRT, lw=3.0, scale=18, zorder=6, linestyle=(0, (3, 2)))
    label(ax, A, "A", 13, dx=-0.3, dy=0.25, weight="bold")
    label(ax, B, "B", 13, dx=0.3, dy=0.25, weight="bold")
    label(ax, A1, "A$'$", 13, dx=-0.4, weight="bold", color=VIRT)
    label(ax, B1, "B$'$", 13, dx=0.4, weight="bold", color=VIRT)
    E_full, E_part = P(0.0, 2.3), P(2.5, 1.5)
    assert sees(E_full, [A1, B1], a, b)
    assert sees(E_part, [A1], a, b) and not sees(E_part, [B1], a, b)
    for e, text, col in ((E_full, "виден весь предмет", INK), (E_part, "виден только конец A$'$", RED)):
        eye(ax, e[0], e[1], ang=-10, s=0.3)
        if e is E_full:
            # label beside the zone with a leader to the eye, clear of the zone sides
            ax.annotate(text, e + P(-0.3, 0), (-2.4, 2.3), ha="right", va="center", fontsize=10.5, color=col, zorder=12,
                        arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8, shrinkA=2, shrinkB=0))
        else:
            label(ax, e + P(0.0, 0.5), text, 10.5, color=col)
        for im in (A1, B1):
            h = intersect(e, im - e, a, b - a)
            inside = 0 <= np.dot(h - a, unit(b - a)) <= np.hypot(*(b - a))
            dashed(ax, e, im if inside else h, color=GREY if inside else RED, lw=1.0, alpha=0.8)
            if not inside:
                ax.plot([h[0]], [h[1]], marker="x", color=RED, ms=7, mew=2.0, zorder=9)
    label(ax, (3.6, 3.7), "область видимости\nвсего предмета", 11, color=ZONE_TEXT, weight="bold")
    save14(f, "mirror-visibility-extended")


@fig
def mirror_tv_room():
    f, ax = blank(10.4, 7.6, (-6.0, 6.6), (-0.6, 5.2))
    ax.add_patch(Polygon([(0, 0), (6, 0), (6, 4.6), (0, 4.6)], closed=True, fc=tint(INK, 0.95), ec="none", zorder=0))
    a, b = P(0, 1.2), P(0, 2.9)
    TA, TB = P(3.0, 0.0), P(4.6, 0.0)
    T1A, T1B = reflect_point(TA, a, b), reflect_point(TB, a, b)
    draw_zone(ax, (0.0, 6), (0, 4.6), [T1A, T1B], a, b, inside=lambda x, y: 0 < x < 6 and 0 < y < 4.6, n=320)
    for im in (T1A, T1B):
        for edge in (a, b):
            d = edge - im
            dashed(ax, edge, im + d * min((6 - im[0]) / d[0], 6.0), color=GREY, lw=1.1)
            dashed(ax, im, edge, color=VIRT, lw=1.0, alpha=0.7)
    ax.plot([0, 6, 6, 0, 0], [0, 0, 4.6, 4.6, 0], color=INK, lw=2.0, zorder=3)
    mirror_line(ax, a, b, side=+1, lw=4.2, tick=0.26)
    ax.plot([TA[0], TB[0]], [0.0, 0.0], color=INK, lw=6.0, solid_capstyle="butt", zorder=6)
    ax.plot([T1A[0], T1B[0]], [0.0, 0.0], color=VIRT, lw=6.0, solid_capstyle="butt", zorder=6, ls=(0, (2, 1.5)))
    label(ax, (3.8, -0.4), "телевизор  A—B", 10.5)
    label(ax, (-3.8, -0.4), "изображение телевизора", 10.5, color=VIRT)
    label(ax, TA, "A", 12, dy=0.3, dx=-0.2, weight="bold")
    label(ax, TB, "B", 12, dy=0.3, dx=0.2, weight="bold")
    label(ax, T1A, "A$'$", 12, dy=0.3, dx=0.2, weight="bold", color=VIRT)
    label(ax, T1B, "B$'$", 12, dy=0.3, dx=-0.2, weight="bold", color=VIRT)
    label(ax, (-0.6, 2.05), "зеркало", 10.5, rotation=90)
    E = P(3.4, 2.6)
    assert sees(E, [T1A, T1B], a, b)
    eye(ax, E[0], E[1], ang=-20, s=0.26)
    label(ax, E + P(0.1, -0.5), "весь экран виден", 10)
    label(ax, (4.6, 4.05), "область\nвидимости", 11.0, color=ZONE_TEXT, weight="bold")
    save14(f, "mirror-tv-room")


@fig
def mirror_sunspot_window():
    f, axs = blank_multi(2, 1, 11.6, 8.4, (-2.4, 12.4), (-2.3, 2.5))
    D = 1.0
    th = np.deg2rad(3.0)  # the angular radius of the Sun is about 0.27 degrees, enlarged here for the picture
    for ax, L, title in ((axs[0], 2.0, "экран близко: пятно повторяет форму зеркала"), (axs[1], 11.5, "экран далеко: пятно круглое, как диск Солнца")):
        ax.plot([0, 0], [-1.9, -D / 2], color=INK, lw=3.0, zorder=6)
        ax.plot([0, 0], [D / 2, 1.9], color=INK, lw=3.0, zorder=6)
        ax.plot([0, 0], [-D / 2, D / 2], color=VIRT, lw=5.0, zorder=7, solid_capstyle="butt")
        ax.plot([L, L], [-2.0, 2.0], color=INK, lw=2.4, zorder=6)
        for ang, col in ((0.0, INC), (th, tint(INC, 0.5)), (-th, tint(INC, 0.5))):
            for edge in (D / 2, -D / 2):
                ray(ax, P(-2.2, edge + 2.2 * np.tan(ang)), P(L, edge - L * np.tan(ang)), marks=(0.3,), lw=1.2, color=col, alpha=0.9)
        lo, hi = -D / 2 - L * np.tan(th), D / 2 + L * np.tan(th)
        core = D / 2 - L * np.tan(th)
        ax.plot([L, L], [lo, hi], color=RED, lw=7.0, solid_capstyle="butt", alpha=0.45, zorder=8)
        if core > 0:
            ax.plot([L, L], [-core, core], color=RED, lw=7.0, solid_capstyle="butt", zorder=9)
        label(ax, (L + 0.35, 0), "пятно", 10.5, color=RED, ha="left")
        label(ax, (-0.3, 1.85), "окно в зазеркалье", 10.5, bg=True)
        label(ax, (-2.3, 2.25), title, 11.5, weight="bold", ha="left")
    label(axs[0], (6.5, -1.9), "лучи от краёв диска Солнца идут под углом около $0{,}5^\\circ$, на рисунке он увеличен", 9, color=GREY, ha="left")
    save14(f, "mirror-sunspot-window")


@fig
def mirror_full_height():
    f, ax = blank(9.0, 6.6, (-1.5, 6.5), (-0.7, 2.6))
    H, h = 1.8, 1.65
    xm = 2.0
    A, B, O = P(0, H), P(0, 0), P(0, h)
    A1, B1, O1 = P(2 * xm, H), P(2 * xm, 0), P(2 * xm, h)
    C = intersect(O, A1 - O, P(xm, 0), P(0, 1))
    D = intersect(O, B1 - O, P(xm, 0), P(0, 1))
    assert abs(C[1] - (H + h) / 2) < 1e-9 and abs(D[1] - h / 2) < 1e-9
    assert abs((C[1] - D[1]) - H / 2) < 1e-9  # the mirror is half as tall as the person
    ax.plot([-1.3, 6.2], [0, 0], color=INK, lw=2.0, zorder=3)
    wall_line(ax, P(xm, 0), P(xm, 2.5), side=-1, lw=2.0, tick=0.15, step=0.25)
    ax.plot([xm, xm], [D[1], C[1]], color=INK, lw=6.0, zorder=6, solid_capstyle="butt")
    ax.plot([xm - 0.06, xm - 0.06], [D[1], C[1]], color=VIRT, lw=2.0, zorder=7, solid_capstyle="butt")
    ax.plot([0, 0], [0, H], color=INK, lw=3.0, zorder=6)
    ax.plot([2 * xm, 2 * xm], [0, H], color=VIRT, lw=3.0, zorder=6, ls=(0, (3, 2)))
    for x, col in ((0, INK), (2 * xm, VIRT)):
        ax.add_patch(Circle((x, H + 0.13), 0.13, fc=PAPER, ec=col, lw=1.6, zorder=6))
    eye(ax, O[0] + 0.14, O[1], s=0.12)
    ray(ax, A, C, marks=(0.5,), lw=1.6)
    ray(ax, C, O, marks=(0.55,), color=REF, lw=1.6)
    ray(ax, B, D, marks=(0.5,), lw=1.6)
    ray(ax, D, O, marks=(0.55,), color=REF, lw=1.6)
    dashed(ax, C, A1, color=VIRT, lw=1.3)
    dashed(ax, D, B1, color=VIRT, lw=1.3)
    dashed(ax, O, O1, color=GREY, lw=0.9)
    label(ax, A, "A", 12, dx=-0.3, dy=0.12, weight="bold")
    label(ax, B, "B", 12, dx=-0.3, weight="bold")
    label(ax, O, "O", 12, dx=-0.3, dy=-0.12, weight="bold")
    label(ax, A1, "A$'$", 12, dx=0.35, weight="bold", color=VIRT)
    label(ax, B1, "B$'$", 12, dx=0.35, weight="bold", color=VIRT)
    label(ax, C, "C", 12, dx=0.3, dy=0.12, weight="bold")
    label(ax, D, "D", 12, dx=0.3, dy=-0.12, weight="bold")
    dim(ax, P(-0.75, 0), P(-0.75, H), "$H$", off=(-0.2, 0))
    dim(ax, P(3.0, D[1]), P(3.0, C[1]), "$L$", off=(0.2, 0), color=RED)
    dim(ax, P(2.55, 0), P(2.55, D[1]), "$l$", off=(0.2, 0), color=RED)
    label(ax, (xm, 2.65), "стена, зеркало", 10.5)
    label(ax, (3.5, -0.4), "$L=\\dfrac{H}{2},\\quad l=\\dfrac{h}{2}$", 12.5, weight="bold")
    save14(f, "mirror-full-height")


@fig
def mirror_task_find_mirror():
    f, ax = blank(8.4, 6.0, (-0.8, 6.4), (-0.4, 5.4))
    A, A1 = P(1.4, 4.2), P(4.6, 1.0)
    mid = (A + A1) / 2
    d = A1 - A
    L = np.hypot(*d)
    rho = 0.72 * L
    nrm = unit(P(-d[1], d[0]))
    p_, q_ = mid + nrm * np.sqrt(rho**2 - (L / 2) ** 2), mid - nrm * np.sqrt(rho**2 - (L / 2) ** 2)
    assert abs(np.hypot(*(p_ - A)) - rho) < 1e-9 and abs(np.hypot(*(p_ - A1)) - rho) < 1e-9
    dashed(ax, A, A1, color=GREY, lw=1.3)
    for c in (A, A1):
        for pt_ in (p_, q_):
            compass_arc(ax, c, rho, pt_)
    for pt_ in (p_, q_):
        dot(ax, pt_, GREY, 4)
    mdir = unit(q_ - p_)
    mirror_line(ax, mid - mdir * 3.6, mid + mdir * 3.0, side=1 if np.dot(np.array([-mdir[1], mdir[0]]), A1 - A) > 0 else -1, lw=3.4)
    dot(ax, mid, INK, 5)
    right_angle(ax, mid, mdir, A1 - A, s=0.25)
    star(ax, *A, size=15)
    image_dot(ax, A1, 9)
    label(ax, A, "A", 13, dx=-0.3, dy=0.25, weight="bold")
    label(ax, A1, "A$_1$", 13, dx=0.45, weight="bold", color=VIRT)
    tick(ax, A, mid)
    tick(ax, mid, A1)
    label(ax, (2.6, 0.2), "зеркало — серединный перпендикуляр к $AA_1$", 10.5)
    save14(f, "mirror-task-find-mirror")


@fig
def mirror_task_b_point():
    f, axs = blank_multi(1, 2, 12.6, 5.0, (-0.3, 4.3), (-0.3, 4.0))
    cases = [
        (P(1.53, 0.41), P(0.39, 2.8), P(3.3, 1.02), True, "а) изображение точки B строится", INK),
        (P(1.3, 3.13), P(0.99, 1.25), P(3.45, 0.56), False, "б) точка B за зеркалом: изображения нет", RED),
    ]
    for ax, (A, A1, B, solvable, title, col) in zip(axs, cases):
        box = Rectangle((-0.2, -0.2), 4.4, 4.2, fc="none", ec=INK, lw=1.6, zorder=1)
        ax.add_patch(box)
        mid = (A + A1) / 2
        n_ = unit(A1 - A)
        mdir = P(-n_[1], n_[0])
        assert (np.dot(A - mid, n_) * np.dot(B - mid, n_) > 0) == solvable  # B lies on the same side of the mirror as A, or not
        p1, p2 = mid - mdir * 4.0, mid + mdir * 4.0
        line, = ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INK, lw=2.2, zorder=3, ls=DASH)
        line.set_clip_path(box)
        star(ax, *A, size=13)
        image_dot(ax, A1, 8)
        dot(ax, B, INK, 7)
        label(ax, A, "A", 12, dy=-0.3, weight="bold")
        label(ax, A1, "A$_1$", 12, dy=0.3, weight="bold", color=VIRT)
        label(ax, B, "B", 12, dx=0.25, dy=0.22, weight="bold")
        dashed(ax, A, A1, color=GREY, lw=1.0)
        if solvable:
            B1 = reflect_point(B, mid - mdir, mid + mdir)
            image_dot(ax, B1, 8)
            label(ax, B1, "B$_1$", 12, dy=0.3, weight="bold", color=VIRT)
            dashed(ax, B, B1, color=GREY, lw=1.1)
            tick(ax, B, (B + B1) / 2, n=2)
            tick(ax, (B + B1) / 2, B1, n=2)
        label(ax, (2.05, -0.55), title, 11, weight="bold", color=col)
    save14(f, "mirror-task-b-point")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
