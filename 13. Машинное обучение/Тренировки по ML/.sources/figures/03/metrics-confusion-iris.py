"""The lecture's iris confusion matrix (slide 36): raw counts, rows normalised, and the per-class numbers read from it."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

cm = np.array([[13, 0, 0], [0, 10, 6], [0, 0, 9]])  # rows: true class, columns: predicted; numbers from slide 36
norm = cm / cm.sum(1, keepdims=True)
names = ["setosa", "versicolor", "virginica"]
print("accuracy", cm.trace(), "/", cm.sum(), "=", round(cm.trace() / cm.sum(), 3))
print("row normalised", np.round(norm, 2).tolist())
print("column sums of the normalised matrix", np.round(norm.sum(0), 2).tolist())
print("precision", np.round(cm.diagonal() / cm.sum(0), 3).tolist(), "recall", np.round(cm.diagonal() / cm.sum(1), 3).tolist())

fig, axes = fk.subplots(1, 2, size=(9.6, 4.0))
for ax, m, title, fmt in ((axes[0], cm, "число объектов", lambda v: f"{v:d}"), (axes[1], norm, "строки нормированы на 1", lambda v: fk.num(v, 2))):
    ax.imshow(m, cmap="ddlc_seq", vmin=0, vmax=m.max())
    for i in range(3):
        for j in range(3):
            v = m[i, j]
            ax.text(j, i, fmt(v), ha="center", va="center", fontsize=11,
                    color="white" if v > 0.6 * m.max() else fk.TEXT)
    ax.set_xticks(range(3), names, rotation=20)
    ax.set_yticks(range(3), names)
    ax.set_xlabel("предсказан")
    ax.set_ylabel("на деле")
    ax.tick_params(length=0)
    ax.set_title(title)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "metrics-confusion-iris.png")
