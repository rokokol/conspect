"""Explained variance of synthetic 10-dimensional data with a decaying spectrum: bars lambda_j and the cumulative share."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

N, D = 300, 10
rng = np.random.default_rng(11)
true_var = 6.0 * 0.55 ** np.arange(D)                      # decaying variances along hidden axes
q, _ = np.linalg.qr(rng.standard_normal((D, D)))           # random orthonormal basis mixes the axes
x = (rng.standard_normal((N, D)) * np.sqrt(true_var)) @ q.T
x = x - x.mean(axis=0)

_, rho, vt = np.linalg.svd(x, full_matrices=False)
lam = rho**2 / (N - 1)
share = np.cumsum(lam) / lam.sum()

c = x.T @ x / (N - 1)
assert np.allclose(np.sort(np.linalg.eigvalsh(c))[::-1], lam)
assert np.all(np.diff(lam) <= 0) and np.isclose(share[-1], 1.0)
assert np.isclose(lam.sum(), np.trace(c))
k = int(np.argmax(share >= 0.9)) + 1                       # fewest components keeping 90 %
assert share[k - 1] >= 0.9 > share[k - 2]
# the dropped part is the sum of the squared singular values of the tail
xk = (x @ vt[:k].T) @ vt[:k]
assert np.isclose(np.sum((x - xk) ** 2) / np.sum(x**2), 1 - share[k - 1])

j = np.arange(1, D + 1)
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.bar(j, lam, color=lafig.VECTOR, width=0.62, zorder=2)
ax.set_xlabel(r"номер компоненты $j$", color=lafig.INK)
ax.set_ylabel(r"$\lambda_j$", color=lafig.INK)
ax.set_xticks(j)
ax.tick_params(colors=lafig.INK)
ax2 = ax.twinx()
ax2.plot(j, share, color=lafig.HIGHLIGHT, lw=2.0, marker="o", ms=4.5, zorder=3)
ax2.axhline(0.9, color=lafig.MUTED, lw=1.2, ls="--", zorder=1)
ax2.plot([k], [share[k - 1]], marker="o", ms=9, mfc="none", mec=lafig.INK, mew=2.0, ls="none", zorder=4)
ax2.set_ylim(0, 1.05)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
ax2.set_ylabel("накопленная доля", color=lafig.INK)
ax2.tick_params(colors=lafig.INK)
for a in (ax, ax2):
    for side in a.spines.values():
        side.set_color(lafig.AUX)

fig.legend(handles=[
    Line2D([0], [0], color=lafig.VECTOR, lw=8, label=r"дисперсия $\lambda_j$"),
    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.0, marker="o", ms=4.5, label=r"доля $\frac{\lambda_1+\dots+\lambda_j}{\lambda_1+\dots+\lambda_d}$"),
    Line2D([0], [0], color=lafig.MUTED, lw=1.2, ls="--", label="порог 90 %"),
    Line2D([0], [0], marker="o", ms=9, mfc="none", mec=lafig.INK, mew=2.0, ls="none", label="наименьшее $k$ над порогом"),
], loc="lower center", ncol=2, frameon=False)
fig.tight_layout(rect=(0, 0.16, 1, 1))

print("k90 =", k, "share =", share.round(3))
lafig.save(fig, 12, "pca-variance")
