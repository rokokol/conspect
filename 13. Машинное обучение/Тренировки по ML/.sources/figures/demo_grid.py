"""Style check for figkit: five models on four data sets. Output goes to argv[1]."""
import sys

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

import figkit as fk

MODELS = {
    "kNN, k=15": lambda: KNeighborsClassifier(15),
    "Дерево, глубина 5": lambda: DecisionTreeClassifier(max_depth=5, random_state=0),
    "Логистическая регрессия": lambda: LogisticRegression(),
    "Random Forest": lambda: RandomForestClassifier(200, random_state=0),
    "Градиентный бустинг": lambda: GradientBoostingClassifier(random_state=0),
}
DATA = ["moons", "circles", "xor", "blobs3"]

fig, axes = fk.subplots(len(DATA), len(MODELS))
for i, d in enumerate(DATA):
    X, y = fk.dataset(d)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for j, (name, make) in enumerate(MODELS.items()):
        fk.plot_decision(axes[i, j], make().fit(Xtr, ytr), Xtr, ytr, X_test=Xte, y_test=yte,
                         title=name if i == 0 else None)
    axes[i, 0].set_ylabel(d)
fig.tight_layout()
fk.save(fig, sys.argv[1])
