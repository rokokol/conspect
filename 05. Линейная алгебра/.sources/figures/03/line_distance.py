"""Deviation delta = (x0, p) - d of a point from a line given in the normal form: its sign says on which side the point lies."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

phi = np.deg2rad(35.0)
p = np.array([np.cos(phi), np.sin(phi)])
u = np.array([np.sin(phi), -np.cos(phi)])
d = 2.0
foot = d * p

cases = [
    (r"$\delta>0$", foot + 1.1 * p + 1.0 * u),
    (r"$\delta<0$", foot - 1.3 * p + 0.8 * u),
]

fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.2))
for ax, (title, x0) in zip(axs, cases):
    delta = x0 @ p - d
    assert np.isclose(abs(delta), np.linalg.norm(x0 - (x0 - delta * p)))  # |delta| is the distance to the line
    geo2d.new_axes(ax, (-0.3, 4.2), (-0.7, 2.9))
    ax.set_title(title, color=lafig.INK, fontsize=11)
    geo2d.line(ax, foot, u, (1.6, 2.5), lafig.VECTOR, lw=2.0)
    geo2d.arrow(ax, (0, 0), 3.4 * p, lafig.AUX, lw=1.1, ls="--", style="-")
    geo2d.arrow(ax, (0, 0), p, lafig.IMAGE, lw=2.6)
    base = x0 - delta * p
    geo2d.arrow(ax, x0, -delta * p, lafig.HIGHLIGHT, lw=1.8, style="-")
    geo2d.square(ax, base, np.sign(delta) * p, u, 0.14)
    geo2d.dot(ax, x0, lafig.INK)
    s = np.sign(delta)
    ax.text(x0[0] + s * 0.14, x0[1] + s * 0.14, r"$x^0$", color=lafig.INK, ha="left" if s > 0 else "right",
            va="bottom" if s > 0 else "top")
    ax.text(p[0] * 0.5 + 0.05, p[1] * 0.5 - 0.22, r"$p$", color=lafig.INK, ha="center", va="center")
    mid = (x0 + base) / 2
    ax.text(*(mid + 0.28 * u), r"$|\delta|$", color=lafig.HIGHLIGHT, ha="center", va="center")
    ax.text(*(0.5 * (1 + d) * p - 0.2 * u), r"$d$", color=lafig.INK, ha="center", va="center")
    # the projection of x0 on the direction of p
    q = (x0 @ p) * p
    ax.plot(*zip(q - 0.1 * u, q + 0.1 * u), color=lafig.INK, lw=1.2)
    ax.text(*(q - 0.4 * u), r"$(x^0,p)$", color=lafig.INK, ha="center", va="center")

lafig.save(fig, 3, "line_distance")
