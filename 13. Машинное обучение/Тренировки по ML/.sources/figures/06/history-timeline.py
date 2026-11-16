"""Timeline of deep learning, 1943-2023: the events of lecture 6 with the dates taken from their papers.

The shaded spans are the lecturer's own periodisation (about ten years after 1969, twelve years up to 2012), not a
dated fact. Gradient boosting (2001) is drawn in another colour: it is the classical method the lecturer sets against
the networks of the 2000s.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

# year, label, height of the label above (+) or below (-) the axis, kind
EVENTS = [
    (1943, "нейрон\nМакКаллока–Питтса", 1.0, "net"),
    (1958, "перцептрон\nРозенблатта", -1.0, "net"),
    (1969, "книга Перцептроны,\nXOR", 1.0, "net"),
    (1986, "backprop\n(Румельхарт, Хинтон,\nУильямс)", -1.0, "net"),
    (1998, "LeNet-5", 1.0, "net"),
    (2001, "градиентный\nбустинг (Фридман)", -1.0, "boost"),
    (2012, "AlexNet", 1.0, "net"),
    (2014, "GAN", -1.0, "net"),
    (2017, "трансформер", 2.0, "net"),
    (2018, "BERT", -1.0, "net"),
    (2020, "GPT-3", 1.0, "net"),
    (2022, "ChatGPT,\nStable Diffusion", -2.0, "net"),
    (2023, "GPT-4, LLaMA", 3.0, "net"),
]
SPANS = [(1969, 1979, "зима AI,\nпо лектору\nоколо 10 лет"), (2000, 2012, "по лектору: сети на втором\nплане 12 лет")]
COLOR = {"net": fk.MODEL_C, "boost": fk.MODEL2_C}

fig, ax = fk.subplots(1, 1, size=(13.6, 5.4))
for a, b, text in SPANS:
    ax.axvspan(a, b, color=fk.P["ash"], alpha=0.35, lw=0)
    ax.text((a + b) / 2, -3.05, text, ha="center", va="bottom", fontsize=7.5, color=fk.TEXT_2)
ax.axhline(0, color=fk.TEXT, lw=1.4)
for year, label, h, kind in EVENTS:
    ax.plot([year, year], [0, h * 0.82], color=COLOR[kind], lw=1.2)
    ax.scatter([year], [0], s=46, color=COLOR[kind], zorder=3, edgecolors="white", linewidths=0.8)
    ax.text(year, h * 0.86, f"{year}\n{label}", ha="center", va="bottom" if h > 0 else "top", fontsize=7.8,
            color=fk.TEXT, linespacing=1.15)
ax.set_xlim(1936, 2030)
ax.set_ylim(-3.1, 3.9)
ax.set_yticks([])
ax.set_xticks(range(1940, 2031, 10))
ax.grid(False)
for side in ("left", "right", "top"):
    ax.spines[side].set_visible(False)
ax.set_title("ключевые даты глубокого обучения")

fk.save(fig, fk.attachments(6) / "history-timeline.png")
