---
title: Навроцкий А. — Базы данных — Модификация данных (DML)
up: "[[f02. Модификация и выборка данных — MOC]]"
prev: "[[Соединения JOIN]]"
next: "[[Подзапросы и обобщённые табличные выражения]]"
lectures:
  - "2"
sources:
  - "[Лекция 02, 05.03.2017](https://www.youtube.com/watch?v=dGwkG2VyDTY)"
created: 2026-06-28
summary: INSERT, UPDATE, DELETE, RETURNING, ON CONFLICT и TRUNCATE
tags:
  - sql
  - мгту
  - навроцкий
aliases:
  - DML модификация
  - INSERT
  - UPDATE
  - DELETE
  - RETURNING
  - ON CONFLICT
  - upsert
  - DML
  - JDBC
---
# Модификация данных (DML)
**DML** (Data Manipulation Language) — подъязык [[Определение данных (DDL)|SQL]] для работы с данными: `SELECT` их читает, а три команды правят содержимое: `INSERT` добавляет строки, `UPDATE` меняет, `DELETE` удаляет. Все умеют `RETURNING` — вернуть затронутые строки тем же запросом

## INSERT [2:12:59](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=7979s)
```sql
INSERT INTO films (code, title, did, date_prod, kind)
VALUES ('B6717', 'Tampopo', 110, '1985-02-10', 'Comedy')
RETURNING *;
```
Значения берут из `VALUES`, из `DEFAULT VALUES` или прямо из [[Выборка данных (SELECT)|SELECT]].

> [!tip] Перечисляй столбцы явно — не полагайся на их порядок [2:16:17](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8177s)
> [[Определение данных (DDL)|`ALTER TABLE` дописывает столбцы в конец]], и за время жизни базы их порядок может разойтись. `INSERT` со списком полей надёжнее, чем расчёт на позицию

> [!note] RETURNING — узнать, что вставилось [2:16:43](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8203s)
> `RETURNING *` отдаёт **все** поля добавленных строк, даже не перечисленные при вставке — в том числе [[Ключи отношения|первичный ключ]], полученный автоинкрементом. `RETURNING id` вернёт только нужный столбец (драйвер **JDBC** (Java Database Connectivity) Postgres так и узнаёт id последней вставки). Порядок возврата — как добавляли

> [!important] ON CONFLICT — upsert [2:15:29](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8129s)
> Что делать, если строка нарушает уникальность:
> ```sql
> INSERT INTO distributors (id, name) VALUES (5, 'Gizmo')
> ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;  -- заменить
> -- ON CONFLICT (id) DO NOTHING;                       -- пропустить
> ```
> `EXCLUDED` — спецалиас для **отклонённых** значений. Без `ON CONFLICT` конфликт даёт ошибку. Важно: `ON CONFLICT` ловит только нарушения `UNIQUE`; на попытку вставить `NULL` в `NOT NULL` он не спасёт — транзакция откатится с ошибкой

## UPDATE [2:20:07](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8407s)
```sql
UPDATE weather SET temp_lo = temp_lo + 1 WHERE city = 'San Francisco'
RETURNING *;
```
`SET` задаёт новые значения, `WHERE` — какие строки трогаем, `RETURNING` отдаёт строки **после** правки. Необязательный `FROM` подмешивает данные из другой таблицы — это [[Соединения JOIN|аналог соединения]] для обновления.

> [!warning] Обмен `SET a = b, b = a` работает по-разному [2:21:31](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8491s)
> По стандарту такая конструкция меняет поля **местами** (правые части берутся из исходных значений). Но некоторые [[Реляционная модель данных|СУБД]] присваивают последовательно, и оба поля получат одно значение — на это поведение лучше не закладываться

## DELETE [2:24:48](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8688s)
```sql
DELETE FROM films WHERE kind <> 'Musical' RETURNING *;
```
`USING` подмешивает другую таблицу (как `FROM` у `UPDATE`), `WHERE` отбирает строки. `RETURNING` отдаёт строки **какими они были до удаления** (после удаления отдавать уже нечего).

> [!tip] TRUNCATE — снести все строки разом [2:25:35](https://www.youtube.com/watch?v=dGwkG2VyDTY&t=8735s)
> `TRUNCATE` чистит таблицу целиком и **очень быстро**. Отличается обращением с [[Целостность и ограничения|каскадными ссылками]]: `DELETE` уважает действие внешнего ключа построчно, а `TRUNCATE … CASCADE` без разбора очищает и саму таблицу, и **все** ссылающиеся на неё
