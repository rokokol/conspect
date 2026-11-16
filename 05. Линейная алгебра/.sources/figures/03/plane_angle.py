"""The angle between two planes in the section orthogonal to their common line: it equals the angle between the normals."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Wedge  # noqa: E402

phi = np.arccos(4 / 21)                      # the example planes of the note
n1 = np.array([2.0, -1.0, 2.0]) / 3
n2 = np.array([6.0, 2.0, -3.0]) / 7
assert np.isclose(n1 @ n2, np.cos(phi))
ph = np.degrees(phi)

dir1 = np.array([1.0, 0.0])
dir2 = np.array([np.cos(phi), np.sin(phi)])
p1 = np.array([0.0, 1.0])                    # looks into the angle, the point x0 lies on its side
p2 = np.array([-np.sin(phi), np.cos(phi)])   # looks out of the angle
assert np.isclose(p1 @ p2, np.cos(phi))

fig, ax = plt.subplots(figsize=(6.2, 4.6))
geo2d.new_axes(ax, (-2.6, 3.2), (-1.5, 3.3), axes=False)
R = 2.8
ax.add_patch(Wedge((0, 0), R, 0, ph, facecolor=lafig.tint(lafig.HIGHLIGHT, 0.25), edgecolor="none", alpha=0.45))
geo2d.line(ax, (0, 0), dir1, (1.9, R), lafig.VECTOR, lw=2.0)
geo2d.line(ax, (0, 0), dir2, (1.9, R), lafig.IMAGE, lw=2.0)
geo2d.arrow(ax, (0, 0), 1.5 * p1, lafig.VECTOR, lw=2.2)
geo2d.arrow(ax, (0, 0), 1.5 * p2, lafig.IMAGE, lw=2.2)
geo2d.angle(ax, (0, 0), 0, ph, 1.3, lafig.HIGHLIGHT, r"$\varphi$", 1.55)
geo2d.angle(ax, (0, 0), 90, 90 + ph, 0.8, lafig.HIGHLIGHT, r"$\varphi$", 1.05)
ax.text(1.5 * p1[0] + 0.1, 1.5 * p1[1] + 0.05, r"$p_1$", color=lafig.INK, ha="left", va="bottom")
ax.text(1.5 * p2[0] - 0.1, 1.5 * p2[1] + 0.05, r"$p_2$", color=lafig.INK, ha="right", va="bottom")
ax.text(R * 0.95, -0.2, r"$\pi_1$", color=lafig.INK, ha="center", va="top")
ax.text(*(-1.9 * dir2 + np.array([0.0, -0.2])), r"$\pi_2$", color=lafig.INK, ha="right", va="top")
x0 = 2.3 * (dir1 + dir2) / np.linalg.norm(dir1 + dir2)
geo2d.dot(ax, x0, lafig.INK)
ax.text(x0[0] + 0.1, x0[1] + 0.05, r"$x^0$", color=lafig.INK, ha="left", va="bottom")
ax.text(1.4, -0.5, r"угол, содержащий $x^0$", color=lafig.HIGHLIGHT, ha="center", va="top")

lafig.save(fig, 3, "plane_angle")
