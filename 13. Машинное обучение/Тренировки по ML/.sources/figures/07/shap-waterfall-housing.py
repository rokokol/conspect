"""Waterfall of one prediction on California Housing: from the mean prediction to f(x), feature by feature.

Object: row 0 of the data set (the values match the lecture slide). Model and Shapley values come from shap_cal.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from shap_cal import explain, fit  # noqa: E402

model, depth, X, y, Xtr, Xte, ytr, yte, names = fit()
x = X[:1]
v, phi = explain(model, x)
phi = phi[0]
base, pred = v[0, 0], v[-1, 0]
assert np.isclose(pred, model.predict(x)[0]) and np.isclose(base + phi.sum(), pred)

order = np.argsort(-np.abs(phi))
fig, ax = fk.subplots(1, 1, size=(7.4, 4.2))
run = base
for row, j in enumerate(order):
    c = fk.RED if phi[j] > 0 else fk.BLUE
    ax.barh(row, phi[j], left=run, height=0.62, color=c, edgecolor="white")
    ax.text(max(run, run + phi[j], pred) + 0.06, row, fk.num(phi[j], "+.2f"), va="center", fontsize=8, color=fk.TEXT)
    run += phi[j]
ax.axvline(base, color=fk.TEXT_2, lw=0.9, ls=":")
ax.axvline(pred, color=fk.TEXT, lw=0.9, ls=":")
ax.set_yticks(range(len(order)), [f"{names[j]} = {fk.num(round(x[0, j], 3), None)}" for j in order], fontsize=8)
ax.invert_yaxis()
ax.set_xlim(min(base, pred, base + np.cumsum(phi[order]).min()) - 0.25, max(base, pred) + 0.6)
ax.set_xlabel(f"предсказание цены; $\\mathsf{{E}}f={fk.num(base, 3, math=True)}$ слева, $f(x)={fk.num(pred, 3, math=True)}$ справа")
ax.grid(True, axis="x")
ax.set_title("От среднего предсказания к предсказанию", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "shap-waterfall-housing.png")

print("depth", depth, "test R2", round(model.score(Xte, yte), 3), "target", y[0])
print("E f", round(base, 3), "f(x)", round(pred, 3))
for j in order:
    print(f"{names[j]:11s} = {x[0, j]:9.3f} phi {phi[j]:+.3f}")
