"""Assemble a self-contained interactive page from a template.

A template has markers such as /*COMMON_CSS*/, each exactly once; build_page
replaces each by its text. The result works offline from a file link: no CDN,
no fetch. The theme is the vault's ddlc palette and report stylesheet from
ddlc_figures (pinned by its vendor.lock), the page roles in page.css, and the
vault fonts inlined by fonts.py.
"""
import re
from pathlib import Path

from .fonts import fonts_css

HERE = Path(__file__).resolve().parent
DDLC = HERE.parent / "ddlc_figures"


# `import ... from "...";` over one line or many; the statement ends at its first semicolon
_IMPORT = re.compile(r"^import\b[^;]*;[ \t]*\n", re.M)


def strip_module(js: str) -> str:
    """An ES module's text for inlining into a classic script: no `import` statements and no
    `export` keywords, so every name it defines is a global of the page"""
    return re.sub(r"^export ", "", _IMPORT.sub("", js), flags=re.M)


def theme_css(*extra: str) -> str:
    """Fonts, palette, report stylesheet and the shared page roles, then a course's own CSS.

    The report asks for Nunito from files beside it. A page is one file, so the report's own
    @font-face rules go and the fonts are inlined by fonts.py instead."""
    report = re.sub(r"@font-face\s*\{[^}]*\}\s*", "", (DDLC / "ddlc-report.css").read_text(encoding="utf-8"))
    return "\n".join([
        fonts_css(),
        (DDLC / "palette.css").read_text(encoding="utf-8"),
        report,
        (HERE / "page.css").read_text(encoding="utf-8"),
        *extra,
    ])


def theme_js() -> str:
    """The script half of the theme: toComma(x, digits) and formatNumber(x) write a number with the
    decimal comma, and css(name) gives a role colour as "#rrggbb" for canvas code."""
    return strip_module((HERE / "number.js").read_text(encoding="utf-8")) + (HERE / "theme.js").read_text(encoding="utf-8")


def assemble(name: str, template: str, parts: dict) -> str:
    html = template
    for marker, text in parts.items():
        if template.count(marker) != 1:
            raise SystemExit(f"{name}: marker {marker} must appear exactly once")
        html = html.replace(marker, text)
    return html


def build_page(name: str, template: Path, parts: dict, out: Path) -> Path:
    """The page, with its headings in the prose face: the report sets a heading in Doki where
    Doki is installed, and data-ddlc-heading="plain" on <html> is the report's switch to Mya
    Nunito. Doki's licence allows personal use only, and a page may be published. The tag is
    looked for in the template, before the parts go in: a stylesheet's comment can say <html>"""
    text, n = re.subn(r"<html\b([^>]*)>", r'<html\1 data-ddlc-heading="plain">', template.read_text(encoding="utf-8"))
    if n != 1:
        raise SystemExit(f"{name}: the template must have exactly one <html> tag")
    html = assemble(name, text, parts)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
