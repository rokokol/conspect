"""Decision regions of bagged full trees on moons: 1, 10 and 100 trees; the data and the split are the same in every cell."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import BaggingClassifier  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

COUNTS = [1, 10, 100]


def make(_, n):
    return BaggingClassifier(DecisionTreeClassifier(random_state=fk.SEED), n_estimators=n, bootstrap=True,
                             random_state=fk.SEED)


fig, axes = fk.model_grid(make, [None], COUNTS, "moons", col_label=lambda n: f"деревьев: {n}", size=(10.4, 3.5))
fk.save(fig, fk.attachments(5) / "bag-moons-zones.png")

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
for n in COUNTS:
    m = make(None, n).fit(Xtr, ytr)
    print(n, "train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))
single = DecisionTreeClassifier(random_state=fk.SEED).fit(Xtr, ytr)
print("single tree on all train: train", round(single.score(Xtr, ytr), 3), "test", round(single.score(Xte, yte), 3))
