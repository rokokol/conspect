"""Error of the simple iteration for y(x)=1+int_0^x y(s)ds on [0,7] against the bound (M(b-a))^k/k! ||y^0-y||."""
import sys
from math import factorial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

a, b, n = 0.0, 7.0, 101
x = np.linspace(a, b, n)
h = x[1] - x[0]
f = np.ones(n)

# the quadrature solution: the exact limit of the discrete iteration
y_star = np.zeros(n)
y_star[0] = f[0]
for i in range(1, n):
    y_star[i] = (f[i] + h / 2 * y_star[0] + h * y_star[1:i].sum()) / (1 - h / 2)

y = f.copy()
K = 30
err = [np.abs(y - y_star).max()]
for k in range(K):
    new = f.copy()
    for i in range(1, n):
        new[i] = f[i] + h / 2 * y[0] + h / 2 * y[i] + h * y[1:i].sum()
    y = new
    err.append(np.abs(y - y_star).max())

ks = np.arange(K + 1)
bound = [(b - a) ** k / factorial(k) * err[0] for k in ks]

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.semilogy(ks, bound, ls="--", color=nmfig.AUX, label=r"оценка $\dfrac{(M(b-a))^k}{k!}\,\|y^0-y\|$")
ax.semilogy(ks, err, marker="o", ms=4, color=nmfig.APPROX, label=r"$\|y^k-y\|$")
ax.set_xlabel("номер итерации $k$")
ax.set_ylabel("наибольшая по узлам погрешность")
ax.grid(True, which="major")
ax.legend()
nmfig.save(fig, 1, "volterra_iteration_error")
