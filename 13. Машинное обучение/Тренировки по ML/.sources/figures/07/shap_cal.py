"""California Housing, one gradient boosting model and its exact Shapley values, shared by the waterfall and beeswarm figures.

The data file comes from the sklearn URL; the venv's Python lacks the system CA bundle, so the archive is fetched once with
curl and unpacked by sklearn's own loader (the checksum is sklearn's). Depth is chosen by 3-fold CV on the train part only.
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from shapley_lib import gbr_coalition_values, shapley_from_values  # noqa: E402

HOME = Path(os.path.expanduser("~/.cache/ml-trainings-digitization/scikit_learn_data"))
URL = "https://ndownloader.figshare.com/files/5976036"
N_TREES = 100
DEPTH_GRID = [2, 3, 4]


def load():
    import sklearn.datasets._california_housing as mod
    from sklearn.datasets import fetch_california_housing
    if not (HOME / "cal_housing_py3.pkz").exists():
        HOME.mkdir(parents=True, exist_ok=True)
        tgz = HOME / "cal_housing.tgz"
        subprocess.run(["curl", "-sL", "-o", str(tgz), URL], check=True)
        mod._fetch_remote = lambda meta, dirname=None, **kw: str(tgz)
    d = fetch_california_housing(data_home=str(HOME))
    return d.data, d.target, list(d.feature_names)


def fit():
    X, y, names = load()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=fk.SEED)
    grid = GridSearchCV(GradientBoostingRegressor(n_estimators=N_TREES, random_state=fk.SEED),
                        {"max_depth": DEPTH_GRID}, cv=3, n_jobs=3).fit(Xtr, ytr)
    return grid.best_estimator_, grid.best_params_["max_depth"], X, y, Xtr, Xte, ytr, yte, names


def explain(model, X):
    """v table [2^8, n] and Shapley values [n, 8]."""
    v = gbr_coalition_values(model, X)
    return v, shapley_from_values(v, X.shape[1]).T
