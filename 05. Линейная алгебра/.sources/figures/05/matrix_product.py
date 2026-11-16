"""Matrix product in Falk's layout: the element c_ij is row i of A times column j of B."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

A = np.array([[5, -1, 3, 1], [2, 0, -1, 4]])
B = np.array([[-1, 3, 0], [-2, 1, 1], [3, 0, -2], [4, 1, 2]])
C = A @ B
assert (C == np.array([[10, 15, -5], [11, 10, 10]])).all()

I, J = 0, 1  # the highlighted element c_12, zero-based
terms = [int(A[I, q]) * int(B[q, J]) for q in range(A.shape[1])]
assert sum(terms) == C[I, J] == 15

m, n = A.shape
p = B.shape[1]
CELL = 1.0
GAP = 1.2  # space between blocks
HOT = lafig.tint(lafig.HIGHLIGHT, 0.5)  # the element c_ij, light enough to keep the digits readable

# block origins (x of left edge, y of top edge); y grows downward in this layout
ax0, ay0 = 0.0, n * CELL + GAP  # A, bottom-left
bx0, by0 = n * CELL + GAP, 0.0  # B, top-right
cx0, cy0 = bx0, ay0  # C, bottom-right

fig, ax = plt.subplots(figsize=(8.2, 5.4))
ax.set_xlim(-0.8, cx0 + p * CELL + 0.8)
ax.set_ylim(ay0 + m * CELL + 0.8, -1.0)
ax.set_aspect("equal")
ax.axis("off")


def block(M, x0, y0, name, hi_row=None, hi_col=None):
    rows, cols = M.shape
    for r in range(rows):
        for c in range(cols):
            hot_row = hi_row is not None and r == hi_row
            hot_col = hi_col is not None and c == hi_col
            if hot_row and hot_col:
                face = HOT
            elif hot_row:
                face = lafig.tint(lafig.VECTOR, 0.55)
            elif hot_col:
                face = lafig.tint(lafig.IMAGE, 0.55)
            else:
                face = "none"
            ax.add_patch(Rectangle((x0 + c * CELL, y0 + r * CELL), CELL, CELL,
                                   facecolor=face, edgecolor=lafig.AUX, lw=0.8))
            ax.text(x0 + (c + 0.5) * CELL, y0 + (r + 0.5) * CELL, str(int(M[r, c])).replace("-", "−"),
                    ha="center", va="center", color=lafig.INK, fontsize=12)
    ax.add_patch(Rectangle((x0, y0), cols * CELL, rows * CELL, fill=False,
                           edgecolor=lafig.INK, lw=1.6))
    ax.text(x0 + cols * CELL / 2, y0 - 0.35, name, ha="center", va="bottom",
            color=lafig.INK, fontsize=13)


block(A, ax0, ay0, f"$A$  ({m}$\\times${n})", hi_row=I)
block(B, bx0, by0, f"$B$  ({n}$\\times${p})", hi_col=J)
block(C, cx0, cy0, f"$C=AB$  ({m}$\\times${p})", hi_row=I, hi_col=J)

# the arithmetic of the highlighted element, under the product
expr = " + ".join(f"$({int(A[I, q])})\\cdot({int(B[q, J])})$" for q in range(n))
ax.text(cx0 + p * CELL / 2, ay0 + m * CELL + 0.55,
        f"$c_{{{I + 1}{J + 1}}}$ = {expr} = {int(C[I, J])}",
        ha="center", va="top", color=lafig.INK, fontsize=10.5)

# legend of the colour convention
legend = [
    (lafig.tint(lafig.VECTOR, 0.55), f"строка {I + 1} ($A$ и $C$)"),
    (lafig.tint(lafig.IMAGE, 0.55), f"столбец {J + 1} матрицы $B$"),
    (HOT, f"элемент $c_{{{I + 1}{J + 1}}}$"),
]
for k, (face, label) in enumerate(legend):
    y = 0.0 + k * 0.9
    ax.add_patch(Rectangle((0.0, y), 0.6, 0.6, facecolor=face, edgecolor=lafig.AUX, lw=0.8))
    ax.text(0.85, y + 0.3, label, ha="left", va="center", color=lafig.INK, fontsize=10.5)

lafig.save(fig, 5, "matrix_product")
