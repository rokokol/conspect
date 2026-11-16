"""Shared helpers for the figures of this course: colour roles and output folders.

Every colour is a ddlc-palette role or its tint. A script names a colour by its
meaning here (CORE, CLADDING, MODE), so the same convention reads the
same way in every figure of the course.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

P = ddlc_theme.P
tint = ddlc_theme.tint
CYCLE = ddlc_theme.CYCLE
num = ddlc_theme.num
keep_dots = ddlc_theme.keep_dots

INK = P["ink"]
MODE = P["bow"]                  # the field, mode profile or curve the figure is about
ODD = P["rule"]                  # the odd branch or mode drawn against MODE: a full colour, never a pale one
CORE = tint(P["bow"], 0.85)      # pale fill of the guiding layer or core of a waveguide
CLADDING = tint(P["rule"], 0.7)  # pale fill of the cladding, substrate or cover around it
AUX = tint(P["rule"], 0.4)       # grids, auxiliary lines, asymptotes
HIGHLIGHT = P["yuri"]            # a root, a cutoff point, a distinguished value
MUTED = P["ash"]                 # axes guides and inactive parts

TOPICS = {
    1: "01. Классификация и модельные уравнения",
    2: "02. Задачи для струны и стержня",
    3: "03. Эллиптические уравнения",
    4: "04. Уравнения Максвелла",
    5: "05. Плоские волны на разделе сред",
    6: "06. Волноводы",
    7: "07. Дифракция",
}


def out_dir(topic: int) -> Path:
    """The attachments folder of a topic, created with its .nomedia marker."""
    d = COURSE / "content" / TOPICS[topic] / "00. Вложения"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".nomedia").touch()
    return d


def save(fig, topic: int, name: str) -> Path:
    """Write <name>.png into the topic's attachments folder and close the figure"""
    path = out_dir(topic) / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(path)
    return path
