"""Polynomials of degree 1, 3 and 15 on the same reg1d points: underfit, fit, overfit."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
import overfit_common as oc  # noqa: E402

DEGREES = (1, 3, 15)
TITLES = {1: "недообучение", 3: "подходящая модель", 15: "переобучение"}

grid = np.linspace(0, 1, 400)
fig, axes = fk.subplots(1, 3, size=(10.5, 3.3), sharey=True)
for ax, d in zip(axes, DEGREES):
    m = oc.fit(d)
    ax.plot(grid, np.sin(2 * np.pi * grid), color=fk.TEXT_2, lw=1, ls="--", label="истинный $\\sin 2\\pi x$")
    ax.plot(grid, m(grid), color=fk.MODEL_C, lw=2, label=f"полином степени {d}")
    ax.scatter(oc.x_tr, oc.y_tr, s=22, color=fk.TRAIN_C, edgecolors="white", linewidths=0.8, zorder=3, label="train")
    ax.scatter(oc.x_te, oc.y_te, s=22, facecolors="white", edgecolors=fk.TEST_C, linewidths=1.2, zorder=3, label="test")
    ax.set_ylim(-1.8, 1.8)
    ax.set_xlabel("$x$")
    ax.set_title(f"степень {d}: {TITLES[d]}", fontsize=10)
    tr, te = oc.mse(m, oc.x_tr, oc.y_tr), oc.mse(m, oc.x_te, oc.y_te)
    ax.text(0.03, 0.03, f"MSE train {fk.num(tr, 3)}\nMSE test {fk.num(te, 3)}", transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8, color=fk.TEXT, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    print(d, "train", round(tr, 4), "test", round(te, 4))
axes[0].set_ylabel("$y$")
axes[0].legend(loc="upper right", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "overfit-poly-grid.png")
