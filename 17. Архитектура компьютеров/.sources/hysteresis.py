#!/usr/bin/env python3
"""Передаточная характеристика триггера Шмитта с петлёй гистерезиса."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "03. Элементная база цифровых ЭВМ" / "00. Вложения"

INK = P["ink"]
ACC = P["rule"]  # loop
ACC2 = P["bow"]  # thresholds

VTm, VTp = 1.4, 2.6      # V_T-, V_T+
LO, HI = 0.0, 3.3        # выходные уровни
xmax = 4.0

fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)

# нижняя ветвь (выход LOW), пока вход не достиг V_T+
ax.plot([-0.4, VTp], [LO, LO], color=ACC, lw=2.6, solid_capstyle="round")
# скачок вверх на V_T+
ax.plot([VTp, VTp], [LO, HI], color=ACC, lw=2.6, ls=(0, (1, 1.2)))
# верхняя ветвь (выход HIGH), пока вход не упал ниже V_T-
ax.plot([VTm, xmax], [HI, HI], color=ACC, lw=2.6, solid_capstyle="round")
# скачок вниз на V_T-
ax.plot([VTm, VTm], [HI, LO], color=ACC, lw=2.6, ls=(0, (1, 1.2)))


# стрелки направления обхода петли
def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                 mutation_scale=16, color=ACC, lw=0))


arrow(0.7, LO, 1.05, LO)          # по низу вправо
arrow(VTp, 1.5, VTp, 1.95)        # вверх
arrow(3.15, HI, 2.8, HI)          # по верху влево
arrow(VTm, 1.8, VTm, 1.35)        # вниз

# пороги: пунктир только под уровнем LOW, выше него порог показывает сам скачок петли
for v, lab, dx in [(VTm, r"$V_{T-}$", -0.05), (VTp, r"$V_{T+}$", 0.05)]:
    ax.plot([v, v], [-0.4, LO - 0.08], color=ACC2, lw=1.0, ls=(0, (4, 3)))
    ax.text(v + dx, -0.42, lab, color=ACC2, ha="center", va="top", fontsize=13)

# ΔV — ширина гистерезиса
ax.annotate("", xy=(VTp, 2.7), xytext=(VTm, 2.7),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1))
ax.text((VTm + VTp) / 2, 2.78, r"$\Delta V$", color=INK, ha="center",
        va="bottom", fontsize=13)

# уровни выхода
ax.text(-0.5, HI, "HIGH", color=INK, ha="right", va="center", fontsize=10)
ax.text(-0.5, LO, "LOW", color=INK, ha="right", va="center", fontsize=10)

ax.set_xlim(-1.0, xmax + 0.1)
ax.set_ylim(-0.55, 3.55)
ax.set_xlabel(r"$V_{\mathrm{вх}}$", fontsize=13, labelpad=20)
ax.set_ylabel(r"$V_{\mathrm{вых}}$", fontsize=13, rotation=0, labelpad=16)
ax.set_title("Петля гистерезиса триггера Шмитта", fontsize=13, pad=12)
ax.set_xticks([])
ax.set_yticks([])
fig.tight_layout()

fig.savefig(OUT / "Петля гистерезиса триггера Шмитта.png", bbox_inches="tight")
