"""Exact coefficient paths of Ridge and LASSO on the scikit-learn diabetes data, against the shrinkage of the L1 norm.

The LASSO path is piecewise linear in the penalty, and lars_path returns its exact corners, so no coordinate
descent (and no convergence question) is involved; Ridge is computed in closed form through the SVD.
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import lars_path
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

data = load_diabetes()
X = StandardScaler().fit_transform(data.data)
y = data.target - data.target.mean()
names = list(data.feature_names)

U, s, Vt = np.linalg.svd(X, full_matrices=False)
w_ols = Vt.T @ ((U.T @ y) / s)
norm_ols = abs(w_ols).sum()

# Ridge: w = V diag(s / (s^2 + lam)) U^T y
lams = np.logspace(-3, 6, 400)
ridge_w = np.array([Vt.T @ (s / (s**2 + l) * (U.T @ y)) for l in lams])
ridge_s = abs(ridge_w).sum(1) / norm_ols

# LASSO: exact corners of the path; straight segments between them are exact too
_, _, coefs = lars_path(X, y, method="lasso")
lasso_w = coefs.T
lasso_s = abs(lasso_w).sum(1) / norm_ols

top = [names.index(n) for n in ("bmi", "s5", "bp", "s3")]
colors = dict(zip(top, [fk.CATEGORICAL[0], fk.CATEGORICAL[1], fk.CATEGORICAL[2], fk.ACCENT]))

fig, axes = fk.subplots(1, 2, size=(10.2, 4.2), sharey=True)
for ax, sh, W, title in ((axes[0], ridge_s, ridge_w, "Ridge"), (axes[1], lasso_s, lasso_w, "LASSO")):
    for k in range(W.shape[1]):
        if k in colors:
            ax.plot(sh, W[:, k], color=colors[k], lw=2.2, zorder=3)
        else:
            ax.plot(sh, W[:, k], color=fk.TEXT_2, alpha=0.45, lw=1.1, zorder=2)
    for k in top:
        ax.annotate(names[k], (1.0, w_ols[k]), xytext=(4, 0), textcoords="offset points", fontsize=8,
                    color=colors[k], va="center")
    ax.axhline(0, color=fk.TEXT_2, lw=0.8)
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("$\\|\\hat w(\\lambda)\\|_1\\,/\\,\\|\\hat w_{\\mathrm{МНК}}\\|_1$ (справа $\\lambda\\to0$)")
    ax.set_title(title)
    ax.grid(True, axis="y")
axes[0].set_ylabel("вес признака")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "reg-paths-ridge-lasso.png")
