---
title: Веб-разработка — Electron на практике
up: "[[f13. Desktop-приложения — MOC]]"
prev: "[[Архитектура Electron]]"
next: "[[Tauri]]"
lectures:
  - "2"
sources:
  - "[Electron — Quick Start](https://www.electronjs.org/docs/latest/tutorial/tutorial-prerequisites)"
  - "[Electron — IPC](https://www.electronjs.org/docs/latest/tutorial/ipc)"
created: 2026-07-19
summary: Минимальное приложение Electron, IPC-канал, нативные API и упаковка
tags:
  - хэндбук
aliases:
  - Electron практика
  - BrowserWindow
  - ipcMain и ipcRenderer
  - electron-builder
  - упаковка приложения
---
# Electron на практике
Собираем минимальное приложение по модели [[Архитектура Electron|"сервер / таможня / клиент"]]. Итоговый проект — десктопная "Колода": те же карточки, что в [[Сервер на Hono и SQLite|API модуля 10]], но в нативном окне и локальном файле

## Минимум

```js
// main.js — "сервер"
const { app, BrowserWindow } = require("electron");
const path = require("node:path");

function createWindow() {
  const win = new BrowserWindow({
    width: 900, height: 700,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,      // дефолт, но границу безопасности пишем явно
      nodeIntegration: false,
    },
  });
  win.loadFile("index.html");      // в dev — loadURL("http://localhost:5173")
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
```

`app` — жизненный цикл приложения (родня [[Анатомия плагина Obsidian#onload / onunload|onload/onunload]] плагина), `BrowserWindow` — окно с веб-страницей. Проверка `platform !== "darwin"` — традиция macOS: там приложение живёт в доке и после закрытия всех окон[^1]

[^1]: `darwin` — имя ядра macOS в `process.platform` (`darwin`/`win32`/`linux`). Кроссплатформенность Electron честная, но не бесплатная: меню, поведение окон, положение кнопок, автозапуск — у каждой [[Операционная система|ОС]] свои традиции, и ветвления по platform в main-коде зрелого приложения встречаются десятками. "Написал раз — работает везде" на десктопе означает "запускается везде; чтобы ощущалось родным — докручивай каждую платформу"

## IPC-канал целиком

Один канал "сохрани и загрузи колоду" через все три файла:

```js
// preload.js — "таможня"
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("deck", {
  save: (cards) => ipcRenderer.invoke("deck:save", cards),
  load: () => ipcRenderer.invoke("deck:load"),
});
```

```js
// main.js — обработчики (рядом с createWindow)
const { ipcMain } = require("electron");
const fs = require("node:fs/promises");
const file = path.join(app.getPath("userData"), "deck.json");

ipcMain.handle("deck:save", (_e, cards) => {
  if (!Array.isArray(cards)) throw new Error("deck:save ждёт массив");  // renderer не на доверии
  return fs.writeFile(file, JSON.stringify(cards));
});
ipcMain.handle("deck:load", async () => {
  try { return JSON.parse(await fs.readFile(file, "utf8")); }
  catch { return []; }        // файла ещё нет — пустая колода
});
```

```js
// renderer (app.js) — "клиент", Node не касается вовсе
await window.deck.save(cards);
const cards = await window.deck.load();
```

> [!important] Данные — в app.getPath("userData")
> Писать рядом с приложением нельзя: в Program Files нет прав, при обновлении всё стирается. Electron знает системные пути каждой ОС: `userData` (настройки, база), `documents`, `temp` — `getPath` возвращает правильный для текущей платформы. Принцип тот же, что [[Деплой в Docker#^volume-persist|volume в Docker]]: данные живут отдельно от кода и переживают его замену

## Нативные возможности

То, ради чего десктоп вместо [[Каркас сайта на Vite|сайта]], — всё из main:

| API | Что даёт |
|---|---|
| `dialog` | нативные окна открыть/сохранить |
| `Menu` / `Tray` | меню приложения, иконка в трее |
| `Notification` | системные уведомления |
| `globalShortcut` | горячие клавиши уровня ОС |
| `shell` | открыть файл или ссылку внешней программой |
| `powerMonitor` | сон/пробуждение машины |

## Dev и упаковка

**Dev-цикл**: renderer грузится с [[Каркас сайта на Vite|Vite dev-сервера]] (`loadURL(":5173")`) — [[Бандлеры#^hmr|HMR]] работает прямо в десктоп-окне; main при правках перезапускается. Связки типа `electron-vite` сводят это в одну команду

**Упаковка**: `electron-builder` собирает установщики — `.exe`/`.dmg`/`.AppImage`, с иконками, автообновлением (`autoUpdater`) и подписью. Здесь всплывает налог, которого не было у [[Деплой сайта|сайта]]:

- **подпись кода** — платный сертификат; без него Windows SmartScreen и macOS Gatekeeper пугают пользователя "неизвестным разработчиком"
- **нотарификация macOS** — с Catalina обязательна: собранный бинарь отправляется Apple на автоматическую проверку, иначе система его не запустит
- вес: минимальное приложение — ~80–100 МБ, это цена Chromium в комплекте

> [!tip] Отладка — двумя знакомыми инструментами сразу
> Renderer — [[Отладка|DevTools]] (`win.webContents.openDevTools()`), как любая страница. Main — это Node: `--inspect` и брейкпоинты в редакторе. Ошибки "почему канал молчит" локализуются за минуту: консоль renderer показывает, ушёл ли invoke, терминал main — дошёл ли handle
