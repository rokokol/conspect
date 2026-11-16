"""Principal components of a planar cloud: the axes w^1, w^2 of lengths 2 sqrt(lambda_j) and the scatter ellipse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from pca_data import cloud  # noqa: E402

x, c, lam, w = cloud()

# SVD of the data gives the same components: w^j = e^j, lambda_j = rho_j^2 / (N - 1)
_, rho, vt = np.linalg.svd(x, full_matrices=False)
assert np.allclose(rho**2 / (len(x) - 1), lam)
assert np.allclose(np.abs(vt @ w), np.eye(2), atol=1e-8)

# variance of the projections on w^j equals lambda_j
for j in range(2):
    assert np.isclose(np.var(x @ w[:, j], ddof=1), lam[j])

# ellipse (C^{-1} x, x) = 4 has semi-axes 2 sqrt(lambda_j) along w^j
t = np.linspace(0, 2 * np.pi, 400)
ell = (w * (2 * np.sqrt(lam))) @ np.vstack([np.cos(t), np.sin(t)])
assert np.allclose(np.einsum("ik,ij,jk->k", ell, np.linalg.inv(c), ell), 4.0)

fig, ax = plt.subplots(figsize=(6.0, 4.6))
ax.axhline(0, color=lafig.AUX, lw=0.8, zorder=0)
ax.axvline(0, color=lafig.AUX, lw=0.8, zorder=0)
ax.scatter(x[:, 0], x[:, 1], s=16, color=lafig.VECTOR, alpha=0.75, linewidths=0, zorder=2)
ax.plot(ell[0], ell[1], color=lafig.MUTED, lw=1.3, ls="--", zorder=3)
for j in range(2):
    tip = 2 * np.sqrt(lam[j]) * w[:, j]
    ax.annotate("", xy=tip, xytext=(0, 0), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=lafig.HIGHLIGHT, lw=2.2, shrinkA=0, shrinkB=0))
    off = 0.45 * w[:, j]
    ax.text(tip[0] + off[0], tip[1] + off[1], rf"$w^{j + 1}$", color=lafig.INK, ha="center", va="center")
ax.set_aspect("equal")
ax.set_xlabel(r"$x_1$", color=lafig.INK)
ax.set_ylabel(r"$x_2$", color=lafig.INK)
ax.tick_params(colors=lafig.INK)
for side in ax.spines.values():
    side.set_color(lafig.AUX)

ax.legend(handles=[
    Line2D([0], [0], marker="o", color="none", markerfacecolor=lafig.VECTOR, markersize=5, label="объекты"),
    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.2, label=r"главные компоненты, длина $2\sqrt{\lambda_j}$"),
    Line2D([0], [0], color=lafig.MUTED, lw=1.3, ls="--", label=r"эллипс рассеяния $(C^{-1}x,x)=4$"),
], loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1, frameon=False)

lafig.save(fig, 12, "pca-cloud")
