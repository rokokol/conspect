"""Circuit schemes for the notes "Закон Ома для участка цепи" and "Сопротивление проводника" (section f11, lessons 151-156).

The TikZ macros for lamp, meter and cell come from circuit_diagrams.py; this file adds the resistor and the rheostat.
Run: nix shell nixpkgs#poppler-utils -c python3 ohm_circuits.py [name ...]
PNG files go to content/11. Электрические явления/00. Вложения/ (prefixes ohm-, resistance-, rheostat-)
"""
import sys

import circuit_diagrams as cd

cd.PREAMBLE += r"""
\usepackage{amsmath}
% resistor: x y angle
\newcommand{\resc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
% the body is filled white so that a wire or a hidden edge behind it does not show through
\draw(-.7,0)--(-.45,0)(.45,0)--(.7,0);\draw[fill=paper](-.45,-.16)rectangle(.45,.16);
\end{scope}}
% rheostat with slider arrow: x y angle; slider terminal at local (.15,.65)
\newcommand{\rheoc}[3]{\begin{scope}[shift={(#1,#2)},rotate=#3]
\draw(-.9,0)--(-.6,0)(.6,0)--(.9,0)(-.6,-.16)rectangle(.6,.16);
\draw[-{Stealth[length=2mm]}](.15,.65)--(.15,.2);
\end{scope}}
% voltage dimension line: x1 y x2 label
\newcommand{\vdim}[4]{\draw[<->,el](#1,#2)--(#3,#2);\node[el,font=\small,fill=paper,inner sep=1pt]at({(#1+#3)/2},#2){#4};}
"""

FIGS = {}


def fig(name):
    def deco(fn):
        FIGS[name] = fn
        return fn

    return deco


@fig("ohm-measuring-circuit")
def _():
    return r"""
\draw(0,2.3)--(0,3.2)--(2.3,3.2)(3.7,3.2)--(7,3.2)--(7,2.3)(7,.9)--(7,0)--(0,0)--(0,.9);
\draw(-1.4,.9)rectangle(1.4,2.3);\node[cp]at(0,1.6){регулируемый\\источник\\тока};
\meterc{3}{3.2}{0}{A}
\draw(5.2,3.2)--(5.2,2.3)(5.2,.9)--(5.2,0);\meterc{5.2}{1.6}{90}{V}\dotc{5.2}{3.2}\dotc{5.2}{0}
\resc{7}{1.6}{-90}
\node[cp,anchor=west]at(7.3,1.6){проводник};
\node[cp]at(3,3.8){амперметр\\последовательно};\node[cp]at(3.4,.7){вольтметр\\параллельно\\проводнику};
"""


@fig("ohm-resistor-symbol")
def _():
    return r"""
\draw(0,0)--(.4,0)(2.4,0)--(2.8,0);\draw(.4,-.3)rectangle(2.4,.3);
\fill(0,0)circle(.06)(2.8,0)circle(.06);
\node[cp]at(1.4,0){$R$};
\vdim{0}{.9}{2.8}{$U$}\draw[dashed,grey](0,.05)--(0,.9)(2.8,.05)--(2.8,.9);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](.2,-.75)--(2.6,-.75);\node[cur,font=\small]at(1.4,-1.05){$I$};
"""


@fig("ohm-lamp-resistance-scheme")
def _():
    return r"""
\draw(0,.9)--(0,0)--(6,0)--(6,.9)(6,2.3)--(6,3.2)--(3.7,3.2)(2.3,3.2)--(0,3.2)--(0,2.3);
\cellc{0}{1.6}{-90}{3}\sgn{-.4}{2.3}{$+$}\sgn{-.4}{.9}{$-$}
\meterc{3}{3.2}{0}{A}
\lampc{6}{1.6}{90}
\draw(4.4,3.2)--(4.4,2.3)(4.4,.9)--(4.4,0);\meterc{4.4}{1.6}{90}{V}\dotc{4.4}{3.2}\dotc{4.4}{0}
\node[cp,anchor=west]at(6.4,1.6){лампа};\node[cp]at(3,3.8){амперметр в цепи с лампой};
\node[cp]at(3,-.7){вольтметр на выводах лампы: $R=\dfrac{U}{I}$};
"""


@fig("ohm-voltmeter-internal-resistance")
def _():
    return r"""
\draw(0,0)--(1.6,0)(3.4,0)--(5,0);\draw(2.5,0)circle(.9);\node[font=\Large]at(2.5,0){V};
\fill(.3,0)circle(.06)(4.7,0)circle(.06);
\draw[dashed,grey](.3,.05)--(.3,1.4)(4.7,.05)--(4.7,1.4);
\draw[<->,el](.3,1.3)--(4.7,1.3);\node[el,font=\small,fill=paper,inner sep=1pt]at(2.5,1.3){$U=120$~В};
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](.3,-.5)--(1.3,-.5);\node[cur,font=\small]at(.8,-.85){$I=15$~мА};
\draw[-{Stealth[length=2mm]}](4.3,-1.3)node[right,font=\small]{$R_\text{В}=\,?$}--(3.05,-.55);
"""


@fig("resistance-gedanken-length")
def _():
    return r"""
\begin{scope}
\draw(0,3)--(1,3)(4,3)--(5,3);\draw[fill=soft](1,2.65)rectangle(4,3.35);
\draw[fill=paper](1,3)ellipse(.08 and .35);\node[cp]at(.6,3.75){$S$};
\draw[<->](1,2.3)--(4,2.3);\node[cp,fill=paper]at(2.5,2.3){$l$};
\vdim{0}{4.1}{5}{$U$}\draw[dashed,grey](0,3.05)--(0,4.1)(5,3.05)--(5,4.1);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](.1,2.6)--(.9,2.6);\node[cur,font=\small]at(.5,2.25){$I$};
\node[cp,anchor=west]at(5.5,3){$R=\dfrac{U}{I}$};
\end{scope}
\begin{scope}[yshift=-3.8cm]
\draw(0,3)--(1,3)(7,3)--(8,3);\draw[fill=soft](1,2.65)rectangle(4,3.35)(4,2.65)rectangle(7,3.35);
\draw[<->](1,2.3)--(4,2.3);\node[cp,fill=paper]at(2.5,2.3){$l$};\draw[<->](4,2.3)--(7,2.3);\node[cp,fill=paper]at(5.5,2.3){$l$};
\draw[<->](1,1.7)--(7,1.7);\node[cp,fill=paper]at(4,1.7){$2l$};
\vdim{0}{4.1}{8}{$U'=2U$}\draw[dashed,grey](0,3.05)--(0,4.1)(8,3.05)--(8,4.1);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](.1,2.6)--(.9,2.6);\node[cur,font=\small]at(.5,2.25){$I$};
\node[cp,anchor=west]at(8.4,3){$R'=\dfrac{2U}{I}=2R$};
\end{scope}
"""


@fig("resistance-gedanken-area")
def _():
    return r"""
\begin{scope}
\draw(0,3)--(1,3)(4,3)--(5,3);\draw[fill=soft](1,2.5)rectangle(4,3.5);
\draw[fill=paper](1,3)ellipse(.1 and .5);\node[cp]at(.6,3.9){$S$};
\vdim{0}{4.3}{5}{$U$}\draw[dashed,grey](0,3.05)--(0,4.3)(5,3.05)--(5,4.3);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](.1,2.6)--(.9,2.6);\node[cur,font=\small]at(.5,2.25){$I$};
\node[cp,anchor=west]at(5.5,3){$R=\dfrac{U}{I}$};
\end{scope}
\begin{scope}[yshift=-3.6cm]
\draw(0,3)--(.5,3)--(.5,3.3)--(1,3.3)(.5,3)--(.5,2.7)--(1,2.7)(4,3.3)--(4.5,3.3)--(4.5,3)--(5,3)(4,2.7)--(4.5,2.7)--(4.5,3);
\draw[fill=soft](1,3.05)rectangle(4,3.55);\draw[fill=soft](1,2.45)rectangle(4,2.95);
\draw[fill=paper](1,3.3)ellipse(.07 and .25)(1,2.7)ellipse(.07 and .25);
\node[cp,anchor=west]at(0,3.95){$S'=S/2$};
\vdim{0}{4.5}{5}{$U$}\draw[dashed,grey](0,3.05)--(0,4.5)(5,3.05)--(5,4.5);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](2,3.85)--(3,3.85);\node[cur,font=\small,anchor=west]at(3.1,3.85){$I'=I/2$};
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](2,2.15)--(3,2.15);\node[cur,font=\small,anchor=west]at(3.1,2.15){$I'=I/2$};
\node[cp,anchor=west]at(5.5,3){$R'=\dfrac{U}{I/2}=2R$};
\end{scope}
"""


@fig("resistance-cube-resistivity")
def _():
    return r"""
\draw[fill=soft](0,0)rectangle(2,2);
\draw[fill=soft!70!grey](0,2)--(.8,2.6)--(2.8,2.6)--(2,2)--cycle;
\draw[fill=soft!85!grey](2,0)--(2.8,.6)--(2.8,2.6)--(2,2)--cycle;
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](-1.2,1)--(.6,1);
\draw[cur,-{Stealth[length=2.6mm]},line width=1.1pt](2.2,1.3)--(4,1.3);
\draw[dashed,cur](.6,1)--(1.9,1.3);
\node[cur,font=\small]at(-.8,1.4){$I$};
\draw[<->](0,-.35)--(2,-.35);\node[cp,fill=paper]at(1,-.35){1 м};
\node[cp,anchor=west]at(4.4,1.3){$R$ численно равно $\rho$};
"""


@fig("rheostat-reohord")
def _():
    return r"""
\draw[fill=soft](0,0)rectangle(9,.5);
\draw[line width=1.4pt,wire](.6,.75)--(8.4,.75);
\foreach\x in{.8,1.3,...,8.2}{\draw(\x,.5)--(\x,.62);}
\foreach\x in{1,2,...,8}{\draw(\x,.5)--(\x,.7);}
\fill(.6,.75)circle(.09)(8.4,.75)circle(.09);
\draw(.6,.75)--(.6,1.2)(8.4,.75)--(8.4,1.2);\draw[fill=paper](.6,1.2)circle(.12)(8.4,1.2)circle(.12);
\draw[fill=grey!40](4.6,.55)rectangle(5.3,1.05);\draw(4.95,1.05)--(4.95,1.7);\draw[fill=paper](4.95,1.7)circle(.12);
\draw[<->](.6,-.35)--(4.95,-.35);\node[cp,fill=paper]at(2.8,-.35){$l$};
\draw[dashed,grey](.6,-.5)--(.6,0)(4.95,-.5)--(4.95,0);
\node[cp]at(7.4,2.1){проволока};\draw[-{Stealth[length=2mm]}](7.4,1.85)--(7.4,.85);
\node[cp]at(.6,1.8){клемма};\node[cp]at(8.4,1.8){клемма};
\node[cp,anchor=west]at(5.2,1.7){ползунок};
\node[cp]at(6.5,-.75){шкала};\draw[-{Stealth[length=2mm]}](6.5,-.55)--(6.5,.05);
"""


@fig("rheostat-slider-circuit")
def _():
    return r"""
% ceramic core with winding
\draw[fill=soft,rounded corners=6pt](0,0)rectangle(6.4,1.6);
\foreach\x in{.25,.45,...,6.2}{\draw[wire,line width=.8pt](\x,.05)--(\x,1.55);}
% rod and slider
\draw[line width=1.6pt](.2,2.6)--(6.4,2.6);
\draw[fill=grey!40](3.0,2.35)rectangle(3.6,2.85);\draw(3.3,2.35)--(3.3,1.55);
% winding ends and rod end terminals
\draw(.2,.8)--(-.4,.8)--(-.4,-.7);\draw[fill=paper](-.4,-.7)circle(.11);
\draw(6.4,.8)--(6.9,.8);\draw[fill=paper](6.9,.8)circle(.11);
\draw(.2,2.6)--(-.9,2.6);\draw[fill=paper](-.9,2.6)circle(.11);
% bracket for used length
\draw[<->](.25,-.35)--(3.3,-.35);\node[cp,fill=paper]at(1.8,-.35){$l$};
% outer circuit
\draw(-.9,2.6)--(-1.6,2.6)--(-1.6,-2.3)(-.4,-.7)--(-.4,-2.3);
\draw(-1.6,-2.3)--(-2.5,-2.3);
\lampc{-3.2}{-2.3}{0}
% the bottom wire stops at the battery leads (x=-3.3 and x=-1.5), so it does not run through the plates
\draw(-3.9,-2.3)--(-4.4,-2.3)--(-4.4,-3.6)--(-3.3,-3.6)(-1.5,-3.6)--(-.4,-3.6)--(-.4,-2.3);
\cellc{-2.4}{-3.6}{0}{3}
\draw[-{Stealth[length=3mm]},line width=1.1pt](3.6,3.1)--(1.3,3.1);\node[cp]at(2.4,3.45){ярче: $l$ меньше};
\draw[-{Stealth[length=3mm]},line width=1.1pt](4.5,3.1)--(6.3,3.1);\node[cp]at(5.4,3.45){тусклее};
\node[cp,anchor=west]at(3.6,2.0){ползунок};\node[cp,anchor=west]at(3.7,-.35){стержень-каркас с обмоткой};
"""


@fig("rheostat-symbol-circuit")
def _():
    return r"""
\rheoc{0}{0}{0}
\fill(-.9,0)circle(.06)(.9,0)circle(.06)(.15,.65)circle(.06);
\node[cp]at(-.9,-.4){A};\node[cp]at(.9,-.4){B};\node[cp]at(.45,.65){C};
\node[cp,anchor=north]at(0,-.9){обозначение реостата};
\begin{scope}[xshift=5cm,yshift=-1.2cm]
\draw(0,.9)--(0,0)--(2,0)(0,2.3)--(0,3.2)--(1.8,3.2)(3.2,3.2)--(4.4,3.2)--(4.4,1.4)--(3.05,1.4)--(3.05,.65);
\cellc{0}{1.6}{-90}{3}\sgn{-.4}{2.3}{$+$}\sgn{-.4}{.9}{$-$}
\lampc{2.5}{3.2}{0}\rheoc{2.9}{0}{0}\fill(3.8,0)circle(.06);
\node[cp]at(2.9,-.55){реостат};\node[cp,anchor=west]at(4.0,0){свободный вывод};
\end{scope}
"""


@fig("rheostat-plug")
def _():
    return r"""
\begin{scope}
\draw(0,0)--(.6,0);
\foreach\i/\r/\p in{0/1/0,1/2/1,2/2/1,3/5/1}{
 \pgfmathsetmacro{\x}{.6+\i*2.6}
 \resc{\x+.7}{0}{0}\node[cp]at({\x+.7},-.45){\r~Ом};
 \ifnum\p=1
  \draw[line width=1.6pt,wire](\x,0)--(\x,.7)--({\x+1.4},.7)--({\x+1.4},0);
 \else
  \draw(\x,0)--(\x,.7)--({\x+.5},.7)({\x+.9},.7)--({\x+1.4},.7)--({\x+1.4},0);\fill({\x+.5},.7)circle(.05)({\x+.9},.7)circle(.05);
 \fi
}
\draw(2,0)--(3.2,0)(4.6,0)--(5.8,0)(7.2,0)--(8.4,0)(9.8,0)--(11,0);
\node[cp,anchor=west]at(11.3,0){вынут штепсель у 1 Ом: $R=1$ Ом};
\end{scope}
\begin{scope}[yshift=-3cm]
\draw(0,0)--(.6,0);
\foreach\i/\r in{0/1,1/2,2/2,3/5}{
 \pgfmathsetmacro{\x}{.6+\i*2.6}
 \resc{\x+.7}{0}{0}\node[cp]at({\x+.7},-.45){\r~Ом};
 \draw(\x,0)--(\x,.7)--({\x+.5},.7)({\x+.9},.7)--({\x+1.4},.7)--({\x+1.4},0);\fill({\x+.5},.7)circle(.05)({\x+.9},.7)circle(.05);
}
\draw(2,0)--(3.2,0)(4.6,0)--(5.8,0)(7.2,0)--(8.4,0)(9.8,0)--(11,0);
\node[cp,anchor=west]at(11.3,0){вынуты все: $R=1+2+2+5=10$ Ом};
\end{scope}
"""


@fig("rheostat-sectional")
def _():
    return r"""
\draw(7.2,0)--(7.6,0)(9.2,0)--(9.6,0);\node[cp]at(8.4,0){$\dots$};
\begin{scope}[cur,line width=1.4pt]
\draw(0,0)--(7.2,0);
\foreach\k in{0,1,2}{\draw[fill=paper]({\k*2.4+.75},-.16)rectangle({\k*2.4+1.65},.16);\node[cp,ink]at({\k*2.4+1.2},.5){1 Ом};}
\end{scope}
\foreach\x in{0,2.4,4.8,7.2,9.6}{\fill(\x,0)circle(.09);}
\foreach\k/\x in{1/2.4,2/4.8,3/7.2,10/9.6}{\node[cp]at(\x,-.45){\k};}
% the label of contact 0 stands beside the vertical wire, not on it
\node[cp,anchor=east]at(-.15,-.45){0};
\draw(0,0)--(0,-1.6);\draw[fill=paper](0,-1.6)circle(.11);
\draw[fill=paper](9.6,-1.6)circle(.11);
\draw[line width=1.2pt,-{Stealth[length=3mm]}](9.6,-1.6)--(7.25,-.12);
\node[cp,anchor=west]at(9.9,-1.6){клемма переключателя};\node[cp,anchor=east]at(-.3,-1.6){нулевой вывод};
\node[cp]at(4.8,-2.3){переключатель на контакте 3: между клеммами три секции, $R=3$ Ом};
"""


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(FIGS)
    for n in wanted:
        cd.build(n, FIGS[n]())
