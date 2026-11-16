"""Checks for the notes "Сумматор и вычитатель" and "Умножитель Карацубы".

Run: python karatsuba.py (standard library only). Every assert is a claim of the notes.
A gate is counted when AND, OR or NOT is called; the constant 0 costs nothing here.
"""
import itertools
import math
import random

CNT = [0]


def AND(a, b):
    CNT[0] += 1
    return a & b


def OR(a, b):
    CNT[0] += 1
    return a | b


def NOT(a):
    CNT[0] += 1
    return 1 - a


def half(x, y):
    """Half adder: returns (carry, sum), 4 elements."""
    c = AND(x, y)
    return c, AND(NOT(c), OR(x, y))


def cell(x, y, q):
    """Adder cell: two half adders and a disjunction, 9 elements."""
    c1, s1 = half(x, y)
    c2, s2 = half(s1, q)
    return OR(c1, c2), s2


def adder(xs, ys):
    """Bit lists, most significant first. Returns z_0..z_n."""
    n = len(xs)
    q, zn = half(xs[-1], ys[-1])
    z = [zn]
    for i in range(n - 2, -1, -1):
        q, zi = cell(xs[i], ys[i], q)
        z.append(zi)
    z.append(q)
    return z[::-1]


def val(bits):
    v = 0
    for b in bits:
        v = 2 * v + b
    return v


def bits(v, n):
    return [(v >> (n - 1 - i)) & 1 for i in range(n)]


def subtractor(xs, ys):
    z = adder([NOT(b) for b in xs], ys)
    return [NOT(b) for b in z[1:]], z[0]


def check_adder_subtractor():
    for n in range(1, 7):
        CNT[0] = 0
        adder([0] * n, [0] * n)
        assert CNT[0] == 9 * n - 5, (n, CNT[0])
        for X, Y in itertools.product(range(2**n), repeat=2):
            assert val(adder(bits(X, n), bits(Y, n))) == X + Y
        CNT[0] = 0
        subtractor([0] * n, [0] * n)
        assert CNT[0] == 11 * n - 5, (n, CNT[0])
        for X in range(2**n):
            assert val([1 - b for b in bits(X, n)]) == 2**n - 1 - X
            for Y in range(X + 1):
                z, z0 = subtractor(bits(X, n), bits(Y, n))
                assert z0 == 0 and val(z) == X - Y
    for x, y, q in itertools.product((0, 1), repeat=3):
        c, s = cell(x, y, q)
        assert s == x ^ y ^ q and c == (x & y | x & q | y & q) == ((x & y) | ((x ^ y) & q))
    print("adder 9n-5 and subtractor 11n-5 ok for n <= 6")


def check_identity():
    for _ in range(10000):
        n = random.randint(1, 20)
        X1, X2, Y1, Y2 = (random.randrange(2**n) for _ in range(4))
        X, Y = X1 * 2**n + X2, Y1 * 2**n + Y2
        mid = (X1 + X2) * (Y1 + Y2) - X1 * Y1 - X2 * Y2
        assert mid == X1 * Y2 + X2 * Y1 >= 0
        assert X * Y == X1 * Y1 * 4**n + mid * 2**n + X2 * Y2
    print("Karatsuba identity ok on 10^4 random sets")


def pad(b, n):
    return [0] * (n - len(b)) + b


def trim(b, n):
    return b[len(b) - n:] if len(b) > n else pad(b, n)


def add(a, b, n):
    return adder(pad(a, n), pad(b, n))


def sub(a, b, n):
    return subtractor(pad(a, n), pad(b, n))[0]


def shift(b, k):
    return b + [0] * k


def schoolbook(a, b):
    n = len(a)
    acc = [0] * (2 * n)
    for j in range(n):
        row = shift([AND(ai, b[n - 1 - j]) for ai in a], j)
        acc = trim(add(acc, pad(row, 2 * n), 2 * n), 2 * n)
    return acc


def lemma11(a, b):
    """(n+1)-bit product by one n-order multiplier."""
    n = len(a) - 1
    x0, y0, X1, Y1 = a[0], b[0], a[1:], b[1:]
    low = kmul(X1, Y1)
    mid = add([AND(x0, bit) for bit in Y1], [AND(y0, bit) for bit in X1], n)
    total = 2 * n + 2
    r = trim(add(pad(shift([AND(x0, y0)], 2 * n), total), pad(shift(mid, n), total), total), total)
    return trim(add(r, pad(low, total), total), total)


def kmul(a, b):
    n = len(a)
    if n <= 1:
        return schoolbook(a, b)
    h = (n + 1) // 2
    a, b = pad(a, 2 * h), pad(b, 2 * h)
    x1, x2, y1, y2 = a[:h], a[h:], b[:h], b[h:]
    p11, p22 = kmul(x1, y1), kmul(x2, y2)
    pm = lemma11(add(x1, x2, h), add(y1, y2, h))
    m = len(pm)
    mid = sub(sub(pm, pad(p11, m), m), pad(p22, m), m)
    total = 4 * h + 2
    r = trim(add(pad(shift(p11, 2 * h), total), pad(shift(mid, h), total), total), total)
    r = trim(add(r, pad(p22, total), total), total)
    return r[-2 * n:] if len(r) >= 2 * n else pad(r, 2 * n)


def check_multiplier():
    random.seed(1)
    for k in range(1, 11):
        n = 2**k
        a, b = random.randrange(2**n), random.randrange(2**n)
        CNT[0] = 0
        assert val(kmul(bits(a, n), bits(b, n))) == a * b
        ck = CNT[0]
        CNT[0] = 0
        assert val(schoolbook(bits(a, n), bits(b, n))) == a * b
        cs = CNT[0]
        print(f"n={n:5d} karatsuba={ck:9d} k/n^lg3={ck / n**math.log2(3):7.2f} "
              f"schoolbook={cs:9d} s/n^2={cs / n**2:6.2f}")
    for n in (1, 2, 3, 5, 6, 7, 9, 13, 20):
        for _ in range(20):
            a, b = random.randrange(2**n), random.randrange(2**n)
            assert val(kmul(bits(a, n), bits(b, n))) == a * b, n
    print("recursive multiplier correct for n = 2^k (k <= 10) and several odd n")


def check_recurrence():
    """M(1)=1, M(2^k)=3M(2^(k-1))+c*2^(k-1): f(k)=M(2^k)/3^k <= f(1)+2c/3."""
    for c in (1, 7, 100):
        M = {0: 1}
        for k in range(1, 40):
            M[k] = 3 * M[k - 1] + c * 2 ** (k - 1)
        bound = M[1] / 3 + 2 * c / 3
        top = max(M[k] / 3**k for k in range(1, 40))
        assert top <= bound
        print(f"c={c}: max f(k)={top:.8f}, bound f(1)+2c/3={bound}")
    print("sum_{j>=2} (2/3)^j =", sum((2 / 3) ** j for j in range(2, 200)))


if __name__ == "__main__":
    check_adder_subtractor()
    check_identity()
    check_multiplier()
    check_recurrence()
