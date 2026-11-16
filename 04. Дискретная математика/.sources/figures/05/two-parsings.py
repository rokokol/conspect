"""The word 010 of the code a->0, b->01, c->10 cut into codewords in two ways (lecture 13)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codefig  # noqa: E402
import codegraph  # noqa: E402
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

code = ["0", "01", "10"]
letters = dict(zip(code, "abc"))
fill_of = dict(zip(code, dmfig.COLOURS))
first, second = codegraph.all_parsings("010", code)
assert first == ["0", "10"] and second == ["01", "0"]

fig, ax = plt.subplots(figsize=(6.4, 3.8))
codefig.draw_word(ax, "010", 3.0)
ax.text(-0.25, 3.35, "слово", ha="right", va="center", fontsize=11, color=dmfig.INK)
codefig.draw_parsing(ax, first, 1.7, [fill_of[w] for w in first], [letters[w] for w in first])
ax.text(-0.25, 2.05, "разбиение 1", ha="right", va="center", fontsize=11, color=dmfig.INK)
codefig.draw_parsing(ax, second, 0.4, [fill_of[w] for w in second], [letters[w] for w in second])
ax.text(-0.25, 0.75, "разбиение 2", ha="right", va="center", fontsize=11, color=dmfig.INK)
ax.text(1.5, 4.1, "у слова $010$ два разбиения на кодовые слова", ha="center", fontsize=10, color=dmfig.INK)
codefig.draw_legend(ax, [(fill_of[w], f"{letters[w]} → {w}") for w in code], 3.6, 3.3)
ax.set_xlim(-1.6, 5.4)
ax.set_ylim(-0.4, 4.4)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, codefig.TOPIC, "two-parsings")
