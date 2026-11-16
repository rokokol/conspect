"""A linear classifier on linear, moons and xor; second row: the same pipeline (scaling, C=10) on degree-3 polynomial features."""
import sys
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

DATA = ("linear", "moons", "xor")
ROWS = {
    "линейные признаки": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=10.0, max_iter=5000)),
    "признаки до степени 3": lambda: make_pipeline(PolynomialFeatures(3, include_bias=False), StandardScaler(),
                                                   LogisticRegression(C=10.0, max_iter=5000)),
}

fig, axes = fk.subplots(len(ROWS), len(DATA), size=(9.6, 6.3))
for j, name in enumerate(DATA):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    for i, (label, make) in enumerate(ROWS.items()):
        model = make().fit(Xtr, ytr)
        fk.plot_decision(axes[i, j], model, Xtr, ytr, X_test=Xte, y_test=yte)
        if i == 0:
            axes[i, j].set_title(name)
        if j == 0:
            axes[i, j].set_ylabel(label)
        print(name, label, "train", round(model.score(Xtr, ytr), 3), "test", round(model.score(Xte, yte), 3))
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "margin-linear-zones.png")
