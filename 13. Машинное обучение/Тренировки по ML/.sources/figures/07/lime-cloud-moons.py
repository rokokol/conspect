"""LIME on moons: the cloud of perturbations around one point, the local line, and its coefficients against the model's gradient.

Kernel width sigma = 0.5, 400 perturbations with tau = 0.8, see lime_common.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from lime_common import (TAU, black_box, boundary_segment, explained_point, gradient, kernel, local_fit,  # noqa: E402
                         proba, sample)

SIGMA, N = 0.5, 400
model, params, (Xtr, Xte, ytr, yte) = black_box()
f = proba(model)
x = explained_point(f, Xte)
rng = np.random.default_rng(fk.SEED)
Z = sample(x, N, rng)
w = kernel(Z, x, SIGMA)
a, c, r2 = local_fit(f, x, Z, w)
grad = gradient(f, x)

fig, axes = fk.subplots(1, 3, size=(12.6, 4.0), gridspec_kw={"width_ratios": [1, 1, 0.8]})
for ax in axes[:2]:
    fk.plot_decision(ax, model, Xtr, ytr, show_points=False, scores=False)
    ax.scatter(Z[:, 0], Z[:, 1], s=4 + 70 * w, color=fk.TEXT_2, alpha=0.55, edgecolor="white", linewidths=0.3,
               zorder=3)
    ax.scatter(*x, marker="*", s=220, color=fk.ACCENT, edgecolor="white", linewidths=0.8, zorder=6)
axes[0].set_title("Облако возмущений и модель $f$", fontsize=9)
xlim = (x[0] - 1.0, x[0] + 1.0)
ylim = (x[1] - 1.0, x[1] + 1.0)
axes[1].set_xlim(*xlim)
axes[1].set_ylim(*ylim)
xs, ys = boundary_segment(a, c, x, (*xlim, *ylim))
axes[1].plot(xs, ys, color=fk.MODEL2_C, lw=2.4, zorder=5, label="граница локальной модели $g$")
axes[1].plot([], [], color=fk.TEXT, lw=1.2, label="граница модели $f$")
axes[1].legend(fontsize=7, loc="lower left")
axes[1].set_title("Окрестность точки и прямая $g=0{,}5$", fontsize=9)

ax = axes[2]
xs_ = np.arange(2)
ax.bar(xs_ - 0.19, c, 0.38, color=fk.MODEL2_C, label="коэффициенты LIME $w$")
ax.bar(xs_ + 0.19, grad, 0.38, color=fk.P["ash"], label="градиент $\\nabla f(x)$")
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.set_xticks(xs_, ["$x_1$", "$x_2$"])
ax.legend(fontsize=7, loc="best")
ax.grid(True, axis="y")
ax.set_title("Объяснение против градиента", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "lime-cloud-moons.png")

print("svm", params, "x", np.round(x, 3), "f(x)", round(float(f(x[None])[0]), 3))
print("n_eff", round(float(w.sum() ** 2 / (w**2).sum()), 1), "weighted R2", round(r2, 3))
print("w", np.round(c, 3), "grad", np.round(grad, 3), "intercept", round(a, 3))
