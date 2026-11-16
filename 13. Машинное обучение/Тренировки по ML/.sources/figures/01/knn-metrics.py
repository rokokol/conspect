"""Unit balls of three metrics and kNN zones on moons under each of them (k = 15)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from matplotlib.patches import Circle, Polygon  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

METRICS = [("euclidean", "Евклидова, $L_2$"), ("manhattan", "Манхэттенская, $L_1$"),
           ("chebyshev", "Чебышёва, $L_\\infty$")]

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
fig, axes = fk.subplots(2, 3, size=(10.5, 6.6))

for j, (metric, label) in enumerate(METRICS):
    ax = axes[0, j]
    fill, edge = fk.tint(fk.BLUE, 0.6), fk.BLUE
    if metric == "euclidean":
        ax.add_patch(Circle((0, 0), 1, fc=fill, ec=edge, lw=2))
    elif metric == "manhattan":
        ax.add_patch(Polygon([(1, 0), (0, 1), (-1, 0), (0, -1)], fc=fill, ec=edge, lw=2))
    else:
        ax.add_patch(Polygon([(1, 1), (-1, 1), (-1, -1), (1, -1)], fc=fill, ec=edge, lw=2))
    ax.plot([0], [0], "o", color=fk.TEXT, ms=4)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axhline(0, color=fk.GRIDC, lw=0.8, zorder=0)
    ax.axvline(0, color=fk.GRIDC, lw=0.8, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(label)
    m = KNeighborsClassifier(15, metric=metric).fit(Xtr, ytr)
    fk.plot_decision(axes[1, j], m, Xtr, ytr, X_test=Xte, y_test=yte)

axes[0, 0].set_ylabel("шар радиуса 1")
axes[1, 0].set_ylabel("зоны, k = 15")
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "knn-metrics-balls-zones.png")
