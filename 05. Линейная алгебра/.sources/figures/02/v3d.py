"""Shared drawing of vectors in three-dimensional space for the figures of topic 02."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection  # noqa: E402


def new_axes(fig, spec, lim, elev=22, azim=-62, zoom=1.1):
    """A 3D axes without a frame: the figure draws its own vectors."""
    ax = fig.add_subplot(spec, projection="3d")
    ax.set_axis_off()
    ax.set_xlim(*lim[0])
    ax.set_ylim(*lim[1])
    ax.set_zlim(*lim[2])
    ax.set_box_aspect((lim[0][1] - lim[0][0], lim[1][1] - lim[1][0], lim[2][1] - lim[2][0]), zoom=zoom)
    ax.view_init(elev=elev, azim=azim)
    return ax


def arrow(ax, vec, color, label=None, start=(0, 0, 0), lw=2.2, offset=(0, 0, 0), ha="center"):
    """Arrow from `start` along `vec` with the label near its tip."""
    start = np.asarray(start, float)
    vec = np.asarray(vec, float)
    ax.quiver(*start, *vec, color=color, lw=lw, arrow_length_ratio=0.12, normalize=False)
    if label:
        tip = start + vec + np.asarray(offset, float)
        ax.text(*tip, label, color=lafig.INK, ha=ha, va="center")


def parallelogram(ax, origin, a, b, color, alpha=0.28):
    """Filled parallelogram spanned by a and b at `origin`, with a visible outline."""
    o = np.asarray(origin, float)
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    poly = Poly3DCollection([[o, o + a, o + a + b, o + b]], facecolor=lafig.tint(color, 0.35),
                            edgecolor=color, linewidths=1.2, alpha=alpha)
    ax.add_collection3d(poly)
    return poly


def box_edges(ax, x, y, z, color, lw=1.0):
    """The nine edges of the parallelepiped spanned by x, y, z that do not start at the origin."""
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    corners = {(i, j, k): i * x + j * y + k * z for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    edges = []
    for (i, j, k), p in corners.items():
        if (i, j, k) == (0, 0, 0):
            continue  # the three edges at the origin are the vector arrows themselves
        for d in range(3):
            idx = [i, j, k]
            if idx[d] == 0:
                idx[d] = 1
                edges.append([p, corners[tuple(idx)]])
    ax.add_collection3d(Line3DCollection(edges, colors=color, linewidths=lw, linestyles="--"))


def segment(ax, p, q, color, lw=1.4, ls="-"):
    """Straight segment from p to q."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    ax.plot(*zip(p, q), color=color, lw=lw, ls=ls)


def axes_xyz(ax, length, labels=(r"$x_1$", r"$x_2$", r"$x_3$"), color=None):
    """The three coordinate axes from the origin as thin arrows with their labels at the tips."""
    color = color or lafig.MUTED
    for k, text in enumerate(labels):
        vec = np.zeros(3)
        vec[k] = length[k] if np.ndim(length) else length
        ax.quiver(0, 0, 0, *vec, color=color, lw=1.1, arrow_length_ratio=0.07)
        ax.text(*(vec * 1.08), text, color=lafig.INK, ha="center", va="center")


def arc(ax, a, b, radius, color, center=(0, 0, 0), lw=1.6):
    """Arc of the angle between the directions a and b, drawn in their plane about `center`."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    w = np.arccos(np.clip(a @ b, -1, 1))
    pts = [(np.sin((1 - s) * w) * a + np.sin(s * w) * b) / np.sin(w) for s in np.linspace(0, 1, 30)]
    ax.plot(*(np.asarray(center, float)[:, None] + radius * np.array(pts).T), color=color, lw=lw)


def right_angle(ax, corner, u, w, size, color=None):
    """Square mark of a right angle at `corner` between the directions u and w."""
    color = color or lafig.MUTED
    c = np.asarray(corner, float)
    u, w = np.asarray(u, float), np.asarray(w, float)
    u, w = size * u / np.linalg.norm(u), size * w / np.linalg.norm(w)
    ax.plot(*zip(c + u, c + u + w, c + w), color=color, lw=1.0)
