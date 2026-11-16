"""One LIF neuron of Shiu et al. 2024 under Poisson input.

Equations and parameters as printed in the paper's Methods:
dv/dt = (g - (v - V_rest)) / T_mbr, dg/dt = -g / tau,
g += w after a presynaptic spike with delay T_dly, w = n * W_syn.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from course import COURSE  # noqa: E402
import ddlc_theme  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "00. Вложения"
rng = np.random.default_rng(3)

V_REST = V_RESET = -52.0  # mV
V_TH = -45.0  # mV
T_MBR = 20.0  # ms, C_mbr * R_mbr = 2 uF/cm2 * 10 kOhm cm2
TAU = 5.0  # ms
T_REF = 2.2  # ms
T_DLY = 1.8  # ms
W_SYN = 0.275  # mV

N_PRE = 10  # presynaptic neurons, illustration
N_SYN = 10  # synapses per connection, illustration
RATE = 100.0  # Hz per presynaptic neuron
DT = 0.1  # ms
T = 200.0  # ms

steps = int(T / DT)
t = np.arange(steps) * DT
w = N_SYN * W_SYN
pre = rng.random((N_PRE, steps)) < RATE * DT / 1000
arrivals = np.roll(pre.sum(0), int(T_DLY / DT))
arrivals[: int(T_DLY / DT)] = 0

v = np.empty(steps)
g = np.empty(steps)
spikes = []
vi, gi, ref_until = V_REST, 0.0, -1.0
for k in range(steps):
    gi += arrivals[k] * w
    if t[k] >= ref_until:
        vi += DT * (gi - (vi - V_REST)) / T_MBR
    gi -= DT * gi / TAU
    if vi >= V_TH:
        spikes.append(t[k])
        vi = V_RESET
        ref_until = t[k] + T_REF
    v[k], g[k] = vi, gi

fig, (a0, a1, a2) = plt.subplots(
    3, 1, figsize=(7, 5.2), dpi=130, sharex=True, gridspec_kw={"height_ratios": [1, 1.2, 1.6]}
)
for i in range(N_PRE):
    a0.vlines(t[pre[i]], i + 0.6, i + 1.4, color=P["jacket"], lw=1)
a0.set_ylabel("входы")
a0.set_yticks([])
a0.set_title("LIF-нейрон модели Shiu под входом")
a1.plot(t, g, color=P["ribbon"])
a1.set_ylabel("$g$, мВ")
a2.plot(t, v, color=P["rule"])
a2.axhline(V_TH, color=P["bow"], ls="--", lw=1)
a2.text(1, V_TH + 0.3, "порог −45 мВ", ha="left", va="bottom", color=P["bow"], fontsize=9)
a2.vlines(spikes, V_TH, V_TH + 3, color=P["ink"], lw=1.2)
a2.set_ylabel("$v$, мВ")
a2.set_xlabel("время, мс")
for a in (a0, a1, a2):
    a.grid(True)
fig.tight_layout()
fig.savefig(OUT / "LIF-нейрон Shiu — вход и спайки.png")
print(f"output rate {len(spikes) / (T / 1000):.0f} Hz, spikes {len(spikes)}")
