---
title: Веб-разработка — Сервер на Hono и SQLite
up: "[[f10. Сервер и API — MOC]]"
prev: "[[Дизайн REST API]]"
next: "[[Аутентификация и сессии]]"
lectures:
  - "3"
sources:
  - "[Hono Docs](https://hono.dev/docs/)"
  - "[Node.js — node:sqlite](https://nodejs.org/api/sqlite.html)"
  - "[SQLite — WAL](https://www.sqlite.org/wal.html)"
created: 2026-07-19
summary: Роутинг на веб-стандартах, middleware-луковица, встроенный SQLite с prepared statements, транзакции и WAL
tags:
  - хэндбук
aliases:
  - Hono
  - node:sqlite
  - middleware
  - prepared statements
---
# Сервер на Hono и SQLite
Стек [[Программный интерфейс приложения|API]] колоды: **Hono** (яп. "пламя" 炎) — микрофреймворк маршрутизации поверх стандартных `Request`/`Response` — тех же объектов, что в [[fetch]], — и **SQLite** — встраиваемая [[Определение данных (DDL)|SQL]]-база: не отдельный сервер-процесс, а библиотека и один файл на диске[^1]

[^1]: SQLite — самая распространённая база данных мира с гигантским отрывом: она в каждом телефоне, браузере, телевизоре и самолёте; оценка "триллион работающих экземпляров" считается консервативной. Проект Ричарда Хиппа (2000) в общественном достоянии; тестового кода в нём в сотни раз больше боевого — уровень авиационного стандарта DO-178B. Девиз применимости от авторов: "SQLite не конкурирует с Postgres; SQLite конкурирует с fopen()"

## Роутинг

```js
import { Hono } from "hono";
import { serve } from "@hono/node-server";   // адаптер: веб-стандарты ↔ node:http

const app = new Hono();

app.get("/cards", (c) => c.json(listCards(c.req.query("status"))));
app.get("/cards/:id", (c) => {
  const card = getCard(Number(c.req.param("id")));
  return card ? c.json(card) : c.json({ error: { code: "not_found" } }, 404);
});
app.post("/cards", async (c) => {
  const body = await c.req.json();
  if (!body.front?.trim()) return c.json({ error: { code: "validation", field: "front" } }, 422);
  return c.json(createCard(body), 201);
});

serve({ fetch: app.fetch, port: Number(process.env.PORT ?? 3000) });
```

`c` — контекст запроса: `c.req.param()` — из пути, `c.req.query()` — из строки запроса, `c.json(данные, статус)` — ответ. Внутри роутер — не перебор регэкспов, а префиксное дерево: тысячи роутов матчатся за один проход по сегментам пути

Ставка на веб-стандарты даёт переносимость: тот же код исполняется в Node, Bun, Deno и на edge-платформах (Cloudflare Workers). Этим Hono и вытесняет Express, чей API заморожен в 2014 — с колбэками вместо промисов и своими объектами `req`/`res`, которых нет ни в одном стандарте

## Middleware

**Middleware** — функция, оборачивающая обработку запроса: код *до*, передача дальше через `await next()`, код *после*. Запрос проходит слои внутрь, ответ — теми же слоями наружу:

```mermaid
flowchart LR
    A["запрос"] --> B["logger"]
    B --> C["cors"]
    C --> D["auth"]
    D --> E["обработчик
роута"]
    E --> D2["auth"]
    D2 --> C2["cors"]
    C2 --> B2["logger"]
    B2 --> F["ответ"]
```

```js
import { logger } from "hono/logger";

app.use(logger());                       // на всё
app.use("/admin/*", requireAuth);        // на поддерево путей
app.onError((err, c) => c.json({ error: { code: "internal" } }, 500));  // общий catch
```

Сквозная логика — логирование, [[CORS на практике|CORS]], [[Аутентификация и сессии|аутентификация]], обработка ошибок — живёт в middleware; обработчики остаются про домен. В луковице узнаётся [[Функции и замыкания#Функции высшего порядка|композиция функций]]; сам паттерн универсален — от Express до ASP.NET

## node:sqlite

База встроена в Node (с v22; экспериментальный статус для учебного сервера не помеха):

```js
import { DatabaseSync } from "node:sqlite";

const db = new DatabaseSync(process.env.DB_PATH ?? "deck.sqlite");
db.exec("PRAGMA journal_mode = WAL");
db.exec(`CREATE TABLE IF NOT EXISTS cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  front TEXT NOT NULL, back TEXT NOT NULL,
  interval INTEGER NOT NULL DEFAULT 1, due_at TEXT
)`);

const insert = db.prepare("INSERT INTO cards (front, back) VALUES (?, ?)");
const byId = db.prepare("SELECT * FROM cards WHERE id = ?");
insert.run("closure", "функция + окружение");
byId.get(1);          // { id: 1, front: "closure", … }
```

Синхронный API здесь не грех: чтение из локального файла — микросекунды, event loop не страдает (сетевой запрос к "настоящей" базе на порядки дольше). [[Журнал транзакций (WAL)|WAL]] — первая PRAGMA любого проекта: писатель перестаёт блокировать читателей, и параллельные запросы к API не выстраиваются в очередь

Группа изменений — только транзакцией: `db.exec("BEGIN")` … `db.exec("COMMIT")` (упало посередине — `ROLLBACK`, база цела). А когда запрос "почему-то медленный" — `EXPLAIN QUERY PLAN SELECT …` покажет, идёт ли он по индексу или сканирует таблицу

> [!warning] [[SQL-инъекции|SQL-инъекция]] — вторая великая дыра веба
> Родня [[Безопасность в браузере#XSS|XSS]] по духу: данные, склеенные в код. `` db.exec(`SELECT … WHERE front = '${userInput}'`) `` — и ввод `'; DROP TABLE cards; --` исполняется как SQL[^2]. Лекарство одно и абсолютное: **prepared statements** — запрос с плейсхолдерами `?` компилируется отдельно, данные передаются отдельно и кодом стать не могут. Интерполяция строк в SQL не используется никогда, даже "тут точно число"

[^2]: Канон фольклора — xkcd №327 про школьника `Robert'); DROP TABLE Students;--` ("little Bobby Tables"). Реальность не смешнее: инъекции десятилетиями держались в топе **OWASP Top 10** (OWASP — Open Worldwide Application Security Project; рейтинг главных классов уязвимостей веба), и утечки сотен миллионов записей шли именно через них — при лекарстве, известном с 90-х

> [!tip] Смотреть базу глазами
> `nix shell nixpkgs#sqlite` → `sqlite3 deck.sqlite` → `.tables`, `.schema cards`, любой SELECT. Заглянуть в файл базы напрямую, минуя своё API, — серверный аналог "открой dist/ глазами": мгновенно отделяет "код пишет не то" от "код читает не так"
