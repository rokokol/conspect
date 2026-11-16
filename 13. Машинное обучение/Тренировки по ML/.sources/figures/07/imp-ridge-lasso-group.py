"""Weights of OLS, Ridge and LASSO on one table with a group of three near-copies of a common signal, and the LASSO path.

The target is built from the common signal g, not from the copies: a copy is g plus its own small noise, so the group carries
one piece of information. Left: weights at a penalty chosen by 5-fold cross-validation on the train part (RidgeCV, and
LassoLarsCV with the exact LARS path, so no solver question). Right: the exact LASSO path (lars_path), the weights against the
share of the OLS L1 norm that is left; the vertical line is the cross-validated LASSO. The held-out part is used only for the
R^2 that the script prints.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LassoLarsCV, LinearRegression, RidgeCV, lars_path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
n = 150
g = rng.normal(size=n)
copies = [g + 0.1 * rng.normal(size=n) for _ in range(3)]
u1, u2 = rng.normal(size=n), rng.normal(size=n)
noise = rng.normal(size=(n, 2))
X = np.column_stack(copies + [u1, u2, noise])
NAMES = ["копия 1", "копия 2", "копия 3", "независимый\nсильный", "независимый\nслабый", "шум 1", "шум 2"]
y = 1.5 * g + 1.0 * u1 + 0.3 * u2 + rng.normal(0, 1.0, n)

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=fk.SEED)
sc = StandardScaler().fit(Xtr)
A, B = sc.transform(Xtr), sc.transform(Xte)

models = {
    "МНК": LinearRegression(),
    "Ridge": RidgeCV(alphas=np.logspace(-3, 3, 61), cv=5),
    "LASSO": LassoLarsCV(cv=5),
}
W, R2 = {}, {}
for name, m in models.items():
    m.fit(A, ytr)
    W[name] = m.coef_
    R2[name] = m.score(B, yte)

fig, (ax, axp) = fk.subplots(1, 2, size=(12.2, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
width = 0.26
xs = np.arange(len(NAMES))
for k, (name, color) in enumerate(zip(models, [fk.P["ash"], fk.CATEGORICAL[0], fk.CATEGORICAL[1]])):
    ax.bar(xs + (k - 1) * width, W[name], width, color=color, label=name)
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.set_xticks(xs, NAMES, fontsize=7)
ax.set_ylabel("вес при стандартизованном признаке")
ax.set_title("Штраф подобран кросс-валидацией")
ax.grid(True, axis="y")
ax.legend(loc="upper right")

_, _, coefs = lars_path(A, ytr - ytr.mean(), method="lasso")
share = np.abs(coefs).sum(0) / np.abs(coefs[:, -1]).sum()
colors = [fk.CATEGORICAL[0], fk.CATEGORICAL[1], fk.CATEGORICAL[2], fk.ACCENT]
for k, c in zip(range(4), colors):
    axp.plot(share, coefs[k], color=c, lw=2.2, zorder=3, label=NAMES[k].replace("\n", " "))
for k in range(4, 7):
    axp.plot(share, coefs[k], color=fk.TEXT_2, alpha=0.45, lw=1.1, zorder=2)
cv_share = np.abs(W["LASSO"]).sum() / np.abs(coefs[:, -1]).sum()
axp.axvline(cv_share, color=fk.TEXT, lw=1, ls="--")
axp.text(cv_share, axp.get_ylim()[1], " штраф из CV", fontsize=8, va="top", ha="left")
axp.axhline(0, color=fk.TEXT_2, lw=0.8)
axp.set_xlabel("доля нормы $\\|\\hat w\\|_1$ от МНК (слева сильный штраф)")
axp.set_title("Путь LASSO: сначала одна копия")
axp.grid(True, axis="y")
axp.legend(loc="upper left", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "imp-ridge-lasso-group.png")

print("corr of copies:", np.round(np.corrcoef(np.array(copies))[np.triu_indices(3, 1)], 3))
for name in models:
    print(name, np.round(W[name], 3), "R2 held-out", round(R2[name], 3))
print("ridge alpha", models["Ridge"].alpha_, "lasso alpha", models["LASSO"].alpha_, "cv L1 share", round(cv_share, 3))
ent = []
for k in range(7):
    nz = np.flatnonzero(coefs[k])
    ent.append((NAMES[k].replace("\n", " "), round(float(share[nz[0]]), 3) if len(nz) else None))
print("L1-share at which each feature enters:", ent)
first = np.flatnonzero(np.abs(coefs[:3]).sum(0))[0]
print("first copy on the path:", np.flatnonzero(coefs[:3, first]), "weights there", np.round(coefs[:, first], 3),
      "share", round(float(share[first]), 3))
