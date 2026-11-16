"""Behaviour of the decimal comma for figures: python -m pytest test_ddlc_numbers.py

The check that runs a figure script, check_numbers.py, has its own tests in the conspect skill"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import pytest  # noqa: E402

import ddlc_theme as t  # noqa: E402
from ddlc_numbers import dotted_numbers, figure_dots  # noqa: E402


def _labels(ax, axis="x"):
    ax.figure.canvas.draw()
    ticks = (ax.xaxis if axis == "x" else ax.yaxis).get_ticklabels()
    return [lab.get_text() for lab in ticks if lab.get_text()]


@pytest.fixture
def ax():
    fig, ax = plt.subplots()
    yield ax
    plt.close(fig)


def test_num_writes_a_comma_in_text_and_a_braced_comma_in_math():
    assert t.num(0.5) == "0,50"
    assert t.num(-2.75, 1) == "-2,8"
    assert t.num(3.14159, 3, math=True) == "3{,}142"
    assert "." not in t.num(12.0, 0)


@pytest.mark.parametrize("x, spec, plain, math", [
    (0.45, "+.2f", "+0,45", "+0{,}45"),
    (0.498, ".1%", "49,8%", "49{,}8%"),
    (0.0064, ".1e", "6,4e-03", "6{,}4e-03"),
    (0.00562, ".3g", "0,00562", "0{,}00562"),
])
def test_num_takes_a_format_spec_where_digits_are_not_enough(x, spec, plain, math):
    assert t.num(x, spec) == plain
    assert t.num(x, spec, math=True) == math


def test_num_with_no_digits_writes_the_shortest_form_as_g_does():
    assert t.num(0.5, None) == "0,5"
    assert t.num(2.0, None) == "2"
    assert t.num(0.125, None, math=True) == "0{,}125"
    assert t.num(1.5e-7, None) == "1,5e-07"


@pytest.mark.parametrize("mathtext", [False, True])
def test_fractional_ticks_get_a_comma_with_no_call(mathtext):
    # The formatter reads use_mathtext when the axes are made, so the axes come after it
    with plt.rc_context({"axes.formatter.use_mathtext": mathtext}):
        fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 0.5])
    labels = _labels(ax) + _labels(ax, "y")
    plt.close(fig)
    assert all(("$" in s) == mathtext for s in labels), labels
    fractional = [s for s in labels if "," in s]
    assert fractional, labels
    assert not any("." in s for s in labels), labels
    # Inside $...$ a bare comma is punctuation and draws a space after itself
    for s in fractional:
        assert ("{,}" in s) == ("$" in s), s


def test_a_colorbar_gets_the_comma_too():
    fig, ax = plt.subplots()
    image = ax.imshow([[0, 0.5], [0.25, 1]])
    bar = fig.colorbar(image)
    fig.canvas.draw()
    labels = [x.get_text() for x in bar.ax.get_yticklabels() if x.get_text()]
    plt.close(fig)
    assert any("," in s for s in labels) and not any("." in s for s in labels), labels


def test_the_colorbar_of_filled_contours_gets_the_comma_too():
    # A contour set's colorbar has boundaries and so a function scale, not a linear one
    fig, ax = plt.subplots()
    filled = ax.contourf([[0, 0.5], [0.25, 1]], levels=[0, 0.25, 0.5, 0.75, 1])
    bar = fig.colorbar(filled)
    fig.canvas.draw()
    labels = [x.get_text() for x in bar.ax.get_yticklabels() if x.get_text()]
    plt.close(fig)
    assert any("," in s for s in labels) and not any("." in s for s in labels), labels


def test_the_offset_text_gets_a_comma(ax):
    ax.plot([0, 1], [1000.1, 1000.6])
    ax.yaxis.get_major_formatter().set_useOffset(1000.25)
    ax.figure.canvas.draw()
    offset = ax.yaxis.get_offset_text().get_text()
    assert offset and "." not in offset and "," in offset, offset


def test_a_text_the_script_wrote_is_drawn_as_written(ax):
    label = ax.text(0, 0, "AUC 0.91")
    ax.figure.canvas.draw()
    assert label.get_text() == "AUC 0.91"


@pytest.mark.parametrize("text, found", [
    ("AUC 0.91", ["0.91"]),
    ("$x=0.5$ при 1.5 с", ["0.5", "1.5"]),
    ("-2.75 и 2.5e-3", ["2.75", "2.5"]),
    ("0.5см", ["0.5"]),
    ("$\\mathdefault{0.5}$", ["0.5"]),
    ("$H\\approx0.693$", ["0.693"]),
    ("$\\mu0.5$", ["0.5"]),
    ("$0{,}5$ и 0,5", []),
    ("192.168.0.1", []),
    ("24.10.2026", []),
    ("HTTP/1.1", []),
    ("$\\hspace{0.5em}x$", []),
    ("v2.0", []),
    ("1...5", []),
])
def test_dotted_numbers_names_each_decimal_written_with_a_dot(text, found):
    assert dotted_numbers(text) == found


def test_figure_dots_finds_every_kind_of_text_and_spares_keep_dots(ax):
    ax.plot([0, 1], [0, 1], label="η = 0.35")
    ax.text(0.5, 0.5, "3.36 кДж")
    ax.annotate("AUC 0,91", (0.2, 0.2))
    ax.set_title("порог 0.5")
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    t.keep_dots(ax.set_xlabel("задача 17.10"))
    ax.legend()
    found = {text for _, text in figure_dots(ax.figure)}
    assert {"η = 0.35", "3.36 кДж", "порог 0.5"} <= found, found
    # the ticks of a formatter the script chose are text like any other
    assert {"0.2", "0.4"} <= found, found
    assert "AUC 0,91" not in found and "задача 17.10" not in found, found


def test_figure_dots_skips_a_hidden_text(ax):
    ax.text(0, 0, "0.5").set_visible(False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    assert figure_dots(ax.figure) == []


def test_reading_a_figure_leaves_the_drawing_of_text_as_it_was(ax):
    import matplotlib.text as mtext

    draw = mtext.Text.draw
    ax.text(0, 0, "0.5")
    figure_dots(ax.figure)
    assert mtext.Text.draw is draw
