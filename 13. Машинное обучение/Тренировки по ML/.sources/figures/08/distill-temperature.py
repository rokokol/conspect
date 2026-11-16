"""The student's zones by temperature T, the train/validation/test curve over T and the CV grid of (T, alpha) on moons.

alpha is the weight of the hard-label term. Teacher and grid as in distill-hard-vs-soft.py. The zones and the curve use the
alpha of the best soft cell of the CV grid; the validation curve is the CV accuracy of that alpha at each T, and the
marked T is its maximum. The test part is only shown. Output: distill-temperature.png
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import distill_common as dc  # noqa: E402
import figkit as fk  # noqa: E402

HIDDEN = (4,)
TEMPS = (1.0, 2.0, 4.0, 8.0, 16.0)
ALPHAS = (0.0, 0.25, 0.5)

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
params = dc.choose_teacher(Xtr, ytr)
best, grid = dc.choose_student(params, Xtr, ytr, HIDDEN, TEMPS, ALPHAS)
soft = {k: v for k, v in grid.items() if k[1] < 1.0}
a_star = max(soft, key=soft.get)[1]
teacher = dc.fit_teacher(params, Xtr, ytr)
students = [dc.fit_student(teacher, Xtr, ytr, hidden=HIDDEN, T=T, alpha=a_star) for T in TEMPS]
train = [s.score(Xtr, ytr) for s in students]
test = [s.score(Xte, yte) for s in students]
val = [grid[(T, a_star)] for T in TEMPS]
hard_cv = grid[(1.0, 1.0)]
print(f"teacher {params}, alpha*={a_star:g}, best overall {best}, hard CV {hard_cv:.3f}")
for T, tr, va, te in zip(TEMPS, train, val, test):
    print(f"T={T:g}\ttrain {tr:.3f}\tCV {va:.3f}\ttest {te:.3f}")

fig = fk.plt.figure(figsize=(3.0 * len(TEMPS), 3.0 + 3.6))
gs = fig.add_gridspec(2, len(TEMPS), height_ratios=[3.0, 3.6])
for j, (T, s) in enumerate(zip(TEMPS, students)):
    ax = fig.add_subplot(gs[0, j])
    fk.plot_decision(ax, s, Xtr, ytr, X_test=Xte, y_test=yte)
    ax.set_title(f"T={fk.num(T, None)}", fontsize=9)

ax = fig.add_subplot(gs[1, :3])
b = fk.complexity_curve(ax, list(TEMPS), train, test, xlabel="температура T", ylabel="точность", val=val, log=True)
ax.axhline(hard_cv, color=fk.MODEL2_C, lw=1.2, ls="-.")
ax.text(2.2, hard_cv, "ученик на жёстких метках, валидация", fontsize=7, color=fk.TEXT, va="bottom", ha="left")
ax.set_xticks(TEMPS)
ax.set_xticklabels([fk.num(t, None) for t in TEMPS])
ax.minorticks_off()
print(f"chosen T at alpha={a_star:g}: {TEMPS[b]:g}")

ax = fig.add_subplot(gs[1, 3:])
M = np.array([[grid[(T, a)] for T in TEMPS] for a in ALPHAS])
# ddlc_seq ends in plum, the colour of the train curve next to this panel: use a neutral ink ramp here.
cmap = LinearSegmentedColormap.from_list("ink_ramp", [fk.tint(fk.TEXT, 0.95), fk.tint(fk.TEXT, 0.5)])
im = ax.imshow(M, cmap=cmap, aspect="auto", origin="lower")
for i, a in enumerate(ALPHAS):
    for j, T in enumerate(TEMPS):
        ax.text(j, i, fk.num(M[i, j], 3), ha="center", va="center", fontsize=7, color=fk.TEXT)
bi, bj = ALPHAS.index(max(soft, key=soft.get)[1]), TEMPS.index(max(soft, key=soft.get)[0])
ax.add_patch(fk.plt.Rectangle((bj - 0.5, bi - 0.5), 1, 1, fill=False, ec=fk.ACCENT, lw=2))
ax.set_xticks(range(len(TEMPS)))
ax.set_xticklabels([fk.num(t, None) for t in TEMPS])
ax.set_yticks(range(len(ALPHAS)))
ax.set_yticklabels([fk.num(a, None) for a in ALPHAS])
ax.set_xlabel("температура T")
ax.set_ylabel("вес жёсткой части")
ax.set_title("Точность на валидации (CV)", fontsize=9)
fig.tight_layout()
fk.save(fig, fk.attachments(8) / "distill-temperature.png")
