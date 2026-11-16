"""Softmax with temperature on the lecturer's ten-class example: five cars and five mushrooms.

The logits are z = ln p, so that at T = 1 the softmax returns the shares the lecturer names for a photo of an Audi:
Lada about 10 %, BMW + Audi + Mercedes together 85 % with Audi at 45 %, the garbage truck 5 %, mushrooms near zero (L08 13:28).
The split of the other 40 % between BMW and Mercedes and the mushroom share are assumed here.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import figkit as fk  # noqa: E402,F401

NAMES = ["Lada", "BMW", "Audi", "Mercedes", "КАМАЗ", "опята", "подберёзовик", "мухомор", "лисичка", "шампиньон"]
P1 = np.array([0.10, 0.26, 0.45, 0.14, 0.05, 0.0005, 0.0005, 0.0005, 0.0005, 0.0005])
P1 = P1 / P1.sum()
Z = np.log(P1)
AUDI = 2
# One colour per class on every figure of the note; plum is kept for train curves and is not used here.
CLASS_COLOR = {"Audi": fk.P["bow"], "BMW": fk.P["rule"], "Lada": fk.P["monika-eye"], "КАМАЗ": fk.P["skirt"]}


def softmax(z, T=1.0):
    T = np.asarray(T, dtype=float)
    s = np.asarray(z, dtype=float) / (T[:, None] if T.ndim else T)
    s = s - s.max(-1, keepdims=True)
    e = np.exp(s)
    return e / e.sum(-1, keepdims=True)


def entropy(q):
    q = np.asarray(q)
    return -(q * np.log(np.where(q > 0, q, 1))).sum(-1)
