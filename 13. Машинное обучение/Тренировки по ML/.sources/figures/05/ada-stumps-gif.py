"""GIF: three decision stumps of AdaBoost on twenty points; the point size is the weight, the last frame is the sum of the stumps."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from boost_common import AdaBoostScratch, toy_quadrant  # noqa: E402

import figkit as fk  # noqa: E402

X, y = toy_quadrant()
ROUNDS = 3
ada = AdaBoostScratch(depth=1).fit(X, y, ROUNDS)
LIM = 1.15
xx, yy = np.meshgrid(np.linspace(-LIM, LIM, 300), np.linspace(-LIM, LIM, 300))
grid = np.c_[xx.ravel(), yy.ravel()]


def frame_axes(ax):
    ax.figure.subplots_adjust(left=0.03, right=0.97, bottom=0.03, top=0.88)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(fk.GRIDC)


def points(ax, w, wrong=None):
    for k in (0, 1):
        m = y == k
        ax.scatter(X[m, 0], X[m, 1], s=40 * len(y) * w[m], color=fk.CLASS_COLORS[k], edgecolors="white",
                   linewidths=0.8, zorder=3)
    if wrong is not None:
        ax.scatter(X[wrong, 0], X[wrong, 1], s=40 * len(y) * w[wrong] + 60, facecolors="none", edgecolors=fk.ACCENT,
                   linewidths=1.1, zorder=4)


def draw(ax, i):
    frame_axes(ax)
    if i < ROUNDS:
        h, w = ada.stumps[i], ada.weights[i]
        side = h.predict(grid).reshape(xx.shape)
        ax.contourf(xx, yy, side, levels=[-2, 0, 2], colors=[fk.tint(fk.CLASS_COLORS[0], 0.6), fk.tint(fk.CLASS_COLORS[1], 0.6)])
        ax.contour(xx, yy, side, levels=[0], colors=fk.ACCENT, linewidths=1.6)
        wrong = h.predict(X) != 2 * y - 1
        points(ax, w, wrong)
        ax.set_title(f"пень {i + 1}: ε = {fk.num(ada.eps[i], 2)}, ρ = {fk.num(ada.rho[i], 2)}")
    else:
        total = sum(ada.rho)
        z = ada.score_at(grid).reshape(xx.shape) / total
        ax.contourf(xx, yy, (z + 1) / 2, levels=np.linspace(0, 1, 21), cmap=fk.PROBA_CMAP, vmin=0, vmax=1)
        ax.contour(xx, yy, z, levels=[0], colors=fk.ACCENT, linewidths=1.6)
        points(ax, np.full(len(y), 1 / len(y)))
        errors = int(np.sum(np.sign(ada.score_at(X)) != 2 * y - 1))
        ax.set_title(f"сумма ρ·h по трём пням, ошибок: {errors}")


if __name__ == "__main__":
    fk.gif(draw, ROUNDS + 1, fk.attachments(5) / "ada-stumps-toy.gif", size=(4.6, 4.4), fps=1, hold_last=2)
    print("eps", np.round(ada.eps, 3), "rho", np.round(ada.rho, 3))
    print("first stump errors", int((ada.stumps[0].predict(X) != 2 * y - 1).sum()), "of", len(y), "; ensemble errors after t:",
          [int(np.sum(np.sign(ada.score_at(X, t)) != 2 * y - 1)) for t in range(1, ROUNDS + 1)])
    print("weights before each round (sum 1):")
    for t in range(ROUNDS):
        print(t + 1, np.round(ada.weights[t] * len(y), 2).tolist())
