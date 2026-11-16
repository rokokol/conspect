"""симм-геометрия.png: the slab, its axes and the step profile n(x)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

fig, (ax, an) = plt.subplots(
    1, 2, figsize=(8.4, 3.6), sharey=True, gridspec_kw={"width_ratios": [2.3, 1], "wspace": 0.06}
)

# Left: the cross-section in the (z, x) plane
L = 10
ax.add_patch(Rectangle((0, -3), L, 2, color=mffig.CLADDING, lw=0))
ax.add_patch(Rectangle((0, 3 - 2), L, 2, color=mffig.CLADDING, lw=0))
ax.add_patch(Rectangle((0, -1), L, 2, color=mffig.CORE, lw=0))
for xv in (-1, 1):
    ax.plot([0, L], [xv, xv], color=mffig.MUTED, lw=1.2, ls="--")
ax.text(0.4, 2, r"оболочка, $n_2$", va="center", color=mffig.INK)
ax.text(0.4, -2, r"оболочка, $n_2$", va="center", color=mffig.INK)
ax.text(0.4, 0, r"сердцевина, $n_1>n_2$", va="center", color=mffig.INK)
ax.annotate("", xy=(8.6, 1), xytext=(8.6, -1),
            arrowprops=dict(arrowstyle="<->", color=mffig.INK, lw=1.2))
ax.text(8.8, 0, r"$2d$", va="center", color=mffig.INK)
ax.annotate("", xy=(L - 0.3, 0.55), xytext=(5.2, 0.55),
            arrowprops=dict(arrowstyle="-|>", color=mffig.MODE, lw=1.8))
ax.text(7.6, 0.2, r"$\beta$", ha="center", va="center", color=mffig.INK)
ax.set_xlim(0, L)
ax.set_ylim(-3, 3)
ax.set_xlabel(r"$z$, направление распространения")
ax.set_ylabel(r"$x$")
ax.set_xticks([])
ax.set_yticks([-1, 0, 1], [r"$-d$", "0", r"$d$"])

# Right: the index profile
an.fill_betweenx([-3, -1], 0, 1, color=mffig.CLADDING)
an.fill_betweenx([1, 3], 0, 1, color=mffig.CLADDING)
an.fill_betweenx([-1, 1], 0, 1, color=mffig.CORE)
an.step([0.35, 0.35, 1, 1, 0.35, 0.35], [-3, -1, -1, 1, 1, 3], color=mffig.MODE, lw=2)
an.plot([0.35, 0.35], [-3, -1], color=mffig.MODE, lw=2)
an.set_xlim(0, 1)
an.set_xticks([0.35, 1], [r"$n_2$", r"$n_1$"])
an.set_xlabel(r"$n(x)$")
an.tick_params(left=False)

mffig.save(fig, 6, "симм-геометрия")
