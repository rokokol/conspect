"""Gradient clipping on the Rosenbrock valley f = (1-x)^2 + 10 (y-x^2)^2: plain gradient descent against the same
descent with the gradient cut to norm c.

Both runs start at the point of the sandbox gd-песочница.html with eta = 0.06. Without clipping the first
step is eta*|grad| = 2.0 long and the descent leaves the valley and diverges; with c = 1 the step is at most
0.06 long and the descent walks down. eta and c are chosen here to show the effect, not tuned.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402

OUT = fk.attachments(6)
S = oc.Rosenbrock
START = np.array([-1.5, 1.8])
LR, C, STEPS = 0.06, 1.0, 100
BOX = (-2.0, 2.0)


def clipped(c):
    def g(p):
        v = S.grad(p)
        n = np.linalg.norm(v)
        return v if n <= c else c * v / n
    return g


def descend(grad):
    """Path of plain descent, cut at the first point beyond 1e3 from the origin (the run has diverged)."""
    w, pts = START.copy(), [START.copy()]
    for _ in range(STEPS):
        w = w - LR * grad(w)
        pts.append(w)
        if np.abs(w).max() > 1e3:
            break
    return np.array(pts)


plain = descend(S.grad)
cut = descend(clipped(C))
print("first gradient norm", np.linalg.norm(S.grad(START)), "-> step", LR * np.linalg.norm(S.grad(START)))
print("plain: steps before blow-up", len(plain) - 1, "| clipped: final loss", S.f(cut[-1]))
assert np.abs(plain[-1]).max() > 1e3 and S.f(cut[-1]) < 0.2

gx, gy = np.meshgrid(np.linspace(*BOX, 300), np.linspace(*BOX, 300))
Z = S.f(np.stack([gx, gy], axis=-1))

fig, axes = fk.subplots(1, 2, size=(10.4, 4.2), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axes[0]
fk.loss_contourf(ax, gx, gy, Z, n=12)
from matplotlib.patches import FancyArrowPatch  # noqa: E402

g0 = S.grad(START)
jump = START - LR * g0
ax.add_patch(FancyArrowPatch(START, jump, arrowstyle="-|>", mutation_scale=16, color=fk.P["bow"], lw=2.2,
                             zorder=5, clip_on=True))
ax.plot([], [], color=fk.P["bow"], lw=2, label=f"первый шаг без обрезки: длина {fk.num(np.linalg.norm(jump - START), 1)}")
ax.plot(cut[:, 0], cut[:, 1], color=fk.P["monika-eye"], lw=1.6, zorder=3,
        label=f"путь с обрезкой до $c={fk.num(C, None, math=True)}$: шаг не длиннее {fk.num(LR * C, 2)}")
ax.scatter(*START, s=50, color=fk.P["paper"], edgecolor=fk.TEXT, zorder=6)
ax.plot(*S.minimum, marker="x", color=fk.TEXT, ms=9, mew=2, zorder=6)
ax.set_xlim(*BOX)
ax.set_ylim(*BOX)
ax.set_aspect("equal")
ax.set_title("Первый шаг и путь с обрезкой")
ax.legend(loc="lower right", fontsize=7)

ax = axes[1]
for run, c, lab in [(plain, fk.P["bow"], "без обрезки"), (cut, fk.P["monika-eye"], "обрезка до $c=1$")]:
    f = S.f(run)
    ok = np.isfinite(f) & (f < 1e12)
    ax.plot(np.arange(len(f))[ok], f[ok], color=c, lw=2, label=lab)
    if not ok.all():
        k = int(np.argmax(~ok))
        ax.scatter(k - 1, f[k - 1], marker="x", color=c, s=50, zorder=5)
        ax.annotate("расходится", (k - 1, f[k - 1]), xytext=(8, -2), textcoords="offset points", fontsize=7)
ax.set_yscale("log")
ax.set_xlabel("номер шага")
ax.set_ylabel("потеря $f$")
ax.set_title(f"Потеря по шагам, $\\eta={fk.num(LR, None, math=True)}$")
ax.grid(True, axis="y")
ax.legend(loc="upper right")
fig.tight_layout()
fk.save(fig, OUT / "act-grad-clipping.png")
