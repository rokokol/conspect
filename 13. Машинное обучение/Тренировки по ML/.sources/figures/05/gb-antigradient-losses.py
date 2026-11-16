"""Loss and antigradient -dL/dq for MSE, MAE, Huber (regression, against the residual y - q) and for the logistic and exponential losses (classification, against the margin M = y q).

The formulas of the note are checked against a numerical derivative before they are drawn.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

DELTA = 1.0

# loss as a function of (y, q); the antigradient is -dL/dq
LOSSES = {
    "MSE": (lambda y, q: 0.5 * (y - q) ** 2, lambda y, q: y - q),
    "MAE": (lambda y, q: np.abs(y - q), lambda y, q: np.sign(y - q)),
    "Huber": (lambda y, q: np.where(np.abs(y - q) <= DELTA, 0.5 * (y - q) ** 2, DELTA * (np.abs(y - q) - 0.5 * DELTA)),
              lambda y, q: np.clip(y - q, -DELTA, DELTA)),
    "logistic": (lambda y, q: np.log1p(np.exp(-y * q)), lambda y, q: y / (1 + np.exp(y * q))),
    "exponential": (lambda y, q: np.exp(-y * q), lambda y, q: y * np.exp(-y * q)),
}

q = np.linspace(-3, 3, 241)
for name, (loss, anti) in LOSSES.items():
    for y0 in (-1.0, 1.0):
        h = 1e-6
        numeric = -(loss(y0, q + h) - loss(y0, q - h)) / (2 * h)
        kink = np.abs(q - y0) < 1e-3 if name in ("MAE", "Huber") else np.zeros_like(q, dtype=bool)
        assert np.allclose(numeric[~kink], anti(y0, q)[~kink], atol=1e-5), (name, y0)
print("antigradients match the numerical derivative")

e = np.linspace(-3, 3, 301)
M = np.linspace(-4, 4, 321)
fig, axes = fk.subplots(2, 2, size=(10.4, 7.2))
colors = {"MSE": fk.CATEGORICAL[0], "MAE": fk.CATEGORICAL[1], "Huber": fk.CATEGORICAL[2],
          "logistic": fk.CATEGORICAL[0], "exponential": fk.CATEGORICAL[1]}
for name in ("MSE", "MAE", "Huber"):
    loss, anti = LOSSES[name]
    axes[0, 0].plot(e, loss(e, 0.0), color=colors[name], label=name)
    axes[0, 1].plot(e, anti(e, 0.0), color=colors[name], label=name, ls="--" if name == "MAE" else "-", lw=2.2 if name == "MAE" else 1.6)
for name in ("logistic", "exponential"):
    loss, anti = LOSSES[name]
    axes[1, 0].plot(M, loss(1.0, M), color=colors[name], label=name)
    axes[1, 1].plot(M, anti(1.0, M), color=colors[name], label=name)
axes[0, 0].set_title("потеря от остатка y − q")
axes[0, 1].set_title("антиградиент от остатка y − q")
axes[1, 0].set_title("потеря от отступа M = yq")
axes[1, 1].set_title("антиградиент (y = 1) от отступа M = yq")
axes[0, 0].set_ylim(0, 5)
axes[1, 0].set_ylim(0, 5)
axes[1, 1].set_ylim(-0.3, 6)
for ax, xl in zip(axes.ravel(), ["y − q", "y − q", "M", "M"]):
    ax.set_xlabel(xl)
    ax.grid(True)
    ax.legend()
for ax in axes[:, 1]:
    ax.axhline(0, color=fk.GRIDC, lw=0.8)
fig.tight_layout()
fk.save(fig, fk.attachments(5) / "gb-antigradient-losses.png")
