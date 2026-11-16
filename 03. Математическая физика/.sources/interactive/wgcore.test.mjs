// wgcore.js against the python reference in fixtures.json (export_fixtures.py).
// Run: node --test wgcore.test.mjs
// Arrays are compared one element at a time with an early exit: assert.deepEqual on a large array once used 4 GB.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as wg from "./wgcore.js";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));

const near = (got, want, tol, what) => assert.ok(Math.abs(got - want) <= tol, `${what}: ${got} vs ${want}, tol ${tol}`);
const cabs = (re, im) => Math.hypot(re, im);

test("J_n(x) for real x matches scipy jv", () => {
  for (const c of fx.besselJ) {
    const got = wg.besselJ(c.n, c.x);
    near(got, c.v, 1e-13 * Math.abs(c.v) + 1e-15, `J_${c.n}(${c.x})`);
  }
});

test("K_n(x) matches scipy kv in relative error, from x = 1e-6 to 600", () => {
  for (const c of fx.besselK) {
    const got = wg.besselK(c.n, c.x);
    near(got / c.v, 1, 2e-13, `K_${c.n}(${c.x})`);
  }
});

test("J_n(z) for complex z matches scipy jv", () => {
  for (const c of fx.besselJc) {
    const [re, im] = wg.besselJc(c.n, [c.re, c.im]);
    const err = cabs(re - c.v[0], im - c.v[1]);
    const tol = 1e-12 * cabs(c.v[0], c.v[1]) + 5e-15 * c.scale;
    assert.ok(err <= tol, `J_${c.n}(${c.re}+${c.im}i): err ${err}, tol ${tol}`);
  }
});

test("H1_n(z) matches scipy hankel1 in relative error wherever Im z <= 0, where the leaky waves live", () => {
  let checked = 0;
  for (const c of fx.hankel1c) {
    if (c.im > 1e-9) continue;
    const [re, im] = wg.hankel1c(c.n, [c.re, c.im]);
    const err = cabs(re - c.v[0], im - c.v[1]);
    const tol = 1e-12 * cabs(c.v[0], c.v[1]);
    assert.ok(err <= tol, `H1_${c.n}(${c.re}+${c.im}i): err ${err}, tol ${tol}`);
    checked++;
  }
  assert.ok(checked > 300, `only ${checked} points checked`);
});

test("H1_n(z) in the upper half-plane is accurate up to the size of J and Y that cancel in J + iY", () => {
  for (const c of fx.hankel1c) {
    if (c.im <= 1e-9) continue;
    const [re, im] = wg.hankel1c(c.n, [c.re, c.im]);
    const err = cabs(re - c.v[0], im - c.v[1]);
    const tol = 1e-12 * cabs(c.v[0], c.v[1]) + 1e-14 * c.cond;
    assert.ok(err <= tol, `H1_${c.n}(${c.re}+${c.im}i): err ${err}, tol ${tol}`);
  }
});

test("zeros of J_n match scipy jn_zeros", () => {
  for (const [n, list] of Object.entries(fx.zeros)) {
    list.forEach((want, i) => near(wg.besselZero(+n, i + 1), want, 1e-12, `zero ${i + 1} of J_${n}`));
  }
});

test("cutoffs of the note: V_c = 0 and the first zeros of J_{m-1}", () => {
  const note = [0, 2.4048, 3.8317, 5.1356, 6.3802];
  note.forEach((want, m) => near(wg.cutoffV(m, 1), want, 5e-5, `V_c(m=${m})`));
  // the second mode of m = 0 and the first of m = 2 share the cutoff 3.8317, as the note says
  near(wg.cutoffV(0, 2), wg.cutoffV(2, 1), 1e-12, "common cutoff");
});

test("surface roots: the same count and values as scipy brentq on every (m, V)", () => {
  for (const c of fx.surface) {
    const got = wg.surfaceRoots(c.m, c.V);
    assert.equal(got.length, c.roots.length, `m=${c.m} V=${c.V}: count ${got.length} vs ${c.roots.length}`);
    c.roots.forEach((want, i) => {
      near(got[i].lambda, want, 1e-10, `m=${c.m} V=${c.V} root ${i + 1}`);
      near(got[i].kappa / c.kappas[i], 1, 1e-8, `m=${c.m} V=${c.V} kappa ${i + 1}`);
    });
  }
});

test("surface roots at V = 8 are the table of the note and kappa = sqrt(V^2 - lambda^2)", () => {
  const lam = [2.1346, 3.3943, 4.5383, 5.6215, 6.6616];
  const kap = [7.710, 7.244, 6.588, 5.692, 4.430];
  lam.forEach((want, m) => {
    const r = wg.surfaceRoots(m, 8)[0];
    near(r.lambda, want, 5e-5, `lambda m=${m}`);
    near(r.kappa, kap[m], 5e-4, `kappa m=${m}`);
    near(r.kappa, Math.sqrt(64 - r.lambda ** 2), 1e-9, `kappa from lambda m=${m}`);
  });
});

test("m = 0 has a surface root at every V, however small, and m >= 1 none below its cutoff", () => {
  for (const V of [0.1, 0.3, 0.5, 1, 2.3]) {
    const r = wg.surfaceRoots(0, V);
    assert.ok(r.length >= 1, `m=0 V=${V}`);
    // below V = 0.5 the kappa of the root is smaller than 1e-3 and lambda equals V to double precision
    assert.ok(r[0].lambda <= V && r[0].kappa > 0, `m=0 V=${V}: lambda ${r[0].lambda}, kappa ${r[0].kappa}`);
  }
  for (let m = 1; m <= 4; m++) {
    assert.equal(wg.surfaceRoots(m, wg.cutoffV(m, 1) - 0.01).length, 0, `m=${m} below cutoff`);
    assert.equal(wg.surfaceRoots(m, wg.cutoffV(m, 1) + 0.01).length, 1, `m=${m} above cutoff`);
  }
});

test("leaky roots match the mpmath determinant roots followed from the note's seed", () => {
  for (const c of fx.leaky) {
    const r = wg.leakyRoot(c.m, c.V);
    assert.ok(r, `m=${c.m} V=${c.V}: no root`);
    const err = cabs(r.lambda[0] - c.lam[0], r.lambda[1] - c.lam[1]);
    assert.ok(err <= 1e-10, `m=${c.m} V=${c.V}: ${r.lambda} vs ${c.lam}, err ${err}`);
  }
});

test("leaky roots at V = 0.5 are the table of the note", () => {
  const note = { 1: [1.0390, -2.5570], 2: [2.6045, -3.1443], 3: [3.9714, -3.5854], 4: [5.2568, -3.9493] };
  for (const [m, want] of Object.entries(note)) {
    const r = wg.leakyRoot(+m, 0.5);
    near(r.lambda[0], want[0], 6e-5, `Re lambda m=${m}`);
    near(r.lambda[1], want[1], 6e-5, `Im lambda m=${m}`);
  }
  const a = wg.leakyRoot(1, 0.5).alpha;
  near(a[0], 1.022, 1e-3, "Re alpha m=1");
  near(a[1], -2.599, 1e-3, "Im alpha m=1");
});

test("a leaky root has Re alpha > 0 and Im alpha < 0, and exists only below the cutoff and for m >= 1", () => {
  for (let m = 1; m <= 4; m++) {
    const vc = wg.cutoffV(m, 1);
    for (const V of [0.1, 0.5, 1, vc - 0.5, vc - 0.05]) {
      const r = wg.leakyRoot(m, V);
      assert.ok(r.alpha[0] > 0 && r.alpha[1] < 0, `m=${m} V=${V}: alpha ${r.alpha}`);
    }
    assert.equal(wg.leakyRoot(m, vc + 0.01), null, `m=${m} above cutoff`);
  }
  assert.equal(wg.leakyRoot(0, 0.5), null);
});

test("the leaky root is continuous in V and joins the cutoff: no jump to another root", () => {
  for (let m = 1; m <= 4; m++) {
    const vc = wg.cutoffV(m, 1);
    let prev = null;
    const N = 400;
    for (let i = 1; i < N; i++) {
      const V = 0.1 + (vc - 0.1) * (i / N) * 0.999;
      const r = wg.leakyRoot(m, V);
      if (prev) {
        const step = cabs(r.lambda[0] - prev.lambda[0], r.lambda[1] - prev.lambda[1]);
        assert.ok(step < 0.2, `m=${m} V=${V}: jump ${step}`);
      }
      prev = r;
    }
    // at the cutoff the root meets lambda = V_c with a vanishing imaginary part
    const end = wg.leakyRoot(m, vc - 1e-3);
    near(end.lambda[0], vc, 0.02, `m=${m}: Re lambda near cutoff`);
    near(end.lambda[1], 0, 0.02, `m=${m}: Im lambda near cutoff`);
  }
});

test("the surface curve passes through the scipy roots of n = 1 and starts at the cutoff", () => {
  for (let m = 0; m <= 4; m++) {
    const c = wg.surfaceCurve(m, 15);
    near(c.V[0], wg.cutoffV(m, 1), 1e-12, `m=${m}: first point is the cutoff`);
    for (let i = 1; i < c.V.length; i++) {
      assert.ok(c.V[i] > c.V[i - 1] && c.lambda[i] >= c.lambda[i - 1], `m=${m}: monotone at ${i}`);
      assert.ok(c.lambda[i] <= c.V[i] * (1 + 1e-12), `m=${m}: lambda <= V at ${i}`);
    }
    for (const f of fx.surface) {
      if (f.m !== m || f.roots.length === 0 || f.V > 15 || f.V < c.V[1] || f.V > c.V[c.V.length - 1]) continue;
      let i = 1;
      while (c.V[i] < f.V) i++;
      const t = (f.V - c.V[i - 1]) / (c.V[i] - c.V[i - 1]);
      const lam = c.lambda[i - 1] + t * (c.lambda[i] - c.lambda[i - 1]);
      near(lam, f.roots[0], 5e-3, `m=${m} V=${f.V}: curve vs scipy n=1`);
    }
  }
});

test("beta and n_eff of the circular mode: the numbers of the note at V = 8 and V = 0.5", () => {
  const epsI = 2.3839;
  const epsE = 2.2124;
  const beta8 = [29.750, 29.633, 29.479, 29.292, 29.073];
  for (let m = 0; m <= 4; m++) {
    const md = wg.circularMode(m, 1, 8, epsI, epsE);
    assert.equal(md.type, "surface", `m=${m}`);
    near(md.k, 19.318, 5e-4, "k");
    near(md.beta[0], beta8[m], 6e-4, `beta m=${m}`);
    assert.equal(md.beta[1], 0);
    assert.ok(md.neff[0] > Math.sqrt(epsE) && md.neff[0] < Math.sqrt(epsI), `m=${m}: n_eff between the cladding and the core`);
  }
  const m1 = wg.circularMode(1, 1, 0.5, epsI, epsE);
  assert.equal(m1.type, "leaky");
  near(m1.beta[0], 3.109, 1e-3, "Re beta m=1");
  near(m1.beta[1], 0.855, 1e-3, "Im beta m=1");
  const m4 = wg.circularMode(4, 1, 0.5, epsI, epsE);
  near(m4.beta[0], 4.113, 1e-3, "Re beta m=4");
  near(m4.beta[1], 5.048, 1e-3, "Im beta m=4");
  assert.ok(m4.beta[1] > 0, "a leaky wave decays along the axis: Im beta > 0");
  assert.equal(wg.circularMode(0, 1, 0.5, epsI, epsE).type, "surface");
  assert.equal(wg.circularMode(3, 2, 3, epsI, epsE), null, "no second mode");
});

test("cutoff wavenumbers k_c = V_c / sqrt(eps_i - eps_e) of the note", () => {
  const kc = [0, 5.807, 9.253, 12.401, 15.406];
  const d = Math.sqrt(2.3839 - 2.2124);
  kc.forEach((want, m) => near(wg.cutoffV(m, 1) / d, want, 1e-3, `k_c m=${m}`));
});

// the derivative of the field on each side of r = 1, by a one-sided difference of second order
function sidedDerivative(md, side) {
  const h = 1e-4;
  const at = (r) => wg.circularField(md, r);
  const s = side;
  const f0 = at(1);
  const f1 = at(1 + s * h);
  const f2 = at(1 + 2 * s * h);
  return [0, 1].map((i) => (-3 * f0[i] + 4 * f1[i] - f2[i]) / (2 * s * h));
}

test("the field of the mode is continuous with its derivative at r = 1: the roots solve the matching conditions", () => {
  const cases = [[0, 8], [1, 8], [2, 8], [3, 8], [4, 8], [1, 0.5], [2, 1.5], [3, 3], [4, 0.5], [1, 2.2], [0, 0.5], [2, 12]];
  for (const [m, V] of cases) {
    const md = wg.circularMode(m, 1, V, 2.3839, 2.2124);
    assert.ok(md, `m=${m} V=${V}`);
    const inside = wg.circularField(md, 1 - 1e-12);
    const outside = wg.circularField(md, 1 + 1e-12);
    near(inside[0], outside[0], 1e-9, `m=${m} V=${V}: Re u`);
    near(inside[1], outside[1], 1e-9, `m=${m} V=${V}: Im u`);
    const dIn = sidedDerivative(md, -1);
    const dOut = sidedDerivative(md, 1);
    near(dIn[0], dOut[0], 1e-5 * (1 + Math.abs(dOut[0])), `m=${m} V=${V}: Re du/dr`);
    near(dIn[1], dOut[1], 1e-5 * (1 + Math.abs(dOut[1])), `m=${m} V=${V}: Im du/dr`);
  }
});

test("circularProfile is circularField at every r, and u(0) = 0 for m >= 1", () => {
  const rs = [0, 0.3, 1, 1.7, 2.5];
  for (const [m, V] of [[0, 8], [2, 0.5], [3, 6]]) {
    const md = wg.circularMode(m, 1, V, 2.3839, 2.2124);
    const prof = wg.circularProfile(md, rs);
    rs.forEach((r, i) => {
      const f = wg.circularField(md, r);
      near(prof[i][0], f[0], 0, `m=${m} r=${r}: re`);
      near(prof[i][1], f[1], 0, `m=${m} r=${r}: im`);
    });
    if (m >= 1) near(Math.hypot(...prof[0]), 0, 1e-12, `m=${m}: u(0)`);
    else near(prof[0][0], 1 / wg.besselJ(0, md.lambda[0]), 1e-12, "m=0: u(0) = 1/J_0(lambda)");
  }
});

test("outside the core a surface wave decays and a leaky wave grows as exp(|Im alpha| r)", () => {
  const surf = wg.circularMode(1, 1, 8, 2.3839, 2.2124);
  let prev = Math.abs(wg.circularField(surf, 1)[0]);
  for (const r of [1.2, 1.5, 2, 3]) {
    const v = Math.abs(wg.circularField(surf, r)[0]);
    assert.ok(v < prev, `surface wave at r=${r}`);
    prev = v;
  }
  const leaky = wg.circularMode(1, 1, 0.5, 2.3839, 2.2124);
  const a = Math.hypot(...wg.circularField(leaky, 2));
  const b = Math.hypot(...wg.circularField(leaky, 3));
  // |H(alpha r)| ~ exp(|Im alpha| r) / sqrt(r)
  const rate = Math.log((b * Math.sqrt(3)) / (a * Math.sqrt(2)));
  near(rate, -leaky.alpha[1], 5e-2, "growth rate between r=2 and r=3");
  assert.ok(b > a, "a leaky wave grows");
});

// ---------------------------------------------------------------- symmetric planar waveguide

test("symmetric planar: roots, n_eff and the number of modes against brentq on the trigonometric forms", () => {
  for (const c of fx.sym) {
    for (const pol of ["TE", "TM"]) {
      const want = c[pol];
      const got = wg.symModes(c.n1, c.n2, c.lam0, c.d, pol);
      near(got.V, want.V, 1e-12 * want.V, "V");
      assert.equal(got.M, want.M, `M for d=${c.d}`);
      assert.equal(got.modes.length, want.modes.length, `${pol} d=${c.d}: number of modes`);
      want.modes.forEach((w, i) => {
        const g = got.modes[i];
        assert.equal(g.j, w.j);
        near(g.X, w.X, 1e-11, `${pol} d=${c.d} j=${w.j}: X`);
        near(g.Y, w.Y, 1e-9, `${pol} d=${c.d} j=${w.j}: Y`);
        near(g.neff, w.neff, 1e-12, `${pol} d=${c.d} j=${w.j}: n_eff`);
      });
    }
  }
});

test("symmetric planar: the table of the note for n1 = 1.45, n2 = 1.44, 1.55 um, d = 16 um", () => {
  const te = [1.4498301, 1.4493211, 1.4484760, 1.4473004, 1.4458050, 1.4440107, 1.4419697, 1.4400071];
  const tm = [1.4498297, 1.4493196, 1.4484728, 1.4472952, 1.4457978, 1.4440024, 1.4419623, 1.4400069];
  const kd = [1.4398, 2.8776, 4.3107, 5.7361, 7.1486, 8.5389, 9.8839, 11.0221];
  const gd = [10.9316, 10.6439, 10.1484, 9.4165, 8.3946, 6.9756, 4.8867, 0.2924];
  const a = wg.symModes(1.45, 1.44, 1.55, 16, "TE");
  const b = wg.symModes(1.45, 1.44, 1.55, 16, "TM");
  near(a.V, 11.03, 5e-3, "V");
  assert.equal(a.modes.length, 8);
  assert.equal(b.modes.length, 8);
  te.forEach((w, j) => {
    near(a.modes[j].neff, w, 6e-8, `TE${j}`);
    near(b.modes[j].neff, tm[j], 6e-8, `TM${j}`);
    near(a.modes[j].X, kd[j], 6e-5, `kappa d TE${j}`);
    near(a.modes[j].Y, gd[j], 6e-5, `gamma d TE${j}`);
    assert.ok(b.modes[j].neff < a.modes[j].neff, `n_eff of TM${j} below TE${j}`);
  });
});

test("symmetric planar: a new mode appears at V = j pi / 2 and the number of modes is floor(2V / pi) + 1 away from the thresholds", () => {
  // n1 = sqrt(2), n2 = 1, lambda0 = 2 pi: V = d
  const modes = (V) => wg.symModes(Math.SQRT2, 1, 2 * Math.PI, V, "TE").modes.length;
  for (let j = 1; j <= 8; j++) {
    const t = j * Math.PI / 2;
    assert.equal(modes(t - 1e-6), j, `just below ${j} pi/2`);
    assert.equal(modes(t + 1e-6), j + 1, `just above ${j} pi/2`);
  }
  assert.equal(modes(0.01), 1, "the fundamental mode exists at any V");
  assert.equal(wg.symModes(Math.SQRT2, 1, 2 * Math.PI, Math.PI / 2 + 1e-6, "TE").modes[1].Y < 1e-5, true, "the new mode is born with gamma d ~ 0");
});

test("symmetric planar: the field is continuous at x = d, so is dE/dx (TE) and (1/n^2) dH/dx (TM), and mode j has j zeros", () => {
  for (const pol of ["TE", "TM"]) {
    const s = wg.symModes(1.45, 1.44, 1.55, 16, pol);
    for (const m of s.modes) {
      const f = (x) => wg.symField(m, x);
      near(f(1 - 1e-12), f(1 + 1e-12), 1e-9, `${pol}${m.j}: field at d`);
      const h = 1e-6;
      const dIn = (f(1 - 2 * h) - 4 * f(1 - h) + 3 * f(1)) / (2 * h);
      const dOut = (-3 * f(1) + 4 * f(1 + h) - f(1 + 2 * h)) / (2 * h);
      const w1 = pol === "TM" ? 1 / 1.45 ** 2 : 1;
      const w2 = pol === "TM" ? 1 / 1.44 ** 2 : 1;
      near(w1 * dIn, w2 * dOut, 1e-5, `${pol}${m.j}: derivative at d`);
      let zeros = 0;
      let prev = f(-0.9999);
      // an odd number of samples would put one exactly on the zero at x = 0, where the product of signs is 0
      for (let i = 1; i <= 4001; i++) {
        const cur = f(-0.9999 + (1.9998 * i) / 4001);
        if (prev * cur < 0) zeros++;
        prev = cur;
      }
      assert.equal(zeros, m.j, `${pol}${m.j}: zeros in the core`);
    }
  }
});

test("symmetric planar: curves of the graphical solution pass through the circle at the roots", () => {
  const s = wg.symModes(3.5, 1.45, 1.55, 0.25, "TM");
  const curves = wg.symCurves(s.V, s.q);
  assert.equal(curves.length, s.modes.length);
  for (const m of s.modes) {
    const c = curves[m.j];
    assert.equal(c.parity, m.parity);
    // the polyline of the branch, read at the abscissa X of the root, gives the Y of the root
    let i = 1;
    while (c.pts[i][0] < m.X) i++;
    const [x0, y0] = c.pts[i - 1];
    const [x1, y1] = c.pts[i];
    const y = y0 + (y1 - y0) * (m.X - x0) / (x1 - x0);
    near(y, m.Y, 2e-3 * (1 + m.Y), `TM${m.j}: Y on the curve`);
    near(Math.hypot(m.X, m.Y), s.V, 1e-12 * s.V, "on the circle");
  }
});

// ---------------------------------------------------------------- asymmetric planar waveguide

const near1 = (got, want, tol, what) => assert.ok(Math.abs(got - want) <= tol, `${what}: ${got} vs ${want}, tol ${tol}`);

test("asymmetric planar: n_eff of every mode against the scan of F with brentq, TE and TM", () => {
  for (const c of fx.asym) {
    for (const pol of ["TE", "TM"]) {
      const got = wg.asymModes(c.na, c.nf, c.ns, c.lam0, c.h, pol).modes;
      const want = c[pol].modes;
      assert.equal(got.length, want.length, `${c.name} ${pol}: number of modes`);
      want.forEach((w, i) => {
        assert.equal(got[i].j, w.j);
        near1(got[i].neff, w.neff, 1e-12, `${c.name} ${pol} j=${w.j}`);
      });
    }
  }
});

test("asymmetric planar: thickness of cutoff against the bisection on the existence of a mode", () => {
  for (const c of fx.asym) {
    for (const pol of ["TE", "TM"]) {
      c[pol].hc.forEach((want, j) => {
        const got = wg.asymCutoffThickness(j, c.na, c.nf, c.ns, c.lam0, pol);
        // bisection starts from 1e-3 um: a mode without a cutoff comes back as that bound
        near1(got, want, j === 0 && c.na === c.ns ? 2e-3 : 1e-9 * (1 + want), `${c.name} ${pol} j=${j}`);
      });
    }
  }
});

test("asymmetric planar: the mode j exists exactly above h_c(j), as in the exercise of the note (h_c +- 0.01 um)", () => {
  for (const [name, args] of [["weak", [1.44, 1.45, 1.44, 1.55]], ["strong", [1.0, 3.6, 3.4, 0.6328]]]) {
    for (const pol of ["TE", "TM"]) {
      for (let j = 1; j <= 3; j++) {
        const hc = wg.asymCutoffThickness(j, ...args, pol);
        const below = wg.asymModes(...args, hc - 0.01, pol).modes.length;
        const above = wg.asymModes(...args, hc + 0.01, pol).modes.length;
        assert.equal(below, j, `${name} ${pol} j=${j}: below cutoff`);
        assert.equal(above, j + 1, `${name} ${pol} j=${j}: above cutoff`);
      }
    }
  }
  near1(wg.asymCutoffThickness(1, 1.44, 1.45, 1.44, 1.55, "TE"), 4.559, 5e-4, "h_c(1), weak");
  assert.equal(wg.asymCutoffThickness(0, 1.44, 1.45, 1.44, 1.55, "TE"), 0, "no cutoff of the fundamental mode at n_a = n_s");
});

test("asymmetric planar: the tables of the note, weak and strong", () => {
  const weakTE = [1.449830, 1.449321, 1.448476, 1.447300, 1.445805, 1.444011, 1.441970, 1.440007];
  const weakTM = [1.449830, 1.449320, 1.448473, 1.447295, 1.445798, 1.444002, 1.441962, 1.440007];
  const te = wg.asymModes(1.44, 1.45, 1.44, 1.55, 32, "TE").modes;
  const tm = wg.asymModes(1.44, 1.45, 1.44, 1.55, 32, "TM").modes;
  assert.equal(te.length, 8);
  assert.equal(tm.length, 8);
  weakTE.forEach((w, j) => {
    near1(te[j].neff, w, 6e-7, `weak TE${j}`);
    near1(tm[j].neff, weakTM[j], 6e-7, `weak TM${j}`);
    assert.ok(tm[j].neff <= te[j].neff, `weak: n_eff of TM${j} does not exceed TE${j}`);
  });
  const sTE = [3.5906, 3.5623, 3.5152, 3.4505];
  const sTM = [3.5900, 3.5600, 3.5103, 3.4428];
  const hcTE = [0.1040, 0.3714, 0.6388, 0.9062, 1.1736];
  const hcTM = [0.1313, 0.3987, 0.6661, 0.9335, 1.2009];
  const a = wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TE").modes;
  const b = wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TM").modes;
  assert.equal(a.length, 4);
  assert.equal(b.length, 4);
  sTE.forEach((w, j) => {
    near1(a[j].neff, w, 6e-5, `strong TE${j}`);
    near1(b[j].neff, sTM[j], 6e-5, `strong TM${j}`);
  });
  hcTE.forEach((w, j) => near1(wg.asymCutoffThickness(j, 1.0, 3.6, 3.4, 0.6328, "TE"), w, 6e-5, `h_c TE${j}`));
  hcTM.forEach((w, j) => near1(wg.asymCutoffThickness(j, 1.0, 3.6, 3.4, 0.6328, "TM"), w, 6e-5, `h_c TM${j}`));
});

test("asymmetric planar: confinement factor against scipy quad of the profile from the null vector of the matching conditions", () => {
  for (const c of fx.asym) {
    for (const pol of ["TE", "TM"]) {
      const modes = wg.asymModes(c.na, c.nf, c.ns, c.lam0, c.h, pol).modes;
      c[pol].modes.forEach((w, i) => near1(wg.asymConfinement(modes[i]), w.gamma, 1e-9, `${c.name} ${pol} j=${w.j}`));
    }
  }
  near1(wg.asymConfinement(wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TE").modes[0]), 0.9964, 5e-5, "note: TE0 strong");
  near1(wg.asymConfinement(wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TM").modes[0]), 0.9969, 5e-5, "note: TM0 strong");
  near1(wg.asymConfinement(wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TE").modes[3]), 0.899, 5e-4, "note: TE3 strong");
  near1(wg.asymConfinement(wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TM").modes[3]), 0.891, 5e-4, "note: TM3 strong");
  near1(wg.asymConfinement(wg.asymModes(1.44, 1.45, 1.44, 1.55, 10, "TE").modes[0]), 0.971, 5e-4, "note: TE0 weak h=10");
  near1(wg.asymConfinement(wg.asymModes(1.44, 1.45, 1.44, 1.55, 32, "TE").modes[0]), 0.9986, 5e-5, "note: TE0 weak h=32");
});

test("asymmetric planar: the profile matches the null vector of the four matching conditions, up to a factor", () => {
  for (const c of fx.asym) {
    for (const pol of ["TE", "TM"]) {
      const modes = wg.asymModes(c.na, c.nf, c.ns, c.lam0, c.h, pol).modes;
      c[pol].modes.forEach((w, i) => {
        assert.ok(w.profile_check < 1e-9, `${c.name} ${pol} j=${w.j}: reference does not satisfy the conditions`);
        let k = 0;
        w.f.forEach((v, t) => { if (Math.abs(v) > Math.abs(w.f[k])) k = t; });
        const ours = c[pol].zs.map((z) => wg.asymField(modes[i], z));
        const scale = ours[k] / w.f[k];
        for (let t = 0; t < ours.length; t++) near1(ours[t], scale * w.f[t], 1e-8 * Math.abs(ours[k]), `${c.name} ${pol} j=${w.j} z[${t}]`);
      });
    }
  }
});

test("asymmetric planar: profile of mode j has j zeros in the film, and no mode exists when the film is not the densest", () => {
  const modes = wg.asymModes(1.0, 3.6, 3.4, 0.6328, 1.1, "TE").modes;
  modes.forEach((m) => {
    let zeros = 0;
    let prev = wg.asymField(m, 1e-9);
    for (let i = 1; i <= 4000; i++) {
      const cur = wg.asymField(m, 1.1 * (i / 4000));
      if (prev * cur < 0) zeros++;
      prev = cur;
    }
    assert.equal(zeros, m.j, `TE${m.j}`);
  });
  assert.equal(wg.asymModes(1.5, 1.45, 1.44, 1.55, 30, "TE").modes.length, 0, "the film is rarer than the cover");
  assert.equal(wg.asymModes(1.44, 1.44, 1.44, 1.55, 30, "TE").modes.length, 0, "no contrast, no mode");
});
