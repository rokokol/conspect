"""Reliability curves of four classifiers on one data set, and the histogram of the predicted probabilities."""
import sys
from pathlib import Path

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# After scikit-learn's plot_compare_calibration example (20 features, 2 informative, 2 redundant),
# with 20000 objects and 2000 of them for training instead of 100000 and 100.
X, y = make_classification(n_samples=20000, n_features=20, n_informative=2, n_redundant=2,
                           random_state=fk.SEED)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.9, random_state=fk.SEED)

svm = LinearSVC(C=1.0, max_iter=100000)


class ScaledSVM:
    """LinearSVC has no probabilities; its margin is min-max scaled to [0, 1] by the training range and clipped, as the example does."""

    def fit(self, X, y):
        svm.fit(X, y)
        d = svm.decision_function(X)
        self.lo, self.hi = d.min(), d.max()
        return self

    def predict_proba(self, X):
        s = np.clip((svm.decision_function(X) - self.lo) / (self.hi - self.lo), 0, 1)
        return np.c_[1 - s, s]


models = [
    ("логистическая регрессия", LogisticRegression(max_iter=1000), fk.MODEL_C),
    ("наивный байес", GaussianNB(), fk.MODEL2_C),
    ("линейный SVM (margin в [0,1])", ScaledSVM(), fk.CATEGORICAL[1]),
    ("случайный лес", RandomForestClassifier(n_estimators=100, random_state=fk.SEED), fk.TEXT_2),
]

fig, axes = fk.subplots(1, 2, size=(10.4, 4.1))
ax = axes[0]
ax.plot([0, 1], [0, 1], color=fk.GRIDC, ls="--", label="идеал")
hists = []
for name, m, color in models:
    m.fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    frac, mean = calibration_curve(yte, p, n_bins=10, strategy="uniform")
    ax.plot(mean, frac, marker="s", ms=4, color=color, label=name)
    hists.append((name, p, color))
    print(name, "bins", len(frac), "max |frac-mean|", round(float(np.abs(frac - mean).max()), 3))
ax.set_xlabel("средняя предсказанная вероятность в корзине")
ax.set_ylabel("доля положительных в корзине")
ax.set_title("reliability curve")
ax.legend(loc="upper left", fontsize=7)
ax.grid(True)

ax = axes[1]
bins = np.linspace(0, 1, 11)
for name, p, color in hists:
    if name in ("логистическая регрессия", "наивный байес"):
        ax.hist(p, bins=bins, histtype="step", lw=2, color=color, label=name)
ax.set_xlabel("предсказанная вероятность")
ax.set_ylabel("число объектов теста")
ax.set_title("распределение предсказаний")
ax.legend(loc="upper center", fontsize=7)
ax.grid(True, axis="y")
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "logreg-calibration.png")
