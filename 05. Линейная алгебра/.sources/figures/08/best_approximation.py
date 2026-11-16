"""The best approximation y of x in the plane L: x - y is orthogonal to L, so |x - y| < |x - z| for every other z in L."""
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
y = np.array([2.0, 0.8, 0.0])
z = np.array([-0.8, 1.2, 0.0])
h = np.array([0.0, 0.0, 1.9])
x = y + h
n = np.array([0.0, 0.0, 1.0])
for p in (y, z):      # y and z lie in the parallelogram that draws L
    s, t = np.linalg.solve(np.column_stack([a[:2], b[:2]]), (p - corner)[:2])
    assert 0 < s < 1 and 0 < t < 1
assert np.isclose((x - y) @ a, 0) and np.isclose((x - y) @ b, 0)
assert np.isclose(np.linalg.norm(x - z) ** 2, np.linalg.norm(x - y) ** 2 + np.linalg.norm(y - z) ** 2)

fig = plt.figure(figsize=(6.6, 4.6))
elev, azim = view.best_view([y, z, x, x - z, y - z], normals=[n], pairs=[(y, x), (z, y)])
ax = v3d.new_axes(fig, 111, ((-2.0, 2.8), (-1.4, 2.0), (-0.1, 2.1)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.parallelogram(ax, corner, a, b, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.segment(ax, z, x, lafig.INK, lw=1.4, ls="--")
v3d.segment(ax, y, x, lafig.HIGHLIGHT, lw=2.4)
v3d.arrow(ax, x, lafig.VECTOR, None, lw=2.0)
v3d.arrow(ax, y, lafig.IMAGE, r"$y$", lw=2.6, offset=(0.15, -0.2, 0.0))
v3d.arrow(ax, z, lafig.P["rule"], r"$z$", lw=2.2, offset=(-0.25, 0.0, 0.0))
ax.text(*(x + np.array([0.0, 0.0, 0.2])), r"$x$", color=lafig.INK, ha="center", va="center", zorder=6)
ax.text(*(y + 0.55 * h + np.array([0.2, 0.0, 0.0])), r"$x-y$", color=lafig.HIGHLIGHT, ha="left", va="center", zorder=6)
ax.text(*(0.5 * (z + x) + np.array([-0.55, 0.0, 0.15])), r"$x-z$", color=lafig.INK, ha="center", va="center", zorder=6)
ax.text(*(corner + 0.9 * a + 0.1 * b + np.array([0.0, 0.0, 0.0])), r"$L$", color=lafig.INK, ha="center", va="center", zorder=6)
v3d.right_angle(ax, y, -y, h, 0.2, lafig.INK)

view.trim(lafig.save(fig, 8, "best_approximation"))
