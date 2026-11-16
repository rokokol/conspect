"""Six optimizers on one loss surface: the Rosenbrock valley f = (1-x)^2 + 10 (y-x^2)^2 from one start.

The surface and the start are those of the sandbox gd-песочница.html. Momentum and Nesterov use rho = 0.9,
RMSProp beta = 0.9, Adam its default betas. The step size of every
optimizer is chosen from a log grid as the one with the lowest loss after 100 steps among the runs whose path
stays inside the frame: there is no validation set on a bare surface, and a step that leaves the frame
cannot be drawn. Outputs: opt-trajectories.png (paths and loss by step) and opt-trajectories.gif.
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
STEPS = 100
XLIM, YLIM = (-2.0, 2.0), (-2.0, 2.0)
GRID = 10 ** np.arange(-5, 0.51, 0.125)

STYLE = {"SGD": (fk.P["ink"], "o"), "Momentum": (fk.P["bow"], "s"), "Nesterov": (fk.P["monika-eye"], "^"),
         "Adagrad": (fk.P["skirt"], "v"), "RMSProp": (fk.P["sayori-eye"], "D"), "Adam": (fk.P["yuri"], "P")}


def inside(p):
    return (np.all(np.isfinite(p)) and (p[:, 0] > XLIM[0]).all() and (p[:, 0] < XLIM[1]).all()
            and (p[:, 1] > YLIM[0]).all() and (p[:, 1] < YLIM[1]).all())


def tune(cls):
    best = None
    for lr in GRID:
        with np.errstate(all="ignore"):
            p = oc.run(cls(lr), START, S.grad, STEPS)
        f = S.f(p[-1])
        if inside(p) and (best is None or f < best[1]):
            best = (lr, f, p)
    return best


RUNS = {name: tune(cls) for name, cls in oc.OPTIMIZERS.items()}
for name, (lr, f, p) in RUNS.items():
    print(f"{name:9s} lr {lr:.4g}  f after {STEPS} steps {f:.3g}  distance to minimum {np.linalg.norm(p[-1] - S.minimum):.3g}")

gx, gy = np.meshgrid(np.linspace(*XLIM, 300), np.linspace(*YLIM, 300))
Z = S.f(np.stack([gx, gy], axis=-1))


def surface(ax):
    fk.loss_contourf(ax, gx, gy, Z, n=12)
    ax.plot(*S.minimum, marker="x", color=fk.TEXT, ms=9, mew=2, zorder=6)
    ax.scatter(*START, s=50, color=fk.P["paper"], edgecolor=fk.TEXT, zorder=6)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")


def paths(ax, k, marker_every=10):
    for name, (lr, f, p) in RUNS.items():
        c, m = STYLE[name]
        q = p[: k + 1]
        ax.plot(q[:, 0], q[:, 1], color=c, lw=1.6, zorder=3, label=f"{name} ($\\eta=10^{{{fk.num(np.log10(lr), '.4g', math=True)}}}$)")
        idx = np.arange(0, len(q), marker_every)
        ax.scatter(q[idx, 0], q[idx, 1], s=22, marker=m, color=c, edgecolor="white", linewidths=0.5, zorder=4)
        ax.scatter(*q[-1], s=34, marker=m, color=c, edgecolor="white", linewidths=0.8, zorder=5)


if __name__ == "__main__":
    fig, axes = fk.subplots(1, 2, size=(11.6, 4.6), gridspec_kw={"width_ratios": [1, 1.15]})
    surface(axes[0])
    paths(axes[0], STEPS)
    axes[0].set_title(f"Пути за {STEPS} шагов")
    axes[0].set_xticks([-2, -1, 0, 1, 2])
    axes[0].set_yticks([-2, -1, 0, 1, 2])
    ax = axes[1]
    for name, (lr, f, p) in RUNS.items():
        c, m = STYLE[name]
        ax.plot(np.arange(STEPS + 1), S.f(p), color=c, lw=2, label=name)
    ax.set_yscale("log")
    ax.set_xlabel("номер шага")
    ax.set_ylabel("потеря $f$")
    ax.set_title("Потеря по шагам")
    ax.grid(True, axis="y")
    ax.legend(loc="lower left", ncol=2)
    fig.tight_layout()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=8)
    fk.save(fig, OUT / "opt-trajectories.png")

    # Frame 0 has no lines yet and the GIF palette is built from the first frame: start at step 2 so every colour is in it
    FRAMES = list(range(2, STEPS + 1, 2))

    def draw(ax, i):
        k = FRAMES[i]
        surface(ax)
        paths(ax, k, marker_every=1000)
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.set_yticks([-2, -1, 0, 1, 2])
        ax.set_title(f"шаг {k}")
        ax.legend(loc="lower right", fontsize=7)

    fk.gif(draw, len(FRAMES), OUT / "opt-trajectories.gif", size=(5.2, 4.9), fps=10, dpi=100, hold_last=10)
