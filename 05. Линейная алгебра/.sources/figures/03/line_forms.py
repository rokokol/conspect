"""A line in the plane: the parametric equation x = x0 + theta e and the normal equation (x, p) - d = 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geo2d  # noqa: E402
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.2))

# (a) parametric: the line through x0 parallel to e
x0 = np.array([0.8, 1.0])
e = np.array([1.1, 0.4])
theta = 2.2
x = x0 + theta * e
geo2d.new_axes(a, (-0.3, 4.4), (-0.3, 2.9))
a.set_title("Параметрическое", color=lafig.INK, fontsize=11)
geo2d.line(a, x0, e, (2.2, 3.4), lafig.AUX, lw=1.4)
geo2d.arrow(a, (0, 0), x0, lafig.VECTOR)
nrm = np.array([-e[1], e[0]]) / np.hypot(*e)
geo2d.arrow(a, x0 + 0.7 * nrm, theta * e, lafig.HIGHLIGHT, lw=1.2, style="<|-|>")
geo2d.arrow(a, (0, 0), x, lafig.VECTOR)
geo2d.arrow(a, x0, e, lafig.IMAGE, lw=2.6)
a.text(x0[0] / 2 - 0.1, x0[1] / 2 + 0.05, r"$x^0$", color=lafig.INK, ha="right", va="center")
a.text(x0[0] + e[0] / 2 - 0.08, x0[1] + e[1] / 2 + 0.2, r"$e$", color=lafig.INK, ha="center", va="bottom")
tm = x0 + theta * e / 2 + 0.95 * nrm
a.text(tm[0], tm[1], r"$\theta e$", color=lafig.HIGHLIGHT, ha="center", va="center")
a.text(x[0] / 2 + 0.55, x[1] / 2 - 0.5, r"$x=x^0+\theta e$", color=lafig.INK, ha="center", va="center")

# (b) normal: p is the unit normal, d the signed distance from the origin
alpha_p = np.deg2rad(35.0)
p = np.array([np.cos(alpha_p), np.sin(alpha_p)])
d = 2.4
u = np.array([np.sin(alpha_p), -np.cos(alpha_p)])
foot = d * p
xp = foot + 1.1 * u
assert np.isclose(xp @ p - d, 0)
geo2d.new_axes(b, (-0.3, 4.4), (-0.3, 2.9))
b.set_title("Нормальное", color=lafig.INK, fontsize=11)
geo2d.line(b, foot, u, (1.2, 2.4), lafig.AUX, lw=1.4)
geo2d.arrow(b, (0, 0), foot, lafig.AUX, lw=1.2, ls="--", style="-")
geo2d.arrow(b, (0, 0), p, lafig.IMAGE, lw=2.6)
geo2d.arrow(b, (0, 0), xp, lafig.VECTOR)
geo2d.square(b, foot, -p, u)
a1, a2 = np.degrees(np.arctan2(xp[1], xp[0])), np.degrees(alpha_p)
geo2d.angle(b, (0, 0), a1, a2, 0.75, lafig.HIGHLIGHT, r"$\alpha$", 0.97)
b.text(p[0] * 0.5 - 0.17, p[1] * 0.5 + 0.2, r"$p$", color=lafig.INK, ha="center", va="center")
b.text(foot[0] * 0.55 + 0.15, foot[1] * 0.55 + 0.3, r"$d$", color=lafig.INK, ha="center", va="center")
b.text(xp[0] * 0.6, xp[1] * 0.6 - 0.22, r"$x$", color=lafig.INK, ha="center", va="center")

lafig.save(fig, 3, "line_forms")
