"""Tests for media.py, the walk over the vault's figure scripts and sandbox pages, and for
its place in lint.py. The checkers here are stand-ins that read markers from the file they
check, so the walk, the cache and the baseline are tested without matplotlib or Chromium;
check_numbers.py and check_page.py have their own tests. Run from the skill root:

    python3 -m unittest discover -s tools -v
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lint  # noqa: E402
import media  # noqa: E402

COURSE = "01. Курс"
OTHER = "02. Другой"

# Prints one line per DOT: marker as check_numbers.py does, fails on CRASH, and counts its
# runs in runs.log beside the script
FIGURE_CHECKER = textwrap.dedent("""\
    import pathlib, sys
    script = pathlib.Path(sys.argv[1]).resolve()
    with open(script.parent / "runs.log", "a", encoding="utf-8") as log:
        log.write(script.name + "\\n")
    text = script.read_text(encoding="utf-8")
    if "CRASH" in text:
        print("Traceback: boom", file=sys.stderr)
        sys.exit(2)
    if "NOSHELL" in text:
        print("error: cannot build the interpreter", file=sys.stderr)
        sys.exit(1)
    dots = [ln.split("DOT:", 1)[1].strip() for ln in text.splitlines() if "DOT:" in ln]
    for d in dots:
        print(f"{script}\\tText\\t{d!r}")
    for noise in [ln.split("NOISE:", 1)[1].strip() for ln in text.splitlines() if "NOISE:" in ln]:
        print(f"T=1\\ttrain {noise}\\ttest 0.9")
    sys.exit(1 if dots else 0)
""")

# Prints check_page.py's --json report from markers in the page, counts its runs in runs.log
PAGE_CHECKER = textwrap.dedent("""\
    import json, pathlib, sys
    args = [a for a in sys.argv[1:] if a != "--json"]
    page = pathlib.Path(args[0]).resolve()
    with open(page.parent / "runs.log", "a", encoding="utf-8") as log:
        log.write(page.name + " " + " ".join(args[2:]) + "\\n")
    text = page.read_text(encoding="utf-8")
    if "BROKEN" in text:
        print("Traceback: no browser", file=sys.stderr)
        sys.exit(1)
    def marked(tag):
        return [ln.split(tag, 1)[1].strip() for ln in text.splitlines() if tag in ln]
    report = {"errors": marked("ERR:"), "overflow": "".join(marked("WIDE:")),
              "long": marked("LONG:"), "dotted": marked("DOT:")}
    print(json.dumps(report, ensure_ascii=False))
    sys.exit(1 if any(report.values()) else 0)
""")


class TempVault(unittest.TestCase):
    """A scratch vault with two courses, stand-in checkers and its own cache"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name)
        self.write("checkers/figure.py", FIGURE_CHECKER)
        self.write("checkers/page.py", PAGE_CHECKER)
        self.write("shared/kit.py", "SHARED = 1\n")
        self.config = {
            "figures": {COURSE: [sys.executable], OTHER: [sys.executable]},
            "figures_shared": ["shared"],
            "pages": {"python": [sys.executable], "glob": "**/*песочница*.html",
                      "steps": ["dark", "width:390"], "shared": ["shared/kit.py"]},
        }
        self.cache = media.Cache(self.vault / "cache.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def figure(self, rel, body=""):
        return self.write(rel, f"fig.savefig('x.png')\n{body}")

    def runs(self, folder):
        log = self.vault / folder / "runs.log"
        return log.read_text(encoding="utf-8").splitlines() if log.exists() else []

    def figures(self, *roots):
        return media.check_figures(self.vault, self.config, [self.vault / r for r in roots], self.cache,
                                   checker=self.vault / "checkers/figure.py", log=lambda *_: None)

    def pages(self, *roots):
        return media.check_pages(self.vault, self.config, [self.vault / r for r in roots], self.cache,
                                 checker=self.vault / "checkers/page.py", log=lambda *_: None)


class FigureWalk(TempVault):
    def test_a_dotted_text_is_a_finding_of_its_script(self):
        self.figure(f"{COURSE}/.sources/plot.py", "# DOT: 'порог 0.5'\n")
        findings, walked = self.figures()
        self.assertEqual([(f[0], f[1]) for f in findings], [("figure-dotted-number", f"{COURSE}/.sources/plot.py")])
        self.assertIn("порог 0.5", findings[0][3])
        self.assertIn(f"{COURSE}/.sources/plot.py", walked)

    def test_a_clean_script_has_no_finding_but_is_walked(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        findings, walked = self.figures()
        self.assertEqual(findings, [])
        self.assertEqual(walked, {f"{COURSE}/.sources/plot.py"})

    def test_a_line_that_does_not_start_with_the_script_is_not_a_finding(self):
        # a library may write to stdout behind the checker; only its own lines count
        self.figure(f"{COURSE}/.sources/plot.py", "NOISE: 0.929\n")
        findings, _ = self.figures()
        self.assertEqual(findings, [])

    def test_a_script_that_fails_is_figure_failed_with_its_error(self):
        self.figure(f"{COURSE}/.sources/plot.py", "CRASH\n")
        findings, _ = self.figures()
        self.assertEqual([f[0] for f in findings], ["figure-failed"])
        self.assertIn("boom", findings[0][3])

    def test_an_interpreter_that_did_not_start_is_a_failure_not_a_clean_figure(self):
        # the shell of a course exits with 1 and names no text, as a figure with a dot never does
        self.figure(f"{COURSE}/.sources/plot.py", "NOSHELL\n")
        findings, _ = self.figures()
        self.assertEqual([f[0] for f in findings], ["figure-failed"])
        self.assertIn("cannot build", findings[0][3])

    def test_kits_tests_and_scripts_that_save_nothing_are_not_figures(self):
        for name in ("figkit.py", "theme.py", "forces_common.py", "test_plot.py", "course.py",
                     "demo_grid.py"):
            self.figure(f"{COURSE}/.sources/{name}")
        self.write(f"{COURSE}/.sources/helper.py", "X = 1\n")
        self.figure(f"{COURSE}/.sources/interactive/build.py")
        _, walked = self.figures()
        self.assertEqual(walked, set())

    def test_a_course_without_an_interpreter_is_not_walked(self):
        self.figure("03. Без конфига/.sources/plot.py", "# DOT: 0.5\n")
        findings, walked = self.figures()
        self.assertEqual((findings, walked), ([], set()))

    def test_a_cached_script_is_not_run_again_and_keeps_its_findings(self):
        self.figure(f"{COURSE}/.sources/plot.py", "# DOT: 'порог 0.5'\n")
        first, _ = self.figures()
        second, _ = self.figures()
        self.assertEqual(second, first)
        self.assertEqual(self.runs(f"{COURSE}/.sources"), ["plot.py"])

    def test_the_cache_survives_a_new_run_of_the_tool(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figures()
        self.cache = media.Cache(self.vault / "cache.json")
        self.figures()
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 1)

    def test_editing_the_script_runs_it_again(self):
        script = self.figure(f"{COURSE}/.sources/plot.py", "# DOT: 'порог 0.5'\n")
        self.figures()
        script.write_text("fig.savefig('x.png')\n", encoding="utf-8")
        findings, _ = self.figures()
        self.assertEqual(findings, [])
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 2)

    def test_editing_a_module_of_the_course_runs_its_figures_again(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figure(f"{OTHER}/.sources/plot.py")
        self.figures()
        self.write(f"{COURSE}/.sources/figkit.py", "COLOR = 'red'\n")
        self.figures()
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 2)
        self.assertEqual(len(self.runs(f"{OTHER}/.sources")), 1)

    def test_editing_a_shared_file_runs_every_figure_again(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figure(f"{OTHER}/.sources/plot.py")
        self.figures()
        self.write("shared/kit.py", "SHARED = 2\n")
        self.figures()
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 2)
        self.assertEqual(len(self.runs(f"{OTHER}/.sources")), 2)

    def test_a_new_interpreter_runs_the_course_again(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figures()
        self.config["figures"][COURSE] = [sys.executable, "-B"]
        self.figures()
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 2)

    def test_a_failure_is_not_cached(self):
        self.figure(f"{COURSE}/.sources/plot.py", "CRASH\n")
        self.figures()
        self.figures()
        self.assertEqual(len(self.runs(f"{COURSE}/.sources")), 2)

    def test_a_path_inside_a_course_takes_the_whole_course_and_no_other(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figure(f"{OTHER}/.sources/plot.py")
        self.write(f"{COURSE}/content/01. Тема/Заметка.md", "")
        _, walked = self.figures(f"{COURSE}/content/01. Тема/Заметка.md")
        self.assertEqual(walked, {f"{COURSE}/.sources/plot.py"})

    def test_the_vault_root_above_the_courses_takes_them_all(self):
        self.figure(f"{COURSE}/.sources/plot.py")
        self.figure(f"{OTHER}/.sources/plot.py")
        _, walked = self.figures(".")
        self.assertEqual(len(walked), 2)


class PageWalk(TempVault):
    PAGE = f"{COURSE}/content/01. Тема/00. Вложения/knn-песочница.html"

    def test_each_kind_of_problem_has_its_code(self):
        self.write(self.PAGE, "ERR: ReferenceError: x\nWIDE: content 600 px\nLONG: 61 words: …\nDOT: AUC 0.91\n")
        findings, walked = self.pages()
        self.assertEqual(sorted(f[0] for f in findings),
                         ["page-dotted-number", "page-error", "page-paragraph-long", "page-scroll"])
        self.assertTrue(all(f[1] == self.PAGE for f in findings))
        self.assertEqual(walked, {self.PAGE})

    def test_the_page_is_checked_with_the_configured_steps(self):
        self.write(self.PAGE, "")
        self.pages()
        self.assertEqual(self.runs(f"{COURSE}/content/01. Тема/00. Вложения"), ["knn-песочница.html dark width:390"])

    def test_a_page_that_is_not_a_sandbox_is_not_checked(self):
        self.write(f"{COURSE}/content/01. Тема/00. Вложения/export.html", "DOT: 0.5\n")
        self.assertEqual(self.pages(), ([], set()))

    def test_a_cached_page_is_not_checked_again_until_it_changes(self):
        page = self.write(self.PAGE, "DOT: AUC 0.91\n")
        first, _ = self.pages()
        self.assertEqual(self.pages()[0], first)
        page.write_text("", encoding="utf-8")
        self.assertEqual(self.pages()[0], [])
        self.assertEqual(len(self.runs(f"{COURSE}/content/01. Тема/00. Вложения")), 2)

    def test_editing_a_shared_file_checks_every_page_again(self):
        self.write(self.PAGE, "")
        self.pages()
        self.write("shared/kit.py", "SHARED = 2\n")
        self.pages()
        self.assertEqual(len(self.runs(f"{COURSE}/content/01. Тема/00. Вложения")), 2)

    def test_a_check_that_did_not_run_is_an_error_and_is_not_cached(self):
        self.write(self.PAGE, "BROKEN\n")
        findings, _ = self.pages()
        self.assertEqual([f[0] for f in findings], ["page-error"])
        self.assertIn("no browser", findings[0][3])
        self.pages()
        self.assertEqual(len(self.runs(f"{COURSE}/content/01. Тема/00. Вложения")), 2)

    def test_a_path_inside_the_course_takes_its_pages(self):
        self.write(self.PAGE, "")
        self.write(f"{COURSE}/.sources/README.md", "")
        _, walked = self.pages(f"{COURSE}/.sources/README.md")
        self.assertEqual(walked, {self.PAGE})


class InLint(TempVault):
    """lint.py --figures and --pages: the findings go through the baseline like any other"""

    def setUp(self):
        super().setUp()
        self.saved = lint.VAULT, lint.BASELINE, media.CONFIG, media.CACHE, media.FIGURE_CHECK, media.PAGE_CHECK
        lint.VAULT, lint.BASELINE = self.vault, self.vault / "baseline.json"
        media.CONFIG, media.CACHE = self.vault / "media.json", self.vault / "cache.json"
        media.FIGURE_CHECK, media.PAGE_CHECK = self.vault / "checkers/figure.py", self.vault / "checkers/page.py"
        media.CONFIG.write_text(json.dumps(self.config), encoding="utf-8")
        self.figure(f"{COURSE}/.sources/plot.py", "# DOT: 'порог 0.5'\n")

    def tearDown(self):
        lint.VAULT, lint.BASELINE, media.CONFIG, media.CACHE, media.FIGURE_CHECK, media.PAGE_CHECK = self.saved
        super().tearDown()

    def lint(self, *argv):
        out = io.StringIO()
        saved = sys.argv
        sys.argv = ["lint.py", *argv]
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                lint.main()
        finally:
            sys.argv = saved
        return out.getvalue()

    def test_the_codes_are_in_the_catalogue(self):
        for code in media.CODES:
            self.assertIn(code, lint.CHECKS)

    def test_a_figure_finding_is_reported_under_its_script(self):
        out = self.lint("--figures")
        self.assertIn("figure-dotted-number", out)
        self.assertIn(f"{COURSE}/.sources/plot.py", out)

    def test_without_the_flag_no_figure_runs_and_none_is_called_silent(self):
        out = self.lint("--all")
        self.assertEqual(self.runs(f"{COURSE}/.sources"), [])
        self.assertNotIn("figure-", out)

    def test_pages_alone_run_no_figure(self):
        self.lint("--pages")
        self.assertEqual(self.runs(f"{COURSE}/.sources"), [])

    def test_an_accepted_figure_finding_is_hidden_next_time(self):
        self.lint("--figures", "--accept")
        out = self.lint("--figures")
        self.assertNotIn("порог 0.5", out)
        self.assertIn("новых находок нет", out)

    def test_an_accept_without_the_flag_keeps_the_figure_entries(self):
        self.lint("--figures", "--accept")
        self.lint("--accept")
        base = json.loads(lint.BASELINE.read_text(encoding="utf-8"))["notes"]
        self.assertIn(f"{COURSE}/.sources/plot.py", base)

    def test_a_fixed_figure_counts_as_resolved(self):
        self.lint("--figures", "--accept")
        self.figure(f"{COURSE}/.sources/plot.py")
        out = self.lint("--figures")
        self.assertIn("исправлено с записи базы: 1", out)


if __name__ == "__main__":
    unittest.main()
