"""Bagging against boosting in the terms of bias^2 and variance, measured by simulation on the noisy sine.

Left: a line and a deep tree, each alone and bagged (50 models on bootstrap samples of the same training sample).
Right: gradient boosting of depth-2 trees (learning rate 0.1) by the number of trees.
Every bar is bias^2 or variance over M fresh training samples of n = 30 points.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bv_common as bv  # noqa: E402
import figkit as fk  # noqa: E402

N, M, K = 30, 300, 50
SIGMA2 = bv.SIGMA ** 2
GRID2 = bv.GRID[:, None]


def single(make):
    def fit(x, y):
        m = make().fit(x[:, None], y)
        return lambda g: m.predict(g[:, None])
    return fit


def bagged(make, k=K):
    def fit(x, y):
        rng = np.random.default_rng(int(1e6 * abs(y[0])) % 2**31)
        models = []
        for _ in range(k):
            idx = rng.integers(0, len(x), len(x))
            models.append(make().fit(x[idx, None], y[idx]))
        return lambda g: np.mean([m.predict(g[:, None]) for m in models], axis=0)
    return fit


def tree():
    return DecisionTreeRegressor(random_state=fk.SEED)


cases = [
    ("линия", single(LinearRegression)),
    (f"{K} линий", bagged(LinearRegression)),
    ("дерево", single(tree)),
    (f"{K} деревьев", bagged(tree)),
]
res = []
for name, fit in cases:
    b, v = bv.decompose(bv.predictions(fit, N, M))
    res.append((name, b, v))
    print(name, round(b, 4), round(v, 4))

fig, axes = fk.subplots(1, 2, size=(11.6, 4.2))
ax = axes[0]
pos = np.arange(len(res))
w = 0.38
ax.bar(pos - w / 2, [r[1] for r in res], w, color=fk.MODEL_C, label="bias²")
ax.bar(pos + w / 2, [r[2] for r in res], w, color=fk.MODEL2_C, label="variance")
for p, (_, b, v) in zip(pos, res):
    ax.text(p - w / 2, b, fk.num(b, 3), ha="center", va="bottom", fontsize=7, color=fk.TEXT)
    ax.text(p + w / 2, v, fk.num(v, 3), ha="center", va="bottom", fontsize=7, color=fk.TEXT)
ax.axhline(SIGMA2, color=fk.TEXT_2, ls="--", lw=1.1, label=f"шум σ² = {fk.num(SIGMA2, 4)}")
ax.set_xticks(pos, [r[0] for r in res])
ax.set_ylabel("вклад в ошибку")
ax.set_title("бэггинг: variance вниз, bias² на месте")
ax.set_ylim(0, 0.27)
ax.grid(True, axis="y")
ax.legend(loc="upper right", fontsize=7)

ax = axes[1]
T = 300
checkpoints = [1, 2, 5, 10, 20, 50, 100, 200, 300]
rng = np.random.default_rng(fk.SEED)
preds = {t: np.empty((M, len(bv.GRID))) for t in checkpoints}
for i in range(M):
    x, y = bv.draw(rng, N)
    gb = GradientBoostingRegressor(n_estimators=T, learning_rate=0.1, max_depth=2, random_state=fk.SEED)
    gb.fit(x[:, None], y)
    for t, p in zip(range(1, T + 1), gb.staged_predict(GRID2)):
        if t in preds:
            preds[t][i] = p
bs, vs = zip(*(bv.decompose(preds[t]) for t in checkpoints))
for t, b, v in zip(checkpoints, bs, vs):
    print("gb", t, round(b, 4), round(v, 4))
ax.plot(checkpoints, bs, color=fk.MODEL_C, marker="o", ms=4, label="bias²")
ax.plot(checkpoints, vs, color=fk.MODEL2_C, marker="o", ms=4, label="variance")
ax.axhline(SIGMA2, color=fk.TEXT_2, ls="--", lw=1.1, label="шум σ²")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("число деревьев в бустинге")
ax.set_title("бустинг: bias² вниз, variance вверх")
ax.grid(True, axis="y")
ax.legend(loc="center right", fontsize=7)

fk.save(fig, fk.attachments(5) / "bv-ensembles.png")
