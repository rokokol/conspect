"""Numbers for the note on AdaBoost: margins and weights e^{-M} of five objects after every round, and two checks of the derivation.

Check 1: the weights of the loop below are the weights of the exponential loss, up to one factor per round.
Check 2: sklearn's estimator weight for two classes is twice rho = 1/2 ln((1 - eps) / eps).
Check 3: right after the update the weighted error of the stump just added is exactly 1/2.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from boost_common import AdaBoostScratch, toy_quadrant  # noqa: E402
from sklearn.ensemble import AdaBoostClassifier  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

import figkit as fk  # noqa: E402

X, y01 = toy_quadrant()
y = 2 * y01 - 1
ROUNDS = 3
ada = AdaBoostScratch(depth=1).fit(X, y01, ROUNDS)

shown = [0, 2, 3, 9, 16]
print("object, class, M after t = 0..3, exp(-M) after t = 0..2 (the weight before round t + 1)")
for i in shown:
    margins = [float(y[i] * ada.score_at(X[i:i + 1], t)[0]) if t else 0.0 for t in range(ROUNDS + 1)]
    print(i, int(y[i]), [round(m, 2) for m in margins], [round(float(np.exp(-m)), 2) for m in margins[:ROUNDS]])

for t in range(ROUNDS):
    exp_w = np.exp(-y * ada.score_at(X, t))
    exp_w = exp_w / exp_w.sum()
    assert np.allclose(exp_w, ada.weights[t]), t
print("check 1 passed: normalised exp(-M) equals the loop weights in every round")

sk = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=fk.SEED), n_estimators=ROUNDS,
                        random_state=fk.SEED).fit(X, y01)
print("sklearn estimator_weights_", np.round(sk.estimator_weights_, 3), "2 * rho", np.round(2 * np.array(ada.rho), 3))
print("sklearn estimator_errors_ ", np.round(sk.estimator_errors_, 3), "eps", np.round(ada.eps, 3))

eps = np.array(ada.eps)
bound = float(np.prod(2 * np.sqrt(eps * (1 - eps))))
mean_loss = float(np.mean(np.exp(-y * ada.score_at(X))))
print("check 4: mean exponential loss", round(mean_loss, 6), "= product of 2 sqrt(eps (1 - eps))", round(bound, 6))
assert np.isclose(mean_loss, bound)
print("train error", float(np.mean(np.sign(ada.score_at(X)) != y)), "<= mean exponential loss")

for t in range(ROUNDS):
    pred = ada.stumps[t].predict(X)
    w_next = ada.weights[t] * np.exp(-ada.rho[t] * y * pred)
    w_next /= w_next.sum()
    print("round", t + 1, "weighted error of the stump on the next weights:", round(float(w_next[pred != y].sum()), 6))
