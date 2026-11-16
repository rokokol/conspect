"""The shortest ambiguous word of the code {01, 010, 101}: the words between cuts of different parsings are the vertices of the cycle (lecture 14, sufficiency)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codefig  # noqa: E402
import codegraph  # noqa: E402
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

code = ["01", "010", "101"]
V, arcs = codegraph.build_graph(code)
cycle = codegraph.cycle_through_lambda(V, arcs)
word, first, second = codegraph.parsings_from_cycle(cycle, arcs)
assert cycle == ["", "0", "1", ""] and word == "010101"
assert first == ["010", "101"] and second == ["01", "01", "01"]
assert codegraph.brute_force_ambiguous(code, 5) is None  # no shorter word has two parsings

fill_of = dict(zip(code, dmfig.COLOURS))
fig, ax = plt.subplots(figsize=(7.4, 4.4))
codefig.draw_word(ax, word, 3.0)
ax.text(-0.25, 3.35, "слово", ha="right", va="center", fontsize=11, color=dmfig.INK)
codefig.draw_parsing(ax, first, 1.7, [fill_of[w] for w in first])
ax.text(-0.25, 2.05, "разбиение 1", ha="right", va="center", fontsize=11, color=dmfig.INK)
codefig.draw_parsing(ax, second, 0.4, [fill_of[w] for w in second])
ax.text(-0.25, 0.75, "разбиение 2", ha="right", va="center", fontsize=11, color=dmfig.INK)
codefig.draw_legend(ax, [(fill_of[w], f"кодовое слово {w}") for w in code], 6.9, 3.3)
for x in (2, 3, 4):
    ax.plot([x, x], [0.25, 3.85], color=dmfig.HIGHLIGHT, linestyle=":", linewidth=1.6, zorder=0)
for (x1, x2), name, dy in (((2, 3), r"$\beta_1=0$", 0.0), ((3, 4), r"$\beta_2=1$", 0.45)):
    ax.annotate("", xy=(x1, -0.4), xytext=(x2, -0.4), arrowprops=dict(arrowstyle="<->", color=dmfig.HIGHLIGHT, lw=1.6))
    ax.text((x1 + x2) / 2, -0.68 - dy, name, ha="center", va="center", fontsize=12, color=dmfig.HIGHLIGHT)
ax.text(3.0, 4.1, r"цикл $\Lambda\to0\to1\to\Lambda$: вершины — слова между соседними разрезами разных разбиений",
        ha="center", fontsize=9.5, color=dmfig.INK)
ax.set_xlim(-1.8, 9.6)
ax.set_ylim(-1.5, 4.4)
ax.set_aspect("equal")
ax.axis("off")
dmfig.save(fig, codefig.TOPIC, "cut-points")
