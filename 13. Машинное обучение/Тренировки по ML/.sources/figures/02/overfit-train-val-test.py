"""Train, validation and test: what is tuned on which part, and where information leaks."""
import sys
from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

fig, ax = fk.plt.subplots(figsize=(8.2, 3.9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis("off")

# Data strip: the proportions are illustrative.
parts = [("train", 2, 48, dict(fc=fk.TRAIN_C, ec="white"), "white"),
         ("validation", 52, 22, dict(fc="white", ec=fk.TEXT_2, lw=1.6), fk.TEXT),
         ("test", 76, 22, dict(fc="white", ec=fk.TEST_C, lw=1.6, ls="--"), fk.TEXT)]
for name, x0, w, style, tc in parts:
    ax.add_patch(Rectangle((x0, 38), w, 9, **style))
    ax.text(x0 + w / 2, 42.5, name, ha="center", va="center", color=tc, fontsize=10)


def box(cx, w, title, sub, color):
    ax.add_patch(FancyBboxPatch((cx - w / 2, 14), w, 12, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.6))
    ax.text(cx, 21.5, title, ha="center", va="center", fontsize=9, color=fk.TEXT)
    ax.text(cx, 17.2, sub, ha="center", va="center", fontsize=7, color=fk.TEXT_2)


def arrow(xy0, xy1, color):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle="-|>", mutation_scale=12, color=color, lw=1.4))


box(25, 38, "параметры $w$", "настраиваются на train", fk.TRAIN_C)
box(63, 24, "гиперпараметры", "выбираются по validation", fk.TEXT_2)
box(87, 19, "вердикт", "один раз, на test", fk.TEST_C)

arrow((25, 38), (25, 27), fk.TRAIN_C)
arrow((87, 38), (87, 27), fk.TEST_C)
arrow((50.5, 20), (45, 20), fk.TEXT_2)

# Leak: the same arrow, validation to hyperparameters, drawn in ink and named: validation is no longer unseen.
arrow((63, 38), (63, 27), fk.ACCENT)
ax.text(64.5, 32.5, "утечка", ha="left", va="center", fontsize=8, color=fk.ACCENT)
ax.text(63, 7, "выбор по validation завышает\nоценку на ней самой", ha="center", va="center", fontsize=7.5,
        color=fk.ACCENT)
ax.text(87, 9, "много проверок\nи выбор лучшей:\nутечка и из test", ha="center", va="center", fontsize=6.5,
        color=fk.TEST_C)
fk.save(fig, fk.attachments(2) / "overfit-train-val-test.png")
