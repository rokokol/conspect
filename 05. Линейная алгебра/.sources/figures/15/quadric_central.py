"""The four central quadrics with d = 0 or d != 0: ellipsoid, elliptic cone, one-sheet and two-sheet hyperboloid, with the sections z = h and x = 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import q3d  # noqa: E402
import view  # noqa: E402

a, b, c = 1.5, 1.0, 1.0
LIM = ((-2.7, 2.7), (-1.9, 1.9), (-1.5, 1.5))
phi = np.linspace(0, 2 * np.pi, 120)


def rim(k, h):
    """The ellipse of the section z = h with the semi-axes k*a and k*b."""
    return k * a * np.cos(phi), k * b * np.sin(phi), np.full_like(phi, h)


def revolve(radius, z):
    """The surface x = a*r(z)cos(phi), y = b*r(z)sin(phi) over the heights z."""
    P, Z = np.meshgrid(phi, z)
    R = radius(Z)
    return a * R * np.cos(P), b * R * np.sin(P), Z


# surface: x^2/a^2 + y^2/b^2 = r(z)^2 with r^2 = 1 - z^2/c^2, z^2/c^2, 1 + z^2/c^2, z^2/c^2 - 1
cases = {
    "ellipsoid": dict(
        title="эллипсоид",
        z=np.linspace(-c, c, 60), r2=lambda z: 1 - z**2 / c**2, hs=(-0.8, -0.4, 0.0, 0.4, 0.8)),
    "cone": dict(
        title="эллиптический конус",
        z=np.linspace(-1.3, 1.3, 60), r2=lambda z: z**2 / c**2, hs=(-1.0, -0.5, 0.5, 1.0)),
    "one": dict(
        title="однополостный гиперболоид",
        z=np.linspace(-1.3, 1.3, 60), r2=lambda z: 1 + z**2 / c**2, hs=(-1.0, -0.5, 0.0, 0.5, 1.0)),
}

fig = plt.figure(figsize=(7.6, 6.9))
elev, azim = 18, -60
for spec, (name, cs) in zip((221, 222, 223), cases.items()):
    ax = q3d.panel(fig, spec, LIM, cs["title"], elev=elev, azim=azim)
    X, Y, Z = revolve(lambda z, cs=cs: np.sqrt(np.maximum(cs["r2"](z), 0.0)), cs["z"])
    q3d.sheet(ax, X, Y, Z)
    for h in cs["hs"]:
        q3d.curve(ax, *rim(np.sqrt(max(cs["r2"](h), 0.0)), h), lafig.AUX, lw=1.2)
    # the section x = 0 in the plane yz
    zz = cs["z"]
    r = np.sqrt(np.maximum(cs["r2"](zz), 0.0))
    for sign in (1, -1):
        q3d.curve(ax, np.zeros_like(zz), sign * b * r, zz, lafig.HIGHLIGHT, lw=1.8)

# two-sheet hyperboloid: two separate sheets over |z| >= c
ax = q3d.panel(fig, 224, LIM, "двуполостный гиперболоид", elev=elev, azim=azim)
t = np.linspace(0, 1.05, 40)
for sign in (1, -1):
    z = sign * c * np.cosh(t)
    P, T = np.meshgrid(phi, t)
    q3d.sheet(ax, a * np.sinh(T) * np.cos(P), b * np.sinh(T) * np.sin(P), sign * c * np.cosh(T))
    for h in (1.25, 1.5):
        q3d.curve(ax, *rim(np.sqrt(h**2 / c**2 - 1), sign * h), lafig.AUX, lw=1.2)
    for s2 in (1, -1):
        q3d.curve(ax, np.zeros_like(t), s2 * b * np.sinh(t), z, lafig.HIGHLIGHT, lw=1.8)

q3d.key(fig, [(lafig.AUX, 2.0, r"сечения плоскостями $z=h$"), (lafig.HIGHLIGHT, 2.0, r"сечение плоскостью $x=0$")], y=0.02)
fig.subplots_adjust(left=0, right=1, top=0.97, bottom=0.07, wspace=0, hspace=-0.12)
view.trim(lafig.save(fig, 15, "quadric-central"))
