"""Bit layout of the IPv6 header for f11 "Заголовок IPv6"."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from netfig import COURSE, EDGE, FIELD, VIOLET, PEACH, GREEN, ACCENT, MUTED, SUBTEXT, P

OUT = COURSE / "content" / "11. IPv6" / "00. Вложения"

fig, ax = plt.subplots(figsize=(11, 8.6))

WORD_W = 32.0
LEFT = 0.0
RIGHT = LEFT + WORD_W

ROW_H = 1.0
TOP = 0.0  # top of the table, y decreases downward


def row(y, h, fields, edge=EDGE):
    x = LEFT
    for w, label, sub, color in fields:
        rect = patches.Rectangle((x, y - h), w, h, facecolor=color, edgecolor=edge, linewidth=1.4)
        ax.add_patch(rect)
        cx = x + w / 2
        if sub:
            ax.text(cx, y - h * 0.38, label, ha="center", va="center", fontsize=12)
            ax.text(cx, y - h * 0.72, sub, ha="center", va="center", fontsize=9.5, color=SUBTEXT)
        else:
            ax.text(cx, y - h / 2, label, ha="center", va="center", fontsize=12)
        x += w
    return y - h


y = TOP

# Row 1: Version | Traffic Class | Flow Label
y = row(y, ROW_H, [
    (4, "Version", "4 бита", FIELD),
    (8, "Traffic Class", "8 бит", VIOLET),
    (20, "Flow Label", "20 бит", PEACH),
])

# Row 2: Payload Length | Next Header | Hop Limit
y = row(y, ROW_H, [
    (16, "Payload Length", "16 бит", FIELD),
    (8, "Next Header", "8 бит", FIELD),
    (8, "Hop Limit", "8 бит", FIELD),
])

# Source Address — one tall block, 128 bit = 4 words
y = row(y, ROW_H * 4, [(32, "Source Address", "128 бит", FIELD)])

# Destination Address — one tall block, 128 bit = 4 words
y = row(y, ROW_H * 4, [(32, "Destination Address", "128 бит", FIELD)])

dst_bottom = y

# dashed separator
ax.plot([LEFT, RIGHT], [dst_bottom, dst_bottom], color=ACCENT, linestyle=(0, (6, 4)), linewidth=1.6)

# extension headers + data block
y = row(y, ROW_H, [(32, "Расширенные заголовки и данные  (по цепочке Next Header)", None, GREEN)])

bottom = y

# bit ruler above the table
ruler_y = TOP + 0.55
for tick in [0, 8, 16, 24, 32]:
    ax.plot([tick, tick], [TOP, TOP + 0.12], color=MUTED, linewidth=1.0, zorder=0)
    ax.text(tick, ruler_y, str(tick), ha="center", fontsize=11, color=MUTED)
ax.text(16, ruler_y + 0.45, "номер бита в 32-битном слове", ha="center", fontsize=11.5, color=MUTED)

# brace marking fixed 40 byte header
brace_x = LEFT - 3.4
ax.annotate("", xy=(brace_x, TOP), xytext=(brace_x, dst_bottom),
            arrowprops=dict(arrowstyle="<->", color=EDGE, lw=1.6))
ax.text(brace_x - 1.05, (TOP + dst_bottom) / 2, "заголовок\nвсегда 40 байт", ha="center", va="center",
        fontsize=11, color=P["plum"], rotation=90)

ax.set_xlim(brace_x - 2.3, RIGHT + 0.5)
ax.set_ylim(bottom - 0.4, ruler_y + 0.9)
ax.axis("off")
ax.set_title("Раскладка заголовка IPv6", fontsize=18, pad=14)

plt.tight_layout()
plt.savefig(OUT / "Раскладка заголовка IPv6.png", dpi=150)
