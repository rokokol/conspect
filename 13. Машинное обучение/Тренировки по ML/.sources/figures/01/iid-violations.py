"""Two ways to break i.i.d.: a sample from another distribution, and observations that depend on each other in time."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)

rng = np.random.default_rng(fk.SEED)
fig, (a, b) = fk.plt.subplots(1, 2, figsize=(9.6, 3.8))

# Left: one generator, plus an object from a different one (non-identical distribution).
mass = rng.normal(0, 0.55, 80)
coat = 2.0 + 0.9 * mass + rng.normal(0, 0.35, 80)
a.scatter(mass, coat, s=22, color=fk.BLUE, edgecolors="white", linewidths=0.6, zorder=3)
a.scatter([2.6], [5.4], s=70, color=fk.RED, edgecolors="white", linewidths=0.8, zorder=3)
a.annotate("белый медведь:\nдругие условия,\nдругой закон", xy=(2.6, 5.4), xytext=(0.9, 5.0),
           fontsize=8.5, color=fk.RED, va="center", ha="left",
           arrowprops=dict(arrowstyle="->", color=fk.RED, lw=1.3))
a.annotate("млекопитающие\nЮжной Африки", xy=(-0.55, 1.65), xytext=(-2.0, 0.2),
           fontsize=8.5, color=fk.BLUE, va="center",
           arrowprops=dict(arrowstyle="->", color=fk.BLUE, lw=1.3))
a.set_xlabel("масса (станд.)")
a.set_ylabel("длина шерсти (станд.)")
a.set_title("Не одинаково распределены")
a.set_xlim(-2.4, 3.3)
a.set_ylim(-0.4, 6.0)

# Right: i.i.d. noise against a series with a trend, a season and a memory (AR(1) noise).
t = np.arange(120)
iid = rng.normal(0, 1, t.size)
memory = np.zeros(t.size)
for k in range(1, t.size):
    memory[k] = 0.8 * memory[k - 1] + 0.4 * rng.normal()
series = 0.03 * t + np.sin(2 * np.pi * t / 24) + memory
b.plot(t, series, color=fk.RED, lw=1.6, label="ряд: тренд, сезон, память")
b.plot(t, iid - 3.0, color=fk.BLUE, lw=1.2, label="i.i.d. шум")
b.axhline(-3.0, color=fk.TEXT_2, lw=0.8, ls="--")
b.set_xlabel("время")
b.set_yticks([])
b.set_title("Зависимость во времени")
b.legend(loc="upper left")

fig.tight_layout()
fk.save(fig, OUT / "iid-violations.png")
