"""Reference answers for the tests of numkit.js, written to fixtures.json (not in git: run this first).

Each answer comes from a method other than the one numkit.js uses:
  parser        sympy's own parser and lambdify, ^ read as a power, evaluated at three points
  quadrature    mpmath (50 digits, tanh-sinh and Gauss-Legendre), a method of another family than Gauss-Kronrod
  eigenvalues   numpy.linalg.eigvals (LAPACK geev); the characteristic polynomial from sympy's exact charpoly
                for integer entries and from numpy.poly otherwise

Courses reuse the sympy helpers below (`sym`, `fn`, `orth`, the symbols) in their own export_fixtures.py:
  from numkit import export_fixtures as nk

Usage: python export_fixtures.py   (writes fixtures.json next to this file)
"""
import json
from pathlib import Path

import mpmath
import numpy as np
import sympy
from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations

HERE = Path(__file__).resolve().parent


def orth(rng, m, n):
    """A random m x n matrix with orthonormal columns from the generator `rng`."""
    q, _ = np.linalg.qr(rng.standard_normal((m, n)))
    return q


X, T, LAM = sympy.symbols("x t lam")
LOCALS = {
    "x": X, "t": T, "lam": LAM, "pi": sympy.pi, "e": sympy.E, "ln": sympy.log, "log": sympy.log, "tg": sympy.tan, "tan": sympy.tan,
    "ctg": sympy.cot, "cot": sympy.cot, "sh": sympy.sinh, "ch": sympy.cosh, "th": sympy.tanh, "abs": sympy.Abs,
    "arcsin": sympy.asin, "arccos": sympy.acos, "arctg": sympy.atan, "arctan": sympy.atan, "Rational": sympy.Rational,
}


def sym(text):
    """A formula of the pages as a sympy expression; sympy's own parser, with ^ as power."""
    return parse_expr(text, local_dict=LOCALS, transformations=standard_transformations + (convert_xor,))


def fn(expr, *vars_):
    f = sympy.lambdify(vars_, expr, "math")
    return lambda *a: float(f(*a))


# Formulas of the page parser: (page text, sympy text or None when it is the same), points (x, t).
PARSER_CASES = [
    "x", "t", "1", "2.5", "1,5*x", "1e-3*x", "x+t", "x-t", "x*t", "x/t", "x^2", "-x^2", "(-x)^2", "2^3^2", "2^-1", "2^-x",
    "1-2-3", "8/2/2", "2*3^2", "-2^2", "2^2^-1", "x - -t", "+x", "sin(x)", "cos(x)", "tan(x)", "tg(x)", "ctg(x)", "cot(x)",
    "exp(x)", "log(x)", "ln(x)", "sqrt(x)", "abs(x-2)", "asin(x/4)", "arcsin(x/4)", "acos(x/4)", "arccos(x/4)", "atan(x)",
    "arctg(x)", "arctan(x)", "sinh(x)", "sh(x)", "cosh(x)", "ch(x)", "tanh(x)", "th(x)", "pi", "π*x", "e", "e^x", "pi*x^2/2",
    "sin(x)^2 + cos(x)^2", "exp(-x^2)*cos(3*t)", "sqrt(x^2+t^2)", "(x+1)*(t-1)/(x+t+1)", "x^t", "-(x+t)^2", "sin(cos(x))",
    "3*x - 2", "x ^ 2 ^ 0.5", "  x  +  t  ", "2*(3+x)*(4+t)", "1/(1+x^2)", "log(x)/log(10)", "x^3*t^-2", "abs(-x)", "(x)", "((x))",
]


def parser_cases():
    pts = [(0.7, 1.3), (1.9, 0.4), (2.6, 3.1)]
    out = []
    for text in PARSER_CASES:
        py = text.replace(",", ".").replace("π", "pi")
        expr = sym(py)
        f = fn(expr, X, T)
        out.append({"src": text, "points": [[x, t, f(x, t)] for x, t in pts]})
    return out


# Integrals checked against mpmath, a method of another family than Gauss-Kronrod.
QUAD_CASES = [
    ("sin(x)", "0", "pi", []), ("exp(x)", "0", "1", []), ("x^5-2*x^2+1", "-1", "2", []), ("1/(1+x^2)", "0", "1", []),
    ("sin(x)^2", "0", "2*pi", []), ("cos(x)*exp(-x)", "0", "5", []), ("abs(x)", "-1", "1", ["0"]),
    ("abs(x-1/3)", "0", "1", ["1/3"]), ("ln(x)", "0", "1", []), ("1/sqrt(x)", "0", "1", []), ("x^-0.5*cos(x)", "0", "2", []),
    ("ln(x)^2", "0", "1", []), ("sqrt(1-x^2)", "-1", "1", []),("sin(50*x)", "0", "pi", []),
    ("exp(-100*(x-0.5)^2)", "0", "1", []), ("x*ln(x)", "0", "1", []), ("tg(x)", "-1", "1", []), ("x", "2", "1", []),
    ("cosh(x)", "-1", "1", []), ("abs(pi-x)", "0", "2*pi", ["pi"]),
]


def quad_cases():
    mpmath.mp.dps = 50
    out = []
    for text, lo, hi, kinks in QUAD_CASES:
        f = sympy.lambdify(X, sym(text), "mpmath")
        a, b = [mpmath.mpf(str(sympy.N(sym(s), 50))) for s in (lo, hi)]
        nodes = [a, *[mpmath.mpf(str(sympy.N(sym(k), 50))) for k in kinks], b]
        # mpmath integrates a > b with the sign by itself; kinks are the break points of the abs
        out.append({"src": text, "lo": lo, "hi": hi, "value": float(mpmath.quad(f, nodes))})
    return out


def eigen_cases(rng):
    """Matrices for the eigenvalue solver: numpy's eigvals, the exact characteristic polynomial from sympy
    for integer entries (numpy.poly otherwise). `tol` is the accuracy to expect: a root of multiplicity m
    is only known to about eps^(1/m)."""
    out = []

    def add(name, a, tol=1e-9, exact=False):
        a = np.array(a, dtype=float)
        n = a.shape[0]
        if exact:
            mu = sympy.symbols("mu")
            coeffs = sympy.Poly(sympy.Matrix(a.astype(int).tolist()).charpoly(mu).as_expr(), mu).all_coeffs()
            poly = [float(x) for x in coeffs]
        else:
            poly = np.poly(a).tolist()
        # det(mu I - A) = mu^n + c_{n-1} mu^(n-1) + ... + c_0 and det(I - lambda A) = 1 + c_{n-1} lambda + ... + c_0 lambda^n:
        # the same list, highest power of mu first, is the list of Delta's coefficients, lowest power of lambda first
        out.append({"name": name, "n": n, "a": a.ravel().tolist(), "mu": [[float(z.real), float(z.imag)] for z in np.linalg.eigvals(a)],
                    "delta": poly, "tol": tol})

    add("scalar", [[3]], exact=True)
    add("zero-3", np.zeros((3, 3)), tol=1e-9, exact=True)
    add("identity-4", np.eye(4), exact=True)
    add("diagonal", np.diag([5, -2, 0, 7]), exact=True)
    add("upper-triangular", [[2, 1, 4], [0, 3, 5], [0, 0, -1]], exact=True)
    add("rotation-block", [[0, -1, 0], [1, 0, 0], [0, 0, 2]], exact=True)
    add("companion-roots-1-2-3-4", [[0, 0, 0, -24], [1, 0, 0, 50], [0, 1, 0, -35], [0, 0, 1, 10]], exact=True)
    add("symmetric-3", [[2, -1, 0], [-1, 2, -1], [0, -1, 2]], exact=True)
    add("jordan-2", [[2, 1], [0, 2]], tol=1e-6, exact=True)
    add("jordan-3", [[2, 1, 0], [0, 2, 1], [0, 0, 2]], tol=1e-4, exact=True)
    add("nilpotent-3", [[0, 1, 0], [0, 0, 1], [0, 0, 0]], tol=1e-4, exact=True)
    add("rank-one-4", np.outer([1, 2, 3, 4], [2, 0, -1, 1]), exact=True)
    add("integer-5", [[4, -2, 1, 0, 3], [1, 3, -1, 2, 0], [0, 5, 2, -3, 1], [2, 0, 1, 4, -2], [-1, 1, 0, 2, 3]], exact=True)
    add("permutation-cycle-5", np.roll(np.eye(5), 1, axis=0))
    add("badly-scaled", np.diag([1e-8, 1, 1e8]) @ np.array([[1, 2, 3], [4, 5, 6], [7, 8, 10]]) @ np.diag([1e8, 1, 1e-8]), tol=1e-7)
    add("hilbert-6", [[1 / (i + j + 1) for j in range(6)] for i in range(6)], tol=1e-8)
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 10):
        for k in range(4):
            add(f"random-{n}-{k}", rng.standard_normal((n, n)))
    for k in range(4):
        q = orth(rng, 6, 6)
        add(f"similar-to-repeated-{k}", q @ np.diag([2.0, 2.0, -1.0, -1.0, 4.0, 0.5]) @ q.T, tol=1e-6)
    return out


def main():
    rng = np.random.default_rng(20261022)
    data = {"parser": parser_cases(), "quad": quad_cases(), "eigen": eigen_cases(rng)}
    (HERE / "fixtures.json").write_text(json.dumps(data), encoding="utf-8")
    print({k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
