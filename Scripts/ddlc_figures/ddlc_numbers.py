"""The Russian decimal comma in figures, with no system locale.

A figure script writes every number of a label, a title or an annotation
with num(), which gives the comma. A text is never rewritten behind the
script: the conspect skill's check_numbers.py runs a figure script and names
each text where a number still has a dot, and dotted_numbers() and
figure_dots() are what it asks.

The ticks are not written by a script, so install() makes the comma
formatter the default of every linear axis, a colorbar's included; the
theme calls it. Importing this module alone changes nothing, so the check
sees a figure as its script draws it.
A formatter a script sets itself is its own, and the check reads its ticks
like any other text.

A text whose dot is not a decimal one, such as the number of a problem
17.10 or TLS 1.3, is marked with keep_dots(text), and the check spares it.

Inside $...$ a bare comma is punctuation and mathtext draws a space
after it, so there the comma is written {,}.
"""
import functools
import re
from contextlib import contextmanager

import matplotlib.scale as mscale
import matplotlib.text as mtext
import matplotlib.ticker as mticker

# A number with a fractional part, not glued to a slash, an underscore or another dot: the
# dot of an address, a date or HTTP/1.1 is no decimal one. A Latin letter or a TeX length
# may follow it only as an exponent, such as 1.5e3, so 0.5em is no number
_NUMBER = re.compile(r"(?<![0-9_./])\d+\.\d+(?=$|[^A-Za-z0-9_.]|[eE][-+]?\d)")
# A number glued to a word is part of a name, such as v2.0. Letters that follow a backslash
# are a TeX command, so $\approx0.5$ still has a number
_GLUED = re.compile(r"(?:^|[^\\A-Za-z])[A-Za-z]+$")


def _comma(text: str) -> str:
    return text.replace(".", "{,}" if "$" in text else ",")


class CommaFormatter(mticker.ScalarFormatter):
    """ScalarFormatter with the decimal comma in its ticks and its offset"""

    def __call__(self, x, pos=None):
        return _comma(super().__call__(x, pos))

    def get_offset(self):
        return _comma(super().get_offset())


# The scales whose default formatter is ScalarFormatter: a linear axis, and the function
# scale a colorbar with boundaries takes, such as the colorbar of filled contours
_SCALES = (mscale.LinearScale, mscale.FuncScale)
_defaults = {scale: scale.set_default_locators_and_formatters for scale in _SCALES}


def _with_comma(defaults):
    def set_default_locators_and_formatters(self, axis):
        defaults(self, axis)
        axis.set_major_formatter(CommaFormatter())
    return set_default_locators_and_formatters


def install() -> None:
    """Make CommaFormatter the default of every linear or function-scale axis made or
    cleared from now on"""
    for scale, defaults in _defaults.items():
        scale.set_default_locators_and_formatters = _with_comma(defaults)


def num(x: float, digits: int | str | None = 2, math: bool = False) -> str:
    """x with `digits` decimals and a comma, or with digits=None in the shortest form, as
    f"{x:g}" writes it. A format spec such as "+.2f", ".1%", ".1e" or ".3g" in place of
    digits writes x as format() does. math=True gives {,} for use inside $...$"""
    if isinstance(digits, str):
        text = format(x, digits)
    else:
        text = f"{x:g}" if digits is None else f"{x:.{digits}f}"
    return text.replace(".", "{,}" if math else ",")


def keep_dots(text: mtext.Text) -> mtext.Text:
    """Mark a text whose dots are not decimal ones, so the check spares it"""
    setattr(text, "_ddlc_keep_dots", True)
    return text


def dotted_numbers(text: str) -> list[str]:
    """The decimal numbers of text that are written with a dot"""
    return [m.group() for m in _NUMBER.finditer(text) if not _GLUED.search(text[:m.start()])]


@contextmanager
def drawn_texts():
    """Collect (text, string) for every text drawn inside the block. A hidden text, or one
    on a hidden axis, is not drawn and so not collected"""
    seen: list[tuple[mtext.Text, str]] = []
    draw = mtext.Text.draw

    @functools.wraps(draw)
    def record(self, renderer):
        if self.get_visible() and self.get_text():
            seen.append((self, self.get_text()))
        return draw(self, renderer)

    mtext.Text.draw = record
    try:
        yield seen
    finally:
        mtext.Text.draw = draw


def dotted(texts) -> list[tuple[mtext.Text, str]]:
    """The (text, string) pairs whose string has a decimal number with a dot, keep_dots spared"""
    return [(t, s) for t, s in texts
            if not getattr(t, "_ddlc_keep_dots", False) and dotted_numbers(s)]


def figure_dots(fig) -> list[tuple[mtext.Text, str]]:
    """Draw fig and give each drawn text that has a decimal number with a dot"""
    with drawn_texts() as seen:
        fig.canvas.draw()
    return dotted(seen)
