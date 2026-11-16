"""Mini-batch training of the hand-written network with any optimizer of opt_common, shared by the optimizer figures.

Every run starts from the same initial weights and sees the same batches in the same order, so a comparison
between optimizers (or between step sizes) changes only the optimizer.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import act_common as ac  # noqa: E402
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402

HIDDEN = (16,)
ACT = "relu"
BATCH = 32
EPOCHS = 100
BLOWN = 1e3  # a loss above this at the end of an epoch counts as divergence and stops the run


def train(make_opt, Xtr, ytr, Xva=None, yva=None, *, epochs=EPOCHS, batch=BATCH, hidden=HIDDEN, act=ACT):
    """Returns (train loss per epoch, validation loss per epoch or None, weights).

    Index 0 of the loss lists is the loss before the first step. make_opt() returns a fresh optimizer.
    A run that diverges is cut at the first epoch whose loss is not finite or above BLOWN; the rest is inf.
    """
    ytr = ytr.astype(float)
    rng = np.random.default_rng(fk.SEED)
    params = ac.init_params([Xtr.shape[1], *hidden, 1], act, rng)
    like = params
    w = ac._flat(params)
    opt = make_opt()

    def loss_of(v, X, y):
        return ac.loss_and_grads(ac._unflat(v, like), X, y, act)[0]

    tr = [loss_of(w, Xtr, ytr)]
    va = None if Xva is None else [loss_of(w, Xva, yva.astype(float))]
    n = len(ytr)
    for _ in range(epochs):
        order = rng.permutation(n)
        for s in range(0, n, batch):
            idx = order[s:s + batch]
            w = opt.step(w, lambda v: ac._flat(ac.loss_and_grads(ac._unflat(v, like), Xtr[idx], ytr[idx], act)[1]))
        tr.append(loss_of(w, Xtr, ytr))
        if va is not None:
            va.append(loss_of(w, Xva, yva.astype(float)))
        if not np.isfinite(tr[-1]) or tr[-1] > BLOWN:
            tr[-1] = np.inf
            if va is not None:
                va[-1] = np.inf
            break
    pad = epochs + 1 - len(tr)
    tr += [np.inf] * pad
    if va is not None:
        va += [np.inf] * (epochs + 1 - len(va))
    return np.array(tr), (None if va is None else np.array(va)), ac._unflat(w, like)


def predict_acc(params, X, y, act=ACT):
    return float(np.mean((ac.forward(params, X, act)[2] > 0).astype(int) == y))


def cv_val_loss(make_opt, X, y, folds=5, **kw):
    """Mean over stratified folds of the validation loss at the last epoch, and the fold curves (train, validation)."""
    from sklearn.model_selection import StratifiedKFold
    ends, curves = [], []
    for tr_i, va_i in StratifiedKFold(folds, shuffle=True, random_state=fk.SEED).split(X, y):
        tr, va, _ = train(make_opt, X[tr_i], y[tr_i], X[va_i], y[va_i], **kw)
        ends.append(va[-1])
        curves.append((tr, va))
    return float(np.mean(ends)), curves


def choose_lr(cls, X, y, grid, **kw):
    """Step size with the lowest mean cross-validation loss at the last epoch among the grid values."""
    scores = [cv_val_loss(lambda lr=lr: cls(lr), X, y, **kw)[0] for lr in grid]
    b = int(np.argmin(scores))
    return float(grid[b]), scores
