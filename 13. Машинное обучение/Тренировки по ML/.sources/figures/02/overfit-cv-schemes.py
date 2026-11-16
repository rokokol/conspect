"""Splitting schemes drawn from the sklearn splitters themselves: holdout, k-fold (k=5) and time series split."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Rectangle
from sklearn.model_selection import KFold, TimeSeriesSplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

N = 30
UNUSED = fk.tint(fk.GRIDC, 0.55)


def bar(ax, row, idx, kind):
    """Draw the samples idx in row `row` as one run of cells of the given kind."""
    for i in idx:
        if kind == "train":
            patch = dict(fc=fk.TRAIN_C, ec="white", lw=0.6)
        elif kind == "val":
            patch = dict(fc="white", ec=fk.TEXT_2, lw=1.4)
        else:
            patch = dict(fc=UNUSED, ec="white", lw=0.6)
        ax.add_patch(Rectangle((i, -row - 0.38), 1, 0.76, **patch))


def panel(ax, splits, title, labels):
    for r, (tr, va) in enumerate(splits):
        used = set(tr) | set(va)
        bar(ax, r, [i for i in range(N) if i not in used], "none")
        bar(ax, r, tr, "train")
        bar(ax, r, va, "val")
    ax.set_xlim(-0.5, N + 0.5)
    ax.set_ylim(-len(splits) + 0.4, 0.7)
    ax.set_yticks([-r for r in range(len(splits))])
    ax.set_yticklabels(labels)
    ax.set_xticks([])
    ax.set_title(title, fontsize=10, loc="left")
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0)
    ax.grid(False)


holdout = [(np.arange(0, 21), np.arange(21, N))]
kfold = list(KFold(5).split(np.arange(N)))
tss = list(TimeSeriesSplit(n_splits=5).split(np.arange(N)))

fig, axes = fk.plt.subplots(3, 1, figsize=(7.4, 6.2), gridspec_kw=dict(height_ratios=[1, 5, 5]))
panel(axes[0], holdout, "отложенная выборка", ["разбиение"])
panel(axes[1], kfold, "k-fold, $k=5$: каждый объект побывает в валидации один раз", [f"фолд {i + 1}" for i in range(5)])
panel(axes[2], tss, "time series split: обучаемся на прошлом, проверяемся на будущем",
      [f"шаг {i + 1}" for i in range(5)])
axes[2].set_xlabel("время (номер объекта)  →")
axes[2].xaxis.set_label_coords(0.5, -0.12)
axes[2].set_xticks([0, N])
axes[2].set_xticklabels(["раньше", "позже"])

handles = [Rectangle((0, 0), 1, 1, fc=fk.TRAIN_C, ec="white"),
           Rectangle((0, 0), 1, 1, fc="white", ec=fk.TEXT_2, lw=1.4),
           Rectangle((0, 0), 1, 1, fc=UNUSED, ec="white")]
fig.legend(handles, ["обучение", "валидация", "не используется на этом шаге"], loc="lower center", ncol=3,
           frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.03, 1, 1))
fk.save(fig, fk.attachments(2) / "overfit-cv-schemes.png")
print("time series train sizes", [len(t) for t, _ in tss], "validation size", len(tss[0][1]))
