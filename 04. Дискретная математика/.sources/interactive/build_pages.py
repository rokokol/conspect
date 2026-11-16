"""Build one self-contained interactive page of the discrete math course.

Each pages/<name>.html is a template with three markers, each exactly once:
  /*COMMON_CSS*/  fonts, ddlc palette and report CSS, sandbox_kit's page.css, pages/_common.css
  /*COMMON_JS*/   sandbox_kit's theme.js (toComma, formatNumber, css(name)), then pages/_common.js: small DOM helpers
  /*DMCORE*/      dmcore.js with its `export` keywords removed
The machinery (fonts, theme, assembly) is sandbox_kit's, shared with every course.
The result works offline from a file link: no CDN, no fetch.

Usage: python build_pages.py <name> <output.html>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import course  # noqa: E402,F401  (puts the vault's scripts on sys.path)
from sandbox_kit import page as kit  # noqa: E402


def build(name: str, out: Path) -> Path:
    parts = {
        "/*COMMON_CSS*/": kit.theme_css((HERE / "pages" / "_common.css").read_text(encoding="utf-8")),
        "/*COMMON_JS*/": kit.theme_js() + (HERE / "pages" / "_common.js").read_text(encoding="utf-8"),
        "/*DMCORE*/": kit.strip_module((HERE / "dmcore.js").read_text(encoding="utf-8")),
    }
    return kit.build_page(name, HERE / "pages" / f"{name}.html", parts, out)


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
