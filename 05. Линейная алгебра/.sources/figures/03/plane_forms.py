"""A plane in space: the parametric equation x = x0 + a1 e1 + a2 e2 and the normal equation (x, p) - q = 0."""
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

fig = plt.figure(figsize=(11.4, 4.8))

# (a) parametric: the plane through x0 spanned by e1, e2
x0 = np.array([0.7, 0.5, 0.9])
e1 = np.array([1.2, 0.1, 0.0])
e2 = np.array([0.0, 1.0, 0.5])
a1, a2 = 0.9, 0.8
x = x0 + a1 * e1 + a2 * e2
elev, azim = view.best_view([e1, e2, np.cross(e1, e2), *np.eye(3)], normals=[np.cross(e1, e2)], pairs=[(e1, e2), (x0, e1)])
ax = v3d.new_axes(fig, 121, ((-0.2, 3.2), (-0.1, 2.4), (-0.1, 2.0)), elev=elev, azim=azim)
ax.computed_zorder = False
ax.set_title("Параметрическое", color=lafig.INK, fontsize=11)
v3d.axes_xyz(ax, (3.0, 1.5, 1.9))
v3d.parallelogram(ax, x0 - 0.5 * e1 - 0.4 * e2, 2.4 * e1, 2.0 * e2, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.arrow(ax, x0, lafig.VECTOR, r"$x^0$", offset=(-0.15, -0.1, 0.0))
v3d.arrow(ax, e1, lafig.IMAGE, r"$e^1$", start=x0, lw=2.6, offset=(0.25, 0.1, -0.3))
v3d.arrow(ax, e2, lafig.IMAGE, r"$e^2$", start=x0, lw=2.6, offset=(0.0, 0.2, 0.05))
v3d.segment(ax, x0, x0 + a1 * e1, lafig.MUTED, ls="--")
v3d.segment(ax, x0 + a1 * e1, x, lafig.MUTED, ls="--")
v3d.arrow(ax, x, lafig.VECTOR, r"$x$", offset=(0.1, 0.0, 0.2))

# (b) normal: p is the unit normal, q the signed distance from the origin
p = np.array([0.6, 0.5, 0.62])
p = p / np.linalg.norm(p)
q = 1.5
u = np.cross(p, [0, 0, 1.0])
u = u / np.linalg.norm(u)
w = np.cross(p, u)
foot = q * p
xp = foot + 0.7 * u + 0.5 * w
assert np.isclose(xp @ p - q, 0)
elev, azim = view.best_view([p, u, w, *np.eye(3)], normals=[p], pairs=[(p, xp - foot), (p, u)])
ax = v3d.new_axes(fig, 122, ((-0.1, 2.6), (-0.1, 2.4), (-0.1, 2.0)), elev=elev, azim=azim)
ax.computed_zorder = False
ax.set_title("Нормальное", color=lafig.INK, fontsize=11)
v3d.axes_xyz(ax, (2.5, 2.3, 1.9))
v3d.parallelogram(ax, foot - 1.0 * u - 0.9 * w, 2.0 * u, 1.8 * w, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.segment(ax, p, foot, lafig.INK, ls="--")
v3d.arrow(ax, p, lafig.IMAGE, r"$p$", lw=2.6, offset=(0.0, 0.0, -0.2))
v3d.arrow(ax, xp, lafig.VECTOR, r"$x$", offset=(0.1, 0.0, 0.15))
v3d.segment(ax, foot, xp, lafig.MUTED, ls="--")
ax.text(*(0.5 * (p + foot) + 0.2 * u), r"$q$", color=lafig.INK, ha="center", va="center", zorder=6)

view.trim(lafig.save(fig, 3, "plane_forms"))
