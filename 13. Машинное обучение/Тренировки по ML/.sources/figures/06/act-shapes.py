"""Activation functions with their derivatives: sigmoid and tanh with the saturation zones, the ReLU family
with the dead zone, and GELU and SiLU against ReLU and ELU.

A zone counts as saturated where |f'| < 0.05, a threshold chosen here for the picture.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402

OUT = fk.attachments(6)
SAT = 0.05
A = np.linspace(-6, 6, 2401)
F_C, D_C = fk.MODEL_C, fk.MODEL2_C


def panel(ax, name, lim, ylim, shade_where=None, note=None):
    f, df = ac.ACT[name]
    a = np.linspace(-lim, lim, 1201)
    if shade_where is not None:
        mask = shade_where(a)
        ax.fill_between(a, ylim[0], ylim[1], where=mask, color=fk.P["ash"], alpha=0.35, lw=0, step=None)
    ax.axhline(0, color=fk.GRIDC, lw=0.8)
    ax.axvline(0, color=fk.GRIDC, lw=0.8)
    ax.plot(a, f(a), color=F_C, lw=2, label="$f(a)$")
    ax.plot(a, df(a), color=D_C, lw=2, label="$f'(a)$")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(*ylim)
    ax.set_title(ac.LABEL[name])
    ax.set_xlabel("$a$")
    ax.grid(True, axis="y")
    if note:
        ax.text(0.03, 0.97, note, transform=ax.transAxes, va="top", fontsize=8, color=fk.TEXT,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


# 1. sigmoid and tanh
fig, axes = fk.subplots(1, 2, size=(8.6, 3.5))
sat = lambda name: (lambda a: np.abs(ac.ACT[name][1](a)) < SAT)  # noqa: E731
panel(axes[0], "sigmoid", 6, (-0.15, 1.15), sat("sigmoid"), f"$\\max f'={fk.num(ac.ACT['sigmoid'][1](np.array(0.0)), 2, math=True)}$")
panel(axes[1], "tanh", 4, (-1.15, 1.15), sat("tanh"), f"$\\max f'={fk.num(ac.ACT['tanh'][1](np.array(0.0)), 0, math=True)}$")
axes[0].legend(loc="center right")
fig.tight_layout()
fk.save(fig, OUT / "act-sigmoid-tanh.png")

# 2. ReLU family
fig, axes = fk.subplots(1, 3, size=(12.0, 3.5))
panel(axes[0], "relu", 3, (-0.6, 3.1), lambda a: a < 0, "серое: $f'=0$, градиент\nне проходит")
panel(axes[1], "leaky_relu", 3, (-0.6, 3.1), None, f"наклон слева ${fk.num(ac.LEAK, None, math=True)}$")
panel(axes[2], "elu", 3, (-1.3, 3.1), None, "$\\alpha=1$")
axes[0].legend(loc="center right")
fig.tight_layout()
fk.save(fig, OUT / "act-relu-family.png")

# 3. GELU and SiLU against ReLU and ELU: functions, zoom near zero, derivatives
CURVES = [("relu", fk.TEXT, "-"), ("elu", fk.P["bow"], "-"), ("gelu", fk.MODEL_C, "-"), ("silu", fk.P["monika-eye"], "--")]
fig, axes = fk.subplots(1, 3, size=(12.6, 3.6))
for ax, (lim, ylim, kind, title) in zip(axes, [((-4, 4), (-1.2, 4.2), 0, "$f(a)$"),
                                                ((-2.5, 1.5), (-1.1, 1.6), 0, "$f(a)$ около нуля"),
                                                ((-4, 4), (-0.3, 1.25), 1, "$f'(a)$")]):
    a = np.linspace(*lim, 1201)
    ax.axhline(0, color=fk.GRIDC, lw=0.8)
    ax.axvline(0, color=fk.GRIDC, lw=0.8)
    for name, c, ls in CURVES:
        ax.plot(a, ac.ACT[name][kind](a), color=c, lw=2, ls=ls, label=ac.LABEL[name])
    ax.set_xlim(*lim)
    ax.set_ylim(*ylim)
    ax.set_title(title)
    ax.set_xlabel("$a$")
    ax.grid(True, axis="y")
axes[0].legend(loc="upper left")
fig.tight_layout()
fk.save(fig, OUT / "act-gelu-silu.png")
