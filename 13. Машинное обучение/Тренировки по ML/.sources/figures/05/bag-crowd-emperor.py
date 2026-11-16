"""Wisdom of the crowd against the emperor: averaging kills zero-mean noise but not a shared bias."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import figkit as fk  # noqa: E402

N = 500
TRUTH = 100.0
NOISE = 15.0
FALSE_CENTER = 70.0  # what everyone "imagines" when nobody has seen the object

rng = np.random.default_rng(fk.SEED)
crowd = TRUTH + rng.normal(0, NOISE, N)
emperor = FALSE_CENTER + rng.normal(0, NOISE, N)
run = lambda a: np.cumsum(a) / np.arange(1, N + 1)  # noqa: E731

fig, (ax1, ax2) = fk.subplots(1, 2, size=(11.6, 3.8))
bins = np.linspace(20, 160, 36)
ax1.hist(crowd, bins=bins, histtype="step", color=fk.MODEL_C, lw=1.8, label="толпа: оценки вокруг истины")
ax1.hist(emperor, bins=bins, histtype="step", color=fk.MODEL2_C, lw=1.8, label="император: оценки вокруг образа")
ax1.axvline(TRUTH, color=fk.ACCENT, lw=1.4, ls="--", label="истинное значение")
ax1.set_xlabel("оценка")
ax1.set_ylabel("число оценщиков")
ax1.set_title(f"{N} независимых оценок")
ax1.set_ylim(0, 85)
ax1.legend(loc="upper left", fontsize=7)

ns = np.arange(1, N + 1)
ax2.plot(ns, run(crowd), color=fk.MODEL_C, lw=1.5, label="среднее толпы")
ax2.plot(ns, run(emperor), color=fk.MODEL2_C, lw=1.5, label="среднее по императору")
ax2.axhline(TRUTH, color=fk.ACCENT, lw=1.2, ls="--", label="истинное значение")
ax2.set_xscale("log")
ax2.set_xlabel("число оценщиков")
ax2.set_ylabel("среднее оценок")
ax2.set_title("среднее против числа оценщиков")
ax2.legend(loc="center right", fontsize=7)
fk.save(fig, fk.attachments(5) / "bag-crowd-emperor.png")

print("crowd mean", round(float(crowd.mean()), 2), "emperor mean", round(float(emperor.mean()), 2))
print("crowd running", [round(float(run(crowd)[k - 1]), 1) for k in (1, 10, 100, 500)])
print("emperor running", [round(float(run(emperor)[k - 1]), 1) for k in (1, 10, 100, 500)])
