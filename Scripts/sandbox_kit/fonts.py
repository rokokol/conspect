"""The vault fonts, subset and inlined into a page as base64 @font-face rules.

A page then shows Mya Nunito and Departure Mono on a device that does not have them
installed. Both are vendored in ddlc_figures from ddlc-themes (pinned by its vendor.lock),
under the family names the vendored ddlc-report.css asks for. Mya Nunito is Nunito with the
Greek letters, arrows, operators and blackboard letters it lacks, so prose needs no fallback
face; its weight axis stays, so the one face serves prose at 500 and bold at 900. No system
font is read, and Doki is not used: its licence allows personal use only. Needs fontTools and
brotli (woff2).
"""
import base64
import hashlib
from pathlib import Path

DDLC = Path(__file__).resolve().parent.parent / "ddlc_figures"

# family -> (vendored file, CSS weight range or None)
FONTS = {
    "Mya Nunito": (DDLC / "MyaNunito.woff2", "200 1000"),
    "Departure Mono": (DDLC / "DepartureMono-Regular.woff2", None),
}

# Latin, Latin-1, modifier letters (ʲ), Greek, Cyrillic, punctuation, super- and subscripts,
# letterlike symbols (ℝ, ℕ), arrows, math operators, miscellaneous technical, geometric shapes,
# the supplemental arrows and operators: what the pages actually print
UNICODES = ("U+0020-007E,U+00A0-00FF,U+02B0-02FF,U+0370-03FF,U+0400-045F,U+2000-206F,U+2070-209F,"
            "U+2100-214F,U+2190-21FF,U+2200-22FF,U+2300-23FF,U+25A0-25FF,U+27C0-27FF,U+2900-2AFF")

CACHE = Path.home() / ".cache/sandbox-kit/fonts"


def fonts_css(cache: Path = CACHE, unicodes: str = UNICODES) -> str:
    from fontTools import subset

    cache.mkdir(parents=True, exist_ok=True)
    rules = []
    for family, (src, weights) in FONTS.items():
        # a new vendored file or a new range is a new subset, never a stale one from the cache
        tag = hashlib.sha256(src.read_bytes() + unicodes.encode()).hexdigest()[:12]
        out = cache / f"{family.replace(' ', '')}-{tag}.woff2"
        if not out.exists():
            subset.main([str(src), f"--unicodes={unicodes}", "--flavor=woff2", f"--output-file={out}"])
        data = base64.b64encode(out.read_bytes()).decode()
        weight = f" font-weight: {weights};" if weights else ""
        rules.append(f'@font-face {{ font-family: "{family}"; src: url(data:font/woff2;base64,{data}) format("woff2");{weight} }}')
    return "\n".join(rules)
