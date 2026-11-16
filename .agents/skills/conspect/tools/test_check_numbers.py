"""Tests for check_numbers.py, the check of the texts a figure script draws. Run from the skill
root (the interpreter needs matplotlib):

    python3 -m unittest discover -s tools -v
"""
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_numbers  # noqa: E402


class CheckNumbers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def script(self, body, theme=True):
        """A figure script; with theme it draws through the vault's ddlc_theme, as a course does"""
        head = (f"import sys\nsys.path.insert(0, {str(check_numbers.DDLC)!r})\n" if theme else "") + textwrap.dedent("""\
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        """) + ("import ddlc_theme\n" if theme else "") + textwrap.dedent("""\
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 0.5])
        """)
        path = self.dir / "figure.py"
        path.write_text(head + textwrap.dedent(body), encoding="utf-8")
        return path

    def check(self, *scripts):
        return subprocess.run([sys.executable, str(HERE / "check_numbers.py"), *map(str, scripts)],
                              capture_output=True, text=True, timeout=120)

    def test_the_checker_names_the_script_and_the_text_and_fails(self):
        r = self.check(self.script('ax.set_title("порог 0.5")\nfig.savefig("out.png")\n'))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("figure.py", r.stdout)
        self.assertIn("порог 0.5", r.stdout)

    def test_the_checker_passes_a_clean_figure(self):
        r = self.check(self.script(
            'ax.set_title("порог " + ddlc_theme.num(0.5, 1))\n'
            'ddlc_theme.keep_dots(ax.set_xlabel("задача 17.10"))\n'
            'fig.savefig("out.png")\n'))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_progress_lines_of_a_script_are_not_texts_of_the_figure(self):
        # a course script prints tab-separated scores while it trains; they are not drawn
        r = self.check(self.script(
            'print("T=1\\ttrain 0.929\\ttest 0.911")\n'
            'print("digit 3\\tp_true 0.9915\\tsecond 2 6.37e-03")\n'
            'fig.savefig("out.png")\n'))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout, "")

    def test_a_drawn_text_is_named_beside_the_progress_lines(self):
        r = self.check(self.script(
            'print("T=1\\ttrain 0.929\\ttest 0.911")\n'
            'ax.set_title("порог 0.5")\n'
            'fig.savefig("out.png")\n'))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual([ln.split("\t")[2] for ln in r.stdout.splitlines()], ["'порог 0.5'"])

    def test_the_checker_sees_a_frame_drawn_without_savefig(self):
        r = self.check(self.script('ax.set_title("кадр 0.5")\nfig.canvas.draw()\n'))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("кадр 0.5", r.stdout)

    def test_the_checker_sees_the_dotted_ticks_of_a_script_without_the_theme(self):
        r = self.check(self.script('fig.savefig("out.png")\n', theme=False))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("'0.5'", r.stdout)

    def test_a_script_that_exits_with_an_error_fails_the_check(self):
        r = self.check(self.script("raise SystemExit(3)\n"))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_a_script_that_raises_is_a_failure_not_a_finding(self):
        # Python exits with 1 on an uncaught exception, the status of a figure with a dot
        r = self.check(self.script("raise IndexError('no argument')\n"))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("IndexError", r.stderr)


if __name__ == "__main__":
    unittest.main()
