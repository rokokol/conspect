"""Kellogg ratios for the kernel min(x, s) on [0, 1]: error of both formulas (5) against the number of iterations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# Eigenpairs of min(x, s): phi_k = sqrt(2) sin(mu_k x), mu_k = (k - 1/2) pi, lambda_k = mu_k^2.
k = np.arange(1, 400001, dtype=np.longdouble)
mu = (k - 0.5) * np.longdouble(np.pi)
lam1 = float(mu[0] ** 2)
# Fourier coefficients c_k = (omega, phi_k) of the starting functions
coef = {
    r"$\omega=1$": np.sqrt(np.longdouble(2)) / mu,
    r"$\omega=x$": np.sqrt(np.longdouble(2)) * (-1) ** (k + 1) / mu**2,
}


def norm(c, n):
    """||omega_n||, omega_n = sum c_k mu_k^(-2n) phi_k."""
    return float(np.sqrt(np.sum((c * mu ** (-2 * n)) ** 2)))


ns = np.arange(1, 7)
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ns, 81.0 ** (-ns.astype(float)) * 20, ls="--", color=nmfig.AUX, label=r"$(\lambda_1/\lambda_2)^{2n}=81^{-n}$ (наклон)")
for (name, c), col, mk in zip(coef.items(), (nmfig.EXACT, nmfig.APPROX), ("o", "s")):
    ratio = [norm(c, n - 1) / norm(c, n) for n in ns]
    ax.semilogy(ns, np.abs(np.array(ratio) - lam1), marker=mk, ms=4, color=col, label=rf"отношение норм (5), {name}")
c = coef[r"$\omega=1$"]
root = [1 / norm(c, n) ** (1 / n) for n in ns]
ax.semilogy(ns, np.abs(np.array(root) - lam1), marker="^", ms=4, color=nmfig.NODES, label=r"корень (5), $\omega=1$")
ax.set_xlabel("номер итерации $n$")
ax.set_ylabel(r"$|\text{оценка}-\lambda_1|$, $\lambda_1=\pi^2/4$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 4, "kellogg_convergence")
for name, c in coef.items():
    print(name, [f"{norm(c, n - 1) / norm(c, n):.7f}" for n in ns])
print("root", [f"{r:.7f}" for r in root])
