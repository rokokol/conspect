"""Mode solver of the three-layer planar waveguide, shared by the несимм-* figures.

Layers: substrate z < 0 (n_s), film 0 < z < h (n_f), cover z > h (n_a), with
n_f > n_s >= n_a. The field f(z) of a TE mode is E_y, of a TM mode H_y.
Dispersion equation, with j the mode number:
    gamma h = arctan(c_a delta_a / gamma) + arctan(c_s delta_s / gamma) + j pi,
    c_m = 1 for TE and (n_f / n_m)^2 for TM.
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class Guide:
    lam: float
    n_a: float
    n_f: float
    n_s: float

    @property
    def k0(self):
        return 2 * np.pi / self.lam

    @property
    def gamma_cut(self):
        """gamma_f at beta = k_s, where n_eff reaches n_s."""
        return self.k0 * np.sqrt(self.n_f**2 - self.n_s**2)

    def weights(self, pol):
        if pol == "TE":
            return 1.0, 1.0
        return (self.n_f / self.n_a) ** 2, (self.n_f / self.n_s) ** 2


WEAK = Guide(lam=1.55, n_a=1.44, n_f=1.45, n_s=1.44)
STRONG = Guide(lam=0.6328, n_a=1.0, n_f=3.6, n_s=3.4)


def residual(n_eff, j, h, g, pol):
    """F(n_eff) = gamma h - phi_a - phi_s - j pi; strictly decreasing in n_eff."""
    k0 = g.k0
    beta = n_eff * k0
    gam = np.sqrt((k0 * g.n_f) ** 2 - beta**2)
    d_a = np.sqrt(beta**2 - (k0 * g.n_a) ** 2)
    d_s = np.sqrt(beta**2 - (k0 * g.n_s) ** 2)
    c_a, c_s = g.weights(pol)
    return gam * h - np.arctan(c_a * d_a / gam) - np.arctan(c_s * d_s / gam) - j * np.pi


def n_eff(j, h, g, pol):
    """The effective index of mode j, or None when the mode is below cutoff."""
    lo = g.n_s * (1 + 1e-14)
    hi = g.n_f * (1 - 1e-14)
    if residual(lo, j, h, g, pol) <= 0:
        return None
    return brentq(residual, lo, hi, args=(j, h, g, pol), xtol=1e-14, rtol=1e-14)


def cutoff(j, g, pol):
    """Cutoff thickness of mode j: the h at which n_eff = n_s."""
    c_a, _ = g.weights(pol)
    d_a = g.k0 * np.sqrt(g.n_s**2 - g.n_a**2)
    return (j * np.pi + np.arctan(c_a * d_a / g.gamma_cut)) / g.gamma_cut


def amplitudes(j, h, g, pol):
    """gamma, delta_a, delta_s and the coefficients A, B=1, C, D=1 of the profile."""
    ne = n_eff(j, h, g, pol)
    k0 = g.k0
    beta = ne * k0
    gam = np.sqrt((k0 * g.n_f) ** 2 - beta**2)
    d_a = np.sqrt(beta**2 - (k0 * g.n_a) ** 2)
    d_s = np.sqrt(beta**2 - (k0 * g.n_s) ** 2)
    _, c_s = g.weights(pol)
    b = 1.0
    c = c_s * d_s / gam
    a = b * np.cos(gam * h) + c * np.sin(gam * h)
    return gam, d_a, d_s, a, b, c, 1.0


def profile(z, j, h, g, pol):
    gam, d_a, d_s, a, b, c, d = amplitudes(j, h, g, pol)
    z = np.asarray(z, dtype=float)
    f = np.where(z < 0, d * np.exp(d_s * np.minimum(z, 0)), 0.0)
    inside = (z >= 0) & (z <= h)
    f = np.where(inside, b * np.cos(gam * z) + c * np.sin(gam * z), f)
    f = np.where(z > h, a * np.exp(-d_a * np.maximum(z - h, 0)), f)
    return f / np.max(np.abs(f))


def confinement(j, h, g, pol):
    """Share of the integral of f^2 that lies in the film, in closed form."""
    gam, d_a, d_s, a, b, c, d = amplitudes(j, h, g, pol)
    core = ((b**2 + c**2) * h / 2
            + (b**2 - c**2) * np.sin(2 * gam * h) / (4 * gam)
            + b * c * (1 - np.cos(2 * gam * h)) / (2 * gam))
    sub = d**2 / (2 * d_s)
    cov = a**2 / (2 * d_a)
    return core / (core + sub + cov)
