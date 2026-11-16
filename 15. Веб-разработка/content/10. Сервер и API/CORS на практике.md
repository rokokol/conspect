---
title: Веб-разработка — CORS на практике
up: "[[f10. Сервер и API — MOC]]"
prev: "[[Аутентификация и сессии]]"
next: "[[Деплой в Docker]]"
lectures:
  - "5"
sources:
  - "[MDN — CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)"
created: 2026-07-19
summary: Простые и preflight-запросы, словарь Access-Control-заголовков, credentials, Vary Origin и диагностика без паники
tags:
  - хэндбук
aliases:
  - CORS
  - preflight
  - Access-Control-Allow-Origin
  - кросс-доменные запросы
---
# CORS на практике
**CORS** (Cross-Origin Resource Sharing — совместное использование ресурсов между источниками) — механизм, которым *сервер* разрешает чужим origin читать свои ответы, точечно ослабляя [[Безопасность в браузере#Origin и его политика|same-origin policy]]. Учебная ситуация в чистом виде: сайт на `localhost:5173` (Vite) ходит в [[Программный интерфейс приложения|API]] на `localhost:3000` — порт входит в origin, origin разные, без CORS браузер ответ не отдаст

> [!important] Чинится на сервере, действует только в браузере
> Два вечных недоразумения:
> 1. "CORS error" в консоли лечится **на сервере** (не хватает заголовка в ответе), а не флагами fetch на клиенте
> 2. это защита *браузерная*: curl и серверный код ходят куда угодно. Запрос чаще всего даже доходит и выполняется — браузер лишь отказывается показать ответ [[Типы и коэрция|JS]]-у. Поэтому CORS — не защита данных, а контроль чтения из чужих вкладок

## Простой запрос против preflight

**Простой** — то, что умела отправить и [[HTML-документ и DOM-дерево|HTML]]-форма до всякого JS: методы GET/HEAD/POST, заголовки из белого списка, `Content-Type` только `text/plain`, `multipart/form-data` или `application/x-www-form-urlencoded`. Едет сразу; браузер лишь проверяет `Access-Control-Allow-Origin` в ответе

**Preflight** — всё остальное (PATCH/DELETE, `Content-Type: application/json`, свои заголовки): браузер сначала сам шлёт разведчика OPTIONS[^1]

```mermaid
sequenceDiagram
    participant J as JS на localhost:5173
    participant B as браузер
    participant S as API localhost:3000
    J->>B: fetch PATCH /cards/42
    B->>S: OPTIONS /cards/42 (preflight)
    Note over B,S: Origin: http://localhost:5173
Access-Control-Request-Method: PATCH
    S-->>B: Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PATCH
    B->>S: теперь сам PATCH
    S-->>B: 200 + Allow-Origin
    B-->>J: ответ доступен
```

[^1]: Граница "простого" не выдумана — это ровно возможности веба *до* fetch: формы и теги. CORS проектировали так, чтобы JS не мог отправить ничего нового, не спросив сервер, — а старое (POST формы) запретить было уже нельзя, на нём стоял весь веб. Эта унаследованная асимметрия и питает [[Безопасность в браузере#CSRF|CSRF]]: форме можно без спроса, fetch с [[Слабоструктурированные данные и JSON|JSON]] — только после preflight. Налог не на каждый запрос: preflight кэшируется (`Access-Control-Max-Age`, Chrome ограничивает потолком в 2 часа)

## Словарь заголовков

| Заголовок ответа | Смысл |
|---|---|
| `Access-Control-Allow-Origin` | кому можно: конкретный origin или `*` |
| `Access-Control-Allow-Methods` / `-Headers` | что разрешено, ответ на preflight |
| `Access-Control-Allow-Credentials: true` | разрешить запросы с cookies |
| `Access-Control-Expose-Headers` | какие заголовки *ответа* видны JS (по умолчанию почти никакие) |
| `Access-Control-Max-Age` | сколько кэшировать preflight |

> [!warning] Vary: Origin при динамическом ответе
> Сервер, отражающий разрешённый origin из списка (а не `*`), обязан добавлять `Vary: Origin` — иначе [[Кэширование и сеть глубже|кэш]] или [[Кэширование и сеть глубже|CDN]] отдаст ответ с `Allow-Origin` одного сайта другому, и CORS начнёт "случайно" ломаться у части пользователей. Классика плавающих багов: локально работает, за CDN — через раз

## Credentials

По умолчанию кросс-origin fetch **не возит cookies**. Для [[Аутентификация и сессии|сессий]] между сайтом и API нужно согласие обеих сторон:

```js
fetch("http://localhost:3000/cards", { credentials: "include" });        // клиент
```

```js
app.use(cors({ origin: "http://localhost:5173", credentials: true }));   // сервер (Hono)
```

Ограничение зашито в браузер: `credentials: true` несовместим с `Allow-Origin: *` — пускать кого угодно с чужими cookies нельзя, origin перечисляется явно. И перечислять стоит скупо: отражать *любой* пришедший Origin с credentials — значит выдать содержимое API всякому сайту, куда зашёл залогиненный пользователь

## Диагностика за минуту

1. Network → упавший запрос: есть ли OPTIONS перед ним и что в его ответе
2. Консоль Chrome называет недостающий заголовок прямым текстом ("No 'Access-Control-Allow-Origin' header…")
3. Частый виновник — preflight получает 404/405: роутер знает GET и POST, а OPTIONS не обслужен (middleware `cors()` это и чинит)
4. Ошибки сервера тоже должны нести CORS-заголовки: если middleware стоит *после* упавшего кода, браузер покажет "CORS error" вместо честного 500 — ставь `cors()` первым слоем
5. Preflight руками, без браузера: `curl -i -X OPTIONS -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: PATCH" localhost:3000/cards/42`

> [!tip] Вторая дорога — не открывать границу вовсе
> Альтернатива CORS: раздавать сайт и API с одного origin (реверс-прокси: `/api/*` → сервер, остальное — статика). Никаких preflight, cookies работают сами. Dev-аналог встроен в Vite — `server.proxy`, [[Каркас сайта на Vite|наш каркас]] так и делает. CORS настраивают, когда API *действительно* публичный для чужих сайтов, а не для собственного фронтенда
