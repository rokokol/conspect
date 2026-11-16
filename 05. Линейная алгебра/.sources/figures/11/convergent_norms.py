"""Norms of the powers of two matrices of the convergent-matrices note: spectral radius below and above one."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

CONVERGENT = np.array([[0.9, 5.0], [0.0, 0.9]])
DIVERGENT = np.array([[1.0, 0.3], [0.0, 1.05]])
P_MAX = 120
powers = np.arange(P_MAX + 1)


def norms(a):
    """Spectral norm of a^p for p = 0 .. P_MAX."""
    out, cur = [], np.eye(2)
    for _ in powers:
        out.append(np.linalg.norm(cur, 2))
        cur = cur @ a
    return np.array(out)


def radius(a):
    return max(abs(np.linalg.eigvals(a)))


fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.axhline(1, color=lafig.AUX, lw=0.8, zorder=0, label=r"уровень $1$")

rho_c, rho_d = radius(CONVERGENT), radius(DIVERGENT)


def comma(x):
    """Number with a decimal comma, as in the note text."""
    return f"{x:g}".replace(".", "{,}")


ax.plot(powers, norms(CONVERGENT), color=lafig.VECTOR, lw=2, label=rf"$\rho(A)={comma(rho_c)}<1$: $\|A^p\|_2\to0$")
ax.plot(powers, rho_c**powers, color=lafig.VECTOR, lw=1.2, ls="--", label=rf"$\rho^p$ при $\rho={comma(rho_c)}$")
ax.plot(powers, norms(DIVERGENT), color=lafig.IMAGE, lw=2, label=rf"$\rho(B)={comma(rho_d)}>1$: $\|B^p\|_2\to\infty$")

top = norms(CONVERGENT).argmax()
ax.scatter([top], [norms(CONVERGENT)[top]], color=lafig.HIGHLIGHT, zorder=3)
ax.annotate(
    f"максимум при $p={top}$, затем спад",
    (top, norms(CONVERGENT)[top]),
    textcoords="offset points",
    xytext=(14, 8),
    color=lafig.INK,
    fontsize=10,
)

ax.set_yscale("log")
ax.set_xlim(0, P_MAX)
ax.set_xlabel("степень $p$", color=lafig.INK)
ax.set_ylabel(r"спектральная норма $\|M^p\|_2$, $M=A,B$", color=lafig.INK)
ax.legend(loc="lower left", frameon=False)
lafig.save(fig, 11, "convergent_norms")
