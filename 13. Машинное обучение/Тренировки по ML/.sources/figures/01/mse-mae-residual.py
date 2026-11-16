"""MSE and MAE as functions of one residual, and how the five random-model residuals of slide 24 weigh in."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import figkit as fk  # noqa: E402

OUT = fk.attachments(1)

TARGET = np.array([5, 4, 5, 5, 2])
RANDOM = np.array([1, 5, 2, 4, 3])
E = TARGET - RANDOM  # 4, -1, 3, 1, -1
NAMES = ["John", "Aahna", "Emily", "Michael", "Some st."]

fig, (a, b) = fk.plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw=dict(width_ratios=[1.1, 1]))

e = np.linspace(-4.6, 4.6, 400)
a.plot(e, e ** 2, color=fk.TEST_C, label="$e^2$")
a.plot(e, np.abs(e), color=fk.TRAIN_C, label="$|e|$")
a.scatter(E, E ** 2, s=30, color=fk.TEST_C, edgecolors="white", zorder=3)
a.scatter(E, np.abs(E), s=30, color=fk.TRAIN_C, edgecolors="white", zorder=3)
a.set_ylim(-0.6, 18)
a.set_xlabel("остаток $e = y - \\hat y$")
a.set_ylabel("штраф")
a.set_title("Штраф за один объект")
a.set_axisbelow(True)
a.grid(True, axis="y")
a.legend(loc="upper center")

x = np.arange(len(E))
w = 0.38
b.bar(x - w / 2, E ** 2, w, color=fk.TEST_C, label=f"$e^2$, сумма {int((E ** 2).sum())}")
b.bar(x + w / 2, np.abs(E), w, color=fk.TRAIN_C, label=f"$|e|$, сумма {int(np.abs(E).sum())}")
b.set_xticks(x)
b.set_xticklabels(NAMES, fontsize=7.5)
b.set_ylabel("вклад в сумму")
b.set_title("Вклад каждого объекта")
b.set_axisbelow(True)
b.grid(True, axis="y")
b.legend(loc="upper right")

fig.tight_layout()
fk.save(fig, OUT / "mse-mae-residual.png")
