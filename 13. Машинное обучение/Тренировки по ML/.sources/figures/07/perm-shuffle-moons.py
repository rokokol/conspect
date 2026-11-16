"""What a shuffle does to the held-out points of a fitted forest: original, x1 shuffled, x2 shuffled.

Moons, one forest fitted on the train part (leaf size by 5-fold CV on it). Only the held-out part is touched; the
shuffle moves values of one column between objects, so each column keeps its own distribution.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xva, ytr, yva = fk.split(X, y)
grid = GridSearchCV(RandomForestClassifier(n_estimators=200, random_state=fk.SEED, n_jobs=-1),
                    {"min_samples_leaf": [1, 3, 5, 10, 20]}, cv=5).fit(Xtr, ytr)
m = grid.best_estimator_
rng = np.random.default_rng(fk.SEED)

variants = [("исходная отложенная часть", Xva)]
for j, nm in enumerate(["$x_1$", "$x_2$"]):
    Xs = Xva.copy()
    Xs[:, j] = rng.permutation(Xs[:, j])
    variants.append((f"перемешан {nm}", Xs))

fig, axes = fk.subplots(1, 3, size=(11.2, 3.7))
accs = []
for ax, (title, Z) in zip(axes, variants):
    fk.plot_decision(ax, m, Xtr, ytr, show_points=False, scores=False)
    pred = m.predict(Z)
    acc = float((pred == yva).mean())
    accs.append(acc)
    for k in (0, 1):
        s = yva == k
        # held-out points are hollow, as everywhere in the course
        ax.scatter(Z[s, 0], Z[s, 1], s=26, facecolors="white", edgecolors=fk.CLASS_COLORS[k], linewidths=1.3, zorder=3)
    wrong = pred != yva
    ax.scatter(Z[wrong, 0], Z[wrong, 1], s=40, marker="x", color=fk.ACCENT, linewidths=1.2, zorder=4)
    ax.set_title(f"{title}\naccuracy {fk.num(acc, 2)}", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "perm-shuffle-moons.png")
print("leaf", grid.best_params_, "held-out accuracy", [round(a, 3) for a in accs], "n", len(yva))
