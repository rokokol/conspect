# Исходники рисунков курса "Архитектура компьютеров"

Каждый PNG из matplotlib во вложениях тем курса собирается скриптом из этой папки. Тема ddlc и шрифты волта приходят из общего набора `Scripts/ddlc_figures/`, его на `sys.path` ставит `course.py`, он же задаёт корень курса

| Скрипт | Рисунки |
| --- | --- |
| `plot_topologies.py` | `топология-*.png` |
| `plot_amdahl.py` | `деление-времени-амдал-густафсон.png`, `ускорение-амдал-густафсон.png` |
| `rings.py` | `кольца-защиты.png` |
| `modrm_sib.py` | `Раскладка ModRM и SIB.png` |
| `hysteresis.py` | `Петля гистерезиса триггера Шмитта.png` |

## Запуск

Окружение — venv курса "Тренировки по ML" с закреплёнными версиями, его `.sources/README.md` говорит, как его собрать

```bash
~/.cache/ml-trainings-digitization/.venv/bin/python plot_topologies.py
```
