"""Graphs and schemes for the note "Электромагниты" (section f12, lessons 173, 174, 176).

Run: python3 electromagnet.py [name ...]   (matplotlib only)
PNG files go to content/12. Магнитные явления/00. Вложения/ (prefix electromagnet-)
Curves that are not from the lectures carry the mark "не из лекции" on the picture itself.
"""
import sys

from magnet_common import *  # noqa: F403
from theme import num

FIGS = {}


def fig(fn):
    FIGS[fn.__name__.replace("_", "-")] = fn
    return fn


def button(ax, x, y, color=INK):
    """Push button, normally open, wires from x-0.7 to x+0.7."""
    line(ax, [(x - 0.7, y), (x - 0.3, y)], color=color)
    line(ax, [(x + 0.3, y), (x + 0.7, y)], color=color)
    ax.plot([x - 0.3, x + 0.3], [y, y], "o", color=color, ms=4)
    line(ax, [(x - 0.4, y + 0.22), (x + 0.4, y + 0.22)], color=color)
    line(ax, [(x, y + 0.22), (x, y + 0.55)], color=color)
    line(ax, [(x - 0.2, y + 0.55), (x + 0.2, y + 0.55)], color=color)


# ------------------------------------------------------------------ core and turns


@fig
def electromagnet_coil_nail():
    f, axs = blank_multi(1, 2, 10.6, 5.6, (-3.4, 3.4), (-1.6, 5.2))
    for k, ax in enumerate(axs):
        y0, y1 = 0.6, 2.9
        if k == 1:
            # one wide core instead of the nail: no second outline inside it
            rect(ax, -0.55, 0.15, 1.1, 3.35, fc=IRON, ec=INK, lw=1.4, zorder=0.5)
        else:
            rect(ax, -0.17, y0 - 0.5, 0.34, (y1 - y0) + 1.0, fc=IRON, ec=INK, lw=1.4, zorder=1)
        coil_vertical(ax, 0, y0, y1, w=1.0, n=7, core=False, wind=-1)
        for yi in np.linspace(y0, y1, 7):
            arrow(ax, (-0.2, yi + 0.06), (0.2, yi - 0.03), color=RED, lw=1.5, scale=9, zorder=5)
        battery(ax, -2.6, 1.75, horizontal=False, size=0.5)
        # the leads end at the outer ends of the winding, outside the core
        xw = 0.45 if k == 0 else 0.62
        line(ax, [(-2.6, 2.25), (-2.6, 4.0), (-xw, 4.0), (-xw, y1 + 0.02)])
        line(ax, [(-2.6, 1.25), (-2.6, 0.0), (xw, 0.0), (xw, y0 - 0.02)])
        top = 3.5 if k == 0 else 3.62
        bot = 0.1  # above the lower lead (y=0)
        for sp in (1.5, 2.3):
            field_loop_v(ax, 0.05, top, bot, sp, side=1, lw=1.4 + 0.9 * k)
        arrow(ax, (0.0, y0 + 0.3), (0.0, y1 - 0.3), color=FIELD, lw=2.0 + k, scale=13, zorder=6)
        pole_label(ax, 0, 4.0, "N", NORTH)
        pole_label(ax, 0, -0.55, "S", SOUTH)
    axs[0].set_title("а) катушка с гвоздём", fontsize=12)
    axs[1].set_title("б) катушка с железным сердечником", fontsize=12)
    # the notes stand above the field loops, which reach x = 2.35 at mid-height
    txt(axs[0], 1.9, 4.3, "гвоздь сам стал магнитом,\nполя складываются", 9.5)
    txt(axs[1], 1.9, 4.3, "сердечник намагничен:\nполе резко усилилось", 9.5)
    save(f, "electromagnet-coil-nail")


def _force_curve(n_turns, i):
    return np.tanh(n_turns * i / 300.0) ** 2 * 10


@fig
def electromagnet_force_current():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    i = np.linspace(0, 3, 300)
    for n, col in ((100, BLUE), (200, GREEN), (400, RED)):
        ax.plot(i, _force_curve(n, i), color=col, lw=2.4, label=f"$N={n}$ витков")
    ax.set_xlabel("сила тока $I$, А")
    ax.set_ylabel("подъёмная сила, отн. ед.")
    ax.set_title("Сила электромагнита и ток")
    ax.legend(frameon=False, loc="lower right")
    ax.text(0.05, 10.2, "качественно, не из лекции", ha="left", color=GREY, fontsize=9)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 10.8)
    grid(ax)
    save(f, "electromagnet-force-current")


@fig
def electromagnet_force_turns():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    n = np.linspace(0, 500, 300)
    for i, col in ((0.5, BLUE), (1.0, GREEN), (2.0, RED)):
        ax.plot(n, _force_curve(n, i), color=col, lw=2.4, label="$I=" + num(i, "", math=True) + "$ А")
    ax.set_xlabel("число витков $N$")
    ax.set_ylabel("подъёмная сила, отн. ед.")
    ax.set_title("Сила электромагнита и витки")
    ax.legend(frameon=False, loc="lower right")
    ax.text(5, 10.2, "качественно, не из лекции", ha="left", color=GREY, fontsize=9)
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 10.8)
    grid(ax)
    save(f, "electromagnet-force-turns")


@fig
def electromagnet_core_effect():
    f, ax = plt.subplots(figsize=(6.6, 4.6))
    i = np.linspace(0, 3, 300)
    ax.plot(i, _force_curve(200, i), color=RED, lw=2.6, label="с железным сердечником")
    ax.plot(i, 0.02 * (200 * i / 100.0) ** 2, color=BLUE, lw=2.6, label="без сердечника")
    ax.set_xlabel("сила тока $I$, А")
    ax.set_ylabel("подъёмная сила, отн. ед.")
    ax.set_title("Действие сердечника")
    ax.legend(frameon=False, loc="lower right")
    ax.text(0.05, 10.2, "качественно, не из лекции", ha="left", color=GREY, fontsize=9)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 10.8)
    grid(ax)
    save(f, "electromagnet-core-effect")


# ------------------------------------------------------------------ armature and two coils


@fig
def electromagnet_armature():
    f, axs = blank_multi(1, 2, 10.6, 5.0, (-3.0, 3.4), (-2.1, 3.9))
    ax = axs[0]
    rect(ax, -0.25, 0.4, 0.5, 2.6, fc=IRON)
    coil_vertical(ax, 0, 0.7, 2.7, w=0.6, n=6, core=False)
    pole_label(ax, 0, 3.4, "N", NORTH)
    pole_label(ax, 0.75, 0.2, "S", SOUTH, 11)
    rect(ax, -0.25, -0.05, 0.5, 0.45, fc=IRON, ec=IRON, lw=0)
    rect(ax, -0.35, -0.5, 0.7, 0.42, fc=IRON)
    txt(ax, 0.95, -0.3, "якорь", 10, ha="left")
    line(ax, [(0, -0.5), (0, -1.0)])
    rect(ax, -0.35, -1.6, 0.7, 0.6, fc=METAL)
    txt(ax, 0, -1.3, "груз", 10)
    ax.set_title("а) якорь у одного полюса", fontsize=12)
    txt(ax, 1.4, 1.5, "работает\nодин полюс", 10, ha="left")
    ax = axs[1]
    rect(ax, -1.5, 0.0, 0.5, 3.0, fc=IRON)
    rect(ax, 1.0, 0.0, 0.5, 3.0, fc=IRON)
    rect(ax, -1.5, 2.6, 3.0, 0.4, fc=IRON)
    coil_vertical(ax, -1.25, 0.5, 2.3, w=0.7, n=5, core=False, wind=1)
    coil_vertical(ax, 1.25, 0.5, 2.3, w=0.7, n=5, core=False, wind=1)
    rect(ax, -1.6, -0.5, 3.2, 0.42, fc=IRON)
    pole_label(ax, -1.9, 0.15, "S", SOUTH, 11)
    pole_label(ax, 1.9, 0.15, "N", NORTH, 11)
    txt(ax, 1.75, -0.29, "якорь", 10, ha="left")  # right of the armature, off the dashed field line
    line(ax, [(0, -0.5), (0, -1.0)])
    rect(ax, -0.35, -1.6, 0.7, 0.6, fc=METAL)
    txt(ax, 0, -1.3, "груз", 10)
    pts = [(-1.25, -0.29), (-1.25, 2.8), (1.25, 2.8), (1.25, -0.29), (-1.25, -0.29)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=FIELD, lw=1.6, ls="--", zorder=4)
    arrow(ax, (0.2, 2.8), (0.6, 2.8), color=FIELD, lw=1.6, scale=12, zorder=6)
    arrow(ax, (1.25, 1.2), (1.25, 0.8), color=FIELD, lw=1.6, scale=12, zorder=6)
    arrow(ax, (-0.8, -0.29), (-1.2, -0.29), color=FIELD, lw=1.6, scale=12, zorder=6)
    arrow(ax, (-1.25, 1.4), (-1.25, 1.8), color=FIELD, lw=1.6, scale=12, zorder=6)
    txt(ax, 0, 1.5, "замкнутая\nмагнитная\nцепь", 10, color=FIELD)
    ax.set_title("б) якорь замыкает оба полюса", fontsize=12)
    save(f, "electromagnet-armature")


@fig
def electromagnet_two_coils():
    f, axs = blank_multi(1, 2, 10.6, 4.9, (-3.4, 3.4), (-1.7, 3.9))
    for k, ax in enumerate(axs):
        rect(ax, -1.7, 0.0, 0.5, 3.0, fc=IRON)
        rect(ax, 1.2, 0.0, 0.5, 3.0, fc=IRON)
        rect(ax, -1.7, 2.6, 3.4, 0.4, fc=IRON)
        rect(ax, -1.75, -0.45, 3.5, 0.4, fc=IRON)
        coil_vertical(ax, -1.45, 0.4, 2.3, w=0.75, n=5, core=False)
        coil_vertical(ax, 1.45, 0.4, 2.3, w=0.75, n=5, core=False)
        d = -1 if k == 0 else 1
        for yi in np.linspace(0.4, 2.3, 5):
            arrow(ax, (-1.68, yi - 0.03), (-1.22, yi + 0.06), color=RED, lw=1.4, scale=8, zorder=5)
            arrow(ax, (1.45 - d * 0.23, yi - 0.03 * d), (1.45 + d * 0.23, yi + 0.06 * d), color=RED, lw=1.4, scale=8, zorder=5)
        arrow(ax, (-1.45, 1.4), (-1.45, 1.9), color=FIELD, lw=2.2, scale=13, zorder=6)
        if k == 0:
            arrow(ax, (1.45, 1.9), (1.45, 1.4), color=FIELD, lw=2.2, scale=13, zorder=6)
            txt(ax, 0, 1.4, "поля\nскладываются", 10, color=FIELD)
            ax.set_title("согласное включение: сильный магнит", fontsize=12, color=GREEN)
            pole_label(ax, -1.45, -0.95, "S", SOUTH, 11)
            pole_label(ax, 1.45, -0.95, "N", NORTH, 11)
        else:
            arrow(ax, (1.45, 1.4), (1.45, 1.9), color=FIELD, lw=2.2, scale=13, zorder=6)
            txt(ax, 0, 1.4, "поля\nвычитаются", 10, color=FIELD)
            ax.set_title("встречное включение: слабый магнит", fontsize=12, color=RED)
    save(f, "electromagnet-two-coils")


@fig
def electromagnet_winding_poles():
    f, axs = blank_multi(1, 2, 10.4, 3.4, (-2.7, 2.7), (-1.7, 1.9))
    for k, ax in enumerate(axs):
        w = +1 if k == 0 else -1
        coil_horizontal(ax, -1.5, 1.5, 0.3, h=0.9, n=7, core=True, wind=w)
        for xi in np.linspace(-1.5, 1.5, 7):
            arrow(ax, (xi - 0.06 * w, 0.3 - 0.25 * w), (xi + 0.06 * w, 0.3 + 0.25 * w), color=RED, lw=1.4, scale=8, zorder=5)
        # The leads start at the ends of the winding: the visible turns carry the current from the + lead to the - lead.
        # With rising turns it enters at the bottom of the first turn and leaves at the top of the last one; with falling turns the other way round.
        yb, yt = 0.3 - 0.9 * 0.62, 0.3 + 0.9 * 0.62
        xa, xb = -1.5 - 0.11 * w, 1.5 - 0.11 * w  # lower ends of the first and the last turn
        xa_top, xb_top = -1.5 + 0.11 * w, 1.5 + 0.11 * w  # upper ends
        if w > 0:
            line(ax, [(xa, yb), (xa, -0.55), (-1.95, -0.55), (-1.95, -1.0)])
            line(ax, [(xb_top, yt), (1.95, yt), (1.95, -1.0)])
        else:
            line(ax, [(xa_top, yt), (-1.95, yt), (-1.95, -1.0)])
            line(ax, [(xb, yb), (xb, -0.55), (1.95, -0.55), (1.95, -1.0)])
        terminal(ax, -1.95, -1.0)
        terminal(ax, 1.95, -1.0)
        txt(ax, -1.95, -1.4, "+", 12)
        txt(ax, 1.95, -1.4, "−", 12)
        if k == 0:
            pole_label(ax, -2.35, 0.3, "N", NORTH)
            pole_label(ax, 2.35, 0.3, "S", SOUTH)
            ax.set_title("витки идут вверх: N у плюса", fontsize=11)
        else:
            pole_label(ax, -2.35, 0.3, "S", SOUTH)
            pole_label(ax, 2.35, 0.3, "N", NORTH)
            ax.set_title("витки идут вниз: N у минуса", fontsize=11)
    save(f, "electromagnet-winding-poles")


@fig
def electromagnet_series_parallel():
    """Task: two windings on a U core, series and parallel connection, N on the left, S on the right."""
    f, axs = blank_multi(1, 2, 11.4, 5.4, (-3.4, 3.4), (-2.7, 3.9))
    for k, ax in enumerate(axs):
        rect(ax, -1.5, 0.0, 0.42, 2.9, fc=IRON)
        rect(ax, 1.08, 0.0, 0.42, 2.9, fc=IRON)
        rect(ax, -1.5, 2.5, 3.0, 0.4, fc=IRON)
        coil_vertical(ax, -1.29, 0.35, 2.1, w=0.7, n=5, core=False)
        coil_vertical(ax, 1.29, 0.35, 2.1, w=0.7, n=5, core=False, wind=1 if k == 0 else -1)
        pole_label(ax, -1.29, -0.35, "N", NORTH, 11)
        pole_label(ax, 1.29, -0.35, "S", SOUTH, 11)
        for yi in np.linspace(0.35, 2.1, 5):
            # left winding: current goes down along the axis, visible turns run to the left (field down, N below)
            arrow(ax, (-1.09, yi + 0.05), (-1.49, yi - 0.05), color=RED, lw=1.3, scale=8, zorder=5)
            if k == 0:
                arrow(ax, (1.09, yi - 0.05), (1.49, yi + 0.05), color=RED, lw=1.3, scale=8, zorder=5)
            else:
                arrow(ax, (1.09, yi + 0.05), (1.49, yi - 0.05), color=RED, lw=1.3, scale=8, zorder=5)
        battery(ax, 0, -1.9, horizontal=True, size=0.55)
        # The visible turns of the left winding rise to the right and carry the current to the left, so the current
        # enters at the right end of its top turn (-0.86; 2.2) and leaves at the left end of its bottom turn (-1.72; 0.25).
        # Series: the right winding rises too, the current enters at the left end of its bottom turn (0.86; 0.25)
        # and leaves at the right end of its top turn (1.72; 2.2).
        # Parallel: the right winding falls to the right, the current enters at the left end of its top turn (0.86; 2.2)
        # and leaves at the right end of its bottom turn (1.72; 0.25).
        if k == 0:
            # + -> top of the left winding -> its bottom -> bottom of the right winding -> its top -> minus
            line(ax, [(-0.55, -1.9), (-2.4, -1.9), (-2.4, 2.35), (-0.86, 2.35), (-0.86, 2.2)])
            line(ax, [(-1.72, 0.25), (-1.72, -0.9), (0.86, -0.9), (0.86, 0.25)])
            line(ax, [(1.72, 2.2), (2.4, 2.2), (2.4, -1.9), (0.55, -1.9)])
            ax.set_title("обмотки последовательно", fontsize=12)
        else:
            # + bus over both top turns, - bus under both bottom turns
            line(ax, [(-0.55, -1.9), (-2.4, -1.9), (-2.4, 2.35), (0.86, 2.35), (0.86, 2.2)])
            line(ax, [(-0.86, 2.35), (-0.86, 2.2)])
            node(ax, -0.86, 2.35)
            line(ax, [(-1.72, 0.25), (-1.72, -0.9), (1.72, -0.9), (1.72, 0.25)])
            line(ax, [(1.72, -0.9), (1.72, -1.9), (0.55, -1.9)])
            node(ax, 1.72, -0.9)
            ax.set_title("обмотки параллельно", fontsize=12)
    save(f, "electromagnet-series-parallel")


# ------------------------------------------------------------------ relay


@fig
def electromagnet_relay_mechanism():
    f, ax = blank(8.4, 6.0, (-2.2, 8.6), (-1.4, 5.4))
    line(ax, [(-0.6, -0.2), (7.9, -0.2)], color=GREY, lw=2.2)
    # core, coil and yoke
    rect(ax, 1.0, 0.0, 0.5, 2.4, fc=IRON)
    coil_vertical(ax, 1.25, 0.3, 2.0, w=0.95, n=5, core=False)
    rect(ax, 3.0, 0.0, 0.42, 2.7, fc=IRON, zorder=3)
    rect(ax, 1.0, 0.0, 2.42, 0.32, fc=IRON, zorder=3)
    # armature: a lever that turns on the yoke edge, the left arm is above the core
    rect(ax, 0.6, 2.55, 4.8, 0.3, fc=IRON)
    ax.plot([3.21], [2.7], "o", color=INK, ms=7, zorder=8)
    # insulating pad on the right arm pushes the moving contact up
    rect(ax, 4.7, 2.85, 0.3, 0.3, fc=tint(ORANGE, 0.5), ec=INK, lw=1.2)
    line(ax, [(6.9, 3.35), (4.85, 3.35)], lw=2.0)
    ax.plot([4.85], [3.35], "o", color=INK, ms=6, zorder=8)
    line(ax, [(4.85, 3.62), (4.85, 3.95), (7.3, 3.95)], lw=2.0)
    ax.plot([4.85], [3.62], "o", color=INK, ms=6, zorder=8)
    line(ax, [(6.9, 3.35), (6.9, -0.2)])
    line(ax, [(7.3, 3.95), (7.3, -0.2)])
    terminal(ax, 6.9, -0.2)
    terminal(ax, 7.3, -0.2)
    txt(ax, 7.1, -0.75, "клеммы\nсиловой цепи", 10)
    # coil terminals
    # both leads start at the ends of the winding; the second one goes over the coil and down the left side, clear of the yoke
    line(ax, [(0.66, 0.21), (0.3, 0.21), (0.3, -0.2)])
    line(ax, [(1.84, 2.09), (1.84, 2.25), (-0.1, 2.25), (-0.1, -0.2)])
    terminal(ax, 0.3, -0.2)
    terminal(ax, -0.1, -0.2)
    txt(ax, 0.1, -0.75, "выводы обмотки", 10)
    # labels
    txt(ax, -0.1, 3.3, "якорь", 11, ha="center")
    arrow(ax, (0.9, 3.15), (0.9, 2.95), color=RED, lw=1.6, scale=11)
    txt(ax, 3.2, 3.35, "шарнир", 10, ha="center")
    txt(ax, -0.25, 1.0, "катушка", 10, ha="right")
    txt(ax, -0.25, 1.7, "сердечник", 10, ha="right")
    txt(ax, 3.6, 1.2, "магнитопровод", 10, ha="left")
    txt(ax, 5.35, 2.35, "изолятор", 10, ha="left")
    txt(ax, 3.6, 5.0, "тока нет: между контактами зазор", 10.5, ha="left")
    txt(ax, 3.6, 4.55, "ток есть: якорь притянут, контакты замкнуты", 10.5, ha="left")
    save(f, "electromagnet-relay-mechanism")


@fig
def electromagnet_relay_gain():
    f, ax = plt.subplots(figsize=(5.8, 4.0))
    ax.bar(["обмотка реле\n(управление)", "лампа\n(силовая цепь)"], [0.05, 2.0], color=[BLUE, RED], width=0.55)
    ax.text(0, 0.12, "50 мА", ha="center", fontsize=12)
    ax.text(1, 2.07, "2 А", ha="center", fontsize=12)
    ax.text(0.5, 1.2, "в 40 раз", ha="center", color=ORANGE, fontsize=14)
    ax.set_ylabel("сила тока, А")
    ax.set_title("Реле усиливает ток")
    ax.set_ylim(0, 2.4)
    grid(ax)
    save(f, "electromagnet-relay-gain")


@fig
def electromagnet_relay_symbols():
    f, ax = blank(8.8, 3.6, (-1.0, 11.2), (-2.4, 2.4))
    rect(ax, 0.2, -0.5, 1.9, 1.0, fc=PAPER)
    txt(ax, 1.15, 0.0, "R", 15)
    line(ax, [(0.2, 0.0), (-0.4, 0.0)])
    line(ax, [(2.1, 0.0), (2.7, 0.0)])
    txt(ax, 1.15, 1.2, "обмотка реле", 10.5)
    # normally open
    line(ax, [(4.2, 0.0), (4.8, 0.0)], lw=2)
    line(ax, [(5.8, 0.0), (6.4, 0.0)], lw=2)
    line(ax, [(4.8, 0.0), (5.75, 0.5)], lw=2)
    node(ax, 4.8, 0.0)
    node(ax, 5.8, 0.0)
    txt(ax, 5.3, 1.2, "НР", 13)
    txt(ax, 5.3, -0.6, "нормально\nразомкнутый", 10)
    # normally closed
    line(ax, [(7.6, 0.0), (8.2, 0.0)], lw=2)
    line(ax, [(9.2, 0.0), (9.8, 0.0)], lw=2)
    line(ax, [(8.2, 0.0), (9.2, 0.0)], lw=2)
    ax.plot([8.7, 8.7], [0.0, 0.5], color=INK, lw=2)
    node(ax, 8.2, 0.0)
    node(ax, 9.2, 0.0)
    txt(ax, 8.7, 1.2, "НЗ", 13)
    txt(ax, 8.7, -0.6, "нормально\nзамкнутый", 10)
    save(f, "electromagnet-relay-symbols")


@fig
def electromagnet_relay_circuit():
    """Task: button pressed - lamp lights, button released - motor runs."""
    f, ax = blank(11.6, 6.6, (-0.9, 10.7), (-2.9, 4.4))
    # control circuit
    battery(ax, 0.6, 1.4, horizontal=False, size=0.6)
    line(ax, [(0.6, 2.0), (0.6, 3.0), (1.0, 3.0)], color=BLUE)
    button(ax, 1.7, 3.0, color=BLUE)
    line(ax, [(2.4, 3.0), (3.4, 3.0), (3.4, 2.4)], color=BLUE)
    rect(ax, 3.0, 1.0, 0.8, 1.4, fc=PAPER, ec=BLUE)
    coil_vertical(ax, 3.4, 1.15, 2.25, w=0.7, n=4, core=False, color=BLUE)
    line(ax, [(3.4, 1.0), (3.4, 0.0), (0.6, 0.0), (0.6, 0.8)], color=BLUE)
    txt(ax, 1.7, 3.9, "кнопка", 10)
    txt(ax, 3.4, -0.4, "обмотка реле", 10)
    # dashed mechanical link
    # the link ends at the middle of the blade, clear of the mains wire
    ax.plot([3.85, 6.1], [1.7, 2.05], color=GREY, lw=1.6, ls="--", zorder=9)
    txt(ax, 4.95, 2.3, "якорь", 9.5, color=GREY)
    # power circuit: common contact, blade, NC (up), NO (down)
    com = (5.6, 1.7)
    nc = (6.8, 2.6)
    no = (6.8, 0.8)
    node(ax, *com)
    node(ax, *nc)
    node(ax, *no)
    line(ax, [com, (nc[0] - 0.05, nc[1] - 0.12)], lw=2.2)
    txt(ax, 7.25, 2.95, "НЗ", 11)
    txt(ax, 7.25, 0.45, "НР", 11)
    # NC -> motor
    line(ax, [nc, (9.6, 2.6), (9.6, 2.05)])
    motor(ax, 9.6, 1.65)
    line(ax, [(9.6, 1.25), (9.6, -0.6)])
    # NO -> lamp
    line(ax, [no, (7.4, 0.8)])
    lamp(ax, 7.75, 0.8)
    line(ax, [(8.1, 0.8), (8.7, 0.8), (8.7, -0.6)])
    # joint and mains
    line(ax, [(8.7, -0.6), (9.6, -0.6)])
    node(ax, 8.7, -0.6)
    line(ax, [(8.7, -0.6), (8.7, -1.9)])
    terminal(ax, 8.7, -1.9)
    line(ax, [com, (com[0], -1.9)])
    terminal(ax, com[0], -1.9)
    txt(ax, 7.15, -1.9, "сеть 220 В", 11)
    txt(ax, 9.6, 0.65, "", 9)
    txt(ax, 10.25, 1.65, "мотор\n220 В", 9.5, ha="left")
    txt(ax, 7.75, 1.4, "лампа\n220 В", 9.5)
    # frames
    ax.plot([-0.7, 4.25, 4.25, -0.7, -0.7], [-0.9, -0.9, 4.2, 4.2, -0.9], color=BLUE, lw=1.3, ls=(0, (5, 4)))
    ax.plot([4.4, 10.5, 10.5, 4.4, 4.4], [-2.3, -2.3, 3.6, 3.6, -2.3], color=RED, lw=1.3, ls=(0, (5, 4)))
    txt(ax, 1.7, 4.4 - 0.05, "цепь управления", 12, color=BLUE)
    txt(ax, 7.5, 3.85, "силовая цепь", 12, color=RED)
    txt(ax, 4.9, -2.65, "кнопка отпущена: ток идёт через НЗ, мотор работает\nкнопка нажата: якорь притянут, ток идёт через НР, лампа горит", 10, ha="center", color=INK)
    save(f, "electromagnet-relay-circuit")


@fig
def electromagnet_buzzer_circuit():
    f, ax = blank(7.4, 4.6, (-1.2, 6.6), (-1.8, 3.6))
    battery(ax, 0.0, 1.0, horizontal=False, size=0.6)
    line(ax, [(0.0, 1.6), (0.0, 2.6), (1.2, 2.6)])
    rect(ax, 1.2, 2.1, 1.7, 1.0, fc=PAPER)
    txt(ax, 2.05, 2.6, "R", 15)
    line(ax, [(2.9, 2.6), (4.6, 2.6), (4.6, 2.0)])
    # NC contact
    node(ax, 4.6, 2.0)
    line(ax, [(4.6, 2.0), (4.6, 0.6)], lw=2.0)
    ax.plot([4.6, 4.95], [1.3, 1.3], color=INK, lw=2.0)  # the NC tick goes to one side, as in the legend
    line(ax, [(4.6, 1.3), (4.6, 1.3)])
    node(ax, 4.6, 0.6)
    line(ax, [(4.6, 0.6), (4.6, -0.6), (0.0, -0.6), (0.0, 0.4)])
    txt(ax, 5.0, 1.3, "НЗ", 12, ha="left")
    ax.plot([2.05, 4.55], [2.05, 1.3], color=GREY, lw=1.6, ls="--")
    txt(ax, 2.05, 3.4, "обмотка реле", 10.5)
    txt(ax, 2.6, -1.3, "зуммер: контакт размыкает обмотку, якорь отпускается, и всё повторяется", 10, ha="center")
    save(f, "electromagnet-buzzer-circuit")


# ------------------------------------------------------------------ bell


@fig
def electromagnet_bell_mechanism():
    f, axs = plt.subplots(1, 2, figsize=(11.2, 4.6), gridspec_kw={"width_ratios": [1.05, 1]})
    ax = axs[0]
    ax.set_xlim(-0.6, 7.6)
    ax.set_ylim(-1.7, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    # electromagnet: two windings on a U core (side view: a bar with coil)
    rect(ax, 0.2, 0.9, 2.6, 0.5, fc=IRON)
    coil_horizontal(ax, 0.55, 2.4, 1.15, h=1.0, n=5, core=False)
    txt(ax, 1.5, 2.15, "обмотка", 10)
    # armature: flexible plate hanging from a hinge, also a contact
    line(ax, [(3.5, 3.6), (3.5, -0.3)], color=INK, lw=3.4)
    txt(ax, 3.5, 4.2, "якорь-контакт", 10)
    # contact screw
    line(ax, [(4.4, 1.9), (3.62, 1.9)], color=ORANGE, lw=3.0)
    txt(ax, 5.15, 1.55, "винт контакта", 10)  # right of the armature, under the end of the lead
    # The hammer sits on the electromagnet side of the armature, so it moves towards the bell when the armature is attracted;
    # at rest there is a gap between the hammer and the bell
    line(ax, [(3.5, -0.1), (2.55, -0.1)], color=INK, lw=2.0)
    circ(ax, 2.35, -0.1, 0.2, fc=METAL)
    ax.add_patch(Wedge((1.2, -0.55), 0.85, 0, 180, fc=LIGHT, ec=INK, lw=1.6))
    txt(ax, 1.2, -0.95, "колокольчик", 10)
    txt(ax, 2.7, 0.2, "молоточек", 8.5)  # above the rod, between the bell and the armature
    arrow(ax, (3.95, 2.9), (3.6, 2.9), color=RED, lw=1.6, scale=11)
    txt(ax, 3.65, 3.25, "притягивается", 9.5, color=RED, ha="left")
    # circuit: source, winding, armature, contact screw; the leads start at the ends of the winding
    line(ax, [(0.45, 0.53), (-0.4, 0.53), (-0.4, -1.5), (0.9, -1.5)], lw=1.4)
    battery(ax, 1.4, -1.5, horizontal=True, size=0.5, label=False)
    line(ax, [(1.9, -1.5), (3.5, -1.5), (3.5, -0.3)], lw=1.4)
    line(ax, [(2.5, 1.77), (2.5, 3.85), (6.0, 3.85), (6.0, 1.9), (4.4, 1.9)], lw=1.4)
    ax.set_title("механизм звонка", fontsize=12)
    # timing
    ax = axs[1]
    t = np.linspace(0, 6, 600)
    period = 2.0
    ph = (t % period) / period
    closed = ph < 0.62
    cur = np.where(closed, 1.0, 0.0)
    pos = np.where(closed, ph / 0.62, 1 - (ph - 0.62) / 0.38)
    ax.plot(t, cur * 0.8 + 1.6, color=RED, lw=2.4)
    ax.plot(t, pos * 0.8, color=BLUE, lw=2.4)
    ax.text(6.05, 2.0, "ток\nв обмотке", color=RED, fontsize=10, va="center")
    ax.text(6.05, 0.4, "якорь\n(1 - у магнита)", color=BLUE, fontsize=10, va="center")
    ax.set_xlim(0, 7.6)
    ax.set_ylim(-0.3, 2.7)
    ax.set_xlabel("время")
    ax.set_yticks([])
    ax.set_title("самопрерывание тока", fontsize=12)
    ax.text(0.05, -0.15, "качественно, не из лекции", color=GREY, fontsize=9)
    grid(ax)
    save(f, "electromagnet-bell-mechanism")


# ------------------------------------------------------------------ separator, crane


@fig
def electromagnet_separator():
    f, ax = blank(7.2, 6.0, (-4.0, 4.6), (-3.2, 3.9))
    ax.add_patch(Circle((0, 0), 1.5, fc=LIGHT, ec=INK, lw=2.0))
    ax.add_patch(Wedge((0, 0), 1.4, 100, 260, width=0.55, fc=tint(ORANGE, 0.5), ec=INK, lw=1.4))
    txt(ax, -1.12, 0.0, "магнит", 9.5, rotation=90)  # in the middle of the orange band
    txt(ax, 0.55, 0.0, "барабан\n(алюминий)", 9.5)
    ax.add_patch(FancyArrowPatch((1.2, 1.5), (0.4, 1.9), connectionstyle="arc3,rad=0.4", arrowstyle="-|>", mutation_scale=13, lw=1.6, color=RED))
    txt(ax, 1.65, 2.15, "против часовой\nстрелки", 9.5, color=RED)
    # hopper
    poly(ax, [(-0.5, 3.6), (1.3, 3.6), (0.7, 2.5), (0.1, 2.5)], fc=LIGHT)
    txt(ax, 0.4, 3.05, "бункер", 10)
    # falling mixture
    rng = np.random.default_rng(3)
    ax.plot(rng.normal(0.4, 0.06, 6), np.linspace(2.4, 1.6, 6), "o", color=ORANGE, ms=4)
    # non-magnetic grains falling off to the left
    for x, y in ((-1.9, 0.9), (-2.1, 0.3), (-2.2, -0.5), (-2.05, -1.3), (-1.85, -2.0)):
        ax.plot([x], [y], "o", color=GREEN, ms=4)
    arrow(ax, (-1.55, 1.15), (-2.15, 0.5), color=GREEN, lw=1.4, scale=10)
    rect(ax, -3.9, -3.0, 1.9, 0.9, fc=PAPER)
    txt(ax, -2.95, -2.55, "зерно", 11, color=GREEN)
    # iron pieces stay on the drum and drop below the magnet
    for a in np.linspace(150, 250, 6):
        ax.plot([1.62 * np.cos(np.radians(a))], [1.62 * np.sin(np.radians(a))], "s", color=INK, ms=5)
    ax.plot([0.75, 0.85, 0.7], [-1.95, -2.15, -2.35], "s", color=INK, ms=5)  # above the label box (top at -2.5)
    arrow(ax, (0.2, -1.7), (0.75, -2.0), color=INK, lw=1.4, scale=10)
    rect(ax, 0.0, -3.1, 1.9, 0.6, fc=PAPER)
    txt(ax, 0.95, -2.8, "гайки, гвозди", 10)
    save(f, "electromagnet-separator")


# ------------------------------------------------------------------ telegraph and Morse


@fig
def electromagnet_telegraph():
    f, ax = blank(11.6, 6.4, (-1.0, 11.8), (-2.0, 5.6))
    # transmitting part
    battery(ax, 0.4, 0.4, horizontal=False, size=0.55)
    line(ax, [(0.4, 0.95), (0.4, 2.2), (0.9, 2.2)])
    line(ax, [(1.6, 2.2), (2.0, 2.2)])
    ax.plot([0.9, 1.6], [2.2, 2.55], color=INK, lw=2.0)
    node(ax, 0.9, 2.2)
    node(ax, 1.6, 2.2)
    txt(ax, 1.25, 3.0, "телеграфный ключ", 10)
    line(ax, [(0.4, -0.15), (0.4, -1.0), (2.0, -1.0)])
    ax.plot([2.0, 3.9], [2.2, 2.2], color=GREY, lw=1.6, ls=(0, (2, 3)))
    ax.plot([2.0, 3.9], [-1.0, -1.0], color=GREY, lw=1.6, ls=(0, (2, 3)))
    txt(ax, 2.95, 0.6, "очень\nдалеко", 10, color=GREY)
    txt(ax, 1.2, -1.6, "передающая часть", 11, color=BLUE)
    # receiving part: electromagnet at the far end of the two wires
    # the upper wire comes from the left into the end of the top turn, so that it crosses neither the lever nor the armature
    line(ax, [(3.9, 2.2), (3.6, 2.2), (3.6, 0.93), (4.17, 0.93)])
    line(ax, [(3.9, -1.0), (4.6, -1.0), (4.6, -0.02)])
    rect(ax, 4.2, -0.3, 0.8, 1.5, fc=PAPER)
    rect(ax, 4.45, -0.1, 0.3, 1.3, fc=IRON, ec=INK, lw=1.2)
    coil_vertical(ax, 4.6, 0.0, 1.0, w=0.7, n=4, core=False)
    # lever with an axis: iron plate over the electromagnet on the left, wheel on the right
    line(ax, [(4.0, 1.85), (9.0, 1.85)], lw=3.0)
    ax.plot([6.3], [1.85], "o", color=INK, ms=9, zorder=8)
    rect(ax, 4.2, 1.57, 0.8, 0.28, fc=IRON)  # the armature hangs right under the lever
    txt(ax, 5.1, 1.55, "якорь", 10, ha="left")
    ax.plot([4.1, 4.1], [1.85, 3.5], color=INK, lw=1.3, ls=(0, (1, 2)))
    txt(ax, 4.1, 3.75, "пружина", 10)
    txt(ax, 6.3, 2.35, "ось рычага", 10)
    circ(ax, 9.0, 1.8, 0.3, fc=tint(ORANGE, 0.5), zorder=7)
    txt(ax, 10.3, 1.8, "колёсико", 10, ha="left")
    # the ink level is above the lower edge of the wheel (1.5), so the wheel dips into the ink
    rect(ax, 8.3, 0.7, 1.4, 0.95, fc=LIGHT)
    rect(ax, 8.3, 0.7, 1.4, 0.9, fc=tint(INK, 0.3), ec=tint(INK, 0.3), lw=0)
    txt(ax, 9.0, 0.35, "краска", 10)
    # tape from the supply reel between the wheel and the roller to the take-up reel
    circ(ax, 7.4, 4.0, 0.65, fc=PAPER)
    circ(ax, 10.6, 4.0, 0.65, fc=PAPER)
    # the tape moves to the left (as on the Morse figure): the supply reel is on the right, the take-up reel on the left
    txt(ax, 7.4, 5.0, "приёмная\nкатушка", 9.5)
    txt(ax, 10.6, 5.0, "подающая\nкатушка", 9.5)
    circ(ax, 9.0, 3.0, 0.3, fc=LIGHT)
    txt(ax, 9.0, 3.65, "ролик", 10)
    line(ax, [(7.6, 3.4), (8.3, 2.65), (9.0, 2.62), (9.7, 2.65), (10.4, 3.4)], color=INK, lw=1.6)
    txt(ax, 7.4, -0.6, "приёмная часть", 11, color=RED)
    save(f, "electromagnet-telegraph")


MORSE = {"Л": ".-..", "И": "..", "Ц": "-.-.", "Е": ".", "Й": ".---"}


@fig
def electromagnet_morse_timing():
    f, axs = plt.subplots(2, 1, figsize=(10.4, 5.6), gridspec_kw={"height_ratios": [1.15, 1]})
    # (a) timing of the letter L: dot dash dot dot, standard unit lengths (not from the lecture)
    ax = axs[0]
    seq = [("d", 1), ("g", 1), ("D", 3), ("g", 1), ("d", 1), ("g", 1), ("d", 1)]
    t0 = 0.0
    xs, ys = [0.0], [0.0]
    marks = []
    for kind, ln in seq:
        on = 1 if kind in "dD" else 0
        xs += [t0, t0 + ln]
        ys += [on, on]
        marks.append((t0, ln, kind))
        t0 += ln
    xs.append(t0)
    ys.append(0)
    ax.step(xs, ys, where="post", color=RED, lw=0)
    for t, ln, kind in marks:
        if kind in "dD":
            ax.add_patch(Rectangle((t, 0.15), ln, 0.7, fc=RED, ec=INK, lw=1.2))
            ax.text(t + ln / 2, 1.0, "точка" if kind == "d" else "тире", ha="center", fontsize=10)
    ax.plot([0, t0], [0.15, 0.15], color=INK, lw=1)
    ax.set_xlim(-0.3, t0 + 0.3)
    ax.set_ylim(0, 1.35)
    ax.set_yticks([0.5])
    ax.set_yticklabels(["ключ\nнажат"])
    ax.set_xticks(range(0, int(t0) + 1))
    ax.set_xlabel("время, условные единицы (точка = 1, тире = 3, пауза внутри буквы = 1)")
    ax.set_title("Буква Л: точка, тире, точка, точка", fontsize=12)
    ax.text(t0 + 0.2, 1.28, "единицы не из лекции", ha="right", color=GREY, fontsize=9)
    grid(ax)
    # (b) tape with the word ЛИЦЕЙ
    ax = axs[1]
    ax.axis("off")
    ax.set_xlim(0, 40)
    ax.set_ylim(-0.4, 1.6)
    ax.add_patch(Rectangle((0, 0.0), 40, 1.0, fc=tint(WARM, 0.85), ec=INK, lw=1.2))
    x = 1.0
    for letter in "ЛИЦЕЙ":
        start = x
        for s in MORSE[letter]:
            if s == ".":
                ax.plot([x + 0.4], [0.5], "o", color=INK, ms=9)
                x += 1.5
            else:
                ax.add_patch(Rectangle((x, 0.38), 2.2, 0.24, fc=INK))
                x += 3.3
        ax.text((start + x - 1.1) / 2, -0.25, letter, ha="center", fontsize=13)
        x += 1.4
    ax.annotate("", xy=(1, 1.4), xytext=(6, 1.4), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6))
    ax.text(7.0, 1.4, "лента движется влево", va="center", fontsize=10, color=RED)
    f.subplots_adjust(hspace=0.6)
    save(f, "electromagnet-morse-timing")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        FIGS[n]()
