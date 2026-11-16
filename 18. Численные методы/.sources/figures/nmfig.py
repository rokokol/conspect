"""Shared helpers for the figures of this course: colour roles and output folders.

Every colour is a ddlc-palette role or its tint. A script names a colour by its
meaning here (EXACT, APPROX, NODES), so the same convention reads the
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
EXACT = P["bow"]              # the exact solution, eigenfunction or limit
APPROX = P["natsuki"]         # an approximation being compared with it
NODES = P["yuri"]             # grid nodes, collocation points, iterates
AUX = tint(P["rule"], 0.4)    # grids, auxiliary lines, error bounds
MUTED = P["ash"]              # axes guides and inactive parts

TOPICS = {
    1: "01. Итерационные методы и неподвижная точка",
    2: "02. Квадратурные методы",
    3: "03. Проекционные методы",
    4: "04. Спектральные задачи",
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
