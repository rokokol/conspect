"""Why Grad-CAM ends with ReLU: the raw weighted sum for the true class and for a wrong class, before and after ReLU, on the flatten net."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cam_common as C  # noqa: E402
import figkit as fk  # noqa: E402

parts = C.split_data()
assert C.check_gradients("flat", parts) < 1e-6
net, epoch, _ = C.train("flat", parts)
X, y, boxes = parts["test"]
cache = net.forward(X)
TRUE, OTHER = 1, 0  # ring against cross
i = int(np.where((y == TRUE) & (net.predict(X) == TRUE))[0][0])

relu_t, raw_t, alpha_t = C.grad_cam(net, cache, TRUE)
relu_o, raw_o, alpha_o = C.grad_cam(net, cache, OTHER)
lim = max(np.abs(raw_t[i]).max(), np.abs(raw_o[i]).max())

fig = plt.figure(figsize=(11.6, 6.4))
gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1], hspace=0.28, wspace=0.18)

ax = fig.add_subplot(gs[0, 0])
C.show_image(ax, X[i], boxes[i])
ax.set_title("Картинка, класс кольцо", fontsize=9)

for col, (name, raw, relu) in enumerate([("кольцо", raw_t, relu_t), ("крест", raw_o, relu_o)], start=1):
    ax = fig.add_subplot(gs[0, col])
    C.show_map(ax, X[i], raw[i], box=boxes[i], signed=True, scale=lim)
    ax.set_title(f"$\\sum_k\\alpha_k A^k$ для класса {name}", fontsize=9)
    ax = fig.add_subplot(gs[1, col])
    C.show_map(ax, X[i], relu[i], box=boxes[i], scale=max(relu_t[i].max(), 1e-12))
    ax.set_title(f"После ReLU, класс {name}", fontsize=9)

ax = fig.add_subplot(gs[1, 0])
ks = np.arange(C.K)
ax.bar(ks - 0.2, alpha_t[i], 0.4, color=fk.CATEGORICAL[1], label="кольцо")
ax.bar(ks + 0.2, alpha_o[i], 0.4, color=fk.CATEGORICAL[0], label="крест")
ax.axhline(0, color=fk.TEXT_2, lw=0.8)
ax.set_xticks(ks, [f"{k + 1}" for k in ks])
ax.set_xlabel("номер карты $k$")
ax.set_title(r"Веса $\alpha_k$", fontsize=9)
ax.legend(fontsize=7)
ax.grid(True, axis="y")

fk.save(fig, fk.attachments(7) / "gradcam-relu.png")

# the same pair the other way round, and the third class, over every test image the net got right (flatten net)
right = net.predict(X) == y
for img_cls in range(C.NC):
    sel = right & (y == img_cls)
    peaks = {c: float(np.mean([C.grad_cam(net, cache, c)[0][n].max() for n in np.where(sel)[0]])) for c in range(C.NC)}
    print("images of", C.CLASSES[img_cls], int(sel.sum()), "mean peak of the ReLU map by class:",
          {C.CLASSES[c]: round(v, 3) for c, v in peaks.items()})

pos_t = float(np.maximum(raw_t[i], 0).sum() / np.abs(raw_t[i]).sum())
pos_o = float(np.maximum(raw_o[i], 0).sum() / np.abs(raw_o[i]).sum())
print("epoch", epoch, "image", i, "logits", np.round(cache["logits"][i], 2))
print("positive share of |raw|: true", round(pos_t, 3), "other", round(pos_o, 3))
print("share of positive mass in target box (after ReLU): true", np.round(C.box_shares(relu_t[i:i + 1], boxes[i:i + 1]), 3),
      "other", np.round(C.box_shares(relu_o[i:i + 1], boxes[i:i + 1]), 3))
print("alpha true", np.round(alpha_t[i], 3), "alpha other", np.round(alpha_o[i], 3))
print("raw min/max true", raw_t[i].min().round(2), raw_t[i].max().round(2), "other", raw_o[i].min().round(2), raw_o[i].max().round(2))
