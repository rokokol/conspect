"""Gradient boosting on reg1d with four outliers: the step along the antigradient of MSE (a residual) against MAE (the sign of a residual); trees, depth, step and size of the ensemble are the same."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import GradientBoostingRegressor  # noqa: E402

import figkit as fk  # noqa: E402

X, y = fk.dataset("reg1d")
OUTLIERS = [8, 17, 26, 33]
y = y.copy()
y[OUTLIERS] += 3.0
grid = np.linspace(0, 1, 400)[:, None]
truth = np.sin(2 * np.pi * grid[:, 0])

fig, axes = fk.subplots(1, 2, size=(10.4, 3.8), sharey=True)
for ax, loss, title, color in [(axes[0], "squared_error", "MSE: шаг по остатку", fk.MODEL_C),
                               (axes[1], "absolute_error", "MAE: шаг по знаку остатка", fk.MODEL2_C)]:
    m = GradientBoostingRegressor(loss=loss, n_estimators=100, learning_rate=0.1, max_depth=2,
                                  random_state=fk.SEED).fit(X, y)
    ax.plot(grid[:, 0], truth, color=fk.GRIDC, lw=1.6, ls="--", label="sin 2πx")
    ax.plot(grid[:, 0], m.predict(grid), color=color, lw=2, label="ансамбль")
    ax.scatter(X[:, 0], y, s=18, color=fk.TEXT_2, zorder=3, label="данные")
    ax.scatter(X[OUTLIERS, 0], y[OUTLIERS], s=60, facecolors="none", edgecolors=fk.ACCENT, linewidths=1.2, zorder=4, label="выбросы")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.grid(True)
    err = float(np.mean((m.predict(grid) - truth) ** 2))
    ax.text(0.02, 0.04, f"MSE до sin 2πx: {fk.num(err, 3)}", transform=ax.transAxes, fontsize=8)
    print(loss, "mean squared distance to the true curve:", round(err, 4))
axes[0].legend(loc="upper right")
fk.save(fig, fk.attachments(5) / "gb-outliers-mse-vs-mae.png")
