"""Width and depth of a ReLU network on xor and circles.

nn-width-depth-<data>.png: zones over depth (1-3 hidden layers) x width (1, 2, 3, 8 neurons per layer).
nn-width-curve.png: train, 5-fold validation on the train part, and test against
the width of one hidden layer; the chosen width is the validation maximum.
Every network is the best of five random starts by training loss.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk  # noqa: E402
import nn_common as nc  # noqa: E402

OUT = fk.attachments(6)
DEPTHS = [1, 2, 3]
WIDTHS = [1, 2, 3, 8]
CURVE_WIDTHS = [1, 2, 3, 4, 6, 8, 16, 32]
DATA = ["xor", "circles"]

for name in DATA:
    fig, axes = fk.model_grid(lambda d, w: nc.BestOf([w] * d), DEPTHS, WIDTHS, name,
                              row_label=lambda d: f"{d} скрытых слоя" if d > 1 else "1 скрытый слой",
                              col_label=lambda w: f"ширина {w}", size=(12.4, 9.4))
    fk.save(fig, OUT / f"nn-width-depth-{name}.png")
    print(name, "grid done")

fig, axes = fk.subplots(1, 2, size=(9.6, 3.6))
for ax, name in zip(axes, DATA):
    X, y = fk.dataset(name)
    Xtr, Xte, ytr, yte = fk.split(X, y)
    tr, te, va = [], [], []
    for w in CURVE_WIDTHS:
        m = nc.BestOf([w]).fit(Xtr, ytr)
        tr.append(m.score(Xtr, ytr))
        te.append(m.score(Xte, yte))
        # Equal fold accuracies can differ in the last float bit; rounding makes a tie a tie,
        # and argmax then takes the first, that is the narrower network.
        va.append(round(nc.cv_score(lambda w=w: nc.BestOf([w]), Xtr, ytr), 12))
    b = fk.complexity_curve(ax, CURVE_WIDTHS, tr, te, xlabel="нейронов в скрытом слое", val=va, log=True)
    ax.legend(loc="lower right")
    ax.set_xticks(CURVE_WIDTHS)
    ax.set_xticklabels([str(w) for w in CURVE_WIDTHS])
    ax.set_title(name)
    print(name, "widths", CURVE_WIDTHS, "train", [round(t, 3) for t in tr], "val", [round(t, 3) for t in va],
          "test", [round(t, 3) for t in te])
    print(name, "chosen by validation:", CURVE_WIDTHS[b], "val", round(va[b], 3), "test", round(te[b], 3))
fig.tight_layout()
fk.save(fig, OUT / "nn-width-curve.png")
