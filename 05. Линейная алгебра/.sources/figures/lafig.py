"""Shared helpers for the figures of this course: colour roles and output folders.

Every colour is a ddlc-palette role or its tint. A script names a colour by its
meaning here (VECTOR, IMAGE, HIGHLIGHT), so the same convention reads the
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
VECTOR = P["bow"]             # the vector, curve or surface the figure is about
IMAGE = P["natsuki"]          # its image under an operator, a second object to compare
AUX = tint(P["rule"], 0.4)    # grids, auxiliary lines, sections
HIGHLIGHT = P["yuri"]         # a point, an angle, a distinguished direction
MUTED = P["ash"]              # axes guides and inactive parts

TOPICS = {
    1: "01. Комплексные числа и многочлены",
    2: "02. Векторная алгебра",
    3: "03. Прямые и плоскости",
    4: "04. Определители",
    5: "05. Матрицы",
    6: "06. Линейные пространства",
    7: "07. Евклидовы пространства",
    8: "08. Подпространства",
    9: "09. Линейные операторы",
    10: "10. Линейные уравнения",
    11: "11. Строение линейного оператора",
    12: "12. Операторы в евклидовом пространстве",
    13: "13. Квадратичные формы",
    14: "14. Кривые второго порядка",
    15: "15. Поверхности второго порядка",
    16: "16. Теория Фредгольма",
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
