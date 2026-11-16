"""A weighted K5 and the run of the lecturer's algorithm; the second panel is the exchange step of the correctness proof."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

pos = {1: (0, 2.0), 2: (1.9, 3.4), 3: (3.8, 2.0), 4: (3.1, -0.2), 5: (0.7, -0.2)}
w = {(1, 2): 1, (2, 3): 2, (3, 4): 2, (4, 5): 3, (3, 5): 3, (1, 3): 2,
     (1, 5): 4, (2, 4): 5, (2, 5): 5, (1, 4): 6}
assert set(w) == set(itertools.combinations(pos, 2))
n = len(pos)

# the algorithm: sort by weight, a tie is broken by the list order, skip an edge that closes a cycle
comp = {v: v for v in pos}


def find(v):
    while comp[v] != v:
        v = comp[v]
    return v


chosen, skipped = [], []
for e in sorted(w, key=lambda e: w[e]):
    if len(chosen) == n - 1:
        break
    a, b = find(e[0]), find(e[1])
    if a == b:
        skipped.append(e)
    else:
        comp[a] = b
        chosen.append(e)
print("chosen", chosen, "weight", sum(w[e] for e in chosen), "skipped", skipped)
assert chosen == [(1, 2), (2, 3), (3, 4), (4, 5)] and skipped == [(1, 3)]

def is_tree(t):
    c = {v: v for v in pos}

    def f(v):
        while c[v] != v:
            v = c[v]
        return v
    for a, b in t:
        if f(a) == f(b):
            return False
        c[f(a)] = f(b)
    return True


best = min(sum(w[e] for e in t) for t in itertools.combinations(w, n - 1) if is_tree(t))
assert best == sum(w[e] for e in chosen) == 8
msts = [t for t in itertools.combinations(w, n - 1) if is_tree(t) and sum(w[e] for e in t) == best]
print("all shortest trees", msts)
assert len(msts) == 4

K = [(1, 2), (2, 3), (3, 4), (3, 5)]
e_m, e_out = (4, 5), (3, 5)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 5.4))

colours = {e: dmfig.MUTED for e in w}
colours.update({e: dmfig.HIGHLIGHT for e in chosen})
styles = {e: "--" for e in skipped}
styles.update({e: ":" for e in w if e not in chosen and e not in skipped})
dmfig.draw_graph(ax1, pos, list(w), edge_colors=colours, edge_styles=styles, node_size=0.22, label_size=14)

# a weight label sits on its edge, shifted along it so that the labels of crossing diagonals do not meet
shift = {(1, 3): 0.3, (2, 4): 0.3, (3, 5): 0.72, (1, 4): 0.3, (2, 5): 0.3, (1, 5): 0.5}


def label(ax, e, text, t=None):
    (x1, y1), (x2, y2) = pos[e[0]], pos[e[1]]
    t = shift.get(e, 0.5) if t is None else t
    ax.text(x1 + t * (x2 - x1), y1 + t * (y2 - y1), text, ha="center", va="center", fontsize=11,
            color=dmfig.INK, zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", fc=dmfig.P["paper"], ec="none"))


for e in w:
    label(ax1, e, str(w[e]))
ax1.set_title(f"алгоритм: вес остова ${sum(w[e] for e in chosen)}$", color=dmfig.INK, fontsize=12)
def legend(ax, handles, ncol):
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=ncol, frameon=True,
              fancybox=False, edgecolor=dmfig.EDGE, facecolor=dmfig.P["paper"], fontsize=9.5,
              labelcolor=dmfig.INK, borderpad=0.7)


legend(ax1, [
    Line2D([0], [0], color=dmfig.HIGHLIGHT, lw=2, label="выбрано"),
    Line2D([0], [0], color=dmfig.MUTED, lw=2, ls="--", label="замкнуло бы цикл"),
    Line2D([0], [0], color=dmfig.MUTED, lw=2, ls=":", label="не понадобилось"),
], 2)

# panel 2: K (another shortest tree), K1 = K + e_m closes the cycle 3-4-5, K2 = K1 - e
from matplotlib.patches import Polygon, Patch  # noqa: E402
ax2.add_patch(Polygon([pos[3], pos[4], pos[5]], closed=True, facecolor=dmfig.tint(dmfig.HIGHLIGHT, 0.85),
                      edgecolor="none", zorder=0))
colours2 = {e: dmfig.MUTED for e in w}
colours2.update({e: dmfig.INK for e in K})
colours2[e_m] = dmfig.HIGHLIGHT
colours2[e_out] = dmfig.VERTEX_EDGE
styles2 = {e: ":" for e in w if e not in K and e != e_m}
styles2[e_out] = "--"
dmfig.draw_graph(ax2, pos, list(w), edge_colors=colours2, edge_styles=styles2, node_size=0.22, label_size=14)
for e in K + [e_m]:
    label(ax2, e, {e_m: "$e_m$: 3", e_out: "$e$: 3"}.get(e, str(w[e])))
ax2.set_title("обмен: $K_1=K+e_m$, $K_2=K_1-e$", color=dmfig.INK, fontsize=12)
legend(ax2, [
    Line2D([0], [0], color=dmfig.INK, lw=2, label="рёбра $K$"),
    Line2D([0], [0], color=dmfig.HIGHLIGHT, lw=2, label="добавленное ребро $e_m$"),
    Line2D([0], [0], color=dmfig.VERTEX_EDGE, lw=2, ls="--", label="выброшенное ребро $e$"),
    Line2D([0], [0], color=dmfig.MUTED, lw=2, ls=":", label="прочие рёбра $K_5$"),
    Patch(facecolor=dmfig.tint(dmfig.HIGHLIGHT, 0.85), label="цикл в $K_1$"),
], 2)
for ax in (ax1, ax2):
    ax.set_xlim(-0.6, 4.4)
    ax.set_ylim(-1.2, 3.9)
dmfig.save(fig, 4, "mst-kruskal")
