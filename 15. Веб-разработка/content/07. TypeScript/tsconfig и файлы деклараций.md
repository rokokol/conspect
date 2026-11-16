---
title: Веб-разработка — tsconfig и файлы деклараций
up: "[[f07. TypeScript — MOC]]"
prev: "[[Utility types]]"
next: "[[Node и npm]]"
lectures:
  - "5"
sources:
  - "[TSConfig Reference](https://www.typescriptlang.org/tsconfig/)"
  - "[obsidian.d.ts](https://github.com/obsidianmd/obsidian-api/blob/master/obsidian.d.ts)"
created: 2026-07-18
summary: Ключевые опции tsconfig и файлы деклараций .d.ts
tags:
  - хэндбук
aliases:
  - tsconfig
  - файлы деклараций
  - .d.ts
  - DefinitelyTyped
---
# tsconfig и файлы деклараций
## tsconfig.json

```jsonc
{
  "compilerOptions": {
    "strict": true,                     // всегда; это зонтик из ~10 проверок
    "target": "ES2022",                 // какой JS генерировать (что транспилировать вниз)
    "module": "ESNext",                 // какие модули генерировать
    "moduleResolution": "Bundler",      // как ИСКАТЬ импорты (для Vite/esbuild — так)
    "noEmit": true,                     // только проверять: JS сделает бандлер
    "skipLibCheck": true,               // не перепроверять чужие .d.ts (скорость)
    "noUncheckedIndexedAccess": true    // arr[i] — это T | undefined; строже strict, стоит того
  },
  "include": ["src"]
}
```

Смысловая карта: `target`/`module` — *что генерируем*, `moduleResolution` — *как понимаем импорты*, `strict` и друзья — *насколько придираемся*. Опций за сотню, но живой проект трогает эти семь; остальное ищется в [справочнике](https://www.typescriptlang.org/tsconfig/) по мере ругани компилятора

> [!tip] Современный расклад: tsc проверяет, бандлер собирает
> Типичная схема 2020-х — `tsc --noEmit` в [[Непрерывная интеграция|CI]]/прекоммите как линтер [[Система типов TypeScript|типов]], а [[Типы и коэрция|JS]] производит [[Бандлеры|esbuild/Vite]], который типы просто вырезает (в 100 раз быстрее, но не проверяя). Разделение обязанностей: скорость сборки отдельно, строгость отдельно

## .d.ts

**Файл деклараций** `*.d.ts` — только сигнатуры: интерфейсы, типы функций, без единой строчки реализации. Так типизируют то, что существует вне твоей компиляции — чужие JS-библиотеки, глобальные [[Программный интерфейс приложения|API]], среду выполнения

```ts
// эти "чудеса" автодополнения — просто предустановленные .d.ts:
document.querySelector(".card");   // lib.dom.d.ts — весь DOM, тысячи сигнатур
[1, 2].map(x => x);                // lib.es2022.d.ts — стандартная библиотека
```

Пакет несёт типы двумя путями: свои (`"types"` в package.json — так делают все современные) или сообщество дописало в **DefinitelyTyped** — гигантский репозиторий деклараций для JS-пакетов, откуда ставятся `@types/*`: `npm i -D @types/node` — и `node:fs` типизирован[^1]

[^1]: DefinitelyTyped — один из самых активных репозиториев GitHub вообще: тысячи контрибьюторов вручную описывают типы чужих библиотек. Качество разное — там встречаются и образцовые декларации, и "any в пальто"; полезно уметь по `Ctrl+Click` провалиться в .d.ts и оценить, чему доверяешь

### Свои декларации

```ts
// globals.d.ts
declare const APP_VERSION: string;          // константа, которую подставит бандлер
declare module "*.css";                     // чтобы import "./style.css" не ругался
```

`declare` — "это существует, поверь": типовая заглушка без кода. Нужен файл в include — и среда знает про твои глобальные штуки

## Чтение реального .d.ts

`obsidian.d.ts` (~4000 строк) — единственная документация-источник для [[f12. Плагины Obsidian — MOC|плагинов]]; практика модуля — навигация по нему. Что там видно из выученного:

```ts
export abstract class Plugin extends Component {
  app: App;
  registerEvent(eventRef: EventRef): void;
  loadData(): Promise<any>;                       // ← та самая дыра: наш store обязан валидировать
}
export function normalizePath(path: string): string;
on(name: "changed", callback: (file: TFile) => any, ctx?: any): EventRef;   // перегрузки по литералу
```

Узнаётся всё: классы с наследованием ([[Объекты, прототипы и классы]]), Promise-методы ([[async и await]]), перегрузки по строковым литералам ([[Дженерики#keyof|паттерн keyof]]), и честный `any` в loadData — сигнал, что граница данных на совести плагина ([[Сужение типов#Свои стражи|стражи]])

> [!tip] Навигация по типам = чтение кода ^nav-types
> Ctrl+Click (Go to Definition) на импорте — и ты внутри .d.ts; Find All References, hover с сигнатурой. В nixvim это `gd`/`gr` через ts_ls. Навык "провалиться в типы и понять API без документации" — главный практический выхлоп всего модуля
