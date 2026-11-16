"""Figures for the note "Средняя скорость" (lessons 16, 17, 20, 22) and one figure for "Графики движения".

Run:
  nix shell --impure --expr 'with import <nixpkgs> {}; [(python3.withPackages(ps: [ps.matplotlib ps.numpy]))]' -c python3 average_speed.py
The PNG files (prefix avg-speed-) go to content/03. Механическое движение/00. Вложения/.
"""


import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

from course import COURSE
OUT = COURSE / "content" / "03. Механическое движение" / "00. Вложения"

from motion_graphs import C1, C2, C3, GREY, INK, NOTE  # the roles of the motion figures live in one place
from theme import saver

SEG = [C1, C2]


_save = saver(OUT)


def save(fig, name):
    _save(fig, name, bbox_inches="tight", pad_inches=0.15)


def fmt(x, math=False):
    """Decimal comma, no trailing zeros; math=True gives the mathtext form."""
    text = f"{x:.1f}".rstrip("0").rstrip(".") if abs(x - round(x)) > 1e-9 else f"{x:.0f}"
    return text.replace(".", "{,}" if math else ",")


def tick(x):
    k = round(x * 3)
    if abs(x * 3 - k) < 1e-9 and k % 3:
        return f"{k}/3"
    return fmt(x)


def two_panel(name, segs, tunit, sunit, vunit, mark=None, approx=False, ymax_s=None):
    """s(t) with the chord and v(t) with the equal-area rectangle.

    segs: list of (speed, duration). mark: ("h", s) or ("v", t) dotted helper on s(t).
    """
    edges = [0.0]
    path = [0.0]
    for v, dt in segs:
        edges.append(edges[-1] + dt)
        path.append(path[-1] + v * dt)
    T, S = edges[-1], path[-1]
    vcp = S / T
    sign = r"\approx" if approx else "="
    vcp_label = rf"$v_{{\mathrm{{ср}}}}{sign}{fmt(round(vcp, 1) if approx else vcp, math=True)}$ {vunit}"

    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"wspace": 0.28})

    # s(t)
    for i, (v, dt) in enumerate(segs):
        a.plot(edges[i : i + 2], path[i : i + 2], color=SEG[i % 2], lw=2.4, solid_capstyle="round")
        mid = edges[i] + 0.65 * (edges[i + 1] - edges[i])
        smid = path[i] + 0.65 * (path[i + 1] - path[i])
        if dt / T < 0.3:
            continue
        if v < vcp:
            a.annotate(f"{fmt(v)} {vunit}", (mid, smid), xytext=(8, -14), textcoords="offset points",
                       ha="left", color=SEG[i % 2], fontsize=10)
        else:
            a.annotate(f"{fmt(v)} {vunit}", (mid, smid), xytext=(-4, 8), textcoords="offset points",
                       ha="right", color=SEG[i % 2], fontsize=10)
    a.plot(edges, path, "o", color=INK, ms=4, zorder=5)
    a.plot([0, T], [0, S], ls="--", lw=1.6, color=C3)
    a.text(0.98, 0.1, vcp_label, transform=a.transAxes, ha="right", color=C3)
    if mark:
        kind, val = mark
        if kind == "h":
            a.plot([0, T], [val, val], ls=":", lw=1, color=GREY)
            a.text(T * 0.02, val, fmt(val), va="bottom", color=NOTE, fontsize=9)
        else:
            a.plot([val, val], [0, S], ls=":", lw=1, color=GREY)
    a.set_xlim(0, T * 1.05)
    a.set_ylim(0, (ymax_s or S) * 1.08)
    a.set_xlabel(f"$t$, {tunit}")
    a.set_ylabel(f"$s$, {sunit}")
    a.set_title("График пути")
    a.set_xticks(edges)
    a.set_xticklabels([tick(e) for e in edges])
    a.grid(alpha=0.25)

    # v(t)
    tt = np.linspace(0, T, 4000)
    vv = np.zeros_like(tt)
    for i, (v, dt) in enumerate(segs):
        m = (tt >= edges[i]) & (tt <= edges[i + 1])
        vv[m] = v
        b.fill_between(tt[m], 0, v, color=SEG[i % 2], alpha=0.16, lw=0)
        b.plot([edges[i], edges[i + 1]], [v, v], color=SEG[i % 2], lw=2.4, solid_capstyle="round")
    for e in edges[1:-1]:
        b.plot([e, e], [0, max(segs[0][0], segs[1][0])], color=GREY, lw=0.6, ls=":")
    b.plot([0, T], [vcp, vcp], ls="--", lw=1.6, color=C3)
    plt.rcParams["hatch.linewidth"] = 0.9
    b.fill_between(tt, vcp, vv, where=vv > vcp, facecolor="none", edgecolor=C2, hatch="///", lw=0)
    b.fill_between(tt, vv, vcp, where=vv < vcp, facecolor="none", edgecolor=C1, hatch="\\\\\\", lw=0)
    vmax = max(v for v, _ in segs)
    b.set_xlim(0, T * 1.05)
    b.set_ylim(0, vmax * 1.32)
    b.set_xlabel(f"$t$, {tunit}")
    b.set_ylabel(f"$v$, {vunit}")
    b.set_title("График скорости")
    b.set_xticks(edges)
    b.set_xticklabels([tick(e) for e in edges])
    low = next(i for i, (v, _) in enumerate(segs) if v < vcp)
    if low == 0:
        b.annotate(vcp_label, (0.02 * T, vcp), xytext=(0, 6), textcoords="offset points", ha="left", color=C3)
    else:
        b.annotate(vcp_label, (T, vcp), xytext=(0, 6), textcoords="offset points", ha="right", color=C3)
    b.grid(alpha=0.25)
    b.legend(
        handles=[
            Patch(facecolor="none", edgecolor=C2, hatch="///", label="выше $v_{\\mathrm{ср}}$"),
            Patch(facecolor="none", edgecolor=C1, hatch="\\\\\\", label="ниже $v_{\\mathrm{ср}}$"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        frameon=False,
    )
    save(fig, name)


def odessa_scheme():
    fig, ax = plt.subplots(figsize=(10, 3.3))
    ax.set_xlim(-30, 530)
    ax.set_ylim(-3.2, 2.6)
    ax.axis("off")
    ax.plot([0, 500], [0, 0], color=INK, lw=2.2)
    for x, lab in [(0, "О"), (300, "У"), (500, "К")]:
        ax.plot([x, x], [-0.18, 0.18], color=INK, lw=2)
        ax.text(x, 0.35, lab, ha="center", fontsize=14, fontweight="bold")
    ax.text(0, -0.65, "Одесса", ha="center", fontsize=9, color=NOTE)
    ax.text(300, -0.65, "Умань", ha="center", fontsize=9, color=NOTE)
    ax.text(500, -0.65, "Киев", ha="center", fontsize=9, color=NOTE)

    def brace(x0, x1, y, text, color):
        ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=1.4))
        ax.text((x0 + x1) / 2, y + 0.22, text, ha="center", color=color, fontsize=11)

    brace(0, 300, 1.15, r"$s_1=300$ км, $t_1=3$ ч" + "\n" + r"$v_{\mathrm{ср}}=100$ км/ч", C1)
    brace(300, 500, 1.15, r"$s_2=200$ км, $t_2=4$ ч" + "\n" + r"$v_{\mathrm{ср}}=50$ км/ч", C2)
    ax.annotate("", (0, -1.5), (500, -1.5), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.6))
    ax.text(250, -2.15, r"$s=500$ км, $t=7$ ч, $v_{\mathrm{ср}}=\frac{500}{7}\approx 71$ км/ч",
            ha="center", color=C3, fontsize=12)
    save(fig, "avg-speed-odessa-kiev-scheme.png")


def path_time_graphs():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw={"wspace": 0.3})
    a.plot([0, 500], [0, 2500], color=C1, lw=2.4)
    a.plot([0, 400, 400], [2000, 2000, 0], ls="--", color=GREY, lw=1)
    a.plot(400, 2000, "o", color=C2, ms=6)
    a.annotate("$t=400$ с", (400, 0), xytext=(4, 14), textcoords="offset points", color=C2, ha="left")
    a.annotate("$s=2000$ м", (0, 2000), xytext=(6, 5), textcoords="offset points", color=C2)
    a.set_xlim(0, 520)
    a.set_ylim(0, 2600)
    a.set_xlabel("$t$, с")
    a.set_ylabel("$s$, м")
    a.set_title("Время по пути: $t=s/v$")
    a.text(60, 1000, "$v=5$ м/с", color=C1, rotation=0, ha="left", fontsize=10)
    a.grid(alpha=0.25)

    b.plot([0, 4.5], [0, 5400], color=C1, lw=2.4)
    b.plot([3.5, 3.5, 0], [0, 4200, 4200], ls="--", color=GREY, lw=1)
    b.plot(3.5, 4200, "o", color=C2, ms=6)
    b.annotate("$t=3{,}5$ ч", (3.5, 0), xytext=(-6, 14), textcoords="offset points", color=C2, ha="right")
    b.annotate("$s=4200$ км", (0, 4200), xytext=(6, 5), textcoords="offset points", color=C2)
    b.set_xlim(0, 4.7)
    b.set_ylim(0, 5600)
    b.set_xlabel("$t$, ч")
    b.set_ylabel("$s$, км")
    b.set_title("Путь по времени: $s=vt$")
    b.text(0.25, 2200, "$v=1200$ км/ч", color=C1, ha="left", fontsize=10)
    b.grid(alpha=0.25)
    save(fig, "avg-speed-path-time-graphs.png")


def mean_vs_v2():
    v1 = 40.0
    v2 = np.linspace(1, 130, 400)
    harm = 2 * v1 * v2 / (v1 + v2)
    arith = (v1 + v2) / 2
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(v2, arith, color=C2, lw=2.2, label="равные времена: $(v_1+v_2)/2$")
    ax.plot(v2, harm, color=C1, lw=2.2, label="равные пути: $2v_1v_2/(v_1+v_2)$")
    ax.axhline(2 * v1, color=GREY, ls=":", lw=1)
    ax.text(129, 2 * v1 + 2, "$2v_1=80$", ha="right", va="bottom", color=NOTE, fontsize=9)
    ax.plot([60, 60], [0, 50], color=GREY, lw=0.8, ls="--")
    ax.plot([60], [48], "o", color=C1, ms=6)
    ax.plot([60], [50], "o", color=C2, ms=6)
    ax.annotate("48", (60, 48), xytext=(8, -14), textcoords="offset points", color=C1)
    ax.annotate("50", (60, 50), xytext=(-22, 8), textcoords="offset points", color=C2)
    ax.set_xlim(0, 130)
    ax.set_ylim(0, 92)
    ax.set_xlabel("$v_2$, км/ч ($v_1=40$ км/ч)")
    ax.set_ylabel("$v_{\\mathrm{ср}}$, км/ч")
    ax.set_title("Два способа усреднить")
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    save(fig, "avg-speed-mean-vs-v2.png")


def boat_scheme():
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.set_xlim(-1, 13)
    ax.set_ylim(0.1, 5.6)
    ax.axis("off")
    xs = np.linspace(0, 12, 200)
    for y in (0.6, 4.0):
        ax.plot(xs, y + 0.1 * np.sin(xs * 2.2), color=C1, lw=1.6)
    ax.add_patch(Rectangle((0, 0.6), 12, 3.4, facecolor=C1, alpha=0.07, lw=0))
    ax.add_patch(FancyArrowPatch((0.2, 4.55), (2.6, 4.55), arrowstyle="-|>", mutation_scale=16, color=C1, lw=1.8))
    ax.text(2.9, 4.5, "течение $v_{\\mathrm{р}}$", color=C1, va="center")
    for x in (1.0, 11.0):
        ax.plot([x, x], [0.35, 4.25], color=INK, lw=1.6)
    ax.annotate("", (1.0, 5.0), (11.0, 5.0), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(6.0, 5.12, "$s=100$ км", ha="center", va="bottom")
    ax.add_patch(FancyArrowPatch((2.2, 3.0), (6.2, 3.0), arrowstyle="-|>", mutation_scale=18, color=C2, lw=2.4))
    ax.text(6.6, 3.0, "по течению: $v_{\\mathrm{к}}+v_{\\mathrm{р}}$, $t_{\\mathrm{по}}=4$ ч", color=C2, va="center")
    ax.add_patch(FancyArrowPatch((10.0, 1.7), (7.0, 1.7), arrowstyle="-|>", mutation_scale=18, color=C3, lw=2.4))
    ax.text(6.6, 1.05, "против течения: $v_{\\mathrm{к}}-v_{\\mathrm{р}}$, $t_{\\mathrm{пр}}=10$ ч", color=C3, va="center", ha="right")
    save(fig, "avg-speed-boat-scheme.png")


def traveler_horseman():
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    t = np.linspace(0, 3.2, 200)
    ax.plot(t, 5 * t, color=C1, lw=2.4, label="путник, $5$ км/ч")
    th = np.linspace(1.5, 3.2, 100)
    ax.plot([0, 1.5], [0, 0], color=C2, lw=2.4)
    ax.plot(th, 30 * (th - 1.5), color=C2, lw=2.4, label="всадник, $30$ км/ч")
    ax.plot([1.8], [9], "o", color=INK, ms=6, zorder=5)
    ax.plot([1.8, 1.8], [0, 9], ls="--", color=GREY, lw=1)
    ax.plot([0, 1.8], [9, 9], ls=":", color=GREY, lw=1)
    ax.annotate("", (1.5, 1.4), (1.8, 1.4), arrowprops=dict(arrowstyle="<->", color=C3, lw=1.5))
    ax.text(1.86, 0.5, "$t^*=0{,}3$ ч", ha="left", color=C3)
    ax.annotate("", (0, 1.4), (1.5, 1.4), arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.2))
    ax.text(1.05, 1.9, "$\\Delta t=1{,}5$ ч", ha="center", color=NOTE)
    ax.text(1.85, 9.6, "встреча: $9$ км", ha="left", color=INK, fontsize=10)
    ax.set_xlim(0, 3.2)
    ax.set_ylim(0, 30)
    ax.set_xlabel("$t$, ч")
    ax.set_ylabel("$l$, км")
    ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
    ax.set_xticklabels(["0", "0,5", "1", "1,5", "2", "2,5", "3"])
    ax.set_title("Всадник догоняет путника")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", frameon=False)
    save(fig, "avg-speed-traveler-horseman-graph.png")


if __name__ == "__main__":
    odessa_scheme()
    two_panel("avg-speed-odessa-kiev-graphs.png", [(100, 3), (50, 4)], "ч", "км", "км/ч", approx=True)
    path_time_graphs()
    two_panel("avg-speed-task-3-7-graphs.png", [(100, 0.5), (75, 2)], "ч", "км", "км/ч")
    two_panel("avg-speed-task-3-9-graphs.png", [(45, 1 / 3), (42, 2 / 3)], "ч", "км", "км/ч")
    two_panel("avg-speed-equal-distance-graphs.png", [(40, 1.5), (60, 1.0)], "ч", "км", "км/ч", mark=("h", 60))
    two_panel("avg-speed-equal-time-graphs.png", [(60, 1), (40, 1)], "ч", "км", "км/ч", mark=("v", 1))
    two_panel("avg-speed-cyclist-graphs.png", [(12, 2), (6, 4)], "ч", "км", "км/ч", mark=("h", 24))
    two_panel("avg-speed-pedestrian-graphs.png", [(3, 2), (6, 1)], "ч", "км", "км/ч", mark=("h", 6))
    mean_vs_v2()
    boat_scheme()
    traveler_horseman()
