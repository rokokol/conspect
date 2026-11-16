#!/usr/bin/env bash
# Build every ready page into the attachments folder of the topic that owns it.
# The topic of each page is listed below. PY is a Python with fonttools and brotli.
# A page inlines numkit and sandbox_kit from the vault, so run this script again after a change there.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/.cache/discrete-math-digitization/.venv/bin/python}
content="$("$PY" "$here/../course.py")/content"
declare -A topic=(
  [matrix2]="11. Строение линейного оператора"
  [fredholm-solver]="16. Теория Фредгольма"
  [fredholm-numbers]="16. Теория Фредгольма"
  [svd]="12. Операторы в евклидовом пространстве"
  [pca]="12. Операторы в евклидовом пространстве"
)
for page in "$here"/pages/*.html; do
  name=$(basename "$page" .html)
  [[ -n ${topic[$name]:-} ]] || { echo "no topic for $name" >&2; exit 1; }
  dest="$content/${topic[$name]}/00. Вложения"
  mkdir -p "$dest"
  [[ -e "$dest/.nomedia" ]] || : > "$dest/.nomedia"
  "$PY" "$here/build_pages.py" "$name" "$dest/$name-песочница.html"
done
