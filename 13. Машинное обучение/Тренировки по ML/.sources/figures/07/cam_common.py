"""A tiny convolutional network written out by hand in numpy, for CAM and Grad-CAM on synthetic images.

Images are 16x16: noise, one target object that decides the class (a cross, a ring or two diagonals, all 5x5)
and one distractor (a dim 3x3 blob, the same in both classes). One conv layer 3x3 with K filters and ReLU gives the maps
A of shape (K, 14, 14). Two heads on top of A:

* "gap": global average pooling, then one linear layer. This is the architecture CAM needs.
* "flat": 2x2 max pooling, flatten, one linear layer. CAM does not apply, Grad-CAM does.

The number of epochs is chosen on a validation part, the test part is only scored. Gradients are written by hand and
checked against central differences in check_gradients().
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

SIZE, K, KS = 16, 8, 3
OUT = SIZE - KS + 1
NOISE = 0.1
CONV_BIAS = -1.0
CLASSES = ["крест", "кольцо", "диагонали"]
NC = len(CLASSES)


def _cross():
    p = np.zeros((5, 5))
    p[2, :] = 1
    p[:, 2] = 1
    return p


def _ring():
    p = np.ones((5, 5))
    p[1:-1, 1:-1] = 0
    return p


def _diag():
    return np.eye(5) + np.eye(5)[::-1]


PATTERNS = [_cross(), _ring(), np.minimum(_diag(), 1)]


def make_images(n, rng):
    """n images, labels alternate at random; also the boxes of the target and the distractor."""
    X = rng.normal(0, NOISE, (n, SIZE, SIZE))
    y = rng.integers(0, NC, n)
    boxes = np.zeros((n, 2, 2), dtype=int)
    for i in range(n):
        while True:
            ty, tx = rng.integers(0, SIZE - 5 + 1, 2)
            dy, dx = rng.integers(0, SIZE - 3 + 1, 2)
            if abs(ty + 2 - (dy + 1)) >= 4 or abs(tx + 2 - (dx + 1)) >= 4:
                break
        X[i, ty:ty + 5, tx:tx + 5] += PATTERNS[y[i]]
        X[i, dy:dy + 3, dx:dx + 3] += 0.6
        boxes[i] = [[ty, tx], [dy, dx]]
    return X, y, boxes


def split_data():
    rng = np.random.default_rng(fk.SEED)
    parts = {name: make_images(n, rng) for name, n in [("train", 600), ("val", 200), ("test", 200)]}
    return parts


class Net:
    def __init__(self, head, rng):
        self.head = head
        self.Wc = rng.normal(0, np.sqrt(2 / (KS * KS)), (K, KS, KS))
        # Fixed negative threshold, never trained: with a free bias some filters fire on pure noise
        # and the classifier takes the background as evidence for a class.
        self.bc = np.full(K, CONV_BIAS)
        fan = K if head == "gap" else K * (OUT // 2) ** 2
        self.Wo = rng.normal(0, np.sqrt(1 / fan), (NC, fan))
        self.bo = np.zeros(NC)

    PARAMS = ("Wc", "bc", "Wo", "bo")

    def params(self):
        return {k: getattr(self, k) for k in self.PARAMS}

    def conv(self, X):
        patches = sliding_window_view(X, (KS, KS), axis=(1, 2))
        pre = np.einsum("nijab,kab->nkij", patches, self.Wc) + self.bc[None, :, None, None]
        return pre, patches

    def forward(self, X):
        pre, patches = self.conv(X)
        A = np.maximum(pre, 0)
        if self.head == "gap":
            feat = A.mean((2, 3))
            pool_arg = None
        else:
            n = A.shape[0]
            blocks = A.reshape(n, K, OUT // 2, 2, OUT // 2, 2).transpose(0, 1, 2, 4, 3, 5).reshape(n, K, OUT // 2, OUT // 2, 4)
            pool_arg = blocks.argmax(-1)
            feat = np.take_along_axis(blocks, pool_arg[..., None], -1)[..., 0].reshape(n, -1)
        logits = feat @ self.Wo.T + self.bo
        return {"pre": pre, "patches": patches, "A": A, "feat": feat, "pool_arg": pool_arg, "logits": logits}

    def dA_from_dfeat(self, cache, dfeat):
        """Gradient wrt the maps A (after ReLU) given the gradient wrt the head's input features."""
        n = dfeat.shape[0]
        if self.head == "gap":
            return np.broadcast_to(dfeat[:, :, None, None] / (OUT * OUT), (n, K, OUT, OUT)).copy()
        h = OUT // 2
        onehot = np.eye(4)[cache["pool_arg"]]
        blocks = onehot * dfeat.reshape(n, K, h, h)[..., None]
        return blocks.reshape(n, K, h, h, 2, 2).transpose(0, 1, 2, 4, 3, 5).reshape(n, K, OUT, OUT)

    def score_grad_A(self, cache, c):
        """d y^c / d A for every image: the class score (logit) c, not the probability."""
        dfeat = np.broadcast_to(self.Wo[c], cache["feat"].shape).copy()
        return self.dA_from_dfeat(cache, dfeat)

    def backprop_conv(self, cache, dA, want_input=False):
        dpre = dA * (cache["pre"] > 0)
        dWc = np.einsum("nkij,nijab->kab", dpre, cache["patches"])
        dbc = dpre.sum((0, 2, 3))
        dX = None
        if want_input:
            n = dpre.shape[0]
            dX = np.zeros((n, SIZE, SIZE))
            for a in range(KS):
                for b in range(KS):
                    dX[:, a:a + OUT, b:b + OUT] += np.einsum("nkij,k->nij", dpre, self.Wc[:, a, b])
        return dWc, dbc, dX

    def loss_and_grads(self, X, y):
        cache = self.forward(X)
        z = cache["logits"] - cache["logits"].max(1, keepdims=True)
        p = np.exp(z) / np.exp(z).sum(1, keepdims=True)
        n = len(y)
        loss = -np.log(p[np.arange(n), y]).mean()
        dz = p.copy()
        dz[np.arange(n), y] -= 1
        dz /= n
        dWo = dz.T @ cache["feat"]
        dbo = dz.sum(0)
        dfeat = dz @ self.Wo
        dWc, dbc, _ = self.backprop_conv(cache, self.dA_from_dfeat(cache, dfeat))
        return loss, {"Wc": dWc, "bc": dbc, "Wo": dWo, "bo": dbo}

    def predict(self, X):
        return self.forward(X)["logits"].argmax(1)

    def val_loss(self, X, y):
        cache = self.forward(X)
        z = cache["logits"] - cache["logits"].max(1, keepdims=True)
        p = np.exp(z) / np.exp(z).sum(1, keepdims=True)
        return -np.log(p[np.arange(len(y)), y]).mean()


def train(head, parts, epochs=200, lr=0.01, batch=32):
    """Adam; the epoch with the lowest validation loss is kept, test is untouched."""
    rng = np.random.default_rng(fk.SEED + 1)
    net = Net(head, rng)
    Xtr, ytr, _ = parts["train"]
    Xva, yva, _ = parts["val"]
    m = {k: np.zeros_like(v) for k, v in net.params().items()}
    v2 = {k: np.zeros_like(v) for k, v in net.params().items()}
    best, best_state, step, history = np.inf, None, 0, []
    for epoch in range(epochs):
        order = rng.permutation(len(ytr))
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            _, g = net.loss_and_grads(Xtr[idx], ytr[idx])
            step += 1
            for k, p in net.params().items():
                if k == "bc":
                    continue
                m[k] = 0.9 * m[k] + 0.1 * g[k]
                v2[k] = 0.999 * v2[k] + 0.001 * g[k] ** 2
                p -= lr * (m[k] / (1 - 0.9**step)) / (np.sqrt(v2[k] / (1 - 0.999**step)) + 1e-8)
        vl = net.val_loss(Xva, yva)
        history.append(vl)
        if vl < best:
            best, best_epoch = vl, epoch
            best_state = {k: p.copy() for k, p in net.params().items()}
    for k, p in net.params().items():
        p[...] = best_state[k]
    return net, best_epoch, history


def check_gradients(head, parts):
    """Central differences against the hand-written gradient of the loss and of a class score wrt the input and wrt A."""
    rng = np.random.default_rng(5)
    net = Net(head, rng)
    net.bc[:] = 0.1  # most cells active, so the check reaches the whole chain
    X, y, _ = parts["train"]
    X, y = X[:6], y[:6]
    _, g = net.loss_and_grads(X, y)
    worst = 0.0
    for name in Net.PARAMS:
        p = net.params()[name]
        flat = p.reshape(-1)
        for i in rng.choice(flat.size, min(5, flat.size), replace=False):
            old = flat[i]
            flat[i] = old + 1e-6
            lp, _ = net.loss_and_grads(X, y)
            flat[i] = old - 1e-6
            lm, _ = net.loss_and_grads(X, y)
            flat[i] = old
            worst = max(worst, abs((lp - lm) / 2e-6 - g[name].reshape(-1)[i]))
    # saliency: y^c wrt the pixels
    cache = net.forward(X)
    dA = net.score_grad_A(cache, 1)
    _, _, dX = net.backprop_conv(cache, dA, want_input=True)
    for n in range(2):
        for _ in range(4):
            i, j = rng.integers(0, SIZE, 2)
            Xp, Xm = X.copy(), X.copy()
            Xp[n, i, j] += 1e-6
            Xm[n, i, j] -= 1e-6
            num = (net.forward(Xp)["logits"][n, 1] - net.forward(Xm)["logits"][n, 1]) / 2e-6
            worst = max(worst, abs(num - dX[n, i, j]))
    # gradient wrt A: perturb a pre-activation-positive cell directly
    A = cache["A"].copy()
    n, k, i, j = 0, 0, 3, 3
    def score_from_A(Aset):
        if head == "gap":
            feat = Aset.mean((2, 3))
        else:
            nn_ = Aset.shape[0]
            bl = Aset.reshape(nn_, K, OUT // 2, 2, OUT // 2, 2).transpose(0, 1, 2, 4, 3, 5).reshape(nn_, K, OUT // 2, OUT // 2, 4)
            feat = bl.max(-1).reshape(nn_, -1)
        return (feat @ net.Wo.T + net.bo)[:, 1]
    # a cell at zero ties with its neighbours in a max-pool window, and the gradient there is a subgradient
    cells = [tuple(c) for c in np.argwhere(A[0] > 1e-3)[::7]]
    assert len(cells) >= 10
    for (k, i, j) in cells:
        Ap, Am = A.copy(), A.copy()
        Ap[n, k, i, j] += 1e-6
        Am[n, k, i, j] -= 1e-6
        num = (score_from_A(Ap)[n] - score_from_A(Am)[n]) / 2e-6
        worst = max(worst, abs(num - dA[n, k, i, j]))
    return worst


def grad_cam(net, cache, c):
    """Grad-CAM for class score c: alpha_k = mean of d y^c / d A^k over space, L = ReLU(sum_k alpha_k A^k)."""
    dA = net.score_grad_A(cache, c)
    alpha = dA.mean((2, 3))
    raw = np.einsum("nk,nkij->nij", alpha, cache["A"])
    return np.maximum(raw, 0), raw, alpha


def cam(net, cache, c):
    """CAM for the gap head: M_c = sum_k w_k^c A^k. No ReLU in the original definition."""
    assert net.head == "gap"
    return np.einsum("k,nkij->nij", net.Wo[c], cache["A"])


def box_shares(M, boxes):
    """Share of the positive mass of maps M (n, 14, 14) inside the target box and inside the distractor box.

    A map cell (a, b) looks at the pixels a..a+2, so its centre is the pixel (a+1, b+1).
    """
    a = np.arange(OUT)[:, None] + 1
    b = np.arange(OUT)[None, :] + 1
    out = []
    for m, ((ty, tx), (dy, dx)) in zip(np.maximum(M, 0), boxes):
        inside_t = (a >= ty) & (a < ty + 5) & (b >= tx) & (b < tx + 5)
        inside_d = (a >= dy) & (a < dy + 3) & (b >= dx) & (b < dx + 3)
        total = max(m.sum(), 1e-12)
        out.append((m[inside_t].sum() / total, m[inside_d].sum() / total))
    return np.mean(out, 0)


def show_image(ax, image, box=None):
    ax.imshow(image, cmap="gray_r", vmin=-0.3, vmax=1.3, extent=(0, SIZE, SIZE, 0), interpolation="nearest")
    if box is not None:
        draw_box(ax, box)
    ax.set_xticks([])
    ax.set_yticks([])


def draw_box(ax, box):
    (ty, tx), _ = box
    ax.add_patch(plt.Rectangle((tx, ty), 5, 5, fill=False, ec=fk.ACCENT, lw=0.9, ls=(0, (3, 2)), zorder=5))


def show_map(ax, image, M, *, box=None, signed=False, scale=None, on_pixels=False):
    """Heat map M over the image. Map cells (14x14) sit at pixel centres 1.5..14.5; pixel maps (16x16) fill the image."""
    gray = plt.cm.gray_r(np.clip((image + 0.3) / 1.6, 0, 1))
    ax.imshow(gray, extent=(0, SIZE, SIZE, 0), interpolation="nearest")
    lim = (1, OUT + 1) if not on_pixels else (0, SIZE)
    extent = (lim[0], lim[1], lim[1], lim[0])
    top = scale if scale is not None else max(np.abs(M).max(), 1e-12)
    if signed:
        rgba = plt.get_cmap("ddlc_div")(0.5 + 0.5 * np.clip(M / top, -1, 1))
        rgba[..., 3] = 0.25 + 0.7 * np.abs(np.clip(M / top, -1, 1))
    else:
        v = np.clip(M / top, 0, 1)
        rgba = plt.get_cmap("ddlc_seq")(v)
        rgba[..., 3] = 0.1 + 0.85 * v
    ax.imshow(rgba, extent=extent, interpolation="nearest")
    ax.set_xlim(0, SIZE)
    ax.set_ylim(SIZE, 0)
    if box is not None:
        draw_box(ax, box)
    ax.set_xticks([])
    ax.set_yticks([])


def pixel_box_share(S, boxes):
    """Mean share of a pixel map S (n, 16, 16) inside the 5x5 target box; a uniform map gives 25/256."""
    out = []
    for s, ((ty, tx), _) in zip(S, boxes):
        out.append(s[ty:ty + 5, tx:tx + 5].sum() / max(s.sum(), 1e-12))
    return float(np.mean(out))


def box_cells(boxes):
    """Number of map cells whose centre lies inside the target box, per image."""
    a = np.arange(OUT)[:, None] + 1
    b = np.arange(OUT)[None, :] + 1
    return np.array([((a >= ty) & (a < ty + 5) & (b >= tx) & (b < tx + 5)).sum() for (ty, tx), _ in boxes])


def saliency(net, cache, c):
    """Simonyan saliency: |d y^c / d pixel|."""
    _, _, dX = net.backprop_conv(cache, net.score_grad_A(cache, c), want_input=True)
    return np.abs(dX)
