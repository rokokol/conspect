"""Lagrange interpolation through four nodes: the basis polynomials and their weighted sum."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

NODES = np.array([-1.0, 0.0, 2.0, 3.0])
VALUES = np.array([1.0, -1.0, 2.0, 0.0])
N = len(NODES) - 1


def basis(i: int, z):
    """phi_i(z) = prod_{k != i} (z - z_k) / (z_i - z_k)."""
    out = np.ones_like(z)
    for k in range(N + 1):
        if k != i:
            out = out * (z - NODES[k]) / (NODES[i] - NODES[k])
    return out


# the coefficients from the Vandermonde system must give the same polynomial
vander = np.vander(NODES, N + 1, increasing=True)
coef = np.linalg.solve(vander, VALUES)

z = np.linspace(-1.6, 3.6, 600)
lagrange = sum(VALUES[i] * basis(i, z) for i in range(N + 1))
direct = np.polynomial.polynomial.polyval(z, coef)
assert np.allclose(lagrange, direct)
for j in range(N + 1):
    assert np.allclose([basis(i, NODES[j]) for i in range(N + 1)], np.eye(N + 1)[:, j])

fig, (left, right) = plt.subplots(1, 2, figsize=(10.4, 4.4), sharex=True)

for i in range(N + 1):
    color = lafig.CYCLE[i % len(lafig.CYCLE)]
    left.plot(z, basis(i, z), color=color, lw=1.8, label=f"$\\varphi_{i}$")
    left.scatter([NODES[i]], [1.0], s=46, color=color, zorder=4)
    left.scatter(np.delete(NODES, i), np.zeros(N), s=46, facecolor="none", edgecolor=color, zorder=4)
left.axhline(0, color=lafig.MUTED, lw=0.8)
left.set_title("базисные многочлены", color=lafig.INK, fontweight="normal")

for i in range(N + 1):
    color = lafig.CYCLE[i % len(lafig.CYCLE)]
    right.plot(z, VALUES[i] * basis(i, z), color=color, lw=1.0, ls="--", alpha=0.8)
right.plot(z, lagrange, color=lafig.INK, lw=2.4, label="$P_3=\\sum h_i\\varphi_i$")
right.scatter(NODES, VALUES, s=60, color=lafig.HIGHLIGHT, zorder=5, label="узлы $(z_j,\\,h_j)$")
right.axhline(0, color=lafig.MUTED, lw=0.8)
right.set_title("многочлен и его слагаемые", color=lafig.INK, fontweight="normal")

for ax in (left, right):
    ax.set_xlabel("$z$")
    ax.set_xticks(NODES)
    ax.grid(color=lafig.AUX, lw=0.5)
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_color(lafig.INK)
left.set_ylim(-1.2, 1.8)
right.set_ylim(-2.6, 3.2)
handles_left, _ = left.get_legend_handles_labels()
handles_left += [
    Line2D([], [], marker="o", ls="", color=lafig.INK, label="$\\varphi_i(z_i)=1$"),
    Line2D([], [], marker="o", ls="", markerfacecolor="none", color=lafig.INK, label="$\\varphi_i(z_k)=0,\\ k\\neq i$"),
]
left.legend(handles=handles_left, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False, fontsize=8, ncol=3)
handles_right, _ = right.get_legend_handles_labels()
handles_right.append(Line2D([], [], color=lafig.MUTED, lw=1.0, ls="--", label="слагаемые $h_i\\varphi_i$ (цвета как слева)"))
right.legend(handles=handles_right, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False, fontsize=8, ncol=1)

lafig.save(fig, 4, "lagrange_interpolation")
