"""Linear weights as importance: raw weight, weight after standardization, standardized coefficient; then one unit changed.

Same table, same least-squares fit on the train part; the second row only rewrites the first feature from km into m.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
n = 400
Z = rng.normal(size=(n, 3))
TRUE = np.array([2.0, 1.0, 0.4])  # effect of one standard deviation of each feature
y = Z @ TRUE + rng.normal(0, 1.0, n)
SCALE = np.array([5.0, 40.0, 10.0])
SHIFT = np.array([20.0, 100.0, 40.0])
X_km = Z * SCALE + SHIFT  # distance km, area m2, age years
NAMES = ["расстояние", "площадь", "возраст"]
UNITS = [["км", "м²", "лет"], ["м", "м²", "лет"]]

Xtr_km, _, ytr, _ = train_test_split(X_km, y, test_size=0.3, random_state=fk.SEED)
Xtr_m = Xtr_km.copy()
Xtr_m[:, 0] *= 1000

colors = [fk.CATEGORICAL[0], fk.CATEGORICAL[1], fk.CATEGORICAL[2]]
fig, axes = fk.subplots(2, 3, size=(11.6, 6.0))
for r, Xtr in enumerate((Xtr_km, Xtr_m)):
    w = LinearRegression().fit(Xtr, ytr).coef_
    w_std = LinearRegression().fit(StandardScaler().fit_transform(Xtr), ytr).coef_
    beta = w * Xtr.std(0) / ytr.std()
    panels = [(w, "вес $\\widehat w_i$ в исходных единицах", True),
              (w_std, "вес после стандартизации", False),
              (beta, "стандартизованный коэффициент", False)]
    for c, (vals, title, log) in enumerate(panels):
        ax = axes[r, c]
        yy = np.arange(3)[::-1]
        ax.barh(yy, vals, color=colors, height=0.62)
        if log:
            ax.set_xscale("log")
            ax.set_xlim(vals.min() / 4, vals.max() * 6)
        else:
            ax.set_xlim(0, vals.max() * 1.3)
        for yi, v, nm, u in zip(yy, vals, NAMES, UNITS[r]):
            ax.text(v, yi, f" {fk.num(v, '.3g')}", va="center", fontsize=8, color=fk.TEXT)
        ax.set_yticks(yy, [f"{nm}, {u}" for nm, u in zip(NAMES, UNITS[r])])
        ax.grid(True, axis="x")
        if r == 0:
            ax.set_title(title, fontsize=9)
    axes[r, 0].set_ylabel("")
fig.text(0.005, 0.74, "расстояние в км", rotation=90, va="center", fontsize=9, color=fk.TEXT_2)
fig.text(0.005, 0.27, "расстояние в м", rotation=90, va="center", fontsize=9, color=fk.TEXT_2)
fig.tight_layout(rect=(0.02, 0, 1, 1))
fk.save(fig, fk.attachments(7) / "imp-linear-scale.png")

print("true std effects", TRUE, "std(y)", round(float(ytr.std()), 3))
