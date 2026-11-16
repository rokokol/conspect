"""20 polynomials of degree 1, 3 and 7, each fitted on its own fresh sample of the noisy sine: bundle, mean, truth."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bv_common as bv  # noqa: E402
import figkit as fk  # noqa: E402

N, SHOWN, M = 30, 20, 500
DEGREES = (1, 3, 7)

fig, axes = fk.subplots(1, 3, size=(13.2, 3.9), sharey=True)

for ax, d in zip(axes, DEGREES):
    pred = bv.predictions(bv.poly_fit(d), N, M)
    bias2, var = bv.decompose(pred)
    ax.plot(bv.GRID, bv.F_GRID, color=fk.TEXT_2, ls="--", lw=1.2, label="истина sin 2πx", zorder=4)
    for i in range(SHOWN):
        ax.plot(bv.GRID, pred[i], color=fk.MODEL_C, lw=0.9, alpha=0.4,
                label="модель на своей выборке" if i == 0 else None)
    ax.plot(bv.GRID, pred.mean(axis=0), color=fk.MODEL2_C, lw=2.4, label=f"среднее по {M} выборкам", zorder=5)
    ax.set_ylim(-2, 2)
    ax.set_xlabel("x")
    ax.set_title(f"степень {d}")
    # The estimate of bias^2 can dip below zero by simulation noise; it is shown as zero then.
    ax.text(0.02, 0.04, f"bias² {fk.num(max(bias2, 0), 3)}\nvariance {fk.num(var, 3)}", transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8, color=fk.TEXT, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    print(d, round(bias2, 4), round(var, 4))
axes[0].set_ylabel("y")
axes[0].legend(loc="upper right", fontsize=7)

fk.save(fig, fk.attachments(5) / "bv-poly-bundle.png")
