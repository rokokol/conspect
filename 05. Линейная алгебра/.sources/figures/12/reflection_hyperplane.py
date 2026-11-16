"""The reflection R = I - 2ww^T in R^3: x = alpha w + z with z in the plane orthogonal to w, Rx = -alpha w + z."""
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

w = np.array([0.0, 0.0, 1.0])
z = np.array([1.8, 0.9, 0.0])
alpha = 1.3
x = alpha * w + z
R = np.eye(3) - 2.0 * np.outer(w, w)
Rx = R @ x
assert np.allclose(R, R.T) and np.allclose(R @ R, np.eye(3))
assert np.allclose(R @ w, -w) and np.allclose(R @ z, z) and np.allclose(Rx, -alpha * w + z)

corner = np.array([-1.7, -1.5, 0.0])
a = np.array([4.6, 0.0, 0.0])
b = np.array([0.4, 3.2, 0.0])
s, t = np.linalg.solve(np.column_stack([a[:2], b[:2]]), (z - corner)[:2])
assert 0 < s < 1 and 0 < t < 1

fig = plt.figure(figsize=(6.6, 4.4))
elev, azim = view.best_view([z, x, Rx], normals=[w])
ax = v3d.new_axes(fig, 111, ((-2.0, 3.6), (-1.6, 1.8), (-1.5, 1.5)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.parallelogram(ax, corner, a, b, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.segment(ax, z, x, lafig.INK, lw=1.2, ls="--")
v3d.segment(ax, z, Rx, lafig.INK, lw=1.2, ls="--")
v3d.arrow(ax, w, lafig.HIGHLIGHT, r"$w$", lw=2.6, offset=(-0.2, 0.0, 0.1))
v3d.arrow(ax, z, lafig.MUTED, r"$z$", lw=2.0, offset=(0.2, -0.1, 0.0))
v3d.arrow(ax, x, lafig.VECTOR, r"$x$", lw=2.2, offset=(0.0, 0.0, 0.2))
v3d.arrow(ax, Rx, lafig.IMAGE, r"$Rx$", lw=2.2, offset=(0.0, 0.0, -0.2))
ax.text(*(z + 0.5 * alpha * w + np.array([0.2, 0.0, 0.0])), r"$\alpha w$", color=lafig.INK, ha="left", va="center", zorder=6)
ax.text(*(z - 0.5 * alpha * w + np.array([0.2, 0.0, 0.0])), r"$-\alpha w$", color=lafig.INK, ha="left", va="center", zorder=6)
ax.text(*(corner + 0.1 * a + 0.15 * b), r"$\pi_w$", color=lafig.INK, ha="center", va="center", zorder=6)
v3d.right_angle(ax, np.zeros(3), z, w, 0.22, lafig.INK)

fig.legend(handles=[Line2D([0], [0], color=lafig.VECTOR, lw=2.0, label=r"вектор $x$"),
                    Line2D([0], [0], color=lafig.IMAGE, lw=2.0, label=r"его отражение $Rx$"),
                    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.0, label=r"нормаль $w$"),
                    Line2D([0], [0], color=lafig.AUX, lw=6.0, label=r"плоскость $\pi_w\perp w$")],
           loc="lower center", bbox_to_anchor=(0.5, 0.2), ncol=2, frameon=False)
fig.subplots_adjust(bottom=0.1, top=1.0)

view.trim(lafig.save(fig, 12, "reflection-hyperplane"))
