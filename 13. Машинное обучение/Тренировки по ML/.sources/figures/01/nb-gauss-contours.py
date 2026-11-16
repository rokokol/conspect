"""Class-conditional Gaussian densities of GaussianNB: axis-aligned ellipses over the zones."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402
from sklearn.naive_bayes import GaussianNB  # noqa: E402

import figkit as fk  # noqa: E402

fig, axes = fk.subplots(1, 2, size=(8.6, 4.0))
for ax, d in zip(axes, ["blobs3", "moons"]):
    X, y = fk.dataset(d)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    m = GaussianNB().fit(Xtr, ytr)
    fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte, title=d)
    n = len(m.classes_)
    for k in range(n):
        c = fk.CLASS_COLORS[k] if n == 2 else fk.CATEGORICAL[k]
        for r, ls in [(1, "-"), (2, "--")]:
            sd = np.sqrt(m.var_[k])
            ax.add_patch(Ellipse(m.theta_[k], 2 * r * sd[0], 2 * r * sd[1], fill=False,
                                 ec=c, lw=1.6, ls=ls, zorder=4))
        ax.plot(*m.theta_[k], marker="+", color=fk.TEXT, ms=9, mew=1.6, zorder=5)
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "nb-gauss-contours.png")
