// Shared helpers of the waveguide page: element lookup, Russian number format, and a small canvas plot.
// Colours are never literals: css(x) from sandbox_kit's theme.js resolves a role ("--text") or any CSS
// colour expression to "#rrggbb" in the scheme the page is in at this moment, so the page does not parse
// a colour. Every drawing asks again; a change of theme redraws the page.
const $ = (id) => document.getElementById(id);
// the roles of the plots, each a mix of the ink with the page ground, so that they follow the theme
const mixInk = (pct) => `color-mix(in srgb, var(--text) ${pct}%, var(--surface))`;
const GRID = mixInk(14);   // grid lines: quiet
const FRAME = mixInk(40);  // the frame of a plot and the zero line
const HELP = mixInk(55);   // helper lines: asymptotes, the diagonal
const LABEL = mixInk(85);  // tick labels and notes on a plot
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

// a number with a decimal comma and a true minus
const fmt = (x, d = 4) => (Number.isFinite(x) ? x.toFixed(d).replace(".", ",").replace("-", "−") : "—");
// significant digits, in the exponent form when the value is very small or large
const SUP = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻" };
const fmtG = (x, d = 4) => {
  if (!Number.isFinite(x)) return "—";
  if (x === 0) return "0";
  const a = Math.abs(x);
  if (a >= 1e-3 && a < 1e5) return x.toPrecision(d).replace(".", ",").replace("-", "−");
  const [mant, exp] = x.toExponential(d - 1).split("e");
  return `${mant.replace(".", ",").replace("-", "−")}·10${String(parseInt(exp, 10)).split("").map((c) => SUP[c]).join("")}`;
};
const fmtC = (z, d = 4) => `${fmt(z[0], d)} ${z[1] < 0 ? "−" : "+"} ${fmt(Math.abs(z[1]), d)} i`;
const parseNum = (s) => Number(String(s).trim().replace(",", ".").replace("−", "-"));

// one nice tick step: 1, 2 or 5 times a power of ten
function niceTicks(lo, hi, n = 6) {
  const raw = (hi - lo) / n;
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  const f = raw / p;
  const step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * p;
  const out = [];
  for (let t = Math.ceil(lo / step - 1e-9) * step; t <= hi + 1e-9; t += step) out.push(+t.toFixed(12));
  return out;
}

// [r, g, b] of a colour string, read back from one pixel of a canvas: the engine converts any CSS colour
function rgbOf(color) {
  const cv = document.createElement("canvas");
  cv.width = 1; cv.height = 1;
  const c = cv.getContext("2d", { willReadFrequently: true });
  c.fillStyle = color;
  c.fillRect(0, 0, 1, 1);
  return Array.from(c.getImageData(0, 0, 1, 1).data.slice(0, 3));
}

class Plot {
  // ratio is the height over the width of the canvas; xr and yr the data ranges
  constructor(canvas, ratio, xr, yr, pad = { l: 48, r: 14, t: 12, b: 34 }) {
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(260, canvas.getBoundingClientRect().width || 640);
    const h = Math.round(w * ratio);
    canvas.style.height = `${h}px`;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    this.ctx = canvas.getContext("2d");
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.w = w; this.h = h; this.pad = pad; this.xr = xr; this.yr = yr;
    this.font = getComputedStyle(document.body).fontFamily;
    this.ctx.clearRect(0, 0, w, h);
  }
  X(x) { return this.pad.l + (x - this.xr[0]) / (this.xr[1] - this.xr[0]) * (this.w - this.pad.l - this.pad.r); }
  Y(y) { return this.h - this.pad.b - (y - this.yr[0]) / (this.yr[1] - this.yr[0]) * (this.h - this.pad.t - this.pad.b); }
  invX(px) { return this.xr[0] + (px - this.pad.l) / (this.w - this.pad.l - this.pad.r) * (this.xr[1] - this.xr[0]); }
  text(str, x, y, o = {}) {
    const c = this.ctx;
    c.font = `${o.size || 12}px ${this.font}`;
    c.fillStyle = o.color || css(LABEL);
    c.textAlign = o.align || "left";
    c.textBaseline = o.base || "alphabetic";
    c.fillText(str, x, y);
  }
  frame(xlabel, ylabel, o = {}) {
    const c = this.ctx;
    const { l, r, t, b } = this.pad;
    const grid = css(GRID);
    const xt = o.xticks || niceTicks(this.xr[0], this.xr[1], Math.max(3, Math.round(this.w / 90)));
    const yt = o.yticks || niceTicks(this.yr[0], this.yr[1], 6);
    c.lineWidth = 1;
    c.strokeStyle = grid;
    c.beginPath();
    for (const x of xt) { c.moveTo(Math.round(this.X(x)) + 0.5, t); c.lineTo(Math.round(this.X(x)) + 0.5, this.h - b); }
    for (const y of yt) { c.moveTo(l, Math.round(this.Y(y)) + 0.5); c.lineTo(this.w - r, Math.round(this.Y(y)) + 0.5); }
    c.stroke();
    c.strokeStyle = css(FRAME);
    c.strokeRect(l + 0.5, t + 0.5, this.w - l - r, this.h - t - b);
    for (const x of xt) this.text(fmtTick(x), this.X(x), this.h - b + 15, { align: "center" });
    for (const y of yt) this.text(fmtTick(y), l - 6, this.Y(y), { align: "right", base: "middle" });
    if (xlabel) this.text(xlabel, this.w - r, this.h - 4, { align: "right", color: css("--text") });
    if (ylabel) this.text(ylabel, l + 4, t + 12, { color: css("--text") });
  }
  clipStart() {
    const c = this.ctx;
    c.save();
    c.beginPath();
    c.rect(this.pad.l, this.pad.t, this.w - this.pad.l - this.pad.r, this.h - this.pad.t - this.pad.b);
    c.clip();
  }
  clipEnd() { this.ctx.restore(); }
  line(xs, ys, o = {}) {
    const c = this.ctx;
    c.beginPath();
    let pen = false;
    for (let i = 0; i < xs.length; i++) {
      if (!Number.isFinite(ys[i])) { pen = false; continue; }
      if (pen) c.lineTo(this.X(xs[i]), this.Y(ys[i])); else c.moveTo(this.X(xs[i]), this.Y(ys[i]));
      pen = true;
    }
    c.strokeStyle = o.color || css("--text");
    c.lineWidth = o.width || 2;
    c.setLineDash(o.dash || []);
    c.lineJoin = "round";
    c.stroke();
    c.setLineDash([]);
  }
  vline(x, o = {}) { this.line([x, x], [this.yr[0], this.yr[1]], { color: o.color || css("--mark"), width: o.width || 1, dash: o.dash || [5, 4] }); }
  hline(y, o = {}) { this.line([this.xr[0], this.xr[1]], [y, y], { color: o.color || css("--mark"), width: o.width || 1, dash: o.dash || [] }); }
  dot(x, y, o = {}) {
    const c = this.ctx;
    c.beginPath();
    c.arc(this.X(x), this.Y(y), o.r || 4, 0, 2 * Math.PI);
    if (o.fill !== false) { c.fillStyle = o.color || css("--text"); c.fill(); }
    c.lineWidth = 2;
    c.strokeStyle = o.color || css("--text");
    if (o.fill === false) { c.fillStyle = css("--surface"); c.fill(); }
    c.stroke();
  }
  rect(x0, x1, y0, y1, color) {
    const c = this.ctx;
    c.fillStyle = color;
    c.fillRect(this.X(x0), this.Y(y1), this.X(x1) - this.X(x0), this.Y(y0) - this.Y(y1));
  }
}

const fmtTick = (v) => String(+(Math.abs(v) < 1e-9 ? 0 : v).toPrecision(6)).replace(".", ",").replace("-", "−");

// a pending redraw after the layout settles or the theme changes
function onRedraw(fn) {
  let queued = false;
  const run = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; fn(); }); };
  window.addEventListener("resize", run);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", run);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(run);
  return run;
}
