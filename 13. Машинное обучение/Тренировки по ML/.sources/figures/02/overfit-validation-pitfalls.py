"""Two failures of validation: one unlucky holdout, and a best-of-M choice on a validation set of pure noise."""
import sys
from pathlib import Path

import numpy as np
from sklearn.model_selection import ShuffleSplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
import overfit_common as oc  # noqa: E402

fig, axes = fk.subplots(1, 2, size=(10.2, 3.6))

# Left: the same degree-3 polynomial, 300 random 28/12 splits of the 40 points.
errs = []
for tr, te in ShuffleSplit(300, test_size=12, random_state=fk.SEED).split(oc.X):
    m = oc.fit(3, oc.X[tr, 0], oc.Y[tr])
    errs.append(oc.mse(m, oc.X[te, 0], oc.Y[te]))
errs = np.array(errs)
ax = axes[0]
ax.hist(errs, bins=24, color=fk.TEST_C, edgecolor="white")
ax.axvline(errs.mean(), color=fk.TEXT_2, ls="--", lw=1)
ax.set_xlabel("MSE на отложенных 12 точках")
ax.set_ylabel("число разбиений из 300")
ax.set_title("Одна отложенная выборка шумит")
ax.text(0.97, 0.95, f"среднее {fk.num(errs.mean(), 3)}\nот {fk.num(errs.min(), 3)} до {fk.num(errs.max(), 3)}", transform=ax.transAxes,
        ha="right", va="top", fontsize=8, color=fk.TEXT)
print("holdout mse mean", round(errs.mean(), 4), "min", round(errs.min(), 4), "max", round(errs.max(), 4),
      "5%/95%", np.percentile(errs, [5, 95]).round(4))

# Right: M candidate models without any signal, 50 validation and 1000 test objects with random labels.
rng = np.random.default_rng(fk.SEED)
N_VAL, N_TEST, REPEATS = 50, 1000, 300
ms = np.array([1, 2, 5, 10, 20, 50, 150, 500, 1500])
best_val, chosen_test = [], []
for M in ms:
    accs = np.array([(rng.integers(0, 2, (M, N_VAL)) == rng.integers(0, 2, N_VAL)).mean(1).max()
                     for _ in range(REPEATS)])
    best_val.append(accs.mean())
    chosen_test.append(rng.binomial(N_TEST, 0.5, REPEATS).mean() / N_TEST)
ax = axes[1]
ax.plot(ms, best_val, color=fk.TEXT_2, marker="s", ms=4, ls=":", label="validation: лучшая из $M$")
ax.plot(ms, chosen_test, color=fk.TEST_C, marker="o", ms=5, mfc="white", label="test: выбранная модель")
ax.set_xscale("log")
ax.set_ylim(0.4, 0.9)
ax.set_xlabel("число проверенных конфигураций $M$")
ax.set_ylabel("accuracy")
ax.set_title("Выбор по validation завышает оценку")
ax.grid(True, axis="y")
ax.legend(loc="upper left")
print("M", ms.tolist())
print("best val", np.round(best_val, 3).tolist())
print("test of chosen", np.round(chosen_test, 3).tolist())
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "overfit-validation-pitfalls.png")
