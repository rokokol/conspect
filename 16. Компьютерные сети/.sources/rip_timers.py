"""RIP timers after the last received update, for f09 "Протокол RIP"."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from netfig import COURSE, P

OUT = COURSE / "content" / "09. Динамическая маршрутизация" / "00. Вложения"

INVALID = P["skirt"]
HOLD = P["plum"]
FLUSH = P["jacket"]
GONE = P["bow"]
UPDATE = P["ribbon"]
RULE = P["jacket"]

plt.rcParams.update({"font.size": 12})
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=100)

rows = {"Update": 4, "Invalid": 3, "Holddown": 2, "Flush": 1, "Состояние": 0}
h = 0.5

# periodic updates before the last one
for t in (-90, -60, -30, 0):
    ax.annotate("", xy=(t, rows["Update"] - 0.25), xytext=(t, rows["Update"] + 0.3),
                arrowprops=dict(arrowstyle="-|>", color=UPDATE, lw=2))
ax.text(0, rows["Update"] + 0.38, "последний апдейт", ha="center", va="bottom", color=UPDATE)
ax.text(-45, rows["Update"] - 0.42, "каждые 30 с", ha="center", va="center", color=UPDATE)


def bar(row, start, end, color, label, hatch=None, alpha=0.85, textcolor=P["paper"]):
    y = rows[row] - h / 2
    ax.add_patch(Rectangle((start, y), end - start, h, facecolor=color, edgecolor=color,
                           hatch=hatch, alpha=alpha, lw=1.5))
    ax.text((start + end) / 2, rows[row], label, ha="center", va="center", color=textcolor)


bar("Invalid", 0, 180, INVALID, "180 с")
bar("Holddown", 180, 240, HOLD, "заморозка")
ax.add_patch(Rectangle((240, rows["Holddown"] - h / 2), 120, h, facecolor="none",
                       edgecolor=HOLD, hatch="//", lw=1.5, ls="--"))
ax.text(300, rows["Holddown"], "не дотикивает до 360 с", ha="center", va="center", color=HOLD, fontsize=10.5,
        bbox=dict(facecolor=P["paper"], edgecolor="none", pad=1))
bar("Flush", 0, 240, FLUSH, "240 с", textcolor=P["ink"])

bar("Состояние", 0, 180, INVALID, "маршрут используется", alpha=0.35, textcolor=P["ink"])
bar("Состояние", 180, 240, HOLD, "метрика 16", alpha=0.35, textcolor=P["ink"])
ax.text(305, rows["Состояние"], "удалён из RIP-базы\nи таблицы", ha="center", va="center", color=GONE)

for t in (180, 240, 360):
    ax.axvline(t, color=RULE, ls=":", lw=1)

ax.set_xlim(-100, 380)
ax.set_ylim(-0.6, 4.9)
ax.set_yticks(list(rows.values()))
ax.set_yticklabels(list(rows.keys()))
ax.set_xticks([-90, -60, -30, 0, 60, 120, 180, 240, 300, 360])
ax.set_xlabel("секунды от последнего полученного апдейта")
ax.set_title("Таймеры RIP (значения Cisco по умолчанию)", fontsize=15)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.tight_layout()
fig.savefig(OUT / "Таймеры RIP после последнего апдейта.png")
