---
title: Веб-разработка — Flexbox и Grid
up: "[[f03. CSS — MOC]]"
prev: "[[Поток и позиционирование]]"
next: "[[Адаптивность и CSS-переменные]]"
lectures:
  - "4"
sources:
  - "[MDN — Basic concepts of flexbox](https://developer.mozilla.org/ru/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox)"
  - "[MDN — Basic concepts of grid layout](https://developer.mozilla.org/ru/docs/Web/CSS/CSS_grid_layout/Basic_concepts_of_grid_layout)"
  - "[CSS-Tricks — A Guide to Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)"
  - "[CSS-Tricks — A Complete Guide to Grid](https://css-tricks.com/snippets/css/complete-guide-grid/)"
created: 2026-07-18
summary: Оси и выравнивание flexbox, треки grid и когда что выбирать
tags:
  - хэндбук
aliases:
  - flexbox
  - CSS Grid
  - CSS-раскладка
  - fr и minmax
  - CSS gap
---
# Flexbox и Grid
Два штатных механизма раскладки: **Flexbox** — одномерный (строка *или* колонка, контент диктует размеры), **Grid** — двумерный (строки *и* колонки сразу, сетка диктует размеры контенту). Оба включаются на контейнере и управляют только прямыми детьми

![[flex-grid-axes.png]]

## Flexbox

```css
.container {
  display: flex;
  flex-direction: row;        /* главная ось: row | column (+ -reverse) */
  justify-content: space-between;  /* распределение ПО главной оси */
  align-items: center;        /* выравнивание ПОПЕРЁК */
  gap: 16px;                  /* зазор между элементами */
  flex-wrap: wrap;            /* переносить не влезших на новую строку */
}
```

> [!important] Все свойства привязаны к осям, а не к сторонам экрана
> **Главная ось** (main axis) — направление `flex-direction`; **поперечная** (cross axis) — перпендикуляр. `justify-content` всегда работает вдоль главной, `align-items` — поперёк: перевернул direction на `column` — и они поменялись ролями. Мнемоника: **just**ify — как выключка текста, **align** — как выравнивание по линии строки

### Как дети делят место

| Свойство | Смысл | Дефолт |
|---|---|---|
| `flex-basis` | стартовый размер до делёжки | `auto` (по контенту) |
| `flex-grow` | доля *свободного* места, если осталось | `0` — не расти |
| `flex-shrink` | доля *ужатия*, если не влезли | `1` — ужиматься |

Шорткат `flex: 1` = `1 1 0` — "раздели всё поровну, стартуя с нуля". Классика: `nav { display: flex } .spacer { flex: 1 }` — распорка, расталкивающая логотип и меню по краям без единого margin[^1]

[^1]: Flexbox шёл к нам мучительно: три несовместимых синтаксиса (`display: box` 2009, `flexbox` 2011, `flex` 2012) успели пожить в браузерах одновременно, и старые туториалы с `-webkit-box-orient` до сих пор всплывают в поиске. Дата, после которой туториалам по flexbox можно верить — 2014

> [!tip] Незаметный дефолт align-items: stretch
> Пока не задал `align-items`, дети растягиваются на всю поперечную ось — поэтому колонки одинаковой высоты во flex-строке получаются "сами". Это тот эффект, ради которого в float-эпоху писали жуткие хаки с отрицательными margin

> [!tip] margin: auto внутри flex — точечная распорка
> У flex-детей auto-margin съедает всё свободное место в свою сторону: `margin-left: auto` у последнего пункта меню прижимает его вправо, `margin: auto` — центрирует элемент по обеим осям. Часто чище, чем городить обёртки

## Grid

```css
.layout {
  display: grid;
  grid-template-columns: 200px 1fr 1fr;   /* три колонки-трека */
  grid-template-rows: auto 1fr auto;      /* шапка / контент / подвал */
  gap: 16px;
}
.sidebar { grid-column: 1; grid-row: 2; } /* ребёнок занимает ячейку */
.hero    { grid-column: 1 / -1; }         /* от первой линии до последней — вся ширина */
```

**Трек** — строка или колонка сетки; нумеруются *линии* между ними, с единицы (и с `-1` с конца). Ребёнок без явного места кладётся в следующую свободную ячейку — авторазмещение

### Единица fr и функции треков

**`fr`** (fraction — доля) — часть свободного места: `1fr 2fr` = треть и две трети. В отличие от `%` доли считаются *после* вычета gap и фиксированных треков — арифметика сходится сама

| Инструмент | Пример | Смысл |
|---|---|---|
| `repeat()` | `repeat(12, 1fr)` | 12 одинаковых колонок |
| `minmax()` | `minmax(200px, 1fr)` | не уже 200px, расти до доли |
| `auto-fill` / `auto-fit` | `repeat(auto-fill, minmax(200px, 1fr))` | столько колонок, сколько влезет |

> [!success] Адаптивная сетка карточек без единого media query
> ```css
> .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
> ```
> Сама решает, сколько колонок влезает при любой ширине экрана. Самая цитируемая строка современного [[Каскад и селекторы|CSS]] — стоит выучить наизусть

### Именованные области

```css
.page {
  display: grid;
  grid-template-areas:
    "header header"
    "nav    main"
    "footer footer";
  grid-template-columns: 200px 1fr;
}
header { grid-area: header; }
nav    { grid-area: nav; }
```

Перестроить страницу на мобильной = переписать одну "картинку" в media query, [[HTML-документ и DOM-дерево|HTML]] не трогается[^2]

[^2]: Grid — редкий случай, когда двигателем стандарта была Microsoft: её команда предложила спецификацию и первой реализовала её в IE10 (2012, префикс `-ms-grid`) для плиточного интерфейса Windows 8. Финальный Grid вышел во всех основных браузерах за один 2017 год — беспрецедентная синхронность после десятилетий браузерных войн

## Когда что

| Ситуация | Инструмент |
|---|---|
| ряд кнопок, меню, карточка (иконка + текст), центрирование | flex |
| каркас страницы, галерея, форма "лейбл — поле", любая настоящая сетка | grid |
| раскладка от *контента* (пусть само разложится) | flex |
| раскладка от *макета* (дизайнер нарисовал сетку) | grid |

Они не конкуренты, а матрёшка: страница — grid, а внутри каждой ячейки ряды элементов — flex. Тренировка на играх: [Flexbox Froggy](https://flexboxfroggy.com/#ru) и [Grid Garden](https://cssgridgarden.com/#ru)
