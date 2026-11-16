"""The plane a x1 + b x2 + c x3 + d = 0 cuts the axes at alpha = -d/a, beta = -d/b, gamma = -d/c."""
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
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

a, b, c, d = 3.0, 2.0, 4.0, -6.0     # 3 x1 + 2 x2 + 4 x3 - 6 = 0
alpha, beta, gamma = -d / a, -d / b, -d / c
A, B, C = np.array([alpha, 0, 0]), np.array([0, beta, 0]), np.array([0, 0, gamma])
for pt in (A, B, C):
    assert np.isclose(a * pt[0] + b * pt[1] + c * pt[2] + d, 0)

fig = plt.figure(figsize=(5.8, 5.0))
elev, azim = view.best_view([A, B, C, *np.eye(3)], normals=[(a, b, c)])
ax = v3d.new_axes(fig, 111, ((-0.1, 3.4), (-0.1, 3.4), (-0.1, 2.0)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.axes_xyz(ax, (3.2, 3.3, 1.9))
tri = Poly3DCollection([[A, B, C]], facecolor=lafig.tint(lafig.AUX, 0.35), edgecolor=lafig.AUX, linewidths=1.4, alpha=0.6)
ax.add_collection3d(tri)
tri.set_zorder(1)
for pt, label, shift in ((A, r"$\alpha$", (0.0, -0.3, -0.05)), (B, r"$\beta$", (0.15, 0.2, 0.0)), (C, r"$\gamma$", (-0.2, 0.0, 0.1))):
    ax.scatter(*pt, color=lafig.HIGHLIGHT, s=30, zorder=5)
    ax.text(*(pt + np.array(shift)), label, color=lafig.HIGHLIGHT, ha="center", va="center", zorder=6)

view.trim(lafig.save(fig, 3, "plane_intercepts"))
