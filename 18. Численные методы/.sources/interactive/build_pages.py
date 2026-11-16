"""Build one self-contained interactive page of the numerical methods course.

Each pages/<name>.html is a template with these markers, each exactly once:
  /*COMMON_CSS*/  fonts, ddlc palette and report CSS, sandbox_kit's page.css, pages/_common.css
  /*COMMON_JS*/   sandbox_kit's theme.js (css(name) colours), then pages/_common.js: small DOM helpers
  /*NUMKIT*/      numkit.js (the vault's numerical mechanisms) with its `export` keywords removed
  /*CHART*/       numkit's kernel-editor.js: the line chart (linear and log axes), ticks and number helpers
  /*NMCORE*/      nmcore.js with its `import` and `export` removed; it comes after /*NUMKIT*/
  /*PRESETS*/     presets.json for the page: `const PRESETS = [...]`
The machinery (fonts, theme, assembly) is sandbox_kit's, the numerical mechanisms and the chart are numkit's,
shared with every course. The result works offline from a file link: no CDN, no fetch.

Usage: python build_pages.py <name> <output.html>
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import course  # noqa: E402,F401  (puts the vault's scripts on sys.path)
from numkit import embed  # noqa: E402
from sandbox_kit import page as kit  # noqa: E402


def build(name: str, out: Path) -> Path:
    presets = [p for p in json.loads((HERE / "presets.json").read_text(encoding="utf-8")) if name in p["pages"]]
    parts = {
        "/*COMMON_CSS*/": kit.theme_css((HERE / "pages" / "_common.css").read_text(encoding="utf-8")),
        "/*COMMON_JS*/": kit.theme_js() + (HERE / "pages" / "_common.js").read_text(encoding="utf-8"),
        "/*NUMKIT*/": embed.numkit_js(),
        "/*CHART*/": embed.kernel_editor_js(),
        "/*NMCORE*/": embed.strip_module((HERE / "nmcore.js").read_text(encoding="utf-8")),
        "/*PRESETS*/": "const PRESETS = " + json.dumps(presets, ensure_ascii=False) + ";",
    }
    return kit.build_page(name, HERE / "pages" / f"{name}.html", parts, out)


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
