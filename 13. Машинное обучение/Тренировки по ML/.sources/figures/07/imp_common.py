"""Shared data and model for the importance figures of topic 07: one table, one forest, so methods differ and nothing else does."""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

N_FOREST = 200
LEAF_GRID = [1, 5, 20]


def table(n=1200, seed=fk.SEED):
    """Binary target from two continuous signals and one binary flag; two pure-noise columns.

    noise_num has a distinct value in every row (the highest possible cardinality), noise_cat has three values.
    """
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    flag = rng.integers(0, 2, size=n)
    score = 1.0 * x1 + 0.6 * x2 + 1.6 * (flag - 0.5) + rng.normal(0, 0.9, size=n)
    y = (score > 0).astype(int)
    cols = {
        "x1": x1,
        "x2": x2,
        "flag": flag.astype(float),
        "noise_num": rng.normal(size=n),
        "noise_cat": rng.integers(0, 3, size=n).astype(float),
    }
    return list(cols), np.column_stack(list(cols.values())), y


def held_out(X, y):
    """Train part and the held-out part; the held-out part never picks anything, it only measures."""
    return train_test_split(X, y, test_size=0.3, random_state=fk.SEED, stratify=y)


def forest(Xtr, ytr):
    """Forest whose leaf size is chosen by 5-fold CV on the train part only."""
    grid = GridSearchCV(
        RandomForestClassifier(n_estimators=N_FOREST, random_state=fk.SEED, n_jobs=-1),
        {"min_samples_leaf": LEAF_GRID}, cv=5, n_jobs=1).fit(Xtr, ytr)
    return grid.best_estimator_, grid.best_params_["min_samples_leaf"]


def drop_column(make, Xtr, ytr, Xval, yval, base_score):
    """Retrain without each column and score on the held-out part: base minus score without the column."""
    out = []
    for j in range(Xtr.shape[1]):
        keep = [k for k in range(Xtr.shape[1]) if k != j]
        m = make().fit(Xtr[:, keep], ytr)
        out.append(base_score - m.score(Xval[:, keep], yval))
    return np.array(out)
