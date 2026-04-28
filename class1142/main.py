import sys

def solve():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    L = int(data[idx]); idx += 1

    total = n * n
    A = [int(data[idx + i]) for i in range(total)]; idx += total
    B = [int(data[idx + i]) for i in range(total)]

    # Choose threshold based on n and L to minimize big-int muls
    # T=1: 7^log2(n) muls (minimum, but lots of recursion overhead)
    # T=2: 7^(log2(n)-1) * 8 muls
    # For large L, T=1 or T=2 is best; for small L, higher T is fine
    if L * n > 16000:
        T = 1
    else:
        T = 32

    sys.setrecursionlimit(10000)

    def strassen(X, Y, s, ox_r, ox_c, oy_r, oy_c, sx, sy):
        """
        Multiply X[ox_r:ox_r+s, ox_c:ox_c+s] with Y[oy_r:oy_r+s, oy_c:oy_c+s]
        X is stored flat with stride sx, Y with stride sy.
        Returns flat s*s result.
        """
        if s <= T:
            # Standard multiply
            C = [0] * (s * s)
            for i in range(s):
                xr = (ox_r + i) * sx + ox_c
                ci = i * s
                for k in range(s):
                    a = X[xr + k]
                    if not a:
                        continue
                    yr = (oy_r + k) * sy + oy_c
                    for j in range(s):
                        C[ci + j] += a * Y[yr + j]
            return C

        if s & 1:
            # Odd size: extract to contiguous arrays first
            X2 = [0] * (s * s)
            Y2 = [0] * (s * s)
            for i in range(s):
                xr = (ox_r + i) * sx + ox_c
                yr = (oy_r + i) * sy + oy_c
                X2[i*s: i*s+s] = X[xr: xr+s]
                Y2[i*s: i*s+s] = Y[yr: yr+s]
            return strassen_flat(X2, Y2, s)

        h = s >> 1
        h2 = h * h

        # Extract 4 submatrices from X and Y
        def get(M, ro, co, stride):
            o = [0] * h2
            for i in range(h):
                src = (ro + i) * stride + co
                dst = i * h
                o[dst: dst+h] = M[src: src+h]
            return o

        A11 = get(X, ox_r,   ox_c,   sx)
        A12 = get(X, ox_r,   ox_c+h, sx)
        A21 = get(X, ox_r+h, ox_c,   sx)
        A22 = get(X, ox_r+h, ox_c+h, sx)
        B11 = get(Y, oy_r,   oy_c,   sy)
        B12 = get(Y, oy_r,   oy_c+h, sy)
        B21 = get(Y, oy_r+h, oy_c,   sy)
        B22 = get(Y, oy_r+h, oy_c+h, sy)

        add = [A11[k]+A22[k] for k in range(h2)]
        bdd = [B11[k]+B22[k] for k in range(h2)]
        M1 = strassen_flat(add, bdd, h)
        M2 = strassen_flat([A21[k]+A22[k] for k in range(h2)], B11, h)
        M3 = strassen_flat(A11, [B12[k]-B22[k] for k in range(h2)], h)
        M4 = strassen_flat(A22, [B21[k]-B11[k] for k in range(h2)], h)
        M5 = strassen_flat([A11[k]+A12[k] for k in range(h2)], B22, h)
        M6 = strassen_flat([A21[k]-A11[k] for k in range(h2)], [B11[k]+B12[k] for k in range(h2)], h)
        M7 = strassen_flat([A12[k]-A22[k] for k in range(h2)], [B21[k]+B22[k] for k in range(h2)], h)

        C = [0] * (s * s)
        for i in range(h):
            row_top = i * s
            row_bot = (i + h) * s
            ih = i * h
            C[row_top:row_top+h]   = [M1[ih+k]+M4[ih+k]-M5[ih+k]+M7[ih+k] for k in range(h)]
            C[row_top+h:row_top+s] = [M3[ih+k]+M5[ih+k] for k in range(h)]
            C[row_bot:row_bot+h]   = [M2[ih+k]+M4[ih+k] for k in range(h)]
            C[row_bot+h:row_bot+s] = [M1[ih+k]-M2[ih+k]+M3[ih+k]+M6[ih+k] for k in range(h)]
        return C

    def strassen_flat(X, Y, s):
        """X, Y are flat contiguous s*s arrays."""
        if s <= T:
            C = [0] * (s * s)
            for i in range(s):
                ins = i * s
                for k in range(s):
                    a = X[ins + k]
                    if not a:
                        continue
                    kns = k * s
                    for j in range(s):
                        C[ins + j] += a * Y[kns + j]
            return C

        if s == 1:
            return [X[0] * Y[0]]

        if s & 1:
            m = s + 1
            Xp = [0] * (m * m)
            Yp = [0] * (m * m)
            for i in range(s):
                Xp[i*m: i*m+s] = X[i*s: i*s+s]
                Yp[i*m: i*m+s] = Y[i*s: i*s+s]
            Cp = strassen_flat(Xp, Yp, m)
            C = [0] * (s * s)
            for i in range(s):
                C[i*s: i*s+s] = Cp[i*m: i*m+s]
            return C

        h = s >> 1
        h2 = h * h

        A11 = [0]*h2; A12 = [0]*h2; A21 = [0]*h2; A22 = [0]*h2
        B11 = [0]*h2; B12 = [0]*h2; B21 = [0]*h2; B22 = [0]*h2
        for i in range(h):
            xs = i*s; xsh = xs+h
            ys = i*s; ysh = ys+h
            ih = i*h
            A11[ih:ih+h] = X[xs:xs+h]
            A12[ih:ih+h] = X[xsh:xsh+h]
            A21[ih:ih+h] = X[(i+h)*s:(i+h)*s+h]
            A22[ih:ih+h] = X[(i+h)*s+h:(i+h)*s+s]
            B11[ih:ih+h] = Y[ys:ys+h]
            B12[ih:ih+h] = Y[ysh:ysh+h]
            B21[ih:ih+h] = Y[(i+h)*s:(i+h)*s+h]
            B22[ih:ih+h] = Y[(i+h)*s+h:(i+h)*s+s]

        M1 = strassen_flat([A11[k]+A22[k] for k in range(h2)], [B11[k]+B22[k] for k in range(h2)], h)
        M2 = strassen_flat([A21[k]+A22[k] for k in range(h2)], B11, h)
        M3 = strassen_flat(A11, [B12[k]-B22[k] for k in range(h2)], h)
        M4 = strassen_flat(A22, [B21[k]-B11[k] for k in range(h2)], h)
        M5 = strassen_flat([A11[k]+A12[k] for k in range(h2)], B22, h)
        M6 = strassen_flat([A21[k]-A11[k] for k in range(h2)], [B11[k]+B12[k] for k in range(h2)], h)
        M7 = strassen_flat([A12[k]-A22[k] for k in range(h2)], [B21[k]+B22[k] for k in range(h2)], h)

        C = [0] * (s * s)
        for i in range(h):
            ih = i * h
            rt = i * s; rb = (i+h) * s
            C[rt:rt+h]   = [M1[ih+k]+M4[ih+k]-M5[ih+k]+M7[ih+k] for k in range(h)]
            C[rt+h:rt+s] = [M3[ih+k]+M5[ih+k] for k in range(h)]
            C[rb:rb+h]   = [M2[ih+k]+M4[ih+k] for k in range(h)]
            C[rb+h:rb+s] = [M1[ih+k]-M2[ih+k]+M3[ih+k]+M6[ih+k] for k in range(h)]
        return C

    result = strassen_flat(A, B, n)

    out = []
    for i in range(n):
        out.append(' '.join(map(str, result[i*n: i*n+n])))
    sys.stdout.write('\n'.join(out) + '\n')

solve()
