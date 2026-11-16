"""Behaviour of the shared figure theme: python -m pytest test_ddlc_theme.py"""
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402

import ddlc_theme as t  # noqa: E402

HERE = Path(__file__).resolve().parent


def test_vendored_files_match_the_lock():
    lock = json.loads((HERE / "vendor.lock").read_text(encoding="utf-8"))
    for f in lock["files"]:
        body = (HERE / Path(f["path"]).name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == f["sha256"], f["path"]


def test_palette_is_read_from_the_vendored_css_by_name():
    css = (HERE / "palette.css").read_text(encoding="utf-8")
    names = re.findall(r"--ddlc-([a-z-]+):", css)
    assert names and sorted(t.P) == sorted(names)
    assert all(re.fullmatch(r"#[0-9A-Fa-f]{6}", v) for v in t.P.values())


def test_style_sets_page_and_text_from_the_palette():
    rc = plt.rcParams
    assert to_hex(rc["figure.facecolor"]) == t.P["paper"].lower()
    assert to_hex(rc["savefig.facecolor"]) == t.P["paper"].lower()
    assert to_hex(rc["text.color"]) == t.P["ink"].lower()
    assert to_hex(rc["axes.edgecolor"]) == t.P["ash"].lower()


def test_cycle_is_the_theme_cycle():
    cycle = [to_hex(c["color"]) for c in plt.rcParams["axes.prop_cycle"]]
    assert cycle == [c.lower() for c in t.CYCLE]
    assert set(cycle) <= {v.lower() for v in t.P.values()}


def _face(path):
    """usWeightClass of a font file, whether it is italic, and whether it still has variation axes."""
    from fontTools.ttLib import TTFont
    f = TTFont(path)
    return f["OS/2"].usWeightClass, bool(f["OS/2"].fsSelection & 1), "fvar" in f


def _find(family=None, **kw):
    return Path(font_manager.findfont(
        font_manager.FontProperties(family=family or plt.rcParams["font.family"], **kw),
        fallback_to_default=False))


def test_the_body_font_is_the_vendored_mya_nunito_static_not_a_system_font():
    assert t.BODY_FONT == "Mya Nunito Static"
    assert t.FONT_STACK[0] == t.BODY_FONT
    path = _find(t.BODY_FONT)
    assert path.parent == HERE and path.name.startswith("MyaNunitoStatic-")


def test_prose_is_medium_500_as_a_static_face():
    assert plt.rcParams["font.weight"] == 500
    path = _find(weight=plt.rcParams["font.weight"])
    assert path.name == "MyaNunitoStatic-Medium.ttf"
    assert _face(path) == (500, False, False)


def test_bold_resolves_to_black_900_without_a_weight_warning(caplog):
    for bold in ("bold", 700, 900):
        assert _face(_find(t.BODY_FONT, weight=bold)) == (900, False, False)
    # every font of the stack answers the weights a script may ask for, so no "Failed to find font weight"
    for weight in (400, 500, "bold", 900):
        for family in plt.rcParams["font.family"]:
            _find(family, weight=weight)
    assert not [r for r in caplog.records if "Failed to find font weight" in r.getMessage()]


def test_titles_are_the_body_font_in_black():
    assert plt.rcParams["axes.titleweight"] == 900
    assert plt.rcParams["figure.titleweight"] == 900
    fig, ax = plt.subplots()
    for title in (ax.set_title("Кольца защиты IPv6"), fig.suptitle("Кольца 0–3")):
        assert _face(_find(title.get_fontfamily(), weight=title.get_fontweight())) == (900, False, False)
    plt.close(fig)


def test_no_figure_font_is_doki():
    fig, ax = plt.subplots()
    families = [*plt.rcParams["font.family"], *ax.set_title("x").get_fontfamily(), *fig.suptitle("y").get_fontfamily()]
    plt.close(fig)
    assert not [f for f in families if "doki" in f.lower()]
    assert not hasattr(t, "TITLE_FONT")


def test_math_is_set_in_mya_nunito_static_and_its_variables_in_italic():
    rc = plt.rcParams
    assert rc["mathtext.fontset"] == "custom"
    # one string and nothing else is read as a fontconfig pattern, as mathtext reads these keys
    rm = font_manager.FontProperties(rc["mathtext.rm"])
    it = font_manager.FontProperties(rc["mathtext.it"])
    assert font_manager.findfont(rm, fallback_to_default=False).endswith("MyaNunitoStatic-Medium.ttf")
    assert _face(font_manager.findfont(it, fallback_to_default=False))[1] is True


def test_drawing_text_with_math_logs_no_weight_warning(caplog):
    fig, ax = plt.subplots()
    ax.set_title(r"Закон $\frac{\sqrt{x}}{\|w\|_2^2}$", fontweight="bold")
    ax.text(0.5, 0.5, r"$\lambda \to \infty$ и $\left(\frac{a}{b}\right)$", fontweight="bold")
    ax.set_xlabel(r"$\sum_i x_i$, \(\alpha\)")
    fig.canvas.draw()
    plt.close(fig)
    assert not [r for r in caplog.records if "Failed to find font weight" in r.getMessage()]


def test_the_body_font_itself_has_the_greek_arrows_and_operators():
    from fontTools.ttLib import TTFont
    cmap = TTFont(_find(weight=500)).getBestCmap()
    assert [ch for ch in "λπΩΔ→⇒↦∈∀≤≥∞−ℝ‖²₁ⁿ" if ord(ch) not in cmap] == []


def test_symbols_and_cyrillic_render_without_missing_glyph_warnings(recwarn):
    fig, ax = plt.subplots()
    ax.set_xlabel("λ → ∈ Ω, ≤ ∞ и кириллица, ℝⁿ")
    ax.set_title("Заголовок λ → x")
    fig.canvas.draw()
    plt.close(fig)
    assert not [w for w in recwarn if "missing from font" in str(w.message)]


def test_titles_keep_an_explicit_family():
    fig, ax = plt.subplots()
    assert ax.set_title("x", fontfamily="DejaVu Sans").get_fontfamily()[0] == "DejaVu Sans"
    plt.close(fig)


def test_fonts_alone_leave_the_axes_style_of_the_importer_untouched():
    import subprocess
    import sys
    # Physics takes the faces alone, so its formulas depend on the math keys set here, not by the style
    code = ("import ddlc_fonts, matplotlib as m; r = m.rcParams;"
            "print(r['axes.titlelocation'], r['axes.facecolor'], r['mathtext.fontset'], r['mathtext.rm'],"
            " r['font.weight'], r['font.family'][0], sep='|')")
    out = subprocess.run([sys.executable, "-c", code], cwd=HERE, check=True,
                         capture_output=True, text=True).stdout.strip().split("|")
    assert out == ["center", "white", "custom", "Mya Nunito Static", "500", "Mya Nunito Static"]


def test_tint_mixes_a_palette_colour_with_paper():
    assert to_hex(t.tint(t.P["bow"], 0)) == t.P["bow"].lower()
    assert to_hex(t.tint(t.P["bow"], 1)) == "#ffffff"
    mid = t.tint("#000000", 0.5)
    assert all(abs(c - 0.5) < 1e-9 for c in mid)
