"""The same toy game as a path from E[f] to f(x): all 3! orders of adding features, and their average.

Left: the running value for every order. Right: the gain each feature gets in each order; the bottom row is the Shapley value.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402
from shapley_lib import interventional_values  # noqa: E402

bg = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)
x = np.array([[1.0, 1.0, 1.0]])
v = interventional_values(lambda Z: 3 * Z[:, 0] + Z[:, 1] * Z[:, 2], x, bg)[:, 0]

orders = list(itertools.permutations(range(3)))
gains = np.zeros((len(orders), 3))
paths = []
for r, order in enumerate(orders):
    mask, run = 0, [v[0]]
    for i in order:
        gains[r, i] = v[mask | 1 << i] - v[mask]
        mask |= 1 << i
        run.append(v[mask])
    paths.append(run)
phi = gains.mean(0)

fig, (a0, a1) = fk.subplots(1, 2, size=(11.2, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
cols = fk.CATEGORICAL
for r, (order, run) in enumerate(zip(orders, paths)):
    for step, i in enumerate(order):
        left, width = run[step], run[step + 1] - run[step]
        a0.barh(r, width, left=left, height=0.62, color=cols[i], edgecolor="white", lw=1.2)
        if width > 0.2:
            a0.text(left + width / 2, r, fk.num(width, 2).rstrip("0").rstrip(","), ha="center", va="center",
                    fontsize=7.5, color="white")
a0.axvline(v[0], color=fk.TEXT, lw=0.9, ls=":")
a0.axvline(v[-1], color=fk.TEXT, lw=0.9, ls=":")
a0.set_yticks(range(6), ["".join(str(i + 1) for i in o) for o in orders], fontsize=8)
a0.invert_yaxis()
a0.set_xlabel("$\\mathsf{E}[f\\mid x_S]$: от $\\mathsf{E}f=1{,}75$ до $f(x)=4$")
a0.set_xlim(1.6, 4.15)
a0.legend(handles=[Patch(color=cols[i], label=f"признак {i + 1}") for i in range(3)], fontsize=7,
          loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
a0.grid(True, axis="x")
a0.set_title("Порядок добавления признаков", fontsize=9, pad=22)

table = np.vstack([gains, phi])
im = a1.imshow(table, cmap="ddlc_seq", aspect="auto", vmin=0, vmax=1.6)
for r in range(table.shape[0]):
    for c in range(3):
        a1.text(c, r, fk.num(table[r, c], 3).rstrip("0").rstrip(","), ha="center", va="center", fontsize=8,
                color="white" if table[r, c] > 1.0 else fk.TEXT)
a1.set_xticks(range(3), ["признак 1", "признак 2", "признак 3"], fontsize=8)
a1.set_yticks(range(7), ["".join(str(i + 1) for i in o) for o in orders] + ["среднее"], fontsize=8)
a1.axhline(5.5, color=fk.TEXT, lw=1.2)
a1.set_title("Прирост признака в каждом порядке", fontsize=9)
a1.grid(False)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "shapley-toy-orders.png")
print("phi", phi, "paths", paths)
