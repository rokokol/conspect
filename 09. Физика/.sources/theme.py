"""Shared matplotlib furniture for every figure script in this course: background, grid,
spine, tick and text colours, and the body font. Importing this module applies them.

Colours are the neutral "interface" role of ddlc-palette (github.com/rokokol/ddlc-palette),
light variant, matching ddlc-themes' own ddlc.mplstyle. The fonts are the vault's Obsidian
theme (Mya Nunito Static: Medium for prose, Black for bold and titles), taken from the shared
ddlc_fonts and never set here, so a figure's labels read like the note's own prose. Math
inside $...$ is set in the same face, through the math keys ddlc_fonts applies.

Each script's own diagram colours (poles, charges, particles, materials, and so on) are that
script's business and are untouched here — this module sets matplotlib's *defaults*, and a
colour a script names explicitly (almost every stroke in these figures) always wins over a
default.

Import for the side effect, same as the four *_common.py helpers: `import theme`.
A script with its own font.size (magnetic_field.py uses 12) sets it after the import.
"""
import matplotlib.pyplot as plt

import course  # noqa: F401  puts the shared ddlc_figures on sys.path
import ddlc_fonts  # noqa: F401  applies the vault's fonts
import ddlc_numbers
from ddlc_numbers import keep_dots, num  # noqa: F401  a number of a label is written with num()
from ddlc_palette import P

ddlc_numbers.install()  # the ticks get the decimal comma

PAPER = P["paper"]  # page ground
ASH = P["ash"]  # neutral separators: grid, spines
JACKET = P["jacket"]  # the one mid grey, here for tick marks
INK = P["ink"]  # text


def tint(color, amount):
    """Mix a colour with white: amount 0 keeps it, 1 gives white. A body's fill is a role at
    0.7 to 0.85, its outline the role itself or INK"""
    c = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return "#" + "".join(f"{round(255 * (x + (1 - x) * amount)):02x}" for x in c)


def saver(out):
    """The save(fig, name, **savefig) of a script whose figures go to the folder out: it
    makes the folder, gives a name with no extension .png, passes the keywords to savefig
    and closes the figure. A script writes `save = saver(OUT)` once"""
    def save(fig, name, **savefig):
        out.mkdir(parents=True, exist_ok=True)
        path = out / (name if "." in name else f"{name}.png")
        fig.savefig(path, **savefig)
        plt.close(fig)
        return path
    return save


# The colour roles of the course's diagrams: a script names a colour by its meaning here and
# never writes a hex. The lecturer's conventions hold: the north pole and the north end of a
# needle are BLUE, the south pole RED; hot is RED and cold BLUE; a positive charge RED and a
# negative one BLUE
RED = P["bow"]  # force, heat, the south pole, a positive charge, the thing the figure is about
BLUE = P["skirt"]  # the north pole, cold, a negative charge, a second quantity beside RED
GREEN = P["ribbon"]  # a third quantity, light rays, a result that is right
VIOLET = P["yuri"]  # a fourth quantity, an image in optics
ACCENT = P["plum"]  # a highlighted point or a fifth quantity
SKY = P["sayori-eye"]  # water, glass, air, gas: fill it with tint(SKY, 0.6–0.8)
COPPER = P["monika"]  # copper, wood, earth, warm metal
WARM = P["sayori"]  # flame, gold, oil, sand, anything yellow or orange
PINK = P["natsuki"]  # a soft warm fill
METAL = tint(INK, 0.55)  # steel, iron, lead and other grey metal; light grey parts tint(INK, 0.8)
MUTED = JACKET  # guides, auxiliary lines, inactive parts
LIGHT = tint(ASH, 0.5)  # a neutral light fill: tables, boxes, backgrounds of a part
SERIES = [RED, BLUE, GREEN, VIOLET, COPPER]  # curves of several cases, in this order

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 13,
        "figure.dpi": 100,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "figure.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": ASH,
        "grid.color": ASH,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "xtick.color": JACKET,
        "ytick.color": JACKET,
        "xtick.labelcolor": INK,
        "ytick.labelcolor": INK,
    }
)
