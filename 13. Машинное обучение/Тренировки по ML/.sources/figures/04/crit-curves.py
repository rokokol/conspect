"""Three impurity criteria of a binary node as functions of p, and what a split gains under each of them."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

# One colour per criterion in every panel and figure. Not the class colours (rule, bow): the ball figures
# of the same note show two classes in exactly those, and a criterion must not read as a class.
C_ENT, C_GINI, C_MIS = fk.P["ribbon"], fk.P["monika"], fk.P["yuri"]


def entropy(p):
    p = np.asarray(p, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.nan_to_num(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


def gini(p):
    return 1 - p**2 - (1 - p) ** 2


def misclass(p):
    return 1 - np.maximum(p, 1 - p)


p = np.linspace(0, 1, 501)

# Figure 1: the curves, as on the lecture slide 23 (log base 2: the entropy peaks at 1).
fig, ax = fk.subplots(1, 1, size=(6.6, 4.3))
ax.plot(p, entropy(p), color=C_ENT, lw=2.2, label="энтропия, $\\log_2$")
ax.plot(p, 2 * gini(p), color=C_GINI, lw=1.6, ls="--", label="2 · Gini")
ax.plot(p, gini(p), color=C_GINI, lw=2.2, label="Gini $=1-p^2-(1-p)^2$")
ax.plot(p, 2 * misclass(p), color=C_MIS, lw=1.6, ls="--", label="2 · ошибка")
ax.plot(p, misclass(p), color=C_MIS, lw=2.2, label="ошибка $=1-\\max(p,1-p)$")
ax.scatter([0.5, 0.5], [1, 0.5], s=30, color=fk.ACCENT, zorder=5)
ax.annotate("1", (0.5, 1), textcoords="offset points", xytext=(8, 2), fontsize=8, color=fk.TEXT)
ax.annotate(fk.num(0.5, 1), (0.5, 0.5), textcoords="offset points", xytext=(8, 4), fontsize=8, color=fk.TEXT)
ax.set_xlabel("p — доля первого класса в узле")
ax.set_ylabel("значение критерия")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.08)
ax.set_title("Три критерия неоднородности")
ax.grid(True)
ax.legend(loc="lower center", fontsize=7)
fk.save(fig, fk.attachments(4) / "crit-curves.png")

# Figure 2: parent p = 0.3 splits into two children of equal weight, p = 0.1 and p = 0.5.
# The weighted children value is the chord of the curve; the gain is the gap between curve and chord.
# All three criteria are scaled to peak 1 so the gaps are comparable.
P0, PL, PR = 0.3, 0.1, 0.5
crits = [("энтропия", entropy, C_ENT), ("2 · Gini", lambda q: 2 * gini(q), C_GINI),
         ("2 · ошибка", lambda q: 2 * misclass(q), C_MIS)]
fig, axes = fk.subplots(1, 3, size=(11.6, 3.7), sharey=True)
for ax, (name, f, col) in zip(axes, crits):
    ax.plot(p, f(p), color=col, lw=2.2)
    fl, fr, f0 = float(f(PL)), float(f(PR)), float(f(P0))
    chord = (fl + fr) / 2
    ax.plot([PL, PR], [fl, fr], color=fk.TEXT_2, lw=1.2, ls="--")
    ax.scatter([PL, PR], [fl, fr], s=34, color=fk.TEXT_2, zorder=5)
    ax.scatter([P0], [chord], s=40, color="white", edgecolors=fk.TEXT, zorder=6)
    ax.scatter([P0], [f0], s=56, color=col, edgecolors=fk.TEXT, zorder=7)  # on top: with zero gain it sits on the chord
    gain = f0 - chord
    ax.plot([P0, P0], [chord, f0], color=fk.ACCENT, lw=3, zorder=4, solid_capstyle="butt")
    ax.annotate(f"прирост {fk.num(gain, 2)}", (P0, (chord + f0) / 2), textcoords="offset points", xytext=(10, 0) if gain > 1e-9 else (12, -16),
                fontsize=9, color=fk.TEXT, va="center")
    ax.text(P0, f0, "родитель  ", ha="right", va="bottom", fontsize=7, color=fk.TEXT)
    ax.set_title(name)
    ax.set_xlabel("p")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.08)
    ax.grid(True)
    print(name, "parent", round(f0, 4), "children avg", round(chord, 4), "gain", round(gain, 4))
axes[0].set_ylabel("значение критерия")
fk.save(fig, fk.attachments(4) / "crit-split-gain.png")
