"""Focus-directrix property r = e d of the ellipse and the hyperbola, with the directrix x = a/e of the right focus."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conics  # noqa: E402


def panel(ax, a, b, kind, t0, title, xl, yl):
    c = np.sqrt(a**2 - b**2) if kind == "ellipse" else np.sqrt(a**2 + b**2)
    e = c / a
    F = np.array([c, 0.0])
    xd = a / e                                                       # directrix x = a/e = a^2/c
    M = np.array([a * np.cos(t0), b * np.sin(t0)]) if kind == "ellipse" else np.array([a * np.cosh(t0), b * np.sinh(t0)])
    r, d = np.linalg.norm(M - F), abs(xd - M[0])
    assert np.isclose(r, e * d)                                      # the focus-directrix property
    assert (e < 1) == (kind == "ellipse")
    conics.frame(ax, xl, yl)
    ax.set_title(title + rf",  $e={lafig.num(e, 2, math=True)}$", color=lafig.INK)
    if kind == "ellipse":
        t = np.linspace(0, 2 * np.pi, 400)
        ax.plot(a * np.cos(t), b * np.sin(t), color=lafig.VECTOR, lw=2.2)
        ax.plot(-F[0], 0, "o", color=lafig.MUTED, ms=5)
    else:
        t = np.linspace(-1.8, 1.8, 400)
        for s in (1, -1):
            ax.plot(s * a * np.cosh(t), b * np.sinh(t), color=lafig.VECTOR, lw=2.2)
        ax.plot(-F[0], 0, "o", color=lafig.MUTED, ms=5)
    ax.plot([xd, xd], yl, color=lafig.AUX, lw=1.4, ls="--")
    ax.plot(*zip(F, M), color=lafig.IMAGE, lw=1.6)
    ax.plot(*zip(M, (xd, M[1])), color=lafig.HIGHLIGHT, lw=1.6)
    ax.plot(*F, "o", color=lafig.HIGHLIGHT, ms=7)
    ax.plot(*M, "o", color=lafig.VECTOR, ms=7)
    conics.label(ax, F, r"$F$", (0.0, -0.3), color=lafig.HIGHLIGHT)
    conics.label(ax, M, r"$M$", (0.0, 0.3))
    conics.label(ax, (F + M) / 2, r"$r$", (-0.12, -0.25) if kind == "ellipse" else (0.1, -0.25))
    conics.label(ax, ((M[0] + xd) / 2, M[1]), r"$d$", (0.0, 0.25))
    conics.label(ax, (xd, yl[0]), rf"$x={lafig.num(xd, 2, math=True)}$", (0.1, 0.35), ha="left")


fig, (left, right) = plt.subplots(1, 2, figsize=(9.6, 4.4))
panel(left, 2.5, 1.8, "ellipse", 1.0, "Эллипс", (-3.3, 5.2), (-2.4, 2.6))
panel(right, 1.5, 1.0, "hyperbola", 0.7, "Гипербола", (-3.6, 3.6), (-2.5, 2.7))
fig.legend(handles=[conics.line(lafig.VECTOR, "кривая"),
                    conics.line(lafig.AUX, "директриса $x=a/e$ правого фокуса", lw=1.4, ls="--"),
                    conics.line(lafig.IMAGE, r"расстояние $r$ до фокуса", lw=1.6),
                    conics.line(lafig.HIGHLIGHT, r"расстояние $d$ до директрисы, $r=ed$", lw=1.6),
                    conics.dot(lafig.MUTED, "левый фокус")],
           loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.14, 1, 1))

lafig.save(fig, 14, "focus-directrix")
