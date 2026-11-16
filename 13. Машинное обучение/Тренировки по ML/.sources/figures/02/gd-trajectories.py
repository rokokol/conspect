"""Gradient descent on the stretched quadratic x^2 + 10 y^2 at three step sizes: GIF of the paths and a loss-curve PNG."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(2)

# f(w) = w^T H w / 2 with H = diag(2, 20): eigenvalues 2 and 20, so GD is stable for eta < 2/20 = 0.1
HESS = np.array([2.0, 20.0])
START = np.array([-2.6, 1.6])
STEPS = 30
BOX = 3.0
CASES = [(0.01, "мало"), (0.09, "хорошо"), (0.105, "много")]


def loss(w):
    return 0.5 * np.sum(HESS * w * w, axis=-1)


def path(eta):
    w = START.copy()
    pts = [w.copy()]
    for _ in range(STEPS):
        w = w - eta * HESS * w
        pts.append(w.copy())
    return np.array(pts)


PATHS = {eta: path(eta) for eta, _ in CASES}

gx, gy = np.meshgrid(np.linspace(-BOX, BOX, 240), np.linspace(-BOX, BOX, 240))
Z = loss(np.stack([gx, gy], axis=-1))


def fmt(v):
    return fk.num(v, ".2g", math=True) if v < 1000 else fk.num(v, ".1e", math=True)


def panel(ax, eta, name, k):
    full = PATHS[eta]
    p = full[: k + 1]
    # A diverging path is drawn up to its first point outside the frame, not as stripes over the picture
    out = np.flatnonzero(np.abs(p).max(1) > BOX)
    shown = p if out.size == 0 else p[: out[0] + 1]
    fk.loss_contourf(ax, gx, gy, Z, n=12)
    ax.plot(shown[:, 0], shown[:, 1], color=fk.MODEL_C, lw=1.6, zorder=3)
    ax.scatter(shown[:, 0], shown[:, 1], s=14, color=fk.MODEL_C, edgecolor="white", linewidths=0.5, zorder=4)
    ax.scatter(*START, s=46, color=fk.MODEL2_C, edgecolor="white", zorder=5)
    ax.plot([0], [0], marker="x", color=fk.TEXT, ms=8, mew=2, zorder=5)
    ax.set_xlim(-BOX, BOX)
    ax.set_ylim(-BOX, BOX)
    ax.set_aspect("equal")
    ax.set_xticks([-2, 0, 2])
    ax.set_yticks([-2, 0, 2])
    ax.set_title(f"$\\eta={fk.num(eta, None, math=True)}$: шаг {name}")
    ax.text(0.03, 0.03, f"шаг {k}\n$Q={fmt(loss(p[-1]))}$", transform=ax.transAxes, fontsize=8,
            color=fk.TEXT, va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


def draw(ax, k):
    ax.set_axis_off()
    ax.set_position([0.0, 0.0, 1.0, 1.0])
    for j, (eta, name) in enumerate(CASES):
        sub = ax.inset_axes([j / 3 + 0.04, 0.09, 0.29, 0.8])
        panel(sub, eta, name, k)


if __name__ == "__main__":
    fk.gif(draw, STEPS + 1, OUT / "gd-trajectories.gif", size=(10.2, 3.9), fps=6, dpi=100, hold_last=8)

    fig, ax = fk.subplots(1, 1, size=(6.4, 3.6))
    colors = [fk.MODEL_C, fk.MODEL2_C, fk.TEXT]
    for (eta, name), c in zip(CASES, colors):
        ax.plot(np.arange(STEPS + 1), loss(PATHS[eta]), color=c, lw=2, label=f"$\\eta={fk.num(eta, None, math=True)}$: {name}")
    ax.set_yscale("log")
    ax.set_xlabel("номер шага")
    ax.set_ylabel("потеря $Q$")
    ax.set_title("Потеря по шагам")
    ax.grid(True, axis="y")
    ax.legend()
    fig.tight_layout()
    fk.save(fig, OUT / "gd-loss-curves.png")
