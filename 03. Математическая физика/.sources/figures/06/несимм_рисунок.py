"""Drawing helpers shared by the несимм-* figures: the key of the polarisation line styles."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mffig  # noqa: E402,F401
from matplotlib.lines import Line2D  # noqa: E402

POL_STYLE = {"TE": "-", "TM": "--"}


def pol_handles():
    """Legend entries that say solid is TE and dashed is TM."""
    return [Line2D([], [], color=mffig.INK, ls=POL_STYLE[p], lw=1.6, label=p) for p in ("TE", "TM")]


def mode_handles(js):
    """Legend entries that say which colour is which mode number."""
    return [Line2D([], [], color=mffig.CYCLE[j % len(mffig.CYCLE)], lw=2, label=rf"$j={j}$") for j in js]
