// Small ML core for the course's interactive pages. Each model follows the
// sklearn algorithm the static figures use, and mlcore.test.mjs checks the
// answers against sklearn. Plain ES module: pages inline it, node imports it.

// ---------- data ----------

export function rng(seed) {
  // mulberry32: small, fast, seeded; enough for demo data, not for science.
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function gauss(r) {
  const u = Math.max(r(), 1e-12);
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r());
}

export function makeMoons(n, noise, seed) {
  const r = rng(seed);
  const half = Math.floor(n / 2);
  const X = [];
  const y = [];
  for (let i = 0; i < n; i++) {
    const outer = i < n - half;
    const m = outer ? n - half : half;
    const j = outer ? i : i - (n - half);
    const t = (Math.PI * j) / Math.max(m - 1, 1);
    const p = outer ? [Math.cos(t), Math.sin(t)] : [1 - Math.cos(t), 0.5 - Math.sin(t)];
    X.push([p[0] + noise * gauss(r), p[1] + noise * gauss(r)]);
    y.push(outer ? 0 : 1);
  }
  return { X, y };
}

export function accuracy(pred, y) {
  let ok = 0;
  for (let i = 0; i < y.length; i++) if (pred[i] === y[i]) ok++;
  return ok / y.length;
}

// ---------- kNN ----------

export function fitKnn(X, y, { k }) {
  const classes = [...new Set(y)].sort((a, b) => a - b);
  return { X, y, k, classes };
}

export function knnProba(m, x) {
  const d = m.X.map((p, i) => [(p[0] - x[0]) ** 2 + (p[1] - x[1]) ** 2, i]);
  d.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const counts = new Array(m.classes.length).fill(0);
  for (let i = 0; i < m.k; i++) counts[m.classes.indexOf(m.y[d[i][1]])]++;
  return counts.map((c) => c / m.k);
}

// ---------- Gaussian naive Bayes ----------

export function fitGnb(X, y, { priors = null, varSmoothing = 1e-9 } = {}) {
  // As sklearn GaussianNB: per class and feature the mean and the population
  // variance, plus varSmoothing times the largest feature variance of the
  // whole sample; the prior is the class frequency unless given.
  const classes = [...new Set(y)].sort((a, b) => a - b);
  const p = X[0].length;
  const eps = varSmoothing * Math.max(...Array.from({ length: p }, (_, j) => {
    const mu = X.reduce((s, x) => s + x[j], 0) / X.length;
    return X.reduce((s, x) => s + (x[j] - mu) ** 2, 0) / X.length;
  }));
  const theta = [], variance = [], prior = [];
  for (const c of classes) {
    const rows = X.filter((_, i) => y[i] === c);
    const mu = Array.from({ length: p }, (_, j) => rows.reduce((s, x) => s + x[j], 0) / rows.length);
    theta.push(mu);
    variance.push(mu.map((m, j) => rows.reduce((s, x) => s + (x[j] - m) ** 2, 0) / rows.length + eps));
    prior.push(rows.length / X.length);
  }
  return { classes, theta, var: variance, prior: priors ? priors.slice() : prior };
}

export function gnbParts(m, x) {
  // log P(C_k) and log P(x_l | C_k) for every class and feature: the terms
  // whose sum is the log of the numerator of Bayes' formula.
  return {
    logPrior: m.prior.map(Math.log),
    feat: m.theta.map((mu, k) => mu.map((t, l) =>
      -0.5 * Math.log(2 * Math.PI * m.var[k][l]) - ((x[l] - t) ** 2) / (2 * m.var[k][l]))),
  };
}

export function gnbLogJoint(m, x) {
  const { logPrior, feat } = gnbParts(m, x);
  return logPrior.map((lp, k) => lp + feat[k].reduce((s, v) => s + v, 0));
}

export function gnbProba(m, x) {
  const j = gnbLogJoint(m, x);
  const top = Math.max(...j);
  const e = j.map((v) => Math.exp(v - top));
  const z = e.reduce((s, v) => s + v, 0);
  return e.map((v) => v / z);
}

// ---------- CART decision tree, Gini ----------

function gini(counts, n) {
  let s = 1;
  for (const c of counts) s -= (c / n) ** 2;
  return s;
}

export function fitTree(X, y, { maxDepth = Infinity, minLeaf = 1, maxFeatures = null, rnd = null, nClasses = null, weights = null, shuffleFeatures = false } = {}) {
  // maxFeatures with a generator rnd: every node looks for its split among a
  // random subset of that many features (more only if none of them splits),
  // the random-forest rule. Without them every feature is scanned in order.
  // shuffleFeatures with rnd: every node scans the features in a random order,
  // so two features with the same gain (an exact copy) win by chance, as in
  // sklearn, not always the first one. Off by default: it draws from rnd.
  // weights: one sample weight per object, as sklearn's sample_weight. Class
  // counts become weight sums, so counts and n of a node are weighted too;
  // minLeaf still counts objects.
  const wt = (i) => (weights ? weights[i] : 1);
  const K = nClasses ?? Math.max(...y) + 1;
  const P = X[0].length;
  const subset = () => {
    const all = Array.from({ length: P }, (_, f) => f);
    const limited = maxFeatures && maxFeatures < P;
    if (!rnd || !(limited || shuffleFeatures)) return all;
    for (let i = P - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [all[i], all[j]] = [all[j], all[i]]; }
    return all;
  };
  const build = (idx, depth) => {
    const counts = new Array(K).fill(0);
    for (const i of idx) counts[y[i]] += wt(i);
    const total = counts.reduce((s, c) => s + c, 0);
    const node = { counts, n: total, impurity: gini(counts, total) };
    if (depth >= maxDepth || idx.length < 2 * minLeaf || node.impurity <= 1e-12) return node;
    let best = null;
    let visited = 0;
    for (const f of subset()) {
      if (best && maxFeatures && rnd && visited >= maxFeatures) break;
      visited++;
      const order = [...idx].sort((a, b) => X[a][f] - X[b][f]);
      const left = new Array(K).fill(0);
      const right = counts.slice();
      let wl = 0;
      for (let s = 0; s < order.length - 1; s++) {
        left[y[order[s]]] += wt(order[s]);
        right[y[order[s]]] -= wt(order[s]);
        wl += wt(order[s]);
        const a = X[order[s]][f];
        const b = X[order[s + 1]][f];
        const nl = s + 1;
        const nr = order.length - nl;
        if (a === b || nl < minLeaf || nr < minLeaf) continue;
        const wr = total - wl;
        const child = (wl * gini(left, wl) + wr * gini(right, wr)) / total;
        if (!best || child < best.child - 1e-15) {
          let thr = (a + b) / 2;
          if (thr === b) thr = a;
          best = { child, f, thr };
        }
      }
    }
    if (!best) return node;
    node.feature = best.f;
    node.threshold = best.thr;
    const L = idx.filter((i) => X[i][best.f] <= best.thr);
    const R = idx.filter((i) => X[i][best.f] > best.thr);
    node.left = build(L, depth + 1);
    node.right = build(R, depth + 1);
    return node;
  };
  return build(X.map((_, i) => i), 0);
}

export function treeLeaf(t, x) {
  while (t.left) t = x[t.feature] <= t.threshold ? t.left : t.right;
  return t;
}

export function treePredict(t, x) {
  const c = treeLeaf(t, x).counts;
  return c.indexOf(Math.max(...c));
}

export function treeProba(t, x) {
  const l = treeLeaf(t, x);
  return l.counts.map((c) => c / l.n);
}

// ---------- bagging and random forest ----------

export function bootstrapIdx(m, r) {
  // m draws with replacement from 0..m-1, r a generator from rng().
  return Array.from({ length: m }, () => Math.floor(r() * m));
}

export function fitForest(X, y, { nTrees = 100, maxFeatures = null, maxDepth = Infinity, minLeaf = 1, bootstrap = true, seed = 1, shuffleFeatures = false } = {}) {
  // Bagged classification trees; maxFeatures adds the random subspace rule at
  // every node. inbag[t][i] counts how often tree t saw object i (0 = out of bag).
  const r = rng(seed), m = X.length, K = Math.max(...y) + 1;
  const trees = [], inbag = [];
  for (let t = 0; t < nTrees; t++) {
    const idx = bootstrap ? bootstrapIdx(m, r) : Array.from({ length: m }, (_, i) => i);
    const counts = new Array(m).fill(0);
    idx.forEach((i) => counts[i]++);
    trees.push(fitTree(idx.map((i) => X[i]), idx.map((i) => y[i]), { maxDepth, minLeaf, maxFeatures, rnd: r, nClasses: K, shuffleFeatures }));
    inbag.push(counts);
  }
  return { X, y, K, trees, inbag };
}

// ---------- feature importance: impurity, permutation, drop column ----------

export function treeImportance(t, P) {
  // Mean decrease of impurity, as sklearn's feature_importances_: for every
  // split n_t H_t - n_L H_L - n_R H_R summed per feature, then divided by the
  // sum so the shares give 1. A tree without a split has all zeros.
  const raw = new Array(P).fill(0);
  const walk = (n) => {
    if (!n.left) return;
    raw[n.feature] += n.n * n.impurity - n.left.n * n.left.impurity - n.right.n * n.right.impurity;
    walk(n.left);
    walk(n.right);
  };
  walk(t);
  const total = raw.reduce((s, v) => s + v, 0);
  return total > 0 ? raw.map((v) => v / total) : raw;
}

export function forestImportance(m, P) {
  // Sum of the trees' importances divided by its sum: sklearn's
  // BaseForest.feature_importances_ is the mean over the trees with a split,
  // divided by its sum, and the count cancels. A tree without a split adds zeros.
  const sum = new Array(P).fill(0);
  for (const t of m.trees) treeImportance(t, P).forEach((v, j) => (sum[j] += v));
  const total = sum.reduce((s, v) => s + v, 0);
  return total > 0 ? sum.map((v) => v / total) : new Array(P).fill(0);
}

export function randomPerms(n, K, rnd) {
  // K independent uniform permutations of 0..n-1 (Fisher-Yates).
  return Array.from({ length: K }, () => {
    const p = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
    return p;
  });
}

export function permutationImportance(score, X, y, perms) {
  // score(X, y) is the quality of a fixed fitted model on a table. For each
  // column and each perm of perms the column is rearranged as sklearn does it:
  // new[i] = current[perm[i]], where current is the column as the previous
  // repeat left it, and the rows are scored again. importances[j][k] is the
  // base score minus the score after repeat k; std is over repeats (ddof 0).
  const base = score(X, y);
  const P = X[0].length;
  const importances = [];
  for (let j = 0; j < P; j++) {
    const Z = X.map((r) => r.slice());
    importances.push(perms.map((perm) => {
      const col = Z.map((r) => r[j]);
      perm.forEach((src, i) => { Z[i][j] = col[src]; });
      return base - score(Z, y);
    }));
  }
  const mean = importances.map((r) => r.reduce((s, v) => s + v, 0) / r.length);
  const std = importances.map((r, j) => Math.sqrt(r.reduce((s, v) => s + (v - mean[j]) ** 2, 0) / r.length));
  return { base, importances, mean, std };
}

export function dropColumn(fit, Xtr, ytr, Xte, yte) {
  // fit(X, y) returns predict(x) -> label. The importance of column j is the
  // held-out accuracy of the model fitted on all columns minus that of the
  // model refitted without j. With one column there is nothing to refit: NaN.
  const P = Xtr[0].length;
  const base = accuracy(Xte.map(fit(Xtr, ytr)), yte);
  const without = (X, j) => X.map((r) => r.filter((_, k) => k !== j));
  const importances = Array.from({ length: P }, (_, j) => (P < 2 ? NaN : base - accuracy(without(Xte, j).map(fit(without(Xtr, j), ytr)), yte)));
  return { base, importances };
}

export function logregWeights(m, X) {
  // Weights of a degree-1 logistic regression read three ways. raw: in the
  // units of each feature (the logit moves by raw_j per unit of x_j). std: for
  // features scaled to unit std, so std_j = raw_j * std(x_j). beta: std_j over
  // the std of the logit on X, the analogue of w std(x) / std(y) when the
  // target is a probability with no scale of its own.
  if (m.degree !== 1) throw new Error("logregWeights needs degree 1");
  const std = m.theta.slice(1);
  const raw = std.map((v, j) => v / m.std[j]);
  const z = X.map((x) => logregDecision(m, x));
  const mu = z.reduce((s, v) => s + v, 0) / z.length;
  const sd = Math.sqrt(z.reduce((s, v) => s + (v - mu) ** 2, 0) / z.length);
  return { raw, std, beta: std.map((v) => v / sd) };
}

export function scaleColumns(X, factors) {
  // Copy of X with column j multiplied by factors[j]: a change of unit.
  return X.map((r) => r.map((v, j) => v * (factors[j] ?? 1)));
}

export const IMPORTANCE_NAMES = ["x1", "x2", "flag", "noise_num", "noise_cat", "x1_copy"];

export function makeImportanceTable(n, seed, { corr = 0 } = {}) {
  // Binary target from two continuous signals (x1 in km, x2) and a binary
  // flag, as figures/07/imp_common.py; noise_num has a distinct value in every
  // row, noise_cat three values; x1_copy has correlation corr with x1 (1 is an
  // exact copy). Every draw comes in a fixed order, so the other columns and
  // the target are the same for every corr.
  const r = rng(seed);
  const X = [], y = [];
  for (let i = 0; i < n; i++) {
    const z1 = gauss(r), z2 = gauss(r), flag = r() < 0.5 ? 0 : 1, eps = 0.9 * gauss(r);
    const noiseNum = gauss(r), noiseCat = Math.floor(r() * 3), zc = gauss(r);
    y.push(z1 + 0.6 * z2 + 1.6 * (flag - 0.5) + eps > 0 ? 1 : 0);
    X.push([20 + 5 * z1, z2, flag, noiseNum, noiseCat, 20 + 5 * (corr * z1 + Math.sqrt(1 - corr * corr) * zc)]);
  }
  return { names: IMPORTANCE_NAMES, X, y };
}

export function forestProba(m, x, n = m.trees.length) {
  // Mean of the class shares of the first n trees.
  const p = new Array(m.K).fill(0);
  for (let t = 0; t < n; t++) treeProba(m.trees[t], x).forEach((v, k) => (p[k] += v / n));
  return p;
}

export function oobProba(m, i, n = m.trees.length) {
  // Mean over those of the first n trees that did not see object i; null if every one did.
  const p = new Array(m.K).fill(0);
  let cnt = 0;
  for (let t = 0; t < n; t++) {
    if (m.inbag[t][i] !== 0) continue;
    treeProba(m.trees[t], m.X[i]).forEach((v, k) => (p[k] += v));
    cnt++;
  }
  return cnt ? p.map((v) => v / cnt) : null;
}

export function ensembleVariance(rho, sigma2, N) {
  // Variance of the mean of N models of variance sigma2 and pairwise correlation rho.
  return rho * sigma2 + ((1 - rho) / N) * sigma2;
}

export function covMatrix(P) {
  // Covariances between the columns (models) of P[s][j] over the rows (training sets).
  const S = P.length, N = P[0].length;
  const mean = Array.from({ length: N }, (_, j) => P.reduce((a, row) => a + row[j], 0) / S);
  return Array.from({ length: N }, (_, i) => Array.from({ length: N }, (_, j) =>
    P.reduce((a, row) => a + (row[i] - mean[i]) * (row[j] - mean[j]), 0) / S));
}

export function ensembleStats(Ps) {
  // Ps: one matrix P[s][j] per point x: prediction of model j trained on set s.
  // sigma2 is the mean variance of one model, rho the mean covariance of two
  // different models over sigma2, varMean[n-1] the variance of the mean of the
  // first n models; all averaged over the points.
  const N = Ps[0][0].length;
  let sig = 0, off = 0;
  const varMean = new Array(N).fill(0);
  for (const P of Ps) {
    const c = covMatrix(P);
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) (i === j ? (sig += c[i][j] / N) : (off += c[i][j] / (N * (N - 1))));
    for (let n = 1; n <= N; n++) {
      let s = 0;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) s += c[i][j];
      varMean[n - 1] += s / (n * n);
    }
  }
  const k = Ps.length;
  return { sigma2: sig / k, rho: N > 1 ? off / k / (sig / k) : 0, varMean: varMean.map((v) => v / k) };
}

export function makeSine(n, noise, seed) {
  // n points x ~ U(0,1) in increasing order, y = sin 2 pi x + noise * N(0,1).
  const r = rng(seed);
  const x = Array.from({ length: n }, () => r()).sort((a, b) => a - b);
  return { x, y: x.map((v) => Math.sin(2 * Math.PI * v) + noise * gauss(r)) };
}

// ---------- impurity criteria and threshold scan ----------

export function impurity(counts, kind) {
  // Share-based node impurity: misclassification 1 - max p, Gini 1 - sum p^2,
  // entropy - sum p log2 p (0 log 0 = 0), so the maximum for K classes is
  // 1 - 1/K, 1 - 1/K and log2 K.
  const n = counts.reduce((s, c) => s + c, 0);
  if (n === 0) return 0;
  const p = counts.map((c) => c / n);
  if (kind === "mis") return 1 - Math.max(...p);
  if (kind === "gini") return 1 - p.reduce((s, v) => s + v * v, 0);
  if (kind === "ent") return p.reduce((s, v) => (v > 0 ? s - v * Math.log2(v) : s), 0);
  throw new Error(`unknown impurity ${kind}`);
}

export function scanSplits(y, kind) {
  // Every threshold "x <= t" of an object sequence in the order of the axis
  // (t = 0 .. n-2): impurity of both parts, their weighted sum, and the gain
  // over the parent.
  const n = y.length;
  const K = Math.max(...y) + 1;
  const total = new Array(K).fill(0);
  y.forEach((v) => total[v]++);
  const parent = impurity(total, kind);
  const left = new Array(K).fill(0);
  const rows = [];
  for (let t = 0; t < n - 1; t++) {
    left[y[t]]++;
    const right = total.map((c, k) => c - left[k]);
    const nl = t + 1, nr = n - nl;
    const hl = impurity(left, kind), hr = impurity(right, kind);
    const weighted = (nl * hl + nr * hr) / n;
    rows.push({ t, nl, nr, left: hl, right: hr, weighted, gain: parent - weighted });
  }
  return rows;
}

export function bestSplit(scan) {
  // The smallest weighted impurity; on a tie the leftmost threshold.
  return scan.reduce((b, r) => (r.weighted < b.weighted - 1e-12 ? r : b), scan[0]);
}

// ---------- regression tree (squared error) and gradient boosting ----------

export function fitRegTree(X, y, { maxDepth = Infinity, minLeaf = 1 } = {}) {
  // CART for regression: the split maximises the decrease of the summed
  // squared error; a leaf predicts the mean of its targets.
  const build = (idx, depth) => {
    const n = idx.length;
    const sum = idx.reduce((s, i) => s + y[i], 0);
    const node = { value: sum / n, n };
    const sse = idx.reduce((s, i) => s + (y[i] - node.value) ** 2, 0);
    if (depth >= maxDepth || n < 2 * minLeaf || sse <= 1e-12) return node;
    let best = null;
    for (let f = 0; f < X[0].length; f++) {
      const order = [...idx].sort((a, b) => X[a][f] - X[b][f]);
      let ls = 0;
      for (let s = 0; s < n - 1; s++) {
        ls += y[order[s]];
        const nl = s + 1, nr = n - nl;
        const a = X[order[s]][f], b = X[order[s + 1]][f];
        if (a === b || nl < minLeaf || nr < minLeaf) continue;
        // SSE decrease = nl * mean_l^2 + nr * mean_r^2 - n * mean^2
        const gain = (ls * ls) / nl + ((sum - ls) ** 2) / nr;
        if (!best || gain > best.gain + 1e-12) {
          let thr = (a + b) / 2;
          if (thr === b) thr = a;
          best = { gain, f, thr };
        }
      }
    }
    if (!best) return node;
    node.feature = best.f;
    node.threshold = best.thr;
    node.left = build(idx.filter((i) => X[i][best.f] <= best.thr), depth + 1);
    node.right = build(idx.filter((i) => X[i][best.f] > best.thr), depth + 1);
    return node;
  };
  return build(X.map((_, i) => i), 0);
}

export function regTreeLeaf(t, x) {
  while (t.left) t = x[t.feature] <= t.threshold ? t.left : t.right;
  return t;
}

export function regTreePredict(t, x) {
  return regTreeLeaf(t, x).value;
}

// The q-quantile as sklearn's _weighted_percentile takes it with unit
// weights ("inverted_cdf"): the smallest value with at least a share q of the
// values at or below it, so the median of an even count is the lower middle.
// The expression for the rank repeats sklearn's, float rounding included.
function lowerQuantile(v, q) {
  const s = [...v].sort((a, b) => a - b);
  return s[Math.max(0, Math.ceil(((100 * q) / 100) * s.length) - 1)];
}

const median = (v) => {
  const s = [...v].sort((a, b) => a - b), n = s.length;
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
};

// Huber's delta for the next tree: the alpha-quantile of |y - f|.
export function huberDelta(res, alpha = 0.9) {
  return lowerQuantile(res.map(Math.abs), alpha);
}

// Antigradient of the loss over the predictions, from residuals y - f:
// squared loss ½r²: r; absolute loss |r|: sign r; Huber: r clipped to ±delta.
export function antigradient(loss, res, alpha = 0.9) {
  if (loss === "squared_error") return res.slice();
  if (loss === "absolute_error") return res.map(Math.sign);
  const d = huberDelta(res, alpha);
  return res.map((r) => Math.sign(r) * Math.min(Math.abs(r), d));
}

export const BOOSTING_LOSSES = ["squared_error", "absolute_error", "huber"];

export function fitBoosting(X, y, { nEstimators = 100, lr = 0.1, maxDepth = 3, loss = "squared_error", alpha = 0.9 } = {}) {
  // Gradient boosting as GradientBoostingRegressor(loss=...) with subsample 1.
  // Start: the mean for squared loss, the median otherwise. Each tree fits
  // the antigradient. For absolute and Huber loss sklearn then replaces the
  // leaf values by the line-search step of the loss over the residuals that
  // fall into the leaf: their median, and for Huber the median plus the mean
  // of the deviations from it clipped at delta (Friedman 2001, before Alg. 4).
  // For squared loss the leaf mean already is that step.
  const f0 = loss === "squared_error" ? y.reduce((s, v) => s + v, 0) / y.length : median(y);
  const pred = y.map(() => f0);
  const trees = [], deltas = [];
  for (let m = 0; m < nEstimators; m++) {
    const res = y.map((v, i) => v - pred[i]);
    const delta = loss === "huber" ? huberDelta(res, alpha) : null;
    const t = fitRegTree(X, antigradient(loss, res, alpha), { maxDepth });
    if (loss !== "squared_error") {
      const byLeaf = new Map();
      X.forEach((x, i) => {
        const leaf = regTreeLeaf(t, x);
        byLeaf.set(leaf, [...(byLeaf.get(leaf) ?? []), res[i]]);
      });
      for (const [leaf, r] of byLeaf) {
        const med = lowerQuantile(r, 0.5);
        leaf.value = loss === "absolute_error" ? med
          : med + r.reduce((s, v) => s + Math.sign(v - med) * Math.min(delta, Math.abs(v - med)), 0) / r.length;
      }
    }
    trees.push(t); deltas.push(delta);
    X.forEach((x, i) => (pred[i] += lr * regTreePredict(t, x)));
  }
  return { f0, lr, trees, loss, deltas };
}

// Predictions on X after 0, 1, ..., all trees: out[k][i] equals boostingPredict(m, X[i], k).
export function boostingStaged(m, X) {
  const F = X.map(() => m.f0), out = [F.slice()];
  for (const t of m.trees) {
    X.forEach((x, i) => (F[i] += m.lr * regTreePredict(t, x)));
    out.push(F.slice());
  }
  return out;
}

export function boostingPredict(m, x, stages = m.trees.length) {
  let s = m.f0;
  for (let k = 0; k < stages; k++) s += m.lr * regTreePredict(m.trees[k], x);
  return s;
}

// Gradient boosting for two classes as GradientBoostingClassifier(loss="log_loss") with subsample 1: the
// decision value F is the log-odds. Start: the log-odds of the class share. Each tree fits the residual
// y - sigma(F), then every leaf value is replaced by the Newton step of the log loss over the objects in it,
// sum(y - p) / sum(p (1 - p)), zero when the denominator vanishes.
export const newtonStep = (num, den) => (Math.abs(den) < 1e-150 ? 0 : num / den);

export function fitBoostingClf(X, y, { nEstimators = 100, lr = 0.1, maxDepth = 3 } = {}) {
  const share = y.reduce((s, v) => s + v, 0) / y.length;
  const f0 = Math.log(share / (1 - share));
  const F = y.map(() => f0);
  const trees = [];
  for (let m = 0; m < nEstimators; m++) {
    const p = F.map(sigmoid);
    const res = y.map((v, i) => v - p[i]);
    const t = fitRegTree(X, res, { maxDepth });
    const byLeaf = new Map();
    X.forEach((x, i) => {
      const leaf = regTreeLeaf(t, x), a = byLeaf.get(leaf) ?? { num: 0, den: 0 };
      a.num += res[i]; a.den += p[i] * (1 - p[i]);
      byLeaf.set(leaf, a);
    });
    for (const [leaf, { num, den }] of byLeaf) leaf.value = newtonStep(num, den);
    trees.push(t);
    X.forEach((x, i) => (F[i] += lr * regTreePredict(t, x)));
  }
  return { f0, lr, trees };
}

// The decision value (log-odds) after the first `stages` trees.
export function boostingClfDecision(m, x, stages = m.trees.length) {
  let s = m.f0;
  for (let k = 0; k < stages; k++) s += m.lr * regTreePredict(m.trees[k], x);
  return s;
}

// ---------- AdaBoost over decision stumps ----------

export function fitAdaBoost(X, y, { nEstimators = 50 } = {}) {
  // Labels y in {0, 1}, read as -1 / +1. Each round fits a stump (a Gini tree
  // of depth 1) on the current weights, takes its weighted error eps and the
  // weight rho = 1/2 ln((1 - eps) / eps), then multiplies every weight by
  // e^(-rho y h) and normalises. sklearn's SAMME multiplies only the wrong
  // objects by e^(2 rho) and keeps the right ones: the same weights after
  // normalising, and its estimator weight is 2 rho for two classes.
  // Stops, as sklearn does, when a stump is perfect (kept, with sklearn's
  // weight 1, so rho = 1/2) or no better than chance (dropped).
  const n = X.length;
  const sgn = y.map((v) => 2 * v - 1);
  let w = new Array(n).fill(1 / n);
  const trees = [], rho = [], eps = [], weights = [];
  let stop = null;
  for (let t = 0; t < nEstimators; t++) {
    const tree = fitTree(X, y, { maxDepth: 1, weights: w, nClasses: 2 });
    const vote = X.map((x) => 2 * treePredict(tree, x) - 1);
    const e = w.reduce((s, v, i) => s + (vote[i] !== sgn[i] ? v : 0), 0);
    if (e >= 0.5) { stop = "chance"; break; }
    trees.push(tree); eps.push(e); weights.push(w);
    if (e <= 0) { rho.push(0.5); stop = "perfect"; break; }
    const r = 0.5 * Math.log((1 - e) / e);
    rho.push(r);
    const next = w.map((v, i) => v * Math.exp(-r * sgn[i] * vote[i]));
    const z = next.reduce((s, v) => s + v, 0);
    w = next.map((v) => v / z);
  }
  return { trees, rho, eps, weights, stop };
}

export function adaStumpVote(m, t, x) {
  return 2 * treePredict(m.trees[t], x) - 1;
}

// F_T(x) = sum of rho_t h_t(x) over the first T stumps; its sign is the class.
export function adaScore(m, x, T = m.trees.length) {
  let s = 0;
  for (let t = 0; t < T; t++) s += m.rho[t] * adaStumpVote(m, t, x);
  return s;
}

// ---------- logistic regression on polynomial features ----------

export function polyFeatures(x, degree, { pure = false } = {}) {
  // Same column order as sklearn PolynomialFeatures(include_bias=False):
  // by degree, then combinations with replacement of feature indices.
  // pure keeps only the columns with one variable (x_j^k), in that order,
  // which makes the model additive: f(x1) + g(x2).
  const out = [];
  const d = x.length;
  for (let deg = 1; deg <= degree; deg++) {
    if (pure) { for (let j = 0; j < d; j++) out.push(x[j] ** deg); continue; }
    const rec = (start, left, prod) => {
      if (left === 0) return out.push(prod);
      for (let j = start; j < d; j++) rec(j, left - 1, prod * x[j]);
    };
    rec(0, deg, 1);
  }
  return out;
}

export function polyNames(vars, degree, { style = "pretty", pure = false } = {}) {
  // Names in the column order of polyFeatures. "sklearn" spells them as
  // get_feature_names_out does ("x1^2 x2"); "pretty" uses superscripts.
  const sup = { 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  const out = [];
  for (let deg = 1; deg <= degree; deg++) {
    const rec = (start, left, counts) => {
      if (left === 0) {
        const parts = counts.map((c, j) => (c === 0 ? null
          : c === 1 ? vars[j] : style === "sklearn" ? `${vars[j]}^${c}` : vars[j] + (sup[c] || `^${c}`)))
          .filter(Boolean);
        if (pure && parts.length > 1) return undefined;
        return out.push(parts.join(style === "sklearn" ? " " : ""));
      }
      for (let j = start; j < vars.length; j++) {
        const next = counts.slice();
        next[j]++;
        rec(j, left - 1, next);
      }
    };
    rec(0, deg, vars.map(() => 0));
  }
  return out;
}

function solve(A, b) {
  const n = b.length;
  const M = A.map((row, i) => [...row, b[i]]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c] / M[c][c];
      for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k];
    }
  }
  return M.map((row, i) => row[n] / row[i]);
}

function lstsq(A, b) {
  // Householder QR of a tall full-rank A, then back substitution: min ||Ax - b||.
  const m = A.length;
  const n = A[0].length;
  const R = A.map((row) => row.slice());
  const y = b.slice();
  for (let k = 0; k < n; k++) {
    let norm = 0;
    for (let i = k; i < m; i++) norm += R[i][k] ** 2;
    norm = Math.sqrt(norm);
    if (norm === 0) continue;
    const alpha = R[k][k] > 0 ? -norm : norm;
    const v = new Array(m).fill(0);
    for (let i = k; i < m; i++) v[i] = R[i][k];
    v[k] -= alpha;
    let vv = 0;
    for (let i = k; i < m; i++) vv += v[i] ** 2;
    if (vv === 0) continue;
    for (let j = k; j < n; j++) {
      let s = 0;
      for (let i = k; i < m; i++) s += v[i] * R[i][j];
      s = (2 * s) / vv;
      for (let i = k; i < m; i++) R[i][j] -= s * v[i];
    }
    let s = 0;
    for (let i = k; i < m; i++) s += v[i] * y[i];
    s = (2 * s) / vv;
    for (let i = k; i < m; i++) y[i] -= s * v[i];
  }
  const x = new Array(n).fill(0);
  for (let k = n - 1; k >= 0; k--) {
    let s = y[k];
    for (let j = k + 1; j < n; j++) s -= R[k][j] * x[j];
    x[k] = s / R[k][k];
  }
  return x;
}

const sigmoid = (z) => (z >= 0 ? 1 / (1 + Math.exp(-z)) : Math.exp(z) / (1 + Math.exp(z)));

export function fitLogreg(X, y, { degree = 1, C = 1, maxIter = 100, pure = false } = {}) {
  // Objective of sklearn LogisticRegression: C * sum(logloss) + ||w||^2 / 2,
  // intercept not penalised. Minimised by Newton steps with backtracking.
  const F = X.map((x) => polyFeatures(x, degree, { pure }));
  const p = F[0].length;
  const mean = new Array(p).fill(0);
  const std = new Array(p).fill(0);
  for (const f of F) f.forEach((v, j) => (mean[j] += v / F.length));
  for (const f of F) f.forEach((v, j) => (std[j] += (v - mean[j]) ** 2 / F.length));
  for (let j = 0; j < p; j++) std[j] = Math.sqrt(std[j]) || 1;
  const Z = F.map((f) => [1, ...f.map((v, j) => (v - mean[j]) / std[j])]);
  const loss = (th) => {
    let s = 0;
    Z.forEach((z, i) => {
      const m = z.reduce((a, v, j) => a + v * th[j], 0);
      s += Math.max(m, 0) - m * y[i] + Math.log1p(Math.exp(-Math.abs(m)));
    });
    return C * s + th.slice(1).reduce((a, v) => a + v * v, 0) / 2;
  };
  let th = new Array(p + 1).fill(0);
  let cur = loss(th);
  for (let it = 0; it < maxIter; it++) {
    const g = th.map((v, j) => (j ? v : 0));
    const H = th.map((_, a) => th.map((__, b) => (a === b && a ? 1 : 0)));
    Z.forEach((z, i) => {
      const q = sigmoid(z.reduce((a, v, j) => a + v * th[j], 0));
      for (let a = 0; a <= p; a++) {
        g[a] += C * (q - y[i]) * z[a];
        for (let b = 0; b <= p; b++) H[a][b] += C * q * (1 - q) * z[a] * z[b];
      }
    });
    const step = solve(H, g);
    let t = 1;
    let next;
    let nl;
    do {
      next = th.map((v, j) => v - t * step[j]);
      nl = loss(next);
      t /= 2;
    } while (nl > cur && t > 1e-10);
    const done = Math.abs(cur - nl) < 1e-13 * Math.max(1, Math.abs(cur));
    th = next;
    cur = nl;
    if (done) break;
  }
  return { degree, pure, mean, std, theta: th };
}

export function logregDecision(m, x) {
  // The logit w . z + b, which sklearn calls decision_function.
  const f = polyFeatures(x, m.degree, { pure: m.pure });
  let z = m.theta[0];
  f.forEach((v, j) => (z += m.theta[j + 1] * ((v - m.mean[j]) / m.std[j])));
  return z;
}

export function logregLine(m) {
  // The decision value of a degree-1 model as a x1 + b x2 + c in original
  // coordinates, so a page can draw the exact boundary a x1 + b x2 + c = 0.
  if (m.degree !== 1) throw new Error("logregLine needs degree 1");
  const a = m.theta[1] / m.std[0], b = m.theta[2] / m.std[1];
  return { a, b, c: m.theta[0] - a * m.mean[0] - b * m.mean[1] };
}

export function logregProba(m, x) {
  return sigmoid(logregDecision(m, x));
}

// ---------- multiclass: One vs Rest and One vs One over logistic regressions ----------

export function fitOvr(X, y, { C = 1 } = {}) {
  // One model per class, that class (1) against all others (0), each on the whole sample.
  const classes = [...new Set(y)].sort((a, b) => a - b);
  return { classes, models: classes.map((c) => fitLogreg(X, y.map((v) => (v === c ? 1 : 0)), { C })) };
}

export function ovrDecision(m, x) {
  return m.models.map((q) => logregDecision(q, x));
}

export function ovrClaims(m, x) {
  // How many classifiers answer "mine": 0 or 2 and more is an undecided point.
  return ovrDecision(m, x).filter((z) => z > 0).length;
}

export function fitOvo(X, y, { C = 1 } = {}) {
  // One model per pair (i < j) on the sub-sample of those two classes, i as 0 and j as 1.
  const classes = [...new Set(y)].sort((a, b) => a - b);
  const pairs = [];
  for (let i = 0; i < classes.length; i++) for (let j = i + 1; j < classes.length; j++) {
    const idx = y.map((v, q) => q).filter((q) => y[q] === classes[i] || y[q] === classes[j]);
    pairs.push({ i, j, model: fitLogreg(idx.map((q) => X[q]), idx.map((q) => (y[q] === classes[j] ? 1 : 0)), { C }) });
  }
  return { classes, pairs };
}

export function ovoScores(m, x) {
  // Votes per class, summed confidences per class, and sklearn's decision value:
  // votes + sum_conf / (3 (|sum_conf| + 1)), a term below one vote, so it only breaks ties.
  const K = m.classes.length;
  const votes = new Array(K).fill(0);
  const conf = new Array(K).fill(0);
  const pairs = m.pairs.map(({ i, j, model }) => {
    const z = logregDecision(model, x);
    const winner = z > 0 ? j : i;
    votes[winner]++;
    conf[i] -= z;
    conf[j] += z;
    return { i, j, z, winner };
  });
  const decision = votes.map((v, k) => v + conf[k] / (3 * (Math.abs(conf[k]) + 1)));
  return { votes, conf, decision, pairs };
}

// ---------- linear regression on polynomial features ----------

function standardize(F) {
  const p = F[0].length;
  const mean = new Array(p).fill(0);
  const std = new Array(p).fill(0);
  for (const f of F) f.forEach((v, j) => (mean[j] += v / F.length));
  for (const f of F) f.forEach((v, j) => (std[j] += (v - mean[j]) ** 2 / F.length));
  for (let j = 0; j < p; j++) std[j] = Math.sqrt(std[j]) || 1;
  return { mean, std, Z: F.map((f) => f.map((v, j) => (v - mean[j]) / std[j])) };
}

export function fitLinear(X, y, { degree = 1, penalty = "ols", alpha = 0, w0 = null, maxSweeps = 1e6 } = {}) {
  // Objectives as in sklearn, intercept never penalised:
  //   ols   ||y - Zw - b||^2
  //   ridge ||y - Zw - b||^2 + alpha ||w||^2
  //   lasso ||y - Zw - b||^2 / (2n) + alpha ||w||_1   (coordinate descent)
  const { mean, std, Z } = standardize(X.map((x) => polyFeatures(x, degree)));
  const n = Z.length;
  const p = Z[0].length;
  const b = y.reduce((s, v) => s + v, 0) / n;
  const r = y.map((v) => v - b);
  let w;
  if (penalty === "lasso") {
    w = w0 ? w0.slice() : new Array(p).fill(0);
    const res = r.map((v, i) => v - Z[i].reduce((s, z, j) => s + z * w[j], 0));
    for (let sweep = 0; sweep < maxSweeps; sweep++) {
      let change = 0;
      for (let j = 0; j < p; j++) {
        let rho = 0;
        for (let i = 0; i < n; i++) rho += Z[i][j] * (res[i] + Z[i][j] * w[j]);
        rho /= n;
        // Standardised columns: z_j . z_j / n = 1, so the update is a soft threshold.
        const next = Math.sign(rho) * Math.max(Math.abs(rho) - alpha, 0);
        const d = next - w[j];
        if (d !== 0) {
          for (let i = 0; i < n; i++) res[i] -= Z[i][j] * d;
          w[j] = next;
          change = Math.max(change, Math.abs(d));
        }
      }
      if (change < 1e-13) break;
    }
  } else {
    // Least squares by QR, not normal equations: at degree 9 Z^T Z is too
    // ill-conditioned for doubles. Ridge is least squares on [Z; sqrt(alpha) I].
    const rows = Z.map((z) => z.slice());
    const rhs = r.slice();
    if (penalty === "ridge") {
      for (let j = 0; j < p; j++) {
        rows.push(Array.from({ length: p }, (_, c) => (c === j ? Math.sqrt(alpha) : 0)));
        rhs.push(0);
      }
    }
    w = lstsq(rows, rhs);
  }
  return { degree, mean, std, w, b };
}

export function olsLine(x, y) {
  // Least-squares line y = w0 + w1 x, as fitLinear in the original units.
  const m = fitLinear(x.map((v) => [v]), y, { degree: 1 });
  const w1 = m.w[0] / m.std[0];
  return { w0: m.b - w1 * m.mean[0], w1 };
}

export function ladLine(x, y) {
  // Least absolute deviations line (the median regression sklearn's
  // QuantileRegressor(quantile=0.5) fits). The objective is a convex
  // piecewise-linear function of (w0, w1), so a minimum lies at a vertex:
  // a line through two data points with different x. All pairs are tried.
  const n = x.length;
  const sae = (w0, w1) => x.reduce((s, v, i) => s + Math.abs(y[i] - w0 - w1 * v), 0);
  let best = null;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    if (x[i] === x[j]) continue;
    const w1 = (y[j] - y[i]) / (x[j] - x[i]);
    const w0 = y[i] - w1 * x[i];
    const q = sae(w0, w1);
    if (!best || q < best.q - 1e-12) best = { w0, w1, q };
  }
  if (!best) {
    // No two distinct x: the best horizontal line is at the median of y.
    const s = [...y].sort((a, b) => a - b);
    return { w0: s.length ? (s[Math.floor((s.length - 1) / 2)] + s[Math.floor(s.length / 2)]) / 2 : 0, w1: 0 };
  }
  return { w0: best.w0, w1: best.w1 };
}

export function regMetrics(y, pred) {
  // MSE, MAE and R2 = 1 - MSE / (variance of y, divided by n), as sklearn.
  const n = y.length;
  const mean = y.reduce((s, v) => s + v, 0) / n;
  let se = 0, ae = 0, tot = 0;
  y.forEach((v, i) => { se += (v - pred[i]) ** 2; ae += Math.abs(v - pred[i]); tot += (v - mean) ** 2; });
  return { mse: se / n, mae: ae / n, r2: tot === 0 ? 0 : 1 - se / tot };
}

// ---------- margins and margin losses ----------

export function margins(X, y, w, b = 0) {
  // M = y (w . x + b) for labels y in {+1, -1}; M > 0 means a correct answer.
  return X.map((x, i) => y[i] * (x.reduce((s, v, j) => s + v * w[j], b)));
}

const LN2 = Math.log(2);
const MARGIN_LOSSES = {
  step: (M) => (M <= 0 ? 1 : 0),
  square: (M) => (1 - M) ** 2,
  hinge: (M) => Math.max(0, 1 - M),
  // log2, so that the loss is 1 at M = 0 and bounds the step from above;
  // the stable form never exponentiates a large positive argument.
  logistic: (M) => (M >= 0 ? Math.log1p(Math.exp(-M)) : -M + Math.log1p(Math.exp(M))) / LN2,
  exp: (M) => Math.exp(-M),
};

export function marginLoss(name, M) {
  const f = MARGIN_LOSSES[name];
  if (!f) throw new Error(`unknown margin loss ${name}`);
  return f(M);
}

export function lassoPath(X, y, { degree = 1 } = {}) {
  // Exact LASSO path by LARS with the lasso modification (Efron et al. 2004),
  // the objective of sklearn Lasso: ||y - Zw - b||^2 / (2n) + alpha ||w||_1.
  // The weights are piecewise linear in alpha; breakpoints are recorded from
  // alpha_max down to 0, where the path ends at least squares.
  const { mean, std, Z } = standardize(X.map((x) => polyFeatures(x, degree)));
  const n = Z.length, p = Z[0].length;
  const b = y.reduce((s, v) => s + v, 0) / n;
  const r = y.map((v) => v - b);
  const w = new Array(p).fill(0);
  const corr = () => Array.from({ length: p }, (_, j) =>
    Z.reduce((s, z, i) => s + z[j] * (r[i] - z.reduce((t, zk, k) => t + zk * w[k], 0)), 0));
  let c = corr();
  let C = Math.max(...c.map(Math.abs));
  const active = [c.map(Math.abs).indexOf(C)];
  const points = [{ alpha: C / n, w: w.slice() }];
  for (let step = 0; step < 8 * p && C > 1e-12; step++) {
    const s = active.map((j) => Math.sign(c[j]));
    const G = active.map((a) => active.map((k) => Z.reduce((t, z) => t + z[a] * z[k], 0)));
    const d = solve(G, s);
    const u = Z.map((z) => active.reduce((t, j, q) => t + z[j] * d[q], 0));
    // Along the step gamma, active |c| = C - gamma; an inactive j joins when |c_j - gamma a_j| = C - gamma.
    let gamma = C, join = -1, drop = -1;
    for (let j = 0; j < p; j++) {
      if (active.includes(j)) continue;
      const aj = Z.reduce((t, z, i) => t + z[j] * u[i], 0);
      for (const g of [(C - c[j]) / (1 - aj), (C + c[j]) / (1 + aj)]) {
        if (g > 1e-12 && g < gamma) { gamma = g; join = j; }
      }
    }
    // Lasso modification: a weight that would cross zero leaves the active set.
    active.forEach((j, q) => {
      const g = -w[j] / d[q];
      if (g > 1e-12 && g < gamma) { gamma = g; drop = q; join = -1; }
    });
    active.forEach((j, q) => (w[j] += gamma * d[q]));
    C -= gamma;
    if (drop >= 0) { w[active[drop]] = 0; active.splice(drop, 1); }
    points.push({ alpha: Math.max(C, 0) / n, w: w.slice() });
    c = corr();
    if (join >= 0) active.push(join);
    if (join < 0 && drop < 0) break;
  }
  return { degree, mean, std, b, points };
}

export function lassoAt(path, alpha) {
  // Linear interpolation between the breakpoints that bracket alpha.
  const pts = path.points;
  let w;
  if (alpha >= pts[0].alpha) w = pts[0].w.slice();
  else if (alpha <= pts[pts.length - 1].alpha) w = pts[pts.length - 1].w.slice();
  else {
    let k = 0;
    while (pts[k + 1].alpha > alpha) k++;
    const a0 = pts[k].alpha, a1 = pts[k + 1].alpha, t = (a0 - alpha) / (a0 - a1);
    w = pts[k].w.map((v, j) => v + t * (pts[k + 1].w[j] - v));
  }
  return { degree: path.degree, mean: path.mean, std: path.std, w, b: path.b };
}

export function linearPredict(m, x) {
  const f = polyFeatures(x, m.degree);
  return f.reduce((s, v, j) => s + m.w[j] * ((v - m.mean[j]) / m.std[j]), m.b);
}

// Minimiser of (w - c)^T A (w - c) + lam * penalty(w) in two dimensions, for
// the geometry picture: penalty "l2" is ||w||^2, "l1" is |w1| + |w2|.
export function penalized2d(A, c, lam, kind) {
  if (kind === "l2") {
    const M = [[A[0][0] + lam, A[0][1]], [A[1][0], A[1][1] + lam]];
    return solve(M, [A[0][0] * c[0] + A[0][1] * c[1], A[1][0] * c[0] + A[1][1] * c[1]]);
  }
  const w = [0, 0];
  for (let it = 0; it < 100000; it++) {
    let change = 0;
    for (let j = 0; j < 2; j++) {
      const k = 1 - j;
      const rho = A[j][j] * c[j] - A[j][k] * (w[k] - c[k]);
      const next = (Math.sign(rho) * Math.max(Math.abs(rho) - lam / 2, 0)) / A[j][j];
      change = Math.max(change, Math.abs(next - w[j]));
      w[j] = next;
    }
    if (change < 1e-15) break;
  }
  return w.map((v) => (v === 0 ? 0 : v));
}

// ---------- gradient descent paths ----------

export function gdPath(grad, x0, { lr, steps, momentum = 0, nesterov = false }) {
  // v <- momentum * v - lr * grad(x or the look-ahead point); x <- x + v.
  // momentum = 0 is plain gradient descent.
  let x = x0.slice();
  let v = x0.map(() => 0);
  const path = [x.slice()];
  for (let k = 0; k < steps; k++) {
    const at = nesterov ? x.map((xi, i) => xi + momentum * v[i]) : x;
    const g = grad(at);
    v = v.map((vi, i) => momentum * vi - lr * g[i]);
    x = x.map((xi, i) => xi + v[i]);
    path.push(x.slice());
  }
  return path;
}

// Test surfaces of the gradient descent and optimizer pages: loss f, gradient g,
// the minimum, the view box and the default start.
export const SURFACES = {
  ellipse: { label: "Вытянутый овраг: x² + 10y²", f: ([x, y]) => x * x + 10 * y * y, g: ([x, y]) => [2 * x, 20 * y], min: [0, 0], box: [-3, 3], start: [-2.6, 1.6] },
  round: { label: "Круглая чаша: x² + y²", f: ([x, y]) => x * x + y * y, g: ([x, y]) => [2 * x, 2 * y], min: [0, 0], box: [-3, 3], start: [-2.6, 1.6] },
  rosen: {
    label: "Розенброк: (1 − x)² + 10(y − x²)²",
    f: ([x, y]) => (1 - x) ** 2 + 10 * (y - x * x) ** 2,
    g: ([x, y]) => [-2 * (1 - x) - 40 * x * (y - x * x), 20 * (y - x * x)],
    min: [1, 1], box: [-2, 2], start: [-1.5, 1.8],
  },
};

export const OPT_METHODS = ["sgd", "momentum", "nesterov", "adagrad", "rmsprop", "adam"];

// The setting of the note's table: Rosenbrock from its start, these steps (powers
// of ten, points of the log grid the note chose them from), rho and beta shared.
export const OPT_PRESET = {
  steps: 100, rho: 0.9, beta: 0.9,
  lr: { sgd: -1.75, momentum: -2, nesterov: -2.25, adagrad: -0.75, rmsprop: -1.375, adam: -1 },
};

// Path of steps + 1 points of one optimizer, the start included. rho is the
// inertia of momentum and Nesterov, beta the average of RMSProp; Adam keeps
// beta1 and beta2. Cache methods divide by sqrt(cache) + eps. Plain descent,
// momentum and Nesterov are gdPath.
export const OPT_FIXED = { beta1: 0.9, beta2: 0.999, eps: 1e-8 };
export function optPath(method, grad, x0, { lr, steps, rho = 0.9, beta = 0.9, beta1 = OPT_FIXED.beta1, beta2 = OPT_FIXED.beta2, eps = OPT_FIXED.eps }) {
  if (method === "sgd") return gdPath(grad, x0, { lr, steps });
  if (method === "momentum" || method === "nesterov") return gdPath(grad, x0, { lr, steps, momentum: rho, nesterov: method === "nesterov" });
  let x = x0.slice();
  let cache = x0.map(() => 0), m = x0.map(() => 0);
  const path = [x.slice()];
  for (let t = 1; t <= steps; t++) {
    const g = grad(x);
    if (method === "adagrad") {
      cache = cache.map((c, i) => c + g[i] * g[i]);
      x = x.map((xi, i) => xi - (lr * g[i]) / (Math.sqrt(cache[i]) + eps));
    } else if (method === "rmsprop") {
      cache = cache.map((c, i) => beta * c + (1 - beta) * g[i] * g[i]);
      x = x.map((xi, i) => xi - (lr * g[i]) / (Math.sqrt(cache[i]) + eps));
    } else if (method === "adam") {
      m = m.map((mi, i) => beta1 * mi + (1 - beta1) * g[i]);
      cache = cache.map((c, i) => beta2 * c + (1 - beta2) * g[i] * g[i]);
      x = x.map((xi, i) => xi - (lr * (m[i] / (1 - beta1 ** t))) / (Math.sqrt(cache[i] / (1 - beta2 ** t)) + eps));
    } else throw new Error(`unknown optimizer ${method}`);
    path.push(x.slice());
  }
  return path;
}

// A run diverged when it ends at a non-number or at a loss a thousand times
// above the start loss (at least 1).
export function optDiverged(f, path, factor = 1e3) {
  const end = path[path.length - 1];
  return !end.every(Number.isFinite) || f(end) > factor * Math.max(f(path[0]), 1);
}

// ---------- multilayer perceptron ----------
// z_k = W_k h_{k-1} + b_k, h_k = phi(z_k), the last layer gives the logit and
// P(y=1) = sigma(logit). W_k is (out, in), as in the notes; sklearn stores the
// transpose. Training is full-batch gradient descent on the mean log loss, the
// step of sklearn's solver="sgd" with momentum=0, batch_size=n and alpha=0.

// phi and its derivative as a function of the activation value h = phi(z), the
// form sklearn's backward pass uses; relu'(0) = 0 as there.
const MLP_ACT = {
  tanh: { f: Math.tanh, d: (h) => 1 - h * h },
  logistic: { f: sigmoid, d: (h) => h * (1 - h) },
  relu: { f: (z) => (z > 0 ? z : 0), d: (h) => (h > 0 ? 1 : 0) },
  linear: { f: (z) => z, d: () => 1 },
};

export function mlpInit(hidden, act, seed) {
  // sklearn's start: uniform in +-sqrt(factor / (fan_in + fan_out)), factor 6, and 2 for the logistic activation.
  const sizes = [2, ...hidden, 1];
  const r = rng(seed);
  const factor = act === "logistic" ? 2 : 6;
  const W = [], b = [];
  for (let k = 1; k < sizes.length; k++) {
    const bound = Math.sqrt(factor / (sizes[k - 1] + sizes[k]));
    const u = () => (2 * r() - 1) * bound;
    W.push(Array.from({ length: sizes[k] }, () => Array.from({ length: sizes[k - 1] }, u)));
    b.push(Array.from({ length: sizes[k] }, u));
  }
  return { act, W, b };
}

// Pre-activations z[k] and outputs h[k] of every layer; h[0] = x, z[last] is the logit.
export function mlpActivations(net, x) {
  const f = MLP_ACT[net.act].f;
  const L = net.W.length;
  const z = [], h = [x];
  for (let k = 0; k < L; k++) {
    const zk = net.W[k].map((row, j) => row.reduce((s, w, i) => s + w * h[k][i], net.b[k][j]));
    z.push(zk);
    h.push(k < L - 1 ? zk.map(f) : zk);
  }
  return { z, h };
}

export function mlpLogit(net, x) {
  const { z } = mlpActivations(net, x);
  return z[z.length - 1][0];
}

export function mlpProba(net, x) {
  return sigmoid(mlpLogit(net, x));
}

// Mean log loss from logits: softplus(z) - y z, stable for huge |z|.
export function mlpLoss(net, X, y) {
  let s = 0;
  X.forEach((x, i) => {
    const z = mlpLogit(net, x);
    s += (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z))) - y[i] * z;
  });
  return s / X.length;
}

// Backpropagation: delta_last = p - y, delta_{k-1} = (W_k^T delta_k) * phi'(h_{k-1}), dW_k = delta_k h_{k-1}^T, db_k = delta_k.
// outDelta(logit, i) is dL_i/d logit of the output neuron; the default is the log loss, p - y.
export function mlpGrad(net, X, y, outDelta = null) {
  const d = MLP_ACT[net.act].d;
  const L = net.W.length;
  const gW = net.W.map((M) => M.map((row) => row.map(() => 0)));
  const gb = net.b.map((v) => v.map(() => 0));
  X.forEach((x, n) => {
    const { z, h } = mlpActivations(net, x);
    let delta = [outDelta ? outDelta(z[L - 1][0], n) : sigmoid(z[L - 1][0]) - y[n]];
    for (let k = L - 1; k >= 0; k--) {
      delta.forEach((dj, j) => {
        gb[k][j] += dj;
        h[k].forEach((hi, i) => { gW[k][j][i] += dj * hi; });
      });
      if (k > 0) delta = h[k].map((hi, i) => d(hi) * net.W[k].reduce((s, row, j) => s + row[i] * delta[j], 0));
    }
  });
  const m = X.length;
  return { W: gW.map((M) => M.map((row) => row.map((v) => v / m))), b: gb.map((v) => v.map((u) => u / m)) };
}

// One step w <- w - lr * grad, on a copy.
export function mlpStep(net, X, y, lr, outDelta = null) {
  const g = mlpGrad(net, X, y, outDelta);
  return {
    act: net.act,
    W: net.W.map((M, k) => M.map((row, j) => row.map((w, i) => w - lr * g.W[k][j][i]))),
    b: net.b.map((v, k) => v.map((w, j) => w - lr * g.b[k][j])),
  };
}

// ---------- softmax with temperature, distillation ----------

// q_i = exp(z_i / T) / sum_j exp(z_j / T), the maximum subtracted first.
export function softmaxT(z, T = 1) {
  const s = z.map((v) => v / T), m = Math.max(...s);
  const e = s.map((v) => Math.exp(v - m)), sum = e.reduce((a, b) => a + b, 0);
  return e.map((v) => v / sum);
}

// H(q) = -sum q ln q with 0 ln 0 = 0.
export function entropy(q) {
  return q.reduce((s, v) => (v > 0 ? s - v * Math.log(v) : s), 0);
}

// dC/dz = (q - p) / T for C = -sum p ln softmax(z / T).
export function softmaxCeGrad(z, p, T = 1) {
  return softmaxT(z, T).map((qi, i) => (qi - p[i]) / T);
}

const softplus = (x) => (x > 0 ? x + Math.log1p(Math.exp(-x)) : Math.log1p(Math.exp(x)));

// The Hinton loss of one object for two classes, with the student's logits (-d/2, d/2) and the teacher's
// (-u/2, u/2): softmax of such a pair at temperature T is (1 - sigma(d/T), sigma(d/T)). Then
// loss = lam CE(y, sigma(d)) + (1 - lam) T^2 CE(sigma(u/T), sigma(d/T)), and its derivative in d is
// lam (sigma(d) - y) + (1 - lam) T (sigma(d/T) - sigma(u/T)): the T^2 turns the 1/T of the soft term into T.
export function distillTerms(d, u, y, T, lam) {
  const p = sigmoid(u / T);
  return {
    loss: lam * (softplus(d) - y * d) + (1 - lam) * T * T * (softplus(d / T) - (p * d) / T),
    delta: lam * (sigmoid(d) - y) + (1 - lam) * T * (sigmoid(d / T) - p),
  };
}

// Mean Hinton loss of a one-logit network; U are the teacher's decision values for the same objects.
export function mlpDistillLoss(net, X, y, U, { T, lam }) {
  return X.reduce((s, x, i) => s + distillTerms(mlpLogit(net, x), U[i], y[i], T, lam).loss, 0) / X.length;
}

// The outDelta of mlpGrad and mlpStep for the Hinton loss.
export const distillDelta = (U, y, { T, lam }) => (d, i) => distillTerms(d, U[i], y[i], T, lam).delta;

// Number of corners of the region logit > 0, for a region that lies inside the
// box and is star-shaped about its centroid; null when it is empty or reaches
// the box edge. Counts the local maxima of the distance from the centroid to
// the boundary over the angle (smoothed over 9 of 720 directions, a maximum
// must stand 3% of the mean radius above both sides): a rounded triangle gives
// 3, a hexagon 6. A measurement of the picture, not a property of the model.
export function mlpCorners(net, { lo, hi }) {
  const inside = (p) => mlpLogit(net, p) > 0;
  const G = 80;
  let sx = 0, sy = 0, n = 0;
  for (let i = 0; i < G; i++) for (let j = 0; j < G; j++) {
    const p = [lo[0] + ((hi[0] - lo[0]) * (i + 0.5)) / G, lo[1] + ((hi[1] - lo[1]) * (j + 0.5)) / G];
    if (inside(p)) { sx += p[0]; sy += p[1]; n++; }
  }
  if (n === 0) return null;
  const c = [sx / n, sy / n];
  const A = 720, radius = [];
  for (let a = 0; a < A; a++) {
    const t = (2 * Math.PI * a) / A, dir = [Math.cos(t), Math.sin(t)];
    // distance from c to the box edge along the ray
    const reach = Math.min(...[0, 1].map((k) => (dir[k] > 0 ? (hi[k] - c[k]) / dir[k] : dir[k] < 0 ? (lo[k] - c[k]) / dir[k] : Infinity)));
    const at = (m) => [c[0] + m * dir[0], c[1] + m * dir[1]];
    if (inside(at(reach * 0.999))) return null;
    let near = 0, far = reach;
    for (let k = 0; k < 50; k++) { const m = (near + far) / 2; if (inside(at(m))) near = m; else far = m; }
    radius.push(near);
  }
  const sm = radius.map((_, i) => { let s = 0; for (let k = -4; k <= 4; k++) s += radius[(i + k + A) % A]; return s / 9; });
  const prominence = (0.03 * sm.reduce((a, b) => a + b, 0)) / A;
  let corners = 0;
  for (let i = 0; i < A; i++) {
    if (!(sm[i] >= sm[(i + 1) % A] && sm[i] > sm[(i - 1 + A) % A])) continue;
    for (let k = 1; k < A / 4; k++) {
      const r = sm[(i + k) % A], l = sm[(i - k + A) % A];
      if (r > sm[i] || l > sm[i]) break;
      if (sm[i] - r > prominence && sm[i] - l > prominence) { corners++; break; }
    }
  }
  return corners;
}

// Scenarios of the page, each a claim of lecture 6 that mlcore.test.mjs measures:
// the page applies the record as it is. epochs is how many full-batch steps the
// claim was checked after; logEpochs asks the page for a logarithmic epoch axis,
// where the first steps of a fast event stay visible; labels carry no numbers,
// the page prints the fields.
export const MLP_SCENARIOS = [
  { id: "tanh3", label: "скруглённый треугольник", data: "circles", hidden: [3], act: "tanh", lr: 1, seed: 1, epochs: 3000 },
  { id: "relu3", label: "шестиугольник на удачном seed", data: "circles", hidden: [3], act: "relu", lr: 1, seed: 3, epochs: 3000 },
  { id: "relu3-stuck", label: "тот же ReLU, другой seed: застрял на неполной границе", data: "circles", hidden: [3], act: "relu", lr: 1, seed: 4, epochs: 3000 },
  { id: "relu3-dead", label: "тот же ReLU, ещё seed: нейроны мертвы, константа", data: "circles", hidden: [3], act: "relu", lr: 1, seed: 10, epochs: 3000 },
  { id: "explode", label: "слишком большой шаг: взрыв потери и константа", data: "circles", hidden: [4, 4, 4], act: "relu", lr: 10, seed: 5, epochs: 300, logEpochs: true },
];

// ---------- metrics ----------

export function confusion(scores, y, t) {
  let tp = 0, fp = 0, fn = 0, tn = 0;
  scores.forEach((s, i) => {
    const pos = s >= t;
    if (pos && y[i] === 1) tp++;
    else if (pos) fp++;
    else if (y[i] === 1) fn++;
    else tn++;
  });
  return {
    tp, fp, fn, tn,
    precision: tp + fp ? tp / (tp + fp) : 0,
    recall: tp + fn ? tp / (tp + fn) : 0,
    fpr: fp + tn ? fp / (fp + tn) : 0,
  };
}

export function rocCurve(scores, y, { dropIntermediate = true } = {}) {
  // sklearn roc_curve: one point per distinct score, collinear points dropped,
  // (0, 0) prepended.
  const order = scores.map((s, i) => i).sort((a, b) => scores[b] - scores[a]);
  const P = y.filter((v) => v === 1).length;
  const N = y.length - P;
  let tps = [], fps = [], thr = [];
  let tp = 0, fp = 0;
  order.forEach((i, k) => {
    if (y[i] === 1) tp++;
    else fp++;
    if (k === order.length - 1 || scores[order[k + 1]] !== scores[i]) {
      tps.push(tp);
      fps.push(fp);
      thr.push(scores[i]);
    }
  });
  if (dropIntermediate && tps.length > 2) {
    const keep = tps.map((_, k) => k === 0 || k === tps.length - 1 ||
      fps[k - 1] - 2 * fps[k] + fps[k + 1] !== 0 || tps[k - 1] - 2 * tps[k] + tps[k + 1] !== 0);
    tps = tps.filter((_, k) => keep[k]);
    fps = fps.filter((_, k) => keep[k]);
    thr = thr.filter((_, k) => keep[k]);
  }
  return {
    fpr: [0, ...fps.map((v) => v / N)],
    tpr: [0, ...tps.map((v) => v / P)],
    thresholds: [Infinity, ...thr],
  };
}

export function auc({ fpr, tpr }) {
  let s = 0;
  for (let i = 1; i < fpr.length; i++) s += ((fpr[i] - fpr[i - 1]) * (tpr[i] + tpr[i - 1])) / 2;
  return s;
}

// ---------- bias-variance: polynomials on fresh samples of a noisy sine ----------

const legendreRow = (x, degree) => {
  // P_0..P_degree at t = 2x - 1, by the three-term recurrence.
  const t = 2 * x - 1;
  const row = [1];
  if (degree >= 1) row.push(t);
  for (let k = 1; k < degree; k++) row.push(((2 * k + 1) * t * row[k] - k * row[k - 1]) / (k + 1));
  return row;
};

export function fitLegendre(x, y, degree) {
  // Least squares polynomial in the Legendre basis on [0, 1], stable where the monomial basis is not.
  return { degree, coef: lstsq(x.map((v) => legendreRow(v, degree)), y) };
}

export function legendrePredict(m, x) {
  const row = legendreRow(x, m.degree);
  let s = 0;
  for (let k = 0; k <= m.degree; k++) s += m.coef[k] * row[k];
  return s;
}

export function decomposeBV(P, f) {
  // P: M models by G grid points, f: the truth on the grid. The grid mean stands for E_x.
  // The mean of M predictions carries its own noise variance / M, which would inflate bias^2: it is removed.
  const M = P.length;
  let bias2 = 0, biasRaw = 0, variance = 0;
  for (let j = 0; j < f.length; j++) {
    let mean = 0;
    for (let m = 0; m < M; m++) mean += P[m][j];
    mean /= M;
    let ss = 0;
    for (let m = 0; m < M; m++) ss += (P[m][j] - mean) ** 2;
    const v = ss / (M - 1);
    variance += v;
    biasRaw += (mean - f[j]) ** 2;
    bias2 += (mean - f[j]) ** 2 - v / M;
  }
  const G = f.length;
  return { bias2: bias2 / G, biasRaw: biasRaw / G, variance: variance / G };
}

export const bvTruth = (x) => Math.sin(2 * Math.PI * x);

export function makeBvStreams({ resamples, fresh, maxN, seed = 1 }) {
  // Three groups of random numbers that share nothing: `a` the training samples behind bias^2 and variance,
  // `b` other training samples for the measured error, `t` the fresh test pairs those models are scored on.
  // A stream holds x ~ U(0,1) and N(0,1) noise; the noise level scales it later, so moving a slider
  // reshapes the same draws instead of redrawing them.
  const stream = (group, i, len) => {
    const r = rng((((seed * 3 + group) * 65537 + i) * 2654435761) >>> 0);
    return { x: Array.from({ length: len }, () => r()), e: Array.from({ length: len }, () => gauss(r)) };
  };
  return {
    a: Array.from({ length: resamples }, (_, i) => stream(0, i, maxN)),
    b: Array.from({ length: resamples }, (_, i) => stream(1, i, maxN)),
    t: Array.from({ length: resamples }, (_, i) => stream(2, i, fresh)),
  };
}

export const BV_GRID = Array.from({ length: 100 }, (_, i) => (i + 0.5) / 100);

export function bvEstimate(streams, { degree, noise, n, batches = 5 }) {
  const fitOn = (s) => {
    const x = s.x.slice(0, n);
    return fitLegendre(x, x.map((v, i) => bvTruth(v) + noise * s.e[i]), degree);
  };
  const f = BV_GRID.map(bvTruth);
  const P = streams.a.map((s) => { const m = fitOn(s); return BV_GRID.map((g) => legendrePredict(m, g)); });
  const d = decomposeBV(P, f);
  // Error of models from group b on the pairs of group t: the squared error of each model, averaged over its pairs.
  const errs = streams.b.map((s, i) => {
    const m = fitOn(s), t = streams.t[i];
    return t.x.reduce((acc, x, k) => acc + (bvTruth(x) + noise * t.e[k] - legendrePredict(m, x)) ** 2, 0) / t.x.length;
  });
  const M = errs.length;
  const measured = errs.reduce((a, b) => a + b, 0) / M;
  const seMeasured = Math.sqrt(errs.reduce((a, b) => a + (b - measured) ** 2, 0) / (M - 1) / M);
  // Standard error of bias^2 + variance from batches of models: each batch is a full estimate of the same sum.
  const size = Math.floor(P.length / batches);
  const sums = Array.from({ length: batches }, (_, b) => {
    const r = decomposeBV(P.slice(b * size, (b + 1) * size), f);
    return r.bias2 + r.variance;
  });
  const meanSum = sums.reduce((a, b) => a + b, 0) / batches;
  const seSum = Math.sqrt(sums.reduce((a, b) => a + (b - meanSum) ** 2, 0) / (batches - 1) / batches);
  return { bias2: d.bias2, variance: d.variance, noise: noise * noise, sum: d.bias2 + d.variance + noise * noise, measured, seMeasured, seSum, P, f };
}

// ---------- LIME ----------

// Default kernel width of lime_tabular.py for p features, in standardised units.
export const limeDefaultWidth = (p) => 0.75 * Math.sqrt(p);

// lime_tabular.py writes sqrt(exp(-d^2 / width^2)), which is exp(-d^2 / (2 width^2)).
// The LIME paper's exp(-d^2 / sigma^2) is the same kernel at width = sigma / sqrt(2).
export const limeKernel = (d, width) => Math.exp(-(d * d) / (2 * width * width));

export function limeSample(x, scale, n, seed) {
  // Perturbations around x, as lime's sample_around_instance: z = x + scale * eps,
  // eps standard normal, scale the standard deviation of every training column.
  const r = rng(seed), E = [], Z = [];
  for (let i = 0; i < n; i++) {
    const e = x.map(() => gauss(r));
    E.push(e);
    Z.push(e.map((v, j) => x[j] + scale[j] * v));
  }
  return { E, Z };
}

export function limeWeights(Z, x, scale, width) {
  // Kernel of the Euclidean distance between standardised rows: (z - x) / scale.
  return Z.map((z) => limeKernel(Math.hypot(...z.map((v, j) => (v - x[j]) / scale[j])), width));
}

export function nEff(w) {
  // Effective number of neighbours (sum w)^2 / sum w^2: n for equal weights, 1 for one point.
  const s = w.reduce((a, b) => a + b, 0), q = w.reduce((a, b) => a + b * b, 0);
  return (s * s) / q;
}

export function weightedLinearFit(Z, x, t, w) {
  // Weighted least squares of t on z - x: intercept a (the value of g at x), coefficients
  // coef, weighted R^2. Solved on weighted-centred data, null when the weighted cloud
  // does not span the p directions.
  const p = x.length, n = Z.length;
  const sw = w.reduce((a, b) => a + b, 0);
  const zbar = x.map((_, j) => Z.reduce((s, z, i) => s + w[i] * z[j], 0) / sw);
  const tbar = t.reduce((s, v, i) => s + w[i] * v, 0) / sw;
  const S = Array.from({ length: p }, () => new Array(p).fill(0)), c = new Array(p).fill(0);
  for (let i = 0; i < n; i++) {
    const d = x.map((_, j) => Z[i][j] - zbar[j]);
    for (let j = 0; j < p; j++) {
      c[j] += w[i] * d[j] * (t[i] - tbar);
      for (let k = 0; k < p; k++) S[j][k] += w[i] * d[j] * d[k];
    }
  }
  const A = S.map((row, j) => [...row, c[j]]);
  const diag = Math.max(...S.map((row, j) => row[j]));
  for (let col = 0; col < p; col++) {
    let piv = col;
    for (let r = col + 1; r < p; r++) if (Math.abs(A[r][col]) > Math.abs(A[piv][col])) piv = r;
    if (!(Math.abs(A[piv][col]) > 1e-12 * diag) || !(sw > 0)) return null;
    [A[col], A[piv]] = [A[piv], A[col]];
    for (let r = 0; r < p; r++) {
      if (r === col) continue;
      const f = A[r][col] / A[col][col];
      for (let k = col; k <= p; k++) A[r][k] -= f * A[col][k];
    }
  }
  const coef = A.map((row, j) => row[p] / row[j]);
  const a = tbar - coef.reduce((s, cj, j) => s + cj * (zbar[j] - x[j]), 0);
  let res = 0, tot = 0;
  for (let i = 0; i < n; i++) {
    const g = a + coef.reduce((s, cj, j) => s + cj * (Z[i][j] - x[j]), 0);
    res += w[i] * (t[i] - g) ** 2;
    tot += w[i] * (t[i] - tbar) ** 2;
  }
  return { a, coef, r2: 1 - res / Math.max(tot, 1e-12) };
}

export function angleDeg(a, b) {
  const dot = a.reduce((s, v, i) => s + v * b[i], 0);
  const c = dot / (Math.hypot(...a) * Math.hypot(...b));
  return (Math.acos(Math.max(-1, Math.min(1, c))) * 180) / Math.PI;
}

export function gradientFd(f, x, h) {
  // Central difference with step h in every coordinate. For a piecewise-constant f
  // (a tree, a forest) this is the slope across a window of width 2h, not a derivative.
  return x.map((_, j) => {
    const up = x.slice(), dn = x.slice();
    up[j] += h; dn[j] -= h;
    return (f(up) - f(dn)) / (2 * h);
  });
}

export function segmentInBox(a, c, x, box, level = 0.5) {
  // Points of the line a + c . (z - x) = level inside the box [xmin, xmax, ymin, ymax].
  const [xmin, xmax, ymin, ymax] = box;
  if (Math.abs(c[1]) > Math.abs(c[0])) {
    const xs = [xmin, xmax];
    return { xs, ys: xs.map((X) => x[1] + (level - a - c[0] * (X - x[0])) / c[1]) };
  }
  const ys = [ymin, ymax];
  return { xs: ys.map((Y) => x[0] + (level - a - c[1] * (Y - x[1])) / c[0]), ys };
}

// ---------- Shapley values and SHAP ----------

// A coalition is a bit mask: bit j set means feature j is known. v[mask] is its value.
export function shapleyWeights(m) {
  // |S|! (m - |S| - 1)! / m! for |S| = 0 .. m - 1.
  const fact = (k) => (k <= 1 ? 1 : k * fact(k - 1));
  return Array.from({ length: m }, (_, s) => (fact(s) * fact(m - s - 1)) / fact(m));
}

export const popcount = (k) => { let c = 0; for (; k; k &= k - 1) c++; return c; };

export function shapleyFromValues(v, m) {
  const w = shapleyWeights(m), phi = new Array(m).fill(0);
  for (let i = 0; i < m; i++) {
    for (let S = 0; S < 1 << m; S++) {
      if ((S >> i) & 1) continue;
      phi[i] += w[popcount(S)] * (v[S | (1 << i)] - v[S]);
    }
  }
  return phi;
}

export function shapleyOrders(v, m) {
  // The same values as the mean over all m! orders of the gain at the moment of arrival.
  // orders in lexicographic order, inc[k][i] the gain of feature i in order k.
  const orders = [];
  const walk = (cur) => {
    if (cur.length === m) { orders.push(cur); return; }
    for (let i = 0; i < m; i++) if (!cur.includes(i)) walk([...cur, i]);
  };
  walk([]);
  const inc = orders.map((o) => {
    const row = new Array(m).fill(0);
    let mask = 0;
    for (const i of o) { row[i] = v[mask | (1 << i)] - v[mask]; mask |= 1 << i; }
    return row;
  });
  const phi = new Array(m).fill(0);
  inc.forEach((row) => row.forEach((g, i) => (phi[i] += g / orders.length)));
  return { orders, inc, phi };
}

export function interventionalValues(predict, x, background) {
  // v(S) = mean over background rows b of f(x_S, b_rest): the features outside S are
  // taken from the background, which breaks their dependence on the features in S.
  const m = x.length, v = new Array(1 << m);
  for (let S = 0; S < 1 << m; S++) {
    let s = 0;
    for (const b of background) s += predict(b.map((bj, j) => ((S >> j) & 1 ? x[j] : bj)));
    v[S] = s / background.length;
  }
  return v;
}

export function treeCoalitionValues(model, x) {
  // v(S) = E[f | x_S] of a boosting model by the rule of lecture slide 27: at a split on a
  // feature outside S go both ways, weighted by the training counts n of the children.
  const m = x.length, v = new Array(1 << m);
  const walk = (t, S) => {
    if (!t.left) return t.value;
    if ((S >> t.feature) & 1) return walk(x[t.feature] <= t.threshold ? t.left : t.right, S);
    return (t.left.n * walk(t.left, S) + t.right.n * walk(t.right, S)) / t.n;
  };
  for (let S = 0; S < 1 << m; S++) v[S] = model.f0 + model.lr * model.trees.reduce((s, t) => s + walk(t, S), 0);
  return v;
}

export function makeShapData(n, seed, { rho = 0.9 } = {}) {
  // Four features: x1 ~ N(0,1), x2 correlated with x1 by rho, x3 and x4 independent.
  // The target uses x1, x2 and the product x3 x4, so a pair of correlated features and a pair
  // that matters only together are both present.
  const r = rng(seed), X = [], y = [];
  for (let i = 0; i < n; i++) {
    const x1 = gauss(r), z2 = gauss(r), x3 = gauss(r), x4 = gauss(r), e = gauss(r);
    const x2 = rho * x1 + Math.sqrt(1 - rho * rho) * z2;
    X.push([x1, x2, x3, x4]);
    y.push(SHAP_TRUTH([x1, x2, x3, x4]) + SHAP_NOISE * e);
  }
  return { X, y };
}

export const SHAP_TRUTH = (x) => 2 * x[0] + x[1] + x[2] * x[3];
export const SHAP_TRUTH_TEXT = "2x₁ + x₂ + x₃x₄";
export const SHAP_NOISE = 0.3;
