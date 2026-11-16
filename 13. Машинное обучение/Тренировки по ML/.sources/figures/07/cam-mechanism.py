"""CAM step by step on a hand-written conv net with a global average pooling head: maps A^k, class weights w_k^c, their weighted sum."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cam_common as C  # noqa: E402
import figkit as fk  # noqa: E402

parts = C.split_data()
assert C.check_gradients("gap", parts) < 1e-6
net, epoch, _ = C.train("gap", parts)
X, y, boxes = parts["test"]
cache = net.forward(X)
CLASS = 1  # the ring
i = int(np.where((y == CLASS) & (net.predict(X) == CLASS))[0][0])
A = cache["A"][i]
w = net.Wo[CLASS]
M = C.cam(net, cache, CLASS)[i]
assert np.allclose(M, (w[:, None, None] * A).sum(0))

fig = plt.figure(figsize=(13.0, 3.9))
gs = fig.add_gridspec(2, 7, width_ratios=[1.45, 1, 1, 1, 1, 1.45, 1.45], wspace=0.3, hspace=0.45)
ax = fig.add_subplot(gs[:, 0])
C.show_image(ax, X[i], boxes[i])
ax.set_title("Картинка, класс кольцо", fontsize=9)

order = np.argsort(-w)
vmax = A.max()
for n, k in enumerate(order):
    a = fig.add_subplot(gs[n // 4, 1 + n % 4])
    a.imshow(A[k], cmap="ddlc_seq", vmin=0, vmax=vmax, interpolation="nearest")
    a.set_xticks([])
    a.set_yticks([])
    color = plt.get_cmap("ddlc_div")(1.0 if w[k] > 0 else 0.0)  # the same ends as on the map of M_c
    a.set_title(f"$A^{{{k+1}}}$, $w={fk.num(w[k], '+.1f', math=True)}$", fontsize=8, color=color)
    for s in a.spines.values():
        s.set_visible(True)
        s.set_edgecolor(color)
        s.set_linewidth(1.6)

ax = fig.add_subplot(gs[:, 5])
lim = np.abs(M).max()
ax.imshow(M, cmap="ddlc_div", vmin=-lim, vmax=lim, interpolation="nearest")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(r"$M_c=\sum_k w_k^c A^k$", fontsize=9)

ax = fig.add_subplot(gs[:, 6])
C.show_map(ax, X[i], np.maximum(M, 0), box=boxes[i])
ax.set_title("Положительная часть", fontsize=9)

fk.save(fig, fk.attachments(7) / "cam-mechanism.png")

print("epoch", epoch, "test acc", float((net.predict(X) == y).mean()))
print("image", i, "w", np.round(w, 2))
print("mass of positive CAM inside target box / distractor box:", np.round(C.box_shares(M[None], boxes[i:i + 1]), 3))
