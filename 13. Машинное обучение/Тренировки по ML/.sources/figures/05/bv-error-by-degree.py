"""Expected error of a polynomial regression split into noise, bias^2 and variance, by degree; and its shift with the sample size.

Every number is a simulation: M fresh training samples per (degree, n). The dots are the error measured directly on fresh
test pairs, so they check that bias^2 + variance + sigma^2 is the error and not just a sum drawn by hand.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bv_common as bv  # noqa: E402
import figkit as fk  # noqa: E402

M = 1000
DEGREES = list(range(0, 10))
FLOOR = 1e-4
SIGMA2 = bv.SIGMA ** 2

fig, axes = fk.subplots(1, 2, size=(11.2, 4.2))

ax = axes[0]
N = 30
rows = []
for d in DEGREES:
    pred = bv.predictions(bv.poly_fit(d), N, M)
    b, v = bv.decompose(pred)
    rows.append((b, v, bv.test_error(pred)))
b, v, t = (np.array(c) for c in zip(*rows))
ax.plot(DEGREES, np.maximum(b, FLOOR), color=fk.MODEL_C, marker="o", ms=4, label="bias²")
ax.plot(DEGREES, v, color=fk.MODEL2_C, marker="o", ms=4, label="variance")
ax.axhline(SIGMA2, color=fk.TEXT_2, ls="--", lw=1.2, label=f"шум σ² = {fk.num(SIGMA2, 4)}")
ax.plot(DEGREES, b + v + SIGMA2, color=fk.TEXT, lw=2.2, label="bias² + variance + σ²")
ax.scatter(DEGREES, t, s=34, facecolors="none", edgecolors=fk.TEST_C, linewidths=1.4, zorder=5,
           label="ошибка на свежих парах")
ax.set_yscale("log")
ax.set_ylim(FLOOR, 30)
ax.text(0.98, 0.03, "bias² ниже 10⁻⁴ (и оценка ниже нуля) прижат к нижней границе", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=6.5, color=fk.TEXT_2)
ax.set_xticks(DEGREES)
ax.set_xlabel("степень многочлена")
ax.set_ylabel("ошибка, логарифмическая шкала")
ax.set_title(f"слагаемые ошибки, n = {N}")
ax.grid(True, axis="y")
ax.legend(loc="upper left", fontsize=7)
for d, bb, vv, tt in zip(DEGREES, b, v, t):
    print("n", N, d, round(bb, 4), round(vv, 4), round(tt, 4), round(bb + vv + SIGMA2, 4))

ax = axes[1]
for n, color in zip((15, 30, 150), fk.CATEGORICAL):
    tot = []
    for d in DEGREES:
        pred = bv.predictions(bv.poly_fit(d), n, M)
        bb, vv = bv.decompose(pred)
        tot.append(bb + vv + SIGMA2)
    ax.plot(DEGREES, tot, color=color, marker="o", ms=4, label=f"n = {n}")
    print("total n", n, [round(x, 3) for x in tot])
ax.axhline(SIGMA2, color=fk.TEXT_2, ls="--", lw=1.2)
ax.set_yscale("log")
ax.set_ylim(0.04, 30)
ax.set_xticks(DEGREES)
ax.set_xlabel("степень многочлена")
ax.set_title("полная ошибка при разном объёме выборки")
ax.grid(True, axis="y")
ax.legend(loc="upper left", fontsize=7)

fk.save(fig, fk.attachments(5) / "bv-error-by-degree.png")
