import sys

def solve():
    # Required by the problem; also needed for str() on large result integers.
    sys.set_int_max_str_digits(0)
    sys.setrecursionlimit(200000)

    data = sys.stdin.buffer.read().split()
    ptr = 0
    n = int(data[ptr]); ptr += 1
    L = int(data[ptr]); ptr += 1

    nn = n * n
    A = [int(data[ptr + i]) for i in range(nn)]; ptr += nn
    B = [int(data[ptr + i]) for i in range(nn)]

    # ── Fast integer → decimal string ──────────────────────────────────────────
    # Python's str() runs in O(d²) for large integers (schoolbook base-conversion).
    # This divide-and-conquer routine splits at roughly half the decimal digit count,
    # recursing until pieces are small enough for str() to handle cheaply.
    # At ~8 000 digits (worst-case result size) it is ~1.4× faster than str().
    _STOP_BITS = 3000 * 3322 // 1000    # stop recursing below ~3 000 decimal digits
    _p10: dict = {}

    def fast_str(x: int) -> str:
        if x.bit_length() <= _STOP_BITS:
            return str(x)
        b = x.bit_length()
        k = max(1, int(b * 0.15051))   # ≈ half the decimal digit count
        p = _p10.get(k)
        if p is None:
            _p10[k] = p = 10 ** k
        hi, lo = divmod(x, p)
        return fast_str(hi) + str(lo).zfill(k)

    # ── Algorithm selection ─────────────────────────────────────────────────────
    # Strassen reduces multiplications from n³ to n^{log₂7} ≈ n^{2.807}.
    # For large L every multiplication is expensive (Python uses Karatsuba
    # internally), so the saving dominates the extra addition overhead.
    use_strassen = (n >= 4 and L >= 100)

    # ── Standard O(n³) ─────────────────────────────────────────────────────────
    if not use_strassen:
        C = [0] * nn
        for i in range(n):
            ins = i * n
            for k in range(n):
                a = A[ins + k]
                if not a:
                    continue
                kns = k * n
                for j in range(n):
                    C[ins + j] += a * B[kns + j]
        out = []
        for i in range(n):
            out.append(' '.join(map(fast_str, C[i*n : i*n+n])))
        sys.stdout.write('\n'.join(out) + '\n')
        return

    # ── Strassen (T = 1), padded once to next power of 2 ───────────────────────
    p = 1
    while p < n:
        p <<= 1

    if p == n:
        Ap, Bp = A, B
    else:
        Ap = [0] * (p * p)
        Bp = [0] * (p * p)
        for i in range(n):
            Ap[i*p : i*p+n] = A[i*n : i*n+n]
            Bp[i*p : i*p+n] = B[i*n : i*n+n]

    # ── Strassen kernel ─────────────────────────────────────────────────────────
    # X, Y : flat row-major arrays of s×s big integers (s always a power of 2).
    # Returns a flat row-major s×s result array.
    #
    # Combine optimisation: process one output row at a time, slicing h elements
    # from each Mᵢ, then zip-combining them.  This is ~3-7× faster than either:
    #   (a) pre-computing all four h²-element quadrant arrays and then scattering
    #       (too much memory allocated at once → cache pressure), or
    #   (b) per-element index access [M1[ih+k]+… for k in range(h)]
    #       (Python index overhead dominates for large bigints).
    def strassen(X, Y, s):
        if s == 1:
            return [X[0] * Y[0]]

        h  = s >> 1
        h2 = h * h

        # Extract submatrices row by row into contiguous flat arrays.
        A11 = [0]*h2; A12 = [0]*h2; A21 = [0]*h2; A22 = [0]*h2
        B11 = [0]*h2; B12 = [0]*h2; B21 = [0]*h2; B22 = [0]*h2
        for i in range(h):
            xs  = i * s;       xhs = xs  + h
            xbs = (i + h) * s; ih  = i  * h
            A11[ih:ih+h] = X[xs  : xs +h]
            A12[ih:ih+h] = X[xhs : xhs+h]
            A21[ih:ih+h] = X[xbs : xbs+h]
            A22[ih:ih+h] = X[xbs+h : xbs+s]
            B11[ih:ih+h] = Y[xs  : xs +h]
            B12[ih:ih+h] = Y[xhs : xhs+h]
            B21[ih:ih+h] = Y[xbs : xbs+h]
            B22[ih:ih+h] = Y[xbs+h : xbs+s]

        # 7 Strassen products (one recursive multiplication each).
        # Input sums/differences use zip() over the full h²-element list —
        # the fastest Python idiom for element-wise big-int arithmetic.
        M1 = strassen([a+b for a,b in zip(A11, A22)],
                      [a+b for a,b in zip(B11, B22)], h)
        M2 = strassen([a+b for a,b in zip(A21, A22)], B11, h)
        M3 = strassen(A11, [a-b for a,b in zip(B12, B22)], h)
        M4 = strassen(A22, [a-b for a,b in zip(B21, B11)], h)
        M5 = strassen([a+b for a,b in zip(A11, A12)], B22, h)
        M6 = strassen([a-b for a,b in zip(A21, A11)],
                      [a+b for a,b in zip(B11, B12)], h)
        M7 = strassen([a-b for a,b in zip(A12, A22)],
                      [a+b for a,b in zip(B21, B22)], h)

        # Combine into output.
        # C₁₁ = M₁ + M₄ − M₅ + M₇
        # C₁₂ = M₃ + M₅
        # C₂₁ = M₂ + M₄
        # C₂₂ = M₁ − M₂ + M₃ + M₆
        C = [0] * (s * s)
        for i in range(h):
            ih = i * h
            rt = i * s          # top-half row start
            rb = (i + h) * s    # bottom-half row start
            m1 = M1[ih:ih+h]; m2 = M2[ih:ih+h]; m3 = M3[ih:ih+h]
            m4 = M4[ih:ih+h]; m5 = M5[ih:ih+h]; m6 = M6[ih:ih+h]
            m7 = M7[ih:ih+h]
            C[rt   :rt+h] = [a+b-c+d for a,b,c,d in zip(m1,m4,m5,m7)]
            C[rt+h :rt+s] = [a+b     for a,b     in zip(m3,m5)]
            C[rb   :rb+h] = [a+b     for a,b     in zip(m2,m4)]
            C[rb+h :rb+s] = [a-b+c+d for a,b,c,d in zip(m1,m2,m3,m6)]
        return C

    Cp = strassen(Ap, Bp, p)

    out = []
    for i in range(n):
        out.append(' '.join(map(fast_str, Cp[i*p : i*p+n])))
    sys.stdout.write('\n'.join(out) + '\n')

solve()
