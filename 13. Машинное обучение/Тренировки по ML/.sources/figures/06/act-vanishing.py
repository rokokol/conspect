"""Norm of the gradient with respect to the activations of every layer of a deep network, at initialisation.

Twelve hidden layers of 32 units on the moons train part, binary cross-entropy, 30 random initialisations;
the geometric mean over initialisations is drawn, relative to the last hidden layer. Layer 12 is next to
the output, layer 1 is the farthest from it.
Left: Glorot weights for sigmoid and tanh, He weights for the rest; the dashed line is 4^-k, the product of
the bound sigma' <= 1/4 over k sigmoids. Right: ReLU with the weights of layers 2-12 multiplied by 1, 2 and 3.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402

OUT = fk.attachments(6)
L, WIDTH, SEEDS = 12, 32, 30
X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
ytr = ytr.astype(float)


def layer_norms(act, gain=1.0, depth=L):
    """Geometric mean over initialisations of |dL/dA_l|, divided by the value at the last hidden layer."""
    rows = []
    for s in range(SEEDS):
        params = ac.init_params([2] + [WIDTH] * depth + [1], act, np.random.default_rng(s))
        for layer in params[1:-1]:
            layer[0] *= gain
        dA = ac.loss_and_grads(params, Xtr, ytr, act)[2]
        rows.append([np.linalg.norm(a) for a in dA])
    g = np.exp(np.mean(np.log(rows), axis=0))
    return g / g[-1]


layers = np.arange(1, L + 1)
fig, axes = fk.subplots(1, 2, size=(10.4, 3.8))
ax = axes[0]
curves = [("sigmoid", fk.MODEL_C), ("tanh", fk.MODEL2_C), ("relu", fk.TEXT), ("gelu", fk.P["bow"])]
for act, c in curves:
    r = layer_norms(act)
    ax.plot(layers, r, color=c, marker="o", ms=4, lw=2, label=ac.LABEL[act])
    print(act, "layer 1 / layer 12:", f"{r[0]:.2e}")
ax.plot(layers, 4.0 ** -(L - layers), color=fk.TEXT_2, ls="--", lw=1.4, label="$4^{-k}$")
ax.set_yscale("log")
ax.set_xlabel("слой (12 — у выхода)")
ax.set_ylabel("норма (у выхода 1)")
ax.set_title("Градиент по слоям")
ax.grid(True, axis="y")
ax.legend(loc="lower right")

ax = axes[1]
# Colours here mean the weight scale, not an activation: x1 is the ReLU curve of the left panel, so it keeps its colour
for gain, c in [(1, fk.TEXT), (2, fk.P["skirt"]), (3, fk.P["yuri"])]:
    r = layer_norms("relu", gain)
    ax.plot(layers, r, color=c, marker="o", ms=4, lw=2, label=f"веса ×{gain}")
    print("relu gain", gain, "layer 1 / layer 12:", f"{r[0]:.2e}")
ax.set_yscale("log")
ax.set_xlabel("слой (12 — у выхода)")
ax.set_title("ReLU: масштаб весов")
ax.grid(True, axis="y")
ax.legend(loc="upper right")
fig.tight_layout()
fk.save(fig, OUT / "act-vanishing.png")

# Numbers quoted in the note: the sigmoid factor per layer and the same experiment at 30 layers
r = layer_norms("sigmoid")
print("sigmoid: geometric mean factor per layer", f"{(1 / r[0]) ** (1 / (L - 1)):.2f}", "(4^k reference: 4)")
for act in ("relu", "tanh", "gelu", "silu"):
    r = layer_norms(act, depth=30)
    print(act, "30 layers: layer 1 / layer 30:", f"{r[0]:.2e}", "per layer", f"{r[0] ** (1 / 29):.2f}")
