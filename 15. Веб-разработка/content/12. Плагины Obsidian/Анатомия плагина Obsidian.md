---
title: Веб-разработка — Анатомия плагина Obsidian
up: "[[f12. Плагины Obsidian — MOC]]"
prev: "[[SEO и метаданные]]"
next: "[[Obsidian API]]"
lectures:
  - "1"
sources:
  - "[Obsidian — Anatomy of a plugin](https://docs.obsidian.md/Plugins/Getting+started/Anatomy+of+a+plugin)"
  - "[Obsidian — Build a plugin](https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin)"
  - "[obsidian-sample-plugin](https://github.com/obsidianmd/obsidian-sample-plugin)"
created: 2026-07-19
summary: Manifest и main.js, класс Plugin, onload и dev-цикл
tags:
  - хэндбук
  - obsidian
aliases:
  - плагин Obsidian
  - manifest.json Obsidian
  - onload onunload
  - жизненный цикл плагина
  - FSRS
---
# Анатомия плагина Obsidian
**Obsidian** — [[Архитектура Electron|Electron-приложение]]: под капотом браузер, а плагин — обычный [[Модули|JS/TS-модуль]], который редактор загружает в собственное окно и пускает к своему [[Программный интерфейс приложения|API]]. Новых языков нет — новая среда выполнения. Живой пример на весь модуль — твой FSRS Vocabulary (личный волт)[^1]

[^1]: `~/Projects/obsidian-fsrs-vocabulary` — плагин, превращающий заметки в словари с интервальным повторением. В нём сходятся все нитки курса: строгий [[Система типов TypeScript|TS]] ([[Система типов TypeScript|модуль 07]]), сборка esbuild ([[Бандлеры|модуль 08]]), алгоритм повторений **FSRS** (Free Spaced Repetition Scheduler) — прямой родственник `nextInterval` из [[Тестирование с vitest|модуля про тесты]]. Разбирать API удобнее всего на коде, который сам написал

## Плагин физически

Три файла в `.obsidian/plugins/<id>/`:

| Файл | Роль |
|---|---|
| `manifest.json` | паспорт: id, версия, minAppVersion, isDesktopOnly |
| `main.js` | весь код одним CommonJS-бандлом |
| `styles.css` | стили плагина (опционально) |

```json
// manifest.json FSRS Vocabulary
{ "id": "fsrs-vocabulary", "name": "FSRS Vocabulary", "version": "0.3.0",
  "minAppVersion": "1.13.0", "isDesktopOnly": false }
```

`id` — технический ключ (имя папки, ключ настроек; сменишь — пользователи "потеряют" плагин), `name` — что видит человек. `isDesktopOnly: false` — обещание не трогать [[Node как рантайм|Node-API]] напрямую: мобильный Obsidian — тот же код в WebView без Node, и `require("fs")` там просто нет

> [!note] Модель доверия — ревью вместо песочницы
> Песочницы для плагинов у Obsidian нет: включённый плагин исполняется с полными правами приложения — читает любой файл хранилища, а на десктопе через Node дотягивается до всей машины
>
> Безопасность держится на трёх опорах: открытый код на GitHub, ревью при попадании в каталог и сознательное включение пользователем. Отсюда практическое следствие для автора: любые сетевые запросы и файлы вне хранилища — только по явной надобности, ревью такое рассматривает под лупой

## Класс Plugin

`main.ts` экспортирует по умолчанию класс-наследник `Plugin` — так Obsidian находит вход в бандле:

```ts
import { Plugin } from "obsidian";

export default class FsrsVocabularyPlugin extends Plugin {
  async onload(): Promise<void> {   // включили плагин / запустили Obsidian
    this.addRibbonIcon("book-a", "Open as dictionary", () => { /* … */ });
    this.addCommand({ id: "add-word", name: "Add word", callback: () => { /* … */ } });
    this.addSettingTab(new FsrsVocabularySettingTab(this.app, this));
  }

  onunload(): void { /* выключили — прибрать за собой */ }
}
```

Всё из [[Объекты, прототипы и классы|модуля 04]]: класс, наследование, `async`-метод. `this.app` — вход в API редактора ([[Obsidian API|следующая заметка]])

## onload / onunload

**onload** — конструктор мира плагина: команды, вью, обработчики, чтение настроек. **onunload** — зеркало: плагины включают и выключают на лету, без перезапуска приложения, — оставшийся после выключения обработчик продолжит стрелять из ниоткуда. Это [[События|подписки]] без хозяина: утечка памяти плюс призрачные баги, которые пользователь спишет на другой плагин

> [!important] register*-методы убирают за собой сами ^register-cleanup
> Ручной `onunload` почти не нужен, если регистрировать через методы Plugin — очистка привязывается к жизни плагина автоматически:
> ```ts
> this.registerEvent(this.app.workspace.on("file-open", handler));  // снимется само
> this.registerDomEvent(document, "click", handler);                // не addEventListener напрямую!
> this.registerMarkdownPostProcessor((el, ctx) => { /* … */ });
> this.registerInterval(window.setInterval(tick, 1000));
> ```
> Правило: даёт Plugin `registerX` — только через него. В FSRS Vocabulary через `registerEvent` висят реакции на `active-leaf-change` и `resolved` кэша метаданных: переключение плагина туда-обратно не оставляет ни одного зомби

## Dev-цикл

Сэмпл-плагин Obsidian клонируется прямо в `.obsidian/plugins/` тестового хранилища, `npm run dev` держит esbuild в watch-режиме. Правка → пересборка за миллисекунды → Ctrl+R (перезагрузка окна) или плагин Hot-Reload, который делает это сам. Ошибки и `console.log` — в консоли DevTools (Ctrl+Shift+I): Obsidian и есть браузер, вся [[Отладка|отладка]] из модуля 08 работает без изменений

Тестовое хранилище — отдельное, не рабочее: плагин в разработке умеет портить файлы, и пусть портит копеечные

> [!tip] Плагин — знакомый стек под новым именем
> Деконструкция перед стартом: манифест — как `package.json`, `main.js` — как бандл сайта, `this.app` — как `window`, вью — компонент, рисующий в [[HTML-документ и DOM-дерево|DOM]], настройки — форма. Каждый "плагинный" навык — переименованный веб-навык; потому модуль и стоит в конце курса, а не вместо него
