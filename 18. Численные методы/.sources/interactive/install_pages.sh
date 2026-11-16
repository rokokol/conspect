#!/usr/bin/env bash
# Build every ready page into the attachments folder of the topic that owns it.
# The topic of each page is listed below. PY is a Python with fonttools and brotli.
# A page inlines numkit and sandbox_kit from the vault, so run this script again after a change there.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/.cache/discrete-math-digitization/.venv/bin/python}
content="$("$PY" "$here/../course.py")/content"
# page template -> the topic folder and the attachment name
declare -A topic=(
  [iterations]="01. Итерационные методы и неподвижная точка"
  [second-kind]="02. Квадратурные методы"
  [spectral]="04. Спектральные задачи"
)
declare -A file=(
  [iterations]="итерации-песочница.html"
  [second-kind]="уравнения-второго-рода-песочница.html"
  [spectral]="спектральные-песочница.html"
)
for page in "$here"/pages/[!_]*.html; do
  name=$(basename "$page" .html)
  [[ -n ${topic[$name]:-} ]] || { echo "no topic for $name" >&2; exit 1; }
  dest="$content/${topic[$name]}/00. Вложения"
  mkdir -p "$dest"
  [[ -e "$dest/.nomedia" ]] || : > "$dest/.nomedia"
  "$PY" "$here/build_pages.py" "$name" "$dest/${file[$name]}"
done
