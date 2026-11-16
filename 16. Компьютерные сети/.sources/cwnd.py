"""Congestion window of TCP Tahoe and Reno under periodic loss, for f08 "Оптимизации TCP"."""
import matplotlib.pyplot as plt

from netfig import COURSE, P

OUT = COURSE / "content" / "08. Транспортный уровень" / "00. Вложения"
CAP = 40   # the window at which the path starts dropping, in segments
T = 60


def run(kind):
    cwnd, ssthresh = 1.0, 64.0
    xs, ys = [], []
    for t in range(T + 1):
        xs.append(t)
        ys.append(cwnd)
        if cwnd > CAP:  # loss detected in this RTT
            ssthresh = max(cwnd / 2, 2)
            cwnd = 1.0 if kind == "tahoe" else ssthresh
        elif cwnd < ssthresh:
            cwnd = min(cwnd * 2, ssthresh) if cwnd * 2 > ssthresh else cwnd * 2
        else:
            cwnd += 1
    return xs, ys


MUTED = P["jacket"]
TAHOE, RENO = P["bow"], P["rule"]
fig, ax = plt.subplots(figsize=(11, 5.2), dpi=130)
for kind, col, label in (("tahoe", TAHOE, "Tahoe: потеря → окно 1, slow start"), ("reno", RENO, "Reno: потеря → окно пополам")):
    xs, ys = run(kind)
    ax.plot(xs, ys, color=col, lw=2, label=label, marker="o", markersize=3)
ax.axhline(CAP, color=MUTED, lw=1.2, ls="--")
ax.text(T + 0.5, CAP + 1.2, "предел пути", color=MUTED, ha="right", va="bottom", fontsize=11)
ax.set_xlim(0, T + 1)
ax.set_ylim(0, 70)
ax.set_xlabel("время, в RTT", fontsize=12)
ax.set_ylabel("cwnd, сегментов", fontsize=12)
ax.set_title("Окно перегрузки при потерях", fontsize=15)
ax.grid(axis="y")
ax.legend(loc="upper right", fontsize=11, bbox_to_anchor=(1.0, 1.0))
fig.savefig(OUT / "Окно перегрузки Tahoe и Reno.png", bbox_inches="tight")
