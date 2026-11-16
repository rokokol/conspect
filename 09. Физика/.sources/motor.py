"""Graphs and schemes for the note "Действие магнитного поля на ток. Электродвигатель" (section f12, lessons 177-180).

Run: python3 motor.py [name ...]   (matplotlib only)
PNG files go to content/12. Магнитные явления/00. Вложения/ (prefix motor-)
Formulas and curves that are not from the lectures carry the mark "не из лекции" on the picture itself.
"""
import sys

from magnet_common import *  # noqa: F403
from theme import num

FIGS = {}


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


def coil_symbol(ax, x0, x1, y, n=4, color=INK, lw=1.8):
    w = (x1 - x0) / n
    for i in range(n):
        ax.add_patch(Arc((x0 + (i + 0.5) * w, y), w, w * 1.3, theta1=0, theta2=180, color=color, lw=lw))


def galvanometer(ax, x, y, r=0.4, color=INK):
    circ(ax, x, y, r, ec=color)
    arrow(ax, (x - r * 0.55, y - r * 0.6), (x + r * 0.6, y + r * 0.62), color=color, lw=1.6, scale=10)


def resistor(ax, x, y, w=0.9, h=0.32, color=INK):
    rect(ax, x - w / 2, y - h / 2, w, h, fc=PAPER, ec=color, lw=1.6)


def brush_motor(ax, x, y, r=0.45, color=INK, terminals=True):
    circ(ax, x, y, r, ec=color)
    txt(ax, x, y, "M", 13, color=color)
    rect(ax, x - r - 0.28, y - 0.22, 0.28, 0.44, fc=PAPER, ec=color, lw=1.5)
    rect(ax, x + r, y - 0.22, 0.28, 0.44, fc=PAPER, ec=color, lw=1.5)


def horseshoe(ax, x, y, w=1.3, h=0.7, s_left=False):
    rect(ax, x - w / 2, y, 0.32, h, fc=NORTH if not s_left else SOUTH, ec=INK, lw=1.3)
    rect(ax, x + w / 2 - 0.32, y, 0.32, h, fc=SOUTH if not s_left else NORTH, ec=INK, lw=1.3)
    rect(ax, x - w / 2, y + h - 0.02, w, 0.28, fc=IRON, ec=INK, lw=1.3)
    txt(ax, x - w / 2 + 0.16, y - 0.22, "N" if not s_left else "S", 10, color=INK)
    txt(ax, x + w / 2 - 0.16, y - 0.22, "S" if not s_left else "N", 10, color=INK)


# ------------------------------------------------------------------ Ampere force and left-hand rule


@fig
def motor_ampere_four_cases():
    f, axs = blank_multi(2, 3, 11.6, 7.4, (-2.2, 2.2), (-2.5, 2.5))
    cases = [
        # field lines leave N and enter S, so the pole the arrows start from is N
        ("B вниз, ток от нас", "N", "S", -1, "in"),
        ("B вверх, ток от нас", "S", "N", +1, "in"),
        ("B вниз, ток к нам", "N", "S", -1, "out"),
        ("B вверх, ток к нам", "S", "N", +1, "out"),
    ]
    for ax, (title, top, bot, bdir, cur) in zip(axs[:4], cases):
        rect(ax, -1.2, 1.3, 2.4, 0.7, fc=NORTH if top == "N" else SOUTH)
        rect(ax, -1.2, -2.0, 2.4, 0.7, fc=NORTH if bot == "N" else SOUTH)
        txt(ax, 0, 1.65, top, 13, color=PAPER)
        txt(ax, 0, -1.65, bot, 13, color=PAPER)
        for x in (-0.7, 0.7):
            if bdir < 0:
                arrow(ax, (x, 1.0), (x, -1.0), color=FIELD, lw=1.4, scale=11)
            else:
                arrow(ax, (x, -1.0), (x, 1.0), color=FIELD, lw=1.4, scale=11)
        (cross_in if cur == "in" else dot_out)(ax, 0, 0, r=0.22, color=INK)
        # force: F = I x B, z is out of the page; I=-z (in) or +z (out), B=+-y
        i_z = -1 if cur == "in" else 1
        fx = -i_z * bdir  # z x y = -x, so F_x = -(i_z * b_y)
        arrow(ax, (fx * 0.3, 0), (fx * 1.3, 0), color=RED, lw=2.4, scale=15, zorder=8)
        txt(ax, fx * 1.75, 0.3, r"$\vec F_А$", 13, color=RED)
        ax.set_title(title, fontsize=11)
    # I along B
    ax = axs[4]
    for y in (-0.6, 0.0, 0.6):
        arrow(ax, (-1.6, y - 0.9), (1.6, y - 0.9), color=FIELD, lw=1.3, scale=10)
    line(ax, [(-1.3, 0.7), (1.3, 0.7)], lw=4)
    arrow(ax, (0.2, 0.7), (0.9, 0.7), color=RED, lw=2, scale=12)
    txt(ax, 0, 1.3, "провод", 10)
    txt(ax, 0, -2.0, r"$\vec F_А=0$", 13, color=RED)
    txt(ax, -1.3, 0.05, "B", 11, color=FIELD)
    ax.set_title("ток вдоль поля", fontsize=11)
    # oblique wire: F perpendicular to both
    ax = axs[5]
    for y in (-0.6, 0.0, 0.6):
        arrow(ax, (-1.8, y - 1.0), (1.8, y - 1.0), color=FIELD, lw=1.3, scale=10)
    line(ax, [(-1.0, 0.0), (1.0, 1.5)], lw=4)
    arrow(ax, (0.2, 0.75), (0.7, 1.12), color=INK, lw=2, scale=12)
    txt(ax, 1.2, 0.8, "I", 11)
    txt(ax, -2.1, -0.75, "B", 11, color=FIELD)  # between two field arrows, off their tails
    # I x B = (1, 1, 0) x (1, 0, 0) = (0, 0, -1): the force points away from the viewer
    cross_in(ax, -0.85, 1.35, r=0.17, color=RED)
    txt(ax, -0.45, 1.35, r"$\vec F_А$", 11, color=RED)
    ax.set_title("под углом к полю", fontsize=11)
    txt(ax, 0, -2.2, "сила перпендикулярна току и полю,\nона направлена от нас, за плоскость рисунка", 10, color=RED)
    save(f, "motor-ampere-four-cases")


@fig
def motor_left_hand_rule():
    f, ax = blank(8.4, 6.0, (-3.2, 6.2), (-3.6, 3.2))

    def P(x, y, z):
        return (x - 0.55 * z, y - 0.5 * z)

    # palm: a parallelogram in the x-z plane at y = 0, it is perpendicular to B (B is along y)
    corners = [P(0.0, 0, -1.4), P(2.8, 0, -1.4), P(2.8, 0, 1.4), P(0.0, 0, 1.4)]
    poly(ax, corners, fc=tint(WARM, 0.7), ec=INK, lw=1.6, zorder=1)
    # four fingers lie along x, the direction of the current
    for zz in (-1.0, -0.35, 0.3, 0.95):
        line(ax, [P(2.8, 0, zz), P(4.0, 0, zz)], color=WARM, lw=9, zorder=2)
    arrow(ax, P(3.3, 0, 0.0), P(5.0, 0, 0.0), color=INK, lw=2.4, scale=15, zorder=6)
    txt(ax, 5.0, 0.55, "I: четыре пальца", 10.5, ha="left")
    # B lines go up and enter the palm from below
    for xx, zz in ((0.6, -0.8), (1.5, 0.5), (2.3, -0.6)):
        arrow(ax, P(xx, -2.0, zz), P(xx, -0.05, zz), color=FIELD, lw=1.8, scale=12, zorder=5)
    txt(ax, 3.3, -2.9, "линии B входят в ладонь", 10.5, color=FIELD, ha="left")
    # thumb: the force is perpendicular to both, along z toward the viewer
    arrow(ax, P(1.4, 0, 1.4), P(1.4, 0, 3.4), color=RED, lw=3, scale=17, zorder=6)
    txt(ax, P(1.4, 0, 3.4)[0] - 0.2, P(1.4, 0, 3.4)[1] - 0.25, "F: большой палец,\nотогнутый на 90°", 10.5, color=RED, ha="right")
    txt(ax, 1.0, 2.8, "левая рука", 12)
    save(f, "motor-left-hand-rule")


@fig
def motor_parallel_currents():
    f, axs = blank_multi(1, 2, 11.0, 4.6, (-3.6, 3.6), (-2.3, 2.3))
    for k, ax in enumerate(axs):
        xs = (-1.3, 1.3)
        same = k == 1
        # currents: first out of the page; second out (same) or in (opposite)
        for j, x in enumerate(xs):
            out = True if j == 0 else same
            (dot_out if out else cross_in)(ax, x, 0, r=0.2, color=INK)
            for rr in (0.6, 1.0):
                th = np.linspace(0, 2 * np.pi, 200)
                ax.plot(x + rr * np.cos(th), rr * np.sin(th), color=FIELD, lw=1.1, alpha=0.8)
                s = 1 if out else -1
                a0 = np.pi * 0.75
                arrow(ax, (x + rr * np.cos(a0), rr * np.sin(a0)), (x + rr * np.cos(a0 + s * 0.12), rr * np.sin(a0 + s * 0.12)), color=FIELD, lw=1.1, scale=9)
        if same:
            arrow(ax, (-1.3, -1.6), (-0.3, -1.6), color=RED, lw=2.4, scale=15)
            arrow(ax, (1.3, -1.6), (0.3, -1.6), color=RED, lw=2.4, scale=15)
            txt(ax, 0, -2.05, "токи одного направления притягиваются", 11, color=RED)
            ax.set_title("ток в обоих проводах к нам", fontsize=11)
        else:
            arrow(ax, (-1.3, -1.6), (-2.3, -1.6), color=RED, lw=2.4, scale=15)
            arrow(ax, (1.3, -1.6), (2.3, -1.6), color=RED, lw=2.4, scale=15)
            txt(ax, 0, -2.05, "противоположные токи отталкиваются", 11, color=RED)
            ax.set_title("ток в левом проводе к нам, в правом от нас", fontsize=11)
        txt(ax, xs[0], 1.4, "1", 11)
        txt(ax, xs[1], 1.4, "2", 11)
    save(f, "motor-parallel-currents")


@fig
def motor_force_angle():
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    a = np.linspace(0, 180, 361)
    ax.plot(a, np.sin(np.radians(a)), color=RED, lw=2.6)
    ax.plot([0, 90, 180], [0, 1, 0], "o", color=INK)
    ax.set_xticks([0, 30, 60, 90, 120, 150, 180])
    ax.set_xlabel(r"угол $\alpha$ между током и полем, град")
    ax.set_ylabel(r"$F_А\ /\ F_{А,\max}$")
    ax.set_title("Сила Ампера и угол")
    ax.text(90, 0.45, r"$F_А\sim\sin\alpha$", ha="center", fontsize=13, color=RED)
    # the note stands under the curve, clear of it and of the axis, and points at the zero
    ax.annotate("ток вдоль поля:\nсилы нет", xy=(1.5, 0.02), xytext=(32, 0.1), fontsize=9.5, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(178, 1.1, "формула 10 класса, не из лекции", ha="right", color=GREY, fontsize=9)
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.2)
    grid(ax)
    save(f, "motor-force-angle")


# ------------------------------------------------------------------ frame in the field


def _frame_panel(ax, phi_deg, title, note=None, wrong_torque=False):
    """Frame seen along its axis. B goes to the right, side A carries the current to the viewer, side B away."""
    phi = np.radians(phi_deg)
    for y in (-1.2, -0.4, 0.4, 1.2):
        arrow(ax, (-2.0, y), (2.0, y), color=FIELD, lw=1.1, scale=9, alpha=0.7)
    txt(ax, 2.35, 1.2, "B", 11, color=FIELD)
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), color=GREY, lw=1, ls=":")
    ax_, ay_ = -np.cos(phi), np.sin(phi)
    line(ax, [(ax_, ay_), (-ax_, -ay_)], color=INK, lw=3)
    ax.plot([0], [0], "+", color=INK, ms=9)
    dot_out(ax, ax_, ay_, r=0.14)
    cross_in(ax, -ax_, -ay_, r=0.14)
    arrow(ax, (ax_, ay_), (ax_, ay_ + 0.8), color=RED, lw=2.4, scale=13, zorder=8)
    arrow(ax, (-ax_, -ay_), (-ax_, -ay_ - 0.8), color=RED, lw=2.4, scale=13, zorder=8)
    txt(ax, ax_ - 0.3, ay_ + 0.95, r"$F_1$", 11, color=RED)
    txt(ax, -ax_ + 0.3, -ay_ - 0.95, r"$F_2$", 11, color=RED)
    ax.set_title(title, fontsize=11)
    if note:
        txt(ax, 0, -2.75, note, 10.5, color=RED if wrong_torque else INK)


@fig
def motor_frame_positions():
    f, axs = blank_multi(1, 4, 13.2, 4.0, (-2.7, 2.9), (-3.4, 2.2))
    _frame_panel(axs[0], 0, "плоскость вдоль поля", "момент наибольший\nрамка идёт по часовой")
    _frame_panel(axs[1], 45, "поворот на 45°", "момент меньше")
    _frame_panel(axs[2], 90, "плоскость перпендикулярна полю", "силы только растягивают\nрамка замирает")
    _frame_panel(axs[3], 135, "проскочила по инерции", "без коллектора\nсилы тянут назад", wrong_torque=True)
    save(f, "motor-frame-positions")


@fig
def motor_torque_angle():
    f, axs = plt.subplots(3, 1, figsize=(7.4, 7.4), sharex=True)
    p = np.linspace(0, 360, 721)
    r = np.radians(p)
    curves = [
        (np.cos(r), "без коллектора: момент меняет знак", BLUE),
        (np.abs(np.cos(r)), "коллектор, одна рамка: знак сохраняется, но есть мёртвые точки", GREEN),
        (np.abs(np.cos(r)) + np.abs(np.sin(r)), "коллектор, две рамки: момент не падает до нуля", RED),
    ]
    for ax, (y, title, col) in zip(axs, curves):
        ax.plot(p, y, color=col, lw=2.4)
        ax.axhline(0, color=GREY, lw=1)
        ax.set_title(title, fontsize=11, loc="left")
        ax.set_ylabel("момент, отн. ед.")
        for x in (90, 270):
            ax.axvline(x, color=GRID, lw=1.2, ls="--")
        grid(ax)
    axs[0].text(92, 0.6, "плоскость перпендикулярна полю", fontsize=9, color=GREY)  # above the zero line, clear of the curve
    axs[1].text(92, 0.55, "мёртвая\nточка", fontsize=9, color=GREY)
    axs[2].set_xlabel(r"угол поворота $\varphi$ от положения вдоль поля, град")
    axs[2].set_xticks(range(0, 361, 90))
    axs[2].set_xlim(0, 360)
    axs[2].text(358, 0.15, "кривые не из лекции", ha="right", fontsize=9, color=GREY)
    f.tight_layout()
    save(f, "motor-torque-angle")


def _commutator_panel(ax, a_deg, title):
    a = np.radians(a_deg)
    # ring halves: A covers a-90..a+90
    ax.add_patch(Wedge((0, 0), 0.75, a_deg - 90, a_deg + 90, width=0.28, fc=tint(BLUE, 0.6), ec=INK, lw=1.4))
    ax.add_patch(Wedge((0, 0), 0.75, a_deg + 90, a_deg + 270, width=0.28, fc=tint(RED, 0.7), ec=INK, lw=1.4))
    # brushes at left (+) and right (-)
    rect(ax, -1.25, -0.16, 0.5, 0.32, fc=PAPER, zorder=5)
    rect(ax, 0.75, -0.16, 0.5, 0.32, fc=PAPER, zorder=5)
    # the signs stand above the brushes, clear of the frame line
    txt(ax, -1.0, 0.45, "+", 13)
    txt(ax, 1.0, 0.45, "−", 13)
    # frame edge-on
    ax_, ay_ = 1.8 * np.cos(a), 1.8 * np.sin(a)
    line(ax, [(ax_, ay_), (-ax_, -ay_)], color=INK, lw=3)
    out_a = np.cos(a) < -1e-6
    at_gap = abs(np.cos(a)) < 1e-6
    for sgn, (px, py) in ((1, (ax_, ay_)), (-1, (-ax_, -ay_))):
        cur_out = out_a if sgn == 1 else (not out_a)
        if at_gap:
            circ(ax, px, py, 0.14, fc=PAPER, ec=GREY, lw=1.2, zorder=6)
            continue
        (dot_out if cur_out else cross_in)(ax, px, py, r=0.14)
        fy = 1 if cur_out else -1
        arrow(ax, (px, py), (px, py + fy * 0.8), color=RED, lw=2.3, scale=13, zorder=8)
    txt(ax, ax_ - 0.35, ay_ + (0.15 if ay_ >= 0 else -0.15), "A", 11, color=BLUE)
    txt(ax, -ax_ + 0.35, -ay_ + (-0.15 if ay_ >= 0 else 0.15), "B", 11, color=ORANGE)
    txt(ax, 0, -3.15, title, 10.5)
    # field
    for y in (-2.05, 2.05):
        arrow(ax, (-2.4, y), (2.4, y), color=FIELD, lw=1.0, scale=8, alpha=0.6)


@fig
def motor_commutator_cycle():
    f, axs = blank_multi(1, 4, 13.6, 4.4, (-2.9, 2.9), (-3.6, 2.6))
    _commutator_panel(axs[0], 170, "рамка вдоль поля\nток A к нам")
    _commutator_panel(axs[1], 125, "поворот идёт\nсилы прежние")
    _commutator_panel(axs[2], 90, "разрезы у щёток\nмомента нет")
    _commutator_panel(axs[3], 55, "A на другом полукольце\nток и силы сменили знак")
    save(f, "motor-commutator-cycle")


@fig
def motor_real_parts():
    f, ax = blank(11.2, 5.6, (-0.5, 11.0), (-3.6, 3.4))
    # shaft
    line(ax, [(0.3, 0), (9.6, 0)], color=GREY, lw=5)
    # stator poles with excitation windings
    rect(ax, 2.0, 1.45, 3.4, 1.0, fc=IRON)
    rect(ax, 2.0, -2.45, 3.4, 1.0, fc=IRON)
    rect(ax, 3.1, 0.95, 1.2, 0.5, fc=NORTH, ec=INK)
    rect(ax, 3.1, -1.45, 1.2, 0.5, fc=SOUTH, ec=INK)
    txt(ax, 3.7, 1.2, "N", 12, color=PAPER)
    txt(ax, 3.7, -1.2, "S", 12, color=PAPER)
    coil_horizontal(ax, 2.2, 5.2, 2.1, h=0.5, n=8, core=False, wind=1, lw=1.4)
    coil_horizontal(ax, 2.2, 5.2, -2.1, h=0.5, n=8, core=False, wind=1, lw=1.4)
    # rotor: iron core with windings in slots
    rect(ax, 2.3, -0.9, 2.8, 1.8, fc=IRON, ec=INK, lw=1.6, zorder=2)
    for x in np.linspace(2.5, 4.7, 7):  # the last turn ends at 5.0, inside the rotor core (right edge 5.1)
        ax.plot([x, x + 0.3], [-0.85, 0.85], color=COPPER, lw=2.4, zorder=3)
    # bearings
    rect(ax, 1.3, -0.3, 0.5, 0.6, fc=IRON)
    rect(ax, 6.0, -0.3, 0.5, 0.6, fc=IRON)
    # commutator
    for k, y in enumerate(np.linspace(-0.6, 0.6, 7)[:-1]):
        rect(ax, 6.9, y, 1.2, 0.2, fc=COPPER if k % 2 == 0 else tint(COPPER, 0.6), ec=INK, lw=0.9, zorder=3)
    # brushes with springs
    for sgn in (1, -1):
        # the brush touches the commutator (|y| = 0.6) and the spring starts at the brush end
        rect(ax, 7.2, 0.6 if sgn > 0 else -1.1, 0.6, 0.5, fc=tint(INK, 0.3), ec=INK, zorder=4)
        ys = np.linspace(sgn * 1.1, sgn * 2.15, 7)
        zz = [(7.5 + (0.22 if i % 2 else -0.22), y) for i, y in enumerate(ys)]
        line(ax, zz, color=INK, lw=1.4)
        line(ax, [(7.5, sgn * 2.15), (7.5, sgn * 2.7), (9.4, sgn * 2.7)], color=INK, lw=1.4)
        terminal(ax, 9.4, sgn * 2.7)
    # labels
    txt(ax, 3.7, 3.05, "статор: полюса с обмоткой возбуждения\nили постоянные магниты", 10.5)
    txt(ax, 3.7, -3.2, "ротор (якорь): рамки в пазах железного сердечника", 10.5)
    txt(ax, 8.5, -0.9, "коллектор", 10.5, ha="left")
    arrow(ax, (8.4, -0.8), (8.15, -0.4), color=INK, lw=1.0, scale=8)
    txt(ax, 8.5, 1.65, "угольная щётка\nи прижимная пружина", 10, ha="left")
    txt(ax, 1.55, -0.75, "подшипник", 10)
    txt(ax, 0.3, 0.55, "вал", 10.5)
    save(f, "motor-real-parts")


@fig
def motor_symbols():
    f, axs = blank_multi(1, 4, 13.2, 3.6, (-2.4, 2.4), (-2.6, 2.6))
    # a) permanent magnet excitation
    ax = axs[0]
    horseshoe(ax, 0, 1.2, w=1.5)
    brush_motor(ax, 0, -0.6)
    line(ax, [(-0.73, -0.6), (-1.6, -0.6)])
    line(ax, [(0.73, -0.6), (1.6, -0.6)])
    terminal(ax, -1.6, -0.6)
    terminal(ax, 1.6, -0.6)
    ax.set_title("постоянный магнит", fontsize=10.5)
    # b) electromagnet excitation, separate supply
    ax = axs[1]
    rect(ax, -0.8, 1.1, 1.6, 0.35, fc=IRON)
    rect(ax, -0.8, 0.8, 0.3, 0.3, fc=IRON)
    rect(ax, 0.5, 0.8, 0.3, 0.3, fc=IRON)
    coil_symbol(ax, -0.5, 0.5, 1.45, n=4)
    line(ax, [(-0.5, 1.45), (-0.9, 1.45), (-0.9, 2.0)])
    line(ax, [(0.5, 1.45), (0.9, 1.45), (0.9, 2.0)])
    terminal(ax, -0.9, 2.0)
    terminal(ax, 0.9, 2.0)
    brush_motor(ax, 0, -0.6)
    line(ax, [(-0.73, -0.6), (-1.6, -0.6)])
    line(ax, [(0.73, -0.6), (1.6, -0.6)])
    terminal(ax, -1.6, -0.6)
    terminal(ax, 1.6, -0.6)
    ax.set_title("электромагнит", fontsize=10.5)
    # c) series
    ax = axs[2]
    brush_motor(ax, -0.6, 0.0)
    line(ax, [(-1.33, 0), (-1.9, 0)])
    terminal(ax, -1.9, 0)
    line(ax, [(-0.12, 0), (0.3, 0)])
    coil_symbol(ax, 0.3, 1.5, 0.0, n=4)
    line(ax, [(1.5, 0), (2.0, 0)])
    terminal(ax, 2.0, 0)
    txt(ax, 0.9, 0.8, "обмотка\nвозбуждения", 9.5)
    txt(ax, 0, -1.4, "сериесный: ротор и обмотка\nпоследовательно", 10)
    ax.set_title("последовательное", fontsize=10.5)
    # d) parallel
    ax = axs[3]
    brush_motor(ax, 0.0, -0.6)
    line(ax, [(-0.73, -0.6), (-1.5, -0.6), (-1.5, 1.2)])
    line(ax, [(0.73, -0.6), (1.5, -0.6), (1.5, 1.2)])
    line(ax, [(-1.5, 1.2), (-1.0, 1.2)])
    coil_symbol(ax, -1.0, 1.0, 1.2, n=4)
    line(ax, [(1.0, 1.2), (1.5, 1.2)])
    line(ax, [(-1.5, -0.6), (-1.5, -1.6), (-1.9, -1.6)])
    line(ax, [(1.5, -0.6), (1.5, -1.6), (1.9, -1.6)])
    terminal(ax, -1.9, -1.6)
    terminal(ax, 1.9, -1.6)
    node(ax, -1.5, -0.6)
    node(ax, 1.5, -0.6)
    txt(ax, 0, -2.3, "шунтовый: ротор и обмотка\nпараллельно", 10)
    ax.set_title("параллельное", fontsize=10.5)
    save(f, "motor-symbols")


# ------------------------------------------------------------------ measuring instruments


@fig
def motor_magnetoelectric():
    f, ax = blank(7.6, 6.2, (-3.6, 3.6), (-3.0, 4.2))
    # pole shoes (arcs) and iron core
    ax.add_patch(Wedge((0, 0), 2.4, 125, 235, width=0.6, fc=NORTH, ec=INK, lw=1.4))
    ax.add_patch(Wedge((0, 0), 2.4, -55, 55, width=0.6, fc=SOUTH, ec=INK, lw=1.4))
    txt(ax, -2.1, 0.0, "N", 14, color=PAPER)
    txt(ax, 2.1, 0.0, "S", 14, color=PAPER)
    circ(ax, 0, 0, 1.0, fc=IRON, ec=INK, lw=1.6, zorder=2)
    txt(ax, 0, -0.35, "железный\nсердечник", 9.5, zorder=9)
    # radial field: from the N shoe to the core and from the core to the S shoe
    for ang in (155, 180, 205):
        a = np.radians(ang)
        arrow(ax, (1.8 * np.cos(a), 1.8 * np.sin(a)), (1.05 * np.cos(a), 1.05 * np.sin(a)), color=FIELD, lw=1.0, scale=8, zorder=3)
    for ang in (-25, 0, 25):
        a = np.radians(ang)
        arrow(ax, (1.05 * np.cos(a), 1.05 * np.sin(a)), (1.8 * np.cos(a), 1.8 * np.sin(a)), color=FIELD, lw=1.0, scale=8, zorder=3)
    # frame sides in the gap, turned slightly
    b = np.radians(20)
    r = 1.42
    pa = (-r * np.cos(b), r * np.sin(b))
    pb = (r * np.cos(b), -r * np.sin(b))
    line(ax, [pa, pb], color=COPPER, lw=2.5, zorder=4)
    dot_out(ax, *pa, r=0.14)
    cross_in(ax, *pb, r=0.14)
    # B is radial, so F = I x B is perpendicular to the radius, that is, to the frame: the tangent (sin b, cos b)
    tang = np.array([np.sin(b), np.cos(b)])
    arrow(ax, pa, (pa[0] + 0.7 * tang[0], pa[1] + 0.7 * tang[1]), color=RED, lw=2.4, scale=13, zorder=8)
    arrow(ax, pb, (pb[0] - 0.7 * tang[0], pb[1] - 0.7 * tang[1]), color=RED, lw=2.4, scale=13, zorder=8)
    txt(ax, pa[0] + 0.7 * tang[0] + 0.4, pa[1] + 0.7 * tang[1] + 0.1, r"$F_1$", 11, color=RED)
    txt(ax, pb[0] - 0.7 * tang[0] - 0.4, pb[1] - 0.7 * tang[1] - 0.1, r"$F_2$", 11, color=RED)
    # pointer and scale above
    scale_r = 3.3
    ax.add_patch(Arc((0, 0.6), 2 * scale_r, 2 * scale_r, theta1=40, theta2=140, color=INK, lw=1.6))
    for t in np.linspace(45, 135, 10):
        tr = np.radians(t)
        line(ax, [(scale_r * np.cos(tr), 0.6 + scale_r * np.sin(tr)), ((scale_r - 0.2) * np.cos(tr), 0.6 + (scale_r - 0.2) * np.sin(tr))], color=INK, lw=1.2)
    tp = np.radians(70)
    arrow(ax, (0, 0.6), ((scale_r - 0.15) * np.cos(tp), 0.6 + (scale_r - 0.15) * np.sin(tp)), color=RED, lw=2.4, scale=1)
    txt(ax, 0, 4.0, "равномерная шкала", 11)
    txt(ax, -3.3, -2.6, "две спиральные пружины: подводят ток к рамке\nи возвращают её в нулевое положение", 10, ha="left")
    save(f, "motor-magnetoelectric")


@fig
def motor_electromagnetic_instrument():
    f, ax = blank(8.4, 6.0, (-1.4, 7.6), (-2.4, 4.6))
    # coil
    rect(ax, 0.0, -1.0, 2.8, 2.0, fc=PAPER, ec=INK, lw=1.6)
    for x in np.linspace(0.3, 2.5, 8):
        ax.plot([x, x + 0.15], [-1.1, 1.1], color=COPPER, lw=2.4, zorder=3)
    # the leads start at the ends of the winding (the first turn, and the last one after its back half), below the plate
    line(ax, [(0.3, -1.1), (0.3, -1.3), (-0.7, -1.3), (-0.7, -1.9)])
    line(ax, [(2.8, -1.1), (2.8, -1.3), (3.5, -1.3), (3.5, -1.9)])
    terminal(ax, -0.7, -1.9)
    terminal(ax, 3.5, -1.9)
    txt(ax, 1.4, -1.6, "катушка", 10.5)
    # iron plate on an axis: partly inside the coil
    ax.plot([3.9], [0.0], "o", color=INK, ms=8, zorder=8)
    poly(ax, [(3.9, 0.0), (2.3, 0.45), (1.3, 0.25), (1.3, -0.25), (2.3, -0.4)], fc=IRON, ec=INK, lw=1.4, zorder=6)
    txt(ax, 2.0, 1.75, "железная пластина", 10.5)
    arrow(ax, (2.0, 1.5), (2.0, 0.4), color=INK, lw=1.0, scale=8, zorder=9)
    # spiral spring
    th = np.linspace(0, 6 * np.pi, 200)
    ax.plot(3.9 + (0.08 + 0.04 * th / np.pi) * np.cos(th), 0.0 + (0.08 + 0.04 * th / np.pi) * np.sin(th), color=INK, lw=1.2, zorder=7)
    txt(ax, 4.9, -0.95, "спиральная\nпружина", 10)
    arrow(ax, (4.5, -0.6), (4.0, -0.3), color=INK, lw=1.0, scale=8)
    # pointer and scale
    arrow(ax, (3.9, 0.0), (3.9 + 0.4, 3.3), color=RED, lw=2.4, scale=1)
    ax.add_patch(Arc((3.9, 0.0), 7.0, 7.0, theta1=68, theta2=98, color=INK, lw=1.6))
    # the current is proportional to the root of the deflection: equal steps of the current give marks that crowd at the zero (96 deg)
    for t in 96 - 26 * np.linspace(0, 1, 9) ** 2:
        tr = np.radians(t)
        line(ax, [(3.9 + 3.5 * np.cos(tr), 3.5 * np.sin(tr)), (3.9 + 3.3 * np.cos(tr), 3.3 * np.sin(tr))], lw=1.1)
    txt(ax, 5.2, 3.7, "неравномерная шкала", 10.5)
    # air damper: piston in a tube
    rect(ax, 5.6, 1.2, 1.6, 0.8, fc=PAPER, ec=INK, lw=1.4)
    rect(ax, 6.2, 1.25, 0.22, 0.7, fc=IRON, ec=INK, lw=1.1)
    line(ax, [(4.08, 1.5), (6.2, 1.6)], lw=1.4)
    txt(ax, 6.4, 2.35, "воздушный успокоитель", 10)
    save(f, "motor-electromagnetic-instrument")


@fig
def motor_scale_uniform():
    f, ax = plt.subplots(figsize=(6.6, 4.4))
    i = np.linspace(0, 1, 200)
    ax.plot(i, i, color=BLUE, lw=2.6, label="магнитоэлектрическая: равномерная")
    ax.plot(i, i**2, color=RED, lw=2.6, label="электромагнитная: неравномерная")
    for x in np.linspace(0, 1, 6):
        ax.plot([x, x], [0, x], color=GRID, lw=1)
        ax.plot([x, x], [0, x**2], color=GRID, lw=1)
    ax.set_xlabel(r"сила тока $I/I_{\max}$")
    ax.set_ylabel(r"отклонение стрелки $\theta/\theta_{\max}$")
    ax.set_title("Шкалы двух систем")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.text(0.98, 0.04, "зависимости не из лекции", ha="right", color=GREY, fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    grid(ax)
    save(f, "motor-scale-uniform")


@fig
def motor_instrument_symbols():
    f, ax = blank(8.8, 6.0, (-0.5, 10.5), (-6.4, 1.0))
    rows = [
        ("electro", "электромагнитная система: катушка и втягиваемый сердечник"),
        ("magneto", "магнитоэлектрическая система: магнит и рамка"),
        ("ac", "для цепей переменного тока"),
        ("dc", "для цепей постоянного тока"),
        ("both", "для цепей постоянного и переменного тока"),
        ("vert", "рабочее положение шкалы вертикальное"),
        ("horiz", "рабочее положение шкалы горизонтальное"),
    ]
    for k, (kind, text) in enumerate(rows):
        y = -k * 0.9
        x = 1.0
        if kind == "electro":
            line(ax, [(x - 0.7, y), (x - 0.5, y), (x - 0.3, y + 0.28), (x - 0.1, y - 0.28), (x + 0.1, y + 0.28), (x + 0.3, y - 0.28), (x + 0.5, y), (x + 0.7, y)], lw=1.6)
            ax.plot([x - 0.3, x + 0.3], [y, y], color=INK, lw=5, solid_capstyle="butt")
        elif kind == "magneto":
            rect(ax, x - 0.4, y - 0.3, 0.8, 0.6, fc=PAPER, lw=1.4)
            line(ax, [(x - 0.7, y - 0.05), (x - 0.4, y - 0.05)], lw=1.6)
            line(ax, [(x + 0.4, y - 0.05), (x + 0.7, y - 0.05)], lw=1.6)
            rect(ax, x - 0.22, y - 0.14, 0.44, 0.28, fc=PAPER, lw=1.3)
        elif kind == "ac":
            t = np.linspace(0, 2 * np.pi, 60)
            ax.plot(x - 0.4 + 0.8 * t / (2 * np.pi), y + 0.14 * np.sin(t), color=INK, lw=2)
        elif kind == "dc":
            line(ax, [(x - 0.4, y), (x + 0.4, y)], lw=2.2)
        elif kind == "both":
            t = np.linspace(0, 2 * np.pi, 60)
            ax.plot(x - 0.4 + 0.8 * t / (2 * np.pi), y + 0.12 + 0.12 * np.sin(t), color=INK, lw=2)
            line(ax, [(x - 0.4, y - 0.1), (x + 0.4, y - 0.1)], lw=2.2)
        elif kind == "vert":
            line(ax, [(x, y - 0.3), (x, y + 0.3)], lw=2)
            line(ax, [(x - 0.3, y - 0.3), (x + 0.3, y - 0.3)], lw=2)
        elif kind == "horiz":
            line(ax, [(x - 0.3, y - 0.3), (x - 0.3, y + 0.1), (x + 0.3, y + 0.1), (x + 0.3, y - 0.3)], lw=2)
        txt(ax, 2.3, y, text, 11, ha="left")
    save(f, "motor-instrument-symbols")


@fig
def motor_voltmeter_ammeter():
    f, axs = blank_multi(1, 2, 12.2, 4.0, (-2.4, 4.8), (-2.4, 2.4))
    # voltmeter: galvanometer in series with an additional resistor
    ax = axs[0]
    line(ax, [(-2.2, 0), (-1.2, 0)])
    galvanometer(ax, -0.85, 0.0, r=0.42)
    line(ax, [(-0.43, 0), (0.35, 0)])
    resistor(ax, 0.8, 0.0, w=0.9)
    line(ax, [(1.25, 0), (2.4, 0)])
    terminal(ax, -2.2, 0)
    terminal(ax, 2.4, 0)
    txt(ax, -0.85, -0.75, r"$r,\ I_0$", 11)
    txt(ax, 0.8, 0.55, r"$R_д$", 11)
    line(ax, [(-2.2, -1.3), (2.4, -1.3)], lw=1.2)
    arrow(ax, (-2.2, -1.3), (-2.05, -1.3), lw=1.2, scale=8)
    arrow(ax, (2.4, -1.3), (2.25, -1.3), lw=1.2, scale=8)
    txt(ax, 0.1, -1.85, r"$U=I_0\,(r+R_д)$", 11.5)
    txt(ax, 0.1, 1.9, "вольтметр: добавочное сопротивление\nпоследовательно с гальванометром", 10.5)
    # ammeter: galvanometer with a shunt in parallel
    ax = axs[1]
    line(ax, [(-2.2, 0), (-1.2, 0), (-1.2, 0.0)])
    line(ax, [(-1.2, 0), (-1.2, 1.1), (0.4, 1.1)], lw=1.8)
    resistor(ax, 0.9, 1.1, w=0.9)
    line(ax, [(1.35, 1.1), (2.0, 1.1), (2.0, 0)])
    line(ax, [(-1.2, 0), (-0.55, 0)])
    galvanometer(ax, -0.1, 0.0, r=0.42)
    line(ax, [(0.32, 0), (2.0, 0), (3.2, 0)])
    node(ax, -1.2, 0)
    node(ax, 2.0, 0)
    terminal(ax, -2.2, 0)
    terminal(ax, 3.2, 0)
    txt(ax, 0.9, 1.65, r"$R_ш$", 11)
    txt(ax, -0.1, -0.85, r"$r,\ I_0$", 11)
    txt(ax, -1.75, 0.35, r"$I$", 11)
    txt(ax, 0.9, 0.62, r"$I-I_0$", 10)
    txt(ax, 0.9, -1.55, r"$R_ш=r\,\dfrac{I_0}{I-I_0}$", 12)
    txt(ax, 0.6, 2.35, "амперметр: шунт параллельно гальванометру", 10.5)
    save(f, "motor-voltmeter-ammeter")


@fig
def motor_shunt_graphs():
    f, axs = plt.subplots(1, 2, figsize=(11.6, 4.4))
    ax = axs[0]
    u = np.linspace(0, 21, 100)
    ax.plot(u, u / 1e-3 - 10, color=BLUE, lw=2.4)
    for uu in (1, 5, 20):
        r = uu / 1e-3 - 10
        ax.plot([uu], [r], "o", color=RED, zorder=5)
        ax.annotate(f"{uu} В: {r:.0f} Ом", (uu, r), textcoords="offset points", xytext=(10, -6 if uu == 1 else -14), ha="left", fontsize=10)  # the 1 V note keeps clear of both the axis and the line
    ax.set_xlabel("предел вольтметра $U$, В")
    ax.set_ylabel(r"добавочное сопротивление $R_д$, Ом")
    ax.set_title("Добавочное сопротивление")
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 22000)
    grid(ax)
    ax = axs[1]
    i = np.linspace(1.6, 110, 400)
    ax.plot(i, 10 * 1.0 / (i - 1.0), color=BLUE, lw=2.4)
    for ii in (5, 20, 100):
        r = 10 * 1.0 / (ii - 1.0)
        ax.plot([ii], [r], "o", color=RED, zorder=5)
        ax.annotate(f"{num(ii, '')} мА: {num(r, 3)} Ом", (ii, r), textcoords="offset points", xytext=(6, 8), ha="left", fontsize=10)
    ax.set_xlabel("предел миллиамперметра $I$, мА")
    ax.set_ylabel(r"сопротивление шунта $R_ш$, Ом")
    ax.set_title("Шунт")
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 8)
    grid(ax)
    ax.text(110, 7.4, "$r=10$ Ом, $I_0=1$ мА", ha="right", fontsize=10, color=GREY)
    f.tight_layout()
    save(f, "motor-shunt-graphs")


@fig
def motor_shunt_schemes():
    f, axs = blank_multi(1, 2, 12.6, 4.6, (-2.6, 4.4), (-2.6, 2.8))
    # scheme 1: clamps -> galvanometer, shunt in a bypass (bad)
    ax = axs[0]
    line(ax, [(-2.2, 0), (-1.1, 0)])
    node(ax, -1.1, 0)
    line(ax, [(-1.1, 0), (-0.55, 0)])
    galvanometer(ax, -0.1, 0.0, r=0.42)
    line(ax, [(0.32, 0), (1.5, 0)])
    node(ax, 1.5, 0)
    line(ax, [(1.5, 0), (2.4, 0)])
    line(ax, [(-1.1, 0), (-1.1, 1.2), (-0.2, 1.2)])
    resistor(ax, 0.3, 1.2, w=0.9)
    line(ax, [(0.75, 1.2), (1.5, 1.2), (1.5, 0)])
    terminal(ax, -2.2, 0)
    terminal(ax, 2.4, 0)
    ax.add_patch(Circle((-1.1, 0.6), 0.32, fill=False, ec=RED, lw=1.6, ls="--"))
    txt(ax, 0.3, 1.75, r"$R_ш$", 11)
    txt(ax, -0.1, -0.75, "гальванометр", 10)
    txt(ax, 0.1, 2.35, "схема 1: плохая", 12, color=RED)
    txt(ax, 0.1, -1.7, "обрыв контакта у шунта:\nвесь ток идёт через гальванометр\nстрелка бьёт в край шкалы, прибор портится", 10, color=RED)
    # scheme 2: clamps -> shunt, galvanometer in a bypass (good)
    ax = axs[1]
    line(ax, [(-2.2, 0), (-1.1, 0)])
    node(ax, -1.1, 0)
    line(ax, [(-1.1, 0), (-0.45, 0)])
    resistor(ax, 0.0, 0.0, w=0.9)
    line(ax, [(0.45, 0), (1.5, 0)])
    node(ax, 1.5, 0)
    line(ax, [(1.5, 0), (2.4, 0)])
    line(ax, [(-1.1, 0), (-1.1, 1.3), (-0.55, 1.3)])
    galvanometer(ax, -0.1, 1.3, r=0.42)
    line(ax, [(0.32, 1.3), (1.5, 1.3), (1.5, 0)])
    terminal(ax, -2.2, 0)
    terminal(ax, 2.4, 0)
    ax.add_patch(Circle((-1.1, 0.65), 0.32, fill=False, ec=GREEN, lw=1.6, ls="--"))
    txt(ax, 0.0, -0.5, r"$R_ш$", 11)
    txt(ax, -0.1, 2.0, "гальванометр", 10)
    txt(ax, 0.1, 2.5, "схема 2: хорошая", 12, color=GREEN)
    txt(ax, 0.1, -1.7, "обрыв контакта у гальванометра:\nток идёт через шунт\nстрелка возвращается к нулю, прибор цел", 10, color=GREEN)
    save(f, "motor-shunt-schemes")


# ------------------------------------------------------------------ tasks


@fig
def motor_task_frame():
    f, axs = blank_multi(1, 2, 11.2, 4.6, (-3.2, 3.2), (-2.6, 2.6))
    # (a) top view, force method
    ax = axs[0]
    rect(ax, -3.0, -1.0, 1.1, 2.0, fc=NORTH)
    rect(ax, 1.9, -1.0, 1.1, 2.0, fc=SOUTH)
    txt(ax, -2.45, 0, "N", 14, color=PAPER)
    txt(ax, 2.45, 0, "S", 14, color=PAPER)
    for y in (-0.6, 0.0, 0.6):
        arrow(ax, (-1.85, y), (1.85, y), color=FIELD, lw=1.1, scale=9, alpha=0.7)
    line(ax, [(-1.0, 0), (1.0, 0)], lw=4)
    ax.plot([0], [0], "+", color=INK, ms=9)
    arrow(ax, (-1.0, 0), (-1.0, -1.25), color=RED, lw=2.4, scale=14)
    arrow(ax, (1.0, 0), (1.0, 1.25), color=RED, lw=2.4, scale=14)
    txt(ax, -1.3, -1.0, r"$F_1$", 11, color=RED)
    txt(ax, 1.3, 1.0, r"$F_2$", 11, color=RED)
    ax.add_patch(FancyArrowPatch((0.6, 0.55), (-0.6, 0.55), connectionstyle="arc3,rad=0.5", arrowstyle="-|>", mutation_scale=14, lw=1.8, color=GREEN))
    txt(ax, 0, 1.95, "вид сверху: рамка вдоль поля,\nсила к нам у левой стороны, от нас у правой", 10)
    txt(ax, 0, -2.2, "поворот против часовой стрелки", 11, color=GREEN)
    # (b) frame as a magnet
    ax = axs[1]
    rect(ax, -3.0, -1.0, 1.1, 2.0, fc=NORTH)
    rect(ax, 1.9, -1.0, 1.1, 2.0, fc=SOUTH)
    txt(ax, -2.45, 0, "N", 14, color=PAPER)
    txt(ax, 2.45, 0, "S", 14, color=PAPER)
    # frame-magnet: initially N to the viewer (down in the top view), finally N to the right
    rect(ax, -0.25, -1.0, 0.5, 1.0, fc=NORTH, ec=INK, lw=1.4, alpha=0.35)
    rect(ax, -0.25, 0.0, 0.5, 1.0, fc=SOUTH, ec=INK, lw=1.4, alpha=0.35)
    txt(ax, 0, -0.5, "N", 12)
    txt(ax, 0, 0.5, "S", 12)
    ax.add_patch(FancyArrowPatch((0.3, -1.2), (1.2, -0.1), connectionstyle="arc3,rad=0.35", arrowstyle="-|>", mutation_scale=14, lw=1.8, color=GREEN))
    txt(ax, 0, 1.95, "вид сверху: ток идёт против часовой стрелки,\nсеверный полюс рамки обращён к нам", 10)
    txt(ax, 0, -2.2, "N рамки поворачивается к S магнита", 11, color=GREEN)
    save(f, "motor-task-frame")


@fig
def motor_task_robinson():
    f, ax = blank(8.6, 4.4, (-4.6, 4.6), (-2.6, 2.4))
    # water line
    ax.plot([-4.4, 4.4], [0.5, 0.5], color=BLUE, lw=1.2, ls=(0, (6, 3)))
    ax.text(-4.4, 0.25, "морская вода", color=BLUE, fontsize=10)
    # bar with turns
    rect(ax, -2.2, 0.5, 4.4, 0.6, fc=tint(COPPER, 0.5), ec=INK, lw=1.4)
    xs = np.linspace(-1.9, 1.9, 9)
    for x in xs:
        ax.plot([x + 0.12, x - 0.12], [0.45, 1.2], color=INK, lw=1.8, zorder=4)
        arrow(ax, (x + 0.04, 0.72), (x - 0.04, 0.92), color=RED, lw=1.4, scale=7, zorder=6)
    # plates hang into the water
    # The current runs from Cu to Zn through the turns: it enters at the lower end of the right turn and leaves at the upper end
    # of the left turn (-2.02; 1.2), so the Zn lead goes round the bar on the left and over its top
    line(ax, [(-2.0, -0.3), (-2.0, 0.2), (-2.6, 0.2), (-2.6, 1.35), (-2.02, 1.35), (-2.02, 1.2)])
    rect(ax, -2.4, -1.3, 0.8, 1.0, fc=IRON, ec=INK, lw=1.4)
    txt(ax, -2.0, -0.8, "Zn", 12)
    line(ax, [(2.0, 0.5), (2.0, -0.3)])
    rect(ax, 1.6, -1.3, 0.8, 1.0, fc=COPPER, ec=INK, lw=1.4)
    txt(ax, 2.0, -0.8, "Cu", 12)
    txt(ax, 2.0, -1.65, "+", 13, color=RED)
    txt(ax, -2.0, -1.65, "−", 13, color=BLUE)
    # pole markers and field
    pole_label(ax, -3.1, 0.8, "N", NORTH)
    pole_label(ax, 3.1, 0.8, "S", SOUTH)
    arrow(ax, (0.8, 1.7), (-0.8, 1.7), color=FIELD, lw=1.8, scale=13)
    txt(ax, 0, 2.05, "поле внутри катушки", 10, color=FIELD)
    txt(ax, 0, -2.3, "ток идёт от Cu к Zn через витки; северный конец определяет правило правой руки\nна рисунке показана одна из двух возможных намоток", 9.5, color=INK)
    save(f, "motor-task-robinson")


@fig
def motor_task_scout():
    f, ax = blank(10.6, 4.8, (-0.5, 10.6), (-2.6, 2.6))
    # forests
    for x0 in (0.0, 9.2):
        for dx in (0.0, 0.5, 1.0):
            ax.add_patch(Circle((x0 + dx, 1.5), 0.45, fc=tint(GREEN, 0.7), ec=INK, lw=1.1))
            line(ax, [(x0 + dx, 1.05), (x0 + dx, 0.5)], lw=1.5)
    txt(ax, 0.5, 2.3, "лес", 11)
    txt(ax, 9.7, 2.3, "лес", 11)
    # two wires
    line(ax, [(1.7, 1.0), (8.7, 1.0)], lw=2.6)
    line(ax, [(1.7, 0.1), (8.7, 0.1)], lw=2.6)
    arrow(ax, (4.4, 1.0), (5.6, 1.0), color=RED, lw=2.4, scale=14)
    arrow(ax, (5.6, 0.1), (4.4, 0.1), color=RED, lw=2.4, scale=14)
    txt(ax, 5.0, 1.35, "ток вправо", 10, color=RED)
    txt(ax, 5.0, -0.25, "ток влево", 10, color=RED)
    # compass under the lower wire: the north end of the needle points to the viewer
    circ(ax, 3.3, -0.85, 0.4, fc=PAPER)
    dot_out(ax, 3.3, -0.85, r=0.16, color=BLUE)
    txt(ax, 3.3, -1.55, "компас: N-конец стрелки\nсмотрит на нас", 10)
    # voltmeter
    # the voltmeter sits between the wires and joins both with short leads, so no lead crosses a wire
    circ(ax, 7.0, 0.55, 0.28, fc=PAPER)
    txt(ax, 7.0, 0.55, "V", 11)
    line(ax, [(7.0, 0.1), (7.0, 0.27)])
    line(ax, [(7.0, 0.83), (7.0, 1.0)])
    node(ax, 7.0, 0.1)
    node(ax, 7.0, 1.0)
    txt(ax, 7.0, -0.75, "магнитоэлектрический вольтметр\nпоказывает полярность", 10)
    save(f, "motor-task-scout")


@fig
def motor_unipolar():
    f, ax = blank(7.4, 6.4, (-3.4, 3.6), (-3.4, 3.4))
    # battery cylinder
    rect(ax, -0.6, 0.4, 1.2, 2.4, fc=tint(BLUE, 0.7), ec=INK, lw=1.6)
    rect(ax, -0.25, 2.8, 0.5, 0.18, fc=IRON, ec=INK, lw=1.3)
    txt(ax, 0, 3.25, "+", 14)
    txt(ax, 0, 0.1, "−", 14)
    arrow(ax, (0, 0.7), (0, 2.5), color=INK, lw=1.4, scale=11)
    # screw tip touching the minus and a disc magnet on the head
    poly(ax, [(-0.2, -0.5), (0.2, -0.5), (0.0, 0.4)], fc=METAL, ec=INK, lw=1.3)
    rect(ax, -1.7, -1.3, 3.4, 0.8, fc=SOUTH, ec=INK, lw=1.4)
    rect(ax, -1.7, -1.7, 3.4, 0.4, fc=NORTH, ec=INK, lw=1.4)
    txt(ax, 0, -0.9, "S", 13, color=PAPER)
    txt(ax, 0, -1.5, "N", 11, color=PAPER)
    # wire from the plus to the side of the magnet
    line(ax, [(0, 2.98), (0, 3.15), (-2.6, 3.15), (-2.6, -0.9), (-1.7, -0.9)], lw=1.8)
    # radial current in the magnet, force on a piece of it
    arrow(ax, (-1.55, -0.75), (-0.4, -0.75), color=PAPER, lw=2.2, scale=13, zorder=9)
    txt(ax, -1.0, -1.0, "I", 11, color=PAPER, zorder=9)
    cross_in(ax, -1.0, -0.9 - 0.45, r=0.15)
    txt(ax, -2.0, -2.15, r"$\vec F_А$ на этот участок: от нас", 10, color=RED)
    txt(ax, 2.7, 0.9, "вращение по часовой\nстрелке, вид сверху", 10, color=GREEN, ha="center")
    txt(ax, 0, -2.6, "южный полюс сверху, северный снизу\n(проверено магнитной стрелкой)", 10)
    save(f, "motor-unipolar")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
