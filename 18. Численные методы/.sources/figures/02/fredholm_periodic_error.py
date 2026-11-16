"""Error of the trapezoid and Simpson quadrature methods for the periodic Fredholm example of exercise 3.9."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

a, b = -np.pi, np.pi
lam = 3 / (10 * np.pi)


def kernel(x, s):
    return 1 / (0.64 * np.cos((x + s) / 2) ** 2 - 1)


def rhs(x):
    return 25 - 16 * np.sin(x) ** 2


def exact(x):
    return 17 / 2 + 128 / 17 * np.cos(2 * x)


def trapezoid_weights(n):
    h = (b - a) / (n - 1)
    w = np.full(n, h)
    w[0] = w[-1] = h / 2
    return w


def simpson_weights(n):
    h = (b - a) / (n - 1)
    w = np.zeros(n)
    w[0] = w[-1] = h / 3
    w[1:-1:2] = 4 * h / 3
    w[2:-1:2] = 2 * h / 3
    return w


def max_error(n, weights):
    x = np.linspace(a, b, n)
    A = np.eye(n) - lam * kernel(x[:, None], x[None, :]) * weights(n)[None, :]
    return np.abs(np.linalg.solve(A, rhs(x)) - exact(x)).max()


ns_trap = np.arange(5, 38, 2)
ns_simp = np.arange(5, 38, 2)
err_trap = [max_error(n, trapezoid_weights) for n in ns_trap]
err_simp = [max_error(n, simpson_weights) for n in ns_simp]
floor = 1e-15

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ns_trap, np.maximum(err_trap, floor), marker="o", ms=4, color=nmfig.CYCLE[0], label="трапеции")
ax.semilogy(ns_simp, np.maximum(err_simp, floor), marker="s", ms=4, color=nmfig.CYCLE[2], label="Симпсон")
ax.set_xlabel("число узлов $n$")
ax.set_ylabel(r"$\max_i|y(x_i)-y_i|$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 2, "fredholm_periodic_error")
