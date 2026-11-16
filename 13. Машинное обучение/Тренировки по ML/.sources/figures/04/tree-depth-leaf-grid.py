"""Decision regions on moons: rows are max_depth, columns are min_samples_leaf; the data and split are the same in every cell."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

DEPTHS = [1, 3, 6, 12]
LEAVES = [1, 5, 15, 40]

fig, axes = fk.model_grid(
    lambda d, leaf: DecisionTreeClassifier(max_depth=d, min_samples_leaf=leaf, random_state=fk.SEED),
    DEPTHS, LEAVES, "moons",
    col_label=lambda c: f"min_samples_leaf = {c}",
    row_label=lambda r: f"max_depth = {r}",
    size=(12.4, 11.6))
fk.save(fig, fk.attachments(4) / "tree-depth-leaf-grid.png")

X, y = fk.dataset("moons")
Xtr, _, ytr, _ = fk.split(X, y)
for d in DEPTHS:
    print(d, [DecisionTreeClassifier(max_depth=d, min_samples_leaf=leaf, random_state=fk.SEED)
              .fit(Xtr, ytr).get_n_leaves() for leaf in LEAVES])
