"""Teacher, student on hard labels, student on soft labels: decision zones side by side on moons and circles.

Teacher: gradient boosting, its depth and number of trees chosen by 5-fold CV on the train part.
Students: the same network (4 tanh units); the soft one has T and the weight of the hard term alpha chosen by CV
on the train part, with the hard-label student (alpha = 1) as the baseline that wins ties. The test part is
only shown. Output: distill-hard-vs-soft.png, and on stdout the choices and a check on other draws of moons.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.special import softmax
from sklearn import datasets as skd
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import distill_common as dc  # noqa: E402
import figkit as fk  # noqa: E402

HIDDEN = (4,)
TEMPS = (1.0, 2.0, 4.0, 8.0, 16.0)
ALPHAS = (0.0, 0.25, 0.5)
TITLES = ["Учитель: бустинг", "Ученик на жёстких метках", "Ученик на мягких метках"]


def run(name):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    params = dc.choose_teacher(Xtr, ytr)
    (T, a), grid = dc.choose_student(params, Xtr, ytr, HIDDEN, TEMPS, ALPHAS)
    teacher = dc.fit_teacher(params, Xtr, ytr)
    hard = dc.fit_student(teacher, Xtr, ytr, hidden=HIDDEN, alpha=1.0)
    soft = dc.fit_student(teacher, Xtr, ytr, hidden=HIDDEN, T=T, alpha=a)
    print(f"{name}\tteacher {params}\tstudent T={T:g} alpha={a:g}\tCV hard {grid[(1.0, 1.0)]:.3f} soft {grid[(T, a)]:.3f}")
    for tag, m in [("teacher", teacher), ("hard", hard), ("soft", soft)]:
        print(f"{name}\t{tag}\ttrain {m.score(Xtr, ytr):.3f}\ttest {m.score(Xte, yte):.3f}")
    p_true = teacher.predict_proba(Xtr)[np.arange(len(ytr)), ytr]
    print(f"{name}\tteacher on its own train part: mean probability of the true class {p_true.mean():.3f},"
          f" share above 0.95 {np.mean(p_true > 0.95):.2f}")
    return (Xtr, Xte, ytr, yte), (teacher, hard, soft), params, (T, a)


def other_draws(params, T, a, seeds=range(1, 9)):
    """Same choices on fresh draws of moons: accuracy and log-loss of the three models on the test part."""
    rows = []
    for s in seeds:
        X, y = skd.make_moons(300, noise=0.3, random_state=s)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=fk.SEED, stratify=y)
        t = dc.fit_teacher(params, Xtr, ytr)
        h = dc.fit_student(t, Xtr, ytr, hidden=HIDDEN, alpha=1.0)
        so = dc.fit_student(t, Xtr, ytr, hidden=HIDDEN, T=T, alpha=a)
        rows.append([[m.score(Xte, yte), log_loss(yte, m.predict_proba(Xte))] for m in (t, h, so)])
    rows = np.array(rows)
    for k, tag in enumerate(["teacher", "hard", "soft"]):
        print(f"draws 1-8 moons\t{tag}\tacc {rows[:, k, 0].mean():.3f}\tlog-loss {rows[:, k, 1].mean():.3f}")
    print("draws: soft beats hard in accuracy", int((rows[:, 2, 0] > rows[:, 1, 0]).sum()), "ties",
          int((rows[:, 2, 0] == rows[:, 1, 0]).sum()), "of", len(rows),
          "; in log-loss", int((rows[:, 2, 1] < rows[:, 1, 1]).sum()), "of", len(rows))


if __name__ == "__main__":
    fig, axes = fk.subplots(2, 3, size=(3.2 * 3, 3.3 * 2))
    for i, name in enumerate(["moons", "circles"]):
        (Xtr, Xte, ytr, yte), models, params, (T, a) = run(name)
        notes = [f"{params['n_estimators']} деревьев, глубина {params['max_depth']}", "только жёсткие метки",
                 f"T={fk.num(T, None)}, вес жёсткой части {fk.num(a, None)}"]
        for j, m in enumerate(models):
            fk.plot_decision(axes[i, j], m, Xtr, ytr, X_test=Xte, y_test=yte)
            axes[i, j].set_xlabel(notes[j], fontsize=7)
            if i == 0:
                axes[i, j].set_title(TITLES[j], fontsize=9)
        axes[i, 0].set_ylabel(name)
        if name == "moons":
            other_draws(params, T, a)
    fig.tight_layout()
    fk.save(fig, fk.attachments(8) / "distill-hard-vs-soft.png")
