"""Train, test and leave-one-out cross-validation error against polynomial degree; the choice is marked by validation only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
import overfit_common as oc  # noqa: E402

degrees = np.arange(0, oc.MAX_DEGREE + 1)
tr = [oc.mse(oc.fit(d), oc.x_tr, oc.y_tr) for d in degrees]
te = [oc.mse(oc.fit(d), oc.x_te, oc.y_te) for d in degrees]
va = [oc.cv_mse(d) for d in degrees]

fig, ax = fk.plt.subplots(figsize=(6.4, 3.8))
b = fk.complexity_curve(ax, degrees, tr, te, val=va, better="min", xlabel="степень полинома $d$ (ёмкость модели)",
                        ylabel="MSE")
ax.set_yscale("log")
ax.set_xticks(degrees)
ax.set_title("Ошибка по ёмкости модели")
ax.legend(loc="lower left")
ax.text(1, 1.5, "недообучение", ha="center", fontsize=8, color=fk.TEXT_2)
ax.text(13.5, 0.052, "переобучение", ha="center", fontsize=7, color=fk.TEXT_2)
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "overfit-complexity-curve.png")
print("degree by validation", degrees[b], "test there", round(te[b], 4), "best test", round(min(te), 4),
      "at", degrees[int(np.argmin(te))])
for k in (5, 10):
    v = [oc.cv_mse(d, k) for d in degrees]
    print(f"{k}-fold validation picks degree", degrees[int(np.argmin(v))], "test there", round(te[int(np.argmin(v))], 4))
for d in degrees:
    print(d, "train", round(tr[d], 4), "test", round(te[d], 4), "cv", round(va[d], 4))
