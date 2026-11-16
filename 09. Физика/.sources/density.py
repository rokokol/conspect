"""Figures for the note "Плотность" (course Физика 7-9, lessons 27-31).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 density.py
PNG files go to content/04. Инерция, масса, плотность/00. Вложения/
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "04. Инерция, масса, плотность"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ASH, BLUE, COPPER, GREEN, INK, PAPER, RED, SKY, WARM, keep_dots, num, saver, tint

GRID = ASH
C_AL = tint(INK, 0.6)  # aluminium, light grey
C_FE = tint(INK, 0.3)  # iron and steel, dark grey
C_BRASS = WARM
C_CU = COPPER
C_WATER = BLUE  # water as a line or a text
WATER_FILL = tint(SKY, 0.6)  # water as a fill
C_ICE = SKY
C_PB = tint(BLUE, 0.4)  # lead, a bluish grey
C_TIN = tint(INK, 0.8)
C_ACC = RED
C_KER = WARM  # kerosene, oil


save = saver(OUT)


def blank(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def dim_arrow(ax, p, q, text, off=(0, 0), both=True, color=INK, fs=11, ha="center", va="center"):
    style = "<->" if both else "->"
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, lw=1.2, color=color))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, color=color, fontsize=fs, ha=ha, va=va)


def box3d(ax, x0, y0, w, d, h, dx, dy, face, edge=INK, alpha=1.0):
    """Oblique-projection box: front face w x h, depth d shifted by (dx, dy) per unit d."""
    ox, oy = dx * d, dy * d
    front = Rectangle((x0, y0), w, h, fc=face, ec=edge, lw=1.4, alpha=alpha)
    top = Polygon([(x0, y0 + h), (x0 + w, y0 + h), (x0 + w + ox, y0 + h + oy), (x0 + ox, y0 + h + oy)],
                  fc=face, ec=edge, lw=1.4, alpha=alpha)
    side = Polygon([(x0 + w, y0), (x0 + w + ox, y0 + oy), (x0 + w + ox, y0 + h + oy), (x0 + w, y0 + h)],
                   fc=face, ec=edge, lw=1.4, alpha=alpha)
    for p in (front, top, side):
        ax.add_patch(p)
    top.set_facecolor(_shade(face, 1.12))
    side.set_facecolor(_shade(face, 0.82))


def _shade(color, k):
    c = np.array(matplotlib.colors.to_rgb(color))
    return tuple(np.clip(c * k, 0, 1))


# 1. m(V) lines ----------------------------------------------------------
def fig_mass_volume():
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    V = np.linspace(0, 30, 2)
    series = [
        ("латунь", 8.5, C_BRASS),
        ("железо", 7.8, C_FE),
        ("алюминий", 2.7, C_AL),
        ("вода", 1.0, C_WATER),
        ("лёд", 0.9, C_ICE),
    ]
    for name, rho, col in series:
        ax.plot(V, rho * V, color=col, lw=2.4)
    ax.text(29.3, 8.5 * 29.3 - 4, "латунь\n$\\rho = 8{,}5$", color=_shade(C_BRASS, 0.75), ha="right", va="top", fontsize=10)
    ax.text(29.3, 7.8 * 29.3 - 28, "железо\n$\\rho = 7{,}8$", color=C_FE, ha="right", va="top", fontsize=10)
    ax.text(29.3, 2.7 * 29.3 + 6, "алюминий $\\rho = 2{,}7$", color=_shade(C_AL, 0.7), ha="right", va="bottom", fontsize=10)
    ax.text(17, 21, "вода $\\rho = 1$", color=C_WATER, ha="center", va="bottom", fontsize=10)
    ax.text(17, 9, "лёд $\\rho = 0{,}9$", color=_shade(C_ICE, 0.65), ha="center", va="top", fontsize=10)
    # slope triangle on iron
    x0, x1 = 5, 10
    y0 = 7.8 * x0
    ax.plot([x0, x1, x1], [y0, y0, 7.8 * x1], color=C_ACC, lw=1.4, ls="--")
    ax.text((x0 + x1) / 2, y0 - 5, "$\\Delta V = 5\\ \\mathrm{см}^3$", color=C_ACC, ha="center", va="top", fontsize=10)
    ax.text(x1 + 0.5, 60, "$\\Delta m = 39\\ \\mathrm{г}$\n$\\rho = \\Delta m / \\Delta V$", color=C_ACC,
            ha="left", va="center", fontsize=10)
    # measured plasticine
    ax.plot([26], [35.17], "o", color=C_ACC, ms=7, zorder=5)
    ax.annotate("пластилин\n$26\\ \\mathrm{см}^3$; $35{,}17\\ \\mathrm{г}$", (26, 35.17), (23.5, 130),
                fontsize=10, color=C_ACC, arrowprops=dict(arrowstyle="->", color=C_ACC, lw=1.1), ha="center")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 260)
    ax.set_xlabel("Объём $V$, см$^3$")
    ax.set_ylabel("Масса $m$, г")
    ax.set_title("Масса от объёма для разных веществ")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "density-mass-volume-graph.png")


# 2. bar chart of densities -------------------------------------------
def fig_bars():
    data = [
        ("осмий", 22500, "тв"),
        ("золото", 19300, "тв"),
        ("ртуть", 13600, "ж"),
        ("свинец", 11300, "тв"),
        ("серебро", 10500, "тв"),
        ("медь", 8900, "тв"),
        ("латунь", 8500, "тв"),
        ("сталь, железо", 7800, "тв"),
        ("олово", 7300, "тв"),
        ("цинк", 7100, "тв"),
        ("алюминий", 2700, "тв"),
        ("стекло", 2500, "тв"),
        ("вода", 1000, "ж"),
        ("лёд", 900, "тв"),
        ("керосин", 800, "ж"),
        ("бензин", 710, "ж"),
        ("сосна сухая", 440, "тв"),
        ("пробка", 240, "тв"),
        ("хлор", 3.21, "г"),
        ("воздух", 1.29, "г"),
        ("водород", 0.09, "г"),
    ]
    cols = {"тв": C_FE, "ж": C_WATER, "г": WARM}
    fig, ax = plt.subplots(figsize=(7.6, 7.2))
    n = len(data)
    for i, (name, rho, st) in enumerate(data):
        y = n - 1 - i
        ax.barh(y, rho, color=cols[st], height=0.72)
        lab = num(rho, None) if rho < 10 else f"{rho:,.0f}".replace(",", "\u202f")
        ax.text(rho * 1.12, y, lab, va="center", fontsize=9.5, color=INK)
    ax.set_yticks(range(n))
    ax.set_yticklabels([d[0] for d in data][::-1])
    ax.set_xscale("log")
    ax.set_xlim(0.05, 90000)
    ax.set_xlabel("Плотность $\\rho$, кг/м$^3$ (логарифмическая шкала)")
    ax.set_title("Плотности некоторых веществ")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=cols[k]) for k in ("тв", "ж", "г")]
    ax.legend(handles, ["твёрдые", "жидкие", "газы (0 °C, 760 мм рт. ст.)"], loc="lower right", frameon=False)
    save(fig, "density-bar-chart.png")


# 3. equal volumes on balance -----------------------------------------
def draw_balance(ax, cx, left, right, tilt_right_heavy=True):
    """Beam tilts down to the right if right is heavier."""
    ang = -0.16 if tilt_right_heavy else 0.16
    L = 2.2
    px, py = cx, 2.2
    lx, ly = px - L * np.cos(ang), py - L * np.sin(ang) * -1 * -1
    lx, ly = px - L * np.cos(ang), py + L * np.sin(-ang) * -1
    # beam ends
    ex_l, ey_l = px - L * np.cos(ang), py - L * np.sin(ang)
    ex_r, ey_r = px + L * np.cos(ang), py + L * np.sin(ang)
    ax.plot([ex_l, ex_r], [ey_l, ey_r], color=INK, lw=3, solid_capstyle="round")
    ax.add_patch(Polygon([(px - 0.35, 0.2), (px + 0.35, 0.2), (px, py)], fc=tint(INK, 0.8), ec=INK, lw=1.4))
    ax.plot([px - 0.7, px + 0.7], [0.2, 0.2], color=INK, lw=3)
    for (ex, ey, item) in ((ex_l, ey_l, left), (ex_r, ey_r, right)):
        name, col = item
        ax.plot([ex - 0.7, ex, ex + 0.7], [ey - 0.9, ey, ey - 0.9], color=INK, lw=1)
        ax.plot([ex - 0.75, ex + 0.75], [ey - 0.9, ey - 0.9], color=INK, lw=3)
        ax.add_patch(Rectangle((ex - 0.28, ey - 0.9), 0.56, 0.9 * 0.75, fc=col, ec=INK, lw=1.3))
        ax.text(ex, ey - 1.25, name, ha="center", va="top", fontsize=11)


def fig_balance():
    fig, ax = blank(9, 4.2, (-3.2, 12.2), (-0.3, 4.0))
    draw_balance(ax, 1.5, ("Al", C_AL), ("Fe", C_FE), True)
    draw_balance(ax, 8.0, ("Fe", C_FE), ("латунь", C_BRASS), True)
    ax.text(1.5, 3.55, "$m_{\\mathrm{Fe}} > m_{\\mathrm{Al}}$", ha="center", fontsize=12)
    ax.text(8.0, 3.55, "$m_{\\mathrm{латунь}} > m_{\\mathrm{Fe}}$", ha="center", fontsize=12)
    ax.set_title("Три цилиндра одного объёма на рычажных весах")
    save(fig, "density-equal-volume-balance.png")


# 4. plasticine in measuring cylinder ---------------------------------
def draw_cyl(ax, x, level, title, water_top=100):
    W = 1.2
    ax.add_patch(Rectangle((x, 0), W, 5.0, fc="none", ec=INK, lw=1.6))
    ax.add_patch(Rectangle((x, 0), W, level * 5.0 / water_top, fc=WATER_FILL, ec="none"))
    ax.plot([x, x + W], [level * 5.0 / water_top] * 2, color=C_WATER, lw=1.6)
    for v in range(0, 101, 10):
        yy = v * 5.0 / water_top
        ax.plot([x, x + 0.3 if v % 20 else x + 0.45], [yy, yy], color=INK, lw=0.9)
        if v % 20 == 0 and v > 0:
            ax.text(x - 0.12, yy, str(v), ha="right", va="center", fontsize=8.5)
    ax.text(x + W / 2, -0.35, title, ha="center", va="top", fontsize=10.5)


def fig_plasticine():
    fig, ax = blank(8, 4.8, (-1.0, 9.0), (-1.2, 5.8))
    draw_cyl(ax, 0.5, 56, "$V_1 = 56\\ \\mathrm{мл}$")
    draw_cyl(ax, 4.5, 82, "$V_2 = 82\\ \\mathrm{мл}$")
    ax.add_patch(Ellipse((5.1, 0.45), 0.7, 0.45, fc=tint(COPPER, 0.2), ec=INK, lw=1.2, zorder=5))
    ax.add_patch(FancyArrowPatch((2.4, 2.8), (3.8, 2.8), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=INK))
    ax.text(3.1, 3.2, "пластилин\nна нитке", ha="center", fontsize=10)
    ax.text(7.6, 2.4, "$V = V_2 - V_1$\n$= 82 - 56$\n$= 26\\ \\mathrm{см}^3$", fontsize=12, va="center")
    ax.set_title("Объём тела неправильной формы")
    save(fig, "density-plasticine-cylinder.png")


# 5. water -> ice -------------------------------------------------
def fig_water_ice():
    fig, ax = blank(8, 4.2, (-0.5, 10.5), (-1.0, 5.2))
    h_w = 3.6
    h_i = h_w * 1000 / 900
    ax.add_patch(Rectangle((0.4, 0), 2.6, h_w, fc=WATER_FILL, ec=INK, lw=1.6))
    ax.add_patch(Rectangle((5.4, 0), 2.6, h_i, fc=tint(C_ICE, 0.25), ec=INK, lw=1.6))
    ax.plot([5.4, 8.6], [h_w, h_w], color=C_ACC, lw=1.2, ls="--")
    ax.text(1.7, h_w / 2, "вода\n$\\rho = 1000$", ha="center", va="center", fontsize=11)
    ax.text(6.7, h_w / 2, "лёд\n$\\rho = 900$", ha="center", va="center", fontsize=11)
    ax.add_patch(FancyArrowPatch((3.4, 1.8), (5.0, 1.8), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=INK))
    ax.text(4.2, 2.15, "замерзание", ha="center", fontsize=10)
    ax.text(1.7, -0.35, "$m$, $V_{\\mathrm{в}}$", ha="center", va="top", fontsize=11)
    ax.text(6.7, -0.35, "$m$, $V_{\\mathrm{л}} > V_{\\mathrm{в}}$", ha="center", va="top", fontsize=11)
    ax.text(9.4, 4.0, "$V = \\dfrac{m}{\\rho}$", fontsize=13, ha="center", va="center")
    ax.text(9.4, 2.5, "$V_{\\mathrm{л}} : V_{\\mathrm{в}}$\n$= 1000 : 900$\n$\\approx 1{,}11$", fontsize=10.5, ha="center", va="center")
    ax.set_title("Масса та же, объём льда больше")
    save(fig, "density-water-ice-volume.png")


# 6. lead shot ------------------------------------------------------
def fig_shot():
    fig, ax = blank(8.2, 4.6, (-0.5, 11), (-1.0, 5.2))
    # left vessel with shot
    ax.add_patch(Rectangle((0.5, 0), 3.2, 4.2, fc="none", ec=INK, lw=1.6))
    r = 0.26
    y = r
    row = 0
    while y < 3.0:
        x = 0.5 + r + (r if row % 2 else 0)
        while x < 3.7 - r:
            ax.add_patch(Circle((x, y), r * 0.98, fc=C_PB, ec=INK, lw=0.5))
            x += 2 * r
        y += r * 1.75
        row += 1
    top_shot = y - r * 0.75
    ax.plot([0.5, 3.7], [top_shot] * 2, color=INK, lw=1, ls="--")
    dim_arrow(ax, (4.05, 0), (4.05, top_shot), "$V_{\\mathrm{др}}$", off=(0.45, 0))
    ax.text(2.1, -0.35, "дробь, масса $m$", ha="center", va="top", fontsize=10.5)
    # right vessel with melted lead
    v_pb = top_shot * 0.66
    ax.add_patch(Rectangle((6.3, 0), 3.2, 4.2, fc="none", ec=INK, lw=1.6))
    ax.add_patch(Rectangle((6.3, 0), 3.2, v_pb, fc=C_PB, ec="none"))
    ax.plot([6.3, 9.5], [top_shot] * 2, color=INK, lw=1, ls="--")
    dim_arrow(ax, (9.85, 0), (9.85, v_pb), "$V_{\\mathrm{Pb}}$", off=(0.5, 0))
    ax.text(7.9, -0.35, "расплавленный свинец, та же $m$", ha="center", va="top", fontsize=10.5)
    ax.add_patch(FancyArrowPatch((4.9, 1.6), (5.9, 1.6), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=INK))
    ax.text(5.4, 2.0, "плавим", ha="center", fontsize=10)
    ax.set_title("Между дробинками остаются пустоты")
    save(fig, "density-lead-shot-melting.png")


# 7. foil slab -------------------------------------------------------
def fig_foil():
    fig, ax = blank(8.4, 3.6, (-1.0, 11.2), (-1.4, 3.6))
    box3d(ax, 0.5, 0.3, 8.0, 1.8, 0.45, 0.6, 0.45, C_AL)
    dim_arrow(ax, (0.5, -0.35), (8.5, -0.35), "$b = 15\\ \\mathrm{м}$", off=(0, -0.4))
    dim_arrow(ax, (8.5 + 0.35, 0.3 - 0.1 + 0.0), (8.5 + 0.35 + 1.08, 0.3 + 0.81), "$a = 0{,}2\\ \\mathrm{м}$", off=(1.0, -0.5))
    dim_arrow(ax, (0.05, 0.3), (0.05, 0.75), "$h$", off=(-0.45, 0))
    ax.text(4.8, 1.15, "алюминий", fontsize=11, ha="center", va="center")
    ax.set_title("Развёрнутая лента фольги")
    save(fig, "density-foil-roll-slab.png")


# 8. hollow cylinder -------------------------------------------------
def fig_hollow():
    fig, ax = blank(5.6, 5.0, (-0.5, 8.5), (-1.2, 6.2))
    cx, w, h, ry = 2.6, 4.0, 4.0, 0.7
    y0 = 0.3
    ax.add_patch(Rectangle((cx - w / 2, y0), w, h, fc=tint(C_CU, 0.3), ec="none"))
    ax.add_patch(Ellipse((cx, y0), w, 2 * ry, fc=tint(C_CU, 0.3), ec="none"))
    ax.add_patch(Ellipse((cx, y0 + h), w, 2 * ry, fc=tint(C_CU, 0.5), ec=INK, lw=1.4))
    ax.plot([cx - w / 2] * 2, [y0, y0 + h], color=INK, lw=1.6)
    ax.plot([cx + w / 2] * 2, [y0, y0 + h], color=INK, lw=1.6)
    t = np.linspace(np.pi, 2 * np.pi, 60)
    ax.plot(cx + w / 2 * np.cos(t), y0 + ry * np.sin(t), color=INK, lw=1.6)
    ax.add_patch(Ellipse((cx, y0 + h / 2), 1.9, 1.5, fc=PAPER, ec=INK, lw=1.5, ls="--", zorder=5))
    ax.text(cx, y0 + h / 2, "$V_{\\mathrm{п}}$", ha="center", va="center", fontsize=15, zorder=6)
    ax.text(cx, y0 + 0.9, "медь", ha="center", va="center", fontsize=11, color=INK)
    dim_arrow(ax, (cx + w / 2 + 0.5, y0), (cx + w / 2 + 0.5, y0 + h), "$V$", off=(0.4, 0), fs=14)
    ax.text(6.0, 4.6, "$m = 890\\ \\mathrm{г}$\n$V = 130\\ \\mathrm{см}^3$", fontsize=11.5, va="center")
    ax.text(6.0, 2.2, "$V - V_{\\mathrm{п}} = \\dfrac{m}{\\rho}$", fontsize=13, va="center")
    ax.set_title("Медный цилиндр с полостью")
    save(fig, "density-hollow-cylinder.png")


# 9. cube and sphere ------------------------------------------------
def fig_cube_sphere():
    fig, ax = blank(7.6, 4.0, (-0.6, 11.4), (-1.3, 4.6))
    a = 3.6
    # square with inscribed circle: cross-section
    ax.add_patch(Rectangle((0.3, 0), a, a, fc=tint(COPPER, 0.75), ec=INK, lw=1.6))
    ax.add_patch(Circle((0.3 + a / 2, a / 2), a / 2, fc=tint(C_CU, 0.3), ec=INK, lw=1.6, alpha=0.85))
    dim_arrow(ax, (0.3, -0.35), (0.3 + a, -0.35), "$d = a$", off=(0, -0.45), fs=12)
    ax.text(0.3 + a / 2, a / 2, "шар", ha="center", va="center", fontsize=11, color=INK)
    ax.text(0.3, a + 0.2, "куб с ребром $a$", ha="left", va="bottom", fontsize=10.5)
    ax.set_title("Шар внутри куба (сечение через центр)")
    ax.text(4.95, 3.2, "$V_{\\mathrm{к}} = a^3$", fontsize=13, va="center")
    ax.text(4.95, 2.1, "$V_{\\mathrm{ш}} = \\dfrac{4}{3}\\pi r^3 = \\dfrac{\\pi}{6}d^3$", fontsize=13, va="center")
    ax.text(4.95, 0.8, "$\\dfrac{m_{\\mathrm{к}}}{m_{\\mathrm{ш}}} = \\dfrac{V_{\\mathrm{к}}}{V_{\\mathrm{ш}}} = \\dfrac{6}{\\pi} \\approx 1{,}91$", fontsize=13, va="center")
    save(fig, "density-cube-sphere.png")


# 10. two cubes 1:3 ---------------------------------------------------
def fig_cubes():
    fig = plt.figure(figsize=(8, 4.2))
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    filled = np.ones((3, 3, 3), dtype=bool)
    ax.voxels(filled, facecolors=C_AL, edgecolor=INK, linewidth=0.9, alpha=0.85)
    ax.set_box_aspect((1, 1, 1))
    ax.axis("off")
    ax.view_init(elev=22, azim=-58)
    ax.set_title("Большой куб: $a_2 = 3a_1$", fontsize=12)
    ax2 = fig.add_subplot(1, 2, 1, projection="3d")
    f1 = np.zeros((3, 3, 3), dtype=bool)
    f1[0, 0, 0] = True
    ax2.voxels(f1, facecolors=C_ACC, edgecolor=INK, linewidth=0.9, alpha=0.9)
    ax2.set_box_aspect((1, 1, 1))
    ax2.set_xlim(0, 3)
    ax2.set_ylim(0, 3)
    ax2.set_zlim(0, 3)
    ax2.axis("off")
    ax2.view_init(elev=22, azim=-58)
    ax2.set_title("Малый куб: $a_1$", fontsize=12)
    fig.text(0.5, 0.03, "В большой куб укладывается $3^3 = 27$ малых, поэтому $m_2 : m_1 = 27$", ha="center", fontsize=11)
    save(fig, "density-two-cubes-27.png")


# 11. scaling k^3 -----------------------------------------------------
def fig_scaling():
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    k = np.logspace(0, 2.3, 100)
    ax.loglog(k, k**3, color=C_FE, lw=2.4)
    pts = [(3, 27, "$k = 3$: 27 раз"), (10, 1000, "$k = 10$: 1000 раз"), (100, 1e6, "$k = 100$: $10^6$ раз\n(модель Эйфелевой башни)")]
    for x, y, t in pts:
        ax.plot([x], [y], "o", color=C_ACC, ms=7, zorder=5)
    ax.annotate(pts[0][2], (3, 27), (1.3, 400), fontsize=10, color=C_ACC, arrowprops=dict(arrowstyle="->", color=C_ACC))
    ax.annotate(pts[1][2], (10, 1000), (1.5, 2e4), fontsize=10, color=C_ACC, arrowprops=dict(arrowstyle="->", color=C_ACC))
    ax.annotate(pts[2][2], (100, 1e6), (2.2, 3e6), fontsize=10, color=C_ACC, arrowprops=dict(arrowstyle="->", color=C_ACC))
    ax.set_xlabel("Во сколько раз размеры больше, $k$")
    ax.set_ylabel("Во сколько раз масса больше, $k^3$")
    ax.set_title("Масса подобных тел растёт как $k^3$")
    ax.grid(color=GRID, lw=0.8, which="both")
    ax.set_axisbelow(True)
    ax.set_xlim(1, 250)
    ax.set_ylim(1, 3e7)
    save(fig, "density-scaling-graph.png")


# 12. overflow tank ------------------------------------------------
def fig_overflow():
    fig, ax = blank(9.4, 4.8, (-0.6, 12.6), (-1.3, 5.6))
    # before
    ax.add_patch(Rectangle((0.5, 0), 3.4, 3.0, fc=C_KER, ec="none", alpha=0.55))
    ax.add_patch(Rectangle((0.5, 0), 3.4, 3.0, fc="none", ec=INK, lw=1.8))
    ax.add_patch(Rectangle((1.5, 3.7), 1.4, 1.3, fc=tint(C_CU, 0.3), ec=INK, lw=1.4))
    ax.text(2.2, 4.35, "$m_{\\mathrm{д}}$", ha="center", va="center", fontsize=12, color=INK)
    ax.add_patch(FancyArrowPatch((2.2, 3.6), (2.2, 2.2), arrowstyle="-|>", mutation_scale=15, lw=1.5, color=INK))
    ax.text(2.2, -0.35, "бак полон до краёв", ha="center", va="top", fontsize=10.5)
    # after
    ax.add_patch(Rectangle((5.5, 0), 3.4, 3.0, fc=C_KER, ec="none", alpha=0.55))
    ax.add_patch(Rectangle((5.5, 0), 3.4, 3.0, fc="none", ec=INK, lw=1.8))
    ax.add_patch(Rectangle((6.7, 0.1), 1.4, 1.3, fc=tint(C_CU, 0.3), ec=INK, lw=1.4))
    ax.add_patch(FancyArrowPatch((8.95, 2.95), (10.7, 0.15), connectionstyle="arc3,rad=-0.35", arrowstyle="-|>", mutation_scale=15, lw=1.5, color=C_KER))
    ax.add_patch(Polygon([(9.6, 0.0), (12.4, 0.0), (12.0, -0.7), (10.0, -0.7)], fc=C_KER, ec=INK, lw=1.4, alpha=0.8))
    ax.text(11.0, -0.95, "$m_{\\mathrm{к}} - ?$", ha="center", va="top", fontsize=12)
    ax.text(7.2, -0.35, "деталь на дне,\nчасть керосина вылилась", ha="center", va="top", fontsize=10.5)
    ax.add_patch(FancyArrowPatch((4.2, 1.5), (5.2, 1.5), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=INK))
    ax.text(8.4, 4.5, "$V_{\\mathrm{д}} = V_{\\mathrm{к}}$", fontsize=13, ha="center")
    ax.set_title("Объём вылившегося керосина равен объёму детали")
    save(fig, "density-overflow-tank.png")


# 13. tin coating -----------------------------------------------------
def fig_tin():
    fig, ax = blank(8.4, 4.0, (-1.6, 10.8), (-1.3, 4.4))
    dx, dy = 0.55, 0.42
    d = 3.0
    w = 7.0
    h_steel = 0.9
    h_tin = 0.16
    box3d(ax, 0.5, 0.0, w, d, h_steel, dx, dy, C_FE)
    box3d(ax, 0.5, h_steel, w, d, h_tin, dx, dy, C_TIN)
    ax.text(0.5 + w / 2 + 0.3, h_steel + h_tin + dy * d / 2 + 0.05, "$S$", fontsize=14, ha="center", va="center")
    ax.text(3.0, 0.4, "сталь", color=PAPER, fontsize=11, ha="center", va="center")
    ax.annotate("слой олова, толщина $h$", (0.5, h_steel + h_tin / 2), (-1.2, 2.7), fontsize=11,
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.1))
    ax.text(5.0, -0.6, "$V = S h,\\quad h = \\dfrac{V}{S} = \\dfrac{m}{\\rho S}$", fontsize=13, ha="center", va="center")
    ax.set_title("Слой олова на стальной основе")
    save(fig, "density-tin-coating.png")


# 14. alloy density vs composition ----------------------------------
def fig_alloy():
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    x = np.linspace(0, 1, 200)  # mass fraction of zinc
    rho_cu, rho_zn = 8.9, 7.1
    rho = 1 / ((1 - x) / rho_cu + x / rho_zn)
    ax.plot(x, rho, color=C_BRASS, lw=2.6)
    ax.plot([0, 1], [rho_cu, rho_zn], color=GRID, lw=1.4, ls="--")
    ax.axhline(rho_cu, color=C_CU, lw=0.8, alpha=0.6)
    ax.axhline(rho_zn, color=C_FE, lw=0.8, alpha=0.6)
    xz = 355 / (178 + 355)
    rz = (178 + 355) * rho_cu * rho_zn / (178 * rho_zn + 355 * rho_cu)
    ax.plot([xz], [rz], "o", color=C_ACC, ms=8, zorder=5)
    rz_txt = num(rz, 1, math=True)
    keep_dots(ax.annotate(f"задача 7.35: $\\rho \\approx {rz_txt}$", (xz, rz), (0.14, 7.35), fontsize=10.5, color=C_ACC,
                arrowprops=dict(arrowstyle="->", color=C_ACC)))
    ax.text(0.02, rho_cu + 0.05, "медь $8{,}9$", color=C_CU, va="bottom", fontsize=10)
    ax.text(0.98, rho_zn - 0.05, "цинк $7{,}1$", color=C_FE, va="top", ha="right", fontsize=10)
    ax.text(0.5, 8.35, "сплошная кривая: $V = V_1 + V_2$\nпунктир: $(1-x)\\rho_1 + x\\rho_2$ (наивная оценка)", fontsize=9.5, ha="center", va="top", color=INK)
    ax.set_xlabel("Доля цинка по массе")
    ax.set_ylabel("Плотность сплава $\\rho$, г/см$^3$")
    ax.set_title("Плотность сплава меди и цинка")
    ax.set_xlim(0, 1)
    ax.set_ylim(6.9, 9.1)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "density-alloy-graph.png")


# 15. wire on spool -------------------------------------------------
def fig_wire():
    fig, ax = blank(8.6, 3.0, (-0.5, 12.0), (-1.4, 2.6))
    ax.add_patch(Rectangle((0.5, 0.3), 9.0, 0.5, fc=tint(C_CU, 0.3), ec=INK, lw=1.4))
    ax.add_patch(Ellipse((0.5, 0.55), 0.22, 0.5, fc=tint(C_CU, 0.55), ec=INK, lw=1.4))
    ax.add_patch(Ellipse((9.5, 0.55), 0.22, 0.5, fc=C_CU, ec=INK, lw=1.4))
    dim_arrow(ax, (0.5, -0.25), (9.5, -0.25), "$L$ (длина провода)", off=(0, -0.45), fs=12)
    dim_arrow(ax, (10.1, 0.3), (10.1, 0.8), "", both=True)
    ax.text(10.35, 0.55, "$d = 0{,}49\\ \\mathrm{мм}$", fontsize=11.5, va="center")
    ax.text(0.5, 1.7, "$V = \\dfrac{\\pi d^2}{4}\\,L = \\dfrac{m}{\\rho}$", fontsize=13, va="center")
    ax.set_title("Провод как растянутый цилиндр")
    save(fig, "density-wire-cylinder.png")


if __name__ == "__main__":
    for f in (fig_mass_volume, fig_bars, fig_balance, fig_plasticine, fig_water_ice, fig_shot, fig_foil,
              fig_hollow, fig_cube_sphere, fig_cubes, fig_scaling, fig_overflow, fig_tin, fig_alloy, fig_wire):
        f()
