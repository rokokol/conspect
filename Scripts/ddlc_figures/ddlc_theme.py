"""The owner's ddlc look for matplotlib figures in any course of the vault.

Importing this module applies the theme. A course reaches it through the
`.sources/course.py` of that course, which puts this folder on sys.path.

Colours come from ddlc-palette and the axes look from ddlc-themes, both
vendored here at pinned commits (vendor.lock, fetch_vendor.py), so no hex
lives in this file or in a figure script. A script names a colour by its
palette role: P["bow"], P["rule"], P["ink"]. The series cycle is CYCLE.

The fonts are those of the vault's Obsidian theme and come from ddlc_fonts,
which this module imports and re-exports: BODY_FONT and FONT_STACK.
No other file of the vault chooses a figure's font.

The decimal comma comes from ddlc_numbers: this module makes its comma
formatter the default of the ticks, and re-exports num(x), which a script
writes every number of a label with, and keep_dots(text). The conspect
skill's check_numbers.py names the texts that still have a dot.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ddlc_palette import P  # noqa: E402  the palette by name, from the vendored palette.css

plt.style.use(HERE / "ddlc.mplstyle")
CYCLE = [c["color"] if str(c["color"]).startswith("#") else "#" + c["color"]
         for c in plt.rcParams["axes.prop_cycle"]]
import ddlc_cmaps  # noqa: E402,F401  registers ddlc_seq, ddlc_div and their dark forms
import ddlc_fonts  # noqa: E402,F401  applies the fonts over the style's font keys
from ddlc_fonts import BODY_FONT, FONT_STACK  # noqa: E402,F401
import ddlc_numbers  # noqa: E402
from ddlc_numbers import keep_dots, num  # noqa: E402,F401

ddlc_numbers.install()


def tint(color, amount):
    """Mix a colour with white: amount 0 keeps it, 1 gives white. For pale fills."""
    c = to_rgb(color)
    return tuple(x + (1 - x) * amount for x in c)
