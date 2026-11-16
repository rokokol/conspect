"""phi(tau) = max(|1 - tau m|, |1 - tau M|) and the error of the iteration for three values of tau."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nmfig  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

n = 5
A = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)
mu, V = np.linalg.eigh(A)
m, M = mu[0], mu[-1]
tau0 = 2 / (M + m)


def phi(t):
    return np.maximum(np.abs(1 - t * m), np.abs(1 - t * M))


# a start vector with both extreme eigenvectors, so the decay follows rho^k
z0 = V[:, 0] + V[:, -1]
taus = [(tau0, r"$\tau_0=2/(M+m)$"), (1 / M, r"$\tau=1/M$"), (0.6, r"$\tau=0{,}6>2/M$")]
cols = [nmfig.CYCLE[0], nmfig.CYCLE[2], nmfig.CYCLE[1]]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 3.9))
t = np.linspace(0, 0.75, 400)
a1.plot(t, phi(t), color=nmfig.INK)
a1.axhline(1, color=nmfig.MUTED, lw=1)
for (tt, lab), c in zip(taus, cols):
    a1.plot([tt], [phi(tt)], "o", color=c, ms=6,
            label=f"{lab}, $\\varphi={phi(tt):.3f}$".replace(".", "{,}"))
a1.axvline(2 / M, color=nmfig.AUX, ls="--", lw=1)
a1.text(2 / M - 0.01, 0.65, r"$2/M$", color=nmfig.INK, ha="right")
a1.set_xlabel(r"$\tau$")
a1.set_ylabel(r"$\varphi(\tau)=\rho(S)$")
a1.set_ylim(0.6, 1.4)
a1.legend(loc="upper left", fontsize=8)

K = 60
for (tt, lab), c in zip(taus, cols):
    S = np.eye(n) - tt * A
    z = z0.copy()
    e = []
    for k in range(K + 1):
        e.append(np.linalg.norm(z) / np.linalg.norm(z0))
        z = S @ z
    a2.semilogy(range(K + 1), e, color=c, label=lab)
a2.set_xlabel("номер итерации $k$")
a2.set_ylabel(r"$|z^k|/|z^0|$")
a2.grid(True, which="major")
a2.legend(fontsize=8)
nmfig.save(fig, 1, "optimal_tau")
print("m, M, tau0, rho0 =", m, M, tau0, phi(tau0))
