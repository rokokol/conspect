"""Boosting over linear regressions stays a line; boosting over stumps leaves the class of lines.

Both are gradient boosting for the squared loss written out: F_t = F_{t-1} + eta * h_t, where h_t is fitted to the
residuals y - F_{t-1}. The first panel adds linear regressions, the second adds decision stumps, on the noisy sine
(reg1d). The step eta is the same in both panels, so only the base model changes.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

X, y = fk.dataset("reg1d")
grid = np.linspace(0, 1, 400)[:, None]
truth = np.sin(2 * np.pi * grid[:, 0])
ROUNDS = (1, 5, 100)
LR = 0.3


def boost(make, rounds, lr):
    F_train = np.zeros(len(y))
    F_grid = np.zeros(len(grid))
    snaps = {}
    for t in range(1, max(rounds) + 1):
        h = make().fit(X, y - F_train)
        F_train += lr * h.predict(X)
        F_grid += lr * h.predict(grid)
        if t in rounds:
            snaps[t] = (F_grid.copy(), F_train.copy())
    return snaps


lin = boost(LinearRegression, ROUNDS, LR)
stump = boost(lambda: DecisionTreeRegressor(max_depth=1, random_state=fk.SEED), ROUNDS, LR)
ols = LinearRegression().fit(X, y)
ols_grid = ols.predict(grid)
ols_mse = float(np.mean((ols.predict(X) - y) ** 2))
# After t steps the boosted line is the OLS line shrunk toward zero by (1 - LR) ** t.
for t in ROUNDS:
    expected = (1 - (1 - LR) ** t) * ols_grid
    print(t, "max |boosted line - (1 - (1 - eta)^t) * OLS line| =", float(np.max(np.abs(lin[t][0] - expected))))
print("max |boosted lines (100) - one OLS line| =", float(np.max(np.abs(lin[100][0] - ols_grid))))
print("train mse of the OLS line", round(ols_mse, 4))
for t in ROUNDS:
    print(t, "train mse lines", round(float(np.mean((lin[t][1] - y) ** 2)), 4),
          "stumps", round(float(np.mean((stump[t][1] - y) ** 2)), 4))

fig, axes = fk.subplots(1, 2, size=(10.4, 4.0), sharey=True)
for ax, snaps, title in ((axes[0], lin, f"бустинг над линейными моделями, шаг {fk.num(LR, None)}"),
                         (axes[1], stump, f"бустинг над пнями, шаг {fk.num(LR, None)}")):
    ax.plot(grid[:, 0], truth, color=fk.TEXT_2, ls="--", lw=1.1, label="sin 2πx")
    ax.scatter(X[:, 0], y, s=20, color=fk.TRAIN_C, edgecolors="white", linewidths=0.6, zorder=3, label="train")
    for t, color, lw, ls in zip(ROUNDS, (fk.TEXT_2, fk.MODEL2_C, fk.MODEL_C), (1.6, 1.6, 2.4), (":", "-", "-")):
        ax.plot(grid[:, 0], snaps[t][0], color=color, lw=lw, ls=ls,
                label=f"{t} {'модель' if t == 1 else 'моделей'}")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.legend(loc="upper right", fontsize=7)
axes[0].set_ylabel("y")

fk.save(fig, fk.attachments(5) / "bv-boosting-linear.png")
