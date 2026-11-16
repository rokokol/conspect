# Исходники рисунков и песочниц курса "Дискретная математика"

Каждый PNG и HTML во вложениях тем курса собирается из этой папки. Тема ddlc и шрифты волта приходят из общего набора `Scripts/ddlc_figures/`, его на `sys.path` ставит `course.py`, он же задаёт корень курса

- `figures/` — скрипты рисунков по темам (`01/` … `07/`) и общий модуль `dmfig.py`: роли цветов, рисование графов, папка вывода темы
- `course.py` — корень курса; от него строятся все пути вывода

## Окружение

```bash
uv venv -p 3.12 ~/.cache/discrete-math-digitization/.venv
uv pip install --python ~/.cache/discrete-math-digitization/.venv/bin/python -r requirements.txt
```

Версии в `requirements.txt` закреплены: другая версия matplotlib меняет пиксели

## Рисунок

Скрипт рисунка называется так же, как файл: `figures/04/k33.py` пишет `k33.png` во вложения темы `04. Графы`. Если такого скрипта нет, имя ищется в коде: `grep -l "k33" figures/*/*.py`

```bash
~/.cache/discrete-math-digitization/.venv/bin/python figures/04/k33.py
```

## Песочницы

Страница `<тема>-песочница.html` лежит во вложениях темы и собирается из `interactive/`. Логика курса живёт в одном модуле `interactive/dmcore.js` (чистые функции, ES-модуль), шаблоны страниц — в `interactive/pages/`. Шрифты, тема ddlc, сборка и headless-проверка страницы — общий набор `Scripts/sandbox_kit/`, их делят все курсы

```bash
PY=~/.cache/discrete-math-digitization/.venv/bin/python
$PY interactive/export_fixtures.py             # эталоны sympy и чистого python, пишет fixtures.json
node --test interactive/dmcore.test.mjs        # ядро против эталонов
bash interactive/install_pages.sh              # собрать все страницы во вложения тем
$PY "$HOME/myWiki/.agents/skills/conspect/tools/check_page.py" <страница.html> <папка снимков> [шаг ...]
```

Шаги `check_page.py` и то, на чём он падает, описаны в его докстринге
