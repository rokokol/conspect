"""Entropy of softmax(z/T) against T, and the shares of four classes against T, on the same ten logits.

Checked on the grid: H grows with T, and dH/dT equals Var_q(z) / T^3 (central differences against the formula).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import softmax_common as S  # noqa: E402
from softmax_common import fk  # noqa: E402

T = np.logspace(-1.5, 2.3, 400)
Q = np.array([S.softmax(S.Z, t) for t in T])
H = S.entropy(Q)
assert np.all(np.diff(H) > 0), "entropy must grow with T"

# dH/dT = Var_q(z) / T^3
h = 1e-5
num = (S.entropy(S.softmax(S.Z, T * (1 + h))) - S.entropy(S.softmax(S.Z, T * (1 - h)))) / (2 * h * T)
var = (Q * S.Z**2).sum(1) - (Q * S.Z).sum(1) ** 2
rel = np.abs(num - var / T**3) / np.maximum(np.abs(var / T**3), 1e-12)
mask = (var / T**3) > 1e-9
print("max relative error of dH/dT = Var/T^3 on", int(mask.sum()), "points:", float(rel[mask].max()))

fig, axes = fk.subplots(1, 2, size=(12.2, 4.2))
ax = axes[0]
ax.plot(T, H, color=fk.ACCENT, lw=2)
ax.axhline(np.log(10), color=fk.TEXT_2, ls="--", lw=1)
ax.text(T[0] * 1.2, np.log(10) - 0.12, r"$\ln N$ (равномерное)", fontsize=8, color=fk.TEXT_2, va="top")
ax.axvline(1, color=fk.TEXT_2, lw=0.8, ls=":")
ax.text(1.08, 0.12, "$T=1$", fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("температура $T$")
ax.set_ylabel("энтропия $H(q)$, нат")
ax.set_title("Энтропия растёт с температурой", fontsize=10)
ax.grid(True, axis="y")

ax = axes[1]
for i in [S.AUDI, 1, 0, 4]:
    ax.plot(T, Q[:, i], color=S.CLASS_COLOR[S.NAMES[i]], lw=2, label=S.NAMES[i])
peaks = {}
for i in range(len(S.NAMES)):
    j = int(Q[:, i].argmax())
    peaks[S.NAMES[i]] = (round(float(T[j]), 2), round(float(Q[j, i]), 4), 0 < j < len(T) - 1)
print("peak of q_i(T): (T, q, interior)", peaks)
print("mean logit", round(float(S.Z.mean()), 3), "excess over the mean:", {n: round(float(z - S.Z.mean()), 2) for n, z in zip(S.NAMES, S.Z)})
ax.plot(T, Q[:, 5], color=fk.TEXT_2, lw=1.5, ls="--", label="гриб (опята)")
ax.axhline(0.1, color=fk.TEXT_2, ls=":", lw=1)
ax.text(T[-1], 0.1 + 0.015, "$1/N$", fontsize=8, color=fk.TEXT_2, ha="right")
ax.set_xscale("log")
ax.set_xlabel("температура $T$")
ax.set_ylabel("вероятность $q_i$")
ax.set_title("Пределы: one-hot слева, $1/N$ справа", fontsize=10)
ax.legend(fontsize=8, loc="center left")
ax.grid(True, axis="y")
fig.tight_layout()
fk.save(fig, fk.attachments(8) / "softmax-entropy-curve.png")
