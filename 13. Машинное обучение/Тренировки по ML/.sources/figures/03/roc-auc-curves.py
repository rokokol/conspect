"""ROC curves of different AUC from two normal score distributions, and two crossing curves with the same AUC."""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm
from sklearn.metrics import roc_auc_score, roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
n = 20000


def sample(mu, sigma):
    """Scores of 20000 negatives from N(0, 1) and 20000 positives from N(mu, sigma)."""
    s = np.r_[rng.normal(0, 1, n), rng.normal(mu, sigma, n)]
    return s, np.r_[np.zeros(n), np.ones(n)]


fig, axes = fk.subplots(1, 3, size=(13.6, 4.3))

# (a) the separation of the two score distributions sets the AUC.
ax = axes[0]
samples = {}
for (mu, c) in ((0.0, fk.TEXT_2), (0.7, fk.CATEGORICAL[2]), (1.5, fk.CATEGORICAL[0]), (3.5, fk.CATEGORICAL[1])):
    s, t = samples[mu] = sample(mu, 1.0)
    f, tp, _ = roc_curve(t, s)
    a = roc_auc_score(t, s)
    ax.plot(f, tp, color=c, lw=2, label=rf"сдвиг $\mu={fk.num(mu, None, math=True)}$, AUC {fk.num(a, 2)}", zorder=3)
    print("shift", mu, "AUC", round(a, 3), "formula", round(float(norm.cdf(mu / np.sqrt(2))), 3))
ax.plot([0, 1], [0, 1], color=fk.TEXT, ls="--", lw=1, zorder=4)
ax.set_title("чем дальше сдвиг, тем больше AUC")

# (b) two models with equal AUC whose curves cross. Binormal: AUC = Phi(mu / sqrt(1 + sigma^2)).
ax = axes[1]
target = float(norm.cdf(1.5 / np.sqrt(2)))
models = [(1.0, fk.CATEGORICAL[0], "A: разброс положительных 1"),
          (2.0, fk.CATEGORICAL[1], "B: разброс положительных 2")]
for sigma, c, name in models:
    mu = norm.ppf(target) * np.sqrt(1 + sigma**2)
    thr = np.linspace(-8, 14, 2000)
    fpr, tpr = norm.sf(thr), norm.sf((thr - mu) / sigma)
    auc = float(-np.trapezoid(tpr, fpr))
    ax.plot(fpr, tpr, color=c, lw=2, label=f"{name}, AUC {fk.num(auc, 3)}")
    print("binormal", sigma, "mu", round(float(mu), 3), "AUC", round(auc, 4))
ax.plot([0, 1], [0, 1], color=fk.TEXT_2, ls="--", lw=1)
ax.set_title("равные AUC, кривые пересекаются")

# (c) the hatched area under one curve.
ax = axes[2]
s, t = samples[1.5]
f, tp, _ = roc_curve(t, s)
ax.fill_between(f, tp, color=fk.tint(fk.CATEGORICAL[0], 0.6))
ax.plot(f, tp, color=fk.CATEGORICAL[0], lw=2)
ax.plot([0, 1], [0, 1], color=fk.TEXT_2, ls="--", lw=1)
ax.text(0.95, 0.12, f"AUC = {fk.num(roc_auc_score(t, s), 2)}", ha="right", fontsize=11, color=fk.TEXT,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
ax.set_title("AUC - площадь под кривой")

for ax in axes:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.grid(True)
for ax in axes[:2]:
    ax.legend(loc="lower right", fontsize=7)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "roc-auc-curves.png")
