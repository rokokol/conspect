"""The elliptic, hyperbolic and parabolic cylinders: the directrix in the plane z = 0 and the generators parallel to Oz."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import q3d  # noqa: E402
import view  # noqa: E402

a, b, p = 1.5, 1.0, 0.9
LIM = ((-2.4, 2.4), (-1.9, 1.9), (-1.3, 1.3))
H = 1.2
z = np.linspace(-H, H, 2)
t = np.linspace(-1, 1, 160)
phi = np.linspace(0, 2 * np.pi, 160)

# directrix (x(s), y(s)) of every cylinder, as a list of branches
branches = {
    "эллиптический цилиндр": [(a * np.cos(phi), b * np.sin(phi))],
    "гиперболический цилиндр": [(a * np.cosh(0.9 * t), b * np.sinh(0.9 * t)), (-a * np.cosh(0.9 * t), b * np.sinh(0.9 * t))],
    "параболический цилиндр": [((1.5 * t) ** 2 / (2 * p), 1.5 * t)],
}
for X, Y in branches["эллиптический цилиндр"]:
    assert np.allclose(X**2 / a**2 + Y**2 / b**2, 1)
for X, Y in branches["гиперболический цилиндр"]:
    assert np.allclose(X**2 / a**2 - Y**2 / b**2, 1)
for X, Y in branches["параболический цилиндр"]:
    assert np.allclose(Y**2, 2 * p * X)

fig = plt.figure(figsize=(9.6, 3.6))
for spec, (title, parts) in zip((131, 132, 133), branches.items()):
    ax = q3d.panel(fig, spec, LIM, title, elev=20, azim=-38)
    for X, Y in parts:
        q3d.sheet(ax, np.array([X, X]), np.array([Y, Y]), np.array([np.full_like(X, -H), np.full_like(X, H)]))
        for k in range(0, len(X), max(len(X) // 14, 1)):
            q3d.curve(ax, [X[k], X[k]], [Y[k], Y[k]], [-H, H], lafig.AUX, lw=0.9)
        q3d.curve(ax, X, Y, np.zeros_like(X), lafig.HIGHLIGHT, lw=2.0)

q3d.key(fig, [(lafig.HIGHLIGHT, 2.0, r"направляющая в плоскости $z=0$"), (lafig.AUX, 2.0, r"образующие, параллельные $Oz$")], y=0.0)
fig.subplots_adjust(left=0, right=1, top=0.97, bottom=0.1, wspace=0)
view.trim(lafig.save(fig, 15, "quadric-cylinders"))
