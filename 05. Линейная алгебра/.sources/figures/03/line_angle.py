"""The angle between two lines y = k1 x + b1 and y = k2 x + b2: phi = alpha2 - alpha1, tan phi = (k2 - k1) / (1 + k1 k2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

al1, al2 = np.deg2rad(18.0), np.deg2rad(58.0)
k1, k2 = np.tan(al1), np.tan(al2)
assert np.isclose(np.tan(al2 - al1), (k2 - k1) / (1 + k1 * k2))

c = np.array([1.6, 1.0])  # the common point of the lines

fig, ax = plt.subplots(figsize=(6.2, 4.4))
geo2d.new_axes(ax, (-0.8, 5.2), (-0.6, 3.4))
ax.plot([c[0], 5.0], [c[1], c[1]], color=lafig.AUX, lw=1.0, ls="--")
geo2d.line(ax, c, (np.cos(al1), np.sin(al1)), (1.9, 3.2), lafig.VECTOR, lw=2.0)
geo2d.line(ax, c, (np.cos(al2), np.sin(al2)), (1.3, 2.0), lafig.IMAGE, lw=2.0)
geo2d.angle(ax, c, 0, np.degrees(al1), 0.8, lafig.HIGHLIGHT, r"$\alpha_1$", 1.0)
geo2d.angle(ax, c, 0, np.degrees(al2), 1.3, lafig.HIGHLIGHT, r"$\alpha_2$", 1.55)
geo2d.angle(ax, c, np.degrees(al1), np.degrees(al2), 1.9, lafig.HIGHLIGHT, r"$\varphi$", 2.15)
end1 = c + 3.2 * np.array([np.cos(al1), np.sin(al1)])
end2 = c + 2.0 * np.array([np.cos(al2), np.sin(al2)])
ax.text(end1[0] + 0.1, end1[1] - 0.3, r"$y=k_1x+m_1$", color=lafig.INK, ha="right", va="top")
ax.text(end2[0] + 0.1, end2[1], r"$y=k_2x+m_2$", color=lafig.INK, ha="left", va="center")

lafig.save(fig, 3, "line_angle")
