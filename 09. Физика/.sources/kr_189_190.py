"""Figures for the preparation problems of lessons 189 and 190 in "Соединение проводников" and "Работа и мощность тока. Закон Джоуля–Ленца" (section f11).

The TikZ helpers come from connections.py, which takes the macros from circuit_diagrams.py and ohm_circuits.py.
Run: nix shell nixpkgs#poppler-utils -c python3 kr_189_190.py [name ...]
The system pdflatex needs the tikz package. PNG files go to content/11. Электрические явления/00. Вложения/ (prefix kr-)
Every figure asserts the numbers that it prints.
"""
import sys
from fractions import Fraction

import connections as cn
from connections import arr, dot, line, res, term, txt
from theme import num

cd = cn.cd

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


def build(name, body):
    cd.build(name, body)


@fig("kr-series-parallel-n")
def _():
    n = 4
    R1 = Fraction(1)
    R_ser = R1 * (n + 1)
    R_par = R1 * n * R1 / (R1 + n * R1)
    assert Fraction(R_ser, 1) / R_par == Fraction((n + 1) ** 2, n) == Fraction(25, 4) and float(Fraction(25, 4)) == 6.25
    s = txt(0.0, 3.3, "последовательно", "west", "font=\\bfseries\\small")
    s += term(0, 2.4) + line((0, 2.4), (0.5, 2.4)) + res(1.2, 2.4, 0, "$R_1$", "a") + line((1.9, 2.4), (2.6, 2.4))
    s += res(3.3, 2.4, 0, "$R_2=4R_1$", "a") + line((4.0, 2.4), (4.7, 2.4)) + term(4.7, 2.4)
    s += txt(5.4, 2.4, "$R_\\text{посл}=R_1(n+1)=5R_1$", "west", "text=el")
    s += txt(0.0, 0.9, "параллельно", "west", "font=\\bfseries\\small")
    s += term(0, -0.6) + line((0, -0.6), (0.9, -0.6)) + dot(0.9, -0.6) + dot(4.7, -0.6)
    s += line((0.9, 0.0), (0.9, -1.4)) + line((4.7, 0.0), (4.7, -1.4))
    s += line((0.9, 0.0), (1.4, 0.0)) + res(2.1, 0.0, 0, "$R_1$", "a") + line((2.8, 0.0), (4.7, 0.0))
    s += line((0.9, -1.4), (2.1, -1.4)) + res(2.8, -1.4, 0, "$R_2=4R_1$", "a") + line((3.5, -1.4), (4.7, -1.4))
    s += line((4.7, -0.6), (5.2, -0.6)) + term(5.2, -0.6)
    s += txt(5.9, -0.6, "$R_\\text{пар}=\\dfrac{nR_1}{n+1}=0{,}8\\,R_1$", "west", "text=el")
    return s


def gelfgat_panel(ox, closed):
    """The bridge of task 11.36: R1 over R2 on the left, R3 over R4 on the right, a key between the middles."""
    L, R = ox - 1.7, ox + 1.7
    s = term(ox, 4.5) + line((ox, 4.5), (ox, 3.8)) + dot(ox, 3.8) + line((L, 3.8), (R, 3.8))
    s += line((L, 3.8), (L, 3.3)) + line((R, 3.8), (R, 3.3))
    s += res(L, 2.6, 90, "$R_1=600$", "l") + res(R, 2.6, 90, "$R_3=1800$", "r")
    s += line((L, 1.9), (L, 1.6)) + line((R, 1.9), (R, 1.6))
    s += line((L, 1.6), (L, 1.3)) + line((R, 1.6), (R, 1.3))
    s += res(L, 0.6, 90, "$R_2=1800$", "l") + res(R, 0.6, 90, "$R_4=600$", "r")
    s += line((L, -0.1), (L, -0.6)) + line((R, -0.1), (R, -0.6)) + line((L, -0.6), (R, -0.6)) + dot(ox, -0.6)
    s += line((ox, -0.6), (ox, -1.3)) + term(ox, -1.3)
    # the key between the middles of the branches
    s += dot(L, 1.6) + dot(R, 1.6) + line((L, 1.6), (ox - 0.7, 1.6)) + line((ox + 0.7, 1.6), (R, 1.6))
    if closed:
        s += rf"\keyk{{{ox}}}{{1.6}}{{0}}" + "\n"
    else:
        s += rf"\keyc{{{ox}}}{{1.6}}{{0}}" + "\n"
    return s


@fig("kr-gelfgat-11-36-scheme")
def _():
    R14, R23 = Fraction(600), Fraction(1800)
    R_open = (R14 + R23) / 2
    R_13 = R14 * R23 / (R14 + R23)
    R_closed = 2 * R_13
    assert R_open == 1200 and R_13 == 450 and R_closed == 900
    s = gelfgat_panel(0, False) + gelfgat_panel(9.6, True)
    s += txt(0, 5.3, "ключ разомкнут", style="font=\\bfseries\\small") + txt(9.6, 5.3, "ключ замкнут", style="font=\\bfseries\\small")
    s += txt(9.6, -2.2, "сопротивления в омах", style="font=\\footnotesize,text=grey")
    s += txt(0, -2.2, "$R_\\text{разомкн}=\\dfrac{R_{14}+R_{23}}{2}=1{,}2$~кОм", style="text=el")
    return s


@fig("kr-gelfgat-11-36-closed")
def _():
    """The scheme redrawn for the closed key: two parallel pairs in series."""
    R14, R23 = Fraction(600), Fraction(1800)
    R_13 = R14 * R23 / (R14 + R23)
    assert R_13 == 450 and 2 * R_13 == 900
    L, R = -1.4, 1.4
    s = term(0, 4.7) + line((0, 4.7), (0, 4.0)) + dot(0, 4.0) + line((L, 4.0), (R, 4.0))
    s += line((L, 4.0), (L, 3.6)) + line((R, 4.0), (R, 3.6))
    s += res(L, 2.9, 90, "$R_1=600$", "l") + res(R, 2.9, 90, "$R_3=1800$", "r")
    s += line((L, 2.2), (L, 1.8)) + line((R, 2.2), (R, 1.8)) + line((L, 1.8), (R, 1.8)) + dot(L, 1.8) + dot(R, 1.8)
    s += line((L, 1.8), (L, 1.4)) + line((R, 1.8), (R, 1.4))
    s += res(L, 0.7, 90, "$R_2=1800$", "l") + res(R, 0.7, 90, "$R_4=600$", "r")
    s += line((L, 0.0), (L, -0.4)) + line((R, 0.0), (R, -0.4)) + line((L, -0.4), (R, -0.4)) + dot(0, -0.4)
    s += line((0, -0.4), (0, -1.1)) + term(0, -1.1)
    s += dot(L, 4.0) + dot(R, 4.0) + dot(L, -0.4) + dot(R, -0.4)
    s += txt(3.3, 2.9, "$R_{13}=\\dfrac{600\\cdot1800}{600+1800}=450$~Ом", "west", "text=el")
    s += txt(3.3, 0.7, "$R_{24}=450$~Ом", "west", "text=el")
    s += txt(3.3, -0.75, "$R_\\text{замкн}=R_{13}+R_{24}=900$~Ом", "west", "text=el")
    return s


def units_scheme(values, unit, series=None, name="", answer=""):
    """Parallel resistors with a right part that replaces each of them by unit-sized resistors."""
    counts = [Fraction(unit, v) for v in values]
    assert all(c.denominator == 1 for c in counts)
    total = sum(int(c) for c in counts)
    n = len(values)
    dy = 1.25
    ys = [((n - 1) / 2 - i) * dy for i in range(n)]
    xl, xr = 1.3, 4.9
    s = line((xl, ys[0]), (xl, ys[-1])) + line((xr, ys[0]), (xr, ys[-1]))
    for y, v in zip(ys, values):
        s += line((xl, y), (2.4, y)) + line((3.8, y), (xr, y)) + res(3.1, y, 0, f"${v}$~Ом", "a")
    s += term(0, 0) + line((0, 0), (xl, 0)) + dot(xl, 0) + dot(xr, 0)
    if series:
        s += line((xr, 0), (5.6, 0)) + res(6.3, 0, 0, f"${series}$~Ом", "a") + line((7.0, 0), (7.6, 0)) + term(7.6, 0)
        x_end = 7.6
    else:
        s += line((xr, 0), (5.5, 0)) + term(5.5, 0)
        x_end = 5.5
    # the replacement
    x0 = x_end + 2.6
    s += txt(x_end + 1.0, 0, "$\\Longrightarrow$")
    for y, c in zip(ys, counts):
        s += rf"\draw[fill=soft,rounded corners=3pt]({x0 + 0.4:.3g},{y - 0.42:.3g})rectangle({x0 + 3.6:.3g},{y + 0.42:.3g});" + "\n"
        s += txt(x0 + 2.0, y, f"${int(c)}$ по ${unit}$~Ом", style="font=\\small")
        s += line((x0, y), (x0 + 0.4, y)) + line((x0 + 3.6, y), (x0 + 4.0, y))
    s += line((x0, ys[0]), (x0, ys[-1])) + line((x0 + 4.0, ys[0]), (x0 + 4.0, ys[-1]))
    s += term(x0 - 0.7, 0) + line((x0 - 0.7, 0), (x0, 0)) + dot(x0, 0) + dot(x0 + 4.0, 0)
    s += line((x0 + 4.0, 0), (x0 + 4.6, 0)) + term(x0 + 4.6, 0)
    s += txt(x0 + 2.0, ys[0] + 1.0, f"${total}$ одинаковых по ${unit}$~Ом", style="text=el")
    if series:
        s += txt(x0 + 2.0, ys[-1] - 1.0, f"$R_\\parallel=\\dfrac{{{unit}}}{{{total}}}$~Ом", style="text=el")
        s += txt(x0 + 2.0, ys[-1] - 2.1, f"$R=\\dfrac{{{unit}}}{{{total}}}+{series}=\\dfrac{{{unit + series * total}}}{{{total}}}$~Ом", style="text=el")
    else:
        s += txt(x0 + 2.0, ys[-1] - 1.0, f"$R=\\dfrac{{{unit}}}{{{total}}}\\approx{num(unit / total, 2, math=True)}$~Ом", style="text=el")
    return s


@fig("kr-ohm-20-units")
def _():
    R = Fraction(20, 17) + 1
    assert R == Fraction(37, 17) and abs(float(R) - 2.176) < 1e-3
    assert 1 / (Fraction(1, 2) + Fraction(1, 5) + Fraction(1, 10) + Fraction(1, 20)) == Fraction(20, 17)
    return units_scheme([2, 5, 10, 20], 20, series=1)


@fig("kr-ohm-24-units")
def _():
    R = Fraction(24, 13)
    assert R == 1 / (Fraction(1, 12) + Fraction(1, 4) + Fraction(1, 6) + Fraction(1, 24)) and abs(float(R) - 1.846) < 1e-3
    return units_scheme([12, 4, 6, 24], 24)


@fig("kr-fuse-wire")
def _():
    d, I, t0, tm = 0.2e-3, 10.0, 27.0, 327.0
    s = ""
    s += rf"\draw[fill=soft](0,-0.45)rectangle(9.0,0.45);" + "\n"
    s += line((-1.4, 0), (0, 0)) + line((9.0, 0), (10.4, 0))
    s += arr(-1.3, 0.3, -0.4, 0.3, "$I=10$~А", 0, 0.35)
    s += rf"\draw[<->,el](1.2,-0.45)--(1.2,0.45);" + "\n"
    s += txt(1.45, 0, "$d=0{,}2$~мм", "west", "text=el")
    s += rf"\draw[<->,el](0,-0.95)--(9.0,-0.95);" + "\n"
    s += txt(4.5, -1.35, "длина $l$ — в условии её нет и в ответ она не войдёт", "center", "text=el")
    s += txt(4.5, 1.25, "свинцовая проволока: $S=\\dfrac{\\pi d^2}{4}$, $m=\\rho_m S l$, $R=\\rho_R\\dfrac{l}{S}$", style="text=grey")
    assert abs(3.14159 * d**2 / 4 - 3.14e-8) < 2e-10
    return s


@fig("kr-fuse-heating")
def _():
    rho_m, c, rho_r = 11300.0, 140.0, 21e-8
    d, I, t0, tm = 0.2e-3, 10.0, 27.0, 327.0
    import math

    S = math.pi * d**2 / 4
    tau = rho_m * c * (tm - t0) / rho_r * (S / I) ** 2
    assert abs(tau - 0.0223) < 2e-4
    # lead wire: R = rho_r l / S, m = rho_m S l, so the heating rate I^2 R / (m c) does not depend on l
    rate = I**2 * rho_r / (rho_m * c * S**2)
    assert abs(rate * tau - (tm - t0)) < 1e-6
    tau_ms = tau * 1e3
    s = r"\draw[->](0,0)--(6.6,0)node[right]{$t$, мс};\draw[->](0,0)--(0,4.6)node[above]{$T$, $^\circ$C};" + "\n"
    xs = 6.0 / 25.0
    ys = 3.6 / 327.0
    x_tau, y_m, y_0 = tau_ms * xs, tm * ys, t0 * ys
    s += rf"\draw[cur,line width=1.4pt](0,{y_0:.3f})--({x_tau:.3f},{y_m:.3f});" + "\n"
    s += rf"\draw[dashed,grey](0,{y_m:.3f})--({x_tau:.3f},{y_m:.3f})--({x_tau:.3f},0);" + "\n"
    s += rf"\fill[cur]({x_tau:.3f},{y_m:.3f})circle(.07);\fill(0,{y_0:.3f})circle(.06);" + "\n"
    s += txt(-0.15, y_m, "$327$", "east") + txt(-0.15, y_0, "$27$", "east")
    s += txt(x_tau, -0.4, f"${tau_ms:.0f}$", style="text=el")
    s += txt(x_tau + 0.25, y_m + 0.5, "свинец плавится, цепь рвётся", "west", "text=cur")
    s += txt(5.35, 1.9, "нагревание с постоянной скоростью:\\\\все тепло идёт в проволоку", "west", "font=\\footnotesize,text=grey")
    return s


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        build(n, FIGS[n]())
