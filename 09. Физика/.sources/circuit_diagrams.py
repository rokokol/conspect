"""Circuit diagrams for the notes "Электрический ток. Электрическая цепь" and "Сила тока и напряжение" (section f11, lessons 143-150).

Symbols are hand-written TikZ macros that copy the lecture symbols (bell with a base line, cell with a long plus plate), so circuitikz is not needed.
Run: nix shell nixpkgs#poppler-utils -c python3 circuit_diagrams.py [name ...]
The system pdflatex needs the tikz package. PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes circuit-, voltage-)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from course import COURSE

OUT = (
    COURSE
    / "content"
    / "11. Электрические явления"
    / "00. Вложения"
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nomedia").touch()

from theme import BLUE, COPPER, GREEN, INK, LIGHT, METAL, PAPER, RED, SKY, WARM, tint

# The one place where the TikZ colour names of every circuit script are defined: each is a role of theme.py
TIKZ_COLOURS = {
    "cur": RED,  # current: arrows and the thing the figure is about
    "el": BLUE,  # voltage: dimension lines and labels
    "ok": GREEN,
    "bad": RED,
    "soft": LIGHT,  # the pale body fill of a part
    "ink": INK,  # every line and every label
    "paper": PAPER,  # the white fill that hides what lies behind a part
    "grey": tint(INK, 0.4),  # guides and small notes
    "wire": COPPER,
    "cu": COPPER,  # copper conductor
    "alu": METAL,  # aluminium conductor
    "stl": tint(INK, 0.2),  # steel conductor
    "water": tint(SKY, 0.4),  # filled with water!60
    "glow": WARM,  # a heated, glowing body
    "soln": tint(SKY, 0.75),  # an electrolyte solution
}
COLOUR_DEFS ="".join(rf"\definecolor{{{name}}}{{HTML}}{{{role[1:].upper()}}}" + "\n" for name, role in TIKZ_COLOURS.items())

PREAMBLE = (
    r"""
\documentclass[border=6pt]{standalone}
\usepackage[T2A]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[russian]{babel}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc}
"""
    + COLOUR_DEFS
    + r"""\hyphenpenalty=10000\exhyphenpenalty=10000
\tikzset{every picture/.style={line width=0.9pt,line cap=round,line join=round,color=ink}}
\tikzset{lbl/.style={font=\small,align=left,text width=4.6cm,anchor=west}}
\tikzset{cp/.style={font=\small,align=center}}

% lamp: x y angle
\newcommand{\lampc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.35,0)(.35,0)--(.7,0)(0,0)circle(.35)(-.25,-.25)--(.25,.25)(-.25,.25)--(.25,-.25);
\end{scope}}
% meter: x y angle label
\newcommand{\meterc}[4]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.4,0)(.4,0)--(.7,0)(0,0)circle(.4);\node[font=\small] at(0,0){#4};
\end{scope}}
% bell: x y angle
\newcommand{\bellc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(.7,0)(-.4,0)arc(180:0:.4);
\end{scope}}
% generator or motor: x y angle letter
\newcommand{\genc}[4]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.4,0)(.4,0)--(.7,0)(0,0)circle(.4);\node at(0,0){#4};
\end{scope}}
% open key
\newcommand{\keyc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.35,0)(.35,0)--(.7,0)(-.35,0)--(.28,.4);\fill(-.35,0)circle(.045)(.35,0)circle(.045);
\end{scope}}
% closed key
\newcommand{\keyk}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(.7,0);\fill(-.35,0)circle(.045)(.35,0)circle(.045);\draw(-.35,0)--(.35,.09);
\end{scope}}
% old key with arrow
\newcommand{\keyold}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.35,0)(.35,0)--(.7,0);\draw[-{Stealth[length=2mm]}](-.35,0)--(.3,.34);\fill(-.35,0)circle(.045)(.35,0)circle(.045);
\end{scope}}
% push button, normally open
\newcommand{\btnc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.3,0)(.3,0)--(.7,0);\fill(-.3,0)circle(.045)(.3,0)circle(.045);
\draw(-.34,.2)--(.34,.2)(0,.2)--(0,.5)(-.17,.5)--(.17,.5);
\end{scope}}
% push button, normally closed
\newcommand{\btnn}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.3,0)--(-.3,.2)(.7,0)--(.3,0)--(.3,.2);
\draw(-.34,.2)--(.34,.2)(0,.2)--(0,.5)(-.17,.5)--(.17,.5);
\end{scope}}
% old push button
\newcommand{\btnold}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.3,0)(.3,0)--(.7,0);\fill(-.3,0)circle(.045)(.3,0)circle(.045);
\draw(-.12,.16)rectangle(.12,.32);\draw(-.3,.16)--(.3,.16);
\end{scope}}
% changeover switch, state u or d
\newcommand{\chgc}[4]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.4,0)(.4,.5)--(.7,.5)(.4,-.5)--(.7,-.5);
\fill(-.4,0)circle(.045)(.4,.5)circle(.045)(.4,-.5)circle(.045);
\ifx#4u\draw(-.4,0)--(.4,.5);\else\draw(-.4,0)--(.4,-.5);\fi
\end{scope}}
% old changeover switch with arrow
\newcommand{\chgold}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.4,0)(.4,.5)--(.7,.5)(.4,-.5)--(.7,-.5);
\fill(-.4,0)circle(.045)(.4,.5)circle(.045)(.4,-.5)circle(.045);
\draw[-{Stealth[length=2mm]}](-.4,0)--(.36,.46);
\end{scope}}
% cells: x y angle n ; plus is the long plate on the local -x side
\newcommand{\cellc}[4]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\pgfmathsetmacro{\cellhw}{0.15*(2*#4-1)/2}
\draw(-.9,0)--(-\cellhw,0)(\cellhw,0)--(.9,0);
\foreach\k in{0,...,\numexpr2*#4-1\relax}{\pgfmathsetmacro{\px}{-\cellhw+0.15*\k}
\ifodd\k\draw[line width=2.2pt](\px,-.14)--(\px,.14);\else\draw(\px,-.3)--(\px,.3);\fi}
\end{scope}}
% battery of many cells with dots
\newcommand{\celld}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-1.1,0)--(-.6,0)(.6,0)--(1.1,0);
\draw(-.6,-.3)--(-.6,.3)(.45,-.3)--(.45,.3);\draw[line width=2.2pt](-.45,-.14)--(-.45,.14)(.6,-.14)--(.6,.14);
\fill(-.2,0)circle(.025)(0,0)circle(.025)(.2,0)circle(.025);
\end{scope}}
% current source box: x y angle
\newcommand{\itbox}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.7,0)--(-.5,0)(.5,0)--(.7,0)(-.5,-.3)rectangle(.5,.3);\node[font=\small]at(0,0){ИТ};
\end{scope}}
% junction dot
\newcommand{\dotc}[2]{\fill(#1,#2)circle(.06);}
% current arrow from point to point
\newcommand{\ca}[4]{\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](#1,#2)--(#3,#4);}
\newcommand{\ea}[4]{\draw[el,-{Stealth[length=2.6mm]},line width=1.1pt](#1,#2)--(#3,#4);}
\newcommand{\sgn}[3]{\node[font=\small]at(#1,#2){#3};}
"""
)

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


def row(x, y, sym, label, dx=1.5):
    return f"{sym}\n\\node[lbl] at({x + dx},{y}){{{label}}};\n"


@fig("circuit-symbols-sources-wires")
def _():
    s = r"\node[font=\bfseries\large,anchor=west] at(0,1.0){Источники тока};\node[font=\bfseries\large,anchor=west] at(10.2,1.0){Проводники и соединения};"
    L = 0.9
    s += row(L, 0, r"\cellc{0.9}{0}{0}{1}\sgn{0.2}{.55}{$+$}\sgn{1.6}{.55}{$-$}", "гальванический элемент или аккумулятор")
    s += row(L, -1.5, r"\cellc{0.9}{-1.5}{0}{3}", "батарея из трёх элементов")
    s += row(L, -3.0, r"\celld{1.1}{-3}{0}", "батарея из многих элементов", 1.7)
    s += row(L, -4.5, r"\genc{0.9}{-4.5}{0}{Г}", "генератор")
    s += row(L, -6.0, r"\itbox{0.9}{-6}{0}", "источник тока неуточнённого вида")
    R = 11.0
    s += row(R, 0, rf"\draw({R - 0.7},0)--({R + 0.7},0);", "проводник")
    s += row(R, -1.5, rf"\draw({R - 0.7},-1.8)--({R + 0.1},-1.8)--({R + 0.1},-1.2);", "изгиб под прямым углом, без точки")
    s += row(R, -3.0, rf"\draw({R - 0.6},-3)--({R + 0.6},-3)({R},-3.6)--({R},-2.4);", "пересечение без соединения")
    s += row(R, -4.5, rf"\draw({R - 0.6},-4.5)--({R - 0.14},-4.5)arc(180:0:.14)({R + 0.14},-4.5)--({R + 0.6},-4.5)({R},-5.1)--({R},-3.9);", "то же, старое обозначение")
    s += row(R, -6.0, rf"\draw({R - 0.6},-6)--({R + 0.6},-6)({R},-6.6)--({R},-5.4);\dotc{{{R}}}{{-6}}", "соединение проводников: точка припоя")
    return s


@fig("circuit-symbols-consumers-switches")
def _():
    s = ""
    cols = [0.0, 7.4, 14.8]
    titles = ["Потребители", "Ключи и переключатели", "Кнопки, клеммы и гнёзда"]
    for c, t in zip(cols, titles):
        s += rf"\node[font=\bfseries\large,anchor=west] at({c},1.0){{{t}}};"
    # column 1
    x = cols[0] + 0.9
    s += row(x, 0, rf"\lampc{{{x}}}{{0}}{{0}}", "лампа накаливания", 1.3)
    s += row(x, -1.5, rf"\bellc{{{x}}}{{-1.5}}{{0}}", "электрический звонок", 1.3)
    s += row(x, -3.0, rf"\genc{{{x}}}{{-3}}{{0}}{{М}}", "электродвигатель: тот же кружок, что у генератора, но с буквой М", 1.3)
    # column 2
    x = cols[1] + 0.9
    s += row(x, 0, rf"\keyc{{{x}}}{{0}}{{0}}", "ключ", 1.3)
    s += row(x, -1.5, rf"\keyold{{{x}}}{{-1.5}}{{0}}", "ключ, старое обозначение", 1.3)
    # a changeover switch is 1.0 high, so the rows are 1.8 and 2.0 apart: two symbols never share a gap
    s += row(x, -3.3, rf"\chgc{{{x}}}{{-3.3}}{{0}}{{u}}", "переключатель", 1.3)
    s += row(x, -5.3, rf"\chgold{{{x}}}{{-5.3}}{{0}}", "переключатель, старое обозначение", 1.3)
    # column 3
    x = cols[2] + 0.9
    s += row(x, 0, rf"\btnc{{{x}}}{{0}}{{0}}", "кнопка", 1.3)
    s += row(x, -1.5, rf"\btnold{{{x}}}{{-1.5}}{{0}}", "кнопка, старое обозначение", 1.3)
    s += row(x, -3.0, rf"\draw({x - 0.7},-3)--({x - 0.1},-3)({x},-3)circle(.09)({x - 0.1},-3.1)--({x + 0.1},-2.9);", "клемма", 1.3)
    s += row(x, -4.5, rf"\draw({x - 0.7},-4.5)circle(.12)({x - 0.58},-4.5)--({x + 0.7},-4.5);", "гнездо, старое обозначение", 1.3)
    s += row(x, -6.0, rf"\draw({x - 0.8},-5.84)--({x - 0.55},-6)--({x - 0.8},-6.16)({x - 0.6},-5.84)--({x - 0.35},-6)--({x - 0.6},-6.16)({x - 0.35},-6)--({x + 0.7},-6);", "гнездо, современное обозначение", 1.3)
    return s


@fig("circuit-lamp-key-battery")
def _():
    return r"""
\draw(0,0)--(2.1,0)(3.9,0)--(6,0)--(6,3)--(5.1,3)(3.7,3)--(2.6,3)(1.2,3)--(0,3)--(0,0);
\cellc{3}{0}{0}{3}\lampc{1.9}{3}{0}\keyk{4.4}{3}{0}
\sgn{1.95}{.42}{$+$}\sgn{4.05}{.42}{$-$}
\ca{-.35}{1.1}{-.35}{1.9}\ca{2.95}{3.5}{3.55}{3.5}\ca{6.35}{1.9}{6.35}{1.1}\ca{5.2}{-.35}{4.5}{-.35}\ca{1.6}{-.35}{.8}{-.35}
\node[cp]at(1.9,3.85){лампа};\node[cp]at(4.4,3.85){ключ};\node[cp]at(3,-.85){батарея из трёх элементов};
"""


@fig("circuit-task-4-14")
def _():
    return r"""
\draw(0,0)--(1.3,0)(2.7,0)--(3.95,0)(5.35,0)--(7,0)--(7,3.4)--(5.9,3.4)(4.1,3.4)--(3.3,3.4)(1.9,3.4)--(0,3.4)--(0,0);
\lampc{2}{0}{0}\bellc{4.65}{0}{0}\keyk{2.6}{3.4}{0}\cellc{5}{3.4}{180}{3}
\sgn{6.3}{3.8}{$+$}\sgn{3.75}{3.8}{$-$}
\ca{7.35}{1.8}{7.35}{1.0}\ca{4.3}{-.4}{3.6}{-.4}\ca{-.35}{1.0}{-.35}{1.8}\ca{1.7}{3.85}{2.4}{3.85}
\node[cp]at(2,-.9){лампа};\node[cp]at(4.65,-.9){звонок};\node[cp]at(2.6,4.25){ключ};
"""


@fig("circuit-task-4-16")
def _():
    return r"""
\draw(0,0)--(1.9,0)(3.3,0)--(5,0)--(5,1.15)(5,2.55)--(5,3.4)--(3.1,3.4)(1.3,3.4)--(0,3.4)--(0,0);
\cellc{2.2}{3.4}{0}{1}\bellc{2.6}{0}{0}\lampc{5}{1.85}{90}
\sgn{1.0}{3.8}{$+$}\sgn{3.45}{3.8}{$-$}
\ca{-.35}{2.6}{-.35}{1.6}\ca{1.6}{-.4}{2.3}{-.4}\ca{5.4}{.8}{5.4}{1.4}\ca{4.4}{3.8}{3.7}{3.8}
\node[cp]at(2.6,-.9){звонок};\node[cp,anchor=west]at(5.55,1.85){лампа};
"""


@fig("circuit-task-4-17")
def _():
    return r"""
\draw(0,0)--(1.9,0)(3.3,0)--(6,0)--(6,3.4)--(3.1,3.4)(1.3,3.4)--(0,3.4)--(0,0);
\draw(0,1.7)--(2.2,1.7)(3.6,1.7)--(6,1.7);
\cellc{2.2}{3.4}{0}{1}\lampc{2.9}{1.7}{0}\bellc{2.6}{0}{0}
\dotc{0}{1.7}\dotc{6}{1.7}
\sgn{1.0}{3.8}{$+$}\sgn{3.45}{3.8}{$-$}
\ca{-.35}{2.8}{-.35}{2.1}\ca{-.35}{1.2}{-.35}{.5}
\ca{.6}{1.35}{1.2}{1.35}\ca{4.8}{1.35}{5.4}{1.35}
\ca{1.6}{-.4}{2.3}{-.4}\ca{6.35}{.5}{6.35}{1.1}\ca{6.35}{2.1}{6.35}{2.9}\ca{4.6}{3.8}{3.9}{3.8}
\node[cp,anchor=east]at(-.6,1.7){узел};\node[cp,anchor=west]at(6.6,1.7){узел};
\node[cp]at(2.9,2.4){лампа};\node[cp]at(2.6,-.9){звонок};
"""


def two_buttons_base(inner, labelbox, label):
    return (
        r"""
\draw(0,0)--(0,3)--(1.4,3)(3.2,3)--(4.9,3)(6.3,3)--(7.5,3)--(7.5,0)--(0,0);
\cellc{2.3}{3}{0}{1}\lampc{5.6}{3}{0}
\sgn{1.1}{3.4}{$+$}\sgn{3.5}{3.4}{$-$}
"""
        + inner
        + labelbox
        + rf"\node[cp,text=el]at(3.75,-.95){{{label}}};"
    )


@fig("circuit-and-two-buttons")
def _():
    inner = r"""
\draw(0,0)--(1.45,0)(2.85,0)--(4.05,0)(5.45,0)--(7.5,0);
\btnc{2.15}{0}{0}\btnc{4.75}{0}{0}
"""
    box = r"\draw[el,dashed,rounded corners=6pt](1.0,-.45)rectangle(5.9,.85);"
    body = two_buttons_base(inner, box, "схема «И»: лампа горит, если нажаты обе кнопки")
    return body.replace(r"--(7.5,0)--(0,0);", r"--(7.5,0);", 1)


@fig("circuit-or-two-buttons")
def _():
    body = r"""
\draw(0,0)--(0,3)--(1.4,3)(3.2,3)--(4.9,3)(6.3,3)--(7.5,3)--(7.5,0)--(5.7,0)(1.8,0)--(0,0);
\cellc{2.3}{3}{0}{1}\lampc{5.6}{3}{0}
\sgn{1.1}{3.4}{$+$}\sgn{3.5}{3.4}{$-$}
\draw(1.8,0)--(1.8,-1.4)--(2.65,-1.4)(4.05,-1.4)--(5.7,-1.4)--(5.7,0)(1.8,0)--(2.65,0)(4.05,0)--(5.7,0);
\btnc{3.35}{0}{0}\btnc{3.35}{-1.4}{0}
\dotc{1.8}{0}\dotc{5.7}{0}
\draw[el,dashed,rounded corners=6pt](1.4,-2.15)rectangle(6.1,.85);
\node[cp,text=el]at(3.75,-2.6){схема «ИЛИ»: лампа горит, если нажата любая кнопка};
"""
    return body


@fig("circuit-not-button")
def _():
    return r"""
\draw(0,0)--(0,3)--(1.4,3)(3.2,3)--(4.9,3)(6.3,3)--(7.5,3)--(7.5,0)--(4.05,0)(2.65,0)--(0,0);
\cellc{2.3}{3}{0}{1}\lampc{5.6}{3}{0}\btnn{3.35}{0}{0}
\sgn{1.1}{3.4}{$+$}\sgn{3.5}{3.4}{$-$}
\draw[el,dashed,rounded corners=6pt](2.25,-.45)rectangle(4.45,.85);
\node[cp,text=el]at(3.75,-.95){схема «НЕ»: лампа горит, пока кнопка не нажата};
"""


@fig("circuit-two-lamps-two-keys")
def _():
    return r"""
% the source stands in the middle, both branches "key + lamp" hang on the same two wires: they are parallel
\draw(0,0)--(6,0)(0,0)--(0,.5)(0,1.9)--(0,2.2)(0,3.6)--(0,4)--(6,4)--(6,3.6)(6,2.2)--(6,1.9)(6,.5)--(6,0)(3,4)--(3,2.9)(3,1.1)--(3,0);
\cellc{3}{2}{-90}{3}\dotc{3}{4}\dotc{3}{0}
\keyk{0}{2.9}{90}\lampc{0}{1.2}{90}\keyk{6}{2.9}{90}\lampc{6}{1.2}{90}
\sgn{3.4}{2.7}{$+$}\sgn{3.4}{1.3}{$-$}
\node[cp,anchor=west]at(.55,2.9){ключ 1};\node[cp,anchor=west]at(.55,1.2){лампа 1};
\node[cp,anchor=east]at(5.45,2.9){ключ 2};\node[cp,anchor=east]at(5.45,1.2){лампа 2};
"""


@fig("circuit-short-circuit")
def _():
    return r"""
\draw(0,0)--(0,3)--(1.4,3)(3.2,3)--(3.8,3)--(3.8,0)--(0,0);
\cellc{2.3}{3}{0}{1}\keyk{3.8}{1.5}{90}
\sgn{1.1}{3.4}{$+$}\sgn{3.5}{3.4}{$-$}
\ca{-.35}{2.4}{-.35}{.6}\ca{.6}{-.35}{3.2}{-.35}\ca{4.15}{.6}{4.15}{2.4}
\node[cp,text=bad,text width=4cm]at(6.6,1.5){потребителей нет: полюса соединены проводником, это короткое замыкание};
"""


@fig("circuit-two-lamps-three-keys")
def _():
    return r"""
\draw(0,0)--(0,3.4)--(.9,3.4)(2.3,3.4)--(3.2,3.4)--(6.6,3.4)--(6.6,3.0)(6.6,1.6)--(6.6,1.2)(6.6,-.2)--(6.6,-.6)--(4.2,-.6)--(3.3,-.6)(1.5,-.6)--(0,-.6)--(0,0);
\draw(4.2,3.4)--(4.2,3.0)(4.2,1.6)--(4.2,1.2)(4.2,-.2)--(4.2,-.6);
\keyk{1.6}{3.4}{0}\keyk{4.2}{2.3}{90}\lampc{4.2}{.5}{90}\keyk{6.6}{2.3}{90}\lampc{6.6}{.5}{90}
\cellc{2.4}{-.6}{0}{3}
\dotc{4.2}{3.4}\dotc{4.2}{-.6}
\sgn{1.1}{-.2}{$+$}\sgn{3.7}{-.2}{$-$}
\node[cp]at(1.6,3.85){главный ключ};\node[cp,anchor=east]at(3.75,2.3){ключ 1};\node[cp,anchor=east]at(3.75,.5){лампа 1};
\node[cp,anchor=west]at(7.15,2.3){ключ 2};\node[cp,anchor=west]at(7.15,.5){лампа 2};
"""


@fig("circuit-bell-two-buttons")
def _():
    return r"""
\draw(0,0)--(0,3)--(1.4,3)(3.2,3)--(4.9,3)(6.3,3)--(7.5,3)--(7.5,0)--(5.7,0)(1.8,0)--(0,0);
\cellc{2.3}{3}{0}{2}\bellc{5.6}{3}{0}
\sgn{1.0}{3.4}{$+$}\sgn{3.6}{3.4}{$-$}
\draw(1.8,0)--(1.8,-1.4)--(2.65,-1.4)(4.05,-1.4)--(5.7,-1.4)--(5.7,0)(1.8,0)--(2.65,0)(4.05,0)--(5.7,0);
\btnc{3.35}{0}{0}\btnc{3.35}{-1.4}{0}
\dotc{1.8}{0}\dotc{5.7}{0}
\node[cp]at(3.35,-.65){кнопка у входа};\node[cp]at(3.35,-2.05){кнопка в парадной};
"""


@fig("circuit-changeover-two-lamps")
def _():
    return r"""
\draw(6.0,2.3)--(6.4,2.3)--(6.4,-.3)--(-.5,-.3)--(-.5,1.8)--(.1,1.8)(6.0,1.3)--(6.4,1.3);
\draw(1.9,1.8)--(2.5,1.8)(3.9,2.3)--(4.6,2.3)(3.9,1.3)--(4.6,1.3);
\cellc{1.0}{1.8}{180}{3}
\chgc{3.2}{1.8}{0}{u}\lampc{5.3}{2.3}{0}\lampc{5.3}{1.3}{0}\dotc{6.4}{1.3}
\sgn{1.7}{2.2}{$+$}\sgn{.3}{2.2}{$-$}
\node[cp]at(3.2,3.1){переключатель};\node[cp,anchor=west]at(6.9,2.3){лампа 1};\node[cp,anchor=west]at(6.9,1.3){лампа 2};
\node[cp,text=el]at(3.2,-.9){в показанном положении горит лампа 1};
"""


@fig("circuit-staircase-switch")
def _():
    def panel(dy, state2, arrows):
        b = f"\\begin{{scope}}[shift={{(0,{dy})}}]\n"
        b += "\\chgc{-3.9}{0}{180}{d}\\chgc{3.9}{0}{0}{" + state2 + "}\n"
        b += "\\draw(-3.2,0)--(-2.7,0)(-.9,0)--(1.3,0)(2.7,0)--(3.2,0);\n"
        b += "\\cellc{-1.8}{0}{0}{3}\\lampc{2.0}{0}{0}\n"
        b += "\\draw(-4.6,.5)--(-5.1,.5)--(-5.1,2.0)--(5.1,2.0)--(5.1,.5)--(4.6,.5);\n"
        b += "\\draw(-4.6,-.5)--(-5.1,-.5)--(-5.1,-2.0)--(5.1,-2.0)--(5.1,-.5)--(4.6,-.5);\n"
        b += "\\sgn{-2.5}{.5}{$+$}\\sgn{-1.1}{.5}{$-$}\n"
        b += arrows
        b += "\\end{scope}\n"
        return b

    on = "\\ca{-.6}{2.4}{.6}{2.4}\\ca{.7}{-.4}{-.1}{-.4}\\node[cp,text=ok]at(0,-2.8){лампа горит: переключатели в одном положении};\n"
    off = "\\node[cp,text=bad]at(0,-2.8){лампа не горит: второй переключатель переброшен, цепь разомкнута};\n"
    return panel(0, "u", on) + panel(-6.6, "d", off)


@fig("circuit-drawing-rules")
def _():
    s = r"""
\node[font=\bfseries\large,text=ok]at(2.8,5.6){верно};\node[font=\bfseries\large,text=bad]at(11.4,5.6){неверно};
% row 1: bend
\draw(0,4.3)--(2.2,4.3)--(2.2,3.5);\node[cp,anchor=west,text width=3.4cm]at(2.7,3.9){изгиб без точки};
\draw(8.6,4.3)--(10.8,4.3)--(10.8,3.5);\dotc{10.8}{4.3};\node[cp,anchor=west,text width=3.4cm]at(11.3,3.9){точка на изгибе};
% row 2: lamp leads
\draw(0,2.0)--(.7,2.0)(2.1,2.0)--(2.8,2.0);\lampc{1.4}{2.0}{0};
\node[cp,anchor=west,text width=3.4cm]at(3.3,2.0){выводы по разные стороны потребителя};
\draw(8.6,2.0)--(9.3,2.0)(10.7,2.0)--(11.1,2.0)--(11.1,2.9)--(8.6,2.9);\lampc{10.0}{2.0}{0};
\node[cp,anchor=west,text width=3.4cm]at(11.6,2.0){оба вывода с одной стороны};
% row 3: short circuit
\draw(0,-.6)--(.5,-.6)(2.3,-.6)--(2.8,-.6)--(2.8,-1.9)--(2.1,-1.9)(.7,-1.9)--(0,-1.9)--(0,-.6);
\cellc{1.4}{-.6}{0}{1}\lampc{1.4}{-1.9}{0};
\node[cp,anchor=west,text width=3.4cm]at(3.3,-1.2){полюса источника связаны через потребитель};
\draw(8.6,-.6)--(9.1,-.6)(10.9,-.6)--(11.4,-.6)--(11.4,-1.9)--(8.6,-1.9)--(8.6,-.6);
\cellc{10.0}{-.6}{0}{1};
\node[cp,anchor=west,text width=3.4cm]at(11.9,-1.2){полюса соединены проводником: короткое замыкание};
"""
    return s


PANEL5 = {
    # kind, meter -> body of one 3.3 x 2.4 panel at origin
}


def variant(kind, meter, ox, oy, label, verdict, why):
    """One panel of the textbook figure: battery on top, lamp at the bottom, meter placed by kind."""
    W, H = 3.6, 2.6
    b = f"\\begin{{scope}}[shift={{({ox},{oy})}}]\n"
    # outer loop pieces
    b += f"\\cellc{{{W / 2}}}{{{H}}}{{0}}{{1}}\n"
    b += f"\\draw(0,{H})--({W / 2 - 0.9},{H})({W / 2 + 0.9},{H})--({W},{H});\n"
    if kind in ("left", "bridge", "right"):
        # left edge, right edge full wires
        pass
    lamp_x = 2.15 if kind == "left" else (1.45 if kind == "right" else W / 2)
    b += f"\\lampc{{{lamp_x}}}{{0}}{{0}}\n"
    if kind == "series":
        b += f"\\draw(0,{H})--(0,0)--({lamp_x - 0.7},0)({lamp_x + 0.7},0)--({W},0)--({W},0.9)({W},{H - 0.9})--({W},{H});\n"
        b += f"\\meterc{{{W}}}{{{H / 2}}}{{90}}{{{meter}}}\n"
    elif kind == "left":
        b += f"\\draw(0,{H})--(0,0)--({lamp_x - 0.7},0)({lamp_x + 0.7},0)--({W},0)--({W},{H});\n"
        b += f"\\draw(0.75,{H})--(0.75,{H / 2 + 0.7})(0.75,{H / 2 - 0.7})--(0.75,0);\\meterc{{0.75}}{{{H / 2}}}{{90}}{{{meter}}}\\dotc{{0.75}}{{{H}}}\\dotc{{0.75}}{{0}}\n"
    elif kind == "right":
        b += f"\\draw(0,{H})--(0,0)--({lamp_x - 0.7},0)({lamp_x + 0.7},0)--({W},0)--({W},{H});\n"
        b += f"\\draw({W - 0.75},{H})--({W - 0.75},{H / 2 + 0.7})({W - 0.75},{H / 2 - 0.7})--({W - 0.75},0);\\meterc{{{W - 0.75}}}{{{H / 2}}}{{90}}{{{meter}}}\\dotc{{{W - 0.75}}}{{{H}}}\\dotc{{{W - 0.75}}}{{0}}\n"
    elif kind == "bridge":
        y = 1.35
        b += f"\\draw(0,{H})--(0,0)--({lamp_x - 0.7},0)({lamp_x + 0.7},0)--({W},0)--({W},{H});\n"
        b += f"\\draw(0,{y})--({W / 2 - 0.7},{y})({W / 2 + 0.7},{y})--({W},{y});\\meterc{{{W / 2}}}{{{y}}}{{0}}{{{meter}}}\\dotc{{0}}{{{y}}}\\dotc{{{W}}}{{{y}}}\n"
    col = "ok" if verdict else "bad"
    txt = "верно" if verdict else "неверно"
    b += f"\\node[cp,text={col}]at({W / 2},-.95){{{label}) {txt}}};\n"
    b += f"\\node[cp,text width=3.4cm,font=\\footnotesize]at({W / 2},-1.7){{{why}}};\n"
    b += "\\end{scope}\n"
    return b


@fig("circuit-task-5-9-ammeter")
def _():
    s = ""
    specs = [
        ("left", "а", False, "амперметр параллельно куску провода: показывает $0$"),
        ("bridge", "б", False, "амперметр соединяет полюса источника: короткое замыкание"),
        ("series", "в", True, "амперметр в разрыве цепи, через него идёт ток лампы"),
        ("right", "г", False, "амперметр параллельно куску провода: показывает $0$"),
    ]
    for i, (k, lab, v, why) in enumerate(specs):
        s += variant(k, "A", i * 5.0, 0, lab, v, why)
    return s


@fig("circuit-task-5-10-voltmeter")
def _():
    s = ""
    specs = [
        ("left", "а", False, "вольтметр параллельно куску провода: показывает $0$"),
        ("right", "б", False, "вольтметр параллельно куску провода: показывает $0$"),
        ("bridge", "в", True, "выводы вольтметра на концах лампы"),
        ("series", "г", False, "вольтметр в разрыве цепи: ток почти не идёт, лампа не горит"),
    ]
    for i, (k, lab, v, why) in enumerate(specs):
        s += variant(k, "V", i * 5.0, 0, lab, v, why)
    return s


@fig("circuit-ammeter-in-series")
def _():
    return r"""
\draw(0,0)--(0,.7)(0,2.5)--(0,3.5)--(1.9,3.5)(3.3,3.5)--(5.5,3.5)--(5.5,0)--(4.3,0)(2.9,0)--(0,0);
\cellc{0}{1.6}{-90}{3}\lampc{2.6}{3.5}{0}\meterc{3.6}{0}{0}{A}
\sgn{-.4}{2.35}{$+$}\sgn{-.4}{.85}{$-$}\sgn{4.15}{.4}{$+$}\sgn{3.05}{.4}{$-$}
\ca{.6}{3.9}{1.2}{3.9}\ca{5.9}{2.2}{5.9}{1.4}\ca{4.9}{-.4}{4.3}{-.4}\ca{-.4}{2.9}{-.4}{3.4}
\node[cp]at(2.6,4.35){лампа};\node[cp]at(3.6,-.95){амперметр в разрыве цепи};
"""


@fig("circuit-two-ammeters-series")
def _():
    return r"""
\draw(0,0)--(0,.7)(0,2.5)--(0,3.5)--(1.6,3.5)(3.0,3.5)--(3.9,3.5)(5.1,3.5)--(6.5,3.5)--(6.5,0)--(5.1,0)(3.7,0)--(0,0);
\cellc{0}{1.6}{-90}{3}\lampc{2.3}{3.5}{0}\meterc{4.5}{3.5}{0}{A}\meterc{4.4}{0}{0}{mA}
\sgn{-.4}{2.35}{$+$}\sgn{-.4}{.85}{$-$}
\ca{.6}{3.9}{1.2}{3.9}\ca{2.5}{3.9}{3.2}{3.9}\ca{6.9}{2.2}{6.9}{1.4}\ca{5.3}{-.4}{4.6}{-.4}\ca{-.4}{2.9}{-.4}{3.4}
\node[cp]at(4.5,4.35){$I$};\node[cp]at(4.4,-.9){$I$};
"""


@fig("circuit-meters-symbols")
def _():
    s = ""
    items = [("A", "амперметр", 0), ("mA", "миллиамперметр", 1), (r"$\mu$A", "микроамперметр", 2), ("kA", "килоамперметр", 3)]
    itemsv = [("V", "вольтметр", 0), ("mV", "милливольтметр", 1), (r"$\mu$V", "микровольтметр", 2), ("kV", "киловольтметр", 3)]
    for sym, name, i in items:
        y = -1.3 * i
        s += f"\\meterc{{0.9}}{{{y}}}{{0}}{{{sym}}}\\node[lbl,text width=3.6cm] at(2.3,{y}){{{name}}};\n"
    for sym, name, i in itemsv:
        y = -1.3 * i
        s += f"\\meterc{{7.4}}{{{y}}}{{0}}{{{sym}}}\\node[lbl,text width=3.6cm] at(8.8,{y}){{{name}}};\n"
    return s


@fig("circuit-voltmeter-across-lamp")
def _():
    return r"""
\draw(0,0)--(0,.7)(0,2.5)--(0,3.6)--(1.5,3.6)(2.9,3.6)--(6.6,3.6)--(6.6,0)--(5.2,0)(3.8,0)--(0,0);
\draw(3.5,0)--(3.5,1.9)--(3.9,1.9)(5.1,1.9)--(5.5,1.9)--(5.5,0);
\cellc{0}{1.6}{-90}{3}\meterc{2.2}{3.6}{0}{A}\lampc{4.5}{0}{0}\meterc{4.5}{1.9}{0}{V}
\dotc{3.5}{0}\dotc{5.5}{0}
\sgn{-.4}{2.35}{$+$}\sgn{-.4}{.85}{$-$}\sgn{1.7}{4.0}{$+$}\sgn{2.75}{4.0}{$-$}
\sgn{5.45}{2.3}{$+$}\sgn{3.55}{2.3}{$-$}
\ca{.6}{4.0}{1.2}{4.0}\ca{7.0}{2.4}{7.0}{1.5}\ca{6.0}{-.4}{5.4}{-.4}\ca{-.4}{2.9}{-.4}{3.4}\ca{3.2}{-.4}{2.5}{-.4}
\node[cp]at(4.5,-.95){лампа};\node[cp]at(4.5,2.95){вольтметр\\параллельно лампе};\node[cp]at(2.2,4.5){амперметр в разрыве};
"""


@fig("voltage-two-lamps-series")
def _():
    return r"""
\draw(0,0)--(0,.7)(0,2.5)--(0,3.5)--(1.5,3.5)(2.9,3.5)--(4.3,3.5)(5.7,3.5)--(7.4,3.5)--(7.4,0)--(0,0);
\cellc{0}{1.6}{-90}{3}\lampc{2.2}{3.5}{0}\lampc{5.0}{3.5}{0}
\sgn{-.4}{2.35}{$+$}\sgn{-.4}{.85}{$-$}
\ca{.6}{3.9}{1.2}{3.9}\ca{3.1}{3.9}{3.7}{3.9}\ca{7.8}{2.4}{7.8}{1.6}
\node[cp]at(2.2,4.5){лампа на 220~В};\node[cp]at(5.0,4.5){лампа на 3,5~В};
\node[cp]at(2.2,2.7){$I=0{,}3$~А};\node[cp]at(5.0,2.7){$I=0{,}3$~А};
\node[cp]at(3.7,-.9){ток один, лампа на 220~В светит ярко, лампа на 3,5~В тускло};
"""


@fig("circuit-task-5-6-bell-voltmeter")
def _():
    return r"""
\draw(0,0)--(0,3)--(1.3,3)(3.3,3)--(5,3)--(5,0)--(3.4,0)(1.8,0)--(0,0);
\draw(0,1.9)--(1.9,1.9)(3.3,1.9)--(5,1.9);
\celld{2.3}{3}{0}\bellc{2.6}{0}{0}\meterc{2.6}{1.9}{0}{V}
\dotc{0}{1.9}\dotc{5}{1.9}
\sgn{.5}{3.4}{$+$}\sgn{4.1}{3.4}{$-$}
\sgn{1.75}{2.3}{$+$}\sgn{3.45}{2.3}{$-$}
\node[cp,anchor=west]at(5.5,1.9){вольтметр на звонке};
\node[cp]at(2.6,-.9){звонок};
"""


def build(name, body):
    tex = PREAMBLE + "\\begin{document}\n\\begin{tikzpicture}\n" + body + "\\end{tikzpicture}\n\\end{document}\n"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "f.tex").write_text(tex, encoding="utf-8")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "f.tex"], cwd=tmp, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            print(r.stdout[-2500:])
            raise SystemExit(f"pdflatex failed for {name}")
        subprocess.run(["pdftoppm", "-png", "-r", "200", "-singlefile", "f.pdf", "f"], cwd=tmp, check=True)
        (OUT / f"{name}.png").write_bytes((tmp / "f.png").read_bytes())
    print("wrote", name)


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        build(n, FIGS[n]())
