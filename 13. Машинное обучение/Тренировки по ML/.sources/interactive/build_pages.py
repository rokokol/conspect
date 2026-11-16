"""Build self-contained interactive pages.

Each pages/<name>.html is a template with four markers, each exactly once:
  /*COMMON_CSS*/  pages/_common.css: theme tokens and layout
  /*COMMON_JS*/   sandbox_kit's theme.js (css(name) colours), then pages/_common.js: lookup, plot frame, axes
  /*MLCORE*/      mlcore.js with its `export` keywords removed
  /*DATA*/        `const DATA = {...}` with the figkit data sets
The result works offline from a file link: no CDN, no fetch.

Usage: python build_pages.py <name> <output.html>
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figures"))
sys.path.insert(0, str(HERE.parents[4] / "01. Data" / "04. Scripts"))
import figkit as fk  # noqa: E402
from sandbox_kit import page as kit  # noqa: E402

SETS = ["moons", "circles", "xor", "linear", "blobs3", "reg1d"]


def build(name: str, out: Path) -> Path:
    core = kit.strip_module((HERE / "mlcore.js").read_text(encoding="utf-8"))
    data = {}
    for s in SETS:
        X, y = fk.dataset(s)
        Xtr, Xte, ytr, yte = fk.split(X, y)
        data[s] = {"Xtr": Xtr.round(4).tolist(), "ytr": ytr.tolist(),
                   "Xte": Xte.round(4).tolist(), "yte": yte.tolist()}
    # The ten logits of the note's Audi example come from the figures' own module, not a copy on the page.
    sys.path.insert(0, str(HERE.parent / "figures" / "08"))
    import softmax_common as sc  # noqa: E402
    data["audi"] = {"names": sc.NAMES, "z": sc.Z.tolist(), "audi": sc.AUDI}
    parts = {
        "/*COMMON_CSS*/": kit.theme_css(),
        "/*COMMON_JS*/": kit.theme_js() + (HERE / "pages" / "_common.js").read_text(encoding="utf-8"),
        "/*MLCORE*/": core,
        "/*DATA*/": "const DATA = " + json.dumps(data) + ";",
    }
    return kit.build_page(name, HERE / "pages" / f"{name}.html", parts, out)


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
