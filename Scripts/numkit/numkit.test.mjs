// numkit.js against the python reference in fixtures.json (export_fixtures.py), and the pure
// functions of kernel-editor.js. Run: node --test numkit.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as ke from "./kernel-editor.js";
import * as nk from "./numkit.js";
import { matchAll, near, nearAll, mulVec, rel } from "./testkit.mjs";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));

// ---------------------------------------------------------------- expressions

test("the parser agrees with sympy on every formula at three points", () => {
  assert.ok(fx.parser.length > 60);
  for (const c of fx.parser) {
    const f = nk.compileExpression(c.src, ["x", "t"]);
    for (const [x, t, want] of c.points) rel(f(x, t), want, 1e-13, `${c.src} at (${x}, ${t})`);
  }
});

test("precedence and associativity, written out by hand", () => {
  const v = (s, x = 3, t = 2) => nk.compileExpression(s, ["x", "t"])(x, t);
  assert.equal(v("-x^2"), -9, "unary minus is looser than ^");
  assert.equal(v("(-x)^2"), 9);
  assert.equal(v("-2^2"), -4);
  assert.equal(v("2^3^2"), 512, "^ is right-associative");
  assert.equal(v("2^-1"), 0.5, "the exponent may carry a sign");
  assert.equal(v("2^-t^2"), 2 ** -4, "a signed exponent takes the power after it");
  assert.equal(v("1-2-3"), -4, "- is left-associative");
  assert.equal(v("8/2/2"), 2, "/ is left-associative");
  assert.equal(v("2+3*4"), 14);
  assert.equal(v("2*3^2"), 18);
  assert.equal(v("x - -t"), 5);
  assert.equal(v("1,5*2"), 3, "a comma is a decimal mark");
  assert.equal(v("1e-3*1000"), 1);
  assert.equal(v("  x  *  t  "), 6);
});

test("the parser reports errors with a stable code and the position of the offending character", () => {
  const bad = [
    ["", "empty", 0], ["   ", "empty", 0], ["2x", "missing-operator", 1], ["x t", "missing-operator", 2], ["2 (3)", "missing-operator", 2],
    ["2*", "unexpected-end", 2], ["x+", "unexpected-end", 2], ["(1+2", "unclosed", 4], ["sin(x", "unclosed", 5], ["1+2)", "unbalanced", 3],
    [")", "unbalanced", 0], ["sin x", "function-brackets", 4], ["foo(1)", "unknown-name", 0], ["1 + y", "unknown-name", 4],
    ["1 $ 2", "bad-char", 2], ["x+*2", "unexpected", 2], ["()", "unexpected", 1], ["*3", "unexpected", 0],
    ["toString(1)", "unknown-name", 0], ["constructor", "unknown-name", 0], ["x^", "unexpected-end", 2],
  ];
  for (const [src, code, pos] of bad) {
    assert.throws(() => nk.parseExpression(src), (e) => {
      assert.ok(e instanceof nk.ExprError, `${JSON.stringify(src)}: not an ExprError: ${e}`);
      assert.equal(e.code, code, `${JSON.stringify(src)}: code`);
      assert.equal(e.pos, pos, `${JSON.stringify(src)}: position`);
      assert.match(e.message, /[А-Яа-я]/, `${JSON.stringify(src)}: message in Russian`);
      return true;
    }, JSON.stringify(src));
  }
});

test("a variable outside the allowed set is an error: t in alpha(x), x in beta(t)", () => {
  assert.throws(() => nk.compileExpression("x*t", ["x"]), (e) => e.code === "bad-variable");
  assert.throws(() => nk.compileExpression("x", ["t"]), (e) => e.code === "bad-variable");
  assert.throws(() => nk.compileExpression("x", []), (e) => e.code === "bad-variable");
  assert.equal(nk.compileExpression("pi/2", [])(), Math.PI / 2);
  assert.equal(nk.evalConstant("-2*pi"), -2 * Math.PI);
  assert.equal(nk.evalConstant("0,5"), 0.5);
  assert.throws(() => nk.evalConstant("x"), (e) => e.code === "bad-variable");
  assert.equal(nk.compileExpression("x*t", ["t", "x"])(2, 5), 10, "arguments follow the order of names");
});

test("a course may name more variables: s and y, any listed name; a name not listed stays an error", () => {
  const f = nk.compileExpression("sin(x)*s^2 + y", ["x", "s", "y"]);
  near(f(0.5, 3, -1), Math.sin(0.5) * 9 - 1, 1e-15, "x, s, y in the order of names");
  assert.equal(nk.compileExpression("s*x", ["s", "x"])(2, 5), 10, "order of names, not alphabet");
  assert.equal(nk.compileExpression("tau*x", ["x", "tau"])(2, 5), 10, "a longer name is a variable when listed");
  for (const [src, names] of [["s", ["x"]], ["y", ["x", "s"]], ["x*s", ["x", "t"]]]) {
    assert.throws(() => nk.compileExpression(src, names), (e) => e.code === "bad-variable" && /[А-Яа-я]/.test(e.message), `${src} in ${names}`);
  }
  assert.throws(() => nk.compileExpression("w", ["x", "s"]), (e) => e.code === "unknown-name");
  assert.throws(() => nk.compileExpression("sin", ["sin"]), (e) => e.code === "function-brackets", "a function name is never a variable");
  assert.throws(() => nk.parseExpression("s"), (e) => e.code === "unknown-name", "the bare parser keeps its x and t");
  assert.equal(nk.compileExpression("e*pi", ["x"])(), Math.E * Math.PI, "constants are not variables");
});

test("the sources of numkit.js and kernel-editor.js have no eval and no Function constructor", () => {
  for (const file of ["./numkit.js", "./kernel-editor.js"]) {
    const src = readFileSync(new URL(file, import.meta.url), "utf8");
    assert.ok(!/\beval\s*\(/.test(src), `${file}: eval found`);
    assert.ok(!/\bFunction\s*\(|new\s+Function|\bFunction\b\s*\./.test(src.replace(/\/\/.*$/gm, "")), `${file}: Function constructor found`);
  }
});

// ---------------------------------------------------------------- quadrature

test("adaptive Gauss-Kronrod agrees with mpmath on smooth, kinked, singular and oscillating integrands", () => {
  assert.ok(fx.quad.length >= 20);
  for (const c of fx.quad) {
    const f = nk.compileExpression(c.src, ["x"]);
    const lo = nk.compileExpression(c.lo, [])(), hi = nk.compileExpression(c.hi, [])();
    const r = nk.integrate(f, lo, hi);
    assert.ok(r.ok, `${c.src}: not converged, err ${r.err}, ${r.intervals} intervals`);
    rel(r.value, c.value, 1e-10, c.src);
    // the estimate is an honest bound, not a decoration
    assert.ok(Math.abs(r.value - c.value) <= Math.max(10 * r.err, 1e-14), `${c.src}: error ${Math.abs(r.value - c.value)} above the estimate ${r.err}`);
  }
});

test("one 15-point Kronrod rule is exact for degree 22; the embedded Gauss rule vouches for degree 13", () => {
  const exact = (n) => (2 ** (n + 1) - (-1) ** (n + 1)) / (n + 1);
  // degree 22 on [-1, 2]: the Kronrod sum alone is exact, the Gauss estimate is not, so the rule alone is "not ok"
  const one = nk.integrate((x) => x ** 22, -1, 2, { maxIntervals: 1 });
  rel(one.value, exact(22), 1e-13, "K15 on x^22");
  assert.equal(one.ok, false);
  // degree 13: Gauss is exact too, the estimate falls to the floor and one interval is enough
  const g = nk.integrate((x) => x ** 13 - 3 * x ** 7 + x, -1, 2);
  assert.equal(g.intervals, 1);
  rel(g.value, exact(13) - 3 * exact(7) + exact(1), 1e-13, "value");
});

test("a singularity that roundoff hides at the endpoint ends in EvalError, not in a wrong number", () => {
  // 1 - x^2 cancels to 0 at the nodes nearest to -1 once the interval there is about 1e-16 wide
  assert.throws(() => nk.integrate((x) => 1 / Math.sqrt(1 - x * x), -1, 1), (e) => e instanceof nk.EvalError);
});

test("the error estimate is tight enough that smooth integrals take one interval and ln x about forty", () => {
  assert.equal(nk.integrate(Math.sin, 0, Math.PI).intervals, 1);
  assert.equal(nk.integrate(Math.exp, 0, 1).intervals, 1);
  assert.equal(nk.integrate((x) => 1 / (1 + x * x), 0, 1).intervals, 2);
  const ln = nk.integrate(Math.log, 0, 1);
  assert.ok(ln.intervals >= 20 && ln.intervals <= 60, `${ln.intervals} intervals for ln x`);
  const bump = nk.integrate((x) => Math.exp(-100 * (x - 0.5) ** 2), 0, 1);
  assert.ok(bump.intervals <= 10, `${bump.intervals} intervals for a narrow bump`);
});

test("the endpoints are never evaluated, and a > b flips the sign", () => {
  const seen = [];
  const r = nk.integrate((x) => { seen.push(x); return Math.log(x); }, 0, 1);
  assert.ok(!seen.includes(0) && !seen.includes(1), "an endpoint was evaluated");
  near(r.value, -1, 1e-11, "int ln");
  near(nk.integrate(Math.sin, Math.PI, 0).value, -2, 1e-13, "reversed");
  assert.deepEqual(nk.integrate(Math.sin, 1, 1), { value: 0, err: 0, ok: true, intervals: 0, scale: 0 });
});

test("a non-finite value raises EvalError with the point; a divergent integral stops at the interval limit", () => {
  assert.throws(() => nk.integrate((x) => Math.log(x), -1, 1), (e) => e instanceof nk.EvalError && e.code === "non-finite" && Number.isFinite(e.at));
  assert.throws(() => nk.integrate((x) => 1 / x, -1, 1), (e) => e instanceof nk.EvalError, "1/x hits the midpoint 0");
  const t0 = Date.now();
  const r = nk.integrate((x) => 1 / x, 0, 1);
  assert.equal(r.ok, false);
  assert.ok(r.intervals <= 400 && Date.now() - t0 < 5000, "ran past the limit");
});

// ---------------------------------------------------------------- dense linear algebra

test("LU: determinant, solution and condition number against hand-checked matrices", () => {
  const m = Float64Array.of(2, 1, 1, 3, 2, 1, 1, 0, 4);
  near(nk.det(m, 3), 2 * 8 - 1 * 11 + 1 * (-2), 1e-13, "det");
  // one row swap by pivoting flips the sign: the pivot 3 of the first column is below the 1
  near(nk.det(Float64Array.of(1, 2, 3, 4), 2), -2, 1e-14, "det with a swap");
  near(nk.det(Float64Array.of(0, 1, 1, 0), 2), -1, 1e-14, "det of a permutation");
  const x = nk.luSolve(nk.luDecompose(m, 3), Float64Array.of(1, 2, 3));
  nearAll(mulVec(m, 3, 3, x), [1, 2, 3], 1e-13, "A x");
  assert.equal(Math.abs(nk.det(Float64Array.of(1, 2, 2, 4), 2)), 0);
  assert.equal(nk.cond1(Float64Array.of(1, 2, 2, 4), 2), Infinity);
  near(nk.cond1(Float64Array.of(1, 0, 0, 1), 2), 1, 1e-15, "cond I");
  near(nk.cond1(Float64Array.of(1, 0, 0, 1e-12), 2) / 1e12, 1, 1e-9, "cond diag");
});

// ---------------------------------------------------------------- eigenvalues

test("eigenvalues match numpy on 56 matrices: random, triangular, Jordan, nilpotent, repeated, badly scaled", () => {
  assert.ok(fx.eigen.length >= 50);
  for (const c of fx.eigen) {
    const got = nk.eigenvalues(Float64Array.from(c.a), c.n);
    const top = Math.max(1, ...c.mu.map(([re, im]) => Math.hypot(re, im)));
    matchAll(got, c.mu, c.tol * top, c.name);
  }
});

test("eigenvalues: hand-checked cases and a matrix with NaN", () => {
  matchAll(nk.eigenvalues(Float64Array.of(0, -1, 1, 0), 2), [[0, 1], [0, -1]], 1e-14, "rotation");
  matchAll(nk.eigenvalues(Float64Array.of(2, 0, 0, 0, 3, 0, 0, 0, 5), 3), [[2, 0], [3, 0], [5, 0]], 1e-14, "diagonal");
  matchAll(nk.eigenvalues(Float64Array.of(7), 1), [[7, 0]], 0, "1x1");
  assert.throws(() => nk.eigenvalues(Float64Array.of(NaN, 1, 2, 3, 4, 5, 6, 7, 8), 3), /did not converge/);
});

test("deltaCoefficients equal the exact or numpy characteristic polynomial, and Delta by LU agrees with the polynomial", () => {
  for (const c of fx.eigen) {
    const A = Float64Array.from(c.a), d = nk.deltaCoefficients(A, c.n);
    const na = nk.norm1(A, c.n);
    assert.equal(d.length, c.n + 1);
    assert.equal(d[0], 1, `${c.name}: Delta(0) = 1`);
    c.delta.forEach((want, k) => {
      const scale = na ** k * 10 ** 3;
      assert.ok(Math.abs(d[k] - want) <= 1e-11 * scale + 1e-9 * Math.abs(want), `${c.name}: d_${k} = ${d[k]} vs ${want}`);
    });
    for (const lam of [-0.7, 0.3, 1.9]) {
      const horner = d.reduceRight((s, v) => s * lam + v, 0);
      // det(I - lambda A) by LU
      const lu = nk.det(Float64Array.from(A, (v, i) => (Math.floor(i / c.n) === i % c.n ? 1 : 0) - lam * v), c.n);
      const mag = d.reduce((s, v, k) => s + Math.abs(v) * Math.abs(lam) ** k, 0);
      assert.ok(Math.abs(horner - lu) <= 1e-9 * mag, `${c.name}: Delta(${lam}) ${horner} vs ${lu}`);
    }
  }
});

// ---------------------------------------------------------------- the text of a problem

test("compileProblem names the field and the row of a bad formula and rejects a bad interval", () => {
  const good = { lo: 0, hi: 1, rows: [{ alpha: "x", beta: "t" }, { alpha: "sin(x)", beta: "cos(t)" }], f: "x" };
  assert.equal(nk.compileProblem(good).n, 2);
  assert.throws(() => nk.compileProblem({ ...good, rows: [good.rows[0], { alpha: "sin(x)", beta: "cos(x)" }] }), (e) => e.field === "beta" && e.row === 1 && e.code === "bad-variable");
  assert.throws(() => nk.compileProblem({ ...good, rows: [{ alpha: "2x", beta: "t" }] }), (e) => e.field === "alpha" && e.row === 0 && e.code === "missing-operator");
  assert.throws(() => nk.compileProblem({ ...good, f: "x +" }), (e) => e.field === "f" && e.code === "unexpected-end");
  assert.throws(() => nk.compileProblem({ ...good, lo: 1, hi: 1 }), (e) => e.code === "bad-interval");
  assert.throws(() => nk.compileProblem({ ...good, lo: 0, hi: Infinity }), (e) => e.code === "bad-interval");
  assert.throws(() => nk.compileProblem({ ...good, rows: [] }), (e) => e.code === "no-terms");
});

// ---------------------------------------------------------------- kernel-editor.js, the parts that need no DOM

// the page supplies esc; here the same escaping stands in
globalThis.esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

test("sci keeps a small number visible, fmt and sub follow the page conventions", () => {
  assert.equal(ke.sci(0), "0");
  assert.equal(ke.sci(0.5), "0,5");
  assert.equal(ke.sci(1.2e-15), "1,2e−15");
  assert.equal(ke.sci(-3e7), "−3,0e+7");
  assert.equal(ke.fmt(1234.5678), "1235");
  assert.equal(ke.sub(10), "₁₀");
});

test("sciText and sciHtml write a number as the notes do: plain from 10^-3 to 10^4, else m·10^k with two digits", () => {
  const cases = [
    [0, "0", "0"], [0.5, "0,5", "0,5"], [0.001, "0,001", "0,001"], [1234.5678, "1235", "1235"], [9999, "9999", "9999"],
    [4.7e-4, "4,7·10⁻⁴", "4,7·10<sup>−4</sup>"], [1.4e-14, "1,4·10⁻¹⁴", "1,4·10<sup>−14</sup>"], [0.00099, "9,9·10⁻⁴", "9,9·10<sup>−4</sup>"],
    [12345, "1,2·10⁴", "1,2·10<sup>4</sup>"], [-3.2e-7, "−3,2·10⁻⁷", "−3,2·10<sup>−7</sup>"], [9.96e-5, "1·10⁻⁴", "1·10<sup>−4</sup>"],
    [2e-8, "2·10⁻⁸", "2·10<sup>−8</sup>"], [-0.25, "−0,25", "−0,25"], [3e12, "3·10¹²", "3·10<sup>12</sup>"],
    [Infinity, "∞", "∞"], [-Infinity, "−∞", "−∞"], [NaN, "—", "—"],
  ];
  for (const [x, text, html] of cases) {
    assert.equal(ke.sciText(x), text, `sciText(${x})`);
    assert.equal(ke.sciHtml(x), html, `sciHtml(${x})`);
  }
  assert.ok(!/e/.test(ke.sciText(1.2e-15)), "no letter e left");
});

test("sumOfTerms puts the sign of each coefficient inside the sum and escapes the formula text", () => {
  assert.equal(ke.sumOfTerms("x", [-1.5, 2], ["sin(x)", "cos(x)"]), "x − 1,5·(sin(x)) + 2·(cos(x))");
  assert.equal(ke.sumOfTerms("0", [1], ["a<b"]), "0 + 1·(a&lt;b)");
});

test("ticks gives nice positions inside the range, and a single one for an empty range", () => {
  nearAll(ke.ticks(0, 1), [0, 0.2, 0.4, 0.6, 0.8, 1], 1e-12, "ticks of [0, 1]");
  assert.deepEqual(ke.ticks(-3, 3), [-2, 0, 2], "the step is 1, 2 or 5 times a power of ten, the first one not below the range");
  assert.ok(ke.ticks(-1.7, 4).includes(0), "zero is a tick of a range that holds it");
  for (const v of ke.ticks(0.13, 7.4)) assert.ok(v >= 0.13 - 1e-9 && v <= 7.4 + 1e-9, `tick ${v} outside`);
  assert.deepEqual(ke.ticks(2, 2), [2]);
  assert.deepEqual(ke.ticks(3, 1), [3]);
});

test("decadeTicks gives whole exponents inside the range, thinned to the count; pow10 writes them with a superscript", () => {
  assert.deepEqual(ke.decadeTicks(1e-3, 1e2), [-3, -2, -1, 0, 1, 2]);
  assert.deepEqual(ke.decadeTicks(0.5e-3, 3), [-3, -2, -1, 0]);
  const wide = ke.decadeTicks(1e-16, 1e3, 6);
  assert.ok(wide.length <= 6 && wide.length >= 3, `thinned to at most the count: ${wide}`);
  for (let i = 1; i < wide.length; i++) assert.equal(wide[i] - wide[i - 1], wide[1] - wide[0], "an even step");
  assert.deepEqual(ke.decadeTicks(5, 5), [], "no whole decade inside a point range");
  assert.equal(ke.pow10(-3), "10⁻³");
  assert.equal(ke.pow10(12), "10¹²");
  assert.equal(ke.pow10(0), "1");
  assert.equal(ke.pow10(1), "10");
});

test("logRange takes whole decades around the positive data and ignores zeros, NaN and negatives", () => {
  assert.deepEqual(ke.logRange([[3e-5, 0.2, 0, NaN, -1]]), [1e-5, 1]);
  assert.deepEqual(ke.logRange([[1e-3], [1e-3]]), [1e-3, 1e-2], "a single decade gets a decade above");
  assert.deepEqual(ke.logRange([[0, NaN]]), [1e-1, 1], "no positive data: a default range");
  assert.deepEqual(ke.logRange([[2]], [1e-4]), [1e-4, 10], "the included values count");
});

test("yRange holds the data with a margin and is never degenerate", () => {
  const [lo, hi] = ke.yRange([[0, 1], [0.5, NaN]]);
  near(lo, -0.08, 1e-12, "a margin of 8 % of the span below");
  near(hi, 1.08, 1e-12, "and above");
  const [a, b] = ke.yRange([[2, 2, 2]]);
  assert.ok(a < 2 && b > 2, "constant data still has a range");
  assert.deepEqual(ke.yRange([[NaN, Infinity]]), [-1, 1]);
  const [c, d] = ke.yRange([[1, 2]], [10]);
  assert.ok(d > 10 && c < 1, "an included value widens the range");
});

test("describe names the place and the character of a formula error, and an integration error", () => {
  const e = new nk.ExprError("missing-operator", "пропущен знак", 1);
  e.place = "Ядро, строка 1, α₁(x)";
  assert.equal(ke.describe(e), "Ядро, строка 1, α₁(x), символ 2: пропущен знак");
  assert.equal(ke.describe(new nk.ExprError("empty", "формула пуста", 0)), "Формула: формула пуста");
  assert.match(ke.describe(new nk.EvalError(0.5)), /^Интеграл не вычислен: .*0\.5/);
  assert.equal(ke.describe(new Error("boom")), "boom");
});
