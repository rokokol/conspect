"""Figures for the notes "Давление газа" and "Закон Паскаля" (course Физика 7-9, lessons 45-46).

Run: python3 pressure_gas_pascal.py
PNG files go to content/06. Давление/00. Вложения/, prefixes gas-* and pascal-*.
Colour code as in pressure_solids.py: force red, pressure blue; molecules purple, water light blue.
Curves in gas-p-of-v-hyperbola.png and gas-p-of-t-isochore.png are qualitative: no numbers on the axes.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Ellipse

from course import COURSE

OUT = COURSE / "content" / "06. Давление" / "00. Вложения"
OUT.mkdir(parents=True, exist_ok=True)
NOMEDIA = OUT / ".nomedia"
if not NOMEDIA.exists():
    NOMEDIA.touch()

from theme import ACCENT, BLUE, COPPER, INK, METAL, MUTED, PAPER, RED, SKY, VIOLET, WARM, saver, tint

GREY = MUTED
LIGHT = tint(INK, 0.9)
C_F = RED
C_P = BLUE
MOL = VIOLET
WATER = tint(SKY, 0.7)
WATER_EDGE = SKY
WOOD = tint(COPPER, 0.55)
SMOKE = tint(INK, 0.7)
VESSEL = tint(SKY, 0.92)  # the pale fill of a glass vessel
MEMBRANE = ACCENT
HOT_FILL = tint(RED, 0.55)
COLD_FILL = tint(BLUE, 0.55)
YELLOW_FILL = tint(WARM, 0.6)
LIT = tint(WARM, 0.85)  # a glowing bulb


save = saver(OUT)


def blank(w, h, xlim, ylim, n=1):
    fig, axes = plt.subplots(1, n, figsize=(w, h))
    axes = np.atleast_1d(axes)
    for ax in axes:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
    return fig, axes


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", scale=13, ls="-", z=5):
    ax.add_patch(
        FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=scale, lw=lw, color=color, linestyle=ls, zorder=z)
    )


def line(ax, xs, ys, color=INK, lw=2, z=4, **kw):
    ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle="round", **kw)


def rect(ax, x, y, w, h, fc="none", ec=INK, lw=1.8, z=3, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))


def mol(ax, x, y, r=0.12, fc=MOL, z=6):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=INK, lw=0.6, zorder=z))


def label(ax, x, y, text, fs=11, color=INK, ha="center", va="center", **kw):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, zorder=10, **kw)


def scatter_in(rng, n, x0, x1, y0, y1, min_d=0.34, tries=4000):
    pts = []
    for _ in range(tries):
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > min_d**2 for q in pts):
            pts.append(p)
            if len(pts) == n:
                break
    return pts


def ground_hatch(ax, x0, x1, y, h=0.15):
    line(ax, [x0, x1], [y, y], lw=1.8)
    for x in np.arange(x0 + 0.1, x1, 0.3):
        line(ax, [x, x - 0.14], [y, y - h], color=GREY, lw=1)


# ---------------------------------------------------------------- gas-*


def molecules_hit_wall():
    rng = np.random.default_rng(3)
    fig, (ax,) = blank(5.6, 4.4, (0, 8), (0, 6.2))
    rect(ax, 0.6, 0.6, 6.4, 4.8, lw=2.2)
    ax.add_patch(Rectangle((7.0, 0.6), 0.28, 4.8, fc=LIGHT, ec=INK, lw=1.5, hatch="///", zorder=2))
    pts = scatter_in(rng, 16, 1.0, 6.4, 1.0, 5.0, min_d=0.75)
    for x, y in pts:
        a = rng.uniform(0, 2 * np.pi)
        mol(ax, x, y)
        arrow(ax, (x, y), (x + 0.55 * np.cos(a), y + 0.55 * np.sin(a)), color=MOL, lw=1.3, scale=9)
    # two highlighted impacts on the right wall
    for y0, dy in ((3.9, 0.7), (2.0, -0.8)):
        mol(ax, 6.85, y0, r=0.14, fc=tint(VIOLET, 0.6))
        arrow(ax, (5.3, y0 - dy), (6.75, y0), color=MOL, lw=1.6, scale=11)
        arrow(ax, (6.75, y0), (5.5, y0 + dy), color=MOL, lw=1.6, scale=11, ls="--")
        arrow(ax, (7.45, y0), (7.95, y0), color=C_F, lw=2.2, scale=13)
    label(ax, 7.75, 3.4, r"$\vec F$", fs=13, color=C_F)
    label(ax, 3.8, 5.75, "Газ в сосуде", fs=12)
    label(ax, 7.15, 0.2, "стенка", fs=10, color=GREY)
    save(fig, "gas-molecules-hit-wall.png")


def impacts_analogy():
    rng = np.random.default_rng(5)
    specs = [
        ("Сосновая шишка", 1, 0.32),
        ("Грецкие орехи", 6, 0.17),
        ("Горох", 22, 0.085),
        ("Песок", 90, 0.035),
        ("Воздух", 280, 0.016),
    ]
    fig, axes = blank(11.5, 3.0, (0, 4), (0, 4), n=5)
    hx, hy, ln = 3.2, 3.7, 3.0
    ang = np.radians(14)
    for ax, (name, n, r) in zip(axes, specs):
        line(ax, [hx, hx], [hy, hy - ln], lw=1.2, color=GREY, ls="--")
        line(ax, [hx, hx + ln * np.sin(ang)], [hy, hy - ln * np.cos(ang)], lw=4, color=WOOD)
        ax.plot([hx], [hy], marker="o", color=INK, ms=5, zorder=7)
        pts = scatter_in(rng, n, 0.3, 2.5, 0.9, 3.6, min_d=max(2 * r, 0.02), tries=20000)
        for x, y in pts:
            ax.add_patch(Circle((x, y), r, fc=MOL, ec=INK, lw=0.4 if r > 0.05 else 0, zorder=6, alpha=0.9))
        if n <= 6:
            for x, y in pts:
                arrow(ax, (x + r + 0.05, y), (x + r + 0.5, y), color=C_F, lw=1.2, scale=8)
        label(ax, 1.9, 0.3, name, fs=11)
    save(fig, "gas-impacts-analogy.png")


def balloon_vacuum():
    rng = np.random.default_rng(8)
    fig, axes = blank(9.4, 5.0, (0, 7), (-0.6, 6.4), n=2)
    cases = [
        (0, 46, 1.3, "Под колпаком воздух: удары снаружи и изнутри равны"),
        (1, 8, 1.75, r"Воздух откачан: снаружи $p \approx 0{,}2\,p_\mathrm{атм}$"),
    ]
    for ax, (k, n_out, R, title) in zip(axes, cases):
        line(ax, [0.6, 0.6, 6.4, 6.4], [0.8, 5.6, 5.6, 0.8], lw=2.2, color=GREY)
        ax.add_patch(Rectangle((0.2, 0.55), 6.6, 0.25, fc=METAL, ec=INK, lw=1.6, zorder=3))
        cx, cy = 3.5, 0.8 + R + 0.05
        ax.add_patch(Circle((cx, cy), R, fc=YELLOW_FILL, ec=INK, lw=2, zorder=4, alpha=0.9))
        pts = scatter_in(rng, n_out, 0.9, 6.1, 1.1, 5.3, min_d=0.5)
        for x, y in pts:
            if (x - cx) ** 2 + (y - cy) ** 2 < (R + 0.3) ** 2:
                continue
            mol(ax, x, y, r=0.09)
        rng2 = np.random.default_rng(2)
        inside = scatter_in(rng2, 9, cx - R * 0.6, cx + R * 0.6, cy - R * 0.6, cy + R * 0.6, min_d=0.45)
        for x, y in inside:
            if (x - cx) ** 2 + (y - cy) ** 2 < (R * 0.6) ** 2:
                mol(ax, x, y, r=0.09, z=7)
        for a in np.radians([25, 90, 155, 205, 335]):
            px, py = cx + R * np.cos(a), cy + R * np.sin(a)
            ca, sa = np.cos(a), np.sin(a)
            out_len = 0.85 if k == 0 else 0.5
            arrow(ax, (px + out_len * ca, py + out_len * sa), (px + 0.03 * ca, py + 0.03 * sa), color=C_F, lw=1.8, scale=9)
            arrow(ax, (px - 0.03 * ca, py - 0.03 * sa), (px - 0.55 * ca, py - 0.55 * sa), color=C_P, lw=1.8, scale=9, z=8)
        label(ax, 3.5, 6.05, title, fs=10.5)
        label(ax, 3.5, -0.1, "красные стрелки: удары снаружи, синие: изнутри", fs=9, color=GREY)
    save(fig, "gas-balloon-vacuum.png")


def piston_volume():
    rng = np.random.default_rng(11)
    fig, axes = blank(10.4, 4.9, (0, 9), (-0.7, 6.2), n=3)
    # (piston height y, film shape, title)
    cases = [
        (2.6, 0.0, "Исходный объём", "плёнка плоская"),
        (3.6, +0.55, "Объём меньше", "плёнка выгнулась наружу"),
        (1.5, -0.55, "Объём больше", "плёнка втянулась внутрь"),
    ]
    x0, x1 = 2.0, 5.8
    top = 4.6
    for ax, (py, bulge, t1, t2) in zip(axes, cases):
        line(ax, [x0, x0], [0.5, top], lw=2.2)
        line(ax, [x1, x1], [0.5, top], lw=2.2)
        ax.add_patch(Rectangle((x0, py - 0.18), x1 - x0, 0.18, fc=METAL, ec=INK, lw=1.5, zorder=4))
        line(ax, [3.9, 3.9], [0.4, py - 0.18], lw=3, color=METAL)
        # film
        xs = np.linspace(x0, x1, 60)
        ys = top + bulge * (1 - ((xs - 3.9) / 1.9) ** 2)
        line(ax, xs, ys, color=C_P, lw=2.6)
        # the same 8 molecules in every panel, also in the squeezed one
        pts = scatter_in(np.random.default_rng(4), 8, x0 + 0.3, x1 - 0.3, py + 0.2, top - 0.1 + min(bulge, 0), min_d=0.3)
        assert len(pts) == 8
        for x, y in pts:
            mol(ax, x, y, r=0.13)
        label(ax, 3.9, 5.55, t1, fs=12)
        label(ax, 3.9, -0.3, t2, fs=10, color=C_P)
        # volume bracket
        arrow(ax, (x1 + 0.4, py), (x1 + 0.4, top), style="<|-|>", color=GREY, lw=1.2, scale=9)
        label(ax, x1 + 0.9, (py + top) / 2, r"$V$", fs=12, color=GREY)
    label(axes[0], 3.9, 5.05, "", fs=1)
    save(fig, "gas-piston-volume.png")


def syringe_film():
    fig, axes = blank(9.6, 4.6, (0, 9), (0, 6.6), n=3)
    # plunger position given as volume in mL; scale 0..20 mL over 4 units
    cases = [(15, -1, "15 мл: плёнка втянута"), (12, 0, "около 12 мл: плоская"), (10, +1, "10 мл: плёнка выгнута")]
    for ax, (v, sgn, t) in zip(axes, cases):
        x0, x1 = 3.1, 5.1
        ytop = 5.2
        ybot = 1.2
        rect(ax, x0, ybot, x1 - x0, ytop - ybot, fc=VESSEL, lw=2)
        for m in range(0, 21, 5):
            y = ytop - m * (ytop - ybot) / 20
            line(ax, [x0, x0 + 0.35], [y, y], lw=1.2)
            label(ax, x0 - 0.35, y, str(m), fs=9, color=GREY)
        for m in range(1, 20):
            if m % 5:
                y = ytop - m * (ytop - ybot) / 20
                line(ax, [x0, x0 + 0.2], [y, y], lw=0.8, color=GREY)
        py = ytop - v * (ytop - ybot) / 20
        # plunger below the air, sitting at the level of volume
        ax.add_patch(Rectangle((x0 + 0.02, py - 0.35), x1 - x0 - 0.04, 0.35, fc=METAL, ec=INK, lw=1.4, zorder=4))
        ax.add_patch(Rectangle((4.0, 0.3), 0.2, py - 0.65, fc=METAL, ec=INK, lw=1.2, zorder=3))
        xs = np.linspace(x0, x1, 40)
        ys = ytop + sgn * 0.45 * (1 - ((xs - 4.1) / 1.0) ** 2)
        line(ax, xs, ys, color=MEMBRANE, lw=3)
        label(ax, 4.1, 6.15, t, fs=11)
        # air dots
        pts = scatter_in(np.random.default_rng(6), 7, x0 + 0.4, x1 - 0.2, py + 0.15, ytop - 0.25, min_d=0.32)
        for x, y in pts:
            mol(ax, x, y, r=0.07)
    save(fig, "gas-syringe-film.png")


def p_of_v():
    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    v = np.linspace(0.6, 5.2, 300)
    ax.plot(v, 4.2 / v, color=C_P, lw=2.6, label=r"$T_1$")
    ax.plot(v, 8.4 / v, color=C_F, lw=2.6, label=r"$T_2 > T_1$")
    ax.set_xlim(0, 5.5)
    ax.set_ylim(0, 8.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$V$", fontsize=13)
    ax.set_ylabel(r"$p$", fontsize=13, rotation=0, labelpad=12)
    ax.annotate("", xy=(5.45, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.annotate("", xy=(0, 8.45), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    for vv in (1.0, 2.1, 4.2):
        ax.plot([vv, vv], [0, 4.2 / vv], color=GREY, lw=0.9, ls=":")
        ax.plot([0, vv], [4.2 / vv, 4.2 / vv], color=GREY, lw=0.9, ls=":")
        ax.plot([vv], [4.2 / vv], "o", color=C_P, ms=6)
    ax.annotate(r"$V \downarrow \Rightarrow p \uparrow$", xy=(1.0, 4.2), xytext=(1.5, 6.6), fontsize=12,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.legend(frameon=False, loc="upper right", fontsize=12)
    ax.set_title("p(V) при данной массе газа")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    save(fig, "gas-p-of-v-hyperbola.png")


def p_of_t():
    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    t = np.linspace(0.3, 5.0, 100)
    ax.plot(t, 1.6 + 1.1 * t, color=C_P, lw=2.6, label=r"объём $V_1$")
    ax.plot(t, 0.8 + 0.55 * t, color=C_F, lw=2.6, label=r"объём $V_2 > V_1$")
    ax.set_xlim(0, 5.5)
    ax.set_ylim(0, 8.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$T$", fontsize=13)
    ax.set_ylabel(r"$p$", fontsize=13, rotation=0, labelpad=12)
    ax.annotate("", xy=(5.45, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.annotate("", xy=(0, 8.45), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.annotate(r"$T \uparrow \Rightarrow p \uparrow$", xy=(3.0, 4.9), xytext=(0.5, 6.8), fontsize=12,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.legend(frameon=False, loc="lower right", fontsize=12)
    ax.set_title("p(T) при данных массе и объёме")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    save(fig, "gas-p-of-t-isochore.png")


def temperature_molecules():
    rng = np.random.default_rng(9)
    fig, axes = blank(9.0, 4.4, (0, 8), (0, 5.6), n=2)
    for ax, hot in zip(axes, (False, True)):
        rect(ax, 0.8, 0.9, 6.0, 3.8, lw=2.2)
        pts = scatter_in(rng, 10, 1.2, 6.4, 1.3, 4.3, min_d=0.9)
        for x, y in pts:
            a = rng.uniform(0, 2 * np.pi)
            L = 1.25 if hot else 0.45
            mol(ax, x, y, r=0.13)
            arrow(ax, (x, y), (x + L * np.cos(a), y + L * np.sin(a)), color=C_F if hot else C_P, lw=1.5, scale=10)
        label(ax, 3.8, 5.2, "Высокая температура" if hot else "Низкая температура", fs=12, color=C_F if hot else C_P)
        label(ax, 3.8, 0.35, "быстрее, чаще, сильнее удары" if hot else "медленнее, реже, слабее удары", fs=10.5)
    save(fig, "gas-temperature-molecules.png")


def flask_balloon():
    fig, axes = blank(11.4, 5.2, (0, 9), (-0.2, 8.2), n=3)
    cases = [
        ("Начало: шарик слегка втянут", "in_small", None),
        ("Горячая вода: шарик надулся", "out", HOT_FILL),
        ("Холодная вода: шарик втянут", "in", COLD_FILL),
    ]
    for ax, (t, mode, water) in zip(axes, cases):
        cx, cy, R = 4.5, 1.9, 1.5
        ax.add_patch(Circle((cx, cy), R, fc=VESSEL, ec=INK, lw=2, zorder=3))
        ax.add_patch(Rectangle((cx - 0.3, cy + R - 0.15), 0.6, 1.8, fc=VESSEL, ec=INK, lw=2, zorder=3))
        ax.add_patch(Rectangle((cx - 0.31, cy + R - 0.13), 0.62, 1.78, fc=VESSEL, ec="none", zorder=4))
        ntop = cy + R + 1.65
        # pan with water
        ax.add_patch(Rectangle((1.4, 0.35), 6.2, 1.3, fc=water or PAPER, ec=INK, lw=1.8, zorder=2, alpha=0.75 if water else 1))
        if mode == "out":
            ax.add_patch(Ellipse((cx, ntop + 0.65), 1.6, 1.6, fc=VIOLET, ec=INK, lw=1.8, zorder=5))
        elif mode == "in_small":
            xs = np.linspace(cx - 0.4, cx + 0.4, 30)
            ax.plot(xs, ntop - 0.25 * (1 - ((xs - cx) / 0.4) ** 2), color=VIOLET, lw=4, zorder=5)
        else:
            xs = np.linspace(cx - 0.4, cx + 0.4, 30)
            ax.plot(xs, ntop - 0.75 * (1 - ((xs - cx) / 0.4) ** 2), color=VIOLET, lw=4, zorder=5)
        pts = scatter_in(np.random.default_rng(1), 8, cx - 1.0, cx + 1.0, cy - 1.0, cy + 1.0, min_d=0.5)
        for x, y in pts:
            if (x - cx) ** 2 + (y - cy) ** 2 < 1.1:
                a = np.random.default_rng(int(x * 100)).uniform(0, 6.28)
                L = 0.8 if mode == "out" else 0.55
                mol(ax, x, y, r=0.1, z=6)
                arrow(ax, (x + 0.1 * np.cos(a), y + 0.1 * np.sin(a)), (x + L * np.cos(a), y + L * np.sin(a)), color=C_F if mode == "out" else C_P, lw=1.3, scale=8, z=6)
        label(ax, 4.5, 7.9, t, fs=10.5)
    save(fig, "gas-flask-balloon.png")


def half_gas_cylinder():
    rng = np.random.default_rng(12)
    fig, axes = blank(8.0, 5.9, (0, 7), (-0.5, 7.6), n=2)
    for ax, n, (m, p) in zip(axes, (16, 8), ((r"$m_1$", r"$p_1$"), (r"$m_2 = \dfrac{m_1}{2}$", r"$p_2 = \dfrac{p_1}{2}$"))):
        ax.add_patch(plt.Rectangle((1.6, 0.9), 3.4, 4.6, fc=VESSEL, ec=INK, lw=2.2, zorder=2, joinstyle="round"))
        rect(ax, 2.7, 5.5, 1.2, 0.5, fc=METAL, lw=1.6)
        rect(ax, 3.9, 5.65, 0.5, 0.2, fc=METAL, lw=1.4)
        pts = scatter_in(np.random.default_rng(21 + n), n, 1.9, 4.7, 1.2, 5.2, min_d=0.6)
        for x, y in pts:
            a = rng.uniform(0, 6.28)
            mol(ax, x, y, r=0.11)
            arrow(ax, (x, y), (x + 0.5 * np.cos(a), y + 0.5 * np.sin(a)), color=MOL, lw=1.2, scale=8)
        label(ax, 3.3, 3.2, "", fs=1)
        label(ax, 3.3, 0.35, m, fs=12)
        label(ax, 3.3, 6.75, p, fs=13, color=C_P)
    save(fig, "gas-half-gas-cylinder.png")


# ---------------------------------------------------------------- pascal-*


def solid_liquid_gas():
    rng = np.random.default_rng(14)
    fig, axes = blank(11.4, 5.0, (0, 9), (0, 7.6), n=3)
    x0, x1, ybot, ytop = 1.6, 6.6, 1.0, 4.6
    titles = ["Твёрдое тело", "Жидкость", "Газ"]
    for ax, t in zip(axes, titles):
        line(ax, [x0, x0, x1, x1], [ytop + 0.4, ybot, ybot, ytop + 0.4], lw=2.4)
        ax.add_patch(Rectangle((x0 + 0.05, ytop - 0.15), x1 - x0 - 0.1, 0.3, fc=METAL, ec=INK, lw=1.5, zorder=4))
        rect(ax, 3.55, ytop + 0.2, 1.0, 0.75, fc=METAL, lw=1.6)
        label(ax, 4.05, ytop + 0.58, "гиря", fs=7.5)
        arrow(ax, (4.05, ytop + 1.9), (4.05, ytop + 1.0), color=C_F, lw=2.2)
        label(ax, 4.05, 7.2, t, fs=13)
    ymid = (ybot + ytop) / 2
    # solid: block, arrows only down
    ax = axes[0]
    ax.add_patch(Rectangle((x0 + 0.5, ybot + 0.1), x1 - x0 - 1.0, ytop - ybot - 0.35, fc=WOOD, ec=INK, lw=1.6, hatch="//", zorder=2))
    for x in (2.8, 4.1, 5.4):
        arrow(ax, (x, ybot + 0.6), (x, ybot - 0.65), color=C_P, lw=2.2)
    label(ax, 4.1, ybot - 1.05, "давит только на дно", fs=10.5, color=C_P)
    # liquid
    ax = axes[1]
    ax.add_patch(Rectangle((x0 + 0.03, ybot + 0.03), x1 - x0 - 0.06, ytop - ybot - 0.2, fc=WATER, ec="none", zorder=1))
    label(ax, 2.3, ytop - 0.8, "Ж", fs=18, color=WATER_EDGE)
    for y, L in ((1.7, 0.75), (2.7, 0.7), (3.7, 0.65)):
        arrow(ax, (x0 + 0.05, y), (x0 - 0.75 - 0.0, y), color=C_P, lw=2.0)
        arrow(ax, (x1 - 0.05, y), (x1 + 0.75, y), color=C_P, lw=2.0)
    for x in (2.8, 4.1, 5.4):
        arrow(ax, (x, ybot + 0.05), (x, ybot - 0.85), color=C_P, lw=2.4)
    label(ax, 4.1, ybot - 1.2, "во все стороны", fs=10.5, color=C_P)
    # gas
    ax = axes[2]
    label(ax, 2.3, ytop - 0.8, "Г", fs=18, color=MOL)
    pts = scatter_in(rng, 12, x0 + 0.4, x1 - 0.4, ybot + 0.4, ytop - 0.6, min_d=0.7)
    for x, y in pts:
        a = rng.uniform(0, 6.28)
        mol(ax, x, y, r=0.1)
        arrow(ax, (x + 0.12 * np.cos(a), y + 0.12 * np.sin(a)), (x + 0.5 * np.cos(a), y + 0.5 * np.sin(a)), color=MOL, lw=1.2, scale=9)
    for y in (1.7, 2.7, 3.7):
        arrow(ax, (x0 + 0.05, y), (x0 - 0.7, y), color=C_P, lw=2.0)
        arrow(ax, (x1 - 0.05, y), (x1 + 0.7, y), color=C_P, lw=2.0)
    for x in (2.8, 4.1, 5.4):
        arrow(ax, (x, ybot + 0.05), (x, ybot - 0.7), color=C_P, lw=2.0)
    label(ax, 4.1, ybot - 1.2, "во все стороны одинаково", fs=10.5, color=C_P)
    save(fig, "pascal-solid-liquid-gas.png")


def particles_solid_liquid():
    rng = np.random.default_rng(15)
    fig, axes = blank(9.4, 4.8, (0, 8.4), (0, 6.4), n=2)
    ax = axes[0]
    rect(ax, 0.8, 0.9, 6.2, 4.0, lw=2)
    xs = np.linspace(1.4, 6.4, 6)
    ys = np.linspace(1.5, 4.2, 5)
    for x in xs:
        for y in ys:
            mol(ax, x, y, r=0.17)
    arrow(ax, (xs[2], 5.85), (xs[2], 5.0), color=C_F, lw=2.6)
    arrow(ax, (xs[3], 5.85), (xs[3], 5.0), color=C_F, lw=2.6)
    for x in xs:
        arrow(ax, (x, 1.25), (x, 0.4), color=C_P, lw=2.0)
    label(ax, 3.9, 6.25, "Кристалл: слои смещаются вертикально", fs=10.5)
    label(ax, 3.9, 0.05, "силы отталкивания только по вертикали", fs=10, color=C_P)
    ax = axes[1]
    rect(ax, 0.8, 0.9, 6.2, 4.0, lw=2)
    pts = scatter_in(rng, 30, 1.2, 6.6, 1.3, 4.5, min_d=0.75)
    for x, y in pts:
        mol(ax, x, y, r=0.17)
        for a in np.radians([0, 90, 180, 270]) + rng.uniform(-0.3, 0.3):
            pass
    arrow(ax, (3.9, 5.85), (3.9, 5.0), color=C_F, lw=2.6)
    for y in (1.9, 3.0, 4.1):
        arrow(ax, (0.85, y), (0.05, y), color=C_P, lw=2.0)
        arrow(ax, (6.95, y), (7.75, y), color=C_P, lw=2.0)
    for x in (2.0, 3.9, 5.8):
        arrow(ax, (x, 1.0), (x, 0.4), color=C_P, lw=2.0)
    label(ax, 3.9, 6.25, "Жидкость: молекулы перескакивают", fs=10.5)
    label(ax, 3.9, 0.05, "давление передаётся во все стороны", fs=10, color=C_P)
    save(fig, "pascal-particles-solid-liquid.png")


def glass_beads_box():
    rng = np.random.default_rng(16)
    fig, axes = blank(9.4, 4.8, (0, 8.6), (0, 7.0), n=2)
    x0, x1, yb, yt = 1.2, 5.4, 0.9, 4.6
    for ax, mode in zip(axes, ("solid", "beads")):
        line(ax, [x0, x0, x1, x1], [yt + 0.3, yb, yb, yt + 0.3], lw=2.4)
        ax.add_patch(Rectangle((x0 + 0.05, yt - 0.7), x1 - x0 - 0.1, 0.5, fc=YELLOW_FILL, ec=INK, lw=1.5, zorder=4))
        label(ax, (x0 + x1) / 2, yt - 0.45, "коробок-поршень", fs=9.5)
        arrow(ax, ((x0 + x1) / 2, yt + 1.2), ((x0 + x1) / 2, yt - 0.1), color=C_F, lw=2.6)
        if mode == "solid":
            ax.add_patch(Rectangle((x0 + 0.5, yb + 0.05), x1 - x0 - 1.0, yt - yb - 0.8, fc=INK, ec=INK, lw=1.5, zorder=2))
            for x in (2.2, 3.3, 4.4):
                arrow(ax, (x, yb + 0.6), (x, yb - 0.45), color=C_P, lw=2.0)
            label(ax, 3.3, 6.65, "Твёрдое тело: давит вниз", fs=11)
            label(ax, 3.3, 0.05, "боковые стенки не нагружены", fs=10, color=C_P)
        else:
            rows = 0
            for j, y in enumerate(np.arange(yb + 0.2, yt - 0.85, 0.37)):
                for i, x in enumerate(np.arange(x0 + 0.25 + 0.18 * (j % 2), x1 - 0.15, 0.37)):
                    ax.add_patch(Circle((x, y), 0.17, fc=tint(SKY, 0.6), ec=INK, lw=0.6, zorder=3))
            for y in (1.6, 2.6, 3.6):
                arrow(ax, (x0 - 0.02, y), (x0 - 0.8, y), color=C_P, lw=2.0)
            for x in (2.2, 3.3, 4.4):
                arrow(ax, (x, yb), (x, yb - 0.5), color=C_P, lw=2.0)
            # hole in right wall with escaping beads
            ax.add_patch(Rectangle((x1 - 0.06, 1.5), 0.12, 0.6, fc=PAPER, ec=PAPER, zorder=5))
            for k, (dx, dy) in enumerate(((0.45, 0.02), (0.95, -0.25), (1.4, -0.75))):
                ax.add_patch(Circle((x1 + dx, 1.8 + dy), 0.17, fc=tint(SKY, 0.6), ec=INK, lw=0.6, zorder=6))
            arrow(ax, (x1 + 0.3, 1.9), (x1 + 1.6, 1.9), color=C_P, lw=1.6, ls="--")
            arrow(ax, (x1 - 0.02, 3.4), (x1 + 0.8, 3.4), color=C_P, lw=2.0)
            label(ax, 3.3, 6.65, "Стеклянные шарики: давят во все стороны", fs=11)
            label(ax, 3.3, 0.05, "шарики выкатываются через отверстие", fs=10, color=C_P)
    save(fig, "pascal-glass-beads-box.png")


def syringe(ax, x, y, w, h, angle=0.0, plunger=0.35, fill=WATER, edge=WATER_EDGE):
    """Draw a syringe with nozzle at the bottom (y) and plunger at the top. Vertical only."""
    rect(ax, x - w / 2, y, w, h, fc=VESSEL, lw=2)
    ax.add_patch(Rectangle((x - w / 2 + 0.03, y + 0.03), w - 0.06, h * (1 - plunger) - 0.06, fc=fill, ec="none", zorder=2))
    py = y + h * (1 - plunger)
    ax.add_patch(Rectangle((x - w / 2 + 0.03, py), w - 0.06, 0.22, fc=METAL, ec=INK, lw=1.3, zorder=4))
    line(ax, [x, x], [py + 0.22, py + 1.0], lw=3, color=METAL)
    ax.add_patch(Rectangle((x - w / 2 - 0.15, py + 1.0), w + 0.3, 0.16, fc=METAL, ec=INK, lw=1.3, zorder=4))
    return py


def two_syringes():
    fig, axes = blank(11.6, 5.2, (0, 12), (0, 6.6), n=3)
    # a) liquid, parallel syringes
    ax = axes[0]
    w, h, y = 1.2, 3.0, 1.3
    pl = 0.25
    syringe(ax, 2.6, y, w, h, plunger=0.45)
    syringe(ax, 7.4, y, w, h, plunger=0.20)
    # tube
    line(ax, [2.6, 2.6, 7.4, 7.4], [y, 0.6, 0.6, y], lw=4, color=WATER_EDGE, z=1)
    arrow(ax, (2.6, 6.4), (2.6, 5.5), color=C_F, lw=2.6)
    arrow(ax, (7.4, 4.9), (7.4, 6.0), color=C_P, lw=2.6)
    label(ax, 5.0, 6.3, "", fs=1)
    label(ax, 5.0, 6.6, "Вода: давят на один поршень, второй уходит вверх", fs=10.5)
    # b) right angle
    ax = axes[1]
    ax.set_xlim(0, 12)
    rect(ax, 1.0, 1.7, 3.0, 1.0, fc=VESSEL, lw=2)
    ax.add_patch(Rectangle((1.03, 1.73), 1.9, 0.94, fc=WATER, ec="none", zorder=2))
    ax.add_patch(Rectangle((2.93, 1.73), 0.2, 0.94, fc=METAL, ec=INK, lw=1.3, zorder=4))
    line(ax, [3.13, 4.6], [2.2, 2.2], lw=3, color=METAL)
    line(ax, [4.6, 4.6], [1.9, 2.5], lw=5, color=METAL)
    # vertical syringe on the right
    syringe(ax, 8.6, 2.1, 1.2, 2.6, plunger=0.3)
    line(ax, [1.0, 0.6, 0.6, 8.6, 8.6], [2.2, 2.2, 0.8, 0.8, 2.1], lw=4, color=WATER_EDGE, z=1)
    arrow(ax, (5.9, 2.2), (4.85, 2.2), color=C_F, lw=2.6)
    arrow(ax, (8.6, 5.4), (8.6, 6.4), color=C_P, lw=2.6)
    label(ax, 6.0, 6.6, "Поршни под прямым углом", fs=10.5)
    # c) gas, one plunger held
    ax = axes[2]
    syringe(ax, 2.6, 1.3, 1.2, 3.0, plunger=0.35, fill=VESSEL)
    syringe(ax, 7.4, 1.3, 1.2, 3.0, plunger=0.30, fill=VESSEL)
    line(ax, [2.6, 2.6, 7.4, 7.4], [1.3, 0.6, 0.6, 1.3], lw=4, color=GREY, z=1)
    rng = np.random.default_rng(3)
    for cx in (2.6, 7.4):
        for x, y in scatter_in(rng, 5, cx - 0.4, cx + 0.4, 1.5, 3.3, min_d=0.35):
            mol(ax, x, y, r=0.07)
    arrow(ax, (2.6, 6.4), (2.6, 5.4), color=C_F, lw=2.6)
    arrow(ax, (7.4, 5.0), (7.4, 6.0), color=C_P, lw=2.6)
    label(ax, 5.0, 6.6, "Воздух: то же, но газ ещё и сжимается", fs=10.5)
    save(fig, "pascal-two-syringes.png")


def pascal_ball():
    fig, axes = blank(9.8, 6.0, (0, 10), (-1.3, 8.3), n=2)
    holes = [-160, -125, -90, -55, -20, 20, 55, 90, 125, 160]
    for ax, mode in zip(axes, ("water", "smoke")):
        cx, cy, R = 5.0, 4.1, 1.35
        ax.add_patch(Circle((cx, cy), R, fc=WATER if mode == "water" else LIGHT, ec=INK, lw=2.2, zorder=3))
        rect(ax, cx - 0.16, cy + R - 0.1, 0.32, 1.7, fc=VESSEL, lw=1.8, z=2)
        ax.add_patch(Rectangle((cx - 0.13, cy + R - 0.12), 0.26, 1.72, fc=WATER if mode == "water" else LIGHT, ec="none", zorder=4))
        holes_use = [-160, -125, -90, -55, -20, 20, 55, 125, 160] if True else holes
        for a in holes_use:
            r = np.radians(a)
            hx, hy = cx + R * np.cos(r), cy + R * np.sin(r)
            ax.plot([hx], [hy], "o", color=PAPER, ms=6, zorder=5, mec=INK)
            L = 1.0
            if mode == "water":
                # parabola-like jet: initial direction along normal, then falls
                t = np.linspace(0, 1, 30)
                vx, vy = np.cos(r), np.sin(r)
                xs = hx + 1.7 * vx * t
                ys = hy + 1.7 * vy * t - 1.3 * t**2
                ax.plot(xs, ys, color=WATER_EDGE, lw=2.4, zorder=4)
            else:
                t = np.linspace(0, 1, 30)
                xs = hx + 1.5 * np.cos(r) * t
                ys = hy + 1.5 * np.sin(r) * t + 0.3 * t**2
                ax.plot(xs, ys, color=SMOKE, lw=6 * (1 - 0.5 * t.mean()), zorder=4, solid_capstyle="round")
        # top hole jet
        r = np.radians(90)
        hx, hy = cx, cy + R
        arrow(ax, (cx, 8.0), (cx, cy + R + 1.75), color=C_F, lw=2.4)
        label(ax, cx + 0.75, 7.6, r"$\vec F$", fs=12, color=C_F)
        label(ax, cx, -0.95, "Вода: струи выгибаются вниз" if mode == "water" else "Дым: струи идут прямо", fs=11)
    save(fig, "pascal-ball.png")


def membrane_tube():
    fig, axes = blank(10.4, 5.6, (0, 11), (-0.6, 7.6), n=3)
    x0, x1 = 3.6, 4.8
    cases = [
        ("Пустая трубка", 0.0, "empty"),
        ("Налили воду", -0.35, "filled"),
        ("Погрузили в воду", +0.35, "dip"),
    ]
    for ax, (t, bulge, mode) in zip(axes, cases):
        label(ax, 5.5, 7.2, t, fs=12)
        if mode == "dip":
            rect(ax, 1.4, 0.7, 6.2, 5.0, fc="none", lw=2)
            ax.add_patch(Rectangle((1.42, 0.72), 6.16, 4.0, fc=WATER, ec="none", zorder=1, alpha=0.8))
            line(ax, [1.4, 7.6], [4.72, 4.72], lw=1.2, color=WATER_EDGE)
            top, bot = 6.4, 1.6
        else:
            top, bot = 6.4, 2.6
        line(ax, [x0, x0], [bot, top], lw=2.2)
        line(ax, [x1, x1], [bot, top], lw=2.2)
        if mode == "filled":
            ax.add_patch(Rectangle((x0 + 0.03, bot + 0.02), x1 - x0 - 0.06, 3.2, fc=WATER, ec="none", zorder=2))
        if mode == "dip":
            ax.add_patch(Rectangle((x0 + 0.03, bot + 0.02), x1 - x0 - 0.06, 0.0, fc=WATER, ec="none", zorder=2))
        xs = np.linspace(x0, x1, 40)
        ys = bot + bulge * (1 - ((xs - (x0 + x1) / 2) / 0.6) ** 2)
        line(ax, xs, ys, color=MEMBRANE, lw=3.2)
        if mode == "filled":
            arrow(ax, (4.2, bot - 0.6 - 0.35), (4.2, bot - 1.6), color=C_F, lw=2.4)
        if mode == "dip":
            arrow(ax, (4.2, bot - 0.75), (4.2, bot + 0.05 + 0.0), color=C_F, lw=2.4)
            arrow(ax, (6.6, 4.72), (6.6, 1.6), style="<|-|>", color=GREY, lw=1.3, scale=9)
            label(ax, 7.1, 3.2, r"$h$", fs=13)
    label(axes[0], 4.2, -0.1, "мембрана плоская", fs=10, color=MEMBRANE)
    label(axes[1], 4.2, -0.1, "мембрана выгнулась вниз", fs=10, color=MEMBRANE)
    label(axes[2], 4.2, -0.1, "мембрана выгнулась вверх", fs=10, color=MEMBRANE)
    save(fig, "pascal-membrane-tube.png")


def cap_experiment():
    fig, axes = blank(9.6, 6.2, (0, 10), (0, 8.4), n=2)
    cases = [
        ("Воды в трубке меньше, чем в сосуде", 3.0, "крышечка держится", False),
        ("Уровни сравнялись", 3.7, "крышечка отпадает", True),  # 3.7 = wlev - tb: tube top level with the vessel
    ]
    for ax, (t, h2, note, fall) in zip(axes, cases):
        vx0, vx1, vb, vt = 1.4, 8.6, 0.6, 6.6
        wlev = 5.2
        rect(ax, vx0, vb, vx1 - vx0, vt - vb, fc="none", lw=2.2)
        ax.add_patch(Rectangle((vx0 + 0.03, vb + 0.03), vx1 - vx0 - 0.06, wlev - vb, fc=WATER, ec="none", zorder=1, alpha=0.85))
        tx0, tx1 = 4.4, 5.6
        tb = 1.5
        ttop = 7.4
        line(ax, [tx0, tx0], [tb, ttop], lw=2)
        line(ax, [tx1, tx1], [tb, ttop], lw=2)
        # water in tube
        ax.add_patch(Rectangle((tx0 + 0.03, tb + 0.0), tx1 - tx0 - 0.06, h2 - 0.0, fc=WATER, ec="none", zorder=2))
        capy = tb - (0.35 if fall else 0.0)
        ax.add_patch(Rectangle((tx0 - 0.05, capy - 0.12), tx1 - tx0 + 0.1, 0.16, fc=INK, ec=INK, lw=1.2, zorder=6))
        # depth markers
        arrow(ax, (2.6, wlev), (2.6, tb), style="<|-|>", color=GREY, lw=1.3, scale=9)
        label(ax, 2.15, (wlev + tb) / 2, r"$h_1$", fs=13)
        arrow(ax, (7.4, tb + h2), (7.4, tb), style="<|-|>", color=GREY, lw=1.3, scale=9)
        label(ax, 7.85, (tb + h2 + tb) / 2, r"$h_2$", fs=13)
        line(ax, [1.9, 4.4], [wlev, wlev], lw=0.9, color=GREY, ls=":")
        line(ax, [5.6, 7.4], [tb + h2, tb + h2], lw=0.9, color=GREY, ls=":")
        # forces on the cap
        if not fall:
            # F1 > F2 in proportion of the heights 3.7 : 3.0
            arrow(ax, (5.0, tb - 1.1), (5.0, tb - 0.1), color=C_F, lw=2.4)
            label(ax, 5.55, tb - 0.55, r"$F_1$", fs=12, color=C_F)
            arrow(ax, (5.0, tb + 0.95), (5.0, tb + 0.15), color=C_P, lw=2.4)
            label(ax, 5.55, tb + 0.7, r"$F_2$", fs=12, color=C_P)
            label(ax, 5.0, 0.05, r"$F_1 > F_2 \Rightarrow p_1 > p_2$", fs=11)
        else:
            label(ax, 5.0, 0.05, r"$F_1 = F_2 \Rightarrow p_1 = p_2$", fs=11)
        label(ax, 5.0, 8.05, t, fs=10.5)
        label(ax, 8.1, 0.05, "", fs=1)
    save(fig, "pascal-cap-experiment.png")


def pressure_vs_depth():
    fig = plt.figure(figsize=(9.4, 4.6))
    ax = fig.add_axes([0.02, 0.05, 0.5, 0.9])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 6.2)
    ax.set_aspect("equal")
    ax.axis("off")
    rect(ax, 0.6, 0.4, 4.8, 5.2, lw=2)
    ax.add_patch(Rectangle((0.63, 0.43), 4.74, 4.6, fc=WATER, ec="none", zorder=1, alpha=0.85))
    line(ax, [0.6, 5.4], [5.03, 5.03], lw=1.4, color=WATER_EDGE)
    for xc, yc, L in ((1.9, 4.2, 0.45), (4.1, 2.9, 0.75), (1.9, 1.75, 1.05)):
        ax.add_patch(Rectangle((xc - 0.2, yc - 0.2), 0.4, 0.4, fc=YELLOW_FILL, ec=INK, lw=1.4, zorder=4))
        for a in (0, 90, 180, 270):
            r = np.radians(a)
            arrow(ax, (xc + (0.2 + L) * np.cos(r), yc + (0.2 + L) * np.sin(r)), (xc + 0.22 * np.cos(r), yc + 0.22 * np.sin(r)), color=C_P, lw=2.0, scale=10)
    label(ax, 3.0, 5.85, "Одна глубина: давление одинаково во все стороны", fs=9.5)
    label(ax, 0.3, 5.03, "", fs=1)
    ax2 = fig.add_axes([0.6, 0.15, 0.37, 0.7])
    h = np.linspace(0, 5, 50)
    ax2.plot(h, 1.0 + 1.5 * h, color=C_P, lw=2.6)
    ax2.set_xlim(0, 5.3)
    ax2.set_ylim(0, 9.5)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlabel("глубина $h$", fontsize=12)
    ax2.set_ylabel("давление $p$", fontsize=12)
    ax2.annotate("", xy=(5.25, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax2.annotate("", xy=(0, 9.45), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.set_title("Чем глубже, тем больше p")
    save(fig, "pascal-pressure-vs-depth.png")


def lamp_forces():
    fig, axes = blank(9.8, 6.0, (0, 10), (0, 8.2), n=2)
    for ax, on in zip(axes, (False, True)):
        cx, cy, R = 5.0, 4.2, 1.9
        ax.add_patch(Circle((cx, cy), R, fc=LIT if on else VESSEL, ec=INK, lw=2.2, zorder=3))
        ax.add_patch(Rectangle((cx - 0.55, cy - R - 0.55), 1.1, 0.8, fc=VESSEL if not on else LIT, ec="none", zorder=4))
        line(ax, [cx - 0.55, cx - 0.55], [cy - R - 0.55, cy - R + 0.2], lw=2.2, z=5)
        line(ax, [cx + 0.55, cx + 0.55], [cy - R - 0.55, cy - R + 0.2], lw=2.2, z=5)
        ax.add_patch(Rectangle((cx - 0.7, cy - R - 1.3), 1.4, 0.75, fc=METAL, ec=INK, lw=1.6, zorder=5))
        # filament
        xs = np.linspace(cx - 0.6, cx + 0.6, 24)
        ys = cy + 0.4 + 0.12 * np.sin(np.linspace(0, 6 * np.pi, 24))
        line(ax, xs, ys, color=WARM if on else INK, lw=2.4 if on else 1.6, z=6)
        # atmospheric arrows (same)
        for a in np.radians([20, 60, 100, 140, 180, 220, 320]):
            px, py = cx + R * np.cos(a), cy + R * np.sin(a)
            arrow(ax, (px + 1.05 * np.cos(a), py + 1.05 * np.sin(a)), (px + 0.05 * np.cos(a), py + 0.05 * np.sin(a)), color=C_F, lw=2.0, scale=11)
        # inside arrows
        Lin = 0.95 if on else 0.32
        for a in np.radians([20, 60, 100, 140, 180, 220, 320]):
            px, py = cx + R * np.cos(a), cy + R * np.sin(a)
            # gas presses on the glass from inside: the arrow points outward, towards the glass
            arrow(ax, (px - (0.05 + Lin) * np.cos(a), py - (0.05 + Lin) * np.sin(a)), (px - 0.05 * np.cos(a), py - 0.05 * np.sin(a)), color=C_P, lw=2.0, scale=11)
        label(ax, cx, 7.9, "Лампа включена" if on else "Лампа выключена", fs=12)
        label(ax, cx, 0.4, "снаружи: атмосфера (красные)   внутри: газ (синие)", fs=8.5, color=GREY)
        if on:
            label(ax, cx, cy - 0.45, "нить горячая", fs=8.5, color=COPPER)
    save(fig, "pascal-lamp-forces.png")


if __name__ == "__main__":
    molecules_hit_wall()
    impacts_analogy()
    balloon_vacuum()
    piston_volume()
    syringe_film()
    p_of_v()
    p_of_t()
    temperature_molecules()
    flask_balloon()
    half_gas_cylinder()
    solid_liquid_gas()
    particles_solid_liquid()
    glass_beads_box()
    two_syringes()
    pascal_ball()
    membrane_tube()
    cap_experiment()
    pressure_vs_depth()
    lamp_forces()
