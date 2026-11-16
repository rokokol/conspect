"""Graph of the permutation 1,3,5,7,9,11,10,8,6,4,2 of M_11 with its inversions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

PERM = [1, 3, 5, 7, 9, 11, 10, 8, 6, 4, 2]
N = len(PERM)

fig, ax = plt.subplots(figsize=(5.6, 5.2))

for k in range(1, N + 1):
    ax.axhline(k, color=lafig.AUX, lw=0.6, zorder=0)
    ax.axvline(k, color=lafig.AUX, lw=0.6, zorder=0)

# every inversion pair, drawn faintly: i < j and n_i > n_j
for i in range(N):
    for j in range(i + 1, N):
        if PERM[i] > PERM[j]:
            ax.plot([i + 1, j + 1], [PERM[i], PERM[j]], color=lafig.IMAGE, lw=0.8, alpha=0.35, zorder=1)

# one pair without inversion, for contrast
ax.plot([1, 4], [PERM[0], PERM[3]], color=lafig.MUTED, lw=1.6, ls="--", zorder=2)
# one inversion, emphasised
ax.plot([6, 9], [PERM[5], PERM[8]], color=lafig.HIGHLIGHT, lw=2.2, zorder=3)

ax.scatter(range(1, N + 1), PERM, s=70, color=lafig.VECTOR, zorder=4)

ax.set_xlim(0.4, N + 0.6)
ax.set_ylim(0.4, N + 0.6)
ax.set_aspect("equal")
ax.set_xticks(range(1, N + 1))
ax.set_yticks(range(1, N + 1))
ax.set_xlabel("$i$")
ax.set_ylabel("$n_i$")
ax.tick_params(length=0)
for side in ax.spines.values():
    side.set_color(lafig.INK)

legend = [
    Line2D([], [], marker="o", ls="", color=lafig.VECTOR, label="точка $(i,\\,n_i)$"),
    Line2D([], [], color=lafig.IMAGE, alpha=0.6, label="инверсия, отрезок с отрицательным наклоном"),
    Line2D([], [], color=lafig.HIGHLIGHT, lw=2.2, label="инверсия $n_6=11>n_9=6$"),
    Line2D([], [], color=lafig.MUTED, ls="--", lw=1.6, label="пара без инверсии: $n_1=1<n_4=7$"),
]
ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=8)

lafig.save(fig, 4, "permutation_graph")
