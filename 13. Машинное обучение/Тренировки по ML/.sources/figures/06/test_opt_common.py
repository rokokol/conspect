"""Behaviour of the optimizers: each rule is checked against a property it must have.
Run: python -m pytest -q test_opt_common.py"""
import numpy as np
import pytest

import opt_common as oc

W0 = np.array([-2.6, 1.6])


def test_momentum_with_zero_rho_is_sgd():
    a = oc.run(oc.SGD(0.05), W0, oc.Valley.grad, 20)
    b = oc.run(oc.Momentum(0.05, rho=0.0), W0, oc.Valley.grad, 20)
    np.testing.assert_allclose(a, b, atol=1e-15)


def test_momentum_is_the_heavy_ball_recurrence():
    # v-form of the slide is the same as w_{t+1} = w_t - eta g_t + rho (w_t - w_{t-1})
    eta, rho = 0.03, 0.8
    path = oc.run(oc.Momentum(eta, rho), W0, oc.Valley.grad, 30)
    for t in range(1, 30):
        expect = path[t] - eta * oc.Valley.grad(path[t]) + rho * (path[t] - path[t - 1])
        np.testing.assert_allclose(path[t + 1], expect, atol=1e-12)


def test_nesterov_looks_ahead_at_w_minus_eta_rho_v():
    # an independent write-up of the look-ahead form from the CS231n notes: v' = mu v' - eta g(x + mu v'), x += v'
    eta, mu = 0.03, 0.8
    x, vp = W0.copy(), np.zeros(2)
    ref = [x.copy()]
    for _ in range(30):
        vp = mu * vp - eta * oc.Valley.grad(x + mu * vp)
        x = x + vp
        ref.append(x.copy())
    got = oc.run(oc.Nesterov(eta, mu), W0, oc.Valley.grad, 30)
    np.testing.assert_allclose(got, np.array(ref), atol=1e-12)


def test_nesterov_differs_from_momentum_once_inertia_exists():
    a = oc.run(oc.Momentum(0.03, 0.8), W0, oc.Valley.grad, 5)
    b = oc.run(oc.Nesterov(0.03, 0.8), W0, oc.Valley.grad, 5)
    assert np.allclose(a[:2], b[:2]) and not np.allclose(a[2:], b[2:])


def test_adam_first_step_has_length_lr_per_coordinate():
    # with bias correction m_hat = g and s_hat = g^2, so the step is lr * sign(g)
    p = oc.run(oc.Adam(0.1), W0, oc.Valley.grad, 1)
    np.testing.assert_allclose(W0 - p[1], 0.1 * np.sign(oc.Valley.grad(W0)), atol=1e-6)


def test_rmsprop_on_constant_gradient_steps_lr_per_coordinate():
    g = np.array([3.0, -0.01])
    p = oc.run(oc.RMSProp(0.01), np.zeros(2), lambda w: g, 400)
    step = p[-1] - p[-2]
    np.testing.assert_allclose(step, -0.01 * np.sign(g), rtol=1e-3)


def test_adagrad_step_shrinks_on_constant_gradient():
    g = np.array([1.0, 1.0])
    p = oc.run(oc.Adagrad(0.5), np.zeros(2), lambda w: g, 10)
    steps = np.abs(np.diff(p[:, 0]))
    assert np.all(np.diff(steps) < 0)
    np.testing.assert_allclose(steps[3], 0.5 / 2.0, rtol=1e-6)  # cache = 4 after four equal gradients


@pytest.mark.parametrize("name,kw", [("SGD", {"lr": 0.05}), ("Momentum", {"lr": 0.02}),
                                      ("Nesterov", {"lr": 0.02}), ("Adagrad", {"lr": 1.0}),
                                      ("RMSProp", {"lr": 0.02}), ("Adam", {"lr": 0.1})])
def test_every_optimizer_descends_the_valley(name, kw):
    p = oc.run(oc.OPTIMIZERS[name](**kw), W0, oc.Valley.grad, 400)
    assert oc.Valley.f(p[-1]) < 1e-2 * oc.Valley.f(W0)


def test_rosenbrock_gradient_matches_finite_differences():
    p = np.array([-0.7, 1.3])
    h = 1e-6
    num = np.array([(oc.Rosenbrock.f(p + h * e) - oc.Rosenbrock.f(p - h * e)) / (2 * h) for e in np.eye(2)])
    np.testing.assert_allclose(oc.Rosenbrock.grad(p), num, rtol=1e-5)
