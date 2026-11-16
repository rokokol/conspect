"""The six optimizers on one network and one data set: 16 ReLU units, moons, mini-batches of 32, 100 epochs.

The step size of every optimizer is chosen on a log grid by 5-fold cross-validation on the train part (lowest
mean validation loss after 100 epochs). Momentum and Nesterov use rho = 0.9, RMSProp beta = 0.9, Adam its default
betas. The curves are means over the folds at the chosen step size; the test part only gives the accuracy of
the network refitted on the whole train part with the chosen step size. Initial weights and batch order are
the same for every optimizer.
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
STYLE = {"SGD": fk.P["ink"], "Momentum": fk.P["bow"], "Nesterov": fk.P["monika-eye"],
         "Adagrad": fk.P["skirt"], "RMSProp": fk.P["sayori-eye"], "Adam": fk.P["yuri"]}

fig, axes = fk.subplots(1, 2, size=(10.6, 3.9))
for name, cls in oc.OPTIMIZERS.items():
    lr, scores = on.choose_lr(cls, Xtr, ytr, GRID)
    val_end, curves = on.cv_val_loss(lambda lr=lr: cls(lr), Xtr, ytr)
    tr = np.mean([t for t, _ in curves], axis=0)
    va = np.mean([v for _, v in curves], axis=0)
    _, _, params = on.train(lambda lr=lr: cls(lr), Xtr, ytr)
    acc = on.predict_acc(params, Xte, yte)
    first = int(np.argmax(va <= 0.30)) if (va <= 0.30).any() else None
    print(f"{name:9s} lr {lr:.3g}  validation loss {val_end:.3f}  test accuracy {acc:.3f}  "
          f"epoch where validation loss <= 0.30: {first}")
    for ax, curve in zip(axes, (tr, va)):
        ax.plot(np.arange(len(curve)), curve, color=STYLE[name], lw=2, label=f"{name} ($\\eta={fk.num(lr, '.2g', math=True)}$)")
for ax, t in zip(axes, ("Потеря на обучении", "Потеря на валидации")):
    ax.set_yscale("log")
    ax.set_xlabel("эпоха")
    ax.set_title(t)
    ax.grid(True, axis="y")
axes[0].set_ylabel("логлосс")
fig.tight_layout()
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.17), frameon=False, fontsize=8)
fk.save(fig, OUT / "opt-nn-moons.png")
