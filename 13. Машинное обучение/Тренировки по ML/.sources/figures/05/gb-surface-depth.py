"""The demo of the lecture, slide 22, redrawn: a surface sin 2πx1 · sin 2πx2, one tree against a boosting of 100 trees, for several depths.

The surface has no noise and is sampled on a 30 x 30 grid; the error is the mean squared distance to the surface on a finer 100 x 100 grid.
No choice is made here: the picture shows what depth does, not which depth is best.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import GradientBoostingRegressor  # noqa: E402
from sklearn.tree import DecisionTreeRegressor  # noqa: E402

import figkit as fk  # noqa: E402

DEPTHS = [1, 2, 3, 4, 6]


def surface(a, b):
    return np.sin(2 * np.pi * a) * np.sin(2 * np.pi * b)


g = np.linspace(0, 1, 30)
A, B = np.meshgrid(g, g)
Xtr, ytr = np.c_[A.ravel(), B.ravel()], surface(A, B).ravel()
f = np.linspace(0, 1, 100)
FA, FB = np.meshgrid(f, f)
Xf = np.c_[FA.ravel(), FB.ravel()]
zf = surface(FA, FB)

fig, axes = fk.subplots(2, len(DEPTHS), size=(3.0 * len(DEPTHS), 6.4))
for j, d in enumerate(DEPTHS):
    models = [DecisionTreeRegressor(max_depth=d, random_state=fk.SEED).fit(Xtr, ytr),
              GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=d,
                                        random_state=fk.SEED).fit(Xtr, ytr)]
    for i, m in enumerate(models):
        z = m.predict(Xf).reshape(zf.shape)
        err = float(np.mean((z - zf) ** 2))
        mesh = axes[i, j].pcolormesh(FA, FB, z, cmap="ddlc_div", vmin=-1, vmax=1, shading="auto")
        axes[i, j].set_xticks([])
        axes[i, j].set_yticks([])
        axes[i, j].set_title(f"глубина {d}\nошибка {fk.num(err, 3)}", fontsize=10)
        print("one tree" if i == 0 else "boosting 100", "depth", d, "error", round(err, 4))
axes[0, 0].set_ylabel("одно дерево")
axes[1, 0].set_ylabel("бустинг, 100 деревьев")
fig.tight_layout()
fig.colorbar(mesh, ax=axes, shrink=0.8, pad=0.02, label="значение поверхности")
fk.save(fig, fk.attachments(5) / "gb-surface-depth.png")
