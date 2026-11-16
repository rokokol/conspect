"""Normal vector and signed distance (w^T x is the distance only when |w| = 1), and margins of a fitted linear classifier."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

OUT = fk.attachments(3)

# Figure 1: hyperplane w^T x = 0, normal w with |w| = 2, two points projected on the normal axis.
fig, ax = fk.plt.subplots(figsize=(5.2, 4.2))
w = np.array([1.2, 1.6])
norm = np.linalg.norm(w)
unit = w / norm
direction = np.array([-unit[1], unit[0]])
t = np.linspace(-3.2, 3.2, 2)
ax.plot(*(t[:, None] * direction).T, color=fk.TEXT, lw=1.6)
axis = np.array([-2.0, 2.6])[:, None] * unit
ax.plot(*axis.T, color=fk.MODEL2_C, lw=0.8, ls="--", zorder=1)
ax.annotate("", xy=w, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=fk.MODEL2_C, lw=2))
ax.text(-0.9, 2.05, f"нормаль $w$, $\\|w\\|={norm:.0f}$", color=fk.TEXT, fontsize=9)
points = {"A": (np.array([2.0, 0.6]), 1, (2.2, 0.4), "top"), "B": (np.array([-1.8, -0.9]), -1, (-3.2, -1.75), "top")}
for name, (p, label, off, va) in points.items():
    proj = (p @ unit) * unit
    color = fk.CLASS_COLORS[1] if label == 1 else fk.CLASS_COLORS[0]
    ax.plot([p[0], proj[0]], [p[1], proj[1]], color=color, lw=1, ls=":")
    ax.scatter(*p, s=46, color=color, edgecolors="white", zorder=4)
    dist = p @ unit
    ax.text(off[0], off[1], f"{name}: $w^\\top x={fk.num(p @ w, 2, math=True)}$\nрасстояние ${fk.num(dist, 2, math=True)}$", fontsize=8,
            color=fk.TEXT, va=va)
    print(name, "w^T x", round(float(p @ w), 3), "signed distance", round(float(dist), 3))
ax.text(-3.0, 1.35, "$w^\\top x=0$", fontsize=9, color=fk.TEXT)
ax.set_xlim(-3.3, 3.3)
ax.set_ylim(-3.0, 3.0)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Нормаль и знаковое расстояние")
fig.tight_layout()
fk.save(fig, OUT / "margin-geometry.png")

# Figure 2: margins M = y * f(x) of a fitted classifier on the linear data set, with the intercept.
X, y = fk.dataset("linear")
Xtr, Xte, ytr, yte = fk.split(X, y)
model = LogisticRegression().fit(Xtr, ytr)
M = (2 * ytr - 1) * model.decision_function(Xtr)
rng = np.random.default_rng(fk.SEED)
fig, bx = fk.plt.subplots(figsize=(6.2, 3.8))
for k in (0, 1):
    m = M[ytr == k]
    bx.scatter(m, rng.uniform(-0.35, 0.35, len(m)) + (0.5 if k == 1 else -0.5), s=16, color=fk.CLASS_COLORS[k],
               edgecolors="white", linewidths=0.5, zorder=3, label=f"класс {2 * k - 1:+d}")
bx.axvspan(M.min() - 0.5, 0, color=fk.tint(fk.GRIDC, 0.55), zorder=0)
bx.axvline(0, color=fk.TEXT, lw=1.2)
bx.text(M.min() + 0.1, 1.05, "ошибка: $M<0$", fontsize=8, color=fk.TEXT)
bx.text(0.15, 1.05, "верный класс: $M>0$", fontsize=8, color=fk.TEXT)
bx.set_ylim(-1.1, 1.25)
bx.set_xlim(M.min() - 0.5, M.max() + 0.5)
bx.set_yticks([])
bx.set_xlabel("отступ $M=y\\cdot f(x)$")
bx.set_title("Отступы обучающих объектов")
bx.legend(loc="lower right", frameon=True, framealpha=0.95)
bx.grid(False)
print("train margins: errors", int((M < 0).sum()), "of", len(M), "min", round(float(M.min()), 2), "max",
      round(float(M.max()), 2))
fig.tight_layout()
fk.save(fig, OUT / "margin-distribution.png")
