"""R^2 compares a model with the constant mean: zero for the mean, near one for a fit, negative for a model worse than the mean."""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
x = np.sort(rng.uniform(0, 10, 20))
y = 2.0 + 0.8 * x + rng.normal(0, 0.6, x.size)
ybar = y.mean()

w1, w0 = np.polyfit(x, y, 1)
MODELS = [
    ("Среднее $\\bar y$", np.full_like(x, ybar)),
    ("Прямая МНК", w0 + w1 * x),
    ("Прямая с обратным наклоном", 11.0 - 0.9 * x),
]

fig, axes = fk.subplots(1, 3, size=(12.0, 3.7))
grid = np.array([-0.3, 10.3])
var = y.var()
for ax, (name, pred), shape in zip(axes, MODELS, ["const", "fit", "bad"]):
    r2 = r2_score(y, pred)
    mse = ((y - pred) ** 2).mean()
    assert abs(r2 - (1 - mse / var)) < 1e-12  # R^2 = 1 - MSE / Var(y)
    for xi, yi, pi in zip(x, y, pred):
        ax.plot([xi, xi], [yi, pi], color=fk.TEXT_2, lw=0.9, ls=":", zorder=2)
    if shape == "const":
        ax.plot(grid, [ybar, ybar], color=fk.MODEL_C, lw=2.2, zorder=3, label="модель = среднее $\\bar y$")
    else:
        ax.axhline(ybar, color=fk.MODEL2_C, lw=1.4, ls="--", zorder=2, label="среднее $\\bar y$: эталон $R^2=0$")
        line = w0 + w1 * grid if shape == "fit" else 11.0 - 0.9 * grid
        ax.plot(grid, line, color=fk.MODEL_C, lw=2.2, zorder=3, label="модель")
    ax.scatter(x, y, s=26, color=fk.TEXT_2, edgecolor="white", zorder=4)
    ax.legend(loc="upper left", fontsize=7)
    ax.set_title(name)
    ax.text(0.97, 0.05, f"$R^2={fk.num(r2, 2, math=True)}$", transform=ax.transAxes, ha="right", fontsize=10, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9))
    ax.set_xlim(-0.3, 10.3)
    ax.set_ylim(-3.5, 15.5)
    ax.set_xlabel("признак $x$")
    ax.grid(True)
axes[0].set_ylabel("целевая переменная $y$")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "metrics-r2.png")
print([round(r2_score(y, p), 3) for _, p in MODELS], "Var(y) =", round(var, 3))
