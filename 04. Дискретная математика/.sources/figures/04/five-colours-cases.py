"""Cases of the five colour theorem: a vertex of degree 5, the c1/c3 swap, the cycle that blocks c2/c4 (lecture 12)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402

C = dmfig.COLOURS  # C[0] is c1, ..., C[4] is c5
HL = dmfig.HIGHLIGHT

# v in the centre; v1..v5 clockwise from the top, so their order around v is the order of the colours c1..c5
R = 1.1
pos = {"v": (0.0, 0.0)}
for i in range(5):
    a = math.pi / 2 - 2 * math.pi * i / 5
    pos[f"v{i + 1}"] = (R * math.cos(a), R * math.sin(a))
labels = {"v": "$v$", **{f"v{i}": f"$v_{i}$" for i in range(1, 6)}}
star = [("v", f"v{i}") for i in range(1, 6)]
base_fill = {f"v{i}": C[i - 1] for i in range(1, 6)}
base_fill["v"] = dmfig.P["paper"]


def panel(ax, title, extra_pos=None, extra_edges=(), extra_fill=None, extra_labels=None, fills=None,
          edge_colors=None, v_fill=None):
    p = dict(pos)
    p.update(extra_pos or {})
    lab = dict(labels)
    lab.update(extra_labels or {})
    f = dict(base_fill)
    f.update(extra_fill or {})
    f.update(fills or {})
    if v_fill is not None:
        f["v"] = v_fill
    dmfig.draw_graph(ax, p, star + list(extra_edges), labels=lab, fills=f, edge_colors=edge_colors or {},
                     node_size=0.2, label_size=10)
    ax.set_title(title, color=dmfig.INK, fontsize=11)
    ax.set_xlim(-2.9, 3.2)
    ax.set_ylim(-2.2, 2.5)


fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.6))
(ax1, ax2), (ax3, ax4) = axes

# 1: only v is uncoloured, the neighbours use all five colours
panel(ax1, "1. $v$ без цвета,\nу соседей все пять цветов")

# 2: case b1, the c1/c3 chain from v1 stays away from v3
chain = {"a": (-0.95, 2.0), "b": (-2.1, 1.35)}
panel(ax2, "2. $A$ — вершины, достижимые из $v_1$\nпо цветам $c_1/c_3$; $v_3$ среди них нет",
      extra_pos=chain,
      extra_edges=[("v1", "a"), ("a", "b")],
      extra_fill={"a": C[2], "b": C[0]},
      extra_labels={"a": "", "b": ""},
      edge_colors={("v1", "a"): HL, ("a", "b"): HL})
ax2.add_patch(Ellipse((-1.0, 1.6), 3.7, 1.55, angle=-14, fill=False, edgecolor=HL, linestyle="--",
                      linewidth=1.8, zorder=0))
ax2.text(-2.55, 2.25, "$A$", color=HL, fontsize=14)

# 3: swap c1 and c3 inside A, v takes the freed c1
panel(ax3, "3. после обмена в $A$ цвета $c_1$\nнет у соседей, $v$ получает $c_1$",
      extra_pos=chain,
      extra_edges=[("v1", "a"), ("a", "b")],
      extra_fill={"a": C[0], "b": C[2]},
      extra_labels={"a": "", "b": ""},
      fills={"v1": C[2]}, v_fill=C[0],
      edge_colors={("v1", "a"): HL, ("a", "b"): HL})
ax3.add_patch(Ellipse((-1.0, 1.6), 3.7, 1.55, angle=-14, fill=False, edgecolor=HL, linestyle="--",
                      linewidth=1.8, zorder=0))
ax3.text(-2.55, 2.25, "$A$", color=HL, fontsize=14)

# 4: case b2, the path L from v1 to v3 closes a cycle through v; v2 inside, v4 outside
ext = {"p": (2.1, 1.7), "q": (2.5, -0.5), "s": (1.75, 0.55), "t": (-1.5, -1.8)}
panel(ax4, "4. путь $L$ и вершина $v$ замыкают цикл $Z$:\n$v_2$ внутри, $v_4$ снаружи",
      extra_pos=ext,
      extra_edges=[("v1", "p"), ("p", "q"), ("q", "v3"), ("v2", "s"), ("v4", "t")],
      extra_fill={"p": C[2], "q": C[0], "s": C[3], "t": C[1]},
      extra_labels={"p": "", "q": "", "s": "", "t": ""},
      edge_colors={("v1", "p"): HL, ("p", "q"): HL, ("q", "v3"): HL, ("v", "v1"): HL, ("v", "v3"): HL,
                   ("v2", "s"): dmfig.INK, ("v4", "t"): dmfig.INK})
ax4.text(2.0, -1.6, "путь по цветам $c_2/c_4$ от $v_2$\nзаперт внутри цикла", ha="center", fontsize=9.5, color=dmfig.INK)

handles = [Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor=C[i],
                  markeredgecolor=dmfig.VERTEX_EDGE, label=f"$c_{i + 1}$") for i in range(5)]
handles.append(Line2D([0], [0], color=HL, linewidth=2, label="путь по $c_1/c_3$ и цикл $Z$"))
handles.append(Line2D([0], [0], color=dmfig.INK, linewidth=2, label="путь по $c_2/c_4$"))
fig.legend(handles=handles, loc="lower center", ncol=7, frameon=False, fontsize=9.5, columnspacing=1.2, labelcolor=dmfig.INK)
fig.subplots_adjust(bottom=0.11, hspace=0.25, wspace=0.05)
dmfig.save(fig, 4, "five-colours-cases")
