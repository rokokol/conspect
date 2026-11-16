// Shared page helpers: element lookup, a plot frame with data to pixel mapping, and
// redraw on theme change. The theme colour lookup css(name) comes from sandbox_kit's theme.js.
const $ = (id) => document.getElementById(id);
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
// Canvas text uses the prose face of the page at the prose weight; size in px.
const font = (px) => `500 ${px}px ${getComputedStyle(document.body).fontFamily}`;

// Canvas text with indices and powers. Unicode sub- and superscripts differ by
// two pixels at small sizes, so x₂ reads as x²; here they are set smaller and
// shifted clearly down or up. Uses the current font size, textAlign and
// textBaseline of ctx, so it is a drop-in for fillText.
const SUB_CHARS = { "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9", "ₖ": "k", "ₗ": "l", "ₜ": "t", "ₘ": "m" };
const SUP_CHARS = { "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "−", "ᴹ": "M" };
function mathText(ctx, s, x, y) {
  const size = +(/(\d+(?:\.\d+)?)px/.exec(ctx.font) || [0, 12])[1];
  const family = ctx.font.replace(/^.*?px\s*/, "");
  const weight = (/^(\d{3})\s/.exec(ctx.font) || [0, 400])[1];
  const parts = [...String(s)].map((c) => {
    if (c in SUB_CHARS) return { t: SUB_CHARS[c], px: Math.round(size * 0.7), dy: Math.round(size * 0.3) };
    if (c in SUP_CHARS) return { t: SUP_CHARS[c], px: Math.round(size * 0.7), dy: -Math.round(size * 0.45) };
    return { t: c, px: size, dy: 0 };
  });
  const width = parts.reduce((w, p) => { ctx.font = `${weight} ${p.px}px ${family}`; return w + ctx.measureText(p.t).width; }, 0);
  const align = ctx.textAlign, base = ctx.textBaseline;
  let cx = align === "center" ? x - width / 2 : align === "right" || align === "end" ? x - width : x;
  const by = y + { top: 0.8, hanging: 0.8, middle: 0.35, bottom: -0.2, ideographic: -0.2 }[base] * size || y;
  ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
  for (const p of parts) {
    ctx.font = `${weight} ${p.px}px ${family}`;
    ctx.fillText(p.t, cx, (base === "alphabetic" ? y : by) + p.dy);
    cx += ctx.measureText(p.t).width;
  }
  ctx.font = `${weight} ${size}px ${family}`; ctx.textAlign = align; ctx.textBaseline = base;
}

// A plot area inside a canvas with margins for axes; equal=true keeps one
// scale on both axes, so circles and angles in the data stay true.
function frame(cv, xlim, ylim, { margin = [44, 28, 14, 42], equal = false } = {}) {
  const [ml, mt, mr, mb] = margin;
  const W = cv.width - ml - mr;
  const H = cv.height - mt - mb;
  let [x0, x1] = xlim;
  let [y0, y1] = ylim;
  if (equal) {
    const s = Math.max((x1 - x0) / W, (y1 - y0) / H);
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    [x0, x1] = [cx - (s * W) / 2, cx + (s * W) / 2];
    [y0, y1] = [cy - (s * H) / 2, cy + (s * H) / 2];
  }
  return {
    ml, mt, W, H, x0, x1, y0, y1,
    px: (x) => ml + ((x - x0) / (x1 - x0)) * W,
    py: (y) => mt + H - ((y - y0) / (y1 - y0)) * H,
    dx: (p) => x0 + ((p - ml) / W) * (x1 - x0),
    dy: (p) => y0 + ((mt + H - p) / H) * (y1 - y0),
  };
}

function axes(ctx, f, { xticks = [], yticks = [], xlabel = "", ylabel = "", fmt = String, xfmt = fmt, yfmt = fmt } = {}) {
  ctx.save();
  ctx.strokeStyle = css("--grid");
  ctx.lineWidth = 1;
  ctx.fillStyle = css("--text-2");
  ctx.font = font(12);
  for (const t of yticks) {
    const y = f.py(t);
    ctx.beginPath(); ctx.moveTo(f.ml, y); ctx.lineTo(f.ml + f.W, y); ctx.stroke();
    ctx.textAlign = "right"; ctx.textBaseline = "middle"; mathText(ctx, yfmt(t), f.ml - 6, y);
  }
  for (const t of xticks) {
    const x = f.px(t);
    ctx.textAlign = "center"; ctx.textBaseline = "top"; mathText(ctx, xfmt(t), x, f.mt + f.H + 6);
  }
  ctx.strokeStyle = css("--text-2");
  ctx.strokeRect(f.ml, f.mt, f.W, f.H);
  // Axis titles stay outside the data area: x under the tick labels at the
  // right end (needs a bottom margin of about 42), y above the plot at the
  // left edge (needs a top margin of about 28).
  if (xlabel) { ctx.textAlign = "right"; ctx.textBaseline = "top"; mathText(ctx, xlabel, f.ml + f.W, f.mt + f.H + 22); }
  if (ylabel) { ctx.textAlign = "left"; ctx.textBaseline = "bottom"; mathText(ctx, ylabel, f.ml, f.mt - 6); }
  ctx.restore();
}

// Labels at the right end of curves, so a curve is told apart by its name and
// its dash, not by hue alone. items: [{text, y, look: {col, w, dash}, strong}],
// y the pixel height where the curve ends. The labels stack upward from the
// bottom in the order of the curve ends (ties keep the given order), each
// joined to its curve by a thin leader and shown with a sample of its line.
// Needs a right margin of about 136.
function endLabels(ctx, f, items) {
  const lxr = f.ml + f.W;
  let prev = Infinity;
  ctx.save();
  ctx.font = font(12); ctx.textBaseline = "middle"; ctx.textAlign = "left";
  [...items].sort((a, b) => b.y - a.y).forEach((it) => {
    const ly = Math.min(it.y, prev - 16, f.mt + f.H + 4);
    ctx.strokeStyle = css("--grid"); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(lxr, it.y); ctx.lineTo(lxr + 10, ly); ctx.stroke();
    polyline(ctx, [[lxr + 12, ly], [lxr + 30, ly]], css(it.look.col), it.look.w, it.look.dash);
    // A label that runs past the canvas edge is a page bug: say so loudly (check_page.py fails on it).
    if (ctx.measureText(it.text).width > ctx.canvas.width - (lxr + 35) - 2) console.error(`endLabels: "${it.text}" does not fit the right margin`);
    ctx.fillStyle = css(it.strong ? "--text" : "--text-2"); mathText(ctx, it.text, lxr + 35, ly);
    prev = ly;
  });
  ctx.restore();
}

function dot(ctx, x, y, color, { hollow = false, r = 4.5 } = {}) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, 2 * Math.PI);
  ctx.fillStyle = hollow ? css("--surface") : color;
  ctx.strokeStyle = hollow ? color : css("--surface");
  ctx.lineWidth = hollow ? 2 : 1.5;
  ctx.fill();
  ctx.stroke();
}

function polyline(ctx, pts, color, width = 2, dash = []) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.setLineDash(dash);
  ctx.beginPath();
  pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
  ctx.stroke();
  ctx.restore();
}

// Same scheme as the static figures: binary uses the blue/red poles,
// multiclass the categorical blue/orange/aqua.
function classColors(nC) {
  return nC === 2 ? [hex(css("--c0")), hex(css("--c1"))]
    : [hex(css("--c0")), hex(css("--c1m")), hex(css("--c2"))];
}

// Square view of a 2D data set with a margin, one scale on both axes.
function dataView(cv, d, pad = 0.5) {
  const all = [...d.Xtr, ...d.Xte];
  const lo = [0, 1].map((j) => Math.min(...all.map((p) => p[j])) - pad);
  const hi = [0, 1].map((j) => Math.max(...all.map((p) => p[j])) + pad);
  const span = Math.max(hi[0] - lo[0], hi[1] - lo[1]);
  for (const j of [0, 1]) {
    const c = (lo[j] + hi[j]) / 2;
    lo[j] = c - span / 2;
    hi[j] = c + span / 2;
  }
  const W = cv.width;
  return {
    lo, hi, W,
    toPx: (p) => [((p[0] - lo[0]) / (hi[0] - lo[0])) * W, W - ((p[1] - lo[1]) / (hi[1] - lo[1])) * W],
    toX: (px, py) => [lo[0] + (px / W) * (hi[0] - lo[0]), lo[1] + ((W - py) / W) * (hi[1] - lo[1])],
    scale: W / (hi[0] - lo[0]),
  };
}

// Decision regions of a classifier: proba(x) returns class probabilities.
// Tint grows with confidence above chance; the boundary is where the
// predicted label changes. Then train points filled, test points hollow.
// outline: false skips the grid-stepped boundary, for a page that draws an
// exactly known one (a line) itself. proba may return null for a point that
// has no class: it is painted grey.
function drawClassifier(ctx, v, d, proba, classes, { showTest = true, N = 96, outline = true } = {}) {
  const nC = classes.length, cols = classColors(nC), mid = hex(css("--mid"));
  const cell = v.W / N, lab = [];
  for (let i = 0; i < N; i++) {
    lab.push([]);
    for (let j = 0; j < N; j++) {
      const p = proba(v.toX((j + 0.5) * cell, (i + 0.5) * cell));
      if (p === null) {
        // Undecided point (no class, or a tie): neutral grey, no class label.
        lab[i].push(-1);
        const g = hex(css("--text-2"));
        ctx.fillStyle = `rgb(${g.map((x, q) => Math.round(mid[q] + (x - mid[q]) * 0.35))})`;
        ctx.fillRect(j * cell, i * cell, cell + 1, cell + 1);
        continue;
      }
      const c = p.indexOf(Math.max(...p));
      lab[i].push(c);
      const conf = (p[c] - 1 / nC) / (1 - 1 / nC);
      const a = 0.18 + 0.32 * conf;
      ctx.fillStyle = `rgb(${cols[c].map((x, q) => Math.round(mid[q] + (x - mid[q]) * a))})`;
      ctx.fillRect(j * cell, i * cell, cell + 1, cell + 1);
    }
  }
  if (outline) {
    ctx.strokeStyle = css("--text");
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      if (j + 1 < N && lab[i][j] !== lab[i][j + 1]) { ctx.moveTo((j + 1) * cell, i * cell); ctx.lineTo((j + 1) * cell, (i + 1) * cell); }
      if (i + 1 < N && lab[i][j] !== lab[i + 1][j]) { ctx.moveTo(j * cell, (i + 1) * cell); ctx.lineTo((j + 1) * cell, (i + 1) * cell); }
    }
    ctx.stroke();
  }
  const pt = (p, y, hollow) => { const [x, yy] = v.toPx(p); dot(ctx, x, yy, `rgb(${cols[classes.indexOf(y)]})`, { hollow }); };
  d.Xtr.forEach((p, i) => pt(p, d.ytr[i], false));
  if (showTest) d.Xte.forEach((p, i) => pt(p, d.yte[i], true));
}

// Background of a loss surface: level bands over the plot area of frame f.
// Band edges are quantiles of the loss over the view, so every function gets
// the same number of visible levels; fn(p) is the loss at the data point p.
function levelBands(ctx, f, fn, { N = 160, bands = 14 } = {}) {
  const cw = f.W / N, ch = f.H / N, vals = [];
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) vals.push(fn([f.dx(f.ml + (j + 0.5) * cw), f.dy(f.mt + (i + 0.5) * ch)]));
  const sorted = [...vals].sort((a, b) => a - b);
  const edges = Array.from({ length: bands - 1 }, (_, b) => sorted[Math.floor(((b + 1) * sorted.length) / bands)]);
  const light = hex(css("--surface")), dark = hex(css("--c0"));
  vals.forEach((v, k) => {
    const t = edges.filter((e) => v > e).length / (bands - 1);
    const rgb = light.map((l, q) => Math.round(l + (dark[q] - l) * t * 0.75));
    ctx.fillStyle = `rgb(${rgb})`;
    ctx.fillRect(f.ml + (k % N) * cw, f.mt + Math.floor(k / N) * ch, cw + 1, ch + 1);
  });
}

// Pointer position in canvas pixels, whatever the CSS size of the canvas is.
function canvasXY(cv, e) {
  const r = cv.getBoundingClientRect();
  return [((e.clientX - r.left) / r.width) * cv.width, ((e.clientY - r.top) / r.height) * cv.height];
}

// The point the user clicked: a dot in the mark colour with a halo in the surface colour.
function probeMark(ctx, px, py) {
  ctx.save();
  ctx.strokeStyle = css("--surface"); ctx.lineWidth = 3;
  ctx.fillStyle = css("--mark");
  ctx.beginPath(); ctx.arc(px, py, 6, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
  ctx.restore();
}

// Subscript digit for class names C₀, C₁, C₂.
const SUB = ["₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉"];
const sub = (k) => String(k).split("").map((c) => SUB[+c]).join("");

function argmaxClass(proba, classes) {
  return (x) => { const p = proba(x); return classes[p.indexOf(Math.max(...p))]; };
}

// Short number for labels: exponent form for huge or tiny magnitudes.
function num(v, digits = 3) {
  const a = Math.abs(v);
  if (v === 0) return "0";
  if (a >= 1e4 || a < 1e-3) return v.toExponential(1).replace("e+", "e").replace(".", ",").replace(/-/g, "−");
  return toComma(+v.toPrecision(digits), null);
}

// Ticks of a log axis whose limits are exponents lo..hi: whole powers of ten,
// at most five of them, counted down from the largest one inside the axis.
function logTicks(lo, hi) {
  const step = Math.max(1, Math.ceil((Math.floor(hi) - lo) / 4));
  const ticks = [];
  for (let q = Math.floor(hi); q >= lo; q -= step) ticks.push(q);
  return ticks;
}

// X-axis ticks for a count 1..n: the first and every step-th value.
function countTicks(n) {
  const step = n > 40 ? 25 : n > 15 ? 10 : 5;
  const t = [1];
  for (let k = step; k <= n; k += step) t.push(k);
  return t;
}

const SUP = { 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
const power = (k) => (k === 1 ? "x" : "x" + String(k).split("").map((c) => SUP[c]).join(""));

// Redraw on a theme switch, and once the embedded fonts finish loading: a
// canvas painted before that keeps the fallback font.
function onTheme(draw) {
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
  document.fonts.ready.then(draw);
}
