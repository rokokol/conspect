"""Bagging on the noisy sine (reg1d): one full tree, a bundle of trees on bootstrap samples, and their mean."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

N_BUNDLE, N_MEAN = 20, 100

Xtr, ytr = fk.dataset("reg1d")
# Fresh test sample from the same sine and the same noise, as in the single-tree figure of topic 4.
rng_te = np.random.default_rng(fk.SEED + 1)
Xte = np.sort(rng_te.uniform(0, 1, 300))[:, None]
yte = np.sin(2 * np.pi * Xte[:, 0]) + rng_te.normal(0, 0.25, 300)
grid = np.linspace(0, 1, 600)[:, None]
truth = np.sin(2 * np.pi * grid[:, 0])

rng = np.random.default_rng(fk.SEED)
trees = []
for _ in range(N_MEAN):
    idx = rng.integers(0, len(Xtr), len(Xtr))
    trees.append(DecisionTreeRegressor(random_state=fk.SEED).fit(Xtr[idx], ytr[idx]))
single = DecisionTreeRegressor(random_state=fk.SEED).fit(Xtr, ytr)


def mse(pred_fn, X, y):
    return float(np.mean((pred_fn(X) - y) ** 2))


def mean_pred(k):
    return lambda X: np.mean([t.predict(X) for t in trees[:k]], axis=0)


fig, axes = fk.subplots(1, 3, size=(13.2, 3.9), sharey=True)


def base(ax):
    ax.plot(grid[:, 0], truth, color=fk.TEXT_2, ls="--", lw=1, label="sin 2πx")
    ax.scatter(Xtr[:, 0], ytr, s=22, color=fk.TRAIN_C, edgecolors="white", linewidths=0.6, zorder=3, label="train")
    ax.set_xlabel("x")


def corner(ax, text):
    ax.text(0.02, 0.04, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


ax = axes[0]
base(ax)
ax.plot(grid[:, 0], single.predict(grid), color=fk.MODEL_C, lw=1.8, label="дерево")
ax.set_title("одно дерево без ограничения")
corner(ax, f"MSE test {fk.num(mse(single.predict, Xte, yte), 3)}")
ax.set_ylabel("y")
ax.legend(loc="upper right", fontsize=7)

ax = axes[1]
base(ax)
for i, t in enumerate(trees[:N_BUNDLE]):
    ax.plot(grid[:, 0], t.predict(grid), color=fk.MODEL_C, lw=0.9, alpha=0.4,
            label="дерево на бутстрепе" if i == 0 else None)
ax.set_title(f"{N_BUNDLE} деревьев на бутстреп-выборках")
corner(ax, "MSE test одного дерева:\n" + f"{fk.num(np.mean([mse(t.predict, Xte, yte) for t in trees[:N_BUNDLE]]), 3)} в среднем")
ax.legend(loc="upper right", fontsize=7)

ax = axes[2]
base(ax)
ax.plot(grid[:, 0], single.predict(grid), color=fk.MODEL_C, lw=1, alpha=0.35, label="одно дерево")
ax.plot(grid[:, 0], mean_pred(N_MEAN)(grid), color=fk.MODEL2_C, lw=2.2, label=f"среднее {N_MEAN} деревьев")
ax.set_title(f"среднее по {N_MEAN} деревьям")
corner(ax, f"MSE test {fk.num(mse(mean_pred(N_MEAN), Xte, yte), 3)}")
ax.legend(loc="upper right", fontsize=7)

fk.save(fig, fk.attachments(5) / "bag-bootstrap-sine.png")

print("single", round(mse(single.predict, Xte, yte), 4))
print("bundle mean of single-tree mse", round(float(np.mean([mse(t.predict, Xte, yte) for t in trees[:N_BUNDLE]])), 4))
print("bagging of", N_MEAN, round(mse(mean_pred(N_MEAN), Xte, yte), 4))
for k in (1, 2, 5, 10, 20, 50, 100):
    print(k, round(mse(mean_pred(k), Xte, yte), 4))
print("noise floor", 0.25 ** 2)
