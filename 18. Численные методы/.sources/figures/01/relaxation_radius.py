"""Spectral radius of the relaxation matrix against omega, with the lower bound |1 - omega| of Theorem 6.2."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

n = 20
A = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)
D = np.diag(np.diag(A))
L = np.tril(A, -1)


def radius(w):
    S = np.eye(n) - w * np.linalg.solve(D + w * L, A)
    return np.abs(np.linalg.eigvals(S)).max()


ws = np.linspace(0.02, 2.3, 300)
rho = np.array([radius(w) for w in ws])
i_best = int(np.argmin(rho))

fig, ax = plt.subplots(figsize=(6.4, 3.8))
def comma(v):
    return f"{v:.2f}".replace(".", "{,}")


ax.axvspan(0, 2, facecolor=nmfig.tint(nmfig.NODES, 0.75), label=r"область $0<\omega<2$",
           edgecolor=nmfig.NODES, linewidth=1.2)
ax.plot(ws, np.abs(1 - ws), ls="--", color=nmfig.AUX, label=r"нижняя граница $|1-\omega|$")
ax.plot(ws, rho, color=nmfig.CYCLE[0], label=r"$\rho(S_\omega)$")
ax.axhline(1, color=nmfig.MUTED, lw=1)
ax.plot([ws[i_best]], [rho[i_best]], "o", color=nmfig.INK, ms=4)
w_opt = 2 / (1 + np.sin(np.pi / (n + 1)))
ax.annotate(f"минимум $\\rho={comma(w_opt - 1)}$ при $\\omega\\approx{w_opt:.3f}$".replace(".", "{,}"),
            (ws[i_best], rho[i_best]), xytext=(1.0, 0.3), textcoords="data", ha="center")
ax.set_xlim(0, 2.3)
ax.set_ylim(0, 1.3)
ax.set_xlabel(r"релаксационный параметр $\omega$")
ax.set_ylabel(r"спектральный радиус $\rho(S_\omega)$")
ax.legend(loc="upper left", fontsize=8)
nmfig.save(fig, 1, "relaxation_radius")
