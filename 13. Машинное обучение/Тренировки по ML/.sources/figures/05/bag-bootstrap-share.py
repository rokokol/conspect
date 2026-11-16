"""Bootstrap on ten objects (how many times each one was drawn) and the share of distinct objects against the sample size."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

M_SMALL = 10
rng = np.random.default_rng(fk.SEED)
counts = np.array([np.bincount(rng.integers(0, M_SMALL, M_SMALL), minlength=M_SMALL) for _ in range(3)])

fig, (ax1, ax2) = fk.subplots(1, 2, size=(11.6, 3.6), gridspec_kw={"width_ratios": [1.1, 1]})

cmap = fk.plt.get_cmap("ddlc_seq").copy()
cmap.set_bad("white")
ax1.imshow(np.ma.masked_equal(counts, 0), cmap=cmap, vmin=0, vmax=4, aspect="auto")
for i in range(counts.shape[0]):
    for j in range(counts.shape[1]):
        v = counts[i, j]
        ax1.text(j, i, str(v) if v else "·", ha="center", va="center", fontsize=11,
                 color="white" if v >= 3 else fk.TEXT)
ax1.set_xticks(range(M_SMALL), [str(j + 1) for j in range(M_SMALL)])
ax1.set_yticks(range(3), [f"выборка {i + 1}\nразных: {int((counts[i] > 0).sum())}" for i in range(3)])
ax1.set_xlabel("номер объекта исходной выборки")
ax1.set_title("сколько раз объект вытащен")
for side in ("top", "right"):
    ax1.spines[side].set_visible(False)
ax1.grid(False)

ms = np.unique(np.round(np.logspace(0.3, 4, 40)).astype(int))
theory = 1 - (1 - 1 / ms) ** ms
sim_m = [5, 10, 30, 100, 1000, 10000]
sim = [np.mean([len(np.unique(rng.integers(0, m, m))) / m for _ in range(200)]) for m in sim_m]
ax2.plot(ms, theory, color=fk.MODEL_C, lw=1.8, label="$1-(1-1/m)^m$")
ax2.scatter(sim_m, sim, s=30, facecolors="white", edgecolors=fk.MODEL_C, linewidths=1.3, zorder=3,
            label="замер, 200 выборок")
ax2.axhline(1 - 1 / np.e, color=fk.ACCENT, lw=1, ls="--", label=f"$1-1/e\\approx{fk.num(1 - 1 / np.e, 3, math=True)}$")
ax2.set_xscale("log")
ax2.set_xlabel("размер выборки m")
ax2.set_ylabel("доля разных объектов")
ax2.set_title("доля попавших в бутстреп-выборку")
ax2.set_ylim(0.6, 0.8)
ax2.legend(loc="upper right")

fk.save(fig, fk.attachments(5) / "bag-bootstrap-share.png")

print("counts", counts.tolist(), "distinct", (counts > 0).sum(1).tolist())
for m in (5, 10, 20, 30, 100, 1000):
    print(m, round(1 - (1 - 1 / m) ** m, 4))
print("limit", round(1 - 1 / np.e, 4), "sim", [round(float(s), 4) for s in sim])
