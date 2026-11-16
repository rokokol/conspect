// Assertions for numeric tests, shared by numkit.test.mjs and the tests of a course.
// Every helper compares element by element and stops at the first miss: a deepEqual on a large
// array of floats eats gigabytes of memory in `node --test`.
import assert from "node:assert/strict";

// |got - want| <= tol, absolute.
export const near = (got, want, tol, what) => assert.ok(Math.abs(got - want) <= tol, `${what}: ${got} vs ${want}, tol ${tol}`);

// The same for two arrays of equal length.
export const nearAll = (got, want, tol, what) => {
  assert.equal(got.length, want.length, `${what}: length`);
  for (let i = 0; i < want.length; i++) near(got[i], want[i], tol, `${what}[${i}]`);
};

// |got - want| <= tol * max(1, |want|): absolute near zero, relative elsewhere.
export const rel = (got, want, tol, what) => assert.ok(Math.abs(got - want) <= tol * Math.max(1, Math.abs(want)), `${what}: ${got} vs ${want}, tol ${tol}`);

export const dot = (u, v) => u.reduce((s, x, i) => s + x * v[i], 0);

// The product of an m x n row-major matrix and a vector.
export const mulVec = (a, m, n, x) => Array.from({ length: m }, (_, i) => { let s = 0; for (let j = 0; j < n; j++) s += a[i * n + j] * x[j]; return s; });

// Every computed complex value matched to a distinct reference value, the distance bounded by `tol`.
// `got` is a list of { re, im }, `want` a list of { re, im } or [re, im].
export const matchAll = (got, want, tol, what) => {
  assert.equal(got.length, want.length, `${what}: number of values`);
  const free = want.map((w) => ({ re: w.re ?? w[0], im: w.im ?? w[1] }));
  for (const g of got) {
    let best = -1, dist = Infinity;
    free.forEach((w, i) => { const d = Math.hypot(g.re - w.re, g.im - w.im); if (d < dist) { dist = d; best = i; } });
    assert.ok(dist <= tol, `${what}: ${g.re}${g.im < 0 ? "-" : "+"}${Math.abs(g.im)}i has no partner within ${tol}, nearest ${dist}`);
    free.splice(best, 1);
  }
};
