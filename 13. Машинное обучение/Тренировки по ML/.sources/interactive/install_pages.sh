#!/usr/bin/env bash
# Build every ready page into the attachments folder of the topic that owns it.
# The topic of each page is listed below.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
content="$(python "$here/../course.py")/content"
declare -A topic=(
  [knn]="01. Основы машинного обучения"
  [nb]="01. Основы машинного обучения"
  [linreg]="02. Линейная регрессия"
  [regularization]="02. Линейная регрессия"
  [polyfit]="02. Линейная регрессия"
  [gd]="02. Линейная регрессия"
  [logreg]="03. Линейная классификация"
  [margin]="03. Линейная классификация"
  [multiclass]="03. Линейная классификация"
  [roc]="03. Линейная классификация"
  [tree]="04. Решающие деревья"
  [entropy]="04. Решающие деревья"
  [boosting]="05. Ансамбли и смещение–разброс"
  [adaboost]="05. Ансамбли и смещение–разброс"
  [bagging]="05. Ансамбли и смещение–разброс"
  [forest]="05. Ансамбли и смещение–разброс"
  [bias-variance]="05. Ансамбли и смещение–разброс"
  [importance]="07. Интерпретация моделей"
  [lime]="07. Интерпретация моделей"
  [shap]="07. Интерпретация моделей"
  [mlp]="06. Нейронные сети"
  [optimizers]="06. Нейронные сети"
  [softmax]="08. Дистилляция и итоги"
  [distill]="08. Дистилляция и итоги"
)
for page in "$here"/pages/*.html; do
  name=$(basename "$page" .html)
  [[ -n ${topic[$name]:-} ]] || { echo "no topic for $name" >&2; exit 1; }
  python "$here/build_pages.py" "$name" "$content/${topic[$name]}/00. Вложения/$name-песочница.html"
done
