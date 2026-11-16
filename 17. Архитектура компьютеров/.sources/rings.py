"""Protection rings of IA-32 for f05 "Режимы работы процессоров Intel"."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "05. Структура и функции центрального процессора" / "00. Вложения"

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.set_aspect("equal")
ax.axis("off")

radii = [1.0, 0.75, 0.5, 0.25]
labels = ["Уровень 3\nПриложения", "Уровень 2\nСлужбы ОС (драйверы)", "Уровень 1\n(редко используется)", "Уровень 0\nЯдро ОС"]
# Outer to inner: the deeper the privilege, the stronger the tint.
colors = [P["dot"], P["blush"], P["natsuki"], P["pink"]]

for i, (r, c) in enumerate(zip(radii, colors)):
    ax.add_patch(plt.Circle((0, 0), r, facecolor=c, edgecolor=P["plum"], linewidth=1.4, zorder=i))

# The labels are wider than the ring bands, so they stand in a column on the
# right and a leader line points from each label into the middle of its band.
mid_radii = [(radii[i] + (radii[i + 1] if i + 1 < len(radii) else 0)) / 2 for i in range(len(radii))]
mid_radii[-1] = 0.0
label_y = [0.80, 0.30, -0.20, -0.70]
for r, lab, y in zip(mid_radii, labels, label_y):
    ang = math.radians(35)
    anchor = (r * math.cos(ang), r * math.sin(ang))
    ax.annotate(lab, xy=anchor, xytext=(1.25, y), ha="left", va="center", fontsize=9, zorder=10,
                arrowprops=dict(arrowstyle="-", color=P["ink"], lw=0.8, shrinkA=2, shrinkB=0))
    ax.plot(*anchor, "o", color=P["ink"], ms=3, zorder=11)

ax.set_xlim(-1.1, 2.75)
ax.set_ylim(-1.1, 1.1)
ax.set_title("Кольца защиты", fontsize=13)
plt.tight_layout()
plt.savefig(OUT / "кольца-защиты.png", dpi=150)
