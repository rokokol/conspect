---
name: project-discrete-math-digitization
description: "Переоцифровка дискретки (Алексеев, ВМК МГУ, 21 лекция): 41 заметка и 7 песочниц готовы и проверены 2026-10-04; где исходники и venv"
metadata:
  type: project
---

Курс `05. Конспекты/04. Дискретная математика` написан заново 2026-10-04: 7 MOC и 41 заметка, все 21 лекция, каждая заметка проверена (верность, математика, рисунки). Старые f01–f16 в корзине. `^graph` и `^degree` живут в "Графы". Песочницы (boolean, nelson, mst, code-graph, huffman, hamming, automaton) — ядро `.sources/interactive/dmcore.js` с тестами против python-эталонов

Леса удалены. Остался `~/.cache/discrete-math-digitization/.venv`: на нём работают `.sources/` курса, пересоздаётся по `.sources/requirements.txt`. Транскрипты не сохранены, `run-whisper.sh` перегенерирует их за 2–3 часа GPU. Студенческий конспект Teach-in — в `00. Вложения/` курса

**How to apply:** при правках курса; процесс оцифровки — скилл `digitize`
