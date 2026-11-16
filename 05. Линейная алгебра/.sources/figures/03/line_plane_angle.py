"""The angle phi between a line and a plane, in the section through e and p: phi + psi = pi / 2, sin phi = cos psi."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

phi = np.deg2rad(52.0)
e = np.array([np.cos(phi), np.sin(phi)])
p = np.array([0.0, 1.0])
psi = np.arccos(e @ p)
assert np.isclose(phi + psi, np.pi / 2) and np.isclose(np.sin(phi), e @ p)

fig, ax = plt.subplots(figsize=(6.0, 4.6))
geo2d.new_axes(ax, (-2.6, 3.2), (-1.4, 3.3), axes=False)
geo2d.line(ax, (0, 0), (1, 0), (2.4, 2.9), lafig.AUX, lw=2.0)
geo2d.line(ax, (0, 0), e, (1.3, 2.9), lafig.VECTOR, lw=2.0)
geo2d.arrow(ax, (0, 0), 1.9 * e, lafig.VECTOR, lw=2.4)
geo2d.arrow(ax, (0, 0), 1.9 * p, lafig.IMAGE, lw=2.6)
geo2d.square(ax, (0, 0), (1, 0), p, 0.16)
geo2d.angle(ax, (0, 0), 0, np.degrees(phi), 1.0, lafig.HIGHLIGHT, r"$\varphi$", 1.25)
geo2d.angle(ax, (0, 0), np.degrees(phi), 90, 0.8, lafig.HIGHLIGHT, r"$\psi$", 1.05)
ax.text(1.9 * e[0] + 0.08, 1.9 * e[1] - 0.05, r"$e$", color=lafig.INK, ha="left", va="center")
ax.text(1.9 * p[0] - 0.1, 1.9 * p[1] + 0.05, r"$p$", color=lafig.INK, ha="right", va="center")
ax.text(2.9, -0.15, r"$\pi$", color=lafig.INK, ha="right", va="top")
ax.text(*(2.9 * e + np.array([0.1, 0.0])), r"$l$", color=lafig.INK, ha="left", va="center")

lafig.save(fig, 3, "line_plane_angle")
