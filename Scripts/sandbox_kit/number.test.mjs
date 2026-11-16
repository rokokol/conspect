// number.js: the numbers of a page as Russian writes them. Run: node --test number.test.mjs
import assert from "node:assert/strict";
import test from "node:test";
import { formatNumber, toComma } from "./number.js";

test("toComma gives fixed decimals with the decimal comma and the minus sign", () => {
  assert.equal(toComma(0.5), "0,50");
  assert.equal(toComma(3.14159, 3), "3,142");
  assert.equal(toComma(-2.75, 1), "−2,8");
  assert.equal(toComma(12, 0), "12");
});

test("toComma with no digits writes the shortest form", () => {
  assert.equal(toComma(0.125, null), "0,125");
  assert.equal(toComma(2, null), "2");
  assert.equal(toComma(-0.5, null), "−0,5");
});

test("toComma keeps a negative zero from showing a minus", () => {
  assert.equal(toComma(-0.001, 2), "0,00");
});

test("toComma leaves what is not a finite number readable", () => {
  assert.equal(toComma(NaN), "NaN");
  assert.equal(toComma(Infinity), "∞");
  assert.equal(toComma(-Infinity), "−∞");
});

test("formatNumber uses the decimal comma and the minus sign, zero stays zero", () => {
  assert.equal(formatNumber(1.5), "1,5");
  assert.equal(formatNumber(-2), "−2");
  assert.equal(formatNumber(1e-15), "0");
  assert.equal(formatNumber(123456789), "1,235e+8");
});
