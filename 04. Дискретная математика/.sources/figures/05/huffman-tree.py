"""Huffman tree of the worked example in "Теорема редукции и метод Хаффмана".

Run the file to check the example before it is drawn: the chain of gluings, the code, its cost,
the identity "cost = sum of the glued frequencies" and the optimality of the cost against a
brute force over all length vectors that satisfy the McMillan inequality.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dmfig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

FREQ = {"a1": 30, "a2": 25, "a3": 20, "a4": 10, "a5": 10, "a6": 5}  # in hundredths, the sum is 1
assert sum(FREQ.values()) == 100

# Gluing: the two smallest frequencies; ties go to the symbol with the larger index, and the
# first of the pair gets the symbol 0 when the word is split back.
items = sorted(FREQ.items(), key=lambda kv: -kv[1])
children = {}
glued = []
chain = [[f for _, f in items]]
while len(items) > 2:
    (n1, f1), (n2, f2) = items[-2], items[-1]
    node = f"u{len(children) + 1}"
    children[node] = (n1, n2)
    glued.append(f1 + f2)
    items = sorted(items[:-2] + [(node, f1 + f2)], key=lambda kv: -kv[1])
    chain.append([f for _, f in items])
children["root"] = (items[0][0], items[1][0])
assert glued == [15, 25, 45, 55]
assert chain == [[30, 25, 20, 10, 10, 5], [30, 25, 20, 15, 10], [30, 25, 25, 20], [45, 30, 25], [55, 45]]

code = {}


def split_back(node, word):
    if node in children:
        left, right = children[node]
        split_back(left, word + "0")
        split_back(right, word + "1")
    else:
        code[node] = word


split_back("root", "")
words = list(code.values())
assert not any(u != v and v.startswith(u) for u in words for v in words)  # prefix code
cost = sum(FREQ[s] * len(w) for s, w in code.items())
assert cost == 240 and cost == sum(glued) + 100  # the final two-symbol code costs p + q = 1

# Optimality without a length cap. By McMillan and its converse, the lengths of uniquely decodable
# codes are exactly the vectors with sum 2^-l <= 1. A code of cost at most `cost` has
# p_i * l_i <= cost, so every length is bounded and the search below covers all candidates.
names = list(FREQ)
bound = {s: cost // FREQ[s] for s in names}
KRAFT_SCALE = 2 ** max(bound.values())
cheaper = []
equal = []


def search(i, lengths, spent, kraft):
    if kraft > KRAFT_SCALE:
        return
    rest = sum(FREQ[s] for s in names[i:])  # every remaining word has length at least 1
    if spent + rest > cost:
        return
    if i == len(names):
        (cheaper if spent < cost else equal).append(tuple(lengths))
        return
    s = names[i]
    for length in range(1, bound[s] + 1):
        search(i + 1, lengths + [length], spent + FREQ[s] * length, kraft + KRAFT_SCALE // 2 ** length)


search(0, [], 0, 0)
assert not cheaper and (2, 2, 2, 3, 4, 4) in equal  # no uniquely decodable code is cheaper

# Leaves left to right as the tree is read; x is the leaf's index, a node sits above its children.
order = []


def leaves(node):
    if node in children:
        for child in children[node]:
            leaves(child)
    else:
        order.append(node)


leaves("root")
pos, weight = {}, {}


def place(node, depth):
    if node not in children:
        pos[node] = (float(order.index(node)), -float(depth))
        weight[node] = FREQ[node]
        return
    for child in children[node]:
        place(child, depth + 1)
    pos[node] = (sum(pos[c][0] for c in children[node]) / 2, -float(depth))
    weight[node] = sum(weight[c] for c in children[node])


place("root", 0)
edges = [(v, c) for v in children for c in children[v]]
labels = {v: (v.replace("a", "$a_") + "$" if v in FREQ else dmfig.num(weight[v] / 100, 2)) for v in pos}
fills = {v: dmfig.COLOURS[0] for v in FREQ}

fig, ax = plt.subplots(figsize=(7.4, 6.2))
dmfig.draw_graph(ax, pos, edges, labels=labels, fills=fills, node_size=0.33, label_size=11)
for v, kids in children.items():
    for digit, c in enumerate(kids):
        (x1, y1), (x2, y2) = pos[v], pos[c]
        side = -1 if digit == 0 else 1
        ax.text((x1 + x2) / 2 + side * 0.17, (y1 + y2) / 2 + 0.06, str(digit), ha="center", va="center",
                fontsize=12, color=dmfig.HIGHLIGHT)
for s, (x, y) in pos.items():
    if s in FREQ:
        ax.text(x, y - 0.48, dmfig.num(FREQ[s] / 100, 2), ha="center", va="center", fontsize=11, color=dmfig.INK)
        ax.text(x, y - 0.78, code[s], ha="center", va="center", fontsize=12, color=dmfig.INK)
ax.text(-0.5, -5.6, "под листом: частота и кодовое слово", ha="left", fontsize=10, color=dmfig.INK)
ax.text(-0.5, -5.9, "в розовых узлах: склеенные частоты, у корня их сумма $1$", ha="left", fontsize=10, color=dmfig.INK)
ax.text(-0.5, -6.2, "красная цифра на ребре: символ, приписываемый при расклейке", ha="left", fontsize=10,
        color=dmfig.INK)
ax.set_xlim(-0.7, 5.7)
ax.set_ylim(-6.5, 0.5)
dmfig.save(fig, 5, "huffman-tree")
