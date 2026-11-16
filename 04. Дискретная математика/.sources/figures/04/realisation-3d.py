"""A realisation of K4 in R^3: the vertices on a line, every edge a semicircle in its own half-plane (lecture 11)."""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

xs = {1: 0.0, 2: 1.0, 3: 2.0, 4: 3.0}
edges = list(itertools.combinations(xs, 2))
assert len(edges) == 6
fig = plt.figure(figsize=(9.0, 3.6))
ax = fig.add_axes([0.0, 0.1, 1.0, 1.0], projection="3d")
ax.set_axis_off()
ax.view_init(elev=24, azim=-76)

t = np.linspace(0, np.pi, 80)
colours = dmfig.COLOURS + [dmfig.HIGHLIGHT]
angles = np.radians(np.linspace(15, 165, len(edges)))  # a different half-plane for every edge
for k, (u, v) in enumerate(edges):
    phi, col = angles[k], colours[k]
    a, b = xs[u], xs[v]
    cx, r = (a + b) / 2, (b - a) / 2
    rho = r * np.sin(t)
    ax.plot(cx - r * np.cos(t), rho * np.cos(phi), rho * np.sin(phi), color=col, lw=2.6, zorder=3)
    # the outline of the half-plane page the edge lies in
    page = np.array([[-0.1, 0], [3.1, 0], [3.1, 1.6], [-0.1, 1.6], [-0.1, 0]])
    ax.plot(page[:, 0], page[:, 1] * np.cos(phi), page[:, 1] * np.sin(phi), color=col, lw=0.8, alpha=0.45)

ax.plot([-0.3, 3.3], [0, 0], [0, 0], color=dmfig.INK, lw=1.2, ls=":")
for v, x in xs.items():
    ax.scatter([x], [0], [0], s=190, color=dmfig.VERTEX, edgecolor=dmfig.VERTEX_EDGE, linewidth=1.6,
               depthshade=False, zorder=10)
    ax.text(x, 0, -0.32, str(v), ha="center", va="center", fontsize=12, color=dmfig.INK, zorder=11)
ax.set_xlim(-0.4, 3.4)
ax.set_ylim(-1.8, 1.8)
ax.set_zlim(-0.5, 1.8)
ax.set_box_aspect((3.8, 3.6, 2.0), zoom=1.3)
fig.text(0.5, 0.2,"вершины на прямой (пунктир), шесть рёбер $K_4$ — в шести разных полуплоскостях;\n"
         "бледные контуры — полуплоскости, каждая цвета своего ребра",
         ha="center", fontsize=10, color=dmfig.INK, linespacing=1.6)
path = dmfig.save(fig, 4, "realisation-3d")

# the 3D axes box leaves an empty band on top: crop the image to its content
from PIL import Image, ImageChops  # noqa: E402

img = Image.open(path).convert("RGB")
box = ImageChops.difference(img, Image.new("RGB", img.size, img.getpixel((0, 0)))).getbbox()
img.crop((0, max(box[1] - 24, 0), img.width, img.height)).save(path)
