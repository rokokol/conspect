"""kNN (k = 15) and Gaussian naive Bayes on the same four data sets, same split."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.naive_bayes import GaussianNB  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

DATA = ["moons", "blobs3", "circles", "xor"]
MODELS = [("kNN, k = 15", lambda: KNeighborsClassifier(15)), ("Гауссов NB", lambda: GaussianNB())]

fig, axes = fk.subplots(len(DATA), len(MODELS), size=(6.6, 12.4))
for i, d in enumerate(DATA):
    X, y = fk.dataset(d)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for j, (name, make) in enumerate(MODELS):
        fk.plot_decision(axes[i, j], make().fit(Xtr, ytr), Xtr, ytr, X_test=Xte, y_test=yte,
                         title=name if i == 0 else None)
    axes[i, 0].set_ylabel(d)
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "nb-vs-knn-grid.png")
