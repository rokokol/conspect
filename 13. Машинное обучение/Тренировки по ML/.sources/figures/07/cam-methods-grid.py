"""One test image per class under four explanations: pixel saliency, CAM and Grad-CAM on the GAP net, Grad-CAM on the flatten net.

Every map is for the true class and scaled by its own maximum. With the GAP head Grad-CAM equals CAM up to the factor 1/Z.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cam_common as C  # noqa: E402
import figkit as fk  # noqa: E402

parts = C.split_data()
for head in ("gap", "flat"):
    assert C.check_gradients(head, parts) < 1e-6
gap, e_gap, _ = C.train("gap", parts)
flat, e_flat, _ = C.train("flat", parts)
X, y, boxes = parts["test"]
cg, cf = gap.forward(X), flat.forward(X)

print("epochs", e_gap, e_flat)
print("test acc gap", float((gap.predict(X) == y).mean()), "flat", float((flat.predict(X) == y).mean()))
worst = 0.0
shares = {}
for c in range(C.NC):
    sel = y == c
    gc = C.grad_cam(gap, cg, c)
    cm = C.cam(gap, cg, c)
    worst = max(worst, np.abs(C.cam(gap, cg, c) - gc[1] * C.OUT * C.OUT).max() / np.abs(cm).max())
    shares[c] = {
        "CAM": C.box_shares(cm[sel], boxes[sel]),
        "Grad-CAM gap": C.box_shares(gc[0][sel], boxes[sel]),
        "Grad-CAM flat": C.box_shares(C.grad_cam(flat, cf, c)[0][sel], boxes[sel]),
    }
    print(C.CLASSES[c], {k: np.round(v, 2).tolist() for k, v in shares[c].items()})
print("max |CAM - Z * raw Grad-CAM| / max|CAM|:", worst)
print("target box is", round(25 / 196, 3), "of the 14x14 map")

for c in range(C.NC):
    sel = y == c
    print(C.CLASSES[c], "saliency |dy/dx| share in box (GAP net):",
          round(C.pixel_box_share(C.saliency(gap, cg, c)[sel], boxes[sel]), 3),
          " flatten net:", round(C.pixel_box_share(C.saliency(flat, cf, c)[sel], boxes[sel]), 3))
print("uniform pixel share 25/256 =", round(25 / 256, 3))
cells = C.box_cells(boxes)
print("cells of the 196 whose centre is inside the box: mean", round(float(cells.mean()), 2), "=", round(float(cells.mean()) / 196, 3),
      "min", int(cells.min()), "full 25:", round(float((cells == 25).mean()), 2))

# where the CAM peak of a cross sits relative to the cross centre
ok = (y == 0) & (gap.predict(X) == 0)
cam_cross = C.cam(gap, cg, 0)[ok]
offsets, centre_mass = [], []
for m, ((ty, tx), _) in zip(cam_cross, boxes[ok]):
    a, b = np.unravel_index(m.argmax(), m.shape)
    offsets.append((a + 1 - (ty + 2), b + 1 - (tx + 2)))
    pos = np.maximum(m, 0)
    rows = np.arange(C.OUT)[:, None] + 1
    colsx = np.arange(C.OUT)[None, :] + 1
    near = (abs(rows - (ty + 2)) <= 1) & (abs(colsx - (tx + 2)) <= 1)
    centre_mass.append(pos[near].sum() / pos.sum())
from collections import Counter  # noqa: E402
print("crosses recognised:", int(ok.sum()), "peak offset (dy,dx) from the centre:", Counter(offsets).most_common(4))
print("share of positive CAM mass in the 3x3 window around the cross centre:", round(float(np.mean(centre_mass)), 3))

# strength of responses on the object and elsewhere (GAP net, test part)
A = cg["A"]
inside = np.zeros_like(A[:, 0], dtype=bool)
for n, ((ty, tx), _) in enumerate(boxes):
    a = np.arange(C.OUT)[:, None] + 1
    b = np.arange(C.OUT)[None, :] + 1
    inside[n] = (a >= ty) & (a < ty + 5) & (b >= tx) & (b < tx + 5)
inside = np.broadcast_to(inside[:, None], A.shape)
active = A > 0
print("active cells:", int(active.sum()), "of them outside the target box:", round(float((active & ~inside).sum() / active.sum()), 3),
      "median response outside / inside:", round(float(np.median(A[active & ~inside])), 2), round(float(np.median(A[active & inside])), 2))
print("share of filters that never fire on the test part:", [int(k) + 1 for k in range(C.K) if not active[:, k].any()])

picks = [int(np.where((y == c) & (gap.predict(X) == c) & (flat.predict(X) == c))[0][0]) for c in range(C.NC)]
cols = ["Картинка", "Карта значимости\n$|\\partial y^c/\\partial x|$", "CAM\n(сеть с GAP)", "Grad-CAM\n(сеть с GAP)",
        "Grad-CAM\n(max-pool и flatten)"]
fig, axes = fk.subplots(C.NC, 5, size=(12.0, 7.4))
for r, i in enumerate(picks):
    c = int(y[i])
    maps = [
        None,
        C.saliency(gap, cg, c)[i],
        np.maximum(C.cam(gap, cg, c)[i], 0),
        C.grad_cam(gap, cg, c)[0][i],
        C.grad_cam(flat, cf, c)[0][i],
    ]
    for j, M in enumerate(maps):
        ax = axes[r, j]
        if M is None:
            C.show_image(ax, X[i], boxes[i])
            ax.set_ylabel(C.CLASSES[c], fontsize=10)
        else:
            C.show_map(ax, X[i], M, box=boxes[i], on_pixels=(j == 1))
        if r == 0:
            ax.set_title(cols[j], fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "cam-methods-grid.png")
