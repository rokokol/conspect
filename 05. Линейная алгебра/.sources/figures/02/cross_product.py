"""Orientation of a triple of vectors and the cross product z = [x, y] with its parallelogram."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402

# right triple: the shortest turn from e1 to e2 is counter-clockwise seen from the tip of e3
E1, E2, E3 = np.array([1.6, 0, 0]), np.array([0, 1.6, 0]), np.array([0, 0, 1.6])

x = np.array([2.0, 0.0, 0.0])
y = np.array([0.7, 1.7, 0.0])
z = np.cross(x, y)
assert np.allclose(z @ x, 0) and np.allclose(z @ y, 0)
area = np.linalg.norm(z)
assert np.isclose(area, np.linalg.norm(x) * np.linalg.norm(y) * np.sin(np.arccos(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))))
assert np.linalg.det(np.array([x, y, z])) > 0  # x, y, [x, y] is a right triple
z = z / np.linalg.norm(z) * 2.0  # drawn with a convenient length

fig = plt.figure(figsize=(12.2, 4.4))
LIM = ((-0.3, 2.3), (-0.3, 2.3), (-1.9, 2.0))


def turn(ax):
    """The arc of the shortest turn from e1 to e2."""
    t = np.linspace(0, np.pi / 2, 40)
    r = 0.55
    ax.plot(r * np.cos(t), r * np.sin(t), 0 * t, color=lafig.HIGHLIGHT, lw=1.8)


ax = v3d.new_axes(fig, 131, LIM)
ax.set_title("Правая тройка", color=lafig.INK, fontsize=11)
v3d.arrow(ax, E1, lafig.VECTOR, r"$e^1$", offset=(0.25, 0, 0))
v3d.arrow(ax, E2, lafig.VECTOR, r"$e^2$", offset=(0, 0.25, 0))
v3d.arrow(ax, E3, lafig.VECTOR, r"$e^3$", offset=(0, 0, 0.25))
turn(ax)

ax = v3d.new_axes(fig, 132, LIM)
ax.set_title("Левая тройка", color=lafig.INK, fontsize=11)
v3d.arrow(ax, E1, lafig.VECTOR, r"$e^1$", offset=(0.25, 0, 0))
v3d.arrow(ax, E2, lafig.VECTOR, r"$e^2$", offset=(0, 0.25, 0))
v3d.arrow(ax, -E3, lafig.VECTOR, r"$e^3$", offset=(0, 0, -0.25))
turn(ax)

ax = v3d.new_axes(fig, 133, ((-0.3, 3.0), (-0.3, 2.3), (-0.3, 2.6)), elev=26)
ax.set_title(r"$z=[x,y]$", color=lafig.INK, fontsize=11)
v3d.parallelogram(ax, (0, 0, 0), x, y, lafig.AUX, alpha=0.55)
v3d.arrow(ax, x, lafig.VECTOR, r"$x$", offset=(0.25, 0, 0))
v3d.arrow(ax, y, lafig.VECTOR, r"$y$", offset=(0, 0.25, 0))
v3d.arrow(ax, z, lafig.IMAGE, r"$z$", lw=2.6, offset=(0, 0, 0.25))
c = 0.28
ax.plot([c, c, 0], [0, 0, 0], [0, c, c], color=lafig.MUTED, lw=1.0)
ax.text(*(0.5 * (x + y) + np.array([0.0, 0.0, 0.0])),r"$S=|z|$", color=lafig.INK, ha="center", va="center")

lafig.save(fig, 2, "cross_product")
