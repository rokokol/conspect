#!/usr/bin/env python3
"""Generate figures for f08 note "Законы Амдала и Густафсона-Барсиса"
and print a numeric example table used in the note text.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "08. Параллельные вычислительные системы" / "00. Вложения"

# Figure 1: illustrative division of execution time (redraw of slides 204-205)
f_illust = 0.3
n_illust = 4

fig, axes = plt.subplots(2, 1, figsize=(6.4, 3.6), sharex=False)

seq_color = P["bow"]  # sequential part
par_color = P["rule"]  # parallel part
# The "n процессоров" bar is the short one in both panels, so its row has room.
LEGEND = dict(loc="lower right", fontsize=7, frameon=True, framealpha=0.9,
              facecolor=P["paper"], edgecolor=P["ash"])
CURVE_LEGEND = dict(fontsize=8, frameon=True, framealpha=1.0,
                    facecolor=P["paper"], edgecolor=P["ash"])

# Amdahl
ax = axes[0]
ts = 1.0
seq = f_illust * ts
par_1 = (1 - f_illust) * ts
par_n = (1 - f_illust) * ts / n_illust

ax.barh(["n процессоров", "1 процессор"], [seq, seq], color=seq_color, label="последовательная часть")
ax.barh(["n процессоров", "1 процессор"], [par_n, par_1], left=[seq, seq], color=par_color, label="распараллеливаемая часть")
ax.set_xlim(0, 1.05)
ax.set_title("Закон Амдала: доля от $T_s$ фиксирована", fontsize=10)
ax.set_xlabel("время")
ax.legend(**LEGEND)

# Gustafson-Barsis
ax = axes[1]
tp = 1.0
seq_g = f_illust * tp
par_g_n = (1 - f_illust) * tp
par_g_1 = (1 - f_illust) * tp * n_illust  # serial replay of the same work n times

ax.barh(["n процессоров", "1 процессор"], [seq_g, seq_g], color=seq_color, label="последовательная часть")
ax.barh(["n процессоров", "1 процессор"], [par_g_n, par_g_1], left=[seq_g, seq_g], color=par_color, label="распараллеливаемая часть")
ax.set_xlim(0, seq_g + par_g_1 + 0.1)
ax.set_title("Закон Густафсона-Барсиса: доля от $T_p$ фиксирована", fontsize=10)
ax.set_xlabel("время")
ax.legend(**LEGEND)

fig.tight_layout()
fig.savefig(OUT / "деление-времени-амдал-густафсон.png", dpi=150)
plt.close(fig)

# Figure 2: speedup vs number of processors for several serial fractions
n = np.linspace(1, 64, 400)
fs = [0.05, 0.1, 0.2, 0.5]
colors = ddlc_theme.CYCLE[:len(fs)]

fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=False)

ax = axes[0]
for fv, c in zip(fs, colors):
    s = n / (1 + (n - 1) * fv)
    ax.plot(n, s, color=c, label=f"f = {ddlc_theme.num(fv, None)}")
    ax.axhline(1 / fv, color=c, linestyle=":", linewidth=0.8, alpha=0.6)
ax.set_title("Закон Амдала", fontsize=11)
ax.set_xlabel("число процессоров $n$")
ax.set_ylabel("ускорение $S$")
ax.set_xlim(1, 64)
ax.set_ylim(0, 21)
ax.legend(**CURVE_LEGEND)
ax.grid(True)

ax = axes[1]
for fv, c in zip(fs, colors):
    s = n - (n - 1) * fv
    ax.plot(n, s, color=c, label=f"f = {ddlc_theme.num(fv, None)}")
ax.set_title("Закон Густафсона-Барсиса", fontsize=11)
ax.set_xlabel("число процессоров $n$")
ax.set_ylabel("ускорение $S$")
ax.set_xlim(1, 64)
ax.legend(**CURVE_LEGEND)
ax.grid(True)

fig.tight_layout()
fig.savefig(OUT / "ускорение-амдал-густафсон.png", dpi=150)
plt.close(fig)

# Numeric worked example table (printed for copying into the note)
f_ex = 0.1
print(f"f = {f_ex}, asymptote 1/f = {1/f_ex:.1f}")
print(f"{'n':>4} | {'S_Amdahl':>9} | {'E_Amdahl':>9} | {'S_Gustafson':>12}")
for nv in [2, 4, 8, 16, 32, 64]:
    s_a = nv / (1 + (nv - 1) * f_ex)
    e_a = s_a / nv
    s_g = nv - (nv - 1) * f_ex
    print(f"{nv:>4} | {s_a:>9.3f} | {e_a:>9.3f} | {s_g:>12.3f}")
