// nmcore.js against the python reference in fixtures.json (export_fixtures.py) and against the numbers
// printed in the notes of the course. The parser, quadrature, LU and eigenvalue tests are numkit's.
// Run: node --test nmcore.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as nk from "../../../Scripts/numkit/numkit.js";
import { near, nearAll, rel } from "../../../Scripts/numkit/testkit.mjs";
import * as nm from "./nmcore.js";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));
const byName = (name) => fx.cases.find((c) => c.name === name);
const A = (c) => Float64Array.from(c.A);
const paramsOf = (cfg) => ({ omega: cfg.omega, tau: cfg.tau });

const tridiag = (n) => Float64Array.from({ length: n * n }, (_, k) => { const i = Math.floor(k / n), j = k % n; return i === j ? 2 : Math.abs(i - j) === 1 ? -1 : 0; });
const ones = (n) => new Float64Array(n).fill(1);

// ---------------------------------------------------------------- against numpy and scipy

test("the transition matrix, its radius and its infinity norm match numpy on every case and method", () => {
  let configs = 0;
  for (const c of fx.cases) {
    for (const cfg of c.configs) {
      const S = nm.transitionMatrix(A(c), c.n, cfg.method, paramsOf(cfg));
      nearAll(Array.from(S), cfg.S, 1e-11, `${c.name} ${cfg.method} S`);
      near(nm.infNorm(S, c.n), cfg.normInf, 1e-11, `${c.name} ${cfg.method} norm`);
      rel(nm.spectralRadius(S, c.n), cfg.rho, 1e-9, `${c.name} ${cfg.method} ${cfg.omega ?? cfg.tau ?? ""} rho`);
      configs++;
    }
  }
  assert.ok(configs >= 60, `only ${configs} configurations compared`);
});

test("30 iterations by the componentwise formulas match the canonical form of numpy, also for divergent runs", () => {
  for (const c of fx.cases) {
    for (const cfg of c.configs) {
      const xs = nm.iterate(A(c), c.b, c.x0, c.n, cfg.method, paramsOf(cfg), 30);
      assert.equal(xs.length, 31);
      for (let k = 0; k <= 30; k++) {
        for (let i = 0; i < c.n; i++) rel(xs[k][i], cfg.iterates[k][i], 1e-9, `${c.name} ${cfg.method} ${cfg.omega ?? cfg.tau ?? ""} x^${k}[${i}]`);
      }
    }
  }
});

test("the error z^{k+1} = S z^k holds along every run: the transition matrix describes the iteration", () => {
  for (const c of fx.cases) {
    for (const cfg of c.configs) {
      const S = nm.transitionMatrix(A(c), c.n, cfg.method, paramsOf(cfg));
      const xs = nm.iterate(A(c), c.b, c.x0, c.n, cfg.method, paramsOf(cfg), 6);
      for (let k = 0; k < 6; k++) {
        const z = Array.from(xs[k], (v, i) => v - c.exact[i]), z1 = Array.from(xs[k + 1], (v, i) => v - c.exact[i]);
        for (let i = 0; i < c.n; i++) {
          let s = 0;
          for (let j = 0; j < c.n; j++) s += S[i * c.n + j] * z[j];
          rel(z1[i], s, 1e-8 * Math.max(1, Math.abs(z[i])), `${c.name} ${cfg.method} k=${k} i=${i}`);
        }
      }
    }
  }
});

test("the exact solution, the dominance q, symmetry and positive definiteness match numpy", () => {
  for (const c of fx.cases) {
    nearAll(Array.from(nm.solveExact(A(c), c.b, c.n)), c.exact, 1e-9, `${c.name} exact`);
    near(nm.dominanceQ(A(c), c.n), c.dominanceQ, 1e-12, `${c.name} q`);
    assert.equal(nm.isSymmetric(A(c), c.n), c.symmetric, `${c.name} symmetric`);
    assert.equal(c.symmetric && nm.isPositiveDefinite(A(c), c.n), c.positiveDefinite, `${c.name} positive definite`);
  }
});

test("the condition of Samarsky agrees with the eigenvalues of B1 - tau/2 A, and is null for a matrix it does not cover", () => {
  let decided = 0;
  for (const c of fx.cases) {
    for (const cfg of c.configs) {
      const got = nm.samarskyHolds(A(c), c.n, cfg.method, paramsOf(cfg));
      assert.equal(got, cfg.samarsky, `${c.name} ${cfg.method} ${cfg.omega ?? cfg.tau ?? ""}`);
      if (got !== null) decided++;
    }
  }
  assert.ok(decided >= 20, `only ${decided} decided cases`);
  assert.ok(fx.cases.some((c) => c.configs.some((cfg) => cfg.samarsky === false)), "the fixtures must contain a violated condition");
  assert.ok(fx.cases.some((c) => c.configs.some((cfg) => cfg.samarsky === null)), "and a matrix that the theorem does not cover");
});

test("the best omega and the best tau reach the minimum that scipy finds", () => {
  for (const c of fx.cases) {
    const w = nm.bestParameter(A(c), c.n, "relax", 1e-3, 2 - 1e-3);
    near(w.rho, c.bestOmega.rho, 1e-6, `${c.name} rho at the best omega`);
    near(w.param, c.bestOmega.param, 2e-3, `${c.name} best omega`);
    if (c.bestTau) {
      const t = nm.bestParameter(A(c), c.n, "explicit", 1e-3, 2.4 / c.tauOptimal.M);
      near(t.rho, c.bestTau.rho, 1e-6, `${c.name} rho at the best tau`);
      near(t.param, c.bestTau.param, 1e-5, `${c.name} best tau`);
      const o = nm.optimalTau(A(c), c.n);
      near(o.tau, c.tauOptimal.tau, 1e-9, `${c.name} tau0`);
      near(o.rho, c.tauOptimal.rho, 1e-9, `${c.name} rho at tau0`);
      near(o.m, c.tauOptimal.m, 1e-9, `${c.name} m`);
      near(o.M, c.tauOptimal.M, 1e-9, `${c.name} M`);
    } else {
      assert.equal(nm.optimalTau(A(c), c.n), null, `${c.name}: no tau0 for a matrix that is not symmetric positive definite`);
    }
  }
});

test("the radius curve is the radius at each node", () => {
  const c = byName("pd-08");
  const grid = [0.2, 0.7, 1, 1.4, 1.9];
  const curve = nm.radiusCurve(A(c), c.n, "relax", grid);
  grid.forEach((w, i) => rel(curve[i], nm.spectralRadius(nm.transitionMatrix(A(c), c.n, "relax", { omega: w }), c.n), 1e-12, `omega ${w}`));
  const tc = nm.radiusCurve(A(c), c.n, "explicit", [0.1, 0.5]);
  rel(tc[0], Math.max(...[0.2, 0.2, 2.6].map((m) => Math.abs(1 - 0.1 * m))), 1e-9, "tau 0.1: 1 - tau mu over mu = 0.2, 2.6");
});

// ---------------------------------------------------------------- the numbers of the notes

const NOTE = Float64Array.from([4, 1, 1, 1, 5, 2, 0, 2, 4]), NOTE_B = [9, 17, 16], X0 = [0, 0, 0];

test("note 'Итерационные методы решения СЛАУ': the first Jacobi and Seidel steps and the table of errors", () => {
  const j = nm.iterate(NOTE, NOTE_B, X0, 3, "jacobi", {}, 4), s = nm.iterate(NOTE, NOTE_B, X0, 3, "seidel", {}, 4);
  nearAll(j[1], [2.25, 3.4, 4], 1e-12, "Jacobi x^1");
  nearAll(j[2], [0.4, 1.35, 2.3], 1e-12, "Jacobi x^2");
  nearAll(s[1], [2.25, 2.95, 2.525], 1e-12, "Seidel x^1");
  const exact = [1, 2, 3];
  nearAll(nm.errorsOf(j, exact), [3, 1.4, 0.7, 0.4, 0.2], 1e-12, "Jacobi errors of the table, up to the printed digits");
  nearAll(nm.errorsOf(s, exact), [3, 1.25, 0.214, 0.0481, 0.0108], 5e-4, "Seidel errors of the table");
  assert.ok(nm.errorsOf(s, exact)[2] > 0.2135 && nm.errorsOf(s, exact)[2] < 0.2145);
  nearAll(nm.solveExact(NOTE, NOTE_B, 3), exact, 1e-13, "solution");
  near(nm.dominanceQ(NOTE, 3), 0.6, 1e-15, "q");
});

test("note 'Сходимость стационарных итерационных методов': rho of the Jacobi and Seidel matrices of two examples", () => {
  const rJ = nm.spectralRadius(nm.transitionMatrix(NOTE, 3, "jacobi"), 3), rS = nm.spectralRadius(nm.transitionMatrix(NOTE, 3, "seidel"), 3);
  near(rJ, 0.544, 5e-4, "Jacobi, root of l^3 - l/4 + 1/40");
  near(rS, 9 / 40, 1e-9, "Seidel, eigenvalues 0, 0, 9/40");
  near(nm.infNorm(nm.transitionMatrix(NOTE, 3, "seidel"), 3), 0.5, 1e-12, "Seidel norm");
  const T3 = tridiag(3);
  near(nm.spectralRadius(nm.transitionMatrix(T3, 3, "jacobi"), 3), Math.SQRT1_2, 1e-12, "tridiag Jacobi sqrt(2)/2");
  near(nm.spectralRadius(nm.transitionMatrix(T3, 3, "seidel"), 3), 0.5, 1e-12, "tridiag Seidel 1/2");
  assert.equal(nm.dominanceQ(T3, 3), 1, "no dominance: q = 1");
  const S = nm.transitionMatrix(T3, 3, "seidel");
  nearAll(Array.from(S), [0, 0.5, 0, 0, 0.25, 0.5, 0, 0.125, 0.25], 1e-14, "the Seidel matrix of the note");
});

test("note 'Теорема Самарского': 0,8·1 + 0,2·I, Jacobi diverges, relaxation converges for every omega in (0, 2)", () => {
  const P = Float64Array.from([1, 0.8, 0.8, 0.8, 1, 0.8, 0.8, 0.8, 1]);
  near(nm.spectralRadius(nm.transitionMatrix(P, 3, "jacobi"), 3), 1.6, 1e-12, "Jacobi");
  assert.equal(nm.samarskyHolds(P, 3, "jacobi", {}), false, "2D - A has the eigenvalue -0,6");
  for (const [w, r] of [[0.5, 0.877], [1, 0.716], [1.5, 0.770]]) {
    near(nm.spectralRadius(nm.transitionMatrix(P, 3, "relax", { omega: w }), 3), r, 5e-4, `omega ${w}`);
  }
  for (const w of [0.05, 0.4, 1, 1.6, 1.95]) assert.equal(nm.samarskyHolds(P, 3, "relax", { omega: w }), true, `omega ${w}`);
  for (const w of [2, 2.2]) assert.equal(nm.samarskyHolds(P, 3, "relax", { omega: w }), false, `omega ${w}`);
  assert.ok(nm.spectralRadius(nm.transitionMatrix(P, 3, "relax", { omega: 2.2 }), 3) > 1, "and the method diverges beyond 2");
  // the boundary is decided with a tolerance of 1e-12 of the entries: a margin of rounding noise is not "holds"
  assert.equal(nm.samarskyHolds(P, 3, "relax", { omega: 2 - 2 ** -51 }), false, "2 - 4e-16 is the boundary within rounding");
  assert.equal(nm.samarskyHolds(P, 3, "relax", { omega: 2 - 1e-6 }), true, "a real margin of 1e-6 is");
});

test("positive definiteness by Cholesky: strict, so a singular or indefinite or NaN matrix is not", () => {
  const pd = (m, n) => nm.isPositiveDefinite(Float64Array.from(m), n);
  assert.equal(pd([2, 1, 1, 2], 2), true);
  assert.equal(pd([1, 1, 1, 1], 2), false, "singular, nonnegative");
  assert.equal(pd([1, 2, 2, 1], 2), false, "indefinite");
  assert.equal(pd([-1], 1), false);
  assert.equal(pd([NaN, 0, 0, 1], 2), false);
});

test("note 'Теорема Самарского': tridiag n = 20, rho of Jacobi, Seidel, the optimal omega with rho = omega - 1", () => {
  const T = tridiag(20);
  near(nm.spectralRadius(nm.transitionMatrix(T, 20, "jacobi"), 20), Math.cos(Math.PI / 21), 1e-9, "Jacobi cos(pi/21)");
  near(nm.spectralRadius(nm.transitionMatrix(T, 20, "seidel"), 20), Math.cos(Math.PI / 21) ** 2, 1e-9, "Seidel is the square");
  const best = nm.bestParameter(T, 20, "relax", 0.01, 1.99);
  const wopt = 2 / (1 + Math.sin(Math.PI / 21));
  near(best.param, wopt, 2e-4, "omega_opt = 1,741");
  near(best.rho, wopt - 1, 1e-6, "rho = omega - 1 at the optimum");
  near(nm.spectralRadius(nm.transitionMatrix(T, 20, "relax", { omega: 1.9 }), 20), 0.9, 1e-6, "rho = omega - 1 beyond the optimum");
});

test("note 'Оптимальный выбор итерационного параметра': tridiag n = 5, tau0 = 1/2, rho = sqrt(3)/2, 97 and 186 steps", () => {
  const T = tridiag(5), o = nm.optimalTau(T, 5);
  near(o.m, 2 - Math.sqrt(3), 1e-12, "m");
  near(o.M, 2 + Math.sqrt(3), 1e-12, "M");
  near(o.tau, 0.5, 1e-12, "tau0");
  near(o.rho, Math.sqrt(3) / 2, 1e-12, "rho");
  const rho = (tau) => nm.spectralRadius(nm.transitionMatrix(T, 5, "explicit", { tau }), 5);
  near(rho(0.5), Math.sqrt(3) / 2, 1e-12, "tau 1/2");
  near(rho(1 / o.M), 0.928, 5e-4, "tau = 1/M, rho = 1 - xi");
  near(rho(0.6), 1.239, 5e-4, "tau = 0,6 > 2/M diverges");
  assert.equal(nm.stepsToReduce(Math.sqrt(3) / 2), 97);
  assert.equal(nm.stepsToReduce(rho(1 / o.M)), 186);
  assert.equal(nm.stepsToReduce(1.2), Infinity);
  const xi = 7 - 4 * Math.sqrt(3);
  near(o.m / o.M, xi, 1e-12, "xi = m/M = 7 - 4 sqrt(3)");
  near(o.rho, (1 - xi) / (1 + xi), 1e-12, "(1 - xi)/(1 + xi)");
  const same = nm.transitionMatrix(T, 5, "jacobi"), tau = nm.transitionMatrix(T, 5, "explicit", { tau: 0.5 });
  nearAll(Array.from(same), Array.from(tau), 1e-14, "tau0 = 1/2 with B = I is the Jacobi matrix, as the note says");
});

// ---------------------------------------------------------------- errors and edge cases

test("a zero on the diagonal is reported in Russian for the methods that divide by it, not for the explicit one", () => {
  const Z = Float64Array.from([0, 1, 1, 2]);
  for (const m of ["jacobi", "seidel", "relax"]) {
    assert.throws(() => nm.transitionMatrix(Z, 2, m, { omega: 1 }), (e) => e instanceof nm.IterationError && e.code === "zero-diagonal" && /[А-Яа-я]/.test(e.message), m);
    assert.throws(() => nm.iterate(Z, [1, 1], [0, 0], 2, m, { omega: 1 }, 3), (e) => e.code === "zero-diagonal", m);
  }
  assert.doesNotThrow(() => nm.iterate(Z, [1, 1], [0, 0], 2, "explicit", { tau: 0.1 }, 3));
  assert.equal(nm.dominanceQ(Z, 2), null);
  assert.throws(() => nm.canonicalForm(Z, 2, "nope"), (e) => e.code === "bad-method");
});

test("a singular matrix has no exact solution, and the spectral radius of a matrix with NaN is NaN", () => {
  assert.equal(nm.solveExact(Float64Array.from([1, 2, 2, 4]), [1, 1], 2), null);
  assert.ok(Number.isNaN(nm.spectralRadius(Float64Array.from([NaN, 1, 1, 1]), 2)));
  assert.equal(nm.stepsToReduce(0), 1);
});

test("a run that diverges to infinity stays an array of numbers and its error grows like rho^k", () => {
  const P = Float64Array.from([1, 0.8, 0.8, 0.8, 1, 0.8, 0.8, 0.8, 1]);
  const xs = nm.iterate(P, [2.6, 2.6, 2.6], [0, 0, 0], 3, "jacobi", {}, 200);
  const e = nm.errorsOf(xs, nm.solveExact(P, [2.6, 2.6, 2.6], 3));
  assert.ok(e[200] > 1e30 || !Number.isFinite(e[200]));
  rel(e[40] / e[39], 1.6, 1e-3, "the ratio of neighbouring errors tends to rho");
  for (const x of xs) assert.ok(x instanceof Float64Array && x.length === 3);
});

// ================================================================ equations of the second kind

const sk = fx.secondKind;
const problemOf = (name, over = {}) => {
  const s = { ...sk.specs[name], ...over };
  return nm.makeProblem({ kind: s.kind, lo: s.lo, hi: s.hi, kernel: s.kernel, f: s.f, lambda: s.lam, exact: s.exact });
};
const exactOf = (name) => problemOf(name).exact;
const sing = (e) => e instanceof nm.ProblemError && e.code === "singular";
// a singular system is reported, or its condition number gives it away
const singularOrIllConditioned = (run) => {
  try { return run().cond >= 1e12; } catch (e) { assert.ok(sing(e), String(e)); return true; }
};

test("Gauss-Legendre nodes and weights match numpy leggauss", () => {
  for (const c of sk.gauss) {
    const g = nm.gaussLegendre(c.n);
    nearAll(Array.from(g.x), c.x, 1e-14, `nodes n=${c.n}`);
    nearAll(Array.from(g.w), c.w, 1e-14, `weights n=${c.n}`);
  }
  const comp = nm.compositeGauss(0, 2, 3, 5);
  near(comp.w.reduce((s, v) => s + v, 0), 2, 1e-14, "the weights of the composite rule sum to the length");
  near(comp.x.reduce((s, v, i) => s + v * comp.w[i], 0), 2, 1e-14, "and integrate x over [0, 2]");
});

test("the weights of the rules: the trapezoid, Simpson, and Simpson needs an odd number of nodes", () => {
  nearAll(Array.from(nm.trapezoidWeights(4, 0.5)), [0.25, 0.5, 0.5, 0.25], 1e-15, "trapezoid");
  nearAll(Array.from(nm.simpsonWeights(5, 0.25)), [1 / 12, 1 / 3, 1 / 6, 1 / 3, 1 / 12], 1e-15, "Simpson");
  for (const n of [2, 4, 1]) assert.throws(() => nm.simpsonWeights(n, 1), (e) => e.code === "simpson-odd" && /[А-Яа-я]/.test(e.message), `n=${n}`);
  nearAll(Array.from(nm.uniformGrid(0, 1, 5)), [0, 0.25, 0.5, 0.75, 1], 1e-15, "grid");
  assert.deepEqual(Array.from(nm.uniformGrid(2, 4, 1)), [3], "one node is the midpoint");
});

test("the series of a kernel in x by jets agrees with the sympy derivatives, over 19 formulas and 4 values of s", () => {
  let checked = 0;
  for (const c of sk.jets) {
    const taylor = nm.kernelTaylor(c.text, c.D, c.x0);
    c.s.forEach((s, i) => {
      const got = taylor(s);
      assert.equal(got.length, c.D + 1);
      for (let k = 0; k <= c.D; k++) { rel(got[k], c.coef[i][k], 1e-11, `${c.text} s=${s} k=${k}`); checked++; }
    });
  }
  assert.equal(checked, 19 * 4 * 9);
});

test("a kernel that is not analytic at the centre is reported in Russian, with the field", () => {
  for (const [src, x0] of [["abs(x)", 0], ["log(x)", 0], ["1/x", 0], ["sqrt(x)", 0], ["x^0.5", 0], ["log(x - 1)*s", 0]]) {
    assert.throws(() => nm.kernelTaylor(src, 4, x0)(0.5), (e) => e instanceof nm.ProblemError && e.code === "not-analytic" && e.field === "kernel" && /[А-Яа-я]/.test(e.message), src);
  }
  assert.doesNotThrow(() => nm.kernelTaylor("abs(x)", 4, 1)(0.5));
});

test("makeProblem names the field of a bad input and lets the nonlinear kernel use y", () => {
  const base = { lo: 0, hi: 1, kernel: "x*s", f: "x", lambda: 1 };
  assert.throws(() => nm.makeProblem({ ...base, lo: 1, hi: 1 }), (e) => e.code === "bad-interval" && e.field === "interval");
  assert.throws(() => nm.makeProblem({ ...base, hi: Infinity }), (e) => e.code === "bad-interval");
  assert.throws(() => nm.makeProblem({ ...base, lambda: NaN }), (e) => e.code === "bad-lambda" && e.field === "lambda");
  assert.throws(() => nm.makeProblem({ ...base, kernel: "x*+" }), (e) => e instanceof nk.ExprError && e.field === "kernel");
  assert.throws(() => nm.makeProblem({ ...base, kernel: "x*y" }), (e) => e.code === "bad-variable" && e.field === "kernel", "y in a linear kernel");
  assert.throws(() => nm.makeProblem({ ...base, f: "x*s" }), (e) => e.code === "bad-variable" && e.field === "f", "s in f(x)");
  assert.throws(() => nm.makeProblem({ ...base, exact: "2x" }), (e) => e.code === "missing-operator" && e.field === "exact");
  const nl = nm.makeProblem({ ...base, kind: "volterra-nonlinear", kernel: "x*s*y^2" });
  assert.equal(nl.K(2, 3, 4), 96);
  assert.equal(nm.makeProblem(base).exact, null);
});

// ---- the method of quadratures

test("Fredholm quadratures match numpy: the solution, the matrix and its condition number, trapezoid and Simpson", () => {
  for (const c of sk.quadrature) {
    const sol = nm.quadratureFredholm(problemOf(c.spec), c.n, c.rule);
    nearAll(Array.from(sol.nodes), c.x, 1e-14, `${c.spec} ${c.rule} ${c.n} nodes`);
    for (let i = 0; i < c.n; i++) rel(sol.y[i], c.y[i], 1e-10, `${c.spec} ${c.rule} ${c.n} y[${i}]`);
    rel(sol.cond, c.cond1, 1e-6, `${c.spec} ${c.rule} ${c.n} cond1`);
    if (c.matrix) nearAll(Array.from(sol.matrix), c.matrix, 1e-12, `${c.spec} ${c.rule} ${c.n} matrix`);
  }
});

test("note 'Метод квадратур': the periodic kernel converges like 4^-N and sits at rounding level by n = 37; Simpson is slower", () => {
  const p = problemOf("periodic"), ex = exactOf("periodic");
  const trap = [[5, 0.45], [9, 1.9e-3], [13, 7.3e-6], [17, 2.8e-8]];
  for (const [n, e] of trap) rel(nm.nodeError(nm.quadratureFredholm(p, n), ex), e, 0.05, `trapezoid n=${n}`);
  assert.ok(nm.nodeError(nm.quadratureFredholm(p, 25), ex) < 1e-12);
  assert.ok(nm.nodeError(nm.quadratureFredholm(p, 37), ex) < 5e-14, "1,4e-14 in the note");
  const simp = [[25, 2.8e-6], [37, 6.9e-10]];
  for (const [n, e] of simp) rel(nm.nodeError(nm.quadratureFredholm(p, n, "simpson"), ex), e, 0.05, `Simpson n=${n}`);
  assert.ok(nm.nodeError(nm.quadratureFredholm(p, 49, "simpson"), ex) < 5e-13);
  rel(nm.quadratureFredholm(p, 37).cond, 2.7, 0.2, "the note gives a condition number of about 2,7");
  const sol = nm.quadratureFredholm(p, 37), x = sol.nodes[10];
  near(sol.at(x), ex(x), 5e-13, "the Nystrom interpolation at a node is the solution");
  near(sol.at(0.123), ex(0.123), 1e-10, "and between nodes it is accurate too");
});

test("note 'Метод квадратур', task 2: the error of the trapezoid for K = xs is h^2 / (10 - h^2) at x = 1", () => {
  const p = problemOf("xs"), ex = exactOf("xs");
  for (const n of [3, 5, 11, 81]) {
    const h = 1 / (n - 1), sol = nm.quadratureFredholm(p, n);
    near(sol.y[n - 1] - 1, h * h / (10 - h * h), 1e-13, `n=${n}`);
    near(nm.nodeError(sol, ex), h * h / (10 - h * h), 1e-13, `max error n=${n}`);
  }
});

test("a Fredholm system at a characteristic number is reported or shows a huge condition number; a bad kernel value is named", () => {
  assert.ok(singularOrIllConditioned(() => nm.quadratureFredholm(problemOf("xs", { lam: 8 / 3 }), 3)), "lambda = 1/0,375 with three trapezoid nodes");
  assert.throws(() => nm.quadratureFredholm(nm.makeProblem({ lo: 0, hi: 1, kernel: "1/(x-s)", f: "1" }), 5), (e) => e.code === "bad-value" && /K\(/.test(e.message));
  assert.throws(() => nm.quadratureFredholm(nm.makeProblem({ lo: 0, hi: 1, kernel: "x*s", f: "1/x" }), 5), (e) => e.code === "bad-value" && /f\(/.test(e.message));
});

test("Volterra quadratures match numpy loops: linear and nonlinear, trapezoid and Simpson with the 5h/6 row", () => {
  for (const c of sk.volterra) {
    const sol = nm.quadratureVolterra(problemOf(c.spec), c.n, c.rule);
    for (let i = 0; i < c.n; i++) rel(sol.y[i], c.y[i], 1e-10, `${c.spec} ${c.rule} ${c.n} y[${i}]`);
  }
  assert.equal(sk.volterra.length, 8 * 2 + 3 * 2 + 4 + 2 * 1 + 2 + 2 - 4 + 0, "the fixtures hold every listed case");
});

test("note 'Метод квадратур для уравнений Вольтерра': y = 1 for K = exp(-(x-s)); the error grows like h^2 x / 12", () => {
  const p = problemOf("volterra-exp"), ex = exactOf("volterra-exp");
  const five = nm.quadratureVolterra(p, 5);
  nearAll(Array.from(five.y), [1, 1.001315, 1.002632, 1.003951, 1.005272], 6e-7, "n = 5");
  const twenty1 = nm.quadratureVolterra(p, 21);
  near(twenty1.y[5], 1.000052, 6e-7, "n = 21, x = 0,25");
  near(twenty1.y[20], 1.000208, 6e-7, "n = 21, x = 1");
  const e5 = nm.nodeError(five, ex), e21 = nm.nodeError(twenty1, ex);
  rel(e5 / e21, 25.3, 0.02, "five times smaller step, 25 times smaller error: order two");
  near(e21, 0.05 ** 2 / 12, 1e-5, "h^2 x / 12 at x = 1");
  assert.ok(five.cond >= 1 && Number.isFinite(five.cond));
  for (let i = 0; i < 5; i++) for (let j = i + 1; j < 5; j++) assert.equal(five.matrix[i * 5 + j], 0, "the matrix is lower triangular");
});

test("Volterra: the mixed Simpson rule is of order three (the trapezoid on the last interval of an odd row), the trapezoid of order two; the quadratic nonlinear note", () => {
  const p = problemOf("volterra-sin"), ex = exactOf("volterra-sin");
  const s = [33, 65, 129].map((n) => nm.nodeError(nm.quadratureVolterra(p, n, "simpson"), ex));
  const t = [33, 65, 129].map((n) => nm.nodeError(nm.quadratureVolterra(p, n), ex));
  assert.ok(s[0] / s[1] > 6.5 && s[0] / s[1] < 10 && s[1] / s[2] > 6.5 && s[1] / s[2] < 10, `Simpson ratios ${s[0] / s[1]}, ${s[1] / s[2]}`);
  assert.ok(t[0] / t[1] > 3.6 && t[0] / t[1] < 4.4 && t[1] / t[2] > 3.6 && t[1] / t[2] < 4.4, `trapezoid ratios ${t[0] / t[1]}, ${t[1] / t[2]}`);
  assert.ok(t[0] > 3 * s[0], "and Simpson is the more accurate on this smooth problem");
  const nl = nm.quadratureVolterra(problemOf("volterra-nl"), 6);
  nearAll(Array.from(nl.y, (v) => v - 1), [0, 6.7e-7, 1.4e-6, 2.1e-6, 2.8e-6, 3.5e-6], 6e-8, "y - 1 of the note, h = 0,02");
  const a = nm.nodeError(nm.quadratureVolterra(problemOf("volterra-nl2"), 9), exactOf("volterra-nl2")), b = nm.nodeError(nm.quadratureVolterra(problemOf("volterra-nl2"), 17), exactOf("volterra-nl2"));
  assert.ok(a / b > 3.5 && a / b < 4.5, `nonlinear order two: ${a / b}`);
});

test("Volterra errors: a zero pivot and a step the scalar equation cannot take are named", () => {
  const sing1 = nm.makeProblem({ kind: "volterra", lo: 0, hi: 1, kernel: "1", f: "1", lambda: 4 });
  assert.throws(() => nm.quadratureVolterra(sing1, 3), sing, "1 - lam A K = 0");
  const stiff = nm.makeProblem({ kind: "volterra-nonlinear", lo: 0, hi: 5, kernel: "10*y^2", f: "1" });
  assert.throws(() => nm.quadratureVolterra(stiff, 3), (e) => e.code === "no-root" && /[А-Яа-я]/.test(e.message));
});

// ---- simple iteration

test("simple iteration matches numpy: the number of steps, the stop, the limit, and the diverging runs", () => {
  for (const c of sk.iteration) {
    const r = nm.simpleIteration(problemOf(c.spec), c.n, { tol: c.tol });
    assert.equal(r.converged, c.converged, `${c.spec} converged`);
    assert.equal(r.diverged, c.diverged, `${c.spec} diverged`);
    assert.equal(r.iterations, c.iterations, `${c.spec} steps`);
    if (c.y) for (let i = 0; i < c.n; i++) rel(r.y[i], c.y[i], 1e-9, `${c.spec} y[${i}]`);
  }
  assert.ok(sk.iteration.some((c) => c.diverged || !c.converged) && sk.iteration.some((c) => c.converged), "both outcomes are in the fixtures");
});

test("the limit of the simple iteration is the solution of the quadrature system; a Volterra equation converges for any lambda", () => {
  const p = problemOf("xs"), it = nm.simpleIteration(p, 9, { tol: 1e-12 }), q = nm.quadratureFredholm(p, 9);
  nearAll(Array.from(it.y), Array.from(q.y), 1e-10, "xs");
  const big = problemOf("volterra-exp", { lam: 20 }), itv = nm.simpleIteration(big, 21, { tol: 1e-10, maxIter: 5000 }), qv = nm.quadratureVolterra(big, 21);
  assert.ok(itv.converged, "factorial convergence, no condition on lambda");
  for (let i = 0; i < 21; i++) rel(itv.y[i], qv.y[i], 1e-7, `Volterra y[${i}]`);
  assert.ok(nm.simpleIteration(problemOf("xs", { lam: 10 }), 9, { tol: 1e-8 }).diverged, "lambda = 10 for a Fredholm kernel of norm 1/2");
  const kz = nm.simpleIteration(problemOf("volterra-exp", { kernel: "0*x*s" }), 6);
  assert.equal(kz.iterations, 1, "K = 0: the first step y = f changes nothing");
  assert.equal(kz.converged, true);
});

// ---- degenerate kernels

test("degenerate kernels match scipy: the terms, the matrix, the coefficients, the error and the norms", () => {
  for (const c of sk.degenerate) {
    const p = problemOf(c.spec), d = nm.degenerateKernel(p, c.M);
    assert.deepEqual(d.degrees, c.degrees, `${c.spec} M=${c.M} degrees`);
    nearAll(Array.from(d.a), c.a, 1e-12, `${c.spec} M=${c.M} a`);
    for (let i = 0; i < c.M; i++) rel(d.c[i], c.c[i], 1e-9, `${c.spec} M=${c.M} c[${i}]`);
    rel(d.cond, c.cond1, 1e-6, `${c.spec} M=${c.M} cond`);
    c.px.forEach((x, i) => rel(d.at(x), c.y[i], 1e-10, `${c.spec} M=${c.M} y(${x})`));
    const b = nm.degenerateBound(p, d, 1);
    rel(b.normA, c.normA, 1e-6, `${c.spec} M=${c.M} norm A`);
    near(b.normDiff, c.normDiff, 1e-8, `${c.spec} M=${c.M} norm A - A_M`);
  }
});

test("note 'Метод вырожденных ядер': x(e^{xs} - 1), three terms give c, the error table and the bound of the theorem", () => {
  const p = problemOf("degenerate-exp"), ex = exactOf("degenerate-exp");
  const d3 = nm.degenerateKernel(p, 3);
  nearAll(Array.from(d3.c), [0.501019, 0.167126, 0.041805], 5e-7, "c");
  nearAll(Array.from(d3.a), [1 / 4, 1 / 5, 1 / 6, 1 / 10, 1 / 12, 1 / 14, 1 / 36, 1 / 42, 1 / 48], 1e-13, "a = 1/(i! (i+j+2))");
  const errors = [0.185, 0.0427, 8.33e-3, 1.38e-3, 1.96e-4, 2.45e-5], norms = [0.218, 0.0516, 9.95e-3, 1.62e-3, 2.26e-4, 2.79e-5];
  const bounds = [3.4, 0.224, 3.66e-2, 5.77e-3, 8.04e-4, 9.89e-5];
  errors.forEach((e, i) => {
    const d = nm.degenerateKernel(p, i + 1), b = nm.degenerateBound(p, d, 1);
    rel(nm.maxError(d.at, ex, 0, 1), e, 0.01, `M=${i + 1} error`);
    rel(b.normDiff, norms[i], 0.01, `M=${i + 1} ||A - A_M||`);
    rel(b.bound, bounds[i], 0.02, `M=${i + 1} bound q/(1-q)`);
    assert.ok(b.bound >= nm.maxError(d.at, ex, 0, 1), "the bound of the theorem holds");
  });
  near(nm.degenerateBound(p, d3, 1).normA, Math.E - 2, 1e-7, "||A|| = e - 2");
  near(d3.at(1), 1.00833, 5e-6, "y(1)");
});

test("a finite series ends: a kernel of rank two is exact with two terms and `exhausted` says so; a zero kernel is refused", () => {
  const lam = 0.3, p = nm.makeProblem({ lo: -1, hi: 1, kernel: "x+s", f: "x^2", lambda: lam });
  const d = nm.degenerateKernel(p, 5);
  assert.equal(d.n, 2);
  assert.equal(d.exhausted, true);
  const exact = (x) => x * x + (2 * lam * x + 4 * lam * lam / 3) / (3 - 4 * lam * lam);
  near(nm.maxError(d.at, exact, -1, 1), 0, 1e-14, "the note, task 1: y = x^2 + (2 lam x + 4 lam^2/3)/(3 - 4 lam^2)");
  assert.equal(nm.degenerateKernel(p, 2).exhausted, false);
  assert.throws(() => nm.degenerateKernel(nm.makeProblem({ lo: 0, hi: 1, kernel: "0*x*s", f: "1" }), 2), (e) => e.code === "zero-kernel");
  assert.throws(() => nm.degenerateKernel(nm.makeProblem({ lo: 0, hi: 1, kernel: "abs(x)*s", f: "1" }), 2, { center: 0 }), (e) => e.code === "not-analytic");
  assert.doesNotThrow(() => nm.degenerateKernel(nm.makeProblem({ lo: 1, hi: 2, kernel: "abs(x)*s", f: "1" }), 2, { center: 1 }));
});

test("note 'Метод вырожденных ядер', task 4: e^{-x^2 s^2} on [0; 1/2], each term gains a factor of 60 to 130", () => {
  const p = problemOf("degenerate-gauss"), ref = nm.referenceSolution(p);
  const want = [2.7e-2, 4.5e-4, 6.5e-6, 7.6e-8, 7.7e-10, 6.7e-12];
  want.forEach((e, i) => {
    const got = nm.maxError(nm.degenerateKernel(p, i + 1).at, ref.at, 0, 0.5);
    rel(got, e, 0.06, `m = ${i}`);
  });
  const d = nm.degenerateKernel(p, 3);
  assert.deepEqual(d.degrees, [0, 2, 4], "the odd powers of x are absent");
  const [c0, c2, c4] = d.c;
  near(1 + c0, 1.9932, 5e-5, "the answer of task 2: 1,9932 - 0,08254 x^2 + 0,00618 x^4");
  near(c2, -0.08254, 5e-6, "x^2");
  near(c4, 0.00618, 5e-6, "x^4");
});

// ---- projection methods

test("basis families: Legendre and Chebyshev polynomials shifted to [a, b], monomials, and the collocation nodes", () => {
  const P = nm.basisFunctions("legendre", 5, 1, 3), T = nm.basisFunctions("chebyshev", 5, 1, 3), X = nm.basisFunctions("monomial", 4, 1, 3);
  for (const x of [1, 1.3, 2, 2.9, 3]) {
    const t = x - 2;
    near(P[0](x), 1, 1e-15, "P0"); near(P[1](x), t, 1e-15, "P1");
    near(P[2](x), (3 * t * t - 1) / 2, 1e-14, "P2"); near(P[3](x), (5 * t ** 3 - 3 * t) / 2, 1e-14, "P3");
    near(P[4](x), (35 * t ** 4 - 30 * t * t + 3) / 8, 1e-14, "P4");
    near(T[2](x), 2 * t * t - 1, 1e-14, "T2"); near(T[3](x), 4 * t ** 3 - 3 * t, 1e-14, "T3"); near(T[4](x), 8 * t ** 4 - 8 * t * t + 1, 1e-14, "T4");
    near(X[3](x), x ** 3, 1e-14, "monomial");
  }
  nearAll(Array.from(nm.collocationNodes("equidistant", 4, -1, 1)), [-1, -1 / 3, 1 / 3, 1], 1e-15, "equidistant");
  nearAll(Array.from(nm.collocationNodes("chebyshev", 3, 0, 1)), [0.5 - 0.5 * Math.cos(Math.PI / 6), 0.5, 0.5 + 0.5 * Math.cos(Math.PI / 6)], 1e-15, "Chebyshev");
  assert.deepEqual(Array.from(nm.collocationNodes("equidistant", 1, 0, 2)), [1]);
});

const SERIES = (c, p) => nm.galerkinSeries(p, c.Nmax, { phi: nm.basisFunctions(c.phi, c.Nmax, p.lo, p.hi), psi: nm.basisFunctions(c.psi, c.Nmax, p.lo, p.hi), u0: c.u0 });

test("Galerkin-Petrov matches scipy: the matrix, the right-hand side, and every leading block, Bubnov and Petrov, u0 = 0 and u0 = f", () => {
  let blocks = 0;
  for (const c of sk.galerkin) {
    const p = problemOf(c.spec), series = SERIES(c, p);
    for (const n of Object.keys(c.solutions).map(Number)) {
      const want = c.solutions[n], s = series.solution(n);
      for (let j = 0; j < n; j++) rel(s.c[j], want.c[j], Math.max(1e-9, 1e-9 * want.cond1), `${c.spec} ${c.phi}/${c.psi}/${c.u0} n=${n} c[${j}]`);
      rel(s.cond, want.cond1, 1e-5, `${c.spec} ${c.phi}/${c.psi} n=${n} cond`);
      c.px.forEach((x, i) => near(s.at(x) - (c.u0 === "f" ? 0 : 0), want.y[i], 1e-8 * Math.max(1, want.cond1), `${c.spec} ${c.phi}/${c.psi}/${c.u0} n=${n} y`));
      blocks++;
    }
  }
  assert.ok(blocks >= 40, `${blocks} blocks`);
});

test("note 'Метод Галёркина–Петрова': K = xs + x^2, phi = (x, x^2): Petrov with psi = (1, x) and Bubnov, u0 = f, both give 1 + 6 x^2", () => {
  const p = problemOf("galerkin-xs"), ex = exactOf("galerkin-xs");
  const phi = [(x) => x, (x) => x * x];
  const petrov = nm.galerkinSeries(p, 2, { phi, psi: [() => 1, (x) => x], u0: "f" }).solution(2);
  nearAll(Array.from(petrov.matrix), [0, 2 / 9, 2 / 9, 0], 1e-13, "a of the note");
  nearAll(Array.from(petrov.c), [0, 6], 1e-12, "c");
  near(nm.maxError(petrov.at, ex, -1, 1), 0, 1e-12, "the solution is exact");
  const bubnov = nm.galerkinSeries(p, 2, { phi, psi: phi, u0: "f" }).solution(2);
  nearAll(Array.from(bubnov.matrix), [2 / 9, 0, 0, 2 / 15], 1e-13, "Bubnov matrix: 2/9 and 2/15");
  nearAll(Array.from(bubnov.c), [0, 6], 1e-12, "Bubnov c");
  near(Math.abs(petrov.matrix[1] * petrov.matrix[2] - petrov.matrix[0] * petrov.matrix[3]), 4 / 81, 1e-14, "det G = -4/81");
});

test("note 'Метод Галёркина–Петрова', task 7: K = e^{xs} on [-1; 1], Legendre and Chebyshev projections give the same space and the same error", () => {
  const p = problemOf("exp-xs-sym"), ex = exactOf("exp-xs-sym");
  const mk = (psi) => nm.galerkinSeries(p, 12, { phi: nm.basisFunctions("legendre", 12, -1, 1), psi: nm.basisFunctions(psi, 12, -1, 1) });
  const bub = mk("legendre"), pet = mk("chebyshev");
  const want = { 1: 1.5, 2: 0.43, 4: 1.1e-2, 6: 1.1e-4, 8: 5.4e-7, 10: 1.6e-9, 12: 3.3e-12 };
  for (const [n, e] of Object.entries(want)) {
    const eb = nm.maxError(bub.solution(+n).at, ex, -1, 1);
    rel(eb, e, 0.06, `Bubnov n=${n}`);
    near(nm.maxError(pet.solution(+n).at, ex, -1, 1), eb, Math.max(1e-12, 1e-6 * eb), `Petrov n=${n} equals Bubnov in exact arithmetic`);
  }
  assert.ok(bub.solution(12).cond < 30, "the condition number of Legendre stays below 26 + a little");
  assert.ok(pet.solution(12).cond > 0);
});

test("note 'Метод Галёркина–Петрова', task 3: monomials against Legendre on [0, 1] with u0 = f, conditioning decides the end of the table", () => {
  const p = problemOf("exp-xs"), ex = exactOf("exp-xs");
  const mono = nm.galerkinSeries(p, 8, { phi: nm.basisFunctions("monomial", 8, 0, 1), psi: nm.basisFunctions("monomial", 8, 0, 1), u0: "f" });
  const leg = nm.galerkinSeries(p, 8, { phi: nm.basisFunctions("legendre", 8, 0, 1), psi: nm.basisFunctions("legendre", 8, 0, 1), u0: "f" });
  for (const [n, e] of [[2, 9.6e-2], [4, 4.5e-4], [6, 8.4e-7]]) {
    rel(nm.maxError(mono.solution(n).at, ex, 0, 1), e, 0.05, `monomials n=${n}`);
    rel(nm.maxError(leg.solution(n).at, ex, 0, 1), e, 0.05, `Legendre n=${n}`);
  }
  assert.ok(mono.solution(8).cond > 1e8 && leg.solution(8).cond < 10, "monomials: 5e9 in the note, Legendre: 5,1");
});

test("Galerkin-Petrov with u0 = f and lambda not 1: K = xs, lambda = 1/2, f = 5x/6, the solution x is f + c x", () => {
  const p = problemOf("xs"), ex = exactOf("xs");
  for (const kind of ["monomial", "legendre"]) {
    const phi = nm.basisFunctions(kind, 2, 0, 1), s = nm.galerkinSeries(p, 2, { phi, psi: phi, u0: "f" }).solution(2);
    near(nm.maxError(s.at, ex, 0, 1), 0, 1e-13, `Bubnov, ${kind}`);
    const zero = nm.galerkinSeries(p, 2, { phi, psi: phi, u0: "zero" }).solution(2);
    near(nm.maxError(zero.at, ex, 0, 1), 0, 1e-13, `u0 = 0 gives the same space, ${kind}`);
  }
});

test("Galerkin-Petrov reports a singular matrix of the note and a non-finite kernel", () => {
  const p = problemOf("galerkin-xs");
  const odd = nm.galerkinSeries(p, 3, { phi: [(x) => x, (x) => x ** 2, (x) => x ** 3], psi: [() => 1, (x) => x, (x) => x ** 2], u0: "f" });
  assert.ok(singularOrIllConditioned(() => odd.solution(3)), "n = 3 with x^j and x^(i-1): det G = 0 in the note");
  assert.throws(() => nm.galerkinSeries(nm.makeProblem({ lo: 0, hi: 1, kernel: "1/(x-s)", f: "1" }), 2, { phi: nm.basisFunctions("legendre", 2, 0, 1), psi: nm.basisFunctions("legendre", 2, 0, 1) }),
    (e) => e instanceof nk.EvalError || e instanceof nm.ProblemError);
});

test("collocation matches scipy: the matrix, the coefficients, the solution and the condition number; singular cases are named", () => {
  let solved = 0, singular = 0;
  for (const c of sk.collocation) {
    const p = problemOf(c.spec), phi = nm.basisFunctions(c.phi, c.n, p.lo, p.hi), nodes = nm.collocationNodes(c.nodes, c.n, p.lo, p.hi);
    if (c.singular) {
      assert.ok(singularOrIllConditioned(() => nm.collocation(p, phi, nodes)), `${c.spec} ${c.phi} ${c.nodes} ${c.n}`);
      singular++;
      continue;
    }
    const s = nm.collocation(p, phi, nodes);
    nearAll(Array.from(s.matrix), c.matrix, 1e-11 * Math.max(1, c.cond1), `${c.spec} ${c.phi} ${c.nodes} ${c.n} matrix`);
    rel(s.cond, c.cond1, 1e-5, `${c.spec} ${c.phi} ${c.nodes} ${c.n} cond`);
    c.px.forEach((x, i) => near(s.at(x), c.y[i], 1e-8 * Math.max(1, c.cond1) * Math.max(1, Math.abs(c.y[i])), `${c.spec} ${c.phi} ${c.nodes} ${c.n} y`));
    solved++;
  }
  assert.ok(solved >= 40 && singular >= 5, `${solved} solved, ${singular} singular`);
});

test("note 'Метод коллокации': K = xs + x^2 with four Legendre functions on equidistant nodes gives c = (3, 0, 4, 0); task 1 table; task 3", () => {
  const p = problemOf("galerkin-xs"), ex = exactOf("galerkin-xs");
  const s = nm.collocation(p, nm.basisFunctions("legendre", 4, -1, 1), nm.collocationNodes("equidistant", 4, -1, 1));
  nearAll(Array.from(s.c), [3, 0, 4, 0], 1e-12, "c");
  const tr = Float64Array.from({ length: 16 }, (_, k) => s.matrix[(k % 4) * 4 + Math.floor(k / 4)]);
  near(nk.cond1(tr, 4), 19, 0.5, "cond_inf M = 19 of the note is cond_1 of the transpose");
  near(nm.maxError(s.at, ex, -1, 1) / 7, 0, 5e-14, "relative error at rounding level, 2,5e-14 in the note");
  const q = problemOf("collocation-sin"), e = exactOf("collocation-sin");
  const table = [[4, 2.4e-3, 39], [8, 7.3e-7, 1.0e2], [12, 5.3e-11, 7.3e2]];
  for (const [d, err, cond] of table) {
    const c = nm.collocation(q, nm.basisFunctions("legendre", d + 1, 0, Math.PI), nm.collocationNodes("equidistant", d + 1, 0, Math.PI));
    rel(nm.maxError(c.at, e, 0, Math.PI) / Math.exp(Math.PI), err, 0.1, `d=${d} relative error`);
    const tm = Float64Array.from({ length: (d + 1) ** 2 }, (_, k) => c.matrix[(k % (d + 1)) * (d + 1) + Math.floor(k / (d + 1))]);
    rel(nk.cond1(tm, d + 1), cond, 0.1, `d=${d} cond_inf`);
  }
  const t3 = problemOf("collocation-x2s2"), e3 = exactOf("collocation-x2s2");
  for (const kind of ["legendre", "chebyshev", "monomial"]) {
    const c = nm.collocation(t3, nm.basisFunctions(kind, 3, 0, 1), nm.collocationNodes("equidistant", 3, 0, 1));
    near(nm.maxError(c.at, e3, 0, 1), 0, 1e-12, `${kind}: x + 5x^2 is in the space`);
  }
  assert.ok(singularOrIllConditioned(() => nm.collocation(t3, nm.basisFunctions("monomial", 2, 0, 1), nm.collocationNodes("equidistant", 2, 0, 1))), "task 3, n = 1: the second column is zero");
});

test("Chebyshev nodes beat equidistant nodes for the Runge kernel s/(1 + 25 x^2), and equidistant ones get worse as N grows", () => {
  const p = nm.makeProblem({ lo: -1, hi: 1, kernel: "s/(1+25*x^2)", f: "1/(1+25*x^2)", lambda: 0.5 });
  const ref = nm.referenceSolution(p);
  const err = (kind, n) => nm.maxError(nm.collocation(p, nm.basisFunctions("legendre", n, -1, 1), nm.collocationNodes(kind, n, -1, 1)).at, ref.at, -1, 1);
  assert.ok(err("chebyshev", 20) < 0.2 * err("equidistant", 20), `Chebyshev ${err("chebyshev", 20)} vs equidistant ${err("equidistant", 20)}`);
  assert.ok(err("equidistant", 28) > 2 * err("equidistant", 14), "Runge effect: the equidistant error grows");
});

// ---- the reference solution and the error measures

test("the Nystrom reference agrees with the exact solutions of the notes to rounding level and its error estimate is honest", () => {
  for (const name of ["periodic", "xs", "exp-xs", "degenerate-exp", "galerkin-xs", "collocation-sin", "collocation-x2s2", "exp-xs-sym"]) {
    const p = problemOf(name, { exact: "" }), ref = nm.referenceSolution(p), ex = exactOf(name);
    assert.equal(ref.exact, false);
    const inner = Array.from({ length: 101 }, (_, i) => p.lo + (p.hi - p.lo) * (i + 0.5) / 101);
    const trueErr = nm.maxError(ref.at, ex, p.lo, p.hi, 0, inner);
    assert.ok(trueErr < 1e-12, `${name}: ${trueErr}`);
    assert.ok(trueErr <= 10 * ref.err + 1e-13, `${name}: the estimate ${ref.err} must cover ${trueErr}`);
  }
  const given = nm.referenceSolution(problemOf("xs"));
  assert.equal(given.exact, true);
  assert.equal(given.err, 0);
});

test("the Volterra reference (trapezoid with a Richardson step) agrees with the exact solutions, linear and nonlinear", () => {
  for (const name of ["volterra-exp", "volterra-sin", "volterra-nl", "volterra-nl2"]) {
    const p = problemOf(name, { exact: "" }), ref = nm.referenceSolution(p), ex = exactOf(name);
    const trueErr = nm.maxError(ref.at, ex, p.lo, p.hi, 301);
    assert.ok(trueErr < 5e-9, `${name}: ${trueErr}`);
    assert.ok(ref.err > 0 && ref.err >= trueErr, `${name}: the Richardson correction ${ref.err} bounds the remaining error ${trueErr}`);
  }
});

test("maxError and nodeError measure the largest deviation on a grid and at the nodes", () => {
  assert.equal(nm.maxError((x) => x, (x) => 2 * x, 0, 1, 11), 1);
  assert.equal(nm.maxError((x) => x, (x) => x, 0, 1, 11), 0);
  near(nm.maxError((x) => x, () => 0, 0, 1, 0, [0.2, 0.9, 0.5]), 0.9, 1e-15, "given points");
  assert.equal(nm.nodeError({ n: 3, nodes: [0, 1, 2], y: [0, 1.5, 2] }, (x) => x), 0.5);
});

test("the nonlinear code path with a kernel linear in y agrees with the linear path, also with lambda not 1", () => {
  const lin = nm.makeProblem({ kind: "volterra", lo: 0, hi: 1, kernel: "exp(-(x-s))", f: "exp(-x)", lambda: 0.7 });
  const non = nm.makeProblem({ kind: "volterra-nonlinear", lo: 0, hi: 1, kernel: "exp(-(x-s))*y", f: "exp(-x)", lambda: 0.7 });
  for (const rule of ["trapezoid", "simpson"]) {
    const a = nm.quadratureVolterra(lin, 12, rule), b = nm.quadratureVolterra(non, 12, rule);
    nearAll(Array.from(b.y), Array.from(a.y), 1e-11, rule);
  }
  const itL = nm.simpleIteration(lin, 12, { tol: 1e-12 }), itN = nm.simpleIteration(non, 12, { tol: 1e-12 });
  nearAll(Array.from(itN.y), Array.from(itL.y), 1e-11, "simple iteration");
  assert.equal(itN.iterations, itL.iterations);
});

test("an exactly singular Fredholm system (K = 1, lambda = 1, two trapezoid nodes) is reported as such", () => {
  const p = nm.makeProblem({ lo: 0, hi: 1, kernel: "1", f: "1", lambda: 1 });
  assert.throws(() => nm.quadratureFredholm(p, 2), (e) => sing(e) && /[А-Яа-я]/.test(e.message));
});

test("a nonlinear step solves its quadratic with the small root, the one that stays finite as h goes to zero", () => {
  const p = nm.makeProblem({ kind: "volterra-nonlinear", lo: 0, hi: 0.2, kernel: "y^2", f: "1" });
  const sol = nm.quadratureVolterra(p, 3);
  const a = 0.05;
  const small = (1 - Math.sqrt(1 - 4 * a * (1 + a))) / (2 * a);
  near(sol.y[1], small, 1e-13, "y_1 = (1 - sqrt(1 - 2h c))/h with the trapezoid weight h/2");
  assert.ok(sol.y[1] < 2, "and not the other root, about 2/h");
});

// ================================================================ spectral problems

const sp = fx.spectral;
const kernelOf = (name, over = {}) => { const s = { ...sp.specs[name], ...over }; return nm.makeKernel({ lo: s.lo, hi: s.hi, kernel: s.kernel }); };
const KINKED = ["min", "green", "robin"];

test("makeKernel names the field of a bad input; symmetryDefect is zero for a symmetric kernel and large for x", () => {
  assert.throws(() => nm.makeKernel({ lo: 1, hi: 1, kernel: "x*s" }), (e) => e.code === "bad-interval" && e.field === "interval");
  assert.throws(() => nm.makeKernel({ lo: 0, hi: 1, kernel: "x*" }), (e) => e instanceof nk.ExprError && e.field === "kernel");
  assert.throws(() => nm.makeKernel({ lo: 0, hi: 1, kernel: "x*y" }), (e) => e.code === "bad-variable" && e.field === "kernel");
  for (const name of Object.keys(sp.specs)) assert.equal(nm.symmetryDefect(kernelOf(name)), 0, name);
  assert.ok(nm.symmetryDefect(nm.makeKernel({ lo: 0, hi: 1, kernel: "x" })) > 0.5);
  assert.ok(nm.symmetryDefect(nm.makeKernel({ lo: 0, hi: 1, kernel: "s-x" })) > 0.5, "an antisymmetric kernel is not symmetric");
  assert.throws(() => nm.symmetryDefect(nm.makeKernel({ lo: 0, hi: 1, kernel: "1/(x-s)" })), (e) => e.code === "bad-value");
});

test("characteristic numbers: exact values of the notes, scipy roots, numpy Nystrom for the smooth Gaussian kernel; the error estimate covers the true error", () => {
  for (const name of Object.keys(sp.specs)) {
    const c = nm.characteristicNumbers(kernelOf(name), 6), want = sp.lambda[name];
    assert.equal(c.lambda.length, Math.min(6, want.length), `${name}: how many numbers`);
    c.lambda.forEach((l, j) => {
      rel(l, want[j], name === "gauss" ? 1e-9 : KINKED.includes(name) ? 1e-7 : 1e-8, `${name} lambda_${j + 1}`);
      assert.ok(Math.abs(l - want[j]) <= 10 * c.err[j] + 1e-12 * Math.abs(l), `${name} lambda_${j + 1}: the estimate ${c.err[j]} covers ${Math.abs(l - want[j])}`);
      near(c.mu[j], 1 / l, 1e-14 * Math.abs(c.mu[j]), "mu = 1/lambda");
    });
  }
  const robin = nm.characteristicNumbers(kernelOf("robin"), 1).lambda[0];
  near(robin, 4.11586, 5e-6, "note 'Метод Келлога', task 350: nu^2 with tan nu = -nu");
});

test("the eigenfunctions are unit, orthogonal and match sqrt(2) sin(pi x / 2), sqrt(2) sin(pi x) and sin(x)/sqrt(pi)", () => {
  for (const name of ["min", "green", "sin"]) {
    const c = nm.characteristicNumbers(kernelOf(name), 2), y = c.eigenfunction(0), w = sp.eigenfunction1[name];
    w.x.forEach((x, i) => near(y(x), w.y[i], 1e-4, `${name} y_1(${x})`));
  }
  const k = kernelOf("green"), c = nm.characteristicNumbers(k, 3), g = nm.compositeGauss(0, 1, 8, 16);
  const ip = (f, h) => g.x.reduce((s, x, i) => s + g.w[i] * f(x) * h(x), 0);
  const y1 = c.eigenfunction(0), y2 = c.eigenfunction(1), y3 = c.eigenfunction(2);
  near(ip(y1, y1), 1, 5e-4, "unit"); near(ip(y2, y2), 1, 5e-4, "unit");
  near(ip(y1, y2), 0, 5e-4, "y1 and y2 orthogonal"); near(ip(y1, y3), 0, 5e-4, "y1 and y3");
  near(y2(0.25), Math.sqrt(2) * Math.sin(2 * Math.PI * 0.25), 3e-4, "y_2 = sqrt(2) sin(2 pi x)");
  assert.ok(ip(y1, (x) => Math.sin(Math.PI * x)) > 0, "the sign is fixed by the largest value");
});

// ---- Kellogg

test("Kellogg's ratios and roots agree with the exact sympy iteration for min, the Green function and the Robin kernel, omega = 1 and omega = x", () => {
  for (const c of sp.kellogg) {
    const om = c.omega === "1" ? () => 1 : (x) => x, r = nm.kellogg(kernelOf(c.spec), om, 5);
    r.ratios.forEach((v, i) => rel(v, c.ratios[i], 4e-5, `${c.spec} omega=${c.omega} r_${i + 1}`));
    r.roots.forEach((v, i) => rel(v, c.roots[i], 4e-5, `${c.spec} omega=${c.omega} root_${i + 1}`));
    for (let i = 1; i < 5; i++) assert.ok(r.ratios[i] <= r.ratios[i - 1] + 1e-12, `${c.spec} omega=${c.omega}: the ratio does not increase`);
    const lam1 = sp.lambda[c.spec][0];
    assert.ok(r.ratios.every((v) => v >= lam1 * (1 - 5e-5)) && r.roots.every((v) => v >= lam1 * (1 - 5e-5)), "from above, up to the error of the quadrature");
  }
});

test("note 'Метод Келлога': the table of K = min(x, s), the one-step answers of the rank-one kernels and the rate q^2 = 1/81", () => {
  const k = kernelOf("min"), one = nm.kellogg(k, () => 1, 4), x = nm.kellogg(k, (t) => t, 4);
  nearAll(one.ratios, [2.7386, 2.4692, 2.4674, 2.4674], 6e-5, "omega = 1");
  nearAll(one.roots, [2.7386, 2.6004, 2.5553, 2.5330], 6e-5, "root, omega = 1");
  nearAll(x.ratios, [2.4853, 2.4676, 2.4674, 2.4674], 1e-4, "omega = x");
  rel(one.ratios[0] ** 2, 7.5, 2e-5, "r_1^2 = 15/2"); rel(x.ratios[0] ** 2, 105 / 17, 2e-5, "r_1^2 = 105/17");
  const long = nm.kellogg(k, () => 1, 3), lam = Math.PI ** 2 / 4;
  const e = long.ratios.map((v) => v - lam);
  assert.ok(e[1] / e[0] < 0.05 && e[1] / e[0] > 0.005, `an error falls by about q^2 = 1/81 per step: ${e[1] / e[0]}`);
  for (const [name, om, want] of [["xs", (t) => t, 3], ["x2s2", (t) => t * t, 5], ["sin", Math.sin, 1 / Math.PI]]) {
    const r = nm.kellogg(kernelOf(name), om, 3);
    r.ratios.forEach((v, i) => rel(v, want, 1e-9, `${name} r_${i + 1}: omega is an eigenfunction`));
  }
  const big = nm.kellogg(k, () => 1, 400);
  assert.ok(big.ratios.every(Number.isFinite) && big.roots.every(Number.isFinite), "no overflow in 400 steps");
  rel(big.ratios[399], lam, 1e-4, "converged");
  assert.equal(big.vectors.length, 401);
  assert.throws(() => nm.kellogg(k, () => 0, 3), (e2) => e2.code === "zero-omega" && /[А-Яа-я]/.test(e2.message));
  assert.throws(() => nm.kellogg(kernelOf("xs"), (t) => 3 * t - 2, 3), (e2) => e2.code === "zero-omega", "omega in the kernel of the operator");
  assert.throws(() => nm.kellogg(k, () => NaN, 3), (e2) => e2.code === "bad-value");
});

// ---- traces

test("traces: A_2m of the notes and exact sums of lambda^-2m, the bounds of formula (4) and their limit", () => {
  for (const name of ["min", "green", "xs", "x2s2", "gauss"]) {
    const t = nm.traces(kernelOf(name), 5), want = sp.traces[name];
    t.a.forEach((a, i) => rel(a, want[i], KINKED.includes(name) ? 5e-5 : 1e-9, `${name} A_${2 * (i + 1)}`));
  }
  const m = nm.traces(kernelOf("min"), 4);
  [1 / 6, 17 / 630, 691 / 155925, 929569 / 1277025750].forEach((v, i) => rel(m.a[i], v, 5e-5, `A_${2 * i + 2} of the note`));
  nearAll(m.lower.slice(0, 3), [2.4495, 2.4673, 2.4674], 6e-5, "lower bounds");
  nearAll(m.upper.slice(0, 3), [2.4853, 2.4676, 2.4674], 6e-5, "upper bounds");
  const lam1 = Math.PI ** 2 / 4;
  m.lower.forEach((l, i) => assert.ok(l <= lam1 * (1 + 5e-5) && m.upper[i] >= lam1 * (1 - 5e-5), `bounds hold at m = ${i + 1}, up to the error of the quadrature`));
  for (let i = 1; i < 4; i++) assert.ok(m.upper[i] <= m.upper[i - 1] + 1e-9 && m.lower[i] >= m.lower[i - 1] - 1e-9, "upper does not increase, lower does not decrease");
  const x = nm.traces(kernelOf("xs"), 3);
  nearAll(x.lower, [3, 3, 3], 1e-9, "task 343: both bounds are 3"); nearAll(x.upper, [3, 3, 3], 1e-9, "upper");
  const r = nm.traces(kernelOf("robin"), 3);
  [11 / 180, 113 / 32400].forEach((v, i) => rel(r.a[i], v, 5e-5, `task 345: A_${2 * i + 2}`));
  nearAll([r.lower[0], r.upper[0], r.lower[1], r.upper[1], r.lower[2], r.upper[2]], [4.0452, 4.1859, 4.1150, 4.1176, 4.1158, 4.1159], 1e-4, "task 345 bounds");
});

// ---- Ritz

const phiOf = (kind, n, k) => nm.basisFunctions(kind, n, k.lo, k.hi);

test("Ritz's method matches scipy: G, M and every lambda^(n) for Legendre, Chebyshev and monomial bases", () => {
  let checked = 0;
  for (const c of sp.ritz) {
    const k = kernelOf(c.spec), series = nm.ritzSeries(k, c.Nmax, phiOf(c.basis, c.Nmax, k));
    for (let n = 1; n <= c.Nmax; n++) {
      const got = series.solution(n).lambda, want = c.lambda[n];
      assert.equal(got.length, want.length, `${c.spec} ${c.basis} n=${n}: how many`);
      got.forEach((l, j) => { rel(l, want[j], 1e-7 * (c.basis === "monomial" ? 1e3 : 1), `${c.spec} ${c.basis} n=${n} lambda_${j + 1}`); checked++; });
    }
  }
  assert.ok(checked >= 60, `${checked} numbers compared`);
});

test("note 'Метод Ритца': the Green function table by n, upper bounds that fall as n grows, exact results for degenerate kernels", () => {
  const k = kernelOf("green"), series = nm.ritzSeries(k, 6, phiOf("legendre", 6, k));
  const table = { 1: [12], 2: [12, 60], 3: [9.8751, 60, 170.125], 4: [9.8751, 39.7649, 170.125], 5: [9.869607, 39.7649, 91.2255], 6: [9.869607, 39.47974, 91.2255] };
  for (const [n, want] of Object.entries(table)) series.solution(+n).lambda.slice(0, want.length).forEach((l, j) => rel(l, want[j], 2e-6, `n=${n} lambda_${j + 1}`));
  const exact = [Math.PI ** 2, 4 * Math.PI ** 2, 9 * Math.PI ** 2];
  for (let n = 1; n <= 6; n++) series.solution(n).lambda.slice(0, 3).forEach((l, j) => assert.ok(l >= exact[j] - 1e-6, `n=${n}: lambda_${j + 1} from above`));
  for (let n = 2; n <= 6; n++) { const a = series.solution(n - 1).lambda, b = series.solution(n).lambda; a.forEach((l, j) => assert.ok(b[j] <= l + 1e-9, `lambda_${j + 1} does not grow from n=${n - 1} to ${n}`)); }
  const r3 = nm.ritzSeries(kernelOf("rank3"), 3, phiOf("legendre", 3, kernelOf("rank3"))), l3 = r3.solution(3).lambda;
  nearAll(l3, [(27 - 3 * Math.sqrt(61)) / 8, 1.5, (27 + 3 * Math.sqrt(61)) / 8], 1e-12, "1 + xs + x^2 s^2: exact at n = 3");
  rel(r3.solution(1).lambda[0], 0.45, 1e-12, "n = 1: 0,45, above 0,44616");
  const x2 = nm.ritzSeries(kernelOf("x2s2"), 3, phiOf("legendre", 3, kernelOf("x2s2")));
  nearAll([1, 2, 3].map((n) => x2.solution(n).lambda[0]), [9, 36 / 7, 5], 1e-12, "task 1: 9, 36/7, 5");
  const neg = nm.ritzSeries(nm.makeKernel({ lo: 0, hi: 1, kernel: "-x*s" }), 2, phiOf("legendre", 2, kernelOf("xs")));
  rel(neg.solution(2).lambda[0], -3, 1e-12, "a negative kernel: lambda = -3");
});

test("Ritz eigenfunctions are unit in L2 and close to the exact ones; a dependent basis is refused", () => {
  const k = kernelOf("green"), s = nm.ritzSeries(k, 6, phiOf("legendre", 6, k)).solution(6), y = s.eigenfunction(0);
  const g = nm.compositeGauss(0, 1, 4, 16), ip = (f, h) => g.x.reduce((t, x, i) => t + g.w[i] * f(x) * h(x), 0);
  near(ip(y, y), 1, 1e-9, "unit");
  const ex = (x) => Math.SQRT2 * Math.sin(Math.PI * x), sgn = Math.sign(ip(y, ex));
  near(Math.abs(ip(y, ex)), 1, 1e-5, "the angle with the exact y_1");
  near(sgn * y(0.3), ex(0.3), 1e-3, "pointwise");
  const bad = nm.ritzSeries(k, 2, [() => 1, () => 1]);
  assert.throws(() => bad.solution(2), (e) => e.code === "dependent" && /[А-Яа-я]/.test(e.message));
  assert.deepEqual(nm.cholesky(Float64Array.of(1, 2, 2, 1), 2), null, "an indefinite matrix has no Cholesky factor");
  nearAll(Array.from(nm.cholesky(Float64Array.of(4, 2, 2, 5), 2)), [2, 0, 1, 2], 1e-15, "Cholesky of [[4,2],[2,5]]");
});

test("Ritz with a non-orthogonal basis (monomials): the eigenfunction is unit in L2, the Gram matrix is not diagonal", () => {
  const k = kernelOf("rank3"), s = nm.ritzSeries(k, 3, phiOf("monomial", 3, k)).solution(3);
  const g = nm.compositeGauss(-1, 1, 4, 16), ip = (f, h) => g.x.reduce((t, x, i) => t + g.w[i] * f(x) * h(x), 0);
  for (let i = 0; i < 3; i++) { const y = s.eigenfunction(i); near(ip(y, y), 1, 1e-10, `y_${i + 1} is unit`); }
  near(ip(s.eigenfunction(0), s.eigenfunction(1)), 0, 1e-10, "y_1 and y_2 are orthogonal");
  const exactY1 = (x) => x * x + (6 + Math.sqrt(61)) / 5;
  const c = ip(s.eigenfunction(0), exactY1) / Math.sqrt(ip(exactY1, exactY1));
  near(Math.abs(c), 1, 1e-10, "the note: y_1 = x^2 + (6 + sqrt 61)/5, up to the sign");
});

test("Ritz entries are integrated until they settle: an oscillating kernel cos(150(x - s)) on one function gives its exact sigma", () => {
  const k = nm.makeKernel({ lo: 0, hi: 1, kernel: "cos(150*(x-s))" });
  const sigma = (Math.sin(150) / 150) ** 2 + ((1 - Math.cos(150)) / 150) ** 2;
  rel(nm.ritzSeries(k, 1, [() => 1]).solution(1).lambda[0], 1 / sigma, 1e-11, "lambda = 1/sigma, sigma = (K 1, 1)");
});

test("a kink on the diagonal near an end of the interval is not missed: the one-function Ritz number of the Green function is 12", () => {
  const k = kernelOf("green");
  near(nm.ritzSeries(k, 1, [() => 1]).solution(1).lambda[0], 12, 1e-9, "(K 1, 1) = 1/12");
});

// ---- Jacobi rotations

test("Jacobi rotations reach the eigenvalues of numpy on every matrix, and every step does what the note proves", () => {
  for (const c of sp.jacobi) {
    const A = Float64Array.from(c.A), r = nm.jacobiRotations(A, c.n);
    nearAll(Array.from(r.diagonal).sort((a, b) => a - b), c.eigenvalues, 1e-10, `${c.name} eigenvalues`);
    near(r.rho, c.n > 1 ? 1 - 2 / (c.n * (c.n - 1)) : 0, 1e-15, "rho");
    let prev = r.S0, a = A;
    r.steps.forEach((s, i) => {
      near(s.A[s.k * c.n + s.l], 0, 1e-12 * Math.max(1, Math.abs(s.akl)), `${c.name} step ${i + 1}: the chosen element is zeroed`);
      near(s.S, prev - 2 * s.akl ** 2, 1e-11 * Math.max(1, prev), `${c.name} step ${i + 1}: S drops by 2 a_kl^2`);
      assert.ok(s.S <= r.rho ** s.p * r.S0 + 1e-12, `${c.name} step ${i + 1}: the lemma of the note`);
      let big = 0;
      for (let u = 0; u < c.n; u++) for (let v = u + 1; v < c.n; v++) big = Math.max(big, Math.abs(a[u * c.n + v]));
      near(Math.abs(s.akl), big, 1e-15, `${c.name} step ${i + 1}: the largest off-diagonal element is chosen`);
      for (let u = 0; u < c.n; u++) for (let v = 0; v < u; v++) assert.equal(s.A[u * c.n + v], s.A[v * c.n + u], "symmetric");
      prev = s.S; a = s.A;
    });
    const TtAT = new Float64Array(c.n * c.n);
    for (let i = 0; i < c.n; i++) for (let j = 0; j < c.n; j++) { let t = 0; for (let u = 0; u < c.n; u++) for (let v = 0; v < c.n; v++) t += r.T[u * c.n + i] * A[u * c.n + v] * r.T[v * c.n + j]; TtAT[i * c.n + j] = t; }
    nearAll(Array.from(TtAT), Array.from(r.final), 1e-11, `${c.name}: A_p = T^T A T`);
    for (let k = 0; k < c.n; k++) {
      let res = 0;
      for (let i = 0; i < c.n; i++) { let t = -r.diagonal[k] * r.T[i * c.n + k]; for (let j = 0; j < c.n; j++) t += A[i * c.n + j] * r.T[j * c.n + k]; res += t * t; }
      assert.ok(Math.sqrt(res) <= Math.sqrt(offDiag(r.final, c.n)) + 1e-12, `${c.name}: the residual of column ${k} is below sqrt(S)`);
    }
  }
});
const offDiag = (A, n) => nm.offDiagonalSum(A, n);

test("note 'Метод вращений Якоби': the 4x4 example, pairs and S_p of the table, one rotation for 2x2, the angle phi = pi/4", () => {
  const B = Float64Array.from(sp.jacobi.find((c) => c.name === "note-4x4").A), r = nm.jacobiRotations(B, 4);
  near(r.S0, 14, 1e-13, "S_0"); near(r.rho, 5 / 6, 1e-15, "rho = 5/6");
  assert.deepEqual(r.steps.slice(0, 6).map((s) => [s.k + 1, s.l + 1]), [[1, 3], [2, 4], [1, 2], [3, 4], [1, 4], [2, 3]]);
  nearAll(r.steps.slice(0, 6).map((s) => s.S), [6, 4, 2.241, 0.4815, 0.2549, 0.02838], [1e-3, 1e-3, 1e-3, 1e-4, 1e-4, 1e-5].reduce((a, b) => Math.max(a, b)), "S_1..S_6 of the table");
  near(r.steps[0].phi, 0.9079, 5e-5, "the first angle, tan 2phi = -4");
  near(r.steps[11].S, 8.3e-10, 5e-11, "S_12");
  near(r.steps[0].S, 6, 1e-12, "S_1 = 14 - 2*4");
  nearAll(Array.from(r.steps[11].A.filter((_, i) => i % 5 === 0)).sort((a, b) => a - b), [0.812163, 2.783823, 3.548378, 6.855635], 1e-6, "the diagonal after 12 rotations");
  assert.equal(nm.jacobiStepsBound(4, 14, 1e-3), 116, "6 ln(16·14/10^-6) = 115,4: the note writes about 115, the bound needs 116");
  const two = nm.jacobiRotations(Float64Array.of(2, -1, -1, 5), 2);
  assert.equal(two.steps.length, 1, "n = 2: rho = 0, one rotation");
  near(two.steps[0].S, 0, 1e-14, "and S = 0 after it");
  near(two.rho, 0, 1e-16, "rho = 0 for n = 2");
  const eq = nm.jacobiRotations(Float64Array.of(1, 2, 0, 2, 1, 0, 0, 0, 3), 3);
  near(eq.steps[0].phi, Math.PI / 4, 1e-15, "a_kk = a_ll: phi = pi/4");
  nearAll(Array.from(eq.diagonal).sort((a, b) => a - b), [-1, 3, 3], 1e-12, "eigenvalues of [[1,2],[2,1]] and 3");
  const neg = nm.jacobiRotations(Float64Array.of(1, -2, 0, -2, 1, 0, 0, 0, 3), 3);
  near(neg.steps[0].phi, -Math.PI / 4, 1e-15, "the sign follows a_kl");
  assert.equal(nm.jacobiRotations(Float64Array.of(3, 0, 0, 0, 1, 0, 0, 0, 2), 3).steps.length, 0, "a diagonal matrix needs no rotation");
});
