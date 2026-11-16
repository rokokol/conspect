"""Figures for the notes "Взаимодействие молекул. Смачивание" and "Агрегатные состояния вещества" (lessons 13-14)."""
from matter_common import *
from matplotlib.gridspec import GridSpec


def rsa(rng, n, xlim, ylim, dmin, tries=40000, avoid=()):
    """Random sequential placement of points at least dmin apart."""
    pts = []
    for _ in range(tries):
        p = np.array([rng.uniform(*xlim), rng.uniform(*ylim)])
        if all(np.hypot(*(p - q)) >= dmin for q in pts):
            pts.append(p)
            if len(pts) == n:
                break
    return np.array(pts)


# ---------- Взаимодействие молекул -----------------------------------------

def fig_pair_forces():
    fig, ax = blank(8.6, 5.2, (-5.0, 6.6), (-1.3, 7.2))
    rows = [
        (5.6, 1.7, "att", "$r > r_0$: притяжение"),
        (3.1, 0.8, "eq", "$r = r_0$: силы уравновешены"),
        (0.6, 0.5, "rep", "$r < r_0$: отталкивание"),
    ]
    R = 0.6
    for y, h, kind, label in rows:
        for s in (-1, 1):
            ax.add_patch(Circle((s * h, y), R, fc=tint(WARM, 0.3), ec=INK, lw=1.4, zorder=3, alpha=0.95))
            if kind == "att":
                arrow(ax, (s * (h - R), y), (s * (h - R - 0.8), y), color=RED, lw=2.6, scale=16)
            if kind == "rep":
                arrow(ax, (s * (h + R), y), (s * (h + R + 0.8), y), color=RED, lw=2.6, scale=16)
        dim(ax, (-h, y - 0.95), (h, y - 0.95), "", color=INK)
        ax.text(0, y - 1.12, "$r$", ha="center", va="top", fontsize=11)
        ax.text(3.0, y, label, ha="left", va="center", fontsize=12)
    save(fig, "molecule-pair-forces.png")


def fig_force_curve():
    fig, ax = plt.subplots(figsize=(8.0, 5.2))
    r = np.linspace(0.9, 3.4, 800)
    F = 24 * (2 * r ** -13 - r ** -7)
    rr = np.linspace(1.0, 3.0, 4000)
    Fmin = np.min(24 * (2 * rr ** -13 - rr ** -7))
    F = F / abs(Fmin)
    r0 = 2 ** (1 / 6)
    x = r / r0
    ax.axhline(0, color=INK, lw=1.4)
    ax.plot(x, F, color=INK, lw=2.6)
    ax.fill_between(x, 0, F, where=F > 0, color=RED, alpha=0.18)
    ax.fill_between(x, 0, F, where=F < 0, color=WATER_D, alpha=0.20)
    ax.set_ylim(-1.6, 5.0)
    ax.set_xlim(0.85, 3.05)
    ax.plot([1], [0], "o", color=INK, ms=7, zorder=5)
    ax.annotate("равновесное расстояние $r_0$:\nсила равна нулю", (1, 0), (1.5, 2.2), ha="left", fontsize=11,
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    ax.text(1.12, 4.2, "отталкивание резко\nрастёт при сближении", color=RED, fontsize=11, va="center")
    ax.text(1.75, -1.32, "притяжение", color=WATER_D, fontsize=11, ha="center")
    ax.annotate("на расстоянии в несколько\nразмеров молекулы\nсилы почти исчезают", (2.7, -0.09), (2.15, -1.0), ha="center", fontsize=10,
                color=NOTE, arrowprops=dict(arrowstyle="->", color=NOTE, lw=1.0))
    ax.set_xlabel("расстояние между молекулами $r/r_0$")
    ax.set_ylabel("сила: выше нуля отталкивание,\nниже нуля притяжение")
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["$r_0$", "$2r_0$", "$3r_0$"])
    ax.set_yticks([])
    ax.grid(color=GRID, lw=0.7)
    save(fig, "intermolecular-force-curve.png")


def fig_chalk_plasticine():
    rng = np.random.default_rng(2)
    x = np.linspace(0, 10, 700)

    def rough(seed, amp):
        g = np.random.default_rng(seed)
        y = np.zeros_like(x)
        for k in (0.7, 1.9, 4.3, 9.0):
            y += amp / k ** 0.6 * np.sin(k * x + g.uniform(0, 6.28)) * 0.55
        return y

    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.0))
    y1 = rough(3, 0.5)
    y2 = rough(8, 0.5)
    diff = y2 - y1
    y2 = y2 - diff.min() + 0.06
    top = y2.max() + 1.0
    ax = axes[0]
    ax.fill_between(x, -1.6, y1, color=LIGHT, ec=INK, lw=1.6)
    ax.fill_between(x, y2, top, color=LIGHT, ec=INK, lw=1.6)
    ax.plot(x, y1, color=INK, lw=1.6)
    ax.plot(x, y2, color=INK, lw=1.6)
    d = y2 - y1
    idx = [i for i in range(1, len(x) - 1) if d[i] < d[i - 1] and d[i] <= d[i + 1] and d[i] < d.min() + 0.2]
    for i in idx:
        ax.plot([x[i]], [(y1[i] + y2[i]) / 2], "o", color=RED, ms=6, zorder=5)
    ax.set_title("мел: молекулы сближаются в нескольких точках", fontsize=11)
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.7, top + 0.1)
    ax.axis("off")
    y1p = 0.35 * np.sin(0.9 * x) + 0.12 * np.sin(2.7 * x + 1)
    y2p = y1p + 0.06
    ax = axes[1]
    ax.fill_between(x, -1.6, y1p, color=tint(GREEN, 0.6), ec=INK, lw=1.6)
    ax.fill_between(x, y2p, 1.6, color=tint(GREEN, 0.6), ec=INK, lw=1.6)
    ax.plot(x, (y1p + y2p) / 2, color=RED, lw=3)
    ax.set_title("пластилин: поверхности прилегают по всей площади", fontsize=11)
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.7, 1.7)
    ax.axis("off")
    fig.text(0.5, 0.01, "красным отмечены места, где молекулы сблизились до расстояния действия сил", ha="center", fontsize=9, color=NOTE)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "chalk-vs-plasticine-contact.png")


def _spring(ax, x, y_top, y_bot, coils=9, w=0.35):
    ys = np.linspace(y_top, y_bot, coils * 2 + 1)
    xs = np.array([x] + [x + (w if i % 2 == 0 else -w) for i in range(coils * 2 - 1)] + [x])
    ax.plot(xs, ys, color=INK, lw=1.6, zorder=3)


def fig_glass_spring():
    fig, axes = blank_row(3, 11.6, 5.6, (-3.7, 3.7), (-0.2, 8.6))
    steps = [
        dict(vessel=0.2, spring_bot=5.0, cap="стекло висит\nна пружине над водой"),
        dict(vessel=2.95, spring_bot=5.0, cap="сосуд поднесли: вода\nкасается стекла снизу"),
        dict(vessel=0.2, spring_bot=3.9, cap="сосуд опускают: вода\nтянет стекло вниз"),
    ]
    for k, (ax, st) in enumerate(zip(axes, steps)):
        v0 = st["vessel"]
        ax.plot([-1.2, 1.2], [8.3, 8.3], color=INK, lw=4)
        _spring(ax, 0, 8.3, st["spring_bot"])
        pb = st["spring_bot"]
        ax.add_patch(Rectangle((-1.0, pb - 0.2), 2.0, 0.2, fc=GLASS, ec=INK, lw=1.6, zorder=4))
        # scale mark and pointer
        ax.plot([-1.55, -1.2], [5.0, 5.0], color=INK, lw=1.4)
        ax.text(-1.6, 5.0, "метка", ha="right", va="center", fontsize=10)
        if k < 2:
            arrow(ax, (-1.4, pb), (-1.08, pb), color=RED, lw=1.6, scale=10)
        else:
            # The glass is below the mark: show the shift between the mark and the glass instead of a pointer
            ax.plot([-1.55, -1.0], [5.0, 5.0], color=INK, lw=1.0, ls=(0, (3, 2)), zorder=2)
            arrow(ax, (-1.3, 5.0), (-1.3, pb), color=RED, lw=1.6, style="<|-|>", scale=9)
            ax.text(-1.45, (5.0 + pb) / 2 - 0.15, "стекло\nниже метки", ha="right", va="center", fontsize=9.5, color=RED)
        # vessel and water
        top = v0 + 1.8
        ax.add_patch(Rectangle((-3.0, v0), 6.0, 1.8, fc=WATER, ec="none", alpha=0.6, zorder=1))
        ax.plot([-3.0, -3.0, 3.0, 3.0], [v0 + 2.5, v0, v0, v0 + 2.5], color=INK, lw=2.2, zorder=3)
        if k == 0 or k == 1:
            if k == 1:
                ax.plot([-3.0 + 0.05, 3.0 - 0.05], [top, top], color=WATER_D, lw=1.6)
            else:
                ax.plot([-3.0 + 0.05, 3.0 - 0.05], [top, top], color=WATER_D, lw=1.6)
        else:
            # water column between the glass and the surface, bulging up to the glass
            xs = np.linspace(-2.9, 2.9, 200)
            base = top
            bump = (pb - top) * np.exp(-(np.abs(xs) - 1.0).clip(0) / 0.55) * (np.abs(xs) < 3.5)
            prof = base + bump
            # the vessel rectangle already fills v0..top: fill only the bulge, or the lower part gets two layers
            ax.fill_between(xs, top, prof, color=WATER, alpha=0.6, zorder=1)
            ax.plot(xs, prof, color=WATER_D, lw=1.6, zorder=3)
            arrow(ax, (1.5, pb + 0.55), (1.5, pb - 0.25), color=RED, lw=2.4, scale=16)
            ax.text(1.75, pb + 0.35, "притяжение", color=RED, fontsize=10, va="center")
        ax.text(0, -0.15, st["cap"], ha="center", va="top", fontsize=11)
    save(fig, "glass-water-spring.png")


def _drop(ax, a, theta_deg, fc, soot=False):
    """A sessile drop with the contact angle theta at the right contact point; a is the base radius."""
    th = np.deg2rad(theta_deg)
    R = a / np.sin(th)
    yc = -R * np.cos(th)
    ang_r = np.arctan2(-yc, a)
    t = np.linspace(ang_r, np.pi - ang_r, 300)
    ax.add_patch(Polygon(np.column_stack([R * np.cos(t), yc + R * np.sin(t)]), fc=fc, ec=INK, lw=1.8, zorder=3))
    ax.add_patch(Rectangle((-2.6, -0.5), 5.2, 0.5, fc=SOOT if soot else GLASS, ec=INK, lw=1.4, zorder=2))
    P = np.array([a, 0.0])
    L = 1.3
    ax.plot([a, a - L], [0, 0], color=RED, lw=1.4, ls="--", zorder=4)
    ax.plot([a, a - L * np.cos(th)], [0, L * np.sin(th)], color=RED, lw=1.8, zorder=4)
    ax.add_patch(Arc(P, 1.4, 1.4, theta1=180 - theta_deg, theta2=180, color=RED, lw=1.8, zorder=5))
    mid = np.deg2rad(180 - theta_deg / 2)
    off = 0.2 if theta_deg < 60 else 0.0
    ax.text(a + 0.95 * np.cos(mid), 0.95 * np.sin(mid) + off, "$\\theta$", color=RED, fontsize=15, ha="center", va="center", zorder=6)


def fig_wetting_drops():
    fig, axes = blank_row(3, 12.6, 4.2, (-2.7, 2.7), (-0.6, 2.7))
    _drop(axes[0], 1.85, 25, WATER)
    axes[0].text(0, -0.75, "вода на чистом стекле:\nсмачивание", ha="center", va="top", fontsize=11)
    _drop(axes[1], 0.85, 140, WATER, soot=True)
    axes[1].text(0, -0.75, "вода на закопчённом стекле:\nнесмачивание", ha="center", va="top", fontsize=11)
    _drop(axes[2], 0.75, 145, tint(INK, 0.75))
    axes[2].text(0, -0.75, "ртуть на стекле:\nнесмачивание", ha="center", va="top", fontsize=11)
    save(fig, "wetting-drops-contact-angle.png")


def fig_meniscus():
    fig, axes = blank_row(2, 9.6, 4.4, (-1.2, 4.6), (-2.2, 2.4))
    lam = 0.5
    for ax, h, title in ((axes[0], 0.75, "смачивание: жидкость\nподнимается по стенке"),
                         (axes[1], -0.55, "несмачивание: жидкость\nоттянута от стенки")):
        x = np.linspace(0, 4.4, 400)
        y = h * np.exp(-x / lam)
        ax.fill_between(x, -2.0, y, color=WATER if h > 0 else tint(INK, 0.75), alpha=0.75, zorder=1)
        ax.plot(x, y, color=INK, lw=2, zorder=3)
        ax.add_patch(Rectangle((-0.6, -2.0), 0.6, 4.3, fc=GLASS, ec=INK, lw=1.6, zorder=2))
        s = abs(h) / lam
        if h > 0:
            t1, t2 = -90, -np.degrees(np.arctan(s))
            theta = np.degrees(np.arctan(1 / s))
        else:
            t1, t2 = -90, np.degrees(np.arctan(s))
            theta = 90 + np.degrees(np.arctan(s))
        P = (0, h)
        ax.add_patch(Arc(P, 1.5, 1.5, theta1=t1, theta2=t2, color=RED, lw=1.8, zorder=5))
        ax.plot([0, 0], [h, h - 1.1], color=RED, lw=1.4, ls="--", zorder=4)
        ta = np.radians(t2)
        ax.plot([0, 1.1 * np.cos(ta)], [h, h + 1.1 * np.sin(ta)], color=RED, lw=1.8, zorder=4)
        mid = np.radians((t1 + t2) / 2)
        ax.text(1.0 * np.cos(mid) + 0.1, h + 1.0 * np.sin(mid), "$\\theta$", color=RED, fontsize=15, ha="center", va="center", zorder=6)
        ax.text(2.2, -2.15, title, ha="center", va="top", fontsize=11)
        ax.text(-0.3, 0.6, "стекло", ha="center", va="center", fontsize=10, rotation=90)
    save(fig, "meniscus-wetting-nonwetting.png")


def fig_glue_solder():
    fig, axes = blank_row(2, 10.4, 3.6, (-4.2, 4.2), (-1.6, 2.6))
    ax = axes[0]
    ax.add_patch(Rectangle((-3.5, 0.3), 7, 0.9, fc=tint(INK, 0.75), ec=INK, lw=1.6))
    ax.add_patch(Rectangle((-3.5, -0.9), 7, 0.9, fc=tint(INK, 0.75), ec=INK, lw=1.6))
    ax.add_patch(Rectangle((-3.5, 0.0), 7, 0.3, fc=tint(WARM, 0.3), ec=COPPER, lw=1.0))
    arrow(ax, (2.2, 2.0), (1.5, 0.35), color=INK, lw=1.4, scale=11)
    ax.text(-3.4, 1.9, "тонкая плёнка клея\nсмачивает обе поверхности", fontsize=10, va="center", ha="left")
    ax.set_title("склеивание", fontsize=12)
    ax = axes[1]
    # a pin standing on a plate; the solder climbs both with concave fillets
    ax.add_patch(Rectangle((-3.5, -0.7), 7, 0.9, fc=tint(INK, 0.75), ec=INK, lw=1.6, zorder=2))
    ax.add_patch(Rectangle((-0.3, 0.2), 0.6, 2.0, fc=tint(INK, 0.75), ec=INK, lw=1.6, zorder=2))
    for s in (-1, 1):
        xs = np.linspace(0.3, 1.9, 100)
        ys = 0.2 + 1.0 * np.exp(-(xs - 0.3) / 0.45)
        ax.fill_between(s * xs, 0.2, ys, color=LIGHT, ec="none", zorder=3)
        ax.plot(s * xs, ys, color=INK, lw=1.6, zorder=4)
    arrow(ax, (2.6, 1.6), (1.0, 0.55), color=INK, lw=1.4, scale=11)
    ax.text(2.7, 1.6, "припой растекается\nпо металлу и застывает", fontsize=10, va="center", ha="left")
    ax.set_xlim(-4.2, 6.0)
    ax.set_title("пайка", fontsize=12)
    save(fig, "gluing-soldering.png")


def fig_water_strider():
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    x = np.linspace(-4, 4, 800)
    feet = [-2.6, -1.6, -0.6, 0.6, 1.6, 2.6]
    y = -0.28 * sum(np.exp(-((x - f) / 0.28) ** 2) for f in feet)
    ax.fill_between(x, -1.5, y, color=WATER, alpha=0.6)
    ax.plot(x, y, color=WATER_D, lw=2)
    ax.add_patch(Ellipse((0, 1.9), 3.0, 0.9, fc=COPPER, ec=INK, lw=1.6, zorder=4))
    for f in feet:
        ax.plot([f * 0.4, f], [1.7, -0.22], color=INK, lw=1.6, zorder=3)
    arrow(ax, (0, 3.2), (0, 2.45), color=RED, lw=2.4, scale=16)
    ax.text(0.2, 2.85, "сила тяжести", color=RED, fontsize=11, va="center")
    ax.text(0, -0.9, "лапки не смачиваются: поверхность воды\nпрогибается и держит насекомое", ha="center", va="center", fontsize=11)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-1.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "water-strider-surface.png")


# ---------- Агрегатные состояния вещества -----------------------------------

def fig_shape_volume():
    rng = np.random.default_rng(21)
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.4))
    for ax in axes:
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-0.9, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
    # solids: cube and cylinder
    ax = axes[0]
    fc = tint(INK, 0.75)
    ax.add_patch(Rectangle((-2.7, 0), 1.7, 1.7, fc=fc, ec=INK, lw=1.6))
    ax.add_patch(Polygon([(-2.7, 1.7), (-1.0, 1.7), (-0.5, 2.2), (-2.2, 2.2)], fc=shade(fc, 1.1), ec=INK, lw=1.6))
    ax.add_patch(Polygon([(-1.0, 0), (-0.5, 0.5), (-0.5, 2.2), (-1.0, 1.7)], fc=shade(fc, 0.85), ec=INK, lw=1.6))
    # the side has no outline of its own: its bottom edge would cut the front half of the lower ellipse
    ax.add_patch(Rectangle((0.5, 0.0), 1.8, 2.2, fc=fc, ec="none", zorder=1))
    ax.plot([0.5, 0.5], [0.0, 2.2], color=INK, lw=1.6, zorder=2)
    ax.plot([2.3, 2.3], [0.0, 2.2], color=INK, lw=1.6, zorder=2)
    ax.add_patch(Ellipse((1.4, 2.2), 1.8, 0.5, fc=shade(fc, 1.1), ec=INK, lw=1.6, zorder=3))
    ax.add_patch(Ellipse((1.4, 0.0), 1.8, 0.5, fc=fc, ec=INK, lw=1.6, zorder=0))
    ax.set_title("твёрдые тела", fontsize=13)
    ax.text(0, -0.75, "сохраняют форму и объём", ha="center", fontsize=11)
    # liquid: same volume in a cylindrical glass and a conical flask
    ax = axes[1]
    ax.add_patch(Rectangle((-2.7, 0), 1.6, 2.4, fc="none", ec=INK, lw=2))
    ax.add_patch(Rectangle((-2.7, 0), 1.6, 1.15, fc=WATER, ec="none", alpha=0.7))
    ax.plot([-2.7, -1.1], [1.15, 1.15], color=RED, lw=2.2)
    fl = [(0.4, 0), (2.8, 0), (1.9, 1.6), (1.9, 2.6), (1.3, 2.6), (1.3, 1.6)]
    fl = [(0.3, 0), (2.7, 0), (1.85, 1.6), (1.85, 2.7), (1.15, 2.7), (1.15, 1.6)]
    ax.add_patch(Polygon(fl, fc="none", ec=INK, lw=2, closed=True))
    hw = 1.2 - 0.9 * (1.0 / 1.6)
    ax.add_patch(Polygon([(0.3, 0), (2.7, 0), (1.5 + hw, 1.0), (1.5 - hw, 1.0)], fc=WATER, ec="none", alpha=0.7))
    ax.plot([1.5 - hw, 1.5 + hw], [1.0, 1.0], color=RED, lw=2.2)
    ax.annotate("свободная\nповерхность", (-1.9, 1.15), (-0.5, 3.15), color=RED, fontsize=10, ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.set_title("жидкости", fontsize=13)
    ax.text(0, -0.75, "форму не сохраняют,\nобъём сохраняют", ha="center", va="top", fontsize=11)
    # gas: the same amount in a large and in a small tank
    ax = axes[2]
    ax.add_patch(Rectangle((-3.2, 0.0), 3.0, 2.6, fc="none", ec=INK, lw=2))
    ax.add_patch(Rectangle((0.4, 0.0), 1.8, 1.5, fc="none", ec=INK, lw=2))
    big = rsa(rng, 26, (-3.1, -0.3), (0.1, 2.5), 0.42)
    small = rsa(rng, 26, (0.5, 2.1), (0.1, 1.4), 0.25)
    ax.scatter(*big.T, s=22, color=RED)
    ax.scatter(*small.T, s=22, color=RED)
    ax.set_title("газы", fontsize=13)
    ax.text(0, -0.75, "не сохраняют\nни форму, ни объём", ha="center", va="top", fontsize=11)
    save(fig, "states-shape-volume.png")


def fig_three_states():
    rng = np.random.default_rng(7)
    fig, grid = plt.subplots(2, 2, figsize=(9.0, 9.4))
    axes = list(grid.flat)
    R = 0.5
    box = 4.6
    for ax in axes:
        ax.set_xlim(-0.3, box + 0.3)
        ax.set_ylim(-0.3, box + 0.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.plot([0, box, box, 0, 0], [0, 0, box, box, 0], color=INK, lw=1.6)
    ax = axes[0]
    sp = 1.12
    o = (box - 3 * sp) / 2
    for i in range(4):
        for j in range(4):
            if i < 3:
                ax.plot([o + i * sp, o + (i + 1) * sp], [o + j * sp] * 2, color=GREY, lw=1.0, zorder=1)
            if j < 3:
                ax.plot([o + i * sp] * 2, [o + j * sp, o + (j + 1) * sp], color=GREY, lw=1.0, zorder=1)
    for i in range(4):
        for j in range(4):
            ax.add_patch(Circle((o + i * sp, o + j * sp), R, fc=tint(BLUE, 0.55), ec=INK, lw=1.1, zorder=3))
    ax.set_title("твёрдое тело", fontsize=14)
    ax.text(box / 2, -0.4, "ряды: кристаллическая решётка", ha="center", va="top", fontsize=12)
    ax = axes[1]
    pts = rsa(rng, 15, (R, box - R), (R, box - R), 1.02 * 2 * R, tries=200000)
    for p in pts:
        ax.add_patch(Circle(p, R, fc=tint(BLUE, 0.55), ec=INK, lw=1.1, zorder=3))
    ax.set_title("жидкость", fontsize=14)
    ax.text(box / 2, -0.4, "плотно, но порядка нет", ha="center", va="top", fontsize=12)
    ax = axes[2]
    pts = rsa(rng, 5, (R, box - R), (R, box - R), 1.75, tries=200000)
    for p in pts:
        ax.add_patch(Circle(p, R, fc=tint(BLUE, 0.55), ec=INK, lw=1.1, zorder=3))
    ax.set_title("газ", fontsize=14)
    ax.text(box / 2, -0.4, "расстояния много больше молекул", ha="center", va="top", fontsize=12)
    ax = axes[3]
    ions = rsa(rng, 5, (R, box - R), (R, box - R), 1.9, tries=200000)
    for p in ions:
        ax.add_patch(Circle(p, R, fc=tint(RED, 0.55), ec=INK, lw=1.1, zorder=3))
        ax.text(p[0], p[1], "+", ha="center", va="center", fontsize=13, zorder=4)
    # plasma is neutral: one electron per singly charged ion
    electrons = []
    while len(electrons) < len(ions):
        p = np.array([rng.uniform(0.3, box - 0.3), rng.uniform(0.3, box - 0.3)])
        if all(np.hypot(*(p - q)) > 0.8 for q in ions) and all(np.hypot(*(p - q)) > 0.5 for q in electrons):
            electrons.append(p)
            ax.add_patch(Circle(p, 0.17, fc=tint(BLUE, 0.45), ec=INK, lw=0.9, zorder=3))
            ax.text(p[0], p[1] - 0.005, "−", ha="center", va="center", fontsize=8, zorder=4)
    ax.set_title("плазма", fontsize=14)
    ax.text(box / 2, -0.4, "ионы и свободные электроны", ha="center", va="top", fontsize=12)
    save(fig, "three-states-molecules.png")


def _ou(rng, n, centre, k=0.22, s=0.07):
    p = np.array(centre, float)
    out = [p.copy()]
    for _ in range(n):
        p = p - k * (p - centre) + s * rng.normal(size=2)
        out.append(p.copy())
    return np.array(out)


def fig_trajectories():
    rng = np.random.default_rng(13)
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.4))
    for ax in axes:
        ax.set_xlim(-0.3, 5.3)
        ax.set_ylim(-0.3, 5.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.plot([0, 5, 5, 0, 0], [0, 0, 5, 5, 0], color=INK, lw=1.4)
    ax = axes[0]
    sites = [(1 + 1.5 * i, 1 + 1.5 * j) for i in range(3) for j in range(3)]
    for k, s in enumerate(sites):
        tr = _ou(rng, 220, s)
        ax.plot(*tr.T, color=[RED, BLUE, GREEN][k % 3], lw=0.8)
        ax.plot(*s, "k+", ms=5, zorder=5)
    ax.set_title("твёрдое тело:\nколебания на месте", fontsize=12)
    ax = axes[1]
    sites = [(1.0, 1.2), (2.3, 1.7), (3.4, 1.0), (3.9, 2.4), (2.9, 3.3), (1.6, 3.6)]
    path = []
    for s in sites:
        path.append(_ou(rng, 45, s))
    full = np.vstack(path)
    ax.plot(*full.T, color=WATER_D, lw=0.9)
    for s in sites:
        ax.plot(*s, "k+", ms=5, zorder=5)
    ax.plot(*full[0], "o", color=INK, ms=5)
    ax.set_title("жидкость: колебания,\nпотом прыжок к соседу", fontsize=12)
    ax = axes[2]
    p = np.array([0.8, 0.9])
    pts = [p.copy()]
    ang = 0.7
    for _ in range(14):
        ang += rng.uniform(-2.4, 2.4)
        step = rng.uniform(1.0, 2.6)
        q = p + step * np.array([np.cos(ang), np.sin(ang)])
        for c in (0, 1):
            if q[c] < 0.1:
                q[c] = 0.2 - q[c]
                ang = np.pi - ang if c == 0 else -ang
            if q[c] > 4.9:
                q[c] = 9.8 - q[c]
                ang = np.pi - ang if c == 0 else -ang
        pts.append(q.copy())
        p = q
    pts = np.array(pts)
    ax.plot(*pts.T, color=RED, lw=1.4, marker="o", ms=4)
    ax.set_title("газ: прямые отрезки\nи столкновения", fontsize=12)
    save(fig, "molecule-trajectories-states.png")


def fig_transitions():
    fig, ax = plt.subplots(figsize=(12.6, 4.6))
    ax.set_xlim(-1.8, 20.4)
    ax.set_ylim(-3.6, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    names = ["ТВЁРДОЕ", "ЖИДКОЕ", "ГАЗ", "ПЛАЗМА"]
    cols = [tint(INK, 0.75), tint(SKY, 0.6), tint(WARM, 0.5), tint(ACCENT, 0.6)]
    xs = [0, 6.2, 12.4, 18.6]
    for x, n, c in zip(xs, names, cols):
        ax.add_patch(Rectangle((x - 1.2, -0.7), 2.4, 1.4, fc=c, ec=INK, lw=2, zorder=3))
        ax.text(x, 0, n, ha="center", va="center", fontsize=12, zorder=4)
    fwd = ["плавление", "парообразование", "ионизация"]
    back = ["кристаллизация", "конденсация", "рекомбинация"]
    for i in range(3):
        a, b = xs[i] + 1.3, xs[i + 1] - 1.3
        arrow(ax, (a, 0.25), (b, 0.25), color=RED, lw=1.8)
        arrow(ax, (b, -0.25), (a, -0.25), color=WATER_D, lw=1.8)
        ax.text((a + b) / 2, 0.42, fwd[i], ha="center", va="bottom", fontsize=11, color=RED)
        ax.text((a + b) / 2, -0.42, back[i], ha="center", va="top", fontsize=11, color=WATER_D)
    ax.add_patch(FancyArrowPatch((0, 0.8), (12.4, 0.8), connectionstyle="arc3,rad=-0.4", arrowstyle="-|>", mutation_scale=15, lw=1.8, color=RED, zorder=2))
    ax.text(6.2, 3.3, "сублимация (возгонка)", ha="center", fontsize=11, color=RED)
    ax.add_patch(FancyArrowPatch((12.4, -0.8), (0, -0.8), connectionstyle="arc3,rad=-0.4", arrowstyle="-|>", mutation_scale=15, lw=1.8, color=WATER_D, zorder=2))
    ax.text(6.2, -3.3, "конденсация сразу в твёрдое (иней)", ha="center", va="top", fontsize=11, color=WATER_D)
    save(fig, "state-transitions-scheme.png")


def fig_heating():
    rng = np.random.default_rng(31)
    fig = plt.figure(figsize=(11.0, 4.6))
    gs = GridSpec(2, 2, width_ratios=[1, 1.5], hspace=0.3, wspace=0.28)
    a1 = fig.add_subplot(gs[0, 0])
    a2 = fig.add_subplot(gs[1, 0])
    ag = fig.add_subplot(gs[:, 1])
    for a in (a1, a2):
        a.set_xlim(-0.3, 4.3)
        a.set_ylim(-0.3, 2.3)
        a.set_aspect("equal")
        a.axis("off")
    for i in range(6):
        for j in range(4):
            a1.add_patch(Circle((0.35 + i * 0.7, 0.3 + j * 0.55), 0.24, fc=tint(BLUE, 0.55), ec=INK, lw=0.9))
    a1.set_title("кристалл: решётка", fontsize=11)
    pts = rsa(rng, 24, (0.25, 4.0), (0.25, 2.0), 0.6, tries=100000)
    for p in pts:
        a2.add_patch(Circle(p, 0.24, fc=tint(WARM, 0.3), ec=INK, lw=0.9))
    a2.set_title("аморфное тело: беспорядок", fontsize=11)
    t = np.linspace(0, 10, 500)
    cr = np.interp(t, [0, 3, 5, 10], [20, 232, 232, 400])
    am = 20 + 380 * (1 / (1 + np.exp(-(t - 5.2) / 1.7)) - 1 / (1 + np.exp(5.2 / 1.7))) / (1 / (1 + np.exp(-(10 - 5.2) / 1.7)) - 1 / (1 + np.exp(5.2 / 1.7)))
    ag.plot(t, cr, color=WATER_D, lw=2.6, label="олово: плавится при 232 °C")
    ag.plot(t, am, color=RED, lw=2.6, label="стекло: размягчается постепенно")
    ag.axhline(232, color=GREY, lw=1, ls="--")
    ag.set_xlabel("время нагрева")
    ag.set_ylabel("температура")
    ag.set_xticks([])
    ag.set_yticks([232])
    ag.set_yticklabels(["232 °C"])
    ag.legend(frameon=False, loc="lower right", fontsize=11)
    ag.grid(color=GRID, lw=0.7)
    ag.set_title("схема нагрева без точных чисел", fontsize=11)
    save(fig, "heating-crystal-vs-amorphous.png")


if __name__ == "__main__":
    fig_pair_forces()
    fig_force_curve()
    fig_chalk_plasticine()
    fig_glass_spring()
    fig_wetting_drops()
    fig_meniscus()
    fig_glue_solder()
    fig_water_strider()
    fig_shape_volume()
    fig_three_states()
    fig_trajectories()
    fig_transitions()
    fig_heating()
