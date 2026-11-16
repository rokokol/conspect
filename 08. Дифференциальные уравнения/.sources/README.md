# Исходники рисунков курса "Дифференциальные уравнения"

Каждый PNG во вложениях тем курса собирается из этой папки. Тема ddlc и шрифты волта приходят из общего набора `Scripts/ddlc_figures/`, его на `sys.path` ставит `course.py`, он же задаёт корень курса

- `figures/` — скрипты рисунков по темам (`01/` … `12/`) и общий модуль `dufig.py`: роли цветов, папки тем, сохранение
- `course.py` — корень курса; от него строятся все пути вывода

## Окружение

```bash
uv venv -p 3.12 ~/.cache/diffury-digitization/.venv
uv pip install --python ~/.cache/diffury-digitization/.venv/bin/python -r requirements.txt
```

Версии в `requirements.txt` закреплены: другая версия matplotlib меняет пиксели

## Рисунок

Скрипт рисунка называется так же, как файл: `figures/01/isoclines.py` пишет `isoclines.png` во вложения темы `01. Введение`. Если такого скрипта нет, имя ищется в коде: `grep -l "isoclines" figures/*/*.py`

```bash
~/.cache/diffury-digitization/.venv/bin/python figures/01/isoclines.py
```
