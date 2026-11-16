"""Optimizers and test surfaces shared by the optimizer figures of topic 6.

Update rules are the ones of lecture 6 (slides 47-48 and the backup slides 61-66),
with the corrections the note "Оптимизаторы нейросетей" lists: Nesterov looks
ahead at w - eta*rho*v, and the cache-based methods divide by the square root of
the cache. Every optimizer takes a gradient function, because Nesterov must
evaluate it at a point of its own choosing.
"""
import numpy as np


class SGD:
    def __init__(self, lr):
        self.lr = lr

    def step(self, w, grad):
        return w - self.lr * grad(w)


class Momentum:
    """v <- rho*v + g(w); w <- w - eta*v (slide 47)."""

    def __init__(self, lr, rho=0.9):
        self.lr, self.rho, self.v = lr, rho, None

    def step(self, w, grad):
        g = grad(w)
        self.v = g if self.v is None else self.rho * self.v + g
        return w - self.lr * self.v


class Nesterov(Momentum):
    """Same as Momentum, but g is taken at the look-ahead point w - eta*rho*v (slide 48, sign fixed)."""

    def step(self, w, grad):
        ahead = w if self.v is None else w - self.lr * self.rho * self.v
        g = grad(ahead)
        self.v = g if self.v is None else self.rho * self.v + g
        return w - self.lr * self.v


class Adagrad:
    """cache <- cache + g^2; w <- w - eta*g/(sqrt(cache)+eps)."""

    def __init__(self, lr, eps=1e-8):
        self.lr, self.eps, self.cache = lr, eps, None

    def step(self, w, grad):
        g = grad(w)
        self.cache = g * g if self.cache is None else self.cache + g * g
        return w - self.lr * g / (np.sqrt(self.cache) + self.eps)


class RMSProp:
    """cache <- beta*cache + (1-beta)*g^2; w <- w - eta*g/(sqrt(cache)+eps)."""

    def __init__(self, lr, beta=0.9, eps=1e-8):
        self.lr, self.beta, self.eps, self.cache = lr, beta, eps, None

    def step(self, w, grad):
        g = grad(w)
        sq = (1 - self.beta) * g * g
        self.cache = sq if self.cache is None else self.beta * self.cache + sq
        return w - self.lr * g / (np.sqrt(self.cache) + self.eps)


class Adam:
    """Momentum average and RMSProp cache, both with bias correction (Kingma and Ba, 2015)."""

    def __init__(self, lr, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, beta1, beta2, eps
        self.m = self.s = None
        self.t = 0

    def step(self, w, grad):
        g = grad(w)
        self.t += 1
        if self.m is None:
            self.m, self.s = np.zeros_like(g), np.zeros_like(g)
        self.m = self.b1 * self.m + (1 - self.b1) * g
        self.s = self.b2 * self.s + (1 - self.b2) * g * g
        mh = self.m / (1 - self.b1 ** self.t)
        sh = self.s / (1 - self.b2 ** self.t)
        return w - self.lr * mh / (np.sqrt(sh) + self.eps)


OPTIMIZERS = {"SGD": SGD, "Momentum": Momentum, "Nesterov": Nesterov, "Adagrad": Adagrad,
              "RMSProp": RMSProp, "Adam": Adam}


def run(opt, w0, grad, steps):
    """Path of steps+1 points, the start included."""
    w = np.asarray(w0, float)
    path = [w]
    for _ in range(steps):
        w = opt.step(w, grad)
        path.append(w)
    return np.array(path)


class Rosenbrock:
    """f = (1-x)^2 + 10 (y-x^2)^2: a curved valley with the minimum at (1, 1), as in the sandbox gd-песочница.html."""

    name = "Розенброк"
    minimum = np.array([1.0, 1.0])
    B = 10.0

    @classmethod
    def f(cls, p):
        p = np.asarray(p, float)
        return (1 - p[..., 0]) ** 2 + cls.B * (p[..., 1] - p[..., 0] ** 2) ** 2

    @classmethod
    def grad(cls, p):
        x, y = p
        return np.array([-2 * (1 - x) - 4 * cls.B * x * (y - x * x), 2 * cls.B * (y - x * x)])


class Valley:
    """f = x^2 + 10 y^2: the stretched bowl of the note "Градиентный спуск" (kappa = 10)."""

    name = "овраг"
    minimum = np.zeros(2)
    H = np.array([2.0, 20.0])

    @classmethod
    def f(cls, p):
        return 0.5 * np.sum(cls.H * np.asarray(p, float) ** 2, axis=-1)

    @classmethod
    def grad(cls, p):
        return cls.H * p
