"""Empirical risk of one fixed model on growing samples against its expected risk.

Population: x ~ U(0, 1), y = 2x + N(0, 1). Model: f(x) = 1.5x, squared loss.
Expected risk: E(0.5x + eps)^2 = 0.25 * E[x^2] + 1 = 0.25 / 3 + 1 = 13/12.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)
RISK = 13 / 12


def draw(rng, n):
    x = rng.uniform(0, 1, n)
    return x, 2 * x + rng.normal(0, 1, n)


rng = np.random.default_rng(fk.SEED)
fig, (a, b) = fk.plt.subplots(1, 2, figsize=(9.6, 3.9), gridspec_kw=dict(width_ratios=[1, 1.15]))

# Left: one sample of n = 10 and the squared residuals the empirical risk averages.
x, y = draw(rng, 10)
grid = np.array([0, 1])
a.plot(grid, 2 * grid, color=fk.TEXT_2, lw=1, ls="--", label="истинная зависимость")
a.plot(grid, 1.5 * grid, color=fk.RED, lw=2, label="модель $f(x)=1.5x$")
a.vlines(x, 1.5 * x, y, color=fk.GRIDC, lw=1.2, zorder=2)
a.scatter(x, y, s=26, color=fk.BLUE, edgecolors="white", linewidths=0.6, zorder=3)
emp = np.mean((y - 1.5 * x) ** 2)
a.set_title(f"Выборка n = 10: $\\widehat R$ = {fk.num(emp, 2)}")
a.set_xlabel("x")
a.set_ylabel("y")
a.set_ylim(-2.6, 3.6)
a.legend(loc="upper left")

# Right: empirical risk of eight independent samples as n grows.
ns = np.unique(np.round(np.logspace(np.log10(5), np.log10(2000), 60)).astype(int))
for _ in range(8):
    xs, ys = draw(rng, ns[-1])
    loss = (ys - 1.5 * xs) ** 2
    b.plot(ns, [loss[:n].mean() for n in ns], color=fk.BLUE, lw=1.1, alpha=0.7)
b.axhline(RISK, color=fk.RED, lw=2, label="ожидаемый риск $R=13/12$")
b.set_xscale("log")
b.set_xlabel("размер выборки n")
b.set_ylabel("$\\widehat R_n$")
b.set_title("Восемь независимых выборок")
b.set_axisbelow(True)
b.grid(True, axis="y")
b.legend(loc="upper right")

fig.tight_layout()
fk.save(fig, OUT / "empirical-risk-convergence.png")
