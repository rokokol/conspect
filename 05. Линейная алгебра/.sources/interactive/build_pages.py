"""Build one self-contained interactive page of the linear algebra course.

Each pages/<name>.html is a template with these markers, each exactly once:
  /*COMMON_CSS*/  fonts, ddlc palette and report CSS, sandbox_kit's page.css, pages/_common.css
  /*COMMON_JS*/   sandbox_kit's theme.js (css(name) colours), then pages/_common.js: small DOM helpers
  /*NUMKIT*/      numkit.js (the vault's numerical mechanisms) with its `export` keywords removed
  /*LACORE*/      lacore.js with its `import` and `export` removed; it comes after /*NUMKIT*/
A page that takes a degenerate kernel adds two more, each exactly once:
  /*KERNEL_CSS*/  pages/_kernel.css (the look), then numkit's kernel-editor.css (the layout)
  /*KERNEL_JS*/   numkit's kernel-editor.js, then pages/_kernel.js: the presets, with presets.json written in
The machinery (fonts, theme, assembly) is sandbox_kit's, the numerical mechanisms and the editor are numkit's,
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
    parts = {
        "/*COMMON_CSS*/": kit.theme_css((HERE / "pages" / "_common.css").read_text(encoding="utf-8")),
        "/*COMMON_JS*/": kit.theme_js() + (HERE / "pages" / "_common.js").read_text(encoding="utf-8"),
        "/*NUMKIT*/": embed.numkit_js(),
        "/*LACORE*/": embed.strip_module((HERE / "lacore.js").read_text(encoding="utf-8")),
    }
    template = HERE / "pages" / f"{name}.html"
    if "/*KERNEL_JS*/" in template.read_text(encoding="utf-8"):
        # the answers of the notes stay out of the page: only what the editor needs
        presets = [{k: v for k, v in p.items() if k != "answer"} for p in json.loads((HERE / "presets.json").read_text(encoding="utf-8"))]
        kernel_js = (HERE / "pages" / "_kernel.js").read_text(encoding="utf-8")
        parts["/*KERNEL_CSS*/"] = (HERE / "pages" / "_kernel.css").read_text(encoding="utf-8") + embed.kernel_editor_css()
        parts["/*KERNEL_JS*/"] = embed.kernel_editor_js() + kernel_js.replace("/*PRESETS_JSON*/[]", json.dumps(presets, ensure_ascii=False))
    return kit.build_page(name, template, parts, out)


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
