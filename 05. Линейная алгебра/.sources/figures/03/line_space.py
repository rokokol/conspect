"""A line in space: x = x0 + theta e through the point x0 parallel to e."""
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

x0 = np.array([1.8, 0.5, 0.4])
e = np.array([-0.6, 1.2, 0.5])
theta = 1.4
x = x0 + theta * e

fig = plt.figure(figsize=(6.0, 4.8))
elev, azim = view.best_view([x0, e, *np.eye(3)], pairs=[(x0, e)])
ax = v3d.new_axes(fig, 111, ((-0.1, 3.0), (-0.1, 3.0), (-0.1, 2.4)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.axes_xyz(ax, (2.8, 1.5, 1.8))
v3d.segment(ax, x0 - 0.4 * e, x0 + 1.8 * e, lafig.AUX, lw=1.6)
v3d.arrow(ax, x0, lafig.VECTOR, r"$x^0$", offset=(0.0, -0.35, -0.2))
v3d.arrow(ax, e, lafig.IMAGE, r"$e$", start=x0, lw=2.6, offset=(0.3, 0.0, -0.1))
v3d.arrow(ax, x, lafig.VECTOR, r"$x=x^0+\theta e$", offset=(0.0, 0.0, 0.35))
ax.text(-0.15, -0.15, -0.1, r"$O$", color=lafig.INK, ha="center", va="center")

view.trim(lafig.save(fig, 3, "line_space"))
