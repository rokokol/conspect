"""One network, eight activations, the same data: only the activation changes.

For moons and circles the width of the hidden layer is chosen by 5-fold cross-validation on the train part
(mean over the seven nonlinear activations, so one width serves every tile); every activation is then fitted
at that width on the whole train part. The test part only prints the accuracy of the models already chosen.
Outputs: act-zones-<data>.png (zones), act-cv-activations.png (train, validation and test accuracy by
activation) and act-width-curve.png (the same three by width, mean over the nonlinear activations).
"""
import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[var] = "1"

import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402

OUT = fk.attachments(6)
DATA = ["moons", "circles"]
WIDTHS = [2, 4, 8, 16]
ACTS = list(ac.ACT)
NONLINEAR = [a for a in ACTS if a != "identity"]
N_INIT = 2


def job(args):
    """Validation accuracy of one (data set, width, activation) cell by cross-validation, and the fit on the whole train part."""
    ds, w, act = args
    X, y = fk.dataset(ds)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    val = ac.cv_score(lambda: ac.ActMLP((w,), act, n_init=N_INIT), Xtr, ytr)
    m = ac.ActMLP((w,), act, n_init=N_INIT).fit(Xtr, ytr)
    return (ds, w, act), dict(val=val, train=m.score(Xtr, ytr), test=m.score(Xte, yte))


def main():
    cells = [(ds, w, a) for ds in DATA for w in WIDTHS for a in ACTS]
    with ProcessPoolExecutor(12) as pool:
        res = dict(pool.map(job, cells))

    chosen = {}
    for ds in DATA:
        mean_val = [np.mean([res[ds, w, a]["val"] for a in NONLINEAR]) for w in WIDTHS]
        chosen[ds] = WIDTHS[int(np.argmax(mean_val))]
        print(ds, "width by validation:", chosen[ds], np.round(mean_val, 3))

    # zones: the model is refitted here, the fit is deterministic and equals the one in job()
    for ds in DATA:
        X, y = fk.dataset(ds)
        Xtr, Xte, ytr, yte = fk.split(X, y)
        w = chosen[ds]
        fig, axes = fk.subplots(2, 4, size=(12.4, 6.2))
        for ax, act in zip(axes.ravel(), ACTS):
            m = ac.ActMLP((w,), act, n_init=N_INIT).fit(Xtr, ytr)
            fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte, title=ac.LABEL[act])
            r = res[ds, w, act]
            print(ds, act, f"val {r['val']:.3f} train {r['train']:.3f} test {r['test']:.3f}")
        fig.tight_layout()
        fk.save(fig, OUT / f"act-zones-{ds}.png")

    # activation as a hyperparameter: accuracy by activation at the chosen width
    fig, axes = fk.subplots(1, 2, size=(12.0, 3.8))
    x = np.arange(len(ACTS))
    for ax, ds in zip(axes, DATA):
        w = chosen[ds]
        vals = [res[ds, w, a]["val"] for a in ACTS]
        ax.plot(x, [res[ds, w, a]["train"] for a in ACTS], color=fk.TRAIN_C, marker="o", ms=5, ls="none", label="train")
        ax.plot(x, [res[ds, w, a]["test"] for a in ACTS], color=fk.TEST_C, marker="o", ms=5, ls="none", label="test")
        ax.plot(x, vals, color=fk.TEXT_2, marker="s", ms=5, ls="none", label="валидация")
        b = int(np.argmax(vals))
        ax.axvline(x[b], color=fk.TEXT_2, lw=1, ls="--")
        ax.set_xticks(x, [ac.LABEL[a].replace("без активации", "нет") for a in ACTS], rotation=30, ha="right")
        ax.set_ylabel("accuracy")
        ax.set_title(f"{ds}, ширина {w}")
        ax.grid(True, axis="y")
    axes[0].legend(loc="lower right")
    fig.tight_layout()
    fk.save(fig, OUT / "act-cv-activations.png")

    # width by the three splits, mean over the nonlinear activations
    fig, axes = fk.subplots(1, 2, size=(9.0, 3.4))
    for ax, ds in zip(axes, DATA):
        mean = {k: [np.mean([res[ds, w, a][k] for a in NONLINEAR]) for w in WIDTHS]
                for k in ("train", "test", "val")}
        fk.complexity_curve(ax, WIDTHS, mean["train"], mean["test"], xlabel="нейронов в слое",
                            val=mean["val"], log=True)
        ax.set_xticks(WIDTHS, [str(w) for w in WIDTHS])
        ax.minorticks_off()
        ax.set_title(ds)
    fig.tight_layout()
    fk.save(fig, OUT / "act-width-curve.png")


if __name__ == "__main__":
    main()
