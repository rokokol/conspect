---
title: Веб-разработка — async и await
up: "[[f05. Асинхронный JavaScript — MOC]]"
prev: "[[Промисы]]"
next: "[[Параллельность, гонки и отмена]]"
lectures:
  - "3"
sources:
  - "[learn.javascript.ru — Async/await](https://learn.javascript.ru/async-await)"
  - "[learn.javascript.ru — Микрозадачи](https://learn.javascript.ru/microtask-queue)"
created: 2026-07-18
summary: Синтаксис async-функций, семантика await, try/catch вместо .catch, типичные ошибки последовательного await
tags:
  - хэндбук
  - javascript
aliases:
  - async await
  - асинхронные функции
  - top-level await
---
# async и await
```js
async function loadReport(id) {
  try {
    const user = await loadUser(id);          // "подожди промис, отдай значение"
    const posts = await loadPosts(user);
    return render(user, posts);               // вернётся промисом
  } catch (err) {                             // reject любого await — сюда
    showError(err);
  }
}
```

`async`/`await` (2017) — синтаксис поверх [[Промисы|промисов]], никакой новой механики: асинхронный код читается и **обрабатывает ошибки** как синхронный — обычным [[Ошибки и их обработка|try/catch]], циклами, ранними return

## Семантика

1. **`async`-функция всегда возвращает промис.** `return 42` → fulfilled(42); `throw` → rejected. Даже `async () => {}` возвращает промис undefined-а
2. **`await p` ставит функцию на паузу до устаканивания `p`**, не блокируя [[Event loop|поток]]: функция снимается со стека, продолжение — микротаск после резолва. fulfilled → await возвращает значение; rejected → бросает исключение. `await` не-промиса просто возвращает его (но пауза на микротаск всё равно случается)

> [!note] Под капотом — генератор
> Движок компилирует async-функцию в [[Коллекции и итераторы#Генераторы|генератор]], где каждый await — точка `yield`; рантайм дёргает `next()` по мере резолва промисов. Отсюда и точное понимание: до первого await функция выполняется **синхронно**, как обычный вызов

## Типичные ошибки

> [!warning] Последовательный await там, где нужна параллельность
> ```js
> const a = await fetchA();      // 300ms          const [a, b] = await Promise.all(
> const b = await fetchB();      // ещё 300ms  →     [fetchA(), fetchB()]);   // 300ms всего
> ```
> Каждый await — точка ожидания: независимые запросы выстраиваются в очередь на ровном месте. Правило: **сначала запусти всё** (вызовы без await создают промисы, работа уже пошла), **потом жди** — `Promise.all` из [[Параллельность, гонки и отмена]]

> [!warning] Забытый await
> `const data = fetchJson(url)` без await — в data лежит промис, а не данные; `data.items` — undefined, а ошибка запроса станет unhandled rejection где-то потом. Коварный вариант — `return await p` против `return p` в try/catch: без await reject **не** поймается этим catch (функция уже вернула промис наружу). Внутри try — пиши `return await`

> [!warning] await в forEach не работает
> `arr.forEach(async x => await save(x))` — forEach не ждёт колбэки: все запустились разом, внешний код пошёл дальше. Последовательно — `for (const x of arr) await save(x)`; параллельно — `await Promise.all(arr.map(save))`. Выбор между ними — осознанный: последовательно = щадяще к серверу, параллельно = быстро

## Top-level await

В [[Модули|ES-модулях]] await разрешён на верхнем уровне файла — без обёртки в async-функцию:

```js
const config = await fetch("/config.json").then(r => r.json());
export default config;
```

Импортёры такого модуля автоматически ждут его готовности. Удобно для инициализации; расплата — модуль-тормоз задерживает всё дерево импортов. В скриптах без `type="module"` и в CommonJS — недоступен

> [!tip] async в обработчиках событий — можно, но осторожно
> `button.onclick = async () => { … }` легально: обработчику никто не ждёт результата, промис уходит в никуда. Значит, весь код внутри обязан сам ловить свои ошибки (try/catch на всё тело), иначе — unhandledrejection. Та же логика для `setInterval(async …)`: интервалы тикают, не дожидаясь предыдущего — легко получить наслоение запросов
