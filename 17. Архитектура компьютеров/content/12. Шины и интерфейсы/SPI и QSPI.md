---
title: Архитектура компьютеров — SPI и QSPI
up: "[[f12. Шины и интерфейсы — MOC]]"
prev: "[[SCSI]]"
lectures:
  - "12.2"
sources:
  - "[Motorola SPI Block Guide V03.06](https://web.archive.org/web/20150413003534/http://www.ee.nmt.edu/~teare/ee308l/datasheets/S12SPIV3.pdf)"
created: 2026-09-19
summary: Синхронный последовательный интерфейс к периферии и его четырёхлинейное расширение
tags:
  - шины
aliases:
  - SPI
  - Serial Peripheral Interface
  - QSPI
  - Quad SPI
  - MISO
  - MOSI
  - SCK
---
# SPI и QSPI

**SPI** (Serial Peripheral Interface) — синхронный последовательный интерфейс для связи микроконтроллера с периферией (flash, датчики, дисплеи), передающий данные по одному биту с тактированием от ведущего. Введён Motorola[^spi-origin]; в отличие от асинхронного [[USB]] на логическом уровне здесь нет пакетов и адресов — просто сдвиг битов под общий такт

[^spi-origin]: SPI как четырёхпроводный синхронный интерфейс master/slave описан в фирменной спецификации Motorola (линии **MISO** — Master Input, Slave Output; **MOSI** — Master Output, Slave Input; **SCK** — Serial Clock; SS) — [Motorola SPI Block Guide V03.06, §1](https://web.archive.org/web/20150413003534/http://www.ee.nmt.edu/~teare/ee308l/datasheets/S12SPIV3.pdf)

## Линии и роли

- **master/slave** — микроконтроллер ведущий (задаёт такт, инициирует обмен), периферия ведомая
- **синхронность** — отдельная линия такта, на каждый импульс передаётся один бит; приёмник защёлкивает его по фронту, поэтому скорость заранее не согласуют (в отличие от **UART** — Universal Asynchronous Receiver/Transmitter)

| Линия | Назначение |
| --- | --- |
| SCLK | Тактовый сигнал от master |
| MOSI | Master Out Slave In — данные к ведомому |
| MISO | Master In Slave Out — данные от ведомого |
| [[Модули и адресация оперативной памяти\|CS]] | Chip Select — выбор микросхемы на время обмена |

MOSI и MISO работают одновременно, поэтому обмен полнодуплексный. Чтение из flash: master опускает CS, шлёт по MOSI команду и адрес, ведомый отдаёт байты по MISO

## QSPI

**QSPI** (Quad SPI) — расширение, где вместо одной линии данных в каждую сторону используются четыре двунаправленных (IO0–IO3), что вчетверо ускоряет чтение. Именно QSPI держит flash в [[XIP]]-режиме: скорость выборки критична, ведь код исполняется прямо из flash. Обращение процессора к адресу превращается контроллером в QSPI-транзакцию к микросхеме
