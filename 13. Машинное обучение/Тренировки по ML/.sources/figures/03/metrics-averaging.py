"""Micro, macro and weighted averages of recall and precision on three classes of different size, with the confusion matrix they come from."""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

cm_true = np.array([[90, 7, 3], [6, 20, 4], [2, 3, 5]])  # rows: true class, columns: predicted
y = np.repeat([0, 1, 2], cm_true.sum(1))
pred = np.concatenate([np.repeat([0, 1, 2], row) for row in cm_true])
assert (confusion_matrix(y, pred) == cm_true).all()

names = ["A (100)", "B (30)", "C (10)"]
res = {}
for metric, f in (("precision", precision_score), ("recall", recall_score), ("F1", f1_score)):
    per = f(y, pred, average=None)
    res[metric] = list(per) + [f(y, pred, average=a) for a in ("micro", "macro", "weighted")]
    print(metric, [round(float(v), 3) for v in res[metric]])
print("accuracy", round(float((y == pred).mean()), 3))

fig, (ax, bx) = fk.subplots(1, 2, size=(10.4, 4.0), gridspec_kw={"width_ratios": [1, 2.2]})
im = ax.imshow(cm_true, cmap="ddlc_seq", vmin=0, vmax=100)
for i in range(3):
    for j in range(3):
        ax.text(j, i, cm_true[i, j], ha="center", va="center", fontsize=11,
                color="white" if cm_true[i, j] > 55 else fk.TEXT)
ax.set_xticks(range(3), ["A", "B", "C"])
ax.set_yticks(range(3), names)
ax.set_xlabel("предсказан")
ax.set_ylabel("на деле")
ax.tick_params(length=0)
ax.set_title("матрица ошибок")

labels = ["A", "B", "C", "micro", "macro", "weighted"]
colors = fk.CATEGORICAL + [fk.TEXT_2] * 3
width = 0.38
x = np.arange(6)
for k, (metric, hatch) in enumerate((("precision", None), ("recall", "//"))):
    vals = res[metric]
    bars = bx.bar(x + (k - 0.5) * width, vals, width, color=colors, hatch=hatch, edgecolor="white",
                  label=metric)
    for b, v in zip(bars, vals):
        bx.text(b.get_x() + b.get_width() / 2, v + 0.015, fk.num(v, 2), ha="center", fontsize=6.5, color=fk.TEXT)
bx.set_xticks(x, labels)
bx.set_ylim(0, 1.1)
bx.grid(True, axis="y")
bx.set_title("сплошные столбцы precision, штрих recall")
bx.axvline(2.5, color=fk.GRIDC, lw=1)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "metrics-averaging.png")
