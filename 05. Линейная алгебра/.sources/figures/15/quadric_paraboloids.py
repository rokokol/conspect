"""The elliptic paraboloid x^2/a^2 + y^2/b^2 = z and the hyperbolic paraboloid x^2/a^2 - y^2/b^2 = z with the sections z = h and x = 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import q3d  # noqa: E402
import view  # noqa: E402

a, b = 1.3, 1.0
LIM_E = ((-1.8, 1.8), (-1.4, 1.4), (0.0, 1.6))
LIM_H = ((-1.5, 1.5), (-1.2, 1.2), (-1.1, 1.1))
phi = np.linspace(0, 2 * np.pi, 140)
s = np.linspace(-1.2, 1.2, 120)
UM = 1.0     # the half-width of the drawn part of the hyperbolic paraboloid in u and v

fig = plt.figure(figsize=(8.4, 4.4))

# elliptic paraboloid: x = a*r*cos(phi), y = b*r*sin(phi), z = r^2
ax = q3d.panel(fig, 121, LIM_E,"эллиптический параболоид", elev=18, azim=-58)
R, P = np.meshgrid(np.linspace(0, 1.2, 40), phi)
q3d.sheet(ax, a * R * np.cos(P), b * R * np.sin(P), R**2)
for h in (0.25, 0.6, 1.0, 1.4):
    r = np.sqrt(h)
    q3d.curve(ax, a * r * np.cos(phi), b * r * np.sin(phi), np.full_like(phi, h), lafig.AUX, lw=1.2)
q3d.curve(ax, np.zeros_like(s), b * s, s**2, lafig.HIGHLIGHT, lw=1.8)
assert np.allclose((b * s) ** 2 / b**2, s**2)

# hyperbolic paraboloid: x = a*u, y = b*v, z = u^2 - v^2
ax = q3d.panel(fig, 122, LIM_H, "гиперболический параболоид", elev=24, azim=-52)
U, V = np.meshgrid(np.linspace(-UM, UM, 40), np.linspace(-UM, UM, 40))
q3d.sheet(ax, a * U, b * V, U**2 - V**2)
for h in (-0.8, -0.4, 0.4, 0.8):
    r = np.sqrt(abs(h))
    u, v = (r * np.cosh(s), r * np.sinh(s)) if h > 0 else (r * np.sinh(s), r * np.cosh(s))
    for sign in (1, -1):
        uu, vv = (sign * u, v) if h > 0 else (u, sign * v)
        keep = (abs(uu) <= UM) & (abs(vv) <= UM)
        assert np.allclose(uu**2 - vv**2, h)
        q3d.curve(ax, np.where(keep, a * uu, np.nan), np.where(keep, b * vv, np.nan), np.full_like(s, h), lafig.AUX, lw=1.2)
w = np.linspace(-UM, UM, 60)
for sign in (1, -1):
    q3d.curve(ax, a * sign * w, b * w, np.zeros_like(w), lafig.AUX, lw=1.2)
q3d.curve(ax, np.zeros_like(w), b * w, -(w**2), lafig.HIGHLIGHT, lw=1.8)

q3d.key(fig, [(lafig.AUX, 2.0, r"сечения плоскостями $z=h$"), (lafig.HIGHLIGHT, 2.0, r"сечение плоскостью $x=0$")], y=0.0)
fig.subplots_adjust(left=0, right=1, top=0.97, bottom=0.08, wspace=0)
view.trim(lafig.save(fig, 15, "quadric-paraboloids"))
