"""The hyperplane Pi_e in X_3 and the decomposition x = mu e + y: y is the foot of the perpendicular from x, mu e = x - y."""
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

corner = np.array([-1.8, -1.2, 0.0])
a = np.array([4.4, 0.0, 0.0])
b = np.array([0.5, 3.0, 0.0])
e = np.array([0.0, 0.0, 1.0])
mu = 1.7
y = np.array([1.9, 0.7, 0.0])
x = mu * e + y
assert np.isclose(y @ e, 0) and np.allclose(x, mu * e + y)
assert np.isclose(mu, (x @ e) / (e @ e))                        # mu = (x, e) / (e, e)
s, t = np.linalg.solve(np.column_stack([a[:2], b[:2]]), (y - corner)[:2])
assert 0 < s < 1 and 0 < t < 1

fig = plt.figure(figsize=(6.6, 4.6))
elev, azim = view.best_view([y, x, mu * e], normals=[e], pairs=[(y, e)])
ax = v3d.new_axes(fig, 111, ((-2.0, 2.8), (-1.4, 2.0), (-0.1, 2.0)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.parallelogram(ax, corner, a, b, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.segment(ax, mu * e, x, lafig.INK, lw=1.2, ls="--")
v3d.segment(ax, e, mu * e, lafig.HIGHLIGHT, lw=2.0, ls=":")
v3d.segment(ax, y, x, lafig.HIGHLIGHT, lw=2.4)
v3d.arrow(ax, y, lafig.IMAGE, r"$y$", lw=2.6, offset=(0.2, -0.15, 0.0))
v3d.arrow(ax, x, lafig.VECTOR, r"$x$", lw=2.0, offset=(0.0, 0.0, 0.2))
v3d.arrow(ax, e, lafig.HIGHLIGHT, r"$e$", lw=2.6, offset=(-0.15, 0.0, 0.0))
ax.text(*(mu * e + np.array([-0.15, 0.0, 0.15])), r"$\mu e$", color=lafig.HIGHLIGHT, ha="right", va="center", zorder=6)
ax.text(*(y + 0.5 * mu * e + np.array([0.2, 0.0, 0.0])), r"$x-y=\mu e$", color=lafig.HIGHLIGHT, ha="left", va="center", zorder=6)
ax.text(*(corner + 0.88 * a + 0.1 * b), r"$\Pi_e$", color=lafig.INK, ha="center", va="center", zorder=6)
v3d.right_angle(ax, 0.0 * e, y, e, 0.22, lafig.INK)

view.trim(lafig.save(fig, 8, "hyperplane_decomposition"))
