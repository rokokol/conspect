"""Error of the Jacobi and Seidel methods against the bound q^k max|z^0| of Theorems 3.1 and 4.1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

A = np.array([[4, 1, 1], [1, 5, 2], [0, 2, 4]], float)
x_exact = np.array([1.0, 2.0, 3.0])
b = A @ x_exact
D = np.diag(np.diag(A))
L = np.tril(A, -1)
R = np.triu(A, 1)
q = max(np.abs(A[i]).sum() / abs(A[i, i]) - 1 for i in range(3))

S_jacobi = -np.linalg.solve(D, L + R)
c_jacobi = np.linalg.solve(D, b)
S_seidel = -np.linalg.solve(D + L, R)
c_seidel = np.linalg.solve(D + L, b)

K = 14
xj = np.zeros(3)
xs = np.zeros(3)
err_j, err_s = [], []
for k in range(K + 1):
    err_j.append(np.abs(xj - x_exact).max())
    err_s.append(np.abs(xs - x_exact).max())
    xj = S_jacobi @ xj + c_jacobi
    xs = S_seidel @ xs + c_seidel

ks = np.arange(K + 1)
bound = q**ks * err_j[0]

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ks, bound, ls="--", color=nmfig.AUX, label=r"оценка $q^k\max|z_j^0|$, $q=0{,}6$")
ax.semilogy(ks, err_j, marker="o", ms=4, color=nmfig.CYCLE[0], label="Якоби")
ax.semilogy(ks, err_s, marker="s", ms=4, color=nmfig.CYCLE[2], label="Зейдель")
ax.set_xlabel("номер итерации $k$")
ax.set_ylabel(r"наибольшая по $j$ погрешность $|x_j^k-x_j|$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 1, "jacobi_seidel_decay")
