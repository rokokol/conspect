---
title: Мосин С. Г. — Архитектура компьютеров — USB
up: "[[f12. Шины и интерфейсы — MOC]]"
prev: "[[PCI Express]]"
next: "[[SCSI]]"
lectures:
  - "12"
sources:
  - "[[Архитектура компьютеров Мосин.pdf#page=337|Лекция 12 — USB, логическая модель, скорости, разъёмы, классы устройств, стр. 337–341]]"
created: 2026-09-17
summary: Последовательный интерфейс периферии — модель endpoint/pipe, версии и разъёмы
tags:
  - кфу
  - мосин
  - шины
aliases:
  - USB
  - Universal Serial Bus
  - USB endpoint
  - оконечная точка
  - USB pipe
  - USB4
  - SuperSpeed
  - Type-C
  - USB Type-C
  - USB hub
  - HID
  - MSD
  - USB-IF
  - CDC
  - CCID
  - DFU
---
# USB

**USB** (Universal Serial Bus) — последовательный интерфейс для подключения периферийных устройств, передающий одновременно и данные, и электропитание

## Endpoint и pipe

На логическом уровне устройство USB поддерживает транзакции приёма и передачи; каждый пакет транзакции несёт номер **оконечной точки** (endpoint) на устройстве. При подключении драйверы ядра [[Операционная система|ОС]] читают с устройства список оконечных точек и создают под каждую управляющую структуру данных. Совокупность оконечной точки устройства и структуры данных в ядре ОС называется **каналом** (pipe)

> [!tip] USB как сетевая инфраструктура в миниатюре
> Лектор проводит прямую параллель с [[PCI Express]]: "опять же мы имеем дело в общем-то с сетевой инфраструктурой" — endpoint и pipe играют для USB ту же роль, что порт и соединение для сети

## Версии и маркетинговые названия

| Спецификация | Скорость | Стандарт USB |
| --- | --- | --- |
| Low-Speed | до 1.5 Мбит/с | USB 1.0 |
| Full-Speed | до 12 Мбит/с | USB 1.1 |
| High-Speed | до 480 Мбит/с | USB 2.0 |
| SuperSpeed | до 5 Гбит/с | USB 3.0 / USB 3.1 Gen 1 / USB 3.2 Gen 1 |
| SuperSpeed+ 10Gbps | до 10 Гбит/с | USB 3.1 Gen 2 / USB 3.2 Gen 2 |
| SuperSpeed+ 20Gbps | до 20 Гбит/с | USB 3.2 Gen 2x2 |
| SuperSpeed+ 40Gbps | до 40 Гбит/с | USB4 |

Три написания в строке SuperSpeed — не три независимых стандарта, а переименования одного и того же физического режима 5 Гбит/с: спецификация USB 3.2 задним числом поглотила все предыдущие версии 3.x, и **USB-IF** (USB Implementers Forum) рекомендует единое маркетинговое имя "SuperSpeed USB" вместо разрозненных номеров[^usb32-rename]

То же с 10 Гбит/с — USB 3.1 Gen 2 и USB 3.2 Gen 2 обозначают один режим под именем "SuperSpeed USB 10Gbps"

[^usb32-rename]: [USB 3.2 Specification Language Usage Guidelines (USB-IF)](https://www.usb.org/sites/default/files/usb_3_2_language_product_and_packaging_guidelines_final.pdf): "The USB 3.2 specification absorbed all prior 3.x specifications. USB 3.2 identifies three transfer rates, USB 3.2 Gen 1 at 5Gbps, USB 3.2 Gen 2 at 10Gbps and USB 3.2 Gen 2x2 at 20Gbps" — рекомендованные потребительские названия "SuperSpeed USB", "SuperSpeed USB 10Gbps", "SuperSpeed USB 20Gbps" соответственно

## Разъёмы

### Standard-A, Standard-B и Micro-B

Базовые 4 контакта (VBUS, D−, D+, GND) общие для всех версий USB 2.0; версии 3.x добавляют пять контактов SuperSpeed — дифференциальные пары приёма и передачи плюс общий возвратный проводник GND_DRAIN

| № контакта | Standard-A | Standard-B | Micro-B |
| --- | --- | --- | --- |
| 1 | VBUS | VBUS | VBUS |
| 2 | D− | D− | D− |
| 3 | D+ | D+ | D+ |
| 4 | GND | GND | ID |
| 5 | StdA_SSRX−[^stda-swap] | StdA_SSTX− | GND |
| 6 | StdA_SSRX+ | StdA_SSTX+ | StdA_SSTX− |
| 7 | GND_DRAIN | GND_DRAIN | StdA_SSTX+ |
| 8 | StdA_SSTX− | StdA_SSRX− | GND_DRAIN |
| 9 | StdA_SSTX+ | StdA_SSRX+ | StdA_SSRX− |
| 10 | — | — | StdA_SSRX+ |

[^stda-swap]: На слайде (стр. 339) столбец Standard-A **дословно повторяет** столбец Standard-B: контакты 5–6 подписаны как SSTX, 7–9 как GND_DRAIN/SSRX. По независимым распиновкам разъём Standard-A несёт SSRX (приём) на контактах 5–6 и SSTX (передача) на 8–9 — то есть ровно наоборот, зеркально Standard-B: тем самым SSTX хоста на одном конце кабеля физически соединяется с SSRX устройства на другом конце. Источники: [pinoutguide.com — USB 3.0 connector pinout](https://pinoutguide.com/Slots/usb_3_0_connector_pinout.shtml) и сходящаяся с ним сводка [industry-electronics.com — USB Pin Assignment](https://industry-electronics.com/knowhow/usb-pin-assignment); таблица выше исправлена на корректный порядок

Разъём Micro-B физически меньше: четвёртым контактом у него идёт ID, земля GND смещена на пятый, а пять SuperSpeed-контактов идут следом, на позицию правее относительно Standard-контактов

### Type-C

24 контакта, зеркальные с двух сторон (A и B) — отсюда реверсивность подключения без учёта ориентации кабеля

| Контакт | Название | Описание | Контакт | Название | Описание |
| --- | --- | --- | --- | --- | --- |
| A1 | GND | Земля | B12 | GND | Земля |
| A2 | TX1+ | SuperSpeed пара 1, передача+ | B11 | RX1+ | SuperSpeed пара 2, приём+ |
| A3 | TX1− | SuperSpeed пара 1, передача− | B10 | RX1− | SuperSpeed пара 2, приём− |
| A4 | VBUS | Плюс питания | B9 | VBUS | Плюс питания |
| A5 | CC1 | Конфигурационный канал | B8 | SBU2 | Дополнительный канал (Sideband) |
| A6 | D+ | High-Speed пара, положение 1, данные+ | B7 | D− | High-Speed пара, положение 2, данные− |
| A7 | D− | High-Speed пара, положение 1, данные− | B6 | D+ | High-Speed пара, положение 2, данные+ |
| A8 | SBU1 | Дополнительный канал (Sideband) | B5 | CC2 | Конфигурационный канал |
| A9 | VBUS | Плюс питания | B4 | VBUS | Плюс питания |
| A10 | RX2− | SuperSpeed пара 4, приём− | B3 | TX2− | SuperSpeed пара 3, передача− |
| A11 | RX2+ | SuperSpeed пара 4, приём+ | B2 | TX2+ | SuperSpeed пара 3, передача+ |
| A12 | GND | Земля | B1 | GND | Земля |

**CC1/CC2** согласуют ориентацию и роль сторон при подключении, **SBU1/SBU2** — дополнительные боковые каналы (альтернативные режимы вроде вывода видео), пара **D+/D−** дублирована на обеих сторонах разъёма, а две независимые SuperSpeed-пары (TX1/RX1 и TX2/RX2) дают Type-C его многоканальность — на них опирается [[USB#Версии и маркетинговые названия|USB 3.2 Gen 2x2]]

> [!tip] Реверсивность — конец эпохи micro-USB
> Лектор напоминает micro-USB как разъём, который нужно было пытаться вставить дважды, чтобы попасть правильной стороной — Type-C убирает саму эту проблему за счёт зеркальной раскладки контактов

## Классы USB-устройств

| Код | Название | Примеры использования |
| --- | --- | --- |
| 00h | N/A | Не задано |
| 01h | Audio | Звуковая карта, MIDI (Musical Instrument Digital Interface) |
| 02h | Communications and CDC Control (**CDC** — Communications Device Class) | Модем, сетевая карта, `COM`-порт |
| 03h | Human Interface Device (HID) | Клавиатура, мышь, джойстик |
| 05h | Physical | Джойстик с поддержкой Force feedback |
| 06h | Image | Веб-камера, сканер |
| 07h | Printer | Принтер |
| 08h | Mass Storage Device (MSD) | USB-накопитель, карта памяти, кардридер, цифровая фотокамера |
| 09h | USB hub | USB-хаб |
| 0Ah | CDC Data | Совместно с классом CDC |
| 0Bh | Smart Card Reader (**CCID** — Integrated Circuit(s) Cards Interface Devices) | Считыватель смарт-карт |
| 0Dh | Content security | Биометрический сканер |
| 0Eh | Video Device Class | Веб-камера |
| 0Fh | Personal Healthcare | Индикатор пульса, медицинское оборудование |
| DCh | Diagnostic Device | Проверка совместимости с USB |
| E0h | Wireless Controller | Bluetooth-адаптер |
| EFh | Miscellaneous | ActiveSync-устройства |
| FEh | Application-specific | IrDA-устройства, режим обновления прошивки (**DFU**, Device Firmware Upgrade) |
| FFh | Vendor-specific | На усмотрение производителя |

Реестр кодов открыт для пополнения: после выхода этого курса USB-IF добавил как минимум коды 10h (Audio/Video Devices), 11h (Billboard), 12h (USB Type-C Bridge), 13h (Bulk Display Protocol), 14h (MCTP over USB) и 3Ch (I3C Device Class)[^class-codes-current]; MCTP — Management Component Transport Protocol, **I3C** — Improved Inter Integrated Circuit ([MIPI I3C FAQ](https://www.mipi.org/resources/i3c-frequently-asked-questions))

[^class-codes-current]: [Defined Class Codes (USB-IF)](https://www.usb.org/defined-class-codes) — актуальный реестр на момент написания заметки

## Дифференциальная передача как защита от помех

Все скоростные сигналы USB — от D+/D− до SuperSpeed-пар — идут дифференциальными парами: значение бита кодируется разностью напряжений двух проводов, а не потенциалом одного относительно земли. Наведённая на кабель внешняя помеха действует на оба провода пары почти одинаково и на приёмнике вычитается: по словам лектора (23.12.2024), "если была помеха, она наведена на обе линии... за счёт разностного сигнала шумы... подавляются"

> [!tip] Унификация разъёмов — вопрос не только техники
> Переход к единому Type-C — не чисто инженерное решение: производители разъёмов и контроллеров получают лицензионные отчисления, а унификация стандарта, по замечанию лектора (23.12.2024), "зачастую является вынужденной мерой" — не только про технику, но и про бизнес
