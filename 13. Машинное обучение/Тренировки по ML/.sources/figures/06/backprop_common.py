"""Hand-written backprop shared by the backprop figures and their numerical check.

Two models, both from lecture 6:
- the computational graph of slide 29, sigma(x0*w0 + x1*w1 + w2), node by node;
- a one-hidden-layer network with sigmoid units and binary cross-entropy,
  in the matrix form derived in the note "Обратное распространение ошибки".
"""
import numpy as np

# Slide 29: inputs and weights of the graph.
SLIDE29 = {"x0": 2.0, "w0": -1.0, "x1": -3.0, "w1": -2.0, "w2": -3.0}


def graph_forward(v):
    """Forward pass of slide 29; returns every intermediate value by node name."""
    n = {}
    n["m0"] = v["x0"] * v["w0"]
    n["m1"] = v["x1"] * v["w1"]
    n["s0"] = n["m0"] + n["m1"]
    n["s"] = n["s0"] + v["w2"]
    n["neg"] = -1.0 * n["s"]
    n["e"] = np.exp(n["neg"])
    n["q"] = n["e"] + 1.0
    n["out"] = 1.0 / n["q"]
    return n


def graph_backward(v, n):
    """Backward pass node by node: each node multiplies the upstream gradient by its local one."""
    g = {"out": 1.0}
    g["q"] = g["out"] * (-1.0 / n["q"] ** 2)      # d(1/q)/dq = -1/q^2
    g["e"] = g["q"] * 1.0                          # d(e+1)/de = 1
    g["neg"] = g["e"] * np.exp(n["neg"])          # d(exp a)/da = exp a
    g["s"] = g["neg"] * (-1.0)                     # d(-s)/ds = -1
    g["s0"] = g["s"]                               # a sum copies the gradient
    g["w2"] = g["s"]
    g["m0"] = g["s0"]
    g["m1"] = g["s0"]
    g["x0"] = g["m0"] * v["w0"]                    # a product swaps its inputs
    g["w0"] = g["m0"] * v["x0"]
    g["x1"] = g["m1"] * v["w1"]
    g["w1"] = g["m1"] * v["x1"]
    return g


def sigmoid(a):
    return 1.0 / (1.0 + np.exp(-a))


def mlp_forward(params, X):
    """X is n x d; returns the cache of the forward pass.

    Z1 = X W1^T + b1, H = sigma(Z1), z2 = H w2 + b2, p = sigma(z2).
    """
    W1, b1, w2, b2 = params
    Z1 = X @ W1.T + b1
    H = sigmoid(Z1)
    z2 = H @ w2 + b2
    p = sigmoid(z2)
    return {"X": X, "Z1": Z1, "H": H, "z2": z2, "p": p}


def bce(p, y):
    """Mean binary cross-entropy."""
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def mlp_loss(params, X, y):
    return bce(mlp_forward(params, X)["p"], y)


def mlp_backward(params, cache, y, *, broken=None):
    """Gradients of the mean BCE by the matrix formulas of the note.

    broken names one deliberate defect, used only to prove that the
    numerical check can fail: "no_sigma_prime" drops the factor sigma'(Z1),
    "wrong_sign" takes y - p for dL/dz2, "no_mean" forgets the 1/n.
    """
    W1, b1, w2, b2 = params
    n = len(y)
    d_z2 = (cache["p"] - y) / n                    # dL/dz2 = (p - y)/n
    if broken == "wrong_sign":
        d_z2 = -d_z2
    if broken == "no_mean":
        d_z2 = d_z2 * n
    g_w2 = cache["H"].T @ d_z2                     # dL/dw2 = H^T d_z2
    g_b2 = d_z2.sum()
    d_H = np.outer(d_z2, w2)                       # dL/dH = d_z2 w2^T
    s_prime = cache["H"] * (1 - cache["H"])
    d_Z1 = d_H if broken == "no_sigma_prime" else d_H * s_prime
    g_W1 = d_Z1.T @ cache["X"]                     # dL/dW1 = d_Z1^T X
    g_b1 = d_Z1.sum(0)
    return [g_W1, g_b1, g_w2, np.array(g_b2)]


def numeric_grad(f, params, eps=1e-6):
    """Central finite differences of f over every entry of every parameter array."""
    out = []
    for k, P in enumerate(params):
        P = np.asarray(P, float)
        G = np.zeros_like(P)
        for idx in np.ndindex(P.shape):
            plus = [np.array(q, float, copy=True) for q in params]
            minus = [np.array(q, float, copy=True) for q in params]
            plus[k][idx] += eps
            minus[k][idx] -= eps
            G[idx] = (f(plus) - f(minus)) / (2 * eps)
        out.append(G)
    return out


def rel_error(a, b):
    a, b = np.concatenate([np.ravel(x) for x in a]), np.concatenate([np.ravel(x) for x in b])
    return float(np.max(np.abs(a - b)) / max(np.max(np.abs(a)), np.max(np.abs(b)), 1e-12))
