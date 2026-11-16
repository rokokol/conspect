"""Reference answers from sklearn for the JS core tests.

Writes fixtures.json next to this file: the shared data sets and what sklearn
predicts on a fixed grid, so mlcore.js is checked against the library the
figures are drawn with, not against itself.
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figures"))
sys.path.insert(0, str(HERE.parent / "figures" / "07"))
import figkit as fk  # noqa: E402


def grid(X, steps=40):
    lo, hi = X.min(0) - 0.5, X.max(0) + 0.5
    xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], steps), np.linspace(lo[1], hi[1], steps))
    return np.c_[xx.ravel(), yy.ravel()]


def mlp_fixtures():
    """Reference answers for the MLP of the "mlp" page.

    forward: weights of a trained MLPClassifier and its predict_proba, so the
    JS forward pass is checked against the library on the same weights.
    step: full-batch SGD without momentum and without L2 (the solver the page
    uses). The start weights are ours, written into a fitted-once model in
    place, so every later partial_fit call is one exact gradient step from a
    known point; weights and the loss before each step are recorded.
    splits: the train and test parts the page shows, rounded as build_pages does.
    """
    import warnings

    from sklearn.exceptions import ConvergenceWarning
    from sklearn.neural_network import MLPClassifier

    splits = {}
    for name in ["xor", "circles", "moons"]:
        X, y = fk.dataset(name)
        Xtr, Xte, ytr, yte = fk.split(X, y)
        splits[name] = {"Xtr": Xtr.round(4).tolist(), "ytr": ytr.tolist(),
                        "Xte": Xte.round(4).tolist(), "yte": yte.tolist()}
    Xtr, ytr = np.array(splits["circles"]["Xtr"]), np.array(splits["circles"]["ytr"])
    pts = np.vstack([grid(Xtr, 30), Xtr])

    forward = []
    for seed, (hidden, act) in enumerate([([3], "tanh"), ([8], "relu"), ([4, 5], "logistic"),
                                          ([6, 6, 6], "identity"), ([2, 3, 4], "tanh"), ([8, 8, 8], "relu")]):
        m = MLPClassifier(hidden, activation=act, solver="adam", max_iter=300, random_state=seed)
        with warnings.catch_warnings():
            # Only the weights matter here, not an optimum.
            warnings.simplefilter("ignore", ConvergenceWarning)
            m.fit(Xtr, ytr)
        forward.append({"hidden": hidden, "act": act, "points": pts.tolist(),
                        "coefs": [c.tolist() for c in m.coefs_], "intercepts": [b.tolist() for b in m.intercepts_],
                        "proba1": m.predict_proba(pts)[:, 1].tolist()})

    step = []
    for seed, (data, hidden, act, lr, n_steps) in enumerate([
            ("circles", [3], "tanh", 0.5, 5), ("circles", [5, 4], "relu", 0.3, 5),
            ("xor", [4, 4, 4], "logistic", 1.0, 5), ("moons", [6], "identity", 0.1, 5),
            ("circles", [3], "tanh", 10.0, 4)]):
        X, y = np.array(splits[data]["Xtr"]), np.array(splits[data]["ytr"])
        n = len(X)
        m = MLPClassifier(hidden, activation=act, solver="sgd", momentum=0.0, nesterovs_momentum=False,
                          learning_rate="constant", learning_rate_init=lr, alpha=0.0, batch_size=n,
                          shuffle=False, max_iter=1, random_state=seed)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            m.partial_fit(X, y, classes=[0, 1])
        rg = np.random.default_rng(seed)
        for c in m.coefs_:
            c[...] = rg.normal(0, 0.7, c.shape)
        for b in m.intercepts_:
            b[...] = rg.normal(0, 0.3, b.shape)
        start = {"coefs": [c.tolist() for c in m.coefs_], "intercepts": [b.tolist() for b in m.intercepts_]}
        after, loss_before, seen = [], [], m.t_
        for _ in range(n_steps):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                m.partial_fit(X, y)
            assert m.t_ == seen + n, "one partial_fit must be one pass over the batch, that is one step"
            seen = m.t_
            loss_before.append(float(m.loss_))
            after.append({"coefs": [c.tolist() for c in m.coefs_], "intercepts": [b.tolist() for b in m.intercepts_]})
        step.append({"data": data, "hidden": hidden, "act": act, "lr": lr, "start": start,
                     "after": after, "loss_before": loss_before})
    return {"splits": splits, "forward": forward, "step": step}


def opt_fixtures():
    """Paths of the six optimizers of figures/06/opt_common.py, the reference of the "optimizers" page.

    table: the note's setting (Rosenbrock, start (-1.5, 1.8), 100 steps, the
    listed steps eta, rho = beta = 0.9). variants: other surface, start, steps,
    rho and beta, so that every parameter of the JS version is pinned.
    surfaces: values and gradients of the surfaces at fixed points.
    """
    sys.path.insert(0, str(HERE.parent / "figures" / "06"))
    import opt_common as oc

    def path(name, surface, w0, lr, steps, rho=0.9, beta=0.9):
        kw = {"Momentum": {"rho": rho}, "Nesterov": {"rho": rho}, "RMSProp": {"beta": beta}}.get(name, {})
        opt = oc.OPTIMIZERS[name](lr, **kw)
        return oc.run(opt, w0, surface.grad, steps).tolist()

    # The steps are points of the log grid of opt-trajectories.py (10^(-5 + k/8)); the note prints them rounded to two digits.
    lr_table = {"SGD": 10 ** -1.75, "Momentum": 10 ** -2.0, "Nesterov": 10 ** -2.25, "Adagrad": 10 ** -0.75,
                "RMSProp": 10 ** -1.375, "Adam": 10 ** -1.0}
    start = [-1.5, 1.8]
    table = [{"method": n, "lr": lr, "path": path(n, oc.Rosenbrock, start, lr, 100)} for n, lr in lr_table.items()]
    variants = []
    for n, lr in lr_table.items():
        variants.append({"method": n, "surface": "rosen", "start": [0.3, -1.2], "lr": lr * 1.7, "steps": 40, "rho": 0.5, "beta": 0.99,
                         "path": path(n, oc.Rosenbrock, [0.3, -1.2], lr * 1.7, 40, 0.5, 0.99)})
        variants.append({"method": n, "surface": "ellipse", "start": [-2.6, 1.6], "lr": min(lr, 0.09), "steps": 30, "rho": 0.8, "beta": 0.8,
                         "path": path(n, oc.Valley, [-2.6, 1.6], min(lr, 0.09), 30, 0.8, 0.8)})
    pts = [[-1.5, 1.8], [0.3, -1.2], [1.0, 1.0], [-0.4, 0.7], [2.0, 2.0]]
    surfaces = {"rosen": {"points": pts, "f": [float(oc.Rosenbrock.f(p)) for p in pts], "grad": [oc.Rosenbrock.grad(np.array(p)).tolist() for p in pts]},
                "ellipse": {"points": pts, "f": [float(oc.Valley.f(np.array(p))) for p in pts], "grad": [oc.Valley.grad(np.array(p)).tolist() for p in pts]}}
    return {"table": table, "variants": variants, "surfaces": surfaces}


def importance_fixtures():
    """Reference answers for the feature importances of the "importance" page.

    One table with the columns of the page (two continuous signals, a binary
    signal, a continuous noise with a distinct value per row, a noise with
    three values), a train and a held-out part. For a tree and for a logistic
    regression: feature_importances_ (tree), sklearn's own permutation_importance
    run on permutations that we choose, and drop column as a refit without the
    column. sklearn draws its permutations itself, so check_random_state is
    replaced by a stub that hands out the listed ones: JS then shuffles the same
    rows. perms[k] is the index array sklearn applies at repeat k to the column
    as the previous repeat left it (every column sees the same list).
    """
    import sklearn.inspection._permutation_importance as pi

    rng = np.random.default_rng(7)
    n, n_train = 450, 300
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    flag = rng.integers(0, 2, size=n)
    y = (x1 + 0.6 * x2 + 1.6 * (flag - 0.5) + rng.normal(0, 0.9, size=n) > 0).astype(int)
    X = np.column_stack([20 + 5 * x1, x2, flag, rng.normal(size=n), rng.integers(0, 3, size=n)]).round(6)
    Xtr, Xte, ytr, yte = X[:n_train], X[n_train:], y[:n_train], y[n_train:]
    perms = [rng.permutation(len(yte)).tolist() for _ in range(6)]

    class Stub:
        def __init__(self):
            self.k = 0

        def randint(self, _n):
            return 0

        def shuffle(self, arr):
            arr[:] = perms[self.k]
            self.k += 1

    def permutation(model):
        original = pi.check_random_state
        pi.check_random_state = lambda _s: Stub()
        try:
            r = pi.permutation_importance(model, Xte, yte, n_repeats=len(perms), random_state=0, scoring="accuracy")
        finally:
            pi.check_random_state = original
        return {"mean": r.importances_mean.tolist(), "std": r.importances_std.tolist(), "all": r.importances.tolist()}

    def drop(make):
        base = make().fit(Xtr, ytr).score(Xte, yte)
        out = []
        for j in range(X.shape[1]):
            keep = [k for k in range(X.shape[1]) if k != j]
            out.append(base - make().fit(Xtr[:, keep], ytr).score(Xte[:, keep], yte))
        return out

    res = {"Xtr": Xtr.tolist(), "ytr": ytr.tolist(), "Xte": Xte.tolist(), "yte": yte.tolist(), "perms": perms, "trees": []}
    # No fully grown tree, no small leaf: two columns that cut off the same
    # class counts have the same gain (two objects of different classes, or a
    # leaf-sized end piece of one class), sklearn breaks that tie by a random
    # feature order and JS by the first column, so the trees differ in who gets
    # the split, not in quality. These settings are the ones where the data
    # at hand has no such tie, and the trees are node for node the same.
    for kw in [{"max_depth": 2}, {"max_depth": 3}, {"min_samples_leaf": 15}, {"min_samples_leaf": 20, "max_depth": 6}]:
        def make(kw=kw):
            return DecisionTreeClassifier(random_state=0, **kw)
        m = make().fit(Xtr, ytr)
        res["trees"].append({"params": kw, "mdi": m.feature_importances_.tolist(), "test_acc": float(m.score(Xte, yte)),
                             "permutation": permutation(m), "drop": drop(make)})

    def make_lr():
        return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=10000, tol=1e-12, solver="newton-cholesky"))
    m = make_lr().fit(Xtr, ytr)
    sc, lr = m.named_steps["standardscaler"], m.named_steps["logisticregression"]
    logit = m.decision_function(Xtr)
    res["logreg"] = {"std": lr.coef_[0].tolist(), "raw": (lr.coef_[0] / sc.scale_).tolist(),
                     "beta": (lr.coef_[0] / logit.std()).tolist(), "test_acc": float(m.score(Xte, yte)),
                     "permutation": permutation(m), "drop": drop(make_lr)}
    return res


def lime_fixtures():
    """Reference answers for the LIME page.

    One cloud Z = x + scale * eps with unequal scales, so a distance taken in raw
    units differs from one taken in standardised units. The weights follow
    lime_tabular.py (read from its source, the package is not installed): the
    distance is Euclidean between standardised rows, the kernel is
    sqrt(exp(-d^2 / width^2)), the default width is 0.75 sqrt(p). The local fit
    is a weighted least squares, from two independent routes that must agree:
    lime_common.local_fit and sklearn LinearRegression with sample_weight.
    """
    import sklearn.metrics
    from sklearn.linear_model import LinearRegression

    import lime_common as lc

    rng = np.random.default_rng(11)
    x = np.array([0.3, -0.2])
    scale = np.array([0.87, 0.52])
    mean = np.array([0.1, 0.4])  # the training mean cancels in a difference
    n = 300
    eps = rng.normal(size=(n, 2))
    Z = x + scale * eps
    t = 1 / (1 + np.exp(-3 * (Z[:, 0] + 1.5 * Z[:, 1] - 0.2 + 0.5 * np.sin(3 * Z[:, 0]))))
    grad = np.array([-1.1, 2.3])

    def lime_weights(width):
        # lime_tabular.py: scaled_data = (data - mean_) / scale_; distances = pairwise_distances(scaled_data,
        # scaled_data[0]); kernel(d, kernel_width) = sqrt(exp(-d^2 / kernel_width^2)).
        scaled = (np.vstack([x, Z]) - mean) / scale
        d = sklearn.metrics.pairwise_distances(scaled, scaled[0].reshape(1, -1)).ravel()[1:]
        return np.sqrt(np.exp(-(d**2) / width**2)), d

    fits = []
    for width in [0.2, 0.5, 0.75 * np.sqrt(2), 3.0]:
        w, d = lime_weights(width)
        a, coef, r2 = lc.local_fit(lambda _Z: t, x, Z, w)
        lr = LinearRegression().fit(Z - x, t, sample_weight=w)
        assert np.allclose(lr.coef_, coef) and np.isclose(lr.intercept_, a) and np.isclose(lr.score(Z - x, t, sample_weight=w), r2)
        fits.append({"width": float(width), "weights": w.tolist(), "dist": d.tolist(), "a": float(a), "coef": coef.tolist(),
                     "r2": float(r2), "n_eff": float(w.sum() ** 2 / (w**2).sum()), "angle": lc.angle(coef, grad)})
    # lime_common writes the kernel as exp(-d^2 / sigma^2), the LIME paper's form: the same one at width = sigma / sqrt(2).
    for sigma in (0.5, 1.3):
        w_paper = lc.kernel(x + eps, x, sigma)
        w_lime = np.sqrt(np.exp(-(np.linalg.norm(eps, axis=1) ** 2) / (sigma / np.sqrt(2)) ** 2))
        assert np.allclose(w_paper, w_lime)
    segs = []
    for a, c, lvl in [(0.536, np.array([-0.30, -0.94]), 0.5), (0.4, np.array([1.2, 0.3]), 0.5), (0.5, np.array([0.0, -1.0]), 0.5),
                     (0.45, np.array([0.8, -0.6]), 0.3), (0.2, np.array([-0.4, 1.1]), 0.7)]:
        xs, ys = lc.boundary_segment(a, c, x, (-2.0, 2.0, -1.5, 1.5), lvl)
        segs.append({"a": a, "c": c.tolist(), "level": lvl, "xs": xs.tolist(), "ys": ys.tolist()})
    return {"x": x.tolist(), "scale": scale.tolist(), "mean": mean.tolist(), "eps": eps.tolist(), "t": t.tolist(),
            "grad": grad.tolist(), "fits": fits, "segments": segs, "box": [-2.0, 2.0, -1.5, 1.5],
            "default_width": {str(p): float(0.75 * np.sqrt(p)) for p in (2, 4, 8)}}


def tree_to_nested(tree):
    """A fitted sklearn regression tree as the nested nodes of mlcore.js: feature, threshold, left, right, value, n."""
    t = tree.tree_

    def go(i):
        node = {"value": float(t.value[i].ravel()[0]), "n": float(t.weighted_n_node_samples[i])}
        if t.children_left[i] != -1:
            node["feature"] = int(t.feature[i])
            node["threshold"] = float(t.threshold[i])
            node["left"] = go(t.children_left[i])
            node["right"] = go(t.children_right[i])
        return node

    return go(0)


def shap_fixtures():
    """Reference answers for the SHAP page, taken from figures/07/shapley_lib.py.

    games: arbitrary value tables v[mask] for m = 3, 4, 5 players, the Shapley values by coalitions and
    by orders (same order of orders as itertools.permutations). toy: the game f = 3 x1 + x2 x3 of the note with
    a fourth player the game does not use, independent coins as the background. gbr: a fitted
    GradientBoostingRegressor on four features, two of them correlated, written out as nested trees;
    v(S) interventional (any model, brute force) and by the tree rule of slide 27, the values for both.
    """
    import itertools
    import math

    from sklearn.ensemble import GradientBoostingRegressor

    import shapley_lib as sl

    rng = np.random.default_rng(3)
    games = []
    for m in (3, 4, 5):
        v = rng.normal(size=2**m)
        games.append({"m": m, "v": v.tolist(), "phi": sl.shapley_from_values(v, m).tolist(),
                      "phi_orders": sl.shapley_by_orders(v, m).tolist()})
    # Per-order increments for m = 4, in the order of itertools.permutations.
    v4 = np.array(games[1]["v"])
    inc = []
    for order in itertools.permutations(range(4)):
        mask, row = 0, [0.0] * 4
        for i in order:
            row[i] = float(v4[mask | (1 << i)] - v4[mask])
            mask |= 1 << i
        inc.append({"order": list(order), "inc": row})

    def toy(Z):
        return 3 * Z[:, 0] + Z[:, 1] * Z[:, 2]

    coins = sl.coalitions(4).astype(float)  # all 16 combinations of four independent fair coins
    xt = np.array([[1.0, 1.0, 1.0, 0.0]])
    vt = sl.interventional_values(toy, xt, coins)[:, 0]
    toy_fx = {"x": xt[0].tolist(), "background": coins.tolist(), "v": vt.tolist(),
              "phi": sl.shapley_from_values(vt, 4).tolist()}

    n, rho = 160, 0.9
    x1, z2, x3, x4 = rng.normal(size=(4, n))
    X = np.column_stack([x1, rho * x1 + np.sqrt(1 - rho**2) * z2, x3, x4])
    y = 3 * x1 + x3 * x4 + 0.3 * rng.normal(size=n)
    Xtr, ytr = X[:100], y[:100]
    gbr = GradientBoostingRegressor(n_estimators=25, learning_rate=0.2, max_depth=3, random_state=0).fit(Xtr, ytr)
    Xo = X[100:106]
    bg = Xtr[:60]
    v_int = sl.interventional_values(gbr.predict, Xo, bg)
    v_path = sl.gbr_coalition_values(gbr, Xo)
    # Independent check of the leaf-product implementation by direct recursion of slide 27.
    for j in range(len(Xo)):
        for mask in range(16):
            S = {i for i in range(4) if mask >> i & 1}
            direct = float(gbr.init_.constant_.ravel()[0]) + gbr.learning_rate * sum(
                sl.recursive_tree_value(est[0], Xo[j], S) for est in gbr.estimators_)
            assert math.isclose(direct, v_path[mask, j], abs_tol=1e-9)
    assert np.allclose(v_int[15], gbr.predict(Xo)) and np.allclose(v_path[15], gbr.predict(Xo))
    gbr_fx = {
        "f0": float(gbr.init_.constant_.ravel()[0]), "lr": float(gbr.learning_rate),
        "trees": [tree_to_nested(est[0]) for est in gbr.estimators_],
        "X": Xo.tolist(), "background": bg.tolist(), "pred": gbr.predict(Xo).tolist(),
        "v_int": v_int.T.tolist(), "v_path": v_path.T.tolist(),
        "phi_int": sl.shapley_from_values(v_int, 4).T.tolist(), "phi_path": sl.shapley_from_values(v_path, 4).T.tolist()}
    return {"games": games, "orders4": inc, "toy": toy_fx, "gbr": gbr_fx}


def softmax_fixtures():
    """Reference answers for the "softmax" page, from figures/08/softmax_common.py.

    softmax and entropy of the ten logits of the note at a range of temperatures, taken from the figures' own
    functions. The gradient of the cross-entropy is not taken from a formula: it is the central difference of
    C(z) = -sum p ln softmax(z / T), the way the note checks (q - p) / T, so the page's closed form is held to
    something that does not share it.
    """
    sys.path.insert(0, str(HERE.parent / "figures" / "08"))
    import softmax_common as sc

    def loss(z, p, T):
        return float(-(p * np.log(sc.softmax(z, T))).sum())

    def numeric_grad(p, T, h=1e-6):
        g = []
        for i in range(len(sc.Z)):
            e = np.zeros(len(sc.Z))
            e[i] = h
            g.append((loss(sc.Z + e, p, T) - loss(sc.Z - e, p, T)) / (2 * h))
        return g

    temps = [0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 20.0, 50.0]
    soft = sc.softmax(sc.Z, 4.0)  # a label that is not one-hot: the teacher's distribution at T = 4
    labels = {"audi": np.eye(10)[sc.AUDI], "lada": np.eye(10)[0], "mushroom": np.eye(10)[5], "soft": soft}
    return {
        "names": sc.NAMES, "z": sc.Z.tolist(), "temps": temps,
        "q": [sc.softmax(sc.Z, T).tolist() for T in temps],
        "entropy": [float(sc.entropy(sc.softmax(sc.Z, T))) for T in temps],
        "labels": {k: p.tolist() for k, p in labels.items()},
        "grad": {k: {str(T): numeric_grad(p, T) for T in (0.5, 1.0, 4.0)} for k, p in labels.items()},
    }


def distill_fixtures():
    """Reference answers for the "distill" page, from figures/08/distill_common.py.

    gbc: GradientBoostingClassifier (the teacher of the figures) on the train part of moons and circles,
    rounded as build_pages rounds it: decision_function on the train points and on a grid, and the log-odds start.
    loss: the Hinton loss and its gradient from distill_common.loss_and_grads for a K = 2 network whose logits
    are (-d/2, d/2): its loss is a function of d = z1 - z0 alone, so a one-logit network with the same hidden
    layer has the same loss, the same hidden-layer gradient, and the gradient of the output weights equal to the
    column of the second logit. The teacher's logits are (-u/2, u/2), as distill_common.teacher_logits makes them.
    """
    sys.path.insert(0, str(HERE.parent / "figures" / "08"))
    import distill_common as dc
    from sklearn.ensemble import GradientBoostingClassifier

    gbc = []
    # "moons-skew" keeps every third object of class 1 only: the classes are balanced in the other sets, where a
    # start at log-odds 0 would equal the right one, so only this set tells the two apart.
    for name, n, depth, lr in [("moons", 20, 2, 0.1), ("moons", 100, 3, 0.1), ("circles", 50, 1, 0.3), ("circles", 40, 2, 1.0),
                               ("moons-skew", 30, 2, 0.2)]:
        Xd, yd = fk.dataset(name.split("-")[0])
        Xtr, _, ytr, _ = fk.split(Xd, yd)
        Xtr = Xtr.round(4)
        if name == "moons-skew":
            keep = (ytr == 0) | (np.cumsum(ytr == 1) % 3 == 0)
            Xtr, ytr = Xtr[keep], ytr[keep]
        m = GradientBoostingClassifier(n_estimators=n, max_depth=depth, learning_rate=lr, random_state=0).fit(Xtr, ytr)
        g = grid(Xtr, 30)
        # Where two splits tie (a node of a few objects can be cut by either feature) sklearn picks one by its
        # random feature order: the train fit is the same for every seed, the geometry off the train points is not.
        # grid_spread is that freedom, measured here; zero means the grid answer is fixed by the data.
        others = [GradientBoostingClassifier(n_estimators=n, max_depth=depth, learning_rate=lr, random_state=rs)
                  .fit(Xtr, ytr).decision_function(g) for rs in range(1, 6)]
        spread = float(max(np.abs(o - m.decision_function(g)).max() for o in others))
        gbc.append({"ds": name, "n": n, "depth": depth, "lr": lr, "X": Xtr.tolist(), "y": ytr.tolist(),
                    "grid_spread": spread,
                    "init": float(np.log(ytr.mean() / (1 - ytr.mean()))),
                    "train": m.decision_function(Xtr).tolist(), "grid": g.tolist(),
                    "decision": m.decision_function(g).tolist(),
                    "staged_train": [s.tolist() for s in list(m.staged_decision_function(Xtr))[:8]]})

    rng = np.random.default_rng(3)
    loss = []
    for T, lam, hidden in [(1.0, 1.0, 4), (1.0, 0.0, 4), (2.0, 0.5, 5), (4.0, 0.25, 3), (8.0, 0.0, 6), (16.0, 0.5, 4), (3.0, 0.7, 1)]:
        X = rng.normal(size=(12, 2))
        y = rng.integers(0, 2, 12)
        u = rng.normal(scale=3.0, size=12)
        W0, b0, v, c = rng.normal(size=(2, hidden)), rng.normal(size=hidden), rng.normal(size=hidden), float(rng.normal())
        params = [[W0, b0], [np.c_[-v / 2, v / 2], np.array([-c / 2, c / 2])]]
        V = np.c_[-u / 2, u / 2]
        P = np.exp(V / T - np.log(np.exp(V / T).sum(1, keepdims=True)))
        val, grads = dc.loss_and_grads(params, X, np.eye(2)[y], P, T, lam, "tanh")
        loss.append({"T": T, "lam": lam, "hidden": hidden, "X": X.tolist(), "y": y.tolist(), "u": u.tolist(),
                     "W0": W0.T.tolist(), "b0": b0.tolist(), "v": v.tolist(), "c": c,
                     "loss": float(val), "gW0": grads[0][0].T.tolist(), "gb0": grads[0][1].tolist(),
                     "gv": grads[1][0][:, 1].tolist(), "gc": float(grads[1][1][1])})
    return {"gbc": gbc, "loss": loss}


def main():
    out = {"datasets": {}, "knn": [], "tree": [], "logreg": [], "poly": {}, "roc": {}}
    for name in ["moons", "circles", "xor", "blobs3"]:
        X, y = fk.dataset(name)
        out["datasets"][name] = {"X": X.round(6).tolist(), "y": y.tolist()}

    X, y = fk.dataset("moons")
    X = X.round(6)
    G = grid(X)
    out["grid"] = G.tolist()

    for k in [1, 5, 15]:
        m = KNeighborsClassifier(k).fit(X, y)
        out["knn"].append({"k": k, "proba1": m.predict_proba(G)[:, 1].tolist()})

    for depth in [1, 2, 3, 4]:
        m = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X, y)
        out["tree"].append({"depth": depth, "pred": m.predict(G).tolist(),
                            "train_acc": float(m.score(X, y))})

    pf = PolynomialFeatures(3, include_bias=False)
    out["poly"] = {"x": [0.7, -1.3], "deg": 3,
                   "features": pf.fit_transform([[0.7, -1.3]])[0].tolist(),
                   "names": pf.get_feature_names_out(["x1", "x2"]).tolist()}

    # newton-cholesky reaches the exact optimum; lbfgs stops short of it at
    # degree 5, C = 100 (objective 4984.03287095 against 4984.03287091).
    for deg, C in [(1, 1.0), (3, 1.0), (3, 0.01), (5, 100.0)]:
        m = make_pipeline(PolynomialFeatures(deg, include_bias=False), StandardScaler(),
                          LogisticRegression(C=C, max_iter=10000, tol=1e-12,
                                             solver="newton-cholesky")).fit(X, y)
        out["logreg"].append({"deg": deg, "C": C, "proba1": m.predict_proba(G)[:, 1].tolist()})

    # "Powers only": the columns of PolynomialFeatures whose monomial has a
    # single nonzero exponent (x1^k or x2^k), so the model is f(x1) + g(x2).
    out["logreg_pure"] = []
    for name, deg, C in [("moons", 3, 1.0), ("xor", 3, 1.0), ("xor", 5, 100.0)]:
        Xd, yd = fk.dataset(name)
        Xd = Xd.round(6)
        pf = PolynomialFeatures(deg, include_bias=False).fit(Xd)
        keep = (pf.powers_ > 0).sum(axis=1) == 1
        m = make_pipeline(StandardScaler(), LogisticRegression(
            C=C, max_iter=10000, tol=1e-12, solver="newton-cholesky")).fit(pf.transform(Xd)[:, keep], yd)
        Gd = grid(Xd, 25)
        out["logreg_pure"].append({
            "data": name, "deg": deg, "C": C, "grid": Gd.tolist(),
            "names": pf.get_feature_names_out(["x1", "x2"])[keep].tolist(),
            "at": [0.7, -1.3], "features": pf.transform([[0.7, -1.3]])[0, keep].tolist(),
            "proba1": m.predict_proba(pf.transform(Gd)[:, keep])[:, 1].tolist()})

    m = make_pipeline(PolynomialFeatures(3, include_bias=False), StandardScaler(),
                      LogisticRegression(C=1.0, max_iter=10000)).fit(X, y)
    s = m.predict_proba(X)[:, 1]
    fpr, tpr, _ = roc_curve(y, s)
    out["roc"] = {"scores": s.tolist(), "y": y.tolist(), "auc": float(roc_auc_score(y, s)),
                  "fpr": fpr.tolist(), "tpr": tpr.tolist(),
                  "at": [{"t": t, "precision": float(precision_score(y, s >= t)),
                          "recall": float(recall_score(y, s >= t))}
                         for t in [0.2, 0.5, 0.8, float(np.sort(s)[150])]]}
    ties_s = [0.9, 0.5, 0.5, 0.5, 0.2, 0.2, 0.7, 0.1]
    ties_y = [1, 1, 0, 0, 1, 0, 1, 0]
    out["roc_ties"] = {"scores": ties_s, "y": ties_y, "auc": float(roc_auc_score(ties_y, ties_s))}

    # Polynomial regression on reg1d: plain least squares, Ridge and Lasso on
    # standardised polynomial features (intercept not penalised in sklearn).
    from sklearn.linear_model import Lasso, LinearRegression, Ridge
    Xr, yr = fk.dataset("reg1d")
    Xr = Xr.round(6)
    yr = yr.round(6)
    xs = np.linspace(-0.05, 1.05, 50)[:, None]
    out["reg1d"] = {"x": Xr[:, 0].tolist(), "y": yr.tolist(), "grid": xs[:, 0].tolist(), "fits": []}
    for kind, deg, alpha in [("ols", 1, 0), ("ols", 3, 0), ("ols", 9, 0), ("ridge", 9, 0.01),
                             ("ridge", 9, 1.0), ("lasso", 9, 0.001), ("lasso", 9, 0.05)]:
        reg = {"ols": LinearRegression(), "ridge": Ridge(alpha=alpha),
               "lasso": Lasso(alpha=alpha, max_iter=1000000, tol=1e-12)}[kind]
        m = make_pipeline(PolynomialFeatures(deg, include_bias=False), StandardScaler(), reg).fit(Xr, yr)
        pred, coef = m.predict(xs), m[-1].coef_
        if kind == "ols":
            # sklearn 1.9 LinearRegression drops the smallest singular value at
            # degree 9 (rank_ 8) and returns a truncated solution with a larger
            # RSS (2.400 against 2.134). The reference is the exact minimiser.
            import scipy.linalg
            Z = m[:-1].transform(Xr)
            coef = scipy.linalg.lstsq(Z - Z.mean(0), yr - yr.mean())[0]
            pred = m[:-1].transform(xs) @ coef + yr.mean() - Z.mean(0) @ coef
        out["reg1d"]["fits"].append({"kind": kind, "deg": deg, "alpha": alpha,
                                     "pred": pred.tolist(), "coef": coef.tolist()})

    # Exact LASSO path (LARS with the lasso modification) on standardised
    # polynomial features, evaluated at a few alphas by linear interpolation.
    from sklearn.linear_model import lars_path
    out["lassopath"] = []
    for deg in [9, 12]:
        Z = StandardScaler().fit_transform(PolynomialFeatures(deg, include_bias=False).fit_transform(Xr))
        alphas, _, coefs = lars_path(Z, yr - yr.mean(), method="lasso")
        probes = [1e-6, 1e-4, 1e-3, 1e-2, 0.1, 0.3]
        at = [[float(np.interp(a, alphas[::-1], c[::-1])) for c in coefs] for a in probes]
        out["lassopath"].append({"deg": deg, "probes": probes, "w": at,
                                 "breakpoints": len(alphas)})

    # Regression trees and gradient boosting on reg1d. Boosting's friedman_mse
    # ranks the splits of a single-output node the same as the MSE decrease,
    # (n_l n_r / n) (mean_l - mean_r)^2 against the same divided by n.
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.tree import DecisionTreeRegressor
    out["regtree"] = []
    for depth in [1, 2, 3, 5]:
        m = DecisionTreeRegressor(max_depth=depth, random_state=0).fit(Xr, yr)
        out["regtree"].append({"depth": depth, "pred": m.predict(xs).tolist()})
    out["gbr"] = []
    for n, lr, depth in [(1, 0.1, 1), (10, 0.3, 2), (50, 0.1, 3), (200, 1.0, 1)]:
        m = GradientBoostingRegressor(n_estimators=n, learning_rate=lr, max_depth=depth,
                                      random_state=0).fit(Xr, yr)
        out["gbr"].append({"n": n, "lr": lr, "depth": depth, "pred": m.predict(xs).tolist(),
                           "staged_train_mse": [float(np.mean((p - yr) ** 2))
                                                for p in m.staged_predict(Xr)]})

    # Gradient boosting under the three regression losses of sklearn 1.9, on
    # reg1d with and without three outliers. For absolute_error and huber
    # sklearn refits the leaf values after every tree (median of the leaf's
    # residuals; for huber also the mean of the clipped deviations), and huber
    # takes delta as the alpha-quantile of the absolute residuals before each
    # tree. Even sample and leaf sizes are on purpose: sklearn's init is the
    # true median (mean of the middle two) while a leaf takes the lower one.
    yo = yr.copy()
    yo[[3, 17, 30]] += np.array([3.0, -3.5, 2.5])
    out["gbr_loss"] = []
    for loss, alpha, n, lr, depth, outl in [
            ("squared_error", 0.9, 30, 0.3, 2, True), ("absolute_error", 0.9, 1, 0.5, 2, False),
            ("absolute_error", 0.9, 40, 0.3, 2, False), ("absolute_error", 0.9, 40, 0.3, 2, True),
            ("absolute_error", 0.9, 120, 0.1, 3, True), ("huber", 0.9, 1, 0.5, 2, True),
            ("huber", 0.9, 40, 0.3, 2, True), ("huber", 0.5, 40, 0.3, 2, True),
            ("huber", 0.9, 100, 0.1, 3, False)]:
        yy = yo if outl else yr
        m = GradientBoostingRegressor(loss=loss, alpha=alpha, n_estimators=n, learning_rate=lr,
                                      max_depth=depth, random_state=0).fit(Xr, yy)
        out["gbr_loss"].append({
            "loss": loss, "alpha": alpha, "n": n, "lr": lr, "depth": depth, "outliers": outl,
            "y": yy.tolist(), "init": float(m.init_.predict(Xr[:1])[0]),
            "pred": m.predict(xs).tolist(),
            "staged_train_mae": [float(np.mean(np.abs(p - yy))) for p in m.staged_predict(Xr)],
            "staged_train_mse": [float(np.mean((p - yy) ** 2)) for p in m.staged_predict(Xr)]})

    # Gaussian naive Bayes: parameters and posteriors, default priors and
    # priors set by hand (sklearn renormalises them, so they must sum to 1).
    from sklearn.naive_bayes import GaussianNB
    out["gnb"] = []
    for name, priors in [("moons", None), ("moons", [0.8, 0.2]), ("blobs3", None),
                         ("blobs3", [0.6, 0.3, 0.1]), ("circles", [0.1, 0.9])]:
        Xd, yd = fk.dataset(name)
        Xd = Xd.round(6)
        gd = grid(Xd)
        m = GaussianNB(priors=priors).fit(Xd, yd)
        out["gnb"].append({"ds": name, "priors": priors, "grid": gd.tolist(),
                           "proba": m.predict_proba(gd).tolist(),
                           "jll": m.predict_joint_log_proba(gd).tolist(),
                           "theta": m.theta_.tolist(), "var": m.var_.tolist(),
                           "class_prior": m.class_prior_.tolist(),
                           "epsilon": float(m.epsilon_)})

    # Line fits under MSE and MAE on small samples: least squares, the median
    # regression (QuantileRegressor, quantile 0.5, no penalty) and the three
    # regression metrics of each. Generic data, so both optima are unique.
    from sklearn.linear_model import QuantileRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    rg = np.random.default_rng(7)
    xs20 = np.sort(rg.uniform(0, 10, 20)).round(6)
    ys20 = (2 + 0.8 * xs20 + rg.normal(0, 0.6, 20)).round(6)
    out_y = ys20.copy()
    out_y[15] += 14
    cases = {"clean": (xs20, ys20), "outlier": (xs20, out_y),
             "tiny": (xs20[:6], ys20[:6] + 0.5 * rg.normal(size=6).round(6))}
    out["lines"] = []
    for name, (lx, ly) in cases.items():
        ly = np.asarray(ly).round(6)
        lin = LinearRegression().fit(lx[:, None], ly)
        lad = QuantileRegressor(quantile=0.5, alpha=0, solver="highs").fit(lx[:, None], ly)
        row = {"name": name, "x": lx.tolist(), "y": ly.tolist()}
        for key, mod in [("ols", lin), ("lad", lad)]:
            p = mod.predict(lx[:, None])
            row[key] = {"w0": float(mod.intercept_), "w1": float(mod.coef_[0]),
                        "mse": float(mean_squared_error(ly, p)),
                        "mae": float(mean_absolute_error(ly, p)), "r2": float(r2_score(ly, p))}
        out["lines"].append(row)

    # Margins and margin losses of fixed lines, none of them an optimum:
    # step as the 0-1 loss, square as the MSE of +-1 labels, hinge, logistic
    # as the log loss of sigmoid(f) rescaled to log2, all summed over objects.
    from scipy.special import expit
    from sklearn.metrics import hinge_loss, log_loss, zero_one_loss
    out["margin"] = []
    for name in ["moons", "xor"]:
        Xm = np.array(out["datasets"][name]["X"])
        k = np.array(out["datasets"][name]["y"])
        ypm = 2 * k - 1
        for w, b in [([1.3, -0.4], 0.2), ([-0.7, 0.9], -0.5), ([0.05, 0.02], 0.0), ([3.0, 2.0], 1.0)]:
            f = Xm @ np.array(w) + b
            n = len(k)
            out["margin"].append({
                "ds": name, "w": w, "b": b, "margins": (ypm * f).tolist(),
                "sum": {"step": float(n * zero_one_loss(ypm, np.where(f >= 0, 1, -1))),
                        "square": float(n * mean_squared_error(ypm, f)),
                        "hinge": float(n * hinge_loss(ypm, f)),
                        "logistic": float(n * log_loss(k, expit(f), labels=[0, 1]) / np.log(2)),
                        "exp": float(np.exp(-ypm * f).sum())}})

    # One vs Rest and One vs One over standardised logistic regressions. Each
    # binary model is a pipeline, so its scaler sees only its own sub-sample,
    # as the JS fit does. decision_function of OvR is the K logits, that of OvO
    # is votes plus a confidence term smaller than one vote.
    from sklearn.datasets import make_blobs
    from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
    mc_sets = {"blobs3": fk.dataset("blobs3"),
               "line3": make_blobs([40, 100, 100], centers=[(0, 0), (-1.5, -1.2), (1.5, 1.2)],
                                   cluster_std=0.5, random_state=3)}
    out["multiclass"] = []
    for name, (Xc, yc) in mc_sets.items():
        Xc = np.asarray(Xc).round(6)
        gc = grid(Xc)
        base = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=10000, tol=1e-12,
                                                                  solver="newton-cholesky"))
        ovr = OneVsRestClassifier(base).fit(Xc, yc)
        ovo = OneVsOneClassifier(base).fit(Xc, yc)
        out["multiclass"].append({
            "ds": name, "X": Xc.tolist(), "y": np.asarray(yc).tolist(), "grid": gc.tolist(),
            "ovr": ovr.decision_function(gc).tolist(), "ovr_pred": ovr.predict(gc).tolist(),
            "ovo": ovo.decision_function(gc).tolist(), "ovo_pred": ovo.predict(gc).tolist()})

    # Node impurities and the best threshold of a one-feature stump. Entropy
    # is scipy's (base 2), Gini is the root impurity sklearn reports,
    # misclassification is the error of the majority class (sklearn has no
    # such criterion). The stump scan runs on positions 0..n-1 with sklearn's
    # midpoint thresholds.
    from scipy.stats import entropy as sp_entropy
    from sklearn.tree import DecisionTreeClassifier as DTC
    out["impurity"] = []
    for counts in [[10, 10], [1, 19], [5, 8], [6, 1], [20, 0], [3, 3, 3], [1, 2, 7], [5, 5, 5, 5], [1, 1, 1, 17]]:
        yy = np.repeat(np.arange(len(counts)), counts)
        Xs = np.arange(len(yy))[:, None]
        gini = DTC(max_depth=1, criterion="gini").fit(Xs, yy).tree_.impurity[0]
        majority = np.full(len(yy), int(np.argmax(counts)))
        out["impurity"].append({"counts": counts, "ent": float(sp_entropy(counts, base=2)),
                                "gini": float(gini), "mis": float(zero_one_loss(yy, majority))})
    rg2 = np.random.default_rng(11)
    balls = [1] + [0] * 4 + [1] * 4 + [0] * 4 + [1] * 6 + [0]  # slide 14: 11 red (1), 9 purple (0)
    # "mirror" has two equally good thresholds, t = 1 and t = 5: a tie to resolve.
    label_sets = {"balls": balls, "mirror": [0, 0, 1, 1, 1, 1, 0, 0],"rand2a": rg2.integers(0, 2, 20).tolist(),
                  "rand2b": rg2.integers(0, 2, 20).tolist(), "rand3": rg2.integers(0, 3, 20).tolist()}
    out["stump"] = []
    for name, yy in label_sets.items():
        yy = np.array(yy)
        Xs = np.arange(len(yy))[:, None]
        row = {"name": name, "y": yy.tolist()}
        for crit in ["gini", "entropy"]:
            tr = DTC(max_depth=1, criterion=crit, random_state=0).fit(Xs, yy).tree_
            imp = tr.impurity
            if crit == "entropy":
                # sklearn's own entropy unit is not assumed: rescale to bits from the root.
                counts = np.bincount(yy)
                scale = sp_entropy(counts, base=2) / imp[0] if imp[0] > 0 else 1.0
                imp = imp * scale
            row[crit] = {"t": int(np.floor(tr.threshold[0])), "root": float(imp[0]),
                         "left": float(imp[1]), "right": float(imp[2]),
                         "nl": int(tr.n_node_samples[1]), "nr": int(tr.n_node_samples[2])}
        out["stump"].append(row)

    # Least squares polynomial in the Legendre basis on [0, 1], as sklearn
    # LinearRegression on the design matrix [P_0 .. P_d](2x - 1), and the
    # bias^2 / variance of the static figures (bv_common.decompose) on a
    # fixed matrix of predictions.
    from numpy.polynomial import legendre as leg
    from sklearn.linear_model import LinearRegression

    sys.path.insert(0, str(HERE.parent / "figures" / "05"))
    import bv_common as bv

    def design(x, degree):
        return leg.legvander(2 * np.asarray(x) - 1, degree)

    rgl = np.random.default_rng(5)
    gx = np.linspace(0, 1, 21)
    out["legendre"] = []
    for n, degree in [(12, 0), (30, 1), (30, 3), (30, 7), (15, 5), (150, 9)]:
        x = rgl.uniform(0, 1, n)
        y = bv.truth(x) + rgl.normal(0, bv.SIGMA, n)
        m = LinearRegression(fit_intercept=False).fit(design(x, degree), y)
        assert np.allclose(m.coef_, bv.poly_fit(degree)(x, y).coef, atol=1e-7)
        out["legendre"].append({"x": x.tolist(), "y": y.tolist(), "degree": degree,
                                "coef": m.coef_.tolist(), "pred": m.predict(design(gx, degree)).tolist()})
    out["legendre_grid"] = gx.tolist()
    P = np.array([bv.poly_fit(3)(*bv.draw(rgl, 20))(gx) for _ in range(40)])
    b2, var = bv.decompose(P, grid=gx)
    out["bv_decompose"] = {"P": P.tolist(), "grid": gx.tolist(), "bias2": b2, "variance": var}

    # AdaBoost (SAMME, the only algorithm of sklearn 1.9) over decision stumps
    # on the train part of each page data set, rounded as the page rounds it.
    # estimator_weights_ are alpha_t = ln((1 - eps) / eps), twice the rho_t of
    # the note for two classes; the sign of the summed vote is the same. The
    # "stump" case is separable by one threshold, so the first stump is perfect
    # and sklearn stops there with weight 1.0.
    from sklearn.ensemble import AdaBoostClassifier
    out["ada"] = []
    sets = {}
    for name in ["moons", "circles", "xor", "linear"]:
        Xd, yd = fk.dataset(name)
        Xa, _, ya, _ = fk.split(Xd, yd)
        sets[name] = (Xa.round(4), ya)
    Xs = sets["moons"][0]
    sets["stump"] = (Xs, (Xs[:, 0] > 0.1).astype(int))
    for name, (Xa, ya) in sets.items():
        ga = grid(Xa, 30)
        m = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=0),
                               n_estimators=60, random_state=0).fit(Xa, ya)
        stages = list(m.staged_decision_function(Xa))
        out["ada"].append({
            "ds": name, "X": Xa.tolist(), "y": ya.tolist(), "grid": ga.tolist(),
            "alpha": m.estimator_weights_.tolist(), "eps": m.estimator_errors_.tolist(),
            "n_fitted": len(m.estimators_),
            "decision": m.decision_function(ga).tolist(),
            "alpha_sum": float(m.estimator_weights_.sum()),
            "pred": m.predict(ga).tolist(),
            "staged_train_pred": [(s > 0).astype(int).tolist() for s in stages[:10]]})

    out["mlp"] = mlp_fixtures()
    out["opt"] = opt_fixtures()
    out["importance"] = importance_fixtures()
    out["lime"] = lime_fixtures()
    out["shap"] = shap_fixtures()
    out["softmax"] = softmax_fixtures()
    out["distill"] = distill_fixtures()

    (HERE / "fixtures.json").write_text(json.dumps(out))
    print("fixtures.json written")


if __name__ == "__main__":
    import warnings

    from sklearn.exceptions import ConvergenceWarning

    # A reference that stopped short of its optimum is not a reference.
    warnings.simplefilter("error", ConvergenceWarning)
    main()
