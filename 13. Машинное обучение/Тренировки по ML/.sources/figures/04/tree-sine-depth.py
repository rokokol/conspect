"""Regression tree on the noisy sine (reg1d): depth 2 describes it, depth 5 and a full tree chase the noise."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

# All 40 points of reg1d are the train part, as on the lecture slide; the test part is a fresh
# sample of 300 points from the same sine with the same noise (0.25), so its MSE is not a 12-point guess.
Xtr, ytr = fk.dataset("reg1d")
rng_te = np.random.default_rng(fk.SEED + 1)
Xte = np.sort(rng_te.uniform(0, 1, 300))[:, None]
yte = np.sin(2 * np.pi * Xte[:, 0]) + rng_te.normal(0, 0.25, 300)
grid = np.linspace(0, 1, 600)[:, None]

fig, axes = fk.subplots(1, 3, size=(13.2, 3.7), sharey=True)
for ax, depth in zip(axes, [2, 5, None]):
    m = DecisionTreeRegressor(max_depth=depth, random_state=fk.SEED).fit(Xtr, ytr)
    ax.plot(grid[:, 0], np.sin(2 * np.pi * grid[:, 0]), color=fk.TEXT_2, ls="--", lw=1, label="sin 2πx")
    ax.plot(grid[:, 0], m.predict(grid), color=fk.MODEL_C, lw=2, label="дерево")
    ax.scatter(Xtr[:, 0], ytr, s=22, color=fk.TRAIN_C, edgecolors="white", linewidths=0.6, zorder=3, label="train")
    mse_tr = float(np.mean((m.predict(Xtr) - ytr) ** 2))
    mse_te = float(np.mean((m.predict(Xte) - yte) ** 2))
    name = "без ограничения" if depth is None else f"глубина {depth}"
    ax.set_title(f"{name}, листьев {m.get_n_leaves()}")
    ax.text(0.02, 0.04, f"MSE train {fk.num(mse_tr, 3)}\nMSE test {fk.num(mse_te, 3)}", transform=ax.transAxes, ha="left",
            va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    ax.set_xlabel("x")
    print(name, m.get_n_leaves(), round(mse_tr, 4), round(mse_te, 4))
axes[0].set_ylabel("y")
axes[0].legend(loc="upper right", fontsize=7)
fk.save(fig, fk.attachments(4) / "tree-sine-depth.png")

# Leaf constants of the depth-2 tree: each step is the mean of the train targets in its leaf.
m2 = DecisionTreeRegressor(max_depth=2, random_state=fk.SEED).fit(Xtr, ytr)
leaf = m2.apply(Xtr)
for lf in np.unique(leaf):
    print("leaf", lf, "n", int((leaf == lf).sum()), "mean", round(float(ytr[leaf == lf].mean()), 4),
          "value", round(float(m2.tree_.value[lf][0, 0]), 4))
print("thresholds", [round(float(t), 3) for t in m2.tree_.threshold if t > -2])
