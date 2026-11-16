"""Encapsulation layouts for f12: IP-in-IP against GRE, and a VXLAN frame."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from netfig import COURSE, EDGE, FIELD, VIOLET, PEACH, SKY, GREEN, GREY, ACCENT, MUTED, SUBTEXT, P

OUT = COURSE / "content" / "12. Туннели и оверлеи" / "00. Вложения"


def block(ax, x, y, w, h, label, sub, color, fs=11.5):
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=color, edgecolor=EDGE, linewidth=1.4))
    cx = x + w / 2
    if sub:
        ax.text(cx, y + h * 0.62, label, ha="center", va="center", fontsize=fs)
        ax.text(cx, y + h * 0.28, sub, ha="center", va="center", fontsize=fs - 2, color=SUBTEXT)
    else:
        ax.text(cx, y + h / 2, label, ha="center", va="center", fontsize=fs)


def brace(ax, x0, x1, y, text):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.5))
    ax.text((x0 + x1) / 2, y + 0.18, text, ha="center", va="bottom", fontsize=10.5, color=ACCENT)


# IP-in-IP против GRE
fig, ax = plt.subplots(figsize=(12, 5.6))
H = 1.0
ETH = 3.8  # wide enough for "Ethernet" in the body font
rows = [
    ("Исходный пакет", [(ETH, "Ethernet", "14 байт", GREY), (6.0, "IPv4", "20 байт", FIELD), (10.0, "TCP / UDP / ICMP и данные", None, GREEN)], None),
    ("IP-in-IP\nprotocol 4", [(ETH, "Ethernet", "14 байт", GREY), (6.0, "внешний IPv4", "20 байт", PEACH), (6.0, "внутренний IPv4", "20 байт", FIELD), (10.0, "TCP / UDP / ICMP и данные", None, GREEN)], (ETH, ETH + 6.0, "+20 байт → MTU туннеля 1480")),
    ("GRE\nprotocol 47", [(ETH, "Ethernet", "14 байт", GREY), (6.0, "внешний IPv4", "20 байт", PEACH), (3.0, "GRE", "4 байта", VIOLET), (7.2, "IPv4, IPv6, MPLS,\nEthernet…", None, FIELD), (10.0, "данные", None, GREEN)], (ETH, ETH + 9.0, "+24 байта → MTU туннеля 1476")),
]
y = 0.0
for name, fields, br in rows:
    x = 0.0
    for w, label, sub, color in fields:
        block(ax, x, y, w, H, label, sub, color, fs=11)
        x += w
    ax.text(-0.4, y + H / 2, name, ha="right", va="center", fontsize=12)
    if br:
        brace(ax, br[0], br[1], y + H + 0.08, br[2])
    y -= 2.0
ax.set_xlim(-5.0, 33)
ax.set_ylim(y + 1.6, 1.8)
ax.axis("off")
ax.set_title("Заголовки IP-in-IP и GRE поверх IPv4", fontsize=17, pad=10)
plt.tight_layout()
plt.savefig(OUT / "Заголовки IP-in-IP и GRE.png", dpi=150)
plt.close(fig)

# VXLAN
fig, ax = plt.subplots(figsize=(13, 7.2))
H = 1.0
fields = [
    (4.0, "внешний\nEthernet", "14 байт", GREY),
    (5.0, "внешний IPv4", "20 байт", PEACH),
    (3.5, "UDP", "8 байт, dst 4789", SKY),
    (3.5, "VXLAN", "8 байт", VIOLET),
    (4.0, "внутренний\nEthernet", "14 байт", FIELD),
    (6.0, "исходная нагрузка кадра", "IP, ARP…", GREEN),
    (2.0, "FCS", "4 байта", GREY),
]
y0 = 3.2
x = 0.0
xs = []
for w, label, sub, color in fields:
    block(ax, x, y0, w, H, label, sub, color, fs=10.5)
    xs.append((x, w))
    x += w
total_w = x
brace(ax, xs[1][0], xs[4][0] + xs[4][1], y0 + H + 0.1, "50 байт поверх IP-MTU underlay")
ax.text(xs[5][0] + xs[5][1] / 2 + 0.6, y0 - 0.25, "исходный кадр без своего FCS", ha="center", va="top", fontsize=10, color=P["plum"])

# zoom into VXLAN header
vx, vw = xs[3]
zy = 0.0
scale = total_w / 32.0
bits = [(8, "Flags", "8 бит, флаг I = 1", VIOLET), (24, "Reserved", "24 бита", GREY)]
bits2 = [(24, "VNI", "24 бита, ~16,7 млн сегментов", PEACH), (8, "Reserved", "8 бит", GREY)]
x = 0.0
for w, label, sub, color in bits:
    block(ax, x * scale, zy, w * scale, H, label, sub, color, fs=11)
    x += w
x = 0.0
for w, label, sub, color in bits2:
    block(ax, x * scale, zy - H, w * scale, H, label, sub, color, fs=11)
    x += w
ax.plot([vx, 0], [y0, zy + H], color=MUTED, linestyle=(0, (4, 3)), linewidth=1)
ax.plot([vx + vw, total_w], [y0, zy + H], color=MUTED, linestyle=(0, (4, 3)), linewidth=1)
for tick in [0, 8, 16, 24, 32]:
    ax.text(tick * scale, zy - H - 0.35, str(tick), ha="center", va="top", fontsize=10, color=MUTED)
ax.text(total_w / 2, zy - H - 0.85, "номер бита в 32-битном слове заголовка VXLAN", ha="center", va="top", fontsize=10.5, color=MUTED)

ax.set_xlim(-0.5, total_w + 0.5)
ax.set_ylim(zy - H - 1.5, y0 + H + 1.1)
ax.axis("off")
ax.set_title("Кадр VXLAN поверх IPv4", fontsize=17, pad=10)
plt.tight_layout()
plt.savefig(OUT / "Кадр VXLAN поверх IPv4.png", dpi=150)
plt.close(fig)
