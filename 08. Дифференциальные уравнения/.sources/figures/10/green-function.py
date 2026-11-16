"""Green function G(t, x) of y'' - y' = f, y(0) = 0, y'(1) = 0, as a function of x at fixed t.

y1 = 1 - e^x meets the left condition, y2 = 1 the right one, W = e^x. For x <= t
G = y1(x) y2(t) / W(t) = (1 - e^x) e^(-t); for x >= t G = y2(x) y1(t) / W(t) = (1 - e^t) e^(-t).
The curve is continuous at x = t and its slope jumps there by 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dufig  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

y1 = lambda x: 1 - np.exp(x)
y2 = lambda x: np.ones_like(x)
W = lambda x: np.exp(x)


def G(t, x):
    left = y1(x) * y2(np.full_like(x, t)) / W(t)
    right = y2(x) * y1(np.full_like(x, t)) / W(t)
    return np.where(x <= t, left, right)


xs = np.linspace(0, 1, 801)
ts = [0.2, 0.5, 0.8]
colors = [dufig.CYCLE[0], dufig.SOLUTION, dufig.CYCLE[2]]

# Slope jump at x = t equals 1 for every t, boundary conditions hold.
h = 1e-6
for t in ts:
    jump = (G(t, np.array([t + 2 * h]))[0] - G(t, np.array([t + h]))[0]) / h \
        - (G(t, np.array([t - h]))[0] - G(t, np.array([t - 2 * h]))[0]) / h
    assert abs(jump - 1) < 1e-4, jump
    assert abs(G(t, np.array([0.0]))[0]) < 1e-12
    assert abs(G(t, np.array([1.0]))[0] - G(t, np.array([1 - 1e-4]))[0]) < 1e-9

fig, ax = plt.subplots(figsize=(6.6, 4.2))
for t, c in zip(ts, colors):
    ax.plot(xs, G(t, xs), color=c, linewidth=2.2, label=rf"$t={dufig.num(t, None, math=True)}$")
    ax.plot([t], [G(t, np.array([t]))[0]], "o", color=dufig.HIGHLIGHT, markersize=6, zorder=5)
ax.plot([], [], "o", color=dufig.HIGHLIGHT, label=r"излом при $x=t$, скачок наклона $1$")
ax.axhline(0, color=dufig.MUTED, linewidth=0.9)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$G(t,x)$")
ax.set_title(r"$G(t,x)$ при фиксированном $t$ для $y''-y'=f$, $y(0)=0$, $y'(1)=0$")
ax.legend(loc="lower left", fontsize=8)

dufig.save(fig, 10, "green-function")
