---
title: Сидоров А. М. — Математический анализ — Открытые и замкнутые множества в n-мерном пространстве
up: "[[f15. n-мерное евклидово пространство — MOC]]"
prev: "[[Теорема Больцано–Вейерштрасса в n-мерном пространстве]]"
next: "[[Предел функции нескольких переменных]]"
lectures:
  - "44.2"
sources:
  - "[[00. Вложения/scans/out213.jpg|Лекция 45 — определение замкнутого множества через производное]]"
  - "[[00. Вложения/scans/out214.jpg|Лекция 45 — замыкание, внутренняя точка, внутренность, открытое множество, открытый шар открыт]]"
  - "[[00. Вложения/scans/out215.jpg|Лекция 45 — граница множества, пример замкнутого шара, двойственность открытого и замкнутого]]"
  - "[[00. Вложения/scans/out237.jpg|Лекция 48 (повтор, семестр 3) — характеризация замыкания через окрестности]]"
  - "[[00. Вложения/scans/out238.jpg|Лекция 48 (повтор, семестр 3) — замыкание объединения и пересечения]]"
created: 2026-06-16
summary: Замкнутое содержит свои предельные точки, открытое состоит из внутренних
tags:
  - кфу
  - функции_многих_переменных
  - сидоров
aliases:
  - открытое множество в Rn
  - замкнутое множество в Rn
  - замыкание множества
  - внутренность множества
  - граница множества
---
# Открытые и замкнутые множества в n-мерном пространстве

## Замкнутые множества и замыкание
> [!note] Замкнутое множество и замыкание
> Множество $A\subset\mathbb{R}^n$ **замкнуто**, если содержит все свои предельные точки:
> $$A'\subset A$$
> **Замыканием** $A$ называется множество $\overline{A}=A\cup A'$ — само $A$ вместе со всеми предельными точками

> [!question]+ Упражнение — три равносильных описания замкнутости
> Для $A\subset\mathbb{R}^n$ эквивалентны:
> 1. $A$ замкнуто $(A'\subset A)$
> 2. $A=\overline{A}$
> 3. если $(x_m)\subset A$ и $x_m\to x$, то $x\in A$ — замкнутость как **устойчивость к пределу**
> 
> > [!success]- Решение
> > Всюду опираемся на $\overline{A}=A\cup A'$ и [[Предельные точки множества в n-мерном пространстве|определение предельной точки]] ($x\in A'$ $\iff$ есть $(x_m)\subset A$, $x_m\neq x$, $x_m\to x$). Замкнём цепочку через $(1)\Leftrightarrow(2)$ и $(1)\Leftrightarrow(3)$
> >
> > **$(1)\Leftrightarrow(2)$.** Включение $A\subset\overline{A}$ верно всегда, поэтому
> > $$A=\overline{A}\iff\overline{A}\subset A\iff A\cup A'\subset A\iff A'\subset A,$$
> > а последнее — в точности определение (1)
> >
> > **$(1)\Rightarrow(3)$.** Пусть $A'\subset A$, дана $(x_m)\subset A$, $x_m\to x$. Если среди $x_m$ бесконечно много равных $x$, то $x\in A$ как один из членов. Иначе бесконечно много $x_m\neq x$ — эта подпоследовательность из точек $A$, отличных от $x$, сходится к $x$, значит $x\in A'\subset A$. В обоих случаях $x\in A$
> >
> > **$(3)\Rightarrow(1)$.** Пусть выполнено (3) и $x\in A'$. По определению предельной точки найдётся $(x_m)\subset A$, $x_m\neq x$, $x_m\to x$. По (3) тогда $x\in A$. Следовательно $A'\subset A$ $\blacksquare$

## Замыкание объединения и пересечения
> [!success] $x\in\overline A\iff$ в каждой окрестности $x$ есть точка $A$
> $$x\in\overline A\iff\forall\varepsilon>0\ \bigl(B_\varepsilon(x)\cap A\neq\varnothing\bigr)$$
> Отличие от [[Предельные точки множества в n-мерном пространстве#Критерий через окрестность|критерия предельной точки]] — здесь точка $A$ в окрестности **может совпадать с $x$**, поэтому ловятся и сами точки $A$, и предельные
>
> > [!success]- Доказательство
> > $\overline A=A\cup A'$. Если $x\in A$, то $x\in B_\varepsilon(x)\cap A$ при любом $\varepsilon$. Если $x\in A'$, то в каждой $B_\varepsilon(x)$ есть точка $A$, отличная от $x$
> >
> > Обратно: пусть каждая $B_\varepsilon(x)$ пересекает $A$. Либо в какой-то окрестности встретилась сама $x$ — тогда $x\in A$; либо во всех окрестностях точки $A$ отличны от $x$ — тогда $x\in A'$. В обоих случаях $x\in A\cup A'=\overline A$ $\blacksquare$

> [!important] $$\overline{A\cup B}=\overline A\cup\overline B,\qquad \overline{A\cap B}\subset\overline A\cap\overline B$$
>
> > [!success]- $\overline{A\cup B}=\overline A\cup\overline B$
> > $(\supset)$ Из $A\subset A\cup B$ следует $\overline A\subset\overline{A\cup B}$, и так же для $B$ — значит $\overline A\cup\overline B\subset\overline{A\cup B}$
> > $(\subset)$ От противного: пусть $x\notin\overline A\cup\overline B$, то есть $x\notin\overline A$ и $x\notin\overline B$. Тогда найдутся $\varepsilon_1,\varepsilon_2$ с $B_{\varepsilon_1}(x)\cap A=\varnothing$ и $B_{\varepsilon_2}(x)\cap B=\varnothing$. При $\varepsilon=\min(\varepsilon_1,\varepsilon_2)$ шар $B_\varepsilon(x)$ не пересекает ни $A$, ни $B$, а значит и $A\cup B$ — поэтому $x\notin\overline{A\cup B}$ $\blacksquare$
> 
> > [!example]- Для пересечения равенства может не быть
> > Возьмём в $\mathbb{R}$ непересекающиеся $A=(0,1)$ и $B=(1,2)$: тогда $A\cap B=\varnothing$, поэтому $\overline{A\cap B}=\varnothing$, тогда как $\overline A\cap\overline B=[0,1]\cap[1,2]=\{1\}$. Вложение строгое — общая точка замыканий $1$ ни в $A$, ни в $B$ не лежит

## Открытые множества
> [!note] Внутренняя точка, внутренность, открытое множество
> Точка $x$ — **внутренняя** для $A$, если входит в $A$ вместе с некоторой своей окрестностью ($\exists\varepsilon>0:\ B_\varepsilon(x)\subset A$). Множество всех внутренних точек — **внутренность** $\overset{\circ}{A}$. Множество $A$ **открыто**, если все его точки внутренние:
> $$A\subset\overset{\circ}{A}\quad(\text{равносильно }A=\overset{\circ}{A})$$

> [!success] Открытый шар — это открытое множество
> Любой открытый шар $B_r(x_0)$ открыт
>
> > [!success]- Доказательство (запас радиуса + неравенство треугольника)
> > Пусть $x\in B_r(x_0)$, т.е. $\lVert x-x_0\rVert<r$. Возьмём остаточный радиус
> > $$r_0=r-\lVert x-x_0\rVert>0$$
> > и покажем $B_{r_0}(x)\subset B_r(x_0)$. Для $y\in B_{r_0}(x)$ по [[n-мерное евклидово пространство#Норма и три её свойства|неравенству треугольника]]:
> > $$\lVert y-x_0\rVert=\lVert(y-x)+(x-x_0)\rVert\leqslant\lVert y-x\rVert+\lVert x-x_0\rVert<r_0+\lVert x-x_0\rVert=r$$
> > Значит $y\in B_r(x_0)$, то есть вокруг $x$ нашёлся шар внутри $B_r(x_0)$ — точка внутренняя $\blacksquare$
>
> ![[ball-is-open.png|380]]

## Граница
> [!note] Граница множества
> **Границей** множества $A$ называется
> $$\partial A=\overline{A}\cap\overline{A^c}$$
> — пересечение замыканий самого $A$ и его дополнения $A^c=\mathbb{R}^n\setminus A$
>
> > [!tip] Эквивалентно определению через внутренность множества
> > $$\partial A=\overline{A}\setminus\overset{\circ}{A}$$

> [!example] Замкнутый шар $A=\{\lVert x-x_0\rVert\leqslant r\}$
> Для замкнутого шара
> $$A'=A,\qquad \overset{\circ}{A}=\{\lVert x-x_0\rVert<r\},\qquad \partial A=\{\lVert x-x_0\rVert=r\}$$
> Производное множество совпало с $A$ (шар замкнут), внутренность — открытый шар, граница — сфера радиуса $r$
>
> ![[closed-ball-parts.png|360]]

## Открытое и замкнутое — двойственны

> [!example] Дополнение меняет тип
> $A\subset\mathbb{R}^n$ открыто $\iff$ $A^c=\mathbb{R}^n\setminus A$ замкнуто
> 
> > [!success]- Доказательство
> > **Определения:**
> > - $A$ **открыто**, если $\forall x \in A\ \exists \varepsilon > 0: B(x,\varepsilon) \subset A$
> > - $A$ **замкнуто**, если для любой $(x_k) \subset A$ с $x_k \to x$ выполнено $x \in A$
> > 
> > ---
> > **($\Rightarrow$) $A$ открыто $\Rightarrow$ $A^c$ замкнуто**
> > 
> > Пусть $(x_k) \subset A^c$ и $x_k \to x$. Допустим $x \in A$. Тогда:
> > $$\exists\, \varepsilon > 0 : B(x,\varepsilon) \subset A$$
> > Но $x_k \to x$, значит $\exists N: \forall k \geq N \quad x_k \in B(x,\varepsilon) \subset A$ — противоречие с $x_k \in A^c$
> > Значит $x \in A^c$, и $A^c$ замкнуто $\blacksquare$
> > 
> > ---
> > **($\Leftarrow$) $A^c$ замкнуто $\Rightarrow$ $A$ открыто**
> > 
> > Пусть $x \in A$. Допустим, что $\forall \varepsilon > 0: B(x,\varepsilon) \not\subset A$. Тогда:
> > $$\forall k \in \mathbb{N}\ \exists\, x_k \in B\!\left(x, \tfrac{1}{k}\right) \cap A^c$$
> > Получаем $(x_k) \subset A^c$ и $x_k \to x$. Так как $A^c$ замкнуто — $x \in A^c$, противоречие
> > Значит, нужный $\varepsilon$ существует, и $A$ открыто $\blacksquare$
