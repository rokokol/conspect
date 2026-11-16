// Logic of the discrete math course pages: pure functions, no DOM.
// One ES module for every page; the build inlines it with `export` removed,
// and `node --test` imports it as is (dmcore.test.mjs).
//
// Conventions of the course notes: a function of n variables is a vector of
// 2^n values over the tuples in the order 0...0, 0...01, ..., 1...1, so x1 is
// the most significant bit of the tuple number and stands leftmost.

// ---------------------------------------------------------------- tuples

// The n bits of the tuple number i, x1 first.
export function bits(i, n) {
  return Array.from({ length: n }, (_, k) => (i >> (n - 1 - k)) & 1);
}

// The tuple number of a bit array, the inverse of bits.
export function index(b) {
  return b.reduce((acc, x) => acc * 2 + x, 0);
}

// The vector of the function fn(bitsArray) -> 0 or 1 over n variables.
export function vectorOf(n, fn) {
  return Array.from({ length: 1 << n }, (_, i) => (fn(bits(i, n)) ? 1 : 0));
}

// ----------------------------------------------------------------- formulas

const SUBSCRIPTS = { "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6" };
const SUBDIGITS = "₀₁₂₃₄₅₆₇₈₉";

// A number in subscript digits: 12 -> ₁₂.
export function sub(k) {
  return String(k).split("").map((c) => SUBDIGITS[+c]).join("");
}
const ALIASES = { x: 1, y: 2, z: 3, w: 4 };

// Operator spellings, longest first so that "<->" is not read as "<" and "->".
const OPS = [
  ["<->", "eqv"], ["≡", "eqv"], ["↔", "eqv"], ["==", "eqv"],
  ["->", "imp"], ["→", "imp"], ["⇒", "imp"],
  ["&", "and"], ["∧", "and"], ["*", "and"], ["·", "and"],
  ["|", "or"], ["∨", "or"],
  ["^", "xor"], ["⊕", "xor"],
  ["!", "not"], ["¬", "not"], ["~", "not"],
  ["(", "("], [")", ")"],
];

export class FormulaError extends Error {
  constructor(message, pos) {
    super(message);
    this.pos = pos;
  }
}

function tokenize(src) {
  const s = [...src].map((c) => SUBSCRIPTS[c] ?? c).join("");
  const out = [];
  let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (/\s/.test(c)) { i++; continue; }
    const op = OPS.find(([text]) => s.startsWith(text, i));
    if (op) { out.push({ type: op[1], pos: i }); i += op[0].length; continue; }
    if (c === "0" || c === "1") { out.push({ type: "const", value: +c, pos: i }); i++; continue; }
    const m = /^(x[1-6]|[xyzw])(?![a-z0-9])/.exec(s.slice(i));
    if (m) {
      const v = m[1].length === 2 ? +m[1][1] : ALIASES[m[1]];
      out.push({ type: "var", value: v, pos: i });
      i += m[1].length;
      continue;
    }
    if (c === "+") throw new FormulaError("знак + не читается: сумма по модулю 2 пишется ^ или ⊕, дизъюнкция — | или ∨", i);
    throw new FormulaError(`неизвестный знак "${c}"`, i);
  }
  return out;
}

// Precedence, tightest first: ! , & , ^ , | , -> (right-associative) , <->.
// Returns the syntax tree: {t: "const"|"var"|"not"|"and"|"or"|"xor"|"imp"|"eqv", ...}.
export function parseFormula(src) {
  const toks = tokenize(src);
  let p = 0;
  const peek = () => toks[p];
  const take = () => toks[p++];
  const fail = (msg) => { throw new FormulaError(msg, peek() ? peek().pos : src.length); };

  function binary(next, type) {
    return () => {
      let left = next();
      while (peek() && peek().type === type) { take(); left = { t: type, a: left, b: next() }; }
      return left;
    };
  }
  function atom() {
    const t = peek();
    if (!t) fail("формула обрывается: ждали переменную, константу или скобку");
    if (t.type === "const") { take(); return { t: "const", value: t.value }; }
    if (t.type === "var") { take(); return { t: "var", value: t.value }; }
    if (t.type === "(") {
      take();
      const e = eqv();
      if (!peek() || peek().type !== ")") fail("не закрыта скобка");
      take();
      return e;
    }
    return fail("здесь ждали переменную, константу, ! или скобку");
  }
  function neg() {
    if (peek() && peek().type === "not") { take(); return { t: "not", a: neg() }; }
    return atom();
  }
  const and = binary(neg, "and");
  const xor = binary(and, "xor");
  const or = binary(xor, "or");
  function imp() {
    const left = or();
    if (peek() && peek().type === "imp") { take(); return { t: "imp", a: left, b: imp() }; }
    return left;
  }
  const eqv = binary(imp, "eqv");

  const tree = eqv();
  if (p < toks.length) fail("лишний знак после конца формулы");
  return tree;
}

// The largest variable index in the tree, 0 for a formula of constants.
export function maxVar(ast) {
  if (ast.t === "var") return ast.value;
  if (ast.t === "const") return 0;
  if (ast.t === "not") return maxVar(ast.a);
  return Math.max(maxVar(ast.a), maxVar(ast.b));
}

export function evalAst(ast, b) {
  switch (ast.t) {
    case "const": return ast.value;
    case "var": return b[ast.value - 1];
    case "not": return 1 - evalAst(ast.a, b);
    case "and": return evalAst(ast.a, b) & evalAst(ast.b, b);
    case "or": return evalAst(ast.a, b) | evalAst(ast.b, b);
    case "xor": return evalAst(ast.a, b) ^ evalAst(ast.b, b);
    case "imp": return (1 - evalAst(ast.a, b)) | evalAst(ast.b, b);
    case "eqv": return 1 - (evalAst(ast.a, b) ^ evalAst(ast.b, b));
    default: throw new Error(`unknown node ${ast.t}`);
  }
}

// The vector of a formula over n variables; a variable beyond n is an error.
export function formulaVector(src, n) {
  const ast = parseFormula(src);
  if (maxVar(ast) > n) throw new FormulaError(`в формуле есть x${maxVar(ast)}, а переменных выбрано ${n}`, 0);
  return vectorOf(n, (b) => evalAst(ast, b));
}

// ------------------------------------------------------- SDNF and SKNF

// SDNF: one conjunction per tuple where f = 1, x for a 1 and the negation for a 0.
// Literals are {v: variable number, neg: boolean}. A function equal to 0 has none.
export function sdnf(vec, n) {
  return vec.flatMap((val, i) => (val === 1
    ? [{ index: i, literals: bits(i, n).map((x, k) => ({ v: k + 1, neg: x === 0 })) }]
    : []));
}

// SKNF: one disjunction per tuple where f = 0, with the opposite signs: a 0 gives x, a 1 its negation.
export function sknf(vec, n) {
  return vec.flatMap((val, i) => (val === 0
    ? [{ index: i, literals: bits(i, n).map((x, k) => ({ v: k + 1, neg: x === 1 })) }]
    : []));
}

export function literalText(l) {
  return (l.neg ? "¬" : "") + "x" + SUBDIGITS[l.v];
}

export function termText(term, glue) {
  return "(" + term.literals.map(literalText).join(glue) + ")";
}

// ------------------------------------------------ Zhegalkin polynomial

// The levels of the fast algorithm of the note: level 0 is the function
// vector cut into blocks of 1; each next level replaces a pair of blocks
// (c, d) by one block (c, c xor d). The last level is one block, the vector
// of the polynomial. Each level is an array of blocks (arrays of 0 and 1).
export function zhegalkinLevels(vec) {
  let blocks = vec.map((x) => [x]);
  const levels = [blocks];
  while (blocks.length > 1) {
    const next = [];
    for (let k = 0; k < blocks.length; k += 2) {
      const c = blocks[k], d = blocks[k + 1];
      next.push([...c, ...c.map((x, j) => x ^ d[j])]);
    }
    blocks = next;
    levels.push(blocks);
  }
  return levels;
}

export function zhegalkinVector(vec) {
  const levels = zhegalkinLevels(vec);
  return levels[levels.length - 1][0];
}

// The variables of the monotone conjunction K_i over n variables: the
// positions of ones in the binary notation of i, counted from the left.
export function monomial(i, n) {
  return bits(i, n).flatMap((x, k) => (x ? [k + 1] : []));
}

// The monomials of the polynomial with the coefficient vector pvec, by number.
export function polynomial(pvec, n) {
  return pvec.flatMap((c, i) => (c ? [{ index: i, vars: monomial(i, n) }] : []));
}

export function monomialText(vars) {
  return vars.length ? vars.map((v) => "x" + SUBDIGITS[v]).join("") : "1";
}

export function polynomialText(monos) {
  return monos.length ? monos.map((m) => monomialText(m.vars)).join(" ⊕ ") : "0";
}

// The value of the polynomial at a tuple: xor of the monomials that are all ones there.
export function evalPolynomial(pvec, n, b) {
  return polynomial(pvec, n).reduce((acc, m) => acc ^ (m.vars.every((v) => b[v - 1] === 1) ? 1 : 0), 0);
}

export function degree(monos) {
  return monos.reduce((d, m) => Math.max(d, m.vars.length), 0);
}

// -------------------------------------------------- closed classes

// Membership in T0, T1, L, S, M. For a class that does not contain f the
// result carries the witness, found by the definition of the class:
//   T0: f(0,...,0) = 1                       -> {alpha}
//   T1: f(1,...,1) = 0                       -> {alpha}
//   S:  a tuple with f(alpha) = f(not alpha) -> {alpha, beta}, beta = not alpha
//   M:  alpha <= beta with f(alpha)=1, f(beta)=0 -> {alpha, beta}
//   L:  a monomial of degree >= 2 in the polynomial -> {monomial: vars}
// A tuple is the tuple number; alpha <= beta means every bit of alpha is at most the bit of beta.
export function classes(vec, n) {
  const last = vec.length - 1;
  const out = {};
  out.T0 = vec[0] === 0 ? { inClass: true } : { inClass: false, witness: { alpha: 0 } };
  out.T1 = vec[last] === 1 ? { inClass: true } : { inClass: false, witness: { alpha: last } };

  const sAlpha = vec.findIndex((v, i) => v === vec[last - i]);
  out.S = sAlpha < 0 ? { inClass: true } : { inClass: false, witness: { alpha: sAlpha, beta: last - sAlpha } };

  let m = null;
  for (let a = 0; a <= last && !m; a++) {
    for (let b = 0; b <= last; b++) {
      if ((a & b) === a && vec[a] === 1 && vec[b] === 0) { m = { alpha: a, beta: b }; break; }
    }
  }
  out.M = m ? { inClass: false, witness: m } : { inClass: true };

  const nonlinear = polynomial(zhegalkinVector(vec), n).find((mono) => mono.vars.length >= 2);
  out.L = nonlinear ? { inClass: false, witness: { monomial: nonlinear.vars, index: nonlinear.index } } : { inClass: true };
  return out;
}

export const CLASS_NAMES = ["T0", "T1", "L", "S", "M"];

// ------------------------------------------------- Nelson's method

// A term (elementary conjunction) is an array of literals {v, neg} sorted by v,
// one literal per variable.

// A CNF as a list of clauses, each an array of literals. The text goes through
// parseFormula, so the spellings are the same; the shape is checked after:
// an AND of ORs of literals, a variable at most once in a clause.
export function parseCnf(src) {
  const ast = parseFormula(src);
  const fail = (msg) => { throw new FormulaError(msg, 0); };
  const flat = (node, type) => (node.t === type ? [...flat(node.a, type), ...flat(node.b, type)] : [node]);
  const lit = (node) => {
    if (node.t === "var") return { v: node.value, neg: false };
    if (node.t === "not" && node.a.t === "var") return { v: node.a.value, neg: true };
    return fail("это не КНФ: внутри скобки допустимы только переменные и их отрицания, соединённые |");
  };
  const clauses = flat(ast, "and").map((c) => {
    const lits = flat(c, "or").map(lit);
    const seen = new Set();
    for (const l of lits) {
      if (seen.has(l.v)) fail(`в скобке переменная x${l.v} встречается дважды: нужна элементарная дизъюнкция`);
      seen.add(l.v);
    }
    return lits.sort((p, q) => p.v - q.v);
  });
  return clauses;
}

// The product of two terms, as the method does it: the literals written one
// after the other (raw), then stage 1: tt = t drops a repeat, t and not-t give 0.
export function multiplyTerms(a, b) {
  const raw = [...a, ...b];
  const seen = new Map();
  for (const l of raw) {
    const old = seen.get(l.v);
    if (old === undefined) seen.set(l.v, l);
    else if (old.neg !== l.neg) return { raw, zero: true, clash: l.v };
  }
  return { raw, zero: false, term: [...seen.values()].sort((p, q) => p.v - q.v) };
}

// big contains small: every literal of small is a literal of big.
export function contains(big, small) {
  return small.every((s) => big.some((l) => l.v === s.v && l.neg === s.neg));
}

// Stage 2 on a list of terms: a term strictly containing another is absorbed
// (K or KL = K), of equal terms the first stays (K or K = K). Returns for each
// term {term, fate}: "keep", {dup: index of the first equal} or {absorbedBy: index}.
export function absorb(terms) {
  const strict = (k) => terms.flatMap((t, j) => (t.length < terms[k].length && contains(terms[k], t) ? [j] : []));
  return terms.map((term, k) => {
    const by = strict(k);
    if (by.length) {
      const best = by.reduce((p, q) => (terms[q].length < terms[p].length ? q : p));
      return { term, fate: { absorbedBy: best } };
    }
    const first = terms.findIndex((t) => t.length === term.length && contains(term, t));
    return { term, fate: first < k ? { dup: first } : "keep" };
  });
}

// One step of the method: the product of two reduced DNFs F and G (arrays of
// terms). products: every pair in order with its stage 1 result; d1: the nonzero
// results; stage2: absorb(d1); d2: the survivors, the reduced DNF of the product.
export function nelsonStep(F, G) {
  const products = [];
  F.forEach((a, i) => G.forEach((b, j) => products.push({ i, j, a, b, ...multiplyTerms(a, b) })));
  const d1 = products.filter((p) => !p.zero).map((p) => p.term);
  const stage2 = absorb(d1);
  const d2 = stage2.filter((s) => s.fate === "keep").map((s) => s.term);
  return { products, d1, stage2, d2 };
}

// Nelson's method on a CNF (clauses from parseCnf). The first clause is its own
// reduced DNF (an elementary disjunction: lemma 5 of the note); the others are
// multiplied in one by one. zero: the product became empty, f is identically 0.
export function nelson(clauses) {
  let current = clauses[0].map((l) => [l]);
  const first = current;
  const steps = [];
  for (let k = 1; k < clauses.length; k++) {
    const step = nelsonStep(current, clauses[k].map((l) => [l]));
    steps.push({ clause: k + 1, left: current, right: clauses[k], ...step });
    current = step.d2;
    if (!current.length) return { first, steps, result: [], zero: true };
  }
  return { first, steps, result: current, zero: false };
}

export function conjunctionText(term) {
  return term.map(literalText).join("");
}

export function dnfText(terms) {
  return terms.length ? terms.map(conjunctionText).join(" ∨ ") : "0";
}

export function cnfVector(clauses, n) {
  return vectorOf(n, (b) => clauses.every((c) => c.some((l) => (l.neg ? 1 - b[l.v - 1] : b[l.v - 1]) === 1)));
}

export function dnfVector(terms, n) {
  return vectorOf(n, (b) => terms.some((t) => t.every((l) => (l.neg ? 1 - b[l.v - 1] : b[l.v - 1]) === 1)));
}

// ------------------------------------------- shortest spanning tree

// The edges of the complete graph on vertices 1..n, as [a, b] with a < b in
// lexicographic order. A weight vector is aligned with this list.
export function completeEdges(n) {
  const out = [];
  for (let a = 1; a <= n; a++) for (let b = a + 1; b <= n; b++) out.push([a, b]);
  return out;
}

// Union-find over vertices 1..n; find returns the component representative.
function components(n) {
  const parent = Array.from({ length: n + 1 }, (_, i) => i);
  const find = (v) => { while (parent[v] !== v) { parent[v] = parent[parent[v]]; v = parent[v]; } return v; };
  return { find, join: (a, b) => { parent[find(a)] = find(b); }, same: (a, b) => find(a) === find(b) };
}

// The lecturer's algorithm. Step k takes, among the edges that close no cycle
// with the chosen ones, the lightest; with several lightest the pick decides:
// picks[k-1] is the preferred edge index, used when it is among them, else the
// first in the list. Each step: {k, candidates (lightest admissible, edge
// indices), chosen, weight, closing (edges outside E that would close a cycle
// before this pick)}. Stops after n - 1 edges.
export function kruskal(n, weights, picks = []) {
  const edges = completeEdges(n);
  const comp = components(n);
  const chosen = [];
  const steps = [];
  while (chosen.length < n - 1) {
    const admissible = [], closing = [];
    edges.forEach(([a, b], i) => {
      if (chosen.includes(i)) return;
      (comp.same(a, b) ? closing : admissible).push(i);
    });
    const lightest = Math.min(...admissible.map((i) => weights[i]));
    const candidates = admissible.filter((i) => weights[i] === lightest);
    const want = picks[chosen.length];
    const pick = candidates.includes(want) ? want : candidates[0];
    steps.push({ k: chosen.length + 1, candidates, chosen: pick, weight: lightest, closing });
    comp.join(edges[pick][0], edges[pick][1]);
    chosen.push(pick);
  }
  return { steps, chosen, weight: chosen.reduce((s, i) => s + weights[i], 0) };
}

// All spanning trees of K_n by brute force over (n-1)-subsets of edges:
// the minimum weight, the trees of that weight, and the number of all trees.
export function spanningTrees(n, weights) {
  const edges = completeEdges(n);
  let total = 0, min = Infinity, best = [];
  const pick = [];
  const rec = (from) => {
    if (pick.length === n - 1) {
      const comp = components(n);
      if (pick.some((i) => { const [a, b] = edges[i]; if (comp.same(a, b)) return true; comp.join(a, b); return false; })) return;
      total++;
      const w = pick.reduce((s, i) => s + weights[i], 0);
      if (w < min) { min = w; best = []; }
      if (w === min) best.push([...pick]);
      return;
    }
    for (let i = from; i < edges.length; i++) { pick.push(i); rec(i + 1); pick.pop(); }
  };
  rec(0);
  return { total, min, best };
}

export function edgeText(e) {
  return `(${e[0]},${e[1]})`;
}

// ------------------------------------------ the graph of a code

// Code words from text: separated by spaces, commas or semicolons; distinct,
// at most 8 words of at most 8 symbols each (the page draws the whole graph).
export function parseCode(src) {
  const words = src.split(/[\s,;]+/).filter(Boolean);
  if (!words.length) throw new FormulaError("введи кодовые слова через пробел или запятую", 0);
  if (words.length > 8) throw new FormulaError("кодовых слов не больше 8", 0);
  const seen = new Set();
  for (const w of words) {
    if (w.length > 8) throw new FormulaError(`слово "${w}" длиннее 8 символов`, 0);
    if (seen.has(w)) throw new FormulaError(`слово "${w}" повторяется: у двух букв одно кодовое слово, это уже неоднозначность`, 0);
    seen.add(w);
  }
  return words;
}

// The first way to cut str into at least minCount code words, as a list of
// word indices; null if there is none. The empty string is the empty list.
export function decompose(str, words, minCount = 0) {
  const walk = (rest, acc) => {
    if (rest === "") return acc.length >= minCount ? acc : null;
    for (let l = 0; l < words.length; l++) {
      if (rest.startsWith(words[l])) {
        const r = walk(rest.slice(words[l].length), [...acc, l]);
        if (r) return r;
      }
    }
    return null;
  };
  return walk(str, []);
}

// The number of ways to cut str into code words.
export function countParsings(str, words) {
  const ways = [1];
  for (let end = 1; end <= str.length; end++) {
    ways[end] = words.reduce((s, w) => s + (end >= w.length && ways[end - w.length] && str.endsWith(w, end) ? ways[end - w.length] : 0), 0);
  }
  return ways[str.length];
}

// G_phi of the note. Vertices: the empty word (index 0) and every word that
// is a proper beginning of some code word and a proper ending of some code
// word (not empty, not the whole word), by length then alphabet. An arc
// i -> j when a code word is beta_i D beta_j, D a run of s code words with
// s >= 0 for two nonempty ends, s >= 1 for one empty end, s >= 2 for two.
// arcs: {from, to, word (index), mid (the D text), D (code word indices)},
// one witness per pair.
export function codeGraph(words) {
  const begin = new Set(), end = new Set();
  for (const w of words) {
    for (let k = 1; k < w.length; k++) { begin.add(w.slice(0, k)); end.add(w.slice(w.length - k)); }
  }
  const vertices = ["", ...[...begin].filter((p) => end.has(p)).sort((p, q) => p.length - q.length || (p < q ? -1 : 1))];
  const arcs = [];
  vertices.forEach((bi, i) => vertices.forEach((bj, j) => {
    const need = (i === 0 ? 1 : 0) + (j === 0 ? 1 : 0);
    for (let l = 0; l < words.length; l++) {
      const w = words[l];
      if (w.length < bi.length + bj.length || !w.startsWith(bi) || !w.endsWith(bj)) continue;
      const mid = w.slice(bi.length, w.length - bj.length);
      const D = decompose(mid, words, need);
      if (D) { arcs.push({ from: i, to: j, word: l, mid, D }); break; }
    }
  }));
  return { vertices, arcs };
}

// The shortest directed cycle through the empty word, as the vertex indices
// [0, v1, ..., vn] (the arc vn -> 0 closes it; [0] is a loop); null if none.
export function cycleThroughEmpty(graph) {
  const { vertices, arcs } = graph;
  const dist = new Array(vertices.length).fill(-1), from = new Array(vertices.length).fill(-1);
  dist[0] = 0;
  const queue = [0];
  while (queue.length) {
    const u = queue.shift();
    for (const a of arcs) if (a.from === u && a.to !== 0 && dist[a.to] < 0) { dist[a.to] = dist[u] + 1; from[a.to] = u; queue.push(a.to); }
  }
  const back = arcs.filter((a) => a.to === 0 && dist[a.from] >= 0);
  if (!back.length) return null;
  const last = back.reduce((p, q) => (dist[q.from] < dist[p.from] ? q : p)).from;
  const path = [];
  for (let v = last; v >= 0; v = from[v]) { path.unshift(v); if (v === 0) break; }
  return path;
}

// From a cycle to a word with two parsings, as in the proof of the note:
// c_i = beta_i D_i beta_{i+1} is the code word of the arc i, w = D_0 beta_1 D_1 ... beta_n D_n.
// Parsing one takes c_i whole for even i and cuts D_i for odd i, parsing two the other way round.
// Each parsing is a list of code word indices.
export function ambiguousWord(words, graph, cycle) {
  const arcOf = (i, j) => graph.arcs.find((a) => a.from === i && a.to === j);
  const m = cycle.length;
  const parts = cycle.map((v, i) => arcOf(v, cycle[(i + 1) % m]));
  const pick = (odd) => parts.flatMap((a, i) => ((i % 2 === 1) === odd ? a.D : [a.word]));
  const one = pick(true), two = pick(false);
  return { word: one.map((l) => words[l]).join(""), one, two };
}

export function lettersOf(parsing) {
  return parsing.map((l) => String.fromCharCode(97 + l)).join("");
}

// ------------------------------------------------- Huffman's method

// Frequencies from text: numbers or name:number, separated by spaces, commas
// or semicolons; 2 to 10 positive numbers with at most 6 decimals. Returned
// as integers in units of 10^-d (d the longest fraction), so sums and ties
// are exact. names default to a, b, c...
export function parseFrequencies(src) {
  const tokens = src.split(/[\s,;]+/).filter(Boolean);
  if (tokens.length < 2) throw new FormulaError("нужно хотя бы две частоты, через пробел или запятую", 0);
  if (tokens.length > 10) throw new FormulaError("частот не больше 10", 0);
  const parsed = tokens.map((t, k) => {
    const [name, num] = t.includes(":") ? t.split(":") : [String.fromCharCode(97 + k), t];
    if (!/^\d+(\.\d{1,6})?$/.test(num ?? "")) throw new FormulaError(`"${t}" не число: частота пишется как 0.25 или 25`, 0);
    return { name, int: num.split(".")[0], frac: num.split(".")[1] ?? "" };
  });
  const d = Math.max(...parsed.map((p) => p.frac.length));
  const values = parsed.map((p) => Number(p.int + p.frac.padEnd(d, "0")));
  if (values.some((v) => v <= 0)) throw new FormulaError("частоты должны быть больше нуля", 0);
  if (new Set(parsed.map((p) => p.name)).size !== parsed.length) throw new FormulaError("имена символов повторяются", 0);
  return { names: parsed.map((p) => p.name), values, scale: 10 ** d, total: values.reduce((s, v) => s + v, 0) };
}

// Huffman's method as the note writes it: keep the list in descending order,
// glue the two last (the smallest) into one node with their sum, insert it
// after the last element that is at least as big, repeat until one node is
// left. In the final cutting the earlier of two glued nodes gets 0, the later 1.
// Nodes 0..n-1 are the symbols, the glued ones follow. steps: {list (node
// indices before the step), left, right, node (the new index), after}.
export function huffman(values) {
  const n = values.length;
  const weight = [...values];
  const kids = values.map(() => null);
  let list = values.map((_, i) => i).sort((a, b) => values[b] - values[a] || a - b);
  const steps = [];
  while (list.length > 1) {
    const right = list[list.length - 1], left = list[list.length - 2];
    const node = weight.length;
    weight.push(weight[left] + weight[right]);
    kids.push([left, right]);
    const rest = list.slice(0, -2);
    let at = rest.length;
    while (at > 0 && weight[rest[at - 1]] < weight[node]) at--;
    const after = [...rest.slice(0, at), node, ...rest.slice(at)];
    steps.push({ list, left, right, node, after });
    list = after;
  }
  const root = list[0];
  const codes = new Array(n).fill("");
  const walk = (v, code) => {
    if (kids[v] === null) { codes[v] = code; return; }
    walk(kids[v][0], code + "0");
    walk(kids[v][1], code + "1");
  };
  walk(root, "");
  const total = weight[root];
  const cost = codes.reduce((s, c, i) => s + values[i] * c.length, 0) / total;
  return { weight, kids, root, steps, codes, cost, glued: weight.slice(n, -1).reduce((s, w) => s + w, 0) / total };
}

// ---------------------------------------------- finite automaton

// An automaton without an initial state: next[q][a] is G(a, q), out[q][a] is
// F(a, q); states and input symbols are 0-based indices.

// The run from state q on a word (an array of input symbols): the states
// before each step and after the last, and the output symbols.
export function runAutomaton(aut, q, word) {
  const states = [q], outputs = [];
  let s = q;
  for (const a of word) {
    outputs.push(aut.out[s][a]);
    s = aut.next[s][a];
    states.push(s);
  }
  return { states, outputs };
}

// The classes of the relations R_m of the note: R_0 puts every state in one class,
// R_{m+1} keeps two states together when on every input symbol they give the same
// output and move into one class of R_m. cls[s] numbers the classes in order of the
// smallest state. The list runs to the first m where R_m = R_{m+1}, the end of the chain.
export function mooreSteps(aut) {
  const r = aut.next.length;
  const groups = (cls) => {
    const out = [];
    cls.forEach((c, s) => { (out[c] ??= []).push(s); });
    return out;
  };
  let cls = new Array(r).fill(0);
  const steps = [{ m: 0, cls, classes: groups(cls) }];
  for (;;) {
    const sig = (s) => aut.out[s].map((o, a) => `${o}:${cls[aut.next[s][a]]}`).join(",");
    const ids = new Map();
    const next = cls.map((_, s) => {
      const key = `${cls[s]}|${sig(s)}`;
      if (!ids.has(key)) ids.set(key, ids.size);
      return ids.get(key);
    });
    const stable = ids.size === steps[steps.length - 1].classes.length;
    if (stable) return steps;
    cls = next;
    steps.push({ m: steps.length, cls, classes: groups(cls) });
  }
}

// The shortest word that distinguishes states s and t (different outputs on it),
// found by breadth-first search over pairs of states; null for indistinguishable states.
export function distinguish(aut, s, t) {
  const seen = new Map([[`${s},${t}`, []]]);
  const queue = [[s, t]];
  while (queue.length) {
    const [x, y] = queue.shift();
    const word = seen.get(`${x},${y}`);
    for (let a = 0; a < aut.out[x].length; a++) {
      if (aut.out[x][a] !== aut.out[y][a]) return [...word, a];
    }
    for (let a = 0; a < aut.out[x].length; a++) {
      const key = `${aut.next[x][a]},${aut.next[y][a]}`;
      if (!seen.has(key)) { seen.set(key, [...word, a]); queue.push([aut.next[x][a], aut.next[y][a]]); }
    }
  }
  return null;
}

// ------------------------------------------------- Hamming's code

// k of the note: 2^(k-1) <= n <= 2^k - 1, the number of bits of n.
export function hammingK(n) {
  return 32 - Math.clz32(n);
}

// D_i, i = 0..k-1: the positions 1..n whose binary notation has a 1 in digit i from the right.
export function hammingSets(n) {
  return Array.from({ length: hammingK(n) }, (_, i) => Array.from({ length: n }, (_, j) => j + 1).filter((m) => (m >> i) & 1));
}

// The free (information) positions: 1..n except the powers of two, ascending.
export function hammingFreePositions(n) {
  return Array.from({ length: n }, (_, j) => j + 1).filter((m) => (m & (m - 1)) !== 0);
}

// The code word for the information bits (one per free position, in order):
// each check position 2^i takes the sum modulo 2 of the other coordinates of D_i.
// A word is an array of n bits, index j - 1 for position j.
export function hammingEncode(n, data) {
  const word = new Array(n).fill(0);
  hammingFreePositions(n).forEach((p, idx) => { word[p - 1] = data[idx] ? 1 : 0; });
  hammingSets(n).forEach((set, i) => {
    word[(1 << i) - 1] = set.filter((j) => j !== 1 << i).reduce((s, j) => s ^ word[j - 1], 0);
  });
  return word;
}

// The syndrome of a received word: delta_i = the sum of beta_j over D_i modulo 2, and
// its number (delta_{k-1}...delta_0) read in binary.
export function hammingSyndrome(n, word) {
  const delta = hammingSets(n).map((set) => set.reduce((s, j) => s ^ word[j - 1], 0));
  return { delta, number: delta.reduce((s, d, i) => s + (d << i), 0) };
}

// The receiver's correction: number 0 means no error, a number in 1..n names the
// position to flip, a number above n cannot come from one error (outside: true).
export function hammingCorrect(n, word) {
  const { delta, number } = hammingSyndrome(n, word);
  const fixed = [...word];
  const outside = number > n;
  if (number >= 1 && !outside) fixed[number - 1] ^= 1;
  return { delta, number, outside, word: fixed };
}

// Shannon entropy in bits of the frequencies.
export function entropy(values) {
  const total = values.reduce((s, v) => s + v, 0);
  return -values.reduce((s, v) => s + (v / total) * Math.log2(v / total), 0);
}

// The least cost of a prefix code for the frequencies, by brute force over all
// length assignments allowed by Kraft's inequality (n <= 7). Exact in the
// integer frequencies: the cost times the total.
export function optimalWeightedLength(values) {
  const n = values.length;
  let best = Infinity;
  const lengths = new Array(n).fill(0);
  const rec = (i, kraft, sum) => {
    if (sum >= best) return;
    if (i === n) { best = sum; return; }
    for (let l = 1; l <= n - 1; l++) {
      const k = kraft + 2 ** -l;
      if (k <= 1 + 1e-12) { lengths[i] = l; rec(i + 1, k, sum + values[i] * l); }
    }
  };
  rec(0, 0, 0);
  return best;
}
