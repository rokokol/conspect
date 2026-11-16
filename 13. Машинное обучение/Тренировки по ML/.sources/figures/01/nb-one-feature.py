"""One feature, two Gaussian classes: the argmax of p(x | C) P(C) and how the prior moves the border."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from scipy.stats import norm  # noqa: E402

import figkit as fk  # noqa: E402

MU, SIGMA = (0.0, 2.5), 1.0
x = np.linspace(-3.5, 6, 800)

fig, axes = fk.subplots(1, 2, size=(10.4, 3.6), sharey=True)
for ax, prior in zip(axes, [(0.5, 0.5), (0.8, 0.2)]):
    f0 = prior[0] * norm.pdf(x, MU[0], SIGMA)
    f1 = prior[1] * norm.pdf(x, MU[1], SIGMA)
    win1 = f1 > f0
    ax.fill_between(x, 0, np.maximum(f0, f1), where=~win1, color=fk.tint(fk.BLUE, 0.6), lw=0)
    ax.fill_between(x, 0, np.maximum(f0, f1), where=win1, color=fk.tint(fk.RED, 0.6), lw=0)
    ax.plot(x, f0, color=fk.BLUE, label=r"$p(x\mid C_0)\,P(C_0)$")
    ax.plot(x, f1, color=fk.RED, label=r"$p(x\mid C_1)\,P(C_1)$")
    # Equal variances: f0 = f1 gives a closed form for the border.
    b = (MU[0] + MU[1]) / 2 + SIGMA**2 * np.log(prior[0] / prior[1]) / (MU[1] - MU[0])
    ax.axvline(b, color=fk.TEXT, lw=1.2, ls="--")
    ax.text(b + 0.1, 0.36, f"граница x = {fk.num(b, 2)}", fontsize=8, color=fk.TEXT)
    ax.set_title(f"Априорные P(C₀) = {fk.num(prior[0], None)}, P(C₁) = {fk.num(prior[1], None)}")
    ax.set_xlabel("x")
    ax.set_ylim(0, 0.46)
    ax.legend(loc="upper left")
axes[0].set_ylabel("числитель Байеса")
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "nb-one-feature-prior.png")
