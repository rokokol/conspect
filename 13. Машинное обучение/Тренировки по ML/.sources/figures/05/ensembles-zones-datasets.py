"""One tree, a random forest, AdaBoost on stumps and gradient boosting on moons, circles and xor.

Every model gets its hyperparameters from 5-fold cross-validation on the train part of its data set (the grids are in GRIDS);
the split is the same as for the other models of the course, and the test part only shows the result. The chosen values are printed under each cell.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier  # noqa: E402
from sklearn.model_selection import GridSearchCV, StratifiedKFold  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

DATA = ["moons", "circles", "xor"]
GRIDS = {
    "одно дерево": (DecisionTreeClassifier(random_state=fk.SEED),
                    {"max_depth": [2, 3, 4, 5, 6, 8, 10, None], "min_samples_leaf": [1, 5, 10]}),
    "случайный лес": (RandomForestClassifier(n_estimators=200, random_state=fk.SEED),
                      {"max_depth": [3, 5, 8, None], "min_samples_leaf": [1, 5]}),
    "AdaBoost на пнях": (AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=fk.SEED), random_state=fk.SEED),
                         {"n_estimators": [10, 50, 200], "learning_rate": [0.1, 0.5, 1.0]}),
    "градиентный бустинг": (GradientBoostingClassifier(random_state=fk.SEED),
                            {"n_estimators": [50, 200], "max_depth": [1, 2, 3], "learning_rate": [0.05, 0.2]}),
}
SHORT = {"max_depth": "глубина", "min_samples_leaf": "лист", "n_estimators": "T", "learning_rate": "η"}

fig, axes = fk.subplots(len(DATA), len(GRIDS), size=(13.2, 10.2))
for i, name in enumerate(DATA):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for j, (title, (est, grid)) in enumerate(GRIDS.items()):
        search = GridSearchCV(est, grid, cv=StratifiedKFold(5, shuffle=True, random_state=fk.SEED)).fit(Xtr, ytr)
        fk.plot_decision(axes[i, j], search, Xtr, ytr, X_test=Xte, y_test=yte)
        params = ", ".join(f"{SHORT[k]} = {fk.num(v, None) if isinstance(v, float) else v}" for k, v in search.best_params_.items())
        axes[i, j].set_xlabel(params, fontsize=8)
        if i == 0:
            axes[i, j].set_title(title)
        if j == 0:
            axes[i, j].set_ylabel(name)
        print(name, "|", title, "|", search.best_params_, "cv", round(search.best_score_, 3),
              "train", round(search.score(Xtr, ytr), 3), "test", round(search.score(Xte, yte), 3))
fig.tight_layout()
fk.save(fig, fk.attachments(5) / "ensembles-zones-datasets.png")
