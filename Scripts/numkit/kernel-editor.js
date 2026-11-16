// The editor of a degenerate kernel K(x,t) = sum_k alpha_k(x) beta_k(t) with the interval [a, b], the
// report of a bad formula and a line chart. Browser code: an ES module that a course build inlines
// with `import` and `export` removed (see README.md); numkit.js is inlined before it.
// The numbers and the formula logic are in numkit.js. The page supplies three globals this file only calls:
//   $(id)     document.getElementById
//   esc(s)    HTML escaping of a string
//   css(name) the colour of a theme role such as "--text-2" as "#rrggbb" (sandbox_kit's theme.js)
// The fields and the layout classes are styled by kernel-editor.css; the look of an input is the page's.
import { EvalError, ExprError, compileProblem, evalConstant } from "./numkit.js";
import { formatNumber } from "../sandbox_kit/number.js";

export const fmt = (x) => formatNumber(x, 4);
// A small number kept visible: 1,2e-15 where formatNumber would round it to 0.
export const sci = (x) => (x === 0 ? "0" : Math.abs(x) >= 1e-3 && Math.abs(x) < 1e6 ? fmt(x) : x.toExponential(1).replace(".", ",").replace("-", "−"));
// A number as the notes write it: plain from 10^-3 up to 10^4 (four digits), else m·10^k with two digits of m and the
// exponent as a power of ten. `sciText` is for canvas text and textContent (unicode superscripts), `sciHtml` for innerHTML.
function sciSplit(x) {
  if (x === 0) return { plain: "0" };
  if (!Number.isFinite(x)) return { plain: Number.isNaN(x) ? "—" : x < 0 ? "−∞" : "∞" };
  const a = Math.abs(x);
  if (a >= 1e-3 && a < 1e4) return { plain: fmt(x) };
  const [m, e] = a.toExponential(1).split("e");
  return { sign: x < 0 ? "−" : "", mant: m.replace(/\.0$/, "").replace(".", ","), exp: Number(e) };
}
export const sciText = (x) => { const s = sciSplit(x); return s.plain ?? `${s.sign}${s.mant}·${pow10(s.exp)}`; };
export const sciHtml = (x) => { const s = sciSplit(x); return s.plain ?? `${s.sign}${s.mant}·10<sup>${s.exp < 0 ? "−" : ""}${Math.abs(s.exp)}</sup>`; };
// A sum of terms c_k * text_k with the signs of the coefficients inside the sum: "x − 1,5·sin(x) + 2·cos(x)".
export const sumOfTerms = (head, cs, texts) => cs.reduce((s, c, k) => `${s} ${c < 0 ? "−" : "+"} ${fmt(Math.abs(c))}·(${esc(texts[k])})`, head);
const SUB = "₀₁₂₃₄₅₆₇₈₉";
export const sub = (k) => String(k).split("").map((c) => SUB[+c]).join("");

// The fields of the kernel editor: the interval a, b, and the terms alpha_k(x) * beta_k(t).
// `host` is an empty element; `onChange` is called after every edit. Returns the editor.
export function kernelEditor(host, onChange) {
  host.innerHTML = `
    <div class="ivl"><label>a<input id="lo" value="0" inputmode="decimal"></label><label>b<input id="hi" value="1" inputmode="decimal"></label></div>
    <div id="krows" class="krows"></div>
    <button id="kadd" type="button">Добавить слагаемое</button>`;
  const rows = $("krows");
  const addRow = (a = "", b = "") => {
    const k = rows.children.length + 1;
    const row = document.createElement("div");
    row.className = "krow";
    row.innerHTML = `<span class="kn">${k}</span><input class="ka" inputmode="text" aria-label="α${sub(k)}(x)" placeholder="α(x)" value="${esc(a)}"><span class="kd">·</span><input class="kb" aria-label="β${sub(k)}(t)" placeholder="β(t)" value="${esc(b)}"><button type="button" class="kx" aria-label="Удалить слагаемое ${k}">×</button>`;
    rows.appendChild(row);
    renumber();
  };
  const renumber = () => {
    Array.from(rows.children).forEach((row, i) => {
      const k = i + 1;
      row.querySelector(".kn").textContent = k;
      row.querySelector(".ka").id = `ka${k}`; row.querySelector(".kb").id = `kb${k}`;
      row.querySelector(".ka").setAttribute("aria-label", `α${sub(k)}(x)`); row.querySelector(".kb").setAttribute("aria-label", `β${sub(k)}(t)`);
      row.querySelector(".kx").disabled = rows.children.length === 1;
    });
  };
  rows.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".kx");
    if (!btn || rows.children.length === 1) return;
    btn.closest(".krow").remove(); renumber(); onChange();
  });
  host.addEventListener("input", onChange);
  $("kadd").addEventListener("click", () => { addRow(); onChange(); });
  return {
    setProblem(p) {
      $("lo").value = p.lo; $("hi").value = p.hi;
      rows.innerHTML = "";
      p.rows.forEach(([a, b]) => addRow(a, b));
    },
    rowsText: () => Array.from(rows.children).map((r) => ({ alpha: r.querySelector(".ka").value, beta: r.querySelector(".kb").value })),
    mark(field, row) {
      host.querySelectorAll("input").forEach((el) => el.removeAttribute("aria-invalid"));
      const el = field === "alpha" ? $(`ka${row + 1}`) : field === "beta" ? $(`kb${row + 1}`) : field === "interval" ? null : null;
      if (el) el.setAttribute("aria-invalid", "true");
    },
  };
}

// An evaluated constant such as "pi/2" from an input; a message for the person on failure.
function constant(id, what) {
  const el = $(id);
  try { return evalConstant(el.value); } catch (e) { e.field = "const"; e.place = what; e.input = id; throw e; }
}

// Reads the interval, the kernel (from `editor`) and the right-hand side text into a compiled problem.
// A bad input throws an Error whose `message` already names the place; `.input` is the offending id.
export function readKernelProblem(editor, fId) {
  const lo = constant("lo", "Отрезок, a"), hi = constant("hi", "Отрезок, b");
  const rows = editor.rowsText();
  try {
    return compileProblem({ lo, hi, rows, f: fId ? $(fId).value : "0" });
  } catch (e) {
    if (!(e instanceof ExprError)) throw e;
    e.place = e.field === "alpha" ? `Ядро, строка ${e.row + 1}, α${sub(e.row + 1)}(x)` : e.field === "beta" ? `Ядро, строка ${e.row + 1}, β${sub(e.row + 1)}(t)`
      : e.field === "f" ? "Правая часть f(x)" : e.code === "no-terms" ? "Ядро" : "Отрезок";
    e.input = e.field === "alpha" ? `ka${e.row + 1}` : e.field === "beta" ? `kb${e.row + 1}` : e.field === "f" ? fId : e.code === "bad-interval" ? "lo" : null;
    throw e;
  }
}

// The text shown under the form for an error of reading, parsing or integrating.
export function describe(e) {
  if (e instanceof ExprError) return `${e.place || "Формула"}${e.code === "empty" || e.code === "no-terms" || e.code === "bad-interval" ? "" : `, символ ${e.pos + 1}`}: ${e.message}`;
  if (e instanceof EvalError) return `Интеграл не вычислен: ${e.message}. Проверь, что формулы определены на всём отрезке [a; b]`;
  return String(e && e.message ? e.message : e);
}

export function showError(host, editor, e) {
  host.textContent = describe(e);
  if (editor) { editor.mark(null, 0); if (e && e.input) { const el = $(e.input); if (el) el.setAttribute("aria-invalid", "true"); } }
}

export function clearError(host, editor) { host.textContent = ""; if (editor) editor.mark(null, 0); }

// ---------------------------------------------------------------- line chart

// "Nice" tick positions on [lo, hi]: about `count` of them with steps 1, 2 or 5 times a power of ten.
export function ticks(lo, hi, count = 5) {
  const span = hi - lo;
  if (!(span > 0)) return [lo];
  const raw = span / count, pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * pow).find((s) => s >= raw);
  const out = [];
  for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9 * step; v += step) out.push(Math.abs(v) < 1e-12 * step ? 0 : v);
  return out;
}

// Whole exponents k with 10^k inside [lo, hi], thinned to an even step so that about `count` remain.
export function decadeTicks(lo, hi, count = 6) {
  const k0 = Math.ceil(Math.log10(lo) - 1e-9), k1 = Math.floor(Math.log10(hi) + 1e-9);
  if (!(k0 <= k1)) return [];
  const step = Math.max(1, Math.ceil((k1 - k0 + 1) / count));
  const out = [];
  for (let k = Math.ceil(k0 / step) * step; k <= k1; k += step) out.push(k);
  return out;
}

const SUPER = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
// 10^k as a tick label: "10⁻³", and "1" and "10" for the first two powers.
export const pow10 = (k) => (k === 0 ? "1" : k === 1 ? "10" : "10" + String(k).split("").map((c) => SUPER[c]).join(""));

// A range of whole decades around the positive finite values of the arrays (and of `include`); zeros, NaN
// and negatives are skipped. Without a positive value: [0,1; 1].
export function logRange(arrays, include = []) {
  let lo = Infinity, hi = 0;
  for (const a of [...arrays, include]) for (const v of a) if (v > 0 && Number.isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  if (!Number.isFinite(lo)) return [1e-1, 1];
  const k0 = Math.floor(Math.log10(lo) + 1e-9);
  const k1 = Math.max(Math.ceil(Math.log10(hi) - 1e-9), k0 + 1);
  return [Number(`1e${k0}`), Number(`1e${k1}`)];
}

// Draws lines on a canvas. spec: { series: [{ xs, ys, color, width, dash, dots }], xlim: [lo, hi], ylim: [lo, hi],
// points: [{ x, y, color, filled }], vlines: [{ x, color, dash }], aspect, xlog, ylog }. A NaN in ys breaks the line.
// `dots` is the radius of a dot at every vertex of a series. `aspect` is height / width (0,5 if absent).
// A log axis takes its limits as values (both positive) and puts a tick at whole powers of ten.
export function plotLines(cv, spec) {
  const cssW = Math.max(240, cv.getBoundingClientRect().width || 600), cssH = Math.round(cssW * (spec.aspect || 0.5));
  const dpr = window.devicePixelRatio || 1;
  cv.width = Math.round(cssW * dpr); cv.height = Math.round(cssH * dpr);
  const g = cv.getContext("2d");
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, cssW, cssH);
  const text = css("--text-2"), grid = css("--grid");
  const L = 68, R = 12, T = 10, B = 24;
  const [x0, x1] = spec.xlim, [y0, y1] = spec.ylim;
  const tx = spec.xlog ? Math.log10 : (v) => v, ty = spec.ylog ? Math.log10 : (v) => v;
  const X = (v) => L + (tx(v) - tx(x0)) / (tx(x1) - tx(x0) || 1) * (cssW - L - R);
  const Y = (v) => T + (ty(y1) - ty(v)) / (ty(y1) - ty(y0) || 1) * (cssH - T - B);
  // a tick is { v, label }: whole powers of ten on a log axis, "nice" numbers on a linear one
  const axisTicks = (lo, hi, log, label) => (log ? decadeTicks(lo, hi).map((k) => ({ v: Number(`1e${k}`), label: pow10(k) })) : ticks(lo, hi).map((v) => ({ v, label: label(v) })));
  g.font = "500 11px " + getComputedStyle(document.body).fontFamily;
  g.lineWidth = 1;
  g.textBaseline = "middle"; g.textAlign = "right";
  for (const { v, label } of axisTicks(y0, y1, spec.ylog, sci)) {
    g.strokeStyle = v === 0 ? text : grid;
    g.beginPath(); g.moveTo(L, Y(v)); g.lineTo(cssW - R, Y(v)); g.stroke();
    g.fillStyle = text; g.fillText(label, L - 6, Y(v));
  }
  g.textAlign = "center"; g.textBaseline = "top";
  for (const { v, label } of axisTicks(x0, x1, spec.xlog, fmt)) {
    g.strokeStyle = v === 0 ? text : grid;
    g.beginPath(); g.moveTo(X(v), T); g.lineTo(X(v), cssH - B); g.stroke();
    g.fillStyle = text; g.fillText(label, X(v), cssH - B + 5);
  }
  g.save();
  g.beginPath(); g.rect(L, T, cssW - L - R, cssH - T - B); g.clip();
  for (const v of spec.vlines || []) {
    g.strokeStyle = v.color; g.setLineDash(v.dash || [4, 3]); g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(X(v.x), T); g.lineTo(X(v.x), cssH - B); g.stroke(); g.setLineDash([]);
  }
  for (const s of spec.series) {
    g.strokeStyle = s.color; g.lineWidth = s.width || 2; g.setLineDash(s.dash || []);
    g.beginPath();
    let pen = false;
    const drawable = (x, y) => Number.isFinite(y) && Number.isFinite(x) && (!spec.ylog || y > 0) && (!spec.xlog || x > 0);
    s.xs.forEach((x, i) => {
      const y = s.ys[i];
      if (!drawable(x, y)) { pen = false; return; }
      pen ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y)); pen = true;
    });
    g.stroke(); g.setLineDash([]);
    if (s.dots) {
      g.fillStyle = s.color;
      s.xs.forEach((x, i) => {
        if (!drawable(x, s.ys[i])) return;
        g.beginPath(); g.arc(X(x), Y(s.ys[i]), s.dots, 0, 2 * Math.PI); g.fill();
      });
    }
  }
  g.restore();
  for (const p of spec.points || []) {
    g.strokeStyle = p.color; g.lineWidth = 2; g.fillStyle = p.filled ? p.color : css("--surface");
    g.beginPath(); g.arc(X(p.x), Y(p.y), 4.5, 0, 2 * Math.PI); g.fill(); g.stroke();
  }
}

// A y-range that holds the data with a margin, never degenerate.
export function yRange(arrays, include = []) {
  let lo = Infinity, hi = -Infinity;
  for (const a of arrays) for (const v of a) if (Number.isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  for (const v of include) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  if (!Number.isFinite(lo)) return [-1, 1];
  if (hi - lo <= 1e-9 * Math.max(Math.abs(hi), Math.abs(lo))) { const m = Math.max(Math.abs(hi), 1) * 0.5; return [lo - m, hi + m]; }
  const pad = (hi - lo) * 0.08;
  return [lo - pad, hi + pad];
}
