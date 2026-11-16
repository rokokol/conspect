"""Spectra of the bidiagonal 10x10 matrix A and of A_eps with one element eps in position (10, 1): the eigenvalue problem of a non-Hermitian matrix is unstable."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

N = 10
EPS = 1e-5
A = np.diag(np.arange(N, 0, -1.0)) + 10.0 * np.diag(np.ones(N - 1), 1)
A_eps = A.copy()
A_eps[N - 1, 0] = EPS

ev = np.linalg.eigvals(A)
ev_eps = np.linalg.eigvals(A_eps)

# det A_eps = 10! - eps * 10^9, and the roots solve prod(k - x) = eps * 10^9
assert np.allclose(np.sort(ev.real), np.arange(1, N + 1))
assert np.isclose(np.linalg.det(A_eps), math.factorial(N) - EPS * 1e9)
for z in ev_eps:
    assert abs(np.prod(np.arange(1, N + 1) - z) - EPS * 1e9) < 1e-3 * EPS * 1e9

# on [3, 8] the product stays below the constant eps * 10^9, so no root of A_eps is real there
grid = np.linspace(3, 8, 5001)
assert np.abs(np.prod(np.arange(1, N + 1)[:, None] - grid, axis=0)).max() < 2.1e3 < EPS * 1e9
assert not np.any((abs(ev_eps.imag) < 1e-9) & (ev_eps.real > 3) & (ev_eps.real < 8))

fig, ax = plt.subplots(figsize=(7.6, 3.6))
ax.axhline(0, color=lafig.AUX, lw=0.8, zorder=0)
ax.scatter(ev.real, ev.imag, s=70, facecolors="none", edgecolors=lafig.VECTOR, linewidths=1.8,
           marker="o", label=r"$\sigma(A)$", zorder=3)
ax.scatter(ev_eps.real, ev_eps.imag, s=36, color=lafig.HIGHLIGHT,
           marker="s", label=r"$\sigma(A_\varepsilon)$, $\varepsilon=10^{-5}$", zorder=4)
ax.set_xticks(range(0, N + 2))
ax.set_yticks([-1, 0, 1])
ax.set_xlim(-0.4, N + 1.4)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect("equal")
ax.set_xlabel(r"$\operatorname{Re}\lambda$", color=lafig.INK)
ax.set_ylabel(r"$\operatorname{Im}\lambda$", color=lafig.INK)
ax.legend(loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.18))
lafig.save(fig, 12, "spectrum_instability")
