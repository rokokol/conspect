"""The lecture's 20 balls on an axis (slides 14-20): every threshold under the three criteria, and the chain of splits.

Slide colours: yellow (11) and purple (9). Here yellow is class 1 (bow, red) and purple is class 0 (rule), the
course's binary colours. Positions are 0..19; "X <= t" sends positions 0..t to the left.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from matplotlib.patches import FancyBboxPatch  # noqa: E402

import figkit as fk  # noqa: E402

# 1 = yellow on the slide (red here), 0 = purple. Read off slide 14: Y, B B B B, Y Y Y Y, B B B B, Y*6, B.
Y = np.array([1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0])
# Criterion colours are not the class colours: the balls above the curves use rule and bow (see crit-curves.py).
C_ENT, C_GINI, C_MIS = fk.P["ribbon"], fk.P["monika"], fk.P["yuri"]
RED, SIR = fk.CLASS_COLORS[1], fk.CLASS_COLORS[0]


def entropy(p):
    return -sum(q * np.log2(q) for q in (p, 1 - p) if q > 0)


def gini(p):
    return 1 - p**2 - (1 - p) ** 2


def misclass(p):
    return 1 - max(p, 1 - p)


def weighted(f, t):
    left, right = Y[: t + 1], Y[t + 1:]
    return (len(left) * f(left.mean()) + len(right) * f(right.mean())) / len(Y)


thresholds = np.arange(19)  # X <= t for t = 0..18
crits = [("ошибка классификации", misclass, C_MIS), ("Gini", gini, C_GINI), ("энтропия, $\\log_2$", entropy, C_ENT)]

fig, axes = fk.plt.subplots(4, 1, figsize=(9.4, 8.6), sharex=True,
                            gridspec_kw={"height_ratios": [0.9, 2, 2, 2], "hspace": 0.28})
ax = axes[0]
ax.scatter(np.arange(20), np.zeros(20), s=150, c=[RED if v else SIR for v in Y], edgecolors="white", linewidths=1, zorder=3)
for t, label in ((4, "X ≤ 4"), (12, "X ≤ 12")):
    ax.axvline(t + 0.5, color=fk.ACCENT, lw=1.6, ls="--", zorder=2)
    ax.text(t + 0.5, 0.62, label, ha="center", fontsize=9, color=fk.TEXT,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"), zorder=4)
ax.set_ylim(-0.5, 1)
ax.set_yticks([])
ax.set_title("20 шариков: красные — жёлтые со слайда, сиреневые — фиолетовые")
ax.grid(False)
for side in ("left", "bottom"):
    ax.spines[side].set_visible(False)

for ax, (name, f, col) in zip(axes[1:], crits):
    vals = np.array([weighted(f, t) for t in thresholds])
    best = np.flatnonzero(np.isclose(vals, vals.min()))
    ax.plot(thresholds, vals, color=col, lw=2, marker="o", ms=4)
    ax.axhline(f(Y.mean()), color=fk.TEXT_2, lw=1, ls=":")
    ax.scatter(thresholds[best], vals[best], s=110, facecolors="none", edgecolors=fk.ACCENT, linewidths=1.8, zorder=5)
    for t in (4, 12):
        ax.annotate(fk.num(vals[t], 3), (t, vals[t]), textcoords="offset points", xytext=(0, -15), ha="center", fontsize=8,
                    color=fk.TEXT)
    ax.set_ylabel(name, fontsize=8)
    ax.grid(True, axis="y")
    ax.set_ylim(min(vals.min(), f(Y.mean())) * 0.9, f(Y.mean()) * 1.05)
    print(name, "root", round(f(Y.mean()), 4), "argmin at X<=", thresholds[best].tolist(), "value", round(vals.min(), 4),
          "| t=4:", round(vals[4], 4), "t=12:", round(vals[12], 4))
axes[-1].set_xticks(thresholds, [f"{t}" for t in thresholds])
axes[-1].set_xlabel("порог: X ≤ t (пунктир — значение до разбиения, кружок — лучший порог)")
fk.save(fig, fk.attachments(4) / "crit-balls-thresholds.png")

# The chain of splits of slide 20: five thresholds, six leaves.
nodes = {  # name: (positions list, centre x, y, split text)
    "root": (list(range(20)), 10.5, 0, "X ≤ 12"),
    "L": (list(range(13)), 4.6, -3.1, "X ≤ 8"),
    "R": (list(range(13, 20)), 16.6, -3.1, "X ≤ 18"),
    "LL": (list(range(9)), 2.4, -6.2, "X ≤ 4"),
    "LR": (list(range(9, 13)), 8.0, -6.2, None),
    "RL": (list(range(13, 19)), 14.8, -6.2, None),
    "RR": ([19], 18.6, -6.2, None),
    "LLL": (list(range(5)), 0.9, -9.3, "X ≤ 0"),
    "LLR": (list(range(5, 9)), 4.2, -9.3, None),
    "LLLL": ([0], -0.6, -12.4, None),
    "LLLR": (list(range(1, 5)), 2.4, -12.4, None),
}
edges = [("root", "L"), ("root", "R"), ("L", "LL"), ("L", "LR"), ("R", "RL"), ("R", "RR"), ("LL", "LLL"),
         ("LL", "LLR"), ("LLL", "LLLL"), ("LLL", "LLLR")]
S = 0.36  # ball spacing
fig, ax = fk.plt.subplots(figsize=(12.6, 9.0))
for a, b in edges:
    xa, ya = nodes[a][1], nodes[a][2]
    xb, yb = nodes[b][1], nodes[b][2]
    ax.annotate("", xy=(xb, yb + 0.62), xytext=(xa, ya - 1.42),
                arrowprops=dict(arrowstyle="-|>", color=fk.TEXT_2, lw=1, shrinkA=0, shrinkB=0))
    ax.text((xa + xb) / 2 + (0.15 if xb > xa else -0.15), (ya + yb) / 2 - 0.25, "да" if xb < xa or b.endswith("L") else "нет",
            fontsize=8, color=fk.TEXT_2, ha="right" if xb < xa else "left")
for name, (pos, cx, cy, split) in nodes.items():
    ys = Y[pos]
    p = ys.mean()
    w = max(len(pos) * S + 0.3, 1.9)
    leaf = split is None
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - 1.42), w, 2.06, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="white", ec=fk.ACCENT if leaf else fk.TEXT_2, lw=2.2 if leaf else 1, zorder=1))
    xs = cx - (len(pos) - 1) * S / 2 + np.arange(len(pos)) * S
    ax.scatter(xs, np.full(len(pos), cy + 0.28), s=62, c=[RED if v else SIR for v in ys], edgecolors="white", linewidths=0.6, zorder=3)
    ax.text(cx, cy - 0.28, f"H = {fk.num(entropy(p) + 0.0, 2)}\nG = {fk.num(gini(p) + 0.0, 2)}", ha="center", va="center",
            fontsize=7.5, color=fk.TEXT, zorder=3, linespacing=1.3)
    if split:
        ax.text(cx, cy - 1.0, split + " ?", ha="center", va="center", fontsize=9, color=fk.TEXT, zorder=3,
                bbox=dict(boxstyle="round,pad=0.2", fc=fk.tint(fk.ACCENT, 0.88), ec="none"))
ax.set_xlim(-2.2, 20.4)
ax.set_ylim(-14.2, 1.0)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Цепочка разбиений слайда 20: H — энтропия, G — Gini; листья в жирной рамке")
fk.save(fig, fk.attachments(4) / "crit-balls-tree.png")

# Checks quoted in the note: a gain table, and sklearn grows the slide's chain under entropy and Gini alike.
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

for name, f, _ in crits:
    root = f(Y.mean())
    gains = [root - weighted(f, t) for t in thresholds]
    print(name, "thresholds with zero gain:", sum(abs(g) < 1e-12 for g in gains), "of", len(gains))
for crit in ("entropy", "gini"):
    m = DecisionTreeClassifier(criterion=crit, random_state=fk.SEED).fit(np.arange(20)[:, None], Y)
    cuts = sorted(float(t) for t in m.tree_.threshold if t > -2)
    print(crit, "thresholds of the grown tree:", cuts, "leaves:", m.get_n_leaves())
