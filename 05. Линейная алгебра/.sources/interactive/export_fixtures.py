"""Reference answers for the tests of lacore.js, written to fixtures.json.

Each answer comes from a method other than the one lacore.js uses (one-sided Jacobi):
  singular values   scipy.linalg.svd with the LAPACK driver gesvd (QR iteration on a bidiagonal form)
  rank              numpy.linalg.matrix_rank
  best rank-k       the truncated sum from that decomposition, only for k with a gap rho_k > rho_{k+1},
                    where the best matrix in the sense of the largest singular value is the one from the note
  errors            numpy.linalg.norm(A - X, 2), computed by numpy's own driver (gesdd), and max |a_ij - x_ij|
  competitors       random matrices Y of rank k with the norm of A - Y: Eckart-Young says none beats rho_{k+1}

2 x 2 matrices ("mat2"):
  eigenvalues       numpy.linalg.eigvals (LAPACK geev), det and trace from numpy
  multiplicities    sympy exact eigenvects over the rationals: the algebraic multiplicity of each root
                    and the dimension of its eigenspace, no rounding involved

Point clouds ("pca"):
  covariance        numpy.cov (the divisor N - 1), the mean from numpy.mean
  principal axes    numpy.linalg.eigh of that covariance, reordered by decreasing eigenvalue
  least squares     numpy.polyfit of degree 1 (y on x)
  sums of squares   perpendiculars to the first-component line: by cross products and as rho_2^2 of the SVD of the centred data;
                    vertical deviations and perpendiculars of both lines by numpy arithmetic

The parser, the quadrature and the eigenvalue solver are numkit's: its fixtures are numkit/export_fixtures.py,
and the sympy helpers below come from there.

Usage: python export_fixtures.py   (writes fixtures.json next to this file)
"""
import json
import sys
from pathlib import Path

import numpy as np
import scipy.integrate
import scipy.linalg
import sympy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import course  # noqa: E402,F401  (puts the vault's scripts on sys.path)
from numkit import export_fixtures as nk  # noqa: E402

X, T, LAM, sym, fn = nk.X, nk.T, nk.LAM, nk.sym, nk.fn
RNG = np.random.default_rng(20261021)


def rand(m, n):
    return RNG.standard_normal((m, n))


def orth(m, n):
    return nk.orth(RNG, m, n)


def matrices():
    out = {}
    out["note-3x2"] = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    out["scalar"] = np.array([[-3.0]])
    out["random-5x3"] = rand(5, 3)
    out["random-3x5"] = rand(3, 5)
    out["random-8x8"] = rand(8, 8)
    out["tall-30x7"] = rand(30, 7)
    out["wide-7x30"] = rand(7, 30)
    out["column-6x1"] = rand(6, 1)
    out["row-1x6"] = rand(1, 6)
    out["identity-4"] = np.eye(4)
    out["ones-5x5"] = np.ones((5, 5))
    out["zeros-3x4"] = np.zeros((3, 4))
    out["rank2-6x4"] = rand(6, 2) @ rand(2, 4)
    out["rank1-5x5"] = np.outer(rand(5, 1).ravel(), rand(5, 1).ravel())
    out["rank3-4x9"] = rand(4, 3) @ rand(3, 9)
    out["repeated-3x3"] = orth(3, 3) @ np.diag([3.0, 3.0, 1.0]) @ orth(3, 3).T
    out["hilbert-8"] = np.array([[1.0 / (i + j + 1) for j in range(8)] for i in range(8)])
    out["decay-40x25"] = orth(40, 25) @ np.diag(2.0 ** -np.arange(25)) @ orth(25, 25).T
    out["wide-decay-12x50"] = orth(12, 12) @ np.diag(3.0 ** -np.arange(12)) @ orth(50, 12).T
    out["scaled-1e6-4x4"] = 1e6 * rand(4, 4)
    out["scaled-1e-6-4x6"] = 1e-6 * rand(4, 6)
    return out


def case(name, a):
    m, n = a.shape
    p = min(m, n)
    rho = scipy.linalg.svd(a, compute_uv=False, lapack_driver="gesvd")
    rank = int(np.linalg.matrix_rank(a))
    c = {"name": name, "m": m, "n": n, "a": a.ravel().tolist(), "rho": rho.tolist(), "rank": rank}
    u, s, vt = scipy.linalg.svd(a, lapack_driver="gesvd")
    approx = []
    for k in range(1, p + 1):
        gap = s[k - 1] - (s[k] if k < p else 0.0)
        if gap <= 1e-9 * max(s[0], 1e-300):
            continue
        x = (u[:, :k] * s[:k]) @ vt[:k, :]
        entry = {
            "k": k,
            "x": x.ravel().tolist(),
            "spectral": float(np.linalg.norm(a - x, 2)),
            "maxdiff": float(np.abs(a - x).max()),
            "competitors": [],
        }
        if k < p:
            for _ in range(4):
                y = rand(m, k) @ rand(k, n) * (s[0] / max(m, n))
                entry["competitors"].append(float(np.linalg.norm(a - y, 2)))
        approx.append(entry)
    c["approx"] = approx
    return c


def mat2_cases():
    """Presets of the page, special shapes and random matrices; rational entries get exact multiplicities."""
    rational = {
        "identity": [[1, 0], [0, 1]], "scalar-3": [[3, 0], [0, 3]], "zero": [[0, 0], [0, 0]],
        "stretch": [[2, 0], [0, 1]], "shear": [[1, 1], [0, 1]], "jordan-2": [[2, 1], [0, 2]],
        "reflection": [[1, 0], [0, -1]], "singular": [[1, 2], [2, 4]], "nilpotent": [[0, 1], [0, 0]],
        "rotation-90": [[0, -1], [1, 0]], "rotation-scaled": [[1, -1], [1, 1]], "diagonalisable": [[4, 1], [2, 3]],
        "lower-jordan": [[-5, 0], [3, -5]], "swap": [[0, 1], [1, 0]], "negative-det": [[1, 2], [3, 0]],
        "projection": [[1, 0], [1, 0]], "irrational-roots": [[1, 1], [1, 0]], "repeated-full-rank-shift": [[3, -1], [1, 1]],
    }
    out = []
    for name, rows in rational.items():
        m = sympy.Matrix(rows)
        entries = []
        for value, alg, vectors in m.eigenvects():
            entries.append({"re": float(sympy.re(value)), "im": float(sympy.im(value)), "alg": int(alg), "geom": len(vectors)})
        out.append({"name": name, "m": [float(x) for x in m], "exact": entries,
                    "numpy": [[float(z.real), float(z.imag)] for z in np.linalg.eigvals(np.array(rows, float))],
                    "det": float(np.linalg.det(np.array(rows, float))), "tr": float(np.trace(np.array(rows, float)))})
    for i in range(60):
        a = RNG.standard_normal((2, 2)) * (10.0 ** RNG.integers(-3, 4))
        out.append({"name": f"random-{i}", "m": a.ravel().tolist(), "exact": None,
                    "numpy": [[float(z.real), float(z.imag)] for z in np.linalg.eigvals(a)],
                    "det": float(np.linalg.det(a)), "tr": float(np.trace(a))})
    return out


def fredholm_numbers(p):
    """A, the vector f_m and Delta samples of a preset from scipy's QUADPACK and numpy."""
    lo, hi = float(sym(p["lo"])), float(sym(p["hi"]))
    al = [fn(sym(r[0]), X) for r in p["rows"]]
    be = [fn(sym(r[1]), T) for r in p["rows"]]
    f = fn(sym(p["f"]), X)
    n = len(al)

    def quad(g):
        return scipy.integrate.quad(g, lo, hi, epsabs=1e-14, epsrel=1e-13, limit=500, points=[0.5 * (lo + hi)])[0]

    a = np.array([[quad(lambda t, k=k, m=m: al[k](t) * be[m](t)) for m in range(n)] for k in range(n)])
    fv = np.array([quad(lambda t, m=m: be[m](t) * f(t)) for m in range(n)])
    return lo, hi, al, be, f, a, fv


def characteristic_groups(a, keep):
    """The characteristic numbers 1/mu of the nonzero eigenvalues of A, equal ones grouped, with the
    multiplicity and the rank of I - lambda A^T from numpy's SVD-based matrix_rank (complex arithmetic)."""
    n = a.shape[0]
    groups = []
    for z in keep:
        for g in groups:
            if abs(g["mu"] - z) <= 1e-6 * abs(z):
                g["alg"] += 1
                break
        else:
            groups.append({"mu": z, "alg": 1})
    out = []
    for g in groups:
        lam = 1 / g["mu"]
        m = np.eye(n) - lam * a.T
        # the rule of the page: a singular value is zero below 1e-5 (1 + |lambda| ||A||_1), the size of the matrix,
        # not 1e-5 of its largest singular value, which for M = 0 + noise is noise itself
        rank = n - int(np.linalg.matrix_rank(m, tol=1e-5 * (1 + abs(lam) * np.abs(a).sum(axis=0).max())))
        out.append({"lambda": [float(lam.real), float(lam.imag)], "alg": g["alg"], "rank": rank})
    return out


def fredholm_cases():
    presets = json.loads((HERE / "presets.json").read_text(encoding="utf-8"))
    out = []
    for p in presets:
        lo, hi, al, be, f, a, fv = fredholm_numbers(p)
        n = len(al)
        lam = float(sym(p["lambda"]))
        c = {"id": p["id"], "lo": lo, "hi": hi, "n": n, "lam": lam, "A": a.ravel().tolist(), "fv": fv.tolist()}
        c["delta"] = [{"lam": s, "value": float(np.linalg.det(np.eye(n) - s * a))} for s in (-3.0, -1.0, -0.4, 0.3, 0.9, 2.5)]
        mu = np.linalg.eigvals(a)
        keep = [z for z in mu if abs(z) > 1e-6 * np.abs(a).sum(axis=0).max()]
        c["mu"] = [[float(z.real), float(z.imag)] for z in mu]
        c["characteristic"] = [[float((1 / z).real), float((1 / z).imag)] for z in keep]
        c["groups"] = characteristic_groups(a, keep)
        if "solve" in p["pages"]:
            xs = [lo + (hi - lo) * s for s in (0.07, 0.23, 0.41, 0.5, 0.66, 0.83, 0.95)]
            coef = np.linalg.solve(np.eye(n) - lam * a.T, fv)
            c["xs"] = xs
            c["C"] = coef.tolist()
            c["phi"] = [f(x) + lam * sum(coef[k] * al[k](x) for k in range(n)) for x in xs]
            answer = sym(p["answer"]).subs(LAM, sympy.Float(p["lambda"]))
            g = fn(answer, X)
            c["answer"] = [g(x) for x in xs]
            c["note_delta"] = None
        out.append(c)
    return out


def pca_clouds():
    """Point clouds of the PCA page: the note's example, random clouds, scaled and shifted ones, and the degenerate ones."""
    def blob(n, sx, sy, deg, shift=(0.0, 0.0)):
        z = RNG.standard_normal((n, 2)) * [sx, sy]
        t = np.deg2rad(deg)
        r = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        return z @ r.T + shift

    ring = [[np.cos(2 * np.pi * i / 8), np.sin(2 * np.pi * i / 8)] for i in range(8)]
    out = {
        "note-four-points": np.array([[2.0, 2.0], [-2.0, -2.0], [1.0, -1.0], [-1.0, 1.0]]),
        "random-3": blob(3, 2.0, 0.5, 20),
        "random-10": blob(10, 3.0, 1.0, -35),
        "random-50": blob(50, 4.0, 1.0, 30),
        "random-200": blob(200, 1.0, 5.0, 75),
        "random-1000-wide": blob(1000, 6.0, 2.0, 110),
        "shifted-1000": blob(40, 2.0, 0.7, 15, (1000.0, -500.0)),
        "tiny-1e-6": blob(30, 2.0, 0.7, 40) * 1e-6,
        "huge-1e5": blob(30, 2.0, 0.7, 40) * 1e5,
        "nearly-round": blob(500, 1.0, 1.0005, 10),
        "line-diagonal": np.array([[x, 2.0 * x + 1.0] for x in (-2.0, -1.0, 0.0, 0.5, 1.5, 3.0)]),
        "line-horizontal": np.array([[x, 3.0] for x in (-2.0, 0.0, 1.0, 4.0)]),
        "line-vertical": np.array([[2.0, y] for y in (-1.0, 0.0, 2.5, 4.0)]),
        "round-square": np.array([[1.0, 1.0], [1.0, -1.0], [-1.0, 1.0], [-1.0, -1.0]]),
        "round-ring-8": np.array(ring),
        "single-point": np.array([[3.0, -2.0]]),
        "two-points": np.array([[1.0, 2.0], [4.0, 6.0]]),
        "two-points-vertical": np.array([[1.0, 2.0], [1.0, 6.0]]),
        "same-points": np.array([[1.5, -2.5]] * 3),
    }
    # exact lines with irrational slopes: det C is zero only in exact arithmetic, and rounding gives it either sign
    for i in range(12):
        slope, shift = RNG.standard_normal(2) * 3
        xs = RNG.standard_normal(7) * 2
        out[f"line-random-{i}"] = np.column_stack([xs, slope * xs + shift])
    # round clouds that are round only up to rounding: a ring turned by a float angle
    for i, deg in enumerate((17.0, 37.0, 71.3)):
        t = np.deg2rad(deg)
        r = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        out[f"round-turned-{i}"] = np.array(ring) @ r.T
    return out


def pca_case(name, pts):
    """Reference for one cloud: np.cov, np.linalg.eigh, np.polyfit, and the sums of squares by cross products and by the SVD of the centred data."""
    n = len(pts)
    mean = pts.mean(axis=0)
    c = {"name": name, "pts": pts.tolist(), "mean": mean.tolist(), "cov": None, "lam": None, "w": None, "gap": None,
         "poly": None, "perp_svd": None, "pc_line": None, "ols_line": None}
    if n < 2:
        return c
    cov = np.cov(pts, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    lam = vals[::-1].clip(min=0.0)
    w = vecs[:, ::-1].T
    c["cov"] = cov.ravel().tolist()
    c["lam"] = lam.tolist()
    c["w"] = w.tolist()
    c["gap"] = float((lam[0] - lam[1]) / lam[0]) if lam[0] > 0 else 0.0
    c["perp_svd"] = float(np.linalg.svd(pts - mean, compute_uv=False)[-1] ** 2)

    def sums(direction):
        d = direction / np.linalg.norm(direction)
        diff = pts - mean
        perp = float(np.sum((diff[:, 0] * d[1] - diff[:, 1] * d[0]) ** 2))
        vert = None if abs(d[0]) < 1e-12 else float(np.sum((diff[:, 1] - d[1] / d[0] * diff[:, 0]) ** 2))
        return {"perp": perp, "vert": vert}

    c["pc_line"] = sums(w[0])
    if np.ptp(pts[:, 0]) > 0:
        slope, intercept = np.polyfit(pts[:, 0], pts[:, 1], 1)
        c["poly"] = [float(slope), float(intercept)]
        c["ols_line"] = sums(np.array([1.0, slope]))
    return c


def pca_cases():
    return [pca_case(name, pts) for name, pts in pca_clouds().items()]


def main():
    data = {"matrices": [case(name, a) for name, a in matrices().items()], "mat2": mat2_cases(),
            "fredholm": fredholm_cases(), "pca": pca_cases()}
    (HERE / "fixtures.json").write_text(json.dumps(data), encoding="utf-8")
    print({"matrices": len(data["matrices"]), "approximations": sum(len(c["approx"]) for c in data["matrices"]),
           "mat2": len(data["mat2"]), "fredholm": len(data["fredholm"]), "pca": len(data["pca"])})


if __name__ == "__main__":
    main()
