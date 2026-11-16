"""Tests for lint.py. Run from the skill root:

    python3 -m unittest discover -s tools -v
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lint  # noqa: E402

PROJECTS = "03. Записки/02. Ядра/02. Проекты"


class TempVault(unittest.TestCase):
    """A scratch vault: lint reads VAULT and BASELINE as module globals"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name)
        self.saved = lint.VAULT, lint.BASELINE
        lint.VAULT = self.vault
        lint.BASELINE = self.vault / "baseline.json"

    def tearDown(self):
        lint.VAULT, lint.BASELINE = self.saved
        self.tmp.cleanup()

    def touch(self, rel):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")


class HubFlavour(TempVault):
    def test_hub_inside_its_same_named_folder_is_moc(self):
        self.touch(f"{PROJECTS}/Почта/Почта.md")
        self.assertEqual(lint.hub_flavour(f"{PROJECTS}/Почта/Почта.md"), "hub-moc")

    def test_neighbour_of_inner_hub_is_project_note(self):
        self.touch(f"{PROJECTS}/Почта/Почта.md")
        self.touch(f"{PROJECTS}/Почта/Предыстория.md")
        self.assertEqual(lint.hub_flavour(f"{PROJECTS}/Почта/Предыстория.md"), "project-note")

    def test_note_nested_deeper_in_hub_folder_is_project_note(self):
        self.touch(f"{PROJECTS}/Почта/Почта.md")
        self.touch(f"{PROJECTS}/Почта/Архив/Старое.md")
        self.assertEqual(lint.hub_flavour(f"{PROJECTS}/Почта/Архив/Старое.md"), "project-note")

    def test_folder_without_same_named_note_is_a_category(self):
        self.touch(f"{PROJECTS}/Obsidian/Плагин.md")
        self.assertEqual(lint.hub_flavour(f"{PROJECTS}/Obsidian/Плагин.md"), "hub-project")

    def test_thin_hub_at_projects_root_stays_thin(self):
        self.touch(f"{PROJECTS}/Клавиатура.md")
        self.assertEqual(lint.hub_flavour(f"{PROJECTS}/Клавиатура.md"), "hub-project")


NOTE_TMPL = """---
title: {title}
created: 2026-01-01
summary: s
tags:
  - y2026
preset: zettel
{extra}---
# {title}
{body}
"""


class DupDefinition(TempVault):
    def write(self, rel, title, body, extra=""):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(NOTE_TMPL.format(title=title, body=body, extra=extra), encoding="utf-8")

    def dup_findings(self, rel):
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(self.vault / rel, idx, out)
        return [f.msg for f in out if f.code == "dup-definition"]

    def test_incidental_alias_holder_is_not_reported_as_owner(self):
        # A sorts before B and lists "виджет" as a bare alias, but its body never
        # defines the term — it only mentions it in passing
        self.write("A.md", "A", "В списке возможностей есть и **виджет**, и многое другое",
                    extra="aliases:\n  - виджет\n")
        # B is the only note that actually bold-defines "виджет"
        self.write("B.md", "B",
                    "**Виджет** — переиспользуемый визуальный блок интерфейса со своим состоянием")
        self.assertEqual(self.dup_findings("B.md"), [],
                          "B — единственная заметка, где термин правда определён; "
                          "флагать её за то, что A когда-то упомянула то же слово, не за что")

    def test_two_genuine_definitions_are_both_reported(self):
        # Two notes each bold-define "гаджет" for real, neither links the other
        self.write("A.md", "A", "**Гаджет** — небольшое устройство узкого назначения")
        self.write("B.md", "B", "**Гаджет** — компактный электронный прибор с одной функцией")
        self.assertEqual(len(self.dup_findings("A.md")), 1,
                          "оба реальных определения конфликтуют — должна флагаться каждая сторона")
        self.assertEqual(len(self.dup_findings("B.md")), 1)

    def test_linking_the_other_definer_on_the_same_line_clears_the_flag(self):
        self.write("A.md", "A", "**Гаджет** — небольшое устройство узкого назначения")
        self.write("B.md", "B",
                    "**[[A|Гаджет]]** — компактный электронный прибор с одной функцией")
        self.assertEqual(self.dup_findings("B.md"), [])

    def test_mid_sentence_bold_phrase_is_still_flagged(self):
        # "**нет**" here is emphasis inside a sentence, not a real term being defined —
        # the check cannot tell the difference from a genuine definition, and on
        # purpose doesn't try to: this is a SUSPECT-tier, human-reviewed finding, and
        # a missed real duplicate costs more than an extra glance at a false one
        self.write("A.md", "A",
                    "В списке этого больше **нет** — проверено отдельно, реестр почистили")
        self.write("B.md", "B",
                    "Площади такой фигуры пока **нет** — её только предстоит определить")
        self.assertEqual(len(self.dup_findings("A.md")), 1)
        self.assertEqual(len(self.dup_findings("B.md")), 1)

    def test_bold_definition_after_list_marker_or_blockquote_still_counts(self):
        self.write("A.md", "A", "- **Гаджет** — небольшое устройство узкого назначения")
        self.write("B.md", "B", "> **Гаджет** — компактный электронный прибор с одной функцией")
        self.assertEqual(len(self.dup_findings("A.md")), 1)
        self.assertEqual(len(self.dup_findings("B.md")), 1)

    def test_second_definition_after_semicolon_on_the_same_line_also_counts(self):
        # "Аутентификация — X; авторизация — Y" genuinely defines two terms in one
        # sentence — the second one must not be lost just because it isn't first
        self.write("A.md", "A",
                    "**Гаджет** — небольшое устройство узкого назначения; "
                    "**виджет** — визуальный блок интерфейса со своим состоянием")
        self.write("B.md", "B", "**Виджет** — переиспользуемый блок UI с собственным состоянием")
        self.assertEqual(len(self.dup_findings("B.md")), 1)


class AnchorRefs(TempVault):
    def write(self, rel, title, body):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(NOTE_TMPL.format(title=title, body=body, extra=""), encoding="utf-8")

    def findings(self, rel, code):
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(self.vault / rel, idx, out)
        return [f.msg for f in out if f.code == code]

    def test_anchor_linked_only_from_a_table_cell_is_not_unused(self):
        # In a table the label pipe is escaped, or Obsidian would break the row —
        # the reference is a reference all the same
        self.write("A.md", "A", "> [!example]- Сопроцессор 287 ^intel287")
        self.write("B.md", "B", "| Флаг | Смысл |\n| --- | --- |\n"
                                "| IC | Совместим с [[A#^intel287\\|Intel 287]] |")
        self.assertEqual(self.findings("A.md", "anchor-unused"), [])

    def test_anchor_nothing_links_is_still_reported(self):
        self.write("A.md", "A", "> [!example]- Сопроцессор 287 ^intel287")
        self.assertEqual(len(self.findings("A.md", "anchor-unused")), 1,
                          "якорь без единой входящей ссылки — ровно то, что проверка ищет")

    def test_block_id_obsidian_rejects_is_not_an_anchor_at_all(self):
        # One definition of a block id for both checks: "my_id" has "_", which Obsidian
        # does not parse, so anchor-broken flags links to it and anchor-unused has no anchor
        self.write("A.md", "A", "Абзац про сопроцессор ^my_id")
        self.assertEqual(self.findings("A.md", "anchor-unused"), [])

    def test_block_id_on_a_heading_is_left_alone(self):
        self.write("A.md", "A", "## Критический угол ^crit-angle")
        self.assertEqual(self.findings("A.md", "anchor-unused"), [])

    def test_anchor_linked_in_another_case_is_used(self):
        self.write("A.md", "A", "Определение ^def-1")
        self.write("B.md", "B", "[[A#^DEF-1|определение]]")
        self.assertEqual(self.findings("A.md", "anchor-unused"), [])

    def test_anchor_linked_through_a_folder_path_is_used(self):
        self.write("x/A.md", "A", "Определение ^def")
        self.write("B.md", "B", "[[x/A#^def|определение]]")
        self.assertEqual(self.findings("x/A.md", "anchor-unused"), [])

    def test_anchor_of_a_second_note_with_the_same_name_is_used(self):
        self.write("x/A.md", "A", "Тело")
        self.write("y/A.md", "A", "Определение ^def")
        self.write("B.md", "B", "[[y/A#^def|определение]]")
        self.assertEqual(self.findings("y/A.md", "anchor-unused"), [])

    def test_escaped_label_pipe_in_a_callout_table_still_resolves_the_note(self):
        # A table inside a callout starts with ">", so a row is not recognised by
        # the line's first character — the escape is the same one either way
        self.write("A.md", "A", "тело")
        self.write("B.md", "B", "> [!note] Т\n> | Что | Где |\n> | --- | --- |\n"
                                "> | Тело | [[A\\|заметка A]] |")
        self.assertEqual(self.findings("B.md", "broken-link"), [])


class TablesInCallouts(TempVault):
    def findings(self, body, code):
        p = self.vault / "A.md"
        p.write_text(NOTE_TMPL.format(title="A", body=body, extra=""), encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(p, idx, out)
        return [f.msg for f in out if f.code == code]

    def test_unescaped_label_pipe_inside_a_callout_table_is_flagged(self):
        # a row of a table inside a callout starts with ">", and the pipe breaks it
        # there exactly as it does at the top level
        self.assertEqual(len(self.findings("> [!note] Т\n> | Что | Где |\n> | --- | --- |\n"
                                           "> | Тело | [[B|заметка]] |", "table-pipe")), 1)

    def test_unescaped_label_pipe_inside_a_nested_callout_table_is_flagged(self):
        self.assertEqual(len(self.findings("> [!note] Т\n> > [!tip] В\n> > | Что | Где |\n"
                                           "> > | --- | --- |\n> > | Тело | [[B|заметка]] |",
                                           "table-pipe")), 1)

    def test_escaped_label_pipe_inside_a_callout_table_is_left_alone(self):
        self.assertEqual(self.findings("> [!note] Т\n> | Что | Где |\n> | --- | --- |\n"
                                       "> | Тело | [[B\\|заметка]] |", "table-pipe"), [])

    def test_escaped_pipe_does_not_split_a_header_cell_into_fake_ones(self):
        # "[[B\|заметка]]" is one cell; splitting on the escaped pipe would leave
        # "заметка]]" looking like a lowercase header of its own
        self.assertEqual(self.findings("| Что | [[B\\|заметка]] |\n| --- | --- |\n| Тело | x |",
                                       "table-header-case"), [])


class CalloutNoBlank(TempVault):
    """A callout head opens a callout only when the line above it is shallower. Obsidian
    keeps a quote open across a line of the same or a greater depth, the bare ">" one
    included, and renders the second [!type] as text of the first callout"""

    findings = TablesInCallouts.findings

    def flagged(self, body):
        return len(self.findings(body, "callout-no-blank"))

    def test_callout_right_after_a_line_of_the_same_level_is_flagged(self):
        self.assertEqual(self.flagged("> [!note] A\n> текст\n> [!tip] B\n> тело"), 1)

    def test_bare_marker_line_does_not_close_the_callout(self):
        self.assertEqual(self.flagged("> [!note] A\n> текст\n>\n> [!tip] B\n> тело"), 1)

    def test_nested_callout_after_an_empty_line_of_its_own_level_is_flagged(self):
        self.assertEqual(self.flagged("> [!note] A\n>\n> > [!tip] X\n> > x\n> >\n"
                                      "> > [!tip] Y\n> > y"), 1)

    def test_callout_after_a_deeper_line_is_flagged(self):
        self.assertEqual(self.flagged("> [!note] A\n>\n> > [!tip] X\n> > x\n> [!tip] B"), 1)

    def test_callout_after_a_closing_fence_inside_the_callout_is_flagged(self):
        self.assertEqual(self.flagged("> [!note] A\n> ```\n> код\n> ```\n> [!tip] B"), 1)

    def test_callouts_split_by_a_blank_line_are_left_alone(self):
        self.assertEqual(self.flagged("> [!note] A\n> текст\n\n> [!tip] B\n> тело"), 0)

    def test_nested_callouts_split_by_the_parent_level_line_are_left_alone(self):
        self.assertEqual(self.flagged("> [!note] A\n>\n> > [!tip] X\n> > x\n>\n"
                                      "> > [!tip] Y\n> > y"), 0)

    def test_nested_callout_right_after_parent_text_is_not_this_check(self):
        # one level deeper opens a new quote; whether it wants a separator is
        # nested-callout-no-blank's question
        self.assertEqual(self.flagged("> [!note] A\n> текст\n> > [!tip] X\n> > x"), 0)

    def test_callout_syntax_shown_in_a_code_block_is_left_alone(self):
        self.assertEqual(self.flagged("```markdown\n> [!note] A\n> текст\n> [!tip] B\n```"), 0)


class NestedCalloutSeparator(TempVault):
    """Obsidian renders a nested callout right after the parent's text as a callout.
    The separator line ">" before it is house style for a readable source, so the
    check is a hint for a human, not a certain defect"""

    findings = TablesInCallouts.findings

    def flagged(self, body):
        return len(self.findings(body, "nested-callout-no-blank"))

    def test_nested_callout_right_after_parent_text_is_flagged(self):
        self.assertEqual(self.flagged("> [!note] A\n> текст\n> > [!tip] X\n> > x"), 1)

    def test_nested_callout_after_the_separator_is_left_alone(self):
        self.assertEqual(self.flagged("> [!note] A\n> текст\n>\n> > [!tip] X\n> > x"), 0)

    def test_the_check_is_a_style_hint(self):
        self.assertEqual(lint.CHECKS["nested-callout-no-blank"][0], lint.SUSPECT)


def words(n, word="слово"):
    return " ".join([word] * n)


class ProseLength(TempVault):
    """Paragraph and caption limits come from SKILL.md, not from constants in the test.
    The limit binds conspects (lectures and papers), not zettels, hubs or the diary"""

    def findings(self, body, code, preset="lecture"):
        p = self.vault / "A.md"
        p.write_text(NOTE_TMPL.format(title="A", body=body, extra="").replace("preset: zettel",
                                                                              f"preset: {preset}"),
                     encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(p, idx, out)
        return [f.msg for f in out if f.code == code]

    def test_paragraph_over_the_limit_is_flagged(self):
        self.assertEqual(len(self.findings(words(lint.PARAGRAPH_MAX_WORDS + 1), "paragraph-long")), 1)

    def test_paragraph_at_the_limit_is_left_alone(self):
        self.assertEqual(self.findings(words(lint.PARAGRAPH_MAX_WORDS), "paragraph-long"), [])

    def test_inline_formula_counts_as_one_word(self):
        # "$a + b = c$" is one token on the page, not five
        body = words(lint.PARAGRAPH_MAX_WORDS - 1) + " $a + b = c$"
        self.assertEqual(self.findings(body, "paragraph-long"), [])

    def test_long_line_inside_a_callout_is_a_paragraph_too(self):
        self.assertEqual(len(self.findings("> [!note] Т\n> " + words(lint.PARAGRAPH_MAX_WORDS + 1),
                                           "paragraph-long")), 1)

    def test_link_with_a_timecode_anchor_counts_only_its_label(self):
        # the anchor copies the heading's "[05 50](https //…)", single brackets included
        link = "[[B#Теорема [05 50](https //www.youtube.com/watch?v=ID&t=350s)|теорема]]"
        body = words(lint.PARAGRAPH_MAX_WORDS - 1) + " " + link
        self.assertEqual(self.findings(body, "paragraph-long"), [])

    def test_footnotes_tables_and_code_are_not_paragraphs(self):
        long = words(lint.PARAGRAPH_MAX_WORDS + 20)
        body = f"Текст[^a]\n\n[^a]: {long}\n\n| Что | Где |\n| --- | --- |\n| {long} | x |\n\n```\n{long}\n```"
        self.assertEqual(self.findings(body, "paragraph-long"), [])

    def test_caption_over_its_limit_is_flagged_as_caption(self):
        body = "![[pic.png]]\n\n" + words(lint.CAPTION_MAX_WORDS + 1)
        self.assertEqual(len(self.findings(body, "caption-long")), 1)
        self.assertEqual(self.findings(body, "paragraph-long"), [])

    def test_caption_at_its_limit_is_left_alone(self):
        self.assertEqual(self.findings("![[pic.png]]\n\n" + words(lint.CAPTION_MAX_WORDS), "caption-long"), [])

    def test_paragraph_after_a_caption_is_not_a_caption(self):
        body = "![[pic.png]]\n\nПодпись\n\n" + words(lint.CAPTION_MAX_WORDS + 1)
        self.assertEqual(self.findings(body, "caption-long"), [])

    def test_a_long_paper_paragraph_is_flagged(self):
        self.assertEqual(len(self.findings(words(lint.PARAGRAPH_MAX_WORDS + 1), "paragraph-long",
                                           preset="paper")), 1)

    def test_zettel_is_not_bound_by_the_limit(self):
        self.assertEqual(self.findings(words(lint.PARAGRAPH_MAX_WORDS + 1), "paragraph-long",
                                       preset="zettel"), [])

    def test_limits_are_read_from_the_skill(self):
        skill = (lint.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f"не длиннее {lint.PARAGRAPH_MAX_WORDS} слов", skill)
        self.assertIn(f"не длиннее {lint.CAPTION_MAX_WORDS}", skill)


class ProvenanceNote(TempVault):
    """A note is not a session report: "taken from memory" and its kin are flagged for a look"""

    findings = ProseLength.findings

    def test_from_memory_in_prose_is_flagged(self):
        self.assertEqual(len(self.findings("Версия взята по памяти", "provenance-note")), 1)

    def test_unverified_mark_in_a_footnote_is_flagged(self):
        body = "Текст[^v]\n\n[^v]: Год приведён без сверки с источником"
        self.assertEqual(len(self.findings(body, "provenance-note")), 1)

    def test_added_during_digitization_is_flagged(self):
        body = "Текст[^e]\n\n[^e]: Не из лекции: пример добавлен при оцифровке"
        self.assertEqual(len(self.findings(body, "provenance-note")), 1)

    def test_checked_by_script_is_flagged(self):
        body = "Текст[^e]\n\n[^e]: Не из лекции: таблица проверена скриптом"
        self.assertEqual(len(self.findings(body, "provenance-note")), 1)

    def test_exhaustive_proof_is_left_alone(self):
        # checking all cases is a proof method, not a trace of the session
        self.assertEqual(self.findings("Равенство проверено перебором всех наборов", "provenance-note"), [])

    def test_not_rechecked_is_flagged(self):
        self.assertEqual(len(self.findings("IP не логируется (не перепроверено)", "provenance-note")), 1)

    def test_mark_in_a_table_cell_is_flagged(self):
        body = "| Версия | Год |\n| --- | --- |\n| 15.0 | 2010, не сверено |"
        self.assertEqual(len(self.findings(body, "provenance-note")), 1)

    def test_mark_inside_a_callout_is_flagged(self):
        self.assertEqual(len(self.findings("> [!note] Т\n> Значение по памяти", "provenance-note")), 1)

    def test_plain_prose_is_left_alone(self):
        self.assertEqual(self.findings("Индекс нагружает запись и память", "provenance-note"), [])

    def test_code_span_is_left_alone(self):
        self.assertEqual(self.findings("Строка `grep -r \"по памяти\"` ищет пометки", "provenance-note"), [])

    def test_diary_is_left_alone(self):
        self.assertEqual(self.findings("Рисовал по памяти", "provenance-note", preset="diary"), [])


class StudyProcess(TempVault):
    """A conspect keeps the knowledge, not the course logistics: exams, homework, tests"""

    findings = ProseLength.findings

    def test_exam_in_prose_is_flagged(self):
        self.assertEqual(len(self.findings("На экзамене их путают", "study-process", preset="lecture")), 1)

    def test_homework_heading_is_flagged(self):
        self.assertEqual(len(self.findings("### Домашнее задание", "study-process", preset="lecture")), 1)

    def test_test_paper_in_a_callout_is_flagged(self):
        body = "> [!note] Т\n> Такие задачи будут в контрольной работе"
        self.assertEqual(len(self.findings(body, "study-process", preset="lecture")), 1)

    def test_left_to_exercises_is_flagged(self):
        self.assertEqual(len(self.findings("Лектор оставляет разбор на упражнения", "study-process",
                                           preset="lecture")), 1)

    def test_next_lecture_is_flagged(self):
        self.assertEqual(len(self.findings("Критерий — на следующей лекции", "study-process",
                                           preset="lecture")), 1)

    def test_exercise_as_a_task_is_left_alone(self):
        # an exercise in the note itself is content, not course logistics
        self.assertEqual(self.findings("Упражнение: доказать лемму", "study-process", preset="lecture"), [])

    def test_points_are_flagged(self):
        self.assertEqual(len(self.findings("Решение даёт два балла", "study-process", preset="lecture")), 1)

    def test_gas_cylinder_is_left_alone(self):
        self.assertEqual(self.findings("Газ выпустили из баллона", "study-process", preset="lecture"), [])

    def test_checksum_is_left_alone(self):
        self.assertEqual(self.findings("Контрольная сумма кадра", "study-process", preset="lecture"), [])

    def test_hub_is_left_alone(self):
        # an event hub about a session may talk about its exams
        self.assertEqual(self.findings("Сдал экзамен", "study-process", preset="hub-event"), [])


class SandboxLine(TempVault):
    """One interactive page gets one ▶ line per note, whatever the preset"""

    findings = ProseLength.findings
    LINE = "▶ [[knn-песочница.html|Песочница kNN]] — можно {}"

    def test_same_page_twice_is_flagged_once(self):
        body = "\n\n".join([self.LINE.format("крутить k"), "## Б", self.LINE.format("щёлкать")])
        self.assertEqual(len(self.findings(body, "sandbox-dup")), 1)

    def test_two_different_pages_are_fine(self):
        body = self.LINE.format("крутить k") + "\n\n" + \
            "▶ [[tree-песочница.html|Песочница дерева]] — можно крутить глубину"
        self.assertEqual(self.findings(body, "sandbox-dup"), [])

    def test_plain_link_to_the_same_page_is_not_a_second_line(self):
        body = self.LINE.format("крутить k") + "\n\nсм. [[knn-песочница.html|песочницу]]"
        self.assertEqual(self.findings(body, "sandbox-dup"), [])

    def test_duplicate_in_a_zettel_is_flagged_too(self):
        body = self.LINE.format("а") + "\n\n" + self.LINE.format("б")
        self.assertEqual(len(self.findings(body, "sandbox-dup", preset="zettel")), 1)


class HiddenFolders(TempVault):
    """Obsidian does not index a folder whose name starts with a dot, so neither does lint"""

    def test_note_in_a_dot_folder_is_not_indexed(self):
        self.touch("Курс/.sources/README.md")
        self.touch("Курс/A.md")
        idx = lint.Index()
        idx.build()
        self.assertIn("A", idx.notes)
        self.assertNotIn("README", idx.notes)

    def test_file_in_a_dot_folder_is_hidden_but_a_plain_note_is_not(self):
        self.assertTrue(lint.obsidian_hidden(self.vault / "Курс/.sources/figures/x.md"))
        self.assertFalse(lint.obsidian_hidden(self.vault / "Курс/content/x.md"))

    def test_dots_above_the_vault_do_not_hide_it(self):
        lint.VAULT = self.vault / ".vaults" / "wiki"
        self.assertFalse(lint.obsidian_hidden(lint.VAULT / "Курс/x.md"))


class ExplicitOnlyFolders(TempVault):
    """The diary and the Inbox are parsed only when a path inside them is named"""

    DIARY = f"{lint.DIARY_ROOT}/01. Daily/2026-01-01 Thursday.md"
    INBOX = f"{lint.INBOX_ROOT}/Черновик.md"
    NEAR = "02. Zettelkasten/01. Inbox старый/Мысль.md"

    def select(self, labels):
        rels = [self.DIARY, self.INBOX, self.NEAR, "Курс/A.md"]
        kept, skipped = lint.select_targets([self.vault / r for r in rels], labels)
        return {p.relative_to(self.vault).as_posix() for p in kept}, skipped

    def test_whole_vault_run_skips_diary_and_inbox(self):
        kept, skipped = self.select([])
        self.assertEqual(kept, {self.NEAR, "Курс/A.md"})
        self.assertEqual(skipped, {lint.DIARY_ROOT: 1, lint.INBOX_ROOT: 1})

    def test_parent_folder_does_not_count_as_naming_the_inbox(self):
        kept, _ = self.select(["02. Zettelkasten"])
        self.assertNotIn(self.INBOX, kept)

    def test_naming_the_inbox_parses_it_and_still_skips_the_diary(self):
        kept, skipped = self.select([lint.INBOX_ROOT])
        self.assertIn(self.INBOX, kept)
        self.assertEqual(skipped, {lint.DIARY_ROOT: 1})

    def test_naming_one_inbox_note_parses_it(self):
        kept, _ = self.select([self.INBOX])
        self.assertIn(self.INBOX, kept)


class AnchorBroken(TempVault):
    """A link to #Heading or #^block must land on a heading or block of the target note.
    Obsidian compares both sides after stripHeading: the punctuation it lists becomes a
    space, runs of spaces collapse, and the case is ignored"""

    findings = AnchorRefs.findings

    def write(self, rel, body):
        AnchorRefs.write(self, rel, pathlib.Path(rel).stem, body)

    def broken(self, target_body, link):
        # lint caches every file it reads; a second call in one test rewrites the same paths
        lint._cache.clear()
        lint._targets.clear()
        self.write("A.md", target_body)
        self.write("B.md", link)
        return self.findings("B.md", "anchor-broken")

    def test_link_to_an_existing_heading_is_fine(self):
        self.assertEqual(self.broken("## Закон Гука", "[[A#Закон Гука|закон]]"), [])

    def test_link_to_a_missing_heading_is_flagged(self):
        self.assertEqual(len(self.broken("## Закон Гука", "[[A#Закон Ома|закон]]")), 1)

    def test_heading_case_does_not_matter(self):
        self.assertEqual(self.broken("## Закон Гука", "[[A#закон гука]]"), [])

    def test_timecode_heading_linked_in_the_form_obsidian_writes(self):
        # Obsidian writes ':' as a space in the link, and keeps the slashes
        head = "## Теорема Пуассона [05:50](https://www.youtube.com/watch?v=ID&t=350s)"
        link = "[[A#Теорема Пуассона [05 50](https //www.youtube.com/watch?v=ID&t=350s)|теорема]]"
        self.assertEqual(self.broken(head, link), [])

    def test_timecode_heading_linked_without_its_timecode_is_flagged(self):
        head = "## Теорема Пуассона [05:50](https://www.youtube.com/watch?v=ID&t=350s)"
        self.assertEqual(len(self.broken(head, "[[A#Теорема Пуассона|теорема]]")), 1)

    def test_link_with_a_stale_timecode_is_flagged(self):
        # the brackets of the timecode are inside the link, which still ends at the first ]]
        head = "## Теорема Пуассона [05:50](https://www.youtube.com/watch?v=ID&t=350s)"
        link = "[[A#Теорема Пуассона [05 51](https //www.youtube.com/watch?v=ID&t=351s)|теорема]]"
        self.assertEqual(len(self.broken(head, link)), 1)

    def test_backslash_of_a_latex_command_becomes_a_space(self):
        head = "## Случай $\\frac{\\infty}{\\infty}$"
        self.assertEqual(self.broken(head, "[[A#Случай $ frac{ infty}{ infty}$|случай]]"), [])
        self.assertEqual(self.broken(head, "[[A#Случай $\\frac{\\infty}{\\infty}$|случай]]"), [])

    def test_literal_formula_may_be_dropped_to_its_digits(self):
        self.assertEqual(self.broken("## Несчётность отрезка $[0, 1]$",
                                     "[[A#Несчётность отрезка 0 1|отрезок]]"), [])

    def test_latex_command_is_not_folded_into_its_argument(self):
        self.assertEqual(len(self.broken("## Счётность $\\mathbb{Q}$", "[[A#Счётность Q|Q]]")), 1)

    def test_nested_heading_path_resolves(self):
        self.assertEqual(self.broken("## Силы\n\n### Трение", "[[A#Силы#Трение|трение]]"), [])

    def test_nested_heading_path_in_the_wrong_order_is_flagged(self):
        self.assertEqual(len(self.broken("## Силы\n\n### Трение", "[[A#Трение#Силы|трение]]")), 1)

    def test_link_to_an_existing_block_is_fine_in_any_case(self):
        self.assertEqual(self.broken("> [!note] Определение ^Def-1", "[[A#^DEF-1|определение]]"), [])

    def test_link_to_a_missing_block_is_flagged(self):
        self.assertEqual(len(self.broken("> [!note] Определение ^def-1", "[[A#^def-2|опр]]")), 1)

    def test_block_id_with_a_character_obsidian_rejects_is_not_a_block(self):
        self.assertEqual(len(self.broken("Абзац ^my_id", "[[A#^my_id|абзац]]")), 1)

    def test_escaped_label_pipe_in_a_table_still_resolves(self):
        self.assertEqual(self.broken("## Закон Гука",
                                     "| Что | Где |\n| --- | --- |\n| Закон | [[A#Закон Гука\\|закон]] |"), [])
        self.assertEqual(self.broken("Закон Гука ^hooke",
                                     "| Что | Где |\n| --- | --- |\n| Закон | [[A#^hooke\\|закон]] |"), [])

    def test_self_link_checks_the_note_itself(self):
        self.write("A.md", "## Есть\n\n[[A#Есть|тут]] и [[#Нет|там]]")
        self.assertEqual(len(self.findings("A.md", "anchor-broken")), 1)

    def test_embed_of_a_missing_section_is_flagged(self):
        self.assertEqual(len(self.broken("## Закон Гука", "![[A#Закон Ома]]")), 1)

    def test_missing_note_is_left_to_broken_link(self):
        self.write("B.md", "[[Нет такой#Раздел|крючок]]")
        self.assertEqual(self.findings("B.md", "anchor-broken"), [])

    def test_heading_inside_a_code_fence_is_not_a_heading(self):
        self.assertEqual(len(self.broken("```\n## Закон Гука\n```", "[[A#Закон Гука]]")), 1)

    def test_link_inside_code_is_not_a_link(self):
        self.assertEqual(self.broken("## Есть", "`[[A#Нет]]`\n\n```\n[[A#Нет]]\n```"), [])

    def test_pdf_page_anchor_is_not_a_heading(self):
        self.touch("Учебник.pdf")
        self.write("B.md", "[[Учебник.pdf#page=3|стр. 3]]")
        self.assertEqual(self.findings("B.md", "anchor-broken"), [])

    def test_note_named_twice_resolves_if_either_copy_has_the_heading(self):
        self.write("x/A.md", "## Первый")
        self.write("y/A.md", "## Второй")
        self.write("B.md", "[[A#Второй]]")
        self.assertEqual(self.findings("B.md", "anchor-broken"), [])

    def test_folder_path_picks_that_copy(self):
        self.write("x/A.md", "## Первый")
        self.write("y/A.md", "## Второй")
        self.write("B.md", "[[x/A#Второй]]")
        self.assertEqual(len(self.findings("B.md", "anchor-broken")), 1)


class LinkResolution(TempVault):
    """A link resolves the way Obsidian's getLinkpathDest does: a name whose last part
    has a dot is first looked up as a file of the vault with any extension, and only then
    as a note with ".md" added; a folder in the link narrows the match by the path's tail,
    and "./" or "../" counts from the folder of the linking note"""

    findings = AnchorRefs.findings

    def write(self, rel, body):
        lint._cache.clear()
        AnchorRefs.write(self, rel, pathlib.Path(rel).stem, body)

    def test_link_to_an_html_page_in_the_attachments_resolves(self):
        self.touch("Курс/00. Вложения/knn-песочница.html")
        self.write("Курс/content/kNN.md", "▶ [[knn-песочница.html|Песочница kNN]]")
        self.assertEqual(self.findings("Курс/content/kNN.md", "broken-link"), [])

    def test_link_to_a_missing_html_page_is_flagged(self):
        self.write("B.md", "▶ [[нет-песочница.html|Песочница]]")
        self.assertEqual(len(self.findings("B.md", "broken-link")), 1)

    def test_any_extension_resolves_not_only_html(self):
        self.touch("00. Вложения/train.py")
        self.write("B.md", "[[train.py|скрипт]]")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_file_name_case_does_not_matter(self):
        self.touch("00. Вложения/knn-песочница.html")
        self.write("B.md", "[[KNN-песочница.HTML|песочница]]")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_note_with_a_dot_in_its_name_resolves(self):
        self.write("f01. Введение.md", "тело")
        self.write("B.md", "[[f01. Введение|введение]]")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_folder_path_to_a_note_resolves(self):
        self.write("x/A.md", "тело")
        self.write("B.md", "[[x/A|заметка]]")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_folder_path_to_the_wrong_folder_is_flagged(self):
        self.write("x/A.md", "тело")
        self.write("B.md", "[[y/A|заметка]]")
        self.assertEqual(len(self.findings("B.md", "broken-link")), 1)

    def test_leading_slash_means_the_vault_root(self):
        self.write("x/A.md", "тело")
        self.write("B.md", "[[/x/A|от корня]] и [[/A|не от корня]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["/A"])

    def test_relative_path_counts_from_the_linking_note(self):
        self.write("x/A.md", "тело")
        self.write("x/sub/B.md", "[[../A|заметка]]")
        self.assertEqual(self.findings("x/sub/B.md", "broken-link"), [])

    def test_relative_path_picks_the_copy_beside_the_linking_note(self):
        # Only the copy in y has the heading; "../A" from x/sub means x/A, so the anchor is broken
        self.write("x/A.md", "тело")
        self.write("y/A.md", "## Есть")
        self.write("x/sub/B.md", "[[../A#Есть|раздел]]")
        self.assertEqual(len(self.findings("x/sub/B.md", "anchor-broken")), 1)

    def test_dot_slash_path_picks_the_copy_in_the_linking_note_folder(self):
        self.write("x/A.md", "тело")
        self.write("y/A.md", "## Есть")
        self.write("x/B.md", "[[./A#Есть|раздел]]")
        self.assertEqual(len(self.findings("x/B.md", "anchor-broken")), 1)

    def test_anchor_on_an_html_page_is_not_a_heading(self):
        self.touch("p.html")
        self.write("B.md", "[[p.html#demo|страница]]")
        self.assertEqual(self.findings("B.md", "anchor-broken"), [])

    def test_missing_image_is_a_missing_attachment_not_a_broken_link(self):
        self.write("B.md", "![[нет.png]]")
        self.assertEqual(len(self.findings("B.md", "missing-attachment")), 1)
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_image_under_a_folder_it_does_not_live_in_is_missing(self):
        self.touch("Курс/00. Вложения/a.png")
        self.write("B.md", "![[Другой/00. Вложения/a.png]]")
        self.assertEqual(len(self.findings("B.md", "missing-attachment")), 1)


class LinksInsideFormulas(TempVault):
    """Obsidian reads a line left to right: what opens first owns the text. "$[[A]]=[A]$"
    is a formula with brackets in it, "[[A#Случай $x$]]" is a link with a formula in its anchor"""

    findings = AnchorRefs.findings
    write = LinkResolution.write

    def test_brackets_inside_inline_math_are_not_a_link(self):
        self.write("B.md", "Замыкание $[[A]]=[A]$ и $$[[B]]$$ рядом")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_brackets_inside_a_math_block_are_not_a_link(self):
        for body in ["$$\n[[A]] = [A]\n$$", "> $$\n> [[A]]\n> $$", "$$\\begin{aligned} x\n[[A]]\n\\end{aligned}$$"]:
            with self.subTest(body=body):
                self.write("B.md", body)
                self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_link_after_a_formula_is_still_a_link(self):
        self.write("B.md", "Пусть $x$ и [[Нет такой]]\n\n$$\nx\n$$\n[[Тоже нет]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["Нет такой", "Тоже нет"])

    def test_formula_inside_a_link_anchor_does_not_hide_the_link(self):
        self.write("B.md", "[[Нет такой#Случай $x$|случай]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["Нет такой"])

    def test_dollar_inside_a_link_does_not_pair_with_one_after_it(self):
        # the link opens first and owns its "$"; read math-first, "$|цена]] — формула $" would eat it
        self.write("B.md", "[[Нет такой#Цена в $|цена]] — формула $x$")
        self.assertEqual(self.findings("B.md", "broken-link"), ["Нет такой"])

    def test_unpaired_dollar_is_currency_not_a_formula(self):
        self.write("B.md", "Стоит ~$5 в месяц, см. [[Нет такой]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["Нет такой"])

    def test_anchor_inside_a_formula_is_not_checked(self):
        self.write("A.md", "## Есть")
        self.write("B.md", "$[[A#Нет]]$")
        self.assertEqual(self.findings("B.md", "anchor-broken"), [])


class NavChain(TempVault):
    """prev/next resolve the way every other link does — Index.link_dests"""

    findings = AnchorRefs.findings

    def write(self, rel, extra):
        lint._cache.clear()
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        stem = pathlib.Path(rel).stem
        p.write_text(NOTE_TMPL.format(title=stem, body="тело", extra=extra), encoding="utf-8")

    def test_chain_written_in_another_case_resolves(self):
        self.write("A.md", 'next: "[[b]]"\n')
        self.write("B.md", 'prev: "[[a]]"\n')
        self.assertEqual(self.findings("A.md", "chain-broken"), [])
        self.assertEqual(self.findings("B.md", "chain-broken"), [])

    def test_chain_written_with_a_folder_path_resolves(self):
        self.write("x/A.md", 'next: "[[x/B]]"\n')
        self.write("x/B.md", 'prev: "[[x/A|назад]]"\n')
        self.assertEqual(self.findings("x/A.md", "chain-broken"), [])
        self.assertEqual(self.findings("x/B.md", "chain-broken"), [])

    def test_chain_to_a_missing_note_is_still_broken(self):
        self.write("A.md", 'next: "[[Нет такой]]"\n')
        self.assertEqual(len(self.findings("A.md", "chain-broken")), 1)

    def test_one_way_chain_is_still_broken(self):
        self.write("A.md", 'next: "[[B]]"\n')
        self.write("B.md", 'prev: "[[C]]"\n')
        self.write("C.md", "")
        self.assertEqual(len(self.findings("A.md", "chain-broken")), 1)

    def test_back_link_to_a_same_named_note_elsewhere_is_broken(self):
        self.write("x/A.md", 'next: "[[B]]"\n')
        self.write("y/A.md", "")
        self.write("B.md", 'prev: "[[y/A]]"\n')
        self.assertEqual(len(self.findings("x/A.md", "chain-broken")), 1)

    def test_relative_up_counts_from_the_note(self):
        # "../MOC" from x/sub means x/MOC, which does not exist; the root MOC is another note
        self.write("MOC.md", "")
        self.write("x/sub/A.md", 'up: "[[../MOC]]"\n')
        self.assertEqual(len(self.findings("x/sub/A.md", "up-broken")), 1)


class AliasIsNotALinkTarget(TempVault):
    """Obsidian resolves a link by file name only: getFirstLinkpathDest("NVML") is null
    for a note that lists NVML in its aliases. An alias feeds search and the "[[" suggestion,
    which writes [[File|alias]]; a bare [[alias]] is an unresolved link"""

    findings = AnchorRefs.findings

    def write(self, rel, body, extra=""):
        lint._cache.clear()
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        stem = pathlib.Path(rel).stem
        p.write_text(NOTE_TMPL.format(title=stem, body=body, extra=extra), encoding="utf-8")

    def setUp(self):
        super().setUp()
        self.write("Графический стек.md", "тело", extra="aliases:\n  - NVML\n")

    def test_bare_alias_link_is_broken(self):
        self.write("B.md", "[[NVML]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["NVML"])

    def test_alias_link_in_another_case_is_broken_too(self):
        self.write("B.md", "[[nvml|NVML]]")
        self.assertEqual(self.findings("B.md", "broken-link"), ["nvml"])

    def test_file_link_with_the_alias_as_label_resolves(self):
        self.write("B.md", "[[Графический стек|NVML]]")
        self.assertEqual(self.findings("B.md", "broken-link"), [])

    def test_up_through_an_alias_is_broken(self):
        self.write("B.md", "тело", extra='up: "[[NVML]]"\n')
        self.assertEqual(len(self.findings("B.md", "up-broken")), 1)

    def test_superseded_by_through_an_alias_is_broken(self):
        self.write("B.md", "тело", extra='status: superseded\nsuperseded_by: "[[NVML]]"\n')
        self.assertEqual(len(self.findings("B.md", "superseded-by-broken")), 1)


class CalloutTitleLabel(TempVault):
    findings = ProseLength.findings

    def test_definition_of_the_label_word_is_not_a_label(self):
        self.assertEqual(self.findings("> [!note] Наблюдение — это исследование явления без "
                                       "создания специальных условий", "callout-title-label"), [])

    def test_label_before_a_dash_is_still_flagged(self):
        self.assertEqual(len(self.findings("> [!tip] Следствие — ряд сходится абсолютно",
                                           "callout-title-label")), 1)

    def test_label_before_a_quoted_name_is_still_flagged(self):
        self.assertEqual(len(self.findings('> [!tip] Рецепт "Делим на старшую степень"',
                                           "callout-title-label")), 1)


class MocSort(TempVault):
    """Dataview compares the quoted lecture numbers as strings, so "10" sorts before "9"""

    findings = ProseLength.findings

    def query(self, sort):
        return f"```dataview\nTABLE summary\nWHERE up = this.file.link\n{sort}\n```"

    def test_string_sort_on_lectures_is_flagged(self):
        self.assertEqual(len(self.findings(self.query("SORT lectures ASC, file.name ASC"),
                                           "moc-sort-lectures", preset="lecture-moc")), 1)

    def test_numeric_sort_on_the_first_lecture_is_fine(self):
        self.assertEqual(self.findings(self.query("SORT number(lectures[0]) ASC, file.name ASC"),
                                       "moc-sort-lectures", preset="lecture-moc"), [])

    def test_sort_outside_a_dataview_block_is_not_a_query(self):
        self.assertEqual(self.findings("Пример: `SORT lectures ASC`", "moc-sort-lectures",
                                       preset="lecture-moc"), [])

    def test_template_in_the_preset_uses_the_numeric_sort(self):
        preset = (lint.SKILL_DIR / "presets/lecture.md").read_text(encoding="utf-8")
        self.assertIn("SORT number(lectures[0]) ASC", preset)
        self.assertNotRegex(preset, r"SORT lectures\b")


class Tags(TempVault):
    """A tag is a property several notes share and nothing else derives: not a year, not the
    note's own name or alias, not the group of one sub-MOC (SKILL.md → ### Теги)"""

    def write(self, rel, tags=None, extra="", preset="zettel"):
        lint._cache.clear()
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        head = "---\ncreated: 2026-01-01\n"
        if preset:
            head += f"preset: {preset}\n"
        if tags is not None:
            head += "tags:\n" + "".join(f"  - {t}\n" for t in tags)
        p.write_text(head + extra + "---\n# T\nтело\n", encoding="utf-8")

    def findings(self, rel, code):
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(self.vault / rel, idx, out)
        return [f.msg for f in out if f.code == code]

    def test_year_tag_is_no_longer_a_check(self):
        self.assertNotIn("tags-no-year", lint.CHECKS)

    def test_no_preset_requires_tags(self):
        for name, spec in lint.PRESETS.items():
            self.assertNotIn("tags", spec["required"], name)

    def test_zettel_without_tags_misses_no_field(self):
        self.write("Z.md")
        self.assertEqual(self.findings("Z.md", "fm-field-missing"), [])

    # tag-is-alias: a tag that sits only on the note(s) it names adds no property
    def test_tag_only_on_the_note_it_names_by_file_name_is_flagged(self):
        self.write("Предел функции.md", ["предел-функции"])
        self.assertEqual(len(self.findings("Предел функции.md", "tag-is-alias")), 1)

    def test_tag_only_on_the_two_notes_it_names_is_flagged(self):
        self.write("A.md", ["закон_ома"], extra="aliases:\n  - Закон Ома\n")
        self.write("B.md", ["закон_ома"], extra="aliases:\n  - закон ома\n")
        self.assertEqual(len(self.findings("A.md", "tag-is-alias")), 1)

    def test_crosscutting_tag_on_its_owner_and_others_is_silent(self):
        self.write("Ом.md", ["закон_ома"], extra="aliases:\n  - Закон Ома\n")
        self.write("B.md", ["закон_ома"])
        self.assertEqual(self.findings("Ом.md", "tag-is-alias"), [])
        self.assertEqual(self.findings("B.md", "tag-is-alias"), [])

    def test_tag_naming_another_note_but_carried_by_others_is_silent(self):
        self.write("Ом.md", extra="aliases:\n  - Закон Ома\n")
        self.write("B.md", ["закон_ома"])
        self.assertEqual(self.findings("B.md", "tag-is-alias"), [])

    def test_tag_equal_to_own_alias_is_flagged(self):
        self.write("B.md", ["свертка"], extra="aliases:\n  - Свёртка\n")
        self.assertEqual(len(self.findings("B.md", "tag-is-alias")), 1)

    def test_tag_naming_no_note_is_fine(self):
        self.write("B.md", ["кфу"])
        self.assertEqual(self.findings("B.md", "tag-is-alias"), [])

    def test_excalidraw_tag_is_never_reported(self):
        self.write("Excalidraw.md")
        self.write("B.md", ["excalidraw"])
        for code in ("tag-is-alias", "tag-singleton", "tags-multiword"):
            self.assertEqual(self.findings("B.md", code), [], code)

    # tag-singleton
    def test_tag_on_one_note_is_a_singleton(self):
        self.write("A.md", ["одинокий"])
        self.assertEqual(len(self.findings("A.md", "tag-singleton")), 1)

    def test_tag_on_two_notes_is_not_a_singleton(self):
        self.write("A.md", ["общий"])
        self.write("B.md", ["общий"])
        self.assertEqual(self.findings("A.md", "tag-singleton"), [])

    def test_diary_use_counts_but_a_diary_singleton_is_not_reported(self):
        diary = f"{lint.DIARY_ROOT}/01. Daily/2026-01-01 Thursday.md"
        self.write(diary, ["грустно", "одинокий"], preset=None)
        self.write("A.md", ["грустно"])
        self.assertEqual(self.findings("A.md", "tag-singleton"), [])
        self.assertEqual(self.findings(diary, "tag-singleton"), [])

    # tag-variant
    def test_tags_differing_by_ending_are_variants(self):
        self.write("A.md", ["предел"])
        self.write("B.md", ["пределы"])
        self.assertEqual(len(self.findings("A.md", "tag-variant")), 1)

    def test_tags_differing_by_separator_or_yo_are_variants(self):
        self.write("A.md", ["теория_обучения", "свёртка"])
        self.write("B.md", ["теория-обучения", "свертка"])
        self.assertEqual(len(self.findings("A.md", "tag-variant")), 2)

    def test_unrelated_tags_are_not_variants(self):
        self.write("A.md", ["сети", "сон"])
        self.write("B.md", ["сети"])
        self.assertEqual(self.findings("A.md", "tag-variant"), [])

    # tag-mirrors-moc
    def moc_group(self, members=("A", "B", "C")):
        self.write("M.md", preset="lecture-moc")
        for m in members:
            self.write(f"{m}.md", extra='up: "[[M]]"\n', preset="lecture")

    def tag_on(self, tag, notes):
        for n in notes:
            p = self.vault / f"{n}.md"
            text = p.read_text(encoding="utf-8")
            p.write_text(text.replace("---\n# T", f"tags:\n  - {tag}\n---\n# T", 1), encoding="utf-8")
        lint._cache.clear()

    def test_tag_on_the_whole_group_is_flagged_on_the_moc(self):
        self.moc_group()
        self.tag_on("тема", ["M", "A", "B", "C"])
        self.assertEqual(len(self.findings("M.md", "tag-mirrors-moc")), 1)
        self.assertEqual(self.findings("A.md", "tag-mirrors-moc"), [])

    def test_tag_on_the_group_without_one_note_is_flagged(self):
        self.moc_group()
        self.tag_on("тема", ["A", "B", "C"])
        self.assertEqual(len(self.findings("M.md", "tag-mirrors-moc")), 1)

    def test_tag_on_the_moc_and_one_note_is_flagged(self):
        self.moc_group(("A", "B", "C", "D"))
        self.tag_on("тема", ["M", "A"])
        self.assertEqual(len(self.findings("M.md", "tag-mirrors-moc")), 1)

    def test_tag_reaching_outside_the_group_is_fine(self):
        self.moc_group()
        self.write("X.md", ["тема"])
        self.tag_on("тема", ["M", "A", "B", "C"])
        self.assertEqual(self.findings("M.md", "tag-mirrors-moc"), [])

    def test_tag_on_the_moc_and_a_note_outside_is_fine(self):
        self.moc_group()
        self.write("X.md", ["тема"])
        self.tag_on("тема", ["M"])
        self.assertEqual(self.findings("M.md", "tag-mirrors-moc"), [])

    def test_group_of_an_up_written_in_another_case_is_the_moc_group(self):
        # up resolves the way every link does, case aside
        self.write("M.md", preset="lecture-moc")
        for m in ("A", "B", "C"):
            self.write(f"{m}.md", extra='up: "[[m]]"\n', preset="lecture")
        self.tag_on("тема", ["M", "A", "B", "C"])
        self.assertEqual(len(self.findings("M.md", "tag-mirrors-moc")), 1)

    def test_tag_on_part_of_a_big_group_is_fine(self):
        self.moc_group(("A", "B", "C", "D", "E"))
        self.tag_on("тема", ["A", "B"])
        self.assertEqual(self.findings("M.md", "tag-mirrors-moc"), [])

    # tags-multiword: the form
    def test_capital_hyphen_and_space_break_the_form(self):
        self.write("A.md", ["Максвелл", "bias-variance", "to be", "интеграл_с_параметром", "🪑"])
        self.assertEqual(len(self.findings("A.md", "tags-multiword")), 3)


class AliasNumber(TempVault):
    """An alias names one concept, and a bare number names none (SKILL.md → ### Связность)"""

    def aliases(self, *values):
        lint._cache.clear()
        items = "".join(f"  - {v}\n" for v in values)
        (self.vault / "A.md").write_text(f"---\ncreated: 2026-01-01\npreset: zettel\naliases:\n{items}---\n# T\nтело\n",
                                         encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(self.vault / "A.md", idx, out)
        return [f.msg for f in out if f.code == "alias-number"]

    def test_bare_integer_year_and_decimal_are_flagged(self):
        self.assertEqual(len(self.aliases("3", '"2024"', "0.5", "1,5")), 4)

    def test_identifiers_that_contain_digits_are_fine(self):
        self.assertEqual(self.aliases("127.0.0.1", "0000-00-00", "802.1Q", "1NF", "area 0", "RFC 4787"), [])


class AbbrevNotes(TempVault):
    """Notes with aliases and the findings one code gives on one of them"""

    def write(self, rel, body, aliases=(), preset="zettel", title=None):
        lint._cache.clear()
        items = "".join(f"  - {a}\n" for a in aliases)
        extra = f"aliases:\n{items}" if aliases else ""
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        text = NOTE_TMPL.format(title=title or pathlib.Path(rel).stem, body=body, extra=extra)
        p.write_text(text.replace("preset: zettel", f"preset: {preset}"), encoding="utf-8")

    def findings(self, rel, code):
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(self.vault / rel, idx, out)
        return [f.msg for f in out if f.code == code]


class AbbrevOwnership(AbbrevNotes):
    """An abbreviation is decoded once, by its owner note, and goes into its aliases;
    homonyms are two owners with unrelated expansions (SKILL.md → ### Тон и пунктуация).
    no_alias writes a term note, which owns every decoding, so abbrev-no-alias shows
    which phrases count as a decoding"""

    def no_alias(self, body):
        self.write("A.md", body, preset="term")
        return self.findings("A.md", "abbrev-no-alias")

    def test_capitalised_latin_expansion_needs_an_alias(self):
        self.assertEqual(len(self.no_alias("**NVML** (NVIDIA Management Library) — библиотека")), 1)
        self.write("A.md", "**NVML** (NVIDIA Management Library) — библиотека", aliases=["NVML"], preset="term")
        self.assertEqual(self.findings("A.md", "abbrev-no-alias"), [])

    # A passing decoding is not ownership: only a note that owns the concept takes the alias.
    # Ownership signs: a term note, the abbreviation or its phrase in the file name, H1 or
    # title, or the decoding inside a [!note] callout
    def passing(self, body, rel="A.md", **kw):
        self.write(rel, body, **kw)
        return self.findings(rel, "abbrev-no-alias")

    def test_passing_decoding_needs_no_alias(self):
        self.assertEqual(self.passing("Контроллер ведёт **DMA** (Direct Memory Access) без процессора"), [])
        self.assertEqual(self.passing("> [!tip] Обход\n> Через **DMA** (Direct Memory Access) быстрее"), [])

    def test_owner_by_name_needs_the_alias(self):
        body = "Контроллер ведёт **DMA** (Direct Memory Access) без процессора"
        self.assertEqual(len(self.passing(body, rel="Контроллер DMA.md")), 1)
        self.assertEqual(len(self.passing(body, title="Прямой доступ к памяти (DMA)")), 1)
        self.assertEqual(len(self.passing(body, title="Direct Memory Access")), 1)
        # a token inside a longer word is not the abbreviation
        self.assertEqual(self.passing(body, title="Режим DMAX"), [])

    def test_owner_by_defining_note_callout_needs_the_alias(self):
        self.assertEqual(len(self.passing("> [!note] **DMA** (Direct Memory Access) — доступ без процессора")), 1)
        self.assertEqual(len(self.passing("> [!note] Определение\n>\n> - **DMA** (Direct Memory Access) — доступ")), 1)
        # a [!note] nested in another callout still owns; a [!tip] around it does not make it passing
        self.assertEqual(len(self.passing("> [!tip] Обход\n>\n> > [!note] **DMA** (Direct Memory Access)")), 1)
        # the decoding after the callout ended is outside it
        self.assertEqual(self.passing("> [!note] Определение\n> Доступ\n\nЧерез **DMA** (Direct Memory Access)"), [])
        # and after a nested [!note] ended, the line is back in the outer callout
        self.assertEqual(self.passing("> [!tip] Обход\n>\n> > [!note] Определение\n> > Доступ\n>\n"
                                      "> Через **DMA** (Direct Memory Access) быстрее"), [])

    def test_term_note_owns_its_decoding(self):
        self.assertEqual(len(self.passing("Контроллер ведёт **DMA** (Direct Memory Access)", preset="term")), 1)

    def test_lowercase_expansion_counts_when_its_initials_spell_the_abbreviation(self):
        self.assertEqual(len(self.no_alias("Нужен **PAT** (personal access token) с правом push")), 1)

    def test_lowercase_phrase_with_other_initials_is_not_an_expansion(self):
        self.assertEqual(self.no_alias("Нужен **PAT** (see the settings page) с правом push"), [])

    def test_cyrillic_expansion_counts_when_its_initials_spell_the_abbreviation(self):
        self.assertEqual(len(self.no_alias("**ОДУ** (обыкновенное дифференциальное уравнение) — связь")), 1)
        self.assertEqual(len(self.no_alias("**ЭВМ** — электронно-вычислительная машина первого поколения")), 1)

    def test_cyrillic_emphasis_is_not_an_expansion(self):
        self.assertEqual(self.no_alias("Это **НЕ** работает без питания, проверено"), [])

    def test_expansion_before_the_abbreviation_counts(self):
        self.assertEqual(len(self.no_alias("**Вольт-амперная характеристика** (ВАХ) — зависимость тока")), 1)
        self.assertEqual(len(self.no_alias("Метод наименьших квадратов (**МНК**) минимизирует риск")), 1)
        self.assertEqual(len(self.no_alias("Протокол **Transmission Control Protocol** (TCP) надёжен")), 1)

    def test_words_before_parenthesised_capitals_need_matching_initials(self):
        self.assertEqual(self.no_alias("Флаги заголовка (**DF**) и прочее"), [])

    def test_expansion_before_the_bracket_must_end_at_it(self):
        # the initials are spelled earlier, but the bracket closes another phrase
        self.assertEqual(self.no_alias("Полевой транзистор греет диод (ПТ) снизу"), [])

    def test_capitalised_expansion_in_the_next_table_cell_counts(self):
        # "Hypertext" carries two letters, so only the capitalised-phrase form catches it
        self.assertEqual(len(self.no_alias("| **HTTP** | Hypertext Transfer Protocol | порт 80 |")), 1)

    def test_bold_term_that_starts_with_an_abbreviation_is_not_its_expansion(self):
        self.assertEqual(self.no_alias("> [!note] **AS External LSA** — ASBR вносит внешний маршрут"), [])
        self.assertEqual(self.no_alias("**TCP Fast Open** (TFO) — данные прямо в SYN"),
                         ["TFO расшифрована здесь, но не в aliases"])

    def test_footnote_mark_does_not_hide_the_expansion_after_it(self):
        body = "| **PCP**[^pcp] | Port Control Protocol | RFC 6887 |\n\n[^pcp]: Не путать с тегом 802.1Q"
        self.assertEqual(len(self.no_alias(body)), 1)

    def test_single_letter_with_a_digit_is_not_spelled_out(self):
        self.assertEqual(self.no_alias("Пять коэффициентов **K1–K5** (K-values) задают вклад"), [])

    def test_quoted_source_is_a_citation_not_a_decoding(self):
        self.assertEqual(self.no_alias('Глава "Programming with the Streaming SIMD Extensions (SSE)" описывает'), [])
        self.assertEqual(self.no_alias('Datasheet: "A clock signal row address strobe (RAS) strobes in a row"'), [])

    def test_abbreviation_in_inline_code_can_be_decoded_too(self):
        self.assertEqual(len(self.no_alias("| `NS` (name server) | какие серверы авторитетны за зону |")), 1)

    def test_code_followed_by_other_code_or_prose_is_not_decoded(self):
        self.assertEqual(self.no_alias("| `REFERENCES` (`FOREIGN KEY`) | ссылка на строку |"), [])
        self.assertEqual(self.no_alias("коммит на каждый `PUT` через Contents API"), [])

    def test_russian_suffix_before_a_lowercase_expansion(self):
        self.assertEqual(len(self.no_alias("Поэтому **SPA**-приложения (single page application) хранили")), 1)

    def test_expansion_in_the_next_table_cell_counts(self):
        self.assertEqual(len(self.no_alias("| **PCP** | Port Control Protocol | RFC 6887 |")), 1)

    def test_word_then_shortened_form_counts(self):
        self.assertEqual(self.no_alias("Между сетями стоит **firewall** (сокращённо **FW**)"), ["FW расшифрована здесь, но не в aliases"])

    def test_passing_decoding_of_an_owned_abbreviation_is_a_redecoding(self):
        self.write("A.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.write("B.md", "Резолвер **DNS** (Domain Name Service) спрашивает корень")
        msgs = self.findings("B.md", "abbrev-redecoded")
        self.assertEqual(len(msgs), 1)
        self.assertIn("A.md", msgs[0])
        # the owner keeps its decoding; the passing one is what goes
        self.assertEqual(self.findings("A.md", "abbrev-redecoded"), [])

    def test_owner_by_sign_without_an_alias_is_still_the_owner(self):
        self.write("A.md", "> [!note] **DNS** (Domain Name System) — имена")
        self.write("B.md", "Резолвер **DNS** (Domain Name Service) спрашивает корень")
        self.assertEqual(len(self.findings("B.md", "abbrev-redecoded")), 1)

    def test_two_passing_decodings_without_an_owner_are_not_a_redecoding(self):
        self.write("A.md", "Резолвер **DNS** (Domain Name System) спрашивает корень")
        self.write("B.md", "Кэш **DNS** (Domain Name System) держит ответ")
        self.assertEqual(self.findings("A.md", "abbrev-redecoded") + self.findings("B.md", "abbrev-redecoded"), [])

    def test_unrelated_expansions_in_two_notes_are_homonyms(self):
        self.write("A.md", "Флаг **CE** (Congestion Experienced) в IP-заголовке", aliases=["CE"])
        self.write("B.md", "Маршрутизатор **CE** (Customer Edge) у клиента", aliases=["CE"])
        self.assertEqual(self.findings("A.md", "abbrev-redecoded"), [])
        self.assertEqual(self.findings("A.md", "alias-collision"), [])
        self.assertEqual(self.findings("B.md", "alias-collision"), [])

    # An abbreviation alias may repeat only as a homonym: every holder decodes it, and the
    # phrases share no word (SKILL.md → ### Связность); a word or a phrase never repeats
    def collisions(self, rel):
        return self.findings(rel, "alias-collision")

    def test_shared_alias_of_one_expansion_still_collides(self):
        self.write("A.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.write("B.md", "**DNS** (Domain Name System) — тоже имена", aliases=["DNS"])
        self.assertEqual(len(self.collisions("A.md")), 1)
        self.assertEqual(len(self.collisions("B.md")), 1)
        self.assertEqual(len(self.findings("B.md", "abbrev-redecoded")), 1)

    def test_alias_holder_that_decodes_nothing_still_collides_with_owner(self):
        self.write("A.md", "**ПК** (прямой код) хранит знак отдельно", aliases=["ПК"])
        self.write("B.md", "План сборки компьютера", aliases=["ПК"])
        self.assertEqual(len(self.collisions("A.md")), 1)
        self.assertEqual(len(self.collisions("B.md")), 1)

    def test_three_holders_collide_only_with_the_one_that_does_not_decode(self):
        self.write("A.md", "Флаг **CE** (Congestion Experienced) в IP-заголовке", aliases=["CE"])
        self.write("B.md", "Маршрутизатор **CE** (Customer Edge) у клиента", aliases=["CE"])
        self.write("C.md", "Про CE тут ни слова расшифровки", aliases=["CE"])
        for rel in ["A.md", "B.md"]:
            msgs = self.collisions(rel)
            self.assertEqual(len(msgs), 1)
            self.assertIn("C.md", msgs[0])
        self.assertEqual(len(self.collisions("C.md")), 1)

    def test_abbreviation_pair_alias_is_an_abbreviation_too(self):
        self.write("A.md", "Ток **AC/DC** (Alternating Current / Direct Current) — оба вида", aliases=["AC/DC"])
        self.write("B.md", "Группа **AC/DC** (Australian Rock Band / Hard Rock Group) — концерт", aliases=["AC/DC"])
        self.assertEqual(self.collisions("A.md") + self.collisions("B.md"), [])

    def test_word_alias_in_two_notes_collides(self):
        self.write("A.md", "Топология сети", aliases=["шина"])
        self.write("B.md", "Компьютерная шина", aliases=["шина"])
        self.assertEqual(len(self.collisions("A.md")), 1)
        self.assertEqual(len(self.collisions("B.md")), 1)

    def test_phrase_alias_and_file_name_collide(self):
        self.write("A.md", "Колебания", aliases=["Математический маятник"])
        self.write("Математический маятник.md", "Схема")
        self.assertEqual(len(self.collisions("A.md")), 1)

    def test_capitalised_token_in_the_prose_dictionary_is_still_an_abbreviation(self):
        # not-abbreviations.txt answers "no decoding needed in prose", not "not an abbreviation"
        for alias, a, b in [("SELECT", "Synchronous Event Logic", "Secure Element Locking"),
                            ("CS", "Carrier Sense", "Chip Select")]:
            with self.subTest(alias=alias):
                self.write("A.md", f"Первая **{alias}** ({a}) заметка", aliases=[alias])
                self.write("B.md", f"Вторая **{alias}** ({b}) заметка", aliases=[alias])
                self.assertEqual(self.collisions("B.md"), [])

    # Each case below is a homonym by its phrases, so only the form check makes it collide
    def test_capitalised_token_that_is_not_an_abbreviation_by_form_collides(self):
        for alias, a, b in [("RX1", "Receive Exchange", "Rapid Xenon"),
                            ("XIV", "Xenon Ion Valve", "Extra Index Vector")]:
            with self.subTest(alias=alias):
                self.write("A.md", f"Первая **{alias}** ({a}) заметка", aliases=[alias])
                self.write("B.md", f"Вторая **{alias}** ({b}) заметка", aliases=[alias])
                self.assertEqual(len(self.collisions("B.md")), 1)

    def test_russian_capitals_written_as_a_word_in_the_vault_collide(self):
        self.write("A.md", "Это важно помнить, **ВАЖНО** (верхний арочный жёлоб нижней опоры)", aliases=["ВАЖНО"])
        self.write("B.md", "Пометка **ВАЖНО** (внешний адаптер журнала новых операций)", aliases=["ВАЖНО"])
        self.assertEqual(len(self.collisions("B.md")), 1)

    def test_abbreviation_written_lowercase_in_one_note_collides(self):
        # only the capitalised spelling is an abbreviation; "пк" is a word-form alias
        self.write("A.md", "**ПК** (прямой код) хранит знак", aliases=["ПК"])
        self.write("B.md", "Сборка **ПК** (персональный компьютер)", aliases=["пк"])
        self.assertEqual(len(self.collisions("B.md")), 1)

    # A latin abbreviation is decoded in its own language; a Russian translation may stand
    # beside it, but alone it is a translation, not a decoding (SKILL.md, [^abbr-forms])
    def translated(self, body):
        self.write("A.md", body)
        return [m for m in self.findings("A.md", "abbrev-undecoded") if "переведена" in m]

    def test_russian_translation_alone_is_not_a_decoding(self):
        for body in ["**TLB** (буфер ассоциативной трансляции) кэширует",
                     "**Распределённая транзакция** (XA) делает коммит",
                     "| Блок трансляции адреса (TLB) — раздельно | Адрес |",
                     "> - Общий принцип дисперсионного анализа (ANOVA) — разбиение"]:
            with self.subTest(body=body):
                self.assertEqual(self.no_alias(body), [])
                self.assertEqual(len(self.translated(body)), 1, "перевод есть — находка просит латинскую фразу")

    def test_latin_expansion_beside_a_translation_is_recognised(self):
        for body in ["**TLB** (Translation Lookaside Buffer, буфер ассоциативной трансляции) кэширует",
                     "**Блок трансляции адреса** (**TLB** — Translation Lookaside Buffer) кэширует"]:
            with self.subTest(body=body):
                self.assertEqual(len(self.no_alias(body)), 1)
                self.assertEqual(self.findings("A.md", "abbrev-undecoded"), [])

    def test_latin_phrase_does_not_decode_a_cyrillic_abbreviation(self):
        self.assertEqual(self.no_alias("Первая **ЭВМ** (Electronic Computing Machine) — ламповая"), [])

    def test_translation_before_a_bracket_needs_the_bracket_to_itself(self):
        # a list in the bracket is examples of the phrase, not its abbreviation
        self.assertEqual(self.translated("| `0x9E3779B9` | Золотое сечение (TEA, xxHash) | приманка |"), [])

    def test_lowercase_fragment_opening_an_item_is_not_a_term(self):
        self.assertEqual(self.translated("Методы:\n\n- численного моделирования (FDTD)"), [])

    def test_link_label_pipe_is_not_a_table_cell(self):
        self.assertEqual(self.translated("Буфер ROB мал\n\nИнструмент — "
                                         "[[P6#Структура|Блок изменения последовательности команд (ROB)]] Intel"), [])

    def test_russian_translation_in_running_prose_has_no_boundary(self):
        # "Без анализатора цепей" — where would the term start? Only bold or a cell start pins it
        self.assertEqual(self.translated("Без анализатора цепей (VNA) перестраивать антенну вслепую"), [])
        self.assertEqual(self.translated("Он работает на канальном уровне (MAC) и выше"), [])

    def test_latin_phrase_beyond_a_closed_bracket_is_not_an_expansion(self):
        self.assertEqual(self.no_alias("Глагол **V2** (форма прошедшего) идёт в Past Simple"), [])

    def test_russian_remark_in_brackets_is_not_a_translation(self):
        for body in ["Её корень **RMSE** (в исходных единицах отклика) читается",
                     "Лог в формате **CSV** (нужен включённый коллектор) пишет",
                     "Вариант **E2** (умолчание Cisco) не растит метрику",
                     "Глагол **V2** (форма прошедшего) идёт в Past Simple",
                     "Память **MRAM** (магниторезистивная) энергонезависима",
                     "Режим **RR** (регистр — регистр) короче"]:
            with self.subTest(body=body):
                self.assertEqual(self.translated(body), [])

    def test_cyrillic_expansion_may_take_letters_from_inside_a_compound_word(self):
        self.assertEqual(len(self.no_alias("Работает **АЭС** (атомная электростанция) на уране")), 1)
        self.assertEqual(len(self.no_alias("Стержни называются **ТВЭЛ** (тепловыделяющий элемент)")), 1)
        self.assertEqual(len(self.no_alias("Ещё **МОП** (металл–оксид–полупроводник) структура")), 1)

    def test_letters_inside_a_camel_case_word_count(self):
        self.assertEqual(len(self.no_alias("**CommonJS** (CJS) — модули Node.js")), 1)
        self.assertEqual(len(self.no_alias("Схема теста — **AAA** (Arrange–Act–Assert): подготовь")), 1)

    def test_word_in_capitals_does_not_spell_an_abbreviation_from_inside(self):
        # "PMC" is the abbreviation itself, and "PMC11446842" is an identifier, not an expansion
        self.assertEqual(self.no_alias("Источник — база PMC (PMC11446842), конспект"), [])
        self.assertEqual(len(self.findings("A.md", "abbrev-undecoded")), 1)

    def test_one_word_does_not_spell_two_letters(self):
        self.assertEqual(self.no_alias("Режим **ОС** (основной) включён"), [])

    def test_cyrillic_partial_name_is_not_an_expansion(self):
        self.assertEqual(self.no_alias("Состояние **ОМВП** (очень малая) и дальше"), [])

    def test_single_latin_word_gives_no_letter_evidence(self):
        self.assertEqual(self.no_alias("Пара на передачу (**TX**, transmitter) и приём"), [])

    def test_slash_compound_is_decoded_as_one_abbreviation(self):
        body = "Дорога — **CI/CD** (Continuous Integration / Continuous Deployment): push публикует"
        self.assertEqual(self.no_alias(body), ["CI/CD расшифрована здесь, но не в aliases"])
        self.write("A.md", body, aliases=["CI/CD"], preset="term")
        self.assertEqual(self.findings("A.md", "abbrev-no-alias"), [])

    def test_translation_and_expansion_of_one_mention_are_one_decoding(self):
        for body in ["| жёсткий диск (**HDD**, Hard Disk Drive) | 20 мс |",
                     "**Unique Local** (**ULA**, Unique Local Address) — для сетей без интернета"]:
            with self.subTest(body=body):
                self.write("A.md", body)
                self.assertEqual(self.findings("A.md", "abbrev-redecoded"), [])

    def test_second_decoding_inside_one_note_is_still_reported(self):
        self.write("A.md", "**DNS** (Domain Name System) — имена\n\nИ снова **DNS** (Domain Name System)",
                   aliases=["DNS"])
        self.assertEqual(len(self.findings("A.md", "abbrev-redecoded")), 1)


class AbbrevUndecoded(AbbrevNotes):
    """A bare abbreviation needs a decoding here or a link to the note that decodes it
    (SKILL.md → ### Тон и пунктуация)"""

    def undecoded(self, body, rel="A.md"):
        self.write(rel, body)
        return self.findings(rel, "abbrev-undecoded")

    def test_bare_abbreviation_without_any_owner_is_flagged(self):
        msgs = self.undecoded("Пакеты идут через MMU процессора")
        self.assertEqual(len(msgs), 1)
        self.assertIn("MMU", msgs[0])

    def test_bare_abbreviation_with_an_owner_elsewhere_names_the_owner(self):
        self.write("Owner.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        msgs = self.undecoded("Резолвер спрашивает DNS о домене")
        self.assertEqual(len(msgs), 1)
        self.assertIn("Owner", msgs[0])

    def test_alias_holder_counts_as_owner_even_without_a_detected_decoding(self):
        self.write("Термин.md", "Сеть доставки контента", aliases=["CDN"])
        msgs = self.undecoded("Статика лежит в CDN")
        self.assertEqual(len(msgs), 1)
        self.assertIn("Термин", msgs[0])

    def test_owner_by_sign_without_an_alias_is_offered_for_the_link(self):
        self.write("Owner.md", "> [!note] **DMA** (Direct Memory Access) — доступ без процессора")
        msgs = self.undecoded("Шина ждёт DMA")
        self.assertEqual(len(msgs), 1)
        self.assertIn("[[Owner|DMA]]", msgs[0])

    def test_passing_decoding_elsewhere_is_not_offered_as_the_owner(self):
        # a link to a note that only mentions the term would make it a formal owner
        self.write("Other.md", "Контроллер ведёт **DMA** (Direct Memory Access) без процессора")
        msgs = self.undecoded("Шина ждёт DMA")
        self.assertEqual(len(msgs), 1)
        self.assertNotIn("[[", msgs[0])
        self.assertIn("Other", msgs[0])
        self.assertIn("00. Термины", msgs[0])

    def test_owned_finding_offers_the_link_and_unowned_offers_none(self):
        self.write("Owner.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.assertIn("[[Owner|DNS]]", self.undecoded("Резолвер спрашивает DNS о домене")[0])
        self.assertNotIn("[[", self.undecoded("Пакеты идут через MMU процессора")[0])

    def test_first_mention_as_a_link_is_fine(self):
        self.write("Owner.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.assertEqual(self.undecoded("Резолвер спрашивает [[Owner|DNS]], потом DNS кэширует"), [])
        self.assertEqual(self.undecoded("Таблица | [[Owner\\|DNS]] | и DNS снова |"), [])

    def test_link_after_a_bare_first_mention_does_not_clear_it(self):
        self.write("Owner.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.assertEqual(len(self.undecoded("Сначала DNS голым\n\nПотом [[Owner|DNS]] ссылкой")), 1)

    def test_spelled_decoding_without_bold_counts_as_a_decoding(self):
        self.assertEqual(self.undecoded("- ЗФО (Защитная Фильтрующая Одежда)"), [])
        self.assertEqual(self.undecoded("заменил FID (First Input Delay), который мерял"), [])
        self.assertEqual(self.undecoded("Метод наименьших квадратов (МНК) минимизирует"), [])

    def test_translated_abbreviation_asks_for_the_phrase_in_its_own_language(self):
        msgs = self.undecoded("Сначала TLB голым\n\n**TLB** (буфер ассоциативной трансляции) кэширует")
        self.assertEqual(len(msgs), 1)
        self.assertIn("буфер ассоциативной трансляции", msgs[0])
        self.assertIn("на языке аббревиатуры", msgs[0])

    def test_alias_holder_with_only_a_translation_is_asked_for_the_phrase(self):
        self.write("A.md", "| Блок трансляции адреса (TLB) | Адрес |", aliases=["TLB"])
        msgs = self.findings("A.md", "abbrev-undecoded")
        self.assertEqual(len(msgs), 1)
        self.assertIn("на языке аббревиатуры", msgs[0])
        self.write("A.md", "| Блок трансляции адреса (TLB, Translation Lookaside Buffer) | Адрес |",
                   aliases=["TLB"])
        self.assertEqual(self.findings("A.md", "abbrev-undecoded"), [])

    def test_alias_holder_is_asked_for_the_phrase_even_when_another_note_decodes_it(self):
        # the alias claims ownership, so the note owes the phrase rather than a link
        self.write("Owner.md", "**TLB** (Translation Lookaside Buffer) — кэш")
        self.write("A.md", "| Блок трансляции адреса (TLB) | Адрес |", aliases=["TLB"])
        msgs = self.findings("A.md", "abbrev-undecoded")
        self.assertEqual(len(msgs), 1)
        self.assertIn("на языке аббревиатуры", msgs[0])

    def test_translated_abbreviation_with_an_owner_still_asks_for_the_link(self):
        self.write("Owner.md", "**TLB** (Translation Lookaside Buffer) — кэш", aliases=["TLB"])
        msgs = self.undecoded("**TLB** (буфер ассоциативной трансляции) кэширует")
        self.assertEqual(len(msgs), 1)
        self.assertIn("[[Owner|TLB]]", msgs[0])

    def test_slash_compound_decoding_covers_its_parts(self):
        self.assertEqual(self.undecoded("**CI/CD** (Continuous Integration / Continuous Deployment): "
                                        "потом CI собирает, CD выкладывает"), [])

    def test_slash_compound_alias_covers_its_parts(self):
        self.write("A.md", "Доступ CSMA и обнаружение CD", aliases=["CSMA/CD"])
        self.assertEqual(self.findings("A.md", "abbrev-undecoded"), [])

    def test_alias_that_is_not_an_abbreviation_pair_covers_no_parts(self):
        self.write("A.md", "Без MPLS и BGP, со скоростью в MT", aliases=["BGP/MPLS IP VPN", "MT/s"])
        self.assertEqual(len(self.findings("A.md", "abbrev-undecoded")), 3)

    def test_code_span_with_two_dollars_does_not_open_a_math_block(self):
        self.assertEqual(len(self.undecoded("Вызов `$$(\"a\")` в консоли\n\nПотом MMU голым")), 1)

    def test_plain_phrase_after_a_bare_abbreviation_is_not_its_decoding(self):
        self.assertEqual(len(self.undecoded("Трафик идёт через VPN, Cloudflare Workers и прокси")), 1)

    def test_link_inside_a_quote_still_counts_as_a_link(self):
        self.write("Owner.md", "**DNS** (Domain Name System) — имена", aliases=["DNS"])
        self.assertEqual(self.undecoded('Лектор: "спроси [[Owner|DNS]]", потом DNS кэширует'), [])

    def test_decoding_anywhere_in_the_note_clears_it(self):
        self.assertEqual(self.undecoded("Сначала MMU голым\n\nПотом **MMU** (Memory Management Unit) — блок"), [])

    def test_note_holding_the_alias_is_its_owner(self):
        self.write("A.md", "Пакеты идут через MMU процессора", aliases=["MMU"])
        self.assertEqual(self.findings("A.md", "abbrev-undecoded"), [])

    def test_one_finding_per_abbreviation_at_its_first_mention(self):
        self.write("A.md", "Строка\n\nТут MMU\n\nИ снова MMU и MMU")
        out = []
        idx = lint.Index()
        idx.build()
        lint.check_note(self.vault / "A.md", idx, out)
        lines = [f.line for f in out if f.code == "abbrev-undecoded"]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 12)

    def test_russian_suffix_after_a_hyphen_is_still_the_abbreviation(self):
        self.assertEqual(len(self.undecoded("Пришёл MMU-запрос и ЭДС-источник")), 2)

    def test_cyrillic_abbreviation_is_flagged(self):
        self.assertEqual(len(self.undecoded("Источник даёт ЭДС в цепь")), 1)

    def test_letter_digit_letter_abbreviation_is_flagged(self):
        self.assertEqual(len(self.undecoded("Сеть P2P без сервера")), 1)

    def test_markup_contexts_are_not_prose(self):
        # one context per note: a mention leaking from any of them must turn the test red
        for body in [
            "## Заголовок про MMU",
            "> ### Заголовок в callout про MMU",
            "Код `MMU` и формула $MMU$ и эмбед ![[MMU.png]]",
            "```\nMMU in code\n```",
            "> $$\n> \\frac{HS}{MMU}\n> \\end{aligned}$$",
            "$$\\begin{aligned} MMU\nx \\end{aligned}$$",
            "Сайт https://x.org/MMU и [текст](https://y.org/MMU)",
            '<span class="e">НАСРАТЬ MMU</span> рядом',
            'Цитата "The MMU translates" из даташита',
            "The cache sits behind the MMU and every core shares it",
        ]:
            with self.subTest(body=body):
                self.assertEqual(self.undecoded(body), [])

    def test_prose_after_a_closed_math_block_is_prose_again(self):
        self.assertEqual(len(self.undecoded("$$\nx\n$$\nПотом MMU")), 1)

    def test_frontmatter_is_not_prose(self):
        self.write("A.md", "Текст", aliases=["Про MMU"])
        self.assertEqual(self.findings("A.md", "abbrev-undecoded"), [])

    def test_identifiers_with_digits_and_roman_numerals_are_not_abbreviations(self):
        self.assertEqual(self.undecoded("Ключ SW1 и резистор R1 на RP2040, век XIV, тип II, порт DNS-01"), [])

    def test_compound_with_latin_continuation_is_one_identifier(self):
        self.assertEqual(self.undecoded("Режим IA-32e включается битом"), [])

    def test_listed_non_abbreviations_are_skipped(self):
        self.assertEqual(self.undecoded("Запрос SELECT с ORDER BY, регистр EAX и RAX, сигнал SIGTERM, 2 ГБ"), [])

    def test_the_skip_list_lives_in_one_file(self):
        self.assertTrue(lint.NOT_ABBREV_FILE.is_file())
        self.assertTrue(any(p.fullmatch("SELECT") for p in lint.NOT_ABBREVIATIONS))

    def test_capitalised_russian_word_used_in_lowercase_too_is_emphasis(self):
        self.assertEqual(self.undecoded("Это НЕ работает, а то, что не работает, — чинить"), [])

    def test_hyphenated_russian_words_in_capitals_are_emphasis(self):
        self.assertEqual(self.undecoded("Вентиль ИЛИ-НЕ: или, а потом не"), [])

    def test_external_link_text_is_a_cited_title(self):
        self.assertEqual(self.undecoded("Данные — [Отчёт NOAA [v2] о грозах](https://x.org/a) за год"), [])

    def test_long_russian_word_written_lowercase_elsewhere_is_emphasis(self):
        self.write("B.md", "Это очень важно")
        self.assertEqual(self.undecoded("Он ОЧЕНЬ много думает"), [])

    def test_short_russian_abbreviation_is_not_cleared_by_a_lowercase_word_elsewhere(self):
        self.write("B.md", "Укусила ос")
        self.assertEqual(len(self.undecoded("Ядро ОС грузится первым")), 1)

    def test_table_cell_holding_only_identifiers_is_a_key(self):
        self.assertEqual(self.undecoded("| EBX | BX, BH | BPU | Блок обработки ветвлений |"), [])
        self.assertEqual(len(self.undecoded("| Блок | Кэш-память и MMU для данных |")), 1)

    def test_hex_bytes_and_active_low_signals_are_not_abbreviations(self):
        self.assertEqual(self.undecoded("Байты C5 E8 58 CB и сигналы RESET#, PERST# на шине"), [])

    def test_tl_dr_is_an_idiom(self):
        self.assertEqual(self.undecoded("> [!abstract] TL;DR"), [])

    def test_diary_is_free_even_when_named(self):
        rel = f"{lint.DIARY_ROOT}/01. Daily/2026-01-01 Thursday.md"
        self.write(rel, "Сегодня MMU и СДЭК")
        p = self.vault / rel
        p.write_text(p.read_text(encoding="utf-8").replace("preset: zettel\n", ""), encoding="utf-8")
        self.assertEqual(self.findings(rel, "abbrev-undecoded"), [])

    def test_diary_note_does_not_own_an_abbreviation(self):
        self.write(f"{lint.DIARY_ROOT}/01. Daily/2026-01-01 Thursday.md", "день", aliases=["MMU"])
        msgs = self.undecoded("Пакеты идут через MMU процессора")
        self.assertEqual(len(msgs), 1)
        self.assertNotIn("Thursday", msgs[0])


class AbbrevNotAnAbbreviation(AbbrevNotes):
    """Capitals that are not an abbreviation, places where no decoding is owed, and
    decodings in a less common form (SKILL.md, [^abbr-skip] and [^abbr-forms])"""

    def undecoded(self, body, rel="A.md"):
        self.write(rel, body)
        return self.findings(rel, "abbrev-undecoded")

    # Words in capitals: emphasis, not an abbreviation

    def test_inflected_word_in_capitals_matches_its_lowercase_stem(self):
        self.write("B.md", "Раковина в ванной и перетаскивать окна")
        self.assertEqual(self.undecoded("Он полез в РАКОВИНУ и сам ПЕРЕТАСКИВАЛ окна"), [])

    def test_abbreviation_without_an_ending_is_not_cleared_by_a_stem(self):
        # "гости" stems to "гост", but ГОСТ has no ending to strip
        self.write("B.md", "Пришли гости")
        self.assertEqual(len(self.undecoded("Стандарт ГОСТ задаёт размер")), 1)

    def test_capitalised_word_counts_as_the_written_word(self):
        self.write("B.md", "Окей, поехали")
        self.assertEqual(self.undecoded("НУ, вот. Ну, ОКЕЙ, приехали"), [])

    def test_short_russian_function_words_and_numerals_are_emphasis(self):
        self.assertEqual(self.undecoded("Фиксировать ДВА сустава, при переломе бедра ТРИ, "
                                        "и всё ДО приезда врачей"), [])

    def test_short_abbreviation_that_looks_like_a_function_word_is_flagged(self):
        self.assertEqual(len(self.undecoded("Поставить ПО на сервер")), 1)

    # Names, units, formulas

    def test_listed_names_and_word_like_abbreviations_are_skipped(self):
        self.assertEqual(self.undecoded("Пишут в VS Code, поле Connection ID и Tx ID, ответ 200 OK, "
                                        "линия HIGH или LOW, ON/OFF, версия MAJOR и MINOR, "
                                        "регистры ST(0) и R8D, команды LOAD/STORE и WRITE(10), префикс LOCK, команды ADC, ADDPD и PHADDW"), [])

    def test_capitalised_latin_neighbour_does_not_make_a_name(self):
        # "CTO Amazon" is a role at a company, "Europe PMC" a name: the form cannot tell them apart
        self.assertEqual(len(self.undecoded("Приезжал CTO Amazon, данные из Europe PMC")), 2)

    def test_unit_and_chemical_formula_are_not_abbreviations(self):
        self.assertEqual(self.undecoded("Около $0{,}4$ МН, угарный газ CO и OH-группы"), [])

    def test_ampersand_joins_one_name(self):
        self.assertEqual(self.undecoded("Процессор AT&T Hobbit"), [])

    # Bibliography

    def test_reference_list_item_is_not_prose(self):
        for body in ["- Ward 1973, PNAS — ранняя гипотеза",
                     "- Sui et al. 2024, WSDM'24",
                     "- Butler и др., ECCV 2012 — датасет Sintel, DOI 10.1007/978-3-642-33783-3_44",
                     "- Butler и др., ECCV 2012 — датасет Sintel, [[DOI]] 10.1007/978-3-642-33783-3_44",
                     "> - Iino и Yoshida 2009, PNAS",
                     "[^d]: P. J. Denning, Communications of the ACM, vol. 48, no. 7, pp. 19–24"]:
            with self.subTest(body=body):
                self.assertEqual(self.undecoded(body), [])

    def test_list_item_with_a_year_is_still_prose(self):
        self.assertEqual(len(self.undecoded("- Пакет прошёл MMU в 2004 году")), 1)

    def test_doi_with_its_number_is_a_reference(self):
        self.assertEqual(self.undecoded("Подтвердили Iino и Yoshida 2009, DOI 10.1523/jneurosci.3633-08.2009"), [])
        self.assertEqual(len(self.undecoded("Статью нашли по DOI через Sci-Hub")), 1)

    # Decodings in a less common form

    def test_foreign_article_inside_a_lowercase_expansion(self):
        self.assertEqual(self.undecoded("Поезд TGV (train à grande vitesse) едет"), [])

    def test_shared_head_decodes_two_abbreviations(self):
        body = "> [!note] Определение\n> Верхняя и нижняя мёртвые точки (**ВМТ** и **НМТ**) — крайние положения"
        self.assertEqual(self.undecoded(body), [])
        self.assertEqual(sorted(self.findings("A.md", "abbrev-no-alias")),
                         ["ВМТ расшифрована здесь, но не в aliases", "НМТ расшифрована здесь, но не в aliases"])

    def test_digit_of_the_abbreviation_is_a_number_in_its_expansion(self):
        body = "Бомба Y2K[^y]\n\n[^y]: **Y2K** (Year 2000) — паника"
        self.assertEqual(self.undecoded(body), [])
        self.write("A.md", body, preset="term")
        self.assertEqual(self.findings("A.md", "abbrev-no-alias"), ["Y2K расшифрована здесь, но не в aliases"])

    # The cases below write a term note: it owns every decoding, so abbrev-no-alias shows
    # which phrases count as one
    def test_number_inside_a_capitalised_expansion_is_a_word(self):
        self.write("A.md", "Бит **VM**-бита (Virtual-8086 Mode flag) и бит **LME** (IA-32e Mode Enable)", preset="term")
        self.assertEqual(sorted(self.findings("A.md", "abbrev-no-alias")),
                         ["LME расшифрована здесь, но не в aliases", "VM расшифрована здесь, но не в aliases"])

    def test_number_after_a_bold_abbreviation_is_not_its_expansion(self):
        self.write("A.md", "Опция **SACK** (RFC 2018) ускоряет", preset="term")
        self.assertEqual(self.findings("A.md", "abbrev-no-alias"), [])

    def test_recursive_acronym_repeats_itself_before_the_expansion(self):
        self.assertEqual(self.undecoded("Язык (**PHP** — PHP: Hypertext Preprocessor) позволяет"), [])

    def test_suffix_word_shared_with_the_expansion(self):
        self.write("A.md", "Восстановлена **ИК**-спектроскопией (инфракрасной спектроскопией) по видео", preset="term")
        self.assertEqual(self.findings("A.md", "abbrev-no-alias"), ["ИК расшифрована здесь, но не в aliases"])

    def test_one_word_still_does_not_spell_two_letters_without_a_shared_suffix(self):
        for body in ["Режим **ИК**-канала (инфракрасный) включён",
                     "Режим **ИК**-канала (инфракрасного диапазона) включён"]:
            with self.subTest(body=body):
                self.write("A.md", body, preset="term")
                self.assertEqual(self.findings("A.md", "abbrev-no-alias"), [])

    # Labels: table header row and callout title

    def test_table_header_row_is_a_label(self):
        self.assertEqual(self.undecoded("| Профиль | TTFB, с |\n| --- | --- |\n| база | 1 |"), [])
        self.assertEqual(len(self.undecoded("| Профиль | Время |\n| --- | --- |\n| база | TTFB, с |")), 1)

    def test_callout_title_is_a_label_and_the_first_mention_is_in_the_body(self):
        self.write("Owner.md", "**КПД** (коэффициент полезного действия) — доля", aliases=["КПД"])
        self.assertEqual(self.undecoded("> [!note] КПД двигателя — это доля\n> Общий смысл [[Owner|КПД]] тот же"), [])
        self.assertEqual(self.undecoded("> [!warning] Двойное отрицание NOT + NEITHER — ошибка"), [])
        msgs = self.undecoded("> [!note] КПД двигателя\n> Голый КПД в теле")
        self.assertEqual(len(msgs), 1)
        out = []
        idx = lint.Index()
        idx.build()
        lint.check_note(self.vault / "A.md", idx, out)
        self.assertEqual([f.line for f in out if f.code == "abbrev-undecoded"], [11])

    def test_link_in_a_label_is_still_the_first_mention(self):
        self.write("Owner.md", "**КПД** (коэффициент полезного действия) — доля", aliases=["КПД"])
        self.assertEqual(self.undecoded("> [!note] Про [[Owner|КПД]] двигателя\n> Голый КПД в теле"), [])
        self.assertEqual(self.undecoded("| [[Owner\\|КПД]] | Доля |\n| --- | --- |\n| база | КПД мал |"), [])

    # English

    def test_italic_english_example_is_not_prose(self):
        self.assertEqual(self.undecoded("> *At 8 pm I was watching TV.* — в 8 вечера процесс шёл"), [])
        self.assertEqual(len(self.undecoded("*Важно*: кэш стоит за MMU")), 1)
        self.assertEqual(len(self.undecoded("*кэш стоит за MMU, see the docs*")), 1)


class AbbrevOwnerLinkOnLine(AbbrevNotes):
    """An abbreviation gets its own link to the owner even when its line already links the
    owner under another term: link-repeat allows that link (SKILL.md → ### Связность).
    A link with the abbreviation itself anywhere on the line is its first mention"""

    def setUp(self):
        super().setUp()
        self.write("Owner.md", "Лид\n\n## Поля\n\n**ECN** (Explicit Congestion Notification) — флаг",
                   aliases=["ECN"])

    def both(self, body):
        self.write("A.md", body)
        return (self.findings("A.md", "abbrev-undecoded"), self.findings("A.md", "link-repeat"))

    def test_owner_link_under_another_term_does_not_cover_the_mention(self):
        for body in ["Поля [[Owner|заголовка]]: длина и ECN",
                     "| Поле | Суть |\n| --- | --- |\n| [[Owner\\|заголовок]] | флаг ECN |",
                     "В [[Owner#Поля|полях]] есть ECN"]:
            with self.subTest(body=body):
                undecoded, repeat = self.both(body)
                self.assertEqual(len(undecoded), 1)
                self.assertIn("[[Owner|ECN]]", undecoded[0])
                self.assertEqual(repeat, [])

    def test_the_link_it_asks_for_breaks_no_link_repeat(self):
        for body in ["Поля [[Owner|заголовка]]: длина и [[Owner|ECN]]",
                     "| Поле | Суть |\n| --- | --- |\n| [[Owner\\|заголовок]] | флаг [[Owner\\|ECN]] |"]:
            with self.subTest(body=body):
                self.assertEqual(self.both(body), ([], []))

    def test_link_with_the_term_on_the_line_covers_a_bare_mention_before_it(self):
        self.assertEqual(self.both("Сначала ECN, потом [[Owner|ECN]]"), ([], []))
        self.assertEqual(self.both("Сначала ECN, потом [[Owner#Поля|ECN]]"), ([], []))


class LinkRepeat(AbbrevNotes):
    """One line links one note under one term at most once: a second link with the same
    term repeats, whatever its anchor, while each term of a line gets its own link even to
    one place (SKILL.md → ### Связность). The term is the shown caption, compared without
    case, markup, extra spaces and ё/е; a link without a caption shows its own target"""

    def repeats(self, body):
        self.write("X.md", "Цель\n\n## Раздел\n\n## Другой")
        self.write("dir/Y.md", "Другая цель")
        self.write("A.md", body)
        return self.findings("A.md", "link-repeat")

    def test_same_term_twice_to_one_note_repeats(self):
        for body in ["Про [[X|ECN]] и снова [[X|ECN]]",
                     "Про [[X]] и снова [[X]]",
                     "Про [[X|ECN]] и [[X#Раздел|ECN]]",
                     "Про [[X#Раздел]] и [[X#раздел]]",
                     "Про [[X]] и [[X|x]]",
                     "Про [[dir/Y]] и [[Y]]",
                     "Про [[X|**Ёлка**]] и [[X|елка]]",
                     "Про [[X|флаг  ECN]] и [[X|флаг ECN]]",
                     "> - В callout [[X|a]], [[X|a]]",
                     "Сноска[^a]\n\n[^a]: [[X]] и [[X|x]]",
                     "| Имя | Суть |\n| --- | --- |\n| [[X\\|икс]] | тоже [[X\\|икс]] |"]:
            with self.subTest(body=body):
                self.assertEqual(len(self.repeats(body)), 1)

    def test_different_terms_link_one_place_freely(self):
        for body in ["Поля [[X|IHL]], [[X|DSCP]] и [[X|ECN]]",
                     "Про [[X]] и снова [[X|икс]]",
                     "Про [[X]] и [[X#Раздел]]",
                     "Про [[X#Раздел|раздел]] и [[X#раздел|его же]]",
                     "Про [[dir/Y|игрек]] и [[Y]]",
                     "По [[X#Раздел|Гейне]] и по [[X#Другой|Коши]]",
                     "| Имя | Суть |\n| --- | --- |\n| [[X#Раздел\\|a]] | [[X#Раздел\\|b]] |"]:
            with self.subTest(body=body):
                self.assertEqual(self.repeats(body), [])

    def test_same_term_to_different_notes_does_not_repeat(self):
        self.assertEqual(self.repeats("Про [[X|ключ]] и [[Y|ключ]]"), [])

    def test_one_finding_per_note_term_and_line(self):
        self.assertEqual(len(self.repeats("[[X|a]], [[X|a]], [[X|a]] и [[Y|d]], [[Y|d]], [[X|b]]")), 2)

    def test_finding_names_the_note_and_the_term(self):
        msgs = self.repeats("Про [[X#Раздел|ECN]] и [[X|ECN]]")
        self.assertEqual(len(msgs), 1)
        self.assertIn("X", msgs[0])
        self.assertIn("ECN", msgs[0])

    def test_links_on_other_lines_or_outside_prose_do_not_repeat(self):
        for body in ["Про [[X]]\n\nИ снова [[X]]",
                     "Эмбед ![[X]] и ссылка [[X]]",
                     "Код `[[X]]` и ссылка [[X]]",
                     "Формула $[[X]]$ и ссылка [[X]]"]:
            with self.subTest(body=body):
                self.assertEqual(self.repeats(body), [])

    def test_self_anchor_is_its_own_note(self):
        self.assertEqual(self.repeats("См. [[#Раздел|выше]] и [[#Другой|ниже]]"), [])
        self.assertEqual(len(self.repeats("См. [[#Раздел|выше]] и [[A#Другой|выше]]")), 1)


class TableHeader(AbbrevNotes):
    """The header row is known by the rule row under it (SKILL.md → ### Таблицы)"""

    def test_blank_and_lowercase_header_cells_are_found_only_above_a_rule_row(self):
        self.write("A.md", "| | Desktop |\n| --- | --- |\n| размер | 1 |\n\n| имя | Значение |\n|:--|--:|\n| a | b |")
        self.assertEqual(len(self.findings("A.md", "table-header-blank")), 1)
        self.assertEqual(len(self.findings("A.md", "table-header-case")), 1)
        self.write("A.md", "| | Desktop |\n| имя | Значение |")
        self.assertEqual(self.findings("A.md", "table-header-blank") + self.findings("A.md", "table-header-case"), [])


class SaveBaseline(TempVault):
    def write_baseline(self, notes):
        lint.BASELINE.write_text(json.dumps({"notes": notes}), encoding="utf-8")

    def read_baseline(self):
        return json.loads(lint.BASELINE.read_text(encoding="utf-8"))["notes"]

    def test_accept_drops_notes_that_no_longer_exist(self):
        self.touch("a.md")
        self.write_baseline({"a.md": [["x", "m"]], "gone.md": [["x", "m"]]})
        lint.save_baseline([], {"a.md"}, {"x"})
        self.assertNotIn("gone.md", self.read_baseline())

    def test_accept_drops_entries_of_checks_that_no_longer_exist(self):
        # a retired code is never active again, so no scoped --accept would ever clear it
        self.touch("a.md")
        self.touch("b.md")
        self.write_baseline({"a.md": [["gone-check", "m"], ["quotes", "m"]], "b.md": [["gone-check", "m"]]})
        lint.save_baseline([], {"a.md"}, {"eof-newline"})
        self.assertEqual(self.read_baseline(), {"a.md": [["quotes", "m"]]})

    def test_accept_keeps_existing_notes_outside_its_scope(self):
        self.touch("a.md")
        self.touch("b.md")
        self.write_baseline({"b.md": [["quotes", "m"]]})
        lint.save_baseline([], {"a.md"}, {"quotes"})
        self.assertEqual(self.read_baseline(), {"b.md": [["quotes", "m"]]})

    def test_accept_keeps_entries_of_a_folder_this_vault_does_not_have(self):
        # база одна на два волта: заметка соседнего волта — не удалённая
        self.touch("a.md")
        self.write_baseline({"a.md": [["quotes", "m"]], "01. Курс/content/01. Тема/x.md": [["quotes", "m"]]})
        lint.save_baseline([], {"a.md"}, {"quotes"})
        self.assertIn("01. Курс/content/01. Тема/x.md", self.read_baseline())


TERMS = "00. Термины"


class TermPreset(TempVault):
    def fm_findings(self, rel, text):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(p, idx, out)
        return [(f.code, f.msg) for f in out if f.code.startswith("fm-field")]

    def test_terms_folder_resolves_to_term(self):
        self.assertEqual(lint.resolve_preset(f"{TERMS}/RFC.md", None), ("term", "таблица путей"))

    def test_course_note_beside_it_stays_lecture(self):
        self.assertEqual(lint.resolve_preset("16. Сети/RFC.md", None)[0], "lecture")

    def test_created_and_aliases_are_the_whole_template(self):
        text = "---\ncreated: 2026-10-03\naliases:\n  - ОС\n---\n# Операционная система\n**Операционная система** (ОС) — x\n"
        self.assertEqual(self.fm_findings(f"{TERMS}/Операционная система.md", text), [])

    def test_lecture_fields_are_unexpected_in_a_term(self):
        text = "---\ntitle: t\ncreated: 2026-10-03\nsummary: s\n---\n# RFC\nx\n"
        codes = [c for c, _ in self.fm_findings(f"{TERMS}/RFC.md", text)]
        self.assertEqual(codes, ["fm-field-unexpected", "fm-field-unexpected"])

    def test_missing_created_is_reported(self):
        text = "---\naliases:\n  - ОС\n---\n# Операционная система\nx\n"
        codes = [c for c, _ in self.fm_findings(f"{TERMS}/Операционная система.md", text)]
        self.assertEqual(codes, ["fm-field-missing"])


class LectureOrder(TermPreset):
    """order: N sets a manual sort where lectures cannot (presets/lecture.md)"""

    def test_order_after_aliases_is_a_lecture_field(self):
        text = "---\ntitle: t\ncreated: 2026-10-04\nsummary: s\naliases:\n  - a\norder: 3\n---\n# T\nx\n"
        self.assertEqual(self.fm_findings("99. Курс/T.md", text), [])

    def lectures_findings(self, *values):
        items = "".join(f"  - {v}\n" for v in values)
        p = self.vault / "99. Курс/T.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"---\ntitle: t\nlectures:\n{items}created: 2026-10-04\nsummary: s\n---\n# T\nx\n", encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(p, idx, out)
        return [f.msg for f in out if f.code == "lectures-unquoted"]

    def test_a_bare_word_lecture_is_already_a_string(self):
        self.assertEqual(self.lectures_findings("S1", "П2", "бонус 1", '"3"'), [])

    def test_a_bare_value_yaml_reads_as_no_string_is_caught(self):
        found = self.lectures_findings("12.10", "3", "-", "true", "~")
        self.assertEqual(len(found), 5, found)

    def test_order_before_title_is_out_of_place(self):
        text = "---\norder: 3\ntitle: t\ncreated: 2026-10-04\nsummary: s\n---\n# T\nx\n"
        codes = [c for c, _ in self.fm_findings("99. Курс/T.md", text)]
        self.assertEqual(codes, ["fm-field-order"])


class CourseRootNotes(TempVault):
    """Имя в корне папки курса не обязано начинаться с номера темы: шаблон
    `[0-9][0-9]. *` держит номер только у самой папки курса"""

    def test_a_note_without_a_number_in_the_course_root_is_a_lecture(self):
        rel = "10. БЖД/Лекция 01. Введение, основные понятия.md"
        self.touch(rel)
        self.assertEqual(lint.resolve_preset(rel, None), ("lecture", "таблица путей"))

    def test_a_moc_named_without_a_number_in_the_course_root_is_a_lecture_moc(self):
        rel = "17. Архитектура компьютеров/Вне курса — MOC.md"
        self.touch(rel)
        self.assertEqual(lint.resolve_preset(rel, None), ("lecture-moc", "таблица путей"))


class HeadingTimecodeSource(TempVault):
    """Only a video source asks H2 for a timecode (references/frontmatter.md → sources)"""

    def timecode_findings(self, source):
        p = self.vault / "99. Курс/T.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\ntitle: t\ncreated: 2026-10-04\nsummary: s\nsources:\n  - \"{source}\"\n---\n# T\n\n## Раздел\n\nx\n",
            encoding="utf-8")
        idx = lint.Index()
        idx.build()
        out = []
        lint.check_note(p, idx, out)
        return [f.msg for f in out if f.code == "heading-no-timecode"]

    def test_a_notebook_source_asks_for_no_timecode(self):
        self.assertEqual(self.timecode_findings("[Блокнот](https://colab.research.google.com/drive/abc)"), [])

    def test_a_video_source_still_asks_for_a_timecode(self):
        for url in ("https://www.youtube.com/watch?v=abc", "https://youtu.be/abc"):
            self.assertEqual(len(self.timecode_findings(f"[Лекция 1, 01.01.2026]({url})")), 1, url)


class TwoVaults(unittest.TestCase):
    """One tool, two vaults. A note of the personal vault is linted by --vault, or by an
    absolute path that brings its own root; the conspects vault stays the default"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name).resolve()
        (self.vault / ".obsidian").mkdir()
        self.note = self.vault / "02. Zettelkasten/Мысль.md"
        self.note.parent.mkdir(parents=True)
        self.note.write_text("---\ncreated: 2026-10-03\n---\n# Мысль\nтело\n", encoding="utf-8")
        self.out = io.StringIO()
        self.saved_argv = sys.argv
        self.saved_vault = lint.VAULT

    def tearDown(self):
        sys.argv = self.saved_argv
        lint.VAULT = self.saved_vault
        self.tmp.cleanup()

    def lint(self, *argv):
        sys.argv = ["lint.py", *argv]
        with contextlib.redirect_stdout(self.out):
            lint.main()
        return self.out.getvalue()

    def test_a_note_of_the_personal_vault_resolves_by_its_own_table(self):
        out = self.lint("--all", "--limit", "2", "--vault", str(self.vault), str(self.note))
        self.assertIn(f"волт:   {self.vault}", out)
        self.assertIn("zettel 1", out)

    def test_an_absolute_path_outside_the_conspect_vault_brings_its_own_vault(self):
        out = self.lint("--all", str(self.note))
        self.assertIn(f"волт:   {self.vault}", out)
        self.assertIn("zettel 1", out)


if __name__ == "__main__":
    unittest.main()
