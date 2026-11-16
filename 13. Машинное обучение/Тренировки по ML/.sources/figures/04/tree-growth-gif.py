"""GIF: a decision tree on moons grows one level per frame; the splits of the new level are drawn thick."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402
from tree_common import box_of, draw_splits  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
box = box_of(X)
MAX_DEPTH = 8  # from depth 8 the tree is pure on the train part and stops growing

models = [DummyClassifier(strategy="prior").fit(Xtr, ytr)]
models += [DecisionTreeClassifier(max_depth=d, random_state=fk.SEED).fit(Xtr, ytr)
           for d in range(1, MAX_DEPTH + 1)]


def draw(ax, i):
    ax.figure.subplots_adjust(left=0.03, right=0.97, bottom=0.03, top=0.9)  # the frame is square: no wide white sides
    m = models[i]
    leaves = 1 if i == 0 else m.get_n_leaves()
    fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte, proba=False,
                     title=f"глубина {i}, листьев {leaves}")
    if i > 0:
        draw_splits(ax, m, box, newest=i)


fk.gif(draw, len(models), fk.attachments(4) / "tree-growth-moons.gif", size=(4.6, 4.4), fps=1.5, hold_last=3)
print("train/test:", [(round(m.score(Xtr, ytr), 3), round(m.score(Xte, yte), 3)) for m in models])
