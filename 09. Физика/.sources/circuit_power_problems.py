"""Schemes and graphs for the problems "Задачи на расчёт электрических цепей" in the note "Работа и мощность тока. Закон Джоуля–Ленца" (section f11, lessons 167-169).

Circuit schemes come from TikZ (macros of circuit_diagrams.py and ohm_circuits.py), the bar graph from matplotlib.
Run: nix shell nixpkgs#poppler-utils nixpkgs#python3Packages.matplotlib -c python3 circuit_power_problems.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefix joule-problem-)
"""
import sys

import circuit_diagrams as cd
import ohm_circuits  # noqa: F401  (adds the resistor macro and the voltage dimension line to the TikZ preamble)
import theme  # noqa: F401 — применяет общий шрифт и служебные цвета
from theme import ASH, BLUE, RED, num

cd.PREAMBLE += r"""
\usetikzlibrary{decorations.pathreplacing}
\tikzset{term/.style={fill=paper}}
"""

OUT = cd.OUT
TIKZ = {}
FIGS = {}


def tikz(name):
    def deco(fn):
        TIKZ[name] = fn
        return fn

    return deco


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


def terminals(x1, x2, y=0):
    return rf"\draw[term]({x1},{y})circle(.07)({x2},{y})circle(.07);"


def dim(x1, x2, y, label):
    return rf"\vdim{{{x1}}}{{{y}}}{{{x2}}}{{{label}}}\draw[dashed,grey]({x1},-.1)--({x1},{y})({x2},-.1)--({x2},{y});"


@tikz("joule-problem-12-22-23-wires")
def _():
    s = r"""
% 12.22: parallel, same voltage
\node[font=\bfseries]at(0,1.9){12.22: параллельно, общее $U$};
\draw(0,0)--(1,0)(1,.9)--(1,-.9)(5,.9)--(5,-.9)(5,0)--(6,0);
\dotc{1}{0}\dotc{5}{0}
\draw(1,.9)--(2.3,.9)(3.7,.9)--(5,.9)(1,-.9)--(2.3,-.9)(3.7,-.9)--(5,-.9);
\draw[cu,line width=2.4pt](2.3,.9)--(3.7,.9);\draw[alu,line width=2.4pt](2.3,-.9)--(3.7,-.9);
\node[cp,text=cu]at(3,1.3){медь, $\rho=0{,}017$};\node[cp,text=alu]at(3,-1.3){алюминий, $\rho=0{,}028$};
\draw[term](0,0)circle(.07)(6,0)circle(.07);
\vdim{1}{-2.1}{5}{$U$}\draw[dashed,grey](1,-.95)--(1,-2.1)(5,-.95)--(5,-2.1);
\node[cp,text=el]at(3,-2.8){$Q\propto U^2/R$: больше там, где $R$ меньше};
\node[cp,font=\footnotesize]at(3,-3.3){$\rho$ в Ом$\cdot$мм$^2$/м};
% 12.23: series, same current
\begin{scope}[shift={(9,0)}]
\node[font=\bfseries]at(3,1.9){12.23: последовательно, общий $I$};
\draw(0,0)--(1.3,0)(4.7,0)--(6,0);
\draw[stl,line width=2.4pt](1.3,0)--(3,0);\draw[alu,line width=2.4pt](3,0)--(4.7,0);
\node[cp,text=stl]at(2.15,.55){сталь, $\rho=0{,}10$};\node[cp,text=alu]at(3.85,-.55){алюминий, $\rho=0{,}028$};
\draw[term](0,0)circle(.07)(6,0)circle(.07);
\ca{.2}{1.2}{1.0}{1.2}\node[cur,font=\small]at(1.3,1.2){$I$};
\node[cp,text=el]at(3,-2.1){$Q\propto I^2R$: больше там, где $R$ больше};
\end{scope}
"""
    return s


@tikz("joule-problem-12-24-lamps")
def _():
    return r"""
\draw(0,0)--(1.3,0)(2.7,0)--(3.7,0)(5.1,0)--(6.4,0);
\lampc{2}{0}{0}\lampc{4.4}{0}{0}
\node[cp]at(2,.9){«220 В, 60 Вт»};\node[cp]at(4.4,.9){«220 В, 40 Вт»};
\node[cp]at(2,-.7){$R_1$};\node[cp]at(4.4,-.7){$R_2$};
\draw[term](0,0)circle(.07)(6.4,0)circle(.07);
\ca{.2}{.5}{.9}{.5}\node[cur,font=\small]at(.55,.8){$I$};
\vdim{0}{-1.7}{6.4}{$U=220$ В}\draw[dashed,grey](0,-.1)--(0,-1.7)(6.4,-.1)--(6.4,-1.7);
"""


@tikz("joule-problem-12-31-schemes")
def _():
    R = lambda x, y, n: rf"\resc{{{x}}}{{{y}}}{{0}}\node[cp]at({x},{y + 0.45}){{{n}}};"
    Rb = lambda x, y, n: rf"\resc{{{x}}}{{{y}}}{{0}}\node[cp]at({x},{y - 0.45}){{{n}}};"
    s = ""

    def panel(ox, oy, letter, body, w):
        return (
            rf"\begin{{scope}}[shift={{({ox},{oy})}}]"
            rf"\node[font=\bfseries\Large,anchor=east]at(-.2,1.5){{{letter})}};"
            + body
            + terminals(0, w)
            + dim(0, w, -2.3, "$U=30$ В")
            + r"\end{scope}"
        )

    # a: R1 parallel to R2+R3
    a = (
        r"\draw(0,0)--(.7,0)(.7,1)--(.7,-1)(5.3,1)--(5.3,-1)(5.3,0)--(6,0);\dotc{.7}{0}\dotc{5.3}{0}"
        r"\draw(.7,1)--(2.3,1)(3.7,1)--(5.3,1)(.7,-1)--(1.3,-1)(4.1,-1)--(5.3,-1);"
        + R(3, 1, "1")
        + Rb(2, -1, "2")
        + Rb(3.4, -1, "3")
    )
    s += panel(0, 0, "а", a, 6)
    # b: R1+R2+R3 series parallel to R4
    b = (
        r"\draw(0,0)--(.5,0)(.5,1)--(.5,-1)(6.0,1)--(6.0,-1)(6.0,0)--(6.5,0);\dotc{.5}{0}\dotc{6.0}{0}"
        r"\draw(.5,1)--(1.2,1)(5.4,1)--(6.0,1)(.5,-1)--(2.55,-1)(3.95,-1)--(6.0,-1);"
        + R(1.9, 1, "1")
        + R(3.3, 1, "2")
        + R(4.7, 1, "3")
        + Rb(3.25, -1, "4")
    )
    s += panel(8.5, 0, "б", b, 6.5)
    # c: R1 in series with R2 parallel R3
    c = (
        r"\draw(0,0)--(.7,0)(2.1,0)--(2.6,0)(2.6,1)--(2.6,-1)(5.4,1)--(5.4,-1)(5.4,0)--(6.1,0);\dotc{2.6}{0}\dotc{5.4}{0}"
        r"\draw(2.6,1)--(3.3,1)(4.7,1)--(5.4,1)(2.6,-1)--(3.3,-1)(4.7,-1)--(5.4,-1);"
        + R(1.4, 0, "1")
        + R(4, 1, "2")
        + Rb(4, -1, "3")
    )
    s += panel(0, -5.6, "в", c, 6.1)
    # d: R1+R2+R3 and R4+R5, two independent branches
    d = (
        r"\draw(0,0)--(.5,0)(.5,1)--(.5,-1)(6.0,1)--(6.0,-1)(6.0,0)--(6.5,0);\dotc{.5}{0}\dotc{6.0}{0}"
        r"\draw(.5,1)--(1.2,1)(5.4,1)--(6.0,1)(.5,-1)--(1.9,-1)(4.7,-1)--(6.0,-1);"
        + R(1.9, 1, "1")
        + R(3.3, 1, "2")
        + R(4.7, 1, "3")
        + Rb(2.6, -1, "4")
        + Rb(4.0, -1, "5")
    )
    s += panel(8.5, -5.6, "г", d, 6.5)
    return s


@tikz("joule-problem-12-42-heater")
def _():
    turns = "".join(rf"\draw[cu,line width=1.3pt](%.2f,0)..controls(%.2f,.6)and(%.2f,1.8)..(%.2f,2.4);" % (x, x + 0.05, x + 0.15, x + 0.2) for x in [1.6 + 0.35 * k for k in range(9)])
    return (
        # body and back end are filled without outline; the outline is the two sides, the back arc and the front end
        r"\fill[soft](1.2,0)rectangle(5.6,2.4);\fill[soft](5.6,1.2)ellipse(.35 and 1.2);"
        r"\draw(1.2,0)--(5.6,0)(1.2,2.4)--(5.6,2.4);\draw(5.6,0)arc(-90:90:.35 and 1.2);"
        r"\draw[fill=soft](1.2,1.2)ellipse(.35 and 1.2);"
        + turns
        + r"\draw[<->,el](.4,0)--(.4,2.4);\node[el,font=\small,fill=paper,inner sep=1pt]at(.4,1.2){$D$};"
        r"\draw[dashed,grey](.4,0)--(1.2,0)(.4,2.4)--(1.2,2.4);"
        r"\draw[<->,el](1.6,3.0)--(1.95,3.0);\node[el,font=\small]at(1.78,3.35){$d$};\draw[dashed,grey](1.6,2.45)--(1.6,3.0)(1.95,2.45)--(1.95,3.0);"
        r"\draw[decorate,decoration={brace,mirror,amplitude=5pt}](1.6,-.2)--(4.75,-.2);\node[cp]at(3.2,-.75){$N$ витков};"
        r"\draw(1.6,2.4)--(1.6,3.3)(4.75,2.4)--(4.75,3.3);\draw[term](1.6,3.6)circle(.07)(4.75,3.6)circle(.07);\draw(1.6,3.3)--(1.6,3.53)(4.75,3.3)--(4.75,3.53);"
        r"\node[cp,text=el]at(7.4,1.2){никелиновая\\проволока\\на фарфоровом\\цилиндре};"
    )


@fig("joule-problem-12-24-power-bars")
def _():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    blue, orange, grid = BLUE, RED, ASH
    f, ax = plt.subplots(figsize=(6.4, 4))
    w = 0.34
    ax.bar([-w / 2, 1 - w / 2], [60, 9.6], w, color=blue, label="лампа $60$ Вт")
    ax.bar([w / 2, 1 + w / 2], [40, 14.4], w, color=orange, label="лампа $40$ Вт")
    for x, v in ((-w / 2, 60), (w / 2, 40), (1 - w / 2, 9.6), (1 + w / 2, 14.4)):
        ax.text(x, v + 1.2, num(v, "") + " Вт", ha="center", fontsize=10.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["по отдельности\nпри $220$ В на каждой", "последовательно\nпри $220$ В на обеих"])
    ax.set_ylabel("мощность, Вт")
    ax.set_ylim(0, 72)
    ax.grid(True, axis="y", color=grid, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    f.tight_layout()
    f.savefig(OUT / "joule-problem-12-24-power-bars.png")
    plt.close(f)
    print("wrote joule-problem-12-24-power-bars")


if __name__ == "__main__":
    wanted = sys.argv[1:] or (list(TIKZ) + list(FIGS))
    for n in wanted:
        if n in FIGS:
            FIGS[n]()
        else:
            cd.build(n, TIKZ[n]())
