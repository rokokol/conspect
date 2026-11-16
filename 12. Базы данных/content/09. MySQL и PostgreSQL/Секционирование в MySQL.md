---
title: Навроцкий А. — Базы данных — Секционирование в MySQL
up: "[[f09. MySQL и PostgreSQL — MOC]]"
prev: "[[Уровни изоляции в MySQL]]"
next: "[[COLLATION и регистронезависимое сравнение]]"
lectures:
  - "9"
sources:
  - "[Лекция 09, mkI2q6twyc0](https://www.youtube.com/watch?v=mkI2q6twyc0)"
created: 2026-06-30
summary: Встроенное секционирование RANGE/LIST/HASH/KEY и его ограничения
tags:
  - мгту
  - навроцкий
  - масштабирование
aliases:
  - секционирование MySQL
  - PARTITION BY RANGE
  - RANGE LIST HASH KEY
  - партиционирование MySQL
---
# Секционирование в MySQL
> [!success] Секционирование встроено в синтаксис [01:08:56](https://www.youtube.com/watch?v=mkI2q6twyc0&t=4136s)
> В отличие от [[Секционирование таблиц|PostgreSQL до версии 10]], где секции собирали вручную через наследование, MySQL давно делит таблицу на куски прямо в `CREATE TABLE` — одной декларацией `PARTITION BY`

## Четыре способа деления [01:09:30](https://www.youtube.com/watch?v=mkI2q6twyc0&t=4170s)
> [!abstract] RANGE / LIST / HASH / KEY
> **RANGE** — по диапазону значений (типично по дате):
> ```sql
> PARTITION BY RANGE (YEAR(order_date)) (
>     PARTITION p_old  VALUES LESS THAN (2008),
>     PARTITION p_2008 VALUES LESS THAN (2009)
> );
> ```
> **LIST** — по точному набору значений:
> ```sql
> PARTITION BY LIST (store_id) (
>     PARTITION p_north VALUES IN (3, 5, 6, 9, 17),
>     PARTITION p_east  VALUES IN (1, 2, 10, 11, 19, 20)
> );
> ```
> **HASH** — равномерно по хешу выражения:
> ```sql
> PARTITION BY HASH (YEAR(hired)) PARTITIONS 10;
> ```
> **KEY** — то же, но хеш по ключу считает сам сервер:
> ```sql
> PARTITION BY KEY (s1) PARTITIONS 10;
> ```

## Ограничения
> [!warning] За удобство платят жёсткими рамками
> - все секции таблицы — **на одном движке хранения** (нельзя горячее на [[Стоимость операций|SSD]], холодное на [[Стоимость операций|HDD]]);
> - любой **уникальный индекс** (включая первичный ключ) обязан содержать столбцы секционирования;
> - сервер всё равно **блокирует все секции** при изменении, а не только затронутую;
> - выражение разбиения ограничено (не всякая функция годится);
> - **внешние ключи не работают** на секционированных таблицах
