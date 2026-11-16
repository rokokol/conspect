// JS core against sklearn answers in fixtures.json. Run: node --test
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as ml from "./mlcore.js";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url)));
const { X, y } = fx.datasets.moons;
const G = fx.grid;

const maxAbs = (a, b) => Math.max(...a.map((v, i) => Math.abs(v - b[i])));
const agree = (a, b) => a.filter((v, i) => v === b[i]).length / a.length;

test("kNN probabilities equal sklearn for every k", () => {
  for (const { k, proba1 } of fx.knn) {
    const m = ml.fitKnn(X, y, { k });
    const p = G.map((g) => ml.knnProba(m, g)[1]);
    assert.ok(maxAbs(p, proba1) < 1e-12, `k=${k}`);
  }
});

test("tree predictions agree with sklearn at every depth", () => {
  for (const { depth, pred, train_acc } of fx.tree) {
    const t = ml.fitTree(X, y, { maxDepth: depth });
    const p = G.map((g) => ml.treePredict(t, g));
    assert.ok(agree(p, pred) >= 0.98, `depth=${depth} agreement ${agree(p, pred)}`);
    const acc = ml.accuracy(X.map((x) => ml.treePredict(t, x)), y);
    assert.ok(Math.abs(acc - train_acc) < 1e-9, `depth=${depth} train acc ${acc} vs ${train_acc}`);
  }
});

test("a deeper tree never fits the training set worse", () => {
  let prev = 0;
  for (const depth of [1, 2, 4, 8, 16]) {
    const t = ml.fitTree(X, y, { maxDepth: depth });
    const acc = ml.accuracy(X.map((x) => ml.treePredict(t, x)), y);
    assert.ok(acc >= prev - 1e-12);
    prev = acc;
  }
  assert.equal(prev, 1);
});

test("polynomial features follow sklearn's column order", () => {
  const { x, deg, features } = fx.poly;
  assert.ok(maxAbs(ml.polyFeatures(x, deg), features) < 1e-12);
});

test("polynomial feature names match sklearn get_feature_names_out", () => {
  const { deg, names } = fx.poly;
  assert.deepEqual(ml.polyNames(["x1", "x2"], deg, { style: "sklearn" }), names);
});

test("logistic regression matches sklearn for each degree and C", () => {
  for (const { deg, C, proba1 } of fx.logreg) {
    const m = ml.fitLogreg(X, y, { degree: deg, C });
    const p = G.map((g) => ml.logregProba(m, g));
    assert.ok(maxAbs(p, proba1) < 1e-4, `deg=${deg} C=${C} diff ${maxAbs(p, proba1)}`);
  }
});

test("powers-only logistic regression matches sklearn on the single-exponent columns", () => {
  for (const { data, deg, C, grid, names, at, features, proba1 } of fx.logreg_pure) {
    // Column order matters for the weight bars: features and names must line up.
    assert.ok(maxAbs(ml.polyFeatures(at, deg, { pure: true }), features) < 1e-12, `order deg=${deg}`);
    const d = fx.datasets[data];
    const m = ml.fitLogreg(d.X, d.y, { degree: deg, C, pure: true });
    const p = grid.map((g) => ml.logregProba(m, g));
    assert.ok(maxAbs(p, proba1) < 1e-4, `${data} deg=${deg} C=${C} diff ${maxAbs(p, proba1)}`);
    assert.deepEqual(ml.polyNames(["x1", "x2"], deg, { style: "sklearn", pure: true }), names);
  }
});

test("powers only make the logit additive, f(x1) + g(x2); all monomials do not", () => {
  // The XOR argument: an additive logit has equal sums over the two diagonals
  // of any rectangle, so it cannot be positive on one and negative on the other.
  const d = fx.datasets.xor;
  const [a, a2, b, b2] = [0.8, -0.6, 0.7, -0.9];
  const diag = (m) => ml.logregDecision(m, [a, b]) + ml.logregDecision(m, [a2, b2])
    - ml.logregDecision(m, [a, b2]) - ml.logregDecision(m, [a2, b]);
  assert.ok(Math.abs(diag(ml.fitLogreg(d.X, d.y, { degree: 5, C: 100, pure: true }))) < 1e-9);
  assert.ok(Math.abs(diag(ml.fitLogreg(d.X, d.y, { degree: 5, C: 100 }))) > 1);
});

test("ROC curve and AUC equal sklearn", () => {
  const { scores, y: yy, auc, fpr, tpr } = fx.roc;
  const r = ml.rocCurve(scores, yy);
  assert.ok(Math.abs(ml.auc(r) - auc) < 1e-12);
  assert.ok(maxAbs(r.fpr, fpr) < 1e-12 && maxAbs(r.tpr, tpr) < 1e-12);
});

test("AUC with tied scores equals sklearn", () => {
  const { scores, y: yy, auc } = fx.roc_ties;
  assert.ok(Math.abs(ml.auc(ml.rocCurve(scores, yy)) - auc) < 1e-12);
});

test("precision and recall at a threshold equal sklearn", () => {
  const { scores, y: yy, at } = fx.roc;
  for (const { t, precision, recall } of at) {
    const c = ml.confusion(scores, yy, t);
    assert.ok(Math.abs(c.precision - precision) < 1e-12, `t=${t}`);
    assert.ok(Math.abs(c.recall - recall) < 1e-12, `t=${t}`);
  }
});

test("polynomial OLS, Ridge and Lasso match sklearn", () => {
  const { x, y: yr, grid, fits } = fx.reg1d;
  for (const { kind, deg, alpha, pred, coef } of fits) {
    const m = ml.fitLinear(x.map((v) => [v]), yr, { degree: deg, penalty: kind, alpha });
    const p = grid.map((g) => ml.linearPredict(m, [g]));
    // OLS at degree 9 is ill-conditioned: compare predictions, not raw weights.
    const tol = kind === "ols" && deg === 9 ? 1e-5 : 1e-6;
    assert.ok(maxAbs(p, pred) < tol, `${kind} deg=${deg} a=${alpha} pred ${maxAbs(p, pred)}`);
    if (kind !== "ols") assert.ok(maxAbs(m.w, coef) < 1e-5, `${kind} a=${alpha} coef ${maxAbs(m.w, coef)}`);
  }
});

test("exact lasso path equals sklearn lars_path at every probe alpha", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  for (const { deg, probes, w } of fx.lassopath) {
    const path = ml.lassoPath(X, yr, { degree: deg });
    probes.forEach((a, k) => {
      const m = ml.lassoAt(path, a);
      assert.ok(maxAbs(m.w, w[k]) < 1e-6, `deg=${deg} alpha=${a} ${maxAbs(m.w, w[k])}`);
    });
  }
});

test("lasso path agrees with converged coordinate descent where that converges", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  const path = ml.lassoPath(X, yr, { degree: 9 });
  for (const a of [0.01, 0.05]) {
    const cd = ml.fitLinear(X, yr, { degree: 9, penalty: "lasso", alpha: a });
    assert.ok(maxAbs(ml.lassoAt(path, a).w, cd.w) < 1e-6, `alpha=${a}`);
  }
});

test("lasso zeroes weights that ridge keeps", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  const lasso = ml.fitLinear(X, yr, { degree: 9, penalty: "lasso", alpha: 0.05 });
  const ridge = ml.fitLinear(X, yr, { degree: 9, penalty: "ridge", alpha: 1 });
  assert.ok(lasso.w.filter((v) => v === 0).length >= 3);
  assert.equal(ridge.w.filter((v) => v === 0).length, 0);
});

test("penalised quadratic satisfies its optimality conditions", () => {
  // f(w) = (w - c)^T A (w - c) + lam * penalty(w); gradient of the smooth part 2A(w - c).
  const A = [[2, 0.9], [0.9, 1]];
  const c = [1.5, 1.2];
  const g = (w) => [0, 1].map((i) => 2 * (A[i][0] * (w[0] - c[0]) + A[i][1] * (w[1] - c[1])));
  for (const lam of [0.1, 1, 3]) {
    const r = ml.penalized2d(A, c, lam, "l2");
    const gr = g(r);
    // ridge: 2A(w - c) + 2 lam w = 0
    assert.ok(Math.abs(gr[0] + 2 * lam * r[0]) < 1e-9 && Math.abs(gr[1] + 2 * lam * r[1]) < 1e-9);
    const l = ml.penalized2d(A, c, lam, "l1");
    const gl = g(l);
    // lasso: grad + lam * sign(w) = 0 where w != 0, |grad| <= lam where w = 0
    for (let i = 0; i < 2; i++) {
      if (l[i] !== 0) assert.ok(Math.abs(gl[i] + lam * Math.sign(l[i])) < 1e-9, `lam=${lam} i=${i}`);
      else assert.ok(Math.abs(gl[i]) <= lam + 1e-9, `lam=${lam} i=${i} zero`);
    }
  }
  // Large lam drives lasso exactly to the origin, ridge only close to it.
  assert.deepEqual(ml.penalized2d(A, c, 50, "l1"), [0, 0]);
  assert.ok(ml.penalized2d(A, c, 50, "l2").every((v) => v !== 0));
});

test("regression tree equals sklearn DecisionTreeRegressor", () => {
  const { x, y: yr, grid } = fx.reg1d;
  for (const { depth, pred } of fx.regtree) {
    const t = ml.fitRegTree(x.map((v) => [v]), yr, { maxDepth: depth });
    const p = grid.map((g) => ml.regTreePredict(t, [g]));
    assert.ok(maxAbs(p, pred) < 1e-9, `depth=${depth} ${maxAbs(p, pred)}`);
  }
});

test("gradient boosting equals sklearn GradientBoostingRegressor, stage by stage", () => {
  const { x, y: yr, grid } = fx.reg1d;
  const X = x.map((v) => [v]);
  for (const { n, lr, depth, pred, staged_train_mse } of fx.gbr) {
    const m = ml.fitBoosting(X, yr, { nEstimators: n, lr, maxDepth: depth });
    const p = grid.map((g) => ml.boostingPredict(m, [g]));
    assert.ok(maxAbs(p, pred) < 1e-9, `n=${n} lr=${lr} d=${depth} ${maxAbs(p, pred)}`);
    const staged = Array.from({ length: n }, (_, k) =>
      X.reduce((s, xi, i) => s + (ml.boostingPredict(m, xi, k + 1) - yr[i]) ** 2, 0) / X.length);
    assert.ok(maxAbs(staged, staged_train_mse) < 1e-9, `staged n=${n}`);
  }
});

test("gradient boosting under squared, absolute and Huber loss equals sklearn, stage by stage, leaf refit included", () => {
  const { x, grid } = fx.reg1d;
  const X = x.map((v) => [v]);
  for (const c of fx.gbr_loss) {
    const tag = `${c.loss} alpha=${c.alpha} n=${c.n} lr=${c.lr} d=${c.depth} outliers=${c.outliers}`;
    const m = ml.fitBoosting(X, c.y, { nEstimators: c.n, lr: c.lr, maxDepth: c.depth, loss: c.loss, alpha: c.alpha });
    assert.ok(Math.abs(m.f0 - c.init) < 1e-12, `init ${tag}`);
    const p = grid.map((g) => ml.boostingPredict(m, [g]));
    assert.ok(maxAbs(p, c.pred) < 1e-9, `${tag} ${maxAbs(p, c.pred)}`);
    const stage = (k) => X.map((xi) => ml.boostingPredict(m, xi, k + 1));
    const mae = Array.from({ length: c.n }, (_, k) => stage(k).reduce((s, v, i) => s + Math.abs(v - c.y[i]), 0) / X.length);
    const mse = Array.from({ length: c.n }, (_, k) => stage(k).reduce((s, v, i) => s + (v - c.y[i]) ** 2, 0) / X.length);
    assert.ok(maxAbs(mae, c.staged_train_mae) < 1e-9, `staged MAE ${tag}`);
    assert.ok(maxAbs(mse, c.staged_train_mse) < 1e-9, `staged MSE ${tag}`);
  }
});

test("under absolute loss every leaf holds the minimiser of the summed absolute residual, which the mean is not", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  const m = ml.fitBoosting(X, yr, { nEstimators: 1, lr: 1, maxDepth: 2, loss: "absolute_error" });
  const res = yr.map((v) => v - m.f0);
  const leaves = new Map();
  X.forEach((xi, i) => {
    const leaf = ml.regTreeLeaf(m.trees[0], xi);
    leaves.set(leaf, [...(leaves.get(leaf) ?? []), res[i]]);
  });
  let someMeanDiffers = false;
  for (const [leaf, r] of leaves) {
    const sae = (c) => r.reduce((s, v) => s + Math.abs(v - c), 0);
    for (const dc of [-0.05, -0.001, 0.001, 0.05]) assert.ok(sae(leaf.value + dc) >= sae(leaf.value) - 1e-12);
    const mean = r.reduce((s, v) => s + v, 0) / r.length;
    if (Math.abs(mean - leaf.value) > 1e-9) someMeanDiffers = true;
  }
  assert.ok(someMeanDiffers);
});

test("on this sample moving an outlier further away changes squared-loss boosting but not absolute-loss boosting", () => {
  const { x, y: yr, grid } = fx.reg1d;
  const X = x.map((v) => [v]);
  const withOutlier = (h) => yr.map((v, i) => (i === 10 ? h : v));
  const fit = (loss, h) => {
    const m = ml.fitBoosting(X, withOutlier(h), { nEstimators: 30, lr: 0.3, maxDepth: 2, loss });
    return grid.map((g) => ml.boostingPredict(m, [g]));
  };
  assert.ok(maxAbs(fit("squared_error", 4), fit("squared_error", 40)) > 0.5);
  assert.ok(maxAbs(fit("absolute_error", 4), fit("absolute_error", 40)) < 1e-12);
});

test("the Huber antigradient and delta do not depend on how far an outlier beyond delta lies", () => {
  const near = [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -5];
  const far = near.slice(0, 9).concat(-500);
  assert.equal(ml.huberDelta(near, 0.9), ml.huberDelta(far, 0.9));
  assert.deepEqual(ml.antigradient("huber", near, 0.9), ml.antigradient("huber", far, 0.9));
  assert.notDeepEqual(ml.antigradient("squared_error", near), ml.antigradient("squared_error", far));
});

test("a leaf holding a single point takes that point's whole residual under absolute and Huber loss, as sklearn does", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  for (const loss of ["absolute_error", "huber"]) {
    const m = ml.fitBoosting(X, yr, { nEstimators: 1, lr: 1, maxDepth: 6, loss });
    const count = new Map();
    X.forEach((xi) => { const l = ml.regTreeLeaf(m.trees[0], xi); count.set(l, (count.get(l) ?? 0) + 1); });
    const lone = X.map((xi, i) => [xi, i]).filter(([xi]) => count.get(ml.regTreeLeaf(m.trees[0], xi)) === 1);
    assert.ok(lone.length > 0, loss);
    for (const [xi, i] of lone) assert.ok(Math.abs(ml.regTreePredict(m.trees[0], xi) - (yr[i] - m.f0)) < 1e-12, loss);
  }
});

test("Huber delta is the alpha-quantile of the absolute residuals, and the antigradient is the residual clipped at it", () => {
  const r = [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -5];
  assert.equal(ml.huberDelta(r, 0.9), 0.9);
  assert.equal(ml.huberDelta(r, 0.5), 0.5);
  assert.deepEqual(ml.antigradient("huber", r, 0.5).map((v) => +v.toFixed(12)), [0.1, -0.2, 0.3, -0.4, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5]);
  assert.deepEqual(ml.antigradient("absolute_error", [0.2, -3, 0], 0.9), [1, -1, 0]);
  assert.deepEqual(ml.antigradient("squared_error", r, 0.9), r);
});

test("staged predictions equal boostingPredict at every number of trees, for every loss", () => {
  const { x, y: yr } = fx.reg1d;
  const X = x.map((v) => [v]);
  for (const loss of ml.BOOSTING_LOSSES) {
    const m = ml.fitBoosting(X, yr, { nEstimators: 12, lr: 0.3, maxDepth: 2, loss });
    const st = ml.boostingStaged(m, X);
    assert.equal(st.length, 13);
    st.forEach((row, k) => assert.ok(maxAbs(row, X.map((xi) => ml.boostingPredict(m, xi, k))) < 1e-12, `${loss} k=${k}`));
  }
});

test("a tree fitted with integer sample weights equals the tree on the rows repeated that many times", () => {
  const w = X.map((_, i) => 1 + (i % 3));
  const rep = X.flatMap((x, i) => Array(w[i]).fill(x));
  const yrep = y.flatMap((v, i) => Array(w[i]).fill(v));
  for (const depth of [1, 2, 4]) {
    const a = ml.fitTree(X, y, { maxDepth: depth, weights: w });
    const b = ml.fitTree(rep, yrep, { maxDepth: depth });
    assert.deepEqual(G.map((g) => ml.treePredict(a, g)), G.map((g) => ml.treePredict(b, g)), `depth=${depth}`);
    assert.deepEqual(a.counts, b.counts);
  }
});

test("equal sample weights change nothing in the tree", () => {
  const a = ml.fitTree(X, y, { maxDepth: 3 });
  const b = ml.fitTree(X, y, { maxDepth: 3, weights: X.map(() => 0.01) });
  assert.deepEqual(G.map((g) => ml.treePredict(a, g)), G.map((g) => ml.treePredict(b, g)));
});

// sklearn's SAMME weight is alpha = ln((1 - eps) / eps) = 2 rho for two classes.
// Its binary decision_function is 2 sum(alpha_t h_t) / sum(alpha) = 4 F / sum(alpha).
test("AdaBoost over stumps equals sklearn AdaBoostClassifier: errors, weights, votes, predictions", () => {
  for (const c of fx.ada.filter((a) => a.n_fitted > 1)) {
    const m = ml.fitAdaBoost(c.X, c.y, { nEstimators: 60 });
    assert.equal(m.trees.length, c.n_fitted, c.ds);
    assert.ok(maxAbs(m.eps, c.eps) < 1e-9, `${c.ds} eps ${maxAbs(m.eps, c.eps)}`);
    assert.ok(maxAbs(m.rho.map((r) => 2 * r), c.alpha) < 1e-9, `${c.ds} alpha`);
    const vote = c.grid.map((g) => 4 * ml.adaScore(m, g));
    const ref = c.decision.map((d) => d * c.alpha_sum);
    assert.ok(maxAbs(vote, ref) < 1e-9, `${c.ds} vote ${maxAbs(vote, ref)}`);
    assert.deepEqual(c.grid.map((g) => (ml.adaScore(m, g) > 0 ? 1 : 0)), c.pred, c.ds);
    c.staged_train_pred.forEach((p, k) =>
      assert.deepEqual(c.X.map((x) => (ml.adaScore(m, x, k + 1) > 0 ? 1 : 0)), p, `${c.ds} stage ${k + 1}`));
  }
});

test("AdaBoost stops at a perfect stump like sklearn: one stump, weight 1 in sklearn's scale", () => {
  const c = fx.ada.find((a) => a.ds === "stump");
  const m = ml.fitAdaBoost(c.X, c.y, { nEstimators: 60 });
  assert.equal(m.trees.length, c.n_fitted);
  assert.equal(m.eps[0], 0);
  assert.equal(2 * m.rho[0], c.alpha[0]);
  assert.equal(m.stop, "perfect");
  assert.deepEqual(c.grid.map((g) => (ml.adaScore(m, g) > 0 ? 1 : 0)), c.pred);
});

test("AdaBoost weights are the normalised e^-M of the ensemble so far, and the new stump then errs on exactly half", () => {
  const c = fx.ada.find((a) => a.ds === "moons");
  const m = ml.fitAdaBoost(c.X, c.y, { nEstimators: 20 });
  const sgn = c.y.map((v) => 2 * v - 1);
  for (let t = 0; t < m.trees.length; t++) {
    const e = c.X.map((x, i) => Math.exp(-sgn[i] * ml.adaScore(m, x, t)));
    const z = e.reduce((s, v) => s + v, 0);
    assert.ok(maxAbs(m.weights[t], e.map((v) => v / z)) < 1e-12, `weights before stump ${t + 1}`);
    // the weights after the update are the weights before the next stump
    const after = c.X.map((x, i) => Math.exp(-sgn[i] * ml.adaScore(m, x, t + 1)));
    const za = after.reduce((s, v) => s + v, 0);
    const wrong = c.X.reduce((s, x, i) => s + (ml.adaStumpVote(m, t, x) !== sgn[i] ? after[i] / za : 0), 0);
    assert.ok(Math.abs(wrong - 0.5) < 1e-12, `stump ${t + 1}: ${wrong}`);
  }
});

test("each AdaBoost stump multiplies the mean exponential loss by 2 sqrt(eps (1 - eps)) < 1", () => {
  for (const name of ["moons", "circles"]) {
    const c = fx.ada.find((a) => a.ds === name);
    const m = ml.fitAdaBoost(c.X, c.y, { nEstimators: 15 });
    const sgn = c.y.map((v) => 2 * v - 1);
    const loss = (T) => c.X.reduce((s, x, i) => s + Math.exp(-sgn[i] * ml.adaScore(m, x, T)), 0) / c.X.length;
    assert.ok(Math.abs(loss(0) - 1) < 1e-12);
    for (let t = 0; t < m.trees.length; t++) {
      const factor = 2 * Math.sqrt(m.eps[t] * (1 - m.eps[t]));
      assert.ok(factor < 1);
      assert.ok(Math.abs(loss(t + 1) / loss(t) - factor) < 1e-12, `${name} stump ${t + 1}`);
    }
    // e^-M lies above the step, so the training error never exceeds the loss
    const err = c.X.filter((x, i) => sgn[i] * ml.adaScore(m, x) <= 0).length / c.X.length;
    assert.ok(err <= loss(m.trees.length));
  }
});

test("a stump that is no better than chance ends AdaBoost without being added", () => {
  // Four corners of a square in XOR order: every stump errs on exactly half. sklearn raises ValueError here.
  const m = ml.fitAdaBoost([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 0], { nEstimators: 10 });
  assert.equal(m.stop, "chance");
  assert.equal(m.trees.length, 0);
});

test("every kept stump beats chance, and the ensemble stops only for a named reason or at the limit", () => {
  for (const c of fx.ada) {
    const m = ml.fitAdaBoost(c.X, c.y, { nEstimators: 25 });
    assert.ok(m.eps.every((e, t) => e < 0.5 && (e > 0 || t === m.trees.length - 1)), c.ds);
    assert.ok(m.stop !== null || m.trees.length === 25, c.ds);
  }
});

test("gradient descent on a quadratic follows x <- (I - lr A) x exactly", () => {
  const A = [[3, 1], [1, 1]];
  const grad = (p) => [A[0][0] * p[0] + A[0][1] * p[1], A[1][0] * p[0] + A[1][1] * p[1]];
  const path = ml.gdPath(grad, [2, -1], { lr: 0.1, steps: 5 });
  assert.equal(path.length, 6);
  let p = [2, -1];
  for (let k = 1; k <= 5; k++) {
    const g = grad(p);
    p = [p[0] - 0.1 * g[0], p[1] - 0.1 * g[1]];
    assert.ok(maxAbs(path[k], p) < 1e-15);
  }
});

test("momentum keeps velocity; nesterov looks ahead", () => {
  const grad = (p) => [2 * p[0], 20 * p[1]];
  const m = ml.gdPath(grad, [1, 1], { lr: 0.01, steps: 3, momentum: 0.9 });
  // v1 = -lr g(x0); x1 = x0 + v1; v2 = 0.9 v1 - lr g(x1); x2 = x1 + v2
  const g0 = grad([1, 1]);
  const v1 = g0.map((g) => -0.01 * g);
  const x1 = [1 + v1[0], 1 + v1[1]];
  const v2 = grad(x1).map((g, i) => 0.9 * v1[i] - 0.01 * g);
  assert.ok(maxAbs(m[2], [x1[0] + v2[0], x1[1] + v2[1]]) < 1e-15);
  const n = ml.gdPath(grad, [1, 1], { lr: 0.01, steps: 3, momentum: 0.9, nesterov: true });
  const look = [x1[0] + 0.9 * v1[0], x1[1] + 0.9 * v1[1]];
  const w2 = grad(look).map((g, i) => 0.9 * v1[i] - 0.01 * g);
  assert.ok(maxAbs(n[2], [x1[0] + w2[0], x1[1] + w2[1]]) < 1e-15);
});

test("seeded generator repeats and moons have two balanced classes", () => {
  const a = ml.makeMoons(200, 0.2, 7);
  const b = ml.makeMoons(200, 0.2, 7);
  assert.deepEqual(a, b);
  const ones = a.y.filter((v) => v === 1).length;
  assert.equal(ones, 100);
  assert.notDeepEqual(ml.makeMoons(200, 0.2, 8).X, a.X);
});

test("noiseless moons lie on their two half-circles", () => {
  const { X, y } = ml.makeMoons(50, 0, 1);
  X.forEach(([u, v], i) => {
    const [cx, cy, up] = y[i] === 0 ? [0, 0, true] : [1, 0.5, false];
    assert.ok(Math.abs(Math.hypot(u - cx, v - cy) - 1) < 1e-12);
    assert.ok(up ? v >= -1e-12 : v <= 0.5 + 1e-12);
  });
  const xs = X.filter((_, i) => y[i] === 0).map((p) => p[0]);
  assert.ok(Math.abs(Math.min(...xs) + 1) < 1e-12 && Math.abs(Math.max(...xs) - 1) < 1e-12);
});

test("gaussian naive Bayes equals sklearn GaussianNB: parameters, joint log and posterior", () => {
  for (const f of fx.gnb) {
    const d = fx.datasets[f.ds];
    const m = ml.fitGnb(d.X, d.y, { priors: f.priors });
    assert.ok(maxAbs(m.theta.flat(), f.theta.flat()) < 1e-12, `${f.ds} theta`);
    assert.ok(maxAbs(m.var.flat(), f.var.flat()) < 1e-12, `${f.ds} var`);
    assert.ok(maxAbs(m.prior, f.class_prior) < 1e-12, `${f.ds} prior`);
    const jll = f.grid.map((g) => ml.gnbLogJoint(m, g));
    assert.ok(maxAbs(jll.flat(), f.jll.flat()) < 1e-9, `${f.ds} jll ${maxAbs(jll.flat(), f.jll.flat())}`);
    const p = f.grid.map((g) => ml.gnbProba(m, g));
    assert.ok(maxAbs(p.flat(), f.proba.flat()) < 1e-12, `${f.ds} proba`);
  }
});

test("least squares line, median (MAE) line and regression metrics equal sklearn", () => {
  for (const c of fx.lines) {
    for (const [kind, fit] of [["ols", ml.olsLine], ["lad", ml.ladLine]]) {
      const ref = c[kind];
      const m = fit(c.x, c.y);
      assert.ok(Math.abs(m.w0 - ref.w0) < 1e-7 && Math.abs(m.w1 - ref.w1) < 1e-7, `${c.name} ${kind} ${m.w0} ${m.w1}`);
      const r = ml.regMetrics(c.y, c.x.map((x) => m.w0 + m.w1 * x));
      for (const k of ["mse", "mae", "r2"]) assert.ok(Math.abs(r[k] - ref[k]) < 1e-9, `${c.name} ${kind} ${k}`);
    }
  }
});

test("the MAE line is a global minimum of the summed absolute error", () => {
  const c = fx.lines.find((l) => l.name === "outlier");
  const m = ml.ladLine(c.x, c.y);
  const sae = (w0, w1) => c.x.reduce((s, x, i) => s + Math.abs(c.y[i] - w0 - w1 * x), 0);
  const best = sae(m.w0, m.w1);
  for (let a = -3; a <= 3; a += 0.25) for (let b = -0.5; b <= 0.5; b += 0.05) {
    assert.ok(sae(m.w0 + a, m.w1 + b) >= best - 1e-9);
  }
});

test("moving an outlier up drags the MSE slope but not the MAE slope", () => {
  const c = fx.lines.find((l) => l.name === "outlier");
  const at = (up) => { const y = c.y.slice(); y[15] += up; return [ml.olsLine(c.x, y).w1, ml.ladLine(c.x, y).w1]; };
  const [o1, l1] = at(0), [o2, l2] = at(30);
  assert.ok(o2 - o1 > 0.3);
  assert.ok(Math.abs(l2 - l1) < 1e-9);
});

test("R2 is 1 for a perfect fit, 0 for the mean and negative for a worse constant", () => {
  const y = [1, 2, 4, 8];
  assert.equal(ml.regMetrics(y, y).r2, 1);
  assert.ok(Math.abs(ml.regMetrics(y, y.map(() => 3.75)).r2) < 1e-12);
  assert.ok(ml.regMetrics(y, y.map(() => 10)).r2 < 0);
});

test("margins and the summed step, square, hinge, logistic and exponential losses equal sklearn", () => {
  for (const c of fx.margin) {
    const d = fx.datasets[c.ds];
    const ypm = d.y.map((k) => 2 * k - 1);
    const M = ml.margins(d.X, ypm, c.w, c.b);
    assert.ok(maxAbs(M, c.margins) < 1e-12, `${c.ds} margins`);
    for (const [name, ref] of Object.entries(c.sum)) {
      const s = M.reduce((t, m) => t + ml.marginLoss(name, m), 0);
      assert.ok(Math.abs(s - ref) < 1e-8 * Math.max(1, ref), `${c.ds} ${name}: ${s} vs ${ref}`);
    }
  }
});

test("every margin loss lies on or above the step (the logistic one only with log base 2)", () => {
  for (let M = -6; M <= 6; M += 0.05) {
    const step = ml.marginLoss("step", M);
    for (const name of ["square", "hinge", "logistic", "exp"]) {
      assert.ok(ml.marginLoss(name, M) >= step - 1e-12, `${name} at M=${M}`);
    }
  }
});

test("margin losses take their anchor values and stay finite at extreme margins", () => {
  for (const name of ["step", "square", "hinge", "logistic", "exp"]) {
    assert.ok(Math.abs(ml.marginLoss(name, 0) - 1) < 1e-12, `${name}(0)`);
  }
  assert.equal(ml.marginLoss("hinge", 1), 0);
  assert.equal(ml.marginLoss("hinge", 7), 0);
  assert.equal(ml.marginLoss("square", 1), 0);
  assert.ok(ml.marginLoss("square", 3) > 0);
  assert.ok(Number.isFinite(ml.marginLoss("logistic", -800)) && ml.marginLoss("logistic", -800) > 1000);
  assert.ok(ml.marginLoss("logistic", 800) >= 0 && ml.marginLoss("logistic", 800) < 1e-12);
  assert.throws(() => ml.marginLoss("nope", 0));
});

test("One vs Rest decision values and labels equal sklearn OneVsRestClassifier", () => {
  for (const c of fx.multiclass) {
    const m = ml.fitOvr(c.X, c.y, { C: 1 });
    const z = c.grid.map((g) => ml.ovrDecision(m, g));
    assert.ok(maxAbs(z.flat(), c.ovr.flat()) < 1e-6, `${c.ds} ${maxAbs(z.flat(), c.ovr.flat())}`);
    assert.ok(agree(z.map((r) => m.classes[r.indexOf(Math.max(...r))]), c.ovr_pred) >= 0.999, c.ds);
    const claims = c.grid.map((g) => ml.ovrClaims(m, g));
    assert.deepEqual(claims, c.ovr.map((r) => r.filter((v) => v > 0).length));
  }
});

test("One vs One votes plus confidence equal sklearn OneVsOneClassifier", () => {
  for (const c of fx.multiclass) {
    const m = ml.fitOvo(c.X, c.y, { C: 1 });
    const s = c.grid.map((g) => ml.ovoScores(m, g));
    assert.ok(maxAbs(s.map((r) => r.decision).flat(), c.ovo.flat()) < 1e-6, `${c.ds} ${maxAbs(s.map((r) => r.decision).flat(), c.ovo.flat())}`);
    const pred = s.map((r) => m.classes[r.decision.indexOf(Math.max(...r.decision))]);
    assert.ok(agree(pred, c.ovo_pred) >= 0.999, c.ds);
  }
});

test("a degree-1 logistic model's line a x1 + b x2 + c equals its decision value everywhere", () => {
  const m = ml.fitLogreg(X, y, { degree: 1, C: 1 });
  const { a, b, c } = ml.logregLine(m);
  for (const g of G.slice(0, 200)) assert.ok(Math.abs(a * g[0] + b * g[1] + c - ml.logregDecision(m, g)) < 1e-10);
  assert.throws(() => ml.logregLine(ml.fitLogreg(X, y, { degree: 2 })));
});

test("One vs One gives every pair exactly one vote and the number of pairs is K(K-1)/2", () => {
  const c = fx.multiclass[0];
  const m = ml.fitOvo(c.X, c.y, { C: 1 });
  assert.equal(m.pairs.length, 3);
  for (const g of c.grid.slice(0, 40)) {
    const s = ml.ovoScores(m, g);
    assert.equal(s.votes.reduce((a, v) => a + v, 0), 3);
    assert.equal(s.pairs.length, 3);
    // The confidence term is smaller than one vote, so it only breaks ties.
    assert.ok(s.decision.every((v, k) => Math.abs(v - s.votes[k]) < 1));
  }
});

test("node impurities (misclassification, Gini, entropy in bits) equal scipy and sklearn", () => {
  for (const c of fx.impurity) {
    for (const [kind, key] of [["mis", "mis"], ["gini", "gini"], ["ent", "ent"]]) {
      assert.ok(Math.abs(ml.impurity(c.counts, kind) - c[key]) < 1e-12, `${kind} ${c.counts}`);
    }
  }
});

test("impurity bounds: zero for a pure node, the maximum for equal shares", () => {
  for (const K of [2, 3, 4, 7]) {
    const eq = new Array(K).fill(5);
    assert.ok(Math.abs(ml.impurity(eq, "ent") - Math.log2(K)) < 1e-12);
    assert.ok(Math.abs(ml.impurity(eq, "gini") - (1 - 1 / K)) < 1e-12);
    assert.ok(Math.abs(ml.impurity(eq, "mis") - (1 - 1 / K)) < 1e-12);
    const pure = new Array(K).fill(0); pure[0] = 9;
    for (const kind of ["mis", "gini", "ent"]) assert.equal(ml.impurity(pure, kind), 0);
  }
  assert.throws(() => ml.impurity([1, 1], "nope"));
});

test("threshold scan matches sklearn's depth-1 tree: best threshold, child impurities and gain", () => {
  for (const s of fx.stump) {
    for (const [kind, key] of [["gini", "gini"], ["ent", "entropy"]]) {
      const ref = s[key];
      const scan = ml.scanSplits(s.y, kind);
      const best = ml.bestSplit(scan);
      assert.equal(best.t, ref.t, `${s.name} ${kind} threshold`);
      assert.equal(best.nl, ref.nl);
      assert.ok(Math.abs(best.left - ref.left) < 1e-9 && Math.abs(best.right - ref.right) < 1e-9, `${s.name} ${kind} children`);
      const gain = ref.root - (ref.nl * ref.left + ref.nr * ref.right) / (ref.nl + ref.nr);
      assert.ok(Math.abs(best.gain - gain) < 1e-9, `${s.name} ${kind} gain`);
    }
  }
});

test("misclassification scan counts the errors of the majority class on each side", () => {
  for (const s of fx.stump) {
    const scan = ml.scanSplits(s.y, "mis");
    const wrong = (part) => { const c = {}; part.forEach((v) => (c[v] = (c[v] || 0) + 1)); return part.length - Math.max(...Object.values(c)); };
    scan.forEach((r) => {
      const errs = wrong(s.y.slice(0, r.t + 1)) + wrong(s.y.slice(r.t + 1));
      assert.ok(Math.abs(r.weighted * s.y.length - errs) < 1e-9, `${s.name} t=${r.t}`);
    });
  }
});

test("the lecture's 20 balls: misclassification cannot tell X<=4 from X<=12, Gini and entropy choose 12", () => {
  const balls = fx.stump.find((s) => s.name === "balls").y;
  const mis = ml.scanSplits(balls, "mis");
  assert.ok(Math.abs(mis[4].weighted - mis[12].weighted) < 1e-12);
  assert.ok(Math.abs(mis[12].weighted - 0.3) < 1e-12);
  assert.equal(ml.bestSplit(ml.scanSplits(balls, "gini")).t, 12);
  assert.equal(ml.bestSplit(ml.scanSplits(balls, "ent")).t, 12);
});

test("information gain is never negative for the concave criteria", () => {
  for (const s of fx.stump) for (const kind of ["mis", "gini", "ent"]) {
    ml.scanSplits(s.y, kind).forEach((r) => assert.ok(r.gain >= -1e-12, `${s.name} ${kind} t=${r.t}`));
  }
});

test("bootstrap indices are seeded, in range, and about 63 % of the objects are distinct", () => {
  const m = 100;
  const a = ml.bootstrapIdx(m, ml.rng(5)), b = ml.bootstrapIdx(m, ml.rng(5));
  assert.deepEqual(a, b);
  assert.equal(a.length, m);
  assert.ok(a.every((i) => Number.isInteger(i) && i >= 0 && i < m));
  const r = ml.rng(9);
  assert.equal(Math.max(...Array.from({ length: 50 }, () => Math.max(...ml.bootstrapIdx(m, r)))), m - 1);
  let share = 0;
  for (let k = 0; k < 400; k++) share += new Set(ml.bootstrapIdx(m, r)).size / m / 400;
  assert.ok(Math.abs(share - (1 - (1 - 1 / m) ** m)) < 0.005, `share ${share}`);
});

test("a tree with random feature subsets still separates the training set and uses both features", () => {
  const r = ml.rng(3);
  const used = new Set(), roots = new Set();
  for (let k = 0; k < 20; k++) {
    const t = ml.fitTree(X, y, { maxFeatures: 1, rnd: r });
    roots.add(t.feature);
    assert.equal(ml.accuracy(X.map((x) => ml.treePredict(t, x)), y), 1);
    const walk = (n) => { if (n.left) { used.add(n.feature); walk(n.left); walk(n.right); } };
    walk(t);
  }
  assert.deepEqual([...used].sort(), [0, 1]);
  // With one candidate feature per node the root feature is drawn at random.
  assert.deepEqual([...roots].sort(), [0, 1]);
});

test("a forest without bootstrap and with all features is one tree: it equals sklearn's tree", () => {
  for (const { depth, pred } of fx.tree) {
    const f = ml.fitForest(X, y, { nTrees: 5, maxDepth: depth, bootstrap: false, seed: 1 });
    const p = G.map((g) => { const q = ml.forestProba(f, g); return q.indexOf(Math.max(...q)); });
    assert.ok(agree(p, pred) >= 0.98, `depth=${depth} ${agree(p, pred)}`);
  }
});

test("every tree reports shares for all classes even if its bootstrap sample lacks the rarest one", () => {
  const Xr = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]], yr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 2];
  const f = ml.fitForest(Xr, yr, { nTrees: 40, seed: 2 });
  assert.ok(f.trees.some((t, k) => f.inbag[k][9] === 0), "no tree missed the rare object");
  f.trees.forEach((t) => assert.equal(ml.treeProba(t, [0]).length, 3));
  assert.equal(ml.forestProba(f, [3]).length, 3);
});

test("forest class shares are probabilities, also for a prefix of the trees", () => {
  const f = ml.fitForest(X, y, { nTrees: 12, maxFeatures: 1, seed: 5 });
  for (const g of G.slice(0, 30)) for (const n of [1, 5, 12]) {
    assert.ok(Math.abs(ml.forestProba(f, g, n).reduce((s, v) => s + v, 0) - 1) < 1e-12);
  }
  assert.deepEqual(ml.forestProba(f, G[0], 1), ml.treeProba(f.trees[0], G[0]));
});

test("OOB prediction averages exactly the trees that did not see the object", () => {
  const f = ml.fitForest(X, y, { nTrees: 15, maxFeatures: 1, seed: 4 });
  X.forEach((x, i) => {
    const ids = f.trees.map((_, t) => t).filter((t) => f.inbag[t][i] === 0);
    const got = ml.oobProba(f, i);
    if (ids.length === 0) { assert.equal(got, null); return; }
    const want = [0, 0];
    ids.forEach((t) => ml.treeProba(f.trees[t], x).forEach((v, k) => (want[k] += v / ids.length)));
    assert.ok(maxAbs(got, want) < 1e-12, `object ${i}`);
  });
});

test("the share of objects with an OOB estimate follows 1 - (1 - 1/e)^n", () => {
  const f = ml.fitForest(X, y, { nTrees: 30, maxFeatures: 1, seed: 6 });
  for (const n of [1, 2, 5]) {
    const covered = X.filter((_, i) => ml.oobProba(f, i, n) !== null).length / X.length;
    assert.ok(Math.abs(covered - (1 - (1 - 1 / Math.E) ** n)) < 0.08, `n=${n} ${covered}`);
  }
  assert.equal(X.filter((_, i) => ml.oobProba(f, i, 30) !== null).length, X.length);
});

test("a forest beats the average single tree on fresh data", () => {
  const train = ml.makeMoons(210, 0.3, 21), test = ml.makeMoons(300, 0.3, 22);
  const f = ml.fitForest(train.X, train.y, { nTrees: 60, maxFeatures: 1, seed: 8 });
  const acc = (fn) => ml.accuracy(test.X.map(fn), test.y);
  const forest = acc((x) => { const q = ml.forestProba(f, x); return q.indexOf(Math.max(...q)); });
  const single = f.trees.map((t) => acc((x) => ml.treePredict(t, x))).reduce((s, v) => s + v, 0) / f.trees.length;
  assert.ok(forest > single, `forest ${forest} single ${single}`);
});

test("variance of an average of correlated models is rho sigma^2 + (1 - rho) sigma^2 / N", () => {
  assert.equal(ml.ensembleVariance(0, 2, 4), 0.5);
  assert.equal(ml.ensembleVariance(1, 2, 4), 2);
  assert.ok(Math.abs(ml.ensembleVariance(0.4, 2, 10) - (0.8 + 0.6 * 2 / 10)) < 1e-12);
  const r = ml.rng(2), N = 10, S = 6000, rho = 0.4, s2 = 2;
  const P = Array.from({ length: S }, () => {
    const shared = ml.gauss(r);
    return Array.from({ length: N }, () => Math.sqrt(s2) * (Math.sqrt(rho) * shared + Math.sqrt(1 - rho) * ml.gauss(r)));
  });
  const st = ml.ensembleStats([P]);
  assert.ok(Math.abs(st.rho - rho) < 0.025 && Math.abs(st.sigma2 - s2) < 0.1, `${st.rho} ${st.sigma2}`);
  assert.ok(Math.abs(st.varMean[N - 1] - ml.ensembleVariance(rho, s2, N)) < 0.06);
  assert.ok(Math.abs(st.varMean[0] - s2) < 0.1);
});

test("covariance matrix of two models over two training sets, by hand", () => {
  // columns [1, 3] and [2, 6]: means 2 and 4, variances 1 and 4, covariance 2
  const c = ml.covMatrix([[1, 2], [3, 6]]);
  assert.deepEqual(c, [[1, 2], [2, 4]]);
  const st = ml.ensembleStats([[[1, 2], [3, 6]]]);
  assert.ok(Math.abs(st.sigma2 - 2.5) < 1e-12 && Math.abs(st.rho - 2 / 2.5) < 1e-12);
  assert.ok(Math.abs(st.varMean[1] - (1 + 4 + 2 * 2) / 4) < 1e-12);
});

test("variance of the mean equals the sum of all covariances over N squared, exactly", () => {
  const r = ml.rng(12);
  const P = Array.from({ length: 50 }, () => { const z = ml.gauss(r); return [z + ml.gauss(r), 2 * z, ml.gauss(r) - z, z]; });
  const cov = ml.covMatrix(P);
  const st = ml.ensembleStats([P]);
  for (let n = 1; n <= 4; n++) {
    let s = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) s += cov[i][j];
    assert.ok(Math.abs(st.varMean[n - 1] - s / (n * n)) < 1e-12, `n=${n}`);
  }
});

test("seeded noisy sine: repeatable, noise-free it is sin 2 pi x", () => {
  const a = ml.makeSine(40, 0.25, 3), b = ml.makeSine(40, 0.25, 3);
  assert.deepEqual(a, b);
  const c = ml.makeSine(30, 0, 1);
  c.x.forEach((x, i) => assert.ok(Math.abs(c.y[i] - Math.sin(2 * Math.PI * x)) < 1e-12));
  assert.ok(c.x.every((x, i) => x >= 0 && x <= 1 && (i === 0 || x >= c.x[i - 1])));
});

test("naive Bayes posterior sums to one and a single class gets all of it", () => {
  const d = fx.datasets.blobs3;
  const m = ml.fitGnb(d.X, d.y);
  for (const g of fx.grid.slice(0, 50)) {
    assert.ok(Math.abs(ml.gnbProba(m, g).reduce((s, v) => s + v, 0) - 1) < 1e-12);
  }
  const far = ml.gnbProba(m, [1e4, 1e4]);
  assert.ok(far.every((v) => Number.isFinite(v)));
  assert.ok(Math.abs(Math.max(...far) - 1) < 1e-12);
});

// ---------- bias-variance sandbox ----------

test("Legendre least squares equals sklearn LinearRegression on the Legendre design", () => {
  for (const c of fx.legendre) {
    const m = ml.fitLegendre(c.x, c.y, c.degree);
    assert.ok(maxAbs(m.coef, c.coef) < 1e-8, `degree ${c.degree} coef ${maxAbs(m.coef, c.coef)}`);
    const p = fx.legendre_grid.map((g) => ml.legendrePredict(m, g));
    assert.ok(maxAbs(p, c.pred) < 1e-8, `degree ${c.degree} pred ${maxAbs(p, c.pred)}`);
  }
});

test("bias^2 and variance equal the static figures' decompose on the same predictions", () => {
  const d = fx.bv_decompose;
  const f = d.grid.map((x) => Math.sin(2 * Math.PI * x));
  const r = ml.decomposeBV(d.P, f);
  assert.ok(Math.abs(r.bias2 - d.bias2) < 1e-12, `${r.bias2} vs ${d.bias2}`);
  assert.ok(Math.abs(r.variance - d.variance) < 1e-12, `${r.variance} vs ${d.variance}`);
});

test("corrected bias^2 plus variance is exactly the mean squared distance of the models from f", () => {
  const r = ml.rng(4);
  const G = 17, M = 23;
  const f = Array.from({ length: G }, (_, j) => Math.sin(j));
  const P = Array.from({ length: M }, () => f.map((v) => v + 0.3 * ml.gauss(r) + 0.2));
  const direct = P.reduce((s, row) => s + row.reduce((t, v, j) => t + (v - f[j]) ** 2, 0), 0) / (M * G);
  const d = ml.decomposeBV(P, f);
  assert.ok(Math.abs(d.bias2 + d.variance - direct) < 1e-12);
  assert.ok(d.bias2 < d.biasRaw, "the correction removes the mean's own noise");
});

test("a constant model: bias^2 is the mean of sin^2 and variance is the variance of y over n", () => {
  const s = ml.makeBvStreams({ resamples: 3000, fresh: 5, maxN: 30, seed: 1 });
  const r = ml.bvEstimate(s, { degree: 0, noise: 0.25, n: 30 });
  assert.ok(Math.abs(r.bias2 - 0.5) < 0.02, `bias2 ${r.bias2}`);
  const v = (0.5 + 0.0625) / 30;
  assert.ok(Math.abs(r.variance - v) < 0.1 * v, `variance ${r.variance} vs ${v}`);
  assert.equal(r.noise, 0.0625);
});

test("the measured error uses samples independent of the ones behind bias^2 and variance", () => {
  const a = ml.makeBvStreams({ resamples: 200, fresh: 10, maxN: 40, seed: 3 });
  const b = ml.makeBvStreams({ resamples: 200, fresh: 10, maxN: 40, seed: 3 });
  const opt = { degree: 3, noise: 0.25, n: 30 };
  const base = ml.bvEstimate(a, opt);
  assert.deepEqual(ml.bvEstimate(b, opt), base, "repeatable");
  // Replace only the measurement group: bias^2 and variance must not move.
  const other = ml.makeBvStreams({ resamples: 200, fresh: 10, maxN: 40, seed: 99 });
  const swappedB = ml.bvEstimate({ ...a, b: other.b, t: other.t }, opt);
  assert.equal(swappedB.bias2, base.bias2);
  assert.equal(swappedB.variance, base.variance);
  assert.notEqual(swappedB.measured, base.measured);
  // Replace only the formula group: the measurement must not move.
  const swappedA = ml.bvEstimate({ ...a, a: other.a }, opt);
  assert.equal(swappedA.measured, base.measured);
  assert.notEqual(swappedA.bias2, base.bias2);
  // No training sample is shared between the two groups.
  const key = (s) => s.x.slice(0, 5).join();
  const keysA = new Set(a.a.map(key));
  assert.ok(a.b.every((s) => !keysA.has(key(s))));
});

test("the parts add up to the error measured on fresh pairs, within estimate noise (an identity in expectation, not a check)", () => {
  const s = ml.makeBvStreams({ resamples: 1500, fresh: 20, maxN: 30, seed: 7 });
  for (const [degree, noise] of [[1, 0.25], [3, 0.25], [5, 0.25], [3, 0.5], [3, 0]]) {
    const r = ml.bvEstimate(s, { degree, noise, n: 30 });
    const tol = 4 * Math.hypot(r.seMeasured, r.seSum) + 1e-9;
    assert.ok(Math.abs(r.sum - r.measured) < tol, `degree ${degree} noise ${noise}: ${r.sum} vs ${r.measured} tol ${tol}`);
    assert.ok(r.seMeasured > 0 && r.seSum > 0);
  }
});

test("the reported standard errors are the real spread of the estimates over repeated experiments", () => {
  const runs = Array.from({ length: 16 }, (_, k) =>
    ml.bvEstimate(ml.makeBvStreams({ resamples: 200, fresh: 20, maxN: 30, seed: 100 + k }), { degree: 3, noise: 0.25, n: 30 }));
  const sd = (v) => { const m = v.reduce((a, b) => a + b, 0) / v.length; return Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / (v.length - 1)); };
  const mean = (v) => v.reduce((a, b) => a + b, 0) / v.length;
  for (const [what, spread, se] of [["sum", sd(runs.map((r) => r.bias2 + r.variance)), mean(runs.map((r) => r.seSum))],
    ["measured", sd(runs.map((r) => r.measured)), mean(runs.map((r) => r.seMeasured))]]) {
    assert.ok(se / spread > 0.5 && se / spread < 2, `${what}: reported ${se}, actual ${spread}`);
  }
});

test("more complexity: bias^2 falls, variance rises; more data: variance falls; more noise: sigma^2 and variance rise", () => {
  const s = ml.makeBvStreams({ resamples: 600, fresh: 5, maxN: 150, seed: 2 });
  const at = (degree, n = 30, noise = 0.25) => ml.bvEstimate(s, { degree, noise, n });
  assert.ok(at(0).bias2 > at(1).bias2 && at(1).bias2 > at(3).bias2);
  assert.ok(at(3).variance < at(5).variance && at(5).variance < at(7).variance);
  assert.ok(at(7, 150).variance < at(7, 30).variance / 3);
  assert.ok(at(3, 30, 0.5).variance > at(3, 30, 0.25).variance);
  assert.equal(at(3, 30, 0.5).noise, 0.25);
});

// ---------- MLP ----------
// The page trains full-batch gradient descent without momentum and without L2:
// sklearn's solver="sgd", momentum=0, batch_size=n. sklearn stores a layer as
// (in, out); the note and mlcore write W as (out, in).

const T = (m) => m[0].map((_, j) => m.map((row) => row[j]));
const netFrom = (act, w) => ({ act, W: w.coefs.map(T), b: w.intercepts.map((b) => b.slice()) });
const SK_ACT = { identity: "linear" };
const MLP = fx.mlp;

test("MLP forward pass equals sklearn predict_proba on the weights of a trained model, to 1e-12", () => {
  for (const c of MLP.forward) {
    const net = netFrom(SK_ACT[c.act] ?? c.act, { coefs: c.coefs, intercepts: c.intercepts });
    const p = c.points.map((x) => ml.mlpProba(net, x));
    assert.ok(maxAbs(p, c.proba1) < 1e-12, `${c.hidden} ${c.act}: ${maxAbs(p, c.proba1)}`);
  }
});

test("MLP forward pass on a network without activation is an affine map of the input", () => {
  const net = ml.mlpInit([5, 4], "linear", 3);
  const logit = (x) => ml.mlpLogit(net, x);
  const a = [0.3, -0.8], b = [-1.1, 0.4];
  const mid = a.map((v, i) => (v + b[i]) / 2);
  assert.ok(Math.abs(logit(mid) - (logit(a) + logit(b)) / 2) < 1e-12);
});

const cloneNet = (net) => ({ act: net.act, W: net.W.map((M) => M.map((r) => r.slice())), b: net.b.map((v) => v.slice()) });

test("MLP backpropagation equals central finite differences for every activation and depth", () => {
  const { Xtr, ytr } = MLP.splits.circles;
  const X = Xtr.slice(0, 40), y = ytr.slice(0, 40);
  for (const [hidden, act] of [[[3], "tanh"], [[4, 3], "logistic"], [[3, 4, 2], "relu"], [[5, 5], "linear"], [[8, 8, 8], "tanh"]]) {
    const net = ml.mlpInit(hidden, act, 11);
    const g = ml.mlpGrad(net, X, y);
    const h = 1e-6;
    let worst = 0;
    const probe = (get, set, analytic) => {
      const v = get();
      set(v + h); const up = ml.mlpLoss(net, X, y);
      set(v - h); const down = ml.mlpLoss(net, X, y);
      set(v);
      worst = Math.max(worst, Math.abs((up - down) / (2 * h) - analytic));
    };
    net.W.forEach((M, k) => M.forEach((row, j) => row.forEach((_, i) =>
      probe(() => net.W[k][j][i], (v) => { net.W[k][j][i] = v; }, g.W[k][j][i]))));
    net.b.forEach((bk, k) => bk.forEach((_, j) =>
      probe(() => net.b[k][j], (v) => { net.b[k][j] = v; }, g.b[k][j])));
    assert.ok(worst < 1e-7, `${hidden} ${act}: worst ${worst}`);
  }
});

test("MLP gradient step equals sklearn solver=sgd, momentum=0, full batch: weights and loss for several steps, to 1e-12", () => {
  for (const c of MLP.step) {
    const { Xtr: X, ytr: y } = MLP.splits[c.data];
    const act = SK_ACT[c.act] ?? c.act;
    let net = netFrom(act, c.start);
    c.after.forEach((want, s) => {
      assert.ok(Math.abs(ml.mlpLoss(net, X, y) - c.loss_before[s]) < 1e-12 * Math.max(1, c.loss_before[s]), `${c.hidden} ${c.act} loss before step ${s}`);
      net = ml.mlpStep(net, X, y, c.lr);
      const ref = netFrom(act, want);
      const err = Math.max(...net.W.map((M, k) => maxAbs(M.flat(), ref.W[k].flat())), ...net.b.map((v, k) => maxAbs(v, ref.b[k])));
      const scale = Math.max(1, ...ref.W.map((M) => Math.max(...M.flat().map(Math.abs))));
      assert.ok(err < 1e-12 * scale, `${c.hidden} ${c.act} lr=${c.lr} step ${s}: ${err}`);
    });
  }
});

test("MLP step does not change the network it is given", () => {
  const { Xtr, ytr } = MLP.splits.xor;
  const net = ml.mlpInit([3, 3], "tanh", 2);
  const before = JSON.stringify(net);
  const next = ml.mlpStep(net, Xtr, ytr, 0.5);
  assert.equal(JSON.stringify(net), before);
  assert.notEqual(JSON.stringify(next), before);
});

test("MLP initial weights are seeded, Glorot-bounded as in sklearn, and differ between seeds", () => {
  const a = ml.mlpInit([4, 3], "relu", 5), b = ml.mlpInit([4, 3], "relu", 5), c = ml.mlpInit([4, 3], "relu", 6);
  assert.deepEqual(a, b);
  assert.notDeepEqual(a, c);
  assert.deepEqual(a.W.map((M) => [M.length, M[0].length]), [[4, 2], [3, 4], [1, 3]]);
  // sklearn: uniform in +-sqrt(6/(fan_in+fan_out)), factor 2 instead of 6 for the logistic activation.
  for (const [act, factor] of [["relu", 6], ["logistic", 2]]) {
    const net = ml.mlpInit([8, 8], act, 1);
    net.W.forEach((M, k) => {
      const bound = Math.sqrt(factor / (M.length + M[0].length));
      const vals = [...M.flat(), ...net.b[k]];
      assert.ok(vals.every((v) => Math.abs(v) <= bound), `${act} layer ${k}`);
      assert.ok(Math.max(...vals.map(Math.abs)) > 0.5 * bound, `${act} layer ${k} should fill the range`);
    });
  }
});

// Scenarios of the page. Each one is a claim of the lecture; the page applies
// the same record, so what the page promises is what these tests measured.
const BOX = { lo: [-2.2, -2.2], hi: [2.2, 2.2] };
const scenario = (id) => ml.MLP_SCENARIOS.find((s) => s.id === id);
function run(s, { seed = s.seed, lr = s.lr, epochs = s.epochs } = {}) {
  const d = MLP.splits[s.data];
  let net = ml.mlpInit(s.hidden, s.act, seed);
  const train = [ml.mlpLoss(net, d.Xtr, d.ytr)];
  for (let e = 0; e < epochs; e++) {
    net = ml.mlpStep(net, d.Xtr, d.ytr, lr);
    train.push(ml.mlpLoss(net, d.Xtr, d.ytr));
  }
  const acc = ml.accuracy(d.Xtr.map((x) => (ml.mlpProba(net, x) > 0.5 ? 1 : 0)), d.ytr);
  return { net, train, acc };
}

test("scenario records are complete and their ids are unique", () => {
  const ids = ml.MLP_SCENARIOS.map((s) => s.id);
  assert.equal(new Set(ids).size, ids.length);
  for (const s of ml.MLP_SCENARIOS) {
    assert.ok(s.label && MLP.splits[s.data] && s.hidden.length >= 1 && s.hidden.length <= 3, s.id);
    assert.ok(s.hidden.every((n) => n >= 1 && n <= 8) && ["tanh", "logistic", "relu", "linear"].includes(s.act), s.id);
    assert.ok(s.lr > 0 && s.lr <= 10 && s.epochs > 0 && Number.isInteger(s.seed), s.id);
  }
});

test("three tanh neurons on circles make a rounded triangle: three corners, separated training set", () => {
  const { net, acc } = run(scenario("tanh3"));
  assert.ok(acc >= 0.98, `train accuracy ${acc}`);
  assert.equal(ml.mlpCorners(net, BOX), 3);
});

test("three ReLU neurons on circles make a hexagon at a lucky seed: six corners", () => {
  const { net, acc } = run(scenario("relu3"));
  assert.ok(acc >= 0.98, `train accuracy ${acc}`);
  assert.equal(ml.mlpCorners(net, BOX), 6);
});

test("the corner counter gives no answer for a region that reaches the box edge or for an empty one", () => {
  const ring = { act: "linear", W: [[[1, 0]], [[1]]], b: [[0], [0]] };
  assert.equal(ml.mlpCorners(ring, BOX), null, "a half-plane touches the box");
  const dead = { act: "relu", W: [[[1, 0]], [[1]]], b: [[-9], [-1]] };
  assert.equal(ml.mlpCorners(dead, BOX), null, "no positive region");
});

test("one architecture, different seeds: tanh always converges, ReLU often does not, and a dead start predicts a constant", () => {
  const seeds = Array.from({ length: 12 }, (_, i) => i + 1);
  const loss = (id, seed) => run(scenario(id), { seed }).train.at(-1);
  const tanh = seeds.map((s) => loss("tanh3", s));
  assert.ok(tanh.every((l) => l < 0.1), `tanh ${tanh}`);
  const relu = seeds.map((s) => loss("relu3", s));
  const good = relu.filter((l) => l < 0.1).length, bad = relu.filter((l) => l > 0.4).length;
  assert.ok(good >= 3 && bad >= 3, `relu converged ${good}, stuck ${bad}: ${relu}`);
  const stuck = run(scenario("relu3-stuck")), dead = run(scenario("relu3-dead"));
  assert.ok(stuck.train.at(-1) > 0.4 && stuck.acc < 0.9);
  const p = MLP.splits.circles.Xtr.map((x) => ml.mlpProba(dead.net, x));
  assert.equal(Math.max(...p), Math.min(...p), "all hidden neurons dead: one probability for every point");
  assert.ok(Math.abs(dead.train.at(-1) - Math.LN2) < 0.01);
});

test("a big step explodes the loss and leaves a constant, while the same start at a small step converges", () => {
  const s = scenario("explode");
  const big = run(s);
  assert.ok(Math.max(...big.train) > 3 * big.train[0], `peak ${Math.max(...big.train)} from ${big.train[0]}`);
  const { Xtr } = MLP.splits[s.data];
  const p = Xtr.map((x) => ml.mlpProba(big.net, x));
  assert.equal(Math.max(...p), Math.min(...p));
  assert.ok(big.train.at(-1) > big.train[0], "the loss ends above where it started");
  const small = run(s, { lr: s.lr / 100, epochs: 3000 });
  assert.ok(small.train.at(-1) < 0.1 && Math.max(...small.train) <= small.train[0] * 1.01, `small step: ${small.train.at(-1)}`);
});

// ---------- optimizers on a surface ----------
// Reference: figures/06/opt_common.py, the code behind the table of the note
// "Оптимизаторы нейросетей". Methods are named as in the page.

const OPT = fx.opt;
const OPT_NAME = { SGD: "sgd", Momentum: "momentum", Nesterov: "nesterov", Adagrad: "adagrad", RMSProp: "rmsprop", Adam: "adam" };
const relErr = (a, b) => Math.max(...a.flat().map((v, i) => Math.abs(v - b.flat()[i]) / Math.max(1, Math.abs(b.flat()[i]))));

test("surfaces: values and gradients equal opt_common.py, gradients equal finite differences", () => {
  for (const [id, ref] of Object.entries(OPT.surfaces)) {
    const S = ml.SURFACES[id];
    ref.points.forEach((p, i) => {
      assert.ok(Math.abs(S.f(p) - ref.f[i]) < 1e-12 * Math.max(1, ref.f[i]), `${id} f at ${p}`);
      assert.ok(maxAbs(S.g(p), ref.grad[i]) < 1e-12 * Math.max(1, ...ref.grad[i].map(Math.abs)), `${id} grad at ${p}`);
    });
  }
  for (const [id, S] of Object.entries(ml.SURFACES)) {
    for (const p of [[-1.5, 1.8], [0.4, -0.7], [1.2, 0.3]]) {
      const h = 1e-6;
      const fd = [0, 1].map((k) => {
        const up = p.slice(), down = p.slice();
        up[k] += h; down[k] -= h;
        return (S.f(up) - S.f(down)) / (2 * h);
      });
      assert.ok(maxAbs(fd, S.g(p)) < 1e-6 * Math.max(1, ...fd.map(Math.abs)), `${id} at ${p}`);
    }
    assert.ok(Math.abs(S.f(S.min)) < 1e-15, `${id} minimum`);
  }
});

test("every optimizer path equals opt_common.py: the note's setting and other surfaces, starts, steps, rho and beta", () => {
  for (const c of OPT.table) {
    const S = ml.SURFACES.rosen;
    const path = ml.optPath(OPT_NAME[c.method], S.g, [-1.5, 1.8], { lr: c.lr, steps: 100 });
    assert.equal(path.length, 101);
    assert.ok(relErr(path, c.path) < 1e-12, `${c.method}: ${relErr(path, c.path)}`);
  }
  for (const c of OPT.variants) {
    const path = ml.optPath(OPT_NAME[c.method], ml.SURFACES[c.surface].g, c.start, { lr: c.lr, steps: c.steps, rho: c.rho, beta: c.beta });
    assert.ok(relErr(path, c.path) < 1e-12, `${c.method} on ${c.surface}: ${relErr(path, c.path)}`);
  }
});

test("the preset steps reproduce the table of the note: loss and distance after the steps, to the digits printed there", () => {
  // loss and distance to the minimum as the note prints them: [value, significant digits]
  const note = { sgd: [[0.125, 3], [0.69, 2]], momentum: [[1.4e-4, 2], [0.002, 1]], nesterov: [[1.1e-5, 2], [0.008, 1]],
    adagrad: [[2.35, 3], [1.67, 3]], rmsprop: [[0.021, 2], [0.31, 2]], adam: [[0.087, 2], [0.59, 2]] };
  const S = ml.SURFACES.rosen, P = ml.OPT_PRESET;
  assert.deepEqual(Object.keys(P.lr), ml.OPT_METHODS);
  for (const m of ml.OPT_METHODS) {
    const path = ml.optPath(m, S.g, S.start, { lr: 10 ** P.lr[m], steps: P.steps, rho: P.rho, beta: P.beta });
    const end = path.at(-1), f = S.f(end), dist = Math.hypot(end[0] - S.min[0], end[1] - S.min[1]);
    const [[nf, df], [nd, dd]] = note[m];
    assert.equal(+f.toPrecision(df), nf, `${m} loss ${f}`);
    assert.equal(+dist.toPrecision(dd), nd, `${m} distance ${dist}`);
  }
  assert.equal(P.steps, 100);
});

test("momentum with rho = 0 is plain descent; Adam's first step is eta g / (|g| + eps) per coordinate", () => {
  const S = ml.SURFACES.ellipse;
  const a = ml.optPath("sgd", S.g, [-2.6, 1.6], { lr: 0.05, steps: 20 });
  const b = ml.optPath("momentum", S.g, [-2.6, 1.6], { lr: 0.05, steps: 20, rho: 0 });
  assert.ok(maxAbs(a.flat(), b.flat()) < 1e-15);
  const x0 = [-2.6, 1.6], g = S.g(x0);
  const adam = ml.optPath("adam", S.g, x0, { lr: 0.1, steps: 1 });
  assert.ok(maxAbs(adam[1], x0.map((v, i) => v - (0.1 * g[i]) / (Math.abs(g[i]) + 1e-8))) < 1e-15);
});

test("on a constant gradient Adagrad's step shrinks every step while RMSProp's settles at eta", () => {
  const grad = () => [1, 0];
  const lens = (m, o = {}) => {
    const p = ml.optPath(m, grad, [0, 0], { lr: 0.1, steps: 200, ...o });
    return p.slice(1).map((q, i) => Math.abs(q[0] - p[i][0]));
  };
  const ada = lens("adagrad"), rms = lens("rmsprop");
  assert.ok(ada.every((s, i) => i === 0 || s < ada[i - 1]), "Adagrad shrinks every step");
  assert.ok(Math.abs(rms.at(-1) - 0.1) < 1e-3, `RMSProp settles at eta, got ${rms.at(-1)}`);
});

test("divergence flag: a too big step is flagged, the preset runs are not", () => {
  const S = ml.SURFACES.rosen;
  const big = ml.optPath("sgd", S.g, S.start, { lr: 0.2, steps: 100 });
  assert.equal(ml.optDiverged(S.f, big), true);
  // Finite but growing: the y coordinate of the ellipse doubles in magnitude every step at this lr.
  const E = ml.SURFACES.ellipse;
  assert.equal(ml.optDiverged(E.f, ml.optPath("sgd", E.g, E.start, { lr: 0.15, steps: 12 })), true);
  assert.equal(ml.optDiverged(E.f, ml.optPath("sgd", E.g, E.start, { lr: 0.15, steps: 2 })), false, "a few steps of growth are not yet a divergence");
  for (const m of ml.OPT_METHODS) {
    const p = ml.optPath(m, S.g, S.start, { lr: 10 ** ml.OPT_PRESET.lr[m], steps: 100, rho: 0.9, beta: 0.9 });
    assert.equal(ml.optDiverged(S.f, p), false, m);
  }
});

test("MLP loss is stable for huge logits and equals the log loss on moderate ones", () => {
  const net = { act: "linear", W: [[[1, 0]], [[1]]], b: [[0], [0]] };
  assert.ok(Math.abs(ml.mlpLoss(net, [[0, 0]], [0]) - Math.LN2) < 1e-15);
  assert.ok(Math.abs(ml.mlpLoss(net, [[2, 0]], [1]) - Math.log(1 + Math.exp(-2))) < 1e-15);
  assert.equal(ml.mlpLoss(net, [[800, 0]], [0]), 800);
  assert.equal(ml.mlpLoss(net, [[800, 0]], [1]), 0);
});

// ---------- feature importance ----------

const IM = fx.importance;
const imAcc = (pred) => (X, y) => ml.accuracy(X.map(pred), y);
const treeFit = (params) => (X, y) => { const t = ml.fitTree(X, y, params); return (x) => ml.treePredict(t, x); };
const lrFit = (X, y) => { const m = ml.fitLogreg(X, y, { C: 1 }); return (x) => (ml.logregDecision(m, x) > 0 ? 1 : 0); };
const sdOf = (v) => { const m = v.reduce((s, a) => s + a, 0) / v.length; return Math.sqrt(v.reduce((s, a) => s + (a - m) ** 2, 0) / v.length); };
const jsParams = (p) => ({ maxDepth: p.max_depth ?? Infinity, minLeaf: p.min_samples_leaf ?? 1 });

test("tree impurity importance equals sklearn feature_importances_ (the tree itself is checked by its held-out accuracy)", () => {
  for (const c of IM.trees) {
    const t = ml.fitTree(IM.Xtr, IM.ytr, jsParams(c.params));
    const acc = ml.accuracy(IM.Xte.map((x) => ml.treePredict(t, x)), IM.yte);
    assert.equal(acc, c.test_acc, JSON.stringify(c.params));
    assert.ok(maxAbs(ml.treeImportance(t, 5), c.mdi) < 1e-12, JSON.stringify(c.params));
  }
});

test("forest importance is the mean of the trees' normalised shares of the trees with a split, divided by its sum (hand-built trees)", () => {
  const leaf = (n, impurity) => ({ n, impurity });
  const t1 = { n: 10, impurity: 0.5, feature: 0, left: leaf(5, 0), right: leaf(5, 0) };
  const t2 = { n: 10, impurity: 0.5, feature: 1, right: leaf(5, 0),
    left: { n: 5, impurity: 0.32, feature: 0, left: leaf(2, 0.5), right: leaf(3, 0) } };
  // t2: feature 1 brings 10*0.5 - 5*0.32 = 3.4, feature 0 brings 5*0.32 - 2*0.5 = 0.6, shares 0.85 and 0.15.
  assert.ok(maxAbs(ml.treeImportance(t2, 2), [0.15, 0.85]) < 1e-12);
  assert.ok(maxAbs(ml.forestImportance({ trees: [t1, t2, leaf(10, 0.5)] }, 2), [0.575, 0.425]) < 1e-12);
  assert.deepEqual(ml.forestImportance({ trees: [leaf(10, 0.5)] }, 2), [0, 0]);
  assert.deepEqual(ml.treeImportance(leaf(10, 0.5), 2), [0, 0]);
});

test("a forest of one tree without bootstrap has sklearn's tree importances", () => {
  const c = IM.trees[0];
  const f = ml.fitForest(IM.Xtr, IM.ytr, { nTrees: 1, bootstrap: false, ...jsParams(c.params), seed: 1 });
  assert.ok(maxAbs(ml.forestImportance(f, 5), c.mdi) < 1e-12);
});

test("permutation importance equals sklearn's on the same permutations, for a tree and for a logistic regression", () => {
  const check = (pred, ref, label) => {
    const r = ml.permutationImportance(imAcc(pred), IM.Xte, IM.yte, IM.perms);
    ref.all.forEach((row, j) => assert.ok(maxAbs(r.importances[j], row) < 1e-12, `${label} column ${j}`));
    assert.ok(maxAbs(r.mean, ref.mean) < 1e-12, label);
    assert.ok(maxAbs(r.std, ref.std) < 1e-12, label);
  };
  for (const c of IM.trees) {
    const t = ml.fitTree(IM.Xtr, IM.ytr, jsParams(c.params));
    check((x) => ml.treePredict(t, x), c.permutation, JSON.stringify(c.params));
  }
  const m = ml.fitLogreg(IM.Xtr, IM.ytr, { C: 1 });
  check((x) => (ml.logregDecision(m, x) > 0 ? 1 : 0), IM.logreg.permutation, "logreg");
});

test("drop column equals the held-out score lost by sklearn's refit without the column", () => {
  for (const c of IM.trees) {
    const r = ml.dropColumn(treeFit(jsParams(c.params)), IM.Xtr, IM.ytr, IM.Xte, IM.yte);
    assert.ok(maxAbs(r.importances, c.drop) < 1e-12, JSON.stringify(c.params));
  }
  const r = ml.dropColumn(lrFit, IM.Xtr, IM.ytr, IM.Xte, IM.yte);
  assert.ok(maxAbs(r.importances, IM.logreg.drop) < 1e-12);
});

test("drop column of the only column has no answer instead of a fit on nothing", () => {
  const r = ml.dropColumn(treeFit({}), IM.Xtr.map((x) => [x[0]]), IM.ytr, IM.Xte.map((x) => [x[0]]), IM.yte);
  assert.ok(Number.isNaN(r.importances[0]));
});

test("logistic weights: original units, standardised, and divided by the std of the logit, as sklearn", () => {
  const m = ml.fitLogreg(IM.Xtr, IM.ytr, { C: 1 });
  const w = ml.logregWeights(m, IM.Xtr);
  assert.ok(maxAbs(w.raw, IM.logreg.raw) < 1e-8);
  assert.ok(maxAbs(w.std, IM.logreg.std) < 1e-8);
  assert.ok(maxAbs(w.beta, IM.logreg.beta) < 1e-8);
});

test("another unit of a feature changes only its original-unit weight, and leaves a tree untouched", () => {
  const km = (X) => X.map((x) => x.slice());
  const metres = IM.Xtr.map((x) => [x[0] * 1000, ...x.slice(1)]);
  const a = ml.logregWeights(ml.fitLogreg(km(IM.Xtr), IM.ytr, { C: 1 }), IM.Xtr);
  const b = ml.logregWeights(ml.fitLogreg(metres, IM.ytr, { C: 1 }), metres);
  assert.ok(Math.abs(a.raw[0] / b.raw[0] - 1000) < 1e-6);
  assert.ok(maxAbs(a.raw.slice(1), b.raw.slice(1)) < 1e-8);
  assert.ok(maxAbs(a.std, b.std) < 1e-8);
  assert.ok(maxAbs(a.beta, b.beta) < 1e-8);
  const scaled = ml.scaleColumns(IM.Xtr, { 0: 1000 });
  assert.deepEqual(scaled, metres);
  assert.deepEqual(ml.treeImportance(ml.fitTree(IM.Xtr, IM.ytr, {}), 5), ml.treeImportance(ml.fitTree(metres, IM.ytr, {}), 5));
});

test("a feature the model does not use has permutation importance exactly zero", () => {
  const t = ml.fitTree(IM.Xtr, IM.ytr, { maxDepth: 1 });
  const used = t.feature;
  const r = ml.permutationImportance(imAcc((x) => ml.treePredict(t, x)), IM.Xte, IM.yte, IM.perms);
  r.mean.forEach((v, j) => { if (j !== used) assert.equal(v, 0, `column ${j}`); });
  assert.ok(r.mean[used] > 0);
  assert.equal(ml.treeImportance(t, 5)[used], 1);
});

test("random permutations are permutations, and different between repeats", () => {
  const ps = ml.randomPerms(50, 8, ml.rng(3));
  assert.equal(ps.length, 8);
  ps.forEach((p) => assert.deepEqual([...p].sort((a, b) => a - b), Array.from({ length: 50 }, (_, i) => i)));
  assert.notDeepEqual(ps[0], ps[1]);
  // All 4! orders of four rows turn up about equally often: 12000 draws, 500 expected each.
  const seen = new Map();
  ml.randomPerms(4, 12000, ml.rng(8)).forEach((p) => seen.set(p.join(), (seen.get(p.join()) ?? 0) + 1));
  assert.equal(seen.size, 24);
  assert.ok(Math.min(...seen.values()) > 420 && Math.max(...seen.values()) < 580, [...seen.values()].join());
});

test("the importance table has the promised columns", () => {
  const t = ml.makeImportanceTable(800, 5, { corr: 0.9 });
  assert.deepEqual(t.names, ml.IMPORTANCE_NAMES);
  assert.equal(t.X.length, 800);
  const col = (j) => t.X.map((r) => r[j]);
  assert.equal(new Set(col(ml.IMPORTANCE_NAMES.indexOf("noise_num"))).size, 800, "noise_num has a value per row");
  assert.deepEqual([...new Set(col(ml.IMPORTANCE_NAMES.indexOf("noise_cat")))].sort(), [0, 1, 2]);
  assert.deepEqual([...new Set(col(ml.IMPORTANCE_NAMES.indexOf("flag")))].sort(), [0, 1]);
  const a = col(0), b = col(5), ma = a.reduce((s, v) => s + v, 0) / 800, mb = b.reduce((s, v) => s + v, 0) / 800;
  const corr = a.reduce((s, v, i) => s + (v - ma) * (b[i] - mb), 0) / 800 / (sdOf(a) * sdOf(b));
  assert.ok(Math.abs(corr - 0.9) < 0.03, `corr ${corr}`);
  const exact = ml.makeImportanceTable(800, 5, { corr: 1 });
  assert.deepEqual(exact.X.map((r) => r[5]), exact.X.map((r) => r[0]));
  // The other columns and the target do not depend on the copy.
  assert.deepEqual(exact.X.map((r) => r.slice(0, 5)), t.X.map((r) => r.slice(0, 5)));
  assert.deepEqual(exact.y, t.y);
  assert.ok(Math.abs(sdOf(col(0)) - 5) < 0.4 && Math.abs(col(0).reduce((s, v) => s + v, 0) / 800 - 20) < 0.5, "x1 is in km around 20");
});

test("tieShuffle lets an exact copy take splits from its original; without it the first column always wins", () => {
  const { X, y } = ml.makeImportanceTable(300, 2, { corr: 1 });
  const share = (shuffleFeatures) => {
    const f = ml.fitForest(X, y, { nTrees: 30, bootstrap: false, maxFeatures: null, shuffleFeatures, seed: 4 });
    return ml.forestImportance(f, 6);
  };
  const plain = share(false), mixed = share(true);
  assert.equal(plain[5], 0);
  assert.ok(plain[0] > 0.2);
  assert.ok(mixed[5] > 0.3 * mixed[0] && mixed[0] > 0.3 * mixed[5], `${mixed[0]} ${mixed[5]}`);
});

test("shuffleFeatures off keeps the old random stream: forests without it are unchanged", () => {
  const a = ml.fitForest(X, y, { nTrees: 5, maxFeatures: 1, seed: 5 });
  const b = ml.fitForest(X, y, { nTrees: 5, maxFeatures: 1, seed: 5, shuffleFeatures: false });
  assert.deepEqual(a.trees, b.trees);
});

// A forest on the table, scored the way the page does: importances by impurity (train), permutation and drop column (held-out).
function importanceRun(seed, { corr = null, minLeaf = 1, maxDepth = Infinity, nTrees = 25, cols = [0, 1, 2, 3, 4], K = 8 } = {}) {
  const t = ml.makeImportanceTable(600, seed, { corr: corr ?? 0 });
  const pick = (X) => X.map((r) => cols.map((j) => r[j]));
  const nTrain = 420;
  const Xtr = pick(t.X.slice(0, nTrain)), ytr = t.y.slice(0, nTrain), Xte = pick(t.X.slice(nTrain)), yte = t.y.slice(nTrain);
  const P = cols.length, mf = Math.max(1, Math.round(Math.sqrt(P)));
  const fit = (X, yy) => {
    const f = ml.fitForest(X, yy, { nTrees, minLeaf, maxDepth, maxFeatures: Math.min(mf, X[0].length), shuffleFeatures: true, seed: 50 + seed });
    return Object.assign((x) => { const q = ml.forestProba(f, x); return q[1] > q[0] ? 1 : 0; }, { f });
  };
  const model = fit(Xtr, ytr);
  const perms = ml.randomPerms(Xte.length, K, ml.rng(900 + seed));
  const perm = ml.permutationImportance(imAcc(model), Xte, yte, perms);
  const drop = ml.dropColumn((X, yy) => fit(X, yy), Xtr, ytr, Xte, yte);
  const named = (v) => Object.fromEntries(cols.map((j, i) => [ml.IMPORTANCE_NAMES[j], v[i]]));
  return { mdi: named(ml.forestImportance(model.f, P)), perm: named(perm.mean), drop: named(drop.importances), trainAcc: imAcc(model)(Xtr, ytr), testAcc: imAcc(model)(Xte, yte) };
}

test("a grown forest gives the many-valued noise more impurity than the three-valued one, and permutation on held-out data gives it about zero", () => {
  let more = 0, noisePerm = 0, noiseCatPerm = 0;
  const S = 12;
  for (let s = 1; s <= S; s++) {
    const r = importanceRun(s);
    assert.ok(r.trainAcc > 0.95 && r.trainAcc - r.testAcc > 0.1,`grown forest memorises the train part: ${r.trainAcc} against ${r.testAcc}`);
    if (r.mdi.noise_num > r.mdi.noise_cat) more++;
    noisePerm += Math.abs(r.perm.noise_num) / S;
    noiseCatPerm += Math.abs(r.perm.noise_cat) / S;
  }
  assert.ok(more >= S - 1, `noise_num beats noise_cat by impurity in ${more} of ${S} seeds`);
  assert.ok(noisePerm < 0.03, `mean |permutation of noise_num| ${noisePerm}`);
  assert.ok(noiseCatPerm < 0.03);
});

test("a larger minimum leaf shrinks the impurity of the many-valued noise", () => {
  const mean = (minLeaf) => { let s = 0; for (let k = 1; k <= 8; k++) s += importanceRun(k, { minLeaf, nTrees: 15 }).mdi.noise_num / 8; return s; };
  const m1 = mean(1), m20 = mean(20);
  assert.ok(m20 < 0.6 * m1, `leaf 1 ${m1}, leaf 20 ${m20}`);
});

test("an exact copy shares impurity with its original, lowers its permutation importance and zeroes its drop column", () => {
  let mdiSum = 0, mdiSumNoCopy = 0, mdiOrig = 0, mdiCopy = 0, permWith = 0, permWithout = 0, dropWith = 0, dropWithout = 0;
  const S = 8;
  for (let s = 1; s <= S; s++) {
    const a = importanceRun(s, { minLeaf: 5 });
    const b = importanceRun(s, { corr: 1, cols: [0, 1, 2, 3, 4, 5], minLeaf: 5 });
    mdiSumNoCopy += a.mdi.x1 / S; mdiSum += (b.mdi.x1 + b.mdi.x1_copy) / S;
    mdiOrig += b.mdi.x1 / S; mdiCopy += b.mdi.x1_copy / S;
    permWithout += a.perm.x1 / S; permWith += b.perm.x1 / S;
    dropWithout += a.drop.x1 / S; dropWith += b.drop.x1 / S;
  }
  assert.ok(Math.abs(Math.log(mdiOrig / mdiCopy)) < Math.log(1.6), `twins ${mdiOrig} ${mdiCopy}`);
  assert.ok(mdiOrig < 0.8 * mdiSumNoCopy, `x1 alone ${mdiSumNoCopy}, with copy ${mdiOrig}`);
  assert.ok(mdiSum > 0.8 * mdiSumNoCopy, `the pair keeps the impurity of the single column: ${mdiSum} vs ${mdiSumNoCopy}`);
  assert.ok(permWith < 0.6 * permWithout, `permutation ${permWithout} -> ${permWith}`);
  assert.ok(dropWithout > 0.03 && Math.abs(dropWith) < 0.5 * dropWithout, `drop ${dropWithout} -> ${dropWith}`);
});

// ---------- LIME ----------

const L = fx.lime;
const Zof = (E, x, s) => E.map((e) => e.map((v, j) => x[j] + s[j] * v));

test("LIME default width is 0.75 sqrt(p), as in lime_tabular.py", () => {
  for (const [p, w] of Object.entries(L.default_width)) assert.ok(Math.abs(ml.limeDefaultWidth(+p) - w) < 1e-12, `p=${p}`);
});

test("LIME kernel weights equal lime's, standardised distance and all, for four widths", () => {
  const Z = Zof(L.eps, L.x, L.scale);
  for (const f of L.fits) {
    const w = ml.limeWeights(Z, L.x, L.scale, f.width);
    assert.ok(maxAbs(w, f.weights) < 1e-12, `width ${f.width}`);
  }
});

test("LIME distances are taken after standardising: unequal scales change the weights", () => {
  const Z = Zof(L.eps, L.x, L.scale);
  const f = L.fits[1];
  const raw = ml.limeWeights(Z, L.x, [1, 1], f.width);
  assert.ok(maxAbs(raw, f.weights) > 0.05);
});

test("LIME weighted least squares equals lime_common.local_fit and sklearn LinearRegression with sample_weight", () => {
  const Z = Zof(L.eps, L.x, L.scale);
  for (const f of L.fits) {
    const g = ml.weightedLinearFit(Z, L.x, L.t, f.weights);
    assert.ok(maxAbs(g.coef, f.coef) < 1e-9, `coef width ${f.width}`);
    assert.ok(Math.abs(g.a - f.a) < 1e-9 && Math.abs(g.r2 - f.r2) < 1e-9, `a, r2 width ${f.width}`);
  }
});

test("LIME effective number of neighbours and the angle to the gradient equal the reference", () => {
  for (const f of L.fits) {
    assert.ok(Math.abs(ml.nEff(f.weights) - f.n_eff) < 1e-9);
    assert.ok(Math.abs(ml.angleDeg(f.coef, L.grad) - f.angle) < 1e-9);
  }
  assert.equal(ml.nEff([1, 1, 1, 1]), 4);
  assert.ok(Math.abs(ml.nEff([1, 0, 0, 0]) - 1) < 1e-12);
});

test("LIME weighted fit recovers a linear function exactly and reports R^2 = 1", () => {
  const Z = Zof(L.eps, L.x, L.scale);
  const t = Z.map((z) => 0.7 - 2 * (z[0] - L.x[0]) + 3 * (z[1] - L.x[1]));
  const g = ml.weightedLinearFit(Z, L.x, t, ml.limeWeights(Z, L.x, L.scale, 0.5));
  assert.ok(Math.abs(g.a - 0.7) < 1e-9 && Math.abs(g.coef[0] + 2) < 1e-9 && Math.abs(g.coef[1] - 3) < 1e-9);
  assert.ok(Math.abs(g.r2 - 1) < 1e-9);
});

test("LIME weighted fit refuses a cloud with fewer than p + 1 points of weight", () => {
  assert.equal(ml.weightedLinearFit([[0, 0], [1, 1]], [0, 0], [0, 1], [1, 1]), null);
});

test("LIME perturbations are x + scale * eps, standard normal eps, and fixed by the seed", () => {
  const a = ml.limeSample([1, 2], [0.5, 2], 6000, 7), b = ml.limeSample([1, 2], [0.5, 2], 6000, 7), c = ml.limeSample([1, 2], [0.5, 2], 6000, 8);
  assert.deepEqual(a.Z, b.Z);
  assert.notDeepEqual(a.Z, c.Z);
  a.Z.forEach((z, i) => { assert.ok(Math.abs(z[0] - (1 + 0.5 * a.E[i][0])) < 1e-12 && Math.abs(z[1] - (2 + 2 * a.E[i][1])) < 1e-12); });
  for (const j of [0, 1]) {
    const m = a.E.reduce((s, e) => s + e[j], 0) / a.E.length, v = a.E.reduce((s, e) => s + (e[j] - m) ** 2, 0) / a.E.length;
    assert.ok(Math.abs(m) < 0.05 && Math.abs(v - 1) < 0.06, `column ${j}: mean ${m}, variance ${v}`);
  }
});

test("LIME gradient by central difference is exact for a quadratic and uses the given step", () => {
  const f = (x) => x[0] ** 2 + 3 * x[0] * x[1] - x[1];
  const g = ml.gradientFd(f, [0.4, -0.7], 0.1);
  assert.ok(Math.abs(g[0] - (2 * 0.4 + 3 * -0.7)) < 1e-12 && Math.abs(g[1] - (3 * 0.4 - 1)) < 1e-12);
  const step = (x) => (x[0] > 0 ? 1 : 0);
  // a jump of 1 across the step 2h is read as slope 1 / (2h): a piecewise-constant f has no gradient of its own, only one at a scale
  assert.ok(Math.abs(ml.gradientFd(step, [0, 0], 0.5)[0] - 1) < 1e-12);
  assert.ok(Math.abs(ml.gradientFd(step, [0, 0], 1e-3)[0] - 500) < 1e-9);
});

test("LIME line g = level inside a box equals lime_common.boundary_segment", () => {
  for (const s of L.segments) {
    const got = ml.segmentInBox(s.a, s.c, L.x, L.box, s.level);
    assert.ok(maxAbs(got.xs, s.xs) < 1e-12 && maxAbs(got.ys, s.ys) < 1e-12);
  }
});

// ---------- SHAP ----------

const SH = fx.shap;
const phiClose = (a, b, tol = 1e-12) => a.length === b.length && maxAbs(a, b) < tol;

test("Shapley values by coalitions equal shapley_lib for 3, 4 and 5 players", () => {
  for (const g of SH.games) assert.ok(phiClose(ml.shapleyFromValues(g.v, g.m), g.phi), `m=${g.m}`);
});

test("Shapley values by all orders equal shapley_lib, order by order, and the same as by coalitions", () => {
  for (const g of SH.games) {
    const r = ml.shapleyOrders(g.v, g.m);
    assert.ok(phiClose(r.phi, g.phi_orders), `m=${g.m}`);
    assert.ok(phiClose(r.phi, ml.shapleyFromValues(g.v, g.m)), `two formulas, m=${g.m}`);
  }
  const r = ml.shapleyOrders(SH.games[1].v, 4);
  assert.equal(r.orders.length, 24);
  r.orders.forEach((o, k) => {
    assert.deepEqual(o, SH.orders4[k].order);
    assert.ok(phiClose(r.inc[k], SH.orders4[k].inc), `increments of order ${k}`);
  });
});

test("Shapley weights |S|!(m-|S|-1)!/m! give 1/3, 1/6, 1/3 for three players and sum to 1 over coalitions", () => {
  const w = ml.shapleyWeights(3);
  assert.ok(phiClose(w, [1 / 3, 1 / 6, 1 / 3]));
  for (const m of [3, 4, 5]) {
    const wm = ml.shapleyWeights(m);
    const binom = (n, k) => (k === 0 ? 1 : (binom(n, k - 1) * (n - k + 1)) / k);
    assert.equal(wm.length, m);
    assert.ok(Math.abs(wm.reduce((s, v, size) => s + v * binom(m - 1, size), 0) - 1) < 1e-12);
  }
});

test("the game f = 3 x1 + x2 x3 of the note: v(S) table and phi = (1.5; 0.375; 0.375; 0)", () => {
  const f = (z) => 3 * z[0] + z[1] * z[2];
  const coins = Array.from({ length: 16 }, (_, k) => [0, 1, 2, 3].map((j) => (k >> j) & 1));
  const v = ml.interventionalValues(f, [1, 1, 1, 0], coins);
  // order of the note's table: {}, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3}; feature 4 is a null player
  const note = [[0, 1.75], [1, 3.25], [2, 2.0], [4, 2.0], [3, 3.5], [5, 3.5], [6, 2.5], [7, 4.0]];
  for (const [mask, val] of note) { assert.ok(Math.abs(v[mask] - val) < 1e-12, `v(${mask})`); assert.ok(Math.abs(v[mask | 8] - val) < 1e-12, `null player at ${mask}`); }
  assert.ok(phiClose(ml.shapleyFromValues(v, 4), [1.5, 0.375, 0.375, 0]));
  assert.ok(phiClose(v, SH.toy.v) && phiClose(ml.shapleyFromValues(v, 4), SH.toy.phi));
});

test("interventional v(S) of a fitted boosting equals shapley_lib.interventional_values", () => {
  const g = SH.gbr, model = { f0: g.f0, lr: g.lr, trees: g.trees };
  const predict = (x) => ml.boostingPredict(model, x);
  g.X.forEach((x, j) => {
    const v = ml.interventionalValues(predict, x, g.background);
    assert.ok(phiClose(v, g.v_int[j], 1e-9), `object ${j}`);
    assert.ok(Math.abs(v[15] - g.pred[j]) < 1e-9, "v(N) is the prediction");
    assert.ok(phiClose(ml.shapleyFromValues(v, 4), g.phi_int[j], 1e-9), `phi, object ${j}`);
  });
});

test("tree-rule v(S) (slide 27, path-dependent) of a fitted boosting equals shapley_lib.gbr_coalition_values", () => {
  const g = SH.gbr, model = { f0: g.f0, lr: g.lr, trees: g.trees };
  g.X.forEach((x, j) => {
    const v = ml.treeCoalitionValues(model, x);
    assert.ok(phiClose(v, g.v_path[j], 1e-9), `object ${j}`);
    assert.ok(phiClose(ml.shapleyFromValues(v, 4), g.phi_path[j], 1e-9), `phi, object ${j}`);
  });
});

test("on correlated features the two v(S) rules disagree, and efficiency holds for both", () => {
  const g = SH.gbr, model = { f0: g.f0, lr: g.lr, trees: g.trees };
  let gap = 0;
  g.X.forEach((x, j) => {
    const vi = ml.interventionalValues((z) => ml.boostingPredict(model, z), x, g.background), vp = ml.treeCoalitionValues(model, x);
    for (const v of [vi, vp]) {
      const phi = ml.shapleyFromValues(v, 4);
      assert.ok(Math.abs(phi.reduce((s, a) => s + a, 0) - (v[15] - v[0])) < 1e-9);
    }
    gap = Math.max(gap, maxAbs(ml.shapleyFromValues(vi, 4), ml.shapleyFromValues(vp, 4)));
  });
  assert.ok(gap > 0.05, `largest gap ${gap}`);
});

test("shap data: fixed by the seed, features 1 and 2 correlated by rho, the others independent", () => {
  const a = ml.makeShapData(5000, 3, { rho: 0.9 }), b = ml.makeShapData(5000, 3, { rho: 0.9 });
  assert.deepEqual(a.X, b.X);
  const corr = (j, k) => {
    const m = (c) => a.X.reduce((s, r) => s + r[c], 0) / a.X.length;
    const mj = m(j), mk = m(k);
    let sj = 0, sk = 0, sjk = 0;
    for (const r of a.X) { sj += (r[j] - mj) ** 2; sk += (r[k] - mk) ** 2; sjk += (r[j] - mj) * (r[k] - mk); }
    return sjk / Math.sqrt(sj * sk);
  };
  assert.ok(Math.abs(corr(0, 1) - 0.9) < 0.02, `corr12 ${corr(0, 1)}`);
  for (const [j, k] of [[0, 2], [0, 3], [1, 2], [2, 3]]) assert.ok(Math.abs(corr(j, k)) < 0.05, `corr ${j}${k}`);
  assert.equal(a.y.length, 5000);
  assert.equal(ml.SHAP_TRUTH([1, 2, 3, 4]), 2 * 1 + 2 + 3 * 4);
  const res = a.y.map((v, i) => v - ml.SHAP_TRUTH(a.X[i])), m = res.reduce((s, v) => s + v, 0) / res.length;
  const sd = Math.sqrt(res.reduce((s, v) => s + (v - m) ** 2, 0) / res.length);
  assert.ok(Math.abs(m) < 0.02 && Math.abs(sd - ml.SHAP_NOISE) < 0.02, `noise mean ${m}, sd ${sd}`);
});

// ---------- softmax with temperature ----------
// The ten logits and the reference softmax and entropy come from figures/08/softmax_common.py; the reference
// gradient of the cross-entropy is a central difference of C(z), so it shares no formula with the code.

const SM = fx.softmax;

test("softmax with temperature equals softmax_common.softmax at every temperature, to 1e-12", () => {
  SM.temps.forEach((t, k) => {
    const q = ml.softmaxT(SM.z, t);
    assert.ok(maxAbs(q, SM.q[k]) < 1e-12, `T=${t}: ${maxAbs(q, SM.q[k])}`);
    assert.ok(Math.abs(q.reduce((s, v) => s + v, 0) - 1) < 1e-14);
  });
});

test("entropy equals softmax_common.entropy at every temperature, to 1e-12", () => {
  SM.temps.forEach((t, k) => {
    assert.ok(Math.abs(ml.entropy(ml.softmaxT(SM.z, t)) - SM.entropy[k]) < 1e-12, `T=${t}`);
  });
});

test("entropy treats 0 ln 0 as 0 and is ln N for the uniform distribution and 0 for one-hot", () => {
  assert.equal(ml.entropy([1, 0, 0, 0]), 0);
  assert.ok(Math.abs(ml.entropy([0.25, 0.25, 0.25, 0.25]) - Math.log(4)) < 1e-15);
  assert.ok(Math.abs(ml.entropy([0.5, 0.5, 0, 0]) - Math.LN2) < 1e-15);
});

test("softmax: shifting all logits changes nothing, extreme temperatures give one-hot and uniform without NaN", () => {
  const z = [3, -1, 0.5];
  assert.ok(maxAbs(ml.softmaxT(z, 2), ml.softmaxT(z.map((v) => v + 1000), 2)) < 1e-12);
  assert.deepEqual(ml.softmaxT(z, 1e-4), [1, 0, 0]);
  assert.ok(maxAbs(ml.softmaxT(z, 1e9), [1 / 3, 1 / 3, 1 / 3]) < 1e-8);
  assert.ok(ml.softmaxT(SM.z, 1e-3).every(Number.isFinite));
});

test("cross-entropy gradient (q - p) / T equals the central difference of C(z) for hard and soft labels, to 1e-8", () => {
  for (const [name, p] of Object.entries(SM.labels)) {
    for (const [t, want] of Object.entries(SM.grad[name])) {
      const g = ml.softmaxCeGrad(SM.z, p, +t);
      assert.ok(maxAbs(g, want) < 1e-8, `${name} T=${t}: ${maxAbs(g, want)}`);
      assert.ok(Math.abs(g.reduce((s, v) => s + v, 0)) < 1e-14, "gradient over logits sums to zero");
    }
  }
});

test("dH/dT equals Var_q(z) / T^3 (central difference in T), to 1e-6 relative", () => {
  const H = (t) => ml.entropy(ml.softmaxT(SM.z, t));
  for (const t of [0.3, 0.7, 1, 2, 5, 12, 40]) {
    const h = 1e-5 * t;
    const q = ml.softmaxT(SM.z, t);
    const mean = q.reduce((s, qi, i) => s + qi * SM.z[i], 0);
    const varq = q.reduce((s, qi, i) => s + qi * (SM.z[i] - mean) ** 2, 0);
    const want = varq / t ** 3, got = (H(t + h) - H(t - h)) / (2 * h);
    assert.ok(Math.abs(got - want) <= 1e-6 * want, `T=${t}: ${got} vs ${want}`);
  }
});

test("the soft-label gradient scaled by T^2 tends to (z - v) / N with logits centred, as T grows", () => {
  const v = SM.z.map((_, i) => Math.cos(i) * 2);
  const centre = (a) => a.map((x) => x - a.reduce((s, y) => s + y, 0) / a.length);
  for (const t of [1e3, 1e4]) {
    const p = ml.softmaxT(v, t);
    const g = ml.softmaxCeGrad(SM.z, p, t).map((x) => x * t * t);
    const want = centre(SM.z).map((x, i) => (x - centre(v)[i]) / SM.z.length);
    assert.ok(maxAbs(g, want) < 20 / t, `T=${t}: ${maxAbs(g, want)}`);
  }
});

// ---------- distillation ----------
// The teacher is a gradient-boosting classifier, the student a one-logit network; distill_common.py is the
// reference, see export_fixtures.distill_fixtures for why a one-logit network has the loss of a two-logit one.

const DS = fx.distill;
const sigm = (x) => 1 / (1 + Math.exp(-x));
const distillNet = (c) => ({ act: "tanh", W: [c.W0, [c.v]], b: [c.b0, [c.c]] });

test("boosting classifier equals sklearn GradientBoostingClassifier: start, every stage, final decision, to 1e-9", () => {
  for (const c of DS.gbc) {
    const m = ml.fitBoostingClf(c.X, c.y, { nEstimators: c.n, lr: c.lr, maxDepth: c.depth });
    assert.ok(Math.abs(m.f0 - c.init) < 1e-12, `${c.ds} init`);
    const train = c.X.map((x) => ml.boostingClfDecision(m, x));
    assert.ok(maxAbs(train, c.train) < 1e-9, `${c.ds} n=${c.n} depth=${c.depth}: train ${maxAbs(train, c.train)}`);
    const grid = c.grid.map((x) => ml.boostingClfDecision(m, x));
    if (c.grid_spread === 0) assert.ok(maxAbs(grid, c.decision) < 1e-9, `${c.ds} n=${c.n}: grid ${maxAbs(grid, c.decision)}`);
    else {
      // sklearn itself changes the grid answer with random_state (tied splits, same fit on the train points),
      // so the grid is compared by sign and by the share of points that moved, not exactly.
      const moved = grid.filter((v, i) => Math.abs(v - c.decision[i]) > 1e-9).length / grid.length;
      const sign = grid.filter((v, i) => v > 0 === c.decision[i] > 0).length / grid.length;
      assert.ok(moved < 0.3 && sign > 0.95, `${c.ds} n=${c.n}: moved ${moved}, same sign ${sign}`);
    }
    c.staged_train.forEach((want, k) => {
      const got = c.X.map((x) => ml.boostingClfDecision(m, x, k + 1));
      assert.ok(maxAbs(got, want) < 1e-9, `${c.ds} stage ${k + 1}: ${maxAbs(got, want)}`);
    });
  }
});

test("boosting classifier: zero trees give the log-odds of the class share, and training accuracy beats it", () => {
  const c = DS.gbc.find((g) => g.ds === "moons-skew");
  const m = ml.fitBoostingClf(c.X, c.y, { nEstimators: 30, lr: 0.3, maxDepth: 2 });
  assert.ok(Math.abs(c.init) > 0.5, "the set must be skewed, or the start tells nothing");
  const share = c.y.reduce((s, v) => s + v, 0) / c.y.length;
  assert.ok(Math.abs(ml.boostingClfDecision(m, c.X[0], 0) - Math.log(share / (1 - share))) < 1e-12);
  const acc = (k) => ml.accuracy(c.X.map((x) => (ml.boostingClfDecision(m, x, k) > 0 ? 1 : 0)), c.y);
  assert.ok(acc(30) > acc(0) + 0.2, `${acc(0)} -> ${acc(30)}`);
});

test("Newton step of a leaf is sum(y - p) / sum(p (1 - p)) and 0 where the Hessian vanishes (sigma saturates past |F| about 37, so 0/0)", () => {
  assert.equal(ml.newtonStep(3, 2), 1.5);
  assert.equal(ml.newtonStep(-1, 4), -0.25);
  assert.equal(ml.newtonStep(0, 0), 0);
  assert.equal(ml.newtonStep(1e-20, 1e-200), 0);
});

test("boosting classifier on separable data with a big step and many trees stays finite and classifies the train part", () => {
  const c = fx.mlp.splits.circles;
  const m = ml.fitBoostingClf(c.Xtr, c.ytr, { nEstimators: 300, lr: 1, maxDepth: 3 });
  const F = c.Xtr.map((x) => ml.boostingClfDecision(m, x));
  assert.ok(F.every(Number.isFinite));
  assert.ok(Math.max(...F.map(Math.abs)) > 40, "the decision values must pass the saturation of sigma");
  assert.equal(ml.accuracy(F.map((v) => (v > 0 ? 1 : 0)), c.ytr), 1);
});

test("Hinton loss and its gradient equal distill_common.loss_and_grads on the same network, to 1e-12", () => {
  for (const c of DS.loss) {
    const net = distillNet(c), opts = { T: c.T, lam: c.lam };
    const loss = ml.mlpDistillLoss(net, c.X, c.y, c.u, opts);
    assert.ok(Math.abs(loss - c.loss) < 1e-12 * Math.max(1, c.loss), `T=${c.T} lam=${c.lam}: ${loss} vs ${c.loss}`);
    const g = ml.mlpGrad(net, c.X, c.y, ml.distillDelta(c.u, c.y, opts));
    const tag = `T=${c.T} lam=${c.lam} hidden=${c.hidden}`;
    assert.ok(maxAbs(g.W[0].flat(), c.gW0.flat()) < 1e-12, `${tag} hidden weights`);
    assert.ok(maxAbs(g.b[0], c.gb0) < 1e-12, `${tag} hidden biases`);
    assert.ok(maxAbs(g.W[1][0], c.gv) < 1e-12, `${tag} output weights`);
    assert.ok(Math.abs(g.b[1][0] - c.gc) < 1e-12, `${tag} output bias`);
  }
});

test("Hinton gradient equals central finite differences of the loss for every parameter", () => {
  for (const c of DS.loss) {
    const net = distillNet(c), opts = { T: c.T, lam: c.lam };
    const g = ml.mlpGrad(net, c.X, c.y, ml.distillDelta(c.u, c.y, opts));
    const h = 1e-6;
    let worst = 0;
    const probe = (get, set, analytic) => {
      const v = get();
      set(v + h); const up = ml.mlpDistillLoss(net, c.X, c.y, c.u, opts);
      set(v - h); const down = ml.mlpDistillLoss(net, c.X, c.y, c.u, opts);
      set(v);
      worst = Math.max(worst, Math.abs((up - down) / (2 * h) - analytic));
    };
    net.W.forEach((M, k) => M.forEach((row, j) => row.forEach((_, i) => probe(() => net.W[k][j][i], (x) => { net.W[k][j][i] = x; }, g.W[k][j][i]))));
    net.b.forEach((bk, k) => bk.forEach((_, j) => probe(() => net.b[k][j], (x) => { net.b[k][j] = x; }, g.b[k][j])));
    assert.ok(worst < 1e-7, `T=${c.T} lam=${c.lam}: worst ${worst}`);
  }
});

test("lam = 1 ignores the teacher and lam = 0 ignores the true label; lam = 1 at any T is the plain log loss", () => {
  const d = 0.7, y = 1;
  const hard = (t) => ml.distillTerms(d, 5, y, t, 1);
  assert.deepEqual(hard(1), hard(9));
  assert.deepEqual(ml.distillTerms(d, 5, y, 3, 1), ml.distillTerms(d, -4, y, 3, 1));
  assert.deepEqual(ml.distillTerms(d, 2, 0, 3, 0), ml.distillTerms(d, 2, 1, 3, 0));
  assert.ok(Math.abs(hard(2).loss - Math.log1p(Math.exp(-d))) < 1e-15);
  assert.ok(Math.abs(hard(2).delta - (sigm(d) - 1)) < 1e-15);
});

test("soft gradient times T^2 tends to (d - u) / 4 for two classes as T grows, and stays bounded in T", () => {
  for (const [d, u] of [[1.5, -0.5], [-3, 2], [0.2, 0.2]]) {
    for (const t of [1e3, 1e4]) {
      const got = ml.distillTerms(d, u, 0, t, 0).delta;
      assert.ok(Math.abs(got - (d - u) / 4) < 1e-5, `d=${d} u=${u} T=${t}: ${got} vs ${(d - u) / 4}`);
    }
    // sigma' <= 1/4, so by the mean value theorem T |sigma(d/T) - sigma(u/T)| <= |d - u| / 4 at every T.
    for (const t of [0.5, 1, 2, 4, 8, 16, 32]) assert.ok(Math.abs(ml.distillTerms(d, u, 0, t, 0).delta) <= Math.abs(d - u) / 4 + 1e-12, `T=${t}`);
  }
});

test("a gradient step along the Hinton gradient lowers the loss", () => {
  const c = DS.loss[2], opts = { T: c.T, lam: c.lam };
  const net = distillNet(c);
  const before = ml.mlpDistillLoss(net, c.X, c.y, c.u, opts);
  const next = ml.mlpStep(net, c.X, c.y, 0.05, ml.distillDelta(c.u, c.y, opts));
  assert.ok(ml.mlpDistillLoss(next, c.X, c.y, c.u, opts) < before);
});
