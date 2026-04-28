import sys

sys.set_int_max_str_digits(0)
sys.setrecursionlimit(200000)

_POW10_CACHE = {}

def fast_dec(n):
    if n < 10**18:
        return str(n)
    hb = n.bit_length() >> 1
    d = (hb * 30103) // 100000
    p = _POW10_CACHE.get(d)
    if p is None:
        p = 10 ** d
        _POW10_CACHE[d] = p
    hi, lo = divmod(n, p)
    return fast_dec(hi) + str(lo).zfill(d)

def best_threshold(n, L):
    if L <= 1:
        return min(n, 32)
    if L <= 10:
        return min(n, 8)
    if L <= 100:
        return min(n, 4)
    return min(n, 2)

def add(A, B):
    return [[x + y for x, y in zip(r1, r2)] for r1, r2 in zip(A, B)]

def sub(A, B):
    return [[x - y for x, y in zip(r1, r2)] for r1, r2 in zip(A, B)]

def naive(A, B, n):
    BT = list(zip(*B))
    return [[sum(x * y for x, y in zip(row, col)) for col in BT] for row in A]

def s2(A, B):
    a, b = A[0]
    c, d = A[1]
    e, f = B[0]
    g, h = B[1]

    m1 = (a + d) * (e + h)
    m2 = (c + d) * e
    m3 = a * (f - h)
    m4 = d * (g - e)
    m5 = (a + b) * h
    m6 = (c - a) * (e + f)
    m7 = (b - d) * (g + h)

    return [
        [m1 + m4 - m5 + m7, m3 + m5],
        [m2 + m4, m1 - m2 + m3 + m6]
    ]

def split(M, h):
    top = M[:h]
    bot = M[h:]
    return (
        [r[:h] for r in top],
        [r[h:] for r in top],
        [r[:h] for r in bot],
        [r[h:] for r in bot],
    )

def merge(M1, M2, M3, M4, M5, M6, M7, h):
    C11 = [
        [a + d - e + g for a, d, e, g in zip(r1, r4, r5, r7)]
        for r1, r4, r5, r7 in zip(M1, M4, M5, M7)
    ]
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = [
        [a - b + c + f for a, b, c, f in zip(r1, r2, r3, r6)]
        for r1, r2, r3, r6 in zip(M1, M2, M3, M6)
    ]

    return [C11[i] + C12[i] for i in range(h)] + \
           [C21[i] + C22[i] for i in range(h)]

def strassen(A, B, n, T):
    if n == 1:
        return [[A[0][0] * B[0][0]]]

    if n == 2:
        return s2(A, B)

    if n <= T:
        return naive(A, B, n)

    if n & 1:
        p = n + 1
        A2 = [row + [0] for row in A] + [[0] * p]
        B2 = [row + [0] for row in B] + [[0] * p]
        C2 = strassen(A2, B2, p, T)
        return [row[:n] for row in C2[:n]]

    h = n >> 1

    A11, A12, A21, A22 = split(A, h)
    B11, B12, B21, B22 = split(B, h)

    M1 = strassen(add(A11, A22), add(B11, B22), h, T)
    M2 = strassen(add(A21, A22), B11, h, T)
    M3 = strassen(A11, sub(B12, B22), h, T)
    M4 = strassen(A22, sub(B21, B11), h, T)
    M5 = strassen(add(A11, A12), B22, h, T)
    M6 = strassen(sub(A21, A11), add(B11, B12), h, T)
    M7 = strassen(sub(A12, A22), add(B21, B22), h, T)

    return merge(M1, M2, M3, M4, M5, M6, M7, h)

def main():
    data = sys.stdin.buffer.read().split()
    pos = 0

    n = int(data[pos])
    pos += 1
    L = int(data[pos])
    pos += 1

    A = []
    for _ in range(n):
        A.append([int(data[pos + j]) for j in range(n)])
        pos += n

    B = []
    for _ in range(n):
        B.append([int(data[pos + j]) for j in range(n)])
        pos += n

    T = best_threshold(n, L)
    C = strassen(A, B, n, T)

    out_digits = 2 * L + ((n.bit_length() * 30103) // 100000) + 1
    to_s = fast_dec if out_digits > 4000 else str

    out = []
    for row in C:
        out.append(" ".join(to_s(x) for x in row))

    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
