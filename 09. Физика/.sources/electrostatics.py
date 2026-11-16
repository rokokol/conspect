"""Figures for the notes "Электризация тел. Электрический заряд" (lessons 135, 136, 141)
and "Электрическое поле. Делимость заряда" (lesson 137).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 electrostatics.py
PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes charge- and field-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "11. Электрические явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, VIOLET, WARM, saver, tint

LIGHT_METAL = tint(INK, 0.75)  # a pale grey metal body

GRID = ASH
GREY = tint(INK, 0.45)  # outlines of neutral bodies, guides and small notes
POS = RED  # positive charge
NEG = BLUE  # negative charge
GOLD = WARM
GLASS = tint(SKY, 0.8)
EBONITE = tint(INK, 0.75)
WOOL = tint(WARM, 0.75)  # polyethylene, fur, silk: the rubbing material
SOFT = tint(INK, 0.94)  # the pale body fill of a neutral part
POS_FILL = tint(RED, 0.85)  # the pale fill of a positively charged body
NEG_FILL = tint(BLUE, 0.85)  # the pale fill of a negatively charged body


save = saver(OUT)


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def sign(ax, x, y, s, r=0.085, fs=9):
    color = POS if s == "+" else NEG
    ax.add_patch(Circle((x, y), r, facecolor=PAPER, edgecolor=color, lw=1.1, zorder=5))
    ax.text(
        x,
        y - 0.004,
        "+" if s == "+" else "−",
        color=color,
        ha="center",
        va="center",
        fontsize=fs,
        fontweight="bold",
        zorder=6,
    )


def signs(ax, pts, s, **kw):
    for x, y in pts:
        sign(ax, x, y, s, **kw)


def arrow(ax, p, q, color=INK, lw=1.8, ms=13, style="-|>", ls="-", z=4):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, lw=lw, color=color, linestyle=ls, zorder=z
        )
    )


# ---------------------------------------------------------------------------
# Lesson 135


def gravity_vs_electric():
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    ax.set_xlim(-3, 47)
    fig.set_size_inches(7.2, 2.5)
    ax.set_ylim(-1, 2.2)
    ax.axhline(0, color=INK, lw=1.5)
    for v in range(0, 46, 6):
        ax.plot([v, v], [-0.08, 0.08], color=INK, lw=1)
        ax.text(v, -0.35, f"$10^{{{v}}}$", ha="center", va="top", fontsize=9)
    # The 10^42 ratio holds for two electrons; charged rods give about 5*10^6 (footnote [^grav])
    ax.plot([0], [0], "o", ms=11, color=NEG, zorder=5)
    ax.plot([np.log10(5e6)], [0], "o", ms=11, color=GOLD, zorder=5)
    ax.plot([np.log10(4e42)], [0], "o", ms=11, color=POS, zorder=5)
    ax.text(0, 0.35, "гравитационное\nвзаимодействие", ha="center", va="bottom", color=NEG)
    ax.plot([np.log10(5e6)] * 2, [0.15, 1.0], color=GOLD, lw=1.2, zorder=1)
    ax.text(np.log10(5e6), 1.05, "заряженные палочки:\n" + r"$\approx5\cdot10^{6}$ раз", ha="center", va="bottom", color=INK)
    ax.text(np.log10(4e42), 0.35, "два электрона:\n" + r"$\approx4\cdot10^{42}$ раз", ha="center", va="bottom", color=POS)
    ax.annotate(
        "",
        xy=(41.3, 0.12),
        xytext=(0.7, 0.12),
        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.4),
    )
    ax.text(24, 0.2, r"$F_{\mathrm{эл}}\,/\,F_{\mathrm{грав}}$", ha="center", va="bottom", color=INK, fontsize=10.5)
    ax.axis("off")
    ax.set_title("Отношение электрической силы к гравитационной на логарифмической шкале", pad=4, fontsize=11)
    save(fig, "charge-gravity-vs-electric.png")


def tribo_series():
    items = [
        ("стекло", "+"),
        ("волосы", ""),
        ("шерсть", ""),
        ("шёлк", ""),
        ("бумага", ""),
        ("янтарь", ""),
        ("эбонит", ""),
        ("полиэтилен", "−"),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.0, len(items) + 0.9)
    n = len(items)
    cmap = np.linspace(0, 1, n)
    for i, (name, _) in enumerate(items):
        y = n - 1 - i
        t = cmap[i]
        col = tuple(np.array(to_rgb(POS)) * (1 - t) + np.array(to_rgb(NEG)) * t)
        ax.add_patch(
            FancyBboxPatch(
                (2.2, y - 0.36),
                3.6,
                0.72,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                fc=col,
                ec="none",
                alpha=0.9,
            )
        )
        ax.text(4.0, y, name, ha="center", va="center", color=PAPER, fontsize=12, fontweight="bold")
    ax.annotate(
        "",
        xy=(7.0, -0.35),
        xytext=(7.0, n - 0.65),
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6),
    )
    ax.text(7.25, n - 1, "заряжается\nположительно", va="center", color=POS, fontsize=11)
    ax.text(7.25, 0, "заряжается\nотрицательно", va="center", color=NEG, fontsize=11)
    ax.text(
        7.25,
        (n - 1) / 2,
        "при трении двух тел\nвышестоящее получает +,\nнижестоящее получает −",
        va="center",
        fontsize=9.5,
        color=INK,
    )
    ax.text(
        0.1,
        -0.95,
        "справочный порядок, не из лекции",
        fontsize=8.5,
        color=GREY,
        ha="left",
    )
    ax.axis("off")
    ax.set_title("Трибоэлектрический ряд", pad=6)
    save(fig, "charge-triboelectric-series.png")


def rod(ax, x, y, w, h, label, color, signs_list=None):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            fc=color,
            ec=INK,
            lw=1.2,
            zorder=2,
        )
    )
    ax.text(x, y - h / 2 - 0.22, label, ha="center", va="top", fontsize=10)


def interaction():
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 5.6))
    cfg = [
        ("стекло и стекло: отталкивание", "+", "+", GLASS, GLASS, "стекло", "стекло"),
        ("эбонит и эбонит: отталкивание", "−", "−", EBONITE, EBONITE, "эбонит", "эбонит"),
        ("стекло и эбонит: притяжение", "+", "−", GLASS, EBONITE, "стекло", "эбонит"),
    ]
    for ax, (title, s1, s2, c1, c2, l1, l2) in zip(axes, cfg):
        blank(ax, (-4.8, 4.8), (-1.0, 0.9))
        ax.set_title(title, fontsize=11, pad=0)
        repel = s1 == s2
        xa, xb = (-2.2, 2.2)
        rod(ax, xa, 0, 2.2, 0.5, l1, c1)
        rod(ax, xb, 0, 2.2, 0.5, l2, c2)
        for x0, s in ((xa, s1), (xb, s2)):
            signs(ax, [(x0 + d, 0) for d in (-0.7, 0, 0.7)], "+" if s == "+" else "-", r=0.11, fs=10)
        if repel:
            arrow(ax, (xa - 1.2, 0), (xa - 2.6, 0), color=GREEN, lw=2.4, ms=16)
            arrow(ax, (xb + 1.2, 0), (xb + 2.6, 0), color=GREEN, lw=2.4, ms=16)
        else:
            arrow(ax, (xa + 1.2, 0), (-0.15, 0), color=GREEN, lw=2.4, ms=16)
            arrow(ax, (xb - 1.2, 0), (0.15, 0), color=GREEN, lw=2.4, ms=16)
    fig.tight_layout(h_pad=0.4)
    save(fig, "charge-interaction.png")


def rubbing_separation():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.2))
    for k, ax in enumerate(axes):
        blank(ax, (-4.4, 4.4), (-2.0, 1.7))
        ax.set_title("до трения: оба тела нейтральны" if k == 0 else "после трения: заряды разделены", fontsize=11, pad=0)
        xa, xb = (-2.2, 2.2)
        # Bodies are 1.4 high so that every sign, including the transferred electrons, lies inside the outline
        rod(ax, xa, 0, 3.2, 1.4, "стекло", GLASS)
        rod(ax, xb, 0, 3.2, 1.4, "полиэтилен", WOOL)
        px = [-1.1, -0.37, 0.37, 1.1]
        if k == 0:
            for x0 in (xa, xb):
                signs(ax, [(x0 + d, 0.4) for d in px], "+")
                signs(ax, [(x0 + d, -0.4) for d in px], "-")
            ax.text(0, -1.6, r"$q_{\mathrm{стекла}}=0,\quad q_{\mathrm{полиэтилена}}=0,\quad$ сумма $=0$", ha="center", fontsize=11)
        else:
            signs(ax, [(xa + d, 0.4) for d in px], "+")
            signs(ax, [(xa + d, -0.4) for d in px[:2]], "-")
            signs(ax, [(xb + d, 0.4) for d in px], "+")
            signs(ax, [(xb + d, -0.4) for d in px], "-")
            signs(ax, [(xb + d, 0.0) for d in (-0.4, 0.4)], "-")
            arrow(ax, (-0.5, 1.0), (0.9, 1.0), color=GREEN, lw=2.2, ms=15)
            ax.text(0.2, 1.2, "электроны", ha="center", fontsize=9.5, color=GREEN)
            ax.text(0, -1.6, r"$q_{\mathrm{стекла}}>0,\quad q_{\mathrm{полиэтилена}}<0,\quad$ сумма $=0$", ha="center", fontsize=11)
    fig.tight_layout(h_pad=0.5)
    save(fig, "charge-rubbing-separation.png")


def conductors_dielectrics():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.6))
    rng = np.random.default_rng(3)
    for k, ax in enumerate(axes):
        blank(ax, (-4.2, 4.2), (-1.3, 1.1))
        ax.set_title(
            "проводник: электроны свободно перемещаются" if k == 0 else "диэлектрик: заряды остаются на месте",
            fontsize=11,
            pad=0,
        )
        ax.add_patch(Rectangle((-3.4, -0.55), 6.8, 1.1, fc=LIGHT_METAL if k == 0 else WOOL, ec=INK, lw=1.2, zorder=1))
        xs = np.linspace(-3.0, 3.0, 7)
        for x in xs:
            for y in (-0.28, 0.28):
                ax.add_patch(Circle((x, y), 0.13, fc=POS, ec="none", zorder=3, alpha=0.85))
                ax.text(x, y, "+", color=PAPER, ha="center", va="center", fontsize=8, zorder=4)
        if k == 0:
            for _ in range(9):
                x, y = rng.uniform(-3.0, 2.6), rng.uniform(-0.45, 0.45)
                sign(ax, x, y, "-", r=0.09, fs=8)
                arrow(ax, (x + 0.12, y), (x + 0.6, y), color=GREEN, lw=1.3, ms=9)
            ax.text(0, -0.95, "направленное движение возможно", ha="center", fontsize=10, color=GREEN)
        else:
            for x in xs:
                for y in (-0.28, 0.28):
                    sign(ax, x + 0.24, y, "-", r=0.09, fs=8)
                    ax.add_patch(Circle((x + 0.24, y), 0.17, fc="none", ec=GREY, lw=0.9, ls="--", zorder=2))
            ax.text(0, -0.95, "только колебания около своих мест", ha="center", fontsize=10, color=POS)
    fig.tight_layout(h_pad=0.5)
    save(fig, "charge-conductors-dielectrics.png")


# ---------------------------------------------------------------------------
# Lesson 136: electroscope and electrometer


def leaf_electroscope(ax, cx, theta_deg, n_plus, title, polarity="+"):
    """Draw an electroscope centred at cx; leaves diverge by theta_deg from the vertical."""
    s = polarity
    th = np.radians(theta_deg)
    # case: one closed outline, a circle arc plus the neck walls, so no arc runs through the neck
    cy, R, hw = -0.05, 1.3, 0.55
    a0 = np.degrees(np.arctan2(np.sqrt(R**2 - hw**2), hw))
    ang = np.radians(np.linspace(a0, -180 - a0, 80))  # clockwise from the right neck wall to the left one
    arc_pts = [(cx + R * np.cos(t), cy + R * np.sin(t)) for t in ang]
    neck = [(cx - hw, 1.5), (cx + hw, 1.5)]
    ax.add_patch(Polygon(arc_pts + neck, closed=True, fc=GLASS, ec=INK, lw=1.4, zorder=0, joinstyle="round"))
    # base
    ax.add_patch(Rectangle((cx - 0.9, -1.6), 1.8, 0.22, fc=LIGHT, ec=INK, lw=1.2, zorder=1))
    # insulator plug
    ax.add_patch(Rectangle((cx - 0.34, 0.98), 0.68, 0.32, fc=tint(VIOLET, 0.5), ec=INK, lw=1.2, zorder=3))
    # rod
    ax.plot([cx, cx], [1.75, -0.45], color=INK, lw=3, zorder=2, solid_capstyle="round")
    # ball
    ax.add_patch(Circle((cx, 1.98), 0.3, fc=LIGHT_METAL, ec=INK, lw=1.4, zorder=3))
    # leaves
    L = 0.75
    for sg in (-1, 1):
        tip = (cx + sg * L * np.sin(th), -0.45 - L * np.cos(th))
        ax.plot([cx, tip[0]], [-0.45, tip[1]], color=GOLD, lw=4, solid_capstyle="round", zorder=2)
    if n_plus:
        pts_ball = [(cx + 0.42 * np.cos(a), 1.98 + 0.42 * np.sin(a)) for a in np.radians([40, 140, 90][:min(3, n_plus)])]
        signs(ax, pts_ball, s, r=0.09)
        pts_rod = [(cx + 0.2, 0.5), (cx - 0.2, 0.15), (cx + 0.2, -0.15)][: max(0, n_plus - 1)]
        signs(ax, pts_rod, s, r=0.09)
        for sg in (-1, 1):
            tip = (cx + sg * L * np.sin(th), -0.45 - L * np.cos(th))
            mid = (cx + sg * (L * 0.55) * np.sin(th) + sg * 0.16, -0.45 - 0.55 * L * np.cos(th))
            sign(ax, mid[0], mid[1], s, r=0.09)
    ax.text(cx, -1.9, title, ha="center", va="top", fontsize=10.5)


def electroscope():
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    blank(ax, (-3.3, 8.0), (-2.6, 2.5))
    leaf_electroscope(ax, 0.0, 0, 0, "заряда нет:\nлепестки висят")
    leaf_electroscope(ax, 3.4, 14, 2, "малый заряд:\nугол небольшой")
    leaf_electroscope(ax, 6.4, 34, 4, "больший заряд:\nугол больше")
    ax.annotate("шар", (-0.3, 2.0), (-3.2, 2.1), fontsize=9.5, va="center", arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("изолятор", (-0.3, 1.14), (-3.2, 1.45), fontsize=9.5, va="center", arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("металлический\nстержень", (0.0, 0.3), (-3.2, 0.5), fontsize=9.5, va="center", arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("прозрачный\nкорпус", (-1.05, -0.6), (-3.2, -0.6), fontsize=9.5, va="center", arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate("лепестки", (-0.04, -0.95), (-3.2, -1.5), fontsize=9.5, va="center", arrowprops=dict(arrowstyle="-", color=GREY))
    fig.tight_layout()
    save(fig, "charge-electroscope.png")


def draw_electrometer(ax, cx, angle_deg, ball_signs=(), rod_signs=(), needle_signs=(), title="", cy=0.0, s_default="+"):
    """Electrometer with metal case; needle is vertical at rest and turns by angle_deg."""
    th = np.radians(angle_deg)
    P = (cx, cy - 0.15)
    ax.add_patch(Circle((cx, cy), 0.95, fc=SOFT, ec=INK, lw=1.6, zorder=0))
    ax.add_patch(Polygon([[cx - 0.35, cy - 0.95], [cx + 0.35, cy - 0.95], [cx + 0.55, cy - 1.45], [cx - 0.55, cy - 1.45]], fc=LIGHT, ec=INK, lw=1.2, zorder=0))
    # scale
    r = 0.72
    ax.add_patch(Arc(P, 2 * r, 2 * r, theta1=0, theta2=90, color=GREY, lw=1.2, zorder=1))
    for a in np.linspace(0, 90, 7):
        ca, sa = np.cos(np.radians(a)), np.sin(np.radians(a))
        ax.plot([P[0] + (r - 0.06) * sa, P[0] + r * sa], [P[1] + (r - 0.06) * ca, P[1] + r * ca], color=GREY, lw=1.0, zorder=1)
    # insulator
    ax.add_patch(Rectangle((cx - 0.2, cy + 0.85), 0.4, 0.28, fc=tint(VIOLET, 0.5), ec=INK, lw=1.2, zorder=3))
    # rod & ball
    ax.plot([cx, cx], [cy + 1.5, P[1]], color=INK, lw=3, zorder=2, solid_capstyle="round")
    ax.add_patch(Circle((cx, cy + 1.75), 0.34, fc=LIGHT_METAL, ec=INK, lw=1.4, zorder=3))
    # needle
    tip = (P[0] + 0.72 * np.sin(th), P[1] + 0.72 * np.cos(th))
    tail = (P[0] - 0.22 * np.sin(th), P[1] - 0.22 * np.cos(th))
    ax.plot([tail[0], tip[0]], [tail[1], tip[1]], color=GOLD, lw=3.6, zorder=3, solid_capstyle="round")
    ax.add_patch(Circle(P, 0.05, fc=INK, zorder=4))
    return P, tip


def electrometer():
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    blank(ax, (-3.2, 4.2), (-1.7, 2.4))
    P2, tip2 = draw_electrometer(ax, 0.0, 38)
    # Rest position of the needle: dashed, shifted 0.1 to the right of the rod so that the rod stays solid
    ax.plot([0.1, 0.1], [P2[1], P2[1] + 0.72], color=GREY, lw=2.0, ls=(0, (3, 2)), zorder=1)
    labels = [
        ("шар", (-0.3, 1.9), (-2.9, 2.0)),
        ("металлический стержень", (0.0, 0.55), (-3.15, 1.0)),
        ("пластиковый изолятор", (-0.2, 1.0), (1.15, 1.55)),
        ("металлический корпус", (-0.67, -0.65), (-3.15, -0.85)),
        ("подставка", (0.0, -1.3), (-1.6, -1.6)),
    ]
    for text, xy, xyt in labels:
        ax.annotate(text, xy, xyt, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=GREY), va="center")
    ax.annotate("алюминиевая стрелка", tip2, (1.3, 1.05), fontsize=9.5, arrowprops=dict(arrowstyle="-", color=GREY), va="center")
    ax.annotate("шкала", (0.55, 0.3), (1.5, 0.15), fontsize=9.5, arrowprops=dict(arrowstyle="-", color=GREY), va="center")
    ax.text(1.25, -0.55, "штриховая линия: стрелка\nбез заряда, вертикальна", fontsize=8.8, color=GREY, va="center")
    fig.tight_layout()
    save(fig, "charge-electrometer.png")


def electrometer_sign():
    fig, ax = plt.subplots(figsize=(10.4, 5.4))
    blank(ax, (-2.0, 9.6), (-2.1, 4.2))
    cases = [
        (0.0, 34, "исходно: электрометр заряжен +", None),
        (3.9, 12, "поднесён −: стрелка опадает", "-"),
        (7.8, 62, "поднесён +: стрелка отклоняется сильнее", "+"),
    ]
    for cx, ang, title, rod_sign in cases:
        P, tip = draw_electrometer(ax, cx, ang)
        # charge counts: ball, rod, needle
        if rod_sign is None:
            nb, nr, nn = 3, 2, 2
        elif rod_sign == "-":
            nb, nr, nn = 5, 1, 1
        else:
            nb, nr, nn = 1, 3, 3  # total stays 7, as in the other two panels
        bx = [cx + 0.48 * np.cos(a) for a in np.radians([30, 90, 150, 210, 330])]
        by = [cy for cy in [1.75 + 0.48 * np.sin(a) for a in np.radians([30, 90, 150, 210, 330])]]
        signs(ax, list(zip(bx, by))[:nb], "+", r=0.085)
        # rod signs sit left of the rod, inside the case and clear of the insulator
        rp = [(cx - 0.22, 0.5), (cx - 0.22, 0.2), (cx - 0.22, -0.1)][:nr]
        signs(ax, rp, "+", r=0.085)
        th = np.radians(ang)
        # needle signs sit on the side of the scale, pitch 0.2, radius from the pivot below the scale arc (0.72)
        needle_pts = [
            (P[0] + t * np.sin(th) + 0.19 * np.cos(th), P[1] + t * np.cos(th) - 0.19 * np.sin(th))
            for t in (0.2, 0.4, 0.6)
        ][:nn]
        signs(ax, needle_pts, "+", r=0.075, fs=8)
        if rod_sign:
            ax.add_patch(
                FancyBboxPatch((cx - 0.75, 3.02), 1.5, 0.42, boxstyle="round,pad=0.02,rounding_size=0.1",
                               fc=EBONITE if rod_sign == "-" else GLASS, ec=INK, lw=1.2, zorder=2)
            )
            signs(ax, [(cx + d, 3.23) for d in (-0.45, 0, 0.45)], rod_sign, r=0.11, fs=10)
        ax.text(cx, -1.95, title, ha="center", va="top", fontsize=10)
    fig.tight_layout()
    save(fig, "charge-electrometer-sign.png")


def induction():
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    blank(ax, (-2.3, 15.6), (-2.9, 3.6))
    steps = [
        (0.0, "1. палочка +, шары\nсоединены проводником", True, True),
        (5.3, "2. проводник убран,\nпалочка ещё рядом", False, True),
        (10.6, "3. палочка убрана: заряды\nпротивоположны и равны", False, False),
    ]
    for x0, title, wire, rodp in steps:
        xa, xb = x0, x0 + 2.4
        angle_left, angle_right = (30, 30) if True else (0, 0)
        for cx, sg in ((xa, "-"), (xb, "+")):
            P, tip = draw_electrometer(ax, cx, 30)
        # ball charges
        # ball signs at 90, 200 and -20 degrees keep clear of the wire, which leaves each ball at its side point
        signs(ax, [(xa + 0.5 * np.cos(a), 1.75 + 0.5 * np.sin(a)) for a in np.radians([90, 200, -20])], "-", r=0.085)
        signs(ax, [(xa + 0.2, 0.7), (xa - 0.2, 0.3)], "-", r=0.085)
        signs(ax, [(xb + 0.5 * np.cos(a), 1.75 + 0.5 * np.sin(a)) for a in np.radians([90, 200, -20])], "+", r=0.085)
        signs(ax, [(xb + 0.2, 0.7), (xb - 0.2, 0.3)], "+", r=0.085)
        if wire:
            ax.plot([xa + 0.34, xa + 0.34, xb - 0.34, xb - 0.34], [1.75, 2.3, 2.3, 1.75], color=INK, lw=2.4, zorder=1)
            ax.plot([xa, xa + 0.34], [1.75, 1.75], color=INK, lw=0.0)
        if rodp:
            rx = xa - 1.2
            ax.add_patch(
                FancyBboxPatch((rx - 0.25, 1.1), 0.5, 1.55, boxstyle="round,pad=0.02,rounding_size=0.1", fc=GLASS, ec=INK, lw=1.2, zorder=2)
            )
            signs(ax, [(rx, y) for y in (1.4, 1.9, 2.4)], "+", r=0.11, fs=10)
        ax.text(x0 + 1.2, -1.75, title, ha="center", va="top", fontsize=9.5)
    fig.tight_layout()
    save(fig, "charge-induction.png")


def draw_pendulum_case(ax, cx, panel, a_init, a_fin, sgn, title, wrong=False, d=0.35):
    L = 1.0
    ax.plot([cx - 0.75, cx + 0.75], [0, 0], color=INK, lw=3)
    for k in range(-3, 4):
        ax.plot([cx + 0.24 * k, cx + 0.24 * k - 0.1], [0, 0.12], color=INK, lw=1)
    pivots = (cx - d, cx + d)
    for i in range(2):
        px = pivots[i]
        ai, af = np.radians(a_init[i]), np.radians(a_fin[i])
        bi = (px + L * np.sin(ai), -L * np.cos(ai))
        bf = (px + L * np.sin(af), -L * np.cos(af))
        ax.plot([px, bi[0]], [0, bi[1]], color=GREY, lw=1.2, ls="--", zorder=1)
        ax.add_patch(Circle(bi, 0.08, fc="none", ec=GREY, lw=1.1, ls="--", zorder=1))
        ax.plot([px, bf[0]], [0, bf[1]], color=INK, lw=1.8, zorder=2)
        s = sgn[i]
        ax.add_patch(Circle(bf, 0.1, fc=POS_FILL if s == "+" else NEG_FILL, ec=INK, lw=1.3, zorder=3))
        ax.text(bf[0], bf[1] - 0.006, str(i + 1), ha="center", va="center", fontsize=8, zorder=6)
        # sign goes on the side the ball moved to, away from its dashed initial position
        side = 1 if bf[0] >= bi[0] else -1
        sign(ax, bf[0] + side * 0.3, bf[1] + 0.02, s, r=0.09)
        # electric force from the plate
        attracted = abs(a_fin[i]) < abs(a_init[i]) if not (panel == "в") else (i == 1)
        up = not attracted
        y0 = bf[1] - 0.16 if not up else bf[1] + 0.16
        y1 = y0 - 0.32 if not up else y0 + 0.32
        arrow(ax, (bf[0], y0), (bf[0], y1), color=GREEN, lw=1.8, ms=11)
    # plate
    ax.add_patch(Rectangle((cx - 1.3, -1.72), 2.6, 0.14, fc=EBONITE, ec=INK, lw=1.2))
    signs(ax, [(cx + x, -1.65) for x in np.linspace(-1.0, 1.0, 6)], "-", r=0.05, fs=6)
    ax.text(cx, -2.0, title, ha="center", va="top", fontsize=10.5, color=POS if wrong else INK)


def gilfgat_94():
    fig, ax = plt.subplots(figsize=(11.6, 3.9))
    blank(ax, (-1.6, 12.0), (-2.6, 0.3))
    draw_pendulum_case(ax, 0.0, "а", (-32, 32), (-18, 18), ("+", "+"), "а) шарики положительны")
    draw_pendulum_case(ax, 3.2, "б", (-32, 32), (-50, 16), ("-", "+"), "б) ошибка: противоречие", wrong=True)
    draw_pendulum_case(ax, 6.4, "в", (12, -12), (26, -6), ("-", "+"), "в) шарики разноимённые", d=0.6)
    draw_pendulum_case(ax, 9.6, "г", (-32, 32), (-52, 52), ("-", "-"), "г) шарики отрицательны")
    fig.tight_layout()
    save(fig, "charge-gilfgat-9-4.png")


# ---------------------------------------------------------------------------
# Lesson 141


def neutron_decay():
    fig, ax = plt.subplots(figsize=(8.0, 2.6))
    blank(ax, (-0.5, 12.5), (-1.9, 1.9))
    def part(x, name, q, col):
        ax.add_patch(Circle((x, 0.2), 0.72, fc=col, ec=INK, lw=1.4))
        ax.text(x, 0.2, name, ha="center", va="center", fontsize=15, fontweight="bold", color=PAPER if col not in (LIGHT,) else INK)
        ax.text(x, -1.15, q, ha="center", va="top", fontsize=11)
    part(1.0, "n", r"$q=0$", GREY)
    arrow(ax, (2.2, 0.2), (3.6, 0.2), lw=2.4, ms=17)
    part(5.0, "p", r"$q=+e$", POS)
    ax.text(6.4, 0.2, "+", ha="center", va="center", fontsize=18)
    part(7.8, r"$e^{-}$", r"$q=-e$", NEG)
    ax.text(9.2, 0.2, "+", ha="center", va="center", fontsize=18)
    part(10.6, r"$\tilde{\nu}$", r"$q=0$", GREY)
    ax.text(6.0, 1.75, r"$0 \;=\; (+e) + (-e) + 0$", ha="center", fontsize=13, color=GREEN)
    fig.tight_layout()
    save(fig, "charge-neutron-decay.png")


def draw_sphere(ax, x, y, r, label, color):
    ax.add_patch(Circle((x, y), r, fc=color, ec=INK, lw=1.4, zorder=2))
    ax.text(x, y, label, ha="center", va="center", fontsize=11, zorder=4)


def task686_scheme():
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    blank(ax, (-1.0, 9.4), (-3.3, 1.3))  # left limit leaves room for the arrowhead at x=-0.75
    # before
    draw_sphere(ax, 1.0, 0.0, 0.5, r"$q$", POS_FILL)
    draw_sphere(ax, 4.0, 0.0, 0.5, r"$4q$", POS_FILL)
    arrow(ax, (0.4, 0), (-0.35, 0), color=GREEN, lw=2.2, ms=14)
    arrow(ax, (4.6, 0), (5.35, 0), color=GREEN, lw=2.2, ms=14)
    ax.annotate("", xy=(4.0, -0.95), xytext=(1.0, -0.95), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    ax.text(2.5, -1.15, r"$r$", ha="center", va="top", fontsize=12)
    ax.text(2.5, 0.9, "до контакта: сила $F$", ha="center", fontsize=10.5)
    # after
    draw_sphere(ax, 0.625, -2.2, 0.5, r"$q'$", POS_FILL)
    draw_sphere(ax, 4.375, -2.2, 0.5, r"$q'$", POS_FILL)
    ax.annotate("", xy=(4.375, -3.0), xytext=(0.625, -3.0), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    ax.text(2.5, -3.15, r"$x=\frac{5}{4}r$", ha="center", va="top", fontsize=12)
    arrow(ax, (0.0, -2.2), (-0.75, -2.2), color=GREEN, lw=2.2, ms=14)
    arrow(ax, (5.0, -2.2), (5.75, -2.2), color=GREEN, lw=2.2, ms=14)
    ax.text(7.7, 0.0, "сумма зарядов\n$5q$", ha="center", va="center", fontsize=11)
    ax.text(7.7, -2.2, "после контакта:\n$q'=\\frac{5q}{2}$, сила $F'=F$", ha="center", va="center", fontsize=11)
    fig.tight_layout()
    save(fig, "charge-task686-scheme.png")


def task686_plot():
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    a = np.logspace(-1.3, 1.5, 300)
    ax.plot(a, (1 + a) / (2 * np.sqrt(a)), color=NEG, lw=2.4)
    ax.axhline(1, color=GREY, lw=1, ls="--")
    ax.plot([1], [1], "o", color=GREEN, ms=8)
    ax.plot([4], [1.25], "o", color=POS, ms=9)
    ax.annotate(r"$\alpha=4$: $x=\frac{5}{4}r$", (4, 1.25), (4.6, 0.86), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(r"$\alpha=1$: $x=r$", (1, 1), (0.14, 0.86), fontsize=10.5, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xscale("log")
    ax.set_ylim(0.7, 3.2)
    ax.set_xlabel(r"$\alpha = q_2/q_1$")
    ax.set_ylabel(r"$x/r$")
    ax.grid(color=GRID, lw=0.8)
    ax.set_title("Расстояние, на которое разводят шарики")
    save(fig, "charge-task686-plot.png")


def task684_plot():
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ap = np.linspace(0.15, 10, 400)
    an = np.linspace(-10, -0.15, 400)
    for a in (ap, an):
        ax.plot(a, (a + 1) ** 2 / (4 * np.abs(a)), color=NEG, lw=2.4)
    ax.axhline(1, color=GREY, lw=1, ls="--")
    ax.axvline(0, color=GREY, lw=1)
    pts = [(5, 1.8, POS, r"$\alpha=5$: $1{,}8$", (6.0, 1.3)), (-5, 0.8, POS, r"$\alpha=-5$: $0{,}8$", (-9.6, 0.9)),
           (1, 1.0, GREEN, r"$\alpha=1$: $1$", (1.8, 0.4)), (-1, 0.0, GREEN, r"$\alpha=-1$: $0$", (-4.5, 0.3))]
    for x, y, c, t, xt in pts:
        ax.plot([x], [y], "o", color=c, ms=8, zorder=5)
        ax.annotate(t, (x, y), xt, fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_ylim(-0.1, 3.6)
    ax.set_xlabel(r"$\alpha = q_2/q_1$")
    ax.set_ylabel(r"$F'/F$")
    ax.grid(color=GRID, lw=0.8)
    ax.set_title("Изменение силы после контакта шариков")
    save(fig, "charge-task684-plot.png")


# ---------------------------------------------------------------------------
# Lesson 137


def _trace(charges, start, sgn, xlim, ylim, h=0.03, nmax=4000):
    pts = [np.array(start, float)]
    p = pts[0].copy()
    for _ in range(nmax):
        E = np.zeros(2)
        for (cx, cy, q) in charges:
            d = p - np.array([cx, cy])
            r = np.hypot(*d)
            if r < 0.11 and q * sgn < 0:
                return np.array(pts)
            E += q * d / r**3
        n = np.hypot(*E)
        if n == 0:
            break
        p = p + sgn * h * E / n
        pts.append(p.copy())
        if not (xlim[0] < p[0] < xlim[1] and ylim[0] < p[1] < ylim[1]):
            break
    return np.array(pts)


def field_lines(ax, charges, nlines=12, xlim=(-3, 3), ylim=(-2.2, 2.2), r0=0.14, phase=0.0):
    """Lines start on a ring of nlines points around every charge, turned by phase.

    A line traced backwards from a negative charge that ends on a positive one repeats a line
    already drawn from that positive charge, so only the lines that leave the window are kept.
    A phase of pi/12 keeps lines off the axis, where they would meet the null point of two like charges.
    """
    for (cx, cy, q) in charges:
        for a in np.linspace(0, 2 * np.pi, nlines, endpoint=False) + phase:
            start = (cx + r0 * np.cos(a), cy + r0 * np.sin(a))
            sgn = 1 if q > 0 else -1
            pts = _trace(charges, start, sgn, xlim, ylim)
            if len(pts) < 3:
                continue
            if q < 0 and len(charges) > 1:
                ends_on_plus = any(
                    q2 > 0 and np.hypot(pts[-1][0] - x2, pts[-1][1] - y2) < 0.2 for (x2, y2, q2) in charges
                )
                if ends_on_plus:
                    continue
            ax.plot(pts[:, 0], pts[:, 1], color=INK, lw=1.1, zorder=1)
            k = len(pts) // 2 if sgn > 0 else len(pts) // 2
            k = max(1, min(k, len(pts) - 2))
            d = (pts[k + 1] - pts[k]) * sgn
            ax.annotate("", xy=pts[k] + d * 0.5, xytext=pts[k] - d * 0.5,
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=11), zorder=2)
    for (cx, cy, q) in charges:
        sign(ax, cx, cy, "+" if q > 0 else "-", r=0.16, fs=12)


def field_lines_fig():
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 6.4))
    xlim, ylim = (-3, 3), (-2.2, 2.2)
    cases = [
        ("положительный заряд", [(0, 0, 1)]),
        ("отрицательный заряд", [(0, 0, -1)]),
        ("два разноимённых заряда", [(-1.1, 0, 1), (1.1, 0, -1)]),
        ("два одноимённых заряда", [(-1.1, 0, 1), (1.1, 0, 1)]),
    ]
    for ax, (title, ch) in zip(axes.flat, cases):
        blank(ax, xlim, ylim)
        ax.set_title(title, fontsize=11, pad=2)
        if title == "отрицательный заряд":
            # lines come from infinity: trace backwards from ring around the charge
            for a in np.linspace(0, 2 * np.pi, 12, endpoint=False):
                start = (0.14 * np.cos(a), 0.14 * np.sin(a))
                pts = _trace(ch, start, -1, xlim, ylim)
                ax.plot(pts[:, 0], pts[:, 1], color=INK, lw=1.1, zorder=1)
                k = max(1, len(pts) // 2)
                d = (pts[k] - pts[k + 1])
                ax.annotate("", xy=pts[k] + d * 0.5, xytext=pts[k] - d * 0.5,
                            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=11), zorder=2)
            sign(ax, 0, 0, "-", r=0.16, fs=12)
        else:
            like = len(ch) > 1 and ch[0][2] == ch[1][2]
            field_lines(ax, ch, xlim=xlim, ylim=ylim, phase=np.pi / 12 if like else 0.0)
    fig.tight_layout()
    save(fig, "field-lines-point-charges.png")


def field_action_theories():
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.2))
    ax = axes[0]
    blank(ax, (-0.5, 6.7), (-1.9, 2.1))
    ax.set_title("дальнодействие", fontsize=11.5, pad=0)
    sign(ax, 0.8, 0, "+", r=0.28, fs=14)
    sign(ax, 5.2, 0, "+", r=0.28, fs=14)
    ax.plot([1.2, 4.8], [0, 0], color=GREY, lw=1.6, ls=":")
    ax.text(3.0, 0.35, "заряд действует прямо на заряд,\nмежду ними ничего нет", ha="center", fontsize=9.5, color=GREY)
    arrow(ax, (5.6, 0), (6.5, 0), color=GREEN, lw=2.2, ms=14)
    ax.text(6.05, 0.3, r"$\vec F$", ha="center", fontsize=12, color=GREEN)
    ax = axes[1]
    blank(ax, (-1.0, 6.7), (-1.9, 2.1))
    ax.set_title("близкодействие", fontsize=11.5, pad=0)
    # outer field circle reaches x=2.0, the caption starts right of it
    for r in (0.5, 0.85, 1.2):
        ax.add_patch(Circle((0.8, 0), r, fc="none", ec=POS, lw=1.0, ls="--", alpha=0.55))
    sign(ax, 0.8, 0, "+", r=0.28, fs=14)
    sign(ax, 5.2, 0, "+", r=0.28, fs=14)
    ax.plot([2.5, 4.8], [0, 0], color=POS, lw=1.0, ls="--", alpha=0.55)
    ax.text(3.7, 0.55, "первый заряд создаёт поле,\nполе действует на второй", ha="center", fontsize=9.5, color=POS)
    arrow(ax, (5.6, 0), (6.5, 0), color=GREEN, lw=2.2, ms=14)
    ax.text(6.05, 0.3, r"$\vec F$", ha="center", fontsize=12, color=GREEN)
    fig.tight_layout()
    save(fig, "field-action-theories.png")


def field_force_delay():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.2), sharey=True)
    t0, dt = 3.0, 2.0
    t = np.linspace(0, 10, 1000)
    F0 = 1.0
    titles = ["дальнодействие", "близкодействие"]
    for ax, title, delay in zip(axes, titles, (0.0, dt)):
        F = np.where(t < t0 + delay, F0, 0.0)
        ax.plot(t, F, color=NEG, lw=2.6)
        ax.axvline(t0, color=GREY, lw=1.2, ls="--")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel(r"$t$")
        ax.set_xticks([t0] if delay == 0 else [t0, t0 + delay])
        ax.set_xticklabels([r"$t_0$"] if delay == 0 else [r"$t_0$", r"$t_0+\frac{r}{v}$"])
        ax.set_ylim(-0.1, 1.35)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["0", r"$F$"])
        ax.grid(color=GRID, lw=0.8)
        if delay:
            ax.annotate("", xy=(t0 + delay, 0.55), xytext=(t0, 0.55), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.5))
            ax.text(t0 + delay / 2, 0.62, "задержка", ha="center", fontsize=9.5, color=GREEN)
    axes[0].set_ylabel("сила на второй заряд")
    fig.suptitle(r"Первый заряд убрали в момент $t_0$", y=1.02, fontsize=11.5)
    fig.tight_layout()
    save(fig, "field-force-delay.png")


def field_probe():
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    xlim, ylim = (-1.4, 6.6), (-2.0, 2.0)
    blank(ax, xlim, ylim)
    field_lines(ax, [(0, 0, 1)], nlines=10, xlim=xlim, ylim=ylim)
    ax.text(0, -0.55, r"$Q$", ha="center", fontsize=12)
    # probe positive (up-right), probe negative (lower right)
    sign(ax, 3.3, 1.0, "+", r=0.16, fs=11)
    ax.text(3.3, 1.35, "пробный $+q$", ha="center", fontsize=9.5)
    arrow(ax, (3.5, 1.0), (4.5, 1.0 + 0.32), color=GREEN, lw=2.2, ms=14)
    ax.text(4.55, 1.25, r"$\vec F$", fontsize=12, color=GREEN)
    sign(ax, 3.3, -1.0, "-", r=0.16, fs=11)
    ax.text(3.3, -1.42, "пробный $-q$", ha="center", fontsize=9.5)
    arrow(ax, (3.1, -1.0), (2.2, -0.66), color=GREEN, lw=2.2, ms=14)
    ax.text(2.0, -0.6, r"$\vec F$", fontsize=12, color=GREEN, ha="right")
    fig.tight_layout()
    save(fig, "field-probe-charge.png")


def field_mutual():
    fig, ax = plt.subplots(figsize=(8.0, 3.6))
    xlim, ylim = (-1.6, 9.0), (-2.5, 1.8)
    blank(ax, xlim, ylim)
    for cx in (1.5, 6.5):
        for r in (0.6, 1.0, 1.4):
            ax.add_patch(Circle((cx, 0), r, fc="none", ec=POS, lw=0.9, ls="--", alpha=0.5))
    sign(ax, 1.5, 0, "+", r=0.26, fs=13)
    sign(ax, 6.5, 0, "+", r=0.26, fs=13)
    ax.text(1.5, 1.55, r"$q_1$", ha="center", fontsize=12)
    ax.text(6.5, 1.55, r"$q_2$", ha="center", fontsize=12)
    arrow(ax, (6.9, 0), (8.3, 0), color=GREEN, lw=2.4, ms=15)
    # force labels lie outside the dashed field circles (radius 1.4)
    ax.text(8.4, 0.6, r"$\vec F_{12}$", fontsize=12, color=GREEN, ha="center")
    arrow(ax, (1.1, 0), (-0.3, 0), color=GREEN, lw=2.4, ms=15)
    ax.text(-0.4, 0.6, r"$\vec F_{21}$", fontsize=12, color=GREEN, ha="center")
    ax.text(6.5, -1.9, "на $q_2$ действует\nполе заряда $q_1$", ha="center", fontsize=10)
    ax.text(1.5, -1.9, "на $q_1$ действует\nполе заряда $q_2$", ha="center", fontsize=10)
    fig.tight_layout()
    save(fig, "field-mutual-action.png")


def charge_sharing():
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    blank(ax, (-0.8, 10.6), (-5.0, 1.0))
    rows = [
        (0.0, ["$q$", "$0$"]),
        (-1.5, [r"$\frac{q}{2}$", r"$\frac{q}{2}$"]),
        (-3.0, [r"$\frac{q}{4}$", r"$0$"]),
        (-4.3, [r"$\frac{q}{8}$", r"$\frac{q}{8}$"]),
    ]
    caps = [
        "заряжен один электрометр",
        "соединили проводником",
        "второй разрядили, снова соединили: $\\frac q4$ и $\\frac q4$",
        "и так далее",
    ]
    for (y, labs), cap in zip(rows, caps):
        pass
    y = 0.0
    sequence = [
        ("электрометры одинаковые, заряжен первый", ["$q$", "0"]),
        ("соединили: заряд поделился поровну", [r"$\frac{q}{2}$", r"$\frac{q}{2}$"]),
        ("второй разрядили, снова соединили", [r"$\frac{q}{4}$", r"$\frac{q}{4}$"]),
        ("ещё раз", [r"$\frac{q}{8}$", r"$\frac{q}{8}$"]),
    ]
    for i, (cap, labs) in enumerate(sequence):
        yy = -i * 1.4
        draw_sphere(ax, 1.5, yy, 0.5, labs[0], POS_FILL if labs[0] != "0" else LIGHT)
        draw_sphere(ax, 4.0, yy, 0.5, labs[1], POS_FILL if labs[1] != "0" else LIGHT)
        if i in (1, 2, 3):
            ax.plot([2.0, 3.5], [yy, yy], color=INK, lw=2.4, zorder=1)
        ax.text(5.0, yy, cap, va="center", fontsize=10)
    fig.tight_layout()
    save(fig, "field-charge-sharing.png")


def halving_graph():
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    n = np.arange(0, 11)
    q = 1024 / 2**n
    ax.bar(n, q, color=NEG, alpha=0.85, zorder=3)
    ax.axhline(1, color=POS, lw=1.6, ls="--", zorder=4)
    ax.annotate("$e$ — наименьший заряд,\nдальше делить нельзя", (10.0, 1.15), (9.6, 90),
                fontsize=10, color=POS, ha="right", arrowprops=dict(arrowstyle="-|>", color=POS))
    ax.set_yscale("log")
    ax.set_ylim(0.1, 2500)
    ax.set_xticks(n)
    ax.set_xlabel("число делений пополам")
    ax.set_ylabel(r"заряд, в единицах $e$")
    ax.grid(color=GRID, lw=0.8, zorder=0, axis="y")
    ax.set_title(r"Деление заряда $q = 1024\,e$ (модельный пример)")
    save(fig, "field-halving-graph.png")


def charge_discrete():
    rng = np.random.default_rng(11)
    N0 = 3000
    steps = rng.poisson(1.0, size=6000)
    # leakage: electrons leave one by one; charge decreases roughly exponentially
    q = [N0]
    t = [0.0]
    cur = N0
    tt = 0.0
    while cur > 0 and tt < 60:
        rate = cur / 25.0
        tt += rng.exponential(1.0 / rate)
        cur -= 1
        t.append(tt)
        q.append(cur)
    t, q = np.array(t), np.array(q)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.step(t, q, where="post", color=NEG, lw=1.2)
    ax.set_xlabel("время")
    ax.set_ylabel(r"заряд, в единицах $e$")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, N0 * 1.05)
    ax.grid(color=GRID, lw=0.8)
    ax.set_title("Разрядка электрометра: издали плавно, вблизи ступенями")
    ins = ax.inset_axes([0.5, 0.42, 0.44, 0.44])
    i0 = np.searchsorted(t, 10.0)
    sl = slice(i0, i0 + 9)
    ins.step(t[sl], q[sl], where="post", color=NEG, lw=1.8)
    ins.plot(t[sl], q[sl], "o", color=NEG, ms=3)
    ins.set_xticks([])
    ins.set_yticks(list(range(int(q[sl].min()), int(q[sl].max()) + 1))[::2])
    ins.tick_params(labelsize=7)
    ins.set_title("ступени высотой $e$", fontsize=8.5)
    ax.indicate_inset_zoom(ins, edgecolor=GREY)
    save(fig, "field-charge-discrete.png")


def capacitor_setup(ax, kind):
    blank(ax, (-0.5, 9.8), (-2.6, 3.2))
    ax.add_patch(Rectangle((1.6, -1.6), 5.6, 3.2, fc=SOFT, ec=INK, lw=1.6, zorder=0))
    # plates
    # the upper plate has a hole at x=4.15..4.45 for the tube
    ax.add_patch(Rectangle((2.0, 0.95), 2.15, 0.16, fc=GOLD, ec=INK, lw=1.2, zorder=2))
    ax.add_patch(Rectangle((4.45, 0.95), 2.35, 0.16, fc=GOLD, ec=INK, lw=1.2, zorder=2))
    ax.add_patch(Rectangle((2.0, -1.11), 4.8, 0.16, fc=GOLD, ec=INK, lw=1.2, zorder=2))
    # charges sit on the facing sides of the plates, clear of the particle at x=4.3 and of its labels
    xs_sign = [2.4, 3.1, 3.8, 5.5, 6.2]
    signs(ax, [(x, 0.8) for x in xs_sign], "-", r=0.12, fs=8)
    signs(ax, [(x, -0.8) for x in xs_sign], "+", r=0.12, fs=8)
    # open tube: filled strip and two walls, so the hole in the plate stays open
    ax.add_patch(Rectangle((4.15, 0.95), 0.3, 1.76, fc=tint(COPPER, 0.3), ec="none", zorder=1))
    ax.plot([4.15, 4.15], [1.11, 2.71], color=INK, lw=1.2, zorder=1)
    ax.plot([4.45, 4.45], [1.11, 2.71], color=INK, lw=1.2, zorder=1)
    ax.annotate("", xy=(4.3, 1.2), xytext=(4.3, 3.0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, ls=":"))
    ax.text(4.3, 3.15, "пылинки цинка" if kind == "ioffe" else "капельки масла", ha="center", fontsize=10)
    # particle
    ax.add_patch(Circle((4.3, 0.0), 0.15, fc=POS, ec=INK, lw=1.2, zorder=6))
    arrow(ax, (4.3, 0.2), (4.3, 0.95), color=GREEN, lw=2.2, ms=13, z=7)
    arrow(ax, (4.3, -0.2), (4.3, -0.95), color=INK, lw=2.2, ms=13, z=7)
    ax.text(4.5, 0.6, r"$F_{\mathrm{эл}}$", fontsize=11, color=GREEN)
    ax.text(4.5, -0.75, r"$mg$", fontsize=11)
    # microscope
    ax.add_patch(Rectangle((7.2, -0.3), 1.6, 0.6, fc=LIGHT, ec=INK, lw=1.4, zorder=1))
    ax.add_patch(Polygon([[7.2, -0.3], [7.2, 0.3], [6.9, 0.45], [6.9, -0.45]], fc=LIGHT, ec=INK, lw=1.2))
    ax.text(8.0, -0.75, "микроскоп", ha="center", fontsize=9.5)
    # source
    if kind == "ioffe":
        ax.add_patch(Circle((-0.1, 0.0), 0.35, fc=GOLD, ec=INK, lw=1.2))
        for dy in (-0.5, 0, 0.5):
            arrow(ax, (0.5, dy), (1.5, dy), color=VIOLET, lw=1.6, ms=11)
        ax.text(0.5, -1.15, "ультрафиолет", ha="center", fontsize=9.5, color=VIOLET)
        ax.text(4.4, -2.2, "к вакуумному насосу", ha="center", fontsize=9.5, color=GREY)
        ax.plot([4.3, 4.3], [-1.6, -2.05], color=GREY, lw=2)
    else:
        ax.add_patch(Polygon([[3.7, 2.7], [4.9, 2.7], [4.3, 2.0]], fc="none", ec="none"))
        ax.add_patch(Circle((-0.1, 0.0), 0.35, fc=tint(INK, 0.85), ec=INK, lw=1.2))
        for dy in (-0.5, 0, 0.5):
            arrow(ax, (0.5, dy), (1.5, dy), color=GREY, lw=1.3, ms=10, ls="--")
        ax.text(0.5, -1.15, "рентген\n(не обязателен)", ha="center", fontsize=9, color=GREY)
        ax.text(5.3, 2.4, "капли электризуются\nпри отрыве от пульверизатора", ha="left", fontsize=9.3, color=INK)


def ioffe_setup():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    capacitor_setup(ax, "ioffe")
    ax.set_title("Опыт Иоффе: пылинка в плоском конденсаторе", fontsize=11, pad=18)
    save(fig, "field-ioffe-setup.png")


def millikan_setup():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    capacitor_setup(ax, "millikan")
    ax.set_title("Опыт Милликена: капля масла в конденсаторе", fontsize=11, pad=18)
    save(fig, "field-millikan-setup.png")


def millikan_forces():
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.6))
    cases = [
        ("поля нет: капля падает\nравномерно", [(-1, "mg"), (1, "Fc")], "F"),
        ("подобрали поле: капля\nвисит", [(-1, "mg"), (1, "Fe")], "H"),
        ("поле больше: капля ползёт\nвверх равномерно", [(-1, "mg"), (-1, "Fc"), (1, "Fe")], "U"),
    ]
    for ax, (title, forces, kind) in zip(axes, cases):
        blank(ax, (-2.2, 2.2), (-2.4, 2.6))
        ax.set_title(title, fontsize=10.2, pad=2)
        ax.add_patch(Circle((0, 0), 0.24, fc=POS, ec=INK, lw=1.3, zorder=5))
        # forces
        down = [f for f in forces if f[0] < 0]
        up = [f for f in forces if f[0] > 0]
        lab = {"mg": r"$m\vec g$", "Fc": r"$\vec F_{\mathrm{сопр}}$", "Fe": r"$\vec F_{\mathrm{эл}}$"}
        col = {"mg": INK, "Fc": NEG, "Fe": GREEN}
        length = {"mg": 1.4, "Fc": None, "Fe": None}
        if kind == "F":
            L = {"mg": 1.4, "Fc": 1.4}
        elif kind == "H":
            L = {"mg": 1.4, "Fe": 1.4}
        else:
            L = {"mg": 1.0, "Fc": 0.6, "Fe": 1.6}
        offs = {"mg": 0.0, "Fc": 0.0, "Fe": 0.0}
        # place multiple downward forces side by side
        xs = {"mg": -0.4, "Fc": 0.4, "Fe": 0.0}
        if kind != "U":
            xs = {"mg": 0.0, "Fc": 0.0, "Fe": 0.0}
        for name in ("mg", "Fc", "Fe"):
            if name not in L:
                continue
            is_up = name == "Fc" and kind == "F" or name == "Fe"
            x = xs[name]
            if is_up:
                arrow(ax, (x, 0.28), (x, 0.28 + L[name]), color=col[name], lw=2.4, ms=15, z=6)
                ax.text(x + 0.2, 0.28 + L[name] * 0.75, lab[name], fontsize=11, color=col[name])
            else:
                arrow(ax, (x, -0.28), (x, -0.28 - L[name]), color=col[name], lw=2.4, ms=15, z=6)
                ax.text(x + 0.2, -0.28 - L[name] * 0.8, lab[name], fontsize=11, color=col[name])
        v = {"F": -1, "H": 0, "U": 1}[kind]
        if v:
            arrow(ax, (1.7, 0.0), (1.7, 0.8 * v), color=GREY, lw=1.8, ms=12, style="->")
            ax.text(1.5, 0.9 * v + (0.1 if v > 0 else -0.25), r"$\vec v$", fontsize=11, color=GREY, ha="center")
        else:
            ax.text(1.7, 0.0, r"$v=0$", fontsize=10, color=GREY, ha="center", va="center")
        ax.text(0, -2.45, r"$\vec F_{\mathrm{равн}}=0$", ha="center", fontsize=10.5)
    fig.tight_layout()
    save(fig, "field-millikan-forces.png")


def charge_histogram():
    rng = np.random.default_rng(7)
    e = 1.602
    n = rng.choice([1, 2, 3, 4, 5, 6, 7, 8], size=220, p=[0.10, 0.20, 0.24, 0.18, 0.12, 0.08, 0.05, 0.03])
    q = n * e + rng.normal(0, 0.09, size=n.size)
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    ax.hist(q, bins=np.arange(0.4, 13.6, 0.16), color=NEG, alpha=0.9, zorder=3)
    for k in range(1, 9):
        ax.axvline(k * e, color=GREY, lw=0.9, ls="--", zorder=1)
        ax.text(k * e, ax.get_ylim()[1] * 1.0, f"{k}e", ha="center", va="bottom", fontsize=8.5, color=GREY)
    ax.axvspan(0.62, 1.4, color=POS, alpha=0.12, zorder=0)
    ax.text(1.0, 6, "здесь\nзарядов\nнет", ha="center", fontsize=8.5, color=POS)
    ax.set_xlabel(r"измеренный заряд капли, $10^{-19}$ Кл")
    ax.set_ylabel("число капель")
    ax.set_xlim(0, 13.6)
    ax.grid(color=GRID, lw=0.8, axis="y", zorder=0)
    ax.set_title("Заряды капель группируются около $ne$ (модельные данные)", pad=16)
    save(fig, "field-charge-histogram.png")


if __name__ == "__main__":
    gravity_vs_electric()
    tribo_series()
    interaction()
    rubbing_separation()
    conductors_dielectrics()
    electroscope()
    electrometer()
    electrometer_sign()
    induction()
    gilfgat_94()
    neutron_decay()
    task686_scheme()
    task686_plot()
    task684_plot()
    field_lines_fig()
    field_action_theories()
    field_force_delay()
    field_probe()
    field_mutual()
    charge_sharing()
    halving_graph()
    charge_discrete()
    ioffe_setup()
    millikan_setup()
    millikan_forces()
    charge_histogram()
