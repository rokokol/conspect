"""Figures for the notes "Равнодействующая сила" and "Сила трения" (course Физика 7-9, lessons 38-41).

Run: python3 forces_resultant_friction.py
PNG files go to content/05. Силы/00. Вложения/, prefixes resultant-*, friction-*, combined-*
"""
from forces_common import *

RESULT = VIOLET  # the resultant force and the elastic force
FRICTION = ACCENT  # a friction or a drag force
FRICTION2 = COPPER  # a second friction force beside FRICTION
WEIGHT = BLUE  # the weight and the support force
OIL = tint(WARM, 0.4)
WOOD_D = tint(COPPER, 0.15)  # a darker wood, the hatched block
WATER = tint(SKY, 0.6)

F_TR = r"F_\mathrm{тр}"
F_TYAZH = r"F_\mathrm{тяж}"


def ground(ax, x0, x1, y, n=None, h=0.18):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.6, zorder=2)
    if not h:
        return
    n = n or int((x1 - x0) / 0.35)
    for x in np.linspace(x0 + 0.1, x1, n):
        ax.plot([x, x - 0.16], [y, y - h], color=GREY, lw=1)


def block(ax, x, y, w=2.2, h=1.0, face=WOOD, hatch=None, lw=1.5, z=3):
    ax.add_patch(Rectangle((x, y), w, h, fc=face, ec=INK, lw=lw, hatch=hatch, zorder=z))


def lab(ax, x, y, text, color=INK, fs=12, ha="center", va="center", **kw):
    ax.text(x, y, text, color=color, fontsize=fs, ha=ha, va=va, **kw)


def dot(ax, x, y, color=INK, r=0.06):
    ax.add_patch(Circle((x, y), r, fc=color, ec=color, zorder=6))


# ---------------------------------------------------------------- resultant

def resultant_cart_replacement():
    fig, axes = blank_row(2, 12.5, 2.9, (-0.5, 6.5), (-0.3, 2.6))
    ax = axes[0]
    cart(ax, 1.8, 0.4, w=2.4, h=0.9)
    ground(ax, 0.3, 6.2, 0.4 - 0.17, h=0.0)
    # rope and pulling force at the front, pushing force at the back
    ax.plot([4.2, 4.7], [0.85, 0.85], color=INK, lw=1.4)
    arrow(ax, (4.7, 0.85), (5.9, 0.85), color=FORCE, lw=2.4)
    lab(ax, 5.3, 1.25, r"$\vec F_1$", FORCE, 14)
    lab(ax, 5.3, 0.45, "тянет верёвкой", INK, 10)
    arrow(ax, (0.5, 0.85), (1.75, 0.85), color=BLUE, lw=2.4)
    lab(ax, 1.05, 1.25, r"$\vec F_2$", BLUE, 14)
    lab(ax, 1.0, 0.45, "толкает", INK, 10)
    lab(ax, 3.0, 2.15, "Две силы вдоль одной прямой", INK, 12, weight="bold")
    arrow(ax, (2.2, 1.6), (3.8, 1.6), color=GREY, lw=1.6)
    lab(ax, 3.0, 1.75, r"скорость меняется", NOTE, 10, va="bottom")
    ax = axes[1]
    cart(ax, 1.8, 0.4, w=2.4, h=0.9)
    ground(ax, 0.3, 6.2, 0.4 - 0.17, h=0.0)
    arrow(ax, (0.5, 0.85), (1.75, 0.85), color=RESULT, lw=2.4)
    arrow(ax, (0.5, 0.85), (1.75, 0.85), color=RESULT, lw=2.4)
    lab(ax, 1.05, 1.25, r"$\vec R$", RESULT, 14)
    lab(ax, 1.0, 0.45, "толкает", INK, 10)
    lab(ax, 3.0, 2.15, "Одна сила, то же действие", INK, 12, weight="bold")
    arrow(ax, (2.2, 1.6), (3.8, 1.6), color=GREY, lw=1.6)
    lab(ax, 3.0, 1.75, r"скорость меняется так же", NOTE, 10, va="bottom")
    fig.text(0.5, -0.02, r"$\vec F_1$ и $\vec F_2$ — составляющие силы, $\vec R$ — равнодействующая", ha="center", fontsize=12)
    save(fig, "resultant-cart-replacement.png")


def _rod_panel(ax, title, down, up, r_down, x0=0.0):
    """Vertical rod of a dynamometer with forces down and up; scale 0.28 units per newton."""
    s = 0.28
    ax.plot([x0, x0], [-0.2, 4.4], color=INK, lw=3, zorder=2)
    y0 = 2.0
    dot(ax, x0, y0)
    xo = -0.35
    for i, f in enumerate(down):
        arrow(ax, (x0 + xo, y0 - sum(down[:i]) * s), (x0 + xo, y0 - sum(down[: i + 1]) * s), color=WEIGHT if i else FORCE, lw=2.6)
        lab(ax, x0 + xo - 0.35, y0 - (sum(down[:i]) + f / 2) * s, f"${f}$ Н", WEIGHT if i else FORCE, 11)
    for f in up:
        arrow(ax, (x0 + xo, y0), (x0 + xo, y0 + f * s), color=FRICTION, lw=2.6)
        lab(ax, x0 + xo - 0.35, y0 + f * s / 2, f"${f}$ Н", FRICTION, 11)
    r = abs(r_down)
    xr = x0 + 0.5
    if r_down > 0:
        arrow(ax, (xr, y0), (xr, y0 - r * s), color=RESULT, lw=3)
        lab(ax, xr + 0.15, y0 - r * s / 2, f"$R={r}$ Н\nвниз", RESULT, 11, ha="left")
    elif r_down < 0:
        arrow(ax, (xr, y0), (xr, y0 + r * s), color=RESULT, lw=3)
        lab(ax, xr + 0.15, y0 + r * s / 2, f"$R={r}$ Н\nвверх", RESULT, 11, ha="left")
    lab(ax, x0, 4.75, title, INK, 11.5, weight="bold")


def resultant_dynamometer_cases():
    fig, axes = blank_row(3, 12.5, 4.9, (-1.3, 1.9), (-1.3, 4.9))
    _rod_panel(axes[0], "Силы в одну сторону", [2, 5], [], 7)
    _rod_panel(axes[1], "Против, большая вниз", [5], [3], 2)
    _rod_panel(axes[2], "Против, большая вверх", [5], [8], -3)
    for ax, t in zip(axes, ("$R = 2 + 5$", "$R = 5 - 3$", "$R = 8 - 5$")):
        lab(ax, 0.1, -0.95, t + " Н", INK, 12)
    fig.text(0.5, 0.0, "Масштаб: $1$ Н $\\leftrightarrow$ $0{,}28$ условной клетки; показание динамометра совпадает с $R$", ha="center", fontsize=10.5, color=NOTE)
    save(fig, "resultant-dynamometer-cases.png")


def resultant_r_vs_f2():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    f = np.linspace(0, 9, 100)
    ax = axes[0]
    ax.plot(f, 5 + f, color=RESULT, lw=2.4)
    for x in (0, 2, 5):
        ax.plot([x], [5 + x], "o", color=RESULT)
    ax.annotate(r"$2+5=7$ Н", (2, 7), (3.4, 5.2), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.set(xlabel=r"$F_2$ вниз, Н", ylabel=r"$R$ вниз, Н", xlim=(0, 9), ylim=(0, 14))
    ax.set_title(r"Обе силы вниз: $R = F_1 + F_2$", fontsize=12)
    ax.grid(color=GRID)
    ax = axes[1]
    r = 5 - f
    ax.axhline(0, color=INK, lw=1.2)
    ax.plot(f, r, color=RESULT, lw=2.4)
    ax.plot(f, np.abs(r), color=GREY, lw=1.6, ls="--", label=r"модуль $|R|$")
    for x, name in ((3, "$5-3=2$ Н, вниз"), (8, "$8-5=3$ Н, вверх"), (5, "$R=0$")):
        ax.plot([x], [5 - x], "o", color=RESULT)
        ax.annotate(name, (x, 5 - x), {3: (3.6, 3.6), 8: (5.4, -3.9), 5: (5.5, 1.3)}[x], arrowprops=dict(arrowstyle="->", color=GREY), fontsize=10.5)
    ax.fill_between(f, 0, r, where=r > 0, color=RESULT, alpha=0.08)
    ax.fill_between(f, 0, r, where=r < 0, color=FRICTION, alpha=0.10)
    ax.text(7.0, -0.8, "$R$ вверх", color=FRICTION, fontsize=11)
    ax.text(0.8, 1.0, "$R$ вниз", color=RESULT, fontsize=11)
    ax.set(xlabel=r"$F_2$ вверх, Н", ylabel=r"$R$ вниз, Н", xlim=(0, 9), ylim=(-5, 6))
    ax.set_title(r"$F_1 = 5$ Н вниз, $F_2$ вверх", fontsize=12)
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    save(fig, "resultant-r-vs-f2.png")


def resultant_equilibrium():
    fig, axes = blank_row(2, 11, 4.2, (-0.8, 4.8), (-1.9, 3.9))
    for ax, moving in zip(axes, (False, True)):
        ground(ax, -0.4, 4.6, 0.0, h=0.16)
        block(ax, 1.0, 0.0, w=2.2, h=1.1)
        dot(ax, 2.1, 0.55)
        arrow(ax, (2.1, 0.55), (2.1, 2.25), color=BLUE, lw=2.6)
        arrow(ax, (2.1, 0.55), (2.1, -0.75), color=GREEN, lw=2.6)
        lab(ax, 2.55, 2.0, r"$\vec F_\mathrm{упр}$", BLUE, 13)
        lab(ax, 2.6, -0.55, r"$\vec F_\mathrm{тяж}$", GREEN, 13)
        if moving:
            arrow(ax, (1.0, 1.45), (0.1, 1.45), color=GREY, lw=1.6, scale=10) if False else None
            arrow(ax, (2.3, 3.2), (3.7, 3.2), color=GREY, lw=1.8)
            lab(ax, 3.0, 3.5, r"$\vec v = \mathrm{const}$", NOTE, 11)
            lab(ax, 2.1, -1.15, r"движется равномерно: $R = 0$", INK, 11.5)
        else:
            lab(ax, 2.1, -1.15, r"покоится: $R = 0$", INK, 11.5)
    fig.text(0.5, 0.0, r"$F_\mathrm{упр} = F_\mathrm{тяж}$, силы направлены противоположно: они компенсируют друг друга", ha="center", fontsize=11.5)
    save(fig, "resultant-equilibrium.png")


def _arrow_row(ax, y, forces, x0, unit, colors, labels=True, fs=11):
    """Chain of horizontal arrows; sign of a force = direction (right positive)."""
    x = x0
    for f, c in zip(forces, colors):
        arrow(ax, (x, y), (x + f * unit, y), color=c, lw=2.6)
        lab(ax, x + f * unit / 2, y + 0.26, f"${abs(f)}$ Н", c, fs)
        x += f * unit
    return x


def resultant_problem_380():
    fig, ax = blank(11, 4.4, (-0.6, 10.2), (-0.4, 5.0))
    unit = 0.9
    # grid, one cell = 1 N
    for k in range(0, 10):
        ax.plot([k * unit + 0.0] * 2, [-0.1, 4.6], color=GRID, lw=0.7, zorder=0)
    lab(ax, 4.5, 4.75, "Клетка $\\leftrightarrow$ $1$ Н", NOTE, 10)
    # same direction
    y = 3.4
    lab(ax, -0.5, y + 0.8, "Силы в одну сторону", INK, 11.5, ha="left", weight="bold")
    arrow(ax, (0, y), (2 * unit, y), color=BLUE, lw=2.6)
    arrow(ax, (2 * unit, y), (7 * unit, y), color=GREEN, lw=2.6)
    lab(ax, unit, y + 0.27, r"$F_1=2$ Н", BLUE, 11)
    lab(ax, 4.5 * unit, y + 0.27, r"$F_2=5$ Н", GREEN, 11)
    arrow(ax, (0, y - 0.55), (7 * unit, y - 0.55), color=RESULT, lw=3)
    lab(ax, 3.5 * unit, y - 0.88, r"$R = 2 + 5 = 7$ Н", RESULT, 12)
    # opposite
    y = 1.2
    lab(ax, -0.5, y + 0.85, "Силы в противоположные стороны", INK, 11.5, ha="left", weight="bold")
    arrow(ax, (2 * unit, y + 0.15), (0, y + 0.15), color=BLUE, lw=2.6)
    arrow(ax, (0, y - 0.25), (5 * unit, y - 0.25), color=GREEN, lw=2.6)
    lab(ax, unit, y + 0.42, r"$F_1=2$ Н", BLUE, 11)
    lab(ax, 3.7 * unit, y - 0.55, r"$F_2=5$ Н", GREEN, 11)
    arrow(ax, (0, y - 0.95), (3 * unit, y - 0.95), color=RESULT, lw=3)
    lab(ax, 3.35 * unit, y - 1.25, r"$R = 5 - 2 = 3$ Н, в сторону $F_2$", RESULT, 12, ha="left")
    save(fig, "resultant-problem-380.png")


def resultant_problem_381():
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 5.4))
    unit = 0.36
    cases = [
        ((3, 4, 5), "Все вправо", 12),
        ((-3, 4, 5), "Меньшая влево", 6),
        ((3, -4, 5), "Средняя влево", 4),
        ((3, 4, -5), "Большая влево", 2),
    ]
    cols = (BLUE, GREEN, FRICTION)
    for ax, (fs, title, R) in zip(axes.flat, cases):
        ax.set_xlim(-6.5, 13.5)
        ax.set_ylim(-0.6, 4.0)
        ax.axis("off")
        ax.set_title(title, fontsize=11.5)
        ax.plot([0, 0], [-0.3, 3.7], color=GRID, lw=1)
        for i, (f, c) in enumerate(zip(fs, cols)):
            y = 3.0 - i * 0.9
            arrow(ax, (0, y), (f, y), color=c, lw=2.4)
            ax.text(f + (0.4 if f > 0 else -0.4), y, f"${abs(f)}$ Н", color=c, ha="left" if f > 0 else "right", va="center", fontsize=11)
        arrow(ax, (0, 0.2), (sum(fs), 0.2), color=RESULT, lw=3.2)
        ax.text(sum(fs) + 0.4, 0.2, rf"$R={R}$ Н", color=RESULT, ha="left", va="center", fontsize=12)
    fig.tight_layout()
    save(fig, "resultant-problem-381.png")


def resultant_problem_381_values():
    fig, ax = plt.subplots(figsize=(11, 2.6))
    options = [1, 2, 3, 4, 6, 10, 12, 15]
    ok = {2, 4, 6, 12}
    ax.axhline(0, color=INK, lw=1.4)
    for v in range(0, 17):
        ax.plot([v, v], [-0.08, 0.08], color=GREY, lw=1)
    for v in options:
        good = v in ok
        ax.scatter([v], [0], s=330, color=GREEN if good else FORCE, zorder=3, alpha=0.9)
        ax.text(v, 0, str(v), color=PAPER, ha="center", va="center", fontsize=11, weight="bold", zorder=4)
    ax.text(8, 0.55, r"Значения $|R|$ при всех расстановках знаков: $2$, $4$, $6$, $12$ Н", ha="center", fontsize=11.5)
    ax.text(8, -0.55, "зелёные — возможны, красные — невозможны", ha="center", fontsize=10, color=NOTE)
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.9, 0.95)
    ax.axis("off")
    save(fig, "resultant-problem-381-values.png")


# ----------------------------------------------------------------- friction

def friction_block_forces():
    fig, ax = blank(8.5, 5.0, (-0.8, 7.8), (-2.3, 4.0))
    ground(ax, 0.2, 7.2, 0.0, h=0.18)
    block(ax, 1.9, 0.0, w=3.0, h=1.6)
    cx, cy = 3.4, 0.8
    dot(ax, cx, cy)
    # the block is at rest: N = F_тяж = P (length 1.9) and F = F_тр (length 1.8)
    arrow(ax, (cx, cy), (cx, 2.7), color=BLUE, lw=2.6)
    lab(ax, cx + 0.45, 2.55, r"$\vec N$", BLUE, 14)
    arrow(ax, (cx, cy), (cx, -1.1), color=GREEN, lw=2.6)
    lab(ax, cx + 0.5, -0.95, r"$\vec F_\mathrm{тяж}$", GREEN, 14)
    arrow(ax, (cx - 0.6, 0.0), (cx - 0.6, -1.9), color=WEIGHT, lw=2.0, style="-|>")
    lab(ax, cx - 1.0, -1.3, r"$\vec P$", WEIGHT, 14)
    arrow(ax, (4.9, 1.1), (6.7, 1.1), color=FORCE, lw=2.6)
    lab(ax, 6.0, 1.5, r"$\vec F$", FORCE, 14)
    arrow(ax, (1.9, 0.0), (0.1, 0.0), color=FRICTION, lw=3)
    lab(ax, 1.1, 0.35, r"$\vec F_\mathrm{тр}$", FRICTION, 14)
    lab(ax, -0.6, 3.6, r"$\vec N$ — сила нормального давления" "\n" r"$\vec F_\mathrm{тр}$ — сила трения" "\n" r"$\vec P$ — вес бруска, приложен к опоре", INK, 9.5, ha="left", va="top")
    save(fig, "friction-block-forces.png")


def friction_static_kinetic_graph():
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    fm = 0.4
    x1 = np.linspace(0, fm, 20)
    ax.plot(x1, x1, color=FRICTION, lw=3)
    ax.plot([fm, 1.05], [fm, fm], color=GREEN, lw=3)
    for x in (0.1, 0.2, 0.3):
        ax.plot([x], [x], "o", color=FRICTION, ms=6)
    ax.plot([fm], [fm], "o", color=INK, ms=8, zorder=5)
    ax.plot([fm, fm], [0, fm], color=GREY, ls="--", lw=1)
    ax.plot([0, fm], [fm, fm], color=GREY, ls="--", lw=1)
    ax.annotate(r"$F_\mathrm{тр\,макс} = 0{,}4$ Н" "\nначинается скольжение", (fm, fm), (0.5, 0.15), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.text(0.03, 0.55, "трение покоя\n" r"$F_\mathrm{тр} = F$, тело в покое", color=FRICTION, fontsize=11.5, va="center")
    ax.text(0.62, 0.47, "трение скольжения\n" r"$F_\mathrm{тр} \approx$ const", color=GREEN, fontsize=11.5, va="bottom")
    ax.annotate("", (0.4, 0.62), (0.0, 0.62), arrowprops=dict(arrowstyle="<->", color=FRICTION))
    ax.annotate("", (1.05, 0.62), (0.4, 0.62), arrowprops=dict(arrowstyle="<->", color=GREEN))
    ax.text(0.72, 0.66, r"при $F = 0{,}4$ Н — равномерно," "\n" r"при $F > 0{,}4$ Н — с ускорением", ha="center", color=GREEN, fontsize=10)
    ax.set(xlabel=r"приложенная сила $F$, Н", ylabel=r"$F_\mathrm{тр}$, Н", xlim=(0, 1.05), ylim=(0, 0.8))
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticks([0, 0.2, 0.4, 0.6])
    ax.grid(color=GRID)
    save(fig, "friction-static-kinetic-graph.png")


def friction_stiction_peak():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    xs = [0, 0.4, 0.43, 0.5, 1.0]
    ys = [0, 0.4, 0.33, 0.32, 0.32]
    ax.plot([0, 0.4], [0, 0.4], color=FRICTION, lw=3)
    ax.plot([0.4, 0.43], [0.4, 0.31], color=INK, lw=2)
    ax.plot([0.43, 1.0], [0.31, 0.31], color=GREEN, lw=3)
    ax.annotate(r"максимум трения покоя", (0.4, 0.4), (0.12, 0.5), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.annotate("трение скольжения\nчуть меньше", (0.7, 0.31), (0.6, 0.12), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.set(xlabel=r"$F$", ylabel=r"$F_\mathrm{тр}$", xlim=(0, 1), ylim=(0, 0.6), xticks=[], yticks=[])
    ax.set_title("Явление застоя: зубец на графике", fontsize=12)
    ax.grid(color=GRID)
    ax = axes[1]
    t = np.linspace(0, 6, 800)
    saw = (t % 1.0)
    ax.plot(t, saw, color=FORCE, lw=2)
    ax.set(xlabel="время", ylabel="отклонение струны", xticks=[], yticks=[], ylim=(-0.1, 1.2))
    ax.set_title("Смычок по струне: сцепление, срыв, снова сцепление", fontsize=12)
    ax.text(0.5, 1.07, "сцепление", color=FRICTION, fontsize=10, ha="center")
    ax.text(1.07, 0.5, "срыв", color=GREEN, fontsize=10, rotation=90, va="center")
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "friction-stiction-peak.png")


def friction_ftr_vs_n_data():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    N = np.array([1.9, 2.9, 3.9])
    F = np.array([0.4, 0.6, 0.8])
    ax = axes[0]
    x = np.linspace(0, 4.4, 20)
    ax.plot(x, 0.21 * x, color=FRICTION, lw=2.4, label=r"прямая $F_\mathrm{тр} = 0{,}21\,N$")
    ax.plot(N, F, "o", color=INK, ms=8, zorder=4, label="измерения")
    for n, f in zip(N, F):
        ax.annotate(f"({num(n, '')}; {num(f, '')})", (n, f), (n + 0.1, f - 0.13), fontsize=10)
    ax.set(xlabel=r"$N = P$, Н", ylabel=r"$F_\mathrm{тр}$, Н", xlim=(0, 4.4), ylim=(0, 1.0))
    ax.set_title("Сила трения пропорциональна $N$", fontsize=12)
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    ax = axes[1]
    mu = F / N
    ax.bar([r"$1{,}9$", r"$2{,}9$", r"$3{,}9$"], mu, color=[NOTE, NOTE, NOTE], width=0.55)
    for i, m in enumerate(mu):
        ax.text(i, m + 0.006, num(m, 3), ha="center", fontsize=10.5)
    ax.axhline(0.21, color=FRICTION, ls="--", lw=1.4)
    ax.set(xlabel=r"$N$, Н", ylabel=r"$F_\mathrm{тр}/N$", ylim=(0, 0.3))
    ax.set_title(r"Отношение $F_\mathrm{тр}/N \approx 0{,}21$", fontsize=12)
    ax.grid(color=GRID, axis="y")
    fig.tight_layout()
    save(fig, "friction-ftr-vs-n-data.png")


def friction_mu_lines():
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    n = np.linspace(0, 4, 10)
    for mu, name, c in ((0.34, "дерево по картону, $\\mu = 0{,}34$", FORCE), (0.21, "дерево по дереву, $\\mu = 0{,}21$", FRICTION), (0.02, "сталь по льду, $\\mu = 0{,}02$", BLUE)):
        ax.plot(n, mu * n, color=c, lw=2.6, label=name)
    ax.set(xlabel=r"$N$, Н", ylabel=r"$F_\mathrm{тр}$, Н", xlim=(0, 4), ylim=(0, 1.5))
    ax.set_title(r"$F_\mathrm{тр} = \mu N$: наклон прямой — коэффициент трения", fontsize=12)
    ax.grid(color=GRID)
    ax.legend(frameon=False, loc="upper left")
    ax.annotate("одна и та же $N$ —\nбольше $\\mu$, больше $F_\\mathrm{тр}$", (3, 1.02), (2.0, 0.1), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=10.5)
    save(fig, "friction-mu-lines.png")


def friction_area_independence():
    fig, axes = blank_row(2, 10.5, 3.6, (-0.5, 5.0), (-1.0, 3.2))
    for ax, (w, h, name) in zip(axes, ((3.0, 1.0, "широкой гранью"), (1.0, 3.0, "узкой гранью"))):
        ground(ax, -0.3, 4.6, 0.0, h=0.15)
        block(ax, 0.9, 0.0, w=w, h=h)
        yc = min(h * 0.6, 0.9)
        arrow(ax, (0.9 + w, yc), (0.9 + w + 1.2, yc), color=FORCE, lw=2.4)
        arrow(ax, (0.9, 0.0), (-0.1, 0.0), color=FRICTION, lw=3)
        lab(ax, 0.3, 0.42, r"$\vec F_\mathrm{тр}$", FRICTION, 13)
        lab(ax, 0.9 + w + 1.4, yc + 0.35, r"$\vec F$", FORCE, 13)
        lab(ax, 2.3, -0.65, f"брусок лежит {name}", INK, 11)
    fig.text(0.5, 0.0, r"Сила трения та же: от площади соприкосновения она не зависит", ha="center", fontsize=11.5)
    save(fig, "friction-area-independence.png")


def friction_surface_roughness():
    fig, ax = blank(9.5, 4.6, (-0.3, 9.3), (-0.4, 4.3))
    rng = np.random.default_rng(3)
    xs = np.linspace(0, 9, 60)
    low = 1.6 + 0.35 * rng.standard_normal(60).cumsum() * 0.0 + 0.32 * np.abs(np.sin(xs * 3.1)) + 0.1 * rng.random(60)
    upp = 2.05 - 0.32 * np.abs(np.sin(xs * 2.7 + 1)) - 0.1 * rng.random(60)
    ax.fill_between(xs, 0, low, color=STONE, ec=INK, lw=1.4)
    ax.fill_between(xs, upp, 3.9, color=WOOD, ec=INK, lw=1.4)
    arrow(ax, (2.0, 3.2), (4.5, 3.2), color=FORCE, lw=2.6)
    lab(ax, 3.2, 3.55, r"$\vec F$", FORCE, 14)
    lab(ax, 7.1, 0.75, "шероховатости — мелкие зубчики", PAPER, 11)
    ax.annotate("зубчики обламываются:\nповерхности изнашиваются", (5.0, 1.98), (6.0, 3.1), arrowprops=dict(arrowstyle="->", color=INK), fontsize=11, ha="left")
    ax.annotate("молекулы соседних тел\nпритягиваются", (1.4, 1.85), (0.2, 0.55), arrowprops=dict(arrowstyle="->", color=INK), fontsize=11, ha="left", color=PAPER)
    lab(ax, 1.2, 4.1, "тело", INK, 11)
    lab(ax, 8.4, 0.15, "опора", INK, 11)
    save(fig, "friction-surface-roughness.png")


def friction_block_stops():
    fig, ax = blank(8.5, 4.4, (-0.8, 7.8), (-1.5, 3.5))
    ground(ax, 0.0, 7.4, 0.0, h=0.18)
    block(ax, 2.2, 0.0, w=2.4, h=1.2)
    cx, cy = 3.4, 0.6
    dot(ax, cx, cy)
    arrow(ax, (cx, cy), (cx, 2.1), color=BLUE, lw=2.4)
    lab(ax, cx + 0.45, 1.95, r"$\vec N$", BLUE, 13)
    arrow(ax, (cx, cy), (cx, -0.9), color=GREEN, lw=2.4)
    lab(ax, cx + 0.5, -0.75, r"$\vec F_\mathrm{тяж}$", GREEN, 13)
    arrow(ax, (2.2, 0.0), (0.5, 0.0), color=FRICTION, lw=3)
    lab(ax, 1.3, 0.35, r"$\vec F_\mathrm{тр}$", FRICTION, 13)
    arrow(ax, (4.8, 0.9), (6.9, 0.9), color=GREY, lw=2.2)
    lab(ax, 6.0, 1.3, r"$\vec v$", NOTE, 13)
    lab(ax, 3.4, -1.35, "по вертикали силы компенсируются, по горизонтали остаётся одна $F_\\mathrm{тр}$: скорость падает до нуля", INK, 10, ha="center")
    save(fig, "friction-block-stops.png")


def friction_rolling_vs_sliding():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    ax.set_xlim(-0.3, 9.6)
    ax.set_ylim(-0.6, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ground(ax, 0.0, 4.4, 0.0, h=0.14)
    block(ax, 0.9, 0.0, w=2.2, h=1.0)
    arrow(ax, (3.1, 0.6), (4.1, 0.6), color=FORCE, lw=2.6)
    lab(ax, 4.55, 0.6, r"$0{,}8$ Н", FORCE, 11.5, ha="left")
    lab(ax, 2.1, 1.5, "скольжение", INK, 12, weight="bold")
    ground(ax, 5.2, 9.4, 0.0, h=0.14)
    for cx in (5.85, 6.7, 7.55):
        ax.add_patch(Circle((cx, 0.22), 0.22, fc=LIGHT, ec=INK, lw=1.3, zorder=3))
    block(ax, 5.55, 0.44, w=2.3, h=1.0)
    arrow(ax, (7.85, 0.95), (8.55, 0.95), color=FORCE, lw=2.6)
    lab(ax, 8.6, 0.95, r"$<0{,}1$ Н", FORCE, 11.5, ha="left")
    lab(ax, 6.7, 1.9, "качение", INK, 12, weight="bold")
    ax = axes[1]
    ax.bar(["скольжение", "качение"], [0.8, 0.1], color=[NOTE, GREEN], width=0.5, hatch=["", "//"])
    ax.text(1, 0.115, r"$<0{,}1$", ha="center", fontsize=11)
    ax.text(0, 0.815, r"$0{,}8$", ha="center", fontsize=11)
    ax.set(ylabel=r"сила, Н", ylim=(0, 1.0))
    ax.set_title("Показания динамометра", fontsize=12)
    ax.grid(color=GRID, axis="y")
    fig.tight_layout()
    save(fig, "friction-rolling-vs-sliding.png")


def friction_rolling_crumbs():
    fig, ax = blank(10, 4.2, (-0.5, 9.5), (-1.0, 3.6))
    ground(ax, 0.0, 9.0, 0.0, h=0.0)
    xs = np.linspace(0, 9, 400)
    ax.plot(xs, np.zeros_like(xs), color=INK, lw=1.6)
    for cx in (5.6, 5.95, 6.3, 6.6):
        ax.add_patch(Circle((cx, 0.06), 0.09, fc=STONE, ec=INK, lw=0.8, zorder=2))
    ax.add_patch(Circle((3.2, 1.2), 1.2, fc=LIGHT, ec=INK, lw=1.5, zorder=3))
    dot(ax, 3.2, 1.2)
    arrow(ax, (3.2, 1.2), (5.2, 1.2), color=FORCE, lw=2.6)
    lab(ax, 4.3, 1.55, r"$\vec F$", FORCE, 14)
    arrow(ax, (3.2, 0.0), (1.6, 0.0), color=FRICTION, lw=3)
    lab(ax, 2.3, -0.4, r"$\vec F_\mathrm{тр\ кач}$", FRICTION, 13)
    lab(ax, 6.0, 0.6, "крошки", NOTE, 10.5)
    lab(ax, 6.0, 2.6, "шар раздавливает неровности: для этого нужна сила,\nэто и есть сила трения качения", INK, 10.5, ha="center")
    save(fig, "friction-rolling-crumbs.png")


def friction_ball_bearing():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(-3.3, 3.3)
    ax.add_patch(Circle((0, 0), 3.0, fc=LIGHT, ec=INK, lw=2))
    ax.add_patch(Circle((0, 0), 2.55, fc=PAPER, ec=INK, lw=1.4))
    ax.add_patch(Circle((0, 0), 1.25, fc=LIGHT, ec=INK, lw=1.4, hatch="////"))
    ax.add_patch(Circle((0, 0), 1.5, fc="none", ec=INK, lw=1.4))
    n = 7
    for k in range(n):
        a = 2 * np.pi * k / n + 0.3
        ax.add_patch(Circle((2.02 * np.cos(a), 2.02 * np.sin(a)), 0.5, fc=BLUE, ec=INK, lw=1.3, alpha=0.75, zorder=4))
    ax.add_patch(Circle((0, 0), 2.02, fc="none", ec=GREY, lw=1, ls="--", zorder=1))
    lab(ax, 0, 0, "вал", INK, 11, weight="bold", bbox=dict(fc=PAPER, ec="none", pad=1.5))
    ax.annotate("внешнее кольцо\n(на корпусе)", (-2.15, 2.1), (-3.3, 3.2), fontsize=10.5, ha="left", arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("шарики", (2.02 * np.cos(0.3 + 2 * np.pi / 7 * 3), 2.02 * np.sin(0.3 + 2 * np.pi / 7 * 3)), (-3.3, -1.1), fontsize=10.5, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("внутреннее кольцо", (0.95, -1.15), (1.2, -3.55), fontsize=10.5, ha="left", arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(0, 3.95, "Шариковый подшипник (сепаратор не показан)", fontsize=12, ha="center")
    ax.set_ylim(-3.8, 4.2)
    ax = axes[1]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-3.0, 3.2)
    ax.plot([-2, 2], [-1, -1], color=INK, lw=2)
    ax.add_patch(Circle((-1.0, -0.2), 0.8, fc=BLUE, ec=INK, alpha=0.75))
    ax.plot([-1.0], [-1.0], "o", color=FORCE, ms=9)
    lab(ax, -1.0, -1.55, "шарик:\nпятнышко", INK, 10.5)
    ax.add_patch(Rectangle((0.3, -0.98), 1.6, 1.6, fc=BLUE, ec=INK, alpha=0.75))
    ax.plot([0.3, 1.9], [-1.0, -1.0], color=FORCE, lw=4)
    lab(ax, 1.1, -1.55, "ролик:\nполоска", INK, 10.5)
    lab(ax, 0, 1.75, "Ролик распределяет нагрузку\nпо большей площади", INK, 11, weight="bold")
    save(fig, "friction-ball-bearing.png")


def friction_fluid_drag():
    fig, axes = blank_row(2, 11.5, 4.3, (-1.0, 6.0), (-1.6, 4.4))
    ax = axes[0]
    xs = np.linspace(-0.6, 5.6, 300)
    ax.fill_between(xs, -1.4, 0.9 + 0.06 * np.sin(xs * 5), color=WATER, alpha=0.7, zorder=0)
    ax.plot(xs, 0.9 + 0.06 * np.sin(xs * 5), color=BLUE, lw=1.5)
    ax.add_patch(Polygon([(1.2, 1.5), (4.2, 1.5), (3.6, 0.5), (1.6, 0.5)], fc=WOOD, ec=INK, lw=1.5, zorder=3))
    arrow(ax, (4.2, 1.1), (5.6, 1.1), color=FORCE, lw=2.6)
    lab(ax, 5.1, 1.5, r"$\vec F$", FORCE, 14)
    arrow(ax, (1.3, 1.0), (-0.2, 1.0), color=FRICTION, lw=2.6)
    lab(ax, 0.3, 1.4, r"$\vec F_\mathrm{сопр}$", FRICTION, 13)
    lab(ax, 2.5, -0.8, "лодка движется равномерно:\n$F = F_\\mathrm{сопр}$", INK, 11)
    ax = axes[1]
    th = np.linspace(0, np.pi, 60)
    ax.fill_between(2.1 + 1.6 * np.cos(th), 2.5 + 1.1 * np.sin(th) * 0 + 0.0, 2.5, alpha=0)
    ax.add_patch(matplotlib.patches.Wedge((2.1, 2.3), 1.7, 0, 180, fc=tint(RED, 0.8), ec=INK, lw=1.6))
    for x in (0.6, 1.35, 2.1, 2.85, 3.6):
        ax.plot([x, 2.1], [2.3, 0.85], color=INK, lw=1)
    ax.add_patch(Rectangle((1.6, 0.4), 1.0, 0.45, fc=STONE, ec=INK, lw=1.4))
    arrow(ax, (2.1, 2.3), (2.1, 4.1), color=FRICTION, lw=2.6)
    lab(ax, 2.7, 3.9, r"$\vec F_\mathrm{сопр}$", FRICTION, 13)
    arrow(ax, (2.1, 0.4), (2.1, -1.2), color=GREEN, lw=2.6)
    lab(ax, 2.8, -1.0, r"$\vec F_\mathrm{тяж}$", GREEN, 13)
    lab(ax, 2.1, -1.45, "", INK)
    fig.text(0.5, 0.0, "Равномерное падение с парашютом: $F_\\mathrm{сопр} = F_\\mathrm{тяж}$", ha="center", fontsize=11.5)
    save(fig, "friction-fluid-drag.png")


def friction_dry_vs_fluid():
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    v = np.linspace(0, 1, 200)
    ax.plot([0, 0], [0, 0.4], color=FRICTION, lw=5, solid_capstyle="butt")
    ax.plot([0, 1], [0.4, 0.4], color=FRICTION, lw=2.6, label="сухое трение: при $v = 0$ есть трение покоя,\nпри скольжении сила почти не зависит от $v$")
    ax.plot(v, 0.55 * v**1.6, color=BLUE, lw=2.6, label="сила сопротивления среды: при $v = 0$ её нет,\nрастёт с ростом скорости")
    ax.plot([0], [0], "o", color=BLUE, ms=7)
    ax.set(xlabel="скорость тела относительно опоры или среды", ylabel="сила трения или сопротивления", xlim=(-0.03, 1.02), ylim=(0, 0.6), xticks=[], yticks=[])
    ax.text(0.03, 0.2, "трение\nпокоя", color=FRICTION, fontsize=10.5, va="center")
    ax.text(0.98, 0.56, "форма кривой условна", color=NOTE, fontsize=10, ha="right")
    ax.legend(frameon=False, loc="upper center", fontsize=10.5, bbox_to_anchor=(0.5, -0.1))
    ax.grid(color=GRID)
    save(fig, "friction-dry-vs-fluid.png")


def friction_skydiver():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6))
    ax = axes[0]
    v = np.linspace(0, 85, 200)
    ax.plot(v, 600 * (v / 60) ** 2, color=BLUE, lw=2.6, label="без парашюта")
    ax.plot(v, 600 * (v / 12) ** 2, color=FRICTION, lw=2.6, label="с раскрытым парашютом (условно)")
    ax.axhline(600, color=GREEN, lw=2, label=r"$F_\mathrm{тяж} = mg = 600$ Н")
    ax.plot([60], [600], "o", color=BLUE, ms=8)
    ax.plot([12], [600], "o", color=FRICTION, ms=8)
    ax.annotate(r"$\approx 60$ м/с", (60, 600), (66, 350), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.set(xlabel=r"скорость $v$, м/с", ylabel=r"$F_\mathrm{сопр}$, Н", xlim=(0, 85), ylim=(0, 1000))
    ax.set_title("Скорость, при которой сопротивление уравновешивает силу тяжести", fontsize=11.5)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(color=GRID)
    ax = axes[1]
    g, m = 10.0, 60.0
    k1, k2 = 600 / 60**2, 600 / 12**2
    t = np.linspace(0, 45, 4500)
    dt = t[1] - t[0]
    vv = np.zeros_like(t)
    t_open = 20.0
    for i in range(1, len(t)):
        k = k1 if t[i] < t_open else k2
        vv[i] = vv[i - 1] + dt * (g - k * vv[i - 1] ** 2 / m)
    ax.plot(t, vv, color=BLUE, lw=2.6)
    ax.axvline(t_open, color=GREY, ls="--", lw=1)
    ax.text(t_open + 0.6, 66, "парашют раскрыт", color=NOTE, fontsize=10.5)
    ax.axhline(60, color=GREY, ls=":", lw=1)
    ax.set(xlabel="время падения, с (условная шкала)", ylabel=r"$v$, м/с", xlim=(0, 45), ylim=(0, 75))
    ax.set_title("Скорость растёт, потом постоянна, после раскрытия падает", fontsize=11.5)
    ax.grid(color=GRID)
    fig.tight_layout()
    save(fig, "friction-skydiver.png")


def friction_sliding_bearing_oil():
    fig, ax = blank(7.6, 6.0, (-3.6, 3.6), (-3.6, 3.6))
    ax.add_patch(Circle((0, 0), 3.2, fc=LIGHT, ec=INK, lw=2))
    ax.add_patch(Circle((0, 0), 1.85, fc=OIL, ec=INK, lw=1.2))
    ax.add_patch(Circle((0, 0), 1.6, fc=STONE, ec=INK, lw=1.6, hatch="////"))
    lab(ax, 0, 0, "вал", INK, 11, weight="bold", bbox=dict(fc=PAPER, ec="none", pad=1.5))
    ax.annotate("слой масла", (1.75, 0.5), (3.0, 1.9), fontsize=11, arrowprops=dict(arrowstyle="->", color=INK), color=INK)
    ax.annotate("вкладыш", (2.6, -1.4), (2.3, -3.3), fontsize=11, arrowprops=dict(arrowstyle="->", color=INK))
    lab(ax, 0, 3.55, "Подшипник скольжения со смазкой:\nсухое трение заменено жидким", INK, 11, weight="bold")
    save(fig, "friction-sliding-bearing-oil.png")


def _book_stack(ax, x, ys, w=2.6, h=0.45, fc=None, hatch_idx=()):
    for i, y in enumerate(ys):
        ax.add_patch(Rectangle((x, y), w, h, fc=(fc or [WOOD])[0] if i not in hatch_idx else WOOD_D, ec=INK, lw=1.3, hatch="////" if i in hatch_idx else None, zorder=3))


def friction_book_stack_lesson40():
    fig, axes = blank_row(2, 11.5, 4.6, (-1.2, 5.4), (-0.9, 3.6))
    ax = axes[0]
    ground(ax, -0.6, 4.4, 0.0, h=0.15)
    for i in range(4):
        ax.add_patch(Rectangle((0.6, i * 0.5), 2.6, 0.5, fc=WOOD, ec=INK, lw=1.3, zorder=3))
    arrow(ax, (3.2, 0.25), (4.9, 0.25), color=FORCE, lw=2.8)
    lab(ax, 4.2, 0.6, r"$\vec F_1$, $5$ Н", FORCE, 12)
    lab(ax, 2.0, 2.6, "тянут всю стопку", INK, 12, weight="bold")
    arrow(ax, (0.6, 0.0), (-0.5, 0.0), color=FRICTION, lw=2.6)
    lab(ax, -0.35, 0.35, r"$\vec F_\mathrm{тр}$", FRICTION, 11)
    lab(ax, 2.0, 2.15, "трение только на границе с столом", NOTE, 10)
    ax = axes[1]
    ground(ax, -0.6, 4.4, 0.0, h=0.15)
    ax.add_patch(Rectangle((0.9, 0.0), 2.6, 0.5, fc=WOOD_D, ec=INK, lw=1.3, zorder=3, hatch="////"))
    for i in range(1, 4):
        ax.add_patch(Rectangle((0.6, i * 0.5), 2.6, 0.5, fc=WOOD, ec=INK, lw=1.3, zorder=3))
    arrow(ax, (3.5, 0.25), (4.9, 0.25), color=FORCE, lw=2.8)
    lab(ax, 4.3, 0.6, r"$\vec F_2$, $7$ Н", FORCE, 12)
    lab(ax, 2.0, 2.6, "тянут только нижнюю книгу", INK, 12, weight="bold")
    arrow(ax, (0.9, 0.12), (-0.2, 0.12), color=FRICTION, lw=2.6)
    arrow(ax, (0.9, 0.42), (-0.2, 0.42), color=FRICTION2, lw=2.6)
    lab(ax, -0.4, 0.8, "две силы\nтрения", FRICTION, 10)
    lab(ax, 2.0, 2.15, "трение и снизу, и сверху", NOTE, 10)
    fig.text(0.5, 0.0, r"$F_2 > F_1$: во втором случае добавляется трение о вышележащие книги", ha="center", fontsize=11.5)
    save(fig, "friction-book-stack-lesson40.png")


# ----------------------------------------------------------------- combined

def combined_block_spring():
    fig, ax = blank(10, 4.8, (-1.0, 9.6), (-1.7, 3.7))
    ground(ax, -0.5, 9.0, 0.0, h=0.18)
    block(ax, 2.2, 0.0, w=2.4, h=1.2)
    cx, cy = 3.4, 0.6
    dot(ax, cx, cy)
    # uniform motion: N = mg (length 1.7), F_упр = F_тр (length 1.5)
    arrow(ax, (cx, cy), (cx, 2.3), color=BLUE, lw=2.6)
    lab(ax, cx + 0.55, 2.15, r"$\vec N$", BLUE, 14)
    arrow(ax, (cx, cy), (cx, -1.1), color=GREEN, lw=2.6)
    lab(ax, cx - 0.6, -0.9, r"$m\vec g$", GREEN, 14)
    arrow(ax, (2.2, 0.0), (0.7, 0.0), color=FRICTION, lw=3)
    lab(ax, 1.3, 0.38, r"$\vec F_\mathrm{тр}$", FRICTION, 13)
    # spring on the right
    xs = np.linspace(4.6, 7.4, 120)
    ys = 0.6 + 0.2 * np.sin(np.linspace(0, 12 * np.pi, 120))
    ax.plot([4.6, 4.8], [0.6, 0.6], color=INK, lw=1.4)
    ax.plot(xs[8:], ys[8:], color=INK, lw=1.6)
    arrow(ax, (4.9, 1.05), (6.4, 1.05), color=RESULT, lw=2.6)
    lab(ax, 5.6, 1.42, r"$\vec F_\mathrm{упр}$", RESULT, 14)
    ax.plot([7.4, 8.6], [0.6, 0.6], color=INK, lw=1.4)
    arrow(ax, (8.0, 0.6), (9.2, 0.6), color=GREY, lw=2.2)
    lab(ax, 9.1, 1.0, r"$\vec v = \mathrm{const}$", NOTE, 11)
    # the extension is the stretched length minus the free length l0, not the whole spring
    ax.plot([6.4, 6.4], [-0.8, 0.3], color=GREY, lw=1, ls="--")
    ax.annotate("", (6.4, -0.55), (4.6, -0.55), arrowprops=dict(arrowstyle="<->", color=GREY))
    lab(ax, 5.5, -0.95, r"$l_0$", NOTE, 12)
    ax.annotate("", (7.4, -0.55), (6.4, -0.55), arrowprops=dict(arrowstyle="<->", color=INK))
    lab(ax, 6.9, -0.95, r"$\Delta l = ?$", INK, 12)
    save(fig, "combined-block-spring.png")


def combined_books_stack():
    fig, axes = blank_row(2, 12.5, 4.0, (-2.2, 6.0), (-1.6, 3.2))
    h = 0.6
    for ax, mode in zip(axes, ("second", "top")):
        ground(ax, -1.0, 5.4, 0.0, h=0.15)
        # on the right panel books 3 and 4 are drawn only in their shifted place
        moved = (2, 3) if mode == "top" else ()
        for i in range(4):
            if i not in moved:
                ax.add_patch(Rectangle((0.6, i * h), 2.8, h, fc=WOOD, ec=INK, lw=1.3, zorder=3))
        for i in range(4):
            x = 2.3 if i in moved else 2.0
            ax.text(x, (i + 0.5) * h, str(i + 1), ha="center", va="center", fontsize=10, zorder=5)
    ax = axes[0]
    ax.add_patch(Rectangle((0.6, h), 2.8, h, fc=WOOD_D, ec=INK, lw=1.3, hatch="////", zorder=4))
    ax.text(2.0, 0.9, "2", ha="center", va="center", fontsize=10, zorder=6, bbox=dict(fc=PAPER, ec="none", pad=0.5))
    ax.set_title("Тянут второй снизу учебник", fontsize=12)
    # scale 0.5 per mu*m*g: F_тр в = 2, F_тр н = 3, F_1 = 5
    arrow(ax, (3.4, 1.5 * h + 0.0), (5.9, 1.5 * h), color=FORCE, lw=3)
    lab(ax, 5.2, 1.5 * h + 0.35, r"$\vec F_1$", FORCE, 14)
    arrow(ax, (0.6, 2 * h - 0.12), (-0.4, 2 * h - 0.12), color=FRICTION, lw=2.6)
    lab(ax, -1.2, 2 * h - 0.12, r"$\vec F_\mathrm{тр\,в}$", FRICTION, 12)
    arrow(ax, (0.6, h + 0.12), (-0.9, h + 0.12), color=FRICTION2, lw=2.6)
    lab(ax, -1.65, h + 0.12, r"$\vec F_\mathrm{тр\,н}$", FRICTION2, 12)
    lab(ax, 0.9, -0.9, r"$N_\mathrm{в} = 2mg$, $N_\mathrm{н} = 3mg$" "\n" r"$F_\mathrm{тр\,в} = \mu\cdot 2mg$, $F_\mathrm{тр\,н} = \mu\cdot 3mg$", INK, 11)
    ax = axes[1]
    for i in (2, 3):
        ax.add_patch(Rectangle((0.6 + 0.3, i * h), 2.8, h, fc=WOOD_D, ec=INK, lw=1.3, hatch="////", zorder=4))
    ax.set_title("Тянут два верхних учебника", fontsize=12)
    # same scale: F_тр = F_2 = 2 mu*m*g
    arrow(ax, (3.7, 2.5 * h + 0.0), (4.7, 2.5 * h), color=FORCE, lw=3)
    lab(ax, 4.3, 2.5 * h + 0.35, r"$\vec F_2$", FORCE, 14)
    arrow(ax, (0.9, 2 * h + 0.12), (-0.1, 2 * h + 0.12), color=FRICTION, lw=2.6)
    lab(ax, -0.9, 2 * h + 0.12, r"$\vec F_\mathrm{тр}$", FRICTION, 12)
    lab(ax, 1.0, -0.9, r"$N = 2mg$" "\n" r"$F_\mathrm{тр} = \mu\cdot 2mg$", INK, 11)
    save(fig, "combined-books-stack.png")


def combined_books_friction_bars():
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.bar([0], [3], color=FRICTION2, width=0.5, label=r"$F_\mathrm{тр\,н} = 3\mu mg$")
    ax.bar([0], [2], bottom=[3], color=FRICTION, width=0.5, label=r"$F_\mathrm{тр\,в} = 2\mu mg$")
    ax.bar([1], [2], color=FRICTION, width=0.5)
    ax.text(0, 5.15, r"$F_1 = 5\mu mg$", ha="center", fontsize=12)
    ax.text(1, 2.15, r"$F_2 = 2\mu mg$", ha="center", fontsize=12)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["второй снизу", "два верхних"])
    ax.set(ylabel=r"сила, единицы $\mu mg$", ylim=(0, 6.2))
    ax.set_title(r"Сила трения при равномерном движении: $F_1 / F_2 = 5/2$", fontsize=12)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(color=GRID, axis="y")
    save(fig, "combined-books-friction-bars.png")


def combined_spring_length():
    fig, ax = blank(9.5, 5.2, (-0.6, 10.2), (-1.4, 4.4))
    def spring(y, l, color, force, name, flen=0.0):
        x0 = 0.4
        ax.plot([x0, x0], [y - 0.35, y + 0.35], color=INK, lw=3)
        n = 100
        xs = np.linspace(x0, x0 + l, n)
        ax.plot(xs, y + 0.2 * np.sin(np.linspace(0, 2 * np.pi * (l * 1.4), n)), color=INK, lw=1.6)
        if force:
            arrow(ax, (x0 + l, y), (x0 + l + flen, y), color=FORCE, lw=2.6)
            lab(ax, x0 + l + flen / 2, y + 0.4, force, FORCE, 12)
        lab(ax, x0 + l / 2, y + 0.65, name, INK, 11)
    # true scale: l2 = 18, l1 = 15, l0 = 10 cm
    unit = 4.6 / 18
    # force arrows in proportion 45 : 72
    spring(3.2, 18 * unit, INK, r"$\vec F_2$", r"$l_2 = 18$ см", flen=2.4)
    spring(1.8, 15 * unit, INK, r"$\vec F_1$", r"$l_1 = 15$ см", flen=1.5)
    spring(0.4, 10 * unit, INK, "", r"$l_0 = ?$")
    ax.annotate("", (0.4 + 15 * unit, 1.25), (0.4 + 10 * unit, 1.25), arrowprops=dict(arrowstyle="<->", color=GREEN))
    ax.annotate("", (0.4 + 18 * unit, 2.65), (0.4 + 10 * unit, 2.65), arrowprops=dict(arrowstyle="<->", color=GREEN))
    lab(ax, 0.4 + 12.5 * unit, 1.05, r"$\Delta l_1$", GREEN, 11)
    lab(ax, 0.4 + 14 * unit, 2.45, r"$\Delta l_2$", GREEN, 11)
    lab(ax, 9.0, 1.2, r"$F_1 = 45$ Н" "\n" r"$F_2 = 72$ Н", INK, 11.5)
    save(fig, "combined-spring-length.png")


def combined_spring_f_vs_l():
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    l = np.linspace(8, 20, 50)
    k = 27 / 3
    ax.plot(l, k * (l - 10), color=RESULT, lw=2.6)
    ax.plot([10], [0], "o", color=GREEN, ms=9, zorder=5)
    ax.plot([15, 18], [45, 72], "o", color=INK, ms=8, zorder=5)
    ax.annotate("$l_0 = 10$ см,\n$F = 0$", (10, 0), (10.6, 22), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11, color=GREEN)
    ax.annotate("$(15;\\ 45)$", (15, 45), (12.3, 58), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.annotate("$(18;\\ 72)$", (18, 72), (15.5, 82), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=11)
    ax.axhline(0, color=INK, lw=1)
    ax.set(xlabel=r"длина пружины $l$, см", ylabel=r"сила $F$, Н", xlim=(8, 20), ylim=(-5, 95))
    ax.set_title(r"Закон Гука: прямая $F = k(l - l_0)$ пересекает ось длины в $l_0$", fontsize=12)
    ax.grid(color=GRID)
    save(fig, "combined-spring-f-vs-l.png")


def main():
    resultant_cart_replacement()
    resultant_dynamometer_cases()
    resultant_r_vs_f2()
    resultant_equilibrium()
    resultant_problem_380()
    resultant_problem_381()
    resultant_problem_381_values()
    friction_block_forces()
    friction_static_kinetic_graph()
    friction_stiction_peak()
    friction_ftr_vs_n_data()
    friction_mu_lines()
    friction_area_independence()
    friction_surface_roughness()
    friction_block_stops()
    friction_rolling_vs_sliding()
    friction_rolling_crumbs()
    friction_ball_bearing()
    friction_fluid_drag()
    friction_dry_vs_fluid()
    friction_skydiver()
    friction_sliding_bearing_oil()
    friction_book_stack_lesson40()
    combined_block_spring()
    combined_books_stack()
    combined_books_friction_bars()
    combined_spring_length()
    combined_spring_f_vs_l()


if __name__ == "__main__":
    main()
