"""Figures for the note "Плавание судов. Воздухоплавание", ship part (lesson 68).

Run: python3 ships.py
PNG files go to content/07. Закон Архимеда и плавание/00. Вложения/, prefix ship-.
Curves marked "не из лекции" are reference models, not from the lesson.
"""
from floating_common import *  # noqa: F401,F403

HULL = tint(INK, 0.6)
HULL_EDGE = INK


def hull(ax, cx, ykeel, w=9.0, h=2.2, fc=HULL, ec=HULL_EDGE, deck=True, funnel=True):
    """Ship side view: a trapezoid hull with keel at ykeel and deck line at ykeel + h."""
    pts = [(cx - w / 2, ykeel + h), (cx - w / 2 + 1.2, ykeel), (cx + w / 2 - 2.0, ykeel), (cx + w / 2, ykeel + h)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=2, zorder=4))
    if deck:
        rect(ax, cx - 1.6, ykeel + h, 2.6, 1.0, fc=LIGHT, ec=ec, lw=1.6, z=4)
        if funnel:
            rect(ax, cx - 0.6, ykeel + h + 1.0, 0.8, 0.9, fc=C_F, ec=ec, lw=1.4, z=4)
    return pts


# ------------------------------------------------------------- 1. steel block to ship


def steel_to_ship():
    fig, axes = blank(15, 5.4, (0, 50), (-0.5, 15))
    ax = axes[0]
    titles = ["Сплошной кусок\nстали тонет", "Внутри пустота:\nобъём растёт, масса та же", "Тонкая оболочка\nвсплывает", "Срезали верх,\nдобавили палубу"]
    for i in range(4):
        x0 = i * 12.5
        cx = x0 + 6.2
        liquid(ax, x0 + 0.3, x0 + 12.2, 0, 8.6)
        vessel(ax, x0 + 0.3, x0 + 12.2, 0, 12.4)
        label(ax, cx, 14.0, titles[i], fs=10.5)
        if i == 0:
            rect(ax, cx - 1.1, 0, 2.2, 2.2, fc=STEEL, ec=HULL_EDGE, lw=2, z=4)
        elif i == 1:
            rect(ax, cx - 2.0, 0, 4.0, 4.0, fc=STEEL, ec=HULL_EDGE, lw=2, z=4)
            # Same steel volume as frame 1: 2.2^3 = 10.6 = 4.0^3 - 3.76^3, so the wall is thin (0.12)
            rect(ax, cx - 1.88, 0.12, 3.76, 3.76, fc=PAPER, ec=HULL_EDGE, lw=1.0, z=5)
            label(ax, cx, 2.0, "пустота", fs=9, color=GREY, zorder=8)
        elif i == 2:
            yb = 8.6 - 3.4
            rect(ax, cx - 2.6, yb, 5.2, 5.2, fc=STEEL, ec=HULL_EDGE, lw=2, z=4)
            rect(ax, cx - 2.5, yb + 0.1, 5.0, 5.1, fc=PAPER, ec="none", z=5)
            label(ax, cx, yb + 3.7, "пустота", fs=9, color=GREY, zorder=8)
        else:
            yb = 8.6 - 2.2
            hull(ax, cx, yb, w=9.5, h=2.2)
            label(ax, cx, 3.5, "  ", fs=9)
    save(fig, "ship-steel-to-ship.png")


# ------------------------------------------------------------- 2. draft, waterline: three loads


def draft_waterline():
    fig, axes = blank(15, 5.2, (0, 45), (-1, 12.5))
    ax = axes[0]
    names = ["Недогружено", "Груз по ватерлинию", "Перегружено"]
    drafts = [1.6, 2.2, 2.9]
    for i in range(3):
        x0 = i * 15
        cx = x0 + 7.5
        surf = 4.0
        liquid(ax, x0 + 0.3, x0 + 14.7, -0.6, surf)
        d = drafts[i]
        hull(ax, cx, surf - d, w=11.0, h=4.2, funnel=True)
        # waterline mark drawn at the same hull height for all three (draft 2.2)
        wl = surf - d + 2.2
        f = 2.2 / 4.2
        xl = cx - 4.3 - 1.2 * f
        xr = cx + 3.5 + 2.0 * f
        line(ax, [xl, xr], [wl, wl], color=C_F, lw=3.6, z=8)
        # keel dimension
        arrow(ax, (cx + 6.4, surf), (cx + 6.4, surf - d), color=INK, lw=1.4, style="<|-|>", scale=9)
        label(ax, cx + 6.65, surf - d / 2, r"$H$", fs=11.5, ha="left")
        label(ax, cx, 11.4, names[i], fs=12)
        if i == 0:
            label(ax, cx, 9.5, "ватерлиния выше воды", fs=10, color=C_F)
        elif i == 1:
            label(ax, cx, 9.5, "ватерлиния на воде", fs=10, color=C_F)
        else:
            label(ax, cx, 9.5, "ватерлиния под водой", fs=10, color=C_F)
        # (surf line over hull)
        line(ax, [x0 + 0.3, x0 + 14.7], [surf, surf], color=WATER_EDGE, lw=1.6, z=7)
    save(fig, "ship-draft-waterline.png")


# ------------------------------------------------------------- 3. draft scale on the bow


def draft_scale():
    fig, axes = blank(5.8, 5.2, (0, 12), (-0.5, 12.5))
    ax = axes[0]
    # bow section: vertical hull plate with a scale in dm (21 dm at the waterline)
    rect(ax, 1.0, -0.2, 3.2, 12.0, fc=HULL, ec=HULL_EDGE, lw=2, z=3)
    surf = 6.0
    liquid(ax, 0.3, 11.7, -0.2, surf)
    marks = [(12, 3.5), (14, 4.1), (16, 4.7), (18, 5.3), (20, 5.9), (22, 6.5), (24, 7.1)]
    # marks: draft increases downwards, so a mark is higher up for a smaller number
    dm_per_unit = 2 / 0.6
    for v in range(12, 26, 2):
        y = surf - (v - 21) / dm_per_unit * 1.0  # 21 dm at the surface
        line(ax, [4.2, 4.9], [y, y], color=INK, lw=1.4, z=6)
        label(ax, 5.05, y, str(v), fs=9.5, ha="left")
    line(ax, [1.0, 4.2], [surf, surf], color=C_F, lw=3.0, z=7)
    label(ax, 8.4, 9.6, "осадка в дециметрах:\nна ватерлинии 21 дм\n= 2 м 10 см", fs=10.5)
    label(ax, 2.6, 11.0, "борт", fs=10)
    save(fig, "ship-draft-scale.png")


# ------------------------------------------------------------- 4. displacement: water displaced weighs as the ship


def displacement():
    fig, axes = blank(11.5, 5.4, (0, 24), (-1, 12.5))
    ax = axes[0]
    surf = 4.4
    liquid(ax, 0.3, 23.7, -0.6, surf)
    d = 2.6
    hull(ax, 7.0, surf - d, w=11.0, h=4.2)
    # displaced volume shaded (same hull shape below the surface)
    label(ax, 7.0, 11.4, "Судно, загруженное по ватерлинию", fs=11.5)
    # Floating at rest: F_А and F_т have the same length (2.9)
    arrow(ax, (4.2, surf - 1.3), (4.2, surf + 1.6), color=C_A, lw=2.6)
    arrow(ax, (4.2, surf - 1.3), (4.2, surf - 4.2), color=C_F, lw=2.6)
    label(ax, 4.5, surf + 1.4,r"$F_А$", fs=12, color=C_A, ha="left")
    label(ax, 4.5, surf - 3.8, r"$F_т = Mg$", fs=12, color=C_F, ha="left")
    # displaced water: a block of water beside the ship
    rect(ax, 15.0, 1.0, 6.0, 4.0, fc=WATER, ec=WATER_EDGE, lw=2, z=3)
    label(ax, 18.0, 3.0, "вытесненная\nвода", fs=10.5)
    label(ax, 18.0, 6.6, r"$P_в = \rho_в g V_{погр}$", fs=11)
    label(ax, 18.0, 8.0, r"$F_А = P_в$", fs=11, color=C_A)
    label(ax, 18.0, 10.0, "водоизмещение\n$=$ масса такой воды", fs=10.5)
    save(fig, "ship-displacement.png")


# ------------------------------------------------------------- 5. barge with cargo removed


def barge():
    fig, axes = blank(14, 5.6, (0, 40), (-1, 12.5))
    ax = axes[0]
    for i, loaded in enumerate([True, False]):
        x0 = i * 20
        cx = x0 + 9.5
        surf = 4.6
        liquid(ax, x0 + 0.3, x0 + 18.7, -0.6, surf)
        ybot = surf - (3.0 if loaded else 2.5)
        ytop = ybot + 5.0
        rect(ax, cx - 6, ybot, 12.0, 5.0, fc=HULL, ec=HULL_EDGE, lw=2, z=4)
        if loaded:
            rect(ax, cx - 3.5, ytop, 7.0, 2.2, fc=tint(COPPER, 0.55), ec=COPPER, lw=2, z=4)
            label(ax, cx, ytop + 1.1, "груз", fs=10.5)
        wl = ybot + 3.0
        line(ax, [cx - 6, cx + 6], [wl, wl], color=C_F, lw=3.4, z=8)
        label(ax, cx, 11.6, "Груженая баржа" if loaded else "Груз сняли", fs=12)
        label(ax, cx, 10.4, r"$F_т = Mg$" if loaded else r"$F'_т = (M - m_г)g$", fs=11, color=C_F)
        line(ax, [x0 + 0.3, x0 + 18.7], [surf, surf], color=WATER_EDGE, lw=1.6, z=7)
        if not loaded:
            arrow(ax, (cx + 7.4, surf - 2.5), (cx + 7.4, surf - 3.0), color=INK, lw=1.4, style="<|-|>", scale=8)
            label(ax, cx + 7.7, surf - 2.75, r"$\Delta H$", fs=11.5, ha="left")
            line(ax, [cx + 6, cx + 7.4], [surf - 3.0, surf - 3.0], color=GREY, lw=1, z=6, ls=":")
            label(ax, cx, wl + 0.55, "ватерлиния выше воды", fs=9.5, color=C_F)
    save(fig, "ship-barge-cargo.png")


# ------------------------------------------------------------- 6. draft vs total mass


def draft_vs_mass():
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    m = np.linspace(0, 22000, 300)
    rho, S = 1000.0, 1000.0
    ax.plot(m, m * 1000 / (rho * S), color=C_A, lw=2.6, label="баржа с вертикальными бортами")
    ax.plot(m, 20 * np.sqrt(m / 20000), color=GREY, lw=2.2, ls="--", label="острый корпус (не из лекции)")
    ax.axvspan(20000, 22000, color=SINKS, zorder=0)
    label(ax, 21000, 12.0, "перегруз", fs=10.5, color=C_F, rotation=90)
    ax.plot([20000], [20], "o", color=INK, ms=8, zorder=5)
    ax.plot([19500], [19.5], "o", color=C_F, ms=8, zorder=5)
    ax.annotate("водоизмещение\n20 000 т, $H=20$ м", (20000, 20), (11500, 21.3), fontsize=10,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    ax.annotate("сняли 500 т:\n$\\Delta H=0{,}5$ м", (19500, 19.5), (12500, 9.2), fontsize=10, color=C_F,
                arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax.set_xlim(0, 22000)
    ax.set_ylim(0, 24)
    style_axes(ax, "Масса судна с грузом $M$, т", "Осадка $H$, м", "Осадка растёт с нагрузкой")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    fig.tight_layout()
    save(fig, "ship-draft-vs-cargo.png")


# ------------------------------------------------------------- 7. raft with tourists


def raft():
    fig = plt.figure(figsize=(12.5, 4.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1])
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 18)
    ax.set_ylim(-1, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    surf = 3.2
    liquid(ax, 0.3, 17.7, -0.6, surf)
    r = 1.1
    xs = [3.0 + 2.2 * k for k in range(6)]
    for x in xs:
        ax.add_patch(plt.Circle((x, surf - r), r, fc=WOOD, ec=WOOD_EDGE, lw=2, zorder=4))
    label(ax, xs[-1] + 1.9, surf - r, "…", fs=14)
    line(ax, [0.3, 17.7], [surf, surf], color=WATER_EDGE, lw=2, z=7)
    for x in [4.5, 7.0, 9.5, 12.0]:
        yb = surf + 0.15
        line(ax, [x, x], [yb, yb + 1.3], color=INK, lw=2)
        ax.add_patch(plt.Circle((x, yb + 1.65), 0.35, fc=PAPER, ec=INK, lw=2, zorder=5))
    # At the limiting load F_А = F_т (both 1.6)
    arrow(ax, (17.0, surf - 1.0), (17.0, surf + 0.6), color=C_A, lw=2.4)
    arrow(ax, (17.0, surf - 1.0), (17.0, surf - 2.6), color=C_F, lw=2.4)
    label(ax, 16.6, surf + 0.4,r"$F_А$", fs=12, color=C_A, ha="right")
    label(ax, 16.6, surf - 2.3, r"$F_т$", fs=12, color=C_F, ha="right")
    label(ax, 9.0, 9.2, "Плот с $N$ брёвнами и $n$ туристами: брёвна почти целиком под водой", fs=10.5)
    ax2 = fig.add_subplot(gs[1])
    mt = np.linspace(45, 130, 200)
    ax2.plot(mt, 1507.96 / mt, color=C_A, lw=2.6)
    ax2.plot([70], [1507.96 / 70], "o", color=C_F, ms=9, zorder=5)
    ax2.plot([70, 70], [0, 1507.96 / 70], color=C_F, lw=1, ls=":")
    ax2.plot([45, 70], [21, 21], color=GREEN, lw=1.3, ls="--")
    ax2.annotate("$n=21{,}5$, значит\nсадится 21 турист", (70, 1507.96 / 70), (82, 27.5), fontsize=10, color=C_F,
                 arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax2.set_xlim(45, 130)
    ax2.set_ylim(0, 36)
    style_axes(ax2, "Масса туриста $m_т$, кг", "Число туристов $n$", "Сколько туристов держит плот")
    fig.tight_layout()
    save(fig, "ship-raft-tourists.png")


def main():
    steel_to_ship()
    draft_waterline()
    draft_scale()
    displacement()
    barge()
    draft_vs_mass()
    raft()


if __name__ == "__main__":
    main()
