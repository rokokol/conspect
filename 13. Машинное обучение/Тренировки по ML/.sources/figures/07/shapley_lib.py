"""Exact Shapley values by enumerating coalitions, and E[f | x_S] for sklearn tree ensembles.

No shap package is needed for a small number of features: with M features there are 2^M coalitions, and M = 8 is 256.

The tree rule is the one on lecture slide 27: a feature outside S is "missing", so the walk goes into both children and the
answers are averaged with the weights n_child / n_node (training objects that fell into each child).
"""
import itertools
import math

import numpy as np


def coalitions(m):
    """All 2^m coalitions as a boolean matrix [2^m, m]; row index is the bitmask (bit j = feature j)."""
    return ((np.arange(2**m)[:, None] >> np.arange(m)) & 1).astype(bool)


def shapley_weights(m):
    """Weight |S|!(m-|S|-1)!/m! for every coalition size |S| = 0 .. m-1."""
    return np.array([math.factorial(s) * math.factorial(m - s - 1) / math.factorial(m) for s in range(m)])


def shapley_from_values(v, m):
    """Shapley values from the table v[mask] = value of the coalition (coalition formula).

    v has shape [2^m] or [2^m, n_objects]; the result has shape [m] or [m, n_objects].
    """
    masks = coalitions(m)
    size = masks.sum(1)
    w = shapley_weights(m)
    out = []
    for i in range(m):
        without = np.flatnonzero(~masks[:, i])
        with_i = without | (1 << i)
        out.append(np.tensordot(w[size[without]], v[with_i] - v[without], axes=(0, 0)))
    return np.array(out)


def shapley_by_orders(v, m):
    """The same values through all m! orders: the average of the marginal gains along the order (permutation formula)."""
    v = np.asarray(v, float)
    phi = np.zeros((m,) + v.shape[1:])
    for order in itertools.permutations(range(m)):
        mask = 0
        for i in order:
            phi[i] += v[mask | (1 << i)] - v[mask]
            mask |= 1 << i
    return phi / math.factorial(m)


def _leaf_paths(tree):
    """For one fitted sklearn tree: per leaf a list of steps (feature, threshold, goes_left, n_child / n_node) and the leaf value."""
    t = tree.tree_
    out = []

    def walk(node, path):
        if t.children_left[node] == -1:
            out.append((path, t.value[node].ravel()[0]))
            return
        f, thr = t.feature[node], t.threshold[node]
        n = t.weighted_n_node_samples[node]
        for child, left in ((t.children_left[node], True), (t.children_right[node], False)):
            walk(child, path + [(f, thr, left, t.weighted_n_node_samples[child] / n)])

    walk(0, [])
    return out


def tree_coalition_values(trees, scale, base, X):
    """E[f | x_S] for f = base + scale * sum(trees), every coalition S, every object: array [2^m, n].

    A leaf contributes its value times, along its path, 1 or 0 (feature in S: does x go this way?) or the training
    fraction (feature not in S).
    """
    n, m = X.shape
    masks = coalitions(m)
    total = np.zeros((2**m, n))
    for tree in trees:
        for path, value in _leaf_paths(tree):
            prod = np.ones((2**m, n))
            for f, thr, left, frac in path:
                goes = (X[:, f] <= thr) if left else (X[:, f] > thr)
                prod *= np.where(masks[:, f][:, None], goes[None, :].astype(float), frac)
            total += value * prod
    return base + scale * total


def gbr_coalition_values(model, X):
    """E[f | x_S] for a fitted GradientBoostingRegressor (squared error, subsample=1: node counts are training counts)."""
    trees = [est[0] for est in model.estimators_]
    base = float(model.init_.constant_.ravel()[0])
    return tree_coalition_values(trees, model.learning_rate, base, X)


def interventional_values(predict, X, background):
    """v(S) with the other features taken from a background sample and averaged: array [2^m, n] (any model, brute force)."""
    n, m = X.shape
    masks = coalitions(m)
    out = np.zeros((2**m, n))
    for k, mask in enumerate(masks):
        for j in range(n):
            Z = np.where(mask[None, :], X[j][None, :], background)
            out[k, j] = predict(Z).mean()
    return out


def recursive_tree_value(tree, x, S):
    """Direct recursion of slide 27 for one tree: independent check of the leaf-product implementation."""
    t = tree.tree_

    def go(node):
        if t.children_left[node] == -1:
            return t.value[node].ravel()[0]
        f = t.feature[node]
        l, r = t.children_left[node], t.children_right[node]
        if f in S:
            return go(l) if x[f] <= t.threshold[node] else go(r)
        n = t.weighted_n_node_samples[node]
        return (t.weighted_n_node_samples[l] * go(l) + t.weighted_n_node_samples[r] * go(r)) / n

    return go(0)
