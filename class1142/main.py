import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

THRESHOLD = 96


def standard_mul(A, B, C, n):
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


def add(A, B, n):
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def sub(A, B, n):
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def strassen(A, B, n):
    if n <= THRESHOLD:
        C = [[0] * n for _ in range(n)]
        standard_mul(A, B, C, n)
        return C

    m = n // 2

    A11 = [row[:m] for row in A[:m]]
    A12 = [row[m:] for row in A[:m]]
    A21 = [row[:m] for row in A[m:]]
    A22 = [row[m:] for row in A[m:]]

    B11 = [row[:m] for row in B[:m]]
    B12 = [row[m:] for row in B[:m]]
    B21 = [row[:m] for row in B[m:]]
    B22 = [row[m:] for row in B[m:]]

    M1 = strassen(add(A11, A22, m), add(B11, B22, m), m)
    M2 = strassen(add(A21, A22, m), B11, m)
    M3 = strassen(A11, sub(B12, B22, m), m)
    M4 = strassen(A22, sub(B21, B11, m), m)
    M5 = strassen(add(A11, A12, m), B22, m)
    M6 = strassen(sub(A21, A11, m), add(B11, B12, m), m)
    M7 = strassen(sub(A12, A22, m), add(B21, B22, m), m)

    C = [[0] * n for _ in range(n)]

    for i in range(m):
        for j in range(m):
            C[i][j] = M1[i][j] + M4[i][j] - M5[i][j] + M7[i][j]
            C[i][j + m] = M3[i][j] + M5[i][j]
            C[i + m][j] = M2[i][j] + M4[i][j]
            C[i + m][j + m] = M1[i][j] - M2[i][j] + M3[i][j] + M6[i][j]

    return C


def next_pow2(n):
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
        A.append([int(x) for x in data[idx:idx + n]])
        idx += n

    B = []
    for _ in range(n):
        B.append([int(x) for x in data[idx:idx + n]])
        idx += n

    size = next_pow2(n)
    A = pad(A, n, size)
    B = pad(B, n, size)

    C = strassen(A, B, size)

    out = []
    for i in range(n):
        out.append(" ".join(str(C[i][j]) for j in range(n)))

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
