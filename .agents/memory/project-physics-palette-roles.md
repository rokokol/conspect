---
name: project-physics-palette-roles
description: "Перевод цветов схем физики на роли ddlc-palette — завершён 2026-10-24; решения, отступления и как прогнать все скрипты курса"
metadata:
  type: project
---

Цвета всех схем `05. Конспекты/09. Физика/.sources/` переведены на роли палитры и приняты Хозяином 2026-10-24. В скриптах не осталось ни одного hex, ни именованного цвета matplotlib, ни чужой colormap: только роли из `theme.py` и `tint(роль, x)`; колормапы собираются из ролей (`matter_atoms.py`).

Роли и соглашения лектора — в `.sources/theme.py`: RED/BLUE/GREEN/VIOLET/ACCENT/SKY/COPPER/WARM/PINK/METAL/MUTED/LIGHT/SERIES, `tint`; север синий, юг красный, горячее красное, «+» красный. Решения Хозяина: жёлтого нет, тёплое (пламя, золото, масло, песок) идёт в WARM; линза BLUE; облик по пилоту «Оптики».

Отступления, принятые по ходу (не ломать при будущих правках):
- WARM (#F1A796) и PINK слишком светлы для тонкой линии или текста на белом. Поэтому тонкие линии и подписи «тёплого» берут COPPER (#D1897E): `OIL_EDGE = COPPER` в `pressure_atmosphere.py` (общий для всех «давлений»), `ORANGE = COPPER` в `pressure_pumps.py`, `work_power.py` и `pressure_manometers.py`
- подписи на бледных заливках — INK (`balloons.py`, «масло» в `pressure_press.py`); белый текст остался только на насыщенных заливках и заменён на PAPER
- жидкости: вода `tint(SKY, 0.7)`, раствор соли `tint(BLUE, 0.6)` в заливке и VIOLET на графиках (иначе сливался с водой), керосин `tint(WARM, 0.6)`, масло `tint(WARM, 0.45)`, ртуть METAL
- металл, дерево, песок: METAL / `tint(COPPER, 0.55)` / `tint(WARM, 0.85)`

Запуск курса: одного `nix shell` с matplotlib мало — семь TikZ-скриптов (`circuit_diagrams`, `circuit_power_problems`, `connections`, `current_media_1`, `joule_lenz`, `kr_189_190`, `ohm_circuits`) зовут `pdflatex` и `pdftoppm`. Нужен `pkgs.poppler-utils` в окружении и системный TeX на PATH:
`nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages (ps: [ps.matplotlib ps.numpy ps.scipy ps.fonttools])) pkgs.poppler-utils]' -c bash -c 'export PATH=/etc/profiles/per-user/rokokol/bin:$PATH; python3 SCRIPT.py'`
Прогон всех 62 скриптов 2026-10-24 — exit 0, предупреждений о глифах нет

**Why:** работа была отложена как дорогая; записаны решения, чтобы следующая правка схем не переоткрывала их заново

**How to apply:** новую схему рисовать сразу ролями и проверять WARM/PINK на белом глазами; после любой правки общих `*_common.py` и `pressure_atmosphere.py` прогонять всех их импортёров (grep по имени); приёмку вести по самим PNG в `content/<тема>/00. Вложения/`, вложений в git нет
