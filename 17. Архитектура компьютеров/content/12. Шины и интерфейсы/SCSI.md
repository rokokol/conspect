---
title: Архитектура компьютеров — SCSI
up: "[[f12. Шины и интерфейсы — MOC]]"
prev: "[[USB]]"
next: "[[SPI и QSPI]]"
lectures:
  - "12.1"
sources:
  - "[USB Mass Storage Class — Bulk-Only Transport, rev. 1.0 (USB-IF)](https://www.usb.org/sites/default/files/usbmassbulk_10.pdf)"
  - "[SCSI Block Commands (SBC) — T10](https://www.t10.org/)"
created: 2026-09-19
summary: Команды для дисков и их перенос поверх USB в Mass Storage
tags:
  - шины
aliases:
  - SCSI
  - Small Computer System Interface
  - READ(10)
  - WRITE(10)
  - CDB
  - LBA
  - Logical Block Address
  - BOT
  - Bulk-Only Transport
---
# SCSI

**SCSI** (Small Computer System Interface) — набор команд для обращения к блочным устройствам (дискам): чтение и запись секторов, опрос параметров, готовность носителя. Исторически это была и параллельная шина, но как **командный набор** SCSI пережил свою шину и лёг в основу дисковых протоколов, включая [[USB|USB]]-накопители

## Команда и CDB

Команда SCSI задаётся блоком **CDB** (Command Descriptor Block) — несколько байт, где первый байт это код операции, а дальше поля адреса и длины. Число в имени команды — длина CDB в байтах:

| Команда | Что делает |
| --- | --- |
| INQUIRY | Опрос: производитель, модель, ревизия |
| TEST UNIT READY | Готов ли носитель (в кибер-сейфе так и гейтят диск до ввода PIN) |
| READ CAPACITY | Число блоков и размер блока |
| READ(10) | Прочитать N блоков с адреса LBA; CDB 10 байт |
| WRITE(10) | Записать N блоков с адреса LBA |

`READ(10)` несёт стартовый **LBA** (Logical Block Address — номер блока) и число блоков; варианты READ(6)/(12)/(16) отличаются размером этих полей. Это и есть команда, которую [[Операционная система|ОС]] шлёт, когда читает сектора диска

## SCSI поверх USB

В [[USB#Классы USB-устройств|USB Mass Storage Class]] диск говорит именно на SCSI: команды заворачиваются в USB bulk-передачи протоколом **BOT** (Bulk-Only Transport) — команда в блоке CBW, затем данные, затем статус в CSW[^bot]

Поэтому ОС видит USB-флешку как обычный диск без драйверов, а прошивка устройства обрабатывает те же READ(10)/WRITE(10). В разобранной прошивке кибер-сейфа это обработчик READ(10), который читает сектор из зашифрованного хранилища и расшифровывает его — Фиксированный ключ шифрования (личный волт)

[^bot]: Класс Mass Storage переносит SCSI-команды поверх USB тремя bulk-транзакциями: CBW (Command Block Wrapper) с CDB, фаза данных, CSW (Command Status Wrapper) — [USB Mass Storage Class Bulk-Only Transport 1.0, §3](https://www.usb.org/sites/default/files/usbmassbulk_10.pdf)
