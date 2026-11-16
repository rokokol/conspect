"""Random forest regions on moons: rows are max_features, columns are the number of trees; data and split are the same everywhere."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import RandomForestClassifier  # noqa: E402

import figkit as fk  # noqa: E402

FEATURES = [1, 2]
COUNTS = [1, 10, 100]

fig, axes = fk.model_grid(
    lambda mf, n: RandomForestClassifier(n_estimators=n, max_features=mf, random_state=fk.SEED),
    FEATURES, COUNTS, "moons",
    col_label=lambda n: f"деревьев: {n}",
    row_label=lambda mf: f"max_features = {mf}",
    size=(10.4, 6.8))
fk.save(fig, fk.attachments(5) / "rf-zones-grid.png")

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
for mf in FEATURES:
    for n in COUNTS:
        m = RandomForestClassifier(n_estimators=n, max_features=mf, random_state=fk.SEED).fit(Xtr, ytr)
        print("max_features", mf, "trees", n, "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
