// Logic of the linear algebra course pages: pure functions, no DOM.
// One ES module for every page; the build inlines it with `import` and `export` removed,
// and `node --test` imports it as is (lacore.test.mjs).
// The mechanisms that are not about linear algebra (parser, quadrature, LU, eigenvalues) live in
// the vault's numkit; the build inlines numkit.js before this module.
import { EPS, cond1, det, eigenvalues, integrate, luDecompose, luDet, luSolve, norm1 } from "../../../Scripts/numkit/numkit.js";

// Conventions of the note "Сингулярное разложение": an operator A with an m x n
// matrix has singular numbers rho_1 >= ... >= rho_r > 0 and orthonormal singular
// bases e^1..e^n of R^n and q^1..q^m of R^m with A e^k = rho_k q^k (k <= r) and
// A e^k = 0 (k > r). A matrix is a flat row-major array of m*n numbers.

// ---------------------------------------------------------------- SVD

// One-sided Jacobi (Hestenes) on a tall matrix, m >= n. The columns of A are
// rotated pairwise until they are mutually orthogonal; the same rotations,
// applied to the identity, build the orthogonal matrix W. Then A W = U Sigma:
// the column norms are the singular numbers and the normalised columns are
// the vectors q^k. Rotations act on the columns themselves, so the small
// singular numbers keep their relative accuracy, which forming A^T A would lose.
function jacobiTall(a, m, n) {
  const cols = Array.from({ length: n }, (_, j) => Float64Array.from({ length: m }, (_, i) => a[i * n + j]));
  const v = Array.from({ length: n }, (_, j) => { const c = new Float64Array(n); c[j] = 1; return c; });
  for (let sweep = 0; sweep < 60; sweep++) {
    let rotated = false;
    for (let i = 0; i < n - 1; i++) {
      for (let j = i + 1; j < n; j++) {
        const ci = cols[i], cj = cols[j];
        let alpha = 0, beta = 0, gamma = 0;
        for (let r = 0; r < m; r++) { alpha += ci[r] * ci[r]; beta += cj[r] * cj[r]; gamma += ci[r] * cj[r]; }
        if (gamma === 0 || Math.abs(gamma) <= EPS * Math.sqrt(alpha * beta)) continue;
        rotated = true;
        // tan of the angle that makes the new columns orthogonal: the smaller root of t^2 + 2 zeta t - 1 = 0
        const zeta = (beta - alpha) / (2 * gamma);
        const t = (zeta >= 0 ? 1 : -1) / (Math.abs(zeta) + Math.sqrt(1 + zeta * zeta));
        const c = 1 / Math.sqrt(1 + t * t), s = c * t;
        for (let r = 0; r < m; r++) { const x = ci[r], y = cj[r]; ci[r] = c * x - s * y; cj[r] = s * x + c * y; }
        const vi = v[i], vj = v[j];
        for (let r = 0; r < n; r++) { const x = vi[r], y = vj[r]; vi[r] = c * x - s * y; vj[r] = s * x + c * y; }
      }
    }
    if (!rotated) break;
  }
  const norms = cols.map((c) => Math.sqrt(c.reduce((acc, x) => acc + x * x, 0)));
  const order = norms.map((_, j) => j).sort((p, q) => norms[q] - norms[p] || p - q);
  return { norms: order.map((j) => norms[j]), u: order.map((j) => cols[j]), w: order.map((j) => v[j]) };
}

// Fills the columns from `from` on with unit vectors orthogonal to all the others.
// Candidates are the standard basis vectors, cleaned twice against the vectors already there.
function completeBasis(vectors, from, dim) {
  for (let k = from; k < vectors.length; k++) {
    for (let t = 0; t < dim; t++) {
      const c = new Float64Array(dim);
      c[t] = 1;
      for (let pass = 0; pass < 2; pass++) {
        for (let j = 0; j < vectors.length; j++) {
          if (j >= k) continue;
          const b = vectors[j];
          let d = 0;
          for (let r = 0; r < dim; r++) d += c[r] * b[r];
          for (let r = 0; r < dim; r++) c[r] -= d * b[r];
        }
      }
      const norm = Math.sqrt(c.reduce((acc, x) => acc + x * x, 0));
      if (norm >= Math.sqrt(0.5 / dim)) {
        vectors[k] = c.map((x) => x / norm);
        break;
      }
    }
  }
}

// The singular value decomposition of the m x n matrix `a` (row-major, not modified).
// Returns { m, n, rho, rank, q, e }: rho has min(m,n) numbers in descending order,
// the first `rank` positive and the others exactly zero; q[k] is a vector of length m,
// e[k] of length n, both families orthonormal. For k >= rank the vector of the longer
// family is a completion with no meaning of its own, added so that V and W stay bases.
export function svd(a, m, n) {
  if (a.length !== m * n) throw new RangeError(`a matrix ${m}x${n} needs ${m * n} numbers, got ${a.length}`);
  const p = Math.min(m, n);
  let norms, q, e;
  if (m >= n) {
    const r = jacobiTall(a, m, n);
    norms = r.norms; q = r.u; e = r.w;
  } else {
    // A^T = U S W^T gives A = W S U^T: the bases swap their roles
    const t = new Float64Array(m * n);
    for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) t[j * m + i] = a[i * n + j];
    const r = jacobiTall(t, n, m);
    norms = r.norms; q = r.w; e = r.u;
  }
  const top = p ? norms[0] : 0;
  const tol = Math.max(m, n) * top * EPS;
  const rank = norms.filter((x) => x > tol).length;
  const rho = Float64Array.from(norms, (x, k) => (k < rank ? x : 0));
  const big = m >= n ? q : e;
  for (let k = 0; k < rank; k++) { const d = norms[k]; big[k] = big[k].map((x) => x / d); }
  completeBasis(big, rank, big[0] ? big[0].length : 0);
  return { m, n, rho, rank, q, e };
}

// ---------------------------------------------------------------- low rank

// The matrix X = sum over j <= k of rho_j q^j (x) e^j, the rank-k approximation of the note.
// k is clamped to 0..min(m,n).
export function lowRank(s, k) {
  const { m, n } = s;
  const x = new Float64Array(m * n);
  for (let j = 0; j < Math.min(Math.max(k, 0), s.rho.length); j++) {
    if (s.rho[j] === 0) continue;
    const q = s.q[j], e = s.e[j];
    for (let i = 0; i < m; i++) {
      const c = s.rho[j] * q[i];
      for (let l = 0; l < n; l++) x[i * n + l] += c * e[l];
    }
  }
  return x;
}

// rho_{k+1}: the largest singular number of A - X, the error of the rank-k approximation.
export function spectralError(s, k) {
  const j = Math.max(k, 0);
  return j < s.rho.length ? s.rho[j] : 0;
}

// max |a_ij - x_ij|
export function maxAbsDiff(a, x) {
  let d = 0;
  for (let i = 0; i < a.length; i++) d = Math.max(d, Math.abs(a[i] - x[i]));
  return d;
}

// Numbers kept for a rank-k approximation of an m x n matrix: k vectors q of length m,
// k vectors e of length n and k singular numbers.
export function storage(m, n, k) {
  return k * (m + n + 1);
}

export function storageFraction(m, n, k) {
  return storage(m, n, k) / (m * n);
}

// ---------------------------------------------------------------- pictures

// The size of a w x h picture shrunk so that the long side is at most `max`.
export function fitSize(w, h, max) {
  const long = Math.max(w, h);
  if (long <= max) return { w, h };
  const f = max / long;
  return { w: Math.max(1, Math.round(w * f)), h: Math.max(1, Math.round(h * f)) };
}

// RGBA bytes of a w x h picture -> three h x w matrices R, G, B (row-major, values 0..255).
export function splitChannels(rgba, w, h) {
  return [0, 1, 2].map((c) => Float64Array.from({ length: w * h }, (_, i) => rgba[4 * i + c]));
}

// Three matrices -> opaque RGBA bytes; every value is rounded and clamped to 0..255.
export function mergeChannels(channels, w, h) {
  const out = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    for (let c = 0; c < 3; c++) out[4 * i + c] = Math.min(255, Math.max(0, Math.round(channels[c][i])));
    out[4 * i + 3] = 255;
  }
  return out;
}

// Integer hash of two coordinates to 0..1: the same picture on every machine.
function hash2(x, y) {
  let h = Math.imul(x + 374761393, 668265263) ^ Math.imul(y + 144665, 2246822519);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

// A deterministic picture with large and small details: a gradient sky, a sun with a glow
// and a sharp edge, wavy hills, a tower with a grid of windows, a ring, a diagonal-striped
// patch and weak noise. RGBA bytes, w x h.
export function syntheticImage(w, h) {
  const out = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      let r = 90 + 90 * v, g = 140 + 70 * v, b = 235 - 70 * v;
      const dSun = Math.hypot((u - 0.72) * (w / h), v - 0.27);
      const glow = Math.exp(-(dSun * dSun) / 0.03);
      r += 110 * glow; g += 80 * glow; b -= 60 * glow;
      if (dSun < 0.1) { r = 255; g = 232; b = 150; }
      const hill = 0.64 + 0.05 * Math.sin(2 * Math.PI * 2.2 * u + 0.6);
      if (v > hill) { const d = (v - hill) / (1 - hill); r = 40 + 30 * d; g = 120 - 50 * d; b = 60 + 20 * d; }
      if (u > 0.14 && u < 0.26 && v > 0.3 && v < hill + 0.02) {
        r = 60; g = 55; b = 80;
        const wx = Math.floor((u - 0.14) * w / 4), wy = Math.floor((v - 0.3) * h / 5);
        if (((x % 4) < 2) && ((y % 5) < 3) && hash2(wx, wy) > 0.35) { r = 250; g = 220; b = 110; }
      }
      const dRing = Math.hypot((u - 0.45) * (w / h), v - 0.8);
      if (Math.abs(dRing - 0.1) < 1.5 / h) { r = 245; g = 245; b = 245; }
      if (u > 0.55 && u < 0.7 && v > 0.74 && v < 0.94 && ((x + y) % 6) < 2) { r = 220; g = 60; b = 120; }
      const noise = (hash2(x, y) - 0.5) * 12;
      const k = 4 * (y * w + x);
      out[k] = r + noise; out[k + 1] = g + noise; out[k + 2] = b + noise; out[k + 3] = 255;
    }
  }
  return out;
}

// ---------------------------------------------------------------- 2 x 2 matrix

// Conventions of the notes "Собственные числа и собственные векторы" and "Характеристический
// многочлен": det(A - lambda I) = lambda^2 - tr(A) lambda + det(A) for n = 2 (the factor (-1)^n is 1),
// roots are the eigenvalues, the algebraic multiplicity is the multiplicity of the root and the
// geometric one is dim Ker(A - lambda I).

export function mapPoint(a, b, c, d, p) {
  return [a * p[0] + b * p[1], c * p[0] + d * p[1]];
}

// Area of a polygon by the shoelace formula; the sign is the orientation of the vertex order.
export function signedArea(points) {
  let s = 0;
  for (let i = 0; i < points.length; i++) {
    const p = points[i], q = points[(i + 1) % points.length];
    s += p[0] * q[1] - q[0] * p[1];
  }
  return s / 2;
}

// Eigen-data of the real matrix [[a, b], [c, d]].
// Returns { tr, det, disc, kind, values, alg, geom, vectors }:
//   disc = (a - d)^2 + 4 b c = tr^2 - 4 det, the discriminant of the characteristic polynomial,
//   kind is "distinct" (two real numbers), "double" (one real number of algebraic multiplicity 2)
//   or "complex" (alpha +- i beta, beta > 0),
//   values are { re, im } in the order: larger real part first,
//   alg and geom are the multiplicities of each value (equal for "distinct" and "complex"),
//   vectors are unit real eigenvectors, one per value for "distinct", a basis of the eigenspace
//   for "double" (one vector for a Jordan block, two for a scalar matrix) and empty for "complex".
// The roots come from the formula with the sign chosen so that no subtraction of close numbers
// happens, and the second root from Vieta, mu1 mu2 = det.
export function eig2(a, b, c, d) {
  const tr = a + d, det = a * d - b * c;
  const disc = (a - d) * (a - d) + 4 * b * c;
  const scale = a * a + b * b + c * c + d * d;
  const eigenvector = (mu) => {
    // the row of A - mu I of larger norm is orthogonal to the eigenvector
    const r1 = [a - mu, b], r2 = [c, d - mu];
    const n1 = Math.hypot(...r1), n2 = Math.hypot(...r2);
    const r = n1 >= n2 ? r1 : r2, n = Math.max(n1, n2);
    if (n <= 1e-12 * Math.sqrt(scale)) return null;
    // the sign is fixed so that the first nonzero coordinate is positive: the same vector on every machine
    const t = r[1] > 0 || (r[1] === 0 && r[0] < 0) ? -1 : 1;
    return [-t * r[1] / n + 0, t * r[0] / n + 0];
  };
  if (Math.abs(disc) <= 1e-12 * scale) {
    const mu = tr / 2;
    const v = eigenvector(mu);
    return { tr, det, disc, kind: "double", values: [{ re: mu, im: 0 }], alg: 2, geom: v ? 1 : 2, vectors: v ? [v] : [[1, 0], [0, 1]] };
  }
  if (disc < 0) {
    return { tr, det, disc, kind: "complex", values: [{ re: tr / 2, im: Math.sqrt(-disc) / 2 }, { re: tr / 2, im: -Math.sqrt(-disc) / 2 }], alg: 1, geom: 1, vectors: [] };
  }
  const sq = Math.sqrt(disc);
  const big = (tr >= 0 ? tr + sq : tr - sq) / 2;
  const small = big === 0 ? 0 : det / big;
  const [m1, m2] = big >= small ? [big, small] : [small, big];
  return { tr, det, disc, kind: "distinct", values: [{ re: m1, im: 0 }, { re: m2, im: 0 }], alg: 1, geom: 1, vectors: [eigenvector(m1), eigenvector(m2)] };
}

// ---------------------------------------------------------------- principal components of a plane cloud

// Conventions of the note "Метод главных компонент": the rows x_i of X are the centred points,
// C = X^T X / (N - 1), the eigenvalues lambda_1 >= lambda_2 >= 0 and the unit eigenvectors w^1, w^2
// are the variances and the directions of the components, the explained share of the first one is
// lambda_1 / (lambda_1 + lambda_2). A point is [x, y].

// The mean of a cloud and the cloud with the mean subtracted. No points give the mean [0, 0].
export function centerPoints(pts) {
  const n = pts.length;
  if (n === 0) return { mean: [0, 0], centered: [] };
  const mean = [0, 1].map((k) => pts.reduce((s, p) => s + p[k], 0) / n);
  return { mean, centered: pts.map((p) => [p[0] - mean[0], p[1] - mean[1]]) };
}

// The sample covariance matrix [[cxx, cxy], [cxy, cyy]] with the divisor N - 1; it is zero for N < 2.
export function covariance2(pts) {
  const n = pts.length;
  if (n < 2) return { n, cxx: 0, cxy: 0, cyy: 0 };
  let sxx = 0, sxy = 0, syy = 0;
  for (const [x, y] of centerPoints(pts).centered) { sxx += x * x; sxy += x * y; syy += y * y; }
  return { n, cxx: sxx / (n - 1), cxy: sxy / (n - 1), cyy: syy / (n - 1) };
}

// Principal components of a symmetric 2 x 2 covariance matrix. Returns
//   { lambda: [l1, l2], w: [w1, w2] | null, status, explained }
// status is "zero" (C = 0: no spread, no axes), "round" (l1 = l2 within 1e-9 l1: every direction is
// principal, so the axes are not defined and w is null) or "ok".
// The eigenvalues come from eig2, with the tiny negative rounding of l2 for points on a line cut to 0.
// eig2 calls roots closer than about 1e-6 of the scale one double root and returns the same value
// twice, so there the pair is rebuilt from its discriminant, tr/2 +- sqrt(disc)/2 (disc is exact and
// non-negative for a symmetric matrix). The directions come from the rotation angle,
// w1 = (cos t, sin t), w2 = (-sin t, cos t), t = atan2(2 cxy, cxx - cyy) / 2: eig2 has no eigenvector
// to give for a near double root, and the angle formula is exact for any gap.
export function principalAxes(cxx, cxy, cyy) {
  const e = eig2(cxx, cxy, cxy, cyy);
  const [r1, r2] = e.kind === "double" ? [e.tr / 2 + Math.sqrt(e.disc) / 2, e.tr / 2 - Math.sqrt(e.disc) / 2] : [e.values[0].re, e.values[1].re];
  const l1 = Math.max(r1, 0);
  const l2 = Math.min(Math.max(r2, 0), l1);
  if (l1 === 0) return { lambda: [0, 0], w: null, status: "zero", explained: null };
  const explained = l1 / (l1 + l2);
  if (l1 - l2 <= 1e-9 * l1) return { lambda: [l1, l2], w: null, status: "round", explained };
  const t = Math.atan2(2 * cxy, cxx - cyy) / 2;
  return { lambda: [l1, l2], w: [[Math.cos(t), Math.sin(t)], [-Math.sin(t), Math.cos(t)]], status: "ok", explained };
}

// The least squares line y = slope x + intercept through a cloud, as { slope, intercept, point, dir }
// (point is the mean, dir the unit direction); null for fewer than two points and for points whose x
// does not vary (a vertical line is not a graph of a function y(x)).
export function olsLine(pts) {
  if (pts.length < 2) return null;
  const { mean, centered } = centerPoints(pts);
  let sxx = 0, sxy = 0, syy = 0;
  for (const [x, y] of centered) { sxx += x * x; sxy += x * y; syy += y * y; }
  if (sxx <= 1e-24 * (sxx + syy)) return null;
  const slope = sxy / sxx, norm = Math.hypot(1, slope);
  return { slope, intercept: mean[1] - slope * mean[0], point: mean, dir: [1 / norm, slope / norm] };
}

// Sums of squares for the line { point, dir } (dir is a unit vector): the perpendicular distances
// and the vertical deviations |y - y_line(x)|; vert is null for a vertical line.
export function lineSums(pts, line) {
  const [px, py] = line.point, [dx, dy] = line.dir;
  let perp = 0, vert = 0;
  for (const [x, y] of pts) {
    const c = (x - px) * dy - (y - py) * dx;
    perp += c * c;
    if (Math.abs(dx) > 1e-12) { const r = (y - py) - dy / dx * (x - px); vert += r * r; }
  }
  return { perp, vert: Math.abs(dx) > 1e-12 ? vert : null };
}

// Everything the PCA page shows for a cloud:
//   n, mean, C = [cxx, cxy, cxy, cyy], lambda, w, status, explained (see principalAxes),
//   pc  the line of the first component with perp and vert (null without axes),
//   ols the least squares line with perp and vert (null without one),
//   coords and projections: the coordinates (x_i - mean, w1) and the points mean + coords w1 (empty without axes).
export function pca2(pts) {
  const { mean } = centerPoints(pts);
  const { n, cxx, cxy, cyy } = covariance2(pts);
  const ax = principalAxes(cxx, cxy, cyy);
  const pc = ax.w ? { point: mean, dir: ax.w[0] } : null;
  const ols = olsLine(pts);
  const coords = ax.w ? pts.map((p) => (p[0] - mean[0]) * ax.w[0][0] + (p[1] - mean[1]) * ax.w[0][1]) : [];
  return {
    n, mean, C: [cxx, cxy, cxy, cyy], ...ax,
    pc: pc && { ...pc, ...lineSums(pts, pc) },
    ols: ols && { ...ols, ...lineSums(pts, ols) },
    coords,
    projections: ax.w ? coords.map((t) => [mean[0] + t * ax.w[0][0], mean[1] + t * ax.w[0][1]]) : [],
  };
}

// A deterministic generator of numbers in [0, 1) (mulberry32): the same seed gives the same cloud.
export function seededRandom(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// A cloud of n points: the standard normal point scaled by (sx, sy), turned by `angle` degrees
// counterclockwise, plus an isotropic normal noise of standard deviation `noise`. The covariance
// is R diag(sx^2 + noise^2, sy^2 + noise^2) R^T up to the sampling error.
export function generateCloud({ n, sx, sy, angle, noise, seed }) {
  const rnd = seededRandom(seed);
  const normal = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
  const t = angle * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
  return Array.from({ length: n }, () => {
    const u = sx * normal(), v = sy * normal();
    return [c * u - s * v + noise * normal(), s * u + c * v + noise * normal()];
  });
}

// ---------------------------------------------------------------- Fredholm equation with a degenerate kernel

// Conventions of the note "Решение уравнения Фредгольма с вырожденным ядром": the equation is
//   phi(x) - lambda * int_a^b K(x,t) phi(t) dt = f(x),   K(x,t) = sum_k alpha_k(x) beta_k(t),
// a_km = int_a^b alpha_k(t) beta_m(t) dt, f_m = int_a^b beta_m(t) f(t) dt, and the constants
// C_k = int beta_k phi satisfy  C_m - lambda sum_k a_km C_k = f_m, i.e. (I - lambda A^T) C = f
// for A = (a_km); the solution is phi = f + lambda sum_k C_k alpha_k.
// A matrix is a flat row-major Float64Array, A[k*n+m] = a_km. The text of a problem is compiled
// by compileProblem of numkit.

// The matrix A, the vector (f_m), the worst quadrature error estimate and `scale`, the 1-norm of the
// matrix of the integrals of |alpha_k beta_m|: entries of A below 1e-14 scale are noise, and
// characteristicNumbers takes this scale to tell the zero eigenvalues of A from the small real ones.
export function kernelData(p) {
  const { n } = p;
  const A = new Float64Array(n * n), B = new Float64Array(n * n), fv = new Float64Array(n);
  let err = 0, ok = true;
  const take = (r) => { err = Math.max(err, r.err); ok = ok && r.ok; return r.value; };
  for (let k = 0; k < n; k++) {
    for (let m = 0; m < n; m++) {
      const r = integrate((t) => p.alpha[k](t) * p.beta[m](t), p.lo, p.hi);
      A[k * n + m] = take(r); B[k * n + m] = r.scale;
    }
  }
  for (let m = 0; m < n; m++) fv[m] = take(integrate((t) => p.beta[m](t) * p.f(t), p.lo, p.hi));
  return { A, fv, err, ok, scale: norm1(B, n) };
}

// The matrix I - lambda A^T of the system for C.
export function systemMatrix(A, n, lambda) {
  const M = new Float64Array(n * n);
  for (let m = 0; m < n; m++) for (let k = 0; k < n; k++) M[m * n + k] = (m === k ? 1 : 0) - lambda * A[k * n + m];
  return M;
}

// Delta(lambda) = det(I - lambda A^T) = det(I - lambda A).
export function delta(A, n, lambda) {
  return det(systemMatrix(A, n, lambda), n);
}

// Solves the system for one lambda: { delta, cond, singular, C }. `singular` is true when
// (1 + |lambda| ||A||_1) ||(I - lambda A^T)^-1||_1 exceeds 1e10: lambda is then a characteristic
// number to the accuracy of the quadrature and C is not returned (no unique solution).
export function solveFredholm(A, fv, n, lambda) {
  const M = systemMatrix(A, n, lambda);
  const f = luDecompose(M, n);
  const cond = cond1(M, n, 1 + Math.abs(lambda) * norm1(A, n));
  const d = luDet(f);
  if (f.singular || cond > 1e10) return { delta: d, cond, singular: true, C: null };
  return { delta: d, cond, singular: false, C: luSolve(f, fv) };
}

export function solutionAt(p, C, lambda, x) {
  let s = p.f(x);
  for (let k = 0; k < p.n; k++) s += lambda * C[k] * p.alpha[k](x);
  return s;
}

// The residual phi(x) - lambda int K(x,t) phi(t) dt - f(x), the integral by quadrature of the
// whole kernel, independent of the reduction to the system. { value, err }.
export function residualAt(p, C, lambda, x) {
  const phi = (t) => solutionAt(p, C, lambda, t);
  const kernel = (t) => { let s = 0; for (let k = 0; k < p.n; k++) s += p.alpha[k](x) * p.beta[k](t); return s; };
  const r = integrate((t) => kernel(t) * phi(t), p.lo, p.hi);
  return { value: phi(x) - lambda * r.value - p.f(x), err: Math.abs(lambda) * r.err };
}

// ---------------------------------------------------------------- characteristic numbers of a degenerate kernel

// Conventions of the note "Характеристические и собственные числа уравнений Фредгольма":
// Delta(lambda) = det(I - lambda A) is a polynomial of degree p <= n with Delta(0) = 1, its roots are the
// characteristic numbers. For lambda != 0, det(I - lambda A) = lambda^n det(I/lambda - A), so
// Delta(lambda) = 0 exactly when mu = 1/lambda is an eigenvalue of A, and a root of multiplicity m of
// Delta is an eigenvalue of multiplicity m of A. The zero eigenvalues of A give no root: a polynomial
// of degree p < n has fewer roots than A has eigenvalues. The "eigenvalue of the kernel" is sigma = 1/lambda = mu.

// Real and imaginary parts of 1 / (re + i im).
const inverse = ({ re, im }) => { const d = re * re + im * im; return { re: re / d, im: im === 0 ? 0 : -im / d }; };

// The number of singular values of a real matrix not above `limit`.
function nullity(M, n, limit) {
  return svd(M, n, n).rho.filter((r) => r <= limit).length;
}

// A singular value of I - lambda A^T counts as zero when it is not above tol (1 + |lambda| ||A||_1): the
// size of the matrix, not its largest singular value, which is itself rounding noise when the matrix is 0.
const nullLimit = (A, n, lambda, tol) => tol * (1 + Math.hypot(lambda.re, lambda.im) * norm1(A, n));

// The nullity of I - lambda A^T for a complex lambda = p + i q: that of the real 2n x 2n matrix
// [[Re, -Im], [Im, Re]], twice as large.
function nullityAt(A, n, lambda, tol) {
  const limit = nullLimit(A, n, lambda, tol);
  if (lambda.im === 0) return nullity(systemMatrix(A, n, lambda.re), n, limit);
  const N = 2 * n, big = new Float64Array(N * N);
  for (let m = 0; m < n; m++) {
    for (let k = 0; k < n; k++) {
      const a = A[k * n + m];
      const re = (m === k ? 1 : 0) - lambda.re * a, im = -lambda.im * a;
      big[m * N + k] = re; big[m * N + n + k] = -im; big[(n + m) * N + k] = im; big[(n + m) * N + n + k] = re;
    }
  }
  return nullity(big, N, limit) / 2;
}

// The characteristic numbers of the kernel with the matrix `A`: the groups of equal roots of Delta.
// Returns [{ lambda: { re, im }, sigma: { re, im }, alg, rank, real }], by |lambda| ascending, a real number
// before a complex one and a conjugate pair as two groups, im > 0 first. The eigenvalues mu of A
// are taken as equal when they differ by less than 1e-4 |mu| (a root of multiplicity m is found to about
// eps^(1/m)); those with |mu| <= 1e-6 `scale` are zero eigenvalues of A and give no characteristic number;
// `scale` is ||A||_1 unless the caller knows the size of the noise in A better (kernelData().scale).
// alg is the multiplicity of the root, rank the dimension of the solution space of the homogeneous
// system, i.e. the number of independent eigenfunctions (the rank of the characteristic number in the note).
export function characteristicNumbers(A, n, scale = norm1(A, n)) {
  const floor = 1e-6 * scale;
  const mus = eigenvalues(A, n).filter((z) => Math.hypot(z.re, z.im) > floor);
  const used = new Array(mus.length).fill(false), groups = [];
  mus.forEach((z, i) => {
    if (used[i]) return;
    const members = [];
    mus.forEach((w, j) => { if (!used[j] && Math.hypot(z.re - w.re, z.im - w.im) <= 1e-4 * Math.max(Math.hypot(z.re, z.im), Math.hypot(w.re, w.im))) { used[j] = true; members.push(w); } });
    const re = members.reduce((s, w) => s + w.re, 0) / members.length, im = members.reduce((s, w) => s + w.im, 0) / members.length;
    const real = Math.abs(im) <= 1e-5 * Math.hypot(re, im);
    groups.push({ mu: { re, im: real ? 0 : im }, alg: members.length, real });
  });
  const out = groups.map((g) => {
    const lambda = inverse(g.mu);
    return { lambda, sigma: g.mu, alg: g.alg, rank: Math.min(g.alg, nullityAt(A, n, lambda, 1e-5)), real: g.real };
  });
  return out.sort((p, q) => Math.hypot(p.lambda.re, p.lambda.im) - Math.hypot(q.lambda.re, q.lambda.im) || q.lambda.im - p.lambda.im || q.lambda.re - p.lambda.re);
}

// The eigenfunctions of a real characteristic number: the coefficient vectors C of a basis of the
// solutions of (I - lambda A^T) C = 0, orthonormal; the function is phi = sum C_k alpha_k (up to the factor lambda).
export function eigenCoefficients(A, n, lambda, tol = 1e-5) {
  const s = svd(systemMatrix(A, n, lambda), n, n);
  const out = [];
  const limit = nullLimit(A, n, { re: lambda, im: 0 }, tol);
  for (let k = 0; k < n; k++) if (s.rho[k] <= limit) out.push(Float64Array.from(s.e[k]));
  return out;
}

// phi(x) = sum C_k alpha_k(x) at the points xs, scaled so that the largest value in modulus is 1 and positive.
export function eigenFunctionValues(p, C, xs) {
  const v = xs.map((x) => { let s = 0; for (let k = 0; k < p.n; k++) s += C[k] * p.alpha[k](x); return s; });
  let top = 0;
  for (const y of v) if (Math.abs(y) > Math.abs(top)) top = y;
  return top === 0 ? v : v.map((y) => y / top);
}
