"""LSA example of the singular value decomposition note: words and documents in the plane of the second and third singular directions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

WORDS = ["вектор", "матрица", "оператор", "отображение", "сила", "скорость", "градиент", "обучение", "модель"]
A = np.array(
    [
        [1, 2, 2, 1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 2, 0],
        [2, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 2, 1, 0, 0, 0],
        [0, 0, 1, 1, 2, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 2],
        [0, 0, 0, 0, 0, 2, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 2],
    ],
    dtype=float,
)
K = 3

V, s, Wh = np.linalg.svd(A)
V, W = V[:, :K], Wh[:K].T
# the sign of a singular pair is free: the first one is made positive, the
# second one points to the mechanics words, the third one to the algebra words
anchors = [range(9), [4, 5], [1, 2]]
for j in range(K):
    if V[list(anchors[j]), j].sum() < 0:
        V[:, j], W[:, j] = -V[:, j], -W[:, j]

words_xy = (V * s[:K])[:, 1:]
docs_xy = (W * s[:K])[:, 1:]

fig, ax = plt.subplots(figsize=(7.2, 5.6))
ax.axhline(0, color=lafig.AUX, lw=0.8, zorder=0)
ax.axvline(0, color=lafig.AUX, lw=0.8, zorder=0)

ax.scatter(*words_xy.T, s=60, color=lafig.VECTOR, zorder=3, label="слова")
ax.scatter(*docs_xy.T, s=60, color=lafig.HIGHLIGHT, marker="s", zorder=3, label="документы")

# (dx, dy, horizontal alignment) of a label, in points from its marker
word_offsets = {
    "вектор": (8, 4, "left"),
    "матрица": (-8, 6, "right"),
    "оператор": (-8, 4, "right"),
    "отображение": (8, -14, "left"),
    "сила": (8, 4, "left"),
    "скорость": (8, -14, "left"),
    "градиент": (-8, -14, "right"),
    "обучение": (-8, 6, "right"),
    "модель": (-8, -14, "right"),
}
for name, (x, y) in zip(WORDS, words_xy):
    dx, dy, ha = word_offsets[name]
    ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, color=lafig.VECTOR, fontsize=10)

doc_offsets = [
    (8, 4, "left"),
    (8, 4, "left"),
    (8, -14, "left"),
    (8, 4, "left"),
    (8, 4, "left"),
    (8, 4, "left"),
    (8, 4, "left"),
    (8, 4, "left"),
]
for i, ((x, y), (dx, dy, ha)) in enumerate(zip(docs_xy, doc_offsets), start=1):
    ax.annotate(f"$d_{i}$", (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, color=lafig.HIGHLIGHT, fontsize=10)

ax.set_xlabel("второе направление: механика против машинного обучения", color=lafig.INK)
ax.set_ylabel("третье направление: линейная алгебра против механики", color=lafig.INK)
ax.set_xlim(-2.8, 2.6)
ax.set_ylim(-2.1, 2.3)
ax.set_aspect("equal")
ax.legend(loc="upper left", frameon=False)

lafig.save(fig, 12, "lsa")
