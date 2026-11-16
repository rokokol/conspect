"""Reference answers for the tests of nmcore.js, written to fixtures.json (not in git: run this first).

Each answer comes from a method other than the one nmcore.js uses:
  iterations (page "iterations")
    transition matrix S   numpy.linalg.solve(B, A) from the canonical form, B built with numpy.tril / numpy.diag
    rho, ||S||_inf       numpy.linalg.eigvals (LAPACK geev), numpy.linalg.norm(S, inf)
    iterates              the canonical form x + tau * solve(B, b - A x), not the componentwise formulas of nmcore.js
    exact solution        numpy.linalg.solve
    dominance q           numpy row sums
    positive definite     numpy.linalg.eigvalsh of the symmetric matrix, smallest eigenvalue > 1e-9
    Samarsky (2.13)       eigvalsh of B1 - tau/2 A
    best omega, best tau  scipy.optimize.minimize_scalar (bounded) around the best node of a fine numpy grid;
                          tau0 = 2/(M+m) from eigvalsh

  second kind (page "second-kind")
    Gauss-Legendre        numpy.polynomial.legendre.leggauss
    Taylor coefficients   sympy: diff(expr, x, k) at the centre over k!, lambdified
    quadratures           numpy solve of I - lam K D with the weights from scipy.integrate.trapezoid / simpson
                          applied to unit vectors; Volterra rows by scipy.optimize.fsolve for the nonlinear step
    simple iteration      numpy: the matrix B and the same stopping rule
    degenerate kernels    scipy.integrate.quad of the sympy coefficient functions, numpy solve
    Galerkin, collocation scipy.integrate.quad / dblquad of numpy.polynomial bases, numpy solve, numpy.linalg.cond(M, 1)
    reference solutions   the exact formulas of the notes

Usage: python export_fixtures.py   (writes fixtures.json next to this file)
"""
import json
import math
from pathlib import Path

import numpy as np
import scipy.integrate as sint
import sympy
from numpy.polynomial import chebyshev as npcheb
from numpy.polynomial import legendre as npleg
from scipy.optimize import fsolve, minimize_scalar

HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261022)


def tridiag(n):
    return 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)


def cases():
    out = {}
    out["note-3x3"] = (np.array([[4.0, 1, 1], [1, 5, 2], [0, 2, 4]]), np.array([9.0, 17, 16]))
    out["tridiag-3"] = (tridiag(3), tridiag(3) @ np.ones(3))
    out["tridiag-5"] = (tridiag(5), tridiag(5) @ np.ones(5))
    out["tridiag-20"] = (tridiag(20), tridiag(20) @ np.ones(20))
    pd = 0.8 * np.ones((3, 3)) + 0.2 * np.eye(3)
    out["pd-08"] = (pd, pd @ np.ones(3))
    p2 = np.array([[1.0, 0.9], [0.9, 1.0]])
    out["strong-2x2"] = (p2, p2 @ np.array([1.0, 2.0]))
    # random: a dominant one, a symmetric positive definite one, a general one (may diverge), a non-symmetric 4x4
    d = RNG.standard_normal((4, 4))
    d += np.diag(np.abs(d).sum(1) * 1.5)
    out["random-dominant-4"] = (d, d @ np.array([1.0, -2, 3, 0.5]))
    g = RNG.standard_normal((5, 5))
    spd = g @ g.T + 0.3 * np.eye(5)
    out["random-spd-5"] = (spd, spd @ np.arange(1.0, 6))
    a3 = RNG.standard_normal((3, 3)) + 2 * np.eye(3)
    out["random-general-3"] = (a3, a3 @ np.array([2.0, 1, -1]))
    a4 = RNG.standard_normal((4, 4)) + 3 * np.eye(4)
    out["random-general-4"] = (a4, a4 @ np.array([1.0, 1, 1, 1]))
    return out


def canonical(A, method, omega=1.0, tau=1.0):
    D = np.diag(np.diag(A))
    Lo = np.tril(A, -1)
    n = len(A)
    if method == "jacobi":
        return D, 1.0
    if method == "seidel":
        return D + Lo, 1.0
    if method == "relax":
        return D + omega * Lo, omega
    return np.eye(n), tau


def rho_of(A, method, **p):
    B, tau = canonical(A, method, **p)
    S = np.eye(len(A)) - tau * np.linalg.solve(B, A)
    return np.abs(np.linalg.eigvals(S)).max()


def config(A, b, x0, method, **p):
    n = len(A)
    B, tau = canonical(A, method, **p)
    S = np.eye(n) - tau * np.linalg.solve(B, A)
    x = x0.copy()
    xs = [x.tolist()]
    for _ in range(30):
        x = x + tau * np.linalg.solve(B, b - A @ x)
        xs.append(x.tolist())
    sym = np.allclose(A, A.T)
    pos = sym and np.linalg.eigvalsh(A).min() > 1e-9
    samarsky = None
    if pos:
        B1 = (B + B.T) / 2
        samarsky = bool(np.linalg.eigvalsh(B1 - tau / 2 * A).min() > 1e-9)
    return {
        "method": method, **p, "S": S.ravel().tolist(), "rho": float(np.abs(np.linalg.eigvals(S)).max()),
        "normInf": float(np.linalg.norm(S, np.inf)), "iterates": xs, "samarsky": samarsky,
    }


def best_parameter(A, method, lo, hi):
    key = "omega" if method == "relax" else "tau"
    grid = np.linspace(lo, hi, 4001)
    vals = np.array([rho_of(A, method, **{key: p}) for p in grid])
    i = int(vals.argmin())
    res = minimize_scalar(lambda p: rho_of(A, method, **{key: p}), bounds=(grid[max(i - 1, 0)], grid[min(i + 1, 4000)]), method="bounded", options={"xatol": 1e-12})
    return {"param": float(res.x), "rho": float(res.fun)}


# ---------------------------------------------------------------- equations of the second kind

XS_, SS_, YS_ = sympy.symbols("x s y", real=True)
LOCALS = {
    "x": XS_, "s": SS_, "y": YS_, "pi": sympy.pi, "e": sympy.E, "ln": sympy.log, "log": sympy.log, "tg": sympy.tan, "tan": sympy.tan,
    "abs": sympy.Abs, "sh": sympy.sinh, "ch": sympy.cosh, "th": sympy.tanh, "arcsin": sympy.asin, "arctg": sympy.atan,
}


def sym(text):
    from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations
    return parse_expr(text, local_dict=LOCALS, transformations=standard_transformations + (convert_xor,))


def lam2(expr, *vars_):
    f = sympy.lambdify(vars_, expr, "numpy")
    return lambda *a: np.asarray(f(*a), dtype=float) + 0 * np.asarray(a[0], dtype=float)


PI = math.pi
SPECS = {
    "periodic": dict(kind="fredholm", lo=-PI, hi=PI, kernel="1/(0.64*cos((x+s)/2)^2-1)", f="25-16*sin(x)^2", lam=3 / (10 * PI), exact="17/2+128/17*cos(2*x)"),
    "xs": dict(kind="fredholm", lo=0.0, hi=1.0, kernel="x*s", f="5*x/6", lam=0.5, exact="x"),
    "volterra-exp": dict(kind="volterra", lo=0.0, hi=1.0, kernel="exp(-(x-s))", f="exp(-x)", lam=1.0, exact="1"),
    "volterra-sin": dict(kind="volterra", lo=0.0, hi=2 * PI, kernel="x-s", f="x", lam=-1.0, exact="sin(x)"),
    "volterra-nl": dict(kind="volterra-nonlinear", lo=0.0, hi=0.1, kernel="exp(-(x-s))*y^2", f="exp(-x)", lam=1.0, exact="1"),
    "volterra-nl2": dict(kind="volterra-nonlinear", lo=0.0, hi=0.4, kernel="exp(-(x-s))*y^2", f="2*exp(-x)", lam=1.0, exact="1/(1-0.5*exp(x))"),
    "degenerate-exp": dict(kind="fredholm", lo=0.0, hi=1.0, kernel="x*(exp(x*s)-1)", f="exp(x)-x", lam=-1.0, exact="1"),
    "degenerate-gauss": dict(kind="fredholm", lo=0.0, hi=0.5, kernel="exp(-x^2*s^2)", f="1", lam=1.0, exact=""),
    "galerkin-xs": dict(kind="fredholm", lo=-1.0, hi=1.0, kernel="x*s+x^2", f="1", lam=1.0, exact="1+6*x^2"),
    "exp-xs": dict(kind="fredholm", lo=0.0, hi=1.0, kernel="exp(x*s)", f="exp(x)-(exp(x+1)-1)/(x+1)", lam=1.0, exact="exp(x)"),
    "exp-xs-sym": dict(kind="fredholm", lo=-1.0, hi=1.0, kernel="exp(x*s)", f="exp(x)-(exp(x+1)-exp(-(x+1)))/(x+1)", lam=1.0, exact="exp(x)"),
    "collocation-sin": dict(kind="fredholm", lo=0.0, hi=PI, kernel="sin(s)+cos(x)", f="exp(x)-(1+exp(pi))/2+(1-exp(pi))*cos(x)", lam=1.0, exact="exp(x)"),
    "collocation-x2s2": dict(kind="fredholm", lo=0.0, hi=1.0, kernel="x^2*s^2", f="x", lam=4.0, exact="x+5*x^2"),
}


def parts(spec):
    nl = spec["kind"] == "volterra-nonlinear"
    K = lam2(sym(spec["kernel"]), XS_, SS_, YS_) if nl else lam2(sym(spec["kernel"]), XS_, SS_)
    return K, lam2(sym(spec["f"]), XS_), (lam2(sym(spec["exact"]), XS_) if spec["exact"] else None)


def unit_weights(x, rule):
    """Weights of a rule on the nodes x, found by integrating the unit vectors with scipy."""
    n = len(x)
    eye = np.eye(n)
    if rule == "trapezoid":
        return np.array([sint.trapezoid(eye[j], x) for j in range(n)])
    return np.array([sint.simpson(eye[j], x=x) for j in range(n)])


def fred_quad(spec, n, rule):
    K, f, _ = parts(spec)
    x = np.linspace(spec["lo"], spec["hi"], n)
    w = unit_weights(x, rule)
    M = np.eye(n) - spec["lam"] * K(x[:, None], x[None, :]) * w[None, :]
    return x, np.linalg.solve(M, f(x)), M


def volterra_row_weights(x, m, rule):
    n = m + 1
    eye = np.eye(n)
    if rule == "trapezoid" or m == 1:
        return np.array([sint.trapezoid(eye[j], x[:n]) for j in range(n)])
    if m % 2 == 0:
        return np.array([sint.simpson(eye[j], x=x[:n]) for j in range(n)])
    return np.array([sint.simpson(eye[j][:m], x=x[:m]) + sint.trapezoid(eye[j][m - 1:], x[m - 1:n]) for j in range(n)])


def volterra_solve(spec, n, rule):
    K, f, _ = parts(spec)
    nl = spec["kind"] == "volterra-nonlinear"
    x = np.linspace(spec["lo"], spec["hi"], n)
    y = np.zeros(n)
    y[0] = f(x[0])
    lam = spec["lam"]
    for m in range(1, n):
        w = volterra_row_weights(x, m, rule)
        if nl:
            c = f(x[m]) + lam * sum(w[j] * K(x[m], x[j], y[j]) for j in range(m))
            y[m] = fsolve(lambda t: t - c - lam * w[m] * K(x[m], x[m], t), y[m - 1], xtol=1e-14)[0]
        else:
            s = sum(w[j] * K(x[m], x[j]) * y[j] for j in range(m))
            y[m] = (f(x[m]) + lam * s) / (1 - lam * w[m] * K(x[m], x[m]))
    return x, y


def simple_iteration(spec, n, tol, max_iter=1000):
    K, f, _ = parts(spec)
    x = np.linspace(spec["lo"], spec["hi"], n)
    vol = spec["kind"] != "fredholm"
    nl = spec["kind"] == "volterra-nonlinear"
    W = np.zeros((n, n))
    for i in range(n):
        w = volterra_row_weights(x, i, "trapezoid") if vol and i > 0 else (np.zeros(0) if vol else unit_weights(x, "trapezoid"))
        W[i, :len(w)] = w
    B = None if nl else spec["lam"] * W * K(x[:, None], x[None, :])
    fx = f(x)
    y = fx.copy()
    for k in range(1, max_iter + 1):
        new = fx + (B @ y if not nl else np.array([spec["lam"] * sum(W[i, j] * K(x[i], x[j], y[j]) for j in range(n)) for i in range(n)]))
        if vol:
            new[0] = fx[0]
        diff, nrm = np.abs(new - y).max(), np.abs(new).max()
        y = new
        if not math.isfinite(nrm) or nrm > 1e150:
            return dict(y=None, iterations=k, converged=False, diverged=True)
        if diff <= tol * nrm:
            return dict(y=y.tolist(), iterations=k, converged=True, diverged=False)
    return dict(y=y.tolist(), iterations=max_iter, converged=False, diverged=False)


def probe(spec, count=11):
    return np.linspace(spec["lo"], spec["hi"], count)


def second_kind():
    out = {"specs": SPECS}
    # Gauss-Legendre
    out["gauss"] = [{"n": n, "x": npleg.leggauss(n)[0].tolist(), "w": npleg.leggauss(n)[1].tolist()} for n in (1, 2, 3, 5, 8, 16, 33)]
    # Taylor coefficients
    jets = []
    for text, x0 in [("x*(exp(x*s)-1)", 0.0), ("exp(-x^2*s^2)", 0.0), ("sin(x+s)", 0.3), ("s/(1+25*x^2)", 0.0), ("log(2+x*s)", 0.0),
                     ("sqrt(1+x*s)", 0.0), ("cos(x*s)/(2+x)", 0.0), ("atan(x*s)+x", 0.0), ("asin(x*s/2)", 0.0), ("tanh(x+s)", 0.2),
                     ("abs(x+2)*s", 0.0), ("(x+s)^3", 0.5), ("x^s", 1.0), ("1/(x+s)", 1.0), ("exp(x)*cos(s*x)", 0.0), ("(x-1)^2.5*s", 2.0),
                     ("cosh(x*s)-x^4", 0.0), ("x^(-2)*s", 1.5), ("2^(x*s)", 0.0)]:
        expr = sym(text)
        D = 8
        svals = [0.3, 0.7, -0.4, 1.1]
        coef = []
        for s in svals:
            row = []
            for k in range(D + 1):
                d = sympy.diff(expr.subs(SS_, s), XS_, k).subs(XS_, x0) / math.factorial(k)
                row.append(float(sympy.N(d, 30)))
            coef.append(row)
        jets.append({"text": text, "x0": x0, "D": D, "s": svals, "coef": coef})
    out["jets"] = jets
    # quadratures
    quad = []
    for name, rules, ns in [("periodic", ("trapezoid",), (5, 9, 13, 17, 25, 37)), ("periodic", ("simpson",), (25, 37, 49)), ("xs", ("trapezoid", "simpson"), (3, 5, 9, 11))]:
        for rule in rules:
            for n in ns:
                x, y, M = fred_quad(SPECS[name], n, rule)
                quad.append({"spec": name, "rule": rule, "n": n, "x": x.tolist(), "y": y.tolist(), "cond1": float(np.linalg.cond(M, 1)), "matrix": M.ravel().tolist() if n <= 13 else None})
    out["quadrature"] = quad
    vq = []
    for name, rules, ns in [("volterra-exp", ("trapezoid", "simpson"), (2, 3, 4, 5, 6, 7, 8, 21)), ("volterra-sin", ("trapezoid", "simpson"), (9, 10, 33)), ("volterra-nl", ("trapezoid",), (6, 11)),
                            ("volterra-nl", ("simpson",), (6, 7)), ("volterra-nl2", ("trapezoid",), (9, 17))]:
        for rule in rules:
            for n in ns:
                x, y = volterra_solve(SPECS[name], n, rule)
                vq.append({"spec": name, "rule": rule, "n": n, "x": x.tolist(), "y": y.tolist()})
    out["volterra"] = vq
    it = []
    for name, n, tol in [("periodic", 13, 1e-8), ("xs", 9, 1e-10), ("volterra-exp", 11, 1e-8), ("volterra-sin", 41, 1e-6), ("volterra-nl", 6, 1e-10), ("galerkin-xs", 9, 1e-6), ("exp-xs", 11, 1e-9)]:
        it.append({"spec": name, "n": n, "tol": tol, **simple_iteration(SPECS[name], n, tol)})
    # a divergent iteration: large lambda
    big = dict(SPECS["xs"], lam=10.0)
    out["specs"]["xs-big"] = big
    it.append({"spec": "xs-big", "n": 9, "tol": 1e-8, **simple_iteration(big, 9, 1e-8)})
    out["iteration"] = it
    # degenerate kernels
    deg = []
    for name, x0 in [("degenerate-exp", 0.0), ("degenerate-gauss", 0.0)]:
        spec = SPECS[name]
        K, f, exact = parts(spec)
        expr = sym(spec["kernel"])
        kappa = []
        for k in range(0, 24):
            c = sympy.simplify(sympy.diff(expr, XS_, k).subs(XS_, x0) / math.factorial(k))
            if c != 0:
                kappa.append((k, c))
        ref_y = exact if exact else None
        if ref_y is None:
            g = npleg.leggauss(60)
            xs_n = 0.5 * (spec["hi"] - spec["lo"]) * g[0] + 0.5 * (spec["hi"] + spec["lo"])
            ws_n = 0.5 * (spec["hi"] - spec["lo"]) * g[1]
            Mn = np.eye(60) - spec["lam"] * K(xs_n[:, None], xs_n[None, :]) * ws_n[None, :]
            yn = np.linalg.solve(Mn, f(xs_n))
            ref_y = lambda t, yn=yn, xs_n=xs_n, ws_n=ws_n: f(t) + spec["lam"] * (K(np.asarray(t)[..., None], xs_n) * ws_n * yn).sum(-1)
        px = probe(spec, 41)
        for M in range(1, 8 if name == "degenerate-gauss" else 7):
            degs = [k for k, _ in kappa[:M]]
            betas = [lam2(c, SS_) for _, c in kappa[:M]]
            a = np.array([[sint.quad(lambda s: float(betas[i](s)) * (s - x0) ** degs[j], spec["lo"], spec["hi"], epsabs=1e-14, epsrel=1e-14)[0] for j in range(M)] for i in range(M)])
            fv = np.array([sint.quad(lambda s: float(betas[i](s)) * float(f(s)), spec["lo"], spec["hi"], epsabs=1e-14, epsrel=1e-14)[0] for i in range(M)])
            Mx = np.eye(M) - spec["lam"] * a
            c = np.linalg.solve(Mx, fv)
            y = np.asarray(f(px)) + spec["lam"] * sum(c[i] * (px - x0) ** degs[i] for i in range(M))
            err = float(np.abs(y - ref_y(px)).max())
            xs41 = np.linspace(spec["lo"], spec["hi"], 41)
            def rown(g):
                return max(sint.quad(lambda s: abs(g(x_, s)), spec["lo"], spec["hi"], epsabs=1e-12, epsrel=1e-10)[0] for x_ in xs41)
            kern = lambda x_, s: float(K(x_, s))
            part = lambda x_, s: sum(float(betas[i](s)) * (x_ - x0) ** degs[i] for i in range(M))
            normA, normDiff = rown(kern), rown(lambda x_, s: kern(x_, s) - part(x_, s))
            deg.append({"spec": name, "M": M, "degrees": degs, "c": c.tolist(), "a": a.ravel().tolist(), "error": err, "cond1": float(np.linalg.cond(Mx, 1)),
                        "normA": normA, "normDiff": normDiff, "y": y.tolist(), "px": px.tolist()})
    out["degenerate"] = deg
    # Galerkin and collocation
    def basis(kind, n, lo, hi):
        if kind == "monomial":
            return [lambda x, j=j: x ** j for j in range(n)]
        t = lambda x: (2 * x - lo - hi) / (hi - lo)
        fam = npleg.Legendre if kind == "legendre" else npcheb.Chebyshev
        return [lambda x, j=j: fam.basis(j)(t(x)) for j in range(n)]

    gal = []
    for name, nmax in [("exp-xs", 8), ("galerkin-xs", 4), ("exp-xs-sym", 8)]:
        spec = SPECS[name]
        K, f, exact = parts(spec)
        lo, hi = spec["lo"], spec["hi"]
        for bk, pk, u0 in [("legendre", "legendre", "zero"), ("legendre", "chebyshev", "zero"), ("monomial", "monomial", "f"), ("chebyshev", "legendre", "f"), ("monomial", "monomial", "zero")]:
            phi, psi = basis(bk, nmax, lo, hi), basis(pk, nmax, lo, hi)
            Kphi = lambda x, j: sint.quad(lambda s: float(K(x, s)) * phi[j](s), lo, hi, epsabs=1e-14, epsrel=1e-14)[0]
            G = np.zeros((nmax, nmax))
            rhs = np.zeros(nmax)
            for i in range(nmax):
                for j in range(nmax):
                    G[i, j] = sint.quad(lambda x: psi[i](x) * phi[j](x), lo, hi, epsabs=1e-14, epsrel=1e-14)[0] - spec["lam"] * sint.quad(lambda x: psi[i](x) * Kphi(x, j), lo, hi, epsabs=1e-13, epsrel=1e-13)[0]
                if u0 == "zero":
                    rhs[i] = sint.quad(lambda x: psi[i](x) * float(f(x)), lo, hi, epsabs=1e-14, epsrel=1e-14)[0]
                else:
                    Kf = lambda x: sint.quad(lambda s: float(K(x, s)) * float(f(s)), lo, hi, epsabs=1e-14, epsrel=1e-14)[0]
                    rhs[i] = spec["lam"] * sint.quad(lambda x: psi[i](x) * Kf(x), lo, hi, epsabs=1e-13, epsrel=1e-13)[0]
            px = probe(spec, 11)
            if name.endswith("-sym"):
                px = px[1:-1]  # f is 0/0 at x = -1
            sols = {}
            for n in range(1, nmax + 1):
                Mn = G[:n, :n]
                c = np.linalg.solve(Mn, rhs[:n])
                y = sum(c[j] * phi[j](px) for j in range(n)) + (np.asarray(f(px)) if u0 == "f" else 0)
                sols[str(n)] = {"c": c.tolist(), "cond1": float(np.linalg.cond(Mn, 1)), "y": np.asarray(y, dtype=float).tolist()}
            gal.append({"spec": name, "phi": bk, "psi": pk, "u0": u0, "Nmax": nmax, "G": G.ravel().tolist(), "rhs": rhs.tolist(), "px": px.tolist(), "solutions": sols})
    out["galerkin"] = gal
    col = []
    for name, ns in [("collocation-sin", (3, 5, 9)), ("collocation-x2s2", (2, 3, 5)), ("galerkin-xs", (2, 4)), ("exp-xs", (4, 8))]:
        spec = SPECS[name]
        K, f, exact = parts(spec)
        lo, hi = spec["lo"], spec["hi"]
        for bk in ("legendre", "chebyshev", "monomial"):
            for nk in ("equidistant", "chebyshev"):
                for n in ns:
                    phi = basis(bk, n, lo, hi)
                    nodes = np.linspace(lo, hi, n) if nk == "equidistant" else (lo + hi) / 2 - (hi - lo) / 2 * np.cos((2 * np.arange(n) + 1) * np.pi / (2 * n))
                    M = np.zeros((n, n))
                    for i in range(n):
                        for j in range(n):
                            M[i, j] = phi[j](nodes[i]) - spec["lam"] * sint.quad(lambda s: float(K(nodes[i], s)) * phi[j](s), lo, hi, epsabs=1e-14, epsrel=1e-14)[0]
                    if np.linalg.cond(M) > 1e13:
                        col.append({"spec": name, "phi": bk, "nodes": nk, "n": n, "singular": True})
                        continue
                    c = np.linalg.solve(M, np.asarray(f(nodes)))
                    px = probe(spec, 11)
                    y = sum(c[j] * phi[j](px) for j in range(n))
                    col.append({"spec": name, "phi": bk, "nodes": nk, "n": n, "nodesValues": nodes.tolist(), "matrix": M.ravel().tolist(), "c": c.tolist(), "cond1": float(np.linalg.cond(M, 1)),
                                "px": px.tolist(), "y": np.asarray(y, dtype=float).tolist()})
    out["collocation"] = col
    # exact solutions at probe points, for the specs that have a formula
    out["exact"] = {name: {"x": probe(spec, 11).tolist(), "y": parts(spec)[2](probe(spec, 11)).tolist()} for name, spec in SPECS.items() if spec["exact"]}
    return out


# ---------------------------------------------------------------- spectral problems

SP = {
    "min": dict(lo=0.0, hi=1.0, kernel="(x+s-abs(x-s))/2", low="s", up="x"),
    "green": dict(lo=0.0, hi=1.0, kernel="(x+s-abs(x-s))/2*(1-(x+s+abs(x-s))/2)", low="s*(1-x)", up="x*(1-s)"),
    "robin": dict(lo=0.0, hi=1.0, kernel="(x+s-abs(x-s))/2*(2-(x+s+abs(x-s))/2)/2", low="s*(2-x)/2", up="x*(2-s)/2"),
    "xs": dict(lo=0.0, hi=1.0, kernel="x*s"),
    "x2s2": dict(lo=0.0, hi=1.0, kernel="x^2*s^2"),
    "sin": dict(lo=-PI, hi=PI, kernel="sin(x)*sin(s)"),
    "rank3": dict(lo=-1.0, hi=1.0, kernel="1+x*s+x^2*s^2"),
    "gauss": dict(lo=0.0, hi=1.0, kernel="exp(-(x-s)^2)"),
}


def sp_kernel(name):
    return lam2(sym(SP[name]["kernel"]), XS_, SS_)


def robin_roots(count):
    from scipy.optimize import brentq
    roots, nu = [], 0.1
    f = lambda v: math.tan(v) + v
    # tan v + v changes sign from - to + inside (pi/2 + (k-1) pi, pi/2 + k pi)
    for k in range(count):
        a, b = math.pi / 2 + k * math.pi + 1e-9, math.pi / 2 + (k + 1) * math.pi - 1e-9
        roots.append(brentq(f, a, b, xtol=1e-14))
    return roots


def sp_exact_lambda(name, count):
    if name == "min":
        return [((k - 0.5) * PI) ** 2 for k in range(1, count + 1)]
    if name == "green":
        return [(k * PI) ** 2 for k in range(1, count + 1)]
    if name == "robin":
        return [v ** 2 for v in robin_roots(count)]
    if name == "xs":
        return [3.0]
    if name == "x2s2":
        return [5.0]
    if name == "sin":
        return [1 / PI]
    if name == "rank3":
        r = math.sqrt(61)
        return [(27 - 3 * r) / 8, 1.5, (27 + 3 * r) / 8]
    return None


def nystrom_numpy(name, n=120):
    spec = SP[name]
    K = sp_kernel(name)
    g = npleg.leggauss(n)
    x = 0.5 * (spec["hi"] - spec["lo"]) * g[0] + 0.5 * (spec["hi"] + spec["lo"])
    w = 0.5 * (spec["hi"] - spec["lo"]) * g[1]
    S = np.sqrt(w)[:, None] * K(x[:, None], x[None, :]) * np.sqrt(w)[None, :]
    return S


def sympy_kellogg(name, omega_text, steps):
    """omega_n = T omega_{n-1} for a kernel with the pieces low (s <= x) and up (s >= x), exactly, by sympy."""
    spec = SP[name]
    low, up = sym(spec["low"]), sym(spec["up"])
    w = sym(omega_text)
    norms = [sympy.sqrt(sympy.integrate(w ** 2, (XS_, spec["lo"], spec["hi"])))]
    for _ in range(steps):
        wl = w.subs(XS_, SS_)
        w = sympy.expand(sympy.integrate(low * wl, (SS_, spec["lo"], XS_)) + sympy.integrate(up * wl, (SS_, XS_, spec["hi"])))
        norms.append(sympy.sqrt(sympy.integrate(w ** 2, (XS_, spec["lo"], spec["hi"]))))
    ratios = [float(norms[n - 1] / norms[n]) for n in range(1, steps + 1)]
    roots = [float(1 / norms[n] ** sympy.Rational(1, n)) for n in range(1, steps + 1)]
    return ratios, roots


def spectral():
    out = {"specs": SP}
    # characteristic numbers: exact where the notes give them, numpy Nystrom (120 Gauss nodes, smooth kernels) otherwise
    ch = {}
    for name in SP:
        ex = sp_exact_lambda(name, 6)
        if ex is None:
            ev = np.linalg.eigvalsh(nystrom_numpy(name))
            ev = ev[np.argsort(-np.abs(ev))]
            ex = [1 / e for e in ev[:6]]
        ch[name] = ex
    out["lambda"] = ch
    # eigenfunctions y_1 (unit L2 norm, positive) at 7 points
    pts = lambda name: np.linspace(SP[name]["lo"], SP[name]["hi"], 9)[1:-1].tolist()
    out["eigenfunction1"] = {
        "min": {"x": pts("min"), "y": [math.sqrt(2) * math.sin(PI * x / 2) for x in pts("min")]},
        "green": {"x": pts("green"), "y": [math.sqrt(2) * math.sin(PI * x) for x in pts("green")]},
        "sin": {"x": pts("sin"), "y": [math.sin(x) / math.sqrt(PI) for x in pts("sin")]},
    }
    # Kellogg by exact sympy integration
    kel = []
    for name in ("min", "green", "robin"):
        for om in ("1", "x"):
            ratios, roots = sympy_kellogg(name, om, 5)
            kel.append({"spec": name, "omega": om, "ratios": ratios, "roots": roots})
    out["kellogg"] = kel
    # traces: exact sums of lambda^-m (zeta values) for min, green, rank-one kernels; numpy matrix powers for the Gaussian kernel
    import mpmath
    def zeta_trace(name, p):
        if name == "min":
            return float((2 ** (2 * p) - 1) * mpmath.zeta(2 * p) / mpmath.pi ** (2 * p))
        if name == "green":
            return float(mpmath.zeta(2 * p) / mpmath.pi ** (2 * p))
        raise KeyError(name)
    traces = {}
    for name in ("min", "green"):
        traces[name] = [zeta_trace(name, 2 * m) for m in range(1, 7)]  # A_2, A_4, ..., A_12
    traces["xs"] = [3.0 ** (-2 * m) for m in range(1, 7)]
    traces["x2s2"] = [5.0 ** (-2 * m) for m in range(1, 7)]
    S = nystrom_numpy("gauss", 160)
    traces["gauss"] = [float(np.trace(np.linalg.matrix_power(S, 2 * m))) for m in range(1, 7)]
    out["traces"] = traces
    # Ritz: scipy generalized eigenproblem, nested quad split at the kink
    from scipy.linalg import eigh

    def basis(kind, n, lo, hi):
        if kind == "monomial":
            return [lambda x, j=j: x ** j for j in range(n)]
        t = lambda x: (2 * x - lo - hi) / (hi - lo)
        fam = npleg.Legendre if kind == "legendre" else npcheb.Chebyshev
        return [lambda x, j=j: float(fam.basis(j)(t(x))) for j in range(n)]

    ritz = []
    for name, nmax, kinds in [("green", 6, ("legendre", "chebyshev", "monomial")), ("min", 5, ("legendre",)), ("rank3", 3, ("legendre", "monomial")), ("x2s2", 3, ("legendre",)),
                              ("gauss", 5, ("legendre",)), ("sin", 3, ("monomial",))]:
        spec = SP[name]
        lo, hi = spec["lo"], spec["hi"]
        K = lambda x, s, f=sp_kernel(name): float(f(x, s))
        for kind in kinds:
            phi = basis(kind, nmax, lo, hi)
            inner = lambda x, k: sint.quad(lambda s: K(x, s) * phi[k](s), lo, hi, points=[x] if lo < x < hi else None, epsabs=1e-14, epsrel=1e-14, limit=200)[0]
            G = np.zeros((nmax, nmax))
            M = np.zeros((nmax, nmax))
            for j in range(nmax):
                for k in range(nmax):
                    G[j, k] = sint.quad(lambda x: phi[j](x) * inner(x, k), lo, hi, epsabs=1e-13, epsrel=1e-13, limit=200)[0]
                    M[j, k] = sint.quad(lambda x: phi[j](x) * phi[k](x), lo, hi, epsabs=1e-14, epsrel=1e-14)[0]
            G = (G + G.T) / 2
            sols = {}
            for n in range(1, nmax + 1):
                sig = eigh(G[:n, :n], M[:n, :n], eigvals_only=True)
                sig = sig[np.argsort(-np.abs(sig))]
                sig = sig[np.abs(sig) > 1e-11 * np.abs(G).max() / np.diag(M[:n, :n]).min()]
                sols[str(n)] = [1 / s for s in sig]
            ritz.append({"spec": name, "basis": kind, "Nmax": nmax, "G": G.ravel().tolist(), "M": M.ravel().tolist(), "lambda": sols})
    out["ritz"] = ritz
    # Jacobi: numpy eigvalsh of symmetric matrices
    mats = {
        "note-4x4": np.array([[4.0, 1, 2, 0], [1, 3, 0, 1], [2, 0, 5, 1], [0, 1, 1, 2]]),
        "equal-diagonal": np.array([[1.0, 2, 0], [2, 1, 0], [0, 0, 3]]),
        "diagonal": np.diag([3.0, 1.0, 2.0]),
        "two": np.array([[2.0, -1], [-1, 5]]),
        "tridiag-5": 2 * np.eye(5) - np.eye(5, k=1) - np.eye(5, k=-1),
    }
    for n in (3, 4, 5):
        a = RNG.standard_normal((n, n))
        mats[f"random-{n}"] = (a + a.T) / 2
    out["jacobi"] = [{"name": k, "n": len(m), "A": m.ravel().tolist(), "eigenvalues": np.linalg.eigvalsh(m).tolist()} for k, m in mats.items()]
    return out


def main():
    out = {"cases": []}
    for name, (A, b) in cases().items():
        n = len(A)
        x0 = np.zeros(n)
        entry = {
            "name": name, "n": n, "A": A.ravel().tolist(), "b": b.tolist(), "x0": x0.tolist(), "exact": np.linalg.solve(A, b).tolist(),
            "dominanceQ": float(((np.abs(A).sum(1) - np.abs(np.diag(A))) / np.abs(np.diag(A))).max()),
            "symmetric": bool(np.allclose(A, A.T)),
            "positiveDefinite": bool(np.allclose(A, A.T) and np.linalg.eigvalsh(A).min() > 1e-9),
            "configs": [],
        }
        for method, params in [("jacobi", {}), ("seidel", {}), ("relax", {"omega": 0.5}), ("relax", {"omega": 1.5}), ("relax", {"omega": 1.9})]:
            entry["configs"].append(config(A, b, x0, method, **params))
        if entry["positiveDefinite"]:
            ev = np.linalg.eigvalsh(A)
            m, M = float(ev.min()), float(ev.max())
            entry["tauOptimal"] = {"m": m, "M": M, "tau": 2 / (M + m), "rho": (M - m) / (M + m)}
            for tau in (0.5 / M, 1 / M, 2 / (M + m), 1.9 / M, 2.4 / M):
                entry["configs"].append(config(A, b, x0, "explicit", tau=float(tau)))
            entry["bestOmega"] = best_parameter(A, "relax", 1e-3, 2 - 1e-3)
            entry["bestTau"] = best_parameter(A, "explicit", 1e-3, 2.4 / M)
        else:
            for tau in (0.05, 0.2):
                entry["configs"].append(config(A, b, x0, "explicit", tau=tau))
            entry["bestOmega"] = best_parameter(A, "relax", 1e-3, 2 - 1e-3)
        out["cases"].append(entry)
    out["secondKind"] = second_kind()
    out["spectral"] = spectral()
    (HERE / "fixtures.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"wrote {len(out['cases'])} cases")


if __name__ == "__main__":
    main()
