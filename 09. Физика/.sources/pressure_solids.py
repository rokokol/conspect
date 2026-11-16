"""Figures for the note "Давление твёрдых тел" (course Физика 7-9, lessons 42-44).

Run: python3 pressure_solids.py
PNG files go to content/06. Давление/00. Вложения/, prefix pressure-.
Colour code, the same in every picture: force red, area green, pressure blue.
Inputs marked "допущение" in a figure belong to the extra problems, not to the lecture.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = COURSE / "content" / "06. Давление" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
NOMEDIA = OUT / ".nomedia"
if not NOMEDIA.exists():
    NOMEDIA.touch()

from theme import ASH, BLUE, COPPER, GREEN, INK, METAL, MUTED, PAPER, PINK, RED, WARM, saver, tint

GRID = ASH
GREY = MUTED
C_F = RED  # force
C_S = GREEN  # area
C_P = BLUE  # pressure
C_ORANGE = WARM  # estimates that are not from the lecture
P_MID = tint(BLUE, 0.35)  # the second of three cases of pressure
P_LIGHT = tint(BLUE, 0.6)  # the third of three cases of pressure
SAND = tint(WARM, 0.6)
SAND_GRAIN = WARM
WOOD = tint(COPPER, 0.55)
BODY = tint(WARM, 0.6)
FOOT = tint(GREEN, 0.8)
SKIN = tint(PINK, 0.6)
PLATE = METAL  # grey slabs
PLATE_TOP = tint(INK, 0.7)
ALUMINIUM = tint(INK, 0.7)
COPPER_FILL = tint(COPPER, 0.55)
BOOK_BIG = tint(PINK, 0.6)
BOOK_SMALL = tint(BLUE, 0.7)
BAND_A = tint(BLUE, 0.85)
BAND_B = tint(BLUE, 0.7)

G = 10.0  # N/kg, the value used in the course


def num(x, nd=2):
    """Decimal comma, trailing zeros removed."""
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return s.replace(".", "{,}")


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=14, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, **kw))


def box(ax, x, y, w, h, d, face=BODY, dxy=(0.55, 0.38), lw=1.3, z=3):
    """Oblique box: front face w x h, depth d drawn along dxy."""
    dx, dy = d * dxy[0], d * dxy[1]
    ax.add_patch(Rectangle((x, y), w, h, fc=face, ec=INK, lw=lw, zorder=z))
    top = [(x, y + h), (x + w, y + h), (x + w + dx, y + h + dy), (x + dx, y + h + dy)]
    side = [(x + w, y), (x + w, y + h), (x + w + dx, y + h + dy), (x + w + dx, y + dy)]
    ax.add_patch(Polygon(top, fc=face, ec=INK, lw=lw, zorder=z))
    ax.add_patch(Polygon(side, fc=face, ec=INK, lw=lw, zorder=z))
    ax.add_patch(Polygon(top, fc=PAPER, alpha=0.35, ec="none", zorder=z + 0.1))
    ax.add_patch(Polygon(side, fc=INK, alpha=0.12, ec="none", zorder=z + 0.1))
    return dx, dy


# ---------------------------------------------------------------------------
# 1. Board with nails on sand
# ---------------------------------------------------------------------------
def nails_board():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.4))
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect("equal")
        ax.axis("off")
    surf = 2.6
    xs = [2.6, 4.2, 5.8, 7.4]
    rng = np.random.default_rng(3)
    for ax, title, depth in zip(axes, ["Шляпками вниз", "Остриями вниз"], [0.3, 1.9]):
        ax.add_patch(Rectangle((0.4, 0.4), 9.2, surf - 0.4, fc=SAND, ec=INK, lw=1.3))
        ax.scatter(rng.uniform(0.6, 9.4, 90), rng.uniform(0.55, surf - 0.15, 90), s=3, color=SAND_GRAIN, zorder=2)
        if title == "Шляпками вниз":
            by = surf - depth + 0.25  # board bottom edge, heads below it
            ax.add_patch(Rectangle((1.7, by), 6.6, 0.55, fc=WOOD, ec=INK, lw=1.3, zorder=4))
            for x in xs:
                ax.add_patch(Rectangle((x - 0.22, by - 0.25), 0.44, 0.25, fc=METAL, ec=INK, lw=0.8, zorder=5))
                ax.add_patch(Rectangle((x - 0.05, by + 0.55), 0.1, 0.6, fc=METAL, ec=INK, lw=0.8, zorder=5))
                ax.add_patch(Polygon([(x - 0.05, by + 1.15), (x + 0.05, by + 1.15), (x, by + 1.45)], fc=METAL, ec=INK, lw=0.8, zorder=5))
            arrow(ax, (5.0, 5.7), (5.0, 3.9), color=C_F, lw=2)
        else:
            by = surf - depth + 1.5
            ax.add_patch(Rectangle((1.7, by), 6.6, 0.55, fc=WOOD, ec=INK, lw=1.3, zorder=4))
            for x in xs:
                ax.add_patch(Rectangle((x - 0.05, by - 1.3), 0.1, 1.3, fc=METAL, ec=INK, lw=0.8, zorder=5))
                ax.add_patch(Polygon([(x - 0.05, by - 1.3), (x + 0.05, by - 1.3), (x, by - 1.6)], fc=METAL, ec=INK, lw=0.8, zorder=5))
                ax.add_patch(Rectangle((x - 0.22, by + 0.55), 0.44, 0.22, fc=METAL, ec=INK, lw=0.8, zorder=5))
            arrow(ax, (5.0, 5.7), (5.0, 4.4), color=C_F, lw=2)
        ax.plot([0.4, 9.6], [surf, surf], color=INK, lw=1.3, zorder=6)
        ax.set_title(title, fontsize=12, color=INK, pad=2)
        ax.text(5.25, 5.3, r"$F_\mathrm{т}$", color=C_F, fontsize=12, va="center")
        ax.text(5.0, 0.0, "проваливается неглубоко" if depth < 1 else "проваливается глубоко", fontsize=10, va="center", color=INK, ha="center", zorder=7)
    fig.text(0.5, 0.0, "Вес дощечки один и тот же, площадь опоры разная", ha="center", fontsize=10.5, color=INK)
    save(fig, "pressure-nails-board-sand.png")


# ---------------------------------------------------------------------------
# 2. Button: finger and wood
# ---------------------------------------------------------------------------
def button_forces():
    fig, ax = blank(9.6, 4.4, (0, 12), (0, 5.6))
    finger = [(0.3, 1.2), (0.9, 2.2), (1.4, 3.6), (2.2, 4.5), (3.4, 4.7), (4.0, 4.0), (3.5, 3.4), (3.3, 2.5), (3.6, 1.6), (3.3, 0.8), (2.0, 0.6), (0.9, 0.7)]
    ax.add_patch(Polygon(finger, closed=True, fc=SKIN, ec=INK, lw=1.4))
    ax.text(1.6, 0.25, "палец", ha="center", fontsize=11, color=INK)
    ax.add_patch(Rectangle((4.05, 1.0), 0.28, 3.4, fc=METAL, ec=INK, lw=1.3, zorder=4))
    ax.add_patch(Polygon([(4.33, 2.55), (6.1, 2.7), (4.33, 2.85)], fc=METAL, ec=INK, lw=1.3, zorder=4))
    ax.text(4.2, 0.55, "кнопка", ha="center", fontsize=11, color=INK)
    ax.add_patch(Rectangle((6.05, 0.9), 5.2, 3.6, fc=WOOD, ec=INK, lw=1.4))
    for yy in (1.5, 2.1, 3.2, 3.9):
        ax.plot([6.5, 10.9], [yy, yy + 0.05], color=COPPER, lw=0.9)
    ax.text(8.6, 0.45, "дощечка", ha="center", fontsize=11, color=INK)
    arrow(ax, (4.0, 2.7), (2.6, 2.7), color=C_F, lw=2.4)
    ax.text(3.15, 3.05, r"$\vec F_1$", color=C_F, fontsize=13)
    arrow(ax, (6.05, 2.78), (7.5, 2.78), color=C_F, lw=2.4)
    ax.text(6.8, 3.15, r"$\vec F_2$", color=C_F, fontsize=13)
    # S1 is the head's face on the finger's side
    ax.plot([4.0, 4.0], [1.0, 4.4], color=C_S, lw=2.6, zorder=5)
    ax.text(3.5, 4.2, r"$S_1$", color=C_S, fontsize=13)
    ax.plot([6.05, 6.05], [2.6, 2.9], color=C_S, lw=4.5, zorder=6)
    ax.text(6.3, 2.15, r"$S_2$", color=C_S, fontsize=13)
    ax.text(6.0, 5.2, r"$F_1 = F_2$,  $S_2 \ll S_1$  $\Rightarrow$  $p_2 \gg p_1$", ha="center", fontsize=13, color=C_P)
    save(fig, "pressure-button-forces.png")


# ---------------------------------------------------------------------------
# 3. p(S) at fixed force
# ---------------------------------------------------------------------------
def hyperbola():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
    S = np.linspace(2, 60, 300)  # cm^2
    for F, c in [(10, P_LIGHT), (20, P_MID), (30, C_P)]:
        a1.plot(S, 10.0 * F / S, color=c, lw=2.2, label=f"$F = {F}$ Н")  # 1 N/cm^2 = 10 kPa
    a1.set_ylim(0, 160)
    a1.set_xlim(0, 60)
    a1.set_xlabel(r"площадь $S$, см$^2$")
    a1.set_ylabel(r"давление $p$, кПа")
    a1.set_title("Гипербола $p = F/S$ при постоянной силе")
    a1.grid(color=GRID, lw=0.8)
    a1.legend(frameon=False, loc="upper right")
    a1.annotate("площадь вдвое меньше,\nдавление вдвое больше", xy=(10, 30), xytext=(24, 92), fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    a1.plot([10, 20], [30, 15], "o", color=INK, ms=4)

    S2 = np.logspace(-9, 0, 200)  # m^2
    a2.loglog(S2, 30.0 / S2, color=C_P, lw=2.4)
    s_head, s_tip = np.pi * 12e-3**2 / 4, np.pi * 0.12e-3**2 / 4
    a2.loglog([s_head], [30 / s_head], "o", color=C_ORANGE, ms=8, zorder=5)
    a2.loglog([s_tip], [30 / s_tip], "o", color=C_F, ms=8, zorder=5)
    a2.annotate("шляпка кнопки на палец\n0,27 МПа", xy=(s_head, 30 / s_head), xytext=(2e-5, 3e3), fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    a2.annotate("остриё кнопки на дерево\n2,7 ГПа", xy=(s_tip, 30 / s_tip), xytext=(4e-6, 3e10), fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    a2.set_xlim(1e-9, 1)
    a2.set_ylim(10, 2e11)
    a2.set_xlabel(r"площадь $S$, м$^2$")
    a2.set_ylabel(r"давление $p$, Па")
    a2.set_title(r"Тот же закон в логарифмах, $F = 30$ Н")
    a2.grid(color=GRID, lw=0.8, which="major")
    fig.tight_layout()
    save(fig, "pressure-hyperbola-p-of-s.png")


# ---------------------------------------------------------------------------
# 4. p(F) at fixed area
# ---------------------------------------------------------------------------
def lines_p_of_f():
    fig, ax = plt.subplots(figsize=(6.4, 4.3))
    F = np.linspace(0, 100, 50)
    for S, c in [(5, C_P), (10, P_MID), (20, P_LIGHT)]:
        ax.plot(F, 10.0 * F / S, color=c, lw=2.2, label=rf"$S = {S}$ см$^2$")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 210)
    ax.set_xlabel(r"сила давления $F$, Н")
    ax.set_ylabel(r"давление $p$, кПа")
    ax.set_title("Прямые $p = F/S$ при постоянной площади")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left")
    ax.annotate("вдвое меньше площадь:\nпрямая вдвое круче", xy=(60, 60), xytext=(52, 20), fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    save(fig, "pressure-lines-p-of-f.png")


# ---------------------------------------------------------------------------
# 5. Scale of typical pressures
# ---------------------------------------------------------------------------
def scale():
    fig, ax = plt.subplots(figsize=(15, 6.8))
    ax.set_xscale("log")
    ax.set_xlim(0.12, 3e10)
    ax.set_ylim(-5.0, 5.2)
    ax.set_yticks([])
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.xaxis.set_ticks_position("bottom")
    bands = [
        (0.12, 100, "паскали", BAND_A),
        (100, 1e3, "гПа", BAND_B),
        (1e3, 1e6, "килопаскали", BAND_A),
        (1e6, 1e9, "мегапаскали", BAND_B),
        (1e9, 3e10, "гигапаскали", BAND_A),
    ]
    for lo, hi, name, c in bands:
        ax.axvspan(lo, hi, color=c, zorder=0)
        ax.text(np.sqrt(lo * hi), 4.85, name, ha="center", fontsize=11, color=C_P, fontweight="bold")
    ax.set_xticks([1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10])
    ax.set_xticklabels(["1 Па", "10 Па", "1 гПа", "1 кПа", "10 кПа", "100 кПа", "1 МПа", "10 МПа", "100 МПа", "1 ГПа", "10 ГПа"], fontsize=10)
    # (value, label, label x in decades, label y, from lecture)
    items = [
        (0.8, "лист бумаги\n0,8 Па", -0.1, 1.5, True),
        (440, "брусок плашмя\n0,44 кПа", 2.3, 3.4, True),
        (830, "брусок на ребре\n0,83 кПа", 2.3, -1.5, True),
        (1000, "асфальт 5 см\n1 кПа", 3.3, -3.3, True),
        (2500, "лыжник\n2,5 кПа", 4.6, -3.3, True),
        (1.5e4, "человек в обуви\n15 кПа", 3.9, 1.5, False),
        (4e4, "гусеничный трактор\n40 кПа", 4.6, -1.5, False),
        (1.4e5, "нога слона\n140 кПа", 4.6, 3.4, False),
        (1e5, "предел кожи факира\n100 кПа", 5.9, -3.3, True),
        (2.7e5, "кнопка на палец\n0,27 МПа", 5.9, 1.5, True),
        (1e7, "лезвие ножа\n10 МПа", 7.0, 1.5, False),
        (5e8, "разрушение стали\n500 МПа", 8.2, -1.5, True),
        (5.1e8, "кончик иглы\n0,5 ГПа", 8.5, 3.4, False),
        (2.7e9, "остриё кнопки\nв дереве 2,7 ГПа", 9.5, -3.3, True),
    ]
    for v, label, lx, y, lect in items:
        color = C_P if lect else C_ORANGE
        ax.plot([v, 10**lx], [0, y], color=color, lw=1.1, zorder=2)
        # estimates are rings, so a lecture point at the same value (steel under the needle) stays visible
        if lect:
            ax.plot([v], [0], "o", color=color, ms=6, zorder=5)
        else:
            ax.plot([v], [0], "o", mfc="none", mec=color, mew=1.8, ms=11, zorder=4)
        ax.text(10**lx, y + (0.08 if y > 0 else -0.08), label, ha="center", va="bottom" if y > 0 else "top", fontsize=9, color=INK, zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", fc=PAPER, ec=color, lw=1.0))
    ax.plot([], [], "o", color=C_P, label="из лекции")
    ax.plot([], [], "o", mfc="none", mec=C_ORANGE, mew=1.8, ms=11, label="типичная оценка, не из лекции")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=10)
    ax.set_title("Порядки давления, логарифмическая шкала", pad=14)
    save(fig, "pressure-units-scale.png")


# ---------------------------------------------------------------------------
# 6. Sheet of paper cut into pieces
# ---------------------------------------------------------------------------
def paper_sheet():
    fig, ax = blank(9.6, 4.6, (-0.2, 8.6), (-2.2, 3.7))
    sheets = [
        (0.0, 3.4, 3.4, "1 м$^2$", "80 г"),
        (4.4, 2.4, 2.4, "0,5 м$^2$", "40 г"),
        (7.3, 0.72, 1.02, "лист А4\n0,063 м$^2$", "5 г"),
    ]
    for x, w, h, area, mass in sheets:
        ax.add_patch(Rectangle((x, 0), w, h, fc=tint(INK, 0.95), ec=INK, lw=1.4, zorder=3))
        ax.text(x + w / 2, h / 2, mass, ha="center", va="center", fontsize=12, color=C_F, zorder=4)
        ax.text(x + w / 2, -0.3, area, ha="center", va="top", fontsize=10.5, color=C_S)
        ax.text(x + w / 2, -1.4, r"$p = 0{,}8$ Па", ha="center", va="top", fontsize=11.5, color=C_P)
    ax.text(4.2, -2.1, "масса и площадь меняются в одно число раз, дробь $mg/S$ остаётся прежней", ha="center", fontsize=10, color=INK, va="center")
    save(fig, "pressure-paper-sheet.png")


# ---------------------------------------------------------------------------
# 7. Brick on its faces
# ---------------------------------------------------------------------------
def brick_faces(name, mass, placements, sc, foot_sc, width):
    """placements: (w, h, d, label) in cm; w x d is the contact face."""
    n = len(placements)
    fig, ax = plt.subplots(figsize=(width * n, 5.6))
    ax.set_xlim(0, width * n)
    ax.set_ylim(-4.3, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    F = mass * G
    for i, (w, h, d, lbl) in enumerate(placements):
        x0 = i * width + 0.5
        W, H, D = w * sc, h * sc, d * sc
        y0 = 0.5
        ax.plot([x0 - 0.3, x0 + W + D * 0.55 + 0.3], [y0, y0], color=INK, lw=1.2)
        box(ax, x0, y0, W, H, D)
        ax.text(x0 + W / 2, y0 + H + D * 0.38 + 0.35, lbl, ha="center", fontsize=11, color=INK)
        S = w * d
        p = F / (S * 1e-4)
        fy = -0.8 - d * foot_sc
        ax.add_patch(Rectangle((x0, fy), w * foot_sc, d * foot_sc, fc=FOOT, ec=C_S, lw=1.6))
        ax.text(x0 + w * foot_sc / 2, fy - 0.3, "$S = " + num(S, 1) + r"$ см$^2$", ha="center", va="top", fontsize=10, color=C_S)
        ax.text(x0 + w * foot_sc / 2, fy - 1.0, "$p = " + num(p / 1000, 2) + r"$ кПа", ha="center", va="top", fontsize=12, color=C_P, fontweight="bold")
    ax.text(width * n / 2, 3.9, "$m = " + num(mass, 3) + r"$ кг,  $F = mg = " + num(F, 2) + r"$ Н", ha="center", fontsize=11, color=C_F)
    save(fig, name)


def brick_lecture():
    a, b = 5.7, 3.0
    brick_faces("pressure-brick-two-faces.png", 0.142, [(a, b, a, "плашмя"), (b, a, a, "на ребре")], 0.28, 0.24, 3.9)


def brick_standard():
    brick_faces(
        "pressure-brick-three-faces.png",
        3.6,
        [(25, 6.5, 12, "плашмя"), (25, 12, 6.5, "на боку"), (12, 25, 6.5, "стоймя")],
        0.11,
        0.11,
        3.9,
    )


# ---------------------------------------------------------------------------
# 8. F-S plane
# ---------------------------------------------------------------------------
def fs_plane():
    fig, ax = plt.subplots(figsize=(9.6, 6.4))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e1, 1e-9)
    ax.set_ylim(1e-1, 1e4)
    S = np.logspace(-9, 1, 10)
    for p, lab, sx in [(1, "1 Па", 6.0), (1e3, "1 кПа", 6.0), (1e6, "1 МПа", 6e-3), (1e9, "1 ГПа", 6e-6)]:
        ax.plot(S, p * S, color=ASH, lw=1.8, zorder=1)
        fy = min(p * sx, 6e3)
        sx = fy / p
        ax.text(sx, fy, " " + lab + " ", color=C_P, fontsize=11, fontweight="bold", ha="left", va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.15", fc=PAPER, ec="none"))
    pts = [
        ("лист бумаги", 0.8, 1.0, (10, 8), "left"),
        ("брусок плашмя", 1.42, 3.249e-3, (-8, 10), "right"),
        ("брусок на ребре", 1.42, 1.71e-3, (10, -14), "left"),
        ("лыжник на лыжах", 900, 0.36, (10, 6), "left"),
        ("факир на 50 лезвиях", 600, 6e-3, (10, 6), "left"),
        ("шляпка кнопки", 30, 1.13e-4, (10, 6), "left"),
        ("остриё кнопки", 30, 1.13e-8, (-10, 8), "right"),
    ]
    for name, F, s, off, ha in pts:
        ax.plot([s], [F], "o", color=C_F, ms=7, zorder=5)
        ax.annotate(name, xy=(s, F), xytext=off, textcoords="offset points", fontsize=9.5, color=INK, ha=ha, va="center", zorder=6)
    ax.set_xlabel(r"площадь опоры $S$, м$^2$ (растёт влево)")
    ax.set_ylabel(r"сила давления $F$, Н")
    ax.set_title("Плоскость $F$–$S$: линии равного давления")
    ax.grid(color=GRID, lw=0.6, which="major", zorder=0)
    ax.annotate("", xy=(2e-1, 3e2), xytext=(2e-1, 4), arrowprops=dict(arrowstyle="-|>", color=C_F, lw=2.4))
    ax.text(1.5e-1, 25, "растёт $F$:\nдавление растёт", color=C_F, fontsize=10, ha="left", va="center")
    ax.annotate("", xy=(3e-8, 2e-1), xytext=(1e-4, 2e-1), arrowprops=dict(arrowstyle="-|>", color=C_S, lw=2.4))
    ax.text(1e-6, 2.4e-1, "убывает $S$: давление растёт", color=C_S, fontsize=10, ha="center", va="bottom")
    save(fig, "pressure-fs-plane.png")


# ---------------------------------------------------------------------------
# 9. Skis and boots
# ---------------------------------------------------------------------------
def skis_boots():
    fig = plt.figure(figsize=(9.6, 3.6))
    ax = fig.add_axes([0.0, 0.02, 0.62, 0.92])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    sc = 6.0  # plot units per metre
    for yy in (5.2, 4.2):
        ax.add_patch(Rectangle((0.5, yy), 1.8 * sc, 0.1 * sc, fc=FOOT, ec=C_S, lw=1.6))
    ax.text(0.5, 6.2, "на лыжах: $S = 2 \\cdot 1{,}8 \\cdot 0{,}1 = 0{,}36$ м$^2$", fontsize=10, color=C_S)
    for yy in (2.0, 1.0):
        ax.add_patch(Rectangle((0.5, yy), 0.30 * sc, 0.1 * sc, fc=FOOT, ec=C_S, lw=1.6))
    ax.text(0.5, 3.0, "в обуви: $S = 2 \\cdot 0{,}30 \\cdot 0{,}10 = 0{,}06$ м$^2$ (допущение)", fontsize=10, color=C_S)
    ax.text(0.5, 0.15, "площади в одном масштабе", fontsize=9, color=GREY)
    ax2 = fig.add_axes([0.72, 0.16, 0.26, 0.72])
    vals = [900 / 0.36 / 1e3, 900 / 0.06 / 1e3]
    bars = ax2.bar(["на лыжах", "в обуви"], vals, color=[C_P, P_LIGHT], width=0.55)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.4, num(v, 1) .replace("{,}", ",") + " кПа", ha="center", fontsize=10.5, color=INK)
    ax2.set_ylabel(r"давление $p$, кПа")
    ax2.set_ylim(0, 18)
    ax2.set_title("$m = 90$ кг", fontsize=11)
    save(fig, "pressure-skis-boots.png")


# ---------------------------------------------------------------------------
# 10. Fakir: p(N)
# ---------------------------------------------------------------------------
def fakir():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    N = np.linspace(1, 100, 400)
    p = 600.0 / (N * 0.6 * 0.2e-3) / 1e3  # kPa
    ax.loglog(N, p, color=C_P, lw=2.4)
    ax.loglog([50], [100], "o", color=C_F, ms=8, zorder=5)
    ax.loglog([1], [5000], "o", color=C_ORANGE, ms=8, zorder=5)
    ax.axhline(100, color=GREY, lw=1, ls="--")
    ax.annotate("50 лезвий: 100 кПа", xy=(50, 100), xytext=(7, 45), fontsize=10, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("одно лезвие: 5 МПа", xy=(1, 5000), xytext=(1.5, 1.4e4), fontsize=10, color=INK, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_xlim(1, 100)
    ax.set_ylim(30, 3e4)
    ax.set_xlabel("число лезвий $N$")
    ax.set_ylabel(r"давление $p$, кПа")
    ax.set_title(r"Факир: $m = 60$ кг, лезвие $60$ см $\times$ $0{,}2$ мм")
    ax.grid(color=GRID, lw=0.7, which="both")
    save(fig, "pressure-fakir-blades.png")


# ---------------------------------------------------------------------------
# 11. Layer shapes: same thickness, same pressure
# ---------------------------------------------------------------------------
def layer_shapes():
    fig, ax = blank(10.4, 4.0, (0, 13.5), (-1.3, 4.6))
    ax.plot([0, 13.5], [0.5, 0.5], color=INK, lw=1.4)
    t = 0.6
    box(ax, 0.6, 0.5, 2.4, t, 1.8, face=PLATE)
    box(ax, 4.2, 0.5, 4.0, t, 2.6, face=PLATE)
    cx, ry, rx = 11.3, 0.7, 1.6
    # the disc stands on the table: its lower ellipse touches the line from above
    b0 = 0.5 + ry
    ax.add_patch(Ellipse((cx, b0), 2 * rx, 2 * ry, fc=PLATE, ec=INK, lw=1.3, zorder=2))
    ax.add_patch(Rectangle((cx - rx, b0), 2 * rx, t, fc=PLATE, ec="none", zorder=3))
    ax.plot([cx - rx, cx - rx], [b0, b0 + t], color=INK, lw=1.3, zorder=4)
    ax.plot([cx + rx, cx + rx], [b0, b0 + t], color=INK, lw=1.3, zorder=4)
    ax.add_patch(Ellipse((cx, b0 + t), 2 * rx, 2 * ry, fc=PLATE_TOP, ec=INK, lw=1.3, zorder=5))
    for x in (1.8, 6.2, 11.3):
        ax.text(x, 3.6, "$S$ любая", ha="center", fontsize=11, color=C_S)
        ax.text(x, -0.7, r"$p = \rho g h$", ha="center", fontsize=13, color=C_P, va="center")
    # h is measured on the front face of the first tile
    arrow(ax, (0.35, 0.5), (0.35, 0.5 + t), color=INK, lw=1.1, style="<|-|>", scale=8)
    ax.text(0.1, 0.5 + t / 2, "$h$", fontsize=11, va="center", ha="right")
    ax.text(6.75, 4.4, "толщина $h$ и плотность $\\rho$ одни и те же: давление одно и то же", ha="center", fontsize=11, color=INK)
    save(fig, "pressure-layer-shapes.png")


# ---------------------------------------------------------------------------
# 12. p(h) for several materials
# ---------------------------------------------------------------------------
def layer_p_of_h():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    h = np.linspace(0, 12, 50)
    mats = [("асфальт, 2000 кг/м$^3$", 2000, tint(INK, 0.25)), ("алюминий, 2700 кг/м$^3$", 2700, METAL), ("медь, 8900 кг/м$^3$", 8900, COPPER)]
    for name, rho, c in mats:
        ax.plot(h, rho * G * h / 100 / 1e3, color=c, lw=2.2, label=name)
    ax.axhline(2.7, color=GREY, lw=1, ls="--")
    ax.plot([5], [1.0], "o", color=INK, ms=7)
    ax.annotate("асфальт 5 см: 1 кПа", xy=(5, 1.0), xytext=(6.2, 0.25), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.plot([10], [2.7], "o", color=INK, ms=7)
    ax.plot([2.7 / (8900 * G / 100 / 1e3)], [2.7], "o", color=INK, ms=7)
    ax.annotate("Al 10 см", xy=(10, 2.7), xytext=(10.2, 3.5), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("Cu 3 см", xy=(3.03, 2.7), xytext=(3.4, 4.6), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10.5)
    ax.set_xlabel(r"высота $h$, см")
    ax.set_ylabel(r"давление $p = \rho g h$, кПа")
    ax.set_title("Давление столбика вещества")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "pressure-layer-p-of-h.png")


# ---------------------------------------------------------------------------
# 13. Two cylinders
# ---------------------------------------------------------------------------
def cylinders():
    fig, ax = blank(8.4, 5.2, (0, 10.4), (-1.3, 6.0))
    ax.plot([0.2, 10.2], [0.0, 0.0], color=INK, lw=1.4)
    sc = 0.4
    rx, ry = 1.25, 0.32
    for cx, hcm, col, name in ((2.8, 10.0, ALUMINIUM, "алюминий\n$h_\\mathrm{Al} = 10$ см"), (7.6, 3.03, COPPER_FILL, "медь\n$h_\\mathrm{Cu} \\approx 3$ см")):
        H = hcm * sc
        ax.add_patch(Ellipse((cx, 0), 2 * rx, 2 * ry, fc=col, ec=INK, lw=1.3, zorder=1))
        ax.add_patch(Rectangle((cx - rx, 0), 2 * rx, H, fc=col, ec="none", zorder=2))
        ax.plot([cx - rx, cx - rx], [0, H], color=INK, lw=1.3, zorder=3)
        ax.plot([cx + rx, cx + rx], [0, H], color=INK, lw=1.3, zorder=3)
        ax.add_patch(Ellipse((cx, H), 2 * rx, 2 * ry, fc=col, ec=INK, lw=1.3, zorder=4))
        ax.add_patch(Ellipse((cx, H), 2 * rx, 2 * ry, fc=PAPER, alpha=0.3, ec="none", zorder=5))
        ax.text(cx, H + 0.6, name, ha="center", fontsize=10.5, color=INK, va="bottom")
        ax.text(cx, -0.65, r"$p = 2{,}7$ кПа,  одно $S$", ha="center", va="top", fontsize=10, color=C_P)
    ax.text(5.2, 5.7, "$m_\\mathrm{Al} = m_\\mathrm{Cu}$: равные $p$ и $S$ дают равный вес", ha="center", fontsize=10.5, color=C_F)
    save(fig, "pressure-cylinders.png")


# ---------------------------------------------------------------------------
# 14. Books
# ---------------------------------------------------------------------------
def books():
    fig, ax = blank(10.0, 5.0, (0, 14.0), (-4.6, 4.6))
    th = 0.32
    bw, sw = 30 * 0.09, 20 * 0.09  # 450 = 30 x 15 cm and 300 = 20 x 15 cm as drawn
    ax.plot([0.3, 6.9], [0, 0], color=INK, lw=1.4)
    ax.plot([7.5, 13.7], [0, 0], color=INK, lw=1.4)
    x0, x1 = 0.9, 8.2
    box(ax, x0, 0, bw, th, 1.4, face=BOOK_BIG)
    box(ax, x0 + 0.3, th, sw, th, 1.0, face=BOOK_SMALL, z=4)
    ax.text(x0 + 2.0, 2.15, "меньшая сверху", ha="center", fontsize=10.5, color=INK)
    box(ax, x1 + 0.2, 0, sw, th, 1.0, face=BOOK_SMALL)
    box(ax, x1, th, bw, th, 1.4, face=BOOK_BIG, z=4)
    ax.text(x1 + 2.0, 2.15, "большая сверху", ha="center", fontsize=10.5, color=INK)
    fs = 0.12
    top = -1.0
    ax.add_patch(Rectangle((x0, top - 15 * fs), 30 * fs, 15 * fs, fc=FOOT, ec=C_S, lw=1.6))
    ax.text(x0 + 15 * fs, top - 7.5 * fs, r"$S_б = 450$ см$^2$", ha="center", va="center", fontsize=10, color=C_S)
    ax.text(x0 + 15 * fs, top - 15 * fs - 0.4, r"$p_1 = P/S_б = 200$ Па", ha="center", fontsize=11.5, color=C_P, fontweight="bold")
    ax.add_patch(Rectangle((x1, top - 15 * fs), 20 * fs, 15 * fs, fc=FOOT, ec=C_S, lw=1.6))
    ax.text(x1 + 10 * fs, top - 7.5 * fs, r"$S_м = 300$ см$^2$", ha="center", va="center", fontsize=10, color=C_S)
    ax.text(x1 + 10 * fs, top - 15 * fs - 0.4, r"$p_2 = P/S_м = 300$ Па", ha="center", fontsize=11.5, color=C_P, fontweight="bold")
    ax.text(7.0, 4.0, "общий вес $P = 9$ Н в обоих случаях", ha="center", fontsize=11, color=C_F)
    save(fig, "pressure-books.png")


# ---------------------------------------------------------------------------
# 15. Thumbtack under weights
# ---------------------------------------------------------------------------
def tack_bars():
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    S = np.pi * (0.12e-3) ** 2 / 4
    Fs = [10, 20, 30]
    p = [F / S / 1e9 for F in Fs]
    b = ax.bar([f"{F} Н\n({F // 10} кг)" for F in Fs], p, color=[P_LIGHT, P_MID, C_P], width=0.55)
    for bar, v, w in zip(b, p, ["не вошла", "почти вошла", "вошла"]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05, num(v, 2).replace("{,}", ",") + " ГПа\n" + w, ha="center", fontsize=10.5, color=INK)
    ax.set_ylim(0, 3.7)
    ax.set_ylabel(r"давление острия $p = 4F/\pi d^2$, ГПа")
    ax.set_title(r"Острие кнопки, $d = 0{,}12$ мм, в дереве")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "pressure-thumbtack-weights.png")


if __name__ == "__main__":
    nails_board()
    button_forces()
    hyperbola()
    lines_p_of_f()
    scale()
    paper_sheet()
    brick_lecture()
    fs_plane()
    skis_boots()
    fakir()
    layer_shapes()
    layer_p_of_h()
    cylinders()
    books()
    tack_bars()
