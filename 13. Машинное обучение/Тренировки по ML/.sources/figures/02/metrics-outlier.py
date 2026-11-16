"""MSE against MAE on a line fit with one outlier: gradient of each loss, the two fitted lines, and the slope as the outlier moves away."""
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression, QuantileRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

rng = np.random.default_rng(fk.SEED)
x = np.sort(rng.uniform(0, 10, 20))
y = 2.0 + 0.8 * x + rng.normal(0, 0.6, x.size)
OUT_IDX = 15  # the point that becomes the outlier
SHIFT = 14.0  # how far it is pushed up from where it was


def fits(yv):
    """Slope and intercept of the least-squares line and of the least-absolute-deviations line."""
    mse = LinearRegression().fit(x[:, None], yv)
    # alpha=0: no penalty, so the fit minimises the absolute deviations alone (quantile 0.5)
    mae = QuantileRegressor(quantile=0.5, alpha=0.0, solver="highs").fit(x[:, None], yv)
    return (mse.intercept_, mse.coef_[0]), (mae.intercept_, mae.coef_[0])


y_out = y.copy()
y_out[OUT_IDX] += SHIFT
clean_mse, clean_mae = fits(y)
bad_mse, bad_mae = fits(y_out)

shifts = np.linspace(0, 30, 31)
slopes = np.array([[fits(np.where(np.arange(x.size) == OUT_IDX, y + s, y))[k][1] for k in (0, 1)] for s in shifts])

fig, axes = fk.subplots(1, 3, size=(12.6, 3.7))

ax = axes[0]
e = np.linspace(-4, 4, 400)
ax.plot(e, 2 * e, color=fk.MODEL_C, lw=2, label="MSE: $2e$")
ax.plot(e[e < 0], np.sign(e[e < 0]), color=fk.MODEL2_C, lw=2, label="MAE: $\\mathrm{sign}(e)$")
ax.plot(e[e > 0], np.sign(e[e > 0]), color=fk.MODEL2_C, lw=2)
ax.scatter([0], [0], s=30, color=fk.MODEL2_C, zorder=4)  # the value 0 the lecturer assigns at e = 0
ax.axhline(0, color=fk.GRIDC, lw=0.8)
ax.set_xlabel("остаток $e=y-\\hat y$")
ax.set_ylabel("$\\partial L/\\partial e$")
ax.set_title("Вклад точки в градиент")
ax.set_ylim(-8.5, 8.5)
ax.grid(True, axis="y")
ax.legend(loc="upper left")

ax = axes[1]
t = np.array([-0.3, 10.3])
ax.plot(t, bad_mse[0] + bad_mse[1] * t, color=fk.MODEL_C, lw=2, label="MSE")
ax.plot(t, bad_mae[0] + bad_mae[1] * t, color=fk.MODEL2_C, lw=2, label="MAE")
ax.plot(t, clean_mse[0] + clean_mse[1] * t, color=fk.TEXT, lw=1.6, ls=(0, (4, 3)), zorder=5, label="MSE без выброса")
mask = np.arange(x.size) != OUT_IDX
ax.scatter(x[mask], y_out[mask], s=26, color=fk.TEXT_2, edgecolor="white", zorder=3)
ax.scatter(x[OUT_IDX], y_out[OUT_IDX], s=70, facecolors="white", edgecolors=fk.TEXT, linewidths=1.8, zorder=4, label="выброс")
ax.set_xlabel("признак $x$")
ax.set_ylabel("целевая переменная $y$")
ax.set_title("Две прямые по одним точкам")
ax.set_xlim(-0.3, 10.3)
ax.grid(True)
ax.legend(loc="upper left")

ax = axes[2]
ax.plot(shifts, slopes[:, 0], color=fk.MODEL_C, lw=2, label="MSE")
ax.plot(shifts, slopes[:, 1], color=fk.MODEL2_C, lw=2, label="MAE")
ax.axvline(SHIFT, color=fk.GRIDC, lw=1, ls=":")
ax.set_xlabel("на сколько поднят выброс")
ax.set_ylabel("наклон прямой $w_1$")
ax.set_title("Наклон при уходе выброса")
ax.grid(True)
ax.legend(loc="upper left")

fig.tight_layout()
fk.save(fig, fk.attachments(2) / "metrics-outlier.png")
print("clean", clean_mse, clean_mae)
print("outlier", bad_mse, bad_mae)
print("slopes at 0, 14, 30:", slopes[0], slopes[14], slopes[30])
