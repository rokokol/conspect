"""Three hidden neurons on circles, the setting of the Playground demo in lecture 6 (1:47:47).

nn-three-logregs.png: a sigmoid layer is three logistic regressions; each hidden
neuron's output over the plane, then the output neuron that weighs them.
nn-tanh-vs-relu.png: tanh gives a rounded triangle, ReLU a polygon whose corners
lie on the neurons' zero lines.
nn-seeds.png: the same ReLU architecture from four random starts, no selection.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import nn_common as nc  # noqa: E402

OUT = fk.attachments(6)
X, y = fk.dataset("circles")
Xtr, Xte, ytr, yte = fk.split(X, y)
allX = np.vstack([Xtr, Xte])
lo, hi = allX.min(0) - 0.6, allX.max(0) + 0.6
BOX = (lo[0], hi[0], lo[1], hi[1])


def frame(ax):
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(fk.GRIDC)


# Three logistic regressions and one more on top.
sig = nc.best_of(lambda s: nc.mlp([3], "logistic", seed=s), Xtr, ytr)
xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], 300), np.linspace(lo[1], hi[1], 300))
grid = np.c_[xx.ravel(), yy.ravel()]
Hgrid = nc.hidden_activations(sig, grid)
fig, axes = fk.subplots(1, 4, size=(13.2, 3.6))
for j in range(3):
    ax = axes[j]
    ax.contourf(xx, yy, Hgrid[:, j].reshape(xx.shape), levels=np.linspace(0, 1, 11), cmap="ddlc_seq",
                vmin=0, vmax=1)
    ax.scatter(Xtr[:, 0], Xtr[:, 1], s=6, c=[fk.CLASS_COLORS[int(k)] for k in ytr], linewidths=0)
    # The line h_j = 1/2 is the zero line w_j^T x + b_j = 0.
    nc.hidden_lines(ax, sig, BOX, only=j)
    frame(ax)
    v = sig.coefs_[1][j, 0]
    ax.set_title(f"нейрон $h_{j + 1}$, вес на выходе {fk.num(v, '+.1f')}")
fk.plot_decision(axes[3], sig, Xtr, ytr, X_test=Xte, y_test=yte)
nc.hidden_lines(axes[3], sig, BOX)
frame(axes[3])
axes[3].set_title("выход $\\sigma(v_1h_1+v_2h_2+v_3h_3+c)$")
fig.tight_layout()
fk.save(fig, OUT / "nn-three-logregs.png")
print("sigmoid 3: train", sig.score(Xtr, ytr), "test", round(sig.score(Xte, yte), 3),
      "output weights", np.round(sig.coefs_[1][:, 0], 2))

# tanh against ReLU with the same three neurons.
fig, axes = fk.subplots(1, 2, size=(7.6, 3.9))
for ax, act in zip(axes, ("tanh", "relu")):
    m = nc.best_of(lambda s, a=act: nc.mlp([3], a, seed=s), Xtr, ytr)
    fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte)
    nc.hidden_lines(ax, m, BOX)
    frame(ax)
    ax.set_title(f"3 нейрона, {'tanh' if act == 'tanh' else 'ReLU'}")
    print(act, "train", m.score(Xtr, ytr), "test", round(m.score(Xte, yte), 3),
          "cells crossed by the boundary", nc.crossed_cells(m, BOX))
    if act == "relu":
        # Inside each cell of the three lines the logit is affine: check on random points of one cell.
        rng = np.random.default_rng(fk.SEED)
        P = rng.uniform(lo, hi, size=(4000, 2))
        Z = P @ m.coefs_[0] + m.intercepts_[0]
        pattern = (Z > 0).astype(int) @ np.array([1, 2, 4])
        cells = 0
        for c in np.unique(pattern):
            Q = P[pattern == c]
            if len(Q) < 10:
                continue
            d = nc.logit(m, Q)
            A = np.c_[Q, np.ones(len(Q))]
            resid = d - A @ np.linalg.lstsq(A, d, rcond=None)[0]
            assert np.max(np.abs(resid)) < 1e-6, (c, np.max(np.abs(resid)))
            cells += 1
        print("relu: logit is affine in each of", cells, "cells holding at least 10 of 4000 random points")
fig.tight_layout()
fk.save(fig, OUT / "nn-tanh-vs-relu.png")

# Same architecture, four random starts, no selection at all.
fig, axes = fk.subplots(1, 4, size=(13.2, 3.5))
for s, ax in enumerate(axes):
    m = nc.mlp([3], "relu", seed=s).fit(Xtr, ytr)
    fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte)
    nc.hidden_lines(ax, m, BOX)
    frame(ax)
    ax.set_title(f"старт {s + 1}")
    active = ((Xtr @ m.coefs_[0] + m.intercepts_[0]) > 0).sum(0)
    p = m.predict_proba(Xtr)[:, 1]
    print("seed", s, "loss", round(m.loss_, 3), "train", round(m.score(Xtr, ytr), 3),
          "points where each neuron is open", active, "p range", round(p.min(), 3), round(p.max(), 3),
          "cells crossed by the boundary", nc.crossed_cells(m, BOX))
fig.tight_layout()
fk.save(fig, OUT / "nn-seeds.png")
