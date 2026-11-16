// The numbers of a page as Russian writes them: the decimal comma and the minus sign −.
// One ES module with no DOM. theme_js() inlines it with `export` removed into every page, so
// toComma and formatNumber are globals there; a module of a course imports it, and the build
// drops the import. check_page.py names every visible number that still has a dot. The name is
// not num, as in the figures, because pages already declare a num of their own.

const russian = (s) => s.replace(".", ",").replace(/^-/, "−").replace(/e-/, "e−");

// x with `digits` decimals, as toFixed gives it; digits = null gives the shortest form.
export function toComma(x, digits = 2) {
  if (Number.isNaN(x)) return "NaN";
  if (!Number.isFinite(x)) return x > 0 ? "∞" : "−∞";
  const s = digits === null ? String(x) : x.toFixed(digits);
  // -0.001 rounded to 0,00 is zero and shows no minus
  return russian(/^-0[.0]*$/.test(s) ? s.slice(1) : s);
}

// x in a short readable form: `digits` significant digits, a power of ten when it is tiny or huge.
export function formatNumber(x, digits = 4) {
  if (!Number.isFinite(x)) return String(x);
  if (Math.abs(x) < 1e-12) return "0";
  const s = Math.abs(x) < 1e-3 || Math.abs(x) >= 1e6 ? x.toExponential(digits - 1) : String(+x.toPrecision(digits));
  return s.replace(".", ",").replace("-", "−");
}
