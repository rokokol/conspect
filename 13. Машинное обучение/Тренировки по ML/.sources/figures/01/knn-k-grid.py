"""kNN decision regions on moons for k in {1, 5, 15, 50}, plus train/test accuracy against k."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.model_selection import cross_val_score  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

KS = [1, 5, 15, 50]

fig, _ = fk.model_grid(lambda r, c: KNeighborsClassifier(c), [0], KS, "moons",
                       col_label=lambda c: f"k = {c}", size=(12.8, 3.3))
fk.save(fig, fk.attachments(1) / "knn-k-grid-moons.png")

# Train/test accuracy against k; the chosen k comes from 5-fold CV on the train part only.
X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
ks = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100, 150]
train, test, cv = [], [], []
for k in ks:
    m = KNeighborsClassifier(k).fit(Xtr, ytr)
    train.append(m.score(Xtr, ytr))
    test.append(m.score(Xte, yte))
    cv.append(cross_val_score(KNeighborsClassifier(k), Xtr, ytr, cv=5).mean())

fig, ax = fk.subplots(1, 1, size=(6.4, 3.6))
b = fk.complexity_curve(ax, ks, train, test, xlabel="k (шкала логарифмическая)", val=cv, log=True)
ax.set_title("Точность kNN против k")
fk.save(fig, fk.attachments(1) / "knn-train-test-by-k.png")
print("k chosen by CV:", ks[b], "cv:", [round(c, 3) for c in cv])
