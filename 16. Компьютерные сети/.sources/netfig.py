"""Colour roles shared by the protocol-header diagrams of this course.

A header field is a pale fill with a darker edge. The roles name what a fill
means across diagrams, and every colour is a ddlc-palette role or its tint.
"""
import matplotlib

matplotlib.use("Agg")

from course import COURSE  # noqa: E402,F401  re-exported for the scripts
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
tint = ddlc_theme.tint
num = ddlc_theme.num  # every number of a label: num(0.25) gives 0,25
keep_dots = ddlc_theme.keep_dots

EDGE = P["plum"]
FIELD = P["dot"]                       # an ordinary header field
VIOLET = tint(P["yuri"], 0.72)         # a field the diagram singles out
PEACH = tint(P["sayori"], 0.45)        # an outer or added header
SKY = tint(P["sayori-eye"], 0.6)       # a third kind of field
GREEN = tint(P["monika-eye"], 0.65)    # payload and data
GREY = tint(P["jacket"], 0.7)          # framing, reserved and padding
ACCENT = P["bow"]                      # a size bracket or a boundary line
MUTED = P["jacket"]                    # bit rulers and their captions
SUBTEXT = P["yuri-shadow"]             # the size line under a field name
