"""Isolation Forest on a cloud with outliers: random cuts that isolate one point, and the mean isolation depth of every point.

Panels one and two replay the idea with plain random cuts (random feature, random threshold between the minimum and
the maximum of the points still in the cell) until the target point is alone. Panel three is the sklearn forest:
the depth of the leaf each point falls in, averaged over its 100 trees, sorted.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import IsolationForest  # noqa: E402

import figkit as fk  # noqa: E402

N_OUT = 8
N_TREES = 100

X_in, _ = fk.dataset("blobs3")
rng = np.random.default_rng(fk.SEED)
outliers = []
while len(outliers) < N_OUT:
    p = rng.uniform([-7, -6], [7, 7])
    if np.min(np.linalg.norm(X_in - p, axis=1)) > 1.8:
        outliers.append(p)
X = np.vstack([X_in, np.array(outliers)])
is_out = np.r_[np.zeros(len(X_in), bool), np.ones(N_OUT, bool)]


def isolate(target, X, rng):
    """Random cuts until `target` is alone: list of (feature, threshold, region before the cut) and the cut count."""
    region = [X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, X[:, 1].min() - 0.5, X[:, 1].max() + 0.5]
    inside = np.ones(len(X), bool)
    cuts = []
    while inside.sum() > 1:
        j = int(rng.integers(2))
        lo, hi = X[inside, j].min(), X[inside, j].max()
        thr = rng.uniform(lo, hi)
        cuts.append((j, thr, list(region)))
        keep = (X[:, j] <= thr) == (X[target, j] <= thr)
        inside &= keep
        if X[target, j] <= thr:
            region[2 * j + 1] = thr
        else:
            region[2 * j] = thr
    return cuts


def mean_cuts(target, repeats=1000):
    r = np.random.default_rng(fk.SEED + 5)
    return float(np.mean([len(isolate(target, X, r)) for _ in range(repeats)]))


i_out = len(X_in)  # the first outlier
i_in = int(np.argmin(np.linalg.norm(X_in - np.median(X_in, axis=0), axis=1)))  # the inlier nearest the median

forest = IsolationForest(n_estimators=N_TREES, random_state=fk.SEED).fit(X)
depth = np.zeros(len(X))
for est, feats in zip(forest.estimators_, forest.estimators_features_):
    depth += np.asarray(est.decision_path(X[:, feats]).sum(1)).ravel() - 1
depth /= N_TREES

def frame(ax):
    ax.set_xlim(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5)
    ax.set_ylim(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(fk.GRIDC)


fig, axes = fk.subplots(2, 2, size=(10.4, 9.0))
for ax, target, name in ((axes[0, 0], i_out, "выброс"), (axes[0, 1], i_in, "объект из плотной группы")):
    cuts = isolate(target, X, np.random.default_rng(fk.SEED + 1))
    ax.scatter(X[:, 0], X[:, 1], s=14, color=fk.GRIDC, edgecolors="white", linewidths=0.4, zorder=2)
    for n, (j, thr, (x0, x1, y0, y1)) in enumerate(cuts, 1):
        if j == 0:
            ax.plot([thr, thr], [y0, y1], color=fk.ACCENT, lw=1.1, zorder=3)
        else:
            ax.plot([x0, x1], [thr, thr], color=fk.ACCENT, lw=1.1, zorder=3)
    ax.scatter(X[target, 0], X[target, 1], s=70, color=fk.CLASS_COLORS[1], edgecolors=fk.ACCENT, linewidths=1.2,
               zorder=5)
    frame(ax)
    ax.set_title(f"{name}: {len(cuts)} разр., в среднем {fk.num(mean_cuts(target), 1)}")

ax = axes[1, 0]
sc = ax.scatter(X[:, 0], X[:, 1], c=depth, s=22, cmap=fk.plt.get_cmap("ddlc_seq").reversed(), edgecolors="white",
                linewidths=0.4)
ax.scatter(X[is_out, 0], X[is_out, 1], s=70, facecolors="none", edgecolors=fk.ACCENT, linewidths=1.1,
           label=f"выбросы ({N_OUT})")
frame(ax)
ax.set_title(f"средняя глубина по {N_TREES} деревьям")
ax.legend(loc="upper left")
fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03, label="средняя глубина листа")

ax = axes[1, 1]
bins = np.arange(3, 8.51, 0.25)
ax.hist(depth[~is_out], bins=bins, color=fk.CLASS_COLORS[0], label="обычные объекты")
ax.hist(depth[is_out], bins=bins, color=fk.CLASS_COLORS[1], label=f"выбросы ({N_OUT})")
ax.set_yscale("log")
ax.set_xlabel("средняя глубина отделения")
ax.set_ylabel("число объектов")
ax.set_title("распределение глубины")
ax.legend(loc="upper left")
fig.subplots_adjust(wspace=0.4, hspace=0.25)
fk.save(fig, fk.attachments(5) / "rf-isolation-forest.png")

order = np.argsort(depth)
print("points", len(X), "outliers", N_OUT)
print("mean cuts outlier", round(mean_cuts(i_out), 2), "inlier", round(mean_cuts(i_in), 2))
print("depth outliers", np.round(np.sort(depth[is_out]), 2).tolist())
print("depth inliers min/median/max", round(depth[~is_out].min(), 2), round(float(np.median(depth[~is_out])), 2),
      round(depth[~is_out].max(), 2))
print("outliers among the", N_OUT, "shallowest:", int(is_out[order[:N_OUT]].sum()))
print("rank of the deepest outlier", int(np.where(order == np.argmax(np.where(is_out, depth, -1)))[0][0]) + 1)
print("max tree depth", [e.get_depth() for e in forest.estimators_[:3]], "max_samples", forest.max_samples_)
