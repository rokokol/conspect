"""Three-layer planar waveguide: the layers, the axes and the step profile n(z)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.6, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})

# layers: z runs upwards, the mode runs along x
H = 1.0
ax.add_patch(Rectangle((0, -1.2), 2.6, 1.2, fc=mffig.CLADDING, ec="none"))
ax.add_patch(Rectangle((0, 0), 2.6, H, fc=mffig.CORE, ec="none"))
ax.add_patch(Rectangle((0, H), 2.6, 1.2, fc=mffig.CLADDING, ec="none"))
for z in (0, H):
    ax.axhline(z, color=mffig.MUTED, ls="--", lw=1)
ax.text(1.3, -0.6, r"подложка $n_s$", ha="center", va="center")
ax.text(1.3, H / 2, r"волноводный слой $n_f$", ha="center", va="center")
ax.text(1.3, H + 0.6, r"покровный слой $n_a$", ha="center", va="center")
ax.text(-0.08, 0, r"$z=0$", ha="right", va="center")
ax.text(-0.08, H, r"$z=h$", ha="right", va="center")
ax.annotate("", xy=(2.45, H / 2 + 0.28), xytext=(1.75, H / 2 + 0.28),
            arrowprops=dict(arrowstyle="-|>", color=mffig.INK, lw=1.6))
ax.text(2.1, H / 2 + 0.38, r"$x,\ \beta$", ha="center", color=mffig.INK)
ax.annotate("", xy=(-0.5, 1.9), xytext=(-0.5, -1.0),
            arrowprops=dict(arrowstyle="-|>", color=mffig.INK, lw=1.2))
ax.text(-0.5, 2.02, r"$z$", ha="center")
ax.set_xlim(-0.9, 2.7)
ax.set_ylim(-1.2, 2.2)
ax.axis("off")

# step profile n(z); the guided n_eff lies between n_s and n_f
n_a, n_s, n_f = 1.0, 1.6, 2.2
zz = [(-1.2, 0, n_s), (0, H, n_f), (H, H + 1.2, n_a)]
for z0, z1, n in zz:
    bx.plot([n, n], [z0, z1], color=mffig.INK, lw=2)
for z in (0, H):
    bx.axhline(z, color=mffig.MUTED, ls="--", lw=1)
bx.plot([n_s, n_f], [0, 0], color=mffig.INK, lw=2)
bx.plot([n_a, n_f], [H, H], color=mffig.INK, lw=2)
bx.axvspan(n_s, n_f, color=mffig.AUX, alpha=0.35, lw=0)
bx.axvline(1.95, color=mffig.HIGHLIGHT, lw=1.8)
bx.text(1.98, H + 1.0, r"$n_{\mathrm{eff}}$", color=mffig.INK, ha="left")
bx.set_xlim(0.8, 2.4)
bx.set_ylim(-1.2, 2.2)
bx.set_xticks([n_a, n_s, n_f], [r"$n_a$", r"$n_s$", r"$n_f$"])
bx.set_yticks([])
bx.set_xlabel(r"показатель преломления")
for s in ("top", "right", "left"):
    bx.spines[s].set_visible(False)

fig.tight_layout()
mffig.save(fig, 6, Path(__file__).stem)
