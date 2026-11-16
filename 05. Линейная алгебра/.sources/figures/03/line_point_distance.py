"""The distance from a point x' to the line x = x0 + theta e: the height of the parallelogram on e and x' - x0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "02"))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402
import view  # noqa: E402

x0 = np.array([0.5, 0.7, 0.5])
e = np.array([1.3, 0.5, 0.2])
zhat = np.array([0.0, 0.0, 1.0])
n = zhat - (zhat @ e) / (e @ e) * e
n = n / np.linalg.norm(n)
h = 1.1
t = 0.8
xs = x0 + t * e + h * n        # the point x'
foot = x0 + t * e
dist = np.linalg.norm(np.cross(e, xs - x0)) / np.linalg.norm(e)
assert np.isclose(dist, h) and np.isclose((xs - foot) @ e, 0)

fig = plt.figure(figsize=(6.4, 4.8))
elev, azim = view.best_view([e, n, np.cross(e, n), *np.eye(3)], pairs=[(e, n)])
ax = v3d.new_axes(fig, 111, ((-0.1, 3.4), (-0.1, 2.0), (-0.1, 2.0)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.axes_xyz(ax, (3.2, 2.8, 1.9))
v3d.segment(ax, x0 - 0.5 * e, x0 + 1.9 * e, lafig.VECTOR, lw=1.8)
v3d.parallelogram(ax, x0, e, xs - x0, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.arrow(ax, x0, lafig.INK, r"$x^0$", offset=(0.0, 0.0, 0.3))
v3d.arrow(ax, e, lafig.IMAGE, r"$e$", start=x0, lw=2.6, offset=(0.0, 0.15, -0.2))
v3d.arrow(ax, xs - x0, lafig.VECTOR, r"$x'$", start=x0, offset=(0.0, 0.0, 0.2))
v3d.segment(ax, xs, foot, lafig.HIGHLIGHT, lw=2.0)
v3d.right_angle(ax, foot, e, xs - foot, 0.16, lafig.INK)
mid = (xs + foot) / 2
ax.text(*(mid + np.array([0.15, 0.0, 0.0])), r"$d$", color=lafig.HIGHLIGHT, ha="center", va="center", zorder=6)

view.trim(lafig.save(fig, 3, "line_point_distance"))
