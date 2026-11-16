"""Figures for the note "Плавание судов. Воздухоплавание", balloon part (lesson 69).

Run: python3 balloons.py
PNG files go to content/07. Закон Архимеда и плавание/00. Вложения/, prefix balloon-.
Curves marked "не из лекции" are reference models, not from the lesson.
"""
from floating_common import *  # noqa: F401,F403
from theme import num
from matplotlib.patches import Circle

G = 9.8
RHO_AIR = 1.29
RHO_HE = 0.18
RHO_H2 = 0.09
M_SHELL = 150.0


# ------------------------------------------------------------- 1. forces on a tethered balloon


def tethered():
    fig, axes = blank(7.2, 6.6, (0, 14), (-1, 14))
    ax = axes[0]
    ax.add_patch(Circle((7, 8.0), 4.0, fc=tint(RED, 0.9), ec=INK, lw=2.2, zorder=3))
    label(ax, 3.4, 11.5, r"$\rho_в$", fs=13, color=GREY)
    label(ax, 5.2, 8.6, r"$V,\ \rho_г$", fs=12.5)
    line(ax, [7, 7], [4.0, 0.6], color=INK, lw=2, z=4)
    line(ax, [5.6, 8.4], [0.6, 0.6], color=INK, lw=2.4, z=4)
    for x in np.arange(5.7, 8.4, 0.35):
        line(ax, [x, x - 0.2], [0.6, 0.2], color=GREY, lw=1)
    # forces
    arrow(ax, (7, 12.0), (7, 13.7), color=C_A, lw=2.6)
    label(ax, 7.3, 13.4, r"$F_А$", fs=12.5, color=C_A, ha="left")
    # Equilibrium: F_А (1.7) = F_т.г (0.5) + F_т.о (0.6) + F_под (0.6)
    arrow(ax, (7.0, 8.0), (7.0, 7.5), color=C_F, lw=2.6)
    label(ax, 7.3, 7.6, r"$F_{т.г}$", fs=12, color=C_F, ha="left")
    arrow(ax, (6.3, 8.0), (6.3, 7.4), color=C_F, lw=2.6)
    label(ax, 5.95, 7.2, r"$F_{т.о}$", fs=12, color=C_F, ha="right")
    arrow(ax, (7.6, 3.9), (7.6, 3.3), color=C_F, lw=2.6)
    label(ax, 7.9, 3.4,r"$F_{под}$", fs=12, color=C_F, ha="left")
    label(ax, 7, -0.5, "Шар на привязи: сила натяжения нити и есть подъёмная сила", fs=10, color=GREY)
    save(fig, "balloon-forces-tethered.png")


# ------------------------------------------------------------- 2. lift per cubic metre of gas


def gas_bars():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    hot = RHO_AIR / 1.3035
    names = ["водород", "гелий", "горячий воздух"]
    rho = [RHO_H2, RHO_HE, hot]
    lift = [(RHO_AIR - r) * G for r in rho]
    cols = [GREEN, C_A, HOT]
    bars = ax.bar(names, lift, color=cols, width=0.55, zorder=3)
    for b, r, l in zip(bars, rho, lift):
        ax.text(b.get_x() + b.get_width() / 2, l + 0.25, f"{num(l, 1)} Н/м$^3$", ha="center", fontsize=10.5)
        ax.text(b.get_x() + b.get_width() / 2, l / 2, rf"$\rho_г={num(r, 2)}$", ha="center", color=PAPER, fontsize=10.5, zorder=5)
    ax.set_ylim(0, 14)
    style_axes(ax, "Газ в оболочке", r"$(\rho_в-\rho_г)\,g$, Н на 1 м$^3$", "Подъёмная сила на кубометр газа")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "balloon-gas-lift.png")


# ------------------------------------------------------------- 3. lift vs volume for three gases


def lift_vs_volume():
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    V = np.linspace(0, 1000, 300)
    hot = RHO_AIR / 1.3035
    for name, r, col in [("водород", RHO_H2, GREEN), ("гелий", RHO_HE, C_A), ("горячий воздух", hot, HOT)]:
        F = G * ((RHO_AIR - r) * V - M_SHELL) / 1000
        ax.plot(V, F, color=col, lw=2.6, label=name)
        v0 = M_SHELL / (RHO_AIR - r)
        ax.plot([v0], [0], "o", color=col, ms=7, zorder=5)
    ax.axhline(0, color=INK, lw=1.4)
    ax.annotate("горячий воздух отрывается\nот земли только при $V=500$ м$^3$", (500, 0), (560, -3.0), fontsize=10, color=HOT,
                arrowprops=dict(arrowstyle="-", color=HOT, lw=0.9))
    ax.set_xlim(0, 1000)
    ax.set_ylim(-4.2, 12)
    style_axes(ax, r"Объём шара $V$, м$^3$", r"Подъёмная сила $F_{под}$, кН", "Подъёмная сила растёт с объёмом")
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)
    fig.tight_layout()
    save(fig, "balloon-lift-vs-volume.png")


# ------------------------------------------------------------- 4. lift vs height


def lift_vs_height():
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    H0 = 8.4  # km, scale height, isothermal model, not from the lesson
    V0 = 500.0
    k = 1 - RHO_HE / RHO_AIR
    h = np.linspace(0, 25, 300)
    rho = RHO_AIR * np.exp(-h / H0)
    F_fixed = G * (k * rho * V0 - M_SHELL) / 1000
    F_expand = np.full_like(h, G * (k * RHO_AIR * V0 - M_SHELL) / 1000)
    ax.plot(h, F_fixed, color=C_A, lw=2.6, label="объём шара постоянный")
    ax.plot(h, F_expand, color=GREEN, lw=2.6, ls="--", label=r"объём растёт как $1/\rho_в$ (стратостат)")
    ax.axhline(0, color=INK, lw=1.4)
    h0 = H0 * np.log(k * RHO_AIR * V0 / M_SHELL)
    ax.plot([h0], [0], "o", color=C_F, ms=8, zorder=5)
    ax.annotate(f"потолок: {h0:.0f} км,\nдальше шар не поднимется", (h0, 0), (h0 + 1.5, 1.8), fontsize=10, color=C_F,
                arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax.set_xlim(0, 25)
    ax.set_ylim(-4, 6.6)
    style_axes(ax, "Высота, км", r"Подъёмная сила $F_{под}$, кН", "Подъёмная сила на высоте (модель, не из лекции)")
    ax.legend(loc="upper right", frameon=False, fontsize=10)
    fig.tight_layout()
    save(fig, "balloon-lift-vs-height.png")


# ------------------------------------------------------------- 5. problem 21.26


def hot_air_ratio():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    ax = axes[0]
    m = np.linspace(0, 600, 300)
    rv = RHO_AIR * 500
    x = rv / (rv - m)
    ax.plot(m, x, color=C_A, lw=2.6)
    ax.plot([150], [rv / (rv - 150)], "o", color=C_F, ms=9, zorder=5)
    ax.annotate("$m=150$ кг:\n$x\\approx1{,}3$", (150, rv / (rv - 150)), (215, 2.4), fontsize=10.5, color=C_F,
                arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax.axvline(rv, color=GREY, ls="--", lw=1.2)
    # Placed left of the dashed line but right of where the curve is still low, so the curve does not cross it
    ax.text(240, 9.6, r"$m\geq\rho_в V=645$ кг:" + "\nне взлететь даже\nс пустотой внутри", fontsize=9.5, color=GREY, ha="left", va="top")
    ax.set_xlim(0, 700)
    ax.set_ylim(1, 10)
    style_axes(ax, "Масса оболочки и груза $m$, кг", r"Отношение $x=\rho_в/\rho_г$", "Шар объёмом 500 м$^3$")
    ax = axes[1]
    V = np.linspace(120, 1000, 300)
    xv = RHO_AIR * V / (RHO_AIR * V - 150)
    ax.plot(V, xv, color=C_A, lw=2.6)
    ax.plot([500], [RHO_AIR * 500 / (RHO_AIR * 500 - 150)], "o", color=C_F, ms=9, zorder=5)
    ax.annotate("$V=500$ м$^3$:\n$x\\approx1{,}3$", (500, RHO_AIR * 500 / (RHO_AIR * 500 - 150)), (620, 2.6), fontsize=10.5, color=C_F,
                arrowprops=dict(arrowstyle="-", color=C_F, lw=0.9))
    ax.set_xlim(120, 1000)
    ax.set_ylim(1, 10)
    style_axes(ax, r"Объём шара $V$, м$^3$", r"Отношение $x=\rho_в/\rho_г$", "Оболочка и груз 150 кг")
    fig.tight_layout()
    save(fig, "balloon-hot-air-ratio.png")


# ------------------------------------------------------------- 6. types of aircraft lighter than air


def types():
    fig, axes = blank(15, 4.8, (0, 60), (-1, 15))
    ax = axes[0]
    # 1 aerostat (probe)
    cx = 7.5
    ax.add_patch(Circle((cx, 8.5), 2.4, fc=tint(SKY, 0.85), ec=INK, lw=2, zorder=3))
    line(ax, [cx, cx], [6.1, 4.2], color=INK, lw=1.6)
    rect(ax, cx - 0.6, 3.2, 1.2, 1.0, fc=LIGHT, ec=INK, lw=1.6)
    label(ax, cx, 13.9, "Аэростат", fs=12)
    label(ax, cx, 1.3, "шар-зонд с гелием\nи радиопередатчиком", fs=9.5, color=INK)
    # 2 stratostat
    cx = 22.5
    ax.add_patch(Circle((cx, 8.6), 4.2, fc=tint(SKY, 0.85), ec=INK, lw=2, zorder=3))
    line(ax, [cx, cx], [4.4, 3.0], color=INK, lw=1.6)
    rect(ax, cx - 0.7, 1.8, 1.4, 1.2, fc=LIGHT, ec=INK, lw=1.6)
    label(ax, cx, 13.9, "Стратостат", fs=12)
    label(ax, cx, 0.2, "очень большой объём:\nвоздух наверху разрежен", fs=9.5, color=INK)
    # 3 dirigible
    cx = 37.5
    ax.add_patch(Ellipse((cx, 8.4), 12.0, 4.0, fc=tint(SKY, 0.85), ec=INK, lw=2, zorder=3))
    rect(ax, cx - 1.5, 5.7, 3.0, 0.9, fc=LIGHT, ec=INK, lw=1.6)  # gondola touches the envelope (its bottom is at 6.4-6.5)
    line(ax, [cx + 6.0, cx + 6.7], [8.4, 8.4], color=INK, lw=2)
    line(ax, [cx + 6.7, cx + 6.7], [7.6, 9.2], color=INK, lw=3)
    line(ax, [cx - 6.0, cx - 7.0], [8.4, 10.0], color=INK, lw=2)
    line(ax, [cx - 6.0, cx - 7.0], [8.4, 6.8], color=INK, lw=2)
    label(ax, cx, 13.9, "Дирижабль", fs=12)
    label(ax, cx, 2.6, "воздушный винт:\nплывёт против ветра", fs=9.5, color=INK)
    # 4 montgolfier
    cx = 52.5
    ax.add_patch(Ellipse((cx, 9.0), 6.8, 6.4, fc=tint(WARM, 0.75), ec=INK, lw=2, zorder=3))
    ax.add_patch(Polygon([(cx - 1.83, 6.3), (cx + 1.83, 6.3), (cx + 0.9, 4.6), (cx - 0.9, 4.6)], closed=True, fc=tint(WARM, 0.75), ec=INK, lw=2, zorder=3))
    ax.add_patch(Polygon([(cx - 0.3, 3.6), (cx, 4.3), (cx + 0.3, 3.6)], closed=True, fc=WARM, ec=C_F, lw=1.4, zorder=4))
    rect(ax, cx - 0.8, 1.9, 1.6, 1.3, fc=LIGHT, ec=INK, lw=1.6)
    line(ax, [cx - 0.9, cx - 0.8], [4.6, 3.2], color=INK, lw=1.6)  # ropes from the skirt to the basket
    line(ax, [cx + 0.9, cx + 0.8], [4.6, 3.2], color=INK, lw=1.6)
    label(ax, cx, 13.9, "Монгольфьер", fs=12)
    label(ax, cx, 0.2, "нагретый воздух\nи газовая горелка", fs=9.5, color=INK)
    save(fig, "balloon-types.png")


def main():
    tethered()
    gas_bars()
    lift_vs_volume()
    lift_vs_height()
    hot_air_ratio()
    types()


if __name__ == "__main__":
    main()
