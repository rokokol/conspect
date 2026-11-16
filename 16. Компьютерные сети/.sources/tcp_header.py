"""Bit layout of the TCP header for f08 "Заголовок TCP и установление соединения"."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from netfig import COURSE, EDGE, FIELD, VIOLET, PEACH, GREEN, GREY, ACCENT, MUTED, SUBTEXT, P

OUT = COURSE / "content" / "08. Транспортный уровень" / "00. Вложения"

U = 1.0  # width of one bit
H = 1.0  # height of one 32-bit word

# (row, start_bit, width_bits, name, size, fill, small)
fields = [
    (0, 0, 16, "Source Port", "16 бит", FIELD, False),
    (0, 16, 16, "Destination Port", "16 бит", FIELD, False),
    (1, 0, 32, "Sequence Number", "32 бита", FIELD, False),
    (2, 0, 32, "Acknowledgment Number", "32 бита", FIELD, False),
    (3, 0, 4, "Data\nOffset", "4 бита", FIELD, True),
    (3, 4, 4, "Reserved", "4 бита", GREY, True),
    (3, 16, 16, "Window", "16 бит", FIELD, False),
    (4, 0, 16, "Checksum", "16 бит", FIELD, False),
    (4, 16, 16, "Urgent Pointer", "16 бит", FIELD, False),
]
flags_ecn = ["CWR", "ECE"]
flags_classic = ["URG", "ACK", "PSH", "RST", "SYN", "FIN"]
ECN_FILL, CLASSIC_FILL = VIOLET, PEACH

fig, ax = plt.subplots(figsize=(18, 10.2), dpi=100)
ax.set_xlim(-17, 33.5)
ax.set_ylim(-8.2, 2.3)
ax.axis("off")


def y_of(row):
    return -row * H


for row, sb, wb, name, size, f, small in fields:
    y = y_of(row)
    ax.add_patch(Rectangle((sb, y - H), wb, H, facecolor=f, edgecolor=EDGE, lw=2))
    fs = 13 if small else 18
    if "\n" in name:
        ax.text(sb + wb / 2, y - 0.36, name, ha="center", va="center", fontsize=12)
        ax.text(sb + wb / 2, y - 0.82, size, ha="center", va="center", fontsize=11, color=SUBTEXT)
    else:
        ax.text(sb + wb / 2, y - 0.38, name, ha="center", va="center", fontsize=fs)
        ax.text(sb + wb / 2, y - 0.72, size, ha="center", va="center", fontsize=13 if not small else 11, color=SUBTEXT)

# flags: 8 one-bit cells in row 3, bits 8..15
y = y_of(3)
for i, fl in enumerate(flags_ecn + flags_classic):
    f = ECN_FILL if i < len(flags_ecn) else CLASSIC_FILL
    ax.add_patch(Rectangle((8 + i, y - H), 1, H, facecolor=f, edgecolor=EDGE, lw=2))
    ax.text(8 + i + 0.5, y - 0.5, fl, ha="center", va="center", fontsize=10.5, rotation=90)

# options and data
y = y_of(5)
ax.add_patch(Rectangle((0, y - H), 32, H, facecolor=GREY, edgecolor=EDGE, lw=2))
ax.text(16, y - 0.5, "Options + Padding  (0–40 байт, кратно 4)", ha="center", va="center", fontsize=17)
y = y_of(6)
ax.add_patch(Rectangle((0, y - H), 32, H, facecolor=GREEN, edgecolor=EDGE, lw=2))
ax.text(16, y - 0.5, "Данные приложения", ha="center", va="center", fontsize=17)
ax.plot([-0.6, 32.6], [y, y], color=ACCENT, lw=2.5, ls="--")

# bit ruler
for b in (0, 8, 16, 24, 32):
    ax.plot([b, b], [0, 0.35], color=MUTED, lw=1.3)
    ax.text(b, 0.55, str(b), ha="center", va="bottom", fontsize=13, color=MUTED)
ax.text(16, 1.35, "номер бита в 32-битном слове", ha="center", va="bottom", fontsize=15, color=MUTED)

# brackets
ax.annotate("", xy=(-1.1, 0.05), xytext=(-1.1, -5.05),
            arrowprops=dict(arrowstyle="<->", color=EDGE, lw=2))
ax.text(-1.7, -2.5, "обязательная часть\n20 байт", ha="right", va="center", fontsize=15, color=P["plum"])
ax.annotate("", xy=(-11.0, 0.05), xytext=(-11.0, -6.05),
            arrowprops=dict(arrowstyle="<->", color=SUBTEXT, lw=2))
ax.text(-11.6, -3.6, "заголовок\nData Offset × 4\n= 20–60 байт", ha="right", va="center", fontsize=15, color=SUBTEXT)

# key for the flag fills, drawn with the fills themselves
key_y = -7.55
for x0, fill, text in ((3.0, ECN_FILL, "флаги ECN (RFC 3168)"), (17.0, CLASSIC_FILL, "флаги исходного TCP")):
    ax.add_patch(Rectangle((x0, key_y - 0.25), 0.9, 0.5, facecolor=fill, edgecolor=EDGE, lw=1.5))
    ax.text(x0 + 1.4, key_y, text, ha="left", va="center", fontsize=13, color=SUBTEXT)

ax.set_title("Раскладка заголовка TCP", fontsize=20, pad=10)
fig.savefig(OUT / "Раскладка заголовка TCP.png", bbox_inches="tight")
