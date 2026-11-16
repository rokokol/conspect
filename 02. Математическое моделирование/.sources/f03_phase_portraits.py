"""Phase portraits of the linear system x' = A x on the plane, one panel per case of the eigenvalue classification.

Every trajectory is integrated with solve_ivp from points on a circle, forwards and backwards in time.
Dashed lines are the eigendirections h of A (for real eigenvalues), arrows show the direction of motion.
The matrix of each panel is A = H J H^-1 with a non-orthogonal H, so the eigenlines are not the axes.

Run: python f03_phase_portraits.py  ->  ../00. Вложения/figures/f03 фазовые портреты линейных систем.png
"""
from pathlib import Path

import course  # noqa: F401  puts ddlc_figures on sys.path
import ddlc_theme  # noqa: E402

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

P = ddlc_theme.P
SOLUTION = P["bow"]
EIGEN = P["rule"]
MUTED = P["ash"]
INK = P["ink"]
OUT = course.COURSE / "00. Вложения" / "figures" / "f03 фазовые портреты линейных систем.png"

H = np.array([[1.0, 0.45], [0.55, 1.0]])
Hinv = np.linalg.inv(H)
LIM = 1.0


def real_pair(l1, l2):
    return H @ np.diag([l1, l2]) @ Hinv


def jordan(lam):
    # h2 = H[:, 1] is the eigenvector, h1 = H[:, 0] is the adjoined one: (A - lam) h1 = h2
    return H @ np.array([[lam, 0.0], [1.0, lam]]) @ Hinv


def complex_pair(alpha, beta):
    return H @ np.array([[alpha, beta], [-beta, alpha]]) @ Hinv


CASES = [
    ("устойчивый узел", r"$\lambda_2<\lambda_1<0$", real_pair(-1.0, -3.0), "eig", 1),
    ("неустойчивый узел", r"$0<\lambda_1<\lambda_2$", real_pair(1.0, 3.0), "eig", -1),
    ("дикритический узел", r"$\lambda_1=\lambda_2<0$, (1)", -1.5 * np.eye(2), "all", 1),
    ("вырожденный узел", r"$\lambda_1=\lambda_2<0$, (2)", jordan(-1.5), "jordan", 1),
    ("седло", r"$\lambda_2<0<\lambda_1$", real_pair(1.0, -2.0), "eig", 1),
    ("центр", r"$\alpha=0$", complex_pair(0.0, 2.0), None, 1),
    ("устойчивый фокус", r"$\alpha<0$", complex_pair(-0.4, 2.0), None, 1),
    ("неустойчивый фокус", r"$\alpha>0$", complex_pair(0.4, 2.0), None, 1),
]


def trajectory(A, x0, forward):
    def rhs(t, x):
        return A @ x

    def out(t, x):
        return np.hypot(*x) - 1.6 * LIM

    out.terminal = True
    span = (0, 12) if forward else (0, -12)
    sol = solve_ivp(rhs, span, x0, rtol=1e-9, atol=1e-12, events=out, dense_output=True)
    ts = np.linspace(0, sol.t[-1], 400)
    return sol.sol(ts)


def draw(ax, name, cond, A, eig_lines, sense):
    ax.set_aspect("equal")
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.axhline(0, color=MUTED, linewidth=0.6, zorder=0)
    ax.axvline(0, color=MUTED, linewidth=0.6, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{name}\n{cond}", fontsize=9)

    n = 12 if eig_lines is not None else 3
    radii = [0.35, 0.65, 0.95] if eig_lines is None else [0.9]
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False) + 0.2
    for r in radii:
        for a in angles:
            x0 = r * np.array([np.cos(a), np.sin(a)])
            if eig_lines is None and a != angles[0]:
                continue
            back = trajectory(A, x0, False)[:, ::-1]
            fwd = trajectory(A, x0, True)
            full = np.concatenate([back, fwd], axis=1)
            ax.plot(*full, color=SOLUTION, linewidth=1.3, zorder=3)
            for part, offset in ((back, 0), (fwd, back.shape[1])):
                k = int(np.argmin(np.abs(np.hypot(*part) - 0.55))) + offset
                k = min(max(k, 1), full.shape[1] - 3)
                ax.annotate("", xy=full[:, k + 2], xytext=full[:, k], zorder=4,
                            arrowprops=dict(arrowstyle="-|>", color=SOLUTION, lw=1.3, mutation_scale=10))

    # eigenvectors come from H itself: np.linalg.eig gives a jordan block a spurious imaginary part
    if eig_lines == "eig":
        dirs = [(H[:, 0], r"$h^1$"), (H[:, 1], r"$h^2$")]
    elif eig_lines == "jordan":
        dirs = [(H[:, 1], r"$h^2$")]
    else:
        dirs = []
    for h, label in dirs:
        h = h / np.hypot(*h)
        ax.plot([-1.6 * h[0], 1.6 * h[0]], [-1.6 * h[1], 1.6 * h[1]], "--", color=EIGEN,
                linewidth=1.6, zorder=2)
        ax.text(0.93 * h[0] + 0.06, 0.93 * h[1] - 0.1, label, color=EIGEN, fontsize=10, zorder=6)
    ax.plot(0, 0, "o", color=INK, markersize=4, zorder=5)


def main():
    fig, axes = plt.subplots(2, 4, figsize=(12, 6.6))
    for ax, (name, cond, A, eig_lines, sense) in zip(axes.ravel(), CASES):
        draw(ax, name, cond, A, eig_lines, sense)
    fig.legend(handles=[
        Line2D([0], [0], color=SOLUTION, lw=1.5, label="траектория, стрелка по ходу времени"),
        Line2D([0], [0], color=EIGEN, lw=1.5, ls="--", label="собственная прямая $h$"),
    ], loc="lower center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=2.5)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(OUT)


if __name__ == "__main__":
    main()
