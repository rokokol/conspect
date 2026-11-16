"""Behaviour of the distillation loss. Run: python -m pytest -q test_distill_common.py"""
import numpy as np
from scipy.special import softmax
from sklearn.ensemble import GradientBoostingClassifier

import distill_common as dc
import figkit as fk  # noqa: E402
import act_common as ac  # noqa: E402

rng = np.random.default_rng(1)
X = rng.normal(size=(12, 2))
Y = np.eye(3)[rng.integers(0, 3, 12)]
V = rng.normal(size=(12, 3))


def _params(act="tanh"):
    return ac.init_params([2, 5, 3], act, np.random.default_rng(2))


def test_gradient_matches_finite_differences():
    per_row = np.where(np.arange(12) < 6, 0.4, 0.0)  # the last rows have no true label
    for T, alpha in [(1.0, 0.0), (4.0, 0.3), (2.0, 1.0), (3.0, per_row)]:
        P = softmax(V / T, axis=1)
        p = _params()
        w = ac._flat(p)
        _, g = dc.loss_and_grads(p, X, Y, P, T, alpha, "tanh")
        g = ac._flat(g)
        num = np.zeros_like(w)
        for i in range(len(w)):
            e = np.zeros_like(w)
            e[i] = 1e-6
            lp = dc.loss_and_grads(ac._unflat(w + e, p), X, Y, P, T, alpha, "tanh")[0]
            lm = dc.loss_and_grads(ac._unflat(w - e, p), X, Y, P, T, alpha, "tanh")[0]
            num[i] = (lp - lm) / 2e-6
        assert np.allclose(g, num, atol=1e-6), (T, alpha)


def test_soft_gradient_at_high_temperature_is_logit_difference_independent_of_T():
    # T^2-scaled soft term: d/dz = T (q - p) -> (z - v) / N for zero-mean logits and T >> |logits|
    n, K = 1, 4
    z = np.array([[0.6, -0.2, -0.5, 0.1]])
    v = np.array([[-0.3, 0.4, 0.2, -0.3]])
    z, v = z - z.mean(), v - v.mean()
    for T in (50.0, 200.0):
        q, p = softmax(z / T, axis=1), softmax(v / T, axis=1)
        assert np.allclose(T * (q - p), (z - v) / K, atol=2e-3)


def test_alpha_one_ignores_the_teacher():
    a = dc.Student(hidden=(4,), alpha=1.0).fit(*_toy())
    b = dc.Student(hidden=(4,), alpha=1.0, T=9.0).fit(*_toy(), V=np.zeros((60, 2)))
    X0 = _toy()[0]
    assert np.allclose(a.decision_function(X0), b.decision_function(X0))


def test_unlabeled_objects_use_the_soft_term_only_and_their_y_is_ignored():
    X0, y0 = _toy()
    t = GradientBoostingClassifier(n_estimators=20, random_state=0).fit(X0, y0)
    V0 = dc.teacher_logits(t, X0)
    mask = np.arange(len(X0)) < 30
    junk = np.where(mask, y0, 1 - y0)
    a = dc.Student(hidden=(4,), T=2.0, alpha=0.5).fit(X0, y0, V0, labeled=mask)
    b = dc.Student(hidden=(4,), T=2.0, alpha=0.5).fit(X0, junk, V0, labeled=mask)
    assert np.allclose(a.decision_function(X0), b.decision_function(X0))


def test_binary_teacher_logits_give_the_sigmoid_at_temperature():
    X0, y0 = _toy()
    t = GradientBoostingClassifier(n_estimators=20, random_state=0).fit(X0, y0)
    v = dc.teacher_logits(t, X0)
    for T in (1.0, 3.0):
        assert np.allclose(softmax(v / T, axis=1)[:, 1], 1 / (1 + np.exp(-t.decision_function(X0) / T)))
    assert np.allclose(softmax(v, axis=1), t.predict_proba(X0))


def test_student_learns_the_teacher_it_is_given():
    X0, y0 = _toy()
    t = GradientBoostingClassifier(n_estimators=30, random_state=0).fit(X0, y0)
    s = dc.Student(hidden=(8,), T=2.0, alpha=0.0).fit(X0, y0, dc.teacher_logits(t, X0))
    assert np.mean(s.predict(X0) == t.predict(X0)) > 0.9


def test_cv_refits_the_teacher_on_every_fold_so_validation_labels_never_reach_it(monkeypatch):
    X0, y0 = _toy()
    calls = []
    real = dc.fit_teacher
    monkeypatch.setattr(dc, "fit_teacher", lambda p, X, y: calls.append(len(X)) or real(p, X, y))
    dc.cv_accuracy(dict(n_estimators=5, max_depth=1), X0, y0, hidden=(2,), alpha=1.0)
    assert len(calls) == dc.FOLDS and max(calls) < len(X0)


def test_the_hard_label_student_wins_a_tie(monkeypatch):
    X0, y0 = _toy()
    monkeypatch.setattr(dc, "cv_accuracy", lambda *a, **k: 0.9)
    best, grid = dc.choose_student({}, X0, y0, (2,), (1.0, 4.0), (0.0, 0.5))
    assert best == (1.0, 1.0) and len(grid) == 1 + 2 * 2


def _toy():
    Xa, ya = fk.dataset("moons")
    return Xa[:60], ya[:60]
