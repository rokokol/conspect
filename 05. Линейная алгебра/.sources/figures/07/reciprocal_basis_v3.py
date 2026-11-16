"""A basis of V3 and its reciprocal basis built from cross products: each reciprocal vector is normal to a face of the basis."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "02"))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402

e = np.array([[1.4, 0.4, 0.1], [0.3, 1.2, 0.3], [0.5, 0.2, 1.1]])
q = np.dot(np.cross(e[0], e[1]), e[2])
assert q > 0
# the reciprocal basis of the lecture: [e2,e3]/Q, -[e1,e3]/Q = [e3,e1]/Q, [e1,e2]/Q
r = np.array([np.cross(e[1], e[2]), -np.cross(e[0], e[2]), np.cross(e[0], e[1])]) / q
assert np.allclose(r @ e.T, np.eye(3))
assert np.allclose(r, np.linalg.inv(e).T)
assert np.isclose(np.dot(np.cross(r[0], r[1]), r[2]), 1 / q)

lim = ((-1.0, 2.2), (-1.0, 2.0), (-0.8, 2.0))
fig = plt.figure(figsize=(10.4, 4.4))

ax = v3d.new_axes(fig, 121, lim, elev=24, azim=-40, zoom=1.5)
ax.set_title("Нормаль к грани основного базиса", color=lafig.INK, fontsize=11)
v3d.parallelogram(ax, (0, 0, 0), e[1], e[2], lafig.AUX, alpha=0.5)
v3d.arrow(ax, e[0], lafig.VECTOR, r"$e^1$", offset=(0.15, 0, 0.12))
v3d.arrow(ax, e[1], lafig.VECTOR, r"$e^2$", offset=(0.15, 0.05, 0))
v3d.arrow(ax, e[2], lafig.VECTOR, r"$e^3$", offset=(0, 0, 0.15))
n1 = r[0] / np.linalg.norm(r[0])
height = e[0] @ n1  # (e1, n) = 1/|r1|: the distance from e1 to the plane of e2, e3
assert np.isclose(height, 1 / np.linalg.norm(r[0]))
v3d.arrow(ax, r[0], lafig.IMAGE, r"$\tilde e^1$", lw=2.8, offset=(-0.2, 0, 0.05))
v3d.segment(ax, np.zeros(3), height * n1, lafig.HIGHLIGHT, ls="--")
v3d.segment(ax, e[0], height * n1, lafig.HIGHLIGHT, ls="--")
v3d.right_angle(ax, np.zeros(3), n1, e[1], 0.3, color=lafig.INK)
ax.text2D(0.5, 0.04, "пунктир — высота $e^1$\nнад гранью, $1/|\\tilde e^1|$", transform=ax.transAxes,
          color=lafig.INK, fontsize=9.5, va="bottom")

ax = v3d.new_axes(fig, 122, lim, elev=24, azim=-40, zoom=1.5)
ax.set_title("Основной и взаимный базисы", color=lafig.INK, fontsize=11)
for k, off in enumerate([(0.15, 0, 0.12), (0.15, 0.05, 0), (0, 0, 0.15)]):
    v3d.arrow(ax, e[k], lafig.VECTOR, rf"$e^{k + 1}$", offset=off)
for k, off in enumerate([(-0.35, 0, -0.05), (0.1, 0.1, 0.1), (-0.15, 0, 0.1)]):
    v3d.arrow(ax, r[k], lafig.IMAGE, rf"$\tilde e^{k + 1}$", lw=2.8, offset=off)
ax.text2D(0.58, 0.04, r"$e^k$ — основной базис" + "\n" + r"$\tilde e^k$ — взаимный базис" + "\n" + r"$(\tilde e^k,e^l)=\delta_{kl}$",
          transform=ax.transAxes, color=lafig.INK, fontsize=9.5, va="bottom")

lafig.save(fig, 7, "reciprocal_basis_v3")
