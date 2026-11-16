"""Maximum likelihood on a one-feature logistic model: the likelihood, its logarithm and the logistic loss peak and dip at the same w."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

# Eight objects on a line through the origin; classes overlap, so the optimum is finite.
x = np.array([-2.0, -1.4, -0.8, -0.2, 0.3, 0.9, 1.5, 2.2])
y = np.array([-1, -1, -1, 1, -1, 1, 1, 1])


def sigma(z):
    return 1 / (1 + np.exp(-z))


def loss(w):
    """Logistic loss summed over the sample: -ln L(w)."""
    return np.sum(np.log1p(np.exp(-y * w * x)))


ws = np.linspace(-1, 6, 700)
J = np.array([loss(w) for w in ws])
L = np.exp(-J)
w_hat = ws[np.argmin(J)]
assert ws[np.argmax(L)] == w_hat
print("w_hat", round(w_hat, 3), "L", L.max(), "J", J.min())

# Model curves avoid the class colours of the points drawn on the same panel.
picks = [(0.3, fk.TEXT_2), (w_hat, fk.TEXT), (5.0, fk.MODEL2_C)]

fig, axes = fk.subplots(1, 3, size=(11.4, 3.6))
ax = axes[0]
xs = np.linspace(-3, 3, 300)
for w, c in picks:
    ax.plot(xs, sigma(w * xs), color=c, lw=2, label=f"$w={fk.num(w, 2, math=True)}$")
for k, col in ((1, fk.CLASS_COLORS[1]), (-1, fk.CLASS_COLORS[0])):
    m = y == k
    ax.scatter(x[m], (k == 1) * np.ones(m.sum()), color=col, s=36, edgecolor="white", zorder=4)
ax.set_xlabel("признак $x$")
ax.set_ylabel("$P(y=+1\\mid x)$")
ax.set_title("модель при разных $w$")
ax.legend(loc="center left")
ax.grid(True)

ax = axes[1]
ax.plot(ws, L, color=fk.TEXT, lw=2)
for w, c in picks:
    ax.plot([w], [np.exp(-loss(w))], "o", color=c, zorder=4, ms=7)
ax.set_xlabel("вес $w$")
ax.set_ylabel("правдоподобие $\\mathcal{L}(w)$")
ax.set_title("правдоподобие: максимум")
ax.grid(True)

ax = axes[2]
ax.plot(ws, J, color=fk.TEXT, lw=2)
for w, c in picks:
    ax.plot([w], [loss(w)], "o", color=c, zorder=4, ms=7)
ax.axvline(w_hat, color=fk.TEXT_2, lw=1, ls="--")
ax.set_xlabel("вес $w$")
ax.set_ylabel("$-\\ln\\mathcal{L}(w)=\\sum\\ln(1+e^{-M})$")
ax.set_title("логистическая потеря: минимум")
ax.grid(True)

fig.tight_layout()
fk.save(fig, fk.attachments(3) / "logreg-likelihood.png")
