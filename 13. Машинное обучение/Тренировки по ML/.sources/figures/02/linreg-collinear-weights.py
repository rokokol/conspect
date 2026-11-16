"""OLS weights on a nearly collinear pair of features: blow-up with the gap shrinking, and the fixed sum."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
from collinear_demo import W_TRUE, ols, sample  # noqa: E402

OUT = fk.attachments(2)

gaps = np.logspace(-4, 0, 50)
W = np.array([ols(*sample(fk.SEED, g)) for g in gaps])

fig, axes = fk.subplots(1, 2, size=(9.4, 3.9))

ax = axes[0]
ax.plot(gaps, W[:, 1], color=fk.CATEGORICAL[0], label="$\\hat w_2$")
ax.plot(gaps, W[:, 2], color=fk.CATEGORICAL[1], label="$\\hat w_3$")
ax.plot(gaps, W[:, 1] + W[:, 2], color=fk.TEXT, lw=1.6, ls="--", label="$\\hat w_2+\\hat w_3$")
ax.axhline(W_TRUE[1] + W_TRUE[2], color=fk.TEXT_2, lw=1, ls=":")
ax.text(1.0, W_TRUE[1] + W_TRUE[2] + 6, "истинная сумма", ha="right", color=fk.TEXT_2, fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("зазор между $x_2$ и $x_3$ (чем меньше, тем ближе к копии)")
ax.set_ylabel("оценка веса")
ax.set_title("Веса против зазора")
ax.grid(True, axis="y")
ax.legend(loc="lower right")

ax = axes[1]
gap = 0.001
pts = np.array([ols(*sample(1000 + s, gap))[1:] for s in range(300)])
line = np.array([pts.min() - 5, pts.max() + 5])
ax.plot(line, (W_TRUE[1] + W_TRUE[2]) - line, color=fk.RED, lw=1.2, ls="--", zorder=1,
        label="$w_2+w_3=$ истинная сумма")
ax.scatter(pts[:, 0], pts[:, 1], s=14, color=fk.BLUE, alpha=0.8, edgecolor="none", zorder=3)
ax.text(0.03, 0.04, f"$\\hat w_2$: $\\sigma \\approx {pts[:, 0].std():.0f}$, размах {np.ptp(pts[:, 0]):.0f}",
        transform=ax.transAxes, fontsize=8)
ax.scatter([W_TRUE[1]], [W_TRUE[2]], color=fk.RED, s=60, zorder=4, edgecolor="white")
ax.annotate("истина", (W_TRUE[1], W_TRUE[2]), xytext=(10, 22), textcoords="offset points",
            color=fk.RED, arrowprops=dict(arrowstyle="->", color=fk.RED))
ax.set_xlabel("$\\hat w_2$")
ax.set_ylabel("$\\hat w_3$")
ax.set_title("300 перевыборок шума, зазор $10^{-3}$")
ax.set_aspect("equal", adjustable="datalim")
ax.grid(True)
ax.legend(loc="upper right")

fig.tight_layout()
fk.save(fig, OUT / "linreg-collinear-weights.png")
