"""Behaviour of mini-batch training. Run: python -m pytest -q test_opt_nn.py"""
import numpy as np

import opt_nn as on  # puts figkit on the path
import figkit as fk  # noqa: E402
import opt_common as oc  # noqa: E402

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)


def test_zero_step_leaves_the_loss_unchanged():
    tr, va, _ = on.train(lambda: oc.SGD(0.0), Xtr, ytr, Xte[:30], yte[:30], epochs=3)
    assert np.ptp(tr) < 1e-12 and np.ptp(va) < 1e-12


def test_sgd_with_a_sane_step_lowers_the_train_loss():
    tr, _, _ = on.train(lambda: oc.SGD(0.05), Xtr, ytr, epochs=30)
    assert tr[-1] < 0.6 * tr[0]


def test_a_huge_step_is_cut_and_marked_infinite():
    tr, _, _ = on.train(lambda: oc.SGD(1e4), Xtr, ytr, epochs=10)
    assert np.isinf(tr[-1])


def test_runs_are_reproducible_and_start_from_the_same_weights():
    a = on.train(lambda: oc.SGD(0.05), Xtr, ytr, epochs=5)[0]
    b = on.train(lambda: oc.Adam(0.01), Xtr, ytr, epochs=5)[0]
    c = on.train(lambda: oc.SGD(0.05), Xtr, ytr, epochs=5)[0]
    np.testing.assert_array_equal(a, c)
    assert a[0] == b[0]


def test_full_batch_momentum_zero_equals_sgd():
    a = on.train(lambda: oc.SGD(0.05), Xtr, ytr, epochs=4)[0]
    b = on.train(lambda: oc.Momentum(0.05, rho=0.0), Xtr, ytr, epochs=4)[0]
    np.testing.assert_allclose(a, b, atol=1e-12)


def test_choose_lr_takes_the_validation_minimum_not_the_largest_step():
    lr, scores = on.choose_lr(oc.SGD, Xtr, ytr, [1e-4, 0.05, 1e4], epochs=20)
    assert lr == 0.05 and np.isinf(scores[2])
