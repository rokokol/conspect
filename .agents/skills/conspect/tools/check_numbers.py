"""Name every text of a figure script whose decimal number is written with a dot.

Usage: python check_numbers.py SCRIPT [SCRIPT ...]

Each script runs from its own folder under the interpreter that runs this check, so a
course checks its scripts with its own interpreter; the script writes its figures as it
always does. Every text drawn while it runs counts, by savefig or by a canvas that renders
a frame: ticks, offsets, titles, labels, legends, annotations. A hidden text is not drawn
and does not count, and a text marked with keep_dots() is spared. One line per text:

    SCRIPT<TAB>ARTIST<TAB>'TEXT'

The script's own output is discarded, so stdout holds the texts alone: a script prints
progress lines with tabs and numbers, and they are not texts of the figure.

Exit 0 when no text has a dot, 1 when some has, 2 when a script itself failed.
"""
import contextlib
import io
import runpy
import subprocess
import sys
import traceback
from pathlib import Path

# The rule of a decimal number is the figures' own, in the vault's shared ddlc_figures
VAULT = Path(__file__).resolve().parents[4]
DDLC = VAULT / "Scripts/ddlc_figures"


def _one(script: Path) -> int:
    """Run one script in this process and print its texts with a dot"""
    sys.path.insert(0, str(DDLC))
    import matplotlib

    matplotlib.use("Agg")
    # Importing ddlc_numbers changes no figure, so the script draws as it would alone
    from ddlc_numbers import dotted, drawn_texts

    sys.argv = [str(script)]
    sys.path.insert(0, str(script.parent))
    with drawn_texts() as seen:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(script), run_name="__main__")
        except SystemExit as stop:
            if stop.code not in (0, None):
                print(f"{script}: exited with {stop.code}", file=sys.stderr)
                return 2
        except Exception:
            # Python itself exits with 1 here, the status of a text with a dot
            traceback.print_exc()
            return 2
    found: dict[str, str] = {}
    for artist, text in dotted(seen):
        found.setdefault(text, type(artist).__name__)
    for text, kind in found.items():
        print(f"{script}\t{kind}\t{text!r}")
    return 1 if found else 0


def main(scripts: list[str]) -> int:
    if not scripts:
        print(__doc__, file=sys.stderr)
        return 2
    worst = 0
    for name in scripts:
        script = Path(name).resolve()
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--one", str(script)],
                           cwd=script.parent, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode not in (0, 1):
            tail = "\n".join(r.stderr.strip().splitlines()[-4:])
            print(f"{script}\tFAILED {r.returncode}\n{tail}", file=sys.stderr)
            worst = 2
        else:
            worst = max(worst, r.returncode)
    return worst


if __name__ == "__main__":
    if sys.argv[1:2] == ["--one"]:
        sys.exit(_one(Path(sys.argv[2])))
    sys.exit(main(sys.argv[1:]))
