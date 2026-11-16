"""What the hidden layer sees on circles: three tanh neurons map the plane into a cube where one plane separates the classes.

Left: input space, the neurons' zero lines and the network's zones.
Right: the same train points at (h1, h2, h3) and the output neuron's plane
v1 h1 + v2 h2 + v3 h3 + c = 0; the script checks that this plane classifies
the hidden points exactly as the network does.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import nn_common as nc  # noqa: E402

X, y = fk.dataset("circles")
Xtr, Xte, ytr, yte = fk.split(X, y)
m = nc.best_of(lambda s: nc.mlp([3], "tanh", seed=s), Xtr, ytr)
print("circles, 3 tanh: train", round(m.score(Xtr, ytr), 3), "test", round(m.score(Xte, yte), 3))

H = nc.hidden_activations(m, Xtr)
v, c = m.coefs_[1][:, 0], m.intercepts_[1][0]
assert np.array_equal((H @ v + c > 0).astype(int), m.predict(Xtr)), "output plane disagrees with the network"
print("output weights", np.round(v, 2), "bias", round(c, 2))

fig = fk.plt.figure(figsize=(9.6, 4.4))
ax = fig.add_subplot(1, 2, 1)
fk.plot_decision(ax, m, Xtr, ytr, X_test=Xte, y_test=yte)
allX = np.vstack([Xtr, Xte])
lo, hi = allX.min(0) - 0.6, allX.max(0) + 0.6
nc.hidden_lines(ax, m, (lo[0], hi[0], lo[1], hi[1]))
ax.set_title("исходные признаки $x_1, x_2$")

ax = fig.add_subplot(1, 2, 2, projection="3d")
for k in (0, 1):
    sel = ytr == k
    ax.scatter(H[sel, 0], H[sel, 1], H[sel, 2], s=12, color=fk.CLASS_COLORS[k], edgecolors="white",
               linewidths=0.4, depthshade=False)
# Solve the plane for the coordinate with the largest output weight, so it stays finite.
k = int(np.argmax(np.abs(v)))
a, b = [i for i in range(3) if i != k]
g = np.linspace(-1, 1, 12)
A, B = np.meshgrid(g, g)
K = -(v[a] * A + v[b] * B + c) / v[k]
K = np.where(np.abs(K) <= 1.05, K, np.nan)
coords = [None] * 3
coords[a], coords[b], coords[k] = A, B, K
ax.plot_surface(*coords, color=fk.GRIDC, alpha=0.3, linewidth=0)
for i, lab in enumerate(("$h_1$", "$h_2$", "$h_3$")):
    getattr(ax, f"set_{'xyz'[i]}label")(lab, color=fk.TEXT)
    getattr(ax, f"set_{'xyz'[i]}lim")(-1, 1)
ax.set_xticks([-1, 0, 1])
ax.set_yticks([-1, 0, 1])
ax.set_zticks([-1, 0, 1])
ax.view_init(elev=22, azim=-58)
ax.set_title("скрытый слой $h_1, h_2, h_3$")
fig.tight_layout()
fk.save(fig, fk.attachments(6) / "nn-hidden-space.png")
