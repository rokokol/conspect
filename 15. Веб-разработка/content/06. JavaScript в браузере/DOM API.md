---
title: Веб-разработка — DOM API
up: "[[f06. JavaScript в браузере — MOC]]"
prev: "[[Параллельность, гонки и отмена]]"
next: "[[События]]"
lectures:
  - "1"
sources:
  - "[learn.javascript.ru — Документ](https://learn.javascript.ru/document)"
  - "[learn.javascript.ru — Поиск элементов](https://learn.javascript.ru/searching-elements-dom)"
created: 2026-07-18
summary: Поиск элементов, создание и вставка, изменение классов и данных, размеры и прокрутка
tags:
  - хэндбук
  - javascript
aliases:
  - DOM API
  - querySelector
  - classList
  - data-атрибуты
---
# DOM API
**DOM [[Программный интерфейс приложения|API]]** — интерфейс между [[Типы и коэрция|JS]] и [[HTML-документ и DOM-дерево|DOM-деревом]]: точка входа — глобальный `document`. Всё, что делает страницу живой, — это чтение и правка дерева, которое браузер уже построил из [[HTML-документ и DOM-дерево|HTML]]

## Поиск элементов

```js
document.querySelector(".card")          // первый по CSS-селектору (или null!)
document.querySelectorAll("nav a")       // все — статичный NodeList
card.querySelector(".title")             // поиск можно вести от любого узла
card.closest("article")                  // вверх по предкам — парный к querySelector
```

Селекторы — ровно те же, что в [[Каскад и селекторы|CSS]], вся мощь включена (`li:nth-child(2n)`, `[data-id="5"]`). Старые `getElementById` / `getElementsByClassName` живы и чуть быстрее, но пара `querySelector`/`querySelectorAll` покрывает всё единым синтаксисом[^1]

[^1]: `querySelector` пришёл в DOM (2008) как ответ браузеров на jQuery — библиотеку, чей `$(".card")` был настолько удобнее родного API, что ей пользовалось 90% сайтов планеты. Значок `$` в консоли DevTools — тоже наследство jQuery: `$` = querySelector, `$$` = querySelectorAll, работают прямо в консоли

> [!warning] NodeList — не массив
> У результата `querySelectorAll` есть `forEach` и [[Коллекции и итераторы#Протокол итератора|итерируемость]] (`for…of`, spread), но нет map/filter. Идиома: `[...document.querySelectorAll("a")].map(…)`. И он **статичен** — снимок на момент запроса, новые элементы в него не попадут

## Создание и вставка

```js
const li = document.createElement("li");
li.textContent = task.title;                    // безопасный текст
li.append(badge);                                // в конец детей
list.prepend(li); li.before(hr); li.after(hr);  // семейство вставок
li.remove();
old.replaceWith(fresh);
```

> [!important] textContent против innerHTML ^xss-innerhtml
> `innerHTML = строка` парсит строку как HTML — вставка *пользовательских* данных через него — готовая [[Безопасность в браузере|XSS]]-дыра (пользователь ввёл `<img src=x onerror="…">` — и его код выполнился у всех). Правило: данные — только `textContent`, `innerHTML` — для собственной статичной разметки. Подробно — [[Безопасность в браузере|модуль 09]]

Пакетная вставка: собрать в `DocumentFragment` (или строкой в `insertAdjacentHTML`) и вставить одним движением — каждая вставка в живое дерево может стоить [[Как браузер превращает ответ в пиксели|пересчёта раскладки]]

## Изменение

```js
el.classList.add("active"); el.classList.toggle("open", isOpen);   // классы — так
el.style.setProperty("--progress", pct);   // инлайн-стили — почти только для CSS-переменных
el.setAttribute("aria-expanded", "true");
el.hidden = true;                          // булевы атрибуты — свойством
input.value                                // у форм — живые свойства, не атрибуты
```

> [!tip] Состояние — классами, оформление — в CSS
> Вместо `el.style.color = "red"` из JS — `el.classList.add("invalid")`, а как выглядит invalid, решает CSS. JS управляет *состоянием*, таблица стилей — *видом*; иначе стили размазываются по двум мирам и [[Каскад и селекторы|каскад]] дерётся с инлайном

### data-атрибуты

```html
<li data-task-id="42" data-status="done">
```

```js
li.dataset.taskId     // "42" — kebab-case → camelCase, всегда строки!
li.dataset.status = "active";
```

Штатный канал "положить данные в разметку": id записи для обработчика, параметры для CSS (`[data-status="done"] { … }`). Именно на dataset строится [[События#Делегирование|делегирование]]

## Геометрия и прокрутка

```js
el.getBoundingClientRect()   // {top, left, width…} относительно окна — уже видели в самотестах
el.scrollIntoView({ behavior: "smooth", block: "center" })
el.offsetWidth               // ширина с border; чтение геометрии = принудительный layout ⚠️
```

Чередование "изменил стиль → прочитал размер → изменил → прочитал" заставляет браузер пересчитывать раскладку на каждом шаге (**layout thrashing**) — пакетируй: сначала все чтения, потом все записи ([[Производительность страницы|модуль 09]]) ^layout-thrashing
