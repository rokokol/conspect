---
title: Веб-разработка — fetch
up: "[[f06. JavaScript в браузере — MOC]]"
prev: "[[События]]"
next: "[[Хранение данных в браузере]]"
lectures:
  - "3"
sources:
  - "[learn.javascript.ru — Fetch](https://learn.javascript.ru/fetch)"
  - "[MDN — Using Fetch](https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch)"
created: 2026-07-18
summary: Запросы через fetch, обработка ошибок и свой api-клиент
tags:
  - хэндбук
  - javascript
aliases:
  - fetch
  - AJAX
  - запросы из JavaScript
  - XHR
---
# fetch
**fetch** — штатный способ сходить по [[HTTP]] из кода страницы, не перезагружая её[^1]. Возвращает [[Промисы|промис]] ответа; вся эргономика — из [[async и await|async/await]]

[^1]: Технология-предок — `XMLHttpRequest`, добавленный Microsoft в IE5 (1999) для веб-версии Outlook. Пять лет никто не замечал, пока Gmail и Google Maps не показали, что страница может обновляться без перезагрузки; в 2005 подходу придумали имя **AJAX** (Asynchronous JavaScript And XML). [[Слабоструктурированные данные и JSON|XML]] из аббревиатуры давно выпал (все возят [[Слабоструктурированные данные и JSON|JSON]]), а слово осталось. fetch (2015) — переосмысление **XHR** (`XMLHttpRequest`) на промисах

## Скелет

```js
const resp = await fetch("/api/tasks");        // Response: статус и заголовки уже тут
if (!resp.ok) throw new HttpError(resp.status, resp.statusText);
const tasks = await resp.json();               // тело докачивается отдельно — второй await
```

Два await — не случайность: первый резолвится по заголовкам, тело может ещё течь по сети. Методы чтения тела — `json()`, `text()`, `blob()` (бинарь), `formData()` — одноразовые: прочитать Response можно один раз

> [!warning] fetch не считает 404 ошибкой
> Промис fetch реджектится **только** на сетевом провале (нет соединения, [[Протокол DNS|DNS]], [[CORS на практике|CORS]], отмена). Ответ 404/500 — это "успешно сходили, сервер ответил" — fulfilled! Проверка `resp.ok` (статус 200–299) — обязанность твоего кода, забывают её все. Идиома: свой [[Ошибки и их обработка#Свои классы ошибок|HttpError]] со статусом

## POST и заголовки

```js
const resp = await fetch("/api/tasks", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "выучить fetch" }),
});
```

JSON руками не собирается никогда — только `JSON.stringify`. Загрузка файлов — без Content-Type вообще: передай `body: new FormData(form)` ([[Формы из JavaScript|FormData]]), браузер сам поставит multipart с boundary; ручной Content-Type здесь — классическая ошибка, ломающая запрос

| Опция fetch | Зачем |
|---|---|
| `signal` | отмена и таймаут — [[Параллельность, гонки и отмена#Отмена|AbortController]] |
| `credentials: "include"` | слать cookies на другой origin (про origin — [[Безопасность в браузере]]) |
| `cache: "no-store"` | мимо HTTP-кэша |

## Паттерн: свой api-клиент

Голый fetch по коду не размазывают — заводят обёртку, где живут base [[URL и адресация|URL]], заголовки, проверка ok и разбор ошибок:

```js
async function api(path, { method = "GET", body } = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body && JSON.stringify(body),
  });
  if (!resp.ok) throw new HttpError(resp.status, await resp.text());
  return resp.status === 204 ? null : resp.json();
}

const tasks = await api("/tasks");
await api("/tasks", { method: "POST", body: { title } });
```

Одно место для будущих сквозных забот: токен авторизации, [[Параллельность, гонки и отмена#Ретрай с паузой|ретраи]], логирование. В [[Дизайн REST API|модуле 10]] этот клиент встретится со своим сервером

> [!tip] Потренироваться без своего сервера
> Публичные [[Программный интерфейс приложения|API]] без ключей: `https://dummyjson.com` (товары/юзеры, поддерживает POST понарошку), `https://api.github.com/users/<логин>`, `https://catfact.ninja/fact`. Практика модуля ходит именно в них; свой сервер поднимем в модуле 10

> [!note] Что fetch не умеет
> Прогресс *отправки* файла (есть только чтение потока ответа) и запросы при закрытии вкладки (для метрик — `navigator.sendBeacon`). Для живого канала сервер→клиент есть SSE (Server-Sent Events, `EventSource`) и WebSocket — двунаправленный сокет; попробуем в [[Сервер на Hono и SQLite|модуле 10]]
