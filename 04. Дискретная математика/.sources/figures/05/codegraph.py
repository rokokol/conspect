"""The code graph G_phi of an alphabetic code and the checks behind the notes of topic 05.

Run the file to verify every code example of the notes with asserts: prefix, suffix and
uniform classes, the ambiguity of a->0, b->01, c->10, the graph of that code, and the
criterion "unique decodability <=> no directed cycle through the empty word" against two
independent oracles (the Sardinas-Patterson test and a brute-force search for a word with
two parsings). Figure scripts of this folder import the builders below.
"""
import itertools
import random
from collections import deque

EMPTY = ""  # the vertex Lambda = beta_0


def is_prefix_code(code):
    return not any(u != v and v.startswith(u) for u in code for v in code)


def is_suffix_code(code):
    return not any(u != v and v.endswith(u) for u in code for v in code)


def is_uniform(code):
    return len({len(w) for w in code}) == 1


def max_split(word, code):
    """The largest number of codewords whose concatenation is `word`, or None if there is no split."""
    best = [None] * (len(word) + 1)
    best[0] = 0
    for i in range(1, len(word) + 1):
        for w in code:
            if i >= len(w) and word.endswith(w, 0, i) and best[i - len(w)] is not None:
                cand = best[i - len(w)] + 1
                if best[i] is None or cand > best[i]:
                    best[i] = cand
    return best[len(word)]


def split_witness(word, code, at_least):
    """A list of codewords with concatenation `word` and length >= at_least, or None."""
    memo = {}

    def go(i):
        if i == len(word):
            return [[]]
        if i not in memo:
            memo[i] = [[w] + rest for w in code if word.startswith(w, i) for rest in go(i + len(w))]
        return memo[i]

    for parts in go(0):
        if len(parts) >= at_least:
            return parts
    return None


def vertices(code):
    """Words that are a proper beginning and a proper end of some codewords, plus Lambda first."""
    heads = {w[:k] for w in code for k in range(1, len(w))}
    tails = {w[k:] for w in code for k in range(1, len(w))}
    return [EMPTY] + sorted(heads & tails, key=lambda s: (len(s), s))


def build_graph(code):
    """Return (V, arcs); arcs maps (beta_i, beta_j) to a list of (B_l, [codewords of D])."""
    V = vertices(code)
    arcs = {}
    for bl in code:
        for bi in V:
            if not bl.startswith(bi):
                continue
            for bj in V:
                if len(bi) + len(bj) > len(bl) or not bl.endswith(bj):
                    continue
                d = bl[len(bi):len(bl) - len(bj)]
                need = 2 if (bi == EMPTY and bj == EMPTY) else 1 if (bi == EMPTY or bj == EMPTY) else 0
                parts = split_witness(d, code, need)
                if parts is not None:
                    arcs.setdefault((bi, bj), []).append((bl, parts))
    return V, arcs


def cycle_through_lambda(V, arcs):
    """A shortest directed cycle Lambda -> ... -> Lambda as a vertex list [Lambda, ..., Lambda], or None."""
    succ = {v: [] for v in V}
    for (u, v) in arcs:
        succ[u].append(v)
    if EMPTY in succ[EMPTY]:
        return [EMPTY, EMPTY]
    prev = {EMPTY: None}
    queue = deque([EMPTY])
    while queue:
        u = queue.popleft()
        if u != EMPTY and EMPTY in succ[u]:
            path = [u]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            return path[::-1] + [EMPTY]
        for v in succ[u]:
            if v not in prev:
                prev[v] = u
                queue.append(v)
    return None


def parsings_from_cycle(cycle, arcs):
    """The word beta_0 D_0 beta_1 D_1 ... beta_n D_n beta_0 and its two parsings, as in the proof."""
    steps = [arcs[(cycle[i], cycle[i + 1])][0] for i in range(len(cycle) - 1)]  # (c_i, D_i as a list)
    first, second, word = [], [], ""
    for i, (c, d) in enumerate(steps):
        beta_i, beta_next = cycle[i], cycle[i + 1]
        assert c == beta_i + "".join(d) + beta_next
        if i % 2 == 0:
            first.append(c)
            second.extend(d)
        else:
            first.extend(d)
            second.append(c)
    for i, (c, d) in enumerate(steps):
        word += cycle[i] + "".join(d)
    assert word == "".join(first) == "".join(second)
    return word, first, second


def all_parsings(word, code):
    """Every way to cut `word` into codewords."""
    if not word:
        return [[]]
    return [[w] + rest for w in code if word.startswith(w) for rest in all_parsings(word[len(w):], code)]


def sardinas_patterson(code):
    """True if the code is uniquely decodable (an oracle independent of G_phi)."""
    code = set(code)

    def dangling(a, b):
        return {y[len(x):] for x in a for y in b if y != x and y.startswith(x)}

    seen = set()
    s = dangling(code, code)
    while s:
        if s & code:
            return False
        key = frozenset(s)
        if key in seen:
            return True
        seen.add(key)
        s = dangling(code, s) | dangling(s, code)
    return True


def brute_force_ambiguous(code, max_len):
    """A word with two parsings and at most max_len symbols, or None."""
    parsings = {EMPTY: 1}  # word -> number of its parsings, filled in order of length
    by_length = {0: [EMPTY]}
    for n in range(max_len):
        for word in by_length.get(n, []):
            for w in code:
                if n + len(w) <= max_len:
                    longer = word + w
                    if longer not in parsings:
                        parsings[longer] = 0
                        by_length.setdefault(len(longer), []).append(longer)
                    parsings[longer] += parsings[word]
    # parsings[word] is final once every shorter word has been expanded, which the loop order guarantees
    return next((w for w, k in parsings.items() if k > 1), None)


def verify():
    # classes of codes
    assert is_uniform(["00", "01", "10", "11"]) and is_prefix_code(["00", "01", "10", "11"])
    assert is_suffix_code(["00", "01", "10", "11"])
    assert is_prefix_code(["0", "10", "11"]) and not is_suffix_code(["0", "10", "11"])
    assert is_suffix_code(["0", "01", "11"]) and not is_prefix_code(["0", "01", "11"])
    for code in ([ "0", "01", "10"],):
        assert not is_prefix_code(code) and not is_suffix_code(code) and not is_uniform(code)
    # a prefix code that is not uniform: the three classes overlap but are distinct
    assert is_prefix_code(["0", "10", "11"]) and not is_uniform(["0", "10", "11"])

    # the lecturer's example a->0, b->01, c->10
    code = ["0", "01", "10"]
    names = dict(zip(code, "abc"))
    assert all_parsings("010", code) == [["0", "10"], ["01", "0"]]
    assert "".join(names[w] for w in all_parsings("010", code)[0]) == "ac"
    assert "".join(names[w] for w in all_parsings("010", code)[1]) == "ba"
    assert all_parsings("100", code) == [["10", "0"]]  # "ca": the word on the board has one parsing
    shortest = min((w for n in range(1, 4) for w in
                    ("".join(p) for p in itertools.product("01", repeat=n))
                    if len(all_parsings(w, code)) > 1), key=len)
    assert shortest in ("010", "101") and len(shortest) == 3
    assert [w for w in map("".join, itertools.product("01", repeat=3)) if len(all_parsings(w, code)) > 1] == ["010"]
    V, arcs = build_graph(code)
    assert V == ["", "0", "1"]
    assert set(arcs) == {("", "1"), ("1", ""), ("0", "1"), ("1", "0")}
    cycle = cycle_through_lambda(V, arcs)
    assert cycle == ["", "1", ""]
    word, p1, p2 = parsings_from_cycle(cycle, arcs)
    assert word == "010" and p1 == ["01", "0"] and p2 == ["0", "10"]

    # the examples of the note "Критерий взаимной однозначности кода"
    V, arcs = build_graph(["01", "010", "101"])
    assert V == ["", "0", "1", "01", "10"]
    cycle = cycle_through_lambda(V, arcs)
    assert cycle == ["", "0", "1", ""]
    word, p1, p2 = parsings_from_cycle(cycle, arcs)
    assert word == "010101" and p1 == ["010", "101"] and p2 == ["01", "01", "01"]
    assert brute_force_ambiguous(["01", "010", "101"], 5) is None
    assert [d for _, d in (arcs[(a, b)][0] for a, b in zip(cycle, cycle[1:]))] == [["01"], [], ["01"]]
    code = ["0", "01", "110"]
    V, arcs = build_graph(code)
    assert V == ["", "0", "1"] and set(arcs) == {("", "1"), ("0", "1")}
    assert cycle_through_lambda(V, arcs) is None and sardinas_patterson(code)
    assert brute_force_ambiguous(code, 16) is None
    assert not is_prefix_code(code) and not is_suffix_code(code)

    # a prefix code has no cycle through Lambda, a loop elsewhere does not matter
    V, arcs = build_graph(["0", "10", "11"])
    assert V == ["", "1"] and set(arcs) == {("1", ""), ("1", "1")}
    assert cycle_through_lambda(V, arcs) is None

    # the criterion on random codes against both oracles
    rng = random.Random(2026)
    checked = {"ambiguous": 0, "unique": 0, "long": 0}
    for _ in range(4000):
        r = rng.randint(2, 5)
        code = list({"".join(rng.choice("01") for _ in range(rng.randint(1, 4))) for _ in range(r)})
        if len(code) < 2:
            continue
        V, arcs = build_graph(code)
        cycle = cycle_through_lambda(V, arcs)
        ud = sardinas_patterson(code)
        assert (cycle is None) == ud, code
        if cycle is None:
            assert brute_force_ambiguous(code, 14) is None, code
            checked["unique"] += 1
        else:
            word, p1, p2 = parsings_from_cycle(cycle, arcs)
            assert p1 != p2 and all(w in code for w in p1 + p2), code
            # the parsings differ already in the first word: the first word of the second is a proper beginning of the first
            assert p1[0].startswith(p2[0]) and len(p2[0]) < len(p1[0]), code
            assert "".join(p1) == "".join(p2) == word
            checked["ambiguous"] += 1
            checked["long"] += len(cycle) > 3
    assert checked["long"] > 0
    return checked


if __name__ == "__main__":
    print(verify())
