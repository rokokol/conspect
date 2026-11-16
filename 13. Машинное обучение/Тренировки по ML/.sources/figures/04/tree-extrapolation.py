"""A tree does not extrapolate: outside the train range it repeats the edge leaf, a line keeps the trend."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LinearRegression  # noqa: E402
from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

# A trend y = 2x + noise on [0, 1]; the plot goes to [-0.5, 1.5], the train data does not.
rng = np.random.default_rng(fk.SEED)
x = np.sort(rng.uniform(0, 1, 60))
y = 2 * x + rng.normal(0, 0.25, x.size)
X = x[:, None]
grid = np.linspace(-0.5, 1.5, 800)[:, None]

fig, axes = fk.subplots(1, 2, size=(10.4, 3.9), sharey=True)
ax = axes[0]
tree = DecisionTreeRegressor(max_depth=4, random_state=fk.SEED).fit(X, y)
line = LinearRegression().fit(X, y)
ax.axvspan(-0.5, 0, color=fk.tint(fk.GRIDC, 0.7), zorder=0)
ax.axvspan(1, 1.5, color=fk.tint(fk.GRIDC, 0.7), zorder=0)
ax.plot(grid[:, 0], 2 * grid[:, 0], color=fk.TEXT_2, ls="--", lw=1, label="истина 2x")
ax.plot(grid[:, 0], line.predict(grid), color=fk.MODEL2_C, lw=2, label="линейная регрессия")
ax.plot(grid[:, 0], tree.predict(grid), color=fk.MODEL_C, lw=2, label="дерево, глубина 4")
ax.scatter(x, y, s=20, color=fk.TRAIN_C, edgecolors="white", linewidths=0.6, zorder=3, label="train")
ax.set_title("Тренд за пределами обучения")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend(loc="upper left", fontsize=7)

# The same on the sine from reg1d: the leaf at the edge is one constant to infinity.
Xs, ys = fk.dataset("reg1d")
ax = axes[1]
t3 = DecisionTreeRegressor(max_depth=3, random_state=fk.SEED).fit(Xs, ys)
ax.axvspan(-0.5, 0, color=fk.tint(fk.GRIDC, 0.7), zorder=0)
ax.axvspan(1, 1.5, color=fk.tint(fk.GRIDC, 0.7), zorder=0)
ax.plot(grid[:, 0], np.sin(2 * np.pi * grid[:, 0]), color=fk.TEXT_2, ls="--", lw=1, label="sin 2πx")
ax.plot(grid[:, 0], t3.predict(grid), color=fk.MODEL_C, lw=2, label="дерево, глубина 3")
ax.scatter(Xs[:, 0], ys, s=20, color=fk.TRAIN_C, edgecolors="white", linewidths=0.6, zorder=3, label="train")
ax.set_title("Крайние листья — константы")
ax.set_xlabel("x")
ax.legend(loc="upper left", fontsize=7)
fk.save(fig, fk.attachments(4) / "tree-extrapolation.png")

print("tree at -0.5, 0, 1, 1.5:", [round(float(v), 3) for v in tree.predict(np.array([[-0.5], [0], [1], [1.5]]))])
print("line at same:", [round(float(v), 3) for v in line.predict(np.array([[-0.5], [0], [1], [1.5]]))])
print("truth at 1.5 = 3; sine tree edge values:", [round(float(v), 3) for v in t3.predict(np.array([[-0.5], [1.5]]))])
