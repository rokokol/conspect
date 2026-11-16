"""Figures for the note "Уравнение теплового баланса" (section f10, lessons 112, 113, 127, 128, 129).

Run: nix shell nixpkgs#python3Packages.matplotlib -c python3 heat_balance.py
PNG files go to content/10. Тепловые явления/00. Вложения/ (prefix balance-)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "10. Тепловые явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)

from theme import ACCENT, ASH, BLUE, GREEN, INK, LIGHT, METAL, MUTED, PAPER, RED, SKY, num, saver, tint

GRID = ASH
GREY = MUTED  # guides and auxiliary lines
NOTE = tint(INK, 0.4)  # small notes and secondary text
HOT = RED
COLD = BLUE
GOLD = ACCENT  # the common temperature theta and what is tied to it: a highlighted value
WATER = tint(SKY, 0.6)  # water as a body
WATER_FILL = tint(SKY, 0.8)

# reference data used in the lessons, kJ / (kg * degC) and kJ / kg
C_W = 4.2
LAM = 330.0
L_100 = 2300.0
L_0 = 2450.0


save = saver(OUT)


def clean_axes(ax):
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)


def arrow(ax, p, q, color=INK, lw=1.6, style="-|>", ms=12, **kw):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=ms, color=color, linewidth=lw, **kw
        )
    )


# ---------------------------------------------------------------- theory


def isolated_system():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    titles = [
        "Порознь: $t_1 > t_2$",
        "Контакт: идёт теплообмен",
        "Равновесие: $\\theta$ у обоих",
    ]
    for ax, title in zip(axs, titles):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis("off")
        ax.set_title(title, color=INK)
        # insulation contour
        ax.add_patch(
            Rectangle(
                (0.4, 0.5), 9.2, 4.2, fill=False, ls=(0, (4, 3)), ec=GREY, lw=1.6
            )
        )
        ax.text(5, 5.15, "теплоизоляция", ha="center", color=NOTE, fontsize=10)
    # stage 1
    ax = axs[0]
    for x0, col, lab, tt in ((1.3, HOT, "1", "$t_1$"), (6.0, COLD, "2", "$t_2$")):
        ax.add_patch(Rectangle((x0, 1.5), 2.7, 2.0, fc=col, alpha=0.30, ec=col, lw=2))
        ax.text(x0 + 1.35, 2.5, f"{lab}   {tt}", ha="center", va="center", fontsize=13)
    # stage 2
    ax = axs[1]
    ax.add_patch(Rectangle((2.0, 1.5), 3.0, 2.0, fc=HOT, alpha=0.30, ec=HOT, lw=2))
    ax.add_patch(Rectangle((5.0, 1.5), 3.0, 2.0, fc=COLD, alpha=0.30, ec=COLD, lw=2))
    ax.text(3.5, 2.5, "1  $t_1\\downarrow$", ha="center", va="center", fontsize=13)
    ax.text(6.5, 2.5, "2  $t_2\\uparrow$", ha="center", va="center", fontsize=13)
    arrow(ax, (4.0, 4.0), (6.2, 4.0), color=INK)
    ax.text(5.1, 4.22, "$Q$", ha="center", fontsize=12)
    # stage 3
    ax = axs[2]
    ax.add_patch(Rectangle((2.0, 1.5), 3.0, 2.0, fc=GOLD, alpha=0.35, ec=GOLD, lw=2))
    ax.add_patch(Rectangle((5.0, 1.5), 3.0, 2.0, fc=GOLD, alpha=0.35, ec=GOLD, lw=2))
    ax.text(3.5, 2.5, "1  $\\theta$", ha="center", va="center", fontsize=13)
    ax.text(6.5, 2.5, "2  $\\theta$", ha="center", va="center", fontsize=13)
    fig.suptitle("Теплоизолированная система из двух тел", color=INK, y=1.03)
    save(fig, "balance-isolated-system.png")


def exp_curves(ax, t1, t2, theta, tau_c, tmax=6.0):
    tau = np.linspace(0, tmax, 300)
    ax.plot(tau, theta + (t1 - theta) * np.exp(-tau / tau_c), color=HOT, lw=2.4)
    ax.plot(tau, theta - (theta - t2) * np.exp(-tau / tau_c), color=COLD, lw=2.4)
    ax.axhline(theta, color=GOLD, lw=1.4, ls="--")
    ax.set_xlabel("время $\\tau$ (условная шкала)")
    ax.set_ylabel("температура $t$, $^\\circ$C")
    ax.set_xlim(0, tmax)
    clean_axes(ax)


def equilibrium_curves():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    # equal heat capacities
    t1, t2 = 90.0, 10.0
    th = (t1 + t2) / 2
    ax = axs[0]
    exp_curves(ax, t1, t2, th, 1.2)
    ax.set_title("Одинаковые теплоёмкости $C_1 = C_2$")
    ax.text(0.15, t1 + 2, "тело 1", color=HOT)
    ax.text(0.15, t2 - 8, "тело 2", color=COLD)
    ax.text(5.9, th + 2, "$\\theta$", color=GOLD, ha="right", fontsize=13)
    # The arrows run exactly from the initial temperature to theta; they stand left of the curves (x < 0), so the labels do not lie on a curve
    ax.set_xlim(-1.9, 6.0)
    ax.set_xticks(range(0, 7))  # the left margin only holds the labels: no negative times
    arrow(ax, (-0.3, t1), (-0.3, th), color=HOT, lw=1.2)
    arrow(ax, (-0.3, t2), (-0.3, th), color=COLD, lw=1.2)
    ax.text(-0.45, (t1 + th) / 2, "$\\Delta t_1 = %d$" % (t1 - th), color=HOT, ha="right", va="center")
    ax.text(-0.45, (t2 + th) / 2, "$\\Delta t_2 = %d$" % (th - t2), color=COLD, ha="right", va="center")
    ax.set_ylim(0, 100)
    # C1 = 3 C2
    ax = axs[1]
    c1, c2 = 3.0, 1.0
    th2 = (c1 * t1 + c2 * t2) / (c1 + c2)
    exp_curves(ax, t1, t2, th2, 1.2)
    ax.set_title("Теплоёмкость тела 1 втрое больше: $C_1 = 3C_2$")
    ax.text(5.9, th2 + 2, "$\\theta$", color=GOLD, ha="right", fontsize=13)
    ax.set_xlim(-1.9, 6.0)
    ax.set_xticks(range(0, 7))  # the left margin only holds the labels: no negative times
    arrow(ax, (-0.3, t1), (-0.3, th2), color=HOT, lw=1.2)
    arrow(ax, (-0.3, t2), (-0.3, th2), color=COLD, lw=1.2)
    ax.text(-0.45, (t1 + th2) / 2, "$\\Delta t_1 = %d$" % (t1 - th2), color=HOT, ha="right", va="center")
    ax.text(-0.45, (t2 + th2) / 2, "$\\Delta t_2 = %d$" % (th2 - t2), color=COLD, ha="right", va="center")
    ax.set_ylabel("")
    fig.suptitle(
        "Кривые остывания и нагревания сходятся к равновесной температуре",
        color=INK,
        y=1.02,
    )
    save(fig, "balance-equilibrium-curves.png")


def energy_bars():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    ax = axs[0]
    ax.bar([0, 1], [-100, 100], color=[HOT, COLD], width=0.55)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["тело 1\nотдаёт", "тело 2\nполучает"])
    ax.set_yticks([-100, 0, 100])
    # Q_i is the received heat: the bar below zero is Q_1 itself, equal to -Q_given
    ax.set_yticklabels(["$Q_1 = -Q_\\mathrm{отд}$", "0", "$Q_2 = Q_\\mathrm{пол}$"])
    ax.text(0, -55, "$Q_\\mathrm{отд}$", ha="center", color=PAPER, fontsize=13)
    ax.text(1, 45, "$Q_\\mathrm{пол}$", ha="center", color=PAPER, fontsize=13)
    ax.set_title("Два тела: $Q_\\mathrm{отд} = Q_\\mathrm{пол}$")
    ax.set_ylim(-130, 130)
    clean_axes(ax)
    # signed, three bodies
    ax = axs[1]
    q = [-90, 40, 50]
    cols = [HOT, COLD, COLD]
    labels = ["$Q_1$", "$Q_2$", "$Q_3$"]
    ax.bar(range(3), q, color=cols, width=0.55)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["тело 1", "тело 2", "тело 3"])
    for i, v in enumerate(q):
        ax.text(i, v + (6 if v > 0 else -12), labels[i], ha="center", fontsize=12)
    ax.text(1, 100, "$Q_1 + Q_2 + Q_3 = -90 + 40 + 50 = 0$", ha="center", fontsize=12, color=INK)
    ax.set_xlim(-0.6, 2.6)
    ax.set_title("Три тела: $\\sum Q_i = 0$")
    ax.set_ylim(-130, 130)
    ax.set_yticks([])
    clean_axes(ax)
    save(fig, "balance-energy-bars.png")


def sign_rule():
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    theta = 60.0
    t0 = np.linspace(0, 120, 200)
    for cm, col, lab in ((2.0, COLD, "$cm = 2$"), (0.8, METAL, "$cm = 0{,}8$")):
        ax.plot(t0, cm * (theta - t0), color=col, lw=2.4, label=lab)
    ax.axhline(0, color=INK, lw=1)
    ax.axvline(theta, color=GOLD, lw=1.4, ls="--")
    ax.fill_between(t0, 0, 130, where=t0 < theta, color=COLD, alpha=0.08)
    ax.fill_between(t0, -130, 0, where=t0 > theta, color=HOT, alpha=0.08)
    ax.text(15, 105, "$Q > 0$: тело получило", color=COLD)
    ax.text(70, -110, "$Q < 0$: тело отдало", color=HOT)
    ax.set_xlabel("начальная температура тела $t_0$, $^\\circ$C")
    ax.set_ylabel("$Q = cm(\\theta - t_0)$, условные единицы")
    ax.text(theta + 1.5, 100, "$t_0 = \\theta$: $Q = 0$", color=GOLD)
    ax.set_xlim(0, 120)
    ax.set_ylim(-130, 130)
    ax.legend(frameon=False, loc="lower left")
    ax.set_title("Знак $Q$ следует из разности $\\theta - t_0$")
    clean_axes(ax)
    save(fig, "balance-sign-rule.png")


def mixture_share():
    t1, t2 = 10.0, 60.0
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    ax = axs[0]
    x = np.linspace(0, 1, 100)
    ax.plot(x, t1 + (t2 - t1) * x, color=GOLD, lw=2.6)
    ax.set_xlabel("доля горячей порции $m_2/(m_1 + m_2)$")
    ax.set_ylabel("$\\theta$, $^\\circ$C")
    ax.set_title("Зависимость от доли: прямая")
    ax.scatter([0.6], [40], color=INK, zorder=5)
    ax.annotate("ванна: 120 л горячей\nиз 200 л", (0.6, 40), (0.05, 47), color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.text(0.02, t1 - 6, "$t_1$: только холодная", color=COLD)
    ax.text(0.98, t2 + 3, "$t_2$: только горячая", color=HOT, ha="right")
    ax.set_ylim(0, 70)
    clean_axes(ax)
    ax = axs[1]
    r = np.linspace(0, 8, 300)
    ax.plot(r, (t1 + t2 * r) / (1 + r), color=GOLD, lw=2.6)
    ax.axhline(t2, color=HOT, lw=1.2, ls=":")
    ax.axhline(t1, color=COLD, lw=1.2, ls=":")
    ax.scatter([1.5], [40], color=INK, zorder=5)
    ax.annotate("120 кг : 80 кг", (1.5, 40), (2.6, 26), color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlabel("отношение масс $m_2/m_1$")
    ax.set_ylabel("$\\theta$, $^\\circ$C")
    ax.set_title("Зависимость от отношения масс: горячей всё больше")
    ax.text(7.9, t2 - 4, "$\\theta \\to t_2$", color=HOT, ha="right")
    ax.set_ylim(0, 70)
    ax.set_xlim(0, 8)
    clean_axes(ax)
    fig.suptitle(
        "Смесь двух порций одной жидкости, $t_1 = 10\\ ^\\circ$C и $t_2 = 60\\ ^\\circ$C",
        color=INK,
        y=1.02,
    )
    save(fig, "balance-mixture-theta-share.png")


# --------------------------------------------------------------- problems


def tau_pair(ax, t_hot, t_cold, theta, tau_c=1.1, tmax=6.0, names=("", "")):
    exp_curves(ax, t_hot, t_cold, theta, tau_c, tmax)
    # At the right edge the curves have merged with theta, so the label touches no curve
    ax.text(5.9, theta + 0.04 * (t_hot - t_cold), f"$\\theta \\approx {theta:.0f}\\ ^\\circ$C",
            color=GOLD, ha="right", va="bottom", fontsize=12)


def bars_pair(ax, qs, labels, colors, unit="кДж"):
    ax.bar(range(len(qs)), qs, color=colors, width=0.55)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks(range(len(qs)))
    ax.set_xticklabels(labels)
    ymax = max(abs(v) for v in qs)
    for i, v in enumerate(qs):
        s = num(v, "+.1f")
        s = s[:-2] if s.endswith(",0") else s
        ax.text(i, v + (0.06 if v > 0 else -0.14) * ymax, s.replace("-", "−") + f" {unit}",
                ha="center", fontsize=11)
    ax.set_ylim(-1.35 * ymax, 1.35 * ymax)
    ax.set_ylabel("$Q$, " + unit)
    clean_axes(ax)


def fmt(x, nd=1):
    return num(x, f".{nd}f")


def task_add_boiling_water():
    # 3.3: 0.5 kg water 20 -> 80; boiling water 1.5 kg 100 -> 80
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    tau_pair(axs[0], 100, 20, 80)
    axs[0].text(0.15, 102, "кипяток $1{,}5$ кг", color=HOT)
    axs[0].text(0.15, 8, "холодная вода $0{,}5$ кг", color=COLD)
    axs[0].set_ylim(0, 115)
    axs[0].set_title("Температуры тел")
    q_cold = C_W * 0.5 * 60
    q_hot = C_W * 1.5 * (80 - 100)
    ax = axs[1]
    bars_pair(ax, [q_cold, q_hot], ["холодная вода", "кипяток"], [COLD, HOT])
    ax.set_title("Количества теплоты: $Q_\\mathrm{в} + Q_\\mathrm{к} = 0$")
    save(fig, "balance-task-boiling-water-added.png")


def task_kettle():
    # 3.4
    m_k, c_s, t_k = 0.4, 0.5, 20.0
    m_w, c_w, t_w = 0.1, 4.2, 100.0
    th = (m_k * c_s * t_k + m_w * c_w * t_w) / (m_k * c_s + m_w * c_w)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    tau_pair(axs[0], t_w, t_k, th)
    axs[0].text(0.15, 102, "кипяток $100$ г", color=HOT)
    axs[0].text(0.15, 8, "стальной чайник $400$ г", color=COLD)
    axs[0].set_ylim(0, 115)
    axs[0].set_title("Температуры тел")
    qk = m_k * c_s * (th - t_k)
    qw = m_w * c_w * (th - t_w)
    bars_pair(axs[1], [qk, qw], ["чайник", "вода"], [COLD, HOT])
    axs[1].set_title("Количества теплоты: $Q_\\mathrm{ч} + Q_\\mathrm{в} = 0$")
    save(fig, "balance-task-kettle.png")


def task_ball_liquid():
    # Gendenstein 4.38: c_liquid / c_ball = 9; illustrated with water (4.2) and c_ball = 4.2 / 9
    c_l = C_W
    c_b = C_W / 9
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    tau_pair(axs[0], 75, 25, 30, tau_c=0.9)
    axs[0].text(0.15, 78, "шар $100$ г", color=HOT)
    axs[0].text(0.15, 14, "жидкость $100$ г", color=COLD)
    axs[0].set_ylim(0, 90)
    axs[0].set_title("Шар остывает на $45\\ ^\\circ$C, жидкость греется на $5\\ ^\\circ$C")
    q_l = c_l * 0.1 * 5
    q_b = c_b * 0.1 * (30 - 75)
    bars_pair(axs[1], [q_l, q_b], ["жидкость", "шар"], [COLD, HOT])
    axs[1].set_title("Равные $Q$ при $c_ж / c_ш = 9$")
    save(fig, "balance-task-ball-liquid.png")


def task_steel_oil():
    # Kirik 2b: steel 0.3 kg 710 -> 30 ; oil 3 kg 10 -> 30
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    tau_pair(axs[0], 710, 10, 30, tau_c=0.9)
    axs[0].text(0.15, 690, "сталь $0{,}3$ кг", color=HOT)
    axs[0].text(2.6, 140, "масло $3$ кг", color=COLD)
    axs[0].set_ylim(0, 760)
    axs[0].set_title("Деталь остывает на $680\\ ^\\circ$C, масло греется на $20\\ ^\\circ$C")
    q_oil = 1.7 * 3 * 20
    q_st = 0.5 * 0.3 * (30 - 710)
    bars_pair(axs[1], [q_oil, q_st], ["масло", "деталь"], [COLD, HOT])
    axs[1].set_title("Теплоёмкость масла в 34 раза больше")
    save(fig, "balance-task-steel-oil.png")


def task_bath_lever():
    fig, ax = plt.subplots(figsize=(9, 3.3))
    t_x, t_g, th = 10.0, 60.0, 40.0
    ax.set_xlim(0, 70)
    ax.set_ylim(-3.5, 4.5)
    ax.axis("off")
    ax.plot([5, 65], [0, 0], color=INK, lw=3, solid_capstyle="round")
    # ticks
    for t in (t_x, th, t_g):
        ax.plot([t, t], [-0.25, 0.25], color=INK, lw=2)
    ax.add_patch(Polygon([[th, 0], [th - 2.2, -1.6], [th + 2.2, -1.6]], fc=GOLD, ec=INK))
    ax.text(th, -2.5, "$\\theta = 40\\ ^\\circ$C", ha="center", fontsize=12, color=INK)
    ax.text(t_x, -1.1, "$t_x = 10\\ ^\\circ$C", ha="center", color=COLD, fontsize=12)
    ax.text(t_g, -1.1, "$t_г = 60\\ ^\\circ$C", ha="center", color=HOT, fontsize=12)
    ax.add_patch(Rectangle((t_x - 4, 0.25), 8, 2.4, fc=COLD, alpha=0.4, ec=COLD, lw=1.6))
    ax.text(t_x, 1.45, "80 кг\nхолодной", ha="center", va="center", fontsize=11)
    ax.add_patch(Rectangle((t_g - 5, 0.25), 10, 3.2, fc=HOT, alpha=0.4, ec=HOT, lw=1.6))
    ax.text(t_g, 1.85, "120 кг\nгорячей", ha="center", va="center", fontsize=11)
    arrow(ax, (t_x, 3.9), (th, 3.9), color=COLD, style="<|-|>", lw=1.3)
    ax.text((t_x + th) / 2, 4.05, "$\\theta - t_x = 30\\ ^\\circ$C", ha="center", color=COLD)
    arrow(ax, (th, 3.9), (t_g, 3.9), color=HOT, style="<|-|>", lw=1.3)
    ax.text((th + t_g) / 2 + 3, 4.05, "$t_г - \\theta = 20\\ ^\\circ$C", ha="center", color=HOT)
    ax.text(35, -3.4, "$80 \\cdot 30 = 120 \\cdot 20 = 2400$: массы обратно пропорциональны отрезкам до $\\theta$",
            ha="center", fontsize=10.5, color=INK)
    fig.suptitle("Ванна: $\\theta$ делит отрезок $t_x \\ldots t_г$ на части $30 : 20$", color=INK, y=1.0)
    save(fig, "balance-task-bath-lever.png")


def heating_curve_axes(ax, xmax, ymin, ymax):
    ax.set_xlabel("переданная теплота $Q$, кДж")
    ax.set_ylabel("температура $t$, $^\\circ$C")
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    clean_axes(ax)


def task_ice_in_boiling_water():
    # Gelfgat 5.37
    m_w, C_k, t_w, th = 2.0, 0.6, 100.0, 20.0
    heat_out = (C_W * m_w + C_k) * (t_w - th)  # 720
    m_i = heat_out / (LAM + C_W * th)
    q_melt = LAM * m_i
    fig, ax = plt.subplots(figsize=(9, 4.4))
    q = np.linspace(0, heat_out, 200)
    ax.plot(q, t_w - q / (C_W * m_w + C_k), color=HOT, lw=2.6, label="кипяток и калориметр отдают")
    xs = [0, q_melt, heat_out]
    ys = [0, 0, th]
    ax.plot(xs, ys, color=COLD, lw=2.6, label="лёд: плавление, затем нагрев воды")
    ax.axhline(th, color=GOLD, lw=1.2, ls="--")
    ax.scatter([heat_out], [th], color=INK, zorder=5)
    ax.annotate("$\\theta = 20\\ ^\\circ$C\n$Q = 720$ кДж", (heat_out, th), (heat_out - 260, 55), color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"плато плавления\n$\\lambda m_л \\approx {q_melt:.0f}$ кДж", (q_melt / 2, 0), (60, 30), color=COLD,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"нагрев талой воды\n$c_в m_л \\theta \\approx {C_W * m_i * th:.0f}$ кДж", ((q_melt + heat_out) / 2, 10), (425, -14), color=COLD,
                arrowprops=dict(arrowstyle="-", color=GREY))
    heating_curve_axes(ax, heat_out * 1.05, -22, 108)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.set_title("Лёд в калориметре с кипятком: $m_л \\approx 1{,}7$ кг")
    save(fig, "balance-task-ice-in-boiling-water.png")


def task_ice_water_steam():
    # Kirik 5 (5 kg ice + 15 kg water, steam 100 -> 80)
    m_i, m_w, th, t_p = 5.0, 15.0, 80.0, 100.0
    q_need = LAM * m_i + C_W * (m_i + m_w) * th
    m_p = q_need / (L_100 + C_W * (t_p - th))
    q_cond = L_100 * m_p
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    # cold body: ice+water mixture
    xs = [0, LAM * m_i, q_need]
    ys = [0, 0, th]
    ax.plot(xs, ys, color=COLD, lw=2.6, label="лёд и вода: плавление, затем нагрев всей воды")
    # hot body: steam condenses at 100, then water cools 100 -> 80
    xs = [0, q_cond, q_need]
    ys = [t_p, t_p, th]
    ax.plot(xs, ys, color=HOT, lw=2.6, label="пар: конденсация, затем остывание воды")
    ax.scatter([q_need], [th], color=INK, zorder=5)
    ax.annotate(f"$\\theta = 80\\ ^\\circ$C\n$Q \\approx {q_need:.0f}$ кДж", (q_need, th), (q_need - 1900, 12), color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"плавление льда\n$\\lambda m_л = {LAM * m_i:.0f}$ кДж", (LAM * m_i / 2, 0), (300, -22), color=COLD,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"конденсация\n$L m_п \\approx {q_cond:.0f}$ кДж", (q_cond / 2, t_p), (2500, 85), color=HOT,
                arrowprops=dict(arrowstyle="-", color=GREY))
    heating_curve_axes(ax, q_need * 1.04, -32, 112)
    ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.62), fontsize=10)
    ax.set_title(f"Смесь $5$ кг льда и $15$ кг воды греют паром: $m_п \\approx$ {fmt(m_p)} кг")
    save(fig, "balance-task-ice-water-steam.png")


def task_copper_in_water():
    # Kirik 7 (high)
    m_w, t_w, m_p = 1.75, 18.0, 0.075
    c_cu, t_d, t_b = 0.4, 720.0, 100.0
    q_w = C_W * m_w * (t_b - t_w)
    q_v = L_100 * m_p
    q_tot = q_w + q_v
    m_d = q_tot / (c_cu * (t_d - t_b))
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    xs = [0, q_w, q_tot]
    ys = [t_w, t_b, t_b]
    ax.plot(xs, ys, color=COLD, lw=2.6, label="вода: нагрев до кипения, затем парообразование")
    q = np.linspace(0, q_tot, 100)
    ax.plot(q, t_d - q / (c_cu * m_d), color=HOT, lw=2.6, label="деталь остывает")
    ax.scatter([q_tot], [t_b], color=INK, zorder=5)
    ax.annotate(f"$t = 100\\ ^\\circ$C\n$Q \\approx {q_tot:.0f}$ кДж", (q_tot, t_b), (q_tot - 210, 470), color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"нагрев воды\n$\\approx {q_w:.0f}$ кДж", (q_w / 2, 60), (60, 170), color=COLD,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.annotate(f"испарение $75$ г\n$L m_п =$ {fmt(q_v)} кДж", ((q_w + q_tot) / 2, t_b), (q_w - 40, 330), color=COLD,
                arrowprops=dict(arrowstyle="-", color=GREY))
    heating_curve_axes(ax, q_tot * 1.05, 0, 760)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.set_title(f"Медная деталь в воде: $m_д \\approx$ {fmt(m_d)} кг")
    save(fig, "balance-task-copper-in-water.png")


def task_supercooled():
    # 32.51 ; per 1 kg of water
    q = C_W * 8.0
    share = q / LAM
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.0), gridspec_kw={"width_ratios": [1.3, 1, 1]})
    ax = axs[0]
    ax.plot([0, q], [-8, 0], color=COLD, lw=2.6, label="вода греется до $0\\ ^\\circ$C")
    ax.plot([0, q], [0, 0], color=HOT, lw=2.6, label="лёд кристаллизуется при $0\\ ^\\circ$C")
    ax.scatter([q], [0], color=INK, zorder=5)
    ax.set_xlabel("теплота $Q$ на $1$ кг воды, кДж")
    ax.set_ylabel("$t$, $^\\circ$C")
    ax.set_ylim(-11, 3)
    ax.set_xlim(0, q * 1.1)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    ax.set_title("Подогрев за счёт кристаллизации")
    clean_axes(ax)
    ax = axs[1]
    ax.bar([0, 1], [q, q], color=[COLD, HOT], width=0.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["греет воду\n$cm\\,\\Delta t$", "выделяет лёд\n$\\lambda m_л$"])
    ax.set_ylabel("кДж")
    for i in range(2):
        ax.text(i, q + 1, fmt(q), ha="center")
    ax.set_ylim(0, q * 1.25)
    ax.set_title("Равные $Q$")
    clean_axes(ax)
    ax = axs[2]
    ax.bar([0], [share], color=HOT, width=0.5)
    ax.bar([0], [1 - share], bottom=[share], color=WATER, width=0.5)
    ax.text(0, share / 2, f"лёд {share * 100:.0f} %", ha="center", va="center")
    ax.text(0, share + (1 - share) / 2, "вода", ha="center", va="center")
    ax.set_xticks([])
    ax.set_ylabel("доля от массы воды")
    ax.set_title("Итог")
    clean_axes(ax)
    fig.suptitle("Переохлаждённая вода, $-8\\ ^\\circ$C", color=INK, y=1.03)
    save(fig, "balance-task-supercooled.png")


def task_superheated():
    q = C_W * 8.0
    share = q / L_100
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.0), gridspec_kw={"width_ratios": [1.3, 1, 1]})
    ax = axs[0]
    ax.plot([0, q], [108, 100], color=HOT, lw=2.6, label="вода остывает до $100\\ ^\\circ$C")
    ax.plot([0, q], [100, 100], color=COLD, lw=2.6, label="часть воды испаряется")
    ax.scatter([q], [100], color=INK, zorder=5)
    ax.set_xlabel("теплота $Q$ на $1$ кг воды, кДж")
    ax.set_ylabel("$t$, $^\\circ$C")
    ax.set_ylim(97, 110)
    ax.set_xlim(0, q * 1.1)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    ax.set_title("Избыток энергии идёт в пар")
    clean_axes(ax)
    ax = axs[1]
    ax.bar([0, 1], [q, q], color=[HOT, COLD], width=0.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["отдаёт вода\n$cm\\,\\Delta t$", "берёт пар\n$L\\,m_п$"])
    ax.set_ylabel("кДж")
    for i in range(2):
        ax.text(i, q + 1, fmt(q), ha="center")
    ax.set_ylim(0, q * 1.25)
    ax.set_title("Равные $Q$")
    clean_axes(ax)
    ax = axs[2]
    ax.bar([0], [1 - share], color=WATER, width=0.5)
    ax.bar([0], [share], bottom=[1 - share], color=COLD, width=0.5, hatch="//", edgecolor=PAPER)
    ax.text(0, (1 - share) / 2, f"вода\n{fmt(100 * (1 - share))} %", ha="center", va="center")
    ax.annotate(f"пар {fmt(share * 100)} %", (0.25, 1 - share / 2), (0.55, 0.78), arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlim(-0.5, 1.4)
    ax.set_xticks([])
    ax.set_ylabel("доля от начальной массы")
    ax.set_title("Итог")
    clean_axes(ax)
    fig.suptitle("Перегретая вода, $108\\ ^\\circ$C", color=INK, y=1.03)
    save(fig, "balance-task-superheated.png")


def task_vacuum_freezing():
    l0 = L_0
    share = l0 / (l0 + LAM)
    q = LAM * share
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.0))
    ax = axs[0]
    ax.bar([0, 1], [q, q], color=[HOT, COLD], width=0.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["отдаёт замерзающая\nвода $\\lambda m_л$", "берёт испаряющаяся\nвода $L\\,m_п$"])
    ax.set_ylabel("кДж на $1$ кг воды")
    for i in range(2):
        ax.text(i, q + 5, f"${q:.0f}$", ha="center")
    ax.set_ylim(0, q * 1.2)
    ax.set_title("Равные количества теплоты при $0\\ ^\\circ$C")
    clean_axes(ax)
    ax = axs[1]
    ax.bar([0], [share], color=HOT, width=0.5)
    ax.bar([0], [1 - share], bottom=[share], color=COLD, width=0.5, hatch="//", edgecolor=PAPER)
    ax.text(0, share / 2, f"лёд {share * 100:.0f} %", ha="center", va="center", color=PAPER)
    ax.annotate(f"пар {100 * (1 - share):.0f} %", (0.25, share + (1 - share) / 2), (0.55, 0.9), arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlim(-0.5, 1.4)
    ax.set_xticks([])
    ax.set_ylabel("доля от начальной массы")
    ax.set_title("Итог")
    clean_axes(ax)
    fig.suptitle("Замораживание воды откачкой воздуха", color=INK, y=1.03)
    save(fig, "balance-task-vacuum-freezing.png")


def task_lead_float():
    rho_w, rho_i, rho_pb = 1.0, 0.9, 11.3
    m_pb, m0 = 5.0, 100.0
    m_star = m_pb * (rho_pb - rho_w) / rho_pb * rho_i / (rho_w - rho_i)
    q = LAM * (m0 - m_star) / 1000.0
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
    # scheme
    ax = axs[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    for x0, lab in ((0.3, "до нагрева"), (5.3, "льда стало меньше:\nвзвешенное состояние")):
        ax.add_patch(Rectangle((x0, 1.0), 4.4, 5.6, fc=PAPER, ec=INK, lw=2))
        ax.add_patch(Rectangle((x0 + 0.05, 1.05), 4.3, 4.0, fc=WATER, ec="none", alpha=0.6))
        ax.text(x0 + 2.2, 8.9, lab, ha="center", va="center", fontsize=10.5)
    # floating ice
    # Submerged share is 105 / (111.1 + 0.44) = 0.94, so the block stands 0.15 of its 2.6 height above the water level 5.05
    ax.add_patch(Rectangle((1.6, 2.6), 2.0, 2.6, fc=WATER_FILL, ec=COLD, lw=1.8))
    ax.add_patch(plt.Circle((2.6, 3.2), 0.3, fc=METAL, ec=INK))
    ax.text(2.6, 5.7, "лёд, 100 г", ha="center", fontsize=9)
    ax.plot([0.35, 4.65], [5.05, 5.05], color=COLD, lw=1)
    # suspended ice
    ax.add_patch(Rectangle((5.8, 2.4), 1.7, 1.9, fc=WATER_FILL, ec=COLD, lw=1.8))
    ax.add_patch(plt.Circle((6.65, 2.9), 0.3, fc=METAL, ec=INK))
    ax.text(6.65, 4.7, "$m'_л \\approx 41$ г", ha="center", fontsize=9)
    arrow(ax, (8.6, 3.35), (8.6, 5.2), color=GREEN, lw=1.8)
    ax.text(9.2, 5.0, "$F_А$", color=GREEN, ha="center", fontsize=11)
    arrow(ax, (8.6, 3.35), (8.6, 1.7), color=HOT, lw=1.8)
    ax.text(9.2, 2.0, "$F_{тяж}$", color=HOT, ha="center", fontsize=11)
    # balance plot
    ax = axs[1]
    m = np.linspace(0, 100, 200)
    mass = m + m_pb
    displaced = rho_w * (m / rho_i + m_pb / rho_pb)
    ax.plot(m, mass, color=HOT, lw=2.4, label="масса льда с дробинкой $m'_л + m_с$")
    ax.plot(m, displaced, color=GREEN, lw=2.4, label="масса вытесненной воды $\\rho_в (V_л + V_с)$")
    ax.scatter([m_star], [m_star + m_pb], color=INK, zorder=5)
    ax.axvline(m_star, color=GOLD, lw=1.2, ls="--")
    ax.text(m_star + 1.5, 35, f"$m'_л \\approx {m_star:.0f}$ г:\n$F_А = F_{{тяж}}$", color=INK)
    ax.fill_between(m, mass, displaced, where=m > m_star, color=GREEN, alpha=0.12)
    ax.fill_between(m, mass, displaced, where=m < m_star, color=HOT, alpha=0.12)
    ax.text(72, 60, "плавает", color=GREEN)
    ax.text(14, 3, "тонет", color=HOT)
    ax.set_xlabel("масса оставшегося льда $m'_л$, г")
    ax.set_ylabel("масса, г")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 120)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    clean_axes(ax)
    ax.set_title(f"Порог плавания; на плавление $Q \\approx$ {fmt(q)} кДж")
    save(fig, "balance-task-lead-float.png")


def task_lead_drop():
    c_pb, lam_pb, t0, t_m = 0.14, 25.0, 27.0, 327.0
    need = c_pb * (t_m - t0) + lam_pb  # kJ/kg
    g = 10.0
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axs[0]
    heat = c_pb * (t_m - t0)
    ax.bar([0], [heat], color=HOT, width=0.5, label="нагрев с $27$ до $327\\ ^\\circ$C")
    ax.bar([0], [lam_pb], bottom=[heat], color=GOLD, width=0.5, label="плавление")
    ax.bar([1], [need], color=COLD, width=0.5, label="доля механической энергии\n$\\eta E_п$")
    ax.bar([1], [need], color="none", width=0.5, edgecolor=INK, lw=1.5)
    ax.bar([2], [need / 0.5], color=LIGHT, width=0.5, edgecolor=GREY, lw=1.5)
    ax.bar([2], [need], color=COLD, width=0.5, alpha=0.9)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["нужно дробинке", "получено\nдробинкой", "$E_п$ на высоте\n(вторая половина\nуходит в среду)"], fontsize=9)
    ax.set_ylabel("кДж на $1$ кг свинца")
    ax.text(0, need + 4, f"${need:.0f}$", ha="center")
    ax.text(1, need + 4, f"${need:.0f}$", ha="center")
    ax.text(2, need / 0.5 + 4, f"${need / 0.5:.0f}$", ha="center")
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    ax.set_ylim(0, need / 0.5 * 1.35)
    clean_axes(ax)
    ax.set_title("Энергетический баланс")
    ax = axs[1]
    eta = np.linspace(0.2, 1.0, 200)
    h = need * 1000 / (eta * g) / 1000.0
    ax.plot(eta, h, color=HOT, lw=2.6)
    ax.scatter([0.5], [need * 1000 / (0.5 * g) / 1000.0], color=INK, zorder=5)
    ax.annotate("$\\eta = 0{,}5$: $h \\approx 13{,}4$ км", (0.5, 13.4), (0.62, 22), arrowprops=dict(arrowstyle="-", color=GREY))
    ax.set_xlabel("доля механической энергии $\\eta$, идущая на дробинку")
    ax.set_ylabel("высота $h$, км")
    ax.set_ylim(0, 36)
    clean_axes(ax)
    ax.set_title("Чем больше уходит в среду, тем выше нужно поднять")
    save(fig, "balance-task-lead-drop.png")


def main():
    isolated_system()
    equilibrium_curves()
    energy_bars()
    sign_rule()
    mixture_share()
    task_add_boiling_water()
    task_kettle()
    task_ball_liquid()
    task_steel_oil()
    task_bath_lever()
    task_ice_in_boiling_water()
    task_ice_water_steam()
    task_copper_in_water()
    task_supercooled()
    task_superheated()
    task_vacuum_freezing()
    task_lead_float()
    task_lead_drop()


if __name__ == "__main__":
    main()
