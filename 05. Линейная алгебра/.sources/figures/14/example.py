"""The curve 3x1^2 + 10x1x2 + 3x2^2 - 2x1 - 14x2 - 13 = 0 in the axes x1, x2 and in the reduced axes z1, z2 (x = x0 + Tz)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conics  # noqa: E402

A = np.array([[3.0, 5.0], [5.0, 3.0]])
a = np.array([-1.0, -7.0])
a0 = -13.0
phi1 = -np.pi / 4
T = np.array([[np.cos(phi1), -np.sin(phi1)], [np.sin(phi1), np.cos(phi1)]])
assert np.allclose(T.T @ A @ T, np.diag([-2.0, 8.0]))
x0 = np.linalg.solve(A, -a)                                          # the centre: Ax + a = 0
assert np.allclose(x0, [2.0, -1.0])
assert np.isclose(a0 + a @ x0, -8.0)                                 # the free term in the centre: a0 + (a, x0)


def curve(x):
    return x @ A @ x + 2 * a @ x + a0


t = np.linspace(-1.7, 1.7, 400)
branches = []
for s in (1, -1):
    z = np.vstack([2.0 * np.sinh(t), s * np.cosh(t)])                # -z1^2/4 + z2^2 = 1
    pts = x0[:, None] + T @ z
    assert np.allclose([curve(p) for p in pts.T], 0.0, atol=1e-8)
    branches.append(pts)

fig, ax = plt.subplots(figsize=(6.6, 5.2))
xl, yl = (-3.0, 7.0), (-5.6, 3.6)
conics.frame(ax, xl, yl, xlabel="$x_1$", ylabel="$x_2$")
L = 6.0
for k, col in enumerate((lafig.IMAGE, lafig.IMAGE)):
    d = T[:, k]
    ax.annotate("", xy=x0 + L * d, xytext=x0 - 3.2 * d,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5, shrinkA=0, shrinkB=0))
conics.label(ax, x0 + 4.2 * T[:, 0], r"$z_1$", (0.35, -0.1))
conics.label(ax, x0 + 3.7 * T[:, 1], r"$z_2$", (-0.35, 0.0))
for sgn in (1, -1):                                                  # the asymptotes z2 = +-z1/2
    d = T @ np.array([2.0, sgn * 1.0])
    d = d / np.linalg.norm(d)
    ax.plot(*zip(x0 - 7 * d, x0 + 7 * d), color=lafig.AUX, lw=1.2, ls="--")
for pts in branches:
    ax.plot(pts[0], pts[1], color=lafig.VECTOR, lw=2.2)
ax.plot([x0[0], x0[0]], [0, x0[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot([0, x0[0]], [x0[1], x0[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot(*x0, "o", color=lafig.HIGHLIGHT, ms=7)
ax.plot(0, 0, "o", color=lafig.INK, ms=4)
ax.plot([x0[0], x0[0] + 1.2], [x0[1]] * 2, color=lafig.MUTED, lw=0.8, ls=":")
arc = np.linspace(0, np.pi / 4, 50)
ax.plot(x0[0] + 0.8 * np.cos(arc), x0[1] + 0.8 * np.sin(arc), color=lafig.HIGHLIGHT, lw=1.6)
conics.label(ax, x0, r"$\pi/4$", (1.35, 0.35), color=lafig.HIGHLIGHT, halo=True)
conics.label(ax, x0, r"$x^0=(2,-1)$", (-0.25, -0.6), color=lafig.HIGHLIGHT, ha="right", halo=True)
conics.label(ax, (x0[0], 0), r"$2$", (0.0, 0.35))
conics.label(ax, (0, x0[1]), r"$-1$", (-0.35, 0.0))
conics.label(ax, (0, 0), r"$0$", (-0.3, 0.3))

fig.legend(handles=[conics.line(lafig.VECTOR, r"кривая $-\frac{z_1^2}{4}+z_2^2=1$"),
                    conics.line(lafig.IMAGE, r"оси $z_1$, $z_2$", lw=1.5),
                    conics.line(lafig.AUX, "асимптоты", lw=1.2, ls="--"),
                    conics.dot(lafig.HIGHLIGHT, "центр $x^0$")],
           loc="lower center", ncol=4, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1))

lafig.save(fig, 14, "example-hyperbola")
