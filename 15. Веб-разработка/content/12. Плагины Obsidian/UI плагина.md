---
title: Веб-разработка — UI плагина
up: "[[f12. Плагины Obsidian — MOC]]"
prev: "[[Obsidian API]]"
next: "[[Сборка и публикация плагина]]"
lectures:
  - "3"
sources:
  - "[Obsidian — Settings](https://docs.obsidian.md/Plugins/User+interface/Settings)"
  - "[Obsidian — Views](https://docs.obsidian.md/Plugins/User+interface/Views)"
  - "[Obsidian Developer Docs](https://docs.obsidian.md/Home)"
created: 2026-07-19
summary: Точки входа UI плагина, Setting, Modal, свой View и стили
tags:
  - хэндбук
  - obsidian
aliases:
  - UI плагина Obsidian
  - класс Setting
  - Modal Obsidian
  - ItemView
  - MarkdownPostProcessor
---
# UI плагина
[[Пользовательский интерфейс|UI]] плагина — это [[DOM API|DOM]], в который Obsidian даёт встроиться в нескольких точках. Каждая точка — знакомая веб-работа: создать элементы, повесить [[События|обработчики]], нарисовать; Obsidian добавляет обёртки и следит, чтобы результат выглядел частью редактора

## Точки входа

| Куда | Метод / класс | В FSRS Vocabulary |
|---|---|---|
| лента слева | `addRibbonIcon(icon, title, cb)` | "Open as dictionary" |
| палитра команд | `addCommand({ id, name, callback })` | "Add word", "Review" |
| статус-бар | `addStatusBarItem()` | счётчик due-карточек |
| настройки | `PluginSettingTab` | колонки, вид, ретенция |
| диалог | `Modal` | сессия повторения |
| своя панель | `ItemView` | интерактивный вид словаря |
| рендер разметки | `registerMarkdownPostProcessor` | словарь в режиме чтения |

Иконки — по именам из набора lucide (`"book-a"`, `"dice"`); свои [[Медиа и таблицы|SVG]] регистрируются через `addIcon`

## Setting и данные

Формы настроек не верстаются руками — описываются построителем `Setting` в методе `display()` вкладки:

```ts
export class FsrsVocabularySettingTab extends PluginSettingTab {
  display(): void {
    this.containerEl.empty();                     // display зовётся при каждом открытии

    new Setting(this.containerEl)
      .setName("Default view")
      .setDesc("Как открывать словари")
      .addDropdown((d) => {
        d.setValue(this.plugin.settings.defaultView)
         .onChange(async (v) => {
           this.plugin.settings.defaultView = v;
           await this.plugin.saveSettings();       // сохранение — сразу, кнопки OK нет
         });
      });
  }
}
```

Это классический способ; FSRS Vocabulary (личный волт) с Obsidian 1.13.0 описывает вкладку декларативно, методом `getSettingDefinitions()` вместо `display()`

`.addText()`, `.addToggle()`, `.addDropdown()`, `.addSlider()` — обёртки над `<input>`. Данные живут через `loadData()`/`saveData()` — [[Слабоструктурированные данные и JSON|JSON]]-файл `data.json` в папке плагина. На границе загрузки — [[Система типов TypeScript#any против unknown|any]], поэтому канон — слить прочитанное с дефолтами: `Object.assign({}, DEFAULT_SETTINGS, await this.loadData())` — новые поля настроек получают значения, а не `undefined`

## Modal

```ts
export class ReviewModal extends Modal {
  onOpen(): void {                    // рисуем в this.contentEl
    this.contentEl.createEl("h2", { text: "Повторение" });
    const btn = this.contentEl.createEl("button", { text: "Показать ответ" });
    btn.onclick = () => this.reveal();
  }
  onClose(): void { this.contentEl.empty(); }
}
new ReviewModal(this.app, items).open();
```

> [!tip] createEl — DOM без строк
> Obsidian добавляет всем HTMLElement хелпер `createEl("button", { text, cls, attr })`: создать, настроить и вставить одним вызовом. Это [[DOM API#Создание и вставка|createElement + append]] без промежуточных переменных — и без `innerHTML`: данные попадают через `text`, так что [[Безопасность в браузере#XSS|XSS-класс]] ошибок закрыт самой конструкцией. Ревью каталога `innerHTML` с пользовательскими данными не пропускает

## Свой View

**ItemView** — полноценная панель, равноправная со встроенными (граф, файловый менеджер). Регистрация связывает строковый тип вью с фабрикой, открытие — запрос листа у [[Obsidian API#Workspace|workspace]]:

```ts
this.registerView("fsrs-vocabulary-view", (leaf) => new DictionaryEditorView(leaf, this));  // в onload

async activateView() {
  const leaf = this.app.workspace.getLeaf(true);            // новая вкладка
  await leaf.setViewState({ type: "fsrs-vocabulary-view", active: true });
}
```

Класс вью определяет `getViewType()`, `getDisplayText()` и рисует в `this.contentEl` из `onOpen`. Состояние раскладки Obsidian сохраняет между запусками — потому вью обязана уметь восстановиться из пустоты, а не рассчитывать на "открыли из команды"

**MarkdownPostProcessor** — перехват рендера режима чтения: Obsidian отдаёт готовый DOM-фрагмент заметки, плагин его дорисовывает. Так FSRS Vocabulary (личный волт) превращает таблицу слов в стилизованный словарь, не меняя текста файла — только отображение

## Стили

`styles.css` плагина грузится в общий документ, поэтому:

- селекторы — под своим префиксом (`.fsrs-vocabulary-word`): чужое не задевается
- цвета и отступы — не хардкод, а [[Адаптивность и CSS-переменные|CSS-переменные]] темы: `var(--text-muted)`, `var(--background-secondary)`, `var(--interactive-accent)`[^1]

[^1]: Obsidian публикует дизайн-токены сотнями [[Каскад и селекторы|CSS]]-переменных (`--text-normal`, `--radius-m`, `--font-monospace`). Плагин, живущий на них, автоматически совпадает с любой из 200+ community-тем и с переключением светлая/тёмная; захардкоженный `#1e1e2e` сломается в светлой теме у половины пользователей. Тот же принцип дизайн-токенов — в любом большом веб-продукте, Obsidian лишь честно его экспортирует

> [!important] Фреймворк ради кнопки не нужен
> Соблазн затащить React в плагин почти всегда вреден: раздутый бандл, конфликт с жизненным циклом вью, риски на мобильном. `createEl` + [[События#Делегирование|делегирование]] + классы покрывают практически всё; тяжёлую интерактивную панель оправданно строить на лёгком Svelte, но стартовать — на ванильном DOM из [[DOM API|модуля 06]]
