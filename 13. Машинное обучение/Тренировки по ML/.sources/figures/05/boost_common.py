"""Shared pieces of the boosting figures: AdaBoost written out as in the note, a toy sample and the cos + noise sample of the lecture."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402


class AdaBoostScratch:
    """AdaBoost with the exponential loss: weights w_i = exp(-M_i), rho_t = 1/2 ln((1 - eps_t) / eps_t).

    Labels are 0/1 outside and -1/+1 inside. After every round it keeps the weights the round started with.
    """

    def __init__(self, depth=1):
        self.depth = depth

    def fit(self, X, y01, rounds):
        y = 2 * np.asarray(y01) - 1
        n = len(y)
        w = np.full(n, 1 / n)
        self.stumps, self.rho, self.eps, self.weights = [], [], [], []
        for _ in range(rounds):
            h = DecisionTreeClassifier(max_depth=self.depth, random_state=fk.SEED).fit(X, y, sample_weight=w)
            pred = h.predict(X)
            eps = w[pred != y].sum() / w.sum()
            rho = 0.5 * np.log((1 - eps) / max(eps, 1e-12))
            self.stumps.append(h)
            self.rho.append(rho)
            self.eps.append(eps)
            self.weights.append(w.copy())
            w = w * np.exp(-rho * y * pred)
            w = w / w.sum()
        self.classes_ = np.array([0, 1])
        return self

    def score_at(self, X, upto=None):
        upto = len(self.stumps) if upto is None else upto
        return sum(r * h.predict(X) for r, h in zip(self.rho[:upto], self.stumps[:upto]))

    def decision_function(self, X):
        return self.score_at(X)


def toy_quadrant(seed=46, n=20):
    """Twenty points on the plane; class 1 is the quadrant x1 > 0, x2 > -0.1, which no single stump separates."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(-1, 1, (n, 2))
    return X, ((X[:, 0] > 0.0) & (X[:, 1] > -0.1)).astype(int)


def ods_cos(n=240, noise_var=0.2):
    """The example of the lecture, slide 24: y = cos x + eps, eps ~ N(0, 1/5), x in [-5, 5]."""
    rng = np.random.default_rng(fk.SEED)
    x = np.sort(rng.uniform(-5, 5, n))
    return x[:, None], np.cos(x) + rng.normal(0, np.sqrt(noise_var), n)
