"""Helpers shared by the neural-network figures of topic 6."""
import sys
from pathlib import Path

import numpy as np
from sklearn.neural_network import MLPClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

MAX_ITER = 50000


def _train_size():
    X, y = fk.dataset("moons")
    return len(fk.split(X, y)[0])


# Every course data set has 300 points, so every train part has the same size.
N_TRAIN = _train_size()


def mlp(hidden, activation="relu", seed=fk.SEED, alpha=1e-4, n=N_TRAIN):
    """Full-batch gradient training (Adam steps on the whole train set) until the loss stops falling.

    L-BFGS was tried first: with ReLU its line search stops in a kink after a
    few dozen iterations (status ABNORMAL) or halts on a flat region with half
    the loss left, so a ReLU picture would show the solver, not the model.
    Full batch keeps the run deterministic and free of mini-batch noise; n is
    the number of points the model will be fitted on.
    """
    return MLPClassifier(hidden_layer_sizes=tuple(hidden), activation=activation, solver="adam",
                         batch_size=n, learning_rate_init=0.01, alpha=alpha, max_iter=MAX_ITER,
                         tol=1e-7, n_iter_no_change=50, random_state=seed)


def best_of(make, X, y, n_init=10):
    """Fit n_init random starts and keep the lowest training loss.

    Restarting from several initial weights and keeping the best training
    optimum uses only training data; the test part is not looked at.
    """
    best = None
    for s in range(n_init):
        m = make(s).fit(X, y)
        if best is None or m.loss_ < best.loss_:
            best = m
    return best


class BestOf:
    """A classifier that fits best_of on its own data, for fk.model_grid and cross-validation loops."""

    def __init__(self, hidden, activation="relu", n_init=5):
        self.hidden, self.activation, self.n_init = hidden, activation, n_init

    def fit(self, X, y):
        self.model_ = best_of(lambda s: mlp(self.hidden, self.activation, seed=s, n=len(X)), X, y,
                              self.n_init)
        self.classes_ = self.model_.classes_
        return self

    def predict(self, X):
        return self.model_.predict(X)

    def predict_proba(self, X):
        return self.model_.predict_proba(X)

    def score(self, X, y):
        return self.model_.score(X, y)


def cv_score(make, X, y, folds=5):
    """Mean accuracy over stratified folds of the train part; make() returns an unfitted model."""
    from sklearn.model_selection import StratifiedKFold
    scores = []
    for tr, va in StratifiedKFold(folds, shuffle=True, random_state=fk.SEED).split(X, y):
        scores.append(make().fit(X[tr], y[tr]).score(X[va], y[va]))
    return float(np.mean(scores))


# A neuron is not a class: its line is neutral ink, told apart by dash style and a label.
NEURON_LS = ["--", ":", "-."]
NEURON_C = fk.TEXT


def neuron_label(ax, x, y, j):
    ax.text(x, y, f"$h_{j + 1}$", fontsize=10, color=NEURON_C, ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def hidden_lines(ax, model, box, only=None):
    """Zero lines w_j^T x + b_j = 0 of every first-layer neuron inside box = (x0, x1, y0, y1), labelled h1, h2, ...

    The label sits near the end of the visible segment; a line that misses the box is not drawn.
    only restricts the drawing to one neuron index.
    """
    W, b = model.coefs_[0], model.intercepts_[0]
    x0, x1, y0, y1 = box
    for j in range(W.shape[1]):
        if only is not None and j != only:
            continue
        w1, w2 = W[:, j]
        # Parametrise the line and keep the part inside the box.
        if abs(w2) >= abs(w1):
            xs = np.linspace(x0, x1, 2001)
            ys = -(w1 * xs + b[j]) / w2
        else:
            ys = np.linspace(y0, y1, 2001)
            xs = -(w2 * ys + b[j]) / w1
        keep = (xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1)
        if keep.sum() < 2:
            continue
        xs, ys = xs[keep], ys[keep]
        ax.plot(xs, ys, color=NEURON_C, lw=1.3, ls=NEURON_LS[j % len(NEURON_LS)], zorder=4)
        k = int(0.92 * (len(xs) - 1))
        neuron_label(ax, xs[k], ys[k], j)


def hidden_activations(model, X):
    """Output of the first hidden layer for points X."""
    Z = X @ model.coefs_[0] + model.intercepts_[0]
    return ACT[model.activation](Z)


def logit(model, X):
    """Pre-sigmoid output of a one-hidden-layer binary network, computed without saturating probabilities."""
    return hidden_activations(model, X) @ model.coefs_[1][:, 0] + model.intercepts_[1][0]


def crossed_cells(model, box, steps=1200):
    """Number of cells of the first-layer line arrangement that the decision boundary passes through.

    A boundary pixel is one where the logit changes sign towards its right
    neighbour; its cell is the on/off pattern of the first-layer neurons.
    """
    x0, x1, y0, y1 = box
    xx, yy = np.meshgrid(np.linspace(x0, x1, steps), np.linspace(y0, y1, steps))
    P = np.c_[xx.ravel(), yy.ravel()]
    s = np.sign(logit(model, P)).reshape(xx.shape)
    edge = (s[:, :-1] != s[:, 1:]).ravel()
    pattern = ((P @ model.coefs_[0] + model.intercepts_[0]) > 0).astype(int) @ (2 ** np.arange(
        model.coefs_[0].shape[1]))
    return len(np.unique(pattern.reshape(xx.shape)[:, :-1].ravel()[edge]))


ACT = {"identity": lambda z: z, "tanh": np.tanh, "relu": lambda z: np.maximum(z, 0),
       "logistic": lambda z: 1 / (1 + np.exp(-z))}
