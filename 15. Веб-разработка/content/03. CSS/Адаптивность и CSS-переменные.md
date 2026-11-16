---
title: Веб-разработка — Адаптивность и CSS-переменные
up: "[[f03. CSS — MOC]]"
prev: "[[Flexbox и Grid]]"
next: "[[Переходы и анимации]]"
lectures:
  - "5"
sources:
  - "[MDN — Using media queries](https://developer.mozilla.org/ru/docs/Web/CSS/CSS_media_queries/Using_media_queries)"
  - "[MDN — Using CSS custom properties](https://developer.mozilla.org/ru/docs/Web/CSS/Using_CSS_custom_properties)"
created: 2026-07-18
summary: Viewport, media queries, mobile-first и CSS-переменные
tags:
  - хэндбук
aliases:
  - адаптивная вёрстка
  - media queries
  - CSS-переменные
  - custom properties
  - CSS clamp()
---
# Адаптивность и CSS-переменные
**Адаптивная вёрстка** (responsive design[^1]) — одна страница, корректная от телефона 320px до монитора 4K. Три кита: резиновые раскладки ([[Flexbox и Grid|auto-fill-сетки]], `%`/`fr` вместо px), гибкие медиа (`max-width: 100%`), и media queries для того, что резиной не решается

[^1]: Термин ввёл Ethan Marcotte статьёй "Responsive Web Design" (A List Apart, 2010) — до неё нормой были отдельные мобильные сайты на поддомене `m.` с редиректом по User-Agent. Некоторые (`m.wikipedia.org`) живы до сих пор

## Viewport

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Без неё мобильный браузер притворяется, что экран шириной 980px, рендерит десктопную страницу и уменьшает её — наследие первого iPhone, которому надо было показывать веб, свёрстанный под мониторы. Все media queries без этой строки мертвы

## Media queries

```css
/* база — мобильная, без условий */
.sidebar { display: none; }

@media (min-width: 768px) {          /* от планшета и шире */
  .sidebar { display: block; }
}
```

> [!tip] Mobile-first — это про направление каскада
> База описывает узкий экран, `min-width`-запросы *добавляют* сложность на широких. Обратный подход (desktop-first, `max-width`) заставляет на телефоне *отменять* десктопные стили — правил получается больше и они дерутся. Брейкпоинты ставь не по "стандартным устройствам", а там, где твоя вёрстка реально ломается — сужай окно и смотри

### Запросы не только про ширину

| Запрос | Что ловит |
|---|---|
| `(prefers-color-scheme: dark)` | системная тёмная тема |
| `(prefers-reduced-motion: reduce)` | пользователь просил меньше анимаций — [[Переходы и анимации#Уважение к prefers-reduced-motion|отключай декоративные]] |
| `(hover: hover)` | есть настоящий ховер (не тач) — прятать функциональность под hover на таче нельзя |
| `(orientation: landscape)` | горизонтальная ориентация |
| `print` | стили для печати: `@media print { nav { display: none } }` |

### clamp

```css
h1 { font-size: clamp(1.5rem, 4vw, 3rem); }     /* min, желаемое, max */
.wrap { width: min(90%, 70ch); margin-inline: auto; }
```

**`clamp(min, val, max)`** зажимает значение в коридор: заголовок плавно растёт с окном, но не мельче 1.5rem и не крупнее 3rem. Вместе с `min()`/`max()` покрывает большинство случаев, где раньше писали три брейкпоинта. Это называют **fluid typography**

### Container queries

```css
.card-host { container-type: inline-size; }
@container (min-width: 400px) {
  .card { flex-direction: row; }     /* карточка широкая — раскладываемся в строку */
}
```

Media query знает только размер *окна*, а карточка в сайдбаре и в основной колонке живёт в разных условиях при одном окне. **Контейнерные запросы** (2023) дают компоненту реагировать на размер собственного контейнера — вёрстка становится по-настоящему компонентной

## CSS-переменные

```css
:root {                       /* корень документа — глобальная область */
  --accent: #1e66f5;
  --gap: 16px;
}
.button {
  background: var(--accent);
  padding: calc(var(--gap) / 2) var(--gap);
}
```

**Custom property** — любое свойство с именем на `--`; читается функцией `var(--имя, fallback)`. Ключевое отличие от переменных Sass/Less: они живут в *рантайме* и **[[Каскад и селекторы|каскадируются]] как обычные свойства** — можно переопределить для поддерева, в media query или из [[Типы и коэрция|JS]] (`element.style.setProperty('--accent', 'red')`)

> [!success] Темизация — главный кейс переменных
> ```css
> :root { --bg: white; --fg: #222; }
> @media (prefers-color-scheme: dark) { :root { --bg: #1e1e2e; --fg: #cdd6f4; } }
> body { background: var(--bg); color: var(--fg); }
> ```
> Компоненты пишутся один раз в терминах переменных, тема меняется в одном месте. Так устроены темы [[f12. Плагины Obsidian — MOC|Obsidian]]: приложение публикует сотни `--background-primary`, `--text-accent` и т.п., а тема — просто файл, переопределяющий их значения

> [!tip] Переменная может хранить что угодно, даже мусор
> Значение custom property — произвольный токен-текст: `--cols: 1fr 2fr` или `--icon: "★"` легальны; валидность проверяется только в момент подстановки. Отсюда трюки: числовые "флаги" (`--dark: 1`) и передача данных из [[HTML-документ и DOM-дерево|HTML]] в [[Каскад и селекторы|CSS]] через `style="--index: 3"` — так делают каскадные задержки анимаций списков без JS: `transition-delay: calc(var(--index) * 50ms)`
