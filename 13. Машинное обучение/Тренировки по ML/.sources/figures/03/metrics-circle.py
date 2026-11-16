"""Predicted positives as a circle over two classes: TP, FP, FN, TN, and the two ratios read off the picture."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
n_pos, n_neg = 36, 36
pos = np.c_[rng.uniform(0.04, 0.96, n_pos), rng.uniform(0.04, 0.96, n_pos)]
neg = np.c_[rng.uniform(1.04, 1.96, n_neg), rng.uniform(0.04, 0.96, n_neg)]
center, radius = np.array([0.95, 0.5]), 0.62


def inside(p):
    return np.linalg.norm(p - center, axis=1) < radius


tp, fn = inside(pos).sum(), (~inside(pos)).sum()
fp, tn = inside(neg).sum(), (~inside(neg)).sum()
precision, recall = tp / (tp + fp), tp / (tp + fn)
print(f"TP {tp} FP {fp} FN {fn} TN {tn} precision {precision:.3f} recall {recall:.3f}")

fig, (ax, bx) = fk.subplots(1, 2, size=(10.4, 4.0), gridspec_kw={"width_ratios": [1.5, 1]})
ax.add_patch(Rectangle((0, 0), 1, 1, fc=fk.tint(fk.CLASS_COLORS[1], 0.85), ec="none", zorder=0))
ax.add_patch(Rectangle((1, 0), 1, 1, fc=fk.tint(fk.CLASS_COLORS[0], 0.85), ec="none", zorder=0))
ax.add_patch(Circle(center, radius, fc="none", ec=fk.TEXT, lw=2, zorder=2))
for p, c in ((pos, 1), (neg, 0)):
    m = inside(p)
    ax.scatter(*p[m].T, s=34, color=fk.CLASS_COLORS[c], edgecolors="white", linewidths=0.8, zorder=3)
    ax.scatter(*p[~m].T, s=34, facecolors="white", edgecolors=fk.CLASS_COLORS[c], linewidths=1.2, zorder=3)
for x, y, label in ((0.16, 1.18, f"FN = {fn}"), (0.65, 1.18, f"TP = {tp}"), (1.3, 1.18, f"FP = {fp}"),
                    (1.8, 1.18, f"TN = {tn}")):
    ax.text(x, y, label, ha="center", va="bottom", fontsize=9, color=fk.TEXT)
ax.text(0.5, -0.2, "настоящие положительные", ha="center", va="top", color=fk.CLASS_COLORS[1], fontsize=9)
ax.text(1.5, -0.2, "настоящие отрицательные", ha="center", va="top", color=fk.CLASS_COLORS[0], fontsize=9)
ax.set_xlim(-0.05, 2.05)
ax.set_ylim(-0.4, 1.4)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("что внутри круга, то объявлено 1")

bx.axis("off")
bx.set_xlim(0, 1)
bx.set_ylim(0, 1)
bx.set_title("две дроби")
bx.text(0.0, 0.78, "precision", fontsize=12, color=fk.TEXT)
bx.text(0.0, 0.62, f"= TP / (TP + FP) = {tp} / {tp + fp} = {fk.num(precision, 2)}", fontsize=9, color=fk.TEXT)
bx.text(0.0, 0.52, "доля положительных среди попавших в круг", fontsize=8, color=fk.TEXT_2)
bx.text(0.0, 0.32, "recall", fontsize=12, color=fk.TEXT)
bx.text(0.0, 0.16, f"= TP / (TP + FN) = {tp} / {tp + fn} = {fk.num(recall, 2)}", fontsize=9, color=fk.TEXT)
bx.text(0.0, 0.06, "доля положительных, попавших в круг", fontsize=8, color=fk.TEXT_2)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "metrics-circle.png")
