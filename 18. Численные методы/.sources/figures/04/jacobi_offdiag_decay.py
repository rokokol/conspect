"""Off-diagonal sum of the classical Jacobi method against the bound rho^p S_0 of Lemma 1, and the eigenvalue error."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

A = np.array([[4, 1, 2, 0], [1, 3, 0, 1], [2, 0, 5, 1], [0, 1, 1, 2]], float)
n = len(A)
rho = 1 - 2 / (n * (n - 1))
exact = np.linalg.eigvalsh(A)


def off(M):
    return (M**2).sum() - (np.diag(M) ** 2).sum()


M = A.copy()
S, err = [off(M)], [np.abs(np.sort(np.diag(M)) - exact).max()]
for p in range(12):
    O = np.abs(M - np.diag(np.diag(M)))
    k, l = np.unravel_index(O.argmax(), O.shape)
    phi = 0.5 * np.arctan2(2 * M[k, l], M[k, k] - M[l, l])
    Q = np.eye(n)
    Q[k, k] = Q[l, l] = np.cos(phi)
    Q[k, l], Q[l, k] = -np.sin(phi), np.sin(phi)
    M = Q.T @ M @ Q
    S.append(off(M))
    err.append(np.abs(np.sort(np.diag(M)) - exact).max())

ps = np.arange(len(S))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ps, S[0] * rho**ps, ls="--", color=nmfig.AUX, label=r"оценка леммы $\rho^p S_0$, $\rho=5/6$")
ax.semilogy(ps, S, marker="o", ms=4, color=nmfig.CYCLE[0], label=r"$S_p=\sum_{i\neq j}|a_{ij}^{(p)}|^2$")
ax.semilogy(ps, err, marker="s", ms=4, color=nmfig.CYCLE[2], label=r"$\max_k|\lambda_k^{(p)}-\lambda_k|$")
ax.set_xlabel("число вращений $p$")
ax.set_ylabel("значение")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 4, "jacobi_offdiag_decay")
print([f"{s:.3e}" for s in S])
print([f"{e:.3e}" for e in err])
