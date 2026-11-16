"""Cross-section of the round waveguide: core Ω_i, cladding Ω_e, boundary Γ and the polar frame."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Circle  # noqa: E402

R_CLAD = 1.9  # drawn extent of the cladding; the cladding itself is unbounded

fig, ax = plt.subplots(figsize=(5.0, 4.6))
ax.add_patch(Circle((0, 0), R_CLAD, facecolor=mffig.CLADDING, edgecolor="none", zorder=0))
ax.add_patch(Circle((0, 0), 1, facecolor=mffig.CORE, edgecolor=mffig.INK, linewidth=1.8, zorder=1))

# axes through the centre
ax.annotate("", xy=(2.15, 0), xytext=(-2.15, 0), arrowprops=dict(arrowstyle="->", color=mffig.INK, linewidth=0.9), zorder=2)
ax.annotate("", xy=(0, 2.1), xytext=(0, -2.1), arrowprops=dict(arrowstyle="->", color=mffig.INK, linewidth=0.9), zorder=2)
ax.text(2.15, -0.1, r"$x_1$", color=mffig.INK, ha="right", va="top")
ax.text(0.08, 2.1, r"$x_2$", color=mffig.INK, ha="left", va="top")

# polar frame: radius to a point of Γ and the angle φ from the x₁ axis
phi0 = np.radians(35)
p = np.array([np.cos(phi0), np.sin(phi0)])
ax.plot([0, p[0]], [0, p[1]], color=mffig.MODE, linewidth=1.8, zorder=3)
ax.plot([p[0]], [p[1]], "o", color=mffig.MODE, markersize=5, zorder=4)
ax.add_patch(Arc((0, 0), 0.7, 0.7, theta1=0, theta2=35, color=mffig.HIGHLIGHT, linewidth=1.6, zorder=3))
ax.text(0.42, 0.09, r"$\varphi$", color=mffig.HIGHLIGHT, ha="left", va="bottom")
ax.text(0.36, 0.44, r"$r$", color=mffig.MODE, ha="right", va="bottom")

ax.text(-0.47, -0.3, r"$\Omega_i$" "\n" r"$-\Delta u=\lambda^2u$", color=mffig.INK, ha="center", va="center", fontsize=9)
ax.text(-1.05, 1.32, r"$\Omega_e$" "\n" r"$-\Delta u=(\lambda^2-V^2)u$", color=mffig.INK, ha="center", va="center")
q = np.radians(-45)
ax.annotate(r"$\Gamma:\ r=1$", xy=(np.cos(q), np.sin(q)), xytext=(1.05, -1.55), color=mffig.INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=mffig.INK, linewidth=0.9))

ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.15, 2.15)
ax.set_aspect("equal")
ax.axis("off")
mffig.save(fig, 6, "круглый-геометрия")
