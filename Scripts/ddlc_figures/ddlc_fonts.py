"""The fonts of the vault's Obsidian theme for matplotlib figures.

Importing this module applies them. It is the only place where a figure's font is chosen:
`ddlc_theme` imports it, and a course whose figures keep their own colours and layout
(Physics) imports it alone.

The face is Mya Nunito Static, vendored from ddlc-themes beside this file (vendor.lock): Nunito
with the Greek letters, arrows, operators and blackboard letters it lacks, so a label needs no
fallback font. Prose is Medium 500, and bold and titles are Black 900, as in the theme. The
family names and the math keys come from the vendored ddlc.mplstyle, so $...$ is set in the
same face. Doki is not used: its licence allows personal use only, and a figure may be published.
"""
import dataclasses
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc_params_from_file

HERE = Path(__file__).resolve().parent
PROSE_WEIGHT, BOLD_WEIGHT = 500, 900


def _alias_weights(weights=(400, 500, 700, 900)):
    """Let every font family answer every weight a script may ask for.

    findfont logs "Failed to find font weight" for any weight a face does not have exactly,
    and both the font stack and mathtext (Mya Nunito Static, and the STIX faces it falls back
    to, upright and italic) ask for the weight of the text. A face of the family and style
    stands in for each missing weight, the nearest one and the heavier on a tie, with no
    synthetic bold: the entry points at the same file.
    """
    entries = font_manager.fontManager.ttflist
    groups = {}
    for e in entries:
        groups.setdefault((e.name, e.style, e.variant, e.stretch), []).append(e)
    for faces in groups.values():
        have = {e.weight for e in faces}
        for w in weights:
            if w not in have:
                nearest = min(faces, key=lambda e: (abs(e.weight - w), -e.weight))
                entries.append(dataclasses.replace(nearest, weight=w))


def _register_fonts():
    for path in sorted(HERE.glob("MyaNunitoStatic-*.ttf")):
        font_manager.fontManager.addfont(str(path))
    _alias_weights()
    # no lookup has run yet, but a cached answer from before the aliases would be stale
    clear = getattr(font_manager.fontManager._findfont_cached, "cache_clear", None)
    if clear:
        clear()


_register_fonts()

# Only the font and math keys of the style: a course that keeps its own look takes the faces alone
_STYLE = rc_params_from_file(HERE / "ddlc.mplstyle", use_default_template=False)
FONT_STACK = list(_STYLE["font.sans-serif"])
BODY_FONT = FONT_STACK[0]

plt.rcParams.update({
    **{k: v for k, v in _STYLE.items() if k.startswith("mathtext.")},
    "font.family": FONT_STACK,
    "font.weight": PROSE_WEIGHT,
    "axes.unicode_minus": True,
    "axes.titleweight": BOLD_WEIGHT,
    "figure.titleweight": BOLD_WEIGHT,
})
