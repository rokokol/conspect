"""Parabola y^2 = 2px: vertex, focus (p/2, 0), directrix x = -p/2 and the equal distances from M to the focus and the directrix."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conics  # noqa: E402

p = 1.4
F = np.array([p / 2, 0.0])
y0 = 1.9
M = np.array([y0**2 / (2 * p), y0])
H = np.array([-p / 2, y0])                                          # the foot of the perpendicular from M to the directrix
assert np.isclose(np.linalg.norm(M - F), np.linalg.norm(M - H))     # focus-directrix property
assert np.isclose(np.linalg.norm(M - F), M[0] + p / 2)

fig, ax = plt.subplots(figsize=(6.4, 4.6))
conics.frame(ax, (-1.6, 4.4), (-2.8, 2.9))
y = np.linspace(-2.7, 2.7, 300)
ax.plot(y**2 / (2 * p), y, color=lafig.VECTOR, lw=2.2)
ax.plot([-p / 2, -p / 2], [-2.8, 2.9], color=lafig.AUX, lw=1.4, ls="--")
ax.plot([M[0], H[0]], [M[1], H[1]], color=lafig.IMAGE, lw=1.6)
ax.plot([F[0], M[0]], [F[1], M[1]], color=lafig.IMAGE, lw=1.6)
ax.plot([M[0], M[0]], [-M[1], M[1]], color=lafig.MUTED, lw=0.8, ls=":")
ax.plot(M[0], -M[1], "o", mfc="none", mec=lafig.MUTED, ms=6)
ax.plot(*M, "o", color=lafig.VECTOR, ms=7)
ax.plot(*F, "o", color=lafig.HIGHLIGHT, ms=7)
ax.plot(0, 0, "o", color=lafig.INK, ms=5)
ax.annotate("", xy=(-p / 2, -0.35), xytext=(0, -0.35),
            arrowprops=dict(arrowstyle="<->", color=lafig.INK, lw=1.0, shrinkA=0, shrinkB=0))

conics.label(ax, M, r"$M(x,y)$", (0.35, 0.28))
conics.label(ax, (M[0], -M[1]), r"$(x,-y)$", (0.55, -0.1))
conics.label(ax, F, r"$F(\frac{p}{2},0)$", (0.2, -0.38), color=lafig.HIGHLIGHT)
conics.label(ax, (0, 0), r"$O$", (0.14, 0.2))
conics.label(ax, (-p / 4, -0.35), r"$\frac{p}{2}$", (0.0, -0.22))
conics.label(ax, (-p / 2, 2.55), r"директриса $x=-\frac{p}{2}$", (0.1, 0.0), ha="left")
conics.label(ax, (M + H) / 2, r"$d$", (0.0, 0.2))
conics.label(ax, (M + F) / 2, r"$r$", (0.2, 0.0))

fig.legend(handles=[conics.line(lafig.VECTOR, "парабола"),
                    conics.line(lafig.AUX, "директриса", lw=1.4, ls="--"),
                    conics.line(lafig.IMAGE, r"расстояния до фокуса и директрисы, $r=d$", lw=1.6),
                    conics.dot(lafig.HIGHLIGHT, "фокус"),
                    conics.dot(lafig.INK, "вершина")],
           loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.13, 1, 1))

lafig.save(fig, 14, "parabola")
