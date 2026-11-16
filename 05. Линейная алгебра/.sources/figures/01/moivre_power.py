"""Raising to the power 3: the modulus is cubed, the argument is tripled."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cmath  # noqa: E402
import math  # noqa: E402

import cplane  # noqa: E402
import lafig  # noqa: E402

rho, phi = 1.2, math.radians(70)
z = cmath.rect(rho, phi)
z3 = z**3
assert abs(abs(z3) - rho**3) < 1e-12 and abs(cmath.phase(z3) % (2 * math.pi) - 3 * phi) < 1e-12

fig, ax = cplane.new_plane((-2.4, 1.6), (-1.6, 1.6), size=(5.6, 4.4))

cplane.vector(ax, z, lafig.VECTOR)
cplane.vector(ax, z3, lafig.IMAGE)
for w, c in ((z, lafig.VECTOR), (z3, lafig.IMAGE)):
    ax.plot(w.real, w.imag, "o", color=c, ms=6)

cplane.angle(ax, 0.45, 0, math.degrees(phi), lafig.HIGHLIGHT, r"$\varphi$", 0.62)
cplane.angle(ax, 0.30, 0, math.degrees(3 * phi), lafig.HIGHLIGHT, r"$3\varphi$", 0.17)
ax.text(z.real + 0.08, z.imag, r"$z$", color=lafig.VECTOR, ha="left", va="center")
ax.text(z3.real - 0.05, z3.imag - 0.08, r"$z^3$", color=lafig.INK, ha="right", va="top")
ax.text(z3.real / 2 + 0.05, z3.imag / 2 + 0.1, r"$|z|^3$", color=lafig.INK, ha="left", va="bottom", rotation=math.degrees(cmath.phase(z3)) - 180)

lafig.save(fig, 1, "moivre_power")
