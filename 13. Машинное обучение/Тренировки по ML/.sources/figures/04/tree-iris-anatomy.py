"""The tree of the lecture's first slide: Fisher's iris on two petal features, as a tree and as rectangles."""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.patches import Patch  # noqa: E402
from sklearn.datasets import load_iris  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, plot_tree  # noqa: E402
from tree_common import box_of, draw_splits  # noqa: E402

import figkit as fk  # noqa: E402

iris = load_iris()
X = iris.data[:, 2:4]  # petal length, petal width
y = iris.target
NAMES = ["setosa", "versicolor", "virginica"]
FEATURES = ["длина лепестка", "ширина лепестка"]


def comma_decimals(text):
    """Rewrite the thresholds plot_tree draws with a dot as the decimal comma."""
    return re.sub(r"\d+\.\d+", lambda m: fk.num(float(m.group()), len(m.group().split(".")[1])), text)
# Petal length <= 2.45 and petal width <= 0.8 both cut setosa off perfectly: a tie. sklearn breaks it by a
# random feature order; random_state=2 picks the length, the split the lecturer shows (about 2.5).
m = DecisionTreeClassifier(max_depth=2, random_state=2).fit(X, y)

fig, (ax_t, ax_r) = fk.subplots(1, 2, size=(12.4, 4.9), gridspec_kw={"width_ratios": [1.25, 1]})

# Left: the tree itself; a node is tinted by its dominant class, paler the less pure it is.
notes = plot_tree(m, ax=ax_t, feature_names=["petal length", "petal width"], class_names=NAMES,
                  impurity=False, filled=False, rounded=True, fontsize=8, precision=2)
nt = m.tree_
# plot_tree also returns the "True"/"False" arrow labels; only node boxes carry "samples".
node_notes = [a for a in notes if "samples" in a.get_text()]
for node, note in enumerate(node_notes):
    note.set_text(comma_decimals(note.get_text()))
    n = int(re.search(r"samples = (\d+)", note.get_text()).group(1))
    assert n == nt.n_node_samples[node], "annotation order differs from node ids"
    frac = nt.value[node][0] / nt.value[node][0].sum()
    k = int(np.argmax(frac))
    note.set_color(fk.TEXT)
    note.get_bbox_patch().set(facecolor=fk.tint(fk.CATEGORICAL[k], 0.35 + 0.5 * (1 - frac[k])),
                              edgecolor=fk.TEXT_2, linewidth=0.8)
ax_t.set_title("Дерево глубины 2")

# Right: the same tree as rectangles on the plane.
fk.plot_decision(ax_r, m, X, y, title="Те же правила: прямоугольники")
draw_splits(ax_r, m, box_of(X), lw=1.6)
ax_r.set_xlabel("длина лепестка, см")
ax_r.set_ylabel("ширина лепестка, см")
ax_r.xaxis.set_visible(True)
ax_r.yaxis.set_visible(True)
ax_r.set_xticks([1, 2, 3, 4, 5, 6, 7])
ax_r.set_yticks([0, 0.5, 1, 1.5, 2, 2.5])
ax_r.legend(handles=[Patch(facecolor=fk.CATEGORICAL[k], label=NAMES[k]) for k in range(3)], loc="upper left",
            fontsize=7)
fk.save(fig, fk.attachments(4) / "tree-iris-anatomy.png")

print("thresholds:", [(FEATURES[int(f)], round(float(t), 3)) for f, t in
                      zip(nt.feature, nt.threshold) if f >= 0])
print("train accuracy:", round(m.score(X, y), 4), "leaves", m.get_n_leaves())
print("values:", [np.round(nt.value[i][0] * nt.n_node_samples[i]).astype(int).tolist()
                  for i in range(nt.node_count)])
