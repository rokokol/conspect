# Скрипты рисунков курса "Физика 7–9"

Каждый PNG во вложениях тем курса нарисован скриптом из этой папки. Скрипт находится по имени картинки без расширения: `grep -l "<имя>" *.py`

Запуск из этой папки, все рисунки скрипта или только названные:

```bash
nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages(ps: [ps.matplotlib ps.numpy ps.scipy])) poppler-utils]' -c python3 boiling.py [name ...]
```

Схемы цепей (`circuit_diagrams.py`) рендерятся через `pdflatex` и `pdftoppm`

Общие модули: `course.py` — корень курса, от него строятся все пути вывода; `theme.py` — служебные цвета (шрифт он берёт из общего `ddlc_fonts` и сам не задаёт); `*_common.py` — общая графика тем
