"""Shared helpers for the figures of this course: colour roles and output folders.

Every colour is a ddlc-palette role or its tint. A script names a colour by its
meaning here (SOLUTION, FIELD, HIGHLIGHT), so the same convention reads the
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
num = ddlc_theme.num  # every number of a label: num(0.25) gives 0,25
keep_dots = ddlc_theme.keep_dots

INK = P["ink"]
SOLUTION = P["bow"]          # the solution or curve the figure is about
FIELD = tint(P["rule"], 0.4)  # direction field, isoclines, auxiliary curves
HIGHLIGHT = P["natsuki"]      # a point, a tangent, an approximation being compared
MUTED = P["ash"]              # axes guides and inactive parts

TOPICS = {
    1: "01. Введение",
    2: "02. Уравнения первого порядка, разрешимые в квадратурах",
    3: "03. Задача Коши",
    4: "04. Численное решение задачи Коши",
    5: "05. Уравнения, не разрешённые относительно производной, и понижение порядка",
    6: "06. Линейные уравнения и системы",
    7: "07. Линейные уравнения и системы с постоянными коэффициентами",
    8: "08. Операционный метод",
    9: "09. Решение уравнений степенными рядами",
    10: "10. Краевые задачи",
    11: "11. Теория устойчивости",
    12: "12. Уравнения с частными производными первого порядка",
}


def out_dir(topic: int) -> Path:
    """The attachments folder of a topic, created with its .nomedia marker."""
    d = COURSE / "content" / TOPICS[topic] / "00. Вложения"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".nomedia").touch()
    return d


def save(fig, topic: int, name: str) -> Path:
    """Write <name>.png into the topic's attachments folder and close the figure."""
    path = out_dir(topic) / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(path)
    return path
