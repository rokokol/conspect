"""Reference answers for the tests of dmcore.js, written to fixtures.json.

Each answer comes from a method other than the one dmcore.js uses:
  Zhegalkin polynomial  sympy.logic.boolalg.ANFform
  formula vectors       sympy expressions evaluated by substitution
  precedence cases      Python's own operators and `not`, `<=`, `==`
  class membership      the definition by brute force: all affine functions for L,
                        all tuple pairs for M, all complementary pairs for S
  Nelson's method       prime implicants by the definition, brute force
  spanning trees        networkx: minimum_spanning_tree and SpanningTreeIterator
  code graph            the definition by brute force; unique decodability by Sardinas-Patterson
  Huffman's code        exhaustive search over length vectors under Kraft, and the textbook heap algorithm
  Hamming code          the definition: all words of E_2^n with even sums over every D_i, by enumeration
  automata              R_m by the definition (all words of length m) and shortest experiments by search
  the rest              added with their pages

Usage: python export_fixtures.py   (writes fixtures.json next to this file)
"""
import heapq
import itertools
import json
import math
import random
from fractions import Fraction
from pathlib import Path

import networkx as nx
import sympy
from sympy.logic.boolalg import ANFform, And, Equivalent, Implies, Not, Or, Xor

HERE = Path(__file__).resolve().parent
RNG = random.Random(20261003)


# ------------------------------------------------------------------ boolean

def bits(i, n):
    return [(i >> (n - 1 - k)) & 1 for k in range(n)]


def symbols(n):
    return sympy.symbols(" ".join(f"x{k}" for k in range(1, n + 1)))


def anf_monomials(vec, n):
    """Monomial numbers of the Zhegalkin polynomial, by sympy's ANFform."""
    xs = symbols(n)
    xs = (xs,) if n == 1 else xs
    expr = ANFform(list(xs), vec)
    terms = list(expr.args) if isinstance(expr, Xor) else [expr]
    out = []
    for t in terms:
        if t is sympy.true:
            out.append(0)
        elif t is sympy.false:
            continue
        else:
            factors = list(t.args) if isinstance(t, And) else [t]
            out.append(sum(1 << (n - int(str(f)[1:])) for f in factors))
    # The polynomial must give back the function: a guard on the reference itself.
    for i in range(1 << n):
        b = bits(i, n)
        v = 0
        for m in out:
            if all(b[k] for k in range(n) if (m >> (n - 1 - k)) & 1):
                v ^= 1
        assert v == vec[i], (vec, out)
    return sorted(out)


def classes_by_definition(vec, n):
    last = (1 << n) - 1
    t0 = vec[0] == 0
    t1 = vec[last] == 1
    s = all(vec[i] != vec[last - i] for i in range(last + 1))
    m = all(not (vec[a] == 1 and vec[b] == 0) for a in range(last + 1) for b in range(last + 1) if a & b == a)
    # L: some a0 xor a1 x1 xor ... xor an xn has this vector.
    linear = False
    for coeffs in itertools.product([0, 1], repeat=n + 1):
        affine = [coeffs[0] ^ (sum(c & x for c, x in zip(coeffs[1:], bits(i, n))) & 1) for i in range(last + 1)]
        if affine == vec:
            linear = True
            break
    return {"T0": t0, "T1": t1, "L": linear, "S": s, "M": m}


def function_cases():
    cases = []
    for n in (1, 2, 3):
        for code in range(1 << (1 << n)):
            cases.append((n, [(code >> ((1 << n) - 1 - i)) & 1 for i in range(1 << n)]))
    cases += [(4, [RNG.randint(0, 1) for _ in range(16)]) for _ in range(1500)]
    cases += [(4, [0] * 16), (4, [1] * 16), (4, [i & 1 for i in range(16)]), (4, [(i >> 3) & 1 for i in range(16)])]
    out = []
    for n, vec in cases:
        cls = classes_by_definition(vec, n)
        out.append({
            "n": n, "vec": vec,
            "monomials": anf_monomials(vec, n),
            "minterms": [i for i, v in enumerate(vec) if v == 1],
            "maxterms": [i for i, v in enumerate(vec) if v == 0],
            "classes": cls,
        })
    return out


SPELL = {
    "and": ["&", "∧", "*", "·"], "or": ["|", "∨"], "xor": ["^", "⊕"],
    "imp": ["->", "→", "⇒"], "eqv": ["<->", "≡", "↔", "=="], "not": ["!", "¬", "~"],
}
SYMPY = {"and": And, "or": Or, "xor": Xor, "imp": Implies, "eqv": Equivalent}


def random_tree(depth, n):
    if depth == 0 or RNG.random() < 0.2:
        if RNG.random() < 0.1:
            return ("const", RNG.randint(0, 1))
        return ("var", RNG.randint(1, n))
    if RNG.random() < 0.2:
        return ("not", random_tree(depth - 1, n))
    op = RNG.choice(list(SYMPY))
    return (op, random_tree(depth - 1, n), random_tree(depth - 1, n))


def to_text(t):
    """Fully parenthesised, so the text does not depend on precedence."""
    if t[0] == "const":
        return str(t[1])
    if t[0] == "var":
        return RNG.choice([f"x{t[1]}", f"x{t[1]}", "xyzw"[t[1] - 1], f"x{'₀₁₂₃₄'[t[1]]}"])
    if t[0] == "not":
        return RNG.choice(SPELL["not"]) + to_text(t[1])
    return "(" + to_text(t[1]) + " " + RNG.choice(SPELL[t[0]]) + " " + to_text(t[2]) + ")"


def to_sympy(t, xs):
    if t[0] == "const":
        return sympy.true if t[1] else sympy.false
    if t[0] == "var":
        return xs[t[1] - 1]
    if t[0] == "not":
        return Not(to_sympy(t[1], xs))
    return SYMPY[t[0]](to_sympy(t[1], xs), to_sympy(t[2], xs))


def formula_cases():
    out = []
    for _ in range(400):
        n = RNG.randint(1, 4)
        tree = random_tree(4, n)
        xs = symbols(4)
        expr = to_sympy(tree, xs)
        vec = []
        for i in range(1 << n):
            b = bits(i, n) + [0] * (4 - n)
            v = expr.xreplace({xs[k]: bool(b[k]) for k in range(4)})
            vec.append(1 if v == sympy.true or v is True else 0)
        out.append({"n": n, "text": to_text(tree), "vec": vec})
    return out


# Each case: our text and the same function written in Python with its own precedence,
# where `^`, `&` and `|` bind as in the course (& over ^ over |), not as `not`.
PRECEDENCE = [
    ("x1 | x2 & x3", "x1 or (x2 and x3)"),
    ("x1 & x2 | x3", "(x1 and x2) or x3"),
    ("x1 | x2 ^ x3", "x1 or (x2 != x3)"),
    ("x1 ^ x2 & x3", "x1 != (x2 and x3)"),
    ("x1 ^ x2 | x3 ^ x1", "(x1 != x2) or (x3 != x1)"),
    ("!x1 & x2", "(not x1) and x2"),
    ("!x1 | x2 -> x3", "(((not x1) or x2) <= x3)"),
    ("x1 -> x2 -> x3", "(x1 <= (x2 <= x3))"),
    ("x1 -> x2 | x3", "(x1 <= (x2 or x3))"),
    ("x1 <-> x2 -> x3", "(x1 == (x2 <= x3))"),
    ("x1 -> x2 <-> x3", "((x1 <= x2) == x3)"),
    ("x1 <-> x2 <-> x3", "((x1 == x2) == x3)"),
    ("!!x1", "x1"),
    ("!(x1 & x2) | x3", "(not (x1 and x2)) or x3"),
    ("x ^ y ^ x & y", "(x != y) != (x and y)"),
]


def precedence_cases():
    out = []
    for ours, py in PRECEDENCE:
        n = 3
        vec = []
        for i in range(1 << n):
            env = dict(zip(["x1", "x2", "x3"], map(bool, bits(i, n))))
            env.update({"x": env["x1"], "y": env["x2"], "z": env["x3"]})
            vec.append(int(bool(eval(py, {}, env))))  # noqa: S307 - the strings are literals above
        out.append({"n": n, "text": ours, "vec": vec})
    return out


BAD_FORMULAS = ["", "x1 &", "(x1 | x2", "x1 x2", "x1 + x2", "x5", "x1 | | x2", ")", "x1 -> ", "2", "x1 = x2", "xy", "!"]


# ------------------------------------------------------------------- Nelson

def prime_implicants(vec, n):
    """All prime implicants by the definition: elementary conjunctions (per variable absent,
    positive or negated) that are implicants and stay so under no deletion of a literal."""
    def is_implicant(term):
        for i in range(1 << n):
            b = bits(i, n)
            if all(b[v - 1] == (0 if neg else 1) for v, neg in term) and not vec[i]:
                return False
        return True

    primes = []
    for choice in itertools.product([None, 0, 1], repeat=n):
        term = [(k + 1, c == 0) for k, c in enumerate(choice) if c is not None]
        if not term or not is_implicant(term):
            continue
        if any(is_implicant(term[:k] + term[k + 1:]) for k in range(len(term)) if len(term) > 1):
            continue
        primes.append(term)
    return sorted(primes)


def cnf_cases():
    out = []
    for _ in range(300):
        n = RNG.randint(2, 5)
        clauses = []
        for _ in range(RNG.randint(1, 5)):
            vs = RNG.sample(range(1, n + 1), RNG.randint(1, min(3, n)))
            clauses.append([(v, RNG.random() < 0.5) for v in sorted(vs)])
        xs = symbols(5)
        expr = And(*[Or(*[Not(xs[v - 1]) if neg else xs[v - 1] for v, neg in c]) for c in clauses])
        vec = []
        for i in range(1 << n):
            b = bits(i, n) + [0] * (5 - n)
            vec.append(1 if expr.xreplace({xs[k]: bool(b[k]) for k in range(5)}) == sympy.true else 0)
        text = " & ".join("(" + " | ".join(("!" if neg else "") + f"x{v}" for v, neg in c) + ")" for c in clauses)
        primes = prime_implicants(vec, n) if any(vec) else []
        out.append({"n": n, "text": text, "clauses": [[[v, neg] for v, neg in c] for c in clauses],
                    "vec": vec, "primes": [[[v, neg] for v, neg in p] for p in primes]})
    return out


# ------------------------------------------------------ shortest spanning tree

def mst_cases():
    """Weighted K_n with many ties: networkx gives the minimum weight and every minimum tree."""
    out = []
    # the first graph is the K5 of the note; weights follow the order of the (a, b) pairs
    graphs = [(5, [{(1, 2): 1, (2, 3): 2, (3, 4): 2, (4, 5): 3, (3, 5): 3, (1, 3): 2,
                    (1, 5): 4, (2, 4): 5, (2, 5): 5, (1, 4): 6}[e] for e in itertools.combinations(range(1, 6), 2)])]
    for _ in range(120):
        n = RNG.randint(3, 6)
        graphs.append((n, [RNG.randint(1, RNG.choice([2, 3, 6])) for _ in range(n * (n - 1) // 2)]))
    for n, weights in graphs:
        G = nx.Graph()
        for (a, b), w in zip(itertools.combinations(range(1, n + 1), 2), weights):
            G.add_edge(a, b, weight=w)
        best = nx.minimum_spanning_tree(G).size(weight="weight")
        minimum = []
        for T in nx.SpanningTreeIterator(G, weight="weight", minimum=True):
            if T.size(weight="weight") > best:
                break
            minimum.append(sorted(tuple(sorted(e)) for e in T.edges()))
        total = sum(1 for _ in nx.SpanningTreeIterator(G)) if n <= 5 else n ** (n - 2)
        out.append({"n": n, "weights": weights, "min": best, "minTrees": sorted(minimum), "total": total})
    return out


# ----------------------------------------------------------- code graph

def sardinas_patterson(words):
    """True when the code is uniquely decodable (Sardinas-Patterson): no dangling suffix is the empty word."""
    def quotient(a_set, b_set, proper):
        return {b[len(a):] for a in a_set for b in b_set if b.startswith(a) and (len(b) > len(a) or not proper)}

    code = set(words)
    current = quotient(code, code, proper=True)
    seen = set()
    while current:
        if "" in current:
            return False
        key = frozenset(current)
        if key in seen:
            return True
        seen.add(key)
        current = quotient(code, current, False) | quotient(current, code, False)
    return True


def parsings(text, words):
    """All cuttings of text into code words, by recursion."""
    if not text:
        return [[]]
    return [[w] + rest for w in words if text.startswith(w) for rest in parsings(text[len(w):], words)]


def ambiguity_found_by_brute_force(words, limit=10):
    for count in range(1, 5):
        for combo in itertools.product(words, repeat=count):
            text = "".join(combo)
            if len(text) <= limit and len(parsings(text, words)) > 1:
                return True
    return False


def decomposition_counts(text, words):
    """The set of numbers of code words that can make up text."""
    reach = {0: {0}}
    for end in range(1, len(text) + 1):
        reach[end] = {c + 1 for w in words if end >= len(w) and text[end - len(w):end] == w for c in reach.get(end - len(w), set())}
    return reach[len(text)]


def graph_by_definition(words):
    begin = {w[:k] for w in words for k in range(1, len(w))}
    end = {w[-k:] for w in words for k in range(1, len(w))}
    vertices = [""] + sorted(begin & end, key=lambda s: (len(s), s))
    arcs = []
    for i, bi in enumerate(vertices):
        for j, bj in enumerate(vertices):
            need = (i == 0) + (j == 0)
            for w in words:
                if len(w) >= len(bi) + len(bj) and w.startswith(bi) and w.endswith(bj):
                    mid = w[len(bi):len(w) - len(bj)]
                    if any(c >= need for c in decomposition_counts(mid, words)):
                        arcs.append([i, j])
                        break
    return vertices, arcs


def code_cases():
    codes = [["0", "01", "10"], ["01", "010", "101"], ["0", "01", "110"], ["0", "10", "11"], ["a", "ab", "b"], ["1", "10", "01", "00"]]
    while len(codes) < 400:
        alphabet = RNG.choice(["01", "01", "01", "abc"])
        pool = {"".join(RNG.choice(alphabet) for _ in range(RNG.randint(1, 5))) for _ in range(RNG.randint(1, 6))}
        if pool:
            codes.append(sorted(pool, key=lambda s: RNG.random()))
    out = []
    for words in codes:
        vertices, arcs = graph_by_definition(words)
        unique = sardinas_patterson(words)
        if ambiguity_found_by_brute_force(words):
            assert not unique, words    # guard on the reference itself
        samples = []
        for _ in range(4):
            text = "".join(RNG.choice(words) for _ in range(RNG.randint(1, 4)))
            samples.append({"text": text, "count": len(parsings(text, words))})
        out.append({"words": words, "vertices": vertices, "arcs": sorted(arcs), "unique": unique, "samples": samples})
    return out


# --------------------------------------------------------------- Huffman

def huffman_heap_weighted_length(values):
    """Sum of the glued weights: the cost times the total, by the textbook heap algorithm."""
    heap = list(values)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        total += a + b
        heapq.heappush(heap, a + b)
    return total


def optimal_weighted_length_by_search(values):
    """Least sum f_i l_i over all length vectors with Kraft's sum at most 1, by exhaustive search."""
    n = len(values)
    best = None
    for lengths in itertools.product(range(1, n), repeat=n):
        if sum(Fraction(1, 2 ** l) for l in lengths) <= 1:
            cost = sum(f * l for f, l in zip(values, lengths))
            best = cost if best is None else min(best, cost)
    return best


def huffman_cases():
    out = []
    for _ in range(200):
        n = RNG.randint(2, 6)
        ints = [RNG.randint(1, RNG.choice([3, 8, 30])) for _ in range(n)]
        decimals = RNG.random() < 0.4
        text = " ".join(f"{v / 10:.1f}" if decimals else str(v) for v in ints)
        scaled = ints
        weighted = optimal_weighted_length_by_search(scaled)
        assert weighted == huffman_heap_weighted_length(scaled), scaled   # guard: two references agree
        total = sum(scaled)
        entropy = -sum(v / total * math.log2(v / total) for v in scaled)
        out.append({"text": text, "values": scaled, "weighted": weighted, "total": total, "entropy": entropy})
    return out


# ----------------------------------------------------------- Hamming code

def hamming_code_by_definition(n):
    """All words of E_2^n whose sums over every D_i are even (the definition of the note), as strings."""
    k = math.floor(math.log2(n)) + 1
    sets = [[m for m in range(1, n + 1) if (m >> i) & 1] for i in range(k)]
    words = []
    for bits_ in itertools.product([0, 1], repeat=n):
        if all(sum(bits_[m - 1] for m in s) % 2 == 0 for s in sets):
            words.append("".join(map(str, bits_)))
    return k, sets, sorted(words)


def hamming_cases():
    out = []
    for n in range(1, 13):
        k, sets, words = hamming_code_by_definition(n)
        assert len(words) == 2 ** (n - k)
        out.append({"n": n, "k": k, "sets": sets, "code": words})
    return out


def hamming_error_cases():
    """Received words: one error (position known), two errors, none; the lecturer's algorithm by plain loops."""
    out = []
    for _ in range(300):
        n = RNG.randint(3, 12)
        k, sets, words = hamming_code_by_definition(n) if n <= 9 else (None, None, None)
        if words is None:
            continue
        sent = RNG.choice(words)
        flips = RNG.sample(range(1, n + 1), RNG.choice([0, 1, 1, 1, 2]))
        got = [int(c) for c in sent]
        for p in flips:
            got[p - 1] ^= 1
        delta = [sum(got[m - 1] for m in s) % 2 for s in sets]
        number = sum(d << i for i, d in enumerate(delta))
        fixed = list(got)
        if 1 <= number <= n:
            fixed[number - 1] ^= 1
        out.append({"n": n, "sent": sent, "flips": flips, "received": "".join(map(str, got)),
                    "delta": delta, "number": number, "fixed": "".join(map(str, fixed))})
    return out


# ------------------------------------------------------------- automata

def run_word(aut, q, word):
    out = []
    for a in word:
        out.append(aut["out"][q][a])
        q = aut["next"][q][a]
    return out


def moore_classes_by_definition(aut, m, alphabet):
    """R_m of the note: s and t together when no word of length m distinguishes them."""
    r = len(aut["next"])
    words = list(itertools.product(range(alphabet), repeat=m))
    together = [[all(run_word(aut, s, w) == run_word(aut, t, w) for w in words) for t in range(r)] for s in range(r)]
    # as the canonical numbering by smallest state
    cls = [None] * r
    for s in range(r):
        if cls[s] is None:
            cls[s] = max([c for c in cls if c is not None], default=-1) + 1
            for t in range(s + 1, r):
                if together[s][t]:
                    cls[t] = cls[s]
    return cls


def shortest_by_search(aut, s, t, alphabet, limit):
    for length in range(1, limit + 1):
        for w in itertools.product(range(alphabet), repeat=length):
            if run_word(aut, s, w) != run_word(aut, t, w):
                return length
    return None


def automaton_cases():
    out = []
    # The 3-state automaton of the note, 0-based (states 1, 2, 3 are 0, 1, 2; columns are the inputs 0, 1):
    # state 1: 0 -> (2, 0), 1 -> (1, 0); state 2: 0 -> (2, 1), 1 -> (1, 0); state 3: 0 -> (2, 0), 1 -> (3, 1)
    note = {"next": [[1, 0], [1, 0], [1, 2]], "out": [[0, 0], [1, 0], [0, 1]]}
    auts = [(note, 2)]
    for _ in range(220):
        r = RNG.randint(2, 6)
        a = RNG.choice([2, 2, 3])
        auts.append(({"next": [[RNG.randrange(r) for _ in range(a)] for _ in range(r)],
                      "out": [[RNG.randint(0, 1) for _ in range(a)] for _ in range(r)]}, a))
    # a chain with the longest shortest experiment r - 1 (the note's footnote)
    for r in range(2, 7):
        auts.append(({"next": [[min(q + 1, r - 1)] for q in range(r)], "out": [[1 if q == r - 1 else 0] for q in range(r)]}, 1))
    for aut, a in auts:
        r = len(aut["next"])
        chain = [moore_classes_by_definition(aut, m, a) for m in range(r + 1)]
        shortest = {}
        for s in range(r):
            for t in range(s + 1, r):
                length = shortest_by_search(aut, s, t, a, min(r + 2, 8))
                if length is not None:
                    assert length <= r - 1, (aut, s, t, length)   # the theorem, as a guard on the reference
                shortest[f"{s},{t}"] = length
        out.append({"aut": aut, "alphabet": a, "chain": chain, "shortest": shortest})
    return out


BAD_CNF = ["x1 | x2 & x3 | x1", "x1 & (x2 & x3 | x4)", "(x1 | !!x2)", "(x1 | x1)", "(x1 | !x1)", "x1 -> x2", "1 & x1", "x1 ^ x2"]


def main():
    data = {
        "functions": function_cases(),
        "formulas": formula_cases(),
        "precedence": precedence_cases(),
        "badFormulas": BAD_FORMULAS,
        "cnfs": cnf_cases(),
        "badCnfs": BAD_CNF,
        "msts": mst_cases(),
        "codes": code_cases(),
        "huffmans": huffman_cases(),
        "hammings": hamming_cases(),
        "hammingErrors": hamming_error_cases(),
        "automata": automaton_cases(),
    }
    (HERE / "fixtures.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print({k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
