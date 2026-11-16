#!/usr/bin/env bash
# Build every ready page into the attachments folder of the topic that owns it.
# The topic of each page is listed below. PY is a Python with fonttools and brotli.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/.cache/discrete-math-digitization/.venv/bin/python}
content="$("$PY" "$here/../course.py")/content"
declare -A topic=(
  [boolean]="02. Полнота и замкнутые классы"
  [nelson]="01. Функции алгебры логики"
  [mst]="04. Графы"
  [code-graph]="05. Алфавитное кодирование"
  [huffman]="05. Алфавитное кодирование"
  [hamming]="06. Коды, исправляющие ошибки"
  [automaton]="07. Автоматы и схемы"
)
for page in "$here"/pages/*.html; do
  name=$(basename "$page" .html)
  [[ -n ${topic[$name]:-} ]] || { echo "no topic for $name" >&2; exit 1; }
  dest="$content/${topic[$name]}/00. Вложения"
  mkdir -p "$dest"
  [[ -e "$dest/.nomedia" ]] || : > "$dest/.nomedia"
  "$PY" "$here/build_pages.py" "$name" "$dest/$name-песочница.html"
done
