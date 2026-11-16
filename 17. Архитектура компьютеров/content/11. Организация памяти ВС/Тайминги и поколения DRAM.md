---
title: Мосин С. Г. — Архитектура компьютеров — Тайминги и поколения DRAM
up: "[[f11. Организация памяти ВС — MOC]]"
prev: "[[Модули и адресация оперативной памяти]]"
next: "[[Кэш-память]]"
lectures:
  - "11"
sources:
  - "[[Архитектура компьютеров Мосин.pdf#page=306|Лекция 11 — временные диаграммы и параметры DRAM, пакетный режим, EDO, SDRAM, DDR SDRAM, стр. 306–311]]"
created: 2026-09-17
summary: Тайминги DRAM и поколения от FPM до DDR5
tags:
  - кфу
  - мосин
aliases:
  - тайминги DRAM
  - тайминги памяти
  - временная диаграмма DRAM
  - tRAC
  - tCAC
  - tRCD
  - tRP
  - tRAS
  - CAS latency
  - CKE
  - Clock Enable
  - FPM
  - FPM DRAM
  - Fast Page Mode
  - EDO
  - EDO DRAM
  - Extended Data Output
  - постраничный режим DRAM
  - SDRAM
  - Synchronous DRAM
  - DDR SDRAM
  - Double Data Rate
  - DQS
  - DDR2
  - DDR3
  - DDR4
  - DDR5
  - DIMM
  - Dual In-line Memory Module
  - SIMM
  - Single In-line Memory Module
  - JEDEC
  - CL
  - DDR
---
# Тайминги и поколения DRAM

$$\boxed{\text{EDO-60: } t_{CAC}=15\ \text{нс}\quad\longrightarrow\quad \text{DDR4-3200 CL22: } 22\cdot 0{,}625=13{,}75\ \text{нс}}$$

За двадцать лет задержка выдачи данных осталась порядка 15 нс, а пропускная способность выросла в десятки раз: поколения [[SRAM и DRAM|DRAM]] ускоряли обмен, а не саму матрицу [[SRAM и DRAM|ЗЭ]]

## Временные диаграммы асинхронной DRAM

![[Архитектура компьютеров Мосин.pdf#page=306&rect=147,25,645,277|480]]

Работа [[Модули и адресация оперативной памяти#Структура микросхемы памяти|микросхемы DRAM]] — последовательность управляющих сигналов с жёсткими требованиями к их взаимному расположению во времени

- **Чтение**: на выводы адреса выставляется номер строки $R_1$ и [[Модули и адресация оперативной памяти|RAS]] переводится в низкий уровень — строка защёлкнута; затем выставляется номер столбца $C_1$ и падает [[Модули и адресация оперативной памяти|CAS]]; через время доступа на линии `DATA` появляются данные $D_1$
- **Запись**: так же выбираются строка и столбец, [[Модули и адресация оперативной памяти|WE]] переводится в низкий уровень, и выставленные на `DATA` данные $D_2$ фиксируются в ячейке

Параметры быстродействия слайд называет так, как их обозначают в учебной литературе; в даташитах те же величины носят другие имена[^names]. Значения слайда — ровно паспорт 60-наносекундной FPM DRAM Micron

| Слайд | Даташит | Что это | FPM, -6 | EDO, -6 |
| --- | --- | --- | --- | --- |
| $t_{RAS}\approx 60$ нс — время доступа $T_д$ | $t_{RAC}$ | От спада RAS до появления данных на выходе | 60 | 60 |
| $t_{RC}\approx 110$ нс — длительность цикла $T_ц$ | $t_{RC}$ | Цикл произвольного чтения или записи: от доступа к одной строке до доступа к следующей | 110 | 104 |
| $t_{CAS}\approx 15$ нс | $t_{CAC}$ | От спада CAS до появления данных | 15 | 15 |
| $t_{PC}\approx 35$ нс | $t_{PC}$ | От доступа к одному столбцу до доступа к следующему — цикл постраничного режима | 35 | 25 |
| — | $t_{RAS}$ | Минимальная длительность низкого уровня RAS | 60 | 60 |
| — | $t_{RP}$ | Подзаряд (precharge) после RAS: минимальная длительность высокого уровня | 40 | 40 |
| — | $t_{RCD}$ | Задержка от спада RAS до спада CAS | — | 14 |

Цикл включает обе фазы RAS, поэтому $t_{RC}\geqslant t_{RAS}+t_{RP}=60+40=100$ нс

Чтение одного слова оказывается долгим — десятки наносекунд на доступ и больше сотни на цикл. Отсюда способы повысить быстродействие

[^names]: На стр. 307 $t_{RAS}$ и $t_{CAS}$ названы временем от перепада RAS и CAS до появления данных. В даташитах так называются $t_{RAC}$ (access time from RAS) и $t_{CAC}$ (access time from CAS), а $t_{RAS}$ и $t_{CAS}$ — минимальные длительности импульсов RAS и CAS (RAS pulse width, CAS pulse width). На диаграмме стр. 306 $T_{RAS}$ и $T_{CAS}$ как раз отмечены как длительности низкого уровня. Значения FPM — [Micron, 4, 8 MEG x 32 DRAM SIMMs MT8D432/MT16D832 datasheet](https://www.pjrc.com/mp3/simm/datasheet.html), "FPM Operating Mode: tRC 110ns, tRAC 60ns, tPC 35ns, tAA 30ns, tCAC 15ns, tRP 40ns"; значения EDO и $t_{RCD}$ — [Micron, 4 MEG x 4 EDO DRAM MT4LC4M4E8/E9 datasheet, rev. 6/98](http://vigir.missouri.edu/~gdesouza/ece4270/Manuals/DRAM.pdf), таблица "AC Electrical Characteristics": "Random READ or WRITE cycle time tRC 104", "RAS# pulse width tRAS 60", "RAS# to CAS# delay time tRCD 14", "RAS# precharge time tRP 40"

## Ускорение асинхронной DRAM

Совершенствование элементной базы даёт эффект, но ограниченный, поэтому ускоряли и сам протокол обмена

### Постраничный режим, FPM

![[Архитектура компьютеров Мосин.pdf#page=308&rect=129,25,661,193|480]]

На запрос по адресу память отдаёт данные этого и нескольких следующих адресов за один цикл RAS: строка выбрана один раз, а дальше меняются только номер столбца и CAS — $C_1, C_2, C_3, C_4$ дают $D_1…D_4$ с периодом $t_{PC}$ вместо полного цикла $t_{RC}$

Слайд называет это **пакетным режимом** (Burst Mode); в даташитах асинхронной памяти это **FPM** (Fast Page Mode)[^fpm]. Та же идея — прочитать соседние слова одной строки — лежит в [[Модули и адресация оперативной памяти#Циклическая схема расслоения|групповом чтении]]

[^fpm]: "Page operations allow faster data operations (READ, WRITE or READ-MODIFY-WRITE) within a row-address-defined page boundary. The page cycle is always initiated with a row address strobed in by RAS#, followed by a column address strobed in by CAS#. Additional columns may be accessed by providing valid column addresses, strobing CAS# and holding RAS# LOW" — [Micron, MT4LC4M4E8 datasheet](http://vigir.missouri.edu/~gdesouza/ece4270/Manuals/DRAM.pdf). Пакетным (burst) в даташитах называют другой режим, синхронной памяти: адреса следующих ячеек берёт внутренний счётчик, и новый адрес столбца подавать не нужно — "CLK also increments the internal burst counter", "Programmable burst lengths: 1, 2, 4, 8, or full page" — [Micron, 256Mb SDRAM datasheet](https://www.alliancememory.com/wp-content/uploads/Micron_256M_SDRAM_PartNo.MT48LC16M16A2.pdf)

### EDO

**EDO** (Extended Data Output, растянутый выход данных): на выходе микросхемы стоит буфер-защёлка — [[Триггеры (схемотехника)#D-триггер|триггер]], который фиксирует данные после извлечения из матрицы при подъёме CAS и держит их до следующего спада CAS. Данные уже никуда не деваются, поэтому CAS не нужно держать до конца чтения: импульс CAS короче, короче и цикл

В FPM выходы переходили в высокоимпедансное состояние по подъёму CAS, у EDO данные остаются действительными, пока RAS и [[Модули и адресация оперативной памяти|OE]] низкие[^edo]. Сокращение каждого из многих импульсов CAS даёт заметный суммарный выигрыш: у 60-наносекундных микросхем Micron $t_{PC}$ падает с 35 нс у FPM до 25 нс у EDO

[^edo]: "FAST-PAGE-MODE DRAMs have traditionally turned the output buffers off (High-Z) with the rising edge of CAS#. EDO-PAGE-MODE DRAMs operate like FAST-PAGE-MODE DRAMs, except data will remain valid or become valid after CAS# goes HIGH during READs, provided RAS# and OE# are held LOW" — [Micron, MT4LC4M4E8 datasheet](http://vigir.missouri.edu/~gdesouza/ece4270/Manuals/DRAM.pdf)

## SDRAM

**SDRAM** (Synchronous DRAM) — синхронная динамическая память: как при переходе от асинхронной логики к синхронной, все переключения в микросхеме происходят по переднему фронту синхросигнала CLK

| Сигнал | Назначение |
| --- | --- |
| **CLK** | Синхросигнал: все входы защёлкиваются по переднему фронту, он же продвигает внутренний счётчик пакета |
| **CKE** (Clock Enable) | Высокий уровень разрешает работу, низкий отключает синхросигнал и переводит микросхему в энергосберегающий режим — power-down или self refresh |
| **BA0, BA1** | Номер одного из четырёх банков внутри микросхемы, к которому относится команда; на слайде BS0, BS1[^sdram] |
| **DQM** | Маска линий данных: при записи блокирует запись, при чтении переводит выходы в высокоимпедансное состояние |
| **A10** | В командах чтения и записи включает автоматический подзаряд строки после операции; в команде подзаряда выбирает все банки или один, заданный BA0, BA1 |
| **[[Модули и адресация оперативной памяти\|CS]], RAS, CAS, WE** | Уже не стробы, а биты кода команды, защёлкиваемого по фронту CLK |

> [!note] **CAS latency** (CL) — задержка в тактах CLK от регистрации команды чтения до появления данных на выходе
> Тайминги синхронной памяти задают в тактах тройкой $t_{RCD}$–$t_{RP}$–CL: у SDRAM PC133 сорта -7E это 2-2-2 при такте 7,5 нс, т.е. по 15 нс на каждый параметр[^sdram]

[^sdram]: [Micron, 256Mb SDRAM MT48LC16M16A2 datasheet, Rev. W 05/15](https://www.alliancememory.com/wp-content/uploads/Micron_256M_SDRAM_PartNo.MT48LC16M16A2.pdf): Table 1 "Target tRCD-tRP-CL", сорт -7E — 133 МГц, 2-2-2, по 15 нс; Table 4 — "BA[1:0] define to which bank the ACTIVE, READ, WRITE, or PRECHARGE command is being applied", "CKE activates (HIGH) and deactivates (LOW) the CLK signal. Deactivating the clock provides precharge power-down and SELF REFRESH operation", "Input data is masked during a WRITE cycle. The output buffers are High-Z (two-clock latency) during a READ cycle", "A10 defining auto precharge", "A10 is sampled during a PRECHARGE command to determine if all banks are to be precharged (A10 HIGH) or bank selected by BA[1:0] (LOW)", "RAS#, CAS#, and WE# (along with CS#) define the command being entered"; "The CAS latency (CL) is the delay, in clock cycles, between the registration of a READ command and the availability of the output data"

## DDR SDRAM

**DDR SDRAM** (Double Data Rate SDRAM) — синхронная память, где за один такт происходят две передачи данных: по переднему и по заднему фронту синхроимпульса. Команды по-прежнему защёлкиваются только по переднему фронту, а данные сопровождает собственный строб **DQS** (Data Strobe)[^ddr]

В пределе это вдвое больше пропускной способности при той же частоте CLK: DDR400 работает с тактом 5 нс, т.е. на частоте 200 МГц, а данные передаёт с удвоенной частотой — отсюда 400 в названии

[^ddr]: [Micron, 512Mb DDR SDRAM MT46V datasheet, Rev. N 2/09](https://media.digikey.com/pdf/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MT46V128M4,_64M8,_32M16.pdf) — "Internal, pipelined double-data-rate (DDR) architecture; two data accesses per clock cycle", "Bidirectional data strobe (DQS) transmitted/received with data", "Commands entered on each positive CK edge", "5ns @ CL = 3 (DDR400B)". На стр. 311 и в записи 23.12.2024 DDR расшифровано как "Double или Dual Data Rate"; JEDEC использует только Double Data Rate — например, "Unbuffered, Double Data Rate, Synchronous DRAM Dual In-Line Memory Modules" в [JESD308](https://www.jedec.org/standards-documents/docs/jesd308b)

## Поколения

Стандарты DRAM и модулей публикует **JEDEC** (JEDEC Solid State Technology Association). Асинхронную память ставили модулями **SIMM** (Single In-line Memory Module), синхронную — модулями **DIMM** (Dual In-line Memory Module)

| Поколение | Обмен | Питание VDD | Скорости | Модуль |
| --- | --- | --- | --- | --- |
| FPM DRAM | Асинхронный, постраничный режим | 5 В | $t_{RAC}$ 60 нс | 72-контактный SIMM |
| EDO DRAM | Асинхронный, защёлка на выходе | 5 В | $t_{RAC}$ 50–60 нс | 72-контактный SIMM |
| SDRAM | По переднему фронту CLK | 3,3 В | До PC133 | 168-контактный DIMM |
| DDR | Данные по обоим фронтам | 2,5 В; 2,6 В у DDR400 | DDR200–DDR400 | 184-контактный DIMM |
| DDR2 | То же | 1,8 В | DDR2-400–DDR2-1066[^ddr2-bins] | 240-контактный DIMM |
| DDR3 | То же | 1,5 В | DDR3-800–DDR3-2133 | 240-контактный DIMM |
| DDR4 | То же | 1,2 В | DDR4-1600–DDR4-3200 | 288-контактный DIMM |
| DDR5 | То же | 1,1 В | DDR5-3200–DDR5-8800 | 288-контактный DIMM |

Число в имени сорта — скорость передачи данных. У модулей DDR, DDR2 и DDR3 в имени стоит пропускная способность в мегабайтах в секунду, в восемь раз больше: DDR200 — PC-1600, DDR3-1600 — PC3-12800. С DDR4 JEDEC называет модуль по сорту: DDR4-3200 — PC4-3200[^generations]

[^ddr2-bins]: Сорта DDR2-400…DDR2-800 заданы стандартом [JESD79-2B](https://cs.baylor.edu/~maurer/CSI5338/JESD79-2B.pdf), JEDEC, 2005; DDR2-1066 — у Micron MT47H

[^generations]: Модули и контакты — по названиям стандартов JEDEC: "168 Pin, PC-133 SDRAM Registered DIMM", "184 Pin, PC-1600/PC-2100 DDR SDRAM Unbuffered DIMM", "240-Pin PC2-5300/PC2-6400 DDR2 SDRAM Unbuffered DIMM", "240-Pin PC3-6400/…/PC3-17000 DDR3 SDRAM Unbuffered DIMM", "288-Pin, 1.2 V (VDD), PC4-1600/…/PC4-3200 DDR4 SDRAM Unbuffered DIMM" ([JEDEC, 4.20.26 Annex F](https://www.jedec.org/standards-documents/docs/module42026f)), "288-pin, 1.1 V (VDD)" DDR5 **UDIMM** — Unbuffered DIMM ([JEDEC JESD308](https://www.jedec.org/standards-documents/docs/jesd308b)); 72-контактный SIMM, 5 В, FPM и EDO — [Micron MT8D432 datasheet](https://www.pjrc.com/mp3/simm/datasheet.html); SDRAM 3,3 В — [Micron 256Mb SDRAM](https://www.alliancememory.com/wp-content/uploads/Micron_256M_SDRAM_PartNo.MT48LC16M16A2.pdf); DDR 2,5/2,6 В — [Micron MT46V](https://media.digikey.com/pdf/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MT46V128M4,_64M8,_32M16.pdf); DDR2 1,8 В и DDR2-533…1066 — [Micron MT47H 1Gb](https://my.eng.utah.edu/~cs5780/DRAM_datasheet.pdf); DDR3 1,5 В и сорта DDR3-800…2133 — [JEDEC JESD79-3F, July 2012](https://www.jedec.org/sites/default/files/docs/JESD79-3F.pdf): "Power Supply: 1.5 V +/- 0.075 V", таблицы 62–67; DDR5 от PC5-3200 — [Micron DDR5 UDIMM Core, Rev. E 10/21](https://gzhls.at/blob/ldb/f/a/8/7/01a8d2e592a701b7b7658543a3bc564a3c76.pdf), до 8800 — [JEDEC, пресс-релиз JESD79-5C, 17.04.2024](https://www.jedec.org/news/pressreleases/jedec-updates-jesd79-5c-ddr5-sdram-standard-elevating-performance-and-security): "Expansion of timing parameters definition from 6800 Mbps to 8800 Mbps"

### Задержка в наносекундах

CL растёт от поколения к поколению, но такт сокращается быстрее, и в наносекундах задержка чтения стоит на месте

| Память | Такт | CL | Задержка |
| --- | --- | --- | --- |
| EDO DRAM -6 | — | — | $t_{CAC}=15$ нс, $t_{RAC}=60$ нс |
| SDRAM PC133 -7E | 7,5 нс | 2 | $2\cdot 7{,}5=15$ нс |
| DDR400 | 5 нс | 3 | $3\cdot 5=15$ нс |
| DDR2-800 | 2,5 нс | 5 | $5\cdot 2{,}5=12{,}5$ нс |
| DDR3-1600K | 1,25 нс | 11 | $11\cdot 1{,}25=13{,}75$ нс |
| DDR4-3200 | 0,625 нс | 22 | $22\cdot 0{,}625=13{,}75$ нс |
| DDR5-4800 | 0,4167 нс | 40 | $40\cdot 0{,}4167\approx 16{,}7$ нс |

Сорта — из тех же документов: DDR3-1600K — "CL - nRCD - nRP 11-11-11", tAA = 13,75 нс по JESD79-3F, таблица 65; DDR4-3200 — "0.62ns @ CL = 22" у [Micron MTA8ATF1G64HZ](https://media.digikey.com/pdf/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MTA8ATF1G64HZ_8GB_DS.pdf); DDR5-4800 — сорт 48B с CL 40 в Micron DDR5 UDIMM Core, где минимальный $t_{AA}$ по всем режимам указан как 16 нс

> [!important] Процессоры ускоряются гораздо быстрее памяти, и память становится якорем производительности
> FPM, EDO, SDRAM и DDR — последовательные попытки решить эту проблему совершенствованием элементной базы и протокола. Эффект есть, но кардинально ситуацию он не меняет: нужны структурные решения, и главное из них — [[Кэш-память|кэш-память]]
