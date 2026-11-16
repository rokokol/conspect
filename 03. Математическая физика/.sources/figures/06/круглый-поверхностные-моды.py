"""Amplitude |u| of the guided (surface) eigenfunctions of the families m = 1..4 at V = 8."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import круглый_расчёт as cc  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

V = 8.0
x = np.linspace(-3, 3, 601)
X, Y = np.meshgrid(x, x)
R, T = np.hypot(X, Y), np.arctan2(Y, X)
theta = np.linspace(0, 2 * np.pi, 200)

fig, axes = plt.subplots(2, 2, figsize=(7.2, 7.2), constrained_layout=True)
for ax, m in zip(axes.flat, range(1, 5)):
    lam = cc.guided_root(V, m)
    Z = np.abs(cc.field(R, T, m, V, lam))
    Z /= Z.max()
    im = ax.pcolormesh(X, Y, Z, shading="gouraud", cmap="ddlc_seq", vmin=0, vmax=1, rasterized=True)
    ax.plot(np.cos(theta), np.sin(theta), color=mffig.INK, linewidth=1.2)
    ax.set_aspect("equal")
    ax.set_title(rf"$m={m}\quad\lambda={mffig.num(lam, 3, math=True)}$")
    ax.set_xticks([-2, 0, 2])
    ax.set_yticks([-2, 0, 2])
cbar = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.03)
cbar.set_label(r"$|u|/\max|u|$")
mffig.save(fig, 6, "круглый-поверхностные-моды")
