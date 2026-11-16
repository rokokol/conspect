"""Behaviour of the shared figure kit: deterministic data, regions that match
the model, files that open. Run: python -m pytest -q test_figkit.py"""
import numpy as np
import pytest
from imageio.v3 import imread, improps
from matplotlib.colors import to_rgb

import figkit as fk


class Const:
    """A fitted classifier that answers one class everywhere."""

    def __init__(self, label, n_classes=2):
        self.label = label
        self.classes_ = np.arange(n_classes)

    def predict(self, X):
        return np.full(len(X), self.label)

    def predict_proba(self, X):
        p = np.zeros((len(X), len(self.classes_)))
        p[:, self.label] = 1.0
        return p


class HalfPlane:
    """Class 1 right of x = 0, class 0 left of it."""

    classes_ = np.array([0, 1])

    def predict(self, X):
        return (X[:, 0] > 0).astype(int)

    def predict_proba(self, X):
        p1 = (X[:, 0] > 0).astype(float)
        return np.c_[1 - p1, p1]


@pytest.mark.parametrize("name", fk.DATASETS)
def test_datasets_are_deterministic(name):
    X1, y1 = fk.dataset(name)
    X2, y2 = fk.dataset(name)
    assert np.array_equal(X1, X2) and np.array_equal(y1, y2)
    assert X1.ndim == 2 and len(X1) == len(y1) >= 20


def test_classification_sets_have_expected_classes():
    assert set(fk.dataset("moons")[1]) == {0, 1}
    assert set(fk.dataset("blobs3")[1]) == {0, 1, 2}


def test_unknown_dataset_is_an_error():
    with pytest.raises(KeyError):
        fk.dataset("nope")


def _pixel(img, fx, fy):
    """RGB in [0, 1] at a fraction of the image width and height."""
    h, w = img.shape[:2]
    return img[int(fy * h), int(fx * w), :3] / 255.0


def _closest(rgb, candidates):
    """Candidate whose hue is nearest: a region is a light tint of its class
    colour, so lightness differs by design and only the hue identifies it."""
    from colorsys import rgb_to_hsv

    def hue(c):
        return rgb_to_hsv(*c)[0]

    def gap(a, b):
        d = abs(a - b) % 1.0
        return min(d, 1 - d)

    d = {k: gap(hue(rgb), hue(to_rgb(v))) for k, v in candidates.items()}
    return min(d, key=d.get)


def _render(model, X, y, path, **kw):
    fig, ax = fk.subplots(1, 1, size=(4, 4))
    fk.plot_decision(ax, model, X, y, show_points=False, **kw)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fk.save(fig, path)
    return imread(path)


def test_region_colour_follows_the_prediction(tmp_path):
    X = np.array([[-1.0, -1.0], [1.0, 1.0]])
    y = np.array([0, 1])
    img = _render(HalfPlane(), X, y, tmp_path / "h.png")
    poles = {0: fk.CLASS_COLORS[0], 1: fk.CLASS_COLORS[1]}
    assert _closest(_pixel(img, 0.15, 0.5), poles) == 0
    assert _closest(_pixel(img, 0.85, 0.5), poles) == 1


@pytest.mark.parametrize("label", [0, 1, 2])
def test_multiclass_region_uses_the_class_colour(tmp_path, label):
    X = np.array([[-1.0, -1.0], [1.0, 1.0], [0.0, 1.0]])
    y = np.array([0, 1, 2])
    img = _render(Const(label, 3), X, y, tmp_path / "m.png")
    tints = {k: fk.region_color(k) for k in range(3)}
    assert _closest(_pixel(img, 0.5, 0.5), tints) == label


def _legends(ax):
    from matplotlib.legend import Legend
    return [c for c in ax.get_children() if isinstance(c, Legend)]


def _axes_text(ax):
    return " ".join([t.get_text() for t in ax.texts] +
                    [t.get_text() for lg in _legends(ax) for t in lg.get_texts()])


def test_scores_are_written_on_the_axes():
    X, y = fk.dataset("moons")
    fig, ax = fk.subplots(1, 1)
    tr, te = slice(0, 150), slice(150, None)
    fk.plot_decision(ax, HalfPlane(), X[tr], y[tr], X_test=X[te], y_test=y[te])
    texts = _axes_text(ax)
    acc_tr = (HalfPlane().predict(X[tr]) == y[tr]).mean()
    acc_te = (HalfPlane().predict(X[te]) == y[te]).mean()
    assert f"{acc_tr:.2f}" != f"{acc_te:.2f}"
    assert f"{acc_tr:.2f}" in texts and f"{acc_te:.2f}" in texts


def _key(ax):
    """(label, marker face is hollow) for every entry of the score key."""
    keys = [lg for lg in _legends(ax) if lg.get_texts()[0].get_text().startswith("train")]
    assert len(keys) == 1, "the score key is missing"
    return [(t.get_text(), to_rgb(h.get_markerfacecolor()) == (1.0, 1.0, 1.0))
            for t, h in zip(keys[0].get_texts(), keys[0].legend_handles)]


def test_score_key_shows_filled_train_and_hollow_test():
    # The figure itself says which points are which (notation.md: filled train, hollow test)
    X, y = fk.dataset("moons")
    fig, ax = fk.subplots(1, 1)
    fk.plot_decision(ax, HalfPlane(), X[:150], y[:150], X_test=X[150:], y_test=y[150:])
    (tr_label, tr_hollow), (te_label, te_hollow) = _key(ax)
    assert tr_label.startswith("train") and not tr_hollow
    assert te_label.startswith("test") and te_hollow
    fk.plt.close(fig)


def test_score_key_without_test_has_only_train():
    X, y = fk.dataset("moons")
    fig, ax = fk.subplots(1, 1)
    fk.plot_decision(ax, HalfPlane(), X, y)
    assert [label.split()[0] for label, _ in _key(ax)] == ["train"]
    fk.plt.close(fig)


def test_a_script_legend_does_not_erase_the_score_key():
    X, y = fk.dataset("moons")
    fig, ax = fk.subplots(1, 1)
    fk.plot_decision(ax, HalfPlane(), X[:150], y[:150], X_test=X[150:], y_test=y[150:])
    ax.plot([0, 1], [0, 1], label="своя кривая")
    ax.legend(loc="upper left")
    assert len(_key(ax)) == 2
    fk.plt.close(fig)


def test_gif_has_all_frames_and_loops(tmp_path):
    def draw(ax, i):
        ax.plot([0, 1], [0, i])

    out = tmp_path / "a.gif"
    fk.gif(draw, 5, out, size=(2, 2))
    frames = imread(out, index=None)
    assert frames.shape[0] == 5
    assert improps(out, index=0).shape[:2] == frames.shape[1:3]
    from PIL import Image
    assert Image.open(out).info.get("loop") == 0


def test_complexity_curve_never_marks_the_test_optimum():
    vals, train, test = [1, 2, 3, 4], [1.0, 0.9, 0.8, 0.7], [0.5, 0.9, 0.6, 0.55]
    fig, ax = fk.subplots(1, 1)
    assert fk.complexity_curve(ax, vals, train, test, xlabel="k") is None
    assert not [ln for ln in ax.lines if ln.get_linestyle() == "--"]
    fk.plt.close(fig)
    fig, ax = fk.subplots(1, 1)
    best = fk.complexity_curve(ax, vals, train, test, val=[0.6, 0.7, 0.8, 0.75], xlabel="k")
    assert best == 2
    marks = [ln for ln in ax.lines if ln.get_linestyle() == "--"]
    assert len(marks) == 1 and marks[0].get_xdata()[0] == 3
    fk.plt.close(fig)
    fig, ax = fk.subplots(1, 1)
    assert fk.complexity_curve(ax, vals, train, test, val=[0.3, 0.2, 0.1, 0.4], better="min", xlabel="k") == 2
    fk.plt.close(fig)


def test_a_script_fails_when_a_solver_does_not_converge():
    # pytest resets warning filters per test, so run it the way a figure script runs.
    import subprocess
    import sys
    from pathlib import Path
    code = ("import numpy as np, figkit as fk\n"
            "from sklearn.linear_model import Lasso\n"
            "X, y = fk.dataset('reg1d')\n"
            "Lasso(alpha=1e-9, max_iter=2, tol=1e-12).fit(np.c_[X, X**2, X**3], y)\n")
    r = subprocess.run([sys.executable, "-c", code], cwd=Path(fk.__file__).parent,
                       capture_output=True, text=True)
    assert r.returncode != 0 and "ConvergenceWarning" in r.stderr


def test_loss_contours_use_every_band_and_darken_uphill(tmp_path):
    # A bowl with a huge range: equal-width colour steps would paint it one colour.
    g = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(g, g)
    Z = np.exp(X ** 2 + Y ** 2)
    fig, ax = fk.subplots(1, 1, size=(4, 4))
    # Fill only: the grey level lines would add colours of their own.
    cs = fk.loss_contourf(ax, X, Y, Z, n=10, lines=False)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    img = imread(fk.save(fig, tmp_path / "c.png"))[..., :3].astype(float)
    assert len(cs.levels) >= 8
    lum = img.mean(axis=2)
    h, w = lum.shape
    # Not the very corner: it holds the single maximum, on the top level's edge.
    centre, edge = lum[h // 2, w // 2], lum[h // 10, w // 10]
    assert centre > edge + 40  # minimum light, far corner dark
    # Along the diagonal from the centre towards a corner (the top bands live in
    # the corners) every band shows, each darker than the last.
    k = np.arange(min(h, w) // 2, int(min(h, w) * 0.95))
    ray = lum[k, k]
    steps = [v for i, v in enumerate(ray) if i == 0 or v != ray[i - 1]]
    assert len(steps) >= 8
    assert all(b <= a for a, b in zip(steps, steps[1:]))


def test_accent_is_not_a_data_colour():
    assert fk.ACCENT not in {fk.TRAIN_C, fk.TEST_C, fk.MODEL_C, fk.MODEL2_C, *fk.CATEGORICAL}


def test_colours_come_from_the_vendored_palette():
    css = (fk.ddlc_theme.HERE / "palette.css").read_text(encoding="utf-8").lower()
    for c in [fk.BLUE, fk.RED, *fk.CATEGORICAL, fk.TEXT, fk.TRAIN_C, fk.TEST_C]:
        assert c.lower() in css
    assert len(set(fk.CATEGORICAL)) == 3 and fk.BLUE != fk.RED


def test_theme_font_is_registered_and_titles_are_its_black():
    names = {f.name for f in fk.ddlc_theme.ddlc_fonts.font_manager.fontManager.ttflist}
    assert fk.BODY_FONT in names
    assert fk.BODY_FONT == "Mya Nunito Static" and fk.plt.rcParams["font.family"][0] == fk.BODY_FONT
    fig, ax = fk.subplots(1, 1)
    t = ax.set_title("Заголовок λ")
    assert t.get_fontfamily()[0] == fk.BODY_FONT and t.get_fontweight() == 900
    fk.plt.close(fig)


def test_attachments_resolve_to_the_topic_folder():
    p = fk.attachments(2)
    assert p.name == "00. Вложения" and p.parent.name.startswith("02. ")
    assert p.parent.parent.name == "content" and p.is_dir()
    assert fk.attachments("02") == p
    with pytest.raises(FileNotFoundError):
        fk.attachments(99)


def test_save_writes_an_opaque_png(tmp_path):
    fig, ax = fk.subplots(1, 1)
    ax.plot([0, 1], [0, 1])
    out = tmp_path / "p.png"
    fk.save(fig, out)
    img = imread(out)
    assert img.shape[2] in (3, 4)
    if img.shape[2] == 4:
        assert img[..., 3].min() == 255
