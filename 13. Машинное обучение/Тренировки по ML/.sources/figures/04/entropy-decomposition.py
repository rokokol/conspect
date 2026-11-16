"""H(p, q) = H(p) + KL(p || q) for p = 0.3: the gap above the entropy line, and stacked bars for four predictions q."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

P0 = 0.3


def h(p):
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def ce(p, q):
    return -p * np.log2(q) - (1 - p) * np.log2(1 - q)


fig, axes = fk.subplots(1, 2, size=(10.8, 4.0), gridspec_kw=dict(width_ratios=[1.35, 1]))

ax = axes[0]
q = np.linspace(0.004, 0.996, 800)
curve = ce(P0, q)
hp = h(P0)
ax.plot(q, curve, color=fk.MODEL_C, lw=2.4, label="$H(p,q)$")
ax.axhline(hp, color=fk.TEXT_2, lw=1.4, ls="--", label=f"$H(p)={fk.num(hp, 2, math=True)}$")
ax.fill_between(q, hp, curve, color=fk.MODEL2_C, alpha=0.25, label="$\\mathrm{KL}(p\\Vert q)$")
qs = 0.6
ax.plot([qs], [ce(P0, qs)], "o", color=fk.ACCENT, zorder=4)
ax.annotate(f"$q={fk.num(0.6, 1, math=True)}$: $H(p,q)={fk.num(ce(P0, qs), 2, math=True)}$", (qs, ce(P0, qs)), (0.14, 2.7),
            arrowprops=dict(arrowstyle="->", color=fk.TEXT_2), color=fk.TEXT, fontsize=8)
ax.plot([qs, qs], [hp, ce(P0, qs)], color=fk.ACCENT, lw=1.6)
ax.text(qs + 0.02, (hp + ce(P0, qs)) / 2, f"KL = {fk.num(ce(P0, qs) - hp, 2)}", color=fk.TEXT, fontsize=8, va="center")
ax.plot([P0], [hp], "o", color=fk.ACCENT, zorder=4)
ax.set_ylim(0, 4.5)
ax.set_xlim(0, 1)
ax.set_xlabel(f"предсказание $q$ при $p={fk.num(0.3, 1, math=True)}$")
ax.set_ylabel("бит")
ax.set_title("зазор над энтропией")
ax.legend(loc="upper center")
ax.grid(True)

ax = axes[1]
qs_bars = [0.1, 0.3, 0.6, 0.9]
xs = np.arange(len(qs_bars))
kl = [ce(P0, v) - hp for v in qs_bars]
ax.bar(xs, [hp] * len(xs), color=fk.TEXT_2, width=0.6, label="$H(p)$")
ax.bar(xs, kl, bottom=[hp] * len(xs), color=fk.MODEL2_C, width=0.6, label="$\\mathrm{KL}(p\\Vert q)$")
for x, v in zip(xs, qs_bars):
    ax.text(x, ce(P0, v) + 0.08, fk.num(ce(P0, v), 2), ha="center", color=fk.TEXT, fontsize=8)
ax.set_xticks(xs)
ax.set_xticklabels([f"$q={fk.num(v, None, math=True)}$" for v in qs_bars])
ax.set_ylim(0, 3.2)
ax.set_ylabel("$H(p,q)$, бит")
ax.set_title("слагаемые для четырёх $q$")
ax.legend(loc="upper left")
ax.grid(True, axis="y")

fig.tight_layout()
fk.save(fig, fk.attachments(4) / "entropy-decomposition.png")
