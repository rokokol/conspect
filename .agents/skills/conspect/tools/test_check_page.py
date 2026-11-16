"""Tests for check_page.py, the headless check of a built page. The page is opened by the
interpreter of the pages in media.json, which has playwright; CHROMIUM or nix gives the
browser. Run from the skill root:

    python3 -m unittest discover -s tools -v
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_page  # noqa: E402
import media  # noqa: E402

PAGE_PYTHON = media.load_config()["pages"]["python"]

PAGE = """<!doctype html><html><body><main>
<p class="lead">{lead}</p><p id="dyn"></p>
<script>document.getElementById("dyn").textContent = "{dyn}";</script>
</main></body></html>"""


def words(n):
    return " ".join(["слово"] * n)


class LongParagraphs(unittest.TestCase):
    def run_page(self, lead, dyn=""):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "p.html"
            page.write_text(PAGE.format(lead=lead, dyn=dyn), encoding="utf-8")
            return subprocess.run([*PAGE_PYTHON, str(HERE / "check_page.py"), str(page), d],
                                  capture_output=True, text=True)

    def test_limit_is_the_conspect_paragraph_limit(self):
        skill = (check_page.vault() / ".agents/skills/conspect/SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f"не длиннее {check_page.PARAGRAPH_MAX_WORDS} слов", skill)

    def test_paragraph_at_the_limit_passes(self):
        r = self.run_page(words(check_page.PARAGRAPH_MAX_WORDS))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_static_paragraph_over_the_limit_fails(self):
        r = self.run_page(words(check_page.PARAGRAPH_MAX_WORDS + 1))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("LONG PARAGRAPHS", r.stdout)

    def test_paragraph_written_by_the_script_is_checked_too(self):
        r = self.run_page("коротко", dyn=words(check_page.PARAGRAPH_MAX_WORDS + 1))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("LONG PARAGRAPHS", r.stdout)


WIDE = """<!doctype html><html><body><main>
<p class="lead">коротко</p><div style="width:{px}px;height:10px"></div>
</main></body></html>"""


class NarrowWidth(unittest.TestCase):
    def run_page(self, px, *steps):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "p.html"
            page.write_text(WIDE.format(px=px), encoding="utf-8")
            return subprocess.run([*PAGE_PYTHON, str(HERE / "check_page.py"), str(page), d, *steps],
                                  capture_output=True, text=True)

    def test_page_that_fits_the_width_passes(self):
        r = self.run_page(300, "width:390")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_page_wider_than_the_width_fails_with_horizontal_scroll(self):
        r = self.run_page(600, "width:390")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("HORIZONTAL SCROLL", r.stdout)

    def test_wide_page_is_not_judged_without_the_width_step(self):
        r = self.run_page(1500)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


NUMBERS = """<!doctype html><html><body><main>
{body}
<canvas id="c" width="200" height="50"></canvas>
<script>{script}</script>
</main></body></html>"""


class DottedNumbers(unittest.TestCase):
    def run_page(self, body="", script=""):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "p.html"
            page.write_text(NUMBERS.format(body=body, script=script), encoding="utf-8")
            return subprocess.run([*PAGE_PYTHON, str(HERE / "check_page.py"), str(page), d],
                                  capture_output=True, text=True)

    def assert_fails_on(self, r, text):
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("DOTTED NUMBERS", r.stdout)
        self.assertIn(text, r.stdout)

    def test_a_dotted_number_in_the_text_fails(self):
        self.assert_fails_on(self.run_page("<p>AUC 0.91</p>"), "AUC 0.91")

    def test_a_number_the_script_writes_is_checked_too(self):
        r = self.run_page('<output id="o"></output>', 'document.getElementById("o").textContent = (0.35).toFixed(2);')
        self.assert_fails_on(r, "0.35")

    def test_a_number_drawn_on_a_canvas_is_checked_too(self):
        r = self.run_page(script='document.getElementById("c").getContext("2d").fillText("φ = 0.12", 10, 20);')
        self.assert_fails_on(r, "φ = 0.12")

    def test_a_number_drawn_one_glyph_at_a_time_is_read_whole(self):
        # As a page's own text routine sets indices: one fillText per glyph, each where the last ended
        r = self.run_page(script='const c = document.getElementById("c").getContext("2d"); let x = 10;'
                                 ' for (const g of ["0", ".", "5"]) { c.fillText(g, x, 20); x += c.measureText(g).width; }')
        self.assert_fails_on(r, "0.5")

    def test_labels_drawn_apart_are_not_joined(self):
        r = self.run_page(script='const c = document.getElementById("c").getContext("2d");'
                                 ' c.fillText("0", 10, 20); c.fillText(".", 60, 20); c.fillText("5", 120, 20);')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_commas_inputs_code_and_kept_or_hidden_text_pass(self):
        r = self.run_page(
            '<p>AUC 0,91 и −2,5</p><input value="0.5"><code>x = 0.5</code>'
            '<p data-keep-dots>TLS 1.3</p><p hidden>0.7</p><p>192.168.0.1</p>',
            'document.getElementById("c").getContext("2d").fillText("0,25", 10, 20);')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class JsonReport(unittest.TestCase):
    """--json: the report media.py reads, one JSON object on the last line of stdout"""

    def run_page(self, body, *steps):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "p.html"
            page.write_text(NUMBERS.format(body=body, script=""), encoding="utf-8")
            r = subprocess.run([*PAGE_PYTHON, str(HERE / "check_page.py"), "--json", str(page), d, *steps],
                               capture_output=True, text=True)
        return r, json.loads(r.stdout.strip().splitlines()[-1])

    def test_a_clean_page_reports_nothing_and_passes(self):
        r, report = self.run_page("<p>AUC 0,91</p>")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(report, {"errors": [], "overflow": "", "long": [], "dotted": []})

    def test_each_problem_lands_in_its_field_and_fails(self):
        body = (f'<p>{words(check_page.PARAGRAPH_MAX_WORDS + 1)}</p><p>AUC 0.91</p>'
                '<div style="width:600px;height:5px"></div><script>undefinedName()</script>')
        r, report = self.run_page(body, "width:390")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(report["dotted"], ["AUC 0.91"])
        self.assertEqual(len(report["long"]), 1)
        self.assertIn("390", report["overflow"])
        self.assertTrue(any("undefinedName" in e for e in report["errors"]), report["errors"])


if __name__ == "__main__":
    unittest.main()
