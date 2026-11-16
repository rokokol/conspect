"""Train and test error of degree-15 polynomial regression against lambda; the choice is marked by cross-validation."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
import poly_demo as pd  # noqa: E402

lams = np.logspace(-9, 2, 45)
fig, axes = fk.subplots(1, 2, size=(9.2, 3.6), sharey=True)
for ax, kind, title in ((axes[0], "ridge", "Ridge (L2)"), (axes[1], "lasso", "LASSO (L1)")):
    tr, te, va = [], [], []
    for lam in lams:
        m = pd.fit(kind, lam)
        tr.append(pd.mse(m, pd.Xtr, pd.ytr))
        te.append(pd.mse(m, pd.Xte, pd.yte))
        va.append(pd.cv_mse(kind, lam))
    b = fk.complexity_curve(ax, lams, tr, te, val=va, better="min", xlabel="$\\lambda$", ylabel="MSE", log=True)
    ax.set_yscale("log")
    ax.set_ylim(1e-2, 3e1)
    ax.set_title(title)
    print(kind, "lambda by validation", lams[b], "test there", round(te[b], 3), "best test", round(min(te), 3),
          "at", lams[int(np.argmin(te))])
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "reg-poly-lambda-curve.png")
