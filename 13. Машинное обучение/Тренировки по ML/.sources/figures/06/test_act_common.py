"""Behaviour of the activation functions and of the hand-written network.
Run: python -m pytest -q test_act_common.py"""
import numpy as np
import pytest
from sklearn.neural_network import MLPClassifier

import act_common as ac
import figkit as fk

NAMES = [n for n in ac.ACT if n != "relu"]  # ReLU has a kink; it gets its own check below


@pytest.mark.parametrize("name", NAMES)
def test_derivative_matches_finite_difference(name):
    f, df = ac.ACT[name]
    a = np.linspace(-4, 4, 41) + 0.013
    h = 1e-6
    np.testing.assert_allclose(df(a), (f(a + h) - f(a - h)) / (2 * h), rtol=1e-5, atol=1e-8)


def test_relu_derivative_is_zero_or_one():
    d = ac.ACT["relu"][1](np.array([-2.0, -0.1, 0.1, 3.0]))
    np.testing.assert_array_equal(d, [0, 0, 1, 1])


def test_sigmoid_derivative_never_exceeds_a_quarter_and_tanh_one():
    a = np.linspace(-8, 8, 2001)
    assert ac.ACT["sigmoid"][1](a).max() == pytest.approx(0.25, abs=1e-6)
    assert ac.ACT["tanh"][1](a).max() == pytest.approx(1.0, abs=1e-6)


def test_tanh_is_a_doubled_shifted_sigmoid():
    a = np.linspace(-3, 3, 13)
    np.testing.assert_allclose(ac.ACT["tanh"][0](a), 2 * ac.ACT["sigmoid"][0](2 * a) - 1, atol=1e-12)


def test_gelu_is_a_times_normal_cdf():
    from scipy.stats import norm
    a = np.linspace(-4, 4, 17)
    np.testing.assert_allclose(ac.ACT["gelu"][0](a), a * norm.cdf(a), atol=1e-12)


def test_gelu_is_close_to_the_sigmoid_approximation_of_the_paper():
    a = np.linspace(-4, 4, 161)
    assert np.max(np.abs(ac.ACT["gelu"][0](a) - a * ac.ACT["sigmoid"][0](1.702 * a))) < 0.03


@pytest.mark.parametrize("name", list(ac.ACT))
def test_backprop_matches_finite_differences(name):
    rng = np.random.default_rng(1)
    X = rng.normal(size=(12, 2)) + 0.05
    y = (rng.random(12) > 0.5).astype(float)
    params = ac.init_params([2, 5, 4, 1], name, rng)
    for layer in params:
        layer[1] = rng.normal(0, 0.3, layer[1].shape)
    loss, grads, _ = ac.loss_and_grads(params, X, y, name, l2=0.01)
    vec = ac._flat(params)
    g = ac._flat(grads)
    h = 1e-6
    num = np.empty_like(vec)
    for i in range(vec.size):
        e = np.zeros_like(vec)
        e[i] = h
        num[i] = (ac.loss_and_grads(ac._unflat(vec + e, params), X, y, name, 0.01)[0]
                  - ac.loss_and_grads(ac._unflat(vec - e, params), X, y, name, 0.01)[0]) / (2 * h)
    np.testing.assert_allclose(g, num, rtol=1e-4, atol=1e-7)


@pytest.mark.parametrize("name,sk", [("relu", "relu"), ("tanh", "tanh"), ("sigmoid", "logistic"),
                                      ("identity", "identity")])
def test_forward_equals_scikit_learn_with_the_same_weights(name, sk):
    X, y = fk.dataset("moons")
    m = MLPClassifier((6, 3), activation=sk, random_state=0)
    m.partial_fit(X, y, classes=[0, 1])
    params = [[W, b] for W, b in zip(m.coefs_, m.intercepts_)]
    logit = ac.forward(params, X, name)[2]
    np.testing.assert_allclose(1 / (1 + np.exp(-logit)), m.predict_proba(X)[:, 1], atol=1e-10)


def test_network_without_activation_draws_a_straight_boundary():
    X, y = fk.dataset("xor")
    m = ac.ActMLP((6,), "identity", n_init=1).fit(X, y)
    g = np.linspace(-1, 1, 5)
    P = np.array([[a, b] for a in g for b in g])
    d = m.decision_function(P)
    A = np.c_[P, np.ones(len(P))]
    assert np.max(np.abs(d - A @ np.linalg.lstsq(A, d, rcond=None)[0])) < 1e-6


def test_relu_network_solves_xor_and_linear_one_cannot():
    X, y = fk.dataset("xor")
    assert ac.ActMLP((8,), "relu", n_init=2).fit(X, y).score(X, y) > 0.9
    assert ac.ActMLP((8,), "identity", n_init=1).fit(X, y).score(X, y) < 0.7


def test_non_convergence_raises_instead_of_drawing(monkeypatch):
    monkeypatch.setattr(ac, "MAX_ITER", 5)
    X, y = fk.dataset("moons")
    with pytest.raises(RuntimeError, match="no convergence"):
        ac.ActMLP((4,), "tanh", n_init=1).fit(X, y)
