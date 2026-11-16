"""Level sets of the loss and the L2 disc against the L1 diamond: where the constrained minimum lands."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

C = np.array([2.1, 0.6])                  # the unregularised optimum (OLS)
A = np.array([[2.0, 0.3], [0.3, 1.0]])    # shape of the MSE level sets
R = 1.0                                   # radius of both balls


def loss(w):
    d = w - C
    return np.einsum("...i,ij,...j->...", d, A, d)


def boundary(p, n=4000):
    t = np.linspace(0, 2 * np.pi, n)
    if p == 2:
        return R * np.c_[np.cos(t), np.sin(t)]
    u = np.cos(t), np.sin(t)
    s = abs(u[0]) + abs(u[1])
    return R * np.c_[u[0] / s, u[1] / s]


g = np.linspace(-1.6, 3.2, 400)
xx, yy = np.meshgrid(g, np.linspace(-1.5, 2.1, 400))
zz = loss(np.stack([xx, yy], -1))

fig, axes = fk.subplots(1, 2, size=(9.4, 4.4))
for ax, p, title in ((axes[0], 2, "Штраф $\\|w\\|_2^2$: круг"), (axes[1], 1, "Штраф $\\|w\\|_1$: ромб")):
    b = boundary(p)
    best = b[np.argmin(loss(b))]
    lvl = float(loss(best))
    ax.contour(xx, yy, zz, levels=np.linspace(0, 9, 13)[1:], colors=fk.tint(fk.BLUE, 0.35), linewidths=1)
    ax.contour(xx, yy, zz, levels=[lvl], colors=fk.RED, linewidths=2)
    ax.add_patch(Polygon(b, closed=True, fc=fk.tint(fk.CATEGORICAL[1], 0.7), ec=fk.CATEGORICAL[1],
                         lw=2, alpha=0.85, zorder=2))
    ax.scatter(*C, color=fk.BLUE, s=45, zorder=4)
    ax.annotate("МНК", C, xytext=(8, 6), textcoords="offset points", color=fk.BLUE)
    ax.scatter(*best, color=fk.RED, s=60, zorder=5, edgecolor="white")
    ax.annotate("решение со штрафом", best, xytext=(25, -80), textcoords="offset points", color=fk.RED,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=6,
                arrowprops=dict(arrowstyle="->", color=fk.RED))
    ax.axhline(0, color=fk.TEXT_2, lw=0.8)
    ax.axvline(0, color=fk.TEXT_2, lw=0.8)
    ax.set_title(title)
    ax.set_xlabel("$w_1$")
    ax.set_xlim(-1.6, 3.2)
    ax.set_ylim(-1.5, 2.1)
    ax.set_aspect("equal")
    print(title, best.round(3))
axes[0].set_ylabel("$w_2$")
fig.tight_layout()
fk.save(fig, OUT / "reg-geometry-l1-l2.png")
