"""Two-sided trace bounds A_2m^(-1/2m) <= lambda_1 <= sqrt(A_2m / A_2m+2) for the Green kernel of problem 345."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

# Eigenvalues of K = x(2-s)/2 (x <= s): lambda_k = mu_k^2, sin(mu) + mu cos(mu) = 0 (tan mu = -mu)
K = 200000
mu = np.array([brentq(lambda t: np.sin(t) + t * np.cos(t), np.pi * (k - 0.5) + 1e-9, np.pi * k - 1e-9) for k in range(1, 3001)])
tail = np.pi * (np.arange(3001, K + 1) - 0.5)
lam = np.concatenate([mu, tail]) ** 2
lam1 = lam[0]


def A(m):
    return np.sum(lam ** (-float(m)))


ms = np.arange(1, 7)
lower = np.array([A(2 * m) ** (-1 / (2 * m)) for m in ms])
upper = np.array([np.sqrt(A(2 * m) / A(2 * m + 2)) for m in ms])
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.plot(ms, upper, marker="o", ms=4, color=nmfig.APPROX, label=r"сверху: $\sqrt{A_{2m}/A_{2m+2}}$")
ax.plot(ms, lower, marker="s", ms=4, color=nmfig.NODES, label=r"снизу: $A_{2m}^{-1/(2m)}$")
ax.axhline(lam1, ls="--", color=nmfig.EXACT, label=rf"$\lambda_1={lam1:.4f}$".replace(".", "{,}"))
ax.set_xlabel("порядок $m$ следа $A_{2m}$")
ax.set_ylabel("оценка $\\lambda_1$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 4, "trace_bounds")
print(lam1)
for m, lo, up in zip(ms, lower, upper):
    print(m, f"{lo:.6f} {up:.6f}")
print("A2,A4", A(2), A(4), "A1", A(1))
