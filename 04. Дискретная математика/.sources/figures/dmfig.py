"""Shared drawing helpers for the figures of this course: graphs, trees, codes.

Every colour is a ddlc-palette role or its tint. A script names a colour by its
meaning here (VERTEX, EDGE, HIGHLIGHT, COLOURS for vertex colourings), so the
same convention reads the same way in every figure of the course.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

P = ddlc_theme.P
tint = ddlc_theme.tint
num = ddlc_theme.num  # every number of a label: num(0.25) gives 0,25
keep_dots = ddlc_theme.keep_dots

INK = P["ink"]
VERTEX = tint(P["dot"], 0.0)           # an ordinary vertex fill
VERTEX_EDGE = P["plum"]                # vertex outline
EDGE = P["rule"]                       # an ordinary edge
HIGHLIGHT = P["bow"]                   # the edge or vertex the figure is about
MUTED = P["ash"]                       # removed or inactive parts
# Distinct fills for proper colourings, in the order c1, c2, ...
COLOURS = [P["sayori-eye"], P["natsuki"], P["monika-eye"], P["sayori"], tint(P["yuri"], 0.45)]

TOPICS = {
    1: "01. Функции алгебры логики",
    2: "02. Полнота и замкнутые классы",
    3: "03. k-значная логика",
    4: "04. Графы",
    5: "05. Алфавитное кодирование",
    6: "06. Коды, исправляющие ошибки",
    7: "07. Автоматы и схемы",
}


def out_dir(topic: int) -> Path:
    """The attachments folder of a topic, created with its .nomedia marker."""
    d = COURSE / "content" / TOPICS[topic] / "00. Вложения"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".nomedia").touch()
    return d


def draw_graph(ax, pos, edges, labels=None, fills=None, edge_colors=None,
               edge_styles=None, curved=None, node_size=0.13, label_size=12):
    """Draw an undirected graph.

    pos: {vertex: (x, y)}; edges: [(u, v), ...]; labels: {vertex: text}, defaults to the key;
    fills: {vertex: colour}; edge_colors / edge_styles: {(u, v): value};
    curved: {(u, v): rad} bends an edge as an arc (for loops of drawings, multigraph pairs)
    """
    from matplotlib.patches import Circle, FancyArrowPatch

    labels = labels or {v: str(v) for v in pos}
    fills = fills or {}
    edge_colors = edge_colors or {}
    edge_styles = edge_styles or {}
    curved = curved or {}
    for e in edges:
        u, v = e
        key = e if e in edge_colors or e in edge_styles or e in curved else (v, u)
        ax.add_patch(FancyArrowPatch(
            pos[u], pos[v], arrowstyle="-", shrinkA=0, shrinkB=0,
            connectionstyle=f"arc3,rad={curved.get(key, 0)}",
            color=edge_colors.get(key, EDGE), linestyle=edge_styles.get(key, "-"),
            linewidth=2, zorder=1))
    for v, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), node_size, facecolor=fills.get(v, VERTEX),
                            edgecolor=VERTEX_EDGE, linewidth=1.6, zorder=2))
        ax.text(x, y, labels[v], ha="center", va="center", fontsize=label_size,
                color=INK, zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()


def save(fig, topic: int, name: str) -> Path:
    """Write <name>.png into the topic's attachments, with a tight frame."""
    path = out_dir(topic) / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(path)
    return path
