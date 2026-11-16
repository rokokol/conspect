"""Shared figure kit for the ML trainings course.

Every figure script imports this module, so all figures share the same data,
palette and look, and a comparison between two models changes only the model.

The look is the owner's ddlc theme, taken from the vault's shared ddlc_theme
(01. Data/04. Scripts/ddlc_figures, vendored there at a pinned commit): the
axes style, palette.css for every colour by name, so no hex lives here, and
the fonts, which this kit never sets itself. Binary classes are rule (class 0)
and bow (class 1), an adjacent pair of the theme's cycle that it validated for
colour blindness; a third class takes monikaEye, the same as the interactive
pages. Train and test curves are the first two series of the cycle, plum and bow.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap  # noqa: E402
from matplotlib.legend import Legend  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from sklearn import datasets as skd  # noqa: E402

SEED = 0

# A solver that stopped short draws a wrong picture that looks right: make it fail.
import warnings  # noqa: E402

from sklearn.exceptions import ConvergenceWarning  # noqa: E402

warnings.simplefilter("error", ConvergenceWarning)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course import COURSE  # noqa: E402,F401  also puts the shared ddlc_figures on sys.path

# Importing ddlc_theme applies the theme: style, palette P, cmaps, fonts and titles.
import ddlc_theme  # noqa: E402
from ddlc_theme import BODY_FONT, P, keep_dots, num, tint  # noqa: E402,F401  num(0.25) gives 0,25

BLUE, RED, GREY = P["rule"], P["bow"], P["paper"]
CATEGORICAL = [P["rule"], P["bow"], P["monika-eye"]]
CLASS_COLORS = {0: BLUE, 1: RED}
TEXT, TEXT_2, GRIDC = P["ink"], P["jacket"], P["ash"]
TRAIN_C, TEST_C = P["plum"], P["bow"]
# A model's curve drawn over train/test points: never plum, which is train.
MODEL_C, MODEL2_C = P["rule"], P["monika-eye"]
# Highlights (a chosen point, a threshold, an arrow) are ink: every hue of the
# palette already carries a role, and plum as accent was mistaken for train.
ACCENT = P["ink"]

# Region fills are tints, so full-colour points stay visible on their own class.
PROBA_CMAP = LinearSegmentedColormap.from_list("proba", [tint(BLUE, 0.55), GREY, tint(RED, 0.55)])

# Course overrides on top of the theme: a little more room for labels. Fonts are the theme's.
plt.rcParams.update({
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})


def _xor(n=300, noise=0.35):
    rng = np.random.default_rng(SEED)
    X = rng.uniform(-1.5, 1.5, size=(n, 2))
    y = ((X[:, 0] > 0) ^ (X[:, 1] > 0)).astype(int)
    return X + rng.normal(0, noise * 0.3, X.shape), y


def _reg1d(n=40, noise=0.25):
    rng = np.random.default_rng(SEED)
    x = np.sort(rng.uniform(0, 1, n))
    return x[:, None], np.sin(2 * np.pi * x) + rng.normal(0, noise, n)


DATASETS = {
    "moons": lambda: skd.make_moons(300, noise=0.3, random_state=SEED),
    "circles": lambda: skd.make_circles(300, noise=0.12, factor=0.45, random_state=SEED),
    "linear": lambda: skd.make_classification(
        300, n_features=2, n_redundant=0, n_informative=2, n_clusters_per_class=1,
        class_sep=1.2, flip_y=0.03, random_state=SEED),
    "blobs3": lambda: skd.make_blobs(300, centers=[(-2, -1), (2, -1), (0, 2.2)],
                                     cluster_std=1.1, random_state=SEED),
    "xor": _xor,
    "reg1d": _reg1d,
}


def dataset(name):
    """Fixed, seeded data set by name; KeyError for an unknown name."""
    X, y = DATASETS[name]()
    return np.asarray(X, float), np.asarray(y)


def split(X, y, test_size=0.3):
    from sklearn.model_selection import train_test_split
    return train_test_split(X, y, test_size=test_size, random_state=SEED,
                            stratify=y if len(np.unique(y)) < 10 else None)


def region_color(k):
    """Light tint of a multiclass label colour for its decision region."""
    return tint(CATEGORICAL[k], 0.62)


def subplots(rows, cols, size=None, **kw):
    size = size or (3.2 * cols, 3.0 * rows)
    fig, axes = plt.subplots(rows, cols, figsize=size, squeeze=True, **kw)
    return fig, axes


def _grid(X, margin=0.6, steps=300):
    lo, hi = X.min(0) - margin, X.max(0) + margin
    xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], steps), np.linspace(lo[1], hi[1], steps))
    return xx, yy, np.c_[xx.ravel(), yy.ravel()]


def _scatter(ax, X, y, n_classes, marker="o", hollow=False):
    for k in range(n_classes):
        c = CLASS_COLORS[k] if n_classes == 2 else CATEGORICAL[k]
        m = y == k
        ax.scatter(X[m, 0], X[m, 1], s=18, marker=marker, linewidths=0.8,
                   facecolors="white" if hollow else c, edgecolors=c if hollow else "white",
                   zorder=3)


def plot_decision(ax, model, X, y, *, X_test=None, y_test=None, proba=True,
                  show_points=True, title=None, scores=True):
    """Decision regions of a fitted classifier over the data's bounding box.

    Binary: P(class 1) on the diverging scale plus the 0.5 boundary.
    Multiclass: tinted regions of the predicted label.
    Train points are filled, test points hollow; accuracies go in a corner.
    """
    classes = np.asarray(getattr(model, "classes_", np.unique(y)))
    n = len(classes)
    allX = X if X_test is None else np.vstack([X, X_test])
    xx, yy, pts = _grid(allX)
    if n == 2 and proba and hasattr(model, "predict_proba"):
        z = model.predict_proba(pts)[:, 1].reshape(xx.shape)
        ax.contourf(xx, yy, z, levels=np.linspace(0, 1, 21), cmap=PROBA_CMAP, vmin=0, vmax=1)
        if z.min() < 0.5 < z.max():
            ax.contour(xx, yy, z, levels=[0.5], colors=TEXT, linewidths=1.2)
    else:
        z = model.predict(pts).reshape(xx.shape)
        idx = np.searchsorted(classes, z)
        cmap = ListedColormap([tint(CLASS_COLORS[k], 0.55) for k in range(2)] if n == 2
                              else [region_color(k) for k in range(n)])
        ax.pcolormesh(xx, yy, idx, cmap=cmap, vmin=-0.5, vmax=n - 0.5, shading="auto")
        # One indicator per class: a 0-2 border is one line, not two crossing levels.
        for k in range(n):
            mask = (idx == k).astype(float)
            if 0 < mask.mean() < 1:
                ax.contour(xx, yy, mask, levels=[0.5], colors=TEXT, linewidths=0.8)
    if show_points:
        _scatter(ax, X, y, n)
        if X_test is not None:
            _scatter(ax, X_test, y_test, n, hollow=True)
    if scores:
        # The key is the accuracy box itself: a filled dot by train, a hollow one by test,
        # so the figure says which points are which (notation.md, "Машинное обучение").
        # A Legend added as an artist, not ax.legend(): a script's own legend must not erase it.
        def dot(hollow):
            return Line2D([], [], ls="none", marker="o", ms=5, mew=0.9, mec=TEXT,
                          mfc="white" if hollow else TEXT)
        handles = [dot(False)]
        labels = [f"train {num((model.predict(X) == y).mean(), 2)}"]
        if X_test is not None:
            handles.append(dot(True))
            labels.append(f"test {num((model.predict(X_test) == y_test).mean(), 2)}")
        key = Legend(ax, handles, labels, loc="lower right", fontsize=8, labelcolor=TEXT,
                     handlelength=0.8, handletextpad=0.4, borderpad=0.3, labelspacing=0.2,
                     borderaxespad=0.3, frameon=True, fancybox=True, framealpha=0.85,
                     facecolor="white", edgecolor="none")
        key.set_zorder(5)
        ax.add_artist(key)
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    ax.set_xticks([])
    ax.set_yticks([])
    # A region map is a framed tile: the theme hides top and right spines for charts.
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(GRIDC)
    if title:
        ax.set_title(title)
    return ax


def model_grid(make, rows, cols, data, *, row_label=None, col_label=None, size=None):
    """Small multiples: make(r, c) returns an unfitted model for cell (r, c).

    rows and cols are value lists; data is a dataset name. The same train/test
    split is used in every cell, so only the model changes across the grid.
    """
    X, y = dataset(data)
    Xtr, Xte, ytr, yte = split(X, y)
    fig, axes = subplots(len(rows), len(cols), size=size)
    axes = np.asarray(axes, dtype=object).reshape(len(rows), len(cols))
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            m = make(r, c).fit(Xtr, ytr)
            plot_decision(axes[i, j], m, Xtr, ytr, X_test=Xte, y_test=yte)
            if i == 0 and col_label:
                axes[i, j].set_title(col_label(c))
            if j == 0 and row_label:
                axes[i, j].set_ylabel(row_label(r))
    fig.tight_layout()
    return fig, axes


def loss_contourf(ax, X, Y, Z, *, n=12, lines=True):
    """Level bands of a loss surface on ddlc_seq: lighter is lower, darker higher.

    Levels are quantiles of Z, so a surface with a huge range still shows n
    distinct bands; a BoundaryNorm maps each band to its own colour, where an
    ordinary norm over levels like [0, 1, ..., 1e9] would paint almost all one.
    """
    from matplotlib.colors import BoundaryNorm
    levels = np.unique(np.quantile(Z, np.linspace(0, 1, n + 1)))
    norm = BoundaryNorm(levels, plt.get_cmap("ddlc_seq").N)
    cs = ax.contourf(X, Y, Z, levels=levels, cmap="ddlc_seq", norm=norm)
    if lines:
        ax.contour(X, Y, Z, levels=levels, colors=[TEXT_2], linewidths=0.4, alpha=0.6)
    return cs


def complexity_curve(ax, values, train, test, *, xlabel, ylabel="accuracy", val=None,
                     better="max", log=False):
    """Train and test score against a complexity parameter.

    The chosen value is marked only from a validation curve (val), the way a
    model is actually tuned: marking the test optimum would choose by test.
    better is "max" for a score and "min" for an error. Returns the index of
    the chosen value, or None without val.
    """
    ax.plot(values, train, color=TRAIN_C, marker="o", ms=4, label="train")
    ax.plot(values, test, color=TEST_C, marker="o", ms=4, label="test")
    b = None
    if val is not None:
        ax.plot(values, val, color=TEXT_2, marker="s", ms=3, ls=":", label="валидация")
        b = int(np.argmax(val)) if better == "max" else int(np.argmin(val))
        ax.axvline(values[b], color=TEXT_2, lw=1, ls="--")
    if log:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y")
    ax.legend()
    return b


def attachments(topic):
    """Attachments folder of a course topic by its number: attachments(2) or "02"."""
    prefix = f"{int(topic):02d}. "
    found = [p for p in (COURSE / "content").iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if len(found) != 1:
        raise FileNotFoundError(f"topic {topic}: expected one content/{prefix}* folder, got {found}")
    return found[0] / "00. Вложения"


def save(fig, path, dpi=150):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", transparent=False)
    plt.close(fig)
    return path


def gif(draw, n_frames, path, *, size=(5, 4), fps=4, dpi=100, hold_last=4):
    """Animated GIF: draw(ax, i) paints frame i on a fresh axes. Loops forever."""
    import imageio.v3 as iio
    frames = []
    for i in range(n_frames):
        fig, ax = plt.subplots(figsize=size, dpi=dpi)
        draw(ax, i)
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        plt.close(fig)
    h = min(f.shape[0] for f in frames)
    w = min(f.shape[1] for f in frames)
    frames = [f[:h, :w] for f in frames]
    durations = [1000 / fps] * n_frames
    durations[-1] += hold_last * 1000 / fps
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(path, np.stack(frames), duration=durations, loop=0)
    return path
