"""Gradient of the cross-entropy with respect to the logits, (q - p) / T, against the temperature, for a hard label.

Two cases on the same ten logits: the label is the class with the largest logit (Audi) or another one (Lada).
The formula is checked against central differences of C(z) = -sum p ln softmax(z / T).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import softmax_common as S  # noqa: E402
from softmax_common import fk  # noqa: E402


def loss(z, p, T):
    return float(-(p * np.log(S.softmax(z, T))).sum())


def grad(z, p, T):
    return (S.softmax(z, T) - p) / T


rng = np.random.default_rng(fk.SEED)
worst = 0.0
for T in (0.5, 1.0, 4.0):
    p = np.eye(10)[3]
    g = grad(S.Z, p, T)
    for i in range(10):
        e = np.zeros(10)
        e[i] = 1e-6
        num = (loss(S.Z + e, p, T) - loss(S.Z - e, p, T)) / 2e-6
        worst = max(worst, abs(num - g[i]))
print("max |numeric - (q-p)/T| over 3 temperatures x 10 logits:", worst)

T = np.logspace(-0.7, 2.0, 300)
Q = S.softmax(S.Z, T)
fig, axes = fk.subplots(1, 2, size=(12.2, 4.2))
ax = axes[0]
for label, y, c, ls in [("метка Audi (совпадает с argmax)", S.AUDI, S.CLASS_COLOR["Audi"], "-"),
                        ("метка Lada (не совпадает)", 0, S.CLASS_COLOR["Lada"], "-")]:
    p = np.eye(10)[y]
    norm = np.linalg.norm((Q - p) / T[:, None], axis=1)
    ax.plot(T, norm, color=c, lw=2, ls=ls, label=label)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("температура $T$")
ax.set_ylabel(r"$\|\partial C/\partial z\|$")
ax.set_title("Норма градиента по логитам", fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, axis="y")

ax = axes[1]
p = np.eye(10)[0]
cmap = plt.get_cmap("ddlc_seq")  # darker means a lower temperature; no class colour is reused here
for t, c in zip([0.5, 1, 5], [cmap(0.95), cmap(0.62), cmap(0.3)]):
    ax.bar(np.arange(10) + {0.5: -0.27, 1: 0, 5: 0.27}[t], grad(S.Z, p, t), 0.27, color=c, label=f"$T={fk.num(t, None, math=True)}$")
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.set_xticks(np.arange(10), S.NAMES, rotation=70, ha="right", fontsize=7)
ax.set_ylabel(r"$\partial C/\partial z_i=(q_i-p_i)/T$")
ax.set_title("Метка Lada: компоненты градиента", fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, axis="y")
fig.tight_layout()
fk.save(fig, fk.attachments(8) / "softmax-gradient-t.png")

na = np.linalg.norm((Q - np.eye(10)[S.AUDI]) / T[:, None], axis=1)
print("Audi label: maximum of the norm", round(float(na.max()), 3), "at T =", round(float(T[na.argmax()]), 2))
for y, name in [(S.AUDI, "Audi"), (0, "Lada")]:
    p = np.eye(10)[y]
    print(name, {t: round(float(np.linalg.norm(grad(S.Z, p, t))), 4) for t in (0.5, 1, 2, 5, 20, 100)})
