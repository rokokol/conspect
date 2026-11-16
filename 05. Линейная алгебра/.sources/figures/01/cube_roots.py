"""The three cube roots of z: one circle of radius |z|^(1/3), arguments phi/3 + 2 pi k/3."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cmath  # noqa: E402
import math  # noqa: E402

import cplane  # noqa: E402
import lafig  # noqa: E402
import numpy as np  # noqa: E402

rho, phi = 3.375, math.radians(125)
z = cmath.rect(rho, phi)
n = 3
r = rho ** (1 / n)
roots = [cmath.rect(r, (phi + 2 * math.pi * k) / n) for k in range(n)]
assert all(abs(w**n - z) < 1e-12 for w in roots)

fig, ax = cplane.new_plane((-3.9, 2.4), (-2.3, 3.4), size=(5.6, 5.0))

t = np.linspace(0, 2 * math.pi, 400)
ax.plot(r * np.cos(t), r * np.sin(t), ls="--", color=lafig.AUX, lw=1.2)

cplane.vector(ax, z, lafig.VECTOR)
ax.plot(z.real, z.imag, "o", color=lafig.VECTOR, ms=6)
ax.text(z.real - 0.08, z.imag + 0.05, r"$z$", color=lafig.VECTOR, ha="right", va="bottom")
cplane.angle(ax, 0.55, 0, math.degrees(phi), lafig.HIGHLIGHT, r"$\varphi$", 0.78)

for k, w in enumerate(roots):
    cplane.vector(ax, w, lafig.IMAGE, lw=1.8)
    ax.plot(w.real, w.imag, "o", color=lafig.IMAGE, ms=6)
    dx = 0.1 * np.sign(w.real) if abs(w.real) > 1e-9 else 0.1
    ax.text(w.real + 1.3 * dx, w.imag + 0.1, rf"$z_{k}$", color=lafig.INK, ha="left" if dx > 0 else "right", va="bottom")

cplane.angle(ax, 0.3, 0, math.degrees(phi / n), lafig.HIGHLIGHT, r"$\varphi/3$", 0.43)
ax.text(2.3, -2.2, r"радиус окружности $\sqrt[3]{|z|}$, шаг по углу $2\pi/3$", color=lafig.INK, ha="right", va="bottom")

lafig.save(fig, 1, "cube_roots")
