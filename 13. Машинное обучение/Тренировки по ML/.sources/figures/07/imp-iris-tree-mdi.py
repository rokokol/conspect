"""Impurity importance of one tree on Fisher's iris, assembled by hand from the nodes and checked against sklearn.

The tree sees all four features and the train part only; every number comes from the train part, because that is where
impurity importance is measured.
"""
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402

iris = load_iris()
FEATURES = ["длина чашелистика", "ширина чашелистика", "длина лепестка", "ширина лепестка"]
EN = ["sepal length", "sepal width", "petal length", "petal width"]
NAMES = ["setosa", "versicolor", "virginica"]
Xtr, Xte, ytr, yte = train_test_split(iris.data, iris.target, test_size=0.3, random_state=fk.SEED,
                                      stratify=iris.target)
m = DecisionTreeClassifier(max_depth=3, random_state=fk.SEED).fit(Xtr, ytr)
t = m.tree_

# Weighted impurity decrease of every internal node; the root holds all N objects.
N = t.weighted_n_node_samples[0]
gain = {}
for node in range(t.node_count):
    if t.children_left[node] == -1:
        continue
    l, r = t.children_left[node], t.children_right[node]
    gain[node] = (t.weighted_n_node_samples[node] * t.impurity[node]
                  - t.weighted_n_node_samples[l] * t.impurity[l]
                  - t.weighted_n_node_samples[r] * t.impurity[r]) / N
by_feature = np.zeros(4)
for node, g in gain.items():
    by_feature[t.feature[node]] += g
by_feature_norm = by_feature / by_feature.sum()
assert np.allclose(by_feature_norm, m.feature_importances_), "hand formula differs from sklearn"

fig, (ax_t, ax_b) = fk.subplots(1, 2, size=(12.6, 5.0), gridspec_kw={"width_ratios": [1.35, 1]})
notes = plot_tree(m, ax=ax_t, feature_names=EN, class_names=NAMES, impurity=True, node_ids=True,
                  filled=False, rounded=True, fontsize=7, precision=2)
for note in notes:
    note.set_text(note.get_text().replace(".", ","))
node_notes = [a for a in notes if "samples" in a.get_text()]
node_colors = {}
for node, note in enumerate(node_notes):
    n = int(re.search(r"samples = (\d+)", note.get_text()).group(1))
    assert n == t.n_node_samples[node], "annotation order differs from node ids"
    frac = t.value[node][0] / t.value[node][0].sum()
    k = int(np.argmax(frac))
    note.set_color(fk.TEXT)
    node_color = fk.tint(fk.CATEGORICAL[k], 0.35 + 0.5 * (1 - frac[k]))
    node_colors[node] = node_color
    note.get_bbox_patch().set(facecolor=node_color, edgecolor=fk.TEXT_2, linewidth=0.8)
ax_t.set_title("Дерево глубины 3 на обучающей части")

# Stacked bars: one segment per split, filled with the colour of its node in the tree on the left.
order = np.argsort(-by_feature_norm)
bottom = np.zeros(4)
thin = 0
for node, g in sorted(gain.items()):
    f = int(t.feature[node])
    share = g / by_feature.sum()
    x = list(order).index(f)
    ax_b.bar(x, share, bottom=bottom[f], color=node_colors[node], edgecolor=fk.TEXT_2, linewidth=0.8, width=0.6)
    if share > 0.04:
        ax_b.text(x, bottom[f] + share / 2, f"#{node}", ha="center", va="center", fontsize=8, color=fk.TEXT)
    else:
        # a sliver too thin for a label inside: name it beside the bar, stacked in the order of the segments
        y_label = bottom[f] + share / 2 + 0.04 * thin
        ax_b.plot([x + 0.3, x + 0.36], [bottom[f] + share / 2, y_label], color=fk.TEXT_2, lw=0.8)
        ax_b.text(x + 0.38, y_label, f"#{node}: {fk.num(share, '.1%')}", ha="left", va="center", fontsize=8, color=fk.TEXT)
        thin += 1
    bottom[f] += share
ax_b.set_xticks(range(4), [FEATURES[f].replace(" ", "\n") for f in order], fontsize=8)
ax_b.set_ylabel("доля суммарного прироста")
ax_b.set_title("Важность: вклады узлов в сумму")
ax_b.grid(True, axis="y")
fig.tight_layout()
fk.save(fig, fk.attachments(7) / "imp-iris-tree-mdi.png")

print("train accuracy", round(m.score(Xtr, ytr), 3), "test accuracy", round(m.score(Xte, yte), 3), "N", int(N))
for node in range(t.node_count):
    kind = "leaf" if t.children_left[node] == -1 else f"{EN[t.feature[node]]} <= {t.threshold[node]:.2f}"
    print(node, kind, "n", int(t.n_node_samples[node]), "counts", np.round(t.value[node][0] * t.n_node_samples[node]).astype(int).tolist(),
          "gini", round(float(t.impurity[node]), 3), "gain" , round(gain.get(node, 0), 4))
print("per feature normalised", dict(zip(EN, np.round(by_feature_norm, 3))))
print("sklearn", np.round(m.feature_importances_, 3))

# The same tree family without the two petal columns: the zero of the sepal columns is a property of the first tree.
m2 = DecisionTreeClassifier(max_depth=3, random_state=fk.SEED).fit(Xtr[:, :2], ytr)
print("without petals: importances", dict(zip(EN[:2], np.round(m2.feature_importances_, 3))),
      "train acc", round(m2.score(Xtr[:, :2], ytr), 3), "test acc", round(m2.score(Xte[:, :2], yte), 3))

# Path of the first held-out virginica object through the first tree.
i = int(np.flatnonzero(yte == 2)[0])
path = m.decision_path(Xte[i:i + 1]).indices
print("object", i, "features", np.round(Xte[i], 2).tolist(), "-> predicted", NAMES[int(m.predict(Xte[i:i + 1])[0])])
for node in path:
    if t.children_left[node] != -1:
        went_left = Xte[i, t.feature[node]] <= t.threshold[node]
        print("  node", node, f"{EN[t.feature[node]]} <= {t.threshold[node]:.2f}:", "yes" if went_left else "no")
    else:
        print("  leaf", node)
