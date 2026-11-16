"""Three classes along a line, the middle one linearly inseparable from the other two together: the middle-vs-rest classifier fails, and One vs Rest follows it when the middle class is small."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from sklearn.datasets import make_blobs
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

K = 3
D, STD = 1.5, 0.5
# Class 0 (the figkit lilac, rule) sits in the middle, 1 and 2 on the sides: the layout of slide 22.
CENTERS = [(0, 0), (-D, -0.8 * D), (D, 0.8 * D)]
ROWS = [("классы поровну", [80, 80, 80]), ("средний класс мал", [40, 100, 100])]
shade = LinearSegmentedColormap.from_list("mid", [fk.tint(fk.GRIDC, 0.7), fk.tint(fk.CATEGORICAL[0], 0.1)])


def frame(ax, xx, yy, Xtr, ytr, Xte, yte):
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(fk.GRIDC)
    fk._scatter(ax, Xtr, ytr, K)
    fk._scatter(ax, Xte, yte, K, hollow=True)


def corner(ax, text):
    ax.text(0.98, 0.02, text, transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


fig, axes = fk.subplots(len(ROWS), 3, size=(11.4, 7.4))
for i, (label, sizes) in enumerate(ROWS):
    X, y = make_blobs(sizes, centers=CENTERS, cluster_std=STD, random_state=fk.SEED)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    ovr = OneVsRestClassifier(LogisticRegression()).fit(Xtr, ytr)
    ovo = OneVsOneClassifier(LogisticRegression()).fit(Xtr, ytr)
    xx, yy, pts = fk._grid(np.vstack([Xtr, Xte]))
    p_mid = ovr.estimators_[0].predict_proba(pts)[:, 1].reshape(xx.shape)
    share = (ovr.predict(X) == 0).mean()
    p_obj = ovr.estimators_[0].predict_proba(X[y == 0])[:, 1]
    print(label, "P(middle) on middle-class objects: mean", round(float(p_obj.mean()), 3),
          "max", round(float(p_obj.max()), 3), "| max over the whole plot (an empty corner)",
          round(float(p_mid.max()), 3),
          "OvR train/test", round(ovr.score(Xtr, ytr), 3), round(ovr.score(Xte, yte), 3),
          "OvO train/test", round(ovo.score(Xtr, ytr), 3), round(ovo.score(Xte, yte), 3),
          "middle predicted share", round(float(share), 3), "true", round(float((y == 0).mean()), 3))

    ax = axes[i, 0]
    cf = ax.contourf(xx, yy, p_mid, levels=np.linspace(0, 1, 11), cmap=shade, vmin=0, vmax=1)
    frame(ax, xx, yy, Xtr, ytr, Xte, yte)
    cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("$P$(средний)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    ax.set_ylabel(label)
    corner(ax, f"на объектах среднего\nкласса $P\\approx{fk.num(p_obj.mean(), 2, math=True)}$")
    if i == 0:
        ax.set_title("средний против остальных")
    for ax, model, title in ((axes[i, 1], ovr, "One vs Rest"), (axes[i, 2], ovo, "One vs One")):
        fk.plot_decision(ax, model, Xtr, ytr, X_test=Xte, y_test=yte, title=title if i == 0 else None)

fig.tight_layout()
fk.save(fig, fk.attachments(3) / "multiclass-failure.png")
