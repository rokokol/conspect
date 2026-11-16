"""симм-число-мод.png: the number of guided modes against the half-thickness d."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

n1, n2, lam = 3.5, 1.45, 1.55  # lambda in micrometres, d comes out in micrometres
k0na = 2 * np.pi / lam * np.sqrt(n1**2 - n2**2)
d = np.linspace(1e-6, 1.0, 20000)
M = np.floor(2 * k0na * d / np.pi) + 1

fig, ax = plt.subplots(figsize=(7.6, 3.8))
ax.step(d, M, where="post", color=mffig.MODE, lw=2)
cuts = np.arange(1, 9) * np.pi / (2 * k0na)
ax.plot(cuts, np.arange(2, 10), "o", color=mffig.HIGHLIGHT, mec=mffig.INK, ms=6, zorder=5)
ax.set_xlim(0, 1)
ax.set_ylim(0, 10)
ax.set_xlabel(r"полутолщина $d$, мкм")
ax.set_ylabel(r"$M$")
ax.set_yticks(range(0, 11, 1))
ax.legend(handles=[
    Line2D([], [], color=mffig.MODE, lw=2, label=r"$M=\lfloor 2V/\pi\rfloor+1$"),
    Line2D([], [], marker="o", ls="", color=mffig.HIGHLIGHT, mec=mffig.INK, label="появление моды"),
], loc="upper left", frameon=False)

mffig.save(fig, 6, "симм-число-мод")
