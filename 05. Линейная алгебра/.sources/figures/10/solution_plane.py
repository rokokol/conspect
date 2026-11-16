"""Solution plane of the lecture example (3x4, rank 2) in X_4, drawn by projection along x2 onto (x1, x3, x4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "03"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "02"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402
import view  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

A = np.array([[1, -1, 1, -1], [1, 1, 2, 3], [2, 4, 5, 10]], float)
b = np.array([4, 8, 20], float)
x0 = np.array([6, 2, 0, 0], float)
f1 = np.array([-1.5, -0.5, 1, 0])
f2 = np.array([-1, -2, 0, 1], float)
assert np.allclose(A @ x0, b) and np.allclose(A @ f1, 0) and np.allclose(A @ f2, 0)
assert np.linalg.matrix_rank(A) == 2 and np.linalg.matrix_rank(np.column_stack([A, b])) == 2


def proj(v):
    """Drop x2: the map (x1, x2, x3, x4) -> (x1, x3, x4)."""
    return np.asarray(v, float)[[0, 2, 3]]


# the projection is injective on the solution plane: x2 = 2 - x3/2 - 2 x4 is a function of (x1, x3, x4)
for c1, c2 in [(0.3, -0.7), (1.1, 0.4), (-0.5, 1.5)]:
    x = x0 + c1 * f1 + c2 * f2
    assert np.isclose(x[1], 2 - x[2] / 2 - 2 * x[3])
p0, p1, p2 = proj(x0), proj(f1), proj(f2)
assert np.linalg.matrix_rank(np.column_stack([p1, p2])) == 2

lo, hi = -1.6, 2.4
span = hi - lo
x = p0 + 0.6 * p1 + 0.8 * p2                 # the solution with c1 = 0.6, c2 = 0.8

fig = plt.figure(figsize=(7.2, 5.0))
nrm = np.cross(p1, p2)
elev, azim = view.best_view([p0, p1, p2], normals=[nrm], pairs=[(p1, p2)], elev_range=(22, 40), azim_range=(-75, -30))
ax = v3d.new_axes(fig, 111, ((-4.5, 8.5), (-2.0, 3.0), (-2.0, 3.0)), elev=elev, azim=azim, zoom=0.9)
ax.computed_zorder = False
v3d.parallelogram(ax, lo * p1 + lo * p2, span * p1, span * p2, lafig.AUX, alpha=0.35).set_zorder(1)
v3d.parallelogram(ax, p0 + lo * p1 + lo * p2, span * p1, span * p2, lafig.VECTOR, alpha=0.3).set_zorder(1)
v3d.arrow(ax, p0, lafig.HIGHLIGHT, None, lw=2.4)
v3d.arrow(ax, p1, lafig.INK, r"$x^1$", start=p0, lw=3.0, offset=(-0.2, 0.0, 0.2))
v3d.arrow(ax, p2, lafig.INK, r"$x^2$", start=p0, lw=3.0, offset=(-0.2, 0.0, 0.2))
ax.scatter(*x, color=lafig.VECTOR, s=30, zorder=6)
ax.text(*(p0 + np.array([0.5, 0.0, -0.6])), r"$x^0$", color=lafig.INK, ha="center", va="center", zorder=6)
ax.text(*(np.array([-0.6, 0.0, -0.4])), r"$0$", color=lafig.INK, ha="center", va="center", zorder=6)

handles = [
    Patch(facecolor=lafig.tint(lafig.VECTOR, 0.35), edgecolor=lafig.VECTOR, label=r"решения системы"),
    Patch(facecolor=lafig.tint(lafig.AUX, 0.35), edgecolor=lafig.AUX, label=r"$\operatorname{Ker}A$"),
    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.4, label=r"частное решение $x^0$"),
    Line2D([0], [0], color=lafig.INK, lw=3.0, label=r"ФСР $x^1,x^2$"),
    Line2D([0], [0], color=lafig.VECTOR, marker="o", ls="", ms=5, label=r"решение $x=x^0+0{,}6x^1+0{,}8x^2$"),
]
fig.legend(handles=handles, loc="upper left", frameon=False, bbox_to_anchor=(0.02, 0.98))

view.trim(lafig.save(fig, 10, "solution_plane"))
