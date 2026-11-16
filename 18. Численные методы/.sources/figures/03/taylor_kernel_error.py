"""Error of the degenerate-kernel method for y + int_0^1 x(e^{xs}-1)y ds = e^x - x against the number of Taylor terms."""
import sys
from math import factorial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

nodes, weights = np.polynomial.legendre.leggauss(40)
s = (nodes + 1) / 2
w = weights / 2
xs = np.linspace(0, 1, 2001)
lam = -1.0
norm_a = np.e - 2                      # ||A|| = max_x int_0^1 x(e^{xs}-1) ds, reached at x = 1
t_inv = 1 / (1 - norm_a)               # Neumann bound on ||(I - lam A)^{-1}||


def tail(m_terms):
    """||A - A_M|| = sum_{m>M} 1/(m!(m+1)), the kernel remainder being positive and increasing in x."""
    return sum(1 / (factorial(m) * (m + 1)) for m in range(m_terms + 1, 40))


def solve(m_terms):
    """Degenerate kernel sum_{m<=M} x^{m+1} s^m / m!: alpha_m = x^{m+1}, beta_m = s^m / m!."""
    idx = np.arange(1, m_terms + 1)
    a = np.array([[1 / (factorial(i) * (i + j + 2)) for j in idx] for i in idx])
    f_s = np.exp(s) - s
    r = np.array([np.sum(w * s**i / factorial(i) * f_s) for i in idx])
    c = np.linalg.solve(np.eye(m_terms) - lam * a, r)
    y = np.exp(xs) - xs + lam * sum(c[k] * xs ** (idx[k] + 1) for k in range(m_terms))
    return np.abs(y - 1).max()


ms = np.arange(1, 9)
err = [solve(m) for m in ms]
bound = []
for m in ms:
    q = t_inv * tail(m)
    bound.append(q / (1 - q) if q < 1 else np.nan)

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ms, err, marker="o", ms=4, color=nmfig.APPROX, label="погрешность $\\max|y-\\widetilde y|$")
ax.semilogy(ms, bound, marker="s", ms=4, color=nmfig.EXACT, label="оценка $q/(1-q)$")
ax.semilogy(ms, [tail(m) for m in ms], ls="--", color=nmfig.AUX, label="$\\|A-A_M\\|$")
ax.set_xlabel("число членов ряда Тейлора $M$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 3, "taylor_kernel_error")
