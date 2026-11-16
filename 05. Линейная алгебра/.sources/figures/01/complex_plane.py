"""The complex plane: z = a + ib, its modulus, its argument and the conjugate number."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cmath  # noqa: E402
import math  # noqa: E402

import cplane  # noqa: E402
import lafig  # noqa: E402

z = complex(3.0, 2.0)
rho, phi = abs(z), cmath.phase(z)
a, b = z.real, z.imag

fig, ax = cplane.new_plane((-1.0, 4.6), (-3.2, 3.4))

ax.plot([a, a], [0, b], ls="--", color=lafig.AUX, lw=1.2)
ax.plot([0, a], [b, b], ls="--", color=lafig.AUX, lw=1.2)
ax.plot([a, a], [0, -b], ls="--", color=lafig.AUX, lw=1.2)

cplane.vector(ax, z, lafig.VECTOR)
cplane.vector(ax, z.conjugate(), lafig.IMAGE)
for w, c in ((z, lafig.VECTOR), (z.conjugate(), lafig.IMAGE)):
    ax.plot(w.real, w.imag, "o", color=c, ms=6)

cplane.angle(ax, 0.9, 0, math.degrees(phi), lafig.HIGHLIGHT, r"$\varphi$", 1.25)
ax.text(a / 2 - 0.15, b / 2 + 0.2, r"$|z|=\rho$", color=lafig.VECTOR, ha="right", va="bottom")
ax.text(a + 0.12, b + 0.1, r"$z=a+ib$", color=lafig.VECTOR, ha="left", va="bottom")
ax.text(a + 0.12, -b - 0.1, r"$\bar z=a-ib$", color=lafig.INK, ha="left", va="top")
ax.text(a + 0.08, 0.08, r"$a$", color=lafig.INK, ha="left", va="bottom")
ax.text(-0.12, b, r"$b$", color=lafig.INK, ha="right", va="center")

lafig.save(fig, 1, "complex_plane")
