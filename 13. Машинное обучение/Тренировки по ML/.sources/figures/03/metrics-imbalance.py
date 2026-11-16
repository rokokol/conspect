"""The 99:1 trap: a constant classifier that always answers the first (majority) class."""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, precision_score, recall_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

n = 10000
y = np.r_[np.zeros(9900, int), np.ones(100, int)]
pred = np.zeros(n, int)
cm = confusion_matrix(y, pred)

# Class 0 is the majority and is taken as the target for precision and recall; class 1 as the target for the other pair.
rows = [
    ("accuracy", accuracy_score(y, pred), fk.TEXT_2),
    ("balanced\naccuracy", balanced_accuracy_score(y, pred), fk.TEXT_2),
    ("precision\nкласса 0", precision_score(y, pred, pos_label=0), fk.CLASS_COLORS[0]),
    ("recall\nкласса 0", recall_score(y, pred, pos_label=0), fk.CLASS_COLORS[0]),
    ("precision\nкласса 1", precision_score(y, pred, pos_label=1, zero_division=0), fk.CLASS_COLORS[1]),
    ("recall\nкласса 1", recall_score(y, pred, pos_label=1), fk.CLASS_COLORS[1]),
]
for name, v, _ in rows:
    print(name.replace("\n", " "), round(float(v), 4))

fig, (ax, bx) = fk.subplots(1, 2, size=(10.4, 4.0), gridspec_kw={"width_ratios": [1, 1.7]})
im = ax.imshow(np.log10(cm + 1), cmap="ddlc_seq", vmin=0, vmax=4.2)
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{cm[i, j]}", ha="center", va="center", fontsize=12,
                color="white" if cm[i, j] > 500 else fk.TEXT)
ax.set_xticks([0, 1], ["предсказан 0", "предсказан 1"])
ax.set_yticks([0, 1], ["на деле 0", "на деле 1"])
ax.tick_params(length=0)
ax.set_title("матрица ошибок, цвет - логарифм")

vals = [v for _, v, _ in rows]
bars = bx.bar(range(len(rows)), vals, color=[c for *_, c in rows])
for b, v, (name, *_) in zip(bars, vals, rows):
    bx.text(b.get_x() + b.get_width() / 2, v + 0.02, "0/0" if name.startswith("precision\nкласса 1") else fk.num(v, 2),
            ha="center", fontsize=9, color=fk.TEXT)
bx.set_xticks(range(len(rows)), [r[0] for r in rows], fontsize=7)
bx.set_ylim(0, 1.12)
bx.set_title("всегда отвечает классом 0")
bx.grid(True, axis="y")
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "metrics-imbalance.png")
