"""Ellipse x^2/a^2 + y^2/b^2 = 1: vertices, foci, the symmetric points of M and the focal radii with r1 + r2 = 2a."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conics  # noqa: E402

a, b = 2.6, 1.6
c = np.sqrt(a**2 - b**2)
t0 = 0.95
M = np.array([a * np.cos(t0), b * np.sin(t0)])
F1, F2 = np.array([-c, 0.0]), np.array([c, 0.0])
assert np.isclose(M[0]**2 / a**2 + M[1]**2 / b**2, 1.0)
r1, r2 = np.linalg.norm(M - F1), np.linalg.norm(M - F2)
assert np.isclose(r1 + r2, 2 * a)                                   # the focal property
assert np.isclose(r1, a + c / a * M[0]) and np.isclose(r2, a - c / a * M[0])

fig, ax = plt.subplots(figsize=(6.6, 4.6))
conics.frame(ax, (-3.4, 3.4), (-2.3, 2.5))
t = np.linspace(0, 2 * np.pi, 400)
ax.plot([-a, a, a, -a, -a], [-b, -b, b, b, -b], color=lafig.AUX, lw=1.0, ls="--")
ax.plot(a * np.cos(t), b * np.sin(t), color=lafig.VECTOR, lw=2.2)
ax.plot(*zip(F1, M, F2), color=lafig.IMAGE, lw=1.6)
for sx, sy in ((-1, 1), (-1, -1), (1, -1)):
    p = np.array([sx * M[0], sy * M[1]])
    ax.plot(p[0], p[1], "o", mfc="none", mec=lafig.MUTED, ms=6)
    ax.plot([p[0], p[0]], [0, p[1]], color=lafig.MUTED, lw=0.8, ls=":")
    ax.plot([0, p[0]], [p[1], p[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot([M[0], M[0]], [0, M[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot([0, M[0]], [M[1], M[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot([-a, a, 0, 0], [0, 0, b, -b], "o", color=lafig.INK, ms=5)
ax.plot([F1[0], F2[0]], [0, 0], "o", color=lafig.HIGHLIGHT, ms=7)
ax.plot(*M, "o", color=lafig.VECTOR, ms=7)

conics.label(ax, M, r"$M(x,y)$", (0.0, 0.22))
conics.label(ax, (-a, 0), r"$(-a,0)$", (-0.05, -0.2), ha="right")
conics.label(ax, (a, 0), r"$(a,0)$", (0.05, -0.2), ha="left")
conics.label(ax, (0, b), r"$(0,b)$", (0.1, 0.18), ha="left")
conics.label(ax, (0, -b), r"$(0,-b)$", (0.1, -0.18), ha="left")
conics.label(ax, F1, r"$F_1(-c,0)$", (0.0, -0.3), color=lafig.HIGHLIGHT)
conics.label(ax, F2, r"$F_2(c,0)$", (0.0, -0.3), color=lafig.HIGHLIGHT)
mid1, mid2 = (F1 + M) / 2, (F2 + M) / 2
conics.label(ax, mid1, r"$r_1$", (-0.17, 0.17))
conics.label(ax, mid2, r"$r_2$", (0.2, 0.1))

fig.legend(handles=[conics.line(lafig.VECTOR, "эллипс"),
                    conics.line(lafig.IMAGE, r"фокальные радиусы, $r_1+r_2=2a$", lw=1.6),
                    conics.dot(lafig.HIGHLIGHT, "фокусы"),
                    conics.dot(lafig.INK, "вершины"),
                    conics.dot(lafig.MUTED, r"точки, симметричные $M$", filled=False),
                    conics.line(lafig.AUX, "прямоугольник $|x|\\leqslant a,\\ |y|\\leqslant b$", lw=1.0, ls="--")],
           loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.13, 1, 1))

lafig.save(fig, 14, "ellipse")
