"""Slide-10 student table with the vocabulary marked on it: object, feature, design matrix, target."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)

HEAD = ["Имя", "Возраст", "Статистика", "Python", "Цвет глаз", "Язык", "Оценка по ML", "Прошёл"]
ROWS = [
    ["John", "22", "5", "4", "Brown", "English", "5", "TRUE"],
    ["Aahna", "17", "4", "5", "Brown", "Hindi", "4", "TRUE"],
    ["Emily", "25", "5", "5", "Blue", "Chinese", "5", "TRUE"],
    ["Michael", "27", "3", "4", "Green", "French", "5", "TRUE"],
    ["Some student", "23", "3", "3", "NA", "Esperanto", "2", "FALSE"],
]
WIDTHS = [1.95, 1.1, 1.45, 1.1, 1.25, 1.45, 1.7, 1.1]
ROW_H, TOP = 0.62, 4.0
OBJ_C, FEAT_C, TARGET_C = fk.CATEGORICAL[0], fk.CATEGORICAL[1], fk.CATEGORICAL[2]

xs = [0.0]
for w in WIDTHS:
    xs.append(xs[-1] + w)
total = xs[-1]

fig, ax = fk.plt.subplots(figsize=(9.2, 4.6))
ax.set_xlim(-0.2, total + 0.2)
ax.set_ylim(-1.95, TOP + 1.25)
ax.axis("off")

# Cells: grey header, plain body.
for j, h in enumerate(HEAD):
    ax.add_patch(Rectangle((xs[j], TOP - ROW_H), WIDTHS[j], ROW_H, fc=fk.GREY, ec=fk.GRIDC))
    ax.text(xs[j] + WIDTHS[j] / 2, TOP - ROW_H / 2, h, ha="center", va="center",
            fontsize=9, fontweight="bold", color=fk.TEXT)
for i, row in enumerate(ROWS):
    y0 = TOP - ROW_H * (i + 2)
    for j, v in enumerate(row):
        ax.add_patch(Rectangle((xs[j], y0), WIDTHS[j], ROW_H, fc="white", ec=fk.GRIDC))
        ax.text(xs[j] + WIDTHS[j] / 2, y0 + ROW_H / 2, v, ha="center", va="center",
                fontsize=9, color=fk.TEXT)

body_top, body_bot = TOP - ROW_H, TOP - ROW_H * (len(ROWS) + 1)

# Design matrix: all feature columns of all objects.
ax.add_patch(FancyBboxPatch((xs[0] + 0.04, body_bot + 0.04), xs[6] - xs[0] - 0.08,
                            body_top - body_bot - 0.08, boxstyle="round,pad=0,rounding_size=0.06",
                            fc="none", ec=FEAT_C, lw=2.2))
ax.text((xs[0] + xs[6]) / 2, TOP + 0.62, "матрица объект-признак  X  (n × p)", ha="center",
        va="center", fontsize=10, color=FEAT_C, fontweight="bold")

# Target column.
ax.add_patch(FancyBboxPatch((xs[6] + 0.04, body_bot + 0.04), xs[8] - xs[6] - 0.08,
                            body_top - body_bot - 0.08, boxstyle="round,pad=0,rounding_size=0.06",
                            fc="none", ec=TARGET_C, lw=2.2))
ax.text((xs[6] + xs[8]) / 2, TOP + 0.62, "цель  y", ha="center", va="center", fontsize=10,
        color=TARGET_C, fontweight="bold")

# Object: the first row.
r0 = TOP - ROW_H * 2
ax.add_patch(Rectangle((xs[0] + 0.02, r0 + 0.02), xs[6] - 0.04, ROW_H - 0.04, fc=OBJ_C, alpha=0.2,
                       ec="none", zorder=2))
for j, v in enumerate(ROWS[0]):
    ax.text(xs[j] + WIDTHS[j] / 2, r0 + ROW_H / 2, v, ha="center", va="center", fontsize=9,
            color=fk.TEXT, zorder=4)

# Callouts underneath.
y_note = body_bot - 0.35
ax.annotate("объект: одна строка,\nвектор признаков $x^{(1)}$", xy=(xs[0] + 0.15, r0 + ROW_H / 2),
            xytext=(0.0, y_note - 0.95), fontsize=9, color=OBJ_C, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=OBJ_C, lw=1.5,
                            connectionstyle="arc3,rad=-0.25", shrinkB=2))
ax.annotate("признак: один столбец,\nодна величина у всех объектов", xy=(xs[2] + WIDTHS[2] / 2, body_bot + 0.02),
            xytext=(xs[2] + 0.05, y_note - 0.95), fontsize=9, color=FEAT_C, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=FEAT_C, lw=1.5, shrinkB=2))
ax.annotate("то, что нужно\nпредсказывать", xy=((xs[6] + xs[8]) / 2, body_bot + 0.02),
            xytext=(xs[6] + 0.3, y_note - 0.95), fontsize=9, color=TARGET_C, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=TARGET_C, lw=1.5, shrinkB=2))

ax.set_title("Выборка: студенты и итоговая оценка", fontsize=11, loc="left", pad=0)
fk.save(fig, OUT / "student-table-anatomy.png")
