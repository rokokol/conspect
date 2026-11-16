"""All course models on the same four data sets, each with its hyperparameters chosen by 5-fold CV on the train part.

The test part only shows the result of the models already chosen. Output: methods-grid-four-datasets.png,
and a plain-text table of the chosen hyperparameters and scores on stdout.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

DATA = ["moons", "circles", "xor", "blobs3"]
# name -> (estimator, grid, how to print the chosen values)
MODELS = {
    "kNN": (KNeighborsClassifier(), {"n_neighbors": [1, 3, 5, 9, 15, 25, 45]},
            lambda p: f"k={p['n_neighbors']}"),
    "Наивный Байес": (GaussianNB(), {}, lambda p: "без параметров"),
    "Логрегрессия": (LogisticRegression(max_iter=2000), {"C": [0.01, 0.1, 1, 10, 100]},
                     lambda p: f"C={fk.num(p['C'], None)}"),
    "Дерево": (DecisionTreeClassifier(random_state=fk.SEED), {"max_depth": list(range(1, 11))},
               lambda p: f"глубина {p['max_depth']}"),
    "Случайный лес": (RandomForestClassifier(200, random_state=fk.SEED),
                      {"min_samples_leaf": [1, 3, 5, 10, 20]},
                      lambda p: f"лист ≥{p['min_samples_leaf']}"),
    "Градиентный бустинг": (GradientBoostingClassifier(random_state=fk.SEED),
                            {"n_estimators": [50, 100, 200], "learning_rate": [0.05, 0.1, 0.3],
                             "max_depth": [1, 2, 3]},
                            lambda p: f"{p['n_estimators']} дер., η={fk.num(p['learning_rate'], None)}, глуб. {p['max_depth']}"),
    "Нейросеть": (make_pipeline(StandardScaler(), MLPClassifier(solver="lbfgs", max_iter=5000,
                                                                random_state=fk.SEED)),
                  {"mlpclassifier__hidden_layer_sizes": [(4,), (8,), (16,), (8, 8)],
                   "mlpclassifier__alpha": [1e-3, 1e-1, 1.0]},
                  lambda p: f"{p['mlpclassifier__hidden_layer_sizes']}, α={fk.num(p['mlpclassifier__alpha'], None)}"),
}


def chosen(name, Xtr, ytr):
    est, grid, _ = MODELS[name]
    if not grid:
        return est.fit(Xtr, ytr), {}, float("nan")
    cv = StratifiedKFold(5, shuffle=True, random_state=fk.SEED)
    gs = GridSearchCV(est, grid, cv=cv, error_score="raise").fit(Xtr, ytr)
    return gs.best_estimator_, gs.best_params_, gs.best_score_


if __name__ == "__main__":
    fig, axes = fk.subplots(len(DATA), len(MODELS), size=(2.5 * len(MODELS), 2.6 * len(DATA)))
    for i, d in enumerate(DATA):
        X, y = fk.dataset(d)
        Xtr, Xte, ytr, yte = fk.split(X, y)
        for j, name in enumerate(MODELS):
            model, params, cv_score = chosen(name, Xtr, ytr)
            fk.plot_decision(axes[i, j], model, Xtr, ytr, X_test=Xte, y_test=yte)
            if i == 0:
                axes[i, j].set_title(name, fontsize=9)
            axes[i, j].set_xlabel(MODELS[name][2](params), fontsize=7)
            print(f"{d}\t{name}\t{MODELS[name][2](params)}\tCV {cv_score:.3f}\ttrain {model.score(Xtr, ytr):.3f}"
                  f"\ttest {model.score(Xte, yte):.3f}")
        axes[i, 0].set_ylabel(d)
    fig.tight_layout()
    fk.save(fig, fk.attachments(8) / "methods-grid-four-datasets.png")
