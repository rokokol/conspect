"""Figures for the notes "Строение атома. Объяснение электрических явлений" and "Закон Кулона" (section f11, lessons 138-140, 142).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 atom_coulomb.py
PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes atom-, coulomb-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "11. Электрические явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

import theme  # noqa: F401 — применяет общий шрифт и служебные цвета

from theme import ASH, BLUE, COPPER, GREEN, INK, LIGHT, PAPER, RED, SKY, WARM, saver, tint

GRID = ASH
GREY = tint(INK, 0.45)  # outlines of neutral bodies, guides and small notes
POS = RED  # positive charge
NEG = BLUE  # negative charge
GOLD = WARM
NEUTRON = tint(INK, 0.65)  # a neutral particle: a pale grey
SOFT = tint(INK, 0.94)  # the pale body fill of a neutral part
CLOUD = tint(INK, 0.87)  # a cloud and other grey bodies
POS_FILL = tint(RED, 0.85)  # the pale fill of a positively charged body
STRING = tint(COPPER, 0.4)  # thread and twine

K = 9e9  # N m^2 / C^2, value used in the lesson


save = saver(OUT)


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.8, style="-|>", ms=14, ls="-", z=5):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, ls=ls, zorder=z
        )
    )


def charge(ax, xy, sign, r=0.3, fs=None, z=6):
    color = POS if sign == "+" else NEG
    ax.add_patch(Circle(xy, r, fc=PAPER, ec=color, lw=1.8, zorder=z))
    ax.text(
        xy[0], xy[1] - r * 0.06, "+" if sign == "+" else "−", color=color, ha="center",
        va="center", fontsize=fs or r * 40, fontweight="bold", zorder=z + 1,
    )


def mark(ax, xy, sign, fs=13, z=6):
    color = POS if sign == "+" else NEG
    ax.text(
        xy[0], xy[1], "+" if sign == "+" else "−", color=color, ha="center", va="center",
        fontsize=fs, fontweight="bold", zorder=z,
    )


def axes_grid(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    return fig, ax


# ---------------------------------------------------------------- atom-


def rutherford_scattering():
    fig, ax = canvas(9, 5.4, (0, 10), (-3.9, 4.1))
    # source with collimator
    ax.add_patch(Rectangle((0.0, -0.9), 1.3, 1.8, fc=LIGHT, ec=INK, lw=1.4))
    ax.text(0.65, 0, "радио-\nактивный\nпрепарат", ha="center", va="center", fontsize=8.5)
    # foil
    ax.add_patch(Rectangle((5.3, -3.0), 0.5, 6.0, fc=tint(WARM, 0.6), ec=GOLD, lw=1.4, zorder=1))
    ax.text(5.55, 3.25, "золотая фольга", ha="center", fontsize=10)
    # nuclei in foil (not to scale)
    for y in (-2.2, -0.9, 0.4, 1.7, 2.6):
        ax.plot(5.55, y, "o", color=POS, ms=3.5, zorder=2)
    # passing alpha particles
    for y, dy in ((-2.2, -0.05), (-1.4, 0.03), (1.0, -0.03), (2.2, 0.06)):
        arrow(ax, (1.3, y), (5.3, y), color=NEG, lw=1.4, ms=10, z=3)
        arrow(ax, (5.8, y), (9.4, y + dy * 6), color=NEG, lw=1.4, ms=10, z=3)
    # large-angle deflection
    ax.plot([1.3, 5.55], [-0.35, -0.35], color=NEG, lw=1.4, zorder=3)
    p = np.array([[5.55, -0.35], [5.9, -0.2], [6.5, 0.3], [7.4, 1.0], [8.6, 1.9]])
    ax.plot(p[:, 0], p[:, 1], color=NEG, lw=1.4, zorder=3)
    arrow(ax, (8.2, 1.6), (8.8, 2.05), color=NEG, lw=1.4, ms=10, z=4)
    # backscatter
    ax.plot([1.3, 5.1], [0.4, 0.4], color=POS, lw=1.6, zorder=3)
    b = np.array([[5.1, 0.4], [5.3, 0.65], [5.1, 1.0], [4.4, 1.5], [3.0, 2.1], [1.6, 2.7]])
    ax.plot(b[:, 0], b[:, 1], color=POS, lw=1.6, zorder=3)
    arrow(ax, (2.2, 2.45), (1.6, 2.7), color=POS, lw=1.6, ms=11, z=4)
    ax.text(2.6, 3.4, "единицы частиц\nлетят назад", color=POS, fontsize=10, ha="center")
    ax.text(7.6, -3.3, "почти все частицы проходят\nне меняя направления", color=NEG,
            fontsize=10, ha="center", va="center")
    ax.text(2.6, -3.3, "ядра нарисованы\nне в масштабе", ha="center", va="center", fontsize=8.5, color=GREY)
    ax.set_title(r"Опыт Резерфорда: $\alpha$-частицы и золотая фольга")
    save(fig, "atom-rutherford-scattering.png")


def shell_atom(ax, c, n_in, n_out, z, r1=1.15, r2=2.0, nuc_r=0.42, phase=0.5, fs=12):
    for r in (r1, r2):
        ax.add_patch(Circle(c, r, fc="none", ec=GREY, lw=1.2, ls="--", zorder=1))
    ax.add_patch(Circle(c, nuc_r, fc=POS, ec=POS, zorder=3))
    ax.text(c[0], c[1], f"+{z}" if z > 1 else "+", color=PAPER, ha="center", va="center",
            fontsize=fs, fontweight="bold", zorder=4)
    for n, r, off in ((n_in, r1, 0.4), (n_out, r2, phase)):
        for i in range(n):
            a = off + 2 * np.pi * i / max(n, 1)
            charge(ax, (c[0] + r * np.cos(a), c[1] + r * np.sin(a)), "-", r=0.22, fs=11)


def planetary_model():
    fig, ax = canvas(6.4, 5.4, (-2.9, 2.9), (-2.6, 2.6))
    shell_atom(ax, (0, 0), 2, 1, 3, phase=0.7)
    ax.annotate("ядро", (0, 0.4), (-2.6, 1.9), fontsize=11, ha="center",
                arrowprops=dict(arrowstyle="-", color=INK))
    ax.annotate("электрон", (1.15 * np.cos(0.4 + np.pi) , 1.15 * np.sin(0.4 + np.pi)),
                (-2.6, -1.9), fontsize=11, ha="center",
                arrowprops=dict(arrowstyle="-", color=INK))
    ax.text(0, -2.55, "планетарная модель атома лития", ha="center", fontsize=11)
    save(fig, "atom-planetary-model.png")


def scale_nucleus():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1.2, 1]})
    # left: log scale
    a1.set_xscale("log")
    a1.set_xlim(1e-16, 1e-9)
    a1.set_ylim(-1, 2)
    a1.spines["left"].set_visible(False)
    a1.set_yticks([])
    a1.grid(True, axis="x", color=GRID)
    a1.set_axisbelow(True)
    for x, lab, col, y in ((1e-15, "ядро\n$10^{-15}$ м", POS, 0.6), (1e-10, "атом\n$10^{-10}$ м", NEG, 0.6)):
        a1.plot(x, 0, "o", color=col, ms=11)
        a1.text(x, y, lab, ha="center", va="bottom", color=col, fontsize=11)
    a1.annotate("", (1e-10, -0.45), (1e-15, -0.45),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
    a1.text(3e-13, -0.85, "в $10^5$ раз", ha="center", fontsize=11)
    a1.set_xlabel("размер, м (логарифмическая ось)")
    a1.set_title("Размеры ядра и атома")
    # right: 1 m -> 100 km
    a2.set_xlim(-8, 108)
    a2.set_ylim(-1, 2)
    a2.spines["left"].set_visible(False)
    a2.set_yticks([])
    a2.plot([0, 100], [0, 0], color=GREY, lw=1.5)
    for x, lab in ((0, "ядро\n$1$ м"), (100, "ядро соседнего\nатома")):
        a2.plot(x, 0, "o", color=POS, ms=8)
        a2.text(x, 0.4, lab, ha="center", va="bottom", fontsize=10.5, color=POS)
    a2.annotate("", (100, -0.45), (0, -0.45), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
    a2.text(50, -0.9, "порядка 100 км", ha="center", fontsize=11)
    a2.set_xlabel("расстояние, км")
    a2.set_title("Ядро увеличено до 1 м")
    save(fig, "atom-scale-nucleus.png")


def nucleus_lithium():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    hexpos = [(0, 0)] + [(1.05 * np.cos(a), 1.05 * np.sin(a)) for a in np.arange(6) * np.pi / 3 + 0.3]
    for ax, n, title, note in (
        (axes[0], 4, "литий-7", "$A=7$, $Z=3$, $N=4$\nбольшинство атомов лития"),
        (axes[1], 3, "литий-6", "$A=6$, $Z=3$, $N=3$\nнебольшая доля атомов"),
    ):
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2.6, 2)
        ax.set_aspect("equal")
        ax.axis("off")
        kinds = ["p", "n", "p", "n", "p", "n", "n"][: 3 + n]
        order = ["p", "n", "p", "n", "n", "p", "n"] if n == 4 else ["p", "n", "p", "n", "p", "n"]
        for pos, kd in zip(hexpos, order):
            if kd == "p":
                ax.add_patch(Circle(pos, 0.5, fc=POS_FILL, ec=POS, lw=1.6))
                ax.text(pos[0], pos[1], "+", ha="center", va="center", color=POS, fontsize=16, fontweight="bold")
            else:
                ax.add_patch(Circle(pos, 0.5, fc=NEUTRON, ec=tint(INK, 0.4), lw=1.6, hatch="////"))
        ax.set_title(title)
        ax.text(0, -2.2, note, ha="center", va="center", fontsize=10.5)
    axes[0].add_patch(Circle((-1.7, 1.7), 0.16, fc=POS_FILL, ec=POS))
    axes[0].text(-1.45, 1.7, "протон", va="center", fontsize=9.5)
    axes[0].add_patch(Circle((-1.7, 1.3), 0.16, fc=NEUTRON, ec=tint(INK, 0.4), hatch="////"))
    axes[0].text(-1.45, 1.3, "нейтрон", va="center", fontsize=9.5)
    fig.suptitle("Изотопы лития: разное число нейтронов при одном $Z$", y=1.02, fontsize=13)
    save(fig, "atom-nucleus-lithium.png")


def periodic_cell():
    fig, ax = canvas(10.5, 4.6, (0, 10.5), (-2.4, 3.2))
    cells = [
        ("Li", 3, "6,941", 7, 4, 0.2),
        ("H", 1, "1,0079", 1, 0, 3.6),
        ("C", 6, "12,011", 12, 6, 7.0),
    ]
    for sym, z, mass, a, n, x0 in cells:
        ax.add_patch(Rectangle((x0, 0.6), 3.0, 2.2, fc=PAPER, ec=INK, lw=1.8))
        ax.text(x0 + 0.2, 2.55, str(z), fontsize=14, va="top", color=POS)
        ax.text(x0 + 1.6, 1.9, sym, fontsize=34, ha="center", va="center", color=INK)
        ax.text(x0 + 1.5, 0.95, mass, fontsize=12, ha="center", va="center", color=NEG)
        ax.text(x0 + 1.5, -0.05, f"$A={a}$", fontsize=12, ha="center", color=NEG)
        ax.text(x0 + 1.5, -0.7, f"$Z={z}$", fontsize=12, ha="center", color=POS)
        ax.text(x0 + 1.5, -1.45, f"$N=A-Z={a}-{z}={n}$", fontsize=12, ha="center", color=INK)
    ax.text(5.25, 3.1, "клетка периодической системы: порядковый номер — это $Z$, масса округляется до $A$",
            ha="center", fontsize=11)
    save(fig, "atom-periodic-cell.png")


def ion_lithium():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
    cases = [(2, 1, "нейтральный атом Li", "$+3e$", "$-3e$", "$0$"),
             (2, 0, "положительный ион Li$^+$", "$+3e$", "$-2e$", "$+e$"),
             (2, 2, "отрицательный ион Li$^-$", "$+3e$", "$-4e$", "$-e$")]
    for ax, (n_in, n_out, title, qn, qe, qa) in zip(axes, cases):
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-3.6, 2.7)
        ax.set_aspect("equal")
        ax.axis("off")
    shell_atom(axes[0], (0, 0), 2, 1, 3, phase=0.7, fs=11)
    shell_atom(axes[1], (0, 0), 2, 0, 3, fs=11)
    shell_atom(axes[2], (0, 0), 2, 2, 3, phase=0.7, fs=11)
    for ax, (n_in, n_out, title, qn, qe, qa) in zip(axes, cases):
        ax.set_title(title, fontsize=11.5)
        ax.text(0, -2.55, f"$q_{{ядра}}={qn[1:-1]}$", ha="center", fontsize=10.5, color=POS)
        ax.text(0, -3.05, f"$q_{{эл}}={qe[1:-1]}$", ha="center", fontsize=10.5, color=NEG)
        ax.text(0, -3.55, f"$q_{{атома}}={qa[1:-1]}$", ha="center", fontsize=10.5, color=INK)
    save(fig, "atom-ion-lithium.png")


def mass_ladder():
    fig, ax = axes_grid(7.6, 3.4)
    ax.set_xscale("log")
    names = ["электрон", "нейтрон", "протон"]
    # The lecture gives 1837 for the proton only; the neutron is "about as heavy as the proton" there.
    # The reference value for the neutron is about 1839 (CODATA 1838.68), not from the lecture.
    vals = [1, 1839, 1837]
    labels = ["1", r"$\approx1839$ (справочно)", "1837"]
    cols = [NEG, NEUTRON, POS]
    ax.barh(names, vals, color=cols, height=0.55)
    ax.set_xlim(0.6, 1e5)
    for i, v in enumerate(vals):
        ax.text(v * 1.15, i, labels[i], va="center", fontsize=11)
    ax.set_xlabel("масса в массах электрона (протон — по лекции)")
    ax.set_title("Масса атома почти вся в ядре")
    save(fig, "atom-mass-ladder.png")


def rubbing_transfer():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    rng = np.random.default_rng(3)
    for ax, after in zip(axes, (False, True)):
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.8, 4.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0.3, 0.4), 3.9, 3.0, fc=tint(SKY, 0.8), ec=INK, lw=1.4))
        ax.add_patch(Rectangle((5.8, 0.4), 3.9, 3.0, fc=tint(WARM, 0.7), ec=INK, lw=1.4))
        ax.text(2.25, 3.65, "стекло", ha="center", fontsize=11)
        ax.text(7.75, 3.65, "шёлк", ha="center", fontsize=11)
        cols = [0.75 + i * 1.15 for i in range(3)]
        for x0 in (0.3, 5.8):
            for i, cx in enumerate(cols):
                for y in (2.7, 1.8):
                    mark(ax, (x0 + cx, y), "+", fs=15)
                    if not (x0 < 1 and after and y == 1.8):
                        mark(ax, (x0 + cx + 0.5, y), "-", fs=15)
        if after:
            for cx in cols:
                mark(ax, (5.8 + cx + 0.25, 0.85), "-", fs=15)
            # the gap between the bodies is 1.6 wide, too narrow for the caption, so it sits above the bodies
            arrow(ax, (4.3, 3.0), (5.7, 3.0), color=NEG, lw=2.2, ms=18)
            ax.text(5.0, 3.65, "электроны", ha="center", fontsize=9.5, color=NEG)
            ax.set_title("после трения", fontsize=11.5)
            ax.text(2.25, -0.35, "недостаток электронов: $+$", ha="center", fontsize=10.5, color=POS)
            ax.text(7.75, -0.35, "избыток электронов: $-$", ha="center", fontsize=10.5, color=NEG)
        else:
            ax.set_title("до трения", fontsize=11.5)
            ax.text(2.25, -0.35, "заряд $0$", ha="center", fontsize=11)
            ax.text(7.75, -0.35, "заряд $0$", ha="center", fontsize=11)
    save(fig, "atom-rubbing-transfer.png")


def metal_lattice():
    fig, ax = canvas(7.4, 4.8, (0, 8), (0, 5.2))
    rng = np.random.default_rng(7)
    ax.add_patch(Rectangle((0.2, 0.4), 7.6, 4.0, fc=SOFT, ec=INK, lw=1.4))
    ions = []
    for i in range(6):
        for j in range(3):
            x, y = 1.0 + i * 1.2, 1.1 + j * 1.3
            ions.append((x, y))
            ax.add_patch(Circle((x, y), 0.36, fc=POS_FILL, ec=POS, lw=1.6, zorder=2))
            ax.text(x, y, "+", ha="center", va="center", color=POS, fontsize=14, fontweight="bold", zorder=3)
    # The metal is neutral: as many free electrons as ions, none on an ion and no arrow into one
    electrons = []
    while len(electrons) < len(ions):
        x, y, a = rng.uniform(0.6, 7.4), rng.uniform(0.7, 4.0), rng.uniform(0, 2 * np.pi)
        end = (x + 0.4 * np.cos(a), y + 0.4 * np.sin(a))
        clear_of_ions = all(np.hypot(x - ix, y - iy) > 0.6 and np.hypot(end[0] - ix, end[1] - iy) > 0.45 for ix, iy in ions)
        clear_of_each_other = all(np.hypot(x - ex, y - ey) > 0.55 for ex, ey, _ in electrons)
        if clear_of_ions and clear_of_each_other:
            electrons.append((x, y, a))
    for x, y, a in electrons:
        ax.plot(x, y, "o", ms=6, color=NEG, zorder=4)
        arrow(ax, (x, y), (x + 0.4 * np.cos(a), y + 0.4 * np.sin(a)), color=NEG, lw=1, ms=7, z=4)
    ax.text(4, 4.85, "ионы в узлах решётки неподвижны, электроны свободны", ha="center", fontsize=10.5)
    ax.plot([], [], "o", color=NEG, label="свободный электрон")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08), frameon=False, ncol=2)
    save(fig, "atom-metal-lattice.png")


def ground_symbol(ax, x, y, s=0.3):
    ax.plot([x, x], [y, y - s], color=INK, lw=1.6)
    for k, w in enumerate((1.0, 0.65, 0.3)):
        ax.plot([x - s * w, x + s * w], [y - s - k * s * 0.35] * 2, color=INK, lw=1.6)


def induction_stages():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    ys = np.linspace(-0.75, 0.75, 4)
    xr = np.sqrt(np.clip(1.0 - ys ** 2, 0, None))
    for idx, ax in enumerate(axes):
        ax.set_xlim(-2.2, 3.4)
        ax.set_ylim(-2.4, 2.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(("1. пластина рядом", "2. заземляем шар", "3. убираем палец и пластину")[idx], fontsize=11.5)
        ax.add_patch(Circle((0, 0), 1.05, fc=SOFT, ec=INK, lw=1.6))
        if idx < 2:
            ax.add_patch(Rectangle((2.5, -1.3), 0.3, 2.6, fc=LIGHT, ec=INK, lw=1.4))
            for y in np.linspace(-1.0, 1.0, 5):
                mark(ax, (2.65, y), "-", fs=14)
        if idx == 0:
            for x, y in zip(xr, ys):
                mark(ax, (x * 0.8, y), "+", fs=13)
                mark(ax, (-x * 0.8, y), "-", fs=13)
        if idx == 1:
            for x, y in zip(xr, ys):
                mark(ax, (x * 0.8, y), "+", fs=13)
            ax.plot([-1.0, -1.6], [0, -0.7], color=INK, lw=2.5)
            ax.plot([-1.6, -1.6], [-0.7, -1.4], color=INK, lw=2.5)
            ground_symbol(ax, -1.6, -1.4)
            # the arrow runs beside the wire, not on it; the caption starts right of the ground symbol
            arrow(ax, (-1.2, 0.35), (-1.8, -0.25), color=NEG, lw=1.6, ms=12)
            ax.text(-1.1, -2.1, "электроны уходят в землю", fontsize=10, color=NEG, ha="left")
        if idx == 2:
            ang = np.linspace(0, 2 * np.pi, 9)[:-1]
            for a in ang:
                mark(ax, (0.8 * np.cos(a), 0.8 * np.sin(a)), "+", fs=13)
            ax.text(0.6, -1.9, "заряд шара противоположен\nзаряду пластины", ha="center", fontsize=10)
    save(fig, "atom-induction-stages.png")


def conductor_charge():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    # solid sphere
    ax = axes[0]
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.add_patch(Circle((0, 0), 1.0, fc=SOFT, ec=INK, lw=1.6))
    for a in np.linspace(0, 2 * np.pi, 13)[:-1]:
        mark(ax, (1.2 * np.cos(a), 1.2 * np.sin(a)), "+", fs=12)
    ax.text(0, 0, "внутри\nизбытка нет", ha="center", va="center", fontsize=10)
    ax.set_title("Шар: заряд снаружи", fontsize=11.5)
    # hollow sphere with rod
    ax = axes[1]
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.9)
    ax.add_patch(Wedge((0, 0), 1.0, 0, 360, width=0.12, fc=tint(INK, 0.8), ec=INK, lw=1.4))
    # the opening cuts the whole wall: the patch starts below the inner radius 0.88 so no inner arc crosses it
    ax.add_patch(Rectangle((-0.3, 0.8), 0.6, 0.45, fc=PAPER, ec="none", zorder=3))
    ax.plot([-0.3, -0.3], [0.827, 0.954], color=INK, lw=1.4, zorder=4)
    ax.plot([0.3, 0.3], [0.827, 0.954], color=INK, lw=1.4, zorder=4)
    rod = Polygon([[-0.05, 1.8], [0.15, 1.8], [0.25, 0.1], [0.05, 0.1]], fc=tint(WARM, 0.6), ec=INK, lw=1.2, zorder=5)
    ax.add_patch(rod)
    for a in np.linspace(0, 2 * np.pi, 13)[:-1]:
        if 1.2 < a < 1.95:
            continue
        mark(ax, (1.2 * np.cos(a), 1.2 * np.sin(a)), "+", fs=12)
    ax.set_title("Полость: палочку вводят внутрь", fontsize=11.5)
    # teardrop
    ax = axes[2]
    ax.set_xlim(-1.8, 2.2)
    ax.set_ylim(-1.3, 1.3)
    t = np.linspace(0, 2 * np.pi, 200)
    xs = np.cos(t)
    ys = 0.75 * np.sin(t) * (1 - xs) / 2 * 1.6
    xs = xs * 1.5 + 0.2
    ax.fill(xs, ys, fc=SOFT, ec=INK, lw=1.6)
    ax.set_xlim(-1.6, 2.4)
    ax.set_title("Острие: заряд собирается на нём", fontsize=11.5)
    # Signs sit 0.17 outside the contour along its normal; they are denser at the sharp end (right)
    def contour(tt):
        c = np.cos(tt)
        return 1.5 * c + 0.2, 0.6 * np.sin(tt) * (1 - c)

    def outside(tt, off=0.17, h=1e-4):
        x0, y0 = contour(tt)
        x1, y1 = contour(tt + h)
        dx, dy = x1 - x0, y1 - y0
        n = np.hypot(dx, dy)
        return x0 + off * dy / n, y0 - off * dx / n

    blunt = [np.pi + d for d in (0, 0.6, -0.6, 1.2, -1.2)]
    sharp = [s * 0.45 for s in (1, -1)] + [s * 0.8 for s in (1, -1)] + [s * 1.15 for s in (1, -1)]
    for tt in blunt + [v % (2 * np.pi) for v in sharp]:
        mark(ax, outside(tt), "+", fs=11)
    mark(ax, (1.92, 0.0), "+", fs=11)
    save(fig, "atom-conductor-charge.png")


def ion_wind():
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    titles = ("1. электрон в поле острия", "2. ударная ионизация", "3. ионный ветер")
    for i, ax in enumerate(axes):
        ax.set_xlim(-0.5, 6)
        ax.set_ylim(-2.8, 2.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[i], fontsize=11.5)
        ax.fill([-0.5, 1.0, -0.5], [-0.9, 0, 0.9], fc=SOFT, ec=INK, lw=1.6)
        # signs inside the triangle (tip at x=1.0)
        for sx, sy in ((0.65, 0.0), (0.35, 0.25), (0.35, -0.25), (0.05, 0.0)):
            mark(ax, (sx, sy), "+", fs=9)
    ax = axes[0]
    ax.add_patch(Circle((3.2, 0.9), 0.5, fc=CLOUD, ec=GREY, lw=1.4))
    ax.text(3.2, 0.9, "N$_2$", ha="center", va="center", fontsize=10)
    ax.plot(4.8, -0.7, "o", color=NEG, ms=7)
    arrow(ax, (4.7, -0.65), (1.5, -0.1), color=NEG, lw=1.6, ms=12)
    ax.text(3.5, -1.55, "быстрый электрон\nпритягивается к острию", ha="center", fontsize=9.5, color=NEG)
    ax = axes[1]
    ax.add_patch(Circle((3.2, 0.2), 0.5, fc=CLOUD, ec=GREY, lw=1.4))
    ax.text(3.2, 0.2, "N$_2$", ha="center", va="center", fontsize=10)
    # the incoming electron hits the molecule (solid); two electrons leave it for the tip (dashed, clear of the circle)
    ax.plot(5.3, 0.0, "o", color=NEG, ms=7)
    arrow(ax, (5.25, 0.0), (3.8, 0.15), color=NEG, lw=1.4, ms=10)
    for sy, ey in ((0.95, 0.5), (-0.6, -0.15)):
        ax.plot(3.5, sy, "o", color=NEG, ms=7)
        arrow(ax, (3.4, sy), (1.6, ey), color=NEG, lw=1.4, ms=10, ls="--")
    ax.text(3.2, -1.3, "электрон выбивает ещё один,\nоба летят к острию", ha="center", fontsize=9.5, color=NEG)
    ax = axes[2]
    for y in (1.5, 0.3, -1.0):
        ax.add_patch(Circle((3.0 + 0.4 * (y > 0), y), 0.4, fc=PAPER, ec=POS, lw=1.6))
        ax.text(3.0 + 0.4 * (y > 0), y, "+", ha="center", va="center", color=POS, fontsize=13, fontweight="bold")
        arrow(ax, (3.5 + 0.4 * (y > 0), y), (5.7, y), color=POS, lw=1.6, ms=12)
    ax.text(5.0, 1.0, "$F_{эл}$", fontsize=11, color=POS)
    ax.text(3.0, -2.35, "положительные ионы отталкиваются\nи уходят: острие разряжается", ha="center", fontsize=9.5)
    save(fig, "atom-ion-wind.png")


def lightning_rod():
    fig, ax = canvas(8.4, 5.6, (0, 10), (-1.2, 5.6))
    ax.plot([0, 10], [0, 0], color=INK, lw=2)
    ax.add_patch(Polygon([[4.3, 0], [4.3, 1.0], [5.1, 1.7], [5.9, 1.0], [5.9, 0]], fc=tint(WARM, 0.6), ec=INK, lw=1.6))
    # rod
    ax.plot([3.4, 3.4], [-0.5, 3.6], color=INK, lw=3.0)
    ax.plot([3.4], [3.6], "^", color=INK, ms=7)
    ground_symbol(ax, 3.4, -0.5)
    # cloud
    t = np.linspace(0, 2 * np.pi, 100)
    cx, cy = 3.6 + 2.2 * np.cos(t) * (1 + 0.12 * np.sin(5 * t)), 4.7 + 0.6 * np.sin(t)
    ax.fill(cx, cy, fc=CLOUD, ec=GREY, lw=1.6)
    for x, y in [(2.0, 4.8), (2.9, 5.0), (3.9, 4.9), (4.9, 5.0), (5.6, 4.7), (3.2, 4.4), (4.3, 4.5)]:
        mark(ax, (x, y), "-", fs=13)
    for x in (3.25, 3.55):
        mark(ax, (x, 3.85), "+", fs=11)
    # safe zone
    ax.plot([3.4, 3.4 + 3.6], [3.6, 0.0], color=GREEN, lw=1.6, ls="--")
    ax.add_patch(Polygon([[3.4, 3.6], [7.0, 0.0], [3.4, 0.0]], fc=GREEN, alpha=0.15, ec="none"))
    ax.text(5.1, 2.3, "безопасная область", fontsize=10, color=GREEN, ha="left")
    ax.text(3.7, 3.0, "$45^\\circ$", fontsize=10, color=GREEN)
    ax.text(3.2, 1.6, "стержень", fontsize=10, ha="right")
    ax.text(3.7, -0.85, "заземление", fontsize=10, ha="left")
    for x in (1.6, 2.4, 6.3, 7.4):
        mark(ax, (x, -0.35), "+", fs=13)
    arrow(ax, (3.4, 3.0), (3.4, 3.55), color=POS, lw=1.4, ms=10)
    ax.set_title("Громоотвод и безопасная область")
    save(fig, "atom-lightning-rod.png")


def cloud_earth():
    fig, ax = canvas(9, 5.4, (0, 12), (-0.6, 5.6))
    ax.add_patch(Rectangle((0, -0.5), 12, 0.5, fc=tint(COPPER, 0.6), ec="none"))
    hill = np.linspace(7, 11, 40)
    ax.fill_between(hill, 0, 0.9 * np.sin((hill - 7) / 4 * np.pi), fc=tint(COPPER, 0.6), ec="none")
    ax.plot([0, 7, 11, 12], [0, 0, 0, 0], color=INK, lw=1.8)
    ax.plot(hill, 0.9 * np.sin((hill - 7) / 4 * np.pi), color=INK, lw=1.8)
    # tree
    # the trunk goes under the crown (lower zorder)
    ax.plot([9, 9], [0.9, 2.2], color=COPPER, lw=4, zorder=1)
    ax.add_patch(Circle((9, 2.6), 0.6, fc=tint(GREEN, 0.6), ec=GREEN, lw=1.4, zorder=2))
    t = np.linspace(0, 2 * np.pi, 100)
    cx, cy = 5.5 + 4.3 * np.cos(t) * (1 + 0.1 * np.sin(6 * t)), 4.6 + 0.65 * np.sin(t)
    ax.fill(cx, cy, fc=CLOUD, ec=GREY, lw=1.6)
    for x in np.linspace(2.0, 9.0, 8):
        mark(ax, (x, 4.65 + 0.25 * np.sin(x * 3)), "-", fs=14)
    for x in (0.8, 2.0, 3.2, 4.4, 5.6, 6.6):
        mark(ax, (x, 0.25), "+", fs=14)
        arrow(ax, (x, 0.5), (x, 3.9), color=GREY, lw=0.9, ms=7, ls=":")
    for x in (8.7, 9.0, 9.3):  # induced charges at the top of the crown, inside its outline
        mark(ax, (x, 2.95), "+", fs=11, z=6)
    bolt = np.array([[8.8, 4.0], [9.2, 3.75], [8.85, 3.55], [9.1, 3.35]])
    ax.plot(bolt[:, 0], bolt[:, 1], color=GOLD, lw=3)
    ax.text(1.0, 2.6, "положительные заряды земли\nудерживают заряды тучи", fontsize=10, ha="left", zorder=8,
            bbox=dict(fc=PAPER, ec="none", pad=2.0))
    ax.text(9.8, 1.2, "влажное дерево:\nближе к туче, здесь\nпроскакивает молния", fontsize=9.5, ha="left")
    ax.set_title("Туча притягивает к себе противоположные заряды земли")
    save(fig, "atom-cloud-earth.png")


def franklin_kite():
    fig, ax = canvas(7, 5.6, (0, 8), (-0.6, 5.6))
    t = np.linspace(0, 2 * np.pi, 100)
    ax.fill(2.7 + 2.0 * np.cos(t) * (1 + 0.1 * np.sin(5 * t)), 5.0 + 0.45 * np.sin(t), fc=CLOUD, ec=GREY, lw=1.6)
    for x in (1.6, 2.4, 3.2, 4.0):
        mark(ax, (x, 5.0), "-", fs=12)
    ax.add_patch(Polygon([[4.7, 4.1], [5.3, 3.5], [4.7, 2.9], [4.1, 3.5]], fc=tint(WARM, 0.6), ec=INK, lw=1.6))
    ax.plot([4.1, 5.3], [3.5, 3.5], color=INK, lw=0.8)
    ax.plot([4.7, 4.7], [2.9, 4.1], color=INK, lw=0.8)
    # Top to bottom as in Franklin's letter: kite, wet twine, key where twine and silk join, dry silk ribbon, hand under a shelter
    # The shelter is a solid roof above the key: the wet twine passes under its right edge,
    # the key, the dry ribbon and the hand are all under it, and rain strokes stay outside
    ax.plot([4.7, 2.1, 1.4], [2.9, 1.35, 1.0], color=NEG, lw=1.6)
    for x, y in [(3.3, 3.1), (2.6, 2.6), (3.9, 3.7), (3.0, 3.6)]:
        ax.plot([x, x - 0.08], [y, y - 0.22], color=NEG, lw=1)
    ax.plot([1.4, 1.4], [1.0, 0.05], color=tint(COPPER, 0.4), lw=3, zorder=2)
    ax.plot(1.4, 1.0, "s", color=GOLD, ms=8, zorder=4)
    ax.add_patch(Rectangle((0.3, 1.55), 1.9, 0.1, fc=tint(COPPER, 0.3), ec=INK, lw=1.1, zorder=3))
    ax.plot([0.35, 0.35], [-0.4, 1.55], color=INK, lw=2.2, zorder=3)
    ax.add_patch(Circle((1.4, -0.05), 0.12, fc=tint(COPPER, 0.4), ec=INK, lw=1.1, zorder=4))
    ax.text(3.2, 1.45, "мокрая нить\n(проводник)", fontsize=9.5, ha="left", color=NEG)
    ax.text(0.3, 1.85, "навес", fontsize=9.5, ha="left", va="center")
    ax.text(1.7, 0.85, "металлический ключ", fontsize=9.5, ha="left", va="center")
    ax.text(1.7, 0.38, "сухая шёлковая\nлента (диэлектрик)", fontsize=9.5, ha="left", va="center")
    ax.text(1.65, -0.2, "рука человека\nв укрытии", fontsize=9.5, ha="left", va="center")
    ax.text(5.5, 3.5, "воздушный змей", fontsize=9.5, ha="left")
    ax.set_title("Опыт Франклина со змеем")
    save(fig, "atom-franklin-kite.png")


def electrostatic_motor():
    fig, ax = canvas(7.4, 5.2, (0, 8), (-0.6, 5.2))
    ax.add_patch(Rectangle((0.6, 0.6), 0.2, 3.6, fc=LIGHT, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((6.6, 0.6), 0.2, 3.6, fc=LIGHT, ec=INK, lw=1.4))
    for y in np.linspace(1.0, 3.8, 5):
        mark(ax, (0.35, y), "+", fs=13)
        mark(ax, (7.05, y), "-", fs=13)
    ax.text(0.7, 4.6, "кондуктор $+$", ha="center", fontsize=10)
    ax.text(6.7, 4.6, "кондуктор $-$", ha="center", fontsize=10)
    ax.plot([0.8], [2.4], marker=">", color=INK, ms=7)
    ax.plot([6.6], [2.4], marker="<", color=INK, ms=7)
    c = np.array([3.7, 2.4])
    for a in (0.0, np.pi / 3, 2 * np.pi / 3):
        d = np.array([np.cos(a), np.sin(a)]) * 2.05
        ax.plot([c[0] - d[0], c[0] + d[0]], [c[1] - d[1], c[1] + d[1]], color=COPPER, lw=2)
    ends = [np.array([np.cos(a), np.sin(a)]) * 2.05 for a in (0.0, np.pi / 3, 2 * np.pi / 3, np.pi, 4 * np.pi / 3, 5 * np.pi / 3)]
    for i, e in enumerate(ends):
        p = c + e
        if i == 3:
            charge(ax, tuple(p), "+", r=0.32)
            arrow(ax, (p[0] + 0.4, p[1] + 0.05), (p[0] + 1.3, p[1] + 0.05), color=POS, lw=2, ms=14)
        elif i == 0:
            charge(ax, tuple(p), "-", r=0.32)
            arrow(ax, (p[0] - 0.4, p[1] - 0.05), (p[0] - 1.3, p[1] - 0.05), color=NEG, lw=2, ms=14)
        else:
            ax.add_patch(Circle(tuple(p), 0.32, fc=tint(INK, 0.8), ec=INK, lw=1.4))
    ax.plot(*c, "o", color=INK, ms=5)
    ax.text(3.7, -0.4, "шарики от настольного тенниса, натёртые графитом, на соломинках", ha="center", fontsize=9.5)
    ax.set_title("Электростатический двигатель")
    save(fig, "atom-electrostatic-motor.png")


def task_neutralization():
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 6.6))
    ax = axes[0]
    ax.set_xlim(0, 12)
    ax.set_ylim(-1.5, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Шар до и после электризации: число протонов не меняется", fontsize=11.5)
    for x0, n_p, n_e, lab in ((1.5, 6, 6, "нейтральный шар"), (8.5, 6, 4, "заряжен положительно")):
        ax.add_patch(Circle((x0 + 0.5, 0.6), 1.7, fc=SOFT, ec=INK, lw=1.6))
        pos = [(x0 - 0.5 + (i % 3) * 0.75, 1.15 - (i // 3) * 0.75) for i in range(6)]
        for p in pos[:n_p]:
            mark(ax, p, "+", fs=13)
        for k, p in enumerate(pos[:n_e]):
            mark(ax, (p[0] + 0.35, p[1] - 0.35), "-", fs=13)
        ax.text(x0 + 0.5, -1.55, lab, ha="center", fontsize=10.5)
    arrow(ax, (4.0, 0.6), (7.0, 0.6), color=NEG, lw=2, ms=16)
    ax.text(5.5, 1.1, "часть электронов ушла", ha="center", fontsize=10, color=NEG)
    ax = axes[1]
    ax.set_xlim(0, 12)
    ax.set_ylim(-1.6, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Разноимённо заряженные шары: электроны идут туда, где их не хватает", fontsize=11.5, pad=12)
    ax.add_patch(Circle((2.0, 0.6), 1.5, fc=POS_FILL, ec=POS, lw=1.6))
    ax.add_patch(Circle((5.0, 0.6), 1.5, fc=tint(NEG, 0.85), ec=NEG, lw=1.6))
    ax.text(2.0, 0.6, "$+q$\nне хватает\n$N$ электронов", ha="center", va="center", fontsize=9.5, color=POS)
    ax.text(5.0, 0.6, "$-q$\nлишние\n$N$ электронов", ha="center", va="center", fontsize=9.5, color=NEG)
    arrow(ax, (4.2, 2.5), (2.8, 2.5), color=NEG, lw=2, ms=14)
    ax.text(3.5, 2.85, "$N$ электронов", ha="center", fontsize=9.5, color=NEG)
    ax.text(3.5, -1.3, "соприкосновение", ha="center", fontsize=10)
    arrow(ax, (6.4, 0.6), (8.0, 0.6), color=INK, lw=2, ms=16)
    # the balls are the same two as on the left, so their radius stays 1.5
    for x0 in (9.8, 12.8):
        ax.add_patch(Circle((x0, 0.6), 1.5, fc=SOFT, ec=INK, lw=1.6))
        ax.text(x0, 0.6, "$0$", ha="center", va="center", fontsize=13)
    ax.text(11.3, -1.3, "оба нейтральны, заряды не исчезли", ha="center", fontsize=10)
    ax.set_xlim(0, 14.6)
    save(fig, "atom-task-neutralization.png")


# ---------------------------------------------------------------- coulomb-


def forces_signs():
    fig, axes = plt.subplots(3, 1, figsize=(8.4, 4.8))
    rows = [("+", "+", "одноимённые: отталкиваются"), ("-", "-", "одноимённые: отталкиваются"),
            ("+", "-", "разноимённые: притягиваются")]
    for ax, (s1, s2, lab) in zip(axes, rows):
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.1, 1.3)
        ax.set_aspect("equal")
        ax.axis("off")
        charge(ax, (3.0, 0), s1, r=0.36)
        charge(ax, (7.0, 0), s2, r=0.36)
        if s1 == s2:
            arrow(ax, (2.55, 0), (1.2, 0), color=INK, lw=2.2, ms=16)
            arrow(ax, (7.45, 0), (8.8, 0), color=INK, lw=2.2, ms=16)
        else:
            arrow(ax, (3.45, 0), (4.8, 0), color=INK, lw=2.2, ms=16)
            arrow(ax, (6.55, 0), (5.2, 0), color=INK, lw=2.2, ms=16)
        ax.plot([3, 7], [-0.75, -0.75], color=GREY, lw=1.2)
        ax.text(5, -0.85, "$r$", ha="center", va="top", fontsize=11)
        ax.text(0.5, 0.75, lab, fontsize=10.5, ha="left")
        ax.text(1.5 if s1 == s2 else 4.1, 0.35, "$\\vec F_1$", fontsize=11, ha="center")
        ax.text(8.5 if s1 == s2 else 5.9, 0.35, "$\\vec F_2$", fontsize=11, ha="center")
    fig.suptitle("Силы лежат на прямой через заряды, $|F_1|=|F_2|=F$", y=1.0, fontsize=12.5)
    save(fig, "coulomb-forces-signs.png")


def torsion_balance():
    fig, ax = canvas(7.4, 6.2, (0, 8), (-1.0, 6.4))
    # glass case: holds the beam and the fixed ball, which comes in through a hole in the lid
    ax.add_patch(Rectangle((0.6, 1.2), 4.8, 3.6, fc="none", ec=GREY, lw=1.4, ls="--"))
    ax.text(3.0, 1.45, "стеклянный корпус", fontsize=9.5, ha="center", va="center", color=GREY)
    # scale head
    ax.add_patch(Rectangle((2.6, 5.4), 2.4, 0.35, fc=LIGHT, ec=INK, lw=1.4))
    for x in np.linspace(2.8, 4.8, 9):
        ax.plot([x, x], [5.75, 5.9], color=INK, lw=0.8)
    ax.text(5.2, 5.75, "шкала: угол\nзакручивания нити", fontsize=9.5, va="center", ha="left")
    # beam in perspective, as on the board: the ball is nearer to the viewer (lower), the disc is farther (higher)
    ax.plot([3.8, 3.8], [5.4, 3.56], color=INK, lw=1.2, zorder=2)
    ax.text(3.95, 4.6, "нить", fontsize=9.5)
    ax.plot([2.8, 5.0], [3.2, 4.0], color=COPPER, lw=3.2, zorder=1)
    ax.add_patch(Circle((2.8, 3.2), 0.2, fc=PAPER, ec=POS, lw=1.8, zorder=3))
    ax.text(2.8, 3.2, "+", color=POS, ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
    ax.add_patch(Circle((5.0, 4.0), 0.28, fc=LIGHT, ec=INK, lw=1.4, zorder=3))
    ax.text(2.45, 3.05, "заряженный\nшарик", fontsize=9, ha="right", va="center")
    ax.text(5.0, 3.5, "диск: гасит\nколебания и\nуравновешивает\nшарик", fontsize=9, ha="center", va="top")
    # fixed ball on dielectric rod: the rod enters through the lid and ends at the top of its ball,
    # the ball stands beside the beam so that the repulsion gives a torque
    ax.plot([2.3, 2.3], [5.6, 4.5], color=STRING, lw=3, zorder=1)
    ax.add_patch(Circle((2.3, 4.3), 0.2, fc=PAPER, ec=POS, lw=1.8, zorder=3))
    ax.text(2.3, 4.3, "+", color=POS, ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
    ax.text(2.15, 5.75, "диэлектрическая\nпалочка с шариком", fontsize=9, ha="right", va="center")
    # distance and forces, along the line between the balls
    ax.plot([2.33, 2.77], [4.1, 3.4], color=GREY, lw=1.1, ls=":", zorder=2)
    ax.text(2.4, 3.75, "$r$", fontsize=11, ha="right", va="center")
    arrow(ax, (2.88, 3.03), (3.2, 2.4), color=POS, lw=1.8, ms=12)
    arrow(ax, (2.22, 4.5), (1.9, 5.1), color=POS, lw=1.8, ms=12)
    ax.text(1.6, 4.9, "$F_2$", fontsize=11, color=POS, ha="center")
    ax.text(3.35, 2.35, "$F_1$", fontsize=11, color=POS)
    ax.text(3.8, -0.4, "Силы отталкивания скручивают нить;\nугол по шкале даёт силу порядка $10^{-11}$ Н", ha="center", va="center", fontsize=10)
    ax.set_title("Крутильные весы Кулона (схема)")
    save(fig, "coulomb-torsion-balance.png")


def inverse_square():
    r = np.linspace(2, 16, 300)  # cm
    f = K * (10e-9) ** 2 / (r * 1e-2) ** 2 * 1e3  # mN
    fig, ax = axes_grid(7.6, 4.9)
    ax.plot(r, f, color=POS, lw=2.4)
    r0 = 3.0
    f0 = K * (10e-9) ** 2 / (r0 * 1e-2) ** 2 * 1e3
    for k, txt, dy in ((1, "$r$: $F_0$", 0.14), (2, "$2r$: $\\dfrac{F_0}{4}$", 0.18), (5, "$5r$: $\\dfrac{F_0}{25}$", 0.22)):
        rr = r0 * k
        ff = K * (10e-9) ** 2 / (rr * 1e-2) ** 2 * 1e3
        ax.plot(rr, ff, "o", color=INK, ms=7, zorder=4)
        ax.plot([rr, rr], [0, ff], color=GREY, ls="--", lw=1)
        ax.text(rr + (0.3 if k < 5 else -0.4), ff + 0.05 + dy * 0.6, txt, fontsize=11, ha="left" if k < 5 else "right")
    ax.set_xlim(2, 16)
    ax.set_ylim(0, 2.4)
    ax.set_xlabel("$r$, см")
    ax.set_ylabel("$F$, мН")
    ax.set_title("Закон Кулона: $F \\sim 1/r^2$")
    save(fig, "coulomb-inverse-square.png")


def loglog_line():
    r = np.logspace(-2, 0, 100)  # m
    f = K * 1e-16 / r ** 2  # 10 nC each
    fig, ax = axes_grid(6.8, 4.9)
    ax.loglog(r * 100, f, color=POS, lw=2.4)
    ax.grid(True, which="both", color=GRID, lw=0.6)
    x1, x2 = 3, 30
    y1 = K * 1e-16 / (x1 * 1e-2) ** 2
    y2 = K * 1e-16 / (x2 * 1e-2) ** 2
    ax.plot([x1, x2, x2, x1], [y1, y1, y2, y1], color=INK, lw=1.2)
    ax.text(9, y1 * 1.15, "$\\times 10$ по $r$", ha="center", fontsize=10)
    ax.text(x2 * 1.12, np.sqrt(y1 * y2), "$\\div 100$\nпо $F$", va="center", fontsize=10)
    ax.set_xlabel("$r$, см")
    ax.set_ylabel("$F$, Н")
    ax.set_title("В двойном логарифмическом масштабе прямая с наклоном $-2$")
    ax.title.set_fontsize(11.5)
    save(fig, "coulomb-loglog.png")


def force_vs_charge():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    q = np.linspace(0, 30, 50)
    for ax in axes:
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    ax = axes[0]
    for q2, col in ((10, BLUE), (20, GREEN), (30, POS)):
        ax.plot(q, K * q * 1e-9 * q2 * 1e-9 / (0.03 ** 2) * 1e3, color=col, lw=2.2, label=f"$q_2={q2}$ нКл")
    ax.set_xlabel("$|q_1|$, нКл")
    ax.set_ylabel("$F$, мН")
    ax.set_title("Сила растёт прямо пропорционально $|q_1|$")
    ax.title.set_fontsize(11.5)
    ax.legend(frameon=False)
    ax.set_xlim(0, 30)
    ax.set_ylim(0)
    ax = axes[1]
    prod = np.linspace(0, 900, 50)  # nC^2
    ax.plot(prod, K * prod * 1e-18 / 0.03 ** 2 * 1e3, color=POS, lw=2.4)
    ax.set_xlabel("$|q_1||q_2|$, нКл$^2$")
    ax.set_ylabel("$F$, мН")
    ax.set_title("Сила от произведения зарядов, $r=3$ см")
    ax.title.set_fontsize(11.5)
    ax.set_xlim(0, 900)
    ax.set_ylim(0)
    save(fig, "coulomb-force-vs-charge.png")


def charge_doubling():
    fig, ax = canvas(8.0, 4.4, (0, 10), (-1.6, 3.6))
    # row 1: one body
    charge(ax, (1.0, 2.6), "+", r=0.4)
    ax.text(1.0, 1.95, "$q_1$", ha="center", fontsize=11)
    charge(ax, (5.0, 2.6), "+", r=0.4)
    ax.text(5.0, 1.95, "$q_2$", ha="center", fontsize=11)
    arrow(ax, (5.6, 2.6), (7.0, 2.6), color=POS, lw=2, ms=14)
    ax.text(7.3, 2.6, "$F$", color=POS, fontsize=12, ha="left", va="center")
    # row 2: two identical bodies
    charge(ax, (1.0, 0.0), "+", r=0.4)
    ax.text(1.0, -0.65, "$q_1$", ha="center", fontsize=11)
    charge(ax, (5.0, 0.42), "+", r=0.4)
    charge(ax, (5.0, -0.42), "+", r=0.4)
    ax.text(5.0, -1.2, "$2q_2$", ha="center", fontsize=11)
    arrow(ax, (5.6, 0.42), (7.0, 0.42), color=POS, lw=2, ms=14)
    arrow(ax, (5.6, -0.42), (7.0, -0.42), color=POS, lw=2, ms=14)
    ax.text(7.3, 0.0, "$F+F=2F$", color=POS, fontsize=12, ha="left", va="center")
    ax.set_title("Удвоенный заряд — два одинаковых тела, силы складываются")
    ax.title.set_fontsize(11.5)
    save(fig, "coulomb-charge-doubling.png")


def electric_vs_gravity():
    e, mp, G = 1.602e-19, 1.6726e-27, 6.674e-11
    k = 8.988e9
    r = np.logspace(-15, -9, 100)
    fe = k * e ** 2 / r ** 2
    fg = G * mp ** 2 / r ** 2
    fig, ax = axes_grid(7.6, 5.0)
    ax.loglog(r, fe, color=POS, lw=2.4, label="электрическая, $ke^2/r^2$")
    ax.loglog(r, fg, color=NEG, lw=2.4, label="гравитационная, $Gm_p^2/r^2$")
    ax.grid(True, which="both", color=GRID, lw=0.5)
    rr = 1e-12
    ax.annotate("", (rr, k * e ** 2 / rr ** 2), (rr, G * mp ** 2 / rr ** 2),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
    ax.text(rr * 1.3, np.sqrt(k * e ** 2 * G * mp ** 2) / rr ** 2, "в $1{,}2\\cdot10^{36}$ раз\nпри любом $r$", fontsize=10.5, va="center")
    ax.set_xlabel("расстояние между протонами, м")
    ax.set_ylabel("$F$, Н")
    ax.set_title("Два протона: электрическая сила против гравитационной")
    ax.title.set_fontsize(11.5)
    ax.legend(frameon=False, loc="lower left")
    save(fig, "coulomb-electric-vs-gravity.png")


def task_319():
    fig, ax = canvas(5.2, 5.4, (-2.4, 3.6), (-1.0, 5.0))
    ax.plot([-1.2, 1.4], [0, 0], color=INK, lw=3)
    ax.plot([0, 0], [0, 4.2], color=STRING, lw=4)
    charge(ax, (0, 0.5), "+", r=0.28)
    charge(ax, (0, 2.4), "+", r=0.28)
    ax.text(-0.5, 0.5, "$q_1$", ha="right", va="center", fontsize=12)
    ax.text(-0.5, 2.4, "$q_2$", ha="right", va="center", fontsize=12)
    ax.plot([0.9, 0.9], [0.5, 2.4], color=GREY, lw=1.2)
    ax.plot([0.8, 1.0], [0.5, 0.5], color=GREY, lw=1.2)
    ax.plot([0.8, 1.0], [2.4, 2.4], color=GREY, lw=1.2)
    ax.text(1.1, 1.45, "$h$", fontsize=12)
    arrow(ax, (0.5, 2.4), (0.5, 3.6), color=POS, lw=2.2, ms=16)
    ax.text(0.75, 3.5, "$F_{эл}$", color=POS, fontsize=12)
    arrow(ax, (0.5, 2.4), (0.5, 1.2), color=INK, lw=2.2, ms=16)
    # under the arrow tip, left of the dimension line at x = 0.9
    ax.text(0.5, 0.95, "$mg$", fontsize=12, ha="center", va="center")
    ax.text(0, 4.55, "диэлектрическая спица", fontsize=9.5, ha="center")
    ax.set_title("Верхний шарик в равновесии: $mg=F_{эл}$")
    ax.title.set_fontsize(11.5)
    save(fig, "coulomb-task-319.png")


def task_681():
    f = np.linspace(0, 0.5, 100)  # mN
    n = 0.1 / 1.6e-19 * np.sqrt(f * 1e-3 / K)
    fig, ax = axes_grid(6.8, 4.6)
    ax.plot(f, n / 1e11, color=POS, lw=2.4)
    ax.plot(0.23, 1.0, "o", color=INK, ms=8, zorder=4)
    ax.plot([0.23, 0.23], [0, 1.0], color=GREY, ls="--")
    ax.plot([0, 0.23], [1.0, 1.0], color=GREY, ls="--")
    ax.text(0.25, 0.8, "$0{,}23$ мН: $n\\approx10^{11}$", fontsize=10.5)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 1.7)
    ax.set_xlabel("$F$, мН")
    ax.set_ylabel("$n$, $10^{11}$ электронов")
    ax.set_title("Избыточные электроны: $n\\sim\\sqrt{F}$, $r=10$ см")
    ax.title.set_fontsize(11.5)
    save(fig, "coulomb-task-681.png")


def task_687():
    d = 4.0
    x = np.linspace(0.35, d - 0.2, 400)
    f1 = 90 / x ** 2
    f2 = 10 / (d - x) ** 2
    fig, ax = axes_grid(7.6, 4.8)
    ax.plot(x, f1, color=POS, lw=2.3, label="от $q_1=90$ нКл")
    ax.plot(x, f2, color=NEG, lw=2.3, label="от $q_2=10$ нКл")
    ax.plot(3.0, 10, "o", color=INK, ms=8, zorder=5)
    ax.plot([3.0, 3.0], [0, 10], color=GREY, ls="--")
    ax.text(2.45, 32, "равновесие: $x=3$ см\nот большего заряда", fontsize=10.5, ha="center")
    ax.set_xlim(0, d)
    ax.set_ylim(0, 50)
    ax.set_xlabel("$x$ — расстояние от заряда $q_1$, см")
    ax.set_ylabel("$F/(kq)$, нКл/см$^2$")
    ax.set_title("Силы на пробный заряд от двух зарядов")
    ax.title.set_fontsize(11.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    save(fig, "coulomb-task-687.png")


def task_687_scheme():
    fig, ax = canvas(8.4, 2.8, (0, 10), (-1.4, 1.6))
    ax.plot([1, 9], [0, 0], color=GREY, lw=1.2, zorder=1)
    charge(ax, (1.0, 0), "+", r=0.5)
    charge(ax, (9.0, 0), "+", r=0.28)
    ax.text(1.0, -0.85, "$q_1=90$ нКл", ha="center", fontsize=10.5)
    ax.text(9.0, -0.85, "$q_2=10$ нКл", ha="center", fontsize=10.5)
    xq = 1.0 + 8.0 * 0.75
    ax.plot(xq, 0, "o", color=INK, ms=9, zorder=6)
    arrow(ax, (xq + 0.15, 0.35), (xq + 1.3, 0.35), color=POS, lw=2, ms=14)
    arrow(ax, (xq - 0.15, 0.35), (xq - 1.3, 0.35), color=NEG, lw=2, ms=14)
    ax.text(xq + 0.7, 0.75, "$F_1$", color=POS, ha="center", fontsize=11)
    ax.text(xq - 0.7, 0.75, "$F_2$", color=NEG, ha="center", fontsize=11)
    ax.text(xq, -0.55, "$q$", ha="center", fontsize=11)
    ax.annotate("", (xq, -1.05), (1.0, -1.05), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(3.9, -1.3, "$x$", ha="center", fontsize=11)
    ax.annotate("", (9.0, -1.05), (xq, -1.05), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(8.0, -1.3, "$d-x$", ha="center", fontsize=11)
    ax.set_title("Пробный заряд $q$ на прямой между зарядами, $d=4$ см")
    ax.title.set_fontsize(11.5)
    save(fig, "coulomb-task-687-scheme.png")


def task_678():
    r = np.linspace(4, 25, 200)  # cm
    f = K * 1e-6 * 10e-9 / (r * 1e-2) ** 2 * 1e3  # mN
    fig, ax = axes_grid(6.8, 4.6)
    ax.plot(r, f, color=POS, lw=2.4)
    ax.plot(10, 9, "o", color=INK, ms=8, zorder=4)
    ax.plot([10, 10], [0, 9], color=GREY, ls="--")
    ax.plot([0, 10], [9, 9], color=GREY, ls="--")
    ax.text(10.6, 9.6, "$9$ мН при $r=10$ см", fontsize=10.5)
    ax.set_xlim(4, 25)
    ax.set_ylim(0, 60)
    ax.set_xlabel("$r$, см")
    ax.set_ylabel("$F$, мН")
    ax.set_title("$q_1=1$ мкКл, $q_2=10$ нКл")
    save(fig, "coulomb-task-678.png")


if __name__ == "__main__":
    for fn in (
        rutherford_scattering, planetary_model, scale_nucleus, nucleus_lithium, periodic_cell,
        ion_lithium, mass_ladder, rubbing_transfer, metal_lattice, induction_stages,
        conductor_charge, ion_wind, lightning_rod, cloud_earth, franklin_kite,
        electrostatic_motor, task_neutralization, forces_signs, torsion_balance,
        inverse_square, loglog_line, force_vs_charge, charge_doubling, electric_vs_gravity,
        task_319, task_681, task_687, task_687_scheme, task_678,
    ):
        fn()
