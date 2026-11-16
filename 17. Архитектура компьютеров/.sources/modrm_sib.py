"""Bit-field diagram for the ModR/M and SIB bytes, in the vault's protocol-header style."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "06. Машинные команды IA-32 и Intel 64" / "00. Вложения"

FILL = P["dot"]
BORDER = P["plum"]

fig, axes = plt.subplots(1, 2, figsize=(9, 2.6))

specs = [
    ("Байт ModR/M", [("Mod", 2), ("Reg/\nOpcode", 3), ("R/M", 3)]),
    ("Байт SIB", [("Scale", 2), ("Index", 3), ("Base", 3)]),
]

for ax, (title, fields) in zip(axes, specs):
    x = 0
    bit = 8
    for name, width in fields:
        ax.add_patch(Rectangle((x, 0), width, 1, facecolor=FILL, edgecolor=BORDER, linewidth=1.5))
        ax.text(x + width / 2, 0.5, f"{name}\n{width} бит", ha="center", va="center", fontsize=10)
        # bit-index ticks at each field boundary
        ax.text(x, 1.08, str(bit - 1), ha="center", va="bottom", fontsize=8, color=P["jacket"])
        bit -= width
        x += width
    ax.text(x, 1.08, "0", ha="center", va="bottom", fontsize=8, color=P["jacket"])
    ax.set_xlim(-0.15, 8.15)
    ax.set_ylim(-0.25, 1.35)
    ax.set_title(title, fontsize=12, pad=14)
    ax.axis("off")

fig.tight_layout()
fig.savefig(OUT / "Раскладка ModRM и SIB.png", dpi=200, bbox_inches="tight")
