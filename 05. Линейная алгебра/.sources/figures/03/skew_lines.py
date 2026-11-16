"""The distance between skew lines: the height of the parallelepiped on e1, e2 and q = x2 - x1 over the base on e1, e2."""
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

# the point x1 is the origin of the drawing
e1 = np.array([1.7, 0.2, 0.0])
e2 = np.array([0.1, 1.5, 0.0])
q = np.array([0.5, -0.3, 1.3])           # x2 - x1
dist = abs(np.linalg.det(np.array([e1, e2, q]))) / np.linalg.norm(np.cross(e1, e2))

# the closest points s e1 on l1 and q + t e2 on l2
s, t = np.linalg.lstsq(np.column_stack([e1, -e2]), q, rcond=None)[0]
P1, P2 = s * e1, q + t * e2
assert np.isclose(np.linalg.norm(P2 - P1), dist)
assert np.isclose((P2 - P1) @ e1, 0) and np.isclose((P2 - P1) @ e2, 0)

fig = plt.figure(figsize=(6.8, 5.2))
elev, azim = view.best_view([e1, e2, q, np.cross(e1, e2)], pairs=[(e1, e2), (e1, q), (e2, q)])
ax = v3d.new_axes(fig, 111, ((-0.8, 3.0), (-1.0, 2.2), (-0.2, 1.6)), elev=elev, azim=azim)
ax.computed_zorder = False
v3d.parallelogram(ax, (0, 0, 0), e1, e2, lafig.AUX, alpha=0.5).set_zorder(1)
v3d.box_edges(ax, e1, e2, q, lafig.AUX)
v3d.segment(ax, -0.5 * e1, 1.5 * e1, lafig.VECTOR, lw=1.8)
v3d.segment(ax, q - 0.4 * e2, q + 1.4 * e2, lafig.IMAGE, lw=1.8)
v3d.arrow(ax, e1, lafig.VECTOR, r"$e^1$", offset=(0.15, 0.0, -0.15))
v3d.arrow(ax, e2, lafig.VECTOR, r"$e^2$", offset=(0.0, 0.2, 0.0))
v3d.arrow(ax, q, lafig.INK, r"$q$", lw=1.6, offset=(0.0, -0.15, 0.1))
v3d.segment(ax, P1, P2, lafig.HIGHLIGHT, lw=2.2)
ax.text(*((P1 + P2) / 2 + np.array([0.2, 0.0, 0.0])), r"$d$", color=lafig.HIGHLIGHT, ha="center", va="center", zorder=6)
ax.text(*(-0.5 * e1 + np.array([0.0, -0.2, -0.1])), r"$l_1$", color=lafig.VECTOR, ha="center", va="center", zorder=6)
ax.text(*(q + 1.4 * e2 + np.array([0.0, 0.1, 0.1])), r"$l_2$", color=lafig.IMAGE, ha="center", va="center", zorder=6)
ax.text(*(-0.2 * np.array([1, 1, 0]) + np.array([0, 0, 0.0])), r"$x^1$", color=lafig.INK, ha="center", va="center", zorder=6)

lafig.save(fig, 3, "skew_lines")
