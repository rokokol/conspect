# Исходники рисунков курса "Математическое моделирование"

Здесь лежат скрипты тех рисунков, которые собраны из кода. Тема ddlc и шрифты волта приходят из общего набора `Scripts/ddlc_figures/`, его на `sys.path` ставит `course.py`, он же задаёт корень курса

- `course.py` — корень курса; от него строятся все пути вывода
- `f03_phase_portraits.py` — `00. Вложения/figures/f03 фазовые портреты линейных систем.png`

## Запуск

Окружение — то же, что у курса "Дифференциальные уравнения" (`.sources/README.md` там): matplotlib, numpy, scipy

```bash
~/.cache/diffury-digitization/.venv/bin/python f03_phase_portraits.py
```
