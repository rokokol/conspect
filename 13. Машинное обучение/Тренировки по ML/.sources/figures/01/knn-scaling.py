"""Effect of feature scale on kNN: baseline, first feature stretched 50x, after standardisation.

All panels are drawn in standardised display coordinates, so the same picture
frame shows what each fitted model does with the same points.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import figkit as fk  # noqa: E402

K = 15
STRETCH = 50.0

X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
mu, sd = Xtr.mean(0), Xtr.std(0)
Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd  # display coordinates
scale = np.array([STRETCH, 1.0])


class Wrapped:
    """A model fitted in raw coordinates, queried in display coordinates."""

    def __init__(self, model, to_raw):
        self.model, self.to_raw = model, to_raw
        self.classes_ = model.classes_

    def predict(self, Z):
        return self.model.predict(self.to_raw(Z))

    def predict_proba(self, Z):
        return self.model.predict_proba(self.to_raw(Z))


def raw_base(Z):
    return Z * sd + mu


def raw_stretched(Z):
    return (Z * sd + mu) * scale


m_base = KNeighborsClassifier(K).fit(Xtr, ytr)
m_str = KNeighborsClassifier(K).fit(Xtr * scale, ytr)
m_std = KNeighborsClassifier(K).fit(Ztr, ytr)

panels = [
    ("Исходные шкалы", Wrapped(m_base, raw_base), raw_base, m_base),
    (f"Первый признак ×{STRETCH:.0f}", Wrapped(m_str, raw_stretched), raw_stretched, m_str),
    ("После стандартизации", Wrapped(m_std, lambda Z: Z), lambda Z: Z, m_std),
]

q = np.array([[0.6, 0.0]])  # query point in display coordinates
fig, axes = fk.subplots(1, 3, size=(12.0, 3.8))
for ax, (title, wrapped, to_raw, model) in zip(axes, panels):
    fk.plot_decision(ax, wrapped, Ztr, ytr, X_test=Zte, y_test=yte, title=title)
    idx = model.kneighbors(to_raw(q), K, return_distance=False)[0]
    ax.scatter(*Ztr[idx].T, s=70, facecolors="none", edgecolors=fk.TEXT, linewidths=1.2, zorder=4)
    ax.scatter(*q.T, marker="*", s=170, color=fk.P["monika"], edgecolors=fk.TEXT,
               linewidths=0.8, zorder=5)
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "knn-scaling-effect.png")
