// dmcore.js against the python reference in fixtures.json (export_fixtures.py).
// Run: node --test dmcore.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as dm from "./dmcore.js";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));
const sameSet = (a, b) => assert.deepEqual([...a].sort((p, q) => p - q), [...b].sort((p, q) => p - q));

test("bits and index are inverse, x1 is the most significant", () => {
  assert.deepEqual(dm.bits(5, 3), [1, 0, 1]);
  assert.deepEqual(dm.bits(1, 4), [0, 0, 0, 1]);
  for (let n = 1; n <= 4; n++) for (let i = 0; i < 1 << n; i++) assert.equal(dm.index(dm.bits(i, n)), i);
});

test("formula vectors match sympy on random formulas in every spelling", () => {
  for (const c of fx.formulas) assert.deepEqual(dm.formulaVector(c.text, c.n), c.vec, c.text);
});

test("operator precedence matches Python's own operators", () => {
  for (const c of fx.precedence) assert.deepEqual(dm.formulaVector(c.text, c.n), c.vec, c.text);
});

test("a malformed formula raises FormulaError with a position", () => {
  for (const text of fx.badFormulas) {
    assert.throws(() => dm.formulaVector(text, 4), (e) => e instanceof dm.FormulaError && Number.isInteger(e.pos), JSON.stringify(text));
  }
});

test("a variable beyond n is an error, within n it is fine", () => {
  assert.throws(() => dm.formulaVector("x1 & x3", 2), dm.FormulaError);
  assert.deepEqual(dm.formulaVector("x1 & x2", 3), [0, 0, 0, 0, 0, 0, 1, 1]);
});

test("Zhegalkin polynomial matches sympy ANFform", () => {
  for (const c of fx.functions) {
    const p = dm.zhegalkinVector(c.vec);
    sameSet(dm.polynomial(p, c.n).map((m) => m.index), c.monomials);
  }
});

test("the fast algorithm doubles the blocks and keeps the first half of each pair", () => {
  for (const c of fx.functions.slice(0, 300)) {
    const levels = dm.zhegalkinLevels(c.vec);
    assert.equal(levels.length, c.n + 1);
    levels.forEach((blocks, k) => {
      assert.equal(blocks.length, 1 << (c.n - k));
      assert.ok(blocks.every((b) => b.length === 1 << k));
    });
    levels.slice(1).forEach((blocks, k) => blocks.forEach((b, j) => {
      const prev = levels[k][2 * j];
      assert.deepEqual(b.slice(0, 1 << k), prev);
    }));
  }
});

test("the majority example of the note: 00 01 01 11 -> 00010110", () => {
  const levels = dm.zhegalkinLevels([0, 0, 0, 1, 0, 1, 1, 1]);
  assert.deepEqual(levels[1].flat(), [0, 0, 0, 1, 0, 1, 1, 0]);
  assert.deepEqual(levels[2].map((b) => b.join("")), ["0001", "0111"]);
  assert.deepEqual(levels[3][0], [0, 0, 0, 1, 0, 1, 1, 0]);
  assert.equal(dm.polynomialText(dm.polynomial(levels[3][0], 3)), "x₂x₃ ⊕ x₁x₃ ⊕ x₁x₂");
});

test("the polynomial equals the function at every tuple", () => {
  for (const c of fx.functions) {
    const p = dm.zhegalkinVector(c.vec);
    for (let i = 0; i < 1 << c.n; i++) assert.equal(dm.evalPolynomial(p, c.n, dm.bits(i, c.n)), c.vec[i]);
  }
});

test("SDNF and SKNF take the tuples with f = 1 and f = 0, and compute f", () => {
  for (const c of fx.functions) {
    const d = dm.sdnf(c.vec, c.n), k = dm.sknf(c.vec, c.n);
    sameSet(d.map((t) => t.index), c.minterms);
    sameSet(k.map((t) => t.index), c.maxterms);
    for (let i = 0; i < 1 << c.n; i++) {
      const b = dm.bits(i, c.n);
      const lit = (l) => (l.neg ? 1 - b[l.v - 1] : b[l.v - 1]);
      const dnf = d.some((t) => t.literals.every((l) => lit(l) === 1)) ? 1 : 0;
      const cnf = k.every((t) => t.literals.some((l) => lit(l) === 1)) ? 1 : 0;
      assert.equal(dnf, c.vec[i]);
      assert.equal(cnf, c.vec[i]);
    }
  }
});

test("literal and term text", () => {
  const t = dm.sdnf([0, 1, 0, 0], 2)[0];
  assert.equal(dm.termText(t, ""), "(¬x₁x₂)");
  assert.equal(dm.termText(dm.sknf([1, 0, 1, 1], 2)[0], " ∨ "), "(x₁ ∨ ¬x₂)");
});

test("class membership matches the definition by brute force", () => {
  for (const c of fx.functions) {
    const got = dm.classes(c.vec, c.n);
    for (const name of dm.CLASS_NAMES) assert.equal(got[name].inClass, c.classes[name], `${name} of ${c.vec}`);
  }
});

test("every witness really refutes membership", () => {
  const last = (c) => (1 << c.n) - 1;
  for (const c of fx.functions) {
    const got = dm.classes(c.vec, c.n);
    const v = c.vec, w = (name) => got[name].witness;
    if (!got.T0.inClass) { assert.equal(w("T0").alpha, 0); assert.equal(v[0], 1); }
    if (!got.T1.inClass) { assert.equal(w("T1").alpha, last(c)); assert.equal(v[last(c)], 0); }
    if (!got.S.inClass) {
      const { alpha, beta } = w("S");
      assert.equal(beta, last(c) - alpha);
      assert.equal(v[alpha], v[beta]);
    }
    if (!got.M.inClass) {
      const { alpha, beta } = w("M");
      assert.equal(alpha & beta, alpha);
      assert.equal(v[alpha], 1);
      assert.equal(v[beta], 0);
    }
    if (!got.L.inClass) {
      const { monomial, index } = w("L");
      assert.ok(monomial.length >= 2);
      assert.deepEqual(dm.monomial(index, c.n), monomial);
      assert.equal(dm.zhegalkinVector(v)[index], 1);
    }
    for (const name of dm.CLASS_NAMES) assert.equal("witness" in got[name], !got[name].inClass);
  }
});

test("the known functions: AND, OR, XOR, implication", () => {
  const cls = (text) => Object.fromEntries(Object.entries(dm.classes(dm.formulaVector(text, 2), 2)).map(([k, v]) => [k, v.inClass]));
  assert.deepEqual(cls("x1 & x2"), { T0: true, T1: true, L: false, S: false, M: true });
  assert.deepEqual(cls("x1 | x2"), { T0: true, T1: true, L: false, S: false, M: true });
  assert.deepEqual(cls("x1 ^ x2"), { T0: true, T1: false, L: true, S: false, M: false });
  assert.deepEqual(cls("x1 -> x2"), { T0: false, T1: true, L: false, S: false, M: false });
  assert.deepEqual(cls("!x1"), { T0: false, T1: false, L: true, S: true, M: false });
});

// ---------------------------------------------------------------- Nelson

const toLits = (pairs) => pairs.map(([v, neg]) => ({ v, neg }));
const termKey = (t) => t.map((l) => (l.neg ? "-" : "") + l.v).join(",");
const sameTerms = (a, b) => assert.deepEqual(a.map(termKey).sort(), b.map(termKey).sort());

test("parseCnf reads the clauses of the python reference", () => {
  for (const c of fx.cnfs) assert.deepEqual(dm.parseCnf(c.text), c.clauses.map(toLits), c.text);
});

test("a text that is not an elementary CNF is refused", () => {
  for (const text of fx.badCnfs) assert.throws(() => dm.parseCnf(text), dm.FormulaError, text);
});

test("Nelson's method gives exactly the prime implicants found by the definition", () => {
  for (const c of fx.cnfs) {
    const r = dm.nelson(dm.parseCnf(c.text));
    assert.equal(r.zero, !c.vec.some(Boolean), c.text);
    sameTerms(r.result, c.primes.map(toLits));
  }
});

test("every step keeps the function: D1 and D2 equal the product, D2 has no repeats or absorption", () => {
  for (const c of fx.cnfs) {
    const clauses = dm.parseCnf(c.text);
    const r = dm.nelson(clauses);
    r.steps.forEach((s, idx) => {
      const product = dm.cnfVector(clauses.slice(0, idx + 2), c.n);
      assert.deepEqual(dm.dnfVector(s.d1, c.n), product, `D1, ${c.text}`);
      assert.deepEqual(dm.dnfVector(s.d2, c.n), product, `D2, ${c.text}`);
      s.d2.forEach((t, i) => s.d2.forEach((u, j) => {
        if (i !== j) assert.ok(!dm.contains(t, u), `${termKey(t)} contains ${termKey(u)} in D2`);
      }));
    });
  }
});

test("the example of the note: (x v y)(!x v z)(y v !z) gives !x y v y z", () => {
  const r = dm.nelson(dm.parseCnf("(x1 | x2) & (!x1 | x3) & (x2 | !x3)"));
  assert.equal(dm.dnfText(r.steps[0].d2), "x₁x₃ ∨ ¬x₁x₂ ∨ x₂x₃");
  assert.equal(dm.dnfText(r.steps[1].d1), "x₁x₂x₃ ∨ ¬x₁x₂ ∨ ¬x₁x₂¬x₃ ∨ x₂x₃");
  assert.equal(dm.dnfText(r.result), "¬x₁x₂ ∨ x₂x₃");
  const fates = r.steps[1].stage2.map((s) => s.fate);
  assert.deepEqual(fates, [{ absorbedBy: 3 }, "keep", { absorbedBy: 1 }, "keep"]);
});

test("stage 1 drops a repeat, a literal against its negation gives zero", () => {
  const a = toLits([[1, false], [2, false]]), b = toLits([[2, false], [3, true]]), c = toLits([[2, true]]);
  assert.equal(dm.conjunctionText(dm.multiplyTerms(a, b).term), "x₁x₂¬x₃");
  const z = dm.multiplyTerms(a, c);
  assert.equal(z.zero, true);
  assert.equal(z.clash, 2);
});

test("stage 2: a duplicate keeps the first, an absorbed term names its absorber", () => {
  const t = (...ls) => toLits(ls);
  const r = dm.absorb([t([1, false], [2, false]), t([1, false]), t([1, false]), t([3, true])]);
  assert.deepEqual(r.map((x) => x.fate), [{ absorbedBy: 1 }, "keep", { dup: 1 }, "keep"]);
});

// ------------------------------------------------ spanning trees

const treeKey = (idx, edges) => idx.map((i) => edges[i].join("-")).sort().join(" ");
const refKey = (tree) => tree.map((e) => e.join("-")).sort().join(" ");

test("complete graph edges are all pairs in lexicographic order", () => {
  assert.deepEqual(dm.completeEdges(4), [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]);
});

test("the algorithm builds a tree of the networkx minimum weight, and that tree is one of the minimum trees", () => {
  for (const c of fx.msts) {
    const edges = dm.completeEdges(c.n);
    const r = dm.kruskal(c.n, c.weights);
    assert.equal(r.chosen.length, c.n - 1);
    assert.equal(r.weight, c.min);
    assert.ok(c.minTrees.map(refKey).includes(treeKey(r.chosen, edges)), "result is not a minimum tree");
  }
});

test("every step takes a lightest edge that closes no cycle, and says which edges would close one", () => {
  for (const c of fx.msts) {
    const edges = dm.completeEdges(c.n);
    const r = dm.kruskal(c.n, c.weights);
    r.steps.forEach((s, idx) => {
      const before = r.chosen.slice(0, idx).map((i) => edges[i]);
      // Reachability by BFS over the chosen edges, independent of the union-find inside dmcore.js.
      const acyclic = (i) => {
        // adding edge i closes a cycle exactly when its ends are already joined by the chosen edges
        const adj = new Map(Array.from({ length: c.n }, (_, k) => [k + 1, []]));
        for (const [a, b] of before) { adj.get(a).push(b); adj.get(b).push(a); }
        const seen = new Set([edges[i][0]]), queue = [edges[i][0]];
        while (queue.length) for (const u of adj.get(queue.shift())) if (!seen.has(u)) { seen.add(u); queue.push(u); }
        return !seen.has(edges[i][1]);
      };
      const free = edges.map((_, i) => i).filter((i) => !r.chosen.slice(0, idx).includes(i));
      const admissible = free.filter(acyclic);
      const lightest = Math.min(...admissible.map((i) => c.weights[i]));
      assert.deepEqual(s.candidates, admissible.filter((i) => c.weights[i] === lightest));
      assert.ok(s.candidates.includes(s.chosen));
      assert.equal(s.weight, lightest);
      assert.deepEqual(s.closing, free.filter((i) => !acyclic(i)));
    });
  }
});

test("a pick among equally light edges is honoured, an impossible pick falls back to the first", () => {
  const note = fx.msts[0];
  const first = dm.kruskal(note.n, note.weights);
  const step2 = first.steps[1];
  assert.ok(step2.candidates.length > 1);
  const other = step2.candidates[step2.candidates.length - 1];
  assert.equal(dm.kruskal(note.n, note.weights, [undefined, other]).steps[1].chosen, other);
  assert.equal(dm.kruskal(note.n, note.weights, [undefined, 0]).steps[1].chosen, step2.candidates[0]);
  assert.equal(dm.kruskal(note.n, note.weights, [undefined, other]).weight, note.min);
});

test("the K5 of the note: 4 shortest trees of weight 8, the steps of the note's table", () => {
  const note = fx.msts[0];
  const edges = dm.completeEdges(5);
  const at = (a, b) => edges.findIndex((e) => e[0] === a && e[1] === b);
  const r = dm.kruskal(5, note.weights, [at(1, 2), at(2, 3), at(3, 4), at(4, 5)]);
  assert.deepEqual(r.chosen.map((i) => edges[i].join("")), ["12", "23", "34", "45"]);
  assert.deepEqual(r.steps.map((s) => s.candidates.length), [1, 3, 1, 2]);
  assert.deepEqual(r.steps.map((s) => s.weight), [1, 2, 2, 3]);
  assert.equal(dm.spanningTrees(5, note.weights).best.length, 4);
});

test("brute force over spanning trees matches networkx: the minimum, the minimum trees, n^(n-2) trees", () => {
  for (const c of fx.msts) {
    const edges = dm.completeEdges(c.n);
    const t = dm.spanningTrees(c.n, c.weights);
    assert.equal(t.total, c.total);
    assert.equal(t.min, c.min);
    assert.deepEqual(t.best.map((x) => treeKey(x, edges)).sort(), c.minTrees.map(refKey).sort());
  }
});

// ------------------------------------------------------- code graph

const pairsOf = (g) => g.arcs.map((a) => [a.from, a.to]).sort((p, q) => p[0] - q[0] || p[1] - q[1]);

test("parseCode splits on spaces and commas and refuses repeats, empties and long input", () => {
  assert.deepEqual(dm.parseCode(" 0, 01;10  "), ["0", "01", "10"]);
  for (const bad of ["", "  ,", "0 0", "123456789", "0 1 2 3 4 5 6 7 8"]) assert.throws(() => dm.parseCode(bad), dm.FormulaError, bad);
});

test("vertices and arcs match the definition by brute force", () => {
  for (const c of fx.codes) {
    const g = dm.codeGraph(c.words);
    assert.deepEqual(g.vertices, c.vertices, c.words.join(" "));
    assert.deepEqual(pairsOf(g), c.arcs, c.words.join(" "));
  }
});

test("each arc witness is a real equality B = beta_i D beta_j with the right number of code words", () => {
  for (const c of fx.codes) {
    const g = dm.codeGraph(c.words);
    for (const a of g.arcs) {
      const bi = g.vertices[a.from], bj = g.vertices[a.to];
      assert.equal(bi + a.D.map((l) => c.words[l]).join("") + bj, c.words[a.word]);
      assert.equal(a.mid, a.D.map((l) => c.words[l]).join(""));
      const need = (a.from === 0 ? 1 : 0) + (a.to === 0 ? 1 : 0);
      assert.ok(a.D.length >= need);
    }
  }
});

test("a cycle through the empty word exists exactly when Sardinas-Patterson says not uniquely decodable", () => {
  for (const c of fx.codes) {
    const g = dm.codeGraph(c.words);
    assert.equal(dm.cycleThroughEmpty(g) === null, c.unique, c.words.join(" "));
  }
});

test("the cycle is a real shortest directed cycle through the empty word", () => {
  for (const c of fx.codes) {
    const g = dm.codeGraph(c.words);
    const cyc = dm.cycleThroughEmpty(g);
    if (!cyc) continue;
    assert.equal(cyc[0], 0);
    assert.equal(new Set(cyc).size, cyc.length);
    const has = (i, j) => g.arcs.some((a) => a.from === i && a.to === j);
    cyc.forEach((v, i) => assert.ok(has(v, cyc[(i + 1) % cyc.length])));
    // No shorter cycle: BFS depth by plain relaxation.
    const dist = new Map([[0, 0]]);
    for (let round = 0; round < g.vertices.length; round++) for (const a of g.arcs) {
      if (a.to !== 0 && dist.has(a.from) && (!dist.has(a.to) || dist.get(a.to) > dist.get(a.from) + 1)) dist.set(a.to, dist.get(a.from) + 1);
    }
    const best = Math.min(...g.arcs.filter((a) => a.to === 0 && dist.has(a.from)).map((a) => dist.get(a.from) + 1));
    assert.equal(cyc.length, best);
  }
});

test("the word built from the cycle has two different parsings of the same text", () => {
  for (const c of fx.codes.filter((x) => !x.unique)) {
    const g = dm.codeGraph(c.words);
    const r = dm.ambiguousWord(c.words, g, dm.cycleThroughEmpty(g));
    const text = (p) => p.map((l) => c.words[l]).join("");
    assert.equal(text(r.one), r.word);
    assert.equal(text(r.two), r.word);
    assert.notDeepEqual(r.one, r.two);
    assert.ok(dm.countParsings(r.word, c.words) >= 2);
  }
});

test("countParsings matches the recursive count of the reference", () => {
  for (const c of fx.codes) for (const s of c.samples) assert.equal(dm.countParsings(s.text, c.words), s.count, s.text);
});

test("the code of the lecture: a->0, b->01, c->10 gives the cycle Lambda, 1 and the word 010", () => {
  const words = ["0", "01", "10"];
  const g = dm.codeGraph(words);
  assert.deepEqual(g.vertices, ["", "0", "1"]);
  const cyc = dm.cycleThroughEmpty(g);
  assert.deepEqual(cyc, [0, 2]);
  const r = dm.ambiguousWord(words, g, cyc);
  assert.equal(r.word, "010");
  assert.deepEqual([dm.lettersOf(r.one), dm.lettersOf(r.two)].sort(), ["ac", "ba"]);
});

test("a code word cut into two code words is a loop in the empty word", () => {
  const words = ["0", "1", "01"];
  const g = dm.codeGraph(words);
  assert.deepEqual(dm.cycleThroughEmpty(g), [0]);
  const r = dm.ambiguousWord(words, g, [0]);
  assert.equal(r.word, "01");
  assert.deepEqual([r.one, r.two].map(dm.lettersOf).sort(), ["ab", "c"]);
});

// ------------------------------------------------------------- Huffman

test("parseFrequencies reads integers, decimals and name:value pairs exactly", () => {
  for (const c of fx.huffmans) assert.deepEqual(dm.parseFrequencies(c.text).values, c.values, c.text);
  const p = dm.parseFrequencies("0.30 0.25 0.20 0.10 0.10 0.05");
  assert.deepEqual(p.values, [30, 25, 20, 10, 10, 5]);
  assert.equal(p.total, 100);
  assert.deepEqual(p.names, ["a", "b", "c", "d", "e", "f"]);
  assert.deepEqual(dm.parseFrequencies("x:2, y:0.5").values, [20, 5]);
  assert.deepEqual(dm.parseFrequencies("x:2, y:0.5").names, ["x", "y"]);
  assert.deepEqual(dm.parseFrequencies("0.25 0.5 1").values, [25, 50, 100]);
  assert.deepEqual(dm.parseFrequencies("0.5 0.25 1.125").values, [500, 250, 1125]);
});

test("bad frequency lists are refused", () => {
  for (const bad of ["", "1", "1 a", "1 -2", "1 0", "1 2 3 4 5 6 7 8 9 10 11", "x:1 x:2", "1 0.1234567"]) {
    assert.throws(() => dm.parseFrequencies(bad), dm.FormulaError, bad);
  }
});

test("Huffman's code is a prefix code whose cost is the exhaustive optimum and the heap algorithm's", () => {
  for (const c of fx.huffmans) {
    const h = dm.huffman(c.values);
    const lens = h.codes.map((s) => s.length);
    assert.ok(lens.every((l) => l >= 1));
    h.codes.forEach((a, i) => h.codes.forEach((b, j) => { if (i !== j) assert.ok(!b.startsWith(a), `${a} is a prefix of ${b}`); }));
    const weighted = h.codes.reduce((s, code, i) => s + c.values[i] * code.length, 0);
    assert.equal(weighted, c.weighted, c.text);
    assert.ok(Math.abs(h.cost - c.weighted / c.total) < 1e-12);
  }
});

test("the cost is 1 plus the glued frequencies and lies between the entropy and the entropy plus 1", () => {
  for (const c of fx.huffmans) {
    const h = dm.huffman(c.values);
    assert.ok(Math.abs(h.cost - (1 + h.glued)) < 1e-12, c.text);
    assert.ok(Math.abs(dm.entropy(c.values) - c.entropy) < 1e-12);
    assert.ok(h.cost >= c.entropy - 1e-12 && h.cost < c.entropy + 1 + 1e-12);
  }
});

test("the brute-force optimum of dmcore matches the python search", () => {
  for (const c of fx.huffmans) assert.equal(dm.optimalWeightedLength(c.values), c.weighted, c.text);
});

test("the example of the note: six symbols, steps, codes and cost 2.4", () => {
  const h = dm.huffman([30, 25, 20, 10, 10, 5]);
  assert.deepEqual(h.codes, ["00", "01", "11", "101", "1000", "1001"]);
  assert.deepEqual(h.steps.map((s) => [h.weight[s.left], h.weight[s.right]]), [[10, 5], [15, 10], [25, 20], [30, 25], [55, 45]]);
  assert.deepEqual(h.steps.map((s) => s.after.map((v) => h.weight[v])), [[30, 25, 20, 15, 10], [30, 25, 25, 20], [45, 30, 25], [55, 45], [100]]);
  assert.ok(Math.abs(h.cost - 2.4) < 1e-12);
  assert.ok(Math.abs(h.glued - (0.15 + 0.25 + 0.45 + 0.55)) < 1e-12);
  assert.ok(Math.abs(dm.entropy([30, 25, 20, 10, 10, 5]) - 2.366) < 5e-4);
});

test("two equal frequencies give the code 0 and 1", () => {
  const h = dm.huffman([1, 1]);
  assert.deepEqual(h.codes, ["0", "1"]);
  assert.equal(h.cost, 1);
});

// --------------------------------------------------------------- Hamming

const wordText = (w) => w.join("");
const allData = (bitsCount) => Array.from({ length: 1 << bitsCount }, (_, v) => Array.from({ length: bitsCount }, (_, q) => (v >> (bitsCount - 1 - q)) & 1));

test("k and the sets D_i match the definition", () => {
  for (const c of fx.hammings) {
    assert.equal(dm.hammingK(c.n), c.k);
    assert.deepEqual(dm.hammingSets(c.n), c.sets);
  }
});

test("the encodings of all information words are exactly the code of the definition", () => {
  for (const c of fx.hammings) {
    const free = dm.hammingFreePositions(c.n);
    assert.equal(free.length, c.n - c.k);
    const words = allData(free.length).map((d) => wordText(dm.hammingEncode(c.n, d))).sort();
    assert.deepEqual(words, c.code, `n = ${c.n}`);
  }
});

test("information bits sit on the free positions and check bits on the powers of two", () => {
  const w = dm.hammingEncode(7, [1, 0, 1, 1]);
  assert.equal(wordText(w), "0110011");
  assert.deepEqual(dm.hammingFreePositions(7), [3, 5, 6, 7]);
});

test("the syndrome of a single error is the number of the position, for every word and every position", () => {
  for (const c of fx.hammings) {
    for (const s of c.code) {
      const word = [...s].map(Number);
      assert.equal(dm.hammingSyndrome(c.n, word).number, 0);
      for (let p = 1; p <= c.n; p++) {
        const got = [...word]; got[p - 1] ^= 1;
        assert.equal(dm.hammingSyndrome(c.n, got).number, p);
        assert.deepEqual(dm.hammingCorrect(c.n, got).word, word);
      }
    }
  }
});

test("syndrome, number and correction match the python reference on received words with 0, 1 or 2 errors", () => {
  for (const e of fx.hammingErrors) {
    const got = [...e.received].map(Number);
    const r = dm.hammingCorrect(e.n, got);
    assert.deepEqual(r.delta, e.delta);
    assert.equal(r.number, e.number);
    assert.equal(wordText(r.word), e.fixed);
    assert.equal(r.outside, e.number > e.n);
  }
});

test("two errors are not corrected: the result differs from what was sent", () => {
  const two = fx.hammingErrors.filter((e) => e.flips.length === 2);
  assert.ok(two.length > 10);
  for (const e of two) assert.notEqual(e.fixed, e.sent);
});

test("the example of the note: 0110011, error at 5, syndrome 101", () => {
  const r = dm.hammingCorrect(7, [...("0110111")].map(Number));
  assert.deepEqual(r.delta, [1, 0, 1]);
  assert.equal(r.number, 5);
  assert.equal(wordText(r.word), "0110011");
});

// -------------------------------------------------------------- automata

const wordsOfLength = (alphabet, m) => (m === 0 ? [[]] : wordsOfLength(alphabet, m - 1).flatMap((w) => Array.from({ length: alphabet }, (_, a) => [...w, a])));

test("the refinement of classes matches R_m by the definition and ends where the chain stops", () => {
  for (const c of fx.automata) {
    const steps = dm.mooreSteps(c.aut);
    const last = steps.length - 1;
    steps.forEach((s, m) => assert.deepEqual(s.cls, c.chain[m], `R_${m}`));
    assert.deepEqual(c.chain[last + 1], c.chain[last], "the chain is stable after the last step");
    if (last > 0) assert.notDeepEqual(c.chain[last - 1], c.chain[last]);
  }
});

test("every step splits some class strictly, and the number of classes never passes r (the proof of Moore's theorem)", () => {
  for (const c of fx.automata) {
    const steps = dm.mooreSteps(c.aut);
    const r = c.aut.next.length;
    const counts = steps.map((s) => s.classes.length);
    assert.equal(counts[0], 1);
    counts.slice(1).forEach((k, i) => assert.ok(k > counts[i]));
    assert.ok(counts[counts.length - 1] <= r);
    assert.ok(steps.length <= r, `p + 1 <= r: ${steps.length} steps, ${r} states`);
  }
});

test("distinguish finds a shortest experiment, no longer than r - 1, and null exactly for indistinguishable states", () => {
  for (const c of fx.automata) {
    const r = c.aut.next.length;
    for (let s = 0; s < r; s++) for (let t = s + 1; t < r; t++) {
      const w = dm.distinguish(c.aut, s, t);
      const want = c.shortest[`${s},${t}`];
      if (want === null) { assert.equal(w, null); continue; }
      assert.equal(w.length, want, `${s},${t}`);
      assert.ok(w.length <= r - 1);
      assert.notDeepEqual(dm.runAutomaton(c.aut, s, w).outputs, dm.runAutomaton(c.aut, t, w).outputs);
    }
  }
});

test("a state pair stays together in R_m exactly when no word of length m distinguishes it", () => {
  for (const c of fx.automata.slice(0, 60)) {
    const steps = dm.mooreSteps(c.aut);
    const r = c.aut.next.length;
    for (let m = 0; m < steps.length; m++) {
      const words = wordsOfLength(c.alphabet, m);
      for (let s = 0; s < r; s++) for (let t = s + 1; t < r; t++) {
        const same = words.every((w) => dm.runAutomaton(c.aut, s, w).outputs.join() === dm.runAutomaton(c.aut, t, w).outputs.join());
        assert.equal(steps[m].cls[s] === steps[m].cls[t], same);
      }
    }
  }
});

test("the automaton of the note: pairwise distinguishable, no word separates all three", () => {
  const aut = { next: [[1, 0], [1, 0], [1, 2]], out: [[0, 0], [1, 0], [0, 1]] };
  assert.deepEqual(dm.distinguish(aut, 0, 1), [0]);
  assert.deepEqual(dm.distinguish(aut, 0, 2), [1]);
  assert.deepEqual(dm.distinguish(aut, 1, 2), [0]);
  const steps = dm.mooreSteps(aut);
  assert.deepEqual(steps.map((s) => s.classes), [[[0, 1, 2]], [[0], [1], [2]]]);
  for (let m = 1; m <= 6; m++) for (const w of wordsOfLength(2, m)) {
    const outs = [0, 1, 2].map((q) => dm.runAutomaton(aut, q, w).outputs.join(""));
    assert.ok(new Set(outs).size < 3, w.join(""));
    assert.equal(outs[0] === outs[2], w[0] === 0);
    assert.equal(outs[0] === outs[1], w[0] === 1);
  }
});

test("the longest shortest experiment is r - 1: the chain automaton of the note", () => {
  for (const r of [2, 3, 4, 5, 6]) {
    const aut = { next: Array.from({ length: r }, (_, q) => [Math.min(q + 1, r - 1)]), out: Array.from({ length: r }, (_, q) => [q === r - 1 ? 1 : 0]) };
    assert.equal(dm.distinguish(aut, 0, 1).length, r - 1);
    assert.equal(dm.mooreSteps(aut).length, r);
  }
});

test("runAutomaton returns the states before each step, after the last, and the outputs", () => {
  const aut = { next: [[1, 0], [1, 0], [1, 2]], out: [[0, 0], [1, 0], [0, 1]] };
  assert.deepEqual(dm.runAutomaton(aut, 0, [0, 0, 1]), { states: [0, 1, 1, 0], outputs: [0, 1, 0] });
  assert.deepEqual(dm.runAutomaton(aut, 2, []), { states: [2], outputs: [] });
});

test("a contradictory CNF has no reduced DNF", () => {
  const r = dm.nelson(dm.parseCnf("x1 & !x1"));
  assert.equal(r.zero, true);
  assert.deepEqual(r.result, []);
});
