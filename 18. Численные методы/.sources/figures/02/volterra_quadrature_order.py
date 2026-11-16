"""Error against the step for the trapezoid and the Simpson-with-trapezoid quadrature methods on a linear Volterra equation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def kernel(x, s):
    return np.exp(x**2 - s**2)


def rhs(x):
    return np.exp(x**2)


def exact(x):
    return np.exp(x**2 + x)


def row_weights_trapezoid(i, h):
    w = np.full(i + 1, h)
    w[0] = h / 2
    w[i] = h / 2
    return w


def row_weights_simpson(i, h):
    """Weights A_ij, j=0..i: Simpson on the nodes 0..i, or on 0..i-1 and a trapezoid on the last step when i is odd."""
    if i == 1:
        return np.full(2, h / 2)
    w = np.zeros(i + 1)
    if i % 2 == 0:
        w[:] = 2 * h / 3
        w[1::2] = 4 * h / 3
        w[0] = w[i] = h / 3
    else:
        m = i - 1
        w[: m + 1] = 2 * h / 3
        w[1:m:2] = 4 * h / 3
        w[0] = w[m] = h / 3
        w[m] += h / 2
        w[i] = h / 2
    return w


def solve(n, row_weights):
    x = np.linspace(0, 1, n)
    h = x[1] - x[0]
    y = np.zeros(n)
    y[0] = rhs(x[0])
    for i in range(1, n):
        w = row_weights(i, h)
        k = kernel(x[i], x[: i + 1])
        y[i] = (rhs(x[i]) + np.sum(w[:i] * k[:i] * y[:i])) / (1 - w[i] * k[i])
    return np.abs(y - exact(x)).max()


ns = np.array([11, 21, 41, 81, 161, 321, 641])
hs = 1 / (ns - 1)
err_trap = [solve(n, row_weights_trapezoid) for n in ns]
err_simp = [solve(n, row_weights_simpson) for n in ns]

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.loglog(hs, err_trap, marker="o", ms=4, color=nmfig.CYCLE[0], label="трапеции")
ax.loglog(hs, err_simp, marker="s", ms=4, color=nmfig.CYCLE[2], label="Симпсон с трапецией")
ax.loglog(hs, err_trap[2] * (hs / hs[2]) ** 2, ls="--", color=nmfig.AUX, label=r"$h^2$")
ax.loglog(hs, err_simp[2] * (hs / hs[2]) ** 3, ls=":", color=nmfig.AUX, label=r"$h^3$")
ax.set_xlabel("шаг $h$")
ax.set_ylabel(r"$\max_i|y(x_i)-y_i|$")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 2, "volterra_quadrature_order")
