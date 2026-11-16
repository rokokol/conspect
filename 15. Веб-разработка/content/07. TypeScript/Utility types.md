---
title: Веб-разработка — Utility types
up: "[[f07. TypeScript — MOC]]"
prev: "[[Дженерики]]"
next: "[[tsconfig и файлы деклараций]]"
lectures:
  - "4"
sources:
  - "[TS Handbook — Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)"
  - "[type-challenges](https://github.com/type-challenges/type-challenges)"
created: 2026-07-18
summary: Partial, Pick, Omit, Record, typeof и as const
tags:
  - хэндбук
aliases:
  - utility types
  - Partial и Pick
  - Record<K, V>
  - mapped types
  - as const
---
# Utility types
**Utility types** — встроенные типы-функции: берут тип, возвращают его преобразование. Идея — **один источник правды**: сущность описана единожды, все производные формы (патч, черновик, словарь) вычисляются из неё и обновляются сами при её изменении

## Ежедневная обойма

| Тип | Что делает | Типичный кейс |
|---|---|---|
| `Partial<T>` | все поля необязательны | патч: `update(id, changes: Partial<Card>)` |
| `Required<T>` | все обязательны | конфиг после подстановки дефолтов |
| `Pick<T, K>` | только поля K | `Pick<Card, "front" \| "back">` — форма создания |
| `Omit<T, K>` | все, кроме K | `Omit<Card, "id">` — до сохранения в базу |
| `Readonly<T>` | всё readonly | иммутабельное состояние |
| `Record<K, V>` | словарь K → V | `Record<Grade, number>` — интервалы повторения |
| `ReturnType<F>` / `Parameters<F>` | из типа функции | типизировать обёртки и моки |
| `Awaited<T>` | распаковать Promise | `Awaited<ReturnType<typeof api>>` |
| `NonNullable<T>` | минус null/undefined | после проверки |

```ts
type NewCard = Omit<Card, "id" | "createdAt">;
function createCard(data: NewCard): Card { … }
```

## typeof и as const

```ts
const defaults = { theme: "dark", pageSize: 20 };
type Config = typeof defaults;               // тип «как у значения» — конфиг сам себе схема

const GRADES = ["again", "good", "easy"] as const;   // readonly ["again", "good", "easy"]
type Grade = (typeof GRADES)[number];        // "again" | "good" | "easy"
```

`typeof` (в типовой позиции) снимает тип с значения; `as const` запрещает расширение литералов до string/number. Связка `as const` + `[number]` — канонический способ иметь **и** массив для рантайма (итерация, кнопки), **и** union-тип для компилятора из одного списка — не дублируя его

> [!warning] as const ≠ as
> `as const` — безопасное уточнение литералов. Голый `x as SomeType` — **приведение**, которое отключает проверку ("поверь мне"): компилятор поверит и ошибётся вместе с тобой. Легитимен на границах после честной проверки; `as any` — капитуляция. Грепни чужой проект по ` as ` — по количеству видно культуру кода

## Под капотом

Все utility — обычные типы, записанные в стандартной библиотеке через два механизма:

```ts
type Partial<T> = { [K in keyof T]?: T[K] };            // mapped: цикл по ключам
type NonNullable<T> = T extends null | undefined ? never : T;   // conditional: if для типов
```

**Mapped type** — "для каждого ключа из [[Дженерики#keyof|keyof]] возьми поле и модифицируй" (`?`, `readonly`, переименование через `as`). **Conditional** `A extends B ? X : Y` — ветвление; по union распределяется поэлементно — так `NonNullable` "вычитает" варианты. Плюс `infer` — паттерн-матчинг ("вытащи тип из середины") — им написан ReturnType

Писать такое с нуля нужно редко — читать в исходниках библиотек приходится постоянно. [[Система типов TypeScript|Система типов TS]], к слову, тьюринг-полна: на ней пишут судоку и шахматы[^1]

[^1]: Спортивная дисциплина существует официально: репозиторий [type-challenges](https://github.com/type-challenges/type-challenges) — сотни задач "реализуй utility type" от easy до extreme. Пара easy-задач оттуда — в практике модуля; extreme-уровень — там реализуют парсеры и арифметику в типах

> [!tip] Шаблонные литеральные типы
> ```ts
> type EventName = `card:${"added" | "removed"}`;   // "card:added" | "card:removed"
> ```
> Типы-строки с интерполяцией (2021): типизируют строковые соглашения — имена событий, роуты, [[Каскад и селекторы|CSS]]-переменные. Комбинаторика раскрывается сама: два union по 3 варианта дают union из 9 строк
