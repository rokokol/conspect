"""Reflection R = I - 2ww^T that maps a onto |a|e or -|a|e: w is parallel to a -/+ |a|e, the mirror is orthogonal to w."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

e = np.array([1.0, 0.0])
a = np.array([1.1, 1.6])
na = np.linalg.norm(a)


def mirror(sign):
    """Unit w and the reflection with R a = sign * |a| e."""
    d = a - sign * na * e
    w = d / np.linalg.norm(d)
    return w, np.eye(2) - 2.0 * np.outer(w, w), np.linalg.norm(d)


for sign in (1, -1):
    w, R, _ = mirror(sign)
    assert np.allclose(R @ a, sign * na * e) and np.allclose(R @ R, np.eye(2))
    assert np.isclose(w @ w, 1.0)
# the numerically safer w has the larger |a - sign |a| e|: here a lies to the right of the vertical axis, so it is a + |a| e
assert mirror(-1)[2] > mirror(1)[2]


def arrow(ax, v, color, label, offset, lw=2.0, ls="-"):
    ax.annotate("", xy=v, xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))
    ax.text(v[0] + offset[0], v[1] + offset[1], label, color=lafig.INK, ha="center", va="center")


def panel(ax, sign, title):
    w, R, _ = mirror(sign)
    ax.set_aspect("equal")
    ax.set_xlim(-2.3, 2.3)
    ax.set_ylim(-2.3, 2.3)
    ax.axhline(0, color=lafig.AUX, lw=0.8, zorder=0)
    ax.axvline(0, color=lafig.AUX, lw=0.8, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title(title, color=lafig.INK)
    m = np.array([-w[1], w[0]])                       # direction of the mirror: orthogonal to w
    ax.plot([-2.2 * m[0], 2.2 * m[0]], [-2.2 * m[1], 2.2 * m[1]], color=lafig.AUX, lw=1.6, ls="--")
    mid = 0.5 * (a + sign * na * e)                    # the segment from a to R a is orthogonal to the mirror and halved by it
    ax.plot(*zip(a, R @ a), color=lafig.INK, lw=0.9, ls=":")
    assert np.isclose(mid @ w, 0.0)
    arrow(ax, e, lafig.MUTED, r"$e$", (0.0, -0.18), lw=1.4)
    arrow(ax, a, lafig.VECTOR, r"$a$", (0.0, 0.2))
    arrow(ax, R @ a, lafig.IMAGE, r"$Ra=" + ("" if sign > 0 else "-") + r"|a|e$", (0.0, -0.22 if sign > 0 else 0.22))
    arrow(ax, w, lafig.HIGHLIGHT, "", (0.0, 0.0), lw=2.4)
    ax.text(*(1.2 * w + 0.15 * m), r"$w$", color=lafig.HIGHLIGHT, ha="center", va="center")


fig, (left, right) = plt.subplots(1, 2, figsize=(8.8, 4.4))
panel(left, 1, r"$\mu=|a|$,  $w\parallel a-|a|e$")
panel(right, -1, r"$\mu=-|a|$,  $w\parallel a+|a|e$")
fig.legend(handles=[Line2D([0], [0], color=lafig.VECTOR, lw=2.0, label=r"вектор $a$"),
                    Line2D([0], [0], color=lafig.IMAGE, lw=2.0, label=r"его образ"),
                    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.0, label=r"нормаль зеркала $w$"),
                    Line2D([0], [0], color=lafig.AUX, lw=1.6, ls="--", label=r"зеркало $w^\perp$")],
           loc="lower center", ncol=4, frameon=False)
fig.tight_layout(rect=(0, 0.07, 1, 1))

lafig.save(fig, 12, "reflection-mirror")
