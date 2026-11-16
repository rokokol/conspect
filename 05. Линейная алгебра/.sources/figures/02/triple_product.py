"""The scalar triple product (x, y, z) as a signed volume: the angle between [x, y] and z is acute or obtuse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import v3d  # noqa: E402

x = np.array([2.0, 0.0, 0.0])
y = np.array([0.6, 1.5, 0.0])
n = np.cross(x, y)
n_hat = n / np.linalg.norm(n)
n_draw = 1.5 * n_hat

cases = [
    ("Угол острый", np.array([0.5, 0.4, 1.5]), "+"),
    ("Угол тупой", np.array([0.5, 0.4, -1.5]), "-"),
]


def arc(ax, a, b, radius, color):
    """Arc of the angle between the directions a and b, drawn in their plane."""
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    w = np.arccos(np.clip(a @ b, -1, 1))
    t = np.linspace(0, 1, 30)
    pts = [(np.sin((1 - s) * w) * a + np.sin(s * w) * b) / np.sin(w) for s in t]
    ax.plot(*(radius * np.array(pts)).T, color=color, lw=1.6)


fig = plt.figure(figsize=(10.4, 4.6))
for k, (title, z, sign) in enumerate(cases):
    volume = np.linalg.det(np.array([x, y, z]))
    assert np.isclose(volume, np.dot(n, z))
    assert (volume > 0) == (sign == "+")
    ax = v3d.new_axes(fig, 121 + k, ((-1.2, 3.4), (-0.4, 2.6), (-2.0, 2.4)), elev=18, azim=-68)
    ax.set_title(title, color=lafig.INK, fontsize=11)
    v3d.box_edges(ax, x, y, z, lafig.AUX)
    v3d.arrow(ax, x, lafig.VECTOR, r"$x$", offset=(0.25, -0.05, 0))
    v3d.arrow(ax, y, lafig.VECTOR, r"$y$", offset=(0, 0.25, 0))
    v3d.arrow(ax, z, lafig.VECTOR, r"$z$", offset=(0, 0, 0.25 * np.sign(z[2])))
    v3d.arrow(ax, n_draw, lafig.IMAGE, r"$[x,y]$", lw=2.6, offset=(-0.45, 0, 0.1))
    arc(ax, n_draw, z, 0.55, lafig.HIGHLIGHT)
    mid = n_hat + z / np.linalg.norm(z)
    ax.text(*(0.8 * mid / np.linalg.norm(mid) + np.array([-0.3, 0, 0]) * (sign == "+") + np.array([0.0, 0.0, -0.45]) * (sign == "-")), r"$\alpha$", color=lafig.HIGHLIGHT, ha="center", va="center")
    ax.text(*(0.5 * (x + y + z) + np.array([0, 0, 0.0])), rf"$(x,y,z)={sign}V$" + "\n" + r"$V$ — объём", color=lafig.INK, ha="center", va="center")

lafig.save(fig, 2, "triple_product")
