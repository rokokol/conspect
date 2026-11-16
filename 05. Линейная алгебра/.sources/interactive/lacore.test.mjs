// lacore.js against the python reference in fixtures.json (export_fixtures.py).
// The parser, quadrature, LU and eigenvalue tests are numkit's (numkit.test.mjs).
// Run: node --test lacore.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as nk from "../../../Scripts/numkit/numkit.js";
import { dot, matchAll, mulVec, near, nearAll, rel } from "../../../Scripts/numkit/testkit.mjs";
import * as la from "./lacore.js";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));

const scale = (c) => Math.max(c.rho[0], 1e-300);
const each = (fn) => { for (const c of fx.matrices) fn(c, Float64Array.from(c.a), la.svd(Float64Array.from(c.a), c.m, c.n)); };

test("singular values match scipy gesvd on every matrix", () => {
  each((c, a, s) => {
    assert.equal(s.rho.length, Math.min(c.m, c.n), c.name);
    nearAll(Array.from(s.rho), c.rho, 1e-12 * scale(c), c.name);
  });
});

test("singular values come out in descending order and are non-negative", () => {
  each((c, a, s) => {
    for (let j = 0; j < s.rho.length; j++) assert.ok(s.rho[j] >= 0, `${c.name}: rho ${j} negative`);
    for (let j = 1; j < s.rho.length; j++) assert.ok(s.rho[j - 1] >= s.rho[j], `${c.name}: order at ${j}`);
  });
});

test("rank equals numpy matrix_rank, including the zero and the deficient matrices", () => {
  each((c, a, s) => assert.equal(s.rank, c.rank, c.name));
});

test("beyond the rank the singular numbers are exactly zero, as in the note", () => {
  each((c, a, s) => {
    for (let k = s.rank; k < s.rho.length; k++) assert.equal(s.rho[k], 0, `${c.name}: rho ${k}`);
    for (let k = 0; k < s.rank; k++) assert.ok(s.rho[k] > 0, `${c.name}: rho ${k}`);
  });
});

test("both bases are orthonormal, even where the singular number is zero", () => {
  each((c, a, s) => {
    for (let i = 0; i < s.rho.length; i++) {
      for (let j = 0; j <= i; j++) {
        const want = i === j ? 1 : 0;
        near(dot(s.q[i], s.q[j]), want, 1e-12, `${c.name}: (q${i},q${j})`);
        near(dot(s.e[i], s.e[j]), want, 1e-12, `${c.name}: (e${i},e${j})`);
      }
    }
    for (const v of s.q) assert.equal(v.length, c.m);
    for (const v of s.e) assert.equal(v.length, c.n);
  });
});

test("the definition: A e^k = rho_k q^k for k <= r and A e^k = 0 beyond", () => {
  each((c, a, s) => {
    for (let k = 0; k < s.rho.length; k++) {
      const got = mulVec(a, c.m, c.n, s.e[k]);
      const want = k < s.rank ? Array.from(s.q[k], (x) => s.rho[k] * x) : new Array(c.m).fill(0);
      nearAll(got, want, 1e-11 * scale(c), `${c.name}: k=${k}`);
    }
  });
});

test("A = V Sigma W*: the sum of all rank-one terms restores the matrix", () => {
  each((c, a, s) => {
    const full = la.lowRank(s, s.rho.length);
    nearAll(Array.from(full), c.a, 1e-12 * scale(c), c.name);
  });
});

test("rank-k approximation equals the truncated sum of scipy where it is unique", () => {
  each((c, a, s) => {
    for (const ap of c.approx) nearAll(Array.from(la.lowRank(s, ap.k)), ap.x, 1e-11 * scale(c), `${c.name} k=${ap.k}`);
  });
});

test("the spectral error of the approximation is rho_{k+1} and equals numpy's 2-norm", () => {
  each((c, a, s) => {
    for (const ap of c.approx) {
      const want = ap.k < s.rho.length ? s.rho[ap.k] : 0;
      near(la.spectralError(s, ap.k), want, 0, `${c.name} k=${ap.k} definition`);
      near(want, ap.spectral, 1e-12 * scale(c), `${c.name} k=${ap.k} vs numpy`);
    }
  });
});

test("max |a_ij - x_ij| matches the reference and never exceeds rho_{k+1}", () => {
  each((c, a, s) => {
    for (const ap of c.approx) {
      const got = la.maxAbsDiff(a, la.lowRank(s, ap.k));
      near(got, ap.maxdiff, 1e-11 * scale(c), `${c.name} k=${ap.k}`);
      assert.ok(got <= la.spectralError(s, ap.k) + 1e-11 * scale(c), `${c.name} k=${ap.k}: bound broken`);
    }
  });
});

test("Eckart-Young: no random matrix of rank k beats rho_{k+1}", () => {
  let tried = 0;
  each((c, a, s) => {
    for (const ap of c.approx) {
      for (const y of ap.competitors) {
        assert.ok(y >= la.spectralError(s, ap.k) - 1e-11 * scale(c), `${c.name} k=${ap.k}: ${y} < rho`);
        tried++;
      }
    }
  });
  assert.ok(tried > 100, `only ${tried} competitors tried`);
});

test("signs: a negative 1x1 matrix has rho 3 and A e = rho q", () => {
  const s = la.svd(Float64Array.of(-3), 1, 1);
  assert.equal(s.rho[0], 3);
  assert.equal(-3 * s.e[0][0], 3 * s.q[0][0]);
});

test("the note's example 3x2 has rho = sqrt(3), 1 and the rank-one term of the note", () => {
  const s = la.svd(Float64Array.of(1, 0, 0, 1, 1, 1), 3, 2);
  nearAll(Array.from(s.rho), [Math.sqrt(3), 1], 1e-14, "rho");
  nearAll(Array.from(la.lowRank(s, 1)), [0.5, 0.5, 0.5, 0.5, 1, 1], 1e-14, "X");
  near(la.spectralError(s, 1), 1, 1e-14, "rho_2");
});

test("lowRank clamps k to 0..min(m,n) and the input is not modified", () => {
  const a = Float64Array.of(1, 2, 3, 4, 5, 6);
  const copy = a.slice();
  const s = la.svd(a, 2, 3);
  assert.deepEqual(a, copy);
  assert.deepEqual(Array.from(la.lowRank(s, 0)), new Array(6).fill(0));
  nearAll(Array.from(la.lowRank(s, 9)), Array.from(a), 1e-13, "k above p");
  assert.equal(la.spectralError(s, 0), s.rho[0]);
  assert.equal(la.spectralError(s, 5), 0);
});

test("svd rejects a length that does not match m x n", () => {
  assert.throws(() => la.svd(Float64Array.of(1, 2, 3), 2, 2), RangeError);
});

test("storage k(m+n+1) per channel and its share of mn", () => {
  assert.equal(la.storage(499, 750, 12), 15000);
  assert.equal(la.storage(3, 2, 1), 6);
  near(la.storageFraction(499, 750, 12), 15000 / 374250, 1e-15, "fraction");
  near(100 * la.storageFraction(499, 750, 12), 4.0, 0.01, "percent from the note");
  assert.ok(la.storageFraction(10, 10, 5) > 1, "k = n/2 on a square matrix saves nothing");
});

test("fitSize shrinks the long side to the limit, keeps the ratio and never enlarges", () => {
  assert.deepEqual(la.fitSize(750, 499, 300), { w: 300, h: 200 });
  assert.deepEqual(la.fitSize(499, 750, 300), { w: 200, h: 300 });
  assert.deepEqual(la.fitSize(100, 80, 300), { w: 100, h: 80 });
  assert.deepEqual(la.fitSize(300, 300, 300), { w: 300, h: 300 });
  assert.deepEqual(la.fitSize(6000, 10, 300), { w: 300, h: 1 });
});

test("splitChannels and mergeChannels are inverse, merge rounds and clamps", () => {
  const rgba = Uint8ClampedArray.of(10, 20, 30, 255, 40, 50, 60, 255, 70, 80, 90, 255, 100, 110, 120, 255, 130, 140, 150, 255, 160, 170, 180, 255);
  const ch = la.splitChannels(rgba, 3, 2);
  assert.equal(ch.length, 3);
  assert.deepEqual(Array.from(ch[0]), [10, 40, 70, 100, 130, 160]);
  assert.deepEqual(Array.from(ch[2]), [30, 60, 90, 120, 150, 180]);
  assert.deepEqual(Array.from(la.mergeChannels(ch, 3, 2)), Array.from(rgba));
  const odd = la.mergeChannels([Float64Array.of(-5, 300.4), Float64Array.of(1.5, 2.49), Float64Array.of(0.4, 254.6)], 2, 1);
  assert.deepEqual(Array.from(odd), [0, 2, 0, 255, 255, 2, 255, 255]);
});

test("the built-in picture is deterministic, opaque, and has structure at several scales", () => {
  const a = la.syntheticImage(240, 160);
  const b = la.syntheticImage(240, 160);
  assert.equal(a.length, 240 * 160 * 4);
  // not deepEqual: on 150 000 bytes its failure message builds a diff that eats gigabytes of memory
  assert.ok(Buffer.from(a).equals(Buffer.from(b)), "two calls gave different pictures");
  for (let i = 3; i < a.length; i += 4) assert.equal(a[i], 255);
  const ch = la.splitChannels(a, 240, 160);
  for (const m of ch) {
    const s = la.svd(m, 160, 240);
    // large details: the first number dominates; small ones: the spectrum has a long tail
    assert.ok(s.rho[0] > 5 * s.rho[5], "no dominant smooth part");
    assert.ok(s.rho[60] > 1e-3 * s.rho[0], "no fine detail");
    assert.ok(s.rank > 100, `rank ${s.rank} too small to be an interesting picture`);
  }
  assert.ok(ch[0][70 * 240 + 2] - ch[0][2 * 240 + 2] > 20, "the sky has no gradient");
  const mean = (x) => x.reduce((p, q) => p + q, 0) / x.length;
  assert.ok(Math.abs(mean(ch[0]) - mean(ch[2])) > 5, "channels are nearly equal");
});

// ---------------------------------------------------------------- 2 x 2 matrix

const sortPairs = (zs) => zs.map((z) => [z.re ?? z[0], z.im ?? z[1]]).sort((p, q) => q[0] - p[0] || q[1] - p[1]);
const mat2 = (c) => la.eig2(...c.m);
const norm2 = (c) => Math.hypot(...c.m);

test("eig2: eigenvalues match numpy eigvals on 60 random and every special matrix", () => {
  for (const c of fx.mat2) {
    const r = mat2(c);
    const got = sortPairs(r.kind === "double" ? [r.values[0], r.values[0]] : r.values);
    const want = sortPairs(c.numpy);
    // a double root is only known to sqrt(eps) from rounded input, so numpy gets that slack there
    const tol = (r.kind === "double" ? 1e-7 : 1e-12) * norm2(c);
    for (let i = 0; i < 2; i++) {
      near(got[i][0], want[i][0], tol, `${c.name}: re ${i}`);
      near(got[i][1], want[i][1], tol, `${c.name}: im ${i}`);
    }
  }
});

test("eig2: tr and det equal numpy's, and the roots satisfy lambda^2 - tr lambda + det = 0", () => {
  for (const c of fx.mat2) {
    const r = mat2(c);
    near(r.tr, c.tr, 1e-13 * norm2(c), `${c.name}: tr`);
    near(r.det, c.det, 1e-12 * norm2(c) ** 2, `${c.name}: det`);
    for (const z of r.values) {
      // p(z) for z = re + i im
      const re = z.re * z.re - z.im * z.im - r.tr * z.re + r.det, im = 2 * z.re * z.im - r.tr * z.im;
      near(Math.hypot(re, im), 0, 1e-12 * norm2(c) ** 2, `${c.name}: p(lambda)`);
    }
  }
});

test("eig2: algebraic and geometric multiplicities equal sympy's exact ones", () => {
  let checked = 0;
  for (const c of fx.mat2.filter((x) => x.exact)) {
    const r = mat2(c);
    const want = c.exact.map((e) => ({ ...e })).sort((p, q) => q.re - p.re || q.im - p.im);
    const got = r.kind === "complex" ? r.values : r.values;
    // sympy lists one entry per distinct root, complex pairs as two entries
    assert.equal(want.length, got.length, `${c.name}: number of distinct roots`);
    for (let i = 0; i < want.length; i++) {
      near(got[i].re, want[i].re, 1e-12 * (1 + norm2(c)), `${c.name}: re`);
      near(Math.abs(got[i].im), Math.abs(want[i].im), 1e-12 * (1 + norm2(c)), `${c.name}: im`);
      assert.equal(r.alg, want[i].alg, `${c.name}: algebraic multiplicity`);
      assert.equal(r.geom, want[i].geom, `${c.name}: geometric multiplicity`);
      checked++;
    }
  }
  assert.ok(checked >= 20, `only ${checked} roots checked`);
});

test("eig2: the Jordan block has geometric multiplicity 1, the scalar matrix 2", () => {
  const j = la.eig2(2, 1, 0, 2);
  assert.deepEqual([j.kind, j.alg, j.geom, j.vectors.length], ["double", 2, 1, 1]);
  const s = la.eig2(2, 0, 0, 2);
  assert.deepEqual([s.kind, s.alg, s.geom, s.vectors.length], ["double", 2, 2, 2]);
  const z = la.eig2(0, 0, 0, 0);
  assert.deepEqual([z.kind, z.alg, z.geom], ["double", 2, 2]);
  const n = la.eig2(0, 1, 0, 0);
  assert.deepEqual([n.alg, n.geom], [2, 1]);
});

test("eig2 tells a double root from rounding noise and from close distinct roots", () => {
  // (a - d)^2 + 4bc is about 1e-17 here, not 0: typed decimals must still give a double root with one eigenvector
  const d = la.eig2(0.7, 0.3, -0.3, 0.1);
  assert.deepEqual([d.kind, d.alg, d.geom], ["double", 2, 1]);
  // 0.1 + 0.2 and 0.3 differ by one ulp: the matrix is scalar for every practical purpose
  const s = la.eig2(0.1 + 0.2, 0, 0, 0.3);
  assert.deepEqual([s.kind, s.alg, s.geom], ["double", 2, 2]);
  // roots 1 and 1.05 are distinct: two eigenvectors, the axes
  const c = la.eig2(1, 0, 0, 1.05);
  assert.equal(c.kind, "distinct");
  nearAll(c.values.map((z) => z.re), [1.05, 1], 1e-15, "roots");
});

test("eig2: real eigenvectors are unit and satisfy A v = lambda v", () => {
  let checked = 0;
  for (const c of fx.mat2) {
    const r = mat2(c);
    if (r.kind === "complex") { assert.equal(r.vectors.length, 0, c.name); continue; }
    assert.equal(r.vectors.length, r.kind === "distinct" ? 2 : r.geom, c.name);
    r.vectors.forEach((v, i) => {
      const mu = r.values[r.kind === "distinct" ? i : 0].re;
      near(Math.hypot(...v), 1, 1e-12, `${c.name}: unit`);
      const av = la.mapPoint(...c.m, v);
      nearAll(av, [mu * v[0], mu * v[1]], 1e-9 * (1 + norm2(c)), `${c.name}: A v = mu v`);
      checked++;
    });
  }
  assert.ok(checked > 60, `only ${checked} vectors checked`);
});

test("eig2: the sign of an eigenvector is fixed, the first nonzero coordinate is positive", () => {
  for (const c of fx.mat2) {
    for (const v of mat2(c).vectors) assert.ok(v[0] > 0 || (v[0] === 0 && v[1] > 0), `${c.name}: ${v}`);
  }
  assert.deepEqual(la.eig2(0, 1, 0, 0).vectors, [[1, 0]]);
  assert.deepEqual(la.eig2(1, 0, 0, -1).vectors, [[1, 0], [0, 1]]);
});

test("eig2: complex roots come as alpha +- i beta with beta > 0 first, tr/2 and sqrt(-disc)/2", () => {
  const r = la.eig2(0, -1, 1, 0);
  assert.equal(r.kind, "complex");
  assert.deepEqual(r.values, [{ re: 0, im: 1 }, { re: 0, im: -1 }]);
  const q = la.eig2(1, -1, 1, 1);
  near(q.values[0].re, 1, 1e-15, "alpha");
  near(q.values[0].im, 1, 1e-15, "beta");
});

test("eig2 keeps the small root accurate where the textbook formula loses it", () => {
  // roots 1e8 and 1e-8: (tr - sqrt(disc)) / 2 cancels to garbage
  const r = la.eig2(1e8, 0, 0, 1e-8);
  near(r.values[1].re / 1e-8, 1, 1e-12, "small root");
  const t = la.eig2(1e8, 1, 1, 1e-8);
  near(t.values[0].re * t.values[1].re, t.det, 1e-12 * Math.abs(t.det), "Vieta");
});

test("the image of the unit square has area |det A| and the orientation sign of det A", () => {
  for (const c of fx.mat2) {
    const square = [[0, 0], [1, 0], [1, 1], [0, 1]].map((p) => la.mapPoint(...c.m, p));
    near(la.signedArea(square), c.det, 1e-12 * norm2(c) ** 2, `${c.name}: signed area`);
    near(Math.abs(la.signedArea(square)), Math.abs(c.det), 1e-12 * norm2(c) ** 2, `${c.name}: area`);
  }
});

test("the image of the unit circle (a 2000-gon) has area pi |det A|", () => {
  for (const c of fx.mat2.filter((x) => !x.exact || x.name.includes("ro") || x.name === "diagonalisable")) {
    const poly = Array.from({ length: 2000 }, (_, i) => la.mapPoint(...c.m, [Math.cos(2 * Math.PI * i / 2000), Math.sin(2 * Math.PI * i / 2000)]));
    near(Math.abs(la.signedArea(poly)), Math.PI * Math.abs(c.det), 1e-5 * norm2(c) ** 2, c.name);
  }
});

// ---------------------------------------------------------------- the Fredholm equation

const presets = JSON.parse(readFileSync(new URL("./presets.json", import.meta.url), "utf8"));

test("the source of lacore.js has no eval and no Function constructor", () => {
  const src = readFileSync(new URL("./lacore.js", import.meta.url), "utf8");
  assert.ok(!/\beval\s*\(/.test(src), "eval found");
  assert.ok(!/\bFunction\s*\(|new\s+Function|\bFunction\b\s*\./.test(src.replace(/\/\/.*$/gm, "")), "Function constructor found");
});

const solveCases = presets.filter((p) => p.pages.includes("solve"));
const build = (p) => nk.compileProblem({
  lo: nk.compileExpression(p.lo, [])(), hi: nk.compileExpression(p.hi, [])(),
  rows: p.rows.map(([alpha, beta]) => ({ alpha, beta })), f: p.f,
});
const fxOf = (id) => fx.fredholm.find((c) => c.id === id);

test("A and f_m of every preset match scipy QUADPACK", () => {
  assert.equal(fx.fredholm.length, presets.length);
  for (const p of presets) {
    const c = fxOf(p.id), data = la.kernelData(build(p));
    assert.ok(data.ok, `${p.id}: quadrature did not converge`);
    const sc = Math.max(...c.A.map(Math.abs), 1);
    nearAll(Array.from(data.A), c.A, 1e-10 * sc, `${p.id}: A`);
    nearAll(Array.from(data.fv), c.fv, 1e-10 * sc, `${p.id}: f`);
  }
});

test("Delta(lambda) = det(I - lambda A) matches numpy's determinant at six values", () => {
  for (const p of presets) {
    const c = fxOf(p.id), data = la.kernelData(build(p));
    for (const { lam, value } of c.delta) rel(la.delta(data.A, c.n, lam), value, 1e-9, `${p.id}: Delta(${lam})`);
  }
});

test("Delta of the notes' examples in closed form: 1 + 2 pi^2 lambda^2, (1 - lambda pi/4)(1 - lambda pi/8), 1, 1 + lambda^2/150", () => {
  const delta = (id, lam) => { const p = presets.find((q) => q.id === id), d = la.kernelData(build(p)); return la.delta(d.A, p.rows.length, lam); };
  for (const lam of [-2, 0.3, 1, 2.5]) {
    rel(delta("note-example", lam), 1 + 2 * Math.PI ** 2 * lam ** 2, 1e-10, "note example");
    rel(delta("example-two-numbers", lam), (1 - lam * Math.PI / 4) * (1 - lam * Math.PI / 8), 1e-10, "example 1");
    rel(delta("example-none", lam), 1, 1e-10, "example 2");
    rel(delta("example-imaginary", lam), 1 + lam * lam / 150, 1e-10, "example 3");
  }
});

test("the solution of every preset matches numpy's solve and the closed-form answer of the note", () => {
  assert.ok(solveCases.length >= 5);
  for (const p of solveCases) {
    const c = fxOf(p.id), prob = build(p), data = la.kernelData(prob);
    const lam = nk.compileExpression(p.lambda, [])();
    const s = la.solveFredholm(data.A, data.fv, prob.n, lam);
    assert.equal(s.singular, false, p.id);
    const sc = Math.max(...c.C.map(Math.abs), 1);
    nearAll(Array.from(s.C), c.C, 1e-9 * sc, `${p.id}: C`);
    c.xs.forEach((x, i) => {
      const got = la.solutionAt(prob, s.C, lam, x);
      rel(got, c.phi[i], 1e-9, `${p.id}: numpy phi(${x})`);
      rel(got, c.answer[i], 1e-8, `${p.id}: the answer of the note at ${x}`);
    });
  }
});

test("the residual phi - lambda int K phi - f is at the quadrature level for every preset", () => {
  for (const p of solveCases) {
    const prob = build(p), data = la.kernelData(prob);
    const lam = nk.compileExpression(p.lambda, [])();
    const s = la.solveFredholm(data.A, data.fv, prob.n, lam);
    for (let i = 1; i < 12; i++) {
      const x = prob.lo + (prob.hi - prob.lo) * i / 12;
      const r = la.residualAt(prob, s.C, lam, x);
      assert.ok(Math.abs(r.value) <= 1e-9 * Math.max(1, Math.abs(la.solutionAt(prob, s.C, lam, x))) + 10 * r.err, `${p.id}: residual ${r.value} at ${x}`);
    }
    // a wrong constant makes the residual large: the check can fail
    const bad = Float64Array.from(s.C, (v, k) => (k === 0 ? v + 0.1 : v));
    const x = prob.lo + (prob.hi - prob.lo) / 3;
    assert.ok(Math.abs(la.residualAt(prob, bad, lam, x).value) > 1e-3 || prob.n === 0, `${p.id}: residual does not see a wrong C`);
  }
});

test("at a characteristic number the system is reported singular; nearby and at lambda = 0 it is solved", () => {
  const p = presets.find((q) => q.id === "example-two-numbers");
  const prob = build({ ...p, f: "cos(x)" }), data = la.kernelData(prob);
  assert.equal(la.solveFredholm(data.A, data.fv, 2, 4 / Math.PI).singular, true);
  assert.equal(la.solveFredholm(data.A, data.fv, 2, 8 / Math.PI).singular, true);
  const near4 = la.solveFredholm(data.A, data.fv, 2, 4 / Math.PI * (1 + 1e-3));
  assert.equal(near4.singular, false);
  assert.ok(near4.cond > 1e2 && near4.cond < 1e5, `cond ${near4.cond}`);
  const zero = la.solveFredholm(data.A, data.fv, 2, 0);
  assert.equal(zero.singular, false);
  nearAll(Array.from(zero.C), Array.from(data.fv), 1e-14, "lambda = 0 gives C = f");
});

test("a characteristic number of a non-diagonal system is singular although no pivot is exactly zero", () => {
  // K = x * 1 + 1 * t on [0, 1]: A = [[1/2, 1/3], [1, 1/2]], mu = 1/2 +- 1/sqrt(3), lambda = 1 / mu
  const prob = nk.compileProblem({ lo: 0, hi: 1, rows: [{ alpha: "x", beta: "1" }, { alpha: "1", beta: "t" }], f: "1" });
  const data = la.kernelData(prob);
  nearAll(Array.from(data.A), [0.5, 1 / 3, 1, 0.5], 1e-14, "A");
  for (const sgn of [1, -1]) {
    // 1e-13 off the exact root: the pivots are not zero, the condition number is about 1e13
    const lam = (1 + 1e-13) / (0.5 + sgn / Math.sqrt(3));
    const s = la.solveFredholm(data.A, data.fv, 2, lam);
    assert.equal(s.singular, true, `lambda ${lam}, cond ${s.cond}`);
    assert.ok(Number.isFinite(s.cond) && s.cond > 1e11, `cond ${s.cond}`);
    assert.ok(Math.abs(s.delta) < 1e-11, `Delta ${s.delta}`);
  }
  const s = la.solveFredholm(data.A, data.fv, 2, 0.5);
  assert.equal(s.singular, false);
});

test("a one-term kernel: lambda = 2 is characteristic for sin x cos t on [0, pi/2], the plain condition number would say 1", () => {
  const prob = nk.compileProblem({ lo: 0, hi: Math.PI / 2, rows: [{ alpha: "sin(x)", beta: "cos(t)" }], f: "sin(x)" });
  const data = la.kernelData(prob);
  near(data.A[0], 0.5, 1e-15, "a_11");
  const exact = la.solveFredholm(data.A, data.fv, 1, 2);
  assert.equal(exact.singular, true, `cond ${exact.cond}`);
  near(nk.cond1(la.systemMatrix(data.A, 1, 2 * (1 + 1e-12)), 1), 1, 1e-12, "the plain condition number of a 1 x 1 matrix is 1 whatever it is");
  assert.equal(la.solveFredholm(data.A, data.fv, 1, 2 * (1 + 1e-3)).singular, false);
  // 1e-6 off a characteristic number the solution is still meaningful (cond about 1e6), 1e-12 off it is not
  const close = la.solveFredholm(data.A, data.fv, 1, 2 * (1 + 1e-6));
  assert.equal(close.singular, false);
  assert.ok(close.cond > 1e5 && close.cond < 1e8, `cond ${close.cond}`);
  assert.equal(la.solveFredholm(data.A, data.fv, 1, 2 * (1 + 1e-12)).singular, true);
});

// ---------------------------------------------------------------- characteristic numbers

const numbersCases = presets.filter((p) => p.pages.includes("numbers"));
const cabs = (z) => Math.hypot(z.re, z.im);

const group = (A, n) => la.characteristicNumbers(Float64Array.from(A), n);

test("characteristic numbers of small matrices: repeated, defective, complex pair, zero and negligible eigenvalues", () => {
  let g = group([2, 0, 0, 0, 2, 0, 0, 0, 3], 3);
  assert.deepEqual(g.map((x) => [x.alg, x.rank, x.real]), [[1, 1, true], [2, 2, true]]);
  near(g[0].lambda.re, 1 / 3, 1e-15, "lambda of mu = 3");
  near(g[1].lambda.re, 1 / 2, 1e-15, "lambda of mu = 2");
  near(g[1].sigma.re, 2, 1e-15, "sigma");
  g = group([2, 1, 0, 2], 2);
  assert.deepEqual(g.map((x) => [x.alg, x.rank]), [[2, 1]], "a Jordan block: multiplicity 2, one eigenfunction");
  g = group([0, -1, 1, 0], 2);
  assert.deepEqual(g.map((x) => [x.alg, x.rank, x.real]), [[1, 1, false], [1, 1, false]]);
  assert.ok(g[0].lambda.im > 0 && g[1].lambda.im < 0, "the pair comes with the positive imaginary part first");
  near(Math.hypot(g[0].lambda.re, g[0].lambda.im), 1, 1e-15, "|lambda|");
  assert.deepEqual(group([0, 0, 0, 0], 2), [], "A = 0: Delta = 1, no characteristic numbers");
  assert.deepEqual(group([0, 1, 0, 0], 2), [], "nilpotent: no nonzero eigenvalues");
  g = group([1, 0, 0, 1e-9], 2);
  assert.equal(g.length, 1, "an eigenvalue 1e-9 of a matrix of norm 1 is zero within the quadrature error");
  g = group([3, 1, 0, 0, 3, 1, 0, 0, 3], 3);
  assert.deepEqual(g.map((x) => [x.alg, x.rank]), [[3, 1]], "a Jordan block of size 3");
  assert.deepEqual(group([0.5, 0, 0, -0.25], 2).map((x) => x.lambda.re), [2, -4], "by |lambda| ascending: 1/0.5 = 2 before 1/(-0.25) = -4");
  assert.equal(group([1, 0, 0, 1.0005], 2).length, 2, "roots 5e-4 apart are two numbers");
  // roots 1 +- 1e-7 i of a nearly Jordan block are one real root of multiplicity 2 within the accuracy of the method
  g = group([1, 1, -1e-14, 1], 2);
  assert.deepEqual(g.map((x) => [x.alg, x.real]), [[2, true]]);
  assert.equal(g[0].lambda.im, 0);
});

test("the rank of a complex characteristic number counts complex solutions: two rotations, and a rotation Jordan block", () => {
  // mu = +-i, each of multiplicity 2: two independent complex eigenvectors each
  let g = group([0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0], 4);
  assert.deepEqual(g.map((x) => [x.alg, x.rank, x.real]), [[2, 2, false], [2, 2, false]]);
  // the Jordan block over the rotation: multiplicity 2, one eigenvector
  g = group([0, -1, 1, 0, 1, 0, 0, 1, 0, 0, 0, -1, 0, 0, 1, 0], 4);
  assert.deepEqual(g.map((x) => [x.alg, x.rank, x.real]), [[2, 1, false], [2, 1, false]]);
});

test("characteristic numbers of the presets: roots, multiplicities and ranks against numpy", () => {
  for (const p of numbersCases) {
    const c = fxOf(p.id), data = la.kernelData(build(p));
    const mine = la.characteristicNumbers(data.A, c.n, data.scale);
    const expanded = mine.flatMap((g) => Array.from({ length: g.alg }, () => g.lambda));
    const top = Math.max(1, ...c.characteristic.map(([re, im]) => Math.hypot(re, im)));
    matchAll(expanded, c.characteristic, 1e-7 * top, p.id);
    assert.equal(mine.length, c.groups.length, `${p.id}: number of distinct numbers`);
    for (const g of mine) {
      const ref = c.groups.find((r) => Math.hypot(r.lambda[0] - g.lambda.re, r.lambda[1] - g.lambda.im) <= 1e-7 * top);
      assert.ok(ref, `${p.id}: no reference group for ${g.lambda.re}`);
      assert.equal(g.alg, ref.alg, `${p.id}: multiplicity`);
      assert.equal(g.rank, ref.rank, `${p.id}: rank`);
    }
  }
});

test("the notes' examples in closed form: 4/pi and 8/pi, none, +-5 sqrt(6) i, +-2/pi, -e/2 and e/(e^2-5)", () => {
  const of = (id) => { const p = presets.find((q) => q.id === id), d = la.kernelData(build(p)); return la.characteristicNumbers(d.A, p.rows.length, d.scale); };
  const one = of("example-two-numbers");
  assert.equal(one.length, 2);
  near(one[0].lambda.re, 4 / Math.PI, 1e-12, "4/pi");
  near(one[1].lambda.re, 8 / Math.PI, 1e-12, "8/pi");
  assert.deepEqual(of("example-none"), []);
  const three = of("example-imaginary");
  assert.equal(three.length, 2);
  for (const g of three) { near(g.lambda.re, 0, 1e-12, "re"); near(Math.abs(g.lambda.im), 5 * Math.sqrt(6), 1e-10, "5 sqrt 6"); assert.equal(g.real, false); }
  assert.ok(three[0].sigma.im * three[0].lambda.im < 0, "sigma = 1/lambda has the opposite sign of the imaginary part");
  const t126 = of("task-126");
  matchAll(t126.map((g) => g.lambda), [[2 / Math.PI, 0], [-2 / Math.PI, 0]], 1e-12, "126");
  const t131 = of("task-131");
  matchAll(t131.map((g) => g.lambda), [[-Math.E / 2, 0], [Math.E / (Math.E ** 2 - 5), 0]], 1e-12, "131");
  const dbl = of("example-double");
  assert.deepEqual(dbl.map((g) => [g.alg, g.rank]), [[2, 2]]);
  near(dbl[0].lambda.re, 1 / Math.PI, 1e-12, "1/pi");
  const jor = of("example-jordan");
  assert.deepEqual(jor.map((g) => [g.alg, g.rank]), [[2, 1]]);
  near(jor[0].lambda.re, 0.5, 1e-6, "1/2 of the Jordan kernel");
});

test("the characteristic numbers are the roots of Delta: its polynomial vanishes at each, complex ones included", () => {
  for (const p of numbersCases) {
    const data = la.kernelData(build(p)), n = p.rows.length;
    const d = nk.deltaCoefficients(data.A, n);
    for (const g of la.characteristicNumbers(data.A, n, data.scale)) {
      // Horner in complex arithmetic
      let re = 0, im = 0;
      for (let k = n; k >= 0; k--) { const nr = re * g.lambda.re - im * g.lambda.im + d[k], ni = re * g.lambda.im + im * g.lambda.re; re = nr; im = ni; }
      let mag = 0;
      for (let k = 0; k <= n; k++) mag += Math.abs(d[k]) * cabs(g.lambda) ** k;
      assert.ok(Math.hypot(re, im) <= 1e-6 * mag, `${p.id}: |Delta(lambda)| = ${Math.hypot(re, im)}`);
      near(cabs(g.lambda) * cabs(g.sigma), 1, 1e-14, "lambda sigma = 1");
    }
  }
});

test("eigenfunctions: C spans the null space, there are rank of them, and phi solves the homogeneous equation by quadrature", () => {
  let checked = 0;
  for (const p of numbersCases) {
    const prob = build(p), data = la.kernelData(prob);
    for (const g of la.characteristicNumbers(data.A, prob.n, data.scale).filter((x) => x.real)) {
      const Cs = la.eigenCoefficients(data.A, prob.n, g.lambda.re);
      assert.equal(Cs.length, g.rank, `${p.id}: number of eigenfunctions`);
      Cs.forEach((C, i) => {
        const M = la.systemMatrix(data.A, prob.n, g.lambda.re);
        nearAll(mulVec(M, prob.n, prob.n, C), new Array(prob.n).fill(0), 1e-8, `${p.id}: (I - lambda A^T) C`);
        near(Math.hypot(...C), 1, 1e-12, "unit C");
        for (let j = 0; j < i; j++) near(dot(C, Cs[j]), 0, 1e-10, "orthogonal");
        for (let s = 1; s < 8; s++) {
          const x = prob.lo + (prob.hi - prob.lo) * s / 8;
          const r = la.residualAt(prob, C, g.lambda.re, x);
          const phi = la.solutionAt(prob, C, g.lambda.re, x);
          assert.ok(Math.abs(r.value) <= 1e-7 * Math.max(1, Math.abs(phi)) + 10 * r.err, `${p.id}: residual ${r.value} at ${x}`);
        }
        // the check sees a wrong C
        // the component that is smallest in C: raising the largest one would only rescale the eigenfunction
        const weak = C.reduce((b, v, k) => (Math.abs(v) < Math.abs(C[b]) ? k : b), 0);
        const bad = Float64Array.from(C, (v, k) => (k === weak ? v + 0.3 : v));
        const x = prob.lo + (prob.hi - prob.lo) / 3;
        if (g.rank === 1) assert.ok(Math.abs(la.residualAt(prob, bad, g.lambda.re, x).value) > 1e-4, `${p.id}: residual does not see a wrong C`);
        checked++;
      });
    }
  }
  assert.ok(checked >= 8, `only ${checked} eigenfunctions checked`);
});

test("eigenfunctions of the notes: cos^2 x for 4/pi, cos 3x for 8/pi, x for the Jordan kernel, normalised to a maximum of 1", () => {
  const xs = [0, 0.4, 1, 1.7, 2.6, Math.PI];
  const ex1 = presets.find((q) => q.id === "example-two-numbers"), prob = build(ex1), data = la.kernelData(prob);
  const [g1, g2] = la.characteristicNumbers(data.A, 2, data.scale);
  const f1 = la.eigenFunctionValues(prob, la.eigenCoefficients(data.A, 2, g1.lambda.re)[0], xs);
  nearAll(f1, xs.map((x) => Math.cos(x) ** 2), 1e-9, "cos^2");
  const f2 = la.eigenFunctionValues(prob, la.eigenCoefficients(data.A, 2, g2.lambda.re)[0], xs);
  nearAll(f2, xs.map((x) => Math.cos(3 * x)), 1e-9, "cos 3x");
  assert.equal(Math.max(...f2.map(Math.abs)), 1);
  const jp = presets.find((q) => q.id === "example-jordan"), jprob = build(jp), jd = la.kernelData(jprob);
  const jg = la.characteristicNumbers(jd.A, 2, jd.scale)[0];
  const xs2 = [0.1, 0.5, 0.9, 1];
  const fj = la.eigenFunctionValues(jprob, la.eigenCoefficients(jd.A, 2, jg.lambda.re)[0], xs2);
  nearAll(fj, xs2, 1e-6, "x on [0, 1]");
  assert.deepEqual(la.eigenFunctionValues({ n: 1, alpha: [() => 0] }, Float64Array.of(1), [1, 2]), [0, 0], "the zero function stays zero");
  // the point of the largest modulus gets the value +1, whatever the sign of C
  const C3 = la.eigenCoefficients(data.A, 2, g2.lambda.re)[0];
  const at = [0.5, Math.PI / 3, 2];
  nearAll(la.eigenFunctionValues(prob, C3, at), at.map((x) => -Math.cos(3 * x)), 1e-9, "-cos 3x: the value at pi/3 is +1");
  nearAll(la.eigenFunctionValues(prob, C3.map((v) => -v), at), at.map((x) => -Math.cos(3 * x)), 1e-9, "the sign of C does not matter");
});

// ---------------------------------------------------------------- principal components of a plane cloud

const clouds = fx.pca;
const cloud = (name) => clouds.find((c) => c.name === name);
const withCov = clouds.filter((c) => c.cov);
// the scale of a cloud: its largest eigenvalue, the unit of every tolerance below
const lam1 = (c) => c.lam[0];
const axes = (c) => { const [cxx, cxy, , cyy] = c.cov; return la.principalAxes(cxx, cxy, cyy); };
const absdot = (u, v) => Math.abs(u[0] * v[0] + u[1] * v[1]);

test("centerPoints: the mean equals numpy's and the centred cloud has mean zero", () => {
  for (const c of clouds) {
    const r = la.centerPoints(c.pts);
    const spread = Math.max(...c.pts.flat().map(Math.abs));
    nearAll(r.mean, c.mean, 1e-13 * spread, `${c.name}: mean`);
    assert.equal(r.centered.length, c.pts.length, c.name);
    const m = [0, 1].map((k) => r.centered.reduce((s, p) => s + p[k], 0) / r.centered.length);
    nearAll(m, [0, 0], 1e-13 * spread, `${c.name}: centred mean`);
  }
  assert.deepEqual(la.centerPoints([]), { mean: [0, 0], centered: [] });
});

test("covariance2 equals np.cov with the divisor N - 1, and is zero for fewer than two points", () => {
  for (const c of withCov) {
    const r = la.covariance2(c.pts);
    assert.equal(r.n, c.pts.length);
    nearAll([r.cxx, r.cxy, r.cyy], [c.cov[0], c.cov[1], c.cov[3]], 1e-12 * lam1(c), `${c.name}: C`);
  }
  for (const pts of [[], [[3, -2]]]) assert.deepEqual(la.covariance2(pts), { n: pts.length, cxx: 0, cxy: 0, cyy: 0 });
});

test("principalAxes: eigenvalues equal np.linalg.eigh, descending and non-negative, also for points on a line", () => {
  for (const c of withCov) {
    const r = axes(c);
    nearAll(r.lambda, c.lam, 1e-12 * lam1(c), `${c.name}: lambda`);
    assert.ok(r.lambda[0] >= r.lambda[1] && r.lambda[1] >= 0, `${c.name}: order or sign`);
  }
  // on a line the second eigenvalue is exactly zero in theory and only rounding in practice
  assert.ok(axes(cloud("line-diagonal")).lambda[1] <= 1e-12 * lam1(cloud("line-diagonal")));
});

test("principalAxes: w1, w2 equal eigh's up to sign when the axes are defined, are orthonormal and satisfy C w = lambda w", () => {
  let checked = 0;
  for (const c of withCov) {
    const r = axes(c);
    if (r.status !== "ok") continue;
    for (let j = 0; j < 2; j++) {
      near(Math.hypot(...r.w[j]), 1, 1e-14, `${c.name}: |w${j}|`);
      near(absdot(r.w[j], c.w[j]), 1, 1e-8, `${c.name}: w${j} against eigh`);
      const Cw = [c.cov[0] * r.w[j][0] + c.cov[1] * r.w[j][1], c.cov[2] * r.w[j][0] + c.cov[3] * r.w[j][1]];
      nearAll(Cw, r.w[j].map((v) => v * r.lambda[j]), 1e-12 * lam1(c), `${c.name}: C w${j}`);
    }
    near(r.w[0][0] * r.w[1][0] + r.w[0][1] * r.w[1][1], 0, 1e-14, `${c.name}: w1 . w2`);
    checked++;
  }
  assert.ok(checked >= 14, `only ${checked} clouds checked`);
});

test("principalAxes: the status is ok / round / zero, and a round or empty cloud has no axes", () => {
  const status = Object.fromEntries(clouds.map((c) => [c.name, c.cov ? axes(c).status : "few"]));
  const round = clouds.map((c) => c.name).filter((n) => n.startsWith("round-"));
  assert.ok(round.length >= 5, "round clouds are missing from the fixtures");
  for (const n of round) {
    // the turned rings are round only up to rounding: lambda1 - lambda2 is about 1e-16, not 0
    assert.equal(status[n], "round", n);
    assert.equal(axes(cloud(n)).w, null, `${n}: no axes`);
    near(axes(cloud(n)).explained, 0.5, 1e-12, `${n}: explained`);
  }
  assert.equal(status["same-points"], "zero");
  assert.equal(la.principalAxes(0, 0, 0).w, null);
  assert.equal(la.principalAxes(0, 0, 0).explained, null);
  // 2 x 2 matrix 2I and a 0.05 % elongation: the second one is not round, its axes are the x and y axes
  assert.equal(la.principalAxes(2, 0, 2).status, "round");
  const slim = la.principalAxes(2.001, 0, 2);
  assert.equal(slim.status, "ok");
  near(absdot(slim.w[0], [1, 0]), 1, 1e-14, "elongated along x");
  // roots closer than eig2's double-root tolerance (1e-6 of the scale) still get their axes, exactly
  const close = la.principalAxes(1 + 1e-7, 0, 1);
  assert.equal(close.status, "ok");
  near(absdot(close.w[0], [1, 0]), 1, 1e-15, "gap 1e-7: w1");
  near(absdot(close.w[1], [0, 1]), 1, 1e-15, "gap 1e-7: w2");
  for (const n of Object.keys(status)) if (!n.startsWith("round-") && !["same-points", "single-point"].includes(n)) assert.notEqual(status[n], "round", n);
});

test("principalAxes: the explained variance is lambda1 / (lambda1 + lambda2), as in eigh", () => {
  for (const c of withCov) {
    const r = axes(c);
    if (r.status === "zero") continue;
    near(r.explained, c.lam[0] / (c.lam[0] + c.lam[1]), 1e-12, `${c.name}: explained`);
  }
});

test("the note's four points: lambda = 16/3 and 4/3, w1 = (1, 1)/sqrt 2, 80 % explained, rho_2^2 = 4, OLS slope 3/5", () => {
  const r = la.pca2(cloud("note-four-points").pts);
  nearAll(r.lambda, [16 / 3, 4 / 3], 1e-14, "lambda");
  nearAll(r.C, [10 / 3, 2, 2, 10 / 3], 1e-14, "C");
  near(absdot(r.w[0], [Math.SQRT1_2, Math.SQRT1_2]), 1, 1e-14, "w1");
  near(absdot(r.w[1], [Math.SQRT1_2, -Math.SQRT1_2]), 1, 1e-14, "w2");
  near(r.explained, 0.8, 1e-14, "explained");
  near(r.pc.perp, 4, 1e-13, "sum of squared perpendiculars = rho_2^2");
  near(r.ols.slope, 0.6, 1e-14, "slope");
  near(r.ols.intercept, 0, 1e-14, "intercept");
  // the projections on w1 are (2 sqrt 2, -2 sqrt 2, 0, 0) along the axis
  nearAll(r.coords, [2 * Math.SQRT2, -2 * Math.SQRT2, 0, 0].map((v, i) => (r.coords[0] > 0 ? v : -v)), 1e-13, "coordinates");
});

test("olsLine equals np.polyfit(x, y, 1) and is null when x does not vary or there are fewer than two points", () => {
  let checked = 0;
  for (const c of withCov) {
    const o = la.olsLine(c.pts);
    if (!c.poly) { assert.equal(o, null, `${c.name}: expected no line`); continue; }
    const spread = Math.max(...c.pts.flat().map(Math.abs));
    near(o.slope, c.poly[0], 1e-9 * Math.max(1, Math.abs(c.poly[0])), `${c.name}: slope`);
    near(o.intercept, c.poly[1], 1e-9 * spread * Math.max(1, Math.abs(c.poly[0])), `${c.name}: intercept`);
    near(Math.hypot(...o.dir), 1, 1e-15, `${c.name}: |dir|`);
    checked++;
  }
  assert.ok(checked >= 15, `only ${checked} fits checked`);
  assert.equal(la.olsLine([[3, -2]]), null);
  assert.equal(la.olsLine([]), null);
  near(la.olsLine(cloud("line-horizontal").pts).slope, 0, 1e-15, "horizontal line has slope 0");
});

test("lineSums: perpendiculars and vertical deviations of both lines equal numpy's, the vertical one of a vertical line is null", () => {
  let checked = 0;
  for (const c of withCov) {
    const r = la.pca2(c.pts);
    const unit = lam1(c) * (c.pts.length - 1);
    if (r.status === "ok") {
      near(r.pc.perp, c.pc_line.perp, 1e-10 * unit, `${c.name}: PC perp`);
      near(r.pc.perp, c.perp_svd, 1e-10 * unit, `${c.name}: PC perp against the SVD`);
      if (c.pc_line.vert === null) assert.equal(r.pc.vert, null, `${c.name}: vertical PC line`);
      else near(r.pc.vert, c.pc_line.vert, 1e-8 * unit, `${c.name}: PC vert`);
      checked++;
    }
    if (c.ols_line) {
      near(r.ols.perp, c.ols_line.perp, 1e-10 * unit, `${c.name}: OLS perp`);
      near(r.ols.vert, c.ols_line.vert, 1e-10 * unit, `${c.name}: OLS vert`);
      checked++;
    }
  }
  assert.ok(checked >= 28, `only ${checked} sums checked`);
  // a vertical line: the deviations along Y do not exist
  assert.equal(la.lineSums([[1, 2], [1, 5]], { point: [1, 0], dir: [0, 1] }).vert, null);
});

test("the sum of squared perpendiculars to the first-component line is (N - 1) lambda2 = rho_2^2", () => {
  for (const c of withCov) {
    const r = la.pca2(c.pts);
    if (r.status !== "ok") continue;
    near(r.pc.perp, (c.pts.length - 1) * c.lam[1], 1e-10 * lam1(c) * (c.pts.length - 1), c.name);
  }
});

test("the first-component line has the smaller sum of perpendiculars, the OLS line the smaller sum of vertical deviations", () => {
  let strict = 0;
  for (const c of withCov) {
    const r = la.pca2(c.pts);
    if (r.status !== "ok" || !r.ols || r.pc.vert === null) continue;
    const unit = lam1(c) * (c.pts.length - 1);
    assert.ok(r.pc.perp <= r.ols.perp + 1e-10 * unit, `${c.name}: perp ${r.pc.perp} vs ${r.ols.perp}`);
    assert.ok(r.ols.vert <= r.pc.vert + 1e-10 * unit, `${c.name}: vert ${r.ols.vert} vs ${r.pc.vert}`);
    if (r.pc.perp < r.ols.perp - 1e-6 * unit && r.ols.vert < r.pc.vert - 1e-6 * unit) strict++;
  }
  assert.ok(strict >= 8, `the two lines differ strictly on only ${strict} clouds`);
});

test("no other line through the centre beats w1 for perpendiculars, and no line y = kx + b beats OLS for vertical deviations", () => {
  for (const name of ["random-50", "random-200", "shifted-1000", "note-four-points"]) {
    const c = cloud(name), r = la.pca2(c.pts);
    for (let i = 0; i < 180; i++) {
      const t = Math.PI * i / 180;
      const s = la.lineSums(c.pts, { point: r.mean, dir: [Math.cos(t), Math.sin(t)] });
      assert.ok(s.perp >= r.pc.perp - 1e-9 * r.pc.perp, `${name}: direction ${i} deg beats w1`);
    }
    for (const dk of [-0.3, -0.01, 0.01, 0.3]) for (const db of [-0.5, 0, 0.5]) {
      const k = r.ols.slope + dk, b = r.ols.intercept + db, n = Math.hypot(1, k);
      const s = la.lineSums(c.pts, { point: [0, b], dir: [1 / n, k / n] });
      assert.ok(s.vert >= r.ols.vert - 1e-9 * r.ols.vert, `${name}: line ${dk}/${db} beats OLS`);
    }
  }
});

test("projections on the first component lie on its line, the residual is orthogonal, and the coordinates have variance lambda1", () => {
  for (const name of ["random-50", "random-1000-wide", "shifted-1000", "line-diagonal", "two-points"]) {
    const c = cloud(name), r = la.pca2(c.pts);
    const unit = Math.max(...c.pts.flat().map(Math.abs));
    r.projections.forEach((q, i) => {
      const p = c.pts[i];
      near((q[0] - r.mean[0]) * r.w[0][1] - (q[1] - r.mean[1]) * r.w[0][0], 0, 1e-12 * unit, `${name}: point ${i} off the line`);
      near((p[0] - q[0]) * r.w[0][0] + (p[1] - q[1]) * r.w[0][1], 0, 1e-12 * unit, `${name}: residual ${i} not orthogonal`);
    });
    const m = r.coords.reduce((s, v) => s + v, 0) / r.coords.length;
    const variance = r.coords.reduce((s, v) => s + (v - m) ** 2, 0) / (r.coords.length - 1);
    near(variance, r.lambda[0], 1e-11 * r.lambda[0], `${name}: variance of the coordinates`);
  }
  // fewer than two points or a round cloud: there is nothing to project on
  assert.deepEqual(la.pca2([[1, 2]]).projections, []);
  assert.deepEqual(la.pca2(cloud("round-square").pts).projections, []);
});

test("pca2 survives every degenerate cloud: no exception, no NaN where a number is promised", () => {
  for (const c of clouds) {
    const r = la.pca2(c.pts);
    assert.equal(r.n, c.pts.length, c.name);
    for (const v of [...r.mean, ...r.C, ...r.lambda]) assert.ok(Number.isFinite(v), `${c.name}: ${v}`);
    if (r.status === "ok") assert.ok(Number.isFinite(r.explained) && r.w.length === 2, c.name);
  }
  const empty = la.pca2([]);
  assert.deepEqual([empty.status, empty.w, empty.ols, empty.explained], ["zero", null, null, null]);
  const one = la.pca2([[3, -2]]);
  assert.deepEqual([one.status, one.w, one.ols, one.mean], ["zero", null, null, [3, -2]]);
  // two points: exactly one axis, the segment, and the second eigenvalue is zero
  const two = la.pca2([[1, 2], [4, 6]]);
  assert.equal(two.status, "ok");
  near(two.lambda[1], 0, 1e-14, "two points: lambda2");
  near(absdot(two.w[0], [0.6, 0.8]), 1, 1e-14, "two points: w1 along the segment");
  near(two.explained, 1, 1e-14, "two points: everything is explained");
  near(two.pc.perp, 0, 1e-14, "two points: no perpendiculars");
  // all points on a vertical line: the OLS line does not exist, the first component is the line itself
  const vert = la.pca2(cloud("line-vertical").pts);
  assert.equal(vert.ols, null);
  near(absdot(vert.w[0], [0, 1]), 1, 1e-14, "vertical line: w1");
  assert.equal(vert.pc.vert, null);
});

test("seededRandom is deterministic per seed and uniform in [0, 1)", () => {
  const a = la.seededRandom(7), b = la.seededRandom(7), c = la.seededRandom(8);
  const xa = Array.from({ length: 5 }, a), xb = Array.from({ length: 5 }, b), xc = Array.from({ length: 5 }, c);
  assert.deepEqual(xa, xb);
  assert.notDeepEqual(xa, xc);
  const u = la.seededRandom(1), v = Array.from({ length: 20000 }, u);
  assert.ok(v.every((t) => t >= 0 && t < 1));
  near(v.reduce((s, t) => s + t, 0) / v.length, 0.5, 0.01, "mean of uniform");
  near(v.reduce((s, t) => s + t * t, 0) / v.length, 1 / 3, 0.01, "second moment of uniform");
});

test("generateCloud: N points, the same cloud for the same seed, covariance R diag(sx^2 + s^2, sy^2 + s^2) R^T", () => {
  const spec = { n: 20000, sx: 3, sy: 1, angle: 30, noise: 0.5, seed: 11 };
  const pts = la.generateCloud(spec);
  assert.equal(pts.length, spec.n);
  assert.deepEqual(la.generateCloud(spec), pts);
  assert.notDeepEqual(la.generateCloud({ ...spec, seed: 12 }), pts);
  const r = la.pca2(pts);
  const t = Math.PI / 6, ex = spec.sx ** 2 + spec.noise ** 2, ey = spec.sy ** 2 + spec.noise ** 2;
  const want = [ex * Math.cos(t) ** 2 + ey * Math.sin(t) ** 2, (ex - ey) * Math.sin(t) * Math.cos(t), (ex - ey) * Math.sin(t) * Math.cos(t), ex * Math.sin(t) ** 2 + ey * Math.cos(t) ** 2];
  nearAll(r.C, want, 0.12, "covariance");
  nearAll(r.lambda, [ex, ey], 0.12, "lambda");
  near(absdot(r.w[0], [Math.cos(t), Math.sin(t)]), 1, 0.01, "axis along the rotation");
  assert.equal(la.generateCloud({ ...spec, n: 0 }).length, 0);
  // no stretching, no noise: the points collapse to the origin; a single stretch gives a line
  assert.ok(la.generateCloud({ n: 5, sx: 0, sy: 0, angle: 0, noise: 0, seed: 1 }).every((p) => p[0] === 0 && p[1] === 0));
  const line = la.pca2(la.generateCloud({ n: 50, sx: 2, sy: 0, angle: 45, noise: 0, seed: 3 }));
  near(line.lambda[1], 0, 1e-13, "a cloud stretched along one axis only lies on a line");
});
