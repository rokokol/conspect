"""Orthogonal operators of the plane: a rotation by phi and the reflection in the axis xi_2."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

phi = np.deg2rad(50.0)
rot = np.array([[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]])
ref = np.diag([-1.0, 1.0])
for q in (rot, ref):
    assert np.allclose(q.T @ q, np.eye(2))
assert np.isclose(np.linalg.det(rot), 1.0) and np.isclose(np.linalg.det(ref), -1.0)

e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
x = np.array([1.45, 0.55])
assert np.isclose(np.linalg.norm(rot @ x), np.linalg.norm(x))
assert np.isclose(np.dot(rot @ x, x) / np.dot(x, x), np.cos(phi))     # (Ax, x) = |x||Ax| cos(phi)


def arrow(ax, v, color, label, offset, lw=2.0, ls="-"):
    ax.annotate("", xy=v, xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))
    ax.text(v[0] + offset[0], v[1] + offset[1], label, color=lafig.INK, ha="center", va="center")


def frame(ax, title):
    ax.set_aspect("equal")
    ax.set_xlim(-2.1, 2.1)
    ax.set_ylim(-0.3, 2.2)
    ax.axhline(0, color=lafig.AUX, lw=0.8, zorder=0)
    ax.axvline(0, color=lafig.AUX, lw=0.8, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title(title, color=lafig.INK)


fig, (left, right) = plt.subplots(1, 2, figsize=(8.6, 3.5))

frame(left, r"Поворот, $A_e=Q_2(\varphi)$")
t = np.linspace(0, np.pi, 200)
left.plot(np.linalg.norm(x) * np.cos(t), np.linalg.norm(x) * np.sin(t), color=lafig.AUX, lw=1.0, ls=":")
arrow(left, e1, lafig.VECTOR, r"$e^1$", (0.0, -0.18), lw=1.5)
arrow(left, e2, lafig.VECTOR, r"$e^2$", (-0.15, 0.0), lw=1.5)
arrow(left, rot @ e1, lafig.IMAGE, r"$Ae^1$", (0.2, 0.1), lw=1.5)
arrow(left, rot @ e2, lafig.IMAGE, r"$Ae^2$", (-0.22, 0.0), lw=1.5)
arrow(left, x, lafig.VECTOR, r"$x$", (0.12, -0.16))
arrow(left, rot @ x, lafig.IMAGE, r"$Ax$", (-0.18, 0.1))
arc = np.linspace(0, phi, 60)
left.plot(0.4 * np.cos(arc), 0.4 * np.sin(arc), color=lafig.HIGHLIGHT, lw=1.6)
left.text(0.62 * np.cos(0.78 * phi), 0.62 * np.sin(0.78 * phi), r"$\varphi$", color=lafig.HIGHLIGHT, ha="center", va="center")

frame(right, r"Отражение, $A_e=\operatorname{diag}(-1,1)$")
right.plot([0, 0], [-0.25, 2.15], color=lafig.HIGHLIGHT, lw=1.4, ls="--")
right.text(0.12, 2.05, r"$\xi_2$", color=lafig.HIGHLIGHT, ha="left", va="center")
arrow(right, e1, lafig.VECTOR, r"$e^1$", (0.0, -0.18), lw=1.5)
arrow(right, e2, lafig.VECTOR, r"$e^2=Ae^2$", (0.52, 0.0), lw=1.5)
arrow(right, ref @ e1, lafig.IMAGE, r"$Ae^1$", (0.0, -0.18), lw=1.5)
arrow(right, x, lafig.VECTOR, r"$x$", (0.12, -0.16))
arrow(right, ref @ x, lafig.IMAGE, r"$Ax$", (-0.12, -0.16))

fig.legend(handles=[Line2D([0], [0], color=lafig.VECTOR, lw=2.0, label="вектор"),
                    Line2D([0], [0], color=lafig.IMAGE, lw=2.0, label="его образ"),
                    Line2D([0], [0], color=lafig.AUX, lw=1.0, ls=":", label=r"окружность радиуса $|x|$")],
           loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.07, 1, 1))

lafig.save(fig, 12, "orthogonal-plane")
