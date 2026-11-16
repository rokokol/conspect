"""The texts of numkit for a course build to put into a page template.

numkit.js and kernel-editor.js are ES modules. A page is one classic script, so a build inlines
them with `import` and `export` removed: every name is then a global of the page, and the page's
own script and the course module (which also lose their `import` lines) call them by name.
The marker each text goes to is the course's choice; README.md names the usual ones.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# the vault's scripts folder holds sandbox_kit; a course's course.py puts it on the path as well
sys.path.insert(0, str(HERE.parent))
from sandbox_kit.page import strip_module  # noqa: E402,F401  re-exported for course builds


def _read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8")


def numkit_js() -> str:
    return strip_module(_read("numkit.js"))


def kernel_editor_js() -> str:
    return strip_module(_read("kernel-editor.js"))


def kernel_editor_css() -> str:
    return _read("kernel-editor.css")
