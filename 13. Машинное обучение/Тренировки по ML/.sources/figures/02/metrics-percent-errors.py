"""MAPE and SMAPE of one object with y = 100 as the prediction moves: which side of the target each metric punishes harder."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

Y = 100.0
pred = np.linspace(0.5, 300, 600)
mape = 100 * np.abs(Y - pred) / Y
smape = 100 * np.abs(Y - pred) / ((np.abs(Y) + np.abs(pred)) / 2)

fig, ax = fk.subplots(1, 1, size=(6.6, 3.8))
ax.plot(pred, mape, color=fk.MODEL_C, lw=2, label="MAPE")
ax.plot(pred, smape, color=fk.MODEL2_C, lw=2, label="SMAPE")
ax.axvline(Y, color=fk.GRIDC, lw=1, ls=":")
for p, text_xy in [(50, (62, 150)), (150, (165, 165))]:
    m = 100 * abs(Y - p) / Y
    s = 100 * abs(Y - p) / ((Y + p) / 2)
    ax.scatter([p, p], [m, s], color=[fk.MODEL_C, fk.MODEL2_C], s=34, edgecolor="white", zorder=4)
    ax.annotate(f"$\\hat y={p}$:\nMAPE {m:.0f}%\nSMAPE {s:.0f}%", (p, max(m, s)), xytext=text_xy, textcoords="data",
                ha="left", va="center", fontsize=8, color=fk.TEXT,
                arrowprops=dict(arrowstyle="->", color=fk.TEXT_2, lw=0.8))
ax.set_ylim(0, 230)
ax.set_xlim(0, 300)
ax.set_xlabel("предсказание $\\hat y$ при $y=100$")
ax.set_ylabel("ошибка объекта, %")
ax.set_title("MAPE и SMAPE при $y=100$")
ax.grid(True, axis="y")
ax.legend(loc="upper left")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "metrics-percent-errors.png")
