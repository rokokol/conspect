"""Figures of f10 "Геометрические приложения интеграла": catenary arc, spherical zone, ball volume
and the Archimedes comparison of a zone with a cylinder band.

Recovered from the owner's own codex session of 13.06.2026 and put on the vault's ddlc theme:
every colour is a palette role, named here by its meaning.
"""
import numpy as np

from course import COURSE  # noqa: F401  puts the shared ddlc_figures on sys.path
import ddlc_theme  # noqa: E402  applies the vault's style, palette and fonts
import matplotlib.pyplot as plt  # noqa: E402

P = ddlc_theme.P
OUT = COURSE / "content" / "10. Геометрические приложения интеграла" / "00. Вложения"

INK = P["ink"]
CURVE = P["bow"]           # the curve the figure is about: the arc, the generating semicircle
SURFACE = P["rule"]        # the whole sphere or cylinder, drawn see-through
ZONE = P["pink"]           # the part being measured: the spherical zone, light enough for its labels
SLICE = P["ribbon"]        # the cylinder slice of the volume, the cylinder band
EQUATOR = P["yuri"]        # the equator of the Archimedes comparison
GUIDE = P["jacket"]        # dashed and dotted guides


def sphere_grid(R, x0, x1, n=80):
    """A sphere of radius R as the surface of revolution of y = sqrt(R^2 - x^2) over [x0, x1]"""
    xv = np.linspace(x0, x1, n)
    th = np.linspace(0, 2 * np.pi, n)
    X, T = np.meshgrid(xv, th)
    Rr = np.sqrt(np.clip(R**2 - X**2, 0, None))
    return X, Rr * np.cos(T), Rr * np.sin(T)


def cylinder_grid(R, x0, x1, n=90):
    xv = np.linspace(x0, x1, n)
    th = np.linspace(0, 2 * np.pi, n)
    X, T = np.meshgrid(xv, th)
    return X, R * np.cos(T), R * np.sin(T)


def bare_3d(ax):
    # whole numbers only: at the theme's size the default half steps run into each other
    ax.set_xticks(range(-2, 3))
    ax.set_yticks([])
    ax.set_zticks([])
    ax.view_init(elev=16, azim=-68)


# A. Цепная линия y = ch x: дуга на [0, a], длина = sh a
fig, ax = plt.subplots(figsize=(6.4, 3.8))
a = 1.3
xfull = np.linspace(-1.5, 1.5, 400)
ax.plot(xfull, np.cosh(xfull), color=GUIDE, lw=1.4, ls="--", label=r"цепная линия $y=\operatorname{ch} x$")
xarc = np.linspace(0, a, 200)
ax.plot(xarc, np.cosh(xarc), color=CURVE, lw=3, zorder=5, label=r"дуга на $[0,a]$, длина $=\operatorname{sh} a$")
# опоры-подвес: интуиция висящей цепи
ax.plot([-1.5, 1.5], [np.cosh(1.5)] * 2, color=INK, lw=0, marker="s", ms=7)
ax.scatter([0, a], [np.cosh(0), np.cosh(a)], color=CURVE, s=40, zorder=6)
ax.annotate(r"$A=(0,\,1)$", (0, 1), textcoords="offset points", xytext=(-58, -2), fontsize=11, color=CURVE)
ax.annotate(r"$B=(a,\,\operatorname{ch} a)$", (a, np.cosh(a)), textcoords="offset points", xytext=(6, -4),
            fontsize=11, color=CURVE)
ax.vlines([0, a], 0, [np.cosh(0), np.cosh(a)], color=GUIDE, lw=0.7, ls=":")
ax.set_xticks([0, a])
ax.set_xticklabels(["0", "a"])
ax.set_ylim(0, None)
ax.set_title(r"Дуга цепной линии $y=\operatorname{ch} x$ на $[0,a]$")
ax.set_xlabel("x")
ax.legend(loc="upper center", fontsize=9.5)
fig.savefig(OUT / "catenary-arc.png")
plt.close(fig)

# B. Шаровой пояс: зона сферы между x=-a и x=a, S = 4πRa
R, a = 2.0, 0.9
fig = plt.figure(figsize=(6.6, 4.4))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(*sphere_grid(R, -R, R), color=SURFACE, alpha=0.14, linewidth=0, shade=True)
ax.plot_surface(*sphere_grid(R, -a, a), color=ZONE, alpha=0.9, linewidth=0, shade=False)
xv = np.linspace(-R, R, 200)
ax.plot(xv, np.sqrt(R**2 - xv**2), np.zeros_like(xv), color=CURVE, lw=2.2)
ax.plot([-R, R], [0, 0], [0, 0], color=INK, lw=1)
# метки -a, a выносим под сферу пунктирной выноской: иначе пояс их закрывает
for xe, lab in [(-a, r"$-a$"), (a, r"$a$")]:
    rb = np.sqrt(R**2 - xe**2)
    ax.plot([xe, xe], [0, 0], [-rb, -R * 1.5], color=INK, lw=0.9, ls=":")
    ax.text(xe, 0, -R * 1.62, lab, color=INK, fontsize=14, ha="center", va="top")
ax.text(0.05, 0, R * 1.2, r"$R$", color=SURFACE, fontsize=13, ha="center")
ax.plot([0, 0], [0, 0], [0, R], color=SURFACE, lw=1.2, ls="--")
ax.set_title(r"Шаровой пояс высоты $2a$:  $S=4\pi R a$", pad=0)
ax.set_xlabel("x")
bare_3d(ax)
ax.set_aspect("equal")
fig.savefig(OUT / "spherical-zone.png")
plt.close(fig)

# C. Объём шара: тело вращения полуокружности, диск-слой, V=4/3πR³
R = 2.0
fig = plt.figure(figsize=(6.6, 4.4))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(*sphere_grid(R, -R, R), color=SURFACE, alpha=0.16, linewidth=0, shade=True)
xi0, xi1 = 0.5, 1.0
xim = 0.5 * (xi0 + xi1)
ri = np.sqrt(R**2 - xim**2)
thd = np.linspace(0, 2 * np.pi, 60)
Xc, Tc = np.meshgrid([xi0, xi1], thd)
ax.plot_surface(Xc, ri * np.cos(Tc), ri * np.sin(Tc), color=SLICE, alpha=0.32, linewidth=0, shade=False)
rr = np.linspace(0, ri, 12)
TT, RR = np.meshgrid(thd, rr)
for xe in (xi0, xi1):
    ax.plot_surface(np.full_like(TT, xe), RR * np.cos(TT), RR * np.sin(TT), color=SLICE, alpha=0.28,
                    linewidth=0, shade=False)
    ax.plot(np.full_like(thd, xe), ri * np.cos(thd), ri * np.sin(thd), color=SLICE, lw=1.7)
xv = np.linspace(-R, R, 200)
ax.plot(xv, np.sqrt(R**2 - xv**2), np.zeros_like(xv), color=CURVE, lw=2.2)
ax.text(xim, 0, ri + 0.4, r"цилиндр $\pi(R^2-x^2)\,dx$", color=SLICE, fontsize=10, ha="center")
ax.plot([-R, R], [0, 0], [0, 0], color=INK, lw=1)
for xe, lab in [(-R, r"$-R$"), (R, r"$R$")]:
    ax.plot([xe, xe], [0, 0], [0, 0], marker="o", color=INK, ms=4)
    ax.text(xe, 0, -R * 0.42, lab, color=INK, fontsize=13, ha="center")
ax.set_title(r"Шар как тело вращения:  $V=\frac{4}{3}\pi R^3$", pad=0)
ax.set_xlabel("x")
bare_3d(ax)
ax.set_aspect("equal")
fig.savefig(OUT / "sphere-volume.png")
plt.close(fig)

# D. Теорема Архимеда: шаровой пояс и боковая полоса цилиндра той же высоты
R, a = 2.0, 0.9
fig = plt.figure(figsize=(11.8, 4.4))
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
th = np.linspace(0, 2 * np.pi, 360)
for ax in (ax1, ax2):
    ax.plot([-R, R], [0, 0], [0, 0], color=INK, lw=1.0)
    ax.set_xlabel("")
    ax.set_xticks(range(-2, 3))
    ax.set_yticks([])
    ax.set_zticks([])
    ax.view_init(elev=18, azim=-64)
    ax.set_box_aspect((1.15, 1, 1))

ax1.plot_surface(*sphere_grid(R, -R, R, 90), color=SURFACE, alpha=0.12, linewidth=0, shade=True)
ax1.plot_surface(*sphere_grid(R, -a, a, 90), color=ZONE, alpha=0.94, linewidth=0, shade=False)
ax1.plot(np.zeros_like(th), R * np.cos(th), R * np.sin(th), color=EQUATOR, lw=2.4)
for xe in (-a, a):
    re = np.sqrt(R**2 - xe**2)
    ax1.plot(np.full_like(th, xe), re * np.cos(th), re * np.sin(th), color=GUIDE, lw=1.0, ls="--", alpha=0.8)
    ax1.plot([xe, xe], [0, 0], [-re, -re * 1.18], color=INK, lw=0.9, ls=":")
ax1.text(0.0, 0.0, R * 1.15, r"$R$", color=SURFACE, fontsize=13, ha="center")
# the label stands off the upper right of the equator, outside the zone that would cover it
ax1.text(0.0, R * 0.95, R * 0.95, "экватор", color=EQUATOR, fontsize=11, ha="left")
ax1.text(0.0, 0.0, -R * 1.42, "шаровой пояс", fontsize=12, ha="center")
ax1.set_title(r"Участок сферы высоты $2a$", pad=0)

ax2.plot_surface(*cylinder_grid(R, -R, R), color=SURFACE, alpha=0.10, linewidth=0, shade=False)
ax2.plot_surface(*cylinder_grid(R, -a, a), color=SLICE, alpha=0.72, linewidth=0, shade=False)
ax2.plot(np.zeros_like(th), R * np.cos(th), R * np.sin(th), color=EQUATOR, lw=2.4)
for xe in (-a, a):
    ax2.plot(np.full_like(th, xe), R * np.cos(th), R * np.sin(th), color=SLICE, lw=1.7)
    ax2.plot([xe, xe], [0, 0], [-R, -R * 1.18], color=INK, lw=0.9, ls=":")
ax2.text(0.0, 0.0, R * 1.15, r"$R$", color=SURFACE, fontsize=13, ha="center")
ax2.text(0.0, R * 0.95, R * 0.95, "экватор", color=EQUATOR, fontsize=11, ha="left")
ax2.text(0.0, 0.0, -R * 1.42, "боковая полоса цилиндра", fontsize=12, ha="center")
ax2.set_title(r"Та же высота $2a$", pad=0)

fig.suptitle(r"Теорема Архимеда: $S_{\mathrm{пояса}}=S_{\mathrm{боковой\ полосы\ цилиндра}}=4\pi R a$",
             y=0.98, fontsize=13.5)
fig.savefig(OUT / "archimedes-zone-comparison.png")
plt.close(fig)
