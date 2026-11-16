"""One step of the fourth-order Runge-Kutta method for y' = y, y(0) = 1, h = 0.2.

Each slope m_i is drawn as a segment through the point where it is evaluated:
m_1 at the left node, m_2 and m_3 at the midpoint (with two different trial values
of y), m_4 at the trial point at the right node. The dotted chord has the weighted
slope (m_1 + 2 m_2 + 2 m_3 + m_4) / 6 and ends at y_1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

H = 0.2
X0, Y0 = 0.0, 1.0


def f(x, y):
    return y


m1 = f(X0, Y0)
p2 = (X0 + H / 2, Y0 + m1 * H / 2)
m2 = f(*p2)
p3 = (X0 + H / 2, Y0 + m2 * H / 2)
m3 = f(*p3)
p4 = (X0 + H, Y0 + m3 * H)
m4 = f(*p4)
slope = (m1 + 2 * m2 + 2 * m3 + m4) / 6
y1 = Y0 + slope * H

xs = np.linspace(X0, X0 + H, 200)

fig, ax = plt.subplots(figsize=(6.4, 5.0))
ax.plot(xs, np.exp(xs), color=dufig.SOLUTION, linewidth=2.2, zorder=2)
ax.plot([X0, X0 + H], [Y0, y1], color=dufig.INK, linewidth=1.2, linestyle=":", zorder=1)

CHORD = 0.04
colours = [dufig.P["plum"], dufig.P["rule"], dufig.P["yuri"], dufig.P["ribbon"]]
points = [(X0, Y0), p2, p3, p4]
slopes = [m1, m2, m3, m4]
handles = [Line2D([], [], color=dufig.SOLUTION, linewidth=2.2, label=r"точное решение $e^x$"),
           Line2D([], [], color=dufig.INK, linewidth=1.2, linestyle=":",
                  label=r"хорда со средним наклоном")]
for i, ((px, py), m, c) in enumerate(zip(points, slopes, colours), start=1):
    ax.plot([px - CHORD, px + CHORD], [py - m * CHORD, py + m * CHORD], color=c,
            linewidth=3, solid_capstyle="round", zorder=3 + i)
    ax.plot([px], [py], marker="o", markersize=5, color=c, markeredgecolor=dufig.INK,
            zorder=3 + i)
    handles.append(Line2D([], [], color=c, linewidth=3,
                          label=rf"$m_{i}={m:.3f}$ в точке $({px:.2f};\ {py:.3f})$"
                          .replace(".", "{,}")))

ax.plot([X0 + H], [y1], marker="o", markersize=8, color=dufig.HIGHLIGHT,
        markeredgecolor=dufig.INK, zorder=9)
handles.append(Line2D([], [], linestyle="none", marker="o", markersize=8,
                      markerfacecolor=dufig.HIGHLIGHT, markeredgecolor=dufig.INK,
                      label=rf"$\tilde y_1={y1:.4f}$".replace(".", "{,}")))

ax.set_xticks([X0, X0 + H / 2, X0 + H])
ax.set_xticklabels([r"$x_j$", r"$x_j+\frac{h}{2}$", r"$x_j+h$"])
ax.set_xlim(X0 - 0.06, X0 + H + 0.06)
ax.set_ylim(0.94, 1.31)
ax.set_title(r"Шаг Рунге–Кутты для $y'=y$, $h=0{,}2$")
ax.legend(handles=handles, loc="upper left", fontsize=8)

dufig.save(fig, 4, "rk4-step")
