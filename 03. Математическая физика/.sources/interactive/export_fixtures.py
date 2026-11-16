"""Reference answers for the tests of wgcore.js, written to fixtures.json.

Each answer comes from a method other than the one wgcore.js uses:
  Bessel J_n(x), K_n(x)           scipy.special.jv, kv (AMOS and Cephes, not the Miller recurrence or the integral of wgcore.js)
  J_n(z), H1_n(z), complex z      scipy.special.jv, hankel1 (AMOS)
  zeros of J_n                    scipy.special.jn_zeros
  surface roots of a round guide  scipy.optimize.brentq on lambda J_{m+1}(lambda) K_m(kappa) - kappa K_{m+1}(kappa) J_m(lambda), scipy Bessel functions
  leaky roots                     mpmath findroot of the full determinant with mpmath besselj and hankel1 at 30 digits,
                                  seeded by the values printed in the note "Круглый слабонаправляющий волновод"
  planar waveguides               scipy.optimize.brentq on the trigonometric form of each equation (no arctangents),
                                  mpmath for the thickness of cutoff, scipy.integrate.quad for the confinement factor

Usage: python export_fixtures.py   (writes fixtures.json next to this file)
"""
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np
import scipy.integrate
import scipy.optimize
import scipy.special as sp

HERE = Path(__file__).resolve().parent
mp.mp.dps = 30


def bessel_j_real():
    out = []
    xs = [1e-6, 1e-3, 0.01, 0.1, 0.5, 1, 2, 2.4048, 3.5, 5, 7.5, 8, 12, 20, 35, 60, 100]
    for n in range(0, 8):
        for x in xs:
            out.append({"n": n, "x": x, "v": float(sp.jv(n, x))})
    return out


def bessel_k_real():
    out = []
    xs = [1e-6, 1e-4, 0.01, 0.1, 0.5, 1, 1.9, 2, 2.1, 3, 5, 8, 12, 20, 35, 60, 120, 600]
    for n in range(0, 8):
        for x in xs:
            v = float(sp.kv(n, x))
            if 1e-290 < v < 1e290:
                out.append({"n": n, "x": x, "v": v})
    return out


def complex_grid():
    radii = [0.01, 0.1, 0.5, 1, 2, 3, 5, 8, 12, 20, 30, 45]
    angles = [-math.pi / 2, -3 * math.pi / 8, -math.pi / 4, -math.pi / 8, 0, math.pi / 8, math.pi / 4, 3 * math.pi / 8, math.pi / 2,
              -2.6, 2.6]
    return [(r * math.cos(a), r * math.sin(a)) for r in radii for a in angles]


def bessel_complex():
    j_out, h_out = [], []
    for re, im in complex_grid():
        z = complex(re, im)
        for n in range(0, 6):
            jv = sp.jv(n, z)
            scale = max(abs(sp.jv(k, z)) for k in range(0, n + 2))
            j_out.append({"n": n, "re": re, "im": im, "v": [jv.real, jv.imag], "scale": float(scale)})
            hv = sp.hankel1(n, z)
            # J and Y grow like exp(|Im z|); in the upper half-plane H1 decays, and J + iY cancels them
            cond = max(abs(sp.jv(n, z)), abs(sp.yv(n, z)))
            h_out.append({"n": n, "re": re, "im": im, "v": [hv.real, hv.imag], "cond": float(cond)})
    return j_out, h_out


def zeros():
    return {str(n): [float(z) for z in sp.jn_zeros(n, 8)] for n in range(0, 6)}


def surface_roots():
    """All roots of the real characteristic equation on (0, V), found by a log-spaced scan in the angle theta (lambda = V cos, kappa = V sin)."""
    out = []
    for m in range(0, 5):
        for V in [0.3, 0.5, 1.0, 2.0, 2.5, 3.0, 4.0, 5.5, 8.0, 12.0, 15.0]:
            def g(theta):
                lam, kap = V * math.cos(theta), V * math.sin(theta)
                return lam * sp.jv(m + 1, lam) * sp.kve(m, kap) - kap * sp.kve(m + 1, kap) * sp.jv(m, lam)
            thetas = np.concatenate([np.geomspace(1e-14, 1e-2, 160), np.linspace(1e-2, math.pi / 2 - 1e-9, 6000)[1:]])
            vals = [g(t) for t in thetas]
            found = []
            for a, b, fa, fb in zip(thetas[:-1], thetas[1:], vals[:-1], vals[1:]):
                if fa == 0 or fa * fb < 0:
                    t = scipy.optimize.brentq(g, a, b, xtol=1e-300, rtol=1e-14)
                    found.append((V * math.cos(t), V * math.sin(t)))
            found.sort()
            out.append({"m": m, "V": V, "roots": [r[0] for r in found], "kappas": [r[1] for r in found]})
    return out


def lam_f(lam, V, m):
    al = mp.sqrt(lam ** 2 - V ** 2)
    if mp.re(al) < 0:
        al = -al
    return (lam * mp.besselj(m + 1, lam) * mp.hankel1(m, al) - al * mp.besselj(m, lam) * mp.hankel1(m + 1, al)) / lam ** m


NOTE_V05 = {1: 1.0390 - 2.5570j, 2: 2.6045 - 3.1443j, 3: 3.9714 - 3.5854j, 4: 5.2568 - 3.9493j}


def leaky_roots():
    """Complex roots below cutoff: from the seed of the note at V = 0.5 the root is followed in V by mpmath in steps of 0.02."""
    out = []
    for m in range(1, 5):
        vc = float(mp.besseljzero(m - 1, 1))
        z0 = mp.findroot(lambda l: lam_f(l, mp.mpf("0.5"), m), mp.mpc(NOTE_V05[m]), tol=1e-22)
        targets_down = [0.1, 0.2, 0.3, 0.4]
        targets_up = [0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        # downward
        z = z0
        v = 0.5
        for tv in sorted(targets_down, reverse=True):
            while v > tv + 1e-12:
                v = max(v - 0.01, tv)
                z = mp.findroot(lambda l: lam_f(l, mp.mpf(v), m), z, tol=1e-22)
            out.append({"m": m, "V": tv, "lam": [float(mp.re(z)), float(mp.im(z))]})
        # upward
        z = z0
        v = 0.5
        for tv in targets_up:
            if tv > vc - 0.8:
                break
            while v < tv - 1e-12:
                v = min(v + 0.01, tv)
                z = mp.findroot(lambda l: lam_f(l, mp.mpf(v), m), z, tol=1e-22)
            out.append({"m": m, "V": tv, "lam": [float(mp.re(z)), float(mp.im(z))]})
    return out


def sym_roots(n1, n2, lam0, d, pol):
    """Roots of the trigonometric forms in each corridor (j pi/2, (j+1) pi/2), no arctangent and no tangent poles."""
    k0 = 2 * math.pi / lam0
    V = k0 * d * math.sqrt(n1 ** 2 - n2 ** 2)
    q = (n1 / n2) ** 2 if pol == "TM" else 1.0
    modes = []
    j = 0
    while j * math.pi / 2 < V:
        lo, hi = j * math.pi / 2, min((j + 1) * math.pi / 2, V)
        Y = lambda X: math.sqrt(max(0.0, V * V - X * X))
        if j % 2 == 0:
            g = lambda X: X * math.sin(X) - q * Y(X) * math.cos(X)
        else:
            g = lambda X: q * Y(X) * math.sin(X) + X * math.cos(X)
        if g(lo) * g(hi) > 0:
            raise SystemExit(f"no sign change: j={j} V={V}")
        X = scipy.optimize.brentq(g, lo, hi, xtol=1e-15, rtol=1e-15)
        Yv = Y(X)
        neff = math.sqrt(n1 ** 2 - (X / (k0 * d)) ** 2)
        modes.append({"j": j, "X": X, "Y": Yv, "neff": neff})
        j += 1
    return {"V": V, "M": int(math.floor(2 * V / math.pi)) + 1, "modes": modes}


def sym_cases():
    out = []
    for n1, n2, lam0, d in [(1.45, 1.44, 1.55, 16.0), (3.5, 1.45, 1.55, 0.13), (3.5, 1.45, 1.55, 0.25), (3.5, 1.45, 1.55, 1.0),
                            (3.5, 1.45, 1.55, 0.2), (1.5, 1.0, 0.8, 0.05), (1.5, 1.0, 0.8, 2.0)]:
        out.append({"n1": n1, "n2": n2, "lam0": lam0, "d": d,
                    "TE": sym_roots(n1, n2, lam0, d, "TE"), "TM": sym_roots(n1, n2, lam0, d, "TM")})
    return out


def asym_F(neff, j, p, pol):
    na, nf, ns, lam0, h = p
    k0 = 2 * math.pi / lam0
    g = k0 * math.sqrt(nf ** 2 - neff ** 2)
    da = k0 * math.sqrt(max(0.0, neff ** 2 - na ** 2))
    ds = k0 * math.sqrt(max(0.0, neff ** 2 - ns ** 2))
    ca = (nf / na) ** 2 if pol == "TM" else 1.0
    cs = (nf / ns) ** 2 if pol == "TM" else 1.0
    return g * h - math.atan(ca * da / g) - math.atan(cs * ds / g) - j * math.pi


def asym_roots(p, pol):
    """The notebook's way: a fine scan of F on (max(n_a, n_s), n_f) for sign changes, then brentq."""
    na, nf, ns, lam0, h = p
    lo = max(na, ns)
    grid = np.linspace(lo, nf, 4001)
    grid[0] = lo + 1e-14
    grid[-1] = nf - 1e-15
    modes = []
    for j in range(0, 60):
        vals = [asym_F(x, j, p, pol) for x in grid]
        if vals[0] <= 0:
            break
        cells = [(a, b) for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]) if fa * fb < 0]
        if len(cells) != 1:
            raise SystemExit(f"F is not monotone: {p} {pol} j={j}: {len(cells)} sign changes")
        root = scipy.optimize.brentq(lambda x: asym_F(x, j, p, pol), *cells[0], xtol=1e-16, rtol=1e-15)
        modes.append({"j": j, "neff": root})
    return modes


def asym_null(p, pol, neff):
    """Profile coefficients from the four matching conditions as a null vector (A, B, C, D) by SVD, not from the formulas of the note."""
    na, nf, ns, lam0, h = p
    k0 = 2 * math.pi / lam0
    g = k0 * math.sqrt(nf ** 2 - neff ** 2)
    da = k0 * math.sqrt(neff ** 2 - na ** 2)
    ds = k0 * math.sqrt(neff ** 2 - ns ** 2)
    wa = 1 / na ** 2 if pol == "TM" else 1.0
    wf = 1 / nf ** 2 if pol == "TM" else 1.0
    ws = 1 / ns ** 2 if pol == "TM" else 1.0
    # unknowns (A, B, C, D): f = D e^{ds z}; B cos + C sin; A e^{-da (z - h)}
    M = np.array([
        [0, 1, 0, -1],                                             # f continuous at 0
        [0, 0, wf * g, -ws * ds],                                  # f' (weighted) at 0
        [-1, math.cos(g * h), math.sin(g * h), 0],                 # f continuous at h
        [wa * da, -wf * g * math.sin(g * h), wf * g * math.cos(g * h), 0],  # wf f'(h-) = wa f'(h+) = -wa da A
    ])
    _, s, vt = np.linalg.svd(M)
    return vt[-1], float(s[-1]), (g, da, ds)


def asym_eval(coefs, p, rates, z):
    A, B, C, D = coefs
    g, da, ds = rates
    h = p[4]
    if z < 0:
        return D * math.exp(ds * z)
    if z > h:
        return A * math.exp(-da * (z - h))
    return B * math.cos(g * z) + C * math.sin(g * z)


def asym_confinement(p, pol, neff):
    """The three integrals of f^2 by scipy.integrate.quad over the three layers."""
    coefs, _, rates = asym_null(p, pol, neff)
    h = p[4]
    f2 = lambda z: asym_eval(coefs, p, rates, z) ** 2
    sub = scipy.integrate.quad(f2, -math.inf, 0, epsabs=1e-14, epsrel=1e-13)[0]
    film = scipy.integrate.quad(f2, 0, h, epsabs=1e-14, epsrel=1e-13)[0]
    cov = scipy.integrate.quad(f2, h, math.inf, epsabs=1e-14, epsrel=1e-13)[0]
    return film / (sub + film + cov)


def asym_cutoff(p, pol, j):
    """Smallest thickness at which the mode j exists, by bisection on the thickness: the mode exists while F > 0 at the lower end."""
    na, nf, ns, lam0, h0 = p
    def exists(h):
        pp = (na, nf, ns, lam0, h)
        return asym_F(max(na, ns), j, pp, pol) > 0
    a, b = 1e-3, 100.0
    for _ in range(200):
        mid = 0.5 * (a + b)
        if exists(mid):
            b = mid
        else:
            a = mid
    return 0.5 * (a + b)


def asym_cases():
    params = [
        ("weak", (1.44, 1.45, 1.44, 1.55, 32.0)),
        ("weak10", (1.44, 1.45, 1.44, 1.55, 10.0)),
        ("strong", (1.0, 3.6, 3.4, 0.6328, 1.1)),
        ("mixed", (1.33, 2.0, 1.5, 0.8, 1.0)),
        ("swapped", (1.5, 2.0, 1.33, 0.8, 1.0)),
    ]
    out = []
    for name, p in params:
        case = {"name": name, "na": p[0], "nf": p[1], "ns": p[2], "lam0": p[3], "h": p[4]}
        for pol in ("TE", "TM"):
            modes = asym_roots(p, pol)
            zs = list(np.linspace(-0.6 * p[4], 1.6 * p[4], 41))
            for m in modes:
                coefs, smin, rates = asym_null(p, pol, m["neff"])
                m["profile_check"] = smin
                m["f"] = [asym_eval(coefs, p, rates, z) for z in zs]
                m["gamma"] = asym_confinement(p, pol, m["neff"])
            case[pol] = {"modes": modes, "zs": zs, "hc": [asym_cutoff(p, pol, j) for j in range(0, 6)]}
        out.append(case)
    return out


def main():
    jc, hc = bessel_complex()
    data = {
        "besselJ": bessel_j_real(),
        "besselK": bessel_k_real(),
        "besselJc": jc,
        "hankel1c": hc,
        "zeros": zeros(),
        "surface": surface_roots(),
        "leaky": leaky_roots(),
        "sym": sym_cases(),
        "asym": asym_cases(),
    }
    (HERE / "fixtures.json").write_text(json.dumps(data), encoding="utf-8")
    print({k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
