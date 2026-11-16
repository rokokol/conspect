"""Activation functions and a small hand-written network with any of them, shared by the activation figures of topic 6.

scikit-learn's MLPClassifier knows identity, logistic, tanh and ReLU only, and the
lecture also names Leaky ReLU, ELU, GELU and SiLU, so the network is written out:
a stack of dense layers, a logit output, binary cross-entropy, full-batch Adam.
It is checked in test_act_common.py against finite differences and against
scikit-learn on the activations both know.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.special import erf, expit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402

SQRT2PI = np.sqrt(2 * np.pi)


def _sigmoid(a):
    return expit(a)


def _gelu(a):
    return a * 0.5 * (1 + erf(a / np.sqrt(2)))


def _dgelu(a):
    return 0.5 * (1 + erf(a / np.sqrt(2))) + a * np.exp(-a * a / 2) / SQRT2PI


def _elu(a):
    return np.where(a > 0, a, np.expm1(np.minimum(a, 0)))


def _delu(a):
    return np.where(a > 0, 1.0, np.exp(np.minimum(a, 0)))


LEAK = 0.01

# name -> (function, derivative); the derivative of ReLU at 0 is taken as 0, as in the lecture's "0 or 1"
ACT = {
    "identity": (lambda a: a, lambda a: np.ones_like(a)),
    "sigmoid": (_sigmoid, lambda a: _sigmoid(a) * (1 - _sigmoid(a))),
    "tanh": (np.tanh, lambda a: 1 - np.tanh(a) ** 2),
    "relu": (lambda a: np.maximum(a, 0), lambda a: (a > 0).astype(float)),
    "leaky_relu": (lambda a: np.where(a > 0, a, LEAK * a), lambda a: np.where(a > 0, 1.0, LEAK)),
    "elu": (_elu, _delu),
    "gelu": (_gelu, _dgelu),
    "silu": (lambda a: a * _sigmoid(a), lambda a: _sigmoid(a) * (1 + a * (1 - _sigmoid(a)))),
}

LABEL = {"identity": "без активации", "sigmoid": "sigmoid", "tanh": "tanh", "relu": "ReLU",
         "leaky_relu": "Leaky ReLU", "elu": "ELU", "gelu": "GELU", "silu": "SiLU"}

# Rectifier-like units get He scaling, saturating ones Glorot: the usual pairing, not a tuned choice
HE = {"relu", "leaky_relu", "elu", "gelu", "silu"}


def init_params(sizes, act, rng):
    """Weights of a stack of dense layers; sizes = [d_in, h1, ..., hL, 1]."""
    params = []
    for fan_in, fan_out in zip(sizes[:-1], sizes[1:]):
        var = 2.0 / fan_in if act in HE else 2.0 / (fan_in + fan_out)
        params.append([rng.normal(0, np.sqrt(var), (fan_in, fan_out)), np.zeros(fan_out)])
    return params


def forward(params, X, act):
    """Caches (Z_l, A_l) of every hidden layer and the output logit."""
    f = ACT[act][0]
    A = [X]
    Z = []
    for W, b in params[:-1]:
        Z.append(A[-1] @ W + b)
        A.append(f(Z[-1]))
    W, b = params[-1]
    return Z, A, (A[-1] @ W + b)[:, 0]


def loss_and_grads(params, X, y, act, l2=0.0):
    """Mean binary cross-entropy on the logit (+ L2 on weights) and its gradient by backprop.

    Also returns the gradient with respect to the activations A_l of every hidden layer
    (list index 0 is the first hidden layer), the quantity that vanishes or explodes.
    """
    df = ACT[act][1]
    Z, A, z = forward(params, X, act)
    n = len(y)
    loss = np.mean(np.logaddexp(0, z) - y * z)
    loss += 0.5 * l2 * sum(np.sum(W * W) for W, _ in params)
    dz = (_sigmoid(z) - y) / n
    grads = [None] * len(params)
    dA_all = [None] * (len(params) - 1)
    W, b = params[-1]
    grads[-1] = [A[-1].T @ dz[:, None] + l2 * W, np.array([dz.sum()])]
    dA = dz[:, None] @ W.T
    for l in range(len(params) - 2, -1, -1):
        dA_all[l] = dA
        dZ = dA * df(Z[l])
        W, b = params[l]
        grads[l] = [A[l].T @ dZ + l2 * W, dZ.sum(0)]
        dA = dZ @ W.T
    return loss, grads, dA_all


def _flat(params):
    return np.concatenate([np.ravel(p) for layer in params for p in layer])


def _unflat(vec, like):
    out, i = [], 0
    for layer in like:
        new = []
        for p in layer:
            new.append(vec[i:i + p.size].reshape(p.shape))
            i += p.size
        out.append(new)
    return out


MAX_ITER = 50000


class ActMLP:
    """Binary classifier: dense layers with one activation, full-batch Adam until the loss stops falling.

    Keeps the best of n_init random starts by training loss (the test part is never looked at).
    Raises if a start has not stopped by max_iter, the analogue of scikit-learn's ConvergenceWarning.
    """

    def __init__(self, hidden, act="relu", n_init=3, l2=1e-4, lr=0.01, tol=1e-6, patience=50, seed=fk.SEED):
        self.hidden, self.act, self.n_init, self.l2 = tuple(hidden), act, n_init, l2
        self.lr, self.tol, self.patience, self.seed = lr, tol, patience, seed

    def _fit_one(self, X, y, rng):
        params = init_params([X.shape[1], *self.hidden, 1], self.act, rng)
        like = params
        opt = oc.Adam(self.lr)
        w = _flat(params)

        def grad(v):
            return _flat(loss_and_grads(_unflat(v, like), X, y, self.act, self.l2)[1])

        best, since = np.inf, 0
        for it in range(MAX_ITER):
            loss = loss_and_grads(_unflat(w, like), X, y, self.act, self.l2)[0]
            if loss < best - self.tol:
                best, since = loss, 0
            else:
                since += 1
                if since >= self.patience:
                    return _unflat(w, like), loss
            w = opt.step(w, grad)
        raise RuntimeError(f"{self.act} {self.hidden}: no convergence in {MAX_ITER} iterations")

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        y01 = (y == self.classes_[1]).astype(float)
        rng = np.random.default_rng(self.seed)
        fits = [self._fit_one(X, y01, rng) for _ in range(self.n_init)]
        self.params_, self.loss_ = min(fits, key=lambda t: t[1])
        return self

    def decision_function(self, X):
        return forward(self.params_, X, self.act)[2]

    def predict_proba(self, X):
        p = _sigmoid(self.decision_function(X))
        return np.c_[1 - p, p]

    def predict(self, X):
        return self.classes_[(self.decision_function(X) > 0).astype(int)]

    def score(self, X, y):
        return float(np.mean(self.predict(X) == y))

    def get_params(self, deep=False):
        return dict(hidden=self.hidden, act=self.act, n_init=self.n_init, l2=self.l2, lr=self.lr,
                    tol=self.tol, patience=self.patience, seed=self.seed)

    def clone(self, **kw):
        return ActMLP(**{**self.get_params(), **kw})


def cv_score(make, X, y, folds=5):
    """Mean validation accuracy over stratified folds of the train part; make() returns an unfitted model."""
    from sklearn.model_selection import StratifiedKFold
    scores = []
    for tr, va in StratifiedKFold(folds, shuffle=True, random_state=fk.SEED).split(X, y):
        scores.append(make().fit(X[tr], y[tr]).score(X[va], y[va]))
    return float(np.mean(scores))
