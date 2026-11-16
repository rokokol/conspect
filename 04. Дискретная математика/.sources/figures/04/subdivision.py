"""Edge subdivision and two homeomorphic graphs (lecture 12): the step, then K4 subdivided once and three times."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402


def smooth(g):
    """Erase vertices of degree 2 (the lecturer's check); a graph of cycles only is left to the caller."""
    g = nx.Graph(g)
    while True:
        v = next((v for v in g if g.degree(v) == 2), None)
        if v is None:
            return g
        a, b = list(g[v])
        assert not g.has_edge(a, b), "smoothing would create a multi-edge"
        g.remove_node(v)
        g.add_edge(a, b)


fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(12.4, 3.9), gridspec_kw={"width_ratios": [1, 1.25, 1.25]})
NEW = dmfig.tint(dmfig.HIGHLIGHT, 0.55)

# the operation: (u, v) is replaced by (u, w) and (w, v)
dmfig.draw_graph(ax0, {"u": (0, 2.4), "v": (3, 2.4)}, [("u", "v")], node_size=0.2, label_size=14)
dmfig.draw_graph(ax0, {"u": (0, 0.6), "w": (1.5, 0.6), "v": (3, 0.6)}, [("u", "w"), ("w", "v")],
                 fills={"w": NEW}, node_size=0.2, label_size=14)
ax0.annotate("", xy=(1.5, 1.2), xytext=(1.5, 1.9), arrowprops=dict(arrowstyle="-|>", color=dmfig.INK, lw=1.6))
ax0.set_xlim(-0.5, 3.5)
ax0.set_ylim(-0.4, 3.0)
ax0.set_title("подразделение ребра (u, v)", color=dmfig.INK, fontsize=11)

K4 = {1: (0, 0), 2: (3.0, 0), 3: (1.5, 2.6), 4: (1.5, 0.95)}
k4_edges = [(1, 2), (2, 3), (3, 1), (1, 4), (2, 4), (3, 4)]


def subdivided(cuts):
    """K4 with the given edges subdivided once; returns positions, edges and the new vertices."""
    pos, edges, new = dict(K4), [], []
    for e in k4_edges:
        if e in cuts:
            w = f"w{len(new) + 1}"
            (x1, y1), (x2, y2) = K4[e[0]], K4[e[1]]
            pos[w] = ((x1 + x2) / 2, (y1 + y2) / 2)
            edges += [(e[0], w), (w, e[1])]
            new.append(w)
        else:
            edges.append(e)
    return pos, edges, new


labels = lambda pos, new: {v: ("" if v in new else str(v)) for v in pos}  # noqa: E731
pos1, e1, new1 = subdivided([(1, 2)])
pos2, e2, new2 = subdivided([(1, 2), (3, 1), (3, 4)])

# both smooth to K4, so they are homeomorphic; they are not isomorphic (different p)
g1, g2 = nx.Graph(e1), nx.Graph(e2)
assert (g1.number_of_nodes(), g1.number_of_edges()) == (5, 7)
assert (g2.number_of_nodes(), g2.number_of_edges()) == (7, 9)
assert not nx.is_isomorphic(g1, g2)
assert nx.is_isomorphic(smooth(g1), smooth(g2)) and nx.is_isomorphic(smooth(g1), nx.complete_graph(4))

for ax, (pos, edges, new), title in ((ax1, (pos1, e1, new1), "G₁: p = 5, q = 7"),
                                     (ax2, (pos2, e2, new2), "G₂: p = 7, q = 9")):
    dmfig.draw_graph(ax, pos, edges, labels=labels(pos, new), fills={w: NEW for w in new},
                     node_size=0.17, label_size=13)
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.4, 3.0)
    ax.set_title(title, color=dmfig.INK, fontsize=11)

fig.text(0.5, 0.0, "цветные вершины степени 2 появились при подразделении; стерев их, из G₁ и G₂ получаем K₄",
         ha="center", fontsize=10, color=dmfig.INK)
dmfig.save(fig, 4, "subdivision")
