"""Figures for the note "Плавание тел" (course Физика 7-9, lessons 67 and 70).

Run: python3 floating.py
PNG files go to content/07. Закон Архимеда и плавание/00. Вложения/, prefix float-.
"""
from floating_common import *  # noqa: F401,F403

RHO_W = 1000


def draw_block(ax, cx, ybot, w=2.6, h=2.0, fc=WOOD, ec=WOOD_EDGE):
    rect(ax, cx - w / 2, ybot, w, h, fc=fc, ec=ec, lw=2, z=4)


# ------------------------------------------------------------- 1. three cases + floating


def three_cases():
    fig, axes = blank(14, 4.9, (0, 40), (-1.8, 11.5))
    ax = axes[0]
    titles = ["Тонет", "Взвешено в толще", "Всплывает", "Плавает на поверхности"]
    cond = [
        r"$F_т > F_А$" + "\n" + r"$\rho_т > \rho_ж$",
        r"$F_т = F_А$" + "\n" + r"$\rho_т = \rho_ж$",
        r"$F_т < F_А$" + "\n" + r"$\rho_т < \rho_ж$",
        r"$F_т = F'_А$" + "\n" + r"$V_{погр} < V_т$",
    ]
    # The sinking body is drawn in the water column: on the bottom it would also need a support force
    ybots = [0.6, 2.8, 0.9, 4.6]
    fa_len = [0.8, 1.5, 2.3, 1.5]
    for i in range(4):
        x0 = i * 10
        cx = x0 + 5
        liquid(ax, x0 + 0.3, x0 + 9.7, -1.6, 6.5)
        vessel(ax, x0 + 0.3, x0 + 9.7, -1.6, 8.0)
        yb = ybots[i]
        draw_block(ax, cx, yb, h=2.4, fc=(STEEL if i == 0 else WOOD), ec=(MERC_EDGE if i == 0 else WOOD_EDGE))
        if i == 3:
            # submerged part hatch
            rect(ax, cx - 1.3, yb, 2.6, 6.5 - yb, fc="none", ec=WATER_EDGE, lw=0, hatch="///", z=5)
            yc = (yb + 6.5) / 2
        else:
            yc = yb + 1.2
        arrow(ax, (cx, yc), (cx, yc - 1.5), color=C_F, lw=2.4)
        arrow(ax, (cx, yc), (cx, yc + fa_len[i]), color=C_A, lw=2.4)
        label(ax, cx + 1.55, yc - 0.5, r"$F_т$", fs=12, color=C_F, ha="left")
        label(ax, cx + 0.4, yc + fa_len[i] + (0.75 if i == 0 else 0.35), (r"$F'_А$" if i == 3 else r"$F_А$"), fs=12, color=C_A, ha="left")
        label(ax, cx, 11.0, titles[i], fs=12.5)
        label(ax, cx, 9.2, cond[i], fs=11.5)
    save(fig, "float-three-cases.png")


# ------------------------------------------------------------- 2. submerged fraction vs body density


def fraction_line():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = np.linspace(0, 1400, 700)
    y = np.minimum(x / RHO_W, 1.0)
    ax.axvspan(RHO_W, 1400, color=SINKS, zorder=0)
    ax.plot(x, y, color=C_A, lw=2.6, zorder=3)
    label(ax, 1200, 0.5, "тонет:\nвсё тело\nпод водой", fs=11, color=C_F)
    label(ax, 250, 0.9, "плавает:\n" + r"$V_{погр}/V_т = \rho_т/\rho_ж$", fs=11, color=C_A)
    pts = [("пенопласт", 20, (60, 0.10)), ("сосна", 400, (470, 0.30)), ("лёд", 900, (930, 0.72)), ("пластилин", 1250, (1180, 0.87))]
    for name, r, (tx, ty) in pts:
        yy = min(r / RHO_W, 1.0)
        ax.plot([r], [yy], "o", color=INK, ms=7, zorder=5)
        ax.annotate(f"{name}\n{r}", (r, yy), (tx, ty), fontsize=10, ha="left", color=INK,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    ax.axvline(RHO_W, color=GREY, ls="--", lw=1.2)
    label(ax, RHO_W, -0.09, r"$\rho_ж$ (вода)", fs=10, color=GREY, va="top", transform=ax.get_xaxis_transform())
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 1.08)
    style_axes(ax, r"Плотность тела $\rho_т$, кг/м$^3$", r"Доля объёма под водой $V_{погр}/V_т$", "Погружение тела в воде")
    fig.tight_layout()
    save(fig, "float-fraction-line.png")


# ------------------------------------------------------------- 3. bodies of different density in water


def bodies_in_water():
    fig, axes = blank(12.5, 4.8, (0, 27), (0, 11.2))
    ax = axes[0]
    liquid(ax, 0.3, 26.7, 0, 6.0)
    vessel(ax, 0.3, 26.7, 0, 8.6)
    bodies = [
        ("пенопласт", 20, WOOD, WOOD_EDGE, LIGHT, MUTED),
        ("сосна", 400, WOOD, WOOD_EDGE, None, None),
        ("стеарин, лёд", 900, ICE, ICE_EDGE, None, None),
        ("пластилин", 1250, PLASTICINE, PLASTICINE_EDGE, None, None),
    ]
    for i, (name, rho, fc, ec, fc2, ec2) in enumerate(bodies):
        cx = 3.8 + i * 6.4
        if fc2:
            fc, ec = fc2, ec2
        f = min(rho / RHO_W, 1.0)
        if rho > RHO_W:
            yb = 0.0
        else:
            yb = 6.0 - f * 2.4
        rect(ax, cx - 1.5, yb, 3.0, 2.4, fc=fc, ec=ec, lw=2, z=4)
        rect(ax, cx - 1.5, yb, 3.0, min(6.0 - yb, 2.4), fc="none", ec=WATER_EDGE, lw=0, hatch="///", z=5)
        label(ax, cx, 10.7, name, fs=11.5)
        label(ax, cx, 9.9, rf"$\rho_т={rho}$ кг/м$^3$" if rho > 0 else "", fs=10, color=GREY)
        if rho > RHO_W:
            label(ax, cx, 3.6, "тонет", fs=11, color=C_F)
        else:
            label(ax, cx, 3.1, f"под водой {round(f * 100)} %", fs=10.5, color=C_A, zorder=11)
    save(fig, "float-bodies-in-water.png")


# ------------------------------------------------------------- 4. one body in water, oil, mercury


def three_liquids():
    fig, axes = blank(12.5, 5.0, (0, 30), (0, 11.2))
    ax = axes[0]
    data = [
        ("Керосин", 800, OIL, OIL_EDGE),
        ("Вода", 1000, WATER, WATER_EDGE),
        ("Ртуть", 13600, MERC, MERC_EDGE),
    ]
    rho_b = 400
    for i, (name, rho, fc, ec) in enumerate(data):
        cx = 5.0 + i * 10
        liquid(ax, cx - 4.4, cx + 4.4, 0, 6.5, fc=fc, ec=ec)
        vessel(ax, cx - 4.4, cx + 4.4, 0, 9.4)
        f = rho_b / rho
        h = 2.4
        yb = 6.5 - f * h
        rect(ax, cx - 1.6, yb, 3.2, h, fc=WOOD, ec=WOOD_EDGE, lw=2, z=4)
        rect(ax, cx - 1.6, yb, 3.2, 6.5 - yb, fc="none", ec=ec, lw=0, hatch="///", z=5)
        label(ax, cx, 10.6, rf"{name}, $\rho_ж={rho}$", fs=11.5)
        label(ax, cx, 1.9, f"под жидкостью\n{num(f * 100, 1)} %", fs=10.5, color=INK, zorder=11)
    label(ax, 15, 9.1, "", fs=1)
    save(fig, "float-three-liquids.png")


# ------------------------------------------------------------- 5. fraction vs liquid density


def fraction_liquids():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = np.logspace(np.log10(200), np.log10(20000), 500)
    y = np.minimum(400 / x, 1.0)
    ax.plot(x, y, color=C_A, lw=2.6, zorder=3)
    ax.axvspan(200, 400, color=SINKS, zorder=0)
    label(ax, 280, 0.55, "тонет", fs=11, color=C_F)
    pts = [("керосин", 800, (900, 0.62)), ("вода", 1000, (1450, 0.55)), ("вода Куяльника, $>1100$", 1100, (1900, 0.44)),
           ("раствор соли", 1230, (2400, 0.34)), ("ртуть", 13600, (5200, 0.16))]
    for name, r, (tx, ty) in pts:
        yy = 400 / r
        ax.plot([r], [yy], "o", color=INK, ms=7, zorder=5)
        ax.annotate(f"{name}", (r, yy), (tx, ty), fontsize=10, ha="left", color=INK,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    ax.set_xscale("log")
    ax.set_xlim(200, 20000)
    ax.set_ylim(0, 1.08)
    style_axes(ax, r"Плотность жидкости $\rho_ж$, кг/м$^3$ (логарифмическая шкала)",
               r"Доля объёма под жидкостью $V_{погр}/V_т$", "Сосновый брусок в разных жидкостях")
    fig.tight_layout()
    save(fig, "float-fraction-liquids.png")


# ------------------------------------------------------------- 6. forces vs submerged fraction


def forces_vs_fraction():
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = np.linspace(0, 1, 100)
    cases = [("сосна, $\\rho_т=400$", 400, C_A), ("лёд, $\\rho_т=900$", 900, GREEN), ("пластилин, $\\rho_т=1250$", 1250, PLASTICINE_EDGE)]
    for name, r, col in cases:
        ax.plot(x, RHO_W / r * x, color=col, lw=2.4, label=name)
    ax.axhline(1.0, color=INK, lw=2.2, ls="--")
    label(ax, 0.03, 1.07, r"сила тяжести $F_т$", fs=10.5, ha="left", va="bottom", color=INK)
    for name, r, col in cases[:2]:
        xe = r / RHO_W
        ax.plot([xe], [1.0], "o", color=col, ms=9, zorder=6)
        ax.plot([xe, xe], [0, 1.0], color=col, lw=1, ls=":")
        ax.annotate(f"равновесие\n{xe * 100:.0f} % под водой", (xe, 1.0), (xe - 0.02, 1.68 if r == 400 else 1.42),
                    fontsize=10, ha="right" if r == 400 else "right", color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.9))
    ax.text(0.98, 0.1, "пластилин: даже при полном погружении\n$F_А < F_т$, поэтому тонет", fontsize=10, color=C_F,
            ha="right", va="bottom")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 2.6)
    style_axes(ax, r"Доля объёма под водой $V_{погр}/V_т$", r"Сила Архимеда $F_А$ в долях $F_т$", "Как тело находит равновесие")
    ax.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.93))
    fig.tight_layout()
    save(fig, "float-force-vs-immersion.png")


# ------------------------------------------------------------- 7. iceberg


def iceberg():
    fig, axes = blank(9, 5.2, (0, 20), (0, 11.5))
    ax = axes[0]
    liquid(ax, 0.3, 19.7, 0, 8.0)
    # Heights above the waterline are scaled by 0.66 so the polygon areas give 10 % above (5.68) and 90 % below (51.0)
    pts_up = [(5.5, 8.0), (7.2, 8.92), (8.4, 8.66), (9.8, 9.58), (11.4, 8.79), (12.6, 8.0)]
    pts_dn = [(12.6, 8.0), (14.2, 6.0), (13.4, 3.6), (11.0, 1.6), (8.0, 1.2), (5.6, 3.0), (4.4, 5.6), (5.5, 8.0)]
    ax.add_patch(Polygon(pts_up, closed=True, fc=ICE, ec=ICE_EDGE, lw=2, zorder=4))
    ax.add_patch(Polygon(pts_dn, closed=True, fc=tint(SKY, 0.8), ec=ICE_EDGE, lw=2, zorder=3))
    line(ax, [0.3, 19.7], [8.0, 8.0], color=WATER_EDGE, lw=2, z=5)
    label(ax, 14.6, 9.0, "10 % над водой", fs=12, color=INK)
    label(ax, 9.0, 4.6, "90 %", fs=13, color=INK)
    label(ax, 16.0, 10.8, r"$\rho_л = 900$ кг/м$^3$", fs=11)
    label(ax, 16.6, 4.5, r"$\rho_в = 1000$ кг/м$^3$", fs=11, color=WATER_EDGE)
    save(fig, "float-iceberg.png")


# ------------------------------------------------------------- 8. areometer


def areometer():
    fig = plt.figure(figsize=(14, 6.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.5])
    ax1, ax2, ax3 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    K = 40.0

    def y_of(rho):
        return K * (1 - 1000 / rho)

    ticks = [1000, 1100, 1200, 1300]
    for ax, rho, fc, ec, name in [(ax1, 1000, WATER, WATER_EDGE, "Вода"), (ax2, 1230, SALT, SALT_EDGE, "Раствор соли")]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 29)
        ax.set_aspect("equal")
        ax.axis("off")
        surf = 16.0
        liquid(ax, 0.5, 9.5, 0.5, surf, fc=fc, ec=ec)
        vessel(ax, 0.5, 9.5, 0.5, 21.0)
        # The 1000 mark sits 2.0 above the stem top in water; a float flush with the surface would be in neutral equilibrium
        stem_up = 2.0
        top = surf + y_of(rho) + stem_up
        stem_l = 10.0
        cx = 5.0
        rect(ax, cx - 0.35, top - stem_l, 0.7, stem_l, fc=PAPER, ec=INK, lw=2, z=6)
        ax.add_patch(Ellipse((cx, top - stem_l - 1.6), 2.2, 3.6, fc=PAPER, ec=INK, lw=2, zorder=6))
        ax.add_patch(Ellipse((cx, top - stem_l - 3.0), 1.1, 1.0, fc=GREY, ec=INK, lw=1.5, zorder=7))
        for t in ticks:
            yt = top - stem_up - y_of(t)
            line(ax, [cx + 0.35, cx + 0.9], [yt, yt], color=INK, lw=1.4, z=7)
            label(ax, cx + 1.05, yt, str(t), fs=9.5, ha="left", zorder=8)
        label(ax, 5.0, 28.0, name, fs=12.5)
        line(ax, [0.5, 9.5], [surf, surf], color=ec, lw=2, z=7)
        if rho == 1230:
            ys = surf
            label(ax, 0.9, surf + 1.5, r"$\rho\approx1230$", fs=11, color=INK, ha="left")
    x = np.linspace(1000, 1300, 200)
    ax3.plot(x, K * (1 - 1000 / x), color=C_A, lw=2.6)
    for t in ticks:
        ax3.plot([t], [y_of(t)], "o", color=INK, ms=6)
    ax3.plot([1230], [y_of(1230)], "o", color=C_F, ms=8)
    ax3.annotate("раствор соли,\n1230", (1230, y_of(1230)), (1030, 6.5), fontsize=10, color=C_F,
                 arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax3.invert_yaxis()
    style_axes(ax3, r"Плотность жидкости $\rho_ж$, кг/м$^3$", "Глубина отметки на стержне (условные единицы)", "Шкала ареометра")
    fig.tight_layout()
    save(fig, "float-areometer.png")


# ------------------------------------------------------------- 9. Cartesian diver


def diver():
    fig, axes = blank(10.5, 5.6, (0, 22), (0, 12.4), n=1)
    ax = axes[0]
    for k, (cx, squeezed) in enumerate([(5.5, False), (16.5, True)]):
        # bottle
        liquid(ax, cx - 3.0, cx + 3.0, 0.4, 9.0)
        line(ax, [cx - 3.0, cx - 3.0, cx + 3.0, cx + 3.0], [9.6, 0.4, 0.4, 9.6], color=INK, lw=2.4, z=6)
        line(ax, [cx - 3.0, cx - 1.2, cx - 1.2], [9.6, 9.6, 10.6], color=INK, lw=2.4, z=6)
        line(ax, [cx + 3.0, cx + 1.2, cx + 1.2], [9.6, 9.6, 10.6], color=INK, lw=2.4, z=6)
        # test tube, open end down
        ytop = 7.0 if not squeezed else 4.6
        tw, th = 1.6, 3.6
        rect(ax, cx - tw / 2, ytop - th, tw, th, fc="none", ec=INK, lw=2, z=6)
        air_h = 2.1 if not squeezed else 1.4
        rect(ax, cx - tw / 2 + 0.05, ytop - air_h, tw - 0.1, air_h - 0.05, fc=PAPER, ec="none", z=5)
        rect(ax, cx - tw / 2 + 0.05, ytop - th + 0.05, tw - 0.1, th - air_h - 0.05, fc=WATER, ec="none", z=5)
        line(ax, [cx - tw / 2, cx + tw / 2], [ytop - air_h, ytop - air_h], color=WATER_EDGE, lw=1.4, z=7)
        label(ax, cx, ytop - air_h / 2 - 0.02, "воздух", fs=8.5, color=GREY, zorder=8)
        ya = ytop - th / 2
        arrow(ax, (cx + 1.9, ya), (cx + 1.9, ya + (1.6 if not squeezed else 0.9)), color=C_A, lw=2.2)
        arrow(ax, (cx + 1.9, ya), (cx + 1.9, ya - 1.25), color=C_F, lw=2.2)
        label(ax, cx + 2.15, ya + (1.6 if not squeezed else 0.9) - 0.2, r"$F_А$", fs=11.5, color=C_A, ha="left")
        label(ax, cx + 2.15, ya - 1.25 + 0.25, r"$F_т$", fs=11.5, color=C_F, ha="left")
        if squeezed:
            arrow(ax, (cx - 5.4, 5.0), (cx - 3.15, 5.0), color=C_F, lw=3.0, scale=16)
            arrow(ax, (cx + 5.4, 5.0), (cx + 3.15, 5.0), color=C_F, lw=3.0, scale=16)
            label(ax, cx, 11.3, "Сжата: воздуха меньше,\n$F_А < F_т$, пробирка тонет", fs=10.5)
        else:
            label(ax, cx, 11.3, "Свободна: $F_А > F_т$,\nпробирка всплывает", fs=10.5)
    save(fig, "float-cartesian-diver.png")


# ------------------------------------------------------------- 10. plank and floe scheme


def plank_floe():
    fig, axes = blank(12.5, 5.0, (0, 30), (0, 11.5))
    ax = axes[0]
    specs = [("Сосновая доска", 400, 8.0, 4.8, WOOD, WOOD_EDGE, 8.0), ("Льдина", 900, 40.0, 4.0, ICE, ICE_EDGE, 8.0)]
    for i, (name, rho, H, h, fc, ec, hs) in enumerate(specs):
        cx = 7.5 + i * 15
        surf = 6.0
        liquid(ax, cx - 6.8, cx + 6.8, 0, surf)
        vessel(ax, cx - 6.8, cx + 6.8, 0, 9.2)
        hh = 3.6  # drawn height of the body
        frac = 1 - h / H
        yb = surf - frac * hh
        rect(ax, cx - 3.5, yb, 7.0, hh, fc=fc, ec=ec, lw=2, z=4)
        rect(ax, cx - 3.5, yb, 7.0, surf - yb, fc="none", ec=WATER_EDGE, lw=0, hatch="///", z=5)
        dim_v(ax, cx + 4.2, yb, yb + hh, rf"$H={H:g}$ см", side="right")
        arrow(ax, (cx - 4.2, surf), (cx - 4.2, yb + hh), color=C_F, lw=1.6, style="<|-|>", scale=9)
        htxt = num(h, None, math=True)
        label(ax, cx - 4.4, yb + hh + 0.7, rf"$h={htxt}$ см", fs=10.5, color=C_F, ha="right")
        label(ax, cx, 10.4, f"{name}, " + rf"$\rho_т={rho}$", fs=11.5)
    save(fig, "float-plank-floe.png")


# ------------------------------------------------------------- 11. freeboard vs thickness


def freeboard_graph():
    fig, ax = plt.subplots(figsize=(8, 4.8))
    H = np.linspace(0, 50, 100)
    for name, r, col in [("пенопласт, 20", 20, GREY), ("сосна, 400", 400, WOOD_EDGE), ("лёд, 900", 900, ICE_EDGE)]:
        ax.plot(H, H * (1 - r / RHO_W), color=col, lw=2.6, label=f"{name} кг/м$^3$")
    ax.plot([8], [4.8], "o", color=INK, ms=8, zorder=5)
    ax.annotate("доска: $H=8$ см,\n$h=4{,}8$ см", (8, 4.8), (11, 14), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    ax.plot([40], [4], "o", color=INK, ms=8, zorder=5)
    ax.annotate("льдина: $h=4$ см,\n$H=40$ см", (40, 4), (33, 13), fontsize=10, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 52)
    style_axes(ax, r"Толщина тела $H$, см", r"Высота над водой $h$, см", "Плоское тело в воде")
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    fig.tight_layout()
    save(fig, "float-freeboard-graph.png")


# ------------------------------------------------------------- 12. cylinder on two liquids


def two_liquids():
    fig = plt.figure(figsize=(12.5, 4.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.15])
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.set_aspect("equal")
    ax.axis("off")
    liquid(ax, 0.5, 13.5, 0, 4.5, fc=WATER, ec=WATER_EDGE)
    liquid(ax, 0.5, 13.5, 4.5, 9.0, fc=OIL, ec=OIL_EDGE)
    line(ax, [0.5, 13.5], [4.5, 4.5], color=WATER_EDGE, lw=2, z=3)
    vessel(ax, 0.5, 13.5, 0, 10.4)
    yb = 4.5 - (2 / 3) * 3.6
    rect(ax, 4.5, yb, 5.0, 3.6, fc=PLASTICINE, ec=PLASTICINE_EDGE, lw=2, z=5)
    line(ax, [4.5, 9.5], [4.5, 4.5], color=INK, lw=1.2, z=6, ls=":")
    dim_v(ax, 10.2, yb, yb + 3.6, r"$V$", side="right")
    dim_v(ax, 3.8, yb, 4.5, r"$xV$", side="left", color=C_A)
    # Scale 0.00268 per unit: F_т = 933 -> 2.5, F_А1 = 800 / 3 = 267 -> 0.71, F_А2 = 1000 * 2/3 = 667 -> 1.79 (F_А1 + F_А2 = F_т)
    arrow(ax, (7, 5.0), (7, 5.71), color=C_A, lw=2.2)
    arrow(ax, (7, 4.0), (7, 0.9 + 0.6), color=C_F, lw=2.2)
    label(ax, 7.4, 6.1, r"$F_{А1}$", fs=11.5, color=C_A, ha="left")
    label(ax, 7.4, 1.6, r"$F_т$", fs=11.5, color=C_F, ha="left")
    arrow(ax, (8.4, 3.6), (8.4, 5.39), color=C_A, lw=2.2)
    label(ax, 8.7, 5.1, r"$F_{А2}$", fs=11.5, color=C_A, ha="left")
    label(ax, 1.2, 7.0, r"$\rho_1=800$", fs=11, ha="left")
    label(ax, 1.2, 2.2, r"$\rho_2=1000$", fs=11, ha="left")
    label(ax, 7, 11.2, "Цилиндр на границе двух жидкостей", fs=11.5)
    ax2 = fig.add_subplot(gs[1])
    x = np.linspace(0, 1, 100)
    ax2.plot(x, 800 * (1 - x) + 1000 * x, color=C_A, lw=2.6)
    ax2.plot([2 / 3], [800 * (1 / 3) + 1000 * (2 / 3)], "o", color=C_F, ms=9, zorder=5)
    ax2.plot([2 / 3, 2 / 3], [780, 933.3], color=C_F, lw=1, ls=":")
    ax2.plot([0, 2 / 3], [933.3, 933.3], color=C_F, lw=1, ls=":")
    ax2.annotate(r"$x=2/3$, $\rho\approx 933$", (2 / 3, 933.3), (0.12, 960), fontsize=10.5, color=C_F,
                 arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax2.text(0.42, 800, "x = 0: весь в верхней жидкости", fontsize=9.5, color=GREY, va="bottom")
    ax2.text(0.55, 1012, "x = 1: весь в нижней жидкости", fontsize=9.5, color=GREY, va="top", ha="left")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(780, 1020)
    style_axes(ax2, r"Доля объёма в нижней жидкости $x$", r"Плотность цилиндра $\rho$, кг/м$^3$", "Плотность цилиндра по глубине посадки")
    fig.tight_layout()
    save(fig, "float-two-liquids.png")


def main():
    three_cases()
    fraction_line()
    bodies_in_water()
    three_liquids()
    fraction_liquids()
    forces_vs_fraction()
    iceberg()
    areometer()
    diver()
    plank_floe()
    freeboard_graph()
    two_liquids()


if __name__ == "__main__":
    main()
