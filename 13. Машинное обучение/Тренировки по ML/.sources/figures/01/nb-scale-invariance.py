"""Gaussian NB zones before and after stretching the first feature 50x, in display coordinates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sklearn.naive_bayes import GaussianNB  # noqa: E402

import figkit as fk  # noqa: E402

STRETCH = 50.0
X, y = fk.dataset("moons")
Xtr, Xte, ytr, yte = fk.split(X, y)
mu, sd = Xtr.mean(0), Xtr.std(0)
Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd
scale = np.array([STRETCH, 1.0])


class Wrapped:
    def __init__(self, model, to_raw):
        self.model, self.to_raw, self.classes_ = model, to_raw, model.classes_

    def predict(self, Z):
        return self.model.predict(self.to_raw(Z))

    def predict_proba(self, Z):
        return self.model.predict_proba(self.to_raw(Z))


m_base = GaussianNB().fit(Xtr, ytr)
m_str = GaussianNB().fit(Xtr * scale, ytr)
fig, axes = fk.subplots(1, 2, size=(8.4, 3.8))
fk.plot_decision(axes[0], Wrapped(m_base, lambda Z: Z * sd + mu), Ztr, ytr, X_test=Zte, y_test=yte,
                 title="Исходные шкалы")
fk.plot_decision(axes[1], Wrapped(m_str, lambda Z: (Z * sd + mu) * scale), Ztr, ytr, X_test=Zte,
                 y_test=yte, title=f"Первый признак ×{STRETCH:.0f}")
fig.tight_layout()
fk.save(fig, fk.attachments(1) / "nb-scale-invariance.png")
