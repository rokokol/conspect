"""A plane cut along the ray {x1 = 0, x2 >= 0} and u = x2^2 in the upper right quarter, 0 elsewhere.

Every horizontal line in the domain is cut into pieces, and u is constant on each piece,
so u_x1 = 0. Still u(-1, 1) = 0 and u(1, 1) = 1: the path between them has to go round
the cut, and on the way round x2 changes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

LIM = 2.0
DETOUR_Y = -0.7
LINES = dufig.P["rule"]  # FIELD is too pale on the colormap
DETOUR = dufig.SOLUTION

x1, x2 = np.meshgrid(np.linspace(-LIM, LIM, 401), np.linspace(-LIM, LIM, 401))
u = np.where((x1 > 0) & (x2 > 0), x2**2, 0.0)

fig, ax = plt.subplots(figsize=(5.6, 4.8))
mesh = ax.pcolormesh(x1, x2, u, cmap="ddlc_seq", shading="auto", vmin=0, vmax=LIM**2)
fig.colorbar(mesh, ax=ax, label=r"$u$")

for y in (1.0, -1.0):
    pieces = [(-LIM, -0.04), (0.04, LIM)] if y > 0 else [(-LIM, LIM)]
    for a, b in pieces:
        ax.plot([a, b], [y, y], color=LINES, linewidth=1.6, linestyle="--", zorder=2)

ax.plot([-1, -1, 1, 1], [1, DETOUR_Y, DETOUR_Y, 1], color=DETOUR, linewidth=2.0, zorder=3)
ax.plot([0, 0], [0, LIM], color=dufig.INK, linewidth=4.0, solid_capstyle="butt", zorder=4)

for (px, py), value in (((-1, 1), "0"), ((1, 1), "1")):
    ax.plot(px, py, marker="o", markersize=7, color=dufig.HIGHLIGHT, markeredgecolor=dufig.INK, zorder=5)
    ax.annotate(rf"$u={value}$", (px, py), xytext=(0, 10), textcoords="offset points",
                ha="center", color=dufig.INK, zorder=6)

ax.set_xlim(-LIM, LIM)
ax.set_ylim(-LIM, LIM)
ax.set_aspect("equal")
ax.set_xlabel(r"$x_1$")
ax.set_ylabel(r"$x_2$")
ax.set_title(r"$u_{x_1}=0$, но $u$ зависит от $x_1$")

handles = [
    Line2D([], [], color=dufig.INK, linewidth=4.0, label="разрез: не входит в область"),
    Line2D([], [], color=LINES, linewidth=1.6, linestyle="--", label="горизонтали: на куске $u$ постоянна"),
    Line2D([], [], color=DETOUR, linewidth=2.0, label="путь в обход разреза"),
]
ax.legend(handles=handles, loc="lower left", fontsize=7)

dufig.save(fig, 12, "cut-plane")
