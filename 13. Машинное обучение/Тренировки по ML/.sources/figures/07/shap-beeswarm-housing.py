"""Beeswarm (summary plot) of Shapley values over 800 held-out objects of California Housing.

One dot is one object and one feature; the horizontal position is its Shapley value, the colour is the feature's value
(percentile rank among the 800), dots of a feature are spread vertically where they crowd. Features sorted by mean |phi|.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from shap_cal import explain, fit  # noqa: E402

model, depth, X, y, Xtr, Xte, ytr, yte, names = fit()
rng = np.random.default_rng(fk.SEED)
idx = rng.choice(len(Xte), 800, replace=False)
S = Xte[idx]
v, phi = explain(model, S)
assert np.allclose(v[0, 0] + phi.sum(1), model.predict(S))

order = np.argsort(np.abs(phi).mean(0))[::-1]
fig, ax = fk.subplots(1, 1, size=(8.2, 4.8))
bins = np.linspace(phi.min(), phi.max(), 60)
for row, j in enumerate(order):
    p = phi[:, j]
    b = np.digitize(p, bins)
    off = np.zeros_like(p)
    step = 0.84 / np.bincount(b).max()
    for k in np.unique(b):
        m = np.flatnonzero(b == k)
        rank = np.argsort(rng.permutation(len(m)))
        off[m] = (rank - (len(m) - 1) / 2) * step
    pct = S[:, j].argsort().argsort() / (len(S) - 1)
    sc = ax.scatter(p, row + off, c=pct, cmap="ddlc_div", vmin=0, vmax=1, s=9, edgecolor="none", zorder=3)
ax.axvline(0, color=fk.TEXT_2, lw=0.8)
ax.set_yticks(range(len(order)), [names[j] for j in order], fontsize=8.5)
ax.invert_yaxis()
ax.set_xlabel("значение Шепли: сдвиг предсказания (цена, сотни тысяч долларов)")
ax.grid(True, axis="x")
cb = fig.colorbar(sc, ax=ax, ticks=[0, 1], pad=0.02, fraction=0.04)
cb.ax.set_yticklabels(["низкое", "высокое"], fontsize=8)
cb.set_label("значение признака", fontsize=8)
ax.set_title("Сводка по 800 объектам отложенной части", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "shap-beeswarm-housing.png")

print("mean |phi|", {names[j]: round(float(np.abs(phi[:, j]).mean()), 3) for j in order})
for j in order:
    c = np.corrcoef(S[:, j], phi[:, j])[0, 1]
    print(f"{names[j]:11s} corr(value, phi) {c:+.2f} phi range [{phi[:, j].min():+.2f}, {phi[:, j].max():+.2f}]")
