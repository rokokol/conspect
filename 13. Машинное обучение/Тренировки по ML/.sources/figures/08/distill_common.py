"""Distillation of a classifier into a small network, shared by the figures of topic 8.

The student is a dense network with K logits z and the loss of Hinton et al. (2015):

    L = alpha * CE(y, softmax(z)) + (1 - alpha) * T^2 * CE(p_T, softmax(z / T)),

p_T = softmax(v / T) are the teacher's soft labels from its logits v. The hard term uses T = 1.
The gradient with respect to the logits is alpha * (q_1 - y) + (1 - alpha) * T * (q_T - p_T):
the factor T^2 turns the 1/T of the soft term into T.
Checked in test_distill_common.py against finite differences.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.special import logsumexp, softmax
from sklearn.ensemble import GradientBoostingClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "06"))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402


def teacher_logits(model, X):
    """Logits v of a fitted GradientBoostingClassifier: log-odds split as (-d/2, d/2) for two classes.

    softmax of (-d/2, d/2) at temperature T is the sigmoid of d / T, so the binary case is the K = 2 case.
    """
    d = model.decision_function(X)
    return np.c_[-d / 2, d / 2] if d.ndim == 1 else d


def forward(params, X, act):
    A = [X]
    Z = []
    f = ac.ACT[act][0]
    for W, b in params[:-1]:
        Z.append(A[-1] @ W + b)
        A.append(f(Z[-1]))
    W, b = params[-1]
    return Z, A, A[-1] @ W + b


def loss_and_grads(params, X, Y, P_soft, T, alpha, act, l2=0.0):
    """Mixed loss (mean over objects) and its gradient by backprop.

    Y is one-hot, P_soft are the teacher's probabilities at temperature T (rows sum to 1).
    alpha is a number or a column of per-object weights: 0 for an object without a true label.
    """
    df = ac.ACT[act][1]
    Z, A, z = forward(params, X, act)
    n = len(X)
    alpha = np.broadcast_to(np.reshape(np.asarray(alpha, float), (-1, 1)), (n, 1))
    logq1 = z - logsumexp(z, axis=1, keepdims=True)
    logqT = z / T - logsumexp(z / T, axis=1, keepdims=True)
    loss = np.sum(alpha * -np.sum(Y * logq1, 1, keepdims=True)) / n
    loss += T**2 * np.sum((1 - alpha) * -np.sum(P_soft * logqT, 1, keepdims=True)) / n
    loss += 0.5 * l2 * sum(np.sum(W * W) for W, _ in params)
    dz = (alpha * (np.exp(logq1) - Y) + (1 - alpha) * T * (np.exp(logqT) - P_soft)) / n
    grads = [None] * len(params)
    W, b = params[-1]
    grads[-1] = [A[-1].T @ dz + l2 * W, dz.sum(0)]
    dA = dz @ W.T
    for l in range(len(params) - 2, -1, -1):
        dZ = dA * df(Z[l])
        W, b = params[l]
        grads[l] = [A[l].T @ dZ + l2 * W, dZ.sum(0)]
        dA = dZ @ W.T
    return loss, grads


class Student:
    """K-class network trained on the mixed loss; hard labels only when alpha = 1.

    fit(X, y, V=None): y are the true labels; V are the teacher's logits (needed when alpha < 1).
    Full-batch Adam until the loss stops falling; raises if it has not stopped by max_iter,
    the analogue of scikit-learn's ConvergenceWarning.
    """

    def __init__(self, hidden=(8,), T=1.0, alpha=1.0, act="tanh", l2=1e-4, lr=0.02, tol=1e-6, patience=50,
                 max_iter=20000, seed=fk.SEED):
        self.hidden, self.T, self.alpha, self.act, self.l2 = tuple(hidden), T, alpha, act, l2
        self.lr, self.tol, self.patience, self.max_iter, self.seed = lr, tol, patience, max_iter, seed

    def fit(self, X, y, V=None, labeled=None):
        """labeled: boolean mask of the objects whose y is a true label; the others (a transfer set of
        unlabeled objects) get the soft term only, whatever alpha is. Their y entries are ignored."""
        labeled = np.ones(len(X), bool) if labeled is None else np.asarray(labeled, bool)
        self.classes_ = np.unique(y[labeled])
        K = len(self.classes_)
        Y = (y[:, None] == self.classes_[None, :]).astype(float) * labeled[:, None]
        P = softmax(V / self.T, axis=1) if V is not None and (self.alpha < 1 or not labeled.all()) else Y
        alpha = self.alpha * labeled if V is not None else 1.0
        rng = np.random.default_rng(self.seed)
        params = ac.init_params([X.shape[1], *self.hidden, K], self.act, rng)
        like = params
        opt = oc.Adam(self.lr)
        w = ac._flat(params)

        def lg(v):
            return loss_and_grads(ac._unflat(v, like), X, Y, P, self.T, alpha, self.act, self.l2)

        best, since = np.inf, 0
        for _ in range(self.max_iter):
            loss = lg(w)[0]
            if loss < best - self.tol:
                best, since = loss, 0
            else:
                since += 1
                if since >= self.patience:
                    self.params_ = ac._unflat(w, like)
                    return self
            w = opt.step(w, lambda v: ac._flat(lg(v)[1]))
        raise RuntimeError(f"student {self.hidden}: no convergence in {self.max_iter} iterations")

    def decision_function(self, X):
        return forward(self.params_, X, self.act)[2]

    def predict_proba(self, X):
        return softmax(self.decision_function(X), axis=1)

    def predict(self, X):
        return self.classes_[np.argmax(self.decision_function(X), axis=1)]

    def score(self, X, y):
        return float(np.mean(self.predict(X) == y))


TEACHER_GRID = [dict(n_estimators=n, max_depth=d) for n in (20, 50, 200) for d in (1, 2, 3)]
FOLDS = 5


def _folds(X, y):
    from sklearn.model_selection import StratifiedKFold
    return list(StratifiedKFold(FOLDS, shuffle=True, random_state=fk.SEED).split(X, y))


def choose_teacher(Xtr, ytr):
    """Hyperparameters of the gradient-boosting teacher by cross-validation on the train part."""
    cv = [np.mean([GradientBoostingClassifier(**p, random_state=fk.SEED).fit(Xtr[a], ytr[a]).score(Xtr[b], ytr[b])
                   for a, b in _folds(Xtr, ytr)]) for p in TEACHER_GRID]
    return TEACHER_GRID[int(np.argmax(cv))]


def fit_teacher(params, X, y):
    return GradientBoostingClassifier(**params, random_state=fk.SEED).fit(X, y)


def fit_student(teacher, X, y, **kw):
    """Student on the logits of a fitted teacher for the same objects; alpha = 1 ignores the teacher."""
    return Student(**kw).fit(X, y, teacher_logits(teacher, X))


def cv_accuracy(params, Xtr, ytr, **kw):
    """Mean validation accuracy of a student over the folds of the train part.

    The teacher is refitted on each fold's own train part, so no fold's labels reach its own validation.
    """
    scores = []
    for a, b in _folds(Xtr, ytr):
        t = fit_teacher(params, Xtr[a], ytr[a])
        scores.append(fit_student(t, Xtr[a], ytr[a], **kw).score(Xtr[b], ytr[b]))
    return float(np.mean(scores))


def choose_student(params, Xtr, ytr, hidden, temps, alphas):
    """Grid over (T, alpha) by CV; the hard-label student (alpha = 1) is the first cell and wins ties.

    Returns (best (T, alpha), {(T, alpha): CV accuracy}).
    """
    grid = {(1.0, 1.0): cv_accuracy(params, Xtr, ytr, hidden=hidden, T=1.0, alpha=1.0)}
    for T in temps:
        for a in alphas:
            grid[(T, a)] = cv_accuracy(params, Xtr, ytr, hidden=hidden, T=T, alpha=a)
    best = max(grid, key=grid.get)
    return best, grid
