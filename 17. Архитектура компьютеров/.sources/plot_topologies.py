#!/usr/bin/env python3
"""Redraw of the 7 slide topologies (pp. 212-216) plus torus (lecturer's live
demo, not on a separate slide) and complete binary tree (table-only row, p.217)
for f09 "Топологии сетей межсоединений".
"""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "09. Сети межсоединений" / "00. Вложения"

NODE = 0.22
FACE = P["dot"]
EDGE = P["plum"]
LINE = dict(color=P["ink"], linewidth=1.3, zorder=1)
WRAP = dict(color=P["ink"], linewidth=1.1, linestyle=(0, (4, 3)), zorder=1)


def node(ax, x, y, shape="square", s=NODE):
    if shape == "square":
        ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, facecolor=FACE, edgecolor=EDGE, linewidth=1.3, zorder=2))
    else:
        ax.add_patch(Circle((x, y), s / 2, facecolor=P["paper"], edgecolor=EDGE, linewidth=1.3, zorder=2))


def edge(ax, p, q, style=LINE):
    ax.plot([p[0], q[0]], [p[1], q[1]], **style)


def new_ax(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / name, dpi=170, bbox_inches="tight")
    plt.close(fig)


# Полносвязная топология (completely-connected), N = 5, как на слайде 212
fig, ax = new_ax((3.4, 3.4))
n = 5
pts = [(math.cos(math.pi / 2 + 2 * math.pi * i / n), math.sin(math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
for i in range(n):
    for j in range(i + 1, n):
        edge(ax, pts[i], pts[j])
for p in pts:
    node(ax, *p)
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
save(fig, "топология-полный-граф.png")

# Линейка (linear array), N = 5
fig, ax = new_ax((4.2, 1.1))
n = 5
pts = [(i, 0) for i in range(n)]
for i in range(n - 1):
    edge(ax, pts[i], pts[i + 1])
for p in pts:
    node(ax, *p)
ax.set_xlim(-0.6, n - 0.4)
ax.set_ylim(-0.6, 0.6)
save(fig, "топология-линейка.png")

# Кольцо (ring), N = 5 — линейка с замкнутыми концами
fig, ax = new_ax((3.0, 3.0))
n = 5
pts = [(math.cos(math.pi / 2 + 2 * math.pi * i / n), math.sin(math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
for i in range(n):
    edge(ax, pts[i], pts[(i + 1) % n])
for p in pts:
    node(ax, *p)
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.35, 1.35)
save(fig, "топология-кольцо.png")

# Звезда (star), 5 листьев + управляющий процессор (коммутатор) в центре
fig, ax = new_ax((3.2, 3.2))
n = 5
hub = (0, 0)
leaves = [(1.05 * math.cos(math.pi / 2 + 2 * math.pi * i / n), 1.05 * math.sin(math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
for p in leaves:
    edge(ax, hub, p)
for p in leaves:
    node(ax, *p)
node(ax, *hub, shape="circle")
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
save(fig, "топология-звезда.png")

# Решётка (2D mesh), N = 16 = 4x4, без свёртывания краёв
fig, ax = new_ax((3.6, 3.6))
k = 4
pts = {(i, j): (i, j) for i in range(k) for j in range(k)}
for i in range(k):
    for j in range(k):
        if i + 1 < k:
            edge(ax, pts[(i, j)], pts[(i + 1, j)])
        if j + 1 < k:
            edge(ax, pts[(i, j)], pts[(i, j + 1)])
for p in pts.values():
    node(ax, *p)
ax.set_xlim(-0.6, k - 0.4)
ax.set_ylim(-0.6, k - 0.4)
save(fig, "топология-решётка.png")

# Тор (torus), N = 16 = 4x4 решётка со свёрнутыми краями. Обёртка показана
# короткими пунктирными "усами" у крайних узлов: сама дуга не рисуется, чтобы
# не перегружать решётку пересекающимися линиями
fig, ax = new_ax((4.2, 4.2))
k = 4
pts = {(i, j): (i, j) for i in range(k) for j in range(k)}
for i in range(k):
    for j in range(k):
        if i + 1 < k:
            edge(ax, pts[(i, j)], pts[(i + 1, j)])
        if j + 1 < k:
            edge(ax, pts[(i, j)], pts[(i, j + 1)])
stub = 0.34
for j in range(k):
    edge(ax, (0, j), (-stub, j), style=WRAP)
    edge(ax, (k - 1, j), (k - 1 + stub, j), style=WRAP)
for i in range(k):
    edge(ax, (i, 0), (i, -stub), style=WRAP)
    edge(ax, (i, k - 1), (i, k - 1 + stub), style=WRAP)
for p in pts.values():
    node(ax, *p)
ax.set_xlim(-stub - 0.4, k - 1 + stub + 0.4)
ax.set_ylim(-stub - 0.4, k - 1 + stub + 0.4)
save(fig, "топология-тор.png")

# Гиперкуб (hypercube), N = 16 = 2^4 — два соединённых 3-куба, как на слайде 216
fig, ax = new_ax((6.4, 3.6))


def cube3(ax, ox, oy, s):
    # 8 corners of a 3-cube drawn in 2D with an oblique (cabinet) projection
    shift = s * 0.42
    base = {
        "000": (ox, oy),
        "100": (ox + s, oy),
        "010": (ox, oy + s),
        "110": (ox + s, oy + s),
    }
    top = {k[:-1] + "1": (v[0] + shift, v[1] + shift) for k, v in base.items()}
    pts = {**base, **top}
    square_edges = [("000", "100"), ("100", "110"), ("110", "010"), ("010", "000")]
    for a, b in square_edges:
        edge(ax, pts[a], pts[b])
        edge(ax, pts[a[:-1] + "1"], pts[b[:-1] + "1"])
    for k in base:
        edge(ax, pts[k], pts[k[:-1] + "1"])
    for p in pts.values():
        node(ax, *p)
    return pts


left = cube3(ax, 0, 0, 1.6)
right = cube3(ax, 3.6, 0, 1.6)
for k in left:
    edge(ax, left[k], right[k], style=WRAP)
ax.set_xlim(-0.5, 6.6)
ax.set_ylim(-0.5, 3.0)
save(fig, "топология-гиперкуб.png")

# Полное двоичное дерево (complete binary tree), 7 узлов (глубина 2)
fig, ax = new_ax((4.2, 2.6))
levels = [[(0, 2)], [(-1.2, 1), (1.2, 1)], [(-1.8, 0), (-0.6, 0), (0.6, 0), (1.8, 0)]]
for i in range(len(levels) - 1):
    for pi, parent in enumerate(levels[i]):
        for ci in (2 * pi, 2 * pi + 1):
            edge(ax, parent, levels[i + 1][ci])
for lvl in levels:
    for p in lvl:
        node(ax, *p, s=0.24)
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-0.5, 2.5)
save(fig, "топология-полное-двоичное-дерево.png")
