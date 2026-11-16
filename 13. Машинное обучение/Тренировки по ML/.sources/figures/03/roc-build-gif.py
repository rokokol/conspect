"""GIF: a threshold slides from 1 to 0 over the scores of 24 objects and the ROC curve grows one step per object."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
model = LogisticRegression().fit(Xtr, ytr)
score = model.predict_proba(Xte)[:, 1]

# 12 objects of each class from the test part, a fixed draw, so every step is visible.
rng = np.random.default_rng(fk.SEED)
idx = np.r_[rng.choice(np.flatnonzero(yte == 1), 12, replace=False),
            rng.choice(np.flatnonzero(yte == 0), 12, replace=False)]
s, t = score[idx], yte[idx]
order = np.argsort(-s)
s, t = s[order], t[order]
P, N = int(t.sum()), int((1 - t).sum())
tpr = np.r_[0, np.cumsum(t) / P]
fpr = np.r_[0, np.cumsum(1 - t) / N]
auc = float(np.trapezoid(tpr, fpr))
# A vertical spread inside each class row, so that objects with close scores do not hide each other.
jitter = np.random.default_rng(fk.SEED + 1).uniform(-0.3, 0.3, len(s))
print("n", len(s), "P", P, "N", N, "AUC", round(auc, 4))

# Frame 0: threshold above every score (point (0, 0)); frame k: threshold just below the k-th object.
n_frames = len(s) + 1


def draw(ax, i):
    fig = ax.figure
    ax.set_position([0.07, 0.17, 0.42, 0.66])
    rx = fig.add_axes([0.58, 0.17, 0.39, 0.66])
    thr = 1.0 if i == 0 else s[i - 1] - 1e-4
    pred = s >= thr
    for k in (1, 0):
        m = t == k
        c = fk.CLASS_COLORS[k]
        ax.scatter(s[m & pred], k + jitter[m & pred], s=46, color=c, edgecolors="white", linewidths=0.8, zorder=3)
        ax.scatter(s[m & ~pred], k + jitter[m & ~pred], s=46, facecolors="white", edgecolors=c,
                   linewidths=1.3, zorder=3)
    ax.axvline(thr, color=fk.TEXT, lw=2, zorder=2)
    ax.axvspan(thr, 1.02, color=fk.tint(fk.ACCENT, 0.85), zorder=0)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.7, 1.7)
    ax.text(0.01, 1.62, "заливка: объявлен положительным", fontsize=7, color=fk.TEXT_2, va="top")
    ax.set_yticks([0, 1], ["класс 0", "класс 1"])
    ax.set_xlabel("оценка P(класс 1)")
    ax.set_title(f"порог {fk.num(thr, 2)}: справа объявлено 1")
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(True)

    rx.plot([0, 1], [0, 1], color=fk.GRIDC, ls="--", lw=1)
    rx.plot(fpr[: i + 1], tpr[: i + 1], color=fk.MODEL_C, lw=2.2)
    rx.scatter([fpr[i]], [tpr[i]], s=70, color=fk.CLASS_COLORS[1], edgecolors="white", zorder=5)
    rx.set_xlim(-0.02, 1.02)
    rx.set_ylim(-0.02, 1.02)
    rx.set_aspect("equal")
    rx.set_xlabel("FPR")
    rx.set_ylabel("TPR")
    rx.set_title(f"TPR {fk.num(tpr[i], 2)}   FPR {fk.num(fpr[i], 2)}")
    rx.grid(True)
    if i == n_frames - 1:
        rx.text(0.98, 0.04, f"AUC = {fk.num(auc, 2)}", ha="right", fontsize=10, color=fk.TEXT,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))


fk.gif(draw, n_frames, fk.attachments(3) / "roc-build.gif", size=(9.6, 4.2), fps=3, hold_last=6)
