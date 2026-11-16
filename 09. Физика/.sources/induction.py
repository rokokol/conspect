"""Figures for the note "Электромагнитная индукция" (section f12, lessons 181-182).

Run: python3 induction.py [name ...]   (matplotlib only)
PNG files go to content/12. Магнитные явления/00. Вложения/ (prefix induction-)
Geometry of the ring and coil pictures: the axis of the ring runs along x, the viewer looks from the side.
A wire cross-section with a dot carries current towards the viewer, with a cross away from the viewer.
By the right-hand rule the field inside a ring points to the left when its top wire has a cross and its bottom wire a dot.
"""
import sys

from magnet_common import *  # noqa: F403
from matplotlib.patches import Ellipse

FIGS = {}
# Field of the magnet or of the primary circuit. It is neither blue nor red (the colours of the poles) nor green (the induced field).
PRIM = VIOLET
IND = GREEN  # field and current of the induced current


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


def bar_magnet(ax, x0, y, w=2.2, h=0.6, left="N", zorder=2):
    """Bar magnet whose left end is the pole `left`."""
    right = "S" if left == "N" else "N"
    col = {"N": NORTH, "S": SOUTH}
    rect(ax, x0, y - h / 2, w / 2, h, fc=col[left], ec=INK, lw=1.4, zorder=zorder)
    rect(ax, x0 + w / 2, y - h / 2, w / 2, h, fc=col[right], ec=INK, lw=1.4, zorder=zorder)
    txt(ax, x0 + w / 4, y, left, 13, color=PAPER, weight="bold", zorder=zorder + 1)
    txt(ax, x0 + 3 * w / 4, y, right, 13, color=PAPER, weight="bold", zorder=zorder + 1)


def galv(ax, x, y, deflect=0.0, r=0.45):
    """Galvanometer with a zero at the top; `deflect` is the needle angle in degrees, to the right when positive."""
    import math

    circ(ax, x, y, r, ec=INK, lw=1.6, zorder=4)
    ax.plot([x, x], [y + r * 0.82, y + r * 0.62], color=GREY, lw=1.2, zorder=5)
    a = math.radians(deflect)
    ax.plot([x, x + r * 0.8 * math.sin(a)], [y - r * 0.15, y - r * 0.15 + r * 0.8 * math.cos(a)], color=RED, lw=2.0, zorder=6)
    ax.plot([x], [y - r * 0.15], "o", color=INK, ms=3, zorder=7)


def ring_side(ax, x, y, R=0.9, top="cross", lw=1.8):
    """Wire ring seen edge-on: two cross-sections, top and bottom, and the thin outline of the ring."""
    ax.add_patch(Ellipse((x, y), 0.34, 2 * R, fc="none", ec=INK, lw=lw, zorder=3))
    for sign, kind in ((1, top), (-1, "dot" if top == "cross" else "cross")):
        (cross_in if kind == "cross" else dot_out)(ax, x, y + sign * R, r=0.19, color=INK, lw=1.6)


def wire(ax, pts, color=INK, lw=1.6):
    line(ax, pts, color=color, lw=lw, zorder=2)


def switch_open(ax, x0, x1, y, color=INK):
    ax.plot([x0, x0 + (x1 - x0) * 0.25], [y, y], color=color, lw=1.6)
    ax.plot([x1 - (x1 - x0) * 0.25, x1], [y, y], color=color, lw=1.6)
    ax.plot([x0 + (x1 - x0) * 0.25, x1 - (x1 - x0) * 0.3], [y, y + 0.32], color=color, lw=1.6)
    ax.plot([x0 + (x1 - x0) * 0.25, x1 - (x1 - x0) * 0.25], [y, y], "o", color=color, ms=3.5)


def coil(ax, x0, x1, y, h=1.0, n=6, lw=1.8):
    """Coil seen from the side: a pale body and the slanted front halves of the turns."""
    step = (x1 - x0) / (n - 1)
    ax.add_patch(Rectangle((x0 - step * 0.35, y - h / 2), x1 - x0 + step * 0.7, h, fc=tint(INK, 0.93), ec=GREY, lw=0.9, zorder=1))
    for i in range(n):
        xi = x0 + i * step
        ax.plot([xi - step * 0.2, xi + step * 0.2], [y - h / 2, y + h / 2], color=INK, lw=lw, zorder=5)
    return x0 - step * 0.35, x1 + step * 0.35


# ------------------------------------------------------------------ Faraday experiments


@fig
def induction_faraday_ring():
    f, ax = blank(9.4, 5.0, (-5.2, 5.6), (-2.6, 2.6))
    ax.add_patch(Circle((0, 0), 1.5, fc=IRON, ec=INK, lw=1.6, zorder=1))
    ax.add_patch(Circle((0, 0), 0.9, fc=PAPER, ec=INK, lw=1.6, zorder=2))
    txt(ax, 0, 0, "железное\nкольцо", 10)
    for ang0, ang1 in ((155, 205), (-25, 25)):
        for a in np.linspace(ang0, ang1, 7):
            t = np.deg2rad(a)
            ax.plot([0.8 * np.cos(t), 1.6 * np.cos(t)], [0.8 * np.sin(t), 1.6 * np.sin(t)], color=COPPER, lw=2.2, zorder=3)
    # left coil to the galvanometer
    for s in (1, -1):
        p = (1.2 * np.cos(np.deg2rad(155 if s > 0 else 205)), 1.2 * np.sin(np.deg2rad(155 if s > 0 else 205)))
        wire(ax, [(p[0] - 0.25, p[1]), (-2.6, p[1]), (-2.6, s * 1.1), (-3.8, s * 1.1), (-3.8, s * 0.45)])
    galv(ax, -3.8, 0, deflect=30)
    txt(ax, -3.8, -1.9, "гальванометр", 10)
    # right coil to the source and the key
    p1 = (1.2 * np.cos(np.deg2rad(25)), 1.2 * np.sin(np.deg2rad(25)))
    p2 = (1.2 * np.cos(np.deg2rad(-25)), 1.2 * np.sin(np.deg2rad(-25)))
    wire(ax, [(p1[0] + 0.25, p1[1]), (2.4, p1[1]), (2.4, 1.6), (3.0, 1.6)])
    switch_open(ax, 3.0, 4.1, 1.6)
    wire(ax, [(4.1, 1.6), (4.9, 1.6), (4.9, -1.6), (4.1, -1.6)])
    battery(ax, 3.6, -1.6, horizontal=True, size=0.5, label=True, flip=True)
    wire(ax, [(3.1, -1.6), (2.4, -1.6), (2.4, p2[1]), (p2[0] + 0.25, p2[1])])
    txt(ax, 3.55, 2.3, "ключ", 10)
    txt(ax, 3.55, -2.35, "источник тока", 10)
    txt(ax, 0, -2.3, "две катушки, изолированные друг от друга", 10, color=GREY)
    save(f, "induction-faraday-ring")


@fig
def induction_magnet_coil():
    f, axs = blank_multi(2, 2, 11.0, 7.6, (-5.0, 2.6), (-3.2, 1.7))
    cases = [
        ("N", "in", +1, "вдвигаем северным полюсом"),
        ("N", "out", -1, "вынимаем"),
        ("S", "in", -1, "вдвигаем южным полюсом"),
        ("S", "out", +1, "вынимаем"),
    ]
    for ax, (pole, motion, sgn, title) in zip(axs, cases):
        # the pole facing the coil is the right end of the magnet
        left = "S" if pole == "N" else "N"
        x0 = -4.7 if motion == "in" else -2.4
        bar_magnet(ax, x0, 0, w=2.2, h=0.5, left=left, zorder=2)
        xl, xr = coil(ax, -1.2, 1.4, 0, h=1.0, n=6)
        for xs, sg in ((xl, -1), (xr, 1)):
            wire(ax, [(xs, -0.5), (xs, -2.3), (sg * 0.45, -2.3)])
        galv(ax, 0, -2.3, deflect=sgn * 40)
        if motion == "in":
            arrow(ax, (x0 + 0.4, 0.75), (x0 + 1.9, 0.75), color=ORANGE, lw=2.2)
        else:
            arrow(ax, (x0 + 1.9, 0.75), (x0 + 0.4, 0.75), color=ORANGE, lw=2.2)
        txt(ax, x0 + 1.15, 1.1, "движение", 10, color=ORANGE)
        txt(ax, -1.2, 1.5, title, 11.5, ha="left", weight="bold")
        txt(ax, 1.9, -2.3, "стрелка\nвправо" if sgn > 0 else "стрелка\nвлево", 10, ha="left", color=RED)
    save(f, "induction-magnet-coil")


@fig
def induction_electromagnet_variants():
    f, axs = blank_multi(2, 1, 11.0, 8.8, (-4.6, 5.4), (-3.3, 2.1))

    def big_coil_with_galvanometer(ax):
        xl, xr = coil(ax, 1.2, 3.6, 0, h=1.5, n=6)
        wire(ax, [(xl, -0.75), (xl, -2.1), (2.4 - 0.45, -2.1)])
        wire(ax, [(xr, -0.75), (xr, -2.1), (2.4 + 0.45, -2.1)])
        galv(ax, 2.4, -2.1, deflect=30)

    # variant 2: a small coil with current moves into the big coil
    ax = axs[0]
    big_coil_with_galvanometer(ax)
    xl, xr = coil(ax, -3.4, -1.8, 0, h=0.9, n=4)
    wire(ax, [(xl, -0.45), (xl, -2.1), (-3.0, -2.1)])
    wire(ax, [(xr, -0.45), (xr, -2.1), (-2.1, -2.1)])
    battery(ax, -2.55, -2.1, horizontal=True, size=0.5, label=False)
    # + of the battery is at the left end: the current rises along the visible turns, so by the right-hand rule N is at the left end
    txt(ax, xl - 0.3, 0, "N", 13, color=NORTH, weight="bold")
    txt(ax, xr + 0.3, 0, "S", 13, color=SOUTH, weight="bold")
    arrow(ax, (-3.2, 0.95), (-1.9, 0.95), color=ORANGE, lw=2.2)
    txt(ax, -2.55, 1.3, "движение", 10, color=ORANGE)
    txt(ax, -4.5, 1.85, "второй опыт: катушка с током вместо магнита", 11, ha="left", weight="bold")
    # variant 3: coils at rest, current changes
    ax = axs[1]
    big_coil_with_galvanometer(ax)
    xl, xr = coil(ax, -3.4, -1.8, 0, h=0.9, n=4)
    wire(ax, [(xl, -0.45), (xl, -2.1), (-3.6, -2.1)])
    rect(ax, -3.6, -2.28, 0.9, 0.36, fc=PAPER, ec=INK, lw=1.6, zorder=3)
    # The circuit goes through the left end of the rheostat, the part of it up to the slider and the slider itself;
    # the right end is free, so a move of the slider to the left shortens the working part
    wire(ax, [(-3.15, -1.55), (-3.15, -1.3), (-2.61, -1.3), (-2.61, -2.1)])
    # the right lead of the battery ends exactly at the corner of the wire (xr)
    battery(ax, xr - 0.5, -2.1, horizontal=True, size=0.5, label=False, flip=True)
    wire(ax, [(xr, -2.1), (xr, -0.45)])
    arrow(ax, (-3.15, -1.55), (-3.15, -1.93), color=INK, lw=1.6, scale=10)
    arrow(ax, (-2.75, -2.75), (-3.55, -2.75), color=ORANGE, lw=2.0)
    txt(ax, -3.15, -3.05, "перемещение ползунка", 10, color=ORANGE)
    txt(ax, -1.0, 1.0, "катушки неподвижны", 10, color=GREY)
    txt(ax, -4.5, 1.85, "третий опыт: катушки неподвижны, ток меняется реостатом", 11, ha="left", weight="bold")
    save(f, "induction-electromagnet-variants")


@fig
def induction_rotating_coil():
    f, axs = blank_multi(1, 3, 12.0, 4.0, (-3.2, 3.2), (-2.4, 2.4))
    for ax, (ang, title, n) in zip(axs, [(90, "виток поперёк поля", "5 линий"), (45, "виток под углом", "3 линии"), (0, "виток вдоль поля", "0 линий")]):
        rect(ax, -3.1, -0.9, 0.7, 1.8, fc=NORTH)
        rect(ax, 2.4, -0.9, 0.7, 1.8, fc=SOUTH)
        txt(ax, -2.75, 0, "N", 13, color=PAPER, weight="bold")
        txt(ax, 2.75, 0, "S", 13, color=PAPER, weight="bold")
        for y in (-0.7, -0.35, 0, 0.35, 0.7):
            arrow(ax, (-2.35, y), (2.35, y), color=PRIM, lw=1.2, scale=10, alpha=0.75)
        a = np.deg2rad(ang)
        dx, dy = 0.85 * np.cos(a), 0.85 * np.sin(a)
        ax.plot([-dx, dx], [-dy, dy], color=INK, lw=4.0, solid_capstyle="round", zorder=5)
        txt(ax, 0, 1.75, title, 11.5, weight="bold")
        txt(ax, 0, -1.7, "пронизывает " + n, 11, color=PRIM)
    save(f, "induction-rotating-coil")


# ------------------------------------------------------------------ Lenz rule


@fig
def induction_lenz_magnet_coil():
    f, ax = blank(11.0, 5.0, (-5.2, 7.0), (-3.4, 2.4))
    bar_magnet(ax, -5.0, 0.0, w=2.4, h=0.6, left="S")
    arrow(ax, (-4.4, 0.75), (-2.8, 0.75), color=ORANGE, lw=2.2)
    txt(ax, -3.6, 1.12, "движение", 10, color=ORANGE)
    # the front half of each turn carries current upwards: the induced field points left and the left end of the coil is N
    x0, x1 = -1.4, 2.6
    n = 5
    step = (x1 - x0) / (n - 1)
    xl, xr = coil(ax, x0, x1, 0, h=1.6, n=n)
    for i in range(n):
        xi = x0 + i * step
        arrow(ax, (xi - step * 0.03, -0.12), (xi + step * 0.03, 0.12), color=IND, lw=1.5, scale=11, zorder=6)
    txt(ax, xl - 0.3, 0, "N", 13, color=NORTH, weight="bold", ha="right")
    txt(ax, xr + 0.3, 0, "S", 13, color=SOUTH, weight="bold", ha="left")
    # circuit: the current flows through the coil to the right, out of the top of the last turn, and back through the lamp
    ex, ey = x1 + step * 0.2, 0.8
    sx, sy = x0 - step * 0.2, -0.8
    wire(ax, [(ex, ey), (ex, 1.6), (xr + 1.0, 1.6), (xr + 1.0, -2.6), (0.7, -2.6)])
    wire(ax, [(-0.0, -2.6), (-2.2, -2.6), (-2.2, sy), (sx, sy)])
    lamp(ax, 0.35, -2.6, r=0.35)
    arrow(ax, (xr + 1.0, 0.4), (xr + 1.0, -0.4), color=IND, lw=1.8, scale=12)
    arrow(ax, (1.6, -2.6), (1.3, -2.6), color=IND, lw=1.8, scale=12)
    arrow(ax, (-2.2, -1.8), (-2.2, -1.4), color=IND, lw=1.8, scale=12)
    # fields
    arrow(ax, (x0 + 0.2, 0.35), (x1 - 0.2, 0.35), color=PRIM, lw=2.0, scale=14)
    arrow(ax, (x1 - 0.2, -0.35), (x0 + 0.2, -0.35), color=IND, lw=2.0, scale=14)
    txt(ax, 4.5, 0.75, "поле магнита\nрастёт", 10.5, color=PRIM, ha="left")
    txt(ax, 4.5, -0.75, "поле индукционного\nтока", 10.5, color=IND, ha="left")
    txt(ax, 0.3, -3.2, "лампа горит: по катушке течёт индукционный ток", 10.5)
    save(f, "induction-lenz-magnet-coil")


def _case_panel(ax, pole, motion):
    """Ring seen edge-on, a bar magnet on the left. `pole` is the pole facing the ring."""
    left = "S" if pole == "N" else "N"
    b_prim = +1 if pole == "N" else -1  # field of the magnet in the ring: to the right when the pole is N
    grows = motion == "in"
    b_ind = -b_prim if grows else +b_prim
    top = "cross" if b_ind < 0 else "dot"
    bar_magnet(ax, -5.0, 0, w=2.2, h=0.55, left=left)
    ring_side(ax, 0, 0, R=0.95, top=top)
    if grows:
        arrow(ax, (-4.2, 0.65), (-2.9, 0.65), color=ORANGE, lw=2.2)
    else:
        arrow(ax, (-2.9, 0.65), (-4.2, 0.65), color=ORANGE, lw=2.2)
    txt(ax, -3.55, 1.0, "движение", 10, color=ORANGE)
    # fields: short arrows on the right of the ring
    arrow(ax, (0.55 if b_prim > 0 else 1.75, 0.4), (1.75 if b_prim > 0 else 0.55, 0.4), color=PRIM, lw=2.0, scale=13)
    arrow(ax, (0.55 if b_ind > 0 else 1.75, -0.4), (1.75 if b_ind > 0 else 0.55, -0.4), color=IND, lw=2.0, scale=13)
    face_left = "N" if b_ind < 0 else "S"
    face_right = "S" if b_ind < 0 else "N"
    txt(ax, -0.62, 0, face_left, 12, color=NORTH if face_left == "N" else SOUTH, weight="bold")
    txt(ax, 0.62, 0, face_right, 12, color=NORTH if face_right == "N" else SOUTH, weight="bold")
    same = face_left == pole
    return same, b_prim, b_ind, grows


@fig
def induction_lenz_four_cases():
    f, axs = blank_multi(2, 2, 11.6, 6.0, (-5.3, 3.4), (-2.3, 2.1))
    cases = [("N", "in", "северный полюс приближается"), ("N", "out", "северный полюс удаляется"), ("S", "in", "южный полюс приближается"), ("S", "out", "южный полюс удаляется")]
    for ax, (pole, motion, title) in zip(axs, cases):
        same, bp, bi, grows = _case_panel(ax, pole, motion)
        txt(ax, -5.2, 1.85, title, 11.5, ha="left", weight="bold")
        s_prim = "поле магнита {} , {}".format("→" if bp > 0 else "←", "растёт" if grows else "убывает")
        s_ind = "поле тока {} : {}".format("→" if bi > 0 else "←", "мешает росту" if grows else "не даёт убывать")
        txt(ax, -5.2, -1.45, s_prim, 10.5, ha="left", color=PRIM)
        txt(ax, -5.2, -1.85, s_ind, 10.5, ha="left", color=IND)
        txt(ax, 1.75, 1.35, "отталкивание" if same else "притяжение", 11, color=RED if same else GREEN, weight="bold")
    save(f, "induction-lenz-four-cases")


@fig
def induction_ring_repelled():
    f, axs = blank_multi(1, 2, 12.4, 4.8, (-5.6, 4.6), (-3.0, 2.8))
    for ax, motion in zip(axs, ("in", "out")):
        # stand and hanging ring
        rect(ax, -0.9, -2.7, 1.8, 0.2, fc=IRON)
        ax.plot([0, 0], [-2.5, 1.9], color=INK, lw=3)
        ax.plot([0, 1.6], [1.9, 1.9], color=INK, lw=3)
        ax.plot([1.6, 1.6], [1.9, 0.9], color=GREY, lw=1.2)
        ax.add_patch(Ellipse((1.6, 0.0), 0.3, 1.8, fc="none", ec=COPPER, lw=3.2, zorder=3))
        txt(ax, 1.6, -1.35, "медное кольцо", 10, color=COPPER)
        bar_magnet(ax, -4.6, 0.0, w=2.2, h=0.55, left="S")
        if motion == "in":
            arrow(ax, (-4.0, 0.6), (-2.7, 0.6), color=ORANGE, lw=2.2)
            arrow(ax, (2.0, 0.0), (3.1, 0.0), color=RED, lw=2.6)
            txt(ax, -3.35, 0.95, "магнит приближается", 10.5, color=ORANGE)
            txt(ax, 2.0, 0.45, "кольцо убегает", 10.5, color=RED, ha="left")
        else:
            arrow(ax, (-2.7, 0.6), (-4.0, 0.6), color=ORANGE, lw=2.2)
            arrow(ax, (3.1, 0.0), (2.0, 0.0), color=GREEN, lw=2.6)
            txt(ax, -3.35, 0.95, "магнит удаляется", 10.5, color=ORANGE)
            txt(ax, 2.0, 0.45, "кольцо тянется", 10.5, color=GREEN, ha="left")
    txt(axs[0], -5.4, 2.5, "приближаем: отталкивание", 11.5, ha="left", weight="bold")
    txt(axs[1], -5.4, 2.5, "удаляем: притяжение", 11.5, ha="left", weight="bold")
    save(f, "induction-ring-repelled")


@fig
def induction_lenz_energy():
    f, axs = blank_multi(1, 2, 13.0, 4.8, (-5.8, 4.6), (-3.2, 2.4))
    for k, ax in enumerate(axs):
        ok = k == 0
        bar_magnet(ax, -5.4, 0, w=2.2, h=0.55, left="S")
        arrow(ax, (-4.7, 0.65), (-3.4, 0.65), color=ORANGE, lw=2.2)
        x0, x1 = -1.6, 2.2
        coil(ax, x0 + 0.3, x1 - 0.3, 0, h=1.4, n=5)
        txt(ax, x0 - 0.15, 0, "N" if ok else "S", 13, color=NORTH if ok else SOUTH, weight="bold", ha="right")
        txt(ax, x1 + 0.15, 0, "S" if ok else "N", 13, color=SOUTH if ok else NORTH, weight="bold", ha="left")
        lamp(ax, 0.3, -1.6, r=0.3)
        wire(ax, [(0.0, -1.6), (x0, -1.6), (x0, -0.7)])
        wire(ax, [(0.6, -1.6), (x1, -1.6), (x1, -0.7)])
        if ok:
            arrow(ax, (-3.4, -0.6), (-4.5, -0.6), color=RED, lw=3.0)
            txt(ax, -3.95, -0.95, "N и N отталкиваются", 10.5, color=RED)
            txt(ax, -0.6, 1.9, "правило Ленца работает так", 11.5, weight="bold")
            txt(ax, -0.6, -2.5, "магнит вдвигают, совершая работу,\nона идёт на свечение лампы", 10.5)
        else:
            arrow(ax, (-4.5, -0.6), (-3.4, -0.6), color=GREEN, lw=3.0)
            txt(ax, -3.95, -0.95, "N и S притягиваются", 10.5, color=GREEN)
            txt(ax, -0.6, 1.9, "если бы правило работало наоборот", 11.5, weight="bold")
            txt(ax, -0.6, -2.5, "магнит разгоняется сам и ещё зажигает лампу:\nэнергия из ничего, противоречие закону сохранения", 10.5, color=RED)
    save(f, "induction-lenz-energy")


# ------------------------------------------------------------------ eddy currents


@fig
def induction_eddy_plate():
    f, axs = blank_multi(1, 2, 11.2, 5.0, (-2.8, 2.8), (-2.9, 2.7))
    # (a) plate as nested rings
    ax = axs[0]
    rect(ax, -2.2, -2.2, 4.4, 4.4, fc=LIGHT, ec=INK, lw=1.6)
    for r in (0.35, 0.75, 1.15, 1.55, 1.95):
        ax.add_patch(Circle((0, 0), r, fc="none", ec=COPPER, lw=2.0))
    txt(ax, 0, 2.5, "пластина как набор вложенных колец", 11.5, weight="bold")
    txt(ax, 0, -2.6, "в каждом кольце возникает свой индукционный ток", 10.5)
    # (b) eddy currents
    ax = axs[1]
    rect(ax, -2.2, -2.2, 4.4, 4.4, fc=LIGHT, ec=INK, lw=1.6)
    for r in (0.35, 0.75, 1.15, 1.55, 1.95):
        t = np.linspace(0, 2 * np.pi, 200)
        ax.plot(r * np.cos(t), r * np.sin(t), color=IND, lw=2.0)
        for a0 in (0.9, 0.9 + np.pi / 2, 0.9 + np.pi, 0.9 + 3 * np.pi / 2):
            arrow(ax, (r * np.cos(a0), r * np.sin(a0)), (r * np.cos(a0 + 0.15), r * np.sin(a0 + 0.15)), color=IND, lw=2.0, scale=13)
    dot_out(ax, 0, 0, r=0.16, color=IND)
    txt(ax, 0, 2.5, "вихревые токи (токи Фуко)", 11.5, weight="bold")
    txt(ax, 0, -2.6, "к пластине приближают северный полюс,\nвид со стороны магнита", 10.5)
    save(f, "induction-eddy-plate")


@fig
def induction_plate_force():
    f, axs = blank_multi(1, 2, 12.6, 4.4, (-5.6, 4.0), (-2.3, 2.3))
    for ax, motion in zip(axs, ("in", "out")):
        rect(ax, 0.8, -1.7, 0.5, 3.4, fc=IRON, ec=INK, lw=1.6)
        txt(ax, 1.05, -2.05, "алюминиевая пластина", 10, ha="center")
        bar_magnet(ax, -4.6, 0.0, w=2.2, h=0.6, left="S")
        if motion == "in":
            arrow(ax, (-4.0, 0.7), (-2.7, 0.7), color=ORANGE, lw=2.2)
            arrow(ax, (1.5, 0), (2.6, 0), color=RED, lw=2.6)
            txt(ax, -3.3, 1.05, "движение", 10.5, color=ORANGE)
            txt(ax, 1.5, 0.4, "пластину отталкивает", 10.5, color=RED, ha="left")
            txt(ax, -5.4, 1.95, "магнит приближают", 11.5, ha="left", weight="bold")
        else:
            arrow(ax, (-2.7, 0.7), (-4.0, 0.7), color=ORANGE, lw=2.2)
            arrow(ax, (2.6, 0), (1.5, 0), color=GREEN, lw=2.6)
            txt(ax, -3.3, 1.05, "движение", 10.5, color=ORANGE)
            txt(ax, 1.5, 0.4, "пластину тянет за собой", 10.5, color=GREEN, ha="left")
            txt(ax, -5.4, 1.95, "магнит удаляют", 11.5, ha="left", weight="bold")
    save(f, "induction-plate-force")


@fig
def induction_pendulum_plate():
    f = plt.figure(figsize=(11.8, 4.6))
    gs = f.add_gridspec(1, 2, width_ratios=[1.0, 1.15])
    ax = f.add_subplot(gs[0])
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-3.2, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-0.8, 0.8], [2.2, 2.2], color=INK, lw=4)
    theta = np.deg2rad(28)
    bx, by = 2.7 * np.sin(theta) * -1, 2.2 - 2.7 * np.cos(theta)
    ax.plot([0, bx], [2.2, by], color=GREY, lw=1.3)
    ax.plot([0, 0], [2.2, -0.3], color=GREY, lw=0.8, ls=":")
    rect(ax, bx - 0.28, by - 0.16, 0.28, 0.32, fc=NORTH, zorder=4)  # the left half stays the same pole as before: N
    rect(ax, bx, by - 0.16, 0.28, 0.32, fc=SOUTH, zorder=4)
    arrow(ax, (bx + 0.6, by - 0.15), (bx + 1.5, by - 0.55), color=ORANGE, lw=2.0, scale=12)
    rect(ax, -2.4, -1.55, 4.8, 0.35, fc=IRON, ec=INK, lw=1.6)
    txt(ax, 0, -2.0, "алюминиевая пластина", 10.5)
    txt(ax, 0, -2.8, "магнит не касается пластины,\nно она его тормозит", 10.5)
    ax2 = f.add_subplot(gs[1])
    t = np.linspace(0, 20, 800)
    w = 2 * np.pi / 2.0
    ax2.plot(t, np.exp(-0.05 * t) * np.cos(w * t), color=ORANGE, lw=1.6, label="над деревянным столом")
    ax2.plot(t, np.exp(-0.45 * t) * np.cos(w * t), color=BLUE, lw=1.8, label="над алюминиевым листом")
    ax2.axhline(0, color=GREY, lw=0.8)
    ax2.set_xlabel("время")
    ax2.set_ylabel("отклонение маятника")
    ax2.set_yticks([])
    ax2.set_xticks([])
    ax2.set_title("Затухание колебаний (схема)")
    ax2.legend(loc="upper right", frameon=False)
    save(f, "induction-pendulum-plate")


@fig
def induction_speedometer():
    f, ax = blank(8.4, 5.6, (-4.8, 4.4), (-3.6, 2.9))
    # aluminium disc on an axle, held by a spring, with a pointer
    ax.add_patch(Circle((0, 0), 1.5, fc=LIGHT, ec=INK, lw=1.8, zorder=2))
    txt(ax, 0, 0.55, "алюминиевая\nпластинка", 10, zorder=5)
    ax.plot([0], [0], "o", color=INK, ms=6, zorder=6)
    # spring from the axle to the fixed wall
    n = 14
    # The spring is fixed at the rim of the disc: a force through the axle would have no arm and could not hold the disc
    p0, p1 = 1.5 * np.array([np.cos(np.radians(-120)), np.sin(np.radians(-120))]), np.array([-1.9, -1.5])
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    nrm = np.array([-d[1], d[0]])
    pts = [p0 + (p1 - p0) * (i / (n - 1)) + nrm * (0.09 if i % 2 else -0.09) * (0 < i < n - 1) for i in range(n)]
    ax.plot(*zip(*pts), color=INK, lw=1.4, zorder=6)
    ax.plot([p1[0]], [p1[1]], "s", color=INK, ms=7, zorder=6)
    txt(ax, -2.2, -1.9, "пружина", 10.5, zorder=6)
    # horseshoe magnet rotating around the disc
    t = np.linspace(np.deg2rad(20), np.deg2rad(160), 80)
    R = 2.05
    ax.plot(R * np.cos(t), R * np.sin(t) + 0.0, color=IRON, lw=12, solid_capstyle="butt", zorder=3)
    for sgn, col, lab in ((1, NORTH, "N"), (-1, SOUTH, "S")):
        a0 = np.deg2rad(20) if sgn > 0 else np.deg2rad(160)
        ax.plot([R * np.cos(a0)], [R * np.sin(a0)], "s", color=col, ms=15, zorder=4)
    txt(ax, R * np.cos(np.deg2rad(160)) - 0.1, R * np.sin(np.deg2rad(160)) + 0.4, "S", 12, weight="bold")
    txt(ax, R * np.cos(np.deg2rad(20)) + 0.1, R * np.sin(np.deg2rad(20)) + 0.4, "N", 12, weight="bold")
    ax.add_patch(FancyArrowPatch((-2.4, 1.5), (-2.9, 0.3), connectionstyle="arc3,rad=0.4", arrowstyle="-|>", mutation_scale=14, lw=2.0, color=ORANGE))
    txt(ax, -3.4, 2.2, "магнит вращается\nвместе с колёсами", 10.5, color=ORANGE)  # above the rotation arrow
    # pointer and scale
    ax.plot([0, 2.5], [0, -1.6], color=RED, lw=2.4, zorder=7)
    sc = np.linspace(np.deg2rad(-75), np.deg2rad(-15), 40)
    ax.plot(2.9 * np.cos(sc), 2.9 * np.sin(sc), color=INK, lw=1.4)
    for a in np.linspace(np.deg2rad(-75), np.deg2rad(-15), 7):
        ax.plot([2.8 * np.cos(a), 3.0 * np.cos(a)], [2.8 * np.sin(a), 3.0 * np.sin(a)], color=INK, lw=1.2)
    txt(ax, 3.7, -1.5, "шкала,\nкм/ч", 10.5)
    txt(ax, -0.3, -3.3, "пластинка отстаёт от магнита, пружина её удерживает", 10.5)
    save(f, "induction-speedometer")


# ------------------------------------------------------------------ tasks


@fig
def induction_task_rheostat():
    f, ax = blank(7.4, 6.2, (-3.6, 3.9), (-3.4, 3.2))
    wire(ax, [(-3.0, 2.6), (3.0, 2.6)])
    wire(ax, [(-3.0, 2.6), (-3.0, -2.3), (-1.2, -2.3)])
    wire(ax, [(3.0, 2.6), (3.0, 0.75)])
    battery(ax, 3.0, 0.3, horizontal=False, size=0.45, label=True)
    wire(ax, [(3.0, -0.15), (3.0, -1.7), (0.9, -1.7)])
    rect(ax, -1.2, -2.5, 2.4, 0.4, fc=PAPER, ec=INK, lw=1.6, zorder=3)
    txt(ax, 0, -2.95, "реостат", 10)
    arrow(ax, (0.9, -1.7), (0.9, -2.07), color=INK, lw=1.6, scale=10)
    arrow(ax, (0.7, -1.4), (2.5, -1.4), color=ORANGE, lw=2.0)
    txt(ax, 1.9, -1.15, "движение ползунка", 10, color=ORANGE)
    # ring A with the field of the square circuit
    ax.add_patch(Circle((0, 0.2), 1.2, fc="none", ec=INK, lw=2.4, zorder=3))
    txt(ax, -0.85, -0.55, "A", 13, weight="bold")
    for x, y in ((-0.45, 0.85), (0.5, 0.95), (0.7, 0.05), (-0.55, 0.0), (0.0, 0.3), (0.05, -0.5)):
        dot_out(ax, x, y, r=0.1, color=PRIM, lw=1.2)
    t = np.linspace(np.deg2rad(30), np.deg2rad(150), 50)
    r = 1.48
    ax.plot(r * np.cos(t), 0.2 + r * np.sin(t), color=IND, lw=2.4)
    arrow(ax, (r * np.cos(t[-3]), 0.2 + r * np.sin(t[-3])), (r * np.cos(t[-1]), 0.2 + r * np.sin(t[-1])), color=IND, lw=2.4, scale=14)
    txt(ax, 0, 2.1, "индукционный ток: против часовой стрелки", 10, color=IND)
    arrow(ax, (-2.6, 1.9), (-2.6, 0.6), color=INK, lw=1.6, scale=10)
    txt(ax, -2.35, 1.3, "ток", 10, ha="left")
    txt(ax, -2.85, -0.4, "поле тока цепи:\nк нам", 10, color=PRIM, ha="left")  # right of the left wire (x = -3.0)
    save(f, "induction-task-rheostat")


@fig
def induction_task_magnet_ring():
    f, ax = blank(9.0, 4.4, (-5.6, 4.2), (-2.4, 2.4))
    bar_magnet(ax, -5.2, 0, w=2.4, h=0.6, left="N")
    ring_side(ax, 0.6, 0, R=0.95, top="cross")
    txt(ax, -0.02, 0, "N", 12, color=NORTH, weight="bold")
    txt(ax, 1.22, 0, "S", 12, color=SOUTH, weight="bold")
    arrow(ax, (0.9, -0.45), (0.0, -0.45), color=IND, lw=2.0, scale=13, alpha=0.0)
    arrow(ax, (1.9, -0.4), (1.1, -0.4), color=IND, lw=2.0, scale=13)
    txt(ax, 2.1, -0.4, "поле\nиндукционного тока", 10, color=IND, ha="left")
    arrow(ax, (-3.1, 0.75), (-4.5, 0.75), color=ORANGE, lw=2.6)
    txt(ax, -3.8, 1.15, "магнит нужно удалять от кольца", 10.5, color=ORANGE)
    txt(ax, -1.5, -1.65, "N кольца притягивает S магнита,\nудаляя магнит, мы совершаем работу", 10.5)
    save(f, "induction-task-magnet-ring")


@fig
def induction_task_frame():
    f, ax = blank(8.4, 5.6, (-4.0, 4.8), (-3.1, 3.1))
    rect(ax, -2.0, 1.7, 4.0, 0.9, fc=NORTH)
    rect(ax, -2.0, -2.6, 4.0, 0.9, fc=SOUTH)
    txt(ax, 0, 2.15, "N", 15, color=PAPER, weight="bold")
    txt(ax, 0, -2.15, "S", 15, color=PAPER, weight="bold")
    for x in (-1.2, 0.0, 1.2):
        arrow(ax, (x, 1.65), (x, -1.65), color=PRIM, lw=1.3, scale=11, alpha=0.7)
    ax.plot([0, 0], [-1.0, 1.0], color=INK, lw=5.0, solid_capstyle="round", zorder=5)
    dot_out(ax, 0, 1.0, r=0.18, color=INK)
    cross_in(ax, 0, -1.0, r=0.18, color=INK)
    arrow(ax, (0.5, 1.0), (1.6, 1.0), color=RED, lw=2.4, scale=13)
    arrow(ax, (-0.5, -1.0), (-1.6, -1.0), color=RED, lw=2.4, scale=13)
    txt(ax, 1.75, 1.0, r"$F_{\mathrm{А}}$", 12, color=RED, ha="left")
    txt(ax, -1.75, -1.0, r"$F_{\mathrm{А}}$", 12, color=RED, ha="right")
    txt(ax, 0.32, 0.0, "N", 12, color=NORTH, weight="bold", ha="left")
    txt(ax, -0.32, 0.0, "S", 12, color=SOUTH, weight="bold", ha="right")
    ax.add_patch(Arc((0, 0), 6.2, 4.4, theta1=-22, theta2=22, color=IND, lw=2.6))
    arrow(ax, (3.1 * np.cos(np.deg2rad(19)), 2.2 * np.sin(np.deg2rad(19))), (3.1 * np.cos(np.deg2rad(23)), 2.2 * np.sin(np.deg2rad(23))), color=IND, lw=2.6, scale=16)
    ax.add_patch(Arc((0, 0), 6.2, 4.4, theta1=158, theta2=202, color=IND, lw=2.6))
    arrow(ax, (3.1 * np.cos(np.deg2rad(199)), 2.2 * np.sin(np.deg2rad(199))), (3.1 * np.cos(np.deg2rad(203)), 2.2 * np.sin(np.deg2rad(203))), color=IND, lw=2.6, scale=16)
    txt(ax, 4.6, -1.7, "вращаем против\nчасовой стрелки", 10.5, color=IND, ha="right")
    txt(ax, -3.9, -1.9, "вид вдоль оси\nот конца a", 10, ha="left", color=GREY)
    txt(ax, 0.2, -3.0, "сила Ампера на рамку с индукционным током мешает вращению", 10, ha="center")
    save(f, "induction-task-frame")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
