// Logic of the numerical methods course pages: pure functions, no DOM.
// One ES module for every page; the build inlines it with `import` and `export` removed,
// and `node --test` imports it as is (nmcore.test.mjs).
// The mechanisms that are not about this course (parser, quadrature, LU, eigenvalues) live in
// the vault's numkit; the build inlines numkit.js before this module, so a name numkit exports
// is never declared here.
import { ExprError, cond1, compileExpression, eigenvalues, integrate, luDecompose, luSolve, parseExpression } from "../../../Scripts/numkit/numkit.js";

// A matrix is a flat row-major array of n*n numbers, a vector is a Float64Array or an array of n numbers.

// ---------------------------------------------------------------- stationary iterations for A x = b

// Conventions of the note "Сходимость стационарных итерационных методов": A = L + D + R, the canonical form
//   (1/tau) B (x^{k+1} - x^k) + A x^k = b,
// the transition matrix S = I - tau B^{-1} A and the error z^k = x^k - x, z^{k+1} = S z^k.
//   jacobi   B = D        tau = 1
//   seidel   B = D + L    tau = 1
//   relax    B = D + w L  tau = w
//   explicit B = I        tau = tau (the simple iteration of the note on the optimal parameter)
export const METHODS = ["jacobi", "seidel", "relax", "explicit"];

export class IterationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

const usesDiagonal = (method) => method !== "explicit";

function requireDiagonal(A, n) {
  for (let i = 0; i < n; i++) {
    if (A[i * n + i] === 0) throw new IterationError("zero-diagonal", `диагональный элемент a${i + 1}${i + 1} равен нулю: метод делит на него`);
  }
}

// { B, tau } of the canonical form. `omega` is used by "relax", `tau` by "explicit".
export function canonicalForm(A, n, method, { omega = 1, tau = 1 } = {}) {
  if (!METHODS.includes(method)) throw new IterationError("bad-method", `метод ${method} неизвестен`);
  if (usesDiagonal(method)) requireDiagonal(A, n);
  const B = new Float64Array(n * n);
  const w = method === "relax" ? omega : 1;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (method === "explicit") B[i * n + j] = i === j ? 1 : 0;
      else if (i === j) B[i * n + j] = A[i * n + j];
      else if (i > j && method !== "jacobi") B[i * n + j] = w * A[i * n + j];
    }
  }
  return { B, tau: method === "explicit" ? tau : method === "relax" ? omega : 1 };
}

// S = I - tau B^{-1} A, the matrix of (2.8).
export function transitionMatrix(A, n, method, params) {
  const { B, tau } = canonicalForm(A, n, method, params);
  const fact = luDecompose(B, n);
  const S = new Float64Array(n * n);
  for (let j = 0; j < n; j++) {
    const col = luSolve(fact, Float64Array.from({ length: n }, (_, i) => A[i * n + j]));
    for (let i = 0; i < n; i++) S[i * n + j] = (i === j ? 1 : 0) - tau * col[i];
  }
  return S;
}

// x^0, x^1, ..., x^steps by the componentwise formulas of the notes (1.3), (1.6), (1.9) and x - tau (A x - b).
// They do not go through B and S, so the transition matrix is checked by a computation of another shape.
export function iterate(A, b, x0, n, method, params = {}, steps = 20) {
  canonicalForm(A, n, method, params);
  const omega = method === "relax" ? params.omega : 1;
  const out = [Float64Array.from(x0)];
  for (let k = 0; k < steps; k++) {
    const x = out[k], next = Float64Array.from(x);
    if (method === "explicit") {
      for (let i = 0; i < n; i++) {
        let r = -b[i];
        for (let j = 0; j < n; j++) r += A[i * n + j] * x[j];
        next[i] = x[i] - params.tau * r;
      }
    } else {
      // jacobi reads the old vector for every j, seidel and relax read the new components for j < i
      const src = method === "jacobi" ? x : next;
      for (let i = 0; i < n; i++) {
        let s = b[i];
        for (let j = 0; j < n; j++) if (j !== i) s -= A[i * n + j] * src[j];
        const gs = s / A[i * n + i];
        next[i] = method === "relax" ? (1 - omega) * x[i] + omega * gs : gs;
      }
    }
    out.push(next);
  }
  return out;
}

// The solution of A x = b by LU, or null when A is singular.
export function solveExact(A, b, n) {
  const fact = luDecompose(A, n);
  return fact.singular ? null : luSolve(fact, b);
}

export const maxNorm = (v) => v.reduce((m, x) => Math.max(m, Math.abs(x)), 0);

// The errors max_j |x_j^k - x_j| of a run, as in the tables of the notes.
export const errorsOf = (xs, exact) => xs.map((x) => maxNorm(Array.from(x, (v, i) => v - exact[i])));

// ||S||_inf, the largest row sum of moduli: the q of the notes when it is below one.
export function infNorm(S, n) {
  let best = 0;
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) s += Math.abs(S[i * n + j]);
    best = Math.max(best, s);
  }
  return best;
}

// rho(S) = max |lambda|; NaN if the eigenvalue iteration does not converge (a matrix with NaN).
export function spectralRadius(S, n) {
  try {
    return eigenvalues(S, n).reduce((m, z) => Math.max(m, Math.hypot(z.re, z.im)), 0);
  } catch {
    return NaN;
  }
}

// How many steps shrink the error by `factor` when it falls like rho^k: ceil(ln factor / -ln rho); Infinity if rho >= 1.
export function stepsToReduce(rho, factor = 1e6) {
  return rho >= 1 || !(rho >= 0) ? Infinity : rho === 0 ? 1 : Math.ceil(Math.log(factor) / -Math.log(rho) - 1e-9);
}

// ---------------------------------------------------------------- the criteria of the notes

// q of (1.4): the largest row sum of |a_ij|/|a_ii| over j != i; the diagonal dominance is q < 1. null if a_ii = 0.
export function dominanceQ(A, n) {
  let q = 0;
  for (let i = 0; i < n; i++) {
    const d = Math.abs(A[i * n + i]);
    if (d === 0) return null;
    let s = 0;
    for (let j = 0; j < n; j++) if (j !== i) s += Math.abs(A[i * n + j]);
    q = Math.max(q, s / d);
  }
  return q;
}

export function isSymmetric(A, n, tol = 1e-12) {
  let scale = 0;
  for (const v of A) scale = Math.max(scale, Math.abs(v));
  for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) if (Math.abs(A[i * n + j] - A[j * n + i]) > tol * Math.max(scale, 1e-300)) return false;
  return true;
}

// Cholesky of a symmetric matrix: true when every pivot exceeds `tol`, that is, the matrix is positive definite.
export function isPositiveDefinite(M, n, tol = 0) {
  const L = new Float64Array(n * n);
  for (let j = 0; j < n; j++) {
    let d = M[j * n + j];
    for (let k = 0; k < j; k++) d -= L[j * n + k] ** 2;
    if (!(d > tol)) return false;
    L[j * n + j] = Math.sqrt(d);
    for (let i = j + 1; i < n; i++) {
      let s = M[i * n + j];
      for (let k = 0; k < j; k++) s -= L[i * n + k] * L[j * n + k];
      L[i * n + j] = s / L[j * n + j];
    }
  }
  return true;
}

// The condition (2.13) of Samarsky's theorem, (B1 x, x) > tau/2 (A x, x) for all x != 0, for a symmetric positive
// definite real A: the matrix B1 - tau/2 A, with B1 the symmetric part of B, is positive definite.
// null when the theorem does not apply (A is not symmetric positive definite).
export function samarskyHolds(A, n, method, params) {
  if (!isSymmetric(A, n) || !isPositiveDefinite(A, n)) return null;
  const { B, tau } = canonicalForm(A, n, method, params);
  const M = new Float64Array(n * n);
  let scale = 0;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const b1 = (B[i * n + j] + B[j * n + i]) / 2, a = tau / 2 * A[i * n + j];
      M[i * n + j] = b1 - a;
      scale = Math.max(scale, Math.abs(b1), Math.abs(a));
    }
  }
  return isPositiveDefinite(M, n, 1e-12 * scale);
}

// Both extreme eigenvalues m <= M of a symmetric positive definite A and the optimal parameter of the note
// "Оптимальный выбор итерационного параметра" for B = I: tau0 = 2/(M+m), rho = (M-m)/(M+m). null if A is not such a matrix.
export function optimalTau(A, n) {
  if (!isSymmetric(A, n) || !isPositiveDefinite(A, n)) return null;
  const ev = eigenvalues(A, n).map((z) => z.re);
  const m = Math.min(...ev), M = Math.max(...ev);
  return { m, M, tau: 2 / (M + m), rho: (M - m) / (M + m) };
}

// ---------------------------------------------------------------- the radius against the parameter

// rho(S) of the method with the parameter `p` (omega for "relax", tau for "explicit") at each value of the grid.
export function radiusCurve(A, n, method, grid) {
  const key = method === "relax" ? "omega" : "tau";
  return grid.map((p) => spectralRadius(transitionMatrix(A, n, method, { [key]: p }), n));
}

// The parameter in (lo, hi) with the least rho(S): the best node of a grid, then golden-section search in the
// two cells around it. { param, rho }.
export function bestParameter(A, n, method, lo, hi, cells = 200) {
  const key = method === "relax" ? "omega" : "tau";
  const rho = (p) => spectralRadius(transitionMatrix(A, n, method, { [key]: p }), n);
  const grid = Array.from({ length: cells + 1 }, (_, i) => lo + (hi - lo) * i / cells);
  const vals = grid.map(rho);
  let best = 0;
  vals.forEach((v, i) => { if (v < vals[best]) best = i; });
  let a = grid[Math.max(best - 1, 0)], b = grid[Math.min(best + 1, cells)];
  const phi = (Math.sqrt(5) - 1) / 2;
  let c = b - phi * (b - a), d = a + phi * (b - a), fc = rho(c), fd = rho(d);
  for (let it = 0; it < 80 && b - a > 1e-12; it++) {
    if (fc < fd) { b = d; d = c; fd = fc; c = b - phi * (b - a); fc = rho(c); }
    else { a = c; c = d; fc = fd; d = a + phi * (b - a); fd = rho(d); }
  }
  const p = (a + b) / 2, r = rho(p);
  return r <= vals[best] ? { param: p, rho: r } : { param: grid[best], rho: vals[best] };
}

// ================================================================ equations of the second kind

// Conventions of the notes "Метод квадратур", "Метод квадратур для уравнений Вольтерра" and the projection notes:
//   Fredholm   y(x) - lam * int_a^b K(x,s) y(s) ds = f(x)
//   Volterra   y(x) - lam * int_a^x K(x,s) y(s) ds = f(x)        (the notes put lam inside K: lam = 1)
//   nonlinear  y(x) - lam * int_a^x K(x,s,y(s)) ds = f(x)       (kind "volterra-nonlinear")
// N is the number of unknowns of a method: nodes of a quadrature, terms of a degenerate kernel, basis functions.

export class ProblemError extends Error {
  constructor(code, message, field = null) {
    super(message);
    this.code = code;
    this.field = field;
  }
}

// kind: "fredholm" | "volterra" | "volterra-nonlinear". `exact` is a formula in x or an empty text.
// A bad formula throws numkit's ExprError with `.field` set to "kernel", "f" or "exact".
export function makeProblem({ kind = "fredholm", lo, hi, kernel, f, lambda = 1, exact = "" }) {
  if (!(Number.isFinite(lo) && Number.isFinite(hi) && lo < hi)) throw new ProblemError("bad-interval", "отрезок [a; b] должен быть конечным, и a < b", "interval");
  if (!Number.isFinite(lambda)) throw new ProblemError("bad-lambda", "λ должно быть числом", "lambda");
  const nonlinear = kind === "volterra-nonlinear";
  const compile = (src, names, field) => {
    try { return compileExpression(src, names); } catch (e) { if (e instanceof ExprError) e.field = field; throw e; }
  };
  return {
    kind, nonlinear, volterra: kind !== "fredholm", lo, hi, lam: lambda, kernelText: kernel,
    K: compile(kernel, nonlinear ? ["x", "s", "y"] : ["x", "s"], "kernel"),
    f: compile(f, ["x"], "f"),
    exact: exact.trim() ? compile(exact, ["x"], "exact") : null,
  };
}

const finite = (v, what) => {
  if (!Number.isFinite(v)) throw new ProblemError("bad-value", `${what} не определено или бесконечно`);
  return v;
};
const short = (v) => String(+v.toPrecision(6));
const Kv = (p, x, s, y) => finite(p.nonlinear ? p.K(x, s, y) : p.K(x, s), `K(${short(x)}; ${short(s)})`);
const fv = (p, x) => finite(p.f(x), `f(${short(x)})`);

// n equidistant nodes from a to b, ends included.
export function uniformGrid(a, b, n) {
  if (n < 2) return Float64Array.of((a + b) / 2);
  return Float64Array.from({ length: n }, (_, i) => a + (b - a) * i / (n - 1));
}

export const trapezoidWeights = (n, h) => Float64Array.from({ length: n }, (_, j) => (j === 0 || j === n - 1 ? h / 2 : h));

// Simpson's weights for an odd number n >= 3 of nodes with the step h.
export function simpsonWeights(n, h) {
  if (n < 3 || n % 2 === 0) throw new ProblemError("simpson-odd", "формула Симпсона берёт нечётное число узлов, не меньше 3");
  return Float64Array.from({ length: n }, (_, j) => (j === 0 || j === n - 1 ? h / 3 : j % 2 === 1 ? 4 * h / 3 : 2 * h / 3));
}

// Weights of the rule on [x_0, x_m] for the Volterra row m: Simpson on an even number of intervals, and
// Simpson on the first m-1 intervals plus a trapezoid on the last one when m is odd (weight 5h/6 at x_{m-1}).
function volterraRow(rule, m, h) {
  const w = new Float64Array(m + 1);
  if (m === 0) return w;
  if (rule === "trapezoid" || m === 1) { w.fill(h); w[0] = h / 2; w[m] = h / 2; return w; }
  if (m % 2 === 0) { w.set(simpsonWeights(m + 1, h)); return w; }
  w.set(simpsonWeights(m, h));
  w[m - 1] += h / 2; w[m] = h / 2;
  return w;
}

// The solution of M c = rhs by LU; the matrix of a problem near a characteristic number is reported, not hidden.
export function solveSystem(M, rhs, n) {
  const fact = luDecompose(M, n);
  if (fact.singular) throw new ProblemError("singular", "матрица системы вырождена: λ равно характеристическому числу или метод не разрешим");
  const c = luSolve(fact, rhs);
  for (const v of c) if (!Number.isFinite(v)) throw new ProblemError("singular", "решение системы бесконечно: матрица вырождена");
  return c;
}

// ---------------------------------------------------------------- quadrature methods

// The method of quadratures for the Fredholm equation: (I - lam K D) y = f on n equidistant nodes.
// `at` is the Nystrom interpolation f(x) + lam sum_j A_j K(x, x_j) y_j.
export function quadratureFredholm(p, n, rule = "trapezoid") {
  const x = uniformGrid(p.lo, p.hi, n), h = (p.hi - p.lo) / (n - 1);
  const w = rule === "simpson" ? simpsonWeights(n, h) : trapezoidWeights(n, h);
  const M = new Float64Array(n * n), rhs = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    rhs[i] = fv(p, x[i]);
    for (let j = 0; j < n; j++) M[i * n + j] = (i === j ? 1 : 0) - p.lam * w[j] * Kv(p, x[i], x[j]);
  }
  const y = solveSystem(M, rhs, n);
  const at = (t) => { let s = 0; for (let j = 0; j < n; j++) s += w[j] * Kv(p, t, x[j]) * y[j]; return fv(p, t) + p.lam * s; };
  return { n, rule, nodes: x, y, matrix: M, cond: cond1(M, n), at };
}

// The scalar equation t = g(t) of a step of the nonlinear Volterra method: the iteration of the note from the
// previous value, then Newton with a numeric derivative if that does not settle.
function solveScalar(g, t0) {
  let t = t0;
  for (let it = 0; it < 200; it++) {
    const next = g(t);
    if (!Number.isFinite(next)) break;
    if (Math.abs(next - t) <= 1e-15 * Math.max(1, Math.abs(next))) return next;
    t = next;
  }
  t = t0;
  for (let it = 0; it < 60; it++) {
    const d = 1e-7 * Math.max(1, Math.abs(t));
    const r = t - g(t), dr = ((t + d - g(t + d)) - (t - d - g(t - d))) / (2 * d);
    if (!(Math.abs(dr) > 0)) break;
    const step = r / dr;
    t -= step;
    if (Math.abs(step) <= 1e-14 * Math.max(1, Math.abs(t))) return t;
  }
  throw new ProblemError("no-root", "уравнение шага не решилось: для итераций нужно A·L < 1, уменьши шаг, взяв больше узлов");
}

// The method of quadratures for the Volterra equation, linear or not: forward substitution on the triangular
// system. `matrix` is the lower triangular matrix of the linear case (only when withMatrix).
export function quadratureVolterra(p, n, rule = "trapezoid", withMatrix = true) {
  const x = uniformGrid(p.lo, p.hi, n), h = (p.hi - p.lo) / (n - 1);
  const y = new Float64Array(n);
  const M = withMatrix && !p.nonlinear ? new Float64Array(n * n) : null;
  y[0] = fv(p, x[0]);
  if (M) M[0] = 1;
  for (let m = 1; m < n; m++) {
    const w = volterraRow(rule, m, h);
    if (p.nonlinear) {
      let c = fv(p, x[m]);
      for (let j = 0; j < m; j++) c += p.lam * w[j] * Kv(p, x[m], x[j], y[j]);
      y[m] = solveScalar((t) => c + p.lam * w[m] * p.K(x[m], x[m], t), y[m - 1]);
    } else {
      let s = 0;
      for (let j = 0; j < m; j++) {
        const kj = Kv(p, x[m], x[j]);
        s += w[j] * kj * y[j];
        if (M) M[m * n + j] = -p.lam * w[j] * kj;
      }
      const kk = Kv(p, x[m], x[m]), d = 1 - p.lam * w[m] * kk;
      if (d === 0) throw new ProblemError("singular", `1 − λ·A·K обращается в нуль в узле ${m + 1}: уменьши шаг`);
      y[m] = (fv(p, x[m]) + p.lam * s) / d;
      if (M) M[m * n + m] = d;
    }
  }
  return { n, rule, nodes: x, y, matrix: M, cond: M ? cond1(M, n) : null, at: null };
}

// Simple iteration y^{k+1} = f + lam K_D y^k on the trapezoid grid from y^0 = f, stopped when
// max|y^{k+1} - y^k| <= tol max|y^{k+1}|, as in the notebook of the course. `matrix` is I - lam K_D.
export function simpleIteration(p, n, { tol = 1e-8, maxIter = 1000 } = {}) {
  const x = uniformGrid(p.lo, p.hi, n), h = (p.hi - p.lo) / (n - 1);
  const rows = Array.from({ length: n }, (_, i) => (p.volterra ? volterraRow("trapezoid", i, h) : trapezoidWeights(n, h)));
  const f = Float64Array.from(x, (t) => fv(p, t));
  const B = p.nonlinear ? null : new Float64Array(n * n);
  if (B) for (let i = 0; i < n; i++) for (let j = 0; j < rows[i].length; j++) B[i * n + j] = rows[i][j] === 0 ? 0 : p.lam * rows[i][j] * Kv(p, x[i], x[j]);
  let y = Float64Array.from(f), iterations = 0, converged = false, diverged = false;
  for (let k = 1; k <= maxIter; k++) {
    const next = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      let s = 0;
      for (let j = 0; j < rows[i].length; j++) s += B ? B[i * n + j] * y[j] : p.lam * rows[i][j] * Kv(p, x[i], x[j], y[j]);
      next[i] = f[i] + s;
    }
    if (p.volterra) next[0] = f[0];
    let diff = 0, nrm = 0;
    for (let i = 0; i < n; i++) { diff = Math.max(diff, Math.abs(next[i] - y[i])); nrm = Math.max(nrm, Math.abs(next[i])); }
    y = next;
    iterations = k;
    if (!Number.isFinite(nrm) || nrm > 1e150) { diverged = true; break; }
    if (diff <= tol * nrm) { converged = true; break; }
  }
  let matrix = null;
  if (B) { matrix = Float64Array.from(B, (v) => -v); for (let i = 0; i < n; i++) matrix[i * n + i] += 1; }
  return { n, nodes: x, y, iterations, converged, diverged, matrix, cond: matrix && !diverged ? cond1(matrix, n) : null, at: null };
}

// ---------------------------------------------------------------- Gauss-Legendre and the reference solution

// Nodes (ascending) and weights of the n-point Gauss-Legendre rule on [-1, 1], by Newton's method on P_n.
export function gaussLegendre(n) {
  const x = new Float64Array(n), w = new Float64Array(n);
  for (let i = 0; i < Math.ceil(n / 2); i++) {
    let z = Math.cos(Math.PI * (i + 0.75) / (n + 0.5)), dp = 1;
    for (let it = 0; it < 100; it++) {
      let p0 = 1, p1 = z;
      for (let k = 2; k <= n; k++) { const p2 = ((2 * k - 1) * z * p1 - (k - 1) * p0) / k; p0 = p1; p1 = p2; }
      dp = n * (z * p1 - p0) / (z * z - 1);
      const dz = p1 / dp;
      z -= dz;
      if (Math.abs(dz) < 1e-16) break;
    }
    let p0 = 1, p1 = z;
    for (let k = 2; k <= n; k++) { const p2 = ((2 * k - 1) * z * p1 - (k - 1) * p0) / k; p0 = p1; p1 = p2; }
    dp = n * (z * p1 - p0) / (z * z - 1);
    x[i] = -z; x[n - 1 - i] = z;
    w[i] = w[n - 1 - i] = 2 / ((1 - z * z) * dp * dp);
  }
  return { x, w };
}

// The composite Gauss-Legendre rule on [a, b]: `panels` equal pieces of `order` nodes each.
export function compositeGauss(a, b, panels, order) {
  const g = gaussLegendre(order), x = [], w = [];
  const h = (b - a) / panels;
  for (let k = 0; k < panels; k++) {
    const mid = a + (k + 0.5) * h;
    for (let i = 0; i < order; i++) { x.push(mid + h / 2 * g.x[i]); w.push(h / 2 * g.w[i]); }
  }
  return { x: Float64Array.from(x), w: Float64Array.from(w) };
}

function nystrom(p, panels, order) {
  const { x, w } = compositeGauss(p.lo, p.hi, panels, order), n = x.length;
  const M = new Float64Array(n * n), rhs = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    rhs[i] = fv(p, x[i]);
    for (let j = 0; j < n; j++) M[i * n + j] = (i === j ? 1 : 0) - p.lam * w[j] * Kv(p, x[i], x[j]);
  }
  const y = solveSystem(M, rhs, n);
  return (t) => { let s = 0; for (let j = 0; j < n; j++) s += w[j] * Kv(p, t, x[j]) * y[j]; return fv(p, t) + p.lam * s; };
}

// `count` points at the centres of equal cells of [a, b]: the ends are never probed, a formula that is 0/0 there still works.
const probeGrid = (p, count = 101) => Float64Array.from({ length: count }, (_, i) => p.lo + (p.hi - p.lo) * (i + 0.5) / count);

// The reference solution of the page: the exact formula if the problem has one, else a Nystrom solution on the
// composite Gauss rule with 1, 2, 4, ... panels of 16 nodes until two neighbours agree (Fredholm), or the
// trapezoid on 2049 and 1025 nodes with a Richardson step and cubic interpolation (Volterra).
// { at, err, exact }: `err` is the distance between the last two stages, an upper estimate of the error.
export function referenceSolution(p) {
  if (p.exact) return { at: p.exact, err: 0, exact: true };
  return p.volterra ? referenceVolterra(p) : referenceFredholm(p);
}

function referenceFredholm(p) {
  const probe = probeGrid(p);
  let prev = null, cur = null, err = Infinity;
  for (const panels of [1, 2, 4, 8, 16, 32]) {
    cur = nystrom(p, panels, 16);
    if (prev) {
      let d = 0, scale = 0;
      for (const t of probe) { const a = cur(t), b = prev(t); d = Math.max(d, Math.abs(a - b)); scale = Math.max(scale, Math.abs(a)); }
      err = d;
      if (d <= 1e-14 * Math.max(scale, 1e-300)) break;
    }
    prev = cur;
  }
  return { at: cur, err, exact: false };
}

function referenceVolterra(p) {
  const fine = quadratureVolterra(p, 2049, "trapezoid", false), coarse = quadratureVolterra(p, 1025, "trapezoid", false);
  const m = 1025, ys = new Float64Array(m);
  let corr = 0;
  for (let k = 0; k < m; k++) { ys[k] = (4 * fine.y[2 * k] - coarse.y[k]) / 3; corr = Math.max(corr, Math.abs(ys[k] - fine.y[2 * k])); }
  const h = (p.hi - p.lo) / (m - 1);
  const at = (t) => {
    let i = Math.floor((t - p.lo) / h);
    i = Math.min(Math.max(i, 1), m - 3);
    let s = 0;
    for (let a = i - 1; a <= i + 2; a++) {
      let term = ys[a];
      for (let b = i - 1; b <= i + 2; b++) if (b !== a) term *= (t - (p.lo + b * h)) / ((a - b) * h);
      s += term;
    }
    return s;
  };
  return { at, err: corr, exact: false };
}

// max |approx(x) - ref(x)| over `count` equidistant points of [a, b], and over given points when `points` is set.
export function maxError(approx, ref, a, b, count = 401, points = null) {
  const xs = points || Array.from({ length: count }, (_, i) => a + (b - a) * i / (count - 1));
  let worst = 0;
  for (const t of xs) worst = Math.max(worst, Math.abs(approx(t) - ref(t)));
  return worst;
}

// max |y_i - ref(x_i)| at the nodes of a node-wise solution (the quadratures, the simple iteration).
export function nodeError(sol, ref) {
  let worst = 0;
  for (let i = 0; i < sol.n; i++) worst = Math.max(worst, Math.abs(sol.y[i] - ref(sol.nodes[i])));
  return worst;
}

// ---------------------------------------------------------------- Taylor jets: derivatives of a formula without symbolic algebra

// A jet is the array of the Taylor coefficients c_0..c_D of a function of x at a point. The tree of numkit's parser
// is evaluated on jets, so the series of K(x, s) in x needs no symbolic differentiation and no eval.
const jzero = (D) => new Float64Array(D + 1);
const jconst = (v, D) => { const r = jzero(D); r[0] = v; return r; };
const jadd = (a, b) => a.map((v, i) => v + b[i]);
const jscale = (a, c) => a.map((v) => c * v);
function jmul(a, b) {
  const r = jzero(a.length - 1);
  for (let k = 0; k < r.length; k++) { let s = 0; for (let i = 0; i <= k; i++) s += a[i] * b[k - i]; r[k] = s; }
  return r;
}
function jnotAnalytic(what) {
  return new ProblemError("not-analytic", `ядро не раскладывается в ряд Тейлора по x: ${what}`, "kernel");
}
function jdiv(a, b) {
  if (b[0] === 0) throw jnotAnalytic("деление на нуль в центре разложения");
  const r = jzero(a.length - 1);
  for (let k = 0; k < r.length; k++) { let s = a[k]; for (let j = 1; j <= k; j++) s -= b[j] * r[k - j]; r[k] = s / b[0]; }
  return r;
}
function jexp(a) {
  const D = a.length - 1, e = jzero(D);
  e[0] = Math.exp(a[0]);
  for (let k = 1; k <= D; k++) { let s = 0; for (let j = 1; j <= k; j++) s += j * a[j] * e[k - j]; e[k] = s / k; }
  return e;
}
function jlog(a) {
  if (!(a[0] > 0)) throw jnotAnalytic("логарифм неположительного числа в центре разложения");
  const D = a.length - 1, l = jzero(D);
  l[0] = Math.log(a[0]);
  for (let k = 1; k <= D; k++) { let s = 0; for (let j = 1; j < k; j++) s += j * l[j] * a[k - j]; l[k] = (a[k] - s / k) / a[0]; }
  return l;
}
function jsincos(a, hyper) {
  const D = a.length - 1, s = jzero(D), c = jzero(D);
  s[0] = hyper ? Math.sinh(a[0]) : Math.sin(a[0]); c[0] = hyper ? Math.cosh(a[0]) : Math.cos(a[0]);
  for (let k = 1; k <= D; k++) {
    let ss = 0, cc = 0;
    for (let j = 1; j <= k; j++) { ss += j * a[j] * c[k - j]; cc += j * a[j] * s[k - j]; }
    s[k] = ss / k; c[k] = (hyper ? cc : -cc) / k;
  }
  return [s, c];
}
function jsqrt(a) {
  if (!(a[0] > 0)) throw jnotAnalytic("корень из неположительного числа в центре разложения");
  const D = a.length - 1, r = jzero(D);
  r[0] = Math.sqrt(a[0]);
  for (let k = 1; k <= D; k++) { let s = a[k]; for (let j = 1; j < k; j++) s -= r[j] * r[k - j]; r[k] = s / (2 * r[0]); }
  return r;
}
// integral of a' q: the series of F with F' = a' q, F_0 = f0
function jintegrate(a, q, f0) {
  const D = a.length - 1, r = jzero(D);
  r[0] = f0;
  for (let k = 1; k <= D; k++) { let s = 0; for (let j = 1; j <= k; j++) s += j * a[j] * q[k - j]; r[k] = s / k; }
  return r;
}
function jpow(a, b) {
  const D = a.length - 1, constantB = b.slice(1).every((v) => v === 0), e = b[0];
  if (constantB && Number.isInteger(e) && Math.abs(e) <= 64) {
    let r = jconst(1, D), base = a, n = Math.abs(e);
    while (n > 0) { if (n & 1) r = jmul(r, base); base = jmul(base, base); n >>= 1; }
    return e < 0 ? jdiv(jconst(1, D), r) : r;
  }
  if (!(a[0] > 0)) throw jnotAnalytic("степень с нецелым показателем от неположительного числа в центре разложения");
  return jexp(jmul(b, jlog(a)));
}

function jetEval(node, env, D) {
  switch (node.type) {
    case "num": return jconst(node.value, D);
    case "var": return env[node.name];
    case "neg": return jscale(jetEval(node.a, env, D), -1);
    case "bin": {
      const a = jetEval(node.a, env, D), b = jetEval(node.b, env, D);
      if (node.op === "+") return jadd(a, b);
      if (node.op === "-") return jadd(a, jscale(b, -1));
      if (node.op === "*") return jmul(a, b);
      if (node.op === "/") return jdiv(a, b);
      return jpow(a, b);
    }
    default: {
      const a = jetEval(node.a, env, D);
      switch (node.name) {
        case "exp": return jexp(a);
        case "log": return jlog(a);
        case "sqrt": return jsqrt(a);
        case "sin": return jsincos(a, false)[0];
        case "cos": return jsincos(a, false)[1];
        case "tan": { const [s, c] = jsincos(a, false); return jdiv(s, c); }
        case "ctg": { const [s, c] = jsincos(a, false); return jdiv(c, s); }
        case "sinh": return jsincos(a, true)[0];
        case "cosh": return jsincos(a, true)[1];
        case "tanh": { const [s, c] = jsincos(a, true); return jdiv(s, c); }
        case "abs":
          if (a[0] === 0) throw jnotAnalytic("модуль не раскладывается в нуле");
          return jscale(a, Math.sign(a[0]));
        case "atan": return jintegrate(a, jdiv(jconst(1, D), jadd(jconst(1, D), jmul(a, a))), Math.atan(a[0]));
        case "asin": return jintegrate(a, jdiv(jconst(1, D), jsqrt(jadd(jconst(1, D), jscale(jmul(a, a), -1)))), Math.asin(a[0]));
        case "acos": return jintegrate(a, jscale(jdiv(jconst(1, D), jsqrt(jadd(jconst(1, D), jscale(jmul(a, a), -1)))), -1), Math.acos(a[0]));
        default: throw jnotAnalytic(`функция ${node.name} не поддержана`);
      }
    }
  }
}

// The function s -> [kappa_0(s), ..., kappa_D(s)], kappa_k = (1/k!) d^k K / dx^k at x = x0, from the text of K(x, s).
export function kernelTaylor(src, D, x0 = 0) {
  const tree = parseExpression(src, ["x", "s"]);
  const x = jzero(D);
  x[0] = x0; if (D >= 1) x[1] = 1;
  return (s) => jetEval(tree, { x, s: jconst(s, D) }, D);
}

// ---------------------------------------------------------------- degenerate kernels

// Taylor series of the kernel in x about x0, cut after the first `terms` non-zero terms:
// K_M(x, s) = sum_i (x - x0)^{p_i} beta_i(s), beta_i(s) = kappa_{p_i}(s). The unknowns c solve
// (I - lam a) c = f with a_ij = int beta_i alpha_j ds, and y_M = f + lam sum c_i alpha_i (the note
// "Метод вырожденных ядер"). A term counts as zero when its largest contribution on the box is below 1e-15 of
// the size of K; `exhausted` says that fewer than `terms` terms are left, the series ends.
export function degenerateKernel(p, terms, { center = 0 } = {}) {
  const Dmax = Math.min(40, 3 * terms + 8);
  const taylor = kernelTaylor(p.kernelText, Dmax, center);
  const cache = new Map();
  const coeffs = (s) => { let v = cache.get(s); if (!v) { v = taylor(s); cache.set(s, v); } return v; };
  const probe = probeGrid(p, 17);
  const width = Math.max(Math.abs(p.lo - center), Math.abs(p.hi - center), 1e-300);
  let kscale = 0;
  for (const s of probe) for (const x of probe) kscale = Math.max(kscale, Math.abs(finite(p.K(x, s), "K")));
  const degrees = [];
  for (let k = 0; k <= Dmax && degrees.length < terms; k++) {
    let big = 0;
    for (const s of probe) big = Math.max(big, Math.abs(coeffs(s)[k]));
    if (big * width ** k > 1e-15 * kscale) degrees.push(k);
  }
  const m = degrees.length;
  if (m === 0) throw new ProblemError("zero-kernel", "ядро равно нулю: приближать нечего", "kernel");
  const alpha = degrees.map((d) => (x) => (x - center) ** d);
  const beta = degrees.map((d) => (s) => coeffs(s)[d]);
  const a = new Float64Array(m * m), fvec = new Float64Array(m);
  for (let i = 0; i < m; i++) {
    for (let j = 0; j < m; j++) a[i * m + j] = integrate((s) => beta[i](s) * alpha[j](s), p.lo, p.hi).value;
    fvec[i] = integrate((s) => beta[i](s) * fv(p, s), p.lo, p.hi).value;
  }
  const M = new Float64Array(m * m);
  for (let i = 0; i < m; i++) for (let j = 0; j < m; j++) M[i * m + j] = (i === j ? 1 : 0) - p.lam * a[i * m + j];
  const c = solveSystem(M, fvec, m);
  const at = (x) => { let s = 0; for (let i = 0; i < m; i++) s += c[i] * alpha[i](x); return fv(p, x) + p.lam * s; };
  const kernelPart = (x, s) => { let t = 0; for (let i = 0; i < m; i++) t += alpha[i](x) * beta[i](s); return t; };
  return { n: m, degrees, exhausted: m < terms, c, matrix: M, cond: cond1(M, m), at, kernelPart, a, center };
}

// The estimates of the note: ||A|| = max_x int |K| ds and ||A - A_M|| = max_x int |K - K_M| ds, on 41 values of x,
// then q = |lam| ||A - A_M|| / (1 - |lam| ||A||) and the bound q/(1-q) ||y||, valid for |lam| ||A|| < 1 and q < 1.
export function degenerateBound(p, deg, yNorm) {
  const xs = uniformGrid(p.lo, p.hi, 41);
  const rowNorm = (g) => xs.reduce((m, x) => Math.max(m, integrateSplit((s) => Math.abs(g(x, s)), p.lo, p.hi, x, { tol: 1e-9, maxIntervals: 60 }).value), 0);
  const normA = rowNorm((x, s) => Kv(p, x, s)), normDiff = rowNorm((x, s) => Kv(p, x, s) - deg.kernelPart(x, s));
  const lamA = Math.abs(p.lam) * normA;
  if (!(lamA < 1)) return { normA, normDiff, q: null, bound: null };
  const q = Math.abs(p.lam) * normDiff / (1 - lamA);
  return { normA, normDiff, q, bound: q < 1 ? q / (1 - q) * yNorm : null };
}

// ---------------------------------------------------------------- projection methods

// N functions of a family on [a, b]: shifted Legendre or Chebyshev (first kind, no weight) polynomials of the
// variable t = (2x - a - b)/(b - a), or the natural monomials x^j. All start at degree 0.
export function basisFunctions(kind, N, a, b) {
  if (kind === "monomial") return Array.from({ length: N }, (_, j) => (x) => x ** j);
  const t = (x) => (2 * x - a - b) / (b - a);
  return Array.from({ length: N }, (_, j) => (x) => {
    const u = t(x);
    if (j === 0) return 1;
    let p0 = 1, p1 = u;
    for (let k = 1; k < j; k++) {
      const p2 = kind === "legendre" ? ((2 * k + 1) * u * p1 - k * p0) / (k + 1) : 2 * u * p1 - p0;
      p0 = p1; p1 = p2;
    }
    return p1;
  });
}

// numkit's adaptive integral of f over [a, b], cut at `at` when that lies inside: a kernel with a kink on the diagonal s = x
// (min(x, s), |x - s|) has its kink at a known place, and a rule that never samples beyond the kink near an end of the
// interval would take the first estimate for settled. Returns { value, err }.
function integrateSplit(f, a, b, at, opts) {
  if (!(at > a && at < b)) return integrate(f, a, b, opts);
  const l = integrate(f, a, at, opts), r = integrate(f, at, b, opts);
  return { value: l.value + r.value, err: l.err + r.err };
}

// For each point x the integrals int K(x, s) g_j(s) ds of all functions at once, kept per x: the entries of a
// projection matrix share them. `worst` is the largest error estimate of numkit's quadrature seen so far.
function innerOperator(p, funcs) {
  const cache = new Map();
  const op = {
    worst: 0,
    at(x) {
      let v = cache.get(x);
      if (!v) {
        v = new Float64Array(funcs.length);
        funcs.forEach((g, j) => {
          const r = integrateSplit((s) => Kv(p, x, s) * g(s), p.lo, p.hi, x);
          op.worst = Math.max(op.worst, r.err);
          v[j] = r.value;
        });
        cache.set(x, v);
      }
      return v;
    },
  };
  return op;
}

// The Galerkin-Petrov method with u0 = 0 or u0 = f (`u0` is "zero" or "f"): y = u0 + sum c_j phi_j with
// (y - lam K y - f, psi_i) = 0, the matrix a_ij = (phi_j, psi_i) - lam (K phi_j, psi_i) and the right-hand side
// (f - u0 + lam K u0, psi_i). Built once for Nmax functions: the leading n x n block with the first n entries of the
// right-hand side is the method with n functions, so `solution(n)` costs one solve.
// The outer integrals over x run on one composite Gauss rule shared by all entries, with 2, 4, 8, 16 panels of
// 16 nodes until the matrix and the right-hand side change by less than 1e-13 of their largest entry: nested
// adaptive quadratures would chase the rounding noise of the inner ones. The inner integrals K phi_j are numkit's.
export function galerkinSeries(p, Nmax, { phi, psi, u0 = "zero" }) {
  const u0f = u0 === "f" ? (x) => fv(p, x) : () => 0;
  const op = innerOperator(p, u0 === "f" ? [...phi, u0f] : phi);
  const level = (panels) => {
    const { x, w } = compositeGauss(p.lo, p.hi, panels, 16);
    const G = new Float64Array(Nmax * Nmax), rhs = new Float64Array(Nmax);
    for (let q = 0; q < x.length; q++) {
      const inner = op.at(x[q]), fq = u0 === "f" ? 0 : fv(p, x[q]);
      const pv = psi.map((g) => w[q] * g(x[q])), fv1 = phi.map((g) => g(x[q]));
      for (let i = 0; i < Nmax; i++) {
        for (let j = 0; j < Nmax; j++) G[i * Nmax + j] += pv[i] * (fv1[j] - p.lam * inner[j]);
        rhs[i] += pv[i] * (u0 === "f" ? p.lam * inner[Nmax] : fq);
      }
    }
    return { G, rhs };
  };
  let cur = level(2);
  for (const panels of [4, 8, 16]) {
    const next = level(panels);
    let scale = 0, change = 0;
    for (const [a, b] of [[cur.G, next.G], [cur.rhs, next.rhs]]) for (let k = 0; k < a.length; k++) { scale = Math.max(scale, Math.abs(b[k])); change = Math.max(change, Math.abs(a[k] - b[k])); }
    cur = next;
    if (change <= 1e-13 * scale) break;
  }
  const { G, rhs } = cur;
  return {
    Nmax,
    solution(n) {
      const M = new Float64Array(n * n);
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) M[i * n + j] = G[i * Nmax + j];
      const c = solveSystem(M, rhs.slice(0, n), n);
      const at = (x) => { let s = u0f(x); for (let j = 0; j < n; j++) s += c[j] * phi[j](x); return s; };
      return { n, c, matrix: M, cond: cond1(M, n), at, nodes: null };
    },
  };
}

// n collocation points of [a, b]: "equidistant" with the ends included, or "chebyshev",
// x_i = (a+b)/2 - (b-a)/2 cos((2i+1) pi / (2n)).
export function collocationNodes(kind, n, a, b) {
  if (kind === "chebyshev") return Float64Array.from({ length: n }, (_, i) => (a + b) / 2 - (b - a) / 2 * Math.cos((2 * i + 1) * Math.PI / (2 * n)));
  return uniformGrid(a, b, n);
}

// The collocation method: y = sum c_j phi_j with the residual zero at the nodes,
// M_ij = phi_j(x_i) - lam int K(x_i, s) phi_j(s) ds, M c = f(x_i).
export function collocation(p, phi, nodes) {
  const n = phi.length, op = innerOperator(p, phi);
  const M = new Float64Array(n * n), rhs = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    const inner = op.at(nodes[i]);
    rhs[i] = fv(p, nodes[i]);
    for (let j = 0; j < n; j++) M[i * n + j] = phi[j](nodes[i]) - p.lam * inner[j];
  }
  const c = solveSystem(M, rhs, n);
  const at = (x) => { let s = 0; for (let j = 0; j < n; j++) s += c[j] * phi[j](x); return s; };
  return { n, c, matrix: M, cond: cond1(M, n), at, nodes };
}

// ================================================================ spectral problems

// Conventions of the notes of the topic "Спектральные задачи": a real symmetric kernel K(x, s) on [a, b], the operator
// (Ty)(x) = int K(x,s) y(s) ds, the characteristic numbers lambda_j = 1/mu_j with |lambda_1| <= |lambda_2| <= ... and the
// orthonormal eigenfunctions y_j. The kernel is held as a problem object of the second-kind section (lam = 1), so the
// inner integrals and the composite Gauss rule are the same code.

export function makeKernel({ lo, hi, kernel }) {
  if (!(Number.isFinite(lo) && Number.isFinite(hi) && lo < hi)) throw new ProblemError("bad-interval", "отрезок [a; b] должен быть конечным, и a < b", "interval");
  let K;
  try { K = compileExpression(kernel, ["x", "s"]); } catch (e) { if (e instanceof ExprError) e.field = "kernel"; throw e; }
  return { kind: "fredholm", nonlinear: false, volterra: false, lo, hi, lam: 1, kernelText: kernel, K, f: () => 0, exact: null };
}

// max |K(x,s) - K(s,x)| over a count x count grid, relative to max |K|: zero for a symmetric kernel.
export function symmetryDefect(k, count = 17) {
  const g = probeGrid(k, count);
  let d = 0, m = 0;
  for (const x of g) for (const s of g) { const a = Kv(k, x, s), b = Kv(k, s, x); d = Math.max(d, Math.abs(a - b)); m = Math.max(m, Math.abs(a), Math.abs(b)); }
  return m > 0 ? d / m : 0;
}

// The Nystrom matrix of a symmetric kernel on the composite Gauss rule, symmetrised as S = W^{1/2} K W^{1/2}: its eigenvalues
// are the numbers mu_j of T, an eigenvector v gives the values y_i = v_i / sqrt(w_i) of an eigenfunction.
export function symmetricNystrom(k, panels, order = 16) {
  const { x, w } = compositeGauss(k.lo, k.hi, panels, order), n = x.length;
  const sw = Float64Array.from(w, Math.sqrt), S = new Float64Array(n * n);
  for (let i = 0; i < n; i++) for (let j = i; j < n; j++) { const v = sw[i] * Kv(k, x[i], x[j]) * sw[j]; S[i * n + j] = v; S[j * n + i] = v; }
  return { x, w, sw, S, n };
}

// The unit eigenvector of a symmetric matrix for the eigenvalue `mu` by inverse iteration with a shift a hair off mu.
function inverseIteration(S, n, mu) {
  const M = Float64Array.from(S), shift = mu * (1 + 1e-10) + (mu === 0 ? 1e-300 : 0);
  for (let i = 0; i < n; i++) M[i * n + i] -= shift;
  const fact = luDecompose(M, n);
  let v = Float64Array.from({ length: n }, (_, i) => Math.sin(1.7 * i + 0.3) + 0.1);
  for (let it = 0; it < 4; it++) {
    if (fact.singular) break;
    v = luSolve(fact, v);
    const nrm = Math.hypot(...v);
    v = v.map((c) => c / nrm);
  }
  const nrm = Math.hypot(...v);
  return v.map((c) => c / nrm);
}

// The best estimate of a limit from values on meshes of step h, h/2, h/4, ...: the last value, or the last entry of a
// Richardson table for an error of order h^2 (and then h^4), whichever has the smallest distance to its predecessor.
// A kernel with a kink on the diagonal converges like h^2, a smooth one is settled early and stays as it is.
function extrapolate(seq) {
  const t1 = seq.slice(1).map((v, i) => (4 * v - seq[i]) / 3), t2 = t1.slice(1).map((v, i) => (16 * v - t1[i]) / 15);
  const cand = [seq, t1, t2].filter((a) => a.length >= 2).map((a) => ({ value: a[a.length - 1], err: Math.abs(a[a.length - 1] - a[a.length - 2]) }));
  if (cand[0].err <= 1e-13 * Math.abs(cand[0].value)) return cand[0];
  return cand.reduce((b, c) => (c.err < b.err ? c : b));
}

// The first `count` characteristic numbers (smallest |lambda|) of a symmetric kernel: eigenvalues of the Nystrom matrix on
// 8, 16, ... 256 nodes, extrapolated. { lambda, mu, err, eigenfunction(j) }; `err` is the distance of the last two stages.
export function characteristicNumbers(k, count = 6) {
  const levels = [1, 2, 4, 8, 16, 32].map((panels) => {
    const ny = symmetricNystrom(k, panels, 8);
    const ev = eigenvalues(ny.S, ny.n).map((z) => z.re).sort((a, b) => Math.abs(b) - Math.abs(a));
    return { ny, ev };
  });
  const top = levels[levels.length - 1];
  const lambda = [], err = [];
  for (let j = 0; j < count && j < top.ev.length; j++) {
    if (!(Math.abs(top.ev[j]) > 1e-12 * Math.abs(top.ev[0]))) break;
    const e = extrapolate(levels.filter((l) => j < l.ev.length).map((l) => 1 / l.ev[j]));
    lambda.push(e.value); err.push(e.err);
  }
  const cache = new Map();
  const eigenfunction = (j) => {
    if (cache.has(j)) return cache.get(j);
    const { ny, ev } = top, v = inverseIteration(ny.S, ny.n, ev[j]);
    const y = Float64Array.from(v, (c, i) => c / ny.sw[i]);
    const mu = ev[j];
    const raw = (t) => { let s = 0; for (let i = 0; i < ny.n; i++) s += ny.w[i] * Kv(k, t, ny.x[i]) * y[i]; return s / mu; };
    let big = 0, sign = 1;
    for (let i = 0; i < ny.n; i += 3) if (Math.abs(y[i]) > big) { big = Math.abs(y[i]); sign = Math.sign(y[i]); }
    const fn = (t) => sign * raw(t);
    cache.set(j, fn);
    return fn;
  };
  return { lambda, mu: lambda.map((l) => 1 / l), err, eigenfunction };
}

// Kellogg's method (the note "Метод Келлога"): omega_n = T omega_{n-1} on the composite Gauss nodes, omega_0 = omega.
// ratios[n-1] = ||omega_{n-1}|| / ||omega_n|| (n = 1..steps), roots[n-1] = 1 / ||omega_n||^{1/n}, both approach lambda_k from
// above for a positive kernel. The norms are kept as logarithms and the iterates normalised, so no step overflows.
// `vectors[n]` is omega_n / ||omega_n|| at the nodes `x`.
export function kellogg(k, omega, steps, { panels = 16, order = 16 } = {}) {
  const { x, w } = compositeGauss(k.lo, k.hi, panels, order), n = x.length;
  const Kw = new Float64Array(n * n);
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) Kw[i * n + j] = Kv(k, x[i], x[j]) * w[j];
  const norm = (v) => Math.sqrt(v.reduce((s, c, i) => s + w[i] * c * c, 0));
  // a bound for the size of the operator: a step that returns less than 1e-12 of it is a rounding residue, omega is in the kernel
  let opNorm = 0;
  for (let i = 0; i < n; i++) { let s = 0; for (let j = 0; j < n; j++) s += Math.abs(Kw[i * n + j]); opNorm = Math.max(opNorm, s); }
  let v = Float64Array.from(x, (t) => finite(omega(t), `ω(${short(t)})`));
  const n0 = norm(v);
  if (!(n0 > 0)) throw new ProblemError("zero-omega", "начальная функция ω равна нулю", "omega");
  v = v.map((c) => c / n0);
  let logNorm = Math.log(n0);
  const ratios = [], roots = [], vectors = [v];
  for (let it = 1; it <= steps; it++) {
    const u = new Float64Array(n);
    for (let i = 0; i < n; i++) { let s = 0; for (let j = 0; j < n; j++) s += Kw[i * n + j] * v[j]; u[i] = s; }
    const s = norm(u);
    if (!(s > 1e-12 * opNorm)) throw new ProblemError("zero-omega", `T ω_${it - 1} равна нулю: ω принадлежит ядру оператора`, "omega");
    ratios.push(1 / s);
    logNorm += Math.log(s);
    roots.push(Math.exp(-logNorm / it));
    v = u.map((c) => c / s);
    vectors.push(v);
  }
  return { x, w, ratios, roots, vectors };
}

// The method of traces (the note "Метод следов"): A_2m = ||S^m||_F^2 on the composite Gauss nodes, S the symmetric Nystrom
// matrix. a[i] = A_{2(i+1)}, lower[i] = A_{2m}^{-1/(2m)} and upper[i] = sqrt(A_{2m} / A_{2m+2}) for m = i + 1 = 1..M, the
// bounds (4) of the note: lower <= |lambda_1| <= upper.
export function traces(k, M, { panels = 16, order = 16 } = {}) {
  const { S, n } = symmetricNystrom(k, panels, order);
  const a = [];
  let P = Float64Array.from(S);
  for (let m = 1; m <= M + 1; m++) {
    a.push(P.reduce((s, v) => s + v * v, 0));
    if (m <= M) {
      const R = new Float64Array(n * n);
      for (let i = 0; i < n; i++) for (let l = 0; l < n; l++) { const pil = P[i * n + l]; if (pil === 0) continue; for (let j = 0; j < n; j++) R[i * n + j] += pil * S[l * n + j]; }
      P = R;
    }
  }
  return { a, lower: Array.from({ length: M }, (_, i) => a[i] ** (-1 / (2 * (i + 1)))), upper: Array.from({ length: M }, (_, i) => Math.sqrt(a[i] / a[i + 1])) };
}

// Cholesky factor L (lower, M = L L^T) of a symmetric positive definite matrix, or null.
export function cholesky(M, n) {
  const L = new Float64Array(n * n);
  for (let j = 0; j < n; j++) {
    let d = M[j * n + j];
    for (let c = 0; c < j; c++) d -= L[j * n + c] ** 2;
    if (!(d > 0)) return null;
    L[j * n + j] = Math.sqrt(d);
    for (let i = j + 1; i < n; i++) {
      let s = M[i * n + j];
      for (let c = 0; c < j; c++) s -= L[i * n + c] * L[j * n + c];
      L[i * n + j] = s / L[j * n + j];
    }
  }
  return L;
}

// Ritz's method (the note "Метод Ритца") for the kernel: V_n = span{phi_1..phi_n}, G_jk = (K phi_k, phi_j), M_jk = (phi_k, phi_j),
// the roots of det(G - sigma M) = 0 and lambda = 1/sigma. Built once for Nmax functions and read from the leading blocks, as the
// Galerkin series; the outer integrals use the shared composite Gauss rule, the inner ones numkit's adaptive quadrature.
// solution(n) gives { sigma, lambda } with the positive and negative numbers sorted by |lambda| ascending, and eigenfunction(i).
export function ritzSeries(k, Nmax, phi) {
  const op = innerOperator(k, phi);
  const level = (panels) => {
    const { x, w } = compositeGauss(k.lo, k.hi, panels, 16);
    const G = new Float64Array(Nmax * Nmax), M = new Float64Array(Nmax * Nmax);
    for (let q = 0; q < x.length; q++) {
      const inner = op.at(x[q]), pv = phi.map((g) => g(x[q]));
      for (let j = 0; j < Nmax; j++) for (let l = 0; l < Nmax; l++) { G[j * Nmax + l] += w[q] * pv[j] * inner[l]; M[j * Nmax + l] += w[q] * pv[j] * pv[l]; }
    }
    return { G, M };
  };
  let cur = level(2);
  for (const panels of [4, 8, 16]) {
    const next = level(panels);
    let scale = 0, change = 0;
    for (const [a, b] of [[cur.G, next.G], [cur.M, next.M]]) for (let i = 0; i < a.length; i++) { scale = Math.max(scale, Math.abs(b[i])); change = Math.max(change, Math.abs(a[i] - b[i])); }
    cur = next;
    if (change <= 1e-13 * scale) break;
  }
  const { G, M } = cur;
  return {
    Nmax,
    solution(n) {
      const Gn = new Float64Array(n * n), Mn = new Float64Array(n * n);
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { Gn[i * n + j] = (G[i * Nmax + j] + G[j * Nmax + i]) / 2; Mn[i * n + j] = (M[i * Nmax + j] + M[j * Nmax + i]) / 2; }
      const L = cholesky(Mn, n);
      if (!L) throw new ProblemError("dependent", "базисные функции линейно зависимы или матрица Грама вырождена: уменьши число функций", "basis");
      // B = L^{-1} G L^{-T}, symmetric, has the eigenvalues of the pencil
      const solveL = (cols) => { const out = new Float64Array(n * n); for (let c = 0; c < n; c++) for (let i = 0; i < n; i++) { let s = cols[i * n + c]; for (let j = 0; j < i; j++) s -= L[i * n + j] * out[j * n + c]; out[i * n + c] = s / L[i * n + i]; } return out; };
      const T = solveL(Gn), Tt = Float64Array.from({ length: n * n }, (_, k2) => T[(k2 % n) * n + Math.floor(k2 / n)]);
      const B0 = solveL(Tt), B = Float64Array.from({ length: n * n }, (_, k2) => (B0[k2] + B0[(k2 % n) * n + Math.floor(k2 / n)]) / 2);
      const ev = eigenvalues(B, n).map((z) => z.re).sort((a, b) => Math.abs(b) - Math.abs(a));
      // a root below the rounding noise of the matrices is zero: sigma = 0 is dropped, as the note says
      let gmax = 0, mmin = Infinity;
      for (const v of G) gmax = Math.max(gmax, Math.abs(v));
      for (let i = 0; i < n; i++) mmin = Math.min(mmin, Mn[i * n + i]);
      const keep = ev.filter((s) => Math.abs(s) > 1e-11 * gmax / mmin);
      return {
        n, sigma: keep, lambda: keep.map((s) => 1 / s),
        eigenfunction(i) {
          const z = inverseIteration(B, n, keep[i]), c = new Float64Array(n);
          for (let r = n - 1; r >= 0; r--) { let s = z[r]; for (let j = r + 1; j < n; j++) s -= L[j * n + r] * c[j]; c[r] = s / L[r * n + r]; }
          return (x) => { let s = 0; for (let j = 0; j < n; j++) s += c[j] * phi[j](x); return s; };
        },
      };
    },
  };
}

// ---------------------------------------------------------------- the rotation method of Jacobi

// S(A) = the sum of squares of the off-diagonal entries.
export function offDiagonalSum(A, n) {
  let s = 0;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j) s += A[i * n + j] ** 2;
  return s;
}

// The method of the note "Метод вращений Якоби" for a real symmetric matrix: A_{p+1} = Q_p^T A_p Q_p, the pair (k, l) with the
// largest |a_kl| (the first one in row-major order among equals), tan 2phi = 2 a_kl / (a_kk - a_ll), phi = pi/4 when a_kk = a_ll,
// Q the rotation with q_kk = q_ll = cos phi, q_kl = -sin phi, q_lk = sin phi. The loop stops when all |a_ij| <= tol * max|a|
// or after maxSteps. steps[p] describes the rotation p -> p + 1 and holds A_{p+1} and S(A_{p+1}); `T` is Q_0 Q_1 ... Q_{P-1}.
export function jacobiRotations(A, n, { tol = 1e-12, maxSteps = 200 } = {}) {
  let cur = Float64Array.from(A);
  const scale = cur.reduce((m, v) => Math.max(m, Math.abs(v)), 0);
  let T = Float64Array.from({ length: n * n }, (_, i) => (i % (n + 1) === 0 ? 1 : 0));
  const steps = [], S0 = offDiagonalSum(cur, n);
  const mul = (X, Y) => { const R = new Float64Array(n * n); for (let i = 0; i < n; i++) for (let l = 0; l < n; l++) for (let j = 0; j < n; j++) R[i * n + j] += X[i * n + l] * Y[l * n + j]; return R; };
  for (let p = 0; p < maxSteps; p++) {
    let k = 0, l = 1, big = -1;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (Math.abs(cur[i * n + j]) > big) { big = Math.abs(cur[i * n + j]); k = i; l = j; }
    if (!(big > tol * scale)) break;
    const akl = cur[k * n + l], diff = cur[k * n + k] - cur[l * n + l];
    const phi = diff === 0 ? Math.sign(akl) * Math.PI / 4 : Math.atan2(2 * akl, diff) / 2;
    const c = Math.cos(phi), s = Math.sin(phi);
    const Q = Float64Array.from({ length: n * n }, (_, i) => (i % (n + 1) === 0 ? 1 : 0));
    Q[k * n + k] = c; Q[l * n + l] = c; Q[k * n + l] = -s; Q[l * n + k] = s;
    const Qt = Float64Array.from({ length: n * n }, (_, i) => Q[(i % n) * n + Math.floor(i / n)]);
    cur = mul(Qt, mul(cur, Q));
    for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) { const m = (cur[i * n + j] + cur[j * n + i]) / 2; cur[i * n + j] = m; cur[j * n + i] = m; }
    T = mul(T, Q);
    steps.push({ p: p + 1, k, l, akl, phi, A: Float64Array.from(cur), S: offDiagonalSum(cur, n) });
  }
  const rho = n > 1 ? 1 - 2 / (n * (n - 1)) : 0;
  return { n, A0: Float64Array.from(A), S0, rho, steps, final: cur, T, diagonal: Float64Array.from({ length: n }, (_, i) => cur[i * n + i]) };
}

// The number of rotations from the note that guarantees |lambda_k - a_kk| <= eps: p >= n(n-1)/2 ln(n^2 S0 / eps^2).
export const jacobiStepsBound = (n, S0, eps) => Math.ceil(n * (n - 1) / 2 * Math.log(n * n * S0 / (eps * eps)));
