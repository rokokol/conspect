---
title: Веб-разработка — Формы из JavaScript
up: "[[f06. JavaScript в браузере — MOC]]"
prev: "[[Хранение данных в браузере]]"
next: "[[Система типов TypeScript]]"
lectures:
  - "5"
sources:
  - "[learn.javascript.ru — Свойства и методы формы](https://learn.javascript.ru/forms-controls)"
  - "[MDN — FormData](https://developer.mozilla.org/ru/docs/Web/API/FormData)"
created: 2026-07-18
summary: Чтение полей, submit с preventDefault, FormData, Constraint Validation API, паттерн формы SPA
tags:
  - хэндбук
  - javascript
aliases:
  - формы из JS
  - FormData
  - валидация форм в JavaScript
---
# Формы из JavaScript
[[Формы|HTML-формы]] умеют отправляться сами, но в [[URL и адресация|SPA]] их перехватывают: собственная валидация, отправка [[fetch|fetch-ем]] без перезагрузки, мгновенная реакция интерфейса

## Доступ к полям

```js
const form = document.querySelector("#signup");
form.elements.email             // поле по name — form.elements лучше querySelector
form.elements.email.value      // текст; у checkbox — .checked, у select — .value
```

`form.elements` — именованная коллекция полей; радиокнопки с одним name приходят группой `RadioNodeList`, у которой `.value` — значение выбранной. Поля доступны и короче — `form.email`, но так легко словить конфликт с существующими свойствами формы (поле `name="action"` затенит `form.action`!) — привычка `elements` надёжнее

## Перехват отправки

```js
form.addEventListener("submit", async e => {
  e.preventDefault();                            // сами — без перезагрузки
  const data = Object.fromEntries(new FormData(form));   // {email: "…", plan: "pro"}
  try {
    await api("/signup", { method: "POST", body: data });
    form.reset();
  } catch (err) { showError(err); }
});
```

**FormData** — снимок формы "имя → значение": конструктор собирает все поля с `name` (безымянные — невидимы для отправки, [[Формы|правило из модуля 02]]). Дальше три пути: `Object.fromEntries` → [[Слабоструктурированные данные и JSON|JSON]] для своего [[Программный интерфейс приложения|API]]; отдать fetch как body (файлы, multipart — сам); пройтись `for (const [k, v] of data)`

> [!warning] Кнопка внутри формы отправляет её
> `<button>` без `type` — это `type="submit"`: любая "просто кнопка" в форме (показать пароль, добавить строку) нечаянно отправит форму. Привычка: во всех формах писать `type="button"` явно, submit — только настоящей кнопке отправки. Enter в текстовом поле тоже триггерит submit — поэтому перехватывают именно событие submit, а не click по кнопке

## Валидация

[[Формы#Встроенная валидация|HTML-атрибуты]] (`required`, `type="email"`, `pattern`, `min`) — первый рубеж. [[Типы и коэрция|JS]]-надстройка над ними — **Constraint Validation API**:

```js
input.validity.valid            // прошёл ли все ограничения
input.validity.typeMismatch     // конкретная причина (valueMissing, tooShort…)
input.setCustomValidity("Пароли не совпадают");   // своя ошибка — поле станет invalid
form.checkValidity()            // вся форма разом
form.noValidate = true;         // выключить браузерные пузыри, оставив validity
```

Паттерн "свои сообщения": `noValidate` на форму, на submit пройтись по полям, читать `validity` и рисовать ошибки в свои элементы (с `aria-describedby` — [[Доступность]]); [[Каскад и селекторы|CSS]]-крючки `:invalid`, `:user-invalid` подсвечивают без JS вовсе. Помнить главное: клиентская валидация — это **[[Пользовательский опыт|UX]]**, **сервер обязан перепроверить всё** ([[Дизайн REST API|модуль 10]]) — DevTools позволяет отправить что угодно мимо любой формы

> [!tip] Черновик формы в localStorage
> Связка модуля: на `input` формы (с debounce) сохранять FormData в [[Хранение данных в браузере|localStorage]], при загрузке — восстанавливать. Пользователь закрыл вкладку — текст жив. Идеальное упражнение, чтобы прочувствовать все три темы разом — оно и есть в практике
