#!/usr/bin/env bash
# Build every ready page into the attachments folder of the topic that owns it.
# The topic and the file name of each page are listed below. PY is a Python with fonttools and brotli.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/.cache/discrete-math-digitization/.venv/bin/python}
content="$("$PY" "$here/../course.py")/content"
declare -A topic=(
  [waveguides]="06. Волноводы"
)
declare -A file=(
  [waveguides]="волноводы-песочница.html"
)
for page in "$here"/pages/*.html; do
  name=$(basename "$page" .html)
  [[ -n ${topic[$name]:-} ]] || { echo "no topic for $name" >&2; exit 1; }
  dest="$content/${topic[$name]}/00. Вложения"
  mkdir -p "$dest"
  [[ -e "$dest/.nomedia" ]] || : > "$dest/.nomedia"
  "$PY" "$here/build_pages.py" "$name" "$dest/${file[$name]}"
done
