"""Balls around the code words of K={0000, 0111} in E_2^4: radius 1 corrects one error, radius 2 detects two (lectures 16-17).

E_2^4 is drawn as a tesseract: the outer cube holds the words with first bit 0, the inner cube those with first bit 1.
Every claim the figure makes is asserted before it is drawn.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

N = 4
CODE = ["0000", "0111"]


def rho(a, b):
    return sum(x != y for x, y in zip(a, b))


words = ["".join(t) for t in itertools.product("01", repeat=N)]
edges = [(a, b) for a, b in itertools.combinations(words, 2) if rho(a, b) == 1]
assert len(words) == 16 and len(edges) == 32


def ball(centre, r):
    return {w for w in words if rho(w, centre) <= r}


def pos_of(w):
    b1, b2, b3, b4 = map(int, w)
    # offsets found by a grid search: no two vertices closer than 0.5, no vertex near a foreign edge
    s, d = (3.0, (0.4, 0.3)) if b1 == 0 else (0.8, (0.5, -0.4))
    return (s * ((b3 - 0.5) + d[0] * (b2 - 0.5)), s * ((b4 - 0.5) + d[1] * (b2 - 0.5)))


pos = {w: pos_of(w) for w in words}

rho_min = min(rho(a, b) for a, b in itertools.combinations(CODE, 2))
assert rho_min == 3
b1, b2 = (ball(c, 1) for c in CODE)
assert len(b1) == len(b2) == 5 and not b1 & b2  # radius 1: disjoint, so one error is corrected
c1, c2 = (ball(c, 2) for c in CODE)
assert len(c1) == len(c2) == 11 and c1 & c2  # radius 2: the balls meet ...
assert CODE[1] not in c1 and CODE[0] not in c2  # ... but neither holds the other code word
overlap = c1 & c2
assert overlap == {"0001", "0010", "0011", "0100", "0101", "0110"}
print("balls r=1:", sorted(b1), sorted(b2), "| r=2 overlap:", sorted(overlap), "| outside r=1:", sorted(set(words) - b1 - b2))

A, B = dmfig.COLOURS[0], dmfig.COLOURS[1]
BOTH = dmfig.tint(dmfig.HIGHLIGHT, 0.35)
OUTSIDE = dmfig.tint(dmfig.MUTED, 0.75)  # neutral: a word in no ball must not look like a ball colour


def panel(ax, balls, title):
    fills, edge_colors = {}, {}
    for w in words:
        inside = [i for i, bl in enumerate(balls) if w in bl]
        fills[w] = BOTH if len(inside) == 2 else (A, B)[inside[0]] if inside else OUTSIDE
    shared = balls[0] & balls[1]
    for u, v in edges:
        if {u, v} <= shared:
            edge_colors[(u, v)] = BOTH
        elif not ({u, v} & shared):
            ins = [{u, v} <= bl for bl in balls]
            if any(ins):
                edge_colors[(u, v)] = (A, B)[ins.index(True)]
    dmfig.draw_graph(ax, pos, edges, labels={w: w for w in words}, fills=fills, edge_colors=edge_colors,
                     node_size=0.21, label_size=7.5)
    for c in CODE:
        x, y = pos[c]
        ax.add_patch(Circle((x, y), 0.29, fill=False, edgecolor=dmfig.INK, linewidth=2.2, zorder=4))
    ax.set_title(title, color=dmfig.INK, fontsize=11.5)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 5.6))
panel(ax1, (b1, b2), "Шары радиуса $1$ не пересекаются:\nкод исправляет $1$ ошибку")
panel(ax2, (c1, c2), "Шары радиуса $2$ пересекаются, но чужих кодовых слов\nв них нет: код обнаруживает $2$ ошибки")
ax1.title.set_fontsize(10.5)
ax2.title.set_fontsize(10.5)
key = [
    Line2D([0], [0], marker="o", color="none", markerfacecolor=A, markeredgecolor=dmfig.VERTEX_EDGE, ms=10,
           label="шар вокруг $0000$"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor=B, markeredgecolor=dmfig.VERTEX_EDGE, ms=10,
           label="шар вокруг $0111$"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor=BOTH, markeredgecolor=dmfig.VERTEX_EDGE, ms=10,
           label="в обоих шарах"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor=OUTSIDE, markeredgecolor=dmfig.VERTEX_EDGE,
           ms=10, label="вне шаров"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=dmfig.INK, markeredgewidth=2.2,
           ms=13, label="кодовое слово"),
]
fig.legend(handles=key, loc="lower center", ncol=5, frameon=False, fontsize=10, labelcolor=dmfig.INK,
           bbox_to_anchor=(0.5, -0.02))
fig.text(0.5, 0.075, "внешний куб: слова с первым разрядом $0$, внутренний: с первым разрядом $1$; ребро соединяет слова на расстоянии $1$",
         ha="center", color=dmfig.INK, fontsize=9)
fig.subplots_adjust(bottom=0.16)
dmfig.save(fig, 6, "code-balls")
