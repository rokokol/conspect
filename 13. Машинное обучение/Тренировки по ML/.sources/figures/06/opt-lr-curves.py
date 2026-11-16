"""Loss by epoch of mini-batch SGD at four step sizes: a network of 16 ReLU units on the moons train part.

The step size eta* is chosen on a log grid by 5-fold cross-validation on the train part (lowest mean
validation loss after 100 epochs). The other three are eta*/100, 10 eta* and 300 eta*, picked to show the
too small, too large and far too large cases. The curves are means over the 5 folds: train loss on the
four fifths, validation loss on the fifth. The test part is not used.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402
import opt_nn as on  # noqa: E402

OUT = fk.attachments(6)
X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
GRID = 10 ** np.arange(-4, 1.01, 0.25)

best, scores = on.choose_lr(oc.SGD, Xtr, ytr, GRID)
print("eta* by validation:", f"{best:.3g}", "validation loss at the grid:", np.round(scores, 3))

CASES = [(best / 100, "слишком мал", fk.P["skirt"]), (best, "выбран по валидации", fk.P["monika-eye"]),
         (best * 10, "слишком велик", fk.P["bow"]), (best * 300, "взрыв", fk.P["ink"])]
fig, axes = fk.subplots(1, 2, size=(10.4, 3.8))
blown = []
for lr, name, c in CASES:
    _, curves = on.cv_val_loss(lambda lr=lr: oc.SGD(lr), Xtr, ytr)
    tr = np.mean([t for t, _ in curves], axis=0)
    va = np.mean([v for _, v in curves], axis=0)
    label = f"$\\eta={fk.num(lr, '.3g', math=True)}$: {name}"
    for ax, curve in zip(axes, (tr, va)):
        ep = np.arange(len(curve))
        ok = np.isfinite(curve)
        ax.plot(ep[ok], curve[ok], color=c, lw=2, label=label)
        if not ok.all():
            blown.append((ax, ep[ok][-1], curve[ok][-1], c))
    print(f"eta {lr:.3g} {name}: train {tr[-1]:.3f} validation {va[-1]:.3f} (inf = diverged)")
for ax, t in zip(axes, ("Потеря на обучении", "Потеря на валидации")):
    ax.set_yscale("log")
    ax.set_xlabel("эпоха")
    ax.set_title(t)
    ax.grid(True, axis="y")
axes[0].set_ylabel("логлосс")
for ax, last, value, c in blown:
    # the mean over folds is cut after the first epoch: the arrow goes up to the top of the axis, not to a real value
    top = ax.get_ylim()[1]
    ax.annotate("", xy=(last + 1, top), xytext=(last, value), arrowprops=dict(arrowstyle="-|>", color=c, lw=2, ls="--"),
                annotation_clip=False)
    ax.annotate("эпоха 1: потеря > 1000", (last + 1, top), xytext=(6, -10), textcoords="offset points", fontsize=7,
                color=fk.TEXT)
fig.tight_layout()
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.17), frameon=False, fontsize=8)
fk.save(fig, OUT / "opt-lr-curves.png")
