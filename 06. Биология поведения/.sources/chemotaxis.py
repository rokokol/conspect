"""Toy model of three chemotaxis strategies in one radial gradient.

Only the turning rule differs between panels; speed, base run length,
turn-angle distribution, start points and random seed are shared.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "00. Вложения"
rng = np.random.default_rng(7)

L = 12.0  # length scale of C = exp(-r / L)
V = 1.0  # speed
TAU0 = 1.0  # mean run length without a gradient
ALPHA = 6.0  # run extension: exp(ALPHA * dlnC/dt) when dlnC/dt > 0
CAST = np.deg2rad(60)  # head-cast angle for the larva
P_RIGHT = 0.8  # probability the cast comparison picks the better side
DT = 0.05
T_END = 160.0
N = 40
START = np.array([28.0, 0.0])


def conc(p):
    return np.exp(-np.hypot(p[..., 0], p[..., 1]) / L)


def turn_angle(n):
    # Berg and Brown: short twiddles change course by 62 +- 26 degrees
    a = np.deg2rad(np.clip(rng.normal(62, 26, n), 0, 180))
    return a * rng.choice([-1, 1], n)


def simulate(strategy):
    steps = int(T_END / DT)
    pos = np.tile(START, (N, 1)) + rng.normal(0, 1.0, (N, 2))
    head = rng.uniform(0, 2 * np.pi, N)
    traj = np.empty((steps, N, 2))
    for k in range(steps):
        d = np.stack([np.cos(head), np.sin(head)], 1)
        r = np.hypot(pos[:, 0], pos[:, 1])
        dlnc = -(pos * d).sum(1) / np.maximum(r, 1e-9) * V / L
        rate = np.full(N, 1 / TAU0)
        if strategy != "random":
            rate *= np.exp(-ALPHA * np.maximum(dlnc, 0))
        turn = rng.random(N) < rate * DT
        if strategy == "larva":
            idx = np.flatnonzero(turn)
            for i in idx:
                left = pos[i] + np.array([np.cos(head[i] + CAST), np.sin(head[i] + CAST)])
                right = pos[i] + np.array([np.cos(head[i] - CAST), np.sin(head[i] - CAST)])
                better = 1 if conc(left) > conc(right) else -1
                side = better if rng.random() < P_RIGHT else -better
                head[i] += side * CAST
        else:
            head[turn] += turn_angle(turn.sum())
        pos = pos + V * DT * np.stack([np.cos(head), np.sin(head)], 1)
        traj[k] = pos
    return traj


names = [
    ("random", "Без смещения"),
    ("ecoli", "E. coli: клинокинезис"),
    ("larva", "Личинка: + пробы головой"),
]
trajs = {}
for key, _ in names:
    rng = np.random.default_rng(7)
    trajs[key] = simulate(key)

# Static summary: mean distance to the source over time
t = np.arange(trajs["random"].shape[0]) * DT
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=130)
colors = {"random": P["jacket"], "ecoli": P["rule"], "larva": P["bow"]}
for key, label in names:
    dist = np.hypot(trajs[key][..., 0], trajs[key][..., 1]).mean(1)
    ax.plot(t, dist, color=colors[key], label=label, lw=2)
ax.set_xlabel("время, средних пробегов")
ax.set_ylabel("среднее расстояние до источника")
ax.set_title("Кто быстрее находит источник")
ax.set_ylim(0, None)
ax.grid(True)
# The band between the E. coli curve and the larva curve is empty on the right.
ax.legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.36))
fig.tight_layout()
fig.savefig(OUT / "Стратегии хемотаксиса — расстояние до источника.png")
plt.close(fig)

# Animation
EXT = 34
g = np.linspace(-EXT, EXT, 200)
X, Y = np.meshgrid(g, g)
C = np.exp(-np.hypot(X, Y) / L)
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), dpi=72)
dots, trails = [], []
for ax, (key, label) in zip(axes, names):
    ax.imshow(C, extent=[-EXT, EXT, -EXT, EXT], origin="lower", cmap="ddlc_seq", alpha=0.45)
    ax.plot(0, 0, marker="*", color=P["paper"], ms=14, mec=P["ink"])
    ax.set_title(label, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-EXT, EXT)
    ax.set_ylim(-EXT, EXT)
    (trail,) = ax.plot([], [], color=colors[key], lw=1.2)
    dot = ax.scatter([], [], s=10, color=colors[key])
    trails.append(trail)
    dots.append(dot)
fig.tight_layout()

STRIDE = 20
frames = range(0, trajs["random"].shape[0], STRIDE)


def update(k):
    for (key, _), dot, trail in zip(names, dots, trails):
        dot.set_offsets(trajs[key][k])
        trail.set_data(trajs[key][: k + 1, 0, 0], trajs[key][: k + 1, 0, 1])
    return dots + trails


anim = FuncAnimation(fig, update, frames=frames, blit=True)
anim.save(OUT / "Стратегии хемотаксиса — три агента.gif", writer=PillowWriter(fps=15))
