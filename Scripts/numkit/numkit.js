// Numerical mechanisms shared by the course pages of the vault: pure functions, no DOM.
// One ES module. A course build inlines it with `export` removed (see README.md),
// and `node --test` imports it as is (numkit.test.mjs).
//
// Inside: a formula parser without eval, adaptive Gauss-Kronrod quadrature, LU, eigenvalues of a real
// matrix, the characteristic polynomial, the text of a degenerate-kernel problem. The numbers of a
// page are written by sandbox_kit's number.js, which every page carries.
// A matrix is a flat row-major array of n*n numbers.

// The machine epsilon: exported because a course module that inlines next to this one must not declare it again.
export const EPS = Number.EPSILON;

// ---------------------------------------------------------------- expressions

// A small safe parser for the formulas typed on the pages: no eval, no Function.
// Numbers (a comma or a point as the decimal mark, an exponent 1e-3), the variables the caller lists
// (parseExpression: x and t by default; compileExpression also knows s and y, and any name in `names`), the
// constants pi and e, the operators + - * / ^, brackets and the functions
//   sin cos tan ctg exp log sqrt abs asin acos atan sinh cosh tanh
// with the aliases ln = log (natural), tg = tan, cot = ctg, arcsin, arccos, arctg, arctan, sh, ch, th.
// Precedence from the loosest: + -, then * /, then unary minus, then ^ (right-associative, and its
// exponent may carry a unary sign): -x^2 = -(x^2), 2^3^2 = 2^9, 2^-1 = 0.5, 1-2-3 = -4, 8/2/2 = 2.
// Multiplication is never implied: 2x is an error that says so.

export class ExprError extends Error {
  constructor(code, message, pos) {
    super(message);
    this.code = code;
    this.pos = pos;
  }
}

const FUNCTIONS = {
  sin: Math.sin, cos: Math.cos, tan: Math.tan, ctg: (v) => 1 / Math.tan(v), exp: Math.exp, log: Math.log, sqrt: Math.sqrt, abs: Math.abs,
  asin: Math.asin, acos: Math.acos, atan: Math.atan, sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh,
};
const ALIASES = { ln: "log", tg: "tan", cot: "ctg", arcsin: "asin", arccos: "acos", arctg: "atan", arctan: "atan", sh: "sinh", ch: "cosh", th: "tanh" };
const CONSTANTS = { pi: Math.PI, "π": Math.PI, e: Math.E };
export const FUNCTION_NAMES = [...Object.keys(FUNCTIONS), ...Object.keys(ALIASES)];

function tokenize(src) {
  const tokens = [];
  const re = /\s*(?:(\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?|[.,]\d+(?:[eE][+-]?\d+)?)|([A-Za-zА-Яа-яπ][A-Za-zА-Яа-я0-9π]*)|([-+*\/^()])|(\S))/y;
  let pos = 0;
  while (pos < src.length) {
    re.lastIndex = pos;
    const m = re.exec(src);
    if (!m) break;
    const start = m.index + m[0].length - (m[1] ?? m[2] ?? m[3] ?? m[4]).length;
    if (m[1] !== undefined) tokens.push({ kind: "num", text: m[1], value: Number(m[1].replace(",", ".")), pos: start });
    else if (m[2] !== undefined) tokens.push({ kind: "name", text: m[2], pos: start });
    else if (m[3] !== undefined) tokens.push({ kind: "op", text: m[3], pos: start });
    else throw new ExprError("bad-char", `символ «${m[4]}» не входит в формулу`, start);
    pos = m.index + m[0].length;
  }
  return tokens;
}

// The syntax tree of `src`; `variables` are the names it may use (a function or a constant name is never one).
// Throws ExprError { code, pos } with pos the index of the offending character.
export function parseExpression(src, variables = ["x", "t"]) {
  const tokens = tokenize(src);
  let i = 0;
  const peek = () => tokens[i];
  const isOp = (s) => tokens[i] && tokens[i].kind === "op" && tokens[i].text === s;
  const here = () => (tokens[i] ? tokens[i].pos : src.length);
  const show = (tk) => (tk ? `«${tk.text}»` : "конец формулы");

  function expression() {
    let node = term();
    while (isOp("+") || isOp("-")) {
      const op = tokens[i++].text;
      node = { type: "bin", op, a: node, b: term() };
    }
    return node;
  }
  function term() {
    let node = unary();
    while (isOp("*") || isOp("/")) {
      const op = tokens[i++].text;
      node = { type: "bin", op, a: node, b: unary() };
    }
    return node;
  }
  function unary() {
    if (isOp("-")) { i++; return { type: "neg", a: unary() }; }
    if (isOp("+")) { i++; return unary(); }
    return power();
  }
  function power() {
    const base = atom();
    if (isOp("^")) { i++; return { type: "bin", op: "^", a: base, b: unary() }; }
    return base;
  }
  function atom() {
    const tk = peek();
    if (!tk) throw new ExprError("unexpected-end", "формула оборвана: не хватает числа, переменной или скобки", src.length);
    if (tk.kind === "num") { i++; return { type: "num", value: tk.value }; }
    if (tk.kind === "name") {
      i++;
      const name = Object.hasOwn(ALIASES, tk.text) ? ALIASES[tk.text] : tk.text;
      if (Object.hasOwn(FUNCTIONS, name)) {
        if (!isOp("(")) throw new ExprError("function-brackets", `после «${tk.text}» нужна скобка, например ${tk.text}(x)`, here());
        i++;
        const arg = expression();
        if (!isOp(")")) throw new ExprError("unclosed", "скобка не закрыта", here());
        i++;
        return { type: "call", name, a: arg };
      }
      if (Object.hasOwn(CONSTANTS, tk.text)) return { type: "num", value: CONSTANTS[tk.text] };
      if (variables.includes(tk.text)) return { type: "var", name: tk.text };
      throw new ExprError("unknown-name", `неизвестное имя «${tk.text}»: допустимы ${variables.join(", ")}, pi, e и функции ${Object.keys(FUNCTIONS).join(", ")}`, tk.pos);
    }
    if (tk.text === "(") {
      i++;
      const inner = expression();
      if (!isOp(")")) throw new ExprError("unclosed", "скобка не закрыта", here());
      i++;
      return inner;
    }
    // a ")" with nothing open is surplus; inside brackets it stands where an operand should be: "()" or "2+)"
    const open = tokens.slice(0, i).filter((k) => k.text === "(").length - tokens.slice(0, i).filter((k) => k.text === ")").length;
    if (tk.text === ")" && open <= 0) throw new ExprError("unbalanced", "лишняя закрывающая скобка", tk.pos);
    throw new ExprError("unexpected", `здесь нужно число, переменная или скобка, а стоит ${show(tk)}`, tk.pos);
  }

  if (!tokens.length) throw new ExprError("empty", "формула пуста", 0);
  const tree = expression();
  if (i < tokens.length) {
    const tk = tokens[i], prev = tokens[i - 1];
    if (tk.kind === "op" && tk.text === ")") throw new ExprError("unbalanced", "лишняя закрывающая скобка", tk.pos);
    const operand = (k) => k.kind === "num" || k.kind === "name" || k.text === "(";
    if (operand(tk) && prev && (prev.kind === "num" || prev.kind === "name" || prev.text === ")")) {
      throw new ExprError("missing-operator", `между «${prev.text}» и «${tk.text}» пропущен знак, возможно * (умножение не подразумевается)`, tk.pos);
    }
    throw new ExprError("unexpected", `лишний фрагмент ${show(tk)}`, tk.pos);
  }
  return tree;
}

// The value of a formula without variables: the ends of an interval such as "-pi" or "pi/2".
export function evalConstant(src) {
  return compileExpression(src, [])();
}

const variablesOf = (node, found = new Set()) => {
  if (node.type === "var") found.add(node.name);
  if (node.a) variablesOf(node.a, found);
  if (node.b) variablesOf(node.b, found);
  return found;
};

// The single-letter variables the pages know: a formula that uses one that `names` lacks gets "bad-variable"
// with the allowed set in the message, not "unknown-name".
const COMMON_VARIABLES = ["x", "t", "s", "y"];

// A function of the variables named in `names` (in that order) from the text `src`; any other
// variable in the text is an ExprError "bad-variable". The tree is walked into closures, once.
export function compileExpression(src, names = ["x"]) {
  const tree = parseExpression(src, [...new Set([...COMMON_VARIABLES, ...names])]);
  for (const v of variablesOf(tree)) {
    if (!names.includes(v)) {
      const pos = Math.max(0, src.indexOf(v));
      const allowed = names.length ? `допустима только переменная ${names.join(", ")}` : "переменных быть не должно";
      throw new ExprError("bad-variable", `здесь ${allowed}, а в формуле есть ${v}`, pos);
    }
  }
  const build = (node) => {
    switch (node.type) {
      case "num": { const v = node.value; return () => v; }
      case "var": { const k = names.indexOf(node.name); return (...args) => args[k]; }
      case "neg": { const a = build(node.a); return (...args) => -a(...args); }
      case "call": { const a = build(node.a), fn = FUNCTIONS[node.name]; return (...args) => fn(a(...args)); }
      default: {
        const a = build(node.a), b = build(node.b);
        switch (node.op) {
          case "+": return (...args) => a(...args) + b(...args);
          case "-": return (...args) => a(...args) - b(...args);
          case "*": return (...args) => a(...args) * b(...args);
          case "/": return (...args) => a(...args) / b(...args);
          default: return (...args) => Math.pow(a(...args), b(...args));
        }
      }
    }
  };
  return build(tree);
}

// ---------------------------------------------------------------- quadrature

// Nodes and weights of the 15-point Kronrod rule and its embedded 7-point Gauss rule (QUADPACK):
// the half of the nodes on [0, 1], the last one is the centre.
const XGK = [0.991455371120812639206854697526329, 0.949107912342758524526189684047851, 0.864864423359769072789712788640926,
  0.741531185599394439863864773280788, 0.586087235467691130294144838258730, 0.405845151377397166906606412076961,
  0.207784955007898467600689403773245, 0];
const WGK = [0.022935322010529224963732008058970, 0.063092092629978553290700663189204, 0.104790010322250183839876322541518,
  0.140653259715525918745189590510238, 0.169004726639267902826583426598550, 0.190350578064785409913256402421014,
  0.204432940075298892414161999234649, 0.209482141084727828012999174891714];
const WG = [0.129484966168869693270611432679082, 0.279705391489276667901467771423780, 0.381830050505118944950369775488975,
  0.417959183673469387755102040816327];

export class EvalError extends Error {
  constructor(at) {
    super(`подынтегральная функция не определена или бесконечна в точке ${at}`);
    this.code = "non-finite";
    this.at = at;
  }
}

// One application of the rule on [lo, hi]: { value, err, resabs }.
// The error estimate is QUADPACK's: |K15 - G7|, sharpened by the roughness of the integrand.
function gk15(f, lo, hi) {
  const c = (lo + hi) / 2, h = (hi - lo) / 2;
  const at = (x) => { const v = f(x); if (!Number.isFinite(v)) throw new EvalError(x); return v; };
  const fc = at(c);
  let resk = WGK[7] * fc, resg = WG[3] * fc, resabs = Math.abs(resk);
  const fv1 = [], fv2 = [];
  for (let j = 0; j < 7; j++) {
    const d = h * XGK[j];
    const f1 = at(c - d), f2 = at(c + d);
    fv1.push(f1); fv2.push(f2);
    resk += WGK[j] * (f1 + f2);
    resabs += WGK[j] * (Math.abs(f1) + Math.abs(f2));
    if (j % 2 === 1) resg += WG[(j - 1) / 2] * (f1 + f2);
  }
  const reskh = resk / 2;
  let resasc = WGK[7] * Math.abs(fc - reskh);
  for (let j = 0; j < 7; j++) resasc += WGK[j] * (Math.abs(fv1[j] - reskh) + Math.abs(fv2[j] - reskh));
  let err = Math.abs((resk - resg) * h);
  resabs *= Math.abs(h); resasc *= Math.abs(h);
  if (resasc !== 0 && err !== 0) err = resasc * Math.min(1, (200 * err / resasc) ** 1.5);
  if (resabs > 2.2250738585072014e-308 / (50 * EPS)) err = Math.max(50 * EPS * resabs, err);
  return { value: resk * h, err, resabs };
}

// The integral of f over [a, b] by globally adaptive Gauss-Kronrod: the interval with the largest
// error estimate is bisected until the sum of the estimates is within tol * |I| (relative) or
// `maxIntervals` is reached. Endpoints are never evaluated, so integrable singularities there
// (ln x, 1/sqrt(x)) are fine. Returns { value, err, ok, intervals, scale }, scale being the integral
// of |f|, the size the rounding noise of the value is measured against; throws EvalError if f is
// not finite at a node. a > b gives the usual sign.
export function integrate(f, a, b, { tol = 1e-12, maxIntervals = 400 } = {}) {
  if (a === b) return { value: 0, err: 0, ok: true, intervals: 0, scale: 0 };
  if (a > b) { const r = integrate(f, b, a, { tol, maxIntervals }); return { ...r, value: -r.value }; }
  const parts = [{ lo: a, hi: b, ...gk15(f, a, b) }];
  const total = () => parts.reduce((s, p) => [s[0] + p.value, s[1] + p.err, s[2] + p.resabs], [0, 0, 0]);
  for (;;) {
    const [value, err, resabs] = total();
    // an integral that cancels to 0 cannot be had to a relative accuracy: the absolute floor is
    // tol/10 of the integral of |f|, which is above 50 eps |f|, the floor of every single estimate
    const ok = err <= Math.max(tol * Math.abs(value), 0.1 * tol * resabs);
    if (ok || parts.length >= maxIntervals) return { value, err, ok, intervals: parts.length, scale: resabs };
    let worst = 0;
    for (let i = 1; i < parts.length; i++) if (parts[i].err > parts[worst].err) worst = i;
    const { lo, hi } = parts[worst];
    const mid = (lo + hi) / 2;
    if (!(mid > lo && mid < hi)) return { value, err, ok, intervals: parts.length, scale: resabs };
    parts.splice(worst, 1, { lo, hi: mid, ...gk15(f, lo, mid) }, { lo: mid, hi, ...gk15(f, mid, hi) });
  }
}

// ---------------------------------------------------------------- dense linear algebra

// LU decomposition with partial pivoting of the n x n row-major matrix `m` (not modified):
// { lu, piv, sign, singular }. The matrix is declared singular only when a pivot is exactly zero.
export function luDecompose(m, n) {
  const lu = Float64Array.from(m), piv = Array.from({ length: n }, (_, i) => i);
  let sign = 1, singular = false;
  for (let k = 0; k < n; k++) {
    let p = k;
    for (let i = k + 1; i < n; i++) if (Math.abs(lu[i * n + k]) > Math.abs(lu[p * n + k])) p = i;
    if (lu[p * n + k] === 0) { singular = true; continue; }
    if (p !== k) {
      for (let j = 0; j < n; j++) { const t = lu[k * n + j]; lu[k * n + j] = lu[p * n + j]; lu[p * n + j] = t; }
      [piv[k], piv[p]] = [piv[p], piv[k]]; sign = -sign;
    }
    for (let i = k + 1; i < n; i++) {
      const l = lu[i * n + k] / lu[k * n + k];
      lu[i * n + k] = l;
      for (let j = k + 1; j < n; j++) lu[i * n + j] -= l * lu[k * n + j];
    }
  }
  return { lu, piv, sign, singular, n };
}

export function luDet({ lu, sign, n }) {
  let d = sign;
  for (let i = 0; i < n; i++) d *= lu[i * n + i];
  return d;
}

export function luSolve({ lu, piv, n }, rhs) {
  const x = Float64Array.from(piv, (p) => rhs[p]);
  for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) x[i] -= lu[i * n + j] * x[j];
  for (let i = n - 1; i >= 0; i--) {
    for (let j = i + 1; j < n; j++) x[i] -= lu[i * n + j] * x[j];
    x[i] /= lu[i * n + i];
  }
  return x;
}

export const det = (m, n) => luDet(luDecompose(m, n));

export function norm1(mat, n) {
  let best = 0;
  for (let j = 0; j < n; j++) { let s = 0; for (let i = 0; i < n; i++) s += Math.abs(mat[i * n + j]); best = Math.max(best, s); }
  return best;
}

// scale * ||M^-1||_1, Infinity for a singular matrix; `scale` is ||M||_1 unless given, which
// makes it the condition number in the 1-norm. A caller that knows M = I - lambda B passes
// 1 + |lambda| ||B||_1: for a 1 x 1 matrix the plain condition number is 1 whatever M is.
export function cond1(m, n, scale = norm1(m, n)) {
  const f = luDecompose(m, n);
  if (f.singular) return Infinity;
  const inv = new Float64Array(n * n);
  for (let j = 0; j < n; j++) {
    const e = new Float64Array(n); e[j] = 1;
    const col = luSolve(f, e);
    for (let i = 0; i < n; i++) inv[i * n + j] = col[i];
  }
  return scale * norm1(inv, n);
}

// ---------------------------------------------------------------- eigenvalues of a real matrix

// Eigenvalues of a real n x n matrix `A` (flat, row-major), as { re, im } sorted by re, then im, descending.
// Balancing, reduction to the Hessenberg form by elimination with pivoting, and the shifted QR iteration
// of Francis (EISPACK balanc, elmhes, hqr). Throws after 60 iterations without convergence of one root.
export function eigenvalues(A, n) {
  const a = Array.from({ length: n + 1 }, () => new Float64Array(n + 1));
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) a[i + 1][j + 1] = A[i * n + j];
  balance(a, n);
  hessenberg(a, n);
  return hqr(a, n).sort((p, q) => q.re - p.re || q.im - p.im);
}

// Similarity scaling by powers of 2: rows and columns of comparable norm, the eigenvalues unchanged.
function balance(a, n) {
  for (let done = false; !done;) {
    done = true;
    for (let i = 1; i <= n; i++) {
      let r = 0, c = 0;
      for (let j = 1; j <= n; j++) if (j !== i) { c += Math.abs(a[j][i]); r += Math.abs(a[i][j]); }
      if (c === 0 || r === 0) continue;
      let g = r / 2, f = 1;
      const s = c + r;
      while (c < g) { f *= 2; c *= 4; }
      g = r * 2;
      while (c > g) { f /= 2; c /= 4; }
      if ((c + r) / f < 0.95 * s) {
        done = false;
        for (let j = 1; j <= n; j++) a[i][j] /= f;
        for (let j = 1; j <= n; j++) a[j][i] *= f;
      }
    }
  }
}

// Gaussian elimination with pivoting to the upper Hessenberg form; the multipliers stored below the
// subdiagonal are cleared at the end.
function hessenberg(a, n) {
  for (let m = 2; m < n; m++) {
    let x = 0, i = m;
    for (let j = m; j <= n; j++) if (Math.abs(a[j][m - 1]) > Math.abs(x)) { x = a[j][m - 1]; i = j; }
    if (i !== m) {
      for (let j = m - 1; j <= n; j++) { const t = a[i][j]; a[i][j] = a[m][j]; a[m][j] = t; }
      for (let j = 1; j <= n; j++) { const t = a[j][i]; a[j][i] = a[j][m]; a[j][m] = t; }
    }
    if (x !== 0) {
      for (let r = m + 1; r <= n; r++) {
        let y = a[r][m - 1];
        if (y === 0) continue;
        y /= x; a[r][m - 1] = y;
        for (let j = m; j <= n; j++) a[r][j] -= y * a[m][j];
        for (let j = 1; j <= n; j++) a[j][m] += y * a[j][r];
      }
    }
  }
  for (let i = 3; i <= n; i++) for (let j = 1; j < i - 1; j++) a[i][j] = 0;
}

function hqr(a, n) {
  const out = [];
  let nn = n, t = 0, anorm = 0;
  for (let i = 1; i <= n; i++) for (let j = Math.max(i - 1, 1); j <= n; j++) anorm += Math.abs(a[i][j]);
  const sign = (v, s) => (s >= 0 ? Math.abs(v) : -Math.abs(v));
  while (nn >= 1) {
    let its = 0, l;
    do {
      for (l = nn; l >= 2; l--) {
        const s0 = Math.abs(a[l - 1][l - 1]) + Math.abs(a[l][l]);
        if (Math.abs(a[l][l - 1]) <= EPS * (s0 === 0 ? anorm : s0)) { a[l][l - 1] = 0; break; }
      }
      let x = a[nn][nn];
      if (l === nn) {
        out.push({ re: x + t, im: 0 });
        nn--;
      } else {
        let y = a[nn - 1][nn - 1], w = a[nn][nn - 1] * a[nn - 1][nn];
        if (l === nn - 1) {
          const p = 0.5 * (y - x), q = p * p + w, z = Math.sqrt(Math.abs(q));
          x += t;
          if (q >= 0) {
            const zz = p + sign(z, p);
            out.push({ re: x + zz, im: 0 }, { re: zz ? x - w / zz : x + zz, im: 0 });
          } else {
            out.push({ re: x + p, im: z }, { re: x + p, im: -z });
          }
          nn -= 2;
        } else {
          if (its === 60) throw new Error("the QR iteration did not converge");
          if (its === 10 || its === 20) {
            t += x;
            for (let i = 1; i <= nn; i++) a[i][i] -= x;
            const s = Math.abs(a[nn][nn - 1]) + Math.abs(a[nn - 1][nn - 2]);
            y = x = 0.75 * s;
            w = -0.4375 * s * s;
          }
          its++;
          let m, p, q, r, z;
          for (m = nn - 2; m >= l; m--) {
            z = a[m][m]; r = x - z;
            let s = y - z;
            p = (r * s - w) / a[m + 1][m] + a[m][m + 1];
            q = a[m + 1][m + 1] - z - r - s;
            r = a[m + 2][m + 1];
            s = Math.abs(p) + Math.abs(q) + Math.abs(r);
            p /= s; q /= s; r /= s;
            if (m === l) break;
            const u = Math.abs(a[m][m - 1]) * (Math.abs(q) + Math.abs(r));
            const v = Math.abs(p) * (Math.abs(a[m - 1][m - 1]) + Math.abs(z) + Math.abs(a[m + 1][m + 1]));
            if (u <= EPS * v) break;
          }
          for (let i = m + 2; i <= nn; i++) { a[i][i - 2] = 0; if (i !== m + 2) a[i][i - 3] = 0; }
          for (let k = m; k <= nn - 1; k++) {
            if (k !== m) {
              p = a[k][k - 1]; q = a[k + 1][k - 1]; r = k !== nn - 1 ? a[k + 2][k - 1] : 0;
              x = Math.abs(p) + Math.abs(q) + Math.abs(r);
              if (x !== 0) { p /= x; q /= x; r /= x; }
            }
            const s = sign(Math.sqrt(p * p + q * q + r * r), p);
            if (s === 0) continue;
            if (k === m) { if (l !== m) a[k][k - 1] = -a[k][k - 1]; } else a[k][k - 1] = -s * x;
            p += s; x = p / s; y = q / s; z = r / s; q /= p; r /= p;
            for (let j = k; j <= nn; j++) {
              p = a[k][j] + q * a[k + 1][j];
              if (k !== nn - 1) { p += r * a[k + 2][j]; a[k + 2][j] -= p * z; }
              a[k + 1][j] -= p * y; a[k][j] -= p * x;
            }
            const mmin = nn < k + 3 ? nn : k + 3;
            for (let i = l; i <= mmin; i++) {
              p = x * a[i][k] + y * a[i][k + 1];
              if (k !== nn - 1) { p += z * a[i][k + 2]; a[i][k + 2] -= p * r; }
              a[i][k + 1] -= p * q; a[i][k] -= p;
            }
          }
        }
      }
    } while (l < nn - 1);
  }
  return out;
}

// The coefficients of Delta(lambda) = det(I - lambda A) = 1 + d_1 lambda + ... + d_n lambda^n, [1, d_1, ..., d_n],
// by the Faddeev - LeVerrier recurrence: M_1 = I, c_{n-k} = -tr(A M_k) / k, M_{k+1} = A M_k + c_{n-k} I,
// where det(mu I - A) = sum_j c_j mu^j; then d_m = c_{n-m}. Exact up to rounding for the small n of a kernel.
export function deltaCoefficients(A, n) {
  const c = new Float64Array(n + 1);
  c[n] = 1;
  let M = new Float64Array(n * n);
  for (let i = 0; i < n; i++) M[i * n + i] = 1;
  for (let k = 1; k <= n; k++) {
    const AM = new Float64Array(n * n);
    for (let i = 0; i < n; i++) for (let l = 0; l < n; l++) { const v = A[i * n + l]; if (v !== 0) for (let j = 0; j < n; j++) AM[i * n + j] += v * M[l * n + j]; }
    let tr = 0;
    for (let i = 0; i < n; i++) tr += AM[i * n + i];
    c[n - k] = -tr / k;
    M = AM;
    for (let i = 0; i < n; i++) M[i * n + i] += c[n - k];
  }
  return Float64Array.from({ length: n + 1 }, (_, m) => c[n - m]);
}

// ---------------------------------------------------------------- text of a degenerate-kernel problem

// The kernel of an integral equation as a sum K(x,t) = sum_k alpha_k(x) beta_k(t) on [lo, hi], with a
// right-hand side f(x). Compiles the text of a problem: { lo, hi, rows: [{ alpha, beta }], f } with the
// formulas as strings. Returns { lo, hi, n, alpha: [fn(x)], beta: [fn(t)], f: fn(x) }. A bad formula throws
// ExprError with `.field` set to "alpha", "beta" or "f" and `.row` to the zero-based row.
export function compileProblem({ lo, hi, rows, f }) {
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) throw new ExprError("bad-interval", "концы отрезка должны быть конечными числами", 0);
  if (!(lo < hi)) throw new ExprError("bad-interval", "нужно a < b", 0);
  if (!rows.length) throw new ExprError("no-terms", "в ядре нет ни одного слагаемого", 0);
  const tag = (fn, field, row) => { try { return fn(); } catch (e) { if (e instanceof ExprError) { e.field = field; e.row = row; } throw e; } };
  return {
    lo, hi, n: rows.length,
    alpha: rows.map((r, k) => tag(() => compileExpression(r.alpha, ["x"]), "alpha", k)),
    beta: rows.map((r, k) => tag(() => compileExpression(r.beta, ["t"]), "beta", k)),
    f: tag(() => compileExpression(f, ["x"]), "f", -1),
  };
}
