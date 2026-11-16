"""Circuit schemes for the note "Соединение проводников" (section f11, lessons 157-162).

The TikZ macros for lamp, meter, cell, resistor and voltage dimension come from circuit_diagrams.py and ohm_circuits.py.
Run: nix shell nixpkgs#poppler-utils -c python3 connections.py [name ...]
The system pdflatex needs the tikz package. PNG files go to content/11. Электрические явления/00. Вложения/ (prefix connection-)
The graphs are in connections_graphs.py
"""
import sys
from math import atan2, degrees, hypot

import circuit_diagrams as cd
import ohm_circuits  # noqa: F401  adds the resistor and voltage dimension macros to the shared preamble
from theme import num

cd.PREAMBLE += r"""
\usetikzlibrary{decorations.pathreplacing}
\newcommand{\term}[2]{\draw[fill=paper](#1,#2)circle(.075);}
"""

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


def f(v):
    return f"{v:.4g}"


def line(*pts, style=""):
    return "\\draw" + (f"[{style}]" if style else "") + "".join(f"({f(x)},{f(y)})--" for x, y in pts)[:-2] + ";\n"


def dot(x, y):
    return rf"\dotc{{{f(x)}}}{{{f(y)}}}" + "\n"


def term(x, y):
    return rf"\term{{{f(x)}}}{{{f(y)}}}" + "\n"


def txt(x, y, s, anchor="center", style=""):
    a = "" if anchor == "center" else f"anchor={anchor},"
    return rf"\node[cp,{a}{style}]at({f(x)},{f(y)}){{{s}}};" + "\n"


def res(x, y, rot=0, lab=None, side="a", style=""):
    """Resistor with leads of 0.7 cm each side; label above (a), below (b), right (r) or left (l)."""
    s = rf"\resc{{{f(x)}}}{{{f(y)}}}{{{rot}}}" + "\n"
    if lab:
        pos = {"a": (0, 0.21, "south"), "b": (0, -0.21, "north"), "r": (0.21, 0, "west"), "l": (-0.21, 0, "east")}[side]
        s += txt(x + pos[0], y + pos[1], lab, pos[2], style)
    return s


def sres(p, q, lab=None, side="a", style=""):
    """Resistor on the segment p-q with wires to the ends of the segment."""
    (x1, y1), (x2, y2) = p, q
    L = hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    m = (L / 2 - 0.7)
    s = line((x1, y1), (x1 + ux * m, y1 + uy * m)) + line((x2 - ux * m, y2 - uy * m), (x2, y2))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    s += rf"\resc{{{f(mx)}}}{{{f(my)}}}{{{f(degrees(atan2(uy, ux)))}}}" + "\n"
    if lab:
        nx, ny = -uy, ux
        k = 0.42 if side == "a" else -0.42
        s += txt(mx + nx * k, my + ny * k, lab, style=style)
    return s


def dim(x1, x2, y, lab, yref=None):
    s = rf"\vdim{{{f(x1)}}}{{{f(y)}}}{{{f(x2)}}}{{{lab}}}" + "\n"
    if yref is not None:
        s += rf"\draw[dashed,grey]({f(x1)},{f(yref)})--({f(x1)},{f(y)})({f(x2)},{f(yref)})--({f(x2)},{f(y)});" + "\n"
    return s


def arr(x1, y1, x2, y2, lab=None, lx=0, ly=0, anchor="center"):
    s = rf"\ca{{{f(x1)}}}{{{f(y1)}}}{{{f(x2)}}}{{{f(y2)}}}" + "\n"
    if lab:
        s += txt((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, lab, anchor, "text=cur")
    return s


def parblock(cx, cy, labels, dy=1.2, w=2.8, lead=0.55, side="a", stubs=True):
    """Resistors in parallel between two vertical buses, centred on (cx, cy). Returns (tikz, [branch y])."""
    n = len(labels)
    ys = [cy + (n - 1) / 2 * dy - i * dy for i in range(n)]
    xl, xr = cx - w / 2, cx + w / 2
    s = line((xl, ys[0]), (xl, ys[-1])) + line((xr, ys[0]), (xr, ys[-1]))
    for y, lab in zip(ys, labels):
        s += line((xl, y), (cx - 0.7, y)) + line((cx + 0.7, y), (xr, y))
        s += res(cx, y, 0, lab, side)
    if stubs:
        s += line((xl - lead, cy), (xl, cy)) + line((xr, cy), (xr + lead, cy)) + dot(xl, cy) + dot(xr, cy)
    return s, ys


@fig("connection-series-scheme")
def _():
    s = ""
    s += term(0, 0) + line((0, 0), (0.5, 0))
    xs = [1.2, 3.6, 7.2]
    labs = ["$R_1$", "$R_2$", "$R_N$"]
    s += line((1.9, 0), (2.9, 0)) + line((4.3, 0), (4.7, 0)) + line((6.1, 0), (6.5, 0)) + line((7.9, 0), (8.6, 0)) + term(8.6, 0)
    for x, lab in zip(xs, labs):
        s += res(x, 0, 0, lab, "b")
        s += dim(x - 0.7, x + 0.7, 1.15, f"$U_{lab[3:-1]}$", 0.05)
        s += arr(x - 0.4, -1.0, x + 0.4, -1.0, f"$I_{lab[3:-1]}$", 0, -0.35)
    s += txt(5.4, 0, "$\\dots$")
    s += dim(0, 8.6, -2.4, "$U$", -0.1)
    s += arr(-1.1, 0.0, -0.35, 0.0, "$I$", 0, 0.35)
    s += txt(9.9, 0, "$\\Longrightarrow$")
    s += term(11.2, 0) + line((11.2, 0), (11.7, 0)) + res(12.4, 0, 0, "$R_\\text{посл}=\\,?$", "a") + line((13.1, 0), (13.6, 0)) + term(13.6, 0)
    s += dim(11.2, 13.6, -2.4, "$U$", -0.1)
    s += arr(10.5, -0.0, 11.1, 0.0, None)
    s += arr(13.7, 0.0, 14.4, 0.0, "$I$", 0, 0.35)
    return s


@fig("connection-parallel-scheme")
def _():
    s = ""
    ys = [2.4, 1.0, -1.6]
    labs = ["$R_1$", "$R_2$", "$R_N$"]
    s += line((1.0, 2.4), (1.0, -1.6)) + line((5.8, 2.4), (5.8, -1.6))
    for y, lab, i in zip(ys, labs, ["1", "2", "N"]):
        s += line((1.0, y), (2.7, y)) + line((4.1, y), (5.8, y)) + res(3.4, y, 0, lab, "a")
        s += arr(1.4, y - 0.3, 2.3, y - 0.3, f"$I_{i}$", 0, -0.32)
    s += txt(3.4, -0.3, "$\\vdots$")
    s += term(-0.8, 0) + line((-0.8, 0), (1.0, 0)) + dot(1.0, 0) + dot(1.0, 1.0) + dot(5.8, 0) + dot(5.8, 1.0)
    s += line((5.8, 0), (6.6, 0)) + term(6.6, 0)
    s += txt(0.95, 3.0, "узел", "center", "text=grey") + txt(5.85, 3.0, "узел", "center", "text=grey")
    s += arr(-1.6, 0.0, -0.9, 0.0, "$I$", 0, 0.35)
    s += arr(6.7, 0.0, 7.4, 0.0, "$I$", 0, 0.35)
    s += dim(-0.8, 6.6, -3.0, "$U$", -0.1)
    s += txt(8.7, 0, "$\\Longrightarrow$")
    s += term(9.9, 0) + line((9.9, 0), (10.4, 0)) + res(11.1, 0, 0, "$R_\\text{пар}=\\,?$", "a") + line((11.8, 0), (12.3, 0)) + term(12.3, 0)
    s += dim(9.9, 12.3, -3.0, "$U$", -0.1)
    return s


@fig("connection-resistance-box")
def _():
    digits = [2, 0, 1, 9, 0, 0]
    mult = ["1000", "100", "10", "1", "0{,}1", "0{,}01"]
    vals = ["2000", "0", "10", "9", "0", "0"]
    s = term(0, 0) + line((0, 0), (0.4, 0))
    x = 0.4
    for d, m, v in zip(digits, mult, vals):
        s += rf"\draw[fill=soft,rounded corners=3pt]({f(x)},-.75)rectangle({f(x + 1.9)},.75);" + "\n"
        s += txt(x + 0.95, 0.42, f"$\\times{m}$", style="font=\\footnotesize")
        s += rf"\draw[fill=paper]({f(x + 0.95)},-.02)circle(.27);" + "\n"
        s += txt(x + 0.95, -0.02, f"\\bfseries {d}")
        s += txt(x + 0.95, -1.15, f"${num(v, '', math=True)}$~Ом", style="font=\\footnotesize")
        s += line((x + 1.9, 0), (x + 2.1, 0))
        x += 2.1
    s += line((x - 0.2, 0), (x, 0)) + term(x, 0)
    s += dim(0, x, -2.05, "$R=2000+0+10+9+0+0=2019$~Ом", -0.1)
    return s


@fig("connection-trap-triangle")
def _():
    s = ""
    # left panel: the triangle as drawn on the board
    BL, A, BR, TR = (0, 0), (2.0, 2.2), (4.0, 0), (5.6, 2.2)
    s += line(BL, BR) + line(A, TR)
    s += sres(BL, A, "$R_1$", "a") + sres(A, BR, "$R_2$", "b") + sres(BR, TR, "$R_3$", "b")
    s += term(-0.9, 0) + line((-0.9, 0), BL) + term(6.5, 2.2) + line(TR, (6.5, 2.2))
    for p in (BL, A, BR, TR):
        s += dot(*p)
    s += txt(0.0, -0.45, "1", style="text=el") + txt(4.0, -0.45, "1", style="text=el")
    s += txt(2.0, 2.65, "2", style="text=cur") + txt(5.6, 2.65, "2", style="text=cur")
    s += txt(2.8, -1.4, "один узел $1$ (внизу) и один узел $2$ (вверху)")
    # right panel: the same resistors as three parallel branches
    s += txt(7.3, 1.1, "$\\Longrightarrow$")
    ox = 9.2
    s += line((ox, 2.2), (ox, 0)) + line((ox + 4.4, 2.2), (ox + 4.4, 0))
    ys = [2.2, 1.1, 0.0]
    for y, lab in zip(ys, ["$R_1$", "$R_2$", "$R_3$"]):
        # the resistor at ox + 2.2 has leads from ox + 1.5 to ox + 2.9
        s += line((ox, y), (ox + 1.5, y)) + line((ox + 2.9, y), (ox + 4.4, y)) + res(ox + 2.2, y, 0, lab, "a")
    s += dot(ox, 1.1) + dot(ox + 4.4, 1.1)
    s += term(ox - 0.7, 1.1) + line((ox - 0.7, 1.1), (ox, 1.1)) + term(ox + 5.1, 1.1) + line((ox + 4.4, 1.1), (ox + 5.1, 1.1))
    s += txt(ox, 2.75, "$1$", style="text=el") + txt(ox + 4.4, 2.75, "$2$", style="text=cur")
    s += txt(ox + 2.2, -1.4, "три резистора параллельно")
    return s


@fig("connection-tricks-10-20")
def _():
    s = ""
    w = 2.8
    # panel 1: 10 and 20 in parallel
    b, ys = parblock(0, 0, ["$10$", "$20$"], dy=1.3, w=w)
    s += b + txt(0, -1.55, "$10\\parallel20$")
    s += txt(2.9, 0, "$\\Longrightarrow$")
    # panel 2: the 10 is two 20 in parallel
    cx = 6.4
    b, ys = parblock(cx, 0, ["$20$", "$20$", "$20$"], dy=1.05, w=w)
    s += b
    s += rf"\draw[el,dashed,rounded corners=5pt]({f(cx - w / 2 + 0.25)},{f(ys[0] + 0.85)})rectangle({f(cx + w / 2 - 0.25)},{f(ys[1] - 0.3)});" + "\n"
    s += txt(cx + 2.35, (ys[0] + ys[1]) / 2 + 0.05, "$=10$", "west", "text=el")
    s += txt(cx, -1.9, "$10$ заменено двумя по $20$")
    s += txt(10.4, 0, "$\\Longrightarrow$")
    # panel 3: three 20 in parallel
    cx = 13.8
    b, ys = parblock(cx, 0, ["$20$", "$20$", "$20$"], dy=1.05, w=w)
    s += b + txt(cx, -1.9, "$R=\\dfrac{20}{3}\\approx6{,}7$")
    return s


@fig("connection-six-parallel")
def _():
    R = [10, 12, 15, 20, 30, 60]
    n = [60 // r for r in R]
    b, ys = parblock(0, 0, [f"${r}$" for r in R], dy=1.05, w=2.8)
    s = b
    for y, k in zip(ys, n):
        s += txt(2.4, y, f"${k}$ по $60$", "west", "text=el")
    # sum(n) = 21 takes the singular "резистор"
    s += txt(0, -3.4, f"всего ${sum(n)}$ резистор по $60$ Ом: $R=\\dfrac{{60}}{{{sum(n)}}}=\\dfrac{{20}}{{7}}$~Ом")
    return s


def battery_left_plus_down(x, y):
    return rf"\cellc{{{f(x)}}}{{{f(y)}}}{{-90}}{{3}}" + "\n"


@fig("connection-task-7-2")
def _():
    s = ""
    s += line((0, 0), (0, 3), (1.0, 3)) + line((3.2, 3), (4.5, 3)) + line((5.9, 3), (7.2, 3), (7.2, 0))
    s += rf"\celld{{2.1}}{{3}}{{180}}" + "\n"
    s += txt(2.9, 2.6, "$+$") + txt(1.3, 2.6, "$-$")
    s += rf"\meterc{{5.2}}{{3}}{{0}}{{A}}" + "\n"
    s += line((0, 0), (1.2, 0)) + line((2.6, 0), (3.6, 0)) + line((5.0, 0), (7.2, 0))
    s += res(1.9, 0, 0, "$R_1=0{,}5$~Ом", "a") + res(4.3, 0, 0, "$R_2=2{,}5$~Ом", "a")
    s += dim(1.0, 3.2, 4.2, "$U_\\text{ист}=\\,?$", 3.05)
    s += dim(1.2, 2.6, -1.35, "$U_1=\\,?$", -0.05)
    s += dim(0, 7.2, -2.3, "$U_\\text{ист}$", -0.05)
    s += arr(6.0, 3.8, 6.8, 3.8, "$I=1$~А", 0, 0.32)
    return s


@fig("connection-task-7-15")
def _():
    s = ""
    s += line((0, 0), (0, 3.2), (3.1, 3.2)) + line((5.1, 3.2), (8.4, 3.2), (8.4, 0))
    s += rf"\celld{{4.1}}{{3.2}}{{0}}" + "\n"
    s += txt(3.3, 3.6, "$+$") + txt(4.9, 3.6, "$-$")
    s += line((0, 0), (0.7, 0)) + line((2.1, 0), (2.8, 0)) + line((4.2, 0), (5.5, 0)) + line((6.9, 0), (8.4, 0))
    s += res(1.4, 0, 0, "$R_1=1$~Ом", "a") + res(3.5, 0, 0, "$R_2=4$~Ом", "a") + res(6.2, 0, 0, "$R_3=2$~Ом", "a")
    s += line((2.8, 0), (2.8, -1.7), (3.1, -1.7)) + line((3.9, -1.7), (4.2, -1.7), (4.2, 0))
    s += rf"\draw(3.5,-1.7)circle(.4);\node[font=\small]at(3.5,-1.7){{V}};" + "\n"
    s += dot(2.8, 0) + dot(4.2, 0)
    s += dim(5.5, 6.9, 1.3, "$U_3=\\,?$", 0.05)
    s += dim(0, 8.4, 4.6, "$U_\\text{ист}=\\,?$", 3.25)
    s += txt(3.5, -2.55, "$U_2=4$~В")
    s += arr(-0.35, 2.4, -0.35, 1.2, "$I=\\,?$", -0.7, 0)
    return s


@fig("connection-task-7-12")
def _():
    s = term(0, 0) + line((0, 0), (1.1, 0)) + res(1.8, 0, 0, "$R_1=6$~Ом", "a") + line((2.5, 0), (3.3, 0)) + res(4.0, 0, 0, "$R_2=2$~Ом", "a")
    s += line((4.7, 0), (5.5, 0)) + rf"\meterc{{6.2}}{{0}}{{0}}{{A}}" + "\n" + line((6.9, 0), (7.6, 0)) + term(7.6, 0)
    for cx, lab in [(1.8, "$V_1$"), (4.0, "$V_2$")]:
        s += line((cx - 0.7, 0), (cx - 0.7, -1.7)) + line((cx + 0.7, 0), (cx + 0.7, -1.7))
        s += rf"\meterc{{{f(cx)}}}{{-1.7}}{{0}}{{{lab}}}" + "\n"
        s += dot(cx - 0.7, 0) + dot(cx + 0.7, 0)
    s += txt(1.8, -2.4, "$U_1=18$~В") + txt(4.0, -2.4, "$U_2=\\,?$")
    s += arr(-1.0, 0, -0.35, 0, "$I=\\,?$", 0, 0.35)
    return s


@fig("connection-task-7-19")
def _():
    s = ""
    # lamp on top, ammeter on the right, battery at the bottom, rheostat on the left
    s += line((0, 2.5), (0, 3.4), (2.3, 3.4)) + line((3.7, 3.4), (6.2, 3.4), (6.2, 2.3)) + line((6.2, 0.9), (6.2, 0), (4.1, 0))
    s += line((1.9, 0), (0, 0), (0, 0.9))
    s += rf"\lampc{{3.0}}{{3.4}}{{0}}" + "\n" + rf"\meterc{{6.2}}{{1.6}}{{90}}{{A}}" + "\n" + rf"\celld{{3.0}}{{0}}{{0}}" + "\n"
    s += txt(1.7, 0.4, "$+$") + txt(4.3, 0.4, "$-$")
    s += rf"\rheoc{{0}}{{1.6}}{{90}}" + "\n"
    s += line((-0.65, 1.75), (-1.0, 1.75), (-1.0, 0.9), (0, 0.9)) + dot(0, 0.9)
    s += txt(0.3, 1.6, "$R_\\text{р}=\\,?$", "west")
    s += txt(4.0, 3.85, "лампа $R_\\text{л}=3$~Ом", "west", "font=\\small")
    s += dim(2.3, 3.7, 4.7, "$U_\\text{л}=5{,}1$~В", 3.45)
    s += dim(1.9, 4.1, -1.25, "$U=9$~В", -0.05)
    s += arr(0.5, 3.75, 1.3, 3.75, "$I$", 0, 0.3)
    return s


@fig("connection-task-8-20")
def _():
    s = ""
    s += line((0, 2.7), (0, 3.6), (1.6, 3.6)) + line((3.0, 3.6), (7.0, 3.6), (7.0, 2.5)) + line((0, 0.9), (0, 0), (7.0, 0), (7.0, 1.1))
    s += rf"\cellc{{0}}{{1.8}}{{-90}}{{3}}" + "\n"
    s += txt(-0.4, 2.4, "$+$") + txt(-0.4, 1.2, "$-$")
    s += rf"\meterc{{2.3}}{{3.6}}{{0}}{{A}}" + "\n"
    s += line((4.9, 3.6), (4.9, 2.5)) + line((4.9, 1.1), (4.9, 0))
    s += res(4.9, 1.8, 90, "$R_1=180$~Ом", "l") + res(7.0, 1.8, 90, "$R_2=60$~Ом", "r")
    s += dot(4.9, 3.6) + dot(4.9, 0)
    s += arr(2.9, 4.1, 3.6, 4.1, "$I=\\,?$", 0, 0.32)
    s += arr(5.35, 2.7, 5.35, 1.5, "$I_1$", 0.3, 0)
    s += arr(6.55, 2.7, 6.55, 1.5, "$I_2$", -0.3, 0)
    s += txt(-1.0, 1.8, "$U=22{,}5$~В", "east")
    return s


@fig("connection-task-8-24")
def _():
    s = term(-0.8, 0) + line((-0.8, 0), (1.0, 0)) + dot(1.0, 0) + dot(5.8, 0) + line((5.8, 0), (6.6, 0)) + term(6.6, 0)
    s += line((1.0, 1.1), (1.0, -1.1)) + line((5.8, 1.1), (5.8, -1.1))
    for y, lab, i in [(1.1, "$R_1=500$~Ом", "1"), (-1.1, "$R_2=1{,}5$~кОм", "2")]:
        s += line((1.0, y), (2.7, y)) + line((4.1, y), (5.8, y)) + res(3.4, y, 0, lab, "a")
        s += arr(1.4, y - 0.3, 2.2, y - 0.3, f"$I_{i}$", 0, -0.32)
    s += arr(-1.6, 0, -0.9, 0, "$I_\\text{общ}$", 0, 0.38)
    s += arr(6.7, 0, 7.4, 0, "$I_\\text{общ}$", 0, 0.38)
    s += txt(3.4, -2.55, "$U$ считаем известным: в ответ оно не войдёт", style="font=\\small")
    return s


@fig("connection-task-8-28")
def _():
    s = ""
    xs = [1.4, 4.8, 8.2]
    s += line((0, 3.3), (8.2, 3.3)) + line((0, 0), (8.2, 0)) + term(0, 3.3) + term(0, 0)
    for x, lab, i in zip(xs, ["$R_1=4$~Ом", "$R_2=6$~Ом", "$R_3=8$~Ом"], "123"):
        # the vertical resistor at y = 1.65 has leads from 0.95 to 2.35
        s += line((x, 3.3), (x, 2.35)) + line((x, 0.95), (x, 0)) + res(x, 1.65, 90, lab, "r")
        s += arr(x - 0.4, 2.35, x - 0.4, 1.0, f"$I_{i}$", -0.32, 0)
    s += dot(1.4, 3.3) + dot(4.8, 3.3) + dot(1.4, 0) + dot(4.8, 0)
    s += rf"\draw[<->,el](-.9,3.3)--(-.9,0);\node[el,font=\small,fill=paper,inner sep=1pt,rotate=90]at(-.9,1.65){{$U=2{{,}}4$~В}};" + "\n"
    s += txt(4.8, -0.75, "$R_\\text{общ}=\\,?$, $I_1,I_2,I_3=\\,?$")
    return s


@fig("connection-task-8-28-check")
def _():
    s = ""
    w = 2.2
    counts = [6, 4, 3]
    caps = ["$4=\\dfrac{24}{6}$", "$6=\\dfrac{24}{4}$", "$8=\\dfrac{24}{3}$"]
    cx = 0.0
    for n, cap in zip(counts, caps):
        b, ys = parblock(cx, 0, [None] * n, dy=0.7, w=w, lead=0.0, stubs=False)
        s += b + txt(cx, -2.6, cap)
        s += txt(cx, 2.3, f"${n}$ по $24$~Ом", style="text=el")
        cx += 4.0
    s += txt(4.0, -3.4, "$6+4+3=13$ резисторов по $24$ Ом параллельно: $R=\\dfrac{24}{13}$~Ом")
    return s


@fig("connection-task-12-34")
def _():
    s = ""
    # the circuit as drawn in the problem book
    P1, C, Y, M = (0, 2.6), (2.4, 2.6), (5.0, 2.6), (2.5, 0.9)
    s += sres(P1, C, "$R_1$", "a") + sres(C, Y, "$R_3$", "a") + sres(C, M, "$R_2$", "a") + sres(Y, M, "$R_4$", "a")
    s += line(P1, M) + line(P1, (0, 0), (0.2, 0)) + line((2.4, 0), (3.5, 0)) + line((4.9, 0), (5.0, 0), Y)
    s += rf"\celld{{1.3}}{{0}}{{0}}" + "\n" + rf"\meterc{{4.2}}{{0}}{{0}}{{A}}" + "\n"
    s += txt(0.25, -0.4, "$+$") + txt(2.35, -0.4, "$-$")
    for p in (P1, C, Y, M):
        s += dot(*p)
    s += txt(2.5, -1.2, "как нарисовано в условии")
    # the same circuit redrawn
    ox = 8.0
    s += line((ox, 2.4), (ox + 1.3, 2.4)) + line((ox, 0), (ox + 2.5, 0)) + line((ox + 3.9, 0), (ox + 6.4, 0))
    b, ys = parblock(ox + 2.6, 2.4, ["$R_1$", "$R_2$"], dy=1.2, w=2.6, lead=0.0, stubs=False)
    s += b + dot(ox + 1.3, 2.4) + dot(ox + 3.9, 2.4)
    s += line((ox + 3.9, 2.4), (ox + 4.3, 2.4)) + res(ox + 5.0, 2.4, 0, "$R_3$", "a") + line((ox + 5.7, 2.4), (ox + 6.4, 2.4))
    s += res(ox + 3.2, 0, 0, "$R_4$", "a")
    s += line((ox, 2.4), (ox, -1.8)) + line((ox + 6.4, 2.4), (ox + 6.4, -1.8))
    s += line((ox, -1.8), (ox + 0.2, -1.8)) + line((ox + 2.4, -1.8), (ox + 3.5, -1.8)) + line((ox + 4.9, -1.8), (ox + 6.4, -1.8))
    s += rf"\celld{{{f(ox + 1.3)}}}{{-1.8}}{{0}}" + "\n" + rf"\meterc{{{f(ox + 4.2)}}}{{-1.8}}{{0}}{{A}}" + "\n"
    s += txt(ox + 0.25, -2.2, "$+$") + txt(ox + 2.35, -2.2, "$-$")
    s += dot(ox, 0) + dot(ox + 6.4, 0)
    s += rf"\draw[el,dashed,rounded corners=6pt]({f(ox + 1.0)},.8)rectangle({f(ox + 6.0)},3.75);" + "\n"
    s += txt(ox + 3.5, 4.4, "$R_{123}=\\dfrac{R_1R_2}{R_1+R_2}+R_3$", style="text=el")
    s += arr(ox + 6.9, -0.4, ox + 6.9, -1.4, "$I$", 0.35, 0)
    s += txt(ox + 3.2, -3.0, "перерисовано: $R_{123}$ параллельно $R_4$")
    s += txt(5.6, 1.2, "$\\Longrightarrow$")
    return s


@fig("connection-task-11-22b")
def _():
    s = term(0, 1.5) + line((0, 1.5), (0.9, 1.5)) + res(1.6, 1.5, 0, "$R_1$", "a") + line((2.3, 1.5), (3.2, 1.5))
    s += line((3.2, 2.5), (3.2, 0.5)) + line((6.6, 2.5), (6.6, 0.5))
    for y, lab in [(2.5, "$R_2$"), (0.5, "$R_3$")]:
        s += line((3.2, y), (4.2, y)) + line((5.6, y), (6.6, y)) + res(4.9, y, 0, lab, "a")
    s += dot(3.2, 1.5) + dot(6.6, 1.5) + line((6.6, 1.5), (7.5, 1.5)) + term(7.5, 1.5)
    s += arr(0.1, 1.9, 0.8, 1.9, "$I_1$", 0, 0.3) + arr(3.5, 2.05, 4.1, 2.05, "$I_2$", 0, -0.3) + arr(3.5, 0.05, 4.1, 0.05, "$I_3$", 0, -0.3)
    s += dim(0, 7.5, -1.0, "$U=12$~В, $R=1$~кОм", 1.45)
    return s


@fig("connection-task-11-22v")
def _():
    s = term(0, 1.5) + line((0, 1.5), (1.0, 1.5)) + dot(1.0, 1.5) + dot(7.2, 1.5) + line((7.2, 1.5), (8.2, 1.5)) + term(8.2, 1.5)
    s += line((1.0, 3.0), (1.0, 0)) + line((7.2, 3.0), (7.2, 0))
    s += line((1.0, 3.0), (3.1, 3.0)) + line((4.5, 3.0), (7.2, 3.0)) + res(3.8, 3.0, 0, "$R_1$", "a")
    s += line((1.0, 1.5), (1.5, 1.5)) + line((2.9, 1.5), (5.7, 1.5)) + line((7.1, 1.5), (7.2, 1.5))
    s += line((1.0, 0), (3.1, 0)) + line((4.5, 0), (7.2, 0)) + res(3.8, 0, 0, "$R_4$", "a")
    s += res(2.2, 1.5, 0, "$R_2$", "a") + res(6.4, 1.5, 0, "$R_3$", "a")
    # the extension lines start at the terminals (y = 1.5)
    s += dim(0, 8.2, -1.0, "$U=12$~В, $R=1$~кОм", 1.4)
    return s


def panel_1132(ox, oy, stage):
    """The circuit of task 11.32 at one of four simplification stages."""
    s = f"\\begin{{scope}}[shift={{({ox},{oy})}}]\n"
    X, W = (3.0, 3.0), (3.0, 0)
    if stage == 0:
        s += term(0, 3) + line((0, 3), (0.8, 3)) + res(1.5, 3, 0, "$R_1$", "a") + line((2.2, 3), (3.0, 3))
        s += line((3.0, 3), (3.8, 3)) + res(4.5, 3, 0, "$R_2$", "a") + line((5.2, 3), (6.0, 3), (6.0, 2.2)) + res(6.0, 1.5, 90, "$R_4$", "r") + line((6.0, 0.8), (6.0, 0), (5.2, 0))
        s += res(4.5, 0, 0, "$R_6$", "b") + line((3.8, 0), (3.0, 0))
        s += line((3.0, 3), (3.0, 2.2)) + res(3.0, 1.5, 90, "$R_3$", "l") + line((3.0, 0.8), (3.0, 0))
        s += line((3.0, 0), (2.2, 0)) + res(1.5, 0, 0, "$R_5$", "b") + line((0.8, 0), (0, 0)) + term(0, 0)
        s += dot(3.0, 3) + dot(3.0, 0)
        cap = "исходная цепь"
    elif stage == 1:
        s += term(0, 3) + line((0, 3), (0.8, 3)) + res(1.5, 3, 0, "$R_1$", "a") + line((2.2, 3), (3.0, 3), (4.6, 3), (4.6, 2.2))
        s += res(3.0, 1.5, 90, "$R_3$", "l") + res(4.6, 1.5, 90, "$3R$", "r", "text=el")
        s += line((3.0, 3), (3.0, 2.2)) + line((3.0, 0.8), (3.0, 0), (4.6, 0), (4.6, 0.8)) + dot(3.0, 3) + dot(3.0, 0)
        s += line((3.0, 0), (2.2, 0)) + res(1.5, 0, 0, "$R_5$", "b") + line((0.8, 0), (0, 0)) + term(0, 0)
        s += rf"\draw[el,dashed,rounded corners=4pt](4.15,.45)rectangle(5.6,2.55);" + "\n"
        cap = "$R_2+R_4+R_6=3R$"
    elif stage == 2:
        s += term(0, 3) + line((0, 3), (0.8, 3)) + res(1.5, 3, 0, "$R_1$", "a") + line((2.2, 3), (3.0, 3), (3.0, 2.2))
        s += res(3.0, 1.5, 90, "$\\dfrac{3R}{4}$", "r", "text=el") + line((3.0, 0.8), (3.0, 0), (2.2, 0)) + res(1.5, 0, 0, "$R_5$", "b") + line((0.8, 0), (0, 0)) + term(0, 0)
        s += rf"\draw[el,dashed,rounded corners=4pt](2.35,.45)rectangle(4.3,2.55);" + "\n"
        cap = "$3R\\parallel R=\\dfrac{3R}{4}$"
    else:
        s += term(0, 1.5) + line((0, 1.5), (0.7, 1.5)) + res(1.4, 1.5, 0, "$\\dfrac{11R}{4}$", "a", "text=el") + line((2.1, 1.5), (2.8, 1.5)) + term(2.8, 1.5)
        cap = "$R_1+\\dfrac{3R}{4}+R_5=\\dfrac{11R}{4}$"
    s += txt(3.0, -1.1 if stage < 3 else -0.5, cap)
    s += "\\end{scope}\n"
    return s


@fig("connection-task-11-32")
def _():
    return panel_1132(0, 0, 0) + panel_1132(8.0, 0, 1) + panel_1132(0, -6.0, 2) + panel_1132(8.0, -5.6, 3)


@fig("connection-task-8-33")
def _():
    s = ""
    s += txt(0, 3.0, "целый провод", "west", "font=\\bfseries")
    s += line((0, 2.2), (0.5, 2.2)) + rf"\draw[fill=soft](.5,1.9)rectangle(5.5,2.5);\draw(5.5,2.2)--(6.0,2.2);" + "\n"
    s += txt(3.0, 1.25, "$R_0$ — надо найти")
    s += txt(3.0, 0.75, "разрезан на $n=3$ равных куска")
    s += txt(7.0, 2.2, "$\\Longrightarrow$")
    # three pieces, connected in parallel
    b, ys = parblock(11.0, 2.2, ["$R_1=\\dfrac{R_0}{n}$"] * 3, dy=1.35, w=3.0)
    s += b
    s += txt(11.0, -0.6, "параллельно: $R=\\dfrac{R_1}{n}=3$~Ом")
    return s


@fig("connection-task-649")
def _():
    s = ""
    # one continuous wire: thick part, cone inside the die and thin part share one fill; the outline has no cross lines
    s += rf"\fill[soft](-3.2,-.8)--(0,-.8)--(1.7,-.4)--(8.4,-.4)--(8.4,.4)--(1.7,.4)--(0,.8)--(-3.2,.8)--cycle;" + "\n"
    s += rf"\draw[fill=grey!45](0,1.7)--(1.7,1.7)--(1.7,.4)--(0,.8)--cycle;\draw[fill=grey!45](0,-1.7)--(1.7,-1.7)--(1.7,-.4)--(0,-.8)--cycle;" + "\n"
    s += rf"\draw(0,.8)--(-3.2,.8)--(-3.2,-.8)--(0,-.8);\draw(1.7,.4)--(8.4,.4)--(8.4,-.4)--(1.7,-.4);" + "\n"
    s += txt(-1.5, 1.15, "$S$", style="") + txt(5.0, 0.85, "$S/4$")
    s += rf"\draw[<->](-3.2,-1.3)--(0,-1.3);\node[cp,fill=paper]at(-1.6,-1.3){{$l$}};" + "\n"
    s += rf"\draw[<->](1.7,-1.3)--(8.4,-1.3);\node[cp,fill=paper]at(5.0,-1.3){{$4l$}};" + "\n"
    # the wire is pulled out of the die, not pushed in: only the pulling arrow at the exit
    s += arr(8.5, 0, 9.0, 0)
    s += txt(0.85, 2.15, "волока (фильера)")
    s += txt(-1.5, -2.2, "объём $V=Sl$ тот же: $S'l'=Sl$", "west")
    return s


@fig("connection-task-839-ring")
def _():
    s = ""
    r = 1.6
    s += rf"\draw[cur,line width=2.2pt](-100:{r}) arc(-100:30:{r});" + "\n"
    s += rf"\draw[el,line width=2.2pt](30:{r}) arc(30:260:{r});" + "\n"
    s += rf"\fill(30:{r})circle(.08)(-100:{r})circle(.08);" + "\n"
    s += txt(-0.4, 0.0, "$R_0=360$~Ом")
    s += txt(2.35, -0.6, "$R$", style="text=cur")
    s += txt(-2.25, 0.6, "$R_0-R$", style="text=el")
    s += rf"\draw(30:{r})--(4.2,1.3);\draw(-100:{r})--(-0.2,-2.2)--(4.2,-2.2);" + "\n"
    s += rf"\draw(4.2,1.3)--(4.2,0.05)(4.2,-2.2)--(4.2,-0.95);\draw(4.2,-0.45)circle(.5);\node at(4.2,-.45){{$\Omega$}};" + "\n"
    s += txt(4.9, -0.45, "$r=80$~Ом?", "west")
    return s


def rhombus_nodes():
    A, B = (0, 2.4), (0, -2.4)
    Q, P = (-1.8, 0), (1.8, 0)
    M1, M2, M3, M4 = (-0.9, 1.2), (0.9, 1.2), (-0.9, -1.2), (0.9, -1.2)
    C = (0, 0)
    return A, B, Q, P, M1, M2, M3, M4, C


def rhombus(ox, oy, mode, r_label=True):
    """mode 0: original; 1: centre split with a thin wire; 2: the wire removed."""
    A, B, Q, P, M1, M2, M3, M4, C = rhombus_nodes()
    s = f"\\begin{{scope}}[shift={{({ox},{oy})}}]\n"
    CL, CR = (-0.14, 0), (0.14, 0)
    ends = [(A, M1), (A, M2), (M1, Q), (M2, P), (Q, M3), (P, M4), (M3, B), (M4, B)]
    for p, q in ends:
        s += sres(p, q)
    if mode == 0:
        for m in (M1, M2, M3, M4):
            s += sres(m, C)
    else:
        for m in (M1, M3):
            s += sres(m, CL)
        for m in (M2, M4):
            s += sres(m, CR)
        s += dot(*CL) + dot(*CR)
        if mode == 1:
            s += rf"\draw[cur,line width=1.4pt]({f(CL[0])},0)--({f(CR[0])},0);" + "\n"
    for p in (A, B, Q, P, M1, M2, M3, M4) + ((C,) if mode == 0 else ()):
        s += dot(*p)
    s += txt(0.0, 2.85, "$A$") + txt(0.0, -2.85, "$B$")
    s += "\\end{scope}\n"
    return s


@fig("connection-task-o40")
def _():
    s = rhombus(0, 0, 0) + txt(0, -3.5, "исходная цепь, каждое звено $r$")
    s += rhombus(6.0, 0, 1) + txt(6.0, -3.5, "разорвали центр и вставили провод")
    # the label stands inside the lower diamond with a leader to the central wire
    s += txt(6.0, -1.5, "тока\\\\нет", style="text=cur")
    s += r"\draw[cur,-{Stealth[length=2mm]}](6.0,-1.12)--(6.0,-0.15);" + "\n"
    s += rhombus(12.0, 0, 2) + txt(12.0, -3.5, "провод убрали: две одинаковые половины")
    return s


@fig("connection-task-o40-equivalent")
def _():
    s = ""
    # left half chain: r, (2r || 2r) = r, r
    s += term(0, 0) + line((0, 0), (0.5, 0)) + res(1.2, 0, 0, "$r$", "a") + line((1.9, 0), (2.4, 0))
    b, ys = parblock(3.6, 0, ["$2r$", "$2r$"], dy=1.2, w=2.4, lead=0.0, stubs=False)
    s += b + dot(2.4, 0) + dot(4.8, 0)
    s += line((4.8, 0), (5.3, 0)) + res(6.0, 0, 0, "$r$", "a") + line((6.7, 0), (7.2, 0)) + term(7.2, 0)
    s += rf"\draw[el,decorate,decoration={{brace,amplitude=6pt,mirror}}](0.5,-1.5)--(6.7,-1.5);" + "\n"
    s += txt(3.6, -2.15, "одна половина: $r+r+r=3r$", style="text=el")
    s += txt(8.3, 0, "$\\Longrightarrow$")
    b, ys = parblock(11.2, 0, ["$3r$", "$3r$"], dy=1.2, w=2.6)
    s += b + txt(11.2, -2.15, "$R_{AB}=\\dfrac{3r}{2}=3$~Ом")
    return s


def cube_pts():
    dx, dy = 1.7, 1.25
    P = {"A": (0, 0), "B": (3.2, 0), "B1": (3.2, 3.2), "A1": (0, 3.2)}
    P["D"] = (dx, dy)
    P["C"] = (3.2 + dx, dy)
    P["C1"] = (3.2 + dx, 3.2 + dy)
    P["D1"] = (dx, 3.2 + dy)
    return P


@fig("connection-task-o44a-cube")
def _():
    P = cube_pts()
    edges_front = [("A", "B"), ("B", "B1"), ("B1", "A1"), ("A1", "A"), ("B", "C"), ("B1", "C1"), ("A1", "D1"), ("D1", "C1"), ("C", "C1")]
    edges_hidden = [("A", "D"), ("D", "C"), ("D", "D1")]
    s = ""
    for a, b in edges_hidden:
        s += line(P[a], P[b], style="grey,dashed")
    for a, b in edges_front:
        s += sres(P[a], P[b])
    for k, p in P.items():
        s += dot(*p)
    lab = {"A": (0.15, -0.4), "B": (0.3, -0.35), "B1": (0.3, -0.3), "A1": (-0.4, 0.3), "D": (0.35, -0.3), "C": (0.35, -0.3), "C1": (-0.15, 0.42), "D1": (-0.1, 0.42)}
    names = {"A": "$A$", "B": "$B$", "B1": "$B_1$", "A1": "$A_1$", "D": "$D$", "C": "$C$", "C1": "$C_1$", "D1": "$D_1$"}
    for k, (ddx, ddy) in lab.items():
        s += txt(P[k][0] + ddx, P[k][1] + ddy, names[k], style="font=\\normalsize")
    s += term(-1.0, -0.7) + line((-1.0, -0.7), P["A"]) + term(P["C1"][0] + 1.0, P["C1"][1] + 0.7) + line(P["C1"], (P["C1"][0] + 1.0, P["C1"][1] + 0.7))
    s += txt(-1.0, -1.15, "$I$", style="text=cur") + txt(P["C1"][0] + 1.0, P["C1"][1] + 1.15, "$I$", style="text=cur")
    s += txt(2.6, -1.5, "каждое ребро $r=12$~Ом, пунктир — невидимые рёбра")
    return s


@fig("connection-task-o44a-layers")
def _():
    s = ""
    xs = [0, 3.4, 6.8, 10.2]
    y3 = [1.9, 0, -1.9]
    A, C1 = (xs[0], 0), (xs[3], 0)
    L1 = {"B": (xs[1], y3[0]), "D": (xs[1], y3[1]), "A1": (xs[1], y3[2])}
    L2 = {"C": (xs[2], y3[0]), "B1": (xs[2], y3[1]), "D1": (xs[2], y3[2])}
    for p in L1.values():
        s += line(A, p)
    links = [("B", "C"), ("B", "B1"), ("D", "C"), ("D", "D1"), ("A1", "B1"), ("A1", "D1")]
    for a, b in links:
        s += line(L1[a], L2[b])
    for p in L2.values():
        s += line(p, C1)
    for p in [A, C1] + list(L1.values()) + list(L2.values()):
        s += dot(*p)
    names = {"B": "$B$", "D": "$D$", "A1": "$A_1$", "C": "$C$", "B1": "$B_1$", "D1": "$D_1$"}
    for k, p in {**L1, **L2}.items():
        s += txt(p[0], p[1] + 0.35, names[k], style="font=\\small")
    s += txt(0, 0.4, "$A$") + txt(xs[3], 0.4, "$C_1$")
    s += txt(5.1, -3.95, "каждая линия — ребро с сопротивлением $r$", style="text=grey")
    s += txt(1.7, -3.05, "$3$ ребра: $\\dfrac{r}{3}$", style="text=el") + txt(5.1, -3.05, "$6$ рёбер: $\\dfrac{r}{6}$", style="text=el") + txt(8.5, -3.05, "$3$ ребра: $\\dfrac{r}{3}$", style="text=el")
    s += txt(1.7, 2.6, "ток $\\dfrac{I}{3}$ в каждом", style="text=cur") + txt(5.1, 2.6, "ток $\\dfrac{I}{6}$ в каждом", style="text=cur") + txt(8.5, 2.6, "ток $\\dfrac{I}{3}$ в каждом", style="text=cur")
    return s


def build(name, body):
    cd.build(name, body)


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        build(n, FIGS[n]())
