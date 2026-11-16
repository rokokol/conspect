# Исходники рисунков и песочниц курса "Тренировки по ML"

Каждый PNG, GIF и HTML во вложениях тем курса собирается из этой папки. Запуск повторяем: тот же скрипт пересоздаёт файл байт в байт

- `figures/` — скрипты рисунков по темам (`01/` … `08/`) и общий модуль `figkit.py`: данные, палитра ddlc, зоны классификации, сетки моделей, GIF
- `interactive/` — песочницы: шаблоны `pages/*.html`, общее ядро моделей `mlcore.js`, сборка и проверка страниц
- тема ddlc для рисунков (стиль, палитра, шрифты) и для страниц живёт не здесь, а в общих `01. Data/04. Scripts/ddlc_figures/` и `sandbox_kit/`; `figkit.py` берёт её из `ddlc_theme` и сам шрифт не задаёт
- `course.py` — корень курса; от него строятся все пути вывода

## Окружение

```bash
uv venv -p 3.12 ~/.cache/ml-trainings-digitization/.venv
uv pip install --python ~/.cache/ml-trainings-digitization/.venv/bin/python -r requirements.txt
. ~/.cache/ml-trainings-digitization/.venv/bin/activate
```

Версии в `requirements.txt` закреплены: другая версия matplotlib или scikit-learn меняет пиксели и числа

## Рисунок

Скрипт рисунка обычно называется так же, как файл: `figures/04/tree-sine-depth.py` пишет `tree-sine-depth.png`. Если такого скрипта нет, имя ищется в коде: `grep -l "tree-growth-moons" figures/*/*.py`. Скрипты зон на нескольких датасетах собирают имя из префикса и датасета (`act-zones-` + `moons`), их находит поиск по префиксу

```bash
python figures/04/tree-sine-depth.py
python -m pytest figures/test_figkit.py
```

## Песочницы

```bash
python interactive/export_fixtures.py          # эталоны sklearn для тестов ядра, пишет fixtures.json
node --test interactive/mlcore.test.mjs        # ядро моделей против sklearn
bash interactive/install_pages.sh              # собрать все страницы во вложения тем
python "$HOME/myWiki/.agents/skills/conspect/tools/check_page.py" <страница.html> <папка снимков> [шаг ...]
```

Сборка шрифтов, темы и страницы живёт в общем наборе `01. Data/04. Scripts/sandbox_kit/`, его делят все курсы. Проверка страницы — `check_page.py` скилла `conspect`: она открывает страницу в headless Chromium из nix, выполняет шаги и сохраняет снимки, а на чём падает, сказано в её докстринге
