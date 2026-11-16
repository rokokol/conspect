"""Level lines of min, arithmetic mean and F1 in the (precision, recall) plane, and F_beta against recall."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

p, r = np.meshgrid(np.linspace(0.001, 1, 400), np.linspace(0.001, 1, 400))
levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
funcs = [
    ("min(P, R)", np.minimum(p, r)),
    ("(P + R) / 2", (p + r) / 2),
    ("F1 = 2PR / (P + R)", 2 * p * r / (p + r)),
]
fig, axes = fk.subplots(1, 4, size=(15.2, 3.9))
for ax, (name, z) in zip(axes[:3], funcs):
    cs = ax.contourf(p, r, z, levels=np.linspace(0, 1, 11), cmap="ddlc_seq")
    cl = ax.contour(p, r, z, levels=levels, colors=fk.TEXT, linewidths=0.6)
    ax.clabel(cl, fmt=lambda v: fk.num(v, 1), fontsize=6)
    ax.set_title(name)
    ax.set_xlabel("precision")
    ax.set_ylabel("recall")
    ax.set_aspect("equal")
    # The lecturer's classifiers A and B, and C and D: precision 0.5 with recall 0.7 and 0.99, where the minimum is the same.
    for (pp, rr), mark, off in (((0.9, 0.8), "A", (8, -12)), ((0.87, 0.85), "B", (-14, 6)),
                                ((0.5, 0.7), "C", (6, -12)), ((0.5, 0.99), "D", (6, -10))):
        ax.scatter([pp], [rr], s=26, color="white", edgecolors=fk.TEXT, zorder=5)
        ax.annotate(mark, (pp, rr), textcoords="offset points", xytext=off, fontsize=8, color=fk.TEXT,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
print("F1(A) =", round(2 * 0.9 * 0.8 / 1.7, 4), "F1(B) =", round(2 * 0.87 * 0.85 / 1.72, 4))
print("min(0.5, 0.7) =", min(0.5, 0.7), "min(0.5, 0.99) =", min(0.5, 0.99))

ax = axes[3]
rec = np.linspace(0.001, 1, 400)
prec = 0.8
for beta, c in ((0.5, fk.CATEGORICAL[0]), (1, fk.CATEGORICAL[1]), (2, fk.CATEGORICAL[2])):
    f = (1 + beta**2) * prec * rec / (beta**2 * prec + rec)
    ax.plot(rec, f, color=c, lw=2, label=rf"$\beta={fk.num(beta, None, math=True)}$")
ax.axhline(prec, color=fk.GRIDC, ls="--", lw=1)
ax.text(0.02, prec + 0.02, f"precision = {fk.num(0.8, 1)}", fontsize=8, color=fk.TEXT_2)
ax.plot(rec, rec, color=fk.GRIDC, ls=":", lw=1)
ax.set_xlabel("recall")
ax.set_ylabel(r"$F_\beta$")
ax.set_title(rf"$F_\beta$ при precision {fk.num(0.8, 1)}")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.legend(loc="lower right")
ax.grid(True)
fig.tight_layout()
fk.save(fig, fk.attachments(3) / "metrics-fscore.png")
