"""The same cloud twice: perpendicular distances to the first-component line and vertical deviations to the least-squares line."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lafig  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from pca_data import cloud  # noqa: E402

x, c, lam, w = cloud()
n = len(x)
w1, w2 = w[:, 0], w[:, 1]

slope_pca = w1[1] / w1[0]
slope_ols = c[0, 1] / c[0, 0]                       # regression of x_2 on x_1 through the centre
assert not np.isclose(slope_pca, slope_ols)

perp_pca = x @ w2                                   # signed perpendicular distances to the PCA line
vert_ols = x[:, 1] - slope_ols * x[:, 0]            # vertical deviations from the OLS line
perp_ols = vert_ols / np.hypot(1, slope_ols)        # perpendicular distances to the OLS line
vert_pca = x[:, 1] - slope_pca * x[:, 0]            # vertical deviations from the PCA line

s_perp_pca, s_perp_ols = np.sum(perp_pca**2), np.sum(perp_ols**2)
s_vert_ols, s_vert_pca = np.sum(vert_ols**2), np.sum(vert_pca**2)
assert np.isclose(s_perp_pca, (n - 1) * lam[1])                       # = sum_{j>1} rho_j^2
assert s_perp_pca < s_perp_ols and s_vert_ols < s_vert_pca            # each line wins on its own criterion
# no other slope beats either line on its criterion
for m in np.linspace(slope_ols - 1.0, slope_pca + 1.0, 2001):
    assert np.sum((x[:, 1] - m * x[:, 0]) ** 2) >= s_vert_ols - 1e-9
    assert np.sum((x @ np.array([-m, 1.0])) ** 2) / (1 + m**2) >= s_perp_pca - 1e-9

xs = np.array([-6.0, 6.0])
fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.3), sharex=True, sharey=True)
panels = (
    (axes[0], "Перпендикуляры к прямой PCA", slope_pca, slope_ols,
     x - np.outer(perp_pca, w2), s_perp_pca),
    (axes[1], "Вертикальные отклонения к МНК", slope_ols, slope_pca,
     np.c_[x[:, 0], slope_ols * x[:, 0]], s_vert_ols),
)
for ax, title, m_act, m_other, foot, total in panels:
    for p, f in zip(x, foot):
        ax.plot([p[0], f[0]], [p[1], f[1]], color=lafig.IMAGE, lw=0.9, zorder=1)
    ax.scatter(x[:, 0], x[:, 1], s=14, color=lafig.VECTOR, alpha=0.85, linewidths=0, zorder=3)
    ax.plot(xs, m_act * xs, color=lafig.HIGHLIGHT, lw=2.0, zorder=4)
    ax.plot(xs, m_other * xs, color=lafig.MUTED, lw=1.5, ls="--", zorder=2)
    ax.text(0.03, 0.04, rf"$\sum d^2={total:.0f}$", transform=ax.transAxes, color=lafig.INK)
    ax.set_title(title, color=lafig.INK)
    ax.set_aspect("equal")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-4.6, 4.6)
    ax.set_xlabel(r"$x_1$", color=lafig.INK)
    ax.tick_params(colors=lafig.INK)
    for side in ax.spines.values():
        side.set_color(lafig.AUX)
axes[0].set_ylabel(r"$x_2$", color=lafig.INK)

# the segments drawn on the left panel are perpendicular to w^1, on the right they are vertical
for p, f in zip(x, panels[0][4]):
    assert abs(np.dot(p - f, w1)) < 1e-9
assert np.allclose(panels[1][4][:, 0], x[:, 0])

fig.legend(handles=[
    Line2D([0], [0], color=lafig.HIGHLIGHT, lw=2.0, label="прямая, минимизирующая показанные отрезки"),
    Line2D([0], [0], color=lafig.MUTED, lw=1.5, ls="--", label="вторая прямая, для сравнения"),
    Line2D([0], [0], color=lafig.IMAGE, lw=0.9, label="отклонение $d$ точки"),
], loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1))

lafig.save(fig, 12, "pca-vs-ols")
