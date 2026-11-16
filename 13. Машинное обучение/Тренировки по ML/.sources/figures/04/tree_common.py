"""Helpers shared by the decision-tree figures: split lines of a fitted tree drawn over a 2D plot."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402


def box_of(X, margin=0.6):
    """Bounding box (x0, x1, y0, y1) used by fk.plot_decision for the same data."""
    lo, hi = X.min(0) - margin, X.max(0) + margin
    return lo[0], hi[0], lo[1], hi[1]


def split_segments(tree, box):
    """Segments (x0, y0, x1, y1, depth) of every split of a fitted sklearn tree inside box."""
    t = tree.tree_
    out = []

    def walk(node, b, depth):
        if t.children_left[node] < 0:
            return
        j, thr = t.feature[node], t.threshold[node]
        x0, x1, y0, y1 = b
        if j == 0:
            out.append((thr, y0, thr, y1, depth))
            walk(t.children_left[node], (x0, thr, y0, y1), depth + 1)
            walk(t.children_right[node], (thr, x1, y0, y1), depth + 1)
        else:
            out.append((x0, thr, x1, thr, depth))
            walk(t.children_left[node], (x0, x1, y0, thr), depth + 1)
            walk(t.children_right[node], (x0, x1, thr, y1), depth + 1)

    walk(0, box, 1)
    return out


def draw_splits(ax, tree, box, *, newest=None, lw=0.9):
    """Draw the split lines; the ones at depth `newest` are thick ink, the rest thin."""
    for x0, y0, x1, y1, d in split_segments(tree, box):
        fresh = newest is not None and d == newest
        ax.plot([x0, x1], [y0, y1], color=fk.ACCENT if fresh else fk.TEXT_2,
                lw=2.2 if fresh else lw, alpha=1.0 if fresh else 0.8, zorder=4,
                solid_capstyle="butt")
