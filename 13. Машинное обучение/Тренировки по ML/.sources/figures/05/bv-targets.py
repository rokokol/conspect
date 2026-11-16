"""Bias and variance as a target: predictions at two points, for polynomials of degree 1, 3 and 7.

Each dot is one model fitted on its own fresh sample; its coordinates are the predictions at x = 0.25 and x = 0.95.
The centre is the truth (1, sin 1.9 pi). The distance from the centre to the cloud centre is the bias at the two points,
the size of the cloud is the variance.
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bv_common as bv  # noqa: E402
import figkit as fk  # noqa: E402

N, M = 30, 300
POINTS = np.array([0.25, 0.95])
DEGREES = (1, 3, 7)
LABEL = {1: "высокое смещение, малый разброс", 3: "малое смещение, малый разброс", 7: "малое смещение, большой разброс"}
centre = bv.truth(POINTS)

fig, axes = fk.subplots(1, 3, size=(12.6, 4.4), sharex=True, sharey=True)
for ax, d in zip(axes, DEGREES):
    pred = bv.predictions(bv.poly_fit(d), N, M, grid=POINTS)
    for r in (0.5, 1.0, 1.5, 2.0):
        ax.add_patch(Circle(centre, r, fill=False, ec=fk.P["ash"], lw=0.9))
    ax.scatter(pred[:, 0], pred[:, 1], s=14, color=fk.MODEL_C, alpha=0.55, linewidths=0, label="модель")
    mean = pred.mean(axis=0)
    ax.scatter(*mean, s=70, marker="X", color=fk.MODEL2_C, edgecolors="white", linewidths=0.8, zorder=5,
               label="среднее моделей")
    ax.scatter(*centre, s=90, marker="*", color=fk.ACCENT, zorder=6, label="истина")
    ax.set_xlim(-1.5, 3.5)
    ax.set_ylim(-2.8, 2.2)
    ax.set_aspect("equal")
    ax.set_title(f"степень {d}")
    ax.set_xlabel(f"предсказание в x = {fk.num(0.25, 2)}")
    ax.text(0.5, 0.02, LABEL[d], transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    print(d, "bias dist", round(float(np.linalg.norm(mean - centre)), 3), "std", np.round(pred.std(axis=0), 3))
axes[0].set_ylabel(f"предсказание в x = {fk.num(0.95, 2)}")
axes[0].legend(loc="upper right", fontsize=7)

fk.save(fig, fk.attachments(5) / "bv-targets.png")
