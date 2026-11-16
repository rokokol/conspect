"""Figures for the notes "Атомы и молекулы" and "Диффузия и броуновское движение" (lessons 11-12)."""
from matter_common import *
from matplotlib.colors import LinearSegmentedColormap
from scipy.special import erf

INK_CMAP = LinearSegmentedColormap.from_list("ink_in_water", [PAPER, tint(BLUE, 0.5), BLUE])  # the density of a dye


# ---------- Атомы и молекулы ----------------------------------------------

def fig_pot():
    """Stones, sand, water: three fillings of one pot."""
    rng = np.random.default_rng(3)
    fig, axes = blank_row(3, 10.5, 4.1, (-0.4, 6.4), (-0.6, 6.6))
    titles = ["камни", "камни и песок", "камни, песок и вода"]
    stones = [(1.15, 1.0), (3.0, 0.95), (4.85, 1.0), (2.05, 2.75), (3.95, 2.7), (3.0, 4.45)]
    for k, ax in enumerate(axes):
        ax.plot([0, 0, 6, 6], [5.6, 0, 0, 5.6], color=INK, lw=2.4)
        if k == 2:
            ax.add_patch(Rectangle((0.05, 0.05), 5.9, 5.0, fc=WATER, ec="none", alpha=0.55, zorder=0))
            ax.plot([0.05, 5.95], [5.05, 5.05], color=WATER_D, lw=1.6)
        if k >= 1:
            pts = []
            while len(pts) < 700:
                x, y = rng.uniform(0.1, 5.9), rng.uniform(0.1, 5.0)
                if all((x - sx) ** 2 + (y - sy) ** 2 > (0.83 + 0.06) ** 2 for sx, sy in stones):
                    pts.append((x, y))
            pts = np.array(pts)
            ax.scatter(pts[:, 0], pts[:, 1], s=5, color=COPPER, zorder=2)
        for sx, sy in stones:
            ax.add_patch(Circle((sx, sy), 0.83, fc=tint(INK, 0.6), ec=INK, lw=1.3, zorder=3))
        ax.text(3, -0.55, titles[k], ha="center", va="top", fontsize=11)
    save(fig, "pot-stones-sand-water.png")


def _atom(ax, x, y, r, fc, label=None, fs=9):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=INK, lw=1.2, zorder=3))
    if label:
        ax.text(x, y, label, ha="center", va="center", fontsize=fs, zorder=4, color=INK)


def fig_molecules():
    """H2O and C2H5OH: schematic, not to scale."""
    fig, axes = blank_row(2, 9.2, 3.8, (-2.6, 2.6), (-2.4, 2.4))
    ax = axes[0]
    a = np.deg2rad(52)
    for sgn in (-1, 1):
        px, py = 1.15 * np.sin(a) * sgn, -1.15 * np.cos(a)
        ax.plot([0, px], [0, py], color=INK, lw=2, zorder=1)
        _atom(ax, px, py, 0.5, PAPER, "H")
    _atom(ax, 0, 0, 0.78, tint(RED, 0.5), "O", 12)
    ax.set_title("вода $\\mathrm{H_2O}$: 3 атома", fontsize=12)

    ax = axes[1]
    ax.set_xlim(-1.9, 4.1)
    ax.set_ylim(-2.4, 2.4)
    c1, c2, o = (-0.4, 0.0), (1.1, 0.35), (2.55, -0.25)
    hs = [(-1.1, 1.2), (-1.15, -1.1), (-0.35, -1.55), (1.2, 1.55), (1.45, -0.95), (3.35, -0.95)]
    bonds = [(c1, c2), (c2, o), (c1, hs[0]), (c1, hs[1]), (c1, hs[2]), (c2, hs[3]), (c2, hs[4]), (o, hs[5])]
    for p, q in bonds:
        ax.plot([p[0], q[0]], [p[1], q[1]], color=INK, lw=2, zorder=1)
    for h in hs:
        _atom(ax, h[0], h[1], 0.4, PAPER, "H", 9)
    _atom(ax, *c1, 0.6, tint(INK, 0.5), "C", 11)
    _atom(ax, *c2, 0.6, tint(INK, 0.5), "C", 11)
    _atom(ax, *o, 0.62, tint(RED, 0.5), "O", 11)
    ax.set_title("спирт $\\mathrm{C_2H_5OH}$: 9 атомов", fontsize=12)
    fig.text(0.5, 0.03, "схема без масштаба и без настоящих углов между связями", ha="center", fontsize=9, color=NOTE)
    save(fig, "water-ethanol-molecules.png")


def fig_lattice_nm():
    """A patch of atoms with a 2 nm scale bar, as on the scanning tunnelling microscope image."""
    fig, ax = blank(5.8, 4.4, (-0.4, 4.4), (-1.0, 2.6))
    d = 0.2
    for i in range(10):
        for j in range(10):
            ax.add_patch(Circle((0.1 + i * d, 0.1 + j * d), 0.075, fc=tint(BLUE, 0.5), ec=BLUE, lw=0.8))
    ax.plot([0, 2.0], [-0.45, -0.45], color=INK, lw=3, solid_capstyle="butt")
    for x in (0, 2.0):
        ax.plot([x, x], [-0.55, -0.35], color=INK, lw=2)
    ax.text(1.0, -0.62, "2 нм", ha="center", va="top", fontsize=12)
    # 1 nm bracket on the right edge spans five atoms
    ax.plot([2.15, 2.25, 2.25, 2.15], [0.0, 0.0, 1.0, 1.0], color=RED, lw=1.8)
    ax.text(2.4, 0.5, "1 нм: около\n5 атомов", color=RED, fontsize=11, va="center")
    arrow(ax, (3.0, 1.75), (1.95, 1.85), color=INK, lw=1.2, style="->")
    ax.text(3.1, 1.75, "атом: доли\nнанометра", fontsize=11, va="center")
    save(fig, "lattice-nanometer-scale.png")


def fig_syringe():
    """Air is compressed in a syringe, water is not."""
    rng = np.random.default_rng(8)
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 4.4))
    for ax in axes.flat:
        ax.set_xlim(-4.6, 10.6)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect("equal")
        ax.axis("off")

    def syringe(ax, px):
        """Nozzle on the right, piston enters from the left, the working volume is [px + 0.35, 8.2]."""
        ax.add_patch(Rectangle((0, -0.9), 8.2, 1.8, fc=tint(SKY, 0.9), ec=INK, lw=2, zorder=0))
        ax.add_patch(Rectangle((8.2, -0.15), 1.4, 0.3, fc=tint(SKY, 0.9), ec=INK, lw=2, zorder=0))
        ax.plot([px, -3.4], [0, 0], color=INK, lw=4, zorder=3)
        ax.add_patch(Rectangle((-3.7, -0.55), 0.3, 1.1, fc=tint(INK, 0.5), ec=INK, lw=1.4, zorder=3))
        ax.add_patch(Rectangle((px, -0.9), 0.35, 1.8, fc=tint(INK, 0.5), ec=INK, lw=1.6, zorder=4))

    n_air = 44
    base = np.column_stack([rng.uniform(0, 1, n_air), rng.uniform(-0.82, 0.82, n_air)])

    def air(ax, px):
        x0, x1 = px + 0.55, 8.05
        ax.scatter(x0 + base[:, 0] * (x1 - x0), base[:, 1], s=26, color=RED, zorder=2)

    def water(ax, px, bubble_r):
        ax.add_patch(Rectangle((px + 0.35, -0.9), 8.2 - px - 0.35, 1.8, fc=WATER, ec="none", alpha=0.6, zorder=1))
        ax.add_patch(Rectangle((8.2, -0.15), 1.4, 0.3, fc=WATER, ec="none", alpha=0.6, zorder=1))
        ax.add_patch(Circle((6.6, 0.0), bubble_r, fc=PAPER, ec=INK, lw=1.2, zorder=2))

    for row, px in enumerate((0.8, 4.4)):
        syringe(axes[row, 0], px)
        air(axes[row, 0], px)
    for row, (px, r) in enumerate(((0.8, 0.62), (1.05, 0.42))):
        syringe(axes[row, 1], px)
        water(axes[row, 1], px, r)
    axes[0, 0].set_title("воздух: молекулы сближаются", fontsize=11)
    axes[0, 1].set_title("вода: поршень почти не идёт", fontsize=11)
    axes[0, 0].text(-4.5, 0.0, "исходно", fontsize=10, va="center", color=NOTE, rotation=90)
    axes[1, 0].text(-4.5, 0.0, "нажали", fontsize=10, va="center", color=NOTE, rotation=90)
    axes[0, 1].annotate("пузырёк воздуха", (6.6, -0.62), (6.6, -1.2), fontsize=9, ha="center", va="top",
                        arrowprops=dict(arrowstyle="-", lw=0.8, color=INK))
    axes[1, 1].annotate("пузырёк сжался, вода нет", (6.6, -0.42), (6.6, -1.2), fontsize=9, ha="center", va="top",
                        arrowprops=dict(arrowstyle="-", lw=0.8, color=INK))
    save(fig, "syringe-air-water.png")


def _flask(ax, level, color, mark):
    # one polygon for bulb and neck: two overlapping translucent patches would darken the join
    a0 = np.arctan2(np.sqrt(1.5**2 - 0.15**2), 0.15)
    arc = np.linspace(a0, a0 - 2 * np.pi + 2 * (np.pi / 2 - a0), 200)
    outline = [(0.15, level)] + list(zip(1.5 * np.cos(arc), 1.5 * np.sin(arc))) + [(-0.15, level)]
    ax.add_patch(Polygon(outline, closed=True, fc=color, ec="none", alpha=0.85, zorder=1))
    th = np.linspace(np.deg2rad(96), np.deg2rad(444), 200)
    ax.plot(1.5 * np.cos(th), 1.5 * np.sin(th), color=INK, lw=2.2, zorder=3)
    for x in (-0.15, 0.15):
        ax.plot([x, x], [1.49, 5.2], color=INK, lw=2.2, zorder=3)
    ax.plot([-0.55, 0.55], [mark, mark], color=INK, lw=3, zorder=4)


def fig_flask():
    fig, axes = blank_row(2, 7.6, 5.4, (-2.4, 2.4), (-2.8, 5.6))
    ink = tint(BLUE, 0.4)  # the coloured water in the flask
    ax = axes[0]
    _flask(ax, 3.0, ink, 3.0)
    ax.text(0, -2.6, "холодная вода", ha="center", va="top", fontsize=11)
    ax = axes[1]
    ax.add_patch(Rectangle((-2.2, -2.1), 4.4, 2.6, fc=tint(RED, 0.8), ec=INK, lw=2.0, zorder=0, alpha=0.9))
    _flask(ax, 3.9, ink, 3.0)
    arrow(ax, (-0.9, 3.0), (-0.9, 3.9), color=RED, lw=1.4)
    ax.text(-1.05, 3.45, "уровень\nвырос", ha="right", va="center", fontsize=10, color=RED)
    ax.text(0, -2.6, "кипяток вокруг колбы", ha="center", va="top", fontsize=11)
    fig.text(0.5, 0.02, "чёрная метка на бумажной полоске стоит против уровня воды до нагрева", ha="center", fontsize=9, color=NOTE)
    save(fig, "water-thermal-expansion-flask.png")


def fig_ball_ring():
    fig, axes = blank_row(3, 11.4, 4.4, (-3, 3), (-2.4, 3.8))
    cold, hot = tint(BLUE, 0.6), tint(RED, 0.55)  # cold is blue, hot is red

    def ring(ax, gap, color):
        """Cross-section of the ring: two blocks with a hole between them."""
        ax.add_patch(Rectangle((-gap / 2 - 1.0, -0.4), 1.0, 0.8, fc=color, ec=INK, lw=1.6, zorder=2))
        ax.add_patch(Rectangle((gap / 2, -0.4), 1.0, 0.8, fc=color, ec=INK, lw=1.6, zorder=2))

    ax = axes[0]
    ring(ax, 2.2, cold)
    ax.add_patch(Circle((0, 1.8), 0.95, fc=cold, ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Circle((0, 0.0), 0.95, fc="none", ec=INK, lw=1.0, ls="--", zorder=3))
    arrow(ax, (0, 0.75), (0, -0.2), color=INK, lw=1.4)
    ax.text(0, -1.5, "шарик холодный:\nпроходит в кольцо", ha="center", va="top", fontsize=11)
    ax = axes[1]
    ring(ax, 2.2, cold)
    ax.add_patch(Circle((0, 0.93), 1.22, fc=hot, ec=INK, lw=1.6, zorder=3))
    ax.text(0, 0.93, "застрял", ha="center", va="center", fontsize=11, color=INK, zorder=4)
    ax.text(0, -1.5, "шарик нагрет:\nне проходит", ha="center", va="top", fontsize=11)
    ax = axes[2]
    ring(ax, 2.7, hot)
    ax.add_patch(Circle((0, 2.4), 1.22, fc=hot, ec=INK, lw=1.6, zorder=3, alpha=0.35))
    ax.add_patch(Circle((0, 0.0), 1.22, fc=hot, ec=INK, lw=1.6, zorder=3))
    arrow(ax, (0, 0.55), (0, -0.2), color=INK, lw=1.6)
    ax.text(0, -1.5, "кольцо тоже нагрето:\nшарик проходит", ha="center", va="top", fontsize=11)
    save(fig, "ball-and-ring.png")


def fig_contraction():
    fig = plt.figure(figsize=(11.5, 4.8))
    ax = fig.add_axes([0.0, 0.0, 0.64, 1.0])
    ax.set_xlim(-0.4, 12.8)
    ax.set_ylim(-2.3, 8.2)
    ax.set_aspect("equal")
    ax.axis("off")

    def cyl(x0, level, color, label):
        ax.add_patch(Rectangle((x0, 0), 1.7, 7.4, fc="none", ec=INK, lw=2))
        ax.add_patch(Rectangle((x0 + 0.05, 0.02), 1.6, level * 3.6 / 100 - 0.02, fc=color, ec="none", alpha=0.8))
        ax.plot([x0 + 0.05, x0 + 1.65], [level * 3.6 / 100] * 2, color=shade(color, 0.6), lw=1.4)
        for v in (100, 200):
            y = v * 3.6 / 100
            ax.plot([x0, x0 + 0.45], [y, y], color=INK, lw=1.4)
            ax.text(x0 - 0.15, y, f"{v}", ha="right", va="center", fontsize=9)
        ax.text(x0 + 0.85, -0.4, label, ha="center", va="top", fontsize=10)

    cyl(0.9, 100, WATER, "100 мл\nводы")
    cyl(4.3, 100, tint(WARM, 0.4), "100 мл\nспирта")
    ax.text(3.25, 3.6, "+", fontsize=22, ha="center", va="center")
    ax.text(7.2, 3.6, "=", fontsize=22, ha="center", va="center")
    cyl(9.0, 192, tint(GREEN, 0.7), "смесь")
    ax.plot([9.0, 10.7], [7.2, 7.2], color=RED, lw=1.2, ls="--")
    ax.text(10.85, 7.2, "200 мл", fontsize=9, color=RED, va="center")
    ax.annotate("меньше\n200 мл", (10.6, 6.92), (11.6, 5.2), fontsize=10, color=RED, ha="center",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.text(6.3, -2.0, "уровень смеси около 192 мл, как в реальном опыте", fontsize=9, color=NOTE, ha="center")

    ax2 = fig.add_axes([0.66, 0.05, 0.33, 0.9])
    ax2.set_xlim(-1.4, 6.0)
    ax2.set_ylim(-1.4, 7.6)
    ax2.set_aspect("equal")
    ax2.axis("off")
    for i in range(3):
        for j in range(3):
            ax2.add_patch(Circle((i * 2.5, j * 2.5), 1.0, fc=tint(WARM, 0.4), ec=INK, lw=1.2))
    for i in range(2):
        for j in range(2):
            ax2.add_patch(Circle((1.25 + i * 2.5, 1.25 + j * 2.5), 0.45, fc=WATER_D, ec=INK, lw=0.9, zorder=4))
    ax2.text(2.5, 6.6,"мелкие молекулы воды встают\nв промежутки между\nкрупными молекулами спирта", ha="center", va="center", fontsize=10)
    save(fig, "water-ethanol-contraction.png")


# ---------- Диффузия и броуновское движение --------------------------------

def fig_ink():
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.0))
    yy, xx = np.mgrid[0:1:200j, 0:0.7:140j]
    fields = [
        np.exp(-((xx - 0.35) ** 2 + (yy - 0.82) ** 2) / (2 * 0.035 ** 2)),
        0.75 * np.exp(-((xx - 0.35) ** 2) / (2 * 0.1 ** 2)) * np.exp(-((yy - 0.55) ** 2) / (2 * 0.3 ** 2))
        + 0.35 * np.exp(-((yy - 0.15) ** 2) / (2 * 0.08 ** 2)) * np.exp(-((xx - 0.35) ** 2) / (2 * 0.2 ** 2)),
        0.55 + 0.25 * (1 - yy),
    ]
    titles = ["сразу после падения капли", "через несколько минут", "через несколько часов"]
    for ax, f, t in zip(axes, fields, titles):
        ax.imshow(f, extent=(0, 0.7, 0, 1), origin="lower", cmap=INK_CMAP, vmin=0, vmax=1.0, aspect="equal")
        ax.plot([0, 0, 0.7, 0.7], [1.05, 0, 0, 1.05], color=INK, lw=2.4)
        ax.set_xlim(-0.05, 0.75)
        ax.set_ylim(-0.05, 1.08)
        ax.axis("off")
        ax.set_title(t, fontsize=11)
    save(fig, "diffusion-ink-stages.png")


def fig_gold_lead():
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.6, 5.4), gridspec_kw=dict(height_ratios=[3, 1], hspace=0.12), sharex=True)
    x = np.linspace(-3, 3, 600)
    w = 0.55
    c_au0 = (x < 0).astype(float)
    c_au = 0.5 * (1 - erf(x / w))
    ax.plot(x, c_au0, color=GOLD, lw=1.6, ls="--", label="золото, в начале")
    ax.plot(x, c_au, color=GOLD, lw=2.8, label="золото, через 5 лет")
    ax.plot(x, 1 - c_au0, color=LEAD, lw=1.6, ls="--", label="свинец, в начале")
    ax.plot(x, 1 - c_au, color=LEAD, lw=2.8, label="свинец, через 5 лет")
    ax.axvspan(-0.5, 0.5, color=RED, alpha=0.10)
    ax.text(0, 1.1, "размытая граница\nшириной около 1 мм", ha="center", va="bottom", fontsize=10, color=RED)
    ax.set_ylim(-0.05, 1.3)
    ax.set_ylabel("доля вещества")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=10)
    ax.set_yticks([0, 0.5, 1])
    ax.grid(color=GRID, lw=0.7)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("au_pb", [LEAD, GOLD])
    ax2.imshow(np.tile(c_au, (20, 1)), extent=(-3, 3, 0, 1), aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax2.set_yticks([])
    ax2.set_xlabel("координата вдоль бруска, мм")
    ax2.spines["left"].set_visible(False)
    ax2.text(-1.6, 0.5, "золото", ha="center", va="center", fontsize=10, color=INK)
    ax2.text(1.6, 0.5, "свинец", ha="center", va="center", fontsize=10, color=PAPER)
    save(fig, "diffusion-gold-lead.png")


def fig_diffusion_time():
    fig, ax = plt.subplots(figsize=(7.6, 3.3))
    labels = ["твёрдое тело", "жидкость", "газ"]
    t = [5 * 365 * 86400, 5 * 3600, 3 * 60]
    cols = [LEAD, WATER_D, RED]
    bars = ax.barh(labels, t, color=cols, height=0.55)
    ax.set_xscale("log")
    ax.set_xlim(10, 3e9)
    ax.set_xticks([60, 3600, 86400, 365 * 86400])
    ax.set_xticklabels(["минута", "час", "сутки", "год"])
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("время заметного перемешивания (порядок величины)")
    for b, txt in zip(bars, ["годы", "часы", "минуты"]):
        ax.text(b.get_width() * 1.25, b.get_y() + b.get_height() / 2, txt, va="center", fontsize=11)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "diffusion-time-by-state.png")


def fig_brownian_hits():
    rng = np.random.default_rng(5)
    fig, axes = blank_row(2, 9.4, 4.6, (-3.6, 3.6), (-3.2, 3.2))
    for k, ax in enumerate(axes):
        ax.add_patch(Circle((0, 0), 1.0, fc=tint(COPPER, 0.3), ec=INK, lw=1.8, zorder=3))
        ax.text(0, 0, "частица", ha="center", va="center", fontsize=9, zorder=4)
        n_left, n_right = (6, 2) if k == 0 else (2, 6)
        for side, n in ((-1, n_left), (1, n_right)):
            for _ in range(n):
                ang = np.deg2rad(rng.uniform(-50, 50)) + (np.pi if side < 0 else 0)
                r = rng.uniform(1.9, 3.0)
                u = np.array([np.cos(ang), np.sin(ang)])
                p = r * u
                ax.add_patch(Circle(p, 0.16, fc=RED, ec=INK, lw=0.8, zorder=3))
                arrow(ax, tuple(p - 0.25 * u), tuple(1.12 * u), color=RED, lw=1.1, scale=9)
        d = 1 if k == 0 else -1
        arrow(ax, (0, -2.0), (0.9 * d, -2.0), color=INK, lw=3, scale=16)
        ax.text(0.45 * d, -2.45, "сдвиг", ha="center", fontsize=10)
        ax.set_title("в момент $t_1$" if k == 0 else "в момент $t_2$", fontsize=12)
    fig.text(0.5, 0.02, "молекул больше с одной стороны: частица смещается в противоположную", ha="center", fontsize=10, color=NOTE)
    save(fig, "brownian-collisions.png")


def _walk(rng, n, step):
    a = rng.uniform(0, 2 * np.pi, n)
    xy = np.cumsum(np.column_stack([step * np.cos(a), step * np.sin(a)]), axis=0)
    return np.vstack([[0, 0], xy])


def fig_brownian_walk():
    rng = np.random.default_rng(11)
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.plot(*_walk(rng, 350, 1.0).T, color=RED, lw=1.0, label="мелкая частица")
    ax.plot(*_walk(rng, 350, 0.42).T, color=WATER_D, lw=1.4, label="крупная частица")
    ax.plot([0], [0], "o", color=INK, ms=6, zorder=5)
    ax.set_aspect("equal")
    ax.set_title("мелкая частица блуждает быстрее", fontsize=12)
    ax.legend(frameon=False, fontsize=11, loc="lower right")
    ax.axis("off")
    save(fig, "brownian-particle-sizes.png")

    fig, ax = plt.subplots(figsize=(6.0, 5.4))
    walk = _walk(np.random.default_rng(4), 450, 1.0)
    ax.plot(*walk.T, color=GREY, lw=0.9)
    ax.plot(*walk[0], "o", color=INK, ms=6)
    ax.plot(*walk[-1], "o", color=RED, ms=7)
    arrow(ax, tuple(walk[0]), tuple(walk[-1]), color=RED, lw=2.4, scale=16)
    ax.text(*(walk[0] + np.array([0.5, 0.8])), "старт", fontsize=11)
    ax.text(*(walk[-1] + np.array([0.6, 0.6])), "конец", fontsize=11, color=RED)
    mid = (walk[0] + walk[-1]) / 2
    ax.text(mid[0] + 1.5, mid[1] - 2.2, "смещение", color=RED, fontsize=12)
    ax.set_title("путь по ломаной намного длиннее смещения", fontsize=12)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "random-walk-path-displacement.png")


if __name__ == "__main__":
    fig_pot()
    fig_molecules()
    fig_lattice_nm()
    fig_syringe()
    fig_flask()
    fig_ball_ring()
    fig_contraction()
    fig_ink()
    fig_gold_lead()
    fig_diffusion_time()
    fig_brownian_hits()
    fig_brownian_walk()
