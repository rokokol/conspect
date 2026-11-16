"""Checks behind the numbers of the Shapley note: toy game by hand, XOR, linear model, tree rule on California Housing.

Prints the values quoted in the note; every assert is a claim the note makes.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402,F401
from shap_cal import fit  # noqa: E402
from shapley_lib import (coalitions, interventional_values, recursive_tree_value, shapley_by_orders,  # noqa: E402
                         shapley_from_values, tree_coalition_values)

np.set_printoptions(precision=4, suppress=True)

# Toy: f = 3 x1 + x2 x3, binary features, other features Bernoulli(1/2), x = (1, 1, 1)
rng_bg = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)


def f_toy(Z):
    return 3 * Z[:, 0] + Z[:, 1] * Z[:, 2]


x = np.array([[1.0, 1.0, 1.0]])
v = interventional_values(f_toy, x, rng_bg)[:, 0]
print("v by bitmask (S as set of 1-based features):")
for k, mask in enumerate(coalitions(3)):
    print({i + 1 for i in np.flatnonzero(mask)} or "{}", v[k])
phi = shapley_from_values(v[:, None], 3)[:, 0]
phi_orders = shapley_by_orders(v, 3)
print("phi coalitions", phi, "phi orders", phi_orders, "sum", phi.sum(), "f(x)-E f", v[-1] - v[0])
assert np.allclose(phi, phi_orders) and np.allclose(phi, [1.5, 0.375, 0.375])
assert np.isclose(phi.sum(), v[-1] - v[0])

# a null player: a fourth feature the model ignores
bg4 = np.array([[*r, d] for r in rng_bg for d in (0, 1)], float)
x4 = np.array([[1.0, 1.0, 1.0, 1.0]])
v4 = interventional_values(lambda Z: f_toy(Z[:, :3]), x4, bg4)[:, 0]
phi4 = shapley_from_values(v4[:, None], 4)[:, 0]
print("with a null player", phi4)
assert np.allclose(phi4, [1.5, 0.375, 0.375, 0.0])

# additivity: f = g + h, phi(f) = phi(g) + phi(h)
g = lambda Z: 3 * Z[:, 0]  # noqa: E731
h = lambda Z: Z[:, 1] * Z[:, 2]  # noqa: E731
pg = shapley_from_values(interventional_values(g, x, rng_bg), 3)[:, 0]
ph = shapley_from_values(interventional_values(h, x, rng_bg), 3)[:, 0]
print("additivity", pg, ph, pg + ph)
assert np.allclose(pg + ph, phi)

# XOR in +-1 coding: f = x1 x2, each feature alone says nothing
bgx = np.array([[a, b] for a in (-1, 1) for b in (-1, 1)], float)
fx = lambda Z: Z[:, 0] * Z[:, 1]  # noqa: E731
xx = np.array([[1.0, -1.0]])
vx = interventional_values(fx, xx, bgx)[:, 0]
print("XOR v", vx, "phi", shapley_from_values(vx[:, None], 2)[:, 0], "f(x)", fx(xx))

# linear model, independent features, large background: phi_i = w_i (x_i - E x_i)
rng = np.random.default_rng(0)
B = rng.normal(size=(400, 4)) * [1, 2, 0.5, 1] + [0, 1, -1, 3]
w = np.array([2.0, -1.0, 4.0, 0.5])
lin = lambda Z: Z @ w + 1.0  # noqa: E731
xl = np.array([[1.0, 3.0, -2.0, 4.0]])
vl = interventional_values(lin, xl, B)[:, 0]
pl = shapley_from_values(vl[:, None], 4)[:, 0]
print("linear", pl, "w(x-Ex)", w * (xl[0] - B.mean(0)))
assert np.allclose(pl, w * (xl[0] - B.mean(0)))

# tree rule on the real model
model, depth, X, y, Xtr, Xte, ytr, yte, names = fit()
sub = Xte[:30]
V = tree_coalition_values([e[0] for e in model.estimators_], model.learning_rate,
                          float(model.init_.constant_.ravel()[0]), sub)
pred = model.predict(sub)
assert np.allclose(V[-1], pred), "v(all) must be the prediction"
print("v(empty) =", V[0, 0], " mean prediction on train =", model.predict(Xtr).mean())
assert np.isclose(V[0, 0], model.predict(Xtr).mean())
est = model.estimators_[7][0]
for j in range(3):
    for k in (0, 5, 77, 200, 255):
        S = {i for i in range(8) if k >> i & 1}
        want = recursive_tree_value(est, sub[j], S)
        got = tree_coalition_values([est], 1.0, 0.0, sub[j:j + 1])[k, 0]
        assert np.isclose(want, got), (j, k, want, got)
phis = shapley_from_values(V, 8).T
assert np.allclose(phis.sum(1), pred - V[0, 0])
print("efficiency holds on 30 objects, depth", depth, "test R2", round(model.score(Xte, yte), 3))

# Row 0 of the data set is in the train part; correlated features make the two definitions of v(S) differ.
assert (np.abs(Xtr - X[0]).sum(1) == 0).any()
print("corr(Latitude, Longitude) on train", round(np.corrcoef(Xtr[:, 6], Xtr[:, 7])[0, 1], 3))
bg = Xtr[np.random.default_rng(0).choice(len(Xtr), 300, replace=False)]
vi = interventional_values(model.predict, X[:1], bg)[:, 0]
phi_i = shapley_from_values(vi[:, None], 8)[:, 0]
vp = tree_coalition_values([e[0] for e in model.estimators_], model.learning_rate,
                           float(model.init_.constant_.ravel()[0]), X[:1])[:, 0]
phi_p = shapley_from_values(vp[:, None], 8)[:, 0]
print("row 0: E f path-dependent", round(vp[0], 3), "interventional (300 train rows)", round(vi[0], 3))
for n, a, b in zip(names, phi_p, phi_i):
    print(f"{n:11s} path-dependent {a:+.3f}  interventional {b:+.3f}")
