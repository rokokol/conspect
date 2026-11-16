"""Projection onto L along M: x = x1 + x2 with x1 = Px in L and x2 = Qx in M; M is not perpendicular to L."""
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

corner = np.array([-2.2, -1.6, 0.0])
a = np.array([4.8, 0.0, 0.0])
b = np.array([0.8, 3.6, 0.0])
m = np.array([0.7, -0.5, 1.6])           # direction of M, oblique to the plane z = 0
x1 = np.array([2.2, 1.0, 0.0])
x2 = 1.0 * m
x = x1 + x2
assert np.isclose(x1[2], 0) and np.allclose(np.cross(x2, m), 0)
assert not np.isclose(m[0] ** 2 + m[1] ** 2, 0)                 # M is not perpendicular to L
s, t = np.linalg.solve(np.column_stack([a[:2], b[:2]]), (x1 - corner)[:2])
assert 0 < s < 1 and 0 < t < 1                                  # x1 lies inside the drawn part of L

fig = plt.figure(figsize=(6.6, 4.8))
elev, azim = view.best_view([x1, x2, x], normals=[np.array([0.0, 0.0, 1.0])], pairs=[(x1, x2)])
ax = v3d.new_axes(fig, 111, ((-2.4, 3.8), (-1.8, 2.2), (-0.9, 2.2)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.parallelogram(ax, corner, a, b, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.segment(ax, -0.5 * m, 1.45 * m, lafig.MUTED, lw=1.3)
v3d.segment(ax, x1, x, lafig.INK, lw=1.2, ls="--")
v3d.segment(ax, x2, x, lafig.INK, lw=1.2, ls="--")
v3d.arrow(ax, x1, lafig.IMAGE, r"$x^1=Px$", lw=2.6, offset=(0.25, -0.25, 0.0), ha="left")
v3d.arrow(ax, x2, lafig.HIGHLIGHT, r"$x^2=Qx$", lw=2.6, offset=(-0.15, 0.0, 0.0), ha="right")
v3d.arrow(ax, x, lafig.VECTOR, r"$x$", lw=2.0, offset=(0.0, 0.0, 0.2))
ax.text(*(corner + 0.9 * a + 0.12 * b), r"$L$", color=lafig.INK, ha="center", va="center", zorder=6)
ax.text(*(1.45 * m + np.array([0.0, 0.0, 0.2])), r"$M$", color=lafig.INK, ha="center", va="center", zorder=6)
ax.text(*(np.array([-0.2, 0.0, -0.1])), r"$0$", color=lafig.INK, ha="center", va="center", zorder=6)

view.trim(lafig.save(fig, 9, "projector"))
