"""The explanation of one point at different kernel widths: same black box, same point, same 500 perturbations.

Only sigma changes. n_eff = (sum w)^2 / sum w^2 is the effective number of neighbours.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from lime_common import (angle, black_box, boundary_segment, explained_point, gradient, kernel, local_fit,  # noqa: E402
                         proba, sample)

SIGMAS = [0.1, 0.25, 0.5, 1.0, 3.0]
N, HALF = 500, 1.3
model, params, (Xtr, Xte, ytr, yte) = black_box()
f = proba(model)
x = explained_point(f, Xte)
Z = sample(x, N, np.random.default_rng(fk.SEED))
grad = gradient(f, x)

fig, axes = fk.subplots(1, len(SIGMAS), size=(3.1 * len(SIGMAS), 3.5))
box = (x[0] - HALF, x[0] + HALF, x[1] - HALF, x[1] + HALF)
for ax, sigma in zip(axes, SIGMAS):
    w = kernel(Z, x, sigma)
    a, c, r2 = local_fit(f, x, Z, w)
    fk.plot_decision(ax, model, Xtr, ytr, show_points=False, scores=False)
    ax.scatter(Z[:, 0], Z[:, 1], s=3 + 60 * w, color=fk.TEXT_2, alpha=0.5, edgecolor="white", linewidths=0.25,
               zorder=3)
    ax.scatter(*x, marker="*", s=170, color=fk.ACCENT, edgecolor="white", linewidths=0.8, zorder=6)
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    xs, ys = boundary_segment(a, c, x, box)
    ax.plot(xs, ys, color=fk.MODEL2_C, lw=2.4, zorder=5)
    n_eff = w.sum() ** 2 / (w**2).sum()
    ax.set_title(f"$\\sigma={fk.num(sigma, None, math=True)}$\n$n_{{eff}}={fk.num(n_eff, 0, math=True)}$, угол к $\\nabla f$ {fk.num(angle(c, grad), 0)}°", fontsize=8.5)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "lime-width-grid.png")
for sigma in SIGMAS:
    w = kernel(Z, x, sigma)
    a, c, r2 = local_fit(f, x, Z, w)
    print(sigma, "n_eff", round(w.sum() ** 2 / (w**2).sum(), 1), "w", np.round(c, 3), "angle", round(angle(c, grad), 1),
          "R2w", round(r2, 3))
