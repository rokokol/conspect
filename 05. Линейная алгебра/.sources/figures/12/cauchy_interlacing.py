"""Eigenvalues of the leading principal submatrices of a symmetric 5x5 matrix: the spectra of consecutive orders interlace."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

A = np.array([
    [4, 2, 2, 1, -2],
    [2, 5, 0, 2, 2],
    [2, 0, 4, -2, -1],
    [1, 2, -2, 4, 2],
    [-2, 2, -1, 2, 4],
], dtype=float)
N = len(A)
spectra = [np.linalg.eigvalsh(A[:k, :k]) for k in range(1, N + 1)]

for k in range(1, N):
    small, big = spectra[k - 1], spectra[k]
    assert np.all(big[:-1] <= small) and np.all(small <= big[1:])

fig, ax = plt.subplots(figsize=(7.6, 3.6))
for k, ev in enumerate(spectra, start=1):
    ax.hlines(k, ev.min() - 0.6, ev.max() + 0.6, color=lafig.AUX, lw=0.8, zorder=0)
    ax.scatter(ev, np.full_like(ev, k), s=55, color=lafig.VECTOR, zorder=3)
for k in range(1, N):
    small, big = spectra[k - 1], spectra[k]
    for i, x in enumerate(small):
        ax.plot([big[i], x, big[i + 1]], [k + 1, k, k + 1], color=lafig.HIGHLIGHT, lw=0.9, alpha=0.6, zorder=1,
                label="число порядка $k$ между соседними числами порядка $k+1$" if (k, i) == (1, 0) else None)
ax.set_yticks(range(1, N + 1))
ax.set_yticklabels([rf"$A_{k}$" for k in range(1, N + 1)])
ax.set_ylim(0.5, N + 0.5)
ax.invert_yaxis()
ax.set_xlabel(r"$\lambda$", color=lafig.INK)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
lafig.save(fig, 12, "cauchy_interlacing")
