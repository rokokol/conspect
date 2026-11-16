// Pure functions behind the waveguide sandbox: Bessel functions of a real and a complex argument,
// the roots of the characteristic equation of a round weakly guiding waveguide (surface and leaky),
// and the symmetric and the asymmetric planar waveguide. No DOM, no globals: an ES module for the
// page (build_pages.py strips `export`) and for node --test (wgcore.test.mjs).
// A complex number is a pair [re, im].

const GAMMA = 0.5772156649015328606;
const TWO_OVER_PI = 2 / Math.PI;

// ---------------------------------------------------------------- complex arithmetic

const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const cdiv = (a, b) => {
  const d = b[0] * b[0] + b[1] * b[1];
  return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
};
const cabs = (a) => Math.hypot(a[0], a[1]);
// Principal square root: Re >= 0, and Im has the sign of the argument's Im.
function csqrt(a) {
  const r = Math.hypot(a[0], a[1]);
  if (r === 0) return [0, 0];
  const re = Math.sqrt((r + Math.abs(a[0])) / 2);
  const im = a[1] / (2 * re);
  return a[0] >= 0 ? [re, im] : [Math.abs(im), a[1] >= 0 ? re : -re];
}
const clog = (a) => [Math.log(Math.hypot(a[0], a[1])), Math.atan2(a[1], a[0])];
const cexp = (a) => {
  const e = Math.exp(a[0]);
  return [e * Math.cos(a[1]), e * Math.sin(a[1])];
};

// ---------------------------------------------------------------- root finding

// Brent's method for a real function with a sign change on [a, b]; null when there is none.
export function brent(f, a, b, tol = 1e-15, maxIter = 200) {
  let fa = f(a);
  let fb = f(b);
  if (fa === 0) return a;
  if (fb === 0) return b;
  if (fa * fb > 0) return null;
  let c = a;
  let fc = fa;
  let d = b - a;
  let e = d;
  for (let i = 0; i < maxIter; i++) {
    if (fb * fc > 0) {
      c = a; fc = fa; d = b - a; e = d;
    }
    if (Math.abs(fc) < Math.abs(fb)) {
      a = b; b = c; c = a; fa = fb; fb = fc; fc = fa;
    }
    const tol1 = 2 * 2.220446049250313e-16 * Math.abs(b) + 0.5 * tol;
    const xm = 0.5 * (c - b);
    if (Math.abs(xm) <= tol1 || fb === 0) return b;
    if (Math.abs(e) >= tol1 && Math.abs(fa) > Math.abs(fb)) {
      const s = fb / fa;
      let p;
      let q;
      if (a === c) {
        p = 2 * xm * s;
        q = 1 - s;
      } else {
        const qq = fa / fc;
        const r = fb / fc;
        p = s * (2 * xm * qq * (qq - r) - (b - a) * (r - 1));
        q = (qq - 1) * (r - 1) * (s - 1);
      }
      if (p > 0) q = -q;
      p = Math.abs(p);
      if (2 * p < Math.min(3 * xm * q - Math.abs(tol1 * q), Math.abs(e * q))) {
        e = d;
        d = p / q;
      } else {
        d = xm;
        e = d;
      }
    } else {
      d = xm;
      e = d;
    }
    a = b;
    fa = fb;
    b += Math.abs(d) > tol1 ? d : (xm > 0 ? tol1 : -tol1);
    fb = f(b);
  }
  return b;
}

// ---------------------------------------------------------------- J_n and Y_n of a complex argument
//
// J_0..J_N: a power series for |z| < 2, otherwise Miller's backward recurrence. The recurrence gives the
// ratios; the scale comes from the generating function at t = -+i, e^{iz} = J_0 + 2 sum i^n J_n, taken with
// the sign for which |e^{+-iz}| = e^{|Im z|} is the large one. The usual 1 = J_0 + 2 sum J_2k would add
// terms of size e^{|Im z|} to get 1 and lose that many digits. Y_0 and Y_1 come from the Neumann series
// (Abramowitz-Stegun 9.1.88 and its derivative) in the J_2k, Y_n for n >= 2 from the upward recurrence.

function jSeries(zr, zi, N) {
  const jr = new Float64Array(N + 1);
  const ji = new Float64Array(N + 1);
  const hr = zr / 2;
  const hi = zi / 2;
  // q = -(z/2)^2
  const qr = -(hr * hr - hi * hi);
  const qi = -2 * hr * hi;
  let pr = 1; // (z/2)^n / n!
  let pi = 0;
  for (let n = 0; n <= N; n++) {
    if (n > 0) {
      const nr = (pr * hr - pi * hi) / n;
      const ni = (pr * hi + pi * hr) / n;
      pr = nr; pi = ni;
    }
    let sr = pr;
    let si = pi;
    let tr = pr;
    let ti = pi;
    for (let k = 1; k < 60; k++) {
      const nr = (tr * qr - ti * qi) / (k * (n + k));
      const ni = (tr * qi + ti * qr) / (k * (n + k));
      tr = nr; ti = ni;
      sr += tr; si += ti;
      if (Math.abs(tr) + Math.abs(ti) <= 1e-18 * (Math.abs(sr) + Math.abs(si))) break;
    }
    jr[n] = sr; ji[n] = si;
  }
  return { jr, ji, N };
}

function jMiller(zr, zi, nmax) {
  const az = Math.hypot(zr, zi);
  let N = Math.ceil(1.4 * az + 40);
  if (N < nmax + 20) N = nmax + 20;
  if (N % 2) N++;
  const jr = new Float64Array(N + 2);
  const ji = new Float64Array(N + 2);
  const d = zr * zr + zi * zi;
  const cr = 2 * zr / d; // 2 / z
  const ci = -2 * zi / d;
  jr[N] = 1;
  for (let n = N; n >= 1; n--) {
    const fr = n * cr;
    const fi = n * ci;
    const ar = fr * jr[n] - fi * ji[n] - jr[n + 1];
    const ai = fr * ji[n] + fi * jr[n] - ji[n + 1];
    jr[n - 1] = ar; ji[n - 1] = ai;
    if (Math.abs(ar) + Math.abs(ai) > 1e250) {
      for (let k = n - 1; k <= N + 1; k++) { jr[k] *= 1e-250; ji[k] *= 1e-250; }
    }
  }
  // scale: sum_n w^n J_n (n >= 1 doubled) = e^{i s z}, with s = +1 and w = i for Im z <= 0, else s = -1, w = -i
  const s = zi <= 0 ? 1 : -1;
  let sr = jr[0];
  let si = ji[0];
  let wr = 1;
  let wi = 0;
  for (let n = 1; n <= N; n++) {
    const nr = -s * wi; // multiply (wr, wi) by (0, s)
    const ni = s * wr;
    wr = nr; wi = ni;
    sr += 2 * (wr * jr[n] - wi * ji[n]);
    si += 2 * (wr * ji[n] + wi * jr[n]);
  }
  const e = cexp([-s * zi, s * zr]);
  const f = cdiv(e, [sr, si]);
  for (let n = 0; n <= N; n++) {
    const a = jr[n];
    const b = ji[n];
    jr[n] = a * f[0] - b * f[1];
    ji[n] = a * f[1] + b * f[0];
  }
  return { jr, ji, N };
}

function jSequence(zr, zi, nmax) {
  return Math.hypot(zr, zi) < 2 ? jSeries(zr, zi, Math.max(nmax + 2, 26)) : jMiller(zr, zi, nmax);
}

// J_0..J_nmax and Y_0..Y_nmax at z, z != 0 and |arg z| < pi.
function besselJY(z, nmax) {
  const [zr, zi] = z;
  const { jr, ji, N } = jSequence(zr, zi, Math.max(nmax, 1));
  const lz = clog([zr / 2, zi / 2]);
  const l = [lz[0] + GAMMA, lz[1]];
  // sums over k of (-1)^k J_2k / k and of (-1)^k (J_2k-1 - J_2k+1) / k
  let s0r = 0;
  let s0i = 0;
  let s1r = 0;
  let s1i = 0;
  for (let k = 1; 2 * k + 1 <= N; k++) {
    const sg = k % 2 ? -1 : 1;
    s0r += sg * jr[2 * k] / k;
    s0i += sg * ji[2 * k] / k;
    s1r += sg * (jr[2 * k - 1] - jr[2 * k + 1]) / k;
    s1i += sg * (ji[2 * k - 1] - ji[2 * k + 1]) / k;
  }
  const yr = new Float64Array(nmax + 1);
  const yi = new Float64Array(nmax + 1);
  const l0 = cmul(l, [jr[0], ji[0]]);
  yr[0] = TWO_OVER_PI * l0[0] - 2 * TWO_OVER_PI * s0r;
  yi[0] = TWO_OVER_PI * l0[1] - 2 * TWO_OVER_PI * s0i;
  if (nmax >= 1) {
    const l1 = cmul(l, [jr[1], ji[1]]);
    const q = cdiv([jr[0], ji[0]], [zr, zi]);
    yr[1] = TWO_OVER_PI * (-q[0] + l1[0] + s1r);
    yi[1] = TWO_OVER_PI * (-q[1] + l1[1] + s1i);
  }
  const c = cdiv([2, 0], [zr, zi]);
  for (let n = 1; n < nmax; n++) {
    const t = cmul([n * c[0], n * c[1]], [yr[n], yi[n]]);
    yr[n + 1] = t[0] - yr[n - 1];
    yi[n + 1] = t[1] - yi[n - 1];
  }
  return { jr, ji, yr, yi };
}

// J_n(z) for an integer n >= 0 and complex z
export function besselJc(n, z) {
  if (z[0] === 0 && z[1] === 0) return n === 0 ? [1, 0] : [0, 0];
  const { jr, ji } = jSequence(z[0], z[1], n);
  return [jr[n], ji[n]];
}

// Y_n(z)
export function besselYc(n, z) {
  const { yr, yi } = besselJY(z, n);
  return [yr[n], yi[n]];
}

// H1_n(z) = J_n(z) + i Y_n(z)
export function hankel1c(n, z) {
  const { jr, ji, yr, yi } = besselJY(z, n);
  return [jr[n] - yi[n], ji[n] + yr[n]];
}

// J_n(x) for real x >= 0
export function besselJ(n, x) {
  if (x === 0) return n === 0 ? 1 : 0;
  return besselJc(n, [x, 0])[0];
}

// ---------------------------------------------------------------- K_n of a real argument
//
// e^x K_nu(x) = integral over t >= 0 of exp(-x (cosh t - 1)) cosh(nu t), for nu = 0 and 1 by the trapezoid rule
// (spectrally accurate: the error is about exp(-pi^2 / h) while h <= 0.55 / sqrt(x)). Higher orders and the ratios
// K_{n+1}/K_n come from the upward recurrence, which is stable for K and cannot overflow in the ratio form.

function kScaled01(x) {
  const h = Math.min(0.25, 0.55 / Math.sqrt(x));
  const tmax = Math.acosh(1 + 760 / x);
  let s0 = 0.5;
  let s1 = 0.5;
  for (let t = h; t <= tmax; t += h) {
    const sh = Math.sinh(t / 2);
    const w = Math.exp(-2 * x * sh * sh);
    s0 += w;
    s1 += w * Math.cosh(t);
  }
  return [s0 * h, s1 * h];
}

// e^x K_n(x)
export function besselKscaled(n, x) {
  const [k0, k1] = kScaled01(x);
  if (n === 0) return k0;
  let a = k0;
  let b = k1;
  for (let j = 1; j < n; j++) {
    const c = a + (2 * j / x) * b;
    a = b; b = c;
  }
  return b;
}

export function besselK(n, x) {
  return besselKscaled(n, x) * Math.exp(-x);
}

// x K_{m+1}(x) / K_m(x): increases from 2m (from 0 for m = 0) to infinity
export function kappaRatio(m, x) {
  const [k0, k1] = kScaled01(x);
  let r = k1 / k0; // K_1 / K_0
  for (let j = 1; j <= m; j++) r = 1 / r + 2 * j / x; // K_{j+1} / K_j = K_{j-1} / K_j + 2 j / x
  return x * r;
}

// ---------------------------------------------------------------- zeros of J_n, cutoffs

// s-th positive zero of J_n, found by a scan for the sign change from n upward and Brent's method
export function besselZero(n, s) {
  let a = Math.max(n, 0.05);
  let fa = besselJ(n, a);
  let count = 0;
  const step = 0.05;
  for (let i = 0; i < 100000; i++) {
    const b = a + step;
    const fb = besselJ(n, b);
    if (fa * fb < 0 && ++count === s) return brent((x) => besselJ(n, x), a, b, 1e-15);
    a = b; fa = fb;
  }
  return NaN;
}

// Cutoff V of the mode (m, n): the zeros of J_{m-1} for m >= 1; for m = 0 it is 0, then the zeros of J_1
export function cutoffV(m, n = 1) {
  if (m === 0) return n === 1 ? 0 : besselZero(1, n - 1);
  return besselZero(m - 1, n);
}

// ---------------------------------------------------------------- surface roots of the round waveguide
//
// lambda J_{m+1}(lambda) K_m(kappa) = kappa K_{m+1}(kappa) J_m(lambda), lambda^2 + kappa^2 = V^2. The
// equation is divided by K_m, so that it cannot overflow, and the roots are searched in the angle theta of
// lambda = V cos theta, kappa = V sin theta: near cutoff kappa is tiny, and lambda = sqrt(V^2 - kappa^2) would
// lose it. Below theta = 0.02 the scan is in ln theta: for m = 0 the root has kappa of about 2 exp(-2 / V^2).

function surfaceG(m, V, theta) {
  const lam = V * Math.cos(theta);
  const kap = V * Math.sin(theta);
  return lam * besselJ(m + 1, lam) - kappaRatio(m, kap) * besselJ(m, lam);
}

export function surfaceRoots(m, V) {
  const grid = [];
  for (let u = Math.log(1e-150); u < Math.log(0.02); u += 1) grid.push(Math.exp(u));
  const n = Math.ceil(300 + 30 * V);
  const top = Math.PI / 2 - 1e-6;
  for (let i = 0; i <= n; i++) grid.push(0.02 + (top - 0.02) * (i / n));
  const roots = [];
  let ta = grid[0];
  let fa = surfaceG(m, V, ta);
  for (let i = 1; i < grid.length; i++) {
    const tb = grid[i];
    const fb = surfaceG(m, V, tb);
    if (fa * fb < 0 || fa === 0) {
      let t;
      if (tb < 0.02) {
        const u = brent((x) => surfaceG(m, V, Math.exp(x)), Math.log(ta), Math.log(tb), 1e-14);
        t = Math.exp(u);
      } else {
        t = brent((x) => surfaceG(m, V, x), ta, tb, 1e-15);
      }
      roots.push({ lambda: V * Math.cos(t), kappa: V * Math.sin(t), theta: t });
    }
    ta = tb; fa = fb;
  }
  roots.sort((a, b) => a.lambda - b.lambda);
  return roots;
}

// ---------------------------------------------------------------- leaky roots

// Below the cutoff V_c the root lambda of mode (m, 1) is complex, with Re alpha > 0 and Im alpha < 0 for
// alpha = sqrt(lambda^2 - V^2); the branch of the square root is the principal one. The root is the
// continuation in V of the surface root through the branch point alpha = 0 of the Hankel function:
//   1. just below V_c (V_c - 0.1 <= V < V_c) the imaginary part is small, and the real root of the model
//      lambda J_{m+1} - alpha Y_{m+1}/Y_m J_m = 0 (the Y part of the Hankel function only) starts a Newton iteration;
//   2. further down the root is followed in steps of V from V_c - 0.1 to 0.05 with a linear predictor, a Newton
//      corrector, in a fixed step of 0.02. The corrector converges at every step of every m; if it did not, the
//      path would throw instead of lose the root.
// A bare secant method from a guess lands on other roots, whose number is infinite: the path is what selects n = 1.

const LEAKY_BAND = 0.1;
const LEAKY_VMIN = 0.05;
const LEAKY_STEP = 0.02;

function alphaOf(lam, V) {
  return csqrt([lam[0] * lam[0] - lam[1] * lam[1] - V * V, 2 * lam[0] * lam[1]]);
}

// f = [lambda J_{m+1}(lambda) H_m(alpha) - alpha J_m(lambda) H_{m+1}(alpha)] / lambda^m; the division removes the
// trivial zero lambda = 0 (J_m(lambda) ~ lambda^m) and is analytic
function leakyF(m, V, lam) {
  const alpha = alphaOf(lam, V);
  if (cabs(alpha) < 1e-300) return [NaN, NaN];
  const a = jSequence(lam[0], lam[1], m + 1);
  const b = besselJY(alpha, m + 1);
  const jm = [a.jr[m], a.ji[m]];
  const jm1 = [a.jr[m + 1], a.ji[m + 1]];
  const hm = [b.jr[m] - b.yi[m], b.ji[m] + b.yr[m]];
  const hm1 = [b.jr[m + 1] - b.yi[m + 1], b.ji[m + 1] + b.yr[m + 1]];
  const t1 = cmul(cmul(lam, jm1), hm);
  const t2 = cmul(cmul(alpha, jm), hm1);
  let p = [1, 0];
  for (let i = 0; i < m; i++) p = cmul(p, lam);
  return cdiv([t1[0] - t2[0], t1[1] - t2[1]], p);
}

// Newton's method with a finite-difference derivative and a step limited to 0.5; null when it does not converge
function newtonComplex(f, z, tol = 1e-12, maxIt = 50) {
  for (let i = 0; i < maxIt; i++) {
    const f0 = f(z);
    const h = 1e-7 * (1 + cabs(z));
    const f1 = f([z[0] + h, z[1]]);
    const d = [(f1[0] - f0[0]) / h, (f1[1] - f0[1]) / h];
    let step = cdiv(f0, d);
    const sn = cabs(step);
    if (!(sn < Infinity)) return null;
    if (sn > 0.5) step = [step[0] * 0.5 / sn, step[1] * 0.5 / sn];
    z = [z[0] - step[0], z[1] - step[1]];
    if (cabs(step) < tol * (1 + cabs(z))) return z;
  }
  return null;
}

// real root lambda > V of the model with the Y part only, nearest to V; null when the scan finds none
function leakyModelRoot(m, V) {
  const model = (a) => {
    const lam = Math.sqrt(V * V + a * a);
    const { yr } = besselJY([a, 0], m + 1);
    return lam * besselJ(m + 1, lam) - (a * yr[m + 1] / yr[m]) * besselJ(m, lam);
  };
  const N = 240;
  const a0 = 1e-8;
  const a1 = 4;
  let prev = a0;
  let fp = model(prev);
  for (let i = 1; i <= N; i++) {
    const a = a0 * Math.pow(a1 / a0, i / N);
    const fa = model(a);
    if (fp * fa < 0) {
      const root = brent(model, prev, a, 1e-15);
      return Math.sqrt(V * V + root * root);
    }
    prev = a; fp = fa;
  }
  return null;
}

function leakyStart(m, V) {
  const lam = leakyModelRoot(m, V);
  return lam === null ? null : newtonComplex((z) => leakyF(m, V, z), [lam, 0]);
}

const leakyPaths = new Map();

// the root followed from V_c - 0.1 down to 0.05: V descending, with the root's re and im
function leakyPath(m) {
  if (leakyPaths.has(m)) return leakyPaths.get(m);
  const vc = cutoffV(m, 1);
  let V = vc - LEAKY_BAND;
  let z = leakyStart(m, V);
  const path = { V: [V], re: [z[0]], im: [z[1]] };
  while (V > LEAKY_VMIN + 1e-12) {
    const Vn = Math.max(V - LEAKY_STEP, LEAKY_VMIN);
    let pred = z;
    const k = path.V.length;
    if (k >= 2) {
      const t = (Vn - V) / (V - path.V[k - 2]);
      pred = [z[0] + (z[0] - path.re[k - 2]) * t, z[1] + (z[1] - path.im[k - 2]) * t];
    }
    const zn = newtonComplex((w) => leakyF(m, Vn, w), pred);
    if (!zn) throw new Error(`leaky path of m=${m}: the corrector does not converge at V=${Vn}`);
    V = Vn; z = zn;
    path.V.push(V); path.re.push(z[0]); path.im.push(z[1]);
  }
  leakyPaths.set(m, path);
  return path;
}

// The complex root of mode (m, 1) for V < V_c, m >= 1: { lambda, alpha }; null above the cutoff and for m = 0
export function leakyRoot(m, V) {
  if (m < 1) return null;
  const vc = cutoffV(m, 1);
  if (!(V < vc)) return null;
  let lam;
  if (V >= vc - LEAKY_BAND) {
    lam = leakyStart(m, V);
  } else {
    const p = leakyPath(m);
    const k = p.V.length;
    let i = 0;
    if (V <= p.V[k - 1]) i = k - 2;
    else {
      let lo = 0;
      let hi = k - 1; // p.V descends: find i with p.V[i] >= V > p.V[i + 1]
      while (hi - lo > 1) {
        const mid = (lo + hi) >> 1;
        if (p.V[mid] >= V) lo = mid; else hi = mid;
      }
      i = lo;
    }
    const t = (V - p.V[i]) / (p.V[i + 1] - p.V[i]);
    const pred = [p.re[i] + t * (p.re[i + 1] - p.re[i]), p.im[i] + t * (p.im[i + 1] - p.im[i])];
    lam = newtonComplex((z) => leakyF(m, V, z), pred);
  }
  return lam === null ? null : { lambda: lam, alpha: alphaOf(lam, V) };
}

// Re and Im of lambda along the leaky branch, V ascending from 0.05 to just below V_c: { V, re, im }
export function leakyCurve(m) {
  const p = leakyPath(m);
  const vc = cutoffV(m, 1);
  const V = [];
  const re = [];
  const im = [];
  for (let i = p.V.length - 1; i >= 0; i--) { V.push(p.V[i]); re.push(p.re[i]); im.push(p.im[i]); }
  // the band below the cutoff, on a grid dense toward V_c where lambda bends sharply
  const band = 40;
  for (let i = 1; i <= band; i++) {
    const v = vc - LEAKY_BAND * Math.pow(1 - i / band, 2) - 1e-5 * (i === band ? 1 : 0);
    if (v >= vc) break;
    const z = leakyStart(m, v);
    if (z) { V.push(v); re.push(z[0]); im.push(z[1]); }
  }
  return { V, re, im };
}

// ---------------------------------------------------------------- dispersion curve of the surface branch
//
// For a given kappa the equation lambda J_{m+1}(lambda) / J_m(lambda) = kappa K_{m+1}(kappa) / K_m(kappa) has
// one root lambda between the zero of J_{m-1} and the first zero of J_m (between 0 and j_01 for m = 0): the left
// side rises monotonically from 2m (from 0) to infinity. That is the first mode n = 1 with no scan; V = sqrt(lambda^2 + kappa^2).

export function surfaceCurve(m, Vmax, count = 300) {
  const lo = m === 0 ? 0 : besselZero(m - 1, 1);
  const hi = besselZero(m, 1);
  const V = [lo];
  const lambda = [lo];
  const kmax = Vmax;
  for (let i = 0; i < count; i++) {
    const kappa = 1e-4 * Math.pow(kmax / 1e-4, i / (count - 1));
    const rho = kappaRatio(m, kappa);
    const h = (x) => x * besselJ(m + 1, x) / besselJ(m, x) - rho;
    const eps = 1e-12;
    const root = brent(h, lo + (m === 0 ? 1e-9 : eps), hi - eps, 1e-15);
    if (root === null) continue;
    const v = Math.hypot(root, kappa);
    if (v > Vmax) {
      // end the curve at Vmax itself, on the chord to the first point beyond it
      const t = (Vmax - V[V.length - 1]) / (v - V[V.length - 1]);
      V.push(Vmax);
      lambda.push(lambda[lambda.length - 1] + t * (root - lambda[lambda.length - 1]));
      break;
    }
    V.push(v);
    lambda.push(root);
  }
  return { V, lambda };
}

// ---------------------------------------------------------------- the mode of the round waveguide at a given V

// Mode (m, n) at the parameter V of a waveguide with eps_i, eps_e: surface (a real root with K_m outside), leaky
// (m >= 1, n = 1, V below the cutoff) or null. k = V / sqrt(eps_i - eps_e) and beta^2 = k^2 eps_i - lambda^2.
export function circularMode(m, n, V, epsI, epsE, surf = surfaceRoots(m, V)) {
  const dEps = epsI - epsE;
  const k = V / Math.sqrt(dEps);
  let lam;
  let alpha;
  let type;
  let kappa = 0;
  if (n <= surf.length) {
    const r = surf[n - 1];
    lam = [r.lambda, 0];
    kappa = r.kappa;
    alpha = [0, kappa];
    type = "surface";
  } else if (m >= 1 && n === 1) {
    const r = leakyRoot(m, V);
    if (!r) return null;
    lam = r.lambda;
    alpha = r.alpha;
    type = "leaky";
  } else {
    return null;
  }
  // beta = sqrt(V^2 eps_i - lambda^2 (eps_i - eps_e)) / sqrt(eps_i - eps_e); for a surface wave the radicand is real:
  // beta^2 = k^2 eps_e + kappa^2 / (eps_i - eps_e) keeps kappa that lambda = sqrt(V^2 - kappa^2) has lost near cutoff
  const beta2 = type === "surface"
    ? [(V * V * epsE + kappa * kappa * dEps) / dEps, 0]
    : [(V * V * epsI - (lam[0] * lam[0] - lam[1] * lam[1]) * dEps) / dEps, -2 * lam[0] * lam[1]];
  const beta = csqrt(beta2);
  return { m, n, type, V, k, lambda: lam, alpha, kappa, beta, neff: [beta[0] / k, beta[1] / k] };
}

// u(r) of the mode with u(1) = 1, as [re, im]. Inside J_m(lambda r) / J_m(lambda); outside K_m(kappa r) / K_m(kappa)
// for a surface wave and H1_m(alpha r) / H1_m(alpha) for a leaky one.
export function circularField(mode, r) {
  const m = mode.m;
  if (mode.type === "surface") {
    if (r <= 1) {
      const a = besselJ(m, mode.lambda[0] * r) / besselJ(m, mode.lambda[0]);
      return [a, 0];
    }
    const x = mode.kappa;
    return [besselKscaled(m, x * r) / besselKscaled(m, x) * Math.exp(-x * (r - 1)), 0];
  }
  // the two values at the boundary are the same for every r: kept on the mode
  if (!mode.edge) mode.edge = { inside: besselJc(m, mode.lambda), outside: hankel1c(m, mode.alpha) };
  if (r <= 1) {
    const num = besselJc(m, [mode.lambda[0] * r, mode.lambda[1] * r]);
    return cdiv(num, mode.edge.inside);
  }
  return cdiv(hankel1c(m, [mode.alpha[0] * r, mode.alpha[1] * r]), mode.edge.outside);
}

// u(r) at every r of the list, as an array of [re, im]
export function circularProfile(mode, rs) {
  return rs.map((r) => circularField(mode, r));
}

// ---------------------------------------------------------------- symmetric planar waveguide
//
// X = kappa d, Y = gamma d, X^2 + Y^2 = V^2, V = k0 d sqrt(n1^2 - n2^2), q = 1 for TE and (n1/n2)^2 for TM.
// The equations tan X = qY/X (even) and tan X = -X/(qY) (odd) are solved in the form with arctangents,
//   even j = 2p:     X - atan2(qY, X) = p pi
//   odd  j = 2p + 1: X + atan2(X, qY) = (p + 1) pi
// whose left sides rise strictly in X on (0, V): there is one root exactly when V > j pi / 2, and Brent's method
// on the whole interval cannot pick another branch of the tangent. Y = sqrt((V - X)(V + X)) keeps Y accurate at cutoff.

export function symModes(n1, n2, lambda0, d, pol) {
  const k0 = 2 * Math.PI / lambda0;
  const V = k0 * d * Math.sqrt(n1 * n1 - n2 * n2);
  const q = pol === "TM" ? (n1 / n2) ** 2 : 1;
  const Yof = (X) => Math.sqrt(Math.max(0, (V - X) * (V + X)));
  const modes = [];
  for (let j = 0; j * Math.PI / 2 < V; j++) {
    let g;
    if (j % 2 === 0) {
      const p = j / 2;
      g = (X) => X - Math.atan2(q * Yof(X), X) - p * Math.PI;
    } else {
      const p = (j - 1) / 2;
      g = (X) => X + Math.atan2(X, q * Yof(X)) - (p + 1) * Math.PI;
    }
    const X = brent(g, 1e-300, V, 1e-15);
    if (X === null) continue;
    const Y = Yof(X);
    const neff = Math.sqrt(n2 * n2 + (Y / (k0 * d)) ** 2);
    modes.push({ j, parity: j % 2 === 0 ? "even" : "odd", X, Y, neff, q, pol });
  }
  return { V, M: Math.floor(2 * V / Math.PI) + 1, k0, d, n1, n2, q, pol, modes };
}

// the field of a mode in x / d: E_y for TE, H_y for TM; not normalized, equals cos(X x) or sin(X x) inside
export function symField(mode, xd) {
  const a = Math.abs(xd);
  if (mode.parity === "even") return a <= 1 ? Math.cos(mode.X * xd) : Math.cos(mode.X) * Math.exp(-mode.Y * (a - 1));
  return a <= 1 ? Math.sin(mode.X * xd) : Math.sign(xd) * Math.sin(mode.X) * Math.exp(-mode.Y * (a - 1));
}

// the curves of the graphical solution on X in (0, V): Y = X tan X (even) and Y = -X cot X (odd), with
// q: Y = X tan X / q and Y = -X cot X / q; each point carries its branch j = floor(2X / pi)
export function symCurves(V, q, count = 600) {
  const out = [];
  for (let j = 0; j * Math.PI / 2 < V; j++) {
    const a = j * Math.PI / 2;
    const b = Math.min((j + 1) * Math.PI / 2, V);
    const pts = [];
    const pole = b === (j + 1) * Math.PI / 2; // the branch rises to infinity at the upper end of its corridor
    for (let i = 0; i <= count; i++) {
      if (pole && i === count) break;
      const X = a + (b - a) * (i / count);
      pts.push([X, j % 2 === 0 ? X * Math.tan(X) / q : -X / Math.tan(X) / q]);
    }
    out.push({ j, parity: j % 2 === 0 ? "even" : "odd", pts });
  }
  return out;
}

// ---------------------------------------------------------------- asymmetric planar waveguide
//
// Substrate n_s, film n_f of thickness h, cover n_a. With n_eff in (max(n_a, n_s), n_f), in units of 1/k0:
//   gamma_f = sqrt(n_f^2 - n_eff^2), delta_m = sqrt(n_eff^2 - n_m^2),
//   F(n_eff, j) = gamma_f k0 h - atan2(c_a delta_a, gamma_f) - atan2(c_s delta_s, gamma_f) - j pi,
// c_m = 1 for TE and (n_f / n_m)^2 for TM. F falls strictly in n_eff and equals -(j + 1) pi at n_eff = n_f, so a mode j
// exists exactly when F > 0 at the lower end, and the root is unique.

function asymCoef(pol, nf, nm) {
  return pol === "TM" ? (nf / nm) ** 2 : 1;
}

export function asymF(neff, j, p) {
  const { na, nf, ns, k0h, pol } = p;
  const g = Math.sqrt(Math.max(0, nf * nf - neff * neff));
  const da = Math.sqrt(Math.max(0, neff * neff - na * na));
  const ds = Math.sqrt(Math.max(0, neff * neff - ns * ns));
  return g * k0h - Math.atan2(asymCoef(pol, nf, na) * da, g) - Math.atan2(asymCoef(pol, nf, ns) * ds, g) - j * Math.PI;
}

// Thickness of cutoff of the mode j: n_eff = max(n_a, n_s). With n_s >= n_a (the substrate is the denser
// cladding) it is the formula of the note; the other order of the cladding swaps their roles.
export function asymCutoffThickness(j, na, nf, ns, lambda0, pol) {
  const k0 = 2 * Math.PI / lambda0;
  const hi = Math.max(na, ns);
  const lo = Math.min(na, ns);
  if (!(hi < nf)) return Infinity;
  const c = asymCoef(pol, nf, lo);
  const a = c * Math.sqrt((hi * hi - lo * lo) / (nf * nf - hi * hi));
  return (j * Math.PI + Math.atan(a)) / (k0 * Math.sqrt(nf * nf - hi * hi));
}

export function asymModes(na, nf, ns, lambda0, h, pol) {
  const k0 = 2 * Math.PI / lambda0;
  const p = { na, nf, ns, k0h: k0 * h, pol };
  const lo = Math.max(na, ns);
  const modes = [];
  if (lo < nf) {
    for (let j = 0; j < 1000; j++) {
      if (!(asymF(lo, j, p) > 0)) break;
      const neff = brent((x) => asymF(x, j, p), lo, nf, 1e-16);
      const gamma = k0 * Math.sqrt(nf * nf - neff * neff);
      const deltaA = k0 * Math.sqrt(Math.max(0, neff * neff - na * na));
      const deltaS = k0 * Math.sqrt(Math.max(0, neff * neff - ns * ns));
      modes.push({ j, neff, gamma, deltaA, deltaS, h, pol, na, nf, ns });
    }
  }
  return { k0, p, modes };
}

// Coefficients of the profile f(z) with B = 1: f = D exp(delta_s z) below, B cos(gamma z) + C sin(gamma z) inside,
// A exp(-delta_a (z - h)) above. C follows from the continuity of f and of f' (TE) or f' / n^2 (TM) at z = 0.
export function asymCoefficients(mode) {
  const { gamma, deltaS, h, pol, nf, ns } = mode;
  const C = asymCoef(pol, nf, ns) * deltaS / gamma;
  const A = Math.cos(gamma * h) + C * Math.sin(gamma * h);
  return { B: 1, C, D: 1, A };
}

// f(z) for z in the same unit as h
export function asymField(mode, z, coef = asymCoefficients(mode)) {
  const { gamma, deltaA, deltaS, h } = mode;
  if (z < 0) return coef.D * Math.exp(deltaS * z);
  if (z > h) return coef.A * Math.exp(-deltaA * (z - h));
  return coef.B * Math.cos(gamma * z) + coef.C * Math.sin(gamma * z);
}

// Confinement factor: the share of the integral of f^2 that lies in the film, by the closed forms of the integrals
export function asymConfinement(mode) {
  const { gamma, deltaA, deltaS, h } = mode;
  const { B, C, D, A } = asymCoefficients(mode);
  const sub = D * D / (2 * deltaS);
  const cov = A * A / (2 * deltaA);
  const film = (B * B + C * C) / 2 * h + (B * B - C * C) / (4 * gamma) * Math.sin(2 * gamma * h) + B * C / (2 * gamma) * (1 - Math.cos(2 * gamma * h));
  return film / (sub + film + cov);
}
