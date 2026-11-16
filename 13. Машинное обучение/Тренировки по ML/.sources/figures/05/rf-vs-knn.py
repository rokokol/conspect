"""Random forest and 3-NN on the same moons data and split, as on slide 40 of the lecture."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

MODELS = {
    "Random Forest, 100 деревьев": lambda: RandomForestClassifier(n_estimators=100, random_state=fk.SEED),
    "3-NN": lambda: KNeighborsClassifier(n_neighbors=3),
}

fig, axes = fk.model_grid(lambda _, name: MODELS[name](), [None], list(MODELS), "moons",
                          col_label=lambda name: name, size=(7.4, 3.6))
fk.save(fig, fk.attachments(5) / "rf-vs-knn.png")

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
for name, make in MODELS.items():
    m = make().fit(Xtr, ytr)
    print(name, "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
