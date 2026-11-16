"""Numerical check of every gradient derived in the note "Обратное распространение ошибки".

1. Slide 29: the node-by-node backward pass against central finite differences
   and against the closed form sigma(s)(1 - sigma(s)) times the other input.
2. One-hidden-layer sigmoid network with BCE: the matrix formulas against finite
   differences, at random weights and at weights fitted by scikit-learn, whose
   predict_proba must equal the hand-written forward pass.
3. Falsification: each deliberate defect in mlp_backward must fail the same check.
Draws backprop-gradcheck.png: analytic against numeric for every parameter.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.neural_network import MLPClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import backprop_common as bc  # noqa: E402

TOL = 1e-7

# 1. Slide 29.
v = dict(bc.SLIDE29)
n = bc.graph_forward(v)
g = bc.graph_backward(v, n)
slide_forward = {"m0": -2.00, "m1": 6.00, "s0": 4.00, "s": 1.00, "neg": -1.00, "e": 0.37, "q": 1.37,
                 "out": 0.73}
slide_backward = {"out": 1.00, "q": -0.53, "e": -0.53, "neg": -0.20, "s": 0.20, "s0": 0.20, "w2": 0.20,
                  "x0": -0.20, "w0": 0.40, "x1": -0.40, "w1": -0.60}
for k, val in slide_forward.items():
    assert round(n[k], 2) == val, (k, n[k], val)
# The slide multiplies already rounded values (0.20 * 2.00 = 0.40), so the
# leaves differ from the exact gradient by up to 0.01.
for k, val in slide_backward.items():
    assert abs(g[k] - val) <= 0.0105, (k, g[k], val)
names = list(v)
f = lambda vals: bc.graph_forward(dict(zip(names, vals)))["out"]  # noqa: E731
num = []
for i in range(len(names)):
    e = np.zeros(len(names))
    e[i] = 1e-6
    base = np.array([v[k] for k in names])
    num.append((f(base + e) - f(base - e)) / 2e-6)
ana = [g[k] for k in names]
err29 = bc.rel_error([np.array(ana)], [np.array(num)])
s = n["s"]
local = bc.sigmoid(s) * (1 - bc.sigmoid(s))
closed = {"x0": local * v["w0"], "w0": local * v["x0"], "x1": local * v["w1"], "w1": local * v["x1"], "w2": local}
for k in closed:
    assert abs(closed[k] - g[k]) < 1e-12, k
assert err29 < TOL, err29
print("slide 29: rounded values match the slide; max rel error vs finite differences", f"{err29:.1e}")
print("  exact gradients:", {k: round(g[k], 4) for k in names}, "sigma'(1) =", round(local, 4))

# 2. Two-layer network, matrix form.
X, y = fk.dataset("circles")
X, y = X[:60], y[:60].astype(float)
rng = np.random.default_rng(fk.SEED)
H = 4
params_rand = [rng.normal(0, 1, (H, 2)), rng.normal(0, 1, H), rng.normal(0, 1, H), np.array(rng.normal())]

clf = MLPClassifier(hidden_layer_sizes=(H,), activation="logistic", solver="lbfgs", alpha=0.01,
                    max_iter=20000, tol=1e-10, random_state=fk.SEED).fit(X, y)
params_fit = [clf.coefs_[0].T, clf.intercepts_[0], clf.coefs_[1][:, 0], np.array(clf.intercepts_[1][0])]
mine = bc.mlp_forward(params_fit, X)["p"]
gap = float(np.max(np.abs(mine - clf.predict_proba(X)[:, 1])))
assert gap < 1e-12, gap
print(f"forward pass equals sklearn predict_proba: max gap {gap:.1e}")

results = {}
for label, params in (("random", params_rand), ("fitted", params_fit)):
    ana = bc.mlp_backward(params, bc.mlp_forward(params, X), y)
    num = bc.numeric_grad(lambda p: bc.mlp_loss(p, X, y), params)
    err = bc.rel_error(ana, num)
    assert err < TOL, (label, err)
    results[label] = (ana, num, err)
    print(f"MLP {label} weights: max rel error vs finite differences {err:.1e}")

# 3. Falsification: every planted defect must be caught.
for defect in ("no_sigma_prime", "wrong_sign", "no_mean"):
    ana = bc.mlp_backward(params_rand, bc.mlp_forward(params_rand, X), y, broken=defect)
    err = bc.rel_error(ana, results["random"][1])
    assert err > 1e-2, (defect, err)
    print(f"defect {defect}: caught, rel error {err:.2f}")

fig, axes = fk.subplots(1, 2, size=(8.4, 3.8))
# The note names the parameters W, b (hidden layer) and v, c (output neuron).
labels = ["$W$", "$b$", "$v$", "$c$"]
for ax, label in zip(axes, ("random", "fitted")):
    ana, num, err = results[label]
    for k, (a, b) in enumerate(zip(ana, num)):
        if k < 3:
            ax.scatter(np.ravel(b), np.ravel(a), s=28, color=fk.CATEGORICAL[k], label=labels[k], zorder=3)
        else:
            # Hollow, so the b points near zero stay visible under it.
            ax.scatter(np.ravel(b), np.ravel(a), s=70, marker="D", facecolors="none", edgecolors=fk.ACCENT,
                       linewidths=1.3, label=labels[k], zorder=4)
    lim = max(np.max(np.abs(np.concatenate([np.ravel(x) for x in num]))), 1e-9) * 1.15
    ax.plot([-lim, lim], [-lim, lim], color=fk.TEXT_2, lw=0.8, ls="--", zorder=1)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel("конечные разности")
    ax.set_ylabel("backprop")
    ax.set_title("случайные веса" if label == "random" else "веса после обучения")
    ax.text(0.03, 0.97, f"отн. ошибка {err:.0e}", transform=ax.transAxes, va="top", fontsize=8)
    ax.legend(loc="lower right")
fig.tight_layout()
fk.save(fig, fk.attachments(6) / "backprop-gradcheck.png")
