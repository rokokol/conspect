"""Kernel width against the explanation: the angle to the model's gradient (systematic error) and the spread over resamplings.

For every sigma, 60 independent clouds of 500 perturbations around the same point; each cloud gives one coefficient vector.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from lime_common import angle, black_box, explained_point, gradient, kernel, local_fit, proba, sample  # noqa: E402

SIGMAS = np.geomspace(0.05, 4, 14)
N, REPEATS = 500, 60
model, params, (Xtr, Xte, ytr, yte) = black_box()
f = proba(model)
x = explained_point(f, Xte)
grad = gradient(f, x)
rng = np.random.default_rng(fk.SEED)
clouds = [sample(x, N, rng) for _ in range(REPEATS)]

mean_ang, std_ang, n_eff = [], [], []
for s in SIGMAS:
    angs, effs = [], []
    for Z in clouds:
        w = kernel(Z, x, s)
        _, c, _ = local_fit(f, x, Z, w)
        angs.append(angle(c, grad))
        effs.append(w.sum() ** 2 / (w**2).sum())
    mean_ang.append(np.mean(angs))
    std_ang.append(np.std(angs))
    n_eff.append(np.mean(effs))
mean_ang, std_ang, n_eff = map(np.array, (mean_ang, std_ang, n_eff))

fig, (a0, a1) = fk.subplots(1, 2, size=(9.6, 3.6))
a0.plot(SIGMAS, mean_ang, "-o", color=fk.MODEL2_C, ms=4, label="средний угол к $\\nabla f(x)$")
a0.fill_between(SIGMAS, np.maximum(mean_ang - std_ang, 0), mean_ang + std_ang, color=fk.MODEL2_C, alpha=0.2,
                label="± разброс по 60 облакам")
a0.set_xscale("log")
a0.set_xlabel("ширина ядра $\\sigma$")
a0.set_ylabel("угол, градусы")
a0.legend(fontsize=7.5)
a0.grid(True)
a0.set_title("Угол к градиенту растёт с шириной ядра", fontsize=9)
a1.plot(SIGMAS, n_eff, "-o", color=fk.MODEL_C, ms=4)
a1.set_xscale("log")
a1.set_yscale("log")
a1.set_xlabel("ширина ядра $\\sigma$")
a1.set_ylabel("$n_{eff}$ из 500")
a1.grid(True)
a1.set_title("Сколько соседей реально считается", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "lime-width-curve.png")
for s, m, d, e in zip(SIGMAS, mean_ang, std_ang, n_eff):
    print(f"sigma {s:.3f} mean angle {m:5.1f} std {d:5.1f} n_eff {e:6.1f}")
