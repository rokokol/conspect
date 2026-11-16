#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Подсказчик по стандарту conspect: показывает места, на которые стоит посмотреть.

Не гейт. Каждая подсказка называет пункт стандарта, из которого выросла, и делится
на два уровня: достоверное и "посмотри глазами". Файлы правит только флаг --fix;
что он исправляет — references/lint-fix.md.
Тип заметки объявляется таблицей PRESET_TABLE ниже или полем `preset:` во frontmatter.

    python3 lint.py                        # весь волт
    python3 lint.py "01. Математический анализ"
    python3 lint.py --only quotes,trailing-period --limit 40
    python3 lint.py --fix                  # механические правки, см. references/lint-fix.md
    python3 lint.py --vault ~/myWiki "03. Записки/01. Дневник/01. Daily/2026-05-17 Sunday.md"
"""
import argparse
import collections
import difflib
import fnmatch
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

# Волт, в котором живёт сам скилл: волт конспектов. Заметки личного волта
# разбираются по --vault или по первому пути вне этого корня (см. main)
DEFAULT_VAULT = pathlib.Path(__file__).resolve().parents[4]
VAULT = DEFAULT_VAULT
SKILL = "SKILL.md"

def obsidian_hidden(p):
    """Obsidian не индексирует папку и файл с точкой в начале имени (.git, .trash, .obsidian,
    .agents, .sources курса…), значит это не заметка и не вложение. Считаем от корня волта"""
    return any(part.startswith(".") for part in p.relative_to(VAULT).parts)

# ── таблица "путь → пресет"────────────────────────────────────────────────
# Тип объявляется, а не угадывается по содержимому (declare-dont-guess).
# Первое совпадение выигрывает; путь — от корня волта, glob по fnmatch.
# Переопределить для одной заметки можно полем `preset:` во frontmatter.
#
# Один инструмент разбирает два волта, и записи обоих лежат в одной таблице.
# Пресеты курсов — от корня волта конспектов (папка курса = `NN. <Курс>`),
# остальные — от корня личного волта; какая запись сработает, решает тот волт,
# который назван аргументом. Порядок держит шаблон курса последним: `NN. `
# подходит любой папке с номером в начале имени, поэтому `00. Термины`, `01. Data`
# и прочие именованные папки обоих волтов стоят выше него, а вложения — выше всех.
PRESET_TABLE = [
    ("AGENTS.md",                          None),             # правила волта, не заметка
    ("README.md",                          None),             # описание репозитория
    ("index.md",                           None),             # карта волта
    ("*/00. Вложения/*",                    None),             # вложения — не заметки
    ("00. Вложения/*",                      None),
    ("00. Термины/*",                       "term"),           # сквозные термины и аббревиатуры
    ("Статьи/*",                            "paper"),          # конспекты статей
    ("Книги/*",                             None),             # учебники, не заметки
    ("Scripts/*",                           None),             # генераторы рисунков и песочниц
    ("Templates/*",                         None),             # шаблоны заметок
    ("01. Data/*",                          None),             # служебка
    ("02. Zettelkasten/*",                  "zettel"),
    ("03. Записки/01. Дневник/01. Daily/*", "diary"),
    ("03. Записки/01. Дневник/*",           "diary-periodic"),
    ("03. Записки/02. Ядра/01. Люди/*",     "hub-person"),
    ("03. Записки/02. Ядра/03. События/*",  "hub-event"),
    ("03. Записки/02. Ядра/02. Проекты/*",  "hub-project"),    # уточняется ниже
    ("04. Книжная полка/*",                 None),             # учебники, не заметки
    ("[0-9][0-9]. *— MOC.md",               "lecture-moc"),
    ("[0-9][0-9]. *",                       "lecture"),
]

# Поля frontmatter: что обязательно, что допустимо. Источник — references/frontmatter.md
# и пресеты; здесь только имена, правила заполнения живут там.
# tags не обязателен нигде: заметка без сквозного свойства тегов не носит (SKILL.md → ### Теги)
COMMON_OPTIONAL = {"preset", "aliases", "cssclasses", "publish", "icon", "tags"}
PRESETS = {
    "lecture": {
        "ref": "presets/lecture.md → ## Метаданные",
        # up обязателен только в курсе с MOC — проверяется отдельно в check_note
        "required": ["title", "created", "summary"],
        "optional": {"up", "prev", "next", "lectures", "sources", "media_link", "published", "order"},
    },
    "lecture-moc": {
        "ref": "references/frontmatter.md → ## Тип C — MOC",
        "required": ["title", "created", "summary"],
        "optional": {"up", "prev", "next", "lectures", "sources"},
    },
    "paper": {
        "ref": "presets/paper.md → ## Метаданные",
        "required": ["title", "authors", "year", "created", "summary"],
        "optional": {"doi", "arxiv", "url", "venue", "sources"},
    },
    "zettel": {
        "ref": "presets/zettel.md → ## Метаданные",
        "required": ["created"],
        "optional": {"title", "summary", "up", "source", "sources", "media_link"},
    },
    "term": {
        "ref": "presets/term.md → ## Метаданные",
        "required": ["created"],
        "optional": set(),
    },
    "diary": {
        "ref": "presets/diary.md → ## Метаданные",
        "required": ["created"],
        "optional": {"mark", "sleep hours", "weight", "neighbours", "mood music", "date"},
    },
    "diary-periodic": {
        "ref": "presets/diary.md → ## Периодические заметки",
        "required": ["created"],
        "optional": {"mark", "sleep hours", "weight", "neighbours", "mood music", "date"},
    },
    "hub-person": {
        "ref": "presets/hub.md → ## Ядро — Человек",
        "required": ["created", "aliases"],
        "optional": {"birthday", "tg", "phone", "home", "title", "summary"},
    },
    "hub-project": {
        "ref": "presets/hub.md → ## Ядро — Проект",
        "required": ["created", "aliases"],
        "optional": {"title", "summary", "up"},
    },
    "hub-moc": {
        "ref": "presets/hub.md → ## Ядро-MOC с папкой",
        "required": ["created", "aliases"],
        "optional": {"title", "summary", "up"},
    },
    "hub-event": {
        "ref": "presets/hub.md → ## Ядро — Событие",
        "required": ["created", "aliases"],
        "optional": {"date", "title", "summary"},
    },
    "project-note": {
        "ref": "presets/hub.md → ## Ядро-MOC с папкой",
        "required": ["created", "summary", "up"],
        "optional": {"title", "prev", "next", "sources", "status", "superseded_by"},
    },
}

# Тег, который ставит шаблон плагина Excalidraw: на него правила тегов не распространяются
TAG_EXEMPT = {"excalidraw"}

# Свежесть заметки-факта: единственный статус — "описанное состояние умерло".
# Источник — presets/hub.md → ### Свежесть
STATUS_VALUES = {"superseded"}

# Порядок полей и потолок summary живут в references/frontmatter.md и отсюда только
# читаются: копия в коде однажды уже разошлась с текстом
FRONTMATTER_REF = pathlib.Path(__file__).resolve().parents[1] / "references/frontmatter.md"


def frontmatter_section(title):
    text = FRONTMATTER_REF.read_text(encoding="utf-8")
    m = re.search(rf"^#+ {re.escape(title)}[^\n]*\n(.*?)(?=^#|\Z)", text, re.M | re.S)
    if not m:
        sys.exit(f'lint.py: в references/frontmatter.md нет раздела "{title}"')
    return m.group(1)


# Канонический порядок — ключи первого yaml-блока раздела "Порядок полей"
FIELD_ORDER = re.findall(r"^([a-z_]+):", frontmatter_section("Порядок полей"), re.M)

MOC_PRESETS = {"lecture-moc", "hub-moc"}
HUB_PRESETS = {"hub-person", "hub-project", "hub-event", "hub-moc"}

# Дневник и Inbox пользователь ведёт сам — в общий прогон они не входят.
# Каждый разбирается, только если путь внутри него назван в аргументах явно
DIARY_ROOT = "03. Записки/01. Дневник"
INBOX_ROOT = "02. Zettelkasten/01. Inbox"
EXPLICIT_ONLY = (DIARY_ROOT, INBOX_ROOT)


def under(rel, root):
    return rel == root or rel.startswith(root + "/")


def select_targets(targets, labels):
    """Заметки прогона без папок EXPLICIT_ONLY, которые не названы в labels явно;
    вторым — сколько заметок пропущено в каждой такой папке"""
    asked = {root for root in EXPLICIT_ONLY if any(under(lbl, root) for lbl in labels)}
    kept, skipped = [], collections.Counter()
    for p in targets:
        rel = p.relative_to(VAULT).as_posix()
        root = next((r for r in EXPLICIT_ONLY if under(rel, r)), None)
        if root and root not in asked:
            skipped[root] += 1
        else:
            kept.append(p)
    return kept, skipped

# Потолок summary — верхняя граница "N–M слов" в references/frontmatter.md → ### `summary`
_summary_span = re.search(r"(\d+)–(\d+) слов", frontmatter_section("`summary`"))
if not _summary_span:
    sys.exit('lint.py: в references/frontmatter.md → ### `summary` нет диапазона "N–M слов"')
SUMMARY_MAX_WORDS = int(_summary_span.group(2))

# Потолки абзаца и подписи под рисунком — из SKILL.md → ### Тон и пунктуация
SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
_prose_span = re.search(r"Абзац прозы — не длиннее (\d+) слов, подпись под рисунком — не длиннее (\d+)",
                        (SKILL_DIR / SKILL).read_text(encoding="utf-8"))
if not _prose_span:
    sys.exit('lint.py: в SKILL.md → ### Тон и пунктуация нет правила "Абзац прозы — не длиннее N слов, '
             'подпись под рисунком — не длиннее M"')
PARAGRAPH_MAX_WORDS, CAPTION_MAX_WORDS = int(_prose_span.group(1)), int(_prose_span.group(2))

# Порог, за которым телу ядра проекта пора в свою папку. Считается только для проектов:
# у человека и события папки-альтернативы нет, там длина законна сама по себе.
# 250 взято по волту — из 69 ядер тело длиннее имеют 13, длиннее 250 слов только 6
HUB_BODY_WORDS = 250

# ── каталог проверок ───────────────────────────────────────────────────────
# level: "точно" — машинно достоверное; "?" — подозрение, решает человек.
# ref   — пункт стандарта, из которого выросла подсказка.
CERTAIN, SUSPECT = "точно", "?"
CHECKS = {
    # frontmatter
    "frontmatter-missing":  (CERTAIN, f"{SKILL} → ### Метаданные", "нет YAML-шапки"),
    "yaml-invalid":         (CERTAIN, "references/frontmatter.md → ## Правила заполнения полей",
                             "YAML не парсится — dataview молча теряет поле"),
    "blank-after-frontmatter": (CERTAIN, f"{SKILL} → ### Метаданные",
                             "пустая строка между --- и H1"),
    "eof-newline":          (CERTAIN, "references/lint-fix.md",
                             "файл кончается ровно одним переводом строки"),
    "fm-field-missing":    (CERTAIN, "по пресету заметки", "нет обязательного поля"),
    "fm-field-unexpected":  (SUSPECT, "по пресету заметки", "поле не из шаблона типа"),
    "fm-field-order":       (SUSPECT, "references/frontmatter.md → ## Порядок полей",
                             "поля идут не в каноническом порядке"),
    "fm-host":              (CERTAIN, "references/course-structure.md → ## Связи", "поле host вместо up"),
    "summary-markup":       (CERTAIN, "references/frontmatter.md → ### `summary`",
                             "в properties не рендерится LaTeX и markdown"),
    "summary-lowercase":    (CERTAIN, "references/frontmatter.md → ### `summary`",
                             "summary начинается с заглавной"),
    "summary-trailing-period": (CERTAIN, "references/frontmatter.md → ### `summary`",
                             "точка в конце summary не ставится"),
    "paragraph-long":       (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             f"абзац прозы — не длиннее {PARAGRAPH_MAX_WORDS} слов"),
    "caption-long":         (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             f"подпись под рисунком — не длиннее {CAPTION_MAX_WORDS} слов, детали — в сноску"),
    "sandbox-dup":          (CERTAIN, f"{SKILL} → ### Вложения",
                             "одна HTML-страница — одна строка ▶ на заметку"),
    "summary-long":         (SUSPECT, "references/frontmatter.md → ### `summary`",
                             f"держим коротко, {_summary_span.group(1)}–{SUMMARY_MAX_WORDS} слов"),
    "lectures-unquoted":    (CERTAIN, "references/frontmatter.md → ### `lectures`",
                             "номер, который YAML прочитает числом, булевым, null или списком, — в кавычках"),
    "lectures-inline":      (CERTAIN, "references/frontmatter.md → ### `lectures`",
                             "lectures — YAML-список, не inline"),
    "aliases-empty":        (CERTAIN, "references/frontmatter.md → ### `aliases`",
                             "пустой aliases: [] не пишем"),
    "abbrev-no-alias":      (SUSPECT, f"{SKILL} → ### Тон и пунктуация",
                             "заметка владеет понятием — аббревиатура в её aliases"),
    "abbrev-redecoded":     (SUSPECT, f"{SKILL} → ### Тон и пунктуация",
                             "у расшифровки один владелец, дальше аббревиатура голая"),
    "abbrev-undecoded":     (SUSPECT, f"{SKILL} → ### Тон и пунктуация",
                             "голая аббревиатура: расшифруй у владельца или поставь на него ссылку; "
                             "не аббревиатуры — в tools/not-abbreviations.txt"),
    "alias-collision":      (SUSPECT, f"{SKILL} → ### Связность",
                             "один термин — один владелец — один алиас"),
    "alias-number":         (CERTAIN, f"{SKILL} → ### Связность",
                             "голое число не называет понятие — уточни алиас до значения"),
    "tags-multiword":       (CERTAIN, "references/frontmatter.md → ### `tags`",
                             "тег — строчные буквы, один токен через подчёркивание"),
    "tag-is-alias":         (CERTAIN, f"{SKILL} → ### Теги",
                             "тег стоит только на заметке, которую называет, — это её алиас"),
    "tag-singleton":        (SUSPECT, f"{SKILL} → ### Теги",
                             "тег на одной заметке ничего не объединяет — алиас или ничего"),
    "tag-variant":          (SUSPECT, f"{SKILL} → ### Теги",
                             "два написания одного тега — регистр, ё, -/_ или окончание"),
    "tag-mirrors-moc":      (SUSPECT, f"{SKILL} → ### Теги",
                             "тег повторяет группу sub-MOC — её уже несёт up"),
    "created-format":       (CERTAIN, "references/frontmatter.md → ### `created`",
                             "created: YYYY-MM-DD без кавычек"),
    # свежесть заметок проекта
    "status-value":         (CERTAIN, "presets/hub.md → ### Свежесть",
                             f"status принимает только {', '.join(sorted(STATUS_VALUES))}"),
    "superseded-by-broken": (CERTAIN, "presets/hub.md → ### Свежесть",
                             "superseded_by — wiki-ссылка на существующую заметку"),
    "superseded-by-no-status": (CERTAIN, "presets/hub.md → ### Свежесть",
                             "superseded_by без status: superseded — dataview не увидит замену"),
    # структура тела
    "intro-blockquote":     (SUSPECT, "presets/lecture.md → ## Скелет конспекта",
                             "вступление после H1 отменено 15.06 — суть уезжает в summary; "
                             "содержательная первая строка остаётся законно"),
    "related-tail":         (CERTAIN, f"{SKILL} → ## Что не делаем",
                             "связь несёт инлайн-ссылка на точный якорь, а не перечень в подвале"),
    "moc-prose":            (SUSPECT, "presets/lecture.md → ## MOC — это индекс",
                             "MOC — индекс, а не вводная глава"),
    "hub-longread":         (SUSPECT, "presets/hub.md → ## Ядро-MOC с папкой",
                             "у проекта набралось тело — проверь, не пора ли ему своя папка"),
    "heading-dash":         (SUSPECT, f"{SKILL} → ### Заголовки",
                             "заголовок — чистое название, без хвоста-пересказа"),
    "callout-title-empty":  (SUSPECT, "references/callouts.md → Заголовок как сама мысль",
                             "титул callout несёт мысль, а не пустует"),
    "callout-title-label":  (SUSPECT, "references/callouts.md → ### Заголовок как сама мысль",
                             "мета-ярлык «Следствие — …» вместо самой мысли"),
    "heading-no-timecode":  (SUSPECT, "presets/lecture.md → ## Заголовки",
                             "заметка объявила видео (media_link или ссылка на видеохостинг в sources) — H2 просят таймкод; "
                             "мета-раздел своего синтеза его не получает"),
    "heading-unicode-math": (SUSPECT, f"{SKILL} → ### Заголовки",
                             "формула в заголовке — TeX $...$, не юникод"),
    "headings-flat":        (SUSPECT, f"{SKILL} → ### Заголовки",
                             "длинный плоский список H2 — поищи грани одного понятия и спусти их в H3; "
                             "честно параллельные блоки (аксиомы, независимые свойства) плоскими и остаются"),
    "heading-level-jump":   (SUSPECT, f"{SKILL} → ### Заголовки",
                             "уровень перепрыгнут — H3 пропущен между H2 и H4"),
    "extra-h1":             (CERTAIN, f"{SKILL} → ### Заголовки",
                             "лишний H1 — у заметки один H1-титул; допустимые исключения задаёт раскладка (references/course-structure.md)"),
    "nested-callout-no-blank": (SUSPECT, "references/callouts.md → ## Вложенные callout",
                             "стиль волта: перед вложенным callout — строка-разделитель > "
                             "уровня родителя, ради читаемости исходника; рендер от неё не зависит"),
    "callout-no-blank":     (CERTAIN, "references/callouts.md → ## Вложенные callout",
                             "callout сразу за строкой своего или более глубокого уровня склеен с блоком выше, "
                             "и [!type] рендерится текстом; разделитель — пустая строка уровнем выше"),
    "footnote-far-from-use": (SUSPECT, f"{SKILL} → ### Связность",
                             "сноска [^x]: — в конце своей секции"),
    # типографика
    "quotes":               (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             "прямые \"...\"; ёлочки только внутри уже закавыченного"),
    "trailing-period":      (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             "точки в конце абзаца, пункта и ячейки таблицы не ставим"),
    "slop-phrase":          (SUSPECT, f"{SKILL} → ## Что не делаем",
                             "подводка, оценка или мета-вода о переезде"),
    "provenance-note":      (SUSPECT, f"{SKILL} → ## Что не делаем",
                             "конспект — не отчёт сессии: факт сверяют и ставят источник, "
                             "а не пишут \"по памяти\"; слова лектора — фактом в тексте, "
                             "оговорка — только в сноске, если подтвердить не удалось"),
    "study-process":        (SUSPECT, f"{SKILL} → ## Что не делаем",
                             "экзамены, контрольные и домашние задания — не знание: "
                             "оставь содержание, сними рамку учебного процесса"),
    # ссылки
    "broken-link":          (SUSPECT, f"{SKILL} → ### Связность",
                             "красная ссылка — законный крючок или опечатка"),
    "link-repeat":          (SUSPECT, f"{SKILL} → ### Связность",
                             "в строке одна ссылка на место заметки, повтор — голым словом"),
    "missing-attachment":   (CERTAIN, f"{SKILL} → ### Вложения", "эмбед ведёт в никуда"),
    "anchor-broken":        (CERTAIN, "references/wikilinks.md → Тайм-код заголовка обязательно копируется в якорь",
                             "#Заголовок или #^блок не находится в заметке-цели — ссылка откроет её начало"),
    "moc-sort-lectures":    (CERTAIN, "references/frontmatter.md → ### `lectures`",
                             "номера лекций — строки, SORT lectures ставит \"10\" перед \"9\"; "
                             "сортируй по number(lectures[0])"),
    "bare-self-link":       (CERTAIN, "references/wikilinks.md → ## Формы ссылок",
                             "ссылка на свой раздел — [[Файл#Заголовок|подпись]]"),
    "link-scaffolding":     (SUSPECT, "references/wikilinks.md → ## Формы ссылок",
                             "инлайн-термин вместо обвязки «подробнее в»"),
    "dup-definition":       (SUSPECT, f"{SKILL} → ### Связность",
                             "определением владеет одна заметка, остальные ссылаются"),
    "formula-in-caption":   (CERTAIN, "references/wikilinks.md → ## Формы ссылок",
                             "формулу выносим из подписи ссылки"),
    "table-pipe":           (CERTAIN, f"{SKILL} → ### Таблицы",
                             "| внутри wiki-ссылки в таблице экранируется"),
    "table-modulus":        (SUSPECT, "references/notation.md → ## Жёсткие предпочтения",
                             "модуль |…| в формуле внутри ячейки ломает таблицу"),
    "table-header-blank":   (CERTAIN, f"{SKILL} → ### Таблицы",
                             "пустая ячейка в шапке — первому столбцу нужно имя"),
    "table-header-case":    (SUSPECT, f"{SKILL} → ### Таблицы",
                             "заголовок столбца с заглавной; строчными — только имена команд и полей"),
    "anchor-unused":        (SUSPECT, "references/wikilinks.md → ## Блок-якоря",
                             "якорь оправдан входящей ссылкой"),
    "up-broken":            (CERTAIN, "references/course-structure.md → ## Связи",
                             "up ведёт в несуществующую заметку"),
    "chain-broken":         (CERTAIN, "references/course-structure.md → ## Связи",
                             "цепь prev/next читается в обе стороны"),
    # математика и код
    "math-spaces":          (CERTAIN, "references/math.md → ## Базовое",
                             "пробел вплотную к $ ломает рендер"),
    "latex-ru-macro":       (CERTAIN, "references/notation.md → ## Жёсткие предпочтения",
                             "\\tan/\\arctan вместо русских макросов"),
    "inline-code-equals":   (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             "инлайн-код с = в начале Dataview считает за запрос"),
    # волт целиком
    "iconic-dangling":      (CERTAIN, f"{SKILL} → ### Иконки файлов и папок",
                             "ключ iconic указывает на несуществующий путь"),
    # рисунки и песочницы — только с --figures и --pages, обход в media.py
    "figure-dotted-number": (CERTAIN, "references/math.md → ### Заголовок и текст на графике",
                             "число подписи — через num(), десятичная запятая; не десятичная точка — keep_dots()"),
    "figure-failed":        (CERTAIN, "references/math.md → ### После генерации",
                             "скрипт рисунка не отработал — рисунок не проверен"),
    "page-error":           (CERTAIN, f"{SKILL} → ### Вложения",
                             "ошибка в консоли страницы, или проверка страницы не отработала"),
    "page-scroll":          (CERTAIN, f"{SKILL} → ### Вложения",
                             "на ширине телефона страница прокручивается вбок"),
    "page-paragraph-long":  (CERTAIN, f"{SKILL} → ### Тон и пунктуация",
                             f"абзац страницы — не длиннее {PARAGRAPH_MAX_WORDS} слов"),
    "page-dotted-number":   (CERTAIN, f"{SKILL} → ### Вложения",
                             "число на странице — через toComma или formatNumber; не десятичная точка — data-keep-dots"),
}

# Что машина не увидит в принципе — печатается в сводке
BY_EYE = [
    ("плотность текста: вода, подводки, оценки", f"{SKILL} → ## Что не делаем"),
    ("правда ли H2 — грани одного понятия (машина видит только плоскую длину списка)",
     f"{SKILL} → ### Заголовки"),
    ("роли callout: теорема, доказательство, без доказательства",
     "references/theorem-proof-patterns.md"),
    ("лид под H1 не дублирует summary и первый раздел",
     "presets/lecture.md → ## Скелет конспекта"),
    ("границы заметки: укрупняй, не дроби", f"{SKILL} → ### Границы заметки"),
    ("ссылка ведёт на владельца термина, а не на соседа", f"{SKILL} → ### Связность"),
    ("нотация LaTeX по справочнику", "references/notation.md"),
    ("длинный список просится в таблицу", f"{SKILL} → ## Что не делаем"),
    ("summary правда описывает заметку", "references/frontmatter.md → ### `summary`"),
    ("сгенерированные картинки посмотреть глазами", "references/math.md → ### После генерации"),
    ("внешние ссылки живы", "references/wikilinks.md → ## Внешние ссылки"),
]

SLOP = [
    r"теперь перейдём", r"прежде чем (?:двигаться|перейти|идти)",
    r"перейдём к (?:доказательству|рассмотрению|обсуждению|следующ)",
    r"рассмотрим важн", r"заметим интересн", r"полезно разобраться",
    r"это изящн", r"красивый результат", r"удобство в том", r"прелесть в том",
    r"(?:грязь|сложность|структура|материал|содержание|суть|логика|смысл)\w*\b[^.]{0,30}"
    r"\b(?:переехал|перекочевал|переселил|уехал)",
]
RE_SLOP = re.compile("|".join(SLOP), re.I)

# Пометка о происхождении текста: след отчёта сессии, а не содержание (SKILL.md → ## Что не делаем)
PROVENANCE = [
    r"по памяти", r"по воспоминани", r"не сверен", r"без сверки", r"сверяется по", r"не перепровер",
    r"не подтвержд[её]н\w*\s+(?:лекци|источник)", r"(?:лекци|источник)\w*\s+не подтвержд",
    r"не удалось (?:провер|свер|найти источник)", r"источник не найден",
    r"требует проверки", r"нуждается в проверке", r"оцифровк",
    r"(?:провер|свер)\w+ (?:независимо )?(?:кодом|скриптом|программно|тестом|прямым моделированием)",
]
RE_PROVENANCE = re.compile("|".join(PROVENANCE), re.I)

# Учебный процесс в конспекте: экзамены, билеты, контрольные, домашние задания (SKILL.md → ## Что не делаем)
STUDY_PROCESS = [
    r"экзамен", r"\bзач[её]т", r"\bбилет", r"домашн\w* задани", r"домашк", r"\bна дом\b",
    r"контрольн\w* работ", r"\bна контрольн", r"самостоятельн\w* работ", r"коллоквиум",
    r"консультаци\w* перед", r"\bбалл(?:а|ов|ы|ом|ами)?\b",
    r"\bна упражнени", r"упражнениям\b", r"\bна семинар",
    r"\bна (?:следующ|прошл)\w+ (?:лекци|урок|заняти|пар[еуы])", r"\bв следующий раз",
]
RE_STUDY_PROCESS = re.compile("|".join(STUDY_PROCESS), re.I)

# Мета-ярлык в титуле callout: "Следствие — …", "Рецепт «…»" (references/callouts.md → Заголовок как сама мысль)
META_LABEL = (r"(?:Пример(?:ы)?|Контрпример|Следствие|Замечание|Упражнение|Мотивировка|Лемма"
              r"|Теорема|Рецепт|Трюк|Приём|Ключ|Смысл|Почему|Идея|Вывод|Итог|Суть|Пояснение"
              r"|Критерий|Осторожно|Достаточность|Необходимость|Определение|Доказательство"
              r"|Задача|Наблюдение|Аналогия|Интуиция|Тонкость|Отрицание)")
RE_LABEL_TAIL = re.compile(rf"^{META_LABEL}\b[^—(]{{0,40}}—\s")
RE_LABEL_QUOTED = re.compile(rf'^{META_LABEL}\b[^"]{{0,20}}"[^"]+"')


def is_meta_label(title):
    """Ярлык перед тире или перед именем в кавычках. Связка "X — это Y" — определение
    или факт, а не ярлык: так же её пропускает heading-dash (SKILL.md → ### Заголовки)"""
    m = RE_LABEL_TAIL.match(title)
    if m and not re.match(r"это\b", title[m.end():]):
        return True
    return bool(RE_LABEL_QUOTED.match(title))

RE_WIKILINK = re.compile(r"\[\[([^\]\[]+)\]\]")
RE_EMBED = re.compile(r"!\[\[([^\]\[]+)\]\]")
# Голый скаляр, который YAML 1.2 (его читает Obsidian) берёт не строкой: число теряет
# нули ("12.10" → 12.1), "-" становится вложенным списком. Остальное — уже строка
RE_YAML_NOT_STRING = re.compile(
    r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|0o[0-7]+|0x[0-9a-fA-F]+"
    r"|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN)"
    r"|true|True|TRUE|false|False|FALSE|null|Null|NULL|~|-|")
RE_CALLOUT = re.compile(r"^\s*>[\s>]*\[!\w+\][+-]?(.*)$")
# ссылка sources на видеохостинг: только ролик просит таймкод в H2, блокнот или статья — нет
RE_VIDEO_SOURCE = re.compile(
    r"\]\(https?://(?:[\w-]+\.)*(?:youtube\.com|youtu\.be|youtube-nocookie\.com|vimeo\.com|rutube\.ru|vkvideo\.ru)[/:?#)]")
RE_DEF = re.compile(r"\*\*([^*]{2,60})\*\*\s*(?:\([^)]{0,80}\)\s*)?[—–-]\s+(?!\*\*)(?=[^—\n]{25,})")


def iter_line_definitions(ln):
    """Термины вида «**Термин** — 25+ символов» где угодно в строке — не только
    в начале пункта. Позиция в строке не фильтруется намеренно: находка уровня
    ПОСМОТРИ дешевле пропустить нельзя, чем один лишний взгляд человека на
    ложное совпадение вроде «**нет** — потому что...» посреди предложения"""
    for m in RE_DEF.finditer(ln):
        yield m.group(1)
RE_SCAFFOLD = re.compile(
    r"(подробнее|подробности|детальнее|см\.|как (?:мы )?разбирал|напомн|посвящена"
    r"|рассказано|описано|речь ид)[^.]{0,40}\[\[", re.I)
UNICODE_MATH = set("≤≥≠≈∞∈∉⊂⊃∑∏∫√±×÷∂∇ℝℕℤℚℂ")
ATTACHMENT_EXT = re.compile(
    r"\.(?:png|jpe?g|gif|svg|webp|avif|pdf|mp3|m4a|wav|ogg|mp4|webm|mov|canvas|base)$", re.I)


class Finding:
    __slots__ = ("code", "rel", "line", "msg")

    def __init__(self, code, rel, line, msg):
        self.code, self.rel, self.line, self.msg = code, rel, line, msg


# ── чтение frontmatter ─────────────────────────────────────────────────────
def split_frontmatter(text):
    """-> (fm_text, номер строки начала тела, есть ли пустая строка после ---)."""
    if not text.startswith("---\n"):
        return None, 0, False
    end = text.find("\n---", 4)
    if end < 0:
        return "", 0, False
    fm = text[4:end]
    body_line = text[:end].count("\n") + 2
    return fm, body_line, text[end + 4:].startswith("\n\n")


def raw_keys(fm):
    """Имена полей в порядке появления — работает и на невалидном YAML."""
    return [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w \-]*):", fm, re.M)]


def parse_fm(fm):
    """-> (dict полей, текст ошибки YAML или None)."""
    if yaml is None:
        return regex_fm(fm), None
    try:
        data = yaml.safe_load(fm)
    except Exception as e:
        return regex_fm(fm), str(e).split("\n")[0]
    if not isinstance(data, dict):
        return regex_fm(fm), None
    return data, None


def regex_fm(fm):
    """Запасной разбор: скаляры и простые списки, без валидации."""
    out, key = {}, None
    for ln in fm.split("\n"):
        m = re.match(r"^([A-Za-z_][\w \-]*):\s*(.*)$", ln)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = val.strip('"') if val else []
        elif key is not None and re.match(r"^\s+- ", ln):
            if not isinstance(out.get(key), list):
                out[key] = []
            out[key].append(ln.split("- ", 1)[1].strip().strip('"'))
    return out


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def strip_markup(s):
    """Снять формулы и markdown-ссылки: в заголовке они законны, разбирается остальное."""
    s = re.sub(r"\$[^$]*\$", "", s)
    return re.sub(r"\[[^\]]*\]\([^)]*\)", "", s)


RE_SENTENCE_DOT = re.compile(r"(?<![.\d])\.$")
RE_ABBR_END = re.compile(r"\b(и т\.д|и т\.п|см|напр)\.$")


def ends_with_period(s):
    """Точка в конце как пунктуация — не хвост сокращения ("и т.д.") и не номер версии."""
    s = s.rstrip()
    return bool(RE_SENTENCE_DOT.search(s)) and not RE_ABBR_END.search(s)


def strip_code_spans(s):
    """Снять `инлайн-код`: внутри него Obsidian не резолвит ни ссылку, ни эмбед, ни формулу."""
    return re.sub(r"`[^`\n]*`", "", s)


def unescape_pipe(raw):
    """В ячейке таблицы пайп подписи экранируют ([[Файл#^a\\|подпись]]) — разделитель тот же."""
    return raw.replace("\\|", "|")


def link_target(raw):
    """[[Файл#Якорь|подпись]] -> имя файла."""
    return unescape_pipe(raw).split("|")[0].split("#")[0].strip()


# ── резолв пресета ─────────────────────────────────────────────────────────
def resolve_preset(rel, declared):
    if declared:
        return declared, "объявлен полем preset:"
    for pattern, preset in PRESET_TABLE:
        if fnmatch.fnmatch(rel, pattern):
            if preset == "hub-project":
                return hub_flavour(rel), "таблица путей"
            return preset, "таблица путей"
    return None, "нет правила"


def hub_flavour(rel):
    """Ядро проекта: тонкое, MOC внутри одноимённой папки, или заметка такой папки."""
    p = pathlib.PurePosixPath(rel)
    root = pathlib.PurePosixPath("03. Записки/02. Ядра/02. Проекты")
    parts = p.relative_to(root).parts
    if len(parts) == 1:
        return "hub-project"                                   # тонкое ядро в корне
    hub = root / parts[0] / (parts[0] + ".md")
    if (VAULT / str(hub)).exists():
        return "hub-moc" if p == hub else "project-note"       # папка ядра-MOC
    return "hub-project"                                       # просто категорийная папка


def course_has_moc(rel):
    """Курс, в котором лежит заметка, завёл super-MOC f00 — значит, up есть куда вести."""
    parts = pathlib.PurePosixPath(rel).parts
    return len(parts) > 2 and any((VAULT / parts[0] / parts[1]).glob("f00*.md"))


# ── индекс волта ───────────────────────────────────────────────────────────
class Index:
    def __init__(self):
        self.notes = {}          # stem -> path
        self.files = collections.defaultdict(list)  # имя файла с расширением (lower) -> все такие файлы, .md тоже
        self.aliases = {}        # alias (lower) -> [rel, ...]
        self.alias_forms = collections.defaultdict(set)  # alias (lower) -> написания в волте
        self.collisions = collections.defaultdict(list)  # rel -> [(alias, чужие rel), ...]
        self.definitions = collections.defaultdict(list)  # норм. термин -> [stem, ... кто его правда **жирным** определяет]
        self.anchor_refs = set() # (путь заметки-цели, id якоря в нижнем регистре)
        self.presets = {}        # rel -> preset
        self.names = collections.defaultdict(set)      # norm_tag(имя или алиас) -> rel
        self.tag_notes = collections.defaultdict(set)  # тег -> rel всех заметок, включая дневник
        self.tag_names = {}      # rel -> теги заметки
        self.groups = {}         # rel sub-MOC -> {он сам и заметки, чей up ведёт на него}
        self.variants = {}       # тег -> другие теги волта с тем же tag_variant_key
        self.decodings = collections.defaultdict(dict)  # аббревиатура (lower) -> {rel: [расшифровки]}
        self.owned = collections.defaultdict(set)  # аббревиатура (lower) -> rel, чья расшифровка — владение
        self.words = Lexicon()   # русские слова тел всех заметок, включая дневник

    def build(self):
        md = []
        for p in VAULT.rglob("*"):
            if p.is_dir() or obsidian_hidden(p):
                continue
            self.files[p.name.lower()].append(p)
            if p.suffix == ".md":
                self.notes.setdefault(p.stem, p)
                md.append(p)

        ups = []                 # (rel, имя заметки в up)
        for p in sorted(md):
            stem = p.stem
            rel = p.relative_to(VAULT).as_posix()
            text = read(p)
            fm, body_line, _ = split_frontmatter(text)
            data = parse_fm(fm)[0] if fm else {}
            preset = resolve_preset(rel, str(data.get("preset")) if data.get("preset") else None)[0]
            self.presets[rel] = preset
            # имя заметки — тоже "алиас": коллизия имени с чужим алиасом такой же сигнал
            self.aliases.setdefault(stem.lower(), []).append(rel)
            self.alias_forms[stem.lower()].add(stem)
            self.names[norm_tag(stem)].add(rel)
            for a in as_list(data.get("aliases")):
                a = str(a).strip()
                if a:
                    self.aliases.setdefault(a.lower(), []).append(rel)
                    self.alias_forms[a.lower()].add(a)
                    self.names[norm_tag(a)].add(rel)
            self.tag_names[rel] = note_tags(data)
            for t in self.tag_names[rel]:
                self.tag_notes[t].add(rel)
            up = nav_field(fm or "", "up")
            if up:
                ups.append((rel, up))
            self.words.add("\n".join(text.split("\n")[body_line:]))
            if not rel.startswith(DIARY_ROOT):
                lines = text.split("\n")
                names = note_names(stem, data, lines, body_line)
                for abbr, at in abbrev_decodings(lines, body_line).items():
                    self.decodings[abbr.lower()][rel] = [e for _, e in at]
                    if owns_decoding(names, preset, lines, abbr, at):
                        self.owned[abbr.lower()].add(rel)
            # владение термином решает не список алиасов, а то, что заметка его правда
            # определяет — **жирным** через тире; иначе первый по алфавиту случайный
            # держатель алиаса молча стал бы "владельцем", которым никогда не был
            if preset and preset not in MOC_PRESETS:
                for line in text.split("\n"):
                    for term in iter_line_definitions(line):
                        k = norm_term(term)
                        if len(k) >= 3:
                            self.definitions[k].append(stem)
        # омонимы среди них отсеивает check_note: homonyms нужен полный self.words
        for alias, owners in self.aliases.items():
            uniq = list(dict.fromkeys(owners))
            if len(uniq) > 1:
                for rel in uniq:
                    self.collisions[rel].append((alias, [o for o in uniq if o != rel]))

        for rel, up in ups:
            for target in self.link_dests(up, VAULT / rel):
                if target.suffix == ".md":
                    moc = target.relative_to(VAULT).as_posix()
                    self.groups.setdefault(moc, {moc}).add(rel)

        by_key = collections.defaultdict(set)
        for t in self.tag_notes:
            if t not in TAG_EXEMPT:
                by_key[tag_variant_key(t)].add(t)
        for same in by_key.values():
            for t in same:
                if len(same) > 1:
                    self.variants[t] = sorted(same - {t})

        # ссылка на блок резолвится как любая ссылка, а id блока сверяется без учёта регистра —
        # так же, как его ищет resolves для anchor-broken
        for p in md:
            for _, ln in iter_prose(read(p).split("\n")):
                for raw in RE_WIKILINK_FULL.findall(ln):
                    link = unescape_pipe(raw).split("|")[0]
                    if "#^" not in link:
                        continue
                    linkpath, anchor = link.split("#^", 1)
                    linkpath = linkpath.strip()
                    for dest in self.link_dests(linkpath, p) if linkpath else [p]:
                        self.anchor_refs.add((dest, anchor.strip().lower()))

    def homonyms(self, alias, a, b):
        """Общий алиас двух заметок — омоним, если он аббревиатура, каждая заметка сама
        его расшифровывает и ни одна её расшифровка не делит слова с расшифровками другой"""
        dec = self.decodings.get(alias.lower(), {})
        if a not in dec or b not in dec or not self.abbreviation_alias(alias):
            return False
        return all(unrelated(x, y) for x in dec[a] for y in dec[b])

    def abbreviation_alias(self, alias):
        """Алиас — аббревиатура, если каждое его написание в волте ею выглядит (пара CI/CD
        тоже) и ни одна часть не отсеяна по форме. Строчное "пк" рядом с "ПК" — уже слово.
        Словарь not-abbreviations.txt здесь не действует, и подключать его не надо. Он
        отвечает, нужна ли расшифровка в прозе, а не аббревиатура ли токен. Повтор алиаса
        без расшифровки у обеих заметок и так коллизия, поэтому словарь не добавил бы ни
        одной находки, а отнял бы законный омоним: CS — Carrier Sense и Chip Select"""
        return all(re.fullmatch(ABBR_PAIR, f)
                   and not any(not_abbreviation_by_form(p, Lexicon(), self.words) for p in f.split("/"))
                   for f in self.alias_forms[alias])

    def abbr_owners(self, abbr):
        """Заметки, которые аббревиатурой владеют: держат её алиасом или именем либо
        расшифровывают по признаку владения (owns_decoding). Расшифровка мимоходом — нет"""
        k = abbr.lower()
        return set(self.aliases.get(k, [])) | self.owned.get(k, set())

    def known(self, name, source=None):
        """Ведёт ли [[name]] в файл. Алиас ссылку не разрешает: getFirstLinkpathDest
        Obsidian ищет только по имени файла, а алиас кормит поиск и подсказку [[,
        которая сама пишет [[Файл|алиас]]"""
        return bool(self.link_dests(name, source))

    def link_dests(self, linkpath, source=None):
        """Файлы волта, в которые может вести [[путь]] из заметки source, по правилам
        getLinkpathDest из app.js Obsidian. Имя с точкой в последней части сперва ищется
        как файл с любым расширением (картинка, pdf, html, сама заметка "x.md"), не нашлось —
        как заметка с приписанным ".md". Регистр не важен. Папка в ссылке сужает выбор:
        сперва полный путь от корня, "./" и "../" — от папки source, иначе любой путь
        с таким хвостом. Одноимённых файлов бывает несколько, поэтому список"""
        n = linkpath.lower()
        cands = self.files.get(n.rsplit("/", 1)[-1]) if "." in n.rsplit("/", 1)[-1] else None
        if not cands:
            n += ".md"
            cands = self.files.get(n.rsplit("/", 1)[-1])
        if not cands:
            return []
        if "/" not in n:
            return list(cands)
        rel = {p: p.relative_to(VAULT).as_posix().lower() for p in cands}
        folder = source.parent.relative_to(VAULT).as_posix().lower() if source else ""
        folder = "" if folder == "." else folder
        if n.startswith(("./", "../")):
            if n.startswith("./../"):
                n = n[2:]
            if n.startswith("./"):
                n = (folder + "/" if folder else "") + n[2:]
            else:
                while n.startswith("../"):
                    n, folder = n[3:], folder.rsplit("/", 1)[0] if "/" in folder else ""
                n = (folder + "/" if folder else "") + n
        n = n.removeprefix("/")
        exact = [p for p in cands if rel[p] == n]
        if exact:
            return exact
        if linkpath.startswith("/"):
            return []
        return [p for p in cands if rel[p].endswith(n)]


_cache = {}


def read(p):
    key = str(p)
    if key not in _cache:
        try:
            _cache[key] = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            _cache[key] = ""
    return _cache[key]


def fix_eof(text):
    """Конец файла по PEP8 (W391, W292): ровно один перевод строки, без пустых строк
    после последней непустой. Хвостовые пробелы самой последней строки не трогаем;
    пустой файл возвращается как есть."""
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return text
    body = "\n".join(lines)
    return (body[:-1] if eol == "\r\n" and body.endswith("\r") else body) + eol


# Что умеет --fix: код находки → функция text -> text. --list-checks помечает эти коды
# сам, так что новая автоправка — одна запись здесь
FIXERS = {"eof-newline": fix_eof}


# ── база известных находок ─────────────────────────────────────────────────
# По умолчанию печатается только новое относительно базы; --accept записывает находки
# охвата как известные, --all показывает всё. База лежит рядом с инструментом: Syncthing
# несёт её на все машины вместе с волтом, а в git она не идёт (.gitignore волта). Пути в ней
# относительные, так что волт можно переносить. Сама база не обновляется: иначе
# неисправленная новая находка пропала бы со второго прогона
BASELINE = pathlib.Path(__file__).resolve().parent / "baseline.json"


def baseline_key(f):
    # номер строки в тексте находки не делает её новой: правка выше по файлу его сдвигает
    return f.code, re.sub(r"строк[аеиу] \d+", "строке N", f.msg)


def load_baseline():
    try:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data.get("notes")


def split_by_baseline(findings, base, scope, active):
    """(новые, скрыто известных, исправлено с записи базы, база есть)."""
    if base is None:
        return findings, 0, 0, False
    left = {rel: collections.Counter(tuple(e) for e in base.get(rel, [])) for rel in scope}
    shown, hidden = [], 0
    for f in findings:
        known, key = left.setdefault(f.rel, collections.Counter()), baseline_key(f)
        if known[key] > 0:
            known[key] -= 1
            hidden += 1
        else:
            shown.append(f)
    resolved = sum(n for known in left.values() for (code, _), n in known.items()
                   if code in active and n > 0)
    return shown, hidden, resolved, True


def save_baseline(findings, scope, active):
    notes = load_baseline() or {}
    fresh = collections.defaultdict(list)
    for f in findings:
        fresh[f.rel].append(list(baseline_key(f)))
    for rel in scope:
        # под --only/--skip принимаются только активные коды, записи остальных остаются
        entries = [e for e in notes.get(rel, []) if e[0] not in active] + fresh.get(rel, [])
        if entries:
            notes[rel] = entries
        else:
            notes.pop(rel, None)
    # удалённая заметка в охват не попадёт уже никогда, поэтому её запись снимается при любом
    # охвате, а не только своём — иначе она висела бы вечно. База одна на два волта, поэтому
    # запись чужого волта в этом не найдётся никогда: снимается только та, чья папка здесь есть
    for rel in [rel for rel in notes
                if not (VAULT / rel).exists() and (VAULT / rel).parent.is_dir()]:
        del notes[rel]
    # код, снятый из каталога, активным не станет — его записи тоже висели бы вечно
    for rel in list(notes):
        notes[rel] = [e for e in notes[rel] if e[0] in CHECKS]
        if not notes[rel]:
            del notes[rel]
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    tmp = BASELINE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"notes": notes}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    tmp.replace(BASELINE)
    return sum(len(v) for v in fresh.values()), len(fresh)


def norm_term(s):
    return re.sub(r"[^0-9a-zа-яё/]+", " ", s.lower()).strip()


def note_tags(data):
    """Теги frontmatter без ведущего #: "#y2025" и y2025 Obsidian считает одним тегом"""
    return [t for t in (str(x).strip().lstrip("#") for x in as_list(data.get("tags"))) if t]


def norm_tag(s):
    """Тег, имя файла и алиас в одном виде: регистр, ё и разделители _ - пробел не различаются"""
    s = str(s).lower().replace("ё", "е")
    return re.sub(r"[\s_-]+", " ", s).strip()


# Окончания, которыми расходятся формы одного слова: "предел/пределы", "функция/функции"
RE_TAG_ENDING = re.compile(r"(?:ами|ями|ов|ев|ей|ой|ий|ый|ая|ое|ые|ие|ых|их|ам|ям|ах|ях|es|s"
                           r"|а|я|ы|и|о|е|у|ю|ь|й)$")


def tag_variant_key(tag):
    """Ключ, по которому два написания одного тега совпадают: norm_tag и основа каждого слова"""
    words = []
    for w in norm_tag(tag).split():
        stem = RE_TAG_ENDING.sub("", w) if len(w) >= 4 else w
        words.append(stem if len(stem) >= 3 else w)
    return " ".join(words)


def tag_mirror(tagged, group, moc):
    """Совпадает ли набор заметок с тегом с группой sub-MOC: вся группа, группа без одной
    заметки или сам MOC с одной заметкой"""
    if not tagged <= group:
        return False
    if tagged == group:
        return True
    if len(group) >= 3 and len(tagged) >= 2 and len(group - tagged) == 1:
        return True
    return moc in tagged and len(tagged) <= 2


# ── проверка одной заметки ─────────────────────────────────────────────────
def check_note(path, idx, out):
    rel = path.relative_to(VAULT).as_posix()
    text = read(path)
    lines = text.split("\n")

    def add(code, line, msg):
        out.append(Finding(code, rel, line, msg))

    fm, body_line, blank = split_frontmatter(text)
    fm_text = fm or ""
    data, yaml_err = (parse_fm(fm_text) if fm_text else ({}, None))
    keys = raw_keys(fm_text)

    # словарь FSRS Vocabulary объявляет себя свойством fsrs-vocabulary; его форма —
    # забота скилла fsrs-vocabulary, а не стандарта конспектов
    if "fsrs-vocabulary" in keys and not data.get("preset"):
        return None

    # тип объявляется до всех проверок: не объявлен — заметку не трогаем
    preset = resolve_preset(rel, str(data.get("preset")) if data.get("preset") else None)[0]
    if preset is None:
        return None
    spec = PRESETS.get(preset)

    if fm is None:
        add("frontmatter-missing", 1, "нет YAML-шапки")
    else:
        if yaml_err:
            add("yaml-invalid", 1, yaml_err[:110])
        if blank:
            add("blank-after-frontmatter", body_line, "пустая строка между --- и H1")
    if text.strip() and fix_eof(text) != text:
        add("eof-newline", len(lines), "лишние пустые строки в конце" if text.endswith("\n")
            else "нет перевода строки в конце")

    # ── frontmatter против пресета ─────────────────────────────────────────
    if spec:
        for field in spec["required"]:
            if field not in keys:
                add("fm-field-missing", 1, f"нет поля {field} ({preset}: {spec['ref']})")
        # отдельной теме вне курса up вести некуда — обязателен он только в курсе с MOC
        if preset == "lecture" and "up" not in keys and course_has_moc(rel):
            add("fm-field-missing", 1, "нет поля up (lecture: references/course-structure.md → ## Связи)")
        allowed = set(spec["required"]) | spec["optional"] | COMMON_OPTIONAL
        for field in keys:
            if field not in allowed:
                add("fm-field-unexpected", 1, f"{field} — не из шаблона {preset}")
        # порядок полей объявлен только для лекционных шапок
        if preset in ("lecture", "lecture-moc"):
            ordered = [k for k in keys if k in FIELD_ORDER]
            if ordered != sorted(ordered, key=FIELD_ORDER.index):
                add("fm-field-order", 1, " · ".join(ordered))

    if "host" in keys:
        add("fm-host", 1, "host вместо up")

    summary = data.get("summary")
    if isinstance(summary, str) and summary.strip():
        s = summary.strip()
        if any(t in s for t in ("$", "**", "[[", "`")):
            add("summary-markup", 1, s[:60])
        if s[0].islower() and not re.match(r"^[a-z_]+[ (]", s):
            add("summary-lowercase", 1, s[:50])
        if len(s.split()) > SUMMARY_MAX_WORDS:
            add("summary-long", 1, f"{len(s.split())} слов: {s[:50]}")
        # правило безусловное: summary — подпись в таблице, а не предложение прозы
        if ends_with_period(s):
            add("summary-trailing-period", 1, s[-50:])

    if re.search(r"^lectures: \[", fm_text, re.M):
        add("lectures-inline", 1, "lectures записан inline-списком")
    for m in re.finditer(r"^lectures:\n((?:  - .*\n)+)", fm_text + "\n", re.M):
        for v in re.findall(r"^  - (.*)$", m.group(1), re.M):
            if RE_YAML_NOT_STRING.fullmatch(v.strip()):
                add("lectures-unquoted", 1, f"YAML прочитает не строкой: {v}")

    if re.search(r"^aliases:\s*\[\s*\]\s*$", fm_text, re.M):
        add("aliases-empty", 1, "пустой aliases: []")
    # число с одним разделителем дробной части; 127.0.0.1, 802.1Q и 0000-00-00 — идентификаторы
    for alias in as_list(data.get("aliases")):
        if re.fullmatch(r"\d+(?:[.,]\d+)?", str(alias).strip()):
            add("alias-number", 1, f"алиас-число: {alias}")

    check_tags(rel, preset, data, idx, add)

    created_raw = re.search(r"^created:[^\S\n]*(.*)$", fm_text, re.M)
    if created_raw:
        raw, value = created_raw.group(1).strip(), data.get("created")
        if isinstance(value, list):
            add("created-format", 1, "created записан списком")
        elif raw.startswith(('"', "'")):
            add("created-format", 1, f"в кавычках: {raw[:40]}")
        elif isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            add("created-format", 1, value.strip()[:40])

    for alias, others in idx.collisions.get(rel, []):
        others = [o for o in others if not idx.homonyms(alias, rel, o)]
        if others:
            add("alias-collision", 1, f"«{alias}» также у {', '.join(others[:2])}")

    # ── тело ───────────────────────────────────────────────────────────────
    body = lines[body_line:] if fm is not None else lines
    # H1 с именем файла не сверяем: имя — ручка для [[ссылок]], H1 — название содержания,
    # и расходятся они законно (SKILL.md → ## Чек-лист перед сдачей заметки)
    h1_idx = next((i for i, ln in enumerate(body) if ln.startswith("# ")), None)
    if h1_idx is not None and preset == "lecture":
        for j in range(h1_idx + 1, min(h1_idx + 3, len(body))):
            s = body[j].strip()
            if not s:
                continue
            if s.startswith(">") and not s.startswith("> [!"):
                add("intro-blockquote", body_line + j + 1, s[:60])
            break

    if preset in MOC_PRESETS:
        check_moc(body, body_line, add)
    if preset == "hub-project":
        words = prose_words(body)
        if words > HUB_BODY_WORDS:
            add("hub-longread", 1, f"слов в теле ядра — {words}")

    last = len(lines)
    while last > 0 and not lines[last - 1].strip():
        last -= 1
    tail_re = re.compile(r"^(?:#{2,6}\s*(?:Смежное|Смежные|См\. также|Связанные)\b"
                         r"|(?:Смежное|Смежные заметки|См\. также)\s*:)")
    for i in range(max(0, last - 12), last):
        if tail_re.match(lines[i].strip()):
            add("related-tail", i + 1, lines[i].strip()[:70])

    # алиас ставит заметка, которая понятием владеет, а не любая, где мелькнула расшифровка
    known = {str(a).strip().lower() for a in as_list(data.get("aliases"))}
    known.add(path.stem.lower())
    names = note_names(path.stem, data, lines, body_line)
    # сначала собираем ВСЕ расшифровки: ранний выход прятал бы повтор той же
    # аббревиатуры, а он и есть отдельная находка
    decoded = abbrev_decodings(lines, body_line)
    for abbr, at in decoded.items():
        if abbr.lower() not in known and owns_decoding(names, preset, lines, abbr, at):
            add("abbrev-no-alias", at[0][0], f"{abbr} расшифрована здесь, но не в aliases")
        if len(at) > 1:
            more = f" и ещё {len(at) - 2} раз ниже" if len(at) > 2 else ""
            add("abbrev-redecoded", at[1][0],
                f"{abbr} уже расшифрована в строке {at[0][0]}{more}; дальше она идёт голой")
        # у расшифровки один владелец: повтор её у владельца — находка, у другой заметки
        # мимоходом — нет; заметка с несвязанной расшифровкой — омоним
        owners = idx.abbr_owners(abbr)
        twins = [o for o, exps in idx.decodings.get(abbr.lower(), {}).items()
                 if o != rel and o in owners and not all(unrelated(e, a[1]) for e in exps for a in at)]
        if twins:
            add("abbrev-redecoded", at[0][0],
                f"{abbr} расшифрована и в {', '.join(twins[:2])}: у расшифровки один владелец")
    # дневник — пространство свободы, как и для титулов callout и оборотов в scan_body
    if not preset.startswith("diary"):
        # пара CI/CD, расшифрованная или взятая в алиас целиком, покрывает и свои части;
        # "GT/s" и "BGP/MPLS IP VPN" — не пары аббревиатур
        def parts(names):
            return {p.lower() for a in names if re.fullmatch(ABBR_PAIR, a) for p in a.split("/")}
        spelled = {a.lower() for a in decoded} | parts(decoded)
        aliased = known | parts(str(a).strip() for a in as_list(data.get("aliases")))
        check_undecoded(rel, lines, body_line, aliased | spelled, spelled, idx, add)

    # "у заметки есть видео" объявляет она сама: media_link или sources-ссылка на видеохостинг
    has_media = "media_link" in keys or any(
        RE_VIDEO_SOURCE.search(str(s)) for s in as_list(data.get("sources")))
    check_nav(path, fm_text, idx, add)
    check_freshness(path, fm_text, data, keys, idx, add)
    scan_body(path, lines, body_line, preset, has_media, idx, add)
    check_anchors(path, idx, add)
    check_link_anchors(path, lines, idx, add)
    check_dataview_sort(lines, add)
    check_footnotes(lines, add)
    check_dup_definitions(path.stem, lines, idx, add)
    return preset


def check_tags(rel, preset, data, idx, add):
    """Тег — сквозное свойство нескольких заметок (SKILL.md → ### Теги)"""
    for t in note_tags(data):
        if t in TAG_EXEMPT:
            continue
        if t != t.lower() or re.search(r"[\s-]", t):
            add("tags-multiword", 1, f"тег не по форме: {t}")
        # тег, стоящий лишь на тех заметках, которые он называет, свойства сверх них не несёт;
        # совпавший с алиасом владельца сквозной тег на других заметках — законное свойство
        owners = idx.names.get(norm_tag(t), set())
        if owners and idx.tag_notes.get(t, set()) <= owners:
            add("tag-is-alias", 1, f"{t} — стоит только на заметках, которые называет")
        if len(idx.tag_notes.get(t, ())) == 1 and not rel.startswith(DIARY_ROOT):
            add("tag-singleton", 1, f"{t} есть только здесь")
        if t in idx.variants:
            add("tag-variant", 1, f"{t} ~ {', '.join(idx.variants[t][:3])}")
    # группу проверяет сам MOC: одна находка на тег, а не по одной на каждую заметку группы
    group = idx.groups.get(rel)
    if group:
        seen = {t for r in group for t in idx.tag_names.get(r, ())}
        for t in sorted(seen - TAG_EXEMPT):
            if tag_mirror(idx.tag_notes[t], group, rel):
                add("tag-mirrors-moc", 1, f"{t} — на {len(idx.tag_notes[t])} из {len(group)} заметок группы")


def nav_field(fm_text, name):
    """Значение up/prev/next как имя заметки, без якоря и подписи."""
    m = re.search(rf'^{name}:\s*"?\[\[(.+?)\]\]"?\s*$', fm_text, re.M)
    return link_target(m.group(1)) if m else None


def check_nav(path, fm_text, idx, add):
    """up ведёт в существующую заметку, цепь prev/next читается в обе стороны.
    Обе стороны резолвятся как любая ссылка — Index.link_dests, от своей заметки"""
    up = nav_field(fm_text, "up")
    if up and not idx.known(up, path):
        add("up-broken", 1, f"up ведёт в никуда: {up}")

    for here, there in (("next", "prev"), ("prev", "next")):
        target = nav_field(fm_text, here)
        if not target:
            continue
        dests = [p for p in idx.link_dests(target, path) if p.suffix == ".md"]
        if not dests:
            add("chain-broken", 1, f"{here} указывает на несозданную «{target}»")
            continue
        backs = [(p, nav_field(split_frontmatter(read(p))[0] or "", there)) for p in dests]
        if not any(back and path in idx.link_dests(back, p) for p, back in backs):
            add("chain-broken", 1, f"{here}={target}, но её {there}={backs[0][1]}")


def check_freshness(path, fm_text, data, keys, idx, add):
    """status/superseded_by: значения, которые dataview прочитает так, как задумано."""
    status = data.get("status")
    if "status" in keys and str(status).strip() not in STATUS_VALUES:
        add("status-value", 1, f"status: {str(status).strip()[:40]}")
    if "superseded_by" in keys:
        target = nav_field(fm_text, "superseded_by")
        if not target:
            add("superseded-by-broken", 1, "superseded_by записан не как \"[[Заметка]]\"")
        elif not idx.known(target, path):
            add("superseded-by-broken", 1, f"superseded_by ведёт в никуда: {target}")
        if "status" not in keys:
            add("superseded-by-no-status", 1, "есть superseded_by, нет status")


def check_moc(body, body_line, add):
    banned = re.compile(r"^#{2,6}\s*(Сюжетн|Что дальше|Куда дальше|Как связ|Введение|Обзор темы)", re.I)
    prose = 0
    in_code = False
    for i, ln in enumerate(body):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if banned.match(ln.strip()):
            add("moc-prose", body_line + i + 1, ln.strip()[:60])
        s = ln.strip()
        if s and not s.startswith(("#", ">", "|", "-", "*", "!", "[", "^")):
            prose += len(s.split())
    if prose > 150:
        add("moc-prose", 1, f"слов прозы в теле индекса — {prose}")


# Строки, которые не абзац прозы: таблица, заголовок, формула, эмбед, сноска, титул callout,
# html и скрытый текст. Сноска — подробности по определению, её длину не считаем
NOT_PROSE = ("|", "#", "---", "$$", "![[", "[^", "[!", "<", "%%")
# Потолок длины — про конспекты: лекции и статьи. У ядер, Zettel и дневника своя мера
LENGTH_PRESETS = {"lecture", "lecture-moc", "paper"}
# строка-ссылка на интерактивную страницу: «▶ [[имя.html|подпись]] — можно …»
RE_SANDBOX_LINE = re.compile(r"^▶\s*\[\[([^\]|#]+\.html)")


def prose_word_count(s):
    """Слова, которые видит читатель: формула и `код` — по одному, у ссылки — её подпись."""
    s = re.sub(r"\$[^$]+\$", " X ", s)
    s = re.sub(r"`[^`]+`", " X ", s)
    s = RE_WIKILINK_FULL.sub(lambda m: unescape_pipe(m.group(1)).split("|", 1)[-1], s)
    s = re.sub(r"\[\^[^\]]+\]", "", s)
    return len(re.sub(r"^([-*]|\d+\.)\s+", "", s).split())


def scan_body(path, lines, body_line, preset, has_media, idx, add):
    # дневник — "пространство свободы": ни титулы callout, ни обороты там не разбираем
    strict_prose = not preset.startswith("diary")
    outline = []                                   # (уровень, строка) секционных заголовков
    h1_seen = 0                                    # H1 после frontmatter: первый — титул, лишние ловим
    in_code = in_math = False
    prev_bare = ""                                 # последняя непустая строка: эмбед перед подписью
    sandbox_lines = {}                             # страница .html → строка её ▶
    prose = dict(iter_prose(lines, body_line))     # строки без кода и формул: где ссылка — ссылка
    for i, ln in enumerate(lines, 1):
        if i <= body_line and body_line:
            continue
        bare_prefix = re.sub(r"^[\s>]*", "", ln)
        if bare_prefix.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # a quote stays open across a line of the same or greater depth, a bare ">" too
        head = RE_CALLOUT_HEAD.match(ln)
        if head and i > 1 and quote_depth(lines[i - 2]) >= head.group(1).count(">"):
            add("callout-no-blank", i, f"[!{head.group(2)}] продолжает блок строки выше")
        if bare_prefix.strip() == "$$":
            in_math = not in_math
            continue
        stripped = ln.strip()
        bare = re.sub(r"^[\s>]*", "", stripped)     # и вложенный callout: «> > » тоже маркер
        nocode = strip_code_spans(ln)              # всё ссылочное разбираем по строке без `кода`

        bad = quote_offences(ln)
        if bad:
            pos, kind = bad[0]
            around = ln[max(0, pos - 25):pos + 25].strip()
            note = "  ← уровни наизнанку: снаружи прямые, ёлочки внутри" if kind == "swapped" \
                else f"  (×{len(bad)} в строке)" if len(bad) > 1 else ""
            add("quotes", i, f"…{around}…{note}")

        if not in_math and bare and not bare.startswith(("|", "#", "---", "$$")):
            if ends_with_period(bare) and not is_latin(bare):
                add("trailing-period", i, bare[-55:])
        elif not in_math and bare.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", bare):
            for cell in re.split(r"(?<!\\)\|", strip_code_spans(bare).strip("|")):
                cell = cell.strip()
                if cell and ends_with_period(cell) and not is_latin(cell):
                    add("trailing-period", i, f"ячейка: {cell[-50:]}")
                    break

        if strict_prose and RE_SLOP.search(bare) and not bare.startswith(("|", "#")):
            add("slop-phrase", i, bare[:70])
        if strict_prose and not bare.startswith("#"):
            hit = RE_PROVENANCE.search(strip_code_spans(bare))
            if hit:
                add("provenance-note", i, f'"{hit.group(0)}": {bare[:60]}')
        if preset in LENGTH_PRESETS:
            hit = RE_STUDY_PROCESS.search(strip_code_spans(bare))
            if hit:
                add("study-process", i, f'"{hit.group(0)}": {bare[:60]}')

        # одна строка — один абзац (жёстких переносов в волте нет); подпись — абзац сразу за эмбедом
        if preset in LENGTH_PRESETS and not in_math and bare and not bare.startswith(NOT_PROSE):
            n = prose_word_count(bare)
            if prev_bare.startswith("![["):
                if n > CAPTION_MAX_WORDS:
                    add("caption-long", i, f"{n} слов: {bare[:50]}")
            elif n > PARAGRAPH_MAX_WORDS:
                add("paragraph-long", i, f"{n} слов: {bare[:50]}")
        if bare:
            prev_bare = bare

        page = RE_SANDBOX_LINE.match(bare)
        if page:
            if page.group(1) in sandbox_lines:
                add("sandbox-dup", i, f"{page.group(1)} уже на строке {sandbox_lines[page.group(1)]}")
            sandbox_lines.setdefault(page.group(1), i)

        if re.search(r"\[\[[^\]]*\|[^\]]*\$[^\]]*\]\]", nocode):
            add("formula-in-caption", i, "формула в подписи ссылки")
        if RE_SCAFFOLD.search(nocode):
            add("link-scaffolding", i, bare[:70])
        if re.search(r"`=[^`]", ln):
            add("inline-code-equals", i, "инлайн-код начинается с =")
        if re.search(r"\\tg|\\arctg|\\ctg|\\arcctg", ln):
            add("latex-ru-macro", i, "русский макрос \\tg/\\arctg")
        for m in re.finditer(r"!?\[\[#[^\]]*\]\]", nocode):
            add("bare-self-link", i, m.group(0)[:70])

        # ни в [[…]], ни в `коде` формул нет: в якоре LaTeX пишется пробелами,
        # а `$set`, `$remote_addr` — это доллар как символ, не открытие формулы
        parts = re.sub(r"\[\[.*?\]\]", "", nocode).split("$")
        # непарный $ — валюта (~$1) или переменная шелла; парные спаны до него остаются
        if len(parts) % 2 == 0:
            parts = parts[:-1]
        for k in range(1, len(parts), 2):
            span = parts[k]
            if span and (span[0] == " " or span[-1] == " "):
                add("math-spaces", i, f"пробел внутри ${span[:30]}$")

        if bare.startswith("|"):
            if re.search(r"\[\[[^\]]*[^\\]\|", nocode):
                add("table-pipe", i, "неэкранированный | в wiki-ссылке")

            if is_table_header(lines, i):
                # пайп подписи внутри ячейки экранирован — он не граница столбца
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", bare.strip("|"))]
                # пустая ячейка ВНУТРИ — разделительный столбец между половинами, это вёрстка
                if cells and not cells[0]:
                    add("table-header-blank", i, bare[:70])
                lower = [c for c in cells if c and c[0].isalpha() and c[0].islower()]
                if lower:
                    add("table-header-case", i, ", ".join(lower[:4]))
            for k in range(1, len(parts), 2):          # только внутри $…$
                pos = parts[k].find("|")
                if pos >= 0:
                    around = parts[k][max(0, pos - 18):pos + 18]
                    add("table-modulus", i, f"…{around}… — нужен \\lvert…\\rvert")

        title = None
        if re.match(r"^#{2,6} ", stripped):
            title = stripped.split(" ", 1)[1]
            outline.append((len(stripped) - len(stripped.lstrip("#")), i))
            if has_media and preset == "lecture" and stripped.startswith("## ") \
                    and "youtube.com/watch" not in ln:
                add("heading-no-timecode", i, title[:60])
            plain = strip_markup(title)
            if " — " in plain and not re.search(r"— это\b", plain) and not plain.rstrip().endswith("MOC"):
                add("heading-dash", i, title[:70])
        elif stripped.startswith("# "):
            h1_seen += 1
            if h1_seen > 1 and stripped[2:].strip() != "Вне курса":
                add("extra-h1", i, stripped[2:][:60])
        m = RE_CALLOUT.match(ln)
        if m and strict_prose:
            title = m.group(1).strip()
            if not title:
                add("callout-title-empty", i, stripped[:50])
            elif is_meta_label(title):
                add("callout-title-label", i, title[:70])
        if title and set(strip_markup(title)) & UNICODE_MATH:
            add("heading-unicode-math", i, title[:60])

        for target in RE_WIKILINK.findall(prose.get(i, "")):
            name = link_target(target)
            if not name:
                continue
            if idx.known(name, path):
                continue
            if ATTACHMENT_EXT.search(name):
                add("missing-attachment", i, name)
            else:
                near = difflib.get_close_matches(name, idx.notes, n=1, cutoff=0.85)
                add("broken-link", i, f"{name}" + (f"  — похоже на «{near[0]}»" if near else ""))

    check_outline(outline, preset, add)

    for i, s in prose.items():
        for name, n in link_repeats(path, s, idx):
            add("link-repeat", i, f"[[{name}]] — {n} ссылки с одним термином в одной строке")

    for i in range(1, len(lines)):
        if re.match(r"^>\s*>\s*\[!", lines[i]) and re.match(r"^>", lines[i - 1]) \
                and lines[i - 1].strip() != ">" and not re.match(r"^>\s*>", lines[i - 1]):
            add("nested-callout-no-blank", i + 1, "нет строки-разделителя > перед вложенным callout")


def link_term(text):
    """Термин подписи ссылки для сравнения: без регистра, разметки и лишних пробелов, ё = е"""
    text = re.sub(r"[*_=~`]", "", text).lower().replace("ё", "е")
    return re.sub(r"\s+", " ", text).strip()


def link_repeats(path, s, idx):
    """-> [(ссылка, сколько раз)] заметок, на которые строка прозы s из path ссылается
    одним термином больше одного раза. Термин — показанная подпись (link_term), у ссылки
    без подписи — её цель без папки: [[X]] и [[X|x]] — один термин. Якорь не важен:
    [[X|ECN]] и [[X#Поля|ECN]] — повтор, а [[X|IHL]] и [[X|ECN]] — нет, это два термина.
    Заметка — файл по link_dests, а не написание: [[dir/X]] и [[X]] одна заметка. Эмбед
    показывает файл, а не ссылается на него, и не считается"""
    s = RE_EMBED.sub(lambda m: " " * len(m.group(0)), s)
    links = collections.defaultdict(list)          # (заметка, термин) -> [ссылка]
    for m in RE_WIKILINK_FULL.finditer(s):
        link, bar, caption = unescape_pipe(m.group(1)).partition("|")
        name, _, anchor = link.partition("#")
        name, anchor = name.strip(), anchor.strip()
        dests = idx.link_dests(name, path) if name else [path]
        note = frozenset(dests) or ("?", name.lower())
        shown = (name or path.stem).rsplit("/", 1)[-1] + (f"#{strip_heading(anchor)}" if anchor else "")
        term = link_term(caption if bar else shown)
        links[note, term].append(link.strip() + (f"|{caption.strip()}" if bar else ""))
    return [(found[0], len(found)) for found in links.values() if len(found) > 1]


def is_table_header(lines, i):
    """Строка i (с 1) — шапка таблицы: её опознаёт строка-разделитель под ней, а не
    позиция в таблице"""
    nxt = re.sub(r"^[\s>]*", "", lines[i]) if i < len(lines) else ""
    return "-" in nxt and bool(re.match(r"^\|[\s:|-]+\|\s*$", nxt))


# Расшифровка — латинская фраза из двух и более слов, первое с заглавной:
# "Carrier-Grade NAT", "HTTP Archive", "Continuous Integration / Continuous Deployment".
# Слово с цифрой и буквой — слово ("IA-32e Mode Enable"), число — слово внутри фразы
# ("Virtual-8086 Mode flag"), но не в её конце: "(RFC 2018)" — ссылка, а не расшифровка.
# У аббревиатуры с цифрой число стоит и в конце: "Year 2000" у Y2K
EXPANSION_WORD = r"[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*"
RE_EXPANSION = re.compile(rf"[A-Z][A-Za-z]+(?:[ /-]+(?:{EXPANSION_WORD}|\d+(?=[ /-]+[A-Za-z]))){{1,6}}")
RE_EXPANSION_NUM = re.compile(rf"[A-Z][A-Za-z]+(?:[ /-]+(?:{EXPANSION_WORD}|\d+)){{1,6}}")


def is_expansion(tail, pattern=RE_EXPANSION):
    """Идёт ли сразу за аббревиатурой её расшифровка — в любой из принятых форм.

    Формы перечислены в SKILL.md → ### Тон и пунктуация, сноска [^abbr-forms].
    Опознаём по латинской фразе, а не по разделителю: разделитель у каждой формы
    свой, фраза есть у всех. Между аббревиатурой и фразой пускаем только знаки,
    пробелы и русский хвост, иначе "**SNI** виден в ClientHello TLS" сошло бы
    за расшифровку.
    """
    m = pattern.search(tail)
    if not m:
        return False
    gap = tail[:m.start()]
    if re.search(r"[A-Za-z]", gap):
        return False
    if "(" in gap:                     # в скобках — русский хвост перед ними не мешает,
        # но скобка не закрылась до фразы: "(форма прошедшего) идёт в Past Simple" — фраза за ней
        return len(gap) <= 30 and ")" not in gap[gap.rindex("("):]
    # пайп — соседняя ячейка таблицы: "| **PCP** | Port Control Protocol |"
    return bool(re.fullmatch(r"[\s,:—–|-]*(?:[а-яё]+[\s,:—–-]*)?", gap))


ABBR = r"[A-ZА-ЯЁ][A-ZА-ЯЁ0-9]+(?:-[A-ZА-ЯЁ0-9]+)*"
# Пара через косую черту — одна аббревиатура, так её пишут и в aliases: CSMA/CD, CI/CD
ABBR_PAIR = rf"{ABBR}(?:/{ABBR})*"
RE_ABBR_BOLD = re.compile(rf"\*\*({ABBR_PAIR})(?:\*\*)?")
# в таблице типов записей аббревиатура стоит кодом: "| `NS` (name server) |"
RE_ABBR_CODE = re.compile(rf"`({ABBR})`")
# "**firewall** (сокращённо **FW**)": расшифровка стоит до аббревиатуры
RE_SHORTENED = re.compile(rf"(?:\*\*([^*]+)\*\*|([\wё-]+))\s*\(\s*(?:сокращённо|сокращенно|сокр\.)\s+\*\*({ABBR})\*\*")
# строчная или русская расшифровка — только после явного разделителя: "**НЕ** работает" — акцент
RE_SPELLED_TAIL = re.compile(r"(?:-?[а-яё]+)?\s*(?:\(|[—–:,|])\s*((?:[\wё]+(?:[ -]+|\s*[–—]\s*)){0,8}[\wё]+)")
# служебные слова: английские, русские и романо-германские артикли и предлоги —
# "train à grande vitesse" (TGV)
ABBR_FILLERS = {"of", "for", "the", "and", "to", "in", "on", "over", "и", "в", "с", "для", "по", "на",
                "à", "de", "la", "le", "les", "du", "des", "di", "da", "del", "von", "van", "der", "den"}


def spells(abbr, phrase, whole=False, one_word=False):
    """Буквы аббревиатуры по порядку берутся из слов фразы: каждое значимое слово отдаёт свою
    начальную букву, составное — ещё и буквы изнутри ("атомная электростанция" — АЭС,
    "металл–оксид–полупроводник" — МОП, CommonJS — CJS); служебные слова пропускаются.
    Слово капсом букв изнутри не даёт: "Europe PMC (PMC11446842)" — сама аббревиатура и номер.
    Одно слово складывает аббревиатуру не короче трёх букв: две буквы внутри одного слова
    совпадают случайно; one_word снимает этот запрет, когда совпадение подтверждено иначе.
    whole — фраза кончается на последней букве: расшифровка стоит перед скобкой"""
    letters = [c.lower() for c in abbr if c.isalpha()]
    split = [w for w in re.split(r"[ \-–—]+", phrase) if w]
    words = [w.lower() for w in split]
    inner = [bool(re.search(r"[a-zа-яё]", w)) for w in split]
    if len(letters) < 2:               # "K1" — буква с номером, складывать нечего
        return False

    def walk(li, wi, used):
        if li == len(letters):
            return (used > 1 or len(letters) >= 3 or one_word) and \
                (not whole or all(w in ABBR_FILLERS for w in words[wi:]))
        if wi == len(words):
            return False
        w = words[wi]
        if w[0] == letters[li]:
            nxt, pos = li + 1, 1
            while True:                # слово отдаёт начальную букву и, может быть, буквы изнутри
                if walk(nxt, wi + 1, used + 1):
                    return True
                pos = w.find(letters[nxt], pos) + 1 if nxt < len(letters) and inner[wi] else 0
                if not pos:
                    break
                nxt += 1
        return w in ABBR_FILLERS and walk(li, wi + 1, used)

    return walk(0, 0, 0)


# "**Вольт-амперная характеристика** (ВАХ)", "метод наименьших квадратов (**МНК**)"
RE_BEFORE = re.compile(rf"((?:[\wё]+[ -]+){{0,8}}[\wё]+)\**\s*\(\**({ABBR_PAIR})\**[),;]")

# Русский перевод латинской аббревиатуры — не расшифровка, но находке полезно его назвать.
# Букв с аббревиатурой он не делит, поэтому опора — форма, в которой видна граница фразы: скобка сразу за жирной аббревиатурой ("**TLB** (буфер ассоциативной
# трансляции)", берётся её первый отрезок до запятой или тире) или скобка с одной аббревиатурой
# сразу за жирным термином, за началом ячейки таблицы или пункта списка. Без жирного фраза
# начинается с заглавной: строчная в начале пункта — обрывок фразы ("- численного моделирования")
RE_BRACKET_HEAD = re.compile(r"(?:-?[а-яё]+)?\s*\(\s*([^()\n,;]*?)\s*(?:[,;)]|\s[—–]\s)")
RE_PINNED_BEFORE = re.compile(
    rf"(?:\*\*([^*\n]+)\*\*|^[\s>]*(?:[-*+]\s+|\d+\.\s+)([А-ЯЁ][^|*()\n]*?)"
    rf"|(?<!\\)\|\s*([А-ЯЁ][^|*()\n]*?))\s*\(\**({ABBR_PAIR})\**\)")
RE_TABLE_ROW = re.compile(r"^[\s>]*\|")
RE_RU_TERM_WORD = re.compile(r"[а-яё]+(?:-[а-яё]+)*", re.I)
# Слова, с которых начинается пояснение, а не перевод: "(в исходных единицах отклика)",
# "(нужен включённый коллектор)"
RU_REMARK_START = {
    "в", "во", "к", "ко", "с", "со", "на", "по", "для", "из", "от", "до", "у", "о", "об", "при",
    "без", "через", "про", "за", "под", "над", "между", "после", "кроме", "вместо", "около",
    "и", "а", "но", "или", "либо", "не", "ни", "как", "это", "то", "так", "где", "когда", "если",
    "что", "чтобы", "он", "она", "оно", "они", "мы", "вы", "я", "его", "её", "их", "тут", "здесь",
    "там", "уже", "ещё", "тоже", "также", "только", "лишь", "даже", "точнее", "иначе", "например",
    "напр", "см", "нужен", "нужна", "нужно", "нужны", "можно", "нельзя",
}


def translates(abbr, phrase, bold=False):
    """Русский перевод латинской аббревиатуры: фраза из кириллических слов, не короче двух
    (жирный термин — и одно слово), и начинается не со служебного слова"""
    words = phrase.split()
    if not re.fullmatch(r"[A-Z0-9]+(?:[/-][A-Z0-9]+)*", abbr) or not 1 <= len(words) <= 8:
        return False
    if not all(RE_RU_TERM_WORD.fullmatch(w) for w in words):
        return False
    return len(words) >= (1 if bold else 2) and words[0].lower() not in RU_REMARK_START


def expansion_before(m):
    """Хвост слов перед скобкой, чьи начальные буквы складывают аббревиатуру, или None"""
    words = m.group(1).split(" ")
    for j in range(len(words)):
        tail = " ".join(words[j:])
        if spells(m.group(2), tail, whole=True):
            return tail
    return None


def expansion_of(abbr, tail, strict=False):
    """Расшифровка, стоящая сразу за аббревиатурой, или None.

    Латинская фраза с заглавной опознаётся формой (is_expansion); строчная латинская и
    русская — только если её начальные буквы складывают аббревиатуру, иначе за
    расшифровку сошёл бы любой поясняющий оборот в скобках. strict — только второй
    путь: `КОД` в прозе чаще команда или ключ, чем аббревиатура
    """
    # рекурсивная аббревиатура повторяет себя перед фразой: "PHP — PHP: Hypertext Preprocessor"
    tail = re.sub(rf"^([\s,:(—–-]*){re.escape(abbr)}:", r"\1", tail)
    # расшифровка — на языке аббревиатуры: латинская фраза не расшифровывает ЭВМ
    pattern = RE_EXPANSION_NUM if re.search(r"\d", abbr) else RE_EXPANSION
    if not strict and re.search(r"[A-Z]", abbr) and is_expansion(tail, pattern):
        return pattern.search(tail).group(0)
    m = RE_SPELLED_TAIL.match(tail)
    if not m:
        return None
    if spells(abbr, m.group(1)):
        return m.group(1)
    # слово за дефисом повторяет конец фразы: "ИК-спектроскопией (инфракрасной
    # спектроскопией)" — аббревиатуру складывает фраза без него, хоть и одним словом
    suffix = re.match(r"-([а-яё]+)", tail)
    words = m.group(1).split()
    if suffix and len(words) > 1 and ru_stem(words[-1].lower()) == ru_stem(suffix.group(1)) \
            and spells(abbr, " ".join(words[:-1]), one_word=True):
        return m.group(1)
    return None


# "Верхняя и нижняя мёртвые точки (**ВМТ** и **НМТ**)": общий хвост фразы у двух аббревиатур
RE_SHARED_TAIL = re.compile(
    rf"((?:[\wё]+[ -]+){{0,8}}?)([\wё]+) и ([\wё]+)((?:[ -]+[\wё]+){{1,6}})"
    rf"\s*\(\**({ABBR})\**\s+и\s+\**({ABBR})\**\)")


def shared_tail_decodings(ln):
    """-> [(аббревиатура, расшифровка)] пары, расшифрованной одной фразой с общим хвостом"""
    out = []
    for m in RE_SHARED_TAIL.finditer(ln):
        rest = m.group(4).strip(" -")
        first, second = f"{m.group(2)} {rest}", f"{m.group(3)} {rest}"
        if spells(m.group(5), first, whole=True) and spells(m.group(6), second, whole=True):
            out += [(m.group(5), first), (m.group(6), second)]
    return out


def abbrev_decodings(lines, start):
    """-> {аббревиатура: [(номер строки, расшифровка), ...]} в теле заметки"""
    notes_txt = {m.group(1): m.group(2)
                 for m in (re.match(r"\[\^([\w-]+)\]:\s*(.*)$", l.strip()) for l in lines) if m}
    out = collections.defaultdict(list)
    for i in range(start, len(lines)):
        ln = blank_quotes(lines[i])
        # только КАПСОВЫЕ токены: "**Mesa** — открытая реализация" это определение слова,
        # а не расшифровка аббревиатуры. Жирный закрывается и до, и после токена
        for m in [*RE_ABBR_BOLD.finditer(ln), *RE_ABBR_CODE.finditer(ln)]:
            tail = ln[m.end():m.end() + 90]
            # "**AS External LSA**" — термин, который начинается с аббревиатуры: внутри
            # незакрытого жирного расшифровку отделяет знак, а не один пробел
            if not m.group(0).endswith(("**", "`")) and re.match(r"\s+[A-Za-z]", tail):
                continue
            fn = re.match(r"\[\^([\w-]+)\]", tail)          # расшифровка уехала в сноску
            code = m.group(0).startswith("`")
            exp = expansion_of(m.group(1), tail[fn.end():] if fn else tail, code)
            if not exp and fn:
                exp = expansion_of(m.group(1), notes_txt.get(fn.group(1), ""), code)
            if exp:
                out[m.group(1)].append((i + 1, exp))
        for m in RE_SHORTENED.finditer(ln):
            out[m.group(3)].append((i + 1, m.group(1) or m.group(2)))
        for m in RE_BEFORE.finditer(ln):
            exp = expansion_before(m)
            if exp:
                out[m.group(2)].append((i + 1, exp))
        for abbr, exp in shared_tail_decodings(ln):
            out[abbr].append((i + 1, exp))
    # "**Unique Local** (**ULA**, Unique Local Address)" — фраза до и расшифровка после одного
    # упоминания: на строке одна расшифровка, иначе она сошла бы за повтор
    return {a: [e for k, e in enumerate(at) if e[0] not in {x[0] for x in at[:k]}]
            for a, at in out.items()}


RE_CALLOUT_HEAD = re.compile(r"^\s*((?:>\s*)+)\[!(\w+)\]")


def quote_depth(ln):
    return re.match(r"^\s*((?:>\s*)*)", ln).group(1).count(">")


def callout_kind(lines, i):
    """Тип самого внутреннего callout, в котором стоит строка i (с 0), или None"""
    depth = quote_depth(lines[i])
    for j in range(i, -1, -1):
        d = quote_depth(lines[j])
        if d == 0:
            return None
        m = RE_CALLOUT_HEAD.match(lines[j])
        if m and m.group(1).count(">") <= depth:
            return m.group(2).lower()
        depth = min(depth, d)
    return None


def note_names(stem, data, lines, start):
    """Имя файла, H1 и title — то, чем заметка себя называет"""
    h1 = next((ln[2:] for ln in lines[start:] if ln.startswith("# ")), "")
    return [stem, h1, str(data.get("title") or "")]


def owns_decoding(names, preset, lines, abbr, at):
    """Расшифровка — владение понятием, а не упоминание мимоходом (SKILL.md → ### Тон
    и пунктуация): заметка-термин, аббревиатура или её фраза в имени, H1 или title,
    расшифровка в определяющем callout [!note]. at — [(номер строки, фраза)]"""
    if preset == "term":
        return True
    token = re.compile(rf"(?<!\w){re.escape(abbr)}(?!\w)")
    if any(token.search(n) or any(e.lower() in n.lower() for _, e in at) for n in names):
        return True
    return any(callout_kind(lines, ln - 1) == "note" for ln, _ in at)


def abbrev_translations(lines, start):
    """-> {аббревиатура: (номер строки, перевод)} — первый русский перевод латинской
    аббревиатуры в теле. Перевод не расшифровка: он только меняет совет находки
    abbrev-undecoded — дописать фразу на языке аббревиатуры"""
    out = {}
    for i in range(start, len(lines)):
        ln = blank_quotes(lines[i])
        for m in RE_ABBR_BOLD.finditer(ln):
            head = RE_BRACKET_HEAD.match(ln, m.end())
            if m.group(0).endswith("**") and head and translates(m.group(1), head.group(1)):
                out.setdefault(m.group(1), (i + 1, head.group(1)))
        for m in RE_PINNED_BEFORE.finditer(ln):
            if m.group(3) is not None and not RE_TABLE_ROW.match(ln):
                continue                       # пайп подписи [[Файл|…]] — не граница ячейки
            phrase = next(g for g in m.groups()[:3] if g is not None).strip()
            if translates(m.group(4), phrase, bold=m.group(1) is not None):
                out.setdefault(m.group(4), (i + 1, phrase))
    return out


def blank_quotes(s):
    """В кавычках — цитата источника: название главы или строка даташита, а не свой текст.
    Пробелы той же длины сохраняют позиции символов"""
    return re.sub(r'"[^"\n]*"', lambda q: " " * len(q.group(0)), s)


# Токены, которые выглядят как аббревиатура, но ею не являются: ключевые слова, регистры,
# единицы, имена. Один источник — файл рядом; запись — регулярное выражение на весь токен
NOT_ABBREV_FILE = pathlib.Path(__file__).resolve().parent / "not-abbreviations.txt"


def load_not_abbreviations(path):
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        out += [re.compile(e) for e in ln.split("#", 1)[0].split()]
    return out


NOT_ABBREVIATIONS = load_not_abbreviations(NOT_ABBREV_FILE)

# Упоминание в прозе. Латинское продолжение через дефис делает токен частью идентификатора
# (IA-32e), русское — нет (MMU-запрос). Перед токеном не стоят якорь, путь, LaTeX и формула;
# после — # активного низкого уровня (RESET#), расширение файла (README.md) и & внутри имени (AT&T)
RE_ABBR_MENTION = re.compile(
    rf"(?<![\w.#$%&\\@=+-])({ABBR})(?![\w#\\@&]|-[A-Za-z0-9]|\.\w)")
# Римское число: век, тип, глава. IV как вектор инициализации — цена этого правила
RE_ROMAN = re.compile(r"(?=[IVX]{2})X{0,3}(?:IX|IV|V?I{0,3})")
# Буква-цифра-буква — аббревиатура (P2P, I2C, L2TP); прочие токены с цифрой — номера деталей,
# подписи схем, модели и версии (R1, SW1, RP2040, DDR4-3200); hex с суффиксом H (F2H) — число
RE_DIGIT_ABBR = re.compile(r"[A-Z]{1,2}\d[A-Z]{1,2}")
RE_HEX_SUFFIX = re.compile(r"[0-9A-F]+H")
# Подряд идущие байты: «C5 E8 58 CB»
RE_HEX_RUN = re.compile(r"(?<![\w-])[0-9A-F]{2}(?:\s+[0-9A-F]{2})+(?![\w-])")
# Ячейка таблицы без строчных букв — ключ строки (регистр, вывод, флаг), его описывает соседняя
RE_KEY_CELL = re.compile(r"[^a-zа-яё]*[A-ZА-ЯЁ][^a-zа-яё]*")


def is_english(s):
    """Строка английского текста — цитата или пример, правило про русскую прозу"""
    words = re.findall(r"\b[a-z]{3,}\b", s)
    lat = len(re.findall(r"[A-Za-z]", s))
    cyr = len(re.findall(r"[А-Яа-яЁё]", s))
    return len(words) >= 4 and lat > cyr


# Русское слово, написанное строчными или с заглавной ("Окей, поехали"): капсом оно акцент
RE_RU_WORD = re.compile(r"(?<![\w-])[А-ЯЁа-яё][а-яё]*(?![\w-])")
# Русское слово капсом — акцент, а не аббревиатура: НЕ, ИЛИ, ОЧЕНЬ. Словом его делает написание
# не капсом в той же заметке, а с этой длины — в любой заметке волта. Короче сверять с волтом
# нельзя: строчные "ос", "ад", "ии" там встречаются, а ОС, АД, ИИ — аббревиатуры
RU_WORD_VAULT_LEN = 4
# Словоформа сверяется по основе: РАКОВИНУ — "раковина", ПЕРЕТАСКИВАЛ — "перетаскивать".
# Основу даёт отсечение одного окончания, и короче этой длины она не бывает
RU_STEM_LEN = 4
RU_ENDINGS = sorted("""
    иями ями ами ией иях иям ием ого его ому ему ыми ими ешь ишь ете ите ает яет ует ают яют
    ть ти чь ла ло ли ет ит ут ют ат ят ая яя ое ее ые ие ой ей ий ый ую юю ом ем ам ям ах ях
    ов ев ию ия ии ье ья а я о е ы и у ю ь й л
""".split(), key=len, reverse=True)


def ru_stem(w):
    """Основа русского слова в нижнем регистре: без возвратной частицы и одного окончания"""
    for e in ("ся", "сь"):
        if w.endswith(e) and len(w) - 2 >= RU_STEM_LEN:
            w = w[:-2]
            break
    for e in RU_ENDINGS:
        if w.endswith(e) and len(w) - len(e) >= RU_STEM_LEN:
            return w[:-len(e)]
    return w


class Lexicon:
    """Русские слова текста в нижнем регистре и их основы"""

    def __init__(self, text=""):
        self.words, self.stems = set(), set()
        self.add(text)

    def add(self, text):
        new = {w.lower() for w in RE_RU_WORD.findall(text)} - self.words
        self.words |= new
        self.stems |= {ru_stem(w) for w in new}

    def has(self, w, min_len=0):
        """Слово w (нижний регистр) написано в тексте как есть или другой формой с той же
        основой. Основа не сверяется, когда у w нет окончания: ГОСТ не "гости"."""
        if len(w) < min_len:
            return False
        stem = ru_stem(w)
        return w in self.words or (stem != w and stem in self.stems)


def not_abbreviation_by_form(tok, note_words, vault_words):
    """Токен капсом — не аббревиатура по самой форме: номер, римское число, русское слово.
    note_words и vault_words — Lexicon заметки и волта"""
    if re.search(r"\d", tok):
        return not RE_DIGIT_ABBR.fullmatch(tok) or bool(RE_HEX_SUFFIX.fullmatch(tok))
    if RE_ROMAN.fullmatch(tok):
        return True
    if re.fullmatch(r"[А-ЯЁ]+(?:-[А-ЯЁ]+)*", tok):
        if all(note_words.has(w) or vault_words.has(w, RU_WORD_VAULT_LEN)
               for w in tok.lower().split("-")):
            return True
    return False


def not_abbreviation(tok, note_words, vault_words):
    """Аббревиатура, которую проза не обязана расшифровывать: форма или словарь
    not-abbreviations.txt — он про расшифровку, а не про то, аббревиатура ли это"""
    return (not_abbreviation_by_form(tok, note_words, vault_words)
            or any(p.fullmatch(tok) for p in NOT_ABBREVIATIONS))


# Строка списка литературы: пункт или сноска, которые открывает автор с годом ("Ward 1973,",
# "Sui et al. 2024", "Iino и Yoshida 2009") или латинский автор с запятой, если в строке есть
# и выходные данные — DOI, arXiv, том, страницы. Название журнала и конференции в ней — имя
RE_REF_START = re.compile(r"(?:[-*+]\s+|\d+\.\s+|\[\^[\w-]+\]:\s*)")
REF_AUTHOR = r"(?:[A-ZА-ЯЁ]\.\s?)*[A-ZА-ЯЁ][\w'’-]+"
RE_REF_AUTHOR_YEAR = re.compile(
    rf"{REF_AUTHOR}(?:(?:,| и| and| &)\s{REF_AUTHOR})*(?:,?\s(?:и др\.|et al\.))?,?\s\(?(?:19|20)\d\d\b")
RE_REF_AUTHOR = re.compile(r"(?:[A-Z]\.\s?)*[A-Z][\w'’-]+(?:\s(?:и|and|&)\s[A-Z][\w'’-]+)?"
                           r"(?:\s(?:и др\.|et al\.))?,")
# DOI бывает и ссылкой на свою заметку: "[[DOI]] 10.1007/…"
RE_REF_DATA = re.compile(r"\bDOI(?:\]\])?:?\s*10\.\d{4,9}/|arXiv:\s?\d{4}\.\d{4,5}|\b(?:vol|pp)\.\s?\d|\bProceedings\b")
# DOI с номером — идентификатор источника, а не аббревиатура в прозе
RE_DOI_NUMBER = re.compile(r"\bDOI:?\s*10\.\d{4,9}/\S+")
# Курсив без кириллицы хотя бы с двумя английскими словами — пример на языке: "*I was watching TV.*"
RE_ITALIC = re.compile(r"(?<![*\w])\*(?![*\s])([^*\n]+?)(?<!\s)\*(?![*\w])|(?<![_\w])_(?![_\s])([^_\n]+?)_(?![_\w])")


def is_reference(s):
    """Строка s (без префикса цитаты) — пункт списка литературы или сноска-ссылка на источник"""
    m = RE_REF_START.match(s)
    if not m:
        return False
    body = s[m.end():]
    return bool(RE_REF_AUTHOR_YEAR.match(body)
                or (RE_REF_AUTHOR.match(body) and RE_REF_DATA.search(body)))


def blank_english_italics(s):
    def blank(m):
        span = m.group(1) or m.group(2)
        foreign = not re.search(r"[А-Яа-яЁё]", span) and len(re.findall(r"\b[a-z]{2,}\b", span)) >= 2
        return " " * len(m.group(0)) if foreign else m.group(0)
    return RE_ITALIC.sub(blank, s)


def abbrev_mentions(lines, start):
    """(номер строки, токен, вид) в прозе тела по порядку. Вид: "link" — в подписи ссылки,
    "decoded" — рядом расшифровка, чьи начальные буквы складывают токен, хоть и без жирного
    ("ЗФО (Защитная Фильтрующая Одежда)"), "bare" — голый. Не проза: код, формулы,
    заголовки, шапки таблиц и титулы callout — это ярлыки, первое упоминание ищется в тексте
    под ними, хотя ссылка в них ссылкой остаётся; эмбеды, html, адреса, цитаты в кавычках,
    английские строки и курсив, ячейки-ключи, строки списка литературы"""
    for i, s in iter_prose(lines, start):
        s = re.sub(r"^[\s>]*", "", s)
        if re.match(r"#{1,6}\s", s):
            continue
        # в ярлыке голый токен расшифровки не требует, но ссылка в нём ссылкой остаётся
        label_only = bool(re.match(r"\[![\w-]+\]", s)) or (s.startswith("|") and is_table_header(lines, i))
        if is_reference(s):
            continue
        s = re.sub(r"!\[\[[^\]]*\]\]", " ", s)
        s = re.sub(r"<(\w+)[^>]*>.*?</\1>", " ", s)
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"\[\^[^\]]*\]:?|\[![\w-]+\][+-]?|\bTL;DR\b", " ", s)
        linked = []

        def label(m):
            raw = unescape_pipe(m.group(1))
            text = raw.split("|", 1)[1] if "|" in raw else raw.split("#")[0]
            linked.extend(t.group(1) for t in RE_ABBR_MENTION.finditer(text))
            return " "
        # ссылка в цитате — всё равно ссылка, поэтому подписи читаются до кавычек
        s = RE_WIKILINK_FULL.sub(label, s)
        if label_only:
            for tok in linked:
                yield i, tok, "link"
            continue
        # текст внешней ссылки — название источника, как цитата, и вики-ссылку в него не вложить
        s = re.sub(r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]\([^)]*\)", " ", s)
        s = re.sub(r"(?:https?://|www\.)\S+", " ", s)
        s = RE_DOI_NUMBER.sub(" ", s)
        s = RE_HEX_RUN.sub(" ", blank_english_italics(blank_quotes(s)))
        if is_english(s):
            continue
        if s.lstrip().startswith("|"):
            s = "|".join(" " if RE_KEY_CELL.fullmatch(c) else c for c in re.split(r"(?<!\\)\|", s))
        for tok in linked:
            yield i, tok, "link"
        # расшифровку перед скобкой без жирного уже находит abbrev_decodings (RE_BEFORE)
        for m in RE_ABBR_MENTION.finditer(s):
            tok = m.group(1)
            near = expansion_of(tok, s[m.end():m.end() + 90], strict=True)
            yield i, tok, "decoded" if near else "bare"


def check_undecoded(rel, lines, start, own, spelled, idx, add):
    """Голая аббревиатура: не расшифрована здесь, заметка не держит её алиасом,
    а первое упоминание — не ссылка. Есть владелец (Index.abbr_owners) — просим ссылку,
    нет — расшифровку, и называем заметки, где она стоит мимоходом.
    spelled — что заметка расшифровала сама (в нижнем регистре), own — это и её алиасы"""
    note_words = Lexicon("\n".join(lines[start:]))
    translated = abbrev_translations(lines, start)
    first, decoded = {}, set()
    for line, tok, kind in abbrev_mentions(lines, start):
        first.setdefault(tok, (line, kind))
        if kind == "decoded":
            decoded.add(tok)
    for tok, (line, kind) in first.items():
        k = tok.lower()
        if kind == "link" or tok in decoded or not_abbreviation(tok, note_words, idx.words):
            continue
        # алиас без расшифровки прощается заметке-владельцу, но не когда она лишь перевела
        # аббревиатуру: расшифровка — на языке самой аббревиатуры
        if k in own and (tok not in translated or k in spelled):
            continue
        # ссылку предлагаем только на владельца: ссылка на заметку, где термин мелькнул,
        # сделала бы её формальным владельцем
        def stems_of(rels):
            return sorted(pathlib.PurePosixPath(o).stem for o in rels
                          if o != rel and not under(o, DIARY_ROOT))

        def named(stems):
            return f"«{stems[0]}»" + (f" и ещё {len(stems) - 1}" if len(stems) > 1 else "")
        owners = stems_of(idx.abbr_owners(k))
        passing = stems_of(set(idx.decodings.get(k, {})) - idx.abbr_owners(k))
        if owners and k not in own:
            add("abbrev-undecoded", line,
                f"{tok} расшифрована в {named(owners)}: первое упоминание — ссылка [[{owners[0]}|{tok}]]")
        elif tok in translated:
            at, phrase = translated[tok]
            add("abbrev-undecoded", line,
                f"{tok} переведена в строке {at} («{phrase}»), но не расшифрована на языке "
                f"аббревиатуры: допиши рядом с переводом латинскую фразу")
        elif passing and k not in own:
            add("abbrev-undecoded", line,
                f"{tok} расшифрована только мимоходом в {named(passing)}, владельца нет: "
                f"расшифруй здесь, а сквозному термину заведи заметку в 00. Термины")
        else:
            add("abbrev-undecoded", line,
                f"{tok} не расшифрована ни здесь, ни в волте: расшифруй при первом появлении")


def expansion_words(exp):
    return {w for w in re.findall(r"[a-zа-яё]{3,}", exp.lower())} - ABBR_FILLERS


def unrelated(a, b):
    """Две расшифровки без общего слова — два понятия, омонимы: CE — Congestion
    Experienced и Customer Edge. Перефразы одного понятия слово делят почти всегда"""
    return not (expansion_words(a) & expansion_words(b))


def is_latin(text):
    """Английская фраза-пример: точка в конце там нормальна, правило про русскую прозу.

    Формулы и код не считаем буквами — иначе `$f(x)=\\sin x$.` сойдёт за английский.
    """
    plain = re.sub(r"`[^`]*`", "", strip_markup(text))
    cyr = sum(1 for c in plain if "а" <= c.lower() <= "я" or c.lower() == "ё")
    lat = sum(1 for c in plain if "a" <= c.lower() <= "z")
    return lat >= 8 and lat > cyr


# Плоских H2 столько, что материал почти наверняка распадается на грани одного понятия.
# Порог взят по волту: заметок с шестью и более H2 без единого H3 — два десятка, это хвост
FLAT_H2_LIMIT = 6


def check_outline(outline, preset, add):
    """Иерархия секционных заголовков: плоский список H2 и перепрыгнутый уровень."""
    for (lvl, _), (nxt, line) in zip(outline, outline[1:]):
        if nxt - lvl > 1:
            add("heading-level-jump", line, f"H{lvl} → H{nxt}, между ними пусто")

    # MOC — индекс, шпаргалка в Zettel — список разделов: плоскость там нормальна
    if preset not in ("lecture", "project-note"):
        return
    h2 = [line for lvl, line in outline if lvl == 2]
    if len(h2) >= FLAT_H2_LIMIT and not any(lvl > 2 for lvl, _ in outline):
        add("headings-flat", h2[0], f"{len(h2)} заголовков H2 подряд, ни одного H3")


def quote_offences(line):
    """Ёлочки и curly-кавычки, которых по стандарту быть не должно.

    Законен ровно один случай — вложенная цитата: «…» **внутри** прямых "…".
    Обратная раскладка (прямые внутри ёлочек) — те же два уровня, но наизнанку,
    и это отдельная подсказка: снаружи должны стоять прямые.
    """
    out = []
    straight = [i for i, c in enumerate(line) if c == '"']
    spans = list(zip(straight[0::2], straight[1::2]))
    guillemets = list(zip([i for i, c in enumerate(line) if c == "«"],
                          [i for i, c in enumerate(line) if c == "»"]))

    for i, c in enumerate(line):
        if c in "“”„":
            out.append((i, "curly"))
        elif c in "«»":
            if any(a < i < b for a, b in spans):
                continue                                   # вложенная цитата — так и надо
            outer = next((g for g in guillemets if g[0] <= i <= g[1]), None)
            if outer and any(outer[0] < a and b < outer[1] for a, b in spans):
                out.append((i, "swapped"))
            else:
                out.append((i, "plain"))
    return out


def prose_words(lines):
    """Слова живого текста. Содержимое фенсов — media-gallery, dataview, код —
    прозой не считается: там `columns: 2` и `type: vertical`, а не написанный текст"""
    total, in_code = 0, False
    for ln in lines:
        if re.sub(r"^[\s>]*", "", ln).startswith("```"):    # фенс внутри callout — тоже фенс
            in_code = not in_code
            continue
        if in_code or not ln.strip() or ln.startswith(("#", "`", "!", ">")):
            continue
        total += len(ln.split())
    return total


def check_anchors(path, idx, add):
    """Блок-якорь без входящей ссылки. Якорь на строке заголовка не разбираем: на заголовок
    ссылаются по тексту, а id там — забота references/wikilinks.md"""
    for key, (line, name, on_heading) in link_targets(path)[1].items():
        if not on_heading and (path, key) not in idx.anchor_refs:
            add("anchor-unused", line, f"^{name} — входящих ссылок нет")


# Якорь ссылки сверяется так же, как его резолвит сам Obsidian (app.js 1.13: resolveSubpath
# и stripHeading). Подпуть после первого # режется по # на части; одна часть с ^ — id блока,
# без учёта регистра; иначе части ищутся среди заголовков по порядку, каждая глубже прошлой.
# Обе стороны сравнения проходят stripHeading: символы ниже → пробел, пробелы схлопываются,
# края обрезаются, регистр не важен. Поэтому якорь "05 50" находит заголовок с "[05:50]"
RE_STRIP_HEADING = re.compile(r"[!\"#$%&()*+,.:;<=>?@^`{|}~/\[\]\\\r\n]")
# id блока — только латиница, цифры и дефис, через пробел после текста (парсер Obsidian)
RE_BLOCK_ID = re.compile(r"(?:^|\s)\^([A-Za-z0-9-]+)\s*$")
RE_HEADING = re.compile(r"^(?:\s*>)*\s*(#{1,6})\s+(.*?)(?:\s+#+)?\s*$")
# В якоре бывают одиночные ] и [ — "[05 50](https //…)", поэтому ссылка тянется до первого ]]
RE_WIKILINK_FULL = re.compile(r"\[\[(.+?)\]\]")


def strip_heading(s):
    return re.sub(r"\s+", " ", RE_STRIP_HEADING.sub(" ", s)).strip().lower()


def iter_live_lines(lines):
    """(номер, строка без `кода`) вне fenced-блоков: в коде нет ни ссылок, ни заголовков"""
    in_code = False
    for i, ln in enumerate(lines, 1):
        if re.sub(r"^[\s>]*", "", ln).startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            yield i, strip_code_spans(ln)


def mask_math(s):
    """Инлайн-формулы $…$ и $$…$$ строки — пробелами той же длины. Obsidian читает строку
    слева направо, и что открылось раньше, то и владеет текстом: `$[[A]]=[A]$` — формула
    со скобками, `[[A#Случай $x$|случай]]` — ссылка с формулой в якоре. Непарный $ — валюта
    или переменная шелла, \\$ — символ доллара"""
    out, i = [], 0
    while i < len(s):
        if s.startswith("[[", i) and "]]" in s[i + 2:]:
            j = s.index("]]", i + 2) + 2
            out.append(s[i:j])
            i = j
            continue
        if s[i] == "$" and (i == 0 or s[i - 1] != "\\"):
            d = "$$" if s.startswith("$$", i) else "$"
            m = re.compile(rf"(?<!\\){re.escape(d)}").search(s, i + len(d) + 1)
            if m:
                out.append(" " * (m.end() - i))
                i = m.end()
                continue
        out.append(s[i])
        i += 1
    return "".join(out)


def iter_prose(lines, start=0):
    """(номер строки с 1, строка) тела после строки start вне fenced-кода и блочных формул:
    `код` снят, инлайн-формулы и куски строки внутри $$…$$ заменены пробелами. Один ответ на
    вопрос "где в строке текст, а не код и не формула" — для ссылок и аббревиатур"""
    in_math = False
    for i, ln in iter_live_lines(lines):
        if i <= start:
            continue
        # $$ открывает и закрывает блок и в начале строки, и в её хвосте (\end{aligned}$$)
        parts = ln.split("$$")
        kept = [" " * len(p) if (k % 2 == 1) != in_math else p for k, p in enumerate(parts)]
        if len(parts) % 2 == 0:
            in_math = not in_math
        yield i, mask_math("  ".join(kept))


_targets = {}


def link_targets(path):
    """-> (заголовки [(уровень, текст)], блоки {id в нижнем регистре: (строка, id, на заголовке ли)})
    заметки. Id блока — RE_BLOCK_ID, единственное его определение: по нему и резолвятся
    ссылки #^id, и ищутся якоря без входящих ссылок"""
    key = str(path)
    if key not in _targets:
        text = read(path)
        _, body_line, _ = split_frontmatter(text)
        lines = text.split("\n")
        heads, blocks = [], {}
        for i, ln in iter_live_lines(lines):
            if i <= body_line:
                continue
            m = RE_HEADING.match(ln)
            if m:
                heads.append((len(m.group(1)), m.group(2)))
            b = RE_BLOCK_ID.search(ln)
            if b:
                blocks.setdefault(b.group(1).lower(), (i, b.group(1), bool(m)))
        _targets[key] = heads, blocks
    return _targets[key]


def resolves(path, subpath):
    heads, blocks = link_targets(path)
    parts = [p for p in subpath.split("#") if p]
    if not parts:
        return True
    if len(parts) == 1 and parts[0].startswith("^") and parts[0][1:].lower() in blocks:
        return True
    if len(parts) == 1 and parts[0].startswith("[^"):
        return True                                    # сноска — не заголовок и не блок
    want, depth = 0, 0
    for level, text in heads:
        if level > depth and strip_heading(text) == strip_heading(parts[want]):
            want, depth = want + 1, level
            if want == len(parts):
                return True
    return False


def check_link_anchors(path, lines, idx, add):
    """[[Заметка#Заголовок]] и [[Заметка#^блок]]: существует ли якорь в заметке-цели.
    Несуществующую заметку оставляем broken-link, вложение (pdf#page=N, html#id) не разбираем"""
    for i, ln in iter_prose(lines):
        for m in RE_WIKILINK_FULL.finditer(ln):
            link = unescape_pipe(m.group(1)).split("|")[0]
            if "#" not in link:
                continue
            linkpath, subpath = link.split("#", 1)
            linkpath = linkpath.strip()
            dests = idx.link_dests(linkpath, path) if linkpath else [path]
            if any(p.suffix.lower() != ".md" for p in dests):
                continue
            if dests and not any(resolves(p, subpath) for p in dests):
                kind = "блока" if subpath.startswith("^") else "заголовка"
                add("anchor-broken", i, f"нет такого {kind}: [[{linkpath or path.stem}#{subpath[:70]}]]")


def check_dataview_sort(lines, add):
    """SORT по lectures внутри dataview-блока: значения — строки в кавычках"""
    in_dv = False
    for i, ln in enumerate(lines, 1):
        bare = re.sub(r"^[\s>]*", "", ln)
        if bare.startswith("```"):
            in_dv = not in_dv and bare[3:].strip() == "dataview"
            continue
        if in_dv and re.match(r"SORT\b.*(?<![\w(])lectures\b", bare.strip()):
            add("moc-sort-lectures", i, bare.strip()[:70])


def check_footnotes(lines, add):
    sections = {}
    cur = 0
    first_use = {}
    for i, ln in enumerate(lines):
        if re.match(r"^#{1,6} ", ln):
            cur = i
        sections[i] = cur
        for m in re.finditer(r"\[\^([\w-]+)\](?!:)", ln):
            first_use.setdefault(m.group(1), i)
    for i, ln in enumerate(lines):
        m = re.match(r"^\[\^([\w-]+)\]:", ln)
        if m and m.group(1) in first_use:
            if sections[i] != sections[first_use[m.group(1)]]:
                add("footnote-far-from-use", i + 1, f"[^{m.group(1)}] определена не в своей секции")


def check_dup_definitions(stem, lines, idx, add):
    for i, ln in enumerate(lines, 1):
        for term in iter_line_definitions(ln):
            definers = list(dict.fromkeys(idx.definitions.get(norm_term(term), [])))
            others = [d for d in definers if d != stem]
            if not others or any(f"[[{d}" in ln for d in others):
                continue
            if len(others) == 1:
                add("dup-definition", i, f"«{term}» — им владеет [[{others[0]}]]")
            else:
                add("dup-definition", i,
                    f"«{term}» уже определяют: {', '.join(f'[[{d}]]' for d in others)}")


def check_iconic(out, scope):
    """Ключи-пути плагина Iconic: Obsidian о нём не знает и при переносе не чинит."""
    data_json = VAULT / ".obsidian/plugins/iconic/data.json"
    if not data_json.exists():
        return False
    try:
        data = json.loads(data_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    for key in data.get("fileIcons", {}):
        if scope and not any(key.startswith(s) for s in scope):
            continue
        if not (VAULT / key).exists():
            out.append(Finding("iconic-dangling", ".obsidian/plugins/iconic/data.json", 0, key))
    return True


# ── отчёт ──────────────────────────────────────────────────────────────────
def report(findings, fired, scope_desc, counted, presets, limit, iconic_ran, active, skipped,
           delta=None):
    """findings — что печатать; fired — коды всех находок прогона, включая скрытые базой;
    delta — None в полном режиме (--all), иначе сводка сравнения с базой."""
    by_code = collections.defaultdict(list)
    for f in findings:
        by_code[f.code].append(f)

    print(f"волт:   {VAULT}")
    print(f"охват:  {scope_desc}, заметок: {counted}")
    if presets:
        print("типы:   " + " · ".join(f"{k} {v}" for k, v in sorted(presets.items(),
                                                                    key=lambda kv: -kv[1])))
    for root, n in sorted(skipped.items()):
        print(f"пропуск:  {n} заметок в «{root}» не тронуто — их пользователь ведёт сам, "
              f"нужен разбор — назвать путь в аргументах")
    if delta is None:
        print(f"всего подсказок: {len(findings)}\n")
    elif delta["base"]:
        print(f"новых: {len(findings)} · известных, скрыто: {delta['hidden']} (--all покажет) · "
              f"исправлено с записи базы: {delta['resolved']}\n")
    else:
        print(f"базы нет — показано всё ({len(findings)}); --accept запишет эти находки как известные\n")
    if delta is not None and not findings:
        print("новых находок нет\n")

    for level, title in ((CERTAIN, "ДОСТОВЕРНО — правится без раздумий"),
                         (SUSPECT, "ПОСМОТРИ — решает человек")):
        codes = [c for c in by_code if CHECKS[c][0] == level]
        if not codes:
            continue
        print(f"{'═' * 74}\n  {title}\n{'═' * 74}\n")
        for code in sorted(codes, key=lambda c: -len(by_code[c])):
            rows = by_code[code]
            _, ref, hint = CHECKS[code]
            print(f"── {code} ({len(rows)})   {ref}")
            print(f"   {hint}")
            for f in rows[:limit]:
                where = f"{f.rel}:{f.line}" if f.line else f.rel
                print(f"   {where}  {f.msg}")
            if len(rows) > limit:
                print(f"   … ещё {len(rows) - limit} (--limit N покажет больше)")
            print()

    clean = sorted(c for c in active if c not in fired)
    if not iconic_ran and "iconic-dangling" in clean:
        clean.remove("iconic-dangling")
    warnings = []
    if yaml is None:
        warnings.append("⚠ PyYAML не найден — yaml-invalid не проверялся, поля разобраны регуляркой")
    if not iconic_ran:
        warnings.append("⚠ .obsidian/plugins/iconic/data.json не прочитан — iconic-dangling не проверялся")

    if delta is not None:
        # короткий хвост: полный список молчащих проверок и чек-лист глазами — в --all
        print(f"проверок прогнано: {len(active)}, молчат: {len(clean)}")
        for w in warnings:
            print(w)
        print("глазами: " + " · ".join(what for what, _ in BY_EYE) + "\n")
        return

    print(f"{'═' * 74}\n  ЧТО ПОСМОТРЕЛ МАШИННО\n{'═' * 74}\n")
    print(f"проверок прогнано: {len(active)}, из них молчат: {len(clean)}")
    print("   " + " · ".join(clean) + "\n")
    for w in warnings:
        print(w + "\n")

    print(f"{'═' * 74}\n  ЧТО ОСТАЛОСЬ ГЛАЗАМИ\n{'═' * 74}\n")
    print("Половина чек-листа машине недоступна. «Чисто» не значит «готово»:\n")
    for what, where in BY_EYE:
        print(f"   👁 {what}\n      {where}")
    print()


def nearest_vault(path):
    """Волт пути — ближайшая папка вверх, которую открыл Obsidian (он держит там .obsidian);
    пути без волта вокруг возвращают папку, в которой лежит"""
    p = pathlib.Path(path).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".obsidian").is_dir():
            return parent
    return p if p.is_dir() else p.parent


def main():
    global VAULT
    ap = argparse.ArgumentParser(description="Подсказчик по стандарту conspect")
    ap.add_argument("paths", nargs="*", help="папки или файлы волта (по умолчанию весь волт)")
    ap.add_argument("--vault", metavar="PATH",
                    help="корень другого волта: по умолчанию — волт конспектов, в котором лежит "
                         "скилл; личный волт разбирается им же (например --vault ~/myWiki)")
    ap.add_argument("--only", help="только эти коды через запятую")
    ap.add_argument("--skip", help="пропустить эти коды")
    ap.add_argument("--limit", type=int, default=12, help="строк на код (по умолчанию 12)")
    ap.add_argument("--list-checks", action="store_true", help="каталог проверок и выход")
    ap.add_argument("--fix", action="store_true",
                    help="исправить механические находки (см. references/lint-fix.md)")
    ap.add_argument("--all", action="store_true",
                    help="показать все находки, а не только новые относительно базы")
    ap.add_argument("--accept", action="store_true",
                    help=f"записать находки этого охвата как известные ({BASELINE})")
    ap.add_argument("--figures", action="store_true",
                    help="ещё и запустить скрипты рисунков курсов охвата (media.py): они "
                         "перерисовывают свои картинки во вложениях, которых нет в git; "
                         "неизменившиеся скрипты берутся из кэша и не запускаются")
    ap.add_argument("--pages", action="store_true",
                    help="ещё и открыть песочницы охвата в Chromium (media.py); "
                         "неизменившиеся берутся из кэша")
    args = ap.parse_args()

    if args.list_checks:
        for code, (level, ref, hint) in sorted(CHECKS.items()):
            fix = "  [--fix]" if code in FIXERS else ""
            print(f"{code:24} {level:6} {ref}{fix}\n{'':24} {hint}")
        return 0

    if args.vault:
        VAULT = pathlib.Path(args.vault).expanduser().resolve()
        if not VAULT.is_dir():
            print(f"нет такого волта: {VAULT}", file=sys.stderr)
            return 2
    elif args.paths:
        # путь вне волта скилла называет свой волт сам: инструмент разбирает оба
        first = pathlib.Path(args.paths[0]).expanduser()
        if first.is_absolute() and not first.resolve().is_relative_to(DEFAULT_VAULT):
            VAULT = nearest_vault(first)

    idx = Index()
    idx.build()

    if args.paths:
        roots, labels = [], []
        for raw in args.paths:
            p = pathlib.Path(raw).expanduser()
            p = p if p.is_absolute() else VAULT / p
            if not p.exists():
                print(f"нет такого пути: {p}", file=sys.stderr)
                return 2
            roots.append(p.resolve())
            if not p.resolve().is_relative_to(VAULT):
                print(f"путь вне волта {VAULT}: {p.resolve()}", file=sys.stderr)
                return 2
            labels.append(p.resolve().relative_to(VAULT).as_posix())
        scope_desc = ", ".join(labels)
    else:
        roots, labels, scope_desc = [VAULT], [], "весь волт"

    targets = []
    for root in roots:
        if root.is_file():
            targets.append(root)
        else:
            targets += [p for p in root.rglob("*.md") if not obsidian_hidden(p)]

    targets, skipped = select_targets(sorted(set(targets)), labels)

    findings, presets, seen = [], collections.Counter(), set()
    for p in targets:
        seen.add(p.relative_to(VAULT).as_posix())
        preset = check_note(p, idx, findings)
        presets[preset or "не объявлен — пропущен"] += 1

    iconic_ran = check_iconic(findings, labels)

    if args.figures or args.pages:
        import media
        config, cache = media.load_config(media.CONFIG), media.Cache(media.CACHE)
        progress = lambda line: print(line, file=sys.stderr, flush=True)  # noqa: E731
        for wanted, walk in ((args.figures, media.check_figures), (args.pages, media.check_pages)):
            if wanted:
                found, walked = walk(VAULT, config, roots if args.paths else [], cache, log=progress)
                findings += [Finding(*f) for f in found]
                seen |= walked

    # коллизия — свойство пары, а не заметки: в охвате обеих сторон она одна
    seen_pairs, deduped = set(), []
    for f in findings:
        if f.code == "alias-collision":
            key = f.msg.split("»")[0], frozenset([f.rel] + f.msg.split("у ")[-1].split(", "))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
        deduped.append(f)
    findings = deduped

    active = set(CHECKS)
    # a walk that did not run neither finds nor clears: its codes are not active, so the report
    # does not call them silent and --accept keeps their entries
    if not args.figures:
        active -= {c for c in CHECKS if c.startswith("figure-")}
    if not args.pages:
        active -= {c for c in CHECKS if c.startswith("page-")}
    if args.only:
        active &= set(args.only.split(","))
    if args.skip:
        active -= set(args.skip.split(","))
    findings = [f for f in findings if f.code in active]

    if args.fix:
        fixed = set()
        for f in findings:
            if f.code in FIXERS and (f.rel, f.code) not in fixed:
                p = VAULT / f.rel
                # newline="" — читать и писать байт в байт, не переводя \r\n
                with open(p, encoding="utf-8", newline="") as fh:
                    raw = fh.read()
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write(FIXERS[f.code](raw))
                fixed.add((f.rel, f.code))
        findings = [f for f in findings if (f.rel, f.code) not in fixed]
        notes = len({rel for rel, _ in fixed})
        print(f"--fix: исправлено находок {len(fixed)} в заметках {notes}\n")

    scope = seen | {f.rel for f in findings}
    if args.accept:
        n, notes = save_baseline(findings, scope, active)
        print(f"база: известными записано находок {n} в заметках {notes} — охват {scope_desc}\n{BASELINE}")
        return 0

    shown, delta = findings, None
    if not args.all:
        shown, hidden, resolved, have = split_by_baseline(findings, load_baseline(), scope, active)
        delta = {"hidden": hidden, "resolved": resolved, "base": have}

    counted = sum(v for k, v in presets.items() if k != "не объявлен — пропущен")
    report(shown, {f.code for f in findings}, scope_desc, counted, presets, args.limit,
           iconic_ran, active, skipped, delta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
