"""One vs Rest and One vs One with logistic regression on blobs3: the binary boundaries, the undecided zones of plain voting, the final regions."""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, y = fk.dataset("blobs3")
Xtr, Xte, ytr, yte = fk.split(X, y)
K = 3
UNDECIDED = fk.tint(fk.GRIDC, 0.35)

ovr = OneVsRestClassifier(LogisticRegression()).fit(Xtr, ytr)
ovo = OneVsOneClassifier(LogisticRegression()).fit(Xtr, ytr)
pairs = list(combinations(range(K), 2))
pair_models = {p: LogisticRegression().fit(Xtr[np.isin(ytr, p)], (ytr[np.isin(ytr, p)] == p[1]).astype(int))
               for p in pairs}

xx, yy, pts = fk._grid(np.vstack([Xtr, Xte]))
ovr_scores = np.column_stack([e.decision_function(pts) for e in ovr.estimators_])
assert (ovr_scores.argmax(1) == ovr.predict(pts)).all()

# Plain voting: a point is decided only when exactly one rule fires, or one class gets two votes.
mine = ovr_scores > 0
ovr_vote = np.where(mine.sum(1) == 1, mine.argmax(1), K)
votes = np.zeros((len(pts), K), int)
for (a, b), m in pair_models.items():
    says_b = m.predict(pts) == 1
    votes[np.arange(len(pts)), np.where(says_b, b, a)] += 1
ovo_vote = np.where(votes.max(1) >= 2, votes.argmax(1), K)
# Voting plus confidences, the way scikit-learn breaks the 1-1-1 tie, must agree where the vote is decisive.
dec = ovo_vote < K
assert (ovo.predict(pts)[dec] == ovo_vote[dec]).all()
print("undecided share OvR vote", round(float((ovr_vote == K).mean()), 3),
      "(share of the 300x300 plotting grid)")
print("OvO vote undecided share of the plotting grid", round(float((ovo_vote == K).mean()), 3),
      "- the grid cell is larger than the tie triangle, so this is not a proof of absence")
print("OvR and OvO agree on", round(float((ovr.predict(pts) == ovo.predict(pts)).mean()), 4), "of the grid")


def vote_at(points):
    v = np.zeros((len(points), K), int)
    for (a, b), m in pair_models.items():
        v[np.arange(len(points)), np.where(m.predict(points) == 1, b, a)] += 1
    return v


# The three pairwise lines nearly meet in one point; zoom there with a grid far finer than the plot's.
verts = []
for p, q in combinations(pairs, 2):
    A = np.array([pair_models[p].coef_[0], pair_models[q].coef_[0]])
    verts.append(np.linalg.solve(A, -np.array([pair_models[p].intercept_[0], pair_models[q].intercept_[0]])))
c0 = np.mean(verts, axis=0)
HALF = 0.03
zg = np.linspace(-HALF, HALF, 801)
zx, zy = np.meshgrid(zg + c0[0], zg + c0[1])
zpts = np.c_[zx.ravel(), zy.ravel()]
zv = vote_at(zpts)
tie = zv.max(1) < 2
tie_area = float(tie.mean()) * (2 * HALF) ** 2
plot_area = float((xx.max() - xx.min()) * (yy.max() - yy.min()))
print("tie triangle: area", round(tie_area, 6), "share of the plotted area", round(tie_area / plot_area, 8))

cmap = ListedColormap([fk.region_color(k) for k in range(K)] + [UNDECIDED])


def frame(ax, title):
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(fk.GRIDC)
    ax.set_title(title)
    fk._scatter(ax, Xtr, ytr, K)
    fk._scatter(ax, Xte, yte, K, hollow=True)


def regions(ax, labels):
    ax.pcolormesh(xx, yy, labels.reshape(xx.shape), cmap=cmap, vmin=-0.5, vmax=K + 0.5, shading="auto")


def score(ax, model):
    ax.text(0.98, 0.02, f"train {fk.num(model.score(Xtr, ytr), 2)}\ntest {fk.num(model.score(Xte, yte), 2)}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


fig, axes = fk.subplots(2, 3, size=(10.8, 7.0))

ax = axes[0, 0]
for k, est in enumerate(ovr.estimators_):
    ax.contourf(xx, yy, (est.decision_function(pts) > 0).reshape(xx.shape), levels=[0.5, 1.5],
                colors=[fk.region_color(k)], alpha=0.4)
    ax.contour(xx, yy, est.decision_function(pts).reshape(xx.shape), levels=[0], colors=[fk.CATEGORICAL[k]],
               linewidths=2)
frame(ax, "One vs Rest: три границы")
ax.set_ylabel("One vs Rest")

ax = axes[0, 1]
regions(ax, ovr_vote)
frame(ax, "по знаку, без отступов")

ax = axes[0, 2]
regions(ax, ovr.predict(pts))
frame(ax, "по наибольшему отступу")
score(ax, ovr)

ax = axes[1, 0]
styles = ["-", "--", ":"]
for (a, b), ls in zip(pairs, styles):
    ax.contour(xx, yy, pair_models[(a, b)].decision_function(pts).reshape(xx.shape), levels=[0],
               colors=[fk.TEXT], linewidths=1.8, linestyles=ls)
frame(ax, "One vs One: три границы")
ax.set_ylabel("One vs One")

ax = axes[1, 1]
regions(ax, ovo_vote)
frame(ax, "голосование")
ax.add_patch(Rectangle((c0[0] - HALF, c0[1] - HALF), 2 * HALF, 2 * HALF, fill=False, ec=fk.TEXT, lw=1))
ins = ax.inset_axes([0.60, 0.60, 0.38, 0.38])
ins.pcolormesh(zx, zy, np.where(tie, K, zv.argmax(1)).reshape(zx.shape), cmap=cmap, vmin=-0.5, vmax=K + 0.5,
               shading="auto")
for (a, b), ls in zip(pairs, styles):
    ins.contour(zx, zy, pair_models[(a, b)].decision_function(zpts).reshape(zx.shape), levels=[0],
                colors=[fk.TEXT], linewidths=1.2, linestyles=ls)
ins.set_xlim(c0[0] - HALF, c0[0] + HALF)
ins.set_ylim(c0[1] - HALF, c0[1] + HALF)
ins.set_xticks([])
ins.set_yticks([])
ins.text(0.03, 0.03, "ничья 1-1-1\nкрупно", transform=ins.transAxes, fontsize=6, color=fk.TEXT,
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

ax = axes[1, 2]
regions(ax, ovo.predict(pts))
frame(ax, "итог OneVsOneClassifier")
score(ax, ovo)

fig.tight_layout()
fk.save(fig, fk.attachments(3) / "multiclass-ovr-ovo.png")
