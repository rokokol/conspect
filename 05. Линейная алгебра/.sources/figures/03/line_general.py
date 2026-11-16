"""The general equation a x1 + b x2 + c = 0: the normal (a, b), the intercepts and the slope."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

a_, b_, c_ = 2.0, 3.0, -6.0           # 2 x1 + 3 x2 - 6 = 0
x1_cut = -c_ / a_                      # 3
x2_cut = -c_ / b_                      # 2
k = -a_ / b_
n = np.array([a_, b_]) / np.hypot(a_, b_)

fig, ax = plt.subplots(figsize=(5.6, 4.2))
geo2d.new_axes(ax, (-1.6, 4.4), (-1.0, 3.0))
direction = np.array([b_, -a_])
geo2d.line(ax, (x1_cut, 0), direction, (4.6, 1.2), lafig.VECTOR, lw=2.0)
for p in ((x1_cut, 0), (0, x2_cut)):
    assert np.isclose(a_ * p[0] + b_ * p[1] + c_, 0)
    geo2d.dot(ax, p, lafig.HIGHLIGHT)
mid = np.array([x1_cut / 2, x2_cut / 2])
geo2d.arrow(ax, mid, 1.3 * n, lafig.IMAGE, lw=2.6)
geo2d.square(ax, mid, n, direction, 0.14)
ax.text(*(mid + 1.3 * n + np.array([0.12, 0.05])), r"$(a,b)$", color=lafig.INK, ha="left", va="bottom")
ax.text(x1_cut, -0.15, r"$-\dfrac{c}{a}$", color=lafig.INK, ha="center", va="top")
ax.text(0.1, x2_cut + 0.2, r"$-\dfrac{c}{b}$", color=lafig.INK, ha="left", va="bottom")
ax.text(1.5, 0.3, r"$k=-\dfrac{a}{b}$", color=lafig.INK, ha="left", va="center")

lafig.save(fig, 3, "line_general")
