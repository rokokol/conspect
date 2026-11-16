"""GIF: the example of the lecture, slide 24: cos x + noise, three trees of depth 2, MSE, the start is the mean.

Left: the ensemble after t trees. Right: the residuals y - f_t, which are the antigradient of L = (y - q)^2 / 2, and the tree fitted to them.
The step rho_t is the exact one-dimensional minimum of the loss, so it is found by the formula and not chosen by hand.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from boost_common import ods_cos  # noqa: E402
from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

X, y = ods_cos(n=100)
M = 3
grid = np.linspace(-5, 5, 400)[:, None]

f = np.full(len(y), y.mean())
f_grid = np.full(len(grid), y.mean())
states = [(f.copy(), f_grid.copy(), None, None)]
for t in range(M):
    r = y - f  # the antigradient of (y - q)^2 / 2 at q = f
    h = DecisionTreeRegressor(max_depth=2, random_state=fk.SEED).fit(X, r)
    h_x = h.predict(X)
    rho = float(h_x @ r / (h_x @ h_x))  # argmin over rho of sum (y - f - rho h)^2 / 2
    states[-1] = states[-1][:2] + (h, rho)
    f = f + rho * h_x
    f_grid = f_grid + rho * h.predict(grid)
    states.append((f.copy(), f_grid.copy(), None, None))
print("exact steps rho_t:", [round(s[3], 6) for s in states[:M]])
print("mse after t trees:", [round(float(np.mean((y - s[0]) ** 2)), 4) for s in states])


def draw(ax, i):
    fig = ax.figure
    ax.remove()
    left, right = fig.subplots(1, 2, sharey=True)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.14, top=0.86, wspace=0.08)
    f_i, f_grid_i, h, rho = states[i]
    for a in (left, right):
        a.set_xlim(-5, 5)
        a.set_ylim(-2.4, 2.4)
        a.set_xlabel("x")
        a.grid(True)
    left.plot(grid[:, 0], np.cos(grid[:, 0]), color=fk.TEXT_2, ls="--", lw=1.4, label="cos x")
    left.scatter(X[:, 0], y, s=12, color=fk.TEXT_2, zorder=3)
    left.plot(grid[:, 0], f_grid_i, color=fk.MODEL_C, lw=2.2, label="ансамбль")
    left.set_title(f"после {i} {'дерева' if i == 1 else 'деревьев'}" if i else "старт: среднее", fontsize=10)
    left.legend(loc="lower left", fontsize=7)
    res = y - f_i
    right.scatter(X[:, 0], res, s=12, color=fk.TEXT_2, zorder=3)
    right.axhline(0, color=fk.GRIDC, lw=0.8)
    if h is not None:
        right.plot(grid[:, 0], h.predict(grid), color=fk.MODEL2_C, lw=2.2, label=f"дерево {i + 1}, ρ = {fk.num(rho, 2)}")
        right.legend(loc="lower left", fontsize=7)
    right.set_title(f"остатки y − f{i}" + (" и дерево по ним" if h is not None else ", итог"), fontsize=10)


fk.gif(draw, M + 1, fk.attachments(5) / "gb-cos-steps.gif", size=(9.0, 3.6), fps=0.8, hold_last=1)
