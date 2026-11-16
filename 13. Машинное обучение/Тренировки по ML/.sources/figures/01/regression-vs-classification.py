"""The two classic supervised tasks: a curve through numeric targets, regions between labelled classes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)

fig, (a, b) = fk.plt.subplots(1, 2, figsize=(9.2, 3.6))

# Regression: target is a number, the model is a curve.
X, y = fk.dataset("reg1d")
a.scatter(X[:, 0], y, s=22, color=fk.BLUE, edgecolors="white", linewidths=0.6, zorder=3)
grid = np.linspace(0, 1, 200)
a.plot(grid, np.polyval(np.polyfit(X[:, 0], y, 3), grid), color=fk.RED, lw=2)
a.set_xlabel("признак x")
a.set_ylabel("цель y (число)")
a.set_title("Регрессия: кривая через точки")

# Classification: target is a label, the model is a partition of feature space.
Xc, yc = fk.dataset("blobs3")
fk.plot_decision(b, KNeighborsClassifier(15).fit(Xc, yc), Xc, yc, scores=False,
                 title="Классификация: зоны классов")
b.set_xlabel("признак 1")
b.set_ylabel("признак 2")

fig.tight_layout()
fk.save(fig, OUT / "regression-vs-classification.png")
