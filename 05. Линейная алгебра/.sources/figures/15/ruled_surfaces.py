"""The two families of straight generators of the one-sheet hyperboloid and of the hyperbolic paraboloid."""
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
fig = plt.figure(figsize=(8.4, 4.6))

# one-sheet hyperboloid: the line through the neck point (a cos t0, b sin t0, 0) with the direction (-a sin t0, b cos t0, +-c);
# the sign -1 gives the family l of the note (alpha(x/a+z/c) = beta(1-y/b), ...), the sign +1 gives l'
ax = q3d.panel(fig, 121, ((-2.6, 2.6), (-1.9, 1.9), (-1.5, 1.5)), "однополостный гиперболоид", elev=16, azim=-58)
phi = np.linspace(0, 2 * np.pi, 120)
S, P = np.meshgrid(np.linspace(-1.3, 1.3, 40), phi)
q3d.sheet(ax, a * np.sqrt(1 + S**2) * np.cos(P), b * np.sqrt(1 + S**2) * np.sin(P), c * S, alpha=0.18)
t = np.linspace(-1.3, 1.3, 2)
for th in np.linspace(0, 2 * np.pi, 16, endpoint=False):
    for sign, color in ((-1, lafig.VECTOR), (1, lafig.HIGHLIGHT)):
        x = a * (np.cos(th) - t * np.sin(th))
        y = b * (np.sin(th) + t * np.cos(th))
        z = sign * c * t
        assert np.allclose(x**2 / a**2 + y**2 / b**2 - z**2 / c**2, 1)
        q3d.curve(ax, x, y, z, color, lw=1.2)
q3d.curve(ax, a * np.cos(phi), b * np.sin(phi), np.zeros_like(phi), lafig.INK, lw=1.6, ls="--")

# hyperbolic paraboloid z = x^2/a^2 - y^2/b^2: the lines x/a - y/b = beta, z = beta (x/a + y/b) and x/a + y/b = lam, z = lam (x/a - y/b)
a2, b2 = 1.3, 1.0
ax = q3d.panel(fig, 122, ((-1.5, 1.5), (-1.2, 1.2), (-1.1, 1.1)), "гиперболический параболоид", elev=24, azim=-52)
U, V = np.meshgrid(np.linspace(-1, 1, 40), np.linspace(-1, 1, 40))
q3d.sheet(ax, a2 * U, b2 * V, U**2 - V**2, alpha=0.18)
w = np.linspace(-1, 1, 2)
for beta in np.linspace(-1, 1, 11):
    # u = x/a, v = y/b: u - v = beta, u + v = w
    u, v = (w + beta) / 2, (w - beta) / 2
    z = beta * w
    assert np.allclose(z, u**2 - v**2)
    q3d.curve(ax, a2 * u, b2 * v, z, lafig.VECTOR, lw=1.2)
    u, v = (beta + w) / 2, (beta - w) / 2
    z = beta * w
    assert np.allclose(z, u**2 - v**2)
    q3d.curve(ax, a2 * u, b2 * v, z, lafig.HIGHLIGHT, lw=1.2)

q3d.key(fig, [(lafig.VECTOR, 2.0, r"семейство прямых $\ell$"), (lafig.HIGHLIGHT, 2.0, r"семейство прямых $\ell'$"),
              (lafig.INK, 1.6, "горловой эллипс", "--")], ncol=3, y=0.0)
fig.subplots_adjust(left=0, right=1, top=0.97, bottom=0.08, wspace=0)
view.trim(lafig.save(fig, 15, "ruled-surfaces"))
