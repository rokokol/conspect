"""Degree-15 polynomial regression at growing lambda: Ridge on the top row, LASSO on the bottom."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
import poly_demo as pd  # noqa: E402

LAMS = [1e-9, 1e-4, 1e-2, 1e0, 1e2]
grid = np.linspace(0, 1, 300)[:, None]

fig, axes = fk.subplots(2, len(LAMS), size=(3.0 * len(LAMS), 5.6))
for i, kind in enumerate(("ridge", "lasso")):
    for j, lam in enumerate(LAMS):
        ax = axes[i, j]
        m = pd.fit(kind, lam)
        print(kind, lam, "train", round(pd.mse(m, pd.Xtr, pd.ytr), 3), "test", round(pd.mse(m, pd.Xte, pd.yte), 3),
              "nonzero", m.n_nonzero)
        ax.plot(grid, np.sin(2 * np.pi * grid), color=fk.TEXT_2, lw=1, ls="--")
        ax.plot(grid, m.predict(grid), color=fk.RED, lw=2)
        ax.scatter(pd.Xtr, pd.ytr, s=26, color=fk.BLUE, edgecolor="white", zorder=3)
        ax.scatter(pd.Xte, pd.yte, s=26, facecolor="white", edgecolor=fk.BLUE, zorder=3)
        ax.set_ylim(-2.5, 2.5)
        ax.set_xticks([])
        ax.set_yticks([])
        lines = [f"train {fk.num(pd.mse(m, pd.Xtr, pd.ytr), 3)}", f"test {fk.num(pd.mse(m, pd.Xte, pd.yte), 3)}"]
        if kind == "lasso":
            lines.append(f"ненулевых весов: {m.n_nonzero}")
        ax.text(0.97, 0.97, "\n".join(lines), transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
        if i == 0:
            ax.set_title(f"$\\lambda=10^{{{int(round(np.log10(lam)))}}}$")
    axes[i, 0].set_ylabel("Ridge (L2)" if kind == "ridge" else "LASSO (L1)")
fig.tight_layout()
fk.save(fig, fk.attachments(2) / "reg-poly-lambda-grid.png")
