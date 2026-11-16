"""Why a centred input matters for ReLU: pre-activations a ~ N(mu, 1) with mu = 0 and mu = 3 against the ReLU curve.

The share of inputs on the linear side is the share of a > 0, printed from the 100000 drawn values.
On a mean-positive input the unit passes almost everything unchanged, so it acts as the identity.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402

OUT = fk.attachments(6)
rng = np.random.default_rng(fk.SEED)
z = rng.normal(size=100_000)
a = np.linspace(-4, 7, 600)
relu = ac.ACT["relu"][0]

fig, axes = fk.subplots(1, 2, size=(9.6, 3.4), sharey=True)
for ax, mu, c in zip(axes, (0.0, 3.0), (fk.P["monika-eye"], fk.P["bow"])):
    x = z + mu
    share = float(np.mean(x > 0))
    print(f"mu={mu}: share of a > 0 is {share:.4f}, mean of ReLU(a) - a over the sample {np.mean(relu(x) - x):.4f}")
    ax.hist(x, bins=60, range=(-4, 7), density=True, color=c, alpha=0.35, label="плотность $a$")
    ax.plot(a, relu(a) / 7, color=fk.TEXT, lw=1.8, label="ReLU, масштаб $1/7$")
    ax.axvline(0, color=fk.GRIDC, lw=0.8)
    ax.set_title(f"среднее входа ${fk.num(mu, None, math=True)}$")
    ax.set_xlabel("$a$")
    ax.text(0.97, 0.55, f"$a>0$ у {fk.num(share, '.1%')}", transform=ax.transAxes, ha="right", fontsize=9, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    ax.grid(True, axis="y")
axes[0].legend(loc="upper left", fontsize=8)
fig.tight_layout()
fk.save(fig, OUT / "act-centering.png")
