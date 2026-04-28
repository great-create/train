import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

THRESHOLD = 64


def zero_matrix(n):
    return [[0] * n for _ in range(n)]


def add(A, B, C, n):
    for i in range(n):
        Ai, Bi, Ci = A[i], B[i], C[i]
        for j in range(n):
            Ci[j] = Ai[j] + Bi[j]


def sub(A, B, C, n):
    for i in range(n):
        Ai, Bi, Ci = A[i], B[i], C[i]
        for j in range(n):
            Ci[j] = Ai[j] - Bi[j]


def standard(A, B, C, n):
    BT = list(zip(*B))
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for j in range(n):
            Bj = BT[j]
            s = 0
            for k in range(n):
                s += Ai[k] * Bj[k]
            Ci[j] = s


def strassen(A, B, C, n):
    if n <= THRESHOLD:
        standard(A, B, C, n)
        return

    m = n // 2

    A11 = [row[:m] for row in A[:m]]
    A12 = [row[m:] for row in A[:m]]
    A21 = [row[:m] for row in A[m:]]
    A22 = [row[m:] for row in A[m:]]

    B11 = [row[:m] for row in B[:m]]
    B12 = [row[m:] for row in B[:m]]
    B21 = [row[:m] for row in B[m:]]
    B22 = [row[m:] for row in B[m:]]

    M1 = zero_matrix(m)
    M2 = zero_matrix(m)
    M3 = zero_matrix(m)
    M4 = zero_matrix(m)
    M5 = zero_matrix(m)
    M6 = zero_matrix(m)
    M7 = zero_matrix(m)

    T1 = zero_matrix(m)
    T2 = zero_matrix(m)

    add(A11, A22, T1, m)
    add(B11, B22, T2, m)
    strassen(T1, T2, M1, m)

    add(A21, A22, T1, m)
    strassen(T1, B11, M2, m)

    sub(B12, B22, T2, m)
    strassen(A11, T2, M3, m)

    sub(B21, B11, T2, m)
    strassen(A22, T2, M4, m)

    add(A11, A12, T1, m)
    strassen(T1, B22, M5, m)

    sub(A21, A11, T1, m)
    add(B11, B12, T2, m)
    strassen(T1, T2, M6, m)

    sub(A12, A22, T1, m)
    add(B21, B22, T2, m)
    strassen(T1, T2, M7, m)

    for i in range(m):
        for j in range(m):
            C[i][j] = M1[i][j] + M4[i][j] - M5[i][j] + M7[i][j]
            C[i][j + m] = M3[i][j] + M5[i][j]
            C[i + m][j] = M2[i][j] + M4[i][j]
            C[i + m][j + m] = M1[i][j] - M2[i][j] + M3[i][j] + M6[i][j]


def next_power(n):
    p = 1
    while p < n:
        p <<= 1
    return p


def pad(M, n, size):
    if size == n:
        return M
    Z = []
    for i in range(n):
        Z.append(M[i] + [0] * (size - n))
    for _ in range(size - n):
        Z.append([0] * size)
    return Z


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    idx = 2

    A = []
    for _ in range(n):
        A.append([int(x) for x in data[idx:idx+n]])
        idx += n

    B = []
    for _ in range(n):
        B.append([int(x) for x in data[idx:idx+n]])
        idx += n

    size = next_power(n)
    A = pad(A, n, size)
    B = pad(B, n, size)

    C = zero_matrix(size)

    strassen(A, B, C, size)

    out = []
    for i in range(n):
        out.append(" ".join(str(C[i][j]) for j in range(n)))

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
