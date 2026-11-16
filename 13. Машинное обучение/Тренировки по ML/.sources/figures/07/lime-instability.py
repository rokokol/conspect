"""The same explanation drawn again and again: 30 independent clouds per panel, kernel width fixed at 0.5.

Only the number of perturbations changes. Each line is the 0.5 line of one local model; the right panel gives the spread
of the coefficient direction over 100 clouds.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from lime_common import (angle, black_box, boundary_segment, explained_point, kernel, local_fit, proba,  # noqa: E402
                         sample)

SIGMA, HALF = 0.5, 1.3
NS = [20, 100, 1000]
model, params, (Xtr, Xte, ytr, yte) = black_box()
f = proba(model)
x = explained_point(f, Xte)
box = (x[0] - HALF, x[0] + HALF, x[1] - HALF, x[1] + HALF)
rng = np.random.default_rng(fk.SEED)

fig, axes = fk.subplots(1, 4, size=(13.4, 3.6), gridspec_kw={"width_ratios": [1, 1, 1, 1.1]})
for ax, n in zip(axes[:3], NS):
    fk.plot_decision(ax, model, Xtr, ytr, show_points=False, scores=False)
    for _ in range(30):
        Z = sample(x, n, rng)
        a, c, _ = local_fit(f, x, Z, kernel(Z, x, SIGMA))
        xs, ys = boundary_segment(a, c, x, box)
        ax.plot(xs, ys, color=fk.MODEL2_C, lw=1.1, alpha=0.55, zorder=4)
    ax.scatter(*x, marker="*", s=170, color=fk.ACCENT, edgecolor="white", linewidths=0.8, zorder=6)
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.set_title(f"{n} возмущений", fontsize=9)

ns = np.array([10, 20, 50, 100, 200, 500, 1000, 3000])
spread, ref = [], None
Zbig = sample(x, 200000, np.random.default_rng(1))
_, ref, _ = local_fit(f, x, Zbig, kernel(Zbig, x, SIGMA))
for n in ns:
    angs = []
    for _ in range(100):
        Z = sample(x, n, rng)
        _, c, _ = local_fit(f, x, Z, kernel(Z, x, SIGMA))
        angs.append(angle(c, ref))
    spread.append((np.mean(angs), np.percentile(angs, 90)))
spread = np.array(spread)
ax = axes[3]
ax.plot(ns, spread[:, 0], "-o", color=fk.MODEL2_C, ms=4, label="средний")
ax.plot(ns, spread[:, 1], "--o", color=fk.TEXT_2, ms=4, label="90-й процентиль")
ax.set_xscale("log")
ax.set_xlabel("число возмущений $n$")
ax.set_ylabel("угол к пределу $n\\to\\infty$, градусы")
ax.legend(fontsize=7.5)
ax.grid(True)
ax.set_title("Разброс направления", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "lime-instability.png")
print("limit w", np.round(ref, 3))
for n, (m, p) in zip(ns, spread):
    print(f"n {n:5d} mean angle {m:5.1f} p90 {p:5.1f}")
