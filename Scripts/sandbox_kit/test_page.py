"""page.py assembles a template: markers exactly once, exports stripped, theme from the vault palette.

Run: python -m unittest test_page   (needs fontTools, brotli and fc-match)
"""
import base64
import io
import re
import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from sandbox_kit import page

TEMPLATE = "<style>/*CSS*/</style><script>/*JS*/</script>"


class Assemble(unittest.TestCase):
    def test_each_marker_is_replaced(self):
        html = page.assemble("t", TEMPLATE, {"/*CSS*/": "a{}", "/*JS*/": "let x;"})
        self.assertEqual(html, "<style>a{}</style><script>let x;</script>")

    def test_missing_marker_stops_the_build(self):
        with self.assertRaises(SystemExit):
            page.assemble("t", "<style></style>", {"/*CSS*/": "a{}"})

    def test_repeated_marker_stops_the_build(self):
        with self.assertRaises(SystemExit):
            page.assemble("t", "/*CSS*/ /*CSS*/", {"/*CSS*/": "a{}"})

    def test_build_page_writes_the_file_with_plain_headings(self):
        with tempfile.TemporaryDirectory() as d:
            tpl = Path(d) / "t.html"
            tpl.write_text(f'<html lang="ru">{TEMPLATE}</html>', encoding="utf-8")
            out = page.build_page("t", tpl, {"/*CSS*/": "", "/*JS*/": ""}, Path(d) / "sub" / "o.html")
            self.assertEqual(out.read_text(encoding="utf-8"),
                             '<html lang="ru" data-ddlc-heading="plain"><style></style><script></script></html>')

    def test_a_template_without_one_html_tag_stops_the_build(self):
        for text in (TEMPLATE, f"<html>{TEMPLATE}<html>"):
            with tempfile.TemporaryDirectory() as d:
                tpl = Path(d) / "t.html"
                tpl.write_text(text, encoding="utf-8")
                with self.assertRaises(SystemExit):
                    page.build_page("t", tpl, {"/*CSS*/": "", "/*JS*/": ""}, Path(d) / "o.html")


class ThemeJs(unittest.TestCase):
    """css(name) hands a canvas script "#rrggbb", though the report writes roles as light-dark() and color-mix()."""

    NAMES = ["--surface", "--text", "--text-2", "--c0", "--t-red", "--t-green"]
    # A browser may hand a resolved colour back in Oklab or Oklch rather than rgb(), and Oklab's
    # a and b go negative. These two are pure red and pure green written that way: the values
    # are the CSS Color 4 conversions of #ff0000 and #00ff00
    PROBES = ":root { --t-red: oklch(0.62796 0.25768 29.234); --t-green: oklab(0.86644 -0.23389 0.1795); }"

    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        from sandbox_kit.browser import chromium

        html = f"<!doctype html><html><head><style>{page.theme_css(cls.PROBES)}</style></head><body><script>{page.theme_js()}</script></body></html>"
        cls.seen = {}
        cls.mixed = {}
        with tempfile.TemporaryDirectory() as d, sync_playwright() as p:
            f = Path(d) / "p.html"
            f.write_text(html, encoding="utf-8")
            b = p.chromium.launch(executable_path=chromium())
            pg = b.new_page()
            pg.goto(f.as_uri())
            for scheme in ("light", "dark"):
                pg.emulate_media(color_scheme=scheme)
                cls.seen[scheme] = pg.evaluate("(names) => names.map((n) => css(n))", cls.NAMES)
                cls.mixed[scheme] = pg.evaluate(
                    "() => css('color-mix(in srgb, var(--text) 50%, var(--surface))')")
            # A host can turn a page dark without the media query, by data-theme on <html>:
            # the canvas has to follow what the page is drawn in, not what the system prefers
            pg.emulate_media(color_scheme="light")
            pg.evaluate("document.documentElement.dataset.theme = 'dark'")
            cls.pinned_dark = pg.evaluate("(names) => names.map((n) => css(n))", cls.NAMES)
            b.close()

    def test_every_role_is_a_hex_colour(self):
        for scheme, colours in self.seen.items():
            for name, c in zip(self.NAMES, colours):
                self.assertRegex(c, r"^#[0-9a-f]{6}$", f"{name} in {scheme}")

    def test_the_colour_follows_the_scheme(self):
        palette = (page.DDLC / "palette.css").read_text(encoding="utf-8")
        paper = re.search(r"--ddlc-paper:\s*(#[0-9A-Fa-f]{6})", palette).group(1).lower()
        ink = re.search(r"--ddlc-ink:\s*(#[0-9A-Fa-f]{6})", palette).group(1).lower()
        self.assertEqual(self.seen["light"][0], paper)
        self.assertEqual(self.seen["dark"][0], ink)
        self.assertEqual(self.seen["light"][1], ink)
        self.assertEqual(self.seen["dark"][1], paper)

    def test_the_colour_follows_a_scheme_set_on_the_page_not_only_the_media_query(self):
        self.assertEqual(self.pinned_dark[:2], self.seen["dark"][:2])

    def test_an_oklab_or_oklch_colour_comes_back_as_its_srgb(self):
        for scheme, colours in self.seen.items():
            for got, want in zip(colours[4:], ((255, 0, 0), (0, 255, 0))):
                channels = [int(got[i:i + 2], 16) for i in (1, 3, 5)]
                for c, w in zip(channels, want):
                    self.assertLessEqual(abs(c - w), 2, f"{got} for {want} in {scheme}")

    def test_a_colour_expression_is_resolved_too(self):
        # the waveguide page builds its plot roles as a color-mix of the ink and the ground
        def rgb(colour):
            return [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
        for scheme, mixed in self.mixed.items():
            paper, ink = (rgb(c) for c in self.seen[scheme][:2])
            for got, a, b in zip(rgb(mixed), paper, ink):
                self.assertLessEqual(abs(got - (a + b) / 2), 1, f"{mixed} in {scheme}")


class StripModule(unittest.TestCase):
    def test_removes_the_export_keyword_at_line_start_only(self):
        src = "export function f() {}\nexport const A = 1;\nconst s = 'export x';\n  // export inside a comment\n"
        self.assertEqual(page.strip_module(src), "function f() {}\nconst A = 1;\nconst s = 'export x';\n  // export inside a comment\n")

    def test_removes_a_one_line_import(self):
        js = 'import { a, b } from "./x.js";\nconst c = a + b;\n'
        self.assertEqual(page.strip_module(js), "const c = a + b;\n")

    def test_removes_a_multi_line_import(self):
        js = 'import {\n  a,\n  b,\n} from "../../x y/numkit.js";\nexport const c = a + b;\n'
        self.assertEqual(page.strip_module(js), "const c = a + b;\n")

    def test_keeps_the_word_import_in_text_and_indented_code(self):
        js = 'const s = "import x";\n  // import y from z;\nfunction f() {\n  const m = import_name;\n}\n'
        self.assertEqual(page.strip_module(js), js)


class Theme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = page.theme_css("/*COURSE*/")

    def test_palette_and_report_come_from_ddlc_figures(self):
        palette = (page.DDLC / "palette.css").read_text(encoding="utf-8")
        report = (page.DDLC / "ddlc-report.css").read_text(encoding="utf-8")
        self.assertIn(palette, self.css)
        # the report's own @font-face rules point at files beside it; the page inlines the fonts instead
        for rule in re.split(r"@font-face\s*\{[^}]*\}\s*", report):
            self.assertIn(rule, self.css)

    def test_fonts_are_inlined_and_nothing_is_fetched(self):
        self.assertEqual(len(re.findall(r"@font-face", self.css)), 2)
        self.assertIn("data:font/woff2;base64,", self.css)
        self.assertNotRegex(self.css, r"url\((?!data:)")
        self.assertNotIn("http", re.sub(r"/\*.*?\*/", "", self.css, flags=re.S))

    def embedded(self, family):
        """The font file a page embeds under `family`, and the face's CSS weight range."""
        m = re.search(r'@font-face\s*\{[^}]*font-family:\s*"%s"[^}]*\}' % family, self.css)
        self.assertIsNotNone(m, f"no @font-face for {family}")
        data = re.search(r"base64,([A-Za-z0-9+/=]+)", m.group(0)).group(1)
        return TTFont(io.BytesIO(base64.b64decode(data))), m.group(0)

    def test_mya_nunito_is_embedded_with_the_weights_and_the_signs_a_page_prints(self):
        font, rule = self.embedded("Mya Nunito")
        axis = {a.axisTag: a for a in font["fvar"].axes}["wght"]
        self.assertLessEqual(axis.minValue, 500)
        self.assertGreaterEqual(axis.maxValue, 900)
        self.assertRegex(rule, r"font-weight:\s*200 1000")
        cmap = font.getBestCmap()
        self.assertTrue(all(cp in cmap for cp in range(0x0410, 0x0450)))
        self.assertEqual([ch for ch in "λΔΩ→⇒↦∀∈∑∫≤∞−ℝℕ‖²₁ⁿ" if ord(ch) not in cmap], [])

    def test_the_data_face_is_the_vendored_monospaced_departure_mono(self):
        font, _ = self.embedded("Departure Mono")
        widths = {font["hmtx"][font.getBestCmap()[ord(ch)]][0] for ch in "il0mW"}
        self.assertEqual(len(widths), 1)

    def test_no_face_of_the_page_is_doki(self):
        faces = re.findall(r'@font-face\s*\{[^}]*font-family:\s*"([^"]+)"', self.css)
        self.assertEqual(sorted(faces), ["Departure Mono", "Mya Nunito"])
        kit = (page.HERE / "page.css").read_text(encoding="utf-8")
        self.assertNotRegex(re.sub(r"/\*.*?\*/", "", kit, flags=re.S), r"--ddlc-font-(prose|heading)\s*:")

    def test_prose_is_medium_and_bold_is_black_without_synthesis(self):
        css = re.sub(r"/\*.*?\*/", "", self.css, flags=re.S)
        body = "".join(re.findall(r"(?:^|\n)body\s*\{[^}]*\}", css))
        self.assertRegex(body, r"font:\s*500 [^;]*var\(--ddlc-font-prose\)")
        self.assertRegex(css, r"--ddlc-font-prose:\s*'Mya Nunito'")
        self.assertRegex(css, r"(?:b|strong)[^{]*\{[^}]*font-weight:\s*900")
        self.assertRegex(css, r"font-synthesis-weight:\s*none")

    def test_course_css_comes_last(self):
        self.assertTrue(self.css.rstrip().endswith("/*COURSE*/"))


class Headings(unittest.TestCase):
    """A built page sets its headings in Mya Nunito, even on a machine that has Doki installed."""

    def test_a_heading_of_a_built_page_is_not_doki(self):
        from playwright.sync_api import sync_playwright
        from sandbox_kit.browser import chromium

        tpl ='<!doctype html><html lang="ru"><head><style>/*CSS*/</style></head><body><h1>Заголовок</h1><p>Текст</p></body></html>'
        with tempfile.TemporaryDirectory() as d, sync_playwright() as p:
            src = Path(d) / "t.html"
            src.write_text(tpl, encoding="utf-8")
            out = page.build_page("t", src, {"/*CSS*/": page.theme_css()}, Path(d) / "o.html")
            b = p.chromium.launch(executable_path=chromium())
            pg = b.new_page()
            pg.goto(out.as_uri())
            heading, prose = pg.evaluate("['h1', 'p'].map((s) => getComputedStyle(document.querySelector(s)).fontFamily)")
            b.close()
        self.assertNotIn("doki", heading.lower())
        self.assertTrue(heading.startswith('"Mya Nunito"'), heading)
        self.assertEqual(heading, prose)


if __name__ == "__main__":
    unittest.main()
